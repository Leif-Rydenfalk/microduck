# GOAL — by the morning of 2026-09-02

Leif, 2026-09-01 (verbatim): *"i want to see it animated and ready for
production when i come back tomorrow. working using the open source
simulator for it. fully simulated"* and *"put a workflow on the
electronics, pcb, datasheet, workflow on wiring, assembly and manufacturing
and blueprints and production research. use many workflows and orchestrate
it nicely."*

The goal, as measurable rungs. Each rung is a file that exists and a
command that exits 0; a rung not reached says so in STATUS.md.

| # | rung | proof |
|---|---|---|
| 1 | **Every part on the shelf** — 38 slugs build through `bin/cad part:<slug>`; parametric where rebuilt (PASS vs Pollen's mesh), mesh-backed otherwise | `bin/triad check --all` in this root; `out/render/duck-now_*.png` |
| 2 | **The whole assembly builds in the kernel** and renders — `bin/cad assembly:microduck --render`, 14/14 joints resolved by measurement | `ce-assemblies/microduck/current/joints.json record.resolved == 14` |
| 3 | **Animated** — Pollen's MJCF driven by their own published policy (walk, sit/stand) in MuJoCo, with OUR rebuilt meshes swapped in for every PASSed part, rendered to `out/sim/*.mp4` (+ a GIF for the README) | `out/sim/walk.mp4` exists, ≥ 5 s, frames read back; `out/sim/report.json` with joint ranges hit, no self-collision growth vs the stock model |
| 4 | **Electronics known and checked** — every electronic part on the shelf with its datasheet cited (elec-datasheets), a `cecad.netlist.Design` of the robot that PASSes its checks, the Robot HAT as a ce-pcb board (schematic → layout → DRC → gerbers) | `electronics/README.md`; `bin/pcb` DRC report PASS or a named CANNOT DETERMINE |
| 5 | **Wiring** — the servo daisy chain, IMU board, ToF, codec, camera as a ce-wire design with cable lengths measured off the placements | `wiring/` + `bin/wire` check |
| 6 | **Manufacturing package** — drawings for every printed part (autosheet, verified), print plates with real grams/seconds from ce-slice, construction manual, BOM with prices cited, delivered as one `bin/deliver` package | `out/release/` + `report.json` exit 0 (or the named failing rung) |
| 7 | **Production research** — suppliers, MOQ, moulding vs printing at 1/10/100/1000 units, battery shipping & CE/FCC obligations, packaging, cost roll-up — with sources | `docs/PRODUCTION.md` |
| 8 | **STATUS.md** written last: what is PASS, what is CANNOT DETERMINE, and why | |

Rules: nothing claims done without its proof; a rung the tools cannot reach
tonight is written down as the tool gap it is (P11) rather than faked.
