# Bought components at volume — vendors, unit prices at 1 / 10 / 100 / 1000, lead times, MOQ

*Written 2026-09-02 from live vendor pages fetched the same day (every URL below
was opened on 2026-09-02; the price quoted is the one on the page at that
moment). A price that could not be read — page blocked (403/500), timed out,
or not showing a price — is **CANNOT DETERMINE**, with the URL that failed so
the next agent can retry. Nothing is estimated. Currencies are left as the
vendor states them; no FX conversion was fetched, so the roll-up (§14) sums
USD lines only and lists EUR/GBP/NZD/INR lines beside it. Inputs: `../BOM.md`
(the bought list B1–B19), `../PARTS.md`, `../../SPEC.md`.*

Quantity per robot is from `BOM.md` §1 / §4. "@1 / @10 / @100 / @1000" is the
**unit** price at that order quantity of the part, as the vendor's own tier
table states it; "—" means the vendor publishes no tier at that quantity (the
@1 price is then the only read price, i.e. the ceiling).

## 0. Summary of what was and was not readable

| line | vendors read (price on page) | vendors blocked / no price |
|---|---|---|
| B1 XL330-M288-T | ROBOTIS US, ROBOTIS intl, Generation Robots (FR), Tribotix (AU) | RobotShop (403), AliExpress (blank) |
| B2 X3P cables | ROBOTIS intl, ROBOTIS US | — |
| B3 Radxa Zero 3W | ALLNET China, Arace, ameriDroid, Evelta (IN) | OKdo (socket closed ×5), RS Online BE/UK/DK (hang/timeout), AliExpress (blank) — **and the 1 GB / 32 GB SKU does not exist in Radxa's own SKU table** |
| B4/B5 NP-F550 + charger | NextBatteries (2 listings), Neewer (2 listings) | B&H (403), Amazon (500), Walmart (captcha), Alibaba Beston (blank), TME (withdrawn), NKON (403), IMR / 18650BatteryStore (price read, sold out) |
| B6 IMX219 M12 board | UCTRONICS (Arducam US shop) ×2, Welectron (DE), The Engineer Store (IN), The Pi Hut (UK), Seeed | arducam.com (403 on all pages), RobotShop (403), Amazon (500) |
| B7 M12 lens | UCTRONICS, The Pi Hut | Amazon (500) |
| B9 ToF | DigiKey ×4, SparkFun ×2, Pololu ×2 | Mouser (timeout ×3) |
| P1 chip TLV320AIC3104 | DigiKey, LCSC | Mouser (timeout ×3), Arrow (Akamai block), TI store (login), Octopart (403), Newark (wrong page) |
| B12 speaker 35×25×7 | Thingbits (IN, sold out); nearest catalogue parts at DigiKey, Adafruit | eBay 3525 lots (timeout ×6), Amazon CQRobot (500 / no price), LCSC (search page renders no products) |
| B10 bearing 22×16×4 | NZ Miniature Bearings, Jiang Xin (made-in-china, MOQ 1000) | 123Bearing (no price rendered), VXB (0 results), Bearings Direct (0 results), Boca (403), Alibaba/AliExpress/Amazon (blank/500) |
| B11 bearing 15×10×3 | Bearings Direct, VXB (search page), FastEddy (10×15×**4**) | Boca (403), 123Bearing (no price), Amazon (500) |
| B18 M2 screws | RST-Versand (DE), der-schraubenladen (DE, M2.5×8 shown) | Accu, Bolt Depot, McMaster, Misumi, GetFPV, Albany County (no price rendered), Amazon, eBay, befestigungsfuchs (503), schraubenhandel24 (403), schraubenking (403) |
| B18 M2 heat-set inserts | CNC Kitchen (DE), Prusa (US), Vector3D (UK) | Amazon (500) |
| ROBOTIS OEM pricing | no public page; only "6pcs Bulk" packs exist (AX/MX, not XL330) | — |

## 1. B1 — Dynamixel XL330-M288-T (×15 per robot)

Sub-variant M288 vs M077 is still not stated by Pollen (SPEC §5); both are
the same price at ROBOTIS intl (M077-T $23.90, lead 40 days; M288-T $23.90,
lead 10 days — list page below), so the price line does not depend on it.

| vendor | URL | @1 | @10 | @100 | @1000 | stock / lead time | MOQ | notes |
|---|---|---|---|---|---|---|---|---|
| ROBOTIS US (robotis.us) | https://www.robotis.us/dynamixel-xl330-m288-t/ | **$27.49** | — | — | — | "Current Stock:" field shown, number not readable in the page text | none stated | no tier table, no OEM text; phone 949-377-0377 |
| ROBOTIS intl (en.robotis.com) | https://en.robotis.com/shop_en/item.php?it_id=902-0163-000 | **$23.90** | — | — | — | item page: "normally ships out within 3 working days when in stock"; XL-series list page https://en.robotis.com/shop_en/list.php?ca_id=202030 shows "XL330-M288-T … Lead Time: 10 days" (M077-T: 40 days) | none stated | ships from Korea; no tier table |
| Generation Robots (FR) | https://www.generationrobots.com/en/403817-dynamixel-xl330-m288-t-servo-motor.html | **€33.50 ex VAT / €40.20 inc** | — | — | — | "373 Available", "Get it in 24/48h!" | none | EU stock |
| Tribotix (AU) | https://tribotix.com/product/xl330-m288-t/ | **AUD 38.00 ex GST (41.80 inc)** | — | — | — | not stated | none | |
| RobotShop | https://www.robotshop.com/products/robotis-dynamixel-xl330-m288-t-smart-servo-actuator | CANNOT DETERMINE (403) | | | | | | search index lists only the XC330-M288-T page |
| AliExpress reseller | https://www.aliexpress.com/i/1005004403336577.html | CANNOT DETERMINE (page blank to fetcher) | | | | | | |

**Bulk / OEM.** ROBOTIS publishes no XL330 bulk pack and no volume tiers:
- https://www.robotis.us/bulk-pack/ (read 2026-09-02) lists only 6-piece bulk packs of AX-12A ($310.39), AX-18A ($655.39), MX-28T ($1,517.89), MX-28R ($1,552.39), MX-64R ($2,104.39), MX-106T ($3,403.89, out of stock), MX-106R ($3,438.39); "The bulk packs of DYNAMIXELs come with just the servo motors. All horns, wires, nuts, bolts, etc. are not included". **No XL330 pack.**
- The size of ROBOTIS's own published bulk discount, from the one servo that has both prices: AX-12A single **$57.39** (https://www.robotis.us/dynamixel-ax-12a/) vs 6pcs bulk **$310.39** (https://www.robotis.us/dynamixel-ax-12a-6pcs-bulk/) = $51.73 each, **−9.9 %**; intl single **$49.90** (https://en.robotis.com/shop_en/item.php?it_id=902-0003-001) vs 6pcs bulk **$269.90** (https://en.robotis.com/shop_en/item.php?it_id=902-0010-001) = $44.98 each, **−9.9 %**. That is the only volume signal ROBOTIS publishes; it is for a different servo and is not evidence of XL330 pricing at 150 / 1,500 / 15,000 units.
- FAQ https://www.robotis.us/faq/ and About https://www.robotis.us/about-us/ contain no bulk/OEM/education text. Contact page https://www.robotis.us/contact-us/ gives america@robotis.com, 949-377-0377, "ROBOTIS INC, 4222 Green River Rd. Corona, CA 92880"; intl shop pages give contactus2@robotis.com and +82-70-8671-2609.
- **OEM price at 15 / 150 / 1,500 / 15,000 servos: CANNOT DETERMINE** — requires a written quote from ROBOTIS (emails above). Until then the servo line is the list price at every quantity, i.e. $23.90 (intl) or $27.49 (US) per unit; for 15 units per robot: **$358.50 / $412.35**.

## 2. B2 — Dynamixel X3P 3-pin cables (×16 per robot: 15 servos daisy-chain + `imu_to_dxl`)

Lengths per link are CANNOT DETERMINE (`BOM.md` B2); the 180 mm pack is the
priced bracket.

| vendor | URL | pack | price | per cable | lead |
|---|---|---|---|---|---|
| ROBOTIS intl | https://en.robotis.com/shop_en/item.php?it_id=903-0251-000 | Robot Cable-X3P (Convertible) 180 mm, 10 pcs | **$15.50** | $1.55 | "Normally ships out within 3 working days when in stock" |
| ROBOTIS US | https://www.robotis.us/robot-cable-x3p-180mm-10pcs/ | Robot Cable-X3P 180 mm (10 pcs) | **$21.85** | $2.19 | not stated |

No tiers at either shop. 16 cables → 2 packs → $31.00 (intl) at order quantity 1; $24.80 per robot pro-rata.

## 3. B3 — Radxa Zero 3W (×1; Pollen: 1 GB LPDDR4 / 32 GB eMMC)

**Finding: Radxa's own product brief lists no 1 GB / 32 GB SKU.** The SKU
table in `radxa_zero_3w_product_brief.pdf` (RAD-DOC-0084, §7 "Models and SKU",
https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_product_brief.pdf, text
extracted 2026-09-02) is:

| DRAM | eMMC | SKU (header pre-soldered / empty) |
|---|---|---|
| 1 GB | none | RS107-D1E0H1W15 / RS107-D1E0H0W15 |
| 1 GB | 8 GB | RS107-D1E8H1W15 / RS107-D1E8H0W15 |
| 2 GB | none | RS107-D2E0H1W15 / RS107-D2E0H0W15 |
| 2 GB | 16 GB | RS107-D2E16H1W15 / RS107-D2E16H0W15 |
| 4 GB | none | RS107-D4E0H1W15 / RS107-D4E0H0W15 |
| 4 GB | 32 GB | RS107-D4E32H1W15 / RS107-D4E32H0W15 |
| 8 GB | none | RS107-D8E0H1W15 / RS107-D8E0H0W15 |
| 8 GB | 64 GB | RS107-D8E64H1W15 / RS107-D8E64H0W15 |

So Pollen's "1 GB / 32 GB" (press kit, `SPEC.md` §5) is either a custom
build from Radxa (an OEM order — price CANNOT DETERMINE) or a mis-statement
of the 1 GB / 8 GB catalogue part. What settles it: the eMMC size reported by
`lsblk` on a production unit, or Pollen's answer. The evelta.com and
allnetchina.cn variant selectors (below) also carry no 1 GB / 32 GB option.

| vendor | URL | variant | price | stock (2026-09-02) | tiers / MOQ / lead |
|---|---|---|---|---|---|
| ALLNET China | https://shop.allnetchina.cn/products/copy-of-radxa-zero-3w | 1 GB / no eMMC, no header (RS107-D1E0H0W15) | **$18** | Sold out | none published |
| | | 1 GB / no eMMC, header (RS107-D1E0H1W15) | **$19** | Sold out | |
| | | 1 GB / 8 GB eMMC, no header (RS107-D1E8H0W15) | **$22** | Sold out | |
| | | 1 GB / 8 GB eMMC, header (RS107-D1E8H1W15) | **$23** | Sold out | |
| | | 2 GB / 16 GB, no header / header | **$32.90 / $33.90** | Sold out | |
| | | 4 GB / 32 GB, no header / header | **$50 / $51** | Sold out | |
| | | 2 GB / no eMMC, header | $55.99 | In stock (only variant in stock) | |
| Arace Tech | https://arace.tech/products/radxa-zero-3w | selector 1/2/4/8 GB × none/8/16/32/64 GB | "$20.00" shown as base | every combination "Sold Out" | none |
| ameriDroid (US) | https://ameridroid.com/products/radxa-zero-3w | selector 1/2/4/8 GB × none/16/32/64 GB | "$41.95 USD" shown | "Out of Stock!"; all variants "sold out or unavailable" | none |
| Evelta (IN) | https://evelta.com/radxa-zero-3w-tiny-rk3566-sbc/ | selector: 1 GB no eMMC (±header), 1 GB/8 GB, 2 GB, 2 GB/16 GB, 4 GB/32 GB | "₹2,995.00 ex. GST / ₹3,534.10 inc." (base) | "in stock" | per-variant prices not rendered |
| OKdo (Radxa's EU/UK distributor) | https://www.okdo.com/p/okdo-rock-zero-3w-1gb-with-wi-fi-ble-without-gpio/ ; https://www.okdo.com/us/p/okdo-rock-zero-3w-4gb-32gb-with-gpio/ | 1 GB; 4 GB/32 GB | CANNOT DETERMINE ("Socket is closed" ×5) | | |
| RS Online (OKdo RS107-D4E32H1W15) | https://befr.rs-online.com/web/p/rock-sbc-boards/2564694 ; https://uk.rs-online.com/web/p/rock-sbc-boards/2564694 | 4 GB / 32 GB | CANNOT DETERMINE (hang / timeout) | | |
| Radxa product page | https://radxa.com/products/zeros/zero3w/ | — | no price; "exclusively available through our network of Approved Partners" | | |

**Volume:** no vendor publishes tiers; Radxa direct/OEM pricing CANNOT
DETERMINE (partner network only). **Lead time:** every US/CN retailer was
sold out on 2026-09-02 for the 1 GB parts — lead time CANNOT DETERMINE.

## 4. B4 / B5 — NP-F550 2600 mAh 2S pack and charger (×1 pack per robot; Pollen sells 2 packs + dual charger for €33 / $39)

| vendor | URL | what | price | stock | tiers |
|---|---|---|---|---|---|
| NextBatteries | https://www.nextbatteries.com/products/sony-np-f550-battery-2-pack-2600mah-l-series-dual-charger | 2 × NP-F550 2600 mAh 7.2 V + dual charger (EU plug + car adapter) | **$49.90** (→ $24.95 per pack incl. charger share) | "In Stock" | none |
| NextBatteries | https://www.nextbatteries.com/products/sony-np-f550-battery-2-pack-2600mah-l-series-charger | 2 × NP-F550 2600 mAh 7.2 V + single charger | **$53.90** | "In Stock" | none |
| Neewer | https://neewer.com/products/neewer-4-packs-7-4v-2600mah-np-f550-replacement-batteries-66601510 | 4 × NP-F550 2600 mAh 7.4 V, no charger | **$104.99** (→ $26.25 per pack) | "0 in stock", "More stock coming soon" | none |
| Neewer (chargers collection) | https://neewer.com/collections/chargers | "NEEWER NP-F550 Battery Charger Set for Sony" (2 packs + charger) | **$49.99** | listed | none; the standalone dual-charger product pages 66600569 / 66600066 returned 404 |
| Pollen (reference) | https://store.pollen-robotics.com/products/charger-pack | 2 packs + dual charger | **€33 / $39** | per `BOM.md` B4 | |
| B&H (Neewer 66600244) | https://www.bhphotovideo.com/c/product/1733125-REG/neewer_66600244_2_2600mah_f550.html | | CANNOT DETERMINE (403) | | |
| Amazon | https://www.amazon.com/NP-F550-Battery-Replacement-Batteries-CCD-SC55/dp/B089NQ7PGS | | CANNOT DETERMINE (500) | | |
| Alibaba (Beston, OEM packs) | https://www.alibaba.com/product-detail/Beston-2600mAh-replacement-NP-F550-NP_60828272766.html | OEM NP-F550 2600 mAh, custom logo | CANNOT DETERMINE (page blank to fetcher; the search index claims $1.20–3.88/pc and MOQ 200/500 — **not read, not used**) | | |

Charger, standalone, at 100 / 1000: CANNOT DETERMINE (no standalone page readable).

**Cells inside an NP-F550** (2 × 18650, 2600 mAh — the pack envelope 38.4 × 20.6 × 70.8 mm holds two 18650s; cell brand in Pollen's packs CANNOT DETERMINE):

| vendor | URL | cell | price | stock |
|---|---|---|---|---|
| IMR Batteries | https://imrbatteries.com/products/samsung-26j-18650-2600mah-5-2a-battery | Samsung 26J 2600 mAh 5.2 A | **$4.99** | "Sold out" |
| 18650 Battery Store | https://www.18650batterystore.com/products/samsung-26jm | Samsung 26J 2600 mAh | **$4.99** | "Sold out" |
| TME | https://www.tme.eu/en/details/accu-icr18650-26jm/rechargeable-batteries/samsung-sdi/icr18650-26j2/ | ICR18650-26J2 | "Product withdrawn from the offer" | — |
| NKON (EU) | https://eu.nkon.nl/rechargeable/li-ion/18650-size/samsung-icr18650-26j3.html | ICR18650-26J | CANNOT DETERMINE (403) | |
| DNK Power (CN pack maker) | https://www.dnkpower.com/samsung-icr18650-26jm/ | ICR18650-26J, packs to order | quote only (sales@dnkpower.com) | |

Cell price at 1000: CANNOT DETERMINE. Building our own NP-F550-format pack also needs a protection PCB and the "banana" contact board (`BOM.md` P3) — unpriced.

## 5. B6 — IMX219 camera board with M12 mount (×1)

| vendor | URL | SKU / what | price | stock / lead | tiers |
|---|---|---|---|---|---|
| UCTRONICS (Arducam's US shop) | https://www.uctronics.com/camera-modules/camera-for-nvidia/arducam-8-mp-sony-imx219-m12-mount-low-distortion-camera-module-for-nvidia-jetson-nano.html | **B0183** IMX219 board + M12 low-distortion lens; package "1pcs Arducam IMX219 Low Distortion Camera Module"; FOV "88°(D) × 75°(H) × 60°(V)" | **$23.99** "Special Price" (regular $39.99) | not stated | none |
| UCTRONICS | https://www.uctronics.com/index.php/arducam-8-mp-sony-imx219-m12-mount-low-distortion-camera-module-for-raspberry-pi-nvidia-jetson-nano.html | **B0188** IMX219 NoIR M12, 75°(H) | **$13.99** special (regular $24.99) | not stated | none. arducam.com's index entry for B0188 reads "[Discontinued]" and "camera board is not included" (search index text; arducam.com itself returned 403) — **whether B0188 includes the sensor board: CANNOT DETERMINE** |
| Welectron (DE) | https://www.welectron.com/Arducam-B0183-IMX219-Low-Distortion-M12-Mount-Camera-Module-for-NVIDIA-Jetson-Nano-Xavier-NX_1 | B0183 | **€45.90 inc 19 % VAT / €38.57 ex** | "On stock", "1 - 3 business days" | none |
| The Engineer Store (IN) | https://www.theengineerstore.in/products/arducam-b0183-imx219-low-distortion-m12-mount-camera-module-for-nvidia-jetson-nano | B0183 | **Rs. 3,839.66** | "3-5 Working Days Dispatch" | none; page says lens sold separately — contradicts UCTRONICS' package list; unresolved |
| The Pi Hut (UK) | https://thepihut.com/products/8mp-sony-imx219-camera-module-with-m12-lens-for-raspberry-pi | **B0103** IMX219 + 70° M12 lens LS40136, two FPC cables | **£57.60 inc VAT** ("Sale price") | "Only 7 units left" | none |
| Seeed Studio | https://www.seeedstudio.com/IMX-219-CMOS-camera-module-M12-and-CS-camera-available-p-5372.html | 102110719 IMX219 M12/CS board, **no lens** | **$15.90**; **10+: $12.50** | "In stock" | 10+ tier only |
| arducam.com direct | https://www.arducam.com/product/arducam-imx219-low-distortion-m12-mount-camera-module-drop-in-replacement-for-raspberry-pi-v2-camera/ | | CANNOT DETERMINE (403 on every arducam.com URL) | | |

Which Arducam board Pollen fits, and the flex length (`BOM.md` B8): CANNOT DETERMINE.

## 6. B7 — M12 wide-angle lens (×1; FOV "still being finalised" per press kit)

| vendor | URL | lens | price |
|---|---|---|---|
| UCTRONICS | https://www.uctronics.com/lens/m12-mount-lens.html?product_list_mode=list | Arducam M40180H13L (LN180), M12 | **$7.99** |
| UCTRONICS | https://www.uctronics.com/lens/m12-mount-lens.html?p=2&product_list_mode=list | Arducam 1/4″ M12 2.05 mm M40205M11 | **$11.99** |
| UCTRONICS | same page 2 | Arducam 1.95 mm M27195H15 (1/2.7″–1/2.9″) | **$9.99** |
| UCTRONICS | https://www.uctronics.com/lk001.html | LK001 kit, 10 lenses 10°–200° for 1/4″ Pi-camera sensors (OV5647, IMX219) | **$89.99** (the kit to pick the FOV with) |
| The Pi Hut | https://thepihut.com/collections/raspberry-pi-camera-lenses | M12 75° (with HQ-cam adapter) | **£14.40** |
| The Pi Hut | same | M12 90° | **£17.30** |
| The Pi Hut | same | M12 140° | **£21.20** |
| The Pi Hut | same | M12 180° fisheye 1/2.5″ 1.7 mm | **£9.60** |

No tiers at either. B0183 already ships with a 75°(H) lens, so at Pollen's
"~62° community" FOV a separate lens is only needed if the spec lands
elsewhere: **$0–11.99 per robot**.

## 7. B9 — ToF 8×8 (VL53L5CX or VL53L8CX) — breakout on the HAT's Stemma J5, or the bare chip on the HAT

| vendor | URL | part | @1 | @5/10 | @25 | @100 | @500–1000 | reel | stock / lead (2026-09-02) |
|---|---|---|---|---|---|---|---|---|---|
| DigiKey | https://www.digikey.com/en/products/detail/stmicroelectronics/VL53L5CX-SATEL/14552430 | VL53L5CX-SATEL (ST breakout) | **$22.70** | — | — | — | — | — | stock 463; "Manufacturer Standard Lead Time 51 Weeks" |
| DigiKey | https://www.digikey.com/en/products/detail/stmicroelectronics/SATEL-VL53L8/18110499 | SATEL-VL53L8 (ST breakout) | **$32.95** | — | — | — | — | — | "In-Stock: 0", "1 past due"; lead 13 weeks |
| SparkFun | https://www.sparkfun.com/sparkfun-qwiic-mini-tof-imager-vl53l5cx.html | SEN-19013 Qwiic Mini, VL53L5CX | **$25.95** | 10+: **$24.65** | 25+: **$23.36** | 100+: **$22.06** | — | — | "In stock" |
| SparkFun | https://www.sparkfun.com/sparkfun-qwiic-tof-imager-vl53l5cx.html | SEN-18642 Qwiic, VL53L5CX | **$32.50** | 10+: $30.88 | 25+: $29.25 | 100+: $27.63 | — | — | "In stock" |
| Pololu | https://www.pololu.com/product/3419 | #3419 VL53L8CX carrier, regulators, 400 cm | **$24.95** | 5+: **$22.95** | 25+: **$21.12** | 100+: **$19.43** | — | — | "Active and Preferred", backorders allowed |
| Pololu | https://www.pololu.com/product/3418 | #3418 VL53L7CX carrier (wide FOV) | $19.95 | 5+: $18.35 | 25+: $16.89 | 100+: $15.53 | — | — | active |
| DigiKey (bare chip) | https://www.digikey.com/en/products/detail/stmicroelectronics/VL53L5CXV0GC-1/14552424 | VL53L5CXV0GC/1 | **$8.77** | 5: $7.916 / 10: $7.597 | $7.217 | **$6.718** | 500: $6.238 / 1000: **$6.059** | 3,600: $5.767 | stock 7,067; lead 22 weeks |
| DigiKey (bare chip) | https://www.digikey.com/en/products/detail/stmicroelectronics/VL53L8CXV0GC-1/18085238 | VL53L8CXV0GC/1 | **$8.77** | 5: $7.92 / 10: $7.60 | $7.22 | **$6.72** | 500: $6.24 / 1000: **$6.06** | 3,600: $5.77 | stock 6,174; lead 22 weeks |
| Mouser | https://www.mouser.com/ProductDetail/STMicroelectronics/VL53L5CX-SATEL?qs=QNEnbhJQKvYJC8TLRg4rBg%3D%3D | | CANNOT DETERMINE (timeout ×3) | | | | | | |

The two bare-chip tier tables came back identical to the cent; both were
read from their own DigiKey pages. The software supports either generation
(`ELECTRONICS-AND-SOFTWARE.md`), so at ≥100 robots the chip belongs on the
HAT ($6.72 → $6.06) rather than a $19–25 breakout.

## 8. P1 chip — TLV320AIC3104IRHBR audio codec (×1, on the Robot HAT)

| vendor | URL | @1 | @10 | @25/30 | @100 | @250/500 | @1000 | reel | stock / lead |
|---|---|---|---|---|---|---|---|---|---|
| DigiKey (cut tape) | https://www.digikey.com/en/products/detail/texas-instruments/TLV320AIC3104IRHBR/1906853 | **$3.82** | $2.874 | $2.637 | **$2.377** | $2.253 / $2.230 | — | 3,000: **$1.926** | "In-Stock: 64"; "Manufacturer Standard Lead Time 16 Weeks" |
| DigiKey (Digi-Reel) | same | $3.60 | $2.711 | $2.488 | $2.243 | $2.126 / $2.104 | — | +$7.00 reeling fee | |
| LCSC (C181753) | https://lcsc.com/product-detail/Audio-OpAmps_TI_TLV320AIC3104IRHBR_TLV320AIC3104IRHBR_C181753.html | **$2.2518** | $1.8547 | 30+: $1.6357 | **$1.389** | 500+: $1.2795 | **$1.2288** | 3000/reel | "420 In stock, ships now"; MOQ 1 |
| Mouser | https://www.mouser.com/ProductDetail/Texas-Instruments/TLV320AIC3104IRHBR | CANNOT DETERMINE (timeout ×3) | | | | | | | |
| TI store | https://www.ti.com/store/ti/en/p/product/?p=TLV320AIC3104IRHBR | CANNOT DETERMINE (page requires login / blocked) | | | | | | | |
| Arrow / Octopart | https://www.arrow.com/en/products/tlv320aic3104irhbr/texas-instruments ; https://octopart.com/tlv320aic3104irhbr-texas+instruments-7106664 | CANNOT DETERMINE (Akamai block / 403) | | | | | | | |

The other HAT/IMU chips (LSM6DSV16X, BMI088, transceiver, MCU) were not in
this lens's list and are not priced here.

## 9. B12 — speaker, 35 × 25 × 7 mm placeholder (×1)

The mesh is a 12-triangle box; the real part number is unknown (`BOM.md`
B12). The 35 × 25 mm "3525" cavity speaker is the commodity part of that
size.

| vendor | URL | part | size | price | stock |
|---|---|---|---|---|---|
| Thingbits (IN) | https://www.thingbits.net/products/3525-waterproof-8-ohm-2w-cavity-speaker | 3525 cavity speaker, 8 Ω (9 Ω ±15 %), 2 W | 35 × 25 × 6.2 mm | **₹89.00 ex GST (₹105.02)** | "Sold Out" |
| DigiKey | https://www.digikey.com/en/products/detail/soberton-inc/SPM-2035NU/10638200 | Soberton SPM-2035NU, 8 Ω, 2 W (2.5 W max), 82 dB | **39 × 20 × 8.2 mm** (nearest catalogued rectangular 2 W part; not 35×25) | **$9.78** @1; $7.52 @10; $6.55 @36; $6.08 @72; $5.83 @108; $5.34 @252; $4.98 @504; $4.89 @1,008 | stock 75; lead 9 weeks |
| Adafruit | https://www.adafruit.com/product/4227 | #4227 mini oval, 8 Ω, 1 W, PicoBlade 1.25 mm | 30 × 20 × 5 mm | **$1.95**; 10–99: $1.76; 100+: $1.56 | "Out of stock" |
| DigiKey | https://www.digikey.com/en/products/detail/pui-audio-inc/AS02508MS/21531551 | PUI AS02508MS, 8 Ω, 1 W | 25 × 9 × 3 mm (too small — listed for the tier shape only) | $3.39 → $1.57 @1,040 → $1.46 @5,040 | stock 100; lead 26 weeks |
| Same Sky CDS series (DigiKey highlight) | https://www.digikey.com/en/product-highlight/c/cui/cds-series-rectangular-micro-speakers | largest is CDS-25148 25 × 25 mm 1.5 W | no 35×25 in the series | — | — |
| CQRobot 35 × 25 × 6.8 mm 8 Ω 2 W/3 W pair | https://www.amazon.com/CQRobot-Rectangle-Electronic-Application-Components/dp/B0CMQCQQV4 | | | CANNOT DETERMINE (page body not served) | |
| eBay 3525 lots (5 pcs) | https://www.ebay.com/itm/277690727056 ; https://www.ebay.com/itm/404330995155 ; https://www.ebay.de/itm/155604312651 | | | CANNOT DETERMINE (timeout ×6) | |

Exact-size 35×25 speaker at a distributor with tiers: **CANNOT DETERMINE**.
Read prices for that size exist only as a sold-out INR listing.

## 10. B10 — bearing 22 × 16 × 4 mm (×11) — designation

Bore 16 / OD 22 / width 4 is **not** a 6700-family size (6702 = 15×21×4).
It is the thin-section **MR1622-ZZ**, sold under the aliases **ET2216ZZ,
SET2216, A2216, DDA2216(ZZ), 1622ZZ** — the alias list is on the NZ Miniature
Bearings page and the made-in-china listing, and the SMB Bearings drawing
`ET2216-thin-section-bearing-16x22x4mm.pdf` (https://www.smbbearings.com/firebrick/ckeditor/plugins/upload/Uploads/Documents/bearingpdfs/ET2216-thin-section-bearing-16x22x4mm.pdf, text extracted 2026-09-02) gives: SAE52100 chrome steel, pressed-steel cage, static 62 kgf, dynamic 97 kgf, 11,000 rpm.

| vendor | URL | part | price | tiers / MOQ | stock |
|---|---|---|---|---|---|
| NZ Miniature Bearings (NZ) | https://nzminiaturebearings.com/product/16x22x4-mm-mr1622-zz-bearing-sku-00206030.html | MR1622-ZZ, GCr15, ZZ shields | **NZD 5.90 + GST each** | none published | "In Stock Now" |
| Jiang Xin Technology (Guangdong, made-in-china.com) | https://jiangxin2020.en.made-in-china.com/product/IvxJnUDERBpq/China-Stainless-Steel-Ball-Bearing-16-22-4-Et2216-Set2216-A2216-MR1622-Zz.html | MR1622 ZZ stainless, ZZ/2RS/open | **US$1.00–4.00 / piece** | **MOQ 1,000 pieces**; capacity "10,000,000 units"; lead time not stated | — |
| 123Bearing (FR) | https://www.123bearing.com/bearing-housing/deep-groove-bearing/single-row/et2216-ezo | ET2216-EZO | CANNOT DETERMINE (page rendered without price) | | |
| Alibaba | https://www.alibaba.com/product-detail/High-quality-ET2216ZZ-16x22x4mm-Thin-section_1600909236326.html | ET2216ZZ | CANNOT DETERMINE (blank to fetcher) | | |
| Amazon (10 pcs) | https://www.amazon.com/Double-Bearings-ET2216ZZ-16x22x4mm-Bearing/dp/B0CCZWYFW7 | ET2216ZZ ×10 | CANNOT DETERMINE (500) | | |
| VXB / Bearings Direct / Boca | https://vxb.com/search?q=16x22x4 ; https://bearingsdirect.com/search.php?search_query=16x22x4 ; https://www.bocabearings.com/parts/10x15x3 | — | 0 bearing results / 0 results / 403 | | |

USD price at 11 / 110 / 1,100 pieces: **CANNOT DETERMINE** (only NZD retail
and a 1,000-MOQ factory range were readable). At 11,000 pieces (1,000
robots): US$1.00–4.00 from the factory listing.

## 11. B11 — bearing 15 × 10 × 3 mm (×3) — designation

**6700 / 6700ZZ is 10 × 15 × 4 mm**, not ×3 (VXB, FastEddy, Bearings Direct
all list 6700-ZZ as 10x15x4). The 3 mm-wide part is sold as **MR6700 (open)
10x15x3** — a thin variant; alternates on the Bearings Direct page: "MR6700,
61700J1, 61700R, 6700E, 6700". The community mesh reading of the width is
"~3 mm" (`replica_fastener-reconstruction.en.md`), so the true width is
CANNOT DETERMINE until measured on a unit; both are priced.

| vendor | URL | part | price | tiers | stock |
|---|---|---|---|---|---|
| Bearings Direct (US) | https://bearingsdirect.com/6700-ball-bearing-10x15x3-open-mr6700/ | "6700 Ball Bearing 10x15x3 Open MR6700" | **$4.86** | "Buy 10 - 24 and get 5% off", "25 - 49 … 10% off", "50 or above … 15% off" → $4.617 / $4.374 / $4.131 | 722 |
| VXB (US) | https://vxb.com/search?q=MR6700 | "MR6700 Ball Bearing 10x15x3mm Open" | **$9.99** (sale, was $19.99) | none | listed |
| VXB | same | "10x15x3mm Non-Standard Ball Bearing Shielded" | $19.99 (was $30.00) | none | listed |
| VXB | same | MR6700-ZZ / MR6700-2RS, **10x15x4** | $7.77 (was $10.00) | none | listed |
| FastEddy Bearings (US) | https://www.fasteddybearings.com/10x15x4-metal-shielded-bearing-6700-zz/ | 6700-ZZ **10x15x4** | **$1.25** | none | "backorder … 7-10 days" |
| Boca Bearings | https://www.bocabearings.com/parts/10x15x3 | | CANNOT DETERMINE (403) | | |
| 123Bearing | https://www.123bearing.com/bearing-housing/deep-groove-bearing/single-row/6700 | | CANNOT DETERMINE (no price rendered) | | |

## 12. B18 — M2 socket-head screws and M2 heat-set inserts

Counts are the community's mesh-derived buy list (`BOM.md` §4, flagged): M2×4
×60, M2×6 ×80, M2×8 ×40, M2×12 ×15 (= 195 M2 screws), M2 nuts ×50, M2
inserts ×60, M2.5×6 ×20.

### 12.1 Screws (price read for M2×6 only; other lengths not read)

| vendor | URL | part | @1 | @10 | @25 | @50 | @100 | @1000 | delivery |
|---|---|---|---|---|---|---|---|---|---|
| RST-Versand (DE) | https://www.rst-versand.de/Zylinderschraube-Innensechskant-M2-x-6-mm-A2-DIN912_1 | M2×6 A2 DIN 912 | **€0.06** | 10-pack €0.56 (€0.056 ea) | 25-pack €1.30 (€0.052) | 50-pack €2.43 (€0.0486) | 100-pack **€4.34 (€0.0434 ea)** | — | "Lieferstatus: 1-2 Tage" |
| der-schraubenladen (DE) | https://shop.der-schraubenladen.de/DIN-912-ISO-4762-Zylinderschraube-Innensechskant-Edelstahl-A2/SW11250.54 | DIN 912 A2, 100-pack; page opened on M2.5×8 = **€4.67/100**; M2×6 is in the size dropdown but its price was not rendered | | | | | (M2.5×8: €4.67/100) | — | "Sofort verfügbar, Lieferzeit: 1-3 Tage" |
| Accu (UK) | https://www.accu.co.uk/socket-cap-screws/1077-SSCM2-6-A2 | | CANNOT DETERMINE (403) | | | | | | |
| Bolt Depot / McMaster-Carr / Misumi (US) | https://www.boltdepot.com/Product-Details?product=15964 ; https://www.mcmaster.com/91292A831/ ; https://us.misumi-ec.com/vona2/detail/221000348314/?HissuCode=SNSS-M2X6 | | CANNOT DETERMINE (403 / blank / 403) | | | | | | |
| Albany County Fasteners (US) | https://www.albanycountyfasteners.com/Socket-Head-Cap-Screw-2MM-A2-Stainless-Steel-p/5020000.htm | M2×6 A2 | CANNOT DETERMINE (page served without price) | | | | | | |
| Amazon 100-pack / eBay 200-pack / GetFPV 20-pack | https://www.amazon.com/100Pcs-Stainless-Screws-Socket-Fastener/dp/B07G2QXHFV ; https://www.ebay.com/itm/172217211739 ; https://www.getfpv.com/m2x6-socket-head-cap-screw-set-20pcs.html | | CANNOT DETERMINE (500 / timeout / 403) | | | | | | |

1,000-piece and 10,000-piece screw pricing: **CANNOT DETERMINE** (no vendor
with a >100 tier was readable). M2 nuts, M2.5×6: not priced.

### 12.2 Heat-set inserts M2 (×60)

| vendor | URL | part | price / 100 | per insert | stock |
|---|---|---|---|---|---|
| CNC Kitchen (DE) | https://cnckitchen.store/products/heat-set-insert-m2-x-3-100-pieces | M2 × 3.0 mm, brass (lead & cadmium free) | **€9.90** | €0.099 | "Auf Lager – Versand vor 12 Uhr am gleichen Tag" |
| Prusa Research (US shop) | https://www.prusa3d.com/product/heat-set-inserts-m2-short-100-pcs/ | M2 short | **$11.99** | $0.1199 | "In stock" |
| Vector 3D (UK) | https://vector3d.shop/products/heat-set-insert-m2-standard | M2 × 3.0 mm | **£9.74** | £0.0974 | "In stock" |
| Amazon HANGLIFE 100 pcs | https://www.amazon.com/Heat-Set-Threaded-Inserts-Insert-Tips/dp/B0D4L464XG | | CANNOT DETERMINE (500) | | |

No tiers above 100 published at any of the three; per robot (60): **$7.19 / €5.94 / £5.84**.

## 13. Not researched in this lens (still CANNOT DETERMINE, as in `BOM.md`)

B8 22-pin CSI flex (length unknown); B13 microphone(s); B14 NFC antennas +
reader IC; B15 REC LED; B16 gamepad; B17 USB-C cable; B19 filament/TPU; the
custom PCBs P1/P2/P3 (bare board + assembly quotes); LSM6DSV16X, BMI088,
half-duplex transceiver, IMU-board MCU.

## 14. Roll-up — bought cost per robot at 1 / 10 / 100 / 1,000 robots

Rules: only lines with a price **read** on 2026-09-02 enter a total; the
cheapest read vendor is used; a line without a tier at that quantity keeps
its @1 price (a ceiling, not a forecast); native-currency lines are summed
separately, unconverted. "10 robots" means 10× the per-robot quantity was
looked up in the vendor's tier table (e.g. 30 bearings, 150 servos).

### 14.1 USD lines, exact part read

| line | qty | vendor used | 1 robot | 10 robots | 100 robots | 1,000 robots | tier basis |
|---|---|---|---|---|---|---|---|
| XL330-M288-T | 15 | ROBOTIS intl $23.90 | **$358.50** | $358.50 | $358.50 | $358.50 | no tiers published; OEM quote CANNOT DETERMINE |
| X3P cables 180 mm | 16 | ROBOTIS intl $15.50/10 | $24.80 | $24.80 | $24.80 | $24.80 | no tiers |
| NP-F550 pack (+ dual-charger share) | 1 | NextBatteries $49.90 / 2 | $24.95 | $24.95 | $24.95 | $24.95 | no tiers; OEM pack CANNOT DETERMINE |
| IMX219 M12 board + 75° lens | 1 | UCTRONICS B0183 $23.99 (sale; regular $39.99) | $23.99 | $23.99 | $23.99 | $23.99 | no tiers |
| ToF breakout | 1 | Pololu #3419 | $24.95 | $22.95 | $19.43 | $19.43 | 5+ / 100+ tiers; no 1000 tier |
| TLV320AIC3104IRHBR | 1 | LCSC | $2.25 | $1.85 | $1.39 | $1.23 | 10+ / 100+ / 1000+ |
| bearing 10×15×3 (MR6700) | 3 | Bearings Direct | $14.58 | $13.12 | $12.39 | $12.39 | −10 % at 25–49, −15 % at 50+ |
| M2 inserts | 60 | Prusa $11.99/100 | $7.19 | $7.19 | $7.19 | $7.19 | no tiers |
| **USD subtotal, exact parts** | | | **$481.21** | **$477.35** | **$472.64** | **$472.48** | |

### 14.2 USD lines where only a bracket / substitute was readable (kept out of 14.1)

| line | qty | what was read | 1 | 10 | 100 | 1,000 |
|---|---|---|---|---|---|---|
| Radxa Zero 3W "1 GB/32 GB" | 1 | SKU does not exist in Radxa's table; nearest catalogue SKU 1 GB/8 GB header $23 (ALLNET, sold out); 4 GB/32 GB $51 | $23–51 | same | same | same |
| speaker 35×25×7 | 1 | nearest catalogued 2 W 8 Ω rectangular part, Soberton SPM-2035NU 39×20×8.2 (DigiKey) | $9.78 | $7.52 | $6.08 (72-tier) | $4.98 (504-tier) |
| ToF as bare chip on the HAT instead of a breakout | 1 | VL53L8CXV0GC/1 (DigiKey) | $8.77 | $7.60 | $6.72 | $6.06 |
| **14.1 + Radxa low bracket + speaker substitute** | | | **$513.99** | **$507.87** | **$501.72** | **$500.46** |
| same, with the ToF moved onto the HAT | | | $497.81 | $492.52 | $489.01 | $487.09 |

### 14.3 Native-currency lines (read, not converted)

| line | qty | vendor | per robot | tier basis |
|---|---|---|---|---|
| bearing 22×16×4 (MR1622-ZZ) | 11 | NZ Miniature Bearings NZD 5.90 + GST | **NZD 64.90 + GST** at 1/10/100 robots; at 1,000 robots (11,000 pcs) the factory listing gives **US$11.00–44.00** (US$1–4/pc, MOQ 1,000) | no NZD tiers |
| M2 screws (195, priced as if all were M2×6) | 195 | RST-Versand €4.34/100 | **€8.46** at every quantity read (100-pack is the largest tier) | lengths other than M2×6 not read |
| M2 nuts ×50, M2.5×6 ×20 | | | CANNOT DETERMINE | |

### 14.4 What the numbers say

- Read bought cost per robot, exact parts only, is **$472–481 in USD plus
  ~NZD 65 of bearings and ~€8.5 of screws**, before the Radxa board (no such
  SKU / sold out everywhere), the speaker, the mics, NFC, LED, gamepad,
  USB-C, flex, three custom PCBs and their remaining chips, and any filament.
  Pollen's retail price is $399 / €340 for the assembled robot with gamepad,
  battery and cable (`BOM.md` §5.1).
- **The servos are $358.50 of that (75 %)** and are the only line with no
  published tier at any quantity. Every other read line together moves by
  less than $9 between 1 and 1,000 robots. The volume question for this
  robot is therefore one number: ROBOTIS's OEM price for XL330-M288-T at
  1,500 and 15,000 units — CANNOT DETERMINE until a quote is obtained
  (america@robotis.com / contactus2@robotis.com; ROBOTIS's only published
  bulk discount is −9.9 % at 6 units on AX-12A).
- Second-order: the Radxa SKU (custom 1 GB/32 GB from Radxa, or the $22–23
  1 GB/8 GB catalogue part) and the ToF-on-HAT decision ($6 vs $19–25).
- Lead times read: XL330 10 days (ROBOTIS intl list page) / 24–48 h (373 in
  stock, Generation Robots); TLV320AIC3104 16 weeks factory (DigiKey, 64 in
  stock) vs 420 in stock at LCSC; VL53L5CX-SATEL 51 weeks factory (463 in
  stock); bare VL53L5/8CX 22 weeks (6–7 k in stock); SPM-2035NU 9 weeks;
  Radxa Zero 3W: sold out at every US/CN retailer read on 2026-09-02, lead
  time CANNOT DETERMINE.

## 15. Retry list for the next agent (URLs that blocked a price)

RobotShop XL330 (403); OKdo Zero 3W 1 GB and 4 GB/32 GB (socket closed);
RS Online 2564694 (hang); arducam.com B0183/B0188 (403); Mouser
VL53L5CX-SATEL and TLV320AIC3104IRHBR (timeouts); TI store TLV320AIC3104
(login); B&H Neewer 66600244 (403); Alibaba Beston NP-F550 (blank); NKON
ICR18650-26J (403); eBay 3525 speaker lots (timeouts); Amazon CQRobot
B0CMQCQQV4 (no body); 123Bearing ET2216-EZO and 6700 (no price rendered);
Boca 10x15x3 (403); Accu SSCM2-6-A2, Bolt Depot 15964, McMaster 91292A831,
Misumi SNSS-M2X6 (403/blank). A browser session (not the text fetcher) reads
most of these.
