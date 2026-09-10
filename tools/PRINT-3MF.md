# Connected 3MF export

`compact_plate.py` now writes shared vertex indices with `indexed_3mf.mesh_xml`.
The prior STL-style export gave every triangle three fresh vertex indices.
OrcaSlicer 2.4.2 accepted that archive but omitted substantial model geometry.

Measured 2026-09-08 on the exact Microduck eye-ring surface, using the farm's
`partgate` with checks enabled, identical .4/.6 Standard H2D profiles and no brim:

| Input | Actual model layers | Slicer estimate |
|---|---|---|
| STL | 1–48 contiguous | 693 s / 2.6 g |
| Shared-index 3MF | 1–48 contiguous | 693 s / 2.6 g |
| Separate vertices per triangle 3MF | 41–46 only; body absent | 469 s / 0.2 g |

All three passed the old partgate, demonstrating why slicer exit status and
watertightness after coordinate welding cannot certify deposited geometry.
The two 3MF inputs differ only in vertex sharing. The experiment retained face
orientation and coordinates. See
`out/print/independent-codex-2026-09-08/experiments/vertex-sharing-controlled-test.png`
and its scripts/results.

The exporter welds coordinates at its serialized precision (four decimals),
including signed zero. It preserves triangle order and winding. This is a
connectivity fix, not automatic repair of self-intersections or zero-volume
components. Run `python3.12 tools/test_indexed_3mf.py` to check topology and
oriented geometry preservation. Use a Python with working XML support.

HEAD-V5 is immutable failed evidence. `HEAD-V6-candidate` changes only vertex
sharing and includes `reindex-proof.json`, asserting identical oriented triangles
for all 11 objects against the original unsliced HEAD-V5 input. Candidate status
does not authorize printing. Re-slice, verify model-only layer continuity and
mesh/toolpath correspondence, then satisfy the normal machine preflight and
physical bed-clearance requirements before any send.

The final offline candidate is `out/print/plates/HEAD-V7-candidate/`: it also
rotates the jaw +90 degrees around Y to resolve a measured layer-2 unsupported
expansion. Its `VALIDATION.md` names exact artifact hash, independent measurements,
remaining terminal-feature uncertainty and physical preflight requirements.
No candidate was sent by the validation agent.

HEAD-V9 supersedes V7 for the final manufacturing handoff. It also rotates the
neck bracket to eliminate its terminal thin-slice omission and removes only the
yaw's six-face zero-volume component, with an unchanged-main-body/A-B-slice proof.
`out/print/plates/HEAD-V9-candidate/VALIDATION.md` records the exact final SHA,
corrected partgate's retained diagnostic log and root's live-H2D PASS. Dimensional
fit/strength are explicitly separate from these print-layer checks.
