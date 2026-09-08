# HEAD-V7 — offline print checks pass; not sent

Artifact: `microduck-head-v7.gcode.3mf`
SHA-256: `ea36330b828bebf04f9ba345363f623187125ec6429deab146529adc01399bc1`

The exact final file passes all strengthened offline blocking checks in
`strengthened-validator.txt`. Independent analysis separately measured:

- 344 actual layers, Z=0.2–68.8 mm, every step 0.2 mm.
- All 11 models have continuous model extrusion from layer 1 to their last model
  layer; support is excluded from that proof. No interior missing model layer.
- Eye ring is complete through layers 1–48; bottom-shell layers 95/98 are restored.
- Jaw now prints on its side, +90 degrees around Y. This removes the broad
  unsupported second-layer expansion seen in V6. Its standalone and full-plate
  strengthened air checks pass. Independent first-layer renders confirm growth
  from a long bed edge into a narrow wall.
- No globally empty layer or extrusion/declared-height mismatch; 241255 actual
  extrusion arcs were included in the independent parse.
- All original project-setting keys match HEAD-V5, including restored Manual
  filament mapping. Restoring that archive metadata left actual G-code bytes
  unchanged. See `final-metadata-proof.json`.

Checks remained ON through the documented partgate/slicer seam; no brim.
Slicer estimate: **31030 seconds (8 h 37 m 10 s), 142.7 g PLA**.
These are slicer quantities, not a physical print-success measurement.

## Scope and unresolved items

The bracket's final 0.118 mm-wide terminal section at Z=40.1 mm falls below the
configured 0.4 mm line width and has no layer-201 extrusion. This is reported
explicitly as terminal shape quantization (L6T CANNOT DETERMINE), not hidden as
an interior gap or asserted to reproduce exact CAD geometry. Independent
`bracket-terminal-wedge.png` shows the shrinking cap at layers 198–201.

The original yaw zero-volume six-face component and original tiny FreeCAD
self-intersection diagnostics were preserved. Vertex sharing repairs the
3MF connectivity/slicer omission; it does not certify every mesh defect,
mechanical fit, strength or surface tolerance as repaired.

No live nozzle/material check or bed-clearance observation was made by this
validation agent. The prior job was stopped by the coordinating operator; a
physical bed-clearance confirmation and fresh normal machine preflight remain
necessary before a new send. **This candidate has not been queued or sent.**

## Rendered and inspected evidence

Under `../../independent-codex-2026-09-08/v7-validation/`:

- `exact-meshes.png`: exact final archive triangles in their print poses.
- `jaw-first-layers-v7.png`: mesh sections and actual first four layers.
- `mesh-versus-extrusion-v7.png`: repaired eye ring and bottom-shell comparison.
- `analysis.json`: complete independently parsed model layer intervals.

Both the producing validation agent and printer-reliability agent opened the
jaw and mesh renders. Root receives the paths for final visual review.

Code change: `tools/compact_plate.py` uses shared-index XML export from
`tools/indexed_3mf.py`; `tools/test_indexed_3mf.py` passes three regressions.
See `tools/PRINT-3MF.md` for the controlled same-surface experiment that isolated
the prior export failure. HEAD-V5 and HEAD-V6 remain separate evidence.
