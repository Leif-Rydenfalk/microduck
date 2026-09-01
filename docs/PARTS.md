# PARTS — every part of the Microduck, one row each, every number sourced

*Written 2026-09-01 from the research dossiers. Leif: "make documents with all of
the specifications your research team found out. all of the parts and how the
software connects to it should be known." This is the parts half; the software
half is `ELECTRONICS-AND-SOFTWARE.md`, the buying half is `BOM.md`.*

Nothing here is a claim that our rebuild is right. Pollen has published **no
CAD, no drawings, no BOM** (press kit: "The mechanical and electronic design
files are not [open], so please do not describe the robot as open-source
hardware" — research/01-product-and-specs.md §2, §14). Every dimension below
is measured off Pollen's own decimated simulation meshes (CC BY-SA-NC) or read
out of their open runtime. Where a fact is not in any source it says
**CANNOT DETERMINE** and what would settle it.

## Source key

| key | file / URL |
|---|---|
| [SPEC §n] | `SPEC.md` |
| [R1 §n] | `research/01-product-and-specs.md` (S-numbers = its §0 URL table) |
| [R2 §n] | `research/02-repos-and-code.md` |
| [M] | `reference/pollen-microduck-simulator/assembled/measured.json` — `meshes[].size_mm` (bbox in the mesh's own file frame, mm) and `joints[]` |
| [PL] | `spec/mesh-placements.json` — one entry per *visual* geom: body, pos, quat, material rgba |
| [MAP] | `spec/mesh-to-part.json` — Pollen mesh name → our `part:` slug |
| [BOM-SEED] | `ce-assemblies/microduck/current/bom.json` — qty per slug counted from the MJCF visual geoms |
| [CP slug] | `ce-parts/<slug>/component.json` + `iterations/v0.0.1/trust.json` + `evidence/ledger.jsonl` (re-read 2026-09-01 23:35 +0800, after commit dcc39bd) |
| [C-fast] | `research/raw/community/replica_fastener-reconstruction.en.md` (fanhao375/microduck-replica — **community, mesh-derived, unverified**) |
| [C-elec] | `research/raw/community/replica_hardware-teardown.en.md` (community) |
| [XL330] | https://emanual.robotis.com/docs/en/dxl/x/xl330-m288/ via `spec/specs-published.json` |
| [store-*] | `research/raw/store_{microduck,devpack,accessory,charger}.json` (Shopify JSON, 2026-09-01) |
| [presskit] | https://pollen-robotics.com/microduck/press-kit/ via `research/raw/presskit.txt` |

Frame for "body" and "joint": MJCF world at zero pose, +x forward (beak), +y
left, +z up, `trunk_base` origin at (0, 0, 120) mm [SPEC §3]. The joint each
servo drives is **inferred** from which body the `xl330` mesh sits in [PL] —
the MJCF does not label servos with Dynamixel IDs; that mapping (IDs 20–24 /
30–34 / 10–14) is `research/raw/duck-control_src_model.rs:15-19`.

Colour column = the MJCF material rgba of the placed geom [PL], as hex. Real
shell colour is the colourway (Cream `#f7e6cb`, Graphite `#6c6a68`, Lavender
`#bfa9cf`, Sky `#a9dbe8`; trim/beak orange for Cream and Sky, yellow for
Graphite and Lavender) [presskit; R1 §12].

Rebuild status = trust tier from `trust.json` (T0 untested … T1 simulated) and
the `component.json` verdict. "no folder" = slug named in [MAP] but
`ce-parts/<slug>/` does not exist yet.

**Qty correction.** `measured.json` `placed` counts *every* geom, so meshes
that are also collision geoms show double (`leg` 4, `power_support` 2,
`hip_l` 4, `np_f970` 2, `top_head_shell` 2, `jaw` 2, `sole_*` 2). SPEC.md §4
copied two of those ("power_support ×2", "leg ×2 per side"). The visual-geom
count in [PL]/[BOM-SEED] is the part count: **`leg` ×2 per robot (one plate
per shin), `power_support` ×1.** `reference/pollen-microduck-simulator/robot_allcollisions.xml:155-156,314-315`
shows one `visual` + one `collision` geom of `leg` per shin.
`ce-parts/microduck-shin/component.json` says `qty_per_robot: 4` — that is
the same double count and should be 2.

## 1. Parts with a mesh (38 rows — every entry of `spec/mesh-to-part.json`)

| # | our slug | Pollen mesh | what it is | qty | kind | size mm (x × y × z) [M] | MJCF colour [PL] | body [PL] | joint / axis it carries | rebuild status | sources |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `microduck-trunk-base` | `trunk_base` | chassis plate both hip-yaw servos hang from; carries the two 22×16×4 hip-yaw idler bearings at (6, ±17.5, −5) body-frame | 1 | printed | 57.0 × 36.0 × 1.0 (community export reads 3.0 [R1 §3.3]) | `#596066` dark grey | trunk_base (root) | hip-yaw axes L/R at world (6, ±17.5, 115) −z [M joints]; neck_pitch axis at (26, 14.5, 152.4) | **T1 PASS** (refcheck vs trunk_base.stl) [CP microduck-trunk-base] | [SPEC §4.1] [M] |
| 2 | `microduck-banana-pcb-locker` | `banana_pcb_locker` | 54 × 1.5 × 6.6 retaining bar, two Ø2.17 M2 holes in Ø4 eyes, 12 mm notch, two key tabs; clamps the "banana" battery-contact PCB to power_support's Ø3.9 pins | 1 | printed (PLA/FDM per component.json) | 53.5 × 3.8 × 6.6 | `#a5a5a5` | trunk_base | none | **T1 PASS** p95 0.013 mm, 2/2 holes [CP microduck-banana-pcb-locker] | [SPEC §4.1] |
| 3 | `microduck-power-support` | `power_support` | battery cradle / power bracket, 8 Ø1.6 M2 tap holes [C-fast]; self-collision geom | **1** (not 2 — see qty correction) | printed (PLA/FDM) | 54.5 × 17.0 × 83.5 | `#e6e6e6` | trunk_base | none | **T1 PASS**, 2 ledger lines [CP microduck-power-support] | [SPEC §4.1] [M] |
| 4 | `microduck-trunk-shell-left` | `left_shell` | left half of the egg body — the colourway part; 7 M2 clearance holes [C-fast] | 1 | printed (shell) | 33.7 × 80.9 × 41.7 | `#cccccc` | trunk_base | none | no folder | [SPEC §4.1] [M] |
| 5 | `microduck-trunk-shell-right` | `right_shell` | right half-shell; 6 M2 clearance + 1 tap [C-fast] | 1 | printed (shell) | 31.8 × 80.9 × 41.7 | `#cccccc` | trunk_base | none | no folder | [SPEC §4.1] [M] |
| 6 | `microduck-yaw2roll` | `yaw2roll` | hip-yaw output link carrying the hip-roll servo; 8 M2 clearance + 6 c'bore [C-fast] | 2 (L in body `yaw2roll`, R in `bearing_roll`) | printed | 23.0 × 25.8 × 20.5 | `#a5a5a5` | yaw2roll / bearing_roll | child of hip_yaw (ID 20/10); houses hip_roll servo (21/11), roll axis +x at (22.5, ±17.5, 102.5) | T0 [CP microduck-yaw2roll] | [SPEC §4.2] [M] |
| 7 | `microduck-bearing-roll` | `bearing_roll` | 3 mm idler plate opposite the yaw-servo horn; 4 M2 clearance [C-fast] | 2 | printed | 23.0 × 3.0 × 40.0 | `#43484d` | yaw2roll / bearing_roll | hip-yaw axis (bearing side) | T0 (part.py modified, uncommitted) [CP microduck-bearing-roll] | [SPEC §4.2] [M] |
| 8 | `microduck-hip-bracket` | `hip_l` | hip-roll output bracket; 9 M2 clearance + 6 c'bore [C-fast]; one 22×16×4 bearing | 2 (bodies `hip_l`, `hip_l_2`) | printed | 32.5 × 34.5 × 19.0 | `#e6e6e6` | hip_l / hip_l_2 | child of hip_roll (21/11); hip_pitch axis +y at (4, ±42.5, 102.5) | T0 [CP microduck-hip-bracket] | [SPEC §4.2] [M] |
| 9 | `microduck-upper-leg-left` | `upper_leg_left` | thigh housing holding hip-pitch + knee servos (2 × xl330 in this body) | 1 | printed | 28.0 × 47.7 × 61.0 | `#dddddd` | upper_leg_left | hip_pitch (22) child; knee (23) axis −y at (−31.8, 38.5, 80.5); thigh 42.0 mm sagittal | **T1 PASS** [CP microduck-upper-leg-left] | [SPEC §3, §4.2] |
| 10 | `microduck-upper-leg-right` | `upper_leg_right` | mirror of 9 | 1 | printed | 28.0 × 47.7 × 61.0 | `#dddddd` | upper_leg_right | hip_pitch (12) / knee (13) | **T1 PASS** p95 0.20 mm, 6/6 features [CP microduck-upper-leg-right] | [M] |
| 11 | `microduck-upper-leg-rigidity-plate` | `upper_leg_rigidity_plate` | 1 mm side plate stiffening the thigh; 4 M2 clearance [C-fast]; mint in MJCF | 2 | printed (or sheet — CANNOT DETERMINE; 1 mm is thin for FDM) | 1.0 × 45.0 × 58.1 | `#89dad3` mint | upper_leg_left / right | spans hip_pitch→knee | T0 [CP microduck-upper-leg-rigidity-plate] | [SPEC §4.2] [R2 §4.3 "1 mm plate (sheet?)"] |
| 12 | `microduck-shin` | `leg` | shin plate, 8 mm thick, 1 mm rim walls, 2.3/2.8 mm stepped plate (docs/REBUILD-PROTOCOL.md §1); carries the ankle servo (1 × xl330 in body `leg`); 6 M2 clearance + 6 c'bore [C-fast] | **2** (one per shin; component.json says 4 — double count) | printed (PLA/FDM) | 8.0 × 20.0 × 58.0 | `#cfdbe5` | leg / leg_2 | knee (23/13) child; ankle (24/14) axis +y at (−31.8, ±64.5, 38.5); shin 42 mm vertical, 26 mm outboard offset | **T1 PASS** p95 1.00 mm (r4) [CP microduck-shin; REBUILD-PROTOCOL] | [SPEC §3, §4.2] |
| 13 | `microduck-ankle-left` | `ankle_left` | ankle bracket (yellow trim); 5 M2 clearance + 5 c'bore [C-fast]; 15×10×3 bearing | 1 | printed | 39.5 × 36.5 × 25.5 | `#fab601` yellow | ankle_left | ankle (24) child; sole contact site Δ(0, −14.1, −23.8) from ankle | T0 [CP microduck-ankle-left] | [SPEC §3, §4.2] |
| 14 | `microduck-ankle-right` | `ankle_right` | mirror of 13 | 1 | printed | 39.5 × 36.5 × 25.5 | `#fab601` | ankle_right | ankle (14) | T0 [CP microduck-ankle-right] | [M] |
| 15 | `microduck-foot-left` | `foot_left` | hard foot (yellow trim) | 1 | printed | 40.1 × 54.0 × 16.9 | `#fab601` | ankle_left | fixed to ankle | no folder | [SPEC §4.2] |
| 16 | `microduck-foot-right` | `foot_right` | mirror of 15 | 1 | printed | 40.1 × 54.0 × 16.9 | `#fab601` | ankle_right | fixed to ankle | no folder | [M] |
| 17 | `microduck-sole-left` | `sole_left` | sole = the foot contact geom (`left_foot_collision`, condim 3, friction 1.0 [R1 §4.3 / `microduck_constants.py:133-138`]) | 1 | **soft** (TPU inferred [SPEC §6]; community says TPU 90–95A [R2 §1c]) | 41.1 × 54.0 × 12.9 | `#89dad3` mint | ankle_left | ground contact | no folder | [SPEC §4.2] |
| 18 | `microduck-sole-right` | `sole_right` | mirror of 17 | 1 | soft | 41.1 × 54.0 × 12.9 | `#89dad3` | ankle_right | ground contact | no folder | [M] |
| 19 | `microduck-neck-plate` | `neck` | 2 mm side plate; two of them span the 50 mm neck with a servo at each end (2 × xl330 in body `neck`); 4 M2 clearance each [C-fast] | 2 | printed | 2.0 × 20.0 × 11.0 | `#cccccc` | neck | neck_pitch (30) child, axis −y at (26, 14.5, 152.4); head_pitch (31) axis +y at (26, 14.5, 202.4) — 50 mm apart | no folder | [SPEC §3, §4.3] |
| 20 | `microduck-neck-pitch-bracket` | `neck_pitch` | head-pitch output bracket; 12 M2 clearance + 4 c'bore [C-fast]; one 22×16×4 bearing at (0, 20.8, −14.5) body = the head-yaw axis | 1 | printed | 35.0 × 18.0 × 27.7 | `#596066` | neck_pitch | head_pitch (31) child; head_yaw axis +z at (26, 0, 221.1) | no folder | [SPEC §3, §4.3] [PL] |
| 21 | `microduck-yaw-roll-motion` | `yaw_roll_motion` | head-yaw output carrying the head-roll servo (1 × xl330); two 22×16×4 bearings at x = −16 and +18 body-frame straddling the roll axis; 4 M2 clearance + 6 c'bore [C-fast] | 1 | printed | 34.0 × 35.9 × 22.5 | `#c4e2f3` | yaw_roll_motion | head_yaw (32) child; head_roll axis −x at (8.1, 0, 235.6) | no folder (the only mesh whose denser copy is in the *simulator* set: `reference/which-mesh-is-denser.json`) | [SPEC §3, §4.3] |
| 22 | `microduck-motor-support` | `motor_support` | plate inside the head holding the roll and mouth servos (2 × xl330 in body `jaw_soft`) and the electronics | 1 | printed | 73.5 × 54.2 × 18.8 | `#43484d` | jaw_soft (the head) | head_roll (33) child; mouth (34) hinge | no folder | [SPEC §4.3] |
| 23 | `microduck-top-head-shell` | `top_head_shell` | the dome (colourway part); 3 M2 clearance [C-fast] | 1 | printed (shell) | 91.6 × 122.7 × 46.3 | `#e6e6e6` | jaw_soft | — | no folder | [SPEC §4.3] |
| 24 | `microduck-bottom-head-shell` | `bottom_head_shell` | underside of the head (trim colour); 4 M2 clearance [C-fast] | 1 | printed | 91.7 × 116.7 × 20.1 | `#fab601` yellow | jaw_soft | — | no folder | [SPEC §4.3] |
| 25 | `microduck-face-part` | `face_part` | front face plate with eyes / camera aperture; 10 M2 clearance + 4 tap [C-fast] | 1 | printed | 87.7 × 12.5 × 44.6 | `#596066` | jaw_soft | camera site at world (81.4, 0, 251.1); ToF at (81.4, 22.4, 249.1) | T0 (folder created, untracked) [CP microduck-face-part] | [SPEC §3, §4.3] |
| 26 | `microduck-eye-ring` | `noenoeil` | eye part ("noenoeil" — French for an eye-piece) | 1 | printed | 29.9 × 9.5 × 29.9 | `#43484d` | jaw_soft | — | T0 (folder created, untracked) [CP microduck-eye-ring] | [SPEC §4.3] |
| 27 | `microduck-m12-lens-holder` | `m12_lens_holder` | M12 lens mount on the IMX219 sensor board; 3 M2 clearance [C-fast] | 1 | **bought** (standard M12 holder) or printed — CANNOT DETERMINE | 23.1 × 14.8 × 16.0 | `#43484d` | jaw_soft | camera | T0 (folder created, untracked) [CP microduck-m12-lens-holder] | [SPEC §4.3] [R1 §3.3] |
| 28 | `microduck-m12-lens` | `lens` | M12 wide-angle lens, Ø16.9 × 18.9 | 1 | bought | 16.9 × 18.9 × 16.9 | `#43484d` | jaw_soft | camera | T0 (folder created, untracked) [CP microduck-m12-lens] | [SPEC §4.3] |
| 29 | `microduck-jaw` | `jaw` | the lower beak (trim colour), the mouth DoF, 5 M2 clearance [C-fast]; a fixed geom in the MJCF (no joint) | 1 | printed | 91.4 × 68.7 × 29.4 | `#fab601` | jaw_soft | mouth (34) −5° closed … +30° open (`model.rs:62-63`); not in the MJCF tree; ~100 g lift (press, R1 §2) | no folder | [SPEC §3, §4.3] |
| 30 | `microduck-jaw-soft` | `jaw_soft` | soft lower lip, 8.4 mm thick | 1 | **soft** (TPU inferred) | 87.7 × 32.2 × 8.4 | `#d9c1dd` lilac | jaw_soft (this mesh names the head body) | mouth | no folder | [SPEC §4.3, §6] |
| 31 | `microduck-soft-mouth-top` | `soft_mouth_top` | soft upper lip, 3.3 mm thick | 1 | soft | 87.8 × 32.6 × 3.3 | `#d9c1dd` | jaw_soft | mouth | no folder | [SPEC §4.3] |
| 32 | `xl330-m288-t` | `xl330` | ROBOTIS Dynamixel XL330 servo incl. horn; sub-variant M288 vs M077 **not stated by Pollen** (community assumes M288-T) | **15** | bought | 29.0 × 20.0 × 34.0 mesh; datasheet body 20.0 × 34.0 × 26.0, 18 g, 288.4:1 [XL330] | `#494949` | trunk_base ×2 (hip yaw 20/10), yaw2roll + bearing_roll ×1 (hip roll 21/11), upper_leg L/R ×2 each (hip pitch 22/12, knee 23/13), leg/leg_2 ×1 (ankle 24/14), neck ×2 (neck pitch 30, head pitch 31), yaw_roll_motion ×1 (head yaw 32), jaw_soft ×2 (head roll 33, mouth 34) | all 15 joints | T0 [CP xl330-m288-t] | [R1 §4] [R2 §3.1] [PL] |
| 33 | `bearing-22x16x4` | `seeed_bearing__configuration__22x16x4` | thin-section ball bearing OD 22 × ID 16 × W 4 ("seeed_bearing" is Pollen's Onshape name; supplier CANNOT DETERMINE) | **11** | bought | Ø22 × 4 | `#b6c2cc` | trunk_base ×2, yaw2roll, bearing_roll, hip_l, hip_l_2, upper_leg L, upper_leg R, neck_pitch, yaw_roll_motion ×2 | hip yaw ×2, hip roll ×2, hip pitch ×2, knee ×2, head yaw ×1, head roll ×2 | T0 [CP bearing-22x16x4] | [PL] [SPEC §4] [C-fast] |
| 34 | `bearing-15x10x3` | `seeed_bearing__configuration_default` | ball bearing OD 15 × ID ~10 × W 3 | **3** | bought | Ø15 × 3 | `#b6c2cc` | ankle_left, ankle_right, jaw_soft | ankle ×2, mouth hinge ×1 | T0 [CP bearing-15x10x3]; connection `press-fit-bearing-15x10x3` exists | [PL] [C-fast] |
| 35 | `np-f550` | `np_f970` | battery — mesh is **named** F970 but its envelope 38.6 × 20.6 × 70.8 is an NP-F550 (an F970 is ~38 mm thick); product spec says NP-F550 2600 mAh removable | 1 | bought | 38.6 × 20.6 × 70.8 | `#e6e6e6` | trunk_base | — | T0 [CP np-f550] | [SPEC §4.1, §5] [R1 §9, §19.2] |
| 36 | `radxa-zero-3w` | `pcb__raspberry_pi_zero_2_w` | compute — mesh is a Pi Zero 2 W (the prototype's board); production is a Radxa Zero 3W, same 65 × 30 footprint; lives **in the head** | 1 | bought | 65.0 × 1.6 × 30.0 | `#7f7f7f` | jaw_soft | — | T0 [CP radxa-zero-3w] | [SPEC §4.3, §5] [R2 §3.3] |
| 37 | `microduck-robot-hat-pcb` | `elec_rpi_robot_hat_pcb` | Pollen "RPI Robot HAT": codec, ToF connector, dormant BMI088, battery power path, (inferred) half-duplex bus transceiver; Pi-Zero footprint, 0.84 mm mesh | 1 | **custom PCB — no design files published** | 65.0 × 30.0 × 0.84 | `#507c69` green | jaw_soft | — | T0 [CP microduck-robot-hat-pcb] | [SPEC §5] [R1 §8] |
| 38 | `microduck-speaker` | `speaker` | placeholder box, 12 triangles — the real speaker part is not modelled | 1 | bought (part number CANNOT DETERMINE) | 35.0 × 25.0 × 7.0 | `#4b4a4a` | jaw_soft | — | T0 [CP microduck-speaker] | [SPEC §4.3] |

Sanity totals: 38 rows; visual geoms 70 [BOM-SEED]; servos 15; bearings 14;
bodies 15 [M joints]. Meshes in Pollen's set that have **no slug** (not
rebuilt): `trunk_shell_left/right` (older alt shells [R1 §3.3]),
`ankle_l_v1/r_v1`, `roller_blade`, `rim`, `tire` (roller variant, §4 below),
and `left_upper_leg/right_upper_leg` (duplicate names in the simulator copy)
— `reference/which-mesh-is-denser.json`.

## 2. Parts with no mesh

These are real parts on the product that Pollen's MJCF does not model. None
has a slug yet.

| part | qty | what we know | CANNOT DETERMINE — what settles it | sources |
|---|---|---|---|---|
| `imu_to_dxl` v2 board | 1 | LSM6DSV16X IMU presented as a Dynamixel Protocol-2 slave, ID 200, 12-byte block at register 124 (gyro i16 ±500 dps, SFLP quaternion fp16); mounted +90° about Y (`trunk = [+raw_z, +raw_y, −raw_x]`); trunk `imu` site at world (−21, 0, 105.3) — behind and below the trunk origin | board outline, MCU, transceiver, mounting holes, cable — a photo of a production trunk with the shell off, or Pollen publishing the board | `research/raw/duck-control_src_imu.rs:1-17, 76-83`; `model.rs:78`; [SPEC §3] |
| second IMU (head) | 1 | press kit: "2 IMUs, one in the body and one in the head"; MJCF `head_imu` site in the head at world (59.2, 0, 250.8); the HAT (in the head) carries a **dormant BMI088** at I²C 0x19/0x68 "unused but still connected" | whether the production head IMU *is* the HAT's BMI088 or a second LSM6DSV16X — read `sensors.xml` bindings on a shipped unit, or i2cdetect on a production board | [R1 §7.3]; `research/raw/deploy_audio_i2c3-pihat.dts:11` |
| camera sensor board | 1 | IMX219 (Pi Camera v2 class), probe log "imx219 2-0010: Model ID 0x0219", overlay `radxa-zero3-rpi-camera-v2`, **mounted upside down** (rotation 180), M12 lens + holder meshes, sits behind `face_part` | exact module (Pi Cam v2 with lens removed vs an M12-mount IMX219 board), ribbon length, FOV ("still being finalised" — press kit) | [R1 §7.1]; `research/raw/microduck_main_docs_project_media-bringup.md:312, 472` |
| ToF module | 1 | VL53L5CX **or** VL53L8CX (both drivers vendored), 8×8, 15 Hz, I²C 0x29 (0x52 legacy), via the HAT's "Stemma J5"; `tof` site at world (81.4, 22.4, 249.1), 22.4 mm left of the camera; 45°×45° FOV in `kinematics/src/tof.rs` | which generation ships; which breakout (Stemma QT = 4-pin JST-SH 1 mm) | `research/raw/tof_src_main.rs:80-87`; [R2 §3.3]; [R1 §7.2] |
| microphone(s) | ≥1 ("Microphones", plural, press kit) | on the head (pet_detect README); codec input **Mic3R mono** [C-elec, community] | part, count, placement — a production teardown | [R1 §7.4]; [R2 §1b] |
| speaker | 1 | 35 × 25 × 7 placeholder box in the head; codec line-out [C-elec]; ALSA `plughw:aic3104` | driver, impedance, amplifier (codec's own vs external) | [SPEC §4.3]; `deploy_robotd.toml [audio]` |
| NFC antennas | 2 | "one in the head and one in the beak" (press kit); accessory NFC Polaroid tapped "on your robot's head"; 10 NFC tags in Dev/Accessory packs | reader IC, bus, antenna geometry — nothing in the runtime source mentions NFC (grep of `duck-ipc-proto_lib.rs` and `research/microduck-elec-grep.txt`: 0 hits) | [R1 §7.5]; [store-accessory] |
| camera-use indicator LED | 1 | "a dedicated camera-use indicator inspired by classic REC lights" | which GPIO, where it sits | [presskit] |
| servo cables | 15–16 | 3-pin TTL Dynamixel leads (XL330 datasheet: TTL multidrop); Dev Pack sells "5 × Motor Cables" as spares; harness must pass the head-yaw joint (±170°) | lengths per joint, routing through neck yaw, daisy-chain order | [XL330]; [store-devpack]; [R1 §19] |
| battery contact PCB ("banana") | 1 | named by `banana_pcb_locker` — the bar clamps a battery-contact PCB to power_support | its shape, contacts, wiring to the HAT | [CP microduck-banana-pcb-locker] |
| screws / inserts | ~146 structural | see §5 | — | [C-fast] |
| gamepad | 1 | in the box; Bluetooth; Xbox-style button names (A/B/X/Y, LB/RB, LT/RT, Start/Select) in the cheatsheet; `padd` reads `gilrs` | make/model | [R1 §2]; `microduck_main_docs_robot_cheatsheet.md:236-249` |
| USB-C cable | 1 | in the box; 5 V charging path | — | [R1 §2, §9] |
| dual battery charger | 1 (Charger Pack) | "1 × Dual Battery Charger, charge two batteries simultaneously", €33 / $39 with 2 batteries, 268 g shipped | voltage/current, whether the robot charges in-situ over USB-C with the pack fitted | [store-charger]; [R1 §19] |
| power switch | ? | none in any source; "Select held 2 s: sit down, then power off" is software | whether a hardware switch exists | [cheatsheet:249] |

## 3. Bearings

| size | qty | where (bodies, [PL] pos mm) | axis | notes |
|---|---|---|---|---|
| 22 × 16 × 4 | 11 | trunk_base (6, ±17.5, −5); yaw2roll & bearing_roll (0, 16.5, 12.5); hip_l & hip_l_2 (21/25, 0, −18.5); upper_leg L/R (22, 35.8, −4); neck_pitch (0, 20.8, −14.5); yaw_roll_motion (−16, 0, 14.5) and (18, 0, 14.5) | every 22×16×4 sits on a servo axis opposite the horn — the idler side of each joint; head roll gets two | Onshape config name "22x16x4"; MR-style thin section [SPEC §6]. Supplier/MPN CANNOT DETERMINE — a Seeed Studio SKU search or a production teardown settles it |
| 15 × 10 × 3 | 3 | ankle_left, ankle_right, jaw_soft | ankle L/R, mouth hinge | ID "~10" is community-measured [C-fast]; our connection `ce-connections/press-fit-bearing-15x10x3` |

Servo horn side: `ce-connections/spline-xl330-horn` (the XL330 output spline).

## 4. Roller variant (accessory)

Not in `mesh-to-part.json`; listed so the omission is deliberate.

| mesh | size mm | role | source |
|---|---|---|---|
| `ankle_l_v1` / `ankle_r_v1` | 39.5 × 46.5 × 25.4 | roller ankle replacing `ankle_left/right` | [R2 §4.3] |
| `roller_blade` | 40.5 × 73 × 30.4 | the skate frame under each foot | [R2 §4.3] |
| `rim` ×2 per foot | Ø20.2 × 7.6 | wheel hub | [R2 §4.3] |
| `tire` ×4 | Ø30 × 7.6 | passive wheels: `passive_LF/LR/RF/RR_wheel` hinges at (∓39.5/±25.5, −32.5, −14.7) → **65 mm wheelbase** | [R2 §4.1] |

Sold as "2 × Rollers" in the Accessory Pack (€33 / $39, orange or yellow to
match the trim) [store-accessory]. Software: `policy.mode = "roller"` loads
`roller.onnx` + `roller_crouch.onnx`, action_scale 0.8; DPad-Up held 3 s
switches modes live (`deploy_robotd.toml [policy]`; cheatsheet:248). Whether
to rebuild the roller kit: CANNOT DETERMINE — Leif's product preference.

## 5. Fasteners (M2 evidence — community, mesh-derived, flagged)

No screw list exists. fanhao375 fitted cylinders to every hole in the 47
meshes [C-fast]:

| Ø | count | reading |
|---|---|---|
| 2.2 | 77 | M2 clearance |
| 4.4 | 28 | M2 socket-head counterbore |
| 1.6 | 20 | M2 tap drill |
| 2.4 | 22 | loose M2 clearance |
| 2.0 | 12 | tight M2 clearance |
| 2.7 / 2.8 | 20 | M2.5 clearance |
| 4.8 | 10 | M2 c'bore, second depth |
| 5.4 / 6.0 | 16 | shaft bores / bearing seats, not fasteners |

Ø2.2 + Ø4.4 pairs on `yaw2roll`, `leg`, `ankle_left`, `neck_pitch`,
`yaw_roll_motion` → **M2 socket-head cap screws**. `xl330.stl` carries
4 × Ø2.0 + 8 × Ø1.6 = the XL330's own M2 pattern. Total M2 clearance holes 213,
of which 60 are on servo bodies; **~146 structural**. Depths: 51 at 0–3 mm, 24
at 3–5 mm, 4 at 8–12 mm. Their purchase estimate (with spares): M2×4 ×60,
M2×6 ×80, M2×8 ×40, M2×12 ×15, M2 nuts ×50, M2 heat-set inserts ×60,
M2.5×6 ×20.

Flags: (1) simulation meshes, not drawings — no tolerances, threads
simplified; (2) FDM holes print 0.1–0.3 mm undersize; (3) counterbores and
clearance holes may be the same screw; (4) slots and partial arcs not
counted; (5) lengths inferred from depth. Corroboration: Dev Pack ships
"1 × Screw Pack" and "1 × Screwdriver" [store-devpack] — one screw family.
Contrast: Open Duck Mini v2 was M3 + heat-set inserts (`research/raw/odm_bom.csv` row "3D printing M3 inserts") [R1 §16.3].
Inserts vs tapped plastic on the production unit: CANNOT DETERMINE — a
teardown settles it; our rebuild uses M2 heat-set inserts where a thread is
loaded [SPEC §6].

## 6. Mass budget

| item | mass | source |
|---|---|---|
| product, press kit / blog | "under 800 g" | [R1 §2] |
| product, store | 780 g | [store-microduck] |
| boxed shipping weight (robot + controller + battery + cable) | 1200 g | [store-microduck JSON `grams`] |
| MJCF inertial sum, 15 bodies | **737.2 g** | [M joints `mass_g`; R1 §3.2] |
| 15 × XL330 | 270 g (15 × 18 g datasheet) = 37 % of the model | [XL330]; [R1 §4.1] |
| trunk_base body | 199.2 g (plate, shells, cradle, battery, 2 servos, locker, 2 bearings) | [M] |
| head (`jaw_soft` body) | 188.8 g (shells, face, jaw, lips, motor_support, 2 servos, lens, HAT, Radxa, speaker, bearing) | [M] |
| yaw2roll / bearing_roll | 23.0 g × 2 | [M] |
| hip_l / hip_l_2 | 6.19 g × 2 | [M] |
| upper_leg L/R | 48.2 g × 2 | [M] |
| leg / leg_2 | 21.6 g × 2 | [M] |
| ankle L/R | 30.0 g × 2 | [M] |
| neck | 36.8 g | [M] |
| neck_pitch | 5.72 g | [M] |
| yaw_roll_motion | 48.6 g | [M] |
| NP-F550 pack | CANNOT DETERMINE (not in our sources; weigh one, or Sony's sheet) | — |
| Radxa Zero 3W | CANNOT DETERMINE (not on the Radxa page we fetched) | — |
| printed parts, per part | CANNOT DETERMINE until sliced — mesh solid volumes are in [R2 §4.3] (e.g. top_head_shell 29.9 cm³, bottom_head_shell 23.8 cm³, foot 12.2 cm³, left_shell 11.4 cm³) and bound the mass | `cad-print` skill on our rebuilt parts settles it |

The 780 − 737 = 43 g gap between store and model is the unmodelled parts
(cables, screws, mics, NFC, speaker real mass, IMU board) plus the Pi→Radxa
swap; the split is CANNOT DETERMINE without a real unit on a scale.

## 7. Open items from this table (what a rebuild agent should do next)

1. Fix `ce-parts/microduck-shin/component.json` `qty_per_robot` 4 → 2 and SPEC.md §4.1/§4.2 "×2" notes (this doc's qty correction).
2. Commit `dcc39bd` ("9 parts PASS … bearing-roll, yaw2roll, … rigidity plate") claims more than the shelf records: `microduck-bearing-roll`, `microduck-yaw2roll` and `microduck-upper-leg-rigidity-plate` have **empty ledgers and T0 trust.json** at 2026-09-01 23:3x. The ledger is the record; run their refchecks and append the evidence, or the claim stands unproven.
3. Create folders for the 15 remaining "no folder" slugs (rows 4, 5, 15–24, 29–31) — the shells, feet, neck and beak are the whole visible product; face/eye/lens folders now exist at T0.
4. Resolve the 12 remaining joints in `ce-assemblies/microduck` (2 of 14 resolved — both knees).
