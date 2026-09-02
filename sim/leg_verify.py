#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""leg_verify.py — read every leg clip back OUT OF THE ENCODED FILE and refuse
a blank, frozen or truncated one.

sim/leg_render.py checks the frames it is about to encode; this checks the mp4
and the gif that actually landed on disk, which is the only thing a reader will
open. Verdicts are written into out/motion/legs_videos.json under "readback".

    /Applications/FreeCAD.app/Contents/Resources/bin/python sim/leg_verify.py
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import imageio.v3 as iio

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(ROOT, "out", "motion")
P = os.path.join(M, "legs_videos.json")
V = json.load(open(P))
bad = []
for v in V:
    rb = {}
    for key in ("mp4", "gif"):
        a = np.asarray(iio.imread(os.path.join(ROOT, v[key]), index=None))
        n = len(a)
        diffs = [float(np.abs(a[i].astype(int) - a[i - 1].astype(int)).mean()) for i in range(1, n)]
        stds = [float(a[i].std()) for i in range(0, n, max(1, n // 24))]
        r = dict(frames=n, shape=list(a.shape[1:]),
                 mean_interframe_diff=round(float(np.mean(diffs)), 4),
                 max_interframe_diff=round(float(max(diffs)), 4),
                 min_sampled_frame_std=round(min(stds), 3),
                 min_pixel=int(a.min()), max_pixel=int(a.max()),
                 bytes=os.path.getsize(os.path.join(ROOT, v[key])))
        r["verdict"] = "PASS"
        if n < 8:
            r["verdict"] = "FAIL truncated"
        elif min(stds) < 3.0:
            r["verdict"] = "FAIL blank frame"
        elif max(diffs) < 0.05:
            r["verdict"] = "FAIL frozen"
        elif key == "gif" and r["bytes"] > 8 * 1024 * 1024:
            r["verdict"] = "FAIL gif over 8 MB"
        rb[key] = r
        if r["verdict"] != "PASS":
            bad.append((v["name"], key, r["verdict"]))
    sheet = os.path.join(ROOT, v["sheet"])
    s = np.asarray(iio.imread(sheet))
    rb["sheet"] = dict(shape=list(s.shape), std=round(float(s.std()), 3),
                       bytes=os.path.getsize(sheet),
                       verdict="PASS" if s.std() > 3.0 else "FAIL blank sheet")
    if rb["sheet"]["verdict"] != "PASS":
        bad.append((v["name"], "sheet", rb["sheet"]["verdict"]))
    v["readback"] = rb
    print("%-22s mp4 %3d f %s  gif %3d f %s  sheet %s" % (
        v["name"], rb["mp4"]["frames"], rb["mp4"]["verdict"],
        rb["gif"]["frames"], rb["gif"]["verdict"], rb["sheet"]["verdict"]))
json.dump(V, open(P, "w"), indent=1)
print("%d clips, %d failures" % (len(V), len(bad)))
if bad:
    raise SystemExit("READBACK FAILURES: %s" % bad)
