# TPU mouth candidate — 2026-09-08

Preferred artifact: `sliced/microduck-mouth-tpu.gate.gcode.3mf`.
SHA-256: `aeb41038511869adc8c1dd685a5f27266109cbf16bfa9cf574f0ee8e66e72819`. **Offline validated; not sent.**

Both repaired source meshes remain geometrically unchanged apart from rigid pose and 0.0001 mm serialization. Each mesh is one watertight shell, with zero degenerate/duplicate triangles, nonmanifold/boundary/flipped edges. See `geometry-proof.json` and `meshdoctor.json` (do not use its legacy min_edge statistic as a dimension).

The original standalone failures were placement outside the bed: both source STLs had negative X/Y and arrangement was disabled. Repositioning resolves that error. Rendered first layers then exposed a 0.5 degree tilt in their broad faces. A 179.5 degree X rotation seats those measured planar faces, so both full seating faces extrude from the first layer. Earlier translated/flipped trials remain in the parent directory for comparison.

The actual preserved slicer log reports no empty layers or object conflicts. Strengthened validation passes motion parsing, every-layer extrusion, body-only object contiguity, embedded-mesh expected-layer coverage, air-layer sampling, and right-extruder reach. No terminal-resolution exception. 45 layers at 0.18 mm, first 0.3 mm; 13.89 g; estimated total 1 h 7 min 40 s. See `validation.txt`, `partgate-result.json`, and the retained `*.slice.log`.

I rendered and opened `mouth-toolpaths.png` from actual final G-code and `mouth-meshes.png` from the final archive. The first four layer plots show broad bed contact without the prior unsupported expansion. Layer checks establish sampled toolpath continuity; physical adhesion, flexible-material tuning and manufactured fit still require observation.

## Remaining requirements before manufacture

Actual stock must be confirmed as 1.75 mm TPU and its grade/profile verified. This candidate uses Generic TPU @BBL H2D, a right 0.6 mm nozzle, 240 C nozzle / 35 C textured bed and 3.2 mm³/s volumetric cap; these are candidate settings, not measurements of loaded stock. Project component records specify TPU without an authoritative grade. Local secondary research mentions 90–95A, which is not sufficient to claim loaded compatibility.

The official [H2D manual](https://csm.bblcdn.com/hub/4668d0ca43994ff3bff4b37f1a65c2e7.pdf) recommends the right toolhead for TPU. Generic soft TPU requires the applicable external/bypass route; it must not be assumed compatible with ordinary automatic AMS feeding. The scheduler's current project-file sender explicitly sets `use_ams=True`, so an explicit verified feed route is required before this candidate can be sent. Live material/nozzle checks remain unmeasured. Rigid HEAD-V9 currently occupies the printer; completion, physical inspection and bed clearance precede a separate TPU job.
