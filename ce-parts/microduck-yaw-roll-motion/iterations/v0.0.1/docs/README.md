# microduck-yaw-roll-motion

The head-yaw output cage of the Pollen Microduck — `yaw_roll_motion.stl` in
the MJCF. The head-yaw XL330 hangs under its top plate (Ø2.5 case screws on
the 30 x 16 pattern), horn down onto neck_pitch; the head rolls about the
mesh-y axis through its two cheek discs: Ø18 disc + Ø16 x 1.9 boss with the
XL330 horn pattern toward the roll servo (in the head's motor_support), and
a Ø16 x 4 bearing boss with Ø12 bore on the other side for the head's
22x16x4 bearing. 34 x 35.9 x 22.5 mm, PLA, FDM.

## Which reference mesh

Graded against `reference/pollen-microduck-simulator/meshes/yaw_roll_motion.stl`
(the canonical vendor file; this part is not in Pollen's original rl asset
set). MEASURED off `reference/pollen-microduck-rl/assets/yaw_roll_motion.stl`
— a denser re-export (5814 vs 1242 tris, same bbox to 0.034 mm) committed to
this repo 2026-09-02 (commit 2e0bc77), whose cylinders resolve at 355 deg
coverage where the sim mesh manages 314-350 deg.

## What was measured, how

- `cecad.meshslice.render` sheets (out/measure/neckgrp/yr_slices_{x,y,z}.png)
  + ~70 `intervals` probes quoted beside each number in `cad/part.py`: top
  plate z 16..18 with two windows, a slot, 45 deg corner chamfers and a
  1 x 1 top rim chamfer; left wall y 10..13; cheek outlines = R9 disc about
  the roll axis (0, 4.5) + a tangent web line z = -2.46 - 0.822(x + 5.72)
  (four bottom-edge probes on the line to < 0.03 mm) + a drafted right edge
  (9.015, z4.5) -> (9.443, z12).
- `cecad.meshfeatures.cylinders` on the dense mesh: boss Ø16 x 4 / bore Ø12
  (roll bearing side), boss Ø16 x 1.9 / Ø6 / 4 x Ø2.2 on Ø12 / Ø4.4 cbores
  (roll horn side), 4 x Ø2.5 case screws with Ø4.6 x 0.5 countersinks on the
  (7.5, +-8) pair — all residual 0.000.

Graded by `ce-cad/bin/cad-refcheck`: **PASS** — p95 0.38 mm ref->ours /
0.90 mm ours->ref, bbox delta [0.0, -0.01, 0.034] mm, 6/6 reference features
matched, 0 unmatched, round 1 (`out/refcheck/microduck-yaw-roll-motion/r1/`,
ledger evidence `evidence/refcheck/2026-09-01T19-39-39Z/`).

The 13 "extra in ours" features in the report are NOT inventions: every one
(4 x Ø2.2 horn screws, 3 more Ø2.5 case screws, Ø4.4 counterbores, Ø4.6
countersinks, the Ø16 horn boss) is detected in the denser re-export at the
same coordinates; the 1242-tri sim mesh is simply too coarse to fit them.
The 0.90 mm ours->ref p95 is dominated by the sim mesh's decimation of
those same small features.

## Still CANNOT DETERMINE

- The exact shape of the small transition webs where the cheeks merge into
  the top plate (probed to ~0.5 mm; the sim mesh is coarser than the
  disagreement).
- Servo screw engagement (self-tapping vs machine thread into the XL330
  case) — needs the physical part or the XL330-M288-T drawing.
