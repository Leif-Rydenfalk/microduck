#!/usr/bin/env python3
"""fea_rejudge.py — re-apply stress_all.py's verdict rules to study JSONs already
on disk, without re-solving (plain python3, no kernel).

Why it exists: the rigidity-plate bounding rule (100 % of the thigh force through
the plate — a FAIL there proves nothing, so it is CANNOT DETERMINE) was added
while the 2026-09-02 run was already past that study. The solve outputs are
untouched; only `verdict`/`why` are rewritten, and the previous pair is kept
under `rejudged_from`.
"""
import glob, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVID = os.path.join(ROOT, "out", "sim-evidence")
REQUIRE_SF = 2.0
for p in sorted(glob.glob(os.path.join(EVID, "fea_microduck-upper-leg-rigidity-plate_*.json"))):
    r = json.load(open(p)); o = r.get("outputs") or {}
    if r.get("verdict") == "FAIL" and o.get("sf") is not None:
        r["rejudged_from"] = {"verdict": r["verdict"], "why": r["why"]}
        r["verdict"] = "CANNOT DETERMINE"
        r["why"] = ("bounding case: 100 %% of the thigh force through the 1 mm plate gives SF %.3f (< %g), but the plate shares that load with the "
                    "housing it closes and its share is unmeasured; a housing that meshes (see fea_meshability) plus a two-body solve settles it" % (o["sf"], REQUIRE_SF))
        json.dump(r, open(p, "w"), indent=1); print("rejudged", os.path.basename(p), "->", r["verdict"])

# the trunk base: a plate that is not the load path on its own (see stress_all.py)
for p in sorted(glob.glob(os.path.join(EVID, "fea_microduck-trunk-base_*.json"))):
    r = json.load(open(p)); o = r.get("outputs") or {}
    if r.get("verdict") == "FAIL" and o.get("sf") is not None:
        r["rejudged_from"] = {"verdict": r["verdict"], "why": r["why"]}
        r["verdict"] = "CANNOT DETERMINE"
        r["why"] = "the 1 mm trunk-base plate cannot carry the stance leg's force on its own: held at its four edge screws and loaded at the left hip-yaw hole wall it reads SF %.3f (< %g), and held at one hip hole and loaded at the other (the first run) it read a 35 mm cantilever. In the product the plate is clamped between the two trunk shells (part:microduck-trunk-shell-left/-right, both rebuilt) and the hip-yaw XL330 case, so the load path is shells + plate + servo case, not the plate alone; the share is unmeasured. What settles it: a two-body solve (shells + base, bolted) in cecad.stress/ce-struct, or a printed trunk loaded to 20 N at one hip on a bench" % (o["sf"], REQUIRE_SF)
        json.dump(r, open(p, "w"), indent=1); print("rejudged", os.path.basename(p), "->", r["verdict"])
