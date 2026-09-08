# microduck-neck-pitch-bracket

The head-pitch output bracket of the Pollen Microduck — `neck_pitch.stl` in
the MJCF. A U-bracket: two R9-ended side plates (3 thick, 18 wide) with the
XL330 horn pattern (Ø6 + 4 x Ø2.2 on Ø12) take the head-pitch servo between
them; the top plate carries a Ø18 disc + Ø16 x 1.9 boss with the same horn
pattern — the head-yaw output face that the yaw servo's horn (hung in
yaw_roll_motion) bolts to. 35 x 18 x 27.7 mm, PLA, FDM.

## What was measured, how

Everything off Pollen's published decimated mesh
`reference/pollen-microduck-rl/assets/neck_pitch.stl` (metres, 7120 tris) —
nobody has their CAD:

- `cecad.meshslice.render` sheets (out/measure/neckgrp/np_slices_{x,y,z}.png)
  + ~60 `intervals` probes, each quoted beside its number in `cad/part.py`:
  side plates |x| 14.5..17.5, width y +-9, plate top z -13, 45 deg outer
  chamfers (14.5, -13) -> (17.5, -16).
- The UNDERSIDE fell out of the probes as ONE feature: a countersink-shaped
  clearance cut about the pitch axis (0, 0, -28.793) — cylinder R13.793 for
  |x| <= 11.5 continuing as a 45 deg cone to R10.793 at |x| = 14.5. Probes at
  (x10,y0) -15.0, (x-8,y-8) -17.558, (x12.5,y8) -18.824, (x14,y8.5) -21.359,
  (x13.5,z-20) y +-7.85: every one matches that cut to < 0.02 mm.
- `cecad.meshfeatures.cylinders`: boss Ø16 x 1.9 (z -12..-10.1), disc
  Ø18 x 1.0, Ø6 centre bore to z -15.33 with a Ø7.6 tube under the plate,
  4 x Ø2.2 horn screws counterbored Ø4.4 from below (to z -17.76), and the
  side plates' Ø6 + 4 x Ø2.2 patterns — all residual 0.000.

Graded by `ce-cad/bin/cad-refcheck` against that mesh: **PASS** — p95
0.007 mm both ways, bbox delta 0.00, volume ratio 1.0000, 21/21 features
matched, round 1 after one build fix (negative cylinder heights for the
disc/boss stack made makeCylinder return a null shape; heights flipped)
(`out/refcheck/microduck-neck-pitch-bracket/r1/`, ledger evidence
`evidence/refcheck/2026-09-01T19-38-41Z/`).

## Still CANNOT DETERMINE

- Which side plate takes the pitch servo's HORN and which its idler — the
  part is x-symmetric; the neck assembly will fix it.
- Whether Pollen's Ø2.2 side holes are tapped by the horn screws or clear
  them — needs the physical part or the XL330 accessory drawing.
