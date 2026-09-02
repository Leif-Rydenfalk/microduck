"""mech.py — mass, inertia, material, the joints this part offers.

Contract (TRIAD.md): `def mech() -> dict`. Numbers with sources, no adjectives.
A number nobody measured stays absent — never a plausible default.
"""


def mech():
    return {
        "slug": "microduck-hip-bracket",
        "material": "PLA",
        "volume_mm3": {"value": 4494.5, "source": "divergence-theorem volume of the built solid's mesh, cad-refcheck r2 compare.json 2026-09-02 (reference mesh: 4524.7, ratio 0.9933)"},
        "mass_g": {"value": None, "source": "the MJCF gives the whole hip_l BODY (bracket + pitch servo + bearing) as one inertial; the bracket alone is not published, and print mass depends on infill — ask ce-slice, never volume x density"},
        "joints": [
            {"at": "roll_horn", "kind": "revolute", "axis": "-y", "source": "MJCF joint left_hip_roll: hip_l body origin at mesh (17.5, -18.5, 0), axis along mesh -y"},
            {"at": "pitch_horn", "kind": "revolute", "axis": "+x", "source": "MJCF joint left_hip_pitch through mesh (42.5, 0, 0) along x; bearing 22x16x4 on the pitch boss"},
        ],
    }
