# MakerWorld 3250889 — what is in this folder, and what it measured out to be

Read `SOURCE.txt` first (URL, author, licence, dates, what the page does and does
not state). This file is the map of the folder and the one-paragraph result.

## Result (measured 2026-09-03/04, out/sources/makerworld-3250889.json)

The 15 STLs are **not new geometry**. Each is the concatenation of every visual
mesh of one MJCF body of Pollen's `microduck_rl` assets at commit `5946fd9`,
placed at qpos 0 with the trunk at the origin and scaled to mm — servos,
bearings, battery, PCBs, lens and speaker box fused into the printed shells.
Order-matched vertex delta against our own placement of those assets:
**<= 8.4e-6 mm on all 15 files**. Bytes 80..end are **identical** to
`cad/01..15` of `github.com/fanhao375/microduck-replica` at `28d8ee9`; only the
80-byte header differs (MakerWorld stamps `MW 1.0 3250889 US`). The page carries
**no print profile, no BOM, no guide**, and the download needs a login.

## Layout

| path | what |
|---|---|
| `SOURCE.txt` | URL, author, licence, lineage, counters, fetch dates, archive hashes |
| `archive/*.zip` | Leif's logged-in download, 2026-09-03 22:11:54, sha256 `910ac19a…` |
| `files/NN_*.stl` | the 15 STLs extracted by `tools/extract_makerworld.py` (sha256 in `out/sources/makerworld-3250889.json`) |
| `page/api-design-3250889.json` | the MakerWorld design API record — the only machine-readable copy of the page an anonymous client can get |
| `page/page-anonymous-curl-403.html`, `page/page-shot-cloudflare.png` | what the page URL returns without a browser session: a Cloudflare challenge |
| `page/images/` | cover (a product photograph of the Sky colourway), coverPortrait (Hugging Face / Pollen comic art), 15 grey per-file renders |
| `upstream-github-fanhao375-microduck-replica/` | the repo the files come from, pinned at `28d8ee9`: README (zh/en), LICENSE, NOTICE, 零件对照表.json, fastener docs + hole_analysis.json, export/render/analyse scripts, 7 assembly drawings, the 2026-09-02 build photo, `git-tree-<sha>.json`, `repo-metadata.json`, `PINNED-COMMIT.txt` |

## Zip entry names

UTF-8 with the zip UTF-8 flag (flag_bits 0x808), measured on the raw central
directory (`30 32 5f e5 b7 a6` = "02_左"). An earlier version of this file said
GBK; that was wrong. macOS `unzip` still fails under a C locale; use the tool.

## Licence

CC BY-SA-NC (MakerWorld `license: BY-NC-SA`; the replica repo: CC BY-SA-NC 4.0
for `cad/`, Apache-2.0 for `scripts/`; upstream Pollen 3D models CC BY-SA-NC).
Reference material for a reverse-engineering study. Nothing here may go into a
commercial part without a licence review, and nothing here is redistributed as
our own work.
