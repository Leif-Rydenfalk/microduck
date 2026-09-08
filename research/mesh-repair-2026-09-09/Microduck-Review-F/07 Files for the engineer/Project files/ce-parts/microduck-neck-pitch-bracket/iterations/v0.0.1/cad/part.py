"""part:microduck-neck-pitch-bracket — the head-pitch output bracket
("neck_pitch" in Pollen's MJCF), rebuilt parametrically.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. There is no
geometry/*.step because nobody has Pollen's CAD. Every number below was
READ OFF Pollen's published mesh
`reference/pollen-microduck-rl/assets/neck_pitch.stl` (metres, decimated)
on 2026-09-02 with `cecad.meshslice` (render sheets in
out/measure/neckgrp/np_slices_{x,y,z}.png + intervals probes quoted per
number) and `cecad.meshfeatures.cylinders`, and the rebuild is graded
against that mesh by `ce-cad/bin/cad-refcheck` (see evidence/).

FRAME — Pollen's mesh frame, kept on purpose: x -17.5..17.5 (the
head-pitch axis runs along x through (0, 0, -28.793)), y -9..9,
z -37.793..-10.1 (the head-yaw axis runs along z through (0, 0)).

WHAT IT IS. A U-bracket between the head-pitch servo and the head-yaw
servo:
  * TWO SIDE PLATES, 3 thick (|x| 14.5..17.5), 18 wide, rounded R9 about
    the pitch axis (0, -28.793), each with the XL330 horn pattern: Ø6
    centre + 4 x Ø2.2 on a Ø12 bolt circle at 0/90/180/270 deg. The
    head-pitch XL330 (carried by the neck plates) sits between them —
    horn on one side, idler on the other.
  * TOP PLATE (z -13 top face) spanning the side plates, carrying on top
    a Ø18 x 1 disc + Ø16 x 1.9 boss (to z -10.1): the head-yaw output
    face. Ø6 centre bore with a Ø7.6 tube under it, 4 x Ø2.2 horn screws
    on the same Ø12 circle, counterbored Ø4.4 from below. The head-yaw
    XL330 (in yaw_roll_motion above) bolts its horn here and the
    yaw_roll_motion body's bearing rides the Ø16 boss.
  * UNDERSIDE: one countersink-shaped clearance cut about the pitch
    axis — a Ø27.586 cylinder for |x| <= 11.5 continuing as a 45 deg
    cone to Ø21.586 at the side-plate faces (|x| = 14.5) — so the
    bracket clears the pitch servo body as it swings. This one cut
    reproduced every underside probe to < 0.02 mm.
  * 45 deg outer chamfers from (|x| 14.5, z -13) to (17.5, -16) joining
    the top plate into the side plates.
"""

import math

# ---- measured off neck_pitch.stl (mm) --------------------------------------
# bbox: x -17.5..17.5, y -9..9, z -37.793..-10.1 (meshslice.load vertices)
X_SIDE_IN, X_SIDE_OUT = 14.5, 17.5   # intervals along x at (y0,z-20): +-14.5..17.5
W2 = 9.0                             # half width: y-extent at (x16,z-20): -9..9
Z_TOP = -13.0                        # plate top: z at (x10,y0): (-15.0, -13.0)
Z_BOSS_FACE = -10.1                  # bbox top; boss d16 len 1.9 centre -11.05
Z_DISC = -12.0                       # disc d18 len 1.0 centre -12.5 (meshfeatures)
PITCH_Z = -28.793                    # pitch axis: hole centres z -34.793/-22.793 +-6
R_END = 9.0                          # side plate bottom round: bbox z min -37.793 = PITCH_Z - 9
SIDE_T = X_SIDE_OUT - X_SIDE_IN      # 3.0: hole len 3.0 (meshfeatures side holes)
# underside countersink about the pitch axis:
R_CUT = 13.793                       # plate underside at y0 is z -15.0 (z at (x10,y0));
                                     #   -28.793 + 13.793 = -15.0; verified at
                                     #   (x-8,y-8) -17.558 and (x0,y+-9) -18.34
X_CYL = 11.5                         # cyl->cone break: x_inner 12.489 at z-16,
                                     #   13.49 at z-17, 14.49 at z-18 -> 45 deg cone
                                     #   from (11.5, R13.793); corner-web probes
                                     #   (x14,y8.5) -21.359 = cone to <0.01 mm
R_CUT_END = R_CUT - (X_SIDE_IN - X_CYL)   # 10.793 at the side-plate face
Z_SLAB_BOT = -23.0                   # below the deepest cut boundary -22.83; the
                                     #   slab bottom is never an exposed face
# chamfer joining plate to side plates (probes: top -13.5 at x15, -14.5 at
# x16, -15.7 at x17.2 -> 45 deg plane (14.5,-13) -> (17.5,-16))
CH_X0, CH_Z0, CH_X1, CH_Z1 = 14.5, -13.0, 17.5, -16.0
# top horn face features (meshfeatures, all residual < 0.001):
DISC_D = 18.0
BOSS_D = 16.0
HORN_HOLE_D = 2.2                    # 4x on Ø12 circle: centres (+-6,0),(0,+-6)
HORN_R = 6.0
BORE_D = 6.0                         # centre bore, len 5.23 -> bottom z -15.33
BORE_BOT = -15.34
TUBE_D = 7.6                         # tube islands y +-(3.0..3.8) at z -15.2
CBORE_D, CBORE_BOT = 4.4, -17.76     # cbores from below: surface -17.75..-13.05
SIDE_HOLE_D = 2.2                    # side plates: 4x Ø2.2 +-6 around Ø6 centre
SIDE_BORE_D = 6.0
MATERIAL = "PLA"


def _side_outline():
    """(y, z) outline of a side plate: rect top at Z_TOP, R9 round bottom
    about (0, PITCH_Z)."""
    pts = [(-W2, Z_TOP), (W2, Z_TOP)]
    n = 24
    for i in range(n + 1):
        a = -math.pi * i / n          # +y round to -y under the bottom
        pts.append((W2 * math.cos(a) * (R_END / W2), PITCH_Z + R_END * math.sin(a)))
    return pts


def build(doc, params=None):
    from cecad.core import Part
    if params:
        raise ValueError("microduck-neck-pitch-bracket takes no build parameters (got %s)" % sorted(params))
    p = Part("microduck-neck-pitch-bracket", material=MATERIAL)
    # side plates
    for x0 in (X_SIDE_IN, -X_SIDE_OUT):
        p.prism(_side_outline(), SIDE_T, at=(x0, 0, 0), axis="x")
    # top slab between them (the countersink cut shapes its underside)
    p.box(2 * X_SIDE_IN, 2 * W2, Z_TOP - Z_SLAB_BOT,
          at=(-X_SIDE_IN, -W2, Z_SLAB_BOT))
    # outer 45 deg chamfers (cut wedges, prism along y; axis "y" takes (z, x))
    for s in (1, -1):
        p.prism([(CH_Z0, s * CH_X0), (CH_Z1, s * CH_X1), (-9.0, s * CH_X1), (-9.0, s * CH_X0)],
                2 * W2 + 1, at=(0, -W2 - 0.5, 0), axis="y", op="cut")
    # underside countersink about the pitch axis: cylinder + two 45 deg cones
    p.cyl(2 * R_CUT, 2 * X_CYL, at=(-X_CYL, 0, PITCH_Z), axis="x", op="cut")
    p.cone(2 * R_CUT, 2 * R_CUT_END, X_SIDE_IN - X_CYL, at=(X_CYL, 0, PITCH_Z), axis="x", op="cut")
    p.cone(2 * R_CUT_END, 2 * R_CUT, X_SIDE_IN - X_CYL, at=(-X_SIDE_IN, 0, PITCH_Z), axis="x", op="cut")
    # centre tube under the bore, disc + boss on top
    p.cyl(TUBE_D, Z_TOP - BORE_BOT + 0.01, at=(0, 0, BORE_BOT), axis="z")
    p.cyl(DISC_D, Z_DISC - Z_TOP + 0.5, at=(0, 0, Z_TOP - 0.5), axis="z")
    p.cyl(BOSS_D, Z_BOSS_FACE - Z_DISC + 0.5, at=(0, 0, Z_DISC - 0.5), axis="z")
    # top horn features: centre bore, 4 x Ø2.2, 4 x Ø4.4 counterbores from below
    p.cyl(BORE_D, Z_BOSS_FACE - BORE_BOT + 1, at=(0, 0, BORE_BOT), axis="z", op="cut")
    for dx, dy in ((HORN_R, 0), (-HORN_R, 0), (0, HORN_R), (0, -HORN_R)):
        p.cyl(HORN_HOLE_D, 4, at=(dx, dy, Z_TOP - 0.1), axis="z", op="cut")
        p.cyl(CBORE_D, Z_TOP - CBORE_BOT, at=(dx, dy, CBORE_BOT), axis="z", op="cut")
    # side plate horn patterns: Ø6 centre + 4 x Ø2.2, through both plates
    p.cyl(SIDE_BORE_D, 2 * X_SIDE_OUT + 2, at=(-X_SIDE_OUT - 1, 0, PITCH_Z), axis="x", op="cut")
    for dy, dz in ((HORN_R, 0), (-HORN_R, 0), (0, HORN_R), (0, -HORN_R)):
        p.cyl(SIDE_HOLE_D, 2 * X_SIDE_OUT + 2, at=(-X_SIDE_OUT - 1, dy, PITCH_Z + dz), axis="x", op="cut")
    # connectors
    p.connector("yaw_horn_top", at=(0.0, 0.0, Z_BOSS_FACE), dir=(0.0, 0.0, 1.0))
    p.connector("pitch_horn_right", at=(X_SIDE_OUT, 0.0, PITCH_Z), dir=(1.0, 0.0, 0.0))
    p.connector("pitch_horn_left", at=(-X_SIDE_OUT, 0.0, PITCH_Z), dir=(-1.0, 0.0, 0.0))
    return p
