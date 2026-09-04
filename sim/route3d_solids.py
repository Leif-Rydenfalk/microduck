"""route3d_solids — sweep every routed path as a SOLID, put a real JST housing on
every located end, and export the harness as CAD.

    ce-cad/bin/cad sim/route3d_solids.py

Inputs  out/wiring/paths.json (sim/route3d.py), the occupancy at
        /private/tmp/int-wire3d/occ.npz, part:jst-ehr-03's own cad/part.py, and
        connection:jst-eh-3pin's cad/mate.py for every housing transform.
Outputs out/wiring/cad/harness.step, harness.stl, per-run <id>.stl,
        out/wiring/solids.json.

THE PLACEMENT RULE IS TRIAD.md's, KEPT: a joined part gets NO literal transform.
Every housing here is placed by calling connection:jst-eh-3pin's `mate()` on two
interface records — the housing's `mate` (part:jst-ehr-03) and the servo's
`socket_pos_y` / `socket_neg_y` (part:xl330-m288-t) — and applying the 4x4 that
comes back. The servo interface itself is built from the servo's placement row,
so the only literal numbers in this file are the ones the part folders publish.

MASS is computed, not asserted: copper 8.9600 g/cm3 (IEC 60228 / CRC) over three
conductors of the ASTM B258 21 AWG area, plus PVC 1.3800 g/cm3 over the
insulation annulus at the NOMINAL 1.4500 mm jacket. Both densities and the
nominal are named in the output, and the whole figure is labelled NOMINAL
because the jacket OD is CANNOT DETERMINE.
"""
import json, math, os, sys, time
import numpy as np

R = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck"
sys.path.insert(0, "/Users/leifrydenfalk/dev/ce-workshop/ce-cad")
sys.path.insert(0, R + "/ce-connections/jst-eh-3pin/current/cad")
from cecad.route import (Occupancy, fillet_corners, sweep_solid, sweep_polyline,
                         polyline_of, path_length)

import FreeCAD as App
import Part

OCC_NPZ = "/private/tmp/int-wire3d/occ.npz"
LOG = open("/private/tmp/int-wiresolids/solids-progress.log", "a", buffering=1)


def say(*a):
    m = " ".join(str(x) for x in a)
    sys.stdout.write(m + "\n")
    LOG.write(m + "\n")
# A SUBSET SWEEP WRITES ITS OWN FILES. CE_SOLIDS_TAG=hat reads paths-hat.json and
# writes solids-hat.json, so re-sweeping four re-routed runs cannot overwrite the
# sixteen-run answer already on disk and already cited.
TAG = os.environ.get("CE_SOLIDS_TAG", "").strip()
_sfx = ("-" + TAG) if TAG else ""
PATHS_IN = R + "/out/wiring/paths%s.json" % _sfx
SOLIDS_OUT = R + "/out/wiring/solids%s.json" % _sfx
OUTDIR = R + "/out/wiring/cad"
CLEAR_MIN = 1.0

RESAMPLE_MM = 1.0      # spacing the routed chain is resampled to before interpolation


def _resample(pts, step):
    """Uniform arc-length resample of a point chain, endpoints kept exactly."""
    P = [np.asarray(q, float) for q in pts]
    seg = [float(np.linalg.norm(P[i + 1] - P[i])) for i in range(len(P) - 1)]
    total = sum(seg)
    if total <= 0:
        return P
    n = max(2, int(round(total / step)) + 1)
    out, si, acc = [P[0]], 0, 0.0
    for k in range(1, n - 1):
        target = total * k / (n - 1)
        while si < len(seg) - 1 and acc + seg[si] < target:
            acc += seg[si]
            si += 1
        f = 0.0 if seg[si] <= 0 else (target - acc) / seg[si]
        out.append(P[si] + (P[si + 1] - P[si]) * f)
    out.append(P[-1])
    return out


def _max_dev(a, b):
    """Largest distance from any point of chain a to the nearest SEGMENT of b."""
    B = [np.asarray(q, float) for q in b]
    worst = 0.0
    for p in [np.asarray(q, float) for q in a]:
        best = 1e18
        for i in range(len(B) - 1):
            u = B[i + 1] - B[i]
            L2 = float(u @ u)
            t = 0.0 if L2 <= 0 else max(0.0, min(1.0, float((p - B[i]) @ u) / L2))
            best = min(best, float(np.linalg.norm(p - (B[i] + u * t))))
        worst = max(worst, best)
    return worst


RHO_CU = 8.96      # g/cm3, annealed copper, IEC 60228 / CRC
RHO_PVC = 1.38     # g/cm3, plasticised PVC (a stated nominal; no vendor jacket material)
BARE_D_21 = 0.127 * 92.0 ** ((36 - 21) / 39.0)
INS_OD_NOM = 1.45


def load_occ():
    z = np.load(OCC_NPZ)
    occ = Occupancy.__new__(Occupancy)
    occ.cell = float(z["cell"][0]); occ.lo = z["lo"]; occ.grid = z["grid"]
    occ.owner = z["owner"]; occ.shape = occ.grid.shape
    occ._edt = z["edt"].astype(np.float64); occ.labels = {}
    return occ


def housing_shape():
    """part:jst-ehr-03's own build(), no copy of its numbers here."""
    sys.path.insert(0, R + "/ce-parts/jst-ehr-03/current/cad")
    import importlib
    m = importlib.import_module("part")
    importlib.reload(m)
    doc = App.newDocument("ehr03")
    p = m.build(doc)
    return p.shape.copy()


def servo_socket_iface(mate_mm, insertion_dir, row_dir):
    """The servo's EH socket as an INTERFACE RECORD, so mate() can be called on it.

    This is the record that belongs in part:xl330-m288-t/cad/interfaces.json —
    wiring/README.md section 5 item 1 named its absence as the tool gap that
    forced the rung-5 lane to measure routes off placements instead of off
    connectors. Built here from the placement, written there by this lane.
    """
    # THE HEADER'S +z LEAVES THE BOARD; the insertion direction points the other
    # way. mate() seats the housing SEAT_MM along the header's +z, so handing it
    # the insertion direction puts the housing 1.6000 mm INSIDE the servo case
    # and the whole 8.1000 mm mated stack on the wrong side of the flank. Flipped
    # here, and the placement is checked in tools/place_harness.py by pushing the
    # housing's own origin and axis back through the 4x4.
    return {"name": "socket", "role": "eh_header", "series": "EH", "circuits": 3,
            "pitch_mm": 2.5, "mated_height_mm": 8.1, "owner_ref": "part:xl330-m288-t",
            "frame": {"origin_mm": list(mate_mm),
                      "z_axis": [-float(v) for v in insertion_dir],
                      "x_axis": list(row_dir)}}


LOFT_STATION_MM = 1.5     # spacing of the loft's circular stations, mm
STL_DEVIATION_MM = 0.25   # mm; a 3.1243 mm tube needs no finer, and 0.0500 mm cost 7.6 MB
                          # and six minutes for ONE 33 mm cable (measured)


TUBE_SIDES = 16           # polygon sides of the cable cross-section


def _tube_mesh(poly, od, sides=TUBE_SIDES):
    """The cable as an explicit triangle tube, built with parallel transport.

    WHY NOT THE KERNEL. Three kernel sweeps were tried on this data and every
    one has a route that defeats it, MEASURED, not supposed:
      * MakePipeShell over a b-spline (Frenet and corrected): dxl-hat-id34 does
        not return in minutes.
      * cecad.route.sweep_polyline's capsule-chain fallback: ~300 fused
        primitives, minutes per cable, and a 7.6 MB STL.
      * a ruled loft of circular stations: fast to build (0.1-2.2 s) but
        dxl-id20-id21's 442-face result does not come back from .Volume OR from
        .tessellate() in six minutes, because the ruled surface self-intersects
        at the tight bends and OCCT integrates and meshes it the hard way.
    A cable is a tube of constant radius along a known curve. Building it is
    arithmetic, so it is done here as arithmetic: a PARALLEL-TRANSPORT frame
    (the rotation-minimising frame — no roll accumulates and, unlike Frenet, it
    does not flip where the curvature vanishes, which is what a relaxed route is
    full of), a `sides`-gon at each station, two triangles per quad, and flat
    caps. Deterministic, O(n), and the numbers it costs are stated: the polygon
    inscribes the circle, so the modelled tube is smaller than the real one by
    at most r(1 - cos(pi/sides)) = %.4f mm on a %.4f mm cable, and the volume it
    reports is the mesh's own, by the divergence theorem, not an envelope
    formula that assumes the path is straight.
    """
    P = [np.asarray(q, float) for q in poly]
    r = od / 2.0
    # tangents
    T = []
    for i in range(len(P)):
        a = P[max(0, i - 1)]
        b = P[min(len(P) - 1, i + 1)]
        v = b - a
        n = float(np.linalg.norm(v))
        T.append(v / n if n > 1e-12 else np.array([0.0, 0.0, 1.0]))
    # parallel transport of an initial normal
    seed = np.array([0.0, 0.0, 1.0])
    if abs(float(seed @ T[0])) > 0.9:
        seed = np.array([1.0, 0.0, 0.0])
    N = [seed - T[0] * float(seed @ T[0])]
    N[0] /= float(np.linalg.norm(N[0]))
    for i in range(1, len(P)):
        v = N[i - 1] - T[i] * float(N[i - 1] @ T[i])
        nn = float(np.linalg.norm(v))
        N.append(v / nn if nn > 1e-9 else N[i - 1])
    pts, ring = [], []
    for i in range(len(P)):
        b = np.cross(T[i], N[i])
        base = len(pts)
        for k in range(sides):
            th = 2.0 * math.pi * k / sides
            pts.append(P[i] + N[i] * (r * math.cos(th)) + b * (r * math.sin(th)))
        ring.append(base)
    fac = []
    for i in range(len(P) - 1):
        a, c = ring[i], ring[i + 1]
        for k in range(sides):
            k2 = (k + 1) % sides
            fac.append((a + k, a + k2, c + k2))
            fac.append((a + k, c + k2, c + k))
    cap0, cap1 = len(pts), None
    pts.append(P[0])
    for k in range(sides):
        fac.append((cap0, ring[0] + (k + 1) % sides, ring[0] + k))
    cap1 = len(pts)
    pts.append(P[-1])
    for k in range(sides):
        fac.append((cap1, ring[-1] + k, ring[-1] + (k + 1) % sides))
    return pts, fac


def _mesh_volume(pts, fac):
    """Signed volume of a closed triangle mesh, divergence theorem."""
    v = 0.0
    for a, b, c in fac:
        pa, pb, pc = pts[a], pts[b], pts[c]
        v += float(pa @ np.cross(pb, pc)) / 6.0
    return abs(v)


def _sweep(poly, od):
    """One cable as (mesh, solid, how). See _tube_mesh for why this is arithmetic."""
    import Part as _P
    pts, fac = _tube_mesh(poly, od)
    sh = None
    try:
        s2 = _P.Shape()
        s2.makeShapeFromMesh(([tuple(float(c) for c in p) for p in pts],
                              [tuple(int(i) for i in f) for f in fac]), 1e-4)
        sh = _P.Solid(_P.Shell(s2.Faces)) if s2.Faces else None
    except Exception as e:
        say("   solid from mesh refused: %s" % e)
    return (pts, fac), sh, "parallel-transport tube, %d-gon" % TUBE_SIDES


def _write_shape_stl(shape, path):
    """A COMPOUND (housings, or the whole harness) as a binary STL."""
    import Mesh as _Mesh
    vts, fcs = shape.tessellate(STL_DEVIATION_MM)
    m = _Mesh.Mesh([((vts[a].x, vts[a].y, vts[a].z), (vts[b].x, vts[b].y, vts[b].z),
                     (vts[c].x, vts[c].y, vts[c].z)) for a, b, c in fcs])
    m.write(path)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        raise IOError("STL export wrote nothing: %s" % path)
    return os.path.getsize(path)


def _write_mesh(pts, fac, path):
    """Write the tube mesh as a BINARY STL, and CHECK IT LANDED.

    MEASURED DEFECTS, 2026-09-04, both of them silent:
      * Part.export([shape], "x.stl") writes NOTHING in this FreeCAD build and
        does not raise — the .stl exporter belongs to the Mesh module, which
        this script never imported. Sixteen cables were reported "exported"
        behind an empty directory.
      * Shape.exportStl ignores the deviation it is handed: 8.5 MB of ASCII for
        one 52 mm tube at both 0.0500 and 0.2500 mm.
    The mesh here is this file's own, so it is simply written, and the file is
    stat-ed afterwards because neither of those two failed loudly.
    """
    import Mesh as _Mesh
    m = _Mesh.Mesh([(tuple(float(c) for c in pts[a]),
                     tuple(float(c) for c in pts[b]),
                     tuple(float(c) for c in pts[c])) for a, b, c in fac])
    m.write(path)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        raise IOError("STL export wrote nothing: %s" % path)
    return os.path.getsize(path)


def apply4(T, shape):
    m = App.Matrix(T[0][0], T[0][1], T[0][2], T[0][3],
                   T[1][0], T[1][1], T[1][2], T[1][3],
                   T[2][0], T[2][1], T[2][2], T[2][3],
                   0, 0, 0, 1)
    s = shape.copy()
    s.transformShape(m, True)
    return s


def main():
    t0 = time.time()
    from mate import mate as eh_mate
    occ = load_occ()
    paths = json.load(open(PATHS_IN))["record"]["paths"]
    say("paths from %s: %d runs" % (PATHS_IN, len(paths)))
    os.makedirs(OUTDIR, exist_ok=True)
    base_housing = housing_shape()
    say("part:jst-ehr-03 built: bbox %s volume %.4f mm3"
          % ([round(v, 4) for v in (base_housing.BoundBox.XLength, base_housing.BoundBox.YLength,
                                    base_housing.BoundBox.ZLength)], base_housing.Volume))

    cable_shapes, housing_shapes, rows = [], [], []
    n_housing = 0
    for rid, p in sorted(paths.items()):
        od = p["od_mm"]
        r_req = od / 2.0 + CLEAR_MIN
        wp = [np.asarray(x, float) for x in p["waypoints_mm"]]
        # THE PATH IS ALREADY A RELAXED POINT CHAIN, so it is swept as one: a
        # b-spline through it and ONE pipe shell. The earlier route through
        # fillet_corners + sweep_solid turns a 31-point chain into ~60 arc and
        # line edges, the kernel refuses the shell, and the capsule-chain
        # fallback fuses ~600 primitives per cable — measured: no cable finished
        # in 7.5 minutes. Resampling to RESAMPLE_MM first keeps the interpolation
        # well conditioned (relax() leaves sub-0.1 mm steps that make a spline
        # oscillate) and the deviation from the routed chain is MEASURED below,
        # never assumed.
        poly_in = _resample(wp, RESAMPLE_MM)
        t_sw = time.time()
        (mpts, mfac), shape, how = _sweep(poly_in, od)
        say("   %-18s swept by %-34s in %5.1f s (%d tris)"
            % (rid, how, time.time() - t_sw, len(mfac)))
        poly = poly_in
        L = path_length(poly)
        dev = _max_dev(wp, poly)
        # THE VOLUME OF A LOFT THROUGH A TIGHT BEND CAN COST MINUTES, because the
        # ruled surface self-intersects there and OCCT integrates it the hard
        # way. Measured: dxl-imu200-id20 (124.6 mm, 0.6739 mm clearance, the
        # tightest route in the set) lofted in 1.7 s and then did not return from
        # .Volume in six minutes. A number that cannot be taken is CANNOT
        # DETERMINE with the reason, not a number the run stalls waiting for.
        vol = _mesh_volume(mpts, mfac)
        # mass, from the geometry and two named densities
        n_cond = 3 if rid.startswith("dxl") else 2
        a_cu = math.pi * (BARE_D_21 / 2.0) ** 2                    # mm2 per conductor
        m_cu = a_cu * n_cond * L * 1e-3 * RHO_CU                   # mm3 -> cm3 = 1e-3
        a_ins = math.pi * ((INS_OD_NOM / 2.0) ** 2 - (BARE_D_21 / 2.0) ** 2)
        m_pvc = a_ins * n_cond * L * 1e-3 * RHO_PVC
        if shape is not None:
            cable_shapes.append(shape)
        stl_bytes = _write_mesh(mpts, mfac, os.path.join(OUTDIR, rid + ".stl"))
        row = {"id": rid, "od_mm": od, "swept_by": how,
               "resampled_to_mm": RESAMPLE_MM,
               "resample_deviation_mm": round(dev, 4),
               "resample_deviation_means": "largest distance from a routed waypoint to the "
                                           "swept centreline; the clearance numbers in "
                                           "cables3d.json are measured on the routed chain, so "
                                           "this is how far the SOLID may sit from what was "
                                           "measured",
               "length_mm": round(L, 4),
               "volume_mm3": round(vol, 4),
               "volume_basis": "the divergence theorem over this cable's own closed tube mesh",
               "triangles": len(mfac), "stl_bytes": stl_bytes,
               "solid_for_step": shape is not None,

               "envelope_volume_check_mm3": round(math.pi * (od / 2.0) ** 2 * L, 4),
               "conductors": n_cond,
               "mass_copper_g": round(m_cu, 4), "mass_jacket_g": round(m_pvc, 4),
               "mass_total_g": round(m_cu + m_pvc, 4),
               "mass_is_nominal": True,
               "housings": []}
        for e in p["ends"]:
            if not e.get("housing_part"):
                continue
            iface_h = json.load(open(R + "/ce-parts/jst-ehr-03/current/cad/interfaces.json"))
            hm = [i for i in iface_h["record"]["interfaces"] if i["name"] == "mate"][0]
            hm = dict(hm); hm["role"] = "eh_housing"; hm["owner_ref"] = "part:jst-ehr-03"
            sk = servo_socket_iface(e["mate_mm"], e["insertion_dir"], e["row_dir"])
            mt = eh_mate(hm, sk)
            housing_shapes.append(apply4(mt.transform, base_housing))
            n_housing += 1
            row["housings"].append({"part": "part:jst-ehr-03",
                                    "connection": "connection:jst-eh-3pin",
                                    "placed_by": "connection:jst-eh-3pin cad/mate.py",
                                    "verdict": mt.verdict,
                                    "seat_mm": mt.provenance["seat_mm"],
                                    "origin_mm": [round(mt.transform[i][3], 4) for i in range(3)],
                                    "transform": [[round(mt.transform[i][j], 9) for j in range(4)]
                                                  for i in range(4)],
                                    "at_device": e.get("device"),
                                    "adds_parts": mt.adds_parts})
        rows.append(row)
        json.dump({"$triad": 1, "kind": "harness-solids-partial",
                   "generated_by": "sim/route3d_solids.py",
                   "record": {"units": "mm, g", "complete": False, "cables": rows}},
                  open(SOLIDS_OUT + ".partial", "w"), indent=1)
        say("%-18s L %8.3f mm  vol %9.2f mm3  env %9.2f  stl %7d B  housings %d  mass %.3f g"
            % (rid, L, vol, math.pi * (od / 2.0) ** 2 * L, stl_bytes,
               len(row["housings"]), m_cu + m_pvc))

    allshapes = cable_shapes + housing_shapes
    comp = Part.Compound(allshapes)
    # A RAW SHAPE EXPORTS AS AN EMPTY STEP. Measured: Part.export([compound], ...)
    # wrote a 1 640-byte file — a valid ISO-10303-21 header with no geometry in
    # it — for 42 solids, and raised nothing. The exporter wants DOCUMENT
    # OBJECTS, so the compound is put in the document first and the size is
    # checked afterwards against a floor no empty file can clear.
    _doc = App.newDocument("harness_export")
    _o = _doc.addObject("Part::Feature", "harness")
    _o.Shape = comp
    _doc.recompute()
    _step = os.path.join(OUTDIR, "harness%s.step" % _sfx)
    Part.export([_o], _step)
    if os.path.getsize(_step) < 100_000:
        raise IOError("STEP export wrote %d bytes for %d solids — that is an empty file "
                      "with a header on it: %s" % (os.path.getsize(_step), len(allshapes), _step))
    exported = {"harness%s.step" % _sfx: os.path.getsize(os.path.join(OUTDIR, "harness%s.step" % _sfx)),
                "harness%s.stl" % _sfx: _write_shape_stl(comp, os.path.join(OUTDIR, "harness%s.stl" % _sfx)),
                "cables-only%s.stl" % _sfx: _write_shape_stl(Part.Compound(cable_shapes),
                                               os.path.join(OUTDIR, "cables-only%s.stl" % _sfx)),
                "housings-only%s.stl" % _sfx: _write_shape_stl(Part.Compound(housing_shapes),
                                                 os.path.join(OUTDIR, "housings-only%s.stl" % _sfx))}
    for k, v in sorted(exported.items()):
        say("exported %-20s %9d bytes" % (k, v))
    tot_L = sum(r["length_mm"] for r in rows)
    tot_m = sum(r["mass_total_g"] for r in rows)
    doc = {"$triad": 1, "kind": "harness-solids", "generated_by": "sim/route3d_solids.py",
           "record": {
               "units": "mm, g",
               "counts": {"cables_swept": len(rows), "housings_placed": n_housing,
                          "solids_exported": len(allshapes)},
               "totals": {"routed_length_mm": round(tot_L, 4),
                          "mass_nominal_g": round(tot_m, 4)},
               "mass_basis": {"copper_g_cm3": RHO_CU, "copper_cite": "IEC 60228 / CRC, annealed",
                              "jacket_g_cm3": RHO_PVC,
                              "jacket_cite": "plasticised PVC, a STATED NOMINAL — no vendor "
                                             "states the X3P's jacket material",
                              "bare_conductor_mm": round(BARE_D_21, 4),
                              "jacket_od_nominal_mm": INS_OD_NOM,
                              "why_nominal": "the jacket OD is CANNOT DETERMINE (JST eEH.pdf p.2 "
                                             "bounds it to 1.0-1.9; the midpoint is used and "
                                             "labelled)"},
               "placement_rule": "TRIAD.md: a joined part gets no literal transform. Every "
                                 "housing was placed by connection:jst-eh-3pin's mate() on the "
                                 "housing's `mate` interface and a servo `socket_*` interface "
                                 "built from that servo's placement row.",
               "exports": {("out/wiring/cad/" + k): v for k, v in exported.items()},
               "exports_are_bytes_on_disk": "every file was stat-ed after writing; Part.export "
                                            "to .stl writes nothing in this FreeCAD build and "
                                            "does not raise, so Shape.exportStl is used and the "
                                            "size is checked",
               "stl_deviation_mm": STL_DEVIATION_MM,
               "cables": rows}}
    json.dump(doc, open(SOLIDS_OUT, "w"), indent=1)
    say("wrote", SOLIDS_OUT)
    say("\n%d cables swept, %d housings placed, %d solids; routed %.3f mm, nominal mass %.3f g; %.1f s"
          % (len(rows), n_housing, len(allshapes), tot_L, tot_m, time.time() - t0))


main()
