# FUSB302 — the datasheet behind the record, and why it is the wrong chip

| | |
|---|---|
| document | onsemi "FUSB302 — Programmable USB Type-C Controller w/PD", p.1 `July 2017`, footer `FUSB302 • Rev. 2`, 35 pages |
| URL | https://files.pine64.org/doc/datasheet/pinecil/FUSB302-D.PDF (mirror) |
| vendor URLs tried | https://www.onsemi.com/pdf/datasheet/fusb302b-d.pdf → 403 · https://www.onsemi.com/pub/Collateral/FUSB302B-D.PDF → 403 · https://www.onsemi.com/download/data-sheet/pdf/fusb302b-d.pdf → 403 · Mouser `/datasheet/2/149/FUSB302B-958669.pdf`, `/2/308/FUSB302B_D-1810324.pdf` → HTML challenge · LCSC `2108140230_onsemi-FUSB302B11MPX_C891306.pdf` → HTML |
| fetched | 2026-09-02, HTTP 200, 1323485 bytes |
| file | `../datasheet.pdf`, sha256 `6af1da8af23e7f015f4896df0b37bde57441c102e5361338e0af566f2bec379f` |
| why this part | `research/raw/deploy_audio_i2c3-pihat.dts` disables `/i2c@fe5c0000/fusb302@22` (docs/ELECTRONICS-AND-SOFTWARE.md §9, §11) |

## The identity finding

The Radxa ZERO 3W schematics — v1.11 (2023-09-21) and v1.12 (2024-11-25), both in `part:radxa-zero-3w/iterations/v0.0.1/docs/fetched/` — put **U6 = ET7301B** (Etek Microelectronics) beside J9 `USB_TYPEC_115H0` on page 17 "USB Port", with `SCL → I2C3_SCL_M1`, `SDA → I2C3_SDA_M1` and `INT# → TYPEC_INT`. There is no FUSB302 on the board. The device-tree node keeps the `fusb302` name because the ET7301B answers at the same slave address (0x22) with the same register map ("compatible FUSB302" is the ET7301B's own marketing; not verified register-by-register here). **The fitted die is `part:et7301b`.**

## Figures, verbatim (for the reference chip)

| figure | quote | cite |
|---|---|---|
| package | `FUSB302MPX \| 14-Lead MLP 2.5 mm x 2.5 mm, 0.5 mm Pitch` | p.1 |
| VDD | `VVDD \| VDD Supply Voltage \| 2.8(3) \| 3.3 \| 5.5 \| V` | p.12 |
| VBUS | `VVBUS \| VBUS Supply Voltage \| 4.0 \| 5.0 \| 21.0 \| V` | p.12 |
| abs max | `VvDD \| Supply Voltage from VDD \| -0.5 \| 6.0 \| V` · `VVBUS \| VBUS Supply Voltage \| -0.5 \| 28.0 \| V` | p.12 |
| I2C address | `Slave Address \| 8 \| 0 1 0 0 0 1 0 \| R/W` (= 0x22) | Table 4 p.18 |
| ESD | `ESD Human Body Model, ANSI/ESDA/JEDEC JS-001-2012 \| All Pins \| 4 \| kV` | p.12 |

## CANNOT DETERMINE

the FUSB302**B** document and its four address variants — unreachable on 2026-09-02.
