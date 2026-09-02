#!/usr/bin/env python3
"""fea_evidence.py — append every finished structural study to its part's
TRIAD evidence ledger (bin/triad evidence), so trust.json is computed from
it rather than asserted. One row per (part, study); --case + --input carry
the dedupe key, so re-running after a re-solve appends only changed studies.

    python3 sim/fea_evidence.py            (needs CE_TRIAD_ROOT)
"""
import glob, json, os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVID = os.path.join(ROOT, "out", "sim-evidence")
TRIAD = os.path.join(os.path.dirname(os.path.dirname(ROOT)), "bin", "triad")
os.environ.setdefault("CE_TRIAD_ROOT", ROOT + os.pathsep + os.path.dirname(os.path.dirname(ROOT)))
BY = "lane F1 structural (Claude Fable 5.1), sim/stress_all.py + sim/fea_rejudge.py + sim/fea_nlgeom.py + sim/struct_ce.py + sim/fatigue_walk.py, 2026-09-03"

CONV_SUBRUN = re.compile(r"_h(auto|[0-9]+(\.[0-9]+)?)\.json$")   # a convergence sub-run tag, e.g. _h1.5.json — NOT "_head_drop"


def is_subrun(path):
    """F1 skeptic finding 1 (2026-09-03): the old test `"_h" in basename` matched every *_head_drop study and no
    sub-run at all (none is ever written as its own file). The tag is the study's own suffix and nothing else."""
    return bool(CONV_SUBRUN.search(os.path.basename(path)))


def rows():
    files = (sorted(glob.glob(os.path.join(EVID, "fea_microduck-*.json"))) + sorted(glob.glob(os.path.join(EVID, "fea_nlgeom_*.json"))) +
             sorted(glob.glob(os.path.join(EVID, "buckling_*.json"))) + [os.path.join(EVID, "fatigue_ankle.json")])
    for p in files:
        if is_subrun(p):
            continue
        if not os.path.exists(p):
            continue
        r = json.load(open(p))
        part = r.get("part")
        if not part or r.get("verdict") not in ("PASS", "FAIL", "CANNOT DETERMINE"):
            continue
        o = r.get("outputs") or {}
        study = r["study"]
        if study.startswith("fea_nlgeom_"):
            case = "fea_nlgeom_%s" % r.get("case")
            summ = "geometrically nonlinear re-solve (%s): %s" % (r.get("case"), r.get("why", "")[:260])
        elif study.startswith("fea_"):
            case = "fea_%s" % r.get("case")
            g = o.get("grading") or {}
            summ = "FEA %s: |F| %.4f N (%s), SF %s (%s) vs %g required, peak vM %s MPa, disp %s mm; %s" % (
                r.get("case"), (r.get("inputs") or {}).get("force_magnitude_N", 0), (r.get("inputs") or {}).get("force_source", "")[:60],
                ("%.3f" % g["sf_used"]) if g.get("sf_used") is not None else (("%.3f" % o["sf"]) if o.get("sf") is not None else "—"), g.get("model", "linear"), 2.0,
                ("%.3f" % o["max_von_mises_mpa"]) if o.get("max_von_mises_mpa") else "—",
                ("%.4f" % o["max_displacement_mm"]) if o.get("max_displacement_mm") else "—", r.get("why", "")[:220])
        elif study.startswith("buckling_"):
            case = "buckling_axial"
            summ = "ce-struct buckling/modal: %s; first mode %s Hz" % (r.get("why", "")[:220], o.get("first_mode_hz"))
        else:
            case = "fatigue_walk"
            summ = "fatigue (Ezeh & Susmel 2019 design curve): %s" % r.get("why", "")[:260]
        yield part, case, p, r["verdict"], summ
    # one fatigue row per part from the all-parts study (the ankle's own file above is the same basis with its mesh-scaled variant)
    fw = os.path.join(EVID, "fatigue_walk.json")
    if os.path.exists(fw):
        for row in json.load(open(fw))["outputs"]["rows"]:
            if row["part"] == "part:microduck-ankle-left":
                continue
            yield row["part"], "fatigue_walk", fw, row["verdict"], "fatigue (Ezeh & Susmel 2019 design curve, sim/fatigue_walk.py): %s" % row.get("why", "")[:260]

def main():
    for part, case, p, verdict, summ in rows():
        cmd = [TRIAD, "evidence", part, "--kind", "sim", "--summary", summ, "--outcome", verdict, "--by", BY,
               "--artifact", os.path.abspath(p), "--case", case, "--input", os.path.abspath(p)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        print("%-40s %-22s %-17s rc=%d %s" % (part, case, verdict, r.returncode, (r.stdout.strip().splitlines() or [r.stderr.strip()[-120:]])[-1][:110]))

if __name__ == "__main__":
    main()
