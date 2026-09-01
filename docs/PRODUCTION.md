# PRODUCTION — what it costs and what it takes to build a Microduck at 1 / 10 / 100 / 1,000 units

*Synthesised 2026-09-02 from three research lenses written the same night —
`production/components.md` (bought parts, vendor pages read 2026-09-02),
`production/process.md` (print vs mould, web sources read 2026-09-02) and
`production/compliance-and-assembly.md` (battery shipping, CE/FCC, packaging,
labour; read 2026-09-02, Pollen store JSON 2026-09-01). Nothing was built,
sliced or quoted; this machine was under load and only the web was used.
Every number below carries a source ID; the ID → URL → date-read table is §8.
A number no source stated is **CANNOT DETERMINE** with what settles it.
Reference price: Pollen sells the assembled robot with gamepad, battery and
USB-C cable for **$399 / €340** [S1].*

## 0. The one-paragraph answer

Bought parts whose price was actually read come to **$472–481 per robot in
USD** (plus ≈ NZD 65 of bearings and ≈ €8.5 of screws) at every quantity from
1 to 1,000, because the only line with real weight — 15 × Dynamixel
XL330-M288-T at $23.90 = **$358.50, 75 % of the total** — has no published
volume tier anywhere [C1][C2]. That subtotal already exceeds Pollen's $399
retail before the Radxa board, speaker, mics, NFC, three custom PCBs, filament,
assembly, packaging, certification or margin. So the whole volume question for
this robot reduces to one quote (ROBOTIS OEM pricing for XL330 at 1,500 and
15,000 units) and one process decision (mould the 9 visible shells at 1,000
units, keep the 22 small brackets printed). Assembly is 36–101 minutes of
attended labour per unit by a Boothroyd-Dewhurst count, i.e. 14–40 CNY at
the Shenzhen minimum wage or $24–67 at a burdened North-American rate
[S43][S44][S46]. Pollen's own manufacturing is at Seeed Studio in Shenzhen
against a > 20,000-unit target [BB]; its only word about process is "printed"
[PK].

## 1. Executive table — cost per robot at 1 / 10 / 100 / 1,000

Rules: a cell is a number only where every input was read from a source; a
bracket "[a–b]" is arithmetic on sourced rates and our own solid volumes or
counts, not a quote; "CD" = CANNOT DETERMINE, with the settling step in §5.
Currencies are the vendor's; no FX rate was fetched.

| line | 1 robot | 10 robots | 100 robots | 1,000 robots | what is in it / what settles the CD |
|---|---|---|---|---|---|
| **Bought, exact parts read (USD)** [C-roll] | **$481.21** | **$477.35** | **$472.64** | **$472.48** | XL330 ×15 $358.50 (no tiers) [C1]; X3P cables ×16 $24.80 [C3]; NP-F550 + charger share $24.95 [C5]; IMX219 B0183 + 75° lens $23.99 (sale price) [C7]; ToF breakout Pololu #3419 $24.95 → $19.43 @100+ [C10]; TLV320AIC3104 LCSC $2.25 → $1.23 @1000 [C13]; MR6700 bearings ×3 $14.58 → $12.39 [C17]; M2 inserts ×60 $7.19 [C20] |
| Bought, native-currency lines read | NZD 64.90 + GST; €8.46 | same | same | bearings: US$11–44 (factory, MOQ 1,000 pcs) [C16]; €8.46 | 22×16×4 MR1622-ZZ ×11 at NZD 5.90 [C15]; 195 M2 screws priced as M2×6 at €4.34/100 [C19] |
| Bought, bracket / substitute only (kept out of the subtotal) | $23–51 Radxa; $9.78 speaker | $23–51; $7.52 | $23–51; $6.08 | $23–51; $4.98 | Radxa: the 1 GB/32 GB SKU **does not exist** in Radxa's SKU table; nearest 1 GB/8 GB $23 or 4 GB/32 GB $51, all sold out 2026-09-02 [C4]. Speaker: nearest catalogued 2 W 39×20 part SPM-2035NU, not the 35×25 mesh [C14] |
| Bought, unpriced | CD | CD | CD | CD | Radxa (see above); CSI flex; mic(s); NFC IC + 2 antennas; REC LED; gamepad; USB-C cable; PCBs P1 Robot HAT / P2 `imu_to_dxl` / P3 banana (no design files exist — must be designed); LSM6DSV16X, BMI088, transceiver, MCU; filament [C-13] |
| **Printed hard parts** (24 slugs, 31 pieces, ≈ 198 cm³ solid) [PR-2] | FDM in-house: material ≤ $6.5 [PR-3]; machine h × $0.10–0.31 [LM1][CC]; labour ≤ $155 if 31 pieces are handled one at a time (15 min @ $20 each) [CC]; **hours CD (not sliced)** | same per robot; one printer | FDM farm: $2–4 per print-hour [LM2][PR2] × Σh **CD**; ≈ 41 printer-days per 100 robots at 76 parts/printer-day [PR2]; MJF floor ≈ €57 grey / €83 smoothed per robot on solid volume [HP] | mould the 9 visible parts: tooling $13,455 (Protolabs floor) – $90,000 (aluminium bracket) → **$13–90 per robot** + moulded parts $4.50–45 [PL1][HT]; 22 brackets stay FDM (hours CD) | grams and hours per piece need `cad-print` / ce-slice on the rebuilt parts; quotes need the STEP export (GOAL rung 6) |
| **Soft parts** (4 pieces, ≈ 34 cm³) [PR-2] | FDM TPU material ≤ $2 [LM3] | same | MJF TPU 90A ≈ €20 per robot [HP]; urethane casting 20–30 pulls per $500–3,000 mould [ML] is worse than printing | TPU injection: 3–4 tools ≥ $4,485 → ≥ $4.50 per robot + parts [PL1] | durometer and material of Pollen's lips CD |
| **Assembly labour** (36–101 min attended) [K-7] | 14–40 CNY @ Shenzhen 23.7 CNY/h [S46]; $24–67 @ $40/h burdened [S44]; €7.4–20.7 @ SMIC gross [S45] | same | same | same | no learning-curve source was read; the 120 → 206 screw count is 17.5 min of the spread; heat-set inserts (0 or 60) another 10 min |
| **Servo ID / EEPROM + image + test** | 10–26 min inside the 36–101 above [K-7] | same | same | same | whether ROBOTIS ships servos pre-ID'd is CD (`model.rs:84`, `bus.rs:128` say the runtime corrects them) |
| **Packaging** | CD | CD | CD | CD | no box price read; constraints known (§3.3): rigid box passing stacking (PI 967 II) and 1.2 m drop if spares packed (PI 966 II) [S9][S10]; insert must prevent activation — the robot has no power switch [S9 E.08]; Pollen ships 1,200 g per robot box [S1] |
| **Certification / test lab** | CD | CD | CD | CD | no lab quote read; obligations in §3 |
| **Total** | **CD** — floor **≥ $481 + NZD 65 + €8.5 + material + labour** before any unpriced line | CD | CD | CD | the floor already exceeds $399 [S1]; the gap is the ROBOTIS OEM price |

Reading across: between 1 and 1,000 robots every *read* bought line together
moves by less than $9 [C-roll]; the material bound on the printed set is
≤ $8.5 per robot; the visible-part moulding decision adds $13–90 per robot of
tooling at 1,000 units and removes an unknown number of print-hours. Nothing
read makes a 1,000-unit robot cheaper than a 1-unit robot by more than about
$10 unless the servo price moves.

## 2. Make / buy and print / mould

### 2.1 Buy list — one vendor per line, with the volume signal each publishes

| line | qty | buy from (cheapest read, 2026-09-02) | @1 | volume signal | lead / stock read |
|---|---|---|---|---|---|
| XL330-M288-T | 15 | ROBOTIS intl [C1] | $23.90 (US $27.49 [C2]; Generation Robots €33.50 ex VAT, 373 in stock [C1b]) | **none** — no bulk pack, no tier; ROBOTIS's only published bulk discount is −9.9 % at 6 pcs on AX-12A [C1c] | 10 days (intl list page); 24–48 h EU [C1b]. M077-T is the same price (40 days) |
| X3P cable 180 mm | 16 | ROBOTIS intl, 10-pack $15.50 [C3] | $1.55 each | none | 3 working days |
| Radxa Zero 3W | 1 | ALLNET China [C4] | $22–23 (1 GB/8 GB), $50–51 (4 GB/32 GB) | none; Radxa sells only through partners [C4b] | all 1 GB SKUs sold out at ALLNET, Arace, ameriDroid; OKdo and RS pages unreadable |
| NP-F550 2600 mAh + dual charger | 1 + charger | NextBatteries 2-pack + dual charger $49.90 [C5] | $24.95 per pack incl. charger share (Pollen sells the same bundle at €33 / $39 [S4]) | none; OEM pack (Alibaba) unreadable | in stock. Cells inside: Samsung 26J $4.99, sold out at two shops [C6] |
| IMX219 + M12 lens | 1 | UCTRONICS B0183 [C7] | $23.99 sale (regular $39.99); Seeed bare M12 board $15.90 → $12.50 @10+, no lens [C8] | Seeed 10+ tier only | not stated |
| M12 lens (if the FOV lands off 75°) | 0–1 | UCTRONICS [C9] | $7.99–11.99 | none | — |
| ToF 8×8 | 1 | Pololu #3419 VL53L8CX carrier [C10] at ≤ 10 robots; bare VL53L8CXV0GC/1 on the HAT at ≥ 100 [C11] | $24.95 → $19.43 @100+; chip $8.77 → $6.72 @100 → $6.06 @1000 | DigiKey full tier table | chip: 6,174 in stock, 22-week factory lead; SATEL breakouts 13–51 weeks [C12] |
| TLV320AIC3104IRHBR | 1 | LCSC [C13] | $2.25 → $1.39 @100 → $1.23 @1000 | full tier table | 420 in stock; DigiKey 64 in stock, 16-week lead |
| bearing 22×16×4 = MR1622-ZZ (alias ET2216ZZ; not a 6700-family size) | 11 | NZ Miniature Bearings [C15] | NZD 5.90 + GST | factory: US$1–4 at MOQ 1,000 [C16] | in stock |
| bearing 15×10×3 = MR6700 open (6700ZZ is 10×15×**4**) | 3 | Bearings Direct [C17] | $4.86 → $4.13 @50+ | 5/10/15 % breaks | 722 in stock; true width CD until measured |
| M2 socket screws | ~195 | RST-Versand M2×6 A2 DIN 912 [C19] | €0.06 → €0.0434 @100 | no > 100 tier read anywhere | 1–2 days |
| M2 heat-set inserts | 0–60 | Prusa / CNC Kitchen / Vector3D [C20] | $0.12 / €0.099 / £0.097 | none | in stock |
| speaker 35×25×7 | 1 | CD — exact size only as a sold-out INR listing [C14] | — | — | — |
| mics, NFC IC + antennas, REC LED, gamepad, USB-C, CSI flex | — | CD [C-13] | — | — | — |
| PCBs P1 / P2 / P3 | 3 | **make** — no design files exist; must be designed (GOAL rung 4) before a fab quote | CD | — | — |

Decisions that follow from the tiers alone: put the ToF chip on the HAT at
≥ 100 robots (saves $13–19 per robot [C10][C11]); buy the codec from LCSC
(45 % under DigiKey at qty 1, 36 % at 100 [C13]); treat the Radxa "1 GB / 32
GB" as an open question before ordering anything (§5 #4); order servos from
ROBOTIS intl unless EU stock speed matters [C1][C1b].

### 2.2 Print or mould — the 24 hard slugs and 4 soft pieces

What has to be made [PR-2]: 3 colourway shells (52.7 cm³), 6 trim parts in
orange/yellow (73.3 cm³), 22 grey internal brackets and plates (72.0 cm³);
plus soles ×2, jaw-soft, soft-mouth-top (33.8 cm³). Largest part 91.6 × 122.7
× 46.3 mm; thinnest 1 mm (rigidity plate) — marginal at MJF/SLS's 1 mm minimum
wall [JC2]. The meshes are drawn for printing: 1 mm plates, 2 mm walls,
printed-style bosses, bearing seats, M2 counterbores (SPEC §6); a moulded
version needs draft, uniform walls and side-actions for the bearing bores and
the dome's undercuts — a redesign, not a re-quote [PL4].

| units | decision | why (sources) |
|---|---|---|
| 1 | **FDM in-house**, PLA-class hard parts, TPU soft parts | material ≤ $8.5 total [LM3][PR-3]; a bureau charges $3–10 setup per part → $93–310 for 31 pieces [3DP]; 24 moulds ≥ $35,880 [PL1] |
| 10 | **FDM in-house**, batch-plated; cast the lips in silicone only if 90A TPU fails the beak test ($37 Mold Star kit, 20–30 pulls) [SO][ML] | tooling would be $3,588+ per robot [PL1] |
| 100 | **FDM farm** (own printers or a no-MOQ farm such as Slant 3D at PLA $10/kg [SL]); mould nothing; MJF TPU ≈ €20/robot [HP] is the soft-part alternative | 100 robots = 3,100 pieces ≈ 41 printer-days at PR2's 76 parts/printer-day; break-even for simple small parts "~200 units" [HT] not yet reached; urethane needs 14–20 moulds per 100 robots [ML] |
| 1,000 | **Mould the 9 visible parts** (3 shells, dome, bottom-head-shell, jaw, ankles, feet) after a DFM redesign; **keep the 22 small grey brackets FDM**; soft parts → TPU mould or MJF TPU on quote | 9 tools $13,455–90,000 = $13–90/robot + $4.50–45 parts [PL1][HT]; 17 mm parts break even at "2,000 units" [XM1] so the brackets stay printed; MJF at ≈ €57,000 floor is the dearest route [HP] |

**Break-even.** N* = T / (c_print − c_mould) with sourced brackets: c_mould
$0.50–5 per piece plus $1,495–10,000 per tool [HT][PL1][XM2]; c_print $3.45
(17 mm MJF knob) to $8–25 (100 g bureau FDM part) [XM1][3DP]. The sources'
own answers: "between 200 and 1,000 units" [HT]; 250 units for a 147 mm part
and 2,000 units for a 17 mm part [XM1]. Our 91–123 mm shells sit at the
250-unit end; the 22 brackets at the 2,000-unit end. Colour: FDM = spool
colour (4 shell + 2 trim spools); MJF = grey/black native, pastel Cream /
Lavender / Sky only via white PA12-W + dye, price CD [XM3][SS]; moulding =
coloured resin, per-colour MOQ CD.

**Calibration from Pollen's own history.** Reachy Mini was announced as "a
3D-printed prototype" and moved "from prototyping to industrial production"
with Seeed after "over 3,000 orders within a week" [SEED]; a reseller page
says its structural parts are "injection molded" [OEL]. Microduck took
5,000 orders in 24 h [AX] against a > 20,000 target [BB] — past every
break-even above for its large parts. Whether "printed" [PK] survives the run:
CD until a shipped shell is examined for layer lines vs gate/ejector marks.

## 3. Compliance checklist

Trigger facts: the Radxa Zero 3W carries Wi-Fi 6 / BT 5.4 [S19], so the robot
is radio equipment; the pack is a 7.2 V × 2.6 Ah = **18.72 Wh** 2S Li-ion
(≤ 20 Wh per cell, ≤ 100 Wh per battery → "small" in every regime) [S15][S9];
Pollen's terms say "recommended for users aged 16 and over" [S6].

### 3.1 Battery shipping (ICAO/IATA 2026, DHL, 49 CFR, USPS, Colissimo)

| configuration | classification | rule read | source |
|---|---|---|---|
| robot box, pack installed | **UN 3481, PI 967 Section II** | ≤ 30 % SoC *recommended*, not mandatory; ≤ 2 packages with ≤ 2 batteries in equipment each need **no mark and no statement**; 5 kg net per package | S9 p.14, F.04; S10 |
| robot + spare packs in one box | **UN 3481, PI 966 Section II** | **≤ 30 % SoC mandatory** (> 2.7 Wh); robot + 2 spare sets max; 1.2 m drop + stacking test; mark + statement; DHL account approval | S9 p.14; S10 |
| Charger Pack / Dev Pack alone (batteries + charger) | **UN 3480, PI 965 Section IB** | Cargo Aircraft Only, Shipper's Declaration, Class 9 + CAO labels; ≤ 30 % SoC | S9 D.05 p.23; S10 |
| US ground | 49 CFR 173.185 | 20 Wh / 100 Wh caps; UN 38.3 + test summary; mark exempt for ≤ 2 packages of ≤ 2 batteries in equipment | S11 |
| USPS domestic / international | Pub 52 §349 / IMM §135.64 | domestic: mailable, UN 3481 mark unless ≤ 2 batteries installed; international: **installed only**, spares prohibited, no lithium markings on the mailpiece | S12; S13 |
| Colissimo (France + Europe) | PI 967 II | ≤ 2 power packs per parcel, 5 kg; "air shipments outside Europe are prohibited" | S14 |
| ADR road (EU) | SP 188 | exempt from full ADR; Wh on case; 100 × 100 mm mark | S41 (snippet) |
| all regimes | UN 38.3 test summary from the pack maker; Wh printed on the pack; package "prevents unintentional activation" — **the robot has no power switch**, so the insert must isolate the contacts or the pack ships unseated | S9 p.8, E.08; S12 §349.241 |

### 3.2 Product compliance by market

| market / rule | applies | requirement read | source |
|---|---|---|---|
| EU RED 2014/53/EU | yes | DoC, CE mark, technical file; own RED assessment — the Radxa module's CE status does not transfer to the host; current ETSI list CD (EC summary PDF settles) | S22; S24 |
| EU RED cybersecurity (Del. Reg. 2022/30, in application Aug 2025) | yes — WebRTC streaming and BLE pairing | EN 18031-1/-2:2024; presumption withheld where the user may skip a password — the default PIN `000000` is the test point | S22; S23 |
| EU safety (LVD / RED 3(1)(a)) | yes | EN 62368-1 family; OJ-cited edition CD (2014 listed; 2020 3rd ed. status unresolved); 15 servo pinch points assessed as mechanical hazards | S25; S26 |
| EU EMC (RED 3(1)(b)) | yes | EN 55032/55035 class B typical — citation not verified | S22 |
| EU Toy Safety 2009/48/EC → Reg. 2025/2509 (applies 1 Aug 2030) | **no, if 16+ holds** — scope is play by children under 14; "whether or not exclusively" invites a market-surveillance argument, so the 16+ mark must be on pack and listing before purchase | S27 Art. 2(1), 11(2); S28; S29 |
| EU Batteries Reg. 2023/1542 | yes (portable battery) | CE on batteries from 18 Aug 2024; labelling from 18 Aug 2026; end-user removability from 18 Feb 2027 — the removable NP-F550 passes by design; producer registration from 18 Aug 2025 | S30; S31 |
| EU RoHS / WEEE | yes | supplier declarations per PCB, servo, cable, pigment; crossed-out bin on product; producer registration per member state | S38 |
| EU GPSR 2023/988 (from 13 Dec 2024) | yes | EU responsible person; manufacturer name + postal + e-address on the listing | S35 |
| EU Machinery (2006/42/EC → Reg. 2023/1230 from 20 Jan 2027) | **CD** — Art. 1(2)(k) exclusions do not obviously cover a walking robot | legal / notified-body opinion settles | S36 |
| EU PPWR 2025/40 | from 12 Aug 2026 | empty-space ratio 2028/2030; material label by 12 Aug 2028 | S34 |
| EU common charger 2022/2380 | not listed (robots absent from the category list) | already USB-C 5 V | S47 |
| France Triman + Info-tri | yes | on product or packaging | S37 (snippet) |
| **US FCC** | yes | Radxa holds FCC ID **2BC6T-RADXAZERO3W**, Single Modular Approval, Part 15C, **2.4 GHz only — no 5 GHz grant listed**; host still needs Part 15B SDoC and testing with the transmitter operating; no US safety mark legally required | S18; S20; S21 |
| **UK** | yes | CE recognised alongside UKCA (page updated 21 Aug 2026); whether 31 Dec 2027 bounds this for radio equipment CD; UK importer address required | S32; S33 |
| **Japan** | yes (launch market) | Giteki mark; PSE for Li cells ≥ 400 Wh/L — a 2600 mAh 18650 ≈ 570 Wh/L is above it; applicability to a pack sold with a robot CD | S39; S40 (snippets) |
| **South Korea** | yes (launch market) | KC EMC/radio; KC 62133 for the pack typical, not verified | S40 (snippet) |
| gamepad in the box | second BLE transmitter with its own maker's approvals; model CD | — | S1 |
| dual charger | mains/USB device with its own LVD/UKCA/UL obligations; specs CD | — | S4 |

### 3.3 Packaging and warranty facts to match

Pollen ships 1,200 g per robot box (robot 780 g → ≈ 420 g of box, gamepad,
cable, insert; whether 780 g includes the 99 g pack is CD) [S1][S15];
Charger Pack 268 g; Dev Pack 416 g [S2][S4]. Box dimensions, materials and
insert: CD (a delivered unit). Warranty norm: 12 months commercial [S5][S6]
under the EU 2-year statutory conformity guarantee; 14-day withdrawal with a
free DHL/FedEx return label [S5] — a returned unit is a used battery device,
surface or DG-approved account only [S12][S9 D.06].

## 4. Assembly labour — the count behind the 36–101 minutes

Boothroyd-Dewhurst handling + insertion times [S43][S44] over this repo's
counts: 31 hard + 4 soft printed pieces, 15 servos, 14 press-fit bearings,
≈ 12 electronics placements, 120 servo screws (ROBOTIS ships 6 × M2×6 and
10 × M2×8 with every XL330 [S42]) rising to ≈ 206 with the community's
structural-hole count, 32 Dynamixel plug insertions, 0–60 heat-set inserts
[K-7]. Build touch time 20.7–59.8 min, ÷ 0.85 plant efficiency = 24.4–70.4
min; plus servo ID/EEPROM 5–11 min, eMMC image + bring-up + walk test 5–15
min, SoC-set and pack-out 2–5 min → **≈ 36–101 min attended per unit**
[K-7]. The largest lever is the screw count (17.5 min of the spread);
snap-fit shells were the single biggest saving in Boothroyd Dewhurst's own
example (29 s per 4 screws) [S44]. Every "our assumption" row in the lens
(cable ends, harness routing, inserts) is labelled as such there.

## 5. Top 10 unknowns — and what settles each

| # | unknown | weight | settles it |
|---|---|---|---|
| 1 | **XL330-M288-T price at 150 / 1,500 / 15,000 pcs** — no tier, no bulk pack, OEM pricing not public | 75 % of read bought cost; the only line that can move the total | written quote from ROBOTIS: america@robotis.com (+1 949-377-0377) / contactus2@robotis.com [C1c] |
| 2 | **Grams and hours per printed piece** | decides in-house vs farm cost and whether FDM survives at 1,000 | slice the 24 rebuilt parts with `cad-print` / ce-slice (no slicer output in `out/` on 2026-09-02) |
| 3 | **Quotes on our geometry** for FDM bureau, MJF, moulding | turns every [bracket] in §2.2 into a price | upload the STEP set from GOAL rung 6 to JLC3DP / Xometry / Protolabs |
| 4 | **Radxa Zero 3W "1 GB / 32 GB"** — not in Radxa's SKU table; all 1 GB SKUs sold out | compute board price and lead time | `lsblk` on a production unit or Pollen's answer; Radxa OEM quote via a partner [C4] |
| 5 | **Custom PCBs P1 / P2 / P3** and their remaining chips (LSM6DSV16X, BMI088, transceiver, MCU) | three unpriced lines; the HAT decides ToF-on-board ($6 vs $19–25) | design them (GOAL rung 4) → fab + assembly quote |
| 6 | **Whether Pollen's production shells are moulded** | the calibration for our 1,000-unit decision | a shipped shell (layer lines vs gate marks) or a Seeed/Pollen statement; the Seeed blog was 403 [SEED] |
| 7 | **Real screw count, lengths, inserts** | 17.5 + 10 min of labour spread; the fastener line | teardown or the Dev Pack "Screw Pack" [S2]; a timed build of our first unit against `bin/deliver`'s manual |
| 8 | **Pollen's certifications, packing instruction and ship SoC** | which of §3 Pollen actually does | the label and manual of a delivered unit; the carrier label on the box |
| 9 | **Pastel colour on MJF; moulded-in-colour MOQ** | whether Cream / Lavender / Sky are reachable off FDM | a PA12-W + dye quote; the moulder's colour-change terms |
| 10 | **Machinery Regulation and Toy Directive applicability** to a 16+ duck-shaped biped | scope of the CE file | notified-body or legal opinion; the 16+ marking is the mitigation meanwhile |

Also open (full lists: `components.md` §15, `process.md` §9,
`compliance-and-assembly.md` §9): speaker part number; 15×10×3 bearing true
width; 22×16×4 USD price at 11–1,100 pcs; M2 screws above 100 pcs; NP-F550
brand and its UN 38.3 summary; standalone charger price; servo supply voltage
vs the 6.0 V datasheet; XL330 sub-variant (same price either way); burdened
labour rates; Radxa 5 GHz vs its 2.4 GHz-only FCC grant; the retry list of
blocked vendor URLs (RobotShop, OKdo, RS, arducam.com, Mouser, TI, B&H, NKON,
McMaster, Bolt Depot, Accu, Misumi, Boca, 123Bearing).

## 6. What Pollen does (as far as it is published)

| fact | verbatim / value | source |
|---|---|---|
| process word | "Four printed colourways - Cream, Graphite, Lavender and Sky. Same robot underneath." | PK |
| openness | firmware and software open; "do not describe the robot as open-source hardware" | PK (SPEC §1) |
| manufacturer | "The robot is manufactured in China with Shenzhen-based open-source hardware provider Seeed Studio." | BB (2026-08-27, via Yahoo Finance mirror) |
| volume | "aiming to sell more than 20,000 Microducks, with the first shipments expected before Christmas"; Delangue: "50,000 would be a great success" | BB; AX (via gagadget / resellcalendar) |
| demand | "more than $2.6 million in orders in its first 24 hours … more than 5,000 units" | AX via resellcalendar (2026-08-29) |
| ramp | "We can't promise Christmas delivery for new microduck orders anymore, but we're ramping up production." | ST (2026-09-01) |
| price and box | $399 / €340; "Robot, battery, USB-C cable, game controller"; shipping weight 1,200 g; launch markets US/Canada/EU/UK/Norway/Switzerland/Japan/South Korea | S1 |
| accessories | Charger Pack €33 / $39 (2 packs + dual charger, 268 g); Dev Pack €99.99 / $119 (3 motors, 5 cables, 2 packs, charger, 10 NFC tags, HF credit, screwdriver, screw pack, 416 g); Accessory Pack €33 / $39 | S2; S3; S4 |
| servo price signal | 3 motors in the $119 Dev Pack at ROBOTIS US list $27.49 = $82 of $119 | S42; S2 |
| battery bundle signal | Pollen's 2 packs + charger at $39 vs NextBatteries' same bundle at $49.90 | S4; C5 |
| origin / logistics | product "is originated in China"; US orders ship from the US; carriers include DHL, FedEx, Colissimo, Mondial Relay | S7 |
| warranty / age | 12 months; 14-day withdrawal with free return label; "recommended for users aged 16 and over"; French law | S5; S6 |
| precedent | Reachy Mini: "3D-printed prototype" → "industrial production" with Seeed after "over 3,000 orders within a week"; "more than 10,000 units" sold | SEED (snippet); OEL; TNW |

Nothing on pollen-robotics.com or the store names a certification, a packing
instruction, a box, a mould, or a supplier other than Seeed (searched
2026-09-02 [K-9]).

## 7. How this document was made, and what would change it

Three agents fetched vendor and regulator pages between 2026-09-01 23:00 and
2026-09-02 01:00 (+0800) and wrote the lens files under `docs/production/`;
this file only re-arranges their sourced figures into the 1/10/100/1,000
frame and takes the decisions in §2. Two arithmetic corrections were made on
the way: the hard-part solid volume re-sums to ≈ 198 cm³ (BOM.md prints ≈ 183;
its own rows sum to 199.06 with the 1.10 cm³ lens holder, 197.96 without),
and the compliance lens counted 32 hard pieces where BOM.md and the process
lens count 31 — the difference does not move any figure above by more than
15 s of labour. Re-run when: a ROBOTIS quote arrives (§5 #1), the parts are
sliced (#2), or a production unit is on the bench (#4, #6, #7, #8).

## 8. Sources — ID → URL → date read

Component vendors (all read 2026-09-02; full tables in `production/components.md`):

| ID | URL |
|---|---|
| C1 | https://en.robotis.com/shop_en/item.php?it_id=902-0163-000 ; list page https://en.robotis.com/shop_en/list.php?ca_id=202030 |
| C1b | https://www.generationrobots.com/en/403817-dynamixel-xl330-m288-t-servo-motor.html |
| C1c | https://www.robotis.us/bulk-pack/ ; https://www.robotis.us/dynamixel-ax-12a/ ; https://www.robotis.us/dynamixel-ax-12a-6pcs-bulk/ ; https://www.robotis.us/contact-us/ |
| C2 | https://www.robotis.us/dynamixel-xl330-m288-t/ |
| C3 | https://en.robotis.com/shop_en/item.php?it_id=903-0251-000 |
| C4 | https://shop.allnetchina.cn/products/copy-of-radxa-zero-3w ; https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_product_brief.pdf ; https://arace.tech/products/radxa-zero-3w ; https://ameridroid.com/products/radxa-zero-3w |
| C4b | https://radxa.com/products/zeros/zero3w/ |
| C5 | https://www.nextbatteries.com/products/sony-np-f550-battery-2-pack-2600mah-l-series-dual-charger |
| C6 | https://imrbatteries.com/products/samsung-26j-18650-2600mah-5-2a-battery ; https://www.18650batterystore.com/products/samsung-26jm |
| C7 | https://www.uctronics.com/camera-modules/camera-for-nvidia/arducam-8-mp-sony-imx219-m12-mount-low-distortion-camera-module-for-nvidia-jetson-nano.html |
| C8 | https://www.seeedstudio.com/IMX-219-CMOS-camera-module-M12-and-CS-camera-available-p-5372.html |
| C9 | https://www.uctronics.com/lens/m12-mount-lens.html?product_list_mode=list |
| C10 | https://www.pololu.com/product/3419 |
| C11 | https://www.digikey.com/en/products/detail/stmicroelectronics/VL53L8CXV0GC-1/18085238 |
| C12 | https://www.digikey.com/en/products/detail/stmicroelectronics/VL53L5CX-SATEL/14552430 ; https://www.digikey.com/en/products/detail/stmicroelectronics/SATEL-VL53L8/18110499 |
| C13 | https://lcsc.com/product-detail/Audio-OpAmps_TI_TLV320AIC3104IRHBR_TLV320AIC3104IRHBR_C181753.html ; https://www.digikey.com/en/products/detail/texas-instruments/TLV320AIC3104IRHBR/1906853 |
| C14 | https://www.digikey.com/en/products/detail/soberton-inc/SPM-2035NU/10638200 ; https://www.thingbits.net/products/3525-waterproof-8-ohm-2w-cavity-speaker |
| C15 | https://nzminiaturebearings.com/product/16x22x4-mm-mr1622-zz-bearing-sku-00206030.html |
| C16 | https://jiangxin2020.en.made-in-china.com/product/IvxJnUDERBpq/China-Stainless-Steel-Ball-Bearing-16-22-4-Et2216-Set2216-A2216-MR1622-Zz.html |
| C17 | https://bearingsdirect.com/6700-ball-bearing-10x15x3-open-mr6700/ |
| C19 | https://www.rst-versand.de/Zylinderschraube-Innensechskant-M2-x-6-mm-A2-DIN912_1 |
| C20 | https://www.prusa3d.com/product/heat-set-inserts-m2-short-100-pcs/ ; https://cnckitchen.store/products/heat-set-insert-m2-x-3-100-pieces ; https://vector3d.shop/products/heat-set-insert-m2-standard |
| C-roll | `production/components.md` §14 (roll-up rules: cheapest read vendor; no tier → @1 price kept as ceiling) |
| C-13 | `production/components.md` §13 (lines not researched) |

Process (read 2026-09-02 unless marked; full table in `production/process.md` §0):

| ID | URL |
|---|---|
| PK | https://pollen-robotics.com/microduck/press-kit/ (2026-09-01) |
| ST | https://store.pollen-robotics.com/products/microduck (2026-09-01) |
| BB | https://www.bloomberg.com/news/articles/2026-08-27/hugging-face-unveils-400-singing-skating-duck-like-robot via https://finance.yahoo.com/technology/ai/articles/hugging-face-unveils-400-singing-121456627.html |
| AX | https://www.axios.com/2026/08/27/hugging-face-debuts-microduck-a-399-robot (403) via https://gagadget.com/en/723594-hugging-faces-399-microduck-is-a-tiny-open-source-robot-you-can-actually-train/ and https://resellcalendar.com/news/news/pollen-robotics-microduck-preorder-sold-out-reseller/ |
| TNW | https://thenextweb.com/news/hugging-face-microduck-399-open-source-robot |
| SEED | https://www.seeedstudio.com/blog/2026/01/06/reachy-mini-an-open-journey-built-together-with-hugging-face-pollen-robotics-seeed-studio/ (403; search snippet only) |
| OEL | https://openelab.io/blogs/learn/seeed-studio-hugging-face-reachy-mini-your-gateway-to-open-source-humanoid-robotics |
| LM1 | https://layermath.com/blog/how-to-run-a-3d-print-farm |
| LM2 | https://layermath.com/blog/3d-printing-hourly-rate |
| LM3 | https://layermath.com/filament-prices |
| PR2 | https://pro.prusa3d.com/guides/how-to-build-a-3d-printing-farm/ |
| CC | https://3dprintingcostcalculator.com/news/3d-printing-cost-formula |
| 3DP | https://3dprinting.com/how-much-does-3d-printing-cost/ |
| SL | https://www.slant3d.com/ |
| PL1 | https://www.protolabs.com/services/injection-molding/ |
| PL4 | https://www.protolabs.com/en-gb/resources/design-tips/comparing-cost-between-injection-moulding-and-3d-printing/ |
| XM1 | https://www.xometry.com/resources/injection-molding/injection-molding-vs-3d-printing/ |
| XM2 | https://www.xometry.com/resources/injection-molding/injection-molding-cost/ |
| XM3 | https://www.xometry.com/resources/materials/mjf-materials/ |
| JC2 | https://jlc3dp.com/help/article/pa12-hp-nylon |
| HP | https://hp3dprint.eu/3d-materials-finishes-pricing/ |
| SS | https://www.stratasys.com/en/stratasysdirect/resources/articles/pa12-white-medical-manufacturing-mjf-production/ |
| HT | https://hotean.com/blogs/hotean-blog/3d-printing-vs-injection-molding-cost |
| ML | https://www.makelab.com/compare/mjf-vs-urethane-casting |
| SO | https://shop.smooth-on.com/mold-star-30 |
| PR-2 / PR-3 | `production/process.md` §2 (what has to be made, volumes) / §3 (FDM cost model) |

Compliance, packaging, labour (read 2026-09-02; store JSON 2026-09-01; full table in `production/compliance-and-assembly.md` §0):

| ID | URL |
|---|---|
| S1–S4 | https://store.pollen-robotics.com/products/microduck.json ; …/dev-pack.json ; …/accessory-pack.json ; …/charger-pack.json |
| S5–S7 | https://store.pollen-robotics.com/policies/refund-policy ; …/terms-of-service ; …/shipping-policy |
| S9 | https://www.iata.org/contentassets/05e6d8742b0047259bf3a700bc9d42b9/lithium-battery-guidance-document.pdf |
| S10 | https://mydhl.express.dhl/content/dam/downloads/global/en/lithium-batteries/dhl_express_lithium_battery_guide.pdf.coredownload.pdf |
| S11 | https://www.law.cornell.edu/cfr/text/49/173.185 |
| S12 / S13 | https://pe.usps.com/text/pub52/pub52c3_028.htm ; https://pe.usps.com/text/imm/immc1_014.htm |
| S14 | https://www.colissimo.entreprise.laposte.fr/en/practical-advice/right-packaging/almost-perfect-parcel-web-series/lithium-batteries |
| S15 | https://www.tradeinn.com/techinn/en/duracell-sony-np-f330-np-f550-2600mah-7.2v-lithium-battery/137796011/p |
| S18 | https://fccid.io/2BC6T-RADXAZERO3W |
| S19 | https://radxa.com/products/zeros/zero3w/ ; https://docs.radxa.com/en/zero/zero3 |
| S20 | https://apps.fcc.gov/kdb/GetAttachment.html?id=bNCiEdkFEKnHsZF9GHCNdg%3D%3D&desc=996369+D04+Module+Integration+Guide+V02&tracking_number=44637 (snippet) |
| S21 | https://www.law.cornell.edu/cfr/text/47/15.101 |
| S22 | https://single-market-economy.ec.europa.eu/sectors/electrical-and-electronic-engineering-industries-eei/radio-equipment-directive-red_en |
| S23 | https://eur-lex.europa.eu/eli/dec_impl/2025/138/oj/eng |
| S24 / S25 | https://single-market-economy.ec.europa.eu/single-market/goods/european-standards/harmonised-standards/radio-equipment_en ; …/low-voltage-lvd_en |
| S26 | https://www.nemko.com/blog/postponed-implementation-of-new-european-safety-standard-edition-for-electronics |
| S27 / S28 | https://eur-lex.europa.eu/eli/dir/2009/48/oj/eng ; https://www.legislation.gov.uk/eudr/2009/48/annex/I |
| S29 | https://www.ul.com/news/ec-publishes-toy-safety-regulation-regeu-20252509 |
| S30 / S31 | https://eur-lex.europa.eu/legal-content/EN/LSU/?uri=CELEX:32023R1542 ; https://www.compliancegate.com/removable-and-replaceable-battery-requirements-european-union/ |
| S32 / S33 | https://www.gov.uk/guidance/using-the-ukca-marking ; https://www.trade.gov/market-intelligence/united-kingdom-extends-ce-mark-recognition |
| S34 | https://www.compliancegate.com/ppwr-timeline-and-dates/ |
| S35 | https://www.tuv.com/regulations-and-standards/en/eu-general-product-safety-regulation-eu-2023-988-gpsr-entered-into-force.html (snippet) |
| S36 | https://f2labs.com/technotes/2016/06/10/machinery-directive-200642ec-article-1-2-k/ ; https://eur-lex.europa.eu/eli/reg/2023/1230/oj/eng (snippet) |
| S37 | https://deutsche-recycling.com/blog/triman-logo-in-france-2/ (snippet) |
| S38 | https://lexparency.org/eu/32012L0019/ANX_IX/ ; https://www.tuvsud.com/en-us/services/product-certification/ce-marking/ce-rohs-2 (snippets) |
| S39 / S40 | http://www.battery-cert.com/en/cases/show/28.html ; https://www.korea-certification.com/en/kc-emc/kc-emc-certification/ ; https://ib-lenhardt.com/kb/mic-requirements (snippets) |
| S41 | https://www.lion-care.com/en/Info-Center/Industry-knowledge/Guidelines-and-laws-for-the-transport-of-lithium-batteries/Special-provisions-from-the-ADR/ (snippet) |
| S42 | https://www.robotis.us/dynamixel-xl330-m288-t/ (screws shipped with the servo) |
| S43 / S44 | https://www.fabflow.app/blog/design-for-assembly-dfa-complete-engineering-guide ; https://www.dfma.com/forum/2019pdf/devenish.pdf |
| S45 | https://www.legisocial.fr/reperes-sociaux/montant-smic-2026-taux-horaire-net-brut.html |
| S46 | https://www.china-briefing.com/news/minimum-wages-china/ ; https://www.playroll.com/minimum-wage/china (snippet) |
| S47 | https://single-market-economy.ec.europa.eu/sectors/electrical-and-electronic-engineering-industries-eei/radio-equipment-directive-red/one-common-charging-solution-all_en (snippet) |
| K-7 / K-9 | `production/compliance-and-assembly.md` §7 (labour arithmetic) / §9 (its CD list, incl. the 2026-09-02 search for a Pollen compliance page) |

"Snippet" = read from a search-engine result, not the page; one notch weaker
than a fetched page.
