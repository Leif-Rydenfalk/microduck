# electronics/ — GOAL.md rung 4: the robot's electronics, known and checked

*Netlist lane, 2026-09-02. The datasheets are on the shelf (ce-parts/, docs/ELECTRONICS-AND-SOFTWARE.md §13); this folder is the robot as one `cecad.netlist.Design`, checked. The Robot HAT as a ce-pcb board is the next lane and lands in `electronics/robot-hat/`.*

## Run it

```
export CE_TRIAD_ROOT="/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck:/Users/leifrydenfalk/dev/ce-workshop"
python3 electronics/netlist.py              # exit 0 PASS · 2 FAIL · 3 CANNOT DETERMINE; writes the files below
python3 electronics/netlist.py --self-test  # every check broken on purpose; exit 0 only if every break is caught
```

| file | what |
|---|---|
| `netlist.py` | the Design: host `radxa-zero-3w`, 6 declared bus segments, 25 parts, 28 nets; nine cecad checks + four of its own (`volts/*`, `dxl/ids`, `i2c3/overlay`, `cross/wiring`); the self-test; the report writer |
| `netlist-report.md` | the three-verdict report — every finding in full, with its quote and cite |
| `report.json` | the same findings, machine-readable |
| `netlist.json` | every net and terminal (`cecad.netlist.netlist_json`) — what the HAT board lane `bind()`s to |
| `netlist.graph.json` | the `cecad.graph` document (declaration + derived nets + findings) |
| `firmware.json` | `cecad.netlist.firmware()` — buses, addresses, pins, per-net demand, every null with its reason |
| `elec-spec.json` | a `bin/elec` spec kept as the probe that records ce-elec's refusal (no RK3566 pin roster) |

## The verdict, 2026-09-02 02:20

**FAIL — 75 PASS · 15 FAIL · 28 CANNOT DETERMINE over 118 findings.**

What PASSes (the checks this rung asked for):

- one controller per bus: `i2c3`, `i2c2`, `uart2`, `dxl`, `i2s3`, `csi` — the Radxa, on the vendor's header pins ([brief] p.6 / [wiki])
- I2C3 addresses unique: codec 0x18, BMI088 0x19 + 0x68, ToF 0x29 — and equal to the set Pollen's overlays name (`i2c3/overlay`)
- the 16 Dynamixel IDs unique, inside 0..252, and exactly `JOINT_IDS` + `IMU_DXL_ID` read out of `model.rs` (`dxl/ids`)
- 19 pin identifiers, none on two nets (`gpio`); the host's 5 V and GND joined (`host_power`); every part's signal directions stated (`pin_directions`)
- connectivity agrees pair-for-pair with the rung-5 wiring lane's `wiring/designs/microduck/nets.json` over the 86 terminals both designs know (`cross/wiring`, 3655 pairs)

What FAILs — one thing, fifteen times: **`volts/SERVO_V`**. The runtime declares the servo bus at 6.6–8.2 V (`model.rs:109,113`, read through the servos' own Present Input Voltage) and the XL330-M288-T's band is 3.7–6.0 V ("Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])", ROBOTIS e-Manual). That is docs §3.4 open question 1 as a verdict: the design as published is over the vendor band. A meter on a production servo's VDD, or Pollen naming a regulated bus or a custom variant, settles it.

What is CANNOT DETERMINE, by name — all of it is the unpublished HAT schematic:

- `power/HAT_3V3`, `power/HAT_1V8`, `volts/HAT_*`: the codec's three domains and the BMI088's two sit on rails nothing on the shelf sources (regulator on the HAT, or the Radxa's 3.3 V — unpublished)
- `current/*` on every rail: the HAT's V5 and SERVO_V provisions carry null capacities (regulator / pass-through unpublished); the XL330 publishes idle and stall but no running current; the pack states no discharge rating
- `volts/SERVO_V imu200.VDD`, `volts/MICBIAS`: the imu_to_dxl board's input band and the mic bias level are unpublished
- `vocabulary/*`: SPK+/SPK−/MIC_IN — audio terminals cecad has no vocabulary for; whether an amplifier sits between codec and speaker is unpublished
- the transceiver behind `dxl/DATA` (ROBOTIS' reference is a 74LVC2G241 with a TX-enable that robotd never drives), the I2S3 mux (M0 asserted; M1 also on the header), MCLK's origin

## What the design file does that the records cannot

1. **Servo IDs.** Fifteen servos share one record, and the ID is an EEPROM register. Each servo is a design-level view of `part:xl330-m288-t` carrying its ID from `model.rs:15-19` as the design's assertion. The self-test puts two servos at ID 10 and the bus check says FAIL.
2. **BMI088.** One package, two I2C targets. cecad reads one address per owner, so the package is wired as `bmi088` (0x19 + supplies) and `bmi088.gyro` (0x68). The self-test moves the gyro to 0x18 and the check names the codec.
3. **HAT pass-throughs.** The HAT record states its header pass-throughs with `bus: I2C/UART`; on the netlist they are copper. Wired with `bus: None` (stated in the file); left as bus terminals they produce a "UART endpoint with no address" that says nothing about the robot — the self-test shows that too.

## Records written by this lane

- `ce-parts/tlv320aic3104/iterations/v0.0.1/electrical.part.json` (+ root symlink) — the codec as a part: three supply domains, I2C 0x18 ("001 1000"), I2S target
- `ce-parts/bmi088/iterations/v0.0.1/electrical.part.json` (+ root symlink) — two I2C targets 0x19/0x68 with the strap inference stated
- `ce-parts/xl330-m288-t/electrical.part.json` — additive: `address_selectable` + `address_basis` on the DATA need (the ID is a register)
- `ce-cad/cecad/netlist.py` `_address_conflict` — **tool fix found by the self-test**: on a bare host (no port standard, nets declared by the design) a duplicate bus address built a FAIL with an empty quote and `Finding` raised `ValueError` instead of reporting. Now quotes the device's own address record and carries the segment's declaration as the assertion. cecad's own `--self-test` output is identical before and after (63 OK; its two pre-existing conformance FAILs are unrelated).

## Tool gaps recorded (P11)

- `cecad/shelf.py` reads one `$CE_PARTS_ROOT`; `netlist.py` builds a symlink union of every `ce-parts` under `$CE_TRIAD_ROOT` in `~/.cache/ce-workshop/shelf-union/<hash>/` and refuses a slug present in two shelves.
- `Design._build_catalogue` admits a shelf record only if it carries `$from: parts.json`; records without it are outside every design's catalogue, which is why the wiring lane's report has no address findings at all. The two records above carry the marker; the servo views are admitted by the design (`_admit`).
- `bin/elec gpio|levels`: REFUSED — `host 'radxa-zero-3w' names no pin_roster`. There is no RK3566 roster in `cecad/data/controllers.json`; the Radxa's pins are the vendor's header table, checked for collisions, never for existence.
- cecad has no vocabulary for audio terminals (speaker, mic) — reported as CANNOT DETERMINE, never passed over.

## Robot HAT as a ce-pcb board

*(next lane — `electronics/robot-hat/board.py`, nets bound from `netlist.json`, DRC → gerbers; this section is its slot.)*
