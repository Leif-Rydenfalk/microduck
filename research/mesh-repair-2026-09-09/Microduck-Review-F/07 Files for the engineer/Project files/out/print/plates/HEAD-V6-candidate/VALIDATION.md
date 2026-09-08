# HEAD-V6 candidate — NOT APPROVED FOR PRINT

Exact artifact: `microduck-head-v6-indexed.gate.gcode.3mf`
SHA-256: `fc2bdf50d05db97bb10286122c4b4797f9fade8743bdb4d48f5ef6ddf1c3cc90`

The shared-index exporter fixes the demonstrated omission: independent parsing
finds all 11 models contiguous from layer 1 to their last extrusion. Eye ring
is now layers 1–48 (was 41–46); bottom shell has model paths at layers 95/98.
Full plate: 232 layers, 0.2–46.4 mm in 0.2 mm steps, no globally empty layer,
no extrusion/declared-Z mismatches. All original oriented triangles and layout
are identical; see reindex-proof.json. This includes the unchanged zero-volume
yaw component and previously measured intersection diagnostics.

Rendered exact geometry/toolpath overlays have been visually inspected:
`../../independent-codex-2026-09-08/v6-validation/mesh-versus-extrusion-v6.png`.
The complete lower eye-ring body and bottom-shell upper features now appear.

**Remaining FAIL: jaw layer 2 expands over substantial unsupported space.**
The jaw underside is shallow and curved within Z=0–0.8 mm, leaving insufficient
space for support under low overhangs. Its second-layer bridge endpoints extend
outside the small first-layer pad. A side-orientation experiment is being
validated separately; this unchanged-pose candidate must not be sent.

The strengthened validator also flags the bracket's final slice plane at Z=40.1
mm where model extrusion is absent at layer 201. Investigation of its narrow
terminal wedge is separate from a genuinely missing interior layer.

Slicer checks are ON. Partgate returned PASS, 30670 s / 141.6 g, which is not the
final approval. All original project-setting keys match except filament_map_mode:
original Manual, candidate Auto For Flush. This routing metadata must be restored
and revalidated for a final send candidate. No machine commands were issued.
