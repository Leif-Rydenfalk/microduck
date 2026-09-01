"""part:microduck-bearing-roll — the idler plate on the hip-roll servo, rebuilt.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. Parametric — nobody
has Pollen's CAD. Every number below was READ OFF Pollen's published mesh
`reference/pollen-microduck-rl/assets/bearing_roll.stl` (metres, decimated)
on 2026-09-01 with `cad-mjcf sections`, `cecad.meshfeatures.cylinders` and
the ray-cast `cecad.meshfeatures.profile` (added for this part), and the
rebuild is graded against that mesh by `cad-refcheck` (see evidence/).

FRAME — Pollen's mesh frame, kept on purpose. It is the SAME frame as
yaw2roll.stl (both geoms sit at pos (-17.5, -2, 12.5) quat (0,±1,0,0) in the
MJCF body): X across the leg 6..29, Y = the plate's THICKNESS (-14.5..-13.5),
Z = down the servo -24.5..15.5. The hip-roll axis is the line x = 17.5,
z = 0 along y. Keeping the frame means the MJCF geom pos/quat place the
part with no re-derivation and refcheck needs no alignment.

WHAT IT IS. A 23 x 40 x 1 mm plate that closes the hip-roll XL330 on its
horn side: it screws to the two ears of yaw2roll (2 x Ø2.2 at z 12.5),
screws into the servo's two bottom through-holes (2 x Ø2.2 at z -22.5),
locates in the servo's two top through-holes with 2 conical pegs
(Ø1.8 -> Ø1.6 x 2 mm at z 7.5), and passes the Ø16 servo horn through a
Ø19 window on the roll axis. The 22x16x4 bearing sits flat on the BACK face
(y -14.5): the MJCF puts its geom at mesh (17.5, -18.5, 0) with its axis
along +y and the bearing mesh spans 0..4 along its axis (meshslice, 2026-09-02),
so it occupies y -18.5..-14.5; the horn's Ø16 x 3 boss (y -16.5..-13.5) runs
through the window into the bore, and hip_l's Ø16 x 1.95 boss fills the rest.
"""
import math

# ---- measured off bearing_roll.stl (mm) -------------------------------------
X0, X1 = 6.0, 29.0                # cad-mjcf sections --axis y: x range [6, 29] at every level
Z0, Z1 = -24.5, 15.5              # z range [-24.5, 15.5]
Y_BACK, Y_FRONT = -14.5, -13.5    # sections --axis z: y range [-14.5, -13.5] at every z except the pegs
CORNER_R = 2.5                    # z = -23.667 -> x [6.64, 28.36] and z = 14.667 -> same: r 2.5 fits both (0.64 = 2.5 - sqrt(2.5^2 - 1.667^2))
# holes (meshfeatures.cylinders, all axis y, all Ø2.2, all 355 deg cover)
EAR_HOLES = ((8.5, 12.5), (26.5, 12.5))       # centres (x, z) — match the yaw2roll ear tap holes at x 8.5 / 26.5, z 12.5
SERVO_HOLES = ((9.5, -22.5), (25.5, -22.5))   # centres (x, z) — match the XL330 bottom through-holes (xl330.stl at (9.5/25.5, z -22.5) in this frame)
HOLE_D = 2.2
WINDOW_D, WINDOW_C = 19.0, (17.5, 0.0)        # Ø19 hole centre (17.5, 0.0) — the roll axis; the XL330 horn is Ø16
# pegs: sections --axis y at y -13.44: x 8.603..26.397, z 6.603..8.397 (two Ø1.79 discs at x 9.5 / 25.5, z 7.5);
#       at y -11.56: 8.70..26.30, 6.70..8.30 (Ø1.60) -> conical pegs 2 mm tall on the +y face
PEGS = ((9.5, 7.5), (25.5, 7.5))
PEG_D_BASE, PEG_D_TIP, PEG_H = 1.8, 1.6, 2.0

MATERIAL = "PLA"


def _rounded_rect_zx(z0, z1, x0, x1, r, n=8):
    """(z, x) polygon — the in-plane pair for a prism along y."""
    pts = []
    corners = [((z1 - r, x1 - r), 0), ((z0 + r, x1 - r), 90), ((z0 + r, x0 + r), 180), ((z1 - r, x0 + r), 270)]
    for (cz, cx), a0 in corners:
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cz + r * math.cos(a), cx + r * math.sin(a)))
    return pts


def build(doc, params=None):
    from cecad.core import Part
    if params:
        raise ValueError("microduck-bearing-roll takes no build parameters (got %s)" % sorted(params))
    p = Part("microduck-bearing-roll", material=MATERIAL)
    p.prism(_rounded_rect_zx(Z0, Z1, X0, X1, CORNER_R), Y_FRONT - Y_BACK, at=(0, Y_BACK, 0), axis="y")
    for (x, z) in EAR_HOLES + SERVO_HOLES:
        p.cyl(HOLE_D, 3, at=(x, Y_BACK - 1, z), axis="y", op="cut")
    p.cyl(WINDOW_D, 3, at=(WINDOW_C[0], Y_BACK - 1, WINDOW_C[1]), axis="y", op="cut")
    for (x, z) in PEGS:
        p.cone(PEG_D_BASE, PEG_D_TIP, PEG_H + 0.01, at=(x, Y_FRONT - 0.01, z), axis="y")
    p.clean()
    # interfaces: the roll axis through the window, the two screw pairs, the pegs
    p.connector("horn_window", at=(WINDOW_C[0], Y_BACK, WINDOW_C[1]), dir="-y")
    p.connector("ear_screw_a", at=(EAR_HOLES[0][0], Y_BACK, EAR_HOLES[0][1]), dir="+y")
    p.connector("ear_screw_b", at=(EAR_HOLES[1][0], Y_BACK, EAR_HOLES[1][1]), dir="+y")
    p.connector("servo_screw_a", at=(SERVO_HOLES[0][0], Y_BACK, SERVO_HOLES[0][1]), dir="+y")
    p.connector("servo_screw_b", at=(SERVO_HOLES[1][0], Y_BACK, SERVO_HOLES[1][1]), dir="+y")
    p.connector("peg_a", at=(PEGS[0][0], Y_FRONT, PEGS[0][1]), dir="+y")
    p.connector("peg_b", at=(PEGS[1][0], Y_FRONT, PEGS[1][1]), dir="+y")
    return p
