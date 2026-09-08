# Microduck head manufacturing status

Updated during the 2026-09-08 manufacturing review. This is a first-article
record; successful slicing does not establish mechanical fit or strength.

## Rigid head set

HEAD-V9 contains 11 PLA pieces: top and bottom head shells, jaw, motor
support, face plate, yaw/roll mechanism, eye ring, neck-pitch bracket, M12
lens holder, and two neck plates. Its exact archive renders and actual
model-extrusion comparisons were opened and inspected by the coordinating
Codex agent as well as the independent reviewer.

The V5 eye-ring omission and bottom-shell interior missing layers are
repaired. V9 has 344 layers and continuous model extrusion for all 11
objects; supports are excluded from that test. Live validation matches
the H2D AMS HT's 0.4/0.6 mm Standard nozzles and PLA. Estimate: 142.76 g,
8 h 36 min 17 s. Evidence: `plates/HEAD-V9-candidate/live-validator.txt`.

The final neck-bracket orientation resolves V7's terminal-layer warning
without changing its shape. The extra six-face zero-volume component was
removed from the yaw mechanism; its main body volume is unchanged. Original
and cleaned slices pass, with sampled model-path differences below 0.032 mm.
V9's final full plate passes the repaired diagnostic gate with detailed logs
retained and no empty-layer/conflict report. Root inspected its exact mesh
render and changed-part layer comparison, including the bracket's final slab.

Final file: `plates/HEAD-V9-candidate/microduck-head-v9.gcode.3mf`.
SHA-256: `58fac4ca6baee18484bba3afbc393d83fad1821075ffe1d9557740a15a0254b4`.
Small original triangle-intersection diagnostics do not produce demonstrated
missing model layers. A locally smoothed yaw notch still requires physical
fit measurement; see `independent-codex-2026-09-08/INTERSECTION-DISPOSITION.md`.

## Flexible head set

The jaw-soft and soft-mouth-top pieces are separate TPU work. Their
previous slicing failure was caused by placement outside the print area.
Corrected placement now slices successfully; final layer/support validation
is in progress. No loaded TPU or its
grade has been confirmed; no PLA substitution is authorized by this record.

## Machine and physical acceptance

The old V5 job was stopped and unapproved. Leif subsequently confirmed that
the printer was ready for whatever is sent and requested as much of the head
as possible. The final V9 file was copied with its SHA-256 verified into the
farm projects directory and registered as job-0002, retaining the failed V5
history. Fresh preflight was READY. The normal job_action(send) revalidated
and returned sent; a subsequent live observation reported running 0%, job-0002.
Evidence: `plates/HEAD-V9-candidate/send-result-2.json` and
`plates/HEAD-V9-candidate/post-send-status.json`. This establishes startup,
not first-layer adhesion or successful completion. Automatic sending remains
off; this was an explicitly requested manual send.

Release checks completed: exact final artifact validated, rendered layers
inspected, printer readiness confirmed by Leif, loaded PLA/nozzles verified,
and normal farm send gate used. Subsequent physical progress remains to monitor.

After printing: inspect all pieces for missing walls, separation, deformation
and support-removal damage; measure mating features against the final CAD;
test shell closure, fastener engagement, lens/servo/bearing fit and free
movement through the intended range. Record actual measurements and any
rework. These physical checks are pending, not passed by the software tests.
