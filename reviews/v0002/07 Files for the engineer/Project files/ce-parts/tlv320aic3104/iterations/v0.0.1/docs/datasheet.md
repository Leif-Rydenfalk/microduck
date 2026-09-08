# TLV320AIC3104 — the datasheet behind the record

| | |
|---|---|
| document | TI SLAS510G, "TLV320AIC3104 Low-Power Stereo Audio Codec for Portable Audio and Telephony", p.1 header verbatim `SLAS510G – MARCH 2007 – REVISED FEBRUARY 2021`, 103 pages |
| URL | https://www.ti.com/lit/ds/symlink/tlv320aic3104.pdf |
| fetched | 2026-09-02, curl with a browser User-Agent, HTTP 200, 3189462 bytes |
| file | `../datasheet.pdf`, sha256 `17ce38b2b2b35e44fedaad6c44fcb9c2133722dccfd5ef80e9ec2e3b8f281e9a` (PROVENANCE.json) |
| why this part | `research/raw/deploy_audio_aic3104-i2c3.dts`: codec node `compatible = "ti,tlv320aic3x"` at I2C 0x18 on I2C3; card name `aic3104` (docs/ELECTRONICS-AND-SOFTWARE.md §7) |
| identity check | name match only — the HAT is unpublished. SLAS510G has ONE package (VQFN-32, RHB), so the package axis cannot be wrong for this family member |

## Figures, verbatim (page = PDF page)

| figure | quote | cite |
|---|---|---|
| package | `TLV320AIC3104 \| VQFN (32) \| 5.00 mm × 5.00 mm` | p.1 |
| AVDD, DRVDD | `AVDD, DRVDD1/2(1) \| Analog supply voltage \| 2.7 \| 3.3 \| 3.6 \| V` | §8.3 p.7 |
| DVDD | `DVDD(1) \| Digital core supply voltage \| 1.525 \| 1.8 \| 1.95 \| V` | §8.3 p.7 |
| IOVDD | `IOVDD(1) \| Digital I/O supply voltage \| 1.1 \| 1.8 \| 3.6 \| V` | §8.3 p.7 |
| abs max | `AVDD to AVSS, DRVDD to DRVSS \| –0.3 \| 3.9 \| V` · `DVDD to DVSS \| –0.3 \| 2.5 \| V` · `IOVDD to DVSS \| –0.3 \| 3.9 \| V` | §8.1 p.7 |
| I2C address | `The TLV320AIC3104 responds to the I2C address of 001 1000.` (= 0x18, arithmetic) | §10.5.1 p.45 |
| MCLK | `The device can accept an MCLK input from 512 kHz to 50 MHz` | p.26 |
| current, DAC to line out | `IDRVDD + IAVDD \| Stereo DAC playback to lineout, fS = 48 ksps, I2S slave, no signal \| 4.9` mA; `IDVDD \| 2.3` mA | p.12 |
| ESD | `Human body model (HBM), per ANSI/ESDA/JEDEC JS-001(1) \| ±2000` V | §8.2 p.7 |

## What the datasheet contradicts

`docs/ELECTRONICS-AND-SOFTWARE.md` §7 says the mic is on "Mic3R" (community source [C-elec]). **SLAS510G contains no pin, register name or string "MIC3"** — grep of the full text, 0 hits. The chip's inputs are MIC1L±, MIC1R±, MIC2L, MIC2R (Table 7-1, p.5–6). Which input the Microduck's microphone uses is CANNOT DETERMINE; the HAT schematic settles it.

## Still CANNOT DETERMINE

- which HAT rails feed the three supply domains (a 1.8 V core rail must exist somewhere)
- whether MCLK is the RK3566's I2S3_MCLK_M0 (header pin 13) — consistent, not proven
- speaker path (line out into an amplifier vs. the headphone driver into 16 Ω)
