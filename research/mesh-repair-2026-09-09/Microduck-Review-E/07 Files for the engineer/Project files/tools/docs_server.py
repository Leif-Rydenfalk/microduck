#!/usr/bin/env python3
"""docs_server.py — the Microduck repository browser: halo's two-column sidebar
layout wearing this repo's own tools/doc.css ink.

Leif, 2026-09-03, verbatim: "I like the halo dock browser more but the styling
of themicroduck more with the white. redesign the microduck repository /
document browser to have this same clean sideview i like it a lot."

Usage:  python3 tools/docs_server.py [port] [repo-root]
        default port 8842, default root = the repo this file lives in.

Routes
  /                  the master dossier (RELEASE.html) inside the frame
  /b/<rel>           browse: an .html dossier inlined into the frame, a .md
                     rendered through tools/md2html.py, .json pretty-printed,
                     an image on its own page, a directory as record + gallery
                     + file table (drawing folders show their verdict)
  /<rel>             the file itself, at its real path — so `tools/doc.css`,
                     `out/render/x.png`, `../../tools/doc.css` all resolve
                     exactly as they do under a bare http.server today.
                     A directory here redirects to /b/<rel>/.
  /api/health        {"app": "microduck-doc-browser", ...}  (launchpad probe)
  /api/tree          the sidebar as JSON
  /llms.txt          this route list
Anything else answers 404 — that is the negative control in ceapp.toml.

The sidebar is DISCOVERED on every request by walking the filesystem one level
deep, so a dossier or a drawing folder that lands while this is running appears
without an edit here. Nothing in this file names a document; it names PLACES
(root *.html, docs/, out/drawings/<slug>/, out/<dir>/, ce-parts/<slug>/ ...)
and the one ordering preference for the dossiers that were listed on
2026-09-03, which is a sort key, not a filter.

Stdlib only. No import of halo's docs_server.py — read as a reference, never
coupled (TRIAD house rule 6).
"""
import html
import json
import mimetypes
import os
import re
import struct
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, quote

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.realpath(sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(HERE))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8842
MARKER = "microduck-doc-browser"
GITHUB = "https://github.com/Leif-Rydenfalk/microduck"

sys.path.insert(0, HERE)
try:
    import md2html  # the repo's own converter — reused, not reimplemented
except Exception as e:  # pragma: no cover
    md2html = None
    print("md2html unavailable:", e, file=sys.stderr)

# ------------------------------------------------------------------ constants
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", ".DS_Store", "trash"}
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg")
TEXT_EXT = (".txt", ".log", ".csv", ".tsv", ".py", ".xml", ".toml", ".sh", ".js",
            ".mjs", ".inp", ".dat", ".sta", ".cvg", ".yaml", ".yml", ".ini", ".gen.py")
RAW_ONLY_EXT = (".pdf", ".dxf", ".stl", ".step", ".stp", ".mp4", ".npz", ".zip",
                ".frd", ".12d", ".FCStd", ".fcstd", ".3mf", ".gcode")
# A sort preference for the dossiers Leif listed on 2026-09-03. Anything not
# in it still appears — after these, alphabetically. A key, not a filter.
DOSSIER_ORDER = ["RELEASE", "INDEX", "GOAL", "SPEC", "STATUS", "SIMULATION", "STRUCTURAL",
                 "ELECTRONICS-DATASHEET", "MANUFACTURING-PLAYBOOK", "COMPARISON",
                 "TEST-PLAN", "PCB-PACKAGE", "SOURCING", "RFQ", "BUILD-BOOK",
                 "HEAD-RECONSTRUCTION", "MOTION", "HEAD-MOTION", "LEG-MOTION",
                 "SHELF-STATUS", "TOOLCHAIN", "LOAD-BASIS-CORRECTION"]
RECORD_FILES = ("result.json", "component.json", "connection.json", "assembly.json",
                "report.json", "trust.json", "summary.json", "jigs.json")
FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:'
         'opsz,wght@8..60,400;8..60,600;8..60,700&family=Source+Sans+3:wght@400;600'
         '&family=IBM+Plex+Mono:wght@400;500&display=swap">')

# The frame's own ink: only what the sidebar, breadcrumb bar, gallery and
# folder table need. Reading typography is doc.css's, linked, never copied.
FRAME_CSS = """
  html,body{margin:0}
  body.mdb{display:flex;background:var(--paper,#ffffff);color:var(--ink,#1a1a1a);font-family:var(--serif,"Source Serif 4",Georgia,serif);font-size:16px;line-height:1.55}
  body.mdb>aside.nav{width:290px;flex:0 0 290px;height:100vh;overflow:auto;position:sticky;top:0;border-right:1px solid var(--line,#d7d3ca);padding:18px 14px 40px;font-family:var(--sans,"Source Sans 3",sans-serif)}
  body.mdb>aside.nav .nav-title{font-family:var(--sans);font-size:13px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--ink);margin:0 0 3px 10px}
  body.mdb>aside.nav .nav-title a{color:var(--ink);text-decoration:none;border:none}
  body.mdb>aside.nav .nav-sub{font-size:12px;color:var(--ink-2,#565656);margin:0 0 14px 10px}
  body.mdb>aside.nav .nav-sub code{font-family:var(--mono);font-size:11px}
  body.mdb>aside.nav .nav-sub a{color:var(--accent,#243b53);text-decoration:none;border:none}
  body.mdb>aside.nav details.nav-group{margin:0}
  body.mdb>aside.nav summary.nav-h{list-style:none;cursor:pointer;display:flex;justify-content:space-between;align-items:baseline;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-2,#565656);font-weight:600;margin:16px 0 4px;padding:0 8px 0 10px}
  body.mdb>aside.nav summary.nav-h::-webkit-details-marker{display:none}
  body.mdb>aside.nav summary.nav-h .n{font-family:var(--mono);font-size:10.5px;letter-spacing:0;font-weight:400;font-variant-numeric:tabular-nums}
  body.mdb>aside.nav details.nav-group:not([open]) summary.nav-h .n::after{content:" +"}
  body.mdb>aside.nav a.nav-a{display:flex;justify-content:space-between;align-items:baseline;gap:8px;padding:3px 8px 3px 10px;margin:0;border:none;border-left:2px solid transparent;color:var(--ink,#1a1a1a);text-decoration:none;font-size:13.5px;line-height:1.35;border-radius:0}
  body.mdb>aside.nav a.nav-a:hover{color:var(--accent,#243b53)}
  body.mdb>aside.nav a.nav-a.on{border-left-color:var(--accent,#243b53);font-weight:600;color:var(--ink)}
  body.mdb>aside.nav a.nav-a .t{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;min-width:0}
  body.mdb>aside.nav a.nav-a .v{flex:0 0 auto;font-size:9.5px;font-weight:600;letter-spacing:.06em;text-transform:uppercase}
  body.mdb>aside.nav a.nav-a .tier{flex:0 0 auto;font-family:var(--mono);font-size:10px;color:var(--ink-2)}
  .v.pass{color:var(--ready,#1c6b3c)} .v.cd{color:var(--partial,#8a5a00)} .v.fail{color:var(--no,#9a2b1e)} .v.none{color:var(--ink-2,#565656)}
  body.mdb>main.doc{flex:1;min-width:0;max-width:960px;padding:34px 46px 90px}
  body.mdb>main.doc .wrap{max-width:840px;margin:0;padding:0}
  body.mdb>main.doc header.top,body.mdb>main.doc header.hero{padding-top:6px}
  body.mdb>main.doc .bar{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;font-family:var(--sans);font-size:12px;color:var(--ink-2,#565656);margin:0 0 22px;padding:0 0 12px;border-bottom:1px solid var(--line,#d7d3ca)}
  body.mdb>main.doc .bar a{color:var(--ink-2);border:none;text-decoration:none}
  body.mdb>main.doc .bar a:hover{color:var(--accent)}
  body.mdb>main.doc .bar .crumbs span.sep{padding:0 6px;color:var(--line)}
  body.mdb>main.doc .bar .meta{font-family:var(--mono);font-size:11px;font-variant-numeric:tabular-nums;white-space:nowrap}
  body.mdb>main.doc .bar .meta a{color:var(--accent)}
  body.mdb>main.doc h1.fh{font-size:28px;margin:0 0 6px;line-height:1.15;font-weight:700}
  body.mdb>main.doc .fh-sub{color:var(--ink-2);max-width:42em;margin:0 0 18px;font-size:15px}
  body.mdb>main.doc .rec{border-top:1.5px solid var(--rule,#1a1a1a);border-bottom:1px solid var(--line);padding:10px 0 6px;margin:8px 0 22px}
  body.mdb>main.doc .rec.rec-head{border-bottom:none;padding-bottom:0;margin-bottom:10px}
  body.mdb>main.doc .rec .rec-v{font-family:var(--sans);font-size:11.5px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;margin-bottom:6px}
  body.mdb>main.doc .rec .rec-v .src{font-weight:400;letter-spacing:0;text-transform:none;color:var(--ink-2);margin-left:10px}
  body.mdb>main.doc .rec .rec-t{font-size:16px;margin:0 0 8px}
  body.mdb>main.doc .rec dl{display:grid;grid-template-columns:max-content 1fr;gap:3px 18px;margin:0;font-size:13.5px}
  body.mdb>main.doc .rec dt{font-family:var(--sans);font-size:11px;letter-spacing:.05em;text-transform:uppercase;color:var(--ink-2);padding-top:3px}
  body.mdb>main.doc .rec dd{margin:0;max-width:none}
  body.mdb>main.doc .rec dd.num{font-family:var(--mono);font-size:12.5px;font-variant-numeric:tabular-nums}
  body.mdb>main.doc .rec ul{margin:2px 0 0;padding-left:18px;font-size:13.5px}
  body.mdb>main.doc .rec p.why{font-size:13.5px;max-width:none;margin:6px 0 0;color:var(--ink)}
  body.mdb>main.doc .gal{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px;margin:8px 0 22px}
  body.mdb>main.doc .gal figure{margin:0;border:1px solid var(--line);background:#fff;padding:6px;border-radius:0}
  body.mdb>main.doc .gal figure a{border:none}
  body.mdb>main.doc .gal img{display:block;width:100%;height:170px;object-fit:contain;background:#fff;border:none}
  body.mdb>main.doc .gal figcaption{font-family:var(--sans);font-size:11.5px;color:var(--ink-2);margin-top:5px;overflow-wrap:anywhere}
  body.mdb>main.doc .gal figcaption .dim{font-family:var(--mono);font-size:10.5px;display:block}
  body.mdb>main.doc table.files{border-collapse:collapse;width:100%;font-size:13.5px;font-variant-numeric:tabular-nums;margin:8px 0 20px}
  body.mdb>main.doc table.files th{font-family:var(--sans);font-weight:600;font-size:11px;letter-spacing:.05em;text-transform:uppercase;color:var(--ink-2);text-align:left;padding:7px 12px 6px 0;border-bottom:1px solid var(--rule,#1a1a1a);border-top:1.5px solid var(--rule,#1a1a1a)}
  body.mdb>main.doc table.files td{padding:5px 12px 5px 0;border-bottom:1px solid var(--line);vertical-align:top}
  body.mdb>main.doc table.files tr:last-child td{border-bottom:1.5px solid var(--rule,#1a1a1a)}
  body.mdb>main.doc table.files td.num{text-align:right;font-family:var(--mono);font-size:12.5px;white-space:nowrap}
  body.mdb>main.doc table.files td.k{font-family:var(--sans);font-size:11.5px;color:var(--ink-2);text-transform:uppercase;letter-spacing:.04em;white-space:nowrap}
  body.mdb>main.doc table.files a{border:none}
  body.mdb>main.doc .imgpage img{max-width:100%;display:block;border:1px solid var(--line);background:#fff}
  body.mdb>main.doc pre.json,body.mdb>main.doc pre.text{font-family:var(--mono);font-size:12.5px;line-height:1.55;background:var(--figbg,#fbfaf7);border:1px solid var(--line);padding:12px 15px;overflow-x:auto;white-space:pre;margin:8px 0 20px;font-variant-numeric:tabular-nums}
  body.mdb>main.doc pre.json .k{color:var(--ink-2)} body.mdb>main.doc pre.json .n{color:var(--accent)} body.mdb>main.doc pre.json .s{color:var(--ink)} body.mdb>main.doc pre.json .b{color:var(--partial)}
  body.mdb>main.doc .empty{color:var(--ink-2);font-style:italic}
  @media(max-width:760px){body.mdb{display:block}body.mdb>aside.nav{width:auto;height:auto;position:static;border-right:none;border-bottom:1px solid var(--line)}}
"""

# ------------------------------------------------------------------ helpers
def esc(s):
    return html.escape(str(s), quote=True)


def safe(rel):
    """Real path under ROOT for a URL-relative path, or None."""
    rel = rel.strip("/")
    fp = os.path.realpath(os.path.join(ROOT, rel))
    if fp != ROOT and not fp.startswith(ROOT + os.sep):
        return None
    parts = os.path.relpath(fp, ROOT).split(os.sep)
    if any(p in SKIP_DIRS for p in parts if p != "."):
        return None
    return fp


def relof(fp):
    r = os.path.relpath(fp, ROOT)
    return "" if r == "." else r


def bhref(rel, is_dir=False):
    rel = rel.strip("/")
    u = "/b/" + quote(rel)
    if is_dir and rel:
        u += "/"
    return u if rel else "/b/"


def rawhref(rel):
    return "/" + quote(rel.strip("/"))


def load_json(fp, limit=4 << 20):
    try:
        if os.path.getsize(fp) > limit:
            return None
        with open(fp, encoding="utf-8", errors="replace") as f:
            return json.load(f)
    except Exception:
        return None


def verdict_class(v):
    if not isinstance(v, str):
        return None
    u = v.strip().upper()
    # "SHEET FAIL · BUILD PASS" — the SHEET half is the one a reader must be
    # shown, so the colour follows it.
    if u.startswith("SHEET "):
        u = u[len("SHEET "):]
    if u.startswith("PASS"):
        return "pass"
    if u.startswith("FAIL"):
        return "fail"
    if u.startswith("CANNOT"):
        return "cd"
    return "none"


def verdict_text(v):
    u = v.strip().upper()
    if u.startswith("SHEET "):
        u = u[len("SHEET "):]
    if u.startswith("CANNOT"):
        return "C/D"
    return u.split()[0] if u else ""


def record_of(d):
    """(verdict, title, trust tier, source file) for a folder that states one."""
    for name in ("result.json", "component.json", "connection.json", "assembly.json",
                 "report.json", "summary.json"):
        fp = os.path.join(d, name)
        if os.path.isfile(fp):
            j = load_json(fp, 2 << 20)
            if not isinstance(j, dict):
                continue
            rec = j.get("record") if isinstance(j.get("record"), dict) else j
            if rec.get("sheet_verdict") or rec.get("build_verdict"):
                v = ("SHEET %s · BUILD %s"
                     % (rec.get("sheet_verdict") or "CANNOT DETERMINE",
                        rec.get("build_verdict") or "CANNOT DETERMINE"))
            else:
                v = rec.get("verdict") or j.get("verdict")
            t = rec.get("title") or j.get("title")
            if v or t:
                tier = None
                tf = os.path.join(d, "current", "trust.json")
                if os.path.isfile(tf):
                    tj = load_json(tf)
                    if isinstance(tj, dict):
                        tier = (tj.get("record") or {}).get("tier")
                return v, t, tier, name
    return None, None, None, None


_rev = {"t": 0, "v": ""}


def revision():
    if time.time() - _rev["t"] < 10:
        return _rev["v"]
    v = ""
    try:
        head = open(os.path.join(ROOT, ".git", "HEAD")).read().strip()
        if head.startswith("ref: "):
            rf = os.path.join(ROOT, ".git", head[5:])
            if os.path.isfile(rf):
                v = open(rf).read().strip()[:7]
            else:
                pr = os.path.join(ROOT, ".git", "packed-refs")
                if os.path.isfile(pr):
                    for ln in open(pr):
                        if ln.strip().endswith(head[5:]):
                            v = ln.split()[0][:7]
        else:
            v = head[:7]
    except Exception:
        v = ""
    if not v:
        try:
            v = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                               capture_output=True, text=True, timeout=5).stdout.strip()
        except Exception:
            v = ""
    _rev.update(t=time.time(), v=v or "no-git")
    return _rev["v"]


def png_size(fp):
    try:
        with open(fp, "rb") as f:
            h = f.read(26)
        if h[:8] == b"\x89PNG\r\n\x1a\n":
            w, hh = struct.unpack(">II", h[16:24])
            return w, hh
    except Exception:
        pass
    return None


def fmt_size(n):
    for unit in ("B", "kB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return ("%d %s" % (n, unit)) if unit == "B" else ("%.1f %s" % (n, unit))
        n /= 1024.0


def listdir(d):
    try:
        names = sorted(os.listdir(d), key=lambda s: s.lower())
    except OSError:
        return [], []
    dirs, files = [], []
    for n in names:
        if n in SKIP_DIRS or n.startswith("."):
            continue
        p = os.path.join(d, n)
        (dirs if os.path.isdir(p) else files).append(n)
    return dirs, files


# ------------------------------------------------------------------ the tree
def build_groups():
    """Sidebar groups, discovered now. Each entry: (label, rel, is_dir, verdict, tier)."""
    groups = []

    def dossiers():
        _, files = listdir(ROOT)
        htmls = [f for f in files if f.lower().endswith(".html")]
        stems = {os.path.splitext(f)[0] for f in htmls}
        mds = [f for f in files if f.lower().endswith(".md") and os.path.splitext(f)[0] not in stems]
        order = {s: i for i, s in enumerate(DOSSIER_ORDER)}
        htmls.sort(key=lambda f: (order.get(os.path.splitext(f)[0], 999), f))
        out = [(os.path.splitext(f)[0], f, False, None, None) for f in htmls]
        out += [(os.path.splitext(f)[0] + " (md)", f, False, None, None) for f in sorted(mds)]
        return out

    groups.append(("Dossiers", "", dossiers(), True))

    def folder_docs(sub):
        d = os.path.join(ROOT, sub)
        if not os.path.isdir(d):
            return []
        dirs, files = listdir(d)
        htmls = [f for f in files if f.lower().endswith(".html")]
        stems = {os.path.splitext(f)[0] for f in htmls}
        mds = [f for f in files if f.lower().endswith(".md") and os.path.splitext(f)[0] not in stems]
        out = [(os.path.splitext(f)[0], sub + "/" + f, False, None, None) for f in sorted(htmls)]
        out += [(os.path.splitext(f)[0] + " (md)", sub + "/" + f, False, None, None) for f in sorted(mds)]
        out += [(dd + "/", sub + "/" + dd, True, None, None) for dd in dirs if dd not in ("__pycache__",)]
        return out

    groups.append(("docs", "docs", folder_docs("docs"), True))

    # drawings: one entry per sheet folder, verdict from its result.json
    dr = os.path.join(ROOT, "out", "drawings")
    if os.path.isdir(dr):
        dirs, files = listdir(dr)
        ents = [(os.path.splitext(f)[0], "out/drawings/" + f, False, None, None)
                for f in files if f.lower().endswith(".html")]
        for dd in dirs:
            v, _, _, _ = record_of(os.path.join(dr, dd))
            label = dd[len("microduck-"):] if dd.startswith("microduck-") else dd
            ents.append((label, "out/drawings/" + dd, True, v, None))
        groups.append(("Drawings", "out/drawings", ents, False))

    # every other out/<dir>: the evidence folders
    od = os.path.join(ROOT, "out")
    if os.path.isdir(od):
        dirs, files = listdir(od)
        ents = []
        for dd in dirs:
            if dd == "drawings":
                continue
            v, _, _, _ = record_of(os.path.join(od, dd))
            ents.append((dd, "out/" + dd, True, v, None))
        for f in files:
            ents.append((f, "out/" + f, False, None, None))
        groups.append(("Evidence · out/", "out", ents, True))

    # electronics / wiring / spec / reference and the remaining top-level dirs
    for sub in ("electronics", "wiring", "spec", "reference", "images"):
        d = os.path.join(ROOT, sub)
        if not os.path.isdir(d):
            continue
        dirs, files = listdir(d)
        ents = [(sub + "/", sub, True, None, None)]
        for f in files:
            lf = f.lower()
            if lf.endswith((".html", ".svg", ".md", ".json")) and sub != "images":
                if lf.endswith(".md") and os.path.splitext(f)[0] + ".html" in files:
                    continue
                ents.append((f, sub + "/" + f, False, None, None))
        for dd in dirs:
            if dd == "__pycache__":
                continue
            v, _, _, _ = record_of(os.path.join(d, dd))
            ents.append((dd + "/", sub + "/" + dd, True, v, None))
        groups.append((sub, sub, ents, sub in ("electronics", "wiring")))

    other = []
    dirs, _ = listdir(ROOT)
    named = {"docs", "out", "electronics", "wiring", "spec", "reference", "images",
             "ce-parts", "ce-connections", "ce-assemblies", "tools", "trash"}
    for dd in dirs:
        if dd not in named:
            other.append((dd + "/", dd, True, None, None))
    other.append(("tools/", "tools", True, None, None))
    groups.append(("Folders", "", other, False))

    # the triad shelf
    for sub, label in (("ce-parts", "Parts · ce-parts"), ("ce-connections", "Connections · ce-connections"),
                       ("ce-assemblies", "Assemblies · ce-assemblies")):
        d = os.path.join(ROOT, sub)
        if not os.path.isdir(d):
            continue
        dirs, _ = listdir(d)
        ents = []
        for dd in dirs:
            v, _, tier, _ = record_of(os.path.join(d, dd))
            ents.append((dd, sub + "/" + dd, True, v, tier))
        groups.append((label, sub, ents, sub == "ce-assemblies"))
    return groups


def nav_html(cur):
    cur = cur.strip("/")
    parts = ['<div class="nav-title"><a href="/">Microduck</a></div>',
             '<div class="nav-sub"><code>%s</code> · %s · <a href="%s" target="_blank">GitHub &#8599;</a></div>'
             % (esc(revision()), MARKER, GITHUB)]
    for label, base, ents, default_open in build_groups():
        inside = any(cur == e[1].strip("/") or (e[2] and cur.startswith(e[1].strip("/") + "/")) for e in ents)
        if base and cur.startswith(base):
            inside = True
        is_open = default_open or inside
        parts.append('<details class="nav-group"%s><summary class="nav-h"><span>%s</span><span class="n">%d</span></summary>'
                     % (" open" if is_open else "", esc(label), len(ents)))
        for lab, rel, is_dir, v, tier in ents:
            on = " on" if cur == rel.strip("/") or (is_dir and cur.startswith(rel.strip("/") + "/") and not inside_deeper(ents, cur, rel)) else ""
            tail = ""
            if v:
                tail = '<span class="v %s">%s</span>' % (verdict_class(v), esc(verdict_text(v)))
            if tier:
                tail = '<span class="tier">%s</span>' % esc(tier) + tail
            parts.append('<a class="nav-a%s" href="%s"><span class="t">%s</span>%s</a>'
                         % (on, bhref(rel, is_dir), esc(lab), tail))
        parts.append("</details>")
    return "".join(parts)


def inside_deeper(ents, cur, rel):
    """True if another entry in this group is a more specific match for cur."""
    r = rel.strip("/")
    for _, other, is_dir, _, _ in ents:
        o = other.strip("/")
        if o != r and len(o) > len(r) and (cur == o or (is_dir and cur.startswith(o + "/"))):
            return True
    return False


# ------------------------------------------------------------------ the frame
def frame(title, rel, body, head_extra="", is_dir=False, fp=None):
    rel = rel.strip("/")
    crumbs = ['<a href="/b/">microduck</a>']
    acc = []
    segs = [s for s in rel.split("/") if s]
    for i, s in enumerate(segs):
        acc.append(s)
        last = i == len(segs) - 1
        if last:
            crumbs.append("<span>%s</span>" % esc(s))
        else:
            crumbs.append('<a href="%s">%s</a>' % (bhref("/".join(acc), True), esc(s)))
    meta = []
    if fp and os.path.isfile(fp):
        st = os.stat(fp)
        meta.append('<a href="%s" target="_blank">raw &#8599;</a>' % rawhref(rel))
        meta.append(esc(fmt_size(st.st_size)))
        meta.append(time.strftime("%Y-%m-%d %H:%M", time.localtime(st.st_mtime)))
    elif fp and os.path.isdir(fp):
        d, f = listdir(fp)
        meta.append("%d folders · %d files" % (len(d), len(f)))
    bar = ('<div class="bar"><div class="crumbs">%s</div><div class="meta">%s</div></div>'
           % ('<span class="sep">/</span>'.join(crumbs), " · ".join(meta)))
    return ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            "<meta name=\"generator\" content=\"%s\">\n<title>%s — Microduck</title>\n%s\n"
            "<link rel=\"stylesheet\" href=\"/tools/doc.css\">\n%s\n<style>%s</style>\n</head>\n"
            "<body class=\"mdb\">\n<aside class=\"nav\">%s</aside>\n<main class=\"doc\">%s\n%s\n</main>\n"
            "<script>(function(){var a=document.querySelector('aside.nav a.nav-a.on');if(a){var s=a.closest('aside');"
            "if(s&&a.offsetTop>s.clientHeight-60){s.scrollTop=a.offsetTop-s.clientHeight/2;}}})();</script>\n</body>\n</html>\n"
            % (MARKER, esc(title), FONTS, head_extra, FRAME_CSS, nav_html(rel), bar, body))


# ------------------------------------------------------------------ documents
_ATTR = re.compile(r'\b(href|src|poster|data)=(["\'])([^"\']*)\2', re.I)


def rewrite_links(doc_html, doc_dir):
    """Relative hrefs/srcs resolved against the document's folder. Documents and
    folders route back into the frame; everything else goes to its real path."""
    def sub(m):
        attr, q, url = m.group(1), m.group(2), m.group(3)
        u = url.strip()
        if not u or u.startswith(("#", "/", "http:", "https:", "data:", "mailto:", "javascript:", "//")):
            return m.group(0)
        path, _, frag = u.partition("#")
        path, _, query = path.partition("?")
        target = os.path.normpath(os.path.join(doc_dir, unquote(path))) if path else doc_dir
        if target == ".":
            target = ""
        if target.startswith(".."):
            return m.group(0)
        fp = os.path.join(ROOT, target)
        lower = target.lower()
        if attr.lower() == "href" and (os.path.isdir(fp) or lower.endswith((".html", ".md", ".json"))):
            new = bhref(target, os.path.isdir(fp))
        else:
            new = rawhref(target)
        if query:
            new += "?" + query
        if frag:
            new += "#" + frag
        return "%s=%s%s%s" % (attr, q, new, q)
    return _ATTR.sub(sub, doc_html)


_HEAD = re.compile(r"<head[^>]*>(.*?)</head>", re.S | re.I)
_BODY = re.compile(r"<body[^>]*>(.*?)</body>", re.S | re.I)
_TITLE = re.compile(r"<title>(.*?)</title>", re.S | re.I)
_DROP = re.compile(r"<title\b[^>]*>.*?</title>|<meta\b[^>]*>", re.S | re.I)


def split_document(text):
    """(title, head extras, body) of a standalone HTML document."""
    title = ""
    m = _TITLE.search(text)
    if m:
        title = html.unescape(re.sub(r"\s+", " ", m.group(1)).strip())
    hm = _HEAD.search(text)
    head_extra = _DROP.sub("", hm.group(1)) if hm else ""
    bm = _BODY.search(text)
    body = bm.group(1) if bm else (text[hm.end():] if hm else text)
    return title, head_extra, body


def page_html(fp, rel):
    text = open(fp, encoding="utf-8", errors="replace").read()
    return framed_document(text, rel, fp)


def framed_document(text, rel, fp):
    title, head_extra, body = split_document(text)
    doc_dir = os.path.dirname(rel)
    head_extra = rewrite_links(head_extra, doc_dir)
    body = rewrite_links(body, doc_dir)
    return frame(title or os.path.basename(rel), rel, body, head_extra, fp=fp)


def page_md(fp, rel):
    src = open(fp, encoding="utf-8", errors="replace").read()
    if md2html is None:
        return frame(os.path.basename(rel), rel, '<pre class="text">%s</pre>' % esc(src), fp=fp)
    title = "Microduck — " + os.path.splitext(os.path.basename(rel))[0].replace("-", " ").title()
    return framed_document(md2html.convert(src, title), rel, fp)


_JSON_TOK = re.compile(r'("(?:\\.|[^"\\])*")(\s*:)?|(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)|\b(true|false|null)\b')


def json_pretty(text):
    try:
        text = json.dumps(json.loads(text), indent=2, ensure_ascii=False)
    except Exception:
        pass

    def tok(m):
        if m.group(1) is not None:
            s = esc(m.group(1))
            return ('<span class="k">%s</span>%s' % (s, m.group(2))) if m.group(2) else '<span class="s">%s</span>' % s
        if m.group(3) is not None:
            return '<span class="n">%s</span>' % m.group(3)
        return '<span class="b">%s</span>' % m.group(4)
    # escape non-token text: tokenise on the raw text, escaping the gaps
    out, pos = [], 0
    for m in _JSON_TOK.finditer(text):
        out.append(esc(text[pos:m.start()]))
        out.append(tok(m))
        pos = m.end()
    out.append(esc(text[pos:]))
    return "".join(out)


def page_json(fp, rel):
    n = os.path.getsize(fp)
    if n > (2 << 20):
        body = ('<h1 class="fh">%s</h1><p class="fh-sub">%s — too large to pretty-print here; '
                '<a href="%s">open the file itself</a>.</p>' % (esc(os.path.basename(rel)), esc(fmt_size(n)), rawhref(rel)))
        return frame(os.path.basename(rel), rel, body, fp=fp)
    text = open(fp, encoding="utf-8", errors="replace").read()
    body = '<h1 class="fh">%s</h1><pre class="json">%s</pre>' % (esc(os.path.basename(rel)), json_pretty(text))
    return frame(os.path.basename(rel), rel, body, fp=fp)


def page_text(fp, rel):
    n = os.path.getsize(fp)
    text = open(fp, encoding="utf-8", errors="replace").read(512 << 10)
    note = "" if n <= (512 << 10) else '<p class="empty">first 512 kB of %s shown; <a href="%s">raw</a> for the whole file.</p>' % (esc(fmt_size(n)), rawhref(rel))
    body = '<h1 class="fh">%s</h1>%s<pre class="text">%s</pre>' % (esc(os.path.basename(rel)), note, esc(text))
    return frame(os.path.basename(rel), rel, body, fp=fp)


def page_image(fp, rel):
    dim = png_size(fp)
    sub = ("%d × %d px · " % dim if dim else "") + fmt_size(os.path.getsize(fp))
    body = ('<h1 class="fh">%s</h1><p class="fh-sub mono">%s</p><div class="imgpage"><a href="%s" target="_blank">'
            '<img src="%s" alt="%s"></a></div>' % (esc(os.path.basename(rel)), esc(sub), rawhref(rel), rawhref(rel), esc(rel)))
    return frame(os.path.basename(rel), rel, body, fp=fp)


# ------------------------------------------------------------------ folders
def render_record(d, rel):
    """The folder's own statement — result.json / component.json / trust.json — as a
    framed note: verdict, title, scalar fields, lists. Generic: it prints what the
    file says and names the file; it invents no field. Returns (head, details)
    so the folder page can put its pictures between the verdict and the fields."""
    heads, blocks = [], []
    for name in RECORD_FILES:
        fp = os.path.join(d, name)
        if not os.path.isfile(fp):
            if name == "trust.json":
                fp = os.path.join(d, "current", "trust.json")
                if not os.path.isfile(fp):
                    continue
            else:
                continue
        j = load_json(fp, 2 << 20)
        if not isinstance(j, dict):
            continue
        rec = j.get("record") if isinstance(j.get("record"), dict) else j
        # A DRAWING FOLDER HAS TWO VERDICTS AND THE SHEET ONE IS THE ANSWER.
        # out/drawings/<slug>/result.json publishes build_verdict (the part
        # built) and sheet_verdict (a machinist can cut from this sheet,
        # A2+A3+A4). Showing the build one beside a sheet is what made 25
        # green rows read as 25 machinable drawings on 2026-09-03.
        if rec.get("sheet_verdict") or rec.get("build_verdict"):
            v = ("SHEET %s · BUILD %s"
                 % (rec.get("sheet_verdict") or "CANNOT DETERMINE",
                    rec.get("build_verdict") or "CANNOT DETERMINE"))
        else:
            v = rec.get("verdict") or j.get("verdict")
        tier = rec.get("tier")
        head = ""
        if v:
            head = '<span class="v %s">%s</span>' % (verdict_class(v), esc(v if len(v) < 60 else v[:57] + "…"))
        elif tier:
            head = '<span class="v none">trust %s · %s</span>' % (esc(tier), esc(rec.get("tier_name", "")))
        else:
            head = '<span class="v none">record</span>'
        src = '<span class="src">from <a href="%s">%s</a></span>' % (bhref(relof(fp)), esc(relof(fp)))
        rows, lists, why = [], [], ""
        for k, val in rec.items():
            if k in ("verdict", "sheet_verdict", "build_verdict", "title",
                     "$triad", "$schema", "$generated", "kind_why"):
                continue
            if isinstance(val, bool):
                rows.append((k, esc(str(val)), False))
            elif isinstance(val, (int, float)):
                rows.append((k, esc(repr(val) if isinstance(val, float) else str(val)), True))
            elif isinstance(val, str):
                if k in ("why", "verdict_scope", "origin_why", "why_this_folder_exists"):
                    why += '<p class="why"><b>%s.</b> %s</p>' % (esc(k.replace("_", " ")), esc(val))
                elif val.startswith(ROOT):
                    r = relof(val)
                    rows.append((k, '<a href="%s">%s</a>' % (rawhref(r) if not os.path.isdir(val) else bhref(r, True), esc(r)), False))
                elif len(val) <= 160:
                    rows.append((k, esc(val), False))
                else:
                    why += '<p class="why"><b>%s.</b> %s</p>' % (esc(k.replace("_", " ")), esc(val))
            elif isinstance(val, list) and val and all(isinstance(x, (int, float)) for x in val):
                rows.append((k, esc(", ".join(repr(x) if isinstance(x, float) else str(x) for x in val)), True))
            elif isinstance(val, list) and val and all(isinstance(x, str) for x in val) and len(val) <= 40:
                if len(val) <= 6 and sum(len(x) for x in val) < 120:
                    rows.append((k, esc(", ".join(val)), False))
                else:
                    lists.append((k, val))
            elif isinstance(val, dict) and len(val) <= 12 and all(isinstance(x, (int, float, str, bool)) or x is None for x in val.values()):
                rows.append((k, esc(", ".join("%s %s" % (a, b) for a, b in val.items())), False))
            elif isinstance(val, list) and k == "unresolved_fails":
                lists.append((k, ["line %s %s: %s" % (x.get("line"), x.get("kind", ""), x.get("summary", "")) for x in val if isinstance(x, dict)]))
        dl = "".join('<dt>%s</dt><dd%s>%s</dd>' % (esc(k.replace("_", " ")), ' class="num"' if num else "", vv) for k, vv, num in rows)
        ul = "".join('<dt>%s</dt><dd><ul>%s</ul></dd>' % (esc(k.replace("_", " ")), "".join("<li>%s</li>" % esc(x) for x in items)) for k, items in lists)
        title = rec.get("title") or j.get("title") or ""
        heads.append('<div class="rec rec-head"><div class="rec-v">%s%s</div>%s</div>'
                     % (head, src, ('<p class="rec-t">%s</p>' % esc(title)) if title else ""))
        blocks.append('<div class="rec"><div class="rec-v"><span class="v none">%s</span></div><dl>%s%s</dl>%s</div>'
                      % (esc(name), dl, ul, why))
    return "".join(heads), "".join(blocks)


def page_dir(d, rel):
    rel = rel.strip("/")
    dirs, files = listdir(d)
    name = os.path.basename(rel) if rel else "microduck"
    parts = ['<h1 class="fh">%s</h1>' % esc(name + "/" if rel else name)]
    rec_head, rec_details = render_record(d, rel)
    parts.append(rec_head)
    imgs = [f for f in files if f.lower().endswith(IMG_EXT)]
    if imgs:
        cap = 120
        figs = []
        for f in imgs[:cap]:
            r = (rel + "/" + f) if rel else f
            dim = png_size(os.path.join(d, f))
            figs.append('<figure><a href="%s"><img src="%s" loading="lazy" alt="%s"></a><figcaption>%s%s</figcaption></figure>'
                        % (bhref(r) if not f.lower().endswith(".svg") else rawhref(r), rawhref(r), esc(f), esc(f),
                           ('<span class="dim">%d × %d</span>' % dim) if dim else ""))
        parts.append('<div class="gal">%s</div>' % "".join(figs))
        if len(imgs) > cap:
            parts.append('<p class="empty">%d images; the first %d are shown above, all are in the table.</p>' % (len(imgs), cap))
    parts.append(rec_details)
    rows = []
    for dd in dirs:
        r = (rel + "/" + dd) if rel else dd
        sd, sf = listdir(os.path.join(d, dd))
        v, t, tier, _ = record_of(os.path.join(d, dd))
        vv = ('<span class="v %s">%s</span>' % (verdict_class(v), esc(v if len(v) < 40 else verdict_text(v)))) if v else ""
        if tier:
            vv = '<span class="tier mono">%s</span> %s' % (esc(tier), vv)
        rows.append('<tr><td><a href="%s">%s/</a>%s</td><td class="k">folder</td><td class="num">%d · %d</td><td>%s</td></tr>'
                    % (bhref(r, True), esc(dd), (' <span class="empty" style="font-size:12.5px">— %s</span>' % esc(t[:110] + ("…" if len(t) > 110 else ""))) if t else "", len(sd), len(sf), vv))
    cap = 600
    for f in files[:cap]:
        r = (rel + "/" + f) if rel else f
        fp = os.path.join(d, f)
        st = os.stat(fp)
        ext = os.path.splitext(f)[1].lower().lstrip(".")
        lower = f.lower()
        v = ""
        if lower.endswith(".json") and st.st_size < (2 << 20) and lower in RECORD_FILES:
            j = load_json(fp)
            if isinstance(j, dict):
                rec = j.get("record") if isinstance(j.get("record"), dict) else j
                vv = rec.get("verdict") or j.get("verdict")
                if vv:
                    v = '<span class="v %s">%s</span>' % (verdict_class(vv), esc(vv if len(vv) < 40 else verdict_text(vv)))
        href = rawhref(r) if lower.endswith(RAW_ONLY_EXT) or lower.endswith(".svg") else bhref(r)
        rows.append('<tr><td><a href="%s">%s</a></td><td class="k">%s</td><td class="num">%s</td><td>%s <span class="mono" style="font-size:11.5px;color:var(--ink-2)">%s</span></td></tr>'
                    % (href, esc(f), esc(ext or "file"), esc(fmt_size(st.st_size)), v,
                       time.strftime("%Y-%m-%d %H:%M", time.localtime(st.st_mtime))))
    if rows:
        parts.append('<table class="files"><thead><tr><th>name</th><th>kind</th><th>size / entries</th><th>verdict · modified</th></tr></thead><tbody>%s</tbody></table>' % "".join(rows))
        if len(files) > cap:
            parts.append('<p class="empty">%d files; the first %d are listed.</p>' % (len(files), cap))
    else:
        parts.append('<p class="empty">empty folder</p>')
    return frame(name, rel, "".join(parts), is_dir=True, fp=d)


# ------------------------------------------------------------------ server
LLMS = """# microduck-doc-browser — routes
/               the master dossier (RELEASE.html) in the frame
/b/<rel>        browse any file or folder of the repo in the frame
/<rel>          the file itself at its real path (doc.css, images, dossiers as-is)
/api/health     {"app":"%s"} — the launchpad probe
/api/tree       the sidebar as JSON
/llms.txt       this list
""" % MARKER


class H(BaseHTTPRequestHandler):
    server_version = MARKER

    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="text/html; charset=utf-8", extra=None):
        b = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("X-App", MARKER)
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(b)

    def _404(self, what="not found"):
        self._send(404, "404 %s — %s" % (what, MARKER), "text/plain; charset=utf-8")

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        try:
            self._route()
        except BrokenPipeError:
            pass
        except Exception as e:  # never a silent 200
            self._send(500, "500 %s: %s" % (type(e).__name__, e), "text/plain; charset=utf-8")

    def _route(self):
        p = unquote(self.path.split("?", 1)[0])
        if p == "/api/health":
            body = json.dumps({"app": MARKER, "status": "ok", "root": ROOT, "port": PORT,
                               "revision": revision(), "time": time.strftime("%Y-%m-%dT%H:%M:%S%z")})
            return self._send(200, body, "application/json")
        if p == "/api/tree":
            g = [{"group": l, "base": b, "entries": [{"label": a, "rel": r, "dir": d, "verdict": v, "tier": t} for a, r, d, v, t in e]}
                 for l, b, e, _ in build_groups()]
            return self._send(200, json.dumps({"app": MARKER, "groups": g}, indent=1), "application/json")
        if p == "/llms.txt":
            return self._send(200, LLMS, "text/plain; charset=utf-8")
        if p == "/":
            for cand in ("RELEASE.html", "INDEX.html"):
                if os.path.isfile(os.path.join(ROOT, cand)):
                    return self._send(200, page_html(os.path.join(ROOT, cand), cand))
            return self._send(200, page_dir(ROOT, ""))
        if p == "/b" or p.startswith("/b/"):
            rel = p[3:]
            fp = safe(rel)
            if fp is None:
                return self._404("outside the repo")
            if os.path.isdir(fp):
                if rel and not p.endswith("/"):
                    return self._send(301, "", extra={"Location": bhref(rel, True)})
                return self._send(200, page_dir(fp, rel))
            if not os.path.isfile(fp):
                return self._404("no such document")
            lower = fp.lower()
            if lower.endswith((".html", ".htm")):
                return self._send(200, page_html(fp, rel))
            if lower.endswith(".md"):
                return self._send(200, page_md(fp, rel))
            if lower.endswith((".json", ".jsonl")) and not lower.endswith(".jsonl"):
                return self._send(200, page_json(fp, rel))
            if lower.endswith(IMG_EXT) and not lower.endswith(".svg"):
                return self._send(200, page_image(fp, rel))
            if lower.endswith(TEXT_EXT) or lower.endswith(".jsonl") or os.path.basename(fp).upper() in ("LICENSE", "LICENCE", "README"):
                return self._send(200, page_text(fp, rel))
            return self._send(302, "", extra={"Location": rawhref(rel)})
        # raw: the file at its real path
        fp = safe(p)
        if fp is None or not os.path.exists(fp):
            return self._404()
        if os.path.isdir(fp):
            return self._send(301, "", extra={"Location": bhref(relof(fp), True)})
        ct = mimetypes.guess_type(fp)[0] or "application/octet-stream"
        if ct.startswith("text/") or ct in ("application/json", "image/svg+xml"):
            ct += "; charset=utf-8"
        with open(fp, "rb") as f:
            data = f.read()
        return self._send(200, data, ct)


if __name__ == "__main__":
    mimetypes.add_type("model/stl", ".stl")
    mimetypes.add_type("application/dxf", ".dxf")
    print("%s on http://127.0.0.1:%d/  root=%s" % (MARKER, PORT, ROOT), flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
