"""mech.py — mass, material, joints of part:microduck-trunk-shell-right.

Contract (TRIAD.md): `def mech() -> dict`. Numbers with sources, no adjectives.
"""


def mech():
    return {
        "slug": "microduck-trunk-shell-right",
        "material": "PLA",
        "volume_mm3": {"value": None, "source": "read it off the build: bin/cad part:microduck-trunk-shell-right prints the MEASURED volume"},
        "mass_g": {"value": None, "source": "not published: the MJCF gives trunk_base (the whole trunk body incl. both shells, plate, battery cradle) as 199.2 g; the shell alone is not separable from it"},
        "joints": [
            {"at": "neck_horn", "kind": "revolute", "axis": "+x", "source": "MJCF joint neck_pitch at world (26, 14.5, 152.4), axis -y == mesh +x on this side after the geom quat; range -90..+60 deg"},
        ],
        "fasteners": [
            {"at": "base_screw", "kind": "M2 self-tapping into the D2.2 pilot", "source": "meshfeatures hole D2.2 axis -z at (-25.5,-9.5,41.53); community hole analysis reads the robot as an M2 system (SPEC.md par.4)"},
            {"at": "cross_screw", "kind": "M2 tapped into this half's D1.6 pilot, driven through the left half", "source": "meshfeatures hole D1.6 at (-2.65,42,52.5) len 4.7"},
        ],
    }
