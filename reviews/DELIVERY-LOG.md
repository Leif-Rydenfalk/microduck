# Review package delivery log

Issued packages are immutable (`AGENTS.md`). This log records what happened to
them in the world, which the packages themselves cannot record. `sent: false`
inside a package means no agent sent it, nothing more.

| Date | Version | Event | Source |
|---|---|---|---|
| 2026-09-08 23:51 CST | v0001 | Frozen. | `v0001-verification.json` |
| 2026-09-09 01:04 CST | v0002 | Frozen, verified after fresh extraction, opened locally for Leif. Not sent by any agent. | `v0002-VERIFICATION.md` |
| 2026-09-09 01:12 CST | v0003 | Frozen from prepared prefix `research/mesh-repair-2026-09-09/Microduck-Review-F/`. Not sent by any agent. | `v0003/VERSION.json` |
| 2026-09-09 | latest (v0003 presumed) | The Microduck is Leif's own design and build; this review package of it was made for Ming and Leif sent it himself. Ming downloaded it. Ming's feedback via Leif: STP files one by one is annoying; wants an export-all for 3D printing and options for SolidWorks, Fusion and other CAD, plus print software, to review in his own tools. Version and channel not recorded by agents; Leif to confirm if needed. | Leif in session, 2026-09-09; `ecosystem/SITUATION.md` |
| 2026-09-09 | v0004 (in preparation) | Export bundles: whole robot 3MF, print-all 3MF per material, all-STL zip, STEP zip of solid-modelled parts, assembly STEP, per-software instructions. Built by `tools/export_bundles.py`. Not sent by any agent. | this log |
