# WIRING — what is connected to what, and how long each cable is (GOAL.md rung 5)

*Written 2026-09-02. The ce-wire design is `designs/microduck/design.json`
(the only input; everything beside it in that folder is `bin/wire build`
output). Every length is in `cables.json` / `CABLES.md`, written by
`measure.py` off `ce-assemblies/microduck/current/placements.json` and
`joints.json` — nothing in this page is a typed length; the numbers quoted
below are copied from that run and say so.*

```bash
export CE_WIRE_ROOT=/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck/wiring
export CE_PARTS_ROOT=/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck/ce-parts
/Users/leifrydenfalk/dev/ce-workshop/ce-wire/bin/wire build microduck     # rewrites designs/microduck/{nets,checks,validation}.json, wiring.svg, schematic.svg, README.md
/Users/leifrydenfalk/dev/ce-workshop/ce-wire/bin/wire check microduck     # exit 3 = CANNOT DETERMINE (recorded in check.txt)
CE_PARTS_ROOT=$CE_PARTS_ROOT python3 measure.py                            # rewrites cables.json, drop.json, CABLES.md
```

## Files

| file | what | source or derived |
|---|---|---|
| `designs/microduck/design.json` | the ce-wire document: host `radxa-zero-3w`, 22 nodes, 26 nets | **source** |
| `designs/microduck/nets.json`, `checks.json`, `validation.json`, `wiring.svg`, `schematic.svg`, `README.md`, `DERIVED` | `bin/wire build` output | derived |
| `check.txt`, `show.txt` | `bin/wire check` / `bin/wire show` output, recorded | derived |
| `measure.py` | the measurement: connector points, route floors, slack rule, `cecad.harness.check_drop` | **source** |
| `cables.json`, `CABLES.md`, `drop.json` | every cable with both endpoints in world mm, floor, slack, cable length; the drop cascade | derived |

Records written for this lane on the design shelf (`ce-parts/`): `microduck-robot-hat-pcb/electrical.part.json`,
`microduck-imu-to-dxl/`, `microduck-tof-module/`, `microduck-camera-module/`, `microduck-mic/` (new folders,
each with `component.json` = CANNOT DETERMINE and the reason). Additive fixes so the shelf loads in
`cecad.netlist` at all: `np-f550/electrical.part.json` (`provision` beside `need` on both provides),
`radxa-zero-3w/electrical.host.json` (HostSpec keys `slug`…`requires` added in front of the rung-4 record),
and a `peak_basis`/`sleep_basis`/`typical_basis` sentence on the null currents of `bmi088`, `et7301b`,
`fusb302`, `imx219`, `tlv320aic3104` (each says "not transcribed here — not zero").

## 1. The Dynamixel daisy chain — order, and why it branches

One UART (`/dev/ttyS2` = RK3566 UART2_M0, 40-pin pins 8/10, docs §3.1 + `part:radxa-zero-3w`), one
half-duplex DATA line out of the HAT's transceiver (part CANNOT DETERMINE), 16 devices. An XL330 has
exactly **two** JST EH 3-pin sockets, one on each ±y flank (`XL,XC-330.pdf` side views; the pockets
measured in `ce-parts/xl330-m288-t/current/cad/part.py`), so a chain through servos is strictly linear.
The robot is a tree (head string, left leg, right leg), so it needs one device with three or more bus
connectors, and the only candidate in the trunk is the `imu_to_dxl` board — whose connector count is
**CANNOT DETERMINE** (docs §4.1). The chain is written with the branch there and says so:

```
HAT (head) ─ 34 mouth ─ 33 head_roll ─ 32 head_yaw ─ 31 head_pitch ─ 30 neck_pitch ─ imu_to_dxl (ID 200, trunk)
                                                                                        ├─ 20 L hip_yaw ─ 21 L hip_roll ─ 22 L hip_pitch ─ 23 L knee ─ 24 L ankle
                                                                                        └─ 10 R hip_yaw ─ 11 R hip_roll ─ 12 R hip_pitch ─ 13 R knee ─ 14 R ankle
```

Servo → joint → body is `docs/ELECTRONICS-AND-SOFTWARE.md` §3.2 and `placements.json` (row numbers in
each node's `note` in `design.json`; `measure.py SERVO_ROW`). The two servos sharing a body were told
apart by `joints.json` (`a.instance` of each hinge names the placements row that drives it).

**Hop length rule** (stated once, in `measure.py`'s docstring and `cables.json.record.rule`):

* **floor** = polyline from the chosen socket of servo A → the world origin of every hinge on the
  kinematic path between the two bodies → the chosen socket of servo B. A hinge origin is on its own
  axis, so this length is the same in every pose: a floor over the whole joint range, not at one pose.
* **slack** = Σ(range span in rad) × 10 mm, 10 mm being half the XL330's 20 mm width (`part.py BODY_Y`):
  the cable is assumed to pass the axis at the servo's flank, so a full sweep pays out that arc.
* **cable** = ⌈(floor + slack) / 5⌉ × 5 mm. It is a floor with a stated allowance, not a loom: a real
  cable goes around bodies and bearings and carries a service loop. ROBOTIS' stock lengths are on no
  fetched vendor page (`part:xl330-m288-t connector.x3p`), so no "nearest stock cable" is claimed.
* socket side (+y / −y) per hop = whichever gives the shorter floor; the other flank is the next hop's.

Sixteen hops, copied from `CABLES.md` (2026-09-02 run): 35, 60, 50, **165** (32→31, through head_yaw
±170° and head_pitch ±90° — 74.1 mm floor + 90.8 mm slack), 35, 120 (30→IMU through neck_pitch), 40,
65, 125 (hip_roll + hip_pitch), 20, 95 (knee), and the mirror 40, 65, 125, 20, 95 mm. Chain total
**1155 mm**. Both ends JST EH 3-pin (EHR-03 / SEH-001T-P0.6, `part:xl330-m288-t connector`), 3 conductors,
21 AWG per ROBOTIS (E1 verbatim "Wire Gauge for DYNAMIXEL | 21 AWG").

## 2. The HAT harness — and the routing problem, measured rather than assumed

The brief asked for the CSI ribbon length "through the ±170° head yaw". **Measured, it does not go
through it:** the Radxa (placements row 51, centroid (68.1, 0, 251.1)), the HAT (row 45, centroid
(59.6, 0, 251.1)), the lens (row 37), the camera site (81.4, 0, 251.1), the ToF site and the speaker are
all in MJCF body `jaw_soft` — the head. The CSI ribbon crosses **no joint**; its floor is 13.3 mm
between the Radxa centroid and the camera site (cable row 15 mm; the CSI connector sits at a short
edge of the 65 × 30 board, so the true floor is up to ~32 mm either way — the connector's place is not
in any fetched drawing, CANNOT DETERMINE).

The cable that DOES cross the ±170° yaw is the **battery feed**: the pack is in the trunk (row 6) and
the HAT that everything is powered through is in the head (docs §9 "battery → banana contact PCB →
HAT → 40-pin"). `bat-hat` runs pack contact end → neck_pitch (150°) → head_pitch (180°) → head_yaw
(340°) → head_roll (50°) → HAT: 213.5 mm floor + 125.7 mm slack = **340 mm**, two conductors carrying
the whole robot. It shares that path with the head string of the servo bus (hops 32→31 and 30→IMU).
**That is the routing problem to name:** 720° of accumulated joint range on one two-wire power cable,
with a 340° yaw in the middle, in a neck that is two 2 mm plates 50 mm apart (`docs/PARTS.md` row 19).
A slip ring, a cable carrier, or a yaw stop below ±170° in the harness is a product decision (not
answered here; the MJCF range is Pollen's).

The rest of the HAT harness (all in the head, no hinge crossed):

| cable | from → to | pins | floor / cable mm | connector |
|---|---|---|---|---|
| `tof-hat` | HAT J5 → ToF site | GND, 3V3, SDA, SCL (I2C3, 0x29) | 31.3 / **35** | JST-SH 4-pin 1 mm (Stemma) at J5 (`i2c3.dts:10`); board end CANNOT DETERMINE |
| `spk-hat` | HAT → speaker centroid | SPK+, SPK− | 65.0 / **70** | representative 3525 speaker's JST GH 1.25 lead; amplifier vs codec output CANNOT DETERMINE |
| `mic-hat` | HAT → mic | MIC, BIAS, GND (codec Mic3R, community) | **CANNOT DETERMINE** — no mesh, no site | CANNOT DETERMINE |
| `csi-radxa-camera` | Radxa CSI → IMX219 board | 22-pin: CLK, D0, D1, I2C2, PDN, 3V3, GND | 13.3 / **15** | 22-pin 0.5 mm FFC at the Radxa; camera end CANNOT DETERMINE |
| `bat-hat` | pack contacts → banana PCB → HAT | BAT+, BAT− | 213.5 / **340** | contacts and HAT input CANNOT DETERMINE |
| `hat-radxa-40pin` | HAT ↔ Radxa | 5 V (2/4), GND, UART2 (8/10), I2C3 (3/5), I2S3 M0 (asserted) | **0** — board-to-board header | 2×20 0.1" |
| `hat-dxl-port` | HAT → bus | SERVO_V, DXL_DATA, GND | not a separate cable: it *is* hop `dxl-hat-id34` (qty 0) | HAT end CANNOT DETERMINE |

HAT, Radxa, speaker and battery endpoints are mesh **centroids** (bbox centre through the placement)
because none of those boards has a published connector position; every such row says `centroid` in
`cables.json`. The battery contact end is the pack end nearer the `banana_pcb_locker` centroid —
measured, not assumed (they are 5 mm apart: (−35.4, 0, 151.5) vs (−30.4, 0, 154.8)).

## 3. Every cable, and the servo-bus voltage drop

The full table is `CABLES.md` (23 rows, one per cable, qty 0 for the non-cable rows). Totals from the run:
**22 cables, 1615 mm** over the 21 with a length; `mic-hat` undetermined; `hat-radxa-40pin` 0 mm.

Voltage drop — `cecad.harness.check_drop` on a `Harness` per hop (`measure.py harness_for`), the
tool's own copper arithmetic (ASTM B258 / IEC 60228, 20 °C, the temperature correction NOT applied),
cascaded so each hop's supply is the previous hop's received voltage. Bases, as passed to the call:

* current: **1 A per moving servo**, applied to every servo downstream of the hop — the brief's basis;
  the vendor publishes no running current (only standby 17 mA and stall 1.47 A at 5 V), so the number
  sits between them and is an assumption, stated. The IMU board's 0.65 mA (chip only) is left out.
* supply: 8.2 V = the runtime's "full", 6.6 V = its "empty" (`model.rs:99-128`), the bus VDD being
  the pack passed through the HAT — itself docs §3.4 open question 1 (stock XL330s are rated 3.7–6.0 V).
* min_v: 3.7 V = the XL330's published lower bound (E1), the only vendor minimum there is.
* gauge: **21 AWG** is the vendor figure and is the primary run; **22 AWG** (the brief's "use 22 AWG as
  ROBOTIS' cable") is run beside it — the fetched e-Manual says 21, so the brief's figure is superseded
  by the record and both are shown.
* length: the **cable** length (floor + slack), so the drop is over the whole cable, not the floor alone.

| run | verdict (vs 3.7 V) | received at the far ankles (24/14) | HAT → ankle drop | what it means for the 6.6 V empty threshold |
|---|---|---|---|---|
| 21 AWG, 8.2 V | PASS, all 16 hops | 7.650 V | **0.550 V** | — |
| 21 AWG, 6.6 V | PASS, all 16 hops | 6.050 V | 0.550 V | the far ankle reports **550 mV below** the threshold robotd reads from the servos: the farthest device trips "empty" first |
| 22 AWG, 8.2 V | PASS | 7.506 V | **0.694 V** | — |
| 22 AWG, 6.6 V | PASS | 5.906 V | 0.694 V | 694 mV early |

Biggest single hop: `dxl-hat-id34` carries all 15 A for 35 mm (44 mV at 21 AWG) but the 165 mm
`dxl-id32-id31` at 12 A drops **166 mV** on its own — the yaw/pitch crossing is both the longest hop and
the one the whole body's current still flows through. A PASS here is necessary, not sufficient
(`check_drop` docstring): the length is a floor with a stated slack, the current is an assumption, and
the wire's temperature rise is not modelled. Not judged: whether 15 A through one JST EH contact is
acceptable — JST's EH rating is on the workshop shelf (`part:conn-jst-eh-2.5mm`) but was not read here.

## 4. `bin/wire check` — recorded

`check.txt` (2026-09-02):

```
  microduck            CANNOT DETERMINE             18 not-PASS finding(s)
```

exit **3** = CANNOT DETERMINE; **0 FAIL**; 71 findings, 53 PASS. The 18 are all of two kinds, and both
are the documents' silence, not a wiring defect (`designs/microduck/checks.json`):

* `current/*` (12): SERVO_V's 15 servos have no published running current; VBAT, V5_HAT, MICBIAS and
  the camera's VCC_3V3 have no sourced draw; J5_3V3's 95 / 150 mA demand is known but the HAT's
  supply limit is not. Each finding says "not 0 mA, not any number".
* `vocabulary/*` (6): the speaker's `SPK±` and the mic's `MIC` are `audio_output` / `audio_input`
  terminals, outside netlist's supply/ground/signal/endpoint vocabulary — carried as signals and
  reported, which is the honest reading of a voice coil.

What the check did establish: 26 nets, GND degree 22, DXL_DATA degree 17 (the HAT + 16 devices —
the bus), I2C3 SDA/SCL degree 2 each (HAT + ToF; the codec and BMI088 are *on* the HAT), no pin
claimed twice, host power 2 of 2 needs joined, every net with a source
(`show.txt`). `ce-wire`'s own loom-drop lane stays UNCHECKED by design (it has no geometry) — the
drop above is the `cecad.harness` call this lane made itself.

## 5. Tool gaps met (P11), each named

1. `cecad.harness.wire(asm, a, b)` measures a route off connectors of kind `electrical` declared on
   parts. `part:xl330-m288-t` declares none (`component.json`: interfaces not yet written), so the
   route was measured from the placements directly and `check_drop` fed a hand-built `Harness`. The
   fix is an `electrical` connector at (6.85, ±10, −9) in the XL330's `cad/part.py`/`interfaces.json`.
2. `cecad.shelf.root()` reads ONE `$CE_PARTS_ROOT`; the design-local shelf is the only one carrying
   these parts, and it did not load until four records were made loader-clean (above). `CE_TRIAD_ROOT`
   is not honoured by the netlist loaders.
3. `cecad.unify.bind()` runs under `bin/cad` against a built `Assembly`; `assembly:microduck` is the
   MJCF-seeded placements record, not a kernel assembly with electrical connectors, so no binding
   was made. The label ↔ placements-row map lives in `design.json` notes and `measure.py SERVO_ROW`.
4. The `imu_to_dxl` board, the HAT, the banana contact PCB, the mic and the camera board have no
   vendor document; their records are what Pollen's source and device tree let one say.

## 6. CANNOT DETERMINE — the list

* HAT: transceiver, regulators, every connector (bus header, J5's 3.3 V source, battery input, speaker,
  mic), I2S3 mux (M0 asserted), NFC, REC LED. Cable endpoints on it are the board centroid.
* `imu_to_dxl` v2: connector count (the chain's branch depends on it), input band, board current.
* Servo bus VDD: raw pack vs regulated (docs §3.4); running current per servo (1 A assumed).
* ROBOTIS X3P stock lengths; whether Pollen uses X3P leads or its own EH crimps.
* ToF generation (L5CX/L8CX) and breakout; camera module, ribbon part and its connector at the camera
  end; the CSI connector's position on the Radxa.
* Mic: part, position, count, connector — no length possible.
* Speaker drive (codec output vs amplifier); speaker terminal side.
* Battery contact layout (no vendor drawing) and the banana PCB's connector to the HAT.
* Whether 15 A through one JST EH contact pair at the HAT port is within JST's rating (not read).
