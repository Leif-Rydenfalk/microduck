"""part:microduck-foot-left — the left foot cap ("foot_left" in Pollen's MJCF), rebuilt.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. Parametric —
nobody has Pollen's CAD. Every number below was READ OFF Pollen's published
mesh `reference/pollen-microduck-rl/assets/foot_left.stl` (metres, decimated)
on 2026-09-02 with `cecad.meshslice.intervals` / `.segments` /
`cecad.meshfeatures.cylinders` (probe scripts and raw outputs in
out/measure/foot/probe_foot*.txt, floor_table.txt), and the rebuild is graded
against that mesh by `cad-refcheck` (evidence/).

FRAME — Pollen's mesh frame, kept on purpose: x heel (30) to toe (70), y
across the foot (-12..42), z up. bbox measured x 30.081..70.166,
y -12.000..42.000, z -29.251..-12.342. The MJCF geom pos (-22, 6.223, -64.7)
/ quat (0.5,-0.5,-0.5,-0.5) places it with no re-derivation — the same body
and transform as ankle_left and sole_left, so the ankle's numbers line up
1:1 in this frame. foot_right.stl IS this mesh mirrored about x = 0
(point-to-triangle p95 0.000 mm, max 0.005 mm — out/measure/foot/measure2.py),
so the right foot is HAND = -1.

WHAT IT IS. The yellow 40.1 x 54 x 16.9 printed cap between the ankle and
the TPU sole:
- LOWER BODY x 31.6..68.4 / y -9.9..39.9 — a perimeter wall + a comb of 10
  ribs (pitch 3.500, thickness 1.750, y 1.288..34.538) whose bottoms follow
  the sole's cavity floor exactly (rib bottoms = sole outer floor + 2.000 mm,
  5 stations checked, max dev 0.005): the sole closes this comb from below.
- A CRADLE for the ankle: the ledges (x 32.9..34.15 / 65.85..67.1) carry an
  R16.3 cylindrical seat about the ankle axis (y 22, z -6.223) — the exact
  radius of the ankle's under-hull (ankle part.py HULL_R 16.3, hull bottom
  z -22.523 = seat bottom, measured equal); the rib tops in the centre band
  y 12.9..31.1 are relieved to R16.5 (0.2 clearance, the slot the clip-on
  roller runs in).
- A FLANGE z -18.342..-13.342 that overhangs the sole rim: side faces
  drafted 0.1134 mm/mm, front/back faces rolling over (loft sections below,
  all from the T-probe table), corners R5.5 back / R7.0 front.
- TWO SNAP FINGERS x 45..55 (front at y ~0, back at y ~37) rising to
  z -12.342 with 1.0 mm barbs facing each other across the slot — the
  clip that holds the roller axle down in the cradle.
- TWO POCKETS x 34.0..39.2 / 60.8..66.0, y 31.563..35.763 — through sockets
  for the ankle's two +y blocks (ankle BLOCK_X 34.1..39.1 / 60.9..65.9,
  block bottom -21.342: 0.1 mm fit).
- ONE M2 THREAD-FORMING PILOT Ø1.6 x 5.5 at (50, 4.502), Ø3.0 x 0.5 relief
  on top — under the ankle's vertical foot screw (ankle SCREW at
  (50.0, 4.502) Ø2.2, same axis to the micron).
"""
import math

HAND = 1        # +1 left (foot_left.stl), -1 right (foot_right.stl = mirror about x=0, p95 0.000 mm)

# ---- levels (mm), each seen in dozens of intervals probes ------------------
Z_BASE = -18.342      # flange base = sole rim plane
Z_STEP = -15.842      # step deck: wall tops, ledge tops (outside the cradle), boss top
Z_DECK = -13.342      # front deck top / ridge A top
Z_TAB = -12.342       # snap-finger tab tops (bbox z max)
Z_LOW = -33.0         # below everything; the floor cut owns the bottom

# ---- lower body plan -------------------------------------------------------
LB_X0, LB_X1 = 31.6, 68.4       # outer faces (= the sole cavity, zero clearance)
LB_Y0, LB_Y1 = -9.9, 39.9
R_LB_BACK, R_LB_FRONT = 3.45, 4.89   # corner fits at z -19.5: back 3.453/3.457, front 4.894/4.893
WALL_T = 1.3                    # side wall x 31.6..32.9 (Y probes at z -20/-21)
LEDGE_X = 34.15                 # ledge inner face (A probes: 34.132 at z-22, 34.158 at z-25)
FRONT_WALL_Y1 = -7.351          # front wall inner face (R probes at z-24)
BACK_WALL_Y0 = 37.351           # back wall inner face below z -21.342 (R probes)
BACK_REBATE_Y0 = 39.163         # back wall face above -21.342 mid-span (U/V probes)

# ---- ribs ------------------------------------------------------------------
RIB_Y0, RIB_PITCH, RIB_T, N_RIB = 1.288, 3.5, 1.75, 10   # y probes at z-24/-26/-27: [1.288,3.038]..[32.788,34.538]
FRONT_RIB_YS = ((-5.712, -3.962), (-2.212, -0.462))       # two short front ribs (R probes x38/x62)
FRONT_RIB_XIN = 41.5                                       # they span wall..41.5 and 58.5..wall (Kx y-3.5)
FRONT_BLOCK_X = 34.106                                     # front side blocks x 31.6..34.106 / 65.894..68.4 (Kx z-19)

# ---- cradle ----------------------------------------------------------------
AXIS_Y, AXIS_Z = 22.0, -6.223   # the ankle axis (same numbers as ankle part.py YC, ZA)
CRADLE_R = 16.3                 # ledge seat radius: seat bottom -22.523 at y22 (= AXIS_Z - R), -21.363 at y16/28, -17.236 at y10/34 — all R16.3
RELIEF_R = 16.5                 # rib-top relief: -21.574 at y16 (R16.5 gives -21.59); rib truncation at z-20 lands y12.996 (R16.5: 12.92)
RELIEF_Y0, RELIEF_Y1 = 12.9, 31.1   # relief band (outside it rib tops measure R16.3: -17.236 at y10/34)

# ---- flange loft (T-probe table: y extents vs z at x=50; x faces drafted) --
# side draft 0.1134 mm/mm (H/I/Jx/Kx probes: x 30.120@-18.0, 30.290@-16.5, 30.403@-15.5, 30.517@-14.5)
FLANGE_SECTIONS = [   # (z, x0, x1, y0, y1)
    (Z_BASE, 30.081, 70.166, -12.000, 42.000),
    (-17.35, 30.194, 70.053, -11.900, 41.900),
    (-16.30, 30.313, 69.934, -11.563, 41.563),
    (-15.25, 30.432, 69.815, -10.929, 40.929),
    (-14.20, 30.551, 69.696,  -9.799, 39.799),
    (Z_DECK, 30.648, 69.599,  -7.900, 37.900),
]
R_FL_BACK, R_FL_FRONT = 5.5, 7.0    # corner fits at z -15: back 5.507/5.493, front 7.025/6.996

# ---- middle structures -----------------------------------------------------
SHELF = (44.0, 56.0, -4.837, 0.063, -23.842, -21.342)   # x0,x1,y0,y1,z0,z1 (V x45/x50 z-22.5; D 44/56,0)
RIDGE_A = (41.5, 58.5, -4.837, -2.337, -23.842, Z_DECK)  # front mid ridge (Kx y-3.5; D 50,-4)
BOSS_D, BOSS_X, BOSS_Y = 5.0, 50.0, 4.502                # screw boss Ø5 (W x-probe: 47.502..52.498)
BOSS_Z0 = -21.342                                        # boss bottom (W 48.5,4.5)
BOSS_BLOCK = (44.0, 56.0, 1.063, 3.702, -21.342, Z_STEP) # block behind the snap (S z-18 x50)
PILOT_D, PILOT_Z0, PILOT_Z1 = 1.6, -21.842, -16.342      # meshfeatures: Ø1.6, len 5.5, centre z -19.092
CBORE_D, CBORE_Z0 = 3.0, -16.342                         # meshfeatures: Ø3.0 x 0.5 on top
SNAP_X0, SNAP_X1 = 45.0, 55.0                            # both fingers + tabs (Lx probes exactly [45,55])
SNAP_DRAFT = 0.111                                       # both drafted faces (front -1.288@-20 .. -0.51@-13; back 38.114@-20 .. 37.336@-13)
FRONT_STEP_SLAB_Y1 = 11.5       # front step slab -2.337..cradle (the cradle cut ends it at y 10.9)
CONNECTOR = (34.538, 39.9, -21.342, Z_STEP)              # back connector slab y0,y1,z0,z1 (C-tower probes; U x40 z-20)
CH_BACK_LO = (41.2, 58.8, 34.538, BACK_REBATE_Y0, -21.342, Z_BASE)  # back channel, lower (Jx y36 z-19/-21)
CH_BACK_HI = (44.0, 56.0, 34.538, BACK_REBATE_Y0, Z_BASE, -14.0)    # back channel, upper (Jx y36 z-16: gap 44..56)
CH_FRONT_A = (44.0, 56.0, -2.337, 0.063, -21.342, -12.0)  # slot around the front finger (S z-18: gap -2.337..-1.065)
CH_FRONT_B = (44.0, 56.0, 0.063, 1.063, -21.342, Z_STEP)  # slot behind it (S z-18: gap 0.063..1.063)
POCKET_Y0, POCKET_Y1 = 31.563, 35.763                     # ankle-block pockets (U probes z-20)
POCKET_XL = (34.0, 39.2)                                  # left pocket (ZZ y33 z-26)
POCKET_XR = (60.8, 66.0)                                  # right pocket (mirror; ZZ y33: rib band ends 60.8)

# ---- the measured floor (shared with the sole): rib/wall bottoms = sole
# outer floor + 2.000 mm. Table = meshslice.intervals along z on sole_left.stl,
# 27 x 31 grid (out/measure/foot/floor_table.py). Analytic record: plane
# z = 0.08697x - 34.4395, heel arc R7.2, toe arc R6.9, side fillets R7.9.
FLOOR_LIFT = 2.0
FLOOR_XS = [29.35, 29.6, 30.0, 30.5, 31.0, 31.5, 32.5, 33.5, 35.0, 36.5, 38.0,
            40.0, 44.0, 48.0, 52.0, 56.0, 60.0, 62.0, 64.0, 65.5, 67.0, 68.0,
            68.8, 69.4, 70.0, 70.35, 70.6]
FLOOR_YS = [-12.4, -12.0, -11.5, -11.0, -10.5, -10.0, -9.0, -8.0, -7.0, -6.0,
            -5.0, -3.0, 0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 33.0, 35.0,
            36.0, 37.0, 38.0, 39.0, 40.0, 40.5, 41.0, 41.5, 42.0, 42.4]
FLOOR_ZB = [
    [-24.001, -24.001, -24.001, -24.001, -24.001, -24.001, -24.001, -24.001, -24.001, -24.001, -24.526, -24.629, -24.739, -24.966, -25.238, -25.473, -25.608, -25.521, -25.251, -25.066, -24.934, -24.878, -24.632, -24.632, -24.632, -24.632, -24.632, -24.632, -24.632, -24.632, -24.632],
    [-24.001, -24.001, -24.001, -24.001, -24.001, -24.001, -24.001, -24.001, -24.001, -24.001, -24.526, -24.629, -24.739, -24.966, -25.238, -25.473, -25.608, -25.521, -25.251, -25.066, -24.934, -24.878, -24.632, -24.632, -24.632, -24.632, -24.632, -24.632, -24.632, -24.632, -24.632],
    [-24.739, -24.739, -24.739, -24.739, -24.739, -24.739, -24.739, -24.739, -24.739, -25.416, -25.734, -25.852, -25.991, -26.273, -26.585, -26.820, -26.925, -26.839, -26.578, -26.380, -26.247, -26.177, -25.895, -25.229, -25.229, -25.229, -25.229, -25.229, -25.229, -25.229, -25.229],
    [-24.921, -24.921, -24.921, -24.921, -24.921, -24.921, -24.921, -24.921, -25.764, -26.259, -26.559, -26.740, -26.898, -27.217, -27.558, -27.812, -27.905, -27.816, -27.539, -27.319, -27.172, -27.053, -26.733, -26.186, -25.265, -25.265, -25.265, -25.265, -25.265, -25.265, -25.265],
    [-24.606, -24.606, -24.606, -24.606, -24.606, -24.606, -24.606, -25.762, -26.413, -26.854, -27.154, -27.393, -27.563, -27.903, -28.253, -28.524, -28.618, -28.525, -28.231, -27.996, -27.837, -27.656, -27.315, -26.809, -26.054, -24.695, -24.695, -24.695, -24.695, -24.695, -24.695],
    [-25.469, -25.469, -25.469, -25.469, -25.469, -25.469, -25.469, -26.332, -26.910, -27.327, -27.625, -27.918, -28.096, -28.444, -28.804, -29.086, -29.179, -29.084, -28.772, -28.528, -28.342, -28.117, -27.767, -27.279, -26.598, -25.555, -24.649, -24.649, -24.649, -24.649, -24.649],
    [-24.535, -24.535, -24.535, -24.535, -24.535, -25.437, -26.475, -27.157, -27.659, -28.046, -28.343, -28.726, -28.922, -29.266, -29.630, -29.922, -30.016, -29.918, -29.578, -29.328, -29.052, -28.789, -28.435, -27.967, -27.353, -26.501, -25.912, -25.072, -25.072, -25.072, -25.072],
    [-24.787, -24.787, -24.787, -24.787, -25.681, -26.288, -27.145, -27.760, -28.226, -28.595, -28.888, -29.299, -29.549, -29.875, -30.214, -30.491, -30.586, -30.488, -30.142, -29.891, -29.540, -29.265, -28.906, -28.457, -27.877, -27.093, -26.570, -25.898, -24.878, -24.878, -24.878],
    [-24.936, -24.936, -24.936, -25.921, -26.579, -27.085, -27.850, -28.411, -28.849, -29.201, -29.489, -29.905, -30.233, -30.512, -30.779, -30.997, -31.091, -30.994, -30.688, -30.414, -30.023, -29.747, -29.401, -28.961, -28.396, -27.630, -27.123, -26.481, -25.566, -25.566, -25.566],
    [-25.528, -25.528, -25.528, -26.445, -27.085, -27.581, -28.320, -28.868, -29.295, -29.636, -29.909, -30.314, -30.667, -30.897, -31.079, -31.204, -31.247, -31.194, -30.976, -30.691, -30.315, -30.042, -29.710, -29.269, -28.688, -27.870, -27.297, -26.571, -25.566, -25.566, -25.566],
    [-22.952, -22.952, -25.555, -26.571, -27.296, -27.844, -28.630, -29.189, -29.610, -29.938, -30.189, -30.566, -30.877, -31.049, -31.121, -31.137, -31.141, -31.135, -31.054, -30.820, -30.484, -30.223, -29.885, -29.421, -28.772, -27.865, -27.275, -26.536, -25.522, -25.522, -25.522],
    [-22.833, -22.833, -25.481, -26.524, -27.272, -27.866, -28.768, -29.405, -29.850, -30.176, -30.412, -30.727, -30.890, -30.920, -30.947, -30.961, -30.966, -30.960, -30.931, -30.841, -30.558, -30.303, -29.925, -29.420, -28.749, -27.834, -27.238, -26.490, -25.459, -25.459, -25.459],
    [-22.594, -22.594, -25.332, -26.392, -27.162, -27.775, -28.698, -29.363, -29.839, -30.182, -30.411, -30.587, -30.585, -30.582, -30.591, -30.608, -30.616, -30.608, -30.598, -30.595, -30.419, -30.184, -29.833, -29.348, -28.680, -27.745, -27.135, -26.366, -25.281, -25.281, -25.281],
    [-22.355, -22.355, -25.107, -26.178, -26.959, -27.581, -28.518, -29.190, -29.669, -29.994, -30.185, -30.263, -30.261, -30.259, -30.258, -30.259, -30.266, -30.262, -30.264, -30.264, -30.188, -29.999, -29.676, -29.197, -28.524, -27.584, -26.962, -26.183, -25.084, -25.084, -25.084],
    [-22.116, -22.116, -24.858, -25.926, -26.701, -27.328, -28.254, -28.915, -29.379, -29.684, -29.864, -29.917, -29.918, -29.918, -29.920, -29.919, -29.917, -29.918, -29.917, -29.917, -29.864, -29.688, -29.379, -28.912, -28.249, -27.321, -26.706, -25.930, -24.856, -24.856, -24.856],
    [-21.877, -21.877, -24.580, -25.637, -26.391, -26.983, -27.875, -28.504, -28.958, -29.269, -29.466, -29.579, -29.588, -29.592, -29.590, -29.576, -29.567, -29.574, -29.579, -29.576, -29.462, -29.264, -28.949, -28.498, -27.865, -26.959, -26.364, -25.611, -24.561, -24.561, -24.561],
    [-21.638, -21.638, -24.250, -25.257, -25.974, -26.542, -27.402, -28.018, -28.455, -28.759, -28.972, -29.215, -29.266, -29.263, -29.238, -29.222, -29.216, -29.223, -29.249, -29.224, -29.017, -28.784, -28.451, -27.995, -27.371, -26.510, -25.940, -25.220, -24.211, -24.211, -24.211],
    [-21.518, -21.518, -24.067, -25.050, -25.757, -26.306, -27.085, -27.630, -28.025, -28.326, -28.559, -28.865, -29.072, -29.080, -29.059, -29.044, -29.040, -29.048, -29.077, -28.973, -28.711, -28.489, -28.174, -27.732, -27.118, -26.269, -25.706, -25.001, -24.022, -24.022, -24.022],
    [-23.750, -23.750, -23.750, -24.645, -25.269, -25.751, -26.471, -26.993, -27.398, -27.713, -27.956, -28.318, -28.619, -28.747, -28.825, -28.864, -28.863, -28.863, -28.788, -28.580, -28.267, -28.027, -27.722, -27.317, -26.777, -26.008, -25.479, -24.793, -23.834, -23.834, -23.834],
    [-22.771, -22.771, -22.771, -23.864, -24.541, -25.049, -25.802, -26.346, -26.769, -27.104, -27.370, -27.752, -28.039, -28.217, -28.392, -28.541, -28.600, -28.537, -28.349, -28.136, -27.798, -27.542, -27.232, -26.826, -26.293, -25.565, -25.082, -24.459, -23.575, -23.575, -23.575],
    [-22.038, -22.038, -22.038, -22.038, -23.316, -23.991, -24.883, -25.492, -25.950, -26.306, -26.584, -26.969, -27.176, -27.421, -27.678, -27.899, -27.972, -27.897, -27.643, -27.463, -27.147, -26.889, -26.557, -26.133, -25.575, -24.802, -24.280, -23.577, -22.374, -22.374, -22.374],
    [-22.784, -22.784, -22.784, -22.784, -22.784, -22.784, -24.013, -24.732, -25.243, -25.626, -25.914, -26.266, -26.416, -26.685, -26.984, -27.232, -27.291, -27.218, -26.958, -26.773, -26.537, -26.290, -25.950, -25.505, -24.896, -24.017, -23.363, -22.234, -22.234, -22.234, -22.234],
    [-22.955, -22.955, -22.955, -22.955, -22.955, -22.955, -22.955, -23.916, -24.507, -24.919, -25.218, -25.507, -25.644, -25.921, -26.229, -26.470, -26.517, -26.452, -26.212, -26.022, -25.867, -25.647, -25.305, -24.826, -24.140, -23.003, -23.003, -23.003, -23.003, -23.003, -23.003],
    [-23.017, -23.017, -23.017, -23.017, -23.017, -23.017, -23.017, -23.017, -23.773, -24.244, -24.546, -24.759, -24.892, -25.169, -25.471, -25.694, -25.731, -25.667, -25.459, -25.276, -25.161, -24.998, -24.661, -24.136, -23.296, -23.296, -23.296, -23.296, -23.296, -23.296, -23.296],
    [-22.613, -22.613, -22.613, -22.613, -22.613, -22.613, -22.613, -22.613, -22.613, -23.272, -23.600, -23.725, -23.846, -24.104, -24.380, -24.573, -24.607, -24.553, -24.370, -24.211, -24.101, -24.031, -23.716, -23.058, -23.058, -23.058, -23.058, -23.058, -23.058, -23.058, -23.058],
    [-22.245, -22.245, -22.245, -22.245, -22.245, -22.245, -22.245, -22.245, -22.245, -22.245, -22.684, -22.756, -22.861, -23.089, -23.334, -23.507, -23.552, -23.495, -23.332, -23.186, -23.088, -23.040, -22.757, -22.757, -22.757, -22.757, -22.757, -22.757, -22.757, -22.757, -22.757],
    [-22.245, -22.245, -22.245, -22.245, -22.245, -22.245, -22.245, -22.245, -22.245, -22.245, -22.684, -22.756, -22.861, -23.089, -23.334, -23.507, -23.552, -23.495, -23.332, -23.186, -23.088, -23.040, -22.757, -22.757, -22.757, -22.757, -22.757, -22.757, -22.757, -22.757, -22.757],
]

MATERIAL = "PLA"


# ---- helpers (HAND-aware) --------------------------------------------------
def _xs(lo, hi):
    """An x span, mirrored for the right foot."""
    return (lo, hi) if HAND > 0 else (-hi, -lo)


def _hand_xy(pts):
    if HAND > 0:
        return pts
    return [(-x, y) for x, y in reversed(pts)]


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


def _floor_sections():
    """Below-(sole floor + 2.0) as loft sections along x."""
    sections = []
    xs = FLOOR_XS if HAND > 0 else [-x for x in reversed(FLOOR_XS)]
    rows = FLOOR_ZB if HAND > 0 else list(reversed(FLOOR_ZB))
    for x, row in zip(xs, rows):
        pts = [(y, z + FLOOR_LIFT) for y, z in zip(FLOOR_YS, row)]
        pts += [(FLOOR_YS[-1] + 0.5, Z_LOW - 2), (FLOOR_YS[0] - 0.5, Z_LOW - 2)]
        sections.append((pts, x))
    return sections


def _arc_cut_pts(r, y_lo, y_hi, n=40):
    """(y, z) polygon of the region ABOVE the cradle arc of radius r about
    (AXIS_Y, AXIS_Z), between y_lo and y_hi — a cut prism along x."""
    pts = []
    for i in range(n + 1):
        y = y_lo + (y_hi - y_lo) * i / n
        dy = y - AXIS_Y
        z = AXIS_Z - math.sqrt(max(r * r - dy * dy, 0.0))
        pts.append((y, z))
    pts += [(y_hi, -5.0), (y_lo, -5.0)]
    return pts


def _box(p, x0, x1, y0, y1, z0, z1, op="add"):
    a, b = _xs(x0, x1)
    p.box(b - a, y1 - y0, z1 - z0, at=(a, y0, z0), op=op)


def build(doc, params=None):
    from cecad.core import Part
    if params:
        raise ValueError("microduck-foot-left takes no build parameters (got %s)" % sorted(params))
    name = "microduck-foot-left" if HAND > 0 else "microduck-foot-right"
    p = Part(name, material=MATERIAL)

    # 1. flange: ruled loft of rounded rects through the measured sections
    sections = []
    for z, x0, x1, y0, y1 in FLANGE_SECTIONS:
        sections.append((_hand_xy(_rounded_rect(x0, x1, y0, y1, R_FL_FRONT, R_FL_BACK)), z))
    p.loft(sections, axis="z", smooth=False, ruled=True)

    # 2. flange interior (below the step deck) and the open middle above it
    _box(p, 32.9, 67.1, -7.4, BACK_REBATE_Y0, Z_BASE - 0.1, Z_STEP, op="cut")
    _box(p, 29.0, 71.2, -2.337, BACK_REBATE_Y0, Z_STEP, -12.0, op="cut")

    # 3. lower body: walls, ledges, blocks, ribs, slabs (bottoms below the
    #    floor on purpose — step 6 cuts them to the measured floor)
    zlo = Z_LOW + 1
    _box(p, LB_X0, LB_X0 + WALL_T, LB_Y0, LB_Y1, zlo, Z_STEP)          # side walls
    _box(p, LB_X1 - WALL_T, LB_X1, LB_Y0, LB_Y1, zlo, Z_STEP)
    _box(p, LB_X0 + WALL_T, LEDGE_X, LB_Y0, LB_Y1, zlo, Z_STEP)        # ledges (cradle-cut later)
    _box(p, LB_X1 - (LEDGE_X - LB_X0 - WALL_T) - WALL_T, LB_X1 - WALL_T, LB_Y0, LB_Y1, zlo, Z_STEP)
    _box(p, LB_X0, LB_X1, LB_Y0, FRONT_WALL_Y1, zlo, Z_BASE)           # front wall
    _box(p, LB_X0, LB_X1, BACK_WALL_Y0, LB_Y1, zlo, -21.342)           # back wall, lower
    _box(p, LB_X0, LB_X1, BACK_REBATE_Y0, LB_Y1, -21.342, Z_BASE)      # back wall, rebated top
    for k in range(N_RIB):                                             # the rib comb
        y = RIB_Y0 + k * RIB_PITCH
        _box(p, LB_X0, LB_X1, y, y + RIB_T, zlo, Z_STEP)
    for y0, y1 in FRONT_RIB_YS:                                        # short front ribs
        _box(p, LB_X0, FRONT_RIB_XIN, y0, y1, zlo, Z_STEP)
        _box(p, LB_X1 - (FRONT_RIB_XIN - LB_X0), LB_X1, y0, y1, zlo, Z_STEP)
    _box(p, LB_X0, FRONT_BLOCK_X, FRONT_WALL_Y1, -0.462, zlo, Z_STEP)  # front side blocks
    _box(p, LB_X1 - (FRONT_BLOCK_X - LB_X0), LB_X1, FRONT_WALL_Y1, -0.462, zlo, Z_STEP)
    _box(p, LB_X0, LB_X1, -2.337, FRONT_STEP_SLAB_Y1, Z_BASE, Z_STEP)  # front step slab
    _box(p, LB_X0, LB_X1, CONNECTOR[0], CONNECTOR[1], CONNECTOR[2], CONNECTOR[3])  # back connector
    _box(p, SHELF[0], SHELF[1], SHELF[2], SHELF[3], SHELF[4], SHELF[5])            # front shelf
    _box(p, RIDGE_A[0], RIDGE_A[1], RIDGE_A[2], RIDGE_A[3], RIDGE_A[4], RIDGE_A[5])  # ridge A
    p.cyl(BOSS_D, Z_STEP - BOSS_Z0, at=(HAND * BOSS_X, BOSS_Y, BOSS_Z0))            # screw boss
    _box(p, BOSS_BLOCK[0], BOSS_BLOCK[1], BOSS_BLOCK[2], BOSS_BLOCK[3], BOSS_BLOCK[4], BOSS_BLOCK[5])

    # 4. channels
    for x0, x1, y0, y1, z0, z1 in (CH_BACK_LO, CH_BACK_HI, CH_FRONT_A, CH_FRONT_B):
        _box(p, x0, x1, y0, y1, z0, z1, op="cut")

    # 5. ankle-block pockets, through
    for x0, x1 in (POCKET_XL, POCKET_XR):
        _box(p, x0, x1, POCKET_Y0, POCKET_Y1, Z_LOW, -14.0, op="cut")

    # 6. the measured floor (sole cavity floor): cut everything below it
    p.loft(_floor_sections(), axis="x", smooth=False, ruled=True, op="cut")

    # 7. cradle: R16.3 seat + R16.5 roller relief
    a, b = _xs(32.9, 67.1)
    p.prism(_arc_cut_pts(CRADLE_R, 8.84, 35.16), b - a, at=(a, 0, 0), axis="x", op="cut")
    a, b = _xs(LEDGE_X, LB_X1 - (LEDGE_X - LB_X0 - WALL_T) - WALL_T)
    p.prism(_arc_cut_pts(RELIEF_R, RELIEF_Y0, RELIEF_Y1), b - a, at=(a, 0, 0), axis="x", op="cut")

    # 8. snap fingers (added after every cut so nothing shaves the barbs)
    a, b = _xs(SNAP_X0, SNAP_X1)
    front = [   # (y, z): drafted -y face, vertical +y face, 1.0 barb, taper to the tab tip
        (-1.437, -21.342), (0.063, -21.342), (0.063, -14.40),
        (1.063, -14.40), (1.063, Z_DECK), (0.350, Z_TAB), (-0.440, Z_TAB),
    ]
    p.prism(front, b - a, at=(a, 0, 0), axis="x")
    back = [    # bottom on the floor (-26.9 at x50), drafted +y face, barb toward -y
        (36.763, -26.9), (38.880, -26.9), (37.260, Z_TAB), (36.460, Z_TAB),
        (35.763, Z_DECK), (35.763, -14.35), (36.763, -14.35),
    ]
    p.prism(back, b - a, at=(a, 0, 0), axis="x")

    # 9. the M2 pilot + relief
    p.cyl(PILOT_D, PILOT_Z1 - PILOT_Z0, at=(HAND * BOSS_X, BOSS_Y, PILOT_Z0), op="cut")
    p.cyl(CBORE_D, Z_STEP - CBORE_Z0 + 0.1, at=(HAND * BOSS_X, BOSS_Y, CBORE_Z0), op="cut")

    return p
