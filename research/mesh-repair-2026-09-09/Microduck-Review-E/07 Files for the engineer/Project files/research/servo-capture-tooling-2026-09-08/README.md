# Offline original-servo evidence intake — 2026-09-08

This tool validates operator-supplied files for corrected SV-01 and the [servo power audit](../servo-power-audit-2026-09-08/AUDIT.md). It has no serial, USB, network, robotd, control-write or hardware interface. It does not authorize a capture operation. The existing SV-01 power/identity prerequisites still apply to the person supplying the evidence.

Run from the Microduck repository:

```sh
python3 tools/testplan_servo_capture.py /path/to/package/manifest.json > /path/to/report.json
```

Exit 1 means invalid/inconsistent submitted evidence; exit 2 means CANNOT DETERMINE. There is no physical PASS or production-acceptance exit. The validator itself only reads regular files and prints JSON; output redirection is an explicit caller action. Files must resolve inside the package directory; paths to devices, FIFOs, outside symlinks and URLs are refused. The report retains submitted observations, including unexpected IDs and duplicate records.

## Existing sources and ownership

Discovery found SV-01 generation and guards at `tools/gen_test_plan.py`, `tools/testplan_power_guard.py` and `tools/test_testplan_power_hold.py`, but no servo snapshot ingestion tool in Microduck tools or the inspected workshop capture/fixture filenames. This extension therefore lives alongside the owning test-plan tools. It reads the current SV-01 readback list and refuses missing coverage or a lost identification-only gate.

`spec/servo-capture-contract.json` pins the archived manufacturer pages and official runtime sources from the power audit by SHA-256. It records unsigned little-endian register widths and decoding units for the union of SV-01 and the audit's read-only capture list. The validator checks those source hashes on every invocation. A regression independently extracts register widths and voltage units from both archived manufacturer HTML control tables and compares expected IDs with the actual pinned Rust array.

The public runtime uses **10–14, 20–24 and 30–34**, fifteen servos, plus IMU **200** separately. These are expected public-runtime IDs, not proof of the target unit's physical mapping. Unlisted observations remain in the report. ID assignment is never performed. Model 1200 maps to standard XL330-M288-T and 1190 to XL330-M077-T; neither proves original-unit correspondence. Unknown models retain raw submissions and require their own control tables; XL330 scaling is not applied to their other registers.

## Manifest and snapshots

The [synthetic manifest](synthetic/manifest.json) and [synthetic register snapshot](synthetic/servo10.json) show the exact format. They contain one fabricated ID10 record, no photographs and no original serial/revision. They intentionally produce missing-evidence findings. Their numbers are parser fixtures, **not programming defaults, measured data or operating instructions**.

Manifest fields:

- `schema: 1`, explicit boolean `synthetic`, `operator`, `sample_id`, timezone-bearing `captured_at`, `original_robot_serial`, `original_robot_revision`, and `runtime_build`. Unknown identity stays null; do not invent a value to populate a field.
- `artifacts`: unique `id`, `kind`, `label`, `sample_id`, package-relative `path`, SHA-256. Use `register_snapshot`, `imu_snapshot` or `photo` kinds. Photo roles requested: `original_robot_identity`, `hat_revision`, `battery_label`, `battery_to_servo_route`. Multiple photos may share a role. Hashes establish bytes, not authenticity, image quality or label readability; these require review.
- `servos`: one record per physical observation, with `observed_id`, observed `joint_label`, `servo_serial` if available, transcribed `label_model`, `label_photos` (artifact IDs), and `snapshot` (artifact ID). Preserve duplicate/conflicting observations for review, rather than silently merging them.
- `imu`: `observed_id` and a separate `snapshot` artifact ID. The IMU JSON records `observed_id`, `sample_id`, timezone-bearing `captured_at`, `communication_errors`, `read_only`, `synthetic`, `raw_observation`, and `format_source`. Missing/nonempty communication-error records and missing/false read-only declarations produce gaps; a synthetic IMU under a nonsynthetic manifest fails provenance consistency. No XL330 register decoding is applied to the bridge. Raw bytes/source description do not establish bridge MCU or firmware identity.

Each servo snapshot contains `observed_id`, `sample_id`, `captured_at`, `read_only`, explicit `communication_errors` (empty list only if none were observed), and a `registers` list. Each register has `address`, original little-endian `raw_hex`, unsigned integer `raw`, decoded numeric `value`, and exact `unit` from the contract. For example register144 bytes `3200` decode to raw50 and **5.0 V**, not50V or5mV. Preserve raw bytes even if decoding is disputed. A mismatch is a FAIL in package validation.

The tool reports standard-model supply telemetry outside3.7–6.0V as a rating conflict. Configurable voltage limits and the Shutdown mask never extend that rating. A missing voltage-protection bit, torque-enabled observation, missing register, missing communication-error record or incomplete label/source capture remains explicit. No fault bits are cleared, supply changed or retest initiated.

## Limits and next review

Original identity, physical joint mapping, firmware provenance, photo authenticity/readability and installed power routing remain CANNOT DETERMINE even when fields and hashes are present. The tool does not read a serial from an image, inspect the actual robot, measure startup/load transients or authenticate an operator. It never updates a triad ledger, trust record, EOL completion or factory readiness. A separate source-backed review must decide what the submitted evidence establishes.

Validation command: `python3 tools/test_testplan_servo_capture.py`. The tests use temporary synthetic files and no hardware. The saved `synthetic-result.json` is an actual validator result, not a physical test report.
