#!/usr/bin/env python3
"""gen_questions.py — FACTORY-QUESTIONS.html: the questions only a factory with
real machines, real materials and real measurement can answer.

    python3 tools/gen_questions.py

The prose lives in tools/data/factory_questions.json and carries {tokens}
instead of numbers. This script computes every token from a measurement file and
fills it. AN UNFILLED TOKEN IS A HARD ERROR — the page cannot ship a literal
"{pla_yield}" to a factory, and it cannot ship a typed number either.

Reads:
    ce-cad/cecad/fits.py                the material row every safety factor rests on
    out/stress/matrix.json              the FEA runs and the material sweep
    out/print/slice.json                real slicer grams and seconds
    out/drawings/microduck-shin/result.json   the sheets' own tolerance-basis note
    spec/sourcing.json                  fastener quantities actually bought
    electronics/pcb-package.json        board outlines, finishes, fab capability
    tools/data/playbook.json            stations, rates, print profile, torque
    out/factory/readiness.json          grades, licence split, sheet count
    out/factory/pack.json               the pack's own BOM and gate counts
    out/jigs/jigs.json                  the fixtures we have drawn
    SPEC.md                             hole census and bearing counts

Writes:
    out/factory/questions.json          every question with its answer branches
    FACTORY-QUESTIONS.html              the document, EN + 简体中文
"""
import datetime
import glob
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WORKSHOP = os.path.dirname(os.path.dirname(ROOT))
OUT_HTML = os.path.join(ROOT, "FACTORY-QUESTIONS.html")
OUT_JSON = os.path.join(ROOT, "out", "factory", "questions.json")
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
E = html.escape


def J(rel, default=None):
    p = rel if os.path.isabs(rel) else os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return default
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def T(rel):
    p = rel if os.path.isabs(rel) else os.path.join(ROOT, rel)
    return open(p, encoding="utf-8").read() if os.path.exists(p) else ""


D = J("tools/data/factory_questions.json")
SL = J("out/print/slice.json", {})
MX = J("out/stress/matrix.json", {})
SRC = J("spec/sourcing.json", {})
PCB = J("electronics/pcb-package.json", {})
PB = J("tools/data/playbook.json", {})
RD = J("out/factory/readiness.json", {})
PK = J("out/factory/pack.json", {})
JG = J("out/jigs/jigs.json", {})
SHEET = J("out/drawings/microduck-shin/result.json", {})
SPEC = T("SPEC.md")
FITS = T(os.path.join(WORKSHOP, "ce-cad", "cecad", "fits.py"))

F = {}          # the token table
WHY = {}        # token -> where it came from, printed in the provenance table


def fact(key, value, src):
    F[key] = value
    WHY[key] = src
    return value


# ---- materials: the one number every safety factor rests on -----------------
mrow, mline = None, None
for n, line in enumerate(FITS.splitlines(), 1):
    m = re.match(r'\s*"PLA":\s*Material\("PLA",\s*([\d.]+),\s*([\d.]+),\s*([\d.]+)\)', line)
    if m:
        mrow, mline = m, n
        break
if not mrow:
    raise SystemExit("gen_questions: could not read the PLA material row out of ce-cad/cecad/fits.py")
fact("pla_density", mrow.group(1), "ce-cad/cecad/fits.py:%d" % mline)
fact("pla_yield", mrow.group(2), "ce-cad/cecad/fits.py:%d" % mline)
fact("pla_E", mrow.group(3), "ce-cad/cecad/fits.py:%d" % mline)
fact("pla_src", "ce-cad/cecad/fits.py:%d" % mline, "the file itself")

# ---- FEA: the governing case and the material sweep -------------------------
res = MX.get("results", [])
ank = [r for r in res if r.get("part") == "microduck-ankle-left" and r.get("material") == "PLA" and r.get("sf") is not None]
land = [r for r in ank if r.get("case") == "landing"]
stand = [r for r in ank if r.get("case") == "standing"]
fact("ankle_sf_pla", "%.4f" % land[0]["sf"] if land else "CANNOT DETERMINE",
     "out/stress/matrix.json results[microduck-ankle-left/landing/PLA].sf")
fact("ankle_sf_standing", "%.4f" % stand[0]["sf"] if stand else "CANNOT DETERMINE",
     "out/stress/matrix.json results[microduck-ankle-left/standing/PLA].sf")
sweep = [s for s in (MX.get("material_sweep") or []) if s.get("sf") is not None]
best = max(sweep, key=lambda s: s["sf"]) if sweep else None
fact("ankle_best_material", best["material"] if best else "CANNOT DETERMINE", "out/stress/matrix.json material_sweep")
fact("ankle_best_sf", "%.4f" % best["sf"] if best else "CANNOT DETERMINE", "out/stress/matrix.json material_sweep")
fact("load_basis", (MX.get("load_basis") or "CANNOT DETERMINE").strip().rstrip("."), "out/stress/matrix.json load_basis")

# ---- print: totals, shells, supports, TPU -----------------------------------
parts = SL.get("parts", [])
gt = SL.get("grand_total", {})
fact("print_slugs", gt.get("printed_slugs"), "out/print/slice.json grand_total")
fact("print_pieces", gt.get("pieces"), "out/print/slice.json grand_total")
fact("print_grams", "%.2f" % gt.get("grams", 0), "out/print/slice.json grand_total")
fact("print_hours", "%.2f" % gt.get("hours", 0), "out/print/slice.json grand_total")
fact("support_count", sum(1 for p in parts if p.get("slicer_warning")), "out/print/slice.json slicer_warning per part")
tpu = (SL.get("totals_per_material") or {}).get("TPU", {})
fact("tpu_pieces", tpu.get("pieces"), "out/print/slice.json totals_per_material.TPU")
fact("tpu_grams", "%.2f" % tpu.get("grams", 0), "out/print/slice.json totals_per_material.TPU")

SHELLS = ["microduck-trunk-shell-left", "microduck-trunk-shell-right", "microduck-top-head-shell",
          "microduck-bottom-head-shell", "microduck-face-part"]
sh = [p for p in parts if p["slug"] in SHELLS]
missing_shells = [s for s in SHELLS if s not in {p["slug"] for p in parts}]
if missing_shells:
    raise SystemExit("gen_questions: shell slug(s) not in out/print/slice.json: %s" % missing_shells)
sh_g = sum(p.get("grams_total") or 0 for p in sh)
sh_s = sum(p.get("seconds_total") or 0 for p in sh)
fact("shell_grams", "%.2f" % sh_g, "out/print/slice.json, sum over the 5 shell slugs")
fact("shell_hours", "%.2f" % (sh_s / 3600.0), "out/print/slice.json, sum over the 5 shell slugs")
fact("shell_share_pct", "%.1f" % (100.0 * (sh_s / 3600.0) / gt.get("hours", 1)), "shell hours / grand_total hours")
head = [p for p in parts if p["slug"] == "microduck-top-head-shell"]
fact("head_bbox", " × ".join("%.3f" % v for v in head[0]["bbox_mm"]) if head else "CANNOT DETERMINE",
     "out/print/slice.json[microduck-top-head-shell].bbox_mm (measured off the STL)")

# ---- the sheets' own tolerance basis ----------------------------------------
det = json.dumps(SHEET, ensure_ascii=False)
m = re.search(r"TOLERANCE BASIS, OUTSOURCED: (.*?)Apply the route", det)
fact("tol_outsourced", (m.group(1).strip().rstrip(".") if m else "CANNOT DETERMINE"),
     "out/drawings/microduck-shin/result.json — the sheet's own note")

# ---- profile ----------------------------------------------------------------
pv = {k: (v, why) for k, v, why in (PB.get("profile") or {}).get("values", [])}
walls = pv.get("wall_loops", ("?", ""))
fact("profile_walls", "%s wall loops at a %s layer" % (walls[0], pv.get("layer_height", ("?",))[0]),
     "tools/data/playbook.json profile (BambuStudio profile, inherit chain resolved)")
wf = re.search(r"([\d.]+) mm wall floor", walls[1] or "")
fact("wall_floor", wf.group(1) if wf else "CANNOT DETERMINE", "tools/data/playbook.json profile.wall_loops note")
rates = PB.get("rates", {})
fact("labour_rate", rates.get("labour_usd_per_hour"), "tools/data/playbook.json rates.labour_usd_per_hour (%s)" % rates.get("labour_src"))
fact("tool_floor", "%.0f" % rates["tool_usd"]["floor"], "tools/data/playbook.json rates.tool_usd")
fact("tool_alu", "%.0f-%.0f USD" % (rates["tool_usd"]["alu_low"], rates["tool_usd"]["alu_high"]), "tools/data/playbook.json rates.tool_usd")
fact("mould_piece", "%.2f-%.2f" % (rates["mould_piece_usd"]["low"], rates["mould_piece_usd"]["high"]), "tools/data/playbook.json rates.mould_piece_usd")
fact("plate_pla", rates["plate_pieces"]["PLA"], "tools/data/playbook.json rates.plate_pieces")
fact("plate_tpu", rates["plate_pieces"]["TPU"], "tools/data/playbook.json rates.plate_pieces")
fact("stations", len(PB.get("stations", [])), "tools/data/playbook.json stations")
fact("station_steps", sum(len(s.get("steps", [])) for s in PB.get("stations", [])), "tools/data/playbook.json stations[].steps")

# ---- fasteners and bearings, out of SPEC.md and the sourcing lines ----------
mm = re.search(r"Ø2\.2 clearance ×(\d+), Ø4\.4 c'bore ×(\d+), Ø1\.6 tap ×(\d+), Ø2\.7/2\.8 ×(\d+)", SPEC)
if not mm:
    raise SystemExit("gen_questions: hole census not found in SPEC.md")
counts = [int(x) for x in mm.groups()]
fact("holes_total", sum(counts), "SPEC.md hole census (%s)" % mm.group(0))
fact("hole_breakdown", mm.group(0), "SPEC.md hole census")
mb = re.search(r"bearings (\d+)×(\d+)×(\d+) \(×(\d+)\) and (\d+)×(\d+)×(\d+) \(×(\d+)\)", SPEC)
fact("bearings_22", mb.group(4) if mb else "CANNOT DETERMINE", "SPEC.md bearing census")
fact("bearings_15", mb.group(8) if mb else "CANNOT DETERMINE", "SPEC.md bearing census")
lines = {l["id"]: l for l in SRC.get("lines", [])}
fact("insert_qty", lines.get("B18c", {}).get("qty_per_robot"), "spec/sourcing.json B18c qty_per_robot")
fact("screw_qty", (lines.get("B18a", {}).get("qty_per_robot") or 0) + (lines.get("B18b", {}).get("qty_per_robot") or 0),
     "spec/sourcing.json B18a + B18b qty_per_robot")

# ---- boards -----------------------------------------------------------------
boards = PCB.get("boards", [])
fact("board_list", "; ".join("%s %s mm, %s layer" % (b.get("name"), " × ".join(str(x) for x in b.get("outline_mm") or []), b.get("layers")) for b in boards),
     "electronics/pcb-package.json boards[].outline_mm")
ban = [b for b in boards if "banana" in (b.get("slug") or b.get("dir") or "")]
fact("banana_size", " × ".join(str(x) for x in (ban[0].get("outline_mm") or [])) if ban else "CANNOT DETERMINE",
     "electronics/pcb-package.json boards[banana-contact].outline_mm")
hat = [b for b in boards if "robot-hat" in (b.get("dir") or "")]
fact("our_hat", " × ".join(str(x) for x in (hat[0].get("outline_mm") or [])) if hat else "CANNOT DETERMINE",
     "electronics/pcb-package.json boards[robot-hat].outline_mm")
hatrow = [r for r in RD.get("rows", []) if r.get("class") == "pcb" and r.get("id") == "robot-hat"]
ph = re.search(r"published outline is ([\d.]+ x [\d.]+ x [\d.]+)", hatrow[0].get("missing", "")) if hatrow else None
fact("pollen_hat", ph.group(1).replace(" x ", " × ") if ph else "CANNOT DETERMINE",
     "out/factory/readiness.json robot-hat row (measured from Pollen's published Apache-2.0 package)")
ven = (PCB.get("fab_quotes") or {}).get("vendors") or []
fact("pcb_capability", ("%s, %s" % (ven[0].get("vendor"), (ven[0].get("spec") or "")[:120])) if ven else "CANNOT DETERMINE",
     "electronics/pcb-package.json fab_quotes.vendors[0]")

# ---- counts off the readiness audit and the pack ----------------------------
pl = (RD.get("summary") or {}).get("print_licence") or {}
fact("ours_parts", pl.get("ours"), "out/factory/readiness.json summary.print_licence.ours")
fact("vendor_parts", pl.get("vendor_mesh_stls"), "out/factory/readiness.json summary.print_licence.vendor_mesh_stls")
fact("sheet_count", ((RD.get("summary") or {}).get("sheets_graded") or {}).get("sheets"), "out/factory/readiness.json summary.sheets_graded")
fact("bom_lines", len((PK.get("bom") or {}).get("lines") or []), "out/factory/pack.json bom.lines")
fact("usd_lines", (PK.get("bom") or {}).get("usd_lines"), "out/factory/pack.json bom.usd_lines")
fact("eol_gates", PK.get("eol_gates"), "out/factory/pack.json eol_gates (TEST-PLAN.html Table 13)")
fact("not_ready_rows", len(PK.get("not_ready") or []), "out/factory/pack.json not_ready")
jigs = JG.get("jigs") if isinstance(JG, dict) else None
if jigs is None:
    jigs = [d for d in os.listdir(os.path.join(ROOT, "out", "jigs")) if d.startswith("microduck-jig-")]
fact("jig_count", len(jigs), "out/jigs/ — one folder per jig")
fact("dxf_count", len(glob.glob(os.path.join(ROOT, "out", "drawings", "*", "*.dxf"))), "out/drawings/*/*.dxf")

# ---- fill ---------------------------------------------------------------------
_TOK = re.compile(r"\{([a-z0-9_]+)\}")


def fill(text):
    def sub(m):
        k = m.group(1)
        if k not in F:
            raise SystemExit("gen_questions: unresolved token {%s} — every number on the page must come from a file" % k)
        return str(F[k])
    return _TOK.sub(sub, str(text))


sections = []
for s in D["sections"]:
    qs = []
    for q in s["questions"]:
        qq = dict(q)
        for k in ("ask_en", "ask_zh", "why_en", "why_zh", "ours_en", "ours_zh"):
            if k in qq:
                qq[k] = fill(qq[k])
        qq["branches_en"] = [[fill(a), fill(b)] for a, b in q.get("branches_en", [])]
        qq["branches_zh"] = [[fill(a), fill(b)] for a, b in q.get("branches_zh", [])]
        qs.append(qq)
    sections.append({**{k: v for k, v in s.items() if k != "questions"},
                     "lede_en": fill(s["lede_en"]), "lede_zh": fill(s["lede_zh"]), "questions": qs})

n_q = sum(len(s["questions"]) for s in sections)
out = {"$doc": "out/factory/questions.json — the questions for the factory, generated by tools/gen_questions.py. Every {token} in tools/data/factory_questions.json was filled from the file named in `facts`.",
       "generated": NOW, "doc": D["doc"], "how_to_answer": D["how_to_answer"],
       "questions_total": n_q, "sections": sections,
       "facts": {k: {"value": F[k], "source": WHY[k]} for k in sorted(F)}}
os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)

# ------------------------------------------------------------------------ HTML
A = []


def th(en, zh):
    return '<th>' + E(en) + '<br><span class="zh">' + E(zh) + '</span></th>'


def cols(*pct):
    return "<colgroup>" + "".join('<col style="width:%s%%">' % w for w in pct) + "</colgroup>"


d = D["doc"]
A.append('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">')
A.append('<title>%s — %s</title>' % (E(d["title"]), E(d["title_zh"])))
A.append('<link rel="stylesheet" href="tools/doc.css">')
A.append('<style>'
         '.zh{font-family:var(--sans);font-size:12px;color:var(--ink-2);display:block}'
         'table{border-collapse:collapse;width:100%;table-layout:fixed;font-size:12.5px;margin:8px 0 18px;overflow-wrap:anywhere}'
         'th{white-space:normal !important;overflow-wrap:break-word;word-break:normal;padding:5px 6px;background:var(--head);'
         'font-family:var(--sans);font-size:12px;text-align:left;vertical-align:top;border-bottom:1px solid var(--hair)}'
         'td{border-bottom:1px solid var(--hair);padding:5px 6px;text-align:left;vertical-align:top}'
         'td.m{font-family:var(--mono);font-size:11.5px;word-break:break-all}'
         '.q{border-left:3px solid var(--accent);padding:2px 0 2px 14px;margin:22px 0}'
         '.q h4{font-size:15.5px;margin:0 0 2px;font-family:var(--serif)}'
         '.q .qid{font-family:var(--mono);font-size:11.5px;color:var(--accent);padding-right:8px}'
         '.tag{font-family:var(--sans);font-size:10.5px;letter-spacing:.06em;text-transform:uppercase;'
         'border:1px solid var(--hair);padding:1px 6px;margin-right:6px;color:var(--ink-2)}'
         '.tag.blocking{color:var(--no);border-color:var(--no)}.tag.high{color:var(--cd);border-color:var(--cd)}'
         '.ours{background:var(--card);border:1px solid var(--hair);padding:8px 12px;margin:8px 0;font-size:13.5px}'
         '.ans{width:100%;border-top:1px solid var(--hair)}'
         '.front{border:2px solid var(--accent);padding:12px 16px;margin:18px 0}.front h2{margin:0 0 6px;border:none;font-size:20px}'
         '</style>')
A.append('</head>\n<body>\n<div class="wrap">')
A.append('<p class="backlink"><a href="INDEX.html">← Document index</a> · <a href="FACTORY-PACK.html">Factory pack</a> · <a href="WORK-BREAKDOWN.html">Work breakdown</a></p>')
A.append('<header class="hero"><p class="eyebrow">Microduck · factory pack · 工厂交付包</p>')
A.append('<h1>%s <span class="zh" style="font-size:22px;display:inline">%s</span></h1>' % (E(d["title"]), E(d["title_zh"])))
A.append('<p class="sub">%s</p><p class="sub zh">%s</p>' % (E(d["sub"]), E(d["sub_zh"])))
A.append('<div class="rev"><span>%s · Rev %s</span><span>generated %s</span><span>%d questions</span><span>tools/gen_questions.py</span></div></header>'
         % (d["id"], d["rev"], E(NOW), n_q))

A.append('<div class="front"><h2>How to answer · 如何作答</h2>')
A.append('<p>%s</p><p class="zh" style="font-size:13px">%s</p>' % (E(D["how_to_answer"]["en"]), E(D["how_to_answer"]["zh"])))
A.append('<div class="statbar">')
prio = {}
need = {}
for s in sections:
    for q in s["questions"]:
        prio[q["priority"]] = prio.get(q["priority"], 0) + 1
        need[q["need"]] = need.get(q["need"], 0) + 1
for b, en, zh in [(str(n_q), "questions", "问题总数"),
                  (str(len(sections)), "sections", "章节"),
                  (str(prio.get("blocking", 0)), "blocking us today", "当前阻塞项"),
                  (str(need.get("coupon", 0) + need.get("datasheet", 0)), "need a measurement or a datasheet", "需实测或数据表"),
                  (str(need.get("quote", 0)), "need a quotation", "需报价"),
                  (str(need.get("decision", 0)), "need your judgement", "需贵方判断")]:
    A.append('<div class="stat"><b>%s</b><span>%s<br>%s</span></div>' % (E(b), E(en), E(zh)))
A.append('</div></div>')

A.append('<nav class="toc">')
for s in sections:
    A.append('<a href="#s%s">%s %s</a>' % (s["n"], s["n"], E(s["title_en"].split("—")[0].strip())))
A.append('</nav>')

for s in sections:
    A.append('<section id="s%s"><h2><span class="n">%s</span>%s</h2>' % (s["n"], s["n"], E(s["title_en"])))
    A.append('<p class="zh" style="font-size:14px;margin:-6px 0 8px">%s</p>' % E(s["title_zh"]))
    A.append('<p class="lede">%s</p>' % re.sub(r"&lt;b&gt;(.*?)&lt;/b&gt;", r"<b>\1</b>", E(s["lede_en"])))
    A.append('<p class="lede zh">%s</p>' % re.sub(r"&lt;b&gt;(.*?)&lt;/b&gt;", r"<b>\1</b>", E(s["lede_zh"])))
    for q in s["questions"]:
        A.append('<div class="q">')
        A.append('<h4><span class="qid">%s</span>%s</h4>' % (E(q["id"]), E(q["ask_en"])))
        A.append('<p class="zh" style="font-size:13px;margin:2px 0 6px">%s</p>' % E(q["ask_zh"]))
        A.append('<p><span class="tag %s">%s</span><span class="tag">%s</span></p>'
                 % (q["priority"], E(D["priority"][q["priority"]]["en"]), E(D["need"][q["need"]]["en"])))
        A.append('<div class="ours"><b>Where we stand · 我方现状.</b> %s<br><span class="zh">%s</span>'
                 '<br><span class="mono" style="font-size:10.5px">source: %s</span></div>'
                 % (re.sub(r"&lt;b&gt;(.*?)&lt;/b&gt;", r"<b>\1</b>", E(q["ours_en"])),
                    re.sub(r"&lt;b&gt;(.*?)&lt;/b&gt;", r"<b>\1</b>", E(q["ours_zh"])), E(q["source"])))
        A.append('<table class="ans">' + cols(34, 66) + '<tr>' + th("If your answer is", "若贵方答复为")
                 + th("then we do this", "则我方将") + '</tr>')
        for i, (iff, then) in enumerate(q["branches_en"]):
            zh = q["branches_zh"][i] if i < len(q["branches_zh"]) else ["", ""]
            A.append('<tr><td>%s<br><span class="zh">%s</span></td><td>%s<br><span class="zh">%s</span></td></tr>'
                     % (E(iff), E(zh[0]), E(then), E(zh[1])))
        A.append('</table></div>')
    A.append('</section>')

A.append('<section id="facts"><h2><span class="n">%d</span>Where every number in this document came from <span class="zh" style="display:inline;font-size:15px">本文件中每个数字的出处</span></h2>' % (len(sections) + 1))
A.append('<p class="lede">The prose of this document is written by hand; the numbers in it are not. Each token below was read out of the file named beside it at generation time, so a reader can check any figure we quote about ourselves.</p>')
A.append('<p class="lede zh">本文件的文字由人撰写，数字则不是。下列每个变量均在生成时从右侧文件中读取，读者可核对我方引用的任何自有数据。</p>')
A.append('<table>' + cols(18, 40, 42) + '<tr>' + th("Token", "变量") + th("Value used", "所用数值") + th("Read from", "读取自") + '</tr>')
for k in sorted(F):
    A.append('<tr><td class="m">{%s}</td><td>%s</td><td class="m">%s</td></tr>' % (E(k), E(str(F[k])[:220]), E(WHY[k])))
A.append('</table></section>')

A.append('<footer class="foot"><p>Generated by <code>tools/gen_questions.py</code> from <code>tools/data/factory_questions.json</code> (prose) and the measurement files listed in the table above. %d questions in %d sections. An unresolved token is a hard error in the generator, so no number on this page was typed.</p>'
         '<p class="zh">本页由 tools/gen_questions.py 从 tools/data/factory_questions.json（文字）与上表所列实测文件生成，共 %d 个问题、%d 个章节。生成器对未解析变量直接报错，因此页面上没有任何手工填写的数字。</p></footer>'
         % (n_q, len(sections), n_q, len(sections)))
A.append('</div></body></html>')

with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write("\n".join(A))
print("wrote %s (%d B) and %s — %d questions in %d sections, %d facts filled"
      % (OUT_HTML, os.path.getsize(OUT_HTML), OUT_JSON, n_q, len(sections), len(F)))
