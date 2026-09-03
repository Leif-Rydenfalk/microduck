# MakerWorld 3250889 — Microduck 机器鸭结构件 (simulation-model export, 15 parts)

Source: https://makerworld.com/en/models/3250889-microduck-robotic-duck-structural-parts-simulation
Downloaded by Leif 2026-09-03 and extracted here the same day.
Original archive: `Microduck+机器鸭结构件（仿真模型导出+·+15+分件）.zip`

The archive stores its filenames in GBK, not UTF-8, and without the zip UTF-8 flag,
so `unzip` on macOS fails with "Illegal byte sequence" on every entry. Extracted with
python zipfile decoding each name as cp437 -> gbk, then NFC-normalised. Reproduce with
`tools/extract_makerworld.py` if the archive is ever re-fetched.

The page title says "仿真模型导出" — SIMULATION MODEL EXPORT. Treat these as exported
from the same simulation source our own CAD was seeded from, NOT as independently
authored manufacturing geometry. That is a claim to verify, not to assume: mesh-compare
each file against our own part of the same name and report the deviation.

## The 15 parts

| # | file | Chinese | English | bytes |
|---|---|---|---|---|
| 01 | `01_躯干主体.stl` | 躯干主体 | torso main body | 6,551,084 |
| 02 | `02_左髋yaw-roll.stl` | 左髋 yaw-roll | left hip, yaw-roll stage | 1,996,084 |
| 03 | `03_左髋roll.stl` | 左髋 roll | left hip, roll stage | 2,097,084 |
| 04 | `04_左大腿.stl` | 左大腿 | left thigh | 2,253,684 |
| 05 | `05_左小腿.stl` | 左小腿 | left shin | 945,184 |
| 06 | `06_左踝脚.stl` | 左踝脚 | left ankle and foot | 3,082,984 |
| 07 | `07_颈根.stl` | 颈根 | neck root | 559,484 |
| 08 | `08_颈俯仰.stl` | 颈俯仰 | neck pitch stage | 1,404,584 |
| 09 | `09_头yaw-roll.stl` | 头 yaw-roll | head yaw-roll stage | 2,594,084 |
| 10 | `10_头部总成.stl` | 头部总成 | **head assembly** | 7,977,084 |
| 11 | `11_右髋yaw-roll.stl` | 右髋 yaw-roll | right hip, yaw-roll stage | 1,996,084 |
| 12 | `12_右髋roll.stl` | 右髋 roll | right hip, roll stage | 2,097,084 |
| 13 | `13_右大腿.stl` | 右大腿 | right thigh | 2,253,684 |
| 14 | `14_右小腿.stl` | 右小腿 | right shin | 945,184 |
| 15 | `15_右踝脚.stl` | 右踝脚 | right ankle and foot | 3,087,484 |

## Why part 10 matters most

GOAL.md names the head as the single biggest geometric blocker: our `top_head_shell`
measures 91.751 x 122.688 x 46.339 mm, far longer front-to-back than the compact domed
head in every product photo, with the eye bezel missing, and it says tooling cut from
that mesh is WRONG. `10_头部总成.stl` is a head assembly from the source. Measure it
before re-modelling anything by photogrammetry — it may settle the blocker outright,
or prove it is the same wrong geometry, and either answer is worth having.

## Handedness check available for free

Parts 02-06 and 11-15 are left/right pairs. Note 02/11, 03/12, 04/13 and 05/14 have
byte-identical sizes while 06/15 differ by 4,500 bytes. That is a measurement waiting
to be taken: are the pairs true mirrors, and is the ankle-foot difference real geometry
or just mesh ordering? Our own shelf ships two ankle revisions (ankle_left Y=36.500 vs
ankle_l_v1 Y=46.500) and GOAL.md finding 4 asks which is current.

## Licence

MakerWorld model pages carry their own licence terms. RECORD THE LICENCE from the source
page before any of this geometry informs a manufactured part, and note it here. Until
that is done, treat these files as reference-only.
