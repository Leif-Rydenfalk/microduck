# Radxa ZERO 3W — the vendor documents behind the record

All fetched 2026-09-02 into `fetched/` (sha256 in `../PROVENANCE.json`):

| key | document | URL |
|---|---|---|
| [brief] | Radxa ZERO 3W Product Brief, RAD-DOC-0084, **Revision 1.10, 2026-06-26**, 9 pp | https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_product_brief.pdf |
| [sch1.12] | Schematic "Zero 3W" **REV V1.12**, "Monday, November 25, 2024", 22 sheets | https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_v1.12_schematic.pdf |
| [sch1.11] | Schematic REV V1.11, 2023-09-21, 22 sheets | https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_v1110_schematic.pdf |
| [wiki] | "Hardware interface description", CC BY 4.0 | https://docs.radxa.com/en/zero/zero3/hardware-design/hardware-interface |
| [product] | product page | https://radxa.com/products/zeros/zero3w/ |

(`https://dl.radxa.com/zero3/docs/hw/zero3w/radxa_zero_3w_v1110_schematic.pdf` — the path guessed first — is a 404; the real folder is `hw/3w/`.)

## What this settles in docs/ELECTRONICS-AND-SOFTWARE.md

| open item | answer | source |
|---|---|---|
| §3.1 "header pins for UART2 M0: CANNOT DETERMINE" | **pin 8 = UART2_TX_M0 (GPIO0_D1), pin 10 = UART2_RX_M0 (GPIO0_D0)** — and it is the U-Boot/debug console at 1500000n8 | [wiki] "Debug Serial Port", verbatim: `The debug serial port of ZERO 3 uses UART2_M0 (40-pin GPIO Pin 8: TX, Pin 10: RX), with a default baud rate of 1500000n8.`; [sch1.12] sheet 5 |
| §11 I2S3 header pins | M0: SCLK 12, MCLK 13, LRCK 35, SDI 38, SDO 40 (M1 alternates on 19/21/23/24 also on the header) | [brief] p.6 table; [wiki] |
| §7 MCLK origin | I2S3_MCLK_M0 is header pin 13 — a candidate for the 12 MHz `fixed-clock`, not proof | [brief] p.6 |
| §9 / §11 FUSB302 | **the board fits an Etek ET7301B (U6), not an FUSB302**; the OTG/power port has no controller at all, only 5.1 kΩ Rd on CC1/CC2 | [sch1.12] sheet 17 (`U6 ET7301B`, `J9 USB_TYPEC_115H0`, `SCL I2C3_SCL_M1`, `SDA I2C3_SDA_M1`, `INT# TYPEC_INT`); sheet 22 (`R9/R10 5.1k` on CC1/CC2) — same on [sch1.11] |
| §2 clock conflict 1.6 vs 1.8 GHz | vendor says 1.6 | [brief] §3.1 p.3 `Quad‑core Arm® Cortex®‑A55 (ARMv8) 64‑bit @ 1.6GHz` |
| §2 "is it the stock module" | still open — and the press kit's 1 GB + 32 GB pairing has **no row** in the SKU table (1 GB pairs with no eMMC or 8 GB) | [brief] §7 p.8 |
| §9 power path | `5V Power from the GPIO PIN 2 & 4`; `Power adapter with 5V/2A on the USB 2.0 OTG Type‑C power port` | [brief] §5.1 p.5 |
| §11 I2C3 pins 3/5 | confirmed `I2C3_SDA_M0` pin 3, `I2C3_SCL_M0` pin 5 — **the board already carries pull-ups on them** | [brief] p.6; [wiki] tip verbatim `Pin 3, Pin 5, Pin 27, and Pin 28 add extra pull-up resistors for I2C device power supply` |
| §5 CSI connector | 22-pin, 4 lanes, I2C2_M1 on pins 20/21, VCC_3V3 pin 22, CAMERAB_PDN_L pin 17, CIF_CLKOUT pin 18 | [wiki] MIPI CSI table; [sch1.12] sheet 9 |

## Still CANNOT DETERMINE

board current draw; board mass; Pollen's SKU/revision; the on-board I2C3 pull-up value; which I2S3 mux `i2s3_2ch` selects; whether U-Boot's 1.5 Mbaud console output reaches the servos at boot.
