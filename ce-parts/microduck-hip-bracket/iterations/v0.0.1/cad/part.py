"""part:microduck-hip-bracket — the hip-roll output bracket ("hip_l" in
Pollen's MJCF), rebuilt.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. Parametric —
there is no geometry/*.step because nobody has Pollen's CAD. Every number
below was READ OFF Pollen's published mesh
`reference/pollen-microduck-rl/assets/hip_l.stl` (metres, decimated) on
2026-09-01 with `ce-cad/bin/cad-mjcf sections`, `cecad.meshfeatures.cylinders`
and the 0.5 mm plane rasters in `out/hip-bracket/sections.py` (least-squares
circle fits for every arc), and the rebuild is graded against that mesh by
`cecad.meshcompare` (see evidence/).

FRAME — Pollen's mesh frame, kept on purpose: x 8 .. 40.45, y -25 .. 9.5,
z -9.5 .. 9.5. The part is SYMMETRIC in z (every feature sits at z = 0 or
z = +/-6), which is why Pollen places the same mesh in both hip_l (left)
and hip_l_2 (right) with the same pos/quat — there is no mirror part.
Keeping their frame means the MJCF geom pos (-17.5, 0, -18.5) mm / quat
(0.707107, -0.707107, 0, 0) places it in the hip_l body directly, and
meshcompare needs no alignment.

WHAT IT IS. An L-bracket joining the hip-ROLL servo (in yaw2roll) to the
hip-PITCH servo (in the thigh):
  * ROLL LEG — a plate perpendicular to y (y -21.5 .. -19.0, 2.5 thick),
    19 wide, rounded R9.5 about (x 17.5, z 0). On its +y face a Ø19 x 0.5
    disc and a Ø16 x 1.95 boss with a Ø6 blind recess; 4 x Ø2.4 on a Ø12
    bolt circle at 0/90/180/270 deg, counterbored Ø4.84 from the -y face
    down to y -19.5. The MJCF puts the hip_l body origin (= the roll axis)
    at mesh (17.5, -18.5, 0) with the axis along mesh -y, and the yaw2roll
    body's 22x16x4 bearing on this boss.
  * PITCH LEG — a plate perpendicular to x (x 34 .. 38, 4 thick), 19 wide,
    rounded R9.5 about (y 0, z 0) at +y, with the SAME disc/boss/hole
    pattern on its +x face. The MJCF's hip-pitch joint passes through mesh
    (42.5, 0, 0) along x and the hip_l body's own 22x16x4 bearing sits on
    this boss (mesh x 38.5 .. 42.5 = boss + the thigh servo's horn).
  * CORNER — inner fillet R6 (centre 28, -13), outer round R8 (centre 30,
    -13.5), and a 10 mm wide GUSSET rib (z +/-5) filling the outer corner
    out to y = -25 and x = 38 with an R5 corner (centre 33, -20), an R5
    round end about the roll boss centre, R2 root fillets, R1 top rounds.
"""
import math

# ---- measured off hip_l.stl (mm) -------------------------------------------
# bbox (cad-mjcf meshes): x 8.0..40.45, y -25.0..9.497, z -9.5..9.5
W = 19.0                              # both plates are 19 wide in z (z-sections)
HZ = W / 2                            # 9.5
R_END = 9.5                           # both plate ends: R9.5 (x=9: |z|=4.23 -> r 9.5; x=38.2 rows: y=+/-9.49)

# roll leg (plate perpendicular to y)
Y_BACK = -25.0                        # rib top face (x=20 section: y -25.00 for |z|<4.25)
Y_PLATE_BOT = -21.5                   # thin plate -y face (x=9/11/13/20 sections: -21.5)
Y_PLATE_TOP = -19.0                   # thin plate +y face outside the disc (x=26: -19.0 for |z|>4.24)
Y_DISC_TOP = -18.5                    # Ø19 disc face (x=20 rows |z|<1.5: -18.5; disc edge = R9.5 circle in z-sections)
Y_BOSS_TOP = -16.55                   # Ø16 boss face (meshfeatures boss Ø16 centre y -17.525 len 1.95)
X_ROLL = 17.5                         # roll axis / boss centre (meshfeatures boss centre x 17.5)

# pitch leg (plate perpendicular to x)
X_PLATE_BACK = 34.0                   # z=0 rows y -9.75..-13: [34.00, 38.00]
X_PLATE_FRONT = 38.0
X_DISC_FRONT = 38.5                   # z=0 rows |y|<9.5: to 38.50; x=38.2 section is the R9.5 circle
X_BOSS_FRONT = 40.45                  # boss Ø16 centre x 39.475 len 1.95 -> 38.5..40.45
Y_PITCH = 0.0                         # pitch boss centre (meshfeatures: (39.475, 0, 0))

DISC_D = 19.0                         # x=38.2 raster: full circle r 9.49
BOSS_D = 16.0                         # meshfeatures boss d 16.0 (both faces)
RECESS_D = 6.0                        # meshfeatures hole Ø6.0, len 1.95 = boss height only (blind, floor at the disc)
HOLE_D = 2.4                          # 4 x Ø2.4, len 2.95 (through boss + disc + 1 mm of plate)
HOLE_PCD = 12.0                       # holes at (±6, 0) and (0, ±6) from the boss centre
CBORE_D = 4.84                        # Ø4.84 counterbores from the far face
CBORE_TO_X = 37.5                     # pitch side: hole len 2.95 from 40.45 -> floor at 37.5
CBORE_TO_Y = -19.5                    # roll side: hole len 2.95 from -16.55 -> floor at -19.5 (x=11/13 rows: [-19.5,-16.55])

# corner
FIL_IN_R, FIL_IN_C = 6.0, (28.0, -13.0)     # inner fillet: circle fit z=0/z=8, residual 0.003 mm
RND_OUT_R, RND_OUT_C = 8.0, (30.0, -13.5)   # outer round (|z|>5): circle fit z=6.5..9, residual 0.003 mm
RIB_HW = 5.0                          # rib half-width (x=20/26/30 flank profiles: wall at z 5.00)
RIB_END_R = 5.0                       # rib -x end: arc about (17.5, 0), r 5.05 at y -23.5
RIB_CORNER_R, RIB_CORNER_C = 5.0, (33.0, -20.0)   # circle fit z=0 corner, residual 0.003 mm
RIB_ROOT_FIL = 2.0                    # flank->plate fillet (x=20 profile: (5.31,-22.44) (5.59,-22.12) (6.2,-21.63))
RIB_TOP_RND = 1.0                     # rib top edge round (x=20: (4.47,-24.88) (4.68,-24.73) (4.87,-24.5))
PLATE_EDGE_RND = 0.75                 # plate z-edges (x=20: z 9.43 -> y -21.07; y=-5: z 9.41 -> x 37.61)

MATERIAL = "PLA"


def _arc(c, r, a0, a1, n=16):
    """points on a circle from angle a0 to a1 (deg), inclusive"""
    return [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def _stadium(cu, cv, r, u_far, n=24):
    """(u, v) outline: semicircle of radius r about (cu, cv) on the -u side,
    straight to u_far. v is +/- r."""
    pts = [(u_far, -r)]
    pts += _arc((cu, cv), r, -90, -270, n)   # from (cu, cv-r) over (cu-r, cv) to (cu, cv+r)
    pts.append((u_far, r))
    return pts


def build(doc, params=None):
    from cecad.core import Part
    if params:
        raise ValueError("microduck-hip-bracket takes no build parameters (got %s)" % sorted(params))
    p = Part("microduck-hip-bracket", material=MATERIAL)

    # 1. GUSSET RIB first (its rounded end is cut before the plates exist).
    #    x-y outline: y -25 .. -19 out to x 34, then up the pitch face to -13.5,
    #    with the R5 corner at (38, -25). Extruded z -5 .. 5.
    rib = [(X_ROLL - RIB_END_R, Y_BACK), (RIB_CORNER_C[0], Y_BACK)]
    rib += _arc(RIB_CORNER_C, RIB_CORNER_R, -90, 0)          # (33,-25) -> (38,-20)
    rib += [(X_PLATE_FRONT, RND_OUT_C[1]), (X_PLATE_BACK, RND_OUT_C[1]),
            (X_PLATE_BACK, Y_PLATE_TOP), (X_ROLL - RIB_END_R, Y_PLATE_TOP)]
    p.prism(rib, 2 * RIB_HW, at=(0, 0, -RIB_HW), axis="z")
    #    round its -x end: cut everything outside the R5 semicircle about (17.5, z 0)
    waste = [(-RIB_HW - 0.1, X_ROLL)]                        # (z, x) pairs for axis="y"
    waste += [(v, u) for (u, v) in _arc((X_ROLL, 0.0), RIB_END_R, -90, -270)]
    waste += [(RIB_HW + 0.1, X_ROLL), (RIB_HW + 0.1, X_ROLL - RIB_END_R - 2),
              (-RIB_HW - 0.1, X_ROLL - RIB_END_R - 2)]
    p.prism(waste, Y_PLATE_TOP - Y_BACK + 0.2, at=(0, Y_BACK - 0.1, 0), axis="y", op="cut")

    # 2. THIN ROLL PLATE: stadium in (z, x), extruded along y from -21.5 by 2.5
    plate = [(v, u) for (u, v) in _stadium(X_ROLL, 0.0, R_END, X_PLATE_BACK)]
    p.prism(plate, Y_PLATE_TOP - Y_PLATE_BOT, at=(0, Y_PLATE_BOT, 0), axis="y")

    # 3. CORNER: one x-y polygon = outer R8 quarter-round minus the inner R6
    #    fillet circle, full height z +/-9.5
    corner = [(RND_OUT_C[0], Y_PLATE_BOT)]
    corner += _arc(RND_OUT_C, RND_OUT_R, -90, 0)             # (30,-21.5) -> (38,-13.5)
    yi = RND_OUT_C[1]
    xi = FIL_IN_C[0] + math.sqrt(FIL_IN_R ** 2 - (yi - FIL_IN_C[1]) ** 2)   # inner circle at y -13.5
    a_in = math.degrees(math.atan2(yi - FIL_IN_C[1], xi - FIL_IN_C[0]))
    corner += [(xi, yi)]
    corner += _arc(FIL_IN_C, FIL_IN_R, a_in, -90)            # down the inner fillet to (28,-19)
    corner += [(RND_OUT_C[0], Y_PLATE_TOP)]
    p.prism(corner, W, at=(0, 0, -HZ), axis="z")

    # 4. PITCH PLATE: stadium in (y, z) with the R9.5 end at +y, down to -13.5,
    #    extruded along x from 34 by 4
    pitch = [(v, u) for (u, v) in _stadium(-Y_PITCH, 0.0, R_END, -RND_OUT_C[1])]   # built as -y then flipped
    pitch = [(-u, v) for (u, v) in pitch]                    # (y, z): arc at +y, straight edge at y -13.5
    p.prism(pitch, X_PLATE_FRONT - X_PLATE_BACK, at=(X_PLATE_BACK, 0, 0), axis="x")

    # 5. rib root fillets R2 (concave, flank z=+/-5 meeting the plate bottom
    #    y=-21.5 and the R8 round) and R1 rounds on the rib top edges
    def _root(e):
        b = e.BoundBox
        return (abs(abs(b.ZMin) - RIB_HW) < 0.02 and abs(abs(b.ZMax) - RIB_HW) < 0.02
                and b.YMin > Y_PLATE_BOT - 0.05 and b.YMax < RND_OUT_C[1] + 0.05
                and b.XMin < X_PLATE_FRONT - 0.05)
    p.fillet(RIB_ROOT_FIL, where=_root)

    def _top(e):
        b = e.BoundBox
        on_top = b.YMax < Y_BACK + 0.05                      # edges of the y=-25 face
        on_corner = (abs(abs(b.ZMin) - RIB_HW) < 0.02 and abs(abs(b.ZMax) - RIB_HW) < 0.02
                     and b.XMin > RIB_CORNER_C[0] - 0.05 and b.YMax < RIB_CORNER_C[1] + 0.05)
        return on_top or on_corner
    p.fillet(RIB_TOP_RND, where=_top)

    # 6. discs, bosses, recesses, holes, counterbores — roll face (axis y)
    p.cyl(DISC_D, Y_DISC_TOP - Y_PLATE_TOP + 0.01, at=(X_ROLL, Y_PLATE_TOP - 0.01, 0), axis="y")
    p.cyl(BOSS_D, Y_BOSS_TOP - Y_DISC_TOP + 0.01, at=(X_ROLL, Y_DISC_TOP - 0.01, 0), axis="y")
    p.cyl(RECESS_D, 5, at=(X_ROLL, Y_DISC_TOP, 0), axis="y", op="cut")
    for ang in (0, 90, 180, 270):
        dx = HOLE_PCD / 2 * math.cos(math.radians(ang))
        dz = HOLE_PCD / 2 * math.sin(math.radians(ang))
        p.cyl(HOLE_D, 12, at=(X_ROLL + dx, Y_BACK - 1, dz), axis="y", op="cut")
        p.cyl(CBORE_D, CBORE_TO_Y - Y_BACK + 1, at=(X_ROLL + dx, Y_BACK - 1, dz), axis="y", op="cut")
    # pitch face (axis x)
    p.cyl(DISC_D, X_DISC_FRONT - X_PLATE_FRONT + 0.01, at=(X_PLATE_FRONT - 0.01, Y_PITCH, 0), axis="x")
    p.cyl(BOSS_D, X_BOSS_FRONT - X_DISC_FRONT + 0.01, at=(X_DISC_FRONT - 0.01, Y_PITCH, 0), axis="x")
    p.cyl(RECESS_D, 5, at=(X_DISC_FRONT, Y_PITCH, 0), axis="x", op="cut")
    for ang in (0, 90, 180, 270):
        dy = HOLE_PCD / 2 * math.cos(math.radians(ang))
        dz = HOLE_PCD / 2 * math.sin(math.radians(ang))
        p.cyl(HOLE_D, 12, at=(X_PLATE_BACK - 1, Y_PITCH + dy, dz), axis="x", op="cut")
        p.cyl(CBORE_D, CBORE_TO_X - X_PLATE_BACK + 1, at=(X_PLATE_BACK - 1, Y_PITCH + dy, dz), axis="x", op="cut")
    p.clean()

    # interfaces: the two joint axes (see cad/interfaces.json)
    p.connector("roll_boss", at=(X_ROLL, Y_BOSS_TOP, 0), dir="+y")
    p.connector("pitch_boss", at=(X_BOSS_FRONT, Y_PITCH, 0), dir="+x")
    return p
