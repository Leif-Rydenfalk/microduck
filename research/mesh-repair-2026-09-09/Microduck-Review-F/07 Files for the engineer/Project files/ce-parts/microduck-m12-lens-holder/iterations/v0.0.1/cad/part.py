"""part:microduck-m12-lens-holder — the M12 camera-lens holder, rebuilt
parametrically.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`.

HOW THIS GEOMETRY WAS AUTHORED (the licence question, answered here so
component.json and docs/LICENCE-POSITION.html can cite one place).
Nobody outside Pollen Robotics has their CAD. This solid was AUTHORED
from measurements — it is not traced from, decimated from, offset from
or in any way derived from the triangles of Pollen's mesh file. Every
driving number below is a CALIPER READING taken on 2026-09-05 with
`cecad.meshslice.intervals` (a ray cast through the published artifact,
reported as material intervals) and `cecad.meshfeatures.cylinders`
(least-squares cylinder fits), and the probe line that produced each one
is quoted beside it. Reading dimensions off a published artifact and
re-authoring the part from those dimensions is ordinary reverse
engineering; the result is our own expression of those dimensions.
Nothing here copies the mesh: the round tube is ONE surface of
revolution through a 9-point meridian, the square mount is ONE extruded
rounded rectangle, each ear is ONE ruled loft between two stadium
outlines, and the three holes are three cylinders. 10 992 triangles in,
16 modelling calls out.

The rebuild is then GRADED against the published mesh by
`ce-cad/bin/cad-refcheck` — grading against a reference is a
measurement, not a derivation.

FRAME — Pollen's mesh frame, kept on purpose (the MJCF geom pos/quat for
body `jaw_soft` then place it with no re-derivation, and refcheck needs
no alignment): the OPTICAL AXIS is the +y line through (x 0, z 0); the
mount face is y = 0 and the lens mouth y = 14.8. bbox x -12..12,
y 0..14.8, z -8..8.

WHAT IT IS. A camera-lens holder in three pieces:
  * a SQUARE MOUNT TUBE, 16 x 16 outer with a 14.2 x 14.2 hollow
    (0.9 mm wall), y 0..7.8, R0.2 on its four outer corners;
  * TWO EARS on the x axis, y 0..3.6, each a stadium tab capped by a
    semicircle at x = +-10 with a Ø2.0 through hole — the two M2 screws
    that hold the holder to the head;
  * a ROUND LENS TUBE, y 6.8..14.8, Ø15.2 outside and Ø11.6 inside
    (Ø11.6 is the MINOR diameter of M12 x 0.5 — NEITHER MESH CARRIES A
    THREAD, so whether the real part is tapped or a plain press bore is
    CANNOT DETERMINE from the reference; see cad/interfaces.json
    `lens_bore`), with a funnel at the mouth and one Ø2.0 radial grub
    hole at y = 12 that breaks into the bore — the focus lock.
"""

import math

# ---- measured off m12_lens_holder.stl, 2026-09-05 (mm) ----------------------
# Every probe below is `meshslice.intervals(T, axis, u, v)` on the mesh loaded
# at scale 1000; the frame is the mesh's own.

# SQUARE MOUNT TUBE
BOX_HALF   = 8.0     # outer half-width. X at (y2, z4/z6/z7): (-8.0,-7.1),(7.1,8.0)
BOX_IN     = 7.1     # inner half-width -> 0.9 mm wall (same probe)
BOX_Y1     = 7.8     # end face. Y at (z0, x7.62): (0, 7.8); at x7.65: (0, 7.8)
R_EDGE     = 0.2     # outer edge round. X at (y2, z7.95) reads x 7.932 =
                     #   7.8 + sqrt(0.2^2 - 0.15^2); the SAME R0.2 fits the
                     #   front outer edge to 0.001 mm at four y stations
                     #   (14.65 -> 7.594, 14.70 -> 7.573, 14.78 -> 7.487,
                     #   14.795 -> 7.444 vs 7.4 + sqrt(0.04-(y-14.6)^2))

# LENS TUBE (surface of revolution about the y axis)
TUBE_R     = 7.6     # outer radius. X at (y8/y10/y12/y14, z0): |x| 5.8..7.6
BORE_R     = 5.8     # Ø11.6 bore; meshfeatures: d 11.6, len 7.498,
                     #   centre (0, 10.549, 0), residual 0.000 mm, 355 deg
TUBE_Y0    = 6.8     # tube back face. Y at (z0, x5.9/6.5/7.0/7.09): starts 6.8
TUBE_Y1    = 14.8    # front face = bbox y max
MOUTH_Y0   = 14.30   # bore funnel starts. Fitted on five probes: X at (y,z0)
MOUTH_SLOPE = 2.60   #   gives inner r 5.935@14.35, 6.065@14.40, 6.326@14.50,
                     #   6.716@14.65, 7.054@14.78 -> dr/dy = 2.600 +- 0.005,
                     #   back-extrapolating to r 5.8 at y 14.298
MOUTH_R1   = BORE_R + MOUTH_SLOPE * (TUBE_Y1 - MOUTH_Y0)   # 7.10 at the mouth

# EARS
EAR_X      = 10.0    # hole centres. meshfeatures: 2 x d 2.0, len 3.6,
                     #   centres (-+10, 1.8, 0), axis y, residual 0.000 mm
EAR_Y1     = 3.6     # ear end face (hole length; X at y3.6 shows no ear)
EAR_W0     = 2.0     # half-width AND cap radius at y=0. X at (y0, z0) reads
                     #   x 12.0 = EAR_X + 2.0; Z at (x8.5/9.0, y1) reads
                     #   +-1.903 (a FLAT flank, not a circle: a circle of
                     #   r 1.903 about x 10 would read 1.62 at x 9.0)
EAR_DRAFT  = 0.0973  # inward taper per mm of y: x_max 12.000@y0, 11.951@0.5,
                     #   11.903@1.0, 11.806@2.0, 11.708@3.0, 11.669@3.4 —
                     #   linear to 0.001 mm (the last 0.2 mm rolls into the
                     #   R0.2 end round, which is not modelled: 0.06 mm)
EAR_X_IN   = BOX_IN  # the tab's inboard end is buried in the box wall

# HOLES
SCREW_D    = 2.0     # the two mount screws (meshfeatures above)
GRUB_D     = 2.0     # focus lock. meshfeatures: d 2.0, len 1.887, centre
GRUB_Y     = 12.0    #   (0, 12, 6.657), axis z -> it pierces the +z wall
GRUB_Z0    = 5.0     #   only (z 5.713..7.600) and breaks into the bore
MATERIAL   = "PLA"
N_ARC      = 8       # segments per modelled arc


def _stadium(w, x_in, x_cap, sign=1, n=16):
    """(z, x) outline of one ear at half-width `w`: a flat-flanked tab from
    x_in to x_cap capped by a semicircle of radius w about (0, x_cap).

    Written for the +x ear and MIRRORED for the -x one (v -> -v, point
    order reversed) so both wires keep the same winding — two wires of
    opposite winding make makeLoft build a twisted or empty solid, which
    is what r1 did (bbox x 20.0 against the reference's 24.0)."""
    pts = [(-w, x_in)]
    for i in range(n + 1):                   # 180 deg -> 0 deg, the cap
        t = math.pi * (1.0 - i / n)
        pts.append((w * math.cos(t), x_cap + w * math.sin(t)))
    pts.append((w, x_in))
    if sign < 0:
        pts = [(u, -v) for u, v in reversed(pts)]
    return pts


def _rounded_square(half, r, n=N_ARC):
    """(u, v) outline of a square of half-width `half` with radius-`r`
    corners."""
    pts = []
    c = half - r
    for cu, cv, a0 in ((c, c, 0.0), (-c, c, 90.0), (-c, -c, 180.0), (c, -c, 270.0)):
        for i in range(n + 1):
            a = math.radians(a0 + 90.0 * i / n)
            pts.append((cu + r * math.cos(a), cv + r * math.sin(a)))
    return pts


def _tube_meridian():
    """(r, y) meridian of the lens tube, revolved about the optical axis.

    Nine points: bore, funnel, front annulus, the R0.2 outer roll, the
    outer wall and the back face."""
    pts = [(BORE_R, TUBE_Y0), (BORE_R, MOUTH_Y0), (MOUTH_R1, TUBE_Y1),
           (TUBE_R - R_EDGE, TUBE_Y1)]
    cy = TUBE_Y1 - R_EDGE
    for i in range(1, N_ARC + 1):            # R0.2 roll, 90 deg -> 0 deg
        a = math.radians(90.0 - 90.0 * i / N_ARC)
        pts.append((TUBE_R - R_EDGE + R_EDGE * math.cos(a),
                    cy + R_EDGE * math.sin(a)))
    pts.append((TUBE_R, TUBE_Y0))
    return pts


def build(doc, params=None):
    from cecad.core import Part
    if params:
        raise ValueError("microduck-m12-lens-holder takes no build parameters "
                         "(got %s)" % sorted(params))
    p = Part("microduck-m12-lens-holder", material=MATERIAL)

    # 1. square mount tube, hollow through
    p.prism(_rounded_square(BOX_HALF, R_EDGE), BOX_Y1, at=(0, 0, 0), axis="y")
    p.prism([(-BOX_IN, -BOX_IN), (BOX_IN, -BOX_IN), (BOX_IN, BOX_IN),
             (-BOX_IN, BOX_IN)], BOX_Y1 + 2.0, at=(0, -1.0, 0), axis="y",
            op="cut")

    # 2. the two ears — a ruled loft between the y=0 and y=EAR_Y1 outlines
    for s in (1, -1):
        w1 = EAR_W0 - EAR_DRAFT * EAR_Y1
        p.loft([(_stadium(EAR_W0, EAR_X_IN, EAR_X, s), 0.0),
                (_stadium(w1, EAR_X_IN, EAR_X, s), EAR_Y1)],
               axis="y", smooth=False, ruled=True)
        p.cyl(SCREW_D, EAR_Y1 + 2.0, at=(s * EAR_X, -1.0, 0), axis="y", op="cut")

    # 3. the lens tube
    p.revolve(_tube_meridian(), at=(0, 0, 0), axis="y")

    # 4. the focus-lock grub hole through the +z wall only
    p.cyl(GRUB_D, BOX_HALF - GRUB_Z0 + 1.0, at=(0, GRUB_Y, GRUB_Z0),
          axis="z", op="cut")

    # connectors — one per interface in cad/interfaces.json
    p.connector("lens_bore", at=(0.0, TUBE_Y0, 0.0), dir=(0.0, 1.0, 0.0))
    p.connector("mount_screws", at=(0.0, 1.8, 0.0), dir=(0.0, -1.0, 0.0))
    p.connector("focus_lock", at=(0.0, GRUB_Y, TUBE_R), dir=(0.0, 0.0, 1.0))
    return p
