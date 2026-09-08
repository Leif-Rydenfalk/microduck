"""out/drawings/BASELINE.md — the TRUE sheet baseline, generated from the
instrument's own output.

    ce-cad/bin/sheetcheck --all out/drawings --refresh \
        --json out/drawings/sheetcheck.json
    python3 tools/gen_sheet_baseline.py

Nothing here measures anything and nothing here is typed. Every number is
copied out of `out/drawings/sheetcheck.json`, which
`ce-cad/cecad/sheetcheck.py` wrote by reading the SVGs, their rendered PNGs
and the SOLIDS through the FreeCAD kernel. If a number on this page is wrong,
the checker is wrong, and it is fixed there.

WHY THIS FILE EXISTS. Two verdicts were being read as one:
`out/drawings/<slug>/result.json` graded whether the PART BUILT and read 25
PASS; `sheetcheck` grades whether A SHOP CAN CUT FROM THE SHEET against
docs/MANUFACTURING-REQUIREMENTS.md A2+A3+A4 and read 27 FAIL on the same
sheets. See out/drawings/VERDICT-RECONCILIATION.md. This page publishes the
sheet number, per sheet and per rule, so the iteration that follows has a
before to be measured against.
"""
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "out", "drawings", "sheetcheck.json")
OUT = os.path.join(ROOT, "out", "drawings", "BASELINE.md")

V = {"PASS": "PASS", "FAIL": "FAIL", "CANNOT DETERMINE": "CD"}


def v(x):
    return V.get(x, "—")


def main():
    d = json.load(open(SRC, encoding="utf-8"))
    rows = d["sheets"]
    rules = d["rules"]
    secs = ["A", "A2", "A3", "A4"]
    s = d.get("summary") or {}
    L = []
    A = L.append

    A("# THE TRUE SHEET BASELINE — every sheet, every rule, measured\n")
    A("Generated %s by `tools/gen_sheet_baseline.py` from "
      "`out/drawings/sheetcheck.json`, which "
      "`ce-cad/bin/sheetcheck --all --refresh` wrote at **%s**. Standard: "
      "`%s`. **Nothing on this page is typed** — every figure is copied from "
      "the instrument's output.\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),
                                      d.get("generated"), d.get("standard")))
    A("## The one sentence\n")
    bv = s.get("by_verdict", {})
    A("**%d sheets graded — PASS %d · FAIL %d · CANNOT DETERMINE %d.** "
      "%d features were enumerated off the solids and %d of them carry a "
      "printed, class-matched dimension (%.1f %%). %d CANNOT DETERMINE "
      "feature rows exist and %d are printed on a sheet's own face. **%d of "
      "%d sheets carry any render with colour AND shadow; %d carry the six "
      "A3 asks for.**\n"
      % (s.get("sheets", len(rows)), bv.get("PASS", 0), bv.get("FAIL", 0),
         bv.get("CANNOT DETERMINE", 0), s.get("features_enumerated", 0),
         s.get("features_dimensioned", 0),
         100.0 * s.get("features_dimensioned", 0)
         / max(1, s.get("features_enumerated", 0)),
         s.get("cd_rows_total", 0), s.get("cd_rows_disclosed_on_sheet", 0),
         s.get("sheets_with_any_colour_shadow_render", 0),
         s.get("sheets", len(rows)),
         s.get("sheets_meeting_render_count", 0)))

    A("## Per rule, over every sheet\n")
    A("| rule | section | PASS | FAIL | CANNOT DETERMINE | the threshold |")
    A("|---|---|---|---|---|---|")
    th = d.get("thresholds", {})
    LIM = {
        "line_ratio": "<line> elements <= %.0fx the solid's edges"
                      % th.get("max_line_ratio", 10),
        "coverage": "content occupancy of the frame >= %.0f %%"
                    % th.get("min_coverage_pct", 85),
        "empty_rect": "largest empty rectangle < %.0f %% of frame"
                      % th.get("max_empty_rect_pct", 5),
        "font": "no text below %.1f mm" % th.get("min_font_mm", 3.5),
        "iso": ">= %d isometric views, each >= %.0f %% of sheet"
               % (th.get("min_iso_views", 4), th.get("min_iso_area_pct", 15)),
        "renders": ">= %d COLOURED AND SHADOWED renders, each >= %.0f %%, "
                   "largest >= %.0f %%"
                   % (th.get("min_shaded_renders", 6),
                      th.get("min_render_area_pct", 12),
                      th.get("min_largest_render_pct", 20)),
        "curve_density": "no %.0f mm patch above %.2f mm of line per mm2"
                         % (th.get("density_cell_mm", 5),
                            th.get("max_line_density_mm_per_mm2", 1.43)),
        "dim_coverage": "%.0f %% of enumerated features dimensioned, AND "
                        "every refusal printed on the sheet"
                        % th.get("min_dim_coverage_pct", 100),
    }
    insec = {r: [k for k in secs if r in (d.get("sections") or {}).get(k, [])]
             for r in rules}
    for r in rules:
        c = (s.get("by_rule") or {}).get(r, {})
        A("| `%s` | %s | %d | %d | %d | %s |"
          % (r, ", ".join(insec.get(r) or ["—"]), c.get("PASS", 0),
             c.get("FAIL", 0), c.get("CANNOT DETERMINE", 0), LIM.get(r, "")))
    A("")

    A("## Per SECTION of the standard, graded apart\n")
    A("| section | what it demands | PASS | FAIL | CANNOT DETERMINE |")
    A("|---|---|---|---|---|")
    WHAT = {
        "A": "the first review: no facet texture, an isometric reference "
             "view, every radius and detail dimensioned",
        "A2": "the layout review: no tessellation, iso as a principal view, "
              "use the whole sheet (at A2's own 60 %), text >= 3.5 mm, every "
              "visible feature dimensioned",
        "A3": "renders are primary: >= 6 colour+shadow renders, many more "
              "angles, no line-art hatch on a curved surface, zero white "
              "space (>= 85 % coverage, largest empty rect < 5 %)",
        "A4": "the completeness gate: every feature carries a real toleranced "
              "dimension, and every refusal is printed on the sheet",
    }
    for k in secs:
        c = (s.get("by_section") or {}).get(k, {})
        A("| **%s** | %s | %d | %d | %d |"
          % (k, WHAT[k], c.get("PASS", 0), c.get("FAIL", 0),
             c.get("CANNOT DETERMINE", 0)))
    A("")

    A("## Every sheet, every rule\n")
    A("| sheet | kind | verdict | " + " | ".join("`%s`" % r for r in rules)
      + " | A | A2 | A3 | A4 |")
    A("|---" * (len(rules) + 7) + "|")
    for r in sorted(rows, key=lambda x: x["slug"]):
        sec = r.get("sections") or {}
        A("| `%s` | %s | **%s** | %s | %s |"
          % (r["slug"],
             "print" if r.get("sheet_kind") == "print-sheet" else "drawing",
             v(r["verdict"]),
             " | ".join(v((r.get("rules") or {}).get(k)) for k in rules),
             " | ".join(v(sec.get(k)) for k in secs)))
    A("")

    A("## A4 in full — features enumerated against features dimensioned\n")
    A("A feature is ONE NUMBER a shop has to be told: a hole is a diameter, "
      "a depth and a position from each of two datums — four rows, because a "
      "sheet that prints the diameter and leaves the position off is exactly "
      "the sheet A4 forbids.\n")
    A("| sheet | enumerated | dimensioned | % | refusals | printed on the "
      "sheet | the classes it could not see |")
    A("|---|---|---|---|---|---|---|")
    for r in sorted(rows, key=lambda x: x["slug"]):
        pct = r.get("dim_coverage_pct")
        if pct is None:
            pct = r.get("dim_coverage_pct_not_a_verdict")
        kinds = sorted({c["kind"] for c in
                        (r.get("cd_rows_undisclosed") or [])})
        A("| `%s` | %s | %s | %s | %s | %s | %s |"
          % (r["slug"], r.get("features_enumerated", "—"),
             r.get("features_dimensioned", "—"),
             ("%.1f" % pct) if pct is not None else "REFUSED",
             r.get("cd_rows_total", "—"),
             r.get("cd_rows_disclosed_on_sheet", "—"),
             ", ".join(kinds) or "—"))
    A("")

    A("## A3's renders — colour, shadow, and how much paper they cover\n")
    A("`shaded` is the older colour-OR-tone bar. `lit` is the pair A3 rule 1 "
      "actually asks for and Leif restated on 2026-09-04: **coloured AND "
      "shadowed**. A flat matte blob is coloured and carries no form.\n")
    A("| sheet | images | shaded | **colour AND shadow** | coloured but flat "
      "| shaded but grey | largest render, % of sheet | iso views |")
    A("|---|---|---|---|---|---|---|---|")
    for r in sorted(rows, key=lambda x: x["slug"]):
        areas = r.get("shaded_render_areas_pct_of_sheet") or [0.0]
        A("| `%s` | %s | %s | **%s** | %s | %s | %.2f | %s |"
          % (r["slug"], r.get("image_count", 0),
             r.get("shaded_render_count", 0),
             r.get("colour_and_shadow_render_count", 0),
             r.get("renders_coloured_but_flat", 0),
             r.get("renders_shadowed_but_grey", 0),
             max(areas), r.get("iso_count", 0)))
    A("")

    A("## Coverage — and WHICH quantity the gate is\n")
    A("Settled in `docs/MANUFACTURING-REQUIREMENTS.md` A5.1: **A3 rule 4's "
      "85 %% is `occupancy_pct`** — %s. `ink_pct` and `cell_pct` are reported "
      "second opinions. A wide gap between them is not a dispute about the "
      "verdict: it says the views are SPARSE INSIDE their own bounding "
      "boxes.\n" % (s.get("coverage_measured_on") or ""))
    A("| sheet | occupancy % (THE RULE) | 5 mm-cell ink % | ink % | largest "
      "empty rect, % of frame | smallest text, mm |")
    A("|---|---|---|---|---|---|")
    for r in sorted(rows, key=lambda x: x["slug"]):
        ler = (r.get("largest_empty_rect") or {}).get("pct_of_frame")
        A("| `%s` | %s | %s | %s | %s | %s |"
          % (r["slug"],
             _n(r.get("occupancy_pct")), _n(r.get("cell_pct")),
             _n(r.get("ink_pct")), _n(ler), _n(r.get("font_min_mm"))))
    A("")

    miss = d.get("part_dirs_with_no_sheet") or []
    A("## The bucket a table of graded sheets cannot show\n")
    A("**%d part folder(s) hold NO sheet SVG at all — each a FAIL.** A part "
      "whose drawing never built is the worst sheet there is.\n" % len(miss))
    if miss:
        A("| part | why there is no sheet |")
        A("|---|---|")
        for m in miss:
            A("| `%s` | %s |"
              % (m["slug"], (m.get("record_why") or m.get("why") or "")[:220]))
        A("")
    sk = d.get("dirs_skipped_not_a_part") or []
    A("**%d directory(ies) skipped as not a part folder**, each with the "
      "reason — a silent skip and a silent inclusion are the same defect from "
      "opposite sides.\n" % len(sk))
    if sk:
        A("| directory | why it is not a part folder |")
        A("|---|---|")
        for x in sk:
            A("| `%s` | %s |" % (x["name"], str(x.get("why"))[:220]))
        A("")

    A("## What this baseline is for\n")
    A("It is the BEFORE of an iteration loop, not a report. The loop is: "
      "run `ce-cad/bin/sheetcheck --all out/drawings --refresh --json "
      "out/drawings/sheetcheck.json`, regenerate this page, change the "
      "GENERATOR (`cecad/autosheet.py`, `cecad/sheets.py`, "
      "`tools/draw_part.py` — never a single sheet by hand), redraw, and "
      "compare. **A threshold is never moved to make a sheet pass.** If a "
      "rule is wrong, it is changed deliberately in "
      "`docs/MANUFACTURING-REQUIREMENTS.md` with the measurement that says "
      "why.\n")

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print("wrote %s — %d sheets, %d rules, %d sections"
          % (OUT, len(rows), len(rules), len(secs)))


def _n(x, nd=2):
    return "—" if x is None else ("%.*f" % (nd, x))


main()
