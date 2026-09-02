# part:microduck-motor-support — the head chassis plate, rebuilt parametric

The frame inside the Microduck's head: a 1.7 mm base plate (z 0.4..2.1, four
Ø2.7 screw holes), perimeter walls, a servo barrel across the part (arch
shell Ø25.4 / Ø22.2 about (x 0, z 4.49) — the mouth-servo swing volume, with
a saddle over the south wall and stepped gusset clearance arches r 9.5 /
r 11.1), a rounded funnel opening westward into a stepped lens tube (axis x
at (y 0, z 7.5), bore rings Ø15/Ø17.5, outer Ø17.4/18.4/20.5), a flat roof
(z 17.5..19.2) over the east half, and an electronics shelf (z 14.5..16.2)
with two rectangular slots along the north edge.

## How it was measured

Everything off Pollen's published decimated mesh (metres, x1000) —
`reference/pollen-microduck-rl/assets/motor_support.stl`:

- `cecad.meshslice` plane cuts traced into closed loops → the outline
  literals in `cad/part.py` (base islands at z 0.8, wall paths at z 6).
- `cecad.meshslice.intervals` calipers: every z-level, band and radius in
  part.py quotes its probe, e.g. barrel r_in 11.1 from probe (0,-17) →
  (15.59, 17.19).
- `cecad.meshfeatures.cylinders`: the four Ø2.7 holes, the tube bore and
  boss.
- Graded by `cad-refcheck` (r1..r6 in out/refcheck/microduck-motor-support/):
  **PASS r6 — p95 0.363 / 0.456 mm, bbox delta 0.00, 6/6 features, 0
  unmatched.**

## Choices a reader should know

- Walls are drafted ~0.3 mm over their height in the mesh; modeled vertical
  at mid-draft positions.
- The lens-tube bore is modeled Ø17.5 about z 7.35 — between the caliper
  reading (Ø16.8 about z 7.5) and the decimated mesh's own cylinder fit
  (Ø17.84 about z 6.75, residual 0.23 mm) — so cad-refcheck's detector reads
  the same feature on both meshes. Same for the boss ring (modeled Ø20.51
  about z 7.2; detector reads Ø20.69 = the reference's own fit). In
  x -34..-30.6 the flat wall legs are replaced by the boss cylinder wall
  down to the base — one smooth surface, without which the detector merges
  the flat legs into the boss fit and reads +0.33 mm.
- The funnel walls (the flared chute from the central opening into the
  tube) lean outward with height; modeled as the measured bands with the
  crown arcs extruded full height.

## CANNOT DETERMINE

- Which y-side of the mouth barrel carries the horn vs the idler.
- Wall thicknesses the decimation hid (interior gusset fine structure is
  approximated by the two clearance arches r 9.5 / r 11.1).
- The real fastener size in the Ø2.7 base holes (M2 loose / M2.5 clearance).
- The exact mate kind of the lens tube (named `connection:press-fit-tube-15`
  as the work item).
