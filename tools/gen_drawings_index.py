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


def sheet_card(r):
    slug = r["slug"]
    thumb = up(r.get("thumbnail"))
    svg = up(r.get("svg"))
    dxf = up(r.get("dxf"))
    pdf = up(r.get("pdf"))
    ref = up(r.get("reference_render"))
    kind = r.get("kind") or r.get("state")
    parts = ['<article class="sheet" id="%s">' % E(slug)]
    parts.append('<div class="sheethead"><h3>%s</h3><div>%s '
                 '<span class="kindtag">%s</span></div></div>'
                 % (E(slug), chip(r.get("verdict", "CANNOT DETERMINE")),
                    E(str(kind))))
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
    acc = t["pass"] + t["fail"] + t["cannot_determine"]
    recon = ("%d PASS + %d FAIL + %d CANNOT DETERMINE = %d, against %d parts "
             "on the shelf — %s"
             % (t["pass"], t["fail"], t["cannot_determine"], acc, t["shelf"],
                "every part is accounted for."
                if acc == t["shelf"] else
                "THEY DO NOT AGREE: %d row(s) carry a verdict this page "
                "cannot count, which is a defect in "
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
  <div class="stat"><b>{t['pass']}</b><span>verify PASS</span></div>
  <div class="stat"><b>{t['fail']}</b><span>verify FAIL</span></div>
  <div class="stat"><b>{t['cannot_determine']}</b><span>cannot determine</span></div>
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
</nav>

<section id="how">
  <h2><span class="n">1</span>What a sheet must carry, and how it is checked</h2>
  <p class="lede">The acceptance standard is <code>docs/MANUFACTURING-REQUIREMENTS.md</code> §A,
  which is Leif's own review of the first generated files. Each sheet below carries, measured
  off the solid: a third-angle orthographic set, an isometric reference view, a shaded
  reference render of the part, every radius and fillet dimensioned with a leader, detail
  callouts at a larger stated scale on the dense regions, a hole table, a section with wall
  dimensions and the cutting-plane line on a view that can show it, a print/DFM note block
  with the tolerance basis, the surface finish, and the title block.</p>
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
    <div class="card"><h3>Two generator defects, fixed and tested</h3><p>The generator merged
    coaxial holes across air into a phantom counterbore, and its only wall figure was a scan
    of one cutting plane. Both are fixed in <code>ce-cad</code> with
    <code>tests/test_cbore_and_wall.py</code>, which fails on the old code and passes on the
    new.</p></div>
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
