# Microduck construction manual

*Authored 2026-09-02 from `joints.json` (14 MJCF hinges), `placements.json`
(70 placements), `docs/PARTS.md`, `docs/ELECTRONICS-AND-SOFTWARE.md` §3.2 and
`wiring/CABLES.md`. `bin/manual` was not used: it requires a `design.py`
exposing `system()`, which this triad assembly does not have. Step order:
trunk -> hips -> legs -> neck -> head, then wiring.*

**Fastener flag.** No screw list is published by Pollen. Every M2 count below
is **community-derived** (fanhao375/microduck-replica hole-fitting on the
sim meshes — `docs/PARTS.md` §5): clearance Ø2.2/2.4, counterbore Ø4.4, tap
Ø1.6. FDM holes print 0.1–0.3 mm undersize; drill or ream before assembly.
Our rebuild uses M2 heat-set inserts where a thread is loaded (SPEC §6);
production may tap the plastic — CANNOT DETERMINE.

**Servo rule.** Set each XL330's ID (and baud 1 Mbps, `baud_rate = 3`)
BEFORE installing it — the bus is one daisy chain and a duplicate ID means
disassembly. IDs per `docs/ELECTRONICS-AND-SOFTWARE.md` §3.2
(`model.rs:15-19`). All servos: Dynamixel Protocol 2.0.

**Bearing rule.** All bearings are press-fit into printed seats
(`ce-connections/press-fit-bearing-15x10x3`, and 22×16×4 seats). Press with
even force on the OUTER race only (an arbor press or a vice with a socket);
each 22×16×4 sits on a servo axis opposite the horn — the idler side.

## Step 1 — Trunk (body `trunk_base`)

Parts: microduck-trunk-base ×1, microduck-power-support ×1,
microduck-banana-pcb-locker ×1, banana contact PCB (P3), NP-F550 battery,
2 × XL330, 2 × bearing 22×16×4.

1. Press the two 22×16×4 hip-yaw idler bearings into trunk_base at
   (6, ±17.5, −5) mm body-frame.
2. Set servo IDs **20** (left hip yaw) and **10** (right hip yaw); bolt both
   XL330s hanging from trunk_base, output horns down (−z), horn axes through
   world (6, ±17.5, 115). Each XL330 carries its own M2 pattern
   (4 × Ø2.0 + 8 × Ø1.6).
3. Bolt power_support (the battery cradle) to trunk_base — power_support has
   8 × Ø1.6 M2 tap holes [community]; use M2×6 into inserts.
4. Clamp the banana contact PCB onto power_support's Ø3.9 pins with
   banana_pcb_locker — 2 × M2 through its Ø2.17 eyes.
5. The NP-F550 slides into the cradle against the banana contacts (do not
   fit the battery until Step 8).

Fasteners this step: trunk_base has 4 × Ø2.3 M2 clearance; ~10 × M2 total
[community, flagged].

## Step 2 — Hips (bodies `yaw2roll`/`bearing_roll`, `hip_l`/`hip_l_2`)

Parts per side: microduck-yaw2roll ×1, microduck-bearing-roll ×1,
microduck-hip-bracket ×1, 2 × XL330, 2 × bearing 22×16×4.

1. Set servo IDs **21** (left hip roll) / **11** (right hip roll).
2. Press one 22×16×4 into yaw2roll/bearing_roll at (0, 16.5, 12.5)
   body-frame (hip-yaw idler side) and one into each hip bracket at
   (21/25, 0, −18.5) (hip-roll idler side).
3. Fix yaw2roll to the hip-yaw servo horn (spline `spline-xl330-horn`);
   the bearing_roll 3 mm plate rides the idler bearing opposite the horn —
   4 × M2 clearance [community].
4. Mount the hip-roll servo in yaw2roll (8 × M2 clearance + 6 c'bore
   [community]); roll axis +x at world (22.5, ±17.5, 102.5).
5. Fix hip-bracket (hip_l) to the hip-roll horn — 9 × M2 clearance +
   6 c'bore [community]. Hip-pitch axis +y at world (4, ±42.5, 102.5).
6. Mirror for the right side (IDs 10/11 set in Step 1/2).

## Step 3 — Legs (bodies `upper_leg_*`, `leg`, `ankle_*`)

Parts per side: microduck-upper-leg ×1, microduck-upper-leg-rigidity-plate
×1, microduck-shin ×1, microduck-ankle ×1, microduck-foot ×1, sole (TPU) ×1,
3 × XL330, 2 × bearing 22×16×4, 1 × bearing 15×10×3.

1. Set IDs **22** hip pitch, **23** knee, **24** ankle (left);
   **12**, **13**, **14** (right).
2. Fit the hip-pitch and knee servos into the upper-leg housing (2 XL330
   per thigh; knee axis −y at (−31.8, ±38.5, 80.5)); press one 22×16×4
   into the upper leg at (22, 35.8, −4) body-frame.
3. Screw the 1 mm rigidity plate across the thigh — 4 × M2 clearance
   [community].
4. Hang the upper leg on the hip bracket: horn side to the hip-pitch servo,
   idler side on the bracket's bearing.
5. Fit the ankle servo into the shin (`leg` body; the shin is the 8 mm
   stepped plate) — 6 × M2 clearance + 6 c'bore [community]; join shin to
   knee horn + idler bearing.
6. Press the 15×10×3 bearing into the ankle bracket; fix ankle to the ankle
   servo horn (5 × M2 clearance + 5 c'bore [community]).
7. Screw the hard foot to the ankle (fixed, no joint), then fit the TPU
   sole onto the foot (the ground-contact part, friction surface down).

## Step 4 — Neck (body `neck`, `neck_pitch`)

Parts: microduck-neck-plate ×2, microduck-neck-pitch-bracket ×1, 2 × XL330,
1 × bearing 22×16×4.

1. Set IDs **30** (neck pitch, bottom) and **31** (head pitch, top).
2. The two 2 mm neck plates span the 50 mm neck with a servo at each end —
   4 × M2 clearance per plate [community]. Neck-pitch axis −y at world
   (26, 14.5, 152.4); head-pitch axis +y at (26, 14.5, 202.4).
3. Bolt the ID-30 servo to the trunk (horn to the neck plates); bolt ID-31
   at the top of the plates.
4. Press one 22×16×4 into neck_pitch at (0, 20.8, −14.5) body-frame — this
   is the head-yaw axis bearing; fix neck_pitch to the ID-31 horn — 12 × M2
   clearance + 4 c'bore [community].

## Step 5 — Head (bodies `yaw_roll_motion`, `jaw_soft`)

Parts: microduck-yaw-roll-motion ×1, microduck-motor-support ×1,
microduck-face-part ×1, microduck-eye-ring ×1, m12 lens + holder, IMX219
camera board, ToF module, Radxa Zero 3W, Robot HAT, speaker,
microduck-top-head-shell ×1, microduck-bottom-head-shell ×1, microduck-jaw
×1, jaw-soft + soft-mouth-top (TPU), 3 × XL330, 2 × bearing 22×16×4,
1 × bearing 15×10×3.

1. Set IDs **32** (head yaw), **33** (head roll), **34** (mouth).
2. Press two 22×16×4 bearings into yaw_roll_motion at x = −16 and +18
   body-frame (straddling the roll axis). Fix yaw_roll_motion onto the
   head-yaw axis: ID-32 horn below, neck_pitch's bearing above — 4 × M2
   clearance + 6 c'bore [community]. Head-yaw axis +z at world (26, 0, 221.1).
3. Mount the ID-33 head-roll servo in yaw_roll_motion; roll axis −x at
   (8.1, 0, 235.6).
4. Fix motor_support (the head plate) to the ID-33 horn. It carries the
   ID-33/ID-34 servos and the electronics.
5. Press the 15×10×3 bearing for the mouth hinge (body jaw_soft); mount the
   jaw on the ID-34 horn + that bearing — 5 × M2 clearance [community].
   Mouth range −5° (closed) … +30° (open).
6. Electronics onto motor_support / face: screw the M12 lens holder to the
   IMX219 board (3 × M2), thread the lens; camera sits behind face_part at
   world (81.4, 0, 251.1), **mounted upside down** (rotation 180 in the
   overlay). ToF at (81.4, 22.4, 249.1), 22.4 mm left of the camera. Fit
   eye-ring into face_part (10 × M2 clearance + 4 tap [community]). Stack
   the Robot HAT on the Radxa Zero 3W 40-pin header (board-to-board).
7. Fit the TPU lips: jaw_soft (8.4 mm) on the jaw, soft_mouth_top (3.3 mm)
   under the top shell.
8. Close the shells: bottom_head_shell (4 × M2), top_head_shell (3 × M2),
   trunk shells left/right (7 and 6+1 × M2) [all community].

## Step 6 — Wiring (from `wiring/CABLES.md`, measured route floors + stated slack)

One Dynamixel bus, 1 Mbps, `/dev/ttyS2` on the Radxa via the HAT. Daisy
chain order and cut lengths (JST EH 3-pin, X3P leads):

HAT → id34 (35 mm) → id33 (60) → id32 (50) → **id31 (165, crosses head yaw
+ head pitch — route at the servo flank, this length pays out the full ±170°
sweep)** → id30 (35) → imu200 board (120, crosses neck pitch) → splits:
imu200 → id20 (40) → id21 (65) → id22 (125) → id23 (20) → id24 (95) and
imu200 → id10 (40) → id11 (65) → id12 (125) → id13 (20) → id14 (95).

Other looms: ToF↔HAT Stemma J5, JST-SH 4-pin, 35 mm (I²C 0x29); speaker↔HAT
70 mm; battery→HAT 340 mm (crosses all four neck/head joints — route with
the bus loom); CSI ribbon Radxa→camera 15 mm floor (22-pin 0.5 mm FFC);
mic loom CANNOT DETERMINE (part/placement unknown). Voltage-drop check at
1 A/servo, AWG 21: PASS (worst drop 0.55 V HAT→ankle).

## Step 7 — Power-up and checks

1. Fit the NP-F550. Servo bus VDD is battery-direct through the HAT (the
   runtime reads pack voltage as the servos' own supply).
2. Scan the bus: expect IDs 10–14, 20–24, 30–34 and **200** (imu_to_dxl).
   The runtime asserts `return_delay_time = 0`, `baud_rate = 3`,
   `pwm_slope = 255`, `shutdown = 52` at boot.
3. Verify joint ranges against the MJCF (e.g. hip yaw −25…+30 left) before
   loading a policy.

*Torque figures: CANNOT DETERMINE — no torque spec exists in any fetched
source; M2 into plastic: snug + a quarter turn.*
