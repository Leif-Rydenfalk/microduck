# part:microduck-bearing-roll — the hip-roll bearing plate

*Rebuilt 2026-09-01 from Pollen's published mesh; identity written
2026-09-02. Everything here is a measurement or a named absence; nothing is
Pollen's CAD.*

## What it is

The `bearing_roll` mesh of the Microduck MJCF (a geom of the `yaw2roll`
body): a 23 × 40 × 1 mm PLA plate, r 2.5 corners, that closes the hip-roll
XL330 on its horn side. Four Ø2.2 holes — two into `part:microduck-yaw2roll`'s
ears at the top, two into the servo's lower through-holes at the bottom —
and two conical pegs (Ø1.8 → 1.6 × 2) into the servo's upper through-holes.
On the roll axis a Ø19 window lets the servo horn's Ø16 × 3 boss through
into the 22×16×4 bearing, whose face sits flat on the plate's back face.

Frame: the mesh's own, shared with yaw2roll.stl — X across the leg 6..29,
Y = thickness (back −14.5, front −13.5, peg tips −11.5), Z along the servo
−24.5..15.5; roll axis (17.5, y, 0). MJCF geom pos (−17.5, −2, 12.5), quat
(0, −1, 0, 0).

**Left ↔ right.** One `bearing_roll.stl`, placed once per leg with the same
rotation (quat (0, −1, 0, 0) in both bodies). One identical print × 2, not a
mirror pair; the legs are mirrored by their body transforms.

## What was measured, and how

| feature | value | how |
|---|---|---|
| plate | x 6..29, z −24.5..15.5, y −14.5..−13.5 (1.0 thick) | `cad-mjcf sections` --axis y and --axis z |
| corner radius | 2.5 | z = −23.667 → x 6.64..28.36 and z = 14.667 → same; r 2.5 predicts 0.64 exactly |
| holes | 4 × Ø2.2 along y at (8.5, 12.5), (26.5, 12.5), (9.5, −22.5), (25.5, −22.5) | `meshfeatures.cylinders`, 355° cover |
| window | Ø19.0 at (17.5, 0) — the roll axis | cylinders |
| pegs | Ø1.79 at y −13.44, Ø1.60 at y −11.56, at (9.5/25.5, 7.5) → cones 2 mm tall | sections --axis y at two levels |
| what they meet | XL330 through-holes Ø2.0 × 23 at (17.5 ± 8, z 7.5 / −22.5); yaw2roll ear holes Ø2.05 at (8.5/26.5, 12.5) | cylinders on xl330.stl + placement transformed into this frame; yaw2roll.stl |
| the bearing | 22×16×4 at (17.5, −18.5, 0), axis +y; its mesh spans 0..4 → y −18.5..−14.5, face on the plate; races r 8..9 / 10..11 | spec/mesh-placements.json + `meshslice.intervals` on the bearing mesh |
| horn and hip_l | horn boss Ø16 × 3 at y −16.5..−13.5 (through the window into the bore); hip_l boss Ø16 × 1.95 at y −18.5..−16.55 with 4 × Ø2.4 on r 6 | cylinders on xl330.stl and hip_l.stl |

Pictures: `out/refcheck/bearing-roll/r1/overlay_*.png`.

## Grade

`cad-refcheck` r1: **PASS — p95 0.002 / 0.002 mm, max 0.021 / 0.012, bbox
Δ (0, 0, 0), 5/5 features, volume ratio 0.9995.** One round. The report's
one "extra in ours" (a Ø43.6 boss) is `meshfeatures` fitting the plate's
r 2.5 rounded outline as one cylinder — the reference's decimation breaks
that outline into flats so it fits nothing there; no feature is missing on
either side. Ledger: `evidence/ledger.jsonl`.

## CANNOT DETERMINE (what would settle it)

- **Who seats the bearing's outer race radially.** This plate only touches
  it axially (window Ø19 vs outer race Ø20..22); `hip_l.stl` has no Ø22
  bore, only the Ø16 boss in the inner race. Either the outer race floats
  as a thrust washer between the plate and hip_l, or a feature below the
  mesh's decimation holds it. A physical unit settles it.
- **Screw sizes.** All four holes are Ø2.2 (M2 close clearance); the peg
  tip Ø1.6 is the M2 minor. Declared `connection:threaded-m2`; Pollen's BOM
  confirms the length (short — the pegs block the far end of the servo's
  upper holes).
- **Peg fit.** Ø1.8 → 1.6 into the servo's Ø2.0 holes as modelled; the
  printed clearance depends on the printer. ce-slice / a print settles it.
