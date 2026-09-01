# BOM — what a Microduck rebuild has to buy, print and mould, with what it costs

*Written 2026-09-01. Pollen publishes no BOM. This one is assembled from the
product pages, the open runtime, the simulation meshes and the Open Duck Mini
v2 ancestry. A price appears only where a source states it; everything else
is CANNOT DETERMINE with what settles it. Companion docs: `PARTS.md` (every
part, dimensions, sources), `ELECTRONICS-AND-SOFTWARE.md` (how the boards
connect).*

Source key: as `PARTS.md` §"Source key"; plus [ODM] = `research/raw/odm_bom.csv`
(Open Duck Mini v2 Google-Sheets BOM, EUR, 2025) and [store-*] =
`research/raw/store_*.json` (Pollen Shopify JSON fetched 2026-09-01).

## 1. Bought items

| # | item | qty | vendor / MPN | price (published) | URL | source & notes |
|---|---|---|---|---|---|---|
| B1 | Dynamixel XL330 servo | 15 | ROBOTIS; sub-variant **CANNOT DETERMINE** (M288-T per community; never named by Pollen) | not in our sources (ROBOTIS lists it; would settle) | https://emanual.robotis.com/docs/en/dxl/x/xl330-m288/ | [R1 §4.1]; Pollen sells "3 × Motors" inside the €99.99 Dev Pack [store-devpack] |
| B2 | Dynamixel 3-pin TTL cables | 15–16 (bus daisy-chain + IMU board) | ROBOTIS X-series 3-pin (JST-type) — exact part/lengths CANNOT DETERMINE | — | — | "5 × Motor Cables" spare in Dev Pack [store-devpack] |
| B3 | Radxa Zero 3W | 1 | Radxa, RK3566, 1 GB LPDDR4 / 32 GB eMMC variant, Wi-Fi 6 / BT 5.4 | not in our sources | https://radxa.com/products/zeros/zero3w/ | `i2c3.dts:46`; [presskit] 1 GB / 32 GB |
| B4 | NP-F550 battery, 2600 mAh, 2S Li-ion | 1 (+ spares) | Sony-format L-series; brand CANNOT DETERMINE | Charger Pack: **2 batteries + dual charger €33 / $39** | https://store.pollen-robotics.com/products/charger-pack | [store-charger]; [presskit] |
| B5 | Dual battery charger (NP-F) | 1 | CANNOT DETERMINE (specs, current) | included in B4's €33 | same | [store-charger] |
| B6 | IMX219 camera board with M12 mount | 1 | Pi Camera v2 sensor class; exact board CANNOT DETERMINE | — | — | `media:312`; meshes `m12_lens_holder`, `lens` [SPEC §4.3] |
| B7 | M12 wide-angle lens | 1 | FOV CANNOT DETERMINE ("still being finalised", press kit; community ~62°) | — | — | [R1 §7.1] |
| B8 | 22-pin MIPI CSI ribbon | 1 | length CANNOT DETERMINE | — | — | [Radxa] "22-Pin MIPI CSI" |
| B9 | ToF module VL53L5CX **or** VL53L8CX, Stemma/Qwiic breakout | 1 | ST; generation CANNOT DETERMINE | — | — | `tof:83-85`; HAT "Stemma J5" `i2c3.dts:10` |
| B10 | ball bearing 22 × 16 × 4 | 11 | "seeed_bearing" (Onshape name); MPN CANNOT DETERMINE | — | — | [PL]; [C-fast] |
| B11 | ball bearing 15 × 10 × 3 | 3 | MPN CANNOT DETERMINE | — | — | [PL]; [C-fast] |
| B12 | speaker | 1 | CANNOT DETERMINE (35 × 25 × 7 placeholder) | — | — | [SPEC §4.3] |
| B13 | microphone(s) | ≥1 | CANNOT DETERMINE; codec input Mic3R mono [C-elec] | — | — | [R1 §7.4] |
| B14 | NFC antennas + reader IC | 2 + 1 | CANNOT DETERMINE | — | — | [presskit]; no code |
| B15 | REC indicator LED | 1 | CANNOT DETERMINE | — | — | [presskit] |
| B16 | Bluetooth gamepad (Xbox-style layout) | 1 | model CANNOT DETERMINE | included with robot | https://store.pollen-robotics.com/products/microduck | [R1 §2]; `cheat:236-249` |
| B17 | USB-C cable | 1 | — | included | same | [R1 §2] |
| B18 | Screws, inserts | see §4 | M2 socket-head family (community) | — | — | [C-fast]; "1 × Screw Pack" in Dev Pack |
| B19 | TPU / filament | see §2–3 | — | — | — | — |

### Custom PCBs (no design files exist — must be designed, not bought)

| # | board | what is on it | source |
|---|---|---|---|
| P1 | Pollen "RPI Robot HAT", 65 × 30 mm Pi-Zero footprint | TLV320AIC3104 codec (I²C 0x18, I²S3, 12 MHz MCLK), BMI088 (dormant, 0x19/0x68), Stemma J5 for ToF, 10 kΩ pull-ups R12/R13, battery power path to the board, (inferred) half-duplex Dynamixel transceiver | `i2c3.dts`; `aic.dts`; [C-elec] |
| P2 | `imu_to_dxl` v2 | LSM6DSV16X + MCU acting as Dynamixel Protocol-2 slave ID 200 serving a 12-byte block at register 124 (20-byte diagnostic) | `imu.rs:1-17`; `model.rs:78` |
| P3 | "banana" battery-contact PCB | contacts for the NP-F550, clamped by `banana_pcb_locker` | `PARTS.md` row 2 |

Chips on them, for pricing: TLV320AIC3104 (TI), LSM6DSV16X (ST), BMI088
(Bosch, could be omitted [C-elec]). Prices: not in our sources.

## 2. Printed parts

Material: SPEC.md §6 targets **FDM** for every custom part (walls ≥ 1.2 mm,
M2 bosses, heat-set inserts where loaded); our finished parts are recorded as
PLA/FDM (`ce-parts/microduck-{shin,trunk-base,banana-pcb-locker,power-support,upper-leg-left}/component.json`).
Community print guide suggests PETG/ASA for hard parts [R2 §1c, ScrapMeta].
Whether Pollen's shells are moulded: CANNOT DETERMINE ("printed" is the only
word, press kit [R1 §12]). **Grams per part: CANNOT DETERMINE** until sliced
— the mesh *solid* volume from [R2 §4.3] is given as the upper bound
(solid, no infill); the `cad-print` skill on our rebuilt parts settles it.

| slug | mesh | qty | colour role | solid vol cm³ [R2 §4.3] | rebuild |
|---|---|---|---|---|---|
| microduck-trunk-base | trunk_base | 1 | internal | 1.42 | T1 PASS |
| microduck-banana-pcb-locker | banana_pcb_locker | 1 | internal | 0.46 | T1 PASS |
| microduck-power-support | power_support | 1 | internal | 10.49 | T1 PASS |
| microduck-trunk-shell-left | left_shell | 1 | **colourway** | 11.4 | no folder |
| microduck-trunk-shell-right | right_shell | 1 | **colourway** | 11.4 | no folder |
| microduck-yaw2roll | yaw2roll | 2 | grey | 2.82 | T0 |
| microduck-bearing-roll | bearing_roll | 2 | dark | 0.63 | T0 |
| microduck-hip-bracket | hip_l | 2 | light | 4.53 | T0 |
| microduck-upper-leg-left | upper_leg_left | 1 | light | 4.15 | T1 PASS |
| microduck-upper-leg-right | upper_leg_right | 1 | light | 4.15 | T1 PASS |
| microduck-upper-leg-rigidity-plate | upper_leg_rigidity_plate | 2 | mint (1 mm — sheet? CANNOT DETERMINE) | 0.75 | T0 |
| microduck-shin | leg | 2 | pale blue | 3.41 | T1 PASS |
| microduck-ankle-left / -right | ankle_left / right | 1 + 1 | **trim** (orange/yellow) | 7.88 | T0 |
| microduck-foot-left / -right | foot_left / right | 1 + 1 | **trim** | 12.18 | no folder |
| microduck-neck-plate | neck | 2 | light | 0.40 | no folder |
| microduck-neck-pitch-bracket | neck_pitch | 1 | dark | 4.11 | no folder |
| microduck-yaw-roll-motion | yaw_roll_motion | 1 | pale blue | 4.56 | no folder |
| microduck-motor-support | motor_support | 1 | internal | 7.52 | no folder |
| microduck-top-head-shell | top_head_shell | 1 | **colourway** | 29.87 | no folder |
| microduck-bottom-head-shell | bottom_head_shell | 1 | **trim** | 23.80 | no folder |
| microduck-face-part | face_part | 1 | dark | 5.82 | T0 |
| microduck-eye-ring | noenoeil | 1 | dark | 4.25 | T0 |
| microduck-m12-lens-holder | m12_lens_holder | 1 | dark — bought or printed CANNOT DETERMINE | 1.10 | T0 |
| microduck-jaw | jaw | 1 | **trim** | 9.36 | no folder |

Printed count: 24 slugs, **31 pieces**. Solid-volume sum ≈ 183 cm³ (sum of
the column with quantities). Colourway hexes: Cream `#f7e6cb`, Graphite
`#6c6a68`, Lavender `#bfa9cf`, Sky `#a9dbe8`; trim orange (Cream, Sky) or
yellow (Graphite, Lavender) [presskit; R1 §12].

## 3. Soft parts (TPU — inferred)

| slug | mesh | qty | thickness | vol cm³ | basis |
|---|---|---|---|---|---|
| microduck-sole-left / -right | sole_left / right | 1 + 1 | 12.9 mm (the foot contact geom, friction 1.0 in sim) | 6.25 each | lilac/mint materials + "soft" names [SPEC §6]; community TPU 90–95A [R2 §1c]; ODM v2 used TPU 40 % infill for `foot_bottom_tpu` [R1 §16.1] |
| microduck-jaw-soft | jaw_soft | 1 | 8.4 mm | 18.6 | same |
| microduck-soft-mouth-top | soft_mouth_top | 1 | 3.3 mm | 2.7 | same |

Material and durometer: **CANNOT DETERMINE** — Pollen has not said; a
production unit's lip would settle it. Grams: CANNOT DETERMINE until sliced.

## 4. Fasteners (community counts — flagged, not Pollen's)

From `research/raw/community/replica_fastener-reconstruction.en.md` (hole
fitting on the 47 meshes): ~146 structural M2 clearance holes + 60 on the
servo bodies; depths 51 @ 0–3 mm, 24 @ 3–5 mm, 4 @ 8–12 mm.

| spec | community buy estimate (incl. spares) | flag |
|---|---|---|
| M2×4 socket head | 60 | lengths inferred from hole depth, not measured |
| M2×6 socket head | 80 | |
| M2×8 socket head | 40 | |
| M2×12 socket head | 15 | |
| M2 nuts | 50 | |
| M2 heat-set inserts | 60 | inserts vs tapped plastic on production: CANNOT DETERMINE |
| M2.5×6 | 20 | the 20 Ø2.7/2.8 holes |

Pollen corroboration: Dev Pack has "1 × Screwdriver" and "1 × Screw Pack"
[store-devpack]. Prices: not in our sources.

## 5. Cost roll-up

### 5.1 Reference points

| | price | source |
|---|---|---|
| Pollen Microduck, assembled, with gamepad + battery + cable | **$399** / **€340** (before tax/shipping); heise €440.30 delivered | [store-microduck]; [R1 §13] |
| + Charger Pack (2 batteries, dual charger) | $39 / €33 | [store-charger] |
| + Dev Pack (3 motors, 5 cables, 2 batteries, charger, 10 NFC tags, HF credit, screwdriver, screw pack) | $119 / €99.99 | [store-devpack] |
| + Accessory Pack (2 rollers, laser, NFC Polaroid, 10 tags, ball) | $39 / €33 | [store-accessory] |
| "Fully loaded" | $596 / €505.99 | [R1 §13] |
| Open Duck Mini v2 DIY BOM (14 × STS3215 servos, Pi Zero 2W, BNO055, 2 × 18650…) | **€398.10** (lowest-price column €331.10) | [ODM] row 24 |
| ODM v2 + "expression package" (speaker, LEDs, mic, projector, Pi camera) | €432.34 (lowest €365.34) | [ODM] row 34 |

### 5.2 Our line-by-line, with what is and is not priced

| line | qty | published price in our sources | ODM v2 analogue [ODM] | note |
|---|---|---|---|---|
| XL330 ×15 | 15 | CANNOT DETERMINE | 14 × Feetech STS3215 @ €14 = €196 | XL330 is a different (dearer, HN: "More expensive but better quality" [R1 §4.1]) family |
| Radxa Zero 3W | 1 | CANNOT DETERMINE | Pi Zero 2W €26.08 + SD €10 | Radxa has eMMC, no SD |
| NP-F550 ×1 + charger | 1 | €33 for 2 + charger (Pollen) → ≈ €16.50 per pack incl. charger share | 2 × 18650 €10 + holder €4.99 + BMS €8.40 + UBEC €4 + switch €4.49 + USB-C charger €9.99 + jacks/XT30 €10 = €51.87 | Microduck needs no BMS/UBEC/switch in the robot (pack has its own protection; no gauge, `model.rs:99-105`) |
| `imu_to_dxl` v2 (LSM6DSV16X + MCU) | 1 | CANNOT DETERMINE (custom) | BNO055 €40 ("Need to find a cheaper alternative") | |
| Robot HAT (codec, ToF conn., power) | 1 | CANNOT DETERMINE (custom) | Waveshare bus servo adapter €5 + amplifier €5 + speaker €6 + mic €15 | |
| IMX219 + M12 lens | 1 | CANNOT DETERMINE | Pi camera €5 ("Not integrated yet") | |
| ToF VL53L5/8CX | 1 | CANNOT DETERMINE | none on ODM | |
| bearings 22×16×4 ×11, 15×10×3 ×3 | 14 | CANNOT DETERMINE | 3 bearings €10.50 (€3.50 ea) | |
| NFC ×2 + IC, REC LED, mics | — | CANNOT DETERMINE | LEDs €0.60, eye diffusers €0.64 | |
| gamepad | 1 | included by Pollen | not in ODM BOM (Xbox One pad) | |
| filament PLA (~31 pieces) | — | CANNOT DETERMINE grams | "Maybe 500 g" €20 | Microduck is 1/3 the mass of ODM (737 vs 2107 g [R2 §1c]) |
| TPU (4 pieces) | — | CANNOT DETERMINE | "negligeable" €0 | |
| M2 screws / inserts | ~146 + spares | CANNOT DETERMINE | M3 inserts €5.99 | |
| cables, sheath | — | CANNOT DETERMINE | sheath €9 + USB cables €13 | |
| **sourced subtotal** | | **€16.50** (battery share only) | **€398.10** | |
| **unpriced lines** | | **13 of 14** | 0 | |

**Verdict on the roll-up:** with only the battery priced from a source, our
parts cost is CANNOT DETERMINE. What settles it, in order of weight: (1)
ROBOTIS XL330-M288-T list price × 15 — the servo line was 49 % of the ODM
BOM; (2) Radxa Zero 3W 1 GB/32 GB price; (3) a quote for the two custom PCBs
(P1, P2) at qty 1–10; (4) ST VL53L8CX breakout, IMX219 M12 board, bearings
from a distributor; (5) slicing our rebuilt parts for filament grams. The
structural comparison is already clear: Microduck removes the ODM's BMS,
UBEC, switch, foot switches (×4, €4), antenna servos (€6.66) and SD card, and
adds a ToF, an NFC reader, a codec HAT and a second IMU; the servo family
swap (STS3215 → XL330) is the dominant unknown.

## 6. What Pollen's $399 buys that this BOM does not

Assembly, calibration, the per-robot voice, signed updates with rollback
(`updaterd`), the pre-trained policies (Apache-2.0, free anyway), and the
warranty (terms CANNOT DETERMINE [R1 §19]). Lead time on 2026-09-01: "We
can't promise Christmas delivery for new microduck orders anymore" [store
banner, R1 §13]; eesel "4 to 6 months".
