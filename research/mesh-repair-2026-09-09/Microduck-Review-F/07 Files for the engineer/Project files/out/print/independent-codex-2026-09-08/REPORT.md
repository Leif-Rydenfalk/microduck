# Independent Codex validation: FAIL

Date: 2026-09-08. Read-only analysis of the exact already-sent archive. No printer commands, service restarts or original-model edits performed.

Artifact: `../plates/HEAD-V5/microduck-head-v5.gcode.3mf`

SHA-256: `02b1a28723673ae97a8185d89abc006e342801cfaf7d344d868e178fe08c1ef9`

## Findings

1. **FAIL — eye-ring body is missing from the actual print instructions.** Embedded mesh number 7 (object label 32) contains a complete annular section at Z=0.1, 0.3, 0.5, 0.7, 1.1, 1.5, 1.9 and 2.3 mm. Its bounding height is 9.52 mm. Actual G-code has support extrusion only in the eye-ring area for layers 1–40. Model extrusion appears only in layers 41–46 (Z=8.2–9.2 mm), as small upper features, never the main annulus. Direct inspection of raw feature tags confirmed this independently of the parser: layers 1, 2 and 40 say Support only; layer 41 adds Overhang wall; layer 46 has just six extrusion moves. This plate cannot produce the complete intended eye ring. Metadata first-layer area 0.595 mm² was an early clue, not the proof.
2. **FAIL — bottom-shell model extrusion has missing intermediate layers.** Object label 12 has model paths layers 1–100 except **95 (Z=19.0 mm) and 98 (Z=19.6 mm)**. Both contain support paths only; model walls resume at 96 and 99 respectively. A check that counts support as object presence hides this defect. This is a specific violation of the requested absence of model layer gaps; physical impact on the upper small features is not experimentally measured.
3. **FAIL — yaw-roll-motion mesh has an extra zero-volume component.** After exact coordinate welding, there are 2 connected components: one 1270-face solid of 4708.3036 mm³, and a 6-face closed coplanar component of volume zero and area 2.6085 mm². The latter lies entirely at Y=116.1999969 mm, X=111.8180–113.7556, Z=11.3334–12.5989. Watertightness and winding checks alone both pass this malformed geometry. See `yaw-zero-volume.json`. This establishes a mesh defect, not an independently demonstrated imminent printer collision.
4. **PASS — plate-wide extrusion ladder:** 231 actual layers, Z=0.2–46.2 mm, each separated by 0.2 mm; no globally empty layer; no extrusion Z mismatch against declared layer height. Header also says 231. The layer-progress template's 232 is a metadata discrepancy, not a missing-height proof.
5. **PASS with scope — all 11 meshes have watertight edge incidence, consistent winding, positive aggregate volume, and zero faces with area below 1e-10 mm².** Ten have exactly one connected component. Smallest measured edge ranges from 0.000426 mm (jaw) to 0.628029 mm (eye ring). These are edge lengths, not wall thicknesses.
6. **FAIL — FreeCAD independently reports triangle self-intersections** in bottom-head-shell (1 triangle pair), jaw (2 pairs), and yaw-roll-motion (1 pair). All other eight parts, including eye-ring, report none through `Mesh.getSelfIntersections()`. This uses FreeCAD mesh tolerance and float conversion, so it is an additional diagnostic rather than proof of the slicing root cause. Face indices and intersection segments are in `freecad-intersections.json`.
7. **CANNOT DETERMINE — strength, fit, adhesion and physical outcome.** No printed part or machine camera was inspected by this agent. Do not convert topology or toolpath measurements into a physical-success claim.
8. **CANNOT DETERMINE — why the slicer omitted the eye-ring body.** Its archive part subtype is `normal_part`, with no modifier volume, identity component matrix, positive aggregate volume, consistent winding and no FreeCAD-detected self-intersections. Slicing mode is regular, XY compensation zero, raft layers zero. These checks rule out several simple explanations; a controlled independent re-slice is needed to distinguish slicer behavior from project-state problems. The omission itself is demonstrated regardless of cause.

## Method and visual evidence

`analyze.py` parses exact 3MF XML triangles and transforms with lxml/trimesh, welds identical vertices, computes topology, and renders a genuine software z-buffer image. It independently parses G0/G1/G2/G3, absolute/relative extrusion, coordinate resets, object labels and feature classifications. **241,211 extrusion arcs** are sampled at at most 0.15 mm chord length. Support is explicitly excluded from model contiguity. No scheduler validator source or verdict was used as proof.

Sampling model paths at 0.25 mm and measuring distance to all prior-layer extrusion flags possible overhangs at >0.65 mm. Those candidates include legal bridges and intentional support gaps: **the red-point plot alone is not a failure verdict**. This screen cannot certify the absence of all unsupported islands, and the overall result remains FAIL due to direct omissions above.

Rendered and visually inspected:

- `exact-meshes.png`: actual 11 archived meshes, z-buffer rasterized.
- `eye-ring-mesh-sections.png`: annulus present in actual mesh sections.
- `eye-ring-layers.png`: only support trees in actual lower-layer paths.
- `actual-toolpaths.png`: whole-plate selected layers; red support-distance candidates.
- `mesh-versus-extrusion-FAIL.png`: overlaid exact mesh sections and actual toolpaths.

Machine-readable measurements: `mesh.json`, `analysis.json`, `yaw-zero-volume.json`, `freecad-intersections.json`, `object-32-actual-model-paths.json`, `object-12-actual-model-paths.json`. Scripts and logs remain beside them for reproduction. Runtime used FreeCAD's bundled Python with an isolated `/tmp/microduck-independent-libs` trimesh install.

## Implication

The earlier statement that the repaired plate has no missing layers is not supported when **model material is distinguished from support**. The current file should not be approved for another print. Reconstruct/repair the actual failing models, re-slice, and compare model sections to deposited model paths before a replacement is authorized. Decisions about an already-running physical job belong to the coordinating operator; this audit issued no machine commands.

## Follow-up controlled diagnosis

The previous unresolved eye-ring cause is now isolated experimentally: **separate
vertex indices for every triangle in the 3MF exporter** trigger omission in
OrcaSlicer 2.4.2. See `experiments/comparison.json` and
`experiments/vertex-sharing-controlled-test.png` (rendered and visually inspected).
The same oriented surface via STL or shared-index 3MF has model extrusion on all
48 layers; the disconnected-index 3MF has model extrusion only on layers 41–46.
All three passed the previous partgate. The 3MF pair differs only in vertex
sharing. Slicer-reported quantities are respectively 693 s / 2.6 g versus
469 s / 0.2 g; these are slicer evidence, not a physical weight measurement.

`tools/compact_plate.py` now uses `tools/indexed_3mf.py`; three topology/export
regressions pass. A separate `HEAD-V6-candidate` preserves all original triangles
and layout while changing only vertex indices, with per-object exact equality
assertions in `reindex-proof.json`. Original HEAD-V5 remains unchanged. Full-plate
candidate validation is recorded separately when complete.

## Final follow-up candidate

`../plates/HEAD-V7-candidate/microduck-head-v7.gcode.3mf`, SHA-256
`ea36330b828bebf04f9ba345363f623187125ec6429deab146529adc01399bc1`,
passes the strengthened **offline blocking checks**, independently confirmed
with 344 actual layers and 11 continuous model-only intervals. It changes
vertex indexing and jaw print pose (+90 degrees around Y), preserving all other
part placements; every original project-setting key including Manual filament
mapping is restored. See that folder's `VALIDATION.md` for the precise scope.
The final bracket terminal 0.118 mm section is explicitly unresolved at nozzle
resolution; original zero-volume/intersection diagnostics remain documented.
No candidate was queued or sent; live preflight and physical bed clearance remain.
