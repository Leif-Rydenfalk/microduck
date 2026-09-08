#!/usr/bin/env python3
"""build_radxa_holes.py — build part:radxa-zero-3w both ways and READ THE HOLES BACK.

part.py takes params {"holes": "mesh"|"radxa"}. After the 2026-09-03 correction
(the Radxa drill is built on Radxa's printed NOMINAL 3.600 mm inset, not on half
the raw raster-measured pitch) the two patterns must come back at

    radxa : (±28.900, ±11.400)      = 65.000/2 - 3.600, 30.000/2 - 3.600
    mesh  : (±29.000, ±11.500)      Pollen's Pi-Zero-2-W stand-in

and this file asserts exactly that against the BUILT SOLID's own connectors —
not against the constants it was built from.

MUST RUN UNDER FreeCAD's python:  ce-cad/bin/cad tools/build_radxa_holes.py
Out: out/measure/radxa-build-nominal-holes.json   exit 0 PASS / 1 FAIL
"""
import importlib.util
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PART = os.path.join(REPO, "ce-parts/radxa-zero-3w/iterations/v0.0.1/cad/part.py")

EXPECT = {
    "radxa": {"x": 28.900, "z": 11.400,
              "basis": "Radxa RAD-DOC-0084 Rev 1.10 §4 printed callouts: inset '3. 6' on '65. 0' x '30. 0'"},
    "mesh":  {"x": 29.000, "z": 11.500,
              "basis": "Pollen's pcb__raspberry_pi_zero_2_w.stl, cecad.meshfeatures"},
}
TOL = 1e-4   # mm — this is arithmetic on constants, not a measurement of ink


def _xyz(text):
    m = re.search(r"at \(([-\d.]+), ([-\d.]+), ([-\d.]+)\)", str(text))
    return tuple(float(g) for g in m.groups()) if m else None


def main():
    import FreeCAD
    spec = importlib.util.spec_from_file_location("radxa_part", PART)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    out, fails = {}, []
    for mode, exp in EXPECT.items():
        doc = FreeCAD.newDocument("d_" + mode)
        p = mod.build(doc, {"holes": mode})
        pts = {}
        for name, c in (getattr(p, "connectors", {}) or {}).items():
            v = _xyz(c)
            if v:
                pts[name] = [round(a, 4) for a in v]
        mounts = {k: v for k, v in pts.items() if k.startswith("mount_")}
        if len(mounts) != 4:
            fails.append("%s: built %d mount connectors, expected 4" % (mode, len(mounts)))
        for name, (x, y, z) in mounts.items():
            for axis, got, want in (("x", abs(x), exp["x"]), ("z", abs(z), exp["z"])):
                if abs(got - want) > TOL:
                    fails.append("%s %s: %s = %.4f, expected %.4f (delta %.4f mm)"
                                 % (mode, name, axis, got, want, got - want))
        out[mode] = {"expected_abs_mm": {"x": exp["x"], "z": exp["z"]},
                     "expected_basis": exp["basis"],
                     "connectors_mm": pts}
        FreeCAD.closeDocument(doc.Name)

    res = {
        "$about": "part:radxa-zero-3w built both ways; hole centres read off the BUILT solid's connectors.",
        "made": "2026-09-03",
        "made_by": "tools/build_radxa_holes.py under ce-cad/bin/cad (FreeCAD python)",
        "tolerance_mm": TOL,
        "tolerance_basis": ("1e-4 mm: these are constants propagated through arithmetic, not a "
                            "measurement. The POSITIONAL uncertainty of the Radxa pattern itself is "
                            "±0.0396 mm (1 sigma of the eight raster-measured edge insets) and lives "
                            "in cad/interfaces.json, not here."),
        "results": out,
        "failures": fails,
        "verdict": "FAIL" if fails else "PASS",
    }
    path = os.path.join(REPO, "out/measure/radxa-build-nominal-holes.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(res, fh, indent=1)
        fh.write("\n")
    print(json.dumps(res, indent=1))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
