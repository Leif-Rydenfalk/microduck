#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""measure_loads.py — the LOAD BASIS for every structural study, read off MuJoCo.

Lane F1 (structural), 2026-09-02. Nothing here is a round number: every force,
torque, period and direction below is measured on Pollen's published MJCF
(reference/pollen-microduck-rl/robot_walk.xml / robot_allcollisions.xml,
METRES) driven by Pollen's own walking policy exactly as sim/run_policy.py
drives it (50 Hz, 4 x 0.005 s physics steps), plus two scripted drop tests.

What it measures
  1. stand      — the robot held at DEFAULT_POSE for 2 s: per-foot vertical
                  ground reaction, holding torque per joint.
  2. walk       — 8 s of BEST_alpha_walking at vx 0.25 m/s (the browser
                  simulator's VEL_FWD): per-physics-step ground reaction per
                  foot (normal + tangential), actuator torque per joint, the
                  frame of the peak, gait period / stride from the left-foot
                  touchdowns, and the gravity + contact-force directions
                  expressed in EVERY structural part's own (mesh) frame at
                  the peak frame — so an FEA case can load the part along
                  the direction it really sees.
  3. drop_foot  — STAND pose rolled 10 deg so one sole strikes first, lowest
                  sole vertex 0.250 m above the floor, actuators holding
                  DEFAULT_POSE, free fall; peak contact force, impulse, peak
                  joint torque, at three contact stiffnesses (MuJoCo solref).
  4. drop_head  — the all-collisions model inverted, head shell lowest vertex
                  0.250 m above the floor; same records, on top_head_shell.

Output: out/sim-evidence/loads_mujoco.json (+ the per-step arrays in
out/sim-evidence/loads_mujoco.npz). Run:
    /Applications/FreeCAD.app/Contents/Resources/bin/python sim/measure_loads.py
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import common  # noqa: E402
from common import CTRL_DT, DECIMATION, DEFAULT_POSE, JOINT_NAMES, TIMESTEP  # noqa: E402
import run_policy  # noqa: E402

import mujoco  # noqa: E402

OUT = os.path.join(ROOT, "out", "sim-evidence")
os.makedirs(OUT, exist_ok=True)
MESH_TO_PART = json.load(open(os.path.join(ROOT, "spec", "mesh-to-part.json")))["map"]
G = 9.81  # MuJoCo default gravity magnitude (model.opt.gravity is read below and asserted)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def gid(model, name):
    i = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, name)
    assert i >= 0, name
    return i


def contact_forces(model, data, floor_id, targets):
    """Sum of floor-contact forces on each target geom id, WORLD frame,
    force ON the target. Returns {gid: (Fworld(3), Fnormal_scalar, ncontacts)}."""
    out = {g: [np.zeros(3), 0.0, 0] for g in targets}
    f6 = np.zeros(6)
    for i in range(data.ncon):
        c = data.contact[i]
        if c.geom1 == floor_id and c.geom2 in out:
            tgt, sign = c.geom2, 1.0      # normal points geom1 -> geom2: force on geom2 is +
        elif c.geom2 == floor_id and c.geom1 in out:
            tgt, sign = c.geom1, -1.0
        else:
            continue
        mujoco.mj_contactForce(model, data, i, f6)
        frame = np.array(c.frame).reshape(3, 3)          # rows = normal, tangent1, tangent2
        fw = sign * frame.T @ f6[:3]
        out[tgt][0] += fw
        out[tgt][1] += abs(f6[0])
        out[tgt][2] += 1
    return out


def geom_world_extent(model, data, g):
    """(zmin, zmax) of the geom's AABB in the world at the current pose."""
    c = model.geom_aabb[g, :3]
    h = model.geom_aabb[g, 3:]
    R = data.geom_xmat[g].reshape(3, 3)
    p = data.geom_xpos[g]
    corners = np.array([[sx, sy, sz] for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]) * h + c
    w = (R @ corners.T).T + p
    return float(w[:, 2].min()), float(w[:, 2].max())


def mesh_geoms(model):
    """mesh name -> first geom id carrying that mesh (visual or collision)."""
    m = {}
    for g in range(model.ngeom):
        if model.geom_type[g] != mujoco.mjtGeom.mjGEOM_MESH:
            continue
        name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_MESH, int(model.geom_dataid[g]))
        m.setdefault(name, g)
    return m


def in_geom_frame(model, data, g, v_world):
    """A world vector in the mesh FILE frame (= the part's frame). MuJoCo
    re-centres every mesh at its CoM and aligns it to its principal axes when
    it compiles; geom_xmat is that processed frame, and model.mesh_pos /
    mesh_quat hold the transform: v_world = p_geom + R_geom R_mq^T (v_file -
    mesh_pos). VERIFIED 2026-09-02 on sole_left: file point (50, 15, -31.0)
    mm (the sole floor, part.py) lands at world z 0.002 m and the rim
    (z -18.342) at 0.0146 m in the STAND pose; file +z in the world is
    (0, 0.0872, 0.9962) = up, rolled by the 5 deg DEFAULT_POSE hip roll.
    The other candidate composition put the rim 43 mm up. So the file-frame
    component is R_mq R_geom^T v."""
    mid = int(model.geom_dataid[g])
    Rmq = np.zeros(9)
    mujoco.mju_quat2Mat(Rmq, model.mesh_quat[mid])
    Rmq = Rmq.reshape(3, 3)
    R = data.geom_xmat[g].reshape(3, 3)
    return (Rmq @ (R.T @ v_world)).tolist()


BODIES = ["trunk_base", "yaw2roll", "hip_l", "upper_leg_left", "leg", "ankle_left",
          "bearing_roll", "hip_l_2", "upper_leg_right", "leg_2", "ankle_right",
          "neck", "neck_pitch", "yaw_roll_motion", "jaw_soft"]


def body_forces(model, data):
    """|force| each body transmits to its parent (MuJoCo cfrc_int, the
    com-based interaction force with the parent, world frame; [torque(3),
    force(3)]) — the load the part bridging that joint carries."""
    out = {}
    for b in BODIES:
        i = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, b)
        if i < 0:
            continue
        f = data.cfrc_int[i, 3:6]
        out[b] = (float(np.linalg.norm(f)), f.copy(), data.cfrc_int[i, 0:3].copy())
    return out


def part_frames(model, data, meshes, vectors):
    """For each structural mesh: every named world vector expressed in the
    mesh (= part) frame, the body it lives in and the geom used."""
    rows = {}
    for mesh, ref in MESH_TO_PART.items():
        g = meshes.get(mesh)
        if g is None:
            continue
        body = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_BODY, int(model.geom_bodyid[g]))
        rows[mesh] = {"part": ref, "body": body, "geom_id": int(g)}
        for vname, v in vectors.items():
            rows[mesh][vname + "_in_part_frame"] = [round(x, 6) for x in in_geom_frame(model, data, g, np.asarray(v))]
    return rows


def solref_for_stiffness(K_N_per_m, m_eff_kg, dampratio=1.0, dmax=0.95):
    """MuJoCo's contact spring is acceleration-based: stiffness per unit
    effective mass k = d/(dmax^2 timeconst^2 dampratio^2), with d -> dmax at
    full penetration (solimp default 0.9 0.95 0.001). A physical stiffness K
    on effective mass m therefore needs timeconst = sqrt(m / (K dmax
    dampratio^2)). (MuJoCo docs, Computation > Solver parameters.)"""
    return float(np.sqrt(m_eff_kg / (K_N_per_m * dmax * dampratio ** 2)))


# ---------------------------------------------------------------------------
# 1 + 2: stand and walk under the policy
# ---------------------------------------------------------------------------
def walk_and_stand(robot="walk", seconds=8.0, vx=0.25, warmup=0.5, stand_seconds=2.0):
    model, scene = common.load_model(robot, os.path.join(OUT, "scene_loads_%s.xml" % robot))
    data = mujoco.MjData(model)
    assert abs(model.opt.timestep - TIMESTEP) < 1e-12
    assert abs(model.opt.gravity[2] + G) < 1e-9, model.opt.gravity
    trunk = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "trunk_base")
    mass = float(model.body_subtreemass[trunk])
    floor = gid(model, "floor")
    lf, rf = gid(model, "left_foot_collision"), gid(model, "right_foot_collision")
    meshes = mesh_geoms(model)
    kid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, "STAND")
    mujoco.mj_resetDataKeyframe(model, data, kid)
    mujoco.mj_forward(model, data)
    run = run_policy.Runner(model, data)
    pol = run_policy.Policy(os.path.join(common.POLICY_DIR, run_policy.POLICY_FILES["walking"]))

    # ---- 1. stand: hold DEFAULT_POSE, no policy, until settled ----------------
    data.ctrl[:] = DEFAULT_POSE
    n = int(round(stand_seconds / TIMESTEP))
    Fl = Fr = None
    tq = []
    for k in range(n):
        mujoco.mj_step(model, data)
        if k >= n - 100:                       # average the last 0.5 s
            cf = contact_forces(model, data, floor, (lf, rf))
            Fl = cf[lf][0] if Fl is None else Fl + cf[lf][0]
            Fr = cf[rf][0] if Fr is None else Fr + cf[rf][0]
            tq.append(data.actuator_force.copy())
    Fl, Fr = Fl / 100.0, Fr / 100.0
    tq = np.array(tq)
    stand = {
        "seconds_settled": stand_seconds, "averaged_over_s": 100 * TIMESTEP,
        "left_foot_N": [round(float(x), 4) for x in Fl], "right_foot_N": [round(float(x), 4) for x in Fr],
        "left_foot_vertical_N": round(float(Fl[2]), 4), "right_foot_vertical_N": round(float(Fr[2]), 4),
        "sum_vertical_N": round(float(Fl[2] + Fr[2]), 4), "weight_N": round(mass * G, 4),
        "closure_pct": round(100.0 * (Fl[2] + Fr[2]) / (mass * G), 3),
        "holding_torque_Nm_mean": {j: round(float(v), 5) for j, v in zip(JOINT_NAMES, tq.mean(0))},
        "holding_torque_Nm_absmax": {j: round(float(v), 5) for j, v in zip(JOINT_NAMES, np.abs(tq).max(0))},
        "trunk_z_m": round(float(data.qpos[run.root_qadr + 2]), 5),
    }
    stand_frames = part_frames(model, data, meshes, {"gravity_unit": (0, 0, -1),
                                                      "left_foot_contact_force_N": Fl,
                                                      "right_foot_contact_force_N": Fr})

    # ---- 2. walk: the policy, exactly run_policy.run() --------------------------
    mujoco.mj_resetDataKeyframe(model, data, kid)
    mujoco.mj_forward(model, data)
    run = run_policy.Runner(model, data)
    class A:  # the parser's defaults that schedule() reads
        pass
    args = A(); args.vx, args.vy, args.wz, args.warmup = vx, 0.0, 0.0, warmup
    n_steps = int(round(seconds / CTRL_DT))
    T = n_steps * DECIMATION
    t = np.zeros(T); FL = np.zeros((T, 3)); FR = np.zeros((T, 3)); FLn = np.zeros(T); FRn = np.zeros(T)
    TQ = np.zeros((T, model.nu)); QV = np.zeros((T, model.nu)); XY = np.zeros((T, 2))
    NL = np.zeros(T, int); NR = np.zeros(T, int)
    BF = np.zeros((T, len(BODIES))); BFv = np.zeros((T, len(BODIES), 3)); BT = np.zeros((T, len(BODIES), 3))
    TA = np.zeros((T, 3))
    frames_at = {}
    i = 0
    for k in range(n_steps):
        twist, sit = run_policy.schedule("walking", k * CTRL_DT, args)
        o = run.obs(twist, sit)
        a = pol(o)
        run.apply(a, pol.action_scale)
        for _ in range(DECIMATION):
            mujoco.mj_step(model, data)
            cf = contact_forces(model, data, floor, (lf, rf))
            t[i] = data.time
            FL[i], FLn[i], NL[i] = cf[lf]
            FR[i], FRn[i], NR[i] = cf[rf]
            TQ[i] = data.actuator_force
            QV[i] = data.qvel[run.qvel_idx]
            XY[i] = data.qpos[run.root_qadr:run.root_qadr + 2]
            bf = body_forces(model, data)
            for j, b in enumerate(BODIES):
                if b in bf:
                    BF[i, j], BFv[i, j], BT[i, j] = bf[b]
            mujoco.mj_rnePostConstraint(model, data)
            TA[i] = data.cacc[trunk, 3:6]
            i += 1
    # peak vertical GRF on either foot, inside the commanded window
    win = t >= warmup
    peak_i = int(np.argmax(np.where(win, np.maximum(FL[:, 2], FR[:, 2]), -1)))
    peak_foot = "left" if FL[peak_i, 2] >= FR[peak_i, 2] else "right"
    peakF = FL[peak_i] if peak_foot == "left" else FR[peak_i]
    # per-body peak transmitted force inside the commanded window, and the step it happens at
    BFw = np.where(win[:, None], BF, -1.0)
    body_peak_step = {b: int(np.argmax(BFw[:, j])) for j, b in enumerate(BODIES)}
    tang = np.maximum(np.hypot(FL[:, 0], FL[:, 1]), np.hypot(FR[:, 0], FR[:, 1]))
    tang_i = int(np.argmax(np.where(win, tang, -1)))
    want = {peak_i: "grf_peak", tang_i: "tangential_peak"}
    for b, st in body_peak_step.items():
        want.setdefault(st, "body_peak:" + b)
    # replay to every wanted step and read the part orientations there
    mujoco.mj_resetDataKeyframe(model, data, kid)
    mujoco.mj_forward(model, data)
    run2 = run_policy.Runner(model, data)
    i = 0
    walk_frames = None
    snaps = {}
    for k in range(n_steps):
        twist, sit = run_policy.schedule("walking", k * CTRL_DT, args)
        o = run2.obs(twist, sit)
        a = pol(o)
        run2.apply(a, pol.action_scale)
        for _ in range(DECIMATION):
            mujoco.mj_step(model, data)
            if i in want:
                bf = body_forces(model, data)
                vecs = {"gravity_unit": (0, 0, -1),
                        "left_foot_contact_force_N": FL[i], "right_foot_contact_force_N": FR[i]}
                for b, (mag, fv, tv) in bf.items():
                    vecs["force_from_body_%s_N" % b] = fv
                fr = part_frames(model, data, meshes, vecs)
                fr["_step"] = i; fr["_time_s"] = round(float(t[i]), 4)
                fr["_joint_torque_Nm"] = {j: round(float(v), 5) for j, v in zip(JOINT_NAMES, data.actuator_force)}
                fr["_body_force_N"] = {b: {"magnitude": round(mag, 4), "world": [round(float(x), 4) for x in fv],
                                           "torque_world_Nm": [round(float(x), 5) for x in tv]} for b, (mag, fv, tv) in bf.items()}
                snaps[i] = fr
            i += 1
    walk_frames = snaps[peak_i]
    walk_frames["_peak_foot"] = peak_foot
    body_peaks = {}
    for j, b in enumerate(BODIES):
        st = body_peak_step[b]
        body_peaks[b] = {"peak_force_N": round(float(BF[st, j]), 4), "step": st, "time_s": round(float(t[st]), 4),
                         "world_vector_N": [round(float(x), 4) for x in BFv[st, j]],
                         "p99_force_N": round(float(np.percentile(BF[win, j], 99)), 4),
                         "mean_force_N": round(float(BF[win, j].mean()), 4),
                         "peak_torque_world_Nm": [round(float(x), 5) for x in BT[st, j]],
                         "part_frames": snaps[st]}
    tangential_snap = snaps[tang_i]

    # gait period from left-foot touchdowns in the commanded window
    inc = (FL[:, 2] > 0.05 * mass * G)               # stance = > 5 % bodyweight
    td = [j for j in range(1, T) if inc[j] and not inc[j - 1] and t[j] >= warmup + 0.5]
    periods = np.diff(t[td]) if len(td) > 2 else np.array([])
    if len(td) > 2:
        x0, x1 = XY[td[0]], XY[td[-1]]
        dist_cycles = float(np.linalg.norm(x1 - x0))
        n_cycles = len(td) - 1
    else:
        dist_cycles, n_cycles = None, 0
    tq_abs = np.abs(TQ[win])
    walk = {
        "robot": robot, "scene_file": os.path.relpath(scene, ROOT), "policy_file": run_policy.POLICY_FILES["walking"],
        "seconds": seconds, "vx_cmd_m_s": vx, "warmup_s": warmup, "physics_hz": round(1 / TIMESTEP, 1),
        "physics_steps": int(T), "commanded_window_steps": int(win.sum()),
        "peak_vertical_grf_N": round(float(peakF[2]), 4), "peak_foot": peak_foot,
        "peak_grf_vector_world_N": [round(float(x), 4) for x in peakF],
        "peak_grf_step": peak_i, "peak_grf_time_s": round(float(t[peak_i]), 4),
        "peak_grf_over_bodyweight": round(float(peakF[2]) / (mass * G), 4),
        "p99_vertical_grf_N": round(float(np.percentile(np.maximum(FL[win, 2], FR[win, 2]), 99)), 4),
        "mean_vertical_grf_when_in_stance_N": round(float(FL[win & inc, 2].mean()), 4),
        "peak_tangential_grf_N": round(float(max(np.hypot(FL[win, 0], FL[win, 1]).max(),
                                                np.hypot(FR[win, 0], FR[win, 1]).max())), 4),
        "max_contacts_per_foot": int(max(NL.max(), NR.max())),
        "peak_abs_torque_Nm": {j: round(float(v), 5) for j, v in zip(JOINT_NAMES, tq_abs.max(0))},
        "p99_abs_torque_Nm": {j: round(float(v), 5) for j, v in zip(JOINT_NAMES, np.percentile(tq_abs, 99, axis=0))},
        "actuator_forcerange_Nm": [float(model.actuator_forcerange[0, 0]), float(model.actuator_forcerange[0, 1])],
        "torque_saturated_steps": {j: int(np.sum(tq_abs[:, k] >= 0.999 * model.actuator_forcerange[k, 1]))
                                   for k, j in enumerate(JOINT_NAMES)},
        "peak_joint_speed_rad_s": {j: round(float(v), 4) for j, v in zip(JOINT_NAMES, np.abs(QV[win]).max(0))},
        "gait": {
            "stance_threshold_N": round(0.05 * mass * G, 4),
            "left_touchdowns_s": [round(float(t[j]), 4) for j in td],
            "n_cycles": int(n_cycles),
            "period_s_mean": round(float(periods.mean()), 5) if len(periods) else None,
            "period_s_min": round(float(periods.min()), 5) if len(periods) else None,
            "period_s_max": round(float(periods.max()), 5) if len(periods) else None,
            "distance_over_cycles_m": round(dist_cycles, 5) if dist_cycles is not None else None,
            "stride_m_per_cycle": round(dist_cycles / n_cycles, 5) if n_cycles else None,
            "cycles_per_km": round(1000.0 * n_cycles / dist_cycles, 1) if n_cycles and dist_cycles else None,
            "left_stance_fraction": round(float(inc[win].mean()), 4),
        },
        "part_frames_at_peak": walk_frames,
        "peak_tangential_grf_step": tang_i, "part_frames_at_tangential_peak": tangential_snap,
        "body_transmitted_force_peaks": body_peaks,
        "trunk_linear_acceleration": {
            "peak_m_s2": round(float(np.linalg.norm(TA[win], axis=1).max()), 4),
            "peak_step": int(np.argmax(np.where(win, np.linalg.norm(TA, axis=1), -1))),
            "p99_m_s2": round(float(np.percentile(np.linalg.norm(TA[win], axis=1), 99)), 4),
            "peak_vector_world_m_s2": [round(float(x), 4) for x in TA[int(np.argmax(np.where(win, np.linalg.norm(TA, axis=1), -1)))]],
            "note": "MuJoCo cacc of trunk_base after mj_rnePostConstraint (com-based linear part, world frame, gravity NOT included: this is the inertial acceleration)"},
        "body_force_note": "MuJoCo cfrc_int force part: the total force each body passes to its parent through its joint (world frame), i.e. the load carried by the part bridging that joint. Peaks taken inside the commanded window.",
    }
    arrays = {"t": t, "FL": FL, "FR": FR, "TQ": TQ, "QV": QV, "XY": XY, "BF": BF}
    return mass, stand, stand_frames, walk, arrays


# ---------------------------------------------------------------------------
# 3 + 4: drops
# ---------------------------------------------------------------------------
def drop(robot, orient_quat, target_geom, height_m, solref, seconds=0.5, label="", dt=None):
    model, scene = common.load_model(robot, os.path.join(OUT, "scene_drop_%s.xml" % robot))
    if dt is not None:
        model.opt.timestep = dt
    data = mujoco.MjData(model)
    floor = gid(model, "floor")
    trunk = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "trunk_base")
    mass = float(model.body_subtreemass[trunk])
    tg = gid(model, target_geom)
    lf, rf = gid(model, "left_foot_collision"), gid(model, "right_foot_collision")
    if solref is not None:
        model.geom_solref[:, 0] = solref[0]
        model.geom_solref[:, 1] = solref[1]
    kid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, "STAND")
    mujoco.mj_resetDataKeyframe(model, data, kid)
    fj = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, "trunk_base_freejoint")
    q0 = int(model.jnt_qposadr[fj])
    data.qpos[q0 + 3:q0 + 7] = orient_quat
    data.qpos[q0 + 2] = 1.0
    mujoco.mj_forward(model, data)
    # lowest point of ANY collision geom of the robot (the thing that strikes first)
    zmin = min(geom_world_extent(model, data, g)[0] for g in range(model.ngeom)
               if g != floor and model.geom_contype[g] | model.geom_conaffinity[g])
    data.qpos[q0 + 2] += height_m - zmin
    data.qvel[:] = 0
    data.ctrl[:] = DEFAULT_POSE
    mujoco.mj_forward(model, data)
    zmin_now = min(geom_world_extent(model, data, g)[0] for g in range(model.ngeom)
                   if g != floor and model.geom_contype[g] | model.geom_conaffinity[g])
    assert abs(zmin_now - height_m) < 1e-6, zmin_now
    n = int(round(seconds / model.opt.timestep))
    watch = sorted(set((tg, lf, rf)))
    Ft = np.zeros((n, 3)); Fn = np.zeros(n); TQ = np.zeros((n, model.nu)); t = np.zeros(n)
    FnAll = np.zeros((n, len(watch)))
    TA = np.zeros((n, 3))
    BFmax = {}
    first_geom = None; first_t = None; frames = None; peak_quat = None
    for k in range(n):
        mujoco.mj_step(model, data)
        t[k] = data.time
        cf = contact_forces(model, data, floor, watch)
        for j, g in enumerate(watch):
            FnAll[k, j] = cf[g][1]
        TQ[k] = data.actuator_force
        mujoco.mj_rnePostConstraint(model, data)
        TA[k] = data.cacc[trunk, 3:6]
        bfk = body_forces(model, data)
        for b, (mag, fv, tv) in bfk.items():
            if mag > BFmax.get(b, (0, None))[0]:
                BFmax[b] = (mag, [round(float(x), 4) for x in fv], round(float(data.time), 5))
        if first_geom is None and data.ncon:
            for i in range(data.ncon):
                c = data.contact[i]
                if floor in (c.geom1, c.geom2):
                    other = c.geom2 if c.geom1 == floor else c.geom1
                    first_geom = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_GEOM, other) or \
                        "mesh:" + str(mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_MESH, int(model.geom_dataid[other])))
                    first_t = float(data.time)
                    break
    # the struck geom is whichever of the watched geoms carries the largest peak
    jbest = int(np.argmax(FnAll.max(0)))
    tg = watch[jbest]
    Fn = FnAll[:, jbest]
    pk = int(np.argmax(Fn))
    # replay to the peak, re-reading the force vector on the struck geom
    struck = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_GEOM, tg) or "mesh:" + str(
        mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_MESH, int(model.geom_dataid[tg])))
    mujoco.mj_resetDataKeyframe(model, data, kid)
    data.qpos[q0 + 3:q0 + 7] = orient_quat
    data.qpos[q0 + 2] = 1.0
    mujoco.mj_forward(model, data)
    data.qpos[q0 + 2] += height_m - zmin
    data.qvel[:] = 0; data.ctrl[:] = DEFAULT_POSE
    mujoco.mj_forward(model, data)
    meshes = mesh_geoms(model)
    for k in range(pk + 1):
        mujoco.mj_step(model, data)
    Ft[pk] = contact_forces(model, data, floor, (tg,))[tg][0]
    bf = body_forces(model, data)
    vecs = {"gravity_unit": (0, 0, -1), "peak_contact_force_N": Ft[pk]}
    for b, (mag, fv, tv) in bf.items():
        vecs["force_from_body_%s_N" % b] = fv
    frames = part_frames(model, data, meshes, vecs)
    frames["_body_force_N_at_peak"] = {b: {"magnitude": round(mag, 4), "world": [round(float(x), 4) for x in fv]} for b, (mag, fv, tv) in bf.items()}
    impulse = float(np.trapz(Fn, t))
    v_impact = float(np.sqrt(2 * G * height_m))
    tq_abs = np.abs(TQ)
    return {
        "label": label, "robot": robot, "scene_file": os.path.relpath(scene, ROOT), "target_geom": target_geom,
        "struck_geom": struck, "timestep_s": float(model.opt.timestep), "n_steps": int(n),
        "height_m": height_m, "orientation_quat_wxyz": [float(x) for x in orient_quat],
        "height_source": "lane F1 brief (orchestrator, 2026-09-02): 'a 0.250 m fall onto one foot and onto the head' — a chosen input; no requirement document sets a drop height (sim/drop_impact.py H_SOURCE)",
        "solref": list(solref) if solref is not None else "model default (MuJoCo 0.02 s, dampratio 1)",
        "mass_kg": round(mass, 6), "energy_J": round(mass * G * height_m, 5),
        "impact_speed_m_s": round(v_impact, 5), "momentum_Ns": round(mass * v_impact, 5),
        "first_contact_geom": first_geom, "first_contact_time_s": round(first_t, 5) if first_t else None,
        "expected_free_fall_time_s": round(float(np.sqrt(2 * height_m / G)), 5),
        "peak_normal_force_N": round(float(Fn[pk]), 4), "peak_force_vector_world_N": [round(float(x), 4) for x in Ft[pk]],
        "peak_time_s": round(float(t[pk]), 5), "time_to_peak_after_contact_s": round(float(t[pk] - first_t), 5) if first_t else None,
        "impulse_on_target_Ns": round(impulse, 5), "peak_over_bodyweight": round(float(Fn[pk]) / (mass * G), 3),
        "peak_abs_torque_Nm": {j: round(float(v), 5) for j, v in zip(JOINT_NAMES, tq_abs.max(0))},
        "torque_saturated_steps": {j: int(np.sum(tq_abs[:, k] >= 0.999 * model.actuator_forcerange[k, 1]))
                                   for k, j in enumerate(JOINT_NAMES)},
        "peak_normal_force_per_watched_geom_N": {(mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_GEOM, g) or "geom_%d" % g):
                                                 round(float(FnAll[:, j].max()), 4) for j, g in enumerate(watch)},
        "part_frames_at_peak": frames,
        "body_transmitted_force_max_N": {b: {"magnitude": round(v[0], 4), "world": v[1], "time_s": v[2]} for b, v in BFmax.items()},
        "trunk_linear_acceleration_peak_m_s2": round(float(np.linalg.norm(TA, axis=1).max()), 4),
        "trunk_linear_acceleration_peak_vector_world": [round(float(x), 4) for x in TA[int(np.argmax(np.linalg.norm(TA, axis=1)))]],
        "trunk_linear_acceleration_at_contact_peak_world": [round(float(x), 4) for x in TA[pk]],
        "_arrays": {"t": t, "Fn": Fn, "Ft": Ft, "TQ": TQ},
    }


def quat_mul(a, b):
    w1, x1, y1, z1 = a; w2, x2, y2, z2 = b
    return np.array([w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2, w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
                     w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2, w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2])


def axis_quat(axis, deg):
    a = np.radians(deg) / 2
    ax = np.asarray(axis, float); ax /= np.linalg.norm(ax)
    return np.concatenate([[np.cos(a)], np.sin(a) * ax])


def main():
    mass, stand, stand_frames, walk, arrays = walk_and_stand()
    print("mass %.6f kg  weight %.4f N" % (mass, mass * G))
    print("stand: L %.4f N  R %.4f N  closure %.3f %%" % (stand["left_foot_vertical_N"], stand["right_foot_vertical_N"], stand["closure_pct"]))
    print("walk: peak GRF %.4f N (%s foot, %.3fx BW) at t=%.4f s; period %s s; cycles/km %s" % (
        walk["peak_vertical_grf_N"], walk["peak_foot"], walk["peak_grf_over_bodyweight"], walk["peak_grf_time_s"],
        walk["gait"]["period_s_mean"], walk["gait"]["cycles_per_km"]))
    print("walk: peak |torque| " + ", ".join("%s %.4f" % (j, v) for j, v in walk["peak_abs_torque_Nm"].items()))

    # contact stiffness for the "stiff" drop: the TPU sole floor in compression,
    # E_TPU = 0.026 GPa = 26 N/mm^2 (ce-cad/cecad/fits.py MATERIALS["TPU"], a
    # class-tier printed figure, NO datasheet behind it) over the first-contact
    # heel patch. The patch is not known before the run, so this is the
    # sensitivity study: K from the whole sole floor 41.1 x 54 mm / 2.0 mm
    # (part.py sole-left: floor 2.000 mm) as the STIFF bound.
    E_tpu = 26.0                     # N/mm^2
    A_floor = 41.1 * 54.0            # mm^2, sole outer envelope (sole-left part.py bbox)
    t_floor = 2.0                    # mm
    K_tpu = E_tpu * A_floor / t_floor * 1000.0   # N/m
    m_eff_foot = 0.0300246 + 0.0215844           # ankle_left + leg body masses (robot_walk.xml lines 161, 151)
    solref_stiff = (solref_for_stiffness(K_tpu, mass), 1.0)          # whole robot behind the spring
    solref_foot = (solref_for_stiffness(K_tpu, m_eff_foot), 1.0)     # only the foot+shin behind it
    drops = []
    roll10 = axis_quat((1, 0, 0), -10.0)                # roll -10 deg: LEFT sole strikes first (measured: +10 struck the right)
    upright = np.array([1.0, 0, 0, 0])
    for label, robot, q, tg, sr, dt in (
        ("drop_foot_rollm10_default_contact_dt5ms", "walk", roll10, "left_foot_collision", None, None),
        ("drop_foot_rollm10_default_contact_dt50us", "walk", roll10, "left_foot_collision", None, 5e-5),
        ("drop_foot_rollm10_stiff_tpu_whole_mass_dt50us", "walk", roll10, "left_foot_collision", solref_stiff, 5e-5),
        ("drop_foot_rollm10_stiff_tpu_foot_mass_dt50us", "walk", roll10, "left_foot_collision", solref_foot, 5e-5),
        ("drop_foot_upright_default_contact_dt5ms", "walk", upright, "left_foot_collision", None, None),
        ("drop_foot_upright_stiff_tpu_whole_mass_dt50us", "walk", upright, "left_foot_collision", solref_stiff, 5e-5),
    ):
        d = drop(robot, q, tg, 0.250, sr, label=label, dt=dt)
        print("%s: struck %s at %.4f s; peak %.3f N (%.1fx BW) at +%.5f s; impulse %.4f Ns; sat steps knee %d; per-geom %s" % (
            label, d["struck_geom"], d["first_contact_time_s"] or -1, d["peak_normal_force_N"], d["peak_over_bodyweight"],
            d["time_to_peak_after_contact_s"] if d["time_to_peak_after_contact_s"] is not None else -1,
            d["impulse_on_target_Ns"], d["torque_saturated_steps"]["left_knee"], d["peak_normal_force_per_watched_geom_N"]))
        drops.append(d)
    # head first: pitch the whole robot 180 deg about y so the head is lowest
    flip = axis_quat((0, 1, 0), 180.0)
    # the head shell is a collision geom only in the all-collisions model
    model_ac, _ = common.load_model("allcollisions", os.path.join(OUT, "scene_drop_allcollisions.xml"))
    head_geom = None
    for g in range(model_ac.ngeom):
        if model_ac.geom_type[g] == mujoco.mjtGeom.mjGEOM_MESH and \
           mujoco.mj_id2name(model_ac, mujoco.mjtObj.mjOBJ_MESH, int(model_ac.geom_dataid[g])) == "top_head_shell" and \
           (model_ac.geom_contype[g] | model_ac.geom_conaffinity[g]):
            head_geom = g
    assert head_geom is not None, "no collision geom for top_head_shell in robot_allcollisions.xml"
    hname = mujoco.mj_id2name(model_ac, mujoco.mjtObj.mjOBJ_GEOM, head_geom)
    if not hname:
        # unnamed geom: name it by patching the scene xml is heavier than
        # addressing it by id — drop() takes a name, so give it one via a
        # tiny wrapper that resolves by id
        hname = "__geom_id_%d" % head_geom
    K_pla_head = 3500.0 * 20.0 / 1.2 * 1000.0      # N/m
    for label, sr, dt in (("drop_head_default_contact_dt5ms", None, None),
                          ("drop_head_default_contact_dt50us", None, 5e-5),
                          ("drop_head_stiff_pla_dt50us", (solref_for_stiffness(K_pla_head, mass), 1.0), 5e-5)):
        # PLA E 3.5 GPa (fits.MATERIALS["PLA"], class-tier); K taken as a 1.2 mm shell
        # loaded over a ~20 mm^2 first-contact patch in through-thickness compression:
        # 3500 N/mm^2 * 20 mm^2 / 1.2 mm = 5.83e4 N/mm — a deliberately stiff bound.
        d = drop_by_id("allcollisions", flip, head_geom, 0.250, sr, label=label, dt=dt)
        print("%s: struck %s at %.4f s; peak %.3f N (%.1fx BW) at +%.5f s; impulse %.4f Ns" % (
            label, d["struck_geom"], d["first_contact_time_s"] or -1, d["peak_normal_force_N"],
            d["peak_over_bodyweight"], d["time_to_peak_after_contact_s"] if d["time_to_peak_after_contact_s"] is not None else -1,
            d["impulse_on_target_Ns"]))
        drops.append(d)

    npz = {"walk_" + k: v for k, v in arrays.items()}
    for d in drops:
        for k, v in d.pop("_arrays").items():
            npz[d["label"] + "_" + k] = v
    np.savez_compressed(os.path.join(OUT, "loads_mujoco.npz"), **npz)
    out = {
        "study": "loads_mujoco",
        "generated": "2026-09-02",
        "script": "sim/measure_loads.py",
        "model": {"robot_walk": "reference/pollen-microduck-rl/robot_walk.xml",
                  "robot_allcollisions": "reference/pollen-microduck-rl/robot_allcollisions.xml",
                  "units": "MJCF in metres; forces N; torques N m; the part-frame vectors are unit-free directions in each part's own mm frame (Pollen mesh frame, see each part.py FRAME note)",
                  "mass_kg_from_mjcf_inertials": round(mass, 6), "weight_N": round(mass * G, 5), "g_m_s2": G,
                  "actuator_class": "chosen_actuator: position kp 0.55, forcerange +-0.96 N m (robot_walk.xml lines 44-46)"},
        "stand": stand, "part_frames_at_stand": stand_frames,
        "walk": walk,
        "drops": drops,
        "drop_contact_stiffness_basis": {
            "K_tpu_sole_floor_N_per_m": K_tpu, "K_pla_head_shell_N_per_m": K_pla_head,
            "note": "with the 0.005 s policy timestep MuJoCo clamps solref timeconst to 2*dt = 0.01 s, so the stiff contacts are only resolved in the 50 us runs; the 5 ms rows are the policy-training physics", "E_tpu_N_mm2": E_tpu, "A_mm2": A_floor, "t_mm": t_floor,
            "m_eff_foot_kg": m_eff_foot, "solref_stiff_whole_mass": list(solref_stiff), "solref_stiff_foot_mass": list(solref_foot),
            "mapping": "timeconst = sqrt(m_eff / (K * dmax * dampratio^2)), dmax 0.95 (MuJoCo default solimp), see solref_for_stiffness()"},
        "arrays": "out/sim-evidence/loads_mujoco.npz",
    }
    path = os.path.join(OUT, "loads_mujoco.json")
    json.dump(out, open(path, "w"), indent=1)
    print("wrote", path)


def drop_by_id(robot, orient_quat, target_gid, height_m, solref, seconds=0.5, label="", dt=None):
    """drop() for a geom that has no name (the head shell in allcollisions)."""
    model, scene = common.load_model(robot, os.path.join(OUT, "scene_drop_%s.xml" % robot))
    # give the target a name by index lookup: drop() resolves via gid(); patch that
    global gid
    _gid = gid
    def gid_patched(m, name):
        if name.startswith("__geom_id_"):
            return int(name.split("_")[-1])
        return _gid(m, name)
    gid = gid_patched
    try:
        return drop(robot, orient_quat, "__geom_id_%d" % target_gid, height_m, solref, seconds, label, dt=dt)
    finally:
        gid = _gid


if __name__ == "__main__":
    main()
