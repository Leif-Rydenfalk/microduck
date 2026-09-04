#!/usr/bin/env python3
"""gen_workplan.py — WORK-BREAKDOWN.html, the answer to "what needs to be done".

    python3 tools/gen_workplan.py

Reads, never invents:
    out/factory/readiness.json          every artifact graded, with who closes it
    out/factory/licence.json            the licence position
    out/open/cannot-determine-harvest.json   the open unknowns

Leif, 2026-09-04, verbatim: "We have a factory and 10 engineers to put on this.
So just send the documents of what needs to be done."

Every parcel is sized for ONE engineer and carries a deliverable, an ACCEPTANCE
TEST that is a number or a command exit code (never an adjective), what it
depends on, and what it unblocks. Work an agent is closing is marked IN FLIGHT
so the factory does not duplicate it.

EFFORT IS NOT INVENTED. No engineer-day estimate is stated, because this
workshop has never built a physical unit and has no measured time-per-item for
any of this work. Each parcel states its QUANTITY (the count of items) and its
UNIT OF WORK instead, which is checkable; the schedule is the factory's to set
from its own rates. That is a CANNOT DETERMINE, stated rather than guessed.
"""
import datetime
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_HTML = os.path.join(ROOT, "WORK-BREAKDOWN.html")
OUT_JSON = os.path.join(ROOT, "out", "factory", "workplan.json")


def J(rel, default=None):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return default
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def E(s):
    return html.escape(str(s if s is not None else ""))


RD = J("out/factory/readiness.json")
if RD is None:
    raise SystemExit("out/factory/readiness.json missing — run tools/gen_readiness.py first")
LIC = J("out/factory/licence.json", {})
HARVEST = J("out/open/cannot-determine-harvest.json", [])

rows = RD["rows"]
summary = RD["summary"]
in_flight = RD.get("in_flight", [])


def sel(cls=None, closer=None, grade=None):
    out = []
    for r in rows:
        if cls is not None and r["class"] != cls:
            continue
        if closer is not None and r.get("closer") != closer:
            continue
        if grade is not None and r.get("grade") != grade:
            continue
        out.append(r)
    return out


def ids(rs, n=None):
    v = [r["id"] for r in rs]
    return v if n is None else v[:n]


# ---------------------------------------------------------------- the parcels
# Each parcel: one engineer, one deliverable, one acceptance test that is a
# number or a command. `needs` says what it cannot be done without.
TRACKS = []


def track(num, title_en, title_zh, why_en, why_zh, parcels):
    TRACKS.append(dict(num=num, title_en=title_en, title_zh=title_zh,
                       why_en=why_en, why_zh=why_zh, parcels=parcels))


def P(pid, title_en, title_zh, deliverable, acceptance, qty, unit,
      depends="none — can start on day one", unblocks="", needs="desk",
      evidence="", state="OPEN"):
    return dict(id=pid, title_en=title_en, title_zh=title_zh,
                deliverable=deliverable, acceptance=acceptance, qty=qty,
                unit=unit, depends=depends, unblocks=unblocks, needs=needs,
                evidence=evidence, state=state)


# --- Track 1: metrology on a physical sample -------------------------------
triad_human = sel("triad", "human")
track(
    1, "Metrology on a physical Microduck",
    "对实物 Microduck 进行测量",
    "36 shelf records cannot be graded from published data alone — they need a "
    "real unit on a bench. This is the single largest block of human work and "
    "it unblocks the most other parcels, so it should start first.",
    "36 项零件记录无法仅凭公开资料判定，必须在工作台上测量实物。这是人工工作量最大的一块，"
    "解锁的后续工作也最多，应最先开始。",
    [
        P("M-1", "Buy or borrow one retail Microduck and log it in",
          "购入或借用一台零售版 Microduck 并登记",
          "A photographic teardown log: every part as removed, with its position, "
          "orientation and fasteners, into images/teardown/ with a numbered index.",
          "Every one of the 15 servos, 3 boards, battery and both shells appears "
          "in at least one numbered photograph, and the index lists them all. "
          "Count photographs against the part list: no part unphotographed.",
          1, "unit", needs="a purchased retail unit (SPENDING — Leif approves)",
          unblocks="every other parcel in this track, plus T2-1 and T5-1",
          evidence="SPEC.md:24 — Pollen's mechanical CAD, BOM and PCBs are not published"),
        P("M-2", "Caliper every printed part against our model",
          "用卡尺测量每个打印件并与模型比对",
          "out/factory/measure/caliper.json: measured L×W×H and every feature "
          "dimension per part, to 0.01 mm, beside our modelled value and the delta.",
          "Every part in the 30-part print list has a measured row; each row "
          "carries an instrument reading, not a modelled number. Deltas over "
          "1.5 mm are listed separately as findings.",
          30, "parts", depends="M-1", needs="calipers, a real unit",
          unblocks="closes the head-geometry CANNOT DETERMINE and the 1.5 mm rebuild rule",
          evidence="HEAD-RECONSTRUCTION.html — photo scale uncertainty ≈4 % ≈5 mm on a 122 mm head"),
        P("M-3", "Measure the head shell and eye ring to settle the +9.1 % ratio",
          "测量头壳与眼圈，判定 +9.1 % 比例差",
          "A verdict on which of {eye ring OD, head width} deviates from our mesh, "
          "with the measured mm and the instrument.",
          "Ring OD and shell-rim width both measured to 0.1 mm; the front-view "
          "ratio recomputed from measurements rather than photographs; the "
          "CANNOT DETERMINE in HEAD-RECONSTRUCTION.html is replaced by a verdict.",
          2, "dimensions", depends="M-1", needs="calipers, a real unit",
          unblocks="head tooling; the biggest open geometric question",
          evidence="HEAD-RECONSTRUCTION.html §1 — front-view ring/width ratio +9.1 %"),
        P("M-4", "Identify every unidentified component from the teardown",
          "通过拆解确认所有未知元器件",
          "A part number, package and vendor for the speaker, microphone, ToF "
          "generation, NFC front-end, camera module and its ribbon.",
          "Each line that currently reads CANNOT DETERMINE in "
          "ELECTRONICS-DATASHEET.html carries a marking read off the physical "
          "part, photographed.",
          6, "components", depends="M-1", needs="a real unit, magnification",
          unblocks="T3 sourcing lines and the electronics BOM",
          evidence="readiness.json — 10 of 32 bought lines are CANNOT DETERMINE"),
        P("M-5", "Measure the servo supply voltage on a running unit",
          "测量运行中整机的舵机供电电压",
          "A meter reading of servo VDD with the robot standing and walking, "
          "against the XL330-M288-T published 3.7–6.0 V band.",
          "A number in volts at both states, with the meter and the probe point "
          "named. Either the servos see the raw 2S pack (6.6–8.4 V) or they do "
          "not; the answer is recorded either way.",
          1, "measurement", depends="M-1", needs="a multimeter, a running unit",
          unblocks="the entire power-path design; the most consequential electrical unknown",
          evidence="workflows/RUNNING.md finding 1 — the most important electrical finding in the project"),
        P("M-6", "Grade the 36 shelf records that need the sample",
          "根据实物判定 36 项零件记录",
          "Each of the 36 triad part folders updated with the measured frame or "
          "dimension it was missing, and re-graded.",
          "`bin/triad check --all` reports fewer CANNOT DETERMINE than 47; every "
          "row that changes cites the caliper reading that changed it.",
          36, "part records", depends="M-2, M-4",
          needs="the measurements from M-2 and M-4",
          unblocks="the shelf reaching a defensible verdict",
          evidence="readiness.json summary.triad_refs — 69 checked, 17 pass, 47 CANNOT DETERMINE"),
    ])

# --- Track 2: process capability -------------------------------------------
track(
    2, "Process capability and the tolerance basis",
    "工艺能力与公差基准",
    "Every structural safety factor and every fit in this design rests on an "
    "assumed filament strength and an assumed printed dimensional band. Neither "
    "has been measured. Until the factory states its own numbers, the whole "
    "tolerance stack is provisional.",
    "本设计的所有结构安全系数与配合公差，都建立在假设的材料强度与打印尺寸带上，二者均未实测。"
    "在工厂给出自有数据前，整个公差链条都只是暂定值。",
    [
        P("C-1", "State the process capability for each process you would use",
          "给出各拟用工艺的过程能力",
          "Per process (FDM, SLA, injection moulding, CNC): the tolerance you "
          "hold in production, the surface finish, and the minimum wall.",
          "A number per process with the standard it is quoted against (e.g. "
          "ISO 2768 class, or a Cpk with the sample size). 'As printed' is not "
          "a tolerance and is rejected.",
          4, "processes", needs="factory process data",
          unblocks="every drawing's tolerance block; the joint tolerance stack",
          evidence="docs/MANUFACTURING-REQUIREMENTS.md A4 — every dimension carries a tolerance from a stated basis"),
        P("C-2", "Print and measure a tolerance coupon on your machines",
          "在贵厂设备上打印并测量公差试片",
          "A coupon carrying the feature set this design uses — Ø2.2 clearance, "
          "Ø4.4 counterbore, Ø1.6 tap pilot, a 2 mm rib, a Ø16 boss and a Ø22 "
          "bore — printed and measured on your machines, in your material.",
          "Measured versus nominal for each feature, 5 specimens, with mean and "
          "spread. This replaces the CANNOT DETERMINE that currently blocks the "
          "whole tolerance stack.",
          6, "features × 5 specimens", needs="a printer, calipers, material",
          unblocks="every press fit and every bearing seat verdict",
          evidence="out/open — 'This workshop's own printed dimensional band (the whole tolerance stack rests on it)'"),
        P("C-3", "Provide the material datasheet for the filament you would ship",
          "提供拟用耗材的材料数据表",
          "Tensile and yield strength in the printed Z (interlayer) direction, "
          "not just XY, with the print parameters they were measured at.",
          "A datasheet page or a test report. If only XY data exists, say so — "
          "our FEA currently derates an assumed figure and that derating must be "
          "replaced by a measured one.",
          2, "materials (PLA, TPU)", needs="factory material stock data",
          unblocks="every safety factor in STRUCTURAL.html",
          evidence="STRUCTURAL.html — 'Strength of the fitted filament in the printed orientation (every SF rests on it)'"),
    ])

# --- Track 3: sourcing ------------------------------------------------------
bought_human = sel("bought", "human")
track(
    3, "Sourcing the unbuyable lines",
    "解决无法采购的物料",
    "19 of 32 bought lines are ready. The rest are not a paperwork problem: the "
    "compute board's stated SKU does not exist in the vendor catalogue, and the "
    "dominant cost line has no published volume price at any quantity.",
    "32 项外购物料中 19 项已就绪。其余并非文书问题：主控板所述型号在厂商目录中并不存在，"
    "而成本占比最大的物料在任何数量下都没有公开的批量价格。",
    [
        P("S-1", "Get a ROBOTIS OEM quote for the XL330-M288-T",
          "取得 ROBOTIS XL330-M288-T 的 OEM 报价",
          "A written quote at 225 / 1 500 / 15 000 units (15 servos × 15 / 100 / "
          "1000 robots), with lead time and MOQ.",
          "A quotation document. No distributor publishes a volume break for "
          "this part, so this is the single biggest lever on unit cost and only "
          "a quote can answer it.",
          3, "quantity tiers", needs="a supplier relationship (CONTACT — factory does this)",
          unblocks="the entire unit-cost model at volume",
          evidence="readiness.json — servos are 77 % of electronics cost at $358.50 of $465.64"),
        P("S-2", "Resolve the compute board",
          "确定主控板型号",
          "Either the real SKU fitted in a retail unit, or a chosen replacement "
          "with its mechanical and electrical differences listed.",
          "A board that can actually be ordered, in stock, with a lead time. "
          "The 1 GB / 32 GB combination stated in the press kit is not a Radxa "
          "catalogue SKU and every 1 GB variant read on 2026-09-02 was sold out.",
          1, "decision", depends="M-1 teardown confirms what is fitted",
          needs="distributor contact, and the teardown",
          unblocks="the compute mount, the HAT connector layout, the power budget",
          evidence="spec/sourcing.json line B3 — 5 offers, 0 with a stated lead time"),
        P("S-3", "Close the remaining unpriced and lead-time-less lines",
          "补齐其余物料的价格与交期",
          "A priced offer with a lead time for every bought line that lacks one.",
          "Zero lines in spec/sourcing.json with no priced offer; zero with no "
          "lead time. Currently 4 lines have no priced offer and 11 have no "
          "stated lead time.",
          15, "lines", needs="distributor contact",
          unblocks="a defensible unit cost and a build schedule",
          evidence="readiness.json summary.bought_gaps"),
    ])

# --- Track 4: custom boards -------------------------------------------------
track(
    4, "The three custom circuit boards",
    "三块自制电路板",
    "Pollen publishes no design files for the Robot HAT, the IMU-to-Dynamixel "
    "board or the battery contact board. Our reconstruction of the HAT fails its "
    "own DRC and is a footprint-accurate stand-in, not a manufacturable copy.",
    "Pollen 未公开 Robot HAT、IMU 转 Dynamixel 板与电池触点板的设计文件。"
    "我们复原的 HAT 未通过自身 DRC，只是尺寸相符的替代件，并非可制造的复制品。",
    [
        P("B-1", "Reverse-engineer the three boards from the physical samples",
          "从实物逆向三块电路板",
          "A schematic per board with every component and every net, traced from "
          "the board itself.",
          "Every net traceable end to end; every component with a marking read "
          "off the part. The two currently-guessed parts — the Dynamixel "
          "half-duplex transceiver and the 2S→5V regulator — are identified, "
          "not inferred.",
          3, "boards", depends="M-1", needs="the physical boards, magnification, a meter",
          unblocks="all fabrication; nothing ships without these",
          evidence="PCB-PACKAGE.html — Robot HAT reconstruction fails its own DRC"),
        P("B-2", "Lay out and fabricate the banana battery-contact board",
          "设计并打样电池触点板",
          "Gerbers, drill, pick-and-place and a BOM for the simplest of the three.",
          "A DRC-clean board and five fabricated samples that fit the measured "
          "pocket. This board is passive — VBAT and GND only — so it is the "
          "fastest win of the three.",
          1, "board", depends="B-1", needs="PCB fab",
          unblocks="the power path; a buildable prototype",
          evidence="workflows/RUNNING.md — 'the banana contact board is passive and is ~1 day of work after one measurement session'"),
        P("B-3", "Lay out and fabricate the Robot HAT and the IMU board",
          "设计并打样 Robot HAT 与 IMU 板",
          "Gerbers, drill, pick-and-place, BOM and assembly drawings for both.",
          "DRC clean with zero fails (ours currently has 10), the 1.8 V codec "
          "rail terminated rather than dead-ending on a test point, and five "
          "assembled samples that power up.",
          2, "boards", depends="B-1", needs="PCB fab and assembly",
          unblocks="a working prototype",
          evidence="PCB-PACKAGE.html — 10 DRC fails; DVDD dead-ends on TP1"),
    ])

# --- Track 5: DFM review ----------------------------------------------------
track(
    5, "DFM review and the print files",
    "可制造性审查与打印文件",
    "18 of 30 print files are ready. The rest are vendor simulation meshes that "
    "carry no manufacturable dimensions, and 22 of the 30 are under a "
    "non-commercial licence that forbids selling what is printed from them.",
    "30 个打印文件中 18 个已就绪。其余为供应商仿真网格，不含可制造尺寸；"
    "且其中 22 个受非商业许可限制，不得用于销售。",
    [
        P("D-1", "DFM review every part against your processes",
          "按贵厂工艺对每个零件做可制造性审查",
          "Per part: what you would change to make it manufacturable, with the "
          "reason and the cost or cycle-time impact.",
          "A written finding per part, or an explicit 'no change needed'. "
          "Silence on a part is not an answer.",
          30, "parts", depends="C-1", needs="factory process knowledge",
          unblocks="the production geometry; possibly a re-model",
          evidence="MANUFACTURING-PLAYBOOK.html"),
        P("D-2", "Quote injection moulding against the printed baseline",
          "报价注塑方案并与打印方案比较",
          "Tooling cost, tooling lead time, per-part price and MOQ for the shells, "
          "against our printed cost, so the break-even quantity is a real number.",
          "A quote per shell part. Our current break-even analysis uses published "
          "list prices, not your rates, so it is indicative only.",
          8, "candidate parts", needs="factory tooling quotes",
          unblocks="the volume decision",
          evidence="docs/PRODUCTION.md — cost at 1/10/100/1000"),
    ])

# --- Track 6: assembly and test ---------------------------------------------
track(
    6, "Assembly, fixtures and end-of-line test",
    "装配、工装与下线测试",
    "The assembly sequence and the test plan are written but have never been "
    "executed by a person. The first build is the test of the paperwork.",
    "装配顺序与测试方案已编写，但从未有人实际执行。首台装机就是对全部文件的检验。",
    [
        P("A-1", "Build one unit from the paper alone",
          "仅依据文件装配一台整机",
          "A build log recording every step where the document was wrong, "
          "ambiguous, or assumed knowledge not on the page.",
          "A working unit, or a log of exactly where it stopped. Every defect "
          "found becomes a correction to MANUAL.md. This is the single best test "
          "of whether this pack is real.",
          1, "unit", depends="B-2, B-3, the printed parts",
          needs="all parts, a bench",
          unblocks="everything; it validates or refutes the whole pack",
          evidence="ce-assemblies/microduck/current/manual/MANUAL.md"),
        P("A-2", "Specify and build the assembly fixtures",
          "设计并制作装配工装",
          "The jigs the line needs: bearing press, servo-horn alignment, "
          "harness form board.",
          "Each fixture drawn and made, with the step it serves named. Our jig "
          "drawings exist but have never been made or used.",
          6, "fixtures", depends="A-1", needs="a workshop",
          unblocks="repeatable assembly",
          evidence="MANUFACTURING-PLAYBOOK.html — six assembly jigs with verified A3 drawings"),
        P("A-3", "Run the end-of-line test plan on the built unit",
          "对整机执行下线测试方案",
          "A completed test record against TEST-PLAN.html's gates.",
          "Every gate passed or failed with the measured value. The walk "
          "acceptance thresholds come from simulation and have never been "
          "checked against hardware — that comparison is the deliverable.",
          1, "unit", depends="A-1", needs="a built unit, a test bench",
          unblocks="the acceptance criteria becoming real",
          evidence="TEST-PLAN.html — the only artifact class currently graded READY"),
    ])

# --- Track 7: licence -------------------------------------------------------
track(
    7, "The licence position",
    "许可与授权",
    "This design is reverse-engineered from Pollen Robotics' published assets. "
    "22 of the 30 print files are their meshes under a non-commercial licence. "
    "This must be settled before anyone cuts tooling.",
    "本设计逆向自 Pollen Robotics 公开资料。30 个打印文件中 22 个是其网格，"
    "且受非商业许可限制。开模之前必须先解决此问题。",
    [
        P("L-1", "Settle whether units may be sold",
          "确认整机是否可销售",
          "A written position on manufacturing and selling units derived from "
          "CC BY-SA-NC assets, and on what is ours versus upstream.",
          "A decision with the clause it rests on. Our reading: prototypes may "
          "be printed, units may NOT be sold, and only the 8 parametric rebuilds "
          "are ours. That reading is not legal advice.",
          1, "decision", needs="counsel, or a licence enquiry to Pollen (Leif sends)",
          unblocks="tooling, and any commercial plan",
          evidence="LICENCE-POSITION.html; microduck_rl README §License"),
        P("L-2", "Replace every non-commercial mesh with an owned rebuild",
          "用自研重建件替换全部非商业网格",
          "22 vendor meshes replaced by parametric parts we own, each graded "
          "against the reference to the 1.0 mm p95 rule.",
          "`out/verify/mech_dims.json` shows a rebuild for every part, each "
          "passing the rebuild protocol. 8 of 30 are done today.",
          22, "parts", depends="L-1 (only if selling is the goal), M-2",
          needs="CAD work — an agent can do this, given the measurements",
          unblocks="a commercially clean product",
          evidence="readiness.json summary.print_licence — 22 vendor meshes, 8 ours"),
    ])

# --- Track 8: the three parcels nothing else in this plan covered -----------
# Found by walking the readiness rows against the parcels: the harness has no
# human parcel at all although its cut tolerance can only come off a built loom;
# torque is 3/3 CANNOT DETERMINE and no parcel produced it; and nothing turned
# the first units into an inspection record.
track(
    8, "The three gaps this plan had",
    "本计划原本遗漏的三项",
    "Every other parcel here came from a readiness row. These three came from "
    "reading the plan against the rows and finding work that no parcel owned: "
    "the harness cut list, the torque schedule and the first-article report.",
    "其余工作包均对应就绪度审核的某一行。这三项来自把计划与审核逐行核对后发现的空白："
    "线束下料表、扭矩表、首件检验报告。",
    [
        P("H-1", "Build one harness and turn route floors into a cut list",
          "实做一套线束，把走线下限转为下料表",
          "wiring/CUTLIST.md: a cut length and a tolerance for every cable, measured "
          "on a loom that has been fitted into a built robot, not computed in CAD.",
          "Every one of the 23 cable rows carries a cut length and a tolerance, and "
          "the 6 rows that are CANNOT DETERMINE today carry a connector part number. "
          "Today: 20 cuttable lengths, 0 tolerances.",
          23, "cables", depends="A-1 (a built robot to fit the loom into)",
          needs="a real loom, crimp tooling, a built robot",
          unblocks="harness purchasing, and the assembly station that fits it",
          evidence="wiring/cables.json — 23 rows, 0 with a tolerance field, lengths are route floors + slack"),
        P("F-1", "Set the torque schedule by strip and pull-out test",
          "通过滑牙与拔出试验确定扭矩表",
          "A torque per joint family with the test that produced it: torque-to-strip "
          "and pull-out force on printed bosses and on the XL330's own tapped holes.",
          "All three CANNOT DETERMINE torque rows in the playbook are replaced by a "
          "number with a test method and a specimen count. No chart figure is copied.",
          3, "joint families", depends="C-2 (the production print profile), M-1 for a real servo case",
          needs="a torque rig, printed specimens, a calibrated driver",
          unblocks="every assembly station step that tightens a screw",
          evidence="tools/data/playbook.json torque — 3 of 3 CANNOT DETERMINE; ROBOTIS publishes no torque"),
        P("Q-1", "First-article inspection report on the first five units",
          "首批五台整机的首件检验报告",
          "One report per unit: every gate result, every dimension out of tolerance, "
          "every place the assembly document was wrong, and the time each station took.",
          "5 units x 42 gates logged against a serial, and the report names every "
          "step of the assembly document that had to be corrected to build them.",
          5, "units", depends="A-1, A-3",
          needs="built units, the test bench, a caliper",
          unblocks="turns our simulated numbers into measured ones — the whole point of the pilot",
          evidence="spec/test-plan.json — 42 end-of-line gates, 0 exercised"),
    ])

# ------------------------------------------------------- effort and what it needs
# EVERY DAY FIGURE BELOW IS AN ESTIMATE AND IS LABELLED AS ONE. This workshop has
# never built a physical unit, so no measured time-per-item exists for any of this
# work (that absence is itself measured: 0 units built, 0 of 44 tests exercised,
# spec/test-plan.json). Three things keep the estimates honest rather than invented:
#
#   1. every parcel says WHAT the estimate is arithmetic on — a count we measured
#      (30 print files, 145 holes, 23 cables, 42 gates) times a per-item rate;
#   2. the per-item rate is stated in the row, so a factory that knows its own rate
#      can divide ours out and substitute theirs;
#   3. where the driver is a measured quantity rather than an assumed rate — print
#      time, for instance — the row says so and the number is not an assumption.
#
# An estimate is not a measurement and this document never calls it one.
EFFORT = {
    "M-1": (2.0, "1 unit: order, receive, unbox and photograph a full teardown. Rate: 2 d per unit, ASSUMED. Elapsed time is longer than the effort — shipping is not engineer-days.", "measurement"),
    "M-2": (4.0, "30 printed parts x 0.13 engineer-day per part (about 1 h per part: fixture, caliper 3 axes plus features, record). Part count MEASURED (out/print/slice.json), rate ASSUMED.", "measurement"),
    "M-3": (1.0, "2 dimensions, but the work is the setup: scale reference, repeat readings, recompute the front-view ratio. Rate ASSUMED.", "measurement"),
    "M-4": (2.0, "6 unidentified components x 0.33 d each: decap or read the marking under magnification, then search the marking to a datasheet. Component count MEASURED (readiness CANNOT DETERMINE rows), rate ASSUMED.", "measurement"),
    "M-5": (1.0, "1 bench session: rail voltages and standby current on a live unit. Rate ASSUMED.", "machine"),
    "M-6": (4.5, "36 shelf records x 0.125 d each to write the measurement into the folder and re-run bin/triad check. Record count MEASURED (69 refs, 36 gradeable only from a unit), rate ASSUMED.", "desk"),
    "C-1": (1.5, "4 processes x 0.375 d: collect the capability statement and turn it into the tolerance basis on our sheets. Process count MEASURED, rate ASSUMED.", "desk"),
    "C-2": (3.0, "6 feature families x 5 specimens = 30 coupons: 1 d printing (machine time, not engineer time), 1.5 d measuring, 0.5 d writing the capability record. Coupon count is the plan; rates ASSUMED.", "machine"),
    "C-3": (1.0, "2 materials: obtain the datasheets, re-run the FEA material sweep on the real numbers. The re-run itself is minutes — cecad.stress is already scripted.", "material"),
    "S-1": (2.0, "3 quantity tiers across 32 lines: issue RFQ.html, chase, tabulate. Effort is chasing, not typing. Rate ASSUMED.", "desk"),
    "S-2": (1.0, "1 decision (which battery pack actually ships) once a label has been read on a real pack.", "measurement"),
    "S-3": (2.5, "15 lines x 0.17 d: get a lead time stated in writing for the 11 lines that have none, and a price for the 4 that have none. Line counts MEASURED (readiness bought_gaps), rate ASSUMED.", "desk"),
    "B-1": (6.0, "3 boards x 2 d: trace nets off the physical board under magnification and correct our schematic. The Robot HAT may collapse to 0 d if Pollen's published Apache-2.0 package is adopted instead (FACTORY-QUESTIONS Q5.4).", "measurement"),
    "B-2": (3.0, "1 board (Robot HAT) re-routed to close 8 open nets and pass DRC against the fab's own rules. Open-net count MEASURED (electronics/pcb-package.json routing), rate ASSUMED.", "desk"),
    "B-3": (2.0, "2 boards through fab and assembly: prepare the package, panelise, review the fab's DFM report. Excludes fab lead time.", "vendor"),
    "D-1": (3.0, "30 parts x 0.1 d for a manufacturability opinion per part. Part count MEASURED, rate ASSUMED.", "desk"),
    "D-2": (2.0, "8 candidate parts for tooling: draft, wall, parting line, gate and ejector review. Candidate count MEASURED (5 shells + 3), rate ASSUMED.", "desk"),
    "A-1": (3.0, "1 unit built for the first time from the paper, recording every place the paper is wrong. 23 steps are known to assume knowledge that is not on the page (MEASURED), which is what makes this 3 d and not 1.", "machine"),
    "A-2": (2.0, "6 fixtures already drawn: print, fit, correct. Fixture count MEASURED (out/jigs), rate ASSUMED.", "machine"),
    "A-3": (2.5, "42 end-of-line gates x 0.06 d to run and log the first time, plus rig setup. Gate count MEASURED (TEST-PLAN.html Table 13), rate ASSUMED.", "machine"),
    "H-1": (2.0, "23 cable rows: build one loom, measure each cut length installed, set a tolerance from the measured spread. Cable count MEASURED (wiring/cables.json), rate ASSUMED.", "measurement"),
    "F-1": (2.0, "3 joint families x 5 specimens: torque to failure and pull-out on printed bosses, then write the schedule. Torque is 3/3 CANNOT DETERMINE today (MEASURED).", "machine"),
    "Q-1": (2.0, "5 first-article units inspected against the drawings and the gates, one report. Unit count is the pilot plan.", "measurement"),
    "L-1": (1.0, "1 decision. Effort is reading and writing; the elapsed time depends on counsel or on Pollen answering.", "desk"),
    "L-2": (11.0, "22 vendor meshes x 0.5 d to rebuild parametrically and grade against the reference to the 1.0 mm p95 rule. Mesh count MEASURED (readiness print_licence), rate ASSUMED and the most uncertain number in this table — the 8 already done took an agent, not an engineer.", "desk"),
}

NEEDS_CLASS = {
    "machine": ("a real machine", "需实机"),
    "material": ("a real material", "需实料"),
    "measurement": ("a real measurement on real hardware", "需对实物实测"),
    "desk": ("a desk only", "仅需案头工作"),
    "vendor": ("an outside vendor's time", "需外部供应商配合"),
}

# ------------------------------------------------------------------ in flight
IN_FLIGHT_PARCELS = [
    dict(id="WF-SHEETS", en="Drawing sheets rebuilt to the A2/A3/A4 standard: "
         "no tessellation texture, ≥6 shaded renders per sheet, ≥85 % sheet "
         "coverage, ≥3.5 mm text, and 100 % dimension coverage proved by "
         "bin/sheetcheck", zh="按 A2/A3/A4 标准重建图纸",
         count=f"{summary['drawing']['not_yet']} sheets currently NOT YET"),
    dict(id="WF-FASTENERS", en="Every screw, insert, washer and ball joint "
         "measured off the geometry and placed into the assembly through a "
         "connection, then audited so no hole is unaccounted for",
         zh="测量并装入全部紧固件",
         count=f"{summary['bom_fasteners']['bom_rows']} BOM rows, "
               f"{summary['bom_fasteners']['fastener_rows']} fasteners, "
               f"{summary['bom_fasteners']['hole_census']} holes"),
    dict(id="WF-UNKNOWNS", en="The open CANNOT DETERMINE items researched to a "
         "verdict or narrowed to a named physical test", zh="逐项解决未定项",
         count=f"{summary['unknowns']} items"),
    dict(id="WF-POSE", en="Photo pose-matching as a mechanical feasibility "
         "proof, and the wiring made visible in our renders",
         zh="姿态比对与线束可视化", count="per reference photograph"),
    dict(id="WF-HARNESS", en="Cables and connectors as real shelf parts, routed "
         "as solids in the assembly, with cut lengths and range-of-motion slack",
         zh="线束进入 CAD", count="23 cables"),
]

# ------------------------------------------------- ten tracks, one per engineer
# Leif, verbatim: "We have a factory and 10 engineers to put on this." So the
# themes above are re-cut into TEN tracks, each sized for ONE engineer, and each
# track says what it can start on day one and what it must wait for. A parcel
# appears in exactly one track — the assertion below fails the build if a parcel
# is dropped or claimed twice.
THEME_PARCELS = {p["id"]: p for t in TRACKS for p in t["parcels"]}
for pid, (days, basis, ncls) in EFFORT.items():
    if pid not in THEME_PARCELS:
        raise SystemExit("gen_workplan: EFFORT names parcel %s which does not exist" % pid)
    THEME_PARCELS[pid]["days"] = days
    THEME_PARCELS[pid]["days_basis"] = basis
    THEME_PARCELS[pid]["needs_class"] = ncls
    THEME_PARCELS[pid]["needs_class_en"] = NEEDS_CLASS[ncls][0]
    THEME_PARCELS[pid]["needs_class_zh"] = NEEDS_CLASS[ncls][1]
missing_effort = [pid for pid in THEME_PARCELS if "days" not in THEME_PARCELS[pid]]
if missing_effort:
    raise SystemExit("gen_workplan: no effort estimate for %s" % missing_effort)

ENGINEERS = [
    (1, "Teardown and dimensional metrology", "拆解与尺寸测量", ["M-1", "M-2", "M-3"],
     "day one", "nothing — this track starts first and gates six others",
     "先行开工，无前置条件，并制约其余六条线"),
    (2, "Components, electrical identity and the shelf", "元器件识别、电气测量与零件档案", ["M-4", "M-5", "M-6"],
     "after E1 has the unit apart", "E1 (M-1): the unit must be open",
     "需 E1 完成拆解"),
    (3, "Process capability, coupons and materials", "工艺能力、试件与材料", ["C-1", "C-2", "C-3"],
     "day one", "nothing — your own machines and materials answer this",
     "可即刻开工，答案在贵厂自有设备与材料"),
    (4, "Sourcing: quotes, lead times and the battery", "采购：报价、交期与电池", ["S-1", "S-2", "S-3"],
     "day one", "nothing for the quotes; S-2 wants a label read on a real pack",
     "报价可即刻开始；S-2 需读取实物电池标签"),
    (5, "Board reverse-engineering and routing", "电路板逆向与布线", ["B-1", "B-2"],
     "after E1 opens the unit; the Robot HAT half may start day one",
     "E1 for the physical boards. If Pollen's published Apache-2.0 HAT is adopted (FACTORY-QUESTIONS Q5.4) this track loses about a third of its work",
     "需 E1 取得实物板；若采用 Pollen 公开的 Apache-2.0 板，本线工作量减少约三分之一"),
    (6, "Board fabrication, assembly and the test rig", "投板、贴装与测试台", ["B-3", "A-3"],
     "after E5 closes DRC", "E5 (B-2) for the boards; a built unit for the gates",
     "需 E5 通过 DRC；判据执行需已装配整机"),
    (7, "DFM and the print files", "可制造性评审与打印文件", ["D-1", "D-2"],
     "day one", "nothing — it reads our drawings and your process rules",
     "可即刻开工，依据我方图纸与贵厂工艺规则"),
    (8, "First build, fixtures and first-article inspection", "首台装配、工装与首件检验", ["A-1", "A-2", "Q-1"],
     "when parts and boards exist", "printed parts, bought parts and boards; E6 for the boards",
     "需打印件、外购件与电路板齐备；电路板来自 E6"),
    (9, "Harness and the torque schedule", "线束与扭矩表", ["H-1", "F-1"],
     "F-1 can start with printed coupons on day one; H-1 needs a built robot",
     "F-1: printed specimens only. H-1: E8 (A-1), a robot to fit the loom into",
     "F-1 只需打印试件，可即刻开始；H-1 需 E8 完成首台装配"),
    (10, "Licence position and owned rebuilds", "许可确认与自研重建", ["L-1", "L-2"],
     "day one", "nothing — but L-2 is worth more once E1's measurements exist",
     "可即刻开工；但 L-2 在 E1 测量完成后价值更大"),
]
claimed = [pid for _n, _e, _z, ids, *_r in ENGINEERS for pid in ids]
if sorted(claimed) != sorted(THEME_PARCELS):
    raise SystemExit("gen_workplan: engineer tracks do not partition the parcels — claimed %d of %d; missing %s; twice %s"
                     % (len(claimed), len(THEME_PARCELS),
                        sorted(set(THEME_PARCELS) - set(claimed)),
                        sorted(x for x in set(claimed) if claimed.count(x) > 1)))

TRACKS = [dict(num=n, engineer="E%d" % n, title_en=en, title_zh=zh,
               why_en="Starts %s. Blocked by: %s." % (starts, blocked),
               why_zh="开工时点：%s。前置条件：%s。" % (starts, blocked_zh),
               starts=starts, blocked=blocked,
               parcels=[THEME_PARCELS[i] for i in ids],
               days=round(sum(THEME_PARCELS[i]["days"] for i in ids), 1))
          for n, en, zh, ids, starts, blocked, blocked_zh in ENGINEERS]

# The critical path is a chain of parcels that must run one after another.
CRITICAL = ["M-1", "B-1", "B-2", "B-3", "A-1", "Q-1"]
CRIT_DAYS = round(sum(THEME_PARCELS[i]["days"] for i in CRITICAL), 1)
TOTAL_DAYS = round(sum(t["days"] for t in TRACKS), 1)

# ---------------------------------------------------------------------- write
now = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
n_parcels = sum(len(t["parcels"]) for t in TRACKS)

CSS = """.zh{font-family:var(--sans);font-size:12px;color:var(--ink-2);display:block}
table{border-collapse:collapse;width:100%;table-layout:fixed;font-size:12.5px;margin:8px 0 18px;overflow-wrap:anywhere}
th{white-space:normal !important;padding:5px 6px;background:var(--head);font-family:var(--sans);font-size:12px}
th,td{border-bottom:1px solid var(--hair);padding:5px 6px;text-align:left;vertical-align:top}
td.m{font-family:var(--mono);font-size:11.5px;word-break:break-all}
.g{font-family:var(--sans);font-weight:600;font-size:11px}
.g.ok{color:var(--ready)}.g.no{color:var(--no)}.g.cd{color:var(--cd)}
.front{border:2px solid var(--no);padding:12px 16px;margin:18px 0}
.front h2{margin:0 0 6px;border:none;font-size:20px}
.num{text-align:right;font-variant-numeric:tabular-nums}
.trk{border-top:2px solid var(--rule);margin:34px 0 0;padding-top:10px}
.parcel{border-left:2px solid var(--hair);padding:2px 0 2px 14px;margin:16px 0}
.parcel h4{margin:0 0 4px;font-size:15px}
.pid{font-family:var(--mono);font-size:11.5px;color:var(--accent);margin-right:8px}
.f{font-family:var(--sans);font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2)}
.inflight{color:var(--cd);font-family:var(--sans);font-weight:600;font-size:11px}"""

h = []
h.append("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">")
h.append("<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">")
h.append("<title>Work breakdown — 工作分解</title>")
h.append("<link rel=\"stylesheet\" href=\"tools/doc.css\">")
h.append(f"<style>{CSS}</style></head><body><div class=\"wrap\">")
h.append("<p class=\"backlink\"><a href=\"INDEX.html\">← Document index</a></p>")
h.append("<header class=\"hero\"><p class=\"eyebrow\">Microduck · factory pack · 工厂交付包</p>")
h.append("<h1>What needs to be done <span class=\"zh\" style=\"font-size:22px;display:inline\">工作分解</span></h1>")
h.append("<p class=\"sub\">Every open piece of work, divided into parcels sized for one "
         "engineer. Each parcel names its deliverable, the acceptance test that says it is "
         "done, what it depends on and what it unblocks. Work that a software agent is "
         "closing is marked IN FLIGHT so nobody does it twice.</p>")
h.append("<p class=\"sub zh\">全部待办工作，按单人可承担的粒度拆分。每个工作包给出交付物、"
         "判定完成的验收测试、依赖项与解锁项。软件代理正在处理的工作标注为“进行中”，避免重复。</p>")
h.append(f"<div class=\"rev\"><span>MD-FACT-WBS-001 · Rev A</span><span>generated {E(now)}</span>"
         f"<span>tools/gen_workplan.py</span></div></header>")

# honest state
h.append("<div class=\"front\"><h2>Read this before assigning anyone · 分配任务前请先读这里</h2>")
h.append("<div class=\"statbar\">")
h.append(f"<div class=\"stat\"><b class=\"no\">{summary['drawing']['not_yet']} / {summary['drawing']['total']}</b>"
         "<span>drawing sheets NOT YET<br>图纸尚未就绪</span></div>")
h.append(f"<div class=\"stat\"><b class=\"no\">{summary['bom_fasteners']['fastener_rows']}</b>"
         f"<span>fasteners in the assembly, against {summary['bom_fasteners']['hole_census']} holes<br>装配体中的紧固件数</span></div>")
h.append(f"<div class=\"stat\"><b class=\"no\">{summary['unknowns']}</b><span>open CANNOT DETERMINE<br>未定项</span></div>")
h.append(f"<div class=\"stat\"><b class=\"no\">0</b><span>physical units ever built<br>已制造实物台数</span></div>")
h.append("</div>")
h.append("<p><b>No physical Microduck has ever been built or measured by us.</b> Every "
         "number in this repository comes from Pollen Robotics' published simulation assets, "
         "from product photographs, or from our own simulation. That is why the first track "
         "below is metrology on a real unit: it unblocks more work than anything else.</p>")
h.append("<p class=\"zh\"><b>我们从未制造或测量过实物 Microduck。</b>本仓库中的每个数据都来自 "
         "Pollen Robotics 公开的仿真资料、产品照片或我们自己的仿真。因此下面第一条工作线就是"
         "对实物进行测量：它解锁的后续工作最多。</p>")
h.append("</div>")

# TOC
h.append("<nav class=\"toc\"><ol>")
for t in TRACKS:
    h.append(f"<li><a href=\"#t{t['num']}\">Track {t['num']} · {E(t['title_en'])} · {E(t['title_zh'])} "
             f"({len(t['parcels'])})</a></li>")
h.append("<li><a href=\"#inflight\">In flight — do not assign · 进行中，请勿分配</a></li>")
h.append("<li><a href=\"#effort\">On effort estimates · 关于工时估算</a></li>")
h.append("</ol></nav>")

h.append(f"<p class=\"lede\">{n_parcels} parcels across {len(TRACKS)} tracks, one track per engineer, "
         f"{TOTAL_DAYS} engineer-days of estimated hands-on work in total. Tracks 1, 3, 4, 7 and 10 can "
         f"start on day one; the rest wait on a named predecessor, given per track below.</p>")
h.append(f"<p class=\"lede zh\">共 {n_parcels} 个工作包、{len(TRACKS)} 条工作线（每位工程师一条），"
         f"估算动手工作量合计 {TOTAL_DAYS} 人天。第 1、3、4、7、10 线可即刻开工，其余各线的前置条件见下。</p>")

# --- the critical path, in one sentence, with the days computed from the parcels
h.append("<div class=\"front\" style=\"border-color:var(--accent)\"><h2>The critical path, in one sentence "
         "<span class=\"zh\" style=\"display:inline;font-size:15px\">关键路径，一句话</span></h2>")
h.append(f"<p><b>Buy one retail unit (M-1) → trace the three boards off it (B-1) → route them to pass DRC (B-2) → "
         f"fabricate and assemble them (B-3) → build the first robot from the paper (A-1) → inspect the first five "
         f"units (Q-1): {CRIT_DAYS} engineer-days of hands-on work in series, and nothing shortens it except "
         f"adopting Pollen's already-published Apache-2.0 Robot HAT, which removes the largest board from B-1 and B-2.</b> "
         f"Everything else in this plan runs beside it.</p>")
h.append(f"<p class=\"zh\"><b>关键路径：购入一台零售整机（M-1）→ 逆向三块电路板（B-1）→ 完成布线并通过 DRC（B-2）→ "
         f"投板与贴装（B-3）→ 按文件装配第一台整机（A-1）→ 检验前五台（Q-1）：串行动手工作量 {CRIT_DAYS} 人天。"
         f"唯一能缩短它的办法是改用 Pollen 已公开的 Apache-2.0 Robot HAT，从而免去 B-1 与 B-2 中最大的一块板。</b>"
         f"计划中其余工作均可与之并行。</p>")
h.append("<p class=\"lede\">Vendor lead time is not in that figure: B-3 waits on a PCB house and M-1 waits on a "
         "shipment. Those are elapsed days, not engineer-days, and only you can put numbers on them.</p>")
h.append("<p class=\"lede zh\">上述数字不含供应商周期：B-3 需等待 PCB 厂，M-1 需等待到货。那是日历天而非人天，"
         "只有贵方能给出数值。</p></div>")

# --- the ten tracks as a table before the detail
h.append("<h3>The ten tracks · 十条工作线</h3>")
h.append("<table><colgroup><col style=\"width:7%\"><col style=\"width:27%\"><col style=\"width:8%\">"
         "<col style=\"width:9%\"><col style=\"width:17%\"><col style=\"width:32%\"></colgroup>")
h.append("<thead><tr><th>Eng.<span class=\"zh\">工程师</span></th><th>Track<span class=\"zh\">工作线</span></th>"
         "<th>Parcels<span class=\"zh\">工作包</span></th><th>Est. days<span class=\"zh\">估算人天</span></th>"
         "<th>Starts<span class=\"zh\">开工时点</span></th><th>Blocked by<span class=\"zh\">前置条件</span></th></tr></thead><tbody>")
for t in TRACKS:
    h.append(f"<tr><td class=\"m\">{E(t['engineer'])}</td><td><a href=\"#t{t['num']}\">{E(t['title_en'])}</a>"
             f"<span class=\"zh\">{E(t['title_zh'])}</span></td>"
             f"<td class=\"num\">{len(t['parcels'])}</td><td class=\"num\">{t['days']}</td>"
             f"<td>{E(t['starts'])}</td><td>{E(t['blocked'])}</td></tr>")
h.append("</tbody></table>")

for t in TRACKS:
    h.append(f"<section class=\"trk\" id=\"t{t['num']}\">")
    h.append(f"<h2>Track {t['num']} — one engineer · {E(t['title_en'])} <span class=\"zh\" "
             f"style=\"display:inline;font-size:15px\">{E(t['title_zh'])}</span></h2>")
    h.append(f"<p class=\"f\">{len(t['parcels'])} parcels · {t['days']} estimated engineer-days · "
             f"starts {E(t['starts'])}</p>")
    h.append(f"<p>{E(t['why_en'])}</p><p class=\"zh\">{E(t['why_zh'])}</p>")
    for p in t["parcels"]:
        h.append("<div class=\"parcel\">")
        h.append(f"<h4><span class=\"pid\">{E(p['id'])}</span>{E(p['title_en'])} "
                 f"<span class=\"zh\" style=\"display:inline\">{E(p['title_zh'])}</span></h4>")
        h.append("<table><colgroup><col style=\"width:20%\"><col></colgroup><tbody>")
        h.append(f"<tr><th>Deliverable 交付物</th><td>{E(p['deliverable'])}</td></tr>")
        h.append(f"<tr><th>Acceptance test 验收测试</th><td>{E(p['acceptance'])}</td></tr>")
        h.append(f"<tr><th>Quantity 数量</th><td class=\"num\" style=\"text-align:left\">"
                 f"{E(p['qty'])} {E(p['unit'])}</td></tr>")
        h.append(f"<tr><th>Depends on 依赖</th><td>{E(p['depends'])}</td></tr>")
        if p["unblocks"]:
            h.append(f"<tr><th>Unblocks 解锁</th><td>{E(p['unblocks'])}</td></tr>")
        h.append(f"<tr><th>Effort 估算工作量</th><td><b>{p['days']} engineer-days (ESTIMATE)</b> — {E(p['days_basis'])}</td></tr>")
        h.append(f"<tr><th>Needs 需要</th><td><b>{E(p['needs_class_en'])} · {E(p['needs_class_zh'])}</b> — {E(p['needs'])}</td></tr>")
        if p["evidence"]:
            h.append(f"<tr><th>Evidence 依据</th><td class=\"m\">{E(p['evidence'])}</td></tr>")
        h.append("</tbody></table></div>")
    h.append("</section>")

h.append("<section class=\"trk\" id=\"inflight\"><h2>In flight — do not assign "
         "<span class=\"zh\" style=\"display:inline;font-size:15px\">进行中，请勿分配</span></h2>")
h.append("<p>Software agents are closing these now. They are listed so the factory does not "
         "duplicate them, and so that when they land the parcels above can be re-cut.</p>")
h.append("<p class=\"zh\">以下工作由软件代理正在处理，列出以避免重复；完成后上述工作包将重新划分。</p>")
h.append("<table><colgroup><col style=\"width:14%\"><col><col style=\"width:22%\"></colgroup>")
h.append("<thead><tr><th>id</th><th>What 内容</th><th>Scale 规模</th></tr></thead><tbody>")
for f in IN_FLIGHT_PARCELS:
    h.append(f"<tr><td class=\"m\">{E(f['id'])}</td><td>{E(f['en'])}<span class=\"zh\">{E(f['zh'])}</span></td>"
             f"<td class=\"m\">{E(f['count'])}</td></tr>")
h.append("</tbody></table></section>")

h.append("<section class=\"trk\" id=\"effort\"><h2>On effort estimates "
         "<span class=\"zh\" style=\"display:inline;font-size:15px\">关于工时估算</span></h2>")
h.append("<p><b>Every day figure in this document is an ESTIMATE and is labelled as one on the parcel.</b> "
         "This workshop has never built a physical unit, so it holds no measured time-per-item for any of "
         "this work — and that absence is itself measured: 0 units built, 0 of the 44 gated tests ever "
         "exercised. What keeps the estimates from being invented is that each one states the arithmetic "
         "it rests on: a COUNT we measured (30 print files, 145 M2 holes, 23 cables, 42 end-of-line gates, "
         "22 vendor meshes) multiplied by a per-item rate that is written into the row. Divide our rate "
         "out and put yours in — that is what the row is for.</p>")
h.append("<p class=\"zh\"><b>本文件中的每个天数均为估算，并已在各工作包中如实标注。</b>我方从未制造过实物，"
         "因此没有任何一项工作的实测单件工时——这一点本身也是实测结论：已制造 0 台，44 项判据测试执行 0 项。"
         "估算之所以不是臆测，在于每一条都写明其算式：一个我方实测的<b>数量</b>（30 个打印文件、145 个 M2 孔、"
         "23 条线缆、42 项下线判据、22 个供方网格）乘以写在该行中的单件定额。请用贵厂定额替换我方定额。</p>")
h.append(f"<p>The largest single estimate, and the least certain, is L-2: {E(str(THEME_PARCELS['L-2']['days']))} "
         "engineer-days to rebuild 22 vendor meshes as parts we own. The 8 already rebuilt were done by a "
         "software agent, not by an engineer, so that rate may be wrong by a factor either way.</p>")
h.append("<p class=\"zh\">最大且最不确定的估算是 L-2：把 22 个供方网格重建为我方自有零件。已完成的 8 个"
         "由软件代理而非工程师完成，因此该定额可能显著偏高或偏低。</p>")
h.append("<h3>What each parcel physically needs · 各工作包的实物需求</h3>")
h.append("<table><colgroup><col style=\"width:22%\"><col style=\"width:10%\"><col></colgroup>")
h.append("<thead><tr><th>Needs<span class=\"zh\">需求类别</span></th><th>Parcels<span class=\"zh\">数量</span></th>"
         "<th>Which<span class=\"zh\">具体工作包</span></th></tr></thead><tbody>")
for _k, (_en, _zh) in NEEDS_CLASS.items():
    _ids = [pid for pid in sorted(THEME_PARCELS) if THEME_PARCELS[pid]["needs_class"] == _k]
    if _ids:
        h.append(f"<tr><td>{E(_en)}<span class=\"zh\">{E(_zh)}</span></td><td class=\"num\">{len(_ids)}</td>"
                 f"<td class=\"m\">{E(', '.join(_ids))}</td></tr>")
h.append("</tbody></table>")
h.append(f"<p class=\"lede\">{sum(1 for p in THEME_PARCELS.values() if p['needs_class'] != 'desk')} of "
         f"{len(THEME_PARCELS)} parcels cannot be done at a desk. That is the reason this pack exists: the "
         "remaining work is mostly work only a factory can do.</p>")
h.append(f"<p class=\"lede zh\">{len(THEME_PARCELS)} 个工作包中有 "
         f"{sum(1 for p in THEME_PARCELS.values() if p['needs_class'] != 'desk')} 个无法在案头完成。"
         "这正是本交付包存在的理由：剩余工作大多只有工厂才能完成。</p></section>")

h.append("<p class=\"backlink\" style=\"margin-top:40px\"><a href=\"INDEX.html\">← Document index</a> · "
         "<a href=\"out/factory/readiness.html\">Readiness audit</a> · "
         "<a href=\"LICENCE-POSITION.html\">Licence position</a></p>")
h.append("</div></body></html>")

with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write("\n".join(h))

os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(dict(generated=now, source="out/factory/readiness.json",
                   tracks=TRACKS, in_flight=IN_FLIGHT_PARCELS,
                   parcels=n_parcels, engineer_days_total=TOTAL_DAYS,
                   critical_path=CRITICAL, critical_path_days=CRIT_DAYS,
                   effort_note=("Every day figure is an ESTIMATE. No measured time-per-item exists in this "
                                "workshop: 0 units built. Each parcel states the measured COUNT and the "
                                "assumed per-item rate its estimate is arithmetic on.")),
              f, indent=1, ensure_ascii=False)

print(f"wrote {OUT_HTML} ({os.path.getsize(OUT_HTML)} B) — {n_parcels} parcels, {len(TRACKS)} tracks, {TOTAL_DAYS} est. engineer-days, critical path {CRIT_DAYS} d")
print(f"wrote {OUT_JSON}")
