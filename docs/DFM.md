# DFM — Microduck rebuilt parts (FDM print check)

Measured 2026-09-02 with `ce-cad`: `cecad.printed.printability` (bed fit,
orientation, thinnest wall vs. the two-perimeter minimum, filament),
`cecad.dfm.measure` (volume, bbox, wall, verdict roll-up), and
`cecad.machining.plan` (subtractive plan). Bed = `prusa_mk4`
(250x210x220 mm), nozzle 0.4 mm, layer 0.2 mm, material PLA.

**What each column is, and is not.**

- **Thinnest wall** is MEASURED off the finished solid by `inspect.thinnest_wall`
  (ray + exact pass). The two-perimeter minimum is `2 x 0.4 = 0.80 mm`. A wall
  read **below 0.80 mm is almost always a knife-edge** — a chamfered or tapered
  face that tapers to a tangent line — not a structural wall. Confirmed on
  `microduck-foot-left`: the 0.015 mm reading is at `z = -16.7` on a 16.9 mm-tall
  part, i.e. the bottom chamfer where the sole meets the ground. The slicer
  rounds such a tip off; it is a cosmetic edge, not a load path. It is still
  reported honestly, because the wall check cannot tell a sliver from a wall and
  will not launder the number.
- **Filament g is MODELLED** (shell + infill over measured surface area and
  volume), NOT sliced. The print farm's slicer is the authority on grams and
  was not asked here (`slice=False`); `dfm.measure` refuses the raw
  solid-volume proxy outright (measured 3.1x over on the demo part). Treat the
  gram figures as a rough size ranking only.
- **Overhang / bridging is NOT measured** — no tool in `ce-cad` computes
  overhang angle, and `printability` says so explicitly. The bridging notes
  below are **DERIVED** from measured hole-axis directions against the natural
  upright print orientation: a hole whose axis is horizontal (perpendicular to
  the build Z) prints as a bridged bore — its top arc sags and it comes out
  undersize and out-of-round. Small tapped holes must be drilled/tapped after
  printing regardless; press-fit and bearing bores should be reamed.
- **Machining = CANNOT DETERMINE on every part is the CORRECT result.** No part
  declares a subtractive `process=`, so `machining.plan` refuses to plan one.
  These are FDM parts; the empty machining verdict confirms it rather than
  contradicting it.

## Summary table

| Part | Fits bed | Print orientation | Thinnest wall (mm) | Filament g (modelled) | Print risks | Verdict |
|---|---|---|---|---|---|---|
| power-support | yes | upright, Z-up (83 mm tall) | 0.80 (= 2 perim) | 13.4 | 14 M2 holes on Y (horizontal): 8x O1.60 + 2x O1.55 tapped print undersize AND bridge; sprung latch tongue (thin + moving); tall/slender 54x17x83 | PRINTABLE-WITH-CARE |
| shin | yes | upright, Z-up (58 mm tall) | 0.028 (knife-edge) | 3.7 | 15 holes all on X (horizontal) O2.2-6.0 bridge; tall thin section 8x20x58; edge sliver | PRINTABLE-WITH-CARE |
| trunk-base | yes | flat, 3 mm plate | 1.00 | 1.8 | flat 57x36x3 plate; all 6 holes vertical (O2.3, O19) print clean; 1.0 mm min wall around holes | PRINTABLE |
| banana-pcb-locker | yes | upright | 0.921 | 0.6 | small thin locker 54x3.8x6.6; 2x O2.17 on Y bridge; 0.92 mm wall | PRINTABLE-WITH-CARE |
| bearing-roll | yes | flat, 3 mm plate | 0.900 | 0.8 | O19 bore on Y bridges — REAM if it seats a bearing; 4x O2.2 on Y; 3 mm thin; 0.9 mm wall | PRINTABLE-WITH-CARE |
| yaw2roll | yes | upright | 0.198 (sliver) | 3.1 | 0.198 mm edge sliver; 8 horizontal holes O2.05-5.5 bridge | PRINTABLE-WITH-CARE |
| upper-leg-left | yes | upright, Z-up (61 mm) | 0.024 (knife-edge) | 4.8 | knife-edge sliver; 2x O5.37 on X bridge (hip pivot — ream) | PRINTABLE-WITH-CARE |
| upper-leg-right | yes | upright, Z-up (61 mm) | 0.024 (knife-edge) | 4.8 | knife-edge sliver; 2x O5.37 on X bridge (hip pivot — ream) | PRINTABLE-WITH-CARE |
| upper-leg-rigidity-plate | yes | MUST lay flat (1 mm thick) | 1.00 | 0.9 | 1 mm-thin flat plate — lay flat (5 layers), do NOT stand on edge; warp/flex risk; O19 + 4x O2.2 through 1 mm | PRINTABLE-WITH-CARE |
| hip-bracket | yes | upright | 0.80 (= 2 perim) | 4.0 | 22 holes all horizontal (X/Y) O2.4-6.0 bridge; dense; 0.80 mm min wall borderline | PRINTABLE-WITH-CARE |
| ankle-left | yes | upright | 0.234 (sliver) | 6.3 | O15 + O14 bores on X bridge — REAM (bearing/press-fit); 4x O2.2 tapped on X; edge sliver | PRINTABLE-WITH-CARE |
| ankle-right | yes | upright | 0.234 (sliver) | 6.3 | O15 + O14 bores on X bridge — REAM (bearing/press-fit); 4x O2.2 tapped on X; edge sliver | PRINTABLE-WITH-CARE |
| foot-left | yes | upright | 0.015 (knife-edge, bottom chamfer) | 13.9 | bottom-chamfer sliver (cosmetic); 1x O1.60 tapped on Z (blind, 5.5 deep) — drill/tap | PRINTABLE-WITH-CARE |
| foot-right | yes | upright | 0.015 (knife-edge, bottom chamfer) | 13.9 | bottom-chamfer sliver (cosmetic); 1x O1.60 tapped on Z (blind, 5.5 deep) — drill/tap | PRINTABLE-WITH-CARE |
| sole-left | yes | flat | 1.232 | 7.3 | clean pad, no holes; 1.23 mm min wall | PRINTABLE |
| sole-right | yes | flat | 1.232 | 7.3 | clean pad, no holes; 1.23 mm min wall | PRINTABLE |
| neck-pitch-bracket | yes | upright | 0.376 (sliver) | 4.2 | 10 horizontal holes O2.2/O6.0 (O2.2 tapped on X) bridge; edge sliver | PRINTABLE-WITH-CARE |
| neck-plate | yes | MUST lay flat (2 mm thick) | 0.850 | 0.5 | 2 mm-thin plate 2x20x11 — lay flat; 4x O2.3 on X bridge; 0.85 mm wall | PRINTABLE-WITH-CARE |

All 18 parts FIT the bed and are FDM-printable. Machining verdict is
CANNOT DETERMINE on all 18 (no subtractive process declared) — the correct
answer for FDM parts.

## Per-part print risks

### power-support  (54.5 x 17.0 x 83.1 mm, PLA, 13.4 g, 416 layers)
- **14 fastener holes, all on the Y axis** (horizontal in the natural Z-up
  print): 8x O1.60 x 4.0 deep + 2x O1.55 x 7.8 deep (M2 tapped) + 2x O2.50.
  The O1.55/O1.60 tapped holes **print undersize on any FDM machine** (first
  layers of a small horizontal bore close in) AND their tops **bridge**. Model
  intent is tap-into-plastic; in practice: print, then drill to size and
  form-tap / heat-set. Do not expect a threadable hole straight off the bed.
- **Sprung latch tongue** — a thin, cantilevered, *moving* feature. FDM layer
  lines run across the flex axis; the tongue is a fatigue/delamination risk and
  the single most fragile feature on the part. Print with the tongue's bending
  plane in-plane if possible; consider higher wall count / anneal; expect it to
  be the first thing that breaks.
- **Tall, slender body** (17 mm deep, 83 mm tall, aspect ~5:1) — needs a brim /
  good bed adhesion; watch for wobble and ringing near the top.
- Two PCB bosses and flanges print fine.
- Thinnest wall 0.80 mm = exactly two 0.4 mm perimeters — the acceptable floor,
  no margin. Any thinner and it would not print as a wall.
- **Verdict: PRINTABLE-WITH-CARE.** It prints; the M2 holes and the sprung
  tongue are the two things a drawing note MUST call out.

### shin  (8.0 x 20.0 x 58.0 mm, 3.7 g)
- Thinnest wall 0.028 mm is a knife-edge, not a wall.
- 15 holes all on X (horizontal), O2.2-6.0 — tops bridge; ream the pivots.
- Tall thin blade (8 mm thick, 58 mm tall) — brim, watch adhesion.

### trunk-base  (57 x 36 x 3 mm, 1.8 g)
- Flat 3 mm plate; all 6 holes vertical (O2.3, O19) — clean. Lowest-risk part.
- 1.0 mm min wall around holes — fine on a flat plate.

### banana-pcb-locker  (54 x 3.8 x 6.6 mm, 0.6 g)
- Small thin PCB locker; 0.92 mm min wall; 2x O2.17 on Y bridge.
- Tiny and slender — handle gently after printing.

### bearing-roll  (23 x 3 x 40 mm, 0.8 g)
- O19 bore on Y bridges — **ream if it seats a bearing/roll shaft.**
- 4x O2.2 on Y; 3 mm-thin plate; 0.9 mm wall.

### yaw2roll  (23 x 25.8 x 20.5 mm, 3.1 g)
- 0.198 mm sliver edge; 8 horizontal holes O2.05-5.5 bridge.

### upper-leg-left / upper-leg-right  (28 x 47.7 x 61 mm, 4.8 g each, mirror pair)
- Knife-edge sliver (0.024 mm).
- 2x O5.37 on X (hip pivot) bridge — ream for a clean pivot fit.
- 61 mm tall — brim recommended.

### upper-leg-rigidity-plate  (1 x 45 x 58 mm, 0.9 g)
- **1 mm-thin flat plate — orientation matters most here.** Lay it FLAT on the
  bed (1 mm = 5 layers); do NOT print it standing on edge (the tool's bbox
  "upright" reading would be 291 layers of a 1 mm wall on its side — it would
  fail). Warp/flex risk; brim.
- O19 + 4x O2.2 through the 1 mm thickness.

### hip-bracket  (32.5 x 34.5 x 19 mm, 4.0 g)
- 22 holes, all horizontal (X and Y), O2.4-6.0 — every one bridges at the top;
  ream pivots, drill/tap the small ones.
- 0.80 mm min wall — borderline (two perimeters, no margin).
- Densest part; check clearances between neighbouring bores.

### ankle-left / ankle-right  (39.5 x 36.5 x 25.5 mm, 6.3 g each, mirror pair)
- **O15 and O14 bores on X bridge — REAM** (these seat bearings / press-fits;
  a bridged O15 comes out oval and undersize).
- 4x O2.2 tapped on X; 0.234 mm edge sliver.

### foot-left / foot-right  (40.1 x 54 x 16.9 mm, 13.9 g each, mirror pair)
- 0.015 mm reading is the bottom sole chamfer (confirmed at z = -16.7) —
  cosmetic knife-edge, not a wall.
- 1x O1.60 tapped on Z, blind 5.5 deep — drill/tap after printing.
- Largest single parts by mass; long print.

### sole-left / sole-right  (41 x 54 x 12.9 mm, 7.3 g each, mirror pair)
- Clean pads, no holes, 1.23 mm min wall. Low risk. Print in a grippy /
  flexible filament (TPU) if these are the ground-contact soles.

### neck-pitch-bracket  (35 x 18 x 27.7 mm, 4.2 g)
- 10 horizontal holes O2.2/O6.0 (O2.2 tapped on X) bridge; 0.376 mm sliver.

### neck-plate  (2 x 20 x 11 mm, 0.5 g)
- **2 mm-thin plate — lay flat.** 4x O2.3 on X bridge; 0.85 mm wall. Tiny.

## Recurring risks (drawing-note block)

1. **Small tapped holes do not print to size.** Every O1.55 / O1.60 (M2) and
   O2.05-O2.3 hole prints undersize and, when horizontal, bridges. Note on the
   drawings: *drill to tapping size and form-tap after printing; heat-set inserts
   preferred for M2 into PLA.*
2. **Horizontal bores that carry a bearing or press-fit must be reamed** —
   ankle O14/O15, upper-leg O5.37, bearing-roll/rigidity-plate/trunk-base O19,
   shin/hip pivots. A bridged bore is oval and undersize at the top.
3. **Thin flat plates (rigidity-plate 1 mm, neck-plate 2 mm) must be laid flat**,
   not printed on edge. Brim for adhesion; expect some warp.
4. **Sub-0.80 mm "walls" are knife-edges** (chamfers/tapers), not structural —
   they slice fine. The one true two-perimeter floors are power-support and
   hip-bracket at 0.80 mm: no margin, keep 0.4 mm nozzle and >=2 perimeters.
5. **power-support's sprung latch tongue** is the one genuinely fragile,
   moving printed feature in the set — thin, cantilevered, cycled. Highest wall
   count, print flat to the flex plane, consider annealing.
