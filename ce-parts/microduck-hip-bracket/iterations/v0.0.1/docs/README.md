# microduck-hip-bracket

The hip-roll output bracket of the Pollen Microduck — `hip_l.stl` in the MJCF,
placed twice (bodies `hip_l` and `hip_l_2`, same pos/quat; the mesh is
z-symmetric so left and right are the SAME part, no mirror). An L-bracket:
the hip-roll XL330's horn bolts to one face, the hip-pitch XL330's horn to
the other at 90 deg, with a Ø16 x 1.95 boss on each face seating a 22x16x4
bearing. 32.45 x 34.5 x 19 mm, PLA, FDM.

## What was measured, how

Everything off Pollen's published decimated mesh
`reference/pollen-microduck-rl/assets/hip_l.stl` (metres, ~21k tris) —
nobody has their CAD:

- `cad-mjcf sections` + the 0.5 mm plane rasters in `out/hip-bracket/`
  (sec_x/y/z.txt, sections.py): plate faces (y -21.5/-19.0/-18.5/-16.55,
  x 34/38/38.5/40.45), widths (19), rib flanks (z ±5), and least-squares
  circle fits for every arc (R9.5 ends, inner R6 at (28,-13), outer R8 at
  (30,-13.5), rib corner R5 at (33,-20), rib end R5 about (17.5,0); fit
  residuals 0.003 mm).
- `cecad.meshfeatures.cylinders`: both Ø16 x 1.95 bosses, Ø6 recesses,
  8 x Ø2.4 horn screw holes on Ø12 bolt circles, Ø4.84 counterbores, and
  the Ø5.22 x ~0.5 counterbore mouth steps on the pitch face.
- Fillet radii (R2 rib roots, R1 rib top rounds, 0.75 plate edge rounds)
  fitted to raster profile points quoted in `cad/part.py`.

Graded by `ce-cad/bin/cad-refcheck` against that mesh:
**PASS** — p95 0.162 mm ref->ours / 0.242 mm ours->ref, median 0.001 mm,
bbox delta 0.00 mm, 21/21 reference holes/bosses matched
(`out/refcheck/microduck-hip-bracket/r2/`, evidence ledger
`evidence/refcheck/2026-09-01T18-58-41Z/`).

Round 1 failed at p95 15.35 mm: a spurious (v,u) swap put the pitch plate
at z 13.5 disjoint from the body, and makeFillet on that 2-solid shape
returned a corrupt solid that later booleans silently evaporated. part.py
now guards every fillet (snapshot; accept only isValid + bbox drift
< 0.3 mm + |dV| < 200 mm3). The grading run also hit and fixed a
cad-refcheck defect: feature perp-distance went complex when a centre sat
exactly on the axis line (max(...,0) clamp, ce-cad/bin/cad-refcheck).

## Still CANNOT DETERMINE

- The plate edge rounds are modelled sharp except the rib R1/R2 blends;
  the reference's 0.75 mm edge rounds contribute < 0.31 mm deviation,
  inside the 1.0 mm decimation floor, so their exact radii are unproven.
- The Ø5.22 counterbore mouth steps: the decimated mesh shows them 0.21 to
  0.58 mm deep on three of four pitch counterbores (the fourth is hidden by
  decimation); modelled as a 0.55 mm cylindrical step on all four. Whether
  Pollen's CAD has a chamfer or a step there cannot be told from the mesh.
- Whether the roll-side counterbores also carry a mouth flare (the mesh
  hints 0.17 mm at y -25 but meshfeatures finds no separate feature).
- True as-designed hole fits (Ø2.4 vs M2 clearance 2.2/2.4; Ø4.84 vs Ø4.8):
  the mesh is decimated; the printed part should follow the connection
  folders' fits, not these raw readings.

## Interfaces

`cad/interfaces.json`: roll_horn / pitch_horn (connection:spline-xl330-horn
+ connection:threaded-m2) and roll_bearing_seat / pitch_bearing_seat
(connection:press-fit-bearing-22x16x4).
