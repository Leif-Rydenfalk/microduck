"""mech.py — mass, inertia, material, the joints this part offers.

Contract (TRIAD.md): `def mech() -> dict`. Numbers with sources, no adjectives.
"""


def mech():
    return {
        "slug": "microduck-motor-support",
        "material": "PLA",
        "volume_mm3": {"value": 7830.3, "source": "divergence-theorem volume of the built solid's mesh (cad-refcheck r6 compare.json, 2026-09-02); reference mesh 7515.1 (ratio 1.042)"},
        "mass_g": {"value": None, "source": "the MJCF gives the whole jaw_soft BODY (188.766 g) as one lump; this plate alone is not published. PLA at 1.24 mg/mm3 would put the solid near 9.7 g, but infill/walls of the real print are not known"},
        "joints": [
            {"at": "head_roll", "kind": "revolute", "axis": "+y", "source": "MJCF joint head_roll, range +/-25 deg"},
            {"at": "mouth_servo", "kind": "revolute", "axis": "-y", "source": "the mouth/jaw servo barrel measured at (x 0, z 4.49); MJCF jaw joint"},
        ],
    }
