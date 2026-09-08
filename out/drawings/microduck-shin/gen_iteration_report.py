"""Render the canonical shin drawing's measured iteration evidence."""
import html,json
from pathlib import Path
p=Path(__file__).resolve().parent
before=json.loads((p/'baseline-2026-09-08/sheetcheck.json').read_text())
after=json.loads((p/'sheetcheck-current.json').read_text())
r=json.loads((p/'result.json').read_text())
esc=lambda value:html.escape(str(value))
measures=[('Dimension coverage (%)','dim_coverage_pct'),('Content occupancy (%)','occupancy_pct'),('Minimum lettering (mm)','font_min_mm'),('Isometric views','iso_count'),('Shaded colour renders','colour_and_shadow_render_count')]
rows=''.join(f'<tr><td>{label}</td><td>{esc(before.get(key))}</td><td>{esc(after.get(key))}</td></tr>' for label,key in measures)
rules=''.join(f'<tr><td>{k}</td><td>{before["rules"][k]}</td><td>{v}</td></tr>' for k,v in after['rules'].items())
gaps=''.join(f'<tr><td>{esc(g["clause"])}</td><td>{esc(g["kind"])} / {esc(g["status"])}</td><td>{esc(g["remaining"])}</td><td>{esc(g["next_action"])}</td></tr>' for g in r.get('full_contract_gaps',[]) if isinstance(g,dict))
report=f'''<!doctype html><meta charset="utf-8"><title>Shin drawing iteration</title>
<style>body{{font:17px/1.5 system-ui;color:#152330;max-width:1180px;margin:30px auto;padding:24px}}img{{width:100%}}td,th{{padding:9px;border-bottom:1px solid #ccd4da;text-align:left}}table{{border-collapse:collapse;width:100%}}a{{color:#12699c}}.status{{background:#eaf3f7;padding:20px;border-left:5px solid #12699c}}pre{{background:#eef2f4;padding:16px;overflow:auto}}</style>
<h1>Microduck shin — measured drawing iteration</h1>
<p class="status"><strong>Solid and drawing readback: {esc(r['build_verdict'])}. Eight sheet gates: {esc(r['sheet_verdict'])}.</strong><br>Full manufacturing contract: {esc(r.get('full_contract_verdict','not separately evaluated'))}. Manufacturing release: {esc(r.get('manufacturing_release','NOT RELEASED'))}.</p>
<p>The geometry remains the existing reconstructed solid. The drawing's layout, source-linked annotations and serialized files are independently checked. A layout or nominal-dimension pass does not settle unknown original geometry or production fits.</p>
<table><tr><th>Measurement</th><th>Preserved baseline</th><th>Current canonical drawing</th></tr>{rows}</table>
<table><tr><th>Unchanged acceptance rule</th><th>Baseline</th><th>Current</th></tr>{rules}</table>
<h2>Drawing and readback</h2><p><a href="microduck-shin.svg">Self-contained SVG</a> · <a href="microduck-shin.pdf">PDF with embedded renders</a> · <a href="microduck-shin.dxf">Vector-only DXF companion</a> · <a href="result.json">Machine-readable result and remaining clauses</a></p>
<img src="microduck-shin-sheet.png" alt="Current canonical shin drawing">
<p><a href="verify-sheet.log">Native drawing readback</a> · <a href="sheetcheck-current.json">Eight measured sheet gates</a> · <a href="pdf-readback.json">PDF image and operator readback</a> · <a href="render-scale-readback.json">Actual camera-to-paper scale readback</a> · <a href="layout-evidence.json">Feature, camera and layout source evidence</a></p>
<h2>Unfinished requirements</h2><table><tr><th>Governing clause</th><th>Subject and status</th><th>Remaining requirement</th><th>Next concrete action</th></tr>{gaps}</table>
<p>Authority: <a href="../../../docs/MANUFACTURING-REQUIREMENTS.md">Manufacturing file requirements</a>. This artifact report does not replace the project's existing closure backlog.</p>
<h2>Reproduce this drawing</h2><pre>ce-cad/bin/cad tools/draw_part.py microduck-shin --layout=render-panels
ce-cad/bin/cad out/drawings/microduck-shin/check_drawing_regressions.py</pre>
<p>The route stages files and replaces canonical artifacts only after solid readback, all eight sheet gates, PDF pixel/placement readback and camera-scale readback pass. Its full-contract status remains separate.</p>
<details><summary>Preserved baseline</summary><img src="baseline-2026-09-08/microduck-shin-sheet.png" alt="Preserved baseline drawing"><a href="baseline-2026-09-08/sheetcheck.json">Baseline measurements</a></details>'''
(p/'iteration-2026-09-08.html').write_text(report)
print('Wrote',p/'iteration-2026-09-08.html')
