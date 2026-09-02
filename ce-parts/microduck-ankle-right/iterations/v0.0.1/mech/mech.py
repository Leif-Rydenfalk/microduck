"""mech.py — mass, inertia, material, the joints this part offers.

Contract (TRIAD.md): `def mech() -> dict`. Numbers with sources, no adjectives.
"""


def mech():
    return {
        "slug": "microduck-ankle-right",
        "material": "PLA",
        "volume_mm3": {"value": 7896.7, "source": "closed-mesh volume of the built solid's STL, cecad.meshcompare (out/refcheck/microduck-ankle-right/r1/compare.json); reference mesh reads 7877.8 (ratio 1.0024)"},
        "mass_g": {"value": None, "source": "the MJCF gives the whole `ankle_right` BODY (bracket + ankle XL330 + foot + sole) as 30.025 g (measured.json joint right_ankle); the bracket alone is not published"},
        "joints": [
            {"at": "ankle_bearing / ankle_horn", "kind": "revolute", "axis": "-x (part frame), the line (y 22.0, z -6.223)", "source": "MJCF joint right_ankle, hinge, range +/-90 deg, actuated; bearing 15x10x3 in this wall, XL330 horn on the other"},
        ],
    }
