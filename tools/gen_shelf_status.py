#!/usr/bin/env python3
"""gen_shelf_status.py — SHELF-STATUS.html from `bin/triad check --all`.

    python3 tools/gen_shelf_status.py [--root DIR] [--json out.json]

The triad shelf grades itself. This runs that grader over every part,
connection and assembly in this repo, parses its output into
out/laneT/shelf-status.json, and renders SHELF-STATUS.html in the shared
academic style (tools/doc.css, the COMPARISON.html pattern: a data file and a
generator, never a hand-maintained table).

It reports each ref WITH ITS REASON, because a bare verdict is not a status —
"CANNOT DETERMINE" tells a reader nothing they can act on, and the sentence the
folder wrote about itself tells them everything. Reasons are grouped by the
DEFECT CLASS they belong to (dangling ref, zero interfaces, unmeasured frame,
stale trust, the folder's own words), so a reader can see how many of one kind
of problem the shelf has rather than reading 60 lines to find out.

Nothing here re-grades anything: every verdict and every sentence in the page
comes from `bin/triad check` and is quoted, not summarised. Exit code mirrors
the checker's own: 0 all PASS, 1 anything not PASS, 2 the checker itself broke.
"""
import argparse
import datetime
import html
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
WORKSHOP = os.path.dirname(os.path.dirname(REPO))
TRIAD = os.path.join(WORKSHOP, "bin", "triad")

VERDICTS = ("PASS", "FAIL", "CANNOT DETERMINE")
HEAD_RE = re.compile(r"^(PASS|FAIL|CANNOT DETERMINE)\s+((?:part|connection|assembly):\S+)\s*"
                     r"(?:\((.*)\))?\s*$")
ROW_RE = re.compile(r"^\s+(PASS|FAIL|CANNOT DETERMINE)\s{2}(.*)$")
TAIL_RE = re.compile(r"^checked (\d+)\s+PASS (\d+)\s+not-PASS (\d+)\s+measured-nothing (\d+)")

# The defect classes, in the order a reader should meet them: the ones that
# break the graph first, then the ones that leave it unmeasured.
CLASSES = [
    ("dangling", "Dangling ref",
     "a folder names a `connection:`/`part:`/`assembly:` that no folder answers to. "
     "TRIAD.md: a dangling ref is a FAIL, never a warning.",
     lambda s: "dangling ref" in s),
    ("joint_side", "Joint side unresolved",
     "an assembly's joints.json row has no {ref, interface} on one side, so the joint "
     "graph does not close.",
     lambda s: "side b needs" in s or "side a needs" in s),
    ("two_spellings", "Two spellings of one fact",
     "cad/interfaces.json carries both `interfaces` and `record.interfaces` and nothing "
     "says which the folder means.",
     lambda s: "two spellings of one fact" in s),
    ("missing_artifact", "Ledger artifact missing",
     "an append-only ledger row cites a file that is not on disk, so the row's claim "
     "cannot be checked.",
     lambda s: "does not exist" in s),
    ("stale_trust", "trust.json stale",
     "the computed tier on disk disagrees with the ledger it was computed from — run "
     "`bin/triad trust <ref>`.",
     lambda s: "stale:" in s),
    ("zero_interfaces", "Zero interfaces declared",
     "cad/interfaces.json exists to name the anchors other things connect to, and it "
     "names none. An empty list is not an answer.",
     lambda s: "declares ZERO interfaces" in s),
    ("unmeasured_frame", "Interface frame unmeasured",
     "an interface row exists but its frame is null, so nothing can be placed against it.",
     lambda s: "frame unmeasured" in s),
    ("own_words", "The folder grades itself",
     "TRIAD.md, “Coverage is part of the verdict”: no reader may grade a folder better "
     "than the folder grades itself. The checker repeats that rule on every one of these rows; "
     "it is said here once and stripped from the rows below, so what is quoted is the "
     "folder's own sentence and nothing else.",
     lambda s: "grades ITSELF" in s),
]


BOILER = ('the folder grades ITSELF CANNOT DETERMINE here and no reader may grade it '
          'better (TRIAD.md, "Coverage is part of the verdict"). Its own words: ')


def trim(why):
    """The folder's OWN sentence, without the standard preamble.

    Every `own_words` reason repeats the same 150-character explanation of why a
    folder's self-grade binds. That explanation belongs once, at the head of the
    class — not sixty times down a table, where it buries the only part of the
    row a reader can act on. Removed here, said once there; the folder's own
    words are kept whole.
    """
    return why.replace(BOILER, "").strip()


def classify(reason):
    for key, _t, _d, test in CLASSES:
        if test(reason):
            return key
    return "other"


def run_check(root):
    env = dict(os.environ)
    env["CE_TRIAD_ROOT"] = root + ":" + WORKSHOP
    p = subprocess.run([TRIAD, "check", "--all"], cwd=root, env=env,
                       capture_output=True, text=True)
    return p.stdout + p.stderr, p.returncode


def enumerate_shelf(root):
    """Every ref that lives in this root, read off the filesystem.

    `bin/triad check --all` prints ONLY the refs that are not PASS — its tail
    line carries the PASS count but not the names. So the PASS names are read
    off the shelf itself and CROSS-CHECKED against that count: if the folder
    count and the checker's own `checked` total disagree, this page names no
    PASS refs at all and says so, rather than inventing the difference.
    """
    out = []
    for sysname, d in (("part", "ce-parts"), ("connection", "ce-connections"),
                       ("assembly", "ce-assemblies")):
        base = os.path.join(root, d)
        if not os.path.isdir(base):
            continue
        for slug in sorted(os.listdir(base)):
            folder = os.path.join(base, slug)
            if slug.startswith(".") or not os.path.isdir(folder):
                continue
            if not any(os.path.exists(os.path.join(folder, f)) for f in
                       ("component.json", "connection.json", "assembly.json", "part.json")):
                continue
            out.append("%s:%s" % (sysname, slug))
    return out


def parse(text):
    refs, cur, totals = [], None, None
    for line in text.splitlines():
        m = HEAD_RE.match(line)
        if m:
            cur = {"verdict": m.group(1), "ref": m.group(2),
                   "meta": (m.group(3) or "").strip(), "reasons": []}
            refs.append(cur)
            continue
        m = ROW_RE.match(line)
        if m and cur is not None:
            where, _, why = m.group(2).partition(": ")
            cur["reasons"].append({"verdict": m.group(1), "where": where.strip(),
                                   "why": why.strip() or m.group(2).strip(),
                                   "class": classify(m.group(2))})
            continue
        m = TAIL_RE.match(line.strip())
        if m:
            totals = {"checked": int(m.group(1)), "pass": int(m.group(2)),
                      "not_pass": int(m.group(3)), "measured_nothing": int(m.group(4))}
    for r in refs:
        r["system"] = r["ref"].split(":", 1)[0]
        r["classes"] = sorted({x["class"] for x in r["reasons"]})
    return refs, totals


def e(s):
    return html.escape(str(s), quote=True)


CHIP = {"PASS": "pass", "CANNOT DETERMINE": "cd", "FAIL": "rail"}


def render(refs, totals, before, exit_code, root):
    now = datetime.date.today().isoformat()
    by_class = {}
    for r in refs:
        for x in r["reasons"]:
            by_class.setdefault(x["class"], []).append((r, x))
    order = {"assembly": 0, "connection": 1, "part": 2}
    refs_sorted = sorted(refs, key=lambda r: (order.get(r["system"], 9),
                                              {"FAIL": 0, "CANNOT DETERMINE": 1, "PASS": 2}[r["verdict"]],
                                              r["ref"]))
    o = []
    A = o.append
    A('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">')
    A('<meta name="viewport" content="width=device-width, initial-scale=1">')
    A('<title>Shelf Status</title>')
    A('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opt_sz,wght@8..60,400;8..60,600;8..60,700&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">')
    A('<link rel="stylesheet" href="tools/doc.css">')
    A('<style>\n'
      '  td.why{font-size:12.5px;color:var(--ink-2);max-width:none}\n'
      '  td.ref code{font-size:12.5px}\n'
      '  tr.pass td.why{color:#7d7d7d}\n'
      '  .cls{margin:18px 0 0}\n'
      '  .cls h3{margin:0 0 2px}\n'
      '  .cls p.lede{margin:0 0 8px}\n'
      '  .count{font-family:var(--mono);color:var(--accent);font-weight:600}\n'
      '  .delta{font-family:var(--mono);font-size:12.5px}\n'
      '  details.folder{border-bottom:1px solid var(--hair);padding:7px 0}\n'
      '  details.folder summary{cursor:pointer;font-family:var(--sans);font-size:13px}\n'
      '  details.folder summary::marker{color:var(--ink-2)}\n'
      '  details.folder ul{margin:8px 0 4px;font-size:13px}\n'
      '</style>\n</head>\n<body>\n<div class="wrap">')
    A('<p class="backlink"><a href="RELEASE.html">← Release dossier</a></p>')
    A('<header class="hero">')
    A('  <p class="eyebrow">Microduck reverse-engineering · triad shelf</p>')
    A('  <h1>Shelf status: every folder, its verdict, and its reason</h1>')
    A('  <p class="sub">The output of <code>bin/triad check --all</code> in this repo, per ref, '
      'with the sentence each folder wrote about itself. Verdicts are quoted, never re-graded: '
      'this page reports the shelf, it does not argue with it.</p>')
    A('  <div class="rev"><span>MD-SHELF-001 · Rev A</span><span>%s</span>'
      '<span>generator: tools/gen_shelf_status.py</span>'
      '<span>root: %s</span><span>checker exit: %d</span></div>' % (now, e(os.path.basename(root)), exit_code))
    A('</header>')
    A('<div class="statbar">')
    A('  <div class="stat"><b>%d</b><span>refs checked</span></div>' % totals["checked"])
    A('  <div class="stat"><b>%d</b><span>PASS</span></div>' % totals["pass"])
    A('  <div class="stat"><b>%d</b><span>not PASS</span></div>' % totals["not_pass"])
    if before:
        A('  <div class="stat"><b>%d → %d</b><span>PASS, before → after</span></div>'
          % (before["pass"], totals["pass"]))
    A('  <div class="stat"><b>%d</b><span>distinct reasons</span></div>'
      % sum(len(v) for v in by_class.values()))
    A('</div>')
    A('<nav class="toc"><a href="#counts">1 The count</a><a href="#classes">2 By defect class</a>'
      '<a href="#refs">3 Every ref</a><a href="#method">4 Method</a></nav>')

    A('<section id="counts"><h2><span class="n">1</span>The count</h2>')
    A('<p class="lede">Three verdicts. CANNOT DETERMINE is not a pass, and a folder that '
      'grades itself CANNOT DETERMINE cannot be graded better by anything reading it.</p>')
    A('<div class="tablewrap"><table class="data"><thead><tr>'
      '<th>system</th><th>refs</th><th>PASS</th><th>CANNOT DETERMINE</th><th>FAIL</th></tr></thead><tbody>')
    for sysname in ("part", "connection", "assembly"):
        rs = [r for r in refs if r["system"] == sysname]
        if not rs:
            continue
        A('<tr><td>%s</td><td class="num">%d</td><td class="num">%d</td>'
          '<td class="num">%d</td><td class="num">%d</td></tr>'
          % (e(sysname), len(rs),
             sum(1 for r in rs if r["verdict"] == "PASS"),
             sum(1 for r in rs if r["verdict"] == "CANNOT DETERMINE"),
             sum(1 for r in rs if r["verdict"] == "FAIL")))
    A('</tbody></table></div>')
    if before:
        A('<p class="delta">Before this lane, on the same checker: checked %d, PASS %d, '
          'not-PASS %d. After: checked %d, PASS %d, not-PASS %d.</p>'
          % (before["checked"], before["pass"], before["not_pass"],
             totals["checked"], totals["pass"], totals["not_pass"]))
    A('</section>')

    A('<section id="classes"><h2><span class="n">2</span>By defect class</h2>')
    A('<p class="lede">A bare verdict is not a status. Every reason the checker gave, grouped by '
      'the kind of defect it is, so the shape of what is left is visible at a glance.</p>')
    for key, title, desc, _t in CLASSES + [("other", "Other", "reasons this page has no class for yet.", None)]:
        rows = by_class.get(key) or []
        if not rows:
            continue
        A('<div class="cls"><h3>%s <span class="count">×%d</span></h3>'
          '<p class="lede">%s</p>' % (e(title), len(rows), e(desc)))
        for r, x in sorted(rows, key=lambda p: p[0]["ref"]):
            A('<details class="folder"><summary><span class="chip %s">%s</span> &nbsp;'
              '<code>%s</code> &nbsp;·&nbsp; %s</summary><ul><li>%s</li></ul></details>'
              % (CHIP[x["verdict"]], e(x["verdict"]), e(r["ref"]), e(x["where"]),
                 e(trim(x["why"]))))
        A('</div>')
    A('</section>')

    A('<section id="refs"><h2><span class="n">3</span>Every ref</h2>')
    A('<p class="lede">Assemblies first, then connections, then parts; within each, whatever is '
      'not PASS comes first. The reason column is the checker’s own words, truncated only '
      'where a folder wrote a paragraph — the full text is in the JSON beside this page.</p>')
    if not totals.get("pass_named", False):
        A('<div class="note"><b>PASS refs are not named below.</b> %s</div>'
          % e(totals.get("pass_named_why", "")))
    else:
        A('<p class="lede"><code>bin/triad check --all</code> prints only what is NOT PASS; its '
          'tail line carries the PASS count but no names. The PASS rows here are the shelf folders '
          'the checker did not complain about, read off the filesystem and cross-checked against '
          'that count \u2014 %d folders on the shelf, %d refs checked. Where those two disagree '
          'this page refuses to name them.</p>' % (totals["checked"], totals["checked"]))
    A('<div class="tablewrap"><table class="data"><thead><tr><th>verdict</th><th>ref</th>'
      '<th>iteration</th><th>why it is not PASS</th></tr></thead><tbody>')
    for r in refs_sorted:
        why = " · ".join(trim(x["why"])[:420] for x in r["reasons"]) or "—"
        A('<tr%s><td><span class="chip %s">%s</span></td><td class="ref"><code>%s</code></td>'
          '<td class="mono" style="font-size:11.5px;color:var(--ink-2)">%s</td><td class="why">%s</td></tr>'
          % (' class="pass"' if r["verdict"] == "PASS" else "",
             CHIP[r["verdict"]], e(r["verdict"]), e(r["ref"]), e(r["meta"]), e(why)))
    A('</tbody></table></div></section>')

    A('<section id="method"><h2><span class="n">4</span>Method</h2>')
    A('<pre class="code">export CE_TRIAD_ROOT="%s:%s"\n%s check --all\npython3 tools/gen_shelf_status.py</pre>'
      % (e(root), e(WORKSHOP), e(os.path.relpath(TRIAD, REPO))))
    A('<p>The checker is <code>bin/triad</code> in the ce-workshop root, shared by all three '
      'triad systems; its contract is <code>TRIAD.md</code>. This page parses its stdout and '
      'renders it. It re-grades nothing and it never softens a verdict: where a folder says '
      'CANNOT DETERMINE about itself, that sentence is reproduced here verbatim, because '
      '“coverage is part of the verdict” and a reader who cannot see the folder’s '
      'own doubt cannot act on it.</p>')
    A('<p>Machine-readable output, regenerated with the page: '
      '<code>out/laneT/shelf-status.json</code> — every ref, every reason, its defect class '
      'and the file it was raised against.</p>')
    A('</section>')
    A('<footer><span>MD-SHELF-001 Rev A</span><span>%s</span>'
      '<span>generated by tools/gen_shelf_status.py</span>'
      '<span>source: bin/triad check --all</span></footer>' % now)
    A('</div>\n</body>\n</html>')
    return "\n".join(o) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=REPO)
    ap.add_argument("--json", default=os.path.join(REPO, "out", "laneT", "shelf-status.json"))
    ap.add_argument("--html", default=os.path.join(REPO, "SHELF-STATUS.html"))
    ap.add_argument("--before", default=os.path.join(REPO, "out", "laneT", "shelf-before.json"),
                    help="a previous shelf-status.json to show a before/after against")
    a = ap.parse_args(argv)

    text, code = run_check(a.root)
    refs, totals = parse(text)
    if totals is not None:
        listed = {r["ref"] for r in refs}
        on_shelf = enumerate_shelf(a.root)
        if len(on_shelf) == totals["checked"]:
            for ref in on_shelf:
                if ref not in listed:
                    refs.append({"verdict": "PASS", "ref": ref, "meta": "", "reasons": [],
                                 "system": ref.split(":", 1)[0], "classes": []})
            totals["pass_named"] = True
            totals["pass_named_why"] = ("the checker's `checked` total and the number of shelf "
                                        "folders carrying an identity file agree at %d, so every "
                                        "ref it did not complain about is named PASS here."
                                        % totals["checked"])
        else:
            totals["pass_named"] = False
            totals["pass_named_why"] = (
                "the checker reports %d refs checked and the shelf holds %d folders that carry an "
                "identity file. They disagree, so the PASS refs are NOT named on this page — only "
                "the %d not-PASS refs the checker printed are. CANNOT DETERMINE, not a guess."
                % (totals["checked"], len(on_shelf), len(refs)))
    if totals is None:
        print("BROKEN INPUT: bin/triad check --all printed no summary line", file=sys.stderr)
        print(text[-2000:], file=sys.stderr)
        return 2
    before = None
    if os.path.exists(a.before):
        try:
            before = json.load(open(a.before, encoding="utf-8"))["totals"]
        except Exception:                                     # noqa: BLE001
            before = None

    doc = {"$what": "the triad shelf's own verdict on every folder in this repo, per ref, "
                    "with the reason the checker gave and the defect class it belongs to",
           "$generated_by": "tools/gen_shelf_status.py (ce-designs/microduck lane T)",
           "date": datetime.date.today().isoformat(),
           "command": "bin/triad check --all", "checker_exit_code": code,
           "totals": totals, "refs": refs}
    os.makedirs(os.path.dirname(a.json), exist_ok=True)
    json.dump(doc, open(a.json, "w", encoding="utf-8"), indent=1)
    open(a.html, "w", encoding="utf-8").write(render(refs, totals, before, code, a.root))
    print("checked %(checked)d  PASS %(pass)d  not-PASS %(not_pass)d" % totals)
    print("wrote", os.path.relpath(a.json, REPO), "and", os.path.relpath(a.html, REPO))
    return code


if __name__ == "__main__":
    sys.exit(main())
