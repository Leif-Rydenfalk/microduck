"""part:microduck-robot-hat-pcb — Pollen's "RPI Robot HAT" bare board, rebuilt.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. Imports only
cecad + stdlib. Every number below was READ OFF Pollen's published mesh
`reference/pollen-microduck-rl/assets/elec_rpi_robot_hat_pcb.stl` (metres)
on 2026-09-01 with `cad-mjcf sections`, `cecad.meshfeatures.cylinders`
and 0.1 mm plane cuts, and the rebuild is graded against that mesh by
`cecad.meshcompare` (evidence/refcheck/).

FRAME — Pollen's mesh frame, kept so the MJCF geom pos/quat (body jaw_soft,
pos (26.94, 28.994, -51.9) mm, quat (0.707, 0, 0, -0.707)) place it with
no re-derivation: the board lies in the x-y plane, z = 0 .. 0.84 (its
thickness), and the ORIGIN IS THE FIRST MOUNTING HOLE: the four Ø2.7
mounting holes are at (0, 0), (58, 0), (0, -23), (58, -23) — the Pi Zero
58 x 23 pattern (meshfeatures: centres (0.005, -0.005), (58.005, -0.005),
(0.005, -23.005), (58.005, -23.005), Ø2.70).

WHAT IT IS. The bare 65 x 30 x 0.84 mm PCB of Pollen's Robot HAT (SPEC.md
§5: TLV320AIC3104 codec, VL53L5CX/L8CX ToF, dormant BMI088, half-duplex
transceiver, battery-to-board power). The mesh is the bare board with its
drill: a 2 x 20 header at 2.54 mm pitch, two Ø2.0 holes on the header's
centreline, two blocks of Ø0.95 connector pins at 2.5 mm pitch (a 2 x 4
and a 2 x 3, rows 4.8 apart) and one Ø1.0 hole. No copper, no components:
the schematic and layout are NOT published (SPEC.md §7).
"""

# ---- outline, measured (mm) -------------------------------------------------
# bbox x -3.52 .. 61.505, y -26.51 .. 3.515, z 0 .. 0.84 (numpy over the STL)
T = 0.84                                # thickness, z 0 .. 0.84
HOLE_X = (0.0, 58.0)                    # Ø2.7 mounting holes (meshfeatures, 4 found)
HOLE_Y = (0.0, -23.0)
MOUNT_D = 2.7
CORNER_R = 3.52                         # corner arcs are CENTRED ON THE MOUNTING HOLES:
# the outline is 3.52 outside the hole centres on every side (x -3.52, y +3.515) and the
# x = -3.0 cut (0.52 in from the edge) spans y -24.84 .. 1.80, i.e. 1.716 in from each
# corner — R 3.5 gives 1.66, R 3.6 gives 1.74, so R = 3.52 centred on the hole (0.02 mm
# off the measured extremes) is the reading.
X_MIN, X_MAX = HOLE_X[0] - CORNER_R, HOLE_X[1] + CORNER_R
Y_MIN, Y_MAX = HOLE_Y[1] - CORNER_R, HOLE_Y[0] + CORNER_R

# ---- drill, every hole from meshfeatures.cylinders (axis z, cover 355 deg) ---
HDR_D, HDR_PITCH, HDR_X0, HDR_N, HDR_Y = 1.02, 2.54, 4.87, 20, (-1.27, 1.27)   # 40 holes
HDR_ANCHOR_D, HDR_ANCHOR = 2.0, ((6.14, 0.0), (51.86, 0.0))                     # 2 holes on the header centreline
CONN_D = 0.95
CONN_A = [(x, y) for x in (43.85, 48.65) for y in (-23.0, -20.5, -18.0, -15.5)]   # 2 x 4 block
CONN_B = [(x, y) for x in (53.5, 58.3) for y in (-17.45, -14.95, -12.45)]         # 2 x 3 block
ONE_D, ONE_AT = 1.0, (31.2, -11.9)

MATERIAL = "FR4"


def _outline(n=8):
    import math
    pts = []
    corners = [((HOLE_X[1], HOLE_Y[0]), 0), ((HOLE_X[0], HOLE_Y[0]), 90),
               ((HOLE_X[0], HOLE_Y[1]), 180), ((HOLE_X[1], HOLE_Y[1]), 270)]
    for (cx, cy), a0 in corners:
        for i in range(n + 1):
            a = math.radians(a0 + 90.0 * i / n)
            pts.append((cx + CORNER_R * math.cos(a), cy + CORNER_R * math.sin(a)))
    return pts


def build(doc, params=None):
    from cecad.core import Part
    if params:
        raise ValueError("microduck-robot-hat-pcb takes no build parameters (got %s)" % sorted(params))
    p = Part("microduck-robot-hat-pcb", material=MATERIAL)
    p.prism(_outline(), T, at=(0, 0, 0), axis="z")
    holes = []
    for x in HOLE_X:
        for y in HOLE_Y:
            holes.append((MOUNT_D, x, y))
    for i in range(HDR_N):
        for y in HDR_Y:
            holes.append((HDR_D, HDR_X0 + HDR_PITCH * i, y))
    for x, y in HDR_ANCHOR:
        holes.append((HDR_ANCHOR_D, x, y))
    for x, y in CONN_A + CONN_B:
        holes.append((CONN_D, x, y))
    holes.append((ONE_D,) + tuple(ONE_AT))
    for d, x, y in holes:
        p.cyl(d, T + 2, at=(x, y, -1), axis="z", op="cut")
    p.clean()
    # interfaces: the four mount holes (M2.5 on a real HAT; the community reads the
    # robot as an M2 system) and the header land, all on the top face z = T
    for i, (x, y) in enumerate([(hx, hy) for hx in HOLE_X for hy in HOLE_Y]):
        p.connector("mount_%d" % i, at=(x, y, 0.0), dir="-z")
    p.connector("header", at=(HDR_X0 + HDR_PITCH * (HDR_N - 1) / 2, 0.0, T), dir="+z")
    return p
