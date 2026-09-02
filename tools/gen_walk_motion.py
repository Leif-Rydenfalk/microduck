#!/usr/bin/env python3
"""gen_walk_motion.py — WALK.html: the walking mechanics, filmed and measured.

Reads (data, never hand-edited):
    out/motion/walk.json              sim/motion_render.py --all
    out/motion/walk_vs_product.json   sim/walk_vs_product.py   (optional)

Writes:
    out/motion/WALK.html

System python3 (stdlib only).
"""
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(REPO, "out", "motion")
E = html.escape

D = json.load(open(os.path.join(OUT, "walk.json")))
VP_PATH = os.path.join(OUT, "walk_vs_product.json")
VP = json.load(open(VP_PATH)) if os.path.exists(VP_PATH) else None

LEG = ["left_hip_yaw", "left_hip_roll", "left_hip_pitch", "left_knee", "left_ankle",
       "right_hip_yaw", "right_hip_roll", "right_hip_pitch", "right_knee", "right_ankle"]
HEAD = ["neck_pitch", "head_pitch", "head_yaw", "head_roll"]


def base(p):
    return os.path.basename(p)


def figure(v, key, wide=False):
    """<video> + its contact sheet + the read-back verdict."""
    ver = v["verify"]
    cls = "pass" if ver["verdict"] == "PASS" else "cd"
    return """
<figure class="fig%s">
  <video controls muted loop playsinline preload="metadata" poster="%s" src="%s"></video>
  <img src="%s" alt="contact sheet, 8 frames of %s">
  <figcaption><b>%s</b> — %s.<br>
    Camera: %s. %d frames at %d fps (%.3f s), mp4 %.2f MB, <a href="%s">GIF</a> %.2f MB.
    Read back frame by frame: <span class="chip %s">%s</span>
    min frame std %.2f (blank &lt; 4.0), max inter-frame delta %.3f, blank frames %d, frozen pairs %d.
  </figcaption>
</figure>""" % (" wide" if wide else "", base(v["contact_sheet"]), base(v["path"]),
                base(v["contact_sheet"]), E(key), E(key), E(v["what"]), E(v["camera"]),
                v["frames"], v["fps"], v["seconds"], v["mp4_mb"], base(v["gif"]), v["gif_mb"],
                cls, ver["verdict"], ver["min_frame_std"], ver["max_interframe_delta"],
                ver["blank_frames"], ver["frozen_pairs"])


def jrow(name):
    j = D["joints"][name]
    lo, hi = j["mjcf_range_deg"]
    return ("<tr><td class=mono>%s</td><td class=num>%.2f … %.2f</td><td class=num>%.2f</td>"
            "<td class=num>%.2f … %.2f</td><td class=num><b>%.2f</b></td><td class=num>%.1f%%</td>"
            "<td class=num>%.1f</td><td class=num>%d</td><td class=num>%.2f</td></tr>") % (
        E(name), lo, hi, hi - lo, j["min_deg"], j["max_deg"], j["travel_deg"],
        j["travel_pct_of_mjcf_range"], j["peak_abs_vel_deg_s"], j["peak_vel_at_frame"],
        j["closest_approach_to_limit_deg"])


w = D["walk"]
g = D["gait"]
V = D["videos"]
order = ["walk_body", "walk_composite", "walk_slowmo", "walk_knee_prof", "walk_knee_34",
         "walk_hip_prof", "walk_hip_34", "walk_ankle_prof", "walk_ankle_34"]
order = [k for k in order if k in V] + [k for k in V if k not in order]
passed = sum(1 for k in V if V[k]["verify"]["verdict"] == "PASS")

vp_html = ""
if VP:
    vp_html = """
<section id="product">
  <h2>7 · Beside the real product</h2>
  <p>The only published asset of the product performing <i>this</i> motion is Pollen's portrait move
  clip <code>%s</code> (%d frames, %.0f fps, %.3f s, %d×%d, %s). It is Pollen's own
  <b>rendered</b> clip, not a photograph — <b>no photograph of the product mid-stride exists in
  <code>images/</code></b>, so this is a render-to-render comparison and is labelled as one.</p>
  <p>Both gait periods are measured, not assumed. The product's comes off the pixels: silhouette
  (luma &gt; 12 on the black alpha background), the x-centroid of the bottom 15&nbsp;%% of the
  silhouette minus the x-centroid of the whole silhouette — one oscillation per gait cycle —
  autocorrelated. Ours comes off <code>left_knee</code> in the trajectory.</p>
  <table class="tbl">
    <tr><th></th><th class=num>gait period (s)</th><th class=num>autocorr peak</th><th class=num>cadence (steps/min)</th></tr>
    <tr><td>product clip</td><td class=num>%.4f</td><td class=num>%.3f</td><td class=num>%.2f</td></tr>
    <tr><td>ours (this sim)</td><td class=num>%.4f</td><td class=num>%.3f</td><td class=num>%.2f</td></tr>
    <tr><td>ratio ours / product</td><td class=num colspan=3>%.4f</td></tr>
  </table>
  <figure class="fig wide"><img src="%s" alt="our walk beside Pollen's move clip, phase matched">
  <figcaption>Five equal phases of one gait cycle each. %s</figcaption></figure>
</section>""" % (E(VP["product_clip"]), VP["product_clip_meta"]["frames"], VP["product_clip_meta"]["fps"],
                 VP["product_clip_meta"]["seconds"], VP["product_clip_meta"]["size"][0],
                 VP["product_clip_meta"]["size"][1], E(VP["product_clip_meta"]["codec"]),
                 VP["product_gait_period_s"], VP["product_autocorr_peak"], VP["product_cadence_steps_per_min"],
                 VP["ours_gait_period_s"], VP["ours_autocorr_peak"], VP["ours_cadence_steps_per_min"],
                 VP["period_ratio_ours_over_product"], base(VP["figure"]), E(VP["camera"]))

doc = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Microduck — walking mechanics, filmed and measured</title>
<link rel="stylesheet" href="../../tools/doc.css">
<style>
 .fig{margin:26px 0}
 .fig video{width:100%%;max-width:760px;display:block;background:#fff;border:1px solid var(--line)}
 .fig.wide video{max-width:100%%}
 .fig img{width:100%%;display:block;margin-top:8px;border:1px solid var(--line)}
 .grid2{display:grid;grid-template-columns:1fr 1fr;gap:22px}
 .grid2 .fig{margin:0}
 .tbl{width:100%%;border-collapse:collapse;font-family:var(--sans);font-size:13px;margin:14px 0 6px}
 .tbl th,.tbl td{border-bottom:1px solid var(--line);padding:5px 7px;text-align:left}
 .tbl th{background:var(--head);font-size:11px;letter-spacing:.04em;text-transform:uppercase}
 .num{text-align:right;font-variant-numeric:tabular-nums;font-family:var(--mono)}
 .chip{font-family:var(--sans);font-size:11px;padding:1px 6px;border:1px solid currentColor;border-radius:2px}
 .chip.pass{color:var(--pass-ink)} .chip.cd{color:var(--cd-ink)}
 figcaption{font-family:var(--sans);font-size:12.5px;color:var(--ink-2);margin-top:7px;line-height:1.5}
 @media(max-width:820px){.grid2{grid-template-columns:1fr}}
</style></head><body><div class="wrap">
<header class="top">
 <div class="eyebrow">Microduck · simulation evidence · motion</div>
 <h1>Walking mechanics, filmed and measured</h1>
 <p class="lede">Leif, 2026-09-02: <i>&ldquo;show me renders of the mechanics like our cad system
 walking, zoom in on joints as they move and the head kmvoing around and the legs moving
 around.&rdquo;</i> Nine videos of OUR rebuilt parts walking under Pollen's own policy, every camera
 tracking the joint it is filming, and every joint's travel and peak angular velocity read off the
 same trajectory.</p>
</header>

<section id="what">
<h2>1 · What ran</h2>
<table class="tbl">
<tr><td>model</td><td class=mono>%s</td></tr>
<tr><td>trajectory</td><td class=mono>%s</td></tr>
<tr><td>written by</td><td class=mono>%s</td></tr>
<tr><td>rendered by</td><td class=mono>%s</td></tr>
<tr><td>scene</td><td class=mono>%s</td></tr>
<tr><td>commanded v<sub>x</sub></td><td class=num>%.3f m/s</td></tr>
<tr><td>duration / control rate</td><td class=num>%.3f s @ %.0f Hz (%d frames, dt %.4f s)</td></tr>
<tr><td>walked</td><td class=num>%.4f m (x %+.4f, y %+.4f), mean %.4f m/s, final yaw %+.2f&deg;</td></tr>
<tr><td>trunk height</td><td class=num>start %.4f, min %.4f, max %.4f, end %.4f m</td></tr>
<tr><td>max tilt / fell</td><td class=num>%.2f&deg; / %s</td></tr>
<tr><td>gait cycle</td><td class=num>%.4f s (%d frames at 50 Hz), cadence %.2f steps/min, stride %.4f m</td></tr>
</table>
<p class="note">Gait period method: %s. Every video below was re-read frame by frame after encoding;
a blank, white or frozen frame is a defect, not a video — <b>%d of %d PASS</b>.</p>
</section>

<section id="body">
<h2>2 · The whole duck</h2>
%s
</section>

<section id="composite">
<h2>3 · All four at once, one timeline</h2>
%s
</section>

<section id="slowmo">
<h2>4 · One gait cycle at 0.25&times;, with the angle traces</h2>
%s
</section>

<section id="joints">
<h2>5 · Joint close-ups, camera tracking the joint</h2>
<div class="grid2">
%s
</div>
</section>

<section id="measured">
<h2>6 · Measured, off the same trajectory</h2>
<p>MJCF range is read off the compiled model (Pollen's limits, verbatim). Travel is what the walking
policy actually used. Peak angular velocity is <code>|qvel|</code> at its maximum, with the 50 Hz
frame index it happened on — <code>out/sim/walk_ours_traj.npz</code>, computed in
<code>sim/motion_render.py measure()</code>.</p>
<h3>Legs</h3>
<table class="tbl">
<tr><th>joint</th><th class=num>MJCF range (&deg;)</th><th class=num>span</th><th class=num>used min … max (&deg;)</th>
<th class=num>travel (&deg;)</th><th class=num>of range</th><th class=num>peak |&omega;| (&deg;/s)</th>
<th class=num>at frame</th><th class=num>closest to a limit (&deg;)</th></tr>
%s
</table>
<h3>Neck and head — during the walk, with no head command</h3>
<p>The walking policy is driven with the head command slots at zero, so what the head does here is
the policy's own stabilisation, not a commanded motion. That is the measured answer to
&ldquo;is the neck stiff&rdquo;: the mechanics allow far more than this row shows.</p>
<table class="tbl">
<tr><th>joint</th><th class=num>MJCF range (&deg;)</th><th class=num>span</th><th class=num>used min … max (&deg;)</th>
<th class=num>travel (&deg;)</th><th class=num>of range</th><th class=num>peak |&omega;| (&deg;/s)</th>
<th class=num>at frame</th><th class=num>closest to a limit (&deg;)</th></tr>
%s
</table>
</section>
%s
<footer>
<p class="note">Regenerate: <code>ce-cad/bin/cad sim/motion_render.py --all</code> (or FreeCAD's
python directly), then <code>sim/walk_vs_product.py</code>, then
<code>python3 tools/gen_walk_motion.py</code>. Numbers come from
<code>out/motion/walk.json</code>; nothing on this page is typed by hand.</p>
</footer>
</div></body></html>
""" % (E(D["model"]), E(D["source_trajectory"]), E(D["trajectory_written_by"]), E(D["rendered_by"]),
       E(D["scene"]), w["commanded_vx_m_s"], w["seconds"], w["control_hz"], w["trajectory_frames"],
       w["frame_dt_s"], w["walked_m"], w["walked_x_m"], w["walked_y_m"], w["mean_speed_m_s"],
       w["final_yaw_deg"], w["trunk_z_m"]["start"], w["trunk_z_m"]["min"], w["trunk_z_m"]["max"],
       w["trunk_z_m"]["end"], w["max_tilt_deg"], "yes" if w["fell"] else "no",
       g["cycle_period_s"], g["cycle_frames_at_50hz"], g["cadence_steps_per_min"], g["stride_length_m"],
       E(g["method"]), passed, len(V),
       figure(V["walk_body"], "walk_body", wide=True),
       figure(V["walk_composite"], "walk_composite", wide=True),
       figure(V["walk_slowmo"], "walk_slowmo", wide=True),
       "\n".join(figure(V[k], k) for k in order if k not in ("walk_body", "walk_composite", "walk_slowmo")),
       "\n".join(jrow(n) for n in LEG), "\n".join(jrow(n) for n in HEAD), vp_html)

open(os.path.join(OUT, "WALK.html"), "w").write(doc)
print("wrote", os.path.join(OUT, "WALK.html"), len(doc), "bytes")
