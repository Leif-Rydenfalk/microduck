# The two sheet verdicts do not contradict — they measure different things

Measured 2026-09-04 by the orchestrator, after a peer session flagged that
`out/drawings/*/result.json` reads 25 PASS / 4 CANNOT DETERMINE / 2 FAIL while
`out/drawings/sheetcheck-before.json` reads 27 FAIL / 0 PASS on the same sheets.

| file | what its `verdict` actually grades | verdict |
|---|---|---|
| `out/drawings/<slug>/result.json` | **the PART**: did `cad/part.py` build a parametric solid, and was a sheet emitted? Its fields are `bbox_mm`, `solids`, `faces`, `material_record`, `process_record`. Generated 2026-09-03 05:21, **before A3 and A4 existed**. | 25 PASS |
| `out/drawings/sheetcheck-before.json` | **the SHEET**, against `docs/MANUFACTURING-REQUIREMENTS.md` A2+A3+A4 — the eight rules `line_ratio, coverage, empty_rect, font, iso, renders, curve_density, dim_coverage`. | 27 FAIL |

**`sheetcheck` is the right instrument for Leif's standard.** `result.json`'s
PASS means "the part built", which is a far weaker claim than "a machinist can
cut this from this sheet", and it is being read as the latter. That is the
classic failure of a tool returning PASS while measuring the wrong quantity.

**The fix, at source, in the generator — not by editing this file:**
`result.json` must stop publishing a bare `verdict` that a reader will take as
sheet quality. It carries `build_verdict` (its real subject) plus the
`sheet_verdict` copied from sheetcheck, and any index that renders a verdict
beside a sheet renders the SHEET one. Until that lands, no reader should treat
a green row in `out/drawings/INDEX.html` as a machinable sheet.

Nothing here loosens either check. Both numbers stand; only the labels were wrong.
