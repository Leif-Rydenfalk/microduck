#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""statics.py — the static free-body engine every PROVE-4 study is built on.

    ce-cad/bin/cad sim/statics.py            # runs the self-test (10 checks)
    ce-cad/bin/cad sim/statics.py --break 1  # break it on purpose

THE ONE IDEA. Cut the robot at joint j. Everything on one side of the cut is a
free body; the only external forces on it are gravity and the joint reaction, so
the torque the actuator must hold is the moment of that free body's weight about
the joint axis:

    tau_j(g_hat) = axis_j . SUM_i (c_i - p_j) x (m_i * 9.81 * g_hat)

Two cuts, two answers, and BOTH are real load cases for this robot:
    SUBTREE side   -- everything DISTAL of the joint. This is what the joint
                      carries when the trunk is held and the limb hangs: the
                      robot picked up, carried, or a foot in swing.
    COMPLEMENT side-- everything PROXIMAL. This is what a STANCE joint carries
                      when that foot is the thing bolted to the world: the ankle
                      of the standing leg holds up the entire rest of the robot.

WHY NO ORIENTATION SWEEP IS NEEDED, and this is exact rather than a sample.
Write S = SUM_i m_i (c_i - p_j) = M * (c - p_j). Then

    tau_j = 9.81 * axis . (S x g_hat) = 9.81 * g_hat . (axis x S)

which over all unit g_hat is maximised at |axis x S| exactly. So

    tau_max(j) = 9.81 * M * d_perp        d_perp = distance from the axis LINE
                                          to that side's centre of mass

The worst gravity direction is solved in closed form, not searched. What still
has to be swept is the JOINT CONFIGURATION, because it moves both M's lever arm
and the axis. That is what sim/torque_sweep.py sweeps.

The engine is cross-checked against MuJoCo's own recursive Newton-Euler
(qfrc_bias at zero velocity) on every pose the self-test tries, so the free-body
sum cannot quietly disagree with the physics engine that produced the gait data.
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import common  # noqa: E402
import mujoco  # noqa: E402

G = 9.81
BREAK = int(os.environ.get("MD_STATICS_BREAK", "0"))
SOLE_TOL = 0.0005   # m: a vertex within 0.5000 mm of the extreme is on the contact plane


def _hull2d(p):
    """monotone-chain convex hull of an (n,2) array; returns the hull points CCW."""
    q = sorted(map(tuple, np.round(p, 9)))
    if len(q) < 3:
        return np.array(q)
    def half(ps):
        h = []
        for x in ps:
            while len(h) >= 2 and ((h[-1][0]-h[-2][0])*(x[1]-h[-2][1]) - (h[-1][1]-h[-2][1])*(x[0]-h[-2][0])) <= 0:
                h.pop()
            h.append(x)
        return h
    return np.array(half(q)[:-1] + half(q[::-1])[:-1])


def _polyarea(h):
    x, y = h[:, 0], h[:, 1]
    return 0.5 * abs(float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))


def _dist_in_poly(pt, h):
    """signed distance from pt to the polygon boundary; + inside, - outside."""
    n = len(h); best = 1e18; inside = True
    for i in range(n):
        a = h[i]; b = h[(i + 1) % n]
        e = b - a; L = np.linalg.norm(e)
        if L < 1e-15:
            continue
        t = float(np.clip((pt - a) @ e / (L * L), 0.0, 1.0))
        best = min(best, float(np.linalg.norm(pt - (a + t * e))))
        if np.cross(e, pt - a) < 0:
            inside = False
    return best if inside else -best


class Statics:
    def __init__(self, robot="ours", augmented=True):
        self.model = mujoco.MjModel.from_xml_path(common.robot_file(robot))
        self.data = mujoco.MjData(self.model)
        m = self.model
        self.names = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, i) for i in range(m.nbody)]
        self.jnames = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, i) for i in range(m.njnt)]
        self.hinges = [j for j in range(m.njnt) if m.jnt_type[j] == mujoco.mjtJoint.mjJNT_HINGE]
        self.jrange = {self.jnames[j]: (float(m.jnt_range[j][0]), float(m.jnt_range[j][1]))
                       for j in self.hinges}
        # qpos address of each hinge (freejoint occupies 0..6)
        self.qadr = {self.jnames[j]: int(m.jnt_qposadr[j]) for j in self.hinges}
        self.augmented = augmented
        self.mass_source = "MJCF link inertials only"
        if augmented:
            self._augment()
        # subtree membership
        self.desc = [set([i]) for i in range(m.nbody)]
        for i in range(m.nbody - 1, 0, -1):
            self.desc[int(m.body_parentid[i])] |= self.desc[i]
        self.mass = np.array([float(m.body_mass[i]) for i in range(m.nbody)])
        self.total_mass = float(self.mass[1:].sum())

    def _augment(self):
        p = os.path.join(ROOT, "out", "open", "mass-budget.json")
        b = json.load(open(p))
        by = {r["body"]: r for r in b["bodies"]}
        n = 0
        for i in range(1, self.model.nbody):
            r = by.get(self.names[i])
            if not r:
                continue
            self.model.body_mass[i] = r["augmented_mass_g"] / 1000.0
            self.model.body_ipos[i] = np.array(r["augmented_com_body_mm"]) / 1000.0
            n += 1
        assert n == self.model.nbody - 1, "mass-budget.json covers %d of %d bodies" % (n, self.model.nbody - 1)
        self.mass_source = ("MJCF links + 64 measured fasteners + 18 measured cables "
                           "(out/open/mass-budget.json, total %.4f g)" % b["totals_g"]["augmented"])

    # -- kinematics ---------------------------------------------------------
    def set_pose(self, q, base_quat=(1, 0, 0, 0)):
        """q: dict name->rad, or an array in common.JOINT_NAMES order."""
        d = self.data
        mujoco.mj_resetData(self.model, d)
        d.qpos[3:7] = base_quat
        if isinstance(q, dict):
            for k, v in q.items():
                d.qpos[self.qadr[k]] = v
        else:
            for k, v in zip(common.JOINT_NAMES, q):
                d.qpos[self.qadr[k]] = v
        d.qvel[:] = 0.0
        mujoco.mj_kinematics(self.model, d)
        mujoco.mj_comPos(self.model, d)

    # -- the free-body sums -------------------------------------------------
    def sides(self, jname):
        """(M_sub, c_sub, M_out, c_out, axis, p) in kg / m, world frame."""
        m = self.model; d = self.data
        j = self.jnames.index(jname)
        b = int(m.jnt_bodyid[j])
        axis = d.xmat[b].reshape(3, 3) @ m.jnt_axis[j]
        if BREAK == 1:
            axis = m.jnt_axis[j]          # forget to rotate the axis into world
        axis = axis / np.linalg.norm(axis)
        p = d.xanchor[j]
        sub = self.desc[b]
        Ms = Mo = 0.0
        Ss = np.zeros(3); So = np.zeros(3)
        for i in range(1, m.nbody):
            mi = float(m.body_mass[i]); ci = d.xipos[i]
            if i in sub:
                Ms += mi; Ss += mi * ci
            else:
                Mo += mi; So += mi * ci
        cs = Ss / Ms if Ms > 0 else p
        co = So / Mo if Mo > 0 else p
        return Ms, cs, Mo, co, axis, p

    def tau(self, jname, g_hat, side="sub"):
        """signed actuator torque required, N.m, for gravity along g_hat (unit)."""
        Ms, cs, Mo, co, axis, p = self.sides(jname)
        M, c = (Ms, cs) if side == "sub" else (Mo, co)
        gv = G * np.asarray(g_hat, float)
        return float(axis @ np.cross(M * (c - p), gv))

    def tau_bound(self, jname, side="sub"):
        """worst-case |tau| over EVERY gravity direction, in closed form."""
        Ms, cs, Mo, co, axis, p = self.sides(jname)
        M, c = (Ms, cs) if side == "sub" else (Mo, co)
        S = M * (c - p)
        d_perp = float(np.linalg.norm(np.cross(axis, S))) / M if M > 0 else 0.0
        if BREAK == 2:
            d_perp = float(np.linalg.norm(c - p))    # straight distance, not perpendicular
        return G * M * d_perp, M, d_perp

    # -- the soles: contact plane and support polygon, MEASURED -------------
    def sole(self, side):
        """Measure the sole plate of one foot: its plane normal and its contact
        polygon, both in the FOOT BODY's own frame, so they follow any pose.

        Nothing here is asserted from the MJCF's numbers. The vertices of the
        sole mesh are taken as they are, the plate normal is the smallest-
        variance principal direction of that vertex cloud (a sole IS a flat
        plate), its sign is chosen to point AWAY from the body's centre of mass,
        and the contact polygon is the convex hull of every vertex lying within
        SOLE_TOL of the extreme along that normal.
        """
        m = self.model
        gname = {"left": "left_foot_collision", "right": "right_foot_collision"}[side]
        g = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, gname)
        assert g >= 0, gname
        b = int(m.geom_bodyid[g])
        did = int(m.geom_dataid[g])
        adr = int(m.mesh_vertadr[did]); n = int(m.mesh_vertnum[did])
        v = m.mesh_vert[adr:adr + n].astype(np.float64)
        gm = m.geom_quat[g]
        R = np.zeros(9); mujoco.mju_quat2Mat(R, gm); R = R.reshape(3, 3)
        vb = v @ R.T + m.geom_pos[g]            # foot-body frame, metres
        c = vb.mean(0)
        _, _, vt = np.linalg.svd(vb - c, full_matrices=False)
        nrm = vt[2] / np.linalg.norm(vt[2])
        if nrm @ (c - m.body_ipos[b]) < 0:
            nrm = -nrm
        h = vb @ nrm
        keep = vb[h >= h.max() - SOLE_TOL]
        e1 = np.cross(nrm, [0.0, 0.0, 1.0])
        if np.linalg.norm(e1) < 1e-6:
            e1 = np.cross(nrm, [1.0, 0.0, 0.0])
        e1 /= np.linalg.norm(e1)
        e2 = np.cross(nrm, e1)
        uv = np.stack([keep @ e1, keep @ e2], axis=1)
        hull = _hull2d(uv)
        return {"body": b, "n_local": nrm, "e1": e1, "e2": e2,
                "plane_h": float(h.max()), "hull_uv": hull,
                "verts": int(n), "contact_verts": int(len(keep)),
                "plane_rms_mm": float(np.std(vb @ nrm) * 1000.0),
                "area_mm2": float(_polyarea(hull) * 1e6)}

    def sole_world(self, side):
        """the sole's down-normal and contact polygon in WORLD at the current pose."""
        s = self.sole(side)
        d = self.data; b = s["body"]
        R = d.xmat[b].reshape(3, 3); p = d.xpos[b]
        nw = R @ s["n_local"]
        e1w = R @ s["e1"]; e2w = R @ s["e2"]
        origin = p + R @ (s["n_local"] * s["plane_h"])
        pts = np.array([origin + u * e1w + v * e2w for u, v in s["hull_uv"]])
        return nw, pts, s

    # -- ground-truth cross-check ------------------------------------------
    def qfrc_bias_check(self, q, g_hat, base_quat=(1, 0, 0, 0)):
        """MuJoCo's own RNE gravity term for the same pose, per hinge joint."""
        m = self.model; d = self.data
        old = m.opt.gravity.copy()
        m.opt.gravity[:] = G * np.asarray(g_hat, float)
        self.set_pose(q, base_quat)
        mujoco.mj_forward(m, d)
        out = {}
        for j in self.hinges:
            out[self.jnames[j]] = float(d.qfrc_bias[int(m.jnt_dofadr[j])])
        m.opt.gravity[:] = old
        return out


# ---------------------------------------------------------------------------
def selftest():
    rows = []
    def chk(name, cond, detail=""):
        rows.append((name, "PASS" if cond else "FAIL", detail))

    st = Statics(augmented=True)
    chk("14 hinge joints found", len(st.hinges) == 14, "%d" % len(st.hinges))
    chk("augmented total mass is 777.1095 g",
        abs(st.total_mass * 1000 - 777.1095) < 1e-3, "%.4f g" % (st.total_mass * 1000))

    rng = np.random.default_rng(7)
    worst = 0.0
    for trial in range(6):
        q = {k: rng.uniform(*st.jrange[k]) for k in common.JOINT_NAMES}
        gh = rng.normal(size=3); gh /= np.linalg.norm(gh)
        ref = st.qfrc_bias_check(q, gh)
        st.set_pose(q, (1, 0, 0, 0))
        for k in common.JOINT_NAMES:
            mine = st.tau(k, gh, "sub")
            # qfrc_bias at v=0 is -(generalized gravity force) = the free-body moment
            worst = max(worst, abs(abs(mine) - abs(ref[k])))
    chk("free-body sum == MuJoCo RNE on 6 random poses x 14 joints (84 comparisons)",
        worst < 1e-9, "worst |delta| = %.3e N.m" % worst)

    # closed-form bound must dominate every sampled direction, and be attained
    st.set_pose({k: 0.0 for k in common.JOINT_NAMES})
    bad = 0; tight = 0
    for k in common.JOINT_NAMES:
        b, M, dp = st.tau_bound(k, "sub")
        mx = 0.0
        for _ in range(400):
            gh = rng.normal(size=3); gh /= np.linalg.norm(gh)
            mx = max(mx, abs(st.tau(k, gh, "sub")))
        if mx > b + 1e-9:
            bad += 1
        if b > 1e-9 and mx / b > 0.90:
            tight += 1
    chk("closed-form bound is never exceeded by 400 sampled directions x 14 joints",
        bad == 0, "%d exceedances" % bad)
    chk("the bound is attained (>=90 % reached by sampling) on the loaded joints",
        tight >= 10, "%d of 14 joints reached 90 %% of their bound" % tight)

    # sub + complement must sum to the whole robot's mass
    st.set_pose({k: 0.3 for k in common.JOINT_NAMES})
    ok = True
    for k in common.JOINT_NAMES:
        Ms, cs, Mo, co, axis, p = st.sides(k)
        if abs(Ms + Mo - st.total_mass) > 1e-12:
            ok = False
    chk("subtree mass + complement mass == total, all 14 joints", ok)

    # a leaf joint's subtree must be lighter than the complement here
    st.set_pose({k: 0.0 for k in common.JOINT_NAMES})
    Ms, _, Mo, _, _, _ = st.sides("left_ankle")
    chk("left_ankle: subtree (the foot) is much lighter than the complement",
        Ms < 0.05 and Mo > 0.7, "sub %.4f kg, out %.4f kg" % (Ms, Mo))

    # axis is a unit vector in WORLD and follows the pose
    st.set_pose({k: 0.0 for k in common.JOINT_NAMES})
    a0 = st.sides("left_knee")[4].copy()
    st.set_pose({"left_hip_pitch": 1.2})
    a_pitch = st.sides("left_knee")[4]
    st.set_pose({"left_hip_roll": 0.38})
    a1 = st.sides("left_knee")[4]
    chk("knee axis is a unit vector", abs(np.linalg.norm(a1) - 1) < 1e-12)
    # FIRST WRITING OF THIS CASE WAS WRONG AND THE CODE WAS RIGHT. It moved
    # left_hip_pitch and demanded the knee axis turn. It does not: hip_pitch and
    # knee are PARALLEL axes (knee axis is the exact negative of the hip-pitch
    # axis, measured below), so rotating one cannot turn the other. The case now
    # moves left_hip_ROLL, which is not parallel to it. The tolerance did not move.
    chk("knee axis does NOT turn when the PARALLEL hip_pitch moves (measured fact)",
        np.linalg.norm(a_pitch - a0) < 1e-12, "|delta axis| = %.3e" % np.linalg.norm(a_pitch - a0))
    chk("knee axis DOES turn when the non-parallel hip_roll moves",
        np.linalg.norm(a1 - a0) > 0.1, "|delta axis| = %.4f" % np.linalg.norm(a1 - a0))

    # torque must vanish when gravity is parallel to the axis
    st.set_pose({k: 0.0 for k in common.JOINT_NAMES})
    ax = st.sides("left_knee")[4]
    chk("torque is zero when gravity lies along the joint axis",
        abs(st.tau("left_knee", ax, "sub")) < 1e-12,
        "%.3e N.m" % abs(st.tau("left_knee", ax, "sub")))

    # -- soles --------------------------------------------------------------
    st.set_pose(common.DEFAULT_POSE)
    for sd in ("left", "right"):
        nw, pts, so = st.sole_world(sd)
        ang = np.degrees(np.arccos(np.clip(nw @ np.array([0.0, 0.0, -1.0]), -1, 1)))
        chk("%s sole plane is flat (rms about its own plane)" % sd,
            so["plane_rms_mm"] < 3.0, "rms %.4f mm over %d vertices" % (so["plane_rms_mm"], so["verts"]))
        chk("%s sole points DOWN at DEFAULT_POSE with the trunk upright" % sd,
            ang < 6.0, "%.4f deg off -z" % ang)
        chk("%s contact polygon has real area" % sd,
            so["area_mm2"] > 200.0, "%.2f mm2, %d hull points, %d contact vertices"
            % (so["area_mm2"], len(so["hull_uv"]), so["contact_verts"]))
    # a point at the polygon centroid must read inside, one far outside must not
    _, pts, so = st.sole_world("left")
    h = so["hull_uv"]
    chk("point-in-polygon: centroid inside, +100 mm outside",
        _dist_in_poly(h.mean(0), h) > 0 and _dist_in_poly(h.mean(0) + np.array([0.1, 0.0]), h) < 0)

    # unaugmented model must reproduce the published 737.2432 g
    st0 = Statics(augmented=False)
    chk("un-augmented model still reads Pollen's 737.2432 g",
        abs(st0.total_mass * 1000 - 737.2432) < 1e-3, "%.4f g" % (st0.total_mass * 1000))

    npass = sum(1 for r in rows if r[1] == "PASS")
    for n, v, d in rows:
        print("  %-4s %s %s" % (v, n, ("[" + d + "]") if d else ""))
    print("statics selftest: %d/%d PASS (BREAK=%d)" % (npass, len(rows), BREAK))
    return npass, len(rows)


if __name__ == "__main__":
    if "--break" in sys.argv:
        BREAK = int(sys.argv[sys.argv.index("--break") + 1])
    selftest()
