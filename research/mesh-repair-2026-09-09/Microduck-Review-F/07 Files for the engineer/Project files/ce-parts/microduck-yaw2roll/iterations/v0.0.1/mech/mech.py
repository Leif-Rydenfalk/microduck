"""mech.py — mass, inertia, material, the joints this part offers.

Contract (TRIAD.md): `def mech() -> dict`. Numbers with sources, no adjectives.
A number nobody measured stays absent — never a plausible default.
"""


def mech():
    return {
        "slug": "microduck-yaw2roll",
        "material": "PLA",
        "volume_mm3": {"value": 2831.4, "source": "cecad.meshcompare on the built STL, refcheck r2 2026-09-02 (out/refcheck/yaw2roll/r2/compare.json volume_cand_mm3); Pollen's decimated mesh reads 2816.1 (ratio 1.0055)"},
        "mass_g": {"value": None, "source": "the MJCF gives the whole `yaw2roll` BODY (this link + the bearing_roll plate + the hip-roll XL330 + a 22x16x4 bearing) as 23.513 g (kin_robot_walk.xml inertial); the link alone is not published. 2831 mm3 of PLA at 1.24 g/cm3 would be 3.5 g solid; a printed figure needs ce-slice"},
        "wall_mm": {"value": 1.4, "source": "meshfeatures.profile y-rays at z 5: material x 6.05..7.35 / 27.65..29 (the two side walls); plate 2.5 (z 9.5..12) from z-rays at (12, y)"},
        "joints": [
            {"at": "yaw_bearing_seat", "kind": "revolute", "axis": "-z (mesh) = world -z", "source": "MJCF joint left_hip_yaw / right_hip_yaw: body axis 0 0 1, world axis (0, 0, -1), range -25..+30 deg left (-30..+25 right); axis line (17.5, -2, z) in this frame, joint origin at mesh (17.5, -2, 12.5)"},
            {"at": "roll_idler", "kind": "revolute", "axis": "-y (mesh) = world +x", "source": "MJCF joint left_hip_roll (child body hip_l, quat 0.707 -0.707 0 0 relative to this body), world axis (1, 0, 0), range +/-22 deg; axis line (17.5, y, 0) in this frame"},
        ],
    }
