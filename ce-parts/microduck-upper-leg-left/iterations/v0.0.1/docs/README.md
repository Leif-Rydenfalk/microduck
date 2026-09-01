# part:microduck-upper-leg-left — the left thigh housing

*Rebuilt 2026-09-01 from Pollen's published mesh. Everything here is a
measurement or a named absence; nothing is Pollen's CAD.*

## What it is

The `upper_leg_left` body of the Microduck MJCF: a one-sided PLA cup,
28 × 47.7 × 61 mm, that holds the hip-pitch and knee XL330 servos side by
side with their horns toward the open face. The hip-pitch axis A0 is the
body origin; the knee axis A1 sits 22 mm across and 35.777 mm along —
**42.000 mm** away, the thigh length in SPEC.md §3. The 1 mm rigidity plate
(`part:microduck-upper-leg-rigidity-plate`, mint) closes the open face.

Frame: the mesh's own. X = depth (open face 42.5 → back face 70.5), Y =
width, Z = length. MJCF geom pos (0, 0, −42.5), quat (0.5, −0.5, −0.5, −0.5)
maps mesh (x, y, z) → body (y, z, x − 42.5).

## What was measured, and how

| feature | value | how |
|---|---|---|
| back plate | x 69.5..70.5, 1.0 thick; outline = hull of R12.2 circles about A0 and A1 | `cecad.meshslice.intervals` along x (probe A: r ≥ 3.7 → 69.5..70.5); bbox z −12.197, y 34.19 |
| outer edge | quarter-round R4.0 all round | edge inset 0.54 / 1.35 / 3.37 at x 68.5 / 69.5 / 70.45 (probe C, I) — R4 predicts exactly those |
| rim | 1.0 wall, x 66.5..69.5, inside the edge | probe C: no rim at x 66.5, rim at 66.8; wall 1.00–1.04 |
| side wall | 1.0, on −y only, drafted 3.0° about z | probe D: outer y −13.462 at x 42.6 → −12.21 at 66.5 = tan 3° |
| top flange | 1.0, drafted 3.0° in x, tilted 1.86° in y | probe C/L: z 48.534 → 47.307 over x 42.6..66; +0.0324/mm of y at x 43 and 64 |
| bend | cone about (y 0, z 35.07), R = wall distance (13.5 at x 43, 12.5 at x 60) | probe G circle fits, 4 points each within 0.05 |
| wall bottom edge, flange +y edge | S-curves, carried as measured polylines | probes F/K (z-rays along the wall) and J (z-rays per 0.25 mm of y) |
| axis bosses | Ø7.27 × (67..69.5) + Ø4.42 × (64.7..67); Ø5.37 × 2.5 c'bore from outside; Ø2.4→2.8 through | `cecad.meshfeatures.cylinders` + probe A at 25 radii |
| pin bosses ×4 | '+' hub Ø1.9, arms 0.8 × 2.9, x 66.5..69.5; Ø1.6→1.8 pin to x 64.5 | probes B/H/M; positions = the plate's Ø2.2 holes |
| left ↔ right | `upper_leg_right.stl` is the exact x-mirror | 6123 welded vertices, 0.0000 mm both ways |

Pictures: `out/measure/thigh_slices_{x,y,z}.png` (the plane cuts on a 1 mm
grid), `out/refcheck/microduck-upper-leg-left/r1/overlay_*.png`.

## Grade

`cad-refcheck` r1: **PASS** — p95 0.20 / 0.20 mm, bbox Δ (0.0, 0.001,
−0.006), 6/6 features. One round. Ledger: `evidence/ledger.jsonl`.

## CANNOT DETERMINE (what would settle it)

- **Inner fillets.** The reference's volume is 7.5 % larger than ours at
  the same skin; that is the ~R1 fillets at the rim base and the
  plate/wall junction, visible in the y = −10 / z = 20 slices as 1.2–1.5 mm
  wall widths near the corner. Modelling them needs Pollen's CAD or a
  denser export; they are below the 1 mm decimation floor.
- **Axle screw size.** The through hole reads Ø2.4 at the boss tip and
  Ø2.8 at the counterbore floor: M2 pilot, M2 clearance, or M2.5
  clearance. A physical unit or the BOM settles it.
- **What the Ø4.42 boss and the Ø1.6 pins enter on the XL330.** They sit
  on the servo's rear at the axis and at 22.5 mm × ±8 mm from it. An XL330
  on the bench, or its drawing, settles it.
- **The flange's inner face near y 19..23 at x 67.5** shows a 3.8 mm gap
  in the rim wall (probe E, x 67.5 row) that our rim closes; ≤ 0.5 mm of
  material over ~4 mm — inside tolerance, not modelled.
