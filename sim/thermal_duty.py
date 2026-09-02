#!/usr/bin/env python3
"""LANE F3 -- the MEASURED electro-thermal duty of every XL330 joint during the walk.

run_policy.py records qpos/qvel/ctrl but NOT the actuator force, so the servo
thermal study had no load to work from.  This runs the same policy loop
(identical construction: sim/run_policy.py Runner + Policy, same DEFAULT_POSE,
same 50 Hz control / 0.005 s physics / decimation 4) and additionally records,
at EVERY physics step (200 Hz, not 50 Hz -- a peak between two control ticks is
still a peak the winding sees):

    data.actuator_force[i]      N.m at joint i (MuJoCo position servo output)
    data.qfrc_constraint        -> vertical ground reaction, summed over foot
                                   contacts with the floor geom

and reports per joint: peak |tau|, RMS tau over the commanded window, and the
duty statistic the winding model needs, mean(tau^2) -- because copper loss is
I^2 R and I is proportional to tau, so mean(tau^2) is the ONLY average that
maps linearly onto heat.  A "mean torque" would understate it.

Units: N.m, N, s.  Written by lane F3, 2026-09-02.

    ce-cad/bin/cad sim/thermal_duty.py --seconds 12 --vx 0.25

Output: out/sim-evidence/gait-torque-duty.json
"""

import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import common                                                    # noqa: E402
import run_policy as rp                                          # noqa: E402
from common import CTRL_DT, DECIMATION, JOINT_NAMES, NUM_JOINTS  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--robot", default="sim/microduck_ours.xml")
    ap.add_argument("--policy", default="walking")
    ap.add_argument("--seconds", type=float, default=12.0)
    ap.add_argument("--vx", type=float, default=0.25)
    ap.add_argument("--vy", type=float, default=0.0)
    ap.add_argument("--wz", type=float, default=0.0)
    ap.add_argument("--warmup", type=float, default=0.5)
    ap.add_argument("--start", default="STAND")
    ap.add_argument("--out", default="out/sim-evidence/gait-torque-duty.json")
    ap.add_argument("--cell", default="baseline_walk_vx0.25",
                    help="the name this duty cell is recorded under; when it names a "
                         "cell of lane F2's sweep (sim/gait_sweep.py) the two are "
                         "directly comparable because the model mods are the same")
    ap.add_argument("--slope-deg", type=float, default=0.0)
    ap.add_argument("--slope-dir", default=None,
                    choices=[None, "up", "down", "side_left", "side_right"])
    args = ap.parse_args()

    import mujoco

    scene = os.path.join(REPO, "out/sim/scene_thermal_duty_%s.xml" % args.cell)
    model, _ = common.load_model(args.robot, scene)
    data = mujoco.MjData(model)
    kid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, args.start)
    assert kid >= 0, args.start
    mujoco.mj_resetDataKeyframe(model, data, kid)
    mujoco.mj_forward(model, data)

    # slope EXACTLY as lane F2 does it (sim/gait_sweep.py:77-81): the floor stays
    # flat and gravity is rotated, so the same policy sees the same contact model.
    slope_rec = None
    if args.slope_deg:
        import math as _m
        downhill = {"up": (-1.0, 0.0), "down": (1.0, 0.0),
                    "side_left": (0.0, 1.0), "side_right": (0.0, -1.0)}
        dx, dy = downhill[args.slope_dir]
        th = _m.radians(args.slope_deg)
        G = 9.81
        model.opt.gravity[:] = [G * _m.sin(th) * dx, G * _m.sin(th) * dy,
                                -G * _m.cos(th)]
        slope_rec = {"slope_deg": args.slope_deg, "slope_dir": args.slope_dir,
                     "gravity_m_s2": [round(float(v), 6) for v in model.opt.gravity],
                     "basis": "sim/gait_sweep.py:77-81 SLOPE_DOWNHILL, G = 9.81 -- "
                              "the floor stays flat and gravity is rotated"}
        mujoco.mj_forward(model, data)

    pol = rp.Policy(os.path.join(common.POLICY_DIR, rp.POLICY_FILES[args.policy]))
    runner = rp.Runner(model, data)
    floor_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, "floor")

    n_ctrl = int(round(args.seconds / CTRL_DT))
    tau = np.zeros((n_ctrl * DECIMATION, NUM_JOINTS))
    omega = np.zeros((n_ctrl * DECIMATION, NUM_JOINTS))
    t_phys = np.zeros(n_ctrl * DECIMATION)
    grf = np.zeros(n_ctrl * DECIMATION)          # total vertical floor reaction, N
    trunk_z = np.zeros(n_ctrl * DECIMATION)
    k = 0
    for step in range(n_ctrl):
        t = step * CTRL_DT
        twist, sit = rp.schedule(args.policy, t, args)
        o = runner.obs(twist, sit)
        a = pol(o)
        runner.apply(a, pol.action_scale)
        for _ in range(DECIMATION):
            mujoco.mj_step(model, data)
            tau[k] = data.actuator_force[:NUM_JOINTS]
            omega[k] = data.qvel[runner.qvel_idx]
            t_phys[k] = (k + 1) * model.opt.timestep
            fz = 0.0
            for ci in range(data.ncon):
                c = data.contact[ci]
                if c.geom1 == floor_id or c.geom2 == floor_id:
                    f = np.zeros(6)
                    mujoco.mj_contactForce(model, data, ci, f)
                    # contact frame: f[0] is the normal component along
                    # c.frame[0:3]; project onto world +z
                    fz += abs(float(f[0]) * float(c.frame[2]))
            grf[k] = fz
            trunk_z[k] = float(data.qpos[runner.root_qadr + 2])
            k += 1

    win = t_phys >= args.warmup                 # after the warm-up, command live
    body_mass = float(sum(model.body_mass))
    g = float(abs(model.opt.gravity[2]))
    weight_N = body_mass * g

    joints = {}
    for j, name in enumerate(JOINT_NAMES):
        s = tau[win, j]
        w = omega[win, j]
        p_mech = s * w                      # W at the output shaft, signed
        joints[name] = {
            "peak_abs_rad_s": round(float(np.max(np.abs(w))), 6),
            "rms_rad_s": round(float(np.sqrt(np.mean(w ** 2))), 6),
            "mean_mech_power_W": round(float(np.mean(p_mech)), 6),
            "mean_positive_mech_power_W": round(float(np.mean(np.clip(p_mech, 0, None))), 6),
            "peak_mech_power_W": round(float(np.max(p_mech)), 6),
            "peak_abs_Nm": round(float(np.max(np.abs(s))), 6),
            "rms_Nm": round(float(np.sqrt(np.mean(s ** 2))), 6),
            "mean_tau_squared_Nm2": round(float(np.mean(s ** 2)), 8),
            "mean_abs_Nm": round(float(np.mean(np.abs(s))), 6),
            "p95_abs_Nm": round(float(np.percentile(np.abs(s), 95)), 6),
            "frac_time_above_half_stall_5V": round(
                float(np.mean(np.abs(s) > 0.26)), 5),
        }

    out = {
        "study": "gait-torque-duty",
        "what": ("per-joint actuator torque of the XL330 joints under Pollen's "
                 "own walking policy, recorded at the PHYSICS step (200 Hz), "
                 "and the vertical ground reaction. The load basis for every "
                 "thermal number in lane F3."),
        "inputs": {
            "cell": args.cell,
            "slope": slope_rec,
            "robot": args.robot,
            "scene": os.path.relpath(scene, REPO),
            "policy_file": rp.POLICY_FILES[args.policy],
            "policy": args.policy,
            "command": {"vx_m_s": args.vx, "vy_m_s": args.vy, "wz_rad_s": args.wz,
                        "warmup_s": args.warmup},
            "seconds": args.seconds,
            "timestep_s": float(model.opt.timestep),
            "decimation": DECIMATION,
            "control_hz": 1.0 / CTRL_DT,
            "record_hz": 1.0 / float(model.opt.timestep),
            "actuator_class": ("chosen_actuator: kp 0.55, kv 0.0, "
                               "forcerange -0.96..0.96 N.m, joint damping 0.053, "
                               "frictionloss 0.0048, armature 0.0018 "
                               "(sim/microduck_ours.xml:41-48)"),
            "model_mass_kg": round(body_mass, 6),
            "gravity_m_s2": g,
            "weight_N": round(weight_N, 5),
        },
        "method": ("mj_step at 0.005 s; data.actuator_force read after every "
                   "step; ground reaction from mj_contactForce on every contact "
                   "touching geom 'floor', normal component projected onto world "
                   "+z. Statistics taken over t >= warmup only (the commanded "
                   "window). mean(tau^2) is reported because copper loss is "
                   "I^2 R and I is proportional to torque -- the mean of the "
                   "SQUARE is the only average that maps linearly onto heat."),
        "outputs": {
            "joints": joints,
            "peak_joint": max(joints, key=lambda n: joints[n]["peak_abs_Nm"]),
            "peak_abs_Nm": max(j["peak_abs_Nm"] for j in joints.values()),
            "worst_rms_joint": max(joints, key=lambda n: joints[n]["rms_Nm"]),
            "worst_rms_Nm": max(j["rms_Nm"] for j in joints.values()),
            "grf_vertical_N": {
                "peak": round(float(np.max(grf[win])), 5),
                "mean": round(float(np.mean(grf[win])), 5),
                "peak_over_weight": round(float(np.max(grf[win]) / weight_N), 5),
            },
            "trunk_z_m": {"min": round(float(np.min(trunk_z[win])), 5),
                          "max": round(float(np.max(trunk_z[win])), 5)},
            "fell": bool(np.min(trunk_z[win]) < 0.06),
        },
        "verdict": "PASS",
        "why": "",
        "script": "sim/thermal_duty.py",
        "artifacts": [os.path.relpath(scene, REPO)],
        "looked_at": ["sim/run_policy.py", "sim/common.py", "sim/microduck_ours.xml"],
    }
    fell = out["outputs"]["fell"]
    out["verdict"] = "CANNOT DETERMINE" if fell else "PASS"
    out["why"] = (
        "the duck fell inside the measurement window, so these torques are a "
        "fall, not a gait" if fell else
        "%d joints measured over %.1f s of commanded walking at vx = %.3f m/s; "
        "peak %.4f N.m at %s, worst RMS %.4f N.m at %s. The MJCF's own force "
        "limit is 0.96 N.m and the vendor's 5.0 V stall torque is 0.52 N.m "
        "(ce-parts/xl330-m288-t/electrical.chip.json current_mA.stall_basis) -- "
        "both are quoted in the servo thermal study, not asserted here."
        % (NUM_JOINTS, args.seconds - args.warmup, args.vx,
           out["outputs"]["peak_abs_Nm"], out["outputs"]["peak_joint"],
           out["outputs"]["worst_rms_Nm"], out["outputs"]["worst_rms_joint"]))

    path = os.path.join(REPO, args.out)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps({"wrote": args.out, "verdict": out["verdict"],
                      "peak_Nm": out["outputs"]["peak_abs_Nm"],
                      "peak_joint": out["outputs"]["peak_joint"],
                      "worst_rms_Nm": out["outputs"]["worst_rms_Nm"],
                      "grf": out["outputs"]["grf_vertical_N"]}, indent=1))


if __name__ == "__main__":
    main()
