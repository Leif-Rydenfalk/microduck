"""tools/build_hat_pcba.py — run under ce-cad/bin/cad.

Builds OUR CAD of the POPULATED Pollen RPI Robot HAT, revision C1, and measures it
against the manufacturer's own 3D assembly.

WHAT IS OURS AND WHAT IS THEIRS
  ours   : the bare board — a parametric solid built from the official Edge.Cuts
           outline (four R3.500 arcs centred on (0,+0.900) (58,+0.900) (0,-23.000)
           (58,-23.000)) and all 63 drilled holes read out of elec_RPI_Robot_HAT.kicad_pcb,
           at the FINISHED thickness 1.000 mm (z -0.080 .. +0.920, so the 0.840 mm
           substrate keeps the STEP's own z centre and the outer copper+mask 0.080 mm
           per face is added).
  theirs : each component body, the vendor's own solid, sliced out of the official
           production STEP by tools/hat_step_harvest.py and re-placed here at the
           position, rotation and side the manufacturer's pick-and-place gives.

OUTPUTS  out/pcb/hat/robot-hat-pcba.step        our populated board, one STEP
         out/pcb/hat/pcba-*.png                 renders (read them back)
         out/pcb/hat/pcba-measured.json         counts and measurements

Run: ce-cad/bin/cad tools/build_hat_pcba.py    (buffered stdout — read the log file)
"""
import json, math, os, time
import FreeCAD as App
import Part
import Import

REPO = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck"
OUT = os.path.join(REPO, "out", "pcb", "hat")
GEO = os.path.join(OUT, "geometry")

# ---- the C1 board, measured (mm) -------------------------------------------
T_FINISHED = 1.000        # kicad_pcb (general (thickness 1)); stackup sums to 1.000
Z_BOT, Z_TOP = -0.080, 0.920      # substrate 0.000..0.840 + 0.080 copper+mask per face
CORNER_R = 3.500
CORNERS = [(0.0, 0.9), (58.0, 0.9), (0.0, -23.0), (58.0, -23.0)]
X_MIN, X_MAX = -3.500, 61.500
Y_MIN, Y_MAX = -26.500, 4.400


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
    wire = Part.makePolygon(outline())
    face = Part.Face(wire)
    solid = face.extrude(App.Vector(0, 0, T_FINISHED))
    for d, x, y in drills:
        cyl = Part.makeCylinder(d / 2.0, T_FINISHED + 2.0, App.Vector(x, y, Z_BOT - 1.0), App.Vector(0, 0, 1))
        solid = solid.cut(cyl)
    return solid


def main():
    t0 = time.time()
    comps = json.load(open(os.path.join(OUT, "components.json")))
    geoidx = json.load(open(os.path.join(OUT, "geometry_index.json")))["parts"]
    drills = json.load(open(os.path.join(OUT, "drills.json")))["holes"]

    doc = App.newDocument("pcba")
    bs = board_solid([(h["d"], h["x"], h["y"]) for h in drills])
    bb = bs.BoundBox
    print("board solid bbox", [round(v, 4) for v in (bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax)],
          "volume", round(bs.Volume, 3), flush=True)
    bo = doc.addObject("Part::Feature", "board")
    bo.Shape = bs

    # index the exported geometry by the designators it stands for
    by_ref = {}
    for key, v in geoidx.items():
        if not v.get("exported"):
            continue
        for r in v.get("instances", []):
            by_ref[r] = key

    placed, missing, shapes = [], [], []
    cache = {}
    for c in comps["components"]:
        if not c["fitted"] or c["dnp"]:
            continue
        key = by_ref.get(c["refdes"])
        if key is None:
            missing.append((c["refdes"], c.get("bom_value"), "no geometry file"))
            continue
        path = os.path.join(GEO, key + ".step")
        if key not in cache:
            cache[key] = Part.Shape()
            cache[key].read(path)
        sh = cache[key].copy()
        rot = c["pos_rot_deg"] or 0.0
        px, py = c["pos_mm"]
        zref = 0.84 if c["pos_side"] == "top" else 0.0
        # ONE placement: rotate about the origin by the pick-and-place angle, then
        # translate to the pick-and-place point and up to the board face. The z shift
        # commutes with a z rotation, so T(p)R T(z) == T(p+z)R and this is exact.
        # (Do NOT mix transformShape() (geometry) with Shape.rotate() (placement) —
        # the second translate then lands in the rotated frame and parts fly off the
        # board by up to 47 mm. Measured; see out/pcb/hat/pcba-top-BROKEN.png.)
        sh.Placement = App.Placement(App.Vector(px, py, zref),
                                     App.Rotation(App.Vector(0, 0, 1), rot))
        o = doc.addObject("Part::Feature", "c_" + c["refdes"])
        o.Shape = sh
        b = sh.BoundBox
        placed.append(dict(refdes=c["refdes"], key=key, side=c["pos_side"], rot=rot,
                           at=[px, py], z=[round(b.ZMin, 4), round(b.ZMax, 4)],
                           bbox=[round(b.XMin, 4), round(b.YMin, 4), round(b.XMax, 4), round(b.YMax, 4)],
                           volume=round(sh.Volume, 4) if sh.Solids else None))
        shapes.append(sh)
    print("placed", len(placed), "missing", missing, flush=True)

    # ---- ROUND TRIP: every placed body must land back where the manufacturer's
    # own STEP has it, to the micron. This is the check that catches a wrong
    # transform; a picture would not.
    ref = {o["refdes"]: o for o in json.load(open(os.path.join(OUT, "step_components.json")))["objects"]
           if o.get("refdes")}
    worst, worst_ref = 0.0, None
    checked = 0
    for p in placed:
        r = ref.get(p["refdes"])
        if not r or r.get("match_dist_mm") is None or r["match_dist_mm"] > 0.6:
            continue
        d = max(abs(p["bbox"][0] - r["bbox_min"][0]), abs(p["bbox"][1] - r["bbox_min"][1]),
                abs(p["bbox"][2] - r["bbox_max"][0]), abs(p["bbox"][3] - r["bbox_max"][1]),
                abs(p["z"][0] - r["bbox_min"][2]), abs(p["z"][1] - r["bbox_max"][2]))
        checked += 1
        if d > worst:
            worst, worst_ref = d, p["refdes"]
    print("round trip checked", checked, "worst deviation mm", round(worst, 6), "at", worst_ref, flush=True)

    comp = Part.makeCompound([bs] + shapes)
    cb = comp.BoundBox
    print("PCBA bbox", [round(v, 4) for v in (cb.XMin, cb.YMin, cb.ZMin, cb.XMax, cb.YMax, cb.ZMax)],
          "size", [round(cb.XLength, 4), round(cb.YLength, 4), round(cb.ZLength, 4)], flush=True)
    allo = doc.addObject("Part::Feature", "pcba")
    allo.Shape = comp
    Import.export([allo], os.path.join(OUT, "robot-hat-pcba.step"))

    tallest_top = max((p for p in placed if p["side"] == "top"), key=lambda p: p["z"][1])
    lowest_bot = min((p for p in placed if p["side"] == "bottom"), key=lambda p: p["z"][0])
    print("tallest top", tallest_top["refdes"], tallest_top["z"], flush=True)
    print("lowest bottom", lowest_bot["refdes"], lowest_bot["z"], flush=True)

    res_early = dict(_generated="tools/build_hat_pcba.py",
                     board=dict(bbox=[round(v, 4) for v in (bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax)],
                                thickness_mm=T_FINISHED, volume_mm3=round(bs.Volume, 4),
                                holes=len(drills)),
                     round_trip=dict(checked=checked, worst_deviation_mm=round(worst, 6), at=worst_ref),
                     pcba=dict(bbox=[round(v, 4) for v in (cb.XMin, cb.YMin, cb.ZMin, cb.XMax, cb.YMax, cb.ZMax)],
                               size_mm=[round(cb.XLength, 4), round(cb.YLength, 4), round(cb.ZLength, 4)],
                               height_above_board_mm=round(cb.ZMax - Z_TOP, 4),
                               depth_below_board_mm=round(Z_BOT - cb.ZMin, 4)),
                     counts=dict(placed=len(placed), missing=len(missing),
                                 top=sum(1 for p in placed if p["side"] == "top"),
                                 bottom=sum(1 for p in placed if p["side"] == "bottom")),
                     tallest_top=tallest_top, lowest_bottom=lowest_bot,
                     missing=missing, placements=placed)
    json.dump(res_early, open(os.path.join(OUT, "pcba-measured.json"), "w"), indent=1)
    open(os.path.join(OUT, "pcba-build.log"), "w").write(json.dumps(res_early["counts"]) +
        "\nround trip worst %.6f mm at %s over %d parts\n" % (worst, worst_ref, checked) +
        "pcba bbox %s\n" % res_early["pcba"]["bbox"])

    # ---- renders. Colour by what the thing is, so a picture is readable.
    def colour(key, refdes):
        k = key or ""
        if refdes.startswith("J") or "wago" in k or "jst" in k or "header" in k:
            return (0.88, 0.87, 0.84)
        if refdes.startswith("U") or refdes.startswith("Q") or refdes.startswith("D") \
           or refdes.startswith("MK") or refdes.startswith("Y"):
            return (0.10, 0.10, 0.11)
        if refdes.startswith("C") and "elec" in k:
            return (0.15, 0.20, 0.42)
        if refdes.startswith("L"):
            return (0.22, 0.20, 0.19)
        if refdes.startswith("TP"):
            return (0.72, 0.72, 0.75)
        return (0.72, 0.66, 0.55)

    items = [(bs, (0.09, 0.28, 0.19))]
    for p, sh in zip(placed, shapes):
        items.append((sh, colour(p["key"], p["refdes"])))
    try:
        from cecad import render
        for name, view in (("top", "top"), ("iso", "iso"), ("bottom", "bottom")):
            out_png = os.path.join(OUT, "pcba-%s.png" % name)
            render(items, out_png, view=view, mode="pbr", W=1800, H=1100,
                   title="Pollen RPI Robot HAT rev C1 — %d components, positions from the "
                         "manufacturer's pick-and-place" % len(placed))
            print("rendered", out_png, flush=True)
    except Exception as e:
        import traceback; traceback.print_exc()
        print("render failed:", e, flush=True)

    print("seconds", round(time.time() - t0, 1), flush=True)
    print("DONE", flush=True)


main()
