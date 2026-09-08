"""mech.py — mass, inertia, material, the joints this part offers.

Contract (TRIAD.md): `def mech() -> dict`. Numbers with sources, no adjectives.
"""


def mech():
    return {
        "slug": "microduck-upper-leg-left",
        "material": "PLA",
        "volume_mm3": {"value": 3837.3, "source": "cecad.meshcompare on the built STL, refcheck r1 2026-09-01 (compare.json volume_cand_mm3); Pollen's decimated mesh reads 4149.7 — the 7.5% gap is their sub-mm inner fillets we do not model"},
        "mass_g": {"value": None, "source": "the MJCF gives the whole `upper_leg_left` BODY (housing + two XL330s + plate) as 48.2 g; the housing alone is not published. 3837 mm3 of PLA at 1.24 g/cm3 would be 4.8 g solid-infill; a printed figure needs ce-slice"},
        "wall_mm": {"value": 1.0, "source": "meshslice ray probes A/C/D/L: plate 69.5..70.5, rim 1.00-1.04, side wall 1.001, flange 1.002"},
        "joints": [
            {"at": "hip_pitch_axle", "kind": "revolute", "axis": "+x", "source": "MJCF joint left_hip_pitch, range +/-90 deg; servo axis A0 (y 0, z 0)"},
            {"at": "knee_axle", "kind": "revolute", "axis": "+x", "source": "MJCF joint left_knee, range +/-90 deg; servo axis A1 (y 22, z 35.777), 42.000 mm from A0"},
        ],
    }
