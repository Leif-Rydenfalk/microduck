# part:microduck-upper-leg-rigidity-plate — the 1 mm thigh side plate

*Rebuilt 2026-09-01 from Pollen's published mesh. Everything here is a
measurement or a named absence; nothing is Pollen's CAD.*

## What it is

The mint (#89dad3) 1 mm plate that closes the open side of each thigh cup
(`part:microduck-upper-leg-left` / `-right`): 45 × 58 mm, with Ø19
windows on the hip-pitch and knee axes, four Ø2.2 screw holes, and three
lightening windows. The MJCF places it once per thigh in the thigh's own
frame (pos (0, 0, −42.5), quat (0.5, −0.5, −0.5, −0.5) in
`upper_leg_left`; mirrored in `upper_leg_right`), so this folder uses the
SAME frame as the left housing: x 42.5..43.5 is the plate, the housing's
cup runs from 42.5 to 70.5 behind it.

How it nests (measured, both parts in one frame): the plate's R12 bend
about (y 0, z 35.06) sits inside the housing's R12.5 inner bend about
(y 0, z 35.07); its left edge (y −12.0 at z 35) sits 0.44 inside the wall's
inner face (−12.44 at x 43); its four Ø2.2 holes are at the same (y, z)
as the housing's four Ø1.6 locating pins, 21 mm away through the servos.

## What was measured, and how

| feature | value | how |
|---|---|---|
| thickness | 1.0 (x 42.5..43.5) | `meshslice.intervals` along x at five (y,z): (42.5, 43.5) each |
| outline | R11.0 arcs about A0 (0,0) and A1 (22,35.777); left edge (−11,0)→(−12,35.06); R12 bend about (0,35.06); top z = 47.06 − 0.0127 y; right edge y = 10 from z 4.58 to 19; concave web into A1's arc | `meshslice.segments` at x 43 chained into loops; radii checked vertex by vertex (R12: (−8.62,43.41) and (−4.86,46.03) both 12.00) |
| windows | Ø19.0 at A0, A1 | `meshfeatures` (Ø19.0), y-ray at z 0 ends at ±9.5 |
| screw holes | 4 × Ø2.2 at (−0.5,43.777), (−0.5,27.777), (±8,22.5) | `meshfeatures`; loop bboxes 2.2 wide |
| W1 | rounded rect y −9.5..−4.5, z 25.78..38.78, r 1.2 | loop bbox + corner vertices |
| W2 | y ±8.5, z 8..19.5 (r 1.5), bottom = R11.5 arc about A0 | loop: z 11.46 at y 0 |
| W3 | quad (2.53,44.28)-(13.5,44.28)-(13.5,27.28)-(9.33,27.28) minus the R11.5 disc about A1 | loop: y 10.5 at z 35.78; left edge through (3.33,42.28),(8.95,28.22) |

Picture: `out/measure/plate_slices_x.png` (the x = 43 cut on a 1 mm grid).

## Grade

`cad-refcheck` history, `out/refcheck/microduck-upper-leg-rigidity-plate/`:
r1 PASS 0.26/0.28 mm but bbox +0.50 y / +0.72 z — the R11.5 web discs
added back around the axes stood outside the R11 outline; r2 FAIL
5.5 mm — the A1 arc walked counter-clockwise, the outline
self-intersected and the prism lost everything past y 22 (the r1 discs
had hidden it); r3: see `component.json` `why` for the PASS line.

## CANNOT DETERMINE (what would settle it)

- **Window corner radii.** W3's corners are ~R1.3–1.5 in the loop; ours
  are sharp (≤ 0.5 mm over ~1 mm² each). A denser export settles it.
- **Screw length and what the screws thread into.** Ø2.2 is M2
  clearance; the only candidate 26 mm behind is the XL330's front-face
  holes, which the servo's drawing or a unit in hand would confirm.
- **Material.** MJCF colour mint like the soles, which SPEC.md §6 reads
  as PLA for rigid parts; not published.
