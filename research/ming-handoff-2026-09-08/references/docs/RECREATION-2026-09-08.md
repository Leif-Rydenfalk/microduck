# Microduck 1:1 recreation — evidence and sourcing, 2026-09-08

The target is the original robot's geometry, fitted hardware, wiring and behavior.
The repository does not yet prove that target. A supplier PASS in
[`spec/sourcing.json`](../spec/sourcing.json) establishes its sourcing rule, not
that the offered part is the one Pollen fits. Keep replacement candidates
separate from confirmed original identities.

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

The local reconstructed electronics report remains **75 PASS / 15 FAIL /
28 CANNOT DETERMINE**, as stored in [`electronics/report.json`](../electronics/report.json).
This is a historical generated result, not a test rerun today. The servo voltage
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
| HAT reconciliation | Compare pinned official schematic/BOM and PCB with the local reconstruction, head envelope and runtime; record every intentional deviation | Next electronics task; corrected source geometry above |
| Servo and power | Establish installed variant, measured supply and firmware/register compatibility; resolve voltage failures before powered tests | Open; measurements not performed |
| IMU bridge | Identify original MCU/transceiver and board revision; compare protocol, register layout, timing and mechanical fit | Original identity unresolved; functional substitutes cannot close 1:1 |
| Procurement | Exact MPN/qty/kit contents, delivery-country quote, stock and lead time per line; reconcile bundled cables and fasteners | Fresh offers above; final basket pending identity and destination |
| Mechanical fidelity | Per-part comparison against pinned meshes and original-unit dimensions, with maximum error, critical fits and mass/inertia separately reported | Existing model/print evidence does not prove physical equivalence |
| Assembly validation | Fastener-to-hole map, harness route/lengths, range of motion, thermal and gait measurements on an assembled unit | Remains open |

Physical edits are blocked by the workshop's mandatory `ce-cad` entry skill:
[workshop instructions](../../../AGENTS.md) says load it
“before touching anything physical.” Searches under local Codex/Claude skills
and the workshop found scoped skills but no `ce-cad/SKILL.md`. This research
pass edits documentation and evidence only. Restore the canonical entry skill
before taking up the physical design parcels.

## Coordination record

User authorized collaboration with the other local Codex/Claude instances.
A Codex child agent completed the read-only supplier audit. The existing local
cockpit endpoints on 127.0.0.1:8877 for sessions/workflows both refused connection;
the default tmux socket was absent. Process-name inspection found Codex processes
but no Claude-named process. This does not prove no Claude app session exists.
No message delivery to an existing external session was verified.

The existing head-print session's
[September 8 handover](../out/print/HEAD-PRINT-2026-09-08-CODEX.md) reports a rigid
head print sent and unresolved TPU slicing. Its files and hardware were left
alone; print completion has not been independently checked here.

This document is the handover for other sessions. Claim a specific parcel and
file set before edits, check current mtimes/status, and do not infer live owners
from September 2 workflow IDs. Consume the existing verification and identity
reports with the correction above. Do not rerun the old manufacturing workflow
into another lane's drawings directory.
