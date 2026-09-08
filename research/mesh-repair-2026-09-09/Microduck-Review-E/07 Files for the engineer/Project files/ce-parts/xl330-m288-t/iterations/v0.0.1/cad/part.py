"""part:xl330-m288-t — ROBOTIS DYNAMIXEL XL330-M288-T, the Microduck's servo.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. Imports only
cecad + stdlib.

WHAT THE VENDOR SAYS (docs/fetched/robotis-emanual-xl330-m288.html, ROBOTIS
e-Manual, fetched 2026-09-01): "Dimensions (W x H x D) 20.0 x 34.0 x 26.0
[mm]", "Weight 18 [g]", "Gear Ratio 288.4 : 1", "Stall Torque 0.52 [N.m]
(at 5.0 [V], 1.47 [A])", "Input Voltage 3.7 ~ 6.0 [V]".

WHAT THE MESH SAYS. Every geometric number below was READ OFF Pollen's
published mesh `reference/pollen-microduck-rl/assets/xl330.stl` (metres,
4126 triangles) on 2026-09-01 with `cad-mjcf sections`,
`cecad.meshfeatures.cylinders` and 0.1 mm plane cuts, and the rebuild is
graded against that mesh by `cecad.meshcompare` (evidence/refcheck/). The
mesh is the servo WITH a Ø16 x 3 disc on BOTH faces (horn side and idler
side): 29.0 x 20.0 x 34.0 overall, body 23.0 deep — the vendor's 26.0 is
the body plus one 3 mm horn, so the two agree once the idler disc is
counted. The horn axis is 9.5 mm below the top of the body (vendor drawing
not machine-readable here; measured off the mesh).

FRAME — Pollen's mesh frame, kept so the MJCF geom pos/quat place it with
no re-derivation: the HORN AXIS IS THE X AXIS through the origin, +x is the
horn side, y is the 20 mm width, z is the 34 mm height with the top at
z = 9.5 and the bottom at z = -24.5.
"""

# ---- body, measured (mm) ----------------------------------------------------
BODY_X = (-11.5, 11.5)       # z-sections: x range [-11.5, 11.5] over the whole height (23.0 deep)
BODY_Y = (-10.0, 10.0)       # y range [-10, 10] (20.0 wide)
BODY_Z = (-24.5, 9.5)        # numpy bbox z min -24.5, max 9.5 (34.0 tall); horn axis at z = 0
# ---- the two Ø16 discs (horn and idler) -------------------------------------
DISC_D, DISC_L = 16.0, 3.0   # meshfeatures bosses: Ø16.0, axis x, centre x = ±13.0, length 3.0
# ---- the two pockets flanking the rib below the horn, +x side only ----------
POCKET_X0 = 2.2              # y = -8 cut at 0.1 mm: material to x 2.15, empty from 2.25
POCKET_Y = (6.0, 10.0)       # x = 11.45 cut at 0.1 mm: material to y 5.95, empty from 6.05, to the face
POCKET_Z = (-14.3, -3.7)     # same cuts: empty rows z -14.25 .. -3.75, filled at -14.35 and -3.65
# ---- drill ------------------------------------------------------------------
THRU_D = 2.0                 # meshfeatures: 4 x Ø2.0 along x, length 23 (through the body)
THRU_Y = (-8.0, 8.0)         #   at y = ±8
THRU_Z = (7.5, -22.5)        #   at z = 7.5 and -22.5, i.e. body-centre z = -7.5 ± 15
FACE_D, FACE_DEPTH = 1.6, 6.0   # meshfeatures: 8 x Ø1.6 along x, length 6, centre x = ±11.5
FACE_PCD = 12.0              #   at (y, z) = (0, ±6), (±6, 0) on both faces — M2 tap-drill size
FACE_AT = ((0.0, 6.0), (0.0, -6.0), (6.0, 0.0), (-6.0, 0.0))

MATERIAL = "PA"   # the vendor's case material is not stated on the fetched page — see README


def build(doc, params=None):
    from cecad.core import Part
    if params:
        raise ValueError("xl330-m288-t takes no build parameters (got %s)" % sorted(params))
    p = Part("xl330-m288-t", material=MATERIAL)
    p.box(BODY_X[1] - BODY_X[0], BODY_Y[1] - BODY_Y[0], BODY_Z[1] - BODY_Z[0],
          at=(BODY_X[0], BODY_Y[0], BODY_Z[0]))
    # the two pockets: from x = POCKET_X0 out through the +x face, |y| 6..10, z -14.3..-3.7
    for y0, y1 in (POCKET_Y, (-POCKET_Y[1], -POCKET_Y[0])):
        p.box(BODY_X[1] - POCKET_X0 + 1, y1 - y0 + (0.01 if y1 < BODY_Y[1] else 1),
              POCKET_Z[1] - POCKET_Z[0], at=(POCKET_X0, y0 if y0 > BODY_Y[0] else y0 - 1, POCKET_Z[0]), op="cut")
    # horn disc (+x) and idler disc (-x)
    p.cyl(DISC_D, DISC_L + 0.01, at=(BODY_X[1] - 0.01, 0, 0), axis="x")
    p.cyl(DISC_D, DISC_L + 0.01, at=(BODY_X[0] - DISC_L, 0, 0), axis="x")
    # 4 x Ø2 through along x
    for y in THRU_Y:
        for z in THRU_Z:
            p.cyl(THRU_D, 40, at=(-20, y, z), axis="x", op="cut")
    # 8 x Ø1.6 x 6 deep from each disc face
    for y, z in FACE_AT:
        p.cyl(FACE_D, FACE_DEPTH + 0.01, at=(BODY_X[1] + DISC_L - FACE_DEPTH, y, z), axis="x", op="cut")
        p.cyl(FACE_D, FACE_DEPTH + 0.01, at=(BODY_X[0] - DISC_L - 0.01, y, z), axis="x", op="cut")
    p.clean()
    p.connector("horn", at=(BODY_X[1] + DISC_L, 0, 0), dir="+x")
    p.connector("idler", at=(BODY_X[0] - DISC_L, 0, 0), dir="-x")
    p.connector("side_pos_y", at=(0, BODY_Y[1], -7.5), dir="+y")
    p.connector("side_neg_y", at=(0, BODY_Y[0], -7.5), dir="-y")
    return p
