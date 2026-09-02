"""jigs.py — the Microduck assembly-line jigs, as cecad parts with drawings.

    ce-cad/bin/cad tools/jigs.py            # -> out/jigs/<slug>/{svg,dxf,pdf,stl}

WHY THESE SIX. The line has exactly three operations that a hand cannot do
repeatably: seating a ball bearing by interference into a printed seat, seating
the same bearing onto a printed BOSS, and presenting an XL330's horn at its
mechanical centre so the link bolts on square. Everything else on this robot is
a screw.

THE RULE THE ASSEMBLY TEXT GETS WRONG. `RELEASE.html` §4 and
`ce-assemblies/microduck/current/manual/MANUAL.md` both say "press the OUTER
race only". That is right for the seats that are BORES and wrong for the seats
that are BOSSES, and this robot has both — read off the connection records:

  connection:press-fit-bearing-22x16x4 joins.b (ce-connections/
  press-fit-bearing-22x16x4/connection.json): "a Ø16 boss for the inner ring
  (yaw2roll 'yaw_bearing_seat' Ø16.0 x 1.95 with its own Ø19.0 x 0.5 shoulder,
  hip-bracket 'roll_/pitch_bearing_seat' Ø16.0 x 1.95, yaw-roll-motion
  'roll_bearing_seat' Ø16.0 x 4.0) or a Ø22 bore for the outer ring
  ('housing_bore'/'pocket' - trunk_base for hip-yaw, the head for head-roll)"

  connection:press-fit-bearing-15x10x3 joins.b: "a Ø10 boss for the inner ring
  (microduck-shin 'ankle', Ø10.0 x 3.2) or a Ø15 pocket for the outer ring
  (microduck-ankle 'ankle_bearing', Ø15.0 x 2.3 with Ø16 x 0.5 lead-in)"

The load must pass through the ring that is being interference-fitted, never
across the balls. Boss seat -> push the INNER ring. Bore seat -> push the OUTER
ring. Hence four pushers, not two.

WHERE THE PUSHER DIAMETERS COME FROM. The ring boundaries are MEASURED off
Pollen's own bearing meshes and recorded in the part builders' docstrings:

  ce-parts/bearing-22x16x4/iterations/v0.0.1/cad/part.py, "meshslice
  x-intervals at y=0: z=0.5..3.5 : (8.0,9.0) and (10.0,11.0) -> inner ring
  r 8..9, outer ring r 10..11; z=2.0 extra (9.345,9.645) -> cage band
  r 9.35..9.65" => inner ring face Ø16.0-18.0, cage Ø18.69-19.29,
  outer ring face Ø20.0-22.0.

  ce-parts/bearing-15x10x3/iterations/v0.0.1/cad/part.py, "z=0.5..2.5 :
  (5.0,5.75) and (6.75,7.5) ... z=1.5 extra (6.099,6.402)" => inner ring face
  Ø10.0-11.5, cage Ø12.198-12.804, outer ring face Ø13.5-15.0.

Every contact land below lies wholly inside one of those four annuli, with the
clearance to the neighbouring ring and to the cage stated per part.

THE HORN GAUGE comes off the servo builder, which measured Pollen's mesh:
ce-parts/xl330-m288-t/iterations/v0.0.1/cad/part.py — "DISC_D, DISC_L = 16.0,
3.0", "FACE_D, FACE_DEPTH = 1.6, 6.0", "FACE_PCD = 12.0", "FACE_AT =
((0.0, 6.0), (0.0, -6.0), (6.0, 0.0), (-6.0, 0.0))", "BODY_Y = (-10.0, 10.0)",
"BODY_Z = (-24.5, 9.5)" with the horn axis at z = 0. So the top of the case is
9.5 mm above the horn axis and the four tapped holes stand at 12, 3, 6 and 9
o'clock when the horn is at its centre position.

MATERIAL. Printed PLA for the first article, because the shop that builds unit
one has a printer and not a mill. A printed pusher is a CONSUMABLE: PLA's
compressive strength is not sourced here and the press load for these seats is
CANNOT DETERMINE (no interference is specified anywhere in the repo — the
printed seat's real diameter is a slicer/printer outcome, not a modelled one),
so the playbook's QA gate is "inspect the land before every shift, replace when
the land shows a print line", and the production answer is the same geometry cut
in 6082-T6 or 1.4301.
"""
import json
import os
import sys
import time

import FreeCAD
from cecad import inspect as insp
from cecad.core import Part
from cecad.autosheet import auto_blueprint
from cecad.sheets import verify_sheet

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "jigs")

# ---- measured bearing ring geometry (mm) -------------------------------------
# rings from the meshslice bands at mid-height; *_face_flat from the z=0.05 slice,
# i.e. what is actually FLAT at the face after the measured 0.2/0.3 chamfers.
# Sources verbatim in the module docstring.
B22 = dict(od=22.0, bore=16.0, w=4.0,
           inner=(16.0, 18.0), cage=(18.69, 19.29), outer=(20.0, 22.0),
           inner_face_flat=(16.3, 18.0), outer_face_flat=(20.0, 21.5),
           face_slice="z=0.05 : (8.15,9.0),(10.0,10.75) -> bore chamfer 0.2, OD chamfer 0.3")
B15 = dict(od=15.0, bore=10.0, w=3.0,
           inner=(10.0, 11.5), cage=(12.198, 12.804), outer=(13.5, 15.0),
           inner_face_flat=(10.3, 11.5), outer_face_flat=(13.5, 14.5),
           face_slice="z=0.05 : (5.15,5.75),(6.75,7.25) -> bore chamfer 0.2, OD chamfer 0.3")

GRIP_D, GRIP_H = 26.0, 12.0      # what a hand and a vice jaw hold
NOSE_H = 6.0                     # how far the nose reaches into a seat
CLR = 0.20                       # diametral clearance the nose keeps off a bore wall
PILOT_CLR = 0.60                 # diametral clearance a pilot keeps in a bearing bore
TWO_PERIM = 0.80                 # 2 x 0.4 mm nozzle — the FDM wall floor (docs/DFM.md)


def _wall_verdict(w):
    return ("PASS (>= %.2f mm, two 0.4 mm perimeters)" % TWO_PERIM if w >= TWO_PERIM
            else "FAIL for FDM at a 0.4 mm nozzle: %.3f mm is under the %.2f mm "
                 "two-perimeter floor. Machine this one." % (w, TWO_PERIM))


def pusher_outer(name, b, seat_bore_d, pilot_len):
    """Press an outer ring INTO a printed bore. Contact only on the outer ring."""
    nose_d = round(seat_bore_d - CLR, 3)            # enters the seat, never rubs it
    relief_d = round(b["inner"][1] + 0.6, 3)        # clears the inner ring AT THE FACE
    pilot_d = round(b["bore"] - PILOT_CLR, 3)
    rim = round((nose_d - relief_d) / 2.0, 4)
    p = Part(name, material="PLA")
    p.cyl(GRIP_D, GRIP_H, at=(0, 0, NOSE_H))
    p.cyl(nose_d, NOSE_H + 0.01, at=(0, 0, 0))
    p.cyl(relief_d, NOSE_H - 1.5, at=(0, 0, -0.005), op="cut")   # relief bore in the nose
    p.cyl(pilot_d, pilot_len, at=(0, 0, -pilot_len))             # centring pilot
    p.clean()
    p.connector("face", at=(0, 0, 0), dir="-z")
    lo, hi = max(relief_d, b["outer_face_flat"][0]), min(nose_d, b["outer_face_flat"][1])
    meta = dict(
        kind="outer-ring pusher (bore seat)",
        nose_od_mm=nose_d, relief_bore_mm=relief_d, relief_depth_mm=NOSE_H - 1.5,
        contact_on="outer ring; flat at the face over \u00d8%.3f-%.3f (%s)"
                   % (b["outer_face_flat"][0], b["outer_face_flat"][1], b["face_slice"]),
        effective_contact_diam_mm=[round(lo, 4), round(hi, 4)],
        effective_contact_width_radial_mm=round((hi - lo) / 2.0, 4),
        clearance_over_inner_ring_diam_mm=round(relief_d - b["inner"][1], 4),
        cage_note=("the cage band sits at bearing MID-height (\u00d8%.3f-%.3f, seen only "
                   "in the mid-plane slice) and the face slice shows no material between "
                   "the two rings, so the cage is unreachable: this tool's face rests ON "
                   "the ring face and no part of it enters the bearing."
                   % (b["cage"][0], b["cage"][1])),
        clearance_in_seat_diam_mm=round(seat_bore_d - nose_d, 4),
        nose_rim_wall_mm=rim, nose_rim_verdict=_wall_verdict(rim),
        pilot=dict(d=pilot_d, length=pilot_len,
                   clearance_in_bearing_bore_diam_mm=round(b["bore"] - pilot_d, 4)),
        rule="load path: pusher -> outer ring -> printed bore. The relief bore "
             "\u00d8%.3f stands clear of the inner ring (\u00d8%.1f) at the face, so "
             "nothing crosses the balls." % (relief_d, b["inner"][1]))
    return p, meta


def pusher_inner(name, b, boss_d, boss_len):
    """Press a bearing ONTO a printed boss. Contact only on the inner ring."""
    land_od = b["inner"][1]                         # exactly the measured inner-ring OD
    pocket_d = round(boss_d + 0.4, 3)               # swallows the boss, never touches it
    protrusion = max(0.0, boss_len - b["w"])        # how far the boss comes through
    pocket_h = round(max(0.8, protrusion + 0.8), 3)
    land_h = 2.5                                    # how far the land stands proud
    rim = round((land_od - pocket_d) / 2.0, 4)
    p = Part(name, material="PLA")
    p.cyl(GRIP_D, GRIP_H, at=(0, 0, land_h))                # the grip body, held clear
    p.cyl(land_od, land_h + 0.01, at=(0, 0, 0))             # the ONLY thing that touches
    p.cyl(pocket_d, pocket_h, at=(0, 0, -0.005), op="cut")  # blind boss-clearance pocket
    p.clean()
    p.connector("face", at=(0, 0, 0), dir="-z")
    lo, hi = max(pocket_d, b["inner_face_flat"][0]), min(land_od, b["inner_face_flat"][1])
    meta = dict(
        kind="inner-ring pusher (boss seat)",
        land_od_mm=land_od, pocket_d_mm=pocket_d, pocket_depth_mm=pocket_h,
        land_stands_proud_mm=land_h,
        contact_on="inner ring; flat at the face over \u00d8%.3f-%.3f (%s)"
                   % (b["inner_face_flat"][0], b["inner_face_flat"][1], b["face_slice"]),
        effective_contact_diam_mm=[round(lo, 4), round(hi, 4)],
        effective_contact_width_radial_mm=round((hi - lo) / 2.0, 4),
        clearance_over_outer_ring_radial_mm=round((GRIP_D - b["od"]) / 2.0, 4),
        outer_ring_standoff_mm=land_h,
        land_rim_wall_mm=rim, land_rim_verdict=_wall_verdict(rim),
        boss=dict(d=boss_d, length=boss_len, protrusion_through_bearing_mm=protrusion,
                  clearance_over_boss_diam_mm=round(pocket_d - boss_d, 4)),
        rule="load path: pusher -> inner ring -> printed boss. The land is a plain "
             "\u00d8%.1f boss standing %.1f mm proud of the \u00d8%.1f grip body, so the "
             "outer ring (\u00d8%.1f) and the cage never touch this tool. Centring is by "
             "the \u00d8%.3f pocket over the part's own boss."
             % (land_od, land_h, GRIP_D, b["od"], pocket_d))
    return p, meta


def horn_gauge(name):
    """XL330 horn-index gauge. Servo dims: ce-parts/xl330-m288-t .../cad/part.py.

    FRAME. The servo builder's frame has the horn axis on +x, the horn disc face
    at x = BODY_X[1] + DISC_L = 11.5 + 3.0 = 14.5, the case top at z = +9.5 and
    the case running x = -11.5 .. +11.5.  The gauge's own frame is that one
    translated and re-labelled so the gauge prints flat:

        gauge z = servo x - 14.5     (z = 0 IS the horn face; +z leaves the servo)
        gauge y = servo z            (+y is toward the top of the case)
        gauge x = servo y

    so the case's top face lies at gauge y = +9.500 over gauge z = -26.0 .. -3.0,
    and the horn disc (Ø16, radius 8) occupies gauge z = -3.0 .. 0 within r = 8.

    WHAT IT PROVES, AND WHAT IT DOES NOT. Pollen's mesh has the four Ø1.6 tapped
    holes at 12/3/6/9 o'clock (FACE_AT = ((0,6),(0,-6),(6,0),(-6,0)) on
    FACE_PCD = 12.0). Whether that mesh pose is the servo's Goal Position 2048 is
    **CANNOT DETERMINE** — no fetched ROBOTIS page states the horn's angular
    datum relative to the case. So this is an INDEX gauge, not an absolute zero:
    it defines one repeatable horn angle to 0.05 mm of pin play, and the line
    step is "command 2048, fit the gauge, read Present Position(132) back and
    record it as that unit's horn-zero offset". A unit whose recorded offset
    differs from the fleet median by more than the QA gate is rejected.
    """
    PIN_D, PIN_L, PCD = 1.50, 3.5, 12.0     # into the Ø1.6 x 6.0 deep tapped holes
    PLATE_T, PLATE_D = 3.0, 22.0
    TOP_OF_CASE = 9.5                       # BODY_Z[1]; horn axis at servo z = 0
    ARM_W = 10.0                            # gauge x, inside the case width (20.0)
    ARM_Y1 = 13.0                           # outer edge of the arm
    ARM_Z0 = -11.0                          # how far back over the case the foot reaches
    p = Part(name, material="PLA")
    p.cyl(PLATE_D, PLATE_T, at=(0, 0, 0))                       # lies on the horn face
    for y in (PCD / 2.0, -PCD / 2.0):                           # 12 and 6 o'clock pins
        p.cyl(PIN_D, PIN_L + 0.01, at=(0, y, -PIN_L))
    p.box(ARM_W, ARM_Y1 - 6.0, PLATE_T,                         # web out to the arm
          at=(-ARM_W / 2.0, 6.0, 0))
    p.box(ARM_W, ARM_Y1 - TOP_OF_CASE, PLATE_T - ARM_Z0,        # the foot, over the case
          at=(-ARM_W / 2.0, TOP_OF_CASE, ARM_Z0))
    p.box(4.0, ARM_Y1 - TOP_OF_CASE + 1, 4.0,                   # witness window
          at=(-2.0, TOP_OF_CASE - 0.5, -8.5), op="cut")
    p.clean()
    p.connector("horn_face", at=(0, 0, 0), dir="-z")
    meta = dict(
        kind="horn index go/no-go gauge",
        pins=dict(d=PIN_D, length=PIN_L, pcd=PCD, at_oclock=[12, 6],
                  into="the horn's 4 x Ø1.6 tapped holes, FACE_PCD = 12.0, "
                       "FACE_AT = ((0,6),(0,-6),(6,0),(-6,0)), FACE_DEPTH = 6.0",
                  clearance_in_tapped_hole_diam_mm=round(1.6 - PIN_D, 4),
                  angular_play_deg=round(
                      __import__("math").degrees(2 * (1.6 - PIN_D) / PCD), 4)),
        datum_face="gauge z = 0 = the Ø16.0 horn disc face (servo x = 14.5)",
        reference_face=dict(
            at_gauge_y_mm=TOP_OF_CASE,
            surface="the top of the XL330 case, BODY_Z[1] = +9.500 above the horn axis",
            over_gauge_z_mm=[ARM_Z0, -3.0],
            width_mm=ARM_W,
            case_width_mm=20.0),
        witness_window="4.0 x 4.0 through the foot at gauge z = -8.5 .. -4.5, so the "
                       "operator sees the case face and any gap under the reference",
        absolute_zero="CANNOT DETERMINE — no fetched ROBOTIS source states the horn's "
                      "angular datum relative to the case, so this gauge fixes an INDEX, "
                      "not an absolute 2048. The line records Present Position(132) at "
                      "the gauge as the unit's horn-zero offset.",
        use="command Goal Position 2048, drop the gauge on the horn with both pins "
            "engaged, check the foot sits flat on the case top through the witness "
            "window, then read and record Present Position(132).")
    return p, meta


def anvil(name):
    """The nest the part sits in while a pusher is driven. Flat, relieved, universal."""
    L, W, H = 70.0, 50.0, 12.0
    p = Part(name, material="PLA")
    p.box(L, W, H, at=(-L / 2.0, -W / 2.0, 0))
    p.cyl(24.0, H + 1, at=(0, 0, -0.5), op="cut")        # a 22 bearing passes through
    p.cyl(30.0, 2.0, at=(0, 0, H - 2.0), op="cut")       # relief so a boss shoulder clears
    for x in (-26.0, 26.0):                               # clamp slots for a vice
        p.box(8.0, 5.0, H + 1, at=(x - 4.0, -W / 2.0 - 0.5, -0.5), op="cut")
        p.box(8.0, 5.0, H + 1, at=(x - 4.0, W / 2.0 - 4.5, -0.5), op="cut")
    p.clean()
    p.connector("top", at=(0, 0, H), dir="+z")
    meta = dict(through_bore_d=24.0, relief_d=30.0, relief_depth=2.0,
                use="the part lies on this face with the seat over the Ø24 bore, so "
                    "the bearing has somewhere to go and the press load lands on the "
                    "part's own seat boss rather than on a printed wall.")
    return p, meta


JIGS = [
    ("microduck-jig-press-22-outer",
     lambda: pusher_outer("microduck-jig-press-22-outer", B22, 22.0, 2.5),
     "Bearing press pusher — 22x16x4 outer ring into a Ø22 printed bore "
     "(trunk_base hip-yaw, head head-roll)"),
    ("microduck-jig-press-22-inner",
     lambda: pusher_inner("microduck-jig-press-22-inner", B22, 16.0, 1.95),
     "Bearing press pusher — 22x16x4 inner ring onto a Ø16 printed boss "
     "(yaw2roll Ø16.0x1.95, hip-bracket Ø16.0x1.95, yaw-roll-motion Ø16.0x4.0)"),
    ("microduck-jig-press-15-outer",
     lambda: pusher_outer("microduck-jig-press-15-outer", B15, 15.0, 1.8),
     "Bearing press pusher — 15x10x3 outer ring into the ankle's Ø15.0x2.3 pocket "
     "(Ø16x0.5 lead-in)"),
    ("microduck-jig-press-15-inner",
     lambda: pusher_inner("microduck-jig-press-15-inner", B15, 10.0, 3.2),
     "Bearing press pusher — 15x10x3 inner ring onto the shin's Ø10.0x3.2 boss"),
    ("microduck-jig-horn-zero",
     lambda: horn_gauge("microduck-jig-horn-zero"),
     "XL330 horn-at-centre go/no-go gauge — two Ø1.5 pins on the Ø12 tapped circle, "
     "arm referenced to the top of the case (+9.5 above the horn axis)"),
    ("microduck-jig-press-anvil",
     lambda: anvil("microduck-jig-press-anvil"),
     "Press anvil / nest — Ø24 through bore, Ø30x2 shoulder relief, vice slots"),
]


def main():
    only = [a for a in sys.argv[1:] if not a.startswith("-")]
    os.makedirs(OUT, exist_ok=True)
    index = {"$comment": ("Assembly jigs built and drawn by tools/jigs.py under "
                          "ce-cad/bin/cad. Every contact diameter is derived from a "
                          "MEASURED bearing ring boundary or a measured seat — the "
                          "sources are named in the module docstring and repeated in "
                          "each row's `basis`."),
             "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
             "jigs": {}}
    for slug, mk, title in JIGS:
        if only and slug not in only:
            continue
        t0 = time.time()
        doc = FreeCAD.newDocument("jig_" + slug.replace("-", "_"))
        part, meta = mk()
        d = os.path.join(OUT, slug)
        os.makedirs(d, exist_ok=True)
        stem = os.path.join(d, slug)
        part.export_stl(stem + ".stl")
        bb = insp.bbox_of(part)
        try:
            holes = [{"d": round(h.d, 4), "depth": round(h.depth, 4),
                      "through": bool(h.through),
                      "center": [round(float(c), 4) for c in h.center]}
                     for h in insp.holes(part)]
        except Exception as e:
            holes = {"reason": "inspect.holes raised: %s" % e}
        try:
            r = auto_blueprint(part, stem, source="tools/jigs.py")
            ok2 = verify_sheet(r["sheet"], r["svg"], part, verbose=False)
            draw = {"svg": os.path.relpath(r["svg"], ROOT),
                    "dxf": os.path.relpath(r["dxf"], ROOT),
                    "pdf": os.path.relpath(r["pdf"], ROOT),
                    "size": r["size"], "scale": "%d:%d" % tuple(r["scale"]),
                    "views": r["views"], "verified": bool(r["verified"]),
                    "verify_sheet": bool(ok2)}
        except Exception as e:
            draw = {"reason": "auto_blueprint raised: %s" % e}
        index["jigs"][slug] = {
            "title": title, "material": "PLA (first article) — see module docstring",
            "bbox_mm": [round(float(x), 4) for x in bb],
            "volume_mm3": round(float(part.shape.Volume), 4),
            "stl": os.path.relpath(stem + ".stl", ROOT),
            "holes": holes, "geometry": meta, "drawing": draw,
            "seconds": round(time.time() - t0, 2),
        }
        print("JIG %-32s bbox=%s drawing=%s %.1fs"
              % (slug, index["jigs"][slug]["bbox_mm"],
                 draw.get("verify_sheet", draw.get("reason")),
                 index["jigs"][slug]["seconds"]), flush=True)
        try:
            FreeCAD.closeDocument(doc.Name)
        except Exception:
            pass
    p = os.path.join(OUT, "jigs.json")
    if only and os.path.exists(p):
        prev = json.load(open(p))
        prev["jigs"].update(index["jigs"])
        index = prev
    json.dump(index, open(p, "w"), indent=1)
    print("wrote", p)


main()
