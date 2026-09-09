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
| 2026-09-09 20:59 CST | v0004 | Frozen: 18 MB supplement to v0003 for Ming's own software. Whole-robot 3MF (70 pieces), assembly STEP (14 placed solids, 10 parts), Print all PLA/TPU 3MF, all-STL zip (30), STEP zip (10 verified parts + servo + HAT), bilingual instructions. STEP verified against the v0003 STLs by FreeCAD; 20 parts remain mesh-only (vendor reference, no solid source). SHA-256 64d8e5aa1d0cdc72e11a83f54793941ed3f0f76dc7af488eb7a1f53542515892. Built by `tools/export_bundles.py` from `research/cad-export-2026-09-09/Microduck-Review-G/` at commit 41f5cbf. Not sent by any agent; Leif sends. | `v0004/VERSION.json`, `v0004/EXPORT REPORT.json` |
| 2026-09-09 | v0005 (in preparation) | Supersedes v0004 before any send. Ming asked (via Leif) for one STP with all the parts and Leif asked for clearly labelled variants plus everything Ming needs for suppliers. Folder 00: STEP 1 whole robot assembled (70 pieces: verified solid CAD, manufacturer servo solids, bearing rings, faceted mesh bodies), STEP 2 all 30 printed parts side by side, STEP 3 real CAD only, STEP 4 one STP per part, 3MF 1-3, STL zip, bilingual guide. Folder 01: brief, BOM xlsx (32 lines + 30 printed parts, tiers 1/10/100), reply sheet, Packets A-F per supplier type with paste-ready EN/中文 requests and files, open decisions, licence. Tools: `tools/export_bundles.py`, `tools/export_assembly_step.py`, `tools/export_supplier_pack.py`, `tools/prepare_export_review.py`. Not sent by any agent. | this log |
