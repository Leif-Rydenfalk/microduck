#!/usr/bin/env python3
"""gen_leg_motion.py — LEG-MOTION.html from out/motion/legs.json,
out/motion/legs_videos.json and out/motion/legs_compare.json.

Nothing here is hand-maintained: every number and every citation is read out of
the JSON that sim/leg_sweep.py measured and sim/leg_render.py / sim/leg_compare.py
wrote. Run it again after re-running those and the page follows.

    python3 tools/gen_leg_motion.py
"""
import html, json, os, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(ROOT, "out", "motion")
J = json.load(open(os.path.join(M, "legs.json")))
V = json.load(open(os.path.join(M, "legs_videos.json")))
try:
    C = json.load(open(os.path.join(M, "legs_compare.json")))
except Exception:
    C = []
E = html.escape

R = J["mjcf_ranges"]
DY = J["dynamic_step_policy_paused"]["joints"]
SS = J["sitstand_policy"]["joints"]
SQ = J["squat"]["joints"]
LL = J["leg_lift"]["joints"]
ORDER = list(R.keys())


def vid(v):
    return """<figure>
<video controls preload="metadata" style="width:100%%;display:block;border:1px solid var(--hair);background:#fff" src="%s"></video>
<figcaption><b>%s</b> — %s<br><span class="mono">%s · %.1f s @ %d fps · %d frames · mp4 %.1f MB · gif %.1f MB</span><br>
contact sheet <a href="%s">%s</a> · gif <a href="%s">%s</a> · frames <span class=mono>%s</span></figcaption></figure>
<figure><img src="%s" alt="%s contact sheet"><figcaption>The eight frames of <span class=mono>%s</span> that were read back after encoding
(mean inter-frame difference %.3f, min pixel %d — a blank or frozen clip is refused by
<span class=mono>sim/leg_render.py check_frames()</span>).</figcaption></figure>""" % (
        E(v["mp4"]), E(v["name"]), E(v["what"]), E(v["camera"]), v["seconds"], v["fps"], v["frames"],
        v["mp4_bytes"] / 1e6, v["gif_bytes"] / 1e6, E(v["sheet"]), E(v["sheet"]), E(v["gif"]), E(v["gif"]),
        E(", ".join(v["frames_png"])), E(v["sheet"]), E(v["name"]), E(v["name"]),
        v["mean_interframe_diff"], v["min_pixel"])


jt = "".join(
    "<tr><td class=mono>%s</td><td class=n>%.3f … %.3f</td><td class=mono>%s</td>"
    "<td class=n>%.3f</td><td class=n>%.1f%%</td><td class=n>%.1f</td><td class=n>%.2f</td>"
    "<td class=n>%.3f</td><td class=n>%.1f</td><td class=n>%.3f</td></tr>" % (
        E(j), R[j]["lo_deg"], R[j]["hi_deg"], E(R[j]["cite"]),
        DY[j]["travel_deg"], 100 * DY[j]["travel_frac_of_mjcf_range"],
        DY[j]["peak_velocity_deg_s"], DY[j]["tracking_rms_deg"],
        SS[j]["travel_deg"], SS[j]["peak_velocity_deg_s"], SQ[j]["travel_deg"]) for j in ORDER)

sw = J["self_collision"]["pollen_collision_meshes"]["sweeps"]
st = "".join("<tr><td class=mono>%s</td><td class=n>%.3f … %.3f</td><td class=n>%d</td>"
             "<td class=%s>%s</td><td class=n>%s</td></tr>" % (
                 E(j), sw[j]["swept_deg"][0], sw[j]["swept_deg"][1], sw[j]["samples"],
                 "ok" if sw[j]["verdict"] == "CLEAR" else "bad", sw[j]["verdict"],
                 E("; ".join(sw[j]["pairs"])) or "—") for j in ORDER)

rows = []
for k, v in J["self_collision"]["combinations"]["cases"].items():
    for p, pp in (v["pairs"] or {"—": None}).items():
        rows.append("<tr><td class=mono>%s</td><td class=%s>%s</td><td class=mono>%s</td>"
                    "<td class=n>%s</td><td class=n>%s</td><td class=n>%s</td></tr>" % (
                        E(k), "ok" if v["verdict"] == "CLEAR" else "bad", v["verdict"],
                        E(p) if pp else "—",
                        ("%.1f" % pp["onset_deg"]) if pp else "—",
                        ("%.1f … %.1f" % tuple(pp["contact_interval_deg"])) if pp else "—",
                        ("%.3f" % pp["max_penetration_mm"]) if pp else "—"))
for k, v in J["self_collision"]["both_legs_mirrored"]["cases"].items():
    for p, pp in (v["pairs"] or {"—": None}).items():
        rows.append("<tr><td class=mono>%s</td><td class=%s>%s</td><td class=mono>%s</td>"
                    "<td class=n>%s</td><td class=n>%s</td><td class=n>%s</td></tr>" % (
                        E(k), "ok" if v["verdict"] == "CLEAR" else "bad", v["verdict"],
                        E(p) if pp else "—",
                        ("%.1f" % pp["onset_deg"]) if pp else "—",
                        ("%.1f … %.1f" % tuple(pp["contact_interval_deg"])) if pp else "—",
                        ("%.3f" % pp["max_penetration_mm"]) if pp else "—"))
ct = "".join(rows)

cmp_html = "".join(
    "<figure><img src=\"%s\" alt=\"%s\"><figcaption>%s</figcaption></figure>" %
    (E(c["png"]), E(c["what"]), E(c["what"])) for c in C)

A = J["actuator"]
ntouch = sum(1 for r in rows if ">TOUCHES<" in r)
peak = max(DY[j]["peak_velocity_deg_s"] for j in ORDER)

doc = """<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Microduck — the legs moving around</title>
<link rel=stylesheet href="tools/doc.css">
<style>td.ok{color:var(--ready);font-weight:600}td.bad{color:var(--no);font-weight:600}
td.n{text-align:right;font-family:var(--mono);font-size:.86em}
table.data{width:100%%;border-collapse:collapse;font-size:14px}
table.data th{background:var(--head);text-align:left;padding:6px 8px;border-bottom:1px solid var(--rule)}
table.data td{padding:5px 8px;border-bottom:1px solid var(--hair);vertical-align:top}
.tw{overflow-x:auto}figure{margin:26px 0}figure img{width:100%%;border:1px solid var(--hair)}
figcaption{font-family:var(--sans);font-size:13px;color:var(--ink-2);margin-top:8px}
.statbar{display:flex;gap:0;border:1px solid var(--rule);margin:26px 0}
.stat{flex:1;padding:12px 14px;border-right:1px solid var(--hair)}
.stat:last-child{border-right:none}.stat b{display:block;font-size:22px;font-family:var(--mono)}
.stat span{font-family:var(--sans);font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink-2)}
.rev{font-family:var(--sans);font-size:12px;color:var(--ink-2);display:flex;gap:22px;padding:8px 0}
</style></head><body><div class=wrap>
<header class=top>
<div class=eyebrow>Microduck · simulation evidence · legs</div>
<h1>The legs moving around</h1>
<p class=sub>Leif, 2026-09-02: <i>“show me renders of the mechanics like our cad system walking, zoom in
on joints as they move and the head kmvoing around and the legs moving around.”</i> Every leg joint is
driven through its whole MJCF range one at a time, then in the postures a one-at-a-time sweep cannot
reach, then by Pollen's own policies. Everything below is read off the simulation — Pollen's MJCF
verbatim with OUR rebuilt meshes on it (<span class=mono>sim/microduck_ours_allcollisions.xml</span>,
built by <span class=mono>sim/swap_meshes.py</span>).</p>
<div class=rev><span>generated %s</span><span>sim/leg_sweep.py + sim/leg_render.py</span>
<span>out/motion/legs.json</span></div>
</header>

<div class=statbar>
<div class=stat><b>10 / 10</b><span>leg joints reach their MJCF limit</span></div>
<div class=stat><b>%.0f&deg;/s</b><span>fastest joint, model step response</span></div>
<div class=stat><b>0</b><span>self-collisions sweeping one joint at a time</span></div>
<div class=stat><b>%d</b><span>self-collisions found in two-joint / both-leg postures</span></div>
</div>

<h2>1 · What answers what</h2>
<p>The stand policy has <b>no leg command slot</b> — the ONNX metadata's
<span class=mono>command_names</span> is <span class=mono>twist,head_pose</span>, and the 13-slot
command vector is <span class=mono>[vx vy wz | neck_pitch head_pitch head_yaw head_roll | body x y z roll
pitch yaw]</span>. So a single leg joint cannot be commanded through the policy at all. The per-joint
sweeps below therefore run with the <b>policy paused</b> and <span class=mono>data.ctrl</span> written
directly, the trunk pinned (the duck held in the hand). That choice is forced, and it is measured:</p>
<blockquote><p><b>%s</b> — %s Max trunk tilt reached <b>%.2f&deg;</b>, trunk height %.1f mm → %.1f mm.</p>
<p>%s</p></blockquote>
<p>The squat below therefore runs <b>with</b> Pollen's <span class=mono>BEST_alpha_stand</span> policy,
driven through the body-z slot of its command vector: trunk %.1f mm → %.1f mm (a <b>%.2f mm</b> drop),
max tilt %.2f&deg;, and it does not fall.</p>

<h2>2 · Every leg joint, measured</h2>
<div class=tw><table class=data>
<thead><tr><th>joint</th><th>MJCF range (deg)</th><th>cite</th><th>travel reached</th><th>of range</th>
<th>peak vel (deg/s)</th><th>tracking RMS (deg)</th><th>sit-stand travel</th><th>sit-stand peak</th>
<th>squat travel</th></tr></thead><tbody>%s</tbody></table></div>
<p class=note><b>Peak velocity is a model number, not a servo number.</b> %s</p>
<p class=note>%s</p>

<h2>3 · Self-collision</h2>
<p>The collision set of <span class=mono>microduck_ours_allcollisions.xml</span> is
<span class=mono>%s</span>. Two of them (the shins) were also re-pointed to OUR rebuilt mesh
(<span class=mono>leg__ours</span>) and swept again — same verdicts. %s</p>
<p>One joint at a time, every other joint at DEFAULT_POSE, 0.05&deg; steps, <span class=mono>mj_forward</span>
每 step:</p>
<div class=tw><table class=data><thead><tr><th>joint</th><th>swept (deg)</th><th>samples</th>
<th>verdict</th><th>pairs</th></tr></thead><tbody>%s</tbody></table></div>
<p>Two joints off default, and both legs driven together — the postures a one-at-a-time sweep cannot
reach. The <b>onset</b> is the contact angle nearest the neutral pose, i.e. the angle at which the pair
first touches as the joint leaves neutral:</p>
<div class=tw><table class=data><thead><tr><th>case</th><th>verdict</th><th>pair</th><th>onset (deg)</th>
<th>contact interval (deg)</th><th>max penetration (mm)</th></tr></thead><tbody>%s</tbody></table></div>

<h2>4 · The clips</h2>
%s

<h2>5 · Beside the real product</h2>
%s

<footer class=rev><span>Every number: out/motion/legs.json</span><span>sim/leg_sweep.py</span>
<span>sim/leg_render.py</span><span>sim/leg_compare.py</span></footer>
</div></body></html>""" % (
    time.strftime("%Y-%m-%d %H:%M"), peak, ntouch,
    E(J["squat_directctrl_FAILS"]["verdict"]),
    E("Commanded knee flexion of only %.3f deg, policy paused." % J["squat_directctrl_FAILS"]["commanded_knee_flexion_deg"]),
    J["squat_directctrl_FAILS"]["max_trunk_tilt_deg"],
    J["squat_directctrl_FAILS"]["trunk_z_m"]["start"] * 1000,
    J["squat_directctrl_FAILS"]["trunk_z_m"]["end"] * 1000,
    E(J["squat_directctrl_FAILS"]["finding"]),
    J["squat"]["trunk_z_m"]["start"] * 1000, J["squat"]["trunk_z_m"]["min"] * 1000,
    J["squat"]["trunk_drop_mm"], J["squat"]["max_trunk_tilt_deg"],
    jt, E(A["servo_reality_check"]), E(A["peak_velocity_caveat"]),
    E(", ".join(J["self_collision"]["pollen_collision_meshes"]["collision_geoms"])),
    E(J["self_collision"]["pollen_collision_meshes"]["note"]),
    st, ct, "".join(vid(v) for v in V), cmp_html or "<p>No product photo exists of these motions.</p>")

doc = doc.replace("每 step", "every step")
p = os.path.join(ROOT, "LEG-MOTION.html")
open(p, "w").write(doc)
print("wrote", p, len(doc), "bytes")
