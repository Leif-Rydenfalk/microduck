"""part:microduck-upper-leg-left — the left thigh housing, rebuilt.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. Parametric —
nobody has Pollen's CAD. Every number below was READ OFF Pollen's published
mesh `reference/pollen-microduck-rl/assets/upper_leg_left.stl` (metres,
decimated) on 2026-09-01 with `cecad.meshslice` (plane cuts drawn as slice
sheets in out/measure/thigh_slices_{x,y,z}.png, and ray-cast material
intervals — the probe letter/row is quoted beside each number) and
`cecad.meshfeatures.cylinders`. The rebuild is graded against that mesh by
`ce-cad/bin/cad-refcheck` (see evidence/).

FRAME — Pollen's mesh frame, kept on purpose: X is the DEPTH of the cup
(open side x = 42.5 where the rigidity plate sits, closed back plate
x 69.5..70.5), Y the width (-13.47 .. 34.19), Z the length (-12.2 .. 48.8).
The MJCF geom pos (0,0,-42.5) quat (0.5,-0.5,-0.5,-0.5) maps mesh (x,y,z)
to body (y, z, x-42.5): both servo axes run along mesh X.

WHAT IT IS. A one-sided cup that holds the hip-pitch and knee XL330s side
by side, horns toward the open side. Two axes in this frame:
  A0 = (y 0, z 0)         hip pitch  (the body origin)
  A1 = (y 22, z 35.777)   knee       — 42.000 mm apart (SPEC.md §3)
Structure, all measured:
  * back plate 1.0 thick (x 69.5..70.5), outline = hull of two R12.2
    circles about A0/A1, closed on -y by the side wall and on +z by the
    top flange; the whole outer edge is a quarter-round R4.0 (probe C/I:
    at x 68.5/69.5/70.45 the edge sits 0.54/1.35/3.37 in from the outline
    — R4 gives 0.54/1.35/3.37).
  * a 1.0 rim wall inside that edge, x 66.5..69.5 (probe C: rim bottom
    between x 66.5 and 66.8; wall 1.00–1.04 thick at x 66.8..67.5).
  * ONE side wall, 1.0 thick, on the -y side, running the full depth,
    drafted 3.0 deg about z (probe D: outer face y -13.462 at x 42.6 ->
    -12.21 at x 66.5 = 0.0524/mm = tan 3 deg); it bends over (a cone:
    centre (y 0, z 35.07) at every x, radius = the drafted wall distance,
    13.5 at x 43 / 12.5 at x 60 — probe G) into a top flange, also 1.0,
    drafted 3.0 deg in x AND tilted 1.86 deg in y (probe L: z rises
    0.0324/mm of +y at x 43 and x 64 alike).
  * the wall's bottom edge and the flange's +y edge are S-curves, carried
    below as measured polylines (probes F/K and J).
  * at each axis, on the plate's inner face: a Ø7.27 boss x 67..69.5, a
    Ø4.42 boss x 64.7..67, a Ø5.37 counterbore 2.5 deep from the outside
    (x 68..70.5) and a Ø2.4->2.8 through hole (probe A, meshfeatures).
  * four "+" bosses (hub Ø1.9, arms 0.8 wide, 2.9 long, x 66.5..69.5) each
    with a Ø1.6 pin to x 64.5, at the four (y,z) positions where the
    rigidity plate has its Ø2.2 holes (probes B/H/M).
"""
import math

# ---- frame / envelope (bbox of upper_leg_left.stl, mm) ----------------------
X_OPEN, X_BACK = 42.5, 70.5           # bbox x; open face and back face
X_PLATE_IN = 69.5                     # plate inner face (probe A: r>=3.7 -> 69.5..70.5)
X_RIM = 66.5                          # rim bottom (probe C: no rim at 66.5, rim at 66.8)
T_WALL = 1.0                          # every wall: plate, rim, side, flange (probes A,C,D,L)
R_EDGE = 4.0                          # quarter-round on the whole outer edge (probe C/I fit)

# ---- the two axes ------------------------------------------------------------
A0 = (0.0, 0.0)                       # hip pitch (meshfeatures hole Ø5.371 at y 0, z 0)
A1 = (22.0, 35.777)                   # knee (meshfeatures hole Ø5.371 at y 22, z 35.777)
R_OUT = 12.2                          # outline circle about each axis (bbox z -12.197, y 34.19)

# ---- side wall + top flange (one bent, drafted sheet) ------------------------
DRAFT = math.tan(math.radians(3.0))   # 0.05241/mm (probe D/E: 1.252 mm over 23.9 mm)
Y_WALL0 = -13.467                     # wall outer face at x 42.5 (bbox y min)
Z_TOP0 = 48.539                       # flange top at x 42.5, y 0 (probe C: 48.534 at x 42.6)
TILT_Y = 0.0324                       # flange top rises this per mm of +y (probe L)
BEND_C = (0.0, 35.07)                 # bend centre (y, z), fixed over x (probe G fits)
# flange +y edge: (x, y_end) measured with z-rays at 0.25 mm y steps (probe J)
FLANGE_EDGE = [(42.4, 4.9), (42.55, 6.0), (43, 8.25), (44, 10.25), (45, 11.75), (46, 12.75),
               (47, 13.5), (48, 14.0), (49, 14.5), (50, 14.75), (51, 15.25), (52, 15.5),
               (53, 16.0), (54, 16.25), (55, 16.5), (56, 17.0), (58, 17.75), (60, 18.5),
               (62, 19.5), (64, 21.0), (65, 22.25), (66, 24.25), (66.4, 25.5), (66.7, 26.6)]
# side wall bottom edge: (x, z_bot) measured with z-rays along the wall (probes F/K)
WALL_BOTTOM = [(42.4, 16.5), (42.51, 14.97), (42.55, 14.43), (43, 12.30), (43.5, 11.06),
               (44, 10.15), (44.5, 9.42), (45, 8.80), (45.5, 8.28), (46, 7.82), (47, 7.07),
               (48, 6.49), (50, 5.68), (52, 4.95), (55, 3.86), (58, 2.77), (60, 2.04),
               (62, 1.28), (63, 0.74), (63.5, 0.39), (64, -0.01), (64.5, -0.49), (65, -1.08),
               (65.5, -1.79), (66, -2.74), (66.25, -3.36), (66.6, -3.6)]

# ---- axis bosses (probe A, identical at A0 and A1) ---------------------------
BOSS_BIG_D, X_BOSS_BIG = 7.27, 67.0         # Ø7.268 (meshfeatures), x 67.0 .. plate
BOSS_SMALL_D, X_BOSS_SMALL = 4.42, 64.7     # Ø4.417 (meshfeatures), x 64.7 .. 67.0
CBORE_D, X_CBORE = 5.37, 68.0               # Ø5.371 from the back face down to x 68.0
HOLE_D_TIP, HOLE_D_FLOOR = 2.4, 2.8         # r 1.2 partial / r 1.3 to 67.6 / r 1.4 to 68.0

# ---- "+" pin bosses (probes B, H, M) -----------------------------------------
X_PIN_TIP, X_HUB = 64.5, 66.5               # pin 64.5..66.5, hub/arms 66.5..69.5
PIN_D_TIP, PIN_D_ROOT = 1.6, 1.8            # r 0.8 -> 64.59, r 0.85 -> 65.55, r 0.9 -> 66.5
HUB_D = 1.9                                 # diag (0.64,0.64) inside, (0.71,0.71) outside
ARM_W, ARM_L = 0.8, 2.9                     # half-width 0.35..0.4 (M), end 2.9..2.95 (M)
# centre (y, z) and which arms exist (+y, -y, +z, -z) — probe H
CROSSES = [((-0.5, 43.777), (True, True, True, True)),    # +z arm runs into the flange
           ((-0.5, 27.777), (True, True, True, True)),
           ((-8.0, 22.5), (False, True, True, True)),
           ((8.0, 22.5), (True, False, True, True))]

MATERIAL = "PLA"


# ---- geometry helpers --------------------------------------------------------
def _y_wall(x):
    return Y_WALL0 + (x - X_OPEN) * DRAFT


def _z_top(x, y=0.0):
    return Z_TOP0 - (x - X_OPEN) * DRAFT + TILT_Y * y


def _arc(c, r, a0, a1, n):
    return [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def _outline(x, d, n_arc=28, n_bend=16):
    """The back-plate outline at depth x, inset by d (mm) — d = 0 is the
    outer skin, d = 1 the rim's inner face, d = 4 the flat back face.
    Same vertex count for every (x, d) so the sections can be lofted."""
    r = R_OUT - d
    yw = _y_wall(x) + d
    phi = math.degrees(math.atan2(A1[1] - A0[1], A1[0] - A0[0]))   # A0 -> A1 direction
    t_tan = phi - 90.0                                              # right-hand tangent
    pts = []
    # circle A0: from the wall tangent (180) down and round to the tangent line
    pts += _arc(A0, r, 180.0, 360.0 + t_tan, n_arc)
    # circle A1: from the tangent line up to where the (tilted) top line cuts it
    t = 60.0
    for _ in range(40):                                             # solve z(t) = z_top(y(t))
        y = A1[0] + r * math.cos(math.radians(t))
        z = A1[1] + r * math.sin(math.radians(t))
        f = z - (_z_top(x, y) - d)
        df = r * math.cos(math.radians(t)) * (math.pi / 180.0) + TILT_Y * r * math.sin(math.radians(t)) * (math.pi / 180.0)
        t -= f / df
    pts += _arc(A1, r, t_tan, t, n_arc)
    # top line from that point back to the bend, then the bend, then the wall
    rb = (BEND_C[0] - yw)
    pts.append((BEND_C[0], _z_top(x, BEND_C[0]) - d))
    pts += _arc(BEND_C, rb, 90.0, 180.0, n_bend)[1:]
    pts.append((yw, A0[1]))
    return pts


def _l_profile(x, y_far=34.0, z_low=-8.0, n_bend=24):
    """Closed (y, z) profile of the bent side-wall/top-flange sheet at depth
    x: outer skin, then the inner skin T_WALL inside. Over-long on both
    legs; the measured edge curves trim it afterwards."""
    yw = _y_wall(x)
    rb = BEND_C[0] - yw
    out = [(yw, z_low), (yw, BEND_C[1])]
    out += _arc(BEND_C, rb, 180.0, 90.0, n_bend)[1:]
    out += [(y_far, _z_top(x, y_far))]
    inn = [(y_far, _z_top(x, y_far) - T_WALL), (BEND_C[0], _z_top(x) - T_WALL)]
    inn += _arc(BEND_C, rb - T_WALL, 90.0, 180.0, n_bend)[1:]
    inn += [(yw + T_WALL, z_low)]
    return out + inn


def build(doc, params=None):
    from cecad.core import Part
    if params:
        raise ValueError("microduck-upper-leg-left takes no build parameters (got %s)" % sorted(params))
    p = Part("microduck-upper-leg-left", material=MATERIAL)

    # 1. back plate + rim slab, x 66.5..70.5, with the R4 quarter-round edge
    #    as a loft through insets d(x) = R - sqrt(R^2 - (x - X_RIM)^2)
    secs = []
    for k in range(0, 10):
        th = math.radians(90.0 * k / 9)
        x = X_RIM + R_EDGE * math.sin(th)
        d = R_EDGE - R_EDGE * math.cos(th)
        secs.append((_outline(x, d), x))
    p.loft(secs, axis="x", smooth=False, ruled=False)
    # 2. hollow it: the cup interior between the rim's inner face and the plate
    p.loft([(_outline(X_RIM - 0.2, T_WALL), X_RIM - 0.2), (_outline(X_PLATE_IN, T_WALL), X_PLATE_IN)],
           axis="x", smooth=False, ruled=True, op="cut")
    # 3. the bent side wall + top flange sheet, open face to the rim
    p.loft([(_l_profile(X_OPEN), X_OPEN), (_l_profile(X_RIM + 0.1), X_RIM + 0.1)],
           axis="x", smooth=False, ruled=True)
    # 4. trim the wall's bottom edge (prism along y takes (z, x) points)
    cut = [(z, x) for x, z in WALL_BOTTOM] + [(-14.0, WALL_BOTTOM[-1][0]), (-14.0, WALL_BOTTOM[0][0])]
    p.prism(cut, 5.0, at=(0, -15.5, 0), axis="y", op="cut")
    # 5. trim the flange's +y edge (prism along z takes (x, y) points)
    cut = [(x, y) for x, y in FLANGE_EDGE] + [(FLANGE_EDGE[-1][0], 40.0), (FLANGE_EDGE[0][0], 40.0)]
    p.prism(cut, 8.0, at=(0, 0, 44.0), axis="z", op="cut")
    # 6. axis bosses, counterbores, through holes
    for (y, z) in (A0, A1):
        p.cyl(BOSS_BIG_D, X_PLATE_IN - X_BOSS_BIG + 0.3, at=(X_BOSS_BIG, y, z), axis="x")
        p.cyl(BOSS_SMALL_D, X_BOSS_BIG - X_BOSS_SMALL + 0.2, at=(X_BOSS_SMALL, y, z), axis="x")
    for (y, z) in (A0, A1):
        p.cyl(CBORE_D, X_BACK - X_CBORE + 1.0, at=(X_CBORE, y, z), axis="x", op="cut")
        p.cone(HOLE_D_TIP, HOLE_D_FLOOR, X_CBORE - X_BOSS_SMALL + 1.0,
               at=(X_BOSS_SMALL - 0.5, y, z), axis="x", op="cut")
    # 7. the four "+" bosses with their locating pins
    h = X_PLATE_IN - X_HUB + 0.3
    for (cy, cz), (py, my, pz, mz) in CROSSES:
        p.cyl(HUB_D, h, at=(X_HUB, cy, cz), axis="x")
        p.cone(PIN_D_TIP, PIN_D_ROOT, X_HUB - X_PIN_TIP + 0.05, at=(X_PIN_TIP, cy, cz), axis="x")
        if py:
            p.box(h, ARM_L, ARM_W, at=(X_HUB, cy, cz - ARM_W / 2))
        if my:
            p.box(h, ARM_L, ARM_W, at=(X_HUB, cy - ARM_L, cz - ARM_W / 2))
        if pz:
            p.box(h, ARM_W, ARM_L, at=(X_HUB, cy - ARM_W / 2, cz))
        if mz:
            p.box(h, ARM_W, ARM_L, at=(X_HUB, cy - ARM_W / 2, cz - ARM_L))
    p.clean()
    # interfaces: the two axes seen from the outside face, the servo seats
    # inside, the four pins
    p.connector("hip_pitch_axle", at=(X_BACK, A0[0], A0[1]), dir="+x")
    p.connector("knee_axle", at=(X_BACK, A1[0], A1[1]), dir="+x")
    p.connector("hip_pitch_servo_seat", at=(X_BOSS_SMALL, A0[0], A0[1]), dir="-x")
    p.connector("knee_servo_seat", at=(X_BOSS_SMALL, A1[0], A1[1]), dir="-x")
    for i, ((cy, cz), _) in enumerate(CROSSES):
        p.connector("pin_%d" % (i + 1), at=(X_PIN_TIP, cy, cz), dir="-x")
    return p
