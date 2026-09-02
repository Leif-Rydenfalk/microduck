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


HEAD_PATH = os.path.join(REPO, "out", "head", "head.json")
HEAD = json.load(open(HEAD_PATH)) if os.path.exists(HEAD_PATH) else None   # tools/head_verdict.py (lane A)

ANKLE_PATH = os.path.join(REPO, "out", "laneT", "ankle-revision.json")
ANKLE = json.load(open(ANKLE_PATH)) if os.path.exists(ANKLE_PATH) else None  # tools/ankle_revision.py (lane T)


def _pm(v, u, nd=2):
    if v is None: return "CANNOT DETERMINE"
    return ("%+." + str(nd) + "f&nbsp;±&nbsp;%." + str(nd) + "f") % (v, u)


def _chip(v):
    return '<span class="chip %s">%s</span>' % ({"PASS": "pass", "FAIL": "no"}.get(v, "cd"), html.escape(v))


def head_verdict_block():
    """§1 head verdict + §5 finding-1 row + §5.1, all from out/head/head.json so this page and
    HEAD-RECONSTRUCTION.html cannot disagree. Returns None when lane A has not run."""
    if HEAD is None:
        return None
    C = HEAD["combined"]; V = HEAD["verdict"]; FV = HEAD["front_view"]["comparison"]; CV = C["verdicts"]
    cls = {"PASS": "", "FAIL": " warn", "CANNOT DETERMINE": " cd"}[V["head"]]
    settle = html.escape(" ".join(V["what_would_settle"])) if V["what_would_settle"] else "Nothing — every check PASSES."
    FP = C.get("front_pair", {})
    conseq = {"PASS": "Head tooling can be cut from the published meshes.",
              "FAIL": "Head tooling must NOT be cut from the published meshes. " + html.escape(V.get("remodel") or "")}.get(
              V["head"], "Tooling waits on one calliper reading of a product head (or one purpose-shot photograph); the 1.5 mm rule cannot be decided from the store photographs alone.")
    v1 = f"""  <div class="verdict{cls}">
    <b>The head — {html.escape(V["head"])}, measured in millimetres.</b> Lane A scaled {C["n_photos"]} product photographs by the
    XL330-M288-T case in the same frame (20.000 mm), posed our model to each with a perspective camera and compared the head shell
    against the mesh: product/mesh size ratio <b>{_pm(C["product_over_mesh"], C["product_over_mesh_unc"], 4)}</b>, head-length deviation
    <b>{_pm(C["head_length_dev_mm"], C["head_length_dev_unc_mm"])}&nbsp;mm</b> on 122.690&nbsp;mm; along the head's own axes
    {_pm(C["dev_major_mm"], C["dev_major_unc_mm"])} / {_pm(C["dev_minor_mm"], C["dev_minor_unc_mm"])}&nbsp;mm ({_chip(CV["length"])} on the length).
    The true front view grades the pair (ring OD, head width) <b>{html.escape(FP.get("verdict", "—"))}</b>: ring OD / beak width
    {FP.get("ratio_photo", 0):.4f} in the photograph against {FP.get("ratio_mesh", 0):.4f} on the mesh ({FP.get("excess_pct", 0):+.1f}&nbsp;%,
    {_pm(FP.get("dev_mm"), FP.get("unc_mm"))}&nbsp;mm at the mesh width, the same verdict at every camera distance); which member is off is CANNOT DETERMINE
    from a ratio — the profiles' ring/length agreement ({_pm(C["eye_dev_mm"], C["eye_dev_unc_mm"])}&nbsp;mm) puts it on the width (implied
    {FP.get("implied_head_width_mm_if_ring_is_mesh", 0):.2f}&nbsp;mm). The eye bezel is <b>{html.escape(V["eye_bezel"])}</b>: it is the <code>noenoeil</code>
    mesh (Ø30.000&nbsp;×&nbsp;7.5&nbsp;mm ring proud of the face), not a missing part.
    Full evidence, every overlay real-beside-ours: <a href="HEAD-RECONSTRUCTION.html">HEAD-RECONSTRUCTION.html</a>.
  </div>"""
    row = f"""      <tr><td class="n">1</td><td><b>Head conformance — {html.escape(V["head"])}.</b> Product/mesh size ratio
        {_pm(C["product_over_mesh"], C["product_over_mesh_unc"], 4)} over {C["n_photos"]} servo-scaled photographs; head length
        {_pm(C["head_length_dev_mm"], C["head_length_dev_unc_mm"])}&nbsp;mm ({html.escape(CV["length"])}); front view ring OD / head width
        {html.escape(FP.get("verdict", "—"))} ({FP.get("excess_pct", 0):+.1f}&nbsp;%, {_pm(FP.get("dev_mm"), FP.get("unc_mm"))}&nbsp;mm, attribution CANNOT DETERMINE);
        eye bezel {html.escape(V["eye_bezel"])} ({_pm(C["eye_dev_mm"], C["eye_dev_unc_mm"])}&nbsp;mm at the head's length scale, profiles).</td>
        <td><a href="HEAD-RECONSTRUCTION.html">HEAD-RECONSTRUCTION.html</a>, <code>out/head/head.json</code></td>
        <td>{conseq}</td>
        <td>{settle}</td></tr>"""
    sub = f"""  <h3 id="head">5.1 Head conformance — settled by measurement (lane A)</h3>
  <p>The scale-free ratio analysis that stood here (<code>tools/head_analysis.py</code>, +3.76&nbsp;% length ratio, +69&nbsp;% confounded aspect)
  is superseded by <a href="HEAD-RECONSTRUCTION.html">HEAD-RECONSTRUCTION.html</a>, which scales each photograph by the servo in frame, poses the
  model (jaw open, head yawed as shot, perspective camera) and measures the head in millimetres. Its numbers, from the same data file:</p>
  <div class="tw"><table class="data">
    <caption>Table 2. Head against the product, mm (product − mesh) ± uncertainty. Source: <code>out/head/head.json</code>.</caption>
    <thead><tr><th>Quantity</th><th class="n">Value</th><th>Verdict at the 1.5 mm rule</th></tr></thead>
    <tbody>
      <tr><td>size ratio product / mesh</td><td class="n">{_pm(C["product_over_mesh"], C["product_over_mesh_unc"], 4)}</td><td>—</td></tr>
      <tr><td>head length deviation (122.690 mm mesh)</td><td class="n">{_pm(C["head_length_dev_mm"], C["head_length_dev_unc_mm"])} mm</td><td>{_chip(CV["length"])}</td></tr>
      <tr><td>head silhouette, major axis</td><td class="n">{_pm(C["dev_major_mm"], C["dev_major_unc_mm"])} mm</td><td>{_chip(CV["major"])}</td></tr>
      <tr><td>head silhouette, minor axis</td><td class="n">{_pm(C["dev_minor_mm"], C["dev_minor_unc_mm"])} mm</td><td>{_chip(CV["minor"])}</td></tr>
      <tr><td>eye ring Ø (30.000 mm mesh), profile photographs</td><td class="n">{_pm(C["eye_dev_mm"], C["eye_dev_unc_mm"])} mm</td><td>{_chip(CV["eye_profile"])}</td></tr>
      <tr><td>front view: ring OD / head width — the pair (which member: CANNOT DETERMINE)</td><td class="n">{_pm(C["eye_front_view_dev_mm"], C["eye_front_view_unc_mm"])} mm at the mesh width</td><td>{_chip(CV["eye_front"])}</td></tr>
      <tr><td>eye centre below shell top (front view)</td><td class="n">{_pm(FV["eye_below_top_over_width"]["dev_mm"], FV["eye_below_top_over_width"]["dev_unc_mm"])} mm</td><td>{_chip(FV["eye_below_top_over_width"]["verdict"])}</td></tr>
      <tr><td>eye centre off the mid-line (front view)</td><td class="n">{_pm(FV["eye_x_offset_over_width"]["dev_mm"], FV["eye_x_offset_over_width"]["dev_unc_mm"])} mm</td><td>{_chip(FV["eye_x_offset_over_width"]["verdict"])}</td></tr>
      <tr><td>ToF window centre from the eye (front view vs MJCF site 22.4 mm)</td><td class="n">{_pm(FV["tof_x_from_eye_over_width"]["dev_mm"], FV["tof_x_from_eye_over_width"]["dev_unc_mm"])} mm</td><td>{_chip(FV["tof_x_from_eye_over_width"]["verdict"])}</td></tr>
    </tbody>
  </table></div>
  <div class="pair">
    <figure><span class="tag">Real · flat-lay, true front view — beside ours</span>
      <img src="out/head/front_pair.png" alt="front view real beside ours" style="aspect-ratio:auto"></figure>
    <figure><span class="tag ours">Profile fit: real | ours | overlay</span>
      <img src="{html.escape(HEAD['photos'][0]['pictures']['pair'])}" alt="profile fit" style="aspect-ratio:auto"></figure>
  </div>
  <p><b>Verdict basis.</b> {html.escape(V["basis"])}</p>
  <p><b>What would settle the rest.</b> {settle}</p>
"""
    return v1, row, sub



def ankle_row():
    """§5 finding-4 row, from out/laneT/ankle-revision.json so this page cannot contradict the
    folder that settled it. Returns the OPEN wording when lane T has not run."""
    if ANKLE is None:
        return """      <tr><td class="n">4</td><td><b>Two ankle variants ship in the asset set</b>
        (<code>ankle_left</code> 36.500&nbsp;mm vs <code>ankle_l_v1</code> 46.500&nbsp;mm in Y).</td>
        <td>Table 1, rows 1\u20134</td>
        <td>Building the wrong revision changes ankle geometry by 10&nbsp;mm.</td>
        <td>CANNOT DETERMINE \u2014 <code>out/laneT/ankle-revision.json</code> is not on disk. Run
        <code>tools/ankle_revision.py</code>.</td></tr>
"""
    n_leg = sum(1 for m in ANKLE["mjcf_inventory"] if not m["roller_kit"])
    n_rol = sum(1 for m in ANKLE["mjcf_inventory"] if m["roller_kit"])
    reads = "; ".join("%s \u2192 %s" % (html.escape(r["reading"]), html.escape(r["supports"]))
                      for r in ANKLE["readings"])
    return """      <tr><td class="n">4</td>
        <td><b>SETTLED %s \u2014 the two ankles are two locomotion VARIANTS, not two
        revisions.</b> The product in the box uses <b>ankle_left</b> / <b>ankle_right</b>.</td>
        <td>%d MJCF model(s) carry <code>ankle_left</code> with a foot and a sole and no roller
        kit; %d carry <code>ankle_l_v1</code> with <code>rim</code>/<code>tire</code>/<code>roller_blade</code>
        and no foot. Three independent readings, all agreeing: %s. Verdict %s in
        <code>out/laneT/ankle-revision.json</code> (%s), which states it plainly: \u201c%s\u201d</td>
        <td>None now \u2014 but the superseded reading would have caused one: treating
        <code>_v1</code> as an older revision deletes the roller variant's ankle.</td>
        <td>Build <code>ankle_left</code>/<code>ankle_right</code>. Still open, and it does not
        change this answer: %s</td></tr>
""" % (html.escape(ANKLE["date"]), n_leg, n_rol, reads, _chip(ANKLE["verdict"]),
       html.escape(ANKLE["date"]), html.escape(ANKLE["not_a_revision_history"]),
       html.escape(ANKLE["still_open"]))


ANKLE_ROW = ankle_row()


_hv = head_verdict_block()
if _hv:
    HEAD_V1, HEAD_ROW, HEAD_SUB = _hv
else:
    HEAD_V1 = f"""  <div class="verdict warn">
    <b>The head — CANNOT DETERMINE, and the first eyeball answer was wrong.</b> By eye the
    simulation head looks too long and flat against the product photographs, so we measured it
    (§5.1). Head <em>length</em> as a fraction of robot height agrees to
    <b>3.76&nbsp;%</b> (product 0.4233, ours 0.4392) — the head is <em>not</em> markedly longer,
    which is the opposite of the visual impression. Head <em>aspect ratio</em> differs by
    <b>+69&nbsp;%</b> (product 1.206, ours 2.042), but that measurement is confounded: in the
    reference photograph the beak is <em>open</em> and the head is <em>tilted</em>, both of which
    inflate the product's apparent head height. We therefore cannot yet conclude a geometry
    mismatch. §5.1 states exactly what would settle it.
  </div>
"""
    HEAD_ROW = f"""      <tr><td class="n">1</td><td><b>Head conformance unresolved.</b> Length ratio agrees to
        3.76&nbsp;%; aspect ratio differs by 69&nbsp;% but the measurement is confounded by an
        open beak and a tilted head in the reference photograph.</td>
        <td>§5.1, <code>out/verify/head_analysis.json</code> + annotated silhouettes</td>
        <td>Head tooling cannot be committed on present evidence — neither confirmed nor refuted.</td>
        <td>Re-shoot the comparison with the beak closed and head levelled, <em>or</em> scale a
        product photograph against the XL330 servo visible in frame (20.000&nbsp;×&nbsp;34.000&nbsp;mm)
        and measure the head shell directly in mm.</td></tr>
"""
    HEAD_SUB = f"""  <h3 id="head">5.1 Head conformance — the measurement that corrected the eyeball</h3>
  <p>Both views are near-orthographic side views on white, so scale-free silhouette ratios can be
  compared without camera calibration. The red box is the head band, ended where the silhouette
  pinches at the neck; the blue box is the whole robot. Generated by
  <code>tools/head_analysis.py</code>.</p>
  <div class="pair">
    <figure><span class="tag">Real · measured silhouette</span>
      <img src="out/verify/head-product-photo.png" alt="product head measurement"></figure>
    <figure><span class="tag ours">Ours · measured silhouette</span>
      <img src="out/verify/head-our-render.png" alt="our head measurement"></figure>
  </div>
  <div class="tw"><table class="data">
    <caption>Table 2. Scale-free head ratios. Source: <code>out/verify/head_analysis.json</code>.</caption>
    <thead><tr><th>Ratio</th><th class="n">Product photo</th><th class="n">Our render</th>
      <th class="n">Difference</th><th>Reading</th></tr></thead>
    <tbody>
      <tr><td>head length / total height</td><td class="n">0.4233</td><td class="n">0.4392</td>
        <td class="n">+3.76 %</td><td>Agrees. The head is <b>not</b> markedly longer.</td></tr>
      <tr><td>head height / total height</td><td class="n">0.3511</td><td class="n">0.2151</td>
        <td class="n">−38.7 %</td><td>Confounded — the open beak adds height to the product.</td></tr>
      <tr><td>head aspect (length / height)</td><td class="n">1.2059</td><td class="n">2.0422</td>
        <td class="n">+69.4 %</td><td>Confounded by beak state and head tilt.</td></tr>
    </tbody>
  </table></div>
  <p><b>Why this is not yet a finding.</b> In the reference photograph the beak is open and hangs
  well below the head shell, and the head is pitched forward; our render has the beak closed and
  the head levelled. Both differences inflate the product's measured head height and therefore
  depress its aspect ratio. The honest verdict is <b>CANNOT DETERMINE</b>.</p>
  <p><b>What would settle it.</b> Either (a) re-render with the beak posed open at the same angle
  as the photograph — note the jaw is <em>not</em> an actuated joint in the published model, so
  this requires posing the <code>jaw_soft</code> body by hand; or (b) photogrammetric scaling: the
  XL330-M288-T servo is visible in the same frame with a known 20.000&nbsp;×&nbsp;34.000&nbsp;mm
  body face, giving mm-per-pixel, after which the head shell can be measured directly in
  millimetres and compared with the mesh's 91.751&nbsp;×&nbsp;122.688&nbsp;×&nbsp;46.339&nbsp;mm.
  Option (b) is the stronger evidence and is the recommended next step.</p>
</section>

"""

HTML = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Reference Match</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="tools/doc.css">
<style>
  .chip.no{{color:var(--no)}}
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
  /* §5 has 5 columns of prose. Without stated widths the browser gives the widest
     cell the space and squeezes the Finding column to two words a line (MEASURED on
     the 2026-09-03 render). Stated here so every row reads. */
  #findings table.data{{table-layout:fixed;font-size:13px}}
  #findings th:nth-child(1),#findings td:nth-child(1){{width:26px}}
  #findings th:nth-child(2),#findings td:nth-child(2){{width:23%}}
  #findings th:nth-child(3),#findings td:nth-child(3){{width:29%}}
  #findings th:nth-child(4),#findings td:nth-child(4){{width:20%}}
  #findings td{{word-break:normal;overflow-wrap:break-word}}
  /* Table 1 is 11 columns wide. MEASURED with tools/tablefit.py 2026-09-03: at the
     inherited size it was 876.0 px inside an 840.0 px sheet, +36.0 px over, so the
     Verdict column sat outside any printed page while the screen showed a scrollbar
     that looked like a design choice. Tightened here and re-measured. */
  #dims table.data{{font-size:13px}}
  #dims table.data th,#dims table.data td{{padding-left:4px;padding-right:4px}}
  #dims table.data td code{{font-size:11.5px}}
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
  <a href="#dims">4 Measured dimensions</a><a href="#findings">5 Findings</a><a href="#head">5.1 Head</a><a href="#method">6 Method</a>
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
{HEAD_V1}
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
{HEAD_ROW}
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
{ANKLE_ROW}    </tbody>
  </table></div>
</section>

{HEAD_SUB}
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
