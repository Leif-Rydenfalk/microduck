# PRINT — the H2D at Black Ark: head first, then down, one compact plate

*2026-09-08, sent from the print farm (localhost:8770) as job-0001. Leif, verbatim: "start with printing parts of the head not the body", "use the h2d printer", "make it way more compact. remember no brim", "if youre able to print more of the body do that also on the same plate … from the head going down so we can actually build more and more connected together."*

## What is on the plate — 24 pieces, 7 h 10 m, 274 g (OrcaSlicer's own numbers)

Order of inclusion followed the joint tree in `ce-assemblies/microduck/current/joints.json`: head (11 pieces), trunk (5), hips (6), then the upper legs one by one until the plate was full. **On the plate:** top-head-shell, bottom-head-shell, jaw, face-part, motor-support, yaw-roll-motion, neck-pitch-bracket, eye-ring, m12-lens-holder, neck-plate ×2 · trunk-shell-left, trunk-shell-right, power-support, trunk-base, banana-pcb-locker · yaw2roll ×2, bearing-roll ×2, hip-bracket ×2 · upper-leg-left, upper-leg-rigidity-plate ×1.
**Not on it (next plate):** upper-leg-right, upper-leg-rigidity-plate ×1, shin ×2, ankle-left/right, foot-left/right (PLA) and the four TPU parts (no TPU loaded anywhere).

| part | x | y | footprint | height | rotated |
|---|---|---|---|---|---|
| top-head-shell | 7.0 | 7.0 | 122.7 x 91.8 | 46.3 | 90° |
| bottom-head-shell | 143.7 | 7.0 | 116.7 x 91.8 | 20.1 | 90° |
| jaw | 3.0 | 108.8 | 68.7 x 91.4 | 29.4 | 90° |
| motor-support | 7.0 | 210.2 | 54.2 x 73.5 | 18.8 | 90° |
| face-part | 71.2 | 206.2 | 44.6 x 87.7 | 12.5 | 90° |
| yaw-roll-motion | 81.7 | 112.8 | 34.0 x 35.9 | 22.5 |  |
| eye-ring | 77.7 | 158.7 | 30.0 x 30.0 | 9.5 |  |
| neck-pitch-bracket | 274.4 | 7.0 | 18.0 x 40.2 | 40.2 | 90° |
| m12-lens-holder | 3.0 | 299.9 | 24.0 x 16.0 | 14.8 |  |
| neck-plate | 33.0 | 293.7 | 11.0 x 20.0 | 2.0 | 90° |
| neck-plate | 50.0 | 293.7 | 11.0 x 20.0 | 2.0 | 90° |
| power-support | 125.8 | 162.7 | 54.5 x 83.1 | 17.0 | 90° |
| trunk-shell-left | 125.7 | 108.8 | 80.8 x 41.3 | 34.0 |  |
| trunk-shell-right | 212.5 | 108.8 | 80.8 x 41.3 | 32.0 |  |
| trunk-base | 121.8 | 255.8 | 36.0 x 57.0 | 3.0 | 90° |
| banana-pcb-locker | 163.8 | 255.8 | 6.6 x 54.0 | 3.8 | 90° |
| bearing-roll | 270.4 | 57.2 | 23.0 x 40.0 | 3.0 | 90° |
| bearing-roll | 176.4 | 255.8 | 23.0 x 40.0 | 3.0 | 90° |
| hip-bracket | 205.4 | 156.1 | 32.5 x 19.0 | 34.5 |  |
| hip-bracket | 243.9 | 156.1 | 32.5 x 19.0 | 34.5 |  |
| yaw2roll | 190.3 | 181.1 | 20.5 x 23.0 | 25.8 |  |
| yaw2roll | 190.3 | 210.1 | 20.5 x 23.0 | 25.8 |  |
| upper-leg-left | 209.4 | 243.1 | 47.7 x 61.0 | 28.0 | 90° |
| upper-leg-rigidity-plate | 216.8 | 181.1 | 58.0 x 45.0 | 1.0 | 90° |

Bed used: 300 × 320 (the H2D's left-extruder reach), 3 mm margin, **6 mm gap, +4 mm around every part that gets supports**. Footprint 62 969 mm² of 92 316 available. Files: `plates/H2D-COMPACT/microduck-head-down-compact.3mf` (the arranged plate), `.gcode.3mf` (what the printer got, stamped printer_model_id O1D), `layout.json`, `orca-command.txt`.

## Machine and settings — every one read off the machine or the file, not assumed

| | |
|---|---|
| printer | Bambu Lab H2D "H2D AMS HT", 0947BJ610900152, 192.168.1.14, Black Ark / Trouble Maker, Shenzhen |
| nozzle | **0.6 mm HS01** — read from the MQTT report (`nozzle_diameter`). The farm sliced for 0.4 by default; it now follows the fitted nozzle |
| profiles | `Bambu Lab H2D 0.6 nozzle` · `0.18mm Balanced Quality @BBL H2D 0.6 nozzle` · `Bambu PLA Basic @BBL H2D 0.6 nozzle` (OrcaSlicer 2.4.2 — BambuStudio's CLI refuses the H2D with -66) |
| filament | AMS slot 2, black PLA, RFID-verified, 41 % left (~410 g for a 274 g plate). Slots 0/1 are "set by hand", amount unknown — the farm now takes `preferred_tray` |
| plate | Textured PEI, first layer 0.3 mm / 0.62 mm wide, bed 55 °C |
| brim | **no_brim, width 0** — the standing rule |
| supports | normal(auto), on build plate only. tree(auto) refused this plate ("Potentially lost branch", critical) |
| orientation | fixed by me — arrange/orient OFF in the slicer. `stl/oriented-repaired/PLA` is the print pose; `stl/PLA` is the MJCF model pose and must not be sliced as-is (1 mm plates on edge) |

## Two things that were wrong before, now on record

**Adhesion.** `tools/plate_for_printer.py` records it: two prints detached and spaghettied at layer 5 and layer 25, the eye-ring and the lens holder, and the fix chosen then was a 5 mm brim (`--brim`). That contradicts the workshop rule. This plate has no brim; its first layer is a 0.6-nozzle 0.3 mm layer, which is a far bigger foot than the 0.4/0.2 mm those two failed on. If a small part lifts again the answer is a raft or a different sheet, not a brim.

**Orientation.** The plate 3MF from 2026-09-02 (`plates/PLA/microduck-PLA.3mf`) has the top-head-shell on its side (116 mm tall) and the jaw standing on its 28 mm face — BambuStudio's auto-orient, not a choice. PRINT.md's rules (dome up, beak underside down, 8 mm plate flat, cradle on its back) are what is on this plate.

## Known slicer warnings — printed through on purpose

OrcaSlicer's validity check aborts on "empty layer" bands in seven of the vendor meshes (bottom-head-shell 17.0–19.0 mm, jaw 28.4–28.9, neck-pitch-bracket 36.8–37.6, eye-ring 6.2–6.6, bearing-roll 1.0–2.1, banana-pcb-locker 1.9–2.8, trunk-base). admesh finds every one of those meshes watertight; the bands are features thinner than a 0.62 mm line (ribs, lips), which a 0.6 nozzle cannot print in any case. The plate was sliced with `--no-check` (it must be the FIRST argument, or Orca ignores it); the toolpath-conflict check was run separately on the same layout and found none. Expect those slivers to be missing on the printed parts.

## What changed in the farm for this (ce-workshop/ce-print-scheduler)

- `slicer.choose()` follows `slice_overrides.nozzle` / the machine's reported nozzle for all three profiles; `process_profile()` knows the "0.6 nozzle" file suffix.
- `bambu.status()` reports `nozzle` and `nozzle_type`; `bambu.ams_maps()` honours a human `preferred_tray`.
- The X1 Carbon is **disabled, note "UNDER MAINTENANCE"** at Leif's request.
- Open defect, not fixed: the farm's build arranges with `--arrange 1 --orient 1` and did not notice Orca overflowing 22 parts onto two plates (it sent plate 1 only), and it re-orients parts. This plate was hand-arranged and inserted with `queue.add`; a PLATE upload still has no build path.
