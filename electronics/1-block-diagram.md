# Microduck — Block Diagram (Deliverable 1 of 3)

**File:** `electronics/1-block-diagram.svg` (clean vector, authored programmatically —
`tools`/scratch generator emits right-angle routes and pill labels; no hand-scribble).

This is the **first** of the three electronics files required by
`docs/MANUFACTURING-REQUIREMENTS.md §B` — the simple "how everything is supposed
to flow" view. **Functional blocks and the buses between them only. No pins.**
The schematic (`2-schematic.*`, every component + every pin) and the layout
(`3-layout.*`, physical connections + cable runs) add the detail on top of this.

Every fact and every bus rate is read out of `docs/ELECTRONICS-AND-SOFTWARE.md`
(which carries the file:line / page cites back to Pollen's own source and the
datasheets). House rule holds: **solid = read from source; dashed = inferred or
CANNOT DETERMINE, never guessed.**

## Blocks (functional)

| block | what | key source |
|---|---|---|
| **COMPUTE** | Radxa Zero 3W — RK3566, 1 GB LPDDR4, 32 GB eMMC, 0.8-TOPS NPU; RPI Robot HAT on the 40-pin header; the netlist host (28 nets) | §2; `electronics/netlist.json` |
| **POWER** | NP-F550 2S pack (6.6–8.2 V under load, 7.4 V nom, no fuel gauge) → banana contact PCB → RPI Robot HAT → 5 V rail (Radxa) + bus VDD (servos) | §9 |
| **SERVO BUS** | one TTL half-duplex chain, Dynamixel Protocol 2.0 — **16 devices**: 15 × XL330-M288 (IDs 10–14, 20–24, 30–34) + `imu_to_dxl` (ID 200) | §3 |
| **MOTION SENSING** | control IMU ST **LSM6DSV16X** (rides the servo bus as `imu_to_dxl`, ID 200) + head **BMI088** on I2C3, dormant | §4 |
| **VISION** | Sony **IMX219** + M12 wide lens, mounted upside-down (rotation 180) | §5 |
| **DEPTH** | **VL53L8CX / VL53L5CX** 8×8 ToF @ 15 Hz, on the HAT Stemma J5, `tofd` daemon | §6 |
| **AUDIO** | TI **TLV320AIC3104** codec (on HAT) + head mic + 35×25×7 speaker | §7 |
| **COMMS** | Wi-Fi 6 / BT 5.4 on-module; USB-C 5 V in (FUSB302 PD disabled) | §2, §9 |
| **NFC** | 2 antennas (head + beak); reader IC & bus **CANNOT DETERMINE** | §8 |

## Buses (labelled edges)

- **Power rails** — pack → banana → HAT → **5 V** to Radxa (solid); **bus VDD ~7.4 V**
  to the servos (**dashed — inferred**: the runtime reads the pack *through* the
  servos' own `present_input_voltage`, §3.4).
- **UART2 (M0) → `/dev/ttyS2`** — **1 Mbps**, 3.3 V TTL, the whole 16-device servo chain.
- **I2C3 · 400 kHz** — one shared bus: codec, ToF, dormant BMI088 (device I2C
  addresses belong in the schematic, not here).
- **I2S3 · 12 MHz** MCLK — audio data to the codec.
- **MIPI CSI (22-pin)** — camera.
- **on-module + USB-C** — the COMMS radios and the 5 V USB-C input.
- **bus unknown** (**dashed**) — NFC; no published code or reader IC.

## Read-back

Rendered (headless Chrome, 1280×900) and read back: the flow is legible at a
glance — power enters left, compute is the hub, the servo bus hangs below as a
single 16-device block, and the sensor/comms peripherals sit right, each on its
own labelled bus. Acceptance (`docs/MANUFACTURING-REQUIREMENTS.md`): one page,
no pins, every bus labelled, unknowns shown as unknown.
