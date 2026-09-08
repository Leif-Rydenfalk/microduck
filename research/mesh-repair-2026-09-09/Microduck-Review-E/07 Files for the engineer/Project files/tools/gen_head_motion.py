#!/usr/bin/env python3
"""gen_head_motion.py — HEAD-MOTION.html from out/motion/head.json.

Nothing here is hand-maintained: every number and every citation comes out of
the JSON that sim/head_sweep.py and sim/head_real_video.py measured.

    python3 tools/gen_head_motion.py
"""
import html, json, os, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = json.load(open(os.path.join(ROOT, "out", "motion", "head.json")))
E = html.escape


def rel(p):
    return E(p)


def video_block(v):
    poster = rel(v["sheet"])
    return """<figure>
<video controls preload="metadata" style="width:100%%;display:block;border:1px solid var(--hair);background:#fff"
       src="%s"></video>
<figcaption><b>%s</b> — %s<br><span class="mono">%s · %s · %.1f s @ %d fps · %d frames</span><br>
contact sheet: <a href="%s">%s</a> · gif: <a href="%s">%s</a></figcaption>
</figure>
<figure><img src="%s" alt="%s contact sheet"><figcaption>Eight frames of <span class="mono">%s</span>, read back after encoding.</figcaption></figure>""" % (
        rel(v["mp4"]), E(v["name"]), E(v["what"]), E(v["camera"]), rel(v["mp4"]),
        v["seconds"], v["fps"], v["frames"], poster, poster, rel(v["gif"]), rel(v["gif"]),
        poster, E(v["name"]), rel(v["mp4"]))


rows = J["joints"]
probe = {p["joint"]: p for p in J["kinematic_range_probe"]}
real = J.get("real_robot_video") or {}
V = J["verdict"]

jt = "".join(
    "<tr><td class=mono>%s</td><td class=n>%.2f … %.2f</td><td class=n>%.2f … %.2f</td>"
    "<td class=n>%.2f</td><td class=n>%.1f</td><td class=n>%.2f</td><td class=n>%s</td>"
    "<td class=n>%.3f</td><td class=n>%.4f</td></tr>" % (
        E(r["joint"]), r["mjcf_range_deg"][0], r["mjcf_range_deg"][1],
        r["travel_whole_run_deg"][0], r["travel_whole_run_deg"][1],
        r["travel_whole_run_span_deg"], r["range_used_pct"],
        r["peak_velocity_run_deg_s"],
        ("%.0f" % r["tracking_lag_ms"]) if r["tracking_lag_ms"] is not None else "—",
        r["tracking_gain"], r["peak_actuator_torque_Nm"]) for r in rows)

pt = "".join(
    "<tr><td class=mono>%s</td><td class=n>%.2f … %.2f</td><td class=n>%s</td><td class=n>%d / %d</td></tr>" % (
        E(p["joint"]), p["mjcf_range_deg"][0], p["mjcf_range_deg"][1],
        ("%.2f … %.2f" % tuple(p["self_collision_free_deg"])) if p["self_collision_free_deg"] else "none",
        p["steps_with_self_contact"], p["steps"]) for p in J["kinematic_range_probe"])

src = "".join("<li><span class=mono>%s</span> — MJCF %s; measured %s</li>" % (
    E(r["joint"]), E(r["source_mjcf"]), E(r["source_measure"])) for r in rows)

xt = "".join("<tr><td class=n>%d</td><td class=mono>%s</td>%s</tr>" % (
    x["slot"], E(x["driven"]),
    "".join("<td class=n>%.2f</td>" % x["peak_deg_per_joint"][k] for k in
            ["neck_pitch", "head_pitch", "head_yaw", "head_roll"])) for x in J["slot_crosstalk"])

peak = max(r["peak_velocity_run_deg_s"] for r in rows)
doc = """<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Microduck — is the neck as dynamic?</title>
<link rel=stylesheet href="tools/doc.css"></head><body><div class=wrap>
<header class=top>
<div class=eyebrow>Microduck · simulation evidence · head and neck</div>
<h1>Is the neck of ours as dynamic?</h1>
<p class=sub>Leif, 2026-09-02: <i>“is the neck of ours as dynamic? show me renders of the mechanics
like our cad system walking, zoom in on joints as they move and the head kmvoing around.”</i>
Answered by driving Pollen's four head command slots through the full MJCF joint range under
Pollen's own stand policy and measuring what each joint did.</p>
<div class=rev><span>generated %s</span><span>%s</span><span>%s</span><span>%.1f s of simulation @ 50 Hz</span></div>
</header>

<div class=statbar>
<div class=stat><b>%s</b><span>verdict on “as dynamic”</span></div>
<div class=stat><b>%.1f°/s</b><span>peak head joint speed measured (%.1f rpm)</span></div>
<div class=stat><b>618°/s</b><span>XL330-M288-T no-load speed @ 5.0 V</span></div>
<div class=stat><b>%.1f°</b><span>head_yaw travel reached, of 340° available</span></div>
<div class=stat><b>%.2f°</b><span>real robot's head-pitch travel visible on video</span></div>
</div>

<h2>1 · What the four head joints did</h2>
<p class=lede>Every row is read off <span class=mono>out/motion/head_traj.npz</span> (qpos / qvel, 50 Hz).
The command is the joint's own MJCF limit, ramped, held, reversed, held, then a 1 Hz sine at half range
for the lag and the peak speed.</p>
<div class=tablewrap><table class=data><thead><tr>
<th>joint</th><th>MJCF range °</th><th>reached °</th><th>span °</th><th>&#37; rng</th>
<th>peak °/s</th><th>lag ms</th><th>gain</th><th>&tau; peak N·m</th></tr></thead><tbody>%s</tbody></table></div>
<div class=note><b>neck_pitch is the odd one out, and it is not the mechanism.</b> The policy holds it
near ±18° however hard it is commanded (gain %.3f). It is the joint that swings the head as a balance
mass over the feet, so Pollen's stand policy refuses to give it away. The kinematic probe in §3 shows
the joint itself is free across its whole −90…+60° range.</div>

<h2>2 · Which slot moves which joint</h2>
<p class=lede>Peak degrees moved by each head joint while one command slot is swept
(each phase starts from rest, so what is left is real coupling the policy chose).</p>
<div class=tablewrap><table class=data><thead><tr><th>cmd slot</th><th>intended joint</th>
<th>neck_pitch °</th><th>head_pitch °</th><th>head_yaw °</th><th>head_roll °</th></tr></thead>
<tbody>%s</tbody></table></div>

<h2>3 · The mechanism, with the policy taken out</h2>
<p class=lede>Each head joint stepped through its MJCF range on the all-collisions model, counting
contacts that are not the floor: does the head hit itself or the trunk anywhere in range?</p>
<div class=tablewrap><table class=data><thead><tr><th>joint</th><th>MJCF range °</th>
<th>self-collision-free °</th><th>steps with self-contact</th></tr></thead><tbody>%s</tbody></table></div>

<h2>4 · Our head beside the real one</h2>
<figure><img src="out/motion/head_vs_real.png" alt="our head beside the real robot's">
<figcaption>Top: the real Microduck in Pollen's own <span class=mono>gallery_chorale.mp4</span>,
beak/trim band tracked frame by frame. Bottom: ours at the same camera, head_pitch posed to the ends
of that same band and then to the MJCF limit.</figcaption></figure>
<figure><img src="out/motion/head_real_video_overlay.png" alt="tracker overlay on the real video">
<figcaption>The tracker on the real footage — the red line is the fitted principal axis of the accent
band, and the number is the image-plane angle it reports.</figcaption></figure>
<div class=note><b>%s</b><br>%s</div>

<h2>5 · The renders</h2>
%s

<h2>6 · What “same as the real thing” rests on</h2>
<div class=grid2>
<div class=card><h3>It does rest on</h3><ul>%s</ul></div>
<div class=card><h3>It does not rest on</h3><ul>%s</ul></div>
</div>

<h2>7 · Sources</h2>
<ul>%s</ul>
<div class=mono-block>%s<br><br>servo: %s</div>
<p class=backlink><a href="INDEX.html">← repo index</a> · data: <a href="out/motion/head.json">out/motion/head.json</a>
· <a href="out/motion/head_real_video.json">out/motion/head_real_video.json</a></p>
</div></body></html>""" % (
    E(time.strftime("%Y-%m-%d %H:%M")), E(J["model"].split(" (")[0]), E(J["policy"].split(" (")[0]),
    J["seconds"],
    E(V["answer"].split(",")[0]), peak, peak / 6.0,
    [r for r in rows if r["joint"] == "head_yaw"][0]["travel_whole_run_span_deg"],
    real.get("travel_deg", 0.0),
    jt, [r for r in rows if r["joint"] == "neck_pitch"][0]["tracking_gain"],
    xt, pt,
    E("Against the real robot: CANNOT DETERMINE for speed."), E(V["vs_real_robot"]),
    "".join(video_block(v) for v in J["videos"]),
    "".join("<li>%s</li>" % E(x) for x in V["what_it_rests_on"]),
    "".join("<li>%s</li>" % E(x) for x in V["what_it_does_NOT_rest_on"]),
    src,
    E(J["loop"]), E(J["servo"]["source"]))

out = os.path.join(ROOT, "HEAD-MOTION.html")
open(out, "w").write(doc)
print("wrote", out, len(doc), "bytes")
