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
from cecad.route import Occupancy, fillet_corners, sweep_solid, polyline_of, path_length

import FreeCAD as App
import Part

OCC_NPZ = "/private/tmp/int-wire3d/occ.npz"
OUTDIR = R + "/out/wiring/cad"
CLEAR_MIN = 1.0

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
    print("part:jst-ehr-03 built: bbox %s volume %.4f mm3"
          % ([round(v, 4) for v in (base_housing.BoundBox.XLength, base_housing.BoundBox.YLength,
                                    base_housing.BoundBox.ZLength)], base_housing.Volume))

    cable_shapes, housing_shapes, rows = [], [], []
    n_housing = 0
    for rid, p in sorted(paths.items()):
        od = p["od_mm"]
        r_req = od / 2.0 + CLEAR_MIN
        wp = [np.asarray(x, float) for x in p["waypoints_mm"]]
        segs, r_int = fillet_corners(wp, p["bend_target_mm"], occ=occ, r_clear_mm=r_req)
        shape, how = sweep_solid(segs, od, name=rid)
        poly = polyline_of(segs, arc_steps=16)
        L = path_length(poly)
        vol = shape.Volume
        # mass, from the geometry and two named densities
        n_cond = 3 if rid.startswith("dxl") else 2
        a_cu = math.pi * (BARE_D_21 / 2.0) ** 2                    # mm2 per conductor
        m_cu = a_cu * n_cond * L * 1e-3 * RHO_CU                   # mm3 -> cm3 = 1e-3
        a_ins = math.pi * ((INS_OD_NOM / 2.0) ** 2 - (BARE_D_21 / 2.0) ** 2)
        m_pvc = a_ins * n_cond * L * 1e-3 * RHO_PVC
        cable_shapes.append(shape)
        Part.export([shape], os.path.join(OUTDIR, rid + ".stl"))
        row = {"id": rid, "od_mm": od, "swept_by": how,
               "length_mm": round(L, 4), "volume_mm3": round(vol, 4),
               "envelope_volume_check_mm3": round(math.pi * (od / 2.0) ** 2 * L, 4),
               "fillet_radius_mm": (round(r_int, 4) if r_int else None),
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
        print("%-18s swept %-14s L %8.3f mm  vol %10.2f mm3  housings %d  mass %.3f g"
              % (rid, how, L, vol, len(row["housings"]), m_cu + m_pvc))

    allshapes = cable_shapes + housing_shapes
    comp = Part.Compound(allshapes)
    Part.export([comp], os.path.join(OUTDIR, "harness.step"))
    Part.export([comp], os.path.join(OUTDIR, "harness.stl"))
    Part.export([Part.Compound(cable_shapes)], os.path.join(OUTDIR, "cables-only.stl"))
    Part.export([Part.Compound(housing_shapes)], os.path.join(OUTDIR, "housings-only.stl"))
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
               "exports": ["out/wiring/cad/harness.step", "out/wiring/cad/harness.stl",
                           "out/wiring/cad/cables-only.stl", "out/wiring/cad/housings-only.stl"],
               "cables": rows}}
    json.dump(doc, open(R + "/out/wiring/solids.json", "w"), indent=1)
    print("\n%d cables swept, %d housings placed, %d solids; routed %.3f mm, nominal mass %.3f g; %.1f s"
          % (len(rows), n_housing, len(allshapes), tot_L, tot_m, time.time() - t0))


main()
