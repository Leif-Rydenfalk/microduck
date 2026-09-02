#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""walk_vs_product.py — our walk beside Pollen's own walk clip, phase-matched.

Leif's standing rule: a render of ours sits next to the real product at the same
view. For WALKING the only published asset of the same motion is Pollen's
portrait move clip images/moves-portrait-alpha_walk.webm (800x1280, 50 fps, 400
frames, 8.000 s — read off the file). It is Pollen's own rendered clip, not a
photograph; no photograph of the product mid-stride exists in images/.

This script
  1. measures the PRODUCT clip's gait period off the pixels: foreground
     silhouette (any channel < 240), the bottom 15 % of rows (the feet), the
     x-centroid of that band minus the x-centroid of the whole silhouette ->
     one oscillation per gait cycle -> autocorrelation peak;
  2. measures OUR gait period the same way in angle space (sim/motion_render.py
     gait_cycle(), autocorrelation of left_knee);
  3. renders OUR duck at azimuth 135 (3/4 front-right, the clip's view) at five
     equal phases of one of our cycles, and pairs them with the product frames
     at the same five phases of one of its cycles.

    /Applications/FreeCAD.app/Contents/Resources/bin/python sim/walk_vs_product.py
"""
import json, os, sys
os.environ.setdefault("MUJOCO_GL", "glfw")
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import common               # noqa: E402
import compare_render       # noqa: E402
import motion_render as MR  # noqa: E402

CLIP = os.path.join(ROOT, "images", "moves-portrait-alpha_walk.webm")
OUT = MR.OUT


def whiten(f):
    """the clip is an alpha portrait and the decoded background is EXACTLY black
    (measured on frame 100: 938762 of 1024000 px at luma 0, 17952 px in (0,12] —
    those are the robot's black plastic, so a luma>12 threshold knocks holes in
    the legs). Background = luma 0; any 0-luma pixel enclosed by foreground on all
    four sides of its row and column is robot, not background. Composited onto
    white to match our studio."""
    g = f.astype(np.float32).mean(axis=2)
    fg = g > 0.5
    L = np.maximum.accumulate(fg, axis=1)
    R = np.maximum.accumulate(fg[:, ::-1], axis=1)[:, ::-1]
    U = np.maximum.accumulate(fg, axis=0)
    D = np.maximum.accumulate(fg[::-1, :], axis=0)[::-1, :]
    fg = fg | (L & R & U & D)
    return np.where(fg[:, :, None], f, np.uint8(255)), fg


def product_signal():
    """pass 1: the foot-band x-centroid minus the whole-silhouette x-centroid,
    per frame. One oscillation per gait cycle. No frames kept (400 x 1280 x 800)."""
    import imageio
    rd = imageio.get_reader(CLIP)
    md = dict(rd.get_meta_data())
    sig, n = [], 0
    for f in rd:
        n += 1
        _, fg = whiten(f)
        ys, xs = np.nonzero(fg)
        if len(xs) < 50:
            sig.append(np.nan); continue
        y0 = ys.max() - int(0.15 * (ys.max() - ys.min()))
        by, bx = np.nonzero(fg[y0:, :])
        sig.append(float(bx.mean() - xs.mean()) if len(bx) > 10 else np.nan)
    rd.close()
    md["n_frames"] = n
    return np.asarray(sig, float), float(md["fps"]), md


def product_frames(indices):
    """pass 2: fetch just the frames the figure needs, composited onto white."""
    import imageio
    want = set(int(i) for i in indices)
    rd = imageio.get_reader(CLIP)
    got = {}
    for i, f in enumerate(rd):
        if i in want:
            got[i] = whiten(f)[0]
        if len(got) == len(want):
            break
    rd.close()
    return got


def autocorr_period(x, dt, lo_s=0.25, hi_s=2.0):
    x = x[np.isfinite(x)]
    x = x - x.mean()
    ac = np.correlate(x, x, mode="full")[len(x) - 1:]
    ac = ac / ac[0]
    lo, hi = int(lo_s / dt), min(int(hi_s / dt), len(ac) - 1)
    lag = int(np.argmax(ac[lo:hi])) + lo
    return lag * dt, float(ac[lag]), lag


def crop_silhouette(im, dark_bg=False, margin=0.06):
    """crop to the robot: on the product frames the duck is a small part of an
    800x1280 portrait, on ours it is a small part of the studio. Without this the
    two rows are not at comparable scale and the figure compares nothing."""
    a = np.asarray(im.convert("RGB")).astype(np.float32).mean(axis=2)
    fg = (a > 12.0) if dark_bg else (a < 250.0)
    ys, xs = np.nonzero(fg)
    if len(xs) < 20:
        return im
    mx = int(margin * max(xs.max() - xs.min(), ys.max() - ys.min()))
    box = (max(0, xs.min() - mx), max(0, ys.min() - mx),
           min(im.size[0], xs.max() + mx), min(im.size[1], ys.max() + mx))
    return im.crop(box)


def main():
    sig, fps, md = product_signal()
    nfr = md["n_frames"]
    dt = 1.0 / fps
    p_period, p_corr, p_lag = autocorr_period(sig, dt)
    # start the product cycle at a maximum of the signal (one foot fully forward)
    s = np.where(np.isfinite(sig), sig, -1e9)
    win = slice(int(1.0 / dt), int(1.0 / dt) + p_lag)
    p_t0 = (int(np.argmax(s[win])) + int(1.0 / dt)) * dt

    nofloor = os.path.join(OUT, "_studio_nofloor_scene.xml")
    open(nofloor, "w").write(compare_render.studio_scene(common.robot_file("ours")))
    rp = MR.Replay(scene_path=nofloor)   # no floor: the product clip has none
    o_period, o_t0, o_corr, o_lag = MR.gait_cycle(rp)
    # our cycle also starts at a maximum of left_knee (gait_cycle does that)
    phases = [0.0, 0.2, 0.4, 0.6, 0.8]
    spec = ("trunk_base", 135, -10, 0.52, 0.0)      # 3/4 front-right = the clip's view

    TW, TH = 330, 470
    pad, top, hdr = 8, 22, 74
    W = len(phases) * (TW + pad) + pad
    H = hdr + 2 * (TH + top + pad) + pad
    canvas = Image.new("RGB", (W, H), (247, 247, 249))
    d = ImageDraw.Draw(canvas)
    f14, f12, f11 = MR.font(15), MR.font(12), MR.font(11)
    d.text((10, 8), "Walking, phase-matched: Pollen's published move clip vs OUR rebuilt CAD in MuJoCo",
           font=f14, fill=(20, 22, 28))
    d.text((10, 30), "product  images/moves-portrait-alpha_walk.webm  %d frames, %.1f fps, %.3f s"
                     "   |  measured gait period %.4f s (autocorr %.3f, lag %d frames)"
           % (nfr, fps, nfr * dt, p_period, p_corr, p_lag), font=f11, fill=(70, 74, 84))
    d.text((10, 46), "ours     out/sim/walk_ours_traj.npz (BEST_alpha_walking, vx 0.25 m/s, our meshes)"
                     "   |  measured gait period %.4f s (autocorr %.3f, lag %d frames at 50 Hz)"
           % (o_period, o_corr, o_lag), font=f11, fill=(70, 74, 84))
    d.text((10, 62), "Pollen's clip is their own RENDER, not a photograph; no photograph of the product "
                     "mid-stride exists in images/. Phases are cycle fractions, not the same wall clock.",
           font=f11, fill=(140, 90, 40))

    pidx = [int(round((p_t0 + ph * p_period) / dt)) % nfr for ph in phases]
    pframes = product_frames(pidx)
    prod_frames_used, our_times = [], []
    for k, ph in enumerate(phases):
        x = pad + k * (TW + pad)
        # product
        idx = int(round((p_t0 + ph * p_period) / dt)) % nfr
        prod_frames_used.append(idx)
        im = crop_silhouette(Image.fromarray(pframes[idx]).convert("RGB"), dark_bg=False)
        im.thumbnail((TW, TH), Image.LANCZOS)
        y = hdr + top
        d.text((x, hdr + 4), "product  phase %.0f%%  frame %d" % (ph * 100, idx), font=f12, fill=(30, 32, 38))
        canvas.paste(im, (x + (TW - im.size[0]) // 2, y + (TH - im.size[1]) // 2))
        # ours
        t = o_t0 + ph * o_period
        our_times.append(round(float(t), 4))
        px = rp.shot(spec, t, 640, 900)
        oi = crop_silhouette(Image.fromarray(px))
        oi.thumbnail((TW, TH), Image.LANCZOS)
        y2 = hdr + TH + top + pad + top
        d.text((x, hdr + TH + top + pad + 4), "ours  phase %.0f%%  t = %.3f s  knee %+.2f deg"
               % (ph * 100, t, rp.angle_deg("left_knee")), font=f12, fill=(30, 32, 38))
        canvas.paste(oi, (x + (TW - oi.size[0]) // 2, y2 + (TH - oi.size[1]) // 2))
    p = os.path.join(OUT, "walk_vs_product.png")
    canvas.save(p)
    doc = {"product_clip": os.path.relpath(CLIP, ROOT),
           "product_clip_meta": {"frames": nfr, "fps": fps, "seconds": round(nfr * dt, 3),
                                 "size": list(md["size"]), "codec": md["codec"]},
           "product_gait_period_s": round(p_period, 4), "product_autocorr_peak": round(p_corr, 4),
           "product_cadence_steps_per_min": round(2 * 60.0 / p_period, 2),
           "product_cycle_start_s": round(p_t0, 4), "product_frames_used": prod_frames_used,
           "ours_gait_period_s": round(o_period, 4), "ours_autocorr_peak": round(o_corr, 4),
           "ours_cadence_steps_per_min": round(2 * 60.0 / o_period, 2),
           "ours_cycle_start_s": round(o_t0, 4), "ours_times_used_s": our_times,
           "period_ratio_ours_over_product": round(o_period / p_period, 4),
           "scene": "out/motion/_studio_nofloor_scene.xml (compare_render studio, no floor)",
           "framing": "both rows cropped to the silhouette bounding box + 6 % margin, then fitted "
                      "to the same tile, so the two are at comparable scale",
           "period_resolution_s": 0.02,
           "camera": "ours at azimuth 135 deg (3/4 front-right), elevation -10, distance 0.52 m, "
                     "tracking trunk_base",
           "caveat": "the product asset is Pollen's own rendered move clip, not a photograph; "
                     "no photograph of the product mid-stride exists in images/",
           "figure": os.path.relpath(p, ROOT),
           "measured_by": "sim/walk_vs_product.py"}
    json.dump(doc, open(os.path.join(OUT, "walk_vs_product.json"), "w"), indent=1)
    print(json.dumps(doc, indent=1))
    print("wrote", p)


if __name__ == "__main__":
    main()
