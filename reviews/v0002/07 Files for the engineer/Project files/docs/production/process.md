# PROCESS — printed vs moulded, for the Microduck's 24 printed slugs and 4 soft parts

*Written 2026-09-02 from web sources only (this machine was under load; nothing
was sliced or built). Companion to `docs/PARTS.md` (sizes), `docs/BOM.md`
(solid volumes, qty) and `SPEC.md` §6. Every number carries its source URL and
the date it was read. A number no source stated is **CANNOT DETERMINE** with
what would settle it. Bracket figures from vendor blogs are labelled
**[bracket]** — they are published ranges, not quotes on our geometry; a quote
on our STEP files is the only thing that turns them into a price.*

## 0. Sources

All fetched 2026-09-02 unless marked; [R1] rows were fetched 2026-09-01 by
`research/01-product-and-specs.md`.

| id | URL | what it gave |
|---|---|---|
| PK | https://pollen-robotics.com/microduck/press-kit/ (`research/raw/presskit.txt`, 2026-09-01) | "Four printed colourways" |
| ST | https://store.pollen-robotics.com/products/microduck (2026-09-01, [R1 §13]) | "ramping up production" banner, 780 g |
| BB | https://www.bloomberg.com/news/articles/2026-08-27/hugging-face-unveils-400-singing-skating-duck-like-robot — read via the mirror https://finance.yahoo.com/technology/ai/articles/hugging-face-unveils-400-singing-121456627.html | manufacturer, volume target, Reachy Mini units |
| TM | https://www.techmeme.com/260827/p21 | Bloomberg headline: "manufactured by Shenzhen-based Seeed Studio" |
| AX | https://www.axios.com/2026/08/27/hugging-face-debuts-microduck-a-399-robot — direct fetch 403; quoted via https://gagadget.com/en/723594-hugging-faces-399-microduck-is-a-tiny-open-source-robot-you-can-actually-train/ and https://resellcalendar.com/news/news/pollen-robotics-microduck-preorder-sold-out-reseller/ | 50,000 target; 5,000 units / $2.6 M in 24 h |
| TNW | https://thenextweb.com/news/hugging-face-microduck-399-open-source-robot | Reachy Mini "more than 10,000 units" |
| SEED | https://www.seeedstudio.com/blog/2026/01/06/reachy-mini-an-open-journey-built-together-with-hugging-face-pollen-robotics-seeed-studio/ — direct fetch 403; search snippet only | Reachy Mini: 3D-printed prototype → industrial production |
| OEL | https://openelab.io/blogs/learn/seeed-studio-hugging-face-reachy-mini-your-gateway-to-open-source-humanoid-robotics (reseller blog, secondary) | "All structural components are injection molded" |
| LM1 | https://layermath.com/blog/how-to-run-a-3d-print-farm (15 Mar 2026) | machine running cost £/hr |
| LM2 | https://layermath.com/blog/3d-printing-hourly-rate (9 Jun 2026) | what to charge per print hour |
| LM3 | https://layermath.com/filament-prices (Apr 2026) | filament £/$ per kg |
| PR1 | https://blog.prusa3d.com/how-to-calculate-printing-costs_38650/ (13 Oct 2020) | Prusa's depreciation-per-hour method |
| PR2 | https://pro.prusa3d.com/guides/how-to-build-a-3d-printing-farm/ | "$2 per print hour per machine"; 1,000 kits / 3 weeks / 50 printers |
| CC | https://3dprintingcostcalculator.com/news/3d-printing-cost-formula (8 Jun 2026, upd. 11 Jun) | five-line formula, wear $/hr, worked example |
| GC | https://grandpacad.com/en/tools/3d-printing-business-calculator | defaults: $600 printer, $3/print-hour base fee |
| 3DP | https://3dprinting.com/how-much-does-3d-printing-cost/ (reviewed 18 May 2026) | bureau $/g for FDM, SLS/MJF $/cm³ |
| SL | https://www.slant3d.com/ | 1,000 printers, PLA $10/kg, no MOQ |
| PL1 | https://www.protolabs.com/services/injection-molding/ | mould from $1,495; 2,000-shot guarantee |
| PL2 | https://www.protolabs.com/help-center/pricing-and-payment-options/ | 3D printing from $95; moulding from $1,495 |
| PL3 | https://www.protolabs.com/resources/design-tips/11-tips-to-reduce-injection-molding-costs/ | 25 pieces minimum economic; 2,000 / 10,000+ tiers |
| PL4 | https://www.protolabs.com/en-gb/resources/design-tips/comparing-cost-between-injection-moulding-and-3d-printing/ | cam/insert adds £1,000–2,000 per component |
| XM1 | https://www.xometry.com/resources/injection-molding/injection-molding-vs-3d-printing/ (upd. 29 Jun 2026) | three worked break-even examples |
| XM2 | https://www.xometry.com/resources/injection-molding/injection-molding-cost/ (upd. 20 Jul 2026) | tooling "up to $10,000" for 1,000–2,000 small parts; resin $/lb |
| XM3 | https://www.xometry.com/resources/materials/mjf-materials/ | MJF colours: natural grey, dyed black; TPU 88A |
| XM4 | https://www.xometry.com/capabilities/vapor-smoothing/ | +1–5 business days; TPU 88A smoothable |
| JC1 | https://jlc3dp.com/news/drastic-material-price-cuts-and-adjusted-post-processing-service-fees (eff. 13 Aug 2025) | MJF-PA12 $0.275/g |
| JC2 | https://jlc3dp.com/help/article/pa12-hp-nylon ; https://jlc3dp.com/help/article/pa12s-hp-nylon ; https://jlc3dp.com/help/article/3301pa-nylon | "From $1.00", colours, min wall, tolerance |
| HP | https://hp3dprint.eu/3d-materials-finishes-pricing/ | MJF €/cm³ incl. TPU 90A and vapour smoothing |
| SS | https://www.stratasys.com/en/stratasysdirect/resources/articles/pa12-white-medical-manufacturing-mjf-production/ (25 Feb 2026) | PA12-W dyes yellow/orange |
| JY | https://www.jaycon.com/injection-moulding-price-a-2025-guide-for-engineers-procurement/ (9 May 2025) | tooling brackets, per-part by volume |
| HT | https://hotean.com/blogs/hotean-blog/3d-printing-vs-injection-molding-cost (10 Feb 2026) | alu $2–10k; per-part $0.50–5; break-even 200–1,000 |
| MK | https://mekalite.com/injection-molding-pricing-overview-what-to-expect-know-the-2025-rates/ (8 Sep 2025) | alu tool life 1k–10k; P20 enclosure $5–8k |
| MM | https://www.momaking.com/en/article/injection-mold-cost-2025-your-essential-guide-to-saving-money | single-cavity from $5,000; tweak $1–5k |
| ML | https://www.makelab.com/compare/mjf-vs-urethane-casting | silicone mould $500–3,000, 20–30 pulls |
| SO | https://shop.smooth-on.com/mold-star-30 | Mold Star 30 trial $37.31 (2 lb) |
| FC | https://thefilamentcalc.com/ | densities PLA 1.24, PETG 1.27, TPU 1.21 g/cm³ |

## 1. What Pollen says about its own manufacturing

| claim | verbatim | source |
|---|---|---|
| shells are printed | "Four printed colourways - Cream, Graphite, Lavender and Sky. Same robot underneath. Swatches are the calibrated shell colours from the press photos." | PK |
| who makes it | "The robot is manufactured in China with Shenzhen-based open-source hardware provider Seeed Studio." | BB (Kelly & Lung, 2026-08-27) |
| volume target | "The company said it's aiming to sell more than 20,000 Microducks, with the first shipments expected before Christmas." | BB |
| volume ambition | Delangue to Axios: "50,000 would be a great success" (~$20 M at $400) | AX via gagadget / resellcalendar |
| first-day demand | "blew past $2.6 million in orders in its first 24 hours alone, translating to more than 5,000 units" | AX via resellcalendar (2026-08-29) |
| ramp | "The community ordered a lot of ducks. We can't promise Christmas delivery for new microduck orders anymore, but we're ramping up production." | ST (2026-09-01) |
| precedent | Reachy Mini "has sold more than 10,000 units since launching last year" | TNW; BB says "about 10,000" |
| precedent process | Reachy Mini: announced July 2025 as "a 3D-printed prototype"; "over 3,000 orders within a week in November" pushed it "from prototyping to industrial production" with Seeed | SEED (snippet only — page 403 on fetch) |
| precedent result | "All structural components are injection molded and ready to assemble" | OEL (reseller page, secondary) |

Reading: "printed" in the press kit is the only process word Pollen has used
for Microduck. Whether that word survives a 20,000-unit run built at Seeed is
**CANNOT DETERMINE** — the Reachy Mini precedent went printed → moulded once
orders passed 3,000 in a week, and Microduck passed 5,000 in a day. No
interview names the Microduck process. What settles it: a production unit's
shell (layer lines vs gate/ejector marks), or a Seeed/Pollen statement.

## 2. What has to be made

From `docs/BOM.md` §2–3 (solid volumes per mesh from [R2 §4.3] table, mesh bboxes [M]).
24 hard slugs = 31 pieces (the M12 lens holder, 1.10 cm³, bought-or-printed
CANNOT DETERMINE, is left out of the piece count as in BOM.md); 4 soft pieces.
Volumes below are per-mesh × qty, re-summed here: **≈198 cm³**, not the
"≈183" BOM.md prints (that figure does not reproduce from its own rows).

| group | slugs | pieces | solid cm³ (sum) | largest bbox mm | colour role |
|---|---|---|---|---|---|
| colourway shells | trunk-shell-left/right, top-head-shell | 3 | 52.7 | 91.6 × 122.7 × 46.3 | 4 pastel colourways |
| trim (orange / yellow) | ankle L/R, foot L/R, bottom-head-shell, jaw | 6 | 73.3 | 91.7 × 116.7 × 20.1 | 2 trim colours |
| structure, grey/dark | trunk-base, banana-locker, power-support, yaw2roll ×2, bearing-roll ×2, hip-bracket ×2, upper-leg L/R, rigidity-plate ×2, shin ×2, neck-plate ×2, neck-pitch, yaw-roll-motion, motor-support, face-part, eye-ring | 22 | 72.0 | 73.5 × 54.2 × 18.8 | internal / dark |
| **hard total** | 24 | **31** | **≈198** | | |
| soft (TPU inferred) | sole L/R, jaw-soft, soft-mouth-top | 4 | 33.8 | 87.8 × 32.6 × 8.4 | mint / lilac |

Every piece fits a 256 × 256 mm bed (largest 122.7 mm) and Protolabs' mould
envelope (480 × 751 × 203 mm, PL1). Thin features: 1 mm rigidity plate,
2 mm neck plates, 1 mm shell walls in the meshes (SPEC §6) — at JLC3DP's
MJF/SLS minimum wall "1mm" / "> 1.0mm" (JC2) they are marginal.

**Mass bound (not a measurement).** Solid volume × PLA 1.24 g/cm³ (FC) gives
the mass if printed 100 % solid: hard parts ≤ 246 g, soft parts (TPU 1.21)
≤ 41 g. Real FDM grams (walls + infill) and print hours are **CANNOT
DETERMINE until sliced** — `cad-print` / ce-slice on the rebuilt parts settles
both; no slicer output exists in `out/` at 2026-09-02.

## 3. FDM — the cost model

### 3.1 Machine-hour rates (five sources)

| source | figure (verbatim) | date |
|---|---|---|
| LM1 | Bambu A1 Mini running cost "£0.188/hr" = depreciation "£0.100" (£299 ÷ 3000 h) + electricity "£0.061" (180 W @ £0.34/kWh) + maintenance "£0.027" (£40/yr ÷ 1500 h); Ender-3 V3 depreciation "£0.076"; labour "£12–15/hr" | 2026-03-15 |
| CC | wear = printer price ÷ "5,000 printing hours": Ender-3 V3 SE "$0.04/hour", Bambu A1 "$0.06-0.08/hour", P1S "$0.08-0.14/hour", Prusa MK4S "$0.20-0.23/hour"; labour "Fifteen minutes at $20/h is $5.00 … 58% of the true cost" | 2026-06-08 |
| PR1 | operation cost = "Printer price / required investment return time (h) * print time (h)"; MK3S "$0.21/hour", MINI "$0.10/hour" at a 6-month (4,392 h) payback; labour "$9.50 USD/hour"; electricity "negligible" | 2020-10-13 |
| LM2 | what to charge: hobby "0.75-1.50/hr", seller "2.00-4.00/hr", pro "5.00-8.00/hr"; "most sellers should charge 2-4 per print hour" | 2026-06-09 |
| PR2 | Zac Hartley (70+ printers): "I aim for $2 per print hour per machine and a 30% gross profit margin"; success rate 90–95 %; 70 printers' electricity "a couple of hundred dollars a month" | undated |
| GC | defaults: "$600" printer, "12 hours/day, 25 days/month", failure "10%", "$3 base fee per print hour", labour "$20.00/hour" | undated |

Cost of owning a machine-hour: **$0.04–0.23/h wear + ~$0.06–0.08/h power**
(CC, LM1). Price of a machine-hour bought from a farm: **$2–4/h** (LM2, PR2, GC).

### 3.2 Material

PLA "$24.00/kg" US / "£20.00/kg" UK; PETG "$29.00/kg"; TPU "$44.00/kg" (LM3,
Apr 2026). Slant 3D buys PLA at "$10/kg" (SL). CC's default "$20/kg … 2 cents
per gram" with "× 1.10" waste.

### 3.3 The per-robot formula (CC's five lines, our symbols)

For piece *i* with sliced grams *g_i* and hours *h_i* (both CANNOT DETERMINE
until sliced):

```
material_i   = g_i / 1000 × $/kg × 1.10
machine_i    = h_i × (wear + power)            in-house: $0.10–0.31/h
             = h_i × $2–4                      bought from a farm
labour_i     = hands-on minutes / 60 × rate   (CC: 15 min @ $20 = $5, 58 % of a 100 g print)
robot        = Σ_i (material_i + machine_i + labour_i) × 1.1–1.3 failure buffer
```

What is already bounded: Σ g_i ≤ 246 g PLA → material ≤ $6.5 at $24/kg (× 1.10),
≤ $2.7 at Slant's $10/kg. What is not: Σ h_i (the dominant term at farm
rates) and labour per piece (31 pieces × CC's 15 min = 7.75 h → $155 at
$20/h if nothing is batched — the number that decides whether FDM survives
at 1,000 units; plating many small parts per job is how PR2's example hit
"1,000 kits every 3 weeks using 50 printers (80,000 total parts)" ≈ 76
parts per printer-day).

### 3.4 FDM bought from a bureau

| source | figure (verbatim) |
|---|---|
| 3DP | "FDM, $0.05-$0.15 per gram plus $3-$10 setup per part. A 100g part lands at $8-$25 before shipping." |
| SL | "1000 3D Printers"; "No MOQs"; PLA "$10/kg" membership; claims additive "typically beats molding on cost once tooling is counted in" up to ~250,000 units (vendor claim) |
| PL2 | 3D printing "Prices start around $95" per order |

At 3DP's bureau rate our ≤ 246 g of PLA spread over 31 pieces is
$12–37 material-side plus 31 × $3–10 = $93–310 setup — the setup term is why a
bureau FDM path only works with parts plated together, which bureaus do not
always allow. Quote on our files: CANNOT DETERMINE.

## 4. MJF / SLS service prices

| source | material | price (verbatim) | colour | date |
|---|---|---|---|---|
| JC1 | MJF-PA12 | "0.35" → "0.275" $/g ("21.50%" cut) | — | eff. 2025-08-13 |
| JC2 | PA12-HP (MJF) | "From $1.00"; wall "1mm"; ±0.3 mm ≤100 mm; "72 hours" | "Natural gray" | 2026-09-02 |
| JC2 | PA12S-HP | "From $1.00"; wall "> 1.0mm" | "Black; Gray" | |
| JC2 | 3301PA (SLS) | "From $1.00"; "96h" | white | |
| HP | MJF PA12 | "0.29 €/cm3" raw grey; "HQ Black … 0.31 €/cm3"; "Vapour smoothing … 0.42 €/cm3" | grey / black | |
| HP | MJF TPU 90A | "0.58 €/cm3" | | |
| 3DP | SLS/MJF bureaus | "$1-$10 per cubic centimetre" | | 2026-05-18 |
| XM1 | drone leg 147 × 140 × 33 mm, SLS | "$32 per part (1 unit); $24 per part (250+ units)" | | 2026-06-29 |
| XM1 | knob 16.8 × 15.2 × 15.2 mm, MJF | "~$3.45 per unit (30 units)" | | |
| XM3 | Nylon 12, TPU 88A | "Can be dyed black and vapor smoothed" | grey / black | |
| SS | PA12-W (white powder) | "can be dyed many colors, including more difficult ones likes yellow or orange" | | 2026-02-25 |

Floor for our hard set at HP's €0.29/cm³ on solid volume: 198 cm³ → **≈ €57
per robot in raw grey**, ≈ €83 vapour-smoothed; soft set at €0.58/cm³ TPU 90A
→ ≈ €20. These are floors: bureaus price on offset or bounding volume (3D
People: "surface is offset by 3.0 mm" — https://www.3dpeople.uk/pa12-nylon-mjf/),
so the invoice is above the solid-volume number. JLC3DP's $0.275/g needs a
PA12 part mass; PA12 density was not read from a source → CANNOT DETERMINE.

Colourways on MJF: grey-substrate PA12 dyes black (XM3, HP). Cream, Lavender
and Sky are pastels — reachable only on a white powder (PA12-W, SS) plus dye
or paint; no source read gives a price for pastel dye. **CANNOT DETERMINE**;
a PA12-W dye quote settles it. Yellow/orange trim: SS says dyeable on PA12-W.

## 5. Injection moulding — tooling brackets [bracket]

| source | bracket (verbatim) | date |
|---|---|---|
| PL1/PL2 | "Mold cost starts at $1,495"; prototyping tool "guaranteed for at least 2,000 shots"; on-demand tool "Unlimited … we will cut a new tool if it wears out"; "as fast as 1 day", standard "7 days" | 2026-09-02 |
| PL3 | economic "as low as 25 pieces"; "2,000 parts" prototyping / on-demand boundary; "10,000+ parts" typical for on-demand aluminium | |
| PL4 | "If a cam or insert is required, your overall mould size can increase by £1,000-£2,000 per component" | |
| JY | "3D-printed/Aluminum mold ($100 to $1,000)"; "Hardened-steel mold ($2,500 to $5,000)" mid-volume; "($25,000 to $75,000)" high-volume; per part: 100–1K "~$4 to $5", 5–10K "~$3", 100K+ "~$1.75" | 2025-05-09 |
| HT | "A basic aluminum mold typically costs $2,000 to $10,000"; steel "$10,000 to over $100,000"; per part "$0.50 to $5.00"; break-even "Between 200 and 1,000 units" — simple small "~200 Units", complex large "~800 Units" | 2026-02-10 |
| MK | aluminium tool life "1,000–10,000 parts"; simple enclosure "~$5,000 – $8,000 for a single-cavity P20 steel mold", "~$0.50 – $0.80" per part; floor "$3,000" | 2025-09-08 |
| MM | "single-cavity molds for low volume injection molding start at $5,000"; "Each mold tweak might cost $1,000–$5,000" | |
| XM1 | knob: moulded "~$0.80 per unit (without tooling, 2,000+ units)", break-even "2,000 units"; junction housing 216 × 172 × 68 mm: tooling "~$10,000", break-even "250 units" | 2026-06-29 |
| XM2 | "Mid-level orders (1,000-2,000 small parts): up to $10,000" tooling | 2026-07-20 |

### 5.1 How many tools

Mirrored pairs (L/R shells, upper legs, ankles, feet) cannot share a cavity;
identical pairs (yaw2roll ×2, hip-bracket ×2, shin ×2 …) can. Counting one
cavity set per slug: **24 tools** for the hard parts, **3–4** for the soft
(TPU is mouldable; a two-shot soft-on-hard beak is a different, dearer tool).
Family moulds (several small parts in one tool) cut the count; how far is a
quoting question → CANNOT DETERMINE.

Tooling totals, Protolabs floor × count and the aluminium bracket × count:

| scope | tools | at $1,495 each (PL1 floor) | at $2,000–10,000 each (HT alu) |
|---|---|---|---|
| everything hard | 24 | $35,880 | $48,000–240,000 |
| visible only (3 shells + 6 trim) | 9 | $13,455 | $18,000–90,000 |
| the two largest (top-head-shell, bottom-head-shell) | 2 | $2,990 | $4,000–20,000 |

The mesh geometry was drawn for printing (SPEC §6: 1 mm plates, 2 mm walls,
printed-style bosses, bearing seats, M2 c'bores). A moulded version needs
draft, uniform walls, side-actions for the bearing bores and the head dome's
undercuts (PL4: £1,000–2,000 per cam) — a redesign, not a re-quote. Colours:
moulding in colour means 4 shell resins + 2 trim resins; per-colour MOQ and
purge cost were not read → CANNOT DETERMINE.

### 5.2 Break-even

N\* = T / (c_print − c_mould). With sourced brackets: c_mould $0.50–5 per
piece (HT) plus $1,495–10,000 per tool; c_print per piece for a small part
$3.45 (MJF knob, XM1) to $8–25 (bureau FDM 100 g part, 3DP) to in-house FDM
(unknown until sliced, ≥ material $0.03–0.19 per piece). Sources' own
answer: "Between 200 and 1,000 units" (HT), "250 units" for a 147 mm part
(XM1), "2,000 units" for a 17 mm part (XM1). Our largest parts (91–123 mm)
sit at the 250-unit end; the 22 small brackets sit at the 2,000-unit end.

## 6. Soft parts (sole ×2, jaw-soft, soft-mouth-top)

| route | numbers (verbatim) | fits |
|---|---|---|
| FDM TPU in-house | filament "$44.00/kg" (LM3); ≤ 41 g solid per robot → ≤ $2 material; hours CANNOT DETERMINE | 1–100; colour = filament colour (lilac/mint TPU availability not checked) |
| MJF TPU | Xometry "TPU 88A" grey, dyeable black (XM3); HP "TPU 90A 0.58 €/cm3" → ≈ €20 per robot on solid volume | any qty; pastel lilac/mint CANNOT DETERMINE |
| urethane casting | silicone mould "$500–$3,000", "degrade after 20–30 pulls", best "50–500 identical parts", shore "30A–80D", lead "2–3 weeks" (ML); DIY: Mold Star 30 trial "$37.31" for "2 lbs", 30 A, 45 min pot life, 6 h cure (SO) | 10–100; pigmentable to lilac/mint; a durometer ≥ 90A is at the top of ML's range |
| TPU injection moulding | same tooling brackets as §5; 3–4 tools | 1,000+ |

Durometer and material of Pollen's lips and soles: CANNOT DETERMINE (community
says TPU 90–95A, `BOM.md` §3). ODM v2 printed its soft foot in TPU (R1 §16.1).

## 7. Post-processing by route

| route | steps | sources |
|---|---|---|
| FDM | support removal, first-layer clean-up, M2 heat-set inserts (~60 per robot, community estimate, `BOM.md` §4), bearing-seat reaming (FDM holes "0.1–0.3 mm undersize", `PARTS.md` §5) | CC's "15 min" hands-on per print is the labour line |
| MJF/SLS | depowder / bead-blast (batch), optional dye (black: +€0.02/cm³ HP), optional vapour smoothing (+€0.13/cm³ HP; "+1-5 business days" XM4), inserts still needed | HP, XM4 |
| moulding | gate/flash trim, no inserts if bosses are designed for thread-forming screws (CANNOT DETERMINE — not in any source for M2 in the chosen resin), moulded-in colour, no colour post-process | JY, MK |

Colourways per route: FDM = spool colour (4 shell + 2 trim spools, no extra
cost beyond spool changes); MJF = grey/black native, pastel only via PA12-W +
dye (price CANNOT DETERMINE); moulding = coloured resin, colour-change MOQ
CANNOT DETERMINE.

## 8. Decision table — 1 / 10 / 100 / 1,000 units

Per robot, hard set (31 pieces) unless noted. "floor" = arithmetic on sourced
rates and our solid volumes; "[bracket]" = vendor range on unlike parts;
"?" = CANNOT DETERMINE with what settles it.

| units | FDM in-house | FDM farm / bureau | MJF / SLS | injection moulding | soft parts | decision |
|---|---|---|---|---|---|---|
| **1** | material ≤ $6.5 floor; machine $0.10–0.31/h × Σh (? sliced); labour 31 × 15 min at $20 = $155 if unbatched (CC) | 3DP: 31 × $3–10 setup = $93–310 + $12–37; PL2 min "$95" | HP floor ≈ €57 grey / €83 smoothed, pastel ? | 24 tools ≥ $35,880 — not a candidate | FDM TPU ≤ $2 material; or cast: $37 kit + a printed master | **FDM in-house.** MJF only for the 3 shells if pastel dye is quoted |
| **10** | as above × 10; one printer, Σh ? | bureau setup term dominates | ≈ €570 floor for 10 | tooling amortised $3,588+/robot — no | FDM TPU or one silicone mould per soft part (20–30 pulls, ML) | **FDM in-house**, batch-plated; cast the lips if 90A TPU printing fails the beak test |
| **100** | 100 × 31 = 3,100 pieces; PR2's farm rate 76 parts/printer-day → ≈ 41 printer-days; farm price $2–4/h × Σh ? | Slant-type: no MOQ, PLA $10/kg (SL); quote ? | ≈ €5,700 floor, pastel ? | 24 tools $35,880–240,000 → $359–2,400/robot before parts; HT's break-even "~200" for simple small parts not yet reached | urethane: 4 moulds × 20–30 pulls → 14–20 moulds per 100 robots × $500–3,000 (ML) — worse than printing; MJF TPU ≈ €20/robot | **FDM farm** (own or Slant-type). Mould nothing. Print TPU or MJF TPU |
| **1,000** | 31,000 pieces ≈ 408 printer-days at PR2's rate — a 20-printer farm for ~3 weeks; labour ? | quote ? | ≈ €57,000+ floor — MJF is the dearest route here | visible-9 tools $13,455–90,000 → $13–90/robot + 9 × $0.50–5 = $4.50–45 parts; all-24 tools → $36–240/robot + $16–155 parts | TPU moulding: 3–4 tools ≥ $4,485 → ≥ $4.50/robot + parts | **Mould the 9 visible parts** (shells, dome, jaw, feet, ankles) after a DFM redesign; **keep the 22 small grey brackets FDM** (XM1: 17 mm parts break even at "2,000 units"); soft parts → TPU mould or MJF TPU on the quote |

The Reachy Mini precedent (§1) is the calibration: at "over 3,000 orders
within a week" the shells went to injection moulding with Seeed. Microduck at
5,000 units in 24 h and a 20,000-unit target is past every break-even in §5.2
for its large parts, so Pollen's "printed" most likely describes the press
units, not the run — CANNOT DETERMINE until a shipped shell is examined.

## 9. CANNOT DETERMINE — the list and what settles each

1. Grams and hours per piece — slice the 24 rebuilt parts (`cad-print`).
2. Quotes on our geometry for FDM bureau, MJF, moulding — upload STEP to JLC3DP / Xometry / Protolabs; quotes need the STEP export from rung 6.
3. Whether Pollen's production shells are moulded — a shipped unit, or a Seeed statement (Seeed blog fetch was 403; snippet only).
4. Pastel (Cream/Lavender/Sky) on MJF — a PA12-W + dye quote.
5. Moulded-in-colour MOQ and colour-change cost — the moulder's quote.
6. Soft-part durometer and material — a production lip on a Shore gauge.
7. Family-mould grouping for the 22 small parts — the moulder's DFM.
8. M2 thread strategy for moulded bosses (inserts vs thread-forming) — resin datasheet + pull test.
9. PA12 part mass for JLC3DP's $/g pricing — PA12 density from a datasheet (not read here).
