# Open Duck Mini v2 (apirrone) — reference catalog and comparison with Microduck

Source: `https://github.com/apirrone/Open_Duck_Mini` (branch v2), README + `docs/assembly_guide.md` images (GitHub user-attachments), wiring diagrams, and 20 print STLs downloaded to `../../cad/odm_print/` for bounding boxes. Onshape doc: `https://cad.onshape.com/documents/64074dfcfa379b37d8a47762/w/3650ab4221e215a4f65eb7fe/e/0505c262d882183a25049d05`.
Published: ~42 cm tall with legs extended, BOM < $400, Feetech STS3215 serial servos (BOM lists 12; legs 2x5 + neck/head), Raspberry Pi Zero 2 W, 2x 18650 battery pack, BNO055 IMU, foot switches, 2 wire antennas. Mini version of Disney's BDX droid.

## Files
| file | px | what |
|---|---|---|
| `readme_1.png` | 820x1248 | Front 3/4 photo of the finished v2: white FDM shells, **trapezoid head box with two round lamp eyes + centre camera hole + flashlight module + wire antenna**, octagonal body with big flat side plates, black STS3215 leg stacks, black wedge feet. |
| `readme_2.png` | 820x1248 | Rear 3/4: rear of head with speaker/flash reflector, body rear plate, thigh side plates, two wire antennas. |
| `readme_3.png` | 820x1248 | Left side: head is a flat wedge with round speaker grille on the side, body hexagonal prism, thigh plates, foot wedge. |
| `community_collage.png` | 2760x1378 | 12 community builds (colours, LED eyes, one with printed "ears"). |
| `wiring_v2.png` / `wiring.png` | 1741x1462 / 3134x3072 | Electrical: Pi Zero 2 W, servo bus, IMU, foot switches, buck converter. |
| `assembly/01-04_*trunk*.png` | CAD | trunk_bottom + trunk_top with two 22 mm bearings for hip yaw; middle motor. |
| `assembly/05-10_*feet*.png` | CAD | Foot = `foot_bottom_tpu` + `foot_bottom_pla` + `foot_top` (wedge with servo cradle) + `foot_side`; foot switches press-fit. |
| `assembly/11-13_*shins*.png` | CAD | Shin = two flat printed side sheets + `leg_spacer`, servo at the ankle. |
| `assembly/14_*thighs*.png` | CAD | Thigh = same sheet sandwich with hip-pitch servo. |
| `assembly/15-20_*hips*.png` | CAD | `left/right_roll_to_pitch` (orange bracket), `roll_motor_top/bottom`, hip yaw servo in trunk; full leg pair. |
| `assembly/21-26_*neck*/*head_mechanism*.png` | CAD | Neck: 2 servos in series; head: pitch->yaw->roll printed brackets with a bearing ring. |
| `assembly/27-28_Mount_the_IMU.png` | CAD/photo | IMU on the trunk. |
| `assembly/29_Electronics.png` | photo | foot switch wiring. |
| `assembly/30-31_Battery_pack.png` | CAD | 2x 18650 in a printed pack with lid, mounted in the body. |
| `assembly/32-34_Head.png` | CAD/photo | head shell interior: Pi Zero, eye LEDs, speaker, antenna holders. |
| `assembly/35-38_Body.png` | CAD/photo | body_front / body_back / body_middle_top / body_middle_bottom around the trunk; finished robot. |
| `sheets/odm_assembly_1-4.jpg` (in `../sheets/`) | contact sheets of the above |

## Key dimensions (STL bounding boxes, mm)
| part | size | Microduck equivalent |
|---|---|---|
| head.stl | 199.8 x 197.3 x 59.4 (trapezoid box) | head 123 x 92 x 66 (loaf) |
| body_middle_bottom / top | 150 x 110 x 86 / 150 x 110 x 57 | trunk shells 82 x 62 x 36 |
| body_front / body_back | 110 x 143 x 10 / 110 x 125 x 40 | (none; Microduck trunk is a 2-piece pill) |
| trunk_top / trunk_bottom (structural) | 125.5 x 100.7 x 41 / 54 x 108 x 74 | trunk_base plate 57 x 36 x 3 |
| foot_top | 103.5 x 34.9 x 46 (wedge) | foot cap 54 x 40 x 17 |
| foot_bottom_tpu | 102 x 40.7 x 8 | sole 54 x 41 x 13 |
| knee_to_ankle sheet | 70.6 tall x 30.7 | shin 58 x 20 x 8 |
| neck sheet | 58 tall | neck link 50 |
| head_pitch_to_yaw | 72 x 45 x 32 | yaw_roll_motion 290k-tri block ~ 35 x 18 x 28 |
| left_eye | Ø35 | eye ring Ø30 (single) |
| antenna holder | 27 x 20 x 42 | none |
| overall | ~420 tall, ~200 wide head | 250-270 tall, 142 wide |

## What changed from Open Duck Mini v2 to Microduck (form language)
1. **Scale**: ~0.6x. ODM ~42 cm / STS3215 (20 kg·cm, 12 V, 2x18650); Microduck 25 cm / XL330-M288 (5 V, NP-F550). Leg links 70 mm -> 42 mm; head 200 mm -> 123 mm.
2. **Head**: BDX-style flat trapezoid slab with two round lamp "eyes" and wire antennas -> a rounded D-profile loaf with one big camera "eye", no antennas, and a **new articulated beak/jaw** (15th motor). ToF LiDAR window added next to the eye. Speaker moved inside.
3. **Body**: faceted octagonal box with large flat thigh side-plates hiding the legs -> small pill trunk with the mechanism exposed; thigh plates shrink to a rounded triangle; battery becomes an externally-swappable NP-F550 on the back instead of an internal 18650 pack.
4. **Legs**: same 5-DOF topology (yaw -> roll -> pitch -> knee -> ankle) and same "servo-at-hip, sheet shin, servo-at-ankle" layout, but printed flat sheets are replaced by grey folded/printed brackets with flanged bearings, and cables are routed visibly.
5. **Feet**: long black wedge (103 mm) with foot switches -> short rounded cap + TPU sole (54 mm) with a slot for clip-on roller skates; no foot switches (IMU-based contact estimation).
6. **Colour**: monochrome white/black -> four two-tone colourways with accent beak/feet/eye ring.
7. **Compute**: Pi Zero 2 W -> RK3566 + NPU (same 65 x 30 footprint), plus camera, mics, NFC.
