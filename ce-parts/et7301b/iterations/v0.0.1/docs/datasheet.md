# ET7301B — the datasheet behind the record

| | |
|---|---|
| document | Etek Microelectronics "ET7301B", footer `Rev 1.2` on every page, no date printed, 32 pages |
| URL | https://www.etekmicro.com/wp-content/uploads/datasheets/ET7301BY_datasheet.pdf |
| fetched | 2026-09-02, HTTP 200, 1155578 bytes |
| file | `../datasheet.pdf`, sha256 `1ac879a37cc082625b55142affa58ce2968eb017c73413c5b982a35b36efc221` |
| why this part | Radxa ZERO 3W schematic v1.12 (2024-11-25) p.17 "USB Port": U6 `ET7301B` on J9 `USB_TYPEC_115H0`, SCL/SDA on `I2C3_SCL_M1`/`I2C3_SDA_M1`, `INT#` → `TYPEC_INT`; same on v1.11 (2023-09-21) p.17. Pollen's overlay disables this node under the name `fusb302@22` |

## Figures, verbatim

| figure | quote | cite |
|---|---|---|
| packages | `ET7301B \| WLCSP \| 1.22mm×1.2mm \| Level 1` · `ET7301BY \| QFN14 \| 2.5mm×2.5mm \| Level 1` | p.1 |
| supply | `Supply Voltage:2.8V to 5.5V` | p.1 |
| VDD | `VDD \| Power Supply Voltage To GND \| GND=0V \| 2.8 \| 5.5 \| V` | p.4 |
| VBUS | `VBUS \| VBUS Voltage To GND \| GND=0V \| 4.0 \| 28 \| V` | p.4 |
| VCONN | `VCONN \| VCONN Supply Voltage To GND \| GND=0V \| 2.7 \| 5.5 \| V` | p.4 |
| abs max | `VBUS \| VBUS Voltage to GND \| -0.3 \| 28 \| V` · `VDD \| Supply Voltage to GND \| -0.3 \| 6 \| V` | p.4 |
| Rd | `RDEVICE \| Device Pull-down Resistance (VDD>3.0 V) \| 4.59 \| 5.10 \| 5.61 \| kΩ` | p.4 |
| I2C address | `Slave Address \| 8 \| 0 1 0 0 0 1 0 \| R/W` (= 0x22) | Table 3 p.18 |
| I2C spec | `The I2C slave fully complies with the I2C specification Version 6 requirements. This block is designed for fast mode.` | p.18 |
| standards | `Full Type-C Specification 1.1 support` · `USB Power Delivery(PD) Specification 2.0, Version 1.1 Support` | p.1 |
| ESD | `Human Body Model, JESD22-A114 \| 4 \| kV` | p.4 |

On the board: VDD at `VCC_3V3`, VCONN at `VCC_SYS` (schematic v1.12 p.17). Package QFN14 (ET7301BY) inferred from the symbol's 14 pins + ePAD.
