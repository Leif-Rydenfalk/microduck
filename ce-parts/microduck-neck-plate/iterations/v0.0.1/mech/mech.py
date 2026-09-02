"""mech.py — mass, inertia, material, the joints this part offers.

Contract (TRIAD.md): `def mech() -> dict`. Numbers with sources, no adjectives.
A number nobody measured stays absent — never a plausible default.
"""


def mech():
    return {
        "slug": "microduck-neck-plate",
        "material": "PLA",
        "volume_mm3": {"value": 399.8, "source": "divergence-theorem volume of the built solid's mesh, cad-refcheck r1 compare.json 2026-09-02 (reference mesh: 399.9, ratio 0.9998)"},
        "mass_g": {"value": None, "source": "the MJCF gives the whole neck BODY (two plates + head-pitch servo) as one 36.8 g inertial; the plate alone is not published, and print mass depends on infill — ask ce-slice, never volume x density"},
        "joints": [],
        "notes": "a rigid strap, no joints of its own: it bolts the neck-pitch servo case to the head-pitch servo case (2 x M2 each end); the neck's two revolute joints live in those servos",
    }
