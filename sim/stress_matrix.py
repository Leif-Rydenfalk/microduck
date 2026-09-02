#!/usr/bin/env python3
"""stress_matrix.py — the full structural simulation matrix for the Microduck.

Beyond the single standing case, this runs:
  * 3 LOAD CASES per structural part  (standing / 3g landing / lateral)
  * a MESH-SIZE FALLBACK so a part gmsh refuses at the default size still solves
  * a MESH CONVERGENCE check on the governing part (SF must be stable vs size)
  * a MATERIAL SWEEP on the governing part (PLA / PETG / ABS / NYLON / ASA)

LOAD BASIS. Robot mass 737 g -> weight 7.23 N. Two-legged stance = 3.6 N/leg.
Slow-walk single-stance peak ~1.3x bodyweight = 9.4 N. Cases:
  standing  20 N  — 2x over the walk peak, the design load
  landing   60 N  — 3x bodyweight on ONE leg, a step-off/drop event
  lateral   15 N  — side load, balance recovery / knock-over
All static, first-order, linear elastic. Not a gait-dynamics or fatigue study.

Run: ce-cad/bin/cad ce-designs/microduck/sim/stress_matrix.py
"""
import json, os, traceback

from cecad.core import Assembly  # noqa: F401  ensures kernel import path
import cecad.triad as triad
from cecad.stress import check_load
import FreeCAD

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "out", "stress")
os.makedirs(OUT, exist_ok=True)
os.environ.setdefault("CE_TRIAD_ROOT",
                      REPO + os.pathsep + os.path.expanduser("~/dev/ce-workshop"))

# part -> (fixed connector, loaded connector, what it carries)
PARTS = {
    "microduck-shin":            ("knee", "ankle",
                                  "carries the stance load from knee to ankle"),
    "microduck-upper-leg-left":  ("hip_pitch_axle", "knee_axle",
                                  "thigh: hip pitch axle down to the knee axle"),
    "microduck-ankle-left":      ("bearing_seat", "horn_face",
                                  "ankle bracket: bearing seat to servo horn face"),
    "microduck-hip-bracket":     ("roll_boss", "pitch_boss",
                                  "hip bracket: roll boss to pitch boss"),
}
CASES = {                     # name -> (force vector N, why)
    "standing": ((0, 0, -20.0), "2x over the 9.4 N slow-walk single-leg peak"),
    "landing":  ((0, 0, -60.0), "3x bodyweight on one leg — step-off / drop"),
    "lateral":  ((0, 15.0, 0.0), "side load: balance recovery / knock-over"),
}
SIZES = [None, 2.0, 1.5, 1.2, 1.0, 0.8]        # gmsh characteristic length fallback
MATERIALS = ["PLA", "PETG", "ABS", "NYLON", "ASA"]


def report_dict(rep):
    """Everything numeric the LoadReport exposes — attribute names vary."""
    d = {}
    for a in dir(rep):
        if a.startswith("_"):
            continue
        try:
            v = getattr(rep, a)
        except Exception:
            continue
        if isinstance(v, (int, float, str, bool)) and not callable(v):
            d[a] = v
    return d


def run(slug, case_name, force, why, material="PLA", size=None):
    """One solve. Returns a record; never raises."""
    doc = FreeCAD.newDocument("%s_%s_%s" % (slug, case_name, material))
    rec = {"part": slug, "case": case_name, "material": material,
           "force_N": list(force), "why": why, "mesh_size": size}
    try:
        part = triad.load(doc, "part:" + slug)
    except Exception as e:
        rec.update(verdict="CANNOT DETERMINE", reason="build failed: %s" % e)
        return rec
    part.material = material
    fixed, load, _ = PARTS[slug]
    cons = list(getattr(part, "_connectors", {}).keys())
    rec["connectors"] = cons
    if fixed not in cons or load not in cons:
        rec.update(verdict="CANNOT DETERMINE",
                   reason="connectors %s/%s absent (have %s)" % (fixed, load, cons))
        return rec
    try:
        part.load_case(case_name, fixed=fixed, load=load, force=force,
                       require_sf=2.0, why=why)
        rep = check_load(part, case=case_name, size=size,
                         workdir=os.path.join(OUT, "%s_%s_%s" % (slug, case_name, material)),
                         verbose=False, accept_class=True)
    except Exception as e:
        rec.update(verdict="CANNOT DETERMINE", reason=str(e)[:400])
        return rec
    rec.update(report_dict(rep))
    rec.setdefault("verdict", str(bool(rep)))
    return rec


def run_with_fallback(slug, case_name, force, why, material="PLA"):
    """Try successive gmsh sizes until one meshes. Records what worked."""
    tried = []
    for size in SIZES:
        rec = run(slug, case_name, force, why, material, size)
        tried.append({"size": size, "verdict": rec.get("verdict"),
                      "reason": rec.get("reason", "")[:120]})
        if rec.get("verdict") not in (None, "CANNOT DETERMINE"):
            rec["mesh_fallback"] = tried
            return rec
        if "gmsh" not in str(rec.get("reason", "")):
            rec["mesh_fallback"] = tried          # not a mesh problem — stop
            return rec
    rec["mesh_fallback"] = tried
    return rec


def main():
    results, log = [], []

    print("=" * 78)
    print("PASS 1 — every structural part, every load case, PLA")
    print("=" * 78)
    for slug, (_f, _l, what) in PARTS.items():
        for case_name, (force, why) in CASES.items():
            print("  %-28s %-9s %s" % (slug, case_name, force))
            r = run_with_fallback(slug, case_name, force, "%s; %s" % (what, why))
            sf = r.get("sf")
            print("      -> %-18s SF=%s  mesh=%s" % (
                r.get("verdict"), ("%.3f" % sf) if isinstance(sf, float) else sf,
                r.get("mesh_size")))
            results.append(r)

    ok = [r for r in results if isinstance(r.get("sf"), float)]
    governing = min(ok, key=lambda r: r["sf"]) if ok else None

    conv, mats = [], []
    if governing:
        g = governing["part"]
        gc = governing["case"]
        force, why = CASES[gc]
        print("\n" + "=" * 78)
        print("PASS 2 — mesh convergence on the governing case: %s / %s (SF %.3f)"
              % (g, gc, governing["sf"]))
        print("=" * 78)
        for size in (2.0, 1.5, 1.0):
            r = run(g, gc, force, why, "PLA", size)
            sf = r.get("sf")
            print("  size %-5s -> SF=%s" % (size, ("%.3f" % sf) if isinstance(sf, float) else r.get("verdict")))
            conv.append({"size": size, "sf": sf, "verdict": r.get("verdict")})

        print("\n" + "=" * 78)
        print("PASS 3 — material sweep on %s / %s" % (g, gc))
        print("=" * 78)
        for m in MATERIALS:
            r = run_with_fallback(g, gc, force, why, m)
            sf = r.get("sf")
            print("  %-7s -> %-18s SF=%s" % (m, r.get("verdict"),
                  ("%.3f" % sf) if isinstance(sf, float) else "-"))
            mats.append({"material": m, "sf": sf, "verdict": r.get("verdict")})

    out = {
        "generated": "2026-09-02",
        "tool": "cecad.stress — gmsh quadratic tets (C3D10) + CalculiX, linear elastic static",
        "load_basis": ("737 g robot -> 7.23 N weight; 3.6 N/leg standing; ~9.4 N slow-walk "
                       "single-stance peak. standing=20 N (2x margin), landing=60 N (3x "
                       "bodyweight one leg), lateral=15 N. Static first-order."),
        "limits": ("Linear elastic, isotropic — FDM parts are anisotropic and weaker across "
                   "layers, so treat these as upper bounds unless the part is printed with "
                   "the load in-plane. No fatigue, no creep, no impact dynamics."),
        "cases": {k: {"force_N": list(v[0]), "why": v[1]} for k, v in CASES.items()},
        "results": results,
        "governing": ({"part": governing["part"], "case": governing["case"],
                       "sf": governing["sf"]} if governing else None),
        "mesh_convergence": conv,
        "material_sweep": mats,
    }
    json.dump(out, open(os.path.join(OUT, "matrix.json"), "w"), indent=1)

    print("\n" + "=" * 78)
    print("SUMMARY")
    print("=" * 78)
    print("%-28s %-9s %-9s %-18s %s" % ("part", "case", "SF", "verdict", "mesh"))
    for r in results:
        sf = r.get("sf")
        print("%-28s %-9s %-9s %-18s %s" % (
            r["part"], r["case"], ("%.3f" % sf) if isinstance(sf, float) else "-",
            r.get("verdict"), r.get("mesh_size")))
    if governing:
        print("\nGOVERNING: %s / %s at SF %.3f" % (governing["part"], governing["case"], governing["sf"]))
    print("\nwrote", os.path.join(OUT, "matrix.json"))


if __name__ == "__main__":
    main()
