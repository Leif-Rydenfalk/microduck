# LSM6DSV16X — the datasheet trail

*Written 2026-09-02 (elec-datasheets lane). Every figure quoted in
`../../../electrical.chip.json` was read off `../../../datasheet.pdf`, whose
URL, fetch date and sha256 are in `../../../PROVENANCE.json`.*

## 1. Identity — is this the part the Microduck carries?

| what the design says | source | what the datasheet says |
|---|---|---|
| "LSM6DSV16X, SFLP block gives a game-rotation quaternion and estimates its own gyro bias on-chip" | `duck-control/src/imu.rs:1-6` | cover p.1: *"6-axis inertial measurement unit (IMU) and AI sensor with embedded sensor fusion"*; §2.8 p.8: game rotation vector (quaternion), gravity vector, gyroscope bias |
| gyro ±500 dps, 17.5 mdps/LSB | `imu.rs:8-17` | Table 3 p.12: `G_So … FS = ±500 dps … 17.50 mdps/LSB` |
| quaternion x/y/z as fp16, w reconstructed | `imu.rs:8-17` | p.3: *"The X, Y, Z quaternion components are stored in FIFO."* — the **word format is not stated** in DS13510 (only the gyro-bias registers are described as half-precision, p.147); AN5763 would settle it |
| ~100 Hz, 25 blocks ≈ 0.25 s readiness | `imu.rs:96-100` | Table 20 p.33: 100 Hz exists only with HAODR_SEL = 10; the default column gives 120 Hz. Which imu_to_dxl v2 configures: not published |

The chip is on Pollen's **imu_to_dxl v2** board (DXL ID 200). The board's
schematic, MCU, strapping and firmware are not in the repository
(`docs/ELECTRONICS-AND-SOFTWARE.md` §4.1) — this folder is the **chip**.

## 2. Document fetched (2026-09-02)

| file | URL | identity |
|---|---|---|
| `../../../datasheet.pdf` | https://www.st.com/resource/en/datasheet/lsm6dsv16x.pdf — ST's own URL, HTTP 200, 5 112 242 bytes | `DS13510 - Rev 4 - May 2023`, 198 pages; every page footer `DS13510 - Rev 4  page N/198`; pdfinfo Author `STMICROELECTRONICS`, Creator `C2 … Techlit_Active`, created 2023-05-26 |

**Currency.** The st.com product page (`/en/mems-and-sensors/lsm6dsv16x.html`,
fetched the same day, 286 536 bytes, not kept — a live page) links this same
PDF and shows the badge **Active** ("Product is in volume production"). A web
search for a Rev 5 / Rev 6 found none; the index carries only Rev 3 (March
2023) and Rev 4 (May 2023). The workshop shelf's sibling `LSM6DSOX` record
could not reach st.com at all in August; today it answered.

Not fetched: AN5763 (device application note), TN0018 (design and soldering) —
both named on the cover, both needed for the two unknowns above.

## 3. What was extracted, verbatim, and where it went

- Table 4 *Electrical characteristics* p.14 → `supplies` (Vdd 1.71 / 1.8 / 3.6 V;
  Vdd_IO 1.08 / – / 3.6 V), `current_mA` (0.65 mA IddHP typ; 2.6 µA power-down;
  190 µA / 100 µA accel-only; Ton 30 ms), `logic` (0.7·Vdd_IO / 0.3·Vdd_IO,
  VOH Vdd_IO − 0.2 and VOL 0.2 at 4 mA), operating −40 … +85 °C.
- Table 9 *Absolute maximum ratings* p.19 → `absolute_max`.
- Table 3 *Mechanical characteristics* p.12 → `sensor` (FS ranges,
  sensitivities, noise, zero-rate level).
- Table 20 p.33 → `sensor.odr`.
- §5.1 / §5.1.1 / Table 8 / Table 12 pp.18–22 → `interface`, `i2c_address`
  (110101xb → 0x6A / 0x6B), fast mode 400 kHz / fast mode plus 1 MHz, *not
  tested in production*.
- §9.13 p.64 → `who_am_i` = 70h.
- §2.8 + Table 1 p.8, §13.30 p.139, §6 p.44, FIFO tag table p.110,
  EMB_FUNC_FIFO_EN_A p.131, §15.1.1 p.147 → `sflp`.
- §7.1 Figure 28 p.47 (100 nF on Vdd and Vdd_IO, Rpu = 10 kΩ, CS to Vdd_IO
  for I²C, pins 10/11 NC) and §18 p.174 → `application_circuit` — the reference
  layout an imu board package would cite.
- Cover p.1 + §19.1 Figure 33 p.175 → `package` (LGA-14L 2.50 ± 0.1 ×
  3.00 ± 0.1 × 0.86 MAX; 14 pads 0.25 × 0.475 on 0.5 pitch). The cover's
  0.83 typ and the drawing's 0.86 MAX are both recorded.

## 4. What the vendor does not say

`electrical.chip.json` `unknowns` — nine items. None of the board-level
questions (SA0 strap, I²C vs SPI, ODR, SFLP ODR, FIFO word format, rail) can
be answered from the chip datasheet; they are properties of imu_to_dxl v2.

## 5. Checks run

- `cecad.electrical.load_chips()` on a scratch shelf that unions the workshop
  shelf with this folder: `LSM6DSV16X` loads as a `ChipSpec`.
- `bin/triad check part:lsm6dsv16x` — see `../trust.json` and the ledger.
