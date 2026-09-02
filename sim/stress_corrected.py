#!/usr/bin/env python3
"""stress_corrected.py — re-solve the leg at a load basis that survives arithmetic.

CORRECTION. sim/stress_matrix.py labelled its landing case "3x bodyweight on one
leg" and applied 60 N. The robot is 737 g -> 7.230 N, so 3x bodyweight is
21.690 N. 60 N is 8.30x bodyweight. Every "ankle FAILS in every material"
result rests on that mis-specified load.

Linear elasticity says the safety factor scales inversely with load, so the
corrected figure is predictable — but a prediction is not a measurement, so
each corrected case is SOLVED here rather than scaled, and the two are printed
side by side. If they disagree, the scaling assumption is wrong and the solve
wins.

LOAD BASIS, stated so the next reader can check the arithmetic:
    mass 737 g -> weight 0.737 * 9.81 = 7.230 N
    two-legged stance                   3.615 N per leg
    slow-walk single-stance peak 1.3x   9.399 N
    standing  20.000 N = 2.13x the walk peak   (design load, unchanged)
    landing   21.690 N = 3.00x bodyweight      (CORRECTED from 60 N)
    lateral   15.000 N = 2.07x bodyweight sideways
A genuine drop/impact load is CANNOT DETERMINE here: peak force depends on drop
height and contact compliance, and this is a static linear solver with no impact
model. 3x bodyweight is the walking-robot design figure, not a drop.
"""
import json, os

from cecad.core import Assembly  # noqa: F401
import cecad.triad as triad
from cecad.stress import check_load
import FreeCAD

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "out", "stress")
os.makedirs(OUT, exist_ok=True)
os.environ.setdefault("CE_TRIAD_ROOT",
                      REPO + os.pathsep + os.path.expanduser("~/dev/ce-workshop"))

W = 0.737 * 9.81
PARTS = {
    "microduck-shin":           ("knee", "ankle"),
    "microduck-ankle-left":     ("bearing_seat", "horn_face"),
    "microduck-hip-bracket":    ("roll_boss", "pitch_boss"),
}
CASES = {
    "standing": (20.0,  "2.13x the 9.399 N slow-walk single-stance peak"),
    "landing":  (3 * W, "3.00x bodyweight on one leg — CORRECTED from 60 N"),
    "lateral":  (15.0,  "2.07x bodyweight sideways — balance recovery"),
}
# measured at 20 N in out/stress/matrix.json, for the scaling cross-check
SF_AT_20N = {"microduck-shin": 7.510634459976798,
             "microduck-ankle-left": 2.0210281854992354,
             "microduck-hip-bracket": 6.424036301436047}


def run(slug, case, force_n, why):
    doc = FreeCAD.newDocument("%s_%s" % (slug, case))
    rec = {"part": slug, "case": case, "force_N": round(force_n, 4), "why": why,
           "load_x_bodyweight": round(force_n / W, 3)}
    try:
        part = triad.load(doc, "part:" + slug)
    except Exception as e:                                      # noqa: BLE001
        rec.update(verdict="CANNOT DETERMINE", reason=str(e)[:200]); return rec
    part.material = "PLA"
    fixed, load = PARTS[slug]
    vec = (0, 0, -force_n) if case != "lateral" else (0, force_n, 0)
    try:
        part.load_case(case, fixed=fixed, load=load, force=vec,
                       require_sf=2.0, why=why)
        rep = check_load(part, case=case,
                         workdir=os.path.join(OUT, "corr_%s_%s" % (slug, case)),
                         verbose=False, accept_class=True)
    except Exception as e:                                      # noqa: BLE001
        rec.update(verdict="CANNOT DETERMINE", reason=str(e)[:200]); return rec
    for a in ("verdict", "sf", "max_von_mises_mpa", "max_displacement_mm"):
        v = getattr(rep, a, None)
        if v is not None:
            rec[a] = v
    rec.setdefault("verdict", str(bool(rep)))
    base = SF_AT_20N.get(slug)
    if base and isinstance(rec.get("sf"), float):
        pred = base * 20.0 / force_n
        rec["sf_predicted_by_scaling"] = round(pred, 4)
        rec["scaling_error_pct"] = round((rec["sf"] / pred - 1) * 100, 3)
    return rec


def main():
    print("LOAD BASIS  weight %.3f N   3x bodyweight = %.3f N   (was 60 N = %.2fx)"
          % (W, 3 * W, 60.0 / W))
    print("=" * 78)
    res = []
    for slug in PARTS:
        for case, (f, why) in CASES.items():
            r = run(slug, case, f, why)
            sf = r.get("sf")
            print("%-26s %-9s %6.2f N  SF %-8s %-16s scaling %s"
                  % (slug, case, r["force_N"],
                     ("%.3f" % sf) if isinstance(sf, float) else "-",
                     r.get("verdict"),
                     ("%+.2f%%" % r["scaling_error_pct"]) if "scaling_error_pct" in r else "-"))
            res.append(r)
    out = {"generated": "2026-09-03",
           "supersedes": "out/stress/matrix.json landing case (60 N, mislabelled 3x bodyweight)",
           "weight_N": round(W, 4),
           "correction": ("matrix.json's landing case applied 60 N while calling it "
                          "3x bodyweight; 3x bodyweight is 21.690 N. 60 N is 8.30x "
                          "bodyweight. Every 'ankle FAILS in every material' result "
                          "came from that mis-specified load."),
           "load_basis": {k: {"N": round(v[0], 4), "x_bodyweight": round(v[0] / W, 3),
                              "why": v[1]} for k, v in CASES.items()},
           "impact_note": ("a genuine drop/impact load is CANNOT DETERMINE: peak force "
                           "depends on drop height and contact compliance, and this is a "
                           "static linear solver with no impact model"),
           "results": res}
    json.dump(out, open(os.path.join(OUT, "corrected.json"), "w"), indent=1)
    print("\nwrote out/stress/corrected.json")


if __name__ == "__main__":
    main()
