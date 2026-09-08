# Active recreation work — September 8

Goal: a verified 1:1 Microduck recreation, including exact electronics,
mechanical fit, sourcing, assembly and behavior. This session has not closed
that goal and has not verified an assembled physical unit.

## Current ownership

- Root Codex: HAT source/fit evidence, reconciliation, readiness/factory documents,
  Ming inquiry delivery, integration and explicit-path commits.
- Codex electrical agent: fastener endpoint/thread and harness evidence completed;
  now correcting test procedure identity gates and readiness source claims.
- Codex sourcing agent: component fit and package-quantity corrections completed;
  now repairing four stale evidence hashes through the owning triad interface.
- Codex drawing agent: `out/drawings/microduck-shin/`, `tools/draw_part.py`, narrowly
  scoped ce-cad drawing generator/checker corrections. No blanket drawing release.
- Existing separate head-print session: its tools, head plate outputs and physical
  jobs are preserved. This session does not own or operate those jobs.

## For the head and harness session

Read `research/hat-orientation-audit-2026-09-08.json` and the corrected
`out/internals/hat-fit.json`. The old 180° fit hypothesis preserves the four
mounting holes but shifts the GPIO header and anchor centroids 23.010002 mm.
Its smaller collision volume does not establish a usable orientation in the
same fixed electronics stack. Historical collision values are retained; they
were not rerun by the coordinate audit.

The public C1 HAT source measures 65.000034 × 30.900064 × 1 mm, with four
2.7 mm mounting drills. Original-unit revision remains unconfirmed. Its
connector positions differ from the older simulation mesh; do not silently
replace the mesh and preserve its old cable endpoint assumptions.

## Current electrical and sourcing state

Public HAT clock comes from local Y1, not GPIO header pin 13. Shared +3V3,
U3-derived +1V8 and the measured +5V topology are now modeled. Netlist rerun:
82 PASS / 15 FAIL / 26 CANNOT DETERMINE. All 15 servo-voltage failures remain.

The selected ROBOTIS package includes one bus lead per servo. For the existing
16-lead plan, extra ten-pack purchases are 1/10/100 over batches of 1/100/1000
robots. Other offers receive no credit without verified bundle evidence.

## Coordination and delivery evidence

The cockpit health check alone did not establish live Claude activity. Later,
the parallel communications session recorded a successful Claude CLI drafting
result in `research/networking-2026-09-08/claude-caption-output.json`. Root read
its success status. Historical workflow IDs remain distinct from current owners.
The networking and head-print files are foreign-owned; preserve them.

The parts inquiry was sent by the parallel session; its evidence is
`research/ming-parts-request-2026-09-08/DELIVERY.json`. Root independently
inspected the outgoing screenshot, then sent supplemental ZIP B at 21:46
(with A inside unchanged) to the same Ming Chan conversation. Exact outgoing
filename and empty composer were verified. See
`research/ming-handoff-2026-09-08/update-b/delivery.json` and `delivery-ui.png`.
The archive and delivery snapshot are frozen. No order or production release
was sent by this lane.

Ming replied at 21:55 asking about the archive's safety. Root inspected
`research/networking-2026-09-08/ming-reply-outgoing.png`, showing both the
incoming question and the parallel session's reply offering plain-text details
and requesting supplier introductions. That exchange does not establish a quote
or component identity. Recipient read/download status is not inferred.
Do not resend the inquiry, archive or already-delivered reply. Coordinate any
further response with the existing communications owner.
