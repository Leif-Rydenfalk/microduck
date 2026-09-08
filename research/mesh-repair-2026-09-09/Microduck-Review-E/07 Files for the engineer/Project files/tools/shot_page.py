#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""shot_page.py — screenshot one of this repo's HTML documents and PROVE it drew,
then slice it into strips a person (or a model) can actually read back.

Why this exists (lane F2, 2026-09-03). Two things kept going wrong:

  1. `cecad.vision.screenshot_url(..., full_page=True)` on a very tall document
     produced a PNG in which the masthead appeared several times — the stitched
     passes did not line up — so a read-back of the middle of the page was
     reading a repeat, not the page. MEASURED on a 16 286 px document: the
     stitched capture repeated the header at y ~= 7 000 px; a single-viewport
     capture at --window-size=1100,16286 did not.
  2. `cecad.imgcheck.verify_png` refuses a text document: it wants one
     continuous mark covering >= 10 % of the frame, and a page of set type has
     none ("ink broken into small pieces is lettering on an empty canvas").
     That check is right for a RENDER and wrong for a DOCUMENT, so this tool
     applies a document-shaped check instead of switching the check off:
       - the document's own scrollHeight, images count and BROKEN-image count
         are read out of the live DOM before the capture, and a broken image
         fails the run;
       - the capture must be exactly that tall;
       - ink fraction must exceed --min-ink (default 2 %), which a blank or
         all-white page cannot reach;
       - every table's scrollWidth is measured against the width available to
         it, and a table wider than its column is reported — that is the defect
         where a column silently sits outside the page in print or PDF.

Run:
  ce-cad/bin/cad tools/shot_page.py out/sim-evidence/f2-preview.html
  ce-cad/bin/cad tools/shot_page.py <page.html> --width 1100 --strip 1400
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

PROBE = """
<pre id="CE_SHOT_MEASURE"></pre>
<script>
window.addEventListener('load', function () {
  var b = document.body, e = document.documentElement, out = {};
  out.height = Math.max(b.scrollHeight, e.scrollHeight);
  out.width = Math.max(b.scrollWidth, e.scrollWidth);
  out.images = document.images.length;
  out.broken = Array.prototype.filter.call(document.images, function (i) {
    return !i.complete || i.naturalWidth === 0;
  }).map(function (i) { return i.getAttribute('src'); });
  out.tables = [];
  document.querySelectorAll('table').forEach(function (t, i) {
    var cap = t.parentElement.previousElementSibling;
    out.tables.push({ i: i, cls: t.className,
                      w: Math.round(t.scrollWidth),
                      avail: Math.round(t.parentElement.clientWidth),
                      cols: t.rows.length ? t.rows[0].cells.length : 0,
                      caption: (cap ? cap.textContent : '').replace(/\\s+/g, ' ').slice(0, 60) });
  });
  document.getElementById('CE_SHOT_MEASURE').textContent = JSON.stringify(out);
});
</script>
"""


def probe(page):
    """Read the live DOM: real height, broken images, and every table's width."""
    d = os.path.dirname(os.path.abspath(page))
    fd, tmp = tempfile.mkstemp(suffix=".html", dir=d)      # same dir: relative CSS/img resolve
    os.close(fd)
    try:
        with open(tmp, "w") as f:
            f.write(open(page).read() + PROBE)
        dom = subprocess.run([CHROME, "--headless", "--disable-gpu", "--window-size=1100,900",
                              "--virtual-time-budget=12000", "--dump-dom", "file://" + tmp],
                             capture_output=True, text=True).stdout
    finally:
        os.remove(tmp)
    m = re.search(r'<pre id="CE_SHOT_MEASURE">(.*?)</pre>', dom, re.S)
    if not m:
        raise SystemExit("the page did not run its own load handler — it did not render")
    import html as H
    return json.loads(H.unescape(m.group(1)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page")
    ap.add_argument("--out", default=None, help="PNG path (default: <page>.png beside it)")
    ap.add_argument("--width", type=int, default=1100)
    ap.add_argument("--strip", type=int, default=1400, help="0 = no strips")
    ap.add_argument("--min-ink", type=float, default=0.02)
    a = ap.parse_args()
    page = os.path.abspath(a.page)
    out = a.out or os.path.splitext(page)[0] + ".png"
    assert os.path.exists(CHROME), CHROME

    info = probe(page)
    print("DOM: %d x %d px, %d images, %d broken, %d tables"
          % (info["width"], info["height"], info["images"], len(info["broken"]), len(info["tables"])))
    if info["broken"]:
        raise SystemExit("BROKEN IMAGES, the page is not correct: " + ", ".join(info["broken"][:8]))

    over = [t for t in info["tables"] if t["w"] > t["avail"] + 1]
    for t in info["tables"]:
        flag = "  <-- WIDER THAN ITS COLUMN, columns will sit outside a printed page" \
            if t["w"] > t["avail"] + 1 else ""
        print("  table %-2d %-14s %4d px in %4d px, %d cols  %s%s"
              % (t["i"], t["cls"] or "-", t["w"], t["avail"], t["cols"], t["caption"], flag))

    h = int(info["height"])
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                    "--window-size=%d,%d" % (a.width, h), "--virtual-time-budget=20000",
                    "--screenshot=" + out, "file://" + page], capture_output=True)
    from PIL import Image
    import numpy as np
    im = Image.open(out).convert("RGB")
    W, H = im.size
    arr = np.asarray(im).astype(float)
    ink = float((arr.mean(axis=2) < 200).mean())
    print("captured %d x %d px, ink fraction %.4f, mean intensity %.1f" % (W, H, ink, arr.mean()))
    if H != h:
        raise SystemExit("capture is %d px tall but the document is %d px — the capture is not the page"
                         % (H, h))
    if ink < a.min_ink:
        raise SystemExit("ink fraction %.4f < %.4f — the page did not draw" % (ink, a.min_ink))
    n = 0
    if a.strip:
        stem = os.path.splitext(out)[0]
        for f in os.listdir(os.path.dirname(out)):
            if re.match(re.escape(os.path.basename(stem)) + r"-\d\d\.png$", f):
                os.remove(os.path.join(os.path.dirname(out), f))
        for top in range(0, H, a.strip):
            n += 1
            im.crop((0, top, W, min(top + a.strip, H))).save("%s-%02d.png" % (stem, n))
    print("wrote %s%s" % (os.path.relpath(out, REPO), " + %d strips" % n if n else ""))
    if over:
        raise SystemExit("%d table(s) overflow their column — fix the page, do not ship it" % len(over))


if __name__ == "__main__":
    main()
