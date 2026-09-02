#!/usr/bin/env python3
"""head_analysis.py — quantify the sim-head vs product-head discrepancy.

Both the product photograph and our render are near-orthographic side views on
white. We threshold each to a silhouette and measure SCALE-FREE ratios, so no
camera calibration is needed:

    head_length / total_height      (how far the head reaches front-to-back)
    head_height / total_height
    head_length / head_height       (the head's own aspect ratio)

If the sim head is genuinely longer front-to-back than the product head, these
ratios diverge and by how much is the finding. Writes out/verify/head_analysis.json
plus annotated silhouettes so a human can check the measurement by eye.
"""
import json, os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(REPO, "out", "verify")
os.makedirs(OUT, exist_ok=True)

TARGETS = {
    "product_photo": os.path.join(REPO, "images", "store",
                                  "store_microduck-cream-standing-profile-left.jpg"),
    "our_render": os.path.join(REPO, "out", "compare", "ours-prof-left.png"),
}
BG_THRESH = 236          # anything brighter than this is background/white sweep


def silhouette(path):
    im = Image.open(path).convert("L")
    w, h = im.size
    px = im.load()
    cols = [[] for _ in range(w)]
    rows = {}
    pts = []
    for y in range(h):
        for x in range(w):
            if px[x, y] < BG_THRESH:
                pts.append((x, y))
                cols[x].append(y)
                rows.setdefault(y, []).append(x)
    return im.size, pts, cols, rows


def analyse(name, path):
    (w, h), pts, cols, rows = silhouette(path)
    if not pts:
        return {"image": name, "verdict": "CANNOT DETERMINE", "why": "no silhouette found"}
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    total_h = y1 - y0
    total_w = x1 - x0
    # The head is the topmost structure. Take the band from the top of the
    # silhouette down to where the neck pinches: scan rows, the head ends at the
    # first row whose horizontal extent drops below 45% of the widest head row.
    head_rows = []
    widest = 0
    for y in range(y0, y0 + int(total_h * 0.55)):
        r = rows.get(y)
        if not r:
            continue
        ext = max(r) - min(r)
        widest = max(widest, ext)
        head_rows.append((y, ext, min(r), max(r)))
    head_end_y = None
    for y, ext, _a, _b in head_rows:
        if widest and ext < 0.45 * widest and y > y0 + 0.10 * total_h:
            head_end_y = y
            break
    if head_end_y is None:
        head_end_y = y0 + int(total_h * 0.35)
    hb = [r for r in head_rows if r[0] < head_end_y]
    head_x0 = min(r[2] for r in hb)
    head_x1 = max(r[3] for r in hb)
    head_len = head_x1 - head_x0
    head_h = head_end_y - y0
    return {
        "image": name, "size_px": [w, h],
        "silhouette_bbox_px": [x0, y0, x1, y1],
        "total_height_px": total_h, "total_width_px": total_w,
        "head_length_px": head_len, "head_height_px": head_h,
        "head_end_y_px": head_end_y,
        "r_headlen_over_height": round(head_len / total_h, 4) if total_h else None,
        "r_headh_over_height": round(head_h / total_h, 4) if total_h else None,
        "r_head_aspect": round(head_len / head_h, 4) if head_h else None,
        "_ann": (x0, y0, x1, y1, head_x0, head_x1, head_end_y),
        "_path": path,
    }


def annotate(a, out_path):
    im = Image.open(a["_path"]).convert("RGB")
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1, hx0, hx1, hey = a["_ann"]
    d.rectangle([x0, y0, x1, y1], outline=(40, 90, 160), width=4)          # whole robot
    d.rectangle([hx0, y0, hx1, hey], outline=(200, 40, 30), width=5)       # head box
    d.line([x0, hey, x1, hey], fill=(200, 40, 30), width=3)                # neck line
    im.save(out_path)


def main():
    res = {}
    for name, path in TARGETS.items():
        if not os.path.exists(path):
            res[name] = {"verdict": "CANNOT DETERMINE", "why": "missing %s" % path}
            continue
        a = analyse(name, path)
        annotate(a, os.path.join(OUT, "head-%s.png" % name.replace("_", "-")))
        a.pop("_ann", None); a.pop("_path", None)
        res[name] = a
        print("%-14s head_len/height=%s  head_aspect=%s  (head %dpx of %dpx tall)"
              % (name, a["r_headlen_over_height"], a["r_head_aspect"],
                 a["head_length_px"], a["total_height_px"]))

    p, o = res.get("product_photo", {}), res.get("our_render", {})
    out = {"generated": "2026-09-02",
           "method": ("scale-free silhouette ratios on two near-orthographic side views; "
                      "background threshold %d/255; head band ends where the row extent "
                      "pinches below 45%% of the widest head row (the neck)" % BG_THRESH),
           "measurements": res}
    if p.get("r_headlen_over_height") and o.get("r_headlen_over_height"):
        rp, ro = p["r_headlen_over_height"], o["r_headlen_over_height"]
        ap, ao = p["r_head_aspect"], o["r_head_aspect"]
        out["comparison"] = {
            "product_head_len_over_height": rp,
            "our_head_len_over_height": ro,
            "our_head_longer_by_pct": round((ro / rp - 1) * 100, 2),
            "product_head_aspect": ap, "our_head_aspect": ao,
            "aspect_difference_pct": round((ao / ap - 1) * 100, 2),
            "sim_head_length_mm": 122.688,
            "implied_product_head_length_mm": round(122.688 * rp / ro, 3),
            "implied_overshoot_mm": round(122.688 - 122.688 * rp / ro, 3),
            "verdict": "MISMATCH" if abs(ro / rp - 1) > 0.08 else "WITHIN 8%",
        }
        c = out["comparison"]
        print("\nproduct head/height %.4f   ours %.4f   -> ours is %+.2f%% longer"
              % (rp, ro, c["our_head_longer_by_pct"]))
        print("implied product head length %.3f mm vs sim mesh 122.688 mm  (overshoot %.3f mm)"
              % (c["implied_product_head_length_mm"], c["implied_overshoot_mm"]))
        print("VERDICT:", c["verdict"])
    json.dump(out, open(os.path.join(OUT, "head_analysis.json"), "w"), indent=1)
    print("\nwrote out/verify/head_analysis.json + annotated silhouettes")


if __name__ == "__main__":
    main()
