# Coupled-pose collision census — 2026-09-09 (vendor servo solid, recorded trajectories, right-ankle grade)

Follows `out/fit/REST-CENSUS-2026-09-09.md`, whose every servo-related number
carried two caveats: penetration was measured against Pollen's 29 mm visual
servo mesh, and the joint-range sweep moved one hinge at a time from the zero
pose. This census removes both, and grades the right-ankle asymmetry the sweep
reported. Everything was measured on the current
`ce-assemblies/microduck/current/placements.json` (134 rows, unchanged) through
`ce-cad/bin/cad`; nothing in `placements.json`, `reviews/`, `research/` or
`out/print/` was touched. Requested by Leif 2026-09-09; lane
`ce-fleet/out/longwork/terminal-lanes/microduck-fit/`.

| stage | command | result file | exit |
|---|---|---|---|
| vendor servo solid, build + frame proof | `ce-cad/bin/cad tools/fit_vendor_servo.py build` | `out/fit/vendor-xl330-local.stl`, `vendor-servo-frame.json`, `vendor-servo-build.log` | 0 |
| rest census with the vendor solid | `ce-cad/bin/cad tools/fit_vendor_servo.py rest` | `out/fit/rest-vendor-servo.json`, `rest-vendor-servo.log` | 0 (403.6 s) |
| right ankle vs mirror of the left | `ce-cad/bin/cad tools/fit_ankle_mirror.py` | `out/fit/ankle-mirror.json`, `ankle-mirror.log` | 0 (65 s) |
| who holds each servo case | `python3 tools/fit_servo_parenting.py` (numpy only; also runs under `bin/cad`) | `out/fit/servo-parenting.json`, `servo-parenting.log` | 0 |
| sit/stand trajectory posed jointly | `ce-cad/bin/cad tools/fit_coupled.py sitstand every=4 servo=vendor` | `out/fit/coupled-sitstand-vendor.json`, `.log` | 0 (5920 s) |
| walking trajectory posed jointly | `ce-cad/bin/cad tools/fit_coupled.py walk every=8 servo=vendor` | `out/fit/coupled-walk-vendor.json`, `.log` | 0 (6779 s) |
| sit/stand with the ankle servos in the ankle bodies | `ce-cad/bin/cad tools/fit_coupled.py sitstand every=8 servo=vendor reparent=1` | `out/fit/coupled-sitstand-vendor-reparented.json` | 0 (4312 s; a first launch exited 1 on a relabel bug, fixed) |
| walking, reparented; sit/stand and walking with Pollen's mesh | `… walk every=8 servo=vendor reparent=1`, `… sitstand/walk every=8 servo=pollen` | `coupled-walk-vendor-reparented.json`, `coupled-*-pollen.json` | queued 23:19 CST; appended when done |
| corrected single-joint sweep | `ce-cad/bin/cad tools/prove_fit.py sweep` then `tools/fit_sweep_depth.py` | `out/fit/sweep.json`, `sweep-depth.json` | 0 (4862 s), 0 (65 s) |

Three verdicts throughout: a depth is a measured penetration (the deepest
vertex of one body inside the other, a lower bound on relief); **CANNOT
DETERMINE** is stated where a mesh is open; 0.3 mm is the grading floor, as in
the rest census. Units mm and degrees.

## 1 · Caveat one removed: the vendor XL330 solid in place of the visual mesh

### 1.1 What was substituted, and how the frame was proven

`ce-parts/xl330-m288-t/iterations/v0.0.1/geometry/robotis-xl-xc-330.stp`
(sha256 `e2f7b060801a…`, the ROBOTIS download audited in
`research/xl330-mechanical-source-2026-09-08/`) is a compound of 15 solids and
6 open shells. `tools/fit_vendor_servo.py build` fuses the 15 solids **one at a
time with a volume check after every step** (previous + solid − measured
common volume): FreeCAD's `multiFuse` of the same 15 solids returned 6299 mm³
for a 15864 mm³ sum and a sequential `fuse` returned 1652 mm³, so a boolean
that is not checked is not trusted here. The checked union is 15692.6 mm³ (two
disjoint solids: the 31.6 mm³ block of vendor solid 4 shares no volume with
anything; disjoint closed shells voxelise correctly, overlapping ones would
not, and that was checked pairwise). Solid 3 (the horn) needed a fuzzy fuse
(0.001) to hold its volume; the other 13 steps fused clean. The 6 open shells
(four 18.3 mm², two 54.0 mm²) carry no volume and are excluded, stated in the
JSON.

Tessellation: `MeshPart` at 0.1 mm linear / 30° angular deflection → **13314
triangles, closed, 15687.7 mm³** against 15692.6 BRep (the coarse chords on
the r 0.8 mm thread cylinders account for the 5 mm³). `Shape.tessellate(0.1)`
alone gave 142004 triangles — 13k per M2 screw — which would have made every
pose 30× slower for no gain at a 0.3 mm grading floor.

Frame: research/xl330-geometry-revision-2026-09-08 records
**local(X,Y,Z) = (vendorZ + 8, vendorX, vendorY)**, a cyclic axis permutation
(det +1, so orientation is preserved — checked: the mapped mesh has positive
volume) plus 8 mm along the horn axis. The mapping is then measured, not
trusted:

| check | vendor solid, local frame | Pollen mesh, same frame |
|---|---|---|
| bounding box | x −14.5..14.5, y −10..10, z −24.5..9.5 | identical to the 0.001 mm |
| horn disc (vendor solid 3, r 8.15, x 8.9..14.5) | normal 0.82° from +x, centre 0.15 mm off the origin axis (0.41° / 0.04 mm on the 0.1 mm linear-only tessellation) | 0.00° / 0.00 mm |
| idler disc (vendor solid 10, r 8.00, x −14.5..−10.35) | 0.00° / 0.00 mm | 0.00° / 0.00 mm |
| horn on +x, idler on −x | yes | yes |
| in the assembly: horn-face centre of the servo driving each of the 14 hinges vs that hinge's axis (`rest-vendor-servo.json` → `servo_axis_check`) | **0.087 mm off-axis, 0.0° tilt, all 14** | 0.000 mm, 0.0° |

The stage refuses to write the STL if any disc is more than 1° or 0.5 mm off,
or if the horn is not on +x. So the vendor solid sits on every hinge axis
exactly where the visual mesh sat, and the two envelopes are the same 29 × 20
× 34 mm: **the vendor body carries the same 29 mm horn+idler stack the visual
mesh does.** The rest census' reading 1 — that the 29 mm mesh "carries about 6
mm of horn/idler stack" the real part lacks — was wrong; the real part has it
too. What differs is inside the envelope: the vendor centre region is hollow
(the audit's probe finding), the horn is a Ø16.3 boss standing 5.6 mm proud
of the front cover rather than a 3 mm solid disc, and the idler carries a
Ø6.8 hub ring in a bore.

### 1.2 The rest census rerun (`out/fit/rest-vendor-servo.json`)

Same rows, same loop (`prove_fit.main_rest`), only the 15 `xl330` rows'
triangles replaced in memory. 409 AABB candidates (399 before), 181 interfering
pairs (174), 403.6 s. Of the **16 distinct structure pairs above 0.3 mm** in
the Pollen-mesh census, **15 survive above 0.3 mm and 1 clears**; nothing new
appears above 0.3 mm.

| a | b | Pollen mesh depth | Pollen overlap mm³ | vendor solid depth | vendor overlap mm³ | verdict |
|---|---|---|---|---|---|---|
| upper_leg_left | its knee servo | 4.45 | 99.1 | **1.43** | 92.3 | survives |
| upper_leg_right | its knee servo | 4.45 | 99.1 | **1.43** | 92.3 | survives |
| yaw2roll | hip-roll servo (L) | 4.33 | 405.6 | **1.36** | 401.1 | survives |
| bearing_roll/yaw2roll | hip-roll servo (R) | 4.33 | 405.6 | **1.36** | 401.1 | survives |
| leg (left shin) | ankle servo | 4.33 | 379.6 | **1.25** | 366.7 | survives |
| leg_2 (right shin) | ankle servo | 4.33 | 379.6 | **1.25** | 366.7 | survives |
| motor_support | speaker | 1.70 | 412.5 | 1.70 | 412.5 | survives (no servo in the pair) |
| top_head_shell | head-roll servo | 1.07 | 24.4 | 1.04 | 17.9 | survives |
| left_shell | hip-yaw servo (trunk) | 1.02 | 10.1 | 0.73 | 9.6 | survives |
| power_support | np_f970 battery | 0.95 | 20.6 | 0.95 | 20.6 | survives (no servo) |
| lens | noenoeil | 0.90 | 359.5 | 0.90 | 359.5 | survives (no servo) |
| bottom_head_shell | jaw servo | 0.90 | 20.2 | 0.60 | 41.3 | survives |
| yaw_roll_motion bearing | speaker | 0.78 | 6.2 | 0.78 | 6.2 | survives (no servo) |
| right_shell | hip-yaw servo (trunk) | 0.66 | 4.8 | 0.64 | 4.7 | survives |
| m12_lens_holder | Pi Zero 2 W pcb | 0.44 | 83.6 | 0.44 | 83.6 | survives (no servo) |
| np_f970 battery | left_shell | 0.33 | 5.8 | 0.33 | 5.8 | survives (no servo) |
| *second* head servo × top_head_shell (same labels as row 8, the shallower of the two) | | 0.42 | 0.2 | 0 — no crossing triangle, no vertex inside | 0 | **clears** |

Where two servo rows share a label (two servos in one body) the table shows the
deeper; the JSON has every row.

### 1.3 Where the six servo-seat survivors are (measured in each servo's own frame)

Every one of the six is entirely in the **horn-disc zone**, none on the case:

- **Shin × ankle servo** (both sides): the shin's mounting face lies at local
  x = 9.55, i.e. 1.95 mm inside the servo's front face (x = 11.5) and 4.95 mm
  inside the horn's outer face (14.5), across the whole footprint (r up to
  25.9, |y| ≤ 8.5, z −24.5..5.9). The vendor horn's hub (r ≤ 4.32, x
  11.5..14.5) stands inside the shin. The shin has no material anywhere along
  the case (polar rays from the axis at x = 0 find no shin at any angle).
- **Upper leg × knee servo** (both sides; the hip-pitch servo in the same body
  gives the identical number): the upper leg's r 3.7 hub sits in the horn's
  centre from x = 9.7 to 14.5; the vendor horn bore is r ≈ 3.5–4 with its own
  r 2.98 shaft in it, so the remaining overlap is hub-in-shaft, 1.43 mm.
- **yaw2roll × hip-roll servo** (both sides): 468 of 486 servo vertices inside
  the bracket are in the horn zone; a further 244 bracket vertices sit inside
  the case front cover (x −8.2..12, r up to 12.6, z −5..9.5) — this one also
  wraps the case top with an overlap, 1.36 mm.

Reading, under the tool's inversion (the real duck walks): the horn is in the
model where a bracket's face or hub already is. Either every horn-side seat is
modelled without its pocket, or every horn-side servo sits 1.3–1.9 mm too
deep along its own axis. The six numbers are identical left/right to the
micron, so it is one modelling convention, not six defects. The vendor solid
did not remove it; it moved it from "4.4 mm, inside a 6 mm mesh uncertainty"
to "1.3–1.4 mm against the manufacturer's geometry", which is a finding that
now stands on its own. **No bracket should change on it** until the pocket
depth of one printed seat is measured.

## 2 · Caveat two removed: the recorded trajectories posed jointly

### 2.1 Method (`tools/fit_coupled.py`)

`out/sim/sitstand_ours_traj.npz` and `out/sim/walk_ours_traj.npz` hold `qpos`
(401 × 21) recorded at 50 Hz from Pollen's `BEST_alpha_sitstand` /
`BEST_alpha_walking` policies (the files `out/motion/legs.json` reads).
Columns 7..20 are the 14 hinges. The scene each file names was compiled and
its joint names and `qpos` addresses asserted identical to the placement
MJCF `prove_fit.Model` uses (15 joints, nq 21, same order — measured, not
assumed). Every sampled frame sets all 14 hinges by name on top of `qpos0`
(root at z 0.12 m, the frame `placements.json` was composed in; a rigid
motion of the whole robot cannot change a self-collision), MuJoCo computes
the body frames, every placed row is moved with its body, and every
cross-body pair whose AABBs overlap is triangle-crossing tested; a pair that
interferes gets `cecad.meshfit.penetration` (deepest vertex of either body
inside the other). Same-body pairs have a constant relative pose and stand as
in the rest census. Two passes: pass 1 every N-th frame on every pair; pass 2
every one of the 401 frames on the pairs pass 1 graded deeper than 0.05 mm,
so a finding's worst frame is exact to the 20 ms control step. Fasteners were
not posed (110 of 212 candidates and 28 of 48.8 s per frame; the sweep and
rest census cover them). The vendor servo solid (§1) and the closed
`yaw_roll_motion` repair are substituted in memory as before.

### 2.2 Sit/stand, vendor solid — `coupled-sitstand-vendor.json` (every 4th frame, 101 samples; pass 2 on 9 pairs; 11358 pair tests; 5920 s)

Posed envelope: left knee −0.3..75.1°, right knee −79.4..0.3°, hip pitch
−44..−18° / 6.7..30.9°, ankles 3.5..45.6° / −31.2..−4.7°, head joints within
±28°. The trunk drops from 0.120 to 0.059 m (frame 94, t = 1.88 s) and sits
there until t ≈ 4.5 s.

| pair | worst depth | frame (t) | frames interfering | joint vector at the worst frame (the 14 hinges, deg) | reading |
|---|---|---|---|---|---|
| ankle bracket L × ankle servo (`leg/xl330 × ankle_left/ankle_left`) | **3.27** | 76 (1.52 s) | 401 / 401 | L hip −2.2/−4.5/−18.2, **knee 33.7, ankle 45.6**; R 24.0/−38.2/−25.1; head 20.6/17.3/4.3/1.0 | §3.4: parenting artefact; the same pair with the servo in the ankle body is clear (§2.4) |
| ankle bracket R × ankle servo | **3.20** | 235 (4.70 s) | 401 / 401 | L −7.8/−2.6/−46.1, 45.6, 8.7; R hip 11.2/2.9/5.3, **knee −65.3, ankle −32.7**; head 15.5/24.6/−6.7/−3.2 | same |
| **hip bracket L × foot L** (`hip_l/hip_l × ankle_left/foot_left`) | **2.99** | 90 (1.80 s) | 144 / 401 (t ≈ 1.7–4.5 s, the whole sit) | L hip 6.2/10.7/−28.5, **knee 74.9**, ankle 3.3; R −0.8/−11.1/27.1, **−74.3**, −4.8; head 16.2/26.2/0/3.2 | **the sweep's knee-into-foot finding survives coupled posing, deeper**: 2.10 mm at knee 75° alone → 2.99 mm with hip pitch −28.5° and ankle 3.3° |
| **hip bracket R × foot R** | **2.81** | 88 (1.76 s) | 144 / 401 | L 6.2/8.6/−29.7, 74.6, 3.5; R −1.2/−11.9/28.2, **−75.8**, −4.7; head 15.4/27.7/−1.8/1.9 | same, right; the sweep had 3.73 mm at −79.7° alone, the policy only reaches −79.4° for a few frames |
| hip bracket R × ankle bracket R | 2.52 | 87 (1.74 s) | 10 / 401 | as above, R knee −77.0 | the deepest 0.2 s of the squat only |
| hip bracket L × ankle bracket L | 1.35 | 88 (1.76 s) | 11 / 401 | as above, L knee 74.6 | same, left |
| yaw_roll_motion bearing × speaker | 0.78 | every frame | 401 / 401 | any | the rest-census pair (0.78 mm at rest); the head joints do not change it |

Below the floor: yaw_roll bearing × bottom_head_shell 0.11 mm (rest 0.10);
fourteen bearing-seat and disc-face contacts ≤ 0.008 mm in every frame
(hip-yaw/roll bearings, knee/ankle bearings, head bearings). **0 CANNOT
DETERMINE** (the closed part-29 mesh grades every head pair). Nothing else
among the 2189 cross-body structure pairs ever crosses.

`frames interfering` counts frames with any crossing; for the two ankle rows
that is every frame because the bracket is 0.4–3.3 mm into the case at every
ankle angle the policy uses (§3.2). Knee-driven pairs interfere only while
the trunk is down.

### 2.3 Walking, vendor solid — `coupled-walk-vendor.json` (every 8th frame, 51 samples; pass 2 on 5 pairs; 6227 pair tests; 6779 s)

Posed envelope: knees −11.2..22.0° / −19.8..9.5°, hip pitch −26.2..−11.6° /
11.3..27.4°, ankles 10.7..27.6° / −27.3..−12.5°, hip yaw/roll within ±8°,
head within 25°; trunk z 0.114–0.121 m (`vx` 0.25 m/s, 8 s).

| pair | worst depth | frame (t) | frames interfering | joint vector at the worst frame (deg) | reading |
|---|---|---|---|---|---|
| ankle bracket R × ankle servo | **2.97** | 54 (1.08 s) | 401 / 401 | L −7.3/2.7/−18.9, knee −14.8, ankle 8.0; R 2.7/5.1/21.5, knee −14.6, **ankle −27.6**; head 15.7/23.4/−4.2/−5.0 | §3.4 parenting artefact: depth tracks |ankle angle| (2.97 at the −27.6° extreme) |
| ankle bracket L × ankle servo | **2.97** | 64 (1.28 s) | 401 / 401 | L −4.8/−4.3/−23.7, knee 16.2, **ankle 27.6**; R 5.8/0/19.7, knee 9.5, ankle −12.5; head 14.5/24.1/2.9/0 | same, mirror |
| yaw_roll_motion bearing × speaker | 0.78 | every frame | 401 / 401 | any | the rest pair, constant |

Below the floor: the same yaw_roll bearing × bottom_head_shell 0.11 mm and
the same fourteen bearing/disc contacts (≤ 0.008 mm). **Nothing knee-driven
touches in the gait**: the hip bracket × foot pair needs knee ≥ 70.9° (sweep)
and the walk never exceeds 22°; the closest the 2189 cross-body pairs come is
no crossing at all — 19 pairs ever interfere, all listed. 0 CANNOT DETERMINE.

### 2.4 Sit/stand with the ankle servos in the ankle bodies — `coupled-sitstand-vendor-reparented.json` (every 8th frame, 51 samples; pass 2 on 10 pairs; 6809 tests; 4312 s)

`reparent=1` moves rows 22 and 64 (the two ankle servos) from `leg` /
`leg_2` to `ankle_left` / `ankle_right` in memory, world pose unchanged at
the zero pose, for the reason in §3.4. The bracket × servo pairs become
same-body (their rest result: face contact, 0 mm) and the shin × servo pairs
become the ones that move.

| pair | worst depth | frame (t) | frames interfering | joint vector (deg) | reading |
|---|---|---|---|---|---|
| hip bracket L × foot L | 2.99 | 90 (1.80 s) | 144 / 401 | as §2.2 | unchanged by the reparenting, as it must be |
| hip bracket R × foot R | 2.81 | 88 (1.76 s) | 144 / 401 | as §2.2 | unchanged |
| hip bracket R × ankle bracket R | 2.52 | 87 (1.74 s) | 10 / 401 | as §2.2 | unchanged |
| **knee servo R × ankle servo R** (`upper_leg_right/xl330 × ankle_right/xl330`) | **2.28** | 233 (4.66 s) | **3 / 401** (frames 233–235) | L −7.9/−1.6/−41.7, knee 61.7, ankle 7.3; R hip 12.6/4.8/16.2, **knee −79.7, ankle −25.2**; head 9.0/24.0/−7.6/0.3 | **new, and only under this parenting**: with the case fixed to the foot, the servo's 24.5 mm long side tilts up the shin with the ankle and meets the knee servo when the knee is past −79° with the ankle past −25°. The policy is there for 60 ms in the stand-up. The left never combines ankle > 30° with knee > 60° (0 frames), so no left twin. |
| shin L × ankle servo L | 1.25 | every frame | 401 / 401 | any | the horn-seat overlap of §1.3, constant — turning the shin about the horn axis does not change it (§3.4) |
| shin R × ankle servo R | 1.25 | every frame | 401 / 401 | any | same |
| hip bracket L × ankle bracket L | 1.35 | 88 (1.76 s) | 11 / 401 | as §2.2 | unchanged |
| yaw_roll_motion bearing × speaker | 0.78 | every frame | 401 / 401 | any | rest pair |

Also new below the floor: the right upper-leg rigidity plate touches the
reparented ankle servo at 0.05 mm in the same frames. The ankle bracket ×
ankle servo rows of §2.2 (3.27 / 3.20 mm) are gone: with the servo in the
body that holds it they cannot move relative to each other.

The walking trajectory with the same reparenting
(`coupled-walk-vendor-reparented.json`) and the two Pollen-mesh coupled runs
are queued behind this one (chain in `out/fit/_coupled_chain5.sh`); their
lines are appended below when they land. The walk cannot reach the
knee-servo × ankle-servo pose (knee within −20..22°).

## 3 · The right-ankle "asymmetry": there is none, and what the finding actually is

The sweep said `ankle_right` enters the shin servo from −0.3° while "the
mirrored left motion is clear". Three things were measured
(`tools/fit_ankle_mirror.py`, `out/fit/ankle-mirror.json`).

### 3.1 Is the right side the mirror of the left? Yes.

| right part vs y-mirror of the left, zero pose | mean nearest-vertex | Hausdorff | vertices off by > 0.3 mm |
|---|---|---|---|
| ankle_right vs ankle_left | 0.003 mm | 4.14 mm | 7 of 4953 (isolated decimation vertices on the outer face) |
| foot_right vs foot_left | 0.002 | 0.47 | 2 of 19874 |
| sole_right vs sole_left | 0.005 | 3.26 | 33 of 15842 |
| ankle bearing | 0.027 | 0.17 | 0 |
| shin (leg.stl in leg_2 vs leg) | 0.001 | 0.63 | 12 of 14748 |
| ankle servo mesh | 0.000 | 0.00 | 0 |
| **leg_2 servo placement** as a frame: R_right vs M·R_left·S (mirror world y, and the servo's own y, which the case is symmetric about) | **0.0000°, 0.0000 mm** | | |

The hinge sign was proven by posing rather than read off an axis vector:
`left_ankle = +20` with `right_ankle = −20` makes `foot_right` the mirror of
`foot_left` to 0.465 mm Hausdorff (the mesh difference above); `right_ankle =
+20` does not (21.6 mm). Same for the knee (±30 → 0.465 vs 62 mm) and hip
pitch (±30 → 0.465 vs 92 mm). **"The mirrored motion" is left +θ ↔ right −θ**,
which is also what the policies do (default stand +25.96 / −25.96; sit/stand
left +3..+46, right −33..−5).

### 3.2 The onset table, each ankle alone, both meshes

Bracket depth in the shin servo (`leg/xl330 × ankle_left/ankle_left`,
`leg_2/xl330 × ankle_right/ankle_right`):

| ankle angle | left, Pollen mesh | right, Pollen mesh | left, vendor solid | right, vendor solid |
|---|---|---|---|---|
| ±0.5° | 0.0009 | 0.0009 | 0.0000 | 0.0000 |
| ±1° | 0.054 | 0.054 | 0.037 | 0.037 |
| ±2° | 0.224 | 0.224 | 0.189 | 0.189 |
| ±5° | 0.716 | 0.716 | 0.629 | 0.629 |
| ±10° | 1.473 | 1.473 | 1.300 | 1.300 |
| ±20° | 2.493 | 2.493 | 2.386 | 2.386 |
| ±30° | 2.493 | 2.493 | 3.108 | 3.108 |

Identical left and right to four decimals, and **symmetric in ±θ**: both
ankles hit both ways from ±0.3°. At the policies' own poses (vendor solid):
stand default ±25.96° → 2.86 mm on **both** sides; sit/stand extremes 0.38 /
3.27 mm left and 3.20 / 0.59 mm right.

### 3.3 Why the sweep reported one side only

`prove_fit.py main_sweep` kept its onsets in a dict keyed by pair; it walks the
"+" side first and then the "−" side, so for any pair that hits both ways the
"−" entry silently overwrote the "+" entry. Both ankles therefore appeared as
"−" only, and because the policies drive the right ankle negative and the left
positive, that read as "right inside its envelope, left clear". It is fixed
(keyed by pair and side; the defect is documented at the fix in
`tools/prove_fit.py`) and the sweep was rerun — section 5. Every other
two-sided pair in the old `sweep.json` has the same gap (head roll and right
ankle were the only joints with entries on both sides).

### 3.4 What the collision physically is — and why it is a parenting artefact

Polar rays from the ankle axis in the servo's own frame (`fit_servo_parenting`,
and the scratch profile that led to it): the ankle bracket is a **channel that
hugs the servo case's short side** (the 9.5 mm side above the horn axis, which
points toward the foot) at **0.12–0.17 mm clearance over φ 50°–135°, at x = −8,
0 and +8**, i.e. along the case's whole length and full 20 mm width. Its
centre pin (r 2.5) sits in the idler hub bore (r 2.65) and four pads at PCD
12 rest on the idler face. The deepest penetrating vertices at −5° are the
case's top edge (servo-local z 9.5, y −9, r 13.09, x from −11.3 to +11.3)
entering that channel, 0.63 mm, exactly the geometry of a 13.1 mm corner
turning against a wall 13.26 mm away. The **shin**, by contrast, touches this
servo only on the horn disc (section 1.3) and has no material along the case.

A channel that fits the case that closely holds it. So the ankle servo's case
is fixed to the ankle bracket and the shin is what the horn turns; Pollen's
MJCF draws the servo geom under the shin body (`leg`, `leg_2`), which is where
`placements.json` (seeded from the MJCF) has it. The collision test therefore
rotates the bracket about a case that in reality rotates with it. **The
"ankle bracket into shin servo" finding is an artefact of which body the servo
geom is parented to, not a design collision.** With the servo moved to the
ankle body in memory, the pair that rotates is shin × servo, and it measures
**1.246 mm (vendor) / 4.335 mm (Pollen) at every angle from −30° to +45°** —
the constant horn-seat overlap of section 1.3, unchanged by rotation — and the
shin is clear of the bracket, the foot and the ankle bearing at every angle.

`tools/fit_servo_parenting.py` asks the same question for all 14 hinges:

| hinge | servo geom in | holds the case (< 0.5 mm over ≥ 60° of arc) | touches the discs | verdict |
|---|---|---|---|---|
| left / right ankle | leg / leg_2 | ankle_left / ankle_right (0.118 mm over 90°) | bracket (idler face, 364 verts) and shin (horn face) | **INVERTED** |
| left / right hip roll | yaw2roll / bearing_roll | yaw2roll (0.122 mm over 60°) | yaw2roll | consistent |
| head roll | jaw_soft | motor_support (0.003 mm over 88°) | yaw_roll_motion, bottom_head_shell | consistent |
| the other 9 | as MJCF | no part within 0.5 mm over 60° | knee/hip-pitch: upper_leg on the horn; head pitch: neck_pitch on both faces; hip yaw: trunk_base | CANNOT DETERMINE by this criterion |

Only the two ankles are measurably inverted; the two-bearing and shell-mounted
servos give the criterion nothing to hold. The MJCF's parenting is right for
dynamics either way (the servo's 18 g moves with the shin or with the foot);
it is wrong only for a collision model, and only at the ankle.

## 4 · What survives, in one table

| finding | where it came from | vendor solid, rest | coupled sit/stand | coupled walk | with the ankle servos parented to the ankle | verdict |
|---|---|---|---|---|---|---|
| six servo-seat overlaps (upper legs × knee servo, yaw2roll × hip-roll servo, shins × ankle servo), 4.3–4.5 mm | rest census | **1.25–1.43 mm, all in the horn-disc zone** | same-body pairs: constant | constant | shin × ankle servo 1.25 mm in every frame, unchanged by rotation | **survives**; one modelling convention (horn pocket depth or 1.3–1.9 mm servo depth), not six defects; needs one printed seat measured |
| knee-into-foot: hip bracket × foot from knee 70.9°, 2.1 / 3.7 mm at the used edge | single-joint sweep | no servo involved | **2.99 / 2.81 mm at the squat (knees ±75°, hip pitch ∓29°), for the whole 2.8 s the trunk is down** | never (knees within −20..22°) | unchanged | **survives coupled posing, deeper than the sweep said**; MuJoCo's convex-hull self-contact count (0, legs.json) does not see it because the collision geoms are hulls |
| hip bracket × ankle bracket | not in the sweep as such (79.7°) | — | 2.52 / 1.35 mm for the deepest 0.2 s | never | unchanged | new coupled finding, same squat |
| right-ankle asymmetry: bracket × ankle servo from −0.3°, right inside its envelope | single-joint sweep | onset unchanged (±0.3°, 0.63 mm at ±5°) | 3.27 / 3.20 mm, every frame, **both sides** | 2.97 / 2.97, every frame, both sides | **gone** (same-body) | **no asymmetry**: a sweep bookkeeping defect (fixed). The pair itself is a parenting artefact: the bracket holds the case (0.12 mm channel over 90°), the shin is driven off the horn. |
| knee servo × ankle servo, right | — | — | — | — | **2.28 mm for 60 ms at t = 4.66 s** (knee −79.7°, ankle −25.2°) | new; exists only if the servo case really travels with the foot, which the bracket geometry says it does |
| head: part 29 bearing × speaker 0.78; bearing × bottom shell 0.11; servo × servo / part 29 at head roll | rest census, sweep | unchanged | constant | constant | — | rest-pose seat findings; the head joints in both gaits (≤ 28°) add nothing |
| shells × trunk servos 0.66 / 1.02, shell × battery 0.33, head shells × head servos 0.90 / 1.07, one 0.42 | rest census | 0.64 / 0.73, 0.33, 0.60 / 1.04, **one clears** | same-body: constant | constant | — | rest-only; within decimated-shell uncertainty |
| screws into a body they are not driven into (#58, #59 → shells 0.71 / 0.58; 6 in the hip-yaw/knee/ankle groups in range) | rest census, sweep | unchanged (not posed per frame) | not posed | not posed | — | as before; these are the withdrawn servo-face proposals |

## 5 · The corrected single-joint sweep (`out/fit/sweep.json`, `sweep-depth.json`, rerun 22:06 CST)

Same tool, same 5° step and 0.5° bisection, with onsets keyed by pair **and
side**. 73 range collisions (54 before: 19 "+" onsets had been overwritten by
the "−" pass — 7 at the ankles, 1 at head roll, the rest screws). 4862 s under
a load average of 20–40. The structure onsets that changed:

| joint | side | onset | pair | before the fix |
|---|---|---|---|---|
| left ankle | + | **+0.31°** | ankle bracket × ankle servo | missing (only −0.31 was listed) |
| left ankle | + | +73.4 / +75.3 / +79.7° | ankle servo × foot, shin × ankle bracket, shin × foot | missing |
| right ankle | + | **+0.31°** | ankle bracket × ankle servo | missing |
| right ankle | + | +79.4 / +79.7 / +82.5° | shin × ankle bracket, ankle servo × foot, shin × foot | missing |
| head roll | + | +13.75° | part 29's servo × head-roll servo | missing (−8.1° was listed) |

Every left "+" onset now has its right "−" twin at the same angle (ankle
73.44 / 75.31 / 79.69 / 82.5, knee 70.94 / 75.31 / 79.69 / 89.69, hip yaw
18.12 / 23.75 / 24.69), which is the mirror the model is (§3.1). Depth at the
used-envelope edge (`fit_sweep_depth.py`, Pollen meshes as before):

| joint | used envelope | first structure collision | depth at the edge | verdict |
|---|---|---|---|---|
| left ankle | 0..+45.6° | bracket × servo from **+0.3°** | 2.50 mm at +45.6° | inside the envelope — the same as the right, see §3 |
| right ankle | −32.7..0° | bracket × servo from −0.3° | 2.50 mm at −32.7° | inside the envelope, unchanged |
| left / right knee | ..75.1° / −79.7.. | hip bracket × foot from ±70.9° | 2.10 / 3.73 mm | inside; coupled posing gives 2.99 / 2.81 (§2.2) |
| head roll | ±25° | part 29 × servo from −7.5°, servo × servo from −8.1° and +13.75° | 0.00 mm at ±25° on the crossing-only measure (the closed-mesh check gave 0.76–1.0 mm, REST-CENSUS §part 29) | within the servo-seat family |
| hip yaw, hip roll, hip pitch, neck pitch, head pitch, head yaw | | as in REST-CENSUS | | unchanged |

## 6 · Not done, and the limits of these numbers

- No physical part was measured. The 1.3–1.4 mm horn-seat overlap (§1.3) is a
  model finding; one printed seat's pocket depth would settle it.
- The vendor STEP is the manufacturer's XL330 family model; whether the fitted
  servos are that revision is the identity question
  `research/xl330-mechanical-source-2026-09-08/` leaves open. The six open
  shells were excluded; solid 4 is disjoint from the rest.
- Coupled posing samples the trajectories (every 4th or 8th frame in pass 1,
  every frame in pass 2 for graded pairs); a pair that touches only between
  two pass-1 samples and never reaches 0.05 mm at one is not in the list.
  Fasteners were not posed per frame (the sweep and rest census cover them).
- `yaw_roll_motion` pairs use the review lane's closed repair in memory; the
  simulator STL is still open.
- The parenting audit's holder criterion (0.5 mm over 60°) finds channel-type
  holders only; it cannot see a servo held by two bearings or by screws.
- `placements.json`, every mesh, every drawing and every review package are
  unchanged.
