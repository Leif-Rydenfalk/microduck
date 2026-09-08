"""part:microduck-upper-leg-rigidity-plate — the 1 mm thigh side plate, rebuilt.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. Parametric —
nobody has Pollen's CAD. Every number below was READ OFF Pollen's published
mesh `reference/pollen-microduck-rl/assets/upper_leg_rigidity_plate.stl`
(metres, decimated) on 2026-09-01: the x = 43 plane cut was chained into
closed loops with `cecad.meshslice.segments` (out/measure/plate_slices_x.png
is that cut drawn on a 1 mm grid), circle radii were checked point by point
against the loop vertices, and the holes with `cecad.meshfeatures.cylinders`
+ ray probes. Graded by `ce-cad/bin/cad-refcheck` (evidence/).

FRAME — Pollen's mesh frame, kept on purpose: the SAME frame as the left
thigh housing (the MJCF places both with pos (0,0,-42.5) quat
(0.5,-0.5,-0.5,-0.5) in body upper_leg_left). X is the plate's thickness
(42.5 .. 43.5), Y its width (-12 .. 33), Z its length (-11 .. 47.06). The
plate closes the open side of the thigh cup: its R12 bend nests 0.45 mm
inside the housing's R12.5 inner bend, its Ø19 windows sit on the two servo
axes A0 (0,0) and A1 (22,35.777), and its four Ø2.2 holes are exactly over
the housing's four locating pins (same y,z to 0.01 mm) — the screws go
through the plate into the servos, the pins locate the servos from behind.

The MJCF places this mesh once per thigh (mint, #89dad3): qty 2 per robot.
"""
import math

# ---- envelope (bbox, mm) -----------------------------------------------------
X0, T = 42.5, 1.0                     # x 42.5 .. 43.5 (ray probe: (42.5, 43.5) everywhere)

# ---- axes and outline circles ----------------------------------------------
A0 = (0.0, 0.0)                       # hip pitch axis: Ø19 hole centre (meshfeatures)
A1 = (22.0, 35.777)                   # knee axis: Ø19 hole centre (meshfeatures)
R_OUT = 11.0                          # outline arcs about both axes (bbox z -11.0, y 33.0; loop pts to 0.02)
D_WINDOW = 19.0                       # Ø19.0 (meshfeatures; y-ray at z 0: material ends at ±9.5)
R_WEB = 11.5                          # the cut-out windows stop 2 mm outside the Ø19 (loop: z 11.46 at y 0)

# ---- outline pieces (loop vertices at x 43) ---------------------------------
Y_LEFT_TOP = -12.0                    # left edge: (-11, 0) -> (-12.0, 35.06), a 1.6 deg lean
Z_LEFT_TOP = 35.06
BEND_C, R_BEND = (0.0, 35.06), 12.0   # top-left bend (loop pts (-8.62,43.41), (-4.86,46.03) -> 12.00)
Z_TOP0, TOP_SLOPE = 47.06, -0.0127    # top edge z = 47.06 - 0.0127 y (pts (1.92,47.03) (22.14,46.78))
T_A0_END = 24.6                       # circle A0 leaves into the y=10 edge at (10, 4.58)
Y_RIGHT = 10.0                        # straight right edge y = 10 from z 4.58 to 19.0
T_A1_END = 245.9                      # circle A1 ends at (17.48, 25.68) where the web starts
WEB = [(15.98, 25.81), (14.51, 25.47), (13.2, 24.72), (12.18, 23.62), (10.74, 21.29),
       (10.14, 19.84), (Y_RIGHT, 19.0)]   # the concave web between A1's arc and the y=10 edge

# ---- holes and windows ------------------------------------------------------
SCREW_D = 2.2                         # 4 x Ø2.2 (meshfeatures), M2 clearance
SCREWS = [(-0.5, 43.777), (-0.5, 27.777), (-8.0, 22.5), (8.0, 22.5)]
W1 = (-9.5, -4.5, 25.78, 38.78, 1.2)  # rounded rect y0,y1,z0,z1,r (loop bbox; corner pts (-9.5,26.98)/(-8.5,25.78))
W2 = (-8.5, 8.5, 8.0, 19.5, 1.5)      # rect whose bottom is the R_WEB arc about A0 (loop: (8.5,18.0)->(6.04,19.5))
W3 = [(2.53, 44.28), (13.5, 44.28), (13.5, 27.28), (9.33, 27.28)]   # minus the R_WEB disc about A1;
#     left edge through (3.33,42.28) and (8.95,28.22): y = 8.95 - 0.4 (z - 28.22)

MATERIAL = "PLA"


def _arc(c, r, a0, a1, n):
    return [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def _rounded_rect(y0, y1, z0, z1, r, n=6):
    pts = []
    for (cy, cz), a0 in (((y1 - r, z1 - r), 0), ((y0 + r, z1 - r), 90), ((y0 + r, z0 + r), 180), ((y1 - r, z0 + r), 270)):
        pts += _arc((cy, cz), r, a0, a0 + 90, n)
    return pts


def _outline(n=32):
    pts = []
    pts += _arc(A0, R_OUT, T_A0_END, -180.0, n)                      # (10,4.58) round the bottom to (-11,0)
    pts.append((Y_LEFT_TOP, Z_LEFT_TOP))                             # left edge up
    pts += _arc(BEND_C, R_BEND, 180.0, 90.0, n // 2)[1:]             # bend to (0, 47.06)
    pts.append((A1[0], Z_TOP0 + TOP_SLOPE * A1[0]))                  # top edge to above A1
    # clockwise round the OUTSIDE of A1 (90 -> 0 -> -90 -> -114.1): r2 walked
    # it the other way, self-intersected, and the prism lost everything y > 22
    pts += _arc(A1, R_OUT, 90.0, T_A1_END - 360.0, n)[1:]            # round A1 down to the web
    pts += WEB                                                       # concave web to the y=10 edge
    return pts


def build(doc, params=None):
    from cecad.core import Part
    if params:
        raise ValueError("microduck-upper-leg-rigidity-plate takes no build parameters (got %s)" % sorted(params))
    p = Part("microduck-upper-leg-rigidity-plate", material=MATERIAL)
    p.prism(_outline(), T, at=(X0, 0, 0), axis="x")
    for (y, z) in (A0, A1):
        p.cyl(D_WINDOW, T + 2, at=(X0 - 1, y, z), axis="x", op="cut")
    for (y, z) in SCREWS:
        p.cyl(SCREW_D, T + 2, at=(X0 - 1, y, z), axis="x", op="cut")
    p.prism(_rounded_rect(*W1), T + 2, at=(X0 - 1, 0, 0), axis="x", op="cut")
    # W2 and W3 are each a window MINUS the R_WEB disc about its axis (the
    # 2 mm web that stays around the Ø19). The disc is clipped to the window
    # by building the cutter first — a full disc added back would stand 0.5
    # outside the R11 outline (refcheck r1: bbox +0.50 y, +0.72 z).
    for pts, (ay, az) in ((_rounded_rect(*W2), A0), (W3, A1)):
        cutter = Part("cutter")
        cutter.prism(pts, T + 2, at=(X0 - 1, 0, 0), axis="x")
        cutter.cyl(2 * R_WEB, T + 4, at=(X0 - 2, ay, az), axis="x", op="cut")
        p.shape = p.shape.cut(cutter.shape)
    p.clean()
    for i, (y, z) in enumerate(SCREWS):
        p.connector("screw_%d" % (i + 1), at=(X0, y, z), dir="-x")
    p.connector("hip_pitch_window", at=(X0, A0[0], A0[1]), dir="-x")
    p.connector("knee_window", at=(X0, A1[0], A1[1]), dir="-x")
    return p
