"""sections.py — plane cuts of Pollen's ankle mesh, as ordered contour loops.

Run with FreeCAD's python (numpy, no kernel):
  /Applications/FreeCAD.app/Contents/Resources/bin/python docs/sections.py [mesh.stl] [axis=value ...]
Prints every closed loop the plane cuts (in the two in-plane coordinates,
mm), decimated, and the loop's bbox — this is how the wall outlines, the
under-hull and the outer-face draft of ankle_left.stl were measured on
2026-09-01. cad-mjcf sections gives only the widths; the loops give the shape.
"""
import sys, struct, os
import numpy as np

def load(p, scale=1000.0):
    data = open(p, 'rb').read(); n = struct.unpack('<I', data[80:84])[0]
    arr = np.frombuffer(data[84:84 + n * 50], dtype=np.dtype([('n', '<3f4'), ('v', '<9f4'), ('a', '<u2')]))
    return arr['v'].reshape(-1, 3, 3).astype(float) * scale

def slice_segments(T, axis, val):
    a = "xyz".index(axis); o = [i for i in range(3) if i != a]
    segs = []
    for t in T:
        d = t[:, a] - val
        pts = []
        for i in range(3):
            j = (i + 1) % 3
            if (d[i] < 0) != (d[j] < 0):
                f = d[i] / (d[i] - d[j]); q = t[i] + f * (t[j] - t[i]); pts.append((q[o[0]], q[o[1]]))
        if len(pts) == 2: segs.append(pts)
    return segs

def loops(segs, tol=1e-3):
    segs = [list(s) for s in segs]; out = []
    while segs:
        cur = segs.pop(); pts = [cur[0], cur[1]]
        changed = True
        while changed and segs:
            changed = False
            for k, s in enumerate(segs):
                for e0, e1 in ((0, 1), (1, 0)):
                    if abs(s[e0][0] - pts[-1][0]) < tol and abs(s[e0][1] - pts[-1][1]) < tol:
                        pts.append(s[e1]); segs.pop(k); changed = True; break
                if changed: break
        out.append(np.array(pts))
    return out

def report(T, axis, val, every=6):
    o = [c for c in "xyz" if c != axis]
    lps = loops(slice_segments(T, axis, val))
    print("== %s = %.3f : %d loops" % (axis, val, len(lps)))
    for L in sorted(lps, key=lambda L: -len(L)):
        lo, hi = L.min(0), L.max(0)
        print("  loop %d pts  %s %.3f..%.3f  %s %.3f..%.3f" % (len(L), o[0], lo[0], hi[0], o[1], lo[1], hi[1]))
        print("   " + " ".join("(%.2f,%.2f)" % (p[0], p[1]) for p in L[::every]))

if __name__ == "__main__":
    mesh = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].endswith('.stl') else 'reference/pollen-microduck-rl/assets/ankle_left.stl'
    T = load(mesh)
    cuts = [a for a in sys.argv[1:] if '=' in a] or ["x=31.0", "x=32.0", "x=33.0", "x=34.0", "x=35.5", "x=50", "x=65.5", "x=67", "x=68.5", "x=69.5", "y=22", "y=10", "y=30", "z=-14.5", "z=-18", "z=-21.5", "z=-8", "z=0"]
    for c in cuts:
        ax, v = c.split('='); report(T, ax, float(v))
