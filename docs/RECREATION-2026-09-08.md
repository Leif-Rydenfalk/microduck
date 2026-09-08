# Microduck 1:1 recreation — evidence and sourcing, 2026-09-08

The target is the original robot's geometry, fitted hardware, wiring and behavior.
The repository does not yet prove that target. A supplier PASS in
[`spec/sourcing.json`](../spec/sourcing.json) establishes its sourcing rule, not
that the offered part is the one Pollen fits. Keep replacement candidates
separate from confirmed original identities.

The latest [servo geometry audit](../research/xl330-geometry-revision-2026-09-08/README.md)
found a 6 mm modeled horn/idler pilot where ROBOTIS specifies 3 mm maximum
and M2 tapping screws. A corrected research candidate passes 100 finished-solid
probes; the published shelf iteration remains unchanged pending integration.
35 of 52 nominal servo-face screw penetrations exceed that limit in the existing
placement model. This is not a physical measurement or a replacement screw list.
The current run generator now withdraws all 52 servo ISO-length proposals.
The 64-screw assembly remains a historical nominal placement; a rebuild refuses
to silently remove withdrawn hardware. Twelve other generic nominal proposals
remain, also without original physical thread acceptance. The
[application check](../research/servo-fastener-restriction-2026-09-08/current-application.json)
records the corrected run data and unchanged assembly hashes.

## Electronics: correction that changes the next task

Pollen publishes [the Robot HAT project](https://github.com/pollen-robotics/elec_RPI_Robot_HAT)
and [its KiCad libraries](https://github.com/pollen-robotics/lib_KiCAD).
The upstream API returned revision `23eab11927f95ceca0dfa35bf182caeb7db39ea0`
on 2026-09-08, the same revision cited by our September 3 identity lane.
The statement that every HAT schematic is unpublished is obsolete.

That lane's geometry report is also wrong. Reading the pinned PCB source gives
an outline coordinate span of **65.000034 × 30.900064 mm**, a declared thickness
of **1 mm**, and **four 2.7 mm drilled pads** inside the J4 footprint on a
**58 × 23 mm** pattern. Its reported 65 × 48.5 mm and absence of mounting holes
must not guide a redesign. These are file measurements, not a physical fit test.

Reproduce: `python3 tools/audit_official_hat.py`. The
[saved report](../research/official-hat-audit-2026-09-08.json) includes source URL,
SHA-256, exact outline blocks, drill counts and local hole coordinates. It checks
the expected eight outline primitives and four mounting holes and refuses a
different structure. No kernel, PCB editor or hardware is invoked.

The Microduck reference mesh was previously measured as 65.025 × 30.025 × 0.840 mm
in [`out/open/identity-sourcing.json`, ID-03](../out/open/identity-sourcing.json).
Thus the public board is much closer than the old report implied, but its roughly
0.875 mm larger short dimension and different thickness still need comparison
against the actual head and connector clearances. Neither the mesh nor the
family resemblance establishes the production revision. Obtain the board's
silkscreen/assembly number and both-side photographs from an original unit.

The existing archived official BOM supplies useful component identities:
TLV320AIC3104IRHBR codec (C181753), PAM8406D amplifier (C86270),
LMA2718T421-OA5-2 MEMS microphone (C7587901), BMI088, AP63205 regulator,
XC6206P182 1.8 V regulator, and LM5050-1. These are **public HAT family** facts;
confirm suffixes, DNP entries and the production revision before kitting.
[Archived BOM](../out/open/identity-evidence/hat/ASE01187-C1_elec_RPI_Robot_HAT_BOM.csv).

The September 8 electrical rerun after correcting I2S/MCLK and public HAT rails produced **82 PASS /
15 FAIL / 26 CANNOT DETERMINE** in [`electronics/report.json`](../electronics/report.json).
GPIO header pin 13 is not codec MCLK: the public HAT uses local oscillator Y1.
The provider is now modeled explicitly, with unresolved timing/installed-variant
evidence still reported as CANNOT DETERMINE. The public +3V3 and U3-derived +1V8 topology is now represented; board-level
current capacity and operating behavior remain unresolved. The servo voltage
conflict is material: catalog XL330 input is 3.7–6.0 V whereas the modeled runtime
bus is 6.6–8.2 V. Confirm the actual servo variant and rail; software error masking
does not establish hardware suitability. [ROBOTIS specification](https://emanual.robotis.com/docs/en/dxl/x/xl330-m288/).

## Where to source components

Vendor observations below were checked on 2026-09-08 by the Codex sourcing agent.
Prices retain vendor currency and exclude unverified shipping, tax and import
costs. Delivery country is still pending. No orders or supplier messages were sent.

| Need | Source and observed offer | Remaining 1:1 question |
|---|---|---|
| 15 servos | [ROBOTIS XL330-M288-T, 902-0163-000](https://en.robotis.com/shop_en/item.php?it_id=902-0163-000), USD 23.90 each; USD 358.50 for 15 | Confirm original M288/M077 ratio, voltage variant and firmware. Firmware ≥53 changes indirect-address/data tables; check runtime register assumptions. |
| Bus leads and servo screws | Same retail package includes one 180 mm X3P lead, six M2×6 TAP and ten M2×8 TAP screws per servo | For the existing 16-lead plan, 15 packaged servos leave one additional lead before spares. Buying only ten-packs would still require one extra pack. Reconcile lengths and slack. Included TAP screws are not automatically replacements for the assembly's metric screws/inserts. |
| Radxa ZERO 3W | [ALLNET China](https://shop.allnetchina.cn/products/copy-of-radxa-zero-3w): 1GB/8GB/header USD 23 sold out; 4GB/32GB/header USD 51 sold out; 2GB/no-eMMC/header USD 55.99 displayed Add to cart | [Radxa product brief §7](https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_product_brief.pdf) omits 1GB/32GB. This means absent from the published catalog, not proof an OEM configuration does not exist. Listed alternatives change the specification. |
| IMX219 camera candidate | [Seeed 102110719](https://www.seeedstudio.com/IMX-219-CMOS-camera-module-M12-and-CS-camera-available-p-5372.html): USD 15.90; USD 12.50 at 10+; in stock | Exact board, lens, FOV and ribbon are unresolved. Sensor compatibility alone does not prove a match. UCTRONICS B0183's old offer was not successfully reverified. |
| HAT codec | [LCSC C181753](https://www.lcsc.com/product-detail/Audio-OpAmps_TI_TLV320AIC3104IRHBR_TLV320AIC3104IRHBR_C181753.html) | Manufacturer code maps to the official family BOM; no current price/quantity imported from search snippets. |
| HAT MEMS microphone | [JLCPCB C7587901](https://jlcpcb.com/partdetail/Linkmems-LMA2718T421_OA52/C7587901) | Listing matches the official family BOM. Confirm stock, assembly availability and the fitted board revision. |
| PCB fabrication/assembly | [JLCPCB process capabilities](https://jlcpcb.com/capabilities/Capabilities%2C/) and [assembly capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities) | Candidate fab route; quote the selected exact revision with stackup, BOM/DNP and placement files. An advertised starting price is not this robot's PCB quote. |

Existing sourcing records already cover bearings (MR1622 and 6700 family), JST
connectors, fasteners, battery packs and soft materials. Their September 2–3
offers remain historical, not refreshed stock. Do not buy the unknown original
battery, lens, NFC, speaker or LED solely because a candidate has supplier PASS.
The later ID-02 record reports support for both ToF generations; identify the
reference unit's generation instead of assuming every duck uses L8CX.

## Work parcels for the next sessions

| Parcel | Concrete output and acceptance evidence | State |
|---|---|---|
| Original-unit baseline | Revision/serial, photos, board markings, component labels and measured dimensions; agree comparison tolerances | Needs original-unit access; asked user |
| HAT reconciliation | Compare pinned official schematic/BOM and PCB with the local reconstruction, head envelope and runtime; record every intentional deviation | Clock/rail/source corrections committed; PCBA DRC, exact installed revision and fit remain open |
| Servo and power | Establish installed variant, measured supply and firmware/register compatibility; resolve voltage failures before powered tests | Open; measurements not performed |
| IMU bridge | Identify original MCU/transceiver and board revision; compare protocol, register layout, timing and mechanical fit | Original identity unresolved; functional substitutes cannot close 1:1 |
| Procurement | Exact MPN/qty/kit contents, delivery-country quote, stock and lead time per line; reconcile bundled cables and fasteners | Bundled-lead arithmetic corrected and tested for 1/100/1000 robots; final basket pending identity and destination |
| Mechanical fidelity | Per-part comparison against pinned meshes and original-unit dimensions, with maximum error, critical fits and mass/inertia separately reported | Existing model/print evidence does not prove physical equivalence |
| Assembly validation | Fastener-to-hole map, harness route/lengths, range of motion, thermal and gait measurements on an assembled unit | Remains open |

The missing `ce-cad` entry was repaired on 2026-09-08 after the user authorized
continued work and the necessary tooling repair. The
[new source-backed entry](../../../ce-cad/.claude/skills/ce-cad/SKILL.md)
is explicitly labelled a reconstruction, routes to the existing authoritative
rules, and is installed through symlinks in both Claude and Codex skill roots.
Validation and source-link checks passed. It does not claim recovery of the
lost original or verification of any physical design. The mandatory-entry
tooling blocker is closed.

## Coordination record

User authorized collaboration with the other local Codex/Claude instances.
Codex child agents are working on electrical reconciliation, exact component
sourcing and drawing validation, with explicit file ownership. The local cockpit
on 127.0.0.1:8877 initially refused connection and later returned health OK. Its
Claude session records are historical metadata; its live Claude CLI check failed,
so they do not establish a running Claude session. Process-name inspection found
Codex processes but no Claude-named process. This does not prove no Claude app
session exists. No message delivery to an existing external session was verified.

The user subsequently authorized contacting Ming with files on WeChat.
[The bilingual inquiry package](../research/ming-handoff-2026-09-08/BRIEF.html)
contains reference attachments and requests original-unit evidence, exact parts,
DFM feedback and itemized prototype/volume quotations. Its manifest records
hashes and evidence limitations. Delivery status belongs in the package's
verification record; a prepared ZIP does not prove a message was sent.

The existing head-print session's
[September 8 handover](../out/print/HEAD-PRINT-2026-09-08-CODEX.md) reports a rigid
head print sent and unresolved TPU slicing. Its files and hardware were left
alone; print completion has not been independently checked here.

This document is the handover for other sessions. Claim a specific parcel and
file set before edits, check current mtimes/status, and do not infer live owners
from September 2 workflow IDs. Consume the existing verification and identity
reports with the correction above. Do not rerun the old manufacturing workflow
into another lane's drawings directory.

## Validation update — September 8

The 22:10 readiness refresh found 27 distinct existing drawing reports: the
shin passes all eight sheet gates and 26 fail; six expected drawing entries
are missing. The shin's canonical PDF contains six verified rendered views.
Its full drawing contract remains incomplete: individual feature locators,
shaded feature details and original/production measurements remain open.
Readiness therefore keeps the drawing NOT_YET despite its eight-gate PASS.
See the [canonical result](../out/drawings/microduck-shin/result.json).

The sourcing generator now subtracts verified packaged servo leads and rounds
remaining ten-packs over the full batch. The selected offer needs 1/10/100
extra ten-packs for 1/100/1000 robots. Alternative offers without verified
bundle evidence receive no inclusion credit. The rollup remains a partial
cost estimate, not a supplier quotation or a confirmed original-parts basket.

The [orientation audit](../research/hat-orientation-audit-2026-09-08.json)
corrects a historical fit claim: the 180° in-plane rotation preserves the four
mounting holes but moves GPIO/anchor centroids 23.010002 mm. The
[fit report](../out/internals/hat-fit.json) retains its historical collision
volumes but disqualifies that pose as interchangeable in the same fixed stack.
This source-coordinate check did not rerun collision geometry or test a unit.

The [conditional PCBA quote appendix](../research/hat-pcba-rfq-2026-09-08/APPENDIX.html)
reconciles 113 physical components and includes per-designator quantities for
1/100/1000 boards. Twelve verification checks passed. Its DRC run reports 40
J4 pad-to-hole clearance errors and nine library warnings, with zero unconnected
items. It also records the fabrication drawing/stackup copper conflict, missing
test-point purchase codes, DNP ambiguity and Y1 land-pattern discrepancy. It is
an engineering inquiry, not a manufacturing release.

The [servo power audit](../research/servo-power-audit-2026-09-08/AUDIT.md) confirms
the published runtime takes its 6.6–8.2 V battery observation directly from
servo register 144, while both standard XL330 variants specify 3.7–6.0 V. The
public HAT connects motor supplies to +BATT. Startup also writes shutdown 52
(0x34), excluding input-voltage bit 0 despite its comment. The audit supplies
a factory evidence procedure; no runtime masks or physical rails were changed.

The [updated Ming review packet B](../research/ming-handoff-2026-09-08/update-b/READ-FIRST.html)
contains the original package unchanged plus hashed engineering attachments,
including the public fabrication archive and the later engineering audits.
[Delivery status](../research/ming-handoff-2026-09-08/update-b/delivery.json)
is **sent — UI observed**: the named ZIP appears as an outgoing file in Ming
Chan's WeChat conversation and the composer is empty. Recipient read/download
and a reply remain unknown. A parallel local session also delivered the
[parts inquiry](../research/ming-parts-request-2026-09-08/DELIVERY.json).
The archive is frozen; its builder now refuses to overwrite a sent packet.

Later coordination evidence supersedes the initial unknown-reply status:
Ming asked “How many virusses are in there?” at 21:55. Root inspected the
parallel session's [conversation capture](../research/networking-2026-09-08/ming-reply-outgoing.png),
which also shows its reply offering plain-text details and asking for trusted
supplier introductions. No engineering quotation or component confirmation is
established by that exchange. The parallel session also records a successful
Claude CLI drafting result. Its networking files remain owned by that session;
this record does not duplicate outreach or modify the frozen delivery snapshot.

The [fastener endpoint audit](../research/fastener-endpoint-integrity-2026-09-08/AUDIT.md)
maps all 64 modeled screws to explicit source-mesh pilot anchors. Five endpoint
and six thread-confidence regressions pass. This repairs reference integrity;
thread identity, stack qualification and torque remain unverified. The nominal
buy list still omits 23 modeled screws by size.

The [harness audit](../research/harness-route-confidence-2026-09-08/)
retains historical modeled lengths but removes unsupported physical cut lengths
and totals. Six route-confidence regressions pass. The zero-length stacking
header is not a cable; no physical loom has been measured.

Whole-kit battery purchasing and conditional ToF selection raise the partial
per-robot sourcing subtotals to USD 641.4564 / 612.4949 / 611.3793 at quantities
1 / 100 / 1000. These are source-based estimates, not landed quotations or a
verified original-component basket. The [power/ToF audit](../research/tof-power-sourcing-2026-09-08/REPORT.html)
records package quantities, interface mismatches and unresolved current ratings.

The test plan is NOT_YET. Its defined 42 end-of-line gates do not establish
physical test completion. The connected-servo high-voltage procedures require
correction and verified original power/servo identity before execution.

The [original CAD access audit](../research/original-cad-access-2026-09-08/REPORT.html)
maps all 43 source sidecars: 37 / 3 / 3 parts belong to three different CAD
microversions. The old single-version source note now has an additive correction.
These IDs do not identify production revisions. A fresh isolated browser redirects
to Onshape sign-in and anonymous API calls return 401/403; no original STEP/BRep
was acquired. Existing public source files and their hashes remain preserved.

The refreshed structural shelf check now reports 18 PASS / 54 CANNOT DETERMINE /
0 FAIL across 72 references. Four stale metadata hashes were reconciled without
changing physical findings. The [eye-ring correction](../research/eye-evidence-correction-2026-09-08/REPORT.md)
withdraws misclassified positive evidence through an audited, append-only CLI;
all eight historical rows and geometry bytes remain unchanged. Its final T1 is
simulation evidence, not physical acceptance. Structural PASS is kept separate
from manufacturing readiness throughout the factory report.

A read-only live farm refresh confirmed the independent head-print job at 16%,
running without a reported print error. Its V9 artifact hash matches the reviewed
file; see the [scoped observation](../out/handover/HEAD-JOB-OBSERVATION-2026-09-08.json).
This establishes continued printing, not completed parts, adhesion quality or
dimensional acceptance. The print-owning session retains control of the job.

The three omitted nominal fastener sizes now have
[conditional source routes](../research/fastener-source-routes-2026-09-08/REPORT.html)
with whole-package quantities. These remain model candidates; original threads,
material, grade and ROBOTIS TAP equivalence are not established.
