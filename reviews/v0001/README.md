# Microduck 1:1 recreation — review v0001

**Engineering review only. A complete 1:1 recreation has not been verified.**

This numbered package is frozen. Later experiments and drawing changes are
separate versions and are not included. Nothing has been sent to your boss by
this tool.

## Version identity

- Microduck source commit: `f82440ce8f856f41e7972b11055d459258491b04`
- CAD core commit: `03b27582302853e6b303760717084728447ef399`
- Previous issued package: `none — first numbered boss review`
- Every included file is listed with its SHA-256 in `MANIFEST.json`.
- Source history remains in Git; the published servo v0.0.1 and the corrected
  research candidate are both included separately. This is a selected evidence
  package, not a complete repository backup or an archive of every temporary run.

## What changed and what remains open

| Area | Verified evidence | Remaining limitation |
|---|---|---|
| Servo mechanics | Manufacturer maximum pilot depth is 3 mm; existing model used 6 mm. Corrected mounting-hole candidate passed 100 geometric probes. | Center geometry and other exterior details remain incomplete; original installed identity is unverified in this revision. |
| Fasteners | All 52 servo ISO-length proposals withdrawn; 35 historical modeled penetrations exceeded 3 mm. Rebuild guard preserves existing assembly records. | Exact original tapping screws, seating, usable engagement and torque remain unresolved. |
| Drawings | Shin principal sheet and enlarged ankle supplement pass eight sheet gates plus PDF, scale and locator readbacks. | Full contract is INCOMPLETE. Hidden E009/E047/E061 leaders and additional enlarged feature clusters remain open in this frozen version. |
| Electronics | Public PCB/runtime and manufacturer voltage limits are reconciled; power-test holds remain explicit. | No completed physical electrical acceptance. Original servo variant and installed power route remain unresolved. |
| Sourcing | Conditional supplier inquiries and priced candidates are available. | Source availability is not original-part identity or purchasing approval; quoted scope is not a complete landed robot cost. |
| Fabrication | Included printer observation records the head job running at 24% on 2026-09-08 at 23:18 UTC+08. | A dated running observation is not print completion, dimensional acceptance or a verified robot. |

## Read first

- [Shin principal drawing](out/drawings/microduck-shin/microduck-shin.pdf)
- [Enlarged ankle supplement](out/drawings/microduck-shin/detail-A-supplement-build/microduck-shin.pdf)
- [Servo source comparison](research/xl330-mechanical-source-2026-09-08/REPORT.html)
- [Servo revision dependencies](research/xl330-interface-revision-review-2026-09-08/REPORT.html)
- [Fastener withdrawal evidence](research/servo-fastener-restriction-2026-09-08/REPORT.html)
- [Sourcing](SOURCING.html) and [supplier questions](RFQ.html)

Manufacturer and supplier links may require internet access. Original research
reports can cite repository sources outside this selected package; the exact
source commit above identifies those records. Synthetic capture examples are
test fixtures, not observations of a physical robot.
