#!/usr/bin/env python3
"""tablefit.py — does every table in a document actually FIT the sheet, or is a column
clipped off the right edge?

    python3 tools/tablefit.py MANUFACTURING-PLAYBOOK.html [more.html ...]

Why this exists.  `tools/doc.css` puts every table inside `.tablewrap{overflow-x:auto}`
inside `.wrap{max-width:920px}`.  A table wider than the sheet therefore does not break
the layout and does not error — it silently grows a scrollbar, and the LAST column, which
in an evidence table is usually the verdict, disappears.  A screenshot of the page looks
fine unless you know to look for it.  On paper (`.tablewrap`'s scroll does not exist in
print) that column is simply gone.  This was a real published defect in
MANUFACTURING-PLAYBOOK.html §3 (2026-09-03).

What it measures, in the real browser, on the real file:

  sheet      the content box of `.wrap` — the width a table is allowed to occupy
  table      the table's own scrollWidth
  over       table - sheet.  > 0 means at least one column is off the sheet.
  clipped    per-cell: scrollWidth > clientWidth + 1, i.e. this cell's own text is
             cut by its box (the "CLE…" / "WAT…" failure), reported with the column
             header and the truncated text.

Three verdicts, no soft pass: PASS (over <= 0 and nothing clipped), FAIL (either),
CANNOT DETERMINE (no browser, or the page did not report).  Exit 0 / 1 / 2.

The measurement runs headless Chrome with `--dump-dom`, on a copy of the document with a
`<base>` and one measuring script appended, so the CSS resolves exactly as published and
nothing about the real file is changed.
"""
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
]

# The sheet the repo's documents are laid out for: tools/doc.css `.wrap{max-width:920px;
# padding:0 40px}`.  Measured from the live element rather than assumed, but the viewport
# is set wide enough that .wrap reaches its max-width and the measurement is of the sheet
# and not of the window.
VIEWPORT = 1400

PROBE = """
<script>
(function () {
  function run() {
    var wrap = document.querySelector('.wrap') || document.body;
    var cs = getComputedStyle(wrap);
    var sheet = wrap.clientWidth
      - parseFloat(cs.paddingLeft || 0) - parseFloat(cs.paddingRight || 0);
    var out = {sheet: sheet, viewport: window.innerWidth, tables: []};
    var secOf = function (el) {
      var s = el.closest('section');
      return s ? (s.id || '') : '';
    };
    document.querySelectorAll('table').forEach(function (t, i) {
      var heads = [];
      t.querySelectorAll('thead th').forEach(function (th) { heads.push(th.innerText.trim()); });
      var clipped = [];
      t.querySelectorAll('td, th').forEach(function (c) {
        if (c.scrollWidth > c.clientWidth + 1) {
          clipped.push({col: c.cellIndex, head: heads[c.cellIndex] || ('#' + c.cellIndex),
                        text: c.innerText.trim().slice(0, 40),
                        want: c.scrollWidth, got: c.clientWidth});
        }
      });
      out.tables.push({i: i, section: secOf(t), cls: t.className,
                       cols: heads.length, heads: heads,
                       width: t.scrollWidth, over: t.scrollWidth - sheet,
                       rows: t.querySelectorAll('tbody tr').length,
                       clipped: clipped});
    });
    var pre = document.createElement('pre');
    pre.id = 'tablefit-result';
    pre.textContent = JSON.stringify(out);
    document.body.appendChild(pre);
  }
  if (document.readyState === 'complete') { run(); }
  else { window.addEventListener('load', run); }
})();
</script>
"""


def chrome():
    for p in CHROMES:
        if os.path.isfile(p):
            return p
    return shutil.which("chromium") or shutil.which("google-chrome")


def measure(doc_path, viewport=VIEWPORT):
    """Returns (dict, None) or (None, reason)."""
    br = chrome()
    if not br:
        return None, "no Chrome/Chromium binary on this machine"
    src = open(doc_path, encoding="utf-8").read()
    rel = os.path.relpath(ROOT, os.path.dirname(doc_path))
    base = os.path.dirname(os.path.abspath(doc_path))
    tmpd = tempfile.mkdtemp(prefix="tablefit-")
    probe = os.path.join(tmpd, "probe.html")
    # <base> points at the ORIGINAL directory so every relative href (tools/doc.css,
    # out/…/*.png) resolves exactly as it does in the published file.
    inject = '<base href="file://%s/">' % base.replace('"', "%22")
    if "<head>" in src:
        src = src.replace("<head>", "<head>\n" + inject, 1)
    else:
        src = inject + src
    src = src.replace("</body>", PROBE + "</body>", 1) if "</body>" in src else src + PROBE
    open(probe, "w", encoding="utf-8").write(src)
    cmd = [br, "--headless=new", "--disable-gpu", "--no-sandbox",
           "--allow-file-access-from-files",
           "--window-size=%d,1200" % viewport,
           "--virtual-time-budget=8000", "--dump-dom", "file://" + probe]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        shutil.rmtree(tmpd, ignore_errors=True)
        return None, "chrome timed out"
    dom = r.stdout
    shutil.rmtree(tmpd, ignore_errors=True)
    m = re.search(r'<pre id="tablefit-result">(.*?)</pre>', dom, re.S)
    if not m:
        return None, "the page did not report (probe did not run)"
    return json.loads(html.unescape(m.group(1))), None


def report(doc, viewport=VIEWPORT):
    path = doc if os.path.isabs(doc) else os.path.join(ROOT, doc)
    if not os.path.exists(path):
        print("CANNOT DETERMINE  %s — no such file" % doc)
        return 2
    data, why = measure(path, viewport)
    if data is None:
        print("CANNOT DETERMINE  %s — %s" % (doc, why))
        return 2
    print("%s   viewport %dpx, sheet %.1fpx" % (doc, data["viewport"], data["sheet"]))
    bad = 0
    for t in data["tables"]:
        v = "PASS"
        if t["over"] > 0 or t["clipped"]:
            v = "FAIL"
            bad += 1
        print("  %-4s §%-10s %2d cols x %3d rows  table %7.1fpx  over %+8.1fpx  %s"
              % (v, t["section"] or "-", t["cols"], t["rows"], t["width"], t["over"],
                 t["cls"]))
        seen = set()
        for c in t["clipped"]:
            k = (c["col"], c["text"])
            if k in seen:
                continue
            seen.add(k)
            print("        clipped col %d %-14s %-22r %.0f -> %.0f px"
                  % (c["col"], c["head"], c["text"], c["want"], c["got"]))
    print("  %d of %d tables FAIL" % (bad, len(data["tables"])))
    return 1 if bad else 0


if __name__ == "__main__":
    args = sys.argv[1:] or ["MANUFACTURING-PLAYBOOK.html"]
    rc = 0
    for a in args:
        rc = max(rc, report(a))
    sys.exit(rc)
