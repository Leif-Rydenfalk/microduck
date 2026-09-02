"""mech.py — mass, inertia, material, the joints this part offers.

Contract (TRIAD.md): `def mech() -> dict`. Numbers with sources, no adjectives.
A number nobody measured stays absent — never a plausible default.
"""


def mech():
    return {
        "slug": "microduck-yaw-roll-motion",
        "material": "PLA",
        "volume_mm3": {"value": 4632.7, "source": "divergence-theorem volume of the built solid's mesh, cad-refcheck r1 compare.json 2026-09-02 (sim reference mesh: 4563.9, ratio 1.0151 — the sparse sim mesh under-counts the features it cannot resolve)"},
        "mass_g": {"value": None, "source": "the MJCF gives the whole yaw_roll_motion BODY (cage + head-yaw servo) as one 48.6 g inertial; the printed cage alone is not published, and print mass depends on infill — ask ce-slice, never volume x density"},
        "joints": [
            {"at": "yaw_servo_case", "kind": "revolute", "axis": "-z", "source": "MJCF joint head_yaw: neck_pitch -> yaw_roll_motion axis +z; the yaw servo hangs under the top plate, horn down onto neck_pitch (yaw axis mesh z through (0,0))"},
            {"at": "roll_horn", "kind": "revolute", "axis": "+y", "source": "MJCF joint head_roll: yaw_roll_motion -> head at body -x = mesh +y; roll axis mesh y through (x 0, z 4.5), horn face y 17.9, bearing boss face y -18"},
        ],
    }
