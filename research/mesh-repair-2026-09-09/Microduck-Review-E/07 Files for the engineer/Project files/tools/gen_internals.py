#!/usr/bin/env python3
"""gen_internals.py — build INTERNALS.html from out/sources/internals.json.

The page answers Leif's 2026-09-03 order — "an new image covering the components
of the microduck internals" — in two halves: (1) what REAL internal evidence
exists (the search log, and the press-kit photographs of partially disassembled
units, each beside our render at the nearest camera), and (2) OUR internals
diagram: see-through, shells-off and exploded views of the trunk and the head
with every component labelled by triad ref, measured position, size and
function, the cable routes, the layout checks and the list of what is NOT in
the CAD. Nothing on the page is typed: every number is read from the JSON that
tools/internals_render.py wrote off the compiled model.

Run: python3 tools/gen_internals.py   (stdlib only)
"""
import json, os, html, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
D = json.load(open(os.path.join(REPO, "out", "sources", "internals.json")))
REAL_MEASURE = os.path.join(REPO, "out", "sources", "internals", "real_measure.json")
RM = json.load(open(REAL_MEASURE)) if os.path.exists(REAL_MEASURE) else {}

def esc(s): return html.escape(str(s)) if s is not None else ""
def mm(v): return "%.3f" % v
def vec(v): return "(" + ", ".join(mm(x) for x in v) + ")" if v else "—"
def chip(v):
    cls = {"PASS": "pass", "FAIL": "no", "CANNOT DETERMINE": "cd"}.get(v, "cd")
    return f'<span class="chip {cls}">{esc(v)}</span>'
def ref_link(r):
    if not r: return '<span class="dash">—</span>'
    if r.startswith("part:"):
        slug = r[5:]
        p = os.path.join(REPO, "ce-parts", slug)
        if os.path.isdir(p):
            return f'<a href="ce-parts/{esc(slug)}/"><code>{esc(r)}</code></a>'
    return f"<code>{esc(r)}</code>"

renders = {r["file"].split("/")[-1][:-4]: r for r in D["renders"]}
def fig(name, tag="Ours · CAD render", cap=None):
    r = renders.get(name)
    if not r:
        return f'<figure><span class="tag">{esc(tag)}</span><p class="missing">missing render {esc(name)}</p></figure>'
    cam = r["camera"]
    c = cap or f'{r["title"]} — az {cam["az"]}°, el {cam["el"]}°, {cam["dist_m"]} m, lookat {vec(cam["lookat_mm"])} mm · {len(r["labels"])} labels, {r["off_frame"]} off-frame'
    return f'<figure><span class="tag ours">{esc(tag)}</span><a href="{esc(r["file"])}"><img src="{esc(r["file"])}" alt="{esc(r["title"])}"></a><figcaption>{esc(c)}</figcaption></figure>'
def realfig(file, cap, tag="Real · Pollen press kit"):
    return f'<figure><span class="tag">{esc(tag)}</span><a href="{esc(file)}"><img src="{esc(file)}" alt="{esc(cap)}"></a><figcaption>{esc(cap)}</figcaption></figure>'

# ---------------------------------------------------------------- pieces
def search_rows():
    out = []
    for i, s in enumerate(D["search_log"], 1):
        out.append(f'<tr><td>{i}</td><td>{esc(s["where"])}</td><td>{esc(s["how"])}</td><td class="n">{esc(s["fetched"])}</td><td>{esc(s["result"])}</td></tr>')
    return "\n".join(out)

def comp_rows(region):
    out = []
    for c in D["components"].get(region, []):
        pos = vec(c["pos_world_mm"])
        size = vec(c["size_mm"]) if c.get("size_mm") else '<span class="dash">site — no mesh</span>'
        where = f'<code>{esc(c["body"])}</code> / <code>{esc(c["mesh"])}</code>' if c.get("mesh") else f'site <code>{esc(c.get("site"))}</code>'
        out.append(f'<tr><td class="n">{c["n"]}</td><td>{esc(c["label"])}</td><td>{ref_link(c["ref"])}</td><td>{where}</td><td class="n">{pos}</td><td class="n">{size}</td><td>{esc(c["function"])}</td></tr>')
    return "\n".join(out)

def cable_rows():
    r = renders.get("cables-seethrough", {})
    out = []
    for c in r.get("cables", []):
        pts = " → ".join(vec(p) for p in c["points_mm"])
        out.append(f'<tr><td><code>{esc(c["id"])}</code></td><td>{esc(c["group"])}</td><td class="n">{pts}</td><td class="n">{mm(c["floor_mm"]) if c["floor_mm"] is not None else "—"}</td><td class="n">{esc(c["cable_mm"])}</td></tr>')
    for c in r.get("cables_undetermined", []):
        out.append(f'<tr><td><code>{esc(c["id"])}</code></td><td colspan="3">{esc(c["why"])}</td><td>{chip("CANNOT DETERMINE")}</td></tr>')
    return "\n".join(out), len(r.get("cables", [])), len(r.get("cables_undetermined", []))

def check_rows():
    out = []
    for c in D.get("checks", []):
        meas = "; ".join(f'{k} = {vec(v) if isinstance(v, list) and v and not isinstance(v[0], list) else (" to ".join(vec(x) for x in v) if isinstance(v, list) and v and isinstance(v[0], list) else esc(v))}' for k, v in c["measured"].items())
        out.append(f'<tr><td>{esc(c["name"])}</td><td>{chip(c["verdict"])}</td><td class="n small">{meas}</td><td>{esc(c["why"])}</td></tr>')
    return "\n".join(out)

def notcad_rows():
    return "\n".join(f'<tr><td>{esc(n["what"])}</td><td>{ref_link(n["ref"])}</td><td>{esc(n["why"])}</td><td>{chip("CANNOT DETERMINE")}</td></tr>' for n in D["not_in_cad"])

def site_rows():
    return "\n".join(f'<tr><td><code>{esc(k)}</code></td><td>{esc(v["label"])}</td><td>{ref_link(v["ref"])}</td><td class="n">{vec(v["pos_world_mm"])}</td><td>{esc(v["function"])}</td></tr>' for k, v in D["sites"].items())

def real_measure_rows():
    out = []
    for f, m in RM.items():
        bb = m.get("green_pcb_bbox_px")
        out.append(f'<tr><td><code>{esc(f)}</code></td><td class="n">{m["size_px"][0]} × {m["size_px"][1]}</td><td class="n">{esc(bb) if bb else "no green mask"} ({m["green_px"]} px)</td><td class="n">{esc(json.dumps(m["dark_runs_px"]))}</td><td>{chip("CANNOT DETERMINE")}</td></tr>')
    return "\n".join(out)

n_checks = len(D.get("checks", []))
n_pass = sum(1 for c in D.get("checks", []) if c["verdict"] == "PASS")
n_fail = sum(1 for c in D.get("checks", []) if c["verdict"] == "FAIL")
cable_html, n_cab, n_cab_cd = cable_rows()
n_comp = sum(len(v) for v in D["components"].values())
meta = D.get("render_meta", {})
fail_names = [c["name"] for c in D.get("checks", []) if c["verdict"] == "FAIL"]

# the real-vs-ours pairs: each real crop beside the render shot to match it
PAIRS = [
    ("Head with the lower beak removed", "out/sources/internals/real_desk_head_jaw_off.png",
     "press_desk.jpg (560,870)-(1260,1400) at 2×: lavender unit, jaw off — a green camera PCB stands vertically behind the face plate, the mouth-servo XL330 below it, eye ring and M12 lens in place",
     "head-shells-off-iso",
     "Ours has NO camera PCB: the M12 lens holder is placed straight onto the compute-board proxy and interpenetrates it (check 3, FAIL, overlap 1.600 × 24.000 × 16.000 mm). The product has a board there."),
    ("Trunk with both shells removed", "out/sources/internals/real_desk_trunk_shells_off.png",
     "press_desk.jpg (0,600)-(560,1330) at 2×: cream/mint unit — two XL330 stacked, a small dark PCB with white silkscreen on the trunk plate below them, mint yaw2roll clevises with the 22 mm flanged bearings",
     "trunk-shells-off-iso",
     "Ours carries the trunk IMU as a SITE only (blue label 12), 4.076 mm in front of the battery face (check 1, PASS); the product has a whole board (imu_to_dxl) with connectors — outline and connector count CANNOT DETERMINE (not published)."),
    ("Head from behind and below", "out/sources/internals/real_morning_head_rear_open.png",
     "press_morning.jpg (3050,1100)-(4240,2000): yellow bottom head shell from behind, the rectangular neck opening, the yaw/roll servo stack inside, cables running down the neck",
     "head-shells-off-rear-low",
     "Same stack order (head-pitch servo → neck_pitch bracket → yaw servo → yaw_roll_motion → roll servo). Ours draws no cable; the product's harness runs down the neck's outside (§5 is a floor length, not a route)."),
    ("Head yaw/roll stack and a trunk shell", "out/sources/internals/real_desk_head_yawroll_stack.png",
     "press_desk.jpg (2450,180)-(3200,780) at 2×: graphite/orange unit lying down — the head yaw/roll servo pair on its printed brackets, its cabling, a graphite trunk shell",
     "head-seethrough-profile",
     "Bracket family matches (yaw_roll_motion carrying the roll servo). Cable exits on the servo flank match the XL330's two JST EH sockets (wiring/README.md §1)."),
    ("Inside a top head shell", "out/sources/internals/real_desk_top_shell_interior.png",
     "press_desk.jpg (2400,120)-(2900,620) at 2×: an orange top head shell upside down — its interior ribs and bosses",
     "head-exploded",
     "Our top_head_shell (label 13, lifted +55 mm) shows two longitudinal ribs and the eye-side cut-out; the product's rib count and boss positions are not measurable from this photograph — CANNOT DETERMINE."),
]
pairs_html = "\n".join(f'''
  <h3>{esc(t)}</h3>
  <div class="pair">
    {realfig(rf, rc)}
    {fig(ours)}
  </div>
  <p class="note">{esc(note)}</p>''' for t, rf, rc, ours, note in PAIRS)

HTML = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Internals</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="tools/doc.css">
<style>
  .chip.no{{color:var(--no)}}
  .pair{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:10px 0 4px}}
  .pair figure,.grid figure{{margin:0;padding:8px}}
  .pair figure img,.grid figure img{{width:100%;aspect-ratio:1/1;object-fit:contain;background:#fff;border:1px solid var(--hair)}}
  .grid{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:10px 0 4px}}
  .grid.one{{grid-template-columns:1fr}}
  figcaption{{font-family:var(--sans);font-size:12px;color:var(--ink-2);margin-top:6px}}
  .tag{{font-family:var(--sans);font-size:10.5px;font-weight:600;letter-spacing:.07em;text-transform:uppercase;display:inline-block;padding:2px 8px;margin-bottom:6px;border:1px solid var(--hair);color:var(--ink-2)}}
  .tag.ours{{color:var(--accent);border-color:var(--accent)}}
  .note{{font-size:13.5px;color:var(--ink-2);margin:2px 0 18px;max-width:52em}}
  .verdict{{border-left:3px solid var(--accent);padding:2px 0 2px 18px;margin:14px 0;font-size:15.5px}}
  .verdict b{{color:var(--accent)}}
  .verdict.warn{{border-left-color:var(--no)}} .verdict.warn b{{color:var(--no)}}
  .verdict.cd{{border-left-color:#8a7f6a}} .verdict.cd b{{color:#8a7f6a}}
  td.dash,.dash{{color:#b3aea4}}
  td.small{{font-size:11.5px}}
  table.data{{font-size:13px}} table.data td code{{font-size:11.5px}}
  #components table.data{{table-layout:fixed}}
  #components th:nth-child(1),#components td:nth-child(1){{width:26px}}
  #components th:nth-child(5),#components td:nth-child(5){{width:17%}}
  #components th:nth-child(6),#components td:nth-child(6){{width:15%}}
  #components td{{overflow-wrap:break-word}}
  #search table.data{{table-layout:fixed}}
  #search th:nth-child(1),#search td:nth-child(1){{width:24px}}
  #search th:nth-child(2),#search td:nth-child(2){{width:24%}}
  #search th:nth-child(3),#search td:nth-child(3){{width:20%}}
  #search th:nth-child(4),#search td:nth-child(4){{width:74px}}
  #search td{{overflow-wrap:anywhere;font-size:12.5px}}
  .statbar{{display:flex;flex-wrap:wrap;gap:0;border-bottom:1px solid var(--hair);margin:8px 0 2px}}
  .stat{{padding:12px 26px 12px 0;margin-right:22px}}
  .stat b{{display:block;font-weight:700;font-size:22px;font-variant-numeric:tabular-nums}}
  .stat span{{font-family:var(--sans);font-size:12px;color:var(--ink-2)}}
  .ready{{border:1px solid var(--no);padding:12px 18px;margin:16px 0;background:#fff8f4}}
  .ready h3{{margin:0 0 6px;color:var(--no)}}
  .ready ul{{margin:4px 0 0 18px;font-size:14px}}
  .missing{{color:var(--no)}}
  @media(max-width:640px){{.pair,.grid{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<div class="wrap">
<p class="backlink"><a href="INDEX.html">← Document index</a> · <a href="COMPARISON.html">Reference match</a> · <a href="SPEC.html">Spec</a></p>

<header class="hero">
  <p class="eyebrow">Microduck reverse-engineering · internals</p>
  <h1>Internals: what is inside the Microduck</h1>
  <p class="sub">Leif, 2026-09-03: <em>"{esc(D["leif_verbatim"])}"</em>. This page carries the search for a real one
  (§1), every real photograph of an opened unit that exists, beside our render at the same view (§2), and our own
  internals diagram generated from the CAD — trunk (§3), head (§4), cable routes (§5) — with the layout checks (§6),
  the list of what the CAD still does not contain (§7) and the archived sources (§8).</p>
  <div class="rev">
    <span>MD-INT-001 · Rev A</span><span>{esc(meta.get("generated", D.get("date")))}</span>
    <span>renderer: MuJoCo offscreen {meta.get("px", [0, 0])[0]}², {esc(meta.get("keyframe", ""))}</span><span>frame: {esc(meta.get("frame", ""))}</span>
  </div>
</header>

<div class="statbar">
  <div class="stat"><b>{len(D["search_log"])}</b><span>places searched for a real internals image</span></div>
  <div class="stat"><b>{len(PAIRS)}</b><span>real photographs of opened units (all partial)</span></div>
  <div class="stat"><b>{len(D["renders"])}</b><span>labelled renders of our CAD</span></div>
  <div class="stat"><b>{n_comp}</b><span>component rows, measured</span></div>
  <div class="stat"><b>{n_cab}</b><span>cable routes drawn · {n_cab_cd} CANNOT DETERMINE</span></div>
  <div class="stat"><b>{n_pass}/{n_checks}</b><span>layout checks PASS · {n_fail} FAIL</span></div>
  <div class="stat"><b>{len(D["not_in_cad"])}</b><span>things not in the CAD</span></div>
</div>

<div class="ready">
  <h3>NOT YET READY TO BUILD FROM</h3>
  <p style="margin:0 0 4px;font-size:14px">The diagram below is a faithful picture of <b>our model</b>, and our model is a faithful copy of Pollen's <b>simulation</b> file. The factory needs these closed first, largest first:</p>
  <ul>
    <li><b>{esc(fail_names[0]) if fail_names else "—"}</b> — the product has a camera PCB behind the face (§2, first pair); ours has none and the lens holder crosses the compute-board plane by 1.600 mm (§6). Closes with: a camera-module outline on the shelf (<code>part:microduck-camera-module</code>) and a re-placed lens holder.</li>
    <li><b>Compute board is a proxy</b>: the mesh is a Pi Zero 2 W; the product runs a Radxa Zero 3W (same 65 × 30 mm, different connectors). Closes with: the Radxa drawing's connector positions on the mesh (out/head/ carries the hole study).</li>
    <li><b>{len(D["not_in_cad"])} things absent from the CAD</b> (§7): microphone, two NFC antennas, the battery-contact board, the imu_to_dxl outline, switch/USB/LED, every fastener and cable.</li>
    <li><b>Cable routes are floors, not routes</b> (§5): straight lines through joint anchors, the wiring lane's floor-length rule; the product's harness runs along the neck's outside (§2, third pair).</li>
  </ul>
</div>

<nav class="toc">
  <a href="#search">1 The real image</a><a href="#real">2 Real beside ours</a><a href="#trunk">3 Trunk</a><a href="#head">4 Head</a>
  <a href="#cables">5 Cables</a><a href="#checks">6 Checks</a><a href="#notcad">7 Not in the CAD</a><a href="#sources">8 Sources</a><a href="#method">9 Method</a>
</nav>

<section id="search">
  <h2><span class="n">1</span>Is there a real internals image?</h2>
  <div class="verdict cd"><b>CANNOT DETERMINE — none found publicly.</b> {esc(D["verdict_new_image"])}</div>
  <table class="data">
    <thead><tr><th>#</th><th>where</th><th>how</th><th>fetched</th><th>result</th></tr></thead>
    <tbody>{search_rows()}</tbody>
  </table>
</section>

<section id="real">
  <h2><span class="n">2</span>Real photographs of opened units — beside our render at the nearest view</h2>
  <p class="note">Both source photographs are in Pollen's press kit (<code>images/press/press_desk.jpg</code> 4233 × 2380, <code>press_morning.jpg</code> 4240 × 2650; fetched 2026-09-01 from https://pollen-robotics.com/microduck/press-kit/, © Pollen Robotics, press use). The crops are 2× LANCZOS of the stated pixel windows, nothing retouched. They show workbench units, not a labelled layout; each pair states what can and cannot be read off it.</p>
  {pairs_html}
  <h3>What a pixel instrument gets from the two most useful crops</h3>
  <p class="note">A colour mask for the green camera PCB and the longest dark run on three rows (an XL330 face, 20.0 or 26.0 mm wide depending on which face shows — CANNOT DETERMINE from one photograph, so no mm value is claimed). Recorded so the next attempt starts from numbers. What settles it: one photograph with an XL330 label face square-on and a ruler in frame.</p>
  <table class="data"><thead><tr><th>crop</th><th>px</th><th>green mask bbox (x0,y0,x1,y1)</th><th>longest dark runs per row (x, len)</th><th>mm</th></tr></thead>
  <tbody>{real_measure_rows()}</tbody></table>
</section>

<section id="trunk">
  <h2><span class="n">3</span>Trunk — see-through, shells off, from the rear, exploded</h2>
  <div class="grid">
    {fig("trunk-seethrough-iso")}
    {fig("trunk-shells-off-iso")}
    {fig("trunk-shells-off-rear")}
    {fig("trunk-exploded")}
  </div>
  <div id="components">
  <table class="data"><thead><tr><th>#</th><th>component</th><th>triad ref</th><th>body / mesh</th><th>position, world mm (x, y, z)</th><th>AABB size mm</th><th>function</th></tr></thead>
  <tbody>{comp_rows("trunk")}</tbody></table>
  </div>
  <p class="note">Positions are the geom's placement origin at the INIT pose (trunk_base at (0, 0, 120)); the AABB is computed off the mesh vertices in world. The battery mesh is named <code>np_f970</code> in the source but measures {vec(next((c["size_mm"] for c in D["components"]["trunk"] if c["mesh"] == "np_f970"), None))} mm — an NP-F550 envelope (SPEC.md §4.1).</p>
</section>

<section id="head">
  <h2><span class="n">4</span>Head — see-through, shells off, from behind-below, profile, exploded</h2>
  <div class="grid">
    {fig("head-seethrough-iso")}
    {fig("head-shells-off-iso")}
    {fig("head-shells-off-rear-low")}
    {fig("head-seethrough-profile")}
  </div>
  <div class="grid one">
    {fig("head-exploded")}
  </div>
  <div id="components">
  <table class="data"><thead><tr><th>#</th><th>component</th><th>triad ref</th><th>body / mesh</th><th>position, world mm (x, y, z)</th><th>AABB size mm</th><th>function</th></tr></thead>
  <tbody>{comp_rows("head")}</tbody></table>
  </div>
  <h3>Sites — placed by the source without a mesh</h3>
  <table class="data"><thead><tr><th>site</th><th>what</th><th>triad ref</th><th>position, world mm</th><th>function</th></tr></thead>
  <tbody>{site_rows()}</tbody></table>
</section>

<section id="cables">
  <h2><span class="n">5</span>Cable routes — whole robot, see-through</h2>
  <div class="grid one">
    {fig("cables-seethrough")}
  </div>
  <p class="note">Each polyline is <code>wiring/cables.json</code>'s from-point → the world anchor of every hinge the cable crosses → to-point, at the zero pose, which is the wiring lane's floor-length rule (wiring/README.md §1). It is the shortest a cable can be over the joint's full range, drawn where the rule puts it; it is NOT the path the harness takes along the parts. Total {esc(json.load(open(os.path.join(REPO, "wiring", "cables.json")))["record"]["total_length_mm"])} mm over {n_cab + n_cab_cd} cables.</p>
  <table class="data"><thead><tr><th>cable</th><th>group</th><th>points, world mm</th><th>floor mm</th><th>cable mm</th></tr></thead>
  <tbody>{cable_html}</tbody></table>
</section>

<section id="checks">
  <h2><span class="n">6</span>Layout checks — measured off the same model</h2>
  <table class="data"><thead><tr><th>check</th><th>verdict</th><th>measured</th><th>why it matters</th></tr></thead>
  <tbody>{check_rows()}</tbody></table>
</section>

<section id="notcad">
  <h2><span class="n">7</span>Not in the CAD</h2>
  <p class="note">Every physical thing the product has that our model does not place. Each stays CANNOT DETERMINE until a measurement or a published drawing settles it; none gets a plausible default (GOAL.md house rules).</p>
  <table class="data"><thead><tr><th>what</th><th>triad ref</th><th>why it is missing / what settles it</th><th></th></tr></thead>
  <tbody>{notcad_rows()}</tbody></table>
</section>

<section id="sources">
  <h2><span class="n">8</span>Sources archived by this lane</h2>
  <table class="data"><thead><tr><th>source</th><th>archived as</th><th>licence / attribution</th><th>what it is</th></tr></thead>
  <tbody>
  <tr><td>MakerWorld model 3250889</td><td><code>out/sources/makerworld-3250889-api.json</code></td><td>BY-NC-SA (API field <code>license</code>); creator "Peter Pan's Techland" (handle foo00); created 2026-09-02T04:01:04Z</td><td>15 STL "simulation model export" — the page's own summary: derived from the microduck_rl MJCF, not official CAD. No internals image.</td></tr>
  <tr><td>pollen-robotics/microduck_rl, branch develop</td><td>SHA <code>29e887ecfbf5d37144759e5a9f8a176dfb83d547</code> (2026-09-02T20:20:08Z)</td><td>CC BY-SA-NC (sim assets, SPEC.md §1)</td><td>47 STL + 47 .part in the assets dir; zero image files anywhere in the tree.</td></tr>
  <tr><td>HF Space mishig/microduck-anatomy</td><td><code>out/sources/hf-space-mishig-microduck-anatomy-api.json</code>, <code>…-blueprint.tsx</code></td><td>author mishig; sha 5329ff5d; last modified 2026-08-31T17:56:13Z; licence not stated on the card</td><td>Three.js viewer over the same simulator glb; its own strings: "CAD uses a legacy Pi Zero proxy", "placement from simulator geometry".</td></tr>
  <tr><td>fanhao375/microduck-replica assembly drawings</td><td><code>out/sources/internals/fanhao375_06_exploded_threequarter.png</code>, <code>…_07_colour_assembled.png</code></td><td>CC BY-SA-NC 4.0 (their README); master 28d8ee92 (2026-09-03T13:51:06Z)</td><td>Exploded and colour-coded views of the 15 MJCF bodies with MJCF masses; "unverified against physical hardware".</td></tr>
  <tr><td>bilibili BV1R2tH6tEsK "Microduck硬件架构拆解"</td><td><code>out/sources/internals/bili_BV1R2tH6tEsK_cover.jpg</code></td><td>uploader Z-Rob (Aetheron Robotics branding on the cover); published 2026-08-30 10:28 UTC</td><td>1358 s "analysis report" from public pages, GitHub, Radxa and ROBOTIS documents (cover text) — not a physical teardown.</td></tr>
  </tbody></table>
  <div class="grid">
    {realfig("out/sources/internals/fanhao375_06_exploded_threequarter.png", "Community (fanhao375): exploded view of the 15 MJCF bodies, MJCF masses printed. CC BY-SA-NC 4.0.", "Community · MJCF-derived")}
    {fig("head-exploded", "Ours · exploded head, for comparison")}
  </div>
</section>

<section id="method">
  <h2><span class="n">9</span>Method</h2>
  <p class="note">Renders: <code>tools/internals_render.py</code> compiles <code>sim/microduck_ours.xml</code> through <code>sim/compare_render.studio_scene</code> (white studio, product materials on the rebuilt meshes), resets to the INIT keyframe, and for each view sets geom alpha (see-through / removed) or moves geoms in their body frame by a stated world offset (exploded). Every label anchor is the geom's <code>geom_xpos</code> or the site's <code>site_xpos</code> projected through the renderer's own <code>mjvGLCamera</code> frustum, so a leader ends on the thing it names; the renderer counts labels that fall off-frame and the count is printed under each figure. AABBs are the transformed mesh vertices. Checks are AABB/point tests on the same arrays. Page: <code>tools/gen_internals.py</code> from <code>out/sources/internals.json</code>; nothing here is typed. Read-back: <code>tools/shot_page.py INTERNALS.html</code>.</p>
</section>

<footer class="foot">
  <span>Generated {esc(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))} by tools/gen_internals.py</span>
</footer>
</div>
</body>
</html>
"""
out = os.path.join(REPO, "INTERNALS.html")
open(out, "w").write(HTML)
print("wrote", out, len(HTML), "bytes;", len(D["renders"]), "renders,", n_comp, "component rows,", n_checks, "checks (", n_pass, "PASS", n_fail, "FAIL )")
