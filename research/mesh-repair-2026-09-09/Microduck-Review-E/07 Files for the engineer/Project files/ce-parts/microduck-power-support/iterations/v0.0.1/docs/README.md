# microduck-power-support — the battery cradle half

**What it is.** Pollen's `power_support` mesh: a 2 mm PLA plate (y 25..27),
42.8 mm wide over the battery and 54.5 wide at its head, that the NP-F550
lies on. On the battery face: two 2 mm rails at x ±19.4..21.4 (8 mm tall,
R2 rounded ends) with 1.5 mm inward lips at y 31.3..32.8; eight 1.47 mm
ribs on a 4.07 mm pitch, 2 mm tall; two R1.9 stadium bosses per PCB with
4 x Ø1.6 M2 tapping holes each; a 10 mm wide, 1.06 mm thick latch tongue
cut free by 0.47 mm slits, with five R0.4 grip ridges and a ramped hook
(1.4:1) rising to y 31.3; across the head a 2 mm shelf at z 49..51 with two
U-notches (2.9 wide, R1.45 bottom at y 30.2, x ±16.9), two 2 x 8 posts at
x ±12 and two Ø3.9 screw pins (Ø1.55 tapped) at (±25, 53.6) on legs and
webs. Through the plate: an 8 x 5 window, two 2 x 7 slots per side and the
same 12 mm notch (centre x = -4) the banana_pcb_locker has. On the far
side: two 1.9 mm flanges (z 14.3..16.3 and 40.7..42.7) with Ø2.5 holes at
(±9.5, y 20.5) between 1 mm gusset cheeks; the lower one bolts up to the
trunk_base's Ø2.3 holes at the same (x, y) in the shared frame.

**Verdict: PASS** — `ce-cad/bin/cad-refcheck part:microduck-power-support
--ref reference/pollen-microduck-rl/assets/power_support.stl`:

| round | p95 ref->ours | p95 ours->ref | max | bbox delta | features |
|---|---|---|---|---|---|
| r1 | 0.211 mm | 0.241 mm | 0.72 / 2.44 | [-0.034, 0, -0.36] | 14/14 |
| r2 | 0.209 mm | 0.226 mm | 0.72 / 1.00 | [-0.034, 0, -0.36] | 14/14 |

r1's 2.44 mm max was 94/30000 samples on the x = ±2 ribs bridging the
window (the window was cut before the ribs were added); r2 cuts it last.
Reports and overlays: `evidence/refcheck/<stamp>/` (two ledger rows) and
`out/refcheck/microduck-power-support/r1`, `r2`.

## "Placed x2" is one part

`reference/pollen-microduck-simulator/assembled/measured.json` says
`"placed": 2` and SPEC.md 4.1 lists it x2, but `robot_walk.xml` lines
98-99 are one `visual` geom and one `self_collision_only` geom of the same
mesh at the SAME pos (0.004, 0, -0.0175215) and quat (0.707, 0, 0, 0.707):
a collision copy, not a second cradle half. `qty_per_robot: 1`. There is no
mirrored mesh; the part is symmetric about x = 0 except the notch (centre
x = -4).

## How it was measured (2026-09-01)

Everything in `cad/part.py` carries the probe it came from. The tools:

- `cad-mjcf sections --at L1,L2 --image DIR` — gridded pictures of a cut
  (added to cecad for this group): `out/measure/ps/section_{x,y,z}_*.png`,
  17 cuts. The y = 26/28/30/32/34 cuts show the plate, the ribs + bosses,
  the rails, the lips and the shelf in turn; z = 42 / 13 show the flanges.
- `cad-mjcf probe --axis A --at L --along B --line V` — material intervals
  along one line (added too): ~200 lines, e.g. rib pitch 4.072, rib 1.466
  wide at y 28, boss outer x 12.474 at z 9.85, rail ends z -16.713..26.813
  at y 30, hook y 31.309 at z -22, tongue 1.059 thick at z -15.
- `cecad.meshfeatures.cylinders`: 8 x Ø1.6 (axis y, length 4), 4 x Ø2.5
  (axis z, length 1.887), 2 bosses Ø3.875 (axis y, length 7.85).

## CANNOT DETERMINE

- The rail and rib drafts (rails 0.16 mm over 10 mm, ribs 0.03 mm over 2
  mm, flanges 0.035 mm) — measured, not modelled; inside the tolerance.
- The screw-pin bore depth: seen at z 53.6/54.0 from y 28 to 32; modelled
  y 27..34.8. A blind end above y 27 would not show in the decimated mesh.
- The notch's top-left round: R2 fits x -10.36 @ z 56 but under-reaches
  -11.35 @ z 56.5; the decimated edge may be an ellipse or a chamfer+round.
- The tongue tip chamfer (y 25.08..25.70 at z -26.4) — not modelled.
- Volume ratio 1.03: ours is slightly fuller (the drafts above, the R0.4
  ridges as full cylinders).
- What the trunk screws thread into and what the upper flange mates.
