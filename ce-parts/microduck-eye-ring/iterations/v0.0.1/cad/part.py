"""part:microduck-eye-ring — the eye bezel, REBUILT parametrically. Ours.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. Imports cecad +
stdlib only.

HOW THIS GEOMETRY WAS AUTHORED — the licence question, answered first.
This file replaces a LOADER that shipped Pollen Robotics' published mesh
`noenoeil.stl` (CC BY-SA-NC 4.0) as our geometry. Nothing of that mesh
survives here: no vertex, no facet, no decimated outline. What survives is a
LIST OF DIMENSIONS taken with calipers off the published artifact
(`tools/own_measure_eyering.py`, a ray-cast through the mesh at 0.1 mm
pitch; readings frozen in `out/own/measure/eye-ring.json`), which is
ordinary reverse engineering, plus the interfaces this part must satisfy
(the M12 lens bore, the face panel's front plane). The part below is a
SOLID OF REVOLUTION generated from ten numbers and three locating tabs —
a machine element whose every dimension is dictated by fit, not by
expression. See docs/REBUILD-PROTOCOL.md and LICENCE-POSITION.html.

FRAME — Pollen's mesh frame, kept on purpose so the MJCF geom pos/quat
place this part with no re-derivation and refcheck needs no alignment:
ring axis is +y, the optical axis sits at (x, z) = (0, 20), the ring
occupies y -63.5 .. -54.0.

THE MEASUREMENTS, each with the probe line that produced it
(out/own/measure/eye-ring.json; probe A = material along x at (y, z=20),
probe C = material along y at (z=20, x=r); 0.1 mm pitch):

  probe A, y -63.0 .. -55.5   outer radius 15.000 flat        -> OD 30.000
  probe A, y -63.5            outer radius 14.500              -> 0.5 x 45 deg
  probe A, y -63.0            outer radius 15.000                 front chamfer
  probe A, y -61.5 .. -55.5   inner radius  7.200 flat        -> bore 14.400
  probe A, y -63.5            inner radius  9.200 }  2.000 mm of y for
  probe A, y -61.5            inner radius  7.200 }  2.000 mm of r -> 45 deg funnel
  probe C, every r 9.5..14.5  material ends at y -55.500      -> rear face plane
  probe C, r 7.2 .. 15.0      material starts at y -63.5      -> front face plane
  section y -54.75            three arcs, r 8.500 .. 9.500,
                              spanning -160..-140, -40..-20 and 80..100 deg
                              about (x=0, z=20)                -> 3 tabs, 20 deg
                              wide, 120 deg apart, wall 1.000, reaching y -54.000

WHAT THE PART IS FOR. The bezel that surrounds the camera eye. Its bore is
clearance for the M12 lens (part:microduck-m12-lens, 16.94 mm barrel, held
behind the panel by part:microduck-m12-lens-holder) — the funnel is the
cone the lens looks through. Its rear face butts on part:microduck-face-part's
front plane at y -55.500, and the three tabs enter that panel and locate it
on the optical axis. The part is printed in the accent colour.
"""
import math

# ---- driving parameters, every one a caliper reading (mm, degrees) --------
OD = 30.000               # probe A: outer radius 15.000 over y -63.0..-55.5
BORE_D = 14.400           # probe A: inner radius 7.200 over y -61.5..-55.5
Y_FRONT = -63.500         # probe C: material starts here at every radius
Y_BACK = -55.500          # probe C: material ends here at every radius >= 9.5
CHAMFER = 0.500           # probe A: r 15.000 at y -63.0 -> 14.500 at y -63.5
FUNNEL = 2.000            # probe A: r 7.200 at y -61.5 -> 9.200 at y -63.5
TAB_OD = 19.000           # section y -54.75: arcs reach r 9.500
TAB_ID = 17.000           # section y -54.75: arcs start at r 8.500
TAB_LEN = 1.500           # y -55.500 .. -54.000
TAB_ARC = 20.0            # each arc spans 20 deg
TAB_ANGLES = (90.0, 210.0, 330.0)   # centres, measured as atan2(z-20, x)
AXIS_X, AXIS_Z = 0.0, 20.000        # optical axis in the mesh frame
MATERIAL = "PLA"


def _sector(r_in, r_out, a_mid, a_span, cz, cx, n=12):
    """Annular sector as (u, v) = (z, x) points — the plane a prism along
    the y axis takes (cecad's cyclic mapping: axis 'y' takes (z, x))."""
    a0, a1 = math.radians(a_mid - a_span / 2), math.radians(a_mid + a_span / 2)
    pts = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        pts.append((cz + r_out * math.sin(a), cx + r_out * math.cos(a)))
    for i in range(n + 1):
        a = a1 + (a0 - a1) * i / n
        pts.append((cz + r_in * math.sin(a), cx + r_in * math.cos(a)))
    return pts


def build(doc, params=None):
    from cecad.core import Part
    if params:
        raise ValueError("microduck-eye-ring takes no build parameters (got %s)"
                         % sorted(params))
    p = Part("microduck-eye-ring", material=MATERIAL)

    ro, ri = OD / 2.0, BORE_D / 2.0
    # (r, y) profile, revolved about the y axis through (x, z) = (0, 20).
    profile = [
        (ri + FUNNEL, Y_FRONT),                 # front bore lip, r 9.200
        (ro - CHAMFER, Y_FRONT),                # front face out to r 14.500
        (ro, Y_FRONT + CHAMFER),                # 45 deg chamfer up to r 15.000
        (ro, Y_BACK),                           # outer cylinder
        (ri, Y_BACK),                           # rear face, in to the bore
        (ri, Y_FRONT + FUNNEL),                 # bore, r 7.200
    ]
    p.revolve(profile, at=(AXIS_X, 0.0, AXIS_Z), axis="y")

    # three locating tabs behind the rear face
    for a in TAB_ANGLES:
        p.prism(_sector(TAB_ID / 2.0, TAB_OD / 2.0, a, TAB_ARC, AXIS_Z, AXIS_X),
                TAB_LEN, at=(0.0, Y_BACK, 0.0), axis="y")

    p.connector("optical_axis", at=(AXIS_X, Y_BACK, AXIS_Z), dir=(0, -1, 0))
    return p
