# connection:press-fit-bearing-22x16x4 — the joint every major axis idles on

The 22 mm OD × 16 mm bore × 4 mm wide ball bearing seated by interference:
inner ring on a Ø16 printed boss, outer ring in a Ø22 printed bore. Eleven
placements — the hip-yaw, hip-roll, hip-pitch, head-yaw and head-roll axes
all turn on this ring opposite their XL330 horns. Shaped after
`~/dev/ce-workshop/ce-connections/press-fit-608` and this shelf's
`press-fit-bearing-15x10x3` (the same joint one size down).

## The ring, measured

`cecad.meshfeatures.cylinders` + bbox on
`reference/pollen-microduck-rl/assets/seeed_bearing__configuration__22x16x4.stl`
(2026-09-02, frozen in `evidence/bearing-22x16x4-geometry.json`): hole
Ø16.0, boss Ø22.0, bbox 22.0 × 22.0 × 4.0. Placed ×11
(`spec/mesh-placements.json`: trunk_base ×2, yaw2roll, hip_l ×2, upper_leg
left+right, neck_pitch, yaw_roll_motion ×2, bearing_roll). The mesh is
named only "seeed_bearing"; **no vendor designation exists in the reference
and none is invented** — the slug is the dimensions.

## The seats it was written against (each measured in its own part folder)

| seat | part interface | measured |
|---|---|---|
| inner ring on boss | microduck-yaw2roll `yaw_bearing_seat` | Ø16.0 × 1.95 boss, **with its own Ø19.0 × 0.5 shoulder** — dead centre of the Ø16..Ø22 abutment band |
| inner ring on boss | microduck-hip-bracket `roll_/pitch_bearing_seat` | Ø16.0 × 1.95 boss |
| inner ring on boss | microduck-yaw-roll-motion `roll_bearing_seat` | Ø16.0 × 4.0 boss with Ø12 through bore (full-width) |
| outer ring face | microduck-bearing-roll `roll_bearing_face` | back face around a Ø19.0 window on the roll axis |

## What the checks can and cannot grade

- **Nominals** — graded; every measured seat lands on Ø16.0 exactly.
- **ISO 286 classes** — graded when declared. Derived limits reproduce the
  published 16 k6 / 16 h6 / 22 k6 rows exactly; the published IT7 at 10–18
  (18 µm) drifts 1 µm above raw 16i (17.32) and is transcribed with the
  drift recorded (`PUBLISHED_IT7_UM`) — at 18–30 the formula's 20.93 rounds
  to the published 21 on its own.
- **Printed seats** — FDM PLA has no ISO class. State `measured_d_mm` and
  the fit check grades the real gap.
- **Partial engagement** — the 1.95 mm bosses carry the 4 mm ring at ~49%
  so the ring spans the joint gap to the mating part (Pollen's own design).
  Reported with the ratio; neither failed nor passed until a bench press
  test exists.
- **Interference envelope** — open until calipers meet the actual ring
  (`ring_deviation_um`) and the printed seat.

## DOF

The seat is rigid; the BEARING's revolute (`rotation_about_z`) lives across
the two seats. `mate(params={"spans_bearing": True})` expresses the idler
side of an axis; a single seat returns `[]`. `driven` is false and doing
work: torque enters every one of these eleven axes through the servo horn
on the opposite face — a walk that read a driven joint off a bearing seat
would double-drive the axis.
