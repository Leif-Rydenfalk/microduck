# XL330-M288-T — the datasheet trail

*Written 2026-09-02 (elec-datasheets lane). Every figure quoted in
`../../../electrical.chip.json` was read off the files in `fetched/`, whose
URLs, fetch date and sha256 are in `../../../PROVENANCE.json`.*

## 1. Identity — is this the part the Microduck carries?

| what the design says | source | what the vendor page says |
|---|---|---|
| "Dynamixel XL330" — sub-variant not stated | `spec/specs-published.json` (microduck_rl README: "the BAM M6 actuator model for the Dynamixel XL330") | ROBOTIS sells two: **XL330-M288-T** (288.4:1) and XL330-M077-T (77:1); same case, bus, controller, connector |
| `rustypot` `Xl330Controller`, Protocol 2, 1 Mbps, IDs 10–34, registers 124–146 | `bus.rs`, `model.rs` | Control table on the fetched page carries every address robotd names, with the same sizes and units (see §3) |
| 18 g, 20 × 34 × 26 mm, 288.4:1, 0.52 N·m at 5 V | `spec/specs-published.json` quotes of the same e-Manual page | identical rows on the page fetched today |
| the mesh `xl330.stl` is 29 × 20 × 34 with a Ø16 × 3 disc on both faces | `cad/part.py` | drawing D1 `[X330 IDLER]` view: 29 overall = 23 + 3 + 3, Ø16 bosses, 9.5 from top to horn axis, 4-Ø1.6 on PCD Ø12 — the idler variant of the same case |

Community says M288-T was "seen on press prototype" (`research/02-repos-and-code.md` §5.1);
Pollen never names the sub-variant. **This folder is the M288 page.** If a
shipped servo reads M077 on its label, the gear-ratio, torque and speed rows
change and nothing else on this page does.

## 2. Documents fetched (2026-09-02)

| id | file in `fetched/` | URL | what it is |
|---|---|---|---|
| E1 | `robotis-emanual-xl330-m288.html` | https://emanual.robotis.com/docs/en/dxl/x/xl330-m288/ | the vendor product page: Specifications, Control Table (EEPROM + RAM, every register described), Connector Information, Communication Circuit, Drawings, Certifications. HTTP 200, 359 049 bytes. No revision number on the page; its source file `docs/en/dxl/x/xl330-m288.md` in github.com/ROBOTIS-GIT/emanual was last committed `91f72d1d` on 2026-01-27 ("Modify X335"). Banner: *"ROBOTIS e-Manual has moved … This e-Manual website will be removed in July."* — still served in September 2026. |
| E2 | `robotis-docs-xl330-m288.html` | https://docs.robotis.com/docs/dxl/model_reference/x_series/xl_series/xl330-m288/ | the successor page, fetched for the currency check. Specifications table identical to E1. **One disagreement:** Shutdown(63) Bit 3 is `-` on E1 and `Motor Encoder Error` on E2; Bit 0 is `Input Voltage Error (default)` on E1 and `Input Voltage Error` on E2. Both give initial value 53. |
| D1 | `XL,XC-330.pdf` | E1 §Drawings "Download XL330.pdf" → robotis.com/service/download.php?no=1986 → Dropbox | one A4 sheet, "X330", 28-May-20, "[FOR REFERENCE ONLY]", mm, Nonescale |
| D2 | `XL330,XC330 Moment of Inertia.pdf` | E1 §Moment Of Inertia → download.php?no=2136 → Dropbox | "The moment of inertia (reference only)", Release Feb. 2023 |
| S1 | `../geometry/robotis-xl-xc-330.stp` | E1 §Drawings "Download XL330.stp" → download.php?no=1987 → Dropbox | vendor STEP, Creo export "DC15_A01_DUMMY_ASSY_IDLE_ASM" 2020-07-27 — **not yet measured on the kernel** |
| — | `3v3_ttl_circuit.png` | https://emanual.robotis.com/assets/images/dxl/3v3_ttl_circuit.png | E1 §Communication Circuit figure |
| — | `jst_b3beha_diagram.png` | https://emanual.robotis.com/assets/images/dxl/jst_b3beha_diagram.png | E1 §Connector Information diagram |
| P2 | `robotis-emanual-protocol2.html` | https://emanual.robotis.com/docs/en/dxl/protocol2/ | DYNAMIXEL Protocol 2.0 — the bus protocol (ledger `standard` row) |

Not fetched, and why: the ROBOTIS shop item the page links
(`en.robotis.com/shop_en/item.php?it_id=903-0220-001`) returned 102 bytes of
nothing; the US shop page (`robotis.us/dynamixel-xl330-m288-t/`, sku
902-0163-000, $27.49, InStock) was read for `sourcing.json` but is a live
store page and is not kept. The JST EH connector datasheet (`eEH.pdf`) is
already on the workshop shelf under `part:conn-jst-eh-2.5mm`, which
`refs.json` uses instead of a second copy (the file fetched today,
sha256 `9e35874b…`, is a different rendition from the one the shelf holds —
JST re-serves the PDF — so it was not adopted here either).

## 3. What was extracted, verbatim, and where it went

- **Specifications table** (E1) → `electrical.chip.json` `supplies`,
  `current_mA` (standby 17 mA; stall 1.11 / 1.47 / 1.74 A at 3.7 / 5.0 / 6.0 V),
  `logic` ("TTL Multidrop Bus (3.3V Logic, 5V Compatible)"), `controller`
  (Cortex-M0+ 64 MHz, AS5601 encoder, cored motor, 4096 pulse/rev, 288.4:1,
  no-load 76/103/123 rev/min, −5 ~ +70 °C, engineering-plastic case and gears).
- **Control table rows** 8, 9, 13, 31, 32, 34, 38, 62, 63, 64, 80/82/84,
  124–146 → `control_table_used_by_robotd`, each as the page prints it
  (`Address | Size | Name | Access | Initial | Range | Unit`), with the
  register descriptions robotd relies on: baud value 3 = 1 M bps; Return
  Delay default 250 = 500 µs; PWM Slope 1.977 mV/ms; Shutdown bit table;
  PID conversions KPP = KPP(TBL)/128 etc.; Present Input Voltage 0.1 V;
  Present Temperature 1 °C; Present Current 1 mA *measured at the input
  power source*.
- **Connector** → `connector`: pinout 1 GND / 2 VDD / 3 DATA; JST EHR-03,
  B3B-EH-A, SEH-001T-P0.6, 21 AWG.
- **Communication circuit** → `communication_circuit`: the 74LVC2G241 /
  NC7WZ241 half-duplex converter with TX_Enable — the reference layout a
  Robot HAT bus port must cite in `layout_provenance`.
- **Drawing D1** → `package`: 23 / 20 / 34 body, 3 mm Ø16 horn, 9.5 top-to-axis,
  16 × 30 hole grid, 4-Ø1.6 DP3.0 on PCD Ø12 for M2 tapping screws, idler
  variant 29 overall. These are the numbers `cad/part.py` measured off Pollen's
  mesh; they agree.
- **Moment of inertia D2** → `mass_properties` (XL330-M288 row, vendor frame).
- **Certifications** → `certifications` (FCC Part 15 Class A statement only).

## 4. What the vendor does not say (and stays CANNOT DETERMINE)

Listed in `electrical.chip.json` `unknowns`. The two that matter for the
Microduck:

1. **Supply band 3.7–6.0 V vs the 6.6–8.2 V pack.** The page gives no
   absolute maximum; the firmware's own Max Voltage Limit(32) cannot be set
   above 7.0 V. Pollen's runtime reads the pack through this register and
   writes Shutdown(63) = 52, i.e. vendor default 53 with the *Input Voltage
   Error* bit cleared. That is an observation on Pollen's code, consistent
   with stock servos on the raw pack, and it is not a vendor figure. A meter
   on a servo VDD pin settles it.
2. **No running current.** Only standby and stall are published; a 15-servo
   rail budget has nothing between 17 mA and 1.47 A per servo to use.

## 5. Checks run

- `cecad.electrical.load_chips()` on a scratch shelf that unions the workshop
  shelf with this folder: `XL330-M288-T` loads as a `ChipSpec` (every figure
  carries its `_basis`, every block its `cite`). Removing one `_basis` from a
  copy makes the loader refuse the whole record — the gate bites.
- `bin/triad check part:xl330-m288-t` — see `../trust.json` and the ledger.
