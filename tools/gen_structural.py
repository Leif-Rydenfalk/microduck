#!/usr/bin/env python3
"""gen_structural.py — build STRUCTURAL.html (lane F1: FEA on every structural
part, drop/impact, fatigue) from the study JSONs in out/sim-evidence/.

Data-driven, regenerable, never hand-edited:
    python3 tools/gen_structural.py            -> STRUCTURAL.html, then selfcheck() — exit 1 on any failed check
    from tools.gen_structural import sections  -> the inner <section>s for a synth (SIMULATION.html)

Inputs (each a study JSON with {study, inputs, method, outputs, verdict, why, script, artifacts, looked_at}):
    out/sim-evidence/loads_mujoco.json           sim/measure_loads.py
    out/sim-evidence/fea_<part>_<case>.json      sim/stress_all.py, graded by sim/fea_rejudge.py (one rule, every study)
    out/sim-evidence/fea_nlgeom_<part>_<case>.json  sim/fea_nlgeom.py (geometrically nonlinear re-solves)
    out/sim-evidence/fea_convergence_*.json      sim/stress_all.py
    out/sim-evidence/fea_materials_*.json        sim/stress_all.py
    out/sim-evidence/fea_meshability_*.json      the mesher refusal, diagnosed to the face
    out/sim-evidence/buckling_*.json             sim/struct_ce.py (+ section_*.json from sim/member_section.py)
    out/sim-evidence/drop_impact.json            sim/drop_impact.py
    out/sim-evidence/fatigue_walk.json           sim/fatigue_walk.py (every part); fatigue_ankle.json (the ankle, mesh-scaled)
    out/stress/matrix.json                       sim/stress_matrix.py (the detached 20/60/15 N matrix, consumed)

History (F1 skeptic, 2026-09-03): the first version skipped every study whose file name contained "_h" — meant for
convergence sub-runs that are never written as files — and so silently dropped all four *_head_drop studies, among
them the worst safety factor in the lane. The filter is now a regex on the sub-run suffix, and selfcheck() counts
what is on disk against what is published before the page is allowed to exist.
"""
import glob
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
EVID = os.path.join(REPO, "out", "sim-evidence")
CONV_SUBRUN = re.compile(r"_h(auto|[0-9]+(\.[0-9]+)?)\.json$")


def load(name):
    p = os.path.join(EVID, name) if not os.path.isabs(name) else name
    return json.load(open(p)) if os.path.exists(p) else None


def esc(s):
    return html.escape(str(s))


def f(v, dp=3):
    if v is None:
        return "—"
    try:
        return ("%%.%df" % dp) % float(v)
    except (TypeError, ValueError):
        return esc(v)


def g(v, sig=4):
    """significant digits — for lives that span 3e-7 .. 1e9 km"""
    if v is None:
        return "—"
    try:
        return ("%%.%dg" % sig) % float(v)
    except (TypeError, ValueError):
        return esc(v)


def chip(v):
    v = v or "CANNOT DETERMINE"
    cls = {"PASS": "pass", "FAIL": "fail"}.get(v, "cd")
    return '<span class="chip %s">%s</span>' % (cls, esc(v))


# the real product photograph that shows each part's joint (Leif: every render of ours sits beside the real one)
REF_PHOTO = {
    "microduck-ankle-left": ("out/compare/ref-joint-ankle.png", "ankle + foot, cropped from the official profile photograph"),
    "microduck-foot-left": ("out/compare/ref-joint-ankle.png", "ankle + foot, cropped from the official profile photograph"),
    "microduck-sole-left": ("out/compare/ref-joint-ankle.png", "ankle + foot, cropped from the official profile photograph"),
    "microduck-shin": ("out/compare/ref-joint-knee.png", "knee, cropped from the official profile photograph"),
    "microduck-upper-leg-left": ("out/compare/ref-joint-knee.png", "knee, cropped from the official profile photograph"),
    "microduck-upper-leg-rigidity-plate": ("out/compare/ref-joint-knee.png", "knee, cropped from the official profile photograph"),
    "microduck-hip-bracket": ("out/compare/ref-joint-hip.png", "hip cluster, cropped from the official photograph"),
    "microduck-yaw2roll": ("out/compare/ref-joint-hip.png", "hip cluster, cropped from the official photograph"),
    "microduck-trunk-base": ("out/compare/ref-joint-hip.png", "hip cluster, cropped from the official photograph"),
    "microduck-neck-plate": ("out/compare/ref-joint-neck.png", "neck stack, cropped from the official photograph"),
    "microduck-neck-pitch-bracket": ("out/compare/ref-joint-neck.png", "neck stack, cropped from the official photograph"),
    "microduck-yaw-roll-motion": ("out/compare/ref-joint-neck.png", "neck stack, cropped from the official photograph"),
    "microduck-motor-support": ("out/compare/ref-joint-neck.png", "neck stack, cropped from the official photograph"),
}
PART_ORDER = ["microduck-sole-left", "microduck-foot-left", "microduck-ankle-left", "microduck-shin", "microduck-upper-leg-left",
              "microduck-upper-leg-rigidity-plate", "microduck-hip-bracket", "microduck-yaw2roll", "microduck-trunk-base",
              "microduck-neck-plate", "microduck-neck-pitch-bracket", "microduck-yaw-roll-motion", "microduck-motor-support",
              "microduck-power-support"]
CASE_ORDER = {"walk": 0, "drop": 1, "head_drop": 2}
CASE_LABEL = {"walk": "walk", "drop": "foot drop", "head_drop": "head drop"}


def slug_of(r):
    return r["part"].split(":", 1)[1]


def fea_files_on_disk():
    return sorted(glob.glob(os.path.join(EVID, "fea_microduck-*.json")))


def fea_studies():
    out = []
    for p in fea_files_on_disk():
        if CONV_SUBRUN.search(os.path.basename(p)):      # a convergence sub-run written as its own file (none today)
            continue
        out.append(json.load(open(p)))
    out.sort(key=lambda r: (PART_ORDER.index(slug_of(r)) if slug_of(r) in PART_ORDER else 99, CASE_ORDER.get(r.get("case"), 9)))
    return out


def sf_used(r):
    """the SF the grading rule judged on (min of table/TDS; nonlinear when the linear left its regime) — else the raw table SF"""
    o = r.get("outputs") or {}
    gr = o.get("grading") or {}
    return gr.get("sf_used", o.get("sf"))


def regime_of(r):
    return ((r.get("outputs") or {}).get("grading") or {}).get("regime") or {}


def nonlinear_of(r):
    return ((r.get("outputs") or {}).get("grading") or {}).get("nonlinear")


def nlgeom_studies():
    return [json.load(open(p)) for p in sorted(glob.glob(os.path.join(EVID, "fea_nlgeom_*.json")))]


def buckling_studies():
    return [json.load(open(p)) for p in sorted(glob.glob(os.path.join(EVID, "buckling_*.json")))]


# ---------------------------------------------------------------------------
def sec_verdict(L, feas, drop, fat, fatw, conv, mats, meshab):
    solved = [r for r in feas if sf_used(r) is not None]
    graded = [r for r in solved if r.get("verdict") in ("PASS", "FAIL")]
    fails = [r for r in feas if r.get("verdict") == "FAIL"]
    cds = [r for r in feas if r.get("verdict") == "CANNOT DETERMINE"]
    passes = [r for r in feas if r.get("verdict") == "PASS"]
    on_disk = len(fea_files_on_disk())
    walk_g = [r for r in graded if r["case"] == "walk"]
    walk_all = [r for r in solved if r["case"] == "walk"]
    gov_walk = min(walk_g, key=sf_used) if walk_g else None
    worst_walk = min(walk_all, key=sf_used) if walk_all else None
    foot_g = [r for r in graded if r["case"] == "drop"]
    foot_all = [r for r in solved if r["case"] == "drop"]
    gov_foot = min(foot_g, key=sf_used) if foot_g else None
    worst_foot = min(foot_all, key=sf_used) if foot_all else None
    head_g = [r for r in graded if r["case"] == "head_drop"]
    gov_head = min(head_g, key=sf_used) if head_g else None
    worst_disk = min(solved, key=sf_used) if solved else None
    s = ['<section id="verdict"><h2><span class="n">1</span>Verdict — does the structure hold?</h2>']
    s.append('<div class="statbar">'
             '<div class="stat"><b>%d</b><span>parts solved</span></div>'
             '<div class="stat"><b>%d / %d</b><span>studies published / on disk</span></div>'
             '<div class="stat"><b>%d / %d / %d</b><span>PASS / FAIL / CANNOT DETERMINE</span></div>'
             '<div class="stat"><b>%s</b><span>walk peak GRF, N (%.3f× weight)</span></div>'
             '<div class="stat"><b>%s</b><span>foot-drop peak, N (MuJoCo, lower bound)</span></div>'
             '<div class="stat"><b>%s</b><span>head-drop peak, N (MuJoCo, lower bound)</span></div>'
             '</div>' % (len({r["part"] for r in solved}), len(feas), on_disk, len(passes), len(fails), len(cds),
                         f(L["walk"]["peak_vertical_grf_N"], 4) if L else "—", L["walk"]["peak_grf_over_bodyweight"] if L else 0,
                         f(next((d["peak_normal_force_N"] for d in L["drops"] if d["label"] == "drop_foot_rollm10_default_contact_dt5ms"), None), 3) if L else "—",
                         f(next((d["peak_normal_force_N"] for d in L["drops"] if d["label"] == "drop_head_default_contact_dt5ms"), None), 3) if L else "—"))
    s.append('<p class="lede">Every number below is the more conservative of two safety factors (class table, fetched datasheet), graded by ONE rule in '
             '<code>sim/fea_rejudge.py</code> applied to all %d studies: SF ≥ 2 passes; a deflection outside the small-deflection regime makes the linear '
             'peak a bound and hands the verdict to the geometrically nonlinear re-solve (§3b) when one has converged; a part declared in <code>sim/load_share.py</code> '
             'as carrying a force in <em>parallel</em> with a body not in the model is CANNOT DETERMINE on a FAIL, with the bound printed. The worst linear number on disk '
             'is stated in every verdict regardless of its grade.</p>' % len(feas))
    if gov_walk:
        o = gov_walk["outputs"]
        s.append('<div class="verdict %s"><b>Walking — %s.</b> Every solved part carries the measured walking peak. Governing graded part: '
                 '<code>%s</code> at SF <b>%s</b> (peak von Mises %s MPa, table yield %s MPa, TDS-yield SF %s, %s against the 17 MPa interlayer figure). '
                 'Worst walking number on disk, any grade: <code>%s</code> SF %s (%s). The walking load is what MuJoCo measured, not a round number: the body '
                 'forces at the gait peak, in each part\'s own frame (§2).</div>' % (
                     "warn" if any(r["verdict"] == "FAIL" for r in walk_g) else "",
                     "PASS on every graded part" if all(r["verdict"] == "PASS" for r in walk_g) else "%d of %d graded parts FAIL" % (sum(r["verdict"] == "FAIL" for r in walk_g), len(walk_g)),
                     esc(gov_walk["part"]), f(sf_used(gov_walk)), f(o["max_von_mises_mpa"]), f(o.get("yield_mpa_used"), 0), f(o.get("sf_vs_tds_yield")),
                     f(o.get("sf_vs_tds_interlayer_across_layers")), esc(worst_walk["part"]), f(sf_used(worst_walk)), esc(worst_walk["verdict"])))
    if gov_foot:
        o = gov_foot["outputs"]
        s.append('<div class="verdict %s"><b>A 0.250 m fall onto one foot — %s.</b> Governing graded part: <code>%s</code> at SF <b>%s</b> '
                 '(peak von Mises %s MPa, linear failure load %s N against the %s N applied). Worst foot-drop number on disk, any grade: <code>%s</code> SF %s (%s). '
                 'The applied drop force is MuJoCo\'s default-contact peak, which §6 shows is the <em>soft</em> end of a bracket that reaches %s N (Hertz heel arc, TDS modulus) '
                 'to %s N (rigid on the sole floor stiffness): a part that fails at the soft end fails at every point of the bracket. The height itself is the brief\'s input, '
                 'not a requirement (§6).</div>' % (
                     "warn" if gov_foot["verdict"] == "FAIL" else "", gov_foot["verdict"], esc(gov_foot["part"]), f(sf_used(gov_foot)), f(o["max_von_mises_mpa"]),
                     f(o.get("failure_load_N_linear"), 2), f(gov_foot["inputs"]["force_magnitude_N"], 3), esc(worst_foot["part"]), f(sf_used(worst_foot)), esc(worst_foot["verdict"]),
                     f((drop or {}).get("outputs", {}).get("bracket_foot_N", {}).get("hertz_heel_tds"), 0),
                     f((drop or {}).get("outputs", {}).get("bracket_foot_N", {}).get("upper_rigid_table"), 0)))
    if gov_head:
        o = gov_head["outputs"]
        reg = regime_of(gov_head)
        nl = nonlinear_of(gov_head) or {}
        s.append('<div class="verdict %s"><b>A 0.250 m fall onto the head — %s.</b> The trunk decelerating through the neck chain (four parts solved, §3): governing '
                 '<code>%s</code> at SF <b>%s</b>, peak von Mises %s MPa, δ %s mm%s. Head-drop transmitted forces: %s.</div>' % (
                     "warn" if gov_head["verdict"] == "FAIL" else "", gov_head["verdict"], esc(gov_head["part"]), f(sf_used(gov_head)), f(o["max_von_mises_mpa"]),
                     f(o["max_displacement_mm"], 4),
                     (" — OUTSIDE the small-deflection regime (d/L %s), so the linear number is a bound%s" % (
                         f(reg.get("d_over_L"), 4), ("; the nonlinear re-solve reads SF %s and carries the verdict" % f(nl.get("sf_governing"))) if nl.get("sf_governing") else " until the nonlinear re-solve lands (§3b)")
                      ) if reg.get("linear_regime_valid") is False else "",
                     esc("; ".join("%s %s N" % (r["part"].replace("part:microduck-", ""), f(r["inputs"]["force_magnitude_N"], 3)) for r in feas if r["case"] == "head_drop"))))
    if fails:
        s.append('<div class="verdict warn"><b>FAIL list — %d studies.</b><ul>%s</ul></div>' % (len(fails), "".join(
            '<li><code>%s</code> %s — SF <b>%s</b>: %s</li>' % (esc(r["part"]), esc(CASE_LABEL.get(r["case"], r["case"])), f(sf_used(r)), esc(r.get("why", ""))) for r in fails)))
    if cds:
        s.append('<div class="verdict warn"><b>CANNOT DETERMINE — %d studies, each with its bound.</b><ul>%s</ul></div>' % (len(cds), "".join(
            '<li><code>%s</code> %s — %s: %s</li>' % (esc(r["part"]), esc(CASE_LABEL.get(r["case"], r["case"])), ("linear bound SF <b>%s</b>" % f(sf_used(r))) if sf_used(r) is not None else "no solve",
                                                       esc(r.get("why", ""))) for r in cds)))
    bk = buckling_studies()
    if bk:
        s.append('<div class="verdict %s"><b>Buckling — %s.</b><ul>%s</ul></div>' % (
            "warn" if any(r["verdict"] == "FAIL" for r in bk) else "", " / ".join(sorted({r["verdict"] for r in bk})),
            "".join('<li><code>%s</code> %s: %s</li>' % (esc(r["part"].replace("part:", "")), chip(r["verdict"]), esc(r["why"])) for r in bk)))
    if fatw:
        s.append('<div class="verdict %s"><b>Fatigue under the walking cycle, every part — %s.</b> %s (§7). The ankle alone (the part the brief named) is PASS: %s</div>' % (
            "warn" if fatw["verdict"] != "PASS" else "", esc(fatw["verdict"]), esc(fatw["why"]), esc((fat or {}).get("why", "—"))))
    elif fat:
        s.append('<div class="verdict %s"><b>Fatigue on the ankle — %s.</b> %s</div>' % ("warn" if fat["verdict"] != "PASS" else "", esc(fat["verdict"]), esc(fat["why"])))
    if conv:
        s.append('<div class="verdict %s"><b>Mesh convergence (ankle, drop) — %s.</b> %s</div>' % ("warn" if conv["verdict"] != "PASS" else "", esc(conv["verdict"]), esc(conv["why"])))
    if meshab:
        s.append('<div class="verdict warn"><b>Thigh housing — CANNOT DETERMINE.</b> %s</div>' % esc(meshab["why"]))
    if worst_disk:
        s.append('<p class="note">Worst linear safety factor anywhere on disk: <code>%s</code> %s, SF %s (%s). Nothing in this document hides behind a grade: every CANNOT DETERMINE above prints its number.</p>' % (
            esc(worst_disk["part"]), esc(CASE_LABEL.get(worst_disk["case"], worst_disk["case"])), f(sf_used(worst_disk)), esc(worst_disk["verdict"])))
    s.append('</section>')
    return "\n".join(s)


def sec_loads(L, drop):
    if not L:
        return '<section id="loads"><h2><span class="n">2</span>Load basis</h2><p>out/sim-evidence/loads_mujoco.json missing.</p></section>'
    w, st, m = L["walk"], L["stand"], L["model"]
    s = ['<section id="loads"><h2><span class="n">2</span>Load basis — measured in MuJoCo, not assumed</h2>',
         '<p class="lede">Pollen\'s MJCF (<code>%s</code>, %s kg from the <code>&lt;inertial&gt;</code> masses, weight %s N) driven by Pollen\'s '
         '<code>%s</code> exactly as <code>sim/run_policy.py</code> drives it (50 Hz, 4 × 0.005 s), for %s s at v<sub>x</sub> = %s m/s. '
         'Ground reaction per foot from <code>mj_contactForce</code> on every physics step; the force each body transmits to its parent from '
         '<code>cfrc_int</code>; every vector re-expressed in each part\'s own mesh frame through MuJoCo\'s <code>mesh_pos/mesh_quat</code> '
         '(verified on the sole: file point (50, 15, −31.0) mm lands on the floor at z = 0.002 m). Script: <code>%s</code>.</p>' % (
             esc(m["robot_walk"]), f(m["mass_kg_from_mjcf_inertials"], 6), f(m["weight_N"], 4), esc(w["policy_file"]), w["seconds"], w["vx_cmd_m_s"], esc(L["script"]))]
    s.append('<div class="tw"><table class="data"><caption>Table 1. Ground reaction and gait, measured. Source: <code>out/sim-evidence/loads_mujoco.json</code>.</caption>'
             '<thead><tr><th>Quantity</th><th class="n">Value</th><th>Unit</th><th>Where</th></tr></thead><tbody>')
    rows = [("Standing, left foot vertical", st["left_foot_vertical_N"], "N", "stand.left_foot_vertical_N (mean of the last 0.5 s)"),
            ("Standing, right foot vertical", st["right_foot_vertical_N"], "N", "stand.right_foot_vertical_N"),
            ("Standing closure Σ GRF / weight", st["closure_pct"], "%", "stand.closure_pct"),
            ("Walk peak vertical GRF (one foot)", w["peak_vertical_grf_N"], "N", "walk.peak_vertical_grf_N at t = %s s, %s foot" % (w["peak_grf_time_s"], w["peak_foot"])),
            ("Walk peak GRF / weight", w["peak_grf_over_bodyweight"], "×", "walk.peak_grf_over_bodyweight"),
            ("Walk p99 vertical GRF", w["p99_vertical_grf_N"], "N", "walk.p99_vertical_grf_N"),
            ("Walk peak tangential GRF", w["peak_tangential_grf_N"], "N", "walk.peak_tangential_grf_N"),
            ("Trunk peak inertial acceleration (walk)", w.get("trunk_linear_acceleration", {}).get("peak_m_s2"), "m/s²", "walk.trunk_linear_acceleration.peak_m_s2"),
            ("Gait period (left touchdowns)", w["gait"]["period_s_mean"], "s", "walk.gait.period_s_mean (min %s, max %s, %d cycles)" % (w["gait"]["period_s_min"], w["gait"]["period_s_max"], w["gait"]["n_cycles"])),
            ("Stride per cycle", w["gait"]["stride_m_per_cycle"], "m", "walk.gait.stride_m_per_cycle"),
            ("Cycles per km", w["gait"]["cycles_per_km"], "1/km", "walk.gait.cycles_per_km"),
            ("Left stance fraction", w["gait"]["left_stance_fraction"], "", "walk.gait.left_stance_fraction (stance = GRF > %s N)" % w["gait"]["stance_threshold_N"])]
    if drop and drop["inputs"].get("stand_height_m"):
        rows.append(("Standing height (top of the robot, STAND keyframe)", drop["inputs"]["stand_height_m"]["stand_top_z_m"], "m", "drop_impact.json inputs.stand_height_m (%s)" % drop["inputs"]["stand_height_m"]["how"]))
    for name, v, u, where in rows:
        s.append('<tr><td>%s</td><td class="n">%s</td><td>%s</td><td><code>%s</code></td></tr>' % (esc(name), f(v, 4), esc(u), esc(where)))
    s.append('</tbody></table></div>')
    dfoot = next((d for d in L["drops"] if d["label"] == "drop_foot_rollm10_default_contact_dt5ms"), {})
    dhead = next((d for d in L["drops"] if d["label"] == "drop_head_default_contact_dt5ms"), {})
    s.append('<div class="tw"><table class="data"><caption>Table 2. Force each body transmits to its parent (|cfrc_int|, N) — the load on the part bridging that joint. '
             'Walk peaks inside the commanded window; foot drop = %s m onto the left foot (roll −10°); head drop = %s m onto the head; both at MuJoCo\'s default contact. '
             'The drop height is the lane brief\'s input (§6), not a requirement.</caption>'
             '<thead><tr><th>MJCF body</th><th>Part</th><th class="n">Walk peak</th><th class="n">Walk p99</th><th class="n">Walk mean</th><th class="n">Foot drop</th><th class="n">Head drop</th></tr></thead><tbody>' % (
                 f(dfoot.get("height_m"), 3), f(dhead.get("height_m"), 3)))
    partof = {"ankle_left": "ankle-left (+ foot, sole)", "leg": "shin", "upper_leg_left": "upper-leg-left (+ rigidity plate)", "hip_l": "hip-bracket",
              "yaw2roll": "yaw2roll", "bearing_roll": "bearing-roll (right hip yaw)", "neck": "neck-plate ×2", "neck_pitch": "neck-pitch-bracket",
              "yaw_roll_motion": "yaw-roll-motion", "jaw_soft": "motor-support (head)"}
    for b, pk in w["body_transmitted_force_peaks"].items():
        s.append('<tr><td><code>%s</code></td><td>%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (
            esc(b), esc(partof.get(b, "—")), f(pk["peak_force_N"], 4), f(pk["p99_force_N"], 4), f(pk["mean_force_N"], 4),
            f(dfoot.get("body_transmitted_force_max_N", {}).get(b, {}).get("magnitude"), 4), f(dhead.get("body_transmitted_force_max_N", {}).get(b, {}).get("magnitude"), 4)))
    s.append('</tbody></table></div>')
    s.append('<div class="tw"><table class="data"><caption>Table 3. Actuator torque per joint during the walk (N·m; MJCF actuator forcerange ±%s N·m).</caption>'
             '<thead><tr><th>Joint</th><th class="n">Peak |τ|</th><th class="n">p99 |τ|</th><th class="n">Saturated steps</th><th class="n">Peak speed rad/s</th></tr></thead><tbody>' % w["actuator_forcerange_Nm"][1])
    for j, v in w["peak_abs_torque_Nm"].items():
        s.append('<tr><td><code>%s</code></td><td class="n">%s</td><td class="n">%s</td><td class="n">%d</td><td class="n">%s</td></tr>' % (
            esc(j), f(v, 5), f(w["p99_abs_torque_Nm"][j], 5), w["torque_saturated_steps"][j], f(w["peak_joint_speed_rad_s"][j], 4)))
    s.append('</tbody></table></div>')
    s.append('<p class="note">Sign convention used by every FEA case: the load applied at a part\'s distal connectors is −cfrc_int of its body (the force the far side '
             'exerts on it); in stance the ankle\'s −cfrc_int reads (−5.94, −3.97, +20.83) N in the ankle frame where the ground reaction reads (−5.46, −4.02, +22.24) N — up.</p>')
    s.append('</section>')
    return "\n".join(s)


def caption_verdict(r):
    """the verdict painted on the PNG = report.json's verdict beside the deck (cecad.feaimage reads exactly that file)"""
    wd = os.path.join(REPO, (r.get("artifacts") or [""])[0])
    rp = os.path.join(wd, "report.json")
    if os.path.exists(rp):
        return json.load(open(rp)).get("verdict")
    return None


def sec_fea(feas):
    s = ['<section id="fea"><h2><span class="n">3</span>FEA — every structural part, every measured load</h2>',
         '<p class="lede">gmsh quadratic tetrahedra (C3D10) + CalculiX linear static, isotropic. Held and loaded patches are boundary faces of the '
         'solid at the named connectors (<code>cecad.stress.load_patch</code>). Two safety factors per case: against the ce-cad class table '
         '(PLA 50 MPa, TPU 25 MPa — untiered, and the table\'s own comment says every polymer "yield" there is an ultimate) and against the fetched '
         'datasheet (Prusament PLA 51 ± 3 MPa yield printed horizontal; NinjaFlex TPU 85A yield 4 MPa). "SF used" is the more conservative, or the nonlinear one '
         'when the linear solve left its regime (§3b). "Fails at" is the linear failure load: applied force × table SF. Regime: plate if t/mid ≤ 0.15; the linear '
         'solve is a prediction while δ ≤ t/2 (plate) and δ ≤ L/10 (any part). Script: <code>sim/stress_all.py</code>; grading <code>sim/fea_rejudge.py</code>.</p>',
         '<div class="tw"><table class="data"><caption>Table 4. Verdict and safety factors, all %d studies. Source: <code>out/sim-evidence/fea_&lt;part&gt;_&lt;case&gt;.json</code>.</caption>'
         '<thead><tr><th>Part</th><th>Case</th><th>Verdict</th><th class="n">|F| N</th><th>Mat.</th><th class="n">SF used</th><th class="n">SF table</th><th class="n">SF TDS</th><th class="n">SF across layers</th></tr></thead><tbody>' % len(feas)]
    for r in feas:
        o = r.get("outputs") or {}
        s.append('<tr><td><code>%s</code></td><td>%s</td><td>%s</td><td class="n">%s</td><td>%s</td><td class="n"><b>%s</b></td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (
            esc(r["part"].replace("part:microduck-", "")), esc(CASE_LABEL.get(r["case"], r["case"])), chip(r.get("verdict")), f(r["inputs"].get("force_magnitude_N"), 3), esc(r.get("material", "—")),
            f(sf_used(r)), f(o.get("sf")), f(o.get("sf_vs_tds_yield")), f(o.get("sf_vs_tds_interlayer_across_layers"))))
    s.append('</tbody></table></div>')
    s.append('<div class="tw"><table class="data"><caption>Table 4a. Peak stress, deflection, regime and the linear failure load, same studies.</caption>'
             '<thead><tr><th>Part</th><th>Case</th><th class="n">σ<sub>vM</sub> MPa</th><th class="n">δ mm</th><th>Regime (plate? d/t, d/L)</th><th>Model graded</th><th class="n">Fails at N</th></tr></thead><tbody>')
    for r in feas:
        o = r.get("outputs") or {}
        reg = regime_of(r)
        gr = o.get("grading") or {}
        regtxt = "—"
        if reg.get("linear_regime_valid") is True:
            regtxt = "inside (%s, %s, %s)" % ("plate" if reg.get("plate") else "member", f(reg.get("d_over_t"), 3), f(reg.get("d_over_L"), 4))
        elif reg.get("linear_regime_valid") is False:
            regtxt = "OUTSIDE (%s, %s, %s)" % ("plate" if reg.get("plate") else "member", f(reg.get("d_over_t"), 3), f(reg.get("d_over_L"), 4))
        s.append('<tr><td><code>%s</code></td><td>%s</td><td class="n">%s</td><td class="n">%s</td><td>%s</td><td>%s</td><td class="n">%s</td></tr>' % (
            esc(r["part"].replace("part:microduck-", "")), esc(CASE_LABEL.get(r["case"], r["case"])), f(o.get("max_von_mises_mpa")), f(o.get("max_displacement_mm"), 4), regtxt,
            esc(gr.get("model", "linear")) if o.get("sf") is not None else "—", f(o.get("failure_load_N_linear"), 1)))
    s.append('</tbody></table></div>')
    s.append('<p class="note">Right-hand parts (ankle-right, foot-right, sole-right, upper-leg-right) are measured mirrors of the left (p95 0.000–0.002 mm, '
             'each part.py header) and inherit these verdicts. The hip bracket is one part used on both sides. The head-drop case exists only on the neck chain: '
             'the leg parts see the head drop as a body in free fall, and the load path of the impact is the head shell → motor support → neck stack → trunk.</p>')
    s.append('<h3>The fields, each beside the real joint</h3>')
    for r in feas:
        img = next((a for a in r.get("artifacts", []) if a.endswith(".png")), None)
        if not img:
            continue
        slug = slug_of(r)
        ref = REF_PHOTO.get(slug)
        o = r.get("outputs") or {}
        mesh = o.get("mesh") or {}
        s.append('<h4 style="margin-bottom:2px">%s — %s</h4><p class="paircap">|F| = %s N in the part frame %s · SF used %s · σ<sub>vM</sub> %s MPa · δ %s mm · mesh %s mm, %s nodes (%s) · %s</p>' % (
            esc(slug), esc(CASE_LABEL.get(r["case"], r["case"])), f(r["inputs"].get("force_magnitude_N"), 3), esc(r["inputs"].get("force_N_part_frame")), f(sf_used(r)),
            f(o.get("max_von_mises_mpa")), f(o.get("max_displacement_mm"), 4), f(mesh.get("size"), 2), mesh.get("nodes", "—"), esc(mesh.get("strategy", "—")), chip(r.get("verdict"))))
        s.append('<p class="paircap">%s</p>' % esc(r.get("why", "")))
        s.append('<div class="pair">')
        if ref and os.path.exists(os.path.join(REPO, ref[0])):
            s.append('<figure><span class="tag">Real · pollen-robotics.com</span><img src="%s" alt="%s real"><figcaption>%s</figcaption></figure>' % (esc(ref[0]), esc(slug), esc(ref[1])))
        else:
            s.append('<figure><span class="tag">Real</span><figcaption>no product photograph shows this part (it is inside the trunk shell)</figcaption></figure>')
        looked = (r.get("looked_at") or [{}])[0].get("facts", {})
        s.append('<figure><span class="tag ours">Ours · von Mises field</span><img src="%s" alt="%s %s FEA"><figcaption>%s; read back: %s × %s px, %s distinct colours, foreground %.1f %%; caption verdict %s</figcaption></figure>' % (
            esc(img), esc(slug), esc(r["case"]), esc(r["inputs"].get("why", "")), looked.get("size", ["?", "?"])[0], looked.get("size", ["?", "?"])[1],
            looked.get("distinct_colors", "?"), 100 * looked.get("foreground_frac", 0), esc(caption_verdict(r))))
        s.append('</div>')
        assum = [a for a in o.get("assumptions", []) if "patch" in a][:4]
        if assum:
            s.append('<p class="note">Patches: %s</p>' % esc(" · ".join(assum)))
    s.append('</section>')
    return "\n".join(s)


def sec_nlgeom(nls):
    s = ['<section id="nlgeom"><h2><span class="n">3b</span>Geometrically nonlinear re-solves — where the linear answer left its regime</h2>',
         '<p class="lede">Five linear studies deflect far beyond the small-deflection assumption (Table 4, "OUTSIDE"). A linear peak there is a bound, not a prediction, so '
         '<code>sim/fea_nlgeom.py</code> re-runs the IDENTICAL deck (mesh, held nodes, nodal loads, E/ν) with CalculiX <code>*STEP, NLGEOM</code>: the stiffness is '
         'updated on the deformed shape and the load ramped in increments. The material stays linear-elastic, so this isolates the geometric effect; a peak still past '
         'yield is still a failure. A solve that does not reach the full load is CANNOT DETERMINE with the fraction it reached — never a number at a load it did not carry.</p>']
    if not nls:
        s.append('<p>No nonlinear re-solve on disk yet (the chain runs one CalculiX job at a time; each takes 20–60 min on this shared machine). Until it lands, every '
                 '"OUTSIDE" row in Table 4 is graded on its linear bound and says so.</p></section>')
        return "\n".join(s)
    s.append('<div class="tw"><table class="data"><caption>Table 4b. Linear vs geometrically nonlinear peak stress, same deck. Source: <code>out/sim-evidence/fea_nlgeom_*.json</code>.</caption>'
             '<thead><tr><th>Part</th><th>Case</th><th>Verdict</th><th class="n">|F| N</th><th class="n">σ<sub>vM</sub> linear MPa</th><th class="n">σ<sub>vM</sub> nonlinear MPa</th><th class="n">ratio</th><th class="n">SF nonlinear</th></tr></thead><tbody>')
    for r in nls:
        i, o = r["inputs"], r["outputs"]
        lin = i["linear"]
        s.append('<tr><td><code>%s</code></td><td>%s</td><td>%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (
            esc(r["part"].replace("part:microduck-", "")), esc(CASE_LABEL.get(r["case"], r["case"])), chip(r["verdict"]), f(i["force_magnitude_N"], 3),
            f(lin["max_von_mises_mpa"]), f(o.get("max_von_mises_mpa")), f(o.get("ratio_nonlinear_over_linear_vm")), f(o.get("sf"))))
    s.append('</tbody></table></div>')
    s.append('<div class="tw"><table class="data"><caption>Table 4c. The same re-solves: load reached, increments, deflection, wall time.</caption>'
             '<thead><tr><th>Part</th><th>Case</th><th class="n">Load reached</th><th class="n">Incr.</th><th class="n">δ linear mm</th><th class="n">δ nonlinear mm</th><th class="n">s</th></tr></thead><tbody>')
    for r in nls:
        i, o = r["inputs"], r["outputs"]
        lin = i["linear"]
        s.append('<tr><td><code>%s</code></td><td>%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (
            esc(r["part"].replace("part:microduck-", "")), esc(CASE_LABEL.get(r["case"], r["case"])), f(o.get("load_fraction_reached"), 3), o.get("increments", "—"),
            f(lin["max_displacement_mm"], 4), f(o.get("max_displacement_mm"), 4), o.get("seconds", "—")))
    s.append('</tbody></table></div>')
    for r in nls:
        s.append('<p class="note"><code>%s</code> %s: %s</p>' % (esc(r["part"]), esc(r["case"]), esc(r["why"])))
    s.append('</section>')
    return "\n".join(s)


def sec_matrix(M):
    if not M:
        return ""
    s = ['<section id="matrix"><h2><span class="n">4</span>The detached load matrix (20 / 60 / 15 N), consumed</h2>',
         '<p class="lede">The night-shift matrix <code>sim/stress_matrix.py</code> → <code>out/stress/matrix.json</code> ran 4 parts × 3 ROUND load cases '
         '(standing 20 N, landing 60 N, lateral 15 N) in PLA with the plate mesh heuristic (element = thinnest bbox side / 3). It is kept as history; '
         'its ankle case held <code>bearing_seat</code> and loaded <code>horn_face</code> — both on the same axle — which is the connector-name bug of '
         '<code>stress_evidence.py</code> and not a load path. §3 re-declares that part through bearing + horn → foot screw + hull seat.</p>',
         '<div class="tw"><table class="data"><caption>Table 5. out/stress/matrix.json (%s).</caption>'
         '<thead><tr><th>Part</th><th>Case</th><th class="n">F N</th><th class="n">SF</th><th class="n">σ<sub>vM</sub> MPa</th><th class="n">δ mm</th><th>Verdict</th></tr></thead><tbody>' % esc(M.get("tool", ""))]
    for r in M["results"]:
        s.append('<tr><td><code>%s</code></td><td>%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td>%s</td></tr>' % (
            esc(r["part"].replace("microduck-", "")), esc(r["case"]), esc(r["force_N"]), f(r.get("sf")), f(r.get("max_vm")), f(r.get("max_disp"), 4), chip(r.get("verdict"))))
    s.append('</tbody></table></div>')
    if M.get("material_sweep"):
        s.append('<p class="note">Material sweep on its governing case (%s / %s, 60 N): %s. Its mesh-convergence rows all came back CANNOT DETERMINE (no reason recorded) — '
                 'redone in §5.</p>' % (esc(M["governing"]["part"]), esc(M["governing"]["case"]),
                                          esc(", ".join("%s SF %s %s" % (x["material"], f(x["sf"]), x["verdict"]) for x in M["material_sweep"]))))
    s.append('</section>')
    return "\n".join(s)


def sec_conv(conv, mats):
    s = ['<section id="conv"><h2><span class="n">5</span>Mesh convergence and material trade — ankle, landing</h2>']
    if conv:
        s.append('<p class="lede">%s</p>' % esc(conv["method"]))
        s.append('<div class="tw"><table class="data"><caption>Table 6. SF vs mesh size — %s. %s</caption>'
                 '<thead><tr><th class="n">Size mm</th><th class="n">Nodes</th><th class="n">Elements</th><th class="n">SF</th><th class="n">σ<sub>vM</sub> MPa</th><th class="n">δ mm</th><th class="n">s</th><th>Verdict</th></tr></thead><tbody>' % (
                     chip(conv["verdict"]), esc(conv["why"])))
        for r in conv["outputs"]["rows"]:
            s.append('<tr><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td>%s</td></tr>' % (
                f(r.get("size_used_mm"), 3), r.get("nodes", "—"), r.get("elements", "—"), f(r.get("sf")), f(r.get("max_von_mises_mpa")), f(r.get("max_displacement_mm"), 4), r.get("seconds", "—"), chip(r.get("verdict"))))
        s.append('</tbody></table></div>')
        imgs = [r["image"] for r in conv["outputs"]["rows"] if r.get("image")]
        if imgs:
            s.append('<div class="pair">' + "".join('<figure><span class="tag ours">Ours · size %s mm</span><img src="%s" alt="convergence"></figure>' % (
                f(r.get("size_used_mm"), 2), esc(r["image"])) for r in conv["outputs"]["rows"] if r.get("image")) + '</div>')
    else:
        s.append('<p>Convergence study not yet on disk (<code>out/sim-evidence/fea_convergence_microduck-ankle-left_drop.json</code>).</p>')
    if mats:
        s.append('<h3>Material trade on the same load</h3><p class="lede">%s — %s %s</p>' % (esc(mats["method"]), chip(mats["verdict"]), esc(mats["why"])))
        cands = (mats.get("outputs") or {}).get("candidates", [])
        if cands:
            s.append('<div class="tw"><table class="data"><caption>Table 7. Candidates (class-table strength, accepted by the caller).</caption>'
                     '<thead><tr><th>Material</th><th class="n">Yield MPa</th><th class="n">E GPa</th><th class="n">SF</th><th class="n">σ<sub>vM</sub> MPa</th><th class="n">δ mm</th><th class="n">Mass g</th><th>Verdict</th></tr></thead><tbody>')
            for c in cands:
                s.append('<tr><td>%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td>%s</td></tr>' % (
                    esc(c.get("material")), f(c.get("yield_mpa"), 0), f(c.get("youngs_gpa"), 2), f(c.get("sf")), f(c.get("max_vm")), f(c.get("max_disp"), 4), f(c.get("mass_g"), 3), chip(c.get("verdict"))))
            s.append('</tbody></table></div>')
    s.append('</section>')
    return "\n".join(s)


def sec_buckling():
    studies = buckling_studies()
    if not studies:
        return ""
    s = ['<section id="buckling"><h2><span class="n">5b</span>Buckling and first mode — the slender members</h2>',
         '<p class="lede">Yield is one way a part fails; a 58 mm shin or a 1 mm plate under the landing load can fold first. ce-struct (voxel hex mesh + CalculiX '
         '*BUCKLE / *FREQUENCY, :8099) on our rebuilt meshes, the member held at one end and loaded over the other with the measured landing force — solved with the '
         'measured AXIAL component alone and with the FULL measured vector, at each of several cell sizes; the factor\'s drift between the two finest cells, the '
         'separation of the three lowest eigen-factors (three within 1 % = a local end-face mode) and, for the shin, an Euler bracket from the section properties read '
         'off the mesh (<code>sim/member_section.py</code>) decide whether the number is a member mode at all. Script <code>sim/struct_ce.py</code>. ce-struct rule: '
         'load factor ≥ 2 PASS. The first version (2026-09-02) applied the force MAGNITUDE as axial — a 20 % error on the shin, found by the skeptic and superseded here.</p>',
         '<div class="tw"><table class="data"><caption>Table 7b. Buckling load factor per cell size and load, and natural frequencies. Source: <code>out/sim-evidence/buckling_&lt;part&gt;.json</code>.</caption>'
         '<thead><tr><th>Part</th><th class="n">Cell mm</th><th>Load</th><th class="n">Cells</th><th class="n">Factor 1</th><th class="n">Factors 2, 3</th><th class="n">f₁ Hz</th><th>Verdict</th></tr></thead><tbody>']
    for r in studies:
        i, o = r["inputs"], r.get("outputs") or {}
        rows = o.get("rows")
        if rows:
            for k, row in enumerate(rows):
                facs = row.get("factors") or []
                s.append('<tr><td><code>%s</code></td><td class="n">%s</td><td>%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td>%s</td></tr>' % (
                    esc(r["part"].replace("part:microduck-", "")) if k == 0 else "",
                    row["cell_mm"], esc(row["load"]), row.get("cells", "—"), f(facs[0], 4) if facs else esc(row.get("error", "—")), ", ".join(f(x, 3) for x in facs[1:3]) if len(facs) > 1 else "—",
                    f(row.get("first_mode_hz"), 2), chip(r["verdict"]) if k == len(rows) - 1 else ""))
        elif not o:
            s.append('<tr><td><code>%s</code></td><td class="n">—</td><td>no solve</td><td class="n">—</td><td class="n">—</td><td class="n">—</td><td class="n">—</td><td>%s</td></tr>' % (
                esc(r["part"].replace("part:microduck-", "")), chip(r["verdict"])))
        else:
            b = o.get("buckle") or {}
            facs = b.get("factors") or []
            s.append('<tr><td><code>%s</code></td><td class="n">%s</td><td>magnitude as axial (v1)</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td>%s</td></tr>' % (
                esc(r["part"].replace("part:microduck-", "")), i["cell_mm"], b.get("cells", "—"),
                f(facs[0], 4) if facs else "—", ", ".join(f(x, 3) for x in facs[1:3]) if len(facs) > 1 else "—", f(o.get("first_mode_hz"), 2), chip(r["verdict"])))
    s.append('</tbody></table></div>')
    for r in studies:
        i = r["inputs"]
        if "long_axis" not in i:
            continue
        s.append('<p class="note"><code>%s</code> inputs: |F| %s N%s, axis %s, held %s, loaded %s, mesh <code>%s</code>, %s, print normal %s. Source: %s</p>' % (
            esc(r["part"].replace("part:", "")), f(i.get("force_magnitude_N", i.get("force_N")), 4),
            (", axial component %s N (%s)" % (f(i["axial_component_N"], 4), "compressive" if i.get("axial_is_compressive") else "tensile")) if "axial_component_N" in i else " (magnitude applied as axial — v1)",
            esc(i["long_axis"]), esc(i["held_face"]), esc(i["loaded_face"]), esc(i["mesh"]), esc(i["material"]), esc(i["printNormal_ASSUMED"]), esc(i["force_source"])))
    for r in studies:
        s.append('<p class="note"><code>%s</code> %s: %s</p>' % (esc(r["part"]), chip(r["verdict"]), esc(r["why"])))
        e = (r.get("outputs") or {}).get("euler_crosscheck")
        if e:
            s.append('<p class="note">Euler cross-check (<code>%s</code>): weakest station I<sub>min</sub> %s mm⁴; P<sub>cr</sub> = π²EI/(KL)² with E 3500 MPa: K = 2 (fixed-free) %s N, K = 1 %s N, K = 0.7 %s N; '
                     'the eigen-solver\'s critical axial load %s N is %s the bracket. %s</p>' % (
                         esc(e["section_study"]), f(e["I_min_mm4_weakest"], 4), f(e["euler_N_K2_fixed_free"], 2), f(e["euler_N_K1_pinned"], 2), f(e["euler_N_K0.7_fixed_pinned"], 2),
                         f(e["eigen_axial_critical_N"], 2), "INSIDE" if e["inside_bracket"] else "OUTSIDE", esc(e["note"])))
    s.append('<p class="note">Print normal assumed = the thickness axis (printed flat) for the material table; no part.py declares it. The plate&#39;s &quot;load over the end face&quot; is a bounding idealisation of four screws.</p>')
    s.append('</section>')
    return "\n".join(s)


def sec_drop(D):
    if not D:
        return '<section id="drop"><h2><span class="n">6</span>Drop / impact</h2><p>out/sim-evidence/drop_impact.json missing.</p></section>'
    o, i = D["outputs"], D["inputs"]
    s = ['<section id="drop"><h2><span class="n">6</span>Drop / impact — %s m onto one foot and onto the head</h2>' % f(i["height_m"], 3),
         '<p class="lede">Energy %s J (m %s kg × g × %s m), impact speed %s m/s, momentum %s N·s. Three models, compared; the disagreement is the finding. %s %s</p>' % (
             f(o["energy_J"], 5), f(i["mass_kg"], 6), f(i["height_m"], 3), f(o["impact_speed_m_s"], 5), f(o["momentum_Ns"], 5), chip(D["verdict"]), esc(D["why"]))]
    s.append('<div class="verdict"><b>Where the height comes from.</b> %s Measured for scale: the robot stands %s m tall in the STAND keyframe (%s), so %s m is %s of its own height — '
             'roughly the fall of the head in a tip-over, or a hand-height drop onto a desk. Table 8a says how every figure here scales if a requirement names a different height.</div>' % (
                 esc(i.get("height_source", "no source recorded")), f(i.get("stand_height_m", {}).get("stand_top_z_m"), 5), esc(i.get("stand_height_m", {}).get("how", "")),
                 f(i["height_m"], 3), f(i.get("stand_height_m", {}).get("ratio_H_over_stand_height"), 3)))
    if i.get("height_sensitivity"):
        s.append('<div class="tw"><table class="data"><caption>Table 8a. Height sensitivity (closed form). Energy ∝ h; impact speed and the rigid-spring peak (model A) ∝ √h; the Hertz peak (model B) ∝ h<sup>3/5</sup>; '
                 'linear FEA stress ∝ force. MuJoCo\'s default contact (model C) is not a linear spring and needs a re-run at the new height.</caption>'
                 '<thead><tr><th class="n">h m</th><th class="n">energy ×</th><th class="n">speed ×</th><th class="n">model A force ×</th><th class="n">model B force ×</th></tr></thead><tbody>')
        for row in i["height_sensitivity"]:
            s.append('<tr><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (
                f(row["height_m"], 3), f(row["energy_ratio"], 4), f(row["speed_ratio"], 4), f(row["model_A_force_ratio"], 4), f(row["model_B_hertz_force_ratio"], 4)))
        s.append('</tbody></table></div>')
        s.append('<p class="note">Heights: %s.</p>' % esc("; ".join("%.3f m — %s" % (row["height_m"], row["what_it_is"]) for row in i["height_sensitivity"])))
    s.append('<div class="tw"><table class="data"><caption>Table 8. Peak contact force by model. A: rigid body on a linear spring, F = v√(Km). B: Hertz on the struck curvature with the bottoming-out check. C: MuJoCo (solref, timestep).</caption>'
             '<thead><tr><th>Model</th><th>Case</th><th class="n">K N/m · E* MPa · solref</th><th class="n">δ mm</th><th class="n">F peak N</th><th class="n">Impulse N·s</th></tr></thead><tbody>')
    notes = []
    for k, v in o["model_A_rigid_spring"].items():
        s.append('<tr><td>A rigid-spring</td><td><code>%s</code></td><td class="n">%s</td><td class="n">—</td><td class="n">%s</td><td class="n">—</td></tr>' % (
            esc(k), f(v.get("K_N_per_m"), 0), f(v.get("F_peak_N"), 1)))
        if "patch_mm2_ASSUMED" in v:
            notes.append("%s: first-contact patch %s mm² ASSUMED (through-thickness of the %s mm apex wall)" % (k, v["patch_mm2_ASSUMED"], f(i["head_shell"]["apex_wall_thickness_mm"], 3)))
        if v.get("why"):
            notes.append("%s: %s" % (k, v["why"]))
    for k, v in o["model_B_hertz"].items():
        s.append('<tr><td>B Hertz</td><td><code>%s</code></td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">—</td></tr>' % (
            esc(k), f(v.get("E_star_MPa"), 2), f(v.get("delta_mm"), 3), f(v.get("F_peak_N"), 1)))
        notes.append("%s: %s" % (k, v.get("note") or v.get("why", "")))
    for k, v in o["model_C_mujoco"].items():
        s.append('<tr><td>C MuJoCo</td><td><code>%s</code></td><td class="n">%s</td><td class="n">—</td><td class="n">%s</td><td class="n">%s</td></tr>' % (
            esc(k), esc("default 0.02 s / 1" if isinstance(v["solref"], str) else "%.3g s / %g" % (v["solref"][0], v["solref"][1])) + " · Δt %g s" % v["timestep_s"],
            f(v["peak_normal_force_N"], 2), f(v["impulse_Ns"], 4)))
        notes.append("%s: struck %s, peak knee torque %s N·m, saturated steps %d" % (k, v["struck"], f(v["peak_knee_torque_Nm"], 4), v["knee_saturated_steps"]))
    s.append('</tbody></table></div>')
    s.append('<ul class="note">' + "".join('<li><code>%s</code> %s</li>' % (esc(n.split(":", 1)[0]), esc(n.split(":", 1)[1])) for n in notes) + '</ul>')
    s.append('<p class="note"><b>Cross-check A vs C:</b> same K, analytic %s N vs MuJoCo %s N (ratio %s) — %s. <b>Joint cap:</b> %s. <b>MuJoCo\'s default contact</b> is equivalent to %s N/m — %s. '
             '<b>Head shell measured:</b> apex wall %s mm; %s. <b>What settles it:</b> %s</p>' % (
                 f(o["cross_check_A_vs_C_stiff"]["analytic_F_N"], 0), f(o["cross_check_A_vs_C_stiff"]["mujoco_stiff_F_N"], 0), f(o["cross_check_A_vs_C_stiff"]["ratio"], 3),
                 esc(o["cross_check_A_vs_C_stiff"]["note"]), esc(o["joint_torque_cap"]["finding"]), f(i["mujoco_default_contact"]["equivalent_stiffness_N_per_m"], 0),
                 esc(i["mujoco_default_contact"]["note"]), f(i["head_shell"]["apex_wall_thickness_mm"], 3),
                 esc("sphere fit rms %s mm on the apex cap (not spherical: no Hertz radius)" % f(i["head_shell"]["sphere_fit_rms_mm"], 3)), esc(D["what_settles_it"])))
    s.append('</section>')
    return "\n".join(s)


def sec_fatigue(F, FW):
    s = ['<section id="fatigue"><h2><span class="n">7</span>Fatigue under the walking cycle — every part, then the ankle in detail</h2>']
    if FW:
        i, o = FW["inputs"], FW["outputs"]
        s.append('<p class="lede">%s %s</p>' % (chip(FW["verdict"]), esc(FW["why"])))
        s.append('<p>S-N basis: %s (<code>%s</code>, sha256 <code>%s…</code>). Design curve %s; median estimate %s. Cycles per km %s (period %s s, stride %s m, %s cycles measured). '
                 'Stress: %s. Threshold: %s km — %s. The first version of this section checked the ankle alone; the F1 skeptic applied the same curve to every walk study and found eight over '
                 'the limit — this table is that check, made permanent.</p>' % (
                     esc(i["sn_curve"]["paper"]), esc(i["sn_curve"]["file"]), esc(i["sn_curve"]["sha256"][:16]), esc(i["sn_curve"]["design_curve"]), esc(i["median_R0"]["source"]),
                     f(i["gait"]["cycles_per_km"], 1), i["gait"]["period_s_mean"], i["gait"]["stride_m_per_cycle"], i["gait"]["n_cycles_measured"], esc(i["stress_basis"]),
                     f(i["life_km_required"]["value"], 0), esc(i["life_km_required"]["source"])))
        s.append('<div class="tw"><table class="data"><caption>Table 9. Design life per part (P<sub>s</sub> ≥ 90 % curve on the least favourable UTS basis; P<sub>s</sub> 50 % median R = 0 curve beside it). Source: <code>out/sim-evidence/fatigue_walk.json</code>.</caption>'
                 '<thead><tr><th>Part</th><th>Verdict</th><th class="n">σ<sub>max</sub> MPa</th><th class="n">Endurance MPa</th><th class="n">σ<sub>max</sub> / limit</th><th class="n">Life km (P<sub>s</sub>≥90 %)</th><th class="n">Life km (median)</th></tr></thead><tbody>')
        for r in o["rows"]:
            has = bool(r.get("curves"))
            s.append('<tr><td><code>%s</code></td><td>%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (
                esc(r["part"].replace("part:microduck-", "")), chip(r["verdict"]), f(r.get("sigma_max_mpa"), 4), f(r.get("design_endurance_mpa_worst"), 2),
                f(r.get("sigma_over_endurance_worst"), 3), ("∞" if has and r.get("life_km_design_Ps90_worst") is None else g(r.get("life_km_design_Ps90_worst"))),
                ("∞" if has and r.get("life_km_Ps50") is None else g(r.get("life_km_Ps50")))))
        s.append('</tbody></table></div>')
        s.append('<div class="tw"><table class="data"><caption>Table 9a. The walk load and static verdict each fatigue row rests on.</caption>'
                 '<thead><tr><th>Part</th><th class="n">|F| walk N</th><th>Material</th><th>Static walk verdict</th><th class="n">Static SF</th><th>Walk study</th></tr></thead><tbody>')
        for r in o["rows"]:
            s.append('<tr><td><code>%s</code></td><td class="n">%s</td><td>%s</td><td>%s</td><td class="n">%s</td><td><code>%s</code></td></tr>' % (
                esc(r["part"].replace("part:microduck-", "")), f(r.get("force_N"), 4), esc(r.get("material") or "—"), chip(r.get("static_verdict")), f(r.get("static_sf")), esc(os.path.basename(r["walk_study"]))))
        s.append('</tbody></table></div>')
        s.append('<ul class="note">' + "".join('<li><code>%s</code>: %s%s</li>' % (esc(r["part"].replace("part:", "")), esc(r["why"]), (" What settles it: %s" % esc(r["what_settles_it"])) if r.get("what_settles_it") else "") for r in o["rows"]) + '</ul>')
        s.append('<p class="note">Limits: %s. What settles it: %s</p>' % (esc("; ".join(FW["limits"])), esc(FW["what_settles_it"])))
    if F:
        i, o = F["inputs"], F["outputs"]
        s.append('<h3>The ankle in detail (with the mesh-scaled peak)</h3><p class="lede">%s %s</p>' % (chip(F["verdict"]), esc(F["why"])))
        s.append('<div class="tw"><table class="data"><caption>Table 9b. Ankle life by basis. σ<sub>max</sub> from the walk-peak FEA (%s N). Load ratio %s. Source: <code>out/sim-evidence/fatigue_ankle.json</code>.</caption>'
                 '<thead><tr><th>UTS basis</th><th class="n">UTS MPa</th><th>Stress</th><th class="n">σ<sub>max</sub> MPa</th><th class="n">Endurance MPa</th><th class="n">σ / limit</th><th class="n">N</th><th class="n">Life km</th></tr></thead><tbody>' % (
                     f(i["stress"]["force_N"], 4), esc(i["stress"]["load_ratio_R"])))
        for c in o["curves"]:
            s.append('<tr><td>%s</td><td class="n">%s</td><td>%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (
                esc(c["uts_basis"].replace("prusament_tds", "TDS").replace("paper_theta0", "paper")), f(c["uts_mpa"], 1), esc(c["stress_basis"].replace("fea_peak_mesh_scaled", "mesh-scaled").replace("fea_peak", "FEA peak")), f(c["sigma_max_mpa"], 4), f(c["design_endurance_sigma_max_2e6_mpa"], 3), f(1 / c["endurance_margin"] if c["endurance_margin"] else None, 3),
                esc(str(c["cycles_to_failure_design_Ps90"]).replace("> 2e6 (below the design endurance limit)", "> 2·10⁶")), esc(str(c["life_km_design_Ps90"]).replace("infinite by the design curve", "∞ (design curve)"))))
        s.append('</tbody></table></div>')
        s.append('<p class="note">Table 1 of the paper (θ<sub>p</sub> = 0°, UTS 42.6 MPa): median endurance amplitude at 2·10⁶ cycles, R = −1: 10.4 MPa, R = 0: 6.1 MPa (σ<sub>max</sub> 12.2 MPa). '
                 'Limits: %s. What settles it: %s</p>' % (esc("; ".join(F["limits"])), esc(F["what_settles_it"])))
    if not F and not FW:
        s.append('<p>No fatigue study on disk (out/sim-evidence/fatigue_walk.json, fatigue_ankle.json).</p>')
    s.append('</section>')
    return "\n".join(s)


def sec_material(feas):
    tds = next((r["inputs"].get("tds") for r in feas if r["inputs"].get("tds") and r.get("material") == "PLA"), None)
    tdst = next((r["inputs"].get("tds") for r in feas if r["inputs"].get("tds") and r.get("material") == "TPU"), None)
    s = ['<section id="material"><h2><span class="n">8</span>Material, regime and print-orientation assumptions</h2><ul>',
         '<li><b>Solver model.</b> Linear elastic, isotropic, small strain; Poisson from <code>cecad.materials.poisson_for</code> (PLA 0.36, TPU 0.48). No plasticity, no creep, no rate effects. '
         'Small strain is CHECKED, not assumed: every study\'s deflection is held against its own deck\'s bbox (plate if t/mid ≤ 0.15; valid while δ ≤ t/2 for a plate and δ ≤ L/10 for any part — '
         'the small-deflection assumptions of Timoshenko &amp; Woinowsky-Krieger\'s plate theory and the small-rotation assumption of beam theory, the fractions being the customary ones), and a study '
         'outside that regime is re-solved with NLGEOM (§3b) — its linear number stays printed as a bound.</li>',
         '<li><b>Class table.</b> <code>ce-cad/cecad/fits.py MATERIALS</code>: PLA 1.24 g/cm³, "yield" 50 MPa, E 3.5 GPa; TPU 1.21, 25 MPa, 0.026 GPa. The table\'s own comment: no source, and every polymer row\'s yield is an ultimate. '
         'Verdicts against it are marked <em>tier = class, accepted by the caller</em> by cecad itself.</li>']
    if tds:
        s.append('<li><b>PLA datasheet, fetched.</b> %s — yield %s ± %s MPa, modulus %s GPa, interlayer adhesion %s ± %s MPa (%s). <code>%s</code> sha256 <code>%s…</code>. '
                 'The interlayer figure is the across-layer strength: a part loaded across its layers has %.0f %% of the in-plane strength, which is the "SF across layers" column of Table 4.</li>' % (
                     esc(tds["what"]), tds["yield_mpa"], tds["yield_tol"], tds["modulus_gpa"], tds["interlayer_mpa"], tds["interlayer_tol"], esc(tds["method"]), esc(tds["file"]), esc(tds["sha256"][:16]),
                     100.0 * tds["interlayer_mpa"] / tds["yield_mpa"]))
    if tdst:
        s.append('<li><b>TPU datasheet, fetched.</b> %s — yield %s MPa, ultimate %s MPa, modulus %s MPa (%s). <code>%s</code> sha256 <code>%s…</code>. The class table\'s 25 MPa is this ultimate; '
                 'the TDS yield is 6.25× lower and is what the TDS column of Table 4 uses.</li>' % (esc(tdst["what"]), tdst["yield_mpa"], tdst["ultimate_mpa"], tdst["modulus_mpa"], esc(tdst["method"]), esc(tdst["file"]), esc(tdst["sha256"][:16])))
    s.append('<li><b>Orientation.</b> Not modelled. No part.py declares a print-up direction (<code>printed.print_up()</code>), so which axis is the weak one is CANNOT DETERMINE per part; '
             'the across-layer column bounds it from below on every part at once. Ezeh &amp; Susmel 2019 found raster angle negligible for fatigue of flat-printed PLA — that is in-plane raster, not across-layer.</li>')
    s.append('<li><b>Load share.</b> Two parts (<code>sim/load_share.py</code>) carry their force in parallel with a body not in the model — the rigidity plate closes the thigh housing, the trunk base is clamped between the shells — '
             'and are solved at 100 % as a bound. Every other part is the sole member between its connectors, so its single-part solve is the load path. This distinction is a declared property of the study, '
             'applied by the same rule to all; its first application (commit d977b96) was written after those two parts\' numbers were known, which the skeptic rightly flagged — hence the rule now lives in one file and §1 prints the worst number on disk regardless of grade.</li>')
    s.append('<li><b>The fitted filament</b> is CANNOT DETERMINE (Pollen publishes "PLA" and "TPU", no brand): the TDS rows are the representative sheets for the class. A tensile coupon of the spool used, in the print orientation used, settles every SF here to a measurement.</li>')
    s.append('</ul></section>')
    return "\n".join(s)


def sec_open(feas, meshab, drop, fat, fatw, conv, nls):
    s = ['<section id="open"><h2><span class="n">9</span>What is still CANNOT DETERMINE, and what settles each</h2><div class="tw"><table class="data">'
         '<thead><tr><th>Item</th><th>Evidence so far</th><th>Best-supported option</th><th>What settles it</th></tr></thead><tbody>']
    if meshab:
        o = meshab["outputs"]
        s.append('<tr><td>Thigh housing FEA</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (esc(o["diagnosis"]), "leave the solid, break the arc-wall tangency in the rebuild (&lt; 0.05 mm)", esc(o["what_settles_it"])))
    if drop:
        s.append('<tr><td>Drop peak force</td><td>%s</td><td>use the MuJoCo default-contact peak as the stated lower bound and report each part\'s failure load beside it</td><td>%s</td></tr>' % (
            esc("bracket %s–%s N on the foot, %s–%s N on the head" % (f(drop["outputs"]["bracket_foot_N"]["lower_mujoco_default"], 0), f(drop["outputs"]["bracket_foot_N"]["upper_rigid_table"], 0),
                                                                    f(drop["outputs"]["bracket_head_N"]["lower_mujoco_default"], 0), f(drop["outputs"]["bracket_head_N"]["upper_rigid_table"], 0))), esc(drop["what_settles_it"])))
        s.append('<tr><td>Drop height as a requirement</td><td>%s</td><td>keep %s m as the studied case (≈ the robot\'s own height, %s m) and scale by Table 8a</td><td>a written drop requirement (height, surface, orientation, pass criterion) in docs/MANUFACTURING-REQUIREMENTS.md; then one MuJoCo re-run at that height</td></tr>' % (
            esc(drop["inputs"].get("height_source", "")), f(drop["inputs"]["height_m"], 3), f(drop["inputs"].get("stand_height_m", {}).get("stand_top_z_m"), 5)))
    for r in feas:
        why = r.get("why", "")
        if r.get("verdict") == "CANNOT DETERMINE" and not why.startswith("no tetrahedral mesh"):
            ls = ((r.get("outputs") or {}).get("grading") or {}).get("load_share") or {}
            settles = ls.get("what_settles_it") or ("what settles it" + why.split("settles it", 1)[1] if "settles it" in why else "see the study JSON")
            option = "state the bound (SF %s) and the unmeasured share; do not certify" % f(sf_used(r))
            s.append('<tr><td><code>%s</code> %s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (esc(r["part"].replace("part:", "")), esc(CASE_LABEL.get(r["case"], r["case"])), esc(why), esc(option), esc(settles)))
    pending = [r for r in feas if regime_of(r).get("linear_regime_valid") is False and not (nonlinear_of(r) or {}).get("sf_governing")]
    for r in pending:
        nl = nonlinear_of(r) or {}
        s.append('<tr><td><code>%s</code> %s — nonlinear number</td><td>linear δ %s mm is outside the regime (d/t %s, d/L %s); %s</td><td>grade on the linear bound (SF %s) and say so</td><td>the NLGEOM re-solve in sim/fea_nlgeom.py (queued, one ccx job at a time); if it cannot reach the full load, a material-nonlinear solve or a printed part on a bench</td></tr>' % (
            esc(r["part"].replace("part:", "")), esc(CASE_LABEL.get(r["case"], r["case"])), f(r["outputs"]["max_displacement_mm"], 4), f(regime_of(r).get("d_over_t"), 3), f(regime_of(r).get("d_over_L"), 4),
            esc(("nonlinear run: %s (%s)" % (nl.get("verdict"), nl.get("why", ""))) if nl else "no nonlinear run on disk yet"), f(sf_used(r))))
    for r in buckling_studies():
        if r["verdict"] == "CANNOT DETERMINE":
            s.append('<tr><td><code>%s</code> buckling</td><td>%s</td><td>no member buckling load reported</td><td>a shell/solid model loaded through the screw holes instead of the end face, or a printed plate compressed in a rig</td></tr>' % (
                esc(r["part"].replace("part:", "")), esc(r["why"])))
    if fatw:
        for r in fatw["outputs"]["rows"]:
            if r["verdict"] == "CANNOT DETERMINE":
                s.append('<tr><td><code>%s</code> fatigue</td><td>%s</td><td>—</td><td>%s</td></tr>' % (esc(r["part"].replace("part:", "")), esc(r["why"]), esc(r.get("what_settles_it", ""))))
    s.append('<tr><td>Fitted filament / print orientation</td><td>no brand published; no print_up declared</td><td>Prusament PLA + NinjaFlex 85A sheets as class representatives</td><td>coupons from the spool in the print orientation (ISO 527-1, 5 per orientation)</td></tr>')
    s.append('<tr><td>Battery mass</td><td>fitted pack CANNOT DETERMINE (part:np-f550); Duracell DR5 99 g used for the power-support load</td><td>99 g class figure</td><td>the label on a shipped pack</td></tr>')
    s.append('</tbody></table></div></section>')
    return "\n".join(s)


def sec_method():
    return ('<section id="method"><h2><span class="n">10</span>Method and honest limits</h2><ul>'
            '<li><b>Loads.</b> <code>sim/measure_loads.py</code>: stock physics of Pollen\'s MJCF (our meshes swap only the visuals; run_policy.py measured stock-vs-ours qpos identical), policy replayed at 50 Hz, contact forces and body interaction forces sampled at every 0.005 s physics step; drops at 0.005 s and 50 µs steps.</li>'
            '<li><b>FEA.</b> <code>sim/stress_all.py</code> over <code>cecad.stress</code>: gmsh C3D10 at a wall-aware size (clamp(thinnest bbox side / 3, 0.8, 1.5) mm — the plate heuristic alone put 8.5 mm elements on the ankle\'s 2.5 mm walls), CalculiX static, nodal von Mises peak. A peak at a re-entrant corner rises with refinement; §5 measures that on the governing case.</li>'
            '<li><b>Grading.</b> <code>sim/fea_rejudge.py</code>: one rule, every study, re-runnable without the kernel; report.json beside each deck is synced to the final verdict so the picture\'s caption and the table cannot disagree. <code>sim/fea_nlgeom.py</code> re-solves the out-of-regime studies with NLGEOM on the identical deck.</li>'
            '<li><b>Patches.</b> Held and loaded regions are boundary faces near the named connector (whole feature for axial kinds, four element faces otherwise) — cecad records each as an assumption and it is quoted under every figure. A connector that sits on an axis loads the nearest skin, not a contact that was measured.</li>'
            '<li><b>Pictures.</b> <code>cecad.feaimage</code> renders the .frd the verdict came from and refuses if the recomputed peak differs from the report by more than 0.5 %; every PNG is read back (size, colours, foreground fraction) and the facts are printed under it, with the caption verdict.</li>'
            '<li><b>Buckling / modal.</b> <code>sim/struct_ce.py</code> through ce-struct (:8099): voxel hex mesh at several cell sizes, CalculiX *BUCKLE (3 modes) and *FREQUENCY, axial component and full vector, on the three slender members; the load enters over an end face, which is an idealisation of screws. <code>sim/member_section.py</code> reads section properties off the mesh for the Euler bracket.</li>'
            '<li><b>Fatigue.</b> <code>sim/fatigue_walk.py</code> on every walk study and <code>sim/fatigue_ankle.py</code> on the ankle with its mesh-scaled peak; one cited S-N basis (Ezeh &amp; Susmel 2019).</li>'
            '<li><b>Self-check.</b> <code>tools/gen_structural.py selfcheck()</code> refuses to leave the page on disk if a study on disk is not published, a FAIL is missing from the FAIL list, a caption verdict differs from the table, an image is missing, a why is truncated, or a link targets a file that does not exist.</li>'
            '<li><b>Not done.</b> No physical part has been loaded. No contact solve, no plasticity. No two-body (assembly) solve — the trunk base and the rigidity plate need one. No thermal coupling (lane F3).</li>'
            '</ul></section>')


def sections():
    L = load("loads_mujoco.json")
    feas = fea_studies()
    drop = load("drop_impact.json")
    fat = load("fatigue_ankle.json")
    fatw = load("fatigue_walk.json")
    conv = load("fea_convergence_microduck-ankle-left_drop.json")
    mats = load("fea_materials_microduck-ankle-left_drop.json")
    meshab = load("fea_meshability_microduck-upper-leg-left.json")
    M = load(os.path.join(REPO, "out", "stress", "matrix.json"))
    nls = nlgeom_studies()
    return [sec_verdict(L, feas, drop, fat, fatw, conv, mats, meshab), sec_loads(L, drop), sec_fea(feas), sec_nlgeom(nls), sec_matrix(M), sec_conv(conv, mats), sec_buckling(),
            sec_drop(drop), sec_fatigue(fat, fatw), sec_material(feas), sec_open(feas, meshab, drop, fat, fatw, conv, nls), sec_method()]


STYLE = """
  .pair{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:10px 0 4px}
  .pair figure{margin:0;padding:8px}
  .pair figure img{width:100%;aspect-ratio:1/1;object-fit:contain;background:#fff}
  .tag{font-family:var(--sans);font-size:10.5px;font-weight:600;letter-spacing:.07em;text-transform:uppercase;display:inline-block;padding:2px 8px;margin-bottom:6px;border:1px solid var(--hair);color:var(--ink-2)}
  .tag.ours{color:var(--accent);border-color:var(--accent)}
  .paircap{font-family:var(--sans);font-size:12.5px;color:var(--ink-2);margin:0 0 2px}
  .note{font-size:13.5px;color:var(--ink-2);margin:2px 0 18px;max-width:52em}
  .verdict{border-left:3px solid var(--accent);padding:2px 0 2px 18px;margin:14px 0;font-size:15.5px}
  .verdict b{color:var(--accent)}
  .verdict ul{margin:6px 0 0;padding-left:18px;font-size:14px}
  .verdict.warn{border-left-color:var(--no)} .verdict.warn b{color:var(--no)}
  .chip.fail{color:var(--no)}
  .statbar{display:flex;flex-wrap:wrap;gap:0;border-bottom:1px solid var(--hair);margin:8px 0 2px}
  .stat{padding:12px 26px 12px 0;margin-right:22px}
  .stat b{display:block;font-weight:700;font-size:22px;font-variant-numeric:tabular-nums}
  .stat span{font-family:var(--sans);font-size:12px;color:var(--ink-2)}
  table.data td code{font-size:12px}
  @media(max-width:640px){.pair{grid-template-columns:1fr}}
"""


def backlinks():
    links = ['<a href="RELEASE.html">← Release dossier</a>', '<a href="INDEX.html">Repo index</a>']
    if os.path.exists(os.path.join(REPO, "SIMULATION.html")):
        links.append('<a href="SIMULATION.html">Simulation evidence</a>')
    return " · ".join(links)


def page():
    secs = sections()
    date = "2026-09-03"
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Structural Evidence</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opt_sz,wght@8..60,400;8..60,600;8..60,700&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="tools/doc.css">
<style>%s</style>
</head>
<body>
<div class="wrap">
<p class="backlink">%s</p>
<header class="hero">
  <p class="eyebrow">Microduck · simulation evidence · lane F1 structural</p>
  <h1>Structural evidence: FEA on every load-bearing part, a 0.250 m drop onto the foot and onto the head, buckling, and fatigue</h1>
  <p class="sub">Every load below was read off MuJoCo running Pollen's walking policy on Pollen's model; every strength figure carries the table or
  datasheet it came from; every field image was read back from the solve that produced the verdict; every study on disk is on this page. Three verdicts only.</p>
  <div class="rev"><span>MD-STR-001 · Rev B</span><span>%s</span><span>generator: tools/gen_structural.py (self-checked)</span><span>data: out/sim-evidence/*.json</span></div>
</header>
<nav class="toc">
  <a href="#verdict">1 Verdict</a><a href="#loads">2 Load basis</a><a href="#fea">3 FEA</a><a href="#nlgeom">3b Nonlinear</a><a href="#matrix">4 Matrix</a><a href="#conv">5 Convergence</a><a href="#buckling">5b Buckling</a>
  <a href="#drop">6 Drop</a><a href="#fatigue">7 Fatigue</a><a href="#material">8 Material</a><a href="#open">9 Open</a><a href="#method">10 Method</a>
</nav>
%s
</div>
</body>
</html>
""" % (STYLE, backlinks(), esc(date), "\n\n".join(secs))


# ---------------------------------------------------------------------------
def selfcheck(doc):
    """Every claim the page makes about its own completeness, measured against disk. Returns (ok, [lines])."""
    out, ok = [], True

    def check(name, cond, detail=""):
        nonlocal ok
        ok = ok and bool(cond)
        out.append("%-4s %s%s" % ("PASS" if cond else "FAIL", name, (" — " + detail) if detail else ""))

    feas = fea_studies()
    disk = fea_files_on_disk()
    skipped = [p for p in disk if CONV_SUBRUN.search(os.path.basename(p))]
    check("every study on disk is published", len(feas) + len(skipped) == len(disk), "%d published + %d sub-runs = %d on disk" % (len(feas), len(skipped), len(disk)))
    check("no head_drop study skipped", all("head_drop" not in os.path.basename(p) for p in skipped) and sum(r["case"] == "head_drop" for r in feas) == sum("head_drop" in os.path.basename(p) for p in disk),
          "%d head_drop published" % sum(r["case"] == "head_drop" for r in feas))
    check("head_drop appears in the page", doc.count("head_drop") + doc.count("head drop") >= 8, "%d mentions" % (doc.count("head_drop") + doc.count("head drop")))
    fails = [r for r in feas if r["verdict"] == "FAIL"]
    check("every FAIL is in the FAIL list", all(esc(r["why"]) in doc for r in fails), "%d FAILs" % len(fails))
    cds = [r for r in feas if r["verdict"] == "CANNOT DETERMINE"]
    check("every CANNOT DETERMINE prints its full why", all(esc(r["why"]) in doc for r in cds), "%d" % len(cds))
    check("every why is printed in full (nothing sliced)", all(esc(r.get("why", "")) in doc for r in feas))
    for r in buckling_studies():
        check("buckling why in full: %s" % r["part"], esc(r["why"]) in doc)
    n_pass, n_fail, n_cd = (sum(r["verdict"] == v for r in feas) for v in ("PASS", "FAIL", "CANNOT DETERMINE"))
    check("statbar counts equal the recount", ("<b>%d / %d / %d</b>" % (n_pass, n_fail, n_cd)) in doc and ("<b>%d / %d</b>" % (len(feas), len(disk))) in doc, "%d/%d/%d, %d/%d" % (n_pass, n_fail, n_cd, len(feas), len(disk)))
    solved = [r for r in feas if sf_used(r) is not None]
    worst = min(solved, key=sf_used)
    check("worst linear SF on disk is printed in §1", ("Worst linear safety factor anywhere on disk: <code>%s</code>" % esc(worst["part"])) in doc and f(sf_used(worst)) in doc, "%s %s" % (worst["part"], f(sf_used(worst))))
    imgs = re.findall(r'<img src="([^"]+)"', doc)
    missing = [i for i in imgs if not os.path.exists(os.path.join(REPO, i))]
    check("every image on the page exists on disk", not missing, "%d images, missing: %s" % (len(imgs), missing[:5]))
    fea_pngs = [r for r in feas if any(a.endswith(".png") for a in r.get("artifacts", []))]
    check("every study with a picture embeds it", all(next(a for a in r["artifacts"] if a.endswith(".png")) in imgs for r in fea_pngs), "%d of %d" % (
        sum(next(a for a in r["artifacts"] if a.endswith(".png")) in imgs for r in fea_pngs), len(fea_pngs)))
    bad_caps = [(r["study"], caption_verdict(r), r["verdict"]) for r in fea_pngs if caption_verdict(r) != r["verdict"]]
    check("every picture's caption verdict equals the study verdict", not bad_caps, str(bad_caps[:4]))
    hrefs = [h for h in re.findall(r'href="([^"#][^"]*)"', doc) if not h.startswith("http")]
    dead = [h for h in hrefs if not os.path.exists(os.path.join(REPO, h.split("#")[0]))]
    check("every local link targets a file that exists", not dead, "%d links, dead: %s" % (len(hrefs), dead[:5]))
    check("no link to a SIMULATION.html that does not exist", os.path.exists(os.path.join(REPO, "SIMULATION.html")) or "SIMULATION.html" not in doc)
    fw = load("fatigue_walk.json")
    walks = [r for r in feas if r["case"] == "walk"]
    check("fatigue table has one row per walk study", fw is not None and len(fw["outputs"]["rows"]) == len(walks), "%s rows vs %d walk studies" % (len(fw["outputs"]["rows"]) if fw else None, len(walks)))
    d = load("drop_impact.json")
    check("drop height carries a source", bool(d and d["inputs"].get("height_source")) and esc(d["inputs"]["height_source"]) in doc)
    check("no truncated sentence markers", " mo.</" not in doc and "back-plat " not in doc)
    return ok, out


if __name__ == "__main__":
    doc = page()
    ok, lines = selfcheck(doc)
    print("\n".join(lines))
    if not ok:
        print("SELFCHECK FAILED — STRUCTURAL.html not written", file=sys.stderr)
        sys.exit(1)
    out = os.path.join(REPO, "STRUCTURAL.html")
    open(out, "w").write(doc)
    print("wrote", out, os.path.getsize(out), "bytes")
