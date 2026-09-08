# microduck-ankle-right — the right ankle bracket

The x-mirror of `part:microduck-ankle-left` — read that part's README for
what the bracket is and how every number was measured. This folder exists
because a mirrored part is its own SKU on the print plate.

## The mirror is measured, not assumed

`ankle_right.stl` vs x-mirrored `ankle_left.stl`: p95 surface distance
0.000 mm, max 0.0087 mm, bbox delta 0.000 mm, no shift
(`out/measure/ankle/mirror-test.json`, 15000 samples). So `cad/part.py`
loads the left bracket's part.py — the single source of measured numbers —
and builds it with `HAND = -1` (mirror about x=0, connectors re-handed).

Graded against its OWN reference mesh
`reference/pollen-microduck-rl/assets/ankle_right.stl`: **p95 0.012 mm both
ways, max 0.081 mm, bbox delta 0.001 mm, 13/13 holes matched**
(`out/refcheck/microduck-ankle-right/r1`, evidence run 2026-09-01T19-04-21Z).

The older `ankle_r_v1.stl` (39.5 x 46.5 x 25.4 mm, 10 mm wider) is a
different bracket no MJCF body references — not this part.

## CANNOT DETERMINE

Same three items as the left bracket: M2 thread form, the roofed slots'
mating feature (in the foot), and the bracket-alone mass.
