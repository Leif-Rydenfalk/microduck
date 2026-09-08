"""measure.py — every number in part.py, read off Pollen's mesh.

Runs under FreeCAD's python (numpy, no kernel):

    /Applications/FreeCAD.app/Contents/Resources/bin/python cad/measure.py

Reads reference/pollen-microduck-rl/assets/left_shell.stl (metres -> mm)
with cecad.meshslice and writes cad/measured.json beside this file: the
convex outer outline of the shell in planes x = const, the measured inner
(cavity) outline where the drafted side wall makes a floor, the material
loops of the horn-plate relief at x = 15.1, the tab / corner-block hulls,
and the scalar feature numbers, each with the probe that produced it.
part.py loads that file; nothing in part.py is typed by hand.

Frame: the mesh's own (mm). x = width (0 = the robot's midplane, +31.76 =
the outboard face), y = fore-aft (-30.5 = beak side, +50.4 = tail),
z = up (17.8 .. 59.5). MJCF: body trunk_base, pos (4, 0, -17.579) mm,
quat (0.7071, 0, 0, 0.7071) = a 90 deg turn about z.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.expanduser("~"), "dev", "ce-workshop", "ce-cad"))
from cecad import meshslice as ms  # noqa: E402

REF = os.path.join(DESIGN, "reference", "pollen-microduck-rl", "assets")
MESH = os.environ.get("SHELL_MESH", "left_shell")
OUT = os.path.join(HERE, "measured.json" if MESH == "left_shell" else "measured_%s.json" % MESH)

T = ms.load(os.path.join(REF, MESH + ".stl"), 1000.0)
P = T.reshape(-1, 3)
BB = [P.min(0).round(3).tolist(), P.max(0).round(3).tolist()]
print("mesh", MESH, "bbox", BB)
SIGN = 1.0 if BB[1][0] > 5 else -1.0          # the right shell lives at x < 0
if SIGN < 0:                                   # measure the right shell mirrored into the left's frame
    T = T.copy()
    T[:, :, 0] *= -1.0
    T = T[:, ::-1, :]                          # keep the winding outward
    P = T.reshape(-1, 3)


def sx(level):
    return ms.segments(T, "x", level)          # (u, v) = (y, z)


def spans_y(S, z):                             # material along y at height z, in an x-plane
    return ms.row_spans(S, z)


def spans_z(S, y):                             # material along z at y, in an x-plane
    return ms.row_spans(S[:, :, ::-1], y)


def outer_outline(X, zmin=19.7):
    """Convex hull of the section at x = X above z = zmin: the shell's own
    outline. The horn plate (x 14.6..17.9, y < -13.7) is excluded by
    choosing X >= 18 — sections below x = 18 are extrapolated in
    part.py from x = 18 and x = 21 (the walls are planes tilted 4 deg)."""
    return ms.outline(T, "x", X, window=((-40, 60), (zmin, 70)))


R = {"mesh": MESH, "bbox": BB, "mirrored_into_left_frame": SIGN < 0, "probes": {}}

# ---- 1. outer outlines ------------------------------------------------------
XS_OUTER = [18.0, 21.0, 24.0, 27.0, 28.5, 29.5, 30.0, 30.5, 31.0, 31.3, 31.55, 31.7]
R["outer"] = {}
for X in XS_OUTER:
    H = outer_outline(X)
    R["outer"]["%.2f" % X] = np.round(H, 3).tolist()
    print("outer x=%.2f: %d hull pts, y %.2f..%.2f z %.2f..%.2f" % (X, len(H), H[:, 0].min(), H[:, 0].max(), H[:, 1].min(), H[:, 1].max()))
R["probes"]["outer"] = "cecad.meshslice.outline(T,'x',X, window z>=19.7): convex hull of the plane cut; X in %s" % XS_OUTER

# ---- 2. the side wall: inner and outer x at y = 10 vs z ---------------------
Sy = ms.segments(T, "y", 10.0)                 # (u, v) = (z, x)
prof = []
for z in np.arange(19.8, 59.0, 0.5):
    sp = ms.row_spans(Sy[:, :, ::-1], z)       # spans along x at this z
    sp = [s for s in sp if s[1] > 20]
    if sp:
        prof.append([round(float(z), 2), round(sp[-1][0], 3), round(sp[-1][1], 3)])
R["side_wall_y10"] = prof
R["probes"]["side_wall_y10"] = "plane y=10, spans along x per z (row_spans): [z, x_inner, x_outer] of the outboard wall"
for row in prof[:16]:
    print("  side wall z=%.1f  x %.2f .. %.2f" % tuple(row))

# ---- 3. cavity sections where the drafted wall makes a floor ----------------
def cavity_section(X):
    """Measured inner outline at x = X: per z row the end of the material
    span that contains the outer front surface (+0.3) and the start of
    the span containing the outer back surface (-0.3); per y column the
    start of the last z-span (the top wall's underside). Convex hull."""
    S = sx(X)
    pts = []
    zs = np.arange(19.8, 59.5, 0.25)
    floor = None
    for z in zs:
        sp = spans_y(S, z)
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
    ys = np.arange(-16, 50, 0.5)
    for y in ys:
        sp = spans_z(S, y)
        if len(sp) >= 2:
            pts.append((y, sp[-1][0]))
        elif len(sp) == 1 and sp[0][1] - sp[0][0] > 8:
            pass
    pts = np.array(pts)
    if len(pts) < 3:
        return np.zeros((0, 2)), floor
    return ms.hull(pts), floor


XS_CAV = [28.01, 28.4, 28.8, 29.05, 29.25, 29.4, 29.5]
R["cavity"] = {}
for X in XS_CAV:
    H, floor = cavity_section(X)
    R["cavity"]["%.2f" % X] = {"hull": np.round(H, 3).tolist(), "floor_z": floor}
    if len(H):
        print("cavity x=%.2f: floor z=%s, %d pts, y %.2f..%.2f z %.2f..%.2f" % (X, floor, len(H), H[:, 0].min(), H[:, 0].max(), H[:, 1].min(), H[:, 1].max()))
R["probes"]["cavity"] = "per x-plane: y-rows 0.25 mm -> inner face of the span holding the outer surface; y-columns 0.5 mm -> underside of the top wall; convex hull"

# ---- 4. the tab and the corner block ----------------------------------------
def hull_in_window(X, ylo, yhi, zlo, zhi):
    return ms.outline(T, "x", X, window=((ylo, yhi), (zlo, zhi)))


R["tab_top"] = {}      # the top wall carried inboard (y >= 25.2)
R["block"] = {}        # the solid back-top corner (y >= 38.5, z >= 49)
for X in [-1.9, -1.0, -0.05, 0.05, 0.5, 2.0, 4.0, 8.0, 12.0, 15.55]:
    Ht = hull_in_window(X, 24.0, 40.0, 54.0, 61.0)
    R["tab_top"]["%.2f" % X] = np.round(Ht, 3).tolist()
    Hb = hull_in_window(X, 38.0, 60.0, 48.5, 61.0)
    R["block"]["%.2f" % X] = np.round(Hb, 3).tolist()
    print("tab x=%.2f: top %d pts y %.2f..%.2f | block %d pts y %.2f..%.2f z %.2f..%.2f" % (
        X, len(Ht), Ht[:, 0].min() if len(Ht) else 0, Ht[:, 0].max() if len(Ht) else 0,
        len(Hb), Hb[:, 0].min() if len(Hb) else 0, Hb[:, 0].max() if len(Hb) else 0, Hb[:, 1].min() if len(Hb) else 0, Hb[:, 1].max() if len(Hb) else 0))
for X in [16.5, 19.0, 22.0, 25.0, 27.0, 28.0, 28.6]:
    Hb = hull_in_window(X, 38.0, 60.0, 48.5, 61.0)
    R["block"]["%.2f" % X] = np.round(Hb, 3).tolist()
    print("block x=%.2f: %d pts y %.2f..%.2f z %.2f..%.2f" % (X, len(Hb), Hb[:, 0].min(), Hb[:, 0].max(), Hb[:, 1].min(), Hb[:, 1].max()))
R["probes"]["tab_top"] = "hull of the cut at x=X inside y 24..40, z 54..61 (the top wall alone)"
R["probes"]["block"] = "hull of the cut at x=X inside y 38..60, z 48.5..61 (top wall + boss + back corner, one solid)"

# the screw boss along x at (y 42, z 52.5)
boss = {}
for X in [-1.9, -1.0, 0.5, 1.5, 2.5, 4.0, 6.0, 10.0, 14.0, 17.0, 18.5, 20.0, 24.0, 27.0]:
    S = sx(X)
    boss["%.2f" % X] = {"z_at_y42": spans_z(S, 42.0), "y_at_z52.5": spans_y(S, 52.5)}
R["boss"] = boss
R["probes"]["boss"] = "per x-plane: spans along z at y=42 and along y at z=52.5 through the boss axis"
for k, v in boss.items():
    print("boss x=%s z@42: %s  y@52.5: %s" % (k, v["z_at_y42"], v["y_at_z52.5"]))

# ---- 5. D-boss at the front-top, hook, ledge ---------------------------------
S25 = sx(25.5)
Sz45 = ms.segments(T, "z", 45.0)               # (u, v) = (x, y)
R["dboss"] = {
    "y_at_x25.5_z45": spans_y(S25, 45.0),
    "x_at_y-9.5_z45": ms.row_spans(Sz45, -9.5),
    "x_at_y-6.5_z45": ms.row_spans(Sz45, -6.5),
    "z_at_x25.5_y-6.2": spans_z(S25, -6.2),
    "z_at_x25.5_y-12.6": spans_z(S25, -12.6),
    "z_at_x25.5_y-9.5": spans_z(S25, -9.5),
    "y_at_x25.5_z41.5": spans_y(S25, 41.5),
    "y_at_x25.5_z56": spans_y(S25, 56.0),
    "y_at_x25.5_z58": spans_y(S25, 58.0),
}
for k, v in R["dboss"].items():
    print("dboss", k, v)
Sz44 = ms.segments(T, "z", 44.0)
S26 = sx(26.0)
R["hook"] = {
    "x_at_y24_z44": ms.row_spans(Sz44, 24.0),
    "x_at_y26_z39.8": ms.row_spans(ms.segments(T, "z", 39.8), 26.0),
    "x_at_y26_z38.8": ms.row_spans(ms.segments(T, "z", 38.8), 26.0),
    "y_at_x26_z44": spans_y(S26, 44.0),
    "z_at_x26_y24": spans_z(S26, 24.0),
    "z_at_x26_y26": spans_z(S26, 26.0),
    "z_at_x28.5_y26": spans_z(sx(28.5), 26.0),
}
for k, v in R["hook"].items():
    print("hook", k, v)
Sz19 = ms.segments(T, "z", 19.2)
Hl = ms.outline(T, "z", 19.2, window=((15, 29), (21, 46)))
R["ledge"] = {"plan_hull_z19.2": np.round(Hl, 3).tolist(),
              "z_at_x24_y30": spans_z(sx(24.0), 30.0),
              "z_at_x22_y39": spans_z(sx(22.0), 39.0),
              "x_at_y30_z19.2": ms.row_spans(Sz19, 30.0),
              "x_at_y39_z19.2": ms.row_spans(Sz19, 39.0),
              "y_at_x24_z19.2": ms.row_spans(Sz19[:, :, ::-1], 24.0)}
for k, v in R["ledge"].items():
    print("ledge", k, v if k != "plan_hull_z19.2" else "%d pts" % len(v))

# ---- 6. the horn plate --------------------------------------------------------
S167 = sx(16.75)
R["plate"] = {
    "x_span_at_y-22_z50": ms.row_spans(ms.segments(T, "z", 50.0), -22.0),
    "x_span_at_y-26_z47": ms.row_spans(ms.segments(T, "z", 47.0), -26.0),
    "y_at_x16.75_z50": spans_y(S167, 50.0),
    "y_at_x16.75_z44": spans_y(S167, 44.0),
    "y_at_x16.75_z42": spans_y(S167, 42.0),
    "y_at_x16.75_z40": spans_y(S167, 40.0),
    "y_at_x16.75_z38": spans_y(S167, 38.0),
    "y_at_x16.75_z56": spans_y(S167, 56.0),
    "z_at_x16.75_y-22": spans_z(S167, -22.0),
    "z_at_x16.75_y-16": spans_z(S167, -16.0),
    "z_at_x16.75_y-14.5": spans_z(S167, -14.5),
    "y_at_x15.1_z56": spans_y(sx(15.1), 56.0),
    "y_at_x15.1_z50": spans_y(sx(15.1), 50.0),
    "y_at_x15.1_z53.4": spans_y(sx(15.1), 53.4),
    "x_at_y-22_z56": ms.row_spans(ms.segments(T, "z", 56.0), -22.0),
    "x_at_y-25.4_z53.4": ms.row_spans(ms.segments(T, "z", 53.4), -25.4),
    "x_at_y-22_z53.07": ms.row_spans(ms.segments(T, "z", 53.07), -22.0),
}
for k, v in R["plate"].items():
    print("plate", k, v)
# the plate's own outline at x = 16.75: material loops restricted to y < -12.3
Lp = ms.loops(S167)
plate_loops = [L for L in Lp if (L[:, 0] < -12.3).any() and abs(ms.polygon_area(L)) > 5]
R["plate"]["loops_x16.75"] = [np.round(L, 3).tolist() for L in plate_loops]
print("plate loops at x=16.75:", [(len(L), round(ms.polygon_area(L), 1)) for L in plate_loops])
# the relief pattern at x = 15.1: every loop, with its nesting depth
S151 = sx(15.1)
Lr = [L for L in ms.loops(S151) if (L[:, 0] < -12.0).all() and (L[:, 1] > 40).all()]


def inside(pt, L):
    x, y = pt
    n = len(L)
    c = False
    for i in range(n):
        x1, y1 = L[i]
        x2, y2 = L[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xi = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if xi > x:
                c = not c
    return c


relief = []
for L in Lr:
    depth = sum(1 for M in Lr if M is not L and abs(ms.polygon_area(M)) > abs(ms.polygon_area(L)) and inside(L[0], M))
    relief.append({"depth": depth, "area": round(ms.polygon_area(L), 3), "pts": np.round(L, 3).tolist()})
R["relief_x15.1"] = relief
print("relief loops at x=15.1:", [(r["depth"], r["area"], len(r["pts"])) for r in relief])

# ---- 7. the front wall inboard of the shell (x < 15.6) -----------------------
R["front_wall"] = {}
for X in [-1.9, -1.0, -0.05, 0.05, 0.5, 4.0, 8.0, 12.0, 15.55]:
    S = sx(X)
    Lw = [L for L in ms.loops(S) if (L[:, 0] < -10).all() and (L[:, 1] < 40).all() and abs(ms.polygon_area(L)) > 3]
    R["front_wall"]["%.2f" % X] = [np.round(L, 3).tolist() for L in Lw]
    print("front wall x=%.2f: loops %s" % (X, [(len(L), round(ms.polygon_area(L), 1), round(L[:, 0].min(), 2), round(L[:, 0].max(), 2), round(L[:, 1].min(), 2), round(L[:, 1].max(), 2)) for L in Lw]))
R["probes"]["front_wall"] = "closed material loops of the cut at x=X with y<-10, z<40: the front wall alone"

# ---- 8. the top wall's tilt in x, the inboard edge of the top wall ------------
top = {}
for X in [-1.5, 0.5, 5.0, 10.0, 15.0, 15.7, 18.0, 21.0, 25.0]:
    top["%.2f" % X] = {"z_at_y15": spans_z(sx(X), 15.0), "z_at_y30": spans_z(sx(X), 30.0)}
R["top_wall"] = top
for k, v in top.items():
    print("top x=%s: %s" % (k, v))
Sz575 = ms.segments(T, "z", 57.5)
R["top_edge_z57.5"] = {"y_at_x8": ms.row_spans(Sz575[:, :, ::-1], 8.0), "y_at_x12": ms.row_spans(Sz575[:, :, ::-1], 12.0),
                       "x_at_y10": ms.row_spans(Sz575, 10.0), "x_at_y20": ms.row_spans(Sz575, 20.0),
                       "x_at_y30": ms.row_spans(Sz575, 30.0), "x_at_y40": ms.row_spans(Sz575, 40.0)}
print("top edge z57.5", R["top_edge_z57.5"])

with open(OUT, "w") as f:
    json.dump(R, f)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
