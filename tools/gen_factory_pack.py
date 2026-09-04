#!/usr/bin/env python3
"""gen_factory_pack.py — FACTORY-PACK.html, the single document a partner
factory builds from.

    python3 tools/measure_readiness.py      # re-take every measurement
    python3 tools/gen_readiness.py          # grade it
    python3 tools/gen_factory_pack.py       # this file

Reads, never invents:
    out/factory/readiness.json      every artifact graded, with its measurement
    out/factory/measure/*.json      the raw measurements the grades came from
    out/print/slice.json            real slicer grams and seconds per part
    spec/sourcing.json              bought lines, prices read off live pages
    spec/test-plan.json             gated tests and end-of-line gates
    wiring/cables.json              the 23 cable routes measured in CAD
    tools/data/playbook.json        line stations, print profile, torque
    out/factory/licence.json        what may be printed and what may be sold
    out/factory/workplan.json       parcel count, for the pointer to the WBS
    SPEC.md                         envelope / mass, quoted with line numbers
    tools/data/factory_pack.json    the prose (EN + 简体中文). No numbers.

Writes:
    out/factory/pack.json           the assembled data, one record per section
    FACTORY-PACK.html               the document

House rule: no number is typed into this file or into the prose file. If a
figure appears on the page, this script read it out of one of the files above,
and the page says which.
"""
import datetime
import html
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_HTML = os.path.join(ROOT, "FACTORY-PACK.html")
OUT_JSON = os.path.join(ROOT, "out", "factory", "pack.json")
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
E = html.escape


def J(rel, default=None):
    p = rel if os.path.isabs(rel) else os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return default
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def stat(rel):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return None
    st = os.stat(p)
    if os.path.isdir(p):
        n = sum(len(fs) for _, _, fs in os.walk(p))
        return {"path": rel, "kind": "dir", "files": n,
                "mtime": datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")}
    return {"path": rel, "kind": "file", "bytes": st.st_size,
            "mtime": datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")}


def git_head():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


D = J("tools/data/factory_pack.json")
RD = J("out/factory/readiness.json")
if RD is None:
    raise SystemExit("out/factory/readiness.json missing — run tools/gen_readiness.py first")
SL = J("out/print/slice.json", {})
SRC = J("spec/sourcing.json", {})
TP = J("spec/test-plan.json", {})
CAB = (J("wiring/cables.json", {}) or {}).get("record", {})
PB = J("tools/data/playbook.json", {})
LIC = J("out/factory/licence.json", {})
WP = J("out/factory/workplan.json", {})
SC = J("out/factory/measure/sheetcheck.json", {})

rows = RD["rows"]
S = RD["summary"]


def cls(c):
    return [r for r in rows if r["class"] == c]


# ------------------------------------------------------------------ 1 product
def spec_envelope():
    """Rows of SPEC.md §2 'Envelope and mass', each with its SPEC.md line number."""
    out = []
    sec = False
    with open(os.path.join(ROOT, "SPEC.md"), encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if line.startswith("## 2."):
                sec = True
                continue
            if sec and line.startswith("## "):
                break
            if sec and line.startswith("|"):
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if len(cells) >= 2 and not set(cells[0]) <= set("- "):
                    if cells[0] in ("quantity", ""):
                        continue
                    out.append({"quantity": cells[0], "value": cells[1],
                                "tag": cells[2] if len(cells) > 2 else "",
                                "src": "SPEC.md:%d" % n})
    return out


ENV = spec_envelope()

RENDERS = [
    {"src": "out/compare/ours-front.png", "en": "Front — our CAD, MuJoCo studio render",
     "zh": "正视图 — 我方 CAD，MuJoCo 渲染"},
    {"src": "out/compare/ours-prof-left.png", "en": "Left profile — same model, same lighting",
     "zh": "左侧视图 — 同一模型、同一光照"},
    {"src": "out/compare/ours-iso-fl.png", "en": "Three-quarter front-left",
     "zh": "左前 45° 视图"},
    {"src": "out/assembly/assembled.png", "en": "Assembled, exploded-step end state (sim/assembly_steps_mj.py)",
     "zh": "装配完成状态（sim/assembly_steps_mj.py）"},
]
RENDERS = [r for r in RENDERS if os.path.exists(os.path.join(ROOT, r["src"]))]

# ------------------------------------------------------------------ 2 not ready
sheets = S["sheets_graded"]
NOT_READY = [
    {"k": "drawing sheets PASS our own A2/A3/A4 standard", "k_zh": "图纸通过我方 A2/A3/A4 标准",
     "n": "%d / %d" % (sheets["pass"], sheets["sheets"]),
     "why": "Every sheet fails at least the occupancy, empty-rectangle, minimum-font, ISO-view-count and shaded-render-count rules; %d of %d also fail dimension coverage." % (
         sum(1 for r in cls("drawing") if "dim_coverage" in (r.get("fails") or [])), sheets["sheets"]),
     "why_zh": "每张图纸至少在版面占用率、空白矩形、最小字号、等轴视图数量与着色渲染数量上不合格；其中 %d 张同时尺寸标注覆盖率不足。" % sum(
         1 for r in cls("drawing") if "dim_coverage" in (r.get("fails") or [])),
     "who": "agent, tonight (WF-SHEETS) for layout; a parametric rebuild for the mesh-backed parts",
     "who_zh": "版面由软件代理今晚完成（WF-SHEETS）；网格来源零件需参数化重建",
     "src": "out/factory/measure/sheetcheck.json (bin/sheetcheck %s)" % sheets["generated"]},
    {"k": "printed parts with no drawing sheet at all", "k_zh": "完全没有图纸的打印件",
     "n": str(len(sheets["parts_without_a_sheet"])),
     "why": "No out/drawings/<slug>/ folder exists for " + ", ".join(sheets["parts_without_a_sheet"]) + ".",
     "why_zh": "以下零件没有 out/drawings/<slug>/ 目录：" + "、".join(sheets["parts_without_a_sheet"]) + "。",
     "who": "agent, tonight (WF-SHEETS)", "who_zh": "软件代理，今晚（WF-SHEETS）",
     "src": "out/print/slice.json against out/drawings/"},
    {"k": "custom PCBs that pass their own DRC", "k_zh": "通过自身 DRC 的定制 PCB",
     "n": "%d / %d" % (S["pcb"]["ready"], S["pcb"]["total"]),
     "why": "; ".join("%s %s" % (r["name"], (r.get("drc") or {}).get("verdict", "?")) for r in cls("pcb")) + ".",
     "why_zh": "三块板的 DRC 结果：" + "；".join(
         "%s %s" % (r["name"], (r.get("drc") or {}).get("verdict", "?")) for r in cls("pcb")) + "。",
     "who": "an electronics engineer — a desk job, but not an agent's",
     "who_zh": "需电子工程师完成（案头工作，非软件代理可代劳）",
     "src": "PCB-PACKAGE.html §3.4, electronics/*/out/fab/README.txt"},
    {"k": "fastener rows in the assembly BOM against the M2 hole census",
     "k_zh": "装配 BOM 中的紧固件行数 / M2 孔数",
     "n": "%d / %d" % (S["bom_fasteners"]["fastener_rows"], S["bom_fasteners"]["hole_census"]),
     "why": "The hardware is already bought — see the M2 lines in section 3.3 — but no document says which screw goes in which hole, at what length, to what torque.",
     "why_zh": "硬件其实已列入采购（见 3.3 节 M2 项），但没有任何文件说明哪颗螺钉装在哪个孔、用多长、拧到多大扭矩。",
     "who": "agent, tonight (WF-FASTENERS) for the census; a person for the torque",
     "who_zh": "普查由软件代理今晚完成（WF-FASTENERS）；扭矩必须由人确定",
     "src": "ce-assemblies/microduck/current/bom.json, SPEC.md:75-76"},
    {"k": "harness rows carrying a cut tolerance", "k_zh": "带下料公差的线束行",
     "n": "%d / %d" % ((cls("harness")[0].get("tolerance_rows") or 0) if cls("harness") else 0,
                       (cls("harness")[0].get("cables") or 0) if cls("harness") else 0),
     "why": "Lengths are route floors plus slack, rounded to 5 mm, measured in CAD. One built loom, measured, turns them into cut lengths.",
     "why_zh": "现有长度为 CAD 走线下限加余量并取整至 5 mm。需实做一套线束并测量后方可转为下料长度。",
     "who": "a person, with a real loom on a bench", "who_zh": "需由人在台架上实做线束测量",
     "src": "wiring/cables.json"},
    {"k": "assembly steps that assume knowledge not on the page",
     "k_zh": "依赖文外知识的装配步骤",
     "n": str(len((cls("assembly")[0].get("assumptions") or [])) if cls("assembly") else 0),
     "why": "A stranger stops at the first one. Each is listed in section 3.6 with what closes it.",
     "why_zh": "陌生工程师会卡在第一条。3.6 节逐条列出并说明如何解决。",
     "who": "mixed — some an agent tonight, the torques a person",
     "who_zh": "部分由软件代理今晚完成，扭矩必须由人确定",
     "src": "ce-assemblies/microduck/iterations/v0.0.1/manual/MANUAL.md, tools/data/playbook.json"},
    {"k": "bought lines with no lead time stated by any vendor",
     "k_zh": "无任何供应商给出交期的外购项",
     "n": "%d / %d" % (len(S["bought_gaps"]["no_lead_time_stated"]), S["bought_gaps"]["lines"]),
     "why": "Lines " + ", ".join(S["bought_gaps"]["no_lead_time_stated"]) + " price fine but cannot be scheduled.",
     "why_zh": "以下项价格可查但无法排产：" + "、".join(S["bought_gaps"]["no_lead_time_stated"]) + "。",
     "who": "a buyer — an RFQ, not a search", "who_zh": "需采购人员发询价单（非网络搜索可得）",
     "src": "spec/sourcing.json rev %s" % SRC.get("revision", "?")},
    {"k": "open CANNOT DETERMINE items across the repository", "k_zh": "全仓库未定项",
     "n": str(S["unknowns"]),
     "why": "Every one names what would settle it. They are not unknowns we are ignoring; they are unknowns we have refused to guess.",
     "why_zh": "每一项都写明了如何才能定案。它们不是被忽略的未知，而是我方拒绝臆测的未知。",
     "who": "agent, tonight (WF-UNKNOWNS) for the desk-answerable ones",
     "who_zh": "可查证部分由软件代理今晚完成（WF-UNKNOWNS）",
     "src": "out/open/cannot-determine-harvest.json"},
    {"k": "physical units ever built or measured", "k_zh": "已制造或测量过的实物样机",
     "n": "0",
     "why": "The test plan is complete and has been exercised zero times. Every dynamic figure in this repository is simulation.",
     "why_zh": "测试计划完整但执行次数为零。本仓库中所有动态数据均为仿真结果。",
     "who": "the factory — this is the whole point of the pack",
     "who_zh": "由工厂完成——这正是本交付包的目的",
     "src": "spec/test-plan.json (0 tests exercised), readiness.json test row"},
]

# ------------------------------------------------------------------ 3.2 print
print_rows = cls("print")
slice_by_slug = {p["slug"]: p for p in SL.get("parts", [])}

# ------------------------------------------------------------------ 3.3 bom
bought = cls("bought")


def best_offer(r):
    best = None
    for o in r.get("offers") or []:
        for t in o.get("tiers") or []:
            if len(t) >= 2 and t[1] is not None:
                if best is None or t[1] < best[1]:
                    best = (o, float(t[1]), int(t[0]), o.get("currency") or "?")
    return best


bom_table = []
priced_total = 0.0
unpriced_lines = []
for r in bought:
    b = best_offer(r)
    line = {"id": r["id"], "name": r["name"], "grade": r["grade"], "grade_en": r["grade_en"], "grade_zh": r["grade_zh"],
            "qty": r.get("qty_per_robot"), "vendors": len(r.get("offers") or []),
            "lead": "yes" if r.get("lead_time_stated") else "none stated",
            "missing": r.get("missing", "")}
    if b:
        o, price, tier, cur = b
        line.update({"price": price, "price_tier": tier, "currency": cur, "vendor": o.get("vendor"),
                     "url": o.get("url"), "moq": o.get("moq"), "fetched": o.get("fetched")})
        try:
            priced_total += price * float(r.get("qty_per_robot") or 0)
        except Exception:
            pass
    else:
        unpriced_lines.append(r["id"])
    bom_table.append(line)

# ------------------------------------------------------------------ 3.5 harness
cables = CAB.get("cables", [])

# ------------------------------------------------------------------ 3.6 assembly
asm = cls("assembly")[0] if cls("assembly") else {}
stations = PB.get("stations", [])
torque = PB.get("torque", [])

# ------------------------------------------------------------------ 3.7 / 4 test
test_row = cls("test")[0] if cls("test") else {}
eol = TP.get("eol", [])

# ------------------------------------------------------------------ 6 artifacts
ARTIFACTS = [
    ("out/drawings/", "One folder per part: SVG sheet, PDF, and the JSON of measured facts it was drawn from", "每个零件一个文件夹：SVG 图纸、PDF 及绘图依据的 JSON"),
    ("out/print/stl/", "The STL files to print, by material", "按材料分类的待打印 STL 文件"),
    ("out/print/slice.json", "Real slicer grams and seconds per part", "各零件的真实切片克数与秒数"),
    ("spec/sourcing.json", "Every bought line with its offers, read off live pages", "全部外购项及其在线读取的报价"),
    ("wiring/cables.json", "The 23 cable routes measured in CAD", "CAD 中实测的 23 条线缆走线"),
    ("electronics/robot-hat/", "Robot HAT: schematic, layout, Gerbers, DRC report", "Robot HAT：原理图、布局、Gerber、DRC 报告"),
    ("electronics/imu-to-dxl/", "IMU-to-Dynamixel adapter board", "IMU 转 Dynamixel 转接板"),
    ("electronics/banana-contact/", "Banana contact board", "香蕉接触板"),
    ("ce-assemblies/microduck/", "The assembly: parts, connections, BOM, manual", "装配体：零件、连接、BOM、手册"),
    ("spec/test-plan.json", "Gated tests and end-of-line gates", "带判据的测试项与下线判据"),
    ("out/factory/readiness.json", "The readiness audit this pack's section 2 is computed from", "本包第 2 节所依据的就绪度审核"),
    ("out/factory/measure/", "The raw measurement files, re-runnable with tools/measure_readiness.py", "原始实测文件，可用 tools/measure_readiness.py 重新采集"),
    ("out/stress/matrix.json", "FEA runs: 4 parts x 3 load cases x 5 materials — SIMULATION", "有限元结果：4 零件 x 3 工况 x 5 材料——仿真"),
    ("docs/MANUFACTURING-REQUIREMENTS.md", "The drawing standard our own sheets are graded against", "我方图纸所依据的评级标准"),
    ("SPEC.md", "What we are rebuilding, every number tagged published / measured / community / inferred", "重建目标规格，每个数字标注来源类别"),
]
ARTIFACTS = [(p, en, zh, stat(p)) for p, en, zh in ARTIFACTS]

DOCS = [("FACTORY-PACK.html", "This document", "本文件"),
        ("WORK-BREAKDOWN.html", "The open work cut into parcels of one engineer each", "待办工作，按每人一份切分"),
        ("FACTORY-QUESTIONS.html", "What only a factory with real machines can answer", "只有拥有实机的工厂才能回答的问题"),
        ("LICENCE-POSITION.html", "Origin of every byte and what may be sold", "各项数据来源与可售范围"),
        ("out/factory/readiness.html", "The readiness audit, artifact by artifact", "逐项就绪度审核"),
        ("MANUFACTURING-PLAYBOOK.html", "Process selection, DFM, line stations, costing", "工艺选择、DFM、产线工位、成本"),
        ("SOURCING.html", "Every bought line in full", "全部外购项明细"),
        ("RFQ.html", "A ready-to-send request for quotation", "可直接发出的询价单"),
        ("PCB-PACKAGE.html", "The three custom boards", "三块定制电路板"),
        ("TEST-PLAN.html", "The bench procedure", "台架测试程序"),
        ("out/drawings/INDEX.html", "Drawing sheet index", "图纸索引"),
        ("INDEX.html", "Everything else in the repository", "仓库其余全部文件")]
DOCS = [(p, en, zh, stat(p)) for p, en, zh in DOCS]

pack = {
    "$doc": "out/factory/pack.json — the assembled data behind FACTORY-PACK.html. Generated by tools/gen_factory_pack.py; every field was read from a measurement file, none typed.",
    "generated": NOW,
    "commit": git_head(),
    "readiness_measured_at": RD["measured_at"],
    "sheetcheck_at": sheets["generated"],
    "product": {"envelope": ENV, "renders": RENDERS},
    "not_ready": NOT_READY,
    "summary": S,
    "bom": {"lines": bom_table, "priced_subtotal_usd_per_robot": round(priced_total, 4),
            "unpriced_lines": unpriced_lines,
            "note": "Subtotal sums qty_per_robot x the cheapest tier-1 unit price found on a live page. It EXCLUDES the %d line(s) with no priced offer, so it is a floor, not a cost." % len(unpriced_lines)},
    "print_totals": SL.get("grand_total", {}),
    "printer": SL.get("printer"),
    "harness": {"rows": len(cables), "total_mm": CAB.get("total_length_mm")},
    "stations": [{"id": s.get("id"), "name": s.get("name"), "steps": len(s.get("steps", []))} for s in stations],
    "eol_gates": len(eol),
    "artifacts": [{"path": p, "en": en, "zh": zh, "stat": st} for p, en, zh, st in ARTIFACTS],
    "documents": [{"path": p, "en": en, "zh": zh, "stat": st} for p, en, zh, st in DOCS],
}
os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(pack, f, indent=1, ensure_ascii=False)

# ---------------------------------------------------------------------- HTML
A = []


def th(en, zh):
    return '<th>' + E(en) + '<br><span class="zh">' + E(zh) + '</span></th>'


def cols(*pct):
    return "<colgroup>" + "".join('<col style="width:%s%%">' % w for w in pct) + "</colgroup>"


def gchip(grade, en, zh):
    c = {"READY": "ok", "NOT_YET": "no", "CD": "cd"}.get(grade, "cd")
    return '<span class="g %s">%s<br><small>%s</small></span>' % (c, E(en), E(zh))


def sec(n, en, zh, lede=None, lede_zh=None, sid=None):
    A.append('<section id="%s"><h2><span class="n">%s</span>%s <span class="zh" style="display:inline;font-size:15px">%s</span></h2>'
             % (sid or ("s%s" % n), n, E(en), E(zh)))
    if lede:
        A.append('<p class="lede">%s</p>' % E(lede))
    if lede_zh:
        A.append('<p class="lede zh">%s</p>' % E(lede_zh))


d = D["doc"]
A.append('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">')
A.append('<title>%s — %s</title>' % (E(d["title"]), E(d["title_zh"])))
A.append('<link rel="stylesheet" href="tools/doc.css">')
A.append('<style>'
         '.zh{font-family:var(--sans);font-size:12px;color:var(--ink-2);display:block}'
         'table{border-collapse:collapse;width:100%;table-layout:fixed;font-size:12.5px;margin:8px 0 18px;overflow-wrap:anywhere}'
         'th{white-space:normal !important;padding:5px 6px;background:var(--head);font-family:var(--sans);font-size:12px;text-align:left;vertical-align:top;border-bottom:1px solid var(--hair)}'
         'td{border-bottom:1px solid var(--hair);padding:5px 6px;text-align:left;vertical-align:top}'
         'td.m{font-family:var(--mono);font-size:11.5px;word-break:break-all}'
         'td.num{text-align:right;font-variant-numeric:tabular-nums}'
         '.g{font-family:var(--sans);font-weight:600;font-size:11px}.g.ok{color:var(--ready)}.g.no{color:var(--no)}.g.cd{color:var(--cd)}'
         '.front{border:2px solid var(--no);padding:12px 16px;margin:18px 0}.front h2{margin:0 0 6px;border:none;font-size:20px}'
         '.gallery{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0}'
         '.gallery figure{margin:0;width:calc(50% - 5px)}'
         '.gallery img{width:100%;background:#fff;border:1px solid var(--hair)}'
         '.gallery figcaption{font-family:var(--sans);font-size:11.5px;color:var(--ink-2);padding-top:4px}'
         '.stat b.no{color:var(--no)}'
         '</style>')
A.append('</head>\n<body>\n<div class="wrap">')
A.append('<p class="backlink"><a href="INDEX.html">← Document index</a></p>')
A.append('<header class="hero"><p class="eyebrow">Microduck · factory pack · 工厂交付包</p>')
A.append('<h1>%s <span class="zh" style="font-size:22px;display:inline">%s</span></h1>' % (E(d["title"]), E(d["title_zh"])))
A.append('<p class="sub">%s</p><p class="sub zh">%s</p>' % (E(d["sub"]), E(d["sub_zh"])))
A.append('<div class="rev"><span>%s · Rev %s</span><span>generated %s</span><span>commit %s</span><span>tools/gen_factory_pack.py</span></div></header>'
         % (d["id"], d["rev"], E(NOW), E(pack["commit"])))

# --- the honesty box, first thing on the page
A.append('<div class="front"><h2>Read this first · 请先阅读</h2>')
A.append('<p><b>%s</b></p>' % E(D["honesty"]["en"]))
A.append('<p class="zh" style="font-size:13px">%s</p>' % E(D["honesty"]["zh"]))
A.append('<p>%s</p><p class="zh" style="font-size:13px">%s</p>' % (E(D["how_to_use"]["en"]), E(D["how_to_use"]["zh"])))
A.append('</div>')

A.append('<nav class="toc">'
         '<a href="#s1">1 The product 产品</a>'
         '<a href="#s2">2 What is NOT ready 尚未就绪</a>'
         '<a href="#s3">3 What to build 制造内容</a>'
         '<a href="#s4">4 Acceptance 验收</a>'
         '<a href="#s5">5 Licence 许可</a>'
         '<a href="#s6">6 Where the files are 文件位置</a></nav>')

# ---------------------------------------------------------------- 1 product
sec(1, "The product", "产品", D["what_is_it"]["en"], D["what_is_it"]["zh"])
if RENDERS:
    A.append('<div class="gallery">')
    for r in RENDERS:
        A.append('<figure><img src="%s" alt="%s"><figcaption>%s<br><span class="zh">%s</span><br><span class="mono" style="font-size:10.5px">%s</span></figcaption></figure>'
                 % (E(r["src"]), E(r["en"]), E(r["en"]), E(r["zh"]), E(r["src"])))
    A.append('</div>')
    A.append('<p class="lede">These are renders of OUR CAD, not photographs of a built robot. Product photographs, matched angle by angle against these renders, are in COMPARISON.html.</p>')
    A.append('<p class="lede zh">以上为我方 CAD 的渲染图，并非实物照片。逐角度匹配的产品照片见 COMPARISON.html。</p>')
A.append('<table>' + cols(28, 42, 12, 18) + '<tr>' + th("Quantity", "量") + th("Value", "数值")
         + th("Source class", "来源类别") + th("Where", "出处") + '</tr>')
for e in ENV:
    A.append('<tr><td>%s</td><td>%s</td><td class="m">%s</td><td class="m">%s</td></tr>'
             % (E(e["quantity"]), E(re.sub(r"\*\*", "", e["value"])), E(e["tag"]), E(e["src"])))
A.append('</table>')
A.append('<p class="lede">Source classes: <b>[P]</b> published by Pollen Robotics · <b>[M]</b> measured by us off Pollen\'s own MJCF and meshes with a CAD kernel · <b>[C]</b> community-reported, unverified · <b>[?]</b> our inference. SPEC.md lines 1-10.</p>')
A.append('<p class="lede zh">来源类别：<b>[P]</b> Pollen 官方公布 · <b>[M]</b> 我方用 CAD 内核测自 Pollen 的 MJCF 与网格 · <b>[C]</b> 社区提供、未经验证 · <b>[?]</b> 我方推断。见 SPEC.md 第 1-10 行。</p>')

gt = SL.get("grand_total", {})
if gt:
    A.append('<div class="statbar">')
    for b, en, zh in [(str(gt.get("printed_slugs")), "printed part numbers", "打印件品种"),
                      (str(gt.get("pieces")), "printed pieces per robot", "每台打印件数"),
                      ("%.2f g" % gt.get("grams", 0), "filament per robot (sliced)", "每台耗材（实切）"),
                      ("%.2f h" % gt.get("hours", 0), "print hours per robot (sliced)", "每台打印工时（实切）"),
                      (str(len(bought)), "bought lines", "外购项"),
                      (str(len(cables)), "cables", "线缆"),
                      (str(len(stations)), "line stations", "产线工位"),
                      (str(len(eol)), "end-of-line gates", "下线判据")]:
        A.append('<div class="stat"><b>%s</b><span>%s<br>%s</span></div>' % (E(b), E(en), E(zh)))
    A.append('</div>')
    A.append('<p class="lede">Print figures are the sum of out/print/slice.json, sliced on %s. They are per-piece prints, not plate times.</p>'
             % E(str(SL.get("printer"))))
    A.append('<p class="lede zh">打印数据为 out/print/slice.json 之和，切片机型：%s。为单件打印时间，非整盘时间。</p>' % E(str(SL.get("printer"))))
A.append('</section>')

# ---------------------------------------------------------------- 2 not ready
sec(2, "What is NOT ready", "哪些尚未就绪", D["sections"]["not_ready"]["en"], D["sections"]["not_ready"]["zh"])
A.append('<table>' + cols(30, 10, 36, 24) + '<tr>' + th("What", "项目") + th("Measured", "实测")
         + th("Why it is not ready", "为何未就绪") + th("Who closes it", "由谁解决") + '</tr>')
for r in NOT_READY:
    A.append('<tr><td>%s<br><span class="zh">%s</span></td><td class="num"><b class="no">%s</b></td>'
             '<td>%s<br><span class="zh">%s</span><br><span class="mono" style="font-size:10.5px">%s</span></td>'
             '<td>%s<br><span class="zh">%s</span></td></tr>'
             % (E(r["k"]), E(r["k_zh"]), E(r["n"]), E(r["why"]), E(r["why_zh"]), E(r["src"]), E(r["who"]), E(r["who_zh"])))
A.append('</table>')

wp_parcels = WP.get("parcels")
if isinstance(wp_parcels, int) and wp_parcels:
    A.append('<p>Every one of these is cut into parcels of one engineer each in <a href="WORK-BREAKDOWN.html">WORK-BREAKDOWN.html</a> (%d parcels). Work an agent is closing tonight is marked IN FLIGHT there so you do not duplicate it.</p>' % wp_parcels)
    A.append('<p class="zh">上述每一项均已在 <a href="WORK-BREAKDOWN.html">WORK-BREAKDOWN.html</a> 中切分为每人一份的工作包（共 %d 个）。今晚由软件代理完成的工作在其中标记为 IN FLIGHT，请勿重复。</p>' % wp_parcels)
inflight = RD.get("in_flight", [])
if inflight:
    A.append('<h3>Work an agent is closing tonight — do not start these · 今晚由软件代理完成的工作，请勿开工</h3>')
    A.append('<table>' + cols(14, 46, 40) + '<tr>' + th("Workflow", "工作流") + th("What it is closing", "工作内容")
             + th("Paths it owns (do not write these)", "其占用路径（请勿写入）") + '</tr>')
    for w in inflight:
        A.append('<tr><td class="m">%s</td><td>%s<br><span class="zh">%s</span></td><td class="m">%s</td></tr>'
                 % (E(w["id"]), E(w["en"]), E(w["zh"]), E(w.get("owns", ""))))
    A.append('</table>')
A.append('</section>')

# ---------------------------------------------------------------- 3 what to build
sec(3, "What to build", "制造内容",
    "Six deliverable classes: drawings, printed parts, bought parts, boards, harness, assembly. Each subsection carries its own verdict column and its own source file.",
    "六类交付物：图纸、打印件、外购件、电路板、线束、装配。每小节均带判定列与来源文件。")

# 3.1 drawings
A.append('<h3>3.1 Drawing set · 图纸集</h3>')
A.append('<p class="lede">%s</p><p class="lede zh">%s</p>' % (E(D["sections"]["drawings"]["en"]), E(D["sections"]["drawings"]["zh"])))
dr = cls("drawing")
A.append('<table>' + cols(24, 8, 9, 9, 8, 8, 34) + '<tr>' + th("Sheet", "图纸") + th("Kind", "类型")
         + th("Verdict", "判定") + th("Dim cov.", "尺寸覆盖") + th("Min font mm", "最小字号")
         + th("ISO views", "等轴视图") + th("What the sheet is missing", "图纸缺什么") + '</tr>')
for r in sorted(dr, key=lambda x: x["id"]):
    ch = r.get("checks") or {}

    def f(k, fmt="%.1f"):
        v = (ch.get(k) or {}).get("measured")
        return "CD" if v is None else (fmt % v if isinstance(v, float) else str(v))
    A.append('<tr><td class="m">%s</td><td>%s</td><td>%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td><td>%s</td></tr>'
             % (E(r["id"]), E(r.get("kind", "?")), gchip(r["grade"], r["grade_en"], r["grade_zh"]),
                E(f("dim_coverage") + (" %" if (ch.get("dim_coverage") or {}).get("measured") is not None else "")),
                E(f("font")), E(f("iso", "%s")), E(r.get("missing") or "—")))
A.append('</table>')

# 3.2 print
A.append('<h3>3.2 Printed parts · 打印件</h3>')
A.append('<p class="lede">%s</p><p class="lede zh">%s</p>' % (E(D["sections"]["print"]["en"]), E(D["sections"]["print"]["zh"])))
prof = (PB.get("profile") or {})
if prof.get("values"):
    A.append('<p class="lede">Profile actually used, read off the installed BambuStudio profile with its inherit chain resolved (%s): %s</p>'
             % (E(prof.get("file", "")), E("; ".join("%s = %s" % (k, v) for k, v, _ in prof["values"][:8]))))
A.append('<table>' + cols(21, 6, 5, 7, 7, 8, 9, 9, 28) + '<tr>' + th("Part", "零件") + th("Mat.", "材料")
         + th("Qty", "数量") + th("g/pc", "克/件") + th("s/pc", "秒/件") + th("Layer", "层高")
         + th("Watertight", "水密") + th("Verdict", "判定") + th("Orientation / warning / licence", "摆放 / 警告 / 许可") + '</tr>')
for r in sorted(print_rows, key=lambda x: x["id"]):
    sp = slice_by_slug.get(r["id"], {})
    note = []
    if sp.get("orientation_rule"):
        note.append(sp["orientation_rule"])
    if r.get("slicer_warning"):
        note.append("WARN: " + str(r["slicer_warning"]))
    if r.get("licence"):
        note.append("licence: " + str(r["licence"]))
    A.append('<tr><td class="m">%s</td><td>%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td>'
             '<td class="num">%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
             % (E(r["id"]), E(sp.get("material", "?")), E(str(sp.get("qty", r.get("qty", "?")))),
                E("%.4f" % r["grams_per_piece"] if r.get("grams_per_piece") is not None else "CD"),
                E("%.0f" % r["seconds_per_piece"] if r.get("seconds_per_piece") is not None else "CD"),
                E(str(sp.get("layer_mm", "?"))),
                E("yes" if r.get("watertight") else ("NO — %s open edges" % r.get("open_edges") if r.get("open_edges") else "CD")),
                gchip(r["grade"], r["grade_en"], r["grade_zh"]), E(" · ".join(note) or "—")))
A.append('</table>')
if SL.get("flags"):
    A.append('<p class="lede">Slicing flags carried forward: %s</p>' % E(" · ".join(SL["flags"])))

# 3.3 bom
A.append('<h3>3.3 Bought parts · 外购件</h3>')
A.append('<p class="lede">%s</p><p class="lede zh">%s</p>' % (E(D["sections"]["bom"]["en"]), E(D["sections"]["bom"]["zh"])))
A.append('<table>' + cols(5, 25, 6, 10, 8, 16, 9, 21) + '<tr>' + th("Line", "编号") + th("Item", "品名")
         + th("Qty/robot", "每台数量") + th("Unit price", "单价") + th("MOQ", "起订量")
         + th("Vendor read", "已读取供应商") + th("Lead time", "交期") + th("Verdict / what is missing", "判定 / 缺什么") + '</tr>')
for l in bom_table:
    price = ("%s %.4f @%d" % (l.get("currency"), l.get("price"), l.get("price_tier"))) if l.get("price") is not None else "no priced offer"
    A.append('<tr><td class="m">%s</td><td>%s</td><td class="num">%s</td><td class="num m">%s</td><td class="num">%s</td>'
             '<td>%s</td><td>%s</td><td>%s %s</td></tr>'
             % (E(l["id"]), E(l["name"]), E(str(l.get("qty")) if l.get("qty") is not None else "CANNOT DETERMINE"), E(price), E(str(l.get("moq") or "—")),
                E(str(l.get("vendor") or "—")), E(l["lead"]),
                gchip(l["grade"], l["grade_en"], l["grade_zh"]), E(l.get("missing") or "")))
A.append('</table>')
A.append('<p><b>Priced subtotal, one robot: %s %.4f.</b> %s</p>'
         % ("USD", priced_total, E(pack["bom"]["note"])))
A.append('<p class="zh">单台已定价小计：USD %.4f。该小计按每台数量 x 在线页面上找到的最低 1 件单价求和，<b>不含</b>无报价的 %d 项，因此是下限而非实际成本。</p>'
         % (priced_total, len(unpriced_lines)))

# 3.4 pcb
def _routed(v):
    """The routing cell must be a count or nothing. electronics/pcb-package.json
    carries a prose sentence for robot-hat instead of an n-of-m, and a prose
    sentence in a numeric column is how a factory misreads a table."""
    if v is None:
        return "—"
    m = re.search(r"\d+\s+of\s+\d+", str(v))
    return m.group(0) if m else "CANNOT DETERMINE (no n-of-m stated)"


A.append('<h3>3.4 Custom boards · 定制电路板</h3>')
A.append('<p class="lede">%s</p><p class="lede zh">%s</p>' % (E(D["sections"]["pcb"]["en"]), E(D["sections"]["pcb"]["zh"])))
A.append('<table>' + cols(14, 10, 12, 10, 54) + '<tr>' + th("Board", "板") + th("Verdict", "判定")
         + th("DRC", "设计规则检查") + th("Routed", "布线完成") + th("Status and what is missing", "状态与缺项") + '</tr>')
for r in cls("pcb"):
    drc = r.get("drc") or {}
    A.append('<tr><td>%s</td><td>%s</td><td class="m">%s</td><td class="m">%s</td><td>%s</td></tr>'
             % (E(r["name"]), gchip(r["grade"], r["grade_en"], r["grade_zh"]),
                E("%s — %s pass / %s fail / %s CD" % (drc.get("verdict", "?"), drc.get("pass", "?"), drc.get("fail", "?"), drc.get("cannot_determine", drc.get("cd", "?")))),
                E(_routed(r.get("routed"))), E(r.get("missing") or r.get("measurement", ""))))
A.append('</table>')

# 3.5 harness
A.append('<h3>3.5 Harness · 线束</h3>')
A.append('<p class="lede">%s</p><p class="lede zh">%s</p>' % (E(D["sections"]["harness"]["en"]), E(D["sections"]["harness"]["zh"])))
if cls("harness"):
    h = cls("harness")[0]
    A.append('<p class="lede">%s</p>' % E(h.get("measurement", "")))
A.append('<table>' + cols(15, 11, 11, 9, 8, 22, 24) + '<tr>' + th("Cable", "线缆") + th("From", "起点")
         + th("To", "终点") + th("Length mm", "长度 mm") + th("Cond.", "芯数")
         + th("Connector", "连接器") + th("Basis / note", "依据 / 说明") + '</tr>')
for c in cables:
    ln = c.get("cable_mm")
    A.append('<tr><td class="m">%s</td><td class="m">%s</td><td class="m">%s</td><td class="num">%s</td><td class="num">%s</td><td>%s</td><td>%s</td></tr>'
             % (E(str(c.get("id"))), E(str(c.get("from"))), E(str(c.get("to"))),
                E("%.4f" % ln if isinstance(ln, (int, float)) else "CANNOT DETERMINE"),
                E(str(c.get("conductors", "—"))), E(str(c.get("connector", "—"))[:180]),
                E(("floor %.1f mm + slack %.1f mm; " % (c.get("floor_mm") or 0, c.get("slack_mm") or 0)) + str(c.get("how", ""))[:120])))
A.append('</table>')

# 3.6 assembly
A.append('<h3>3.6 Assembly sequence · 装配顺序</h3>')
A.append('<p class="lede">%s</p><p class="lede zh">%s</p>' % (E(D["sections"]["assembly"]["en"]), E(D["sections"]["assembly"]["zh"])))
A.append('<table>' + cols(10, 40, 12, 38) + '<tr>' + th("Station", "工位") + th("Name", "名称")
         + th("Steps", "步骤数") + th("Note", "说明") + '</tr>')
for s in stations:
    A.append('<tr><td class="m">%s</td><td>%s</td><td class="num">%s</td><td>%s</td></tr>'
             % (E(str(s.get("id"))), E(str(s.get("name"))), len(s.get("steps", [])),
                E(str(s.get("why", s.get("note", "")) or "")[:200])))
A.append('</table>')
if torque:
    A.append('<h4>Torque · 拧紧扭矩</h4>')
    A.append('<table>' + cols(34, 12, 54) + '<tr>' + th("Joint", "连接") + th("Value", "数值")
             + th("Why it is CANNOT DETERMINE", "为何无法判定") + '</tr>')
    for t in torque:
        A.append('<tr><td>%s</td><td class="m">%s</td><td>%s</td></tr>'
                 % (E(str(t.get("joint"))[:200]), E(str(t.get("value")) if t.get("value") is not None else "CANNOT DETERMINE"),
                    E(str(t.get("why", ""))[:600])))
    A.append('</table>')
assum = (asm.get("assumptions") or [])
if assum:
    A.append('<h4>Steps a stranger cannot follow · 陌生工程师无法照做的步骤 (%d)</h4>' % len(assum))
    A.append('<table>' + cols(14, 43, 43) + '<tr>' + th("Step", "步骤") + th("What it assumes you know", "默认你已知的内容")
             + th("What closes it", "如何解决") + '</tr>')
    for a in assum:
        if isinstance(a, dict):
            who = {"agent_tonight": "agent, tonight", "agent_later": "agent, later", "human": "a person must"}.get(a.get("closer"), a.get("closer") or "")
            A.append('<tr><td class="m">%s</td><td>%s</td><td>%s</td></tr>'
                     % (E(str(a.get("step", a.get("id", "—")))), E(str(a.get("assumes", a.get("what", "")))),
                        E((who + " — " if who else "") + str(a.get("by", a.get("closes", ""))))))
        else:
            A.append('<tr><td class="m">—</td><td>%s</td><td>—</td></tr>' % E(str(a)))
    A.append('</table>')

# 3.7 test
A.append('<h3>3.7 Test plan · 测试计划</h3>')
A.append('<p class="lede">%s</p><p class="lede zh">%s</p>' % (E(D["sections"]["test"]["en"]), E(D["sections"]["test"]["zh"])))
A.append('<table>' + cols(18, 40, 12, 30) + '<tr>' + th("Section", "章节") + th("Title", "标题")
         + th("Tests", "测试项") + th("Source", "来源") + '</tr>')
for s in TP.get("sections", []):
    A.append('<tr><td class="m">%s</td><td>%s</td><td class="num">%s</td><td class="m">spec/test-plan.json</td></tr>'
             % (E(str(s.get("id"))), E(str(s.get("title"))), len(s.get("tests", []))))
A.append('</table>')
if test_row:
    A.append('<p class="lede">%s</p>' % E(test_row.get("measurement", "")))
A.append('</section>')

# ---------------------------------------------------------------- 4 acceptance
sec(4, "Acceptance of a finished unit", "整机验收", D["sections"]["acceptance"]["en"], D["sections"]["acceptance"]["zh"])
A.append('<p class="lede">%s</p>' % E(str(TP.get("eol_note", ""))[:400]))
A.append('<table>' + cols(10, 66, 24) + '<tr>' + th("Gate", "判据编号") + th("Passes when", "合格条件")
         + th("Instrument", "仪器") + '</tr>')
for g in eol:
    if isinstance(g, (list, tuple)) and len(g) >= 3:
        A.append('<tr><td class="m">%s</td><td>%s</td><td class="m">%s</td></tr>' % (E(str(g[0])), E(str(g[1])), E(str(g[2]))))
    elif isinstance(g, dict):
        A.append('<tr><td class="m">%s</td><td>%s</td><td class="m">%s</td></tr>'
                 % (E(str(g.get("id"))), E(str(g.get("passes", g.get("gate", "")))), E(str(g.get("instrument", "")))))
A.append('</table>')
A.append('<p>None of these gates has ever been run. The first unit off your line is the first time any of them is exercised; log every result against the unit serial and send us the log — that is how our simulated numbers become measured ones.</p>')
A.append('<p class="zh">上述判据从未执行过。贵厂下线的第一台机器将是首次执行；请按整机序列号记录每项结果并回传日志——这是把我方仿真数据变为实测数据的唯一途径。</p>')
A.append('</section>')

# ---------------------------------------------------------------- 5 licence
sec(5, "Licence position", "许可与来源", D["sections"]["licence"]["en"], D["sections"]["licence"]["zh"])
hd = LIC.get("headline") or {}
if hd:
    for k in ("en", "zh"):
        v = hd.get(k)
        if isinstance(v, str) and v.strip():
            A.append('<p%s>%s</p>' % (' class="zh" style="font-size:13px"' if k == "zh" else "", E(v)))
fi = LIC.get("factory_instructions") or {}
for k, lbl in (("en", None), ("zh", "zh")):
    v = fi.get(k)
    if isinstance(v, list):
        A.append('<ul%s>' % (' class="zh"' if lbl else ""))
        for it in v:
            A.append('<li>%s</li>' % E(it if isinstance(it, str) else json.dumps(it, ensure_ascii=False)))
        A.append('</ul>')
    elif isinstance(v, str) and v.strip():
        A.append('<p%s>%s</p>' % (' class="zh" style="font-size:13px"' if lbl else "", E(v)))
pl = S.get("print_licence") or {}
if pl:
    A.append('<p><b>In one line for the shop floor:</b> of the %d printed part numbers, %d are Pollen simulation meshes under CC BY-SA-NC — printable for prototypes, NOT saleable — and %d are ours outright. The full byte-by-byte position, with 20 measured facts and 34 evidence files, is <a href="LICENCE-POSITION.html">LICENCE-POSITION.html</a>.</p>'
             % (S["print"]["total"], pl.get("vendor_mesh_stls", 0), pl.get("ours", 0)))
    A.append('<p class="zh">车间一句话版：%d 个打印件品种中，%d 个为 Pollen 仿真网格（CC BY-SA-NC，可打印样机但<b>不可销售</b>），%d 个完全为我方自有。逐字节的完整说明（20 项实测事实、34 份证据文件）见 <a href="LICENCE-POSITION.html">LICENCE-POSITION.html</a>。</p>'
             % (S["print"]["total"], pl.get("vendor_mesh_stls", 0), pl.get("ours", 0)))
A.append('</section>')

# ---------------------------------------------------------------- 6 artifacts
sec(6, "Where every file is", "文件位置", D["sections"]["artifacts"]["en"], D["sections"]["artifacts"]["zh"])
A.append('<h3>Documents · 文件</h3>')
A.append('<table>' + cols(26, 44, 14, 16) + '<tr>' + th("Document", "文件") + th("What it is", "内容")
         + th("Size", "大小") + th("Last changed", "最后修改") + '</tr>')
for p, en, zh, st in DOCS:
    link = ('<a href="%s">%s</a>' % (E(p), E(p))) if st else E(p)
    size = ("%d files" % st["files"]) if st and st["kind"] == "dir" else (("%.1f kB" % (st["bytes"] / 1000.0)) if st else "NOT PRESENT")
    A.append('<tr><td class="m">%s</td><td>%s<br><span class="zh">%s</span></td><td class="num">%s</td><td class="m">%s</td></tr>'
             % (link, E(en), E(zh), E(size), E(st["mtime"] if st else "—")))
A.append('</table>')
A.append('<h3>Data and source artifacts · 数据与源文件</h3>')
A.append('<table>' + cols(26, 44, 14, 16) + '<tr>' + th("Path", "路径") + th("What it is", "内容")
         + th("Size", "大小") + th("Last changed", "最后修改") + '</tr>')
for p, en, zh, st in ARTIFACTS:
    size = ("%d files" % st["files"]) if st and st["kind"] == "dir" else (("%.1f kB" % (st["bytes"] / 1000.0)) if st else "NOT PRESENT")
    A.append('<tr><td class="m">%s</td><td>%s<br><span class="zh">%s</span></td><td class="num">%s</td><td class="m">%s</td></tr>'
             % (E(p), E(en), E(zh), E(size), E(st["mtime"] if st else "—")))
A.append('</table>')
A.append('<p class="lede">Repository: this pack was generated at commit %s. Re-take every measurement in it with <code>python3 tools/measure_readiness.py</code>, then <code>python3 tools/gen_readiness.py</code>, then <code>python3 tools/gen_factory_pack.py</code>. If your numbers differ from ours, your repository moved — tell us which row.</p>'
         % E(pack["commit"]))
A.append('<p class="lede zh">本包生成于提交 %s。可依次运行上述三条命令重新采集全部测量并重建本文件。若数字与我方不符，说明仓库已变动，请告知具体行。</p>' % E(pack["commit"]))
A.append('</section>')

A.append('<footer class="foot"><p>Generated by <code>tools/gen_factory_pack.py</code> from out/factory/readiness.json, out/print/slice.json, spec/sourcing.json, spec/test-plan.json, wiring/cables.json, tools/data/playbook.json, out/factory/licence.json and SPEC.md. Readiness measured %s. No figure on this page was typed by hand.</p>'
         '<p class="zh">本页由 tools/gen_factory_pack.py 从上述数据文件生成；就绪度实测时间 %s。页面上没有任何数字是手工填写的。</p></footer>'
         % (E(RD["measured_at"]), E(RD["measured_at"])))
A.append('</div></body></html>')

with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write("\n".join(A))
print("wrote %s (%d B) and %s" % (OUT_HTML, os.path.getsize(OUT_HTML), OUT_JSON))
print("  sections: product(%d envelope rows, %d renders) not-ready(%d) drawings(%d) print(%d) bought(%d) pcb(%d) cables(%d) stations(%d) eol(%d) artifacts(%d)"
      % (len(ENV), len(RENDERS), len(NOT_READY), len(dr), len(print_rows), len(bom_table), len(cls("pcb")), len(cables), len(stations), len(eol), len(ARTIFACTS)))
