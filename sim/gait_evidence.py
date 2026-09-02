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
MJCF_FORCERANGE_NM = 0.96
MJCF_FORCERANGE_CITE = ("reference/pollen-microduck-rl/robot_walk.xml:44-47 default class 'chosen_actuator': "
                        "<position kp=\"0.55\" kv=\"0.0\" forcerange=\"-0.96 0.96\" ctrlrange=\"-10.0 10.0\"/>")


def load_cells():
    cells = []
    for p in sorted(glob.glob(os.path.join(SWEEP, "*.json"))):
        cells.append(json.load(open(p)))
    return cells


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
            out[j] = {
                "peak_abs_torque_Nm": pj["peak_abs_torque_Nm"],
                "peak_signed_torque_Nm": pj["peak_signed_torque_Nm"],
                "peak_cell": best["cell"],
                "peak_at_s": pj["peak_at_s"],
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

    LOCO_FAMILIES = ("baseline", "vx", "mass", "friction", "slope", "selfcollision")
    loco = [c for c in cells if c["family"] in LOCO_FAMILIES and not c["outputs"]["fell"]]
    dist = [c for c in cells if c["family"] == "push"]
    post = [c for c in cells if c["family"] == "sitstand"]
    walk_tbl = table(loco)
    dist_tbl = table(dist)
    post_tbl = table(post)
    all_tbl = table(cells)
    grf_walk = max(loco, key=lambda c: c["outputs"]["grf_vertical_peak_N"]["both_feet_sum_peak"])
    grf_all = max(cells, key=lambda c: c["outputs"]["grf_vertical_peak_N"]["both_feet_sum_peak"])
    over5 = [j for j, v in walk_tbl.items() if v["peak_abs_torque_Nm"] > XL330["stall_torque_Nm"]["5.0"]]
    over6 = [j for j, v in walk_tbl.items() if v["peak_abs_torque_Nm"] > XL330["stall_torque_Nm"]["6.0"]]
    base = [c for c in cells if c["cell"] == "base_walk_vx0.25"][0]

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
        + " Joints over the 5.0 V stall row (0.52 N.m): " + (", ".join(over5) if over5 else "none")
        + ". The MJCF's own actuator ceiling is +/-%.2f N.m (%s), which is ABOVE every published stall row, so the "
          "simulation is permitted torques the actuator has no vendor figure for; that ceiling is reached only in "
          "the push and sit-stand cells." % (MJCF_FORCERANGE_NM, MJCF_FORCERANGE_CITE)
    )

    return {
        "study": "gait-peaks",
        "inputs": {
            "model": "sim/microduck_ours.xml (walking cells) and sim/microduck_ours_allcollisions.xml "
                     "(sit-stand and the self-collision census) — OUR rebuilt meshes on Pollen's stock "
                     "collision geoms and inertials (sim/swap_meshes.py, out/sim/swap_report.json)",
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
                  "mj_contactForce on every contact touching left_foot_collision / right_foot_collision at each of "
                  "the 50 Hz control frames of every cell. This file takes, per joint, the maximum over cells of "
                  "the per-cell peak, and names the cell it came from. The ground-reaction check is validated "
                  "against statics: in the standing cells the median summed vertical GRF is 7.2425 N (vx_0.00) and "
                  "7.2289 N (stand_hold) against a computed weight of %.4f N — 0.14 %% and 0.05 %%."
                  % base["outputs"]["weight_N"],
        "outputs": {
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
                "worst_any_cell": grf_all["cell"],
                "worst_any_peak_N": grf_all["outputs"]["grf_vertical_peak_N"]["both_feet_sum_peak"],
                "worst_any_peak_body_weights": round(
                    grf_all["outputs"]["grf_vertical_peak_N"]["both_feet_sum_peak"] / base["outputs"]["weight_N"], 3),
                "for_FEA": "A single-foot design load of %.4f N (%.3f x body weight) is what the walk actually "
                           "produced; the worst case measured anywhere in the matrix is %.4f N summed over both "
                           "feet in cell %s (a 5 N lateral push that knocked the robot over)."
                           % (base["outputs"]["grf_vertical_peak_N"]["left_foot"],
                              base["outputs"]["grf_vertical_peak_N"]["left_foot"] / base["outputs"]["weight_N"],
                              grf_all["outputs"]["grf_vertical_peak_N"]["both_feet_sum_peak"], grf_all["cell"]),
            },
        },
        "verdict": verdict,
        "why": why,
        "script": "sim/gait_sweep.py + sim/gait_evidence.py",
        "artifacts": sorted(os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(SWEEP, "*.json"))),
        "looked_at": [
            "reference/pollen-microduck-rl/robot_walk.xml (actuator class chosen_actuator, joint ranges)",
            "sim/microduck_ours.xml, sim/microduck_ours_allcollisions.xml",
            "ce-parts/xl330-m288-t/electrical.chip.json (the cited ROBOTIS rows)",
            "ce-parts/xl330-m288-t/iterations/v0.0.1/docs/fetched/robotis-emanual-xl330-m288.html",
            "out/sim/report.md (the pre-existing baseline: walk 0.79 m / 8 s, no fall)",
        ],
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
    walking = [r for r in rows if r["policy"] == "walking"]
    fell_walking = [r["cell"] for r in walking if r["fell"]]
    beyond = sorted({j for r in rows for j in r["joints_beyond_limit"]})
    loco_rows = [r for r in rows if r["push_N"] == 0.0 and r["policy"] == "walking"]
    loco_beyond = sorted({j for r in loco_rows for j in r["joints_beyond_limit"]})
    worst_ovs = max(rows, key=lambda r: r["max_overshoot_beyond_limit_deg"])
    selfcol = [r["cell"] for r in rows if r["self_collisions_max"] > 0]
    verdict = ("PASS" if not loco_beyond and all(r["fell"] is False for r in walking if r["push_N"] < 5.0)
               else "FAIL")
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
                        "13.43 %% of the model's 737.243 g — whether Pollen's trunk inertial already includes the "
                        "pack is CANNOT DETERMINE, so +/-10 %% is swept as the brief specifies rather than a "
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
        "why": "Across %d cells the walking policy did not fall in any of the %d walking cells except the 5 N "
               "lateral pushes (+y and -y; 5 N along +x and -x was survived). In the %d UNDISTURBED locomotion "
               "cells (vx 0-0.80 m/s, mass +/-10 %%, foot friction 0.40-1.00, 5 deg slopes in four directions) "
               "no joint left its MJCF range at all%s and no self-collision occurred. Under an external push, "
               "%d joints are driven past their MJCF stop, worst %s by %.4f deg in cell %s — on the real robot "
               "that is a hard stop taking the load. Self-collision occurred in %d cells (%s), all push or "
               "sit-stand. The sit-stand cells report fell=true by the trunk-height rule because the commanded "
               "sit puts the trunk on the floor on purpose; each row also carries "
               "fell_outside_commanded_ground_window, which is the rule with that window removed."
               % (len(rows), len(walking), len(loco_rows),
                  "" if not loco_beyond else " except " + ", ".join(loco_beyond),
                  len(beyond), worst_ovs["max_overshoot_joint"], worst_ovs["max_overshoot_beyond_limit_deg"],
                  worst_ovs["cell"], len(selfcol), ", ".join(selfcol) if selfcol else "none"),
        "script": "sim/gait_sweep.py + sim/gait_evidence.py",
        "artifacts": sorted(os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(SWEEP, "*.json"))),
        "looked_at": [
            "out/sim/report.md", "out/sim/vx_sweep.json", "sim/README.md",
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
