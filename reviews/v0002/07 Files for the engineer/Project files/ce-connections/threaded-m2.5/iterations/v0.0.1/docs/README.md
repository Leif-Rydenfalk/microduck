# connection:threaded-m2.5 — the Microduck's minority fastener

M2.5 ISO metric coarse (60 degree ISO 68-1 profile, pitch 0.45 mm, ISO 261).
Created 2026-09-03 by the electronics-verification lane because
`part:radxa-zero-3w`'s four Ø2.8140 mm mount holes had nothing correct to name.

## Why it exists

`SPEC.md` §4's hole census over Pollen's meshes counts four hole populations:

| measured | count | fasteners.py row it lands on |
|---|---|---|
| Ø2.2 | 77 | M2 close clearance |
| Ø4.4 | 28 | M2 counterbore |
| Ø1.6 | 20 | M2 tap drill |
| Ø2.7 / Ø2.8 | 20 | **M2.5 close (2.70) and normal (2.90) clearance** |

Three of the four are `connection:threaded-m2`. The fourth is not, and
`docs/BOM.md` §4 already buys `M2.5×6 ×20` for it. Before this folder existed,
an interface in that fourth population had to write
`accepts: ["connection:threaded-m2"]` — naming a screw it carries 0.814 mm of
diametral float on — or leave `accepts` empty. Both are wrong answers to a
question with a right one.

Two subsets of the twenty are measured rather than inferred:

- **the three head-close screws** — Ø2.695 clearance + Ø5.500 × 2.824
  counterbore in `bottom_head_shell`, into Ø2.100 × 11.200 thread-forming posts
  with a Ø2.800 × 0.800 lead-in in `top_head_shell`
  (`out/verify/manufacturing_partial.json`). Ø2.100 is the fasteners.py M2.5
  tap drill (2.05) + 0.05.
- **the four compute-board mount holes** — Ø2.8140 mm, sd 0.0125 over the four,
  measured off Radxa RAD-DOC-0084 Rev 1.10 §4 by
  `tools/measure_radxa_drawing.py` (`part:radxa-zero-3w`
  `cad/interfaces.json`, interface `mount_holes`).

## What is derived here, and what it is checked against

`compat.py` evaluates the ISO 68-1 basic profile at P = 0.45 mm. The
coefficients are computed from H = P·√3/2, not typed in:

```
$ python3 compat.py
As derived = 3.390804 mm2; published M2.5 tensile stress area = 3.39 mm2 -> PASS
d2_pitch_mm       derived 2.207716 vs published 2.208 -> PASS
d3_bolt_minor_mm  derived 1.947909 vs published 1.948 -> PASS
D1_nut_minor_mm   derived 2.012861 vs published 2.013 -> PASS
```

Four published figures reproduced by arithmetic that did not use them. Artifact:
`evidence/m2p5-thread-derivation.json`.

## What it refuses

`mate.py`'s `__main__` runs four deliberate breaks and refuses all four
(watched 2026-09-03): an M2 screw, a fine-pitch M2.5 × 0.35, a missing
`provider`, and a provider (`button_head`) whose ce-parts folder does not
exist. The last is the TRIAD rule — a dangling ref is a FAIL, so only
`part:screw-m2.5-iso4762` (on the workshop shelf, 14 lengths verified on a
fetched page) is mapped.

`compat.py` returns **CANNOT DETERMINE** on preload and on engagement unless
the caller supplies measured friction coefficients. Nobody in this workshop has
measured one, at any size. The PLA self-tapped case adds a second unmeasured
number: pull-out of an M2.5 formed thread in a printed Ø2.1 pilot, worse here
than for M2 because `top_head_shell` slices dome-up and the layer planes run
perpendicular to the post axis. A bench pull-out with a scale closes both.

## Trust

T0 untested — 4 ledger entries, 3 PASS and 1 CANNOT DETERMINE, all of them
document reads and derivations. Nothing has been screwed together and pulled
apart. `bin/triad trust connection:threaded-m2.5`.
