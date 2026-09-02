#!/usr/bin/env python3
"""md2html.py — convert the project's Markdown docs to standalone HTML pages
in the shared academic/datasheet style. Leif, 2026-09-02: "no md files they
look like shit, more html and it must be complete." Stdlib only (no markdown
package on this Mac). Covers: ATX headings, tables (GFM), ordered/unordered
lists, fenced code, blockquotes, bold/italic/inline-code, links, hr, para.
"""
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CSS = open(os.path.join(HERE, "doc.css")).read() if os.path.exists(os.path.join(HERE, "doc.css")) else ""


def inline(t):
    t = html.escape(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\w)\*([^*]+)\*(?!\w)", r"<em>\1</em>", t)
    # links [text](url) — turn .md targets into .html
    def link(m):
        txt, url = m.group(1), m.group(2)
        if url.endswith(".md"):
            url = url[:-3] + ".html"
        return '<a href="%s">%s</a>' % (url, txt)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, t)
    return t


def convert(md, title):
    lines = md.split("\n")
    out = []
    i = 0
    n = len(lines)
    while i < n:
        ln = lines[i]
        # fenced code
        if ln.startswith("```"):
            code = []
            i += 1
            while i < n and not lines[i].startswith("```"):
                code.append(html.escape(lines[i]))
                i += 1
            i += 1
            out.append('<pre class="code">%s</pre>' % "\n".join(code))
            continue
        # table (a line with | and a following |---| separator)
        if "|" in ln and i + 1 < n and re.match(r"^\s*\|?[\s:|-]+\|[\s:|-]+$", lines[i + 1]):
            header = [c.strip() for c in ln.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            th = "".join("<th>%s</th>" % inline(h) for h in header)
            trs = []
            for r in rows:
                tds = "".join("<td>%s</td>" % inline(c) for c in r)
                trs.append("<tr>%s</tr>" % tds)
            out.append('<div class="tw"><table class="data"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
                       % (th, "".join(trs)))
            continue
        # headings
        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if m:
            lvl = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (min(lvl + 1, 6), inline(m.group(2)), min(lvl + 1, 6)))
            i += 1
            continue
        # hr
        if re.match(r"^\s*---+\s*$", ln):
            out.append("<hr>")
            i += 1
            continue
        # blockquote
        if ln.startswith(">"):
            q = []
            while i < n and lines[i].startswith(">"):
                q.append(inline(lines[i].lstrip(">").strip()))
                i += 1
            out.append("<blockquote>%s</blockquote>" % "<br>".join(q))
            continue
        # unordered list
        if re.match(r"^\s*[-*]\s+", ln):
            items = []
            while i < n and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append("<li>%s</li>" % inline(re.sub(r"^\s*[-*]\s+", "", lines[i])))
                i += 1
            out.append("<ul>%s</ul>" % "".join(items))
            continue
        # ordered list
        if re.match(r"^\s*\d+\.\s+", ln):
            items = []
            while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append("<li>%s</li>" % inline(re.sub(r"^\s*\d+\.\s+", "", lines[i])))
                i += 1
            out.append("<ol>%s</ol>" % "".join(items))
            continue
        # blank
        if not ln.strip():
            i += 1
            continue
        # paragraph (gather until blank)
        para = [ln]
        i += 1
        while i < n and lines[i].strip() and not re.match(r"^(#{1,6}\s|```|>|\s*[-*]\s|\s*\d+\.\s|\s*---+\s*$)", lines[i]) and not ("|" in lines[i] and i + 1 < n and re.match(r"^\s*\|?[\s:|-]+\|", lines[i + 1] if i + 1 < n else "")):
            para.append(lines[i])
            i += 1
        out.append("<p>%s</p>" % inline(" ".join(para)))
    body = "\n".join(out)
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<title>%s</title>\n'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opt_sz,wght@8..60,400;8..60,600;8..60,700&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">\n'
            '<style>\n%s\n</style>\n</head>\n<body>\n<div class="wrap"><p class="backlink"><a href="RELEASE.html">← Release dossier</a></p>\n%s\n</div>\n</body>\n</html>\n'
            % (html.escape(title), CSS, body))


def main(paths):
    for rel in paths:
        src = os.path.join(REPO, rel)
        if not os.path.exists(src):
            print("skip (missing)", rel)
            continue
        title = "Microduck — " + os.path.splitext(os.path.basename(rel))[0].replace("-", " ").title()
        out = os.path.splitext(src)[0] + ".html"
        open(out, "w").write(convert(open(src).read(), title))
        print("wrote", os.path.relpath(out, REPO))


if __name__ == "__main__":
    main(sys.argv[1:])
