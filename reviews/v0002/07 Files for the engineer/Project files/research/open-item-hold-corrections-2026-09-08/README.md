# Open-item instruction corrections

The current harvested queue still contained the historical connected-servo
8.20/6.60 V procedure after the owning test plan placed it on HOLD. Eight rows
now refer to the original identity/power prerequisites and reviewed procedures.
`superseded-rows.json` preserves the original records and whole-file source hash.
No underlying requirement was closed and the list still contains 139 entries.

The list has repeated subjects, including walking performance and servo supply.
Its length is therefore a harvested-entry count, not 139 distinct requirements.
The readiness and reconciliation descriptions now state this limitation.

Factory and work-plan prose also no longer infer that nobody has built a unit
from the absence of test results in a plan. Defined tests and simulation cannot
establish physical 1:1 acceptance. The five held power procedures remain held.

Sources: `spec/test-plan.json`, the servo-power audit, and the preserved rows.
These edits update current instructions; frozen inquiry archives are unchanged.
