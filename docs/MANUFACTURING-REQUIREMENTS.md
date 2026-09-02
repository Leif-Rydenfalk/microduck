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
