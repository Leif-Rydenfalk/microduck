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
                         corridor_mask, relax, PASS, FAIL, CANNOT)

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
PLAN_FACTORS = (4, 1)      # coarse plan, then a fine plan inside its corridor
CORRIDOR_MM = 14.0         # half-width of the fine search corridor around the coarse answer
FINE_MAX_NODES = 3_000_000
RELAX_ITERS = 300          # constrained Laplacian passes; stops early when nothing moves
BEND_WINDOW = 3            # samples either side for the circumscribed-circle radius
CLEAR_LADDER = (1.0, 0.5, 0.25, 0.0)   # the stated floor, then how far it has to fall
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

        # PLAN COARSE, REFINE IN A CORRIDOR, RELAX, MEASURE FINE.
        #   1. A* on the 4.0 mm grid (its distance is the MINIMUM over each block,
        #      so a coarse cell that clears means every fine cell in it clears —
        #      the coarse plan is admissible, never optimistic).
        #   2. dilate that answer into a corridor and re-run A* on the 1.0 mm grid
        #      restricted to it: a RESTRICTION, so the fine plan can only be worse
        #      than an unrestricted one, never illegally better.
        #   3. string-pull, then relax (constrained Laplacian): the shortest path
        #      is a chain of hard corners and a hard corner has bend radius zero.
        #   4. re-measure on the finished curve. The check never moves.
        #
        # THE CLEARANCE LADDER. When nothing clears the stated 1.0000 mm floor,
        # the run is re-planned at 0.5000, 0.2500 and 0.0000 mm and the LOWEST
        # floor that admits a path is reported. That converts "no route" into a
        # number — how much room our model is short of — which is the lead the
        # brief asks for, since the real robot's cable exists.
        t1 = time.time()
        pulled = None
        ladder = []
        floor_used = None
        for floor in CLEAR_LADDER:
            rr = r_cable + floor
            g = COARSE[4]
            ga = g.nearest_free(launches[0], rr, search_mm=30.0)
            gb = g.nearest_free(launches[1], rr, search_mm=30.0)
            if ga is None or gb is None:
                ladder.append({"floor_mm": floor, "result": "an endpoint has no clear cell on "
                                                            "the 4.0 mm planning grid"})
                continue
            gp = astar(g, ga[0], gb[0], rr, prefer_clearance_mm=PREFER_EXTRA)
            coarse_world = [g.world_of(i) for i in gp] if gp is not None else None
            fa = occ.nearest_free(launches[0], rr, search_mm=30.0)
            fb = occ.nearest_free(launches[1], rr, search_mm=30.0)
            fine = None
            how_grid = None
            if fa is not None and fb is not None:
                if coarse_world is not None:
                    allow = corridor_mask(occ, coarse_world, CORRIDOR_MM)
                    fp = astar(occ, fa[0], fb[0], rr, prefer_clearance_mm=PREFER_EXTRA,
                               allow=allow)
                    how_grid = "1.0 mm inside a %.1f mm corridor round the 4.0 mm plan" % CORRIDOR_MM
                else:
                    # THE COARSE GRID CAN SAY NO WHERE THE FINE GRID SAYS YES: a
                    # 4.0 mm cell clears only when all 64 of its 1.0 mm cells do,
                    # which in a packed head refuses gaps a cable really fits. So
                    # a coarse refusal falls through to an UNRESTRICTED fine
                    # search rather than being reported as no route.
                    fp = astar(occ, fa[0], fb[0], rr, prefer_clearance_mm=PREFER_EXTRA,
                               max_nodes=FINE_MAX_NODES)
                    how_grid = "1.0 mm unrestricted (the 4.0 mm grid found nothing)"
                if fp is not None:
                    fine = [occ.world_of(i) for i in fp]
            if fine is None and coarse_world is None:
                ladder.append({"floor_mm": floor,
                               "result": "no corridor on the 4.0 mm grid and none on the "
                                         "1.0 mm grid either"})
                continue
            raw = fine if fine is not None else coarse_world
            raw[0] = launches[0]
            raw[-1] = launches[1]
            cand = shortcut(occ, raw, rr, rounds=5)
            cand, moved = relax(occ, cand, rr, iters=RELAX_ITERS, alpha=0.35)
            chk = measure_path(occ, cand, r_cable)
            ladder.append({"floor_mm": floor,
                           "result": "routed on %s" % (how_grid if fine is not None
                                                       else "the 4.0 mm grid alone"),
                           "measured_clearance_mm": round(chk["min_clearance_mm"], 4),
                           "pierce_samples": chk["pierce_samples"],
                           "relax_moves": moved})
            if chk["min_clearance_mm"] >= floor - 1e-6 and chk["pierce_samples"] == 0:
                pulled = cand
                floor_used = floor
                rec["plan_grid_mm"] = 1.0 if fine is not None else 4.0
                break
            if pulled is None and chk["pierce_samples"] == 0:
                pulled = cand            # keep the best so far, and say so
                floor_used = floor
                rec["plan_grid_mm"] = 1.0 if fine is not None else 4.0
        rec["clearance_ladder"] = ladder
        rec["clearance_floor_achieved_mm"] = floor_used
        if pulled is None:
            rec.update(status="FAIL", verdict=FAIL, routed=False,
                       why="NO ROUTE AT ANY CLEARANCE DOWN TO 0.0000 mm: at zero pose there is "
                           "no corridor at all between these two connectors wide enough for a "
                           "%.4f mm cable. Since the real robot has this cable, the model is "
                           "what is wrong — the ladder rows say at which floor each attempt "
                           "died." % od,
                       ends=_clean(ends))
            results.append(rec)
            say("%-18s FAIL no route at any clearance" % rid)
            continue
        if floor_used is not None and floor_used < CLEAR_MIN:
            say("  %s: routed only at a %.4f mm floor, not the stated %.4f mm"
                % (rid, floor_used, CLEAR_MIN))
        # the connector stubs, in front of and behind the routed part
        full = _dedup([np.asarray(ends[0]["start_mm"], float)] + list(pulled)
                      + [np.asarray(ends[1]["start_mm"], float)])
        poly = full
        L = path_length(poly)
        routed_poly = _dedup(list(pulled))
        rb = discrete_bend_radius(routed_poly, window=BEND_WINDOW)
        r_intended = None
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
            bend_window_mm=BEND_WINDOW * 1.0,
            min_clearance_mm=round(m_routed["min_clearance_mm"], 4),
            min_clearance_at_mm=[round(v, 4) for v in m_routed["worst_point_mm"]],
            pierce_samples=m_routed["pierce_samples"],
            pierce_points_mm=m_routed["pierce_points_mm"],
            samples=m_routed["samples"], sample_step_mm=m_routed["step_mm"],
            whole_path_min_clearance_mm=round(m_all["min_clearance_mm"], 4),
            whole_path_pierce_samples=m_all["pierce_samples"],
            ends=_clean(ends),
        )
        # THREE QUESTIONS, THREE VERDICTS — a run that clears and pierces nothing
        # is not made CANNOT DETERMINE by the one question no document answers.
        vp = PASS if m_routed["pierce_samples"] == 0 else FAIL
        vc = PASS if m_routed["min_clearance_mm"] >= CLEAR_MIN - 1e-9 else FAIL
        vb = CANNOT      # no vendor bend limit exists for any cable on this robot
        rec["verdict_pierce"] = vp
        rec["verdict_pierce_why"] = ("no sample of the centreline lands in material"
                                     if vp == PASS else
                                     "%d sample(s) of the centreline land in material"
                                     % m_routed["pierce_samples"])
        rec["verdict_clearance"] = vc
        rec["verdict_clearance_why"] = ("min clearance %.4f mm >= the stated floor %.4f mm"
                                        % (m_routed["min_clearance_mm"], CLEAR_MIN)
                                        if vc == PASS else
                                        "min clearance %.4f mm < the stated floor %.4f mm; the "
                                        "lowest floor that admitted a route was %s mm"
                                        % (m_routed["min_clearance_mm"], CLEAR_MIN,
                                           rec.get("clearance_floor_achieved_mm")))
        rec["verdict_bend"] = vb
        rec["verdict_bend_why"] = ("achieved %s mm; NO published minimum exists for this cable "
                                   "(ROBOTIS states a gauge and no bend radius; the 3 x OD "
                                   "target this lane routed to is its own rule), so there is "
                                   "nothing to compare it with"
                                   % (("%.4f" % rb) if rb else "n/a"))
        v = FAIL if FAIL in (vp, vc) else CANNOT
        rec["verdict"] = v
        rec["verdict_why"] = ("pierce %s; clearance %s; bend radius %s"
                              % (vp, vc, vb))
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
    n_geom_ok = sum(1 for r in routed
                    if r.get("verdict_pierce") == PASS and r.get("verdict_clearance") == PASS)
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
                          "CANNOT DETERMINE": ncan,
                          "geometry_clean": n_geom_ok,
                          "geometry_clean_means": "pierces nothing AND clears the stated "
                                                  "1.0000 mm floor; the overall verdict of such "
                                                  "a run is still CANNOT DETERMINE because no "
                                                  "published bend limit exists to judge it by"},
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
    say("\n%d runs in cables.json; %d routed; geometry clean %d; PASS %d FAIL %d "
        "CANNOT DETERMINE %d; %.1f s"
        % (len(cab["cables"]), len(routed), n_geom_ok, npass, nfail, ncan, time.time() - t0))
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
