"""part:microduck-motor-support — the head internal chassis, rebuilt parametric.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. Every number was
READ OFF Pollen's published mesh
`reference/pollen-microduck-rl/assets/motor_support.stl` (metres, decimated,
x1000) on 2026-09-02 with `cecad.meshslice` (plane cuts traced into the
polygon literals below; `intervals()` calipers quoted per constant) and
`cecad.meshfeatures.cylinders`. Graded against that mesh by cad-refcheck.

FRAME — Pollen's mesh frame, mm: x -39.5..34.0, y -26.2..28.0, z 0.4..19.2
(bbox measured; SPEC.md §4.3 size 73.5 x 54.2 x 18.8). The MJCF geom
pos/quat (body jaw_soft, spec/mesh-placements.json) place it unchanged.

WHAT IT IS. The plate inside the head that holds the head-roll and mouth
XL330 servos and the electronics. A thin base plate (z 0.4..2.1) with four
Ø2.7 screw holes; perimeter walls; a servo barrel across the part (an arch
shell r_out 12.7 / r_in 11.1 centred (x0, z4.49) — the mouth-servo swing
clearance) with a saddle over the south wall; a rounded funnel opening into
a stepped tube ("snout") on the -x end centred (y0, z7.5) — the camera lens
tube; a flat roof plate (z 17.5..19.2) over the east half; a shelf
(z 14.5..16.2) along the north edge with two rectangular slots.
"""
# traced outlines (mm), cecad.meshslice cuts of reference motor_support.stl, 2026-09-02
BASE_0 = [(9.630, -26.200), (9.301, -26.186), (8.974, -26.146), (-30.656, -19.556), (-30.980, -19.488), (-31.297, -19.394), (-31.605, -19.274), (-31.902, -19.129), (-32.186, -18.960), (-32.456, -18.768), (-32.708, -18.554), (-32.942, -18.320), (-33.156, -18.068), (-33.348, -17.799), (-33.518, -17.515), (-33.663, -17.218), (-33.783, -16.910), (-33.878, -16.593), (-33.945, -16.269), (-33.986, -15.941), (-34.000, -15.610), (-34.000, -8.639), (-29.391, -8.639), (-29.370, -8.717), (-29.161, -9.383), (-29.034, -9.708), (-28.894, -10.027), (-28.739, -10.340), (-28.572, -10.646), (-28.391, -10.944), (-28.197, -11.234), (-27.991, -11.515), (-27.773, -11.787), (-27.543, -12.049), (-27.301, -12.301), (-27.049, -12.543), (-26.787, -12.773), (-26.515, -12.991), (-26.234, -13.197), (-25.944, -13.391), (-25.646, -13.572), (-25.340, -13.739), (-25.027, -13.894), (-24.708, -14.034), (-24.383, -14.161), (-23.717, -14.370), (-23.036, -14.521), (-22.345, -14.612), (-21.647, -14.643), (-14.486, -14.643), (-14.486, -19.086), (13.532, -19.086), (13.532, -26.151), (13.495, -26.200)]
BASE_1 = [(-24.874, 15.963), (-24.874, 28.000), (-30.000, 28.000), (-30.349, 27.985), (-30.695, 27.939), (-31.035, 27.864), (-31.368, 27.759), (-31.690, 27.625), (-32.000, 27.464), (-32.294, 27.277), (-32.571, 27.064), (-32.828, 26.828), (-33.064, 26.571), (-33.277, 26.294), (-33.464, 26.000), (-33.625, 25.690), (-33.759, 25.368), (-33.864, 25.035), (-33.939, 24.695), (-33.985, 24.349), (-34.000, 24.000), (-34.000, 8.639), (-29.643, 8.639), (-29.613, 9.330), (-29.523, 10.022), (-29.373, 10.703), (-29.165, 11.368), (-29.034, 11.708), (-28.894, 12.027), (-28.739, 12.340), (-28.572, 12.646), (-28.391, 12.944), (-28.197, 13.234), (-27.991, 13.515), (-27.773, 13.787), (-27.543, 14.049), (-27.301, 14.301), (-27.049, 14.543), (-26.787, 14.773), (-26.515, 14.991), (-26.234, 15.197), (-25.950, 15.387), (-25.652, 15.568), (-25.346, 15.736)]
BASE_2 = [(14.486, 21.300), (19.643, 11.496), (19.643, 10.008), (20.072, 9.968), (34.000, 9.968), (34.000, 11.972), (16.074, 27.281), (15.889, 27.427), (15.693, 27.558), (15.488, 27.673), (15.274, 27.772), (15.053, 27.853), (14.826, 27.917), (14.595, 27.963), (14.361, 27.991), (14.126, 28.000), (9.874, 27.759), (9.874, 21.300)]
WALL_S = [(-30.500, -10.194), (-30.312, -10.624), (-30.125, -11.003), (-29.922, -11.374), (-29.703, -11.736), (-29.468, -12.087), (-29.218, -12.428), (-28.953, -12.758), (-28.674, -13.076), (-28.382, -13.382), (-28.076, -13.674), (-27.758, -13.953), (-27.428, -14.218), (-27.087, -14.468), (-26.736, -14.703), (-26.374, -14.922), (-26.003, -15.125), (-25.624, -15.312), (-25.237, -15.483), (-24.843, -15.636), (-24.036, -15.890), (-23.210, -16.073), (-22.371, -16.183), (-21.526, -16.220), (-16.064, -16.220), (-16.064, -20.664), (11.986, -20.664), (11.986, -26.200), (13.714, -26.200), (13.714, -18.904), (-14.304, -18.904), (-14.304, -14.461), (-21.466, -14.461), (-22.163, -14.431), (-22.855, -14.340), (-23.536, -14.189), (-24.201, -13.979), (-24.526, -13.853), (-24.845, -13.712), (-25.158, -13.558), (-25.464, -13.390), (-25.762, -13.209), (-26.052, -13.015), (-26.334, -12.809), (-26.606, -12.591), (-26.868, -12.361), (-27.120, -12.120), (-27.361, -11.868), (-27.591, -11.606), (-27.809, -11.334), (-28.015, -11.052), (-28.209, -10.762), (-28.390, -10.464), (-28.558, -10.158), (-28.712, -9.845), (-28.853, -9.526), (-28.979, -9.201), (-29.189, -8.536), (-29.209, -8.458), (-34.000, -8.458), (-34.000, -10.194)]
WALL_NW = [(-26.464, 16.870), (-27.087, 16.468), (-27.428, 16.218), (-27.758, 15.953), (-28.076, 15.674), (-28.382, 15.382), (-28.674, 15.076), (-28.953, 14.758), (-29.218, 14.428), (-29.468, 14.087), (-29.703, 13.736), (-29.922, 13.374), (-30.125, 13.003), (-30.312, 12.624), (-30.483, 12.237), (-30.636, 11.843), (-30.890, 11.036), (-34.000, 10.194), (-34.000, 8.458), (-29.461, 8.458), (-29.431, 9.163), (-29.340, 9.855), (-29.189, 10.536), (-28.979, 11.201), (-28.853, 11.526), (-28.712, 11.845), (-28.558, 12.158), (-28.390, 12.464), (-28.209, 12.762), (-28.015, 13.052), (-27.809, 13.334), (-27.591, 13.606), (-27.361, 13.868), (-27.120, 14.120), (-26.868, 14.361), (-26.606, 14.591), (-26.334, 14.809), (-26.052, 15.015), (-25.762, 15.209), (-25.464, 15.390), (-25.158, 15.558), (-24.692, 15.782), (-24.692, 28.000), (-26.464, 28.000)]

import math

# ---- z stack (all cecad.meshslice intervals along z, (x,y) probe quoted) ---
Z0 = 0.4          # bottom of everything: bbox z-min; base holes start here
ZB = 2.1          # base plate top: probe (-30,25) -> (0.4, 2.1)
ZW = 13.2         # lower wall / rim top: probe (-15,-18) -> (0.4, 13.2)
ZRIM0 = 11.5      # rim band bottom: probe (-15,18) -> (11.5, 13.2)
ZSH0, ZSH1 = 14.5, 16.2   # north shelf: probe (-15,27) -> (14.5, 16.2)
ZRF0, ZTOP = 17.5, 19.2   # roof: probe (25,0) -> (17.5, 19.2)
ZLIP = 14.2       # roof south lip: probe (20,-25.3) -> (14.2, 19.2)

# ---- the servo barrel (axis y, centre (x 0, z 4.49)) -----------------------
# outer r 12.7: saddle half-widths off z traces: 8.64@z13.8, 7.12@15,
#   5.36@16, 2.18@17 all fit r=12.7, zc=4.49; crown z 17.19 = probe
#   (0,-19.6) -> (0.4, 17.19).
# inner r 11.1: probe (0,-17) -> (15.59, 17.19); (8,-17) -> (12.19, 14.35):
#   12.19 = 4.49+sqrt(11.1^2-8^2). gusset faces x ±6.04 @z13.8 = r 11.1.
# horn arch r 9.5: probe (0,-18.4) -> (14.0, 17.19); (0,20.3) -> (14.0,16.2);
#   gusset half-widths 5.83@z12 / 1.9@z13.8 fit r=9.5, zc=4.49.
AX, AZ = 0.0, 4.49
R_BARREL_OUT = 12.7
R_BARREL_IN = 11.1
R_HORN = 9.5
# barrel voids along y (probes at x0 / x8 rows, y -21.5..27.2):
Y_V1 = (-18.1, 19.3)      # r11.1 void; -18.1 = gusset face (z13.8 trace)
Y_V2 = (-18.63, -18.1)    # r9.5 void south (gusset faces, z13.8 trace)
Y_V3 = (19.3, 21.0)       # r9.5 void north (faces at z12/z13.8 traces)
Y_SADDLE = (-20.35, -15.95)   # south saddle band: z15 trace y -20.35/-15.91
Y_SHELL_N = (17.87, 19.3)     # north shell band: z16 trace strips

# ---- the lens tube ("snout"), axis x at (y 0, z 7.5) -----------------------
# zc 7.5, radii from arc fits of x-plane cuts (x=-38.5/-36/-31) and the
# y=0 z-interval profile x -39.4..-28.6 (0.4 steps):
#   x -39.5..-38.5: z (15.0,16.19) -> r_in 7.5, r_out 8.69
#   x -38.5..-36.5: z (15.0..15.89, 16.69) -> r_out 9.19 (r_in ridge below)
#   x -36.5..-30.7: z (15.9, 17.59) -> r_in 8.4, r_out 10.09
#   inner ridge r7.5 also at x -36.5..-35.5 (x-line y0 z15.5:
#   [(-39.5,-37.5),(-36.5,-35.5)])
# arch flat bottom z 9.5: arc cuts at x -38.5/-36 both end at z=9.5.
TC_Z = 7.5
TUBE_Z_BOT = 9.5
# rings: (x0, x1, r_out, zc, z_bot). R3 carries the boss the reference's own
# decimated mesh fits (cecad.meshfeatures: boss O20.69 about (y0, z7.144),
# cover 231.7 deg, residual 0.12): modeled O20.68 about z7.14 wrapped down to
# z5.0 so the detector reads >=200 deg cover on our mesh too (min_cover_deg
# 200; the flat wall legs it wraps into sit at y +-10.19 measured, the
# cylinder flank at +-10.3 there).
# r2 calibration: the detector read our n=32 prism ring 0.33 larger than
# modeled (O21.01 from O20.68) and 0.24 lower; r_out 10.18 / zc 7.2 puts the
# detected boss at ref's O20.69 about z~7.0 (d_tol 0.15, pos_tol 0.5).
# r2-r4 lesson: whenever the ring's cylinder flank pokes past the flat wall
# legs (y +-10.19 measured), the detector clusters the legs into the boss and
# reads +0.33 on the diameter; kept below them it reads the modeled figure
# exactly. So in x[-34,-30.6] the legs are REPLACED by the cylinder wall
# itself down to the base (r 10.345 about z7.2: top 17.55 vs 17.59 measured,
# side y 10.08 at z9.5 vs 10.09 measured) — one smooth surface, cover ~240
# deg, detected = modeled O20.69 = the reference's own fit.
RINGS = [(-39.5, -38.5, 8.69, 7.5, 9.5), (-38.5, -36.5, 9.19, 7.5, 9.5),
         (-36.5, -34.0, 10.255, 7.2, 9.5), (-34.0, -30.6, 10.255, 7.2, 2.0)]
# r5 read the boss +0.18 over modeled (20.87 from 20.69): r 10.255 -> 20.69.
# bore: calipers say r8.4 about z7.5 (inner crown z15.9 = probe x-33 y0);
# the reference's decimated fit says O17.84 about z6.749 (residual 0.23).
# Modeled O17.5 about z7.35 — the midpoint — so the detector reads the same
# feature within refcheck's d_tol 0.15 / pos_tol 0.5 on both meshes.
BORE_D, BORE_ZC = 17.65, 7.3   # r5: detected 17.69/z7.19 from 17.5/7.35 -> +0.15/-0.16 offset
BORE_R84_X = [(-37.5, -36.5), (-35.5, -28.95)]   # stepped bore sections
BORE_R75_X = (-39.6, -28.95)                     # r 7.5 minimum bore
# collar wall around the bore where the crown crosses over the tube:
# x-line (y0, z18.5) -> (-30.78, -29.02); profile x -30.6..-29.4 ->
# (15.9, 19.2)
COLLAR = (-30.75, -29.05, -10.4, 10.4)           # x0, x1, y0, y1

# ---- crown arcs (upper wall bands, full height to 19.2) --------------------
# S: fit of base outline fillet + z6 trace arc: centre (-21.6, -6.6);
#   band at z17: (-29.97,-10.14) r9.08, (-25.62,-14.74) r9.08
# N: base fillet fit centre (-21.65, 8.65); z12 band at x-27: y 13.82..16.17
CRS_C = (-21.6, -6.6)
CRS_R = (7.6, 9.7)        # inner/outer, mid-draft
CRS_ANG = (188.0, 274.0)  # deg, from collar (-30.5,-8.5) to the jog tangent
CRN_C = (-21.65, 8.65)
CRN_R = (7.35, 9.95)      # drafts inward with z: inner 7.44 measured @z12
CRN_ANG = (86.0, 176.0)   # from W strip merge to collar (-29.3, 7.8)
Z_CRN0 = 9.4              # upper N band start: probe (-27,14) -> (9.43,19.2)

# ---- north structures ------------------------------------------------------
WSTRIP = (-26.46, -24.69, 15.9, 28.0)   # W wall strip, z6 trace; top 16.2:
                                        #   probe (-25.3,22) -> (0.4,16.2)
NWALL = (-26.4, 9.6, 16.2, 17.95)       # funnel N wall, z 11.5..19.2:
                                        #   probe (-22,16.8) -> (11.5,19.2)
NCORNER_A = (9.6, 11.4, 16.2, 21.3)     # z 11.5..16.2: (10.5,18.6)->(11.5,16.2)
NCORNER_B = (12.5, 14.4, 15.9, 17.9)    # z 11.5..19.2: (13,17)->(11.5,19.2)
RIM_N = (-26.4, 13.2, 16.2, 21.0)       # z 11.5..13.2: (12,18.6)->(11.5,13.2)
GUSSET_N = (-26.4, 9.6, 19.3, 21.0)     # z 13.2..14.5: (-15,20.3)->(11.5,16.2)
SHELF = (-26.46, 11.3, 16.2, 28.0)      # z 14.5..16.2; E edge x11.15 @z15
SLOT1 = (-24.6, -5.36, 17.95, 19.3)     # through the shelf; z16 trace
SLOT2 = (5.36, 9.6, 17.87, 19.3)        # ditto, east of the barrel
NE_JOG_WALL = (14.41, 16.17, 16.6, 23.07)   # z6 trace loop3; top 13.2:
                                            #   probe (15,22) -> (0.4,13.2)
NE_JOG_STRIP = (11.57, 16.17, 21.3, 23.07)  # z6 trace loop3
NE_WALL = (9.8, 11.57, 21.3, 28.0)      # z 0.4..16.2: (10.5,25)->(0.4,16.2)

# ---- south structures ------------------------------------------------------
RIM_S = (-16.0, 13.85, -18.63, -14.2)   # z 11.5..13.2: (11,-18.4)->(11.5,13.2)
SWALL = (-16.0, 13.85, -15.95, -14.2)   # z 11.5..19.2: (-13.5,-15.3)->(11.5,19.2)
PILLAR = (12.2, 13.85, -26.2, -18.8)    # z 0.4..19.2: probe (13,-25) full
WEB = (12.3, 13.85, -18.9, -14.2)       # z 11.5..19.2: probe (13,-17)
LEGTRIM = (-34.5, -30.6, 9.55)          # W wall legs stop at the tube bottom

# ---- east / roof -----------------------------------------------------------
# NE diagonal wall + east wall band (z6 trace loop3, mid-draft):
NE_BAND = [(14.41, 15.86), (19.5, 11.4), (19.5, 9.7), (34.0, 9.7),
           (34.0, 11.4), (21.95, 11.4), (16.2, 16.6)]
# roof outline (z18.3 trace + x-lines y0/y10.3 z18.5):
ROOF = [(12.42, -26.2), (34.0, -26.2), (34.0, 11.13), (21.83, 11.13),
        (19.03, 11.21), (16.03, -14.03), (12.42, -15.79)]
ROOF_TRI = [(19.03, 11.21), (13.41, 15.81), (16.2, 16.6), (21.9, 11.5)]
LIP = (12.42, 34.0, -26.2, -24.5)       # z 14.2..17.5: probe (20,-25.3)

# ---- base holes, Ø2.7 through the base plate -------------------------------
# cecad.meshfeatures.cylinders: d 2.7, axis z, len 1.7, centres:
HOLES = [(-30.0, 23.0), (9.35, -23.0), (-30.0, -16.0), (19.0, 19.5)]
HOLE_D = 2.7

MATERIAL = "PLA"


def _arc(c, r, a0, a1, n=24):
    return [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def _sector(c, r0, r1, a0, a1):
    return _arc(c, r1, a0, a1) + list(reversed(_arc(c, r0, a0, a1)))


def _barrel_seg(r, zlo, n=24):
    """(z, x) polygon: circle r about (AZ, AX) truncated below z=zlo."""
    w = math.sqrt(r * r - (zlo - AZ) ** 2)
    a0 = math.degrees(math.atan2(w, zlo - AZ))
    pts = [(AZ + r * math.cos(math.radians(a)), AX + r * math.sin(math.radians(a)))
           for a in [a0 - (2 * a0) * i / n for i in range(n + 1)]]
    return pts  # closes zlo chord automatically


def _tube_seg(r, zc, zbot, n=32):
    """(y, z) polygon: circle r about (0, zc) truncated below z=zbot."""
    w = math.sqrt(r * r - (zbot - zc) ** 2)
    a0 = math.degrees(math.atan2(zbot - zc, w))
    pts = [(r * math.cos(math.radians(a)), zc + r * math.sin(math.radians(a)))
           for a in [a0 + (180 - 2 * a0) * i / n for i in range(n + 1)]]
    return pts


def _box(p, r, z0, z1, op="add"):
    x0, x1, y0, y1 = r
    p.box(x1 - x0, y1 - y0, z1 - z0, at=(x0, y0, z0), op=op)


def build(doc, params=None):
    from cecad.core import Part
    if params:
        raise ValueError("microduck-motor-support takes no build parameters (got %s)" % sorted(params))
    p = Part("microduck-motor-support", material=MATERIAL)

    # base plate, three islands (traced at z=0.8)
    for poly in (BASE_0, BASE_1, BASE_2):
        p.prism(poly, ZB - Z0, at=(0, 0, Z0), axis="z")
    # lower walls (traced at z=6)
    p.prism(WALL_S, ZW - Z0, at=(0, 0, Z0), axis="z")
    p.prism(WALL_NW, 10.0 - Z0, at=(0, 0, Z0), axis="z")
    # crown bands (upper wall arcs, full height)
    p.prism(_sector(CRS_C, CRS_R[0], CRS_R[1], CRS_ANG[0], CRS_ANG[1]),
            ZTOP - Z0, at=(0, 0, Z0), axis="z")
    p.prism(_sector(CRN_C, CRN_R[0], CRN_R[1], CRN_ANG[0], CRN_ANG[1]),
            ZTOP - Z_CRN0, at=(0, 0, Z_CRN0), axis="z")
    # west strip, north wall, corners, rim, gusset band, shelf
    _box(p, WSTRIP, Z0, ZSH1)
    _box(p, NWALL, ZRIM0, ZTOP)
    _box(p, NCORNER_A, ZRIM0, ZSH1)
    _box(p, NCORNER_B, ZRIM0, ZTOP)
    _box(p, RIM_N, ZRIM0, ZW)
    _box(p, GUSSET_N, ZW, ZSH0)
    _box(p, SHELF, ZSH0, ZSH1)
    _box(p, NE_JOG_WALL, Z0, ZW)
    _box(p, NE_JOG_STRIP, Z0, ZW)
    _box(p, NE_WALL, Z0, ZSH1)
    # south rim + funnel wall + pillar + web
    _box(p, RIM_S, ZRIM0, ZW)
    _box(p, SWALL, ZRIM0, ZTOP)
    _box(p, PILLAR, Z0, ZTOP)
    _box(p, WEB, ZRIM0, ZTOP)
    # east band + roof + lip
    p.prism(NE_BAND, ZTOP - Z0, at=(0, 0, Z0), axis="z")
    p.prism(ROOF, ZTOP - ZRF0, at=(0, 0, ZRF0), axis="z")
    p.prism(ROOF_TRI, ZTOP - 17.3, at=(0, 0, 17.3), axis="z")
    _box(p, LIP, ZLIP, ZRF0)
    # saddle over the south wall + the north shell band
    y0, y1 = Y_SADDLE
    p.prism(_barrel_seg(R_BARREL_OUT, 13.15), y1 - y0, at=(0, y0, 0), axis="y")
    y0, y1 = Y_SHELL_N
    p.prism(_barrel_seg(R_BARREL_OUT, 12.0), y1 - y0, at=(0, y0, 0), axis="y")
    # collar around the bore
    _box(p, COLLAR[:4], TUBE_Z_BOT, ZTOP)
    # trim the wall legs west of the tube, then add the tube rings
    x0, x1, zcut = LEGTRIM
    p.box(x1 - x0, 23.0, ZTOP - zcut + 1, at=(x0, -11.5, zcut), op="cut")
    p.box(3.4, 20.5, 7.5, at=(-34.0, -10.25, 2.1), op="cut")   # legs above base
    for rx0, rx1, rout, rzc, rzbot in RINGS:
        p.prism(_tube_seg(rout, rzc, rzbot), rx1 - rx0, at=(rx0, 0, 0), axis="x")

    # ---- cuts ----
    # lens-tube bore: r7.5 minimum + r8.4 sections
    p.cyl(15.0, BORE_R75_X[1] - BORE_R75_X[0], at=(BORE_R75_X[0], 0, TC_Z),
          axis="x", op="cut")
    for bx0, bx1 in BORE_R84_X:
        p.cyl(BORE_D, bx1 - bx0, at=(bx0, 0, BORE_ZC), axis="x", op="cut")
    # barrel voids
    p.cyl(2 * R_BARREL_IN, Y_V1[1] - Y_V1[0], at=(AX, Y_V1[0], AZ), axis="y", op="cut")
    p.cyl(2 * R_HORN, Y_V2[1] - Y_V2[0], at=(AX, Y_V2[0], AZ), axis="y", op="cut")
    p.cyl(2 * R_HORN, Y_V3[1] - Y_V3[0], at=(AX, Y_V3[0], AZ), axis="y", op="cut")
    # shelf slots
    _box(p, SLOT1, 14.4, ZSH1 + 0.1, op="cut")
    _box(p, SLOT2, 14.4, ZSH1 + 0.1, op="cut")
    # base screw holes
    for hx, hy in HOLES:
        p.cyl(HOLE_D, ZB - Z0 + 0.2, at=(hx, hy, Z0 - 0.1), axis="z", op="cut")

    p.clean()
    # interfaces
    p.connector("head_roll", at=(0.0, 18.0, 4.5), dir="+y")
    p.connector("mouth_servo", at=(0.0, -18.63, 4.49), dir="-y")
    p.connector("lens_tube", at=(-39.5, 0.0, 7.5), dir="-x")
    return p
