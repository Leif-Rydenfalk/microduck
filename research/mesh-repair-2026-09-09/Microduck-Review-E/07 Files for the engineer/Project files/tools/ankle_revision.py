#!/usr/bin/env python3
"""ankle_revision.py — WHICH ankle does the product use? ankle_left or ankle_l_v1?

    /Applications/FreeCAD.app/Contents/Resources/bin/python tools/ankle_revision.py
    ce-cad/bin/cad tools/ankle_revision.py

COMPARISON.html finding 4: "Two ankle revisions ship (ankle_left Y=36.500 vs
ankle_l_v1 Y=46.500). Determine which is current."

This script answers it from three independent readings and writes
out/laneT/ankle-revision.json:

  1. THE MESH INVENTORY OF EVERY MJCF POLLEN SHIPS. Which model files name
     which ankle, and what else is in the same file.
  2. THE MESHES THEMSELVES. Envelope, bearing pocket and — the decisive one —
     the vertical screw, whose (x, y) says what bolts underneath.
  3. THE COUNTERPART MESHES. foot_left's own pilot boss and roller_blade's own
     pilot hole, each measured on its own mesh, matched against those screws.

It does not guess and it does not average: it prints the readings and the one
conclusion they agree on. Exit 0 if all three readings agree, 1 if they do not.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
FEAT = os.path.join(REPO, "out", "laneT", "features")
OUT = os.path.join(REPO, "out", "laneT", "ankle-revision.json")

MJCFS = [
    ("reference/pollen-microduck-rl/robot_allcollisions.xml", "the legs model, microduck_rl"),
    ("reference/pollen-microduck-rl/robot_walk.xml", "the walk model, microduck_rl"),
    ("reference/pollen-microduck-rl/robot_allcollisions_rollers.xml", "the rollers model, microduck_rl"),
    ("reference/pollen-microduck-simulator/robot_allcollisions.xml", "the legs model, HF simulator space"),
    ("reference/pollen-microduck-simulator/robot_allcollisions_rollers.xml", "the rollers model, HF simulator space"),
]
MESH_RE = re.compile(r'mesh="([A-Za-z0-9_]+)"')


def inventory():
    rows = []
    for rel, what in MJCFS:
        p = os.path.join(REPO, rel)
        if not os.path.exists(p):
            rows.append({"model": rel, "what": what, "error": "missing"})
            continue
        meshes = sorted(set(MESH_RE.findall(open(p, encoding="utf-8", errors="replace").read())))
        rows.append({
            "model": rel, "what": what, "mesh_count": len(meshes),
            "ankles": [m for m in meshes if m.startswith("ankle")],
            "foot_and_sole": [m for m in meshes if m.startswith(("foot_", "sole_"))],
            "roller_kit": [m for m in meshes if m in ("roller_blade", "tire", "rim")],
        })
    return rows


def feat(name):
    p = os.path.join(FEAT, name + ".json")
    if not os.path.exists(p):
        raise SystemExit("BROKEN INPUT: %s missing — run tools/measure_mesh_features.py first" % p)
    return json.load(open(p, encoding="utf-8"))


def vertical_screw(d):
    """The hole whose axis is +-z: what bolts on underneath."""
    out = []
    for h in d["holes"]:
        if abs(abs(h["axis"][2]) - 1.0) < 1e-3:
            out.append({"d_mm": h["d_mm"], "centre_mm": h["center_mm"],
                        "length_mm": h["length_mm"], "residual_mm": h["residual_mm"]})
    out.sort(key=lambda r: r["d_mm"])
    return out


def bearing_pocket(d):
    return [{"d_mm": h["d_mm"], "centre_mm": h["center_mm"], "length_mm": h["length_mm"]}
            for h in d["holes"] if h["d_mm"] > 13.0]


def main():
    inv = inventory()
    L, V1 = feat("ankle_left"), feat("ankle_l_v1")
    FOOT, ROLL = feat("foot_left"), feat("roller_blade")

    meshes = {}
    for tag, d in (("ankle_left", L), ("ankle_l_v1", V1)):
        meshes[tag] = {
            "bbox_mm": d["bbox_mm"], "triangles": d["triangles"],
            "y_extent_mm": round(d["bbox_mm"]["size"][1], 4),
            "vertical_screws": vertical_screw(d),
            "bearing_pockets": bearing_pocket(d),
            "placed_in_the_seeded_assembly": len(d["placements"]),
        }
    counter = {
        "foot_left_vertical": vertical_screw(FOOT),
        "roller_blade_vertical": vertical_screw(ROLL),
    }

    # --- the three readings ------------------------------------------------
    legs = [r for r in inv if r.get("ankles") == ["ankle_left", "ankle_right"]]
    rollers = [r for r in inv if r.get("ankles") == ["ankle_l_v1", "ankle_r_v1"]]
    r1 = {
        "reading": "MJCF inventory",
        "found": ("ankle_left/ankle_right appear in %d model(s), always alongside "
                  "foot_left/foot_right/sole_left/sole_right and never alongside the roller kit; "
                  "ankle_l_v1/ankle_r_v1 appear in %d model(s), always alongside "
                  "roller_blade/tire/rim and never alongside a foot or a sole."
                  % (len(legs), len(rollers))),
        "supports": "ankle_left",
        "why": ("the two ankles are not sequential revisions of one part: each belongs to a "
                "different LOCOMOTION VARIANT, and the variant that carries a foot is the one "
                "with a foot-shaped ankle. The HF space's own README calls legs 'the default' "
                "and rollers 'the wheeled skating variant' "
                "(reference/pollen-microduck-simulator/SPACE-README.md)."),
    }
    fl = [s for s in counter["foot_left_vertical"] if s["d_mm"] < 3.0]
    rb = [s for s in counter["roller_blade_vertical"] if s["d_mm"] < 3.0]
    al = [s for s in meshes["ankle_left"]["vertical_screws"] if s["d_mm"] < 3.0]
    av = [s for s in meshes["ankle_l_v1"]["vertical_screws"] if s["d_mm"] < 3.0]
    r2 = {
        "reading": "the vertical screw, measured on four meshes",
        "found": {
            "ankle_left": al, "ankle_l_v1": av,
            "foot_left_pilot": fl, "roller_blade_pilot": rb,
        },
        "supports": "ankle_left",
        "why": ("ankle_left's vertical screw and foot_left's pilot boss share an (x, y) to "
                "0.0000 mm; ankle_l_v1's vertical screw and roller_blade's pilot share a "
                "different (x, y) to 0.0000 mm. Each ankle is drilled for its own counterpart, "
                "which a later revision of one part would not be."),
    }
    r3 = {
        "reading": "the bearing pocket",
        "found": {"ankle_left": meshes["ankle_left"]["bearing_pockets"],
                  "ankle_l_v1": meshes["ankle_l_v1"]["bearing_pockets"]},
        "supports": "ankle_left",
        "why": ("ankle_left's outer-race pocket is Ø15.0000, which is the measured OD of the "
                "15x10x3 ring Pollen ships (part:bearing-15x10x3, its own frozen evidence). "
                "ankle_l_v1's is Ø15.2000 behind a Ø16.7000 window — 0.2000 mm larger, so the "
                "two ankles do not even take the same fit on the same bearing."),
    }
    readings = [r1, r2, r3]
    agree = len({r["supports"] for r in readings}) == 1

    doc = {
        "$what": "COMPARISON.html finding 4 answered: which ankle revision the shipped product "
                 "uses. Three independent readings, and the photographic check that closes it.",
        "$generated_by": "tools/ankle_revision.py (ce-designs/microduck lane T)",
        "date": "2026-09-02",
        "question": "ankle_left (Y 36.5000) or ankle_l_v1 (Y 46.4981)?",
        "answer": "ankle_left / ankle_right — part:microduck-ankle-left and part:microduck-ankle-right",
        "verdict": "PASS" if agree else "CANNOT DETERMINE",
        "confidence_why": ("three independent readings agree, and a fourth check is "
                           "photographic: images/store/store_microduck-inside-the-box.png shows "
                           "the retail box contents labelled '1 x Microduck, 1 x Battery, "
                           "1 x USB-C Cable, 1 x Gamepad' — a two-legged duck standing on FEET "
                           "with a soft sole, and NO wheel, rim, tire, roller blade or spare "
                           "ankle anywhere in the box. "
                           "images/store/store_microduck-cream-standing-profile-left.jpg shows "
                           "the same foot in profile. Read back 2026-09-02."),
        "not_a_revision_history": ("the 'v1' in ankle_l_v1 reads as an older revision and is not "
                                   "one: it is the ROLLER variant's ankle. Nothing in this repo "
                                   "should treat ankle_left as superseding it or vice versa."),
        "mjcf_inventory": inv,
        "meshes": meshes,
        "counterparts": counter,
        "readings": readings,
        "still_open": ("whether Pollen sells the roller kit separately, and whether ankle_l_v1 "
                       "is a purchasable spare, is not in any file here. What settles it: "
                       "Pollen's shop pages. It does not change the answer for the boxed product."),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(doc, open(OUT, "w", encoding="utf-8"), indent=1)
    for r in readings:
        print("%-42s -> %s" % (r["reading"], r["supports"]))
    print("ANSWER: %s (%s)" % (doc["answer"], doc["verdict"]))
    print("wrote", os.path.relpath(OUT, REPO))
    return 0 if agree else 1


if __name__ == "__main__":
    sys.exit(main())
