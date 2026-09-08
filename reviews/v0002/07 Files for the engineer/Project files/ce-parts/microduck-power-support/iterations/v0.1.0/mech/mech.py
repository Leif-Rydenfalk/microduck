"""mech.py — mass, inertia, material, the joints this part offers.

Contract (TRIAD.md): `def mech() -> dict`. Numbers with sources, no adjectives.
A number nobody measured stays absent — never a plausible default.
"""


def mech():
    return {
        "slug": "microduck-power-support",
        "material": "PLA",
        "volume_mm3": {"value": None, "source": "read it off the build: bin/cad part:microduck-power-support prints the MEASURED volume (refcheck volume ratio ours/ref 1.03 — the reference is decimated and its ridges/drafts are approximated)"},
        "mass_g": {"value": None, "source": "the MJCF gives the whole trunk_base BODY as 199.2 g; the cradle alone is not published"},
        "joints": [
            {"at": "battery_bay", "kind": "snap", "axis": "-z", "source": "the latch tongue (x ±5, 1.06 mm thick, 13.3 mm free length from z -12.9 to -26.2) flexes in y to let the cell past its 1.4:1 ramp; stiffness CANNOT DETERMINE — no PLA modulus measured for this print"},
        ],
    }
