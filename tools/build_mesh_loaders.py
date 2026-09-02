#!/usr/bin/env python3
"""build_mesh_loaders.py — does each mesh-backed part folder actually build a SOLID?

    ce-cad/bin/cad tools/build_mesh_loaders.py [part-slug ...]

Written 2026-09-02 for ce-designs/microduck lane T. Ten folders on this shelf
grade THEMSELVES CANNOT DETERMINE with the words "a loader: the mesh is the
vendor's; whether it builds as a closed solid is read off bin/cad part:<slug>".
That is a question with a command behind it, so this is the command. It runs
each folder's own `build()` through cecad.triad.load and reports what came back:
solids, shells, closedness, volume and bbox — measured off the built object, not
off the file it came from.

Writes out/laneT/build-report.json and prints one line per part.
Exit 0 all built · 1 at least one produced no solid and no shell · 2 broken input.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(REPO, "out", "laneT", "build-report.json")

DEFAULT = ["microduck-jaw", "microduck-jaw-soft", "microduck-soft-mouth-top",
           "microduck-top-head-shell", "microduck-bottom-head-shell",
           "microduck-face-part", "microduck-eye-ring", "microduck-m12-lens",
           "microduck-m12-lens-holder", "microduck-robot-hat-pcb",
           "microduck-trunk-shell-left", "microduck-trunk-shell-right",
           "bearing-15x10x3", "bearing-22x16x4"]


def main(argv):
    os.environ.setdefault("CE_TRIAD_ROOT", REPO + ":" + os.path.dirname(os.path.dirname(REPO)))
    import FreeCAD as App
    import cecad.triad as triad

    slugs = argv[1:] or DEFAULT
    doc = App.newDocument("laneT_build")
    rows, bad = [], 0
    for slug in slugs:
        row = {"ref": "part:" + slug}
        try:
            p = triad.load(doc, "part:" + slug)
            shp = getattr(p, "shape", None) or getattr(p, "obj", None)
            if hasattr(shp, "Shape"):
                shp = shp.Shape
            row["solids"] = len(getattr(shp, "Solids", []) or [])
            row["shells"] = len(getattr(shp, "Shells", []) or [])
            row["faces"] = len(getattr(shp, "Faces", []) or [])
            row["closed"] = bool(getattr(shp, "isClosed", lambda: False)())
            row["volume_mm3"] = round(float(getattr(shp, "Volume", 0.0)), 4)
            row["area_mm2"] = round(float(getattr(shp, "Area", 0.0)), 4)
            bb = getattr(shp, "BoundBox", None)
            if bb is not None:
                row["bbox_mm"] = {"min": [round(bb.XMin, 4), round(bb.YMin, 4), round(bb.ZMin, 4)],
                                  "max": [round(bb.XMax, 4), round(bb.YMax, 4), round(bb.ZMax, 4)],
                                  "size": [round(bb.XLength, 4), round(bb.YLength, 4), round(bb.ZLength, 4)]}
            if row["solids"]:
                row["verdict"] = "PASS"
                row["why"] = ("built %d solid(s), %d face(s), volume %.4f mm^3; the sewn shell closed"
                              % (row["solids"], row["faces"], row["volume_mm3"]))
            elif row["shells"]:
                row["verdict"] = "CANNOT DETERMINE"
                row["why"] = ("built %d shell(s) and NO solid, %d face(s) — the decimated mesh does not "
                              "sew closed, so the part places, renders and prints but carries no volume "
                              "and no boolean may be cut against it (ce-cad/CLAUDE.md)."
                              % (row["shells"], row["faces"]))
            else:
                row["verdict"] = "FAIL"
                row["why"] = "built neither a solid nor a shell"
                bad += 1
        except Exception as exc:                        # noqa: BLE001
            row["verdict"] = "FAIL"
            row["why"] = "%s: %s" % (type(exc).__name__, exc)
            bad += 1
        rows.append(row)
        print("%-12s %-34s %s" % (row["verdict"], row["ref"], row.get("why", "")[:110]))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump({"$what": "does each mesh-backed part folder build a solid? measured off the built "
                            "object through cecad.triad.load, not off the file it came from",
                   "$generated_by": "tools/build_mesh_loaders.py (ce-designs/microduck lane T)",
                   "date": "2026-09-02", "rows": rows}, fh, indent=1)
    print("wrote", os.path.relpath(OUT, REPO))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
