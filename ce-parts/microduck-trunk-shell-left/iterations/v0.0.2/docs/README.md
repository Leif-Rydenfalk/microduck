# part:microduck-trunk-shell-left — the left half of the Microduck's egg trunk

**What it is.** The left half of the Microduck's trunk shell — Pollen's MJCF
mesh `left_shell` (body `trunk_base`, pos (4, 0, −17.579) mm, quat
(0.7071, 0, 0, 0.7071)), 33.7 × 80.9 × 41.7 mm, a printed colourway part.
A drafted, filleted half-egg, open at the bottom and toward the robot's
midplane: outboard wall + top wall + a full-width front skirt + a back wall
spanning only the outboard x 20..31.8 — all 2.2 mm — plus a top-wall tab
(y 24.9..39.9) and the back-top corner block carried inboard to the
midplane, where an M2 cross screw and a 1.0 mm half-lap close the two
halves against each other.

**How it was measured** (all 2026-09-02, off
`reference/pollen-microduck-rl/assets/left_shell.stl`, metres → mm):

- `cecad.meshslice` plane cuts: convex outlines of the skin in every plane
  x = const (`cad/measure.py` → `cad/measured.json`), material intervals as
  the caliper for wall thickness (2.2 mm on all four walls), the bottom
  edges (front skirt z = 17.84 + 0.043x; outboard 19.75; foot 17.23 + 0.04x),
  the lap strip (inner 1.0 mm of the walls, x −1.95..0.05), the snap hook,
  the foot, and the vertical boss.
- `cecad.meshfeatures.cylinders`: every hole and boss — the 4 × Ø2.2 on the
  Ø12 PCD of the neck-horn disc, the Ø2.2 pilots of both screw bosses, the
  relief-pocket arcs at x = 15.1.
- The skin itself is LOFTED through the measured outlines (`Part.loft`,
  ruled, 120-point sections): a drafted egg has no revolve profile, and the
  draft is linear — verified by extrapolating the x = 21/24 sections and
  landing on the measured front wall at x = 0.05 (17.85 predicted vs
  17.84 measured) and the tab top at x = 0.5 (59.37 vs 59.35).

**Left vs right.** The two meshes are true mirrors to 0.01 mm on every
measured outline EXCEPT: the left carries the 1.0 mm lap strip
(x −1.95..0.05) and the Ø2.2 cross-screw clearance + Ø3.5→4.4 drafted
driver bore (boss OD 6.1→8.0); the right ends at the midplane (x = 0) and
carries the Ø1.6 tapped pilot (x 0.3..5.0) + Ø3.0→4.0 bore (boss OD
6.0→7.4). One `part.py` builds both (SIDE constant), the right mirrored
about yz into its own mesh frame.

**The other mesh names.** The rl asset set also ships `trunk_shell_left` /
`trunk_shell_right`. Measured against `left_shell`: p95 6.13/3.86 mm, bbox
delta up to 6.0 mm, volume ratio 0.86, different fastening (four vertical
top bosses, cutouts in the walls) — a DIFFERENT, unplaced revision of this
part, not the one the MJCF places. Graded against `left_shell`.

**Verdict.** See `component.json` and `evidence/refcheck/` — the
`cad-refcheck` report against `left_shell.stl` is the proof of shape.

**CANNOT DETERMINE, written down:**
- What the `base_ledge` foot rests on inside the trunk (needs the
  assembled-MJCF clearance check; the trunk_base plate sits 23 mm below
  the vertical boss's pilot).
- The exact fillet radii where the foot and the vertical boss blend into
  the walls — the 1 mm decimation hides them; modelled as sharp.
- The purpose of the 0.7 mm slit beside the cross-screw boss (left) /
  2.4 mm slot (right); not modelled (≤ 3 mm² per section).
- Print orientation and colourway assignment (Pollen ships four
  colourways; material set to PLA per SPEC).
