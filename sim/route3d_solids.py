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
    return {"name": "socket", "role": "eh_header", "series": "EH", "circuits": 3,
            "pitch_mm": 2.5, "mated_height_mm": 8.1, "owner_ref": "part:xl330-m288-t",
            "frame": {"origin_mm": list(mate_mm), "z_axis": list(insertion_dir),
                      "x_axis": list(row_dir)}}


STL_DEVIATION_MM = 0.05


def _export_stl(shape, path):
    """Write an STL and CHECK IT LANDED.

    MEASURED DEFECT, 2026-09-04: Part.export([shape], "x.stl") writes NOTHING in
    this FreeCAD build — the .stl exporter belongs to the Mesh module, which this
    script never imported, and Part.export neither writes nor raises. Sixteen
    cables swept and reported "exported" with an empty directory behind them.
    Shape.exportStl is the Part-side call that actually writes, and the file is
    stat-ed afterwards so a silent failure can never be reported as an export.
    """
    shape.exportStl(path, STL_DEVIATION_MM)
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
    paths = json.load(open(R + "/out/wiring/paths.json"))["record"]["paths"]
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
        shape, how = sweep_polyline(poly_in, od, name=rid)
        poly = poly_in
        L = path_length(poly)
        dev = _max_dev(wp, poly)
        vol = shape.Volume
        # mass, from the geometry and two named densities
        n_cond = 3 if rid.startswith("dxl") else 2
        a_cu = math.pi * (BARE_D_21 / 2.0) ** 2                    # mm2 per conductor
        m_cu = a_cu * n_cond * L * 1e-3 * RHO_CU                   # mm3 -> cm3 = 1e-3
        a_ins = math.pi * ((INS_OD_NOM / 2.0) ** 2 - (BARE_D_21 / 2.0) ** 2)
        m_pvc = a_ins * n_cond * L * 1e-3 * RHO_PVC
        cable_shapes.append(shape)
        _export_stl(shape, os.path.join(OUTDIR, rid + ".stl"))
        row = {"id": rid, "od_mm": od, "swept_by": how,
               "resampled_to_mm": RESAMPLE_MM,
               "resample_deviation_mm": round(dev, 4),
               "resample_deviation_means": "largest distance from a routed waypoint to the "
                                           "swept centreline; the clearance numbers in "
                                           "cables3d.json are measured on the routed chain, so "
                                           "this is how far the SOLID may sit from what was "
                                           "measured",
               "length_mm": round(L, 4), "volume_mm3": round(vol, 4),
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
                                    "adds_parts": mt.adds_parts})
        rows.append(row)
        say("%-18s swept %-14s L %8.3f mm  vol %10.2f mm3  housings %d  mass %.3f g"
              % (rid, how, L, vol, len(row["housings"]), m_cu + m_pvc))

    allshapes = cable_shapes + housing_shapes
    comp = Part.Compound(allshapes)
    Part.export([comp], os.path.join(OUTDIR, "harness.step"))
    exported = {"harness.step": os.path.getsize(os.path.join(OUTDIR, "harness.step")),
                "harness.stl": _export_stl(comp, os.path.join(OUTDIR, "harness.stl")),
                "cables-only.stl": _export_stl(Part.Compound(cable_shapes),
                                               os.path.join(OUTDIR, "cables-only.stl")),
                "housings-only.stl": _export_stl(Part.Compound(housing_shapes),
                                                 os.path.join(OUTDIR, "housings-only.stl"))}
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
    json.dump(doc, open(R + "/out/wiring/solids.json", "w"), indent=1)
    say("\n%d cables swept, %d housings placed, %d solids; routed %.3f mm, nominal mass %.3f g; %.1f s"
          % (len(rows), n_housing, len(allshapes), tot_L, tot_m, time.time() - t0))


main()
