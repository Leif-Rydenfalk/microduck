# 02 — Repos and code: what the open source encodes about Microduck's mechanics

Date: 2026-09-01. Clones under `/private/tmp/claude-501/-Users-leifrydenfalk/191ca988-e752-45fb-a6f7-89dde34532e7/scratchpad/microduck/repos/` (abbreviated `repos/` below). Machine-readable companion: `02-kinematics.json` (14 parsed models, 5 STL sets with bounding boxes). Full-precision body/joint tables: `kinematics-tables.txt`. Raw electronics grep: `microduck-elec-grep.txt`.

Trust levels used: **T-official** = in a Pollen/apirrone repo; **T-derived** = computed by me from those files; **T-community** = third-party claim, cited but not verified here.

---

## 0. Headline answers

| Question | Answer |
|---|---|
| Microduck-specific public repos | `pollen-robotics/microduck` (runtime, Apache-2.0), `pollen-robotics/microduck_rl` (RL + **MJCF + 47 STL meshes**, Apache-2.0 code / **CC BY-SA-NC meshes**), `pollen-robotics/microduck-gst-plugins`, HF space `pollen-robotics/microduck-simulator`, HF model `pollen-robotics/microduck-policies` (9 ONNX). Plus apirrone's prototype-era satellites: `microduck_app` (ships **v1, v1.5, alpha** MJCF+STL), `microduck_kinematics_rs`, `microduck_maploc_rs`, `microduck_pet_detect`, `microduck_sounds`. The prototype runtime `apirrone/microduck_runtime` is **gone (404)**; a March-2026 snapshot survives at `TommyZihao/microduck_runtime`. |
| Is Microduck (not just Open Duck Mini) geometry public? | **Yes, as simulation assets**: `microduck_rl/.../robot/microduck/assets/*.stl` — 47 real binary STLs (not LFS pointers, verified with `head -c 20`), authored in **metres** by onshape-to-robot, plus `.part` sidecars naming the Onshape document/element/partId for every part. MJCF gives per-body mass, CoM, full inertia, joint axes/limits, sensor sites. **No** STEP, no editable CAD, no PCB, no BOM from Pollen. |
| Servo | **ROBOTIS Dynamixel XL330** ×15 (`rustypot::servo::dynamixel::xl330::Xl330Controller`, Protocol 2, 1 Mbps). Sub-variant (M288-T vs M077-T) is **not** stated anywhere in Pollen code; BAM model `motor_name="xl330"`; community assumes M288-T (288.35:1). Open Duck Mini v2 used **Feetech STS3215 7.4 V** ×14. |
| Onshape | Microduck document **`804927696f06d877f3f1803e`** (cited in every MJCF header and `.part` file). Open Duck Mini v2 document `64074dfcfa379b37d8a47762` (public, linked in README). |
| Compute | Radxa Zero 3W (RK3566) on the shipped robot; Raspberry Pi Zero 2 W on the prototype (and the `pcb__raspberry_pi_zero_2_w` mesh is still what the CAD carries). |
| IMU | LSM6DSV16X on a custom **`imu_to_dxl` v2** board that sits on the Dynamixel bus as ID 200 (production); BNO055 over I2C on the prototype; a dormant BMI088 on the Robot HAT. |

---

## 1. Repo inventory

### 1a. Official — Pollen Robotics (`gh api orgs/pollen-robotics/repos`: 214 repos; full list `pollen-repos.tsv`)

| Repo | Licence | Commit | Clone path | Contents relevant to mechanics |
|---|---|---|---|---|
| github.com/pollen-robotics/microduck | Apache-2.0 | 590b986 (2026-08-27) | `repos/pollen-robotics_microduck` | Rust workspace: `robotd` (50 Hz loop), `duck-control` (Dynamixel bus, IMU decode, safety), `tofd` (VL53L5CX/L8CX, vendored ST drivers in `tof/vendor/`), `mediad` (IMX219 → WebRTC), `kinematics` (MJCF-driven FK; bundles `kinematics/assets/alpha/robot_walk.xml`), `deploy/` (robotd.toml, **device-tree overlays for the Robot HAT**), `scripts/setup-board.sh`, `policies/*.onnx` (9), `docs/`. No meshes except a baked `robotctl/assets/duck.bin`. |
| github.com/pollen-robotics/microduck_rl | Apache-2.0; **"3D model files are licensed under Creative Commons BY-SA-NC"** (`README.md:196`) | 5946fd9 (2026-09-01) | `repos/pollen-robotics_microduck_rl` | **The geometry source.** `src/mjlab_microduck/robot/microduck/`: 6 MJCF variants + `config_mjcf_*.json` (onshape-to-robot configs), `joints_properties.xml`, `sensors.xml`, `scene*.xml` (keyframes), `ball.xml`, `add_backlash.py`, `assets/` (47 STL + 47 `.part`). Also `robot/xl330_test_bench/` (BAM identification rig, 11 STL, own Onshape element). `microduck_constants.py` (HOME_FRAME, BAM actuator config). |
| github.com/pollen-robotics/microduck-gst-plugins | Apache-2.0 | — | `repos/pollen-robotics_microduck-gst-plugins` | Prebuilt aarch64 GStreamer (Rockchip MPP encoders, webrtcsink). No mechanics. |
| github.com/pollen-robotics/Open_Duck_Blender | Apache-2.0 | — | `repos/pollen-robotics_Open_Duck_Blender` | `open-duck-mini.blend` (16 MB) rig/animation of **Open Duck Mini** for reference-motion recording. Not Microduck. |
| huggingface.co/spaces/pollen-robotics/microduck-simulator | (space) | 1261013 (2026-08-28) | `repos/microduck-simulator` (cloned by coordinator) | Browser sim; `app/public/robot/mjlab/robot_allcollisions{,_rollers}.xml` + meshes copied from microduck_rl; README: "Policies and MJCF model from pollen-robotics/microduck and microduck_rl". |
| huggingface.co/pollen-robotics/microduck-policies | Apache-2.0 | — | (not cloned; file list recorded) | `alpha_ground_pick / alpha_sitstand / alpha_stand / alpha_walking / ball_kick_left / ball_kick_right / roller / roller_crouch / roulade .onnx`. README is empty. |

Other Pollen HF assets: no Microduck datasets; `pollen-robotics/reachy_mini_*` unrelated. `gh api orgs/huggingface/repos` → no duck repos.

### 1b. Official — Antoine Pirrone (`apirrone`, full list `apirrone-repos.tsv`)

| Repo | Licence | Clone path | Contents |
|---|---|---|---|
| apirrone/Open_Duck_Mini | Apache-2.0 | `repos/apirrone_Open_Duck_Mini` (256 MB) | Open Duck Mini **v2** hub: `print/*.stl` (36 printable parts, mm units), `print/mods/` (STEP + 3MF community mods), `mini_bdx/robots/{bdx,open_duck_mini_v2}/robot.{urdf,xml}`, `docs/` (assembly guide, print guide, wiring diagrams PNG/drawio, configure_motors.md, feetech_identification.md, sim2real.md), `experiments/` (BAM STS3215 identification `params_m6.json`). README links Onshape + Google-Sheets BOM (fetched → `open_duck_mini_v2_bom.csv`). |
| apirrone/Open_Duck_Mini_Runtime | (none stated) | `repos/apirrone_Open_Duck_Mini_Runtime` | Python runtime for Pi Zero 2W: `rustypot_position_hwi.py` (`rustypot.feetech(port, 1000000)`, `/dev/ttyACM0`), `imu.py` (`adafruit_bno055.BNO055_I2C`). |
| apirrone/Open_Duck_Playground | (none) | `repos/apirrone_Open_Duck_Playground` | MuJoCo-Playground env; `playground/open_duck_mini_v2/xmls/open_duck_mini_v2.xml` (+backlash variant), `constants.py`. |
| apirrone/Open_Duck_reference_motion_generator | (none) | `repos/apirrone_Open_Duck_reference_motion_generator` | Placo-based gait generator; URDFs for `open_duck_mini`, `open_duck_mini_v2`, `go_bdx`. |
| apirrone/microduck_app | (none) | `repos/apirrone_microduck_app` (95 MB) | PWA companion for the prototype. **`robot_assets/{v1,v1.5,alpha}/robot_walk.xml` + `assets/*.stl`** — the only public copy of the **v1 and v1.5** Microduck geometry. |
| apirrone/microduck_kinematics_rs | (none) | `repos/apirrone_microduck_kinematics_rs` | MJCF-driven FK crate; bundles the same three MJCFs in `assets/{alpha,v1,v1.5}/`. Documents which sites exist per version. |
| apirrone/microduck_maploc_rs | (none) | `repos/apirrone_microduck_maploc_rs` | ToF-based 2D SLAM; `mount` module = VL53L5CX zone-projection LUT. |
| apirrone/microduck_pet_detect | (none) | `repos/apirrone_microduck_pet_detect` | Audio classifier; confirms onboard mic sits on the head; ALSA device `plughw:aic3104`. |
| apirrone/microduck_sounds | (none) | `repos/apirrone_microduck_sounds` | Synth voice. |
| apirrone/duck_gym | (none) | `repos/apirrone_duck_gym` | 2024 Isaac-Gym BDX AMP video only. |
| apirrone/microduck_runtime | — | **404** | The Pi-Zero prototype runtime that `microduck_app`, `microduck_sounds`, `pet_detect`, `maploc` all link to. Removed/private. Snapshot: `TommyZihao/microduck_runtime` (commit dcb9023, 2026-03-19) at `repos/TommyZihao_microduck_runtime`. |

### 1c. Community reverse-engineering repos (`gh search repos microduck` → 50+ hits; `"open duck"` → 100+; most relevant cloned)

| Repo | Licence | Clone path | What it adds | Contradictions vs Pollen files |
|---|---|---|---|---|
| fanhao375/microduck-replica | scripts Apache-2.0; `cad/`+drawings **CC BY-SA-NC** (inherits mesh licence) | `repos/fanhao375_microduck-replica` (102 MB) | `cad/00_…整机装配体.stl` (whole robot, world-transformed, mm, 796 792 tris) + 15 per-rigid-body assembled STLs + `零件对照表.json` (body→source-mesh map); `assembly-drawings/` 7 PNG (exploded views); `scripts/analyze_holes.py` (cylinder-fit hole scanner), `docs/hole_analysis.json` (per-mesh hole dia/depth/coverage), `docs/fastener-reconstruction.en.md`, `docs/hardware-teardown.en.md`, `docs/actuator-selection.en.md`. Claims: **M2 system** (Ø2.2 ×77, Ø4.4 c'bore ×28, Ø1.6 tap ×20, Ø2.4 ×22, Ø2.0 ×12, Ø2.7/2.8 ×20, Ø4.8 ×10, Ø5.4/6.0 ×16 bearing seats); xl330.stl carries 4×Ø2.0 + 8×Ø1.6 (matches XL330 M2 pattern); ~146 structural clearance holes; hole depths 51@0–3 mm, 24@3–5 mm, 4@8–12 mm; bearings 22×16×4 (×11) and 15×10×3 (×3); mass 737.2 g; envelope 144×141×264 mm. | README table still says battery "✅ 索尼 NP-F970" while `model.rs:108` says **NP-F550** and the `np_f970.stl` mesh is 20.6 mm thick (= F550/F570 thickness; a real F970 is ~38 mm). Their own hardware page later concedes "NP-F550/F970 2S". They also assert "M288-T" — not in any Pollen file. |
| SaberOnGo/open-microduck ("OpenMicroDuck") | no LICENSE file; DISCLAIMER + provenance page | `repos/SaberOnGo_open-microduck` | Curated docs (EN/ZH): `hardware/public-bom.md` (evidence-graded inventory), `parameter-reference.md` (motor map, joint limits, 15-body mass table, home pose in degrees), `electronics-and-buses.md`, `research/open-questions-and-conflicts.md` (ledger of unknowns: XL330 sub-variant, final ToF, camera FOV, HAT schematic, imu_to_dxl MCU, NFC IC, mic/speaker, fasteners, harness). No geometry of its own. | Flags the same F550-vs-F970 conflict and the 780 g (store) vs "<800 g" (press) mass. Notes product spec says **two IMUs (body + head)** — consistent with the `head_imu` site in the MJCF. |
| ScrapMeta/microduck-diy | none stated | `repos/ScrapMeta_microduck-diy` (78 MB) | `day1/stl/` 38 STL (the alpha structural set, copied), `microduck_rl_assembly.3mf` / `_exploded.3mf` (Bambu-ready plates), `Microduck_RL_3D_Print_Guide.pdf`: print list with counts (38 kinds / 70 instances), material advice (PETG/ASA for hard parts, TPU 90–95A for `sole_*`, `jaw_soft`, `soft_mouth_top`), official four colourways (Cream #f7e6cb, Graphite #6c6a68, Lavender #bfa9cf, Sky #a9dbe8), buy-not-print list (xl330 ×15, bearings 22×16×4 ×11 + 15×10×3 ×3, HAT, Pi/Radxa, NP-F550, lens, speaker). | Correctly notes the mesh is Pi Zero 2W but production is Radxa; np_f970 placeholder is NP-F550 in production. |
| boris721/microduck-3d | none | `repos/boris721_microduck-3d` | MJCF + 43 STL + `microduck.glb` + `kinematics.json` extracted from the HF space. Descriptions are partly wrong (calls `np_f970` a "NEMA motor"). | — |
| IronSpiderMan/MicroDuckModels, Treescoder/microduck_simulator, mertcookimg/Open_Duck_Mini_Viewer | — | cloned | Browser viewers; mirror the same MJCF/STL. | — |
| mishig/microduck-anatomy (HF space) | no LICENSE | `repos/mishig_microduck-anatomy` | Next.js "holographic anatomy" viewer over `public/robot/mjlab/microduck.glb` + `kinematics.json`. `components/microduck-blueprint.tsx:336-354` hard-codes callouts: XL330 "20 × 34 × 26 mm · 12-bit encoder · TTL bus", "XL330 family confirmed · **M288-T likely / seen on press prototype**", "NP-F550 POWER PACK", "RADXA ZERO 3W ENVELOPE … 1 GB RAM · 32 GB storage · 65 × 30 mm". | Nothing contradicting; the M288-T claim is stated as "likely". |
| joeynyc/awesome-microduck (CC0), ob1-s/awesome-microduck | CC0 / — | cloned | Indexes. States hardware ships Dec 2026, "almost nobody outside Pollen has a physical unit", hardware section: "not open source (no BOM, CAD or PCB files), but the MJCF and STL meshes are public". Lists further repos (osrbot/microduck-ros2-isaac, jvpflum/microduck-lab, x10zyn/microduck-sim-playground, craigm26/duckkit Swift port, littlejohntj/microduck-sim iPhone, ApurvK032/microduck-webxr). | — |
| blublear/open-duck-mini-hat | MIT | `repos/blublear_open-duck-mini-hat` | **KiCad** Pi HAT for Open Duck Mini: `openduckminihat.kicad_{pro,sch,pcb}`; 2×20 Pi header, JST-XH 2.50 mm connectors (6×3-pin, 4×2-pin, 2×4-pin, 1×5-pin): UART, POWER, I2C_0, I2C_1, LEFT/RIGHT FOOT, LEFT/RIGHT EYE, LEFT/RIGHT ANTENNA, FLASHLIGHT, Speaker, PI_SW. Only open PCB in the ecosystem (ODM, not Microduck). | — |
| namaewa-im/Open_Duck_Mini_v2_urdf, jmachuca77/open_duck_mini_description, meetsitaram/open-duck-mini-onshape-to-isaac-sim | BSD-3 / — / Apache-2.0 | cloned | ROS2/Isaac conversions of ODM v2; `meetsitaram` has onshape-to-robot `config.json` pointing at a **different** ODM Onshape doc `4d2197571dde40bdb6b7647f`; `jmachuca77` URDF header cites doc `d7b35ee4f5c6e2f6765ac99d` (v1 mini_bdx). | — |
| kgediya/specs-microduck (MIT), craigm26/duckkit, TommyZihao/microduck_runtime | — | cloned | AR teleop; Swift port; **prototype runtime snapshot** (see §3.4). | — |

---

## 2. Onshape links (all occurrences, file:line)

| Document / workspace / element | Meaning | Where cited |
|---|---|---|
| `804927696f06d877f3f1803e` /w/`5b75db19292e71970de02dee` /e/`ef6e972847fec8d82570b35e` | **Microduck alpha, walking assembly** | `microduck_rl/.../config_mjcf_{walk,walk_backlash,allcollisions,allcollisions_backlash}.json:2`; `robot_walk.xml:3`, `robot_allcollisions.xml:3` (+backlash twins); `microduck_app/robot_assets/alpha/robot_walk.xml:3`; copies in microduck-simulator, boris721, IronSpiderMan, Treescoder |
| same doc /w/`5b75db19…` /e/`ed34b749f5a3718f68024fd5` | **Microduck alpha, roller (wheels) assembly** | `config_mjcf_allcollisions_rollers{,_backlash}.json:2`; `robot_allcollisions_rollers.xml:3` |
| same doc /w/`3df6f6a8dcea50fb5658e3c0` /e/`54c1186243f1b4db10e4bd59` | XL330 BAM test bench | `microduck_rl/.../xl330_test_bench/config.json:2`, `xl330_test_bench.xml:3` |
| same doc /w/`3df6f6a8dcea50fb5658e3c0` /e/`e9ad89ea0c0270c6f03a5522` | **Microduck v1** | `microduck_app/robot_assets/v1/robot_walk.xml:3` |
| same doc /w/`3239ba0df7349fc5129ac49f` /e/`5e56598923b6e0d9c566370f` | **Microduck v1.5** | `microduck_app/robot_assets/v1.5/robot_walk.xml:3` |
| `64074dfcfa379b37d8a47762` /w/`3650ab4221e215a4f65eb7fe` /e/`0505c262d882183a25049d05` | Open Duck Mini v2 (public) | `Open_Duck_Mini/README.md:50`, `docs/assembly_guide.md:17`, `docs/sim2real.md:13` |
| `4d2197571dde40bdb6b7647f` /w/`0073f934…` /e/`6a071f62…` | ODM (community copy) | `meetsitaram_…/config.json:3`, `robot.urdf:3` |
| `d7b35ee4f5c6e2f6765ac99d` /w/`8247700b…` /e/`901fe794…` | mini_bdx v1 | `jmachuca77_open_duck_mini_description/urdf/mini_bdx.urdf:3` |

Per-part Onshape identity (T-official): every `microduck_rl/.../assets/<name>.part` is JSON with `documentId`, `documentMicroversion`, `elementId`, `partId`, `name`. Examples: `xl330.part` → element `e34e27a4a091c95d26a71da8`, partId `JND`, name `"xl330 <11>"`; `rim.part` → element `a48e2e3940da29620aa227db`, partId `RVHD`, documentVersion `f839e201fb05eeec735c386e`. The Microduck document is **not** publicly accessible (only the ODM one is), but these IDs pin exactly which Onshape parts each STL came from.

onshape-to-robot config facts (`config_mjcf_allcollisions.json`): `simplify_stls: true`, `max_stl_size: 1.0` (MB — explains the many 1 048 584-byte meshes = decimated to 20 970 faces), collision kept only for `sole_left/right, leg, power_support, top/bottom_head_shell, jaw, left/right_upper_leg, hip_l, NP-F970, trunk_shell_left/right` (+`tire` for rollers); post-import sed sets `trunk_base pos="0 0 0.12"`, names foot collisions, injects a `<camera name="head_camera" … quat="0 0 -1 0">` at the `head_camera` site. `joint_properties`: default class `chosen_actuator`, `passive*` joints unactuated.

---

## 3. Electronics and servo facts (Microduck, T-official, file:line)

### 3.1 Motor bus
- Servo driver: `duck-control/src/bus.rs:18` `use rustypot::servo::dynamixel::xl330::Xl330Controller;` ; `bus.rs:110` `Xl330Controller::new()`; crate `duck-control/Cargo.toml:33` `rustypot = "1.6.0"`.
- 15 joints: `duck-control/src/model.rs:12` `NUM_JOINTS = 15`. IDs `model.rs:15-19`: left leg **20 21 22 23 24**, neck/head/mouth **30 31 32 33 34**, right leg **10 11 12 13 14**. Names `duck-ipc-proto/src/lib.rs:239-255`: `left_hip_yaw, left_hip_roll, left_hip_pitch, left_knee, left_ankle, neck_pitch, head_pitch, head_yaw, head_roll, mouth, right_hip_yaw, right_hip_roll, right_hip_pitch, right_knee, right_ankle`.
- Mouth = index 9, ID 34, **not in any policy** (`model.rs:28-31`); travel −5°…+30° (`model.rs:62-63`); prototype used −10°…+70° (`TommyZihao…/src/motor.rs:17-18`). `scripts/bake-duck-mesh.py:29-31`: "`mouth` is a servo without an MJCF joint (the jaw is a fixed geom)".
- Baud 1 Mbps: `model.rs:80`; EEPROM asserted at boot `model.rs:89-94`: `return_delay_time=0, baud_rate=3, pwm_slope=255, shutdown=52`. Comment `model.rs:84-86`: "the XL330 ships at 250 … Across 16 devices".
- Port: `deploy/robotd.toml:16-19` `/dev/ttyS2` = Radxa Zero 3W UART2 (`scripts/setup-board.sh:111` overlay `uart2-m0`; `:168` UART2 is also the SoC debug console; `:377` mask `serial-getty@ttyS2`).
- Position gain 200 (`robotd.toml:131`, `safety.rs:75`), limp gain 50 (`safety.rs:76`), loop 50 Hz (`robotd.toml:34`; "inherited from the prototype … Raspberry Pi Zero 2W" `:30`).
- Actuator travel sanity clamp ±π (`safety.rs:47-48`, "real joint limits live in the MJCF").
- Voltage/temperature via registers 144–146, 0.1 V/count (`bus.rs:33-34,45`); position 12-bit, 2048 = 0 rad (`TommyZihao…/motor.rs` tests); velocity 0.229 rpm/count (`motor.rs:61`).
- BAM actuator model (`microduck_rl/.../microduck_constants.py:120-132`): `motor_name="xl330", model="m6", kp_fw=200, vin_range=(6.5, 8.2), vin_drop_gain_range=(0,0.2), vin_min=6.0, delay 3–6 ticks`. MuJoCo-PD fallback `joints_properties.xml:23-28` class `chosen_actuator`: damping 0.053, frictionloss 0.0048, armature 0.0018, kp 0.55, forcerange ±0.96 N·m (≈9.8 kg·cm — consistent with XL330-M288 stall ≈ 0.52 N·m @5 V / higher at 7.4 V).

### 3.2 IMU(s)
- `duck-control/src/imu.rs:1` "The `imu_to_dxl` v2 board (**LSM6DSV16X**)"; rides the Dynamixel bus, ID 200 (`model.rs:78`); block at register 124: 6 B gyro i16 ±500 dps (17.5 mdps/LSB, `imu.rs:47`) + 6 B SFLP quaternion xyz fp16 (`imu.rs:8-13`). Mount quaternion `imu.rs:76-83` `[0.7071, 0, 0.7071, 0]` = +90° about Y ("trunk = [+raw_z, +raw_y, −raw_x]").
- MJCF `imu` site on `trunk_base` at **[−0.021, 0.0001, −0.0147] m** (`robot_walk.xml`, `sensors.xml` binds framequat/gyro/accelerometer to it); a second `head_imu` site on `jaw_soft` at [0.0152, 0.0001, −0.0511]. Product spec (per community) says two IMUs.
- Prototype: BNO055 over I2C (`TommyZihao…/README.md:3`, `Cargo.toml` `bno055 = "0.4"`); alpha app MJCF still has an `imu_bno` site on `trunk_base` at [−0.032, 0.014, 0.0431] (`microduck_app/robot_assets/alpha/robot_walk.xml:109`).
- Dormant **BMI088** at I2C 0x19/0x68 on the Robot HAT (`deploy/audio/i2c3-pihat.dts:11,31`).

### 3.3 Compute, HAT, camera, ToF, audio, battery
- Board: Radxa Zero 3W / RK3566, Armbian, vendor kernel 6.1.115 (`.cargo/config.toml:3`; `deploy/audio/i2c3-pihat.dts:46` `compatible = "radxa,zero-3w", "rockchip,rk3566"`; `deploy/overlays/rk3568-npu-enable.dts`). Pi-Zero form factor — the CAD mesh is literally `pcb__raspberry_pi_zero_2_w.stl` (65×30×1.6 mm).
- "Pollen Robotics RPI Robot HAT" (`deploy/audio/aic3104-i2c3.dts:4-6`; mesh `elec_rpi_robot_hat_pcb.stl` 65.0×30.0×0.84 mm, sits in the **head** body `jaw_soft`): I2C3-M0 on header pins 3/5 (GPIO1_A0 SDA / GPIO1_A1 SCL) @400 kHz, codec **TLV320AIC3104** @0x18, BMI088 @0x19/0x68, ToF via **Stemma "J5"** @0x29, pull-ups R12/R13 10 kΩ, battery power enters through the HAT (`i2c3-pihat.dts:5-34`). Audio: I2S3, fixed 12 MHz MCLK (`aic3104-i2c3.dts:33-37`); ALSA `plughw:aic3104` (`robotd.toml:259`). Mic on the head (pet_detect README).
- Camera: Raspberry Pi Camera v2 / **IMX219** overlay `radxa-zero3-rpi-camera-v2` (`docs/project/media-bringup.md:65`; probe log `:312` "imx219 2-0010: Model ID 0x0219"); pinned 1920×1080@30 mode, ISP-scaled to 720p30 (`robotd.toml:372-378`, `mediad/src/exposure.rs:71`); **mounted upside-down / a quarter turn off** (`media-bringup.md:337,472` rotation 180). MJCF: `head_camera` site on `jaw_soft` at [0.0155, −0.0001, −0.0733], camera quat `0 0 -1 0`; meshes `m12_lens_holder.stl` (24×14.8×16 mm) and `lens.stl` (Ø16.9 × 18.9 mm) — an **M12 lens** on the IMX219 board.
- ToF: `tof/vendor/vl53l5cx` and `vl53l8cx` both vendored; `tof/src/main.rs:84-87` addresses 0x29 (default) then 0x52 (prototype moved it when a BNO wanted 0x29); 8×8 @15 Hz (`main.rs:104-107`); 45°×45° FOV (`kinematics/src/tof.rs:27-33`); reported generation string e.g. `VL53L8CX` (`duck-ipc-proto/src/lib.rs:3187`). MJCF `tof` site on `jaw_soft` at [0.0135, 0.0224, −0.0733] (22 mm lateral of the camera). Theremin band 0.10–0.70 m (`robotd.toml:290-291`).
- Battery: `model.rs:108-113` "**NP-F550, 2S Li-ion**" full 8.2 V / empty-under-load 6.6 V; nominal 7.4 V (`robotd.toml:162`); no fuel gauge/ADC — pack voltage = servo-reported input voltage (`model.rs:101-106`). CAD placeholder mesh `np_f970.stl` measures **38.6×20.6×70.8 mm** — that is NP-F550/F570 thickness (F970 is ~38 mm thick), so the mesh name is misleading and the bay is sized for an F550-class pack.
- NPU: RKNN `duck_detect.rknn` at 2 Hz thermal limit (`robotd.toml:330-332`). Bluetooth gamepad (Xbox), Wi-Fi WebRTC.
- Speaker mesh `speaker.stl` is a 35×25×7 mm box placeholder (12 faces).

### 3.4 Prototype runtime (T-official snapshot via `TommyZihao/microduck_runtime`, orig. `apirrone/microduck_runtime`, now 404)
`README.md:3` "Runs on Raspberry Pi Zero 2W with 15 Dynamixel XL330 motors and a BNO055 IMU". `src/motor.rs:11` `NUM_MOTORS = 14` (+ mouth ID 34 `:14`), `:22-37` same ID map, `:42-58` older home pose (hip_pitch ±0.6, knee ∓1.2, ankle ±0.6, neck −0.5, head 0.5 — the v1.5 posture), `Cargo.toml` `rustypot 1.4.2`, `bno055 0.4`, `ort 2.0.0-rc.11`; `rpi_setup/config.txt` `enable_uart=1`, `dtoverlay=miniuart-bt`, `dtparam=i2c_arm=on`.

### 3.5 Open Duck Mini v2 (ancestor, T-official)
- Servos: **Feetech STS3215 7.4 V "19 kg·cm"** ×14 (`open_duck_mini_v2_bom.csv`; `experiments/v2/*.py` `FeetechSTS3215IO`; MJCF class `sts3215` `open_duck_mini_v2.xml:45-49` damping 0.56, frictionloss 0.068, armature 0.027, kp 13.37, forcerange ±3.23 N·m) + 2× 9 g hobby servos (antennas). IDs identical to Microduck minus the mouth (`docs/configure_motors.md`).
- Bus: Waveshare "Bus Servo Adapter (A)" USB, `/dev/ttyACM0` @1 Mbps (`Open_Duck_Mini_Runtime/.../rustypot_position_hwi.py:9,77`). IMU BNO055 I2C (`imu.py:30`). Pi Zero 2W. Power: 2×18650 Molicel P30B 2S + BMS + 5 V UBEC, XT30. Foot switches SS-10. BOM total €398 (+€34 "expression package": speaker, LEDs, projector reflector, mic, Pi camera). Bearings ×3.
- Community KiCad HAT: `blublear_open-duck-mini-hat/openduckminihat.kicad_sch` (MIT).

---

## 4. Kinematic tree — Microduck alpha (T-official from `microduck_rl/.../robot_allcollisions_rollers.xml`, superset model; walking model identical minus the four wheels, with `ankle_left/right` replacing `ankle_l_v1/r_v1`)

Frame: MJCF, `trunk_base` free-joint at z = 0.12 m, +x forward, +z up. Total in-model mass **0.7372 kg** (walk/allcollisions) / 0.7368 kg (rollers); 15 rigid bodies; 14 hinges, all axis `0 0 1` in the child frame; all actuated hinges class `chosen_actuator`.

### 4.1 Joints (pos/quat = child body frame in parent; range from `autolimits`)

| Joint | Parent → child | body pos [m] | body quat [w x y z] | Range rad | Range ° |
|---|---|---|---|---|---|
| left_hip_yaw | trunk_base → yaw2roll | 0.006, 0.0175, −0.005 | 0, −.7071, −.7071, 0 | −0.4363, 0.5236 | −25, +30 |
| left_hip_roll | yaw2roll → hip_l | 0, 0.0165, 0.0125 | .7071, −.7071, 0, 0 | ±0.3840 | ±22 |
| left_hip_pitch | hip_l → upper_leg_left | 0.025, 0, −0.0185 | .5, −.5, .5, −.5 | ±1.5708 | ±90 |
| left_knee | upper_leg_left → leg | 0.022, 0.0358, −0.004 | 0, .7071, .7071, 0 | ±1.5708 | ±90 |
| left_ankle | leg → ankle_left | 0, 0.042, −0.026 | 0, 1, 0, 0 | ±1.5708 | ±90 |
| neck_pitch | trunk_base → neck | 0.026, 0.0145, 0.0324 | 0, 0, .7071, −.7071 | −1.5708, 1.0472 | −90, +60 |
| head_pitch | neck → neck_pitch | 0, −0.05, 0 | 0, 1, 0, 0 | ±1.5708 | ±90 |
| head_yaw | neck_pitch → yaw_roll_motion | 0, 0.0187, −0.0145 | 0, 0, −.7071, −.7071 | ±2.9671 | ±170 |
| head_roll | yaw_roll_motion → jaw_soft | −0.0179, 0, 0.0145 | .7071, 0, −.7071, 0 | ±0.4363 | ±25 |
| right_hip_yaw | trunk_base → bearing_roll | 0.006, −0.0175, −0.005 | 0, .7071, .7071, 0 | −0.5236, 0.4363 | −30, +25 |
| right_hip_roll | bearing_roll → hip_l_2 | 0, 0.0165, 0.0125 | 0, 0, .7071, .7071 | ±0.3840 | ±22 |
| right_hip_pitch | hip_l_2 → upper_leg_right | 0.025, 0, −0.0185 | .5, −.5, .5, −.5 | ±1.5708 | ±90 |
| right_knee | upper_leg_right → leg_2 | −0.022, 0.0358, −0.004 | 0, 1, 0, 0 | ±1.5708 | ±90 |
| right_ankle | leg_2 → ankle_right | −0.042, 0, −0.026 | 0, −.7071, −.7071, 0 | ±1.5708 | ±90 |
| passive_LF_wheel / passive_LR_wheel | ankle_l_v1 → tire / tire_2 | −0.0395 / +0.0255, −0.0325, −0.0147 | 1 0 0 0 | free | rollers only |
| passive_RF_wheel / passive_RR_wheel | ankle_r_v1 → tire_3 / tire_4 | +0.0395 / −0.0255, −0.0325, −0.0145 | 0 0 1 0 | free | rollers only |

Derived link lengths (T-derived): hip-yaw axes are 35 mm apart laterally (y = ±0.0175); hip_roll→hip_pitch offset 25 mm; **thigh** (hip_pitch→knee) = |(0.022, 0.0358, −0.004)| ≈ 42.2 mm; **shank** (knee→ankle) = |(0, 0.042, −0.026)| ≈ 49.4 mm; neck_pitch→head_pitch 50 mm; head_pitch→head_yaw ≈ 23.7 mm; head_yaw→head_roll ≈ 23.0 mm; roller wheelbase 65 mm, track = ankle spacing.

Home pose (`microduck_constants.py:73-97`, `model.rs:39-55`, `scene.xml:30-40` "STAND2"): hip_roll ∓0.0873 (5°), hip_pitch ∓0.4579 (26.24°), knee ∓0.0049, ankle ±0.4530 (25.95°), neck_pitch = head_pitch = 0.3491 (20°). Keyframes SIT (z 0.07) and FOLD in `scene.xml:41-56`.

### 4.2 Bodies (mass, CoM in body frame, full inertia ixx iyy izz ixy ixz iyz, meshes)

| Body | Parent | Mass kg | CoM [m] | Inertia [kg m²] | Visual meshes (× = repeated) | Collision |
|---|---|---|---|---|---|---|
| trunk_base | world | 0.19922 | −0.0226, 0, 0.0028 | 1.240e-4, 1.459e-4, 1.154e-4, 7.2e-8, −2.07e-5, 1.3e-7 | trunk_base, left_shell, right_shell, power_support, np_f970, banana_pcb_locker, xl330 ×2, bearing 22×16×4 ×2 | power_support (self-only) |
| yaw2roll | trunk_base | 0.02304 | 0, 0.001, 0.0169 | 4.20e-6, 3.42e-6, 2.33e-6 | yaw2roll, xl330, bearing_roll, bearing 22×16×4 | — |
| hip_l | yaw2roll | 0.00619 | 0.0148, 0, −0.0083 | 8.61e-7, 1.16e-6, 6.52e-7 | hip_l, bearing 22×16×4 | — |
| upper_leg_left | hip_l | 0.04821 | 0.0068, 0.0229, 0.0135 | 1.69e-5, 1.04e-5, 1.98e-5, −4.4e-6 | upper_leg_left, upper_leg_rigidity_plate, xl330 ×2, bearing 22×16×4 | — |
| leg | upper_leg_left | 0.02158 | 0, 0.0319, −0.0095 | 5.25e-6, 2.16e-6, 4.34e-6 | leg, xl330 | leg (self-only) |
| ankle_left (walk) / ankle_l_v1 (rollers) | leg | 0.03002 | −0.0062, −0.0137, −0.0157 | 5.92e-6, 1.12e-5, 7.74e-6 | ankle_left, foot_left, sole_left, bearing 15×10×3 (rollers: ankle_l_v1, roller_blade, rim ×2) | sole_left = `left_foot_collision` |
| neck | trunk_base | 0.03684 | 0, −0.025, 0.0142 | 1.73e-5, 3.13e-6, 1.64e-5 | neck ×2, xl330 ×2 | — |
| neck_pitch | neck | 0.00572 | 0, 0.0117, −0.0145 | 1.09e-6, 9.67e-7, 5.12e-7 | neck_pitch, bearing 22×16×4 | — |
| yaw_roll_motion | neck_pitch | 0.04860 | −0.0002, −0.005, 0.0178 | 6.98e-6, 8.10e-6, 9.58e-6 | yaw_roll_motion, xl330, bearing 22×16×4 ×2 | — |
| jaw_soft (head) | yaw_roll_motion | **0.18877** | 0.0046, 0.0012, −0.0325 | 3.21e-4, 2.54e-4, 1.50e-4 | top_head_shell, bottom_head_shell, face_part, jaw, jaw_soft, soft_mouth_top, motor_support, xl330 ×2, m12_lens_holder, lens, noenoeil, elec_rpi_robot_hat_pcb, pcb__raspberry_pi_zero_2_w, speaker, bearing 15×10×3 | jaw, shells |
| bearing_roll / hip_l_2 / upper_leg_right / leg_2 / ankle_right | mirrored | 0.02304 / 0.00619 / 0.04821 / 0.02158 / 0.03003 | mirrored | mirrored | mirrored | mirrored |
| tire ×4 (rollers) | ankle_*_v1 | ~0 | — | — | tire | tire |

Sites: `imu` (trunk_base, −0.021 0.0001 −0.0147), `head_imu`, `head_camera`, `tof`, `mouth_tip` (jaw_soft, −0.0081 0 −0.0777), `left_foot`/`right_foot` (ankle, 0 ∓0.0238 −0.0141). Full precision in `kinematics-tables.txt` and `02-kinematics.json`.

**Head is 25 % of robot mass (189 g) and the compute/HAT/battery-less head carries the Pi/HAT meshes** — the electronics stack lives in the head, the NP-F550 in the trunk (T-derived from mesh membership).

### 4.3 Meshes — `microduck_rl/.../assets/` (47 STL, binary, metres; bounding boxes T-derived with trimesh; all watertight)

| Mesh | Extent mm (x,y,z) | Vol cm³ | Note |
|---|---|---|---|
| xl330 | 29.0 × 20.0 × 34.0 | 15.68 | Dynamixel XL330 incl. horn (datasheet body 20×34×26) |
| seeed_bearing__configuration__22x16x4 | Ø22 × 4 (ID 16) | 0.49 | ×11 in robot |
| seeed_bearing__configuration_default | Ø15 × 3 (ID ~10) | 0.19 | ×3 (ankles, head) |
| np_f970 | 38.6 × 20.6 × 70.8 | 51.56 | NP-F550-class envelope |
| pcb__raspberry_pi_zero_2_w | 65.0 × 1.6 × 30.0 | 3.02 | Pi Zero / Radxa Zero footprint |
| elec_rpi_robot_hat_pcb | 65.0 × 30.0 × 0.84 | 1.57 | Robot HAT |
| trunk_base | 57.0 × 36.0 × 3.0 | 1.42 | plate |
| left_shell / right_shell | 33.7 × 80.9 × 41.7 | 11.4 | trunk shells (replace `trunk_shell_left/right`) |
| power_support | 54.5 × 17.0 × 83.5 | 10.49 | battery/power bracket |
| banana_pcb_locker | 54.1 × 3.8 × 6.7 | 0.46 | |
| yaw2roll | 23.0 × 25.8 × 20.5 | 2.82 | hip yaw→roll bracket |
| bearing_roll | 23.0 × 3.0 × 40.0 | 0.63 | |
| hip_l | 32.5 × 34.5 × 19.0 | 4.53 | |
| upper_leg_left/right | 28.0 × 47.7 × 61.0 | 4.15 | |
| upper_leg_rigidity_plate | 1.0 × 45.0 × 58.1 | 0.75 | 1 mm plate (sheet?) |
| leg | 7.95 × 20.0 × 58.0 | 3.41 | shank |
| ankle_left/right | 39.5 × 36.5 × 25.5 | 7.88 | |
| ankle_l_v1/r_v1 | 39.5 × 46.5 × 25.4 | 6.69 | roller ankle |
| foot_left/right | 40.1 × 54.0 × 16.9 | 12.18 | hard foot |
| sole_left/right | 41.1 × 54.0 × 12.9 | 6.25 | TPU sole = contact geom |
| neck | 2.0 × 20.0 × 11.0 | 0.40 | 2 mm side plate ×2 |
| neck_pitch | 35.0 × 18.0 × 27.7 | 4.11 | |
| yaw_roll_motion | 34.0 × 35.9 × 22.5 | 4.56 | |
| top_head_shell | 91.8 × 122.7 × 46.3 | 29.87 | |
| bottom_head_shell | 91.8 × 116.8 × 20.1 | 23.80 | |
| face_part | 87.7 × 12.5 × 44.6 | 5.82 | |
| jaw | 91.4 × 68.7 × 29.5 | 9.36 | beak |
| jaw_soft / soft_mouth_top | 87.7 × 32.2 × 8.4 / 87.8 × 32.6 × 3.3 | 18.6 / 2.7 | TPU beak pads |
| motor_support | 73.5 × 54.2 × 18.8 | 7.52 | head motor bracket |
| m12_lens_holder / lens | 24 × 14.8 × 16 / 16.9 × 18.9 × 16.9 | 1.10 / 2.80 | camera |
| noenoeil | 30 × 9.5 × 30 | 4.25 | eye |
| speaker | 35 × 25 × 7 | 6.13 | placeholder box |
| roller_blade / rim / tire | 40.5×73×30.4 / Ø20.2×7.6 / Ø30×7.6 | 11.8 / 1.03 / 2.81 | roller kit |

Head envelope ≈ 92 × 123 mm; whole robot per fanhao375 ≈ 144 × 141 × 264 mm (T-community, consistent with 25 cm product height).

### 4.4 Version history encoded in `microduck_app/robot_assets` (T-official)
| Version | Onshape element | Mass | Bodies | Distinguishing meshes |
|---|---|---|---|---|
| v1 | e9ad89ea… (w/3df6f6a8…) | 0.678 kg | 15 | Open-Duck-Mini-style parts: `roll_motor_top/bottom`, `left/right_roll_to_pitch`, `head_pitch_to_yaw`, `head_yaw_to_roll`, `leg_plate`, `foot`+`foot_tpu_bottom`, `mouth`, `camshaft`, `electronics_hub`, `long_neck_plate1/2`; sites `torso_camera`, `head_camera`, `imu`. Joint ranges differ (knee −110°…0, hip_roll ±40°). |
| v1.5 | 5e565989… (w/3239ba0d…) | 0.646 kg | 17 (jaw + rod, 2 passive joints, 2 `connect` equalities = **4-bar beak linkage** driven by servo) | `battery_holder`, `cam_support`, `head_plate`, `head_shell`, `pitch_to_yaw`, `yaw_roll`, `mouth_roof`, `mouth_tongue`, `neck_support`, `motor_cap`, `noenoeil`, `rod`. `torso_camera` site at trunk front. |
| alpha (shipping) | ef6e9728… (w/5b75db19…) | 0.744 (app) / 0.737 (rl) kg | 15 | as §4.3; jaw is a fixed geom, `tof`/`head_imu` sites added, `torso_camera` removed. |

### 4.5 Open Duck Mini v2 (ancestor) tree — `Open_Duck_Playground/.../open_duck_mini_v2.xml` (T-official)
Total 2.107 kg; `trunk_assembly` 0.699 kg, `head_assembly` 0.407 kg. Joint origins: hip_yaw at (−0.019, ±0.035, 0.0459); hip_roll offset (0.019, 0, −0.046); hip_pitch (0.074, 0, 0.035); **thigh 78.65 mm** (knee at (0, −0.0787, 0)); **shank 78.65 mm**; neck_pitch at (0.001, 0.019, 0.090); head chain 66 / 57 / 41 mm. Limits: hip_yaw ±30°, hip_roll ±25°, hip_pitch −70…+30°, knee ±90°, ankle ±90°, neck_pitch −20…+65°, head_pitch ±45°, head_yaw ±160°, head_roll ±30°. 36 printable STLs in `print/` (mm units; e.g. `head.stl` 199.8×197.3×59.4 mm, `trunk_top.stl` 125.5×100.7×41 mm — see `02-kinematics.json["stl_bboxes"]["Open_Duck_Mini/print"]`). Print guide: PLA 15 % infill except `foot_bottom_tpu` (TPU 40 %). Assembly uses M3 inserts, M3×6/M3×10 screws, Loctite 243 on motor screws.

Lineage: Microduck keeps ODM's ID scheme (+34 mouth), joint naming, BAM/onshape-to-robot pipeline and 50 Hz loop, but halves the size (thigh 42 vs 79 mm), swaps STS3215 (3.2 N·m, 55 g) for XL330 (0.96 N·m cal., 18 g), M3 for M2 hardware, 18650 pack for NP-F550, Pi Zero 2W for Radxa Zero 3W, BNO055 for LSM6DSV16X-on-bus.

---

## 5. What is NOT in the code (open items for the RE project)
1. XL330 sub-variant (M288-T vs M077-T) — never named; only "xl330". Calibrated forcerange 0.96 N·m and the 288-ish behaviour favour **M288-T** (community consensus, mishig "seen on press prototype").
2. Screw sizes — no BOM; fanhao375's hole scan says M2 (Ø2.2/Ø4.4 c'bore/Ø1.6 tap) with a few M2.5; STL-derived, unverified here.
3. Bearings — only geometry: 22×16×4 (×11) and ~15×10×3 (×3) named "seeed_bearing" (Seeed Studio part?).
4. `imu_to_dxl` v2 schematic/MCU, Robot HAT schematic, NFC IC, mic/speaker part numbers, harnesses.
5. Production battery mesh vs name (F550 vs F970) and whether the Radxa replaces the Pi Zero mesh 1:1 (same 65×30 footprint).
6. Camera lens FOV; ToF final generation (L5CX vs L8CX both supported).
7. The Microduck Onshape document is private; the ODM one is public.

## 6. Files written
- `research/02-repos-and-code.md` (this)
- `research/02-kinematics.json` — 14 parsed models (MJCF: bodies w/ mass/CoM/inertia/meshes/collision, joints w/ parent/child/pos/quat/axis/range, sites, cameras, actuators, equality; URDF: links/joints w/ origin xyz rpy, axis, limits) + STL bboxes for 5 mesh sets + `_meta` (Onshape IDs, servo, DXL IDs)
- `research/kinematics-tables.txt` — full-precision tables for alpha walk / rollers / ODM v2
- `research/open_duck_mini_v2_bom.csv` — Google-Sheets BOM export
- `research/microduck-elec-grep.txt` — 2 054 hardware-keyword hits with file:line
- `research/pollen-repos.tsv`, `research/apirrone-repos.tsv`
- `parse_models.py` + `venv/` (trimesh 5.1.0) in `scratchpad/microduck/`
