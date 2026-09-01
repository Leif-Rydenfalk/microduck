#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""run_policy.py — drive Pollen's Microduck MJCF with Pollen's published ONNX
policies in MuJoCo, exactly the way scripts/infer_policy.py (microduck_rl) and
the browser simulator's game.js do it, and record what happened.

    run_policy.py --policy walking  --robot walk           --seconds 8  --vx 0.15
    run_policy.py --policy walking  --robot ours           --seconds 8  --vx 0.15
    run_policy.py --policy sitstand --robot ours_allcollisions --seconds 8
    run_policy.py --policy stand    --robot ours_allcollisions --start SIT --seconds 6

Loop (50 Hz): obs(61) = [gyro(3) | projected gravity(3) | q - DEFAULT_POSE(14) |
qdot(14) | last action(14) | command(13)] -> ONNX -> action(14);
ctrl = DEFAULT_POSE + action * action_scale; 4 x mj_step at 0.005 s.
Command slots: [vx vy wz | neck_pitch head_pitch head_yaw head_roll | body x y z roll pitch yaw].
sitstand uses cmd[0] as the posture flag (1 = sit, 0 = stand); stand runs all-zero.

Outputs (out/sim/<name>_traj.npz + <name>_summary.json): every number in the
summary is measured off the simulation state.
"""
import argparse
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
from common import (ACTION_SCALE, CMD_SIZE, CTRL_DT, DECIMATION, DEFAULT_POSE, HEAD_ALPHA,  # noqa: E402
                    JOINT_NAMES, NUM_JOINTS, OBS_SIZE)

POLICY_FILES = {
    "walking": "BEST_alpha_walking.onnx",
    "sitstand": "BEST_alpha_sitstand.onnx",
    "stand": "BEST_alpha_stand.onnx",
}
FALL_Z = 0.06
FALL_TILT_DEG = 60.0


class Policy:
    def __init__(self, path):
        import onnxruntime as ort
        so = ort.SessionOptions()
        so.intra_op_num_threads = 1
        so.inter_op_num_threads = 1
        self.sess = ort.InferenceSession(path, so, providers=["CPUExecutionProvider"])
        self.in_name = self.sess.get_inputs()[0].name
        self.out_name = self.sess.get_outputs()[0].name
        assert self.sess.get_inputs()[0].shape == [1, OBS_SIZE], self.sess.get_inputs()[0].shape
        md = self.sess.get_modelmeta().custom_metadata_map
        self.meta = dict(md)
        names = md.get("joint_names", "").split(",")
        assert names == JOINT_NAMES, names
        dp = np.array([float(x) for x in md.get("default_joint_pos", "").split(",")])
        assert np.allclose(dp, DEFAULT_POSE, atol=1e-3), dp
        self.action_scale = float(md.get("action_scale", ACTION_SCALE))

    def __call__(self, obs):
        return self.sess.run([self.out_name], {self.in_name: obs.reshape(1, -1)})[0][0].astype(np.float32)


class Runner:
    """State + observation assembly, mirroring infer_policy.py's PolicyInference and game.js's buildObs."""

    def __init__(self, model, data):
        import mujoco
        self.mujoco = mujoco
        self.model, self.data = model, data
        self.trunk_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "trunk_base")
        sid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SENSOR, "imu_ang_vel")
        assert sid >= 0, "sensor imu_ang_vel missing"
        self.gyro_adr = int(model.sensor_adr[sid])
        self.qpos_idx = [int(model.jnt_qposadr[model.actuator_trnid[i, 0]]) for i in range(model.nu)]
        self.qvel_idx = [int(model.jnt_dofadr[model.actuator_trnid[i, 0]]) for i in range(model.nu)]
        fj = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, "trunk_base_freejoint")
        self.root_qadr = int(model.jnt_qposadr[fj])
        self.root_vadr = int(model.jnt_dofadr[fj])
        self.last_action = np.zeros(NUM_JOINTS, np.float32)
        self.cmd = np.zeros(CMD_SIZE, np.float32)
        self.head_target = np.zeros(4, np.float32)
        self.head_smooth = np.zeros(4, np.float32)
        self.floor_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, "floor")
        self.jnt_range = np.array([model.jnt_range[model.actuator_trnid[i, 0]] for i in range(model.nu)])

    def trunk_quat(self):
        return self.data.xquat[self.trunk_id].astype(np.float32)

    def projected_gravity(self):
        return common.quat_rotate_inverse(self.trunk_quat(), np.array([0, 0, -1], np.float32))

    def obs(self, twist=(0, 0, 0), sit_flag=None):
        d = self.data
        self.head_smooth += HEAD_ALPHA * (self.head_target - self.head_smooth)   # game.js EMA
        self.cmd[:] = 0
        if sit_flag is None:
            self.cmd[0:3] = twist
        else:
            self.cmd[0] = float(sit_flag)
        self.cmd[3:7] = self.head_smooth
        o = np.concatenate([
            d.sensordata[self.gyro_adr:self.gyro_adr + 3].astype(np.float32),
            self.projected_gravity(),
            d.qpos[self.qpos_idx].astype(np.float32) - DEFAULT_POSE,
            d.qvel[self.qvel_idx].astype(np.float32),
            self.last_action,
            self.cmd,
        ]).astype(np.float32)
        assert o.shape == (OBS_SIZE,)
        return o

    def apply(self, action, action_scale):
        self.last_action = action.copy()
        self.data.ctrl[:] = DEFAULT_POSE + action * action_scale

    def self_contacts(self):
        d = self.data
        n = 0
        for i in range(d.ncon):
            c = d.contact[i]
            if c.geom1 != self.floor_id and c.geom2 != self.floor_id:
                n += 1
        return n


def schedule(policy, t, args):
    """-> (twist, sit_flag) for time t. Walking: zero twist during warm-up then the command.
    sitstand: stand, sit at --sit-at, stand again at --stand-at (game.js: hold the stand under
    the sitstand policy first, or the switch knocks the duck over). stand: all zero."""
    if policy == "walking":
        if t < args.warmup:
            return (0.0, 0.0, 0.0), None
        return (args.vx, args.vy, args.wz), None
    if policy == "sitstand":
        sit = 1 if args.sit_at <= t < args.stand_at else 0
        return (0, 0, 0), sit
    return (0.0, 0.0, 0.0), None


def build_parser():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--policy", choices=sorted(POLICY_FILES), default=None)
    ap.add_argument("--robot", default="walk", help="walk | allcollisions | ours | ours_allcollisions | path")
    ap.add_argument("--seconds", type=float, default=8.0)
    ap.add_argument("--vx", type=float, default=0.25, help="forward command m/s (walking); 0.15 is inside the "
                    "policy's stand-still band (measured), 0.25 is the browser simulator's VEL_FWD")
    ap.add_argument("--vy", type=float, default=0.0)
    ap.add_argument("--wz", type=float, default=0.0)
    ap.add_argument("--warmup", type=float, default=0.5, help="s of zero twist before the walking command")
    ap.add_argument("--sit-at", type=float, default=1.0)
    ap.add_argument("--stand-at", type=float, default=4.5)
    ap.add_argument("--start", default="STAND", help="keyframe to start from: STAND | SIT | FOLD | INIT")
    ap.add_argument("--name", default=None, help="output stem (default <policy>_<robot>)")
    ap.add_argument("--out", default=common.OUT_DIR)
    ap.add_argument("--all", action="store_true", help="run the standard set (see STANDARD_RUNS)")
    return ap


# The standard set: --all runs these; render_video.py --all renders from them.
STANDARD_RUNS = [
    dict(name="walk_stock", policy="walking", robot="walk", seconds=8.0, vx=0.25),
    dict(name="walk_ours", policy="walking", robot="ours", seconds=8.0, vx=0.25),
    dict(name="walk_stock_vx0.15", policy="walking", robot="walk", seconds=8.0, vx=0.15),
    dict(name="walk_ours_vx0.15", policy="walking", robot="ours", seconds=8.0, vx=0.15),
    dict(name="sitstand_stock", policy="sitstand", robot="allcollisions", seconds=8.0),
    dict(name="sitstand_ours", policy="sitstand", robot="ours_allcollisions", seconds=8.0),
    dict(name="stand_hold_ours", policy="stand", robot="ours_allcollisions", seconds=4.0, start="STAND"),
    dict(name="stand_from_sit_ours", policy="stand", robot="ours_allcollisions", seconds=6.0, start="SIT"),
    dict(name="stand_from_fold_ours", policy="stand", robot="ours_allcollisions", seconds=6.0, start="FOLD"),
]


def main():
    ap = build_parser()
    args = ap.parse_args()
    if args.all:
        for cfg in STANDARD_RUNS:
            a = ap.parse_args([])
            for k, v in cfg.items():
                setattr(a, k, v)
            print("=== %s" % cfg["name"])
            run(a)
        return
    if args.policy is None:
        ap.error("--policy or --all")
    run(args)


def run(args):
    import mujoco
    name = args.name or "%s_%s" % (args.policy, os.path.basename(args.robot).replace(".xml", ""))
    os.makedirs(args.out, exist_ok=True)
    model, scene_path = common.load_model(args.robot, os.path.join(args.out, "scene_%s.xml" % name))
    assert abs(model.opt.timestep - common.TIMESTEP) < 1e-12, model.opt.timestep
    data = mujoco.MjData(model)
    kid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, args.start)
    assert kid >= 0, args.start
    mujoco.mj_resetDataKeyframe(model, data, kid)
    mujoco.mj_forward(model, data)
    pol = Policy(os.path.join(common.POLICY_DIR, POLICY_FILES[args.policy]))
    run = Runner(model, data)

    n_steps = int(round(args.seconds / CTRL_DT))
    T = n_steps + 1
    rec = {k: [] for k in ("time", "qpos", "qvel", "ctrl", "action", "obs", "cmd", "ncon", "nself", "trunk_z", "roll", "pitch")}

    def record(t, action):
        q = data.qpos[run.root_qadr + 3:run.root_qadr + 7]
        roll, pitch = common.quat_to_roll_pitch(q)
        rec["time"].append(t)
        rec["qpos"].append(data.qpos.copy())
        rec["qvel"].append(data.qvel.copy())
        rec["ctrl"].append(data.ctrl.copy())
        rec["action"].append(action.copy())
        rec["cmd"].append(run.cmd.copy())
        rec["ncon"].append(data.ncon)
        rec["nself"].append(run.self_contacts())
        rec["trunk_z"].append(float(data.qpos[run.root_qadr + 2]))
        rec["roll"].append(float(roll))
        rec["pitch"].append(float(pitch))

    t0 = time.time()
    start_xy = data.qpos[run.root_qadr:run.root_qadr + 2].copy()
    record(0.0, np.zeros(NUM_JOINTS, np.float32))
    rec["obs"].append(run.obs(*schedule(args.policy, 0.0, args)))
    for k in range(n_steps):
        t = k * CTRL_DT
        twist, sit = schedule(args.policy, t, args)
        o = run.obs(twist, sit)
        a = pol(o)
        run.apply(a, pol.action_scale)
        for _ in range(DECIMATION):
            mujoco.mj_step(model, data)
        record((k + 1) * CTRL_DT, a)
        rec["obs"].append(o)
    wall = time.time() - t0

    A = {k: np.asarray(v) for k, v in rec.items()}
    # ---- measurements -------------------------------------------------------
    end_xy = A["qpos"][-1, run.root_qadr:run.root_qadr + 2]
    disp = end_xy - start_xy
    tilt = np.degrees(np.maximum(np.abs(A["roll"]), np.abs(A["pitch"])))
    fell_z = A["trunk_z"] < FALL_Z
    fell_tilt = tilt > FALL_TILT_DEG
    fell = bool(np.any(fell_z | fell_tilt))
    first_fall = float(A["time"][np.argmax(fell_z | fell_tilt)]) if fell else None
    # A commanded sit (sitstand) and a start on the ground (stand from SIT/FOLD) put the
    # trunk below FALL_Z on purpose; report the rule verbatim AND the rule outside those windows.
    excl = np.zeros(T, bool)
    if args.policy == "sitstand":
        excl = (A["time"] >= args.sit_at) & (A["time"] < args.stand_at + 1.5)
    elif args.policy == "stand" and args.start != "STAND":
        excl = A["time"] < 2.0
    fell_outside = bool(np.any((fell_z & ~excl) | fell_tilt))
    jq = A["qpos"][:, run.qpos_idx]
    jv = A["qvel"][:, run.qvel_idx]
    lo, hi = run.jnt_range[:, 0], run.jnt_range[:, 1]
    margin = np.radians(1.0)
    hits = {}
    for i, jn in enumerate(JOINT_NAMES):
        near = int(np.sum((jq[:, i] <= lo[i] + margin) | (jq[:, i] >= hi[i] - margin)))
        beyond = int(np.sum((jq[:, i] < lo[i]) | (jq[:, i] > hi[i])))
        hits[jn] = {"range_rad": [round(float(lo[i]), 4), round(float(hi[i]), 4)],
                    "min_rad": round(float(jq[:, i].min()), 4), "max_rad": round(float(jq[:, i].max()), 4),
                    "used_pct_of_range": round(float((jq[:, i].max() - jq[:, i].min()) / (hi[i] - lo[i]) * 100), 1),
                    "frames_within_1deg_of_limit": near, "frames_beyond_limit": beyond,
                    "max_abs_vel_rad_s": round(float(np.abs(jv[:, i]).max()), 3)}
    # commanded-window forward speed (body frame x projected on the world yaw)
    cmd_mask = A["time"] >= (args.warmup if args.policy == "walking" else 0.0)
    if cmd_mask.sum() > 1:
        tt = A["time"][cmd_mask]
        xy = A["qpos"][cmd_mask][:, run.root_qadr:run.root_qadr + 2]
        speed = float(np.linalg.norm(xy[-1] - xy[0]) / max(tt[-1] - tt[0], 1e-9))
    else:
        speed = 0.0
    ctrl_sat = float(np.mean(np.abs(A["action"]) >= 0.999 * 3.0))  # actions are unbounded; informative only
    summary = {
        "name": name, "policy": args.policy, "policy_file": POLICY_FILES[args.policy], "policy_meta": pol.meta,
        "robot": args.robot, "robot_file": os.path.relpath(common.robot_file(args.robot), common.ROOT),
        "scene_file": os.path.relpath(scene_path, common.ROOT), "start_keyframe": args.start,
        "seconds": round(n_steps * CTRL_DT, 3), "control_hz": round(1.0 / CTRL_DT, 1), "timestep": model.opt.timestep,
        "decimation": DECIMATION, "control_steps": n_steps, "physics_steps": n_steps * DECIMATION,
        "wall_seconds": round(wall, 2), "action_scale": pol.action_scale,
        "command": {"vx": args.vx, "vy": args.vy, "wz": args.wz, "warmup_s": args.warmup} if args.policy == "walking"
        else ({"sit_at_s": args.sit_at, "stand_at_s": args.stand_at} if args.policy == "sitstand" else "all zero"),
        "walked_m": round(float(np.linalg.norm(disp)), 4), "walked_x_m": round(float(disp[0]), 4),
        "walked_y_m": round(float(disp[1]), 4), "mean_speed_m_s_commanded_window": round(speed, 4),
        "final_yaw_deg": round(float(np.degrees(np.arctan2(
            2 * (A["qpos"][-1, run.root_qadr + 3] * A["qpos"][-1, run.root_qadr + 6] + A["qpos"][-1, run.root_qadr + 4] * A["qpos"][-1, run.root_qadr + 5]),
            1 - 2 * (A["qpos"][-1, run.root_qadr + 5] ** 2 + A["qpos"][-1, run.root_qadr + 6] ** 2)))), 2),
        "trunk_z_m": {"start": round(float(A["trunk_z"][0]), 4), "min": round(float(A["trunk_z"].min()), 4),
                      "max": round(float(A["trunk_z"].max()), 4), "end": round(float(A["trunk_z"][-1]), 4)},
        "max_tilt_deg": round(float(tilt.max()), 2), "end_tilt_deg": round(float(tilt[-1]), 2),
        "fell": fell, "fell_by_height": bool(np.any(fell_z)), "fell_by_tilt": bool(np.any(fell_tilt)),
        "first_fall_s": first_fall,
        "fell_outside_commanded_ground_window": fell_outside,
        "commanded_ground_window_s": [float(A["time"][excl].min()), float(A["time"][excl].max())] if excl.any() else None,
        "fall_rule": "trunk z < %.2f m or |roll|,|pitch| > %.0f deg" % (FALL_Z, FALL_TILT_DEG),
        "max_joint_speed_rad_s": round(float(np.abs(jv).max()), 3),
        "max_joint_speed_joint": JOINT_NAMES[int(np.unravel_index(np.abs(jv).argmax(), jv.shape)[1])],
        "joint_range_hits": hits,
        "joints_within_1deg_of_limit": [j for j, h in hits.items() if h["frames_within_1deg_of_limit"] > 0],
        "joints_beyond_limit": [j for j, h in hits.items() if h["frames_beyond_limit"] > 0],
        "contacts": {"mean": round(float(A["ncon"].mean()), 2), "max": int(A["ncon"].max()),
                     "self_mean": round(float(A["nself"].mean()), 3), "self_max": int(A["nself"].max()),
                     "frames_with_self_contact": int(np.sum(A["nself"] > 0))},
        "max_abs_action": round(float(np.abs(A["action"]).max()), 3),
        "nan": bool(np.any(~np.isfinite(A["qpos"]))),
    }
    np.savez_compressed(os.path.join(args.out, name + "_traj.npz"), scene=scene_path, robot=args.robot, policy=args.policy,
                        ctrl_dt=CTRL_DT, root_qadr=run.root_qadr, **A)
    json.dump(summary, open(os.path.join(args.out, name + "_summary.json"), "w"), indent=1)
    print(json.dumps({k: summary[k] for k in ("name", "seconds", "walked_m", "walked_x_m", "mean_speed_m_s_commanded_window",
                                              "fell", "first_fall_s", "max_tilt_deg", "trunk_z_m", "max_joint_speed_rad_s",
                                              "joints_within_1deg_of_limit", "joints_beyond_limit", "contacts", "wall_seconds")}, indent=1))
    print("wrote", os.path.relpath(os.path.join(args.out, name + "_traj.npz"), common.ROOT),
          os.path.relpath(os.path.join(args.out, name + "_summary.json"), common.ROOT))


if __name__ == "__main__":
    main()
