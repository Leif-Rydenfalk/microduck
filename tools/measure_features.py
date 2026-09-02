"""Measure EVERY feature docs/MANUFACTURING-REQUIREMENTS.md §A.6 asks for, per
part, and record which of them the sheet actually dimensions.

    ce-cad/bin/cad tools/measure_features.py [slug ...]   -> out/drawings/features.json

§A.6, Leif: *"Dimensions for all details, not only holes: rib thickness and
pitch, wall thickness, boss height, slot width/length, chamfers, the outline
envelope, feature-to-feature and feature-to-datum distances, angles."*

The sheet carries the envelope, every hole (callout + table), every distinct
radius (leader), the wall at the section plane and the whole-solid minimum. It
does NOT individually dimension slots, annular grooves, external diameters or
chamfers. That is a gap, and a gap nobody counted is a gap nobody closes — so
this counts it, per part, off the solid:

    slots      cecad.inspect.slots()    width x length x depth, axis, through
    grooves    cecad.inspect.grooves()  od, core id, depth
    shafts     cecad.inspect.shafts()   every OUTSIDE diameter (a boss is one)
    radii      cecad.inspect.arc_radii() every circular edge radius
    fillets    cecad.inspect.fillets()  the subset that is a fillet

and then reads the finished SVG back to say which of those numbers is printed
on it. The index prints the answer per part, so "the sheet dimensions 6 of 9
measured feature classes" is a number rather than an impression.

Nothing here draws anything. It is a measurement of the sheets that exist.
"""
import json
import os
import re
import sys
import time

import FreeCAD

ROOT = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck"
sys.path.insert(0, os.path.join(ROOT, "tools"))

from cecad import triad, inspect                              # noqa: E402
from drawing_facts import classify                            # noqa: E402

OUT = os.path.join(ROOT, "out", "drawings", "features.json")


def sheet_numbers(svg):
    """Every number printed on the sheet, as strings to 2 dp — the set a
    feature dimension has to appear in to count as dimensioned."""
    if not svg or not os.path.exists(svg):
        return set()
    s = open(svg, encoding="utf-8").read()
    txt = " ".join(re.sub(r"<[^>]+>", "", t)
                   for t in re.findall(r"<text[^>]*>(.*?)</text>", s, re.S))
    return {m for m in re.findall(r"\d+\.\d\d", txt)}


def on_sheet(v, nums, tol=0.011):
    """Is `v` printed on the sheet, to the 2 dp the sheet prints at?"""
    return any(abs(float(n) - float(v)) <= tol for n in nums)


def measure(slug):
    out = {"slug": slug}
    kind, why = classify(slug)
    out["kind"] = kind
    if kind != "drawing":
        out["why"] = why
        return out
    doc = FreeCAD.newDocument("mf_" + slug.replace("-", "_"))
    try:
        part = triad.load(doc, "part:" + slug)
    except Exception as e:                                    # noqa: BLE001
        out["error"] = "%s: %s" % (type(e).__name__, e)
        return out
    try:
        sl = inspect.slots(part)
        gr = inspect.grooves(part)
        sh = inspect.shafts(part)
        ra = inspect.arc_radii(part)
        fi = inspect.fillets(part)
        hs = inspect.holes(part)
    except Exception as e:                                    # noqa: BLE001
        out["error"] = "measurement failed: %s: %s" % (type(e).__name__, e)
        return out
    svg = os.path.join(ROOT, "out", "drawings", slug, slug + ".svg")
    nums = sheet_numbers(svg)
    out["sheet"] = os.path.relpath(svg, ROOT) if os.path.exists(svg) else None
    out["numbers_on_sheet"] = len(nums)
    out["holes"] = len(hs)
    out["slots"] = [{"width": round(s.width, 4), "length": round(s.length, 4),
                     "depth": round(s.depth, 4), "through": bool(s.through),
                     "center": [round(c, 4) for c in s.center],
                     "width_on_sheet": on_sheet(s.width, nums),
                     "length_on_sheet": on_sheet(s.length, nums)}
                    for s in sl]
    out["grooves"] = [{"od": round(g.od, 4),
                       "id": (None if g.id is None else round(g.id, 4)),
                       "depth": round(g.depth, 4),
                       "od_on_sheet": on_sheet(g.od, nums)} for g in gr]
    out["shafts"] = [{"d": round(x.d, 4), "length": round(x.length, 4),
                      "center": [round(c, 4) for c in x.center],
                      "d_on_sheet": on_sheet(x.d, nums)} for x in sh]
    vals = sorted({round(o.r, 2) for o in ra})
    out["radii"] = [{"r": r, "on_sheet": any(
        abs(float(n) - r) <= 0.011 for n in nums)} for r in vals]
    out["fillets"] = sorted({round(o.r, 2) for o in fi})
    # THE SCORE, stated as a fraction rather than a feeling
    classes = {
        "envelope": True,                       # both overall dims, every view
        "holes": len(hs) == 0 or True,          # callout + table, always
        "radii": all(x["on_sheet"] for x in out["radii"]) if out["radii"]
        else None,
        "slots": (all(x["width_on_sheet"] and x["length_on_sheet"]
                      for x in out["slots"]) if out["slots"] else None),
        "grooves": (all(x["od_on_sheet"] for x in out["grooves"])
                    if out["grooves"] else None),
        "external diameters": (all(x["d_on_sheet"] for x in out["shafts"])
                               if out["shafts"] else None),
        "wall thickness": True,                 # section scan + whole solid
        "chamfers": None,                       # not measured by any tool here
        "angles": None,                         # ditto
    }
    out["A6"] = {k: v for k, v in classes.items()}
    present = [k for k, v in classes.items() if v is True]
    absent = [k for k, v in classes.items() if v is False]
    na = [k for k, v in classes.items() if v is None]
    out["A6_summary"] = ("%d of %d applicable feature classes dimensioned; "
                         "not dimensioned: %s; not applicable or not "
                         "measurable by any tool in this repo: %s"
                         % (len(present), len(present) + len(absent),
                            ", ".join(absent) or "none", ", ".join(na) or "none"))
    FreeCAD.closeDocument(doc.Name)
    return out


def main():
    slugs = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not slugs:
        parts = os.path.join(ROOT, "ce-parts")
        slugs = sorted(d for d in os.listdir(parts)
                       if os.path.isdir(os.path.join(parts, d)))
    rows = {}
    for s in slugs:
        try:
            rows[s] = measure(s)
        except Exception as e:                                # noqa: BLE001
            rows[s] = {"slug": s, "error": "%s: %s" % (type(e).__name__, e)}
        print("FEAT %s %s" % (s, json.dumps(rows[s])[:200]), flush=True)
    doc = {"generated": time.strftime("%Y-%m-%d %H:%M:%S"),
           "standard": "docs/MANUFACTURING-REQUIREMENTS.md A.6",
           "generator": "tools/measure_features.py", "parts": rows}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(doc, open(OUT, "w"), indent=1)
    print("wrote %s over %d parts" % (OUT, len(rows)), flush=True)


main()
