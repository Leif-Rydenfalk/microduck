"""mech.py — mass, volume, material. Numbers with sources, no adjectives.

Contract (TRIAD.md): `def mech() -> dict`.
"""


def mech():
    return {
        "slug": 'microduck-sole-left',
        "material": 'TPU',
        "volume_mm3": {"value": None, "source": "read it off the build: bin/cad part:microduck-sole-left prints the MEASURED volume"},
        "mass_g": {"value": None, "source": "the MJCF gives only the WHOLE body 'ankle_left' inertial mass (30.025 g: ankle bracket + servo + foot + sole); this mesh alone is not published"},
        "joints": [],
        "contact": {"value": "ground contact geom (the MJCF collision geom for this side is this mesh)", "source": "pollen-microduck-rl scene.xml"},
    }
