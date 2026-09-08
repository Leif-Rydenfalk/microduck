"""part:microduck-banana-pcb-locker — the PCB retaining bar
("banana_pcb_locker" in Pollen's MJCF), rebuilt.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. Parametric —
there is no geometry/*.step because nobody has Pollen's CAD. Every number
below was READ OFF Pollen's published mesh
`reference/pollen-microduck-rl/assets/banana_pcb_locker.stl` (metres,
decimated) on 2026-09-01 with `cad-mjcf sections`, `cad-mjcf probe` and
`cecad.meshfeatures.cylinders`, and the rebuild is graded against that
mesh by `cecad.meshcompare` (see evidence/).

FRAME — Pollen's mesh frame, kept on purpose: Y is the bar's THICKNESS
(y 35.0 .. 36.5, tabs to 32.7), X its LENGTH (-27 .. 27), Z its HEIGHT
(48.99 .. 55.61). The MJCF places it at pos (4, -0.5, -17.5) mm with the
same 90 deg turn about z as trunk_base and power_support, so the three
parts share one frame: this bar's Ø2.17 holes at (±25, 53.6) sit exactly
over the power_support's Ø3.9 screw pins at (±25, 53.6), 0.2 mm off its
pin tops (y 34.8 vs 35.0).

WHAT IT IS. A 1.5 mm bar, 54 long, with a Ø4 eye at each end round an
M2 clearance hole, a 12 mm wide notch (centre x = -4, the same notch the
power_support's head has) that clears a connector, and two 2.5 x 2.3 x 2
tabs under it that key into the power_support's shelf. It clamps the
"banana" PCB against the power support.
"""
import math

# ---- measured off banana_pcb_locker.stl (mm) -------------------------------
Y0, Y1 = 35.0, 36.5                     # bar thickness: probe z=50 x=0 -> y 35.0..36.5
Z_BOT, Z_TOP = 48.987, 55.613           # probe y=35.75 x=-12 -> z 48.987..55.613
HOLE_D = 2.174                          # meshfeatures: two holes Ø2.174, axis y, at (±25, 53.6)
HOLE_X, HOLE_Z = 25.0, 53.6
EYE_R = 2.013                           # x extreme 26.973 at z=54 -> sqrt(1.973^2+0.4^2); top 55.613-53.6
# the lower edge runs flat z=48.987 between x=±23.0, then rises at 47 deg
# (probe: x extreme 23.555 @ z49.5, 25.164 @ z51, 26.236 @ z52 -> dx/dz 1.072)
# to meet the eye tangentially at (26.373, 52.128)
FLAT_HALF = 23.006
SLOPE = 1.072                           # dx per dz
# notch: probe y=35.75 -> gap x -9.99..1.99 (centre -4.0, half-width 5.99), floor z 52.117
# (x=-8..0 -> z max 52.113/52.117); top corners round R2 (x=-10 -> 54.3, -11 -> 55.53,
# -12 -> 55.613, mirrored about x=-4: 2 -> 54.3, 3 -> 55.53); floor corners ~R1 (x=-9 -> 52.203)
NOTCH_XC, NOTCH_HW, NOTCH_FLOOR = -4.0, 5.99, 52.117
NOTCH_R_TOP, NOTCH_R_FLOOR = 2.0, 1.0
# tabs: probe y=34 z=50 -> x 15.667..18.133 (both signs); z=50 x=±17.5 -> y 32.7..36.5;
# y=34 x=±17.5 -> z 49.017..50.983
TAB_X0, TAB_X1 = 15.667, 18.133
TAB_Y0 = 32.7
TAB_Z0, TAB_Z1 = 49.017, 50.983

MATERIAL = "PLA"


def _arc(cx, cz, r, a0, a1, n=10):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cz + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def _outline_xz():
    """(x, z) profile of the bar without the notch, counter-clockwise."""
    # tangent point of the 47 deg lower edge on the right eye
    t = (SLOPE, 1.0)
    L = math.hypot(*t)
    nx, nz = t[1] / L, -t[0] / L          # outward normal (down-right)
    tx, tz = HOLE_X + EYE_R * nx, HOLE_Z + EYE_R * nz
    a_t = math.degrees(math.atan2(tz - HOLE_Z, tx - HOLE_X))   # about -47 deg
    pts = [(-FLAT_HALF, Z_BOT), (FLAT_HALF, Z_BOT), (tx, tz)]
    pts += _arc(HOLE_X, HOLE_Z, EYE_R, a_t, 90, 16)[1:]
    pts += [(-HOLE_X, Z_TOP)]
    pts += _arc(-HOLE_X, HOLE_Z, EYE_R, 90, 180 - a_t, 16)[1:]
    pts += [(-tx, tz)]
    return pts


def _notch_xz():
    """(x, z) polygon of the CUT: the notch with R1 floor fillets and R2
    convex rounds where its walls meet the top edge."""
    xl, xr = NOTCH_XC - NOTCH_HW, NOTCH_XC + NOTCH_HW
    rf, rt, zf, zt = NOTCH_R_FLOOR, NOTCH_R_TOP, NOTCH_FLOOR, Z_TOP
    pts = [(xr, zf + rf)]
    pts += _arc(xr - rf, zf + rf, rf, 0, -90, 6)[1:]        # right floor fillet
    pts += [(xl + rf, zf)]
    pts += _arc(xl + rf, zf + rf, rf, -90, -180, 6)[1:]     # left floor fillet
    pts += [(xl, zt - rt)]
    pts += _arc(xl - rt, zt - rt, rt, 0, 90, 8)[1:]         # left top round
    pts += [(xl - rt, zt + 2), (xr + rt, zt + 2), (xr + rt, zt)]
    pts += _arc(xr + rt, zt - rt, rt, 90, 180, 8)[1:]       # right top round
    return pts


def _zx(pts):
    """prism(axis='y') takes (z, x) pairs."""
    return [(z, x) for x, z in pts]


def build(doc, params=None):
    from cecad.core import Part
    if params:
        raise ValueError("microduck-banana-pcb-locker takes no build parameters (got %s)" % sorted(params))
    p = Part("microduck-banana-pcb-locker", material=MATERIAL)
    p.prism(_zx(_outline_xz()), Y1 - Y0, at=(0, Y0, 0), axis="y")
    p.prism(_zx(_notch_xz()), Y1 - Y0 + 2, at=(0, Y0 - 1, 0), axis="y", op="cut")
    for sx in (-1, 1):
        p.cyl(HOLE_D, 5, at=(sx * HOLE_X, Y0 - 2, HOLE_Z), axis="y", op="cut")
        x0 = min(sx * TAB_X0, sx * TAB_X1)
        p.box(TAB_X1 - TAB_X0, Y0 - TAB_Y0 + 0.01, TAB_Z1 - TAB_Z0, at=(x0, TAB_Y0, TAB_Z0))
    p.clean()
    p.connector("screw_left", at=(-HOLE_X, Y0, HOLE_Z), dir="-y")
    p.connector("screw_right", at=(HOLE_X, Y0, HOLE_Z), dir="-y")
    return p
