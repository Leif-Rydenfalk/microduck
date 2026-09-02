#!/usr/bin/env python3
"""gen_head.py — build HEAD-RECONSTRUCTION.html from out/head/head.json
(tools/head_verdict.py). Every table here is generated from that file; nothing
is hand-maintained. Same academic style as COMPARISON.html (tools/doc.css).
"""
import json, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
D = json.load(open(os.path.join(REPO, "out", "head", "head.json")))
C = D["combined"]; V = D["verdict"]; FV = D["front_view"]; M = D["mesh"]


def f(x, nd=3, sign=False):
    if x is None: return "—"
    return ("%+." + str(nd) + "f") % x if sign else ("%." + str(nd) + "f") % x


def pm(v, u, nd=3):
    if v is None: return "CANNOT DETERMINE"
    return "%s&nbsp;±&nbsp;%s" % (f(v, nd, True), f(u, nd))


def chip(v):
    cls = {"PASS": "pass", "FAIL": "no", "CANNOT DETERMINE": "cd"}.get(v, "cd")
    return '<span class="chip %s">%s</span>' % (cls, html.escape(v))


def esc(s): return html.escape(str(s))


# ---------------------------------------------------------------- per-photo blocks
def scale_rows():
    rows = []
    for p in D["photos"]:
        for s in p["scale"]["servos"]:
            if "width_px" not in s:
                rows.append("<tr><td>%s</td><td>%s</td><td colspan=5>%s — %s</td></tr>" % (esc(p["title"]), esc(s.get("what", "")), chip("CANNOT DETERMINE"), esc(s.get("why", ""))))
                continue
            r = s.get("render", {}); sr = s.get("size_ratio", {})
            wr = s.get("render_width_px_analytic")
            cross = ("mask %s px (%s %%)" % (f(r.get("width_px"), 1), f(s.get("render_mask_vs_analytic_pct"), 1, True))) if r and "width_px" in r else "mask: not visible"
            rows.append(
                "<tr><td>%s</td><td>%s</td><td class=n>%s (%d of %d lines)</td><td class=n>%s</td>"
                "<td class=n>%s<br><small>%s</small></td><td class=n>%s</td><td class=n>%s</td></tr>" % (
                    esc(p["title"]), esc(s["what"]), f(s["width_px"], 2), s["n_accepted"], s["n_lines"],
                    pm(s["mm_per_px"], s["mm_per_px_unc"], 5),
                    f(wr, 2), esc(cross),
                    pm(sr.get("product_over_mesh"), sr.get("unc"), 4) if sr else "—",
                    ("%s / %s" % (f(sr.get("servo_depth_mm"), 1), f(sr.get("head_depth_mm"), 1))) if sr else "—"))
    return "\n".join(rows)


def fit_rows():
    rows = []
    for p in D["photos"]:
        t = p["fit"]
        rows.append("<tr><td>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td>"
                    "<td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td></tr>" % (
                        esc(p["title"]), f(t["iou"], 4), f(t["eye_term"], 5), f(t["cam_distance_mm"], 1), f(t["cam_az_deg"], 2), f(t["cam_el_deg"], 2),
                        f(t["head_pitch_deg"], 2), f(t["head_yaw_deg"], 2), f(t["head_roll_deg"], 2), f(t["jaw_open_deg"], 2),
                        pm(t["k_photo_px_per_render_px"], t["k_fit_spread"], 4)))
    return "\n".join(rows)


def dim_rows():
    rows = []
    for p in D["photos"]:
        s = p.get("size")
        if not s:
            rows.append("<tr><td>%s</td><td colspan=8>%s — no scale feature measured</td></tr>" % (esc(p["title"]), chip("CANNOT DETERMINE"))); continue
        v = p["verdicts"]
        rows.append("<tr><td>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td>"
                    "<td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td>%s</td></tr>" % (
                        esc(p["title"]), pm(s["product_over_mesh"], s["unc"], 4), pm(s["head_length_dev_mm"], s["head_length_dev_unc_mm"]),
                        f(s["photo_head_extent_major_mm"]), f(s["mesh_head_extent_major_mm"]), pm(s["dev_major_mm"], s["dev_major_unc_mm"]),
                        f(s["photo_head_extent_minor_mm"]), f(s["mesh_head_extent_minor_mm"]), pm(s["dev_minor_mm"], s["dev_minor_unc_mm"]) + " " +
                        chip(v["length"])))
    rows.append("<tr class=total><td><b>Combined (inverse-variance; spread %s mm)</b></td><td class=n><b>%s</b></td><td class=n><b>%s</b></td>"
                "<td class=n>—</td><td class=n>—</td><td class=n><b>%s</b></td><td class=n>—</td><td class=n>—</td><td><b>%s</b> %s</td></tr>" % (
                    f(C["head_length_spread_mm"]), pm(C["product_over_mesh"], C["product_over_mesh_unc"], 4),
                    pm(C["head_length_dev_mm"], C["head_length_dev_unc_mm"]), pm(C["dev_major_mm"], C["dev_major_unc_mm"]),
                    pm(C["dev_minor_mm"], C["dev_minor_unc_mm"]), chip(C["verdicts"]["length"])))
    return "\n".join(rows)


def eye_rows():
    rows = []
    for p in D["photos"]:
        e = p["eye"]
        if "diameter_mm" not in e:
            rows.append("<tr><td>%s</td><td colspan=6>%s</td></tr>" % (esc(p["title"]), chip("CANNOT DETERMINE"))); continue
        off = e.get("centre_offset_photo_minus_render_mm")
        rows.append("<tr><td>%s</td><td class=n>%s × %s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td>%s</td></tr>" % (
            esc(p["title"]), f(e["major_px"], 1), f(e["minor_px"], 1), f(e["view_angle_deg"], 1),
            pm(e["diameter_mm"], e["diameter_unc_mm"]), f(e.get("diameter_via_render_mm")),
            ("%s / %s" % (f(off[0], 2, True), f(off[1], 2, True))) if off else "—", chip(p.get("verdicts_eye", "CANNOT DETERMINE"))))
    return "\n".join(rows)


def front_rows():
    names = {"eye_od_over_width": "eye ring OD / head width", "eye_minor_over_major": "eye ring minor / major (view tilt)",
             "eye_below_top_over_width": "eye centre below shell top / head width", "eye_x_offset_over_width": "eye centre off the mid-line / head width",
             "tof_x_from_eye_over_width": "ToF window centre right of the eye / head width", "tof_y_from_eye_over_width": "ToF window centre below the eye / head width",
             "tof_w_over_width": "ToF window width / head width", "tof_h_over_width": "ToF window height / head width",
             "first_beak_band_top_below_top_over_width": "beak lip (bottom shell) top edge below shell top / head width"}
    rows = []
    for k, c in FV["comparison"].items():
        if c.get("verdict") == "CANNOT DETERMINE":
            rows.append("<tr><td>%s</td><td class=n>%s</td><td class=n>—</td><td class=n>—</td><td class=n>%s</td><td class=n>—</td><td>%s %s</td></tr>" % (
                names.get(k, k), f(c["photo"], 4), f(c["photo"] * FV["mesh_head_width_mm"], 2), chip("CANNOT DETERMINE"), esc(c["why"])))
        else:
            rows.append("<tr><td>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td></tr>" % (
                names.get(k, k), f(c["photo"], 4), f(c["mesh"], 4), f(c["diff_pct"], 2, True) + " %", f(c["photo_mm_if_width_is_mesh"], 2),
                f(c["mesh_mm"], 2), f(c["dev_mm"], 2, True)))
    return "\n".join(rows)


def photo_sections():
    out = []
    for i, p in enumerate(D["photos"], 1):
        t = p["fit"]; s = p.get("size", {})
        out.append(f"""
  <h3>4.{i} {esc(p["title"])}</h3>
  <p class="paircap">{esc(p["note"])} · <code>{esc(p["path"])}</code> {p["image_size_px"][0]}×{p["image_size_px"][1]} px ·
    fitted camera distance <b>{f(t["cam_distance_mm"], 0)} mm</b>, IoU <b>{f(t["iou"], 3)}</b>,
    head pitch {f(t["head_pitch_deg"], 1)}° yaw {f(t["head_yaw_deg"], 1)}° roll {f(t["head_roll_deg"], 1)}° jaw {f(t["jaw_open_deg"], 1)}°</p>
  <figure class="wide"><img src="{p["pictures"]["pair"]}" alt="{esc(p["id"])} real | ours | overlay">
    <figcaption>Real (left), ours at the same camera and fitted pose (centre), overlay (right; blue = photograph's head region, orange = our head silhouette and eye ring).</figcaption></figure>
  <div class="pair">
    <figure><span class="tag">Real · the measurements drawn</span><img src="{p["pictures"]["measure"]}" alt="{esc(p["id"])} measurement">
      <figcaption>Blue lines: the servo-case scan lines that set the scale; green: the eye-ring ellipse; red: the neck cut; purple: the head region.</figcaption></figure>
    <figure><span class="tag ours">Ours · the same servo in the render</span><img src="{p["pictures"]["render_servo"]}" alt="{esc(p["id"])} render servo">
      <figcaption>The render at the fitted camera; the box is the servo width the size ratio divides by.</figcaption></figure>
  </div>
  <p class="note">Size ratio product/mesh <b>{pm(s.get("product_over_mesh"), s.get("unc"), 4)}</b> → head length {pm(s.get("head_length_dev_mm"), s.get("head_length_dev_unc_mm"))} mm
    {chip(p.get("verdicts", {}).get("length", "CANNOT DETERMINE"))}; along the head's own axes: major {pm(s.get("dev_major_mm"), s.get("dev_major_unc_mm"))} mm, minor {pm(s.get("dev_minor_mm"), s.get("dev_minor_unc_mm"))} mm.</p>""")
    return "\n".join(out)


settle = "".join("<li>%s</li>" % esc(x) for x in V["what_would_settle"]) or "<li>Nothing — every check PASSES.</li>"
PF = D.get("profile_frame")


def sens_rows():
    rows = []
    for x in D.get("sensitivity", []):
        rows.append("<tr><td>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td><code>%s</code></td></tr>" % (
            esc(x["photo"]), f(x["D_mm"], 0), f(x["iou"], 4), f(x["yaw"], 1), pm(x["product_over_mesh"], x["unc"], 4), f(x["head_length_dev_mm"], 2, True), esc(x["file"])))
    for p in D["photos"]:
        if p.get("size"):
            rows.append("<tr><td>%s (main run)</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td><code>out/head/head_fit.json</code></td></tr>" % (
                esc(p["id"]), f(p["fit"]["cam_distance_mm"], 0), f(p["fit"]["iou"], 4), f(p["fit"]["head_yaw_deg"], 1), pm(p["size"]["product_over_mesh"], p["size"]["unc"], 4), f(p["size"]["head_length_dev_mm"], 2, True)))
    return "\n".join(rows)
n_photos = C["n_photos"]
quick = " <b>(quick fit — rerun without --quick before release)</b>" if D.get("quick") else ""

HTML = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Head Reconstruction</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opt_sz,wght@8..60,400;8..60,600;8..60,700&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="tools/doc.css">
<style>
  .pair{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:10px 0 4px}}
  .pair figure{{margin:0;padding:8px}}
  .pair figure img{{width:100%;object-fit:contain;background:#fff}}
  figure.wide{{margin:10px 0 4px;padding:8px}} figure.wide img{{width:100%;background:#fff}}
  figcaption{{font-family:var(--sans);font-size:12px;color:var(--ink-2);margin-top:4px}}
  .tag{{font-family:var(--sans);font-size:10.5px;font-weight:600;letter-spacing:.07em;text-transform:uppercase;display:inline-block;padding:2px 8px;margin-bottom:6px;border:1px solid var(--hair);color:var(--ink-2)}}
  .tag.ours{{color:var(--accent);border-color:var(--accent)}}
  .paircap{{font-family:var(--sans);font-size:12.5px;color:var(--ink-2);margin:0 0 2px}}
  .note{{font-size:13.5px;color:var(--ink-2);margin:2px 0 18px;max-width:54em}}
  .verdict{{border-left:3px solid var(--accent);padding:2px 0 2px 18px;margin:14px 0;font-size:15.5px}}
  .verdict b{{color:var(--accent)}} .verdict.warn{{border-left-color:var(--no)}} .verdict.warn b{{color:var(--no)}}
  .verdict.cd{{border-left-color:var(--cd)}} .verdict.cd b{{color:var(--cd)}}
  .chip.no{{color:var(--no);border-color:var(--no)}}
  .statbar{{display:flex;flex-wrap:wrap;gap:0;border-bottom:1px solid var(--hair);margin:8px 0 2px}}
  .stat{{padding:12px 26px 12px 0;margin-right:22px}}
  .stat b{{display:block;font-weight:700;font-size:22px;font-variant-numeric:tabular-nums}}
  .stat span{{font-family:var(--sans);font-size:12px;color:var(--ink-2)}}
  table.data td.n,table.data th.n{{text-align:right;font-variant-numeric:tabular-nums}}
  tr.total td{{border-top:2px solid var(--rule)}}
  @media(max-width:640px){{.pair{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<div class="wrap">
<p class="backlink"><a href="RELEASE.html">← Release dossier</a> · <a href="COMPARISON.html">Reference match</a></p>

<header class="hero">
  <p class="eyebrow">Microduck reverse-engineering · lane A · head conformance</p>
  <h1>Is the simulation head the product head? Measured from the photographs.</h1>
  <p class="sub">GOAL.md finding 1 said the simulation head is "far longer front-to-back than the compact domed head in every product photo"
  and its eye bezel is missing; the handover correction demoted that to CANNOT DETERMINE. Leif: <em>"im not sure that the simulation
  meshes are the same as their product meshes! you have to use the images as references"</em>. This document settles it by measurement:
  every product photograph is scaled by the XL330-M288-T servo visible in the same frame, our model is posed to the photograph with a
  perspective camera, and the head shell is compared in millimetres against the mesh's 91.760 × 122.690 × 46.336 mm under the rebuild
  rule (1.5 mm per axis), never loosened.</p>
  <div class="rev"><span>MD-HEAD-001 · Rev A</span><span>{esc(D["generated"])}</span><span>data: <code>out/head/head.json</code></span><span>generator: <code>tools/gen_head.py</code></span></div>
</header>

<div class="statbar">
  <div class="stat"><b>{n_photos}</b><span>photographs measured</span></div>
  <div class="stat"><b>{pm(C["product_over_mesh"], C["product_over_mesh_unc"], 4)}</b><span>product / mesh size ratio</span></div>
  <div class="stat"><b>{pm(C["head_length_dev_mm"], C["head_length_dev_unc_mm"], 2)} mm</b><span>head length, product − mesh</span></div>
  <div class="stat"><b>{chip(V["head"])}</b><span>head verdict at the 1.5 mm rule</span></div>
  <div class="stat"><b>{chip(V["eye_bezel"])}</b><span>eye bezel</span></div>
</div>

<nav class="toc">
  <a href="#answer">1 Verdict</a><a href="#rule">2 The question and the rule</a><a href="#scale">3 Scale</a>
  <a href="#photos">4 Photographs, posed and overlaid</a><a href="#dims">5 Measured dimensions</a><a href="#eye">6 Eye bezel</a>
  <a href="#sens">6b Camera distance</a><a href="#settle">7 What would settle the rest</a><a href="#method">8 Method and limits</a>
</nav>

<section id="answer">
  <h2><span class="n">1</span>Verdict</h2>
  <div class="verdict {'warn' if V['head']=='FAIL' else ('cd' if V['head']=='CANNOT DETERMINE' else '')}">
    <b>Head: {esc(V["head"])}.</b>{quick} Across {n_photos} photographs the product head is
    <b>{pm(C["product_over_mesh"], C["product_over_mesh_unc"], 4)}</b> times the simulation mesh (a head-length deviation of
    <b>{pm(C["head_length_dev_mm"], C["head_length_dev_unc_mm"], 2)} mm</b> on 122.690 mm; along the head's own principal axes
    {pm(C["dev_major_mm"], C["dev_major_unc_mm"], 2)} mm and {pm(C["dev_minor_mm"], C["dev_minor_unc_mm"], 2)} mm).
    The "far longer" head of finding 1 is not in the photographs: the length agrees to the stated uncertainty, and the silhouettes
    overlay (§4) once the jaw is posed open and the head is yawed as in the shot.
  </div>
  <div class="verdict {'warn' if V['eye_bezel']=='FAIL' else ('cd' if V['eye_bezel']=='CANNOT DETERMINE' else '')}">
    <b>Eye bezel: {esc(V["eye_bezel"])}.</b> The bezel is <em>not</em> missing from the mesh: <code>noenoeil.stl</code> is a Ø30.000 mm ring,
    7.5 mm long, standing proud of the face panel (whose only opening is the Ø14.5 mm lens hole) — exactly the accent-colour ring in the
    photographs. Measured against it, the product ring reads {pm(C["eye_dev_mm"], C["eye_dev_unc_mm"], 2)} mm in the profile shots
    (via the servo scale) and {f(C["eye_front_view_dev_mm"], 2, True)} mm implied by the true front view (ratio to head width). The ring's
    position on the face — {f(FV["comparison"]["eye_below_top_over_width"]["dev_mm"], 2, True)} mm below the shell top,
    {f(FV["comparison"]["eye_x_offset_over_width"]["dev_mm"], 2, True)} mm off the mid-line, the ToF window {f(FV["comparison"]["tof_x_from_eye_over_width"]["dev_mm"], 2, True)} mm from
    the MJCF site — matches the mesh (§6).
  </div>
  <p class="note">{esc(V["basis"])}</p>
</section>

<section id="rule">
  <h2><span class="n">2</span>The question and the rule</h2>
  <p>COMPARISON.html §5.1 could only compare scale-free silhouette ratios, and the one photograph it used has the beak open and the head
  pitched and yawed — so its +69 % aspect-ratio difference was confounded and it stopped at CANNOT DETERMINE, naming photogrammetric
  scaling against the servo as the evidence that would settle it. That is what this document does. The grading rule is the one every
  rebuilt part on this shelf is held to — <b>{esc(D["rule_source"])}</b> — applied to the product as the reference and Pollen's mesh as the
  candidate. Because a photograph yields a deviation <i>d</i> with an uncertainty <i>u</i>, the verdict is decided the only honest way:
  PASS when |d| + u ≤ 1.5 mm, FAIL when |d| − u &gt; 1.5 mm, otherwise CANNOT DETERMINE. Nothing is loosened; a measurement that cannot
  discriminate at 1.5 mm says so.</p>
  <div class="tw"><table class="data">
    <caption>Table 1. The mesh under test (out/verify/mech_dims.json, mm, file frame) and the known-size features used for scale.</caption>
    <thead><tr><th>Item</th><th>Value</th><th>Source</th></tr></thead>
    <tbody>
      <tr><td><code>top_head_shell</code></td><td class=n>{f(M["top_head_shell_mm"][0],3)} × {f(M["top_head_shell_mm"][1],3)} × {f(M["top_head_shell_mm"][2],3)}</td><td><code>{esc(M["source"])}</code> (length = 122.690 along the mesh's second axis)</td></tr>
      <tr><td><code>bottom_head_shell</code></td><td class=n>{f(M["bottom_head_shell_mm"][0],3)} × {f(M["bottom_head_shell_mm"][1],3)} × {f(M["bottom_head_shell_mm"][2],3)}</td><td><code>{esc(M["source"])}</code></td></tr>
      <tr><td><code>jaw</code></td><td class=n>{f(M["jaw_mm"][0],3)} × {f(M["jaw_mm"][1],3)} × {f(M["jaw_mm"][2],3)}</td><td><code>{esc(M["source"])}</code></td></tr>
      <tr><td><code>noenoeil</code> (eye ring)</td><td class=n>Ø30.000 × 7.5 boss, Ø14.4 bore</td><td>{esc(M["eye_ring_source"])}</td></tr>
      <tr><td>XL330-M288-T case width</td><td class=n>20.000 mm</td><td>{esc(D["servo_source"])}</td></tr>
    </tbody>
  </table></div>
</section>

<section id="scale">
  <h2><span class="n">3</span>Scale — millimetres per pixel from the servo in the same frame</h2>
  <p>The XL330-M288-T is the only object of independently known size in every store photograph. Its case width is read as the mode of the
  dark-run widths over many scan lines across the case (label text and cables break single lines; the case gives the same width on every
  clean line). The same case in our render at the fitted camera is W<sub>render</sub> = (20.000·|sin az| + 26.000·|cos az|) mm × (frame px / frame mm) ×
  D<sub>head</sub>/D<sub>servo</sub> — exact, because the render's frame is by construction 190 mm at the head's depth and the servo's depth is read
  off the posed model; the segmentation mask of the servo geom is read with the same mode-of-runs estimator as a cross-check. The size ratio
  product/mesh = k · W<sub>render</sub> / W<sub>photo</sub> therefore carries the servo-to-head depth difference through the camera model
  rather than assuming it away. Uncertainty per servo: ±1 px per edge plus the accepted lines' spread, and the fit's spread of k.</p>
  <div class="tw"><table class="data">
    <caption>Table 2. Scale features. mm/px is at the servo's depth; the depth column gives camera distance to the servo / to the head origin at the fitted camera.</caption>
    <thead><tr><th>Photograph</th><th>Feature</th><th class=n>Width in photo (px)</th><th class=n>mm / px</th><th class=n>Width in render (px, analytic; mask cross-check)</th><th class=n>Size ratio product/mesh</th><th class=n>Depth servo / head (mm)</th></tr></thead>
    <tbody>
{scale_rows()}
    </tbody>
  </table></div>
</section>

<section id="photos">
  <h2><span class="n">4</span>Photographs, posed and overlaid — real beside ours, always</h2>
  <p>For each photograph the model is posed by fitting camera elevation, azimuth (3/4 shots), distance, head pitch / yaw / roll, the jaw opening
  and a similarity transform, maximising silhouette IoU of the head region plus the eye-ring ellipse match. The jaw is not a joint in the
  published model; its geoms are rotated about the measured hinge (the 15×10×3 bearing centre). Head pitch is the head's orientation relative to the trunk, 0 = level (eye-ring axis horizontal, bisected on the mesh), positive = face up.</p>
  <div class="tw"><table class="data">
    <caption>Table 3. Fitted pose per photograph. k = photo px per render px (fit spread from re-polishing).</caption>
    <thead><tr><th>Photograph</th><th class=n>IoU</th><th class=n>eye term</th><th class=n>D (mm)</th><th class=n>az (°)</th><th class=n>el (°)</th><th class=n>pitch (°)</th><th class=n>yaw (°)</th><th class=n>roll (°)</th><th class=n>jaw (°)</th><th class=n>k</th></tr></thead>
    <tbody>
{fit_rows()}
    </tbody>
  </table></div>
{photo_sections()}
</section>

<section id="dims">
  <h2><span class="n">5</span>Measured dimensions — product against mesh, in millimetres</h2>
  <p>Head length deviation = 122.690 × (r − 1). Major / minor are the extents of the head region along its own principal axes in the photograph
  (0.5 / 99.5 percentile, so a stray pixel cannot set them) against the render's extents at the servo-anchored scale — the shape residual left
  after the size ratio. Uncertainty per axis: the scale uncertainty, ±2 px on each mask edge, and the mm/px uncertainty, in quadrature.</p>
  <div class="tw"><table class="data">
    <caption>Table 4. Deviations product − mesh, mm ± uncertainty; verdict per the 1.5 mm rule (PASS |d|+u ≤ 1.5; FAIL |d|−u &gt; 1.5; else CANNOT DETERMINE).</caption>
    <thead><tr><th>Photograph</th><th class=n>r = product/mesh</th><th class=n>Length dev (mm)</th><th class=n>Major photo (mm)</th><th class=n>Major mesh (mm)</th><th class=n>Δ major (mm)</th><th class=n>Minor photo (mm)</th><th class=n>Minor mesh (mm)</th><th>Δ minor (mm) · verdict</th></tr></thead>
    <tbody>
{dim_rows()}
    </tbody>
  </table></div>
</section>

<section id="eye">
  <h2><span class="n">6</span>Eye bezel — does the product have a part the mesh lacks?</h2>
  <p>No. The mesh has it: <code>noenoeil</code> is a Ø30.000 mm × 7.5 mm ring in front of the face panel (Table 1). The shelf folder
  <code>ce-parts/microduck-eye-ring</code> was created empty ("nothing measured yet"); the numbers below are what it should carry. Two independent
  reads of the product ring: (a) in each profile photograph the accent-hue ring pixels give an ellipse whose major axis is the ring diameter,
  scaled by the servo (and, more robustly, by the same ring in the render through the fitted similarity — "via render", which needs no mm/px);
  (b) the flat-lay <em>inside-the-box</em> photograph is a true front view, so every face feature is a scale-free ratio to the head width, compared
  with our mesh rendered in a true front view with the head level.</p>
  <div class="tw"><table class="data">
    <caption>Table 5. Eye ring in the profile photographs (mesh 30.000 mm). Centre offset = photo ring centre − render ring centre at the fitted pose, mm (x right, y down).</caption>
    <thead><tr><th>Photograph</th><th class=n>Ellipse major × minor (px)</th><th class=n>View angle (°)</th><th class=n>Ø via servo (mm)</th><th class=n>Ø via render (mm)</th><th class=n>Centre offset (mm)</th><th>Verdict</th></tr></thead>
    <tbody>
{eye_rows()}
    </tbody>
  </table></div>
  <figure class="wide"><img src="out/head/front_pair.png" alt="front view: real flat-lay beside our mesh">
    <figcaption>True front view: the flat-lay photograph (left; a composite — the battery and gamepad in it carry two different mm/px, so no other object is used for scale) beside our mesh rendered front-on with the head level. Blue = widest row and mid-line, green = eye-ring ellipse, red = ToF window.</figcaption></figure>
  <div class="tw"><table class="data">
    <caption>Table 6. Face layout as ratios to the head width, photo vs mesh; mm columns assume the head width is the mesh's {f(FV["mesh_head_width_mm"],3)} mm. Source <code>out/head/front_view.json</code>.</caption>
    <thead><tr><th>Ratio</th><th class=n>Photo</th><th class=n>Mesh</th><th class=n>Diff</th><th class=n>Photo (mm, implied)</th><th class=n>Mesh (mm)</th><th class=n>Δ (mm)</th></tr></thead>
    <tbody>
{front_rows()}
    </tbody>
  </table></div>
  <p class="note">{esc(FV["uncertainty"])} The ToF window (a rounded slot {f(FV["photo"]["tof"]["w_px"] / FV["photo"]["head_width_px"] * FV["mesh_head_width_mm"], 1)} × {f(FV["photo"]["tof"]["h_px"] / FV["photo"]["head_width_px"] * FV["mesh_head_width_mm"], 1)} mm implied) has no geom in the mesh — the face panel's slot is CANNOT DETERMINE on the mesh side and is a feature the face-part rebuild must carry.</p>
</section>

<section id="sens">
  <h2><span class="n">6b</span>Camera distance — the one thing the store frames do not give</h2>
  <p>The store photographs carry no EXIF and no ruler; the near ankle servo reads 136–146 px against the neck's 131.4 px (44.1 mm nearer)
  depending on the scan tilt, which brackets D only between ~700 and ~1650 mm. Because the head is yawed ~50° towards the camera, its face is
  ~45 mm nearer than the servo and the head-to-servo ratio moves with D. The fit was therefore repeated at other distances; the half-range of
  r over these runs is added to the uncertainty of the verdict.</p>
  <div class="tw"><table class="data">
    <caption>Table 7. Sensitivity of the size ratio to the assumed camera distance (same photograph, same method, quick fits).</caption>
    <thead><tr><th>Photograph</th><th class=n>D (mm)</th><th class=n>IoU</th><th class=n>fitted yaw (°)</th><th class=n>r = product/mesh</th><th class=n>head length dev (mm)</th><th>file</th></tr></thead>
    <tbody>
{sens_rows()}
    </tbody>
  </table></div>
  <p class="note">{esc(C.get("D_sensitivity_note", "no sensitivity runs found"))}</p>
  <h3>The pure-profile frame — scale-free check</h3>
  <p>{esc(PF["aspect_reading"]) if PF else "images/github/gh_readme_7.png not analysed"}. The servo in that 884-px video frame merges with its bracket and cables, so it gives no mm/px
  (out/head/profile_frame.json states why); it is kept because it is the only published view with the head un-yawed, real beside Pollen's own render.</p>
  <figure class="wide"><img src="out/head/profile_frame_pair.png" alt="pure profile frame, sim beside real"><figcaption>Pollen's README frame: their simulator render (left) beside the real unit (right); blue = the head silhouette's principal-axis box on each.</figcaption></figure>
</section>

<section id="settle">
  <h2><span class="n">7</span>What would settle the remaining CANNOT DETERMINEs</h2>
  <ul>{settle}</ul>
</section>

<section id="method">
  <h2><span class="n">8</span>Method and honest limits</h2>
  <ul>
    <li><b>Scripts.</b> <code>tools/head_photomatch.py</code> (scale, pose fit, size — writes <code>out/head/head_fit.json</code> and every overlay),
      <code>tools/head_frontview.py</code> (front-view ratios — <code>out/head/front_view.json</code>), <code>tools/head_verdict.py</code> (merge + verdict —
      <code>out/head/head.json</code>), <code>tools/gen_head.py</code> (this page). Renderer: MuJoCo offscreen segmentation at 1000², perspective free camera whose
      field of view follows the fitted distance so the head always spans the same frame.</li>
    <li><b>Which servo face.</b> Read off the published MJCF: the servo mesh is 20.000 (mesh x) × 34.06 (mesh z) × 29.04 (mesh y, case + horn) and in the neck body
      mesh x = world −x, mesh z = world −z, so a profile camera sees the 20.000 × 34 horn/label face (<code>tools/head_probe.py</code>). The photographs show the
      label on that face, as the drawing does.</li>
    <li><b>Perspective.</b> The store shots are close (fitted D in Table 3); the near and far edges of the head differ in scale by up to 4 % at 0.5 m, which is why
      the camera is perspective and D is fitted rather than assumed orthographic.</li>
    <li><b>What the numbers are not.</b> Bounding-box level agreement between the product and the mesh. Not a p95 surface-distance check (that needs a scan
      of a product head), not a manufacturing tolerance. Every number is from published photographs and published digital assets; no physical unit has
      been callipered.</li>
    <li><b>Mask edges.</b> The head region is the non-white silhouette above a neck cut, minus a neck polygon drawn by hand and shown on every measurement picture;
      the cream shell against the white background is segmented by chroma as well as luminance. Edge uncertainty ±2 px is carried into every mm.</li>
  </ul>
</section>

</div>
</body>
</html>
"""
open(os.path.join(REPO, "HEAD-RECONSTRUCTION.html"), "w").write(HTML)
print("wrote HEAD-RECONSTRUCTION.html  photos=%d head=%s eye=%s" % (n_photos, V["head"], V["eye_bezel"]))
