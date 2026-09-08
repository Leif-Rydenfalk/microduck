# VL53L8CX — the datasheet behind the record

| | |
|---|---|
| document | ST DS14161 "Low-power high-performance 8x8 multizone Time-of-Flight (ToF) sensor", footer verbatim `DS14161 - Rev 12 - July 2025`, 45 pages |
| URL | https://www.st.com/resource/en/datasheet/vl53l8cx.pdf |
| fetched | 2026-09-02, curl with a browser User-Agent, HTTP 200, 3587088 bytes |
| file | `../datasheet.pdf`, sha256 `a24f8bbc282bf04e28aa285b80fc165517f70704457a1b9546e8a18adfb3f844` |
| why this part | the second generation `tofd` supports (`research/raw/tof_src_main.rs:83-85`) |

## Figures, verbatim

| figure | quote | cite |
|---|---|---|
| package | `Package \| Optical LGA16` · `Size \| 6.4 x 3.0 x 1.75 mm` | Table 1 p.4 |
| voltages | `AVDD: 3.3 V` · `CORE_1V8: 1.8 V` · `IOVDD: 1.2/1.8 V` | Table 1 p.4 |
| AVDD | `AVDD supply \| 3.13 \| 3.3 \| 3.47` | Table 12 p.20 |
| CORE_1V8 | `CORE_1V8 supply \| 1.62 \| 1.8 \| 1.98` | Table 12 p.20 |
| IOVDD | `IOVDD supply with 1.8 V configuration \| 1.62 \| 1.8 \| 1.98` · `… 1.2 V configuration \| 1.08 \| 1.2 \| 1.32` | Table 12 p.20 |
| abs max | `AVDD \| -0.5 \| — \| 3.47` · `CORE_1V8 \| -0.5 \| — \| 1.98` · `IOVDD \| -0.5 \| — \| 1.98` V | Table 11 p.20 |
| current | `Active ranging \| 43 \| 50 \| 50 \| 80 \| 0.003 \| 0.006 \| mA` | Table 14 p.21 |
| power | `Continuous mode (4x4 or 8x8 mode) \| 215 \| mW` | Table 15 p.21 |
| I2C | `uses a device 8-bit address of 0x52` · `maximum speed of 1 Mbit/s/s` | p.12 |
| FoV | `Detection volume \| 45° \| 45° \| 65°` | Table 2 p.4 |
| laser | `Class 1 … in compliance with IEC 60825-1:2014` | p.34 |

## The fact that matters for the HAT

**IOVDD absolute maximum is 1.98 V and there is no 3.3 V configuration.** The Microduck's I2C3 is a 3.3 V bus with 10 kΩ pull-ups on the HAT. If an L8CX ships, something between the HAT and the die must level-shift — a breakout with its own regulator + shifter, or 1.8 V pull-ups. Nothing fetched says which. CANNOT DETERMINE.
