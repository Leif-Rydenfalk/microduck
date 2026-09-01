# BMI088 — the datasheet behind the record

| | |
|---|---|
| document | Bosch Sensortec "BMI088: Data Sheet", p.1 verbatim `Document revision 1.9`, `Document release date January 2024`, `Document number BST-BMI088-DS000-19`, 62 pages |
| URL | https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmi088-ds001.pdf (the URL says ds001; the file says DS000-19 — recorded as is) |
| fetched | 2026-09-02, curl with a browser User-Agent, HTTP 200, 1368590 bytes |
| file | `../datasheet.pdf`, sha256 `53ab734dba49ac202fa6182fc2b545df6c6d7459c9fec6e851a1209e6bac417e` |
| why this part | `research/raw/deploy_audio_i2c3-pihat.dts`: BMI088 at 0x19 / 0x68 on I2C3, "dormant", "unused but still connected" (docs/ELECTRONICS-AND-SOFTWARE.md §4.2) |

## Figures, verbatim

| figure | quote | cite |
|---|---|---|
| package | `LGA 3.0mm x 4.5mm x 0.95mm housing` | p.2 |
| VDD | `Supply Voltage \| VDD \| Internal Domains \| 2.4 \| 3.6 \| V` | Table 1 p.7 |
| VDDIO | `Supply Voltage \| VDDIO \| I/O Domain \| 1.2 \| 3.6 \| V` | Table 1 p.7 |
| abs max | `Voltage at Supply Pin \| VDD Pin \| -0.3 \| 4 \| V` · `VDDIO Pin \| -0.3 \| 4 \| V` | Table 7 p.12 |
| accel current | `Total Supply Current in Normal mode \| IDD \| VDD = VDDIO =3.0V, 25°C, gFS4g \| 150 \| µA` | Table 2 p.8 |
| gyro current | `Supply Current in Normal Mode \| IDD \| VDD = VDDIO = 3.0V, 25°C, ODR =1kHz \| 5 \| mA` | Table 3 p.8 |
| I2C addresses | `SDO1 pin pulled to ‘GND’: 0011000b (0x18)` · `SDO1 pin pulled to ‘VDDIO’: 0011001b (0x19)` · `SDO2 pin pulled to ‘GND’: 1101000b (0x68)` · `SDO2 pin pulled to ‘VDDIO’: 1101001b (0x69)` | §6.2 p.48 |
| I2C spec | `compatible with the I²C Specification UM10204 Rev. 03 (19 June 2007)` | §6.2 p.48 |
| accel ranges | `±3 … ±24 g`, `ODR 12.5 … 1600 Hz` | Table 4 p.9 |
| gyro range | `0x00 \| ±2000 \| 16.384 LSB/°/s` | p.39 |

The overlay's 0x19 / 0x68 pair means SDO1 tied high and SDO2 tied low on the HAT — an inference from the address table, not a schematic reading.

## Still CANNOT DETERMINE

whether the production head IMU is this chip; whether any release binary reads it; which HAT rails feed VDD and VDDIO.
