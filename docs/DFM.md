# DFM — the 20 rebuilt Microduck parts, measured for FDM

**Set.** Every part whose `ce-parts/<slug>/component.json` says
`record.origin = "generated"` **and** `record.verdict = "PASS"` — 20 parts.
Nothing else is in this table: a vendor mesh is not a rebuild and a decimated
mesh has no callable dimension.

**Measured** 2026-09-02 under `ce-cad/bin/cad`, on the PARAMETRIC SOLID loaded
by `cecad.triad.load("part:<slug>")` — not on a mesh someone shipped us:

| what | by | where it lands |
|---|---|---|
| bed fit, upright, thinnest wall vs two perimeters, modelled filament | `cecad.printed.printability` | `out/dfm/dfm-rebuilt.json` → `printability` |
| exact thinnest wall + the point it occurs at | `cecad.inspect.thinnest_wall_detail` | → `thinnest_wall_detail` |
| every hole: Ø, axis, depth, through/blind | `cecad.inspect.holes` | → `holes` |
| figures + verdict roll-up | `cecad.dfm.measure(slice=False)` | → `dfm_measure` |
| subtractive plan | `cecad.machining.plan` | → `machining` |
| **overhang and support area, six build directions** | `tools/dfm_rebuilt.py` + `tools/dfm_orient.py` on this solid's own tessellation | → `mesh`, `orientation` |
| **grams and seconds** | the print farm's OrcaSlicer, already run | `out/print/slice.json` |

Bed for the geometry checks `prusa_mk4` (250 x 210 x 220); nozzle 0.4, layer
0.2, two-perimeter floor **0.80 mm**. The farm that actually sliced these is a
**Bambu Lab H2S**, 0.4 nozzle, `0.20mm Standard @BBL H2S`, PLA 1.26 g/cm3.

---

## How to read the columns — and what each one is NOT

**Orientation is MEASURED, and the first way we measured it was wrong.**
`ce-cad` has no overhang tool — `printed.printability` says so in as many
words ("It does NOT check overhangs or warping") — so overhang is computed here
from facet normals: for a down-facing facet with unit normal `n` and build-up
direction `u`, `d = -(n.u)` and `beta = acos(d)` is the facet's angle to the
build plate. `beta < 30 deg` is BambuStudio's default support threshold,
`beta < 10 deg` is a flat down-face (a bridge or a floating island).

The first pass ranked the six axis-aligned directions on total `beta<30` area,
and it produced a **wrong answer from a correct measurement**: a part's flat
bottom is a `beta = 0` face, so `microduck-trunk-base` — a 57 x 36 x **3 mm**
plate — scored 43.7% overhang lying flat and 2.4% standing on its 57 mm edge,
and the ranking recommended printing a 3 mm plate 285 layers tall. The bed is
not support material. `tools/dfm_orient.py` therefore splits the `beta<30` area
into **on the plate** (every vertex within one first layer of the part's lowest
point) and **elevated**, and ranks on elevated area only. The naive answer is
kept in the JSON as `naive_best_bed_counted` so the correction stays auditable.
`orient()` re-checks itself on a 10 mm cube (100 mm2 down-face, 100 on the bed,
0 elevated; four vertical walls that must not count) and on a slab standing on
four legs (4 mm2 bed, 100 mm2 elevated) before it will report anything — and
that check **failed on its first run**, on an assertion of 96 that should have
been 100, which is the only reason the numbers below are worth anything.

**Support area is an UPPER BOUND.** An elevated down-face spanning between two
walls is a bridge and prints; one with nothing under it is an island and does
not. Nothing in `ce-cad` tells them apart, and this does not either.

**Thinnest wall: read the exact figure AND the ray percentiles.**
`inspect.thinnest_wall` is exact and reports the single thinnest place on the
solid, which on a chamfered part is a **knife-edge** — a face tapering to a
tangent line, which the slicer rounds off. So the table also carries `p1` and
`p5` from 4000 seeded internal rays (`seed 20260902`): `p1 >= 0.80` means the
sub-0.8 exact reading is a sliver and the part has no thin wall; `p1 < 0.80`
means it really does. Both are reported; neither is laundered.

**Grams are SLICED, by the farm.** `printability`'s modelled shell+infill
figure is in the JSON but is not the authority and is not what the table
quotes. Where `stl_source` says *vendor mesh*, the slicer was run on Pollen's
mesh, not on our rebuild — flagged in the per-part list.

**Machining CANNOT DETERMINE on all 20 is the CORRECT result**, and it now says
why in its own words: *"fdm is ADDITIVE — the findings this module measures
(internal corners, tool reach, depth ratios) do not constrain it."* These are
printed parts. The empty machining verdict confirms that; it does not
contradict it.

**Verdict rule**, applied mechanically, not by feel:

- **PRINTABLE** — fits the bed, **and** needs 0 mm2 of support in the chosen
  orientation, **and** ray `p1 >= 0.80 mm` (no real sub-two-perimeter wall).
- **PRINTABLE-WITH-CARE** — fits and prints, but carries at least one measured
  risk: support needed, a real wall under 0.80 mm, a bore across the layers, a
  thin moving feature, or a foot too small to hold the part down.
- **CANNOT DETERMINE** — a required measurement is missing.

---

## Summary table

Orientation is the build-up direction in the part's own frame, chosen on
elevated support area. "Wall" is exact / ray-p1. "Support" is elevated
`beta<30` mm2 in that orientation; "foot" is bed contact.

| Part | Mat | Fits bed | Print orientation | Wall exact / p1 (mm) | Sliced g | Support mm2 | Foot mm2 | Print risks | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **power-support** | PLA | yes | **+Z upright**, 83.1 mm, 416 L | **0.800 / 0.7998** | 13.15 | **969** | **10.6** | stands on the 10.6 mm2 latch-tongue tip; 437 mm2 head-shelf ledge; 2 flange ledges; 0.466 mm latch slits; 10 M2 tap holes across the layers | PRINTABLE-WITH-CARE |
| shin | PLA | yes | +Z, 58.0 mm, 290 L | 0.028 / 0.804 | 3.60 | 203 | **3.6** | foot is 3.6 mm2 — will not stay on the bed without a brim; all 15 bores across the layers | PRINTABLE-WITH-CARE |
| trunk-base | PLA | yes | +Z flat, 3.0 mm, 15 L | 1.000 / 1.000 | 1.82 | **0** | 1397 | none measured; all 6 holes up the build axis | **PRINTABLE** |
| banana-pcb-locker | PLA | yes | -Y flat, 3.8 mm, 19 L | 0.921 / 0.922 | 0.68 | **0** | 290 | 54 mm long, 1.5 mm thin bar — handling, not printing | **PRINTABLE** |
| bearing-roll | PLA | yes | +Y flat, 3.0 mm, 15 L | 0.900 / 1.000 | 0.85 | **0** | 616 | none measured; Ø19 bore up the build axis | **PRINTABLE** |
| yaw2roll | PLA | yes | -Y, 25.8 mm, 130 L | 0.198 / 0.794 | 2.96 | 108 | 242 | 8 bores across the layers incl. Ø4.84 horn seats; p1 0.794 grazes the floor | PRINTABLE-WITH-CARE |
| upper-leg-left | PLA | yes | -X, 28.0 mm, 140 L | 0.024 / **0.101** | 4.67 | 190 | 1533 | **thinnest real wall in the set** — p5 0.478 mm, under two perimeters over 5% of the surface; Ø5.37 pivots up the axis | PRINTABLE-WITH-CARE |
| upper-leg-right | PLA | yes | +X, 28.0 mm, 140 L | 0.024 / **0.0885** | 4.67 | 190 | 1533 | mirror of the left, same wall problem (p5 0.460) | PRINTABLE-WITH-CARE |
| upper-leg-rigidity-plate | PLA | yes | +X flat, 1.0 mm, **5 L** | 1.000 / 1.000 | 1.00 | **0** | 740 | 5 layers total — must lie flat; warp/handling | **PRINTABLE** |
| hip-bracket | PLA | yes | -Z, 19.0 mm, 95 L | 0.800 / 0.920 | 3.81 | 237 | 134 | 22 bores, **every one across the layers**; densest part in the set | PRINTABLE-WITH-CARE |
| ankle-left | PLA | yes | +Y, 36.5 mm, 183 L | 0.234 / 1.202 | 6.18 | 163 | 82 | Ø15 + Ø14 bearing seat across the layers — bridged, oval, undersize | PRINTABLE-WITH-CARE |
| ankle-right | PLA | yes | +Y, 36.5 mm, 183 L | 0.234 / 1.202 | 6.18 | 163 | 82 | mirror; same bearing seat | PRINTABLE-WITH-CARE |
| foot-left | PLA | yes | -X, 40.1 mm, 201 L | 0.015 / **0.263** | 13.35 | **870** | 43 | most support work in the set after power-support; real sub-mm material in the rib comb | PRINTABLE-WITH-CARE |
| foot-right | PLA | yes | +X, 40.1 mm, 201 L | 0.015 / **0.324** | 13.35 | **870** | 43 | mirror; same | PRINTABLE-WITH-CARE |
| sole-left | TPU | yes | -Y, 54.0 mm, 270 L | 1.232 / 1.316 | 7.07 | 274 | 204 | TPU + 270 layers = the slowest part (2497 s); no holes | PRINTABLE-WITH-CARE |
| sole-right | TPU | yes | -Y, 54.0 mm, 270 L | 1.232 / 1.317 | 7.07 | 275 | 204 | mirror; same | PRINTABLE-WITH-CARE |
| motor-support | PLA | yes | -X, 73.5 mm, 368 L | 0.008 / **0.530** | 9.20 | **836** | 100 | tallest part after power-support; real sub-mm material; slicer says "floating cantilever" | PRINTABLE-WITH-CARE |
| neck-pitch-bracket | PLA | yes | +Y, 18.0 mm, 90 L | 0.376 / **0.339** | 4.38 | 146 | 264 | real sub-mm material; 19 bores, 15 across the layers | PRINTABLE-WITH-CARE |
| neck-plate | PLA | yes | +X flat, 2.0 mm, 11 L | 0.850 / 0.863 | 0.55 | **0** | 200 | 11 layers; tiny (0.55 g) | **PRINTABLE** |
| yaw-roll-motion | PLA | yes | -Z, 22.5 mm, 113 L | **0.750** / 0.850 | 4.71 | 207 | 698 | **exact wall 0.750 mm is genuinely under two perimeters** at (8.75, 8.02, 17.0); Ø12 bore across the layers | PRINTABLE-WITH-CARE |

**20 / 20 fit the bed** in their as-modelled orientation. **5 are PRINTABLE with
nothing to watch; 15 are PRINTABLE-WITH-CARE. 0 are CANNOT DETERMINE, and 0
fail.** Machining is CANNOT DETERMINE on all 20 — correct, they are FDM parts.

Total sliced, one piece of each: **109.26 g** and **22 723 s = 6 h 18 m**
of machine time (Bambu H2S, 0.2 mm, PLA/TPU) — summed from `out/print/slice.json`,
not from the modelled figures.

### Where `printability` says FAIL and this table does not

`printed.printability` returns `ok = fits and wall >= 0.80` and so reports
**FAIL on 10 parts** (ankle L/R, foot L/R, motor-support, neck-pitch-bracket,
shin, upper-leg L/R, yaw-roll-motion, yaw2roll). That flag is doing its job —
it cannot tell a knife-edge from a wall. The ray percentiles can, and on shin
(p1 0.804), ankle (1.202) and yaw2roll (0.794) the exact minimum is a chamfer
sliver, not a wall. The five where the thin material is **real** are
**upper-leg L/R (p1 0.10/0.09), foot L/R (0.26/0.32), motor-support (0.53),
neck-pitch-bracket (0.34)** and **yaw-roll-motion (exact 0.750)**. Both numbers
are in the table; the FAIL is not hidden and it is not obeyed blindly.

---

## Per-part print risks

### power-support — 54.5 x 17.0 x 83.1 mm, PLA, 13.15 g sliced, 2302 s
The hardest part in the set on every axis: tallest, most support, smallest
foot, the only moving printed feature. Full risk list below in its own section.

### shin — 8.0 x 20.0 x 58.0 mm, 3.60 g, 869 s
- **Foot 3.6 mm2.** Standing +Z (58 mm, 290 layers) is the least-support
  orientation (203 mm2) but the part touches the bed on almost nothing. A brim
  is not optional. The alternative the farm chose, "8 mm plate flat, rim walls
  up" (±X, 40 layers, 190 mm2 of bed), costs 696-831 mm2 of support instead —
  a real trade, both numbers measured.
- **All 15 bores run across the layers** in +Z: 4 x Ø2.20, 2 x Ø2.40, 1 x Ø2.70,
  4 x Ø4.40, 2 x Ø4.84, 1 x Ø5.50, 1 x Ø6.00. Each one's top arc bridges. The
  Ø6.00 and Ø5.50 are the knee/ankle pivots — ream them.
- Exact wall 0.028 mm at (35.87, 31.98, 14.88) is a knife-edge; p1 0.804 mm
  says the plate itself is sound.

### trunk-base — 57 x 36 x 3.0 mm, 1.82 g, 280 s
- **Zero support, 1397 mm2 of bed, 15 layers.** The easiest part here.
- All 6 holes (4 x Ø2.30, 2 x Ø19.00) run up the build axis: they print round,
  slightly undersize, and never bridge.

### banana-pcb-locker — 54.0 x 3.8 x 6.6 mm, 0.68 g, 140 s
- Zero support laid on its 54 mm face (19 layers, 290 mm2 of bed).
- Both Ø2.17 holes run up the build axis. Nothing bridges.
- 1.5 mm thin over 54 mm: the risk is snapping it off the plate, not printing it.

### bearing-roll — 23 x 3.0 x 40 mm, 0.85 g, 164 s
- Zero support flat; the Ø19 window and 4 x Ø2.20 are all axial. Prints clean.
- 0.9 mm minimum wall around the window is 2.25 perimeters — thin but real.

### yaw2roll — 23 x 25.8 x 20.5 mm, 2.96 g, 787 s
- 108 mm2 of support in -Y (130 layers), the least of the six directions.
- **8 bores across the layers**: 4 x Ø2.20 + 4 x Ø4.40. The Ø4.84 horn seats and
  Ø5.50 run up the axis in this orientation and print clean — that is the whole
  reason -Y wins.
- Exact 0.198 mm is a sliver, but p1 0.794 mm grazes the two-perimeter floor:
  the 1.4 mm walls the record describes have thin spots. Keep 2 perimeters
  minimum and do not thin this part further.

### upper-leg-left / upper-leg-right — 28 x 47.7 x 61.0 mm, 4.67 g each, ~918 s
- **The thinnest real material in the set.** Exact 0.024 mm is a knife-edge,
  but the rays say p1 = 0.1012 mm (left) / 0.0885 mm (right) and **p5 = 0.478 /
  0.460 mm** — over five per cent of the sampled surface is under half a
  millimetre, i.e. thinner than a single 0.4 mm perimeter can bridge cleanly.
  The record calls these "1 mm walls" and the median ray agrees (0.9986 mm), so
  the thin fifth is local, not global — but it is not a chamfer either.
  **This is the one part where the geometry, not the print, should be revisited.**
- Laying it on its side (-X left / +X right, 140 layers) buys 1533 mm2 of bed
  and cuts support from 745 mm2 (the naive upright answer) to 190 mm2.
- Both Ø5.37 hip/knee pivots run up the build axis in that orientation — they
  print round. Ream anyway if a shaft passes through.
- Slicer flag: "floating cantilever - enable supports".

### upper-leg-rigidity-plate — 1.0 x 45.0 x 58.1 mm, 1.00 g, 204 s
- **Five layers total.** Zero support, 740 mm2 of bed, wall a flat 1.000 mm
  everywhere (min = p1 = p5 = median). Print it dead flat; standing it on edge
  is 291 layers of a 1 mm wall and is not a real option.
- Ø19 windows and 4 x Ø2.20 all run up the build axis.
- Warp and handling are the risks, not the print.

### hip-bracket — 32.45 x 34.5 x 19.0 mm, 3.81 g, 1067 s
- **All 22 bores run across the layers** in every orientation that is any good
  (best is -Z, 237 mm2 support, 95 layers): 8 x Ø2.40, 8 x Ø4.84, 4 x Ø5.22,
  2 x Ø6.00. This is an L-bracket with a horn pattern and a bearing boss on
  **both** legs, so the two hole axes are perpendicular and no single build
  direction can put both up the axis. Ream the Ø6.00 bearing seats.
- Exact wall 0.800 mm = exactly two perimeters, no margin, at (17.52, -17.53, 7.20);
  p1 0.920 confirms it is a real wall, not a sliver.

### ankle-left / ankle-right — 39.5 x 36.5 x 25.5 mm, 6.18 g each, ~1315 s
- **The Ø15 + Ø14 bearing seat runs across the layers** (+Y, 183 layers, 163 mm2
  support — by far the best of the six). A bridged Ø15 comes out oval and
  undersize at the top. **Ream it, or the 15x10x3 bearing will not seat.**
- 13 bores total, **all** across the layers here: 5 x Ø2.20, 5 x Ø4.40,
  1 x Ø5.00, plus the Ø14/Ø15 pair.
- Exact 0.234 mm at (±32.5, 22.60, 0.92) is a sliver; p1 1.202 mm — no real
  thin wall.
- Slicer flag: "floating regions - enable supports". Sliced from the **vendor
  mesh**, not our rebuild.

### foot-left / foot-right — 40.1 x 54.0 x 16.9 mm, 13.35 g each, ~1972 s
- **870 mm2 of support** on its side (±X, 201 layers) — the second-worst in the
  set, and every other direction is worse (the flattest, ±Z, needs 1274-1460).
  The 10-rib comb bottom and the two snap fingers are the cost.
- **Real sub-millimetre material**: p1 0.263 / 0.324 mm, p5 1.06 / 1.12 mm. The
  exact 0.015 mm reading is the bottom sole chamfer at z = -16.65 and is
  cosmetic; the p1 is the comb.
- 1 x Ø1.60 M2 pilot + 1 x Ø3.00, both across the layers in this orientation.
  Drill and tap the Ø1.60 after printing.
- Heaviest single part in the set. Sliced from the **vendor mesh as shelved**.

### sole-left / sole-right — 41.1 x 54.0 x 12.9 mm, TPU, 7.07 g each, ~2494 s
- **The slowest parts in the set** — 2497 s each, more than the 83 mm
  power-support, because TPU is printed slow.
- 274 mm2 support, 204 mm2 bed, on its side (-Y, 270 layers). The farm printed
  them "sole tread face down, dead flat" instead and the slicer raised no
  warning; that is a defensible different call and it is the tread finish, not
  the support number, that should decide.
- No holes. Wall 1.232 exact, p1 1.316 — the soundest walls of the twenty.
- Sliced from the **vendor mesh as shelved**.

### motor-support — 73.5 x 54.2 x 18.8 mm, 9.20 g, 1265 s
- **836 mm2 of support and 368 layers** standing on its 73.5 mm edge — that is
  the best of six, and the flat option (±Z, 95 layers) costs 1077-1287 mm2.
  There is no cheap orientation for this frame.
- **Real thin material**: p1 0.530 mm. The exact 0.008 mm at (-28.95, -8.56, 6.68)
  is a knife-edge.
- 4 x Ø2.70 across the layers; the Ø17.65 lens tube runs up the axis.
- Slicer flag: "floating cantilever - enable supports". Sliced from the
  **vendor mesh as shelved**.

### neck-pitch-bracket — 35.0 x 18.0 x 27.7 mm, 4.38 g, 1185 s
- 146 mm2 support in +Y (90 layers), less than half the naive upright answer.
- **Real thin material**: p1 0.339 mm, p5 1.064 mm; exact 0.376 mm at
  (-14.10, -8.79, -21.87).
- 19 bores, 15 of them across the layers here: 12 x Ø2.20, 4 x Ø4.40 (axial),
  3 x Ø6.00. Ream the Ø6.00 bearing seat.
- Slicer flag: "floating regions - enable supports". Sliced from the
  **vendor mesh as shelved**.

### neck-plate — 2.0 x 20.0 x 11.0 mm, 0.55 g, 127 s
- Zero support, 11 layers, 200 mm2 of bed, all 4 x Ø2.30 up the build axis.
- 0.850 mm wall (p1 0.863) — just over two perimeters. Keep 2 perimeters.
- Smallest part in the set; print it with something else.

### yaw-roll-motion — 34.0 x 35.9 x 22.5 mm, 4.71 g, 933 s
- **The one part with a genuinely sub-two-perimeter wall**: exact 0.750 mm at
  (8.749, 8.021, 17.0), and p1 0.850 mm says it is local rather than pervasive.
  0.750 mm is 1.9 perimeters — the slicer will either thin the extrusion or
  drop a wall there. **Fix the model or accept a weak spot; do not print it and
  hope.**
- 207 mm2 support in -Z (113 layers).
- **10 bores across the layers**, including the **Ø12.00** — bridged and oval
  if it is a bearing seat.
- Slicer note: "sliced AS MODELLED - auto-orient (-100) crashed the slicer on
  this mesh". The gram figure is therefore for a different orientation than the
  one recommended here. Sliced from the **vendor mesh as shelved**.

---

## power-support — the full risk list

54.466 x 17.000 x 83.130 mm, PLA, **13.15 g / 2302 s sliced** (from OUR
rebuild, not a vendor mesh), 416 layers at 0.2 mm upright. `printability` = OK
(fits, wall exactly at the floor). This is the part the drawing has to carry,
and it has seven distinct print risks.

**1. Printed upright it balances on the latch tongue's tip — 10.64 mm2.**
MEASURED: in the +Z build the *entire* bed contact is **two facets**, x
-5.017..+5.017, y 25.000..26.060, at z = -26.186 — exactly the latch tongue's
`2 x TONGUE_HW x TONGUE_T = 10.034 x 1.060 mm` from `cad/part.py`. The next
material is **3.7 mm above the bed** (the plate bottom at z = -22.483, 59.6 mm2
of flat down-face). An 83 mm tall, 13 g part on a 10.6 mm2 foot will come off
the plate, and the foot is the one feature that must survive as a spring.
*This is the single most important note on the drawing.*

**2. There is no good orientation, only a choice of which problem to buy.**
All six measured, elevated `beta<30` area / bed contact:

| build dir | support mm2 | bed mm2 | height | layers |
|---|---|---|---|---|
| **+Z (upright)** | **969** | **10.6** | 83.1 | 416 |
| -Z (inverted) | 1027 | 0.9 | 83.1 | 416 |
| ±X (on edge) | 1710-1712 | 26.1 | 54.5 | 273 |
| -Y (back down) | 3190 | 249 | 17.0 | 85 |
| +Y (face down) | 3444 | 37 | 17.0 | 85 |

The farm's own rule for this part reads *"auto-orient: tall cradle laid on its
back to cut supports"* — and the measurement says laying it on its back
**triples** the support (969 → 3190 mm2), because the plate's back face is held
7 mm off the bed by the two mounting flanges and the whole 54 x 83 mm plate
then floats. It buys 24x the bed contact for 3.3x the support. Both numbers are
here; the drawing must state which was chosen and why. The slicer independently
flagged this part **"floating regions - enable supports"**.

**3. The head shelf is a 437 mm2 cantilevered ledge.** MEASURED by z band, +Z
build — where the 969 mm2 of support work actually is:

| z band (mm) | support mm2 | of which flat (beta<10) | what it is |
|---|---|---|---|
| 48 .. 54 | **437.0** | 428.2 | head shelf underside at z = 49.017, 46 mm wide x ~8 mm deep, out to y = 35, plus the two screw-pin legs and webs |
| 36 .. 42 | 151.8 | 148.7 | **upper mounting flange** underside at z = 40.73 (y 18..27) + gusset |
| 12 .. 18 | 153.6 | 153.6 | **lower mounting flange** underside at z = 14.33 + gusset |
| -18 .. -12 | 97.6 | 73.5 | rail bottom ends (z -16.75), cell lips (z -16.678), the latch slit tops (z -12.917) |
| -24 .. -18 | 68.3 | 59.6 | **the plate's own bottom edge** (z = -22.483) — floating 3.7 mm up, see risk 1 |
| 6 .. 12 | 19.9 | 8.5 | battery-face bosses / window lower edge (x ±11, y 25..29) |
| 24 .. 30 | 8.1 | 8.1 | upper cell lip underside (z 20.022, y 31.3..32.8) |
| 18 .. 24 | 5.7 | 5.7 | upper cell lip |
| 54 .. 60 | 12.5 | 4.7 | head top / notch |

None of these bridge between two walls — they are all one-sided ledges off the
plate. They need support, and support under the head shelf and both flanges
will leave witness marks on faces that mate with the trunk base and the banana
PCB locker.

**4. The 0.466 mm latch slits are narrower than one extrusion.**
`SLIT_W = 0.466` in `cad/part.py`. The two slits are the *only* thing separating
the sprung tongue from the plate — they run from z = -12.917 down through the
plate bottom. A 0.4 mm nozzle laying one line into a 0.466 mm gap leaves
0.066 mm of air, and gap-fill closes what it cannot fit a line into. **If the
slits fuse, the tongue is not a spring, it is part of the plate, and the
battery does not clip in.** This is a geometry problem, not a slicing one:
0.466 mm is a mesh-derived dimension copied from Pollen's decimated STL, and it
wants to be widened to at least one clean nozzle width (0.5-0.6 mm) before
anyone prints this. Verify with a slice preview before committing a plate.

**5. The sprung latch tongue is thin, cantilevered, moving — and it is also the
foot.** 10.034 mm wide x **1.060 mm thick** (2.6 perimeters), free length
13.27 mm from the slit top at z = -12.917 to the tip at z = -26.186, with five
R0.4 grip ridges and a hook that stands 5.31 mm proud (ramp y 26.0 → 31.31 over
z -26.186 → -22.1). Printed +Z the layer lines run **across** the bending axis,
so every flex works a layer bond: this is the delamination/fatigue candidate of
the whole robot. The hook's ramp face measures **35.5 deg to the plate** — above
the 30 deg threshold, so it needs no support, but it is in the 45 deg band and
will show stair-stepping on the ramp the battery slides over.

**6. Ten M2 tap holes, all across the layers.** MEASURED axes: **8 x Ø1.60 x 4.0
deep** on Y (the two stadium bosses, 4 each, for the battery-contact PCB) and
**2 x Ø1.55 x 7.8 deep** on Y (the Ø3.9 screw pins the banana PCB locker bolts
to). In the +Z build every one of them is horizontal: the top arc bridges, and
a Ø1.55 bore this small closes further on any FDM machine. `cad/part.py` calls
them tapping holes; in practice **drill to tapping size and form-tap after
printing, or use M2 heat-set inserts.** Do not expect a threadable hole off the
bed. (No shrinkage figure is quoted here because nothing in this repo has
measured one — the farm's printer is the authority.)

**7. The Ø2.50 flange holes are the only ones that print clean.** 4 hole
records on the **Z** axis in 2 coaxial groups (`of_group = 2`, span 28.34 mm) —
i.e. two bolt holes at x = ±9.5, y = 20.5, each passing through both 1.94 mm
flange lips at z = 15.3 and z = 41.7. In the +Z build they run up the build
axis: round, slightly undersize, no bridge. They mate with the trunk base's
Ø2.30 holes.

**8. Wall exactly at the floor, no margin.** Exact thinnest wall **0.800 mm** at
(-1.672, 26.217, -16.945) — precisely two 0.4 mm perimeters — and the rays
agree it is a real wall (min 0.7998, **p1 0.7998**, p5 1.175, median 2.000), not
a chamfer sliver. Any nozzle bigger than 0.4, or a slicer that drops to one
perimeter on thin features, and that wall is air. **0.4 mm nozzle, >= 2
perimeters, no exceptions.**

**Verdict: PRINTABLE-WITH-CARE**, and the two items that are model problems
rather than print problems — the **0.466 mm slit** and the **10.6 mm2 foot** —
should be resolved in CAD before this part is drawn for manufacture.

---

## The drawing note block

Every rebuilt part's sheet should carry the ones that apply to it.

1. **FDM, PLA, 0.4 mm nozzle, 0.2 mm layer, minimum 2 perimeters.** The
   two-perimeter floor is 0.80 mm and four parts sit at or under it
   (power-support 0.800, hip-bracket 0.800, neck-plate 0.850,
   **yaw-roll-motion 0.750 — under**).
2. **Build direction is a dimension.** State it on the sheet. It is not the
   part's Z: measured, the best direction is +Z on only 3 of 20 parts.
3. **A bore across the layers is not the bore you drew.** Its top arc bridges
   and it prints oval and undersize. **Ream after printing**: ankle Ø15/Ø14,
   hip-bracket and neck-pitch-bracket Ø6.00, yaw-roll-motion Ø12.00,
   shin Ø6.00/Ø5.50, upper-leg Ø5.37.
4. **Small tapped holes are not tapped by the printer.** Every Ø1.55 / Ø1.60
   (M2) — power-support x10, foot x1 — must be drilled to tapping size and
   form-tapped, or fitted with an M2 heat-set insert. No shrinkage allowance is
   given here because none has been measured on this farm.
5. **Support is required on 15 of 20 parts**, up to 969 mm2 (power-support) and
   870 mm2 (feet). Support witness marks land on mating faces — say on the sheet
   which face must stay clean.
6. **Brim the small-footed parts.** shin (3.6 mm2), power-support (10.6 mm2),
   foot L/R (43 mm2) do not hold the plate on their own.
7. **Thin plates lie flat.** rigidity-plate (1 mm, 5 layers), neck-plate (2 mm,
   11 layers), trunk-base and bearing-roll (3 mm, 15 layers). Standing them on
   edge is hundreds of layers of a single wall.
8. **A sub-0.80 mm reading is not automatically a thin wall.** Quote the exact
   figure with the ray p1 beside it, as this document does, or the note is
   noise.
9. **Machining: not applicable.** `machining.plan` returns CANNOT DETERMINE on
   all 20 because *"fdm is ADDITIVE"*. If a part is ever moved to a subtractive
   process it must be re-planned, not assumed.

---

## What is still NOT measured

- **Bridge vs. island.** Support area is an upper bound; nothing here tells a
  spanning bridge from a floating ledge.
- **Hole shrinkage.** No measurement of printed-vs-nominal bore diameter exists
  in this repo. That is why every note says "ream/tap", never "add 0.2 mm".
- **Warp, first-layer adhesion, TPU stringing.** Process, not geometry.
- **Non-axis-aligned orientations.** Only the six axis-aligned build directions
  were measured. A tilted orientation could beat all six and was not tried.
- **Twelve of the twenty were sliced from the VENDOR mesh, not our rebuild**
  (ankle L/R, foot L/R, hip-bracket, motor-support, neck-pitch-bracket,
  neck-plate, sole L/R, rigidity-plate, yaw-roll-motion): their grams and
  seconds are Pollen's mesh's, not ours. The other eight (banana-pcb-locker,
  bearing-roll, power-support, shin, trunk-base, upper-leg L/R, yaw2roll) were
  sliced from our own rebuild. The rebuilds match the reference to p95 <= 1 mm,
  but a matching part is not the same STL and the slicer read the other file.

## Reproduce

```sh
export CE_TRIAD_ROOT="$PWD:$(dirname $(dirname $PWD))"
ce-cad/bin/cad tools/dfm_rebuilt.py     # solid + mesh DFM  -> out/dfm/dfm-rebuilt.json
ce-cad/bin/cad tools/dfm_orient.py      # self-check, then the orientation block
ce-cad/bin/cad tools/dfm_rows.py        # the rows above + the power-support breakdown
python3 tools/dfm_verify_md.py          # read the table above BACK and check every cell
```

`tools/dfm_verify_md.py` re-parses the summary table the way a reader does and
re-derives all ten columns from `out/dfm/dfm-rebuilt.json` and
`out/print/slice.json`, including re-applying the verdict rule. It currently
reports **20 rows, reads back clean**. It was broken on purpose first, seven
ways, and bit on every one: a gram figure nudged, a support area nudged, a
build direction flipped, a layer count wrong, a thin wall laundered upward, a
verdict upgraded to PRINTABLE, and a whole row deleted.

`microduck-ankle-left` was re-measured on its own: in the 20-part run its
`export_stl` hit a full disk (FreeCAD's own cache failed to write in the same
second) and its mesh block was missing. Recorded in the JSON as `$rerun`.
