# BUILD PACK — what to print, what to buy, and what still blocks a working robot

*Assembled 2026-09-05 for a build at Black Ark, Room 405, Electronic Technology Building,
Huaqiangbei, Shenzhen. Every number below is copied from an artifact in this repo, not
re-derived. Nothing here was bought and nothing was ordered.*

---

## 1 · WHAT YOU CAN DO TODAY — the print files are ready and verified

Two plates, both re-verified this morning:

| file | contents | verified |
|---|---|---|
| `out/print/plates/PLA/microduck-PLA.3mf` | 26 slugs → **32 pieces** | zip OK, 33 `.model`, sha256 `5b8518b894b2` |
| `out/print/plates/TPU/microduck-TPU.3mf` | 4 slugs → **4 pieces** | zip OK, 5 `.model`, sha256 `6f1acd0f86d5` |
| `out/print/stl/**` | **30 STLs**, binary, millimetres | **30/30 structurally valid** (header triangle count matches file length exactly) |

**Totals, from the slicer's own `result.json` — not estimated from volume:**

- **PLA — 218.29 g, 9.93 h** of per-piece print time
- **TPU — 26.20 g, 2.41 h**
- Machine: **Bambu Lab H2S, 0.4 nozzle**, process `0.20mm Standard @BBL H2S`,
  filament `Bambu PLA Basic` (1.26 g/cm³) / `Bambu TPU 85A` (1.18 g/cm³)

Per-part orientation rules and which parts need supports are in `out/print/PRINT.md`.
Nine parts are flagged **floating regions / cantilever — enable supports**; the biggest are
`top-head-shell` (34.61 g, 68m46s) and `bottom-head-shell` (28.28 g, 59m16s).

**One part has a known slicer defect:** `microduck-yaw-roll-motion` was sliced **as modelled**
because auto-orient crashed BambuStudio on that mesh. Check its orientation by eye before
committing the plate.

> **Filament to buy: ~250 g PLA and ~30 g TPU per robot.** One 1 kg spool of each covers four
> robots with margin. Bambu Lab is a Shenzhen company — this is a local purchase.

---

## 2 · THE THREE THINGS THAT BLOCK A COMPLETE ROBOT

**Printing is not blocked. Finishing a robot is.** In priority order:

### 2.1 The three custom PCBs do not exist as design files — this is the hard blocker
`docs/BOM.md` §"Custom PCBs (no design files exist — must be designed, not bought)":

| board | what it carries | status |
|---|---|---|
| **P1 — Robot HAT**, 65 × 30 mm Pi-Zero footprint | TLV320AIC3104 codec (I²C 0x18, I²S3, 12 MHz MCLK), BMI088, Stemma J5 for the ToF, 10 kΩ pull-ups R12/R13, battery power path, inferred half-duplex Dynamixel transceiver | **must be designed** |
| **P2 — `imu_to_dxl` v2** | LSM6DSV16X + MCU acting as a Dynamixel Protocol-2 slave, ID 200, 12-byte block at register 124 | **must be designed** |
| **P3 — "banana" battery PCB** | NP-F550 contacts, clamped by `banana_pcb_locker` | **must be designed** |

No amount of purchasing fixes this. Until P1 exists there is no servo bus, no audio and no ToF.
**JLCPCB is in Shenzhen** and will fab + assemble these in days once schematics exist — the
constraint is design time, not lead time.

### 2.2 Licence — 22 of the 30 printed parts CANNOT BE SOLD
`out/print/PRINT.md`, verbatim: *8 parts are our parametric rebuilds; **22 are Pollen's vendor
meshes as shelved (CC BY-SA-NC — fine to print, NOT licensed for sale)**.*

**Print for yourself: fine. Manufacture for sale: not with these files.** If "start
manufacturing" means units that leave the building, those 22 slugs must be replaced by
parametric rebuilds first. Rung 1 already has **20 parametric rebuilds passing** refcheck, so
the path exists and is partly walked — but it is not done, and this is the item most likely to
be discovered late and expensively.

### 2.3 Eighteen BOM lines are CANNOT DETERMINE
Priced today: **USD 563.78/robot** across 11 lines. Unpriced and unspecified: Radxa Zero 3W SKU,
speaker, microphone, NFC reader + antennas, indicator LED, gamepad, USB-C cable, 22-pin MIPI CSI
ribbon, four M2 screw lengths, M2 nuts, M2.5×6, all three PCBs, and both filaments.

**And the cost headline from `docs/PRODUCTION.md`:** 15 × XL330 = **$358.50 = 75 % of bought
cost**, which already exceeds Pollen's **$399** retail price for the finished robot.

---

## 3 · SOURCING — and the finding is that you are standing in the supply chain

**Almost none of this needs to ship to Room 405. Most of it is a walk, and the rest is Shenzhen
next-day.** Split by where it actually comes from:

### 3.1 Walk downstairs — Huaqiangbei, same day
| item | qty | note |
|---|---|---|
| ball bearing **MR1622-ZZ** 22×16×4 | 11 | priced NZD 5.90 in the BOM from a New Zealand vendor — buy locally instead |
| ball bearing **MR6700** 15×10×3 | 3 | same |
| M2×4 / ×6 / ×8 / ×12 socket head, M2 nuts, M2.5×6 | ~80+ | BOM prices M2×6 at EUR 0.04 from a German vendor |
| M2 heat-set inserts | 60 | BOM prices these at USD 0.12 from Prusa |
| speaker 35×25×7, 2 W 8 Ω | 1 | **CANNOT DETERMINE** in the BOM — spec it here by buying and measuring |
| microphone | ≥1 | same |
| IMX219 camera board + M12 lens | 1 | BOM has Arducam B0183 at $23.99 + $7.99; local equivalents abundant |
| NP-F550 2600 mAh pack + charger | 1 | BOM: $24.95 |
| JST connectors / ribbon / USB-C | — | |
| **PLA and TPU filament** | 250 g / 30 g | Bambu Lab is a Shenzhen company |

### 3.2 Shenzhen, next-day
- **LCSC** — TLV320AIC3104IRHBR (already priced **$2.25**, LCSC part **C181753**), LSM6DSV16X,
  BMI088, passives. LCSC is Shenzhen.
- **JLCPCB** — P1/P2/P3 fab + assembly, *once designs exist*.
- **Radxa Zero 3W** — Radxa is Shenzhen-based. Note the BOM's finding: **the 1 GB/32 GB SKU
  Pollen cites does not exist in Radxa's own SKU table.** Resolve the SKU before ordering.

### 3.3 Actually needs importing
- **15 × Dynamixel XL330-M288-T** — ROBOTIS, Korea. $23.90 each intl / $27.49 US.
- **2 × Robot Cable-X3P 180 mm 10-packs** — ROBOTIS, $15.50 each.
- **VL53L8CX ToF breakout** — BOM prices Pololu #3419 at $24.95; ST silicon is available through
  Chinese distributors, so a local carrier may remove this import.

> ### The one decision that changes the whole cost structure
> **The ancestor design uses Feetech STS3215 servos, and Feetech is a Shenzhen company.**
> `research/raw/odm_bom.csv` (Open Duck Mini v2) lists **14 × Feetech STS3215 7.4 V (19 kg·cm)
> at €14 = €196**. Microduck's 15 × XL330 is **$358.50**.
>
> That is roughly **a 45 % cut to the dominant cost line, and it converts your single largest
> import into a local purchase.**
>
> **It is not free.** The servo pockets in `upper-leg`, `yaw2roll`, `motor-support` and the ankle
> group are modelled to XL330 geometry; STS3215 has different dimensions, mounting and a
> different bus. Changing servo means re-modelling those parts and re-testing the walk policy —
> the MuJoCo sim (rung 3, PASS) is the thing that tells you whether it still walks.
>
> **This is a decision for you, not for me.** But it is the highest-value question in the whole
> build and it should be settled before 15 servos are bought.

---

## 4 · WHAT I DID NOT DO, AND WHY

- **I did not buy anything.** I have no payment authority and purchasing is not something I do
  on your behalf unattended.
- **I could not drive your browser.** This session has a shell, files and web *fetch* — no
  mouse or keyboard control. To have me click through a checkout you would need Claude in
  Chrome, the desktop app's computer use, or Playwright MCP wired into this session.
- **Your payment rail is currently broken anyway** — mainland Alipay is blocked from paying
  overseas merchants, which is exactly the constraint that makes §3's "buy it locally in RMB"
  split the right shape rather than a nicety.

## 5 · THE ORDER I WOULD DO THIS IN

1. **Start the PLA plate now.** 9.93 h, no decisions pending, nothing downstream depends on it.
2. **Settle the servo question** (XL330 vs Feetech STS3215) before spending $358.
3. **Walk the §3.1 list** — bearings, screws, inserts, speaker, mic, camera, battery, filament.
   Measure the speaker and mic you actually buy and close two CANNOT DETERMINEs by doing it.
4. **Design P1.** It is the critical path and everything electrical waits on it.
5. **Replace the 22 NC-licensed meshes** if any of this is ever going to be sold.
