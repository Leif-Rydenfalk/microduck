"""mech.py — mass, volume, material. Numbers with sources, no adjectives.

Contract (TRIAD.md): `def mech() -> dict`.
"""


def mech():
    return {
        "slug": 'microduck-foot-left',
        "material": 'PLA',
        "volume_mm3": {"value": None, "source": "read it off the build: bin/cad part:microduck-foot-left prints the MEASURED volume"},
        "mass_g": {"value": None, "source": "the MJCF gives only the WHOLE body 'ankle_left' inertial mass (30.025 g: ankle bracket + servo + foot + sole); this mesh alone is not published"},
        "joints": [],
    }
