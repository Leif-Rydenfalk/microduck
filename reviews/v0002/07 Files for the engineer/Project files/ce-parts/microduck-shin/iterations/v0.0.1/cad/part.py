"""part:microduck-shin — the shin plate ("leg" in Pollen's MJCF), rebuilt.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. Parametric —
there is no geometry/*.step because nobody has Pollen's CAD. Every number
below was READ OFF Pollen's published mesh
`reference/pollen-microduck-rl/assets/leg.stl` (metres, decimated) with
`ce-cad/bin/cad-mjcf sections` and `cecad.meshfeatures.cylinders` on
2026-09-01, and the rebuild is graded against that mesh by
`cecad.meshcompare` (see evidence/).

FRAME — Pollen's mesh frame, kept on purpose: X is the plate's THICKNESS
(back face x = 33.2, front face 38.5, raised pad to 40.45), Y its WIDTH
(12 .. 32), Z its LENGTH (-12.2 .. 45.8). Keeping their frame means the
MJCF's own geom pos/quat place this part in the assembly with no
re-derivation, and meshcompare needs no alignment.

WHAT IT IS. One of the two parallel plates of each shin (the MJCF places
`leg` twice per side). The knee end (top, z = 35.777) carries a Ø15.9 disc
(the XL330 horn face) with the horn's 4 x M2 on an 8.49 mm square;
the ankle end (bottom, z = -6.223) carries a Ø10 x 3 boss that the 15x10x3
bearing sits on. The two axes are 42.000 mm apart — the shin length in
SPEC.md §3.
"""
import math

# ---- measured off leg.stl (mm) ---------------------------------------------
# x-sections (cad-mjcf sections --axis x): at x 33.5 / 34.5 the material is
# only y 16.3..27.7 (a central RIB, full length); at x 36.0 it is the full
# 20 mm width. So the plate is 2.8 thick with an 11.4 wide rib behind it.
X_BACK_RIB, X_BACK_PLATE, X_FRONT = 33.2, 35.7, 38.0
X_FRONT_TOP, Z_TOP_STEP = 38.5, 26.5      # the top region (disc end) is 0.5 thicker
X_PAD = 40.45                         # rim + horn disc front face
W = 20.0                              # plate width, y 12 .. 32
Y0 = 12.0
YC = Y0 + W / 2                       # 22.0, the centreline
RIB_W = 12.4                          # y 15.8 .. 28.2 (x=34.5 sections)
Z_KNEE = 35.777                       # knee axis (XL330 horn face)
Z_ANKLE = -6.223                      # ankle axis (bearing seat)
R_TOP = 10.0                          # top end: semicircle, z max 45.777
R_BOTTOM = 6.0                        # bottom end round, z min -12.223
W_BOTTOM_AT_AXIS = 12.5               # taper width measured at the ankle axis
Z_TAPER_START = 8.0                   # where the full width starts to taper
RIB_Z0, RIB_Z1 = 5.0, 41.5            # rib extent along z (x=34.5: 9 wide at z 6, full at z 10, rounded off by 43)
X_FRONT_LOW = 38.0

# knee end: a raised RIM (rounded rect, wall RIM_W) and a Ø15.9 DISC inside
# it, both up to X_PAD; the pocket floor between them is X_FRONT
HORN_DISC_D = 15.9
HORN_BORE_D = 6.0
HORN_SCREW_D, HORN_SCREW_SQUARE = 2.2, 8.486     # 4 x M2 clearance on a square
HORN_CBORE_D, HORN_CBORE_DEPTH = 4.4, 4.5        # from the back face
# rim walls, 1 mm thick, read off x-plane sections at 38.3 / 39.0 / 40.3:
#   outer walls y 13.5-14.5 and 29.5-30.5: z 9..23, to x 38.5, and to X_PAD over z 17.5..23
#   inner walls y 17.5-18.5 and 25.5-26.5: z 17.5..23, to X_PAD
WALL_T = 1.0
OUTER_WALL_Y = (13.5, 29.5)
INNER_WALL_Y = (17.5, 25.5)
WALL_Z0, WALL_Z_HI, WALL_Z1 = 9.0, 17.5, 23.0

# mid features
SLOT_W, SLOT_Z0, SLOT_Z1, SLOT_R = 5.0, 15.0, 26.5, 1.5   # y 19.5 .. 24.5
SIDE_HOLE_D, SIDE_HOLE_Z, SIDE_HOLE_Y = 2.4, 16.277, (14.0, 30.0)
SIDE_CBORE_D, SIDE_CBORE_TO_X = 4.84, 36.2   # from the very back, into rib flank and plate

# ankle end features
BEARING_BOSS_D = 10.0                            # on the BACK, x 32.5 .. plate
X_BOSS_BACK = 32.5
ANKLE_PIN_D, ANKLE_PIN_LEN = 4.92, 2.3           # on the FRONT, from X_FRONT
ANKLE_RING_D = 10.0                              # Ø10 ring standing 0.5 above the low front face
ANKLE_RECESS_D, ANKLE_RECESS_DEPTH = 8.0, 0.5    # inside the ring, down to the low face
ANKLE_HOLE_D, ANKLE_CBORE_D, ANKLE_CBORE_DEPTH = 2.7, 5.5, 3.5

MATERIAL = "PLA"


def _outline():
    """(y, z) polygon of the plate seen from +x: full width from the taper
    start up to the top semicircle, tapering to the R_BOTTOM round at the
    ankle axis."""
    pts = []
    n = 24
    # top semicircle, centred (YC, Z_KNEE), from +y round to -y
    for i in range(n + 1):
        a = math.pi * i / n
        pts.append((YC + R_TOP * math.cos(a), Z_KNEE + R_TOP * math.sin(a)))
    # left side down to the taper start
    pts.append((Y0, Z_TAPER_START))
    # taper to the bottom round: tangent-ish straight to the half width at the axis
    hw = W_BOTTOM_AT_AXIS / 2
    pts.append((YC - hw, Z_ANKLE))
    # bottom round
    for i in range(n + 1):
        a = math.pi + math.pi * i / n
        pts.append((YC + R_BOTTOM * math.cos(a), Z_ANKLE + R_BOTTOM * math.sin(a)))
    pts.append((YC + hw, Z_ANKLE))
    pts.append((Y0 + W, Z_TAPER_START))
    return pts


def _rounded_rect(y0, y1, z0, z1, r, n=8):
    pts = []
    corners = [((y1 - r, z1 - r), 0), ((y0 + r, z1 - r), 90), ((y0 + r, z0 + r), 180), ((y1 - r, z0 + r), 270)]
    for (cy, cz), a0 in corners:
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cy + r * math.cos(a), cz + r * math.sin(a)))
    return pts


def build(doc, params=None):
    from cecad.core import Part
    if params:
        raise ValueError("microduck-shin takes no build parameters (got %s)" % sorted(params))
    p = Part("microduck-shin", material=MATERIAL)
    # base plate, 2.3 thick, full outline; 0.5 thicker over the top (disc) region
    p.prism(_outline(), X_FRONT - X_BACK_PLATE, at=(X_BACK_PLATE, 0, 0), axis="x")
    p.prism(_outline(), X_FRONT_TOP - X_FRONT + 0.01, at=(X_FRONT - 0.01, 0, 0), axis="x")
    p.box(X_FRONT_TOP - X_FRONT + 1, W + 2, Z_TOP_STEP - (Z_ANKLE - R_BOTTOM) + 1,
          at=(X_FRONT, Y0 - 1, Z_ANKLE - R_BOTTOM - 1), op="cut")
    # central rib behind it, rounded top
    p.prism(_rounded_rect(YC - RIB_W / 2, YC + RIB_W / 2, RIB_Z0, RIB_Z1, RIB_W / 2 - 0.01),
            X_BACK_PLATE - X_BACK_RIB + 0.01, at=(X_BACK_RIB, 0, 0), axis="x")
    # rim walls on the front
    for y in OUTER_WALL_Y:
        p.box(X_FRONT_TOP - X_FRONT + 0.01, WALL_T, WALL_Z1 - WALL_Z0, at=(X_FRONT - 0.01, y, WALL_Z0))
        p.box(X_PAD - X_FRONT + 0.01, WALL_T, WALL_Z1 - WALL_Z_HI, at=(X_FRONT - 0.01, y, WALL_Z_HI))
    for y in INNER_WALL_Y:
        p.box(X_PAD - X_FRONT + 0.01, WALL_T, WALL_Z1 - WALL_Z_HI, at=(X_FRONT - 0.01, y, WALL_Z_HI))
    # horn disc Ø15.9 standing on the thick top region, up to the pad face
    p.cyl(HORN_DISC_D, X_PAD - X_FRONT_TOP + 0.01, at=(X_FRONT_TOP - 0.01, YC, Z_KNEE), axis="x")
    p.cyl(HORN_BORE_D, 20, at=(X_BACK_RIB - 1, YC, Z_KNEE), axis="x", op="cut")
    # 4 x M2 horn screws on the 8.486 square, counterbored from the back
    h = HORN_SCREW_SQUARE / 2
    for dy in (-h, h):
        for dz in (-h, h):
            p.cyl(HORN_SCREW_D, 20, at=(X_BACK_RIB - 1, YC + dy, Z_KNEE + dz), axis="x", op="cut")
            p.cyl(HORN_CBORE_D, HORN_CBORE_DEPTH, at=(X_BACK_RIB - 0.01, YC + dy, Z_KNEE + dz), axis="x", op="cut")
    # the central slot
    p.prism(_rounded_rect(YC - SLOT_W / 2, YC + SLOT_W / 2, SLOT_Z0, SLOT_Z1, SLOT_R), 20,
            at=(X_BACK_RIB - 1, 0, 0), axis="x", op="cut")
    # two side holes, counterbored from the very back into the rib flank and plate
    for y in SIDE_HOLE_Y:
        p.cyl(SIDE_HOLE_D, 20, at=(X_BACK_RIB - 1, y, SIDE_HOLE_Z), axis="x", op="cut")
        p.cyl(SIDE_CBORE_D, SIDE_CBORE_TO_X - X_BACK_RIB + 1, at=(X_BACK_RIB - 1, y, SIDE_HOLE_Z), axis="x", op="cut")
    # ankle end: Ø10 ring 0.5 proud with a Ø8 recess, pin boss, bearing boss on the back, through hole + c'bore
    p.cyl(ANKLE_RING_D, X_FRONT_TOP - X_FRONT_LOW + 0.01, at=(X_FRONT_LOW - 0.01, YC, Z_ANKLE), axis="x")
    p.cyl(ANKLE_RECESS_D, X_FRONT_TOP - X_FRONT_LOW + 0.02, at=(X_FRONT_LOW, YC, Z_ANKLE), axis="x", op="cut")
    p.cyl(BEARING_BOSS_D, X_BACK_PLATE - X_BOSS_BACK + 0.01, at=(X_BOSS_BACK, YC, Z_ANKLE), axis="x")
    p.cyl(ANKLE_PIN_D, ANKLE_PIN_LEN, at=(X_FRONT_LOW - 0.01, YC, Z_ANKLE), axis="x")
    p.cyl(ANKLE_HOLE_D, 30, at=(X_BOSS_BACK - 1, YC, Z_ANKLE), axis="x", op="cut")
    p.cyl(ANKLE_CBORE_D, ANKLE_CBORE_DEPTH, at=(X_BOSS_BACK - 0.01, YC, Z_ANKLE), axis="x", op="cut")
    p.clean()
    # interfaces: the two axes, as connectors along +x
    p.connector("knee", at=(X_PAD, YC, Z_KNEE), dir="+x")
    p.connector("ankle", at=(X_BOSS_BACK, YC, Z_ANKLE), dir="+x")
    return p
