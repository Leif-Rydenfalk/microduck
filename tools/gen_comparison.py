#!/usr/bin/env python3
"""gen_comparison.py — build COMPARISON.html: every render of ours beside the
real product photo at the same camera angle, plus the measured dimension table.
Data-driven from out/verify/mech_dims.json + out/compare/*.png. Regenerable.
"""
import json, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DIMS = json.load(open(os.path.join(REPO, "out", "verify", "mech_dims.json")))

BODY_PAIRS = [
    ("Left profile", "cream colourway, standing",
     "images/store/store_microduck-cream-standing-profile-left.jpg",
     "out/compare/ours-prof-left.png", "azimuth 270°, elevation −8°"),
    ("Right profile", "graphite colourway, standing",
     "images/store/store_microduck-graphite-standing-profile-right-02.jpg",
     "out/compare/ours-prof-right.png", "azimuth 90°, elevation −8°"),
    ("Three-quarter front-left", "sky colourway, standing",
     "images/store/store_microduck-sky-standing-three-quarter-left-02.jpg",
     "out/compare/ours-iso-fl.png", "azimuth 225°, elevation −10°"),
    ("Three-quarter back-right", "graphite colourway, standing",
     "images/store/store_microduck-graphite-standing-back-three-quarter-right-02.jpg",
     "out/compare/ours-iso-br.png", "azimuth 45°, elevation −12°"),
]
JOINT_PAIRS = [
    ("Neck — 2× XL330 pitch/roll stack", "out/compare/ref-joint-neck.png",
     "out/compare/ours-joint-neck.png",
     "Two XL330-M288-T in series above the trunk; the beak assembly hangs off the upper horn."),
    ("Hip — yaw / roll / pitch cluster", "out/compare/ref-joint-hip.png",
     "out/compare/ours-joint-hip.png",
     "Three orthogonal hinges inside one bracket group; 22×16×4 bearing opposes each servo horn."),
    ("Knee", "out/compare/ref-joint-knee.png", "out/compare/ours-joint-knee.png",
     "Triangular thigh plate carries the knee servo; the shin bolts to the output horn."),
    ("Ankle + foot", "out/compare/ref-joint-ankle.png", "out/compare/ours-joint-ankle.png",
     "Ankle servo drives the foot plate; sole is a separate compliant pad."),
]

def dim_rows():
    parts = sorted(DIMS["parts"], key=lambda p: (not p["rebuilt"], p["mesh"]))
    out = []
    for p in parts:
        r = p["ref_mm"]
        if p["rebuilt"]:
            o, d = p["our_mm"], p["delta_mm"]
            v = p["dim_verdict"]
            cls = "pass" if v == "PASS" else "cd"
            out.append(
                f'<tr><td><code>{html.escape(p["mesh"])}</code></td>'
                f'<td class="n">{r["x"]:.3f}</td><td class="n">{r["y"]:.3f}</td><td class="n">{r["z"]:.3f}</td>'
                f'<td class="n">{o["x"]:.3f}</td><td class="n">{o["y"]:.3f}</td><td class="n">{o["z"]:.3f}</td>'
                f'<td class="n">{p["max_delta_mm"]:.4f}</td>'
                f'<td><span class="chip {cls}">{v}</span></td></tr>')
        else:
            out.append(
                f'<tr><td><code>{html.escape(p["mesh"])}</code></td>'
                f'<td class="n">{r["x"]:.3f}</td><td class="n">{r["y"]:.3f}</td><td class="n">{r["z"]:.3f}</td>'
                f'<td class="n dash">—</td><td class="n dash">—</td><td class="n dash">—</td>'
                f'<td class="n dash">—</td><td><span class="chip ref">reference</span></td></tr>')
    return "\n".join(out)

def pair_block(title, sub, real, ours, cam, note=None):
    return f"""
  <h3>{html.escape(title)}</h3>
  <p class="paircap">{html.escape(sub)} · our camera: <code>{html.escape(cam)}</code></p>
  <div class="pair">
    <figure><span class="tag">Real · pollen-robotics.com</span>
      <img src="{real}" alt="{html.escape(title)} official"></figure>
    <figure><span class="tag ours">Ours · CAD render</span>
      <img src="{ours}" alt="{html.escape(title)} ours"></figure>
  </div>
  {'<p class="note">' + html.escape(note) + '</p>' if note else ''}"""

n_reb = sum(1 for p in DIMS["parts"] if p["rebuilt"])
n_pass = sum(1 for p in DIMS["parts"] if p.get("dim_verdict") == "PASS")
worst = max((p["max_delta_mm"] for p in DIMS["parts"] if p["rebuilt"]), default=0)

body = "\n".join(pair_block(t, s, r, o, c) for t, s, r, o, c in BODY_PAIRS)
joints = "\n".join(pair_block(t, "real robot, same joint (cropped from the profile photograph)",
                              r, o, "left profile, matched", n) for t, r, o, n in JOINT_PAIRS)

HTML = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Reference Match</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opt_sz,wght@8..60,400;8..60,600;8..60,700&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="tools/doc.css">
<style>
  .pair{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:10px 0 4px}}
  .pair figure{{margin:0;padding:8px}}
  .pair figure img{{width:100%;aspect-ratio:1/1;object-fit:contain;background:#fff}}
  .tag{{font-family:var(--sans);font-size:10.5px;font-weight:600;letter-spacing:.07em;
       text-transform:uppercase;display:inline-block;padding:2px 8px;margin-bottom:6px;
       border:1px solid var(--hair);color:var(--ink-2)}}
  .tag.ours{{color:var(--accent);border-color:var(--accent)}}
  .paircap{{font-family:var(--sans);font-size:12.5px;color:var(--ink-2);margin:0 0 2px}}
  .note{{font-size:13.5px;color:var(--ink-2);margin:2px 0 18px;max-width:44em}}
  .verdict{{border-left:3px solid var(--accent);padding:2px 0 2px 18px;margin:14px 0;font-size:15.5px}}
  .verdict b{{color:var(--accent)}}
  .verdict.warn{{border-left-color:var(--no)}} .verdict.warn b{{color:var(--no)}}
  td.dash{{color:#b3aea4}}
  .chip.ref{{color:var(--ink-2);font-weight:400;text-transform:none;letter-spacing:0}}
  table.data td code{{font-size:12px}}
  .statbar{{display:flex;flex-wrap:wrap;gap:0;border-bottom:1px solid var(--hair);margin:8px 0 2px}}
  .stat{{padding:12px 26px 12px 0;margin-right:22px}}
  .stat b{{display:block;font-weight:700;font-size:22px;font-variant-numeric:tabular-nums}}
  .stat span{{font-family:var(--sans);font-size:12px;color:var(--ink-2)}}
  @media(max-width:640px){{.pair{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<div class="wrap">
<p class="backlink"><a href="RELEASE.html">← Release dossier</a></p>

<header class="hero">
  <p class="eyebrow">Microduck reverse-engineering · reference conformance</p>
  <h1>Reference match: our CAD against the real Microduck</h1>
  <p class="sub">Every render of ours sits beside the real product photograph shot from the same
  camera angle. Below the visual check is the measured dimension table for all
  {DIMS['count']} mechanical parts, at full precision.</p>
  <div class="rev">
    <span>MD-CMP-001 · Rev B</span><span>{DIMS['generated']}</span>
    <span>renderer: MuJoCo 3.12 offscreen, 1400²</span><span>pose: STAND, head levelled</span>
  </div>
</header>

<div class="statbar">
  <div class="stat"><b>{DIMS['count']}</b><span>parts measured</span></div>
  <div class="stat"><b>{n_reb}</b><span>re-modelled parametrically</span></div>
  <div class="stat"><b>{n_pass}/{n_reb}</b><span>dimensional PASS</span></div>
  <div class="stat"><b>{worst:.4f} mm</b><span>worst bbox deviation</span></div>
  <div class="stat"><b>8</b><span>photo-matched viewpoints</span></div>
</div>

<nav class="toc">
  <a href="#answer">1 Verdict</a><a href="#body">2 Whole robot</a><a href="#joints">3 Joints</a>
  <a href="#dims">4 Measured dimensions</a><a href="#findings">5 Findings</a><a href="#method">6 Method</a>
</nav>

<section id="answer">
  <h2><span class="n">1</span>Verdict — is it the same?</h2>
  <div class="verdict">
    <b>Geometry — yes, and it is measured.</b> The renders are driven by the meshes Pollen
    published, in Pollen's own kinematic tree. The {n_reb} load-bearing links we re-modelled
    parametrically reproduce the reference bounding box to a worst case of
    <b>{worst:.4f}&nbsp;mm</b> — {n_pass} of {n_reb} inside 1&nbsp;mm, six of them exact to
    the fourth decimal. The full table is in §4.
  </div>
  <div class="verdict warn">
    <b>The head does not match the product — this is a real gap.</b> Pollen's simulation head
    (<code>top_head_shell</code>, 91.751&nbsp;×&nbsp;122.688&nbsp;×&nbsp;46.339&nbsp;mm) is
    markedly longer front-to-back than the compact domed head in every product photograph, and
    the prominent eye bezel is absent from the sim mesh. We reproduce the <em>simulation</em>
    faithfully; the simulation does not reproduce the <em>product</em>. Tooling cut from this
    mesh would give the wrong head. See §5.
  </div>
  <div class="verdict">
    <b>Colour is schematic, not product paint.</b> The yellow beak and teal soles are the
    material colours inside the simulation model. Pollen's own simulator renders these same
    colours. Nothing was repainted to flatter the comparison.
  </div>
</section>

<section id="body">
  <h2><span class="n">2</span>Whole robot — real beside ours</h2>
  <p class="lede">Four viewpoints for which an official photograph exists. Our camera azimuth
  and elevation were set to match each photograph; the pose is the model's STAND keyframe with
  the head levelled.</p>
{body}
</section>

<section id="joints">
  <h2><span class="n">3</span>Joints — real beside ours</h2>
  <p class="lede">The same posed robot with the camera pushed in on each joint, against the
  corresponding region of the profile photograph. Posing costs milliseconds — the kinematics are
  already in the model, so no CAD-kernel rebuild is involved.</p>
{joints}
</section>

<section id="dims">
  <h2><span class="n">4</span>Measured dimensions — all {DIMS['count']} parts</h2>
  <p class="lede">Axis-aligned bounding box of every mesh in its own file frame, in millimetres
  to three decimal places. Reference meshes are Pollen's, converted from metres. For the
  re-modelled parts the table also gives our geometry and the worst-axis deviation to four
  decimals. Values are nominal geometry, not toleranced manufacturing dimensions — see §6.</p>
  <div class="tw"><table class="data">
    <caption>Table 1. Bounding-box dimensions and rebuild deviation. Source:
      <code>out/verify/mech_dims.json</code>, generated by <code>sim/mech_dims.py</code>.</caption>
    <thead><tr>
      <th rowspan="2">Mesh</th><th colspan="3">Reference (mm)</th>
      <th colspan="3">Ours (mm)</th><th rowspan="2">Δ max<br>(mm)</th><th rowspan="2">Verdict</th></tr>
      <tr><th class="n">X</th><th class="n">Y</th><th class="n">Z</th>
          <th class="n">X</th><th class="n">Y</th><th class="n">Z</th></tr></thead>
    <tbody>
{dim_rows()}
    </tbody>
  </table></div>
</section>

<section id="findings">
  <h2><span class="n">5</span>Findings that affect manufacturing</h2>
  <div class="tw"><table class="data">
    <thead><tr><th>#</th><th>Finding</th><th>Evidence</th><th>Consequence</th><th>Action</th></tr></thead>
    <tbody>
      <tr><td class="n">1</td><td><b>Sim head ≠ product head.</b> Simulation head shell is
        122.688&nbsp;mm front-to-back and lacks the eye bezel; product head reads far shorter and
        domed.</td>
        <td>§2 profile and three-quarter pairs; <code>top_head_shell</code> in Table 1</td>
        <td>Head tooling or prints cut from the sim mesh will not match the product.</td>
        <td>Re-model the head from photogrammetry of product photographs, or obtain the real
        head geometry, before committing head tooling.</td></tr>
      <tr><td class="n">2</td><td><b>Battery mesh is an NP-F970, not the NP-F550 class cell the
        documentation calls out.</b></td>
        <td><code>np_f970</code> 38.600&nbsp;×&nbsp;20.600&nbsp;×&nbsp;70.800&nbsp;mm in Table 1</td>
        <td>Battery bay volume and mass budget may be sized for the wrong cell.</td>
        <td>Confirm the shipping cell, then re-check <code>power_support</code> cavity against it.</td></tr>
      <tr><td class="n">3</td><td><b>Compute placeholder is a Raspberry&nbsp;Pi Zero 2&nbsp;W mesh</b>
        while the documented host is a Radxa Zero 3W.</td>
        <td><code>pcb__raspberry_pi_zero_2_w</code> 65.000&nbsp;×&nbsp;1.600&nbsp;×&nbsp;30.000&nbsp;mm</td>
        <td>Both are 65×30&nbsp;mm so the envelope holds, but connector positions differ.</td>
        <td>Verify mounting-hole and connector positions against the real Radxa Zero 3W.</td></tr>
      <tr><td class="n">4</td><td><b>Two ankle variants ship in the asset set</b>
        (<code>ankle_left</code> 36.500&nbsp;mm vs <code>ankle_l_v1</code> 46.500&nbsp;mm in Y).</td>
        <td>Table 1, rows 1–4</td>
        <td>Building the wrong revision changes ankle geometry by 10&nbsp;mm.</td>
        <td>Confirm which revision ships; the <code>_v1</code> parts appear superseded.</td></tr>
    </tbody>
  </table></div>
</section>

<section id="method">
  <h2><span class="n">6</span>Method and honest limits</h2>
  <ul>
    <li><b>Renders.</b> MuJoCo 3.12 offscreen at 1400², white studio, no floor, two directional
      fills plus a reduced headlight. Script <code>sim/compare_render.py</code>; the exact scene is
      written to <code>out/compare/_studio_scene.xml</code>.</li>
    <li><b>Measurements.</b> <code>sim/mech_dims.py</code> reads every STL through the FreeCAD
      mesh kernel and reports the axis-aligned bounding box. Reference assets are stored in
      metres and multiplied by 1000; our rebuilds are native millimetres.</li>
    <li><b>Bounding box is not a tolerance.</b> Table 1 proves overall envelope agreement. It does
      not prove feature-level agreement — that is the surface-distance check (p95 ≤ 1 mm both ways)
      recorded separately in the refcheck ledger. Neither is a manufacturing tolerance: no drawing
      dimension here carries a ± yet.</li>
    <li><b>Meshes are decimated.</b> Pollen published decimated STLs, so fine radii and small
      features are approximations of the true CAD, which was never released.</li>
    <li><b>No physical unit has been measured.</b> Every number here is derived from published
      digital assets and photographs. Nothing has been laser-scanned or callipered.</li>
  </ul>
</section>

</div>
</body>
</html>
"""
open(os.path.join(REPO, "COMPARISON.html"), "w").write(HTML)
print("wrote COMPARISON.html  parts=%d rebuilds=%d pass=%d worst=%.4f mm"
      % (DIMS["count"], n_reb, n_pass, worst))
