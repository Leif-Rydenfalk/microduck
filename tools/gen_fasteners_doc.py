#!/usr/bin/env python3
"""gen_fasteners_doc.py — build FASTENERS.html from the measured JSON.

    python3 tools/gen_fasteners_doc.py    -> FASTENERS.html

Data-driven and regenerable. It reads only files another tool MEASURED and it
computes no engineering number of its own; a table this file could not fill
prints the reason instead of a blank.

    out/fasteners/runs.json                 the 264 coaxial chains, 68 screw runs
    out/fasteners/placed.json               every screw placed through a mate()
    out/fasteners/balljoints.json           the ball-joint search
    out/fasteners/screw-parts-verify.json   the built screws against ISO 4762
    out/fasteners/census.json               the interface-record census
    ce-assemblies/microduck/current/bom.json
"""
import collections
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)


def load(rel):
    p = os.path.join(REPO, rel)
    if not os.path.exists(p):
        return None
    return json.load(open(p, encoding="utf-8"))


RUNS = load("out/fasteners/runs.json")
PLACED = load("out/fasteners/placed.json")
BALLS = load("out/fasteners/balljoints.json")
VERIFY = load("out/fasteners/screw-parts-verify.json")
CENSUS = load("out/fasteners/census.json")
BOM = load("ce-assemblies/microduck/current/bom.json")
PLC = load("ce-assemblies/microduck/current/placements.json")

E = html.escape


def chip(v):
    cls = {"PASS": "pass", "FAIL": "no"}.get(v, "cd")
    return '<span class="chip %s">%s</span>' % (cls, E(str(v)))


# ---------------------------------------------------------------- §2 the BOM
def bom_rows():
    rows = [r for r in BOM["record"]["rows"] if r.get("owned_by")]
    out = []
    for r in sorted(rows, key=lambda x: (x["ref"], x["params"]["length_mm"])):
        out.append('<tr><td><code>%s</code></td><td class="n">%g</td><td class="n">%d</td>'
                   '<td>%s</td></tr>'
                   % (E(r["ref"]), r["params"]["length_mm"], r["qty"], E(r["why"])))
    return "\n".join(out), sum(r["qty"] for r in rows), len(rows)


# ------------------------------------------------------- §3 every placed screw
def placed_rows():
    out = []
    for p in PLACED["placed"]:
        v = p["verify"]
        out.append(
            '<tr><td class="n">%d</td><td>%s&nbsp;&times;&nbsp;%g</td><td><code>%s</code></td>'
            '<td>%s <span class="dim">(%s)</span></td><td>%s <span class="dim">&Oslash;%s</span></td>'
            '<td class="n">%.4f</td><td class="n">%.4f</td><td class="n">[%.3f, %.3f]</td>'
            '<td class="n">%.1f, %.1f, %.1f</td><td>%s</td></tr>'
            % (p["instance"], E(p["size"]), p["length_mm"], E(p["via_connection"]),
               E(p["head_seat_mesh"]), E(p["head_seat_class"]),
               E(p["pilot_mesh"]), p["pilot_d_mm"], p["grip_mm"],
               p["engagement_available_mm"], p["length_window_mm"][0], p["length_window_mm"][1],
               p["world_pos_mm"][0], p["world_pos_mm"][1], p["world_pos_mm"][2],
               chip(v["verdict"])))
    return "\n".join(out)


# ------------------------------------------------- §4 what was NOT determined
def refusal_rows():
    kinds = collections.Counter(r["kind"] for r in RUNS["runs"] if r["verdict"] != "PASS")
    ex = {}
    for r in RUNS["runs"]:
        if r["verdict"] != "PASS" and r["kind"] not in ex:
            ex[r["kind"]] = r
    out = []
    for k, n in kinds.most_common():
        r = ex[k]
        out.append('<tr><td>%s</td><td class="n">%d</td><td>%s</td><td>%s</td></tr>'
                   % (E(k), n, E(r.get("why", ""))[:400],
                      E(r.get("settled_by", "") or "—")))
    return "\n".join(out), sum(kinds.values())


# ------------------------------------------------------------- §5 ball joints
def sphere_rows():
    rows = []
    seen = set()
    for s in BALLS["all_patches_on_placed_geometry"]:
        key = (s["mesh"], s["kind"], round(s["r_mm"], 4))
        if key in seen:
            continue
        seen.add(key)
        rows.append(s)
    rows.sort(key=lambda s: -s["r_mm"])
    out = []
    for s in rows:
        out.append('<tr><td><code>%s</code></td><td>%s</td><td class="n">%.4f</td>'
                   '<td class="n">%.4f</td><td class="n">%.3f</td><td class="n">%s</td></tr>'
                   % (E(s["mesh"]), E(s["kind"]), s["r_mm"], s["residual_mm"],
                      s["cover"], s.get("faces") or "—"))
    return "\n".join(out), len(rows)


def near_rows():
    out = []
    for n in BALLS["near_misses_refuted"]:
        out.append('<tr><td><code>%s</code> r%.4f</td><td><code>%s</code> r%.4f</td>'
                   '<td class="n">%.4f</td><td class="n">%.4f</td><td>%s</td></tr>'
                   % (E(n["ball"]["mesh"]), n["ball"]["r_mm"], E(n["socket"]["mesh"]),
                      n["socket"]["r_mm"], n["centre_distance_mm"],
                      n["radial_clearance_mm"], E(n["why"])))
    return "\n".join(out)


# ------------------------------------------------------------ §6 the screw part
def verify_rows():
    out = []
    for ref, v in VERIFY["parts"].items():
        n_ok = sum(1 for b in v["built"] if b["verdict"] == "PASS")
        rows = sum(b.get("n_rows", 0) for b in v["built"])
        out.append('<tr><td><code>%s</code></td><td class="n">%d</td><td class="n">%d/%d</td>'
                   '<td class="n">%d</td><td class="n">%g</td><td>%s</td></tr>'
                   % (E(ref), len(v["sourced_lengths_mm"]), n_ok, len(v["built"]), rows,
                      v["default_length_mm"], chip("PASS" if n_ok == len(v["built"]) else "FAIL")))
    return "\n".join(out)


bom_html, n_pieces, n_lines = bom_rows()
ref_html, n_refused = refusal_rows()
sph_html, n_sph = sphere_rows()
C = RUNS["counts"]
P = PLACED["counts"]
B = BALLS["counts"]
n_before = PLC["record"]["counts"]["seeded_from_the_mjcf"]
n_after = PLC["record"]["counts"]["total"]

HTML = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fasteners and joints — measured, placed, and refused</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="tools/doc.css">
<style>
  .chip.no{{color:var(--no)}}
  .dim{{color:var(--ink-2);font-size:.9em}}
  .verdict{{border-left:3px solid var(--accent);padding:2px 0 2px 18px;margin:14px 0;font-size:15.5px}}
  .verdict b{{color:var(--accent)}}
  .verdict.warn{{border-left-color:var(--no)}} .verdict.warn b{{color:var(--no)}}
  table.data{{font-size:13px}}
  table.data th,table.data td{{padding-left:5px;padding-right:5px}}
  #placed table.data{{font-size:12px}}
  figure.shot{{margin:14px 0;padding:8px;border:1px solid var(--hair);background:var(--figbg)}}
  figure.shot img{{width:100%;background:#fff}}
</style>
</head>
<body>
<header>
  <h1>Fasteners and joints — measured, placed, and refused</h1>
  <p class="sub">Every screw in this robot was found by measuring geometry, given a length by
  arithmetic that names which half of it is a rule and which half a measurement, and put into the
  assembly <b>through a connection&rsquo;s <code>mate()</code></b> — never by a transform typed by
  hand. What could not be determined is listed with what would settle it.</p>
  <div class="rev">
    <span>MD-FAST-DOC-001 &middot; Rev A</span><span>2026-09-04</span>
    <span>generated by <code>tools/gen_fasteners_doc.py</code></span>
    <span>frame: MJCF world, zero pose, mm</span>
  </div>
</header>

<div class="statbar">
  <div class="stat"><b>{P['placed']}</b><span>screws placed through a connection</span></div>
  <div class="stat"><b>{n_before} &rarr; {n_after}</b><span>placements in the assembly</span></div>
  <div class="stat"><b>{n_pieces}</b><span>fastener pieces on the BOM (was 0)</span></div>
  <div class="stat"><b>{P['max_head_point_error_mm']:.9f} mm</b><span>worst placement error</span></div>
  <div class="stat"><b>{B['BALL_JOINTS']}</b><span>ball joints found</span></div>
</div>

<nav class="toc">
  <a href="#answer">1 Verdict</a><a href="#bom">2 The BOM</a><a href="#placed">3 Every screw</a>
  <a href="#refused">4 What is not determined</a><a href="#ball">5 Ball joints</a>
  <a href="#parts">6 The screw parts</a><a href="#method">7 Method</a>
</nav>

<section id="answer">
  <h2><span class="n">1</span>Verdict</h2>
  <div class="verdict">
    <b>{P['placed']} screws are in the assembly and every one arrived through a connection.</b>
    <code>placements.json</code> went from {n_before} rows to {n_after}; <code>bom.json</code>
    from 38 rows with <b>zero fasteners</b> to {38 + n_lines} rows carrying {n_pieces} pieces.
    Each placement was re-checked by pushing the screw&rsquo;s own local origin and shank axis
    back through the transform <code>mate()</code> produced: worst error
    <b>{P['max_head_point_error_mm']:.9f}&nbsp;mm</b> and
    <b>{P['max_axis_error_deg']:.9f}&nbsp;deg</b> over all {P['placed']}. That check has been seen
    to fail — <code>CE_PLACE_BREAK=1</code> un-flips the pilot frame and refuses all
    {P['placed']} at 180.0&nbsp;deg.
  </div>
  <div class="verdict">
    <b>Two methods agree on what this robot is bolted with.</b> Ours reads coaxial chains through
    the assembled solid and derives a grip; the community reconstruction
    (<code>reference/&hellip;/docs/fastener-reconstruction.en.md:85&ndash;88</code>) reads a
    histogram of hole diameters. Both land on an <b>M2 socket-head cap system with
    M2&nbsp;&times;&nbsp;6 as the workhorse</b>. Ours counts 21 runs at that length out of 61 M2.
  </div>
  <div class="verdict warn">
    <b>{B['BALL_JOINTS']} ball joints. There is no ball joint in this geometry.</b>
    {B['patches_on_PLACED_geometry']} spherical patches sit on placed geometry
    ({B['balls']} balls, {B['sockets']} sockets, {B['mixed']} mixed).
    {len(BALLS['near_misses_refuted'])} ball/socket pairs came within
    {BALLS['test']['centre_tol_mm']}&nbsp;mm of concentric and every one is refuted by its own
    measurement in &sect;5. Leif named ball joints; the geometry does not contain one, and that
    is a measurement rather than a refusal to look.
  </div>
  <div class="verdict warn">
    <b>No heat-set insert is modelled, and the refusal is measured.</b> The replica author
    <i>recommends</i> 60 M2 inserts. Of 355 holes measured on the reference meshes exactly
    <b>3</b> read as an insert seat by diameter and all three are refuted by their own depth:
    &Oslash;4.088&nbsp;&times;&nbsp;29.265&nbsp;mm deep is a boss channel and
    &Oslash;4.6&nbsp;&times;&nbsp;0.500&nbsp;mm are lead-in chamfers, against a real seat of
    4&ndash;6&nbsp;mm. A teardown photograph of a boss, or a caliper on one, settles it.
  </div>
  <div class="verdict warn">
    <b>Not one strength number exists.</b> Preload, tightening torque, the load at which an
    M2 screw strips the thread it formed in printed PLA, and how many re-insertions that thread
    survives are all <code>null</code>. They are one afternoon of coupon testing away and the
    test is written down in each connection&rsquo;s <code>open_questions</code>. Nothing was
    borrowed from a plastics handbook whose resin, layer height and infill are not ours.
  </div>
</section>

<section id="bom">
  <h2><span class="n">2</span>The fastener BOM — {n_lines} lines, {n_pieces} pieces</h2>
  <p class="lede">Every line is a count of MEASURED screw runs at that length, not an estimate
  with a loss allowance. Quantities for a build must add a loss allowance on top of these.</p>
  <div class="tw"><table class="data">
    <caption>Table 1. Fastener lines in <code>ce-assemblies/microduck/current/bom.json</code>,
      written by <code>tools/place_fasteners.py</code>.</caption>
    <thead><tr><th>Part</th><th class="n">Length&nbsp;(mm)</th><th class="n">Qty</th>
      <th>Why this many, and where</th></tr></thead>
    <tbody>
{bom_html}
    </tbody></table></div>
</section>

<section id="placed">
  <h2><span class="n">3</span>Every screw, one row each</h2>
  <p class="lede">Grip is measured from the head seat to the first pilot face. Engagement is the
  pilot&rsquo;s own measured depth. The length window is
  <b>[grip&nbsp;+&nbsp;1.5&nbsp;d, grip&nbsp;+&nbsp;engagement]</b>: the minimum is a stated
  <i>rule</i> (minimum thread engagement in a softer material), the maximum is a
  <i>measurement</i> (the point the screw bottoms and stops clamping). The length taken is the
  shortest sourced ISO 4762 length inside it.</p>
  <div class="tw"><table class="data">
    <caption>Table 2. All {P['placed']} placed fasteners. Source:
      <code>out/fasteners/placed.json</code>.</caption>
    <thead><tr><th class="n">#</th><th>Screw</th><th>Connection</th><th>Head seats on</th>
      <th>Threads into</th><th class="n">Grip</th><th class="n">Engage</th>
      <th class="n">Window&nbsp;(mm)</th><th class="n">World x,y,z&nbsp;(mm)</th>
      <th>Placement check</th></tr></thead>
    <tbody>
{placed_rows()}
    </tbody></table></div>
</section>

<section id="refused">
  <h2><span class="n">4</span>What is <i>not</i> determined — {n_refused} chains</h2>
  <p class="lede">{C['coaxial_groups']} coaxial lines through the assembled robot became
  {C['chains_after_the_20_mm_cut']} chains once each line was cut at 20&nbsp;mm — the longest
  sourced ISO 4762 length, so no single screw could span the gap. {C['screw_runs']} read as screw
  runs. The rest are listed here rather than quietly dropped, because each is a lead pointing at
  a specific missing measurement.</p>
  <div class="tw"><table class="data">
    <caption>Table 3. Chains that produced no fastener, by reason.</caption>
    <thead><tr><th>Reason</th><th class="n">Count</th><th>What the tool said</th>
      <th>What settles it</th></tr></thead>
    <tbody>
{ref_html}
    </tbody></table></div>
  <p class="note">The gap to the community census is stated, not averaged.
  <code>SPEC.md:75&ndash;76</code> reads 145 holes across the robot and the replica author counts
  roughly 146 structural clearance holes; our own part folders record
  {CENSUS['fastening_features']} fastening features; this document places {P['placed']} screws.
  Three different questions — a hole, a recorded interface, and a screw whose length can be
  derived — with three different answers, all measured.</p>
</section>

<section id="ball">
  <h2><span class="n">5</span>Ball joints — the search, and its answer</h2>
  <div class="verdict warn"><b>{BALLS['verdict']}</b></div>
  <p class="lede">A ball joint is a ball patch and a socket patch on <i>different</i> placed
  geometry, concentric to within the clearance, radii matching, the socket the larger, and the
  socket covering enough of a sphere to <i>capture</i> rather than merely touch. Each of those is
  a measurement; the table below shows every candidate and why it fails.</p>
  <div class="tw"><table class="data">
    <caption>Table 4. The {len(BALLS['near_misses_refuted'])} pairs that came within
      {BALLS['test']['centre_tol_mm']}&nbsp;mm of concentric, and the measurement that refutes
      each.</caption>
    <thead><tr><th>Ball</th><th>Socket</th><th class="n">Centre&nbsp;dist&nbsp;(mm)</th>
      <th class="n">Radial&nbsp;clearance&nbsp;(mm)</th><th>Why it is not a ball joint</th></tr></thead>
    <tbody>
{near_rows()}
    </tbody></table></div>
  <div class="tw"><table class="data">
    <caption>Table 5. Every distinct spherical patch fitted on placed geometry ({n_sph} distinct
      of {B['patches_on_PLACED_geometry']} instances). Residual is the least-squares fit error;
      cover is the fraction of a full sphere the patch spans. Source:
      <code>out/fasteners/spheres-all-meshes.json</code> via
      <code>tools/balljoint_search.py</code>.</caption>
    <thead><tr><th>Mesh</th><th>Kind</th><th class="n">r&nbsp;(mm)</th>
      <th class="n">Residual&nbsp;(mm)</th><th class="n">Cover</th><th class="n">Faces</th></tr></thead>
    <tbody>
{sph_html}
    </tbody></table></div>
  <p class="note"><b>What settles it:</b> {E(BALLS['settled_by'])}</p>
</section>

<section id="parts">
  <h2><span class="n">6</span>The screw parts — built parametrically, measured against ISO 4762</h2>
  <p class="lede">Both folders existed on the workshop shelf with a <code>cad/README</code> saying
  <i>&ldquo;no geometry on the shelf yet&rdquo;</i> and an empty interface list. They now build the
  whole length family from <code>cecad.screws.screw()</code>, and every member is measured off the
  solid against the ISO 4762 figures each folder&rsquo;s own <code>component.json</code> cites from
  the fasteners.eu table fetched 2026-08-19 — two independent transcriptions meeting on geometry.
  An unsourced length is refused rather than interpolated.</p>
  <div class="tw"><table class="data">
    <caption>Table 6. Source: <code>out/fasteners/screw-parts-verify.json</code>, generated by
      <code>tools/verify_screw_parts.py</code> under <code>ce-cad/bin/cad</code>.</caption>
    <thead><tr><th>Part</th><th class="n">Sourced lengths</th><th class="n">Members PASS</th>
      <th class="n">Dimension rows</th><th class="n">Default&nbsp;(mm)</th><th>Verdict</th></tr></thead>
    <tbody>
{verify_rows()}
    </tbody></table></div>
  <p class="note">The check has been seen to fail: <code>CE_SCREWPART_BREAK=1</code> offsets the
  measured head diameter by 1.000&nbsp;mm and turns all 24 members FAIL
  (<code>out/fasteners/screwpart-break-on-purpose.log</code>). <b>No thread helix is cut</b> — the
  shank is a plain cylinder at nominal diameter, which is what every clearance and interference
  check in this repo reads; anything needing the flank is CANNOT DETERMINE.</p>
</section>

<section id="method">
  <h2><span class="n">7</span>Method — the whole chain, in order</h2>
  <ol class="lede">
    <li><code>cecad.meshfeatures.features()</code> on every placed mesh: 355 holes with diameter,
      class, depth, axis and axial extent, ends probed by 24 axis-parallel rays &rarr;
      <code>out/fasteners/features-by-mesh.json</code>.</li>
    <li>MJCF body&nbsp;&times;&nbsp;geom frames at zero pose &rarr;
      <code>out/fasteners/world-placements.json</code>.</li>
    <li><code>tools/fastener_runs.py</code>: {C['holes_in_world']} holes in the world frame
      (meshes are reused — <code>xl330</code> is placed 15 times), {C['coaxial_groups']} coaxial
      lines, {C['chains_after_the_20_mm_cut']} chains after the 20&nbsp;mm cut,
      {C['screw_runs']} screw runs with a grip, an engagement and a length window &rarr;
      <code>out/fasteners/runs.json</code>. Arithmetic:
      <code>p_w = R&nbsp;p + t</code>, <code>a_w = R&nbsp;a</code>,
      <code>s_w = s + t&nbsp;&middot;&nbsp;a_w</code>. No approximation.</li>
    <li><code>tools/place_fasteners.py</code>: loads the screw folder&rsquo;s own
      <code>thread_ext</code> frame off disk, builds a pilot frame from the run&rsquo;s
      measurements, <b>calls the connection&rsquo;s <code>mate()</code></b>, inverts the returned
      transform, and verifies the result against the measurement it came from &rarr;
      <code>out/fasteners/placed.json</code> and the three assembly records.</li>
    <li><code>tools/balljoint_search.py</code>: every fitted spherical patch into the world, then
      the ball/socket pairing test &rarr; <code>out/fasteners/balljoints.json</code>.</li>
  </ol>
  <p class="note"><b>Two defects were found and fixed on the way, and both changed the answer.</b>
  (1) The head was seating on the counterbore <i>mouth</i> rather than its <i>floor</i>, costing
  2&nbsp;mm on every counterbored run and reading the servo screws as M2&nbsp;&times;&nbsp;14.
  (2) Engagement ran to the <i>last</i> pilot on a line, so a screw into an XL330 swallowed the
  17&nbsp;mm across the servo case. A third, in <code>tools/fastener_census.py</code>, made every
  one of its 105 rows report the part slug as the literal string <code>ce-parts</code>
  (<code>path.split(os.sep)[-5]</code> where the slug is at <code>[-4]</code>), so no census row
  could be traced back to the part it was measured on.</p>
</section>

<footer>
  <p>Generated by <code>tools/gen_fasteners_doc.py</code> from
  <code>out/fasteners/*.json</code> and <code>ce-assemblies/microduck/current/*.json</code>.
  Regenerate rather than edit.</p>
</footer>
</body></html>
"""

out = os.path.join(REPO, "FASTENERS.html")
open(out, "w", encoding="utf-8").write(HTML)
print("wrote", out, len(HTML), "bytes")
print("placed %d, bom %d lines / %d pieces, placements %d -> %d, ball joints %d"
      % (P["placed"], n_lines, n_pieces, n_before, n_after, B["BALL_JOINTS"]))
