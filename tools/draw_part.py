"""Draw ONE microduck part to out/drawings/<slug>/, to the standard in
docs/MANUFACTURING-REQUIREMENTS.md §A, and read the result back.

    ce-cad/bin/cad tools/draw_part.py <slug>

Two documents, and WHICH ONE a part gets is measured, not chosen:

  * a PARAMETRIC part (its `cad/part.py` builds a solid) gets the shop
    drawing — third-angle set, isometric reference, a shaded reference render,
    every radius dimensioned, detail bubbles at a larger scale, hole table,
    section with wall dimensions, print/DFM block, tolerance basis, title
    block. `cecad.autosheet.auto_blueprint(manufacturing=True)`.
  * a MESH-BACKED part (its builder is a `cecad.meshshelve` loader for a
    vendor's published mesh) gets a PRINT SHEET — `cecad.printsheet` — because
    §A.3 of the standard forbids a drawing off a decimated triangulation, and
    the part still has to be made.

Writes out/drawings/<slug>/result.json: TWO verdicts, every measurement, and
what the sheet had to give up to read back clean.

TWO VERDICTS, NEVER ONE. This file used to publish a bare `verdict`, and that
key was read as "a machinist can cut this" when what it graded was "the part
built and its sheet read back against the solid". Measured 2026-09-04: the 27
shipped sheets read 25 PASS by that key and 27 FAIL by `ce-cad/bin/sheetcheck`,
which grades the SHEET against MANUFACTURING-REQUIREMENTS A2+A3+A4. The two
numbers never contradicted; they graded different subjects, and one label was
carrying both. So:

  build_verdict   did `cad/part.py` build a solid, did a sheet emit, and does
                  every number on it read back off that solid (`verify_sheet`)?
  sheet_verdict   is the SHEET usable in a shop — the eight rules of A2+A3+A4,
                  copied here from `cecad.sheetcheck.grade_sheet`, measured on
                  the file this run just wrote.

`verdict` is NOT written. A reader who wants one number must say which.
"""
import json
import os
import sys
import time
import traceback

import FreeCAD

ROOT = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck"
sys.path.insert(0, os.path.join(ROOT, "tools"))

from cecad import triad, inspect                              # noqa: E402
from cecad.autosheet import auto_blueprint                    # noqa: E402
from cecad.sheets import verify_sheet                         # noqa: E402
from cecad.printsheet import (print_sheet, verify_print_sheet,  # noqa: E402
                              _NO_FILE)

from drawing_facts import (TOLERANCE_DFM, VENDOR_DFM, classify,  # noqa: E402
                           part_record, is_bought, GENERAL_TOLERANCE,
                           mesh_geometry_of, design_radii)


#: printed into every result.json so a reader who opens one file, with no
#: context, cannot mistake one subject for the other.
VERDICT_NOTE = (
    "build_verdict grades THE PART AND ITS READ-BACK (cad/part.py built a "
    "solid, a sheet emitted, and every number on the sheet re-measured off "
    "that solid). sheet_verdict grades THE SHEET against "
    "docs/MANUFACTURING-REQUIREMENTS.md A2+A3+A4 via ce-cad/bin/sheetcheck "
    "(line_ratio, coverage, empty_rect, font, iso, renders, curve_density, "
    "dim_coverage). ONLY sheet_verdict answers 'can a machinist cut this "
    "part from this sheet'. There is deliberately no bare 'verdict' key.")


def grade_the_sheet(svg, slug, outdir):
    """The SHEET verdict, from the instrument that grades sheets.

    Not a second opinion written here: `cecad.sheetcheck.grade_sheet` is the
    same code `ce-cad/bin/sheetcheck` runs, called on the file this run just
    wrote, so result.json and the sweep table cannot drift apart. A failure
    inside the grader is a CANNOT DETERMINE naming the failure — never an
    absent key that a reader fills in with the build verdict.
    """
    try:
        from cecad import sheetcheck                          # noqa: PLC0415
        png = os.path.join(outdir, slug + "-sheet.png")
        g = sheetcheck.grade_sheet(svg, png_path=png if os.path.exists(png)
                                   else None, slug=slug, use_kernel=True)
        return {
            "sheet_verdict": g["verdict"],
            "sheet_verdict_why": g["checks"].get("dim_coverage", {}).get(
                "why", "")[:200],
            "sheet_rules": g.get("rules"),
            "sheet_sections": g.get("sections"),
            "sheet_measurements": {
                "line_ratio": g.get("line_ratio"),
                "occupancy_pct": g.get("occupancy_pct"),
                "largest_empty_rect_pct": (g.get("largest_empty_rect") or {})
                    .get("pct_of_frame"),
                "font_min_mm": g.get("font_min_mm"),
                "iso_count": g.get("iso_count"),
                "shaded_render_count": g.get("shaded_render_count"),
                "colour_and_shadow_render_count": g.get(
                    "colour_and_shadow_render_count"),
                "density_cells_over": (g.get("line_density") or {})
                    .get("over_cells"),
                "features_enumerated": g.get("features_enumerated"),
                "features_dimensioned": g.get("features_dimensioned"),
                "dim_coverage_pct": g.get("dim_coverage_pct"),
            },
            "sheet_failing_rules": [k for k, v in (g.get("rules") or {}).items()
                                    if v != "PASS"],
        }
    except Exception as e:                                    # noqa: BLE001
        return {"sheet_verdict": "CANNOT DETERMINE",
                "sheet_verdict_why":
                    "cecad.sheetcheck.grade_sheet raised %s: %s; what settles "
                    "it: ce-cad/bin/sheetcheck %s"
                    % (type(e).__name__, e, outdir),
                "sheet_rules": None}


def export_stl(part, outdir, slug):
    """Write <outdir>/<slug>.stl off the LOADED SOLID and read it back.

    A print sheet that names no file is a CANNOT DETERMINE with a next step,
    and for a mesh-backed vendor part that next step is finding the vendor's
    mesh. For a part routed here because its own outline cannot be dimensioned
    (`drawing_facts._seam_forest`) there is nothing to find: the geometry is
    the solid in memory. Writing it is the next step, so it is taken.
    """
    import Mesh
    path = os.path.join(outdir, slug + ".stl")
    shape = getattr(part, "shape", None) or getattr(part, "Shape", None)
    m = Mesh.Mesh()
    m.addFacets(shape.tessellate(0.02))
    m.write(path)
    n = m.CountFacets
    if n < 4 or os.path.getsize(path) < 200:
        raise RuntimeError("STL export of %s produced %d facets / %d bytes"
                           % (slug, n, os.path.getsize(path)))
    return path


def render_reference(part, slug, outdir):
    """A shaded raster of the part, for the sheet's reference box.

    ISO2 on purpose: `reference_iso()` already draws the vector isometric from
    the standard iso camera, so a raster from the SAME angle would say nothing
    the line drawing does not. From the other rear quarter it shows the face
    the orthographic set hides.
    """
    from cecad.render import render
    from cecad.imgcheck import verify_png
    os.makedirs(outdir, exist_ok=True)
    png = os.path.join(outdir, "%s-ref.png" % slug)
    render(part, png, view="iso2", W=900, H=680, ss=2, mode="pbr",
           verbose=False)
    facts = verify_png(png, what="sheet reference render")
    return png, facts


def shoot_sheet(svg_path, out_png):
    """Photograph the FINISHED SVG in headless Chrome and read the picture
    back.

    LOOK AT EVERY ARTIFACT. A sheet that verifies is a sheet whose numbers
    agree with the solid; it is not yet a sheet anybody has seen. This renders
    the file on disk — not the Sheet object that wrote it — and
    `imgcheck.verify_png` refuses a blank, a caption-only canvas or a
    truncated capture, so the thumbnail on the index is evidence rather than
    decoration.

    1400 x 990 is the ISO aspect (all A-series sheets are 1:sqrt(2)), so the
    picture is the whole sheet at its own proportions with no letterboxing.
    """
    from cecad.vision import screenshot_url
    from cecad.imgcheck import verify_png
    # THE WHOLE SHEET, NOT THE TOP-LEFT CORNER OF IT. Chrome lays an SVG out
    # at its own physical size — an A1 sheet is 841 mm, about 3180 CSS px —
    # so a 1400 px viewport photographs a CROP and the picture looks like a
    # drawing while showing a quarter of one (measured on
    # `microduck-trunk-base`'s A1 sheet: the capture held the title line and
    # two holes). Wrapping it in one line of HTML at `width:100vw` scales the
    # whole sheet into the frame, at the sheet's own aspect.
    holder = os.path.splitext(out_png)[0] + "-view.html"
    with open(holder, "w", encoding="utf-8") as fh:
        fh.write('<!doctype html><meta charset="utf-8">'
                 '<style>html,body{margin:0;padding:0;background:#fff}'
                 'img{display:block;width:100vw;height:auto}</style>'
                 '<img src="%s">' % os.path.basename(svg_path))
    screenshot_url("file://" + os.path.abspath(holder), out_png,
                   width=1400, height=990, verify=False)
    return out_png, verify_png(out_png, what="sheet thumbnail", min_ink=0.004)


def _shoot(svg_path, stem):
    """(thumbnail path, measured facts) — or (None, the reason it failed).

    A thumbnail is a convenience and must never cost a sheet its verdict, so a
    failure here is recorded with its reason instead of raised.
    """
    try:
        png, facts = shoot_sheet(svg_path, stem + "-sheet.png")
        return png, {"size": list(facts["size"]),
                     # imgcheck calls it `ink_frac`; reading `ink` recorded
                     # 0.0 for every sheet, which is the one value a thumbnail
                     # must never be able to claim by accident.
                     "ink_frac": round(float(facts.get("ink_frac", 0.0)), 5),
                     "max_stroke": round(float(facts.get("max_stroke", 0.0)), 4),
                     "distinct_colors": facts.get("distinct_colors")}
    except Exception as e:                                    # noqa: BLE001
        return None, {"error": "%s: %s" % (type(e).__name__, e)}


def draw(slug):
    outdir = os.path.join(ROOT, "out", "drawings", slug)
    stem = os.path.join(outdir, slug)
    os.makedirs(outdir, exist_ok=True)
    t0 = time.time()
    out = {"slug": slug, "kind": None,
           "build_verdict": "CANNOT DETERMINE",
           "sheet_verdict": "CANNOT DETERMINE",
           "sheet_verdict_why": "no sheet has been graded yet",
           "verdict_note": VERDICT_NOTE,
           "generated": time.strftime("%Y-%m-%d %H:%M:%S")}

    rec = part_record(slug)
    out["origin"] = rec.get("origin")
    out["record_verdict"] = rec.get("verdict")
    out["title"] = rec.get("title")
    out["material_record"] = rec.get("material")
    out["process_record"] = rec.get("process")

    doc = FreeCAD.newDocument("draw_" + slug.replace("-", "_"))
    try:
        part = triad.load(doc, "part:" + slug)
    except Exception as e:                                    # noqa: BLE001
        out.update(build_verdict="CANNOT DETERMINE",
                   sheet_verdict="CANNOT DETERMINE",
                   sheet_verdict_why="no sheet was written, so there is "
                                     "nothing for sheetcheck to grade",
                   why="part:%s does not build: %s: %s"
                       % (slug, type(e).__name__, e),
                   traceback=traceback.format_exc()[-1200:])
        json.dump(out, open(os.path.join(outdir, "result.json"), "w"), indent=1)
        print("DRAW " + json.dumps(out), flush=True)
        return out

    shape = getattr(part, "shape", None) or getattr(part, "Shape", None)
    bb = inspect.bbox_of(part)
    out["bbox_mm"] = [round(float(v), 4) for v in bb]
    out["solids"] = len(getattr(shape, "Solids", []) or [])
    out["faces"] = len(getattr(shape, "Faces", []) or [])
    kind, why = classify(slug, part)
    out["kind"], out["kind_why"] = kind, why
    out["bought"] = bool(is_bought(slug))

    # WHAT THE BUILDER NAMES AGAINST WHAT THE SOLID CARRIES. A reader who
    # opens ce-parts/microduck-sole-left/current/cad/part.py finds "heel arc
    # R7.2, toe arc R6.9, side fillets R7.9" and finds none of the three on
    # the sheet, and the only honest reading of that gap is that the drawing
    # dropped them. It did not: `cecad.inspect.arc_radii` measures ZERO arcs
    # in the R0.2..R60 band on that solid, because its blends are a loft
    # through a measured station table and exist as sampled points, not as
    # circular edges. Both facts go in the record, and onto the sheet.
    out["design_radii_named_in_builder"] = design_radii(slug)
    try:
        out["arc_radii_on_solid"] = sorted(
            {round(float(o.r), 3) for o in inspect.arc_radii(part)})
    except Exception as e:                                    # noqa: BLE001
        out["arc_radii_on_solid"] = "CANNOT DETERMINE (%s)" % e
    radii_gap = None
    named = out["design_radii_named_in_builder"]
    onsolid = out["arc_radii_on_solid"]
    if named and isinstance(onsolid, list):
        missing = [r for r in named
                   if not any(abs(r - v) <= 0.011 for v in onsolid)]
        if missing:
            # STATED IN mm, NOT IN R NOTATION. `verify_sheet` checks every
            # `R<n.nn>` printed on a sheet against the solid's own arcs, and
            # these are exactly the radii the solid has NOT got — writing
            # them as "R7.20" would fail the sheet on the note that explains
            # why they are absent.
            # SHORT, AND ONLY WHAT IS MEASURED. The first version of this
            # note ran to 430 characters and explained the gap as "design
            # blends of a lofted surface, sampled station to station" — true
            # of microduck-sole-left, where the finding was made, and an
            # unmeasured assertion about every other part. MEASURED
            # 2026-09-03: on microduck-hip-bracket it cost the sheet its
            # verdict, running the notes column down into the title block at
            # A1 and 77.92 mm past the frame at A2, across 21 attempts. The
            # fact goes on the paper in one line; the reasoning lives in this
            # result.json and on out/drawings/INDEX.html, which is where a
            # reader who wants it is.
            radii_gap = (
                "RADII NAMED IN cad/part.py THAT ARE NOT CIRCULAR EDGES ON "
                "THIS SOLID: %s. cecad.inspect.arc_radii measures %d ARC(S) "
                "HERE AND EVERY ONE IS DIMENSIONED ABOVE. NO DIMENSION IS "
                "MISSING: A LEADER NEEDS AN EDGE. THE GEOMETRY FILE CARRIES "
                "THE SURFACE."
                % (", ".join("%.2f mm" % r for r in missing), len(onsolid)))
    out["design_radii_gap"] = radii_gap

    # HOW MANY ORTHOGRAPHIC VIEWS THE PART EARNS, and why — on the record and
    # on the paper. §A asks for a third-angle set; §A.2 orders the opposite
    # for a thin part ("a 2 mm rib seen on its end is a black band that means
    # nothing"). `cecad.autosheet.choose_views` already decides this off the
    # bounding box, and until now it decided silently, so a sheet with two
    # orthographic views looked like a sheet that had lost one. MEASURED
    # 2026-09-03: 6 of 15 sheets carried two, every one of them a plate or a
    # rod, and nothing on any of them said so.
    from cecad.autosheet import choose_views                  # noqa: PLC0415
    try:
        chosen, primary = choose_views(part)
        ex, ey, ez = [float(v) for v in bb]
        thin = min(ex, ey, ez) / max(ex, ey, ez, 1e-9)
        out["views_chosen"] = list(chosen)
        out["views_primary"] = primary
        views_note = (
            "ORTHOGRAPHIC VIEWS: %d (%s) — cecad.autosheet.choose_views ON "
            "THE %.3f x %.3f x %.3f mm BBOX, THIN/LONG %.4f. %s"
            % (len(chosen), ", ".join(chosen).upper(), ex, ey, ez, thin,
               ("A THIRD VIEW WOULD BE THIS PART EDGE-ON, WHICH A.2 ORDERS "
                "SUPPRESSED; THE SECTION AND THE ISOMETRIC CARRY IT."
                if len(chosen) < 3 else
                "THE FULL THIRD-ANGLE SET IS DRAWN.")))
        out["views_note"] = views_note
    except Exception as e:                                    # noqa: BLE001
        out["views_chosen"] = "CANNOT DETERMINE (%s: %s)" % (
            type(e).__name__, e)
        views_note = None

    if kind == "print-sheet":
        stl = mesh_geometry_of(slug)
        if stl is None:
            # NOTHING TO PRINT IS NOT AN ANSWER WHEN THE SOLID IS RIGHT HERE.
            # A part routed to a print sheet by `_seam_forest` is a
            # PARAMETRIC solid we own — there is no vendor mesh to find, and
            # the file the shop needs is one we can write. Exported from the
            # loaded shape, at a deflection stated on the sheet, so the STL
            # and the solid are the same geometry.
            stl = export_stl(part, outdir, slug)
            out["stl_exported_from"] = "the loaded solid"
        r = print_sheet(part, stem, stl=stl, size="A3",
                        source="ce-parts/%s/current/cad/part.py" % slug,
                        material=rec.get("material"),
                        why=" ".join(x for x in
                                     ["Origin: %s. %s" % (rec.get("origin"),
                                                          why), radii_gap]
                                     if x))
        ok, checks = verify_print_sheet(r, part, verbose=False)
        out["thumbnail"], out["thumbnail_facts"] = _shoot(r["svg"], stem)
        out.update({k: v for k, v in r.items() if k != "notes"})
        out["verified"] = bool(ok)
        out["checks"] = [{"name": n, "ok": o, "detail": str(d)[:200]}
                         for n, o, d in checks]
        # A PRINT SHEET WITH NOTHING TO PRINT IS NOT A WRONG SHEET. Every
        # number on it is measured off the loaded shape and reads back clean;
        # what is missing is the one thing the sheet is FOR — the file. That
        # is a CANNOT DETERMINE with a named next step, not a FAIL, and the
        # distinction is the difference between "fix the drawing" and "find
        # the mesh". Any OTHER failing check still fails the sheet.
        bad = [n for n, o, _ in checks if not o]
        if bad and bad == [_NO_FILE]:
            out["build_verdict"] = "CANNOT DETERMINE"
            out["why"] = ("the print sheet reads back clean but names no file "
                          "to print; what settles it is the GEOMETRY path in "
                          "ce-parts/%s/current/cad/part.py or an STL exported "
                          "from the loaded shape" % slug)
        else:
            out["build_verdict"] = "PASS" if ok else "FAIL"
    else:
        png, pfacts = render_reference(part, slug, outdir)
        out["reference_render"] = png
        out["reference_render_px"] = list(pfacts["size"])
        # The tolerance basis is a PROGRAMME fact, not a part fact — see
        # tools/drawing_facts.py, where every clause carries its source.
        bp = getattr(part, "blueprint", None)
        if bp is not None and getattr(bp, "meta", None) is not None:
            bp.meta["general_tolerance"] = GENERAL_TOLERANCE
        r = auto_blueprint(
            part, stem, manufacturing=True,
            source="ce-parts/%s/current/cad/part.py" % slug,
            reference_image=png,
            reference_caption="REFERENCE RENDER (ISO2) — rendered off this "
                              "solid, %d x %d px" % tuple(pfacts["size"]),
            dfm_extra=((TOLERANCE_DFM + VENDOR_DFM if out["bought"]
                        else TOLERANCE_DFM)
                       + ((radii_gap,) if radii_gap else ())
                       + ((views_note,) if views_note else ())))
        sh = r["sheet"]
        ok2 = verify_sheet(sh, r["svg"], part, verbose=False)
        out.update({
            "dxf": r["dxf"], "svg": r["svg"], "pdf": r["pdf"],
            "size": r["size"], "scale": "%d:%d" % tuple(r["scale"]),
            "views": r["views"], "details": r.get("details", []),
            "details_dropped": r.get("details_dropped", []),
            "dfm": r.get("dfm", []), "density": r.get("density"),
            "verified": bool(r["verified"]), "verify_sheet": bool(ok2),
            "attempts": len(r["attempts"]),
            "attempt_log": [{k: a.get(k) for k in
                             ("size", "scale", "section", "dim", "holes",
                              "details", "sec_rank", "verified", "reason")}
                            for a in r["attempts"]],
            "hidden_lines": r.get("hidden_lines"),
            "last_reason": r["attempts"][-1].get("reason", ""),
            "gave_up": {k: r["attempts"][-1].get(k)
                        for k in ("section", "dim", "holes", "details")},
            "warnings": list(sh.warnings),
        })
        hs = inspect.holes(part)
        out["holes"] = len(hs)
        out["hole_diameters"] = sorted({round(h.d, 3) for h in hs})
        out["counterbores"] = sum(1 for h in hs if h.kind == "counterbore")
        out["slots"] = len(inspect.slots(part))
        out["grooves"] = len(inspect.grooves(part))
        try:
            out["radii"] = sorted({round(o.r, 3)
                                   for o in inspect.arc_radii(part)})[:40]
        except Exception as e:                                # noqa: BLE001
            out["radii"] = "CANNOT DETERMINE (%s)" % e
        tw = inspect.thinnest_wall_detail(part)
        out["thinnest_wall_mm"] = tw.get("mm")
        out["thinnest_wall_where"] = tw.get("where")
        out["thinnest_wall_step_mm"] = tw.get("step_mm")
        out["thumbnail"], out["thumbnail_facts"] = _shoot(r["svg"], stem)
        out["build_verdict"] = "PASS" if (r["verified"] and ok2) else "FAIL"

    # THE SHEET VERDICT, on the file just written, from sheetcheck itself.
    svg_written = out.get("svg")
    if svg_written and os.path.exists(svg_written):
        out.update(grade_the_sheet(svg_written, slug, outdir))
    else:
        out["sheet_verdict"] = "CANNOT DETERMINE"
        out["sheet_verdict_why"] = (
            "no SVG on disk for this part, so no sheet could be graded")

    out["seconds"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(outdir, "result.json"), "w"), indent=1)
    print("DRAW " + json.dumps(out), flush=True)
    return out


def main():
    """Every slug on the command line, in ONE kernel.

    One FreeCAD boot instead of N (0.45 s each), and — the reason that matters
    — `cecad.measured`'s content-addressed caches and the render cache stay
    warm across parts, so a part redrawn at three paper sizes measures its
    thinnest wall once.
    """
    slugs = [a for a in sys.argv[1:] if not a.startswith("-")]
    done = []
    for slug in slugs:
        try:
            done.append(draw(slug))
        except Exception as e:                                # noqa: BLE001
            print("DRAW-CRASH %s %s: %s\n%s"
                  % (slug, type(e).__name__, e,
                     traceback.format_exc()[-1500:]), flush=True)
        for d in list(FreeCAD.listDocuments()):
            try:
                FreeCAD.closeDocument(d)
            except Exception:                                 # noqa: BLE001
                pass
    nb = sum(1 for d in done if d and d.get("build_verdict") == "PASS")
    ns = sum(1 for d in done if d and d.get("sheet_verdict") == "PASS")
    print("DRAW-SUMMARY build %d/%d PASS · SHEET %d/%d PASS (sheetcheck, "
          "A2+A3+A4) over %d requested"
          % (nb, len(done), ns, len(done), len(slugs)), flush=True)


main()
