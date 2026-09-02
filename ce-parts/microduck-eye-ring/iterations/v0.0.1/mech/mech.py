"""mech.py — mass, inertia, material, the joints this part offers.

Contract (TRIAD.md): `def mech() -> dict`. Numbers with sources, no adjectives.
A number nobody measured stays absent — never a plausible default.
"""


def mech():
    return {
        "slug": "microduck-eye-ring",
        "material": "PLA",
        "material_source": "the accent-colour printed ring in every product photograph (images/CATALOG.md: 'Eye-ring colour = the contrasting accent'); Pollen prints the shells in PLA (docs/PARTS.md)",
        "mass_g": None,
        "mass_why": "the MJCF lumps the whole head (body jaw_soft) into one inertial; no per-geom mass is published and no ring has been weighed",
        "bbox_mm": [30.0000, 9.5000, 30.0000],
        "bbox_source": "noenoeil.stl x/y/z extents, cecad.meshslice at scale 1000 (tools/head_eye_ring_shelve.py, 2026-09-02)",
        "joints": [],
    }
