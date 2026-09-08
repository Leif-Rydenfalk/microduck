"""part:microduck-yaw2roll — the hip-yaw output link that carries the hip-roll
servo, rebuilt.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. Parametric — nobody
has Pollen's CAD. Every number below was READ OFF Pollen's published mesh
`reference/pollen-microduck-rl/assets/yaw2roll.stl` (metres, decimated) on
2026-09-01 with `cad-mjcf sections`, `cecad.meshfeatures.cylinders` and the
ray-cast `cecad.meshfeatures.profile` (added for this part: material
intervals along a line, which is how the ears, the 1.4 mm walls and the
lug outline were read), and the rebuild is graded against that mesh by
`cad-refcheck` (see evidence/): r1 2026-09-01 p95 0.79/0.27 mm (the -x
blend arc of the lug swept the wrong way, 4.55 mm max), r2 2026-09-02
p95 0.05/0.05 mm, 19/19 features — out/refcheck/yaw2roll/r1, r2.

FRAME — Pollen's mesh frame, kept on purpose: X across the leg 6..29
(centre 17.5), Y from the ears (-13.3) to the front face (12.5), Z from the
lug tip (-5) to the ear tops (15.5). The hip-YAW axis is the line
x 17.5, y -2 along z (the disc on top); the hip-ROLL axis is the line
x 17.5, z 0 along y (the lug hole). Both from the MJCF body/joint
transforms (kin_robot_walk.xml body yaw2roll pos 0.006 0.0175 -0.005
quat 0 -0.707107 -0.707107 0; geom yaw2roll pos -17.5 -2 12.5 quat 0 1 0 0).

WHAT IT IS. A 2.5 mm plate (z 9.5..12) with, on top, the Ø19 x 0.5 shoulder
and Ø16 x 1.95 boss that seat the trunk's 22x16x4 yaw bearing (MJCF: the
bearing geom sits at the hip-yaw joint origin = mesh (17.5, -2, 12.5), axis
+z, and the bearing mesh spans 0..4 along its axis, so it occupies z
12.5..16.5 here — the last 2.05 mm of its bore rides the horn's Ø16 boss), and the
4 x M2 (Ø2.2, Ø4.4 c'bore from below, on Ø12 PCD) that bolt the yaw servo
horn to it; two ears (5 wide, semicircular top r2.5, Ø2.05 tap holes along
y) at the back that the bearing_roll plate screws to; two 1.4 mm side walls
with a 27.6 deg sloped bottom edge that flank the XL330 roll servo; and a
front block (y 9.5..12.5) shaped as the lug outline (r5 round on the roll
axis, 60 deg flanks, r5 blends into the sides) that carries the servo's
two top M2 screws (Ø2.4, Ø4.84 c'bore) and the idler stub (Ø5 x 1.8 boss,
Ø2.7 through, Ø5.5 c'bore) on the roll axis.
"""
import math

# ---- measured off yaw2roll.stl (mm) -----------------------------------------
X0, X1 = 6.0, 29.0                    # sections --axis y: x range [6, 29] at every level
XC = 17.5                             # symmetry / both axes: features come in pairs about x 17.5
Y0, Y1 = -13.3, 12.5                  # sections --axis x: y range [-13.3, 12.5]
Z_BOT, Z_TOP = 9.5, 12.0              # profile z-rays at (12, y): plate material [9.5, 12] for every y not under a boss
FRONT_FILLET_R = 2.0                  # z-rays at x 17.5: top 12.482 @ y 10.25, 12.059 @ 11.25, 11.466 @ 11.75, 10.962 @ 12.25 -> r 2 centred (y 10.5, z 10)

# yaw axis boss (meshfeatures.cylinders: bosses Ø19 @ z 12.25 len 0.5, Ø16 @ z 13.475 len 1.95, both centred (17.5, -2))
YAW_C = (17.5, -2.0)
SHOULDER_D, SHOULDER_Z1 = 19.0, 12.5
BOSS_D, BOSS_Z1 = 16.0, 14.45
# yaw horn screws: 4 holes Ø2.2 at (17.5,4) (17.5,-8) (23.5,-2) (11.5,-2) = radius 6 on the axes; Ø4.4 c'bores centred z 10.5 len 2 -> z 9.5..11.5
HORN_HOLE_D, HORN_PCD_R = 2.2, 6.0
HORN_CBORE_D, HORN_CBORE_Z1 = 4.4, 11.5

# ears: z-rays at (x, -12): top 13.775 @ x 6.125, 14.313 @ 6.375, 15.085 @ 7.125, 15.495 @ 8.375 -> semicircle r 2.5 centred (8.5, 13);
#       x-rays at z 12.2, y -12.8: material [6, 11] (and [24, 29]); the plan-view end is the measured polyline below
EAR_X0, EAR_X1 = 6.0, 11.0
EAR_Z_C, EAR_R = 13.0, 2.5
EAR_END = [                           # (x, y) of the ear's end face read at z 12.2 (x-rays), the hole cone y -9.3..-8.9 skipped
    (11.0, -11.5), (10.95, -11.225), (10.73, -10.98), (10.43, -10.74), (10.12, -10.49),
    (9.86, -10.25), (9.60, -10.0), (8.99, -9.3), (8.53, -8.78), (8.35, -8.54),
    (8.03, -8.05), (7.71, -7.56), (7.26, -7.08), (6.91, -6.83), (6.0, -7.0)]
EAR_HOLE_D, EAR_HOLE_Z, EAR_HOLE_X = 2.05, 12.5, (8.5, 26.5)   # cylinders: Ø2.05 axis y, centre y -11.3, len 4 -> y -13.3..-9.3
EAR_HOLE_Y1 = -9.3

# side walls: y-rays at z 5 sweeping x: [1.6, 12.5] for x 6.05..7.35, plate-only from 7.45 -> wall x 6..7.4 (and 27.6..29)
WALL_T = 1.4
# sloped underside: z-rays at x 6.3: bottom 8.902 @ y -5.858 ... 2.152 @ y 7.042 -> z = 9.5 - 0.523 (y + 7.0); flat from y 7.25
SLOPE_Y0, SLOPE_Z0 = -7.0, 9.5
SLOPE_DZDY = 0.523
SLOPE_Y1 = 7.25
# front block: z-rays at x 8.5: plate-only up to y 9.275, full depth from y 9.771 -> starts at y 9.5; ends at the front face 12.5
BLOCK_Y0 = 9.5
# lug outline (x-rays at y 11, half-widths about x 17.5): 1.55 @ z -4.75 ... 8.7 @ -0.75 = tan 60 deg flank tangent to r 5 about (17.5, 0);
#   10.07 @ 0.25, 10.83 @ 1.25, 11.27 @ 2.25, 11.5 @ 3.75 = r 5 blend centred (hw 6.5, z 3.75) into the vertical sides
LUG_R, LUG_C_Z = 5.0, 0.0
FLANK_SLOPE = math.tan(math.radians(60))          # d(half-width)/dz
BLEND_R, BLEND_C = 5.0, (6.5, 3.75)                # (half-width, z) of the blend centre
# idler stub on the roll axis: boss Ø5 centre y 8.6 len 1.8 -> y 7.7..9.5; hole Ø2.7 centre y 8.85 len 2.3 -> 7.7..10.0; c'bore Ø5.5 centre 11.25 len 2.5 -> 10..12.5
ROLL_C = (17.5, 0.0)
STUB_D, STUB_Y0 = 5.0, 7.7
STUB_HOLE_D, STUB_HOLE_Y1 = 2.7, 10.0
STUB_CBORE_D = 5.5
# servo screws: holes Ø2.4 axis y centre (25.5/9.5, 9.9, 7.5) len 0.8 -> y 9.5..10.3; c'bores Ø4.84 centre y 11.4 len 2.2 -> 10.3..12.5
SERVO_HOLE_X, SERVO_HOLE_Z = (9.5, 25.5), 7.5
SERVO_HOLE_D, SERVO_CBORE_D, SERVO_CBORE_Y0 = 2.4, 4.84, 10.3

MATERIAL = "PLA"


def _lug_outline(z_top=9.6, n=10):
    """(z, x) polygon — the in-plane pair for a prism along y — of the front
    block / wall bottom: r5 round on the roll axis, 60 deg flanks, r5 blends,
    vertical sides, closed above the plate underside."""
    pts = []
    # bottom arc, from the -x tangent point round the bottom to the +x one
    for i in range(n + 1):
        a = math.radians(-120 + 60 * i / n)
        pts.append((LUG_C_Z + LUG_R * math.sin(a), XC + LUG_R * math.cos(a)))
    # +x flank up to the blend tangent point, blend arc to the vertical side
    hw_c, z_c = BLEND_C
    for i in range(n + 1):
        a = math.radians(-60 + 60 * i / n)
        pts.append((z_c + BLEND_R * math.sin(a), XC + hw_c + BLEND_R * math.cos(a)))
    pts.append((z_top, X1))
    pts.append((z_top, X0))
    # -x blend: the mirror of the +x one, 180 -> 240 deg (r1 swept 180 -> 120, i.e. UP,
    # and left the -x flank 4.8 mm short at z 3.75: ref x 6.0, ours 10.77 — meshslice at y 11, r1 overlay_left)
    for i in range(n + 1):
        a = math.radians(180 + 60 * i / n)
        pts.append((z_c + BLEND_R * math.sin(a), XC - hw_c + BLEND_R * math.cos(a)))
    return pts


def _slope_cut():
    """(y, z) polygon — the in-plane pair for a prism along x — of everything
    below the sloped underside, for y < SLOPE_Y1 and z < the plate."""
    z1 = SLOPE_Z0 - SLOPE_DZDY * (SLOPE_Y1 - SLOPE_Y0)
    return [(SLOPE_Y0, SLOPE_Z0), (SLOPE_Y1, z1), (SLOPE_Y1, -10.0), (-20.0, -10.0), (-20.0, SLOPE_Z0)]


def build(doc, params=None):
    from cecad.core import Part
    if params:
        raise ValueError("microduck-yaw2roll takes no build parameters (got %s)" % sorted(params))
    p = Part("microduck-yaw2roll", material=MATERIAL)
    # plate
    p.box(X1 - X0, Y1 - Y0, Z_TOP - Z_BOT, at=(X0, Y0, Z_BOT))
    # walls + front block: the lug outline extruded along y, hollowed between the walls, trimmed by the slope
    p.prism(_lug_outline(), Y1 - SLOPE_Y0 + 0.5, at=(0, SLOPE_Y0 - 0.5, 0), axis="y")
    p.box(X1 - X0 - 2 * WALL_T, BLOCK_Y0 - (Y0 - 1), 30, at=(X0 + WALL_T, Y0 - 1, Z_BOT - 30), op="cut")
    p.prism(_slope_cut(), X1 - X0 + 2, at=(X0 - 1, 0, 0), axis="x", op="cut")
    # front-top edge round r2 (y 12.5, z 12): cut the corner, put the quarter round back
    p.box(X1 - X0 + 2, FRONT_FILLET_R + 1, FRONT_FILLET_R + 1, at=(X0 - 1, Y1 - FRONT_FILLET_R, Z_TOP - FRONT_FILLET_R), op="cut")
    p.cyl(2 * FRONT_FILLET_R, X1 - X0, at=(X0, Y1 - FRONT_FILLET_R, Z_TOP - FRONT_FILLET_R), axis="x")
    p.box(X1 - X0, FRONT_FILLET_R, FRONT_FILLET_R, at=(X0, Y1 - 2 * FRONT_FILLET_R, Z_TOP - 2 * FRONT_FILLET_R))
    # yaw boss: Ø19 shoulder, Ø16 bearing seat, 4 x M2 horn screws with c'bores from below
    p.cyl(SHOULDER_D, SHOULDER_Z1 - Z_TOP + 0.01, at=(YAW_C[0], YAW_C[1], Z_TOP - 0.01), axis="z")
    p.cyl(BOSS_D, BOSS_Z1 - SHOULDER_Z1 + 0.01, at=(YAW_C[0], YAW_C[1], SHOULDER_Z1 - 0.01), axis="z")
    for dx, dy in ((HORN_PCD_R, 0), (-HORN_PCD_R, 0), (0, HORN_PCD_R), (0, -HORN_PCD_R)):
        p.cyl(HORN_HOLE_D, 10, at=(YAW_C[0] + dx, YAW_C[1] + dy, Z_BOT - 1), axis="z", op="cut")
        p.cyl(HORN_CBORE_D, HORN_CBORE_Z1 - Z_BOT + 1, at=(YAW_C[0] + dx, YAW_C[1] + dy, Z_BOT - 1), axis="z", op="cut")
    # ears: block + semicircular top, trimmed to the measured plan-view end, tapped hole along y
    for xa in (EAR_X0, X1 - (EAR_X1 - EAR_X0)):
        p.box(EAR_X1 - EAR_X0, -Y0 - 5.0, EAR_Z_C - Z_TOP + 0.01, at=(xa, Y0, Z_TOP - 0.01))
        p.cyl(2 * EAR_R, -Y0 - 5.0, at=(xa + EAR_R, Y0, EAR_Z_C), axis="y")
    end = list(EAR_END)
    trim = end + [(EAR_X0, -4.0), (EAR_X1 + 0.5, -4.0), (EAR_X1 + 0.5, end[0][1])]
    p.prism(trim, 5, at=(0, 0, Z_TOP), axis="z", op="cut")
    p.prism([(2 * XC - x, y) for (x, y) in trim], 5, at=(0, 0, Z_TOP), axis="z", op="cut")
    for x in EAR_HOLE_X:
        p.cyl(EAR_HOLE_D, EAR_HOLE_Y1 - Y0 + 1, at=(x, Y0 - 1, EAR_HOLE_Z), axis="y", op="cut")
    # idler stub on the roll axis, its through hole and c'bore from the front face
    p.cyl(STUB_D, BLOCK_Y0 - STUB_Y0 + 0.01, at=(ROLL_C[0], STUB_Y0, ROLL_C[1]), axis="y")
    p.cyl(STUB_HOLE_D, STUB_HOLE_Y1 - STUB_Y0 + 1, at=(ROLL_C[0], STUB_Y0 - 1, ROLL_C[1]), axis="y", op="cut")
    p.cyl(STUB_CBORE_D, Y1 - STUB_HOLE_Y1 + 1, at=(ROLL_C[0], STUB_HOLE_Y1, ROLL_C[1]), axis="y", op="cut")
    # servo screws through the front block
    for x in SERVO_HOLE_X:
        p.cyl(SERVO_HOLE_D, Y1 - BLOCK_Y0 + 2, at=(x, BLOCK_Y0 - 1, SERVO_HOLE_Z), axis="y", op="cut")
        p.cyl(SERVO_CBORE_D, Y1 - SERVO_CBORE_Y0 + 1, at=(x, SERVO_CBORE_Y0, SERVO_HOLE_Z), axis="y", op="cut")
    p.clean()
    # interfaces
    p.connector("yaw_horn", at=(YAW_C[0], YAW_C[1], BOSS_Z1), dir="+z")
    p.connector("yaw_bearing_seat", at=(YAW_C[0], YAW_C[1], SHOULDER_Z1), dir="+z")
    p.connector("roll_idler", at=(ROLL_C[0], BLOCK_Y0, ROLL_C[1]), dir="-y")
    p.connector("servo_screw_a", at=(SERVO_HOLE_X[0], BLOCK_Y0, SERVO_HOLE_Z), dir="-y")
    p.connector("servo_screw_b", at=(SERVO_HOLE_X[1], BLOCK_Y0, SERVO_HOLE_Z), dir="-y")
    p.connector("ear_tap_a", at=(EAR_HOLE_X[0], Y0, EAR_HOLE_Z), dir="-y")
    p.connector("ear_tap_b", at=(EAR_HOLE_X[1], Y0, EAR_HOLE_Z), dir="-y")
    return p
