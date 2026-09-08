"""part:radxa-zero-3w — the Microduck's compute board, rebuilt as a bare PCB.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. Imports only
cecad + stdlib.

TWO SOURCES THAT DISAGREE, both kept:
  * Pollen's published mesh `reference/pollen-microduck-rl/assets/
    pcb__raspberry_pi_zero_2_w.stl` (metres) — NAMED a Raspberry Pi Zero 2 W
    and measured as one on 2026-09-01 (cad-mjcf sections, meshfeatures,
    0.1 mm plane cuts): 65.0 x 30.0 x 1.6 mm, R3 corners, 4 x Ø2.7 on a
    58 x 23 pattern, 2 x 20 Ø1.0 header holes at 2.54 mm pitch.
  * Radxa's own product brief (docs/fetched/radxa_zero_3w_product_brief.pdf,
    RAD-DOC-0084 rev 1.10, 2026-06-26, §4 Mechanical Specification), MEASURED
    off its raster drawing on 2026-09-02 by tools/measure_radxa_drawing.py
    (result: iterations/v0.0.1/evidence/radxa-zero-3w-mechanical.json): 65.0 x
    30.0 mm, 4 x Ø2.814 (Radxa prints Ø2.8), edge inset 3.5727 mm (Radxa
    prints 3.6), pitch 22.8662 across x 57.8429 along.

CORRECTED 2026-09-02 (lane C): this file previously carried
RADXA_LONG_SPAN = 54.7 as the hole pitch along the length. It is not. 54.7 is
a CONNECTOR dimension on the same view (a feature line 54.68 mm from the top
edge); the hole pitch measures 57.8429 mm, and Radxa's own printed 3.6 mm edge
inset implies 65.0 - 2(3.6) = 57.8. The measurement carries four negative
controls that a wrong scale would fail: the 40-pin header body comes out
5.1001 x 50.8187 mm (a 2x20 2.54 mm header is 5.08 x 50.80) with its centre
3.3355 mm from the right edge and 32.4343 mm from the top — and Radxa prints
"3. 3" and "32. 4" for exactly those two.

THE TWO PATTERNS BARELY DISAGREE. Pi Zero 2 W mesh 58.0 x 23.0 / Ø2.70 vs
Radxa measured 57.8429 x 22.8662 / Ø2.814: 0.157 mm and 0.134 mm apart, and
0.114 mm on the hole. The printed head parts fit either board; what actually
differs between the two boards is the CONNECTORS (2 x USB-C + micro-HDMI +
22-pin MIPI CSI here, micro-USB + mini-HDMI on a Pi Zero 2 W), which is a
shell-cutout question and not a mounting one.

The DEFAULT build is still the mesh (it is what every neighbouring part in the
MJCF was measured against and what cad-refcheck grades), and
`params={"holes": "radxa"}` builds the vendor drawing's measured pattern.

FRAME — Pollen's mesh frame, kept so the MJCF geom pos/quat (body jaw_soft,
pos (15.435, -0.011, -60.01) mm, quat (0.5, -0.5, -0.5, 0.5)) place it
with no re-derivation: the board lies in the x-z plane, THICKNESS ALONG Y
(y -0.8 .. 0.8), x -32.5 .. 32.5 (length), z -15 .. 15 (width).
"""

# ---- outline, measured off the mesh (mm) ------------------------------------
L, W, T = 65.0, 30.0, 1.6              # bbox x -32.5..32.5, z -15..15, y -0.8..0.8
CORNER_R = 3.0                          # x = -30.179 cut (2.32 in): z half-span 14.919 -> inset 0.081; R3 gives 0.078
# ---- drill: the mesh (Pi Zero 2 W) ------------------------------------------
MESH_MOUNT_D = 2.7                      # meshfeatures: 4 x Ø2.70 at (±29.0, ±11.5)
MESH_MOUNT_X, MESH_MOUNT_Z = (-29.0, 29.0), (-11.5, 11.5)
HDR_D, HDR_PITCH, HDR_N = 1.0, 2.54, 20   # 40 x Ø0.998, x -24.13 .. 24.13 step 2.54
HDR_Z = (-10.23, -12.77)                 # the two header rows (mesh)
# ---- drill: Radxa's brief, §4 drawing (mm) — the alternative pattern --------
RADXA_MOUNT_D = 2.814                    # MEASURED (Radxa prints "4 X Ø2. 8"); sd 0.0125 over the four
# The MEASUREMENT and the NOMINAL, kept apart on purpose (corrected 2026-09-03).
RADXA_EDGE_IN_MEAS = 3.5727              # MEASURED, sd 0.0396 over the eight edge insets
RADXA_LONG_SPAN_MEAS = 57.8429           # MEASURED pitch along the length. NOT 54.7 — see the header note above.
RADXA_WIDE_SPAN_MEAS = 22.8662           # MEASURED pitch across the width
# The NOMINAL is what the solid is built on. Radxa PRINTS one inset, "3. 6", on
# an outline it prints as "65. 0" x "30. 0"; that nominal reconstructs the two
# measured pitches to within 0.043 and 0.066 mm, where the competing
# Raspberry-Pi-Zero nominal (58.0 x 23.0) is 0.157 and 0.134 mm out. Building on
# half the raw measured pitch instead would cut the raster's own noise (1 sigma
# 0.0396 mm) into the geometry as if it were design intent. cad/interfaces.json
# `mount_holes.centres_mm` carries both figures and the 0.0215 / 0.0331 mm
# difference between them.
RADXA_EDGE_IN = 3.600                    # Radxa's printed callout "3. 6"
RADXA_LONG_SPAN = L - 2 * RADXA_EDGE_IN  # 57.800
RADXA_WIDE_SPAN = W - 2 * RADXA_EDGE_IN  # 22.800
RADXA_MOUNT_X = (-RADXA_LONG_SPAN / 2, RADXA_LONG_SPAN / 2)         # ±28.900
RADXA_MOUNT_Z = (-RADXA_WIDE_SPAN / 2, RADXA_WIDE_SPAN / 2)         # ±11.400

MATERIAL = "FR4"


def _outline(n=8):
    """(z, x) pairs — cecad's prism along axis 'y' takes (z, x)."""
    import math
    pts = []
    hx, hz = L / 2 - CORNER_R, W / 2 - CORNER_R
    corners = [((hz, hx), 0), ((-hz, hx), 90), ((-hz, -hx), 180), ((hz, -hx), 270)]
    for (cz, cx), a0 in corners:
        for i in range(n + 1):
            a = math.radians(a0 + 90.0 * i / n)
            pts.append((cz + CORNER_R * math.cos(a), cx + CORNER_R * math.sin(a)))
    return pts


def build(doc, params=None):
    from cecad.core import Part
    params = dict(params or {})
    holes = params.pop("holes", "mesh")
    if params:
        raise ValueError("radxa-zero-3w: unknown build parameters %s" % sorted(params))
    if holes not in ("mesh", "radxa"):
        raise ValueError("radxa-zero-3w: holes must be 'mesh' (Pollen's Pi Zero 2 W stand-in) "
                         "or 'radxa' (Radxa ZERO 3W product brief §4), got %r" % holes)
    p = Part("radxa-zero-3w", material=MATERIAL)
    p.prism(_outline(), T, at=(0, -T / 2, 0), axis="y")
    if holes == "mesh":
        mount = [(MESH_MOUNT_D, x, z) for x in MESH_MOUNT_X for z in MESH_MOUNT_Z]
    else:
        mount = [(RADXA_MOUNT_D, x, z) for x in RADXA_MOUNT_X for z in RADXA_MOUNT_Z]
    for d, x, z in mount:
        p.cyl(d, T + 2, at=(x, -T / 2 - 1, z), axis="y", op="cut")
    x0 = -HDR_PITCH * (HDR_N - 1) / 2
    for i in range(HDR_N):
        for z in HDR_Z:
            p.cyl(HDR_D, T + 2, at=(x0 + HDR_PITCH * i, -T / 2 - 1, z), axis="y", op="cut")
    p.clean()
    for i, (d, x, z) in enumerate(mount):
        p.connector("mount_%d" % i, at=(x, -T / 2, z), dir="-y")
    p.connector("header", at=(0.0, T / 2, sum(HDR_Z) / 2), dir="+y")
    return p
