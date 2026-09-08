#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""skeptic_f2_recheck.py — INDEPENDENT re-measurement of lane F2's gait sweep.

Written by the F2 skeptic, not by F2. It shares only sim/common.py and
sim/run_policy.py (both untouched since commit 2e0bc77, i.e. they predate F2)
and re-implements the recording loop, the aggregation and the electrical model
from scratch, so agreeing with out/sim-evidence/gait-peaks.json is evidence and
not a tautology.

What it measured (2026-09-02), against the committed F2 files:

  AGREES EXACTLY (5 dp) on: total mass 0.737243 kg / weight 7.2324 N; all 14
  per-joint peak torques of base_walk_vx0.25, slope5_side_left, mu_0.40 and
  vx_0.00; walked_m; push_5N_lat fell=true; the 93.0579 N summed foot reaction;
  the 23.3897 N single-foot walking peak; head_yaw's 7.6355 deg overshoot and
  4 self-contacts in push_5N_lat_neg; 0.0000 deg overshoot in vx_0.80; and the
  battery model's 8.9553 W walking / 2.8301 W standing and 1.8784-1.3400 h.

  DISAGREES WITH THE READING PUT ON THEM in one place, measured by --postfall:
  sim/microduck_ours.xml gives only 2 of its 85 geoms a floor-colliding contype
  (the two soles), so once the robot tips the body passes THROUGH the floor.
  The 93.0579 N that gait-peaks.json offers under "for_FEA" as the worst case
  in the matrix occurs at t = 6.565 s, 0.105 s AFTER the fall at 6.46 s, with
  the trunk 47.4 mm below the floor plane. The largest PRE-fall value is
  62.9594 N at 6.320 s. A design load must come from the pre-fall record.

Run:  ce-cad/bin/cad sim/skeptic_f2_recheck.py [--cells base,push5,slope,vx0,mu04]
      ce-cad/bin/cad sim/skeptic_f2_recheck.py --postfall
      ce-cad/bin/cad sim/skeptic_f2_recheck.py --range
      ce-cad/bin/cad sim/skeptic_f2_recheck.py --battery
"""
import argparse
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
from common import CTRL_DT, DECIMATION, JOINT_NAMES, NUM_JOINTS  # noqa: E402
from run_policy import FALL_TILT_DEG, FALL_Z, POLICY_FILES, Policy, Runner, schedule  # noqa: E402

ROOT = common.ROOT
TMP = os.path.join(ROOT, "out", "sim-sweep", "_skeptic")
G = 9.81
# ROBOTIS e-Manual XL330-M288-T Specifications, 5.0 V row, verbatim:
# "0.52 [N.m] (at 5.0 [V], 1.47 [A], 0.354 [Nm/A])" ; "103 [rev/min] (at 5.0 [V])"
STALL_TAU, STALL_I, NOLOAD_RPM, V_ROW = 0.52, 1.47, 103.0, 5.0
STANDBY_A, N_SERVOS, V_PACK, PACK_WH = 0.017, 15, 7.4, 18.7


def simulate(name, robot="ours", vx=0.25, seconds=12.0, warmup=0.5, start="STAND",
             mass_scale=1.0, friction=None, slope=None, push=None, policy="walking"):
    """Run one cell. Returns every per-physics-step array the checks below need."""
    import mujoco
    os.makedirs(TMP, exist_ok=True)
    model, _ = common.load_model(robot, os.path.join(TMP, "scene_%s.xml" % name))
    data = mujoco.MjData(model)
    floor = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, "floor")
    feet = [mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, n)
            for n in ("left_foot_collision", "right_foot_collision")]
    if mass_scale != 1.0:
        model.body_mass[:] = model.body_mass * mass_scale
        model.body_inertia[:] = model.body_inertia * mass_scale
    if friction is not None:
        for g in [floor] + feet:
            model.geom_friction[g, 0] = friction
    if slope is not None:
        deg, (dx, dy) = slope
        th = math.radians(deg)
        model.opt.gravity[:] = [G * math.sin(th) * dx, G * math.sin(th) * dy, -G * math.cos(th)]
    total_mass = float(model.body_mass.sum())

    kid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, start)
    mujoco.mj_resetDataKeyframe(model, data, kid)
    mujoco.mj_forward(model, data)
    pol = Policy(os.path.join(common.POLICY_DIR, POLICY_FILES[policy]))
    rn = Runner(model, data)
    n = int(round(seconds / CTRL_DT))
    args = argparse.Namespace(vx=vx, vy=0.0, wz=0.0, warmup=warmup, sit_at=1.0, stand_at=4.5)

    P = n * DECIMATION + 1
    tau = np.zeros((P, NUM_JOINTS))
    jq = np.zeros((P, NUM_JOINTS))
    jv = np.zeros((P, NUM_JOINTS))
    grfz = np.zeros((P, 2))
    trunk_z_p = np.zeros(P)
    min_geom_z = np.zeros(P)
    tilt = np.zeros(n + 1)
    trunk_z = np.zeros(n + 1)
    nself = np.zeros(n + 1, int)
    w = np.zeros(6)
    xy0 = data.qpos[rn.root_qadr:rn.root_qadr + 2].copy()

    def phys(k):
        tau[k] = data.actuator_force
        jq[k] = data.qpos[rn.qpos_idx]
        jv[k] = data.qvel[rn.qvel_idx]
        trunk_z_p[k] = data.qpos[rn.root_qadr + 2]
        min_geom_z[k] = float(data.geom_xpos[:, 2].min())
        for i in range(data.ncon):
            c = data.contact[i]
            for kk, g in enumerate(feet):
                if c.geom1 == g or c.geom2 == g:
                    mujoco.mj_contactForce(model, data, i, w)
                    fw = c.frame.reshape(3, 3).T @ w[:3]
                    grfz[k, kk] += (1.0 if c.geom2 == g else -1.0) * float(fw[2])

    def ctrl(i):
        q = data.qpos[rn.root_qadr + 3:rn.root_qadr + 7]
        r, p = common.quat_to_roll_pitch(q)
        trunk_z[i] = data.qpos[rn.root_qadr + 2]
        tilt[i] = math.degrees(max(abs(r), abs(p)))
        nself[i] = rn.self_contacts()

    ctrl(0)
    phys(0)
    for k in range(n):
        t = k * CTRL_DT
        twist, sit = schedule(policy, t, args)
        rn.apply(pol(rn.obs(twist, sit)), pol.action_scale)
        data.xfrc_applied[:] = 0.0
        if push is not None and push[1] <= t < push[1] + push[2]:
            d = np.array(push[3], float)
            data.xfrc_applied[rn.trunk_id, 0:3] = push[0] * d / np.linalg.norm(d)
        for j in range(DECIMATION):
            mujoco.mj_step(model, data)
            phys(k * DECIMATION + j + 1)
        ctrl(k + 1)

    tv = np.arange(n + 1) * CTRL_DT
    fell_mask = (trunk_z < FALL_Z) | (tilt > FALL_TILT_DEG)
    lo = np.array([model.jnt_range[model.actuator_trnid[i, 0], 0] for i in range(model.nu)])
    hi = np.array([model.jnt_range[model.actuator_trnid[i, 0], 1] for i in range(model.nu)])
    end = data.qpos[rn.root_qadr:rn.root_qadr + 2]
    return {
        "name": name, "model": model, "total_mass_kg": total_mass,
        "weight_N": total_mass * G, "tau": tau, "jq": jq, "jv": jv,
        "grfz": grfz, "trunk_z_phys": trunk_z_p, "min_geom_z": min_geom_z,
        "phys_time": np.arange(P) * float(model.opt.timestep),
        "fell": bool(fell_mask.any()),
        "first_fall_s": float(tv[np.argmax(fell_mask)]) if fell_mask.any() else None,
        "walked_m": float(np.linalg.norm(end - xy0)),
        "walked_x_m": float(end[0] - xy0[0]), "walked_y_m": float(end[1] - xy0[1]),
        "self_contacts_max": int(nself.max()), "lo": lo, "hi": hi,
    }


def report_cell(r):
    print("== %s" % r["name"])
    print("   mass %.6f kg  weight %.4f N  fell %s  first_fall_s %s"
          % (r["total_mass_kg"], r["weight_N"], r["fell"],
             ("%.3f" % r["first_fall_s"]) if r["first_fall_s"] is not None else "None"))
    print("   walked %.5f m  (x %+.5f, y %+.5f)" % (r["walked_m"], r["walked_x_m"], r["walked_y_m"]))
    for i, jn in enumerate(JOINT_NAMES):
        print("     %-16s peak |tau| %.5f N.m" % (jn, float(np.abs(r["tau"][:, i]).max())))
    s = r["grfz"].sum(axis=1)
    print("   GRFz: median summed %.4f N | max single foot %.4f N | max summed %.4f N"
          % (float(np.median(s)), float(r["grfz"].max()), float(s.max())))


def check_postfall():
    """The claim under test: gait-peaks.json's for_FEA worst case, 93.0579 N."""
    import mujoco
    r = simulate("push_5N_lat", push=(5.0, 6.0, 0.2, (0.0, 1.0, 0.0)))
    m = r["model"]
    floor = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, "floor")
    can = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g) for g in range(m.ngeom)
           if g != floor and (m.geom_contype[g] & m.geom_conaffinity[floor]
                              or m.geom_contype[floor] & m.geom_conaffinity[g])]
    print("geoms in sim/microduck_ours.xml that can contact the floor: %d of %d -> %s"
          % (len(can), m.ngeom, can))
    t, s = r["phys_time"], r["grfz"].sum(axis=1)
    i = int(s.argmax())
    ff = r["first_fall_s"]
    pre = t < ff
    print("fall detected at %.3f s (fall rule: trunk z < %.2f m or tilt > %.0f deg)"
          % (ff, FALL_Z, FALL_TILT_DEG))
    print("peak summed vertical GRF %.4f N at t = %.3f s -> %s the fall"
          % (s[i], t[i], "AFTER" if t[i] >= ff else "before"))
    print("  trunk z there %.5f m ; lowest geom centre there %.5f m" % (r["trunk_z_phys"][i], r["min_geom_z"][i]))
    print("largest PRE-fall summed GRF %.4f N at t = %.3f s" % (s[pre].max(), t[pre][s[pre].argmax()]))
    print("trunk z minimum over the run %.5f m ; lowest geom centre %.5f m"
          % (r["trunk_z_phys"].min(), r["min_geom_z"].min()))
    n_under = int((r["min_geom_z"] < -0.005).sum())
    print("physics frames with a geom centre below the floor: %d of %d (%.1f %%)"
          % (n_under, len(r["min_geom_z"]), 100.0 * n_under / len(r["min_geom_z"])))


def check_range():
    for r in (simulate("vx_0.80", vx=0.80),
              simulate("push_5N_lat_neg", push=(5.0, 6.0, 0.2, (0.0, -1.0, 0.0)))):
        lo, hi, jq = r["lo"], r["hi"], r["jq"]
        print("== %s   self-contacts max %d" % (r["name"], r["self_contacts_max"]))
        worst, wj = 0.0, None
        for i, jn in enumerate(JOINT_NAMES):
            ov = max(0.0, float(lo[i] - jq[:, i].min()), float(jq[:, i].max() - hi[i]))
            if ov > 0:
                print("   past its MJCF stop: %-16s %.4f deg" % (jn, math.degrees(ov)))
            if ov > worst:
                worst, wj = ov, jn
        print("   worst overshoot: %s %.4f deg" % (wj, math.degrees(worst)))


def check_battery():
    """Re-derive the motor constants and the runtime from the committed trajectories."""
    kT = STALL_TAU / STALL_I
    R = V_ROW / STALL_I
    w0 = NOLOAD_RPM * 2 * math.pi / 60.0
    kE = V_ROW / w0
    print("kT %.6f N.m/A   R %.6f ohm   w0 %.6f rad/s   kE %.6f V.s/rad" % (kT, R, w0, kE))
    for label, rel, t0 in (("walking", "out/sim-sweep/base_walk_vx0.25_traj.npz", 0.5),
                           ("standing", "out/sim-sweep/stand_hold_traj.npz", 1.0)):
        z = np.load(os.path.join(ROOT, rel), allow_pickle=True)
        t = z["phys_time"]
        m = t >= t0
        tau, jv = z["tau"][m], z["jv"][m]
        I = np.abs(tau) / kT
        Vm = kE * np.abs(jv) + R * I
        P = np.minimum(Vm, V_PACK) * I
        tot = P.sum(axis=1) + N_SERVOS * STANDBY_A * V_PACK
        print("%s: %d frames %.3f-%.3f s | servo total mean %.4f W peak %.4f W | pack %.4f/%.4f A"
              % (label, int(m.sum()), t[m][0], t[m][-1], tot.mean(), tot.max(),
                 tot.mean() / V_PACK, tot.max() / V_PACK))
        print("   frames needing Vm > V_pack: %d of %d" % (int((Vm > V_PACK).sum()), Vm.size))
        for c in (0.0, 1.0, 2.0, 3.0, 5.0):
            print("   + %.1f W compute -> %.4f h on %.1f Wh" % (c, PACK_WH / (tot.mean() + c), PACK_WH))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", default="")
    ap.add_argument("--postfall", action="store_true")
    ap.add_argument("--range", action="store_true")
    ap.add_argument("--battery", action="store_true")
    a = ap.parse_args()
    known = {
        "base": lambda: simulate("base_walk_vx0.25"),
        "push5": lambda: simulate("push_5N_lat", push=(5.0, 6.0, 0.2, (0.0, 1.0, 0.0))),
        "slope": lambda: simulate("slope5_side_left", slope=(5.0, (0.0, 1.0))),
        "vx0": lambda: simulate("vx_0.00", vx=0.0),
        "mu04": lambda: simulate("mu_0.40", friction=0.40),
    }
    if a.cells:
        for c in a.cells.split(","):
            report_cell(known[c.strip()]())
    if a.postfall:
        check_postfall()
    if a.range:
        check_range()
    if a.battery:
        check_battery()
    if not (a.cells or a.postfall or a.range or a.battery):
        ap.error("give --cells and/or --postfall / --range / --battery")


if __name__ == "__main__":
    main()
