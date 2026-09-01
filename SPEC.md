# SPEC — the Microduck we are rebuilding

*Every number carries its source and a confidence tag. Nothing here is a
claim that our rebuild is correct — this is what the rebuild is measured
against. Tags: **[P]** published by Pollen (press kit, store, blog, docs);
**[M]** measured by us off Pollen's own MJCF + meshes with
`ce-cad/bin/cad-mjcf` (reference/pollen-microduck-simulator/assembled/measured.json);
**[C]** community-reported, not verified by us; **[?]** not published, our
inference. Sources by number: research/01-product-and-specs.md §0.*

Leif, 2026-09-01: *"It should match the images exactly."* The standard this
document sets is stricter: match **Pollen's own geometry**, which they
published as 38 decimated STL meshes and one MJCF with every joint axis,
range, mass and placement. The photos are the check on colour, finish and
anything the decimated meshes lost.

## 1. Identity

| | | |
|---|---|---|
| product | Microduck, Pollen Robotics (Bordeaux) | [P] |
| price | $399 / €340; pre-orders opened 2026-08-27, Christmas 2026 target | [P] |
| lineage | commercial descendant of Open Duck Mini v2 (Antoine Pirrone): same joint naming and ID scheme (+34 for the mouth), different servo family, compute, IMU, battery; adds ToF, NFC, gripper beak; drops the two antenna servos | [P][C] |
| what is open | firmware + software Apache-2.0; MJCF + STL sim assets CC BY-SA-NC; **mechanical CAD, BOM, PCBs: not published** ("do not describe the robot as open-source hardware" — press kit) | [P] |
| Onshape source | `cad.onshape.com/documents/804927696f06d877f3f1803e` (from the MJCF header; not readable without a key — API 403 measured 2026-09-01) | [M] |

## 2. Envelope and mass

| quantity | value | source |
|---|---|---|
| standing height | 25 cm | [P] |
| width | 14 cm | [P] |
| mass | "under 800 g" / 780 g (store) | [P] |
| summed MJCF inertial mass | **737.2 g** over 15 bodies | [M] |
| zero-pose envelope (legs straight, head level) | **144.1 × 141.0 × 264.0 mm** (x × y × z), feet 13.5 mm above the free-joint ground | [M] |
| STAND keyframe | trunk z = 120 mm; hip_roll −5°, hip_pitch −26.24°, knee −0.28°, ankle +25.95°, neck_pitch +20°, head_pitch +20° (both legs mirrored) — the crouch that makes 264 mm into 25 cm | [P] microduck_rl scene xml |
| colourways | Cream `#f7e6cb` (orange trim/beak), Graphite `#6c6a68` (yellow), Lavender `#bfa9cf` (yellow), Sky `#a9dbe8` (orange) — "four printed colourways" | [P] |
| MJCF material colours | shells `0.8/0.8/0.8` grey-white; beak/feet/ankles `#fab601` yellow; soles + rigidity plate `#89dad3` mint; shin `#cfdbe5`; jaw_soft/mouth_top `#d9c1dd` lilac (soft parts) | [M] |

## 3. Kinematics — 15 motors, 14 policy DoF

Frame: MJCF world at zero pose — **+x forward (beak), +y left, +z up**,
trunk_base body origin at (0, 0, 120). All mm / degrees. [M]

| joint | ID | parent → child | axis origin (x, y, z) | world axis | range |
|---|---|---|---|---|---|
| left_hip_yaw | 20 | trunk_base → yaw2roll | (6.0, 17.5, 115.0) | −z | −25 … +30 |
| left_hip_roll | 21 | yaw2roll → hip_l | (22.5, 17.5, 102.5) | +x | ±22 |
| left_hip_pitch | 22 | hip_l → upper_leg_left | (4.0, 42.5, 102.5) | +y | ±90 |
| left_knee | 23 | upper_leg_left → leg | (−31.8, 38.5, 80.5) | −y | ±90 |
| left_ankle | 24 | leg → ankle_left | (−31.8, 64.5, 38.5) | +y | ±90 |
| neck_pitch | 30 | trunk_base → neck | (26.0, 14.5, 152.4) | −y | −90 … +60 |
| head_pitch | 31 | neck → neck_pitch | (26.0, 14.5, 202.4) | +y | ±90 |
| head_yaw | 32 | neck_pitch → yaw_roll_motion | (26.0, 0, 221.1) | +z | ±170 |
| head_roll | 33 | yaw_roll_motion → jaw_soft (the head) | (8.1, 0, 235.6) | −x | ±25 |
| mouth | 34 | inside the head; not in the MJCF tree; −5° closed … +30° open | — | — | [P] runtime |
| right_* | 10–14 | mirror of left about y = 0 | | | |

Derived link lengths [M]: hip-yaw axes 35 mm apart (y ±17.5); hip-pitch axes
85 mm apart (y ±42.5); knee axes y ±38.5; ankle axes y ±64.5 (shin offset
26 mm outboard of the knee). Thigh hip-pitch→knee: Δ(−35.8, −4, −22) mm =
**42.0 mm** sagittal. Shin knee→ankle: Δ(0, +26, −42) = 42 mm vertical.
Ankle→sole contact site Δ(0, −14.1, −23.8). Neck pitch→head pitch **50 mm**.
Head-roll axis→mouth tip 77.7 mm forward. Camera site (81.4, 0, 251.1),
ToF (81.4, 22.4, 249.1), head IMU (59.2, 0, 250.8), trunk IMU (−21, 0, 105.3).

Body masses (MJCF inertials) [M]: trunk_base 199.2 g · yaw2roll 23.0 ×2 ·
hip_l 6.19 ×2 · upper_leg 48.2 ×2 · leg 21.6 ×2 · ankle 30.0 ×2 · neck 36.8 ·
neck_pitch 5.72 · yaw_roll_motion 48.6 · head (jaw_soft body) 188.8.

## 4. The parts — what each mesh is, measured

Every mesh's bbox in its own file frame (mm), from `cad-mjcf meshes`. [M]
Fasteners: the community hole analysis reads the whole robot as an **M2
system** (Ø2.2 clearance ×77, Ø4.4 c'bore ×28, Ø1.6 tap ×20, Ø2.7/2.8 ×20)
[C]; bearings 22×16×4 (×11) and 15×10×3 (×3) — named "seeed_bearing" [M].

### 4.1 Trunk
| mesh | size | reading |
|---|---|---|
| trunk_base | 57.0 × 36.0 × 1.0 (a 3 mm plate in the community export) | the chassis plate both hip-yaw servos hang from |
| left_shell / right_shell | 33.7 × 80.9 × 41.7 / 31.8 × 80.9 × 41.7 | the two half-shells of the egg body, colourway part |
| power_support ×2 | 54.5 × 17.0 × 83.5 | battery cradle halves (self-collision geom) |
| np_f970 (named) | 38.6 × 20.6 × 70.8 | **an NP-F550** envelope (38.4 × 20.6 × 70.8), not F970; product spec says NP-F550 |
| banana_pcb_locker | 53.5 × 3.8 × 6.6 | PCB retaining bar |
| xl330 ×2 (hip yaw) | 29.0 × 20.0 × 34.0 | XL330 incl. horn; datasheet body 20.0 × 34.0 × 26.0 |

### 4.2 Leg (×2, mirrored)
| mesh | size | reading |
|---|---|---|
| yaw2roll | 23.0 × 25.8 × 20.5 | hip-yaw output link carrying the roll servo |
| bearing_roll | 23.0 × 3.0 × 40.0 | the idler plate opposite the yaw servo horn |
| hip_l | 32.5 × 34.5 × 19.0 | hip-roll output bracket (used ×4 counting collision) |
| upper_leg_left/right | 28.0 × 47.7 × 61.0 | thigh housing holding the hip-pitch and knee servos |
| upper_leg_rigidity_plate | 1.0 × 45.0 × 58.1 | a 1 mm side plate stiffening the thigh (mint) |
| leg ×2 per side | 8.0 × 20.0 × 58.0 | shin: two parallel plates 8 mm thick |
| xl330 ×3 per leg | | hip roll, hip pitch, knee — plus ankle servo in the shin |
| ankle_left/right | 39.5 × 36.5 × 25.5 | ankle bracket (yellow) |
| foot_left/right | 40.1 × 54.0 × 16.9 | foot (yellow) |
| sole_left/right | 41.1 × 54.0 × 12.9 | sole, mint, the contact geom |

### 4.3 Neck and head
| mesh | size | reading |
|---|---|---|
| neck ×2 | 2.0 × 20.0 × 11.0 | two 2 mm plates spanning the 50 mm neck (servo at each end) |
| neck_pitch | 35.0 × 18.0 × 27.7 | head-pitch output bracket |
| yaw_roll_motion | 34.0 × 35.9 × 22.5 | head-yaw output carrying the roll servo |
| motor_support | 73.5 × 54.2 × 18.8 | the plate inside the head that holds the roll/mouth servos + electronics |
| top_head_shell | 91.6 × 122.7 × 46.3 | the dome (colourway) |
| bottom_head_shell | 91.7 × 116.7 × 20.1 | the yellow underside of the head |
| face_part | 87.7 × 12.5 × 44.6 | the front face plate with eyes/camera aperture |
| noenoeil | 29.9 × 9.5 × 29.9 | eye part |
| jaw | 91.4 × 68.7 × 29.4 | the lower beak (yellow), mouth DoF |
| jaw_soft / soft_mouth_top | 87.7 × 32.2 × 8.4 / 87.8 × 32.6 × 3.3 | soft lips (lilac — TPU/soft) |
| lens / m12_lens_holder | 16.9 × 18.9 × 16.9 / 23.1 × 14.8 × 16.0 | M12 lens + holder → IMX219 sensor board |
| pcb__raspberry_pi_zero_2_w | 65.0 × 1.6 × 30.0 | **Radxa Zero 3W** footprint (same as Pi Zero) — compute lives IN THE HEAD |
| elec_rpi_robot_hat_pcb | 65.0 × 30.0 × 0.84 | Pollen "RPI Robot HAT" (codec, ToF, dormant BMI088) |
| speaker | 35.0 × 25.0 × 7.0 | placeholder box, 12 tris |

## 5. Electronics (what the rebuild must house)

| item | fact | source |
|---|---|---|
| servos | 15 × Dynamixel XL330 (sub-variant M288 vs M077 **not stated**; community assumes M288-T). 18 g each; 20.0 × 34.0 × 26.0 mm; 3.7–6.0 V datasheet, run here at 6.6–8.2 V pack; one 1 Mbps TTL half-duplex bus on `/dev/ttyS2` | [P][?] |
| compute | Radxa Zero 3W (RK3566, 1 GB, 32 GB eMMC, Wi-Fi 6/BT 5.4, 65 × 30 mm) — device-tree `radxa,zero-3w` | [P] |
| HAT | Pollen "RPI Robot HAT", 65 × 30 mm, TLV320AIC3104 codec, VL53L5CX/L8CX 8×8 ToF on I²C3, dormant BMI088, half-duplex transceiver, battery-to-board power | [P] source |
| control IMU | LSM6DSV16X on `imu_to_dxl` v2 board, Dynamixel ID 200 — trunk site at (−21, 0, 105.3) | [P][M] |
| camera | IMX219 sensor, M12 wide-angle lens, mounted upside down | [P] |
| battery | NP-F550 2S Li-ion 2600 mAh, removable, 6.6–8.2 V window, ~1 h | [P] |
| audio | mic(s) + speaker (35 × 25 × 7 placeholder) | [P][M] |
| NFC | two antennas: head and beak; IC not published | [P] |

## 6. Manufacturing (published vs inferred)

- "Four **printed** colourways" is the only word about process [P]. The
  meshes show 1–3 mm plates, 2 mm shell walls and printed-style bosses;
  our rebuild targets **FDM print** for every custom part, walls ≥ 1.2 mm,
  bosses for **M2** screws, and heat-set inserts where a thread is loaded [?].
- Soft parts (jaw_soft, soft_mouth_top): TPU [?].
- Bearings: 22×16×4 (MR-style thin section) ×11, 15×10×3 ×3 [M].

## 7. What we do NOT know (CANNOT DETERMINE until measured on a unit)

Official CAD/STEP, drawings, BOM; PCB schematics; XL330 sub-variant; screw
lengths and insert types; whether shells are moulded; soft-part material;
speaker/mic part numbers; NFC IC; harness routing through the neck yaw;
charger specs; real weight breakdown. Each is listed with what would settle
it in research/01-product-and-specs.md §19.

## 8. Acceptance — how "matches" is measured

For every rebuilt custom part: `cecad.meshcompare.compare(ours, theirs)`
against the reference mesh — **PASS at p95 surface distance ≤ 1.0 mm both
ways and bbox within 1.5 mm per axis** (the decimation error of their
export is the floor). For the assembly: every joint axis within 0.5 mm and
0.5° of the table in §3, via `cad-mjcf tree` on our exported model. For the
look: photo-match overlays of `cecad.meshview` silhouettes on the press
photos (images/). Results land in `evidence/ledger.jsonl`.

## Status

- 2026-09-01: reference material collected and measured; tools written
  (`cad-mjcf`, `meshview`, `meshcompare`, `Part.loft/ellipsoid/shell/from_mesh`,
  multi-root triad); this spec. Next: blueprint (P12) and the part-by-part
  rebuild.
