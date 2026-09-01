"""part:microduck-trunk-base — the chassis plate ("trunk_base" in Pollen's
MJCF), rebuilt.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. Parametric —
there is no geometry/*.step because nobody has Pollen's CAD. Every number
below was READ OFF Pollen's published mesh
`reference/pollen-microduck-rl/assets/trunk_base.stl` (metres, decimated)
on 2026-09-01 with `cad-mjcf sections`, `cad-mjcf probe` (material
intervals along a line — added to cecad for this part) and
`cecad.meshfeatures.cylinders`, and the rebuild is graded against that
mesh by `cecad.meshcompare` (see evidence/).

FRAME — Pollen's mesh frame, kept on purpose: Z is the plate's THICKNESS
(z 16.5 .. 17.5, pins to 19.5), X its LENGTH (-28.5 .. 28.5), Y its WIDTH
(-13 .. 23). The MJCF places the mesh at pos (4, 0, -17.5) mm, quat
(0.707, 0, 0, 0.707) — a 90 deg turn about z — in the trunk_base body, so
this frame needs no re-derivation to sit in the assembly.

WHAT IT IS. A 57 x 36 x 1 mm plate with two Ø19 holes 35 mm apart: the
hip-yaw XL330s hang under it (their axes are the MJCF joints left/right
_hip_yaw at body (6, ±17.5) = mesh (±17.5, -2) after the 90 deg turn).
Four Ø2.3 (M2 clearance) holes along the +y edge take the power_support's
Ø2.5 flange holes (same x = ±9.5, same y = 20.5 in the shared frame) and
the two outer shell screws; four Ø1.8 tapered locating pins stand 2 mm
proud of the top along the -y edge; a 6 x 12 slot in the middle passes
the servo cables.
"""
import math

# ---- measured off trunk_base.stl (mm) --------------------------------------
# sections --axis z: x -28.5..28.5, y -13..23 at every level 16.5..17.5
X0, X1 = -28.5, 28.5                  # plate length 57.0
Y0, Y1 = -13.0, 23.0                  # plate width 36.0
Z0, Z1 = 16.5, 17.5                   # plate thickness 1.0 (sections --axis x: z [16.5, 17.5])
CORNER_R = 2.0                        # y width 35.828 at x=±27.075 and x width 56.337 at y=-12.1 both fit R=2
# meshfeatures: two Ø19.0 holes, axis z, at (±17.5, -2.0); probe z=17 y=-2: gap x 8..27
HIP_HOLE_D = 19.0
HIP_HOLE_XY = ((-17.5, -2.0), (17.5, -2.0))
# meshfeatures: four Ø2.3 holes at y 20.5, x ±9.5 / ±25.5 (probe y=20.5: gaps -26.65..-24.35 etc.)
SCREW_D = 2.3
SCREW_XY = ((-25.5, 20.5), (-9.5, 20.5), (9.5, 20.5), (25.5, 20.5))
# slot: probe z=17 x=0 -> gap y -2..10; y=-2..5 -> gap x -3..3; at x=±2 the gap
# is y -1.732..9.732, which only R=2 corners give (R2 centred (1,0): dy=sqrt(4-1)=1.732)
SLOT_X0, SLOT_X1, SLOT_Y0, SLOT_Y1, SLOT_R = -3.0, 3.0, -2.0, 10.0, 2.0
# pins: probe z=18.5 y=-9.5 -> 1.696 wide at x ±9.5, ±25.5; sections --axis z
# give Ø1.787 at z 17.625 and Ø1.598 at z 19.425 (a 0.105/mm taper) -> Ø1.80
# at the plate face, Ø1.59 at the tip; probe along z: material 17.5..19.5
PIN_XY = ((-25.5, -9.5), (-9.5, -9.5), (9.5, -9.5), (25.5, -9.5))
PIN_D_BASE, PIN_D_TIP, PIN_H = 1.80, 1.59, 2.0

MATERIAL = "PLA"


def _rounded_rect(x0, x1, y0, y1, r, n=8):
    """(x, y) polygon of a rectangle with R corners, counter-clockwise."""
    pts = []
    corners = [((x1 - r, y1 - r), 0), ((x0 + r, y1 - r), 90), ((x0 + r, y0 + r), 180), ((x1 - r, y0 + r), 270)]
    for (cx, cy), a0 in corners:
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def build(doc, params=None):
    from cecad.core import Part
    if params:
        raise ValueError("microduck-trunk-base takes no build parameters (got %s)" % sorted(params))
    p = Part("microduck-trunk-base", material=MATERIAL)
    # the plate: 57 x 36 x 1, R2 corners, extruded along z
    p.prism(_rounded_rect(X0, X1, Y0, Y1, CORNER_R), Z1 - Z0, at=(0, 0, Z0), axis="z")
    # two Ø19 hip-yaw holes
    for x, y in HIP_HOLE_XY:
        p.cyl(HIP_HOLE_D, 5, at=(x, y, Z0 - 2), axis="z", op="cut")
    # four Ø2.3 M2 clearance holes along the +y edge
    for x, y in SCREW_XY:
        p.cyl(SCREW_D, 5, at=(x, y, Z0 - 2), axis="z", op="cut")
    # the cable slot 6 x 12, R2
    p.prism(_rounded_rect(SLOT_X0, SLOT_X1, SLOT_Y0, SLOT_Y1, SLOT_R), 5, at=(0, 0, Z0 - 2), axis="z", op="cut")
    # four tapered locating pins on the top face along the -y edge
    for x, y in PIN_XY:
        p.cone(PIN_D_BASE, PIN_D_TIP, PIN_H + 0.01, at=(x, y, Z1 - 0.01), axis="z")
    p.clean()
    # interfaces: the two hip-yaw axes (servo horn faces, down through the plate), the screw holes
    p.connector("hip_yaw_left", at=(-17.5, -2.0, Z1), dir="+z")
    p.connector("hip_yaw_right", at=(17.5, -2.0, Z1), dir="+z")
    return p
