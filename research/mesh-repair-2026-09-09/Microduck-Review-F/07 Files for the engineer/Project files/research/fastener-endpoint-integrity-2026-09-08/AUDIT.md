# Fastener endpoint integrity — 2026-09-08

All 64 formerly null fastener target refs are recoverable from existing source
records without guessing which servo is involved. `fastener_runs.collect()` kept
`body`, `geom_index` and local feature `index` on each transformed hole;
`classify()` discarded that identity when selecting the actual pilot. The source
now carries the selected pilot record into `runs.json`. The placement generator
joins `(body, geom_index, mesh)` to exactly one existing assembly placement. A
missing or duplicate match is refused. The target instance label follows the
existing `cad/assembly.py` body/part-slug/placement-row convention exactly.

There are 20 distinct local pilot anchors across 7 part shelves, used at 64 unique
placed endpoints. Existing shelf interfaces were too coarse to name these pilot
features individually (XL330 had horn, idler and case_screws patterns). Merely
filling refs beside a nonexistent `thread_int` would pass the shallow structural
checker but fail full interface resolution. `tools/gen_pilot_interfaces.py` now
adds individually named `mesh_pilot_<feature index>` records from frozen feature
measurements. The seven shelves all explicitly declare the corresponding
reference-mesh coordinate frame; their full frame statements travel as provenance.

These anchors carry the measured hole center, axis, diameter, depth, extent,
fit residual/coverage and source SHA. They are CANNOT DETERMINE for original
hardware compatibility and reconstructed-CAD correspondence. `accepts` stays
empty, with the reason stated: no actual compatible screw or seating datum is
established. No pitch/material/thread profile was invented. The top-head-shell
source itself warns that this mesh is not the product head; that warning remains.
The nominal assembly connection IDs remain unchanged. Resolving an anchor does
not prove that the actual joint can mate or hold load.

## Sources and outputs

Owning generators: `tools/fastener_runs.py`, `tools/place_fasteners.py`, new
`tools/gen_pilot_interfaces.py`, and new `tools/gen_fastener_verify.py`.
Derived run/placement JSON and assembly joint refs changed; no CAD builder changed.
The exact additive interface paths are:

- `ce-parts/xl330-m288-t/iterations/v0.0.1/cad/interfaces.json` — 8 added
- `ce-parts/microduck-face-part/iterations/v0.0.1/cad/interfaces.json` — 4
- `ce-parts/microduck-top-head-shell/iterations/v0.0.1/cad/interfaces.json` — 3
- `ce-parts/microduck-power-support/iterations/v0.0.1/cad/interfaces.json` — 2
- `ce-parts/microduck-trunk-shell-right/iterations/v0.0.2/cad/interfaces.json` — 1
- `ce-parts/microduck-foot-left/iterations/v0.0.2/cad/interfaces.json` — 1
- `ce-parts/microduck-foot-right/iterations/v0.0.2/cad/interfaces.json` — 1

All 36 prior interface records are preserved byte-for-value after JSON parsing.
The XL330 shelf is Microduck-local, not the shared workshop shelf. The new
`ce-connections/threaded-m2/current/sim/README.md` truthfully documents an empty
simulation directory, existing conditional `compat.py` arithmetic, missing fixture
coverage and absent strength evidence. It supplies no fabricated simulation.

## Verification

Five endpoint tests pass. They call real `cecad.triad.interface()` on every target,
check actual assembly instance labels, independently push mesh-local anchor centers
through source `world-placements.json` R/t and match all 64 selected pilot centers
within 1e-8 mm, refuse missing/duplicate target placements, preserve all old interfaces
and spatial values, and exercise stale-input refusal in a temporary fixture root.
Six preceding thread-identity regressions also pass, including bad-axis refusal
and unsupported identity PASS rejection. No geometry kernel was used or needed.

All 64 previous placed rows match exactly except the additive endpoint provenance;
all unowned assembly records and counts match the saved baseline. Counts remain
134 placements, 78 joints, 45 BOM rows/64 fastener pieces. All refs, length choices,
positions, quaternions and modeled DOF are unchanged.

Actual `triad check assembly:microduck`: PASS, exit 0; the 64 null target-ref
structural failures are gone. This structural result is not fabrication acceptance.
Actual `triad-test assembly:microduck --case evidence/verify.py`: ran and parsed
393 checks, overall CANNOT DETERMINE, exit 2; original thread identity remains
unresolved. Existing connection checker: 62 PASS, 0 FAIL, 2 CANNOT DETERMINE
(missing shelf_cases and fixture), exit 2. `compat.py`'s four conditional ISO
geometry comparisons print PASS; they do not measure the actual screw.

The runner only hashes verify.py, not imported helpers or data. Its first call
reused prior CD evidence; see `triad-test-prior-cached.json`. The new verifier
generator embeds hashes of all 11 helper/data inputs so regeneration changes the
case key; it also refuses stale inputs at execution. The placer refreshes this
verifier after writing assembly records. After editing pilot interfaces or helper
code, run `python3 tools/gen_fastener_verify.py` before triad-test. The final run
was executed, not cached. Runner-owned ledger/transcript/trust updates were made
through triad-test; no computed trust edits were made manually.

## Reproduction

Run, in order, `python3 tools/fastener_runs.py`,
`python3 tools/gen_pilot_interfaces.py`, `python3 tools/place_fasteners.py`.
Then the dedicated tests and normal triad interfaces. `endpoints.json` contains
the per-fastener exact target audit; source hashes and complete logs accompany it.
No physical operations, purchasing or new compatibility assumptions were made.
