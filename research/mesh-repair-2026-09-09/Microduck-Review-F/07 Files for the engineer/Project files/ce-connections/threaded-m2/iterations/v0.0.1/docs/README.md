# connection:threaded-m2 — the Microduck's fastener system

The M2 ISO metric threaded joint: 60° ISO 68-1 profile, 0.4 mm ISO 261
coarse pitch. Shaped after `~/dev/ce-workshop/ce-connections/threaded-m3`
(the workshop's worked example), with every number changed to the M2 row and
each change carrying its source.

## Why this folder exists

REBUILD-PROTOCOL.md §4 named it as work: *"we need `threaded-m2` — say so in
`accepts` and it will be created; a dangling ref is a FAIL that names the
work."* On 2026-09-02, 60+ interfaces across the microduck `ce-parts/` shelf
already declared `accepts: ["connection:threaded-m2"]` (ankle, foot,
power-support, trunk-base, trunk shells, upper legs, rigidity plate,
yaw2roll, bearing-roll, neck plate, motor support, banana-pcb-locker …).

## The numbers, and where each came from

| number | value | source |
|---|---|---|
| nominal d | 2.0 mm | the name; ISO 262 selected size |
| coarse pitch P | 0.40 mm | ISO 261; cross-checked `ce-cad/cecad/fasteners.py:57` M2 row (0.40) |
| d2 (pitch Ø) | 1.740192 mm | DERIVED, d − 0.649519 P from H = P√3/2 (compat.py); published 1.740 |
| d3 (bolt minor) | 1.509252 mm | derived, d − 1.226869 P; published 1.509 |
| D1 (nut minor) | 1.566987 mm | derived, d − 1.082532 P; published 1.567 |
| As (stress area) | 2.0732 mm² | derived (ISO 898-1 definition); published 2.07 |
| tap drill | 1.60 mm | fasteners.py M2 row; matches the Ø1.6 ×20 tap population measured on Pollen's meshes (SPEC.md §4) |
| close clearance | 2.20 mm | fasteners.py M2 row; matches the Ø2.2 ×77 clearance population [SPEC §4] |
| counterbore | 4.40 mm | fasteners.py M2 row; matches the Ø4.4 ×28 c'bore population [SPEC §4] |

Run `python3 compat.py` to reprint the derivation and its four PASS lines
against the published figures (which were quoted as the check, never used as
the source). The frozen artifact is `evidence/m2-thread-derivation.json`.

## The two contracts

- `cad/mate.py` — `mate(a_iface, b_iface, params)`: thread_ext → thread_int,
  F(a)·J·F(b)⁻¹ with the 180° flip; `state: tight` (six DOF closed by
  preload) or `loose` (one helical DOF, 0.4 mm/turn). Refuses a missing
  provider, a wrong size, a fine pitch, an unmapped fastener family.
- `compat.py` — `compatible(a, b)`: names, designation, pitch, hand,
  engagement (reported, not graded), pilot diameter (against the derived D1
  and the 1.60 tap drill), preload (structurally CANNOT DETERMINE without
  measured friction).

## What is still CANNOT DETERMINE, and what would settle it

- **Tightening torque / preload** — needs measured µ_thread, µ_bearing and
  the under-head bearing diameter. Same refusal as threaded-m3 row 0004; no
  friction coefficient has ever been measured in this workshop.
- **Self-tapped PLA pull-out** — the Microduck drives most M2 screws into
  printed Ø1.55–1.65 pilots (measured: power_support Ø1.55 pins, foot
  Ø1.6 × 5.5 pilots, trunk-shell Ø1.6 taps, yaw2roll Ø2.05 ears). Nothing
  says how many N such a formed thread holds; a bench pull-out with a scale
  would settle it and earn T2.
- **Adds beyond the cap screw** — no nut-m2 / insert-m2 folder exists on any
  reachable shelf (checked 2026-09-02), so `mate()` refuses those providers
  by name rather than dangling a ref. Putting those families on a shelf
  unlocks them here with a two-line map change.
