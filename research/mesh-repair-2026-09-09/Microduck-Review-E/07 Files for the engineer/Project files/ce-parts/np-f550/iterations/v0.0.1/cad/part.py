"""part:np-f550 — Sony-style NP-F550 2S Li-ion camera battery, the Microduck's pack.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. Imports only
cecad + stdlib. A BOUGHT part (see sourcing.json / docs/); the geometry is a
faithful envelope of Pollen's published mesh
`reference/pollen-microduck-rl/assets/np_f970.stl` — NAMED np_f970 but it
MEASURES an NP-F550: 38.5 x 20.5 x 70.7 mm (an F970 is ~38 x 60 x 70) —
measured 2026-09-02 with `cecad.meshslice.intervals` (probe lines quoted
below), `cecad.meshfeatures.cylinders` and slice renders (out/measure/
npf550_slices_*.png), and graded against that mesh by `cad-refcheck`.
NOTE: the mesh has internal/degenerate faces (probe parity flips between
scan directions in the bottom-rail region); the x-scan family, which was
self-consistent across y in 0.3 mm steps, is the one modelled.

FRAME — Pollen's mesh frame: z is the 70.7 mm length (terminal end at
z = -35.35), y is the 20.5 mm height (+y is the grooved top), x the
38.5 mm width. Cross-section bbox x -19.25..19.25, y -10.25..10.25.

MEASURED SHAPE:
  * body slab x +-19.25, y -7.25..2.25 (x-intervals: full width for y -7.2..2.25)
  * top: R8.0 corner arcs centred (+-11.25, 2.25) — circle fit through
    (17.14,7.65),(15.53,9),(13.22,10),(12.1,10.2), residual < 0.02 mm —
    tangent to the side walls and to the flat top y = 10.25 (|x| <= 11.25)
  * top groove: drafted slot, floor y 7.6 half-width 1.665, mouth y 10.25
    half-width 2.75 (notch wall through (1.67,7.65) and (2.73,10.2));
    runs from the terminal end to z = 20.0 (z-intervals at (0, 9):
    material 19.93..35.35), filled beyond
  * bottom rails y -10.25..-7.25: left x -17.2..-2.25, right x 2.25..17.15
    (x-intervals at y -10.2..-7.5: (-17.2,-2.25),(2.25,17.15))
  * rail ends set back to z -33.55 for |x| 13..17.2 (z-intervals at
    y=-9.5: x +-13..17 start -33.55, x +-5..11 reach -35.35)
  * rail inner-edge latch notches (z-intervals at y=-9.5):
      left  x -4.0..-2.25: open z < -6.35            (x=-3: material -6.35..35.35)
      right x  2.25..4.0 : open z < -27.85 and -14.65..-6.35
                                                     (x=3: (-27.85,-14.65),(-6.35,35.35))
  * centre feet x -2.25..2.25, y to -10.25, at z (-22.95,-14.65),
    (-6.35,-3.2), (6.7,14.95), (22.5,25.35)          (z-intervals at x 0/1.5, y -9.5)
  * 2 x D2.4 terminal-end holes, axis z, centres (+-16.9, -7.75),
    z -33.05..-27.55 (meshfeatures: d 2.4, len 5.5, centre z -30.3)
"""

# ---- measured (mm) ----------------------------------------------------------
X_HALF = 19.25            # width 38.5
Y_BOT_SLAB = -7.25        # slab underside
Y_SIDE_TOP = 2.25         # top of the flat side wall = arc centre height
Y_TOP = 10.25             # flat top
Z_HALF = 35.35            # length 70.7
ARC_R, ARC_CX = 8.0, 11.25   # top corner arcs, centres (+-11.25, 2.25)
GROOVE_FLOOR, GROOVE_HW_FLOOR, GROOVE_HW_TOP = 7.6, 1.665, 2.75
GROOVE_Z_END = 20.0       # groove stops here (filled toward +z)
RAIL_Y = -10.25           # rail underside
RAIL_L = (-17.2, -2.25)   # left rail x span
RAIL_R = (2.25, 17.15)    # right rail x span
RAIL_END_Z = -33.55       # outer rail set-back at the terminal end
RAIL_END_X = 13.0         # ...for |x| >= 13
NOTCH_W = 4.0             # latch notches reach in to |x| = 4.0
FOOT_Z = ((-22.95, -14.65), (-6.35, -3.2), (6.7, 14.95), (22.5, 25.35))
HOLE_D, HOLE_X, HOLE_Y = 2.4, 16.9, -7.75
HOLE_Z = (-33.6, -27.55)  # cut span (measured -33.05..-27.55, opened to the rail end face)
# 2 shallow Ø3.2 dimples in the bottom-rail undersides (meshfeatures: d 3.198,
#   axis +y, centres (+-14.65, y -10.201, z -30.75), len ~0.12 mm)
DIMPLE_D, DIMPLE_X, DIMPLE_Z = 3.2, 14.65, -30.75
DIMPLE_Y0, DIMPLE_DEPTH = RAIL_Y - 0.05, 0.20      # cut +y from just below the rail face
# 2 shallow Ø3.48 counterbores on the terminal-end face, coaxial with the D2.4
#   holes (meshfeatures: d 3.476, axis z, centres (+-16.9, -7.75, z ~-33.5), len 0.1..0.23)
END_CB_D = 3.48
END_CB_Z = (-33.7, -33.35)  # shallow ring on the rail end face (z -33.55) around each terminal hole

MATERIAL = "ABS"          # moulded pack shell, assumed — see docs/README.md


def build(doc, params=None):
    from cecad.core import Part
    if params:
        raise ValueError("np-f550 takes no build parameters (got %s)" % sorted(params))
    p = Part("np-f550", material=MATERIAL)
    L = 2 * Z_HALF
    # body slab + flat-top block + R8 corner cylinders = the measured cross-section
    p.box(2 * X_HALF, Y_SIDE_TOP - Y_BOT_SLAB, L, at=(-X_HALF, Y_BOT_SLAB, -Z_HALF))
    p.box(2 * ARC_CX, Y_TOP - Y_SIDE_TOP, L, at=(-ARC_CX, Y_SIDE_TOP, -Z_HALF))
    for sx in (-1, 1):
        p.cyl(2 * ARC_R, L, at=(sx * ARC_CX, Y_SIDE_TOP, -Z_HALF), axis="z")
    # top groove: drafted slot cut from the terminal end to GROOVE_Z_END
    p.prism([(-GROOVE_HW_TOP, Y_TOP + 0.1), (-GROOVE_HW_FLOOR, GROOVE_FLOOR),
             (GROOVE_HW_FLOOR, GROOVE_FLOOR), (GROOVE_HW_TOP, Y_TOP + 0.1)],
            GROOVE_Z_END - (-Z_HALF - 0.1), at=(0, 0, -Z_HALF - 0.1), axis="z", op="cut")
    # bottom rails
    p.box(RAIL_L[1] - RAIL_L[0], Y_BOT_SLAB - RAIL_Y, L, at=(RAIL_L[0], RAIL_Y, -Z_HALF))
    p.box(RAIL_R[1] - RAIL_R[0], Y_BOT_SLAB - RAIL_Y, L, at=(RAIL_R[0], RAIL_Y, -Z_HALF))
    # terminal-end set-back of the outer rail portions
    for x0, x1 in ((-X_HALF, -RAIL_END_X), (RAIL_END_X, X_HALF)):
        p.box(x1 - x0, Y_BOT_SLAB - RAIL_Y - 0.001, RAIL_END_Z - (-Z_HALF - 0.1),
              at=(x0, RAIL_Y - 0.1, -Z_HALF - 0.1), op="cut")
    # inner-edge latch notches (left notch x -4.0..-2.25, width 1.75)
    p.box(NOTCH_W + RAIL_L[1], Y_BOT_SLAB - RAIL_Y - 0.001, -6.35 - (-Z_HALF - 0.1),
          at=(-NOTCH_W, RAIL_Y - 0.1, -Z_HALF - 0.1), op="cut")            # left: z < -6.35
    for z0, z1 in ((-Z_HALF - 0.1, -27.85), (-14.65, -6.35)):              # right
        p.box(NOTCH_W - RAIL_R[0], Y_BOT_SLAB - RAIL_Y - 0.001, z1 - z0,
              at=(RAIL_R[0], RAIL_Y - 0.1, z0), op="cut")
    # centre feet
    for z0, z1 in FOOT_Z:
        p.box(2 * 2.25, Y_BOT_SLAB - RAIL_Y, z1 - z0, at=(-2.25, RAIL_Y, z0))
    # terminal-end holes
    for sx in (-1, 1):
        p.cyl(HOLE_D, HOLE_Z[1] - HOLE_Z[0], at=(sx * HOLE_X, HOLE_Y, HOLE_Z[0]),
              axis="z", op="cut")
    # shallow Ø3.48 counterbores on the end face, coaxial with the terminal holes
    for sx in (-1, 1):
        p.cyl(END_CB_D, END_CB_Z[1] - END_CB_Z[0], at=(sx * HOLE_X, HOLE_Y, END_CB_Z[0]),
              axis="z", op="cut")
    # shallow Ø3.2 dimples in the bottom-rail undersides
    for sx in (-1, 1):
        p.cyl(DIMPLE_D, DIMPLE_DEPTH, at=(sx * DIMPLE_X, DIMPLE_Y0, DIMPLE_Z),
              axis="y", op="cut")
    p.clean()
    p.connector("terminals", at=(0, HOLE_Y, -Z_HALF), dir="-z")   # contact end
    p.connector("rails", at=(0, RAIL_Y, 0), dir="-y")             # the NP-F latch rails
    return p
