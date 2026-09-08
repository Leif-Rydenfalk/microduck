# HEAD-V9 — print-layer and live-printer validation PASS

Final file: `microduck-head-v9.gcode.3mf`
SHA-256: `58fac4ca6baee18484bba3afbc393d83fad1821075ffe1d9557740a15a0254b4`

The coordinating operator ran the strengthened validator against this exact
file and the live H2D. `live-validator.txt` reports **PASS**, including fitted
0.4/0.6 mm Standard nozzles, PLA availability, reachable extrusion, contiguous
model layers and unsupported-extrusion checks. There is **no terminal L6T
warning** in this candidate. This report does not claim physical print success.

## What changed

- Shared 3MF vertex indices restore the formerly omitted eye-ring body and
  bottom-shell layers. The exporter fix is in `tools/indexed_3mf.py`, used by
  `tools/compact_plate.py`, with three regression tests.
- The jaw prints on its side to eliminate its unsupported second-layer expansion.
- The neck bracket is rigidly rotated +90 degrees around bed Y and moved into
  unused space at X150/Y120. Its thickness is now along Z: model layers 1–90
  include the final slab. No fit geometry was redesigned to remove the former
  0.118 mm terminal-slice omission.
- Six faces belonging to the yaw's extra coplanar zero-volume component were
  removed. `removed-faces-proof.json` proves no other oriented triangle was added
  or changed. Main-body volume remains 4708.3036 mm³. Winding-number probes at
  the component centroid and ±0.01 mm establish that neighborhood lies inside
  the main volume. Both original and cleaned standalone yaw slices passed the
  corrected diagnostic gate; all 112 model layers were compared. Maximum
  symmetric path-sample distance is 0.0319 mm at 0.05 mm sampling, within that
  sampling resolution. The A/B render was inspected; no unwanted paths appear.

## Independent measurements

A separate parser read this exact archive, including 240236 extrusion arcs:
344 layers from Z0.2 to Z68.8 mm, every increment 0.2 mm; no globally empty layer,
no extrusion/declared-height mismatch, and all 11 model-only intervals contiguous.
Support extrusion is excluded from the model-presence proof. Eye ring is layers
1–48, bottom shell 1–100, bracket 1–90, jaw 1–344. All 11 final meshes now have
one connected component, positive volume, watertight incidence and consistent
winding. These topology checks alone are not a manufacturing-success claim.

The fixed partgate preserved the full Orca log at
`microduck-head-v9-clean.gate.gcode.3mf.slice.log`; `partgate-result.json` confirms
`diagnostic_log_available=true`, no empty-layer diagnostics and no conflicts.
All original HEAD-V5 project-setting keys match, including Manual filament
mapping. Metadata restoration did not change actual G-code bytes.

Slicer estimate: **8 h 36 m 17 s, 142.76 g PLA** (partgate rounds to 142.8 g),
no brim. Exact images were rendered from the archive and inspected:

- `../../independent-codex-2026-09-08/v9-validation/exact-meshes.png`
- `../../independent-codex-2026-09-08/v9-validation/changed-parts-layer-proof.png`
- `../../independent-codex-2026-09-08/experiments/yaw-zero-volume-ab.png`

## Remaining limits: fit and strength are separate from print-layer proof

FreeCAD still reports tiny intersection diagnostics in bottom shell (one pair),
jaw (two) and yaw-roll (one), remeasured on this exact archive. Nearby actual
slice comparisons show continuous bottom/jaw walls with approximately 0.21 mm
centerline offsets, consistent with 0.42 mm line width. The yaw side's small
notch is locally smoothed: maximum contour-to-centerline distance about 0.468 mm.
Whether that local deviation is on a mating surface or within the required fit
tolerance is **CANNOT DETERMINE** without current interface evidence or a
physical mating test. No unsupported-extrusion or missing-layer failure was
detected there. See `v9-validation/intersection-functional-sections.png` and
`INTERSECTION-DISPOSITION.md` in the independent evidence folder.

The zero-volume component is resolved; the remaining microscopic intersections
have not been described as pristine geometry or as mechanically validated.
Fit, strength, adhesion, support removal quality, material behavior and the
completed physical product remain unverified. The old reconstruction BOM is
not evidence of current fit. Check the printed pieces against actual mating
hardware before treating the head as accepted production hardware.

At report handoff, the coordinating operator is awaiting physical bed-clearance
confirmation after the previous stopped job. This validation agent issued no
printer command and did not queue or send V9. The operator owns that final
physical step and subsequent print monitoring.
