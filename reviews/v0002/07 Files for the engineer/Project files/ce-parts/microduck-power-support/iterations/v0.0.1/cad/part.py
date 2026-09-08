"""part:microduck-power-support — the battery cradle half ("power_support"
in Pollen's MJCF), rebuilt.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. Parametric —
there is no geometry/*.step because nobody has Pollen's CAD. Every number
below was READ OFF Pollen's published mesh
`reference/pollen-microduck-rl/assets/power_support.stl` (metres,
decimated) on 2026-09-01 with `cad-mjcf sections --at/--image` (gridded
section pictures), `cad-mjcf probe` (material intervals along a line) and
`cecad.meshfeatures.cylinders` — the first two were added to cecad for
this part — and the rebuild is graded against that mesh by
`cecad.meshcompare` (see evidence/).

FRAME — Pollen's mesh frame, kept on purpose: Y is the plate's THICKNESS
(plate y 25 .. 27, ribs/rails to 35, mounting flanges down to 18), X its
WIDTH (-27.25 .. 27.25), Z its LENGTH (-26.2 .. 57.1). The MJCF places it
at pos (4, 0, -17.521) mm with the same 90 deg turn about z as trunk_base
and banana_pcb_locker, so the three parts share one frame.

WHAT IT IS. A 2 mm plate, 42.8 wide over the battery and 54.5 wide at the
head, lying against the NP-F550 (its 38.4 mm width fits between the two
2 mm rails at x = ±19.4..21.4, whose inward lips at y 31.3..32.8 hold the
cell). Eight 2 mm ribs on the battery face, two stadium bosses with 4 x
Ø1.6 M2 tapping holes each (the battery-contact PCB), a sprung latch
tongue at the bottom with a ramped hook and five grip ridges, a 2 mm
shelf across the head at z 49..51 with two U-notches, two small posts and
two Ø3.9 screw pins (Ø1.55 tapped) at (±25, 53.6) that the
banana_pcb_locker bolts to, and — on the far side — two 1.9 mm flanges at
z 15.3 and z 41.7 with Ø2.5 holes at (±9.5, y 20.5) matching the
trunk_base's Ø2.3 holes at the same x/y in the shared frame.
"""
import math

# ---- plate (y 25..27) — probes at y=26 ------------------------------------
PY0, PY1 = 25.0, 27.0                 # probe z=0 x=0: y 25..27
BODY_HW = 21.383                       # z=-15..26.5: x ±21.383
BODY_Z0 = -22.483                      # x=6..16: z from -22.483
BODY_R = 2.0                           # x extreme 19.946 @ z-22.4, 20.685 @ z-22 -> R2
HEAD_Z0 = 40.317                       # x=21.4..25: z from 40.317
HEAD_HW = 27.233                       # z=45: x ±27.233
HEAD_R = 2.0                           # x=27: z from 41.382; 26.5: 40.771; 26: 40.470 -> R2 (bottom & top)
TOP_Z_AT_0, TOP_SLOPE = 57.111, 0.0524 # top edge z = 57.111 - 0.0524|x|: x=4 -> 56.901, 15 -> 56.325, 25 -> 55.80
# notch: z=54..55 -> gap x -9.983..1.983, floor z 52.117 (x=-4..-7); corners: left
# R2 (x=-10.36 @ z56, -11.35 @ z56.5), right R1.2 (2.098 @ 56, 2.437 @ 56.5, 2.884 @ 56.8);
# floor corners ~R1 (x=1 -> 52.21)
NOTCH_XL, NOTCH_XR, NOTCH_FLOOR = -9.983, 1.983, 52.117
NOTCH_RL, NOTCH_RR, NOTCH_RF = 2.0, 1.2, 1.0
WIN_HW, WIN_Z0, WIN_Z1 = 4.0, 7.35, 12.35      # z=8..12: gap x ±4; x=0..4: gap z 7.35..12.35
SLOT_X0, SLOT_X1 = 17.348, 19.383      # z=-15/-13/23: gap x -19.383..-17.348 (both signs)
SLOT_Z = ((-16.817, -9.783), (19.883, 26.917))   # x=-18.6/-19: gaps in z
# latch tongue: x ±5.017, slits 5.017..5.483 from z -12.917 (x=5.25 -> z from -12.917)
# down through the plate bottom; tongue thin (y 25..26.06: x=0 z=-15 -> 26.059) and
# extends to z -26.186; five R0.4 ridges (y=26.5 -> 0.768 wide bands at z -20.06,
# -18.56, -17.06, -15.56, -14.06; z=-14 -> y to 26.996); hook ramp y = 26.26+1.4(z+26)
# (z-25 -> 27.66, -23 -> 30.46), nose y 31.31 @ z -22.1..-22, top face z -21.85
TONGUE_HW, SLIT_W, SLIT_Z_TOP = 5.017, 0.466, -12.917
TONGUE_T, TONGUE_Z_END = 1.06, -26.186
RIDGE_R, RIDGE_Y, RIDGE_Z = 0.4, 26.6, (-20.06, -18.56, -17.06, -15.56, -14.06)
HOOK_YZ = ((26.0, -26.186), (31.02, -22.6), (31.31, -22.1), (31.31, -21.85), (26.0, -21.85))
# ---- battery face (+y) -----------------------------------------------------
RIB_H = 2.0                            # z=0 x=-14.25: y 25..29
RIB_W = 1.47                           # y=28: 1.466 wide, y=28.9: 1.434 (slight draft)
RIB_X = (2.036, 6.108, 10.18, 14.25)   # y=28 z=0 centres: (1.303+2.768)/2 ... pitch 4.072
RIB_Z = {14.25: (-12.433, 22.533), 10.18: (-12.433, 22.533), 6.108: (-9.433, 22.533), 2.036: (-12.433, 22.533)}
BOSS_R = 1.9                           # y=28 z=9.85: x to -12.474 -> 12.474-10.6; z=-13.95: -5.577 -> 7.45-1.873
BOSS_PAIRS = (((7.45, 7.95), (10.6, 9.85)), ((7.45, -13.95), (10.6, -15.85)))  # meshfeatures Ø1.6 hole centres
PCB_HOLE_D = 1.6                       # meshfeatures: 8 holes Ø1.6 axis y, length 4 (y 25..29)
RAIL_X0, RAIL_X1 = 19.383, 21.383      # z=0 y=25.5: -21.391..-19.374; drafts 0.16 over 10 mm ignored
RAIL_Z0, RAIL_Z1, RAIL_Y1 = -16.75, 26.85, 35.0   # x=-20.4 y=30: z -16.713..26.813; y=34.8: -15.53..25.63 -> R2 top ends
RAIL_END_R = 2.0
LIP_X0, LIP_Y0, LIP_Y1 = 17.487, 31.3, 32.8      # z=23 y=32: x -21.278..-17.487; x=-18.5: y 31.3..32.8
LIP_Z = ((-16.678, -9.922), (20.022, 26.778))     # x=-18.5 y=32
SHELF_Z0, SHELF_Z1, SHELF_HW, SHELF_Y1 = 49.017, 50.983, 22.983, 35.0   # y=28 x=-14.25: z 49.017..50.983; z=50 y=28: x ±22.983
SHELF_END_R = 2.0                      # z=50: x -22.215 @ y34.5, -21.514 @ y34.9 -> R2 centred (±20.98, 33)
U_X, U_W, U_YC = 16.9, 2.9, 31.654     # z=50 y=33: gap -18.324..-15.476; bottom y 30.204 @ x=-16.8 -> R1.45
POST_X0, POST_X1, POST_Z0, POST_Z1 = 11.017, 12.983, 52.817, 55.683   # y=28 z=54; x=-11.7 z 52.817..55.683
PIN_X, PIN_Z, PIN_D, PIN_BORE_D = 25.0, 53.6, 3.9, 1.55   # meshfeatures boss Ø3.875; bore chord 1.53 @ z53.6/54
PIN_Y1 = 34.8                          # z=53.6 x=-26.5: y 25..34.8
LEG_X0, LEG_X1, LEG_Z0 = 24.267, 25.733, 49.617  # z=50 y=28: x -25.733..-24.267; x=-25: z from 49.617
WEB_X0, WEB_Z0, WEB_Z1 = 21.017, 52.867, 54.333  # y=28 z=54: x -24.346..-21.017; x=-22.5: z 52.867..54.333
# ---- mounting flanges (-y) --------------------------------------------------
FL_Y0, FL_YBAR = 18.0, 20.5            # z=42 x=-9.5: y from 18.0; x=0: from 20.5
FL_HW = 12.45                          # y=22 z=42: x ±12.448
FL_LOBE_XI, FL_LOBE_R = 6.5, 1.2       # y=18.5: x 6.739..12.261 -> lobe 6.5..12.45 with R1.2 corners
FL_Z = ((14.33, 16.27), (40.73, 42.67)) # y=22 x=-9.5: z 14.352..16.248 / 40.752..42.648 (y=24: ±0.035 draft)
FL_HOLE_D, FL_HOLE_X, FL_HOLE_Y = 2.5, 9.5, 20.5  # meshfeatures: Ø2.5 axis z at (±9.5, 20.5), z 15.3 / 41.7
GUS_X0, GUS_X1 = 11.5, 12.45           # y=22 z=43: x -12.448..-11.552
GUS_Z = ((12.35, 16.25), (40.75, 44.65)) # y=22 x=-12: z 12.352..16.248 / 40.752..44.648

MATERIAL = "PLA"


def _arc(cx, cy, r, a0, a1, n=10):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def _zx(pts):
    """prism(axis='y') takes (z, x) pairs."""
    return [(z, x) for x, z in pts]


def _top(x):
    return TOP_Z_AT_0 - TOP_SLOPE * abs(x)


def _plate_xz():
    r = BODY_R
    pts = _arc(-BODY_HW + r, BODY_Z0 + r, r, 180, 270, 8)
    pts += _arc(BODY_HW - r, BODY_Z0 + r, r, 270, 360, 8)
    pts += [(BODY_HW, HEAD_Z0), (HEAD_HW - HEAD_R, HEAD_Z0)]
    pts += _arc(HEAD_HW - HEAD_R, HEAD_Z0 + HEAD_R, HEAD_R, 270, 360, 8)[1:]
    cx = HEAD_HW - HEAD_R
    pts += _arc(cx, _top(cx) - HEAD_R, HEAD_R, 0, 90, 8)
    pts += [(0.0, _top(0.0))]
    pts += _arc(-cx, _top(cx) - HEAD_R, HEAD_R, 90, 180, 8)
    pts += _arc(-cx, HEAD_Z0 + HEAD_R, HEAD_R, 180, 270, 8)
    pts += [(-BODY_HW, HEAD_Z0)]
    return pts


def _notch_xz():
    xl, xr, zf, rf = NOTCH_XL, NOTCH_XR, NOTCH_FLOOR, NOTCH_RF
    ztl, ztr = _top(xl - NOTCH_RL), _top(xr + NOTCH_RR)
    pts = [(xr, zf + rf)]
    pts += _arc(xr - rf, zf + rf, rf, 0, -90, 6)[1:]
    pts += [(xl + rf, zf)]
    pts += _arc(xl + rf, zf + rf, rf, -90, -180, 6)[1:]
    pts += [(xl, ztl - NOTCH_RL)]
    pts += _arc(xl - NOTCH_RL, ztl - NOTCH_RL, NOTCH_RL, 0, 90, 8)[1:]
    pts += [(xl - NOTCH_RL, 62), (xr + NOTCH_RR, 62), (xr + NOTCH_RR, ztr)]
    pts += _arc(xr + NOTCH_RR, ztr - NOTCH_RR, NOTCH_RR, 90, 180, 8)[1:]
    return pts


def _stadium_xz(a, b, r, n=12):
    """(x, z) hull of two R circles at a and b."""
    ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    return _arc(b[0], b[1], r, ang - 90, ang + 90, n) + _arc(a[0], a[1], r, ang + 90, ang + 270, n)


def _rail_yz():
    r = RAIL_END_R
    pts = [(PY1 - 0.1, RAIL_Z0), (PY1 - 0.1, RAIL_Z1), (RAIL_Y1 - r, RAIL_Z1)]
    pts += [(RAIL_Y1 - r + r * math.sin(math.radians(a)), RAIL_Z1 - r + r * math.cos(math.radians(a)))
            for a in range(10, 91, 10)]
    pts += [(RAIL_Y1 - r + r * math.sin(math.radians(a)), RAIL_Z0 + r - r * math.cos(math.radians(a)))
            for a in range(90, -1, -10)]
    return pts


def _shelf_xy():
    r = SHELF_END_R
    pts = [(-SHELF_HW, PY1 - 0.1), (SHELF_HW, PY1 - 0.1), (SHELF_HW, SHELF_Y1 - r)]
    pts += _arc(SHELF_HW - r, SHELF_Y1 - r, r, 0, 90, 8)[1:]
    pts += _arc(-SHELF_HW + r, SHELF_Y1 - r, r, 90, 180, 8)
    return pts


def _flange_xy():
    """(x, y) outline of one -y mounting flange: a bar y 20.5..25 across
    x ±12.45 with two lobes to y 18 round the Ø2.5 holes."""
    r = FL_LOBE_R
    pts = [(-FL_HW, PY0 + 0.1), (-FL_HW, FL_Y0 + r)]
    pts += _arc(-FL_HW + r, FL_Y0 + r, r, 180, 270, 6)[1:]
    pts += [(-FL_LOBE_XI - r, FL_Y0)]
    pts += _arc(-FL_LOBE_XI - r, FL_Y0 + r, r, 270, 360, 6)[1:]
    pts += [(-FL_LOBE_XI + 0.8, FL_YBAR), (FL_LOBE_XI - 0.8, FL_YBAR), (FL_LOBE_XI, FL_Y0 + r)]
    pts += _arc(FL_LOBE_XI + r, FL_Y0 + r, r, 180, 270, 6)[1:]
    pts += [(FL_HW - r, FL_Y0)]
    pts += _arc(FL_HW - r, FL_Y0 + r, r, 270, 360, 6)[1:]
    pts += [(FL_HW, PY0 + 0.1)]
    return pts


def build(doc, params=None):
    from cecad.core import Part
    if params:
        raise ValueError("microduck-power-support takes no build parameters (got %s)" % sorted(params))
    p = Part("microduck-power-support", material=MATERIAL)
    # ---- the plate and its cut-outs
    p.prism(_zx(_plate_xz()), PY1 - PY0, at=(0, PY0, 0), axis="y")
    p.prism(_zx(_notch_xz()), 30, at=(0, PY0 - 10, 0), axis="y", op="cut")
    for sx in (-1, 1):
        for z0, z1 in SLOT_Z:
            x0 = min(sx * SLOT_X0, sx * SLOT_X1)
            p.box(SLOT_X1 - SLOT_X0, 6, z1 - z0, at=(x0, PY0 - 2, z0), op="cut")
        x0 = min(sx * TONGUE_HW, sx * (TONGUE_HW + SLIT_W))
        p.box(SLIT_W, 6, SLIT_Z_TOP - BODY_Z0 + 2, at=(x0, PY0 - 2, BODY_Z0 - 2), op="cut")
    # ---- latch tongue: thin it, extend it, ridge it, hook it
    p.box(2 * (TONGUE_HW + SLIT_W), 4, SLIT_Z_TOP - BODY_Z0 + 2,
          at=(-(TONGUE_HW + SLIT_W), PY0 + TONGUE_T, BODY_Z0 - 2), op="cut")
    p.box(2 * TONGUE_HW, TONGUE_T, BODY_Z0 - TONGUE_Z_END + 0.1, at=(-TONGUE_HW, PY0, TONGUE_Z_END))
    for z in RIDGE_Z:
        p.cyl(2 * RIDGE_R, 2 * TONGUE_HW, at=(-TONGUE_HW, RIDGE_Y, z), axis="x")
    p.prism(HOOK_YZ, 2 * TONGUE_HW, at=(-TONGUE_HW, 0, 0), axis="x")
    # ---- battery face: ribs, bosses, rails, lips
    for sx in (-1, 1):
        for xc in RIB_X:
            z0, z1 = RIB_Z[xc]
            p.box(RIB_W, RIB_H + 0.1, z1 - z0, at=(sx * xc - RIB_W / 2, PY1 - 0.1, z0))
        for a, b in BOSS_PAIRS:
            a, b = (sx * a[0], a[1]), (sx * b[0], b[1])
            p.prism(_zx(_stadium_xz(a, b, BOSS_R)), RIB_H + 0.1, at=(0, PY1 - 0.1, 0), axis="y")
        x0 = min(sx * RAIL_X0, sx * RAIL_X1)
        p.prism(_rail_yz(), RAIL_X1 - RAIL_X0, at=(x0, 0, 0), axis="x")
        x0 = min(sx * LIP_X0, sx * (RAIL_X0 + 0.1))
        for z0, z1 in LIP_Z:
            p.box(RAIL_X0 + 0.1 - LIP_X0, LIP_Y1 - LIP_Y0, z1 - z0, at=(x0, LIP_Y0, z0))
    # ---- head: shelf with U-notches, posts, screw pins on legs and webs
    p.prism(_shelf_xy(), SHELF_Z1 - SHELF_Z0, at=(0, 0, SHELF_Z0), axis="z")
    for sx in (-1, 1):
        p.box(U_W, 6, 4, at=(sx * U_X - U_W / 2, U_YC, SHELF_Z0 - 1), op="cut")
        p.cyl(U_W, 4, at=(sx * U_X, U_YC, SHELF_Z0 - 1), axis="z", op="cut")
        x0 = min(sx * POST_X0, sx * POST_X1)
        p.box(POST_X1 - POST_X0, SHELF_Y1 - PY1 + 0.1, POST_Z1 - POST_Z0, at=(x0, PY1 - 0.1, POST_Z0))
        x0 = min(sx * LEG_X0, sx * LEG_X1)
        p.box(LEG_X1 - LEG_X0, PIN_Y1 - PY1 + 0.1, PIN_Z - LEG_Z0, at=(x0, PY1 - 0.1, LEG_Z0))
        x0 = min(sx * WEB_X0, sx * PIN_X)
        p.box(PIN_X - WEB_X0, PIN_Y1 - PY1 + 0.1, WEB_Z1 - WEB_Z0, at=(x0, PY1 - 0.1, WEB_Z0))
        p.cyl(PIN_D, PIN_Y1 - PY1 + 0.1, at=(sx * PIN_X, PY1 - 0.1, PIN_Z), axis="y")
        p.cyl(PIN_BORE_D, PIN_Y1 - PY1 + 1, at=(sx * PIN_X, PY1, PIN_Z), axis="y", op="cut")
    # ---- far side: two mounting flanges with gusset cheeks and Ø2.5 holes
    for z0, z1 in FL_Z:
        p.prism(_flange_xy(), z1 - z0, at=(0, 0, z0), axis="z")
    for z0, z1 in GUS_Z:
        for sx in (-1, 1):
            x0 = min(sx * GUS_X0, sx * GUS_X1)
            p.box(GUS_X1 - GUS_X0, PY0 + 0.1 - FL_YBAR, z1 - z0, at=(x0, FL_YBAR, z0))
    # ---- window and holes last, through everything they cross (r1 cut the
    # window before the ribs and the x=±2 ribs bridged it: 94/30000 samples
    # 1..2.4 mm off; the reference ribs stop at z 7.35 / 12.35)
    p.box(2 * WIN_HW, 30, WIN_Z1 - WIN_Z0, at=(-WIN_HW, PY0 - 10, WIN_Z0), op="cut")
    for sx in (-1, 1):
        for a, b in BOSS_PAIRS:
            for x, z in (a, b):
                p.cyl(PCB_HOLE_D, 10, at=(sx * x, PY0 - 3, z), axis="y", op="cut")
        for z0, z1 in FL_Z:
            p.cyl(FL_HOLE_D, 6, at=(sx * FL_HOLE_X, FL_HOLE_Y, z0 - 2), axis="z", op="cut")
    p.clean()
    p.connector("locker_screw_left", at=(-PIN_X, PIN_Y1, PIN_Z), dir="+y")
    p.connector("locker_screw_right", at=(PIN_X, PIN_Y1, PIN_Z), dir="+y")
    p.connector("trunk_screw_low_left", at=(-FL_HOLE_X, FL_HOLE_Y, FL_Z[0][0]), dir="-z")
    p.connector("trunk_screw_low_right", at=(FL_HOLE_X, FL_HOLE_Y, FL_Z[0][0]), dir="-z")
    return p
