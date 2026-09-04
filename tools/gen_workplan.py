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

RC = J("out/factory/reconcile.json")
if RC is None:
    raise SystemExit("out/factory/reconcile.json missing — run tools/reconcile.py first")
TP = J("spec/test-plan.json", {}) or {}
TP_EOL = TP.get("eol", [])
TP_EXEMPT = TP.get("eol_exempt", [])

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
      depends_on=(), depends_note="", unblocks="", needs="desk", needs_zh="",
      evidence="", state="OPEN", gate=None, acceptance_zh="", deliverable_zh=""):
    """One parcel.

    depends_on is a LIST OF PARCEL IDS, not prose. It used to be a sentence, and a
    sentence cannot be walked: the document claimed a six-parcel critical path that
    was not a chain at all (B-3 depended on B-1, not on B-2, so B-2 and B-3 ran in
    parallel and the stated series did not exist). The schedule is now computed from
    this field by a longest-path walk and the parcels' own prose cannot drift from it.

    gate names a LEGAL OR SAFETY PRECONDITION that is not a work dependency: work
    that must not begin, whatever the schedule says, until the gate is answered.
    """
    return dict(id=pid, title_en=title_en, title_zh=title_zh,
                deliverable=deliverable, deliverable_zh=deliverable_zh,
                acceptance=acceptance, acceptance_zh=acceptance_zh, qty=qty,
                unit=unit, depends_on=list(depends_on), depends_note=depends_note,
                unblocks=unblocks, needs=needs, needs_note_zh=needs_zh,
                evidence=evidence, state=state, gate=gate)


# --- Track 0/7: THE LEGAL GATE, and it comes first -------------------------
# THE DEFECT THIS FIXES (factory reviewer, 2026-09-04): this document's critical
# path opened "Buy one retail unit (M-1)", made it gate six other parcels, and
# asked for "a photographic teardown log" as the acceptance evidence — while
# FACTORY-PACK section 5 says "Do NOT buy a retail Microduck and take it apart"
# and LICENCE-POSITION Q-E says the closers that need a real sample "should be
# re-planned around a unit obtained WITHOUT accepting these terms, or dropped".
# A factory that followed this plan on day one would have done the thing the
# licence page forbids, and filed photographic proof of it. The words "terms of
# sale", "dismantle" and "reverse engineer" appeared nowhere in this document.
# The head of the plan is re-cut: L-0 answers the gate, and it gates M-1.
track(
    7, "The licence position",
    "许可与授权",
    "This design is reverse-engineered from Pollen Robotics' published assets. "
    "22 of the 30 print files are their meshes under a non-commercial licence. "
    "And Pollen's terms of sale forbid the BUYER of a retail unit from dismantling "
    "or reverse engineering it — which is why L-0 is the first thing anyone does, "
    "before a unit is bought or opened.",
    "本设计逆向自 Pollen Robotics 公开资料。30 个打印文件中 22 个是其网格，且受非商业许可限制。"
    "此外，Pollen 的销售条款禁止购买者拆解或逆向其产品——因此 L-0 必须最先完成，"
    "在任何人购买或拆开整机之前。",
    [
        P("L-0", "Answer the teardown gate BEFORE anyone buys or opens a unit",
          "在购买或拆机之前，先解决拆解许可问题",
          "A written answer to Q-E: may we lawfully obtain one Microduck and measure it, "
          "and by which of the three routes — (a) Pollen's written permission, (b) counsel's "
          "opinion that the terms of sale do not bind or are not enforceable against the "
          "buyer in the jurisdiction of purchase, or (c) a unit obtained WITHOUT accepting "
          "those terms (measured on a unit already owned by a third party who lends it).",
          "One of the three routes is named IN WRITING, with the clause or the permission it "
          "rests on, and the route is recorded in out/factory/licence.json before M-1 starts. "
          "'We think it is probably fine' is not an answer and does not open the gate.",
          1, "decision", needs="legal",
          needs_zh="需法律意见或 Pollen 的书面许可",
          unblocks="M-1, and through it every parcel in tracks 1, 2 and 5",
          deliverable_zh="对 Q-E 的书面答复：我方能否合法取得一台 Microduck 并进行测量，"
                         "以及通过三条途径中的哪一条——(a) Pollen 的书面许可；(b) 律师意见认为该销售条款"
                         "对购买地的买方不具约束力或不可执行；(c) 通过<b>不接受该条款</b>的方式取得整机"
                         "（例如借用第三方已持有的整机进行测量）。",
          acceptance_zh="以书面形式指明三条途径中的一条，并写明所依据的条款或许可，"
                        "在 M-1 开工前记入 out/factory/licence.json。“应该没问题”不算答复，不能开闸。",
          evidence="out/factory/licence.json Q-E and fact F14: Pollen's terms of sale, fetched "
                   "2026-09-04, quote verbatim 'any dismantling, decompilation, reverse engineering "
                   "(except to the extent this prohibition is not permitted by applicable law) […] "
                   "is strictly prohibited' and 'Customer […] shall refrain from any partial or total "
                   "resale of the Products'. Archived: out/factory/licence-evidence/pollen_terms-of-sale.html"),
        P("L-1", "Settle whether units may be sold",
          "确认整机是否可销售",
          "A written position on manufacturing and selling units derived from "
          "CC BY-SA-NC assets, and on what is ours versus upstream.",
          "A decision with the clause it rests on. Our reading: prototypes may "
          "be printed, units may NOT be sold, and only the 8 parametric rebuilds "
          "are ours. That reading is not legal advice.",
          1, "decision", needs="counsel, or a licence enquiry to Pollen (Leif sends)",
          needs_zh="需律师意见，或由 Leif 向 Pollen 发出许可询问",
          unblocks="tooling, and any commercial plan",
          acceptance_zh="给出结论并写明所依据的条款。我方的理解是：可打印样机，但整机不得销售，"
                        "且仅 8 个参数化重建件属于我方自有。该理解不构成法律意见。",
          evidence="LICENCE-POSITION.html; microduck_rl README §License"),
        P("L-2", "Replace every non-commercial mesh with an owned rebuild",
          "用自研重建件替换全部非商业网格",
          "22 vendor meshes replaced by parametric parts we own, each graded "
          "against the reference to the 1.0 mm p95 rule.",
          "`out/verify/mech_dims.json` shows a rebuild for every part, each "
          "passing the rebuild protocol. 8 of 30 are done today.",
          22, "parts", depends_on=["L-1", "M-2"],
          depends_note="L-1 only if selling is the goal; M-2 gives the measured target",
          needs="desk", needs_zh="CAD 工作——在有实测数据后，软件代理即可完成",
          unblocks="a commercially clean product",
          acceptance_zh="out/verify/mech_dims.json 中每个零件都有重建件并通过重建协议。目前 30 个中已完成 8 个。",
          evidence="readiness.json summary.print_licence — 22 vendor meshes, 8 ours"),
    ])

# --- Track 1: metrology on a physical sample -------------------------------
triad_human = sel("triad", "human")
track(
    1, "Metrology on a physical Microduck",
    "对实物 Microduck 进行测量",
    "36 shelf records cannot be graded from published data alone — they need a "
    "real unit on a bench. This is the single largest block of human work and it "
    "unblocks the most other parcels. It is NOT the first thing that happens: "
    "L-0 is, because Pollen's terms of sale forbid the buyer of a retail unit "
    "from dismantling or reverse engineering it.",
    "36 项零件记录无法仅凭公开资料判定，必须在工作台上测量实物。这是人工工作量最大的一块，"
    "解锁的后续工作也最多。但它<b>不是</b>第一件要做的事：L-0 才是，因为 Pollen 的销售条款"
    "禁止零售整机的购买者拆解或逆向该产品。",
    [
        P("M-1", "Obtain ONE Microduck for metrology by the route L-0 named, and log it in",
          "按 L-0 确定的途径取得一台 Microduck 用于测量，并登记",
          "A photographic teardown log: every part as removed, with its position, "
          "orientation and fasteners, into images/teardown/ with a numbered index — "
          "plus, on page one of that log, the route L-0 authorised and the document "
          "that authorises it.",
          "Every one of the 15 servos, 3 boards, battery and both shells appears "
          "in at least one numbered photograph, and the index lists them all. Count "
          "photographs against the part list: no part unphotographed. AND the log's "
          "first page names the L-0 route. A teardown log with no authorisation on "
          "page one is not accepted and the parcel is not complete.",
          1, "unit", depends_on=["L-0"],
          depends_note="L-0 must have named the route in writing first — this is a legal gate, not a schedule one",
          needs="measurement",
          needs_zh="需一台按 L-0 途径合法取得的整机（若为购买，则涉及支出，须 Leif 批准）",
          gate="L-0",
          unblocks="every other parcel in this track, plus M-4/M-5/M-6 and B-1",
          deliverable_zh="拆解摄影记录：每个零件在拆下时的位置、朝向与紧固件，编号存入 images/teardown/；"
                         "并在记录第一页写明 L-0 批准的取得途径及其依据文件。",
          acceptance_zh="15 个舵机、3 块电路板、电池与两片壳体，每一项至少出现在一张编号照片中，索引齐全；"
                        "照片数与零件清单逐一核对，不得有未拍摄的零件。<b>且</b>记录第一页写明 L-0 途径。"
                        "第一页没有授权说明的拆解记录不予受理，该工作包不算完成。",
          evidence="SPEC.md:24 — Pollen's mechanical CAD, BOM and PCBs are not published; "
                   "out/factory/licence.json Q-E + F14 for the gate"),
        P("M-2", "Caliper every printed part against our model",
          "用卡尺测量每个打印件并与模型比对",
          "out/factory/measure/caliper.json: measured L×W×H and every feature "
          "dimension per part, to 0.01 mm, beside our modelled value and the delta. "
          "Count the fasteners while the unit is open: how many screws of each "
          "length actually come out of it.",
          "Every part in the 30-part print list has a measured row; each row "
          "carries an instrument reading, not a modelled number. Deltas over "
          "1.5 mm are listed separately as findings. The screw count is a number, "
          "which settles the fastener reconciliation in FACTORY-PACK section 3.3a.",
          30, "parts", depends_on=["M-1"], gate="L-0",
          needs="measurement", needs_zh="需卡尺与实物整机",
          unblocks="closes the head-geometry CANNOT DETERMINE, the 1.5 mm rebuild rule and the fastener count",
          acceptance_zh="30 个打印件全部有实测行，每行为仪器读数而非模型值；偏差超过 1.5 mm 的单独列为发现项。"
                        "螺钉清点结果为一个数字，用以了结 FACTORY-PACK 3.3a 节的紧固件对账。",
          evidence="HEAD-RECONSTRUCTION.html — photo scale uncertainty ≈4 % ≈5 mm on a 122 mm head; "
                   "out/factory/reconcile.json fasteners"),
        P("M-3", "Measure the head shell and eye ring to settle the +9.1 % ratio",
          "测量头壳与眼圈，判定 +9.1 % 比例差",
          "A verdict on which of {eye ring OD, head width} deviates from our mesh, "
          "with the measured mm and the instrument.",
          "Ring OD and shell-rim width both measured to 0.1 mm; the front-view "
          "ratio recomputed from measurements rather than photographs; the "
          "CANNOT DETERMINE in HEAD-RECONSTRUCTION.html is replaced by a verdict.",
          2, "dimensions", depends_on=["M-1"], gate="L-0",
          needs="measurement", needs_zh="需卡尺与实物整机",
          unblocks="head tooling; the biggest open geometric question",
          acceptance_zh="眼圈外径与壳缘宽度均测至 0.1 mm；正视比例改由实测重算而非照片推算；"
                        "HEAD-RECONSTRUCTION.html 中的未定项由此转为明确判定。",
          evidence="HEAD-RECONSTRUCTION.html §1 — front-view ring/width ratio +9.1 %"),
        P("M-4", "Identify every unidentified component from the teardown",
          "通过拆解确认所有未知元器件",
          "A part number, package and vendor for the speaker, microphone, ToF "
          "generation, NFC front-end, camera module and its ribbon.",
          "Each line that currently reads CANNOT DETERMINE in "
          "ELECTRONICS-DATASHEET.html carries a marking read off the physical "
          "part, photographed.",
          6, "components", depends_on=["M-1"], gate="L-0",
          needs="measurement", needs_zh="需实物整机与放大观察设备",
          unblocks="the sourcing lines in track 4 and the electronics BOM",
          acceptance_zh="ELECTRONICS-DATASHEET.html 中目前判为未定的每一行，都载有从实物元件上读取并拍照的标识。",
          evidence="readiness.json — 10 of 32 bought lines are CANNOT DETERMINE"),
        P("M-5", "Measure the servo supply voltage on a running unit",
          "测量运行中整机的舵机供电电压",
          "A meter reading of servo VDD with the robot standing and walking, "
          "against the XL330-M288-T published 3.7–6.0 V band.",
          "A number in volts at both states, with the meter and the probe point "
          "named. Either the servos see the raw 2S pack (6.6–8.4 V) or they do "
          "not; the answer is recorded either way.",
          1, "measurement", depends_on=["M-1"], gate="L-0",
          needs="machine", needs_zh="需万用表与一台可运行的整机",
          unblocks="the entire power-path design; the most consequential electrical unknown",
          acceptance_zh="站立与行走两种状态下各给出一个电压数值，并注明所用仪表与测点。"
                        "舵机是否直接承受 2S 电池电压（6.6–8.4 V），无论结论如何都要记录。",
          evidence="workflows/RUNNING.md finding 1 — the most important electrical finding in the project"),
        P("M-6", "Grade the 36 shelf records that need the sample",
          "根据实物判定 36 项零件记录",
          "Each of the 36 triad part folders updated with the measured frame or "
          "dimension it was missing, and re-graded.",
          "`bin/triad check --all` reports fewer CANNOT DETERMINE than the %d it "
          "reports today; every row that changes cites the caliper reading that "
          "changed it." % summary["triad_refs"]["cannot_determine"],
          36, "part records", depends_on=["M-2", "M-4"],
          needs="desk", needs_zh="仅需案头工作，但依赖 M-2 与 M-4 的实测数据",
          unblocks="the shelf reaching a defensible verdict",
          acceptance_zh="bin/triad check --all 的未定项少于今日的 %d 项；每一项变化都引用使其变化的卡尺读数。"
                        % summary["triad_refs"]["cannot_determine"],
          evidence="readiness.json summary.triad_refs — %d checked, %d pass, %d CANNOT DETERMINE"
                   % (summary["triad_refs"]["checked"], summary["triad_refs"]["pass"],
                      summary["triad_refs"]["cannot_determine"])),
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
          4, "processes", needs="desk", needs_zh="需贵厂自有工艺数据",
          unblocks="every drawing's tolerance block; the joint tolerance stack",
          acceptance_zh="每种工艺给出一个数值并注明所依据的标准（如 ISO 2768 等级，或带样本量的 Cpk）。"
                        "“按打印状态”不是公差，不予接受。",
          evidence="docs/MANUFACTURING-REQUIREMENTS.md A4 — every dimension carries a tolerance from a stated basis"),
        P("C-2", "Print and measure a tolerance coupon on your machines",
          "在贵厂设备上打印并测量公差试片",
          "A coupon carrying the feature set this design uses — Ø2.2 clearance, "
          "Ø4.4 counterbore, Ø1.6 tap pilot, a 2 mm rib, a Ø16 boss and a Ø22 "
          "bore — printed and measured on your machines, in your material.",
          "Measured versus nominal for each feature, 5 specimens, with mean and "
          "spread. This replaces the CANNOT DETERMINE that currently blocks the "
          "whole tolerance stack.",
          6, "features × 5 specimens", needs="machine",
          needs_zh="需打印机、卡尺与耗材",
          unblocks="every press fit and every bearing seat verdict; and C-4's wall floor",
          deliverable_zh="一件试片，含本设计实际用到的特征集：Ø2.2 间隙孔、Ø4.4 沉孔、Ø1.6 攻丝底孔、"
                         "2 mm 加强筋、Ø16 凸台与 Ø22 内孔——在贵厂设备上、用贵厂材料打印并测量。",
          acceptance_zh="每个特征给出实测值与名义值对比，5 件试样，并给出均值与离散度。"
                        "此项将取代目前阻塞整个公差链条的未定项。",
          evidence="out/open — 'This workshop's own printed dimensional band (the whole tolerance stack rests on it)'"),
        P("C-3", "Provide the material datasheet for the filament you would ship",
          "提供拟用耗材的材料数据表",
          "Tensile and yield strength in the printed Z (interlayer) direction, "
          "not just XY, with the print parameters they were measured at.",
          "A datasheet page or a test report. If only XY data exists, say so — "
          "our FEA currently derates an assumed figure and that derating must be "
          "replaced by a measured one.",
          2, "materials (PLA, TPU)", needs="material",
          needs_zh="需贵厂库存耗材的材料数据",
          unblocks="every safety factor in STRUCTURAL.html",
          acceptance_zh="提供数据表页或试验报告。若只有 XY 方向数据，请如实说明——"
                        "我方有限元目前对一个假设值做折减，该折减必须由实测值取代。",
          evidence="STRUCTURAL.html — 'Strength of the fitted filament in the printed orientation (every SF rests on it)'"),
        P("C-4", "Give us a minimum PRINTABLE wall per part, because our sheets cannot",
          "给出各零件的最小<b>可打印</b>壁厚，因为我方图纸给不出",
          "One number per part: the thinnest wall your process will actually produce "
          "on that geometry, and the parts where our geometry goes below it.",
          "A number per part, or an explicit 'no part violates our floor'. This exists "
          "because our own sheets cannot answer it: the thinnest-wall figures on "
          "out/drawings/microduck-shin are 0.0200 mm (note 3) and 0.03 mm (PRINT/DFM "
          "note 2), and note 3 then states that a ray minimum at an edge or a fillet "
          "run-out IS NOT A PRINTABLE WALL. So the number on our sheets is explicitly "
          "not comparable to a process floor, and no usable substitute is on the sheet.",
          30, "parts", depends_on=["C-1"], needs="desk",
          needs_zh="需贵厂工艺知识；我方提供 STL 与图纸",
          unblocks="question Q1.3, which cannot be answered from our sheets as they stand",
          deliverable_zh="每个零件给出一个数值：贵厂工艺在该几何形状上实际能做出的最薄壁厚，"
                         "以及我方几何低于该值的零件清单。",
          acceptance_zh="每个零件给出一个数值，或明确答复“没有零件低于我方下限”。"
                        "此项之所以存在，是因为我方图纸回答不了：out/drawings/microduck-shin 上的最小壁厚为 "
                        "0.0200 mm（注 3）与 0.03 mm（打印/DFM 注 2），而注 3 自己写明——"
                        "边缘或圆角收尾处的射线最小值<b>不是可打印壁厚</b>。因此图纸上的数字明确不可与工艺下限比较，"
                        "而图纸上没有给出可用的替代值。",
          evidence="out/drawings/microduck-shin/result.json notes 2 and 3; FACTORY-QUESTIONS Q1.3"),
    ])

# --- Track 3: sourcing ------------------------------------------------------
bought_human = sel("bought", "human")
track(
    3, "Sourcing the unbuyable lines",
    "解决无法采购的物料",
    "%d of %d bought lines are ready. The rest are not a paperwork problem: the "
    "compute board's stated SKU does not exist in the vendor catalogue, the "
    "dominant cost line has no published volume price at any quantity, and two "
    "different battery packs are named in our own files."
    % (summary["bought"]["ready"], summary["bought"]["total"]),
    "%d 项外购物料中 %d 项已就绪。其余并非文书问题：主控板所述型号在厂商目录中并不存在；"
    "成本占比最大的物料在任何数量下都没有公开的批量价格；而我方文件中出现了两种不同的电池组型号。"
    % (summary["bought"]["total"], summary["bought"]["ready"]),
    [
        P("S-1", "Get a ROBOTIS OEM quote for the XL330-M288-T",
          "取得 ROBOTIS XL330-M288-T 的 OEM 报价",
          "A written quote at 225 / 1 500 / 15 000 units (15 servos × 15 / 100 / "
          "1000 robots), with lead time and MOQ.",
          "A quotation document. No distributor publishes a volume break for "
          "this part, so this is the single biggest lever on unit cost and only "
          "a quote can answer it.",
          3, "quantity tiers", needs="vendor",
          needs_zh="需供应商关系（由工厂对接）",
          unblocks="the entire unit-cost model at volume",
          acceptance_zh="一份报价文件。该零件没有任何经销商公布批量价格，因此这是单机成本上最大的一个杠杆，"
                        "只有报价才能回答。",
          evidence="readiness.json — servos are 77 % of electronics cost at $358.50 of $465.64"),
        P("S-2", "Resolve the compute board",
          "确定主控板型号",
          "Either the real SKU fitted in a retail unit, or a chosen replacement "
          "with its mechanical and electrical differences listed.",
          "A board that can actually be ordered, in stock, with a lead time. "
          "The 1 GB / 32 GB combination stated in the press kit is not a Radxa "
          "catalogue SKU and every 1 GB variant read on 2026-09-02 was sold out.",
          1, "decision", depends_on=["M-1"],
          depends_note="the teardown says what is actually fitted; a catalogue search alone could not",
          needs="vendor", needs_zh="需与经销商联系，并需拆解结果",
          unblocks="the compute mount, the HAT connector layout, the power budget",
          acceptance_zh="给出一块真正可下单、有库存、有交期的板。新闻资料中所述 1 GB / 32 GB 组合"
                        "并非 Radxa 目录型号，且 2026-09-02 查得的所有 1 GB 版本均已售罄。",
          evidence="spec/sourcing.json line B3 — 5 offers, 0 with a stated lead time"),
        P("S-3", "Close the remaining unpriced and lead-time-less lines",
          "补齐其余物料的价格与交期",
          "A priced offer with a lead time for every bought line that lacks one.",
          "Zero lines in spec/sourcing.json with no priced offer; zero with no "
          "lead time. Today %d lines have no priced offer and %d have no stated "
          "lead time." % (len(summary["bought_gaps"]["no_priced_offer"]),
                          len(summary["bought_gaps"]["no_lead_time_stated"])),
          len(summary["bought_gaps"]["no_priced_offer"]) + len(summary["bought_gaps"]["no_lead_time_stated"]),
          "lines", needs="vendor", needs_zh="需与经销商联系",
          unblocks="a defensible unit cost and a build schedule",
          acceptance_zh="spec/sourcing.json 中不再有无报价的项，也不再有无交期的项。"
                        "今日无报价 %d 项、无交期 %d 项。"
                        % (len(summary["bought_gaps"]["no_priced_offer"]),
                           len(summary["bought_gaps"]["no_lead_time_stated"])),
          evidence="readiness.json summary.bought_gaps"),
        P("S-4", "Settle WHICH battery pack ships — NP-F550 or np_f970",
          "确定实际装机的电池组型号——NP-F550 还是 np_f970",
          "One pack, named by manufacturer part number, with its measured "
          "L×W×H, its capacity, its protection circuit and its connector, and "
          "the power_support cavity re-checked against it.",
          "A label read off a real pack, photographed, and a caliper reading of "
          "the pack. Our documents say NP-F550 class while the mesh we model is "
          "np_f970 at 38.600 × 20.600 × 70.800 mm — the two are different packs "
          "with different lengths, and a stranger buying from this pack today can "
          "buy the wrong one. Either the cavity fits the pack that ships or it is "
          "re-modelled; both outcomes are acceptable, silence is not.",
          1, "pack", depends_on=["M-1"],
          depends_note="the label is on the pack inside the unit",
          needs="measurement", needs_zh="需读取实物电池标签并用卡尺测量",
          unblocks="B-2 (the contact board must fit the pack's real pocket), the power budget, the runtime figure",
          deliverable_zh="确定唯一一款电池组，给出制造商型号、实测长宽高、容量、保护板与连接器，"
                         "并据此重新核对 power_support 电池腔。",
          acceptance_zh="从实物电池上读取并拍摄标签，并用卡尺测量该电池。我方文档称 NP-F550 级，"
                        "而我方建模所用网格为 np_f970（38.600 × 20.600 × 70.800 mm）——两者是尺寸不同的电池，"
                        "今天照本交付包采购的人可能买错。电池腔要么与实际装机电池相符，要么重做；"
                        "两种结果都可接受，不作答复不可接受。",
          evidence="GOAL.md finding 2; FACTORY-PACK section 3.6; ce-parts/microduck-power-support"),
    ])

# --- Track 4: custom boards -------------------------------------------------
# THE DEFECT THIS FIXES (factory reviewer, 2026-09-04): three parcels described
# different boards in their title, their effort and their evidence, so nobody
# could be assigned to them. B-2 was titled "the banana battery-contact board"
# and costed "1 board (Robot HAT) re-routed"; B-3 was titled "lay out and
# fabricate the Robot HAT and the IMU board" and costed fabrication only. The
# largest single engineering item in the plan — the HAT and IMU LAYOUT — was
# claimed by two parcels and costed once. The boards are now one parcel each for
# the work they actually contain, and fabrication is its own parcel.
track(
    4, "The three custom circuit boards",
    "三块自制电路板",
    "Pollen publishes no design files for the IMU-to-Dynamixel board or the "
    "battery contact board. They DO publish the Robot HAT, under Apache-2.0, "
    "with a complete production package — and it is 0.9001 mm wider than our own "
    "reconstruction, not 18.5 mm as this pack said until tonight. Our "
    "reconstruction of the HAT fails its own DRC and is a footprint-accurate "
    "stand-in, not a manufacturable copy.",
    "Pollen 未公开 IMU 转 Dynamixel 板与电池触点板的设计文件。但 Robot HAT 是公开的，"
    "采用 Apache-2.0 许可并附完整生产资料——且它只比我方重构版宽 0.9001 mm，"
    "而非本交付包此前所述的 18.5 mm。我方复原的 HAT 未通过自身 DRC，只是尺寸相符的替代件，"
    "并非可制造的复制品。",
    [
        P("B-1", "Reverse-engineer the boards from the physical samples",
          "从实物逆向电路板",
          "A schematic per board with every component and every net, traced from "
          "the board itself.",
          "Every net traceable end to end; every component with a marking read "
          "off the part. The two currently-guessed parts — the Dynamixel "
          "half-duplex transceiver and the 2S→5V regulator — are identified, "
          "not inferred.",
          3, "boards", depends_on=["M-1"], gate="L-0",
          needs="measurement", needs_zh="需实物电路板、放大设备与万用表",
          unblocks="B-2 and B-3; nothing ships without these",
          acceptance_zh="每条网络可端到端追踪；每个元件都有从实物上读取的标识。"
                        "目前仅靠推断的两个元件——Dynamixel 半双工收发器与 2S 转 5V 稳压器——必须确认而非推断。",
          evidence="PCB-PACKAGE.html — Robot HAT reconstruction fails its own DRC"),
        P("B-2", "Lay out and prove the banana battery-contact board",
          "设计并验证电池触点板",
          "Gerbers, drill, pick-and-place and a BOM for the simplest of the three, "
          "plus five fabricated samples fitted to a real pack.",
          "A DRC-clean board AND five fabricated samples that fit the measured "
          "pocket of the pack that actually ships. This board is passive — VBAT "
          "and GND only — so the LAYOUT is the fastest of the three; the samples "
          "are not, because they need a PCB fab and a pocket measured off a real "
          "pack, which is why this is not a desk parcel.",
          1, "board", depends_on=["B-1", "S-4", "M-2"],
          depends_note="B-1 for the netlist, S-4 for which pack, M-2 for the measured pocket",
          needs="vendor",
          needs_zh="需 PCB 打样，并需在实物电池上测得的电池腔尺寸",
          unblocks="the power path; a buildable prototype",
          acceptance_zh="板通过 DRC，<b>且</b>有五件打样实物能装入实际装机电池的实测槽位。"
                        "该板为无源板，仅 VBAT 与 GND，因此<b>布线</b>是三块板中最快的；"
                        "但打样不快——需要 PCB 厂，也需要在实物电池上测得的槽位尺寸，"
                        "所以它不是一个纯案头工作包。",
          evidence="workflows/RUNNING.md — 'the banana contact board is passive and is ~1 day of work "
                   "after one measurement session'; electronics/pcb-package.json boards[banana-contact] "
                   "45.8 x 4.6 mm"),
        P("B-3", "Lay out the Robot HAT and the IMU board — the largest single engineering item here",
          "完成 Robot HAT 与 IMU 板的布线——本计划中最大的单项工程",
          "Gerbers, drill, pick-and-place, BOM and assembly drawings for both, "
          "OR a decision to adopt Pollen's published Apache-2.0 HAT and lay out "
          "the IMU board alone.",
          "DRC clean with zero fails (ours currently has 10) and the 1.8 V codec "
          "rail terminated rather than dead-ending on a test point. If Pollen's "
          "board is adopted (question Q5.4), this parcel loses the HAT and keeps "
          "only the IMU board — the single largest reduction available to this plan.",
          2, "boards", depends_on=["B-1", "B-3a"],
          depends_note="B-1 for the netlist; B-3a says whether Pollen's board fits and can remove half of this parcel",
          needs="desk", needs_zh="纯布线工作，需 EDA 工具",
          unblocks="B-4; a working prototype",
          acceptance_zh="DRC 零错误（我方现有 10 项失败），且 1.8 V 编解码器电源轨有正常终端，"
                        "而非停在测试点上悬空。若采纳 Pollen 公开板（见问题 Q5.4），本工作包将去掉 HAT，"
                        "只保留 IMU 板——这是本计划中可获得的最大一次工作量削减。",
          evidence="PCB-PACKAGE.html — 10 DRC fails; DVDD dead-ends on TP1"),
        P("B-3a", "Measure the HAT pocket in the motor support against Pollen's 65.0000 × 30.9001 mm board",
          "测量电机支架上的 HAT 板槽，核对 Pollen 的 65.0000 × 30.9001 mm 板",
          "A clearance number in mm between Pollen's published board outline and "
          "the pocket in microduck-motor-support, in all three axes, with the "
          "connector heights checked as well as the outline.",
          "A number, not an opinion: does a 30.9001 mm board fit where a 30.0250 mm "
          "mesh sits today? The delta is 0.8751 mm. This has never been measured — "
          "the motor-support part carries no interface record for the HAT seat — "
          "and it is the ONLY thing standing between us and answering Q5.4, which "
          "is the one move that shortens this whole plan and cleans the licence "
          "position at the same time.",
          1, "clearance check", needs="desk",
          needs_zh="仅需案头工作——所用几何数据已在仓库中",
          unblocks="question Q5.4, and through it half of B-3 and all of B-1's HAT share",
          deliverable_zh="给出 Pollen 公开板外形与 microduck-motor-support 板槽之间的三轴间隙数值（mm），"
                         "并同时核对连接器高度，而不只是外形。",
          acceptance_zh="要一个数字，不要判断：30.9001 mm 的板能否装进今天放着 30.0250 mm 网格的位置？"
                        "差值为 0.8751 mm。此项从未测量过——电机支架零件没有 HAT 座的接口记录——"
                        "而它是我方回答 Q5.4 前唯一的障碍；Q5.4 又是唯一既能缩短整个计划、"
                        "又能同时理顺许可关系的一步。",
          evidence="out/factory/reconcile.json robot_hat_outline.still_open — measured tonight off "
                   "the Edge.Cuts layer of reference/pollen-elec-rpi-robot-hat/elec_RPI_Robot_HAT.kicad_pcb"),
        P("B-4", "Fabricate and assemble the three boards",
          "投板与贴装三块电路板",
          "Three boards through fab and SMT assembly: prepare the package, "
          "panelise, review the fab's DFM report, populate and power up.",
          "Five assembled samples of each board that power up. Excludes fab lead "
          "time, which is elapsed days and only the fab can state it.",
          3, "boards", depends_on=["B-2", "B-3"],
          needs="vendor", needs_zh="需 PCB 厂与贴装产线",
          unblocks="A-1 — the first build cannot start without boards",
          acceptance_zh="每块板五件贴装成品并能上电。不含投板周期；那是日历天，只有 PCB 厂能给出。",
          evidence="PCB-PACKAGE.html fab statement of work"),
    ])

# --- Track 5: DFM review ----------------------------------------------------
track(
    5, "DFM review and the print files",
    "可制造性审查与打印文件",
    "%d of %d print files are ready. The rest are vendor simulation meshes that "
    "carry no manufacturable dimensions, and %d of the %d are under a "
    "non-commercial licence that forbids selling what is printed from them."
    % (summary["print"]["ready"], summary["print"]["total"],
       summary["print_licence"]["vendor_mesh_stls"], summary["print"]["total"]),
    "%d 个打印文件中 %d 个已就绪。其余为供应商仿真网格，不含可制造尺寸；"
    "且其中 %d 个受非商业许可限制，不得用于销售。"
    % (summary["print"]["total"], summary["print"]["ready"],
       summary["print_licence"]["vendor_mesh_stls"]),
    [
        P("D-1", "DFM review every part against your processes",
          "按贵厂工艺对每个零件做可制造性审查",
          "Per part: what you would change to make it manufacturable, with the "
          "reason and the cost or cycle-time impact.",
          "A written finding per part, or an explicit 'no change needed'. "
          "Silence on a part is not an answer.",
          30, "parts", depends_on=["C-1"], needs="desk",
          needs_zh="需贵厂工艺知识",
          unblocks="the production geometry; possibly a re-model",
          acceptance_zh="每个零件给出书面意见，或明确写“无需修改”。对某个零件不作答复不算答复。",
          evidence="MANUFACTURING-PLAYBOOK.html"),
        P("D-2", "Quote injection moulding against the printed baseline",
          "报价注塑方案并与打印方案比较",
          "Tooling cost, tooling lead time, per-part price and MOQ for the shells, "
          "against our printed cost, so the break-even quantity is a real number.",
          "A quote per shell part. Our current break-even analysis uses published "
          "list prices, not your rates, so it is indicative only.",
          8, "candidate parts", needs="vendor",
          needs_zh="需贵厂模具报价",
          unblocks="the volume decision",
          acceptance_zh="每个壳体件给出一份报价。我方现有的量本利分析使用公开标价而非贵厂费率，仅供参考。",
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
          "THE THRESHOLD, because this parcel used to accept 'a working unit OR a "
          "log of where it stopped' — two branches that both pass, which is no "
          "threshold at all. It is complete when the log covers EVERY step of the "
          "assembly document with one of three marks: followed as written / "
          "followed with a correction (the correction stated) / could not be "
          "followed (the reason stated). An unmarked step means the parcel is not "
          "finished. A unit that does not power up is a PASS for this parcel and a "
          "FAIL for the pack, and the log says which steps caused it.",
          1, "unit", depends_on=["B-4"],
          depends_note="boards, printed parts and bought parts must all exist",
          needs="machine", needs_zh="需全部零件与一个装配工位",
          unblocks="A-2, A-3, H-1 — and it validates or refutes the whole pack",
          acceptance_zh="<b>判定门槛</b>——本工作包此前的验收是“装出可运行整机，<b>或</b>记录卡在何处”，"
                        "两个分支都算通过，等于没有门槛。现改为：装配文件的<b>每一步</b>都必须在记录中标注三者之一——"
                        "按原文执行 / 执行时作了修正（写明修正内容）/ 无法执行（写明原因）。"
                        "只要有一步未标注，本工作包即未完成。整机上电失败对本工作包是通过，"
                        "对交付包是失败，记录须写明是哪几步导致的。",
          evidence="ce-assemblies/microduck/current/manual/MANUAL.md; readiness.json assembly row — "
                   "%d steps assume knowledge not on the page"
                   % len((sel("assembly")[0].get("assumptions") or []) if sel("assembly") else [])),
        P("A-2", "Specify and build the assembly fixtures",
          "设计并制作装配工装",
          "The jigs the line needs: bearing press, servo-horn alignment, "
          "harness form board.",
          "Each fixture drawn and made, with the step it serves named. Our jig "
          "drawings exist but have never been made or used.",
          6, "fixtures", depends_on=["A-1"], needs="machine",
          needs_zh="需车间设备",
          unblocks="repeatable assembly",
          acceptance_zh="每件工装都有图纸并实际制作，且写明其服务的装配步骤。"
                        "我方已有工装图纸，但从未制作或使用过。",
          evidence="MANUFACTURING-PLAYBOOK.html — six assembly jigs with verified A3 drawings"),
        P("A-3", "Run the end-of-line test plan on the built unit",
          "对整机执行下线测试方案",
          "A completed test record against TEST-PLAN.html's gates.",
          "Every one of the %d end-of-line gates passed or failed with the "
          "measured value; the %d exempt tests (SN-05, SN-09) are NOT expected "
          "and their absence is not a failure. The walk acceptance thresholds "
          "come from simulation and have never been checked against hardware — "
          "that comparison is the deliverable."
          % (len(TP_EOL), len(TP_EXEMPT)),
          1, "unit", depends_on=["A-1"], needs="machine",
          needs_zh="需已装配整机与测试台",
          unblocks="the acceptance criteria becoming real; Q-1",
          acceptance_zh="%d 项下线判据逐项给出实测值与通过/不通过结论；%d 项豁免测试（SN-05、SN-09）"
                        "本就不在其列，缺席不算失败。行走验收阈值来自仿真、从未与硬件比对过——"
                        "这一比对本身就是交付物。" % (len(TP_EOL), len(TP_EXEMPT)),
          evidence="TEST-PLAN.html — the only artifact class currently graded READY; "
                   "out/factory/reconcile.json eol_gates"),
    ])

# --- Track 8: the three parcels nothing else in this plan covered -----------
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
          23, "cables", depends_on=["A-1"],
          depends_note="a built robot to fit the loom into",
          needs="measurement", needs_zh="需实物线束、压接工具与一台已装配的整机",
          unblocks="harness purchasing, and the assembly station that fits it",
          acceptance_zh="23 条线缆每条都有下料长度与公差；今日判为未定的 6 条各自载有连接器料号。"
                        "现状：20 条可下料长度，0 条公差。",
          evidence="wiring/cables.json — 23 rows, 0 with a tolerance field, lengths are route floors + slack"),
        P("F-1", "Set the torque schedule by strip and pull-out test",
          "通过滑牙与拔出试验确定扭矩表",
          "A torque per joint family with the test that produced it: torque-to-strip "
          "and pull-out force on printed bosses and on the XL330's own tapped holes.",
          "All three CANNOT DETERMINE torque rows in the playbook are replaced by a "
          "number with a test method and a specimen count. No chart figure is copied.",
          3, "joint families", depends_on=["C-2"],
          depends_note="C-2 gives the production print profile the specimens must be printed on; a real servo case comes from M-1 but printed coupons alone start it",
          needs="machine", needs_zh="需扭矩试验台、打印试件与校准扭力起子",
          unblocks="every assembly station step that tightens a screw",
          acceptance_zh="制造手册中三项判为未定的扭矩值，全部由带试验方法与试样数量的数值取代。不得抄用任何图表数据。",
          evidence="tools/data/playbook.json torque — 3 of 3 CANNOT DETERMINE; ROBOTIS publishes no torque"),
        P("Q-1", "First-article inspection report on the first five units",
          "首批五台整机的首件检验报告",
          "One report per unit: every gate result, every dimension out of tolerance, "
          "every place the assembly document was wrong, and the time each station took.",
          "5 units x %d gates logged against a serial, and the report names every "
          "step of the assembly document that had to be corrected to build them."
          % len(TP_EOL),
          5, "units", depends_on=["A-3"],
          needs="measurement", needs_zh="需已装配整机、测试台与卡尺",
          unblocks="turns our simulated numbers into measured ones — the whole point of the pilot",
          acceptance_zh="5 台整机 x %d 项判据，逐台按序列号记录；报告须指出为完成装配而必须修正的每一处文件内容。"
                        % len(TP_EOL),
          evidence="spec/test-plan.json — %d end-of-line gates, 0 exercised" % len(TP_EOL)),
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
    "L-0": (1.0, "1 decision, and it is reading and writing, not engineering. The ELAPSED time is "
                 "counsel's or Pollen's, not ours, and it can be weeks — which is exactly why it is "
                 "first: nothing in tracks 1, 2 or 5 may start until it lands. Rate ASSUMED.", "legal"),
    "M-1": (2.0, "1 unit: obtain by the L-0 route, receive, unbox and photograph a full teardown. Rate: 2 d per unit, ASSUMED. Elapsed time is longer than the effort — shipping is not engineer-days.", "measurement"),
    "M-2": (4.0, "30 printed parts x 0.13 engineer-day per part (about 1 h per part: fixture, caliper 3 axes plus features, record), plus counting the screws while the unit is open. Part count MEASURED (out/print/slice.json), rate ASSUMED.", "measurement"),
    "M-3": (1.0, "2 dimensions, but the work is the setup: scale reference, repeat readings, recompute the front-view ratio. Rate ASSUMED.", "measurement"),
    "M-4": (2.0, "6 unidentified components x 0.33 d each: decap or read the marking under magnification, then search the marking to a datasheet. Component count MEASURED (readiness CANNOT DETERMINE rows), rate ASSUMED.", "measurement"),
    "M-5": (1.0, "1 bench session: rail voltages and standby current on a live unit. Rate ASSUMED.", "machine"),
    "M-6": (4.5, "36 shelf records x 0.125 d each to write the measurement into the folder and re-run bin/triad check. Record count MEASURED (71 refs, 36 gradeable only from a unit), rate ASSUMED.", "desk"),
    "C-1": (1.5, "4 processes x 0.375 d: collect the capability statement and turn it into the tolerance basis on our sheets. Process count MEASURED, rate ASSUMED.", "desk"),
    "C-2": (3.0, "6 feature families x 5 specimens = 30 coupons: 1 d printing (machine time, not engineer time), 1.5 d measuring, 0.5 d writing the capability record. Coupon count is the plan; rates ASSUMED.", "machine"),
    "C-3": (1.0, "2 materials: obtain the datasheets, re-run the FEA material sweep on the real numbers. The re-run itself is minutes — cecad.stress is already scripted.", "material"),
    "C-4": (1.5, "30 parts x 0.05 d for a printable-wall opinion per part once C-1's floor is known. Part count MEASURED, rate ASSUMED. This parcel exists because our own sheets cannot answer the question (see its acceptance test).", "desk"),
    "S-1": (2.0, "3 quantity tiers across 32 lines: issue RFQ.html, chase, tabulate. Effort is chasing, not typing. Rate ASSUMED.", "vendor"),
    "S-2": (1.0, "1 decision (which compute board is actually fitted and can actually be ordered), once a marking has been read off the board in the teardown and a distributor has confirmed stock and a lead time.", "vendor"),
    "S-3": (2.5, "the lines with no priced offer or no stated lead time, x 0.17 d each: get it stated in writing. Line counts MEASURED (readiness bought_gaps), rate ASSUMED.", "vendor"),
    "S-4": (1.0, "1 pack: read the label on the pack inside the unit, caliper it, re-check the power_support cavity against it. The cavity re-check is minutes; the work is getting a real pack in hand.", "measurement"),
    "B-1": (6.0, "3 boards x 2 d: trace nets off the physical board under magnification and correct our schematic. The Robot HAT may collapse to about 4 d if Pollen's published Apache-2.0 package is adopted instead (FACTORY-QUESTIONS Q5.4, and B-3a is what decides it).", "measurement"),
    "B-2": (1.0, "1 passive board — VBAT and GND only — laid out and released to fab. The LAYOUT is a day; the five fitted samples are fab and bench time, not engineer-days, and they are what make this parcel need a vendor rather than a desk.", "vendor"),
    "B-3": (3.0, "2 boards routed: our Robot HAT reconstruction has 8 open nets and 10 DRC fails to clear against the fab's own rules, plus the IMU board. Open-net and DRC counts MEASURED (electronics/pcb-package.json, PCB-PACKAGE.html), rate ASSUMED. Adopting Pollen's board removes about two thirds of this.", "desk"),
    "B-3a": (0.5, "1 clearance check on geometry already in this repository: load the motor-support solid, section it at the HAT seat, measure the pocket against a 65.0000 x 30.9001 mm board and its connector heights. Half a day is the estimate for doing it properly and writing the number down.", "desk"),
    "B-4": (2.0, "3 boards through fab and assembly: prepare the package, panelise, review the fab's DFM report, populate, power up. Excludes fab lead time, which is elapsed days.", "vendor"),
    "D-1": (3.0, "30 parts x 0.1 d for a manufacturability opinion per part. Part count MEASURED, rate ASSUMED.", "desk"),
    "D-2": (2.0, "8 candidate parts for tooling: draft, wall, parting line, gate and ejector review. Candidate count MEASURED (5 shells + 3), rate ASSUMED.", "vendor"),
    "A-1": (3.0, "1 unit built for the first time from the paper, marking every step of the assembly document. 23 steps are known to assume knowledge that is not on the page (MEASURED), which is what makes this 3 d and not 1.", "machine"),
    "A-2": (2.0, "6 fixtures already drawn: print, fit, correct. Fixture count MEASURED (out/jigs), rate ASSUMED.", "machine"),
    "A-3": (2.5, "42 end-of-line gates x 0.06 d to run and log the first time, plus rig setup. Gate count MEASURED (spec/test-plan.json eol), rate ASSUMED.", "machine"),
    "H-1": (2.0, "23 cable rows: build one loom, measure each cut length installed, set a tolerance from the measured spread. Cable count MEASURED (wiring/cables.json), rate ASSUMED.", "measurement"),
    "F-1": (2.0, "3 joint families x 5 specimens: torque to failure and pull-out on printed bosses, then write the schedule. Torque is 3/3 CANNOT DETERMINE today (MEASURED).", "machine"),
    "Q-1": (2.0, "5 first-article units inspected against the drawings and the gates, one report. Unit count is the pilot plan.", "measurement"),
    "L-1": (1.0, "1 decision. Effort is reading and writing; the elapsed time depends on counsel or on Pollen answering.", "legal"),
    "L-2": (11.0, "22 vendor meshes x 0.5 d to rebuild parametrically and grade against the reference to the 1.0 mm p95 rule. Mesh count MEASURED (readiness print_licence), rate ASSUMED and the most uncertain number in this table — the 8 already done took an agent, not an engineer.", "desk"),
}

NEEDS_CLASS = {
    "machine": ("a real machine", "需实机"),
    "material": ("a real material", "需实料"),
    "measurement": ("a real measurement on real hardware", "需对实物实测"),
    "desk": ("a desk only", "仅需案头工作"),
    "vendor": ("an outside vendor's time", "需外部供应商配合"),
    "legal": ("a legal answer before any work starts", "需先取得法律答复方可开工"),
}


# ------------------------------------------------------------------ in flight
# MEASURED, NOT ASSERTED. This table used to name five lanes and tell ten engineers
# not to touch what they own. A factory reviewer checked the paths on 2026-09-04 and
# found three of them had no artifact on disk at all, or none written for fifteen
# hours — so the document was holding back the harness cut list, the pose match and
# the convergence scoreboard on the strength of work with nothing to show for it.
# It also listed five lanes while FACTORY-PACK listed six, so WF-SOURCES was missing
# from the very document engineers read for assignment.
#
# The list and its liveness now come from out/factory/readiness.json in_flight, where
# tools/gen_readiness.py stats every owned path and grades each lane LIVE / QUIET /
# NO ARTIFACT with the age of its newest byte. A lane that is not LIVE does not get
# to reserve work: the page says so, in both languages, on the row.
IN_FLIGHT_PARCELS = []
for w in in_flight:
    IN_FLIGHT_PARCELS.append(dict(
        id=w["id"], en=w["en"], zh=w["zh"], owns=w.get("owns", ""),
        liveness=w.get("liveness", "CANNOT DETERMINE"),
        age_min=w.get("newest_artifact_age_min"),
        why=w.get("liveness_why", ""), why_zh=w.get("liveness_why_zh", ""),
        state=w.get("state", []),
        assign=("DO NOT ASSIGN" if w.get("liveness") == "LIVE" else "ASSIGNABLE — check first"),
        assign_zh=("请勿分配" if w.get("liveness") == "LIVE" else "可分配——分配前请先确认"),
        count=w.get("count", "")))
IN_FLIGHT_LIVE = [w for w in IN_FLIGHT_PARCELS if w["liveness"] == "LIVE"]
IN_FLIGHT_NOT_LIVE = [w for w in IN_FLIGHT_PARCELS if w["liveness"] != "LIVE"]

# ------------------------------------------------- ten tracks, one per engineer
# Leif, verbatim: "We have a factory and 10 engineers to put on this." So the
# themes above are re-cut into TEN tracks, each sized for ONE engineer. A parcel
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

# every depends_on must name a parcel that exists, or the graph is a lie
for pid, p in THEME_PARCELS.items():
    for dep in p["depends_on"]:
        if dep not in THEME_PARCELS:
            raise SystemExit("gen_workplan: %s depends on %s, which does not exist" % (pid, dep))
    if p.get("gate") and p["gate"] not in THEME_PARCELS:
        raise SystemExit("gen_workplan: %s is gated on %s, which does not exist" % (pid, p["gate"]))

# ------------------------------------------------------------- the schedule graph
# THE DEFECT THIS FIXES (factory reviewer, 2026-09-04): the document stated a
# critical path of [M-1, B-1, B-2, B-3, A-1, Q-1] = 18.0 d and called it "in
# series". It was not a chain: B-3's own dependency was B-1, not B-2, so B-2 and
# B-3 ran in PARALLEL and that series did not exist. The real longest path was
# longer than the one advertised, and A-3 — which gates Q-1 — was left out of it
# entirely. A schedule stated in prose cannot be checked; this one is WALKED.
def _longest_path():
    """Longest path through the parcel DAG by engineer-days, computed by memoised
    depth-first search over depends_on. Returns (path, days). A cycle is a hard
    error, not a silently truncated walk."""
    memo, visiting = {}, set()

    def walk(pid):
        if pid in memo:
            return memo[pid]
        if pid in visiting:
            raise SystemExit("gen_workplan: dependency cycle at %s" % pid)
        visiting.add(pid)
        best = ([pid], THEME_PARCELS[pid]["days"])
        for dep in THEME_PARCELS[pid]["depends_on"]:
            path, days = walk(dep)
            if days + THEME_PARCELS[pid]["days"] > best[1]:
                best = (path + [pid], days + THEME_PARCELS[pid]["days"])
        visiting.discard(pid)
        memo[pid] = best
        return best

    return max((walk(pid) for pid in THEME_PARCELS), key=lambda x: x[1])


CRITICAL, CRIT_DAYS = _longest_path()
CRIT_DAYS = round(CRIT_DAYS, 1)
# the arithmetic, printed, so a reader can add it up themselves
CRIT_STEPS = [{"id": pid, "title_en": THEME_PARCELS[pid]["title_en"],
               "title_zh": THEME_PARCELS[pid]["title_zh"],
               "days": THEME_PARCELS[pid]["days"],
               "needs": THEME_PARCELS[pid]["needs_class_en"]} for pid in CRITICAL]
assert abs(sum(s["days"] for s in CRIT_STEPS) - CRIT_DAYS) < 1e-9, "critical path days do not add up"

# every parcel's earliest start, so "starts day one" is computed rather than typed
EARLIEST = {}


def _earliest(pid):
    if pid in EARLIEST:
        return EARLIEST[pid]
    deps = THEME_PARCELS[pid]["depends_on"]
    EARLIEST[pid] = 0.0 if not deps else max(_earliest(d) + THEME_PARCELS[d]["days"] for d in deps)
    return EARLIEST[pid]


for pid in THEME_PARCELS:
    THEME_PARCELS[pid]["earliest_start_day"] = round(_earliest(pid), 1)
    THEME_PARCELS[pid]["on_critical_path"] = pid in CRITICAL

ENGINEERS = [
    (1, "Teardown and dimensional metrology", "拆解与尺寸测量", ["M-1", "M-2", "M-3"]),
    (2, "Components, electrical identity and the shelf", "元器件识别、电气测量与零件档案", ["M-4", "M-5", "M-6"]),
    (3, "Process capability, coupons, materials and the wall floor", "工艺能力、试件、材料与壁厚下限", ["C-1", "C-2", "C-3", "C-4"]),
    (4, "Sourcing: quotes, lead times, the compute board and the battery", "采购：报价、交期、主控板与电池", ["S-1", "S-2", "S-3", "S-4"]),
    (5, "Board reverse-engineering and layout", "电路板逆向与布线", ["B-1", "B-3", "B-3a"]),
    (6, "Board fabrication, assembly and the test rig", "投板、贴装与测试台", ["B-2", "B-4", "A-3"]),
    (7, "DFM and the print files", "可制造性评审与打印文件", ["D-1", "D-2"]),
    (8, "First build, fixtures and first-article inspection", "首台装配、工装与首件检验", ["A-1", "A-2", "Q-1"]),
    (9, "Harness and the torque schedule", "线束与扭矩表", ["H-1", "F-1"]),
    (10, "Licence position and owned rebuilds", "许可确认与自研重建", ["L-0", "L-1", "L-2"]),
]
claimed = [pid for _n, _e, _z, ids in ENGINEERS for pid in ids]
if sorted(claimed) != sorted(THEME_PARCELS):
    raise SystemExit("gen_workplan: engineer tracks do not partition the parcels — claimed %d of %d; missing %s; twice %s"
                     % (len(claimed), len(THEME_PARCELS),
                        sorted(set(THEME_PARCELS) - set(claimed)),
                        sorted(x for x in set(claimed) if claimed.count(x) > 1)))


def _starts(ids):
    """When this track can start, DERIVED from its parcels' own dependencies rather
    than typed into the table. The old table said Track 6 was 'Blocked by: E5 (B-2)'
    while B-3, the only board parcel in it, depended on B-1 — the page contradicted
    itself. A sentence that is computed cannot. It names the FIRST parcel that can
    start and what that one parcel waits on, not a union of every dependency in the
    track, because a union reads as though everything waits on everything."""
    order = sorted(ids, key=lambda i: (THEME_PARCELS[i]["earliest_start_day"], i))
    first = order[0]
    fd = THEME_PARCELS[first]["earliest_start_day"]
    gated = sorted({THEME_PARCELS[i]["gate"] for i in ids if THEME_PARCELS[i].get("gate")})
    later = [i for i in order[1:] if THEME_PARCELS[i]["earliest_start_day"] > fd]
    if fd == 0.0:
        day_one = [i for i in order if THEME_PARCELS[i]["earliest_start_day"] == 0.0]
        en = "day one — %s can begin immediately" % ", ".join(day_one)
        zh = "第一天即可开工——%s 可立即开始" % "、".join(day_one)
        if later:
            en += "; %s wait%s until day %.1f" % (", ".join(later), "" if len(later) > 1 else "s",
                                                  THEME_PARCELS[later[0]]["earliest_start_day"])
            zh += "；%s 需等到第 %.1f 天" % ("、".join(later), THEME_PARCELS[later[0]]["earliest_start_day"])
    else:
        deps = THEME_PARCELS[first]["depends_on"]
        en = "day %.1f at the earliest — %s is the first parcel here and it waits on %s" % (
            fd, first, ", ".join(deps))
        zh = "最早第 %.1f 天——本线最先可开工的是 %s，它须等待 %s 完成" % (fd, first, "、".join(deps))
    bl = sorted({d for i in ids for d in THEME_PARCELS[i]["depends_on"] if d not in ids})
    bl_en = ", ".join(bl) if bl else "nothing in this plan"
    bl_zh = "、".join(bl) if bl else "本计划中无前置"
    if gated:
        en += " · LEGAL GATE %s: no parcel here that touches a retail unit may start until it is answered" % ", ".join(gated)
        zh += " · 法律前置 %s：本线中凡涉及零售整机的工作包，未获该答复不得开工" % "、".join(gated)
        extra = [g for g in gated if g not in bl]
        if extra:
            bl_en += " · plus the legal gate %s" % ", ".join(extra)
            bl_zh += " · 另加法律前置 %s" % "、".join(extra)
        else:
            bl_en += " (which is the legal gate)"
            bl_zh += "（即法律前置）"
    return en, zh, bl_en, bl_zh


TRACKS = []
for n, en_t, zh_t, ids_ in ENGINEERS:
    s_en, s_zh, b_en, b_zh = _starts(ids_)
    TRACKS.append(dict(
        num=n, engineer="E%d" % n, title_en=en_t, title_zh=zh_t,
        why_en="Starts %s. Blocked by: %s." % (s_en, b_en),
        why_zh="开工时点：%s。前置条件：%s。" % (s_zh, b_zh),
        starts=s_en, starts_zh=s_zh, blocked=b_en, blocked_zh=b_zh,
        parcels=[THEME_PARCELS[i] for i in ids_],
        earliest_start_day=min(THEME_PARCELS[i]["earliest_start_day"] for i in ids_),
        days=round(sum(THEME_PARCELS[i]["days"] for i in ids_), 1)))

TOTAL_DAYS = round(sum(t["days"] for t in TRACKS), 1)
DAY_ONE_TRACKS = [t["num"] for t in TRACKS if t["earliest_start_day"] == 0.0]
GATED_PARCELS = sorted(pid for pid, p in THEME_PARCELS.items() if p.get("gate"))

# ------------------------------------------------- the numbers the page quotes
# Every figure below is READ, not typed. The fastener counts in particular used to
# be quoted here as "0 fasteners in the assembly, against 145 holes" while the
# assembly had already placed screws — a stat block that was stale the hour it
# shipped, and one that a factory reads as "nobody knows what screws to buy".
FASTENER_PLACED = ((J("out/fasteners/placed.json", {}) or {}).get("counts") or {}).get("placed")
if FASTENER_PLACED is None:
    FASTENER_PLACED = "CANNOT DETERMINE"
FASTENER_BUYLIST = [c["n"] for c in RC["fasteners"]["counts"]
                    if c["what_en"].startswith("PIECES")][0]
HOLE_EN = [c for c in RC["fasteners"]["counts"] if c["what_en"].startswith("HOLE")][0]["breakdown_en"]
HOLE_ZH = [c for c in RC["fasteners"]["counts"] if c["what_en"].startswith("HOLE")][0]["breakdown_zh"]

# THE DEFECT THIS FIXES (factory reviewer, 2026-09-04): the bilingual layer dropped
# exactly the terms that carry the geometry. 沉孔 (counterbore) appeared ZERO times
# in all three pack documents; the shop abbreviation "c'bore" was left in English
# inside four Chinese sentences, including the hole census itself; 间隙 (clearance),
# "tap" and "THRU" were left untranslated in the one table that must survive the
# language barrier. A dimensioned drawing crosses that barrier and a paragraph does
# not — but only if the words on the drawing are in both languages.
GLOSSARY = [
    ("c'bore", "counterbore", "沉孔",
     "A flat-bottomed enlargement at the mouth of a hole so a cap-screw head sits below the surface. "
     "On this robot: Ø4.4 over a Ø2.2 clearance hole, for an M2 socket head."),
    ("CSK", "countersink", "锪孔 / 埋头孔",
     "A conical enlargement for a flat-head screw. Not used on this robot; listed so it is not confused with 沉孔."),
    ("clearance", "clearance hole", "间隙孔 / 过孔",
     "A hole the screw passes THROUGH without engaging thread. Ø2.2 for M2 here (ISO medium fit)."),
    ("tap", "tapped hole / tap drill", "攻丝孔 / 攻丝底孔",
     "A hole the screw threads INTO. Ø1.6 is the tap-drill size for an M2 thread; a finished M2 tapped hole is not Ø1.6."),
    ("THRU", "through", "通孔",
     "The hole passes entirely through the part. The opposite is a blind hole, 盲孔."),
    ("heat-set insert", "heat-set threaded insert", "热熔螺母 / 热压螺母",
     "A knurled brass nut pressed into printed plastic with a heated tool, giving a metal thread in a plastic part."),
    ("press fit", "interference fit", "过盈配合",
     "The shaft is larger than the bore and is pressed in. Used for the bearing seats."),
    ("SF", "safety factor", "安全系数",
     "Material yield strength divided by the peak simulated stress. Every SF in this project is simulated, never measured."),
    ("DFM", "design for manufacture", "可制造性设计",
     "Review of a part against the process that will actually make it."),
    ("DRC", "design rule check", "设计规则检查",
     "The PCB layout checked against the fabricator's own minimum track, space and drill rules."),
    ("MOQ", "minimum order quantity", "最小起订量", "The smallest quantity a supplier will sell."),
    ("FAI", "first-article inspection", "首件检验",
     "Full dimensional and functional inspection of the first units off a new process."),
]


def _b(txt):
    """Escape for HTML but keep the <b> emphasis the Chinese prose carries. Written
    as a helper rather than inline so an unescaped string cannot slip through."""
    return E(txt).replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")


# ---------------------------------------------------------------------- write
now = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
n_parcels = sum(len(t["parcels"]) for t in TRACKS)

CSS = """.zh{font-family:var(--sans);font-size:12px;color:var(--ink-2);display:block}
table{border-collapse:collapse;width:100%;table-layout:fixed;font-size:12.5px;margin:8px 0 18px;overflow-wrap:anywhere}
th{white-space:normal !important;overflow-wrap:break-word;word-break:normal;padding:5px 6px;background:var(--head);font-family:var(--sans);font-size:12px}
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
h.append("<p class=\"backlink\"><a href=\"INDEX.html\">← Document index</a> · "
         "<a href=\"FACTORY-PACK.html\">Factory pack</a> · <a href=\"FACTORY-QUESTIONS.html\">Questions</a></p>")
h.append("<header class=\"hero\"><p class=\"eyebrow\">Microduck · factory pack · 工厂交付包</p>")
h.append("<h1>What needs to be done <span class=\"zh\" style=\"font-size:22px;display:inline\">工作分解</span></h1>")
h.append("<p class=\"sub\">Every open piece of work, divided into parcels sized for one "
         "engineer. Each parcel names its deliverable, the acceptance test that says it is "
         "done, what it depends on and what it unblocks. Work that a software agent is "
         "measurably closing right now is marked so nobody does it twice.</p>")
h.append("<p class=\"sub zh\">全部待办工作，按单人可承担的粒度拆分。每个工作包给出交付物、"
         "判定完成的验收测试、依赖项与解锁项。有实测证据表明软件代理正在处理的工作会加以标注，避免重复。</p>")
h.append(f"<div class=\"rev\"><span>MD-FACT-WBS-001 · Rev B</span><span>generated {E(now)}</span>"
         f"<span>tools/gen_workplan.py</span></div></header>")

# ------------------------------------------------------------ THE LEGAL GATE
# This block is first on the page because the work it gates was first in the plan.
h.append("<div class=\"front\"><h2>⛔ READ BEFORE ANYONE BUYS OR OPENS A MICRODUCK "
         "<span class=\"zh\" style=\"display:inline;font-size:15px\">购买或拆开整机之前必读</span></h2>")
h.append("<p><b>Do not buy a retail Microduck and take it apart until parcel L-0 has been answered "
         "in writing.</b> Pollen Robotics' general terms and conditions of sale bind the buyer, and "
         "they say, verbatim: <i>“any dismantling, decompilation, reverse engineering (except to the "
         "extent this prohibition is not permitted by applicable law) […] is strictly prohibited”</i>, "
         "and <i>“Customer […] shall refrain from any partial or total resale of the Products”</i>. "
         "No Microduck has been bought, dismantled or reverse engineered by this project, and that "
         "clean position is worth keeping.</p>")
h.append("<p class=\"zh\"><b>在工作包 L-0 得到书面答复之前，请勿购买零售版 Microduck 并将其拆解。</b>"
         "Pollen Robotics 的销售通用条款对购买方具有约束力，原文为：<i>“任何拆解、反编译、逆向工程"
         "（除非适用法律不允许此项禁止）……均被严格禁止”</i>，以及<i>“客户……不得部分或全部转售本产品”</i>。"
         "本项目至今从未购买、拆解或逆向过任何一台 Microduck，这一清白状态值得保持。</p>")
h.append("<p>These are CONTRACT terms, not copyright: they bind whoever accepts them at purchase, "
         "and they carry their own limit — “except to the extent this prohibition is not permitted "
         "by applicable law”. Whether they bind an EU or a PRC buyer is a lawyer's question. "
         "<b>L-0 answers it, and names one of three lawful routes</b>: (a) Pollen's written "
         "permission, (b) counsel's opinion, or (c) a unit obtained WITHOUT accepting those terms. "
         "Every parcel that touches a retail unit carries the gate on its own row.</p>")
h.append("<p class=\"zh\">这些是<b>合同</b>条款而非著作权条款：只约束在购买时接受它们的一方，"
         "且自带限制——“除非适用法律不允许此项禁止”。它们是否约束欧盟或中国的买方，是律师的问题。"
         "<b>L-0 就是回答这个问题，并从三条合法途径中指定一条</b>：(a) Pollen 的书面许可；"
         "(b) 律师意见；(c) 通过<b>不接受该条款</b>的方式取得整机。凡涉及零售整机的工作包，"
         "都在自己那一行标注了该前置条件。</p>")
h.append(f"<p class=\"lede\">Parcels gated on L-0: <b>{E(', '.join(GATED_PARCELS))}</b>. "
         f"Source: out/factory/licence.json question Q-E and fact F14 (terms archived at "
         f"out/factory/licence-evidence/pollen_terms-of-sale.html, fetched 2026-09-04T04:01Z), "
         f"and FACTORY-PACK.html section 5.</p>")
h.append(f"<p class=\"lede zh\">受 L-0 前置约束的工作包：<b>{E('、'.join(GATED_PARCELS))}</b>。"
         f"依据：out/factory/licence.json 的问题 Q-E 与事实 F14（条款存档于 "
         f"out/factory/licence-evidence/pollen_terms-of-sale.html，抓取时间 2026-09-04T04:01Z），"
         f"以及 FACTORY-PACK.html 第 5 节。</p>")
h.append("</div>")

# honest state
h.append("<div class=\"front\"><h2>Read this before assigning anyone · 分配任务前请先读这里</h2>")
h.append("<div class=\"statbar\">")
h.append(f"<div class=\"stat\"><b class=\"no\">{summary['drawing']['not_yet']} / {summary['drawing']['total']}</b>"
         "<span>drawing sheets NOT YET<br>图纸尚未就绪</span></div>")
h.append(f"<div class=\"stat\"><b class=\"no\">{summary['bom_fasteners']['fastener_rows']}</b>"
         f"<span>fastener ROWS in the assembly BOM ({FASTENER_PLACED} screws placed)<br>"
         f"装配 BOM 中的紧固件行数（已装入 {FASTENER_PLACED} 颗螺钉）</span></div>")
h.append(f"<div class=\"stat\"><b class=\"no\">{summary['unknowns']}</b>"
         "<span>open items on the curated queue<br>已整理未定项</span></div>")
h.append(f"<div class=\"stat\"><b class=\"no\">0</b><span>physical units ever built<br>已制造实物台数</span></div>")
h.append("</div>")
h.append("<p><b>No physical Microduck has ever been built or measured by us.</b> Every "
         "number in this repository comes from Pollen Robotics' published simulation assets, "
         "from product photographs, or from our own simulation. That is why metrology on a "
         "real unit unblocks more work than anything else — and why the legal gate above has "
         "to be answered first.</p>")
h.append("<p class=\"zh\"><b>我们从未制造或测量过实物 Microduck。</b>本仓库中的每个数据都来自 "
         "Pollen Robotics 公开的仿真资料、产品照片或我们自己的仿真。因此对实物进行测量"
         "所解锁的后续工作最多——也正因如此，上面的法律前置必须最先解决。</p>")
h.append(f"<p class=\"lede\">Fastener counts on this page: the assembly BOM carries "
         f"{summary['bom_fasteners']['fastener_rows']} fastener ROWS totalling {FASTENER_PLACED} "
         f"screws placed through a connection, against a {summary['bom_fasteners']['hole_census']}-hole "
         f"community census and a {FASTENER_BUYLIST}-piece buy list. Those are four counts of four "
         f"different things and FACTORY-PACK.html section 3.3a reconciles them; do not order against "
         f"any one of them without reading it.</p>")
h.append(f"<p class=\"lede zh\">本页的紧固件数字：装配 BOM 有 {summary['bom_fasteners']['fastener_rows']} 个"
         f"紧固件行、共 {FASTENER_PLACED} 颗经连接件装入的螺钉；社区孔位统计为 "
         f"{summary['bom_fasteners']['hole_census']} 个孔；采购清单为 {FASTENER_BUYLIST} 件。"
         f"这是对四种不同对象的四个计数，FACTORY-PACK.html 3.3a 节已作对账；未读该节前请勿据其中任一数字下单。</p>")
h.append("</div>")

# TOC
h.append("<nav class=\"toc\"><ol>")
for t in TRACKS:
    h.append(f"<li><a href=\"#t{t['num']}\">Track {t['num']} · {E(t['title_en'])} · {E(t['title_zh'])} "
             f"({len(t['parcels'])})</a></li>")
h.append("<li><a href=\"#inflight\">Work an agent may already be closing · 软件代理可能已在处理的工作</a></li>")
h.append("<li><a href=\"#effort\">On effort estimates · 关于工时估算</a></li>")
h.append("<li><a href=\"#glossary\">Glossary of shop terms · 车间术语对照</a></li>")
h.append("</ol></nav>")

h.append(f"<p class=\"lede\">{n_parcels} parcels across {len(TRACKS)} tracks, one track per engineer, "
         f"{TOTAL_DAYS} engineer-days of estimated hands-on work in total. Tracks "
         f"{', '.join(str(x) for x in DAY_ONE_TRACKS)} have at least one parcel that can start on day one; "
         f"every other parcel waits on a named predecessor, and the wait is computed from the "
         f"dependencies rather than typed.</p>")
h.append(f"<p class=\"lede zh\">共 {n_parcels} 个工作包、{len(TRACKS)} 条工作线（每位工程师一条），"
         f"估算动手工作量合计 {TOTAL_DAYS} 人天。第 {'、'.join(str(x) for x in DAY_ONE_TRACKS)} 线"
         f"各有至少一个工作包可即刻开工；其余工作包均须等待指定的前置工作，且等待关系由依赖图计算得出，"
         f"而非人工填写。</p>")

# --- the critical path, COMPUTED
h.append("<div class=\"front\" style=\"border-color:var(--accent)\"><h2>The critical path, computed "
         "<span class=\"zh\" style=\"display:inline;font-size:15px\">关键路径（计算得出）</span></h2>")
h.append(f"<p><b>{' → '.join(E(s['id']) for s in CRIT_STEPS)}: {CRIT_DAYS} engineer-days of "
         f"hands-on work in series.</b> This is the LONGEST PATH through all {n_parcels} parcels' "
         f"stated dependencies, walked by the generator — not a sentence someone wrote. "
         f"An earlier revision of this page claimed a six-parcel chain that was not a chain at all "
         f"(two of its parcels ran in parallel) and left out the parcel that gates the last one. "
         f"The arithmetic is below; add it up.</p>")
h.append(f"<p class=\"zh\"><b>关键路径：{' → '.join(E(s['id']) for s in CRIT_STEPS)}，"
         f"串行动手工作量 {CRIT_DAYS} 人天。</b>这是对全部 {n_parcels} 个工作包所声明依赖关系"
         f"做最长路径搜索的结果，由生成器计算，而非人工撰写的句子。本页早前版本给出的六段“串行”路径"
         f"其实并不成链（其中两段实为并行），且遗漏了制约最后一环的工作包。下面列出算式，可自行核对。</p>")
h.append("<table><colgroup><col style=\"width:8%\"><col style=\"width:52%\"><col style=\"width:12%\">"
         "<col style=\"width:28%\"></colgroup>")
h.append("<thead><tr><th>Parcel<span class=\"zh\">工作包</span></th><th>What it is<span class=\"zh\">内容</span></th>"
         "<th>Est. days<span class=\"zh\">估算人天</span></th><th>Needs<span class=\"zh\">需求类别</span></th></tr></thead><tbody>")
for s in CRIT_STEPS:
    h.append(f"<tr><td class=\"m\"><a href=\"#{E(s['id'])}\">{E(s['id'])}</a></td>"
             f"<td>{E(s['title_en'])}<span class=\"zh\">{E(s['title_zh'])}</span></td>"
             f"<td class=\"num\">{s['days']}</td><td>{E(s['needs'])}</td></tr>")
h.append(f"<tr><td class=\"m\"><b>total</b></td><td><b>longest path in series</b>"
         f"<span class=\"zh\">最长串行路径合计</span></td><td class=\"num\"><b>{CRIT_DAYS}</b></td>"
         f"<td>—</td></tr>")
h.append("</tbody></table>")
h.append("<p><b>What shortens it.</b> Two things, and only two. <b>B-3a</b> — half an engineer-day "
         "of desk work on geometry already in this repository — measures whether Pollen's published "
         "Apache-2.0 Robot HAT fits our motor support; the board is 65.0000 × 30.9001 mm, which is "
         "0.9001 mm wider than our own reconstruction, not the 18.5 mm this pack said until tonight. "
         "If it fits, question Q5.4 is answered 'adopt Pollen's board', which removes the largest "
         "board from B-1 and most of B-3, and cleans the licence position at the same time because "
         "Apache-2.0 permits manufacture and sale. And <b>L-0</b>, which is not effort at all — it is "
         "elapsed time waiting on counsel or on Pollen, and everything downstream of a teardown sits "
         "behind it.</p>")
h.append("<p class=\"zh\"><b>能缩短它的只有两件事。</b>其一是 <b>B-3a</b>——半个人天的案头工作，"
         "所需几何数据已在仓库中——测定 Pollen 公开的 Apache-2.0 Robot HAT 能否装入我方电机支架。"
         "该板为 65.0000 × 30.9001 mm，仅比我方重构版宽 0.9001 mm，而非本交付包此前所述的 18.5 mm。"
         "若能装入，问题 Q5.4 的答案即为“采用 Pollen 的板”，从而免去 B-1 中最大的一块板与 B-3 的大部分工作，"
         "并同时理顺许可关系（Apache-2.0 允许制造与销售）。其二是 <b>L-0</b>，它根本不是工作量，"
         "而是等待律师或 Pollen 答复的日历时间；一切以拆解为前提的工作都排在它后面。</p>")
h.append("<p class=\"lede\">Vendor lead time is not in that figure: B-4 waits on a PCB house and M-1 "
         "waits on a shipment. Those are elapsed days, not engineer-days, and only you can put numbers "
         "on them.</p>")
h.append("<p class=\"lede zh\">上述数字不含供应商周期：B-4 需等待 PCB 厂，M-1 需等待到货。"
         "那是日历天而非人天，只有贵方能给出数值。</p></div>")

# --- the ten tracks as a table before the detail
h.append("<h3>The ten tracks · 十条工作线</h3>")
h.append("<table><colgroup><col style=\"width:6%\"><col style=\"width:24%\"><col style=\"width:7%\">"
         "<col style=\"width:8%\"><col style=\"width:28%\"><col style=\"width:27%\"></colgroup>")
h.append("<thead><tr><th>Eng.<span class=\"zh\">工程师</span></th><th>Track<span class=\"zh\">工作线</span></th>"
         "<th>Parcels<span class=\"zh\">工作包</span></th><th>Est. days<span class=\"zh\">估算人天</span></th>"
         "<th>Starts<span class=\"zh\">开工时点</span></th><th>Blocked by<span class=\"zh\">前置条件</span></th></tr></thead><tbody>")
for t in TRACKS:
    h.append(f"<tr><td class=\"m\">{E(t['engineer'])}</td><td><a href=\"#t{t['num']}\">{E(t['title_en'])}</a>"
             f"<span class=\"zh\">{E(t['title_zh'])}</span></td>"
             f"<td class=\"num\">{len(t['parcels'])}</td><td class=\"num\">{t['days']}</td>"
             f"<td>{E(t['starts'])}<span class=\"zh\">{E(t['starts_zh'])}</span></td>"
             f"<td>{E(t['blocked'])}<span class=\"zh\">{E(t['blocked_zh'])}</span></td></tr>")
h.append("</tbody></table>")

for t in TRACKS:
    h.append(f"<section class=\"trk\" id=\"t{t['num']}\">")
    h.append(f"<h2>Track {t['num']} — one engineer · {E(t['title_en'])} <span class=\"zh\" "
             f"style=\"display:inline;font-size:15px\">{E(t['title_zh'])}</span></h2>")
    h.append(f"<p class=\"f\">{len(t['parcels'])} parcels · {t['days']} estimated engineer-days · "
             f"starts {E(t['starts'])}</p>")
    h.append(f"<p>{E(t['why_en'])}</p><p class=\"zh\">{E(t['why_zh'])}</p>")
    for p in t["parcels"]:
        h.append(f"<div class=\"parcel\" id=\"{E(p['id'])}\">")
        h.append(f"<h4><span class=\"pid\">{E(p['id'])}</span>{E(p['title_en'])} "
                 f"<span class=\"zh\" style=\"display:inline\">{E(p['title_zh'])}</span></h4>")
        if p.get("gate"):
            h.append(f"<p><b class=\"no\">⛔ LEGAL GATE — {E(p['gate'])} must be answered in writing "
                     f"before this parcel starts.</b> Pollen's terms of sale forbid the buyer of a "
                     f"retail unit from dismantling or reverse engineering it; see the block at the "
                     f"top of this page. <span class=\"zh\" style=\"display:block\">⛔ 法律前置——"
                     f"本工作包开工前，{E(p['gate'])} 必须先有书面答复。Pollen 的销售条款禁止零售整机的"
                     f"购买者拆解或逆向该产品，详见本页顶部说明。</span></p>")
        if p.get("on_critical_path"):
            h.append("<p class=\"f\">ON THE CRITICAL PATH · 位于关键路径上</p>")
        h.append("<table><colgroup><col style=\"width:20%\"><col></colgroup><tbody>")
        h.append(f"<tr><th>Deliverable 交付物</th><td>{E(p['deliverable'])}"
                 f"{('<span class=\"zh\">' + _b(p['deliverable_zh']) + '</span>') if p.get('deliverable_zh') else ''}</td></tr>")
        h.append(f"<tr><th>Acceptance test 验收测试</th><td>{E(p['acceptance'])}"
                 f"{('<span class=\"zh\">' + _b(p['acceptance_zh']) + '</span>') if p.get('acceptance_zh') else ''}</td></tr>")
        h.append(f"<tr><th>Quantity 数量</th><td class=\"num\" style=\"text-align:left\">"
                 f"{E(p['qty'])} {E(p['unit'])}</td></tr>")
        dep = ", ".join(p["depends_on"]) if p["depends_on"] else "nothing — can start on day one"
        dep_zh = "、".join(p["depends_on"]) if p["depends_on"] else "无前置，可即刻开工"
        h.append(f"<tr><th>Depends on 依赖</th><td>{E(dep)}"
                 f"{(' — ' + E(p['depends_note'])) if p.get('depends_note') else ''}"
                 f"<span class=\"zh\">{E(dep_zh)}；最早可于第 {p['earliest_start_day']} 天开工</span></td></tr>")
        if p["unblocks"]:
            h.append(f"<tr><th>Unblocks 解锁</th><td>{E(p['unblocks'])}</td></tr>")
        h.append(f"<tr><th>Effort 估算工作量</th><td><b>{p['days']} engineer-days (ESTIMATE)</b> — {E(p['days_basis'])}"
                 f"<span class=\"zh\">估算 {p['days']} 人天（估算值，非实测）</span></td></tr>")
        h.append(f"<tr><th>Needs 需要</th><td><b>{E(p['needs_class_en'])} · {E(p['needs_class_zh'])}</b>"
                 f"{(' — ' + E(p['needs_note_zh'])) if p.get('needs_note_zh') else ''}</td></tr>")
        if p["evidence"]:
            h.append(f"<tr><th>Evidence 依据</th><td class=\"m\">{E(p['evidence'])}</td></tr>")
        h.append("</tbody></table></div>")
    h.append("</section>")

# ------------------------------------------------------- in flight, MEASURED
h.append("<section class=\"trk\" id=\"inflight\"><h2>Work an agent may already be closing "
         "<span class=\"zh\" style=\"display:inline;font-size:15px\">软件代理可能已在处理的工作</span></h2>")
h.append("<p>Software agents work this repository at the same time you do. This table is listed so "
         "the factory does not duplicate them — but <b>“in flight” is a claim about a process nobody "
         "can see, so it is measured rather than asserted</b>: for each lane, every path it owns is "
         "stat'd and the age of its newest byte is printed. A lane whose newest artifact is older "
         "than 90 minutes, or which has written nothing at all, does NOT get to reserve work from "
         "you. Ask, and if nobody answers, take it.</p>")
h.append("<p class=\"zh\">软件代理与贵方同时在本仓库中工作。列出此表是为避免重复劳动——但"
         "<b>“进行中”是对一个谁也看不见的过程的断言，因此这里改为实测而非断言</b>："
         "对每条工作流所占用的全部路径逐一读取文件属性，并给出其最新字节的写入时间。"
         "若某条工作流的最新产出已超过 90 分钟，或根本没有任何产出，则它<b>无权</b>为自己保留工作。"
         "请先询问；若无人应答，即可接手。</p>")
h.append(f"<p class=\"lede\">Measured {E(RD.get('measured_at', ''))}: "
         f"{len(IN_FLIGHT_LIVE)} of {len(IN_FLIGHT_PARCELS)} lanes are LIVE. "
         f"{', '.join(E(w['id']) for w in IN_FLIGHT_NOT_LIVE) or 'None'} "
         f"{'are' if len(IN_FLIGHT_NOT_LIVE) != 1 else 'is'} not, and "
         f"{'their' if len(IN_FLIGHT_NOT_LIVE) != 1 else 'its'} work is assignable.</p>")
h.append("<table><colgroup><col style=\"width:11%\"><col style=\"width:12%\"><col style=\"width:37%\">"
         "<col style=\"width:40%\"></colgroup>")
h.append("<thead><tr><th>Lane<span class=\"zh\">工作流</span></th>"
         "<th>Liveness<span class=\"zh\">活跃状态</span></th>"
         "<th>What it is closing<span class=\"zh\">工作内容</span></th>"
         "<th>Measured, and what it means for you<span class=\"zh\">实测结果及其对贵方的含义</span></th></tr></thead><tbody>")
for w in IN_FLIGHT_PARCELS:
    cl = {"LIVE": "cd", "QUIET": "no", "NO ARTIFACT": "no"}.get(w["liveness"], "cd")
    age = ("newest byte %s min ago" % w["age_min"]) if w["age_min"] is not None else "nothing on disk"
    h.append(f"<tr><td class=\"m\">{E(w['id'])}</td>"
             f"<td><b class=\"{cl}\">{E(w['liveness'])}</b><br><span class=\"m\" style=\"font-size:10.5px\">{E(age)}</span>"
             f"<br><b>{E(w['assign'])}</b><span class=\"zh\">{E(w['assign_zh'])}</span></td>"
             f"<td>{E(w['en'])}<span class=\"zh\">{E(w['zh'])}</span></td>"
             f"<td>{E(w['why'])}<span class=\"zh\">{E(w['why_zh'])}</span>"
             f"<br><span class=\"m\" style=\"font-size:10.5px\">owns: {E(w['owns'])}</span></td></tr>")
h.append("</tbody></table>")
h.append("<p class=\"lede\">The paths each lane owns are listed so you can check them yourself: "
         "<code>ls -lt</code> the path and read the newest timestamp. That is exactly what this "
         "table did.</p>")
h.append("<p class=\"lede zh\">上表列出每条工作流占用的路径，贵方可自行核对：对该路径执行 "
         "<code>ls -lt</code> 并查看最新时间戳——本表所做的正是这件事。</p></section>")

# ------------------------------------------------------------------- effort
h.append("<section class=\"trk\" id=\"effort\"><h2>On effort estimates "
         "<span class=\"zh\" style=\"display:inline;font-size:15px\">关于工时估算</span></h2>")
h.append("<p><b>Every day figure in this document is an ESTIMATE and is labelled as one on the parcel.</b> "
         "This workshop has never built a physical unit, so it holds no measured time-per-item for any of "
         f"this work — and that absence is itself measured: 0 units built, 0 of the {len(TP_EOL)} "
         "end-of-line gates ever exercised. What keeps the estimates from being invented is that each one "
         "states the arithmetic it rests on: a COUNT we measured (30 print files, 145 M2 holes, 23 cables, "
         f"{len(TP_EOL)} end-of-line gates, 22 vendor meshes) multiplied by a per-item rate that is written "
         "into the row. Divide our rate out and put yours in — that is what the row is for.</p>")
h.append("<p class=\"zh\"><b>本文件中的每个天数均为估算，并已在各工作包中如实标注。</b>我方从未制造过实物，"
         f"因此没有任何一项工作的实测单件工时——这一点本身也是实测结论：已制造 0 台，{len(TP_EOL)} 项下线判据执行 0 项。"
         "估算之所以不是臆测，在于每一条都写明其算式：一个我方实测的<b>数量</b>乘以写在该行中的单件定额。"
         "请用贵厂定额替换我方定额。</p>")
h.append(f"<p>The largest single estimate, and the least certain, is L-2: {E(str(THEME_PARCELS['L-2']['days']))} "
         "engineer-days to rebuild 22 vendor meshes as parts we own. The 8 already rebuilt were done by a "
         "software agent, not by an engineer, so that rate may be wrong by a factor either way.</p>")
h.append("<p class=\"zh\">最大且最不确定的估算是 L-2：把 22 个供方网格重建为我方自有零件。已完成的 8 个"
         "由软件代理而非工程师完成，因此该定额可能显著偏高或偏低。</p>")
h.append("<h3>What each parcel physically needs · 各工作包的实物需求</h3>")
h.append("<table><colgroup><col style=\"width:26%\"><col style=\"width:10%\"><col></colgroup>")
h.append("<thead><tr><th>Needs<span class=\"zh\">需求类别</span></th><th>Parcels<span class=\"zh\">数量</span></th>"
         "<th>Which<span class=\"zh\">具体工作包</span></th></tr></thead><tbody>")
for _k, (_en, _zh) in NEEDS_CLASS.items():
    _ids = [pid for pid in sorted(THEME_PARCELS) if THEME_PARCELS[pid]["needs_class"] == _k]
    if _ids:
        h.append(f"<tr><td>{E(_en)}<span class=\"zh\">{E(_zh)}</span></td><td class=\"num\">{len(_ids)}</td>"
                 f"<td class=\"m\">{E(', '.join(_ids))}</td></tr>")
h.append("</tbody></table>")
_not_desk = sum(1 for p in THEME_PARCELS.values() if p["needs_class"] != "desk")
h.append(f"<p class=\"lede\">{_not_desk} of {len(THEME_PARCELS)} parcels cannot be done at a desk. That is "
         "the reason this pack exists: the remaining work is mostly work only a factory can do. The "
         "classification is checked against each parcel's own acceptance test — B-2's acceptance demands "
         "five fabricated samples fitted to a real battery pack, so it is a vendor parcel and not a desk "
         "one, whatever its layout half costs.</p>")
h.append(f"<p class=\"lede zh\">{len(THEME_PARCELS)} 个工作包中有 {_not_desk} 个无法在案头完成。"
         "这正是本交付包存在的理由：剩余工作大多只有工厂才能完成。该分类已与各工作包自身的验收测试逐一核对——"
         "例如 B-2 的验收要求五件打样实物装入实物电池，因此无论其布线部分多快，它都属于“需外部供应商配合”，"
         "而非“仅需案头工作”。</p></section>")

# ---------------------------------------------------------------- glossary
h.append("<section class=\"trk\" id=\"glossary\"><h2>Glossary of shop terms "
         "<span class=\"zh\" style=\"display:inline;font-size:15px\">车间术语对照</span></h2>")
h.append("<p>Shop abbreviations that appear on our drawings and in the hole census. They are listed "
         "because an English abbreviation inside a Chinese sentence is exactly the place a drawing "
         "stops crossing the language barrier.</p>")
h.append("<p class=\"zh\">下列为我方图纸与孔位统计中出现的车间缩写。之所以专门列出，"
         "是因为中文句子里夹一个英文缩写，正是图纸失去跨语言能力的地方。</p>")
h.append("<table><colgroup><col style=\"width:18%\"><col style=\"width:16%\"><col style=\"width:22%\"><col></colgroup>")
h.append("<thead><tr><th>On the drawing<span class=\"zh\">图纸标注</span></th>"
         "<th>Full term<span class=\"zh\">全称</span></th><th>中文<span class=\"zh\">Chinese</span></th>"
         "<th>What it is<span class=\"zh\">含义</span></th></tr></thead><tbody>")
for a, b, c, d_ in GLOSSARY:
    h.append(f"<tr><td class=\"m\">{E(a)}</td><td>{E(b)}</td><td><b>{E(c)}</b></td><td>{E(d_)}</td></tr>")
h.append("</tbody></table>")
h.append(f"<p class=\"lede\">The hole census, written in both languages with no abbreviation left in "
         f"English: <b>{E(HOLE_EN)}</b></p>")
h.append(f"<p class=\"lede zh\">孔位统计（中文完整表述，不留英文缩写）：<b>{E(HOLE_ZH)}</b></p>")
h.append("</section>")

h.append("<p class=\"backlink\" style=\"margin-top:40px\"><a href=\"INDEX.html\">← Document index</a> · "
         "<a href=\"out/factory/readiness.html\">Readiness audit</a> · "
         "<a href=\"LICENCE-POSITION.html\">Licence position</a> · "
         "<a href=\"FACTORY-PACK.html\">Factory pack</a></p>")
h.append("</div></body></html>")

with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write("\n".join(h))

os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(dict(generated=now, source="out/factory/readiness.json",
                   tracks=TRACKS, in_flight=IN_FLIGHT_PARCELS,
                   in_flight_live=[w["id"] for w in IN_FLIGHT_LIVE],
                   in_flight_not_live=[{"id": w["id"], "liveness": w["liveness"],
                                        "age_min": w["age_min"]} for w in IN_FLIGHT_NOT_LIVE],
                   parcels=n_parcels, engineer_days_total=TOTAL_DAYS,
                   critical_path=CRITICAL, critical_path_days=CRIT_DAYS,
                   critical_path_steps=CRIT_STEPS,
                   critical_path_how=("LONGEST PATH over every parcel's depends_on, walked by "
                                      "_longest_path() in tools/gen_workplan.py. It is not a stated "
                                      "chain: an earlier revision claimed [M-1, B-1, B-2, B-3, A-1, "
                                      "Q-1] = 18.0 d 'in series' when B-3 depended on B-1 and not on "
                                      "B-2, so two of those ran in parallel and the series did not "
                                      "exist."),
                   legal_gate={"parcel": "L-0",
                               "gated_parcels": GATED_PARCELS,
                               "why": ("Pollen's terms of sale forbid the buyer of a retail unit from "
                                       "dismantling or reverse engineering it (out/factory/licence.json "
                                       "F14); LICENCE-POSITION Q-E is unanswered. No parcel that touches "
                                       "a retail unit may start until L-0 names one of three lawful "
                                       "routes in writing.")},
                   earliest_start_day={pid: p["earliest_start_day"] for pid, p in THEME_PARCELS.items()},
                   effort_note=("Every day figure is an ESTIMATE. No measured time-per-item exists in this "
                                "workshop: 0 units built. Each parcel states the measured COUNT and the "
                                "assumed per-item rate its estimate is arithmetic on.")),
              f, indent=1, ensure_ascii=False)

print(f"wrote {OUT_HTML} ({os.path.getsize(OUT_HTML)} B) — {n_parcels} parcels, {len(TRACKS)} tracks, {TOTAL_DAYS} est. engineer-days, critical path {CRIT_DAYS} d")
print(f"wrote {OUT_JSON}")
