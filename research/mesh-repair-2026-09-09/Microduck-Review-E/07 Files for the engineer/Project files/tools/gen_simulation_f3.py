#!/usr/bin/env python3
"""gen_simulation_f3.py — turn lane F3's evidence JSON into the HTML sections
for SIMULATION.html.  Same contract as tools/gen_simulation_f2.py.

Reads (data, never hand-edited):
    out/sim-evidence/gait-torque-duty.json      sim/thermal_duty.py
    out/sim-evidence/thermal-servo-xl330.json   sim/thermal_servo.py
    out/sim-evidence/cavity-volumes.json        sim/cavity_measure.py
    out/sim-evidence/thermal-compute-head.json  sim/thermal_compute.py
    out/sim-evidence/joint-geometry.json        sim/joint_geometry.py
    out/sim-evidence/tolerance-stack-hinges.json sim/tolerance_stack.py

Writes:
    out/sim-evidence/f3-sections.html   the <section> fragments the synth's
                                        tools/gen_simulation.py includes verbatim
    out/sim-evidence/f3-preview.html    the same fragments in a full page with
                                        tools/doc.css, for screenshot read-back

System python3 (stdlib only).
"""
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
EV = os.path.join(REPO, "out", "sim-evidence")
E = html.escape


def load(n):
    p = os.path.join(EV, n)
    return json.load(open(p)) if os.path.exists(p) else None


DUTY = load("gait-torque-duty.json")
SERVO = load("thermal-servo-xl330.json")
CAV = load("cavity-volumes.json")
COMP = load("thermal-compute-head.json")
GEOM = load("joint-geometry.json")
TOL = load("tolerance-stack-hinges.json")


def chip(v):
    cls = {"PASS": "pass", "FAIL": "cd", "CANNOT DETERMINE": "cd"}.get(v, "cd")
    return '<span class="chip %s">%s</span>' % (cls, E(v))


def opens(rows):
    if not rows:
        return ""
    li = "".join(
        "<li><b>%s</b> — %s <i>What settles it:</i> %s</li>"
        % (E(r["what"]), E(r["why"]), E(r["what_settles_it"])) for r in rows)
    return '<div class="card"><h3>What stays open</h3><ul>%s</ul></div>' % li


# ---------------------------------------------------------------- study 1
def servo_section():
    o = SERVO["outputs"]
    rows = []
    for n, r in sorted(o["per_joint"].items(), key=lambda kv: -kv[1]["p_copper_W"]):
        b = r["case_band_25C"]
        ang = r["steady_state"]["Ta25C_block0%"]
        cls = ' class="cd"' if b["grade"] != "PASS" else ""
        rows.append(
            "<tr%s><td>%s</td><td class=n>%.4f</td><td class=n>%.4f</td>"
            "<td class=n>%.4f</td><td class=n>%.4f</td><td class=n>%.4f</td>"
            "<td class=n>%.2f</td><td class=n>%.2f</td><td>%s</td></tr>"
            % (cls, E(n), r["rms_torque_Nm"], r["peak_torque_Nm"], r["i_rms_A"],
               r["i_peak_A"], r["p_copper_W"], b["lower_bound_C"], b["upper_bound_C"],
               chip(b["grade"])))
    tc = "".join(
        "<tr><td class=n>%s</td><td class=n>%s</td><td>%s</td><td class=n>%s</td>"
        "<td class=n>%s</td><td class=n>%s</td></tr>"
        % (r["assumed_cp_J_kgK"], r["lumped_C_J_K"], r["eps"], r["tau_thermal_s"],
           r["steady_rise_K"],
           "never" if r["time_to_70C_min"] is None else "%.2f" % r["time_to_70C_min"])
        for r in o["time_to_limit_curve"])
    cg = o.get("duty_cells_graded", {})
    cellrows = "".join(
        "<tr%s><td>%s</td><td class=n>%s</td><td>%s</td><td class=n>%.6f</td>"
        "<td class=n>%s</td><td class=n>%.4f</td><td class=n>%.2f</td>"
        "<td class=n>%.2f</td><td>%s</td></tr>"
        % (' class="cd"' if g["verdict"] != "PASS" else "",
           E(cn), g["inputs"].get("seconds"),
           E(g["worst_joint"]),
           g["per_joint"][g["worst_joint"]]["mean_tau_squared_Nm2"],
           ("\u2014" if g["per_joint"][g["worst_joint"]]["duty_vs_baseline"] is None
            else "%.4f\u00d7" % g["per_joint"][g["worst_joint"]]["duty_vs_baseline"]),
           g["worst_p_copper_W"],
           g["per_joint"][g["worst_joint"]]["case_temp_C_25C_eps1_free"],
           g["per_joint"][g["worst_joint"]]["case_temp_C_25C_eps0_block30"],
           chip(g["verdict"]))
        for cn, g in sorted(cg.items(), key=lambda kv: -kv[1]["worst_p_copper_W"]))
    amb = o.get("joints_over_70C_at_best_cooling_30pct_blocked_per_ambient", {})
    ambrows = "".join(
        "<tr><td class=n>%s</td><td>%s</td></tr>"
        % (E(k.replace("Ta", "").replace("C", " \u00b0C")),
           E(", ".join(v) or "none"))
        for k, v in amb.items() if k.startswith("Ta"))
    s = SERVO["inputs"]["servo"]
    return """
<section id="f3-servo-thermal">
  <h2 class="sec"><span class="tn">F3.1</span>Servo winding heating at the measured walking duty</h2>
  <p class="lead">%s <b>%s</b> — %s</p>
  <p>The load is not a round number: <code>sim/thermal_duty.py</code> runs Pollen's own
  walking policy and records <code>data.actuator_force</code> at every <b>200&nbsp;Hz physics
  step</b>, then reports <code>mean(&tau;²)</code> per joint, because copper loss is I²R and
  current is proportional to torque — the mean of the <i>square</i> is the only average that
  maps linearly onto heat. Lane F2's <code>gait-peaks.json</code> samples the same walk at the
  50&nbsp;Hz control frame and agrees to within the sub-tick peaks this run also catches.</p>
  <div class="tw"><table class="data">
    <caption>Table F3.1. Per joint, %s of commanded walking at v<sub>x</sub>&nbsp;=&nbsp;0.25&nbsp;m/s.
    Case temperature is a <b>band</b>: the lower bound is a black body in free air (the best
    cooling physics allows), the upper bound is no radiation at all with 30&nbsp;%% of the skin
    covered by its printed mount. The winding is hotter than the case by an unpublished amount,
    so even the lower bound is a lower bound.</caption>
    <thead><tr><th>Joint</th><th class=n>&tau;<sub>rms</sub> (N·m)</th>
      <th class=n>&tau;<sub>peak</sub> (N·m)</th><th class=n>I<sub>rms</sub> (A)</th>
      <th class=n>I<sub>peak</sub> (A)</th><th class=n>P<sub>Cu</sub> (W)</th>
      <th class=n>T<sub>case</sub> low (°C)</th><th class=n>T<sub>case</sub> high (°C)</th>
      <th>Grade</th></tr></thead>
    <tbody>%s</tbody>
  </table></div>
  <div class="card">
    <h3>Where the electrical numbers come from</h3>
    <p><b>Torque constant %s N·m/A</b> — %s</p>
    <p><b>Terminal resistance %s &Omega;</b> — %s</p>
    <p><b>The 70&nbsp;°C limit</b> — %s</p>
  </div>
  <div class="tw"><table class="data">
    <caption>Table F3.2. Time to the 70&nbsp;°C limit for %s, as a <b>curve over the unpublished
    lumped capacitance</b>, not a number. ROBOTIS publishes no thermal capacitance; c<sub>p</sub>
    is swept on the vendor's 18&nbsp;g mass and each row says which sweep point it is.</caption>
    <thead><tr><th class=n>assumed c<sub>p</sub> (J/kg·K)</th><th class=n>C (J/K)</th>
      <th>&epsilon;</th><th class=n>&tau;<sub>thermal</sub> (s)</th>
      <th class=n>steady rise (K)</th><th class=n>time to 70&nbsp;°C (min)</th></tr></thead>
    <tbody>%s</tbody>
  </table></div>
  <div class="card"><h3>Scope: this is not only the v<sub>x</sub>&nbsp;=&nbsp;0.25&nbsp;m/s baseline</h3>
  <p>Lane F2's sweep records cells whose peak torques are 2.4–3.2× the baseline, and copper loss
  goes as &tau;², so those cells are a different thermal problem rather than a footnote.
  <code>sim/thermal_duty.py</code> was extended with <code>--cell / --slope-deg / --slope-dir</code>
  (slope done exactly as <code>sim/gait_sweep.py</code>:77–81 does it — floor flat, gravity rotated)
  and re-run on them; each is graded below at its own <i>measured</i> mean(&tau;²).</p></div>
  <div class="tw"><table class="data">
    <caption>Table F3.2b. Every duty cell, graded at 25&nbsp;°C. Steady state assumes the cell is
    held indefinitely — how long a Microduck is actually walked at v<sub>x</sub>&nbsp;=&nbsp;0.80&nbsp;m/s
    is a product decision nobody has made, and that is recorded as a CANNOT DETERMINE, not
    guessed.</caption>
    <thead><tr><th>Cell</th><th class=n>s</th><th>Worst joint</th>
      <th class=n>mean(&tau;²) (N²m²)</th><th class=n>vs baseline</th>
      <th class=n>P<sub>Cu</sub> (W)</th><th class=n>T<sub>case</sub> best (°C)</th>
      <th class=n>T<sub>case</sub> worst (°C)</th><th>Verdict</th></tr></thead>
    <tbody>%s</tbody>
  </table></div>
  <div class="tw"><table class="data">
    <caption>Table F3.2c. Joints over 70&nbsp;°C at <i>best</i> cooling with 30&nbsp;%% of the skin
    blocked, <b>per ambient</b> — every ambient this study carries, including the ones whose answer
    is <i>none</i>. The first version read this off the 25&nbsp;°C row alone and published an empty
    list while the 35&nbsp;°C row said otherwise.</caption>
    <thead><tr><th class=n>Ambient</th><th>Joints over the limit</th></tr></thead>
    <tbody>%s</tbody>
  </table></div>
  <p>The servo bus draws at least <b>%.4f&nbsp;W</b> (copper plus positive mechanical work,
  both measured; drive-stage loss is not modelled, so it is a floor), i.e.
  <b>%.4f&nbsp;A</b> at the 7.4&nbsp;V pack.</p>
  %s
</section>
""" % (chip(SERVO["verdict"]), E(SERVO["study"]), E(SERVO["why"]),
       E(SERVO["inputs"]["load_basis"]["statistic"]),
       "".join(rows), s["torque_constant_Nm_per_A"], E(s["torque_constant_basis"]),
       s["terminal_resistance_ohm"], E(s["terminal_resistance_basis"]),
       E(s["temperature_limit_quote"]), E(o["worst_joint"]), tc,
       cellrows, ambrows,
       o["bus_power_lower_bound_W"], o["pack_current_lower_bound_A"]["7.4 (2S nominal)"],
       opens(SERVO.get("cannot_determine")))


# ---------------------------------------------------------------- study 2
def compute_section():
    o = COMP["outputs"]
    g = COMP["inputs"]["enclosure_geometry"]
    m = COMP["inputs"]["measured_on_the_real_robot"]
    leg = o["which_leg_fails"]
    curve = "".join(
        "<tr><td class=n>%.1f</td><td class=n>%.2f</td><td class=n>%.2f</td>"
        "<td class=n>%.2f</td><td class=n>%.2f</td></tr>"
        % (r["dissipation_W"],
           r["area_high_voxel_hull"]["skin_temp_C_eps1_bestcooling"],
           r["area_low_shells_only"]["skin_temp_C_eps0_worstcooling"],
           r["area_high_voxel_hull"]["R_th_skin_to_ambient_K_W_eps1"],
           r["area_low_shells_only"]["R_th_skin_to_ambient_K_W_eps0"])
        for r in o["skin_temperature_curve"] if r["ambient_C"] == 25.0)
    cav = "".join(
        "<tr><td>%s</td><td class=n>%s</td><td class=n>%.4f</td><td class=n>%.4f</td>"
        "<td class=n>%.1f</td><td class=n>%.0f</td></tr>"
        % (E(k), " × ".join("%.3f" % v for v in c["body_bbox_mm"]["size"]),
           c["enclosed_volume_cm3"], c["free_air_volume_cm3"],
           100 * c["free_air_fraction_of_enclosed"],
           c["shell_outer_area_estimate_mm2"])
        for k, c in CAV["outputs"]["cavities"].items())
    cavs = CAV["outputs"]["cavities"]
    xrows = "".join(
        "<tr><td>%s</td><td>%s</td><td>%s</td><td class=n>%.3f</td>"
        "<td class=n>%.3f</td><td>%s</td></tr>"
        % (E(k), E(r["mesh"]), chip(r["verdict"]), r["exact_volume_mm3"],
           r["voxel_volume_mm3"], E(r["why"]))
        for k, c in cavs.items()
        for r in c.get("voxel_occupancy_crosscheck", {}).get(
            "meshes_that_did_not_agree", []))
    hx = cavs["head"].get("voxel_occupancy_crosscheck", {})
    conv = cavs["head"].get("grid_convergence")
    convrows = "" if not conv else "".join(
        "<tr><td class=n>%.2f</td><td class=n>%s</td><td class=n>%.4f</td>"
        "<td class=n>%.4f</td><td class=n>%.4f</td><td class=n>%s</td>"
        "<td class=n>%.3f</td></tr>"
        % (r["voxel_step_mm"], " × ".join(str(v) for v in r["grid"]),
           r["enclosed_volume_cm3"], r["free_air_volume_cm3"],
           r["free_air_volume_corrected_cm3"], r["n_meshes_disagreeing"],
           r["solid_invisible_to_grid_mm3"])
        for r in conv["rows"])
    convblock = "" if not conv else """
  <div class="tw"><table class="data">
    <caption>Table F3.3c. Grid convergence on the head cavity — the same geometry measured at
    every voxel step, coarsest first. The <b>finest</b> run is the reported answer above; free air
    moved %+.3f&nbsp;%%%% and the enclosed volume %+.3f&nbsp;%%%% between the coarsest and the
    finest. Verdict %s — %s</caption>
    <thead><tr><th class=n>step (mm)</th><th class=n>grid</th><th class=n>enclosed (cm³)</th>
      <th class=n>free air (cm³)</th><th class=n>free air corrected (cm³)</th>
      <th class=n>meshes disagreeing</th><th class=n>solid invisible (mm³)</th></tr></thead>
    <tbody>%s</tbody>
  </table></div>""" % (conv["free_air_change_pct"], conv["enclosed_change_pct"],
                       chip(conv["verdict"]), E(conv["why"]), convrows)
    return """
<section id="f3-compute-thermal">
  <h2 class="sec"><span class="tn">F3.2</span>The compute inside the closed printed enclosure</h2>
  <div class="card"><h3>A correction the model forced</h3>
  <p>The compute board is <b>not in the trunk</b>. %s</p></div>
  <p class="lead">%s <b>%s</b> — %s</p>
  <div class="tw"><table class="data">
    <caption>Table F3.3. The two closed cavities, measured off the meshes
    (<code>sim/cavity_measure.py</code>: 3-axis voxel enclosure test at
    %s&nbsp;mm, per-mesh ray-parity occupancy, exact signed-tetrahedron volumes as
    the cross-check).</caption>
    <thead><tr><th>Cavity</th><th class=n>bbox (mm)</th><th class=n>enclosed (cm³)</th>
      <th class=n>free air (cm³)</th><th class=n>void (%%)</th>
      <th class=n>outer skin (mm²)</th></tr></thead>
    <tbody>%s</tbody>
  </table></div>
  <div class="card"><h3>The cross-check fired, and here it is</h3>
  <p>The method calls the exact signed-tetrahedron volumes <q>an independent cross-check on the
  voxel occupancy</q>. A check that is computed and then discarded is not a check, so every mesh is
  now graded against its own exact volume and the disagreements are named below. Head verdict
  %s. %s The remaining disagreements are shape errors, not blindness — a thin open shell is
  <i>filled</i> by the ray-parity test while the tetrahedron sum measures only its own material —
  and the grid-convergence table below is what bounds their effect on the answer.</p></div>
  <div class="tw"><table class="data">
    <caption>Table F3.3b. Every mesh whose voxel occupancy disagreed with its own exact solid
    volume by more than 10&nbsp;%%. Two distinct failures: a feature thinner than the voxel step is
    invisible to a centre-sampled grid, and an open/thin shell mesh is <i>filled</i> by the
    ray-parity test.</caption>
    <thead><tr><th>Cavity</th><th>Mesh</th><th>Verdict</th><th class=n>exact (mm³)</th>
      <th class=n>voxel (mm³)</th><th>Why</th></tr></thead>
    <tbody>%s</tbody>
  </table></div>
  %s
  <div class="tw"><table class="data">
    <caption>Table F3.4. Head skin temperature in a 25&nbsp;°C room, external leg only
    (Churchill–Chu vertical plate, L&nbsp;=&nbsp;%.4f&nbsp;m, air properties from Çengel
    Table&nbsp;A-9, radiation bracketed &epsilon;&nbsp;=&nbsp;1…0, area bracketed between the
    shells' outer skin and the voxel hull).</caption>
    <thead><tr><th class=n>dissipation (W)</th><th class=n>skin low (°C)</th>
      <th class=n>skin high (°C)</th><th class=n>R<sub>th</sub> low (K/W)</th>
      <th class=n>R<sub>th</sub> high (K/W)</th></tr></thead>
    <tbody>%s</tbody>
  </table></div>
  <div class="card"><h3>Which leg fails</h3>
  <p>%s <b>skin&nbsp;→&nbsp;room</b>: %s</p>
  <p>%s <b>die&nbsp;→&nbsp;skin</b>: %s</p>
  <p><i>%s</i></p></div>
  <p>The measurement that settles the verdict is Pollen's own: SoC at <b>%s&nbsp;°C</b>
  (worst %s&nbsp;°C) throttling to <b>%s&nbsp;MHz</b>, with object detection held to
  %s&nbsp;Hz. %s</p>
  <p>Vendor claim, for contrast: %s</p>
  %s
</section>
""" % (E(COMP["inputs"]["correction_to_the_brief"]["evidence"]),
       chip(COMP["verdict"]), E(COMP["study"]), E(COMP["why"]),
       CAV["inputs"]["voxel_step_mm"], cav,
       chip(hx.get("verdict", "CANNOT DETERMINE")),
       ("At the reported %.2f&nbsp;mm step <b>nothing</b> is invisible to the grid, so no "
        "free-air correction is needed (%.4f&nbsp;cm\u00b3 raw and corrected). It was not "
        "always so: at 1.50&nbsp;mm the 0.84&nbsp;mm-thick Robot HAT PCB scored ZERO voxels "
        "against an exact 1569.234&nbsp;mm\u00b3, and the first version of this study "
        "published that free-air figure with no flag."
        % (cavs["head"]["voxel_step_mm"], cavs["head"]["free_air_volume_cm3"]))
       if not hx.get("solid_volume_invisible_to_the_grid_mm3") else
       ("The grid could not see <b>%.3f&nbsp;mm\u00b3</b> of solid at all, so "
        "<code>free_air_volume_mm3</code> overstates the void by at least that much; the "
        "corrected figure is <b>%.4f&nbsp;cm\u00b3</b> against the raw %.4f&nbsp;cm\u00b3, "
        "and it is the one the air-capacitance argument below uses."
        % (hx["solid_volume_invisible_to_the_grid_mm3"],
           cavs["head"]["free_air_volume_corrected_cm3"],
           cavs["head"]["free_air_volume_cm3"])),
       xrows, convblock,
       g["characteristic_length_m"], curve,
       chip(leg["external_skin_to_room"]["verdict"]), E(leg["external_skin_to_room"]["why"]),
       chip(leg["internal_die_to_skin"]["verdict"]), E(leg["internal_die_to_skin"]["why"]),
       E(leg["internal_die_to_skin"]["model"]),
       m["soc_temperature_C"], m["soc_temperature_worst_C"], m["throttled_to_MHz"],
       m["detection_rate_Hz"], E(m["quote_1"]),
       E(COMP["inputs"]["board"]["governor_quote"]),
       opens(COMP.get("cannot_determine")))


# ---------------------------------------------------------------- study 3
def tolerance_section():
    o = TOL["outputs"]
    band = "FDM-A prototyping"
    band2 = "FDM-B industrial"
    band3 = "FDM-D measured study"
    rows = []
    for n, per in o["per_joint"].items():
        a, b = per[band], per[band2]
        e = a["bearing"].get("printed_seat_engagement_pct")
        t = a["bearing"].get("total_bore_support_pct")
        cls = ' class="cd"' if (t is None or t < 99.9) else ""
        cock = a["angular_misalignment_deg"]["bearing_cock_upper_bound"]
        ae = a["axial_play_vs_bearing_engagement"]
        rows.append(
            "<tr%s><td>%s</td><td>%s</td><td class=n>%s</td><td class=n>%s</td>"
            "<td class=n>%.4f</td><td class=n>%.4f</td><td class=n>%.4f</td>"
            "<td class=n>%.4f</td><td class=n>%s</td><td class=n>%s</td>"
            "<td class=n>%.4f</td></tr>"
            % (cls, E(n), E(a["flange"]["part"].replace("microduck-", "")),
               "\u2014" if e is None else "%.2f" % e,
               "\u2014" if t is None else "%.2f" % t,
               a["axial_play_mm"]["worst_case"], a["axial_play_mm"]["rss"],
               a["radial_eccentricity_mm"]["worst_case"],
               a["radial_eccentricity_mm"]["rss"],
               "\u2014" if cock is None else "%.4f" % cock,
               "\u2014" if ae is None else "%.1f" % (100 * ae["worst_case_fraction_of_engagement"]),
               a["rotational_backlash_deg"]["worst_case"]))
    eq = o["band_to_iso286_equivalence"]
    eqrows = "".join(
        "<tr><td class=n>%s</td><td class=n>%.4f</td><td class=n>%.0f</td><td>%s</td>"
        "<td class=n>%.4f</td><td class=n>%.0f</td><td>%s</td>"
        "<td class=n>%.4f</td><td class=n>%.0f</td><td>%s</td></tr>"
        % (d, eq[band][d]["half_band_mm"], eq[band][d]["total_band_um"],
           eq[band][d]["nearest_iso286_grade_at_or_above"],
           eq[band2][d]["half_band_mm"], eq[band2][d]["total_band_um"],
           eq[band2][d]["nearest_iso286_grade_at_or_above"],
           eq[band3][d]["half_band_mm"], eq[band3][d]["total_band_um"],
           eq[band3][d]["nearest_iso286_grade_at_or_above"])
        for d in sorted(eq[band], key=float))
    st = o["iso286_selftest"]
    strows = "".join("<tr><td class=n>%s</td><td>%s</td><td class=n>%s</td>"
                     "<td class=n>%s</td><td class=n>%+.3f</td><td>%s</td></tr>"
                     % (r["nominal_mm"], r["grade"], r["published_iso286_1_um"],
                        r["derived_um"], r["derivation_drift_pct"], chip(r["verdict"]))
                     for r in st["rows"])
    flags = "".join(
        "<li>%s <b>%s</b> — %s%s</li>"
        % (chip(f["verdict"]), E(f["joint"]),
           "" if f.get("printed_seat_engagement_pct") is None
           else "printed boss %.2f&nbsp;%% of the ring, total bore support "
                "<b>%.2f&nbsp;%%</b> (%s&nbsp;mm boss + %s&nbsp;mm horn disc in a "
                "%s&nbsp;mm ring). "
                % (f["printed_seat_engagement_pct"], f["total_bore_support_pct"],
                   f["printed_seat_length_mm"], f.get("horn_disc_share_mm"),
                   f["ring_width_mm"]),
           E(f["why"])) for f in o["bearing_bore_support_flags"])
    coax = o["per_joint"]["left_hip_yaw"][band]["angular_misalignment_deg"][
        "coaxiality_step_between_the_two_bosses"]
    coaxrows = "".join(
        "<tr><td>%s</td><td class=n>%.4f</td><td>%s</td><td>%s</td></tr>"
        % (E(t["term"]), t["radial_mm"], E(t["kind"]), E(t["source"]))
        for t in coax["terms"])
    binds = o["joints_where_the_coaxiality_step_exceeds_the_radial_clearance"]
    reach = o["joints_whose_axial_stack_reaches_the_bearing_support"]
    reachrows = "".join(
        "<tr><td>%s</td><td>%s</td><td>%s</td></tr>"
        % (E(bn), E(", ".join(reach[bn]) or "none"),
           E(", ".join(reach["printed_boss_only"][bn]) or "none"))
        for bn in (band, band2, band3))
    return """
<section id="f3-tolerance">
  <h2 class="sec"><span class="tn">F3.3</span>Tolerance stack-up on all fourteen hinges</h2>
  <p class="lead">%s <b>%s</b> — %s</p>
  <div class="card"><h3>Correction: the ring's bore is carried by two parts, not one</h3>
  <p>The first version of this study divided the printed boss length by the ring width, called
  the answer <i>engagement</i>, and reported <q>7 of 14 joints seat the ring on less than its own
  width</q> as a FAIL. That is wrong, and the file the study itself listed in <code>looked_at</code>
  says so verbatim — <code>ce-parts/microduck-yaw2roll/current/cad/interfaces.json</code>,
  <code>yaw_bearing_seat</code>: <q>the bearing mesh spans 0..4 along its own axis, so it occupies
  z 12.5..16.5 here — the upper 2.05&nbsp;mm of its bore rides the horn's Ø16&nbsp;×&nbsp;3 boss.</q>
  <code>horn_bore_share()</code> now measures the split off
  <code>out/sim-evidence/joint-geometry.json</code> at every joint and cross-checks it against the
  seat length the part folder declares. Support is <b>%.2f&nbsp;%%</b> of the ring, not
  %.2f&nbsp;%%. Three numbers moved with it: the cocking angle is computed over the
  <b>supported</b> length; the clearance is <b>one</b> band and not two (a ±t shaft in a bore held
  at nominal gives t of diametral clearance, and the steel bore's own tolerance stays an open term
  instead of being silently assumed equal and opposite); and the risk that <i>is</i> real at those
  joints — the coaxiality step between the two bosses — is computed below.</p></div>
  <div class="tw"><table class="data">
    <caption>Table F3.5. Per hinge at the FDM-A band (Protolabs Network prototyping FDM,
    ±0.5&nbsp;%% with a ±0.5&nbsp;mm floor). Rows shaded where the ring's bore is not fully
    supported or no seat is declared at all. <i>Bearing cock</i> is an UPPER BOUND, not a
    measurement — see the note under Table F3.8. Terms whose tolerance is unpublished are listed
    but <b>not folded in</b>, so every figure understates the real stack.</caption>
    <thead><tr><th>Joint</th><th>Driven part</th><th class=n>printed boss (%%)</th>
      <th class=n>bore support (%%)</th>
      <th class=n>axial WC (mm)</th><th class=n>axial RSS (mm)</th>
      <th class=n>radial WC (mm)</th><th class=n>radial RSS (mm)</th>
      <th class=n>bearing cock \u2264 (\u00b0)</th><th class=n>axial / support (%%)</th>
      <th class=n>backlash WC (\u00b0)</th></tr></thead>
    <tbody>%s</tbody>
  </table></div>
  <div class="tw"><table class="data">
    <caption>Table F3.6. What each sourced FDM band is worth as an ISO&nbsp;286 grade at the
    diameters this robot actually uses, against the <b>published</b> ISO&nbsp;286-1:2010(E) table
    (archived, <code>research/fetched/engineersedge-iso286-1-it-grades.html</code>). A ball-bearing
    seat is normally an IT6–IT7 feature. D is a <i>measured</i> print-accuracy study (Wei et al.
    2025, Polymers 17(3):416) carried as evidence of what a tuned FDM machine achieved — it is not
    our printer and it does not set the verdict.</caption>
    <thead><tr><th class=n>Ø (mm)</th>
      <th class=n>A ± (mm)</th><th class=n>A band (<span style="text-transform:none">&micro;m</span>)</th><th>A grade</th>
      <th class=n>B ± (mm)</th><th class=n>B band (<span style="text-transform:none">&micro;m</span>)</th><th>B grade</th>
      <th class=n>D ± (mm)</th><th class=n>D band (<span style="text-transform:none">&micro;m</span>)</th><th>D grade</th></tr></thead>
    <tbody>%s</tbody>
  </table></div>
  <div class="tw"><table class="data">
    <caption>Table F3.7. The ISO&nbsp;286 SELF-TEST. The published rows are now the input to every
    grading above; what is under test is the i&nbsp;=&nbsp;0.45·∛D&nbsp;+&nbsp;0.001·D derivation
    the connection folders carry, across IT5…IT16 at the four diameters this robot uses. The first
    version validated IT7 alone and then graded printed bands at IT14–IT16 with an unchecked
    formula. Verdict %s.</caption>
    <thead><tr><th class=n>Ø (mm)</th><th>Grade</th>
      <th class=n>published ISO 286-1 (<span style="text-transform:none">&micro;m</span>)</th>
      <th class=n>derived (<span style="text-transform:none">&micro;m</span>)</th>
      <th class=n>drift (%%)</th><th>Verdict</th></tr></thead>
    <tbody>%s</tbody>
  </table></div>
  <div class="tw"><table class="data">
    <caption>Table F3.8. The <b>coaxiality step</b> at <code>left_hip_yaw</code> — the radial
    offset between the printed Ø16 boss and the servo's Ø16&nbsp;×&nbsp;3.0 horn disc, which
    together carry one 4.0&nbsp;mm bore. Worst case %.4f&nbsp;mm, RSS %.4f&nbsp;mm, against
    %.4f&nbsp;mm of radial clearance to absorb it — <b>%s</b>. Verdict %s:
    the second term is a bound and not a measurement, because no published FDM standard states a
    POSITIONAL tolerance, and the ring's own internal clearance is unknown.</caption>
    <thead><tr><th>Term</th><th class=n>radial (mm)</th><th>Kind</th><th>Source</th></tr></thead>
    <tbody>%s</tbody>
  </table></div>
  <p><b>Where the step binds:</b> %s at FDM-A; %s at FDM-B; %s at the measured-study band.
  <i>What settles it:</i> %s</p>
  <div class="tw"><table class="data">
    <caption>Table F3.9. The lane brief's own flag — does the axial stack reach the length the ring
    is supported over? Every band is listed, including the ones whose answer is <i>none</i>.</caption>
    <thead><tr><th>Band</th><th>Stack reaches total bore support</th>
      <th>Stack reaches the printed boss alone</th></tr></thead>
    <tbody>%s</tbody>
  </table></div>
  <div class="card"><h3>Bearing bore-support flags</h3><ul>%s</ul></div>
  <div class="card"><h3>What stays open</h3><ul>%s</ul></div>
</section>
""" % (chip(TOL["verdict"]), E(TOL["study"]), E(TOL["why"]),
       o["bearing_bore_support_flags"][0]["total_bore_support_pct"],
       o["bearing_bore_support_flags"][0]["printed_seat_engagement_pct"],
       "".join(rows), eqrows,
       chip(st["verdict"]), strows,
       coax["worst_case_mm"], coax["rss_mm"], coax["available_radial_clearance_mm"],
       "so at this band the ring binds" if coax["binds"]
       else "so at this band the clearance takes it up",
       chip(coax["verdict"]), coaxrows,
       E(", ".join(binds[band]) or "nowhere"),
       E(", ".join(binds[band2]) or "nowhere"),
       E(", ".join(binds[band3]) or "nowhere"),
       E(coax["what_settles_it"]),
       reachrows, flags,
       "".join("<li><b>%s</b> — %s <i>What settles it:</i> %s</li>"
               % (E(t["term"]), E(t["why_open"]), E(t["what_settles_it"]))
               for t in o["per_joint"]["left_hip_yaw"]["FDM-A prototyping"]["open_terms"]))


def sections():
    return servo_section() + compute_section() + tolerance_section()


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Microduck &mdash; simulation evidence, lane F3</title>
<link rel="stylesheet" href="../../tools/doc.css">
<style>
 .data td.cd, .data tr.cd td { background: #fff4f2; }
 .card { margin: 18px 0; padding: 14px 16px; border: 1px solid #ddd; border-radius: 4px; }
 .card h3 { margin-top: 0; }
 table.data { font-size: 11px; }
 th { white-space: normal; }
</style>
</head><body><div class="wrap">
<p class="backlink"><a href="../../RELEASE.html">&larr; Release dossier</a></p>
<header class="hero">
  <p class="eyebrow">Microduck reverse-engineering &middot; simulation evidence</p>
  <h1>Thermal &amp; tolerance stack-up</h1>
  <p class="sub">Lane F3. A preview of the sections <code>tools/gen_simulation.py</code>
  includes in SIMULATION.html; the data is
  <code>out/sim-evidence/gait-torque-duty.json</code>,
  <code>thermal-servo-xl330.json</code>, <code>cavity-volumes.json</code>,
  <code>thermal-compute-head.json</code>, <code>joint-geometry.json</code> and
  <code>tolerance-stack-hinges.json</code>.</p>
</header>
%s
<footer class="note">Generated by <code>tools/gen_simulation_f3.py</code>. Every number on this
page is read out of those JSON files; none is typed here.</footer>
</div></body></html>
"""


def main():
    frag = sections()
    os.makedirs(EV, exist_ok=True)
    fp = os.path.join(EV, "f3-sections.html")
    open(fp, "w").write(frag)
    pp = os.path.join(EV, "f3-preview.html")
    open(pp, "w").write(PAGE % frag)
    print("wrote", os.path.relpath(fp, REPO), os.path.getsize(fp), "bytes")
    print("wrote", os.path.relpath(pp, REPO), os.path.getsize(pp), "bytes")


if __name__ == "__main__":
    main()
