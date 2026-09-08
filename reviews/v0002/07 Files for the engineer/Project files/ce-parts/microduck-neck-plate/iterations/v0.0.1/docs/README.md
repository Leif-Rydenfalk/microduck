# microduck-neck-plate

One of the two neck plates of the Pollen Microduck — `neck.stl` in the MJCF,
placed TWICE in the `neck` body (pos (22, 50, 28) and (22, 50, 3) mm, same
quat): the two parallel 2 mm plates that strap the neck-pitch XL330 (in the
trunk) to the head-pitch XL330 (at the top of the 50 mm neck). 2 x 20 x 11 mm,
R2 corners, 4 x Ø2.3 M2 clearance holes. PLA, FDM.

## What was measured, how

Everything off Pollen's published decimated mesh
`reference/pollen-microduck-rl/assets/neck.stl` (metres, 1468 tris) — nobody
has their CAD:

- `cecad.meshslice.intervals`: thickness (x 0..2 at (y -22, z 75)), outline
  (y -32..-12, z 69.5..80.5), corner radius R2.0 (y-extent lost 1.381 mm at
  0.1 mm above the face, 0.679 at 0.5 — both fit R2.0), hole centres
  (z-scans at y -30/-14: gaps 71.35..73.65 and 76.35..78.65).
- `cecad.meshfeatures.cylinders`: 4 x Ø2.3 through holes at
  (y -30/-14, z 72.5/77.5), residual 0.000, 355 deg coverage.

Graded by `ce-cad/bin/cad-refcheck` against that mesh: **PASS** — p95
0.001 mm both ways, bbox delta 0.00, 5/5 features matched, round 1
(`out/refcheck/microduck-neck-plate/r1/`, ledger evidence
`evidence/refcheck/2026-09-01T19-35-29Z/`).

## Interfaces

The hole pairs are 16 mm apart — exactly the gap between two 34 mm XL330
bodies whose axes are 50 mm apart — so each pair takes one servo's M2 case
screws (`connection:threaded-m2`, being written in parallel on this shelf).

## Still CANNOT DETERMINE

- Which plate face (x = 0 or x = 2) lies against the servo cases, and which
  hole pair belongs to which servo — the part is symmetric and the mesh
  cannot say; the neck assembly will fix both.
- Screw length and whether the XL330 case holes are self-tapping or through —
  needs the XL330-M288-T drawing (part:xl330-m288-t on this shelf).
