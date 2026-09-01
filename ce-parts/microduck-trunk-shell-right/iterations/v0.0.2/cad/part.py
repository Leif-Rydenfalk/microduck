"""part:microduck-trunk-shell-<SIDE> — one half of the Microduck's egg-shaped
trunk shell (Pollen's MJCF mesh `left_shell` / `right_shell`), rebuilt.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. Parametric —
nobody has Pollen's CAD. Every number below was READ OFF Pollen's
published mesh `reference/pollen-microduck-rl/assets/<side>_shell.stl`
(metres, decimated) on 2026-09-02 with `cecad.meshslice` (plane cuts,
material intervals, convex outlines), `cecad.meshfeatures.cylinders`
(holes and bosses) and `cad-mjcf sections`; the probe that produced each
number is in its comment. The organic skin is lofted through the measured
outlines in `measured.json` (written by `measure.py` beside this file);
the rebuild is graded against the mesh by `cad-refcheck` (see evidence/).

FRAME — the LEFT mesh's own frame, kept on purpose (the MJCF geom pos
(4, 0, -17.579) mm + quat (0.7071, 0, 0, 0.7071) place it): X is the
robot's width (0 = the midplane between the two halves, +31.764 = the
outboard face), Y is fore-aft (-30.5 = beak side, +50.4 = tail), Z is up
(17.8 .. 59.5). The RIGHT half is modelled in this same frame and mirrored
about the yz plane at the end, so it lands in ITS mesh's frame (x < 0).
The two meshes are true mirrors to 0.01 mm everywhere except the lap
strip and the cross-screw boss (see SIDE_PARAMS).

WHAT IT IS. A drafted, filleted half-egg open at the bottom and toward the
midplane: an outboard wall, a top wall, a full-width front wall (a skirt
that reaches the midplane) and a back wall that only spans the outboard
20..31.8 mm — all 2.2 mm — plus, carried inboard to the midplane, a top-
wall tab (y 24.9..39.9) and the back-top corner block holding the
cross-screw boss that joins the two halves. Features: the XL330 neck-pitch
horn disc (D17 x 1 raised, with the horn's relief pocket and 4 x D2.2 on a
D12 PCD) on a D16.9 x 2.3 plate at the front-top corner; a vertical screw
boss D8 with a D2.2 pilot and a D5.06 access bore; a U-shaped snap hook on
the outboard wall; a 2.2 mm foot at the back-bottom.
"""
import json
import math
import os

SIDE = "right"

HERE = os.path.dirname(os.path.abspath(__file__))
MEASURED = os.path.join(HERE, "measured.json")
MATERIAL = "PLA"

# ---- the skin -------------------------------------------------------------
T_WALL = 2.2          # top wall z 56.41..58.60 at (x18,y15); outboard x 28.85..31.05 at (y0,z30);
#                       front y -17.14..-14.93 at (x18,z28); back y 47.88..50.07 at (x21,z34)  [meshslice.intervals]
X_OUT = 31.764        # bbox x max
X_LAP0 = -1.95        # bbox x min (left): the lap strip that overlaps the right half
X_MAIN0 = 0.05        # front-wall loop at x=0.05 has the full 2.2 wall; right half's bbox max is 0.0
X_TOP_EDGE = 15.6     # top wall's inboard edge: z=57.5 cut, x_at_y10 = 15.6..27.07, x_at_y20 = 15.6..27.55
X_BACK_EDGE = 20.0    # back wall's inboard end: z=19.2 cut x_at_y39 = 20.0..; plan cuts z 25..48 all start at x=20
Y_TAB0 = 24.9         # top-wall tab inboard of x=15.6: hull y 24.72..39.87 at x=8, 24.98..39.84 at x=0.5
Y_BLOCK0 = 38.0       # back-top corner block + boss: hull y_min 38.0 at x=27, 38.8 at x=0.5 (= boss OD edge)
Z_FRONT_TOP = (36.0, 0.035)   # front-wall top edge z = 36.0 + 0.035 x (loops: 36.0 at x=0.05, 36.42 at x=12)
Z_FRONT_BOT = (17.836, 0.043)  # front-wall bottom edge z = 17.836 + 0.043 x (front_zmin: 17.84 at 0.05, 18.70 at 20, 18.88 at 24)
FRONT_BOT_CORNER = [(24.0, 18.879), (25.0, 19.031), (26.0, 19.342), (27.0, 19.832), (28.0, 19.947)]  # front_zmin x 24..28 (the plan corner round)
Z_LAP_FRONT_BOT = 19.13       # front-wall loop at x=-1.9: z 19.13..35.93 (the lap strip stops 1.3 higher)
Z_BOTTOM = 19.75      # skin bottom edge outboard: x=28.0 z_min 19.75; side wall exists at z=19.8 (y=10)
LAP_OFFSET = 1.2      # lap strip = the inner 1.0 of the wall: x=-1.5 top wall z 57.24..58.22 vs 57.13..59.35 at x=0.5;
#                       front wall at x=-1.9 y -17.2..-13.04 vs -18.37..-12.98 at x=0.05
N_SECTION = 120       # points per lofted section (arc-length resample of the measured outline);
#                       polygon wires (smooth=False): BOP flagged the interpolated B-spline wires
#                       GeomAbs_C0 and left boolean junk (r1); a 120-gon on the R3 corners is 0.15 mm sagitta
Z_PUSH = 14.0         # sections whose bottom is the cut plane are carried down to here and cut back

# ---- the foot (ledge) at the back-bottom -------------------------------------
LEDGE_Y0 = 23.0       # z=19.2 cut: y_at_x24 = 23.14..41.19; plan cut z=19.3 front edge y=23
LEDGE_X0_LOW = 22.0   # z=19.2 cut: x_at_y30 = 22.0..27.2
LEDGE_X0_HIGH = 20.0  # z=19.2 cut: x_at_y39 = 20.0..26.3
LEDGE_Y_STEP = 36.5   # plan cut z=19.3: the inboard edge steps from x=22 to x=20 at y=36.5
LEDGE_BOT = (17.23, 0.04)   # z = 17.23 + 0.04 x: ledge z_min 18.07 at x=21, 18.19 at x=24
LEDGE_T = 2.25        # z 18.11..20.31 at (x22.5,y30), 18.19..20.40 at (x24,y30)

# ---- the snap hook on the outboard wall ---------------------------------------
HOOK_Y = (23.46, 28.54)      # y_at_x26_z44: (23.458,24.842),(27.158,28.542) -> arms 1.38 thick
HOOK_SLOT_Y = (24.84, 27.16)
HOOK_Z = (38.59, 47.98)      # z_at_x26_y24 = 38.59..47.98
HOOK_WEB_TOP = 39.98         # z_at_x26_y26 = 38.59..39.98 (the web between the arms)
HOOK_X0 = 22.0               # x_at_y24_z44 = 22.03..; x_at_y26_z39.8 = 21.88..
HOOK_TIP = (43.1, 24.0)      # arms end at z 43.1 at x=22 (x=22 cut) and are full height by x=24
HOOK_SLOT_XMAX = 29.3        # the slot runs to the wall's inner face (29.18 at z=40, 29.48 at z=48)

# ---- the vertical screw boss at the front-outboard corner ----------------------
VB_XY = (25.5, -9.5)         # meshfeatures: hole D2.2 axis z at (25.5, -9.5, 41.53) length 1.94
VB_OD = 8.0                  # x_at_y-9.5_z45: wall 21.5..22.96 -> OD 8.0; y -13.5..-5.5 at z=41.5
VB_Z0 = 40.58                # z_at_x25.5_y-6.2 = 40.58..54.4
VB_PILOT = (2.2, 42.5)       # D2.2 from the boss bottom to z 42.5 (hole length 1.94 about 41.53)
VB_BORE = 5.06               # y_at_x25.5_z45: -12.04..-6.96; z_at_x25.5_y-9.5 = [] -> open through the top skin
VB_WEB_XMAX = 30.5           # the boss is D-shaped: filled to the outboard wall between y -13.5 and -5.5

# ---- the cross-screw boss along x in the back-top corner ------------------------
HB_YZ = (42.0, 52.5)         # meshfeatures: hole axis x at (1.0, 42.0, 52.5) (left) / (-2.65, 42, 52.5) (right)
HB_NOTCH_Y0 = 45.8           # y@52.5 at x=0.5: boss wall ..45.07, gap, corner fill from 45.81 (left)
HB_FILL_Z = (51.79, -0.101)  # corner fill underside z = 51.79 - 0.101 x: 51.39 (x=4), 50.85 (10), 50.05 (18), 49.37 (24) at y=46.5
HB_FILL_Y1 = 52.0            # clipped by the skin (back wall outer y 50.3)

SIDE_PARAMS = {
    "left": {
        "lap": True,
        # boss OD 6.10 + 0.0717 x: bottom z 49.43 at x=0.5 -> 48.51 at x=27 about the 52.5 axis
        "od": (6.10, 0.0717),
        # D2.2 clearance x 0..2.0 (meshfeatures length 2.0 about x=1.0), then a drafted bore
        "pilot": (2.2, 2.0),
        # bore D 3.50 at x=2 -> 4.38 at x=27 (z@42 spans 50.74..54.26 at x=2.5, 50.31..54.69 at x=27)
        "bore": (2.0, 3.50, 0.0357),
    },
    "right": {
        "lap": False,
        # boss bottom 49.50 (x=0.5) -> 48.80 (x=27): OD 6.0 + 0.0528 x
        "od": (6.00, 0.0528),
        # D1.6 tapped x 0.3..5.0 (meshfeatures length 4.7 about x=-2.65 in its own frame)
        "pilot": (1.6, 5.0),
        # bore D 3.05 at x=6 -> 4.00 at x=27
        "bore": (5.0, 3.00, 0.0452),
    },
}

# ---- the neck-pitch horn disc and plate at the front-top corner ---------------
DISC_YZ = (-22.0, 50.0)      # 4 x D2.2 holes at (-16,50) (-22,44) (-28,50) (-22,56): PCD 12, centre (-22,50)
DISC_D = 17.0                # relief loop [0] area 226.5 mm2 -> D 16.98
DISC_X = (14.6, 15.6)        # bosses at x=15.1 length 1.01; x_at_y-25.4_z53.4 = 14.6..17.9
PLATE_D = 16.9               # y -30.44 at z=50 -> R 8.44; z 41.55 at y=-22 -> R 8.45
PLATE_X = (15.6, 17.9)       # x_span_at_y-22_z50 = 15.6..17.9
PLATE_FILL_Y1 = -10.18       # y_at_x16.75_z50: material to -10.18 (the plate fills the corner to the cavity round)
PLATE_FILL_Z0 = 43.9         # z_at_x16.75_y-14.5: 43.87..57.61
HORN_HOLE_D = 2.2
HORN_PCD = 12.0

# ---- inboard cuts -----------------------------------------------------------------
BLOCK_BOT_EXTRA = 0.0        # back wall bottom edge inboard of x=20 sits 0.25 above the boss bottom; not modelled


def _od(x, side):
    a, b = SIDE_PARAMS[side]["od"]
    return a + b * x


def _boss_bottom(x, side):
    return HB_YZ[1] - _od(x, side) / 2.0


def _front_bot(x):
    if x < X_MAIN0:
        return Z_LAP_FRONT_BOT
    if x <= FRONT_BOT_CORNER[0][0]:
        return Z_FRONT_BOT[0] + Z_FRONT_BOT[1] * x
    pts = FRONT_BOT_CORNER
    for (x0, z0), (x1, z1) in zip(pts, pts[1:]):
        if x <= x1:
            return z0 + (z1 - z0) * (x - x0) / (x1 - x0)
    return pts[-1][1]


# ---------------------------------------------------------------------------
# sections: measured outlines -> lofted skin and cavity
# ---------------------------------------------------------------------------
def _sections(M):
    """Returns (outer, cavity_main, cavity_dome, lap_inner): lists of
    (points, x) for Part.loft(axis="x"), every section N_SECTION points
    resampled by arc length from the same start ray (a ruled loft between
    same-count sections cannot twist)."""
    from cecad import meshslice as ms
    centre = (16.0, 39.0)

    def rs(P):
        return ms.resample(P, N_SECTION, start_dir=(1.0, 0.0), centre=centre)

    def push(P, thr, z_to=Z_PUSH):
        """Open the section's bottom: clip at z = thr (a clean two-corner
        edge — pushing raw hull points interleaved about the threshold
        made self-intersecting wires, r1) and carry the edge down to
        z_to, where the bottom cutters remove it."""
        P = ms.clip_polygon(P, [(0.0, 1.0, -thr)])
        P = P.copy()
        P[P[:, 1] < thr + 0.05, 1] = z_to
        return P

    def arr(L):
        return ms.hull(L)

    base21 = rs(arr(M["outer_base"]["21.00"]))
    base24 = rs(arr(M["outer_base"]["24.00"]))

    def extrap(x):
        return base21 + (base21 - base24) * ((21.0 - x) / 3.0)

    def cavity_of(H):
        C = ms.offset_polygon(H, T_WALL)
        # 2 mm below the outer's own pushed bottom, so the cavity cuts
        # THROUGH the skin instead of sharing a face with it (r1 collapse)
        return rs(push(C, 22.5, Z_PUSH - 2.0))

    outer, cav_main = [], []
    # inboard end: the straight draft continued past the midplane, cut later.
    # The cavity starts 1 mm beyond the outer so no two loft end faces are
    # coplanar (a coplanar cut collapsed the boolean to 4 slivers, r1).
    H = extrap(-3.0)
    outer.append((rs(push(H, H[:, 1].min() + 3.0)).tolist(), -3.0))
    cav_main.append((cavity_of(extrap(-4.0)).tolist(), -4.0))
    for key in ("21.00", "24.00", "27.00", "28.00"):
        H = arr(M["outer"][key])
        outer.append((rs(push(H, H[:, 1].min() + 0.4)).tolist(), float(key)))
        cav_main.append((cavity_of(H).tolist(), float(key)))
    for key in ("28.50", "29.00", "29.50", "30.00", "30.50", "30.75", "31.00", "31.20", "31.40", "31.55", "31.65", "31.72"):
        H = arr(M["outer"][key])
        outer.append((rs(H).tolist(), float(key)))
    last = arr(M["outer"]["31.72"])
    outer.append(([(float(last[:, 0].mean()), float(last[:, 1].mean()))], X_OUT))

    cav_dome = [cav_main[-1]]
    for key in ("28.40", "28.80", "29.05", "29.25", "29.40", "29.50"):
        H = arr(M["cavity"][key]["hull"])
        cav_dome.append((rs(H).tolist(), float(key)))
    H = arr(M["cavity"]["29.50"]["hull"])
    c = H.mean(axis=0)
    cav_dome.append((rs(c + (H - c) * 0.6).tolist(), 29.62))

    lap = []
    for x in (-4.0, X_MAIN0):
        H = extrap(x)
        C = ms.offset_polygon(H, LAP_OFFSET)
        lap.append((rs(push(C, C[:, 1].min() + 0.4)).tolist(), x))
    return outer, cav_main, cav_dome, lap


def _relief(M):
    return [(float(u), float(v)) for u, v in M["relief"]]


# ---------------------------------------------------------------------------
def build(doc, params=None):
    from cecad.core import Part
    if params:
        raise ValueError("microduck-trunk-shell-%s takes no build parameters (got %s)" % (SIDE, sorted(params)))
    with open(MEASURED) as f:
        M = json.load(f)
    if M["side"] != SIDE:
        raise ValueError("measured.json was measured for the %s shell, this is the %s" % (M["side"], SIDE))
    sp = SIDE_PARAMS[SIDE]
    outer_s, cav_main_s, cav_dome_s, lap_s = _sections(M)

    name = "microduck-trunk-shell-%s" % SIDE
    outer = Part("outer", material=MATERIAL)
    outer.loft(outer_s, axis="x", smooth=False, ruled=True)
    p = Part(name, material=MATERIAL)
    p.merge(outer, "add")

    def clipped(q):
        """A feature stopped at the skin: q ∩ outer."""
        q.merge(outer, "common")
        return q

    # 1. hollow it: the cavity, open at the bottom and toward the midplane
    cav = Part("cavity")
    cav.loft(cav_main_s, axis="x", smooth=False, ruled=True)
    cav.loft(cav_dome_s, axis="x", smooth=False, ruled=True, op="add")
    p.merge(cav, "cut")

    # 2. the bottom: z 19.75 outboard; the front wall hangs lower on a tilted edge
    p.box(40, 120, Z_BOTTOM - 5.0, at=(-5, -8.0, 5.0), op="cut")
    xs = [-5.0, X_MAIN0 - 1e-3, X_MAIN0] + [x for x, _ in FRONT_BOT_CORNER[:1]] + [x for x, _ in FRONT_BOT_CORNER[1:]] + [34.0]
    line = [(_front_bot(x), x) for x in xs]          # (z, x) for a prism along y
    p.prism([(5.0, -5.0)] + line + [(5.0, 34.0)], 32.0, at=(0, -40.0, 0), axis="y", op="cut")

    # 3. inboard of the shell proper: only the front skirt, the top tab and the corner block reach the midplane
    p.box(X_TOP_EDGE + 5, Y_TAB0 + 10.0, 80, at=(-5, -10.0, 0), op="cut")                     # R1
    zt0, zt1 = Z_FRONT_TOP[0] - 5 * Z_FRONT_TOP[1], Z_FRONT_TOP[0] + X_TOP_EDGE * Z_FRONT_TOP[1]
    p.prism([(zt0, -5.0), (90.0, -5.0), (90.0, X_TOP_EDGE), (zt1, X_TOP_EDGE)], 30.0, at=(0, -40.0, 0), axis="y", op="cut")  # R2
    p.prism([(0.0, -5.0), (_boss_bottom(-5.0, SIDE), -5.0), (_boss_bottom(X_BACK_EDGE, SIDE), X_BACK_EDGE), (0.0, X_BACK_EDGE)],
            30.0, at=(0, Y_BLOCK0, 0), axis="y", op="cut")                                          # R4
    if sp["lap"]:
        lap_cut = Part("lap-cut")
        lap_cut.box(X_MAIN0 + 5, 120, 80, at=(-5, -40, 0))
        lap_in = Part("lap-inner")
        lap_in.loft(lap_s, axis="x", smooth=False, ruled=True)
        lap_cut.merge(lap_in, "cut")
        p.merge(lap_cut, "cut")
        p.box(10, 120, 80, at=(X_LAP0 - 10, -40, 0), op="cut")
    else:
        p.box(10, 120, 80, at=(-10 + 0.0, -40, 0), op="cut")

    # 4. the foot at the back-bottom
    foot = Part("foot")
    foot.prism([(LEDGE_X0_LOW, LEDGE_Y0), (28.6, LEDGE_Y0), (28.6, 48.0), (LEDGE_X0_HIGH, 48.0),
                (LEDGE_X0_HIGH, LEDGE_Y_STEP), (LEDGE_X0_LOW, LEDGE_Y_STEP)], 15.0, at=(0, 0, 10.0), axis="z")
    clipped(foot)
    zb = lambda x: LEDGE_BOT[0] + LEDGE_BOT[1] * x
    foot.prism([(5.0, 15.0), (zb(15.0), 15.0), (zb(30.0), 30.0), (5.0, 30.0)], 40.0, at=(0, 15.0, 0), axis="y", op="cut")
    foot.prism([(zb(15.0) + LEDGE_T, 15.0), (30.0, 15.0), (30.0, 30.0), (zb(30.0) + LEDGE_T, 30.0)], 40.0, at=(0, 15.0, 0), axis="y", op="cut")
    p.merge(foot, "add")

    # 5. the snap hook: a U channel standing off the outboard wall
    hook = Part("hook")
    # ends at x=30.5, INSIDE the outboard wall's material (inner face 29.2
    # at z=40, outer 31.4) — merging into the wall needs no skin clip
    hook.prism([(HOOK_Z[0], HOOK_X0), (HOOK_Z[0], 30.5), (HOOK_Z[1], 30.5), (HOOK_Z[1], HOOK_TIP[1]), (HOOK_TIP[0], HOOK_X0)],
               HOOK_Y[1] - HOOK_Y[0], at=(0, HOOK_Y[0], 0), axis="y")
    hook.box(HOOK_SLOT_XMAX - 21.0, HOOK_SLOT_Y[1] - HOOK_SLOT_Y[0], 12.0, at=(21.0, HOOK_SLOT_Y[0], HOOK_WEB_TOP), op="cut")
    p.merge(hook, "add")

    # 6. the vertical screw boss, D-shaped against the outboard wall
    vb = Part("vboss")
    # capped at z=54.4 where it merges into the top wall's underside
    # (z_at_x25.5_y-6.2 = 40.58..54.4) and at x=29.6 inside the wall:
    # nowhere past the outer skin, so no skin clip
    vb.cyl(VB_OD, 54.4 - VB_Z0, at=(VB_XY[0], VB_XY[1], VB_Z0), axis="z")
    vb.box(29.6 - VB_XY[0], VB_OD, 54.0 - VB_Z0, at=(VB_XY[0], VB_XY[1] - VB_OD / 2, VB_Z0))
    p.merge(vb, "add")

    # 7. the cross-screw boss along x and the corner fill behind it
    hb = Part("hboss")
    hb.cone(_od(X_MAIN0, SIDE), _od(33.0, SIDE), 33.0 - X_MAIN0, at=(X_MAIN0, HB_YZ[0], HB_YZ[1]), axis="x")
    clipped(hb)
    p.merge(hb, "add")
    fill = Part("corner-fill")
    fill.box(30.0 - X_MAIN0, HB_FILL_Y1 - HB_NOTCH_Y0, 20.0, at=(X_MAIN0, HB_NOTCH_Y0, 40.0))
    zf = lambda x: HB_FILL_Z[0] + HB_FILL_Z[1] * x
    fill.prism([(30.0, -1.0), (zf(-1.0), -1.0), (zf(31.0), 31.0), (30.0, 31.0)], 20.0, at=(0, 40.0, 0), axis="y", op="cut")
    clipped(fill)
    p.merge(fill, "add")

    # 8. the horn disc, its plate and the corner it fills
    plate = Part("plate")
    plate.cyl(PLATE_D, PLATE_X[1] - PLATE_X[0], at=(PLATE_X[0], DISC_YZ[0], DISC_YZ[1]), axis="x")
    pf = Part("plate-fill")
    pf.box(PLATE_X[1] - PLATE_X[0], PLATE_FILL_Y1 + 30.0, 20.0, at=(PLATE_X[0], -30.0, PLATE_FILL_Z0))
    clipped(pf)
    plate.merge(pf, "add")
    plate.cyl(DISC_D, DISC_X[1] - DISC_X[0], at=(DISC_X[0], DISC_YZ[0], DISC_YZ[1]), axis="x")
    plate.prism(_relief(M), DISC_X[1] - DISC_X[0] + 0.1, at=(DISC_X[0] - 0.1, 0, 0), axis="x", op="cut")
    p.merge(plate, "add")

    # 9. holes, last, through everything
    p.cyl(VB_PILOT[0], VB_PILOT[1] - VB_Z0 + 2.0, at=(VB_XY[0], VB_XY[1], VB_Z0 - 2.0), axis="z", op="cut")
    p.cyl(VB_BORE, 30.0, at=(VB_XY[0], VB_XY[1], VB_PILOT[1]), axis="z", op="cut")
    d_p, x_p = sp["pilot"]
    p.cyl(d_p, x_p + 4.0, at=(-4.0, HB_YZ[0], HB_YZ[1]), axis="x", op="cut")
    x_b, d_b, k_b = sp["bore"]
    p.cone(d_b, d_b + k_b * (33.0 - x_b), 33.0 - x_b, at=(x_b, HB_YZ[0], HB_YZ[1]), axis="x", op="cut")
    r = HORN_PCD / 2
    for dy, dz in ((r, 0), (-r, 0), (0, r), (0, -r)):
        p.cyl(HORN_HOLE_D, 5.0, at=(DISC_X[0] - 0.5, DISC_YZ[0] + dy, DISC_YZ[1] + dz), axis="x", op="cut")
    p.clean()

    sx = 1.0
    if SIDE == "right":
        p.mirror("yz", keep=False)
        sx = -1.0

    def d(s):
        return s if sx > 0 else {"+x": "-x", "-x": "+x"}.get(s, s)
    p.connector("neck_horn", at=(sx * DISC_X[0], DISC_YZ[0], DISC_YZ[1]), dir=d("-x"))
    p.connector("base_screw", at=(sx * VB_XY[0], VB_XY[1], VB_Z0), dir="-z")
    p.connector("cross_screw", at=(sx * X_MAIN0, HB_YZ[0], HB_YZ[1]), dir=d("-x"))
    return p
