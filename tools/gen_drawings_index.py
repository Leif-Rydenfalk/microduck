"""Generate out/drawings/INDEX.html from out/drawings/index.json.

    python3 tools/collect_drawings.py      # the DATA
    python3 tools/gen_drawings_index.py    # the DOCUMENT

The pattern this repo uses everywhere (see tools/gen_comparison.py): a data
file and a generator, never a hand-maintained table. Nothing here measures
anything — every number on the page was measured by `tools/draw_part.py` under
the FreeCAD kernel and is copied through, so the index cannot disagree with
the sheets it indexes.

Styling: tools/doc.css, the shared academic sheet, same structure as
COMPARISON.html.
"""
import html
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "out", "drawings", "index.json")
OUT = os.path.join(ROOT, "out", "drawings", "INDEX.html")

E = html.escape


def up(p):
    """A path in index.json (repo-relative) rewritten for a page that lives in
    out/drawings/."""
    if not p:
        return None
    return os.path.relpath(os.path.join(ROOT, p),
                           os.path.join(ROOT, "out", "drawings"))


def chip(v):
    cls = {"PASS": "pass", "FAIL": "rail"}.get(v, "cd")
    return '<span class="chip %s">%s</span>' % (cls, E(str(v)))


def fmt(v, nd=4):
    if v is None:
        return '<span class="dash">—</span>'
    if isinstance(v, float):
        return "%.*f" % (nd, v)
    return E(str(v))


def bbox_txt(b):
    if not b or len(b) != 3:
        return '<span class="dash">—</span>'
    return " × ".join("%.4f" % float(x) for x in b)


def _gave_up_line(r):
    """What the sheet does NOT carry, and the last reason it could not.

    `autosheet._search` answers a failed read-back by dropping content — the
    connector dimension, then the hole callouts, then the detail bubbles, then
    the section. That is the right order and it must not be silent: measured
    2026-09-03, microduck-shin passed only after sixteen attempts by dropping
    its SECTION, and nothing on the page said the sheet had one fewer view
    than the standard asks for.
    """
    g = r.get("gave_up") or {}
    if not g:
        return "not recorded"
    lost = [k for k, v in g.items() if v is False]
    if not lost:
        return ("nothing — the sheet carries the section, the hole callouts, "
                "the connector dimension and the detail bubbles it measured")
    return ("DROPPED to make the sheet read back clean: %s. Last reason "
            "before it was dropped: %s"
            % (", ".join(sorted(lost)),
               str(r.get("last_reason") or "not recorded")[:300]))


def _radius_line(r):
    """§A.5 — Leif's own words, *"Every radius and fillet dimensioned"* — as a
    fraction rather than an impression.

    The count comes from `tools/measure_features.py`, which reads every arc
    radius off the SOLID and asks whether that number is printed on the sheet.
    Absent census, the row says the pass has not been run: a blank would read
    as full coverage, and full coverage is exactly what the shipped shelf did
    NOT have (50 of 97 distinct radii, 2026-09-03).
    """
    f = (r.get("features") or {}).get("radii")
    if f is None:
        return ("not measured — run tools/measure_features.py; the solid "
                "carries %d distinct arc radii"
                % len(r.get("radii") or []))
    on = sum(1 for x in f if x.get("on_sheet"))
    miss = [("R%.2f" % x["r"]) for x in f if not x.get("on_sheet")]
    if not f:
        return "the solid has no arc radius in the dimensionable band"
    return ("%d of %d distinct radii printed on the sheet%s"
            % (on, len(f),
               "" if not miss else " — MISSING: " + ", ".join(miss)))


#: The §A items the census counts, each with the MEASUREMENT that decides
#: whether a given sheet carries it. `None` from a probe means "not applicable
#: to this part" (a part with no holes cannot carry a hole table) and is
#: counted in neither the numerator nor the denominator; a probe that cannot
#: answer returns the string "?" and the item is reported as unmeasured.
def _ortho_views(r):
    return [v for v in (r.get("views") or [])
            if not v.startswith(("SEC", "DET", "ISO"))]


def _A_PROBES():
    return [
        ("A.4 isometric reference view on the sheet",
         lambda r: "ISO" in (r.get("views") or [])),
        ("A.4 shaded reference render of the part",
         lambda r: bool(r.get("reference_render"))),
        # NOT "3 or more views". §A asks for a third-angle set and §A.2 orders
        # the third view SUPPRESSED on a thin part — "a 2 mm rib seen on its
        # end is a black band that means nothing" — so counting sheets with
        # two orthographic views as failures would score a sheet down for
        # obeying the standard. `cecad.autosheet.choose_views` decides off the
        # bounding box; the sheet now prints that decision and its ratio, and
        # this asks whether every view it earned is on the paper.
        ("Every orthographic view the part's extents earn is drawn "
         "(A, and A.2 for the ones that earn two)",
         lambda r: ("?" if not isinstance(r.get("views_chosen"), list)
                    else set(_ortho_views(r)) == set(r["views_chosen"]))),
        ("A.5 every arc radius leadered or stated in a note",
         lambda r: (None if (r.get("features") or {}).get("radii") == []
                    else ("?" if (r.get("features") or {}).get("radii") is None
                          else all(x.get("on_sheet") for x in
                                   r["features"]["radii"])))),
        ("A.7 detail callout at a larger stated scale",
         lambda r: bool(r.get("details"))),
        ("Hole table",
         lambda r: (None if not r.get("holes")
                    else (r.get("gave_up") or {}).get("holes") is not False)),
        ("Section view with the cutting plane drawn",
         lambda r: any(v.startswith("SEC") for v in (r.get("views") or []))),
        ("A.9 print / DFM block with the tolerance basis",
         lambda r: bool(r.get("dfm"))),
        ("verify_sheet PASS on the finished SVG",
         lambda r: bool(r.get("verified")) and bool(r.get("verify_sheet"))),
        ("Independent re-check after the run (tools/verify_drawings.py)",
         lambda r: ("?" if not r.get("recheck")
                    else r["recheck"].get("verdict") == "PASS")),
    ]


def coverage(rs):
    """WHAT THE SHEETS ON THIS SHELF ACTUALLY CARRY, counted off index.json.

    §1 of this page used to open with a blanket sentence — *"Each sheet below
    carries ... every radius and fillet dimensioned with a leader, detail
    callouts at a larger stated scale ..., a hole table, a section"* — and the
    cards directly beneath it contradicted it: measured 2026-09-03 on the
    shipped page, 17 of 21 rows read "Detail callouts: none". A claim a reader
    can refute by scrolling is worse than no claim, so the paragraph is a
    COUNT now, per §A item, with the sheets that do not carry it named. Every
    figure here is computed from the same rows the cards are drawn from, so
    the two cannot disagree.
    """
    out = []
    for name, probe in _A_PROBES():
        yes, no, na, unk = [], [], [], []
        for r in rs:
            try:
                v = probe(r)
            except Exception:                                 # noqa: BLE001
                v = "?"
            (na if v is None else unk if v == "?" else yes if v else no
             ).append(r["slug"])
        out.append({"item": name, "yes": yes, "no": no, "na": na, "unk": unk})
    return out


def coverage_table(rs):
    cov = coverage(rs)
    h = ['<div class="tablewrap"><table class="data">',
         "<thead><tr><th>§A item</th><th>carried</th><th>of applicable"
         "</th><th>sheets that do not carry it</th></tr></thead><tbody>"]
    for c in cov:
        appl = len(c["yes"]) + len(c["no"])
        miss = ", ".join(c["no"]) or "—"
        if c["unk"]:
            miss += (" · NOT MEASURED on %d sheet(s): %s"
                     % (len(c["unk"]), ", ".join(c["unk"])))
        if c["na"]:
            miss += (" · not applicable to %d part(s): %s"
                     % (len(c["na"]), ", ".join(c["na"])))
        h.append("<tr><th scope=\"row\">%s</th><td>%d</td><td>%d</td>"
                 "<td>%s</td></tr>" % (E(c["item"]), len(c["yes"]), appl,
                                       E(miss)))
    h.append("</tbody></table></div>")
    return "\n".join(h)


def sheet_card(r):
    slug = r["slug"]
    thumb = up(r.get("thumbnail"))
    svg = up(r.get("svg"))
    dxf = up(r.get("dxf"))
    pdf = up(r.get("pdf"))
    ref = up(r.get("reference_render"))
    kind = r.get("kind") or r.get("state")
    parts = ['<article class="sheet" id="%s">' % E(slug)]
    # THE VERDICT BESIDE A SHEET IS THE SHEET'S VERDICT.
    #
    # Until 2026-09-04 this line printed result.json's bare `verdict`, which
    # grades whether the PART BUILT — and 25 of 27 rows read PASS while
    # ce-cad/bin/sheetcheck read 27 FAIL on the same sheets against A2+A3+A4.
    # A reader scrolling this page took the green chip for "a machinist can
    # cut this". So the big chip is the SHEET verdict, the build verdict sits
    # behind the word "build", and the row says which rules failed.
    sv = r.get("sheet_verdict") or "CANNOT DETERMINE"
    bv = r.get("build_verdict") or "CANNOT DETERMINE"
    parts.append('<div class="sheethead"><h3>%s</h3><div>'
                 '<span class="vlab">sheet A2+A3+A4</span> %s '
                 '<span class="vlab">build</span> %s '
                 '<span class="kindtag">%s</span></div></div>'
                 % (E(slug), chip(sv), chip(bv), E(str(kind))))
    parts.append('<p class="paircap"><b>SHEET %s</b> — %s. '
                 '<b>BUILD %s</b> — the part built and every number on the '
                 'sheet re-measured off the solid. Source: %s.</p>'
                 % (E(sv), E(str(r.get("sheet_verdict_why")
                                 or "no rule detail recorded")[:300]),
                    E(bv), E(str(r.get("sheet_verdict_source") or "—"))))
    if r.get("sheet_rules"):
        parts.append('<p class="paircap">' + " · ".join(
            "%s %s" % (E(k), chip(v))
            for k, v in sorted(r["sheet_rules"].items())) + "</p>")
    if r.get("sheet_sections"):
        parts.append('<p class="paircap">by section — ' + " · ".join(
            "%s %s" % (E(k), chip(r["sheet_sections"][k]))
            for k in ("A", "A2", "A3", "A4")
            if k in r["sheet_sections"]) + "</p>")
    if r.get("title"):
        parts.append('<p class="paircap">%s</p>' % E(str(r["title"])[:240]))
    if thumb:
        link = svg or thumb
        parts.append('<figure><a href="%s"><img src="%s" alt="%s sheet"></a>'
                     '<figcaption>The finished sheet, photographed in headless '
                     'Chrome off the SVG on disk and read back — not a preview '
                     'of what the generator meant to draw.</figcaption>'
                     '</figure>' % (E(link), E(thumb), E(slug)))
    elif ref:
        parts.append('<figure><img src="%s" alt="%s reference render">'
                     '<figcaption>Reference render (no sheet thumbnail).'
                     '</figcaption></figure>' % (E(ref), E(slug)))

    rows = []
    if kind in ("drawing", "reference-drawing"):
        rows += [
            ("Sheet", "%s at %s, %d attempt(s)"
             % (r.get("size", "?"), r.get("scale", "?"), r.get("attempts", 0))),
            ("Views", ", ".join(r.get("views") or []) or "—"),
            ("Detail callouts", "; ".join(r.get("details") or []) or "none"),
            ("Envelope (mm)", bbox_txt(r.get("bbox_mm"))),
            ("Holes measured", "%s (%s counterbore)"
             % (r.get("holes"), r.get("counterbores"))),
            ("Ø on the solid", ", ".join("%.3f" % d for d in
                                         (r.get("hole_diameters") or []))
             or "none"),
            ("Slots / grooves", "%s / %s" % (r.get("slots"), r.get("grooves"))),
            ("Radii on the solid", ", ".join("R%.3f" % x for x in
                                             (r.get("radii") or [])[:14])
             or "none"),
            ("Thinnest wall, whole solid",
             ("%s mm at (%s), %s mm sample spacing"
              % (fmt(r.get("thinnest_wall_mm")),
                 ", ".join("%.3f" % c
                           for c in (r.get("thinnest_wall_where") or [])),
                 fmt(r.get("thinnest_wall_step_mm"), 3)))
             if r.get("thinnest_wall_mm") is not None
             else "CANNOT DETERMINE"),
            ("Hidden lines", "; ".join(
                "%s: %s" % (k, (v or {}).get("why", "—"))
                for k, v in sorted((r.get("hidden_lines") or {}).items()))
             or "not recorded"),
            ("verify_sheet", "%s (independent read-back: %s)"
             % (r.get("verified"), r.get("verify_sheet"))),
            ("Re-checked after the run",
             ("%s — the SVG on disk re-read against a freshly built solid on "
              "%s; the sheet's own header says %s %s"
              % ((r.get("recheck") or {}).get("verdict"),
                 (r.get("recheck") or {}).get("svg_mtime"),
                 ((r.get("recheck") or {}).get("svg_header") or {}).get("scale"),
                 ((r.get("recheck") or {}).get("svg_header") or {}).get("size")))
             if r.get("recheck") else
             "not run — tools/verify_drawings.py has not been over this sheet"),
            ("Orthographic views the extents earn",
             ("%s (primary %s) — cecad.autosheet.choose_views off the "
              "bounding box; %s"
              % (", ".join(r["views_chosen"]), r.get("views_primary"),
                 ("a third view of this part would be its own edge, which "
                  "docs/MANUFACTURING-REQUIREMENTS.md §A.2 orders suppressed"
                  if len(r["views_chosen"]) < 3
                  else "the full third-angle set")))
             if isinstance(r.get("views_chosen"), list)
             else str(r.get("views_chosen")
                      or "not recorded — redraw with the current "
                         "tools/draw_part.py")),
            ("Radii the builder's own text names",
             ", ".join("R%.2f" % x for x in
                       (r.get("design_radii_named_in_builder") or []))
             or "none — cad/part.py names no radius in its text"),
            ("Arc radii cecad.inspect measures on the solid",
             (", ".join("R%.2f" % x for x in r["arc_radii_on_solid"])
              or "none")
             if isinstance(r.get("arc_radii_on_solid"), list)
             else str(r.get("arc_radii_on_solid") or "not recorded")),
            ("Named-but-not-an-edge radii",
             r.get("design_radii_gap")
             or ("none — every radius the builder names is a circular edge "
                 "on the solid, or the builder names none. A radius that is "
                 "not an edge cannot carry a leader; where one exists the "
                 "sheet states it in one line and this row carries the rest.")),
            ("Content the search had to give up", _gave_up_line(r)),
            ("§A.5 radii dimensioned", _radius_line(r)),
            ("§A.6 feature census",
             (r.get("features") or {}).get("A6_summary")
             or "not run — tools/measure_features.py has not been over this part"),
        ]
        if r.get("warnings"):
            rows.append(("Warnings", "; ".join(r["warnings"])))
    elif kind == "print-sheet":
        rows += [
            ("Why no drawing", r.get("kind_why", "—")),
            ("Envelope (mm)", bbox_txt(r.get("bbox_mm"))),
            ("Shells / solids", "%s / %s" % (r.get("shells"), r.get("solids"))),
            ("Volume", ("%s mm³" % fmt(r.get("volume_mm3")))
             if r.get("volume_mm3") is not None else "CANNOT DETERMINE"),
            ("Mass", ("%s g" % fmt(r.get("mass_g")))
             if r.get("mass_g") is not None else "CANNOT DETERMINE"),
            ("Orientation", r.get("orientation", "—")),
            ("Print this file", r.get("stl") or "CANNOT DETERMINE"),
            ("sha256", r.get("stl_sha256") or "CANNOT DETERMINE"),
            ("verify_print_sheet", str(r.get("verified"))),
        ]
    else:
        rows.append(("Why there is no sheet", r.get("why", "—")))
    rec = r.get("record") or {}
    rows += [("component.json origin", rec.get("origin") or "unset"),
             ("component.json verdict", rec.get("verdict") or "—"),
             ("Material / process", "%s / %s" % (rec.get("material") or "—",
                                                 rec.get("process") or "—"))]
    parts.append('<div class="tablewrap"><table class="data"><tbody>')
    for k, v in rows:
        parts.append("<tr><th scope=\"row\">%s</th><td>%s</td></tr>"
                     % (E(k), E(str(v)) if not str(v).startswith("<") else v))
    parts.append("</tbody></table></div>")

    files = [(n, p) for n, p in (("SVG", svg), ("DXF", dxf), ("PDF", pdf),
                                 ("reference render", ref)) if p]
    if files:
        parts.append('<p class="files">' + " · ".join(
            '<a href="%s">%s</a>' % (E(p), E(n)) for n, p in files) + "</p>")
    if r.get("checks"):
        bad = [c for c in r["checks"] if not c["ok"]]
        if bad:
            parts.append('<p class="note"><b>Failed checks:</b> '
                         + "; ".join(E(c["name"]) for c in bad) + "</p>")
    parts.append("</article>")
    return "\n".join(parts)


#: What would settle each state of "no answer", by the state `collect_drawings`
#: measured. A CANNOT DETERMINE that does not say what closes it is a shrug,
#: and this page is where the shrug would live.
_SETTLES = {
    "no-geometry": ("Write `build()` in ce-parts/<slug>/current/cad/part.py "
                    "against a measured source (the vendor drawing, a "
                    "calliper, or the published mesh) — the folder is a "
                    "`bin/triad new part` stub and there is no solid to draw."),
    "no-builder": ("Create ce-parts/<slug>/current/cad/part.py. There is no "
                   "builder at all, so nothing in this repo can be measured "
                   "or drawn for this slug."),
    "not-drawn": ("Run `ce-cad/bin/cad tools/draw_part.py <slug>`. The part "
                  "builds and would carry a drawing; no sheet has been "
                  "generated yet."),
    "not-print-sheeted": ("Run `ce-cad/bin/cad tools/draw_part.py <slug>`. "
                          "The part is mesh-backed and would carry a print "
                          "sheet; none has been generated yet."),
    "unbuildable": ("Fix the builder named in the reason — the kernel raised "
                    "while loading the part, so neither document can be "
                    "produced."),
    "stale": ("Redraw the part: the result.json and the sheet beside it "
              "describe different files, so neither can be trusted until one "
              "run writes both."),
    "stale-result": ("Redraw the part with tools/draw_part.py — its "
                     "result.json predates the current generator."),
    "unreadable": ("Delete and redraw: the result.json will not parse."),
    "print-sheet": ("Name the geometry file. A print sheet whose whole "
                    "purpose is the file it prints, with no file, is the one "
                    "thing this document cannot supply."),
}


def open_items(rows):
    """Every row this pass could not answer, with what settles it.

    Generated from the same index.json as everything else, so an item cannot
    be quietly dropped from the list by editing prose.
    """
    out = []
    for r in rows:
        # OPEN AGAINST THE SHEET, not against the build. A part that built
        # perfectly and whose sheet no shop can cut from is open.
        if r.get("sheet_verdict") == "PASS":
            continue
        st = r.get("state") or r.get("kind") or "unknown"
        out.append({"slug": r["slug"], "state": st,
                    "verdict": r.get("sheet_verdict") or "CANNOT DETERMINE",
                    "build_verdict": r.get("build_verdict")
                    or "CANNOT DETERMINE",
                    "why": (r.get("sheet_verdict_why") or r.get("why")
                            or _first_failed(r) or "no reason recorded — "
                            "that is itself a defect of this row"),
                    "settles": _SETTLES.get(st, "Not classified — read the "
                                            "reason and the sheet.")})
    out.sort(key=lambda d: (d["verdict"] != "FAIL", d["state"], d["slug"]))
    return out


def _first_failed(r):
    bad = [c["name"] for c in (r.get("checks") or []) if not c.get("ok")]
    if bad:
        return "failed checks: " + "; ".join(bad)
    rc = r.get("recheck") or {}
    if rc.get("failed"):
        return "independent re-check failed: " + "; ".join(
            str(x) for x in rc["failed"])[:600]
    return None


def open_table(rows):
    items = open_items(rows)
    if not items:
        return ('<p class="note">Every row on this shelf is PASS against '
                'A2+A3+A4. Nothing is open.</p>')
    h = ['<div class="tablewrap"><table class="data">',
         "<thead><tr><th>part</th><th>sheet verdict</th><th>build verdict"
         "</th><th>state</th>"
         "<th>why</th><th>what settles it</th></tr></thead><tbody>"]
    for d in items:
        h.append("<tr><th scope=\"row\">%s</th><td>%s</td><td>%s</td>"
                 "<td>%s</td><td>%s</td><td>%s</td></tr>"
                 % (E(d["slug"]), chip(d["verdict"]),
                    chip(d.get("build_verdict")), E(d["state"]),
                    E(str(d["why"])[:700]), E(d["settles"])))
    h.append("</tbody></table></div>")
    return "\n".join(h)


FINDINGS = os.path.join(ROOT, "tools", "data", "drawings_findings.json")


def findings_section():
    """§7 — the sixteen problems an outside reader measured on this deliverable
    on 2026-09-03, and what each one turned out to be.

    Generated from `tools/data/drawings_findings.json` so a finding cannot be
    dropped from the page by editing prose, and so the verdict on a finding
    sits beside the measurement that earned it. A finding whose verdict is
    CANNOT DETERMINE carries what would settle it; the others carry the
    before and after they were judged on.
    """
    if not os.path.exists(FINDINGS):
        return ('<p class="note">tools/data/drawings_findings.json is not on '
                'disk — the review ledger cannot be rendered, and its absence '
                'is not evidence that there was nothing to review.</p>')
    d = json.load(open(FINDINGS, encoding="utf-8"))
    h = ['<p class="lede">%s</p>' % E(d.get("about", "")),
         '<div class="tablewrap"><table class="data">',
         "<thead><tr><th>#</th><th>what was reported</th><th>verdict</th>"
         "<th>measured before</th><th>measured after</th></tr></thead><tbody>"]
    for f in d["findings"]:
        after = f.get("after") or ""
        if f.get("settles"):
            after += ("  WHAT SETTLES IT: " + f["settles"])
        h.append("<tr><th scope=\"row\">%s</th><td><b>%s</b><br><span "
                 "class=\"kindtag\">%s</span></td><td>%s</td><td>%s</td>"
                 "<td>%s</td></tr>"
                 % (E(str(f["id"])), E(f["title"]), E(f.get("where") or ""),
                    chip(f["verdict"]), E(f.get("before") or ""), E(after)))
    h.append("</tbody></table></div>")
    n = len(d["findings"])
    fixed = sum(1 for f in d["findings"] if f["verdict"].startswith("FIXED"))
    nd = sum(1 for f in d["findings"] if f["verdict"].startswith("NOT A"))
    cd = n - fixed - nd
    h.append('<p class="note">%d reported, %d fixed, %d measured to be a '
             'defect somewhere other than where it was reported, %d still '
             'open.</p>' % (n, fixed, nd, cd))
    return "\n".join(h)


def main():
    if not os.path.exists(DATA):
        sys.exit("no %s — run tools/collect_drawings.py first" % DATA)
    doc = json.load(open(DATA, encoding="utf-8"))
    rows = doc["rows"]
    t = doc["totals"]
    drawings = [r for r in rows if r.get("state") == "drawing" and r.get("svg")]
    refs = [r for r in rows if r.get("state") == "reference-drawing"
            and r.get("svg")]
    prints = [r for r in rows if r.get("state") == "print-sheet"
              and r.get("svg")]
    done = drawings + refs + prints
    rest = [r for r in rows if r not in done]

    def group(rs, title, n, lede, empty, anchor=None):
        h = ['<section id="%s"><h2><span class="n">%s</span>%s</h2>'
             % (anchor or title.lower().replace(" ", "-"), n, E(title)),
             '<p class="lede">%s</p>' % lede]
        h.append("".join(sheet_card(r) for r in rs) if rs
                 else '<p class="note">%s</p>' % empty)
        h.append("</section>")
        return "\n".join(h)

    # THE COUNTERS MUST ADD UP, AND THE PAGE SAYS SO. MEASURED 2026-09-03 on
    # the shipped index: 16 drawings + 1 print sheet + 36 cannot-determine =
    # 53 against a headline of 54 parts on the shelf, because one row carried
    # `verdict: null` and was counted by nothing. An arithmetic identity
    # printed on the page cannot go quietly wrong.
    acc = (t["build_pass"] + t["build_fail"] + t["build_cannot_determine"])
    recon = ("TWO VERDICTS, TWO SUBJECTS, AND ONLY ONE OF THEM ANSWERS 'CAN A "
             "MACHINIST CUT THIS'. SHEET (docs/MANUFACTURING-REQUIREMENTS.md "
             "A2+A3+A4, measured by ce-cad/bin/sheetcheck %s): %d PASS, %d "
             "FAIL, %d CANNOT DETERMINE. BUILD (the part built and its sheet "
             "read back off the solid): %d PASS + %d FAIL + %d CANNOT "
             "DETERMINE = %d, against %d parts on the shelf — %s"
             % (t.get("sheet_verdict_measured") or "NOT MEASURED",
                t.get("sheet_pass", 0), t.get("sheet_fail", 0),
                t.get("sheet_cannot_determine", 0),
                t["build_pass"], t["build_fail"], t["build_cannot_determine"],
                acc, t["shelf"],
                "every part is accounted for."
                if acc == t["shelf"] else
                "THEY DO NOT AGREE: %d row(s) carry a build verdict this "
                "page cannot count, which is a defect in "
                "tools/collect_drawings.py, not a rounding."
                % abs(t["shelf"] - acc)))
    if not doc.get("features_generated"):
        recon += (" The §A.6 feature census has not been run: "
                  "out/drawings/features.json is absent, so no row carries "
                  "one (ce-cad/bin/cad tools/measure_features.py).")
    if not doc.get("recheck_generated"):
        recon += (" The independent re-check has not been run: "
                  "out/drawings/verify.json is absent "
                  "(ce-cad/bin/cad tools/verify_drawings.py).")
    else:
        recon += (" Independent re-check of the files on disk: %s, %d of %d "
                  "rows rechecked, %d PASS."
                  % (doc["recheck_generated"], t.get("rechecked", 0),
                     len(rows), t.get("rechecked_pass", 0)))

    unsheeted = {}
    for r in rest:
        unsheeted.setdefault(r.get("state", "unknown"), []).append(r)
    rest_tbl = ['<div class="tablewrap"><table><thead><tr>'
                '<th>Part</th><th>State</th><th>Origin</th>'
                '<th>Why there is no sheet</th></tr></thead><tbody>']
    for st in sorted(unsheeted):
        for r in sorted(unsheeted[st], key=lambda x: x["slug"]):
            rest_tbl.append(
                "<tr><td><code>%s</code></td><td>%s</td><td>%s</td>"
                "<td>%s</td></tr>"
                % (E(r["slug"]), E(st),
                   E(str((r.get("record") or {}).get("origin") or "unset")),
                   E(str(r.get("why") or r.get("kind_why") or "—"))))
    rest_tbl.append("</tbody></table></div>")

    body = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mechanical drawings — index</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="../../tools/doc.css">
<style>
  .sheet{{border:1px solid var(--hair);background:var(--card);padding:16px 18px;margin:18px 0}}
  .sheethead{{display:flex;justify-content:space-between;align-items:baseline;gap:16px;flex-wrap:wrap}}
  .sheethead h3{{margin:0;font-size:17px;font-family:var(--mono);font-weight:500}}
  .kindtag{{font-family:var(--sans);font-size:10.5px;font-weight:600;letter-spacing:.07em;
           text-transform:uppercase;color:var(--ink-2);border:1px solid var(--hair);padding:2px 7px;margin-left:8px}}
  .sheet figure{{margin:12px 0;padding:6px;background:#fff}}
  .sheet figure img{{width:100%;background:#fff;border:1px solid var(--hair)}}
  .sheet table.data th[scope=row]{{width:34%;text-transform:none;letter-spacing:0;font-size:12.5px;
           border-top:none;border-bottom:1px solid var(--hair);white-space:normal;vertical-align:top}}
  .sheet table.data td{{font-family:var(--mono);font-size:12px}}
  .files{{font-family:var(--sans);font-size:12.5px;margin:6px 0 0}}
  .paircap{{font-family:var(--sans);font-size:12.5px;color:var(--ink-2);margin:6px 0 0}}
  .note{{font-size:13.5px;color:var(--ink-2);max-width:46em}}
  td.dash,.dash{{color:#b3aea4}}
  .vlab{{font-family:var(--sans);font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2);margin-right:3px}}
  .statbar{{display:flex;flex-wrap:wrap;gap:0;border-bottom:1px solid var(--hair);margin:8px 0 2px}}
  .stat{{padding:12px 26px 12px 0;margin-right:22px}}
  .stat b{{display:block;font-weight:700;font-size:22px;font-variant-numeric:tabular-nums}}
  .stat span{{font-family:var(--sans);font-size:12px;color:var(--ink-2)}}
</style>
</head>
<body>
<div class="wrap">
<p class="backlink"><a href="../../RELEASE.html">← Release dossier</a> ·
<a href="../../docs/MANUFACTURING-REQUIREMENTS.md">the standard these sheets are held to</a></p>

<header class="hero">
  <p class="eyebrow">Microduck reverse-engineering · manufacturing files</p>
  <h1>Mechanical drawings — index</h1>
  <p class="sub">Every part on the shelf, and the document it carries: a dimensioned shop
  drawing where a parametric solid exists, a print sheet where the geometry is a published
  mesh, and a named reason where there is neither. Every number here was measured off the
  solid under the FreeCAD kernel by <code>tools/draw_part.py</code> and read back off the
  finished SVG by <code>verify_sheet</code>; this page copies, and measures nothing of its
  own.</p>
  <div class="rev">
    <span>MD-DWG-000 · index</span><span>{E(doc['generated'])}</span>
    <span>data: out/drawings/index.json</span>
    <span>generator: tools/gen_drawings_index.py</span>
    <span>standard: {E(doc['standard'])}</span>
  </div>
</header>

<div class="statbar">
  <div class="stat"><b>{t['shelf']}</b><span>parts on the shelf</span></div>
  <div class="stat"><b>{t['drawings']}</b><span>dimensioned drawings</span></div>
  <div class="stat"><b>{t.get('reference_drawings', 0)}</b><span>bought-part references</span></div>
  <div class="stat"><b>{t['print_sheets']}</b><span>print sheets</span></div>
  <div class="stat"><b>{t.get('sheet_pass', 0)}</b><span>SHEET PASS &mdash; A2+A3+A4</span></div>
  <div class="stat"><b>{t.get('sheet_fail', 0)}</b><span>SHEET FAIL</span></div>
  <div class="stat"><b>{t.get('sheet_cannot_determine', 0)}</b><span>sheet cannot determine</span></div>
  <div class="stat"><b>{t.get('build_pass', 0)}</b><span>build PASS &mdash; the part built</span></div>
  <div class="stat"><b>{t.get('build_fail', 0)}</b><span>build FAIL</span></div>
  <div class="stat"><b>{t.get('build_cannot_determine', 0)}</b><span>build cannot determine</span></div>
  <div class="stat"><b>{t.get('stale', 0)}</b><span>stale rows</span></div>
  <div class="stat"><b>{t.get('rechecked', 0)}</b><span>independently rechecked</span></div>
</div>
<p class="note">{E(recon)}</p>

<nav class="toc">
  <a href="#how">1 What a sheet must carry</a>
  <a href="#dimensioned-drawings">2 Dimensioned drawings</a>
  <a href="#reference-drawings">3 Reference drawings</a>
  <a href="#print-sheets">4 Print sheets</a>
  <a href="#no-sheet">5 Parts with no sheet</a>
  <a href="#open">6 What could not be settled</a>
  <a href="#review">7 The outside review</a>
</nav>

<section id="how">
  <h2><span class="n">1</span>What a sheet must carry, and how it is checked</h2>
  <p class="lede">The acceptance standard is <code>docs/MANUFACTURING-REQUIREMENTS.md</code> §A,
  which is Leif's own review of the first generated files. What the sheets on this shelf
  <em>actually</em> carry against it is COUNTED below, not asserted — every figure computed
  from the same <code>out/drawings/index.json</code> rows the cards further down are drawn
  from, so the table and the cards cannot disagree. An item a sheet does not carry names that
  sheet. Absence is a measurement here: an item that is not applicable to a part (a hole table
  on a part with no holes) is outside the denominator and is named as such, and an item no
  pass has measured yet is reported as unmeasured rather than as carried.</p>
  {coverage_table(drawings + refs)}
  <p class="note">The census covers the {len(drawings) + len(refs)} dimensioned and reference
  sheets. Print sheets (§4) are a different document and are held to
  <code>verify_print_sheet</code>, not to §A.</p>
  <div class="grid2">
    <div class="card"><h3>Every number is read back</h3><p><code>verify_sheet</code> parses the
    finished SVG and checks the stated scale, the title-block bbox and volume, both overall
    dimensions on every view, every hole-table row against <code>cecad.inspect</code>, every
    printed radius against the solid's own arcs, the detail rings, the isometric, the DFM
    block, that no two labels overlap and that nothing runs outside the frame.</p></div>
    <div class="card"><h3>A mesh gets no drawing</h3><p>§A.3: a vendor mesh part gets no
    dimensioned drawing, because every dimension read off a decimated triangulation is a
    dimension of the decimation. It gets a print sheet instead — envelope to 4 dp, mass,
    orientation, the STL path and its sha256, and the refusal printed on the sheet.</p></div>
    <div class="card"><h3>The tolerance basis is stated, not guessed</h3><p>Every Bambu
    machine on this farm records <code>tolerance_mm: null</code> with the cite “no coupon
    printed and measured on this machine”, and Bambu Lab's own H2D Pro specification carries
    no dimensional-accuracy line. The sheets say so, and print the two cited outsourced
    figures beside it. Sources: <code>tools/drawing_facts.py</code>.</p></div>
    <div class="card"><h3>Generator defects, fixed and tested</h3><p>GOAL.md finding 5 named
    two: the generator merged coaxial holes across air into a phantom counterbore, and its
    only wall figure was a scan of one cutting plane. Both are fixed in <code>ce-cad</code>
    with <code>tests/test_cbore_and_wall.py</code>, which fails on the old code and passes on
    the new. Five more were measured on the shipped sheets afterwards and are fixed here:
    an ASCII capital O printed where every other diameter carries Ø; a counterbore whose face
    the code could not name printing “?X” (it is centred in its bore — it opens on neither
    face, and the table says <code>INT</code>); a whole-solid ray minimum printed as the wall
    with no verdict, beside a note saying it is not a wall (both figures now, and the
    printable one — the smallest neighbourhood-median thickness — carries the PASS/FAIL);
    a sheet with no detail bubble saying nothing about why; and a note that stated a radius
    band in R notation, putting two radii on the paper the solid has not got.</p></div>
    <div class="card"><h3>A part with nothing to dimension gets a print sheet</h3><p>§A.3
    refuses a drawing off geometry with no dimension a shop can work to, and the case it was
    written for is a decimated vendor mesh. Measured 2026-09-03 there is a second and worse
    case, because it looks like a drawing: <code>part:microduck-sole-left</code> is a
    parametric solid whose floor is lofted station to station through a measured 27 × 31
    table, so it carries 1363 visible edges in its top view (TechDraw.projectEx) against
    4–131 for a clean shop view on this shelf — and zero holes and zero arc radii in the
    leaderable band. Its sheet carried three numbers over a forest of seams, which is exactly
    the “unusable detail … random lines” §A.1–A.2 orders removed. Those parts are routed to a
    print sheet by measurement (<code>tools/drawing_facts.py _seam_forest</code>), never by
    choice, and the sheet states the count and the reason.</p></div>
    <div class="card"><h3>Radii the builder names and the solid has not got</h3><p>The same
    sole names “heel arc R7.2, toe arc R6.9, side fillets R7.9” in its own builder, and
    <code>cecad.inspect.arc_radii</code> finds no arc at all on the solid those lines build —
    the blends are sampled points of a loft, not circular edges, so no leader can be drawn to
    one. A reader comparing the builder to the paper would conclude three radii were dropped.
    Both facts are measured per part (<code>design_radii_named_in_builder</code> against
    <code>arc_radii_on_solid</code>) and the gap is stated on the sheet.</p></div>
    <div class="card"><h3>Every radius, including the ones no view can leader</h3><p>A radius
    is leadered only in a view that sees its edge square — a circle seen obliquely projects as
    an ellipse whose fitted radius is not the edge's. A radius <em>no</em> orthographic view on
    the sheet sees square used to be invisible to the read-back, and 50 of 97 distinct solid
    arc radii carried a leader across the shelf. Those radii are now STATED in the notes with
    their count, their axis and a point on the metal, and <code>verify_sheet</code> fails a
    sheet carrying a band radius that is neither leadered nor stated
    (<code>ce-cad/tests/test_sheet_hygiene.py</code>).</p></div>
    <div class="card"><h3>No line printed through a label</h3><p>Leif's <q>random lines</q> had
    a second half nothing measured: <code>overlapping_labels</code> answers text over text, and
    a cutting-plane line drawn straight through a hole callout passed every check.
    <code>lines_over_labels</code> reads the CUT groups back out of the finished SVG; a sheet
    with a plane through a label fails, and the search reaches for a different cutting plane
    or bigger paper.</p></div>
  </div>
</section>

{group(drawings, "Dimensioned drawings", 2,
       "Parts whose <code>cad/part.py</code> constructs a parametric solid.",
       "No dimensioned drawing has been generated.")}

{group(refs, "Reference drawings — bought parts", 3,
       "Parts we BUY. The solid is our parametric model of the vendor's part, so the "
       "sheet is a reference for checking the assembly against a real envelope — the "
       "vendor's own drawing governs every dimension. Each sheet says so in its "
       "print/DFM block.",
       "No bought part has been drawn.", anchor="reference-drawings")}

{group(prints, "Print sheets", 4,
       "Parts backed by a published mesh. No dimension can be read off a decimated "
       "triangulation, so these carry what is true of a mesh and say what is missing.",
       "No print sheet has been generated.")}

<section id="no-sheet">
  <h2><span class="n">5</span>Parts with no sheet, and why</h2>
  <p class="lede">Every remaining folder on the shelf, with the measured reason. A part
  missing from this page would be a part nobody looked at; that state is not available here.</p>
  {''.join(rest_tbl)}
</section>

<section id="open">
  <h2><span class="n">6</span>What this pass could not settle</h2>
  <p class="lede">Every row that is not PASS, with the reason measured off the folder and the
  one action that closes it. Generated from the same <code>out/drawings/index.json</code> as
  the cards above, so an item cannot be dropped from this list by editing prose. A row here is
  a work item, not a shrug.</p>
  {open_table(rows)}
</section>

<section id="review">
  <h2><span class="n">7</span>What an outside reader found, and what it turned out to be</h2>
  {findings_section()}
</section>

</div>
</body>
</html>
"""
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(body)
    print("wrote %s (%d drawings, %d bought-part references, %d print sheets, "
          "%d other)" % (OUT, len(drawings), len(refs), len(prints), len(rest)))


if __name__ == "__main__":
    main()
