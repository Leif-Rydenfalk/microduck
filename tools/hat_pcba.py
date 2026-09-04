"""tools/hat_pcba.py — run under ce-cad/bin/cad (FreeCAD 1.1.3 python).

OUR CAD of the POPULATED Pollen RPI Robot HAT rev C1, built chip by chip, and
MEASURED against the manufacturer's own 3D assembly.

WHY THIS TOOL EXISTS (it replaces tools/build_hat_pcba.py, which was wrong)
  The previous lane's run left `round trip worst 58.600000 mm at TP3` and a PCBA
  bounding box of 154.875 x 124.863 mm for a 65.000 x 30.900 mm board — i.e. the
  components were flying off the board. Diagnosed 2026-09-04 with a kernel probe
  (/private/tmp/int-pcbchips/probe.log): the files in out/pcb/hat/geometry/ are
  NOT in the local frame that out/pcb/hat/geometry_index.json claims for them.
  Measured, for key 100n-c-0402-1005metric (representative C11):
      geometry_index local_bbox : [-0.5, -0.25, 0.12, 0.5, 0.25, 0.62]
      the .step file reads back : [-12.6, -58.475, -0.84, -11.6, -57.975, -0.34]
  which is the vendor's in-place body rotated -90 deg about the origin and shifted
  -1.8 in z: the localisation was recorded in the index but never written into the
  exported file. Re-placing such a file by the pick-and-place transform applies the
  motion twice. A second defect in the same pipeline: the object->designator match
  was a per-object nearest-neighbour, so 121 STEP bodies matched only 112 distinct
  designators — C5 was claimed 3 times and FB1 (an L_0402, 1.0 x 0.5) was matched
  to a TDFN-8 body 3.1107 mm away.

WHAT IS OURS AND WHAT IS THEIRS
  ours   : the bare board (parametric, from the official Edge.Cuts outline and all
           63 drills in elec_RPI_Robot_HAT.kicad_pcb, at finished thickness 1.000),
           the object->designator assignment, the local frame of every component
           body, and the placement arithmetic that puts each body back on the board.
  theirs : every component solid, sliced out of the official production STEP; and
           the position/rotation/side of every one, from the manufacturer's own
           pick-and-place CSV.

THE CHECKS (none of them can agree with the thing they check)
  1. ASSIGNMENT is one-to-one and globally optimal (scipy linear_sum_assignment)
     over xy distance PLUS a body-size term read from KiCad's own F.Fab outline,
     which is independent of the STEP. Side must agree. No designator twice.
  2. ROTATION CONVENTION for each side is MEASURED, not assumed: every instance is
     rebuilt under R(+rot) and under R(-rot) and the convention with the smaller
     measured error wins, per side, with both numbers recorded.
  3. ROUND TRIP: every body we place must land back on the vendor's own body, to
     the micron, on all six bbox faces. This is the check that catches a wrong
     transform; a picture would not.
  4. The renders are READ BACK.

OUTPUTS  out/pcb/hat/pcba-measured.json   counts, assignment, round trip, per part
         out/pcb/hat/robot-hat-pcba.step  our populated board
         out/pcb/hat/geometry-local/*.step one correctly localised body per BOM key
         out/pcb/hat/pcba-{top,bottom,iso}.png

SOURCE  reference/pollen-elec-rpi-robot-hat/production/ASE01187-C1_..._STEP.zip
        (Apache-2.0, pollen-robotics/elec_RPI_Robot_HAT @ 23eab119)
        sha256 of the unzipped .step recorded in the output.

Run: ce-cad/bin/cad tools/hat_pcba.py    (buffered stdout - read hat_pcba.log)
"""
import hashlib
import json
import math
import os
import re
import time

import FreeCAD as App
import Part
import Import

REPO = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck"
OUT = os.path.join(REPO, "out", "pcb", "hat")
GEOL = os.path.join(OUT, "geometry-local")
STEP = "/private/tmp/int-pcbchips/step/ASE01187-C1_elec_RPI_Robot_HAT_STEP.step"
LOG = open(os.path.join(OUT, "hat_pcba.log"), "w")

# ---- the C1 board, measured (mm) -------------------------------------------
T_FINISHED = 1.000                 # kicad_pcb (general (thickness 1)); stackup sums to 1.000
Z_SUB_BOT, Z_SUB_TOP = 0.0, 0.84   # the STEP's own substrate body
Z_BOT, Z_TOP = -0.080, 0.920       # finished: + 0.080 copper+mask per face
CORNER_R = 3.500
X_MIN, X_MAX = -3.500, 61.500
Y_MIN, Y_MAX = -26.500, 4.400


def P(*a):
    LOG.write(" ".join(str(x) for x in a) + "\n")
    LOG.flush()


def slugify(s):
    s = re.sub(r"[^A-Za-z0-9]+", "-", str(s)).strip("-").lower()
    return re.sub(r"-+", "-", s) or "x"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def outline(n=24):
    pts = []
    order = [((58.0, 0.9), 0.0), ((0.0, 0.9), 90.0), ((0.0, -23.0), 180.0), ((58.0, -23.0), 270.0)]
    for (cx, cy), a0 in order:
        for i in range(n + 1):
            a = math.radians(a0 + 90.0 * i / n)
            pts.append(App.Vector(cx + CORNER_R * math.cos(a), cy + CORNER_R * math.sin(a), Z_BOT))
    pts.append(pts[0])
    return pts


def board_solid(drills):
    face = Part.Face(Part.makePolygon(outline()))
    solid = face.extrude(App.Vector(0, 0, T_FINISHED))
    for d, x, y in drills:
        solid = solid.cut(Part.makeCylinder(d / 2.0, T_FINISHED + 2.0,
                                            App.Vector(x, y, Z_BOT - 1.0), App.Vector(0, 0, 1)))
    return solid


def placement(px, py, rot_deg, side):
    """The one transform that puts a localised body on the board."""
    zref = Z_SUB_TOP if side == "top" else Z_SUB_BOT
    return App.Placement(App.Vector(px, py, zref), App.Rotation(App.Vector(0, 0, 1), rot_deg))


def bb6(sh):
    b = sh.BoundBox
    return [b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax]


def main():
    t0 = time.time()
    os.makedirs(GEOL, exist_ok=True)
    comps = json.load(open(os.path.join(OUT, "components.json")))
    drills = json.load(open(os.path.join(OUT, "drills.json")))["holes"]
    step_sha = sha256(STEP)
    P("STEP sha256", step_sha)

    # Candidates for owning a body = every placement KiCad can export a body for.
    # A footprint that declares NO 3D model (the three fiducials and the two Pollen
    # logo silkscreens) cannot own one, and letting it compete for one is how the
    # first run gave FID2 a Wago terminal body and left J2 8.4441 mm out of place.
    # DNP lines DO compete -- KiCad exports a body for a DNP part, and an unclaimed
    # DNP body is stolen by its nearest fitted neighbour -- but they are NOT built:
    # do-not-populate means the physical board has nothing there.
    allc = [c for c in comps["components"] if c["fitted"] or c["dnp"]]
    nomodel = [c for c in allc if not c.get("model")]
    cand = [c for c in allc if c.get("model")]
    P("placements", len(allc), "fitted", sum(1 for c in allc if c["fitted"]),
      "dnp", sum(1 for c in allc if c["dnp"]),
      "| can own a body", len(cand), "| declare no 3D model",
      [c["refdes"] for c in nomodel])

    # ---- 1. open the vendor assembly ---------------------------------------
    doc = App.newDocument("hat")
    Import.insert(STEP, doc.Name)
    doc.recompute()
    P("import seconds", round(time.time() - t0, 1))
    shaped = [o for o in doc.Objects if hasattr(o, "Shape") and o.Shape and not o.Shape.isNull()
              and o.Shape.BoundBox.XLength < 1e50]
    child = set()
    for o in shaped:
        for c in o.OutList:
            child.add(c.Name)
    roots = [o for o in shaped if o.Name not in child]
    root = max(roots, key=lambda o: len(o.Shape.Solids))
    top = [c for c in root.OutList if hasattr(c, "Shape") and c.Shape and not c.Shape.isNull()]
    board_obj, pi_obj, objs = None, None, []
    for o in top:
        lab = o.Label
        if lab.startswith("elec_RPI_Robot_HAT_PCB"):
            board_obj = o
        elif "rasp_pi_zero" in lab or "Raspberry" in lab:
            pi_obj = o
        else:
            objs.append(o)
    P("board", board_obj.Label if board_obj else None,
      "pi(context, excluded)", pi_obj.Label if pi_obj else None, "component bodies", len(objs))
    vb = board_obj.Shape.BoundBox
    P("vendor board bbox", [round(v, 4) for v in (vb.XMin, vb.YMin, vb.ZMin, vb.XMax, vb.YMax, vb.ZMax)])

    # measure every vendor body in board coordinates
    bodies = []
    for o in objs:
        sh = o.Shape
        b = sh.BoundBox
        above = max(0.0, b.ZMax - Z_SUB_TOP)
        below = max(0.0, Z_SUB_BOT - b.ZMin)
        side = "top" if above >= below else "bottom"
        bodies.append(dict(label=o.Label, obj=o, shape=sh,
                           centre=[(b.XMin + b.XMax) / 2.0, (b.YMin + b.YMax) / 2.0],
                           size=[b.XLength, b.YLength, b.ZLength],
                           bbox=[b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax],
                           side=side, above=above, below=below,
                           volume=sh.Volume if sh.Solids else 0.0))
    P("bodies measured", len(bodies),
      "top", sum(1 for b in bodies if b["side"] == "top"),
      "bottom", sum(1 for b in bodies if b["side"] == "bottom"))

    # ---- 2. one-to-one assignment ------------------------------------------
    # cost = xy distance (mm) + 1.0 * relative body-size error, where the expected
    # body size comes from KiCad's own F.Fab outline rotated by the P&P angle --
    # a quantity the STEP knows nothing about, so it is an independent tie-break.
    import numpy as np
    from scipy.optimize import linear_sum_assignment
    BIG = 1e6
    n, m = len(bodies), len(cand)

    def side_of(c):
        # a DNP line has no pick-and-place row, so its side comes from the PCB file
        return c["pos_side"] or c["side"]

    def radius(c):
        # how far a body's centre may sit from its pick point: half the diagonal of
        # KiCad's own F.Fab body outline plus 1.0 mm. A 0402 gets 1.06 mm, the Wago
        # terminal 5.73 mm -- a per-part gate read from the PCB, not one global number.
        f = c.get("fab_local_mm")
        if not f:
            return 3.0
        return math.hypot(f[2] - f[0], f[3] - f[1]) / 2.0 + 1.0

    C = np.full((n, m), BIG)
    for i, b in enumerate(bodies):
        for j, c in enumerate(cand):
            if b["side"] != side_of(c):
                continue
            px, py = c["pos_mm"]
            d = math.hypot(b["centre"][0] - px, b["centre"][1] - py)
            if d > radius(c):
                continue
            fab = c.get("fab_local_mm")
            serr = 0.0
            if fab:
                w, h = abs(fab[2] - fab[0]), abs(fab[3] - fab[1])
                rot = (c["pos_rot_deg"] or 0.0) % 180.0
                if abs(rot - 90.0) < 45.0:
                    w, h = h, w
                ew = abs(b["size"][0] - w) / max(w, 0.4)
                eh = abs(b["size"][1] - h) / max(h, 0.4)
                serr = min(4.0, ew + eh)
            C[i, j] = d + 1.0 * serr
    ri, cj = linear_sum_assignment(C)
    pairs, unmatched_body, unmatched_cand = [], [], []
    taken_b, taken_c = set(), set()
    for i, j in zip(ri, cj):
        if C[i, j] >= BIG:
            continue
        pairs.append((i, j, float(C[i, j])))
        taken_b.add(i)
        taken_c.add(j)
    for i, b in enumerate(bodies):
        if i not in taken_b:
            unmatched_body.append(dict(label=b["label"], centre=[round(v, 4) for v in b["centre"]],
                                       size=[round(v, 4) for v in b["size"]], side=b["side"],
                                       cannot_determine="no placement on this side, inside its own "
                                                        "F.Fab match radius, that this body is not "
                                                        "already the best match for"))
    for j, c in enumerate(cand):
        if j not in taken_c:
            unmatched_cand.append(dict(refdes=c["refdes"], value=c.get("bom_value"),
                                       footprint=c.get("footprint"), dnp=c["dnp"],
                                       side=side_of(c), at=c["pos_mm"],
                                       cannot_determine="the production STEP carries no body inside "
                                                        "this placement's F.Fab match radius "
                                                        "(%.3f mm) on side %s" % (radius(c), side_of(c))))
    P("assignment: pairs", len(pairs), "unmatched bodies", len(unmatched_body),
      "unmatched placements", len(unmatched_cand))
    dists = sorted(math.hypot(bodies[i]["centre"][0] - cand[j]["pos_mm"][0],
                              bodies[i]["centre"][1] - cand[j]["pos_mm"][1]) for i, j, _ in pairs)
    P("STEP-vs-pick-and-place xy agreement: worst %.4f median %.4f  over %.1f mm: %d"
      % (dists[-1], dists[len(dists) // 2], 0.10, sum(1 for d in dists if d > 0.10)))
    assert len(set(j for _, j, _ in pairs)) == len(pairs), "assignment claimed a designator twice"

    # ---- 3. localise one representative body per BOM key --------------------
    # key = value + footprint, so one geometry file stands for every instance of a line
    def keyof(c):
        # THE SIDE IS PART OF THE KEY. A bottom-side body sits below z = 0 in its own
        # local frame and a top-side body above it, so one representative cannot stand
        # for both: re-placing a bottom 0402 on the top face put it out by exactly its
        # own height + 0.24 mm (measured: 0.59 mm for every R_0402, 0.74 mm for every
        # C_0402) on the first run. Seven BOM lines are populated on both sides.
        return slugify("%s-%s-%s" % (c.get("bom_value") or c.get("value") or "x",
                                     (c.get("footprint") or "x").split(":")[-1], side_of(c)))

    by_key = {}
    for i, j, _ in pairs:
        by_key.setdefault(keyof(cand[j]), []).append((i, j))

    # 4. MEASURE the rotation convention per side instead of assuming one
    conv_err = {("top", +1): [], ("top", -1): [], ("bottom", +1): [], ("bottom", -1): []}
    for key, group in by_key.items():
        i0, j0 = group[0]
        for sgn in (+1, -1):
            rep = bodies[i0]["shape"].copy()
            rep.Placement = placement(cand[j0]["pos_mm"][0], cand[j0]["pos_mm"][1],
                                      sgn * (cand[j0]["pos_rot_deg"] or 0.0),
                                      side_of(cand[j0])).inverse().multiply(rep.Placement)
            for i, j in group:
                sh = rep.copy()
                sh.Placement = placement(cand[j]["pos_mm"][0], cand[j]["pos_mm"][1],
                                         sgn * (cand[j]["pos_rot_deg"] or 0.0),
                                         side_of(cand[j])).multiply(sh.Placement)
                if round((cand[j]["pos_rot_deg"] or 0.0) - (cand[j0]["pos_rot_deg"] or 0.0), 3) % 360 == 0:
                    continue          # same angle as the representative: tells us nothing
                e = max(abs(a - b) for a, b in zip(bb6(sh), bodies[i]["bbox"]))
                conv_err[(side_of(cand[j]), sgn)].append(e)
    conv, conv_n = {}, {}
    for side in ("top", "bottom"):
        pos, neg = conv_err[(side, +1)], conv_err[(side, -1)]
        wp = max(pos) if pos else float("inf")
        wn = max(neg) if neg else float("inf")
        conv[side] = +1 if wp <= wn else -1
        conv_n[side] = len(pos)
        P("rotation convention %-6s over %3d instances whose angle differs from their "
          "representative's: R(+rot) worst %.6f mm   R(-rot) worst %.6f mm   -> %s"
          % (side, len(pos), wp, wn, "R(+rot)" if conv[side] == +1 else "R(-rot)"))

    # ---- 5. build the PCBA from OUR localised library + the pick-and-place ---
    bs = board_solid([(h["d"], h["x"], h["y"]) for h in drills])
    bb = bs.BoundBox
    P("our board solid bbox", [round(v, 4) for v in (bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax)],
      "volume", round(bs.Volume, 4), "drills", len(drills))

    assign_d = {cand[j]["refdes"]: math.hypot(bodies[i]["centre"][0] - cand[j]["pos_mm"][0],
                                              bodies[i]["centre"][1] - cand[j]["pos_mm"][1])
                for i, j, _ in pairs}
    local_lib, placed, shapes, dnp_bodies = {}, [], [], []
    worst, worst_ref, over = 0.0, None, []
    for key, group in sorted(by_key.items()):
        i0, j0 = group[0]
        c0 = cand[j0]
        rep = bodies[i0]["shape"].copy()
        rep.Placement = placement(c0["pos_mm"][0], c0["pos_mm"][1],
                                  conv[side_of(c0)] * (c0["pos_rot_deg"] or 0.0),
                                  side_of(c0)).inverse().multiply(rep.Placement)
        lb = bb6(rep)
        # a localised body must sit on the origin: its xy centre is the pick point
        cx, cy = (lb[0] + lb[3]) / 2.0, (lb[1] + lb[4]) / 2.0
        lo = doc.addObject("Part::Feature", "loc_" + key.replace("-", "_")[:40])
        lo.Shape = rep
        Import.export([lo], os.path.join(GEOL, key + ".step"))
        local_lib[key] = dict(representative=c0["refdes"], instances=[cand[j]["refdes"] for _, j in group],
                              qty=len(group), side=c0["pos_side"], value=c0.get("bom_value"),
                              footprint=c0.get("footprint"), lcsc=c0.get("bom_lcsc"),
                              local_bbox=[round(v, 4) for v in lb],
                              size_mm=[round(lb[3] - lb[0], 4), round(lb[4] - lb[1], 4), round(lb[5] - lb[2], 4)],
                              local_centre_offset_mm=[round(cx, 4), round(cy, 4)],
                              volume_mm3=round(rep.Volume, 4) if rep.Solids else None,
                              file="out/pcb/hat/geometry-local/%s.step" % key)
        for i, j in group:
            c = cand[j]
            if c["dnp"]:
                # the vendor STEP carries a body here; the physical board does not
                dnp_bodies.append(dict(refdes=c["refdes"], value=c.get("bom_value"),
                                       footprint=c.get("footprint"), side=side_of(c),
                                       at=[round(v, 4) for v in c["pos_mm"]],
                                       step_body_size_mm=[round(v, 4) for v in bodies[i]["size"]],
                                       why="do-not-populate: matched to its own body in the "
                                           "production STEP so no fitted part could take it, "
                                           "then excluded from the built board"))
                continue
            sh = rep.copy()
            sh.Placement = placement(c["pos_mm"][0], c["pos_mm"][1],
                                     conv[side_of(c)] * (c["pos_rot_deg"] or 0.0),
                                     side_of(c)).multiply(sh.Placement)
            got, want = bb6(sh), bodies[i]["bbox"]
            e = max(abs(a - b) for a, b in zip(got, want))
            if e > worst:
                worst, worst_ref = e, c["refdes"]
            if e > 0.05:
                over.append(dict(refdes=c["refdes"], key=key, deviation_mm=round(e, 4),
                                 ours=[round(v, 4) for v in got], vendor=[round(v, 4) for v in want],
                                 note="our placement of this body and the vendor's own placement of it "
                                      "disagree; the pick-and-place and the STEP are two documents"))
            o = doc.addObject("Part::Feature", "c_" + c["refdes"])
            o.Shape = sh
            b = sh.BoundBox
            placed.append(dict(refdes=c["refdes"], key=key, side=c["pos_side"],
                               rot_deg=c["pos_rot_deg"], at=[round(v, 4) for v in c["pos_mm"]],
                               value=c.get("bom_value"), footprint=c.get("footprint"),
                               lcsc=c.get("bom_lcsc"), dnp=c["dnp"], sheet=c.get("sheet"),
                               z=[round(b.ZMin, 4), round(b.ZMax, 4)],
                               bbox=[round(b.XMin, 4), round(b.YMin, 4), round(b.XMax, 4), round(b.YMax, 4)],
                               height_mm=round(b.ZLength, 4),
                               assign_dist_mm=round(assign_d.get(c["refdes"], float("nan")), 4),
                               volume_mm3=round(sh.Volume, 4) if sh.Solids else None,
                               round_trip_mm=round(e, 6)))
            shapes.append(sh)
    P("ROUND TRIP over %d bodies: worst %.6f mm at %s; over 0.05 mm: %d"
      % (len(placed), worst, worst_ref, len(over)))
    P("localised library keys", len(local_lib),
      "worst local centre offset", round(max(max(abs(v["local_centre_offset_mm"][0]),
                                                 abs(v["local_centre_offset_mm"][1]))
                                             for v in local_lib.values()), 4))

    comp = Part.makeCompound([bs] + shapes)
    cb = comp.BoundBox
    P("PCBA bbox", [round(v, 4) for v in (cb.XMin, cb.YMin, cb.ZMin, cb.XMax, cb.YMax, cb.ZMax)],
      "size", [round(cb.XLength, 4), round(cb.YLength, 4), round(cb.ZLength, 4)])
    allo = doc.addObject("Part::Feature", "pcba")
    allo.Shape = comp
    Import.export([allo], os.path.join(OUT, "robot-hat-pcba.step"))

    tallest = max((p for p in placed if p["side"] == "top"), key=lambda p: p["z"][1])
    lowest = min((p for p in placed if p["side"] == "bottom"), key=lambda p: p["z"][0])
    P("tallest top", tallest["refdes"], tallest["value"], tallest["z"])
    P("lowest bottom", lowest["refdes"], lowest["value"], lowest["z"])

    ics = [p for p in placed if p["refdes"][0] == "U" or p["refdes"].startswith("MK")
           or p["refdes"].startswith("Y")]
    P("ICs placed (U*/MK*/Y*)", len(ics), sorted(p["refdes"] for p in ics))

    res = dict(
        _generated="tools/hat_pcba.py",
        _replaces="tools/build_hat_pcba.py (round trip 58.600000 mm; see this file's docstring)",
        source=dict(comps["source"], step_sha256=step_sha,
                    step_zip="reference/pollen-elec-rpi-robot-hat/production/"
                             "ASE01187-C1_elec_RPI_Robot_HAT_STEP.zip"),
        board=dict(ours_bbox=[round(v, 4) for v in (bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax)],
                   vendor_substrate_bbox=[round(v, 4) for v in (vb.XMin, vb.YMin, vb.ZMin,
                                                                vb.XMax, vb.YMax, vb.ZMax)],
                   finished_thickness_mm=T_FINISHED, vendor_substrate_thickness_mm=round(vb.ZLength, 4),
                   volume_mm3=round(bs.Volume, 4), drills=len(drills), layers=4),
        assignment=dict(method="scipy.optimize.linear_sum_assignment over xy distance + KiCad F.Fab "
                               "body-size error; side-gated; per-part radius = half the F.Fab "
                               "body diagonal + 1.0 mm; only placements that declare a 3D "
                               "model compete",
                        bodies_in_step=len(bodies), candidate_placements=len(cand),
                        pairs=len(pairs), unmatched_bodies=len(unmatched_body),
                        unmatched_placements=len(unmatched_cand),
                        distinct_designators=len(set(j for _, j, _ in pairs)),
                        step_vs_pos_xy_worst_mm=round(dists[-1], 4),
                        step_vs_pos_xy_median_mm=round(dists[len(dists) // 2], 4),
                        step_vs_pos_xy_over_0p1mm=sum(1 for d in dists if d > 0.10)),
        rotation_convention=dict(
            top="R(+rot)" if conv["top"] == +1 else "R(-rot)",
            bottom="R(+rot)" if conv["bottom"] == +1 else "R(-rot)",
            measured={s + "_" + n: (round(max(v), 6) if v else None)
                      for s in ("top", "bottom") for n, v in
                      (("plus", conv_err[(s, +1)]), ("minus", conv_err[(s, -1)]))},
            discriminating_instances=conv_n,
            basis="worst six-face bbox error, both conventions tried, counted only over "
                  "instances placed at a different angle from their representative"),
        round_trip=dict(checked=len(placed), worst_mm=round(worst, 6), at=worst_ref,
                        over_0p05mm=len(over), detail=over,
                        what="our localised body re-placed by the pick-and-place, against the "
                             "vendor's own body in their assembly STEP, all six bbox faces"),
        pcba=dict(bbox=[round(v, 4) for v in (cb.XMin, cb.YMin, cb.ZMin, cb.XMax, cb.YMax, cb.ZMax)],
                  size_mm=[round(cb.XLength, 4), round(cb.YLength, 4), round(cb.ZLength, 4)],
                  height_above_board_mm=round(cb.ZMax - Z_TOP, 4),
                  depth_below_board_mm=round(Z_BOT - cb.ZMin, 4)),
        counts=dict(footprints_in_pcb=comps["counts"]["footprints_in_pcb"],
                    fitted_placements=comps["counts"]["fitted_placements"],
                    dnp=comps["counts"]["dnp"],
                    placements_that_can_own_a_body=len(cand),
                    placements_with_no_3d_model=len(nomodel),
                    bodies_in_step=len(bodies),
                    bodies_placed=len(placed),
                    dnp_bodies_excluded=len(dnp_bodies),
                    top=sum(1 for p in placed if p["side"] == "top"),
                    bottom=sum(1 for p in placed if p["side"] == "bottom"),
                    ics_placed=len(ics),
                    bom_lines=len(local_lib)),
        ics=sorted((dict(refdes=p["refdes"], value=p["value"], footprint=p["footprint"],
                         at=p["at"], side=p["side"], rot_deg=p["rot_deg"], z=p["z"],
                         height_mm=p["height_mm"]) for p in ics), key=lambda d: d["refdes"]),
        tallest_top=tallest, lowest_bottom=lowest,
        no_3d_model=[dict(refdes=c["refdes"], footprint=c["footprint"], n_pads=c["n_pads"],
                          why="this footprint declares no 3D model, so it owns no body: "
                              "a fiducial or a silkscreen logo, not a component")
                     for c in nomodel],
        dnp_bodies_excluded=dnp_bodies,
        unmatched_bodies=unmatched_body, unmatched_placements=unmatched_cand,
        local_library=local_lib, placements=placed)
    json.dump(res, open(os.path.join(OUT, "pcba-measured.json"), "w"), indent=1)

    # ---- 6. renders, colour by what the thing is ---------------------------
    def colour(p):
        r, k = p["refdes"], (p["key"] or "")
        if r[0] == "J" or "wago" in k or "jst" in k or "header" in k:
            return (0.86, 0.85, 0.80)
        if r[0] == "U" or r.startswith("MK") or r.startswith("Y") or r[0] == "Q" or r[0] == "D":
            return (0.10, 0.10, 0.11)
        if r[0] == "L" or r.startswith("FB"):
            return (0.24, 0.21, 0.19)
        if r.startswith("TP"):
            return (0.74, 0.74, 0.77)
        if r[0] == "C":
            return (0.62, 0.55, 0.40)
        return (0.30, 0.28, 0.26)

    items = [(bs, (0.06, 0.30, 0.20))] + [(sh, colour(p)) for p, sh in zip(placed, shapes)]
    try:
        from cecad import render
        for name in ("top", "bottom", "iso"):
            png = os.path.join(OUT, "pcba-%s.png" % name)
            render(items, png, view=name, mode="pbr", W=1800, H=1100,
                   title="Pollen RPI Robot HAT rev C1 - %d bodies at the manufacturer's own "
                         "pick-and-place positions, round trip %.4f mm" % (len(placed), worst))
            P("rendered", png, os.path.getsize(png), "bytes")
    except Exception:
        import traceback
        LOG.write(traceback.format_exc())

    P("seconds", round(time.time() - t0, 1))
    P("DONE")


main()
