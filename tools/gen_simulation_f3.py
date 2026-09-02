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
        % (E(k), " × ".join("%.3f" % v for v in c["shell_bbox_mm"]["size"]),
           c["enclosed_volume_cm3"], c["free_air_volume_cm3"],
           100 * c["free_air_fraction_of_enclosed"],
           c["shell_outer_area_estimate_mm2"])
        for k, c in CAV["outputs"]["cavities"].items())
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
       CAV["inputs"]["voxel_step_mm"], cav, g["characteristic_length_m"], curve,
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
    rows = []
    for n, per in o["per_joint"].items():
        a, b = per[band], per[band2]
        e = a["bearing"].get("engagement_pct")
        cls = ' class="cd"' if (e is None or e < 100.0) else ""
        cock = a["angular_misalignment_deg"]["bearing_cock_worst_case"]
        ae = a["axial_play_vs_bearing_engagement"]
        rows.append(
            "<tr%s><td>%s</td><td>%s</td><td class=n>%s</td>"
            "<td class=n>%.4f</td><td class=n>%.4f</td><td class=n>%.4f</td>"
            "<td class=n>%.4f</td><td class=n>%s</td><td class=n>%s</td>"
            "<td class=n>%.4f</td></tr>"
            % (cls, E(n), E(a["flange"]["part"].replace("microduck-", "")),
               "—" if e is None else "%.2f" % e,
               a["axial_play_mm"]["worst_case"], a["axial_play_mm"]["rss"],
               a["radial_eccentricity_mm"]["worst_case"],
               a["radial_eccentricity_mm"]["rss"],
               "—" if cock is None else "%.4f" % cock,
               "—" if ae is None else "%.1f" % (100 * ae["worst_case_fraction_of_engagement"]),
               a["rotational_backlash_deg"]["worst_case"]))
    eq = o["band_to_iso286_equivalence"]
    eqrows = "".join(
        "<tr><td class=n>%s</td><td class=n>%.4f</td><td class=n>%.0f</td><td>%s</td>"
        "<td class=n>%.4f</td><td class=n>%.0f</td><td>%s</td></tr>"
        % (d, eq[band][d]["half_band_mm"], eq[band][d]["total_band_um"],
           eq[band][d]["nearest_iso286_grade_at_or_above"],
           eq[band2][d]["half_band_mm"], eq[band2][d]["total_band_um"],
           eq[band2][d]["nearest_iso286_grade_at_or_above"])
        for d in sorted(eq[band], key=float))
    st = o["iso286_selftest"]
    strows = "".join("<tr><td class=n>%s</td><td>%s</td><td class=n>%s</td>"
                     "<td class=n>%s</td><td>%s</td></tr>"
                     % (r["nominal_mm"], r["grade"], r["derived_um"],
                        r["published_iso286_2_um"], chip(r["verdict"]))
                     for r in st["rows"])
    flags = "".join("<li><b>%s</b> — %s%s</li>"
                    % (E(f["joint"]),
                       "" if f["engagement_pct"] is None
                       else "%.2f %% engagement (%s mm boss in a %s mm ring). "
                            % (f["engagement_pct"], f["seat_length_mm"], f["ring_width_mm"]),
                       E(f["why"])) for f in o["engagement_flags"])
    return """
<section id="f3-tolerance">
  <h2 class="sec"><span class="tn">F3.3</span>Tolerance stack-up on all fourteen hinges</h2>
  <p class="lead">%s <b>%s</b> — %s</p>
  <div class="card"><h3>The joint is one station, not two</h3>
  <p><code>sim/joint_geometry.py</code> projects every geom onto each hinge's own axis. On
  twelve of the fourteen joints the driven horn face and the supporting ball bearing are
  <b>coincident to 0.1&nbsp;mm</b> — the bearing's inner race sits on the same Ø16 boss the
  horn bolts to. So no two-support span model is used; the angle is held by the bolted flange
  and by how much the bearing's short engagement lets the boss cock in its bore, and which of
  the two governs is computed.</p></div>
  <div class="tw"><table class="data">
    <caption>Table F3.5. Per hinge at the FDM-A band (Protolabs Network prototyping FDM,
    ±0.5&nbsp;%% with a ±0.5&nbsp;mm floor). Rows shaded where the ring seats on less than its
    own width or no seat is declared at all. Terms whose tolerance is unpublished are listed
    but <b>not folded in</b>, so every figure understates the real stack.</caption>
    <thead><tr><th>Joint</th><th>Driven part</th><th class=n>engage (%%)</th>
      <th class=n>axial WC (mm)</th><th class=n>axial RSS (mm)</th>
      <th class=n>radial WC (mm)</th><th class=n>radial RSS (mm)</th>
      <th class=n>bearing cock (°)</th><th class=n>axial / engage (%%)</th>
      <th class=n>backlash WC (°)</th></tr></thead>
    <tbody>%s</tbody>
  </table></div>
  <div class="tw"><table class="data">
    <caption>Table F3.6. What each published FDM band is worth as an ISO&nbsp;286 grade at the
    diameters this robot actually uses. A ball-bearing seat is normally an IT6–IT7 feature.</caption>
    <thead><tr><th class=n>Ø (mm)</th><th class=n>A ± (mm)</th><th class=n>A band (<span style="text-transform:none">&micro;m</span>)</th>
      <th>A grade</th><th class=n>B ± (mm)</th><th class=n>B band (<span style="text-transform:none">&micro;m</span>)</th>
      <th>B grade</th></tr></thead>
    <tbody>%s</tbody>
  </table></div>
  <div class="tw"><table class="data">
    <caption>Table F3.7. The ISO&nbsp;286 derivation's own self-test — IT7 derived from
    i&nbsp;=&nbsp;0.45·∛D&nbsp;+&nbsp;0.001·D and checked against published rows it was not
    fitted to. Verdict %s.</caption>
    <thead><tr><th class=n>Ø (mm)</th><th>Grade</th><th class=n>derived (<span style="text-transform:none">&micro;m</span>)</th>
      <th class=n>published (<span style="text-transform:none">&micro;m</span>)</th><th>Verdict</th></tr></thead>
    <tbody>%s</tbody>
  </table></div>
  <div class="card"><h3>Bearing engagement flags</h3><ul>%s</ul></div>
  <div class="card"><h3>What stays open</h3><ul>%s</ul></div>
</section>
""" % (chip(TOL["verdict"]), E(TOL["study"]), E(TOL["why"]), "".join(rows), eqrows,
       chip(st["verdict"]), strows, flags,
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
