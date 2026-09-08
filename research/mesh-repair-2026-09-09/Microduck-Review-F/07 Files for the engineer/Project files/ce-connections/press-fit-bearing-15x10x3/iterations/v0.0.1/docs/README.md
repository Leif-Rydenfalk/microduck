# connection:press-fit-bearing-15x10x3 — the ankle and jaw bearing seat

The 15 mm OD × 10 mm bore × 3 mm wide ball bearing seated by interference:
inner ring on a Ø10 printed boss, outer ring in a Ø15 printed pocket.
Shaped after `~/dev/ce-workshop/ce-connections/press-fit-608`; the ISO 286
mathematics is the same module at this joint's own sizes.

## The ring, measured

`cecad.meshfeatures.cylinders` + bbox on
`reference/pollen-microduck-rl/assets/seeed_bearing__configuration_default.stl`
(2026-09-02, frozen in `evidence/bearing-15x10x3-geometry.json`): hole
Ø10.0, boss Ø15.0, bbox 15.0 × 15.0 × 3.0. Placed ×3 on the robot
(ankle_left, ankle_right, jaw_soft — `spec/mesh-placements.json`). The mesh
is named only "seeed_bearing"; **no vendor designation exists in the
reference and none is invented** — the slug is the dimensions.

## The seats it was written against (each measured in its own part folder)

| seat | part interface | measured |
|---|---|---|
| inner ring on boss | microduck-shin `ankle` | Ø10.0 × 3.2 boss on the back face |
| outer ring in pocket | microduck-ankle-left/right `ankle_bearing` | Ø15.0 × 2.3 pocket behind a Ø14.0 window, Ø16 × 0.5 45° lead-in |

## What the checks can and cannot grade

- **Nominals** — graded; both sides of the reference pair measure at 10.0 /
  15.0 exactly.
- **ISO 286 classes** — graded WHEN the seat declares one (a machined
  seat). Limits derived from ISO 286-1's formulae reproduce the published
  10 k6 / 10 h6 / 15 k6 rows exactly. **Measured drift, recorded not
  hidden:** the published IT7 (15 µm at 6–10, 18 µm at 10–18) sits 1 µm
  above raw 16i (14.37, 17.32) — the ISO 286-2 tables are not pure formula
  output, so those two values are transcribed (`PUBLISHED_IT7_UM`) and the
  self-test checks both spellings.
- **Printed seats** — the reference design's seats are FDM PLA: **a printed
  bore has no ISO class.** State `measured_d_mm` (calipers on the printed
  part) and the fit check grades the real gap; it will not grade nominal
  against nominal and call that a fit.
- **Partial engagement** — Pollen's own ankle pocket is 2.3 mm deep for the
  3 mm ring (the proud 0.7 mm clears the shin boss). Reported as CANNOT
  DETERMINE with the ratio, neither failed (the reference design does it)
  nor passed (nobody has bench-tested the press).
- **Interference envelope** — open until someone measures the actual ring
  (`ring_deviation_um`) and the as-printed seat. No vendor sheet exists to
  fetch for an unnamed ring.

## DOF

The seat is rigid; the BEARING's revolute (`rotation_about_z`) lives across
the two seats — on this robot the ankle hinges (MJCF left_ankle/right_ankle)
and the jaw pivot. `mate(params={"spans_bearing": True})` expresses that;
a single seat returns `[]`. The press-fit-608 friction/form split is kept
verbatim.
