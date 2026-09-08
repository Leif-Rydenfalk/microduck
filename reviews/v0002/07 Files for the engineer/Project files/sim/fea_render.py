#!/usr/bin/env python3
"""fea_render.py — re-paint the von Mises PNG of every study whose report.json
verdict changed (out/sim-evidence/fea/rerender.txt from sim/fea_rejudge.py),
with cecad.feaimage, and read each picture back (F1 skeptic finding 11: a
picture captioned FAIL beside a table row that says CANNOT DETERMINE).

    ce-cad/bin/cad sim/fea_render.py [--all]
"""
import json
import os
import sys

import cecad.feaimage as feaimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVID = os.path.join(ROOT, "out", "sim-evidence")
FEA = os.path.join(EVID, "fea")


def main():
    todo = []
    if "--all" in sys.argv:
        for d in sorted(os.listdir(FEA)):
            if os.path.isfile(os.path.join(FEA, d, "report.json")) and "_h" not in d and d != "materials_ankle_drop":
                todo.append((os.path.join(FEA, d), os.path.join(FEA, d + ".png")))
    else:
        for line in open(os.path.join(FEA, "rerender.txt")):
            wd, png = line.split()
            todo.append((os.path.join(ROOT, wd), png))
    for wd, png in todo:
        rpath = os.path.join(wd, "report.json")
        study = os.path.join(EVID, "fea_" + os.path.basename(wd) + ".json")
        fea = feaimage.produce(rpath, out_png=png, annotate=False)
        if os.path.exists(study):
            r = json.load(open(study))
            r["looked_at"] = [{"image": os.path.relpath(png, ROOT), "facts": fea["image_facts"], "caption_verdict": fea["verdict"],
                               "check": "peak von Mises recomputed from the .frd agrees with the report to 0.5 % (cecad.feaimage); caption verdict = study verdict"}]
            assert fea["verdict"] == r["verdict"], (fea["verdict"], r["verdict"])
            json.dump(r, open(study, "w"), indent=1)
        print("repainted", os.path.relpath(png, ROOT), fea["verdict"], fea["image_facts"]["size"], fea["image_facts"]["distinct_colors"])
        sys.stdout.flush()


if __name__ == "__main__":
    main()
