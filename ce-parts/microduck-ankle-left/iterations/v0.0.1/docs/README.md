# microduck-ankle-left — the left ankle bracket

The yellow U-bracket (MJCF body `ankle_left`, rgba 0.980 0.714 0.004) that
closes the ankle joint: one wall seats the 15x10x3 bearing (Ø15 x 2.3 pocket
behind a Ø14 window, Ø16 lead-in), the other bolts to the ankle XL330's horn
(Ø5 centre + 4 x Ø2.2 on a 6 mm-radius diamond, Ø4.4 counterbores through the
inclined outer face). A 2.5 mm plate joins the walls; under it hangs the
R16.3 cylindrical heel hull the foot wraps, clipped flush at the +y face.
One vertical Ø2.2/Ø4.4 counterbored screw hangs the foot; two 1.4 mm edge
notches and two roofed-slot blocks under the +y edge locate it.

## How it was measured

Everything was read off Pollen's published decimated mesh
`reference/pollen-microduck-rl/assets/ankle_left.stl` (metres, 15147 tris) on
2026-09-01:

- `cad-mjcf sections` + the plane-cut loops in `docs/sections.py` — outlines,
  wall positions, the two inclined outer faces (planar fits, residual 0.0000),
  the R9.25 top arc, the R13.5 tangent flank arc, the R16.3 hull
  (`out/measure/ankle/fits_ankle_left.txt`, `sections_ankle_left.txt`,
  `contours*_ankle_left.txt`)
- `cecad.meshfeatures.cylinders` — all 13 holes (Ø2.2 x5, Ø4.4 x5, Ø5, Ø14, Ø15)
- graded by `cad-refcheck`: **p95 0.012 / 0.011 mm, max 0.081 mm, bbox delta
  0.001 mm, 13/13 holes matched** (`out/refcheck/microduck-ankle-left/r3`,
  evidence run 2026-09-01T19-03-54Z)

## Mirrors and variants (measured, not assumed)

- `ankle_right.stl` IS this mesh mirrored about x=0: p95 0.000 mm, max
  0.0087 mm, zero bbox delta (`out/measure/ankle/mirror-test.json`). The right
  bracket is therefore this part.py with `HAND = -1`.
- `ankle_l_v1.stl` / `ankle_r_v1.stl` are an OLDER, different bracket —
  39.5 x 46.5 x 25.4 mm, 10 mm wider in y, volume 6686.8 mm³ vs 7877.8 — that
  no MJCF body references. They are true mirrors of each other (max 0.033 mm)
  but are NOT this part.

## Build history

- r1: profile bug — the -y flank arc's start angle was `th_j + pi` (5.999 rad)
  instead of the equivalent `th_j - pi` (-0.284 rad), so the arc swept 434°
  round the back of the circle: self-intersecting profile, 441-solid compound.
- r2: profile fixed, FAIL 5.89 mm — the R16.3 hull's crown (y up to
  22 + 16.3 = 38.3) poked 1.64 mm past the flat +y face the reference has.
- r3: hull clipped flush at y = 36.663 — **PASS 0.012 mm**.

## CANNOT DETERMINE

- Thread engagement: the Ø2.2 holes print as plain bores; whether Pollen taps
  them or drives self-tapping M2s is not in the mesh. Declared as
  `connection:threaded-m2`.
- What exactly the two roofed slots under the +y edge grip (foot tabs, by
  position under the heel hull) — the mating feature lives in the foot part.
- Physical bracket mass: only the whole MJCF body (30.025 g with servo and
  foot) is published.
