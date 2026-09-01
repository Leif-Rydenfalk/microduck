# Microduck — dimensional estimate

**Authority ranking:** (1) the MuJoCo model shipped in `pollen-robotics/microduck_rl` (`src/mjlab_microduck/robot/microduck/robot_walk.xml` + STL assets, exported with onshape-to-robot from Onshape doc `804927696f06d877f3f1803e`) — downloaded to `../cad/`; (2) published spec sheet (press kit); (3) photo measurement. The MJCF is the *alpha* CAD (it contains a Raspberry Pi Zero 2 W 65x30 board where production has an RK3566 board of the same Pi-Zero footprint, and an "np_f970" battery mesh that is actually NP-F550 sized: 38.6 x 20.6 x 70.8 mm), but every shell, leg, foot and head mesh matches the launch photos, so treat it as ground truth for geometry.

## Published
- Height 25 cm; width 14 cm; weight < 800 g (store lists 780 g); 15 motors; battery NP-F550 2600 mAh (press kit, store).
- Model total mass in MJCF: 737 g (trunk 199 g, head assembly 189 g, each thigh 48 g, shin 22 g, foot 30 g, yaw/roll blocks 23 g + 6 g).

## Kinematics (from MJCF; z = height above floor with trunk origin at 120 mm, all joints zero; mm)
| joint | position (x fwd, y left, z up) | axis | range |
|---|---|---|---|
| hip yaw L/R | (6, ±17.5, 115) | z | -25..+30 deg |
| hip roll L/R | (22.5, ±17.5, 102.5) | x | ±22 deg |
| hip pitch L/R | (4, ±42.5, 102.5) | y | ±90 |
| knee L/R | (-31.8, ±38.5, 80.5) | y | ±90 |
| ankle L/R | (-31.8, ±64.5, 38.5) | y | ±90 |
| neck pitch | (26, 14.5, 152.4) | y | -90..+60 |
| head pitch | (26, 14.5, 202.4) | y | ±90 |
| head yaw | (26, 0, 221.1) | z | ±170 |
| head roll | (8.1, 0, 235.6) | x | ±25 |
| jaw | closed-loop linkage off head (15th motor) | | |

Derived link lengths (perpendicular distance between parallel axes):
- **Thigh (hip pitch -> knee): 42.0 mm**; **shin (knee -> ankle): 42.0 mm**; ankle axis to sole bottom: ~36 mm; hip yaw to hip roll: 12.5 mm; hip roll to hip pitch: 25 mm lateral offset.
- Hip pitch spacing (stance width at hips): 85 mm; ankle spacing: 129 mm (legs splay outward ~26 mm per side through the knee offset, hence the wide-track duck stance).
- Neck: trunk -> neck-pitch 32 mm; neck link 50 mm; head-pitch -> head-yaw 19 mm; head-yaw -> head-roll 15 mm.
- Standing pose (`STAND` keyframe): hip pitch 26.2 deg, knee ~0, ankle 26 deg, neck pitch 20 deg, head pitch 20 deg. Sitting pose lowers trunk origin to 70 mm.

## Overall envelope (assembled model, floor at z = 0)
| pose | length (x) | width (y) | height |
|---|---|---|---|
| STAND (head pitched 40 deg total, hips 26 deg) | 123 mm | **142 mm** (feet outer edges; = published 14 cm) | **272 mm** to top of head |
| INIT (all zero, legs straight, head level) | 144 mm | 141 mm | 264 mm |
The published "25 cm" is the head-level figure with knees slightly bent; 25-27 cm depending on head pitch.

## Part dimensions (STL bounding boxes, mm)
| part | L x W x H | notes |
|---|---|---|
| Head top shell | 122.7 long x **91.8 wide** x 46.3 tall | D-profile loaf; front face flat |
| Head bottom shell | 116.7 x 91.8 x 20.1 | carries fixed upper beak lip |
| Head total | ~123 x 92 x 66 (shell) | head centre ~ z 245 above floor; head length : width = 1.34 |
| Face panel (grey inset) | 87.7 wide x 44.6 tall x 12.5 deep | |
| Eye ring ("noenoeil") | Ø30 x 9.5 deep | centred on face; lens Ø16.9 (M12 lens, holder 24 x 14.8 x 16) |
| ToF window | ~8 x 4 mm rounded slot, 22 mm right of eye centre, same height | site `tof` at y = +22.4 |
| Jaw (lower beak) | 68.7 long x 91.4 wide x 29.4 (incl. side brackets) | plate ~3-4 mm thick; soft pad 87.7 x 32 x 8 |
| Trunk shells L+R | 82.4 long x ~62 wide (31 + 31) x 35.7 tall | pill; assembled z 120-162 |
| Battery NP-F550 | 70.8 x 38.4 x 20.5 | vertical, rear of trunk, z 81-152 |
| Power support (battery cradle) | 54.5 x 17 x 83.5 | |
| Compute board | 65 x 30 (Pi-Zero footprint) + 65 x 30 "robot hat" | production RK3566 (Radxa-Zero-3W class) |
| Thigh plate (upper_leg) | 61 tall x 47.7 x 28 | rounded triangle, 2 screws |
| Shin ("leg") sheet | 58 x 20 x 8 | grey; large 22x16x4 bearing at knee |
| Ankle block | 39.5 x 36.5 x 25.5 | XL330 vertical |
| Foot cap | 54 long x 40.1 wide x 16.9 tall | accent colour; top slot |
| Sole (TPU) | 54 x 41.1 x 12.9 | rounded rect, slightly proud |
| Foot height total | ~19 mm (z 2.8-21.2) | |
| Hip yaw2roll block | 23 x 25.8 x 20.5 | + XL330 |
| Servo XL330-M288-T | 20 x 34 x 29 (with horn) | 14 in kinematic chain + jaw |
| Roller-skate | tire Ø30 x 7.6, rim Ø20.2; blade 73 x 40.5 x 30 | clips under foot |
| Speaker | 35 x 25 x 7 | rear of head |
| Bearings | 22 x 16 x 4 (hips, knees), 15 x ? x 3 | Seeed listed |

## Ratios (for matching the photos)
- Head length / total height: 0.46 (CAD 123/268); photo measure on the store profile shots: 0.42 cream, 0.39 graphite (head pitched down, so foreshortened). Head height / total: ~0.25 incl. beak.
- Head width / trunk width: 92 / 62 = 1.48. Head width / foot-track width: 92 / 142 = 0.65.
- Trunk length / total height: 82 / 268 = 0.31. Trunk sits from 0.45 to 0.60 of total height.
- Leg (hip pitch to sole) / total height: (102.5 - 0) / 268 = 0.38; thigh = shin = 42 mm = 0.16 each.
- Eye ring Ø / head width: 30 / 92 = 0.33; eye centre at ~48 % of face height from the beak lip.
- Beak (jaw) protrusion / head length: 69 / 123 = 0.56 (the jaw reaches to roughly the front face; it does not overhang much when closed — the "bill" look comes from the ~10 mm colour lip under the head).
- Foot length / total height: 54 / 268 = 0.20; foot width 41.

## Scale references present in images
- NP-F550 battery in `store_microduck-inside-the-box.png` (70.8 x 38.4 mm); Xbox/8BitDo-style controllers (~150 mm) in `press_desk`, `press_skate`; keyboard key pitch 19 mm in `press_closeup`/`press_morning`; adult hands in `blog_scale-in-hand`, `press_carried`, `press_stickers`; foam ball ~65 mm in `press_kickabout`; book spines in `store_microduck-squad-sitting`.

## Notes for reverse engineering
- Servo count: 2x5 legs + neck pitch + head pitch + head yaw + head roll + jaw = 15. Hip yaw servos are inside the trunk pointing down; hip roll servos lie horizontal in the grey clevis; hip pitch, knee(?) and ankle are XL330s outboard. In the MJCF the knee is driven by the servo at the hip (the thigh houses one servo, the shin is a passive sheet with a bearing) — the shin's servo body visible at the bottom of the leg is the **ankle** servo.
- The trunk_base is a 57 x 36 x 3 mm plate; both hip-yaw servos bolt to it with 22x16x4 bearings on the output side.
- Head is assembled from: top shell, bottom shell, face panel, eye cone, lens holder, jaw, jaw soft pad, soft mouth top, neck_pitch bracket, yaw_roll_motion block, speaker, camera PCB, head IMU.
- Onshape document for the robot: `https://cad.onshape.com/documents/804927696f06d877f3f1803e/w/5b75db19292e71970de02dee/e/ef6e972847fec8d82570b35e` (private; the exported STLs are what we have).
