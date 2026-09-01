"""mech.py — mass, inertia, material, the joints this part offers.

Contract (TRIAD.md): `def mech() -> dict`. Numbers with sources, no adjectives.
"""


def mech():
    return {
        "slug": "microduck-upper-leg-right",
        "material": "PLA",
        "volume_mm3": {"value": 3837.3, "source": "cecad.meshcompare on the built STL, refcheck r1 2026-09-01 (compare.json volume_cand_mm3) — identical to the left, as a mirror must be; Pollen's decimated mesh reads 4150.0"},
        "mass_g": {"value": None, "source": "the MJCF gives the whole `upper_leg_right` BODY (housing + two XL330s + plate) as 48.2 g; the housing alone is not published"},
        "wall_mm": {"value": 1.0, "source": "measured on the left (meshslice probes A/C/D/L); the right is its exact x-mirror (0.0000 mm, 6123 vertices)"},
        "joints": [
            {"at": "hip_pitch_axle", "kind": "revolute", "axis": "-x", "source": "MJCF joint right_hip_pitch, range +/-90 deg; servo axis A0 (y 0, z 0)"},
            {"at": "knee_axle", "kind": "revolute", "axis": "-x", "source": "MJCF joint right_knee, range +/-90 deg; servo axis A1 (y 22, z 35.777), 42.000 mm from A0"},
        ],
    }
