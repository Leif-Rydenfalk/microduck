#!/usr/bin/env python3
"""head_dome_conformance.py — re-test COMPARISON.html finding #1 with both
confounds removed.

COMPARISON.html §5.1 measured head aspect off the WHOLE silhouette and had to
call CANNOT DETERMINE because two things polluted the number: the beak is open
in the reference photograph (adds apparent head height) and the head is tilted
(rotates the measurement axes). This script removes both:

  * beak -> colour-segmented OUT. The trim and beak are the chroma colour of
    the colourway (orange on Cream, yellow on Graphite); the shell is not.
  * tilt -> measured on the shell component's OWN principal axes (PCA), so an
    in-plane head rotation cannot change the ratio.

Run under an interpreter that has PIL. FreeCAD's has it:
    /Applications/FreeCAD.app/Contents/Resources/bin/python tools/head_dome_conformance.py

Writes out/verify/head_dome_conformance.json.
"""
import os, sys, json, math, colorsys
from collections import deque
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "out", "verify")

# top_head_shell bbox from out/verify/mech_dims.json (the dimensional truth)
MESH_Y, MESH_Z = 122.6900, 46.3361


def load(path, long_edge=1200):
    im = Image.open(os.path.join(REPO, path)).convert("RGB")
    sc = long_edge / max(im.size)
    return im.resize((int(im.size[0] * sc), int(im.size[1] * sc)), Image.LANCZOS)


def shell_mask(im, mode, vlo=None, vhi=None, smax=None, vthr=None, sthr=0.45):
    """mode 'light': shell is the bright, low-chroma colour (Cream render/photo).
       mode 'band' : shell is a mid-value, low-chroma grey (Graphite photo)."""
    w, h = im.size
    px = im.load()
    m = [[0] * h for _ in range(w)]
    for y in range(h):
        for x in range(w):
            r, g, b = [c / 255.0 for c in px[x, y]]
            hh, s, v = colorsys.rgb_to_hsv(r, g, b)
            if v > 0.955 and s < 0.045:
                continue                                  # white sweep
            deg = hh * 360.0
            if mode == "light":
                if s > sthr and 5 <= deg <= 70:
                    continue                              # trim + beak
                if v >= vthr:
                    m[x][y] = 1
            else:
                if vlo <= v <= vhi and s <= smax:
                    m[x][y] = 1
    return m, w, h


def top_component(m, w, h):
    start = None
    for y in range(h):
        for x in range(w):
            if m[x][y]:
                start = (x, y)
                break
        if start:
            break
    if not start:
        return []
    seen = {start}
    q = deque([start])
    out = []
    while q:
        x, y = q.popleft()
        out.append((x, y))
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                n = (x + dx, y + dy)
                if 0 <= n[0] < w and 0 <= n[1] < h and n not in seen and m[n[0]][n[1]]:
                    seen.add(n)
                    q.append(n)
    return out


def pca(pts):
    n = len(pts)
    mx = sum(p[0] for p in pts) / n
    my = sum(p[1] for p in pts) / n
    sxx = syy = sxy = 0.0
    for x, y in pts:
        dx, dy = x - mx, y - my
        sxx += dx * dx; syy += dy * dy; sxy += dx * dy
    sxx /= n; syy /= n; sxy /= n
    tr, det = sxx + syy, sxx * syy - sxy * sxy
    l1 = tr / 2 + math.sqrt(max(tr * tr / 4 - det, 0.0))
    e1 = (l1 - syy, sxy) if abs(sxy) > 1e-9 else ((1.0, 0.0) if sxx >= syy else (0.0, 1.0))
    L = math.hypot(*e1); e1 = (e1[0] / L, e1[1] / L); e2 = (-e1[1], e1[0])
    a = [(p[0] - mx) * e1[0] + (p[1] - my) * e1[1] for p in pts]
    b = [(p[0] - mx) * e2[0] + (p[1] - my) * e2[1] for p in pts]
    long_px, short_px = max(a) - min(a), max(b) - min(b)
    return {"n": n, "long_px": round(long_px, 2), "short_px": round(short_px, 2),
            "aspect": round(long_px / short_px, 4),
            "axis_deg": round(math.degrees(math.atan2(e1[1], e1[0])), 2)}


def sweep(path, mode, params):
    im = load(path)
    rows = {}
    for p in params:
        m, w, h = shell_mask(im, mode, **p)
        pts = top_component(m, w, h)
        if len(pts) < 200:
            continue
        key = str(p.get("vthr", "%.2f-%.2f" % (p.get("vlo", 0), p.get("vhi", 0))))
        rows[key] = pca(pts)
    return rows


def main():
    res = {
        "generated": "2026-09-02",
        "reference_mesh": {"mesh": "top_head_shell", "bbox_y_mm": MESH_Y, "bbox_z_mm": MESH_Z,
                           "profile_aspect": round(MESH_Y / MESH_Z, 4),
                           "source": "out/verify/mech_dims.json"},
        "ours_render": sweep("out/compare/ours-prof-left.png", "light",
                             [{"vthr": v} for v in (0.60, 0.65, 0.70, 0.72, 0.75)]),
        "product_cream_beak_open": sweep(
            "images/store/store_microduck-cream-standing-profile-left.jpg", "light",
            [{"vthr": v} for v in (0.60, 0.65, 0.70, 0.72)]),
        "product_graphite_beak_closed": sweep(
            "images/store/store_microduck-graphite-standing-profile-right-02.jpg", "band",
            [{"vlo": a, "vhi": b, "smax": 0.25}
             for a, b in ((0.26, 0.62), (0.28, 0.60), (0.30, 0.58), (0.30, 0.62), (0.32, 0.60))]),
    }
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "head_dome_conformance_raw.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
