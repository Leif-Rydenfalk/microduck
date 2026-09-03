# MANUFACTURING FILE REQUIREMENTS — the standard the drawings and schematics must meet

*Leif's review of the first generated files, 2026-09-02, verbatim:*

> we need a lot better files for manufacturing this. More detail in blueprints.
> Currently lots of detail is missing. And you want many angles and reference
> images in the blueprint and it needs to be properly scaled with lots more
> information and dimensions for all of the details.
> Too much unusable detail and textures like what are the random lines and
> stuff it should be clean with only the details we want to manufacture and
> those should have dimensions. What are the dimensions of the radius and stuff?
> Proper schematics.
> Block diagram. Simple how everything is supposed to flow
> Then you turn it into a schematic with everything single components and every
> single pin output and where it goes to what.
> Then you need a layout file - how things are physically connected to each other.

## A · Mechanical drawings — what a sheet must have

Diagnosed against `out/drawings/microduck-shin/microduck-shin.svg` (the first
attempt): the primary view is clean and hole-tabled, but the thin side and
section views carry **edge-on rib / hidden-line "texture" — the random lines**,
and radii and most feature dimensions are absent.

**REMOVE (the "unusable detail / textures"):**
1. Hidden lines that are not a manufacturing feature — no dashed forest behind
   a face. Show hidden detail only where a section cannot reach it, and only
   the feature edges, never the tessellation.
2. Edge-on rib/thread hatching in a thin view — a 2 mm rib seen on its end is a
   black band that means nothing. Suppress it or replace that view with a
   section or a detail.
3. Any facet / mesh artefact. Drawings come from the parametric solid; a
   vendor mesh part gets **no** drawing (it has no manufacturable dimensions).

**ADD (the "detail that is missing"):**
4. **A dimensioned isometric reference view** on every sheet (small, top-right)
   so the shop sees the part in 3D.
5. **Every radius and fillet dimensioned** — `R2`, `R0.4`, `R1.2` etc. with a
   leader to each. This is the specific gap Leif named.
6. **Dimensions for all details**, not only holes: rib thickness and pitch,
   wall thickness, boss height, slot width/length, chamfers, the outline
   envelope, feature-to-feature and feature-to-datum distances, angles.
7. **More views / more angles** when one orthographic set cannot show a
   feature — additional projected views, and **detail callout views** (e.g.
   the latch, a boss cluster, the flange holes) at a **larger scale** (2:1,
   4:1, 10:1) with `DETAIL A / SCALE 4:1`.
8. **Proper scale** — a dense/large part goes on A2 (or splits to sheet 2)
   rather than shrinking to an unreadable 1:2 on A3. Each view states its own
   scale when it differs from the sheet.
9. Print/DFM note block: orientation, thinnest wall, that tapped holes print
   undersize, filament. (`docs/DFM.md`.)

**KEEP:** the measured-off-the-solid discipline (every number read back with
`verify_sheet`), the hole table, the title block, third-angle projection.

## B · Electronics — three files, in this order

Not one mixed diagram. Three deliverables, each turning the previous into more
detail:

1. **BLOCK DIAGRAM** — `electronics/1-block-diagram.*` — simple, "how everything
   is supposed to flow": the functional blocks (compute, power, servo bus,
   sensors, audio, comms) and the buses between them. One page, readable at a
   glance. No pins.
2. **SCHEMATIC** — `electronics/2-schematic.*` — every single component and
   **every single pin**, with each pin's net and where it goes to what. Drawn
   per board (Radxa header, RPI Robot HAT, imu_to_dxl, banana PCB) and the
   servo-bus harness. Pins that are unknown are shown as unknown, never guessed.
3. **LAYOUT** — `electronics/3-layout.*` — how things are **physically**
   connected to each other: the boards and devices in their real positions
   (from `spec/mesh-placements.json`), the connectors between them, cable runs
   and lengths (from `wiring/CABLES.md`). This is the physical-connection map,
   not the logical schematic.

`wiring/designs/microduck/wiring.svg` is a graphic input, not the deliverable —
the layout file supersedes it.

## Acceptance
Each drawing: `verify_sheet` PASS **and** a human read-back (Read the SVG) that
confirms it is clean, fully dimensioned incl. radii, and buildable from the
sheet alone. Each EE file: every net traceable end to end; unknowns named.
Status tracked in `STATUS.md`.

## A2 · THE SHEET LAYOUT STANDARD — Leif's second review, 2026-09-03, verbatim

> the layout in the blueprint is fucked and not usable. why isnt the iso images
> as large as possible and why is the text so small and not enough angles of iso
> image is shown and rednerings and there is so much empty white space like use
> all available space proeprly

> there is still wierd texture in rotations also remove those.

> its impossible to know if its detail you should cnc or what it is

MEASURED on `out/drawings/microduck-foot-left/microduck-foot-left-sheet.png`
(A2, 594 × 420 mm) and on every sheet's SVG, 2026-09-03:

| defect | measurement | source |
|---|---|---|
| iso view is a stamp | 58.0000 × 43.8222 mm on an 841 × 594 mm sheet = **0.51 % of sheet area** | `<image>` element, `out/drawings/microduck-ankle-left/microduck-ankle-left.svg` |
| one iso angle only | `imgs=1` on every parametric sheet | SVG image count, all 26 sheets |
| text unreadable | font sizes **1.7000–6.0000 mm**; the notes block is 1.7 mm on A2 | `font-size` attributes, all sheets |
| tessellation texture | **9543 `<line>` elements** on foot-left, 9721 on foot-right, 5781 upper-leg-left | SVG line count |
| empty space | the left half of the foot-left sheet carries no view at all | the rendered PNG, read back |

### The rules that follow (acceptance, never loosened)

1. **NO TESSELLATION LINES.** A curved or rotated surface is drawn as its
   SILHOUETTE plus its true feature edges. Facet boundaries and tangent-
   continuous edges are SUPPRESSED. A sheet whose line count exceeds roughly
   ten times its true edge count is a FAIL, not a dense drawing. This is Leif's
   "weird texture in rotations" and his "impossible to know if its detail you
   should cnc or what it is": every line on the sheet must be a real edge a
   machinist would cut to, or it must not be there.
2. **THE ISO VIEW IS A PRINCIPAL VIEW, NOT A STAMP.** At least **four**
   isometric angles (front-left, front-right, rear-left, rear-right, plus
   top/bottom where the part warrants), each at least **15 % of sheet area**,
   dimensioned or annotated where a feature is only visible there. Shaded
   renders sit beside them at the same scale.
3. **USE THE WHOLE SHEET.** Views are packed to fill the drawing frame: the
   generator computes the largest uniform scale at which the required views fit
   the frame with the stated margins, and uses it. **Measured ink/annotation
   coverage of the frame must be ≥ 60 %**; below that the sheet is re-laid out
   at a larger scale or a smaller sheet size, and the coverage number is printed
   in the title block so it can be checked.
4. **TEXT SIZED TO THE SHEET.** Minimum **3.5 mm** for dimensions and notes on
   A2 and larger (ISO 3098 lettering), **5.0 mm** for view labels, **7.0 mm** for
   the part name. No text below the minimum anywhere on the sheet.
5. **EVERY VISIBLE FEATURE DIMENSIONED**, radii included, as §A already requires.

Acceptance is MEASURED by `ce-cad/bin/sheetcheck` (line-count ratio, coverage,
minimum font size, iso count and area) and by READING THE RENDERED PNG BACK —
a sheet nobody has looked at is not a sheet.

## A3 · RENDERED COLOUR VIEWS ARE PRIMARY — Leif, 2026-09-03, verbatim

> the lines for curved shapes in the blueprints is very ugly. use colored
> properly rendered blueprints as references with the same and more detailed
> informatio nand even more angles and more detail for the blueprints so that
> they are actually manufacturable and use all empty space no white space fill
> everything with images and redners and dimesions and information for
> manufacturers.

This AMENDS §A2. §A2 rule 1 said the fix for the tessellation hatch was to
suppress facet lines. That is still true for the orthographic views, but it is
only half the answer: **a doubly-curved organic shell (this whole robot) does
not read as a line drawing at all.** A silhouette-plus-feature-edge projection
of a shin or a head shell tells a manufacturer almost nothing about the surface
between the edges. So:

### The new rules

1. **SHADED COLOUR RENDERS ARE FIRST-CLASS SHEET CONTENT, not decoration.**
   Every sheet carries **at least six** properly rendered colour views —
   material-coloured, lit, anti-aliased, read off the SOLID through the kernel —
   at a size where a shop can see the form: **each ≥ 12 % of sheet area**, and
   the largest ≥ 20 %. They sit beside the dimensioned orthographic views and
   carry their own callouts.
2. **MANY MORE ANGLES.** At minimum: 4 isometric corners (front-left,
   front-right, rear-left, rear-right), top-down and bottom-up, plus one view
   per face that carries a manufacturable feature, plus a detail render at
   larger scale for every feature cluster (a boss group, a latch, a bearing
   seat, a cable channel). More angles is always better than more empty paper.
3. **NO LINE-ART HATCH ON A CURVED SURFACE.** Where a surface is curved, the
   shaded render carries the form and the line view carries only the silhouette,
   the true feature edges and the dimensions. If a line view of a curved region
   would be a thicket, replace that view with a shaded render plus a section.
4. **ZERO WHITE SPACE.** §A2 rule 3 set coverage ≥ 60 %; this raises it:
   **≥ 85 % of the drawing frame carries content** — a view, a render, a table,
   a dimension, a note or the title block — and the largest empty rectangle is
   **< 5 % of frame area**. Empty paper is a defect the generator must fill by
   adding another angle, another detail render, or another table, not by
   scaling one view up to fill space it does not need.
5. **EVERYTHING A MANUFACTURER NEEDS IS ON THE SHEET**, not in a linked file:
   full dimension set including every radius; hole table; section views;
   material and its source; process; tolerance basis; surface finish; print
   orientation and support strategy; the fasteners that land in this part with
   their sizes; the mating parts named by triad ref; mass and volume measured
   off the solid; and the CANNOT DETERMINE list for anything unmeasured.

### Acceptance
`ce-cad/bin/sheetcheck` gains: shaded-render count and each one's area
percentage, total frame coverage ≥ 85 %, largest empty rectangle < 5 %, and a
curved-region check that FAILS a line view whose local line density exceeds a
stated threshold inside a region the solid says is curved. Plus the human
read-back: open the PNG and answer "could a shop cut this part from this sheet
alone, and does the surface form read at a glance?"
