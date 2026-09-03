#!/usr/bin/env python3
"""gen_licence.py — render LICENCE-POSITION.html from out/factory/licence.json.

The data file holds every licence FACT (URL, verbatim quote, fetch time, sha256
of the archived bytes). This generator adds the checks that must be LIVE, because
they are about this repository rather than about the web:

  * the census of ce-parts/*/component.json licence strings (how many assert a
    CC version Pollen never wrote; how many of our own rebuilds carry no licence
    field at all);
  * whether the repo has a LICENSE file of its own;
  * whether the README quote still sits at the cited line in both local mirrors;
  * whether every archived evidence file still hashes to the value recorded in
    licence.json (a page that is quoted must be the page that was archived).

Every number on the page is therefore either a quoted fact with a source or a
measurement taken at generation time. The page is bilingual (English + Simplified
Chinese) in its summary and every table header, because the reader is a factory.

Run:  python3 tools/gen_licence.py            (system python3 is enough: stdlib only)
Owns: LICENCE-POSITION.html only. Reads everything, writes nothing else.
"""
import datetime as _dt
import glob
import hashlib
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "out", "factory", "licence.json")
EVID = os.path.join(REPO, "out", "factory", "licence-evidence")
OUT = os.path.join(REPO, "LICENCE-POSITION.html")


def e(s):
    return html.escape("" if s is None else str(s), quote=True)


def chip(verdict):
    v = str(verdict)
    cls = "pass" if v.startswith("PASS") else ("rail" if v.startswith("FAIL") else "cd")
    return '<span class="chip %s">%s</span>' % (cls, e(v))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------- live checks

def census_component_json():
    """Read every ce-parts/*/component.json and count what it says about the licence."""
    rows = []
    for fp in sorted(glob.glob(os.path.join(REPO, "ce-parts", "*", "component.json"))):
        try:
            rec = json.load(open(fp)).get("record", {})
        except Exception as ex:  # a broken file is a finding, not a crash
            rows.append({"slug": os.path.basename(os.path.dirname(fp)), "error": str(ex)})
            continue
        text = " ".join(str(rec.get(k, "")) for k in ("licence", "license", "origin_why", "why"))
        rows.append({
            "slug": rec.get("slug") or os.path.basename(os.path.dirname(fp)),
            "origin": rec.get("origin"),
            "licence_field": rec.get("licence") or rec.get("license"),
            "says_4_0": bool(re.search(r"BY-SA-NC\s*4\.0|BY-NC-SA\s*4\.0", text)),
            "says_no_version": "version not stated" in text,
            "mentions_cc": bool(re.search(r"CC BY|Creative Commons", text)),
        })
    by_origin = {}
    for r in rows:
        by_origin[r.get("origin")] = by_origin.get(r.get("origin"), 0) + 1
    generated = [r for r in rows if r.get("origin") == "generated"]
    return {
        "n": len(rows),
        "by_origin": by_origin,
        "assert_4_0": sorted(r["slug"] for r in rows if r.get("says_4_0")),
        "no_version": sorted(r["slug"] for r in rows if r.get("says_no_version")),
        "generated_total": len(generated),
        "generated_with_licence": sorted(r["slug"] for r in generated if r.get("licence_field")),
        "generated_without_licence": sorted(r["slug"] for r in generated if not r.get("licence_field")),
        "vendor_cc_folders": sorted(r["slug"] for r in rows if r.get("origin") == "vendor" and r.get("mentions_cc")),
    }


def check_readme_lines():
    """The quote in F1 must still be at the cited line of both local mirrors."""
    targets = [
        ("reference/pollen-microduck-rl-develop/microduck_rl_README.md", 261,
         "3D model files are licensed under Creative Commons BY-SA-NC."),
        ("reference/pollen-microduck-rl/microduck_rl_README.md", 196,
         "3D model files are licensed under Creative Commons BY-SA-NC."),
        ("research/raw/microduck_rl_main_README.md", 191,
         "Hardware design files are licensed under Creative Commons BY-SA-NC."),
        ("out/factory/licence-evidence/microduck_rl_develop_README.md", 261,
         "3D model files are licensed under Creative Commons BY-SA-NC."),
        ("out/factory/licence-evidence/microduck_rl_main_README.md", 191,
         "Hardware design files are licensed under Creative Commons BY-SA-NC."),
    ]
    out = []
    for rel, line, want in targets:
        fp = os.path.join(REPO, rel)
        if not os.path.exists(fp):
            out.append({"file": rel, "line": line, "verdict": "FAIL", "why": "file missing"})
            continue
        lines = open(fp, encoding="utf-8", errors="replace").read().split("\n")
        got = lines[line - 1].strip() if line <= len(lines) else ""
        if got == want:
            out.append({"file": rel, "line": line, "verdict": "PASS", "why": "line %d reads exactly: %s" % (line, want)})
        else:
            hit = [i + 1 for i, l in enumerate(lines) if l.strip() == want]
            out.append({"file": rel, "line": line, "verdict": "FAIL",
                        "why": "line %d reads %r; the sentence is at line(s) %s" % (line, got, hit or "none")})
    # the version check: does ANY line of any mirror name a CC version?
    for rel, _l, _w in targets[:3]:
        fp = os.path.join(REPO, rel)
        if os.path.exists(fp):
            txt = open(fp, encoding="utf-8", errors="replace").read()
            m = re.findall(r"Creative Commons[^\n]*", txt)
            has_ver = any(re.search(r"\b[234]\.0\b", s) for s in m)
            out.append({"file": rel, "line": "-", "verdict": "FAIL" if has_ver else "PASS",
                        "why": ("a CC version IS named: %s" % m) if has_ver
                        else "no version number on any 'Creative Commons' line (%d line(s))" % len(m)})
    return out


def verify_evidence(data):
    out = []
    for ev in data.get("evidence_files", []):
        fp = os.path.join(EVID, ev["file"])
        if not os.path.exists(fp):
            out.append(dict(ev, verdict="FAIL", why="archived file missing", size=None, measured=None))
            continue
        h = sha256(fp)
        size = os.path.getsize(fp)
        if ev.get("sha256") is None:
            out.append(dict(ev, verdict="PASS", why="archived; no hash was recorded at fetch time, this is the first", size=size, measured=h))
        elif h == ev["sha256"]:
            out.append(dict(ev, verdict="PASS", why="sha256 matches the value recorded at fetch time", size=size, measured=h))
        else:
            out.append(dict(ev, verdict="FAIL", why="sha256 differs from the recorded value: the archived bytes changed", size=size, measured=h))
    return out


def repo_licence_file():
    # Exact licence-file names only. A bare LICENCE* glob matched LICENCE-POSITION.html
    # (this page) and reported a false PASS — caught by reading the screenshot back.
    names = ["LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE", "LICENCE.md", "LICENCE.txt", "COPYING"]
    hits = [n for n in names if os.path.isfile(os.path.join(REPO, n))]
    return {"present": bool(hits), "files": hits, "looked_for": names}


# ---------------------------------------------------------------- rendering

def th(en, zh):
    return '<th>%s<br><span class="zh">%s</span></th>' % (e(en), e(zh))


def h2(n, en, zh, anchor):
    return '<section id="%s"><h2><span class="n">%s</span>%s <span class="zh">%s</span></h2>' % (anchor, n, e(en), e(zh))


def para_list(items):
    return "<ul>" + "".join("<li>%s</li>" % e(x) for x in items) + "</ul>"


def quote_block(q):
    return '<blockquote class="q">%s</blockquote>' % e(q).replace("\n", "<br>")


def render(data, census, readme_checks, evidence, lic_file, now):
    o = []
    A = o.append
    facts = data["facts"]
    qs = data["questions"]
    cds = data["cannot_determine"]

    n_fact_pass = sum(1 for f in facts if str(f.get("verdict", "")).startswith("PASS"))
    n_fact_fail = sum(1 for f in facts if str(f.get("verdict", "")).startswith("FAIL"))
    n_fact_cd = len(facts) - n_fact_pass - n_fact_fail
    n_ev_pass = sum(1 for x in evidence if x["verdict"] == "PASS")
    n_readme_pass = sum(1 for x in readme_checks if x["verdict"] == "PASS")

    A('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">')
    A('<meta name="viewport" content="width=device-width, initial-scale=1">')
    A('<title>Licence and origin position · 许可证与来源立场</title>')
    A('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">')
    A('<link rel="stylesheet" href="tools/doc.css">')
    A('<style>\n'
      '  .zh{font-family:var(--sans);font-weight:400;color:var(--ink-2);font-size:.86em}\n'
      '  h2 .zh{font-size:.72em;margin-left:.5em}\n'
      '  th .zh{display:block;font-size:10.5px;letter-spacing:0;text-transform:none;color:var(--ink-2)}\n'
      '  blockquote.q{margin:8px 0 10px;padding:8px 14px;border-left:3px solid var(--accent);background:var(--card);'
      'font-family:var(--serif);font-size:14px;line-height:1.5}\n'
      '  .fact{border-top:1px solid var(--hair);padding:14px 0 8px}\n'
      '  .fact h3{margin:0 0 4px;font-size:16px}\n'
      '  .fact h3 .id{font-family:var(--mono);color:var(--accent);margin-right:8px}\n'
      '  .src{font-family:var(--mono);font-size:11.5px;color:var(--ink-2);word-break:break-all}\n'
      '  .src a{color:var(--accent)}\n'
      '  .fact ul{margin:6px 0 6px 18px;font-size:13.5px}\n'
      '  .fact ul li{margin:3px 0}\n'
      '  .headline{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:14px 0}\n'
      '  .headline p{margin:0;font-size:15px;line-height:1.55}\n'
      '  .headline p.zh{font-size:14.5px;color:var(--ink)}\n'
      '  @media(max-width:800px){.headline{grid-template-columns:1fr}}\n'
      '  table.data td{vertical-align:top;font-size:13px}\n'
      '  table.data td.v{white-space:nowrap}\n'
      '  table.data td.v .chip.long{white-space:normal;display:inline-block;max-width:150px;line-height:1.35}\n'
      '  table#q4 td.v{white-space:normal;min-width:120px}\n'
      '  table#q4{table-layout:fixed}\n'
      '  table#ev{table-layout:fixed;width:100%%;min-width:0} table#ev td,table#ev th{overflow-wrap:anywhere;word-break:break-all;white-space:normal}\n'
      '  table#repo{table-layout:fixed;width:100%%;min-width:0} table#repo td{overflow-wrap:anywhere;white-space:normal}\n'
      '  .instr{display:grid;grid-template-columns:1fr 1fr;gap:18px}\n'
      '  .instr ol{margin:0 0 0 20px;font-size:13.5px}\n'
      '  .instr ol li{margin:5px 0}\n'
      '  @media(max-width:800px){.instr{grid-template-columns:1fr}}\n'
      '  .num{font-family:var(--mono);text-align:right}\n'
      '</style>\n</head>\n<body>\n<div class="wrap">')
    A('<p class="backlink"><a href="FACTORY-PACK.html">← Factory pack</a> · <a href="RELEASE.html">Release dossier</a></p>')
    A('<header class="hero">')
    A('  <p class="eyebrow">Microduck · factory handoff pack · 工厂交接资料包</p>')
    A('  <h1>Licence and origin position <span class="zh">许可证与来源立场</span></h1>')
    A('  <p class="sub">What Pollen Robotics published, under which terms, what that plainly allows a factory to do, '
      'and what is ours. Every fact carries a URL, a verbatim quote, a fetch time and a hash of the archived bytes. '
      'This is the licence text and its plain reading; it is not legal advice. '
      '<span class="zh">本页记录 Pollen Robotics 发布了什么、采用何种条款、字面上允许工厂做什么、哪些属于我们。'
      '每条事实都附有网址、原文引用、抓取时间和存档字节的哈希值。本页是许可证原文及其字面解读，不构成法律意见。</span></p>')
    A('  <div class="rev"><span>MD-LIC-001 · Rev A</span><span>%s</span>'
      '<span>generator: tools/gen_licence.py</span><span>data: out/factory/licence.json</span>'
      '<span>facts fetched: %s</span></div>' % (e(now), e(data["measured_at_utc"])))
    A('</header>')

    A('<div class="statbar">')
    A('  <div class="stat"><b>%d</b><span>facts · 事实</span></div>' % len(facts))
    A('  <div class="stat"><b>%d / %d / %d</b><span>PASS / FAIL / CD</span></div>' % (n_fact_pass, n_fact_fail, n_fact_cd))
    A('  <div class="stat"><b>%d</b><span>questions answered · 已答问题</span></div>' % len(qs))
    A('  <div class="stat"><b>%d</b><span>CANNOT DETERMINE · 无法确定</span></div>' % len(cds))
    A('  <div class="stat"><b>%d / %d</b><span>evidence hashes PASS · 证据哈希</span></div>' % (n_ev_pass, len(evidence)))
    A('  <div class="stat"><b>%d / %d</b><span>README line checks PASS</span></div>' % (n_readme_pass, len(readme_checks)))
    A('  <div class="stat"><b>%d</b><span>our folders asserting a CC version Pollen never wrote</span></div>' % len(census["assert_4_0"]))
    A('</div>')

    A('<nav class="toc"><a href="#headline">0 Position · 立场</a><a href="#questions">1 Four questions · 四个问题</a>'
      '<a href="#facts">2 Facts · 事实</a><a href="#ours">3 Ours vs upstream · 我方与上游</a>'
      '<a href="#cd">4 CANNOT DETERMINE · 无法确定</a><a href="#factory">5 To the factory · 致工厂</a>'
      '<a href="#repo">6 Our own metadata · 我方元数据</a><a href="#evidence">7 Evidence · 证据</a><a href="#method">8 Method · 方法</a></nav>')

    # 0 headline
    A(h2(0, "The position, in one paragraph", "立场（一段话）", "headline"))
    A('<div class="headline"><p>%s</p><p class="zh">%s</p></div>' % (e(data["headline"]["en"]), e(data["headline"]["zh"])))
    A('<div class="note"><b>Read this before cutting tooling.</b> Engineering and validation units may be built now. '
      'Production units for sale may not, on the licence as published. The two things that change that answer are '
      'named in section 4 (Q-A, Q-B) and neither is a task for the factory. '
      '<span class="zh">开模前先读本页。工程样机与验证样机现在可以制造。按已发布的许可证，用于销售的量产整机不可以。'
      '能改变该答案的两件事列于第 4 节（Q-A、Q-B），都不是工厂的任务。</span></div>')
    A('</section>')

    # 1 questions
    A(h2(1, "The four questions a factory asks", "工厂会问的四个问题", "questions"))
    A('<div class="tablewrap"><table class="data" id="q4"><colgroup><col style="width:5%%"><col style="width:20%%"><col style="width:16%%"><col style="width:41%%"><col style="width:18%%"></colgroup><thead><tr>%s%s%s%s%s</tr></thead><tbody>'
      % (th("#", "编号"), th("Question", "问题"), th("Verdict", "结论"), th("Plain reading of the licence", "许可证字面解读"), th("What settles it", "如何确定")))
    for q in qs:
        A('<tr><td class="v"><code>%s</code></td><td><b>%s</b><br><span class="zh">%s</span></td><td class="v">%s</td><td>%s%s%s</td><td>%s</td></tr>'
          % (e(q["id"]), e(q["q_en"]), e(q["q_zh"]), chip(q["verdict"]).replace('class="chip ', 'class="chip long '), e(q.get("plain_reading", "")),
             ('<br><br><b>May do now:</b> %s' % e(q["what_the_factory_may_do_now"])) if q.get("what_the_factory_may_do_now") else "",
             ('<br><b>May not do now:</b> %s' % e(q["what_the_factory_may_not_do_now"])) if q.get("what_the_factory_may_not_do_now") else "",
             e(q.get("settles_it", "see section 3"))))
    A('</tbody></table></div>')
    A('</section>')

    # 2 facts
    A(h2(2, "The facts, each with its quote, URL and fetch time", "事实——各附原文引用、网址与抓取时间", "facts"))
    A('<p class="lede">Verdict here means: is the FACT established? PASS = quote, URL, time and hash agree. '
      'CANNOT DETERMINE = the fact needs a search nobody has run. FAIL = our own record is wrong. '
      '<span class="zh">此处的结论指该事实是否已确立：PASS＝引用、网址、时间与哈希一致；CANNOT DETERMINE＝尚需未进行的检索；FAIL＝我方记录有误。</span></p>')
    for f in facts:
        A('<div class="fact" id="%s"><h3><span class="id">%s</span>%s %s <span class="zh">%s</span></h3>'
          % (e(f["id"]), e(f["id"]), chip(f.get("verdict", "CANNOT DETERMINE")), e(f["topic"]), e(f.get("topic_zh", ""))))
        if f.get("verdict_note"):
            A('<p class="lede">%s</p>' % e(f["verdict_note"]))
        if f.get("source_url"):
            A('<p class="src">source: <a href="%s">%s</a>%s · fetched %s%s</p>'
              % (e(f["source_url"]), e(f["source_url"]),
                 (' · page <a href="%s">%s</a>' % (e(f["page_url"]), e(f["page_url"]))) if f.get("page_url") else "",
                 e(f.get("fetched_utc", "-")),
                 (' · sha256 <code>%s</code> · archived %s' % (e(f["sha256"][:16]) + "…", e(f["archived"]))) if f.get("sha256") else ""))
        if f.get("page_note"):
            A('<p class="lede">%s</p>' % e(f["page_note"]))
        if f.get("quote"):
            A(quote_block(f["quote"]))
            if f.get("quote_lines"):
                A('<p class="src">%s</p>' % e(f["quote_lines"]))
        if f.get("readme_quote"):
            A('<p class="src">README: <a href="%s">%s</a> · sha256 %s… · %s</p>' % (e(f["readme_url"]), e(f["readme_url"]), e(f["readme_sha256"][:16]), e(f.get("readme_lines", ""))))
            A(quote_block(f["readme_quote"]))
        if f.get("licence_file_sha256"):
            A('<p class="src">LICENSE file: %s</p>' % e(f["licence_file_sha256"]))
        if f.get("fields"):
            A('<div class="tablewrap"><table class="data compact"><thead><tr>%s%s</tr></thead><tbody>' % (th("API field", "接口字段"), th("Value", "值")))
            for k, v in f["fields"].items():
                A('<tr><td><code>%s</code></td><td>%s</td></tr>' % (e(k), e(v)))
            A('</tbody></table></div>')
        if f.get("summary_quote_zh"):
            A('<p class="src">uploader description, verbatim (zh):</p>' + quote_block(f["summary_quote_zh"]))
            A('<p class="src">our translation (en):</p>' + quote_block(f["summary_quote_en"]))
        if f.get("version_caveat"):
            A('<div class="note">%s</div>' % e(f["version_caveat"]))
        if f.get("clauses"):
            A('<div class="tablewrap"><table class="data"><thead><tr>%s%s</tr></thead><tbody>' % (th("Clause", "条款"), th("Text, verbatim", "原文")))
            for c in f["clauses"]:
                A('<tr><td class="v"><code>%s</code>%s</td><td>%s</td></tr>'
                  % (e(c["ref"]), ('<br><a class="src" href="%s">deed</a>' % e(c["source_url"])) if c.get("source_url") else "", e(c["quote"])))
            A('</tbody></table></div>')
        if f.get("cc_faq_quote"):
            A('<p class="src">Creative Commons FAQ: <a href="%s">%s</a></p>' % (e(f["cc_faq_source"].split(" ,")[0]), e(f["cc_faq_source"])))
            A(quote_block(f["cc_faq_quote"]))
        if f.get("items"):
            A('<div class="tablewrap"><table class="data"><thead><tr>%s%s%s%s</tr></thead><tbody>'
              % (th("What", "对象"), th("Licence / statement", "许可证 / 声明"), th("Quote", "原文"), th("Source · fetched", "来源 · 抓取时间")))
            for it in f["items"]:
                src = it.get("source_url") or it.get("source") or ""
                srch = ('<a href="%s">%s</a>' % (e(src), e(src))) if src.startswith("http") else e(src)
                A('<tr><td>%s%s</td><td>%s</td><td>%s</td><td class="src">%s%s%s%s</td></tr>'
                  % (e(it.get("what", "")), ('<br><span class="zh">%s</span>' % e(it["byline"])) if it.get("byline") else "",
                     e(it.get("licence", "")), e(it.get("quote", "")) + (("<br><i>" + e(it["quote_also"]) + "</i>") if it.get("quote_also") else ""),
                     srch, (" · fetched " + e(it["fetched_utc"])) if it.get("fetched_utc") else "",
                     (" · sha256 " + e(it["sha256"][:16]) + "…") if it.get("sha256") else "",
                     ("<br>" + e(it["note"])) if it.get("note") else "" + (("<br>" + e(it["licence_file_sha256"])) if it.get("licence_file_sha256") else "")))
            A('</tbody></table></div>')
        if f.get("apache_conditions_quote"):
            A('<p class="src">%s</p>' % e(f["apache_quote_source"]))
            A(quote_block(f["apache_conditions_quote"]))
            A(quote_block(f["apache_trademark_quote"]))
        if f.get("price_table"):
            A('<div class="tablewrap"><table class="data"><thead><tr>%s%s%s%s</tr></thead><tbody>'
              % (th("Item", "商品"), th("USD", "美元"), th("EUR", "欧元"), th("Basis", "依据")))
            for p in f["price_table"]:
                A('<tr><td>%s</td><td class="num">%s</td><td class="num">%s</td><td>%s</td></tr>' % (e(p["item"]), e(p["usd"]), e(p["eur"]), e(p["basis"])))
            A('</tbody></table></div>')
        if f.get("checks"):
            A('<p class="lede">Checks this generator runs live (results in section 6):</p>' + para_list(f["checks"]))
            A('<p class="src">known at write time: %s</p>' % e(f["known_at_write_time"]))
        if f.get("reading"):
            A('<p class="lede"><b>Plain reading · 字面解读</b></p>' + para_list(f["reading"]))
        if f.get("settles_it"):
            A('<p class="lede"><b>What settles it · 如何确定:</b> %s</p>' % e(f["settles_it"]))
        A('</div>')
    A('</section>')

    # 3 ours vs upstream
    q4 = next(q for q in qs if q["id"] == "Q4")
    A(h2(3, "What is ours, what is upstream, under what terms", "哪些是我们的、哪些是上游的、各适用什么条款", "ours"))
    A('<p class="lede">%s %s</p>' % (chip(q4["verdict"]), e("Inventory first, then the terms. The one open item is the legal status of our parametric rebuilds (Q-B).")))
    A('<h3>3.1 Ours <span class="zh">我方资产</span></h3>')
    A('<div class="tablewrap"><table class="data"><thead><tr>%s%s%s</tr></thead><tbody>' % (th("Asset", "资产"), th("Origin", "来源"), th("Terms", "条款")))
    for r in q4["ours_table"]:
        A('<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (e(r["asset"]), e(r["origin"]), e(r["terms"])))
    A('</tbody></table></div>')
    A('<h3>3.2 Upstream <span class="zh">上游资产</span></h3>')
    A('<div class="tablewrap"><table class="data"><thead><tr>%s%s%s</tr></thead><tbody>' % (th("Asset", "资产"), th("Owner", "权利人"), th("Terms", "条款")))
    for r in q4["upstream_table"]:
        A('<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (e(r["asset"]), e(r["owner"]), e(r["terms"])))
    A('</tbody></table></div>')
    A('</section>')

    # 4 CD
    A(h2(4, "CANNOT DETERMINE — and exactly what settles each", "无法确定——以及各自如何确定", "cd"))
    A('<div class="tablewrap"><table class="data"><thead><tr>%s%s%s%s</tr></thead><tbody>'
      % (th("#", "编号"), th("Open question", "未决问题"), th("Who settles it, how", "由谁、如何确定"), th("Blocks", "阻塞项")))
    for c in cds:
        extra = ""
        if c.get("question_for_counsel"):
            extra = '<br><br><b>Question for counsel:</b> %s' % e(c["question_for_counsel"])
        if c.get("draft_enquiry_en"):
            extra = ('<br><br><b>Draft enquiry (Leif sends; nobody else):</b>%s<p class="zh">%s</p>'
                     % (quote_block(c["draft_enquiry_en"]), e(c["draft_enquiry_zh"])))
        A('<tr><td class="v"><code>%s</code></td><td>%s%s</td><td>%s</td><td>%s</td></tr>'
          % (e(c["id"]), e(c["what"]), extra, e(c["who"]), e(", ".join(c["blocks"]))))
    A('</tbody></table></div>')
    A('</section>')

    # 5 factory instructions
    A(h2(5, "Instructions to the factory", "致工厂的说明", "factory"))
    A('<div class="instr"><div><ol>%s</ol></div><div class="zh"><ol>%s</ol></div></div>'
      % ("".join("<li>%s</li>" % e(x) for x in data["factory_instructions"]["en"]),
         "".join("<li>%s</li>" % e(x) for x in data["factory_instructions"]["zh"])))
    A('</section>')

    # 6 repo metadata, live
    A(h2(6, "Our own metadata, re-measured at generation", "我方元数据（生成时重新测量）", "repo"))
    A('<div class="statbar">')
    A('  <div class="stat"><b>%d</b><span>ce-parts folders</span></div>' % census["n"])
    for k in ("generated", "vendor", "inferred"):
        A('  <div class="stat"><b>%d</b><span>origin = %s</span></div>' % (census["by_origin"].get(k, 0), k))
    A('  <div class="stat"><b>%d</b><span>assert "CC … 4.0"</span></div>' % len(census["assert_4_0"]))
    A('  <div class="stat"><b>%d</b><span>say "version not stated"</span></div>' % len(census["no_version"]))
    A('  <div class="stat"><b>%d / %d</b><span>our rebuilds with a licence field</span></div>' % (len(census["generated_with_licence"]), census["generated_total"]))
    A('  <div class="stat"><b>%s</b><span>repo LICENSE file</span></div>' % ("present" if lic_file["present"] else "ABSENT"))
    A('</div>')
    A('<div class="tablewrap"><table class="data" id="repo"><colgroup><col style="width:40%%"><col style="width:10%%"><col style="width:50%%"></colgroup><thead><tr>%s%s%s</tr></thead><tbody>' % (th("Check", "检查项"), th("Verdict", "结论"), th("Measured", "测量结果")))
    A('<tr><td>Folders asserting a CC version (4.0) that Pollen\'s README does not name</td><td class="v">%s</td><td>%s</td></tr>'
      % (chip("FAIL" if census["assert_4_0"] else "PASS"), e(", ".join(census["assert_4_0"]) or "none")))
    A('<tr><td>Folders that say "version not stated" (correct)</td><td class="v">%s</td><td>%s</td></tr>'
      % (chip("PASS" if census["no_version"] else "CANNOT DETERMINE"), e(", ".join(census["no_version"]) or "none")))
    A('<tr><td>Our parametric rebuilds (origin=generated) that carry NO licence field although they are rebuilt from CC-licensed meshes</td><td class="v">%s</td><td>%d of %d: %s</td></tr>'
      % (chip("FAIL" if census["generated_without_licence"] else "PASS"), len(census["generated_without_licence"]), census["generated_total"], e(", ".join(census["generated_without_licence"]) or "none")))
    A('<tr><td>Vendor-origin folders that mention the CC licence at all</td><td class="v">%s</td><td>%d of %d: %s</td></tr>'
      % (chip("PASS" if len(census["vendor_cc_folders"]) else "FAIL"), len(census["vendor_cc_folders"]), census["by_origin"].get("vendor", 0), e(", ".join(census["vendor_cc_folders"]) or "none")))
    A('<tr><td>This repository has a LICENSE file of its own, so the partner knows the terms on OUR documents</td><td class="v">%s</td><td>%s</td></tr>'
      % (chip("PASS" if lic_file["present"] else "FAIL"), e(", ".join(lic_file["files"]) or ("none of %s exists at the repo root" % ", ".join(lic_file["looked_for"])))))
    for r in readme_checks:
        A('<tr><td>README quote at cited line: <code>%s</code>%s</td><td class="v">%s</td><td>%s</td></tr>'
          % (e(r["file"]), (":%s" % e(r["line"])) if r["line"] != "-" else " (version check)", chip(r["verdict"]), e(r["why"])))
    A('</tbody></table></div>')
    A('<p class="lede">The fixes for the FAIL rows are metadata edits in <code>ce-parts/*/component.json</code> and a LICENSE file at the root; '
      'they belong to the shelf lane and to Leif (the choice of licence on our own work is a product decision), not to this page. This page reports them.</p>')
    A('</section>')

    # 7 evidence
    A(h2(7, "Evidence archive, hashed", "证据存档（含哈希）", "evidence"))
    A('<p class="lede">Every page quoted above was archived byte-for-byte in <code>out/factory/licence-evidence/</code> at fetch time. '
      'The hash was recorded in <code>licence.json</code> then and is re-computed now; a mismatch would mean the quoted page is not the archived page.</p>')
    A('<div class="tablewrap"><table class="data compact" id="ev"><colgroup><col style="width:22%%"><col style="width:34%%"><col style="width:7%%"><col style="width:22%%"><col style="width:15%%"></colgroup><thead><tr>%s%s%s%s%s</tr></thead><tbody>'
      % (th("File", "文件"), th("URL", "网址"), th("Bytes", "字节"), th("sha256 (measured now)", "sha256（当前测量）"), th("Verdict", "结论")))
    for x in evidence:
        A('<tr><td><code>%s</code></td><td class="src"><a href="%s">%s</a></td><td class="num">%s</td><td class="src">%s</td><td class="v">%s<br><span class="src">%s</span></td></tr>'
          % (e(x["file"]), e(x["url"]), e(x["url"]), e(x["size"]) if x["size"] is not None else "-", e(x["measured"] or "-"), chip(x["verdict"]), e(x["why"])))
    A('</tbody></table></div>')
    A('</section>')

    # 8 method
    A(h2(8, "Method", "方法", "method"))
    A('<ul>')
    A('<li>Fetch: %s</li>' % e(data["fetch_method"]))
    A('<li>Quotes are verbatim from the archived bytes; line numbers are of the archived file. The README quote is re-checked at the cited line in both local mirrors every time this page is generated (section 6).</li>')
    A('<li>Verdict words: PASS / FAIL / CANNOT DETERMINE. For a fact, PASS means established. For a question, PASS means the plain reading of the licence permits it, FAIL means it does not, CANNOT DETERMINE means the licence text does not answer it and the thing that does is named.</li>')
    A('<li>No search was run for trade marks, registered designs or patents (F9). No message was sent to anyone. Nothing was bought.</li>')
    A('<li>The Creative Commons clause text is the 4.0 International legal code. Pollen names no version; both 3.0 and 4.0 carry the NonCommercial and ShareAlike elements, so the plain-reading answers do not turn on the version, but the exact clause numbering would.</li>')
    A('<li>Generated %s by tools/gen_licence.py from out/factory/licence.json.</li>' % e(now))
    A('</ul></section>')
    A('</div>\n</body>\n</html>\n')
    return "\n".join(o)


def main():
    data = json.load(open(DATA, encoding="utf-8"))
    census = census_component_json()
    readme_checks = check_readme_lines()
    evidence = verify_evidence(data)
    lic_file = repo_licence_file()
    now = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    page = render(data, census, readme_checks, evidence, lic_file, now)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    summary = {
        "written": os.path.relpath(OUT, REPO),
        "bytes": len(page.encode("utf-8")),
        "facts": len(data["facts"]),
        "census": {k: (v if not isinstance(v, list) else len(v)) for k, v in census.items()},
        "assert_4_0": census["assert_4_0"],
        "generated_without_licence": len(census["generated_without_licence"]),
        "repo_licence_file": lic_file,
        "readme_checks": [(r["file"], r["line"], r["verdict"]) for r in readme_checks],
        "evidence": [(x["file"], x["verdict"]) for x in evidence],
    }
    print(json.dumps(summary, indent=1, ensure_ascii=False))
    bad = [r for r in readme_checks if r["verdict"] != "PASS"] + [x for x in evidence if x["verdict"] != "PASS"]
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
