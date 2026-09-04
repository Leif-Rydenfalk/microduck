# connection:self-tap-m2.5-pla

A M2.5 ISO 4762 cap screw thread-forming its own thread in an FDM-printed Ø2.05 mm pilot.

## What is measured

- 11 pilot holes of this size on Pollen's reference meshes (`out/fasteners/features-by-mesh.json`), measured by `cecad.meshfeatures.features()`.
- The screw: `part:screw-m2.5-iso4762`, built parametrically and measured against the ISO 4762 table (`out/fasteners/screw-parts-verify.json`, 120 rows 0 FAIL).
- Per-instance grip and pilot depth: `out/fasteners/runs.json`.

## What is refused

Preload, tightening torque, strip load and re-insertion count — all four `None`, each with the coupon test that settles it in `connection.json` `record.open_questions`. Heat-set inserts are NOT modelled; see `record.why_not_a_heat_set_insert` for the measurement that refuses them.

## Self-test

`python3 cad/mate.py` — 13 PASS / 0 FAIL, of which 6 are refusals it must make. Log: `evidence/mate-selftest.log`.
