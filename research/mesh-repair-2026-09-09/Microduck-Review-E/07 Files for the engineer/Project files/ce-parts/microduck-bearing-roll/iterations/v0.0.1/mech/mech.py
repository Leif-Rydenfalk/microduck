"""mech.py — mass, inertia, material, the joints this part offers.

Contract (TRIAD.md): `def mech() -> dict`. Numbers with sources, no adjectives.
A number nobody measured stays absent — never a plausible default.
"""


def mech():
    return {
        "slug": "microduck-bearing-roll",
        "material": "PLA",
        "volume_mm3": {"value": 625.0, "source": "cecad.meshcompare on the built STL, refcheck r1 2026-09-01 (out/refcheck/bearing-roll/r1/compare.json volume_cand_mm3); Pollen's decimated mesh reads 625.3 (ratio 0.9995)"},
        "mass_g": {"value": None, "source": "the MJCF gives the whole `yaw2roll` BODY (yaw2roll link + this plate + the hip-roll XL330 + a 22x16x4 bearing) as 23.513 g (kin_robot_walk.xml inertial); the plate alone is not published. 625 mm3 of PLA at 1.24 g/cm3 would be 0.8 g solid; a printed figure needs ce-slice"},
        "thickness_mm": {"value": 1.0, "source": "cad-mjcf sections --axis z: y range -14.5..-13.5 at every z except the pegs"},
        "joints": [
            {"at": "roll_bearing_face", "kind": "revolute (thrust face only)", "axis": "-y (mesh) = world +x", "source": "MJCF joint left_hip_roll, world axis (1, 0, 0), range +/-22 deg; axis line (17.5, y, 0) in this frame. This plate is fixed to the servo body; the 22x16x4 bearing's outer race face runs on its back face (y -14.5) — see interfaces.json roll_bearing_face"},
        ],
    }
