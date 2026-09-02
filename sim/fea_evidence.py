#!/usr/bin/env python3
"""fea_evidence.py — append every finished structural study to its part's
TRIAD evidence ledger (bin/triad evidence), so trust.json is computed from
it rather than asserted. One row per (part, study); --case + --input carry
the dedupe key, so re-running after a re-solve appends only changed studies.

    python3 sim/fea_evidence.py            (needs CE_TRIAD_ROOT)
"""
import glob, json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVID = os.path.join(ROOT, "out", "sim-evidence")
TRIAD = os.path.join(os.path.dirname(os.path.dirname(ROOT)), "bin", "triad")
os.environ.setdefault("CE_TRIAD_ROOT", ROOT + os.pathsep + os.path.dirname(os.path.dirname(ROOT)))
BY = "lane F1 structural (Claude Fable 5.1), sim/stress_all.py + sim/struct_ce.py + sim/fatigue_ankle.py, 2026-09-02"

def rows():
    for p in sorted(glob.glob(os.path.join(EVID, "fea_microduck-*.json")) + glob.glob(os.path.join(EVID, "buckling_*.json")) +
                    [os.path.join(EVID, "fatigue_ankle.json")]):
        if "_h" in os.path.basename(p) and "fea_microduck" in p:
            continue
        r = json.load(open(p))
        part = r.get("part")
        if not part or r.get("verdict") not in ("PASS", "FAIL", "CANNOT DETERMINE"):
            continue
        o = r.get("outputs") or {}
        study = r["study"]
        if study.startswith("fea_"):
            case = "fea_%s" % r.get("case")
            summ = "FEA %s: |F| %.4f N (%s), SF %s vs %g required, peak vM %s MPa, disp %s mm; %s" % (
                r.get("case"), (r.get("inputs") or {}).get("force_magnitude_N", 0), (r.get("inputs") or {}).get("force_source", "")[:60],
                ("%.3f" % o["sf"]) if o.get("sf") is not None else "—", 2.0, ("%.3f" % o["max_von_mises_mpa"]) if o.get("max_von_mises_mpa") else "—",
                ("%.4f" % o["max_displacement_mm"]) if o.get("max_displacement_mm") else "—", r.get("why", "")[:220])
        elif study.startswith("buckling_"):
            case = "buckling_axial"
            summ = "ce-struct buckling/modal: %s; first mode %s Hz" % (r.get("why", "")[:220], o.get("first_mode_hz"))
        else:
            case = "fatigue_walk"
            summ = "fatigue (Ezeh & Susmel 2019 design curve): %s" % r.get("why", "")[:260]
        yield part, case, p, r["verdict"], summ

def main():
    for part, case, p, verdict, summ in rows():
        cmd = [TRIAD, "evidence", part, "--kind", "sim", "--summary", summ, "--outcome", verdict, "--by", BY,
               "--artifact", os.path.abspath(p), "--case", case, "--input", os.path.abspath(p)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        print("%-40s %-22s %-17s rc=%d %s" % (part, case, verdict, r.returncode, (r.stdout.strip().splitlines() or [r.stderr.strip()[-120:]])[-1][:110]))

if __name__ == "__main__":
    main()
