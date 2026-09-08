# PRINT — plates and real slicer numbers for every printed part

*Sliced 2026-09-02 on ce-slice 0.1.0 (BambuStudio 02.08.02.61, http://127.0.0.1:8886). Grams and seconds are the SLICER'S own result.json numbers — never derived from volume. Machine: Bambu Lab H2S 0.4 nozzle; process 0.20mm Standard @BBL H2S; filament Bambu PLA Basic @BBL H2S (1.26 g/cm3) / Bambu TPU 85A @BBL H2S (1.18 g/cm3). Placement: auto-oriented (--orient 1 --allow-rotations) except where noted. Exact reproduce command per part: `out/print/slice.json` + ce-slice journal.*

STLs: `out/print/stl/<material>/<slug>.stl`, binary, **mm** (vendor meshes are metres in the MJCF and were scaled x1000; every bbox re-read and checked against docs/PARTS.md). Source per part is in `out/print/stl_manifest.json`: 8 parts are OUR parametric rebuilds (latest PASS refcheck export); 22 are Pollen's vendor meshes as shelved (CC BY-SA-NC — fine to print, NOT licensed for sale).

## PLA — 26 slugs, 32 pieces, **218.29 g**, 9.93 h of per-piece print time

| part | qty | g/piece | time/piece | g total | orientation rule | note |
|---|---|---|---|---|---|---|
| microduck-ankle-left | 1 | 6.18 | 21m56s | 6.18 | auto-orient: bearing bore vertical | floating regions - enable supports |
| microduck-ankle-right | 1 | 6.18 | 21m54s | 6.18 | auto-orient: bearing bore vertical | floating regions - enable supports |
| microduck-banana-pcb-locker | 1 | 0.68 | 2m20s | 0.68 | bar flat on its 54 mm face, eyes up |  |
| microduck-bearing-roll | 2 | 0.85 | 2m43s | 1.71 | 3 mm plate flat, bore vertical |  |
| microduck-bottom-head-shell | 1 | 28.28 | 59m16s | 28.28 | outer face down per auto-orient | floating cantilever - enable supports |
| microduck-eye-ring | 1 | 2.71 | 5m52s | 2.71 | ring flat on the bed |  |
| microduck-face-part | 1 | 6.64 | 15m09s | 6.64 | face plate back-side down, eyes up |  |
| microduck-foot-left | 1 | 13.35 | 32m53s | 13.35 | sole face down, toes up | floating regions - enable supports |
| microduck-foot-right | 1 | 13.35 | 32m51s | 13.35 | sole face down, toes up | floating regions - enable supports |
| microduck-hip-bracket | 2 | 3.81 | 17m46s | 7.63 | auto-orient: bracket web down, bearing seat vertical |  |
| microduck-jaw | 1 | 10.90 | 31m58s | 10.90 | beak underside down per auto-orient |  |
| microduck-m12-lens-holder | 1 | 1.40 | 6m43s | 1.40 | threaded bore vertical |  |
| microduck-motor-support | 1 | 9.20 | 21m04s | 9.20 | plate flat, servo pockets up | floating cantilever - enable supports |
| microduck-neck-pitch-bracket | 1 | 4.38 | 19m44s | 4.38 | auto-orient: bearing seat vertical | floating regions - enable supports |
| microduck-neck-plate | 2 | 0.55 | 2m06s | 1.10 | 2 mm plate flat on the bed |  |
| microduck-power-support | 1 | 13.15 | 38m21s | 13.15 | auto-orient: tall cradle laid on its back to cut supports | floating regions - enable supports |
| microduck-shin | 2 | 3.60 | 14m28s | 7.20 | 8 mm plate flat, rim walls up |  |
| microduck-top-head-shell | 1 | 34.61 | 68m46s | 34.61 | dome up, rim down (auto-orient confirms) | floating regions - enable supports |
| microduck-trunk-base | 1 | 1.82 | 4m40s | 1.82 | flat plate: largest face down, holes vertical |  |
| microduck-trunk-shell-left | 1 | 13.04 | 29m51s | 13.04 | shell: flat rim (mating face) down, dome up |  |
| microduck-trunk-shell-right | 1 | 12.82 | 29m14s | 12.82 | shell: flat rim (mating face) down, dome up |  |
| microduck-upper-leg-left | 1 | 4.67 | 15m16s | 4.67 | auto-orient: servo cavity opening up | floating cantilever - enable supports |
| microduck-upper-leg-right | 1 | 4.67 | 15m21s | 4.67 | auto-orient: servo cavity opening up | floating cantilever - enable supports |
| microduck-upper-leg-rigidity-plate | 2 | 1.00 | 3m23s | 2.00 | 1 mm plate dead flat on the bed |  |
| microduck-yaw-roll-motion | 1 | 4.71 | 15m33s | 4.71 | auto-orient: both bearing bores vertical | floating regions; sliced AS MODELLED - auto-orient (-100) crashed the slicer on this mesh |
| microduck-yaw2roll | 2 | 2.96 | 13m07s | 5.91 | auto-orient: servo pocket up, bearing bore vertical |  |

## TPU — 4 slugs, 4 pieces, **26.2 g**, 2.41 h of per-piece print time

| part | qty | g/piece | time/piece | g total | orientation rule | note |
|---|---|---|---|---|---|---|
| microduck-jaw-soft | 1 | 8.82 | 44m39s | 8.82 | 8.4 mm lip flat on the bed |  |
| microduck-soft-mouth-top | 1 | 3.24 | 16m51s | 3.24 | 3.3 mm lip flat on the bed |  |
| microduck-sole-left | 1 | 7.07 | 41m37s | 7.07 | sole tread face down, dead flat |  |
| microduck-sole-right | 1 | 7.07 | 41m31s | 7.07 | sole tread face down, dead flat |  |

**Grand total: 30 slugs / 36 pieces / 244.49 g / 12.35 h.** Times are sequential per-piece prints; a plate prints faster than its parts' sum.

## Plates

One plate never mixes filaments: `out/print/plates/PLA/microduck-PLA.3mf` (32 pieces) and `out/print/plates/TPU/microduck-TPU.3mf` (4 pieces), arranged for the H2S bed and read back against it. NOTHING WAS SENT TO A PRINTER — sending needs the machine's LAN access code, deliberately not stored here.

## Flags

- microduck-m12-lens-holder may be a bought part (CANNOT DETERMINE, docs/PARTS.md row 27) - sliced anyway
- TPU durometer is inferred: Pollen says nothing; community says 90-95A; the H2S 0.4 preset resolves to Bambu TPU 85A
- 11 parts carry slicer support warnings - see slicer_warning per part; the 0.20mm Standard preset slices without supports, production plates should enable them

Plate readback: both project files re-opened and their `printable_area`/`printable_height` measured — 340 x 320, h 340 = the H2S bed asked for (PASS, both). PLA plate holds 32 pieces, TPU plate 4.

Print farm: the print-farm MCP (`farm_summary`) is not reachable in this session — no farm tool is registered; the roster used is `ce-cad/cecad/data/printers.json` (H2D 192.168.1.7, X2D 192.168.1.45, H2S 192.168.1.133). Nothing was sent to any printer.
