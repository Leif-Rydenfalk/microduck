#!/usr/bin/env python3
"""verify_screw_parts.py — MEASURE the built M2 / M2.5 cap screws against the
ISO 4762 figures their own component.json cites.

    ce-cad/bin/cad tools/verify_screw_parts.py   -> out/fasteners/screw-parts-verify.json

Runs under FreeCAD python. Every member of each length family is BUILT and
MEASURED; a family that builds at one length and not another is a defect this
catches, and a dimension that cannot be measured off the solid is CANNOT
DETERMINE, never a pass.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "fasteners", "screw-parts-verify.json")
os.environ.setdefault("CE_TRIAD_ROOT", "%s:%s" % (ROOT, os.path.dirname(os.path.dirname(ROOT))))

import FreeCAD as App  # noqa: E402
import cecad.triad as triad  # noqa: E402

REFS = ["part:screw-m2-iso4762", "part:screw-m2.5-iso4762"]

doc = App.newDocument("screwverify")
report = {"doc": {"id": "MD-FAST-SCREWPART-001", "rev": "A",
                  "title": "M2 / M2.5 ISO 4762 cap screws — the built solid measured "
                           "against the ISO figures component.json cites",
                  "generated_by": "tools/verify_screw_parts.py"},
          "parts": {}}
fails = 0
for ref in REFS:
    f = triad.resolve(ref)
    path = f.find("cad/part.py")
    mod = {"__file__": path, "__name__": "part_%s" % ref.split(":")[1].replace("-", "_").replace(".", "p")}
    exec(compile(open(path, encoding="utf-8").read(), path, "exec"), mod)
    lengths = mod["lengths"]()
    entry = {"folder": f.path, "sourced_lengths_mm": lengths,
             "default_length_mm": mod["DEFAULT_LENGTH_MM"],
             "spec_cited_in_component_json": mod["SPEC_MM"],
             "built": [], "refusals": []}
    for L in lengths:
        try:
            rows = mod["verify"](doc, L)
            bad = [r for r in rows if r[3] != "PASS"]
            fails += len(bad)
            entry["built"].append({"length_mm": L, "rows": rows,
                                   "verdict": "PASS" if not bad else "FAIL",
                                   "n_rows": len(rows)})
        except Exception as e:  # noqa: BLE001
            fails += 1
            entry["built"].append({"length_mm": L, "verdict": "FAIL",
                                   "error": "%s: %s" % (type(e).__name__, e)})
    # THE REFUSAL IS PART OF THE CONTRACT — an unsourced length must be refused.
    for L in (7.0, 6.5):
        try:
            mod["build"](doc, {"length_mm": L})
            entry["refusals"].append({"length_mm": L, "verdict": "FAIL",
                                      "why": "built an unsourced length without complaint"})
            fails += 1
        except ValueError as e:
            entry["refusals"].append({"length_mm": L, "verdict": "PASS",
                                      "refused_with": str(e)[:160]})
    report["parts"][ref] = entry

n_built = sum(len(v["built"]) for v in report["parts"].values())
n_pass = sum(1 for v in report["parts"].values() for b in v["built"] if b["verdict"] == "PASS")
n_rows = sum(b.get("n_rows", 0) for v in report["parts"].values() for b in v["built"])
report["counts"] = {"parts": len(REFS), "members_built": n_built,
                    "members_PASS": n_pass, "dimension_rows_checked": n_rows,
                    "failed_rows_or_builds": fails,
                    "refusal_checks": sum(len(v["refusals"]) for v in report["parts"].values())}
report["verdict"] = "PASS" if fails == 0 else "FAIL"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(report, fh, indent=1)
print("members built:", n_built, "PASS:", n_pass, "dimension rows:", n_rows, "failures:", fails)
print("verdict:", report["verdict"])
print("wrote", OUT)
