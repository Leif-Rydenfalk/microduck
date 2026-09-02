"""part:microduck-yaw-roll-motion — the head-yaw output cage
("yaw_roll_motion" in Pollen's MJCF), rebuilt parametrically.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. There is no
geometry/*.step because nobody has Pollen's CAD. Every number below was
READ OFF Pollen's published mesh — graded against
`reference/pollen-microduck-simulator/meshes/yaw_roll_motion.stl` (the
canonical vendor file for this part; the copy in
reference/pollen-microduck-rl/assets/ is a denser re-export committed
2026-09-02 with the SAME bbox 34 x 35.9 x 22.5, used for the feature and
slice measurements below because its cylinders resolve at 355 deg
coverage) — on 2026-09-02 with `cecad.meshslice` (sheets in
out/measure/neckgrp/yr_slices_{x,y,z}.png + intervals probes quoted per
number) and `cecad.meshfeatures.cylinders`, and the rebuild is graded by
`ce-cad/bin/cad-refcheck` (see evidence/).

FRAME — Pollen's mesh frame, kept on purpose: x -24.5..9.5, y -18..17.9,
z -4.5..18. The head-yaw axis is mesh z; the head-roll axis is mesh y
through (x 0, z 4.5).

WHAT IT IS. The cage that hangs the head-yaw XL330 and offers the
head-roll joint:
  * TOP PLATE z 16..18, outline x -24.5..9.5, y -13..15 (45 deg corner
    chamfers at the left corners; the y > 13 strip only from x -16.5),
    with two rectangular windows and a slot over the servo, 4 x Ø2.5
    case-screw holes ((-22.5, +-8) and (7.5, +-8) — the XL330's 30 x 16
    case pattern), Ø4.6 x 0.5 countersinks on the (7.5, +-8) pair, and a
    1 x 1 45 deg chamfer round the top rim (y edges + x max edge).
  * The yaw servo hangs under it between a LEFT WALL (y 10..13) and
    side ribs; its horn (pointing down) bolts to neck_pitch's top boss.
  * ROLL SIDE (-y): a cheek plate — Ø18 disc about the roll axis
    carrying a Ø16 x 4 boss (bearing seat, face y -18) with a Ø12
    through bore, plus a tangent web up to the top plate.
  * HORN SIDE (+y): the mirrored cheek with the XL330 horn pattern: Ø18
    disc + Ø16 x 1.9 boss (face y 17.9), Ø6 centre bore, 4 x Ø2.2 on a
    Ø12 circle, counterbored Ø4.4 from y 12 — the head-roll servo (in
    the head's motor_support) bolts its horn here.
"""

import math

# ---- measured off yaw_roll_motion (mm) --------------------------------------
# bbox: x -24.5..9.5, y -18..17.9, z -4.5..18 (meshslice.load vertices; the
# sim mesh decimates z min to -4.466)
ROLL = (0.0, 4.5)                 # roll axis (x, z): every feature centre
Z_PLATE0, Z_PLATE1 = 16.0, 18.0   # top plate: z at (x-20,y0): (16.0, 18.0)
PX0, PX1 = -24.5, 9.5             # plate x: x at (y-12.6,z17) + bbox
PY0, PY1 = -13.0, 15.0            # plate y: y at (x9.3,z17): (-13.0, 15.0)
PY1_LEFT = 13.0                   # y at (x-18..-21,z17): (-13, 13)
TAB_X0 = -16.518                  # the y 13..15 strip starts here: x at (y14,z17)
CORNER = 2.0                      # 45 deg corner chamfers: y at (x-24.3,z17) +-11.2,
                                  #   (x-23,z17) +-12.5 -> lines x+-y = -35.5
# plate windows (all through, z probes at 16.5 and 17 identical):
WIN_A = (-14.25, -3.75, -10.0, -6.0)   # x0,x1,y0,y1: x at (y-8,z17) gap; y at (x-10,z17) gap
WIN_B = (-14.25, -3.75, 6.0, 13.0)     # y at (x-10,z17) gap 6..13
SLOT_C = (-14.25, -12.25, 13.0, 15.0)  # x at (y14.9,z17) gap -14.25..-12.25
SCREW_D = 2.5                     # 4x, meshfeatures: (-22.5,+-8) len 2.0, (7.5,+-8) len 1.5
SCREWS = ((-22.5, 8.0), (-22.5, -8.0), (7.5, 8.0), (7.5, -8.0))
CSK_D, CSK_Z = 4.6, 17.5          # Ø4.6 x 0.5 pockets at (7.5,+-8): meshfeatures len 0.5 at z 17.75
RIM_CH = 1.0                      # top rim chamfer: y at (x0,z17.9): -12.1..14.1 (1 in at 0.9 up)
# tab under the y 13..15 strip: material 13..18 at (x-15,y13.5); y at
# (x-10,z14.5): (13,15)
TAB_Z0 = 13.0
# left wall: x at (y11.5,z14): (-24.0,-14.25); y at (x-20,z14): (10,13);
# z at (x-20,y11.5): (13,18)
LWALL = (-24.0, -14.25, 10.0, 13.0, 13.0, 16.0)
# two small ribs beside the servo pocket, same band (x pieces at (y11.5,z14))
RIB1_X = (-3.75, -2.488)
RIB2_X = (8.238, 9.5)
# cheeks: disc R9 about the roll axis + tangent web; tangent line fitted to
# bottom-edge probes (x-22,y-12.7) z 10.94 / (-20) 9.30 / (-15) 5.19 /
# (-10) 1.07: z = -2.46 - 0.822*(x + 5.72), tangent to the R9 circle at
# (-5.72, -2.46); right edge drafted: (9.015, z4.5) -> (9.443, z12)
R_CHEEK = 9.0
TANGENT_PT = (-5.72, -2.46)
TAN_SLOPE = -0.822
ROLL_X0_ROLLSIDE = -22.8          # cheek left edge, roll side: x at (y-12.7,z12..15.5)
ROLL_X0_HORNSIDE = -12.25         # horn side: x at (y13.5,z6..12)
# roll side (-y): disc y -14..-10 (4 thick: y at (x8.6,z2): (-14,-10)); web
# 3 thick (y at (x-22,z13): (-13,-10)); boss + bore from meshfeatures:
ROLL_DISC_D, ROLL_DISC_Y = 18.0, (-14.0, -10.0)
ROLL_BOSS_D, ROLL_BOSS_Y = 16.0, (-18.0, -14.0)   # boss d16 len 4.0 face y -18
ROLL_BORE_D, ROLL_BORE_Y = 12.0, (-18.0, -10.0)   # hole d12 len 8.0
# horn side (+y): cbore wall y 12..14.5 (cbores len 2.5 at y 13.25), disc
# y 14.5..16 (y at (x0,z-3): 14.5..17.9 minus boss), boss y 16..17.9
HORN_WALL_Y = (12.0, 14.5)
HORN_DISC_Y = (14.5, 16.0)
HORN_BOSS_Y = (16.0, 17.9)
HORN_BORE_D = 6.0                 # d6 len 5.9 centre y 14.95 -> y 12..17.9
HORN_HOLE_D, HORN_R = 2.2, 6.0    # 4x d2.2 len 3.4 at y 16.2 on Ø12 circle
HORN_CBORE_D = 4.4
MATERIAL = "PLA"


def _cheek_outline(x_left):
    """(z, x) outline of a cheek (prism axis 'y' takes (z, x)): left edge at
    x_left, tangent web line, R9 disc about the roll axis, drafted right
    edge, top at z 16 (merges into the plate)."""
    zc, xc = ROLL[1], ROLL[0]
    pts = [(Z_PLATE0, x_left)]
    # down the left edge to the tangent line: z where line hits x_left
    z_at_left = zc  # placeholder replaced below
    # tangent line: x = -5.72 + (z + 2.46) / TAN_SLOPE  (z as function of x):
    # z = -2.46 + TAN_SLOPE * (x + 5.72)... slope in dz/dx is -0.822 going left
    z_at_left = -2.46 - 0.822 * (x_left + 5.72)
    pts.append((z_at_left, x_left))
    # tangent point on the circle
    pts.append((TANGENT_PT[1], TANGENT_PT[0]))
    # arc about (zc, xc): from the tangent point round the bottom to (zc, +9)
    a0 = math.atan2(TANGENT_PT[0] - xc, TANGENT_PT[1] - zc)   # ~219.4 deg
    if a0 > 0:
        a0 -= 2 * math.pi
    a1 = math.pi / 2 - 2 * math.pi                             # sweep down through 180
    n = 24
    # go from a0 decreasing to -270 deg (= +90 deg): through bottom (180)
    a_end = -3 * math.pi / 2
    for i in range(1, n + 1):
        a = a0 + (a_end - a0) * i / n
        pts.append((zc + R_CHEEK * math.cos(a), xc + R_CHEEK * math.sin(a)))
    # drafted right edge: (9.015, z 4.5) -> (9.443, z 12) -> capped 9.5
    pts.append((12.0, 9.443))
    pts.append((13.3, 9.5))
    pts.append((Z_PLATE0, 9.5))
    return pts


def build(doc, params=None):
    from cecad.core import Part
    if params:
        raise ValueError("microduck-yaw-roll-motion takes no build parameters (got %s)" % sorted(params))
    p = Part("microduck-yaw-roll-motion", material=MATERIAL)
    # ---- top plate (prism axis z takes (x, y)) with chamfered left corners
    p.prism([(PX0, PY0 + CORNER), (PX0 + CORNER, PY0), (PX1, PY0),
             (PX1, PY1), (TAB_X0, PY1), (TAB_X0, PY1_LEFT),
             (PX0 + CORNER, PY1_LEFT), (PX0, PY1_LEFT - CORNER)],
            Z_PLATE1 - Z_PLATE0, at=(0, 0, Z_PLATE0), axis="z")
    # tab under the y 13..15 strip
    p.box(PX1 - TAB_X0, PY1 - PY1_LEFT, Z_PLATE0 - TAB_Z0 + 0.01,
          at=(TAB_X0, PY1_LEFT, TAB_Z0))
    # windows + slot
    for x0, x1, y0, y1 in (WIN_A, WIN_B):
        p.box(x1 - x0, y1 - y0, 3, at=(x0, y0, Z_PLATE0 - 0.5), op="cut")
    x0, x1, y0, y1 = SLOT_C
    p.box(x1 - x0, y1 - y0 + 0.1, Z_PLATE1 - TAB_Z0 + 1, at=(x0, y0, TAB_Z0 - 0.5), op="cut")
    # case screws + countersinks
    for sx, sy in SCREWS:
        p.cyl(SCREW_D, 3, at=(sx, sy, Z_PLATE0 - 0.5), axis="z", op="cut")
    for sx, sy in ((7.5, 8.0), (7.5, -8.0)):
        p.cyl(CSK_D, Z_PLATE1 - CSK_Z + 0.5, at=(sx, sy, CSK_Z), axis="z", op="cut")
    # top rim 45 deg chamfers: +y, -y edges (prism axis x takes (y, z)) and
    # +x edge (prism axis y takes (z, x))
    p.prism([(PY1 - RIM_CH, Z_PLATE1), (PY1, Z_PLATE1 - RIM_CH), (PY1 + 1.5, Z_PLATE1 - RIM_CH),
             (PY1 + 1.5, Z_PLATE1 + 1.5), (PY1 - RIM_CH, Z_PLATE1 + 1.5)],
            40, at=(PX0 - 1, 0, 0), axis="x", op="cut")
    p.prism([(PY0 + RIM_CH, Z_PLATE1), (PY0, Z_PLATE1 - RIM_CH), (PY0 - 1.5, Z_PLATE1 - RIM_CH),
             (PY0 - 1.5, Z_PLATE1 + 1.5), (PY0 + RIM_CH, Z_PLATE1 + 1.5)],
            40, at=(PX0 - 1, 0, 0), axis="x", op="cut")
    p.prism([(Z_PLATE1 - RIM_CH, PX1), (Z_PLATE1, PX1 - RIM_CH), (Z_PLATE1 + 1.5, PX1 - RIM_CH),
             (Z_PLATE1 + 1.5, PX1 + 1.5), (Z_PLATE1 - RIM_CH, PX1 + 1.5)],
            40, at=(0, -19, 0), axis="y", op="cut")
    # ---- left wall + ribs
    x0, x1, y0, y1, z0, z1 = LWALL
    p.box(x1 - x0, y1 - y0, z1 - z0 + 0.01, at=(x0, y0, z0))
    for rx0, rx1 in (RIB1_X, RIB2_X):
        p.box(rx1 - rx0, 3.0, Z_PLATE0 - TAB_Z0 + 0.01, at=(rx0, 10.0, TAB_Z0))
    # ---- cheeks (prism axis y takes (z, x))
    p.prism(_cheek_outline(ROLL_X0_ROLLSIDE), 3.0, at=(0, -13.0, 0), axis="y")
    p.prism(_cheek_outline(ROLL_X0_HORNSIDE), HORN_WALL_Y[1] - HORN_WALL_Y[0],
            at=(0, HORN_WALL_Y[0], 0), axis="y")
    # roll-side disc + boss, bore
    p.cyl(ROLL_DISC_D, ROLL_DISC_Y[1] - ROLL_DISC_Y[0] + 0.01,
          at=(ROLL[0], ROLL_DISC_Y[0], ROLL[1]), axis="y")
    p.cyl(ROLL_BOSS_D, ROLL_BOSS_Y[1] - ROLL_BOSS_Y[0] + 0.01,
          at=(ROLL[0], ROLL_BOSS_Y[0], ROLL[1]), axis="y")
    p.cyl(ROLL_BORE_D, ROLL_BORE_Y[1] - ROLL_BORE_Y[0] + 1,
          at=(ROLL[0], ROLL_BORE_Y[0] - 0.5, ROLL[1]), axis="y", op="cut")
    # horn-side disc + boss, bore, screws, counterbores
    p.cyl(ROLL_DISC_D, HORN_DISC_Y[1] - HORN_DISC_Y[0] + 0.01,
          at=(ROLL[0], HORN_DISC_Y[0] - 0.01, ROLL[1]), axis="y")
    p.cyl(ROLL_BOSS_D, HORN_BOSS_Y[1] - HORN_BOSS_Y[0],
          at=(ROLL[0], HORN_BOSS_Y[0] - 0.01, ROLL[1]), axis="y")
    p.cyl(HORN_BORE_D, HORN_BOSS_Y[1] - HORN_WALL_Y[0] + 1,
          at=(ROLL[0], HORN_WALL_Y[0] - 0.5, ROLL[1]), axis="y", op="cut")
    for du, dv in ((HORN_R, 0), (-HORN_R, 0), (0, HORN_R), (0, -HORN_R)):
        p.cyl(HORN_HOLE_D, 4, at=(ROLL[0] + du, HORN_DISC_Y[0] - 0.1, ROLL[1] + dv),
              axis="y", op="cut")
        p.cyl(HORN_CBORE_D, HORN_WALL_Y[1] - HORN_WALL_Y[0] + 0.5,
              at=(ROLL[0] + du, HORN_WALL_Y[0] - 0.4, ROLL[1] + dv), axis="y", op="cut")
    # connectors
    p.connector("yaw_servo_case", at=(-7.5, 0.0, Z_PLATE0), dir=(0.0, 0.0, -1.0))
    p.connector("roll_horn", at=(ROLL[0], HORN_BOSS_Y[1], ROLL[1]), dir=(0.0, 1.0, 0.0))
    p.connector("roll_bearing_seat", at=(ROLL[0], ROLL_BOSS_Y[0], ROLL[1]), dir=(0.0, -1.0, 0.0))
    return p
