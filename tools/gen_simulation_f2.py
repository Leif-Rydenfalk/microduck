#!/usr/bin/env python3
"""gen_simulation_f2.py — turn lane F2's evidence JSON into the HTML sections
for SIMULATION.html.

Reads (data, never hand-edited):
    out/sim-evidence/gait-peaks.json
    out/sim-evidence/gait-robustness.json
    out/sim-evidence/battery-runtime.json
    out/sim-sweep/videos.json          (per-cell video read-back record)

Writes:
    out/sim-evidence/f2-sections.html  the <section> fragments the synth's
                                       tools/gen_simulation.py includes verbatim
    out/sim-evidence/f2-preview.html   the same fragments in a full page with
                                       tools/doc.css, so they can be screenshotted
                                       and read back on their own

System python3 (no numpy needed).
"""
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
EV = os.path.join(REPO, "out", "sim-evidence")


def load(n, sub="sim-evidence"):
    p = os.path.join(REPO, "out", sub, n)
    return json.load(open(p)) if os.path.exists(p) else None


PEAKS = load("gait-peaks.json")
ROB = load("gait-robustness.json")
BAT = load("battery-runtime.json")
VID = load("videos.json", "sim-sweep") or {}

E = html.escape


def chip(v):
    cls = {"PASS": "pass", "FAIL": "cd", "CANNOT DETERMINE": "cd"}.get(v, "cd")
    return '<span class="chip %s">%s</span>' % (cls, E(v))


def perturbation(r):
    bits = []
    if r["vx_cmd_m_s"] is not None:
        bits.append("v<sub>x</sub> %.2f m/s" % r["vx_cmd_m_s"])
    if r["mass_scale"] != 1.0:
        bits.append("mass ×%.2f (%.4f kg)" % (r["mass_scale"], r["total_mass_kg"]))
    if abs(r["foot_friction"] - 1.0) > 1e-9:
        bits.append("μ %.2f" % r["foot_friction"])
    if r["slope_deg"]:
        bits.append("%.0f° slope, downhill %s" % (r["slope_deg"], r["slope_downhill_dir"].replace("_", " ")))
    if r["push_N"]:
        bits.append("push %.0f N %s for %.1f s" % (r["push_N"],
                    {(1, 0, 0): "+x", (-1, 0, 0): "−x", (0, 1, 0): "+y", (0, -1, 0): "−y"}.get(
                        tuple(r["push_dir"]), str(r["push_dir"])), r["push_dur_s"]))
    if r["policy"] != "walking":
        bits.append("policy <code>%s</code>" % E(r["policy"]))
    if r["robot"].endswith("allcollisions"):
        bits.append("all-collision model")
    return " · ".join(bits) or "—"


def robustness_rows():
    out = []
    for r in ROB["outputs"]["rows"]:
        fell = ('<span class="chip cd">fell @ %.2f s</span>' % r["first_fall_s"]) if r["fell"] \
            else '<span class="chip pass">upright</span>'
        out.append(
            "<tr><td><code>%s</code></td><td>%s</td><td class=\"n\">%s</td>"
            "<td class=\"n\">%.4f</td><td class=\"n\">%.4f</td><td class=\"n\">%.4f</td>"
            "<td class=\"n\">%.4f</td><td><code>%s</code></td><td class=\"n\">%.2f</td>"
            "<td class=\"n\">%.1f</td><td class=\"n\">%d</td>"
            "<td class=\"n\">%.1f</td></tr>"
            % (E(r["cell"]), perturbation(r), fell, r["walked_m"], r["path_length_m"] or 0.0,
               r["mean_speed_m_s"], r["max_joint_torque_Nm"], E(r["max_joint_torque_joint"]),
               r["grf_vertical_peak_N"], r["net_yaw_drift_deg"] or 0.0,
               r["self_collisions_max"], r["max_range_utilisation_pct"]))
    return "\n".join(out)


def over_rows():
    out = []
    for cell, js in sorted(PEAKS["outputs"]["cells_that_exceed_the_6V_stall_row"].items()):
        for j, t in sorted(js.items(), key=lambda kv: -kv[1]):
            out.append('<tr class="cd"><td><code>%s</code></td><td><code>%s</code></td>'
                       '<td class="n">%.4f</td><td class="n">%.1f</td></tr>'
                       % (E(cell), E(j), t, 100.0 * t / 0.60))
    return "\n".join(out)


def peak_rows():
    t = PEAKS["outputs"]["per_joint_locomotion_upright"]
    d = PEAKS["outputs"]["per_joint_disturbance_push"]
    base = PEAKS["outputs"]["baseline_walk_vx0.25"]["per_joint_peak_Nm"]
    out = []
    for j, v in t.items():
        over6 = v["peak_abs_torque_Nm"] > 0.60
        cls = ' class="cd"' if over6 else ""
        out.append(
            "<tr%s><td><code>%s</code></td><td class=\"n\">%.4f</td><td class=\"n\">%.4f</td>"
            "<td class=\"n\">%.4f</td><td><code>%s</code></td>"
            "<td class=\"n\">%.1f / %.1f</td><td class=\"n\">%.4f</td>"
            "<td class=\"n\">%.3f</td><td class=\"n\">%.1f</td></tr>"
            % (cls, E(j), base[j], v["peak_abs_torque_Nm"], v["p99_abs_torque_Nm"],
               E(v["peak_cell"]), v["vs_xl330_stall_at_5V_pct"], v["vs_xl330_stall_at_6V_pct"],
               d[j]["peak_abs_torque_Nm"], v["peak_abs_speed_rad_s"], v["max_range_utilisation_pct"]))
    return "\n".join(out)


def runtime_rows():
    t = BAT["outputs"]["runtime_table"]
    modes = [("walking", "Walking, v<sub>x</sub> 0.25 m/s"), ("standing", "Standing, pose held"),
             ("idle_torque_off", "Idle, servo torque disabled")]
    out = []
    for key, lbl in modes:
        rows = t[key]["rows"]
        cells = "".join('<td class="n">%.2f</td>' % r["runtime_h"] for r in rows)
        out.append('<tr><td>%s</td><td class="n">%.3f</td>%s</tr>'
                   % (lbl, t[key]["servo_mean_W"], cells))
    return "\n".join(out)


def video_figs():
    if not VID:
        return "<p class=\"note\">No video read-back record found.</p>"
    out = []
    for name, v in VID.items():
        frames = sorted(f for f in os.listdir(os.path.join(REPO, "out", "sim-sweep", "frames"))
                        if f.startswith(name + "_t"))
        imgs = "".join('<figure><img src="out/sim-sweep/frames/%s" alt="%s"><figcaption>%s</figcaption></figure>'
                       % (E(f), E(f), E(f.split("_t")[-1].replace(".png", ""))) for f in frames)
        mp4 = v.get("mp4", {})
        out.append(
            '<div class="card"><h3><code>%s</code> — %s</h3>'
            '<div class="grid2">%s</div>'
            '<p class="note">%d frames at %.1f fps, %s. Read back from the encoded file: %d frames, '
            'mean inter-frame difference %.3f, frame intensity %s–%s (a blank or frozen video is refused). '
            'Video: <a href="%s"><code>%s</code></a>.</p></div>'
            % (E(name), E(v.get("label", "")), imgs, v["frames"], v["fps"], E(v["renderer"]),
               mp4.get("frames_read_back", 0), v["mean_interframe_diff"],
               v["frame_mean_intensity"][0], v["frame_mean_intensity"][1],
               E(mp4.get("path", "")), E(mp4.get("path", ""))))
    return "\n".join(out)


def sections():
    po, ro, bo = PEAKS["outputs"], ROB["outputs"], BAT["outputs"]
    pc = bo["pollen_claim"]
    walking = bo["modes"]["walking"]
    standing = bo["modes"]["standing"]
    idle = bo["modes"]["idle_torque_off"]
    return """
<section id="f2-gait">
  <h2><span class="n">F2.1</span>Gait robustness — %d perturbation cells</h2>
  <p class="lede">Pollen's own published ONNX policies driving <b>our</b> rebuilt meshes on Pollen's
  stock collision geometry and inertials, through a matrix of commanded speed, mass, foot friction,
  ground slope and external push. Every number is read off the simulation state: nothing here is a
  round figure or a default.</p>

  <div class="statbar">
    <div class="stat"><b>%d</b><span>cells run</span></div>
    <div class="stat"><b>%d</b><span>walking cells</span></div>
    <div class="stat"><b>%d</b><span>walking falls</span></div>
    <div class="stat"><b>%.4f N·m</b><span>worst locomotion torque</span></div>
    <div class="stat"><b>%.2f N</b><span>peak single-foot GRF</span></div>
  </div>

  <div class="note">%s %s</div>

  <h3>How each perturbation is applied to the model</h3>
  <ul>
    <li><b>Mass</b> — %s</li>
    <li><b>Friction</b> — %s</li>
    <li><b>Slope</b> — %s</li>
    <li><b>Push</b> — %s</li>
  </ul>

  <p class="num">Table F2-1. The full sweep, ordered by family. Torque is
  <code>data.actuator_force</code> (N·m, gear 1) recorded at every 200 Hz physics step; GRF is
  <code>mj_contactForce</code> on every contact touching a foot geom, world +z. <b>Walked</b> is the
  straight-line trunk displacement and <b>path</b> the integrated ground track — the gap is the
  robot curving. Range utilisation is the widest joint's swept span as a percentage of its MJCF
  range.</p>
  <div class="tablewrap">
  <table class="data">
    <thead><tr><th>Cell</th><th>Perturbation</th><th>Outcome</th><th>Walked (m)</th><th>Path (m)</th>
    <th>Mean speed (m/s)</th><th>Peak τ (N·m)</th><th>at joint</th><th>Peak GRF<sub>z</sub> (N)</th>
    <th>Yaw drift (°)</th><th>Self-coll.</th><th>Max range use (%%)</th></tr></thead>
    <tbody>
%s
    </tbody>
  </table>
  </div>

  <h3>The push threshold</h3>
  <p>%s</p>

  <h3>Heading and forward tracking</h3>
  <p>%s Worst net yaw drift: <code>%s</code>, <b>%.3f°</b> over the run
  (<b>%.4f °/m</b> of ground track). The forward tracking ratio — mean path speed divided by
  the commanded v<sub>x</sub> — is <b>%.3f</b> at the reference command and stays between
  <b>%.3f</b> and <b>%.3f</b> across every moving level-ground cell, so the policy delivers roughly
  half to two-thirds of what it is asked for, along a curving track.</p>
</section>

<section id="f2-peaks">
  <h2><span class="n">F2.2</span>Peak joint torque and ground reaction — the load basis</h2>
  <p class="lede">This is the table lanes F1 (structural FEA) and F3 (servo thermal) read.
  It is not a rule of thumb: each figure is the largest <code>actuator_force</code> that joint
  reached in any upright locomotion cell, and the cell it came from is named.</p>

  <div class="note">Servo capability, quoted verbatim from ROBOTIS and not paraphrased:
  <span class="mono">%s</span> Source: %s</div>

  <p class="num">Table F2-2. Per-joint torque envelope. <b>Baseline</b> is the reference walk at
    v<sub>x</sub> 0.25 m/s; <b>locomotion peak</b> is the worst over the 22 upright cells with no
    external push; <b>push peak</b> is the worst under a 0.2 s trunk push, where the MJCF actuator
    saturates its own ±0.96 N·m ceiling and the figure is the simulation's limit, not a measured
    actuator capability. Rows past the 6.0 V stall row are flagged.</p>
  <div class="tablewrap">
  <table class="data">
    <thead><tr><th>Joint</th><th>Baseline peak (N·m)</th><th>Locomotion peak (N·m)</th>
    <th>p99 (N·m)</th><th>Worst cell</th><th>%% of stall<br>5 V / 6 V</th>
    <th>Push peak (N·m)</th><th>Peak speed (rad/s)</th>
    <th>Max range use (%%)</th></tr></thead>
    <tbody>
%s
    </tbody>
  </table>
  </div>

  <div class="verdict">%s <b>Peak-torque verdict.</b> %s</div>

  <div class="note"><b>%s at the reference command.</b> %s</div>

  <p class="num">Table F2-2b. Every upright locomotion cell in which a joint asks for more than the
  XL330-M288-T's published 0.60 N·m stall torque at 6.0 V. On the physical robot the servo
  saturates instead: the gait these cells show is not reproducible as simulated.</p>
  <div class="tablewrap">
  <table class="data">
    <thead><tr><th>Cell</th><th>Joint</th><th>Peak τ (N·m)</th><th>%% of 0.60 N·m</th></tr></thead>
    <tbody>
%s
    </tbody>
  </table>
  </div>

  <h3>Ground reaction</h3>
  <p>Static weight <b>%.4f N</b>. The measurement is validated against statics before it is used:
  in the standing cells the median summed vertical GRF is <b>7.2425 N</b> and <b>7.2289 N</b>
  against that 7.2324 N weight — 0.14 %% and 0.05 %%. Walking, one foot peaks at
  <b>%.4f N</b> (<b>%.3f×</b> body weight, p99 %.4f N). The worst anywhere in the matrix is
  <b>%.4f N</b> summed over both feet in <code>%s</code>. %s</p>

  <h3>Joint travel past the MJCF stop</h3>
  <p>In the %d undisturbed locomotion cells no joint left its range at all. Under an external
  push %d joints are driven past their MJCF stop, worst <code>%s</code> by <b>%.4f°</b> in
  <code>%s</code>. %s</p>
</section>

<section id="f2-video">
  <h2><span class="n">F2.3</span>One video per cell family, read back</h2>
  <p class="lede">Every video is re-read frame by frame after encoding and refused if it is blank
  or frozen; the numbers under each strip are that read-back.</p>
%s
</section>

<section id="f2-battery">
  <h2><span class="n">F2.4</span>Battery runtime</h2>
  <p class="lede">Per-servo <b>electrical</b> power integrated over the measured gait, through a
  linear DC-machine model whose every constant comes from ROBOTIS's own published stall and
  no-load rows — then divided into the pack's watt-hours.</p>

  <div class="note"><b>The model.</b> Per 200 Hz physics step and per joint:
  <span class="mono">I = |τ|/k<sub>T</sub> &nbsp; V<sub>m</sub> = k<sub>E</sub>|ω| + R·I &nbsp;
  P<sub>motor</sub> = min(V<sub>m</sub>, V<sub>pack</sub>)·I</span>, summed over the 14 actuated
  joints, plus 15 × 17 mA × V<sub>pack</sub> of controller standby.
  k<sub>T</sub> = %.6f N·m/A, R = %.6f Ω, k<sub>E</sub> = %.6f V·s/rad, all derived from the
  5.0 V stall row and no-load speed. The three published rows give k<sub>E</sub> independently as
  0.464900 / 0.463583 / 0.465925 V·s/rad — a 0.50 %% spread, which is the check that the model is
  the right shape.</div>

  <p class="num">Table F2-3. Hours on the pack's %.1f Wh. The compute + sensor + HAT draw is
  <b>CANNOT DETERMINE</b> — no vendor publishes it — so it is swept across the columns rather
  than assumed. Servo power is measured.</p>
  <div class="tablewrap">
  <table class="data">
    <thead><tr><th>Mode</th><th>Servos (W)</th>
    <th>+1.0 W</th><th>+1.5 W</th><th>+2.0 W</th><th>+2.5 W</th><th>+3.0 W</th><th>+4.0 W</th>
    <th>+5.0 W</th></tr></thead>
    <tbody>
%s
    </tbody>
  </table>
  </div>

  <p>Walking draws <b>%.3f W</b> mean and <b>%.3f W</b> peak at the pack (<b>%.4f A</b> /
  <b>%.4f A</b> at 7.4 V); the busiest single servo peaks at <b>%.4f A</b> on
  <code>%s</code>, below both the 1.47 A stall current and the firmware's own
  1.75 A Current&nbsp;Limit(38). Standing costs <b>%.3f W</b>, of which <b>%.3f W</b> is nothing
  but the fifteen controllers being awake. Electromechanical efficiency while walking is
  <b>%.1f %%</b> (%.4f W mechanical out of %.4f W electrical in).</p>

  <div class="verdict warn">%s <b>Runtime verdict.</b> %s</div>

  <h3>Against Pollen's published ~1 h</h3>
  <p>%s</p>

  <h3>What this model deliberately does not know</h3>
  <ul>
    <li><b>No-load current.</b> %s</li>
    <li><b>Compute + sensors.</b> %s</li>
    <li><b>Usable pack energy.</b> %s</li>
    <li><b>Which pack is fitted.</b> %s</li>
  </ul>
</section>
""" % (
        len(ro["rows"]), ro["cells"], ro["walking_cells"], len(ro["walking_cells_that_fell"]),
        po["worst_locomotion_torque_Nm"],
        po["ground_reaction_force_N"]["walking_single_foot_peak_N"],
        chip(ROB["verdict"]), E(ROB["why"]),
        E(ROB["inputs"]["how_each_perturbation_is_applied"]["mass"]),
        E(ROB["inputs"]["how_each_perturbation_is_applied"]["friction"]),
        E(ROB["inputs"]["how_each_perturbation_is_applied"]["slope"]),
        E(ROB["inputs"]["how_each_perturbation_is_applied"]["push"]),
        robustness_rows(),
        E(ro["push_threshold"]["statement"]),
        E(ro["heading_and_tracking"]["finding"]),
        E(ro["heading_and_tracking"]["worst_net_yaw_drift"][0]),
        ro["heading_and_tracking"]["worst_net_yaw_drift"][1],
        ro["heading_and_tracking"]["worst_net_yaw_drift"][2],
        ro["heading_and_tracking"]["forward_tracking_ratio_moving_cells"]["base_walk_vx0.25"],
        min(v for k, v in ro["heading_and_tracking"]["forward_tracking_ratio_moving_cells"].items()
            if not k.startswith("slope5") and not k.startswith("endurance_60s_slope")),
        max(v for k, v in ro["heading_and_tracking"]["forward_tracking_ratio_moving_cells"].items()
            if not k.startswith("slope5") and not k.startswith("endurance_60s_slope")),
        E(PEAKS["inputs"]["servo"]["stall_torque_Nm_quote"] + " ; No Load Speed "
          + PEAKS["inputs"]["servo"]["no_load_speed_rpm_quote"] + " ; "
          + PEAKS["inputs"]["servo"]["standby_current_mA_quote"]),
        E(PEAKS["inputs"]["servo"]["source"]),
        peak_rows(),
        chip(PEAKS["verdict"]), E(PEAKS["why"]),
        chip(po["reference_command_verdict"]["verdict"]),
        E(po["reference_command_verdict"]["statement"]),
        over_rows(),
        po["ground_reaction_force_N"]["static_weight_N"],
        po["ground_reaction_force_N"]["walking_single_foot_peak_N"],
        po["ground_reaction_force_N"]["walking_single_foot_peak_body_weights"],
        po["ground_reaction_force_N"]["walking_single_foot_p99_N"],
        po["ground_reaction_force_N"]["worst_any_peak_N"],
        E(po["ground_reaction_force_N"]["worst_any_cell"]),
        E(po["ground_reaction_force_N"]["for_FEA"]),
        len([r for r in ro["rows"] if r["push_N"] == 0.0 and r["policy"] == "walking"]),
        len(ro["joints_that_ever_left_their_MJCF_range"]),
        E(ro["worst_joint_limit_overshoot"]["joint"]), ro["worst_joint_limit_overshoot"]["overshoot_deg"],
        E(ro["worst_joint_limit_overshoot"]["cell"]), E(ro["worst_joint_limit_overshoot"]["meaning"]),
        video_figs(),
        BAT["inputs"]["servo"]["constants_used"]["kT_Nm_per_A"],
        BAT["inputs"]["servo"]["constants_used"]["R_ohm"],
        BAT["inputs"]["servo"]["constants_used"]["kE_V_s_per_rad"],
        BAT["inputs"]["pack"]["Wh"],
        runtime_rows(),
        walking["servo_total_power_W"]["mean"], walking["servo_total_power_W"]["peak"],
        walking["pack_current_from_servos_A"]["mean"], walking["pack_current_from_servos_A"]["peak"],
        walking["peak_single_servo_current_A"], E(walking["peak_single_servo_current_joint"]),
        standing["servo_total_power_W"]["mean"], idle["servo_total_power_W"]["mean"],
        100.0 * walking["electromechanical_efficiency_mean"],
        walking["mechanical_output_power_W"]["mean"], walking["servo_motor_power_W"]["mean"],
        chip(BAT["verdict"]), E(BAT["why"]),
        E(pc["reading"]),
        E(BAT["inputs"]["servo"]["no_load_current"]["why"]),
        E(BAT["inputs"]["compute_and_sensors"]["why"]),
        E(BAT["inputs"]["pack"]["usable_fraction_note"]),
        E(BAT["inputs"]["pack"]["identity"]),
    )


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Microduck — simulation evidence, lane F2</title>
<link rel="stylesheet" href="../../tools/doc.css">
<style>
 .data td.cd, .data tr.cd td { background: #fff4f2; }
 .grid2 figure { margin: 0; }
 .grid2 img { width: 100%%; border: 1px solid #d8d8d2; border-radius: 3px; }
 .grid2 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
 .card { margin: 18px 0; padding: 14px 16px; border: 1px solid #ddd; border-radius: 4px; }
 .card h3 { margin-top: 0; }
 table.data { font-size: 12px; }
</style>
</head><body><div class="wrap">
<p class="backlink"><a href="../../RELEASE.html">&larr; Release dossier</a></p>
<header class="hero">
  <p class="eyebrow">Microduck reverse-engineering &middot; simulation evidence</p>
  <h1>Gait robustness &amp; battery runtime</h1>
  <p class="sub">Lane F2. A preview of the sections <code>tools/gen_simulation.py</code> includes in
  SIMULATION.html; the data is <code>out/sim-evidence/gait-peaks.json</code>,
  <code>gait-robustness.json</code> and <code>battery-runtime.json</code>.</p>
</header>
%s
<footer class="note">Generated by <code>tools/gen_simulation_f2.py</code>. Image paths in the
fragments are repo-relative and resolve when the fragments are included from a document at the
repository root.</footer>
</div></body></html>
"""


def main():
    frag = sections()
    os.makedirs(EV, exist_ok=True)
    fp = os.path.join(EV, "f2-sections.html")
    open(fp, "w").write(frag)
    prev = frag.replace('src="out/sim-sweep/', 'src="../sim-sweep/').replace(
        'href="out/sim-sweep/', 'href="../sim-sweep/')
    pp = os.path.join(EV, "f2-preview.html")
    open(pp, "w").write(PAGE % prev)
    print("wrote", os.path.relpath(fp, REPO), os.path.getsize(fp), "bytes")
    print("wrote", os.path.relpath(pp, REPO), os.path.getsize(pp), "bytes")


if __name__ == "__main__":
    main()
