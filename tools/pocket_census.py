"""tools/pocket_census.py — does ANY pocket in this robot accept a nut?

Runs cecad.meshpockets over every Pollen reference mesh and writes
out/fasteners/pockets.json. This is the measurement behind the decision NOT
to create nut, washer and heat-set-insert parts: the community
reconstruction recommends 50 M2 nuts and 60 M2 heat-set inserts
(reference/.../docs/fastener-reconstruction.en.md, "Purchase Estimate"),
and its own limitation 4 says non-circular features were never detected.
Nobody had looked. This looks.

Run:  ce-cad/bin/cad tools/pocket_census.py
"""
import glob
import json
import os
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, "/Users/leifrydenfalk/dev/ce-workshop/ce-cad")

from cecad import meshpockets  # noqa: E402

MESHDIR = os.path.join(REPO, "reference/pollen-microduck-simulator/meshes")
OUT = os.path.join(REPO, "out/fasteners/pockets.json")

# heat-set insert bore, for the second question. The ONE heat-set insert
# family on the workshop shelf with a measured geometry is
# part:insert-m3-heatset (ruthex / CNC Kitchen form, vendor geometry — no ISO
# or DIN governs these parts, see that folder's origin_why). Its M3 member's
# outer knurl diameter sets the bore an insert needs. The M2 member of the
# same family is not on the shelf and is not invented here; what IS stated is
# the rule a bore must satisfy to be an insert bore at all.
INSERT_RULE = {
    "what": "a heat-set insert bore is a straight bore of roughly the insert's "
            "OUTER knurl diameter, not a tap-drill pilot. For M2 inserts of the "
            "ruthex/CNC Kitchen form the outer diameter is ~3.2-3.6 mm, so the "
            "bore is 3.0-3.4 mm.",
    "bore_window_mm_for_M2_insert": [3.0, 3.4],
    "bore_window_mm_for_M2.5_insert": [3.6, 4.2],
    "why_this_matters": "a Ø1.6 mm hole cannot take a heat-set insert. It is the "
                        "M2 TAP DRILL — the hole you cut a thread in, or drive a "
                        "self-tapping screw into. The two are not interchangeable "
                        "and the diameter tells them apart with no judgement.",
    "source": "part:insert-m3-heatset component.json (workshop shelf), vendor "
              "geometry; window scaled to M2/M2.5 from that family's published "
              "M3 figures and stated as a WINDOW, not a claimed dimension.",
}


def main():
    t0 = time.time()
    files = sorted(glob.glob(os.path.join(MESHDIR, "*.stl")))
    by_mesh = {}
    totals = {"meshes": 0, "meshes_failed": 0, "planar_patches": 0,
              "opposed_wall_pairs": 0, "pockets": 0, "hex": 0, "rect": 0,
              "slot": 0, "other": 0, "hex_that_name_a_nut": 0}
    failures = []
    for f in files:
        name = os.path.basename(f)[:-4]
        try:
            r = meshpockets.pockets(f, scale=1000.0)
        except Exception as e:                       # noqa: BLE001
            failures.append({"mesh": name, "error": "%s: %s"
                             % (type(e).__name__, e)})
            totals["meshes_failed"] += 1
            continue
        c = r["counts"]
        totals["meshes"] += 1
        for k in ("planar_patches", "opposed_wall_pairs", "pockets", "hex",
                  "rect", "slot", "hex_that_name_a_nut"):
            totals[k] += c[k]
        totals["other"] += sum(1 for p in r["pockets"]
                               if p["kind"].startswith("prismatic"))
        by_mesh[name] = {
            "counts": c,
            "pockets": r["pockets"],
            "rejected_reasons": _hist(r["rejected"]),
        }
        print("%-42s patches %4d pairs %3d pockets %2d hex %2d nut %2d"
              % (name, c["planar_patches"], c["opposed_wall_pairs"],
                 c["pockets"], c["hex"], c["hex_that_name_a_nut"]))

    named = []
    for m, d in by_mesh.items():
        for p in d["pockets"]:
            if p.get("nut"):
                named.append(dict(p, mesh=m))

    doc = {
        "doc": {
            "id": "MD-POCKET-001", "rev": "A",
            "title": "Non-circular pocket census — the nut question, measured",
            "generated_by": "tools/pocket_census.py",
            "instrument": "cecad.meshpockets (new 2026-09-04; selftest 15/15 "
                          "PASS, CECAD_MESHPOCKETS_BREAK=1 -> 14/15, =2 -> 13/15)",
            "reads": ["reference/pollen-microduck-simulator/meshes/*.stl"],
        },
        "question": "Does any pocket in this robot's geometry accept a hex nut, "
                    "and does any bore accept a heat-set insert?",
        "why_it_is_asked": "the community reconstruction "
            "(reference/makerworld-3250889/upstream-github-fanhao375-microduck-"
            "replica/docs/fastener-reconstruction.en.md, 'Purchase Estimate') "
            "suggests 50 M2 nuts 'where there is nothing to tap into' and 60 M2 "
            "heat-set inserts 'recommended over tapping printed plastic "
            "directly'. Both lines are BUILD ADVICE for someone printing a "
            "replica, not measurements of the product, and that document's own "
            "limitation 4 says non-circular features were never detected by its "
            "tool. Ours is the first instrument here that can see them.",
        "totals": totals,
        "nut_pockets_found": named,
        "heat_set_insert_rule": INSERT_RULE,
        "by_mesh": by_mesh,
        "failures": failures,
        "seconds": round(time.time() - t0, 2),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        json.dump(doc, fh, indent=1)
    print("\nTOTALS %s" % json.dumps(totals))
    print("nut pockets found: %d" % len(named))
    print("wrote %s in %.1f s" % (OUT, time.time() - t0))


def _hist(rej):
    h = {}
    for r in rej:
        key = r["why"].split("—")[0].strip()[:70]
        h[key] = h.get(key, 0) + 1
    return h


if __name__ == "__main__":
    main()
