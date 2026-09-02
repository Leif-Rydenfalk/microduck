#!/usr/bin/env python3
"""stress_evidence.py — real FEA on the load-bearing parts. Leif, 2026-09-02:
"have you ran material simulations and stress tests? run more simulations."

Runs cecad.stress (gmsh mesh + CalculiX static solve) on the structural leg
links in PLA, under a stated standing/walking load, and compiles the evidence:
safety factor, peak von Mises, max deflection, and the FEA field image, into
out/stress/report.json + a per-part ledger.

LOAD BASIS (stated, not hidden). Robot mass 737 g -> weight 7.23 N. Standing on
two legs = 3.6 N per leg (compression through the links). Slow-walk peak
vertical ground reaction on a single stance leg ~= 1.3x bodyweight = 9.4 N. A
2x design factor over that peak gives ~= 19 N; we use a round DESIGN LOAD of
20 N per structural link, applied at the distal joint with the proximal joint
held. This is a first-order static case, not a gait dynamics study.

Run with FreeCAD's python via bin/cad (needs the kernel + gmsh/ccx):
    ce-cad/bin/cad ce-designs/microduck/sim/stress_evidence.py
"""
import json
import os

from cecad.core import Assembly  # noqa: F401  (ensures kernel import path)
import cecad.triad as triad
from cecad.stress import check_load
import FreeCAD

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "out", "stress")
os.makedirs(OUT, exist_ok=True)
os.environ.setdefault("CE_TRIAD_ROOT", REPO + os.pathsep + os.path.expanduser("~/dev/ce-workshop"))

DESIGN_LOAD_N = 20.0  # per structural link, see LOAD BASIS
# part -> (fixed connector, loaded connector, force vector N, why)
CASES = {
    "microduck-shin": ("knee", "ankle", (0, 0, -DESIGN_LOAD_N),
                       "shin carries the standing/walking load from the knee down to the ankle"),
    "microduck-upper-leg-left": None,   # filled below once connectors are known
    "microduck-ankle-left": None,
    "microduck-hip-bracket": None,
}


def connectors_of(part):
    return list(getattr(part, "_connectors", {}).keys())


def run_one(slug):
    doc = FreeCAD.newDocument(slug)
    try:
        part = triad.load(doc, "part:" + slug)
    except Exception as e:  # noqa: BLE001
        return {"slug": slug, "verdict": "CANNOT DETERMINE", "why": "build failed: %s" % e}
    part.material = "PLA"
    cons = connectors_of(part)
    spec = CASES.get(slug)
    if spec is None:
        if len(cons) < 2:
            return {"slug": slug, "verdict": "CANNOT DETERMINE",
                    "why": "fewer than two connectors to fix/load (%s)" % cons, "connectors": cons}
        spec = (cons[0], cons[1], (0, 0, -DESIGN_LOAD_N),
                "standing/walking load from %s (held) to %s (loaded)" % (cons[0], cons[1]))
    fixed, load, force, why = spec
    if fixed not in cons or load not in cons:
        return {"slug": slug, "verdict": "CANNOT DETERMINE",
                "why": "connectors %s/%s not on the part (%s)" % (fixed, load, cons), "connectors": cons}
    try:
        part.load_case("standing", fixed=fixed, load=load, force=force, require_sf=2.0, why=why)
        rep = check_load(part, workdir=os.path.join(OUT, slug), verbose=False, accept_class=True)
    except Exception as e:  # noqa: BLE001
        return {"slug": slug, "verdict": "CANNOT DETERMINE", "why": "solve failed: %s" % e, "connectors": cons}
    d = {"slug": slug, "material": "PLA", "load_N": DESIGN_LOAD_N,
         "fixed": fixed, "loaded": load, "why": why, "connectors": cons}
    for attr in ("verdict", "sf", "max_von_mises_mpa", "max_displacement_mm", "image", "report_path"):
        v = getattr(rep, attr, None)
        if v is not None:
            d[attr] = v
    d["verdict"] = getattr(rep, "verdict", str(bool(rep)))
    d["summary"] = str(rep)[:400]
    return d


def main():
    results = []
    for slug in ("microduck-shin", "microduck-upper-leg-left", "microduck-ankle-left", "microduck-hip-bracket"):
        print("=== FEA", slug)
        r = run_one(slug)
        print("   ", r.get("verdict"), "SF", r.get("sf"), "vM", r.get("max_von_mises_mpa"), "MPa",
              "disp", r.get("max_displacement_mm"), "mm")
        results.append(r)
    out = {"generated": "2026-09-02", "tool": "cecad.stress (gmsh + CalculiX), PLA",
           "load_basis": "737 g robot; 20 N design load per structural link (2x over ~9.4 N slow-walk single-leg peak); static, first-order",
           "results": results}
    json.dump(out, open(os.path.join(OUT, "report.json"), "w"), indent=1)
    print("wrote", os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
