# PRINT — X1 Carbon plates, because the H2S plates do not fit

*Sliced 2026-09-05, BambuStudio 02.08.02.61, by `tools/plate_for_printer.py`.*

**Why this file exists.** `out/print/plates/{PLA,TPU}/*.3mf` are sliced for a **Bambu H2S,
340 × 320**. The machine reachable on the LAN is an **X1 Carbon, 256 × 256 × 250**
(`00M09D4C0101091`, 192.168.1.86, TroubleMaker). Handing the H2S plate to it returns BambuStudio
**return_code −52, "Some objects are located over the boundary of the heated bed."** That is a
refusal, not a warning, and no amount of retrying the same file changes it.

## The plates

| file | objects | note |
|---|---|---|
| `plates/X1C/microduck-PLA-X1C-01.3mf` | 1 | bottom-head-shell |
| `plates/X1C/microduck-PLA-X1C-02.3mf` | 1 | jaw |
| `plates/X1C/microduck-PLA-X1C-03.3mf` | **28** | everything else |
| `plates/X1C/microduck-PLA-X1C-04.3mf` | 1 | top-head-shell — **`--orient 0`** |
| `plates/X1C/microduck-PLA-X1C-05.3mf` | 1 | yaw-roll-motion — **`--orient 0`** |
| `plates/X1C-TPU/microduck-TPU-X1C-01.3mf` | 4 | jaw-soft, soft-mouth-top, sole-left, sole-right |

Presets: `Bambu Lab X1 Carbon 0.4 nozzle` · `0.20mm Standard @BBL X1C` ·
`Bambu PLA Basic @BBL X1C` / **`Bambu TPU 85A @BBL X1C`**.

> **The TPU preset is 85A on purpose.** The X1C's 0.4-nozzle default alias for TPU is **90A**, and
> the first slice silently used it. The soles and the soft mouth were designed and sliced at
> **85A** — a different shore hardness on exactly the parts where compliance is the function. The
> plate was thrown away and re-sliced at 85A. A material substituted by a preset default is still
> a substituted material.

## Two parts refuse auto-orient, and that is recorded rather than worked around
`top-head-shell` and `yaw-roll-motion` both fail with `--orient 1`; `yaw-roll-motion` is the mesh
`PRINT.md` already records as crashing the slicer's auto-orient. Both slice cleanly **as
modelled**, each alone on its own plate.

## VERIFIED BY COUNTING, not by the tool reporting success
The packer printed "OK" for five plates. That is a claim. The check is the `<item>` count inside
each 3MF, mapped to object names through `Metadata/model_settings.config`:

    plate 01  1     plate 02  1     plate 03  28     plate 04  1     plate 05  1
    TOTAL PLACEMENTS 32      EXPECTED 32  (26 slugs, 6 of them x2)
    per-part mismatches: NONE      unexpected objects: NONE
    TPU plate: 4 placements, expected 4 — PASS

**The first version of this check was wrong and said 64.** It counted names in
`model_settings.config`, which lists every object twice — once as `<object>` and once as its
`<part>`. The plates were right and the check was broken. Recorded because a check that reports
double is the same family as one that reports zero: *the number a tool prints is not evidence
until you know what it counted.*

## Sending them
`ce-cad/bin/printsend --file <plate>.3mf --slot 0 --yes`. Upload works (byte-exact). **The X1's
firmware OTA 01.11.02.00 refuses `project_file` with `mqtt message verify failed`** — five payload
variants tested (md5 lower/upper/absent, bare-filename url, `param` with and without `Metadata/`),
all identical, so it is firmware policy and not the payload. **Enable Developer Mode / LAN Mode on
the printer** and it will start.

**TPU cannot print until someone loads it**: AMS0 slot 0 is PLA, slot 1 is PETG, external spool
empty. TPU belongs on the external spool, not through an AMS.
