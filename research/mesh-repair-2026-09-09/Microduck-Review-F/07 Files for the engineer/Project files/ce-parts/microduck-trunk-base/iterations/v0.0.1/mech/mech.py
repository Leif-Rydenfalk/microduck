"""mech.py — mass, inertia, material, the joints this part offers.

Contract (TRIAD.md): `def mech() -> dict`. Numbers with sources, no adjectives.
A number nobody measured stays absent — never a plausible default.
"""


def mech():
    return {
        "slug": "microduck-trunk-base",
        "material": "PLA",
        "volume_mm3": {"value": None, "source": "read it off the build: bin/cad part:microduck-trunk-base prints the MEASURED volume (refcheck volume ratio ours/ref 0.9996)"},
        "mass_g": {"value": None, "source": "the MJCF gives the whole trunk_base BODY (plate + shells + battery + servos) as 199.2 g; the plate alone is not published"},
        "joints": [
            {"at": "hip_yaw_left", "kind": "revolute", "axis": "-z", "source": "MJCF joint left_hip_yaw, range -25..+30 deg, axis through the Ø19 hole"},
            {"at": "hip_yaw_right", "kind": "revolute", "axis": "-z", "source": "MJCF joint right_hip_yaw, mirror"},
        ],
    }
