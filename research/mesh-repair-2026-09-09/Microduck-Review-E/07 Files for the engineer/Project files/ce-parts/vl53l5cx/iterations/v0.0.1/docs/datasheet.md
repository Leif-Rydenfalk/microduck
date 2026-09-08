# VL53L5CX — the datasheet behind the record

| | |
|---|---|
| document | ST DS13754 "Time-of-Flight 8x8 multizone ranging sensor with wide field of view", footer verbatim `DS13754 - Rev 13 - September 2024`, 40 pages |
| URL | https://www.st.com/resource/en/datasheet/vl53l5cx.pdf |
| fetched | 2026-09-02, curl with a browser User-Agent, HTTP 200, 2582429 bytes |
| file | `../datasheet.pdf`, sha256 `34999dcf5ea4483065c4245e6908e6529b46e31f26f1f40e124d3a453d65d6af` |
| why this part | `research/raw/tof_src_main.rs:83-85` vendors both ST drivers; "Both sensor generations are supported" (docs/ELECTRONICS-AND-SOFTWARE.md §6) |
| the workshop copy | `ce-workshop/ce-parts/VL53L5C/` holds Rev 12 (Farnell mirror, sha256 b266214c…). It has no component.json and `bin/triad check part:VL53L5C` FAILs, so this design keeps its own record. Rev 13's history (p.37) changes notes and packing text, not electrical values |

## Figures, verbatim

| figure | quote | cite |
|---|---|---|
| package | `Package \| Optical LGA16` · `Size \| 6.4 x 3.0 x 1.5 mm` | Table 1 p.4 |
| voltages | `IOVDD: 1.8 or 2.8 V or 3.3 V` · `AVDD: 2.8 V or 3.3 V` | Table 1 p.4 |
| AVDD 3.3 config | `3.3 V configuration \| 3.0 \| 3.3 \| 3.6` | Table 12 p.17 |
| IOVDD 3.3 config | `3.3 V configuration \| 3.0 \| 3.3 \| 3.6` | Table 12 p.17 |
| abs max | `AVDD, IOVDD \| -0.5 \| — \| 3.6` · `SCL, SDA, LPn, INT, and I2C_RST \| -0.5 \| — \| 3.6` V | Table 11 p.17 |
| current | `Active ranging \| 45 \| 50 \| 50 \| 80 \| mA` (AVDD typ/max, IOVDD typ/max) | Table 14 p.18 |
| power | `Continuous mode (4x4 mode or 8x8 mode) \| 216 \| 266 \| 313 \| mW` | Table 15 p.18 |
| I2C | `I2C: 400 kHz to 1 MHz serial bus, address: 0x52` | Table 1 p.4 |
| FoV | `Detection volume \| 45° \| 45° \| 65°` | Table 2 p.4 |
| range | `Ranging \| 2 to 400 cm per zone` · `Sample rate \| Up to 60 Hz` | Table 1 p.4 |
| laser | `Class 1 laser safety limits … in compliance with IEC 60825-1:2014` | §9 p.30 |
| ESD | `Human body model \| JEDEC JS-001-2014 \| ± 2 kV` | Table 13 p.17 |

## Still CANNOT DETERMINE

which generation ships; which breakout (Stemma QT = JST-SH 4-pin is the connector family the HAT's "Stemma J5" name implies, not a fact read anywhere); range as configured.
