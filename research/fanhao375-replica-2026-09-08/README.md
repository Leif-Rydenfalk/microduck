# The "open-source Microduck" poster, the fanhao375 replica, and what it changes — 2026-09-08

Owner: Claude coordinating session. Trigger: Hans-Joachim Michl (弥汉斯) forwarded a WeChat
Channels video by "AI研究室-帆哥" at 23:48 CST; Leif sent the poster frame with "someone has
already made an open source version".

## 1 · The poster is an AI-generated graphic, not a product sheet

`poster-forwarded-…jpg`. Verdict: generated image. Evidence:
- The applications row and two colour names are garbled glyphs ("由雅版", "紫黄版", "机器人竞赛"
  and "编程学习" half-rendered). Real marketing art does not misspell its own captions.
- Its specs contradict the real robot on every line that can be checked: 16 DOF / STM32F407 /
  650 g / 7.4 V 2000 mAh / ABS + aluminium. The real Microduck is 15 DOF (14 controlled),
  Radxa Zero 3W (RK3566 Linux SoC, needed for ONNX + WebRTC + NPU), 737–780 g, NP-F550 2S,
  printed PLA/TPU. "MD-01" is the only true token; it is the real model number on microduck.shop.
- The channel name says "AI研究室": an AI-content account riding the launch hype.

The video itself cannot be downloaded from here. WeChat Channels media is streamed and the
desktop cache holds only an encrypted bubble record (`cache/2026-09/Message/…/Bubble/7_1788882489_b.dat`,
141 KB) and the 720×540 thumbnail; the message DB is SQLCipher-encrypted. If Leif wants it
anyway: play it full-screen in WeChat and Claude records the screen with
`screencapture -V <seconds> out.mov`. No UI automation of WeChat (outreach freeze).

## 2 · The real "already open source" is two things, and the project already cites one

1. **Pollen Robotics itself.** Software Apache-2.0; the RPI Robot HAT fully open (KiCad,
   Gerber, BOM, placements); 47 STLs + MJCF in `microduck_rl` under **CC BY-NC-SA** (stated only
   in that repo's README, the LICENSE file is Apache-2.0). `imu_to_dxl` board, editable CAD,
   BOM and assembly docs are NOT published.
2. **fanhao375/microduck-replica** (GitHub, created 2026-08-28, the day after launch; 575 stars,
   111 forks, pushed 2026-09-08 12:45 UTC). Cloned to
   `research/fetched/microduck-replica-fanhao375/` (gitignored, 167 MB). Our own
   `research/01-product-and-specs.md` and `02-repos-and-code.md` already cite it; the lanes'
   325-piece fastener list (60/80/40/15 + 50 nuts + 60 inserts + 20 M2.5) is copied from its
   `docs/机械采购清单.md` verbatim. What the lanes had NOT consumed is below.
   "帆哥" ≈ fanhao375 is a name match only, not proven.

Three WeChat groups of 200 are full; group 4 QR is `assets/wechat-group.png` in the clone,
valid until **2026-09-15**. That is 600+ people in China buying exactly our parts list. Leif
should scan it himself. No agent joins groups (freeze).

## 3 · What the replica settles for the Ming list

| Ming item | replica finding | effect |
|---|---|---|
| 7 servos, voltage conflict | **Settled as fact, not a mystery.** Pollen runs XL330 (rated 3.7–6.0 V) directly on +BATT at 6.6–8.2 V, ~37 % over rating, trading heat and life for torque. HAT schematic: J3/J11/J13/J14 power pin = +BATT, only one buck (AP63205, 2 A) and it feeds the Pi. Our servo-power audit found the same topology but kept it "undecidable"; the replica's reading is the plain one. | Stop treating this as blocking. Decide: copy the over-voltage (official ONNX policies were trained under it) or add a 5–6 V stage and retrain. |
| 7 servos, alternative | **Feetech HD-1910-C001**, spec sheet A/0 dated **2026-09-07**, marketed by Feetech as "开源小鸭舵机, custom-developed for the little duck AI toy". 4–8.4 V (matches 2S), 34×20×23 mm (3 mm thinner than XL330), 21 g, 1.47 N·m @7.4 V (≈2.5× XL330), TTL half-duplex 1 Mbps, AMP-3P connector (pin order GND/Vcc/Signal), factory mode 4 "position PD (sim2real)". Pre-sale. Over-current and over-voltage protection ship **disabled**; enable before install. Open: which voltage the torque was measured at, gear ratio, encoder resolution, backlash. Shenzhen company. | This is the third route and probably the right one for a Shenzhen build: local, voltage-matched, near drop-in. Needs a 3 mm shim or pocket edit and a policy retrain since the packet format differs from Dynamixel. Replaces the STS3215 idea (that route = build Open Duck Mini v2 instead). |
| 1 Radxa | Replica recommends **2 GB / 16 GB eMMC** (ALLNET USD 32.90, ≈¥237); storage need ≈3–4 GB; 1 GB is tight with zram logs. Domestic Taobao prices are 3–6× marked up; Lichuang Taishan Pi does not fit the head. | Ask Ming for 2G/16G, accept 1G/32G if that is what is available. Our "all variants unavailable" check stands. |
| 9 bearings | 14 total (11 × 22/16/4, 3 × 15/10/3), Taobao: NBZH 永天轴承 ¥2.2 (539024647147), 鑫燚 NSK both sizes one link ¥5 (670727787832). | Give Ming the links. |
| 12 fasteners | Same 325-piece list we have, plus Taobao sets (广州信邦 600 pcs ¥26.8, 842110292995), M2 heat-set inserts (榕誉 400 pcs ¥22, 1000673642588), insert press tips ¥13, Loctite 243. The replica's own build log (2026-09-02) confirms M2 screws seat in the printed leg parts. | Quantities still unverified (our reconciliation stands), but buying a ¥27 assortment is the correct move; stop quoting screws by the piece. |
| 2 camera | Generic IMX219 ¥32.8 vs Radxa's own ¥130; 15↔22-pin adapter only if the board is 15-pin; buy the shortest cable, the camera and SoC are in the head with no joint between. | Confirms our "shortest cable" line. |
| 11 imu_to_dxl | Replica **designed the board**: STM32G031F8P6 + LSM6DSV16X, 45×22 mm 2-layer, DRC 0, JLC project file `hardware/imu_to_dxl/imu_to_dxl.eprj2`, schematic + PCB PDFs, STEP. Unprototyped. | Send this to Ming/JLC for 5 boards instead of asking Ming to "find the original". |
| 6 HAT | Official KiCad/Gerber/BOM/placements, 4-layer, 47-line BOM. Replica: "you may not need it" (see its §六). | Already in packet A/B. |

## 4 · Licence flag Leif must own

The 3D models are CC BY-NC-SA per Pollen's README. Our packets A/B ask Ming for 100- and
1,000-unit quotes of a 1:1 recreation. Quoting is not selling, but a production run of the
printed geometry would be commercial use of NC material. HAT and software are Apache-2.0 and
fine. Options: (a) prototype only, (b) re-model the mechanicals from our own blueprint (the
ce-cad parts are ours, the STL-derived ones are not), (c) ask Pollen/HF for a licence.
`LICENCE-POSITION.html` in this repo already discusses this; it should be re-read against the
1,000-unit line in the Ming packets.

## 5 · Sources

- https://github.com/fanhao375/microduck-replica (README, PROGRESS.md, docs/执行器选型.md,
  docs/硬件方案逆向.md §五之三 and HD-1910 section, docs/电控采购清单.md, docs/机械采购清单.md,
  NOTICE.md, BUILD-LOG.en.md)
- https://www.microduck.shop/ and /md-01-specifications/ (25 cm, ~780 g, 15 DOF, $399, deposit $119)
- https://pollen-robotics.com/microduck/
- Bilibili BV1Wr4y6TEkB (GTROB开源机器人社区, 2026-08-29) — not the 帆哥 video
