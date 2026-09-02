# WRITTEN by tools/head_eye_ring_shelve.py on 2026-09-02 — a LOADER for a published mesh (the cecad.meshshelve shape).
"""part:microduck-eye-ring — cad/part.py, the TRIAD build contract.

    def build(doc, params=None) -> Part

WHAT THIS BUILDS. Pollen Robotics' published mesh `noenoeil` (MJCF sim asset, CC BY-SA-NC 4.0 (pollen-robotics/microduck_rl README)): the
EYE BEZEL — a Ø30.000 mm ring, 7.5 mm long, with a Ø14.4 bore for the M12 lens, that
stands proud of the face panel (whose only opening on this axis is the Ø14.5 lens hole).
GOAL.md finding 1 called the product's bezel "missing" from the simulation meshes; it is
this mesh (HEAD-RECONSTRUCTION.html §6). Loaded through `cecad.core.Part.from_mesh` at
scale 1000.0 (the file is in metres). Render, place, measure and print it; do not cut it.

FRAME. The mesh's own frame, unchanged: bbox x -15.000..15.000, y -63.500..-54.000, z 5.000..35.000 mm,
ring axis y, boss centre (0, -59.25, 20). The MJCF geom pos/quat for `noenoeil` (body jaw_soft,
spec/mesh-placements.json) place it directly.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GEOMETRY = "geometry/noenoeil.stl"
SCALE = 1000.0
MATERIAL = "PLA"


def build(doc, params=None):
    if params:
        raise ValueError("microduck-eye-ring takes no build parameters (got %s) — it loads a published mesh" % sorted(params))
    from cecad.core import Part
    path = os.path.join(ROOT, GEOMETRY)
    if not os.path.exists(path):
        raise FileNotFoundError("microduck-eye-ring: %s is missing — the folder cannot build without its geometry" % path)
    return Part.from_mesh(path, name="microduck-eye-ring", material=MATERIAL, scale=SCALE, tol=0.05)
