#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""head_real_video.py — measure the REAL Microduck's head motion off Pollen's
own published video, so our simulated head has something to be compared with.

Method (stated so the error budget is visible):
  * one robot, filmed near-profile, is cropped out of the frame;
  * the accent-colour beak / head-trim band is thresholded in RGB and its
    principal axis found by SVD -> a line angle in the IMAGE PLANE;
  * that angle tracks HEAD PITCH for a robot seen close to profile. It is a
    proxy, not a joint encoder: camera roll, head yaw away from profile and
    lens distortion all bias it, and the zero is arbitrary (the band is not
    horizontal at head_pitch = 0). Only CHANGES are used.

So the numbers this writes are a LOWER BOUND on what the real head does: the
clip is a scripted "chorale" animation, not a maximum-rate test.

    .../bin/python sim/head_real_video.py images/gallery_chorale.mp4 60 80 440 420
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw
import imageio.v2 as iio

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "motion")


def track(src, box, out_json, overlay_every=60):
    x0, y0, x1, y1 = box
    rd = iio.get_reader(src)
    fps = float(rd.get_meta_data()["fps"])
    rows, overlays = [], []
    for i, fr in enumerate(rd):
        c = fr[y0:y1, x0:x1].astype(np.int16)
        R, G, B = c[:, :, 0], c[:, :, 1], c[:, :, 2]
        m = (R > 165) & (G > 140) & (B < 115) & (R - B > 70) & (G - B > 55)
        n = int(m.sum())
        if n < 200:
            rows.append([i / fps, None, n]); continue
        ys, xs = np.nonzero(m)
        p = np.stack([xs, ys]).astype(float)
        p -= p.mean(axis=1, keepdims=True)
        u, s, vt = np.linalg.svd(p, full_matrices=False)
        ax = u[:, 0]
        ang = math.degrees(math.atan2(-ax[1], ax[0]))
        ang = ang - 180 if ang > 90 else (ang + 180 if ang < -90 else ang)
        rows.append([i / fps, ang, n])
        if i % overlay_every == 0 and len(overlays) < 6:
            im = Image.fromarray(fr[y0:y1, x0:x1].copy())
            d = ImageDraw.Draw(im)
            cx, cy, L = xs.mean(), ys.mean(), 130
            d.line([(cx - ax[0] * L, cy + ax[1] * L), (cx + ax[0] * L, cy - ax[1] * L)],
                   fill=(230, 30, 30), width=3)
            d.text((5, 5), "t=%.2fs  %.2f deg" % (i / fps, ang), fill=(230, 30, 30))
            overlays.append(im)
    rd.close()
    a = np.array([r[1] for r in rows if r[1] is not None], float)
    t = np.array([r[0] for r in rows if r[1] is not None], float)
    sm = np.convolve(a, np.ones(3) / 3.0, mode="same")
    rate = np.gradient(sm, 1.0 / fps)[2:-2]
    w = int(round(0.5 * fps))
    exc = max((a[i:i + w].max() - a[i:i + w].min(), t[i]) for i in range(len(a) - w))
    res = {
        "source_video": os.path.relpath(src, ROOT),
        "catalog": "images/CATALOG.md:98 — gallery_chorale.mp4 (12 s) 'four robots, jaws moving; "
                   "jaw range; head roll/yaw expressiveness'",
        "crop_xyxy_px": list(box), "fps": fps, "frames": len(rows), "frames_tracked": int(len(a)),
        "measures": "image-plane principal-axis angle of the accent beak/trim band; proxy for head pitch",
        "angle_deg_min": round(float(a.min()), 4), "angle_deg_max": round(float(a.max()), 4),
        "travel_deg": round(float(a.max() - a.min()), 4),
        "peak_rate_deg_s_raw": round(float(np.abs(np.gradient(a, 1.0 / fps)).max()), 3),
        "peak_rate_deg_s_smoothed3": round(float(np.abs(rate).max()), 3),
        "largest_0p5s_excursion_deg": round(float(exc[0]), 4),
        "largest_0p5s_excursion_at_s": round(float(exc[1]), 3),
        "caveats": ["camera is hand-held: its own roll drift is inside this signal",
                    "head yaw off-profile foreshortens the band and biases the angle",
                    "clip is a scripted animation, not a maximum-rate test — LOWER BOUND only",
                    "no scale or camera calibration is published, so absolute joint angle is not recoverable"],
        "script": "sim/head_real_video.py",
    }
    os.makedirs(OUT, exist_ok=True)
    json.dump({"summary": res, "trace": rows}, open(out_json, "w"), indent=1)
    if overlays:
        w0, h0 = overlays[0].size
        sh = Image.new("RGB", (w0 * len(overlays), h0), (255, 255, 255))
        for j, im in enumerate(overlays):
            sh.paste(im, (j * w0, 0))
        sh.save(out_json.replace(".json", "_overlay.png"))
    return res


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "images", "gallery_chorale.mp4")
    box = [int(v) for v in sys.argv[2:6]] or [60, 80, 440, 420]
    r = track(src, box, os.path.join(OUT, "head_real_video.json"))
    print(json.dumps(r, indent=1))
