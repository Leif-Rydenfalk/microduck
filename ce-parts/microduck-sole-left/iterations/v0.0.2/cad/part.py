"""part:microduck-sole-left — the left TPU sole ("sole_left" in Pollen's MJCF), rebuilt.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. Parametric, and
INDEPENDENTLY AUTHORED: no vertex, triangle or sampled surface of Pollen's
mesh is carried in this file. Every number below is a DIMENSION — a plane
slope, a fillet radius, a wall face, a floor thickness — established by
caliper measurement (cecad.meshslice.intervals / .segments probes, scripts
and raw output in out/measure/foot/) of Pollen's published visual mesh, and
then FITTED to a named analytic feature whose residual is quoted beside it.
The shape is built the way a designer builds it: a plan outline, a sloping
floor plane, four edge fillets, a shelled socket. The rebuild is graded
against reference/pollen-microduck-rl/assets/sole_left.stl by `cad-refcheck`
(evidence/) — grading against a published artifact, not copying it.

HISTORY (2026-09-05, own-the-geometry lane). v0.0.2 as first written drove
the outer floor from a 27 x 31 = 837-number height table of
`meshslice.intervals` probes lifted off sole_left.stl. That graded 0.05 mm
p95 but it is a RESAMPLING of Pollen's surface, not an authored one, and a
licence position cannot rest on it. The table is gone. The surface it
described is now four fitted numbers (out/own/floor-fit.json):

    floor plane   z = 0.085578*x - 34.36817     36 probe cells, max resid 0.0295 mm
    heel fillet   R 7.850 at x = 29.445         30 probe cells, rms 0.043 mm
    toe fillet    R 6.430 at x = 70.555         27 probe cells, rms 0.036 mm
    side fillets  R 7.920 at y = -12.000        44 probe cells, rms 0.099 mm
                  R 8.320 at y =  42.180        40 probe cells, rms 0.083 mm

FRAME — Pollen's mesh frame, kept on purpose: x runs heel (30) to toe (70),
y across the foot (-12..42), z up (ground at z ~ -31.25). The MJCF geom
pos (-22, 6.223, -64.7) / quat (0.5,-0.5,-0.5,-0.5) places it with no
re-derivation. sole_right.stl IS this mesh mirrored about x = 0 (point-to-
triangle p95 0.002 mm, max 0.008 mm — out/measure/foot/measure2.py), so the
right sole is HAND = -1.

WHAT IT IS. A 41.1 x 54 x 12.9 mm boot-shaped shell, 2.0 mm floor and
~1.6-2.1 mm walls, open at the top rim (z -18.342). The cavity is a
zero-clearance socket for the foot cap's lower body (foot outer
x 31.6..68.4 / y -9.9..39.9 = this cavity, measured equal on both meshes);
the foot's rib bottoms sit exactly on the cavity floor (rib bottoms =
outer floor + 2.000 mm, five stations checked, max deviation 0.005 mm).
"""
import math

HAND = 1        # +1 left (sole_left.stl), -1 right (sole_right.stl = mirror about x=0, p95 0.002 mm)

# ---- envelope, measured (mm) ----------------------------------------------
Z_RIM = -18.342                 # top rim plane (every rim probe: intervals end -18.342)
Z_BOT = -34.0                   # below everything; the floor plane cut owns the bottom
Y0, Y1 = -12.0, 42.0            # outer y faces, vertical (y extents constant -12/42 for z -22..-18.3)
# outer x faces vs z (E profile, probe_sole2.txt): heel leans 0.106 mm/mm, toe bulges to 70.542 at z -22
LOFT_XS = [                     # (z, x_heel, x_toe) sections; the section is constant below z -24
    (Z_BOT,  29.473, 70.542),
    (-24.0,  29.473, 70.542),   # x_heel min 29.473 measured at z -24
    (-22.0,  29.666, 70.542),   # x_toe max 70.542 measured at z -22
    (-20.5,  29.836, 70.436),
    (-19.0,  30.006, 70.249),
    (Z_RIM,  30.074, 70.174),   # rim ring outer extents (segments at z -18.40)
]
X0, X1 = LOFT_XS[0][1], LOFT_XS[0][2]   # the widest plan, constant below z -24
R_BACK, R_FRONT = 5.5, 7.0      # outer plan corner radii (circle fits at z -19: back R 5.514/5.514, front R 7.016/7.017)

# ---- cavity: vertical walls, zero-clearance socket for the foot's lower body
CAV_X0, CAV_X1 = 31.6, 68.4     # inner x faces (A probes, constant at every z)
CAV_Y0, CAV_Y1 = -9.9, 39.9     # inner y faces (P/Q probes, constant)
R_CAV_BACK, R_CAV_FRONT = 3.4, 4.9   # inner corner fits at z -19: back R 3.392/3.393 c (65,36.5); front R 4.888/4.896 c (36.5,-5)
FLOOR_T = 2.0                   # floor thickness, vertical (C grid: every interval 2.000 +- 0.005)

# ---- the outer floor, AUTHORED (out/own/floor-fit.json, 2026-09-05) --------
FLOOR_M, FLOOR_C = 0.085578, -34.36817   # sloping ground plane, max resid 0.0295 mm over 36 probe cells
R_FIL_HEEL = 7.85               # heel roll-up, fit edge x 29.445, rms 0.043 mm
R_FIL_TOE = 6.43                # toe roll-up,  fit edge x 70.555, rms 0.036 mm
R_FIL_SIDE = 8.0                # side roll-ups, fits 7.920 (y -12.000) / 8.320 (y 42.180), rms 0.099 / 0.083 mm

MATERIAL = "TPU"    # SPEC.md: soles + jaw_soft + soft_mouth_top print in TPU (mint #89dad3)


def _rounded_rect(x0, x1, y0, y1, r_front, r_back, n=10):
    """(x, y) polygon, CCW, back corners (y1 side) r_back, front r_front."""
    pts = []
    corners = [
        ((x1 - r_back, y1 - r_back), 0, r_back),
        ((x0 + r_back, y1 - r_back), 90, r_back),
        ((x0 + r_front, y0 + r_front), 180, r_front),
        ((x1 - r_front, y0 + r_front), 270, r_front),
    ]
    for (cx, cy), a0, r in corners:
        for i in range(n + 1):
            a = math.radians(a0 + 90.0 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def _hand_xy(pts):
    """Mirror an (x, y) polygon about x=0 for the right sole, keeping winding."""
    if HAND > 0:
        return pts
    return [(-x, y) for x, y in reversed(pts)]


def _floor_z(x):
    """The authored ground plane at x (mm), in the LEFT frame."""
    return FLOOR_M * x + FLOOR_C


def _base_solid(name, lift=0.0):
    """The sole's outer body BELOW the rim, built the way it is designed:
    an arc-exact rounded-rect plan, cut off by the fitted ground plane, and
    the resulting bottom loop rolled over with the fitted fillet radii.
    `lift` raises the floor plane — FLOOR_T gives the cavity floor, which
    every C-grid probe found parallel to the outer floor at 2.000 mm.

    Arc-exact matters: a polygonised corner cannot be filleted (the kernel
    refuses 40 sub-millimetre edges at R 7.9), so the plan is a union of
    three boxes and four corner cylinders, and the bottom loop comes out as
    4 lines + 4 arcs — the loop a designer would select in any CAD system.
    """
    from cecad.core import Part
    p = Part(name, material=MATERIAL)
    h = Z_RIM - Z_BOT
    x0, x1 = (X0, X1) if HAND > 0 else (-X1, -X0)
    rf, rb = R_FRONT, R_BACK
    p.box(x1 - x0, (Y1 - rb) - (Y0 + rf), h, at=(x0, Y0 + rf, Z_BOT))
    p.box((x1 - rf) - (x0 + rf), rf, h, at=(x0 + rf, Y0, Z_BOT))
    p.box((x1 - rb) - (x0 + rb), rb, h, at=(x0 + rb, Y1 - rb, Z_BOT))
    for cx, cy, r in ((x0 + rf, Y0 + rf, rf), (x1 - rf, Y0 + rf, rf),
                      (x0 + rb, Y1 - rb, rb), (x1 - rb, Y1 - rb, rb)):
        p.cyl(2 * r, h, at=(cx, cy, Z_BOT))
    p.clean()

    # the sloping ground plane (prism along y takes (z, x))
    xa, xb = 10.0, 90.0
    za, zb = _floor_z(xa) + lift, _floor_z(xb) + lift
    sgn = 1 if HAND > 0 else -1
    p.prism([(za, sgn * xa), (zb, sgn * xb), (Z_BOT - 10, sgn * xb), (Z_BOT - 10, sgn * xa)],
            (Y1 - Y0) + 4, at=(0, Y0 - 2, 0), axis="y", op="cut")

    def on_floor(e, tol=0.05):
        return all(abs(v.Point.z - (_floor_z(HAND * v.Point.x) + lift)) <= tol
                   for v in e.Vertexes)

    def is_toe(e):
        return on_floor(e) and all(abs(HAND * v.Point.x - X1) < 0.5 for v in e.Vertexes)

    p.fillet(R_FIL_TOE, where=is_toe)
    p.fillet(R_FIL_SIDE, where=lambda e: on_floor(e) and not is_toe(e))
    return p


def _skin_solid(name):
    """The tapered outer skin, lofted through the measured wall sections."""
    from cecad.core import Part
    p = Part(name, material=MATERIAL)
    sections = []
    for z, xh, xt in LOFT_XS:
        sections.append((_hand_xy(_rounded_rect(xh, xt, Y0, Y1, R_FRONT, R_BACK, n=40)), z))
    p.loft(sections, axis="z", smooth=False, ruled=True)
    return p


def build(doc, params=None):
    from cecad.core import Part
    if params:
        raise ValueError("microduck-sole-left takes no build parameters (got %s)" % sorted(params))
    name = "microduck-sole-left" if HAND > 0 else "microduck-sole-right"
    p = _skin_solid(name)
    p.merge(_base_solid("floor", 0.0), "common")     # the rolled-over ground face

    # the socket: the cavity column, floored by the same authored surface
    # raised by the measured 2.000 mm floor thickness.
    cav = Part("cavity", material=MATERIAL)
    plan = _hand_xy(_rounded_rect(CAV_X0, CAV_X1, CAV_Y0, CAV_Y1, R_CAV_FRONT, R_CAV_BACK, n=40))
    cav.prism(plan, Z_RIM - Z_BOT, at=(0, 0, Z_BOT), axis="z")
    cav.merge(_base_solid("floor_lift", FLOOR_T), "common")
    p.merge(cav, "cut")
    return p
