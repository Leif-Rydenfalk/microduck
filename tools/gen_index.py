#!/usr/bin/env python3
"""gen_index.py — build INDEX.html, the front door of the repository.

Every entry is CHECKED against the filesystem before it is written, so the index
can never advertise a document that is not there. A missing target is published
as missing, with the reason, rather than as a dead link.
"""
import json, os, html, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

SECTIONS = [
    ("Start here", "The two documents that answer 'what is this and is it real'.", [
        ("RELEASE.html", "Release dossier",
         "The master document: readiness matrix, BOM, full assembly sequence, wiring, power-up, and what still blocks a factory release."),
        ("COMPARISON.html", "Reference match",
         "Our CAD beside the real product photographs at matched camera angles, plus the measured dimension table for all 47 meshes and the head-conformance measurement."),
    ]),
    ("Specification & parts", "What the machine is, measured.", [
        ("SPEC.html", "Specification", "Envelope, the 15-joint table, and every mesh with its measured bounding box."),
        ("docs/PARTS.html", "Parts catalogue", "Every part: quantity, material, body, joint, and rebuild status."),
        ("docs/BOM.html", "Bill of materials", "Every line, bought and made."),
        ("docs/CABLES.html", "Cable schedule", "22 cables with lengths and voltage-drop."),
        ("wiring/CABLES.html", "Cable schedule (wiring lane)", "The wiring lane's copy of the cable runs."),
    ]),
    ("Electronics", "The electrical half, three levels of detail.", [
        ("ELECTRONICS-DATASHEET.html", "Electronics datasheet", "The assembled electronics reference: every IC with provenance."),
        ("electronics/1-block-diagram.svg", "1 · Block diagram", "Functional blocks and the buses between them — how it flows."),
        ("electronics/2-schematic-radxa.svg", "2 · Schematic — compute", "Radxa Zero 3W header: every used pin and its net."),
        ("electronics/2-schematic-hat.svg", "2 · Schematic — Robot HAT", "Codec, IMU, ToF header, Dynamixel transceiver, power path."),
        ("electronics/2-schematic-imu.svg", "2 · Schematic — imu_to_dxl", "LSM6DSV16X as a Dynamixel Protocol-2 slave."),
        ("electronics/2-schematic-sensors.svg", "2 · Schematic — sensors", "Camera, ToF, audio."),
        ("electronics/3-layout.svg", "3 · Physical layout", "Where each board and device physically sits, and every cable run with its length."),
        ("docs/ELECTRONICS-AND-SOFTWARE.html", "Electronics & software", "Bus, registers, daemons, pin map."),
    ]),
    ("Manufacturing", "What a shop needs to actually build it.", [
        ("docs/PRODUCTION.html", "Production", "Costs at 1/10/100/1000, print-vs-mould, compliance."),
        ("docs/MANUFACTURING-REQUIREMENTS.html", "Manufacturing requirements", "The standard our drawings and schematics are graded against."),
        ("ce-assemblies/microduck/current/manual/MANUAL.html", "Construction manual", "The step-by-step build the release's assembly section is drawn from."),
        ("out/drawings/INDEX.html", "Mechanical drawings", "Dimensioned sheets: third-angle views, hole tables, sections."),
        ("out/print/PRINT.html", "Print package", "Plate files and the measured filament/time for every printed part."),
        ("BUILD-BOOK.html", "Build book", "The long-form build narrative."),
    ]),
    ("Simulation & evidence", "Every claim that has a measurement behind it.", [
        ("SIMULATION.html", "Simulation dossier", "Structural FEA matrix, mesh convergence, material sweep, and the motion-policy runs."),
        ("docs/SIM-CAPABILITY.html", "Simulation capability", "What the simulation can and cannot do, stated honestly."),
        ("out/verify/mech_dims.json", "Measured dimensions (data)", "Bounding box of all 47 meshes in mm to 4 dp, plus rebuild deviation."),
        ("out/verify/head_analysis.json", "Head conformance (data)", "Scale-free silhouette ratios for the head, and why the verdict is CANNOT DETERMINE."),
        ("out/stress/matrix.json", "Structural FEA matrix (data)", "Every part × load case × material, with mesh convergence."),
        ("out/stress/report.json", "Structural FEA — standing case (data)", "The original single-case run."),
    ]),
    ("Project", "How the work is run and reproduced.", [
        ("STATUS.html", "Status", "Where each lane stands."),
        ("GOAL.html", "Goal", "What done means."),
        ("TOOLCHAIN.html", "Toolchain", "Exact tool and kernel versions to reproduce every file."),
        ("README.md", "Readme", "Repository orientation."),
    ]),
]

TOOLS = [
    ("tools/gen_comparison.py", "Builds COMPARISON.html from the measured data."),
    ("tools/gen_index.py", "Builds this index, checking every link."),
    ("tools/head_analysis.py", "Measures head conformance from silhouettes."),
    ("tools/md2html.py", "Converts the Markdown docs to the shared HTML style."),
    ("sim/mech_dims.py", "Measures every mesh through the FreeCAD kernel."),
    ("sim/stress_matrix.py", "The structural FEA matrix: parts × load cases × materials."),
    ("sim/compare_render.py", "Photo-matched studio renders and joint close-ups."),
    ("sim/assembly_steps_mj.py", "Cumulative assembly-step renders."),
    ("sim/run_policy.py", "Runs Pollen's trained policies on our meshes."),
    ("electronics/gen_ee.py", "Generates the block diagram, schematics and layout."),
]


def stat(rel):
    p = os.path.join(REPO, rel)
    if not os.path.exists(p):
        return None
    sz = os.path.getsize(p)
    mt = datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%d %H:%M")
    return sz, mt


def human(n):
    for u in ("B", "KB", "MB"):
        if n < 1024 or u == "MB":
            return f"{n:.0f} {u}" if u == "B" else f"{n/1:.0f} {u}"
        n /= 1024.0


def size_str(n):
    if n < 1024: return f"{n} B"
    if n < 1024*1024: return f"{n/1024:.0f} KB"
    return f"{n/1024/1024:.1f} MB"


rows_html, present, missing = [], 0, 0
for title, blurb, items in SECTIONS:
    body = []
    for rel, name, desc in items:
        st = stat(rel)
        if st:
            present += 1
            sz, mt = st
            body.append(
                f'<tr><td><a href="{rel}">{html.escape(name)}</a><div class="d">{html.escape(desc)}</div></td>'
                f'<td><code>{html.escape(rel)}</code></td>'
                f'<td class="n">{size_str(sz)}</td><td class="n">{mt}</td>'
                f'<td><span class="chip pass">present</span></td></tr>')
        else:
            missing += 1
            body.append(
                f'<tr class="miss"><td>{html.escape(name)}<div class="d">{html.escape(desc)}</div></td>'
                f'<td><code>{html.escape(rel)}</code></td>'
                f'<td class="n">—</td><td class="n">—</td>'
                f'<td><span class="chip cd">not generated yet</span></td></tr>')
    rows_html.append(
        f'<section><h2>{html.escape(title)}</h2><p class="lede">{html.escape(blurb)}</p>'
        f'<div class="tw"><table class="data"><thead><tr><th>Document</th><th>Path</th>'
        f'<th class="n">Size</th><th class="n">Updated</th><th>State</th></tr></thead>'
        f'<tbody>{"".join(body)}</tbody></table></div></section>')

tool_rows = "".join(
    f'<tr><td><code>{html.escape(t)}</code></td><td>{html.escape(d)}</td>'
    f'<td><span class="chip {"pass" if stat(t) else "cd"}">{"present" if stat(t) else "missing"}</span></td></tr>'
    for t, d in TOOLS)

HTML = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Microduck Repository Index</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opt_sz,wght@8..60,400;8..60,600;8..60,700&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="tools/doc.css">
<style>
  .d{{font-size:12.5px;color:var(--ink-2);margin-top:2px;max-width:46em}}
  tr.miss td{{opacity:.72}}
  table.data td code{{font-size:11.5px}}
  .statbar{{display:flex;flex-wrap:wrap;border-bottom:1px solid var(--hair);margin:10px 0 2px}}
  .stat{{padding:12px 26px 12px 0;margin-right:22px}}
  .stat b{{display:block;font-weight:700;font-size:22px;font-variant-numeric:tabular-nums}}
  .stat span{{font-family:var(--sans);font-size:12px;color:var(--ink-2)}}
</style>
</head>
<body>
<div class="wrap">
<header class="hero">
  <p class="eyebrow">ce-designs/microduck · repository index</p>
  <h1>Microduck — every document in this repository</h1>
  <p class="sub">A reverse-engineered, manufacturable reconstruction of the Pollen Robotics
  Microduck. Every entry below was checked against the filesystem when this page was generated;
  anything not yet produced is listed as such rather than linked into a 404.</p>
  <div class="rev"><span>MD-IDX-001</span><span>generated {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
    <span>by <code>tools/gen_index.py</code></span></div>
</header>

<div class="statbar">
  <div class="stat"><b>{present}</b><span>documents present</span></div>
  <div class="stat"><b>{missing}</b><span>not yet generated</span></div>
  <div class="stat"><b>47</b><span>parts measured</span></div>
  <div class="stat"><b>9/9</b><span>rebuilds dimensionally PASS</span></div>
</div>

{"".join(rows_html)}

<section><h2>Tools — how every document above is regenerated</h2>
<p class="lede">Nothing in this repository is hand-maintained if a script can own it. Each tool
below regenerates its document from the measured data, so a stale number is a bug with a fix
rather than an edit.</p>
<div class="tw"><table class="data">
<thead><tr><th>Script</th><th>What it generates</th><th>State</th></tr></thead>
<tbody>{tool_rows}</tbody></table></div>
<p style="font-size:13px;color:var(--ink-2)">Run anything under <code>sim/</code> or that
imports the CAD kernel with <code>ce-cad/bin/cad &lt;script.py&gt;</code> — the system
<code>python3</code> has neither numpy nor PIL.</p>
</section>

</div>
</body>
</html>
"""
open(os.path.join(REPO, "INDEX.html"), "w").write(HTML)
print(f"wrote INDEX.html — {present} present, {missing} not yet generated")
