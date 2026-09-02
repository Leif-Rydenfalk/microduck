#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""head_verify.py — read every video in out/motion/head.json BACK off disk.

A file that exists is not a file that is correct: this decodes each mp4, pulls
two frames out of the middle of it, checks they are neither blank (std < 1.0)
nor identical to each other (a frozen clip), and writes them to
out/motion/frames/ so a human (and the agent) can look at them.
"""
import json, os, sys
import numpy as np
import imageio.v2 as iio
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "motion")
FR = os.path.join(OUT, "frames")
os.makedirs(FR, exist_ok=True)
J = json.load(open(os.path.join(OUT, "head.json")))
bad = []
for v in J["videos"]:
    p = os.path.join(ROOT, v["mp4"])
    rd = iio.get_reader(p)
    n = v["frames"]
    want = {int(n * 0.28), int(n * 0.72)}
    got = {}
    for i, fr in enumerate(rd):
        if i in want:
            got[i] = np.asarray(fr)
        if len(got) == len(want):
            break
    rd.close()
    for i, px in sorted(got.items()):
        s = float(px.std()); m = float(px.mean())
        f = os.path.join(FR, "%s_f%04d.png" % (v["name"], i))
        Image.fromarray(px).save(f)
        ok = s > 1.0
        print("%-22s frame %4d  mean %6.2f  std %6.2f  %s  %s" % (
            v["name"], i, m, s, "OK" if ok else "BLANK", os.path.relpath(f, ROOT)))
        if not ok:
            bad.append(f)
    ks = sorted(got)
    if len(ks) == 2 and np.array_equal(got[ks[0]], got[ks[1]]):
        print("  FROZEN: the two frames are identical"); bad.append(p)
    for k in ("gif", "sheet"):
        q = os.path.join(ROOT, v[k])
        sz = os.path.getsize(q)
        px = np.asarray(Image.open(q).convert("RGB"))
        print("  %-5s %7.2f MB  std %6.2f  %s" % (k, sz / 1e6, px.std(), v[k]))
        if k == "gif" and sz > 8 * 1024 * 1024:
            bad.append(q)
print("\n%d video(s), %d defect(s)" % (len(J["videos"]), len(bad)))
sys.exit(1 if bad else 0)
