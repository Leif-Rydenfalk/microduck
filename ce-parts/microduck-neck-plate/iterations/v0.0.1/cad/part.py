"""part:microduck-neck-plate — one of the two neck plates ("neck" in
Pollen's MJCF), rebuilt parametrically.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. There is no
geometry/*.step because nobody has Pollen's CAD. Every number below was
READ OFF Pollen's published mesh
`reference/pollen-microduck-rl/assets/neck.stl` (metres, decimated) on
2026-09-02 with `cecad.meshslice.intervals` (probe lines quoted per
number) and `cecad.meshfeatures.cylinders`, and the rebuild is graded
against that mesh by `ce-cad/bin/cad-refcheck` (see evidence/).

FRAME — Pollen's mesh frame, kept on purpose: x 0..2 (the plate's
THICKNESS), y -32..-12 (its 20 mm length), z 69.5..80.5 (its 11 mm
width). The MJCF places this mesh TWICE in the `neck` body (pos
(22, 50, 28) and (22, 50, 3) mm, same quat (0.5, 0.5, 0.5, -0.5)) — the
two parallel plates that span the 50 mm neck between the neck-pitch
XL330 (in the trunk) and the head-pitch XL330 (at the top of the neck).

WHAT IT IS. A 2 mm flat plate, rounded-rectangle outline, with four
Ø2.3 through holes: two at y = -30 and two at y = -14 (16 mm apart —
the gap between the two servo cases 50 mm axis-to-axis minus one 34 mm
XL330 body), each pair 5 mm apart in z. Each pair takes the M2 side
screws of one XL330 case.
"""

# ---- measured off neck.stl (mm) --------------------------------------------
# bbox (meshslice.load vertices): x 0..2, y -32..-12, z 69.5..80.5
T = 2.0                    # thickness: intervals along x at (y-22,z75): [(0.0, 2.0)]
Y0, Y1 = -32.0, -12.0      # length 20: intervals along y at (x1,z75): [(-32, -12)]
Z0, Z1 = 69.5, 80.5        # width 11: intervals along z at (x1,y-22): bbox
R_CORNER = 2.0             # corner round: y-extent at z 69.6 is -30.619..-13.381
                           #   (lost 1.381 at 0.1 above the face -> R 2.0; at
                           #   z 70.0 lost 0.679 -> R 2.0 again)
HOLE_D = 2.3               # 4 holes, meshfeatures: d 2.3, cover 355 deg,
                           #   residual 0.000, at (y,z) = (-30/-14, 72.5/77.5)
HOLE_Y = (-30.0, -14.0)    # z-scan at y -30: gaps 71.35..73.65 & 76.35..78.65
HOLE_Z = (72.5, 77.5)      #   -> Ø2.3 centred at z 72.5 and 77.5
MATERIAL = "PLA"

import math


def _rounded_rect(u0, u1, v0, v1, r, n=12):
    pts = []
    corners = [((u1 - r, v1 - r), 0), ((u0 + r, v1 - r), 90),
               ((u0 + r, v0 + r), 180), ((u1 - r, v0 + r), 270)]
    for (cu, cv), a0 in corners:
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cu + r * math.cos(a), cv + r * math.sin(a)))
    return pts


def build(doc, params=None):
    from cecad.core import Part
    if params:
        raise ValueError("microduck-neck-plate takes no build parameters (got %s)" % sorted(params))
    p = Part("microduck-neck-plate", material=MATERIAL)
    # the plate: 2 mm prism along x of the R2 rounded rectangle
    p.prism(_rounded_rect(Y0, Y1, Z0, Z1, R_CORNER), T, at=(0, 0, 0), axis="x")
    # 4 x Ø2.3 M2 clearance through holes
    for y in HOLE_Y:
        for z in HOLE_Z:
            p.cyl(HOLE_D, T + 2, at=(-1, y, z), axis="x", op="cut")
    # one connector per servo-case hole pair (each pair bolts to one XL330)
    p.connector("servo_a_case", at=(0.0, HOLE_Y[0], (HOLE_Z[0] + HOLE_Z[1]) / 2), dir=(-1.0, 0.0, 0.0))
    p.connector("servo_b_case", at=(0.0, HOLE_Y[1], (HOLE_Z[0] + HOLE_Z[1]) / 2), dir=(-1.0, 0.0, 0.0))
    return p
