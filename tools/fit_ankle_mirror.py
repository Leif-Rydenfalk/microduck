#!/usr/bin/env python3
"""fit_ankle_mirror.py — is the right ankle a mirror of the left, and if the
model says no, WHICH of the ankle mesh, the foot mesh, the shin servo placement
or the hinge is the odd one out.

    ce-cad/bin/cad tools/fit_ankle_mirror.py   -> out/fit/ankle-mirror.json (+ .log)

THE QUESTION. tools/prove_fit.py sweep found the ankle bracket entering the
shin servo from -0.3 deg on BOTH ankles (leg/xl330 x ankle_left/ankle_left and
leg_2/xl330 x ankle_right/ankle_right, identical 0.716 mm at -5 deg), while
the policies drive the left ankle to +3..+46 deg and the right to -33..-5 deg.
So the right is inside its envelope and the left is not. Either the two sides
are not mirror images, or the sign convention is not what the reader assumes.
This tool measures both, in the one frame everything else is measured in.

THE MEASUREMENTS
  1 rest-pose mirror: every right-leg mesh (ankle bracket, foot, sole, ankle
    bearing, shin, shin servo) against the y-mirror of its left twin, as
    symmetric Hausdorff distance and mean nearest-vertex distance. The servo
    placement is also compared as a frame: R_right against M R_left S, where
    M mirrors world y and S mirrors the servo's own y (the XL330 case is
    symmetric about its width).
  2 hinge mirror: pose left_ankle=+20 with right_ankle=-20 and with
    right_ankle=+20 and see which makes foot_right the mirror of foot_left.
    The same for the knee at +-30. This settles what "the mirrored motion"
    means in joint angles without trusting a sign by eye.
  3 onset table: each ankle driven alone through -30..+30 deg, depth of the
    bracket in the shin servo at every step, with Pollen's mesh and with the
    vendor solid. The two sides are then compared at MIRRORED angles (left
    +t vs right -t), which is the comparison the sweep did not make.
  4 where: at -5 deg each side, the bracket vertices inside the servo,
    expressed in that servo's own frame (horn side +x / idler side -x, and z
    above or below the horn axis), so the entry point can be named.
  5 the policies' own poses: depth at the standing default (+-26 deg) and at
    the sit/stand extremes read from out/motion/legs.json.
"""
import json
import os
import sys
import time

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSHOP = os.path.dirname(os.path.dirname(REPO))
sys.path.insert(0, os.path.join(WORKSHOP, "ce-cad"))
sys.path.insert(0, os.path.join(REPO, "tools"))
OUT = os.path.join(REPO, "out", "fit")
sys.argv = [sys.argv[0], "ankle-mirror"]
import prove_fit as pf                     # noqa: E402
import fit_vendor_servo as fvs             # noqa: E402
from cecad import meshfit as mf            # noqa: E402

P = pf.P
MIRROR = np.diag([1.0, -1.0, 1.0])


def nn(A, B, chunk=400):
    out = np.empty(A.shape[0])
    for s in range(0, A.shape[0], chunk):
        d = ((A[s:s + chunk, None, :] - B[None, :, :]) ** 2).sum(-1)
        out[s:s + chunk] = np.sqrt(d.min(1))
    return out


def hausdorff(A, B):
    a, b = nn(A, B), nn(B, A)
    return float(max(a.max(), b.max())), float((a.mean() + b.mean()) / 2), a, b


def verts(W):
    return np.unique(W.reshape(-1, 3), axis=0)


def row(M, body, mesh):
    r = [i for i in range(M.n) if M.body_of[i] == body and M.rows[i].get("mesh") == mesh]
    assert len(r) == 1, (body, mesh, r)
    return r[0]


def depth_pair(M, W, i, j):
    r = mf.measure_pair(W[i], W[j], volume=False, depth=False)
    if not r.get("interferes"):
        return 0.0, r
    pen = mf.penetration(W[i], W[j])
    return max(pen["a_in_b_mm"], pen["b_in_a_mm"]), r


def main():
    t0 = time.time()
    M = pf.Model()
    res = {"$what": "right ankle vs mirror of the left: meshes, servo placement, hinge sign, onset, entry point"}
    L = {k: row(M, *v) for k, v in {
        "ankle": ("ankle_left", "ankle_left"), "foot": ("ankle_left", "foot_left"),
        "sole": ("ankle_left", "sole_left"), "bearing": ("ankle_left", "seeed_bearing__configuration_default"),
        "shin": ("leg", "leg"), "servo": ("leg", "xl330")}.items()}
    R = {k: row(M, *v) for k, v in {
        "ankle": ("ankle_right", "ankle_right"), "foot": ("ankle_right", "foot_right"),
        "sole": ("ankle_right", "sole_right"), "bearing": ("ankle_right", "seeed_bearing__configuration_default"),
        "shin": ("leg_2", "leg"), "servo": ("leg_2", "xl330")}.items()}

    # ---- 1 rest-pose mirror ---------------------------------------------------
    W0 = M.world(M.zero)
    rest = {}
    P("1 rest-pose mirror (right vs y-mirror of left):")
    for k in L:
        A = verts(W0[L[k]]) @ MIRROR
        B = verts(W0[R[k]])
        h, m, a, b = hausdorff(A, B)
        far = int((a > 0.3).sum() + (b > 0.3).sum())
        rest[k] = {"left": M.label[L[k]], "right": M.label[R[k]], "hausdorff_mm": round(h, 3), "mean_mm": round(m, 4),
                   "vertices_off_by_more_than_0p3": far, "vertices": [int(A.shape[0]), int(B.shape[0])]}
        P("   %-8s hausdorff %6.3f mm  mean %.4f mm  %d of %d+%d vertices off by >0.3 mm"
          % (k, h, m, far, A.shape[0], B.shape[0]))
    # servo placement as a frame
    rl, rr = M.rows[L["servo"]], M.rows[R["servo"]]
    Rl, Rr = pf.quat_R(rl["world_quat_wxyz"]), pf.quat_R(rr["world_quat_wxyz"])
    S = np.diag([1.0, -1.0, 1.0])
    Rm = MIRROR @ Rl @ S
    tm = MIRROR @ np.asarray(rl["world_pos_mm"])
    rest["servo_frame"] = {"R_right": np.round(Rr, 6).tolist(), "M_R_left_S": np.round(Rm, 6).tolist(),
                           "rotation_difference_deg": round(float(np.degrees(np.arccos(min(1.0, (np.trace(Rr.T @ Rm) - 1) / 2)))), 4),
                           "t_right": rr["world_pos_mm"], "M_t_left": tm.tolist(),
                           "translation_difference_mm": round(float(np.linalg.norm(np.asarray(rr["world_pos_mm"]) - tm)), 4),
                           "horn_axis_world_left": np.round(Rl[:, 0], 4).tolist(), "horn_axis_world_right": np.round(Rr[:, 0], 4).tolist()}
    P("   servo frame: R_right vs M.R_left.S differ by %.4f deg, %.4f mm; horn +x world left %s right %s"
      % (rest["servo_frame"]["rotation_difference_deg"], rest["servo_frame"]["translation_difference_mm"],
         rest["servo_frame"]["horn_axis_world_left"], rest["servo_frame"]["horn_axis_world_right"]))
    res["rest_mirror"] = rest

    # ---- 2 hinge mirror ---------------------------------------------------------
    P("2 hinge mirror: which right angle mirrors the left?")
    hinge = {}
    for jl, jr, ang, part in (("left_ankle", "right_ankle", 20.0, "foot"), ("left_knee", "right_knee", 30.0, "foot"),
                              ("left_hip_pitch", "right_hip_pitch", 30.0, "foot")):
        for sgn in (-1.0, 1.0):
            Wp = M.world(M.body_frames(M.qpos_for({jl: ang, jr: sgn * ang})))
            h, m, _, _ = hausdorff(verts(Wp[L[part]]) @ MIRROR, verts(Wp[R[part]]))
            hinge["%s=%+g,%s=%+g" % (jl, ang, jr, sgn * ang)] = {"hausdorff_mm": round(h, 3), "mean_mm": round(m, 4)}
            P("   %s=%+g %s=%+g : %s_right vs mirror(%s_left) hausdorff %.3f mm mean %.4f mm"
              % (jl, ang, jr, sgn * ang, part, part, h, m))
    res["hinge_mirror"] = hinge
    # world hinge axes for the record
    m, d, mj = M.m, M.d, M.mujoco
    d.qpos[:] = M.qpos_for({})
    mj.mj_forward(m, d)
    axes = {}
    for i in range(m.njnt):
        nme = mj.mj_id2name(m, mj.mjtObj.mjOBJ_JOINT, i)
        if nme in ("left_ankle", "right_ankle", "left_knee", "right_knee"):
            b = m.jnt_bodyid[i]
            Rb = np.asarray(d.xmat[b]).reshape(3, 3)
            tb = np.asarray(d.xpos[b]) * 1000.0
            axes[nme] = {"anchor_mm": np.round(Rb @ (np.asarray(m.jnt_pos[i]) * 1000.0) + tb, 3).tolist(),
                         "axis_world": np.round(Rb @ np.asarray(m.jnt_axis[i]), 4).tolist()}
    res["hinge_axes_world"] = axes

    # ---- 3 onset table, Pollen then vendor ---------------------------------------
    angles = [-30, -25, -20, -15, -10, -5, -2, -1, -0.5, 0, 0.5, 1, 2, 5, 10, 15, 20, 25, 30]
    onset = {}
    for servo in ("pollen", "vendor"):
        if servo == "vendor":
            fvs.substitute(M, P)
        P("3 onset table (%s servo): bracket depth in the shin servo, each ankle alone" % servo)
        tab = []
        for a in angles:
            Wl = M.world(M.body_frames(M.qpos_for({"left_ankle": float(a)})))
            dl, _ = depth_pair(M, Wl, L["servo"], L["ankle"])
            Wr = M.world(M.body_frames(M.qpos_for({"right_ankle": float(a)})))
            dr, _ = depth_pair(M, Wr, R["servo"], R["ankle"])
            tab.append({"angle_deg": a, "left_depth_mm": round(dl, 4), "right_depth_mm": round(dr, 4)})
            P("   %+6.1f deg   left %.4f mm   right %.4f mm" % (a, dl, dr))
        # mirrored comparison: left +t vs right -t
        byang = {t["angle_deg"]: t for t in tab}
        mirrored = [{"left_deg": a, "right_deg": -a, "left_depth_mm": byang[a]["left_depth_mm"],
                     "right_depth_mm": byang[-a]["right_depth_mm"]} for a in angles if -a in byang]
        onset[servo] = {"table": tab, "mirrored_pairs": mirrored}
    res["onset"] = onset

    # ---- 4 where does the bracket enter (vendor servo in memory now) ------------
    P("4 entry point at -5 deg, bracket vertices inside the servo, in the servo's own frame:")
    where = {}
    for side, jn, s, b in (("left", "left_ankle", L["servo"], L["ankle"]), ("right", "right_ankle", R["servo"], R["ankle"])):
        Wp = M.world(M.body_frames(M.qpos_for({jn: -5.0})))
        Vb = verts(Wp[b])
        lo, hi = mf.aabb(Wp[s])
        sel = Vb[np.all(Vb >= lo, axis=1) & np.all(Vb <= hi, axis=1)]
        ins = sel[mf.points_inside(Wp[s], sel)] if sel.size else sel
        rr = M.rows[s]
        Rs = pf.quat_R(rr["world_quat_wxyz"])
        ts = np.asarray(rr["world_pos_mm"], float)
        loc = (ins - ts) @ Rs if ins.size else ins
        rad = np.hypot(loc[:, 1], loc[:, 2]) if ins.size else np.zeros(0)
        # cluster by polar angle to count the bosses sitting in the disc's pilot holes
        ang = np.degrees(np.arctan2(loc[:, 2], loc[:, 1])) if ins.size else np.zeros(0)
        clusters = sorted(set(int(round(a / 90.0)) % 4 for a in ang)) if ins.size else []
        where[side] = {"vertices_inside": int(ins.shape[0]),
                       "servo_local_x_range_mm": ([round(float(loc[:, 0].min()), 3), round(float(loc[:, 0].max()), 3)] if ins.size else None),
                       "radius_from_horn_axis_mm": ([round(float(rad.min()), 3), round(float(rad.max()), 3)] if ins.size else None),
                       "polar_clusters_90deg": clusters,
                       "servo_local_bbox_mm": ([np.round(loc.min(0), 2).tolist(), np.round(loc.max(0), 2).tolist()] if ins.size else None),
                       "servo_side": (("horn +x" if loc[:, 0].mean() > 0 else "idler -x") if ins.size else None),
                       "world_bbox_mm": ([np.round(ins.min(0), 2).tolist(), np.round(ins.max(0), 2).tolist()] if ins.size else None)}
        P("   %s: %d bracket vertices inside the servo; servo-local bbox %s -> %s; radius from horn axis %s mm, x %s, %d polar clusters"
          % (side, ins.shape[0], where[side]["servo_local_bbox_mm"], where[side]["servo_side"],
             where[side]["radius_from_horn_axis_mm"], where[side]["servo_local_x_range_mm"], len(clusters)))
    res["entry_at_minus5"] = where

    # ---- 5 the policies' own poses ---------------------------------------------
    P("5 depth at the policies' own ankle poses (vendor servo):")
    legs = json.load(open(os.path.join(REPO, "out/motion/legs.json")))
    poses = {"stand default (policy default_joint_pos)": {"left_ankle": 25.96, "right_ankle": -25.96}}
    for key in ("walking_policy", "sitstand_policy"):
        J = legs[key]["joints"]
        poses[key + " min"] = {"left_ankle": J["left_ankle"]["min_deg"], "right_ankle": J["right_ankle"]["min_deg"]}
        poses[key + " max"] = {"left_ankle": J["left_ankle"]["max_deg"], "right_ankle": J["right_ankle"]["max_deg"]}
    pol = {}
    for name, ang in poses.items():
        Wp = M.world(M.body_frames(M.qpos_for(ang)))
        dl, _ = depth_pair(M, Wp, L["servo"], L["ankle"])
        dr, _ = depth_pair(M, Wp, R["servo"], R["ankle"])
        pol[name] = {"angles_deg": ang, "left_depth_mm": round(dl, 4), "right_depth_mm": round(dr, 4)}
        P("   %-44s L %+7.2f -> %.3f mm   R %+7.2f -> %.3f mm" % (name, ang["left_ankle"], dl, ang["right_ankle"], dr))
    res["policy_poses"] = pol
    res["seconds"] = round(time.time() - t0, 1)
    json.dump(res, open(os.path.join(OUT, "ankle-mirror.json"), "w"), indent=1)
    P("DONE ankle-mirror in %.1f s" % (time.time() - t0))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        P("RAISED:\n" + traceback.format_exc())
        raise
