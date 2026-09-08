#!/usr/bin/env python3
"""measure_radxa_drawing.py — MEASURE the Radxa ZERO 3W mechanical drawing.

Radxa's Product Brief RAD-DOC-0084 §4 "Mechanical Specification" (p.5 of the
document = PDF page 6) is a RASTER drawing: there is no text layer, no DXF and
no STEP, so every number a carrier board needs — the mounting-hole frame, the
40-pin header frame — has to be read off the picture. Reading it by eye is how
`ce-parts/radxa-zero-3w/iterations/v0.0.1/cad/part.py` came to carry
`RADXA_LONG_SPAN = 54.7`, which this tool measures to be a CONNECTOR dimension
and not the hole pitch (the hole pitch is 57.84 mm).

So this measures it instead, and states its own error basis:

  1. `pdfimages` extracts the two embedded images of PDF page 6 — the RGB layer
     (obj 68, 2480 x 1754) and its 8-bit SMask (obj 66). They are composited
     onto white; nothing is rescaled, so one pixel is one pixel of the drawing
     as Radxa shipped it.
  2. The board outline's four edges are located SUB-PIXEL by an ink-weighted
     centroid across each line's profile. The outline is 30.000 x 65.000 mm by
     Radxa's own two largest callouts, which sets the scale in each axis
     independently (they agree to 0.018 %).
  3. The four mounting holes are found by a Hough circle sweep over the corner
     windows, then refined by a weighted algebraic circle fit to the ring ink.
  4. The 40-pin header body rectangle is located the same way as the outline.

  NEGATIVE CONTROLS (printed by --check): three numbers Radxa DOES print are
  re-derived from the same pixels and compared. The header body must come out
  5.08 x 50.80 mm (a 2x20 2.54 mm header), its centre 3.3 mm from the right
  edge and 32.4 mm from the top edge. If any of those three drift, the scale is
  wrong and every other number here is wrong with it.

Run:  python3 tools/measure_radxa_drawing.py [--json out.json] [--check]
Needs: pdfimages (poppler) on PATH, and numpy + PIL — which on this Mac live
       ONLY in FreeCAD's python, so run it as
       /Applications/FreeCAD.app/Contents/Resources/bin/python tools/measure_radxa_drawing.py
       (or ce-cad/bin/cad tools/measure_radxa_drawing.py).
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(REPO, "ce-parts", "radxa-zero-3w", "iterations", "v0.0.1",
                   "docs", "fetched", "radxa_zero_3w_product_brief.pdf")
PDF_SHA256 = "edfb01374bbc6ee4062adf50d5d7241de64b64c8e87d186b3577bbb8761ddead"
PDF_PAGE = 6                      # document page 5, "4 Mechanical Specification"
BOARD_W_MM = 30.0                 # Radxa's callout "30. 0"
BOARD_L_MM = 65.0                 # Radxa's callout "65. 0"


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _flatten(pdf, page, workdir):
    """Extract page `page`'s RGB image + SMask and composite onto white."""
    import numpy as np
    from PIL import Image
    subprocess.run(["pdfimages", "-f", str(page), "-l", str(page), "-png", "-p",
                    pdf, os.path.join(workdir, "img")], check=True)
    pngs = sorted(f for f in os.listdir(workdir) if f.endswith(".png"))
    if len(pngs) != 2:
        raise SystemExit("expected the RGB layer + its SMask on page %d, got %d "
                         "images — the PDF changed; re-read it before trusting "
                         "anything downstream" % (page, len(pngs)))
    a = np.asarray(Image.open(os.path.join(workdir, pngs[0])).convert("L")).astype(float)
    m = np.asarray(Image.open(os.path.join(workdir, pngs[1])).convert("L")).astype(float) / 255.0
    if a.shape != m.shape:
        raise SystemExit("RGB layer %s and SMask %s differ in size" % (a.shape, m.shape))
    return a * m + 255.0 * (1.0 - m)          # grey, white background


def _edge(ink, axis, lo, hi, other):
    """Ink-weighted centroid of one straight line's profile. Sub-pixel."""
    import numpy as np
    prof = ink[other, lo:hi].mean(0) if axis == "v" else ink[lo:hi, other].mean(1)
    xs = np.arange(lo, hi)
    return float((xs * prof).sum() / prof.sum())


def _hough(dark, x0, x1, y0, y1, rmin, rmax, step=0.5, nth=180):
    import numpy as np
    w = dark[y0:y1, x0:x1]
    ys, xs = np.nonzero(w)
    th = np.linspace(0, 2 * np.pi, nth, endpoint=False)
    ct, st = np.cos(th), np.sin(th)
    H, W = w.shape
    best = None
    for r in np.arange(rmin, rmax, step):
        acc = np.zeros((H, W), dtype=np.int32)
        cxs = (xs[:, None] - r * ct[None, :]).astype(int)
        cys = (ys[:, None] - r * st[None, :]).astype(int)
        ok = (cxs >= 0) & (cxs < W) & (cys >= 0) & (cys < H)
        np.add.at(acc, (cys[ok], cxs[ok]), 1)
        v = int(acc.max())
        if best is None or v > best[0]:
            m = acc >= v * 0.85
            yy, xx = np.nonzero(m)
            wg = acc[m].astype(float)
            best = (v, float((xx * wg).sum() / wg.sum()) + x0,
                    float((yy * wg).sum() / wg.sum()) + y0, float(r))
    return best


def _refine_circle(ink, cx, cy, r, band=5.0, iters=8):
    """Weighted algebraic circle fit to the ring ink around (cx, cy)."""
    import numpy as np
    for _ in range(iters):
        y0, y1 = int(cy - 45), int(cy + 46)
        x0, x1 = int(cx - 45), int(cx + 46)
        yy, xx = np.mgrid[y0:y1, x0:x1]
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        m = (d > r - band) & (d < r + band)
        W = ink[y0:y1, x0:x1][m]
        if W.sum() == 0:
            break
        X = xx[m].astype(float)
        Y = yy[m].astype(float)
        A = np.c_[2 * X, 2 * Y, np.ones(len(X))] * W[:, None]
        sol, *_ = np.linalg.lstsq(A, (X ** 2 + Y ** 2) * W, rcond=None)
        ncx, ncy, c = sol
        nr = float(np.sqrt(c + ncx ** 2 + ncy ** 2))
        moved = abs(ncx - cx) + abs(ncy - cy)
        cx, cy, r = float(ncx), float(ncy), nr
        if moved < 1e-4:
            break
    return cx, cy, r


def measure():
    import numpy as np
    got = _sha256(PDF)
    if got != PDF_SHA256:
        raise SystemExit("PDF sha256 %s != the revision this tool was written "
                         "against (%s). Re-read §4 before trusting a number."
                         % (got, PDF_SHA256))
    with tempfile.TemporaryDirectory() as wd:
        grey = _flatten(PDF, PDF_PAGE, wd)
    ink = 255.0 - grey
    dark = grey < 128

    # --- board outline, sub-pixel. Seeds from the dark-pixel column/row sums.
    cols = dark[:, :1250].sum(0)
    rows = dark[:, :1250].sum(1)
    lx0 = int(np.argmax(cols[:700]))
    rx0 = int(700 + np.argmax(cols[700:1250]))
    ty0 = int(np.argmax(rows[:700]))
    by0 = int(700 + np.argmax(rows[700:]))
    L = _edge(ink, "v", lx0 - 5, lx0 + 6, slice(by0 - 900, by0 - 300))
    R = _edge(ink, "v", rx0 - 5, rx0 + 6, slice(by0 - 900, by0 - 300))
    T = _edge(ink, "h", ty0 - 5, ty0 + 6, slice(lx0 + 170, lx0 + 370))
    B = _edge(ink, "h", by0 - 5, by0 + 6, slice(lx0 + 170, lx0 + 370))
    sx = (R - L) / BOARD_W_MM
    sy = (B - T) / BOARD_L_MM

    # --- four mounting holes, one per corner window
    holes = {}
    win = 200
    for name, (x0, x1, y0, y1) in {
            "TL": (int(L), int(L) + win, int(T), int(T) + win),
            "TR": (int(R) - win, int(R), int(T), int(T) + win),
            "BL": (int(L), int(L) + win, int(B) - win, int(B)),
            "BR": (int(R) - win, int(R), int(B) - win, int(B))}.items():
        v, cx, cy, r = _hough(dark, x0, x1, y0, y1, 20, 34)
        cx, cy, r = _refine_circle(ink, cx, cy, r)
        holes[name] = {
            "centre_px": [round(cx, 3), round(cy, 3)],
            "hough_votes": v,
            "diameter_mm": round(2 * r / ((sx + sy) / 2), 4),
            "x_from_left_edge_mm": round((cx - L) / sx, 4),
            "y_from_top_edge_mm": round((cy - T) / sy, 4),
        }

    # --- 40-pin header body rectangle.
    # Its two long sides are the only pair of vertical lines INSIDE the board
    # whose single longest dark run exceeds 900 px (the 50.8 mm body) and whose
    # separation is a 2x20 header's 5.08 mm. Column SUMS are not enough: the
    # drawing's dimension extension lines are taller still.
    def longest_run(col):
        best = run = 0
        for v in col:
            run = run + 1 if v else 0
            best = max(best, run)
        return best

    inside = slice(int(T) + 2, int(B) - 2)
    tall = [x for x in range(int(L) + 200, int(R))
            if longest_run(dark[inside, x]) > 900]
    want = 5.08 * sx
    pair = min(((a, b) for i, a in enumerate(tall) for b in tall[i + 1:]),
               key=lambda ab: abs((ab[1] - ab[0]) - want))
    if abs((pair[1] - pair[0]) - want) > 0.3 * want:
        raise SystemExit("no pair of long vertical lines a 2x20 header wide "
                         "apart; the drawing changed")
    hl = _edge(ink, "v", pair[0] - 5, pair[0] + 6, slice(int(T) + 220, int(B) - 220))
    hr = _edge(ink, "v", pair[1] - 5, pair[1] + 6, slice(int(T) + 220, int(B) - 220))
    # The body's two ends: the longest dark run down either side line.
    col = dark[:, int(round(hl))]
    runs, st = [], None
    for y in range(len(col)):
        if col[y] and st is None:
            st = y
        elif not col[y] and st is not None:
            runs.append((st, y - 1))
            st = None
    if st is not None:
        runs.append((st, len(col) - 1))
    y0, y1 = max(runs, key=lambda r: r[1] - r[0])
    ht = _edge(ink, "h", y0 - 5, y0 + 6, slice(int(hl) + 20, int(hr) - 20))
    hb = _edge(ink, "h", y1 - 5, y1 + 6, slice(int(hl) + 20, int(hr) - 20))

    pitch_x = ((holes["TR"]["centre_px"][0] - holes["TL"]["centre_px"][0])
               + (holes["BR"]["centre_px"][0] - holes["BL"]["centre_px"][0])) / 2 / sx
    pitch_y = ((holes["BL"]["centre_px"][1] - holes["TL"]["centre_px"][1])
               + (holes["BR"]["centre_px"][1] - holes["TR"]["centre_px"][1])) / 2 / sy
    dias = [h["diameter_mm"] for h in holes.values()]
    insets = [holes["TL"]["x_from_left_edge_mm"], holes["BL"]["x_from_left_edge_mm"],
              BOARD_W_MM - holes["TR"]["x_from_left_edge_mm"],
              BOARD_W_MM - holes["BR"]["x_from_left_edge_mm"],
              holes["TL"]["y_from_top_edge_mm"], holes["TR"]["y_from_top_edge_mm"],
              BOARD_L_MM - holes["BL"]["y_from_top_edge_mm"],
              BOARD_L_MM - holes["BR"]["y_from_top_edge_mm"]]

    def stats(v):
        m = sum(v) / len(v)
        sd = (sum((x - m) ** 2 for x in v) / (len(v) - 1)) ** 0.5
        return round(m, 4), round(sd, 4)

    inset_mean, inset_sd = stats(insets)
    dia_mean, dia_sd = stats(dias)
    px_mm = 1.0 / ((sx + sy) / 2)
    return {
        "$about": "MEASURED off the raster in Radxa's Product Brief §4 by "
                  "tools/measure_radxa_drawing.py. Every number below is a "
                  "measurement of a PICTURE, not a value Radxa printed, unless "
                  "the key says printed_*.",
        "source": {
            "document": "Radxa ZERO 3W Product Brief, RAD-DOC-0084 Rev 1.10, 2026-06-26",
            "path": os.path.relpath(PDF, REPO),
            "sha256": PDF_SHA256,
            "section": "§4 Mechanical Specification, document p.5 (PDF page 6)",
            "url": "https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_product_brief.pdf",
            "fetched": "2026-09-02",
            "raster": "embedded image 2480 x 1754 px (RGB + 8-bit SMask); no text "
                      "layer, no DXF, no STEP published for this board",
        },
        "printed_callouts_verbatim": ["30. 0", "65. 0", "15. 5", "3. 3", "12. 5",
                                      "41. 5", "14. 4", "32. 4", "3. 6",
                                      "4 X Ø2. 8", "15. 0", "2. 8", "9. 9"],
        "scale": {
            "px_per_mm_x": round(sx, 5), "px_per_mm_y": round(sy, 5),
            "axis_disagreement_pct": round(abs(sx - sy) / ((sx + sy) / 2) * 100, 4),
            "one_pixel_mm": round(px_mm, 5),
            "basis": "the outline's own two printed callouts, 30.0 mm across and "
                     "65.0 mm along; edges located sub-pixel by ink-weighted "
                     "centroid",
        },
        "outline_px": {"left": round(L, 3), "right": round(R, 3),
                       "top": round(T, 3), "bottom": round(B, 3)},
        "mount_holes": {
            "count": 4,
            "printed_diameter_mm": 2.8,
            "measured_diameter_mm": dia_mean,
            "measured_diameter_sd_mm": dia_sd,
            "printed_edge_inset_mm": 3.6,
            "measured_edge_inset_mm": inset_mean,
            "measured_edge_inset_sd_mm": inset_sd,
            "pitch_across_mm": round(pitch_x, 4),
            "pitch_along_mm": round(pitch_y, 4),
            "per_hole": holes,
        },
        "header_40pin_body": {
            "x_from_left_edge_mm": [round((hl - L) / sx, 4), round((hr - L) / sx, 4)],
            "y_from_top_edge_mm": [round((ht - T) / sy, 4), round((hb - T) / sy, 4)],
            "width_mm": round((hr - hl) / sx, 4),
            "length_mm": round((hb - ht) / sy, 4),
            "centre_from_right_edge_mm": round((R - (hl + hr) / 2) / sx, 4),
            "centre_from_top_edge_mm": round(((ht + hb) / 2 - T) / sy, 4),
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="write the measurement to this path")
    ap.add_argument("--check", action="store_true",
                    help="run the negative controls and exit 0/1")
    a = ap.parse_args()
    m = measure()
    if a.json:
        os.makedirs(os.path.dirname(os.path.abspath(a.json)), exist_ok=True)
        with open(a.json, "w") as fh:
            json.dump(m, fh, indent=1)
            fh.write("\n")
        print("wrote", a.json)
    print(json.dumps(m, indent=1))
    if a.check:
        h = m["header_40pin_body"]
        # A 2x20 header on 2.54 mm pitch is 5.08 x 50.80 mm. Radxa prints 3.3
        # and 32.4 for its centre. Three independent numbers, one scale.
        controls = [("header body width", h["width_mm"], 5.08, 0.06),
                    ("header body length", h["length_mm"], 50.80, 0.10),
                    ("header centre from right edge", h["centre_from_right_edge_mm"], 3.3, 0.06),
                    ("header centre from top edge", h["centre_from_top_edge_mm"], 32.4, 0.06)]
        bad = 0
        for name, got, want, tol in controls:
            ok = abs(got - want) <= tol
            bad += not ok
            print("%-32s %8.4f vs %-7.2f  d=%+.4f  %s"
                  % (name, got, want, got - want, "PASS" if ok else "FAIL"))
        print("negative controls:", "PASS" if not bad else "%d FAIL" % bad)
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
