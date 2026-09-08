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


def verdict(a):
    """the one place a clip is judged, so the self-test grades the same code the
    real check runs."""
    n = len(a)
    diffs = [float(np.abs(a[i].astype(int) - a[i - 1].astype(int)).mean()) for i in range(1, n)] or [0.0]
    stds = [float(a[i].std()) for i in range(0, n, max(1, n // 24))]
    v = "PASS"
    if n < 8:
        v = "FAIL truncated"
    elif min(stds) < 3.0:
        v = "FAIL blank frame"
    elif max(diffs) < 0.05:
        v = "FAIL frozen"
    return v, dict(frames=n, mean_interframe_diff=round(float(np.mean(diffs)), 4),
                   max_interframe_diff=round(float(max(diffs)), 4),
                   min_sampled_frame_std=round(min(stds), 3))


def self_test():
    """break it on purpose: three clips that MUST be refused, graded by verdict()."""
    import imageio, tempfile
    d = tempfile.mkdtemp()
    blank = [np.full((240, 320, 3), 255, np.uint8) for _ in range(40)]
    ramp = np.tile(np.linspace(0, 255, 320, dtype=np.uint8), (240, 1))[:, :, None].repeat(3, 2)
    cases = [("blank", blank, "FAIL blank frame"), ("frozen", [ramp] * 40, "FAIL frozen"),
             ("truncated", blank[:4], "FAIL truncated")]
    ok = True
    for nm, fr, want in cases:
        p = os.path.join(d, nm + ".mp4")
        imageio.mimwrite(p, fr, fps=10, quality=8, macro_block_size=8)
        got, st = verdict(np.asarray(iio.imread(p, index=None)))
        print("self-test %-10s want %-16s got %-16s %s" % (nm, want, got, "OK" if got == want else "BROKEN"))
        ok &= (got == want)
    print("self-test:", "the check fires on all three failure modes" if ok else "THE CHECK IS BROKEN")
    return ok
M = os.path.join(ROOT, "out", "motion")
P = os.path.join(M, "legs_videos.json")
if "--self-test" in sys.argv:
    raise SystemExit(0 if self_test() else 1)

V = json.load(open(P))
bad = []
for v in V:
    rb = {}
    for key in ("mp4", "gif"):
        a = np.asarray(iio.imread(os.path.join(ROOT, v[key]), index=None))
        vd, st = verdict(a)
        r = dict(shape=list(a.shape[1:]), min_pixel=int(a.min()), max_pixel=int(a.max()),
                 bytes=os.path.getsize(os.path.join(ROOT, v[key])), **st)
        if vd == "PASS" and key == "gif" and r["bytes"] > 8 * 1024 * 1024:
            vd = "FAIL gif over 8 MB"
        r["verdict"] = vd
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
