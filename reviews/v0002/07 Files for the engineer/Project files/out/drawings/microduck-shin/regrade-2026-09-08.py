"""Refresh this sheet only after generator changes; preserve build evidence."""
import json
from pathlib import Path
from cecad import sheetcheck
p = Path(__file__).resolve().parent
r = json.loads((p / "result.json").read_text())
g = sheetcheck.grade_sheet(str(p / "microduck-shin.svg"), png_path=str(p / "microduck-shin-sheet.png"), slug="microduck-shin", use_kernel=True, refresh=True)
(p / "sheetcheck-current.json").write_text(json.dumps(g, indent=1))
r["sheet_verdict"] = g["verdict"]
r["sheet_verdict_why"] = g["checks"]["dim_coverage"]["why"]
r["sheet_rules"] = g["rules"]
r["sheet_sections"] = g["sections"]
r["sheet_failing_rules"] = [k for k,v in g["rules"].items() if v != "PASS"]
for k in ["features_enumerated", "features_dimensioned", "dim_coverage_pct"]:
    r["sheet_measurements"][k] = g.get(k)
r["sheet_refresh_evidence"] = "sheetcheck-current.json; fresh solid probe, no cache reuse"
(p / "result.json").write_text(json.dumps(r, indent=1))
print(g["verdict"], g["rules"], g["checks"]["dim_coverage"]["why"])
