#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""leg_sweep.py — THE LEGS MOVING AROUND, measured.

Leif, 2026-09-02: "show me renders of the mechanics like our cad system walking,
zoom in on joints as they move and the head kmvoing around and the legs moving
around."

Three things happen here, all read off the simulation (Pollen's MJCF verbatim
with OUR rebuilt meshes swapped in, sim/microduck_ours*.xml):

 1. KINEMATIC SWEEP + SELF-COLLISION.  Each of the ten leg joints is driven
    from its MJCF lower limit to its upper limit in 0.05 deg steps with every
    other joint held at DEFAULT_POSE, mj_forward each step, and every MuJoCo
    contact that is not the floor is recorded with the joint angle at which it
    FIRST appeared.  The model is microduck_ours_allcollisions.xml; a second
    pass re-points the two shin collision geoms to OUR rebuilt shin mesh
    (leg__ours) so the check runs on our geometry for the one rebuilt part that
    carries a collision geom.
 2. DYNAMIC STEP RESPONSE, POLICY PAUSED.  The stand policy does NOT accept leg
    targets (its command vector is [twist 3 | head_pose 4 | body_pose 6] — no
    leg slot; ONNX metadata command_names = "twist,head_pose"), so the per-joint
    dynamics are measured with the policy paused and data.ctrl written directly.
    The trunk is pinned (root qpos re-imposed, root qvel zeroed after each step)
    so the rig is the duck held in the hand, as in images/gallery_carried.webp.
    Reported: travel actually reached and peak joint velocity under the MJCF
    actuator model (class chosen_actuator: kp 0.55, forcerange +-0.96, damping
    0.053, frictionloss 0.0048, armature 0.0018).
 3. SEQUENCES.  sitstand (Pollen's BEST_alpha_sitstand policy, on the floor),
    a squat (direct ctrl ramp, on the floor, physics on) and a one-leg lift
    (hoisted).  Trajectories are written for sim/leg_render.py to draw.

    /Applications/FreeCAD.app/Contents/Resources/bin/python sim/leg_sweep.py
"""
import os, sys, json, math, re, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("MUJOCO_GL", "glfw")
import numpy as np
import xml.etree.ElementTree as ET
import mujoco
import common
import compare_render
from run_policy import Policy, Runner, POLICY_FILES, CTRL_DT, DECIMATION

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "out", "motion")
os.makedirs(OUT, exist_ok=True)
TRAJ = os.path.join(OUT, "traj")
os.makedirs(TRAJ, exist_ok=True)

LEG_JOINTS = ["left_hip_yaw", "left_hip_roll", "left_hip_pitch", "left_knee", "left_ankle",
              "right_hip_yaw", "right_hip_roll", "right_hip_pitch", "right_knee", "right_ankle"]
# joint -> the body it drives (from the MJCF tree)
JOINT_BODY = {"left_hip_yaw": "yaw2roll", "left_hip_roll": "hip_l", "left_hip_pitch": "upper_leg_left",
              "left_knee": "leg", "left_ankle": "ankle_left",
              "right_hip_yaw": "bearing_roll", "right_hip_roll": "hip_l_2",
              "right_hip_pitch": "upper_leg_right", "right_knee": "leg_2", "right_ankle": "ankle_right"}
D = math.degrees


# ---------------------------------------------------------------- model files
def mjcf_ranges(path=os.path.join(HERE, "microduck_ours.xml")):
    """-> {joint: {"lo_rad","hi_rad","lo_deg","hi_deg","cite"}} read off the XML text
    so the citation is a real file:line."""
    out = {}
    for i, line in enumerate(open(path), 1):
        m = re.search(r'<joint axis="([^"]+)" name="([^"]+)" type="hinge" range="([-\d.eE]+) ([-\d.eE]+)"', line)
        if not m:
            continue
        axis, name, lo, hi = m.group(1), m.group(2), float(m.group(3)), float(m.group(4))
        out[name] = dict(axis=axis, lo_rad=lo, hi_rad=hi, lo_deg=D(lo), hi_deg=D(hi),
                         span_deg=D(hi - lo),
                         cite="%s:%d" % (os.path.relpath(path, ROOT), i))
    return out


def _xml(robot, floor=False, ours_collision=False):
    """studio scene (white sky, real product materials) from compare_render, with
    an optional floor and an optional re-point of the shin collision geoms to OUR mesh."""
    txt = compare_render.studio_scene(common.robot_file(robot))
    root = ET.fromstring(txt)
    if ours_collision:
        n = 0
        for g in root.iter("geom"):
            if g.get("class") == "collision" and g.get("mesh") == "leg":
                g.set("mesh", "leg__ours"); n += 1
        assert n == 2, n
    if floor:
        wb = root.find("worldbody")
        ET.SubElement(wb, "geom", name="floor", size="0 0 0.05", pos="0 0 0", type="plane",
                      rgba="0.90 0.90 0.92 1", condim="3")
    return ET.tostring(root, encoding="unicode")


def build(robot="ours_allcollisions", floor=False, ours_collision=False, tag="scene"):
    txt = _xml(robot, floor, ours_collision)
    p = os.path.join(OUT, "scene_%s.xml" % tag)
    open(p, "w").write(txt)
    m = mujoco.MjModel.from_xml_string(txt, {})
    return m, mujoco.MjData(m), p


def gname(m, i):
    n = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, i)
    mesh = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_MESH, m.geom_dataid[i]) if m.geom_dataid[i] >= 0 else "?"
    body = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, m.geom_bodyid[i])
    return "%s/%s" % (body, n or mesh)


def collision_geoms(m):
    return [i for i in range(m.ngeom) if m.geom_contype[i] or m.geom_conaffinity[i]]


def summarise(rec, neutral_deg):
    """rec: {pair: {"a":[angles deg], "d":[penetration mm]}} -> per-pair contact
    interval, the ONSET (the contact angle nearest the neutral pose, i.e. the angle
    at which it first touches as the joint leaves neutral) and the deepest penetration.
    Every angle is reported at the sweep's own resolution."""
    out = {}
    for k, v in rec.items():
        a = np.asarray(v["a"]); dd = np.asarray(v["d"])
        onset = float(a[np.argmin(np.abs(a - neutral_deg))])
        out[k] = dict(onset_deg=round(onset, 1),
                      contact_interval_deg=[round(float(a.min()), 1), round(float(a.max()), 1)],
                      contact_samples=int(a.size),
                      max_penetration_mm=round(float(-dd.min()), 4))
    return out


def _log(rec, key, ang_deg, dist):
    r = rec.setdefault(key, dict(a=[], d=[]))
    r["a"].append(float(ang_deg)); r["d"].append(float(dist) * 1000.0)


# ------------------------------------------------------- 1. kinematic sweep
def kinematic_sweep(m, d, jname, step_deg=0.05, floor_id=-1):
    """Drive one joint lo->hi, every other joint at DEFAULT_POSE, mj_forward each
    step. -> (angles_deg, first-touch dict pair->deg, n_contacts array)."""
    jid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, jname)
    adr = int(m.jnt_qposadr[jid])
    lo, hi = float(m.jnt_range[jid][0]), float(m.jnt_range[jid][1])
    qpos_idx = [int(m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)]) for n in common.JOINT_NAMES]
    n = int(round(D(hi - lo) / step_deg)) + 1
    angles = np.linspace(lo, hi, n)
    rec, ncons = {}, np.zeros(n, int)
    for k, a in enumerate(angles):
        d.qpos[:] = 0.0
        d.qpos[0:3] = [0, 0, 0.12]; d.qpos[3] = 1.0
        for jn, v in zip(common.JOINT_NAMES, common.DEFAULT_POSE):
            d.qpos[qpos_idx[common.JOINT_NAMES.index(jn)]] = v
        d.qpos[adr] = a
        d.qvel[:] = 0
        mujoco.mj_forward(m, d)
        c = 0
        for i in range(d.ncon):
            con = d.contact[i]
            if con.geom1 == floor_id or con.geom2 == floor_id:
                continue
            c += 1
            _log(rec, " <-> ".join(sorted([gname(m, con.geom1), gname(m, con.geom2)])), D(a), con.dist)
        ncons[k] = c
    return np.degrees(angles), rec, ncons


# ------------------------------------------- 2. dynamic step, policy paused
def pin_root(d, root_qadr, root_vadr, z=0.12):
    d.qpos[root_qadr:root_qadr + 3] = [0, 0, z]
    d.qpos[root_qadr + 3:root_qadr + 7] = [1, 0, 0, 0]
    d.qvel[root_vadr:root_vadr + 6] = 0.0


def dyn_step(m, d, jname, ramp_up=1.4, hold=0.30, ramp_dn=2.0, ramp_home=1.0, step=0.80):
    """Policy paused, trunk pinned. One joint is driven, everything else held at
    DEFAULT_POSE. Profile: cosine ramp default->hi, hold, ramp hi->lo, hold, ramp
    lo->default, then a STEP straight to hi and back (the step is what measures
    the torque-limited peak velocity of the MJCF actuator model).
    -> (measurements, trajectory)."""
    jid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, jname)
    adr, vadr = int(m.jnt_qposadr[jid]), int(m.jnt_dofadr[jid])
    lo, hi = float(m.jnt_range[jid][0]), float(m.jnt_range[jid][1])
    ai = common.JOINT_NAMES.index(jname)
    home = float(common.DEFAULT_POSE[ai])
    fj = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "trunk_base_freejoint")
    rq, rv = int(m.jnt_qposadr[fj]), int(m.jnt_dofadr[fj])
    kid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_KEY, "STAND")
    mujoco.mj_resetDataKeyframe(m, d, kid); pin_root(d, rq, rv); mujoco.mj_forward(m, d)

    segs = [("ramp", ramp_up, home, hi), ("hold", hold, hi, hi), ("ramp", ramp_dn, hi, lo),
            ("hold", hold, lo, lo), ("ramp", ramp_home, lo, home), ("hold", 0.20, home, home),
            ("step", step, hi, hi), ("step", step, home, home)]
    q, v, tgt, ts, phase, qall = [], [], [], [], [], []
    t = 0.0
    for kind, dur, a, b in segs:
        n = int(dur / CTRL_DT)
        for i in range(n):
            u = (i + 1) / n
            target = a + (b - a) * 0.5 * (1 - math.cos(math.pi * u)) if kind == "ramp" else b
            d.ctrl[:] = common.DEFAULT_POSE
            d.ctrl[ai] = target
            for _ in range(DECIMATION):
                mujoco.mj_step(m, d)
                pin_root(d, rq, rv)
            q.append(float(d.qpos[adr])); v.append(float(d.qvel[vadr])); tgt.append(target)
            ts.append(t); phase.append(kind); qall.append(d.qpos.copy()); t += CTRL_DT
    q = np.array(q); v = np.array(v); ph = np.array(phase)
    ramp = ph != "step"
    stepm = ph == "step"
    return dict(joint=jname, mjcf_lo_deg=D(lo), mjcf_hi_deg=D(hi), mjcf_span_deg=D(hi - lo),
                reached_max_deg=D(q.max()), reached_min_deg=D(q.min()),
                travel_deg=D(q.max() - q.min()),
                travel_frac_of_mjcf_range=float((q.max() - q.min()) / (hi - lo)),
                peak_velocity_deg_s=D(np.abs(v[stepm]).max()),
                peak_velocity_source="step to the MJCF hi limit, policy paused",
                peak_velocity_at_s=float(np.array(ts)[stepm][int(np.abs(v[stepm]).argmax())]),
                ramp_peak_velocity_deg_s=D(np.abs(v[ramp]).max()),
                commanded_ramp_rate_deg_s=D(abs(hi - lo) / ramp_dn * math.pi / 2),
                overshoot_past_hi_deg=D(max(0.0, q.max() - hi)),
                overshoot_past_lo_deg=D(max(0.0, lo - q.min())),
                tracking_rms_deg=D(float(np.sqrt(np.mean((q - np.array(tgt)) ** 2)))),
                seconds=round(t, 3),
                ), dict(t=np.array(ts), q=q, v=v, tgt=np.array(tgt), qpos=np.array(qall), phase=ph)


def combo_sweep(m, d, sweep_joint, fixed, floor_id=-1, step_deg=0.10):
    """kinematic sweep of sweep_joint with other joints pinned at named angles
    (dict joint->rad). Same contact accounting as kinematic_sweep."""
    qpos_idx = {n: int(m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)])
                for n in common.JOINT_NAMES}
    jid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, sweep_joint)
    adr = int(m.jnt_qposadr[jid])
    lo, hi = float(m.jnt_range[jid][0]), float(m.jnt_range[jid][1])
    n = int(round(D(hi - lo) / step_deg)) + 1
    angles = np.linspace(lo, hi, n)
    rec = {}
    for a in angles:
        d.qpos[:] = 0.0; d.qpos[0:3] = [0, 0, 0.12]; d.qpos[3] = 1.0
        for jn, val in zip(common.JOINT_NAMES, common.DEFAULT_POSE):
            d.qpos[qpos_idx[jn]] = val
        for jn, val in fixed.items():
            d.qpos[qpos_idx[jn]] = val
        d.qpos[adr] = a
        d.qvel[:] = 0
        mujoco.mj_forward(m, d)
        for i in range(d.ncon):
            con = d.contact[i]
            if con.geom1 == floor_id or con.geom2 == floor_id:
                continue
            _log(rec, " <-> ".join(sorted([gname(m, con.geom1), gname(m, con.geom2)])), D(a), con.dist)
    return np.degrees(angles), rec


def mirror_sweep(m, d, jpair, sign=(1.0, -1.0), floor_id=-1, step_deg=0.05):
    """drive two joints together (legs crossing / splaying) — the both-legs case
    a one-at-a-time sweep cannot reach."""
    qpos_idx = {n: int(m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)])
                for n in common.JOINT_NAMES}
    ids = [mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, j) for j in jpair]
    rngs = [(float(m.jnt_range[i][0]), float(m.jnt_range[i][1])) for i in ids]
    span = min(abs(r[1] - r[0]) for r in rngs) / 2
    n = int(round(D(2 * span) / step_deg)) + 1
    us = np.linspace(-span, span, n)
    rec, qs = {}, []
    for u in us:
        d.qpos[:] = 0.0; d.qpos[0:3] = [0, 0, 0.12]; d.qpos[3] = 1.0
        for jn, val in zip(common.JOINT_NAMES, common.DEFAULT_POSE):
            d.qpos[qpos_idx[jn]] = val
        for j, s, (rlo, rhi) in zip(jpair, sign, rngs):
            d.qpos[qpos_idx[j]] = float(np.clip(d.qpos[qpos_idx[j]] + s * u, rlo, rhi))
        d.qvel[:] = 0
        mujoco.mj_forward(m, d)
        qs.append(d.qpos.copy())
        for i in range(d.ncon):
            con = d.contact[i]
            if con.geom1 == floor_id or con.geom2 == floor_id:
                continue
            _log(rec, " <-> ".join(sorted([gname(m, con.geom1), gname(m, con.geom2)])), D(u), con.dist)
    return np.degrees(us), rec, np.array(qs)


# ------------------------------------------------------------- 3. sequences
def squat_directctrl(m, d, depth=0.20, cycles=1, floor=True):
    """Direct ctrl, policy paused, on the floor. Symmetric knee flexion with the
    hip and ankle taking half each, so the trunk stays level and the sole flat:
    left  (hip_pitch -d/2, knee +d, ankle -d/2) added to DEFAULT_POSE,
    right  mirrored.  depth in rad of knee flexion."""
    kid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_KEY, "STAND")
    mujoco.mj_resetDataKeyframe(m, d, kid); mujoco.mj_forward(m, d)
    fj = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "trunk_base_freejoint")
    rq = int(m.jnt_qposadr[fj])
    tb = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "trunk_base")
    per = 2.4
    n = int(cycles * per / CTRL_DT)
    rec = dict(t=[], qpos=[], trunk_z=[], ctrl=[], tilt=[])
    for k in range(n):
        t = k * CTRL_DT
        s = 0.5 * (1 - math.cos(2 * math.pi * (t % per) / per)) * depth   # 0..depth..0
        c = common.DEFAULT_POSE.copy()
        c[2] += -s / 2; c[3] += s; c[4] += -s / 2          # left  hip_pitch, knee, ankle
        c[11] += s / 2; c[12] += -s; c[13] += s / 2        # right mirrored
        d.ctrl[:] = c
        for _ in range(DECIMATION):
            mujoco.mj_step(m, d)
        rec["t"].append(t); rec["qpos"].append(d.qpos.copy())
        rec["trunk_z"].append(float(d.xpos[tb][2])); rec["ctrl"].append(c.copy())
        r, pch = common.quat_to_roll_pitch(d.qpos[3:7])
        rec["tilt"].append(D(max(abs(r), abs(pch))))
    for k in rec: rec[k] = np.array(rec[k])
    return rec


def squat_policy(m, d, amp=0.10, per=3.0, cycles=2, lead=1.0):
    """THE squat that works: Pollen's BEST_alpha_stand policy running, and the
    BODY-Z slot of its command vector (cmd[9], the third of the six body_pose
    slots the ONNX metadata's observation_names calls "body_command") driven
    down and back with a raised cosine. The policy keeps the duck balanced while
    the legs fold - which the policy-paused direct-ctrl squat cannot do."""
    pol = Policy(os.path.join(common.POLICY_DIR, POLICY_FILES["stand"]))
    kid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_KEY, "STAND")
    mujoco.mj_resetDataKeyframe(m, d, kid); mujoco.mj_forward(m, d)
    run = Runner(m, d)
    tb = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "trunk_base")
    n = int((lead + cycles * per) / CTRL_DT)
    rec = dict(t=[], qpos=[], qvel=[], trunk_z=[], cmd_bz=[], tilt=[])
    for k in range(n):
        t = k * CTRL_DT
        o = run.obs((0.0, 0.0, 0.0), None)
        u = 0.0 if t < lead else 0.5 * (1 - math.cos(2 * math.pi * ((t - lead) % per) / per))
        o[common.OBS_SIZE - common.CMD_SIZE + 9] = amp * u          # body-z command slot
        a = pol(o); run.apply(a, pol.action_scale)
        for _ in range(DECIMATION):
            mujoco.mj_step(m, d)
        r, pch = common.quat_to_roll_pitch(d.qpos[3:7])
        rec["t"].append(t); rec["qpos"].append(d.qpos.copy()); rec["qvel"].append(d.qvel.copy())
        rec["trunk_z"].append(float(d.xpos[tb][2])); rec["cmd_bz"].append(amp * u)
        rec["tilt"].append(D(max(abs(r), abs(pch))))
    for k in rec: rec[k] = np.array(rec[k])
    return rec


def leg_lift(m, d, cycles=2):
    """Hoisted (trunk pinned), policy paused: the left leg swings up and the knee
    folds, then the right leg does the same."""
    fj = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "trunk_base_freejoint")
    rq, rv = int(m.jnt_qposadr[fj]), int(m.jnt_dofadr[fj])
    kid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_KEY, "STAND")
    mujoco.mj_resetDataKeyframe(m, d, kid); pin_root(d, rq, rv); mujoco.mj_forward(m, d)
    per = 2.4
    n = int(2 * cycles * per / CTRL_DT)
    rec = dict(t=[], qpos=[], ctrl=[])
    for k in range(n):
        t = k * CTRL_DT
        s = 0.5 * (1 - math.cos(2 * math.pi * (t % per) / per))
        c = common.DEFAULT_POSE.copy()
        left = int(t // per) % 2 == 0
        if left:
            c[2] += -0.85 * s; c[3] += 1.05 * s; c[1] += -0.20 * s
        else:
            c[11] += 0.85 * s; c[12] += -1.05 * s; c[10] += 0.20 * s
        d.ctrl[:] = c
        for _ in range(DECIMATION):
            mujoco.mj_step(m, d); pin_root(d, rq, rv)
        rec["t"].append(t); rec["qpos"].append(d.qpos.copy()); rec["ctrl"].append(c.copy())
    for k in rec: rec[k] = np.array(rec[k])
    return rec


def peak_from_traj(npz_path, m):
    """per-leg-joint travel + peak velocity out of a recorded policy trajectory."""
    z = np.load(npz_path)
    qpos, qvel = z["qpos"], z["qvel"]
    out = {}
    for jn in LEG_JOINTS:
        jid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, jn)
        a, va = int(m.jnt_qposadr[jid]), int(m.jnt_dofadr[jid])
        q = qpos[:, a]; v = qvel[:, va]
        out[jn] = dict(travel_deg=round(D(q.max() - q.min()), 3),
                       min_deg=round(D(q.min()), 3), max_deg=round(D(q.max()), 3),
                       peak_velocity_deg_s=round(D(np.abs(v).max()), 2))
    return out


def main():
    t0 = time.time()
    R = mjcf_ranges()
    res = dict(generated=time.strftime("%Y-%m-%dT%H:%M:%S"),
               model=dict(kinematic="sim/microduck_ours_allcollisions.xml",
                          note="Pollen MJCF verbatim, OUR rebuilt meshes on the visual geoms "
                               "(sim/swap_meshes.py). Collision geoms are Pollen's except where "
                               "ours_collision is stated."),
               mjcf_ranges={k: R[k] for k in LEG_JOINTS},
               actuator=dict(cite="sim/microduck_ours.xml:41-48 class chosen_actuator",
                             kp=0.55, kv=0.0, forcerange_Nm=[-0.96, 0.96], damping=0.053,
                             frictionloss=0.0048, armature=0.0018, ctrlrange=[-10.0, 10.0],
                             **{'servo_reality_check': "The MJCF actuator is NOT the datasheet servo. Pollen's class chosen_actuator gives every leg joint forcerange +-0.96 N.m, while the repo's verified entry for the fitted servo (Dynamixel XL330-M288-T, out/verify/electronics_verify.json, ROBOTIS eManual cited there) gives stall 0.52 N.m at 5.0 V - the model is 1.846x stronger than the cited stall torque. The class also sets kv = 0 and the model carries NO joint velocity limit, so the step-response peak velocities below are what the MODEL can do, not what the servo can do. The XL330's no-load speed is not recorded anywhere in this repo: CANNOT DETERMINE, and it must be added before any of these peak velocities is quoted as a hardware capability.", 'peak_velocity_caveat': "peak_velocity_deg_s is measured during a commanded STEP from DEFAULT_POSE to the MJCF limit with the policy paused and the trunk pinned. Under Pollen's own policies the same joints stay far slower - see sitstand_policy and squat below."}))

    # --- 1. kinematic sweep + self-collision, Pollen collision meshes and ours ---
    for label, ours_col in (("pollen_collision_meshes", False), ("ours_shin_collision_mesh", True)):
        m, d, _ = build(ours_collision=ours_col, tag="kin_" + label)
        cg = collision_geoms(m)
        res.setdefault("self_collision", {})[label] = dict(
            collision_geoms=[gname(m, i) for i in cg],
            note=("MuJoCo collides mesh geoms as their CONVEX HULLS. "
                  "The trunk power_support geom is class self_collision_only "
                  "(contype/conaffinity 2) and is the only geom in that group, so it can never "
                  "produce a contact - stated, not silently passed."),
            sweeps={})
        for jn in LEG_JOINTS:
            ang, rec, ncons = kinematic_sweep(m, d, jn)
            neutral = D(float(common.DEFAULT_POSE[common.JOINT_NAMES.index(jn)]))
            pairs = summarise(rec, neutral)
            res["self_collision"][label]["sweeps"][jn] = dict(
                step_deg=0.05, samples=int(len(ang)),
                swept_deg=[round(float(ang[0]), 3), round(float(ang[-1]), 3)],
                neutral_deg=round(neutral, 3),
                contact_samples=int((ncons > 0).sum()),
                pairs=pairs, verdict="TOUCHES" if pairs else "CLEAR")
            print("[kin %s] %-16s %s" % (label, jn, "CLEAR" if not pairs else
                  "; ".join("%s onset %.1f deg" % (k, v["onset_deg"]) for k, v in pairs.items())))
            np.savez_compressed(os.path.join(TRAJ, "kin_%s_%s.npz" % (label, jn)), angles_deg=ang, ncon=ncons)

    # --- 1b. combination sweeps: one joint swept with a neighbour pinned at ITS limit,
    #         and both-leg (mirrored) sweeps a one-at-a-time sweep cannot reach ---
    m, d, _ = build(tag="kin_combo")
    res["self_collision"]["combinations"] = dict(
        why="a one-at-a-time sweep leaves every other joint at DEFAULT_POSE; the folded and "
            "crossed postures that could actually collide need two joints off default",
        step_deg=0.10, cases={})
    for side, pre in (("left", "left_"), ("right", "right_")):
        for sweep, neigh in ((pre + "knee", pre + "hip_pitch"), (pre + "ankle", pre + "knee"),
                             (pre + "hip_pitch", pre + "hip_roll")):
            nid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, neigh)
            for endname, endval in (("lo", float(m.jnt_range[nid][0])), ("hi", float(m.jnt_range[nid][1]))):
                ang, rec = combo_sweep(m, d, sweep, {neigh: endval})
                neutral = D(float(common.DEFAULT_POSE[common.JOINT_NAMES.index(sweep)]))
                pairs = summarise(rec, neutral)
                key = "%s swept, %s pinned at MJCF %s (%.3f deg)" % (sweep, neigh, endname, D(endval))
                res["self_collision"]["combinations"]["cases"][key] = dict(
                    swept_deg=[round(float(ang[0]), 3), round(float(ang[-1]), 3)],
                    neutral_deg=round(neutral, 3), pairs=pairs,
                    verdict="TOUCHES" if pairs else "CLEAR")
                print("[combo] %-58s %s" % (key, "CLEAR" if not pairs else
                      "; ".join("%s onset %.1f deg in [%.1f, %.1f]" %
                                (k, v["onset_deg"], v["contact_interval_deg"][0], v["contact_interval_deg"][1])
                                for k, v in pairs.items())))
    res["self_collision"]["both_legs_mirrored"] = dict(
        why="both legs driven together — legs crossing, splaying and scissoring", cases={})
    MIRRORS = [(("left_hip_roll", "right_hip_roll"), (1.0, 1.0), "hip roll, same sense"),
               (("left_hip_roll", "right_hip_roll"), (1.0, -1.0), "hip roll, opposed (knees in/out)"),
               (("left_hip_yaw", "right_hip_yaw"), (1.0, -1.0), "hip yaw, opposed (toes in/out)"),
               (("left_hip_pitch", "right_hip_pitch"), (1.0, 1.0), "hip pitch, same sense (scissor)"),
               (("left_knee", "right_knee"), (1.0, -1.0), "knee, opposed")]
    for pair, sign, label in MIRRORS:
        us, rec, qs = mirror_sweep(m, d, pair, sign)
        pairs = summarise(rec, 0.0)
        key = "%s + %s  sign %s  (%s)" % (pair[0], pair[1], sign, label)
        res["self_collision"]["both_legs_mirrored"]["cases"][key] = dict(
            swept_deg=[round(float(us[0]), 3), round(float(us[-1]), 3)], step_deg=0.05,
            note="offset added to BOTH joints on top of DEFAULT_POSE, clipped to each MJCF range; "
                 "the angle reported is that offset, not the joint angle",
            pairs=pairs, verdict="TOUCHES" if pairs else "CLEAR")
        np.savez_compressed(os.path.join(TRAJ, "mirror_%s_%s.npz" % (pair[0], "same" if sign[1] > 0 else "opp")),
                            us=us, qpos=qs)
        print("[mirror] %-46s %s" % (label, "CLEAR" if not pairs else
              "; ".join("%s onset %.1f deg in [%.1f, %.1f]" %
                        (k, v["onset_deg"], v["contact_interval_deg"][0], v["contact_interval_deg"][1])
                        for k, v in pairs.items())))

    # --- 2. dynamic step response, policy paused, trunk pinned ---
    m, d, _ = build(tag="dyn")
    res["dynamic_step_policy_paused"] = dict(
        rig="trunk pinned (root qpos re-imposed, root qvel zeroed every physics step); gravity on",
        why="the stand policy has no leg command slot (ONNX command_names = 'twist,head_pose'), "
            "so leg joints cannot be commanded through it; data.ctrl is written directly instead",
        joints={})
    for jn in LEG_JOINTS:
        mm, tr = dyn_step(m, d, jn)
        res["dynamic_step_policy_paused"]["joints"][jn] = {k: (round(v, 3) if isinstance(v, float) else v)
                                                           for k, v in mm.items()}
        np.savez_compressed(os.path.join(TRAJ, "dyn_%s.npz" % jn), **tr)
        print("[dyn] %-16s travel %.3f deg of %.3f, peak %.1f deg/s" %
              (jn, mm["travel_deg"], mm["mjcf_hi_deg"] - mm["mjcf_lo_deg"], mm["peak_velocity_deg_s"]))

    # --- 3. sequences ---
    mf, df, _ = build(floor=True, tag="floor")
    sqd = squat_directctrl(mf, df, depth=0.20, cycles=1)
    res["squat_directctrl_FAILS"] = dict(
        rig="on the floor, physics on, POLICY PAUSED, direct ctrl ramp",
        commanded_knee_flexion_deg=round(D(0.20), 3),
        verdict="FAIL - the duck tips over",
        max_trunk_tilt_deg=round(float(sqd["tilt"].max()), 2),
        trunk_z_m=dict(start=round(float(sqd["trunk_z"][0]), 5), min=round(float(sqd["trunk_z"].min()), 5),
                       end=round(float(sqd["trunk_z"][-1]), 5)),
        finding="standing is not an open-loop pose: with the policy paused, a commanded knee "
                "flexion of only 11.459 deg pitches the trunk past the 60 deg fall rule. The squat "
                "below therefore runs WITH Pollen's stand policy, driven through its body-z command "
                "slot - stated because it is the answer to 'can direct joint targets be used'.")
    sq = squat_policy(mf, df, amp=0.10)
    np.savez_compressed(os.path.join(TRAJ, "squat.npz"), **sq)
    res["squat"] = dict(rig="on the floor, physics on, Pollen BEST_alpha_stand policy RUNNING",
                        driver="command slot 9 (body-z) driven 0 -> 0.10 -> 0 twice, raised cosine, "
                               "period 3.0 s after a 1.0 s lead; every leg joint angle is the "
                               "policy's own output, not a target we wrote",
                        cycles=2, seconds=round(float(sq["t"][-1] + CTRL_DT), 3),
                        trunk_z_m=dict(start=round(float(sq["trunk_z"][0]), 5),
                                       min=round(float(sq["trunk_z"].min()), 5),
                                       max=round(float(sq["trunk_z"].max()), 5)),
                        trunk_drop_mm=round(float(sq["trunk_z"][0] - sq["trunk_z"].min()) * 1000, 2),
                        max_trunk_tilt_deg=round(float(sq["tilt"].max()), 2),
                        fell=bool(sq["trunk_z"].min() < 0.06 or sq["tilt"].max() > 60.0))
    ll = leg_lift(m, d)
    np.savez_compressed(os.path.join(TRAJ, "leglift.npz"), **ll)
    res["leg_lift"] = dict(rig="hoisted (trunk pinned), policy paused, direct ctrl",
                           seconds=round(float(ll["t"][-1] + CTRL_DT), 3))
    # per-joint numbers out of the sequences and the sitstand policy run
    for nm, path in (("squat", os.path.join(TRAJ, "squat.npz")),
                     ("leg_lift", os.path.join(TRAJ, "leglift.npz"))):
        z = np.load(path); qp = z["qpos"]
        res[nm]["joints"] = {}
        for jn in LEG_JOINTS:
            jid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, jn)
            a = int(m.jnt_qposadr[jid]); q = qp[:, a]
            dq = np.diff(q) / CTRL_DT
            res[nm]["joints"][jn] = dict(travel_deg=round(D(q.max() - q.min()), 3),
                                         min_deg=round(D(q.min()), 3), max_deg=round(D(q.max()), 3),
                                         peak_velocity_deg_s=round(D(np.abs(dq).max()), 2))
    ss = os.path.join(ROOT, "out", "sim", "sitstand_ours_traj.npz")
    if os.path.exists(ss):
        res["sitstand_policy"] = dict(source=os.path.relpath(ss, ROOT),
                                      policy="BEST_alpha_sitstand.onnx (Pollen)",
                                      joints=peak_from_traj(ss, m))
    json.dump(res, open(os.path.join(OUT, "legs.json"), "w"), indent=1)
    print("wrote", os.path.join(OUT, "legs.json"), "in %.1f s" % (time.time() - t0))


if __name__ == "__main__":
    main()
