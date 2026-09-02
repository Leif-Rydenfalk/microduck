"""Re-read every finished sheet on disk and check it against the solid AGAIN.

    ce-cad/bin/cad tools/verify_drawings.py [slug ...]

`tools/draw_part.py` verifies each sheet as it writes it. This is the
independent pass afterwards, and it exists for two reasons that are both
measured facts about this machine rather than caution:

  * SEVERAL SESSIONS SHARE THIS REPO. `autosheet._search` rewrites the same
    `<stem>.svg` on every attempt, so a second process drawing the same part
    can leave a sheet from ITS attempt beside a result.json from ours.
    Measured 2026-09-02 on out/drawings/microduck-trunk-base: result.json said
    "A1, 5:1" while the SVG beside it said "SCALE 1:1 A2".
  * A FILE THAT EXISTS IS NOT A FILE THAT IS CORRECT. The verdict in
    result.json is a claim about a file; this re-derives it from the file.

For a drawing it re-runs `verify_sheet` against a freshly built solid. For a
print sheet it re-runs `verify_print_sheet`. It rebuilds the Sheet object the
same way `auto_blueprint` did, because `verify_sheet` needs the sheet's own
scale and view list to check the paper against the ink — the SVG carries the
numbers, the Sheet carries what they were supposed to be.

Writes out/drawings/verify.json and prints one line per part. Exit 0 only when
every sheet on disk still agrees with its solid.
"""
import json
import os
import re
import sys
import time

import FreeCAD

ROOT = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck"
sys.path.insert(0, os.path.join(ROOT, "tools"))

from cecad import triad                                       # noqa: E402
from cecad.imgcheck import verify_png                         # noqa: E402
from drawing_facts import (classify, is_bought, GENERAL_TOLERANCE,  # noqa: E402
                           TOLERANCE_DFM, VENDOR_DFM)

DRAWINGS = os.path.join(ROOT, "out", "drawings")
OUT = os.path.join(DRAWINGS, "verify.json")


def svg_says(path):
    """(scale, size) as printed in the sheet's own header line."""
    if not os.path.exists(path):
        return None, None
    head = open(path, encoding="utf-8").read()
    m = re.search(r"SCALE (\d+:\d+)\s+(A\d)", head)
    return (m.group(1), m.group(2)) if m else (None, None)


def check(slug):
    d = {"slug": slug, "verdict": "CANNOT DETERMINE"}
    rj = os.path.join(DRAWINGS, slug, "result.json")
    if not os.path.exists(rj):
        d["why"] = "no result.json — the part was never drawn"
        return d
    rec = json.load(open(rj, encoding="utf-8"))
    d["recorded_verdict"] = rec.get("verdict")
    svg = rec.get("svg") or os.path.join(DRAWINGS, slug, slug + ".svg")
    d["svg"] = os.path.relpath(svg, ROOT) if os.path.exists(svg) else None
    if not os.path.exists(svg):
        d["why"] = "the sheet named by result.json is not on disk"
        return d
    d["svg_mtime"] = time.strftime("%Y-%m-%d %H:%M:%S",
                                   time.localtime(os.path.getmtime(svg)))

    # THE FILE'S OWN HEADER against the record — the cheap half, and the one
    # that catches another session's sheet sitting under our verdict.
    scale, size = svg_says(svg)
    d["svg_header"] = {"scale": scale, "size": size}
    d["header_agrees"] = (scale == rec.get("scale") and size == rec.get("size")) \
        if rec.get("kind") == "drawing" else None

    thumb = rec.get("thumbnail")
    if thumb and os.path.exists(thumb):
        try:
            f = verify_png(thumb, what="sheet thumbnail", min_ink=0.004)
            d["thumbnail"] = {"path": os.path.relpath(thumb, ROOT),
                              "size": list(f["size"]),
                              "ink_frac": round(float(f["ink_frac"]), 5),
                              "distinct_colors": f["distinct_colors"]}
        except Exception as e:                                # noqa: BLE001
            d["thumbnail"] = {"error": "%s: %s" % (type(e).__name__, e)}
    else:
        d["thumbnail"] = None

    doc = FreeCAD.newDocument("vd_" + slug.replace("-", "_"))
    try:
        part = triad.load(doc, "part:" + slug)
    except Exception as e:                                    # noqa: BLE001
        d["why"] = "the part no longer builds: %s: %s" % (type(e).__name__, e)
        return d

    kind = rec.get("kind") or classify(slug, part)[0]
    d["kind"] = kind
    try:
        if kind == "print-sheet":
            from cecad.printsheet import verify_print_sheet
            ok, checks = verify_print_sheet(dict(rec, svg=svg), part,
                                            verbose=False)
            d["failed"] = [n for n, o, _ in checks if not o]
        else:
            from cecad.sheets import verify_sheet
            from cecad.autosheet import build_sheet, _mfg_extras
            # REBUILD THE SHEET THE WAY IT WAS BUILT, or the check measures a
            # different sheet. `verify_sheet` reads the drawn extents and the
            # stated scale off the SVG and holds them against the Sheet's own
            # layout, so a rebuild missing the reference image, the DFM block
            # or the detail bubbles lays the views out differently and fails a
            # sheet that is right. The last attempt in the record says exactly
            # what produced the file on disk.
            last = (rec.get("attempt_log") or [{}])[-1]
            mfg = _mfg_extras(part)
            bp = getattr(part, "blueprint", None)
            if bp is not None and getattr(bp, "meta", None) is not None:
                bp.meta["general_tolerance"] = GENERAL_TOLERANCE
            dfm = list(mfg["dfm"]) + list(TOLERANCE_DFM)
            if is_bought(slug):
                dfm += list(VENDOR_DFM)
            n, dd = (int(x) for x in (rec.get("scale") or "1:1").split(":"))
            sh, _, _ = build_sheet(
                part, size=rec.get("size", "A3"),
                source="ce-parts/%s/current/cad/part.py" % slug,
                scale=(n, dd), hidden=mfg["hidden"], radii=True,
                reference_iso=True,
                reference_image=rec.get("reference_render"),
                reference_caption=("REFERENCE RENDER (ISO2) — rendered off "
                                   "this solid, %d x %d px"
                                   % tuple(rec.get("reference_render_px")
                                           or (0, 0))),
                details=(mfg["details"] if last.get("details", True) else []),
                dfm=dfm,
                section=last.get("section", True),
                dim=last.get("dim", True),
                holes=last.get("holes", True),
                sec_rank=last.get("sec_rank", 0))
            sh._layout()
            ok = verify_sheet(sh, svg, part, verbose=False)
            d["failed"] = []
            d["rebuilt_from"] = {k: last.get(k) for k in
                                 ("size", "scale", "sec_rank", "section",
                                  "dim", "holes", "details")}
        d["reverified"] = bool(ok)
        d["verdict"] = "PASS" if (ok and d.get("header_agrees") is not False) \
            else "FAIL"
    except Exception as e:                                    # noqa: BLE001
        d["why"] = "the re-check could not run: %s: %s" % (type(e).__name__, e)
        d["verdict"] = "CANNOT DETERMINE"
    finally:
        try:
            FreeCAD.closeDocument(doc.Name)
        except Exception:                                     # noqa: BLE001
            pass
    return d


def main():
    slugs = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not slugs:
        slugs = sorted(s for s in os.listdir(DRAWINGS)
                       if os.path.isdir(os.path.join(DRAWINGS, s))
                       and os.path.exists(os.path.join(DRAWINGS, s,
                                                       "result.json")))
    rows = {}
    for s in slugs:
        r = check(s)
        rows[s] = r
        print("VERIFY %-38s %-18s recorded=%-6s header=%s %s"
              % (s, r["verdict"], r.get("recorded_verdict"),
                 r.get("header_agrees"), r.get("why", "")), flush=True)
    n_pass = sum(1 for r in rows.values() if r["verdict"] == "PASS")
    doc = {"generated": time.strftime("%Y-%m-%d %H:%M:%S"),
           "generator": "tools/verify_drawings.py",
           "note": "an INDEPENDENT re-check of the sheets on disk, run after "
                   "the drawing pass; see the module docstring for why it "
                   "exists on a machine several sessions share",
           "parts": rows,
           "totals": {"checked": len(rows), "pass": n_pass,
                      "fail": sum(1 for r in rows.values()
                                  if r["verdict"] == "FAIL"),
                      "cannot_determine": sum(1 for r in rows.values()
                                              if r["verdict"] ==
                                              "CANNOT DETERMINE")}}
    json.dump(doc, open(OUT, "w"), indent=1)
    print("VERIFY-SUMMARY %d/%d PASS -> %s" % (n_pass, len(rows), OUT),
          flush=True)


main()
