"""part:microduck-speaker — the speaker stand-in of Pollen's Microduck MJCF.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. Imports only
cecad + stdlib. Every number below was READ OFF Pollen's published mesh
`reference/pollen-microduck-rl/assets/speaker.stl` (metres, 12 triangles)
on 2026-09-01 with `cad-mjcf sections` and a numpy bbox, and the rebuild is
graded against that mesh by `cecad.meshcompare` (evidence/refcheck/).

FRAME — Pollen's mesh frame, kept on purpose so the MJCF geom pos/quat
(body jaw_soft, pos (10, -16.786, 26.023) mm, quat (0.5, 0.5, 0.5, 0.5))
place it with no re-derivation: x 0..35, y -25..0, z 0..7.

WHAT IT IS. A 35 x 25 x 7 mm box, 12 triangles — Pollen's placeholder for
the bought speaker (SPEC.md §4.3 / §5). The mesh carries no hole, no
terminal, no grille: nothing about the real speaker is measurable from it.
The part number is CANNOT DETERMINE (docs/README.md).
"""

# ---- measured off speaker.stl (mm): bbox min (0, -25, 0) max (35, 0, 7) ----
L, W, H = 35.0, 25.0, 7.0           # size along x, y, z
X0, Y0, Z0 = 0.0, -25.0, 0.0        # min corner

MATERIAL = "ABS"   # a moulded speaker frame, assumed — see README (CANNOT DETERMINE)


def build(doc, params=None):
    from cecad.core import Part
    if params:
        raise ValueError("microduck-speaker takes no build parameters (got %s)" % sorted(params))
    p = Part("microduck-speaker", material=MATERIAL)
    p.box(L, W, H, at=(X0, Y0, Z0))
    p.clean()
    # the face that radiates: +z in the mesh frame (the 35 x 25 face), stated as a connector
    p.connector("front", at=(X0 + L / 2, Y0 + W / 2, Z0 + H), dir="+z")
    p.connector("back", at=(X0 + L / 2, Y0 + W / 2, Z0), dir="-z")
    return p
