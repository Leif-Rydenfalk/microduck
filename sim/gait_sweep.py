#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""gait_sweep.py — MuJoCo gait-robustness sweep for the Microduck (lane F2).

Drives OUR model (sim/microduck_ours.xml, sim/microduck_ours_allcollisions.xml)
with Pollen's published ONNX policies through a matrix of perturbations and
records, per cell: fell / did not fall, walked distance, mean speed, the peak
actuator torque PER JOINT, joint-range utilisation vs the MJCF limits, the peak
per-foot ground-reaction force, and the self-collision count.

Everything is measured off the simulation state — nothing is asserted.

Perturbations, and exactly how each is applied to the model:
  mass_scale   model.body_mass *= s and model.body_inertia *= s (rigid-body
               scaling of every body; the geometry and the actuator are
               untouched).
  friction     model.geom_friction[:,0] set on the floor AND on both
               *_foot_collision geoms. MuJoCo mixes a contact pair's friction
               elementwise-max, so both sides must be set or the higher wins.
  slope_deg    the FLOOR STAYS FLAT and GRAVITY IS ROTATED, which is the same
               mechanics in the plane's frame: G = g*(sin(th)*dhat - cos(th)*zhat)
               with dhat the horizontal DOWNHILL direction. up: dhat=(-1,0,0)
               (the robot walks +x, so +x is uphill). down: dhat=(+1,0,0).
               side_left: dhat=(0,+1,0). side_right: dhat=(0,-1,0).
  push_N       data.xfrc_applied[trunk_base, 0:3] = F for push_dur seconds
               starting at push_at, in the WORLD frame.

Run:  /Applications/FreeCAD.app/Contents/Resources/bin/python sim/gait_sweep.py --all
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
from common import CTRL_DT, DECIMATION, DEFAULT_POSE, JOINT_NAMES, NUM_JOINTS  # noqa: E402
from run_policy import FALL_TILT_DEG, FALL_Z, POLICY_FILES, Policy, Runner, schedule  # noqa: E402

ROOT = common.ROOT
OUT = os.path.join(ROOT, "out", "sim-sweep")
G = 9.81
SLOPE_DOWNHILL = {"up": (-1.0, 0.0), "down": (1.0, 0.0), "side_left": (0.0, 1.0), "side_right": (0.0, -1.0)}


class Cfg:
    """One sweep cell. Only the fields a cell actually varies are ever set."""

    def __init__(self, name, family, policy="walking", robot="ours", seconds=12.0, vx=0.25, vy=0.0, wz=0.0,
                 warmup=0.5, start="STAND", mass_scale=1.0, friction=None, slope_deg=0.0, slope_dir=None,
                 push_N=0.0, push_dir=(0.0, 1.0, 0.0), push_at=6.0, push_dur=0.2,
                 sit_at=1.0, stand_at=4.5, save_traj=False, note=""):
        self.__dict__.update(locals())
        del self.__dict__["self"]

    def as_inputs(self):
        d = dict(self.__dict__)
        d.pop("save_traj")
        return d


def apply_model_mods(model, cfg, floor_gid, foot_gids):
    """Mutate the compiled model in place. Returns the measured state after mutation."""
    rec = {}
    if cfg.mass_scale != 1.0:
        model.body_mass[:] = model.body_mass * cfg.mass_scale
        model.body_inertia[:] = model.body_inertia * cfg.mass_scale
    rec["total_mass_kg"] = round(float(model.body_mass.sum()), 6)
    if cfg.friction is not None:
        for gid in [floor_gid] + list(foot_gids):
            model.geom_friction[gid, 0] = cfg.friction
    rec["floor_friction_slide"] = round(float(model.geom_friction[floor_gid, 0]), 4)
    rec["foot_friction_slide"] = [round(float(model.geom_friction[g, 0]), 4) for g in foot_gids]
    if cfg.slope_deg:
        dx, dy = SLOPE_DOWNHILL[cfg.slope_dir]
        th = math.radians(cfg.slope_deg)
        model.opt.gravity[:] = [G * math.sin(th) * dx, G * math.sin(th) * dy, -G * math.cos(th)]
    rec["gravity_m_s2"] = [round(float(v), 6) for v in model.opt.gravity]
    rec["gravity_magnitude_m_s2"] = round(float(np.linalg.norm(model.opt.gravity)), 6)
    return rec


def run_cell(cfg, out_dir=OUT):
    import mujoco
    os.makedirs(out_dir, exist_ok=True)
    scene = os.path.join(out_dir, "scene_%s.xml" % cfg.name)
    model, scene_path = common.load_model(cfg.robot, scene)
    data = mujoco.MjData(model)

    floor_gid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, "floor")
    foot_gids = [mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, n)
                 for n in ("left_foot_collision", "right_foot_collision")]
    assert floor_gid >= 0 and all(g >= 0 for g in foot_gids), (floor_gid, foot_gids)
    model_state = apply_model_mods(model, cfg, floor_gid, foot_gids)

    kid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, cfg.start)
    assert kid >= 0, cfg.start
    mujoco.mj_resetDataKeyframe(model, data, kid)
    mujoco.mj_forward(model, data)

    pol = Policy(os.path.join(common.POLICY_DIR, POLICY_FILES[cfg.policy]))
    rn = Runner(model, data)
    trunk_bid = rn.trunk_id
    n_steps = int(round(cfg.seconds / CTRL_DT))

    args = argparse.Namespace(vx=cfg.vx, vy=cfg.vy, wz=cfg.wz, warmup=cfg.warmup,
                              sit_at=cfg.sit_at, stand_at=cfg.stand_at)

    T = n_steps + 1
    tau = np.zeros((T, NUM_JOINTS))          # actuator_force, N.m (gear 1 -> joint torque)
    jq = np.zeros((T, NUM_JOINTS))
    jv = np.zeros((T, NUM_JOINTS))
    grf = np.zeros((T, 2))                   # per-foot |contact force| resultant, N
    grf_z = np.zeros((T, 2))                 # per-foot world +z component, N
    trunk_z = np.zeros(T)
    tilt = np.zeros(T)
    nself = np.zeros(T, int)
    ncon = np.zeros(T, int)
    tvec = np.arange(T) * CTRL_DT
    qpos_hist = np.zeros((T, model.nq))
    wrench = np.zeros(6)

    def foot_forces():
        f = np.zeros(2)
        fz = np.zeros(2)
        for i in range(data.ncon):
            c = data.contact[i]
            for k, gid in enumerate(foot_gids):
                if c.geom1 == gid or c.geom2 == gid:
                    mujoco.mj_contactForce(model, data, i, wrench)
                    frame = c.frame.reshape(3, 3)          # rows: normal, tangent1, tangent2
                    fw = frame.T @ wrench[:3]
                    sign = 1.0 if c.geom2 == gid else -1.0  # force on geom2 by convention
                    f[k] += float(np.linalg.norm(wrench[:3]))
                    fz[k] += float(sign * fw[2])
        return f, fz

    def snap(i):
        q = data.qpos[rn.root_qadr + 3:rn.root_qadr + 7]
        r, p = common.quat_to_roll_pitch(q)
        tau[i] = data.actuator_force
        jq[i] = data.qpos[rn.qpos_idx]
        jv[i] = data.qvel[rn.qvel_idx]
        a, b = foot_forces()
        grf[i], grf_z[i] = a, b
        trunk_z[i] = data.qpos[rn.root_qadr + 2]
        tilt[i] = math.degrees(max(abs(r), abs(p)))
        nself[i] = rn.self_contacts()
        ncon[i] = data.ncon
        qpos_hist[i] = data.qpos

    t0 = time.time()
    start_xy = data.qpos[rn.root_qadr:rn.root_qadr + 2].copy()
    snap(0)
    push_frames = 0
    for k in range(n_steps):
        t = k * CTRL_DT
        twist, sit = schedule(cfg.policy, t, args)
        o = rn.obs(twist, sit)
        a = pol(o)
        rn.apply(a, pol.action_scale)
        data.xfrc_applied[:] = 0.0
        if cfg.push_N and cfg.push_at <= t < cfg.push_at + cfg.push_dur:
            d = np.array(cfg.push_dir, float)
            d = d / np.linalg.norm(d)
            data.xfrc_applied[trunk_bid, 0:3] = cfg.push_N * d
            push_frames += 1
        for _ in range(DECIMATION):
            mujoco.mj_step(model, data)
        snap(k + 1)
    wall = time.time() - t0

    end_xy = qpos_hist[-1, rn.root_qadr:rn.root_qadr + 2]
    disp = end_xy - start_xy
    fell_z = trunk_z < FALL_Z
    fell_tilt = tilt > FALL_TILT_DEG
    fell = bool(np.any(fell_z | fell_tilt))
    first_fall = float(tvec[np.argmax(fell_z | fell_tilt)]) if fell else None
    excl = np.zeros(T, bool)
    if cfg.policy == "sitstand":
        excl = (tvec >= cfg.sit_at) & (tvec < cfg.stand_at + 1.5)
    elif cfg.policy == "stand" and cfg.start != "STAND":
        excl = tvec < 2.0
    fell_outside = bool(np.any((fell_z & ~excl) | fell_tilt))

    lo = np.array([model.jnt_range[model.actuator_trnid[i, 0], 0] for i in range(model.nu)])
    hi = np.array([model.jnt_range[model.actuator_trnid[i, 0], 1] for i in range(model.nu)])
    frange = model.actuator_forcerange
    margin = math.radians(1.0)

    per_joint = {}
    for i, jn in enumerate(JOINT_NAMES):
        pk = float(np.abs(tau[:, i]).max())
        pk_i = int(np.abs(tau[:, i]).argmax())
        per_joint[jn] = {
            "peak_abs_torque_Nm": round(pk, 5),
            "peak_at_s": round(float(tvec[pk_i]), 3),
            "peak_signed_torque_Nm": round(float(tau[pk_i, i]), 5),
            "p95_abs_torque_Nm": round(float(np.percentile(np.abs(tau[:, i]), 95)), 5),
            "p99_abs_torque_Nm": round(float(np.percentile(np.abs(tau[:, i]), 99)), 5),
            "rms_torque_Nm": round(float(np.sqrt(np.mean(tau[:, i] ** 2))), 5),
            "mean_abs_torque_Nm": round(float(np.abs(tau[:, i]).mean()), 5),
            "frames_at_forcerange_limit": int(np.sum(np.abs(tau[:, i]) >= 0.999 * frange[i, 1])),
            "mjcf_forcerange_Nm": [round(float(frange[i, 0]), 4), round(float(frange[i, 1]), 4)],
            "peak_abs_speed_rad_s": round(float(np.abs(jv[:, i]).max()), 4),
            "peak_abs_speed_rpm_output": round(float(np.abs(jv[:, i]).max()) * 60.0 / (2 * math.pi), 3),
            "range_rad": [round(float(lo[i]), 5), round(float(hi[i]), 5)],
            "range_deg": [round(math.degrees(lo[i]), 3), round(math.degrees(hi[i]), 3)],
            "q_min_deg": round(math.degrees(float(jq[:, i].min())), 3),
            "q_max_deg": round(math.degrees(float(jq[:, i].max())), 3),
            "range_utilisation_pct": round(float((jq[:, i].max() - jq[:, i].min()) / (hi[i] - lo[i]) * 100), 2),
            "frames_within_1deg_of_limit": int(np.sum((jq[:, i] <= lo[i] + margin) | (jq[:, i] >= hi[i] - margin))),
            "frames_beyond_limit": int(np.sum((jq[:, i] < lo[i]) | (jq[:, i] > hi[i]))),
            "max_overshoot_beyond_limit_deg": round(math.degrees(float(max(
                0.0, float(lo[i] - jq[:, i].min()), float(jq[:, i].max() - hi[i])))), 5),
        }

    cmd_mask = tvec >= (cfg.warmup if cfg.policy == "walking" else 0.0)
    xy = qpos_hist[cmd_mask][:, rn.root_qadr:rn.root_qadr + 2]
    tt = tvec[cmd_mask]
    speed = float(np.linalg.norm(xy[-1] - xy[0]) / max(tt[-1] - tt[0], 1e-9)) if len(tt) > 1 else 0.0

    out = {
        "cell": cfg.name, "family": cfg.family, "note": cfg.note,
        "inputs": cfg.as_inputs(),
        "model": {
            "robot_file": os.path.relpath(common.robot_file(cfg.robot), ROOT),
            "scene_file": os.path.relpath(scene_path, ROOT),
            "policy_file": "sim/policies/" + POLICY_FILES[cfg.policy],
            "action_scale": pol.action_scale,
            "control_hz": round(1.0 / CTRL_DT, 1), "timestep_s": float(model.opt.timestep),
            "decimation": DECIMATION, "control_steps": n_steps,
            "push_frames_applied": push_frames,
            **model_state,
        },
        "outputs": {
            "fell": fell, "fell_by_height": bool(np.any(fell_z)), "fell_by_tilt": bool(np.any(fell_tilt)),
            "first_fall_s": first_fall,
            "fell_outside_commanded_ground_window": fell_outside,
            "fall_rule": "trunk z < %.2f m or |roll|,|pitch| > %.0f deg" % (FALL_Z, FALL_TILT_DEG),
            "walked_m": round(float(np.linalg.norm(disp)), 5),
            "walked_x_m": round(float(disp[0]), 5), "walked_y_m": round(float(disp[1]), 5),
            "mean_speed_m_s": round(speed, 5),
            "trunk_z_m": {"start": round(float(trunk_z[0]), 5), "min": round(float(trunk_z.min()), 5),
                          "max": round(float(trunk_z.max()), 5), "end": round(float(trunk_z[-1]), 5)},
            "max_tilt_deg": round(float(tilt.max()), 3), "end_tilt_deg": round(float(tilt[-1]), 3),
            "max_joint_torque_Nm": round(float(np.abs(tau).max()), 5),
            "max_joint_torque_joint": JOINT_NAMES[int(np.unravel_index(np.abs(tau).argmax(), tau.shape)[1])],
            "sum_abs_torque_peak_Nm": round(float(np.abs(tau).sum(axis=1).max()), 5),
            "grf_peak_N": {"left_foot": round(float(grf[:, 0].max()), 4),
                           "right_foot": round(float(grf[:, 1].max()), 4),
                           "both_feet_sum_peak": round(float(grf.sum(axis=1).max()), 4)},
            "grf_vertical_peak_N": {"left_foot": round(float(grf_z[:, 0].max()), 4),
                                    "right_foot": round(float(grf_z[:, 1].max()), 4),
                                    "both_feet_sum_peak": round(float(grf_z.sum(axis=1).max()), 4)},
            "grf_vertical_percentiles_N": {
                "both_feet_sum_p50": round(float(np.percentile(grf_z.sum(axis=1), 50)), 4),
                "both_feet_sum_p95": round(float(np.percentile(grf_z.sum(axis=1), 95)), 4),
                "both_feet_sum_p99": round(float(np.percentile(grf_z.sum(axis=1), 99)), 4),
                "single_foot_p99": round(float(np.percentile(np.maximum(grf_z[:, 0], grf_z[:, 1]), 99)), 4),
                "single_foot_max": round(float(np.maximum(grf_z[:, 0], grf_z[:, 1]).max()), 4)},
            "weight_N": round(float(model.body_mass.sum() * np.linalg.norm(model.opt.gravity)), 4),
            "self_collisions": {"max": int(nself.max()), "frames": int(np.sum(nself > 0)),
                                "mean": round(float(nself.mean()), 4)},
            "contacts": {"mean": round(float(ncon.mean()), 3), "max": int(ncon.max())},
            "joints_beyond_limit": [j for j, h in per_joint.items() if h["frames_beyond_limit"] > 0],
            "joints_within_1deg_of_limit": [j for j, h in per_joint.items() if h["frames_within_1deg_of_limit"] > 0],
            "joints_saturating_mjcf_forcerange": [j for j, h in per_joint.items()
                                                  if h["frames_at_forcerange_limit"] > 0],
            "per_joint": per_joint,
            "nan": bool(np.any(~np.isfinite(qpos_hist))),
            "wall_seconds": round(wall, 3),
        },
    }
    json.dump(out, open(os.path.join(out_dir, cfg.name + ".json"), "w"), indent=1)
    if cfg.save_traj:
        np.savez_compressed(os.path.join(out_dir, cfg.name + "_traj.npz"), scene=scene_path, robot=cfg.robot,
                            policy=cfg.policy, ctrl_dt=CTRL_DT, root_qadr=rn.root_qadr,
                            time=tvec, qpos=qpos_hist, qvel=np.zeros((T, model.nv)), ctrl=np.zeros((T, NUM_JOINTS)),
                            action=np.zeros((T, NUM_JOINTS)), tau=tau, jq=jq, jv=jv, grf=grf, grf_z=grf_z,
                            trunk_z=trunk_z, roll=np.zeros(T), pitch=np.zeros(T), ncon=ncon, nself=nself)
    return out


def matrix():
    """The sweep matrix. Baselines first so gait-peaks.json can be written early."""
    cells = []
    cells.append(Cfg("base_walk_vx0.25", "baseline", vx=0.25, seconds=12.0, save_traj=True,
                     note="the reference walk: our meshes, stock physics, browser-simulator VEL_FWD"))
    for vx in (0.00, 0.05, 0.10, 0.15, 0.20, 0.30, 0.35, 0.40, 0.50, 0.60, 0.80):
        cells.append(Cfg("vx_%.2f" % vx, "vx", vx=vx, seconds=12.0,
                         save_traj=(abs(vx - 0.60) < 1e-9)))
    for s, lbl in ((0.90, "m090"), (1.10, "m110")):
        cells.append(Cfg("mass_%s" % lbl, "mass", mass_scale=s, seconds=12.0, save_traj=(s == 1.10),
                         note="every body mass and inertia x %.2f" % s))
    for mu in (0.40, 0.70, 1.00):
        cells.append(Cfg("mu_%.2f" % mu, "friction", friction=mu, seconds=12.0,
                         save_traj=(abs(mu - 0.40) < 1e-9),
                         note="sliding friction on floor and both foot geoms"))
    for d in ("up", "down", "side_left", "side_right"):
        cells.append(Cfg("slope5_%s" % d, "slope", slope_deg=5.0, slope_dir=d, seconds=12.0,
                         save_traj=(d == "up"), note="5 deg slope by rotated gravity, downhill %s" % d))
    for f in (1.0, 2.0, 5.0):
        cells.append(Cfg("push_%.0fN_lat" % f, "push", push_N=f, push_dir=(0, 1, 0), push_at=6.0,
                         seconds=12.0, save_traj=(f == 5.0),
                         note="+y lateral push on trunk_base, %.1f N for 0.2 s at t=6.0 s" % f))
    cells.append(Cfg("push_5N_lat_neg", "push", push_N=5.0, push_dir=(0, -1, 0), push_at=6.0, seconds=12.0,
                     note="-y lateral push, 5 N for 0.2 s"))
    cells.append(Cfg("push_5N_fwd", "push", push_N=5.0, push_dir=(1, 0, 0), push_at=6.0, seconds=12.0,
                     note="+x forward push, 5 N for 0.2 s"))
    cells.append(Cfg("push_5N_back", "push", push_N=5.0, push_dir=(-1, 0, 0), push_at=6.0, seconds=12.0,
                     note="-x backward push, 5 N for 0.2 s"))
    # sit-stand family: all-collisions model, the one that actually puts the body on the floor
    cells.append(Cfg("sitstand", "sitstand", policy="sitstand", robot="ours_allcollisions", seconds=10.0,
                     save_traj=True, note="stand -> sit at 1.0 s -> stand at 4.5 s"))
    cells.append(Cfg("sitstand_mu0.40", "sitstand", policy="sitstand", robot="ours_allcollisions",
                     seconds=10.0, friction=0.40))
    cells.append(Cfg("sitstand_m110", "sitstand", policy="sitstand", robot="ours_allcollisions",
                     seconds=10.0, mass_scale=1.10))
    cells.append(Cfg("stand_from_SIT", "sitstand", policy="stand", robot="ours_allcollisions",
                     seconds=8.0, start="SIT"))
    cells.append(Cfg("stand_from_FOLD", "sitstand", policy="stand", robot="ours_allcollisions",
                     seconds=8.0, start="FOLD"))
    cells.append(Cfg("stand_hold", "sitstand", policy="stand", robot="ours_allcollisions",
                     seconds=8.0, start="STAND"))
    # self-collision census on the all-collisions model while walking
    cells.append(Cfg("walk_allcollisions", "selfcollision", robot="ours_allcollisions", vx=0.25, seconds=12.0,
                     note="the walk on the model that has EVERY body's collision geom enabled"))
    return cells


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--only", default=None, help="comma-separated cell names")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    cells = matrix()
    if a.only:
        want = set(a.only.split(","))
        cells = [c for c in cells if c.name in want]
    for c in cells:
        r = run_cell(c, a.out)
        o = r["outputs"]
        print("%-22s %-12s fell=%-5s d=%7.4f m  v=%6.4f m/s  tau_max=%.4f Nm (%s)  GRFz=%.2f N  self=%d  %.2fs" % (
            c.name, c.family, o["fell"], o["walked_m"], o["mean_speed_m_s"], o["max_joint_torque_Nm"],
            o["max_joint_torque_joint"], o["grf_vertical_peak_N"]["both_feet_sum_peak"],
            o["self_collisions"]["max"], o["wall_seconds"]))


if __name__ == "__main__":
    main()
