"""part:microduck-ankle-left — the left ankle bracket ("ankle_left" in Pollen's MJCF), rebuilt.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. Parametric —
nobody has Pollen's CAD. Every number below was READ OFF Pollen's published
mesh `reference/pollen-microduck-rl/assets/ankle_left.stl` (metres,
decimated) on 2026-09-01 with `cad-mjcf sections`, `cecad.meshfeatures.cylinders`
and the plane-cut loops in `docs/sections.py` (fits in
`out/measure/ankle/fits_ankle_left.txt`), and the rebuild is graded against
that mesh by `cad-refcheck` (evidence/).

FRAME — Pollen's mesh frame, kept on purpose: X runs ACROSS the bracket
between its two walls (bearing wall at x 30.4..35.3, horn wall at
64.7..69.9), Y is the width (0.163 .. 36.663), Z is up (-22.523 .. 2.977).
The ankle axis is the x-line through (y 22.0, z -6.223) — the same axis
the shin's bearing boss sits on. Keeping their frame means the MJCF geom
pos (-22, 6.223, -64.7) / quat (0.5,-0.5,-0.5,-0.5) place this part with no
re-derivation. The RIGHT ankle is this solid mirrored about x = 0
(ankle_right.stl vs x-mirrored ankle_left.stl: max deviation 0.009 mm,
out/measure/ankle/mirror-test.json) — HAND = -1 below.

WHAT IT IS. A U-bracket that straddles the shin/ankle-servo stack: one
wall carries the 15x10x3 bearing (Ø15 pocket behind a Ø14 window), the
other bolts to the XL330 horn (4 x M2 on a 6 mm radius diamond, Ø4.4
counterbores from outside, Ø5 centre). A 2.5 mm plate joins them, with a
rounded R16.3 hull under it (the heel the foot hangs from), one vertical M2
for the foot, two edge notches, and two small blocks with roofed slots
under the +y edge.
"""
import math

HAND = 1                               # +1 left (ankle_left.stl), -1 right (ankle_right.stl = mirror about x=0)

# ---- envelope, measured (mm) ----------------------------------------------
# bbox of ankle_left.stl: x 30.364..69.854, y 0.163..36.663, z -22.523..2.977 (cecad.meshfeatures / numpy)
Y0, Y1 = 0.163, 36.663                 # full width, every y-section spans it
Z_PLATE_BOT, Z_PLATE_TOP = -15.842, -13.342   # y=10 loop: plate top -13.342 / bottom -15.842 (2.5 thick)
YC, ZA = 22.0, -6.223                  # the ankle axis: centre of the Ø14/Ø15/Ø5 holes (meshfeatures) and of every arc
Z_TOP = 2.977                          # bbox z max; the top arc is capped flat here (x=34 loop: y 21.04..22.96 at z 2.98)

# the two outer faces are PLANES inclined in x-z (fit on y=10 and y=30 loops, residual 0.0000):
#   bearing wall  x = 32.1622 + 0.11348 z  -> through (30.364, -15.842) and (32.500, 2.977)
#   horn wall     x = 67.8723 - 0.12507 z  -> through (69.854, -15.842) and (67.500, 2.977)
X_OUT_B_BOT, X_OUT_B_TOP = 30.364, 32.500
X_OUT_H_BOT, X_OUT_H_TOP = 69.854, 67.500
X_IN_B, X_IN_H = 35.3, 64.7            # wall inner faces: y=30 / y=10 loops (35.30 and 64.70 verticals)

# wall outline in y-z (identical on both walls, x=34 and x=65.5 loops):
R_TOP = 9.25                           # top arc about the axis: fit cy 22.000 cz -6.228 R 9.249/9.250
# -y flank: an arc tangent to the plate top at the corner (Y0, Z_PLATE_TOP) AND to the top arc;
# tangency gives R 13.50 (fit: centre (0.166, 0.152) R 13.49, resid 0.007)
# +y flank: the straight line from the corner (Y1, Z_PLATE_TOP) tangent to the top arc
# (fit y = 29.106 - 0.56643 z, distance from axis 9.250)

# under-hull: cylinder about the axis, x 33..67 (z=-18/-20/-21.5 loops), R 16.3 (fit 16.292; z min -22.523)
HULL_R, X_HULL0, X_HULL1 = 16.3, 33.0, 67.0

# channel between the walls cut down to the plate bottom (x=50 loop):
CH_Y_TOP = (10.178, 33.822)            # at z -13.342
CH_Y_BOT = (12.105, 31.895)            # at z -15.842 (straight chamfer, 52 deg)

# two notches on the +-y edges (z=-14.0 / -13.6 loops: y 0.16->1.56 and 36.66->35.26 over x 44..56; floor z -14.64 at x=50)
NOTCH_X0, NOTCH_X1, NOTCH_D, NOTCH_Z = 44.0, 56.0, 1.4, -14.64

# vertical foot screw (meshfeatures): Ø2.2 axis z at (50.0, 4.502), z -15.842..-14.342; Ø4.4 c'bore z -14.342..-13.342
SCREW_X, SCREW_Y, SCREW_D, SCREW_CB_D, SCREW_CB_DEPTH = 50.0, 4.502, 2.2, 4.4, 1.0

# bearing seat (meshfeatures): Ø14 x 30.66..32.5 (the window), Ø15 x 32.5..34.8 (the pocket, 2.3 deep);
# y=22 loop: Ø16 at the inner face x 35.3 -> a 0.5 x 45 deg lead-in from 34.8 to 35.3
BRG_WINDOW_D, X_BRG_STEP = 14.0, 32.5
BRG_POCKET_D, X_BRG_POCKET_END, BRG_LEADIN_D = 15.0, 34.8, 16.0

# horn wall (meshfeatures): Ø5 through at the axis; 4 x Ø2.2 at (22,-12.223) (22,-0.223) (28,-6.223) (16,-6.223)
# i.e. a 6.0 mm radius diamond, x 64.7..66.5; Ø4.4 counterbores from x 66.5 out through the outer face
HORN_CENTRE_D, HORN_SCREW_D, HORN_SCREW_R = 5.0, 2.2, 6.0
HORN_CB_D, X_HORN_CB = 4.4, 66.5

# +y blocks under the plate (z=-17/-19/-21 loops): x 34.1..39.1 and 60.9..65.9, y 31.663..35.663, down to z -21.342
BLOCK_X = ((34.1, 39.1), (60.9, 65.9))
BLOCK_Y0, BLOCK_Y1, BLOCK_Z = 31.663, 35.663, -21.342
# slot in each block (z=-19 loops: x 35.6..37.6, y 33.163..34.163; x=36.6 loop: roof from (34.163,-17.07) to (33.163,-18.10))
SLOT_X = ((35.6, 37.6), (62.4, 64.4))
SLOT_Y0, SLOT_Y1, SLOT_ROOF_Y1, SLOT_ROOF_Y0 = 33.163, 34.163, -17.07, -18.10

MATERIAL = "PLA"


def _flank_radius():
    """R of the -y flank arc: tangent to z = Z_PLATE_TOP at y = Y0 (centre (Y0, Z_PLATE_TOP + R))
    and externally tangent to the top arc: |Q - C| = R_TOP + R."""
    dy = YC - Y0
    dz0 = Z_PLATE_TOP - ZA
    # dy^2 + (R + dz0)^2 = (R_TOP + R)^2  ->  linear in R
    return (dy * dy + dz0 * dz0 - R_TOP * R_TOP) / (2 * (R_TOP - dz0))


def _wall_profile(n=36):
    """(y, z) polygon of a wall seen along +x, plate included."""
    r_fl = _flank_radius()
    qy, qz = Y0, Z_PLATE_TOP + r_fl                      # -y flank centre
    # +y tangent point from the corner P = (Y1, Z_PLATE_TOP)
    px, pz = Y1 - YC, Z_PLATE_TOP - ZA
    th_t = math.atan2(pz, px) + math.acos(R_TOP / math.hypot(px, pz))
    # join with the -y flank arc: along C -> Q
    th_j = math.atan2(qz - ZA, qy - YC)
    pts = [(Y1, Z_PLATE_BOT), (Y1, Z_PLATE_TOP)]
    for i in range(n + 1):
        a = th_t + (th_j - th_t) * i / n
        pts.append((YC + R_TOP * math.cos(a), min(Z_TOP, ZA + R_TOP * math.sin(a))))
    a0 = th_j - math.pi                                  # J seen from Q (th_j - pi lands at -0.28 rad, so the sweep to -pi/2 is the short 74 deg arc, not 434 deg round the back)
    a1 = -math.pi / 2                                    # bottom tangent point (Y0, Z_PLATE_TOP)
    for i in range(1, n + 1):
        a = a0 + (a1 - a0) * i / n
        pts.append((qy + r_fl * math.cos(a), qz + r_fl * math.sin(a)))
    pts.append((Y0, Z_PLATE_BOT))
    return pts


def _x_outer_b(z):
    return X_OUT_B_BOT + (X_OUT_B_TOP - X_OUT_B_BOT) * (z - Z_PLATE_BOT) / (Z_TOP - Z_PLATE_BOT)


def _x_outer_h(z):
    return X_OUT_H_BOT + (X_OUT_H_TOP - X_OUT_H_BOT) * (z - Z_PLATE_BOT) / (Z_TOP - Z_PLATE_BOT)


def build(doc, params=None):
    from cecad.core import Part
    if params:
        raise ValueError("microduck-ankle takes no build parameters (got %s)" % sorted(params))
    p = Part("microduck-ankle-left" if HAND > 0 else "microduck-ankle-right", material=MATERIAL)
    W = Y1 - Y0
    # under-hull first, clipped to the plate bottom
    p.cyl(2 * HULL_R, X_HULL1 - X_HULL0, at=(X_HULL0, YC, ZA), axis="x")
    p.box(X_HULL1 - X_HULL0 + 2, W + 6, 30, at=(X_HULL0 - 1, Y0 - 1, Z_PLATE_BOT), op="cut")
    # the hull's crown (y up to YC + R = 38.3) pokes past the +y face; the reference is FLAT at
    # y = Y1 (bbox y max 36.663 = the wall face), so clip it flush (r2: 48 stray tris, y <= 38.3)
    p.box(X_HULL1 - X_HULL0 + 2, 5, 40, at=(X_HULL0 - 1, Y1, -25), op="cut")
    # the two walls (profile includes the plate under them) and the plate between
    prof = _wall_profile()
    p.prism(prof, X_IN_B - X_OUT_B_BOT + 0.01, at=(X_OUT_B_BOT, 0, 0), axis="x")
    p.prism(prof, X_OUT_H_BOT - X_IN_H + 0.01, at=(X_IN_H - 0.01, 0, 0), axis="x")
    p.box(X_IN_H - X_IN_B + 0.02, W, Z_PLATE_TOP - Z_PLATE_BOT, at=(X_IN_B - 0.01, Y0, Z_PLATE_BOT))
    # +y blocks with their roofed slots
    for (bx0, bx1), (sx0, sx1) in zip(BLOCK_X, SLOT_X):
        p.box(bx1 - bx0, BLOCK_Y1 - BLOCK_Y0, Z_PLATE_BOT - BLOCK_Z + 0.01, at=(bx0, BLOCK_Y0, BLOCK_Z))
        p.prism([(SLOT_Y0, BLOCK_Z - 1), (SLOT_Y1, BLOCK_Z - 1), (SLOT_Y1, SLOT_ROOF_Y1), (SLOT_Y0, SLOT_ROOF_Y0)],
                sx1 - sx0, at=(sx0, 0, 0), axis="x", op="cut")
    # channel between the walls, down to the plate bottom
    p.prism([(CH_Y_TOP[0], Z_PLATE_TOP + 1), (CH_Y_TOP[0], Z_PLATE_TOP), (CH_Y_BOT[0], Z_PLATE_BOT),
             (CH_Y_BOT[1], Z_PLATE_BOT), (CH_Y_TOP[1], Z_PLATE_TOP), (CH_Y_TOP[1], Z_PLATE_TOP + 1)],
            X_IN_H - X_IN_B, at=(X_IN_B, 0, 0), axis="x", op="cut")
    # edge notches
    p.box(NOTCH_X1 - NOTCH_X0, NOTCH_D + 1, 5, at=(NOTCH_X0, Y0 - 1, NOTCH_Z), op="cut")
    p.box(NOTCH_X1 - NOTCH_X0, NOTCH_D + 1, 5, at=(NOTCH_X0, Y1 - NOTCH_D, NOTCH_Z), op="cut")
    # the inclined outer faces: cut everything outside the two measured planes (prism along y takes (z, x))
    zlo, zhi = -30.0, 10.0
    p.prism([(zlo, _x_outer_b(zlo)), (zhi, _x_outer_b(zhi)), (zhi, 20.0), (zlo, 20.0)],
            W + 2, at=(0, Y0 - 1, 0), axis="y", op="cut")
    p.prism([(zlo, _x_outer_h(zlo)), (zhi, _x_outer_h(zhi)), (zhi, 80.0), (zlo, 80.0)],
            W + 2, at=(0, Y0 - 1, 0), axis="y", op="cut")
    # vertical foot screw with its counterbore
    p.cyl(SCREW_D, 10, at=(SCREW_X, SCREW_Y, Z_PLATE_BOT - 5), op="cut")
    p.cyl(SCREW_CB_D, 5, at=(SCREW_X, SCREW_Y, Z_PLATE_TOP - SCREW_CB_DEPTH), op="cut")
    # bearing seat: Ø14 window from outside, Ø15 pocket, 0.5 x 45 lead-in to Ø16 at the inner face
    p.cyl(BRG_WINDOW_D, X_BRG_STEP - 25.0, at=(25.0, YC, ZA), axis="x", op="cut")
    p.cyl(BRG_POCKET_D, X_BRG_POCKET_END - X_BRG_STEP, at=(X_BRG_STEP, YC, ZA), axis="x", op="cut")
    p.cone(BRG_POCKET_D, BRG_LEADIN_D, X_IN_B - X_BRG_POCKET_END + 0.01, at=(X_BRG_POCKET_END, YC, ZA), axis="x", op="cut")
    # horn wall: Ø5 centre, 4 x Ø2.2 on the 6 mm diamond, Ø4.4 counterbores from x 66.5 outwards
    p.cyl(HORN_CENTRE_D, 20, at=(X_IN_H - 5, YC, ZA), axis="x", op="cut")
    for dy, dz in ((0, -HORN_SCREW_R), (0, HORN_SCREW_R), (HORN_SCREW_R, 0), (-HORN_SCREW_R, 0)):
        p.cyl(HORN_SCREW_D, 20, at=(X_IN_H - 5, YC + dy, ZA + dz), axis="x", op="cut")
        p.cyl(HORN_CB_D, 10, at=(X_HORN_CB, YC + dy, ZA + dz), axis="x", op="cut")
    p.clean()
    if HAND < 0:
        p.mirror("yz", at=(0, 0, 0), keep=False)
    # interfaces, as connectors along the ankle axis
    p.connector("bearing_seat", at=(HAND * X_BRG_STEP, YC, ZA), dir="+x" if HAND > 0 else "-x")
    p.connector("horn_face", at=(HAND * X_IN_H, YC, ZA), dir="-x" if HAND > 0 else "+x")
    p.connector("foot_screw", at=(HAND * SCREW_X, SCREW_Y, Z_PLATE_BOT), dir="-z")
    return p
