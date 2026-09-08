#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""skeptic_f1_recheck.py — INDEPENDENT re-measurement of lane F1 (structural).

Written by the F1 skeptic, 2026-09-03. Nothing here reads lane F1's derived
numbers and agrees with them: every check recomputes the quantity from the
primary source (the MJCF, the policy run, the CalculiX .frd) and then compares.

Run:
    /Applications/FreeCAD.app/Contents/Resources/bin/python sim/skeptic_f1_recheck.py
Writes out/sim-evidence/skeptic_f1_recheck.json.

Checks
  1 mass        sum of <inertial mass> in robot_walk.xml           vs loads_mujoco.json
  2 walk peak   8 s of BEST_alpha_walking re-run from the STAND    vs loads_mujoco.json
                keyframe, contact forces summed independently
  3 von Mises   max nodal von Mises recomputed from the raw .frd   vs each study's outputs
                stress tensor for every committed solver deck
  4 SF          yield / peak von Mises for every study             vs outputs.sf
  5 census      what tools/gen_structural.py PUBLISHES             vs what is on disk
  6 fatigue     the lane's OWN S-N design curve applied to every    (the lane applied it
                walk study, not only the ankle                      to the ankle alone)
  7 buckling    the shin's axial load factor recomputed on the      vs the published 0.9262
                MEASURED axial component, not the vector magnitude
"""
import glob
import json
import math
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EVID = os.path.join(ROOT, "out", "sim-evidence")
sys.path.insert(0, HERE)

R = {"study": "skeptic_f1_recheck", "generated": "2026-09-03",
     "script": "sim/skeptic_f1_recheck.py", "checks": []}


def add(name, verdict, ours, theirs, note):
    R["checks"].append({"check": name, "verdict": verdict, "recomputed": ours,
                        "published": theirs, "note": note})
    print("%-26s %-18s %s" % (name, verdict, note))


# ---------------------------------------------------------------------------
def check_mass(L):
    xml = os.path.join(ROOT, "reference/pollen-microduck-rl/robot_walk.xml")
    ms = [float(e.get("mass")) for e in ET.parse(xml).getroot().iter("inertial")]
    ours = round(sum(ms), 6)
    theirs = L["model"]["mass_kg_from_mjcf_inertials"]
    add("mass_kg", "PASS" if abs(ours - theirs) < 1e-6 else "FAIL", ours, theirs,
        "%d <inertial> masses in %s" % (len(ms), os.path.relpath(xml, ROOT)))


# ---------------------------------------------------------------------------
def check_walk_peak(L):
    """Re-run the policy from scratch and sum the floor contact forces myself."""
    import numpy as np
    import mujoco
    import common
    import run_policy
    from common import CTRL_DT, DECIMATION

    m = mujoco.MjModel.from_xml_path(os.path.join(EVID, "scene_loads_walk.xml"))
    d = mujoco.MjData(m)
    gid = lambda n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, n)
    lf, rf, floor = gid("left_foot_collision"), gid("right_foot_collision"), gid("floor")
    kid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_KEY, "STAND")
    mujoco.mj_resetDataKeyframe(m, d, kid)
    mujoco.mj_forward(m, d)
    run = run_policy.Runner(m, d)
    pol = run_policy.Policy(os.path.join(common.POLICY_DIR, run_policy.POLICY_FILES["walking"]))

    class A:
        vx, vy, wz, warmup = 0.25, 0.0, 0.0, 0.5

    f6 = np.zeros(6)
    best = (-1.0, None, None)
    tang = (-1.0, None)
    for k in range(int(round(8.0 / CTRL_DT))):
        tw, sit = run_policy.schedule("walking", k * CTRL_DT, A)
        run.apply(pol(run.obs(tw, sit)), pol.action_scale)
        for _ in range(DECIMATION):
            mujoco.mj_step(m, d)
            FL, FR = np.zeros(3), np.zeros(3)
            for c in range(d.ncon):
                con = d.contact[c]
                if con.geom1 == floor and con.geom2 in (lf, rf):
                    tgt, s = con.geom2, 1.0
                elif con.geom2 == floor and con.geom1 in (lf, rf):
                    tgt, s = con.geom1, -1.0
                else:
                    continue
                mujoco.mj_contactForce(m, d, c, f6)
                fw = s * np.array(con.frame).reshape(3, 3).T @ f6[:3]
                if tgt == lf:
                    FL += fw
                else:
                    FR += fw
            if d.time >= A.warmup:
                v = max(FL[2], FR[2])
                if v > best[0]:
                    best = (float(v), round(float(d.time), 4), "left" if FL[2] >= FR[2] else "right")
                tg = max(float(np.hypot(*FL[:2])), float(np.hypot(*FR[:2])))
                if tg > tang[0]:
                    tang = (tg, round(float(d.time), 4))
    ours = {"peak_vertical_grf_N": round(best[0], 4), "t_s": best[1], "foot": best[2],
            "peak_tangential_N": round(tang[0], 4)}
    theirs = {"peak_vertical_grf_N": L["walk"]["peak_vertical_grf_N"],
              "t_s": L["walk"].get("peak_time_s"), "foot": L["walk"].get("peak_foot"),
              "peak_tangential_N": L["walk"].get("peak_tangential_N")}
    ok = abs(ours["peak_vertical_grf_N"] - theirs["peak_vertical_grf_N"]) < 1e-3
    add("walk_peak_grf_N", "PASS" if ok else "FAIL", ours, theirs,
        "policy re-run from the STAND keyframe, contact forces summed independently")


# ---------------------------------------------------------------------------
def frd_peak(path):
    """max nodal von Mises and |u| straight out of a CalculiX .frd."""
    mode, vm, dm, n = None, 0.0, 0.0, 0
    for line in open(path, errors="replace"):
        s = line.rstrip("\n")
        if len(s) > 5 and s[1:3] == "-4":
            name = s[5:13].strip()
            mode = "S" if name == "STRESS" else ("D" if name == "DISP" else None)
            continue
        if len(s) > 5 and s[1:3] == "-3":
            mode = None
            continue
        if mode and s.startswith(" -1"):
            body, vals = s[13:], []
            for i in range(0, len(body), 12):
                t = body[i:i + 12].strip()
                if t:
                    try:
                        vals.append(float(t))
                    except ValueError:
                        pass
            if mode == "S" and len(vals) >= 6:
                sxx, syy, szz, sxy, syz, szx = vals[:6]
                vm = max(vm, math.sqrt(0.5 * ((sxx - syy) ** 2 + (syy - szz) ** 2 + (szz - sxx) ** 2)
                                       + 3 * (sxy ** 2 + syz ** 2 + szx ** 2)))
                n += 1
            if mode == "D" and len(vals) >= 3:
                dm = max(dm, math.sqrt(sum(v * v for v in vals[:3])))
    return vm, dm, n


def check_frd(studies):
    rows, bad = [], 0
    for r in studies:
        o = r.get("outputs") or {}
        if o.get("max_von_mises_mpa") is None:
            continue
        deck = None
        for a in r.get("artifacts", []):
            cand = os.path.join(ROOT, a, os.path.basename(a) + ".frd")
            if os.path.isdir(os.path.join(ROOT, a)):
                g = glob.glob(os.path.join(ROOT, a, "*.frd"))
                if g:
                    deck = g[0]
                    break
        if not deck:
            continue
        vm, dm, n = frd_peak(deck)
        ok = abs(vm - o["max_von_mises_mpa"]) < 1e-4 and abs(dm - o["max_displacement_mm"]) < 1e-4
        bad += 0 if ok else 1
        rows.append({"study": r["study"], "nodes": n, "vm_from_frd_mpa": round(vm, 6),
                     "vm_published_mpa": o["max_von_mises_mpa"], "disp_from_frd_mm": round(dm, 6),
                     "disp_published_mm": o["max_displacement_mm"], "agrees": ok})
    add("von_mises_from_frd", "PASS" if rows and bad == 0 else ("FAIL" if bad else "CANNOT DETERMINE"),
        rows, None, "%d decks re-reduced from the raw CalculiX .frd, %d disagree" % (len(rows), bad))


def check_sf(studies):
    bad = []
    for r in studies:
        o = r.get("outputs") or {}
        if o.get("sf") is None:
            continue
        calc = o["yield_mpa_used"] / o["max_von_mises_mpa"]
        if abs(calc - o["sf"]) > 1e-9:
            bad.append({"study": r["study"], "recomputed": calc, "published": o["sf"]})
    add("sf_arithmetic", "PASS" if not bad else "FAIL", {"disagree": bad}, None,
        "SF = yield / peak von Mises on every study with a solve")


# ---------------------------------------------------------------------------
def check_census(studies):
    """What the generator PUBLISHES vs what is on disk."""
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import gen_structural
    pub = {r["study"] for r in gen_structural.fea_studies()}
    disk = {r["study"] for r in studies}
    missing = sorted(disk - pub)
    worst = None
    for r in studies:
        if r["study"] in missing and (r.get("outputs") or {}).get("sf") is not None:
            if worst is None or r["outputs"]["sf"] < worst[1]:
                worst = (r["study"], r["outputs"]["sf"], r["verdict"])
    add("published_study_census", "FAIL" if missing else "PASS",
        {"on_disk": len(disk), "published": len(pub), "dropped": missing,
         "worst_dropped": worst},
        {"statbar_load_cases": len(pub)},
        "tools/gen_structural.py:79 and sim/fea_evidence.py:19 skip any file whose "
        "basename contains '_h' — which is every *_head_drop study, not just the "
        "*_h<size> convergence sub-runs they meant")


# ---------------------------------------------------------------------------
def check_fatigue_scope(studies, fat):
    cpk = fat["inputs"]["gait"]["cycles_per_km"]
    lim = fat["outputs"]["curves"][0]["design_endurance_sigma_max_2e6_mpa"]
    med = fat["outputs"]["curves"][0]["median_R0_sigma_max_2e6_mpa_theta0"]
    k = fat["outputs"]["curves"][0]["k"]
    nref = 2e6
    rows = []
    for r in studies:
        o = r.get("outputs") or {}
        if r.get("case") != "walk" or o.get("max_von_mises_mpa") is None:
            continue
        s = o["max_von_mises_mpa"]
        rows.append({"part": r["part"], "sigma_walk_mpa": round(s, 4),
                     "over_design_limit": round(s / lim, 4),
                     "N_design_Ps90": nref * (lim / s) ** k,
                     "life_km_design_Ps90": nref * (lim / s) ** k / cpk,
                     "life_km_median_R0": nref * (med / s) ** k / cpk,
                     "fea_verdict": r["verdict"]})
    rows.sort(key=lambda x: -x["sigma_walk_mpa"])
    over = [r for r in rows if r["over_design_limit"] > 1.0]
    add("fatigue_scope", "FAIL" if over else "PASS",
        {"design_endurance_sigma_max_mpa": lim, "cycles_per_km": cpk, "rows": rows,
         "parts_over_the_limit": len(over)},
        {"parts_the_lane_checked": [fat["part"]]},
        "%d of %d walk studies exceed the SAME P_s>=90%% design endurance limit the "
        "ankle was judged against; the lane published a fatigue verdict for the ankle only "
        "(the least-stressed part in the set)" % (len(over), len(rows)))


# ---------------------------------------------------------------------------
def check_buckling_axial(studies):
    b = json.load(open(os.path.join(EVID, "buckling_microduck-shin.json")))
    shin = next(r for r in studies if r["study"] == "fea_microduck-shin_drop")
    axial = abs(shin["inputs"]["force_N_part_frame"][2])
    crit = b["outputs"]["critical_load_N"]
    add("buckling_shin_axial_component", "FAIL",
        {"axial_component_N": round(axial, 5), "critical_load_N": crit,
         "factor_on_axial_component": round(crit / axial, 4),
         "lowest_factor_gap_to_next": round(b["outputs"]["buckle"]["factors"][1]
                                            / b["outputs"]["buckle"]["factors"][0], 3),
         "cells": b["outputs"]["buckle"]["cells"], "cell_mm": b["inputs"]["cell_mm"]},
        {"published_factor": b["outputs"]["buckle"]["factors"][0]},
        "the study applies the 118.8160 N vector MAGNITUDE as pure axial compression, but "
        "the measured axial component is %.5f N; on that the factor is %.4f, not %.4f. "
        "Verdict still FAIL (rule >= 2). One voxel cell size, no convergence, and the same "
        "solver produced a spurious ~1.0 localised factor on the rigidity plate."
        % (axial, crit / axial, b["outputs"]["buckle"]["factors"][0]))


# ---------------------------------------------------------------------------
def check_regeneration():
    p = os.path.join(ROOT, "STRUCTURAL.html")
    before = open(p, "rb").read()
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "gen_structural.py")],
                   capture_output=True, cwd=ROOT)
    after = open(p, "rb").read()
    add("generator_byte_identical", "PASS" if before == after else "FAIL",
        {"bytes": len(after)}, {"bytes": len(before)},
        "tools/gen_structural.py re-run over the same data")


# ---------------------------------------------------------------------------
def main():
    L = json.load(open(os.path.join(EVID, "loads_mujoco.json")))
    fat = json.load(open(os.path.join(EVID, "fatigue_ankle.json")))
    studies = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(EVID, "fea_microduck-*.json")))]
    check_mass(L)
    check_walk_peak(L)
    check_frd(studies)
    check_sf(studies)
    check_census(studies)
    check_fatigue_scope(studies, fat)
    check_buckling_axial(studies)
    check_regeneration()
    v = [c["verdict"] for c in R["checks"]]
    R["verdict"] = "FAIL" if "FAIL" in v else ("CANNOT DETERMINE" if "CANNOT DETERMINE" in v else "PASS")
    out = os.path.join(EVID, "skeptic_f1_recheck.json")
    json.dump(R, open(out, "w"), indent=1)
    print("\n%s  ->  %s" % (R["verdict"], out))


if __name__ == "__main__":
    main()
