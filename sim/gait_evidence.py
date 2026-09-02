#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""gait_evidence.py — turn the raw cells in out/sim-sweep/*.json into the two
lane-F evidence files other lanes consume:

  out/sim-evidence/gait-peaks.json       the per-joint peak actuator torque and
                                         per-foot ground-reaction force table
                                         (F1 FEA and F3 thermal read this)
  out/sim-evidence/gait-robustness.json  the full perturbation matrix, one row
                                         per cell, with the verdict

Nothing is computed here that was not measured by sim/gait_sweep.py; this file
only aggregates and states the verdict against cited servo limits.
"""
import glob
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
from common import JOINT_NAMES  # noqa: E402

ROOT = common.ROOT
SWEEP = os.path.join(ROOT, "out", "sim-sweep")
EVID = os.path.join(ROOT, "out", "sim-evidence")

# --- the servo's own published limits, verbatim from the fetched vendor page ---
XL330 = {
    "part": "XL330-M288-T",
    "source": "ROBOTIS e-Manual, https://emanual.robotis.com/docs/en/dxl/x/xl330-m288/ , Specifications table; "
              "fetched 2026-09-02, sha256 in ce-parts/xl330-m288-t/PROVENANCE.json, local copy "
              "ce-parts/xl330-m288-t/iterations/v0.0.1/docs/fetched/robotis-emanual-xl330-m288.html. "
              "The same table on the successor host https://docs.robotis.com/docs/dxl/model_reference/"
              "x_series/xl_series/xl330-m288/ reads identically.",
    "stall_torque_Nm_quote": "0.42 [N.m] (at 3.7 [V], 1.11 [A], 0.378 [Nm/A]) / "
                             "0.52 [N.m] (at 5.0 [V], 1.47 [A], 0.354 [Nm/A]) / "
                             "0.60 [N.m] (at 6.0 [V], 1.74 [A], 0.345 [Nm/A])",
    "stall_torque_Nm": {"3.7": 0.42, "5.0": 0.52, "6.0": 0.60},
    "no_load_speed_rpm_quote": "76 [rev/min] (at 3.7 [V]) / 103 [rev/min] (at 5.0 [V]) / 123 [rev/min] (at 6.0 [V])",
    "no_load_speed_rpm": {"3.7": 76, "5.0": 103, "6.0": 123},
    "standby_current_mA_quote": "Standby Current | 17 [mA]",
    "standby_current_mA": 17,
    "gear_ratio_quote": "Gear Ratio | 288.4 : 1",
    "note": "ROBOTIS publishes NO no-load CURRENT and NO continuous-torque rating for this actuator; the "
            "only currents on the page are the three stall rows and the 17 mA standby. Above 6.0 V the vendor "
            "states nothing at all, and the Microduck runs the servos on the raw 6.6-8.2 V pack "
            "(docs/ELECTRONICS-AND-SOFTWARE.md 3.4), outside the 3.7-6.0 V input band.",
}
KNOWN_LIMITATIONS = [
    {"limitation": "In sim/microduck_ours.xml only the two soles can touch the floor (2 of 75 robot geoms, "
                   "MEASURED in out/sim-evidence/collision-model-census.json). After a fall the body passes "
                   "THROUGH the floor plane and the contact solver reports reactions no physical robot can "
                   "produce.",
     "consequence": "Every torque and ground-reaction figure is published twice — over the whole record and "
                    "over the physically valid window (before the first uncommanded fall, and before any geom "
                    "centre goes below z = 0). ONLY the valid-window figures are design loads. Cells whose "
                    "record goes through the floor are named in "
                    "outputs.ground_reaction_force_N.cells_whose_record_goes_through_the_floor.",
     "what_would_close_it": "a collision set with real body shells that meet the floor, which Pollen does not "
                            "publish; sim/microduck_ours_fullcontact.xml is the nearest available and is NOT a "
                            "substitute, because letting every geom touch the floor also puts four extra "
                            "ankle/foot geoms on the ground and that is a different foot (measured per cell in "
                            "outputs.contacts.floor_contact_points_by_geom_summed_over_control_frames)."},
    {"limitation": "The walking, sit-stand and stand policies are Pollen's published ONNX nets, run open-loop "
                   "against a velocity command. Nothing here retrains or tunes them.",
     "consequence": "A heading failure on a slope is a property of THAT policy on THIS model, not a proof that "
                    "the mechanism cannot walk uphill.",
     "what_would_close_it": "a policy trained on our own mass/inertia set, or a heading controller closing yaw."},
    {"limitation": "The one body pair excluded from the self-collision census, jaw_soft <-> neck_pitch, whose "
                   "convex hulls already interpenetrate 2.117-4.472 mm in the STAND pose.",
     "consequence": "A genuine head-to-neck interference would not be seen by the census.",
     "what_would_close_it": "a solid-solid boolean intersection of neck_pitch + its 22x16x4 bearing against "
                            "bottom_head_shell + jaw in the STAND pose."},
]
MJCF_FORCERANGE_NM = 0.96
MJCF_FORCERANGE_CITE = ("reference/pollen-microduck-rl/robot_walk.xml:44-47 default class 'chosen_actuator': "
                        "<position kp=\"0.55\" kv=\"0.0\" forcerange=\"-0.96 0.96\" ctrlrange=\"-10.0 10.0\"/>")


def artifact_list():
    """Every file this lane wrote that a reader can open: the per-cell records, the compiled
    scenes, the saved trajectories, the videos and the frames read back out of them."""
    out = []
    for pat in ("*.json", "scene_*.xml", "*_traj.npz", "video/*.mp4", "frames/*.png"):
        out += [os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(SWEEP, pat))]
    return sorted(set(out))


def load_cells():
    cells = []
    for p in sorted(glob.glob(os.path.join(SWEEP, "*.json"))):
        d = json.load(open(p))
        if not isinstance(d, dict) or "inputs" not in d or "outputs" not in d:
            continue      # the _summary.json render shims and videos.json are not cells
        cells.append(d)
    return cells


def _peak_time(cell):
    """The time of the whole-record GRF peak, measured in sim/gait_sweep.py."""
    return cell["outputs"]["grf_vertical_peak_N"]["both_feet_sum_peak_at_s"]


def peaks(cells):
    walking = [c for c in cells if c["inputs"]["policy"] == "walking"]
    upright = [c for c in walking if not c["outputs"]["fell"]]
    families = {}
    for c in cells:
        families.setdefault(c["family"], []).append(c)

    def table(group):
        out = {}
        for j in JOINT_NAMES:
            best = max(group, key=lambda c: c["outputs"]["per_joint"][j]["peak_abs_torque_Nm"])
            pj = best["outputs"]["per_joint"][j]
            spd = max(group, key=lambda c: c["outputs"]["per_joint"][j]["peak_abs_speed_rad_s"])
            vbest = max(group, key=lambda c: c["outputs"]["per_joint"][j]["prefall_peak_abs_torque_Nm"])
            vpj = vbest["outputs"]["per_joint"][j]
            out[j] = {
                "peak_abs_torque_Nm": pj["peak_abs_torque_Nm"],
                "peak_signed_torque_Nm": pj["peak_signed_torque_Nm"],
                "peak_cell": best["cell"],
                "peak_at_s": pj["peak_at_s"],
                "peak_is_inside_the_physically_valid_window": pj["peak_is_inside_valid_window"],
                "prefall_peak_abs_torque_Nm": vpj["prefall_peak_abs_torque_Nm"],
                "prefall_peak_cell": vbest["cell"],
                "prefall_peak_at_s": vpj["prefall_peak_at_s"],
                "p99_abs_torque_Nm": pj["p99_abs_torque_Nm"],
                "p95_abs_torque_Nm": pj["p95_abs_torque_Nm"],
                "rms_torque_Nm_in_peak_cell": pj["rms_torque_Nm"],
                "peak_abs_speed_rad_s": spd["outputs"]["per_joint"][j]["peak_abs_speed_rad_s"],
                "peak_abs_speed_rpm_output": spd["outputs"]["per_joint"][j]["peak_abs_speed_rpm_output"],
                "peak_speed_cell": spd["cell"],
                "range_deg": pj["range_deg"],
                "max_range_utilisation_pct": max(c["outputs"]["per_joint"][j]["range_utilisation_pct"] for c in group),
                "cells_with_frames_beyond_limit": [c["cell"] for c in group
                                                   if c["outputs"]["per_joint"][j]["frames_beyond_limit"] > 0],
                "max_overshoot_beyond_limit_deg": max(
                    c["outputs"]["per_joint"][j]["max_overshoot_beyond_limit_deg"] for c in group),
                "cells_saturating_mjcf_forcerange": [c["cell"] for c in group
                                                     if c["outputs"]["per_joint"][j]["frames_at_forcerange_limit"] > 0],
                "vs_xl330_stall_at_5V_pct": round(100.0 * pj["peak_abs_torque_Nm"] / XL330["stall_torque_Nm"]["5.0"], 2),
                "vs_xl330_stall_at_6V_pct": round(100.0 * pj["peak_abs_torque_Nm"] / XL330["stall_torque_Nm"]["6.0"], 2),
            }
        return out

    LOCO_FAMILIES = ("baseline", "vx", "mass", "friction", "slope", "selfcollision", "endurance")
    # family "collision_census" is EXCLUDED from every load table on purpose: those cells run
    # sim/microduck_ours_selfcontact.xml and _fullcontact.xml, which exist to answer what CAN
    # touch what, not to produce loads. walk_selfcontact reproduces base_walk_vx0.25 to 5 dp
    # (that is its validation); push_5N_lat_fullcontact does NOT reproduce push_5N_lat, because
    # letting every geom touch the floor also lets four extra ankle/foot geoms touch it and that
    # is a different foot (measured: outputs.contacts.floor_contact_points_by_geom_...).
    census_cells = [c for c in cells if c["family"] == "collision_census"]
    loco = [c for c in cells if c["family"] in LOCO_FAMILIES and not c["outputs"]["fell"]]
    dist = [c for c in cells if c["family"] == "push"]
    post = [c for c in cells if c["family"] == "sitstand"]
    walk_tbl = table(loco)
    dist_tbl = table(dist)
    post_tbl = table(post)
    all_tbl = table(cells)
    grf_walk = max(loco, key=lambda c: c["outputs"]["grf_vertical_peak_N"]["both_feet_sum_peak"])
    load_cells = [c for c in cells if c["family"] != "collision_census"]
    grf_all = max(load_cells, key=lambda c: c["outputs"]["grf_vertical_peak_N"]["both_feet_sum_peak"])
    grf_valid = max(load_cells, key=lambda c: c["outputs"]["grf_vertical_peak_PREFALL_N"]["both_feet_sum_peak"])
    gv = grf_valid["outputs"]["grf_vertical_peak_PREFALL_N"]
    grf_loco = max(loco, key=lambda c: c["outputs"]["grf_vertical_peak_PREFALL_N"]["both_feet_sum_peak"])
    gl = grf_loco["outputs"]["grf_vertical_peak_PREFALL_N"]
    ga = grf_all["outputs"]
    postfall_cells = {c["cell"]: {
        "reported_peak_N": c["outputs"]["grf_vertical_peak_N"]["both_feet_sum_peak"],
        "prefall_peak_N": c["outputs"]["grf_vertical_peak_PREFALL_N"]["both_feet_sum_peak"],
        "first_fall_s": c["outputs"]["first_fall_s"],
        "frames_with_a_geom_centre_below_the_floor":
            c["outputs"]["physically_valid_window"]["frames_with_a_geom_centre_below_the_floor"],
        "fraction_of_frames_below_the_floor":
            c["outputs"]["physically_valid_window"]["fraction_of_frames_below_the_floor"],
        "min_geom_centre_z_m": c["outputs"]["physically_valid_window"]["min_geom_centre_z_m"],
        "min_trunk_z_m": c["outputs"]["physically_valid_window"]["min_trunk_z_m"],
    } for c in load_cells
        if c["outputs"]["physically_valid_window"]["frames_with_a_geom_centre_below_the_floor"] > 0}
    over5 = [j for j, v in walk_tbl.items() if v["peak_abs_torque_Nm"] > XL330["stall_torque_Nm"]["5.0"]]
    over6 = [j for j, v in walk_tbl.items() if v["peak_abs_torque_Nm"] > XL330["stall_torque_Nm"]["6.0"]]
    base = [c for c in cells if c["cell"] == "base_walk_vx0.25"][0]

    bpk = base["outputs"]["per_joint"]
    base_worst_j = max(JOINT_NAMES, key=lambda j: bpk[j]["peak_abs_torque_Nm"])
    base_worst = bpk[base_worst_j]["peak_abs_torque_Nm"]
    base_ok5 = base_worst <= XL330["stall_torque_Nm"]["5.0"]
    over_by_cell = {}
    for c in loco:
        bad = [j for j in JOINT_NAMES
               if c["outputs"]["per_joint"][j]["peak_abs_torque_Nm"] > XL330["stall_torque_Nm"]["6.0"]]
        if bad:
            over_by_cell[c["cell"]] = {j: c["outputs"]["per_joint"][j]["peak_abs_torque_Nm"] for j in bad}
    verdict = "PASS" if not over6 else "FAIL"
    why = (
        "Peak actuator torque over %d upright LOCOMOTION cells is %.4f N.m at %s (cell %s). "
        % (len(loco),
           max(v["peak_abs_torque_Nm"] for v in walk_tbl.values()),
           max(walk_tbl, key=lambda j: walk_tbl[j]["peak_abs_torque_Nm"]),
           walk_tbl[max(walk_tbl, key=lambda j: walk_tbl[j]["peak_abs_torque_Nm"])]["peak_cell"])
        + ("No joint exceeds the XL330-M288-T's published stall torque at 6.0 V (0.60 N.m) in any upright locomotion cell."
           if not over6 else
           "THESE JOINTS EXCEED the XL330-M288-T's published stall torque at 6.0 V (0.60 N.m) in an upright locomotion "
           "cell, so the physical servo cannot reproduce the simulated gait there: " + ", ".join(
               "%s %.4f N.m in %s" % (j, walk_tbl[j]["peak_abs_torque_Nm"], walk_tbl[j]["peak_cell"]) for j in over6))
        + " AT THE REFERENCE COMMAND (vx 0.25 m/s, level, nominal mass) the worst joint is %s at %.4f N.m = "
          "%.2f %% of the 5.0 V stall row, so the nominal gait is inside the actuator; the failure is at the "
          "edges of the envelope (%s)." % (base_worst_j, base_worst,
                                           100.0 * base_worst / XL330["stall_torque_Nm"]["5.0"],
                                           ", ".join(sorted(over_by_cell)) or "none")
        + " Joints over the 5.0 V stall row (0.52 N.m): " + (", ".join(over5) if over5 else "none")
        + ". The MJCF's own actuator ceiling is +/-%.2f N.m (%s), which is ABOVE every published stall row, so the "
          "simulation is permitted torques the actuator has no vendor figure for; that ceiling is reached only in "
          "the push and sit-stand cells." % (MJCF_FORCERANGE_NM, MJCF_FORCERANGE_CITE)
    )

    return {
        "study": "gait-peaks",
        "inputs": {
            "model": "sim/microduck_ours.xml (walking cells) and sim/microduck_ours_allcollisions.xml "
                     "(sit-stand) — OUR rebuilt meshes on Pollen's stock collision geoms and inertials "
                     "(sim/swap_meshes.py, out/sim/swap_report.json). The self-collision census runs on "
                     "sim/microduck_ours_selfcontact.xml and the through-the-floor question on "
                     "sim/microduck_ours_fullcontact.xml, both GENERATED and re-verified by "
                     "sim/collision_model.py; neither feeds a load table. What each model can and cannot "
                     "touch is MEASURED in out/sim-evidence/collision-model-census.json.",
            "policies": "sim/policies/BEST_alpha_walking.onnx, BEST_alpha_sitstand.onnx, BEST_alpha_stand.onnx "
                        "— Pollen's published policies (sim/README.md)",
            "actuator_model": "MuJoCo <position> actuator, gear 1, kp 0.55, kv 0.0, forcerange +/-0.96 N.m, "
                              "joint damping 0.053, frictionloss 0.0048, armature 0.0018 (class 'chosen_actuator', "
                              + MJCF_FORCERANGE_CITE + "). data.actuator_force is therefore the joint torque in N.m.",
            "total_mass_kg": base["model"]["total_mass_kg"],
            "total_mass_source": "model.body_mass.sum() of the compiled scene, measured in sim/gait_sweep.py; "
                                 "Pollen's inertials, unchanged by the mesh swap",
            "weight_N": base["outputs"]["weight_N"],
            "servo": XL330,
            "cells": len(cells), "upright_locomotion_cells": len(loco),
            "disturbance_cells": len(dist), "posture_cells": len(post),
        },
        "method": "sim/gait_sweep.py records data.actuator_force (N.m), data.qvel per actuated joint (rad/s) and "
                  "mj_contactForce on every contact touching left_foot_collision / right_foot_collision at "
                  "EVERY 200 Hz PHYSICS STEP of every cell (MuJoCo timestep 0.005 s, decimation 4 under a 50 Hz "
                  "control loop) — sampling only the 50 Hz control frame misses the intra-step peak, measured "
                  "5.4 %% low on left_knee in the reference cell. This file takes, per joint, the maximum over "
                  "cells of the per-cell peak, and names the cell and the frame time it came from. It also "
                  "carries, per joint, prefall_peak_abs_torque_Nm — the same maximum restricted to the "
                  "physically valid window (see known_limitations[0]) — because a post-fall frame in a model "
                  "where the body can pass through the floor is not a load. Family collision_census is excluded "
                  "from every table here: those cells exist to measure what CAN touch what. The "
                  "ground-reaction check is validated against statics: in the standing cells the median summed "
                  "vertical GRF is 7.2425 N (vx_0.00) and 7.2289 N (stand_hold) against a computed weight of "
                  "%.4f N — 0.14 %% and 0.05 %%. "
                  "PROVENANCE OF THIS FILE, for any lane that read an earlier copy: the first version "
                  "(commit 4df37e3, 2026-09-02 21:40) sampled torque at the 50 Hz control frame; commit "
                  "577070a (23:01) moved every cell to the 200 Hz physics record and EVERY per-joint peak "
                  "changed by +7.6 to +9.0 %% (right_hip_pitch 0.74179 -> 0.80221 N.m, left_hip_pitch "
                  "0.52286 -> 0.56991, left_knee 0.71519 -> 0.76987). This revision adds the pre-fall column "
                  "and re-runs the whole matrix. A consumer holding numbers from before 577070a has stale "
                  "ones; the reference-walk baseline did not move."
                  % base["outputs"]["weight_N"],
        "outputs": {
            "FOR_CONSUMERS": {
                "$read_this": "F1 (structural FEA) and F3 (servo thermal) read this file. If your lane quotes "
                              "numbers from it, check them against per_joint_locomotion_upright_fingerprint "
                              "below; if it differs from the one you recorded, re-read the table.",
                "per_joint_locomotion_upright_fingerprint": hashlib.sha256(
                    json.dumps({j: walk_tbl[j]["peak_abs_torque_Nm"] for j in JOINT_NAMES},
                               sort_keys=True).encode()).hexdigest()[:16],
                "per_joint_locomotion_upright_peaks_Nm": {j: walk_tbl[j]["peak_abs_torque_Nm"]
                                                          for j in JOINT_NAMES},
                "sampling_rate": "200 Hz, the MuJoCo physics step (timestep 0.005 s). NOT the 50 Hz control "
                                 "frame. Any consumer note that says F2 samples at 50 Hz is stale — that was "
                                 "true only of the version committed at 4df37e3 (2026-09-02 21:40) and it was "
                                 "superseded at 577070a the same evening.",
                "revision_history": [
                    {"commit": "4df37e3", "when": "2026-09-02 21:40",
                     "what": "first version; torque sampled at the 50 Hz control frame; no script committed "
                             "alongside it. STALE — do not quote."},
                    {"commit": "577070a", "when": "2026-09-02 23:01",
                     "what": "moved to the 200 Hz physics record; EVERY per-joint peak rose 7.6-9.0 % "
                             "(right_hip_pitch 0.74179 -> 0.80221 N.m, left_hip_pitch 0.52286 -> 0.56991, "
                             "left_knee 0.71519 -> 0.76987)."},
                    {"commit": "this one", "when": "2026-09-03",
                     "what": "adds the physically-valid-window columns (prefall_peak_abs_torque_Nm, "
                             "grf_vertical_peak_PREFALL_N) and the tiered FEA design loads, and EXCLUDES the "
                             "two collision-model instrument cells from every table. The 200 Hz per-joint "
                             "locomotion peaks are unchanged by this revision; what changed is the "
                             "ground-reaction design load, which is now pre-fall."},
                ],
            },
            "per_joint_locomotion_upright": walk_tbl,
            "per_joint_disturbance_push": dist_tbl,
            "per_joint_posture_sit_stand": post_tbl,
            "per_joint_all_cells": all_tbl,
            "group_definitions": {
                "locomotion_upright": "families baseline/vx/mass/friction/slope/selfcollision that did not fall "
                                      "(%d cells) — the undisturbed walking envelope; THIS is the table to size "
                                      "structure and thermals against for normal operation." % len(loco),
                "disturbance_push": "family push (%d cells) — an external 0.2 s force on the trunk; the actuator "
                                    "saturates its MJCF +/-0.96 N.m ceiling here, so these torques are the "
                                    "simulation's ceiling, not a measured actuator capability." % len(dist),
                "posture_sit_stand": "families sitstand/stand (%d cells) — commanded sit, stand-up from SIT and "
                                     "from FOLD, and a stand hold." % len(post),
            },
            "worst_locomotion_joint": max(walk_tbl, key=lambda j: walk_tbl[j]["peak_abs_torque_Nm"]),
            "worst_locomotion_torque_Nm": max(v["peak_abs_torque_Nm"] for v in walk_tbl.values()),
            "worst_disturbance_torque_Nm": max(v["peak_abs_torque_Nm"] for v in dist_tbl.values()),
            "worst_posture_torque_Nm": max(v["peak_abs_torque_Nm"] for v in post_tbl.values()),
            "joints_over_stall_5V": over5, "joints_over_stall_6V": over6,
            "cells_that_exceed_the_6V_stall_row": over_by_cell,
            "reference_command_verdict": {
                "cell": "base_walk_vx0.25",
                "verdict": "PASS" if base_ok5 else "FAIL",
                "worst_joint": base_worst_j, "worst_torque_Nm": base_worst,
                "pct_of_stall_5V": round(100.0 * base_worst / XL330["stall_torque_Nm"]["5.0"], 2),
                "pct_of_stall_6V": round(100.0 * base_worst / XL330["stall_torque_Nm"]["6.0"], 2),
                "statement": "At the reference walk command (vx 0.25 m/s, the browser simulator's VEL_FWD, "
                             "level ground, nominal mass, friction 1.0) the worst joint is %s at %.4f N.m — "
                             "%.2f %% of the XL330-M288-T's 0.52 N.m stall torque at 5.0 V and %.2f %% of the "
                             "0.60 N.m row at 6.0 V. The reference gait is inside the actuator. The FAIL above "
                             "is about the EDGES of the envelope, not about walking."
                             % (base_worst_j, base_worst,
                                100.0 * base_worst / XL330["stall_torque_Nm"]["5.0"],
                                100.0 * base_worst / XL330["stall_torque_Nm"]["6.0"])},
            "baseline_walk_vx0.25": {
                "per_joint_peak_Nm": {j: base["outputs"]["per_joint"][j]["peak_abs_torque_Nm"] for j in JOINT_NAMES},
                "sum_abs_torque_peak_Nm": base["outputs"]["sum_abs_torque_peak_Nm"],
                "walked_m": base["outputs"]["walked_m"], "mean_speed_m_s": base["outputs"]["mean_speed_m_s"],
            },
            "ground_reaction_force_N": {
                "static_weight_N": base["outputs"]["weight_N"],
                "walking_single_foot_peak_N": base["outputs"]["grf_vertical_peak_N"]["left_foot"],
                "walking_single_foot_peak_body_weights": round(
                    base["outputs"]["grf_vertical_peak_N"]["left_foot"] / base["outputs"]["weight_N"], 3),
                "walking_single_foot_p99_N": base["outputs"]["grf_vertical_percentiles_N"]["single_foot_p99"],
                "walking_both_feet_p50_N": base["outputs"]["grf_vertical_percentiles_N"]["both_feet_sum_p50"],
                "worst_upright_walking_cell": grf_walk["cell"],
                "worst_upright_walking_peak_N": grf_walk["outputs"]["grf_vertical_peak_N"]["both_feet_sum_peak"],
                "DESIGN_LOAD_worst_valid_cell": grf_valid["cell"],
                "DESIGN_LOAD_worst_valid_both_feet_peak_N": gv["both_feet_sum_peak"],
                "DESIGN_LOAD_worst_valid_both_feet_peak_at_s": gv["both_feet_sum_peak_at_s"],
                "DESIGN_LOAD_worst_valid_single_foot_peak_N": gv["single_foot_max"],
                "DESIGN_LOAD_worst_valid_body_weights": round(
                    gv["both_feet_sum_peak"] / base["outputs"]["weight_N"], 3),
                "worst_any_cell_INCLUDING_POST_FALL": grf_all["cell"],
                "worst_any_peak_N_INCLUDING_POST_FALL": ga["grf_vertical_peak_N"]["both_feet_sum_peak"],
                "worst_any_peak_body_weights_INCLUDING_POST_FALL": round(
                    ga["grf_vertical_peak_N"]["both_feet_sum_peak"] / base["outputs"]["weight_N"], 3),
                "cells_whose_record_goes_through_the_floor": postfall_cells,
                "why_post_fall_numbers_are_not_loads":
                    "sim/microduck_ours.xml gives only 2 of its 75 robot geoms a floor-colliding contype — the "
                    "two soles (MEASURED: sim/collision_model.py -> "
                    "out/sim-evidence/collision-model-census.json). Once the robot tips, every other body "
                    "passes THROUGH the floor plane and the contact solver resolves the remaining feet against "
                    "a robot that is partly inside the ground. In cell %s that produces %.4f N summed over the "
                    "feet at %.3f s, %.3f s AFTER the fall at %.2f s. Later in the same cell the trunk "
                    "centre reaches %.4f m BELOW z = 0 and the lowest geom centre %.5f m; %d of %d physics "
                    "frames (%.1f %%) of that cell have a geom centre below the floor. NO PHYSICAL ROBOT CAN "
                    "PRODUCE THAT NUMBER and it must not be used as a load."
                    % (grf_all["cell"], ga["grf_vertical_peak_N"]["both_feet_sum_peak"],
                       _peak_time(grf_all),
                       max(0.0, _peak_time(grf_all) - (grf_all["outputs"]["first_fall_s"] or 0.0)),
                       grf_all["outputs"]["first_fall_s"] or 0.0,
                       abs(ga["physically_valid_window"]["min_trunk_z_m"]),
                       ga["physically_valid_window"]["min_geom_centre_z_m"],
                       ga["physically_valid_window"]["frames_with_a_geom_centre_below_the_floor"],
                       ga["physically_valid_window"]["frames_total"],
                       100.0 * ga["physically_valid_window"]["fraction_of_frames_below_the_floor"]),
                "for_FEA_tiers": {
                    "1_nominal_walking": {
                        "single_foot_N": base["outputs"]["grf_vertical_peak_N"]["left_foot"],
                        "body_weights": round(base["outputs"]["grf_vertical_peak_N"]["left_foot"]
                                              / base["outputs"]["weight_N"], 3),
                        "cell": "base_walk_vx0.25", "post_fall_frames": 0,
                        "use_for": "the load the robot sees every step of a normal walk"},
                    "2_worst_undisturbed_locomotion": {
                        "both_feet_N": gl["both_feet_sum_peak"], "single_foot_N": gl["single_foot_max"],
                        "at_s": gl["both_feet_sum_peak_at_s"], "cell": grf_loco["cell"],
                        "body_weights": round(gl["both_feet_sum_peak"] / base["outputs"]["weight_N"], 3),
                        "use_for": "the structural design load for the whole commanded envelope "
                                   "(vx 0-0.80 m/s, mass +/-10 %, friction 0.40-1.00, 5 deg slopes) with no "
                                   "external disturbance"},
                    "3_worst_physically_valid_anywhere": {
                        "both_feet_N": gv["both_feet_sum_peak"], "single_foot_N": gv["single_foot_max"],
                        "at_s": gv["both_feet_sum_peak_at_s"], "cell": grf_valid["cell"],
                        "body_weights": round(gv["both_feet_sum_peak"] / base["outputs"]["weight_N"], 3),
                        "use_for": "the abuse case — a 0.2 s external push on the trunk, PRE-FALL record only"},
                    "NOT_A_LOAD_post_fall": {
                        "both_feet_N": ga["grf_vertical_peak_N"]["both_feet_sum_peak"],
                        "cell": grf_all["cell"], "at_s": _peak_time(grf_all),
                        "why": "post-fall, body inside the floor plane — see "
                               "why_post_fall_numbers_are_not_loads"},
                },
                "for_FEA": "THREE TIERS, all from the PHYSICALLY VALID record. (1) NOMINAL WALKING: %.4f N on "
                           "one foot (%.3f x body weight), cell base_walk_vx0.25 — the load of every step. "
                           "(2) WORST UNDISTURBED LOCOMOTION, the structural design load for the commanded "
                           "envelope: %.4f N summed over both feet, %.4f N on one foot, at t = %.3f s in cell "
                           "%s (%.3f x body weight). (3) ABUSE, external push: %.4f N summed over both feet at "
                           "t = %.3f s in cell %s (%.3f x body weight). DO NOT USE the %.4f N that cell %s "
                           "reports over its whole record — it is POST-FALL and NON-PHYSICAL, see "
                           "why_post_fall_numbers_are_not_loads. A drop or impact load is a separate study "
                           "(out/sim-evidence/drop_impact.json), not this one."
                           % (base["outputs"]["grf_vertical_peak_N"]["left_foot"],
                              base["outputs"]["grf_vertical_peak_N"]["left_foot"] / base["outputs"]["weight_N"],
                              gl["both_feet_sum_peak"], gl["single_foot_max"], gl["both_feet_sum_peak_at_s"],
                              grf_loco["cell"], gl["both_feet_sum_peak"] / base["outputs"]["weight_N"],
                              gv["both_feet_sum_peak"], gv["both_feet_sum_peak_at_s"], grf_valid["cell"],
                              gv["both_feet_sum_peak"] / base["outputs"]["weight_N"],
                              ga["grf_vertical_peak_N"]["both_feet_sum_peak"], grf_all["cell"]),
            },
        },
        "verdict": verdict,
        "why": why,
        "known_limitations": KNOWN_LIMITATIONS,
        "script": "sim/gait_sweep.py + sim/gait_evidence.py + sim/collision_model.py",
        "artifacts": artifact_list(),
        "looked_at": [
            "out/sim-evidence/collision-model-census.json",
            "out/sim-evidence/f2-preview.png (this lane's own rendered page, read back)",
            "reference/pollen-microduck-rl/robot_walk.xml (actuator class chosen_actuator, joint ranges)",
            "sim/microduck_ours.xml, sim/microduck_ours_allcollisions.xml",
            "ce-parts/xl330-m288-t/electrical.chip.json (the cited ROBOTIS rows)",
            "ce-parts/xl330-m288-t/iterations/v0.0.1/docs/fetched/robotis-emanual-xl330-m288.html",
            "out/sim/report.md (the pre-existing baseline: walk 0.79 m / 8 s, no fall)",
        ],
    }


def _census_statement(cells):
    """The self-collision answer from the model that can actually answer it."""
    cc = [c for c in cells if c["cell"] == "walk_selfcontact"]
    if not cc:
        return {"verdict": "CANNOT DETERMINE",
                "why": "cell walk_selfcontact is not in out/sim-sweep — run sim/gait_sweep.py --all"}
    c = cc[0]
    o, sc = c["outputs"], c["outputs"]["self_collisions"]
    base = [x for x in cells if x["cell"] == "base_walk_vx0.25"]
    b = base[0]["outputs"] if base else None
    same = (b is not None
            and abs(b["walked_m"] - o["walked_m"]) < 1e-5
            and abs(b["max_joint_torque_Nm"] - o["max_joint_torque_Nm"]) < 1e-5)
    return {
        "cell": c["cell"],
        "model": c["model"]["robot_file"],
        "candidate_geom_pairs": sc["candidate_geom_pairs_in_this_model"],
        "bodies_that_can_self_collide": c["model"]["collision_scope"]["bodies_that_can_self_collide"],
        "excluded_body_pairs": c["model"]["collision_scope"]["excluded_body_pairs"],
        "self_contacts_max_per_frame": sc["max"],
        "self_contact_frames": sc["frames"],
        "pairs_that_touched": sc["pairs_first_touching_during_the_motion"],
        "reproduces_the_reference_walk": same,
        "reproduction_check": ("walked_m %.5f vs %.5f and peak torque %.5f vs %.5f N.m against "
                               "base_walk_vx0.25 — the census model is dynamically the SAME robot, which is "
                               "what makes its zero meaningful"
                               % (o["walked_m"], b["walked_m"], o["max_joint_torque_Nm"],
                                  b["max_joint_torque_Nm"])) if b else "no baseline cell to compare against",
        "verdict": "PASS" if sc["max"] == 0 else "FAIL",
        "statement": ("On the model where all 15 bodies can self-collide (%d candidate geom pairs, vs 4 in "
                      "microduck_ours.xml), a 12 s reference walk at vx 0.25 m/s produced %d self-contacts. "
                      "%s"
                      % (sc["candidate_geom_pairs_in_this_model"], sc["max"],
                         "The 'no self-collision while walking' result is therefore a real measurement and not "
                         "an artefact of the collision mask." if sc["max"] == 0 else
                         "Pairs: " + ", ".join(sc["pairs_first_touching_during_the_motion"]))),
        "what_this_still_cannot_see": "the one excluded body pair, jaw_soft <-> neck_pitch. Their convex hulls "
                                      "already interpenetrate by 2.117-4.472 mm in the STAND pose because "
                                      "MuJoCo collides the CONVEX HULL of a mesh and the neck-pitch bracket and "
                                      "its 22x16x4 bearing sit INSIDE the concave head shell — which is what "
                                      "the real assembly does. Whether the real parts clear each other is a CAD "
                                      "question, not a simulation one. WHAT SETTLES IT: a solid-solid boolean "
                                      "intersection of neck_pitch + bearing against bottom_head_shell + jaw in "
                                      "the STAND pose; a non-empty common() is an interference, an empty one "
                                      "confirms the hull artefact.",
    }


def _downhill_finding(rows):
    """Name every slope cell whose displacement ended DOWN the fall line, with the number."""
    out = {}
    for r in rows:
        if not r.get("slope_deg"):
            continue
        d = r.get("downhill_progress_m")
        if d is None:
            continue
        out[r["cell"]] = {
            "downhill_dir": r["slope_downhill_dir"],
            "walked_m_unsigned": r["walked_m"],
            "walked_x_m": r["walked_x_m"], "walked_y_m": r["walked_y_m"],
            "downhill_progress_m": d,
            "uphill_progress_m": r["uphill_progress_m"],
            "fraction_of_displacement_along_the_fall_line": r["fraction_of_displacement_along_the_fall_line"],
            "net_yaw_drift_deg": r["net_yaw_drift_deg"],
            "forward_progress_m": r["forward_progress_m"],
            "commanded_direction_tracking_ratio": r["commanded_direction_tracking_ratio"],
            "path_tracking_ratio_UNSIGNED": r["path_tracking_ratio_UNSIGNED"],
            "ended_downhill_of_its_start": bool(d > 0),
            "reading": ("The robot walked FORWARD in its own frame (forward_progress_m %+.5f m) but its heading "
                        "drifted %+.3f deg, so it turned and ended %.5f m %s of where it started. It did not "
                        "slide: it turned around and walked %s."
                        % (r["forward_progress_m"], r["net_yaw_drift_deg"], abs(d),
                           "DOWNHILL" if d > 0 else "uphill", "down the hill" if d > 0 else "up the hill"))
            if r["forward_progress_m"] > 0 else
            ("The robot's own forward progress was %+.5f m — it went BACKWARDS — and it ended %.5f m %s of "
             "where it started." % (r["forward_progress_m"], abs(d), "downhill" if d > 0 else "uphill")),
        }
    down = [k for k, v in out.items() if v["ended_downhill_of_its_start"]]
    return {
        "cells": out,
        "cells_that_ended_downhill_of_their_start": down,
        "finding": ("%d of the %d 5-degree slope cells ended DOWNHILL of where they started, and the unsigned "
                    "'walked' distance that a table shows does not say so. Every one of them is a heading "
                    "failure, not a foot-slip: forward_progress_m is positive in each, so the robot kept "
                    "walking forward in its own frame while its yaw drifted far enough to point it down the "
                    "hill. A 5 degree slope is therefore NOT a cell this gait passes, whatever the "
                    "did-not-fall column says." % (len(down), len(out))) if down else
                   "No slope cell ended downhill of its start.",
    }


def robustness(cells):
    rows = []
    for c in cells:
        o, m, i = c["outputs"], c["model"], c["inputs"]
        rows.append({
            "cell": c["cell"], "family": c["family"], "note": c["note"],
            "policy": i["policy"], "robot": i["robot"], "seconds": i["seconds"],
            "vx_cmd_m_s": i["vx"] if i["policy"] == "walking" else None,
            "mass_scale": i["mass_scale"], "total_mass_kg": m["total_mass_kg"],
            "foot_friction": m["foot_friction_slide"][0], "floor_friction": m["floor_friction_slide"],
            "slope_deg": i["slope_deg"], "slope_downhill_dir": i["slope_dir"],
            "gravity_m_s2": m["gravity_m_s2"],
            "push_N": i["push_N"], "push_dir": list(i["push_dir"]), "push_at_s": i["push_at"],
            "push_dur_s": i["push_dur"], "push_frames_applied": m["push_frames_applied"],
            "fell": o["fell"], "first_fall_s": o["first_fall_s"],
            "fell_outside_commanded_ground_window": o["fell_outside_commanded_ground_window"],
            "walked_m": o["walked_m"], "mean_speed_m_s": o["mean_speed_m_s"],
            "path_length_m": o.get("path_length_m"), "mean_path_speed_m_s": o.get("mean_path_speed_m_s"),
            "net_yaw_drift_deg": o.get("net_yaw_drift_deg"),
            "yaw_drift_deg_per_m_of_path": o.get("yaw_drift_deg_per_m_of_path"),
            "path_tracking_ratio_UNSIGNED": o.get("path_tracking_ratio_UNSIGNED"),
            "forward_progress_m": o.get("forward_progress_m"),
            "backward_path_m": o.get("backward_path_m"),
            "mean_forward_speed_m_s": o.get("mean_forward_speed_m_s"),
            "commanded_direction_tracking_ratio": o.get("commanded_direction_tracking_ratio"),
            "displacement_along_initial_heading_m": o.get("displacement_along_initial_heading_m"),
            "walked_x_m": o.get("walked_x_m"), "walked_y_m": o.get("walked_y_m"),
            "downhill_progress_m": o.get("downhill_progress_m"),
            "uphill_progress_m": o.get("uphill_progress_m"),
            "fraction_of_displacement_along_the_fall_line":
                o.get("fraction_of_displacement_along_the_fall_line"),
            "physically_valid_fraction": o["physically_valid_window"]["valid_fraction"],
            "frames_below_the_floor": o["physically_valid_window"]["frames_with_a_geom_centre_below_the_floor"],
            "min_geom_centre_z_m": o["physically_valid_window"]["min_geom_centre_z_m"],
            "grf_vertical_peak_PREFALL_N": o["grf_vertical_peak_PREFALL_N"]["both_feet_sum_peak"],
            "max_joint_torque_PREFALL_Nm": o["max_joint_torque_PREFALL_Nm"],
            "self_collision_candidate_geom_pairs": o["self_collisions"]["candidate_geom_pairs_in_this_model"],
            "self_collisions_max_excluding_rest_pose_overlap":
                o["self_collisions"]["max_excluding_rest_pose_overlap"],
            "max_tilt_deg": o["max_tilt_deg"], "trunk_z_min_m": o["trunk_z_m"]["min"],
            "max_joint_torque_Nm": o["max_joint_torque_Nm"], "max_joint_torque_joint": o["max_joint_torque_joint"],
            "sum_abs_torque_peak_Nm": o["sum_abs_torque_peak_Nm"],
            "grf_vertical_peak_N": o["grf_vertical_peak_N"]["both_feet_sum_peak"],
            "grf_vertical_p50_N": o["grf_vertical_percentiles_N"]["both_feet_sum_p50"],
            "self_collisions_max": o["self_collisions"]["max"],
            "self_collision_frames": o["self_collisions"]["frames"],
            "max_range_utilisation_pct": max(v["range_utilisation_pct"] for v in o["per_joint"].values()),
            "max_range_utilisation_joint": max(o["per_joint"], key=lambda j: o["per_joint"][j]["range_utilisation_pct"]),
            "joints_beyond_limit": o["joints_beyond_limit"],
            "max_overshoot_beyond_limit_deg": round(max(
                v["max_overshoot_beyond_limit_deg"] for v in o["per_joint"].values()), 5),
            "max_overshoot_joint": max(o["per_joint"], key=lambda j: o["per_joint"][j]["max_overshoot_beyond_limit_deg"]),
            "joints_within_1deg_of_limit": o["joints_within_1deg_of_limit"],
            "joints_saturating_mjcf_forcerange": o["joints_saturating_mjcf_forcerange"],
            "nan": o["nan"],
        })
    order = {"baseline": 0, "vx": 1, "endurance": 2, "mass": 3, "friction": 4, "slope": 5,
             "push": 6, "sitstand": 7, "selfcollision": 8}
    rows.sort(key=lambda r: (order.get(r["family"], 99), r["cell"]))
    walking = [r for r in rows if r["policy"] == "walking"]
    fell_walking = [r["cell"] for r in walking if r["fell"]]
    beyond = sorted({j for r in rows for j in r["joints_beyond_limit"]})
    loco_rows = [r for r in rows if r["push_N"] == 0.0 and r["policy"] == "walking"]
    loco_beyond = sorted({j for r in loco_rows for j in r["joints_beyond_limit"]})
    worst_ovs = max(rows, key=lambda r: r["max_overshoot_beyond_limit_deg"])
    selfcol = [r["cell"] for r in rows if r["self_collisions_max"] > 0]
    downh = _downhill_finding(rows)
    down_cells = downh["cells_that_ended_downhill_of_their_start"]
    no_fall_ok = all(r["fell"] is False for r in walking if r["push_N"] < 5.0)
    verdict = "PASS" if (not loco_beyond and no_fall_ok and not down_cells) else "FAIL"
    return {
        "study": "gait-robustness",
        "inputs": {
            "matrix": {
                "vx_m_s": [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50, 0.60, 0.80],
                "mass_scale": [0.90, 1.00, 1.10],
                "foot_and_floor_sliding_friction": [0.40, 0.70, 1.00],
                "slope_deg": [0.0, 5.0], "slope_downhill_dir": ["up", "down", "side_left", "side_right"],
                "lateral_push_N_for_0.2_s": [1.0, 2.0, 5.0],
                "policies": ["walking", "sitstand", "stand"],
            },
            "baseline_from": "out/sim/report.md — walk 0.79 m in 8 s at vx 0.25, no fall (this sweep re-runs the "
                             "same cell for 12 s and measures 1.2232 m, the same 0.106 m/s)",
            "how_each_perturbation_is_applied": {
                "mass": "model.body_mass and model.body_inertia scaled; the fitted NP-F550-class pack is 99 g "
                        "(ce-parts/np-f550/electrical.part.json mass_g, Duracell DR5 page 'Weight 99 g'), which is "
                        "13.43 % of the model's 737.243 g — whether Pollen's trunk inertial already includes the "
                        "pack is CANNOT DETERMINE, so +/-10 % is swept as the brief specifies rather than a "
                        "battery-in/battery-out pair being asserted.",
                "friction": "geom_friction[:,0] set on the floor AND both foot geoms (MuJoCo mixes a contact "
                            "pair's friction elementwise-max, so setting one side alone does nothing).",
                "slope": "floor kept flat, gravity rotated: G = g*(sin(th)*dhat - cos(th)*zhat), dhat the "
                         "horizontal downhill direction. Identical mechanics in the plane's frame.",
                "push": "data.xfrc_applied on body trunk_base, world frame, held for 0.2 s from t = 6.0 s.",
            },
        },
        "method": "sim/gait_sweep.py runs each cell as its own compiled scene (written to out/sim-sweep/scene_*.xml) "
                  "with Pollen's ONNX policy in the 50 Hz loop of sim/run_policy.py, and measures every row below "
                  "off the simulation state. sim/gait_evidence.py aggregates.",
        "outputs": {
            "cells": len(rows), "rows": rows,
            "walking_cells": len(walking),
            "walking_cells_that_fell": fell_walking,
            "joints_that_ever_left_their_MJCF_range": beyond,
            "joints_that_left_their_MJCF_range_in_an_UNDISTURBED_locomotion_cell": loco_beyond,
            "worst_joint_limit_overshoot": {
                "cell": worst_ovs["cell"], "joint": worst_ovs["max_overshoot_joint"],
                "overshoot_deg": worst_ovs["max_overshoot_beyond_limit_deg"],
                "meaning": "MuJoCo enforces a joint range as a soft constraint, so an overshoot is the solver "
                           "letting the joint past its stop under load. On the physical robot that load is taken "
                           "by a mechanical hard stop, not by the servo — the parts on the list above are the "
                           "ones that would be struck."},
            "cells_with_any_self_collision": selfcol,
            "self_collision_scope": {
                "$read_this_first": "A self-collision count is only as large as the model's collision mask "
                                    "allows. MEASURED per model by sim/collision_model.py "
                                    "(out/sim-evidence/collision-model-census.json):",
                "candidate_geom_pairs_per_model": {r["cell"]: r["self_collision_candidate_geom_pairs"]
                                                   for r in rows},
                "microduck_ours.xml": "5 of 15 bodies can take part in a self-contact at all, over exactly 4 "
                                      "candidate geom pairs: the two shin `leg` meshes with each other and each "
                                      "with the trunk's `power_support`, plus the two soles with each other. "
                                      "Head, feet, hips, ankles, trunk shells and BOTH UPPER LEGS cannot "
                                      "self-collide in that model. 30 of the cells in this matrix run on it, "
                                      "so for them 'no self-collision' means only 'those four pairs did not "
                                      "touch'.",
                "microduck_ours_allcollisions.xml": "8 of 15 bodies, 40 candidate pairs (trunk_base, hip_l, "
                                                    "leg, ankle_left, jaw_soft, hip_l_2, leg_2, ankle_right). "
                                                    "yaw2roll, upper_leg_left, upper_leg_right, neck, "
                                                    "neck_pitch, yaw_roll_motion and bearing_roll carry "
                                                    "visual-only geoms and can contact nothing. It is NOT "
                                                    "'every body', and the F2 note that said so was wrong.",
                "microduck_ours_selfcontact.xml": "15 of 15 bodies, 2187 candidate pairs — every geom given "
                                                  "contype/conaffinity 2, floor contact left exactly as "
                                                  "microduck_ours.xml, and the one body pair that already "
                                                  "interpenetrates in the rest pose (jaw_soft <-> neck_pitch, "
                                                  "2.117-4.472 mm of convex-hull overlap injecting up to "
                                                  "179.73 N) excluded by a measured, re-verified "
                                                  "<contact><exclude/>. THIS is the model the census question "
                                                  "should be asked on.",
                "THE_CENSUS": _census_statement(cells),
            },
            "heading_and_tracking": {
                "finding": "The walking policy does not hold a line, and on a slope the drift is large enough "
                           "to turn the robot around. In every moving cell the integrated ground track "
                           "(path_length_m) exceeds the straight-line displacement (walked_m) and the trunk "
                           "yaw drifts monotonically. path_length_m is UNSIGNED and therefore direction-blind, "
                           "so it is not a tracking metric; commanded_direction_tracking_ratio (below) "
                           "projects each step of the ground track onto the robot's OWN instantaneous heading "
                           "and is negative when the robot goes backwards.",
                "worst_net_yaw_drift": max(
                    ((r["cell"], r["net_yaw_drift_deg"], r["yaw_drift_deg_per_m_of_path"])
                     for r in rows if r.get("net_yaw_drift_deg") is not None),
                    key=lambda x: abs(x[1])),
                "commanded_direction_tracking_ratio_moving_cells": {
                    r["cell"]: r["commanded_direction_tracking_ratio"] for r in rows
                    if r.get("commanded_direction_tracking_ratio") is not None
                    and r["mean_path_speed_m_s"] > 0.05},
                "path_tracking_ratio_UNSIGNED_moving_cells": {
                    r["cell"]: r["path_tracking_ratio_UNSIGNED"] for r in rows
                    if r.get("path_tracking_ratio_UNSIGNED") is not None and r["mean_path_speed_m_s"] > 0.05},
                "SLOPE_CELLS_ENDED_DOWNHILL": downh,
            },
            "push_threshold": {
                "survived_N": [r["push_N"] for r in rows if r["family"] == "push" and not r["fell"]],
                "fell_N": [r["push_N"] for r in rows if r["family"] == "push" and r["fell"]],
                "statement": "A 0.2 s lateral push on the trunk is survived at 1 N and 2 N and knocks the robot "
                             "over at 5 N in both +y and -y. 5 N along +x and -x is survived. Body weight is "
                             "7.2324 N, so the lateral tipping threshold lies between 0.28 and 0.69 body weights "
                             "applied for 0.2 s (an impulse between 0.2 and 1.0 N.s).",
            },
        },
        "verdict": verdict,
        "why": "STAYING UPRIGHT: across %d cells the walking policy did not fall in any of the %d walking cells "
               "except the 5 N lateral pushes (+y and -y; 5 N along +x and -x was survived). "
               "GOING WHERE COMMANDED: it FAILS. %s "
               "JOINT LIMITS: in the %d UNDISTURBED locomotion cells (vx 0-0.80 m/s, mass +/-10 %%, foot "
               "friction 0.40-1.00, 5 deg slopes in four directions) no joint left its MJCF range at all%s. "
               "Under an external push %d joints are driven past their MJCF stop, worst %s by %.4f deg in cell "
               "%s — on the real robot that is a hard stop taking the load. "
               "SELF-COLLISION: %d cells report a self-contact (%s), but READ outputs.self_collision_scope "
               "first — 30 of these cells run on sim/microduck_ours.xml, where only 4 geom pairs can touch at "
               "all. The question was re-asked on sim/microduck_ours_selfcontact.xml, where all 15 bodies can "
               "self-collide over 2187 candidate pairs and which reproduces the reference walk to 5 dp: "
               "%d self-contacts in the 12 s reference walk. "
               "POSTURE: the sit-stand cells report fell=true by the trunk-height rule because the commanded "
               "sit puts the trunk on the floor on purpose; each row also carries "
               "fell_outside_commanded_ground_window, which is the rule with that window removed."
               % (len(rows), len(walking),
                  downh["finding"],
                  len(loco_rows),
                  "" if not loco_beyond else " except " + ", ".join(loco_beyond),
                  len(beyond), worst_ovs["max_overshoot_joint"], worst_ovs["max_overshoot_beyond_limit_deg"],
                  worst_ovs["cell"], len(selfcol), ", ".join(selfcol) if selfcol else "none",
                  _census_statement(cells).get("self_contacts_max_per_frame", -1)),
        "known_limitations": KNOWN_LIMITATIONS,
        "script": "sim/gait_sweep.py + sim/gait_evidence.py + sim/collision_model.py",
        "artifacts": artifact_list(),
        "looked_at": [
            "out/sim/report.md", "out/sim/vx_sweep.json", "sim/README.md",
            "out/sim-evidence/collision-model-census.json",
            "out/sim-evidence/f2-preview.png (this lane's own rendered page, read back)",
            "reference/pollen-microduck-rl/robot_walk.xml",
            "ce-parts/np-f550/electrical.part.json",
        ],
    }


def main():
    os.makedirs(EVID, exist_ok=True)
    cells = load_cells()
    assert cells, "no cells in " + SWEEP
    for name, doc in (("gait-peaks", peaks(cells)), ("gait-robustness", robustness(cells))):
        p = os.path.join(EVID, name + ".json")
        json.dump(doc, open(p, "w"), indent=1)
        print("wrote", os.path.relpath(p, ROOT), doc["verdict"])
        print("  ", doc["why"][:400])


if __name__ == "__main__":
    main()
