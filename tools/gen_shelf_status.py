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
import hashlib
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

IFACE_RE = re.compile(r"interface '([^']+)' frame unmeasured")
ART_RE = re.compile(r"sha256 of (\S+) is ")

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
    ("superseded_row", "Ledger row superseded \u2014 the record working, not a gap",
     "an earlier row's artifact was re-measured and a LATER row names the same artifact. "
     "TRIAD.md: the later row's hash is the one checked, and the earlier row is REPORTED as "
     "CANNOT DETERMINE rather than silently skipped or deleted, because the ledger is append-only "
     "and that row records what the artifact WAS when it was measured. A ref whose only reasons "
     "are these has no gap in it \u2014 its current measurement passed and the old one is kept as "
     "history. Nothing inside the folder closes it; only a change to the checker's contract would, "
     "and that is a decision about the contract, not a defect in the part.",
     lambda s: "SUPERSEDED:" in s),
    ("artifact_changed", "Ledger artifact changed after it was ledgered",
     "a ledger row's sha256 no longer matches the file on disk and NO later row names that "
     "artifact. TRIAD.md: editing a ledgered artifact WITHOUT appending a row is a FAIL, by "
     "design \u2014 the last row's hash is the one checked, so a re-run that overwrites its own "
     "evidence file is caught. The fix is never to edit the row: append a new row for the new run, "
     "which supersedes the old one and says so.",
     lambda s: "ledger says" in s or "this row says" in s),
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
    ("no_why", "Refusal with no reason",
     "a folder grades itself CANNOT DETERMINE or FAIL and its record carries no `why`. "
     "TRIAD.md: a refusal that cannot say why it does not know does not know that it does not "
     "know \u2014 and a reader has nothing to act on. This class must be EMPTY; four rows sat in it "
     "on 2026-09-03 (part:s-8252, part:fusb302, part:microduck-m12-lens, part:microduck-speaker) "
     "under a commit message claiming every refusal named what settles it, which is why the class "
     "exists on this page instead of being fixed silently.",
     lambda s: "with no `why`" in s),
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


TRUNC_AT = 420


def cut(text, n=TRUNC_AT):
    """(head, dropped) — truncate on a WORD boundary, and say how much was cut.

    The first version of this page sliced at exactly 420 characters with no
    marker, so a folder's paragraph rendered as "...so the frame" and
    "...355.0 deg c" — fragments that end mid-word and read as if the folder
    had written them that way. A reader could not see WHERE the cut was, which
    is the one thing a truncation must show. This cuts at the last space
    before the limit and returns the number of characters dropped so the row
    can print it.
    """
    text = text.strip()
    if len(text) <= n:
        return text, 0
    head = text[:n]
    sp = head.rfind(" ")
    if sp > n * 0.5:
        head = head[:sp]
    head = head.rstrip(" ,;:.\u2014-")
    return head, len(text) - len(head)


def why_cell(reasons):
    """The reason column: the checker's own words, with every cut marked."""
    if not reasons:
        return "\u2014"
    parts = []
    for x in reasons:
        full = x.get("why_full") or trim(x["why"])
        head, dropped = cut(full)
        cell = e(head)
        if dropped:
            cell += ('<span class="trunc"> \u2026 <span class="tn">[CUT HERE \u2014 %d more '
                     'characters; whole sentence in out/laneT/shelf-status.json and in %s]'
                     '</span></span>' % (dropped, e(x["where"])))
        parts.append(cell)
    return " \u00b7 ".join(parts)


def classify(reason):
    for key, _t, _d, test in CLASSES:
        if test(reason):
            return key
    return "other"


def norm(t):
    return " ".join(str(t).split())


def attach_full_why(refs, root):
    """Put the folder's WHOLE sentence back.

    MEASURED 2026-09-03: the mid-word fragments in this page's reason column
    ("...so the frame", "...RESEARCHED AND A") are not this generator's cut —
    they are `bin/_triadlib.py:1482`, which prints a folder's own `why` as
    `.strip().replace("\n", " ")[:400]`. The checker hands out 400 characters
    and no marker, so nothing downstream can tell a folder that stopped there
    from one that was cut. The whole sentence is on disk in the folder's own
    record, so this reads it back, checks the checker's text is a prefix of it,
    and records how much was dropped. Where the prefix does not match, nothing
    is claimed: the row keeps the checker's words and no `why_full`.
    """
    cache, recovered, recoverable = {}, 0, 0

    def doc_at(rel):
        path = os.path.join(root, rel)
        if path not in cache:
            try:
                cache[path] = json.load(open(path, encoding="utf-8"))
            except Exception:                                 # noqa: BLE001
                cache[path] = None
        return cache[path]

    for r in refs:
        for x in r["reasons"]:
            # A ledger artifact that no longer hashes: say WHEN the file was
            # last written. A reader who can see the artifact was rewritten
            # after the row was ledgered knows this is a re-run in flight, not
            # a corrupted record, and knows which of the two to go and fix.
            if x["class"] in ("artifact_changed", "superseded_row"):
                m = ART_RE.search(x["why"])
                if m:
                    # bin/_triadlib.artifact_path resolves a ledger row's
                    # artifact against res.dir, the ITERATION directory — two
                    # levels above evidence/ledger.jsonl, not one. Resolving it
                    # against the evidence directory instead silently produced
                    # a path that does not exist and dated nothing (measured
                    # and fixed 2026-09-03).
                    led = os.path.join(root, x["where"].split(":")[0])
                    art = os.path.normpath(os.path.join(
                        os.path.dirname(os.path.dirname(led)), m.group(1)))
                    try:
                        ts = datetime.datetime.fromtimestamp(os.path.getmtime(art))
                        x["artifact"] = os.path.relpath(art, root)
                        x["artifact_mtime"] = ts.strftime("%Y-%m-%d %H:%M")
                        x["why_full"] = ("%s (that file was last written %s)"
                                         % (norm(trim(x["why"])), x["artifact_mtime"]))
                        recovered += 1
                        recoverable += 1
                    except OSError:
                        pass
                continue

            doc = doc_at(x["where"])
            if not isinstance(doc, dict):
                continue

            if x["class"] in ("own_words", "unmeasured_frame"):
                recoverable += 1
            if x["class"] == "own_words":
                full = norm(((doc.get("record") or {}).get("why")) or "")
                printed = norm(trim(x["why"]))
                if not full or not printed or not full.startswith(printed):
                    continue
                x["why_full"] = full
                x["dropped_by_checker"] = len(full) - len(printed)
                recovered += 1
                continue

            # An unmeasured frame: the checker names the interface but not the
            # folder's reason, so a reader sees "frame unmeasured" and nothing
            # they can act on. The interface row itself carries a `why` that
            # says what would settle it; put it back.
            if x["class"] == "unmeasured_frame":
                m = IFACE_RE.search(x["why"])
                if not m:
                    continue
                rows = doc.get("interfaces") or (doc.get("record") or {}).get("interfaces") or []
                for row in rows:
                    if row.get("name") != m.group(1):
                        continue
                    own = norm(row.get("why") or "")
                    if not own:
                        break
                    x["why_full"] = "%s Its own words: %s" % (norm(trim(x["why"])), own)
                    x["interface_why"] = own
                    recovered += 1
                    break
    return recovered, recoverable


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


SYSDIR = {"part": "ce-parts", "connection": "ce-connections", "assembly": "ce-assemblies"}


def folder_of(ref):
    """The repo-relative folder a ref lives in — a link a reader can follow.

    Until 2026-09-03 this page linked to nothing but RELEASE.html and its
    stylesheet: every ref it named was a dead string. A ref is a citation and a
    citation that cannot be followed is decoration.
    """
    sysname, slug = ref.split(":", 1)
    return "%s/%s/" % (SYSDIR.get(sysname, sysname), slug)


VCOL = {"PASS": "#1c6b3c", "CANNOT DETERMINE": "#8a5a00", "FAIL": "#9a2b1e"}
VKEY = {"PASS": "P", "CANNOT DETERMINE": "?", "FAIL": "F"}


def svg_shelf_map(refs):
    """Figure 1 — the whole shelf as one picture, drawn from the same `refs`
    list the tables below are drawn from, so the two cannot disagree.

    A page about a shelf that carries no picture of that shelf cannot be
    audited from itself: a reader has to take the tables' word for the shape of
    the problem. One cell per ref, coloured by verdict, grouped by system and
    ordered worst-first, answers "how bad, and where" before any table is read.
    """
    order = {"assembly": 0, "connection": 1, "part": 2}
    vrank = {"FAIL": 0, "CANNOT DETERMINE": 1, "PASS": 2}
    groups = []
    for sysname in ("assembly", "connection", "part"):
        rs = sorted((r for r in refs if r["system"] == sysname),
                    key=lambda r: (vrank[r["verdict"]], r["ref"]))
        if rs:
            groups.append((sysname, rs))
    CELL, GAP, PER = 22, 4, 26
    W, x0, lab = 812, 118, 13
    y, rows = 34, []
    for sysname, rs in groups:
        n_rows = (len(rs) + PER - 1) // PER
        rows.append((sysname, rs, y, n_rows))
        y += n_rows * (CELL + GAP) + 26
    H = y + 4
    o = ['<svg viewBox="0 0 %d %d" width="100%%" role="img" '
         'aria-label="every ref on the shelf, one cell per ref, coloured by verdict" '
         'xmlns="http://www.w3.org/2000/svg" style="display:block;background:#fff">' % (W, H)]
    o.append('<style>.lb{font:600 11px "Source Sans 3",sans-serif;fill:#565656}'
             '.lg{font:11px "Source Sans 3",sans-serif;fill:#565656}'
             '.ck{font:600 11px "IBM Plex Mono",monospace;fill:#fff}</style>')
    lx = x0
    for v in ("FAIL", "CANNOT DETERMINE", "PASS"):
        n = sum(1 for r in refs if r["verdict"] == v)
        o.append('<rect x="%d" y="8" width="12" height="12" fill="%s"/>' % (lx, VCOL[v]))
        o.append('<text class="lg" x="%d" y="18">%s &#183; %d</text>'
                 % (lx + 17, e(v), n))
        lx += 34 + len(v) * 6.4 + len(str(n)) * 7
    for sysname, rs, ytop, n_rows in rows:
        o.append('<text class="lb" x="0" y="%d">%s &#183; %d</text>'
                 % (ytop + 15, e(sysname), len(rs)))
        for i, r in enumerate(rs):
            cx = x0 + (i % PER) * (CELL + GAP)
            cy = ytop + (i // PER) * (CELL + GAP)
            o.append('<g><title>%s &#8212; %s</title>'
                     '<rect x="%d" y="%d" width="%d" height="%d" fill="%s"/>'
                     '<text class="ck" x="%d" y="%d" text-anchor="middle">%s</text></g>'
                     % (e(r["ref"]), e(r["verdict"]), cx, cy, CELL, CELL,
                        VCOL[r["verdict"]], cx + CELL // 2, cy + 15,
                        VKEY[r["verdict"]]))
    o.append('</svg>')
    return "\n".join(o)


def svg_class_bars(refs, by_class, classes):
    """Figure 2 — how many REFS carry each defect class.

    The statbar counts reason ROWS, which is a different number: one ref can
    carry five rows of one class. This counts refs, so a reader can see that
    the shelf has a few kinds of problem repeated, not sixty separate ones.
    """
    counts = []
    for key, title, _lede, _fn in classes:
        rs = {r["ref"] for r, _x in by_class.get(key, [])}
        if rs:
            counts.append((title, len(rs)))
    counts.sort(key=lambda t: -t[1])
    if not counts:
        return ""
    BAR, GAP, x0, W = 20, 8, 330, 812
    mx = max(n for _t, n in counts)
    H = len(counts) * (BAR + GAP) + 12
    o = ['<svg viewBox="0 0 %d %d" width="100%%" role="img" '
         'aria-label="refs carrying each defect class" '
         'xmlns="http://www.w3.org/2000/svg" style="display:block;background:#fff">' % (W, H)]
    o.append('<style>.bl{font:12px "Source Sans 3",sans-serif;fill:#1a1a1a}'
             '.bn{font:600 12px "IBM Plex Mono",monospace;fill:#243b53}</style>')
    for i, (title, n) in enumerate(counts):
        y = i * (BAR + GAP) + 4
        w = int(round((W - x0 - 46) * n / float(mx)))
        o.append('<text class="bl" x="%d" y="%d" text-anchor="end">%s</text>'
                 % (x0 - 10, y + 14, e(title)))
        o.append('<rect x="%d" y="%d" width="%d" height="%d" fill="#243b53" opacity=".82"/>'
                 % (x0, y, max(w, 2), BAR))
        o.append('<text class="bn" x="%d" y="%d">%d</text>' % (x0 + max(w, 2) + 7, y + 14, n))
    o.append('</svg>')
    return "\n".join(o)


def reason_key(x):
    """Everything about one reason row that this page PRINTS.

    `why` is the checker's own output and `bin/_triadlib.py` cuts it at 400
    characters with no marker, so `why` alone is blind to anything a folder
    wrote past that point — and section 4 of this page prints `why_full`, the
    whole sentence read back from the folder's record. MEASURED 2026-09-03 on
    the live shelf: 33 of 90 reason rows on 29 refs carry a tail the checker
    dropped, 30 680 characters in all (184 shortest, 1849 longest). All of that
    is on the page and none of it was in the digest. `where` and the row's own
    verdict are covered for the same reason: both are printed, and a row moving
    from one file to another, or from CANNOT DETERMINE to FAIL while the ref's
    overall verdict stays put, is a change a reader can see.
    """
    return [x.get("verdict", ""), x.get("class", ""), x.get("where", ""),
            trim(x.get("why_full") or x.get("why", ""))]


def fingerprint(refs):
    """A canonical digest of the WHOLE shelf reading: every ref, its verdict, and
    every reason row this page prints for it — the row's verdict, its defect
    class, where the checker found it, and the folder's WHOLE sentence.

    Why this exists: until 2026-09-03 `--verify` compared only totals['checked'],
    ['pass'], ['not_pass'] and the SET of ref names. Those three totals are blind
    to the one movement that matters most — a ref going CANNOT DETERMINE -> FAIL
    keeps `not_pass` identical — and the committed page was materially wrong about
    which folders FAIL while `--verify` printed CURRENT and exited 0. A staleness
    detector that cannot see a verdict change is a decoration.

    The first repair of it covered `trim(why)` only, which left the second half
    of the same hole open: see reason_key() for the measurement. The digest now
    covers every field the page renders.
    """
    rows = sorted(
        [r["ref"], r["verdict"], sorted(reason_key(x) for x in r["reasons"])]
        for r in refs)
    blob = json.dumps(rows, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def verdict_counts(refs):
    c = {}
    for r in refs:
        c[r["verdict"]] = c.get(r["verdict"], 0) + 1
    return c


def render(refs, totals, before, exit_code, root, recovered_n=0, recoverable_n=0):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
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
    A('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">')
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
      '  span.trunc{color:var(--ink-2)}\n'
      '  span.tn{font-family:var(--sans);font-size:10.5px;letter-spacing:.01em}\n'
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
      '<span>root: %s</span><span>checker exit: %d</span>'
      '<span>digest %s</span></div>'
      % (now, e(os.path.basename(root)), exit_code, fingerprint(refs)[:16]))
    A('</header>')
    A('<div class="statbar">')
    A('  <div class="stat"><b>%d</b><span>refs checked</span></div>' % totals["checked"])
    A('  <div class="stat"><b>%d</b><span>PASS</span></div>' % totals["pass"])
    A('  <div class="stat"><b>%d</b><span>not PASS</span></div>' % totals["not_pass"])
    if before:
        A('  <div class="stat"><b>%d → %d</b><span>PASS, before → after</span></div>'
          % (before["pass"], totals["pass"]))
    # NOT "distinct reasons": this is the number of reason ROWS the checker
    # printed, and most of them share one defect class. Both numbers are shown,
    # each labelled as what it is.
    n_rows = sum(len(v) for v in by_class.values())
    n_classes = len([k for k, v in by_class.items() if v])
    n_texts = len({trim(x["why"]) for r in refs for x in r["reasons"]})
    A('  <div class="stat"><b>%d</b><span>reason rows</span></div>' % n_rows)
    A('  <div class="stat"><b>%d</b><span>distinct sentences</span></div>' % n_texts)
    A('  <div class="stat"><b>%d</b><span>defect classes</span></div>' % n_classes)
    A('</div>')
    A('<nav class="toc"><a href="#map">1 The shelf, drawn</a><a href="#counts">2 The count</a>'
      '<a href="#classes">3 By defect class</a>'
      '<a href="#refs">4 Every ref</a><a href="#method">5 Method</a></nav>')

    A('<section id="map"><h2><span class="n">1</span>The shelf, drawn</h2>')
    A('<p class="lede">One cell per ref, coloured by the verdict <code>bin/triad check --all</code> '
      'gave it, grouped by system and ordered worst-first. Both figures are drawn from the same '
      '<code>refs</code> list as every table below, in the same run of the same generator, so the '
      'picture and the tables cannot disagree — and the page can be checked against its own '
      'subject without leaving it. Hover a cell for its ref.</p>')
    A('<figure><div class="dia">%s</div>' % svg_shelf_map(refs))
    fails = sorted(r["ref"] for r in refs if r["verdict"] == "FAIL")
    A('<figcaption><b>Figure 1.</b> %d refs: %d FAIL, %d CANNOT DETERMINE, %d PASS. '
      'F = FAIL, ? = CANNOT DETERMINE, P = PASS. The FAIL block at the head of each row is, '
      'in this run: %s. That list is read out of the same data as the cells, so it cannot drift '
      'from the picture.</figcaption></figure>'
      % (len(refs),
         len(fails),
         sum(1 for r in refs if r["verdict"] == "CANNOT DETERMINE"),
         sum(1 for r in refs if r["verdict"] == "PASS"),
         ", ".join("<code>%s</code>" % e(f) for f in fails) or "nothing"))
    fail_refs = [r for r in refs if r["verdict"] == "FAIL"]
    if fail_refs:
        A('<div class="note"><b>Every FAIL on the shelf right now, and what closes each.</b> '
          'A FAIL is not a coverage gap — it is a broken record, and TRIAD.md gives each kind '
          'one remedy. Read out of this run, never typed:<ul>')
        for r in sorted(fail_refs, key=lambda r: r["ref"]):
            fr = [x for x in r["reasons"] if x["verdict"] == "FAIL"] or r["reasons"]
            cls = {x["class"] for x in fr}
            if cls == {"artifact_changed"}:
                fix = ("the ledgered artifact was re-measured and no later row names it. "
                       "APPEND a row for the new run — never edit the old one; the ledger is "
                       "append-only and the last row&rsquo;s hash is the one checked. The "
                       "artifact belongs to another lane, so that lane appends it.")
            elif cls == {"dangling"}:
                fix = ("a ref nothing on the shelf answers to. Create the folder, or correct "
                       "the ref to one that resolves.")
            else:
                fix = "see the reason rows in &sect;4."
            A('<li><code>%s</code> &mdash; %s. <em>%s</em><br><span class="trunc">%s</span></li>'
              % (e(r["ref"]), e(", ".join(sorted(cls)) or "unclassified"), fix,
                 e(trim(fr[0]["why"])[:220])))
        A('</ul></div>')
    bars = svg_class_bars(refs, by_class, CLASSES)
    if bars:
        A('<figure><div class="dia">%s</div>' % bars)
        A('<figcaption><b>Figure 2.</b> How many <em>refs</em> carry each defect class — not '
          'how many reason rows, which is the larger number in the bar above (%d rows across %d '
          'refs), because one ref can carry five rows of one class. The shelf has a few kinds of '
          'problem repeated, not %d separate ones.</figcaption></figure>'
          % (n_rows, len({r["ref"] for r in refs if r["reasons"]}), n_rows))
    A('</section>')

    A('<section id="counts"><h2><span class="n">2</span>The count</h2>')
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
    # WHAT the not-PASS rows are, not just how many. A bare "PASS went down"
    # invites the reader to guess a cause; the composition names it.
    A('<p class="lede">Composition of what is not PASS, by defect class \u2014 one folder can '
      'raise several rows, so these count rows, not folders:</p>')
    A('<div class="tablewrap"><table class="data"><thead><tr><th>defect class</th>'
      '<th>reason rows</th><th>refs affected</th></tr></thead><tbody>')
    for key, title, _d, _t in CLASSES + [("other", "Other", "", None)]:
        rows = by_class.get(key) or []
        if not rows:
            continue
        A('<tr><td>%s</td><td class="num">%d</td><td class="num">%d</td></tr>'
          % (e(title), len(rows), len({r["ref"] for r, _x in rows})))
    A('</tbody></table></div>')
    only_sup = [r for r in refs if r["verdict"] != "PASS" and r["reasons"]
                and all(x["class"] == "superseded_row" for x in r["reasons"])]
    if only_sup:
        A('<div class="note"><b>%d of the not-PASS refs have no gap in them.</b> Their only '
          'reasons are superseded ledger rows \u2014 an artifact was re-measured and a later row '
          'names it, so the earlier row is reported rather than deleted. The current measurement '
          'passed. Nothing inside those folders closes this; it is what an append-only ledger '
          'costs, and it is the price of being able to check that nobody edited one. They are: '
          '%s.</div>'
          % (len(only_sup), ", ".join("<code>%s</code>" % e(r["ref"]) for r in only_sup)))
    A('</section>')

    A('<section id="classes"><h2><span class="n">3</span>By defect class</h2>')
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
                 e(x.get("why_full") or trim(x["why"]))))   # whole sentence: section 2 never cuts
        A('</div>')
    A('</section>')

    A('<section id="refs"><h2><span class="n">4</span>Every ref</h2>')
    A('<p class="lede">Assemblies first, then connections, then parts; within each, whatever is '
      'not PASS comes first. The reason column is the checker’s own words. Where a folder wrote a '
      'paragraph the cell is cut at the last whole word before %d characters and the cut is MARKED '
      'in the row, with the number of characters dropped — an unmarked truncation reads as if the '
      'folder had stopped there. Section 2 above truncates nothing, and '
      '<code>out/laneT/shelf-status.json</code> carries every sentence whole.</p>' % TRUNC_AT)
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
        why = why_cell(r["reasons"])
        A('<tr%s><td><span class="chip %s">%s</span></td>'
          '<td class="ref"><a href="%s"><code>%s</code></a></td>'
          '<td class="mono" style="font-size:11.5px;color:var(--ink-2)">%s</td><td class="why">%s</td></tr>'
          % (' class="pass"' if r["verdict"] == "PASS" else "",
             CHIP[r["verdict"]], e(r["verdict"]), e(folder_of(r["ref"])), e(r["ref"]),
             e(r["meta"]), why))
    A('</tbody></table></div></section>')

    A('<section id="method"><h2><span class="n">5</span>Method</h2>')
    A('<pre class="code">export CE_TRIAD_ROOT="%s:%s"\n%s check --all\npython3 tools/gen_shelf_status.py            # regenerate this page\npython3 tools/gen_shelf_status.py --verify   # is it still true? exit 0 CURRENT / 1 STALE</pre>'
      % (e(root), e(WORKSHOP), e(os.path.relpath(TRIAD, REPO))))
    A('<p><b>Where a sentence was cut, and by whom.</b> <code>bin/triad</code> prints a folder\u2019s own <code>why</code> as <code>[:400]</code> (<code>bin/_triadlib.py:1482</code>) \u2014 400 characters, no marker, so its output cannot tell a folder that stopped there from one that was cut. That is where fragments like \u201c\u2026so the frame\u201d came from, not from this page. The whole sentence is on disk in the folder\u2019s own record, so this generator reads it back, checks the checker\u2019s text is a prefix of it, and prints the full sentence in section 2. Section 3\u2019s narrow column still cuts, at the last whole word before %d characters, and says so in the row with the number of characters dropped and the file that holds the rest. %d of the %d reason rows that quote a folder were recovered this way; where the prefix did not match, the checker\u2019s words stand and nothing is claimed about what follows them.</p>' % (TRUNC_AT, recovered_n, recoverable_n))
    A('<p>The checker is <code>bin/triad</code> in the ce-workshop root, shared by all three '
      'triad systems; its contract is <code>TRIAD.md</code>. This page parses its stdout and '
      'renders it. It re-grades nothing and it never softens a verdict: where a folder says '
      'CANNOT DETERMINE about itself, that sentence is reproduced here verbatim, because '
      '“coverage is part of the verdict” and a reader who cannot see the folder’s '
      'own doubt cannot act on it.</p>')
    A('<p>Machine-readable output, regenerated with the page: '
      '<code>out/laneT/shelf-status.json</code> — every ref, every reason, its defect class '
      'and the file it was raised against.</p>')
    A('<div class="note"><b>This page is a SNAPSHOT, and it goes stale.</b> The shelf is written '
      'by many hands at once; a folder created after the timestamp above is not on this page and '
      'its verdict is not in these counts. Nothing regenerates the page on its own. To find out '
      'whether what you are reading is still true, ask it: '
      '<code>python3 tools/gen_shelf_status.py --verify</code> re-runs the checker and prints '
      'CURRENT or STALE with the difference, exit 0 or 1, writing nothing. '
      '<code>python3 tools/gen_shelf_status.py</code> then brings it up to date.</div>')
    A('<h3>What <code>--verify</code> compares, and what it used to miss</h3>')
    n_tail = sum(1 for r in refs for x in r["reasons"] if x.get("dropped_by_checker"))
    tail_chars = sum(x.get("dropped_by_checker") or 0 for r in refs for x in r["reasons"])
    tail_refs = len({r["ref"] for r in refs for x in r["reasons"]
                     if x.get("dropped_by_checker")})
    A('<p>It builds a SHA-256 digest from a live run of the checker over <em>every field this '
      'page renders</em> — each ref name, its verdict, and for each of its reason rows the '
      'row\u2019s own verdict, its defect class, the file the checker raised it against, and the '
      'folder\u2019s WHOLE sentence (<code>why_full</code>, not the checker\u2019s 400-character '
      'cut) — sorted and canonically encoded, and compares it with the same digest recomputed '
      'from the committed <code>out/laneT/shelf-status.json</code>. Recomputed, not read: a digest '
      'stored in the file could be edited to certify a page that does not match it. This run\u2019s '
      'digest is <code>%s</code>, printed in the header above and in the JSON as '
      '<code>fingerprint_sha256</code>. When it differs, <code>--verify</code> names every ref '
      'whose verdict moved, in which direction, and every ref whose reasons changed.</p>'
      % e(fingerprint(refs)))
    A('<div class="note"><b>A measured defect in this generator, and the fix.</b> Until '
      '2026-09-03 <code>--verify</code> compared only three totals — <code>checked</code>, '
      '<code>pass</code>, <code>not_pass</code> — plus the set of ref names. Those are blind to '
      'the movement that matters most: a ref going CANNOT DETERMINE &rarr; FAIL leaves '
      '<code>not_pass</code> identical. Measured live: with the page written 2026-09-03 04:06 on '
      'disk, <code>--verify</code> printed <code>CURRENT … checked 64 PASS 17 not-PASS 47</code> '
      'and exited 0, while the live shelf held FAIL 5 against the page’s 3 and the two FAIL '
      'sets had ZERO refs in common — the page named <code>part:microduck-neck-plate</code>, '
      '<code>part:microduck-shin</code> and '
      '<code>part:microduck-upper-leg-rigidity-plate</code>; the shelf named the five head '
      'folders. The page was materially wrong about which folders FAIL and its only staleness '
      'detector could not see it. A detector that cannot go red is a decoration. It now compares '
      'the digest above and, on the same pair of files, printed STALE with all eight verdict '
      'moves named.</div>')
    A('<div class="note"><b>The same hole, second half \u2014 measured and closed the same day.</b> '
      'That first repair hashed the checker\u2019s <code>why</code> string only. But '
      '<code>bin/_triadlib.py:1482</code> cuts that string at 400 characters, and section&nbsp;4 '
      'of this page prints <code>why_full</code>, the whole sentence read back from the '
      'folder\u2019s own record. Measured on this run: <b>%d of the %d reason rows</b>, across '
      '<b>%d refs</b>, carry a tail the checker dropped \u2014 <b>%s characters</b> in all. Every '
      'one of those characters is printed on this page and none of them was in the digest, so a '
      'folder could rewrite the second half of its own reason and <code>--verify</code> would '
      'still say CURRENT. Neither was a reason row\u2019s own verdict (a row going CANNOT '
      'DETERMINE&nbsp;&rarr;&nbsp;FAIL under a ref whose overall verdict does not move), nor '
      '<code>where</code> (the same complaint raised against a different file). All four fields '
      'are in the digest now. Proved by deliberate breakage on copies of this JSON, checker run '
      'live each time: <b>(A)</b> two characters changed at offset 600 of one '
      '<code>why_full</code> \u2014 old digest <code>c5b0c5865cc2</code> UNCHANGED, new digest '
      'moved, STALE, exit&nbsp;1; <b>(B)</b> one reason row CANNOT DETERMINE&nbsp;&rarr;&nbsp;FAIL '
      'with the ref verdict and all three totals untouched \u2014 old digest UNCHANGED, new moved, '
      'STALE, exit&nbsp;1; <b>(C)</b> one <code>where</code> repointed at another file \u2014 old '
      'digest UNCHANGED, new moved, STALE, exit&nbsp;1; <b>the untouched control</b> \u2014 '
      'CURRENT, exit&nbsp;0. A detector is only worth what you have watched it catch.</div>'
      % (n_tail, n_rows, tail_refs, "{:,}".format(tail_chars).replace(",", "\u2009")))
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
    ap.add_argument("--verify", action="store_true",
                    help="re-run the checker and compare it with the committed JSON. Prints "
                         "CURRENT or STALE and the difference; writes nothing. Exit 0 current, "
                         "1 stale, 2 the checker or the JSON could not be read.")
    a = ap.parse_args(argv)

    text, code = run_check(a.root)
    refs, totals = parse(text)
    recovered, recoverable = attach_full_why(refs, a.root)
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
           "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
           "command": "bin/triad check --all", "checker_exit_code": code,
           "totals": totals, "refs": refs,
           "fingerprint_sha256": fingerprint(refs),
           "fingerprint_covers": "every ref name, its verdict, and for every reason row "
                                 "printed for it: the row's own verdict, its defect class, "
                                 "where the checker found it, and the folder's WHOLE sentence "
                                 "(why_full, not the checker's 400-character cut) — sorted, "
                                 "canonically encoded, SHA-256. --verify recomputes it from a "
                                 "live run and compares.",
           "verdict_counts": verdict_counts(refs)}
    if a.verify:
        try:
            old = json.load(open(a.json, encoding="utf-8"))
        except Exception as exc:                              # noqa: BLE001
            print("CANNOT DETERMINE: %s cannot be read (%s)" % (a.json, exc), file=sys.stderr)
            return 2
        o, n = old.get("totals") or {}, totals
        old_ref_list = old.get("refs", [])
        # The digest is recomputed from the committed JSON's own refs rather than
        # read out of it, so a file written before fingerprints existed still
        # verifies, and so a hand-edited digest cannot certify a page.
        old_fp, new_fp = fingerprint(old_ref_list), fingerprint(refs)
        keys = ("checked", "pass", "not_pass")
        diff = [(k, o.get(k), n.get(k)) for k in keys if o.get(k) != n.get(k)]
        oldv, newv = verdict_counts(old_ref_list), verdict_counts(refs)
        vdiff = [(k, oldv.get(k, 0), newv.get(k, 0)) for k in VERDICTS
                 if oldv.get(k, 0) != newv.get(k, 0)]
        old_by = {r["ref"]: r for r in old_ref_list}
        new_by = {r["ref"]: r for r in refs}
        added = sorted(set(new_by) - set(old_by))
        gone = sorted(set(old_by) - set(new_by))
        moved, reworded = [], []
        for ref in sorted(set(old_by) & set(new_by)):
            ov_, nv_ = old_by[ref]["verdict"], new_by[ref]["verdict"]
            if ov_ != nv_:
                moved.append((ref, ov_, nv_))
                continue
            os_ = sorted(reason_key(x) for x in old_by[ref]["reasons"])
            ns_ = sorted(reason_key(x) for x in new_by[ref]["reasons"])
            if os_ != ns_:
                reworded.append((ref, len(os_), len(ns_)))
        if old_fp == new_fp:
            print("CURRENT  page written %s  checked %d  PASS %d  not-PASS %d  "
                  "digest %s" % (old.get("date"), n["checked"], n["pass"],
                                 n["not_pass"], new_fp[:16]))
            nfull = sum(1 for r in refs for x in r["reasons"]
                        if x.get("dropped_by_checker"))
            print("         the digest covers every ref, its verdict, and per reason row its "
                  "verdict, class, where and WHOLE sentence — %d refs, %d reason rows, "
                  "%d of them longer than the checker's 400-character cut." %
                  (len(refs), sum(len(r["reasons"]) for r in refs), nfull))
            return 0
        print("STALE    page written %s" % old.get("date"))
        print("  digest    page %s  ->  now %s" % (old_fp[:16], new_fp[:16]))
        for k, ov_, nv_ in diff:
            print("  %-9s page %s  ->  now %s" % (k, ov_, nv_))
        for k, ov_, nv_ in vdiff:
            print("  %-17s page %s  ->  now %s" % (k, ov_, nv_))
        for ref in added:
            print("  NEW on the shelf, not on the page: %s" % ref)
        for ref in gone:
            print("  on the page, no longer on the shelf: %s" % ref)
        for ref, ov_, nv_ in moved:
            print("  VERDICT MOVED  %-52s page %s  ->  now %s" % (ref, ov_, nv_))
        for ref, on_, nn_ in reworded:
            print("  reasons changed %-51s page %d row(s)  ->  now %d" % (ref, on_, nn_))
        if not (diff or vdiff or added or gone or moved or reworded):
            print("  the totals and every verdict agree, but a reason SENTENCE differs — "
                  "the checker's wording or a folder's own words changed.")
        print("  fix: python3 tools/gen_shelf_status.py")
        return 1
    os.makedirs(os.path.dirname(a.json), exist_ok=True)
    json.dump(doc, open(a.json, "w", encoding="utf-8"), indent=1)
    open(a.html, "w", encoding="utf-8").write(render(refs, totals, before, code, a.root, recovered, recoverable))
    print("checked %(checked)d  PASS %(pass)d  not-PASS %(not_pass)d" % totals)
    print("wrote", os.path.relpath(a.json, REPO), "and", os.path.relpath(a.html, REPO))
    return code


if __name__ == "__main__":
    sys.exit(main())
