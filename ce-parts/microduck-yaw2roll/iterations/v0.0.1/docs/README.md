# part:microduck-yaw2roll — the hip-yaw link

*Rebuilt 2026-09-01/02 from Pollen's published mesh. Everything here is a
measurement or a named absence; nothing is Pollen's CAD.*

## What it is

The `yaw2roll` body of the Microduck MJCF: the PLA link between the hip-yaw
XL330 in the trunk and the hip-roll XL330 of the leg, 23 × 25.8 × 20.5 mm.
A 2.5 mm plate carries, on top, the Ø19/Ø16 boss that seats the trunk's
22×16×4 yaw bearing and the 4-hole XL330 horn pattern; below it, two
1.4 mm side walls with a sloped bottom edge and a front block shaped as the
servo's lug outline cradle the hip-roll XL330 (its 23 mm body sits between
this block, y 9.5, and the bearing_roll plate, y −13.5). Two ears at the
back take the two screws that hold `part:microduck-bearing-roll`.

Frame: the mesh's own — X across the leg 6..29, Y ear-backs −13.3 → front
face 12.5, Z lug tip −5 → ear tops 15.5. Yaw axis (17.5, −2, z); roll axis
(17.5, y, 0); they intersect at (17.5, −2, 0). MJCF geom pos (−17.5, −2,
12.5) quat (0, 1, 0, 0) maps mesh (x, y, z) → body (x − 17.5, −y − 2,
12.5 − z); the body origin is the hip-yaw joint origin.

**Left ↔ right.** Both legs place the same `yaw2roll.stl` with the same
rotation (the MJCF writes the quaternion as (0, 1, 0, 0) for the left and
(0, −1, 0, 0) for the right — the same rotation). The part is one print
× 2, not a mirror pair; mirroring happens in the parent body transforms.
The right-leg body is named `bearing_roll` in `kin_robot_walk.xml`.

## What was measured, and how

| feature | value | how |
|---|---|---|
| plate | z 9.5..12.0, x 6..29, y −13.3..12.5; r 2 round on the front-top edge | `meshfeatures.profile` z-rays at (12, y); top 12.48 @ y 10.25 … 10.96 @ 12.25 = r 2 about (y 10.5, z 10) |
| yaw boss | Ø19.0 × 0.5 (z 12..12.5) + Ø16.0 × 1.95 (z 12.5..14.45), centre (17.5, −2) | `meshfeatures.cylinders` |
| horn screws | 4 × Ø2.2 on r 6.0 at (±6, 0), (0, ±6); Ø4.4 c'bores from below, z 9.5..11.5 | cylinders; matches xl330.stl's 4 × Ø1.6 on r 6 |
| ears | x 6..11 and 24..29, semicircular top r 2.5 about z 13; Ø2.05 × 4 hole along y at z 12.5 | z-rays at (x, −12); x-rays at z 12.2 gave the plan-view end polyline (15 points in part.py) |
| side walls | 1.4 thick (x 6..7.4, 27.6..29); bottom edge z = 9.5 − 0.523 (y + 7) to y 7.25 | y-rays at z 5 sweeping x; z-rays at x 6.3 |
| front block | y 9.5..12.5; outline r 5 about the roll axis, 30°-from-horizontal flanks, r 5 blends into vertical sides at z 3.75 | x-rays at y 11: half-widths 1.55 @ z −4.75 … 8.7 @ −0.75, 10.07 @ 0.25, 11.5 @ 3.75; `meshslice` re-check: ref x 7.7 @ z 0, 6.32 @ z 2, 6.0 @ 3.75 both sides |
| idler stub | Ø5 × 1.8 (y 7.7..9.5), Ø2.7 through, Ø5.5 × 2.5 c'bore from the front | cylinders |
| servo screws | Ø2.4 at (9.5/25.5, z 7.5), Ø4.84 c'bore y 10.3..12.5 | cylinders; the XL330's upper Ø2.0 × 23 through-holes at (±8, 7.5) |
| symmetry about x 17.5 | walls, flanks, lug identical both sides at every probe | meshslice x-rays y −4..12, z −3..8; z-rays at x 6.7 vs 28.3 |
| the yaw bearing | 22×16×4 at the joint origin, axis +z, mesh spans 0..4 → z 12.5..16.5 here; races r 8..9 / 10..11 | spec/mesh-placements.json + meshslice on the bearing mesh |
| the roll servo | horn axis = our y; body y −13.5..9.5; through-holes at (17.5 ± 8, z 7.5 / −22.5) | mesh-placements.json transformed into this frame; cylinders on xl330.stl |

Pictures: `out/measure/yaw2roll_slices_{y,z}.png`,
`out/refcheck/yaw2roll/r{1,2}/overlay_*.png`.

## Grade

`cad-refcheck` r1 (2026-09-01): PASS at p95 0.79 / 0.27 mm but max 4.55 mm —
`overlay_left.png` showed the −x flank of the front block 4.8 mm short
(ours x 10.77 vs ref 6.0 at z 3.75): the −x blend arc in `_lug_outline`
swept 180 → 120° instead of 180 → 240°. r2 (2026-09-02, one arc fixed):
**PASS — p95 0.05 / 0.05 mm, max 1.24 / 1.30, bbox Δ (0, 0, 0), 19/19
features, volume ratio 1.0055.** Ledger: `evidence/ledger.jsonl`.

## CANNOT DETERMINE (what would settle it)

- **The idler screw.** Ø2.7 through with a Ø5.5 c'bore reads as M2.5
  close-fit or M2 loose; what it threads into on the XL330's rear is not in
  the sim (its servo mesh is a solid Ø16 × 3 boss at both ends, which
  overlaps this block by 3 mm). Pollen's BOM or the XL330 idler-set drawing
  settles it. Declared as `connection:threaded-m2` with the caveat.
- **The ear holes.** Ø2.05 × 4 blind: an M2 self-tap in printed PLA (the
  part's clearance holes are 2.2 / 2.4). A physical unit settles insert vs
  self-tap.
- **Sub-mm fillets.** The 1.24 / 1.30 mm max is at the wall-to-plate and
  ear-to-plate junctions where the decimated mesh shows fillet-sized
  facets below the 1 mm floor; 99.8 % of both surfaces is within 1 mm.
- **Wall thickness 1.4** is read off a decimated mesh at ±0.05 mm; Pollen's
  CAD would give the design value.
