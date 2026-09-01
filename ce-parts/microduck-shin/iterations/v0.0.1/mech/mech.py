"""mech.py — mass, inertia, material, the joints this part offers.

Contract (TRIAD.md): `def mech() -> dict`. Numbers with sources, no adjectives.
"""


def mech():
    return {
        "slug": "microduck-shin",
        "material": "PLA",
        "volume_mm3": {"value": None, "source": "read it off the build: bin/cad part:microduck-shin prints the MEASURED volume"},
        "mass_g": {"value": None, "source": "the MJCF gives the whole `leg` BODY (two plates + knee servo) as 21.584 g; the plate alone is not published"},
        "joints": [
            {"at": "knee", "kind": "revolute", "axis": "+x", "source": "MJCF joint left_knee, range +/-90 deg"},
            {"at": "ankle", "kind": "revolute", "axis": "+x", "source": "MJCF joint left_ankle, range +/-90 deg; bearing 15x10x3"},
        ],
    }
