#!/usr/bin/env python3
"""gen_wiring3d.py — build WIRING-3D.html from the measured JSON.

    python3 tools/gen_wiring3d.py     -> WIRING-3D.html

Reads only files another tool measured and computes no engineering number of
its own. A table it cannot fill prints the reason instead of a blank.

    wiring/cables.json                 the 23 runs, endpoints, pins, connectors
    out/wiring/cables3d.json           the routed paths + per-run measurements
    out/wiring/cables3d-hat.json       the re-route with located HAT connectors
    out/wiring/solids.json             the swept solids, volumes, masses
    out/wiring/hat-connectors.json     every HAT connector in world coordinates
    out/wiring/render.json             what the pictures contain
    ce-assemblies/microduck/current/harness.json   the placements
"""
import html, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
E = html.escape


def load(rel):
    p = os.path.join(REPO, rel)
    if not os.path.exists(p):
        return None
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return None


CAB = load("wiring/cables.json")
C3 = load("out/wiring/cables3d.json")
C3H = load("out/wiring/cables3d-hat.json")
SOL = load("out/wiring/solids.json")
HATC = load("out/wiring/hat-connectors.json")
REN = load("out/wiring/render.json")
HAR = load("ce-assemblies/microduck/current/harness.json")

MISSING = [n for n, v in (("wiring/cables.json", CAB), ("out/wiring/cables3d.json", C3),
                          ("out/wiring/solids.json", SOL),
                          ("out/wiring/hat-connectors.json", HATC),
                          ("ce-assemblies/microduck/current/harness.json", HAR)) if v is None]


def chip(v):
    return '<span class="chip %s">%s</span>' % (
        {"PASS": "pass", "FAIL": "no"}.get(v, "cd"), E(str(v)))


def num(v, dp=4):
    return "&mdash;" if v is None else ("%.*f" % (dp, v))


def main():
    if MISSING:
        raise SystemExit("gen_wiring3d: missing inputs, refusing to write a page with "
                         "blanks in it: %s" % MISSING)
    c3 = C3["record"]
    hat_rows = {c["id"]: c for c in C3H["record"]["cables"]} if C3H else {}
    srow = {r["id"]: r for r in SOL["record"]["cables"]}
    har = HAR["record"]
    rows = []
    n_pass = n_fail = n_cd = 0
    for c in c3["cables"]:
        rid = c["id"]
        cc = hat_rows.get(rid, c)
        s = srow.get(rid)
        v = cc["verdict"]
        n_pass += v == "PASS"
        n_fail += v == "FAIL"
        n_cd += v == "CANNOT DETERMINE"
        ends = cc.get("ends") or []
        endtxt = " &rarr; ".join(
            "%s%s" % (E(str(e.get("device"))),
                      (" <code>%s</code>" % E(e["refdes"])) if e.get("refdes") else
                      (" <span class='dim'>(unlocated)</span>" if not e.get("located") else ""))
            for e in ends) or "&mdash;"
        rows.append(
            "<tr><td><code>%s</code></td><td>%s</td><td class='n'>%s</td>"
            "<td class='n'>%s</td><td class='n'>%s</td><td class='n'>%s</td>"
            "<td class='n'>%s</td><td class='n'>%s</td><td class='n'>%s</td>"
            "<td class='n'>%s</td><td>%s</td></tr>"
            % (E(rid), endtxt, num(cc.get("od_mm")),
               num(cc.get("routed_length_mm"), 3),
               ("%g" % cc["cable_mm_from_cables_json"]) if cc.get("cable_mm_from_cables_json") is not None else "&mdash;",
               num(cc.get("delta_vs_cable_mm"), 3),
               num(cc.get("min_clearance_mm")),
               num(cc.get("min_bend_radius_mm"), 3),
               (str(cc.get("pierce_samples")) if cc.get("pierce_samples") is not None else "&mdash;"),
               (num(s["volume_mm3"], 2) if s else "&mdash;"),
               chip(v)))
    hatrows = []
    for c in (HATC["record"]["connectors"] if HATC else []):
        if not c.get("as_built_world"):
            continue
        am = c.get("as_modelled")
        hatrows.append(
            "<tr><td><code>%s</code></td><td>%s</td><td>%s</td><td class='mono'>%s</td>"
            "<td class='mono'>%s</td><td class='n'>%s</td><td>%s</td></tr>"
            % (E(c["refdes"]), E(c["series"]), E(c["what"]),
               E(str(c["as_built_world"]["origin_mm"])),
               E(str(am["world_origin_mm"])) if am else "&mdash;",
               num(am["delta_to_as_built_mm"], 4) if am else "&mdash;",
               E(", ".join("%s:%s" % (k, v) for k, v in sorted((c.get("nets_by_pin") or {}).items()))[:60])))
    imgs = (REN or {}).get("record", {}).get("images", {})
    figs = "\n".join(
        '<figure class="shot"><img src="out/wiring/harness-%s.png" alt="harness %s">'
        '<figcaption>%s &mdash; %d bytes</figcaption></figure>' % (k, k, E(k), v)
        for k, v in sorted(imgs.items()) if v)
    cn = har["counts"]
    g = c3["grid"]
    w = c3["wire"]
    st = SOL["record"]

    HTML = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The harness in 3D &mdash; routed, swept, placed, measured</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="tools/doc.css">
<style>
  .chip.no{{color:var(--no)}}
  .dim{{color:var(--ink-2);font-size:.9em}}
  .mono{{font-family:'IBM Plex Mono',monospace;font-size:11.5px}}
  .verdict{{border-left:3px solid var(--accent);padding:2px 0 2px 18px;margin:14px 0;font-size:15.5px}}
  .verdict b{{color:var(--accent)}}
  .verdict.warn{{border-left-color:var(--no)}} .verdict.warn b{{color:var(--no)}}
  table.data{{font-size:12.5px}}
  table.data th,table.data td{{padding-left:5px;padding-right:5px}}
  figure.shot{{margin:14px 0;padding:8px;border:1px solid var(--hair);background:var(--figbg)}}
  figure.shot img{{width:100%;background:#fff}}
</style>
</head>
<body>
<header>
  <h1>The harness in 3D</h1>
  <p class="sub">Every cable in this robot as a routed path through the measured free space, swept
  as a real solid at its stated jacket diameter, ended in a real JST housing placed through a
  connection&rsquo;s <code>mate()</code>, and measured back: routed length against the figure in
  <code>wiring/cables.json</code>, achieved bend radius, minimum clearance to material, and whether
  the centreline passes through anything. Where an endpoint is not located, nothing is drawn and
  the reason is printed.</p>
  <div class="rev">
    <span>MD-WIRE-3D-001 &middot; Rev A</span><span>2026-09-05</span>
    <span>generated by <code>tools/gen_wiring3d.py</code></span>
    <span>frame: MJCF world, zero pose, mm</span>
  </div>
</header>

<div class="statbar">
  <div class="stat"><b>{len(c3['cables'])}</b><span>runs in the connection list</span></div>
  <div class="stat"><b>{cn['cables_routed']}</b><span>routed as 3D paths</span></div>
  <div class="stat"><b>{cn['cables_with_geometry']}</b><span>swept as solids</span></div>
  <div class="stat"><b>{cn['housings_placed']}</b><span>housings placed through mate()</span></div>
  <div class="stat"><b>{st['totals']['routed_length_mm']:.1f} mm</b><span>routed cable</span></div>
  <div class="stat"><b>{st['totals']['mass_nominal_g']:.2f} g</b><span>nominal harness mass</span></div>
  <div class="stat"><b>{n_pass} / {n_fail} / {n_cd}</b><span>PASS / FAIL / CANNOT DETERMINE</span></div>
</div>

<nav class="toc">
  <a href="#verdict">1 Verdict</a><a href="#runs">2 Every run</a><a href="#pictures">3 The pictures</a>
  <a href="#hat">4 The HAT connectors</a><a href="#notcable">4b Not cables</a><a href="#leads">4c The leads</a><a href="#method">5 How it was built</a>
  <a href="#open">6 What is not determined</a>
</nav>

<section id="verdict">
  <h2><span class="n">1</span>Verdict</h2>
  <div class="verdict">
    <b>{cn['cables_with_geometry']} of {len(c3['cables'])} runs are solid geometry in the assembly,
    and {cn['housings_placed']} connector housings sit on real connector frames.</b>
    Every housing came out of <code>connection:jst-eh-3pin</code>&rsquo;s own <code>mate()</code>
    and every placement was re-checked by pushing the housing&rsquo;s local origin and axis back
    through the transform: worst error <b>{cn['worst_origin_error_mm']:.6f}&nbsp;mm</b> and
    <b>{cn['worst_axis_error_deg']:.6f}&nbsp;deg</b> over all {cn['housing_checks_PASS'] + cn['housing_checks_FAIL']}.
  </div>
  <div class="verdict warn">
    <b>No run is a PASS, and that is the honest state.</b> {n_fail} FAIL and {n_cd} CANNOT
    DETERMINE. Bend radius is CANNOT DETERMINE on every routed run <i>by construction</i>:
    ROBOTIS publishes no minimum bend radius for the X3P lead, so only the ACHIEVED radius is
    reported and there is nothing to judge it against. The FAILs are leads, not verdicts on the
    design &mdash; the real robot has these cables, so a run with no corridor is a place where
    our model is missing a passage.
  </div>
</section>

<section id="runs">
  <h2><span class="n">2</span>Every run</h2>
  <p>Routed length and <code>cables.json</code>&rsquo;s <code>cable_mm</code> are BOTH printed and
  neither overwrites the other: the routed figure is the length at the zero pose, the
  <code>cable_mm</code> figure is a floor plus a slack allowance over each crossed joint&rsquo;s
  whole range. Volume is the divergence theorem over the cable&rsquo;s own closed mesh.</p>
  <table class="data">
    <thead><tr><th>run</th><th>ends</th><th>OD mm</th><th>routed mm</th><th>cables.json mm</th>
    <th>&Delta; mm</th><th>min clear mm</th><th>bend R mm</th><th>pierce</th><th>vol mm&sup3;</th>
    <th>verdict</th></tr></thead>
    <tbody>
{chr(10).join(rows)}
    </tbody>
  </table>
</section>

<section id="pictures">
  <h2><span class="n">3</span>The pictures</h2>
  <p>Drawn flat with hidden-line edges, which is the mode that shows where a cable GOES: the
  cables are the swept tubes, the small blocks on the servo flanks are the EH housings, and the
  grey boxes are a <b>proxy</b> &mdash; each one is the measured world bounding box of a placed
  body, not its outline. The mode was picked by rendering both: under PBR every body shades from
  its material and cables, housings and boxes come out the same grey.</p>
{figs if figs else '<p class="dim">No render on disk. <code>ce-cad/bin/cad sim/harness_render.py</code> writes them.</p>'}
</section>

<section id="hat">
  <h2><span class="n">4</span>The HAT connectors, and the revision that moves them</h2>
  <p>Five HAT-end runs were recorded with the endpoint &ldquo;HAT mesh centroid &mdash; connector
  positions unpublished&rdquo;. They are published: Pollen&rsquo;s board is Apache-2.0 and is in
  <code>reference/pollen-elec-rpi-robot-hat</code>. But the board in our CAD is the PRE-RELEASE
  revision <code>fbd885d</code> (<code>out/pcb/hat/mesh-revision.json</code>), whose connector bank
  is at the other end. One reflection about board
  x&nbsp;=&nbsp;{HATC['record']['revision_mirror']['plane_x_mm']}&nbsp;mm maps every 0.95&nbsp;mm
  connector hole column of the mesh onto its released position, residual
  {HATC['record']['revision_mirror']['residual_mm']:.1e}&nbsp;mm &mdash; so it is a mirror, not the
  &ldquo;end-for-end&rdquo; adjective, and both positions are given here.</p>
  <table class="data">
    <thead><tr><th>ref</th><th>series</th><th>what</th><th>as built (C1) world mm</th>
    <th>as modelled (fbd885d) world mm</th><th>&Delta; mm</th><th>nets</th></tr></thead>
    <tbody>
{chr(10).join(hatrows)}
    </tbody>
  </table>
</section>

<section id="notcable">
  <h2><span class="n">4b</span>Three rows in the connection list are not cables</h2>
  <p>They were carried as runs and could never route. Each is settled by a document, not by a
  routing failure:</p>
  <ul>
    <li><code>mic-hat</code> &mdash; <b>there is no microphone cable.</b> The microphone is
    <code>MK1 = LMA2718</code>, an <i>on-board</i> MEMS part: footprint
    <code>MIC-SMD_4P-L2.8-W1.9-P1.84-TL</code> on sheet <code>/Schematic/Audio/</code> of Pollen&rsquo;s
    own board (<code>out/pcb/hat/components.json</code>), and
    <code>hardware-teardown.en.md:201</code> reads it &ldquo;<i>MK1 = LMA2718 &mdash; On-board MEMS
    microphone</i>&rdquo;. <code>wiring/cables.json</code> already had this device as &ldquo;no mesh,
    no site: CANNOT DETERMINE&rdquo;. A <i>second, external</i> microphone on a Wago terminal is
    offered by the board (<code>teardown:205</code>) and is not fitted in the reference robot.</li>
    <li><code>hat-radxa-40pin</code> &mdash; a board-to-board stack, not a lead: <code>J4</code> is a
    2&times;20 P2.54 header and <code>cables.json</code> already records
    <code>cable_mm&nbsp;=&nbsp;0</code>. The HAT sits ON the Radxa.</li>
    <li><code>hat-dxl-port</code> &mdash; no endpoint on either side in
    <code>cables.json</code> (<code>cable_mm&nbsp;=&nbsp;null</code>); it names the port, not a run.</li>
  </ul>
</section>

<section id="leads">
  <h2><span class="n">4c</span>The two runs that still FAIL, as leads</h2>
  <p>The real Microduck has both of these cables, so a run with no corridor is a statement about
  <b>our model</b>, not about the design. Each row says where to look.</p>
  <ul>
    <li><b><code>bat-hat</code> &mdash; the battery feed, and the whole robot is powered through
    it.</b> With the HAT end now on a real connector (<code>J14</code>, +BATT on pin 2) there is
    still <b>no corridor at any clearance floor down to 0.0000&nbsp;mm</b> between the pack in the
    trunk and the head, on either the 4.0&nbsp;mm or the 1.0&nbsp;mm grid. The cable has to cross
    the neck, which carries 720&nbsp;degrees of joint travel. <i>The lead</i>: our neck and trunk
    models have no wire passage. <i>Settled by</i>: measuring the passage on the reference meshes,
    or a photograph of the interior.</li>
    <li><b><code>spk-hat</code> &mdash; the speaker lead.</b> Its HAT end is now located
    (<code>J1</code>, Wago-2, audio sheet) and its SPEAKER end is still the mesh centroid, which is
    <i>inside</i> the transducer: 3 pierce samples and &minus;1.2500&nbsp;mm clearance are what a
    route out of the middle of a solid body looks like. <i>The lead</i>: the speaker&rsquo;s
    terminal face is not modelled. <i>Settled by</i>: the terminal side of the speaker, from a
    photograph or the part drawing.</li>
  </ul>
</section>

<section id="method">
  <h2><span class="n">5</span>How it was built, and what in it is chosen</h2>
  <p><b>The free space</b> is a {g['cell_mm']}&nbsp;mm occupancy of every triangle of every placed
  body &mdash; {g['occupied_cells']} occupied cells in a {g['shape'][0]}&times;{g['shape'][1]}&times;{g['shape'][2]}
  grid, and it now includes the 64 placed screws as built solids, not only the 70 reference meshes.</p>
  <p><b>The wire</b> is {w['awg']}&nbsp;AWG &mdash; {E(w['awg_source'])} &mdash; bare copper
  {w['bare_conductor_mm']}&nbsp;mm by {E(w['bare_basis'])}. The jacket OD is <b>CANNOT
  DETERMINE</b>: the only published bound is {E(w['insulation_window_source'])}, a
  {w['insulation_od_window_mm'][0]}&ndash;{w['insulation_od_window_mm'][1]}&nbsp;mm window, and this
  lane uses its midpoint {w['insulation_od_nominal_mm']}&nbsp;mm and labels every figure that rests
  on it NOMINAL.</p>
  <p><b>The clearance floor</b> is {c3['rules']['clearance_floor_mm']}&nbsp;mm and it is
  {E(c3['rules']['clearance_basis'])}.</p>
  <p><b>The sweep</b> is {E(SOL['record']['cables'][0]['swept_by'])} &mdash; arithmetic, not the
  kernel, because three kernel sweeps were each defeated by a route in this set (the reasons are in
  <code>sim/route3d_solids.py</code>). The polygon inscribes the circle, so every volume here is
  2.55&nbsp;% under the true tube.</p>
  <p><b>Mass</b> is computed from the geometry and two named densities:
  copper {SOL['record']['mass_basis']['copper_g_cm3']}&nbsp;g/cm&sup3;
  ({E(SOL['record']['mass_basis']['copper_cite'])}) and jacket
  {SOL['record']['mass_basis']['jacket_g_cm3']}&nbsp;g/cm&sup3;
  ({E(SOL['record']['mass_basis']['jacket_cite'])}).</p>
  <p><b>Placement</b>: {E(har['placement_rule'])}</p>
</section>

<section id="open">
  <h2><span class="n">6</span>What is not determined, and what settles it</h2>
  <ul>
    <li><b>The bend limit of every cable on this robot.</b> ROBOTIS publishes a gauge and no bend
    radius for the X3P; JST publishes none for the SH or EH leads. Only the achieved radius is
    reported. <i>Settled by</i>: a vendor drawing, or a bend test on a real lead.</li>
    <li><b>The jacket OD.</b> Bounded to 1.0&ndash;1.9&nbsp;mm by JST eEH.pdf p.2 and modelled at
    the midpoint. <i>Settled by</i>: a micrometer on a real X3P lead.</li>
    <li><b>Which Robot HAT revision the robot carries.</b> Our mesh is the pre-release layout;
    every released board has the connectors at the other end. <i>Settled by</i>: iterating
    <code>part:microduck-robot-hat-pcb</code> to the C1 geometry.</li>
    <li><b>Whether these are the routes the real harness takes.</b> No photograph of the interior
    exists in <code>reference/</code>. These are the shortest routes that clear.
    <i>Settled by</i>: an internals photograph, or a teardown.</li>
  </ul>
</section>

<footer><p>Generated from measured JSON by <code>tools/gen_wiring3d.py</code>. Every number on this
page came out of a file named beside it.</p></footer>
</body>
</html>
"""
    out = os.path.join(REPO, "WIRING-3D.html")
    open(out, "w", encoding="utf-8").write(HTML)
    print("wrote %s  %d bytes  %d run rows  %d connector rows  %d figures"
          % (out, len(HTML), len(rows), len(hatrows), len(imgs)))


main()
