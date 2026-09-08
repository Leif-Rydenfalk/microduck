# Original fastener thread verification — 2026-09-08

The former placement PASS did not establish thread identity. `tools/place_fasteners.py`
selected `connection:threaded-m2` whenever an XL330 mesh pilot was not printed PLA,
then supplied M2x0.4 and `self_tapped_boss` itself. It called `mate()` for a transform,
not `compatible()`. Its verification compared position/axis residuals only. Thus the
52 servo runs had a valid nominal-placement check but unsupported thread inputs.
A smooth approximately 1.6 mm pilot does not identify pitch, profile or original screw.

Sources inspected: `tools/place_fasteners.py`, `tools/fastener_runs.py`,
`ce-connections/threaded-m2/current/{connection.json,compat.py,cad/mate.py}`,
`ce-assemblies/microduck/{assembly.json,current/placements.json,current/joints.json,current/bom.json}`,
workshop `TRIAD.md`, `docs/verify-contract.md`, `bin/triad-test`, and
`research/fastener-reconciliation-2026-09-08/AUDIT.md` (archived ROBOTIS kit evidence).
Generic ISO connection compatibility already retains unmeasured preload/engagement
as CANNOT DETERMINE. Its conditional arithmetic was not changed. The assembly's
root PASS is explicitly scoped to 14 hinge graph resolutions, not thread identity.

## Correction

The placement generator retains every nominal part/connection ref, dimension,
length, transform and sequence. It now emits explicit actual-thread identity
CANNOT DETERMINE and separately labels nominal placement PASS. Overall per-placement
verification is CD unless geometry fails, in which case it remains FAIL. The same
identity evidence travels into joint rows and provisional BOM identities. All 64
runs have unknown original hardware identity: 52 servo runs and 12 printed-pilot runs.
No metric/TAP substitution or change in purchasing quantities was made.

`current/evidence/verify.py` follows the marked-verdict contract and calls
`thread_identity.py`. It checks actual generated row coverage/residuals and refuses
missing identity qualifiers or unsupported promotion to PASS. It always reports CD
for these mesh-only original identities; adding measurements will require an explicit
source-backed extension, not simply changing a record's verdict. It does not grade
other assembly gates. FASTENERS.html was regenerated with the identity limitation.

## Verification

- Six dedicated tests pass: real-record CD, false PASS rejection, missing identity/run
  rejection, preservation of geometric FAIL, exact before/after geometry and unowned
  rows, and actual placer refusal for a deliberately reversed insertion axis.
- 64 placed, 0 refused; 52 threaded-m2 / 9 self-tap-m2-pla / 3 self-tap-m2.5-pla.
  All 64 nominal positions/quaternions, refs, lengths and modeled DOF remain exactly
  equal to the saved baseline. Assembly counts remain 134 placements, 78 joints,
  45 BOM rows / 64 fastener pieces. All unowned source rows remain equal.
- Actual `triad-test assembly:microduck --case evidence/verify.py --json`: exit 2,
  CANNOT DETERMINE with marked parsed verdict. See `triad-test.json`.
- Actual `triad check assembly:microduck --json`: exit 1, FAIL, preserves the 64
  pre-existing fastener joint side-b null-ref failures. See `triad-check.json`.
- Existing connection checker: 61 PASS, 1 FAIL (missing sim/README.md), 2 CD (missing
  shelf_cases and fixture). These unrelated missing artifacts were not fabricated.
- Initial runner execution exposed a missing `$verify` marker; its CD evidence is
  retained in `triad-test-initial-unmarked.json` and append-only ledger. Corrected
  entry reran successfully and parsed. Runner owns both ledger rows, test artifacts
  and recomputed trust.json; none were edited manually.

## Remaining closure

Obtain the exact original per-joint screw schedule or inspect original screw profile,
pitch, length and head with the matching boss/servo specification. ROBOTIS retail-kit
TAP contents do not establish screws used in the target unit, and nominal M2 diameter
is not enough to equate TAP and ISO metric threads. No physical action was performed.
