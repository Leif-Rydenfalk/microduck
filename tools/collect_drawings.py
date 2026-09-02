"""Assemble out/drawings/index.json — the DATA the drawings index is made of.

    python3 tools/collect_drawings.py

Reads every `out/drawings/<slug>/result.json` that `tools/draw_part.py` wrote,
joins it to the part's own `ce-parts/<slug>/component.json` record, and adds a
row for every part on the shelf that has NO sheet — with the reason, measured
from the folder rather than guessed:

    drawing       a parametric solid, drawn to MANUFACTURING-REQUIREMENTS A
    print-sheet   a published-mesh loader; no dimension can be read off it
    no-geometry   `build()` raises NotImplementedError — a `bin/triad new`
                  stub with nothing measured yet
    no-builder    no cad/part.py at all

A part missing from this file is a part nobody looked at, and that is the one
state this index must never be able to show as silence. Stdlib only — no
kernel, so the index can be regenerated on any interpreter.
"""
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

from drawing_facts import (part_record, builder_source,  # noqa: E402
                           classify, is_bought)

DRAWINGS = os.path.join(ROOT, "out", "drawings")
PARTS = os.path.join(ROOT, "ce-parts")


def shelf_slugs():
    return sorted(d for d in os.listdir(PARTS)
                  if os.path.isdir(os.path.join(PARTS, d))
                  and not d.startswith("."))


def rel(p):
    """A repo-relative path, so the index opens from anywhere in the tree."""
    if not p:
        return None
    p = os.path.abspath(p)
    return os.path.relpath(p, ROOT) if p.startswith(ROOT) else p


def _sheet_state(slug):
    """Why this slug has no sheet, measured off its folder."""
    src = builder_source(slug)
    if not src.strip():
        return "no-builder", "no cad/part.py under ce-parts/%s" % slug
    if "NotImplementedError" in src and "def build" in src and len(
            src.splitlines()) < 20:
        return "no-geometry", ("cad/part.py is a `bin/triad new part` stub — "
                               "build() raises NotImplementedError, so there "
                               "is no solid and nothing measured")
    kind, why = classify(slug)
    # NOT "drawing". A part that COULD carry a drawing and has none is a
    # different state from a part that has one, and collapsing the two is how
    # an index comes to over-report what exists.
    return ("not-drawn" if kind == "drawing" else "not-print-sheeted",
            why + " — no sheet has been generated for it yet")


#: the component.json fields every row carries
_REC_KEYS = ("title", "origin", "origin_why", "material", "process",
             "verdict", "qty_per_robot", "sector", "subsector",
             "source_reference")


def _mtime(p):
    return (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(
        os.path.getmtime(p))) if p and os.path.exists(p) else None)


def _svg_header(p):
    """(scale, size) as PRINTED in the sheet's own title line, or (None, None).

    The sheet says what it is; this asks it rather than asking the record."""
    if not p or not os.path.exists(p):
        return (None, None)
    head = open(p, encoding="utf-8", errors="replace").read(400000)
    m = re.search(r"SCALE (\d+:\d+)\s+(A\d)", head)
    return (m.group(1), m.group(2)) if m else (None, None)


def _drift(r, svg_p, rj):
    """The reason this result.json no longer describes the sheet beside it,
    or None. Three measurements, no judgement."""
    if not os.path.exists(svg_p):
        return ("result.json names %s and it is not on disk"
                % os.path.basename(svg_p))
    if os.path.getmtime(svg_p) > os.path.getmtime(rj) + 1.0:
        return ("the sheet on disk (%s) is NEWER than the result.json that "
                "reports on it (%s): another draw run rewrote it, so the "
                "verdict below is about a file that no longer exists"
                % (_mtime(svg_p), _mtime(rj)))
    if r.get("kind") == "drawing":
        scale, size = _svg_header(svg_p)
        if scale and size and (scale != r.get("scale")
                               or size != r.get("size")):
            return ("result.json says %s at %s and the sheet's own title line "
                    "says %s at %s" % (r.get("size"), r.get("scale"),
                                       size, scale))
    return None


def _side(name):
    """out/drawings/<name>.json, or {} — the optional side measurements the
    index folds in. Absent is an ANSWER here: the row says the pass has not
    been run rather than showing nothing."""
    p = os.path.join(DRAWINGS, name + ".json")
    if not os.path.exists(p):
        return {}
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:                                         # noqa: BLE001
        return {}


def main():
    feats = _side("features").get("parts", {})
    ver = _side("verify").get("parts", {})
    rows, seen = [], set()
    for slug in sorted(os.listdir(DRAWINGS)) if os.path.isdir(DRAWINGS) else []:
        rj = os.path.join(DRAWINGS, slug, "result.json")
        if not os.path.exists(rj):
            continue
        try:
            r = json.load(open(rj, encoding="utf-8"))
        except Exception as e:                                # noqa: BLE001
            rows.append({"slug": slug, "state": "unreadable",
                         "verdict": "CANNOT DETERMINE",
                         "why": "result.json will not parse: %s" % e})
            seen.add(slug)
            continue
        rec = part_record(slug)
        row = dict(r)

        # IS THE result.json STILL ABOUT THE FILE BESIDE IT? Several sessions
        # and several draw runs share this folder, and `autosheet._search`
        # rewrites `<stem>.svg` on every attempt. MEASURED 2026-09-03: the
        # shipped index said microduck-trunk-base was A2 at 2:1 and the SVG on
        # disk beside it was A1 at 5:1, 5 h 22 min newer — the index described
        # a sheet that no longer existed. An index that can publish that
        # silently is worse than no index, so the drift is measured here and
        # the row says so.
        svg_p = r.get("svg") or os.path.join(DRAWINGS, slug, slug + ".svg")
        row["result_mtime"] = _mtime(rj)
        row["svg_mtime"] = _mtime(svg_p)
        # A part that never built has no sheet BY DESIGN and must not be
        # reported as one that lost its sheet: `draw()` records the kernel's
        # own NotImplementedError before it can classify the part, so `kind`
        # and `svg` are both absent and `why` carries the reason. Asking the
        # drift question first told microduck-bottom-head-shell that its
        # result.json "names a file that is not on disk", which is true and
        # is not the reason.
        drift = _drift(r, svg_p, rj) if r.get("svg") else None
        if drift:
            row["state"] = "stale"
            row["verdict"] = "CANNOT DETERMINE"
            row["why"] = drift
            row["record"] = {k: rec.get(k) for k in _REC_KEYS}
            for k in ("svg", "dxf", "pdf", "reference_render", "thumbnail"):
                if row.get(k):
                    row[k] = rel(row[k])
            rows.append(row)
            seen.add(slug)
            continue

        # A RESULT WITH NO KIND AND NO VERDICT IS NOT A ROW, IT IS A GAP.
        # MEASURED 2026-09-03: out/drawings/microduck-robot-hat-pcb/result.json
        # (written 2026-09-02 02:35, before this generator existed) carried
        # `kind: null` and `verdict: null`; the index printed it as state
        # "unknown" with an em dash for a reason — exactly the silence the
        # docstring above says this file must never be able to show.
        if not r.get("verdict") or (not r.get("kind") and not r.get("why")):
            row["state"] = "stale-result"
            row["verdict"] = "CANNOT DETERMINE"
            row["why"] = ("result.json predates the current generator: it "
                          "carries kind=%r and verdict=%r (written %s). "
                          "Redraw the part with tools/draw_part.py."
                          % (r.get("kind"), r.get("verdict"),
                             row["result_mtime"]))
        elif not r.get("kind"):
            # THE DRAW RAN AND THE PART DID NOT BUILD. `draw()` records the
            # kernel's own reason before it can classify the part, so `kind`
            # is absent by design here and the row is that reason, not a gap.
            row["state"] = "unbuildable"
            row["verdict"] = r.get("verdict") or "CANNOT DETERMINE"
            row["why"] = r.get("why") or "the part did not build"
        else:
            row["state"] = None
        if row.get("state"):
            row["record"] = {k: rec.get(k) for k in _REC_KEYS}
            for k in ("svg", "dxf", "pdf", "reference_render", "thumbnail"):
                if row.get(k):
                    row[k] = rel(row[k])
            rows.append(row)
            seen.add(slug)
            continue

        st = r.get("kind") or "unknown"
        if st == "drawing" and (r.get("bought") or is_bought(slug)):
            # A BOUGHT PART IS NOT A PART WE MAKE. Same sheet, same read-back,
            # different meaning: the vendor's drawing governs and ours is a
            # reference for the assembly. Filing it under "dimensioned
            # drawings" would tell a shop to make an XL330 servo.
            st = "reference-drawing"
        row["state"] = st
        row["record"] = {k: rec.get(k) for k in
                         ("title", "origin", "origin_why", "material",
                          "process", "verdict", "qty_per_robot", "sector",
                          "subsector", "source_reference")}
        for k in ("svg", "dxf", "pdf", "reference_render", "thumbnail"):
            if row.get(k):
                row[k] = rel(row[k])
        for t in row.get("tiles", []) or []:
            t["path"] = rel(t.get("path"))
        row["features"] = feats.get(slug)
        row["recheck"] = ver.get(slug)
        rows.append(row)
        seen.add(slug)

    for slug in shelf_slugs():
        if slug in seen:
            continue
        state, why = _sheet_state(slug)
        rec = part_record(slug)
        rows.append({"slug": slug, "state": state, "verdict": "CANNOT DETERMINE",
                     "why": why, "kind": state,
                     "record": {k: rec.get(k) for k in
                                ("title", "origin", "origin_why", "material",
                                 "process", "verdict", "qty_per_robot",
                                 "sector", "subsector", "source_reference")}})

    rows.sort(key=lambda r: (r.get("state") != "drawing",
                             r.get("state") != "print-sheet",
                             r.get("verdict") != "PASS", r["slug"]))
    doc = {
        "$schema": "microduck/out/drawings/index.json v1",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "standard": "docs/MANUFACTURING-REQUIREMENTS.md A",
        "generator": "tools/collect_drawings.py",
        "rows": rows,
        "totals": {
            "shelf": len(shelf_slugs()),
            "drawings": sum(1 for r in rows if r.get("state") == "drawing"),
            "reference_drawings": sum(1 for r in rows
                                      if r.get("state") == "reference-drawing"),
            "print_sheets": sum(1 for r in rows
                                if r.get("state") == "print-sheet"),
            "pass": sum(1 for r in rows if r.get("verdict") == "PASS"),
            "fail": sum(1 for r in rows if r.get("verdict") == "FAIL"),
            "cannot_determine": sum(1 for r in rows
                                    if r.get("verdict") == "CANNOT DETERMINE"),
            "rechecked_pass": sum(1 for r in rows
                                  if (r.get("recheck") or {}).get("verdict")
                                  == "PASS"),
            "rechecked": sum(1 for r in rows if r.get("recheck")),
            "stale": sum(1 for r in rows
                         if r.get("state") in ("stale", "stale-result")),
        },
        "features_generated": _side("features").get("generated"),
        "recheck_generated": _side("verify").get("generated"),
    }
    out = os.path.join(DRAWINGS, "index.json")
    os.makedirs(DRAWINGS, exist_ok=True)
    json.dump(doc, open(out, "w", encoding="utf-8"), indent=1)
    print("wrote %s — %d rows (%d drawings, %d print sheets, %d PASS, %d FAIL, "
          "%d CANNOT DETERMINE)"
          % (out, len(rows), doc["totals"]["drawings"],
             doc["totals"]["print_sheets"], doc["totals"]["pass"],
             doc["totals"]["fail"], doc["totals"]["cannot_determine"]))


if __name__ == "__main__":
    main()
