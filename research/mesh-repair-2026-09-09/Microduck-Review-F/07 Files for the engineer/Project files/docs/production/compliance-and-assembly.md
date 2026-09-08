# Compliance, shipping, packaging and assembly labour — Microduck rebuild

*Written 2026-09-02 (web research done 2026-09-02 between 00:00 and 01:00 +0800; the
Pollen store JSON was fetched 2026-09-01 and lives in `research/raw/store_*.json`).
Lens: what it takes to put a Microduck-class product — 15 × XL330, Radxa Zero 3W,
custom HAT + `imu_to_dxl`, removable NP-F550 2S pack, Wi-Fi/BT, sold to consumers
aged 16+ — legally into a box and onto a carrier, and how many minutes of labour
the box contains. Every number carries a source ID from §0 and the date it was
read. A number we did not read is CANNOT DETERMINE with what settles it. Companion
docs: `docs/BOM.md`, `docs/PARTS.md`, `docs/ELECTRONICS-AND-SOFTWARE.md`.*

## 0. Sources (all fetched 2026-09-02 unless marked)

| ID | what | URL |
|---|---|---|
| S1 | Pollen store, Microduck listing JSON (fetched 2026-09-01) | https://store.pollen-robotics.com/products/microduck.json |
| S2 | Pollen store, Dev Pack JSON (2026-09-01) | https://store.pollen-robotics.com/products/dev-pack.json |
| S3 | Pollen store, Accessory Pack JSON (2026-09-01) | https://store.pollen-robotics.com/products/accessory-pack.json |
| S4 | Pollen store, Charger Pack JSON (2026-09-01) | https://store.pollen-robotics.com/products/charger-pack.json |
| S5 | Pollen store refund policy | https://store.pollen-robotics.com/policies/refund-policy |
| S6 | Pollen store terms of service | https://store.pollen-robotics.com/policies/terms-of-service |
| S7 | Pollen store shipping policy | https://store.pollen-robotics.com/policies/shipping-policy |
| S8 | Microduck press kit | https://pollen-robotics.com/microduck/press-kit/ |
| S9 | IATA "Battery Guidance Document — Revised for the 2026 Regulations" (dated 01/01/2026, based on ICAO TI 2025–2026 and DGR 67th ed.) | https://www.iata.org/contentassets/05e6d8742b0047259bf3a700bc9d42b9/lithium-battery-guidance-document.pdf |
| S10 | DHL Express "Lithium Batteries and Sodium Ion Batteries Guidance" V2.1, effective 01 January 2026 | https://mydhl.express.dhl/content/dam/downloads/global/en/lithium-batteries/dhl_express_lithium_battery_guide.pdf.coredownload.pdf |
| S11 | 49 CFR 173.185 (US ground/air, DOT) | https://www.law.cornell.edu/cfr/text/49/173.185 |
| S12 | USPS Publication 52 §349 (domestic mail) | https://pe.usps.com/text/pub52/pub52c3_028.htm |
| S13 | USPS International Mail Manual §135.64 | https://pe.usps.com/text/imm/immc1_014.htm |
| S14 | Colissimo (La Poste) lithium battery conditions | https://www.colissimo.entreprise.laposte.fr/en/practical-advice/right-packaging/almost-perfect-parcel-web-series/lithium-batteries |
| S15 | Duracell NP-F330/NP-F550 replacement listing (7.2 V, 2600 mAh, 18 Wh, 3.5 oz) | https://www.tradeinn.com/techinn/en/duracell-sony-np-f330-np-f550-2600mah-7.2v-lithium-battery/137796011/p |
| S16 | Neewer NP-F550 replacement listing (DC 7.2 V, 2600 mAh, $24.99) | https://neewer.com/products/neewer-7-4v-2600mah-rechargeable-li-ion-battery-pack-replacement-for-sony-np-f550-570-530-66600682 |
| S17 | Lion Technology, "New lithium battery state of charge limit in effect Jan 1 [2026]" | https://www.lion.com/lion-news/december-2025/new-lithium-battery-state-of-charge-limit-in-effect-jan-1 |
| S18 | FCC ID 2BC6T-RADXAZERO3W (fccid.io mirror) | https://fccid.io/2BC6T-RADXAZERO3W |
| S19 | Radxa Zero 3W product page + docs | https://radxa.com/products/zeros/zero3w/ ; https://docs.radxa.com/en/zero/zero3 |
| S20 | FCC KDB 996369 D04 "Module Integration Guide" (read via search snippet only) | https://apps.fcc.gov/kdb/GetAttachment.html?id=bNCiEdkFEKnHsZF9GHCNdg%3D%3D&desc=996369+D04+Module+Integration+Guide+V02&tracking_number=44637 |
| S21 | 47 CFR 15.101 (equipment authorisation, Table 1) | https://www.law.cornell.edu/cfr/text/47/15.101 |
| S22 | European Commission, Radio Equipment Directive page | https://single-market-economy.ec.europa.eu/sectors/electrical-and-electronic-engineering-industries-eei/radio-equipment-directive-red_en |
| S23 | Commission Implementing Decision (EU) 2025/138 (EN 18031 listing) | https://eur-lex.europa.eu/eli/dec_impl/2025/138/oj/eng |
| S24 | EC RED harmonised-standards page | https://single-market-economy.ec.europa.eu/single-market/goods/european-standards/harmonised-standards/radio-equipment_en |
| S25 | EC LVD harmonised-standards page | https://single-market-economy.ec.europa.eu/single-market/goods/european-standards/harmonised-standards/low-voltage-lvd_en |
| S26 | Nemko, EN IEC 62368-1 3rd-edition status (article dated 2023-01-02) | https://www.nemko.com/blog/postponed-implementation-of-new-european-safety-standard-edition-for-electronics |
| S27 | Directive 2009/48/EC (Toy Safety), EUR-Lex | https://eur-lex.europa.eu/eli/dir/2009/48/oj/eng |
| S28 | Directive 2009/48/EC Annex I (legislation.gov.uk copy) | https://www.legislation.gov.uk/eudr/2009/48/annex/I |
| S29 | UL Solutions on Regulation (EU) 2025/2509 (new Toy Safety Regulation) | https://www.ul.com/news/ec-publishes-toy-safety-regulation-regeu-20252509 |
| S30 | EUR-Lex summary of Regulation (EU) 2023/1542 (Batteries) | https://eur-lex.europa.eu/legal-content/EN/LSU/?uri=CELEX:32023R1542 |
| S31 | Compliance Gate, removable/replaceable battery rules | https://www.compliancegate.com/removable-and-replaceable-battery-requirements-european-union/ |
| S32 | GOV.UK "Using the UKCA marking" (page updated 21 August 2026) | https://www.gov.uk/guidance/using-the-ukca-marking |
| S33 | US ITA trade.gov, "UK extends CE mark recognition" | https://www.trade.gov/market-intelligence/united-kingdom-extends-ce-mark-recognition |
| S34 | Compliance Gate, PPWR (EU) 2025/40 timeline | https://www.compliancegate.com/ppwr-timeline-and-dates/ |
| S35 | TÜV Rheinland on GPSR (EU) 2023/988 (search snippet) | https://www.tuv.com/regulations-and-standards/en/eu-general-product-safety-regulation-eu-2023-988-gpsr-entered-into-force.html |
| S36 | F2 Labs on Machinery Directive Art. 1(2)(k); Regulation (EU) 2023/1230 EUR-Lex (search snippet) | https://f2labs.com/technotes/2016/06/10/machinery-directive-200642ec-article-1-2-k/ ; https://eur-lex.europa.eu/eli/reg/2023/1230/oj/eng |
| S37 | Deutsche Recycling on Triman / Info-tri (search snippet) | https://deutsche-recycling.com/blog/triman-logo-in-france-2/ |
| S38 | WEEE Annex IX (lexparency, search snippet); RoHS 2 (TÜV SÜD, search snippet) | https://lexparency.org/eu/32012L0019/ANX_IX/ ; https://www.tuvsud.com/en-us/services/product-certification/ce-marking/ce-rohs-2 |
| S39 | Japan PSE for lithium batteries (battery-cert.com, search snippet) | http://www.battery-cert.com/en/cases/show/28.html |
| S40 | Korea KC EMC (MPR, search snippet); Japan Giteki (IB-Lenhardt, search snippet) | https://www.korea-certification.com/en/kc-emc/kc-emc-certification/ ; https://ib-lenhardt.com/kb/mic-requirements |
| S41 | ADR SP 188 (lion-care, search snippet) | https://www.lion-care.com/en/Info-Center/Industry-knowledge/Guidelines-and-laws-for-the-transport-of-lithium-batteries/Special-provisions-from-the-ADR/ |
| S42 | ROBOTIS US store, XL330-M288-T | https://www.robotis.us/dynamixel-xl330-m288-t/ |
| S43 | FabFlow, Boothroyd-Dewhurst DFA guide (secondary; time tables) | https://www.fabflow.app/blog/design-for-assembly-dfa-complete-engineering-guide |
| S44 | Devenish, "Conducting a Step-by-Step DFA Analysis", DFMA Forum 2019 (Boothroyd Dewhurst Inc.) | https://www.dfma.com/forum/2019pdf/devenish.pdf |
| S45 | LégiSocial, SMIC 2026 | https://www.legisocial.fr/reperes-sociaux/montant-smic-2026-taux-horaire-net-brut.html |
| S46 | China Briefing minimum wages (updated 2026-06-15); Playroll China (search snippet) | https://www.china-briefing.com/news/minimum-wages-china/ ; https://www.playroll.com/minimum-wage/china |
| S47 | EC common charger page (search snippet) | https://single-market-economy.ec.europa.eu/sectors/electrical-and-electronic-engineering-industries-eei/radio-equipment-directive-red/one-common-charging-solution-all_en |
| S48 | Local: `SPEC.md`, `docs/BOM.md`, `docs/PARTS.md`, `research/01-product-and-specs.md` | — |

"Search snippet" = the figure was read from a search-engine result, not from the
page itself; treat as one notch weaker than a fetched page.

## 1. The battery — what is being shipped

| fact | value | source |
|---|---|---|
| pack | removable NP-F550, "2600 mAh", 2S Li-ion | S8; `SPEC.md` §5 |
| nominal voltage (replacement-pack listings; Sony's own page could not be fetched) | 7.2 V | S15, S16 |
| Watt-hour rating | 7.2 V × 2.6 Ah = **18.72 Wh**; Duracell listing prints "18 Wh" | S15 (computed per USPS definition Wh = Ah × V, S12 §349.21) |
| per-cell | 2 cells in series → 9.36 Wh per cell if the cells are equal | derived from S15 "Number of cells: 2" (search-snippet level) |
| mass | "3.5 oz" (99 g) | S15 |
| envelope | 38.4 × 20.6 × 70.8 mm (mesh `np_f970`, F550-sized) | `SPEC.md` §4.1 |
| threshold position | cell 9.36 Wh ≤ 20 Wh and battery 18.72 Wh ≤ 100 Wh → **"small" lithium-ion in every regime below**; > 2.7 Wh so it is *not* a button-cell-class exemption | S9 classification (cells ≤ 20 Wh / batteries ≤ 100 Wh → Section II) |
| UN 38.3 test summary | required from the manufacturer and "subsequent distributors … of equipment powered by cells and batteries manufactured after 30 June 2003"; ten data elements (a–j); may be a website + QR/URL, not a paper per shipment | S9 p.8 |
| Wh marking on the battery case | required (USPS: "Each battery must display the 'Watt-hour' or 'Wh' marking"; ADR SP 188 likewise) | S12 §349.241; S41 |

**CANNOT DETERMINE:** which NP-F550 brand Pollen fits and therefore whose UN 38.3
test summary applies (a supplier's test summary settles it); whether Pollen's pack is
7.2 V or 7.4 V nominal (Neewer's URL says 7.4 V, its page says DC 7.2 V — the label
on a shipped pack settles it; either way < 20 Wh).

## 2. Lithium battery shipping rules, regime by regime

### 2.1 Air (ICAO TI 2025–2026 / IATA DGR 67th edition, from 1 Jan 2026) — S9, S10

Three configurations arise from Pollen's own SKUs (S1–S4):

| configuration | UN number / PI | why | 2026 state-of-charge rule | package limits | marks / paperwork |
|---|---|---|---|---|---|
| **Robot box** (battery installed in the robot; S1 "Robot, battery, USB-C cable, game controller") | **UN 3481, PI 967 Section II** | one battery ≤ 100 Wh *contained in* equipment | *recommended* only: "at a state of charge not exceeding 30% … or with an indicated battery capacity not exceeding 25%" — "not mandatory for these items" (S9 p.14) | 5 kg net batteries per package, PAX and CAO (S10) | lithium battery mark (UN 3481) + AWB statement "Lithium ion batteries in compliance with Section II of PI967" — **except** "for consignments of two packages or less where each package contains no more than four cells, or two batteries installed in equipment" (S9 F.04); one robot = one battery → a 1- or 2-box consignment needs **no mark and no statement** (S10: "No requirements … Maximum 2 packages per shipment") |
| **Robot + spare packs in the same outer box** | **UN 3481, PI 966 Section II** | batteries *packed with* the equipment they power | **mandatory ≤ 30 % SoC** for cells/batteries > 2.7 Wh (18.72 Wh qualifies): "must be offered for transport at a state of charge not exceeding 30% of their rated capacity" (S9 p.14) | "those necessary to power the equipment plus 2 spare sets" → robot + 2 spares max; 5 kg net; 1.2 m drop + stacking test on the package (S10) | mark + statement "Lithium ion batteries in compliance with Section II of PI966"; DHL: "TDI – Account must be approved" (S10) |
| **Charger Pack / Dev Pack shipped alone** (2 batteries + charger, S4; 2 batteries + charger + motors, S2) | **UN 3480, PI 965 Section IB** | IATA D.05: "When a package contains only an AC adaptor or charger, or ancillary cables etc, and lithium-ion batteries, the package must be classified as 'UN 3480, Lithium ion batteries' and packaged in accordance with PI 965" (S9 p.23) | mandatory ≤ 30 % SoC (S10) | **Cargo Aircraft Only**, 10 kg net per package, Shipper's Declaration required, Class 9 label + CAO label + battery mark (S10 PI 965 IB) | "TDI – Account must be approved. The service is limited due to CAO restrictions" (S10) |

Consequences for a Pollen-like store: an order of "robot + Charger Pack" is cheapest
to ship by air as **one box (PI 966 Section II)** with the spares discharged to ≤ 30 %,
never as two parcels — the stand-alone Charger Pack is fully regulated DG by air. Which
of these Pollen actually does: **CANNOT DETERMINE** (an order with both, and the
carrier label on the box, settles it).

Other 2026 air facts read from S9: the mark is 100 × 100 mm, reducible to 100 × 70 mm,
red hatched border ≥ 5 mm, UN number ≥ 12 mm high (F.01–F.02); equipment must be
packaged "in a manner that prevents unintentional activation" (E.08) — the Microduck
has **no power switch** in any source (`ELECTRONICS-AND-SOFTWARE.md` §9), so the box
insert must physically prevent the battery contacts from being made, or the pack ships
*outside* the robot (which turns the robot box into PI 966, see row 2); damaged or
recalled batteries are forbidden by air (D.06).

### 2.2 Road within Europe (ADR) — S41 (search-snippet level)

SP 188: cells ≤ 20 Wh, batteries ≤ 100 Wh, UN 38.3 tested, short-circuit protected;
Wh marked on the case; exempt from full ADR (no orange plates, no transport document,
no ADR driver certificate); the ADR 2023 mark no longer needs a telephone number and
is 100 × 100 mm. Primary text (UNECE ADR 2025 vol. II, 3.3 SP 188) not fetched —
CANNOT DETERMINE beyond the snippet.

### 2.3 United States ground (49 CFR 173.185) — S11

"Watt-hour (Wh) rating may not exceed 20 Wh for a lithium ion cell or 100 Wh for a
lithium ion battery"; UN 38.3 + test summary under (b); lithium battery mark required
except "when a consignment contains two packages or fewer where each package contains
not more than four lithium cells or two lithium batteries contained in equipment";
"Except when lithium cells or batteries are packed with, or contained in, equipment,
each package must not exceed 30 kg". Pollen ships US orders "from the US" (S7), so the
domestic leg is this regime.

### 2.4 Postal — USPS (S12, S13) and La Poste/Colissimo (S14)

| | robot box (battery installed) | spares packed with robot | spares alone |
|---|---|---|---|
| USPS domestic | mailable, air or surface; ≤ 8 cells or 2 batteries per mailpiece; UN 3481 mark unless ≤ 4 cells / 2 batteries installed (S12 §349.242, §349.221) | mailable; 8 cells or 2 batteries; mark required (§349.243) | **surface only**, 5 lb, "Forbidden for Transportation Aboard Passenger Aircraft" text (§349.244) |
| USPS international | only "installed in the equipment they are intended to operate"; max "four lithium cells or two lithium batteries"; 20 Wh / 100 Wh; Wh marked on the battery; "Mailpieces must not bear markings or labels identifying the contents as lithium batteries" (S13 §135.64) | **prohibited** | **prohibited** |
| Colissimo (France + Europe only) | "maximum 4 lithium ion batteries or 2 ion power packs, UN3481 (packaging instruction 967, Section II) per parcel … 20 Wh … 100 Wh … 5 kg per parcel"; "air shipments outside Europe are prohibited" (S14) | not stated on the page — CANNOT DETERMINE | not stated — CANNOT DETERMINE |

Pollen names Colissimo and Mondial Relay among its carriers (S7); Mondial Relay's
battery terms were not fetched — CANNOT DETERMINE.

## 3. Product compliance — EU (CE)

The Radxa Zero 3W's radio makes the whole robot **radio equipment**; the RED then
carries safety (Art. 3(1)(a)) and EMC (Art. 3(1)(b)) as well as spectrum (Art. 3(2))
(S22). Directives that apply in parallel are listed with their trigger.

| obligation | applies? | what it requires | source |
|---|---|---|---|
| **RED 2014/53/EU** | yes — Wi-Fi 6 / BT 5.4 on the Radxa (S19 "Onboard Wi-Fi 6 & BT 5.4"; press kit: "radio versions … still being finalised", S8) | DoC, CE mark, technical file; harmonised standards for 2.4/5 GHz and EMC are listed by Implementing Decision (EU) 2022/2191 as amended (latest amendment "9 December 2025", S24). **Which ETSI standards are currently cited was not read** — the EC summary list PDF (generated 13.10.2025, S24) settles it. **No EU equivalent of the FCC modular grant**: the Radxa module's CE status does not transfer to the host; the robot needs its own RED assessment | S22, S24 |
| **RED cybersecurity, Delegated Reg. (EU) 2022/30** | yes — "entered into application in August 2025", activating Art. 3(3)(d)(e)(f) for "internet-connected, process personal data, or are toys/childcare products" (S22). Microduck streams camera/audio over WebRTC and pairs by BLE with a PIN (`ELECTRONICS-AND-SOFTWARE.md` §10) → (d) and (e) | EN 18031-1:2024 (d) and EN 18031-2:2024 (e) listed by Decision (EU) 2025/138 of 28 Jan 2025 — presumption of conformity **withheld** "if the user is allowed not to set and use any password" (18031-1 cl. 6.2.5.1/6.2.5.2) and, for 18031-2, where "parental or guardian access control is not ensured" (S23). Pollen's default pairing PIN `000000` (`cheat:553`) is a design point to test against this | S22, S23 |
| **Safety standard** | EN 62368-1 family (AV/ICT) via RED 3(1)(a) / LVD 2014/35/EU | EN 62368-1:2014 (2nd ed.) is OJ-listed; EN IEC 62368-1:2020 (3rd ed.) was not, per Nemko (article 2023-01-02, S26). The EC LVD list has amendments up to "22 July 2025" but its summary "from April 2025 onwards … not updated" (S25) → **current OJ edition CANNOT DETERMINE**; OJ L series search settles it. Battery-powered ≤ 8.2 V and USB-C 5 V in: inside 62368-1 ES1 territory, but servo pinch points (15 joints, up to ±0.96 N·m fitted, `SPEC.md`) are MS (mechanical) hazards to be assessed | S25, S26 |
| **EMC 2014/30/EU** | subsumed by RED 3(1)(b) for radio equipment | EN 55032/55035 class B typical — standard citation not verified here (CANNOT DETERMINE) | S22 |
| **Toy Safety Directive 2009/48/EC** | **not applicable if Pollen's positioning holds**: scope is "products designed or intended, whether or not exclusively, for use in play by children under 14 years of age" (Art. 2(1), S27); Pollen's terms say products are "recommended for users aged 16 and over" and not children's toys (S6); press kit: "any age recommendation … still being finalised" (S8). Annex I excludes "Electronic equipment, such as personal computers and game consoles, used to access interactive software and their associated peripherals" and "products for collectors, provided that the product or its packaging bears a visible and legible indication that it is intended for collectors of 14 years of age and above" (S28). Because "whether or not exclusively" and the duck styling invite a market-surveillance argument, the 16+ marking must be on the packaging and listing ("before the purchase, including in cases where the purchase is made on-line", Art. 11(2), S27) | S6, S8, S27, S28 |
| **Toy Safety Regulation (EU) 2025/2509** | same scope question; in force 1 Jan 2026, applies 1 Aug 2030, repeals 2009/48/EC then (S29) | no change to the answer above before 2030 | S29 |
| **Batteries Regulation (EU) 2023/1542** | yes — NP-F550 is a "portable battery" (sealed, ≤ 5 kg; S31) | CE marking of batteries from 18 Aug 2024; labelling from 18 Aug 2026; QR code and **Art. 11 removability/replaceability by the end-user from 18 Feb 2027** (S30, S31). Microduck's removable camera pack **passes Art. 11 by design**: removable with no tool, and NP-F550s are a commodity, satisfying the "five years after placing the last unit" spare-availability rule (S31). Producer registration/EPR from 18 Aug 2025 (S30) | S30, S31 |
| **RoHS 2011/65/EU** | yes — EEE | 10 restricted substances, CE-marking directive; supplier declarations for every PCB, servo, cable, filament pigment | S38 |
| **WEEE 2012/19/EU** | yes | crossed-out wheeled bin (Annex IX) "printed visibly, legibly and indelibly" on the product; producer registration in each member state sold to | S38 |
| **GPSR (EU) 2023/988** | yes, from 13 Dec 2024 | EU responsible person; online listing must show manufacturer name, postal and electronic address (Art. 19) — Pollen's store shows "Pollen Robotics SAS … 2 Place Jean Jaurès, 33000 Bordeaux" (S5, S6) | S35 |
| **Machinery** (Dir. 2006/42/EC → Reg. (EU) 2023/1230 from 20 Jan 2027) | **CANNOT DETERMINE (legal interpretation)**: Art. 1(2)(k) excludes "household appliances intended for domestic use, audio and video equipment, information technology equipment" (S36); a 780 g walking robot for 16+ hobbyists is not obviously any of these. A notified-body or lawyer opinion settles it | S36 |
| **Common charger Dir. (EU) 2022/2380** | category list (phones, tablets, cameras, headphones, consoles, e-readers, keyboards, mice, navigation; laptops from 28 Apr 2026) does not name robots (S47) → not applicable as of the list read; robot already charges via USB-C 5 V (`ELECTRONICS-AND-SOFTWARE.md` §9) | S47 |
| **France: Triman + Info-tri** | yes (EEE and batteries): mandatory since 15 Dec 2022, no sell-through after 16 Jun 2023, on product or packaging (S37, search-snippet level) | S37 |
| **PPWR (EU) 2025/40** | applies from 12 Aug 2026; empty-space ratio (Art. 24) preliminary 12 Feb 2028, full 1 Jan 2030; material-composition label by 12 Aug 2028; minimisation (Art. 10) by 1 Jan 2030 (S34) | affects the box design in §6 | S34 |

## 4. Product compliance — US, UK, Japan, Korea

| market | radio | safety / other | source |
|---|---|---|---|
| **US (FCC)** | Radxa Zero 3W holds **FCC ID 2BC6T-RADXAZERO3W**, grantee "Radxa Computer (Shenzhen) Co., Ltd.", granted 11/13/2023, **"Single Modular Approval"**, Part 15C DTS/DSS, 2402–2480 MHz (0.00287 W / 0.00318 W conducted) and 2412–2462 MHz (0.0207 W) — **no 5 GHz (Part 15E) grant listed**, so the "Wi-Fi 6" 5 GHz radio, if enabled, is not covered by this grant (S18). Host obligations per KDB 996369 D04: the host still needs Part 15B authorisation (SDoC for "Other Class B digital devices", 47 CFR 15.101 Table 1, S21) and "testing on the product with the transmitter(s) operating" (S20, snippet); the module's integration instructions (antenna, RF exposure) must be followed | SDoC + label; no US safety mark is legally required for a battery-powered device, retailers may ask for UL/ETL/62368-1 report (CANNOT DETERMINE what Pollen holds) | S18, S20, S21 |
| **UK** | CE marking "continues to be recognised … alongside or in place of the UKCA marking, for the Great Britain market" (S32, page updated 21 Aug 2026); the 2023 announcement covered radio equipment, EMC, toys and low-voltage electrical equipment (S33). S32 also mentions transition provisions ending 31 Dec 2027 — **whether that date bounds CE recognition for radio equipment is CANNOT DETERMINE** from the page summary; the Product Safety and Metrology etc. (Amendment) Regulations 2024 text settles it | UK importer address on the product/packaging still required; UK WEEE/battery producer registration separate | S32, S33 |
| **Japan** (in Pollen's launch list, S1) | Giteki (MIC) mark and number on the radio — module or host (S40, snippet) | PSE (DENAN) for lithium cells/packs ≥ 400 Wh/L per cell since 1 Feb 2019 (S39, snippet). A 2600 mAh 18650 (9.36 Wh in ≈ 16.5 cm³) is ≈ 570 Wh/L → **above the threshold**; whether an NP-F-format pack sold with/inside a robot is a "mobile battery" under METI's definition: **CANNOT DETERMINE** — METI's scope note or a Japanese importer settles it | S39, S40 |
| **South Korea** (launch list, S1) | KC EMC/radio certification; pre-certified modules reduce but do not remove host testing (S40, snippet) | KC safety for the lithium pack (KC 62133) typical — not verified here | S40 |
| **Switzerland / Norway** (launch list, S1) | CE accepted (EEA / Swiss MRA) — not verified here; CANNOT DETERMINE | | |

**The gamepad** in the box (S1) is a second BLE transmitter with its own maker's FCC ID
/ CE DoC; its model is CANNOT DETERMINE (`docs/BOM.md` B16). **The dual charger**
(S4) is a mains or USB device with its own LVD/UKCA/UL obligations: CANNOT DETERMINE
(no specs published).

## 5. Warranty and returns — what Pollen actually offers (the norm to match)

| term | Pollen | source |
|---|---|---|
| commercial warranty | "12 months from the date of delivery" against manufacturing defects; exclusions: misuse, drops, "incorrect assembly", unauthorised modification, wear | S5, S6 |
| statutory (EU consumers) | "legal guarantee of conformity (2 years from delivery …)" and "legal guarantee against hidden defects" (French Consumer Code / Civil Code) | S6 |
| withdrawal | "14 days from the date you receive your order"; "Return shipping is free of charge" with prepaid DHL/FedEx label; unit must be "in working condition" with "all original accessories, cables, and documentation", "original box preferred" | S5 |
| accessory packs | returnable only "unopened and unused" | S5 |
| pre-orders | full refund before dispatch | S5 |
| damage in transit | report "within 15 days of delivery" | S7 |
| law | French law, French courts | S6 |
| age | "recommended for users aged 16 and over" | S6 |

A rebuild sold in the EU inherits the 2-year conformity guarantee whatever its
commercial warranty says; the 12-month figure is Pollen's choice. **Returned units
with a battery** are a used device: USPS forbids used/damaged devices by air (S12
footnote 1) and IATA forbids recalled/damaged batteries by air (S9 D.06) — return
labels must be surface or a DG-approved account (Pollen uses DHL/FedEx labels, S5).

## 6. Packaging

| fact | value | source |
|---|---|---|
| Pollen shipping weights (Shopify `grams`) | robot **1200 g** per colourway; Dev Pack 416 g; Accessory Pack 138 g; Charger Pack 268 g | S1–S4 |
| robot mass | 780 g (store) / "under 800 g" (press kit) / 737.2 g MJCF sum | `SPEC.md` §2 |
| what else is in the robot box | "Robot, battery, USB-C cable, game controller" | S1, `research/01` §2 |
| implied box + gamepad + cable + insert | 1200 − 780 = **420 g** (battery is inside the 780 g? — CANNOT DETERMINE whether 780 g includes the pack; if not, 420 − 99 = 321 g for box + pad + cable) | derived from S1, S15 |
| Charger Pack sanity check | 2 × 99 g packs = 198 g of 268 g → 70 g for charger + carton (plausible only for a small USB charger) | S4, S15 |
| box dimensions, materials, print, insert design | **CANNOT DETERMINE** — nothing published; a delivered unit settles it | — |

Design constraints on our own box, from the rules above: (1) a rigid outer box able to
pass a stacking test (PI 967 II, S10) and, if spares are packed with it, a 1.2 m drop
(PI 966 II); (2) an insert that keeps the pack from making contact, or ships it
unseated (S9 E.08); (3) space on one face for a 100 × 100 mm (min 100 × 70 mm) battery
mark when > 2 boxes or spares are consigned (S9 F.01–F.04); (4) the 16+ age
indication, CE, WEEE bin, Triman/Info-tri, UKCA-or-CE, manufacturer + EU/UK importer
addresses (§3–§4); (5) the ≤ 30 % SoC handling step at pack-out when spares are
boxed with the robot (S9) — which also means the customer's first act is a charge,
so the manual and the charger belong in the box path; (6) PPWR empty-space and
material labelling from 2028 (S34).

## 7. Assembly labour estimate

### 7.1 Method

Boothroyd-Dewhurst manual-assembly time estimation: each part gets a handling time
(grasp 1.5 s one-hand / 4.0 s two-hand or tool, plus symmetry and size penalties) and
an insertion time by operation (snap-fit 1.5–2.5 s, press-fit 2.0–3.0 s, self-tapping
screw with power tool 4.0–6.0 s, machine screw into pre-tapped hole 5.0–8.0 s, bolt +
nut 8–12 s) (S43, secondary tabulation of Boothroyd-Dewhurst). Boothroyd Dewhurst's own
worked example: 11 parts incl. 4 screws + 1 operation = 87.64 s, ideal time per part
2.93 s, default fully-burdened rate $40/h, plant efficiency 85 % (S44). We take the
low end of each range as "trained line worker", the high end as "first-article".

### 7.2 Counts (from this repo)

| item | count | source |
|---|---|---|
| hard printed pieces | 32 across 24 slugs | `docs/BOM.md` §2 |
| soft (TPU) pieces | 4 (2 soles, jaw_soft, soft_mouth_top) | `docs/BOM.md` §3 |
| servos | 15 XL330 | `SPEC.md` §5 |
| screws per servo joint (our model) | 4 × M2x8 body-to-frame + 4 × M2x6 horn-to-link = 8 → **120** for 15 servos; ROBOTIS ships "PHS M2x6 TAP" ×6 and "PHS M2x8 TAP" ×10 with every servo (S42), so the servo screws come in the servo box | S42; task brief "~120 M2 screws" |
| structural screws (community hole count, upper bound) | ~146 structural + 60 on servo bodies = **~206** | `docs/BOM.md` §4 (community, unverified) |
| bearings (press-fit) | 11 × 22×16×4 + 3 × 15×10×3 = 14 | `SPEC.md` §4 |
| Dynamixel 3-pin cable ends | 16 devices on one daisy chain → 15 inter-device cables + 1 lead to the HAT = 16 cables, **32 plug insertions** | `ELECTRONICS-AND-SOFTWARE.md` §3.1 |
| other electronics placements | Radxa, HAT (on 40-pin header), camera board + CSI ribbon, ToF on Stemma J5, `imu_to_dxl`, banana contact PCB, speaker, mic(s), 2 NFC antennas, REC LED ≈ 12 | `ELECTRONICS-AND-SOFTWARE.md` §11 |
| heat-set inserts | 0 or ~60 — CANNOT DETERMINE (community guess) | `docs/BOM.md` §4 |

### 7.3 Arithmetic

| step | low (trained) | high (first-article) | basis |
|---|---|---|---|
| handling, ~77 parts (32+4+15+14+12) | 77 × 1.5 s = 1.9 min | 77 × 4.0 s = 5.1 min | S43 grasp times |
| non-screw insertions (shells, plates, servo drop-in, boards): 63 | 63 × 2.0 s = 2.1 min | 63 × 3.0 s = 3.2 min | S43 press-fit band |
| bearings press-fit: 14 | 14 × 2.0 s = 0.5 min | 14 × 3.0 s = 0.7 min | S43 |
| screws: 120 → 206 | 120 × 5.0 s = **10.0 min** | 206 × 8.0 s = **27.5 min** | S43 machine-screw band (XL330 holes are tapped; printed bosses are self-tapping → 4–6 s, we keep the wider band) |
| heat-set inserts, if used: 0 → 60 | 0 | 60 × 10 s = 10.0 min (our assumption; no DFA figure read) | — |
| cable ends: 32, incl. routing through legs/neck | 32 × 6 s = 3.2 min | 32 × 10 s = 5.3 min | our assumption (S43 has no connector row) |
| harness routing through head_yaw (±170°) and neck, tie-down | 3 min | 8 min | our assumption; routing is CANNOT DETERMINE (`ELECTRONICS-AND-SOFTWARE.md` §12.9) |
| **build touch time** | **20.7 min** | **59.8 min** | |
| ÷ 0.85 plant efficiency | **24.4 min** | **70.4 min** | S44 default |
| servo ID + EEPROM (baud 3, return delay 0, shutdown 52) if not pre-programmed by the supplier: 15 | 15 × 20 s = 5 min | 15 × 45 s = 11 min | `ELECTRONICS-AND-SOFTWARE.md` §3.3; our timing assumption |
| eMMC image, Wi-Fi/BT bring-up, voice-bank seed, functional stand/walk test | 5 min attended | 15 min attended | our assumption (flashing parallelises) |
| SoC set to ≤ 30 % for spares, pack-out, labels | 2 min | 5 min | S9; our assumption |
| **total attended labour per unit** | **≈ 36 min** | **≈ 101 min** | |

### 7.4 Cost of that labour (wage only, rate × time)

| rate basis | rate | 36 min | 101 min | source |
|---|---|---|---|---|
| Shenzhen hourly minimum wage (part-time rate, 2025) | 23.7 CNY/h | 14 CNY | 40 CNY | S46 (Playroll, snippet). China Briefing lists Shenzhen "2,700" CNY/month with a printed effective date "2027.09.01" (as read; looks like a typo — CANNOT DETERMINE) |
| Boothroyd Dewhurst default, North America, fully burdened | $40/h | $24 | $67 | S44 |
| France, SMIC gross hourly | 12.02 € (1 Jan 2026) → 12.31 € (1 Jun 2026) | 7.4 € | 20.7 € | S45 (gross wage only; employer contributions not sourced → CANNOT DETERMINE the burdened rate) |

Pollen's shipping policy says the product "is originated in China" (S7), so the first
row is the one that maps onto Pollen's cost; against a €340 / $399 price the direct
assembly wage is under 1 % in Shenzhen and 6–17 % at the burdened North-American
default. Everything that moves the estimate is a screw count: 120 → 206 screws is
17.5 minutes of the 40-minute spread, and replacing screwed shells with snap-fits
(S44's redesign cut 29 s per 4 screws) is the single largest labour lever.

**What settles the estimate:** (1) the real screw count and lengths — a teardown or
Pollen's screw pack (S2 "1 × Screw Pack") ; (2) whether inserts are used; (3) whether
ROBOTIS ships servos pre-ID'd — `model.rs:84` only says "the XL330 ships at 250"
(return delay), and `bus.rs:128` handles "a servo that has been factory-reset or
swapped in", so per-servo ID and EEPROM writes are a real production step; the
factory ID is CANNOT DETERMINE from our sources (ROBOTIS eManual settles it); (4) a timed build of our own first unit — `bin/deliver`'s construction manual
is the checklist to time it against.

## 8. What Pollen's packs contain (verbatim from the store, S2–S4, fetched 2026-09-01)

| pack | price | shipping weight | contents (verbatim list items) |
|---|---|---|---|
| Charger Pack | €33.00 (store JSON) / $39 | 268.13 g | "2 × Batteries"; "1 × Dual Battery Charger, charge two batteries simultaneously" |
| Dev Pack | €99.99 / $119 | 416.46 g | "3 × Motors"; "5 × Motor Cables"; "2 × Batteries"; "1 × Dual Battery Charger"; "10 × NFC Tags"; "Hugging Face Credit"; "1 × Screwdriver"; "1 × Screw Pack, a set of spare screws" |
| Accessory Pack (Orange / Yellow) | €33.00 / $39 | 138.12 g | "2 × Rollers … orange for Cream and Sky, and yellow for Graphite and Lavender"; "1 × Laser"; "1 × NFC Polaroid, a 1.54-inch color NFC-powered E-Ink display"; "10 × NFC Tags"; "1 × Ball" |
| Robot | €340.00 / $399 | 1200 g | "Robot, battery, USB-C cable, game controller" (S1 body text via `research/01` §2); "Available at launch in US/Canada/EU/UK/Norway/Switzeland/Japan and South Korea" |

Dev Pack arithmetic: 3 × 18 g motors + 2 × 99 g packs = 252 g of 416 g → 164 g for
charger, cables, screws, screwdriver, tags, carton (S42 weight, S15). The Dev Pack's
"3 × Motors" at ROBOTIS's US list price of **$27.49** each (S42) is $82 of the $119 —
the first published XL330 price in this repo; `docs/BOM.md` §5 should pick it up
(15 × $27.49 = $412 at list, before any volume discount).

## 9. CANNOT DETERMINE — the list, with what settles each

1. Pollen's actual certifications (CE DoC, FCC ID or SDoC for the robot, UKCA, Giteki, KC, PSE) — no compliance page exists on pollen-robotics.com or the store (searched 2026-09-02); a delivered unit's label and manual settle it.
2. Which packing instruction Pollen ships under and at what SoC — the carrier label on a delivered box.
3. NP-F550 supplier and its UN 38.3 test summary — the pack label.
4. Whether the robot's 780 g includes the pack — a scale.
5. Box dimensions, materials, insert, whether the pack ships seated — a delivered unit.
6. Gamepad model and its radio approvals — a delivered unit.
7. Dual charger specs and safety approvals — a delivered unit.
8. Currently OJ-cited edition of EN (IEC) 62368-1 and the RED ETSI list — the EC summary list PDFs (S24, S25) or OJ L.
9. Machinery Regulation applicability to a 16+ consumer biped — legal opinion.
10. Toy Directive: whether market surveillance would treat a duck-shaped robot marked 16+ as a toy — legal opinion; the 16+ marking on pack and listing is the mitigation.
11. Japan PSE applicability to an NP-F pack inside/with a robot — METI scope note.
12. Radxa Zero 3W 5 GHz operation vs its 2.4 GHz-only FCC grant — the grant exhibits (fccid.io lists 15C only).
13. Heat-set inserts, real screw count and lengths — teardown / Pollen screw pack.
14. Whether servos arrive pre-configured — Pollen/ROBOTIS purchasing terms.
15. Burdened labour rate in France (employer contributions) and the Shenzhen average assembler wage — payroll sources not fetched.
16. Mondial Relay battery terms; ADR SP 188 primary text; FedEx lithium pages (both FedEx URLs returned errors on 2026-09-02).
