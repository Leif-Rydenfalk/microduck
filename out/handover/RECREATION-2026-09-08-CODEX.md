# Active recreation work — September 8

Goal: a verified 1:1 Microduck recreation, including exact electronics,
mechanical fit, sourcing, assembly and behavior. This session has not closed
that goal and has not verified an assembled physical unit.

## Current ownership

- Root Codex: HAT source/fit evidence, reconciliation, readiness/factory documents,
  Ming inquiry delivery, integration and explicit-path commits.
- Codex electrical agent: public HAT source/model reconciliation (completed in
  `47448ff`), now `research/servo-power-audit-2026-09-08/`.
- Codex sourcing agent: bundle quantities and Y1 evidence (completed in `47448ff`),
  now `research/hat-pcba-rfq-2026-09-08/`.
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

## Coordination and delivery limits

The cockpit at localhost:8877 returned health OK, but its Claude session
records do not establish live Claude status. No delivery to the independent
head-print session has been verified; this shared-file notice is available
for it to read. Historical September 2 workflow IDs are not current ownership.

The bilingual Ming inquiry and ZIP are in `research/ming-handoff-2026-09-08/`.
User authorized contacting Ming. Delivery is pending selecting his WeChat
conversation; consult `verification.json` for actual delivery evidence. Prepared
files do not mean sent files. No component order has been placed.

## Discovered parallel communications work

Another local session has prepared a PCB-specific inquiry and CRM evidence in
`../../ce-comms/docs/MING-PCB-INQUIRY-2026-09-08.txt` and
`../../ce-comms/evidence/crm/ming-source-audit.json` (paths relative to this
repository root). It correctly records the original package as unsent and the
configured WeChat transport as a simulator. Those files are preserved.

Native WeChat on this Mac is logged in. A conversation displayed as **Ming
Chan** has prior factory/supplier automation context matching the requested
contact. This is a candidate conversation match, not a recovered platform
handle or verified factory identity. Its chat has not yet been selected for
sending. Do not deliver a second duplicate inquiry if another session records
actual delivery first; check both package verification and CRM evidence.

## Delivery update — 21:46 China time

Ming's parts inquiry was sent by the parallel session; its evidence is
`research/ming-parts-request-2026-09-08/DELIVERY.json`. Root independently
inspected the outgoing screenshot. Root then sent the supplemental ZIP B
(with A inside unchanged) to the same Ming Chan conversation. Exact outgoing
filename and empty composer were read through Accessibility and screenshot.
See `research/ming-handoff-2026-09-08/update-b/delivery.json` and
`delivery-ui.png`; the archive SHA-256 is recorded there. These supersede the
pending-delivery notes above. Do not resend either inquiry or archive.
Recipient read/download and response remain unknown. Await Ming's feedback;
no purchase or production release was sent.
