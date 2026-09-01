"""measure.py — the organic outlines part.py lofts, read off Pollen's mesh.

Runs under FreeCAD's python (numpy, no kernel):

    /Applications/FreeCAD.app/Contents/Resources/bin/python cad/measure.py

Reads reference/pollen-microduck-rl/assets/<SIDE>_shell.stl (metres -> mm)
with cecad.meshslice and writes cad/measured.json beside this file. It
carries ONLY what a number cannot say — closed outlines of plane cuts:

  outer[x]      convex outer outline of the shell skin in the plane x = X
                (the skin is convex in every such plane; the ledge at the
                back-bottom is part of it, the horn plate is not — x >= 18)
  outer_base    the same at x = 21 and x = 24 with the ledge dropped, the
                two sections part.py extrapolates the inboard walls from
                (the skin is a straight draft between them: top wall
                z_max 58.63 -> 58.31, front y_min -17.47 -> -17.16)
  cavity[x]     the measured inner outline where the outboard wall's
                inner face makes a floor (x 28.4 .. 29.5)
  relief        the relief pocket in the horn disc at x = 15.1, as the
                closed loop of that cut (area 72.9 mm2)
  front_zmin    the bottom edge of the front wall per x

Every scalar (wall thickness, boss sizes, hole sizes, cut planes) lives
in part.py with its own probe; this file is the caliper for outlines.

Frame: the LEFT mesh's own (mm). x = width (0 = the robot's midplane,
+31.764 = the outboard face), y = fore-aft (-30.5 = beak side, +50.4 =
tail), z = up (17.8 .. 59.5). The right shell (x < 0) is measured
mirrored into this frame; part.py mirrors it back. MJCF: body trunk_base,
pos (4, 0, -17.579) mm, quat (0.7071, 0, 0, 0.7071).
"""
import json
import os
import sys

import numpy as np

SIDE = "right"

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.expanduser("~"), "dev", "ce-workshop", "ce-cad"))
from cecad import meshslice as ms  # noqa: E402

REF = os.path.join(DESIGN, "reference", "pollen-microduck-rl", "assets")
MESH = "%s_shell" % SIDE
OUT = os.path.join(HERE, "measured.json")

T = ms.load(os.path.join(REF, MESH + ".stl"), 1000.0)
P = T.reshape(-1, 3)
BB = [P.min(0).round(3).tolist(), P.max(0).round(3).tolist()]
print("mesh", MESH, "bbox", BB)
if BB[1][0] < 5:                              # the right shell lives at x < 0
    T = T.copy()
    T[:, :, 0] *= -1.0
    T = T[:, ::-1, :]                          # keep the winding outward
    P = T.reshape(-1, 3)
    print("mirrored into the left frame: bbox", P.min(0).round(3).tolist(), P.max(0).round(3).tolist())

R = {"mesh": MESH, "side": SIDE, "bbox": BB, "probes": {}}


def hull_at(X, zmin=17.5, ymin=-19.5, drop_ledge=False):
    """Convex hull of the cut x = X above z = zmin and behind y = ymin
    (the horn plate is x <= 17.9, so no station needs a y window in
    practice). drop_ledge removes the back-bottom foot (y > 22, z < 20.7)
    for the two extrapolation bases."""
    S = ms.segments(T, "x", X)
    Q = S.reshape(-1, 2)
    keep = (Q[:, 1] >= zmin) & (Q[:, 0] >= ymin)
    if drop_ledge:
        keep &= ~((Q[:, 0] > 22.0) & (Q[:, 1] < 20.7))
    return ms.hull(Q[keep])


# ---- 1. outer skin outlines ------------------------------------------------
OUTER_X = [18.0, 21.0, 24.0, 27.0, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5, 30.75,
           31.0, 31.2, 31.4, 31.55, 31.65, 31.72]
R["outer"] = {}
for X in OUTER_X:
    H = hull_at(X)
    R["outer"]["%.2f" % X] = np.round(H, 3).tolist()
    print("outer x=%.2f: %d pts, y %.2f..%.2f z %.2f..%.2f" % (X, len(H), H[:, 0].min(), H[:, 0].max(), H[:, 1].min(), H[:, 1].max()))
R["outer_base"] = {}
for X in (21.0, 24.0):
    H = hull_at(X, drop_ledge=True)
    R["outer_base"]["%.2f" % X] = np.round(H, 3).tolist()
    print("base  x=%.2f: %d pts, y %.2f..%.2f z %.2f..%.2f" % (X, len(H), H[:, 0].min(), H[:, 0].max(), H[:, 1].min(), H[:, 1].max()))
R["probes"]["outer"] = "cecad.meshslice.segments(T,'x',X) -> hull of the points with z>=17.5, y>=-19.5; X in %s" % OUTER_X
R["probes"]["outer_base"] = "as outer at x=21 and 24 with the foot (y>22, z<20.7) dropped; x=18 has no back wall below z=49 so its hull is not the skin there"


# ---- 2. the inner outline where the outboard wall makes a floor -------------
def cavity_section(X):
    """Inner outline at x = X: per z row the inner end of the span holding
    the outer front surface and the inner start of the span holding the
    outer back surface; per y column the underside of the top wall.
    Convex hull; floor = the lowest z at which front and back walls are
    two spans (below it the section is one solid: the outboard wall)."""
    S = ms.segments(T, "x", X)
    pts = []
    floor = None
    for z in np.arange(19.8, 59.5, 0.25):
        sp = ms.row_spans(S, z)
        if not sp:
            continue
        yf, yb = sp[0][0], sp[-1][1]
        fi = [s for s in sp if s[0] <= yf + 0.3 <= s[1]]
        bi = [s for s in sp if s[0] <= yb - 0.3 <= s[1]]
        if fi and bi and fi[0] is not bi[0]:
            pts.append((fi[0][1], z))
            pts.append((bi[0][0], z))
            if floor is None:
                floor = float(z)
    for y in np.arange(-16, 50, 0.5):
        sp = ms.row_spans(S[:, :, ::-1], y)
        if len(sp) >= 2:
            pts.append((y, sp[-1][0]))
    pts = np.array(pts)
    if len(pts) < 3:
        return np.zeros((0, 2)), floor
    return ms.hull(pts), floor


R["cavity"] = {}
for X in [28.4, 28.8, 29.05, 29.25, 29.4, 29.5]:
    H, floor = cavity_section(X)
    R["cavity"]["%.2f" % X] = {"hull": np.round(H, 3).tolist(), "floor_z": floor}
    print("cavity x=%.2f: floor z=%s, %d pts, y %.2f..%.2f z %.2f..%.2f" % (X, floor, len(H), H[:, 0].min(), H[:, 0].max(), H[:, 1].min(), H[:, 1].max()))
R["probes"]["cavity"] = "per x-plane: y-rows 0.25 mm -> inner face of the span holding the outer surface; y-columns 0.5 mm -> underside of the top wall; convex hull"

# ---- 3. the relief pocket in the horn disc at x = 15.1 -----------------------
S151 = ms.segments(T, "x", 15.1)
Lr = [L for L in ms.loops(S151) if (L[:, 0] < -12.0).all() and (L[:, 1] > 40).all()]
Lr.sort(key=lambda L: -abs(ms.polygon_area(L)))
areas = [round(abs(ms.polygon_area(L)), 3) for L in Lr]
print("disc loops at x=15.1 (areas):", areas)
R["disc_outer_area"] = areas[0]
R["relief"] = np.round(Lr[1], 3).tolist()
R["relief_area"] = areas[1]
R["probes"]["relief"] = "closed loops of the cut x=15.1 inside y<-12, z>40, by area: [0] the disc outline (area %.1f -> D %.2f), [1] the relief pocket (area %.1f), then 4 x D2.2 holes" % (
    areas[0], 2 * (areas[0] / np.pi) ** 0.5, areas[1])

# ---- 4. the bottom edge of the front wall vs x --------------------------------
R["front_zmin"] = []
for X in [0.05, 2, 4, 8, 12, 16, 20, 24, 25, 26, 27, 28]:
    S = ms.segments(T, "x", X)
    Q = S.reshape(-1, 2)
    f = Q[Q[:, 0] < 0]
    R["front_zmin"].append([X, round(float(f[:, 1].min()), 3)])
print("front wall bottom (x, zmin):", R["front_zmin"])
R["probes"]["front_zmin"] = "min z of the cut x=X over points with y<0"

with open(OUT, "w") as f:
    json.dump(R, f)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
