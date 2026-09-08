"""mech.py — mass, inertia, material, the joints this part offers.

Contract (TRIAD.md): `def mech() -> dict`. Numbers with sources, no adjectives.
A number nobody measured stays absent — never a plausible default.
"""


def mech():
    return {
        "slug": "microduck-banana-pcb-locker",
        "material": "PLA",
        "volume_mm3": {"value": None, "source": "read it off the build: bin/cad part:microduck-banana-pcb-locker prints the MEASURED volume (refcheck volume ratio ours/ref 0.9962)"},
        "mass_g": {"value": None, "source": "the MJCF gives the whole trunk_base BODY as 199.2 g; the bar alone is not published"},
        "joints": [],
    }
