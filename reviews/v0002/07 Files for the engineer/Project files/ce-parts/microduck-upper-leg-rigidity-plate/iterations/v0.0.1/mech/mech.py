"""mech.py — mass, inertia, material, the joints this part offers.

Contract (TRIAD.md): `def mech() -> dict`. Numbers with sources, no adjectives.
"""


def mech():
    return {
        "slug": "microduck-upper-leg-rigidity-plate",
        "material": "PLA",
        "volume_mm3": {"value": None, "source": "read it off the build: cecad.meshcompare volume_cand_mm3 in the PASS refcheck's compare.json (evidence/refcheck/<stamp>/); Pollen's decimated mesh reads 747.8"},
        "mass_g": {"value": None, "source": "not published; the MJCF's 48.2 g is the whole upper_leg body. ~750 mm3 of PLA at 1.24 g/cm3 is ~0.9 g solid"},
        "thickness_mm": {"value": 1.0, "source": "meshslice x-ray probes: (42.5, 43.5) at every sampled (y, z); bbox x 1.0"},
        "joints": [],
        "note": "A stiffening plate: it offers no joint of its own. Its two Ø19 windows are clearance around the hip-pitch and knee axes (the XL330 horn side), not seats — Ø19 is smaller than the 22 mm bearing OD and larger than the 15.9 horn disc measured on the shin.",
    }
