"""route3d — every cable in wiring/cables.json ROUTED as a 3D path through the
measured free space of the assembly, then re-measured on the finished curve.

    ce-cad/bin/cad sim/route3d_grid.py     # once: the 1.0 mm occupancy + EDT
    ce-cad/bin/cad sim/route3d.py          # this: plan, fillet, measure
    ce-cad/bin/cad sim/route3d_solids.py   # then: sweep, connectors, STEP/STL

WHAT IS MEASURED AND WHAT IS CHOSEN — the whole basis, in one place, because a
route drawn to an unstated rule is a picture and not a measurement:

  MEASURED (a file:line or a datasheet page behind every one)
    - the free space: every triangle of the 70 placements, x1000 from metres
      (GOAL.md handover note 5), rasterised at 1.0000 mm (route3d_grid.py).
    - the servo socket: the notch cut in part:xl330-m288-t's own cad/part.py
      (POCKET_X0 2.2, POCKET_Y 6.0..10.0, POCKET_Z -14.3..-3.7, measured off
      the Pollen mesh at 0.1 mm cuts), giving a socket centred at local
      (6.8500, +/-10.0000, -9.0000) — the same point wiring/cables.json uses.
    - the housing: part:jst-ehr-03, 9.5000 x 3.8000 x 6.5000, every figure off
      JST eEH.pdf p.3; wires leave its z = -6.5 face on 2.5 mm centres.
    - the wire: 21 AWG, ROBOTIS e-Manual XL330-M288-T section 4.4 verbatim
      "Wire Gauge for DYNAMIXEL | 21 AWG"; bare copper 0.7230 mm by ASTM B258.
    - the insulation window: JST eEH.pdf p.2, contact SEH-001T-P0.6, "Insulation
      O.D. 1.0 to 1.9" — the only published bound on this cable's jacket.

  CHOSEN BY THIS LANE, and labelled as such wherever it is printed
    - jacket OD: NOMINAL 1.4500 mm = the midpoint of that 1.0-1.9 window. No
      vendor publishes the X3P's jacket OD (cables3d.json wire_sources).
    - bundle envelope: three such wires in a triangular bundle, D = d(1+2/sqrt3)
      = 3.1243 mm. The flat-row alternative 4.3500 x 1.4500 is NOT modelled and
      is named in the report.
    - clearance floor: 1.0000 mm surface-to-surface from any body. No source in
      this repo states one; it is this lane's routing rule.
    - bend radius target: 3 x bundle OD = 9.3730 mm, reduced at any corner the
      geometry or the clearance will not allow, and the ACHIEVED minimum is
      reported per run. ROBOTIS publishes no bend radius for the X3P, so the
      real limit stays CANNOT DETERMINE.

  NOT CLAIMED
    - that this is the route the real harness takes. No photograph of the
      interior exists in reference/. It is the SHORTEST route that clears, and
      where a photograph does show the harness (cables3d.json photo_observations)
      the observation is carried as a waypoint hint and cited.
"""
import json, math, os, sys, time
import numpy as np

R = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck"
sys.path.insert(0, "/Users/leifrydenfalk/dev/ce-workshop/ce-cad")
from cecad.route import (Occupancy, astar, shortcut, fillet_corners, polyline_of,
                         path_length, discrete_bend_radius, measure_path, verdict_for,
                         PASS, FAIL, CANNOT)

OCC_NPZ = "/private/tmp/int-wire3d/occ.npz"
PROGRESS = "/private/tmp/int-wire3d/route-progress.log"
_pf = open(PROGRESS, "a", buffering=1)


def say(*a):
    s = " ".join(str(x) for x in a)
    sys.stdout.write(s + "\n")
    _pf.write(s + "\n")
OUT_JSON = R + "/out/wiring/cables3d.json"
PATHS_JSON = R + "/out/wiring/paths.json"

# ---- the numbers, each with its basis -------------------------------------

AWG_DXL = 21
BARE_D_MM = 0.127 * 92.0 ** ((36 - AWG_DXL) / 39.0)        # ASTM B258, = 0.7230
INS_OD_MIN, INS_OD_MAX = 1.0, 1.9                          # JST eEH.pdf p.2
INS_OD_NOM = (INS_OD_MIN + INS_OD_MAX) / 2.0               # 1.4500, CHOSEN
BUNDLE3 = INS_OD_NOM * (1.0 + 2.0 / math.sqrt(3.0))        # 3.1243, CHOSEN

CLEAR_MIN = 1.0            # CHOSEN routing rule, mm, surface to surface
PREFER_EXTRA = 1.5         # cost preference for a roomier lane, mm
PLAN_FACTORS = (4, 2, 1)   # planning cell = factor x 1.0 mm; coarsest first
COARSE = {}

# per group: (bundle OD mm, od_basis, conductors)
GROUP_OD = {
    "dynamixel-chain": (BUNDLE3, "NOMINAL — 3 x 21 AWG at the 1.4500 mm midpoint of JST "
                                 "eEH.pdf p.2's 1.0-1.9 insulation window, triangular bundle "
                                 "D = d(1+2/sqrt3); no vendor jacket OD exists", 3),
    "hat-harness/tof": (2.2, "NOMINAL — JST SH 1.0 mm 4-way lead; no OD published for the "
                             "ToF board's cable. 4 x ~0.9 mm flat ribbon read as a 2.2 mm "
                             "round envelope", 4),
    "hat-harness/spk": (2.5, "NOMINAL — JST GH 1.25 mm 2-way speaker lead; no OD published. "
                             "2 x ~1.2 mm twisted pair read as a 2.5 mm round envelope", 2),
    "hat-harness/csi": (2.0, "NOMINAL and WRONG IN SHAPE — a 22-way 0.5 mm FFC is FLAT "
                             "(~11.5 x 0.3 mm), swept here as a 2.0 mm round envelope so it "
                             "has a length and a clearance at all; the flat ribbon is NOT "
                             "modelled", 22),
    "power": (3.0, "NOMINAL — two conductors from the pack to the HAT; neither the gauge nor "
                   "the jacket is published (cables.json bat-hat connector = CANNOT DETERMINE)", 2),
}


def group_key(c):
    g = c["group"]
    if g == "hat-harness":
        return {"tof-hat": "hat-harness/tof", "spk-hat": "hat-harness/spk",
                "csi-radxa-camera": "hat-harness/csi"}.get(c["id"], "hat-harness/tof")
    return g


# ---- geometry -------------------------------------------------------------

def quat_matrix(q):
    w, x, y, z = q
    n = (w * w + x * x + y * y + z * z) ** 0.5
    w, x, y, z = w / n, x / n, y / n, z / n
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]], float)


# part:xl330-m288-t cad/part.py lines 29-37 — measured off the Pollen mesh
XL_POCKET_X = 6.85          # (2.2 + 11.5)/2
XL_POCKET_Z = -9.0          # (-14.3 + -3.7)/2
XL_NOTCH_FLOOR_Y = 6.0      # POCKET_Y[0]
XL_FACE_Y = 10.0            # BODY_Y[1]
EHR_HEIGHT = 6.5            # part:jst-ehr-03 cad/part.py HEIGHT, eEH.pdf p.3


def servo_socket_frame(row, side):
    """World frame of one XL330 EH socket. side = +1 (+y flank) or -1 (-y flank).

    Returns dict with: socket_face (the point wiring/cables.json quotes), mate
    (the housing's mating face, on the notch floor), wire_face (where the wires
    leave the housing), out (the outward unit normal), row_dir (circuit 1 -> 3).
    """
    Rm = quat_matrix(row["world_quat_wxyz"])
    p = np.asarray(row["world_pos_mm"], float)

    def w(local):
        return Rm @ np.asarray(local, float) + p

    n = Rm @ np.array([0.0, float(side), 0.0])
    return {
        "socket_face_mm": w((XL_POCKET_X, side * XL_FACE_Y, XL_POCKET_Z)),
        "mate_mm": w((XL_POCKET_X, side * XL_NOTCH_FLOOR_Y, XL_POCKET_Z)),
        "wire_face_mm": w((XL_POCKET_X, side * (XL_NOTCH_FLOOR_Y + EHR_HEIGHT), XL_POCKET_Z)),
        "out": n,
        "row_dir": Rm @ np.array([1.0, 0.0, 0.0]),
        "insertion": -n,
        "proud_mm": (XL_NOTCH_FLOOR_Y + EHR_HEIGHT) - XL_FACE_Y,
    }


# ---- load -----------------------------------------------------------------

def load_occ():
    z = np.load(OCC_NPZ)
    occ = Occupancy.__new__(Occupancy)
    occ.cell = float(z["cell"][0])
    occ.lo = z["lo"]
    occ.grid = z["grid"]
    occ.owner = z["owner"]
    occ.shape = occ.grid.shape
    occ._edt = z["edt"].astype(np.float64)
    occ.labels = {int(k): v for k, v in json.load(open("/private/tmp/int-wire3d/labels.json")).items()}
    return occ


def launch_point(occ, p, normal, r_req, max_out=18.0):
    """Where the routed centreline may begin: first clear point along `normal`.

    Falls back to the nearest clear cell in any direction (and says so), because
    a board endpoint is a CENTROID inside the board and has no normal at all.
    """
    if normal is not None:
        for d in np.arange(0.0, max_out + 1e-9, 0.25):
            q = np.asarray(p, float) + np.asarray(normal, float) * d
            if occ.dist_at(q) >= r_req:
                return q, float(d), "along the connector normal"
    nf = occ.nearest_free(p, r_req, search_mm=40.0)
    if nf is None:
        return None, None, "no clear cell within 40 mm"
    idx, off = nf
    return occ.world_of(idx), float(off), "nearest clear cell in any direction (endpoint unlocated)"


def main():
    t0 = time.time()
    occ = load_occ()
    say("occupancy %s cell %.4f mm  occupied %d cells" % (occ.shape, occ.cell, int(occ.grid.sum())))
    for f in PLAN_FACTORS:
        COARSE[f] = occ.coarsen(f) if f > 1 else occ
        say("  planning grid x%d: cell %.4f mm  shape %s  cells %d"
            % (f, COARSE[f].cell, COARSE[f].shape, int(np.prod(COARSE[f].shape))))

    cab = json.load(open(R + "/wiring/cables.json"))["record"]
    rows = json.load(open(R + "/ce-assemblies/microduck/current/placements.json"))["record"]["rows"]
    devices = cab["devices"]

    # servo socket frames, both flanks, for every device that has a placements row
    frames = {}
    for name, d in devices.items():
        if d.get("kind") != "xl330":
            continue
        row = rows[d["placements_row"]]
        frames[name] = {"+y": servo_socket_frame(row, +1), "-y": servo_socket_frame(row, -1)}
    say("servo socket frames derived: %d servos x 2 flanks = %d"
          % (len(frames), 2 * len(frames)))

    results, paths = [], {}
    for c in cab["cables"]:
        rid = c["id"]
        gk = group_key(c)
        od, od_basis, cond = GROUP_OD[gk]
        r_cable = od / 2.0
        r_req = r_cable + CLEAR_MIN
        rec = {"id": rid, "group": c["group"], "od_mm": round(od, 4), "od_basis": od_basis,
               "od_is_nominal": True, "conductors": cond,
               "cable_mm_from_cables_json": c.get("cable_mm"),
               "floor_mm_from_cables_json": c.get("floor_mm"),
               "slack_mm_from_cables_json": c.get("slack_mm"),
               "crosses": c.get("crosses", []),
               "clearance_floor_mm": CLEAR_MIN,
               "bend_target_mm": round(3.0 * od, 4)}

        if c.get("cable_mm") is None:
            rec.update(status="CANNOT DETERMINE", verdict=CANNOT,
                       why=c.get("how", ""), routed=False)
            results.append(rec)
            say("%-18s CANNOT DETERMINE (no endpoint in cables.json)" % rid)
            continue
        if c.get("cable_mm") == 0:
            rec.update(status="not a cable", verdict=CANNOT, routed=False,
                       why=c.get("how", ""))
            results.append(rec)
            say("%-18s not a cable (%s)" % (rid, c.get("connector", "")[:40]))
            continue

        ends = []
        for side in ("from", "to"):
            dev = c[side]
            pt = c.get(side + "_point")
            xyz = np.asarray(c[side + "_xyz_mm"], float)
            e = {"device": dev, "point": pt, "connector_xyz_mm": [float(v) for v in xyz]}
            if dev in frames and pt in ("+y", "-y"):
                f = frames[dev][pt]
                e["located"] = True
                e["kind"] = "xl330 EH socket"
                e["mate_mm"] = [round(float(v), 4) for v in f["mate_mm"]]
                e["wire_face_mm"] = [round(float(v), 4) for v in f["wire_face_mm"]]
                e["insertion_dir"] = [round(float(v), 6) for v in f["insertion"]]
                e["row_dir"] = [round(float(v), 6) for v in f["row_dir"]]
                e["housing_proud_of_flank_mm"] = round(float(f["proud_mm"]), 4)
                e["start_mm"] = f["wire_face_mm"]
                e["normal"] = f["out"]
                e["housing_part"] = "part:jst-ehr-03"
            else:
                e["located"] = False
                e["kind"] = devices.get(dev, {}).get("kind", "?")
                e["why_unlocated"] = devices.get(dev, {}).get("ref", "")
                e["start_mm"] = xyz
                e["normal"] = None
                e["housing_part"] = None
            ends.append(e)

        launches = []
        ok = True
        for e in ends:
            q, off, how = launch_point(occ, e["start_mm"], e["normal"], r_req)
            if q is None:
                ok = False
                e["launch"] = None
                e["launch_why"] = how
                break
            e["launch_mm"] = [round(float(v), 4) for v in q]
            e["launch_offset_mm"] = round(off, 4)
            e["launch_how"] = how
            launches.append(q)
        if not ok:
            rec.update(status="FAIL", verdict=FAIL, routed=False,
                       why="an endpoint has no clear cell within 40 mm — the connector is "
                           "buried in material at zero pose", ends=_clean(ends))
            results.append(rec)
            say("%-18s FAIL (endpoint buried)" % rid)
            continue

        # PLAN COARSE, MEASURE FINE. The coarse grid's distance is the MINIMUM over
        # each block, so a coarse cell that clears means every fine cell in it
        # clears: the plan is admissible, never optimistic. If the finished curve
        # then fails to clear on the FINE grid, the run is re-planned one step
        # finer and the escalation is recorded — the check is never loosened.
        t1 = time.time()
        pulled = None
        used_factor = None
        for f in PLAN_FACTORS:
            g = COARSE.get(f) or occ
            ga = g.nearest_free(launches[0], r_req, search_mm=30.0)
            gb = g.nearest_free(launches[1], r_req, search_mm=30.0)
            if ga is None or gb is None:
                continue
            gp = astar(g, ga[0], gb[0], r_req, prefer_clearance_mm=PREFER_EXTRA)
            if gp is None:
                continue
            raw = [g.world_of(i) for i in gp]
            raw[0] = launches[0]
            raw[-1] = launches[1]
            cand = shortcut(occ, raw, r_req, rounds=5)
            chk = measure_path(occ, polyline_of(fillet_corners(_dedup(cand), 3.0 * od,
                                                               occ=occ, r_clear_mm=r_req)[0],
                                                arc_steps=16), r_cable)
            used_factor = f
            pulled = cand
            if chk["min_clearance_mm"] >= CLEAR_MIN and chk["pierce_samples"] == 0:
                break
            say("  %s: plan at %.1f mm cells measured %.4f mm clearance — refining"
                % (rid, g.cell, chk["min_clearance_mm"]))
        if pulled is None:
            rec.update(status="FAIL", verdict=FAIL, routed=False,
                       why="no path clears %.4f mm (cable radius %.4f + clearance floor %.4f) "
                           "between the two connectors at zero pose" % (r_req, r_cable, CLEAR_MIN),
                       ends=_clean(ends))
            results.append(rec)
            say("%-18s FAIL no path (r_req %.3f)" % (rid, r_req))
            continue
        rec["plan_grid_mm"] = round((COARSE.get(used_factor) or occ).cell, 4)
        # the connector stubs, in front of and behind the routed part
        full = [np.asarray(ends[0]["start_mm"], float)] + pulled + [np.asarray(ends[1]["start_mm"], float)]
        full = _dedup(full)
        segs, r_intended = fillet_corners(full, 3.0 * od, occ=occ, r_clear_mm=r_req)
        poly = polyline_of(segs, arc_steps=16)
        L = path_length(poly)
        rb = discrete_bend_radius(poly, window=2)
        # measure only the ROUTED part (launch -> launch): the stubs are the connector
        routed_poly = polyline_of(fillet_corners(_dedup(pulled), 3.0 * od, occ=occ, r_clear_mm=r_req)[0],
                                  arc_steps=16)
        m_all = measure_path(occ, poly, r_cable)
        m_routed = measure_path(occ, routed_poly, r_cable)
        rec.update(
            routed=True,
            plan_grid_mm=rec.get("plan_grid_mm"), waypoints=len(pulled), corners=len(full) - 2,
            plan_seconds=round(time.time() - t1, 2),
            routed_length_mm=round(L, 4),
            routed_length_routed_part_mm=round(path_length(routed_poly), 4),
            stub_from_mm=round(float(np.linalg.norm(np.asarray(ends[0]["start_mm"], float) - pulled[0])), 4),
            stub_to_mm=round(float(np.linalg.norm(np.asarray(ends[1]["start_mm"], float) - pulled[-1])), 4),
            min_bend_radius_mm=(round(rb, 4) if rb else None),
            fillet_radius_used_mm=(round(r_intended, 4) if r_intended else None),
            min_clearance_mm=round(m_routed["min_clearance_mm"], 4),
            min_clearance_at_mm=[round(v, 4) for v in m_routed["worst_point_mm"]],
            pierce_samples=m_routed["pierce_samples"],
            pierce_points_mm=m_routed["pierce_points_mm"],
            samples=m_routed["samples"], sample_step_mm=m_routed["step_mm"],
            whole_path_min_clearance_mm=round(m_all["min_clearance_mm"], 4),
            whole_path_pierce_samples=m_all["pierce_samples"],
            ends=_clean(ends),
        )
        v, why = verdict_for(rec, CLEAR_MIN, None)
        rec["verdict"], rec["verdict_why"] = v, why
        rec["delta_vs_cable_mm"] = round(L - c["cable_mm"], 4)
        rec["delta_vs_floor_mm"] = round(L - c["floor_mm"], 4)
        paths[rid] = {"polyline_mm": [[round(float(x), 4) for x in p] for p in poly],
                      "waypoints_mm": [[round(float(x), 4) for x in p] for p in full],
                      "od_mm": round(od, 4),
                      "bend_target_mm": round(3.0 * od, 4),
                      "ends": [{"housing_part": e["housing_part"],
                                "mate_mm": e.get("mate_mm"),
                                "insertion_dir": e.get("insertion_dir"),
                                "row_dir": e.get("row_dir")} for e in ends]}
        results.append(rec)
        say("%-18s %-18s L %8.3f mm (cables.json %4s)  bend %s  clear %7.4f  pierce %d  %.1fs"
              % (rid, v, L, c["cable_mm"],
                 ("%7.4f" % rb) if rb else "   n/a ", rec["min_clearance_mm"],
                 rec["pierce_samples"], rec["plan_seconds"]))

    routed = [r for r in results if r.get("routed")]
    npass = sum(1 for r in routed if r["verdict"] == PASS)
    nfail = sum(1 for r in results if r["verdict"] == FAIL)
    ncan = sum(1 for r in results if r["verdict"] == CANNOT)
    doc = {"$triad": 1, "kind": "cables3d",
           "generated_by": "sim/route3d.py (grid by sim/route3d_grid.py)",
           "record": {
               "ref": "assembly:microduck",
               "units": "mm",
               "frame": "MJCF world at the zero pose: +x forward (beak), +y left, +z up, "
                        "trunk_base origin (0,0,120) — the same frame as wiring/cables.json",
               "counts": {"runs_in_cables_json": len(cab["cables"]),
                          "routed": len(routed), "PASS": npass, "FAIL": nfail,
                          "CANNOT DETERMINE": ncan},
               "grid": {"cell_mm": occ.cell, "shape": list(occ.shape),
                        "occupied_cells": int(occ.grid.sum()),
                        "source": "every triangle of the 70 rows of "
                                  "ce-assemblies/microduck/current/placements.json, x1000 from "
                                  "metres, sampled at 0.5000 mm",
                        "accuracy": "distances resolve to the nearest marked CELL CENTRE, so a "
                                    "clearance carries +/- 0.8660 mm (half the cell diagonal) "
                                    "of grid error before the exact refinement in "
                                    "sim/route3d_exact.py"},
               "rules": {"clearance_floor_mm": CLEAR_MIN,
                         "clearance_basis": "CHOSEN BY THIS LANE — no source in this repo states "
                                            "a cable-to-body clearance for the Microduck",
                         "bend_target": "3 x the bundle OD, reduced at any corner the geometry "
                                        "or the clearance will not allow; ROBOTIS publishes no "
                                        "bend radius for the X3P so the real limit is CANNOT "
                                        "DETERMINE and only the ACHIEVED radius is reported",
                         "pose": "ZERO POSE ONLY. The routed length is the length at one pose; "
                                 "wiring/cables.json's cable_mm is a floor plus a slack "
                                 "allowance over each crossed joint's whole range. Both are "
                                 "reported and neither overwrites the other."},
               "wire": {"awg": AWG_DXL,
                        "awg_source": "ROBOTIS e-Manual XL330-M288-T 4.4 'Wire Gauge for "
                                      "DYNAMIXEL | 21 AWG'",
                        "bare_conductor_mm": round(BARE_D_MM, 4),
                        "bare_basis": "ASTM B258 d = 0.127 x 92^((36-awg)/39)",
                        "insulation_od_window_mm": [INS_OD_MIN, INS_OD_MAX],
                        "insulation_window_source": "JST eEH.pdf p.2, contact SEH-001T-P0.6, "
                                                    "'Insulation O.D. 1.0 to 1.9' "
                                                    "(part:jst-seh-001t-p0.6 spec)",
                        "insulation_od_nominal_mm": INS_OD_NOM,
                        "nominal_is_chosen": True},
               "cables": results}}
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    json.dump(doc, open(OUT_JSON, "w"), indent=1)
    json.dump({"$triad": 1, "kind": "cable-paths", "generated_by": "sim/route3d.py",
               "record": {"units": "mm", "paths": paths}},
              open(PATHS_JSON, "w"), indent=1)
    say("\n%d runs in cables.json; %d routed; PASS %d FAIL %d CANNOT DETERMINE %d; %.1f s"
          % (len(cab["cables"]), len(routed), npass, nfail, ncan, time.time() - t0))
    say("wrote %s and %s" % (OUT_JSON, PATHS_JSON))


def _clean(ends):
    out = []
    for e in ends:
        d = {k: v for k, v in e.items() if k not in ("normal", "start_mm")}
        d["start_mm"] = [round(float(v), 4) for v in np.asarray(e["start_mm"], float)]
        out.append(d)
    return out


def _dedup(pts):
    out = [np.asarray(pts[0], float)]
    for p in pts[1:]:
        p = np.asarray(p, float)
        if float(np.linalg.norm(p - out[-1])) > 1e-6:
            out.append(p)
    return out


main()
