"""mech.py — mass, inertia, material, the joints this part offers.

Contract (TRIAD.md): `def mech() -> dict`. Numbers with sources, no adjectives.
A number nobody measured stays absent — never a plausible default.
"""


def mech():
    return {
        "slug": "microduck-neck-pitch-bracket",
        "material": "PLA",
        "volume_mm3": {"value": 4106.8, "source": "divergence-theorem volume of the built solid's mesh, cad-refcheck r1 compare.json 2026-09-02 (reference mesh: 4106.7, ratio 1.0000)"},
        "mass_g": {"value": None, "source": "the MJCF gives the whole neck_pitch BODY (bracket + head-yaw servo) as one 5.72 g inertial; the bracket alone is not published, and print mass depends on infill — ask ce-slice, never volume x density"},
        "joints": [
            {"at": "pitch_horn_right", "kind": "revolute", "axis": "+x", "source": "MJCF joint head_pitch: neck -> neck_pitch at (26, 14.5, 202.4) axis +y world; the pitch axis is mesh x through (0, 0, -28.793)"},
            {"at": "yaw_horn_top", "kind": "revolute", "axis": "+z", "source": "MJCF joint head_yaw: neck_pitch -> yaw_roll_motion at (26, 0, 221.1) axis +z; the yaw axis is mesh z through (0, 0), horn face z -10.1"},
        ],
    }
