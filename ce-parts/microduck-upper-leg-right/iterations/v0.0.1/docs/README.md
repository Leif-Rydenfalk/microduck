# part:microduck-upper-leg-right — the right thigh housing

*Rebuilt 2026-09-01. This folder is the left thigh reflected; read
`ce-parts/microduck-upper-leg-left/current/docs/README.md` for every
measurement.*

## What it is

The `upper_leg_right` body of the Microduck MJCF: the right-hand twin of
the left thigh cup. It is a different print (chirality — the single side
wall is on −y in both, so the right cannot be the left turned over) but
not a different measurement.

## The one thing measured here

Is `upper_leg_right.stl` really the mirror of `upper_leg_left.stl`, or a
separately drawn part that merely looks like one?

Measured, 2026-09-01, numpy in FreeCAD's python: negate x on the right
mesh, weld vertices (6123 unique on each), nearest-neighbour distance from
every vertex to the other set — **max 0.0000 mm, both ways**. Both files
are 12250 triangles and 612584 bytes; `cad-mjcf sections --axis z --n 20`
gives identical widths at all 20 levels; bboxes are x −70.5..−42.5 versus
42.5..70.5 with y, z equal to the third decimal.

So `cad/part.py` composes `part:microduck-upper-leg-left` through the
triad loader and reflects it in the yz plane (`Part.mirror(plane="yz",
keep=False)`), and `refs.json` records that edge. The connectors are
re-declared at (−x, y, z) with x-directions flipped.

## Grade

`cad-refcheck` r1 against `upper_leg_right.stl` itself (not the left):
**PASS** — p95 0.20 / 0.20 mm, bbox Δ (0.0, 0.001, −0.006), 6/6 features.
`out/refcheck/microduck-upper-leg-right/r1/`; ledger in `evidence/`.

## CANNOT DETERMINE

The same four items as the left (inner fillets, axle screw size, what the
bosses and pins enter on the XL330, the 4 mm rim gap near y 20). Nothing
right-specific is unknown: the mirror relation is measured exact.
