# Microduck (Pollen Robotics / Hugging Face) — product & specification dossier

Compiled 2026-09-01 for a mechanical reverse-engineering project. Every fact carries a source ID (see §0) and, where possible, a verbatim quote. Confidence tags: **T-official** (Pollen page/store/press kit/blog), **T-source** (Pollen's own open-source code/docs on GitHub or HF), **T-press** (third-party journalism), **T-community** (third-party reverse-engineering), **T-derived** (computed here from official files).

Raw downloads used for this dossier are in `research/raw/` (MJCF, READMEs, design docs, store JSON, device trees, STL meshes, HN thread JSON, Open Duck Mini BOM CSV).

---

## 0. Sources (URLs fetched)

| ID | URL | Note |
|---|---|---|
| S1 | https://pollen-robotics.com/microduck/ | product page (HTML text extracted to raw/product_page.txt) |
| S2 | https://pollen-robotics.com/microduck/press-kit/ | press kit + spec sheet (raw/presskit.txt) |
| S3 | https://pollen-robotics.com/microduck/blog/introducing-microduck/ | "Meet Microduck", 2026-08-27 (raw/blog.txt) |
| S4 | https://pollen-robotics.com/microduck/blog/ | blog index (1 post) |
| S5 | https://pollen-robotics.com/ | homepage |
| S6 | https://store.pollen-robotics.com/products/microduck (+ `.json`) | Shopify listing, EUR pricing, shipping weight |
| S7 | https://store.pollen-robotics.com/products/dev-pack (+ `.json`) | Dev Pack |
| S8 | https://store.pollen-robotics.com/products/accessory-pack (+ `.json`) | Accessory Pack |
| S9 | https://store.pollen-robotics.com/products/charger-pack (+ `.json`) | Charger Pack |
| S10 | https://store.pollen-robotics.com/collections/all | catalogue |
| S11 | https://github.com/pollen-robotics/microduck (README, docs/README.md, docs/design/robotd-design.md, docs/design/architecture.md, docs/project/media-bringup.md, docs/project/npu-bringup.md, docs/project/roadmap.md, docs/robot/cheatsheet.md, docs/robot/install-dev.md, duck-control/src/{model,imu,bus}.rs, duck-ipc-proto/src/lib.rs, tof/src/{lib,main}.rs, deploy/robotd.toml, deploy/audio/i2c3-pihat.dts, deploy/audio/aic3104-i2c3.dts) | official runtime (Rust) |
| S12 | https://github.com/pollen-robotics/microduck_rl (README, LICENSE, src/mjlab_microduck/robot/microduck/{robot_walk.xml, robot_allcollisions_rollers.xml, joints_properties.xml, sensors.xml, scene_rollers.xml, additional.xml, assets/*.stl}, robot/microduck_constants.py) | official RL / MJCF / meshes |
| S13 | https://huggingface.co/pollen-robotics/microduck-policies (via HF API) | 9 shipped ONNX policies |
| S14 | https://huggingface.co/spaces/pollen-robotics/microduck-simulator | browser sim ("Microduck Sandbox") |
| S15 | https://github.com/apirrone/Open_Duck_Mini (README main + v2, docs/print_guide.md, docs/assembly_guide.md, docs/prepare_robot.md) | Open Duck Mini |
| S16 | Open Duck Mini v2 BOM Google Sheet (gviz CSV export of 1gq4iWWHEJVgAA_eemkTEsshXqrYlFxXAPwO515KpCJc) | raw/odm_bom.csv |
| S17 | https://github.com/apirrone/Open_Duck_Mini_Runtime | ODM runtime |
| S18 | https://www.cnx-software.com/2026/08/28/microduck-a-duck-like-biped-robot-designed-for-physical-ai-experimentation-and-fun/ | |
| S19 | https://techcrunch.com/2026/08/27/hugging-face-is-selling-a-cute-399-open-source-duck-robot-microduck/ | |
| S20 | https://www.engadget.com/2245407/huggingface-and-pollen-robotics-opn-pre-orders-for-the-microduck-robot/ | |
| S21 | https://www.marktechpost.com/2026/08/28/pollen-robotics-hugging-face-microduck-399-open-source-rl-biped-robot/ | |
| S22 | https://interestingengineering.com/ai-robotics/new-robot-duck-learn-from-its-mistakes | |
| S23 | https://www.popsci.com/technology/microduck-robot-fall-learn-new-skills/ | |
| S24 | https://www.theregister.com/ai-and-ml/2026/08/27/hugging-face-offers-399-robot-duck-to-help-you-quack-the-ai-code/5293011 | |
| S25 | https://www.eesel.ai/blog/microduck | |
| S26 | https://www.explainx.ai/blog/microduck-hugging-face-399-open-source-rl-robot-august-2026 | |
| S27 | https://www.androidauthority.com/hugging-face-launches-microduck-3704139/ | |
| S28 | https://kingy.ai/blog/hugging-face-microduck-physical-ai-robot/ | |
| S29 | https://byteiota.com/hugging-face-microduck-399-open-source-robot-with-full-rl-stack/ | |
| S30 | https://hn.algolia.com/api/v1/items/49462763 (+ search API) | HN launch thread (raw/hn.json) |
| S31 | https://emanual.robotis.com/docs/en/dxl/x/xl330-m288/ | XL330-M288-T datasheet |
| S32 | https://spectrum.ieee.org/video-friday-microduck-robot | |
| S33 | https://thenextweb.com/news/hugging-face-microduck-399-open-source-robot | |
| S34 | https://gagadget.com/en/723594-hugging-faces-399-microduck-is-a-tiny-open-source-robot-you-can-actually-train/ | |
| S35 | https://www.ibtimes.com.au/hugging-face-microduck-open-source-robot-1874678 | |
| S36 | https://www.techeblog.com/hugging-face-pollen-robotics-microduck-robot/ | |
| S37 | https://www.progressiverobot.com/2026/08/27/microduck-hugging-face-pollen-robotics-399-preorder/ | |
| S38 | https://www.howtogeek.com/hugging-face-microduck-duck-robot-launch/ | |
| S39 | https://www.gadgetreview.com/hugging-faces-399-robot-duck-bets-on-crowdsourced-ai | |
| S40 | https://www.heise.de/en/news/Microduck-The-duck-robot-from-France-11434364.html | |
| S41 | https://github.com/joeynyc/awesome-microduck | community index |
| S42 | https://github.com/fanhao375/microduck-replica (README.en.md, docs/hardware-teardown.en.md, docs/actuator-selection.en.md, docs/fastener-reconstruction.en.md) | community RE (raw/community/) |
| S43 | https://github.com/SaberOnGo/open-microduck (docs/en/hardware/{parameter-reference,electronics-and-buses,community-bom-reconstruction}.md, docs/en/research/open-questions-and-conflicts.md) | community RE (raw/community/) |
| S44 | https://github.com/ScrapMeta/microduck-diy | community build log |
| S45 | https://radxa.com/products/zeros/zero3w/ | Radxa Zero 3W specs |
| S46 | https://hackaday.com/2025/04/05/disneys-bipedal-bdx-series-droid-gets-the-diy-treatment/ | ODM coverage |
| S47 | https://deepwiki.com/varga0725/duck_sim/7.1-open-duck-mini-v2-robot-model | ODM v2 model |
| S48 | https://explainx.ai/blog/gemma-4-open-duck-mini-robot-on-device-ai-2026 | ODM Gemma 4 demo |
| S49 | https://www.tindie.com/products/wsk/open-duck-mini-v2-robot/ ; https://cereboto.com/product/open-duck-mini-v2/ | ODM third-party kits |
| S50 | https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=RAtzEyGBGFU | launch film title |
| S51 | https://www.digitaltrends.com/... (via search snippet only; direct fetch returned empty) | |
| S52 | https://www.axios.com/2026/08/27/hugging-face-debuts-microduck-a-399-robot (via search snippet; direct fetch 403) | |
| S53 | https://docs.pollen-robotics.com/ | Reachy 2 docs only — no Microduck section |

Fetch failures worth knowing: Bloomberg (paywall), Yahoo/Tom's Guide (403), TechRadar (signup wall), Axios (403), Digital Trends (empty body), huggingface.co pages (domain blocked for WebFetch; HF API via curl worked), apirrone/microduck_runtime (404 — private), docs.pollen-robotics.com has no Microduck docs (404 on /blog/, no duck content).

---

## 1. Identity, makers, launch

- **Name:** Microduck. Tagline: "Made to move · Ready to learn" / "A 25 cm open-source biped you train yourself with reinforcement learning. Playable out of the box." [S1, T-official]
- **Maker:** "Pollen Robotics builds open-source robots from Bordeaux, France. Founded in 2016 by former Inria researchers, the team joined Hugging Face in April 2025 and is its robotics team. Microduck is their second consumer robot, after Reachy Mini." [S2]
- **Launch:** "Pre-orders open August 27, 2026 ★ $399 before taxes and shipping ★ Open source" [S1, S2]. Blog dated "August 27, 2026 · 6 min read" [S3].
- **Core team (blog byline):** "Matthieu Lapeyre, Thomas Wolf, Antoine Pirrone, Augustin Crampette, Coralie Deplane, Anne Charlotte Passanisi"; photo caption "Microduck's core team: Antoine, Augustin, Matthieu, Coralie, and Anne-Charlotte" [S3].
- **Launch film:** YouTube RAtzEyGBGFU, title "We made a new robot.", channel Pollen Robotics [S50]. Product page: "Play the film · 0:51" [S1].
- **Positioning:** "Microduck is not Reachy Mini with legs." … "Reachy Mini is a platform for AI that interacts, while Microduck is a platform for AI that acts." [S3]
- **Reachy Mini context:** "more than 10,000 of them have made their way to people around the world." [S3]
- **Hacker News:** story id 49462763 "Microduck" → pollen-robotics.com/microduck/, 780 points, 252 comments, created 2026-08-27T10:57:56Z [S30]. (eesel quotes "763 points and 246 comments in about two days" [S25] — an earlier snapshot.)

---

## 2. Official headline specification (press kit "The spec sheet")

Verbatim from [S2] (press kit), with store [S6] and blog [S3] variants:

| Item | Verbatim |
|---|---|
| Motors | "15 degrees of freedom, across articulated legs, head and neck" [S2]; "15 motors for whole-body movement" [S6] |
| Dimensions | "25 cm tall, 14 cm wide" [S2]; "25 cm tall, 780 g" [S6] |
| Weight | "Under 800 g" [S2]; "It weighs less than 800 g" [S3]; "780 g" [S6] |
| Compute | "Rockchip RK3566 with AI accelerator" [S2]; "Rockchip RK3566 + AI accelerator" [S6] |
| Memory | "1 GB RAM, 32 GB storage" [S2] |
| Vision | "Front camera, with a dedicated camera-use indicator inspired by classic REC lights" [S2]; "Wide-angle front camera" [S6] |
| Motion sensing | "2 IMUs, one in the body and one in the head" [S2] |
| Range sensing | "Compact LiDAR, an 8x8 time-of-flight matrix" [S2]; "Compact 8×8 ToF LiDAR" [S6] |
| Physical interaction | "Articulated grasping beak" [S2] |
| Audio | "Microphones and speaker, with a per-robot generated voice" [S2] |
| NFC | "2 antennas, one in the head and one in the beak" [S2] |
| Connectivity | "Wi-Fi and Bluetooth" [S2] |
| Battery | "Removable NP-F550 camera battery, 2600 mAh, around one hour of runtime depending on use" [S2]; "Removable NP-F550 battery (approx. 1 hour battery life)" [S6] |
| In the box | "Game controller, playable before writing any code, plus autonomous behaviours at launch" [S2]; "Robot, battery, USB-C cable, game controller." [S1] |
| Policy loop | "50 Hz Onboard policy loop" [S1, S2] |
| Trained moves | "7 Trained moves in the box" [S1, S2] |
| Software | "Open-source SDK with virtual training environments, RL training scripts and tools, and a tested sim-to-real workflow, released before the first robots ship" [S2] |
| Provisional | "Not final yet — Camera resolution and field of view, LiDAR range, radio versions and SDK languages are still being finalised - and so is any age recommendation. Please treat them as provisional." [S2] |
| Openness | "Open source = software — The open-source statement covers the software stack. The mechanical and electronic design files are not, so please do not describe the robot as open-source hardware." [S2] |

"Fast facts" tile on [S1]/[S2]: "15 Motors · 25 cm Tall · 800 g To pick up · Camera Plus LiDAR and two IMUs · 7 Trained moves in the box · 50 Hz Onboard policy loop". (Note the tile literally says "800 g / To pick up" — a layout artefact; the fact sheet line is "15 motors · 25 cm · under 800 g".)

Blog summary sentence: "Microduck is a 25 cm tall biped robot with 15 motors, a camera, a small depth sensor, two IMUs, and an articulated beak that can pick up objects. It can walk, sit, crouch, get back up from many common falls, and even roller-skate. It weighs less than 800 g, fits on a desk, and is available for pre-order today for $399 before taxes and shipping." [S3]

Imperial restatements in press: "roughly 10 inches by 5.5 inches and weighing less than two pounds" [S51 snippet]; "25 centimeters (9.8 inches)… Less than 800 grams (1.8 pounds)… under 1.7 pounds" [S22]; "10 inches tall, 5.5 inches wide, and weighs less than 2 pounds" [S52 snippet].

Behaviours (product page cards) [S1]: "Walk — Velocity-tracking gait." "Sit & stand — Sits down, holds the pose, stands back up on its own." "Kick — A one-shot boot, then straight back to walking." "Grab — Dips the beak to the ground, scoops, and pops back upright." "Roller skating — Roller skating locomotion when the skates are equipped." "Get back up — Flat on its back to standing, all by itself, ready for the next command."

Lift capacity (press only): "Lift capacity: Approximately 100 grams maximum" [S24]; "~100 g lift capacity" [S37]. (TechEBlog's "lifts objects up to 800 grams" [S36] is an error conflating the robot's mass.)

---

## 3. Dimensions & mass — official vs model-derived

### 3.1 Official
- 25 cm tall, 14 cm wide, under 800 g / 780 g [S2, S6]. Blog: "Twenty-five centimetres, under 800 grams: it fits in a hand and on the desk between the laptops training it." [S3]
- Store shipping weight per variant: `grams: 1200` (1.2 kg, boxed with controller/battery/cable) [S6 JSON, T-official]. Pack shipping weights: Dev Pack 416 g, Accessory Pack 138 g, Charger Pack 268 g [S7–S9 JSON].

### 3.2 Official simulation model (microduck_rl `robot_walk.xml`) [S12, T-derived]
Sum of inertial masses of the 15 rigid bodies = **0.7372 kg** (737.2 g); model COM at INIT pose = (0.0017, 0.000, 0.1462) m with trunk origin at z = 0.120 m.

| Body | Mass (kg) | Visual meshes attached |
|---|---|---|
| trunk_base | 0.199224 | trunk_base, left_shell, right_shell, power_support ×2, np_f970, xl330 ×2, banana_pcb_locker, 22x16x4 bearing ×2 |
| yaw2roll / bearing_roll (L/R hip-yaw links) | 0.0230406 each | yaw2roll, xl330, bearing_roll, bearing |
| hip_l / hip_l_2 (hip-roll links) | 0.00618934 each | hip_l, bearing |
| upper_leg_left/right | 0.0482067 each | upper_leg_*, xl330 ×2, upper_leg_rigidity_plate, bearing |
| leg / leg_2 (shins) | 0.0215844 each | leg ×2, xl330 |
| ankle_left/right | 0.0300246 / 0.0300251 | ankle_*, foot_*, sole_*, 15x10x3 bearing |
| neck | 0.0368414 | neck ×2, xl330 ×2 |
| neck_pitch | 0.00572 | neck_pitch, bearing |
| yaw_roll_motion | 0.0486 | yaw_roll_motion, xl330, bearing ×2 |
| jaw_soft (head + beak) | 0.188766 | top/bottom_head_shell, face_part, noenoeil, jaw, jaw_soft, soft_mouth_top, motor_support, xl330 ×2, lens, m12_lens_holder, elec_rpi_robot_hat_pcb, pcb__raspberry_pi_zero_2_w, speaker, bearing |

Community bounding envelope of the assembled model: "144 × 141 × 264 mm", "Total mass: 737.2g" [S42, T-community].

### 3.3 STL bounding boxes (assets/*.stl, metres → mm) [S12, T-derived]
| Mesh | X | Y | Z (mm) | Reading |
|---|---|---|---|---|
| xl330 | 29.0 | 20.0 | 34.0 | XL330 body incl. horn; datasheet 20.0×34.0×26.0 [S31] |
| np_f970 | 38.6 | 20.6 | 70.8 | **matches an NP-F550 envelope (38.4×20.6×70.8 mm), not an NP-F970 (38.4×60×70.8)** despite the file name |
| pcb__raspberry_pi_zero_2_w | 65.0 | 1.6 | 30.0 | Pi-Zero form factor = Radxa Zero 3W footprint |
| elec_rpi_robot_hat_pcb | 65.0 | 30.0 | 0.8 | Pollen "RPI Robot HAT" |
| top_head_shell | 91.8 | 122.7 | 46.3 | head ≈ 92 wide × 123 long |
| bottom_head_shell | 91.8 | 116.7 | 20.1 | |
| jaw | 91.4 | 68.7 | 29.4 | lower beak |
| jaw_soft / soft_mouth_top | 87.7×32.2×8.4 / 87.8×32.6×3.3 | | | soft beak lips (likely TPU/soft) |
| face_part | (download truncated) | | | |
| left_shell / right_shell | 33.7 / 31.8 | 80.9 | 41.7 | trunk side shells |
| trunk_shell_left | 30.9 | 82.4 | 35.7 | alt trunk shell |
| trunk_base | 57.0 | 36.0 | 3.0 | 3 mm plate |
| power_support | 54.5 | 17.0 | 83.5 | battery cradle |
| banana_pcb_locker | 54.1 | 3.8 | 6.7 | |
| upper_leg_left | 28.0 | 47.7 | 61.0 | thigh |
| leg | 8.0 | 20.0 | 58.0 | shin plate (used ×2 per leg) |
| ankle_left | 39.5 | 36.5 | 25.5 | |
| foot_left | 40.1 | 54.0 | 16.9 | foot ≈ 40 × 54 mm |
| sole_left | 41.1 | 54.0 | 12.9 | sole |
| hip_l | 32.5 | 34.5 | 19.0 | |
| yaw2roll | 23.0 | 25.8 | 20.5 | |
| bearing_roll | 23.0 | 3.0 | 40.0 | |
| yaw_roll_motion | 34.0 | 35.9 | 22.5 | |
| neck | 2.0 | 20.0 | 11.0 | 2 mm plate ×2 |
| neck_pitch | 35.0 | 18.0 | 27.7 | |
| motor_support | 73.5 | 54.2 | 18.8 | head motor plate |
| m12_lens_holder | 24.0 | 14.8 | 16.0 | **M12 lens mount → wide-angle M12 lens camera** |
| lens | 16.9 | 18.9 | 16.9 | |
| speaker | 35.0 | 25.0 | 7.0 | box placeholder (12 tris) |
| bearings | 22×16×4 (name), 15×10×3 (community measured [S42]) | | | "seeed_bearing" names |

---

## 4. Actuators

### 4.1 Model & count
- **Dynamixel XL330 × 15**: microduck_rl README: "All tasks use the BAM M6 actuator model for the Dynamixel XL330 (voltage control law, back-EMF, Coulomb/Stribeck/load-dependent friction)" [S12]; `microduck_constants.py`: `motor_name="xl330", model="m6"` [S12]; bus.rs: `use rustypot::servo::dynamixel::xl330::Xl330Controller` [S11]; model.rs: "the XL330 ships at 250 [return_delay_time]" [S11]. Mesh `xl330` used 15× in the MJCF [S42]. Press: "Dynamixel XL330 servos" [S21, S29]; HN user modeless: "Interesting that they're using Dynamixel instead of Feetech for the servos. More expensive but better quality." [S30]
- **Sub-variant (M288 vs M077) is NOT stated officially** [S43]. Community assumes XL330-M288-T (288.35:1) [S42].
- XL330-M288-T datasheet [S31, T-official-Robotis]: weight "18 [g]"; dimensions "20.0 x 34.0 x 26.0 [mm]"; gear ratio "288.4 : 1"; stall torque "0.42 [N.m] (1.11 [A])" @3.7 V, "0.52 [N.m] (1.47 [A])" @5.0 V, "0.60 [N.m] (1.74 [A])" @6.0 V; no-load speed 76/103/123 rpm @3.7/5/6 V; input voltage "3.7 ~ 6.0 [V]" (recommended 5.0 V); resolution "4096 [pulse/rev]"; cored motor; Protocol 2.0; "9,600 [bps] ~ 4 [Mbps]"; "TTL Multidrop Bus (3.3V Logic, 5V Compatible)"; operating temp "-5 ~ +70 [°C]".
- Servo mass budget (community): "the 15 servos alone are 270 g of it (37 %)" [S42].

### 4.2 Bus & IDs (official source) [S11]
- "Fifteen servos and the `imu_to_dxl` board share one UART. There is no second bus and no second port" — "/dev/ttyS2 · 1 Mbps · Dynamixel protocol v2" (robotd-design.md).
- `JOINT_IDS = [20,21,22,23,24 (left leg), 30,31,32,33,34 (neck, head, mouth), 10,11,12,13,14 (right leg)]`; `IMU_DXL_ID = 200`; `BAUD_RATE = 1_000_000` (model.rs).
- `JOINT_NAMES` (duck-ipc-proto): left_hip_yaw, left_hip_roll, left_hip_pitch, left_knee, left_ankle, neck_pitch, head_pitch, head_yaw, head_roll, **mouth**, right_hip_yaw, right_hip_roll, right_hip_pitch, right_knee, right_ankle.
- "The mouth is absent from every alpha policy — they are all 61-D observation, 14-action, and the action vector skips this index." `MOUTH_INDEX = 9`; `MOUTH_CLOSED = −5°`, `MOUTH_OPEN = +30°` ("The alpha reuses the v1.6 range, −5°..+30°") (model.rs).
- Per tick: "one sync_read · IMU board + 15 servos · registers 124–136" then sync_write goal positions; "every 1 s slow_sensors() · registers 144–146 · voltage + temperature" (robotd-design.md). `READ_ADDR = 124`, `SLOW_READ_ADDR = 144`, "present_input_voltage counts 0.1 V each", `READ_TIMEOUT = 30 ms` (bus.rs). `RAD_PER_SEC_PER_COUNT = 0.229 × 2π/60`.
- EEPROM registers asserted at startup: `return_delay_time=0, baud_rate=3, pwm_slope=255, shutdown=52` — "the XL330 ships at 250, which is 500 µs of turnaround per device. Across 16 devices that is 8 ms per tick — 40% of a 20 ms budget"; "`shutdown = 52` is the error mask that latches on overload, overheating and input-voltage faults" (model.rs).
- Gains (robotd.toml defaults): `gain = 200` (position P), I = D = 0 ("The position P gain is written with I and D at zero"), `standing_gain_ratio = 0.8`, `action_scale = 0.9` walking / 0.8 roller, `head_lowpass = 0.5`, `legs_lowpass = 0.7` ("must match training or transfer degrades"), `voltage_adapt = false`, `nominal_voltage = 7.4`, `gain_limp = 50` on predicted fall [S11, S42].
- Physical layer (community reading of source): "3-wire TTL half-duplex… It is not RS-485… there is no direction-control GPIO in the code, which means direction switching is done in hardware by a self-steering circuit, and that circuit lives on the HAT." [S42, T-community]

### 4.3 Simulated actuator parameters (joints_properties.xml, class `chosen_actuator`, comment "marc", "200 kp") [S12]
`joint damping=0.053 frictionloss=0.0048 armature=0.0018`; `position kp=0.55 kv=0.0 forcerange="-0.96 0.96" ctrlrange="-10 10"`. Alternative fitted sets: `chosen_actuator_old` kp 0.52 / ±0.91; `chosen_actuator_new` kp 0.386 / ±0.67; `chosen_actuator_antoine` kp 0.43 / ±0.75; `perfect_actuator` kp 10 / ±20. BAM kwargs (`microduck_constants.py`): `kp_fw=200.0` ("microduck's preserved firmware stiffness (microban uses 125)"), `vin_range=(6.5, 8.2)`, `vin_drop_gain_range=(0.0, 0.2)`, `vin_min=6.0`, `delay_min_lag=3, delay_max_lag=6` (control steps). Backlash variants: "±1° of gear play (2° total) in series with each of the 14 servo joints" [S12].

**Observation (T-derived):** the fitted ±0.96 N·m exceeds the XL330-M288-T datasheet stall (0.60 N·m @ 6.0 V) and the runtime battery span 6.6–8.2 V exceeds the datasheet input range 3.7–6.0 V. Both are consistent with the servos being run directly off the 2S pack (~7.4 V nominal). Whether Pollen uses a stock XL330 over-spec, a custom-firmware/variant, or a regulated bus is **not published** (see §19).

---

## 5. Kinematics (from `robot_walk.xml`, INIT keyframe qpos = 0, trunk origin at z = 0.120 m) [S12, T-derived]

World-frame joint axes/positions at INIT (m). Legs are mirror images about y = 0.

| Joint | Position (x, y, z) | Axis (world) | Range (rad) | Range (deg) |
|---|---|---|---|---|
| left_hip_yaw | (0.006, +0.0175, 0.115) | −z | [−0.436, +0.524] | −25 … +30 |
| left_hip_roll | (0.0225, +0.0175, 0.1025) | +x | ±0.384 | ±22 |
| left_hip_pitch | (0.004, +0.0425, 0.1025) | +y | ±1.571 | ±90 |
| left_knee | (−0.0318, +0.0385, 0.0805) | −y | ±1.571 | ±90 |
| left_ankle | (−0.0318, +0.0645, 0.0385) | +y | ±1.571 | ±90 |
| left_foot site | (−0.0318, +0.0504, 0.0147) | | | |
| neck_pitch | (0.026, +0.0145, 0.1524) | −y | [−1.571, +1.047] | −90 … +60 |
| head_pitch | (0.026, +0.0145, 0.2024) | +y | ±1.571 | ±90 |
| head_yaw | (0.026, 0, 0.2211) | +z | ±2.967 | ±170 |
| head_roll | (0.0081, 0, 0.2356) | −x | ±0.436 | ±25 |
| right_hip_yaw | (0.006, −0.0175, 0.115) | −z | [−0.524, +0.436] | −30 … +25 |
| right_* | mirror of left | | | |
| Sites (head) | head_camera (0.0814, 0, 0.2511); tof (0.0814, +0.0224, 0.2491); head_imu (0.0592, 0, 0.2508); mouth_tip (0.0858, 0, 0.2275) | | | |
| Site (trunk) | imu (−0.021, 0, 0.1053) | | | |

Derived link geometry (INIT pose):
- Hip-yaw axis lateral spacing **35 mm** (y = ±17.5); hip-pitch axis spacing **85 mm** (y = ±42.5); knee axes at y = ±38.5; ankle axes at y = ±64.5 (shin/ankle offset **26 mm outboard** of the knee axis).
- Hip yaw → hip roll: Δ(16.5, 0, −12.5) mm. Hip roll → hip pitch: Δ(−18.5, +25, 0) mm.
- Thigh (hip_pitch → knee): Δ(−35.8, −4, −22) mm ⇒ **42.0 mm** in the sagittal plane at INIT.
- Shin (knee → ankle): Δ(0, +26, −42) mm ⇒ **42 mm vertical**, 49.4 mm straight-line.
- Ankle → foot-contact site: Δ(0, −14.1, −23.8) mm ⇒ sole contact ≈ 14.7 mm above floor origin at INIT (trunk z=0.120).
- Neck pitch → head pitch: **50 mm** (vertical at INIT). Head pitch → head yaw: 18.7 mm up, 14.5 mm inboard. Head yaw → head roll: Δ(−17.9, 0, +14.5) mm. Head-roll axis → mouth tip: 77.7 mm forward. Camera sits 73 mm ahead of and 15.5 mm above the head-roll axis; ToF is 22.4 mm to the left of the camera at the same forward station.
- Trunk IMU is 21 mm behind and 14.7 mm below the trunk origin.

Home / STAND keyframe (scene_rollers.xml; matches `DEFAULT_POSITION` in model.rs): trunk z = 0.12; left leg (hip_yaw 0, hip_roll −0.0873 [−5°], hip_pitch −0.4579 [−26.24°], knee −0.0049 [−0.28°], ankle +0.4530 [+25.95°]); neck_pitch 0.3491 [20°], head_pitch 0.3491 [20°], head_yaw 0, head_roll 0; right leg mirrored. Comment: "STAND2: trunk shifted ~5mm forward (CoM over ankle axis). Leg pitch leaned forward vs old STAND: hip_pitch 30->26.24deg, ankle 30->25.95deg, knee 0->0.28deg." SIT keyframe: trunk z 0.07, hip_pitch −0.5236, knee +1.0472, head_pitch 0.5, head_yaw 1.6. FOLD: trunk z 0.07, hip_pitch/knee 1.57.

Joint layout summary: **legs 2 × (hip yaw, hip roll, hip pitch, knee, ankle) = 10 DoF; neck/head 4 DoF (neck pitch, head pitch, head yaw, head roll); mouth/beak 1 DoF (ID 34, not in policy); total 15 motors / 14 policy-controlled.** No antenna actuators (unlike Open Duck Mini's 2 × 9 g antenna servos). Roller model adds passive wheel hinges `passive_LF_wheel`, `passive_LR_wheel`, `passive_RF_wheel`, `passive_RR_wheel` under each foot (`tire`, `rim`, `roller_blade` meshes) [S12].

---

## 6. Compute

- Official: "Rockchip RK3566 with AI accelerator", "1 GB RAM, 32 GB storage" [S2]. CNX: "Quad-core Cortex-A55 @ up to 1.8 GHz, Arm Mali-G52, 0.8 TOPS NPU, 32GB eMMC flash" [S18, T-press].
- Board (official source): "What a Radxa Zero 3W does about video. Everything below was observed on a board" (media-bringup.md); robotd.toml: "/dev/ttyS2 is the Radxa Zero 3W's wiring"; docs/README.md references the Radxa Zero 3W; install-dev.md: flash "Pick Radxa Zero 3" with "Armbian 26.2.1 Minimal"; roadmap: "Runs on Radxa Zero 3W with non-RT kernel maintaining 50.0 Hz loop" [S11]. Kernel "6.1.115-vendor-rk35xx". NPU: "The RK3566 has a small INT8 NPU — 0.8 TOPS, one core" (npu-bringup.md); duck detector `yolo11n` at 320×320 as `.rknn`; detection at 2 Hz "is a thermal limit, not a preference" (95 °C, throttling to 408 MHz) [S11 via S42].
- Radxa Zero 3W public spec: "Rockchip RK3566", "Quad-Core Arm Cortex-A55 Up to 1.6GHz", "Arm Mali-G52 2EE", "Wi-Fi 6 / BT 5.4", "22-Pin MIPI CSI", "USB 3.0 HOST Type C" + "USB 2.0 OTG Type C", "40-Pin GPIO Header", LPDDR4, onboard eMMC [S45].
- Prototype ran on a Raspberry Pi Zero 2W: "50 is inherited from the prototype, where it was chosen on a Raspberry Pi Zero 2W. It has never been re-derived on the Radxa." (robotd.toml) [S11]. The MJCF still carries a `pcb__raspberry_pi_zero_2_w` mesh in the head [S12].
- Policy inference: ONNX Runtime, dlopened, "obs[1,61] -> actions[1,14]" [S11].
- Software architecture: Rust daemons `robotd, updaterd, configd, btd, padd, mediad, tofd` over JSON-RPC on Unix sockets [S11 README].

---

## 7. Sensors

### 7.1 Camera
- Official: front camera, wide-angle, REC-style indicator; resolution/FOV provisional [S2, S6].
- Source: sensor identified on the board as "imx219 2-0010: Model ID 0x0219…" (Pi Camera v2 class), overlay `radxa-zero3-rpi-camera-v2`, "the IMX219 is mounted upside down" (rotation 180 in hardware encoder), capture node `rkisp_mainpath` "formats to 3280x2464", stream "1280x720 constrained-baseline" H.264 via Rockchip MPP (media-bringup.md) [S11]. MJCF has `m12_lens_holder` + `lens` meshes → M12-mount lens (wide angle) [S12]. Community: "HFOV ~62°" [S42, unverified].

### 7.2 Depth (ToF)
- Official: "Compact LiDAR, an 8x8 time-of-flight matrix" [S2].
- Source (tof/src/lib.rs): "A VL53L5CX or VL53L8CX on the HAT's I²C bus — the same `i2c3` bus the audio [codec uses]"; 8×8 zones pinned; 15 Hz ranging ("an 8×8 frame costs about 5% of a 400 kHz bus"); addresses tried 0x29 then 0x52; bus `/dev/i2c-pihat` → `/dev/i2c-3` [S11]. CNX: "possibly VL53L8CX; range not finalized" [S18]. Used for the "ToF theremin" demo (0.10–0.70 m band) [S11, S42].

### 7.3 IMUs
- Official: 2 IMUs, body + head [S2].
- Body/control IMU (source, imu.rs): "The `imu_to_dxl` v2 board (LSM6DSV16X), decoded. One IMU, one code path. The board rides the Dynamixel bus and its 12-byte block is fetched in the same `sync_read` as the servos… the chip's SFLP block ships a game-rotation quaternion and estimates its own gyro bias." Block at address 124: bytes 0..6 gyro i16 ±500 dps (17.5 mdps/LSB), 6..12 SFLP quaternion x/y/z as fp16, w reconstructed; full diagnostic block 20 bytes [S11].
- Second IMU: device tree `i2c3-pihat.dts` lists "dormant BMI088 0x19/0x68" on the Robot HAT ("unused but still connected") [S11]. MJCF has a `head_imu` site inside the head [S12]. Community reads the HAT (which sits in the head with the Pi-footprint board) as the "head IMU" location; **production mapping of the 2nd IMU not published** [S43].
- Fall logic: fall verdict on projected gravity "debounced 0.2 s"; `limp_fall` predictive detector "fires when the robot is already tilted (≈26°)… extrapolating over ~0.3 s… debounced three ticks" [S11].

### 7.4 Audio
- Official: microphones and speaker, per-robot generated voice: "Each Microduck gets its own audio identity the first time it wakes up, tied to that individual robot so it keeps the same voice for life." [S3]
- Source: `aic3104-i2c3.dts`: "TLV320AIC3104 audio codec on the Pollen Robotics RPI Robot HAT", codec@18, MCLK 12 MHz, I2S3 system clock 12.288 MHz, card name "aic3104" [S11]. Mic wake-word: "pet-detect/ — a ~20 KB CNN over a 40-band log-mel window from the onboard mic" [S11]. Community: mic on codec input "Mic3R (mono)" [S42].

### 7.5 NFC
- "2 antennas, one in the head and one in the beak" [S2]. Accessory pack: "NFC Polaroid, a 1.54-inch color NFC-powered E-Ink display… Tap it on your robot's head to discover what your robot is dreaming about"; "10 × NFC Tags, create custom interactions, triggers, and behaviors using NFC" [S8]. Controller IC not published [S43].

---

## 8. Electronics boards (from official source; no schematics published)
- **Radxa Zero 3W** (off-the-shelf) — main compute [S11].
- **Pollen Robotics "RPI Robot HAT"** — 65×30 mm Pi-Zero-footprint board (`elec_rpi_robot_hat_pcb` mesh 65.0×30.0×0.84 mm [S12]); carries TLV320AIC3104 @0x18, dormant BMI088 @0x19/0x68, "ToF via Stemma J5" @0x29; I²C3 on header pins 3/5 (GPIO1_A0/A1) at 400 kHz; "the HAT has a single 10k pull-up pair, R12/R13"; "In-robot power comes from the battery via the HAT regardless"; overlay disables the Radxa's FUSB302 USB-C PD node (power-on defaults still give 5 V) [S11 i2c3-pihat.dts].
- **`imu_to_dxl` v2** — LSM6DSV16X IMU presented as a Dynamixel Protocol-2 slave, ID 200, register block 124 [S11]. MCU/transceiver not published.
- Bus wiring: 16 devices on one half-duplex TTL UART (/dev/ttyS2 = RK3566 UART2 M0) [S11, S42].

---

## 9. Power
- "Removable NP-F550 camera battery, 2600 mAh, around one hour of runtime depending on use" [S2]; "2,600mAH battery should be good for around one hour of continuous runtime" [S20].
- Source: "Off a full charge, under load. NP-F550, 2S Li-ion. BATTERY_FULL_V = 8.2"; "BATTERY_EMPTY_V = 6.6"; "There is no fuel gauge and no ADC. The only measurement available is what the servos report as their own supply"; "reaching the empty floor on the smoothed voltage sits the robot down and powers the board off. The EMA moves over ~10 s" [S11]. Battery pill example `{"volts":7.62,"percent":64}` [S11].
- MJCF mesh is named `np_f970` but its envelope (38.6×20.6×70.8 mm) is that of an NP-F550 [S12, T-derived]. Community flags the naming conflict [S43].
- Charger Pack: "2 × Batteries… 1 × Dual Battery Charger, charge two batteries simultaneously" €33 / $39; shipping weight 268 g [S9]. USB-C cable in box [S1]; charging path via USB-C to the board (5 V) [S11].

---

## 10. Connectivity & control
- Wi-Fi + Bluetooth [S2]; Radxa module "Wi-Fi 6 / BT 5.4" [S45] (press kit says radio versions provisional).
- Gamepad in box; `padd` reads gamepad over Bluetooth; `duckctl` = "The robot from a laptop over Bluetooth, with no network and no ssh"; `mediad` streams camera over WebRTC (console :8080, signalling :8443); `ssh microduck` + `robotctl monitor/configure/update` [S1, S11].
- Gamepad mapping (cheatsheet): "left stick | drive: forward/back and strafe · head: head yaw and pitch · body pose: up and crouch"; Start toggles policy; A = ground pick, X = roulade, Y = sit/stand, kicks on shoulder buttons; D-pad up = roller mode; triggers = mouth/audio [S11].

---

## 11. Software, policies, training
- Licence: "Apache-2.0 — The whole software stack, permissively licensed"; "MuJoCo — The physics sim every policy is trained in"; "7 policies — Every shipped move, published and retrainable" [S1]. microduck_rl: "This project is licensed under the Apache 2.0 License… Hardware design files are licensed under Creative Commons BY-SA-NC." [S12] (i.e., the MJCF/STL assets are CC BY-SA-NC).
- Shipped policy files on HF `pollen-robotics/microduck-policies` (Apache-2.0, last modified 2026-08-31): `alpha_ground_pick.onnx, alpha_sitstand.onnx, alpha_stand.onnx, alpha_walking.onnx, ball_kick_left.onnx, ball_kick_right.onnx, roller.onnx, roller_crouch.onnx, roulade.onnx` (9 files) [S13]. robotd.toml walk-mode slots: walk (alpha_walking = "the velstand gait"), stand, sitstand, ground_pick, kick_left, kick_right, roulade [S11].
- Training: "built on mjlab (MuJoCo Warp) with PPO"; "~1-2 h for a usable gait at 4096 envs"; "Requires a CUDA GPU"; `--hf-jobs` to train on Hugging Face Jobs; 61-D obs = "48 proprioception + commands [twist(3), head_pose(4), body_pose(6)]"; obs layout in runtime "[gyro(3) | projected_gravity(3) | joint_pos(14) | joint_vel(14) | last_action(14) | command(13)]"; export bakes normaliser into ONNX; ball-kick task uses "a 70 mm / 15 g ball"; models "exported from Onshape with onshape-to-robot" [S12, S11].
- Task families: Velocity, VelStand, StandUp, SitStand, GroundPick, BallKick, Roulade, Velocity-Rollers, Swizzle, RollerCrouch, RollerSlope, RollerStandUp, Spin (+ Flat/Rough and Backlash twins) [S12].
- Out-of-box interactions: "make it walk with a gamepad, have it follow a laser dot, trigger movements, or let it react to its surroundings" [S3]; "chorale" (several ducks singing), "theremin" (ToF → pitch), duck detector on NPU [S11].
- Updates: signed releases with health-gated rollback (`updaterd`) [S11]. Roadmap decision "2026-08-26: Publishing the repository so customer robots download directly without tokens" [S11].

---

## 12. Materials / manufacturing (what is published)
- Press kit: "Four printed colourways - Cream, Graphite, Lavender and Sky. Same robot underneath. Swatches are the calibrated shell colours from the press photos." Cream #f7e6cb "Cream shells, orange trim and beak"; Graphite #6c6a68 "Graphite shells, yellow trim and beak"; Lavender #bfa9cf "Lavender shells, yellow trim and beak"; Sky #a9dbe8 "Sky-blue shells, orange trim and beak" [S2]. "printed" is the only word about shell manufacture; **injection-moulded vs 3D-printed is not stated** (search found no statement) [T-unknown].
- Accessory rollers colour-matched: "We recommend orange for Cream and Sky, and yellow for Graphite and Lavender robots." [S8]
- Beak: `jaw_soft` / `soft_mouth_top` meshes (8.4 mm and 3.3 mm thick lips) indicate a soft/compliant beak material [S12, T-derived]. Blog: "the beak closes, and the object comes along" [S3].
- Fasteners (community, from mesh hole analysis): "The Whole Robot Is an M2 System" — Ø2.2 ×77 (M2 clearance), Ø4.4 ×28 (counterbore), Ø1.6 ×20 (M2 tap), Ø2.7/2.8 ×20 (M2.5); `xl330.stl` carries "4× Ø2.0 + 8× Ø1.6"; bearings "OD 22 × ID 16 × W 4 mm" and "OD 15 × ID ~10 × W 3 mm (×3)" [S42, T-community].
- Dev Pack spare parts: "3 × Motors… 5 × Motor Cables… 1 × Screwdriver… 1 × Screw Pack" (implies user-serviceable servo swaps with a single screw type) [S7].

---

## 13. Price, packs, availability
- Robot: "$399 — Introductory price, before taxes and shipping" [S1]; store "€340,00 EUR" per colour [S6]; heise: "€440.30 (including delivery and taxes)" [S40].
- Packs [S1, S6–S9]: Charger pack $39 / €33 ("Dual charger, 2x batteries"); Dev pack $119 / €99.99 ("3x spare motors, 5x motor cables, 2x batteries, dual charger, 10x NFC tags, Hugging Face credit, screwdriver, screw pack"); Accessory pack $39 / €33 ("Laser pointer, NFC polaroid, 2x rollers, ball, 10x NFC tags"). "Fully Loaded: $596 USD (€505.99 EUR)" [S37].
- Regions: press kit "North America and Europe at launch"; blog "North America, Europe, and the UK"; store "Available at launch in US/Canada/EU/UK/Norway/Switzeland/Japan and South Korea. More countries available later." [S2, S3, S6]
- Delivery: "First deliveries targeted before Christmas 2026" [S2]; store banner (2026-09-01): "The community ordered a lot of ducks. We can't promise Christmas delivery for new microduck orders anymore, but we're ramping up production." [S6]; eesel: "Current lead time: 4 to 6 months" [S25].
- Store product record created 2026-08-10, published 2026-08-27T09:22:51+02:00 [S6 JSON].
- Volume ambition: Delangue to Axios "I think 50,000 would be a great success" (~$20 M) [S52 snippet, S34].

---

## 14. Open source vs proprietary — the official line
- "The SDK, the simulation and the full RL training stack are on GitHub. What the robot runs is what you can read, fork and retrain." [S1]
- "The open-source statement covers the software stack. The mechanical and electronic design files are not, so please do not describe the robot as open-source hardware." [S2]
- The Register: "Hardware is NOT open source (no plans to open source it)" [S24]. HN victor9000: "The hardware is not open" [S30].
- microduck_rl assets: "Hardware design files are licensed under Creative Commons BY-SA-NC" — i.e., the released MJCF + 64 STL visual meshes are the only published geometry, under CC BY-SA-NC [S12]. No Onshape document, BOM, PCB, or STEP has been published (confirmed by [S41] "Hardware is not open-source (no BOM, CAD, or PCB files published by Pollen)").
- `imu_to_dxl` board firmware: not in the repository [S42].

---

## 15. Press quotes (verbatim)
- Clem Delangue (HF CEO): "It's a tiny $399 open-source robot you can teach new tricks with reinforcement learning." / "Welcome to the era of open-source affordable robots to democratize physical AI and world models!" [S19, S23, S24]
- Thomas Wolf (HF CSO, to Bloomberg): "I think we're creating a new category of consumer robots here, which is AI native and kind of playful but also education tools." [S23]
- Santiago Pavon (Pollen): "Anyone can train new behaviors … in simulation using reinforcement learning."; autonomy "is something we are still working on, and we expect the community to pick up and contribute." [S24]
- Blog: "Microduck was designed not to be taken too seriously." [S27]; "One very unscientific thing we learned internally is that Microduck is about ten times more fun when there are several of them." [S3]
- HN hadlock: "the fact that their simulator actually works out of the box, 'batteries included', is a big deal for home hobbyists." [S30]

---

## 16. Lineage: Open Duck Mini (v2) → Microduck

### 16.1 Open Duck Mini v2 facts (official repo & BOM) [S15, S16, S17, T-official-ODM]
- "Making a miniature version of the BDX Droid by Disney. It is about 42 centimeters tall with its legs extended. The full BOM cost should be under $400!" — Apache-2.0; Onshape CAD https://cad.onshape.com/documents/64074dfcfa379b37d8a47762/w/3650ab4221e215a4f65eb7fe/e/0505c262d882183a25049d05 ; Discord; "Thanks a lot to HuggingFace and Pollen Robotics for sponsoring this project!"; runtime on Raspberry Pi Zero 2W; RL in MuJoCo → Mujoco Playground; ONNX policies.
- BOM (Google Sheet, EUR) [S16]: 18650 cell ×2 (Molicel P30B 3000 mAh 30 A, €5 ea); 18650 holder; 2S BMS €8.40; 5 V UBEC regulator (4–12 A) €4; power switch; USB-C charger; 2.1 mm barrel jack ×2; XT30 connector; **IMU BNO055** €40 ("Need to find a cheaper alternative"); **Raspberry Pi Zero 2W** €26.08; SD card; **Waveshare Bus Servo Adapter (A)** €5; **Feetech 7.4 V STS3215 ×14** @ €14 = €196 ("Be sure to buy the 7.4v ones, also called 19kg.cm"); feet contact switches SS-10 ×4; **9 g servos ×2** (antennas); M3 inserts; ~500 g standard PLA; TPU for feet; cable sheath; USB cables; bearings ×3 €10.50; **subtotal €398.1 (lowest €331.1)**. "Expression package": projector reflector, speaker €6, LEDs (eyes + projector), microphone €15 ("not integrated yet"), eye diffusers, amplifier, Raspberry Pi camera €5 ("Not integrated yet") → **total €432.34 (lowest €365.34)**.
- Print guide: "standard PLA with 15% infill", TPU 40% for `foot_bottom_tpu.stl`; 35 unique files, 66 parts [S15]. Assembly guide: BNO055, Pi Zero 2W, MAX98357A amp, foot switches ×2 press-fit, 2 antennas with PWM, "Loctite Threadlocker blue 243", M3 screws/inserts [S15].
- Joint set (14 DoF): left/right hip_yaw, hip_roll, hip_pitch, knee, ankle + neck_pitch, head_pitch, head_yaw, head_roll; limits hip yaw ±30°, hip roll ±25°, hip pitch −70/+30°, knee ±90°, ankle ±90°, neck pitch −20/+65°, head pitch ±45°, head yaw ±160°, head roll ±30° [S47]. ID scheme 20-24 / 30-33 / 10-14 [S42].
- Community MJCF mass of ODM v2: "2107.1 g" at 42 cm [S42]. Hackaday: "a little over 40 cm tall", "hobby servos", "around 400 USD" [S46]. Runtime: Xbox One controller over Bluetooth [S17]. Third-party assembled kits: Tindie $1,000 (5+ @ $800), Cereboto $780 [S49]. Gemma 4 E2B on-device demo at Google I/O 2026 used Pi 5 / Jetson Orin Nano variants [S48].

### 16.2 Published statements linking the two
- Pollen's official Microduck pages **never mention Open Duck Mini** (checked S1–S3, S11 README). Antoine Pirrone is on the byline and core team [S3].
- robotd-design.md: "The prototype being absorbed is `apirrone/microduck_runtime`… Only the alpha variant, only the Radxa, only the v2 `imu_to_dxl` board. v1/v1.5/v1.6, the four other IMUs, the three cameras and the Pi are dropped" [S11] — i.e., Microduck went through v1 → v1.5 → v1.6 → alpha prototypes, on a Pi first.
- eesel: "Microduck is the shipped, assembled version of the Open Duck Mini project… The robot got smaller, from about 35 cm to 25 cm, the sensing got richer with a time-of-flight array, a second IMU and NFC antennas, and the beak became a gripper rather than a decoration." [S25, T-press]
- explainx: "Microduck is the commercial successor to the June 2026 Open Duck Mini… Open Duck Mini cost '~$400 in parts'" [S26]. kingy.ai (more cautious): "The overlap in personnel, price ambition, form, and training method suggests a lineage… the reviewed public sources do not establish that Microduck is a direct commercial version of Open Duck Mini, nor do they promise compatible parts or policies." [S28]
- HN jgrizou (Pollen alumnus): "He works at Pollen, so that was the inspiration for it pre-product." HN croes: "it seems Open Duck Mini is it's predecessor" [S30].
- Community: "This ID scheme is identical to Open Duck Mini v2 (20-24 / 30-33 / 10-14), with only the extra 34 added. The lineage shows." [S42]

### 16.3 Concrete differences (Open Duck Mini v2 → Microduck)
| | Open Duck Mini v2 | Microduck |
|---|---|---|
| Height | ~42 cm (README) / "35 cm" (eesel) | 25 cm |
| Mass | ~2.1 kg (MJCF) | <800 g / 780 g (737 g MJCF) |
| Servos | 14 × Feetech STS3215 7.4 V 19 kg·cm (+2 × 9 g antenna servos) | 15 × Dynamixel XL330 (14 policy + mouth) |
| Servo bus | Feetech serial via Waveshare adapter | Dynamixel Protocol 2, 1 Mbps, one UART |
| IMU | BNO055 (I²C) | LSM6DSV16X on Dynamixel-bus `imu_to_dxl` v2 (+ dormant BMI088 on HAT; 2 IMUs officially) |
| Compute | Raspberry Pi Zero 2W | Radxa Zero 3W (RK3566, 1 GB, 32 GB eMMC, NPU) |
| Battery | 2 × 18650 (2S, 3000 mAh) + BMS + UBEC | Removable NP-F550 2600 mAh 2S, no fuel gauge |
| Depth sensor | none | 8×8 ToF (VL53L5CX/L8CX) |
| Camera | Pi camera (optional) | IMX219 M12-lens wide-angle, upside-down mounted, HW H.264 |
| Beak | decorative | 1-DoF articulated gripper (~100 g lift) |
| Antennas | 2 actuated antennas | none actuated; 2 NFC antennas (head, beak) |
| Feet | foot contact switches ×4 | none in source (odometry from joint/IMU); passive rollers accessory |
| Shell | 3D-printed PLA, TPU feet | "printed colourways" — process not stated |
| Fasteners | M3 + inserts | M2 system (mesh-derived) |
| Open hardware | Yes (Apache-2.0, Onshape) | No (CC BY-SA-NC sim meshes only) |
| Price | ~€400 parts, DIY | $399 assembled |

---

## 17. Community reverse-engineering resources (for the RE project)
- fanhao375/microduck-replica [S42]: per-body STL export with MJCF transforms, exploded drawings, hole analysis (`scripts/analyze_holes.py`), electronics teardown from source. Licence: scripts Apache-2.0; drawings/CAD CC BY-SA-NC 4.0. Claims: "Microduck: XL330, 737.2 g, 25 cm; Open Duck Mini v2: STS3215, 2107.1 g, 42 cm" and STS3215 MJCF params "kp 17.8, forcerange ±3.35 N·m, damping 0.60, frictionloss 0.052, armature 0.028".
- SaberOnGo/open-microduck [S43]: bilingual parameter reference; keeps a running "open questions and conflicts" ledger.
- ScrapMeta/microduck-diy [S44]: 38-STL print guide and 3MF plates from public meshes ("open mesh resources; not official production spec sheets… typically requiring ×1000 scaling to millimeters").
- joeynyc/awesome-microduck [S41]: index incl. HF Space `mishig/microduck-anatomy` (interactive viewer), Genesis/Isaac ports, community policies (backflip, moonwalk, flamingo…), MCP servers, videos ("Product overview: youtube.com/watch?v=reiTh7K4KSc", "Sim 2 Real comparison: youtube.com/watch?v=szW7N_7B3tU").

---

## 18. Numeric quick sheet
See `01-specs.json` (same directory) for the machine-readable list with source and confidence.

---

## 19. CONTRADICTIONS / UNKNOWNS

### Contradictions between sources
1. **Weight:** "Under 800 g" (press kit, blog) vs "780 g" (store) vs MJCF sum 737.2 g vs shipping weight 1.2 kg (boxed). Press: "1.7 pounds" / "1.76 pounds" / "1.8 pounds" / "under 2 pounds".
2. **Battery model in CAD vs product:** mesh named `np_f970` (MJCF) vs official "NP-F550"; mesh envelope 38.6×20.6×70.8 mm matches NP-F550, so the geometry agrees with the spec and only the name is stale.
3. **Servo voltage:** XL330-M288-T datasheet input 3.7–6.0 V (stall 0.60 N·m @ 6 V) vs runtime pack window 6.6–8.2 V measured "as the servos' own supply" and simulated forcerange ±0.96 N·m. Not explained in any published source (stock part over-spec? regulated bus? custom variant?).
4. **Open Duck Mini height:** ODM README "about 42 centimeters"; eesel "from about 35 cm to 25 cm".
5. **Markets:** press kit "North America and Europe"; blog adds "UK"; store lists US/Canada/EU/UK/Norway/Switzerland/Japan/South Korea.
6. **Beak lift:** The Register "approximately 100 grams" vs TechEBlog "up to 800 grams" (error).
7. **Compute board:** product spec says only "Rockchip RK3566"; source is explicitly Radxa Zero 3W. Whether production units use the stock Radxa module or a custom carrier is not stated ([S43] flags it; [S42] asserts stock module from device-tree `compatible = "radxa,zero-3w"`).
8. **Camera/ToF part numbers:** source uses IMX219 and supports VL53L5CX *or* VL53L8CX; press kit says camera resolution/FOV and LiDAR range are provisional.
9. **Radxa clock:** Radxa page "Up to 1.6GHz" vs CNX "up to 1.8 GHz".
10. **HN metrics:** 780 pts / 252 comments (Algolia, 2026-09-01) vs "763 points and 246 comments" (eesel snapshot).
11. **Pre-order date:** TheNextWeb "Thursday, August 29, 2026" vs official August 27, 2026 (TNW error).
12. **Lineage wording:** press calls Microduck the "shipped version of Open Duck Mini"; Pollen never says so; the runtime docs instead describe the prototype `microduck_runtime` with variants v1/v1.5/v1.6/alpha.

### Not published anywhere (as of 2026-09-01)
- Official CAD (Onshape/STEP), mechanical drawings, BOM, PCB schematics/Gerbers for the Robot HAT and `imu_to_dxl` v2; the `imu_to_dxl` MCU and firmware; the half-duplex transceiver on the HAT.
- XL330 sub-variant (M288 vs M077) and whether servos are stock; servo cable type/lengths; harnessing through the neck yaw joint.
- Shell manufacturing process (injection-moulded vs printed) and materials; beak lip material (soft); sole material; part count.
- Exact bearing part numbers (only "seeed_bearing 22x16x4" and a 15×10×3 geometry).
- Screw sizes/quantities (community estimates only), heat-set inserts vs tapped plastic.
- Camera module (lens FOV, resolution in product), mic part numbers, speaker part number/impedance/power, NFC controller IC, second-IMU production placement.
- Battery charger specs (voltage/current), USB-C charging behaviour when the battery is fitted, whether the robot can run tethered.
- Battery runtime under specific loads; charge time.
- Servo temperature limits used by `shutdown=52` mask, torque/current limits set at runtime (only P-gain 200 is published).
- Weight breakdown of real hardware (only MJCF inertials).
- Warranty terms, age recommendation ("still being finalised"), SDK language list (press kit: provisional; source is Rust + Python RL).
- Any teardown photos of a production unit (none exist — robots have not shipped; all community RE is from the released MJCF/STL/source).
