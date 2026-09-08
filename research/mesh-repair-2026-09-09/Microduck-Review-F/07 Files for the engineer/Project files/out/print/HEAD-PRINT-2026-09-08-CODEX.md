# Head print continuation — 2026-09-08

**REVOKED — independent validation subsequently FAILED.** The prior validator counted supports as model extrusion. Independent Codex mesh-versus-G-code comparison found the eye-ring body absent and bottom-shell model layers 95/98 missing. Root inspected the actual comparison renders, stopped job-0001 at 1%, confirmed the printer returned FAILED/cancelled, and unapproved the file to prevent auto-send. The plate must not be printed. See `independent-codex-2026-09-08/REPORT.md` and `mesh-versus-extrusion-FAIL.png`. The observations below are historical, including the incorrect PASS.

Revalidated the existing HEAD-V5 repaired plate with `scheduler.validate` against live H2D AMS HT. PASS: 231 layers at 0.2 mm, 11 expected objects all extruding continuously, no detected empty layers or unsupported object layers, extrusion within reach, PLA loaded, fitted left/right 0.4/0.6 Standard nozzles matched. No brim. This is toolpath validation, not proof of physical print completion.

The queued file and design output have identical SHA-256: `02b1a28723673ae97a8185d89abc006e342801cfaf7d344d868e178fe08c1ef9`.

Preflight reported READY; previous FAILED state was a cancellation record (0300_400C). Sent existing job-0001 through `job_action(send)` as Leif via Codex. The API confirmed sent, and subsequent printer_status calls reported running at 0%. Estimated total 8h 52m 24s, 141.81 g PLA. Physical completion and first-layer adhesion have not been confirmed.

The 11 rigid pieces are top/bottom head shells, jaw, motor support, face part, yaw-roll motion, eye ring, neck pitch bracket, M12 lens holder, and two neck plates.

Two additional flexible mouth components remain outstanding: jaw-soft and soft-mouth-top. Only PLA is reported loaded. Asked which TPU is available for a separate print. Repaired both original TPU meshes through scheduler.meshfix into `stl/fixed/TPU/`; post-repair meshdoctor reports zero degenerate/duplicate faces, non-manifold/boundary edges, or flipped faces, and one shell each. Originals preserved.

Their H2D TPU partgate runs FAILED with `run found error, exit`; see `stl/fixed/TPU/partgate.json`. Neither is slice-validated or sent. Empty error-detail arrays do not constitute a pass. Resolve the slicer error and validate the final plate against the selected, loaded TPU before printing these pieces.
