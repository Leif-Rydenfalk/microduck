"""part:radxa-zero-3w — the Microduck's compute board, rebuilt as a bare PCB.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. Imports only
cecad + stdlib.

TWO SOURCES THAT DISAGREE, both kept:
  * Pollen's published mesh `reference/pollen-microduck-rl/assets/
    pcb__raspberry_pi_zero_2_w.stl` (metres) — NAMED a Raspberry Pi Zero 2 W
    and measured as one on 2026-09-01 (cad-mjcf sections, meshfeatures,
    0.1 mm plane cuts): 65.0 x 30.0 x 1.6 mm, R3 corners, 4 x Ø2.7 on a
    58 x 23 pattern, 2 x 20 Ø1.0 header holes at 2.54 mm pitch.
  * Radxa's own product brief (docs/fetched/radxa-zero3w-product-brief.pdf,
    RAD-DOC-0084 rev 1.10, 2026-06-26, §4 Mechanical Specification): 65.0 x
    30.0 mm, 4 x Ø2.8, hole centres 3.6 mm in from the long edges (22.8
    apart) and 54.7 apart along the length — NOT the Pi Zero's 58 x 23.
The Microduck runs a Radxa Zero 3W (SPEC.md §5, device tree radxa,zero-3w)
but its simulator carries a Pi Zero 2 W stand-in. Which drill the PRINTED
head parts actually fit is CANNOT DETERMINE from published material, so:
the DEFAULT build is the mesh (it is what every neighbouring part in the
MJCF was measured against and what cad-refcheck grades), and
`params={"holes": "radxa"}` builds the vendor drawing's pattern instead.

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
RADXA_MOUNT_D = 2.8                      # "4 x Ø2.8"
RADXA_EDGE_IN = 3.6                      # "3.6" from the long edge to the hole centre
RADXA_LONG_SPAN = 54.7                   # "54.7" between the hole rows along the length (read off the raster drawing)
RADXA_MOUNT_X = (-RADXA_LONG_SPAN / 2, RADXA_LONG_SPAN / 2)
RADXA_MOUNT_Z = (-(W / 2 - RADXA_EDGE_IN), W / 2 - RADXA_EDGE_IN)   # ±11.4

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
