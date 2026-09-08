#!/usr/bin/env python3
"""fea_rejudge.py — ONE grading rule, applied to EVERY FEA study on disk,
without re-solving (plain python3, no kernel). Rewrites only verdict / why /
outputs.grading; the solve outputs are untouched and every previous
(verdict, why) pair is kept under `rejudged_from`.

History. The 2026-09-02 version of this file re-graded exactly two parts
(rigidity plate, trunk base) from FAIL to CANNOT DETERMINE after their numbers
were known — the F1 skeptic (2026-09-03, finding 12) called that grading
asymmetric, and finding 10 noted that five studies report deflections far
outside the small-strain regime the document declares, with no consequence.
This version is the answer to both: the rule below is written once, reads its
inputs from declarations (sim/load_share.py) and measurements (the deck's own
node coordinates, the study's own displacement, the nonlinear re-solve when it
exists), and is applied to all 32 studies in the same loop.

THE RULE
  1. SF = the more conservative of SF against the class-table yield and SF
     against the fetched TDS yield. SF >= 2 PASS, else FAIL.       (unchanged)
  2. Regime. From the deck's node bbox (t <= mid <= L): a PLATE if t/mid <=
     0.15. The linear solve is a prediction while delta <= t/2 (plate) and
     delta <= L/10 (any part); outside that it is a BOUND. A study outside
     the regime keeps rule 1's verdict on the linear number ONLY until a
     converged geometrically nonlinear re-solve exists (sim/fea_nlgeom.py);
     then the verdict is taken on the nonlinear peak and both are printed.
     Inside the regime both are predictions and the MORE CONSERVATIVE of the
     two carries the verdict (the shin's lateral+axial landing load is a
     beam-column: its nonlinear peak is 1.18x the linear one).
     A study outside the regime with no nonlinear answer is graded on the
     linear bound and SAYS SO in its why — a FAIL it stays, because a peak
     6x past yield does not come back inside yield by the geometric effect
     alone, and the nonlinear run is what measures that.
  3. Share. A study whose part is declared in sim/load_share.py carries 100 %
     of a force it shares in PARALLEL with a body not in the model. PASS at
     100 % is PASS; FAIL at 100 % is CANNOT DETERMINE with the bound printed.
     Every other part is the SOLE member between its connectors and its
     single-part solve IS the load path.
  4. report.json beside each deck (cecad.feaimage's input, whose verdict is
     painted onto the PNG caption) is synced to the final verdict, so the
     picture and the table cannot disagree (finding 11); the PNGs whose
     caption changed are listed in out/sim-evidence/fea/rerender.txt for
     sim/fea_render.py (needs the kernel).

    python3 sim/fea_rejudge.py            re-grade every study, print the changes
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EVID = os.path.join(ROOT, "out", "sim-evidence")
FEA = os.path.join(EVID, "fea")
sys.path.insert(0, HERE)
from load_share import LOAD_SHARE  # noqa: E402

REQUIRE_SF = 2.0
PLATE_ASPECT = 0.15
PLATE_W_OVER_T = 0.5
MEMBER_D_OVER_L = 0.1
RULE_TEXT = ("SF = min(table, TDS) >= 2; plate if t/mid <= 0.15; linear regime valid while d <= t/2 (plate) and d <= L/10 (all); "
             "outside the regime a converged NLGEOM re-solve (sim/fea_nlgeom.py) carries the verdict when it exists; a declared parallel load share "
             "(sim/load_share.py) turns FAIL into CANNOT DETERMINE with the bound printed")


def bbox_of_inp(path):
    mn, mx, innode = [1e9] * 3, [-1e9] * 3, False
    for line in open(path):
        if line.startswith("*"):
            innode = line.upper().startswith("*NODE")
            continue
        if innode:
            f = line.split(",")
            if len(f) >= 4:
                try:
                    c = [float(f[1]), float(f[2]), float(f[3])]
                except ValueError:
                    continue
                for j in range(3):
                    mn[j] = min(mn[j], c[j]); mx[j] = max(mx[j], c[j])
    return sorted(round(mx[j] - mn[j], 4) for j in range(3))


def regime(bbox, disp):
    t, mid, L = bbox
    plate = (t / mid) <= PLATE_ASPECT
    d_t, d_L = disp / t, disp / L
    valid = d_L <= MEMBER_D_OVER_L and (not plate or d_t <= PLATE_W_OVER_T)
    return {"bbox_sorted_mm": bbox, "plate": plate, "d_over_t": round(d_t, 4), "d_over_L": round(d_L, 4), "linear_regime_valid": valid,
            "rule": "plate if t/mid <= %g; valid while d/t <= %g (plate) and d/L <= %g" % (PLATE_ASPECT, PLATE_W_OVER_T, MEMBER_D_OVER_L)}


def grade(r):
    o = r.get("outputs") or {}
    if o.get("sf") is None:
        return None
    slug = r["part"].split(":", 1)[1]
    wd = os.path.join(ROOT, r["artifacts"][0])
    inp = glob.glob(os.path.join(wd, "*_mesh.inp"))
    reg = regime(bbox_of_inp(inp[0]), o["max_displacement_mm"]) if inp else {"linear_regime_valid": None, "note": "no mesh deck on disk"}
    y_table = o.get("yield_mpa_used")
    sf_table, sf_tds = o["sf"], o.get("sf_vs_tds_yield")
    sf_lin = min(x for x in (sf_table, sf_tds) if x is not None)
    basis_lin = "table" if sf_lin == sf_table else "TDS"
    # the nonlinear re-solve, when it exists and converged
    nl_path = os.path.join(EVID, "fea_nlgeom_%s.json" % r["study"][4:])
    nl = json.load(open(nl_path)) if os.path.exists(nl_path) else None
    nlo = (nl or {}).get("outputs") or {}
    nl_ok = bool(nl) and nl.get("verdict") in ("PASS", "FAIL") and nlo.get("max_von_mises_mpa")
    grading = {"rule": RULE_TEXT, "sf_table": sf_table, "sf_tds": sf_tds, "sf_linear_governing": round(sf_lin, 6), "basis": basis_lin, "regime": reg,
               "load_share": LOAD_SHARE.get(slug), "nonlinear_study": os.path.relpath(nl_path, ROOT) if nl else None}
    sf_used, model = sf_lin, "linear"
    if nl_ok:
        vm_nl = nlo["max_von_mises_mpa"]
        sf_nl_table = (y_table / vm_nl) if y_table else None
        sf_nl_tds = (o["tds_yield_mpa"] / vm_nl) if o.get("tds_yield_mpa") else None
        sf_nl = min(x for x in (sf_nl_table, sf_nl_tds) if x is not None)
        grading["nonlinear"] = {"max_von_mises_mpa": vm_nl, "max_displacement_mm": nlo["max_displacement_mm"], "sf_table": sf_nl_table, "sf_tds": sf_nl_tds,
                                "sf_governing": round(sf_nl, 6), "ratio_vm_nonlinear_over_linear": nlo.get("ratio_nonlinear_over_linear_vm"),
                                "increments": nlo.get("increments"), "verdict": nl["verdict"]}
        if not reg.get("linear_regime_valid", True):
            sf_used, model = sf_nl, "nonlinear"          # the linear number is not a prediction there
        elif sf_nl < sf_lin:
            sf_used, model = sf_nl, "nonlinear (more conservative than the linear)"   # both are predictions: never the looser one
    elif nl:
        grading["nonlinear"] = {"verdict": nl["verdict"], "why": nl.get("why", "")[:300], "load_fraction_reached": nlo.get("load_fraction_reached")}
    verdict = "PASS" if sf_used >= REQUIRE_SF else "FAIL"
    why = ["SF %.3f (%s, %s model) on |F| %.4f N: peak von Mises %.3f MPa vs table yield %g MPa (SF %.3f) and TDS yield %g MPa (SF %s); the case requires %g" % (
        sf_used, basis_lin if model == "linear" else "nonlinear governing", model, r["inputs"]["force_magnitude_N"], o["max_von_mises_mpa"], y_table or 0, sf_table,
        o.get("tds_yield_mpa") or 0, ("%.3f" % sf_tds) if sf_tds is not None else "—", REQUIRE_SF)]
    if reg.get("linear_regime_valid") is False:
        why.append("delta %.4f mm is OUTSIDE the small-deflection regime (%s: d/t %.3f, d/L %.4f) so the linear peak is a bound, not a prediction" % (
            o["max_displacement_mm"], "plate" if reg["plate"] else "member", reg["d_over_t"], reg["d_over_L"]))
        if nl_ok:
            why.append("geometrically nonlinear re-solve (sim/fea_nlgeom.py, %d increments): peak %.3f MPa (%.3fx the linear), delta %.4f mm, SF %.3f — the verdict is taken on it" % (
                nlo.get("increments") or 0, nlo["max_von_mises_mpa"], nlo.get("ratio_nonlinear_over_linear_vm") or 0, nlo["max_displacement_mm"], sf_used))
        elif nl:
            why.append("the nonlinear re-solve did not reach the full load (%s of it) — graded on the linear bound; what settles it: a material-nonlinear solve or a printed part on a bench" % nlo.get("load_fraction_reached"))
        else:
            why.append("no nonlinear re-solve on disk yet — graded on the linear bound")
    elif reg.get("linear_regime_valid"):
        why.append("delta %.4f mm inside the small-deflection regime (d/t %.3f, d/L %.4f)" % (o["max_displacement_mm"], reg["d_over_t"], reg["d_over_L"]))
        if nl_ok:
            why.append("geometrically nonlinear re-solve (sim/fea_nlgeom.py, %d increments): peak %.3f MPa (%.3fx the linear), delta %.4f mm, SF %.3f — %s" % (
                nlo.get("increments") or 0, nlo["max_von_mises_mpa"], nlo.get("ratio_nonlinear_over_linear_vm") or 0, nlo["max_displacement_mm"], sf_nl,
                "the more conservative of the two carries the verdict" if sf_nl < sf_lin else "the linear stays the more conservative and carries the verdict"))
    if verdict == "FAIL" and slug in LOAD_SHARE:
        ls = LOAD_SHARE[slug]
        verdict = "CANNOT DETERMINE"
        why.append("BOUND, not a verdict: this study applies %.0f %% of a force the part carries in %s; the share is unmeasured (%s). A PASS at 100 %% would have been a PASS; "
                   "a FAIL at 100 %% proves only that the bound is not enough. What settles it: %s" % (100 * ls["share_applied"], ls["kind"], ls["why_unmeasured"], ls["what_settles_it"]))
    grading.update(sf_used=round(sf_used, 6), model=model, verdict=verdict)
    return verdict, "; ".join(why), grading


def sync_report(r):
    """report.json is what cecad.feaimage paints the caption from — keep it equal to the study's final verdict."""
    wd = os.path.join(ROOT, r["artifacts"][0])
    rp = os.path.join(wd, "report.json")
    if not os.path.exists(rp):
        return False
    rep = json.load(open(rp))
    changed = rep.get("verdict") != r["verdict"]
    rep["verdict"] = r["verdict"]
    rep["verdict_cecad_linear"] = (r.get("outputs") or {}).get("verdict_cecad")
    rep["grading"] = "sim/fea_rejudge.py: " + RULE_TEXT
    json.dump(rep, open(rp, "w"), indent=1)
    return changed


def main():
    changed_png = []
    for p in sorted(glob.glob(os.path.join(EVID, "fea_microduck-*.json"))):
        r = json.load(open(p))
        g = grade(r)
        if g is None:
            continue
        verdict, why, grading = g
        before = (r.get("verdict"), r.get("why"))
        if before != (verdict, why):
            hist = r.get("rejudged_from")
            hist = ([hist] if isinstance(hist, dict) else (hist or []))
            hist.append({"verdict": before[0], "why": before[1], "generator": "sim/fea_rejudge.py 2026-09-03"})
            r["rejudged_from"] = hist
        r["verdict"], r["why"] = verdict, why
        r["outputs"]["grading"] = grading
        json.dump(r, open(p, "w"), indent=1)
        if sync_report(r):
            png = os.path.join(FEA, os.path.basename(r["artifacts"][0]) + ".png")
            changed_png.append((r["artifacts"][0], png))
        mark = "" if before[0] == verdict else "  (was %s)" % before[0]
        print("%-52s %-17s SF %.3f %s%s" % (r["study"], verdict, grading["sf_used"], grading["model"], mark))
    with open(os.path.join(FEA, "rerender.txt"), "w") as fh:
        for wd, png in changed_png:
            fh.write("%s %s\n" % (wd, png))
    print("%d report.json verdicts changed -> out/sim-evidence/fea/rerender.txt (sim/fea_render.py re-paints them)" % len(changed_png))


if __name__ == "__main__":
    main()
