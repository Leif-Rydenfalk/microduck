"""part:microduck-upper-leg-right — the right thigh housing: the left one, mirrored.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`.

MEASURED, 2026-09-01: Pollen's `upper_leg_right.stl` is the EXACT x-mirror
of `upper_leg_left.stl`. With x negated and y, z kept, every one of the
6123 welded vertices of one mesh has a vertex of the other at 0.0000 mm
(nearest-neighbour distance both ways, numpy; both meshes 12250 triangles,
612584 bytes). Bboxes: left x 42.5..70.5, right x -70.5..-42.5, y and z
identical to the third decimal. `cad-mjcf sections --axis z` gives the
same 20 widths for both to 0.001 mm.

So this folder does not carry a second copy of two hundred measured
numbers that could drift from the first. It composes
`part:microduck-upper-leg-left` through the triad loader — TRIAD.md:
"cad/part.py of a part that uses parts may compose other parts' build()"
— and reflects it in the yz plane at x = 0, which is exactly the map
Pollen's two meshes are related by. refs.json names the dependency.

Chirality matters: a mirrored cup is a different print, not the left one
turned over — the single side wall is on -y in both, and the servo axes
run along x from the open face at x = -42.5 to the back plate at x = -70.5.
The MJCF places this mesh with pos (0,0,-42.5) quat (0.5,-0.5,0.5,0.5) in
body upper_leg_right (spec/mesh-placements.json).

Every connector of the left is re-declared here at (-x, y, z) with its
direction reflected. Frame in the right's own mesh coordinates.
"""


def build(doc, params=None):
    from cecad import triad
    from cecad.core import Part
    if params:
        raise ValueError("microduck-upper-leg-right takes no build parameters (got %s)" % sorted(params))
    left = triad.load(doc, "part:microduck-upper-leg-left")
    # reflect the solid in the yz plane through x = 0 (keep=False: no union
    # with the unmirrored left — this is the right, not both)
    left.mirror(plane="yz", at=(0, 0, 0), keep=False)
    p = Part("microduck-upper-leg-right", material=left.material, shape=left.shape)
    p.notes.extend(left.notes)
    # connectors: the same anchors, x negated, x-directions flipped
    # (positions from the left's measured constants — see its part.py)
    X_BACK, X_BOSS_SMALL, X_PIN_TIP = 70.5, 64.7, 64.5
    A0, A1 = (0.0, 0.0), (22.0, 35.777)
    PINS = [(-0.5, 43.777), (-0.5, 27.777), (-8.0, 22.5), (8.0, 22.5)]
    p.connector("hip_pitch_axle", at=(-X_BACK, A0[0], A0[1]), dir="-x")
    p.connector("knee_axle", at=(-X_BACK, A1[0], A1[1]), dir="-x")
    p.connector("hip_pitch_servo_seat", at=(-X_BOSS_SMALL, A0[0], A0[1]), dir="+x")
    p.connector("knee_servo_seat", at=(-X_BOSS_SMALL, A1[0], A1[1]), dir="+x")
    for i, (cy, cz) in enumerate(PINS):
        p.connector("pin_%d" % (i + 1), at=(-X_PIN_TIP, cy, cz), dir="+x")
    return p
