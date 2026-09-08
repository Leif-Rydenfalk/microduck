# Readiness claim audit — 2026-09-08

Scope: assembly, tests and public-electronics identity claims in
`tools/gen_readiness.py` and `tools/data/readiness.json`. No print work was changed.
The readiness generator is owned by the root lane and was not edited here.
Line references describe the inspected snapshot; use the named row/key when lines
move during root integration.

## Corrections for root integration

1. **Assembly paragraph, gen_readiness.py ~329–351**: replace “zero-fastener BOM”
   and “assembly BOM carries 0 fastener rows” with computed current evidence:
   45 BOM rows, 7 modeled fastener rows, 64 placed screws; 64 exact pilot target
   references now resolve. A per-run nominal length/endpoint schedule exists in
   out/fasteners/placed.json and assembly joints.json. It is not an original
   per-joint hardware specification: all actual thread identities remain CD.
   Do not say “no screw-by-screw schedule” without that distinction.
   Keep assembly manufacturing NOT_YET; no torque, actual thread/profile or
   original-unit geometry acceptance is established.

2. **Same row's procurement claim**: delete “SOURCING already buys the hardware”,
   “not the purchase order” and equivalent reconciliation text. No purchase was
   made; these are provisional listed quantities. The 325-piece assortment
   includes nuts/inserts and cannot be compared one-for-one with holes or screws.
   It omits 23 nominal modeled screws: M2x5 (12), M2x10 (8), M2.5x8 (3).
   Retail ROBOTIS TAP screws are not established substitutes for ISO metric
   models or proof of original kit contents. Cite
   research/fastener-reconciliation-2026-09-08/AUDIT.md and per-line.csv.

3. **Test row ~357–365**: change hardcoded READY to NOT_YET. There are 44 test
   definitions, 42 EOL entries, 2 explicit EOL exemptions, 18 equipment entries,
   9 sections and 16 open questions. These are definitions, not test completions.
   The inspected generator did explicitly say “0 tests exercised”; I found no
   literal assertion that all 42 passed. The defect is assigning READY TO BUILD
   FROM despite unresolved procedures, and any summary that treats the checklist
   count as completed coverage. Prefer `defined_tests:44`, `defined_eol:42`,
   `completion_status:'CANNOT DETERMINE/no unit-level execution evidence found'`
   rather than an unsupported live assertion that nobody has built a unit.
   Project logs/out/evidence inspection found no EB-04/SN-05/WK-02 unit logs;
   out/testplan/tp2-eol.png is a rendered document image, not test results.

4. **Test procedure readiness**: the old EB-04 instruction connected all devices
   then applied 8.20/6.60 V, and called either measured rail result PASS. EB-05
   used 7.40 V on the connected chain; EB-06 fitted a charged pack and started
   robotd; EN-01 ran a charged pack through shutdown; EN-02 stood/walked while
   commanding the conflicting voltage sweep. Standard XL330 ratings and pinned
   public raw+BATT topology contradict treating these as executable without
   identity/rating review. This lane corrected those five tests to HOLD through
   spec/test-plan.json, generator and TEST-PLAN.html, preserving old rows in
   superseded-power-procedures.json as DO NOT EXECUTE history. EB-02/03 are
   explicitly board-only, pending identified board ratings, with servos disconnected.
   Replace “Executable as a bench procedure once a unit exists” with
   “Defined procedure set; five power tests and their EOL entries HOLD pending
   original identity, rated supply path and reviewed replacement procedures.”

5. **Triad rows ~370–382**: shallow `triad check` PASS proves folder/graph contract
   properties, not READY TO BUILD FROM. In particular assembly:microduck currently
   passes the structural checker while its actual evidence script returns CD
   (393 checks, original thread identity unresolved). Keep `contract_verdict:PASS`
   but classify manufacturing readiness separately, and include the scoped source
   evidence verdict. `out/factory/measure/triad.json` showed only two ledger rows
   in the inspected snapshot, while newer executed evidence exists in
   research/fastener-endpoint-integrity-2026-09-08/triad-test.json: refresh snapshot
   through its owning instrument, never modify computed trust.

6. **PCB grading ~279**: ternary mapping gives READY for every DRC string other
   than FAIL/CD, including the explicitly constructed '?' when the HTML regex
   has no match. Require an explicit PASS plus the other scoped readiness
   conditions; missing/unparseable results must be CD. PCB connectivity/DRC
   alone does not establish original board identity or production release.

7. **readiness.json pcb_notes**:
   - robot-hat.what currently offers “adopt public board or re-route our board”
     as closure. For 1:1, first identify the installed revision; public C1 is a
     conditional source candidate, not proof. Keep its design_status identity CD.
   - imu-to-dxl.design_status should say “No original schematic/BOM/MCU/bridge
     firmware located in inspected official sources on 2026-09-08; local
     STM32G031F6P6 reconstruction is not identified as original.” Replace route/
     write/fab as original closure with exact board IDs/markings/firmware sources.
   - banana-contact.design_status “Passive strip; artwork complete...” is a local
     reconstruction statement, not original-board evidence. State original
     circuit, contacts, pitch, revision and procurement identity unresolved.
     Factory acceptance of local geometry/ENIG does not establish 1:1 identity.
   Cite research/imu-contact-identity-2026-09-08/AUDIT.md.

8. **readiness.json manual_assumptions**: replace “reader must choose” tapped
   thread/insert with identify original hardware; a design choice is not original
   closure. Replace “factory buys a standard M12 holder” with identify original
   camera/holder/attachment and focal settings; a compatible purchase is not 1:1.
   Mic mounting assumption should recognize public onboard MK1 versus an
   unconfirmed external mic, consistent with current harness. The quoted manual
   itself can remain an identified historical source until its owning generator
   updates it; do not present its assumptions as newly measured facts.

9. **readiness.json licence prose**: the blanket factual claim “PCBs are not
   published (SPEC.md:24)” is obsolete: official HAT PCB/BOM/POS/Gerbers are
   archived. Correct publication scope to public HAT family, original target
   revision and IMU/contact-board identity unresolved. This audit does not
   reinterpret licence terms or make new commercial-use determinations.

## Remaining procedure issues, not silently closed

SV-01/EOL and register table expect model number 1200 (M288) and call any other
model wrong, but original M288 versus M077 is unresolved (M077 model1190). A
source-backed original identity gate must precede applying that model-specific
acceptance table. SN-05 already says expected CD on an assembled robot: no
verified direct IMU register path. Its blanket “no firmware exists” statement
should be narrowed to inspected sources. WK-02's 75% simulation criterion is
explicitly a local decision, not a measured original performance threshold.

## This lane's completed guard

`spec/test-plan.json` now has power_execution_hold, five execution_status HOLD
rows, no active higher-voltage steps in those rows, and HOLD EOL entries. The
new tools/testplan_power_guard.py is called by generator selfcheck; the generator
renders a prominent HOLD banner and defined-versus-completed count explanation.
`tools/test_testplan_power_hold.py` has five passing cases: valid held data,
missing hold/false PASS, reintroduced voltage sequence, omitted EOL hold, and
rendered HOLD/no superseded steps. Generator reports 20 checks, zero failures.
TEST-PLAN.html was regenerated; no unit was energized, powered or moved.

## Follow-up implementation completed

Root subsequently authorized this lane to implement items 7–9 in
`tools/data/readiness.json`. The public HAT versus installed-original distinction,
inspected-source scope for IMU, unverified original contact-board circuitry,
original-fastener/camera selection requirements and onboard-versus-external mic
ambiguity now replace the obsolete closure instructions. Licence wording is
unchanged except the obsolete factual claim that PCBs are unpublished, corrected
in both English and Chinese.

SV-01 is now IDENTIFICATION_ONLY: model1200 identifies M288, model1190 identifies
M077, and neither alone proves the original-unit match. Its procedure and readback
list are read-only, preserve observed values and do not prescribe EEPROM writes,
Shutdown changes or automatic restoration to local defaults. Production
configuration PASS is unavailable until original identity and reviewed settings
are established. The old assignment procedure is preserved separately in
superseded-servo-assignment.json as DO NOT EXECUTE provenance. The register table
is visibly labelled local model/runtime reference, not programming authorization.

SN-05 now scopes missing schematic/BOM/firmware/register-path evidence to the
sources inspected on 2026-09-08. WK-02's title, PASS text, EOL description and
criterion_scope explicitly identify a local simulation comparison rather than
original-product acceptance; its preconditions retain the unresolved power hold.

The existing generator guard now refuses loss of these identity/scope distinctions.
Six tests pass, including deliberate false READY, reopened higher-voltage steps,
omitted EOL hold, M288-only identity promotion, universal source-absence language
and original-acceptance promotion. Generator: 20 checks, zero failures. Final
owned files for integration: tools/data/readiness.json; spec/test-plan.json;
tools/gen_test_plan.py; tools/testplan_power_guard.py;
tools/test_testplan_power_hold.py; TEST-PLAN.html; this audit directory.
No edit to tools/gen_readiness.py, physical operation or original-unit completion
claim was made. Overall test/production readiness remains NOT_YET.
