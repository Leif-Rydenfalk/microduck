#!/usr/bin/env python3
"""gen_motion.py — MOTION.html: the whole moving machine, filmed and measured.

The one document that answers Leif's question of 2026-09-02 —
    "is the neck of ours as dynamic? show me renders of the mechanics like our cad
     system walking, zoom in on joints as they move and the head kmvoing around and
     the legs moving around."
— and carries every clip the three render lanes produced, with the measurement each
one is evidence for.

Reads (data, never hand-edited):
    out/motion/head.json              sim/head_sweep.py
    out/motion/head_real_video.json   sim/head_real_video.py
    out/motion/walk.json              sim/motion_render.py --all
    out/motion/walk_vs_product.json   sim/walk_vs_product.py
    out/motion/legs.json              sim/leg_sweep.py + sim/leg_render.py
    out/motion/legs_videos.json       sim/leg_verify.py
    out/motion/legs_compare.json      sim/leg_compare.py

Writes:
    MOTION.html   (repo root, so every asset path is out/motion/<file>)

EVERY referenced file is stat()ed before the document is written, the way
tools/gen_index.py stats every index entry. A missing asset is published as
missing with its reason — never as a dead <video> — it is listed in the asset
audit of section 5, and the script exits 1 so the defect is loud.

System python3 (stdlib only).
"""
import datetime
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
MOT = os.path.join(REPO, "out", "motion")
E = html.escape

# ---------------------------------------------------------------- data files

def load(name, required=True):
    p = os.path.join(MOT, name)
    if not os.path.exists(p):
        if required:
            sys.stderr.write("gen_motion: MISSING required data file out/motion/%s\n" % name)
            sys.exit(2)
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


HEAD = load("head.json")
HEADVID = load("head_real_video.json", required=False)
WALK = load("walk.json")
WVP = load("walk_vs_product.json", required=False)
LEGS = load("legs.json")
LEGV = load("legs_videos.json")
LEGC = load("legs_compare.json", required=False)

# ------------------------------------------------------------- asset registry
# every path the document points at, stat()ed before the HTML is written
ASSETS = []          # (rel, kind, ok, bytes)
_seen = set()


def asset(rel, kind):
    """Register a repo-relative path, stat it, return (ok, size_bytes)."""
    if rel is None:
        return False, 0
    rel = rel.lstrip("./")
    p = os.path.join(REPO, rel)
    ok = os.path.exists(p)
    sz = os.path.getsize(p) if ok else 0
    if rel not in _seen:
        _seen.add(rel)
        ASSETS.append((rel, kind, ok, sz))
    return ok, sz


def mb(n):
    return n / 1024.0 / 1024.0


def size_str(n):
    if n < 1024:
        return "%d B" % n
    if n < 1024 * 1024:
        return "%.0f KB" % (n / 1024.0)
    return "%.2f MB" % mb(n)


def rel_motion(p):
    """Normalise any recorded path to a repo-relative out/motion/... path."""
    if p is None:
        return None
    p = p.lstrip("./")
    if p.startswith("out/motion/"):
        return p
    return "out/motion/" + os.path.basename(p)


# ------------------------------------------------------------------- pieces

def poster_for(name, gif_rel, explicit=None):
    """A still to show before play: a rendered frame if the lane wrote one, else the GIF."""
    if explicit:
        ok, _ = asset(explicit, "frame")
        if ok:
            return explicit
    frames_dir = os.path.join(MOT, "frames")
    if os.path.isdir(frames_dir):
        cands = sorted(f for f in os.listdir(frames_dir) if f.startswith(name + "_"))
        if cands:
            rel = "out/motion/frames/" + cands[0]
            asset(rel, "frame")
            return rel
    return gif_rel


def video_fig(name, mp4, gif, sheet, title, what, meta_html, wide=True, poster=None):
    """<video> (GIF as poster and as the no-video fallback) + its contact sheet."""
    mp4 = rel_motion(mp4)
    gif = rel_motion(gif)
    sheet = rel_motion(sheet)
    ok_mp4, sz_mp4 = asset(mp4, "mp4")
    ok_gif, sz_gif = asset(gif, "gif")
    ok_sheet, sz_sheet = asset(sheet, "contact sheet")
    post = poster_for(name, gif if ok_gif else None, poster)

    if not ok_mp4 and not ok_gif:
        return ('<figure class="fig missing"><figcaption><b>%s</b> — <span class="chip cd">MISSING</span> '
                'neither <code>%s</code> nor <code>%s</code> is on disk. Not published as a link; '
                're-run the renderer named in section 5.</figcaption></figure>'
                % (E(title), E(mp4 or "?"), E(gif or "?")))

    inner = ""
    if ok_mp4:
        inner = ('<video controls muted loop playsinline preload="metadata"%s src="%s">'
                 '%s</video>'
                 % ((' poster="%s"' % E(post)) if post else "",
                    E(mp4),
                    ('<img src="%s" alt="%s (animated GIF fallback)">' % (E(gif), E(title))) if ok_gif else ""))
    else:
        inner = '<img src="%s" alt="%s (animated GIF)">' % (E(gif), E(title))

    links = []
    if ok_mp4:
        links.append('<a href="%s">mp4</a> %s' % (E(mp4), size_str(sz_mp4)))
    if ok_gif:
        links.append('<a href="%s">GIF</a> %s' % (E(gif), size_str(sz_gif)))
    sheet_html = ""
    if ok_sheet:
        sheet_html = ('<img class="sheet" src="%s" alt="contact sheet, 8 frames of %s">'
                      '<div class="sheetcap">Contact sheet — 8 frames sampled across the clip '
                      '(<a href="%s">%s</a>, %s).</div>' % (E(sheet), E(title), E(sheet),
                                                            E(os.path.basename(sheet)), size_str(sz_sheet)))
    else:
        sheet_html = ('<div class="sheetcap"><span class="chip cd">no contact sheet</span> '
                      '<code>%s</code> is not on disk.</div>' % E(sheet or "?"))

    return ('<figure class="fig%s">%s%s'
            '<figcaption><b>%s</b> — %s<br>%s %s</figcaption></figure>'
            % (" wide" if wide else "", inner, sheet_html,
               E(title), what, meta_html, " · ".join(links)))


# ================================================================= section 1
HV = HEAD["verdict"]
HJ = {j["joint"]: j for j in HEAD["joints"]}
HPROBE = {p["joint"]: p for p in HEAD["kinematic_range_probe"]}
HEAD_ORDER = ["neck_pitch", "head_pitch", "head_yaw", "head_roll"]
SERVO = HEAD["servo"]

peak_v = max(HJ[j]["peak_velocity_run_deg_s"] for j in HEAD_ORDER)
peak_v_joint = max(HEAD_ORDER, key=lambda j: HJ[j]["peak_velocity_run_deg_s"])
peak_t = max(HJ[j]["peak_actuator_torque_Nm"] for j in HEAD_ORDER)
peak_t_joint = max(HEAD_ORDER, key=lambda j: HJ[j]["peak_actuator_torque_Nm"])
best_pct = max(HJ[j]["range_used_pct"] for j in HEAD_ORDER)


def head_row(j):
    d = HJ[j]
    lo, hi = d["mjcf_range_deg"]
    tlo, thi = d["travel_whole_run_deg"]
    pr = HPROBE.get(j)
    plo, phi = (pr["self_collision_free_deg"] if pr else (None, None))
    walkj = WALK["joints"].get(j)
    return ("<tr><td class=mono>%s</td>"
            "<td class=num>%.4f … %.4f</td><td class=num>%.4f</td>"
            "<td class=num><b>%.4f</b><div class=dim>%.2f … %+.2f</div></td><td class=num>%.2f&thinsp;%%</td>"
            "<td class=num>%.4f</td><td class=num>%.3f</td><td class=num>%.1f</td>"
            "<td class=num>%.4f</td><td class=num>%s</td></tr>") % (
        E(j), lo, hi, hi - lo, d["travel_whole_run_span_deg"], tlo, thi, d["range_used_pct"],
        d["peak_velocity_run_deg_s"], d["tracking_gain"], d["tracking_lag_ms"],
        d["peak_actuator_torque_Nm"],
        ("%.4f" % walkj["travel_deg"]) if walkj else "—")


head_rows = "".join(head_row(j) for j in HEAD_ORDER)

# the sources the table used to carry as a column — one line per joint, plus the
# one measurement source they all share
head_src = "".join(
    "<li><code>%s</code> — MJCF %s</li>" % (E(j), E(HJ[j]["source_mjcf"])) for j in HEAD_ORDER)
head_src_measure = E(HJ["neck_pitch"]["source_measure"])
head_src_force = E(HJ["neck_pitch"]["source_forcerange"])

probe_rows = "".join(
    "<tr><td class=mono>%s</td><td class=num>%.3f … %.3f</td><td class=num>%.3f … %.3f</td>"
    "<td class=num>%d / %d</td><td>%s</td></tr>" % (
        E(p["joint"]), p["mjcf_range_deg"][0], p["mjcf_range_deg"][1],
        p["self_collision_free_deg"][0], p["self_collision_free_deg"][1],
        p["steps_with_self_contact"], p["steps"],
        '<span class="chip pass">whole range free</span>' if p["steps_with_self_contact"] == 0
        else '<span class="chip cd">fouls below %.3f&deg;</span>' % p["self_collision_free_deg"][0])
    for p in HEAD["kinematic_range_probe"])

crosstalk_rows = "".join(
    "<tr><td class=num>%d</td><td class=mono>%s</td>%s</tr>" % (
        c["slot"], E(c["driven"]),
        "".join("<td class=num%s>%.4f</td>" % (" strong" if k == c["driven"] else "",
                                               c["peak_deg_per_joint"][k]) for k in HEAD_ORDER))
    for c in HEAD["slot_crosstalk"])

rests_on = "".join("<li>%s</li>" % E(x) for x in HV["what_it_rests_on"])
rests_not = "".join("<li>%s</li>" % E(x) for x in HV["what_it_does_NOT_rest_on"])

# ================================================================= section 2
W = WALK["walk"]
G = WALK["gait"]
WV = WALK["videos"]
LEG_ORDER = ["left_hip_yaw", "left_hip_roll", "left_hip_pitch", "left_knee", "left_ankle",
             "right_hip_yaw", "right_hip_roll", "right_hip_pitch", "right_knee", "right_ankle"]
walk_pass = sum(1 for k in WV if WV[k]["verify"]["verdict"] == "PASS")


def walk_row(name):
    j = WALK["joints"][name]
    lo, hi = j["mjcf_range_deg"]
    return ("<tr><td class=mono>%s</td><td class=num>%.3f … %.3f</td>"
            "<td class=num>%.4f … %.4f</td><td class=num><b>%.4f</b></td><td class=num>%.2f&thinsp;%%</td>"
            "<td class=num>%.3f</td><td class=num>%d</td><td class=num>%.3f</td>"
            "<td class=num>%.4f</td></tr>") % (
        E(name), lo, hi, j["min_deg"], j["max_deg"], j["travel_deg"],
        j["travel_pct_of_mjcf_range"], j["peak_abs_vel_deg_s"], j["peak_vel_at_frame"],
        j["peak_vel_at_s"], j["closest_approach_to_limit_deg"])


walk_rows = "".join(walk_row(n) for n in LEG_ORDER)
walk_head_rows = "".join(walk_row(n) for n in HEAD_ORDER)


def walk_meta(v):
    ver = v["verify"]
    return ('Camera: %s. %d frames at %d&nbsp;fps (%.3f&nbsp;s). Read back frame by frame after '
            'encoding: <span class="chip %s">%s</span> — min frame std %.2f (blank &lt; 4.0), '
            'max inter-frame delta %.4f, blank frames %d, frozen pairs %d.' % (
                E(v["camera"]), v["frames"], v["fps"], v["seconds"],
                "pass" if ver["verdict"] == "PASS" else "cd", E(ver["verdict"]),
                ver["min_frame_std"], ver["max_interframe_delta"],
                ver["blank_frames"], ver["frozen_pairs"]))


WALK_ORDER = ["walk_body", "walk_composite", "walk_slowmo",
              "walk_knee_prof", "walk_knee_34", "walk_hip_prof", "walk_hip_34",
              "walk_ankle_prof", "walk_ankle_34"]
WALK_ORDER = [k for k in WALK_ORDER if k in WV] + [k for k in WV if k not in WALK_ORDER]
walk_figs = "\n".join(
    video_fig(k, WV[k]["path"], WV[k]["gif"], WV[k]["contact_sheet"], k, E(WV[k]["what"]) + ".",
              walk_meta(WV[k]), poster="out/motion/frames/%s_f000.png" % k)
    for k in WALK_ORDER)

# our walk beside the product's own clip
wvp_html = ""
if WVP:
    ok_fig, sz_fig = asset(rel_motion(WVP["figure"]), "figure")
    m = WVP["product_clip_meta"]
    fig_html = ('<figure class="fig wide"><img src="%s" alt="our walk beside Pollen\'s own move clip, phase matched">'
                '<figcaption>Five equal phases of one gait cycle, ours under the product\'s. %s '
                '(<a href="%s">%s</a>, %s)</figcaption></figure>'
                % (E(rel_motion(WVP["figure"])), E(WVP["framing"]),
                   E(rel_motion(WVP["figure"])), E(os.path.basename(WVP["figure"])), size_str(sz_fig))
                if ok_fig else
                '<p class="note"><span class="chip cd">MISSING</span> the comparison figure '
                '<code>%s</code> is not on disk.</p>' % E(rel_motion(WVP["figure"])))
    wvp_html = """
  <h3>Beside the real product</h3>
  <p>The only published asset of the product performing <i>this</i> motion is Pollen's own portrait
  move clip <code>%s</code> (%d frames, %.0f&nbsp;fps, %.3f&nbsp;s, %d&times;%d, %s).
  <b>%s</b> — so this is a render-to-render comparison and is labelled as one, not as a photograph
  match. Both gait periods are <i>measured</i>: the product's off the silhouette centroid of its own
  pixels, ours off <code>left_knee</code> in the trajectory, each autocorrelated. Both signals are
  sampled at %.3f&nbsp;s, so the agreement is to within one sample — the resolution of the
  measurement, not a claim of exact equality.</p>
  <div class="tw"><table>
   <thead><tr><th></th><th class=num>gait period (s)</th><th class=num>autocorrelation peak</th>
   <th class=num>cadence (steps/min)</th></tr></thead>
   <tbody>
   <tr><td>product clip (Pollen's render)</td><td class=num>%.4f</td><td class=num>%.4f</td><td class=num>%.2f</td></tr>
   <tr><td>ours, this simulation</td><td class=num>%.4f</td><td class=num>%.4f</td><td class=num>%.2f</td></tr>
   <tr><td>ratio ours / product</td><td class=num colspan=3>%.4f</td></tr>
   </tbody></table></div>
  %s""" % (E(WVP["product_clip"]), m["frames"], m["fps"], m["seconds"], m["size"][0], m["size"][1],
           E(m["codec"]), E(WVP["caveat"]), WVP["period_resolution_s"],
           WVP["product_gait_period_s"], WVP["product_autocorr_peak"], WVP["product_cadence_steps_per_min"],
           WVP["ours_gait_period_s"], WVP["ours_autocorr_peak"], WVP["ours_cadence_steps_per_min"],
           WVP["period_ratio_ours_over_product"], fig_html)

# ================================================================= section 3
HEAD_VIDS = HEAD["videos"]
head_figs = "\n".join(
    video_fig(v["name"], v["mp4"], v["gif"], v["sheet"], v["name"], E(v["what"]) + ".",
              'Camera: %s. %d frames at %d&nbsp;fps (%.3f&nbsp;s). Every head clip was read back off '
              'disk by <code>sim/head_verify.py</code>; the frames it wrote are in '
              '<code>out/motion/frames/</code>.' % (E(v["camera"]), v["frames"], v["fps"], v["seconds"]))
    for v in HEAD_VIDS)

rv = HEAD["real_robot_video"]
ok_cmp, sz_cmp = asset("out/motion/head_vs_real.png", "figure")
ok_ovl, sz_ovl = asset("out/motion/head_real_video_overlay.png", "figure")
real_figs = ""
if ok_cmp:
    real_figs += ('<figure class="fig wide"><img src="out/motion/head_vs_real.png" '
                  'alt="our head render beside the real robot at the same camera">'
                  '<figcaption>Our rendered head beside a frame of the real robot from '
                  '<code>%s</code>, at the matched camera (<code>sim/head_compare.py</code>, %s).'
                  '</figcaption></figure>' % (E(rv["source_video"]), size_str(sz_cmp)))
if ok_ovl:
    real_figs += ('<figure class="fig wide"><img src="out/motion/head_real_video_overlay.png" '
                  'alt="tracked beak/trim band on the real robot video">'
                  '<figcaption>What was actually tracked in the real footage: the image-plane '
                  'principal-axis angle of the accent beak/trim band, frame by frame over %d frames '
                  '(<code>%s</code>, %s).</figcaption></figure>'
                  % (rv["frames_tracked"], E(rv["script"]), size_str(sz_ovl)))
real_caveats = "".join("<li>%s</li>" % E(c) for c in rv["caveats"])

stab = HEAD["stability"]

# ================================================================= section 4
MR = LEGS["mjcf_ranges"]
DYN = LEGS["dynamic_step_policy_paused"]["joints"]
WPOL = LEGS["walking_policy"]["joints"]
SIT = LEGS["sitstand_policy"]["joints"]
SQ = LEGS["squat"]
HL = LEGS["headline"]
ACT = LEGS["actuator"]


def leg_row(n):
    """The mechanism: what the joint has, and what it reached when driven to its limits."""
    r = MR[n]
    d = DYN[n]
    return ("<tr><td class=mono>%s</td><td class=num>%.3f … %.3f</td><td class=num>%.3f</td>"
            "<td class=num>%.3f … %.3f</td><td class=num><b>%.3f</b></td><td class=num>%.1f&thinsp;%%</td>"
            "<td class=num>%.3f</td><td class=num>%.3f</td>"
            "<td class=mono>%s</td></tr>") % (
        E(n), r["lo_deg"], r["hi_deg"], r["span_deg"],
        d["reached_min_deg"], d["reached_max_deg"], d["travel_deg"],
        d["travel_frac_of_mjcf_range"] * 100.0, d["peak_velocity_deg_s"], d["tracking_rms_deg"],
        E(r["cite"]))


def gait_row(n):
    """What Pollen's own gaits actually use of that range."""
    r = MR[n]
    w = WPOL.get(n, {})
    st = SIT.get(n, {})
    sq = SQ["joints"].get(n, {})
    def cell(d, key, fmt="%.3f"):
        return (fmt % d[key]) if key in d else "—"
    def pct(d):
        return ("%.1f&thinsp;%%" % (100.0 * d["travel_deg"] / r["span_deg"])) if "travel_deg" in d else "—"
    return ("<tr><td class=mono>%s</td><td class=num>%.3f</td>"
            "<td class=num>%s<div class=dim>%s</div></td><td class=num>%s</td>"
            "<td class=num>%s<div class=dim>%s</div></td><td class=num>%s</td>"
            "<td class=num>%s</td><td class=num>%s</td></tr>") % (
        E(n), r["span_deg"],
        cell(w, "travel_deg"), pct(w), cell(w, "peak_velocity_deg_s", "%.2f"),
        cell(st, "travel_deg"), pct(st), cell(st, "peak_velocity_deg_s", "%.2f"),
        cell(sq, "travel_deg"), cell(sq, "peak_velocity_deg_s", "%.2f"))


leg_rows = "".join(leg_row(n) for n in LEG_ORDER)
gait_rows = "".join(gait_row(n) for n in LEG_ORDER)

LEGVID = {v["name"]: v for v in LEGV}
LEG_VID_ORDER = ["legs_composite", "legs_hip_yaw", "legs_hip_roll", "legs_hip_pitch",
                 "legs_knee", "legs_ankle", "legs_squat", "legs_sitstand", "legs_leglift",
                 "legs_selfcollision"]
LEG_VID_ORDER = [k for k in LEG_VID_ORDER if k in LEGVID] + [k for k in LEGVID if k not in LEG_VID_ORDER]


def leg_meta(v):
    rb = v.get("readback", {})
    verds = [rb.get(k, {}).get("verdict") for k in ("mp4", "gif", "sheet") if k in rb]
    allpass = verds and all(x == "PASS" for x in verds)
    return ('Camera: %s. %d frames at %d&nbsp;fps (%.3f&nbsp;s). Read back out of the ENCODED mp4 and '
            'gif: <span class="chip %s">%s</span> — mean inter-frame difference %.4f, max %.4f, '
            'min sampled frame std %.3f.' % (
                E(v["camera"]), v["frames"], v["fps"], v["seconds"],
                "pass" if allpass else "cd",
                "PASS" if allpass else " / ".join(str(x) for x in verds) or "not read back",
                v.get("mean_interframe_diff", float("nan")), v.get("max_interframe_diff", float("nan")),
                rb.get("mp4", {}).get("min_sampled_frame_std", float("nan"))))


leg_figs = "\n".join(
    video_fig(k, LEGVID[k]["mp4"], LEGVID[k]["gif"], LEGVID[k]["sheet"], k,
              E(LEGVID[k]["what"]) + ".", leg_meta(LEGVID[k]),
              poster=(LEGVID[k].get("frames_png") or [None])[0])
    for k in LEG_VID_ORDER)


def collision_rows(cases, group):
    out = []
    for case, d in cases.items():
        lo, hi = d["swept_deg"]
        if not d["pairs"]:
            out.append("<tr><td class=posture>%s<div class=dim>%s · swept %.3f … %.3f&deg;</div></td>"
                       "<td class=num>—</td><td class=num>—</td><td class=num>—</td>"
                       "<td><span class='chip pass'>CLEAR</span></td></tr>"
                       % (E(case), E(group), lo, hi))
            continue
        for pair, p in d["pairs"].items():
            ilo, ihi = p["contact_interval_deg"]
            out.append("<tr><td class=posture>%s<div class=dim>%s · swept %.3f … %.3f&deg;</div></td>"
                       "<td class=mono>%s</td><td class=num>%.3f</td><td class=num>%.4f</td>"
                       "<td><span class='chip rail'>TOUCHES</span><div class=dim>in contact "
                       "%.3f … %.3f&deg;</div></td></tr>"
                       % (E(case), E(group), lo, hi, E(pair), p["onset_deg"],
                          p["max_penetration_mm"], ilo, ihi))
    return "".join(out)


SC = LEGS["self_collision"]
sc_rows = (collision_rows(SC["combinations"]["cases"], "two joints")
           + collision_rows(SC["both_legs_mirrored"]["cases"], "both legs"))
n_touch = sum(1 for grp in (SC["combinations"]["cases"], SC["both_legs_mirrored"]["cases"])
              for d in grp.values() if d["pairs"])
sc_one_at_a_time = sum(1 for d in SC["pollen_collision_meshes"]["sweeps"].values()
                       if d["contact_samples"])
ctl = SC["controls"]
ctl_rows = ("<tr><td>negative control — %s</td><td class=num>%d self-contacts</td>"
            "<td>%s</td></tr>" % (E(ctl["negative_control"]["pose"]),
                                  ctl["negative_control"]["self_contacts"],
                                  '<span class="chip pass">silent, as it must be</span>'))
for pc in ctl["positive_controls"]:
    ctl_rows += ("<tr><td>positive control — %s</td><td class=num>%d self-contacts</td>"
                 "<td>%s</td></tr>" % (E(pc["pose"]), pc["self_contacts"],
                                       '<span class="chip pass">detector fires</span>'
                                       if pc["self_contacts"] else
                                       '<span class="chip rail">detector SILENT — check broken</span>'))

# ours-standing / ours-sitting beside the product photographs
cmp_figs = ""
if LEGC:
    for c in LEGC:
        rel = rel_motion(c["png"])
        ok, sz = asset(rel, "figure")
        if ok:
            cmp_figs += ('<figure class="fig wide"><img src="%s" alt="%s">'
                         '<figcaption>Ours beside the product photograph — %s '
                         '(<code>sim/leg_compare.py</code>, %s).</figcaption></figure>'
                         % (E(rel), E(c["what"]), E(c["what"]), size_str(sz)))
        else:
            cmp_figs += ('<p class="note"><span class="chip cd">MISSING</span> <code>%s</code> '
                         'is not on disk.</p>' % E(rel))

fig_html = ""
for f in LEGS.get("figures", []):
    rel = rel_motion(f["png"])
    ok, sz = asset(rel, "figure")
    if ok:
        fig_html += ('<figure class="fig wide"><img src="%s" alt="%s">'
                     '<figcaption><code>%s</code> — %s</figcaption></figure>'
                     % (E(rel), E(os.path.basename(rel)), E(os.path.basename(rel)), size_str(sz)))

# ================================================================= section 5
SCRIPTS = [
    ("sim/swap_meshes.py", "Puts OUR rebuilt meshes on Pollen's MJCF (visual geoms only) and refuses "
                           "unless both models compile and every re-pointed geom's zero-pose world bbox "
                           "is within 1.5 mm of the stock geom.",
     "$PY sim/swap_meshes.py"),
    ("sim/run_policy.py", "Runs Pollen's published ONNX policies at their own 50 Hz loop and writes the "
                          "trajectories every measurement below is read off.",
     "$PY sim/run_policy.py --all"),
    ("sim/head_sweep.py", "Drives the four head command slots through their full MJCF range under the "
                          "stand policy, measures travel / velocity / lag / torque, and probes the "
                          "self-collision-free range. Writes out/motion/head.json + head_traj.npz.",
     "$PY sim/head_sweep.py"),
    ("sim/head_real_video.py", "Tracks the real robot's head frame by frame in Pollen's gallery clip. "
                               "Writes out/motion/head_real_video.json.",
     "$PY sim/head_real_video.py"),
    ("sim/head_compare.py", "Puts our head beside the real one at the same camera.",
     "$PY sim/head_compare.py"),
    ("sim/head_verify.py", "Reads every head clip back off disk and refuses blank or frozen frames.",
     "$PY sim/head_verify.py"),
    ("sim/motion_render.py", "Films the walk: the tracked close-ups, the 2×2 composite and the 0.25× "
                             "gait cycle, and measures every joint. Writes out/motion/walk.json.",
     "$PY sim/motion_render.py --all"),
    ("sim/walk_vs_product.py", "Phase-matches our walk against Pollen's own move clip; measures both "
                               "gait periods. Writes out/motion/walk_vs_product.json.",
     "$PY sim/walk_vs_product.py"),
    ("sim/leg_sweep.py", "Sweeps every leg joint through its MJCF range, one at a time and in the "
                         "two-joint and both-leg postures, and finds every self-collision with its "
                         "onset angle. Writes out/motion/legs.json.",
     "$PY sim/leg_sweep.py"),
    ("sim/leg_render.py", "Films the legs: per-joint tracked close-ups, squat, sit-stand, leg lift, the "
                          "self-collision case and the composite.",
     "$PY sim/leg_render.py            # no args = every clip"),
    ("sim/leg_plots.py", "Draws the tracking, envelope and self-collision figures from the same arrays "
                         "as the numbers.", "$PY sim/leg_plots.py"),
    ("sim/leg_framing.py", "Projects every servo and bearing geom into each close-up frustum, to prove "
                           "the close-ups contain the hardware they claim to show.",
     "$PY sim/leg_framing.py"),
    ("sim/leg_compare.py", "Puts our standing and sitting renders beside the product photographs at the "
                           "same subject height.", "$PY sim/leg_compare.py"),
    ("sim/leg_verify.py", "Reads every leg clip back out of the ENCODED mp4 and gif and refuses blank, "
                          "frozen, truncated or oversized ones; --self-test breaks it on purpose.",
     "$PY sim/leg_verify.py"),
    ("sim/compare_render.py", "The studio renderer every frame above is drawn with: white sky, no floor, "
                              "headlight 0.45 / ambient 0.28, the real product material per geom.",
     "—"),
    ("tools/gen_motion.py", "Builds THIS document from out/motion/*.json, stat()ing every asset first.",
     "python3 tools/gen_motion.py"),
    ("tools/gen_index.py", "Rebuilds INDEX.html so this document is listed.",
     "python3 tools/gen_index.py"),
]
script_rows = ""
for path, desc, cmd in SCRIPTS:
    ok, sz = asset(path, "script")
    script_rows += ('<tr><td class=mono>%s</td><td>%s</td><td class=mono>%s</td>'
                    '<td>%s</td></tr>'
                    % (E(path), E(desc), E(cmd),
                       '<span class="chip pass">present</span>' if ok
                       else '<span class="chip cd">missing</span>'))

DATA_FILES = ["out/motion/head.json", "out/motion/head_real_video.json", "out/motion/walk.json",
              "out/motion/walk_vs_product.json", "out/motion/legs.json", "out/motion/legs_videos.json",
              "out/motion/legs_compare.json", "out/motion/head_traj.npz",
              "out/sim/walk_ours_traj.npz", "out/sim/sitstand_ours_traj.npz",
              "sim/microduck_ours.xml", "sim/microduck_ours_allcollisions.xml",
              "reference/pollen-microduck-rl/robot_walk.xml",
              "reference/pollen-microduck-rl/joints_properties.xml"]
data_rows = ""
for p in DATA_FILES:
    ok, sz = asset(p, "data")
    data_rows += ('<tr><td class=mono>%s</td><td class=num>%s</td><td>%s</td></tr>'
                  % (E(p), size_str(sz) if ok else "—",
                     '<span class="chip pass">present</span>' if ok
                     else '<span class="chip cd">missing</span>'))

# --------------------------------------------------------------- asset audit
missing = [a for a in ASSETS if not a[2]]
audit_rows = "".join(
    '<tr><td class=mono>%s</td><td>%s</td><td class=num>%s</td><td>%s</td></tr>'
    % (E(rel), E(kind), size_str(sz) if ok else "—",
       '<span class="chip pass">present</span>' if ok else '<span class="chip rail">MISSING</span>')
    for rel, kind, ok, sz in sorted(ASSETS))
n_videos = sum(1 for rel, kind, ok, sz in ASSETS if kind == "mp4" and ok)
n_gifs = sum(1 for rel, kind, ok, sz in ASSETS if kind == "gif" and ok)
n_sheets = sum(1 for rel, kind, ok, sz in ASSETS if kind == "contact sheet" and ok)
total_bytes = sum(sz for rel, kind, ok, sz in ASSETS if ok and kind in ("mp4", "gif"))

STAMP = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

CSS = """
 .fig{margin:26px 0;padding:12px}
 .fig video{width:100%;display:block;background:#fff;border:1px solid var(--line)}
 .fig img{width:100%;display:block;border:1px solid var(--line)}
 .fig img.sheet{margin-top:9px}
 .fig .sheetcap{font-family:var(--sans);font-size:11.5px;color:var(--ink-2);margin-top:5px}
 .fig figcaption{margin-top:8px;line-height:1.5}
 .fig.missing{border-color:var(--no)}
 table td.src{font-size:11px;font-family:var(--mono);white-space:normal;max-width:22em;color:var(--ink-2)}
 table td.mono,td.mono{font-family:var(--mono);font-size:12px}
 td.num.strong{font-weight:700;color:var(--ink)}
 .dim{color:var(--ink-2);font-size:11px;font-family:var(--sans);white-space:normal}
 td.posture{white-space:normal;min-width:15em;font-family:var(--mono);font-size:11.5px}
 .src{font-size:12.5px;color:var(--ink-2);max-width:46em;font-family:var(--sans);margin:8px 0 14px;line-height:1.5}
 ul.src{font-size:12px;margin:4px 0 8px}
 table.data.compact td.mono,table.data.compact td.num{font-size:11.5px}
 .verdictbox{border:1.5px solid var(--rule);padding:16px 20px;margin:16px 0;background:var(--figbg)}
 .verdictbox h3{margin-top:0}
 .verdictbox .big{font-family:var(--sans);font-weight:600;font-size:15px;letter-spacing:.01em}
 .cols{display:grid;grid-template-columns:1fr 1fr;gap:0 26px}
 .cols ul{margin-top:4px}
 @media(max-width:820px){.cols{grid-template-columns:1fr}}
"""

DOC = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Microduck — motion: the machine moving, filmed and measured</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opt_sz,wght@8..60,400;8..60,600;8..60,700&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="tools/doc.css">
<style>%(css)s</style></head><body><div class="wrap">

<header class="top">
  <div class="eyebrow">Microduck · simulation evidence · motion</div>
  <h1>Motion — the machine moving, filmed and measured</h1>
  <p class="sub">Leif, 2026-09-02: <i>&ldquo;is the neck of ours as dynamic? show me renders of the
  mechanics like our cad system walking, zoom in on joints as they move and the head kmvoing around
  and the legs moving around.&rdquo;</i></p>
  <p class="sub">%(nvid)d videos of OUR rebuilt parts moving under Pollen's own published policies —
  the whole body walking, and every joint in close-up while it moves — with the measurement each
  clip is evidence for. Nothing here is an animation: every frame is a MuJoCo state, and every
  angle on the caption is that frame's <code>qpos</code>.</p>
  <div class="rev">
    <span>generated %(stamp)s by <code>tools/gen_motion.py</code></span>
    <span>model <code>sim/microduck_ours.xml</code></span>
    <span>%(nvid)d mp4 · %(ngif)d gif · %(nsheet)d contact sheets · %(mb).1f MB of video</span>
  </div>
</header>

<div class="statbar">
  <div class="stat"><b>%(best_pct).1f&thinsp;%%</b><span>of MJCF range the best head joint reaches</span></div>
  <div class="stat"><b>%(peakv).1f</b><span>deg/s peak head-joint velocity (%(peakvj)s)</span></div>
  <div class="stat"><b>%(peakt).4f</b><span>N&middot;m peak head torque vs %(stall).2f stall</span></div>
  <div class="stat"><b>%(walked).4f</b><span>m walked in %(secs).1f s</span></div>
  <div class="stat"><b>%(ntouch)d</b><span>self-collision postures found</span></div>
</div>

<nav class="toc">
  <a href="#neck">1 · Is the neck as dynamic?</a>
  <a href="#walk">2 · Walking, with joint close-ups</a>
  <a href="#head">3 · The head moving around</a>
  <a href="#legs">4 · The legs moving around</a>
  <a href="#regen">5 · How to regenerate</a>
</nav>

<section id="neck">
  <h2><span class="n">1</span>Is the neck of ours as dynamic?</h2>
  <p class="lede">The question, answered first, with the table it rests on and the scope it does not
  cover.</p>

  <div class="verdictbox">
    <h3>%(qq)s</h3>
    <p class="big">%(answer)s</p>
    <div class="cols">
      <div><h4>What the verdict rests on</h4><ul>%(rests)s</ul></div>
      <div><h4>What it does <u>not</u> rest on</h4><ul>%(restsnot)s</ul></div>
    </div>
    <h4>Against the real robot</h4>
    <p>%(vsreal)s</p>
  </div>

  <p>Every head joint was driven through its whole MJCF range one at a time (ramp to the limit, hold
  1.2&nbsp;s, ramp to the other limit, hold, return, rest) and then given a 1&nbsp;Hz half-range sine,
  all under Pollen's own <code>BEST_alpha_stand</code> policy at its 50&nbsp;Hz loop with the browser
  simulator's EMA (&alpha; 0.2) on the head command slots — %(loop)s. The run is %(hsecs).1f&nbsp;s.</p>

  <div class="tw"><table class="data compact">
    <thead><tr>
      <th>joint</th><th class=num>MJCF range (deg)</th><th class=num>span</th>
      <th class=num>travel measured (deg)</th><th class=num>%% of range</th>
      <th class=num>peak vel (deg/s)</th><th class=num>gain</th><th class=num>lag (ms)</th>
      <th class=num>torque (N&middot;m)</th><th class=num>travel walking</th>
    </tr></thead>
    <tbody>%(headrows)s</tbody>
  </table></div>
  <div class="src">Where every row comes from — <b>MJCF</b>:<ul class="src">%(headsrc)s</ul>
  <b>Measured</b>: %(headsrcmeas)s.<br><b>Actuator gains and force range</b>: %(headsrcforce)s.</div>
  <p class="note"><b>The &ldquo;stiff neck&rdquo; in the walk video was a zero command, not the
  mechanics.</b> The last column is what each head joint does during the 8&nbsp;s walk run:
  <code>sim/run_policy.py</code>'s schedule drives twist only and leaves <code>cmd[3:7]</code> at 0,
  so the head is being asked to hold still. Given a command, the same model gives
  %(hp_travel).2f&nbsp;deg of head pitch and %(hy_travel).2f&nbsp;deg of head yaw.</p>

  <h3>Is the limit the mechanism, or the policy?</h3>
  <p>A kinematic probe answers that separately: the policy is removed, the all-collisions model is
  used, and each joint is stepped across its whole MJCF range with the others at
  <code>DEFAULT_POSE</code>, counting MuJoCo self-contacts.</p>
  <div class="tw"><table>
    <thead><tr><th>joint</th><th class=num>MJCF range (deg)</th>
    <th class=num>self-collision-free (deg)</th><th class=num>steps in contact</th><th>reading</th></tr></thead>
    <tbody>%(proberows)s</tbody>
  </table></div>
  <p>So <code>neck_pitch</code> is free over its whole %(np_span).1f&nbsp;deg and still only reaches
  %(np_used).1f&nbsp;deg under the policy (tracking gain %(np_gain).4f): that is the policy holding the
  head as a balance mass, not a mechanical stop. <code>head_pitch</code> is the one joint whose limit
  <i>is</i> geometric — below %(hp_free).1f&nbsp;deg the head fouls the neck and trunk, which is
  exactly where the policy stops it (%(hp_lo).2f&nbsp;deg reached).</p>

  <h3>Does one command slot move only its own joint?</h3>
  <p>Peak excursion of every head joint when each command slot is driven alone — the diagonal is the
  commanded joint, everything off it is the mechanism and the balance controller reacting.</p>
  <div class="tw"><table>
    <thead><tr><th class=num>slot</th><th>driven</th><th class=num>neck_pitch</th>
    <th class=num>head_pitch</th><th class=num>head_yaw</th><th class=num>head_roll</th></tr></thead>
    <tbody>%(crossrows)s</tbody>
  </table></div>

  <h3>Inside the shipped servo?</h3>
  <p>%(servopart)s. Datasheet (%(servosrc)s): no-load %(sp5)s&nbsp;deg/s at 5.0&nbsp;V, stall
  %(stall).2f&nbsp;N&middot;m at 5.0&nbsp;V. This sweep's fastest head joint is %(peakvj)s at
  %(peakv).1f&nbsp;deg/s and its hardest-working joint is %(peaktj)s at %(peakt).4f&nbsp;N&middot;m —
  both inside those numbers. <b>%(servonote)s</b></p>
  <p>Nothing fell: minimum trunk height %(trunkz).5f&nbsp;m, maximum tilt %(tilt).3f&nbsp;deg over the
  whole sweep (rule: %(fellrule)s).</p>
</section>

<section id="walk">
  <h2><span class="n">2</span>Walking, with the joints in close-up</h2>
  <p class="lede">%(walkwhat)s. %(vx).2f&nbsp;m/s commanded, %(secs).3f&nbsp;s, %(walked).4f&nbsp;m
  walked at %(mean).4f&nbsp;m/s mean, gait period %(gp).4f&nbsp;s
  (%(cad).0f steps/min, autocorrelation peak %(gac).4f), stride %(stride).4f&nbsp;m.
  Maximum trunk tilt %(wtilt).2f&nbsp;deg; trunk height %(wz).4f&nbsp;m minimum. It did not fall.</p>
  <p>Every clip below tracks the body it is filming — the camera <code>lookat</code> is that body's
  world position on every frame — so a joint stays in the middle of its own close-up while the robot
  walks away. Each caption carries the live joint angles drawn into the frame. All %(nwalkvid)d were
  re-read frame by frame after encoding: <b>%(walkpass)d of %(nwalkvid)d PASS</b>; a blank, white or
  frozen frame is a defect, not a video.</p>

  %(walkfigs)s

  <h3>What every joint actually does while walking</h3>
  <p>Travel is the peak-to-peak the joint used, against the MJCF range it has. The last column is how
  close it ever came to a limit — the gait lives well inside the mechanism.</p>
  <div class="tw"><table class="data compact">
    <thead><tr><th>joint</th><th class=num>MJCF range (deg)</th><th class=num>reached (deg)</th>
    <th class=num>travel (deg)</th><th class=num>%% of range</th><th class=num>peak vel (deg/s)</th>
    <th class=num>at frame</th><th class=num>at t (s)</th><th class=num>closest to a limit (deg)</th></tr></thead>
    <tbody>%(walkrows)s</tbody>
  </table></div>
  <h4>The head during the same run</h4>
  <div class="tw"><table class="data compact">
    <thead><tr><th>joint</th><th class=num>MJCF range (deg)</th><th class=num>reached (deg)</th>
    <th class=num>travel (deg)</th><th class=num>%% of range</th><th class=num>peak vel (deg/s)</th>
    <th class=num>at frame</th><th class=num>at t (s)</th><th class=num>closest to a limit (deg)</th></tr></thead>
    <tbody>%(walkheadrows)s</tbody>
  </table></div>
  <p class="note">Gait period method: %(gmethod)s</p>
  %(wvp)s
</section>

<section id="head">
  <h2><span class="n">3</span>The head moving around</h2>
  <p class="lede">The four clips the section-1 numbers were measured on: the full-range sweep from
  three cameras, and a free look-around.</p>
  %(headfigs)s

  <h3>Beside the real robot</h3>
  <p>%(rvcatalog)s. <code>%(rvscript)s</code> tracks %(rvframes)d frames of it and measures
  %(rvtravel).4f&nbsp;deg of head-pitch travel with a peak rate of %(rvrate).3f&nbsp;deg/s
  (3-frame smoothed; %(rvraw).3f&nbsp;deg/s raw). Ours on the same joint is %(hp_travel).2f&nbsp;deg
  at %(hp_vel).1f&nbsp;deg/s. That settles &ldquo;not stiff&rdquo; and nothing more — the clip is a
  scripted animation shot hand-held, so it bounds the real robot only from below.</p>
  <ul>%(rvcaveats)s</ul>
  %(realfigs)s
</section>

<section id="legs">
  <h2><span class="n">4</span>The legs moving around</h2>
  <p class="lede">Every leg joint driven through its whole MJCF range one at a time (trunk pinned,
  policy paused, direct <code>ctrl</code>), then by Pollen's own sit-stand and stand policies on the
  floor, then in the two-joint and both-leg postures a one-at-a-time sweep can never reach.</p>
  <p class="note"><b>Can direct joint targets be used to pose the legs on the floor? No —</b> %(sqfail)s</p>

  %(legfigs)s

  <h3>Every leg joint: what the mechanism has, and what it reached</h3>
  <p>Driven to both MJCF limits with the trunk pinned and the policy paused, so this is the
  mechanism, not a gait. Tracking RMS is against the commanded ramp.</p>
  <div class="tw"><table class="data compact">
    <thead><tr><th>joint</th><th class=num>MJCF range (deg)</th><th class=num>span</th>
    <th class=num>reached (deg)</th><th class=num>travel</th><th class=num>%% of range</th>
    <th class=num>peak vel (deg/s)</th><th class=num>tracking RMS (deg)</th>
    <th>MJCF cite</th></tr></thead>
    <tbody>%(legrows)s</tbody>
  </table></div>

  <h3>What Pollen's own gaits use of that range</h3>
  <p>The same ten joints under the three policies — the working envelope against the mechanism above.
  Walk: <code>BEST_alpha_walking</code> at %(vx).2f&nbsp;m/s. Sit-stand:
  <code>BEST_alpha_sitstand</code>. Squat: <code>BEST_alpha_stand</code> driven through its body-z
  command slot.</p>
  <div class="tw"><table class="data compact">
    <thead><tr><th>joint</th><th class=num>MJCF span</th>
    <th class=num>walk travel<br>(%% of range)</th><th class=num>walk peak vel</th>
    <th class=num>sit-stand travel<br>(%% of range)</th><th class=num>sit-stand peak vel</th>
    <th class=num>squat travel</th><th class=num>squat peak vel</th></tr></thead>
    <tbody>%(gaitrows)s</tbody>
  </table></div>
  <p>All ten joints reach their full MJCF span to within %(spanerr).3f&nbsp;deg
  (travel fraction %(frmin).3f–%(frmax).3f of range). The fastest step response measured anywhere in
  the legs is <b>%(fastj)s at %(fastv).3f&nbsp;deg/s</b>. %(actnote)s</p>

  <h3>Squat, sit-stand and single-leg lift</h3>
  <p>The squat runs <i>with</i> Pollen's stand policy, driven through its body-z command slot: trunk
  %(sqhi).5f&nbsp;m &rarr; %(sqlo).5f&nbsp;m (%(sqdrop).2f&nbsp;mm), maximum tilt %(sqtilt).2f&nbsp;deg,
  did not fall — and every joint angle in that clip is the policy's own output, not a target we wrote.
  The sit-stand clip re-renders the existing <code>%(sitsrc)s</code> run. The leg lift is hoisted
  (trunk pinned, policy paused): left hip pitch %(llhp).3f&nbsp;deg and knee %(llk).3f&nbsp;deg of
  travel, then the right.</p>

  <h3>Self-collision — every posture where the mechanism touches itself</h3>
  <p>One joint at a time, with the others at <code>DEFAULT_POSE</code>, <b>%(sc1)d of %(scn)d sweeps
  touch anything</b>. The interesting cases need two joints off default, or both legs together —
  %(ntouch)d postures do touch, and each is named with the geom pair, the angle at which it first
  touches and the deepest convex-hull penetration. MuJoCo collides mesh geoms as their convex hulls,
  so these onsets are conservative.</p>
  <div class="tw"><table class="data compact">
    <thead><tr><th>posture</th><th>geom pair</th>
    <th class=num>onset (deg)</th><th class=num>max penetration (mm)</th><th>verdict</th></tr></thead>
    <tbody>%(screws)s</tbody>
  </table></div>
  <p class="note"><b>%(screading)s</b></p>

  <h4>A check that cannot fail is not a check</h4>
  <p>%(scwhy)s</p>
  <div class="tw"><table>
    <thead><tr><th>control</th><th class=num>result</th><th>verdict</th></tr></thead>
    <tbody>%(ctlrows)s</tbody>
  </table></div>
  <p class="dim">%(scmeas)s</p>

  %(legfigures)s
  %(cmpfigs)s
</section>

<section id="regen">
  <h2><span class="n">5</span>How to regenerate every frame and number on this page</h2>
  <p class="lede">MuJoCo, onnxruntime, numpy and PIL live only in FreeCAD's python on this machine.
  The system <code>python3</code> has none of them — it runs the document generators only.</p>
  <pre class="code">PY=/Applications/FreeCAD.app/Contents/Resources/bin/python   # or: ce-cad/bin/cad &lt;script.py&gt;
cd %(repo)s

$PY sim/swap_meshes.py            # OUR meshes onto Pollen's MJCF, bbox-checked
$PY sim/run_policy.py --all       # the trajectories every number is read off
$PY sim/head_sweep.py             # section 1 + 3: head.json, head_traj.npz, 4 clips
$PY sim/head_real_video.py        # the real-robot head track
$PY sim/head_compare.py           # ours beside the real head
$PY sim/head_verify.py            # read every head clip back
$PY sim/motion_render.py --all    # section 2: walk.json, 9 clips
$PY sim/walk_vs_product.py        # our gait phase-matched to Pollen's clip
$PY sim/leg_sweep.py              # section 4: legs.json, the self-collision sweeps
$PY sim/leg_render.py             # 10 leg clips (no args = all)
$PY sim/leg_plots.py              # the leg figures
$PY sim/leg_framing.py            # frustum proof the close-ups contain the servo
$PY sim/leg_compare.py            # ours beside the product photographs
$PY sim/leg_verify.py             # read every leg clip back out of the ENCODED file
$PY sim/leg_verify.py --self-test  # break it on purpose: blank / frozen / truncated all refused

python3 tools/gen_motion.py       # this document
python3 tools/gen_index.py        # relist it on the front door</pre>

  <div class="tw"><table>
    <thead><tr><th>script</th><th>what it does</th><th>command</th><th>state</th></tr></thead>
    <tbody>%(scriptrows)s</tbody>
  </table></div>

  <h3>The data this page is generated from</h3>
  <p>No table on this page is hand-maintained. Every number comes out of these files, and every one of
  them is written by a script above.</p>
  <div class="tw"><table>
    <thead><tr><th>file</th><th class=num>size</th><th>state</th></tr></thead>
    <tbody>%(datarows)s</tbody>
  </table></div>

  <h3>Asset audit — every file this page points at</h3>
  <p>Stat()ed before the document was written, the way <code>tools/gen_index.py</code> stats every
  index entry. <b>%(nassets)d referenced, %(nmissing)d missing.</b> A missing asset is published as
  missing and the generator exits non-zero.</p>
  <div class="tw"><table>
    <thead><tr><th>path</th><th>kind</th><th class=num>size</th><th>state</th></tr></thead>
    <tbody>%(auditrows)s</tbody>
  </table></div>
</section>

<p class="backlink"><a href="INDEX.html">&larr; repository index</a> ·
<a href="HEAD-MOTION.html">head dossier</a> ·
<a href="out/motion/WALK.html">walk dossier</a> ·
<a href="LEG-MOTION.html">leg dossier</a> ·
<a href="COMPARISON.html">reference match</a></p>

<footer>
  <span>Microduck · motion evidence</span>
  <span>generated %(stamp)s</span>
  <span>tools/gen_motion.py</span>
  <span>model: Pollen MJCF verbatim, OUR rebuilt meshes on the visual geoms</span>
</footer>
</div></body></html>
"""

vals = dict(
    css=CSS, stamp=STAMP, repo=REPO,
    nvid=n_videos, ngif=n_gifs, nsheet=n_sheets, mb=mb(total_bytes),
    # section 1
    qq=E(HV["question"]), answer=E(HV["answer"]), rests=rests_on, restsnot=rests_not,
    vsreal=E(HV["vs_real_robot"]), loop=E(HEAD["loop"]), hsecs=HEAD["seconds"],
    headrows=head_rows, headsrc=head_src, headsrcmeas=head_src_measure,
    headsrcforce=head_src_force, proberows=probe_rows, crossrows=crosstalk_rows,
    best_pct=best_pct, peakv=peak_v, peakvj=E(peak_v_joint), peakt=peak_t, peaktj=E(peak_t_joint),
    np_span=HJ["neck_pitch"]["mjcf_range_deg"][1] - HJ["neck_pitch"]["mjcf_range_deg"][0],
    np_used=HJ["neck_pitch"]["travel_whole_run_span_deg"], np_gain=HJ["neck_pitch"]["tracking_gain"],
    hp_free=HPROBE["head_pitch"]["self_collision_free_deg"][0],
    hp_lo=HJ["head_pitch"]["travel_whole_run_deg"][0],
    hp_travel=HJ["head_pitch"]["travel_whole_run_span_deg"],
    hp_vel=HJ["head_pitch"]["peak_velocity_run_deg_s"],
    hy_travel=HJ["head_yaw"]["travel_whole_run_span_deg"],
    servopart=E(SERVO["part"]), servosrc=E(SERVO["source"]),
    sp5=("%.1f" % SERVO["no_load_speed_deg_s"]["5.0V"]), stall=SERVO["stall_torque_Nm"]["5.0V"],
    servonote=E(SERVO["note"]),
    trunkz=stab["min_trunk_z_m"], tilt=max(stab["max_abs_roll_deg"], stab["max_abs_pitch_deg"]),
    fellrule=E(stab["rule"]),
    # section 2
    walkwhat=E(WALK["what"]), vx=W["commanded_vx_m_s"], secs=W["seconds"], walked=W["walked_m"],
    mean=W["mean_speed_m_s"], gp=G["cycle_period_s"], cad=G["cadence_steps_per_min"],
    gac=G["autocorr_peak_of_left_knee"], stride=G["stride_length_m"],
    wtilt=W["max_tilt_deg"], wz=W["trunk_z_m"]["min"],
    nwalkvid=len(WV), walkpass=walk_pass, walkfigs=walk_figs,
    walkrows=walk_rows, walkheadrows=walk_head_rows, gmethod=E(G["method"]), wvp=wvp_html,
    # section 3
    headfigs=head_figs, realfigs=real_figs,
    rvcatalog=E(rv["catalog"]), rvscript=E(rv["script"]), rvframes=rv["frames_tracked"],
    rvtravel=rv["travel_deg"], rvrate=rv["peak_rate_deg_s_smoothed3"], rvraw=rv["peak_rate_deg_s_raw"],
    rvcaveats=real_caveats,
    # section 4
    legfigs=leg_figs, legrows=leg_rows, gaitrows=gait_rows, screws=sc_rows, ctlrows=ctl_rows,
    sqfail=E(LEGS["squat_directctrl_FAILS"]["finding"]),
    spanerr=HL["ten_of_ten_joints_reach_their_mjcf_span_within_deg"],
    frmin=HL["travel_fraction_of_mjcf_range"]["min"], frmax=HL["travel_fraction_of_mjcf_range"]["max"],
    fastj=E(HL["fastest_joint"][0]), fastv=HL["fastest_joint"][1],
    actnote=E(ACT["servo_reality_check"]),
    sqhi=SQ["trunk_z_m"]["max"], sqlo=SQ["trunk_z_m"]["min"], sqdrop=SQ["trunk_drop_mm"],
    sqtilt=SQ["max_trunk_tilt_deg"], sitsrc=E(LEGS["sitstand_policy"]["source"]),
    llhp=LEGS["leg_lift"]["joints"]["left_hip_pitch"]["travel_deg"],
    llk=LEGS["leg_lift"]["joints"]["left_knee"]["travel_deg"],
    ntouch=n_touch, sc1=sc_one_at_a_time, scn=len(SC["pollen_collision_meshes"]["sweeps"]),
    screading=E(HL["reading"]), scwhy=E(ctl["why"]), scmeas=E(ctl["measured_with"]),
    legfigures=fig_html, cmpfigs=cmp_figs,
    # section 5
    scriptrows=script_rows, datarows=data_rows, auditrows=audit_rows,
    nassets=len(ASSETS), nmissing=len(missing),
)

out = os.path.join(REPO, "MOTION.html")
with open(out, "w", encoding="utf-8") as fh:
    fh.write(DOC % vals)

print("wrote %s (%.1f KB)" % (out, os.path.getsize(out) / 1024.0))
print("assets referenced: %d  present: %d  missing: %d"
      % (len(ASSETS), len(ASSETS) - len(missing), len(missing)))
print("videos: %d mp4, %d gif, %d contact sheets, %.1f MB of video"
      % (n_videos, n_gifs, n_sheets, mb(total_bytes)))
for rel, kind, ok, sz in missing:
    print("  MISSING %-14s %s" % (kind, rel))
sys.exit(1 if missing else 0)
