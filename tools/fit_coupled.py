#!/usr/bin/env python3
"""fit_coupled.py — the recorded trajectories posed JOINTLY, every structure
pair measured at every sampled pose.

    ce-cad/bin/cad tools/fit_coupled.py walk     [every=N] [servo=vendor|pollen] [screws=0|1] [reparent=0|1]
    ce-cad/bin/cad tools/fit_coupled.py sitstand [every=N] [servo=vendor|pollen] [screws=0|1] [reparent=0|1]
        -> out/fit/coupled-<traj>-<servo>[-reparented].json  (+ .log; bin/cad buffers stdout)

reparent=1 moves the two ANKLE servos, in memory, from the shin bodies (leg,
leg_2) where Pollen's MJCF draws them to the ankle bodies (ankle_left,
ankle_right). tools/fit_servo_parenting.py measured (2026-09-09) that the
ankle bracket is a channel holding the servo case at 0.12 mm over 90 deg of
arc along the case's full length, while the shin touches that servo only on
its horn disc: the case is fixed to the bracket and the shin is what the horn
turns. With the geom in the shin, every ankle rotation drives the bracket
into a case that in reality moves with it (the "ankle bracket into shin
servo" sweep finding). With reparent=1 the pair that rotates is shin x servo,
which is the pair the real ankle has. The other 12 hinges are left as the MJCF
has them (the audit found no other holder mismatch it could determine).

TWO PASSES, because one pair test costs 0.05-0.7 s and a frame has ~200
AABB candidates (measured 2026-09-09: 48.8 s per frame with screws, 21 s
without). Pass 1 poses every N-th frame (every=4 by default, 80 ms, stated in
the JSON) and tests every cross-body candidate. Pass 2 then poses EVERY frame
and re-tests only the pairs pass 1 graded — deeper than 0.05 mm at some
sample, or CANNOT DETERMINE — so the worst frame of every finding is exact to
the 20 ms control step while a pair that never came within its decimation
floor is sampled at N. A pair clear at all pass-1 samples and touching only
between two of them would be missed; at the fastest joint (right knee, 731
deg/s in sit/stand) that window is 58 deg, at walking speeds ~26 deg.
screws=0 (default) leaves the 64 fasteners out of the per-frame loop: they
were 110 of 212 candidates and 28 of the 48.8 s, and the single-joint sweep
already covers screw x other-body onsets; the rest census covers them at rest.

WHY. tools/prove_fit.py sweep drives one hinge at a time from the zero pose.
Its knee finding (hip bracket into the foot from 71 deg) and its ankle finding
(ankle bracket into the shin servo from -0.3 deg) are single-joint poses the
gait never reaches as such: in a squat the hip pitch, knee and ankle all move
together. This tool poses what the policies actually drove.

WHAT IS POSED. out/sim/walk_ours_traj.npz and out/sim/sitstand_ours_traj.npz
carry qpos (401 x 21) recorded at 50 Hz from Pollen's BEST_alpha_walking /
BEST_alpha_sitstand policies running in MuJoCo (out/motion/legs.json reads the
same files). Columns 0..6 are the free root; 7..20 are the 14 hinges in the
MJCF's own order. The scene each npz names is compiled here and its joint
names and qpos addresses are asserted identical to the placement MJCF that
prove_fit.Model uses (measured identical 2026-09-09: 15 joints, nq 21). Only
the hinge columns are used, by joint name; the root stays at qpos0 because a
rigid motion of the whole robot cannot change a self-collision, and the local
body frames were built at qpos0 (prove_fit.py, "THE ZERO POSE IS qpos0").

WHAT IS MEASURED. At each sampled frame every row is placed by the compiled
body transforms; pairs whose two rows sit in the SAME body have a constant
relative pose and are not re-tested (their rest result in rest.json /
rest-vendor-servo.json stands); every cross-body pair with overlapping AABBs
is triangle-crossing tested and, if it interferes, penetration depth is
measured (cecad.meshfit.penetration: the deepest vertex of one body inside
the other, a lower bound on relief). Each pair keeps its worst frame: depth,
time, and the full 14-joint vector at that frame. Pairs above 0.3 mm are the
finding; 0.05-0.3 mm is reported, not graded (mesh decimation floor).

GEOMETRY. servo=vendor (default) substitutes the fused ROBOTIS solid for
every xl330 row (tools/fit_vendor_servo.py); servo=pollen keeps the 29 mm
visual mesh so the single-joint sweep numbers can be compared like for like.
yaw_roll_motion always uses the review lane's closed repair
out/review-geometry/microduck-yaw-roll-motion.stl (same part frame, see
tools/fit_yaw_roll_closed.py) so that part can be graded at all. Fasteners are
posed too; a screw against a body it is not driven into is listed separately.
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

TRAJ = {"walk": "out/sim/walk_ours_traj.npz", "sitstand": "out/sim/sitstand_ours_traj.npz"}
YAW_ROLL_FIX = os.path.join(REPO, "out/review-geometry/microduck-yaw-roll-motion.stl")


def parse_args():
    traj = sys.argv[1] if len(sys.argv) > 1 and not "=" in sys.argv[1] else "walk"
    opts = {"every": 4, "servo": "vendor", "frames": None, "screws": 0, "refine": 1, "reparent": 0}
    for a in sys.argv[2:]:
        if "=" in a:
            k, v = a.split("=", 1)
            opts[k] = int(v) if k in ("every", "frames", "screws", "refine", "reparent") else v
    if traj not in TRAJ:
        raise SystemExit("traj must be one of %s" % sorted(TRAJ))
    if opts["servo"] not in ("vendor", "pollen"):
        raise SystemExit("servo must be vendor or pollen")
    return traj, opts


def substitute_row(M, label, stl, P):
    """Same in-memory substitution fit_yaw_roll_closed.py makes."""
    import prove_fit as pf
    from cecad import meshfit as mf
    rows = [i for i in range(M.n) if M.label[i] == label]
    assert len(rows) == 1, (label, rows)
    i = rows[0]
    r = M.rows[i]
    T0 = mf.load_stl_tris(stl)
    assert np.ptp(T0.reshape(-1, 3), axis=0).max() > 1.0, "substitute mesh must be mm"
    R = pf.quat_R(r["world_quat_wxyz"])
    t = np.asarray(r["world_pos_mm"], float)
    W = mf.transform_tris(T0, R, t).reshape(-1, 3, 3)
    R0, t0 = M.zero[M.body_of[i]]
    M.tris[i] = ((W.reshape(-1, 3) - t0) @ R0).reshape(-1, 3, 3)
    M.closed[label] = mf.is_closed(M.tris[i])
    P("substituted %s for %s (closed=%s, %d triangles)" % (os.path.relpath(stl, REPO), label, M.closed[label], T0.shape[0]))
    return i


def reparent_ankle_servos(M, P):
    """Move the ankle servo rows from the shin bodies to the ankle bodies: the
    world pose at the zero pose is unchanged, only the frame the triangles are
    stored in (and therefore which hinge moves them) changes."""
    moved = []
    for old, new in (("leg", "ankle_left"), ("leg_2", "ankle_right")):
        for i in range(M.n):
            if M.body_of[i] == old and M.rows[i].get("mesh") == "xl330":
                R0, t0 = M.zero[old]
                W = M.tris[i].reshape(-1, 3) @ R0.T + t0          # world at zero
                R1, t1 = M.zero[new]
                M.tris[i] = ((W - t1) @ R1).reshape(-1, 3, 3)
                M.body_of[i] = new
                M.label[i] = "%s/xl330(reparented from %s)" % (new, old)
                moved.append({"row": i, "from": old, "to": new, "label": M.label[i]})
                P("reparented row %d xl330 %s -> %s (world pose unchanged)" % (i, old, new))
    assert len(moved) == 2, moved
    return moved


def load_traj(M, traj, P):
    import mujoco
    path = os.path.join(REPO, TRAJ[traj])
    z = np.load(path, allow_pickle=True)
    scene = str(z["scene"])
    ms = mujoco.MjModel.from_xml_path(scene)
    # the recorded scene and the placement model must agree joint for joint
    names_s = [(mujoco.mj_id2name(ms, mujoco.mjtObj.mjOBJ_JOINT, i), int(ms.jnt_qposadr[i]))
               for i in range(ms.njnt) if ms.jnt_type[i] == mujoco.mjtJoint.mjJNT_HINGE]
    names_m = [(j["name"], j["qadr"]) for j in M.joints]
    if names_s != names_m or ms.nq != M.m.nq:
        raise RuntimeError("joint layout differs: scene %s vs model %s" % (names_s, names_m))
    qpos = np.asarray(z["qpos"], float)
    if qpos.shape[1] != M.m.nq:
        raise RuntimeError("qpos has %d columns, model nq %d" % (qpos.shape[1], M.m.nq))
    P("trajectory %s: %d frames at %.3f s, policy %s, scene %s; joint layout identical to the placement model"
      % (os.path.relpath(path, REPO), qpos.shape[0], float(z["ctrl_dt"]), str(z["policy"]), os.path.relpath(scene, REPO)))
    return z, qpos


def main():
    traj, opts = parse_args()
    tag = "coupled-%s-%s%s" % (traj, opts["servo"], "-reparented" if opts["reparent"] else "")
    sys.argv = [sys.argv[0], tag]           # prove_fit names its log after argv[1]
    import prove_fit as pf
    from cecad import meshfit as mf
    P = pf.P
    P("stage:", tag, "opts:", opts)
    t0 = time.time()
    M = pf.Model()
    P("model built in %.1f s: %d rows, %d hinges" % (time.time() - t0, M.n, len(M.joints)))
    subs = {}
    if opts["servo"] == "vendor":
        import fit_vendor_servo as fvs
        rows = fvs.substitute(M, P)
        subs["xl330"] = {"stl": os.path.relpath(fvs.STL, REPO), "rows": rows}
    if os.path.exists(YAW_ROLL_FIX):
        i = substitute_row(M, "yaw_roll_motion/yaw_roll_motion", YAW_ROLL_FIX, P)
        subs["yaw_roll_motion"] = {"stl": os.path.relpath(YAW_ROLL_FIX, REPO), "row": i}
    else:
        P("NOTE: %s missing; yaw_roll_motion stays the open simulator mesh (CANNOT DETERMINE for its pairs)" % YAW_ROLL_FIX)
    if opts["reparent"]:
        subs["reparented"] = reparent_ankle_servos(M, P)
    z, qpos = load_traj(M, traj, P)
    jn = [j["name"] for j in M.joints]
    qadr = [j["qadr"] for j in M.joints]
    nF = qpos.shape[0] if opts["frames"] is None else min(opts["frames"], qpos.shape[0])
    sample = list(range(0, nF, opts["every"]))
    if sample[-1] != nF - 1:
        sample.append(nF - 1)
    P("sampling %d of %d frames (every %d)" % (len(sample), nF, opts["every"]))

    # cross-body pairs only; same-body pairs are constant and stand as in the rest census
    rows_ok = [i for i in range(M.n) if opts["screws"] or M.kind[i] == "structure"]
    cross = [(i, j) for i in rows_ok for j in rows_ok if i < j and M.body_of[i] != M.body_of[j]]
    P("%d cross-body pairs of %d (%s)" % (len(cross), M.n * (M.n - 1) // 2,
                                           "fasteners included" if opts["screws"] else "structure rows only"))
    worst = {}          # (i,j) -> record
    per_frame = []
    tests = 0

    def pose(f):
        angles = {name: float(np.degrees(qpos[f, a])) for name, a in zip(jn, qadr)}
        return angles, M.world(M.body_frames(M.qpos_for(angles)))

    def test(f, angles, W, i, j, r=None):
        nonlocal tests
        tests += 1
        r = mf.measure_pair(W[i], W[j], volume=False, depth=False)
        if not r.get("interferes"):
            return None
        ci, cj = M.closed[M.label[i]], M.closed[M.label[j]]
        if ci and cj:
            pen = mf.penetration(W[i], W[j])
            dep = max(pen["a_in_b_mm"], pen["b_in_a_mm"])
        else:
            pen = {"verdict": "CANNOT DETERMINE", "why": "mesh not closed (a=%s b=%s)" % (ci, cj)}
            dep = None
        k = (i, j)
        prev = worst.get(k)
        if prev is None or (dep is not None and (prev["depth_mm"] is None or dep > prev["depth_mm"])):
            worst[k] = {"a": M.label[i], "b": M.label[j], "class": pf.pair_class(M, i, j),
                        "a_body": M.body_of[i], "b_body": M.body_of[j],
                        "depth_mm": dep, "penetration": pen,
                        "intersecting_tri_pairs": r.get("intersecting_tri_pairs"),
                        "a_vertices_inside_b": r.get("a_vertices_inside_b"),
                        "b_vertices_inside_a": r.get("b_vertices_inside_a"),
                        "frame": int(f), "time_s": round(float(z["time"][f]), 3),
                        "joints_deg": {k_: round(v, 2) for k_, v in angles.items()},
                        "frames_interfering": prev["frames_interfering"] if prev else 0,
                        "frames_tested": prev["frames_tested"] if prev else 0}
        worst[k]["frames_interfering"] += 1
        return dep

    # ---- pass 1: every N-th frame, every candidate pair --------------------------
    for n, f in enumerate(sample):
        angles, W = pose(f)
        lo, hi = pf.boxes(W)
        above = nint = 0
        for (i, j) in cross:
            if not (np.all(hi[i] >= lo[j]) and np.all(hi[j] >= lo[i])):
                continue
            dep = test(f, angles, W, i, j)
            if dep is None and (i, j) not in worst:
                continue
            nint += 1
            worst[(i, j)]["frames_tested"] += 1
            if dep is not None and dep > 0.3:
                above += 1
        per_frame.append({"frame": int(f), "time_s": round(float(z["time"][f]), 3), "pass": 1,
                          "interfering_cross_pairs": nint, "above_0p3": above})
        if n % 10 == 0 or n == len(sample) - 1:
            P("  pass 1 frame %3d (t=%.2f s): %d cross pairs interfere, %d above 0.3 mm; %d tests, %.1f s"
              % (f, float(z["time"][f]), nint, above, tests, time.time() - t0))
    # ---- pass 2: every frame, only the graded pairs --------------------------------
    graded = [k for k, h in worst.items() if h["depth_mm"] is None or h["depth_mm"] > 0.05]
    refined_frames = 0
    if opts["refine"] and graded:
        P("pass 2: %d graded pairs at every one of the %d frames" % (len(graded), nF))
        done = set(sample)
        for f in range(nF):
            if f in done:
                continue
            angles, W = pose(f)
            lo, hi = pf.boxes(W)
            above = 0
            for (i, j) in graded:
                worst[(i, j)]["frames_tested"] += 1
                if not (np.all(hi[i] >= lo[j]) and np.all(hi[j] >= lo[i])):
                    continue
                dep = test(f, angles, W, i, j)
                if dep is not None and dep > 0.3:
                    above += 1
            refined_frames += 1
            per_frame.append({"frame": int(f), "time_s": round(float(z["time"][f]), 3), "pass": 2, "above_0p3": above})
            if f % 50 == 0:
                P("  pass 2 frame %3d: %d graded pairs above 0.3 mm; %d tests, %.1f s" % (f, above, tests, time.time() - t0))
        per_frame.sort(key=lambda r: r["frame"])
    hits = sorted(worst.values(), key=lambda h: -(h["depth_mm"] if h["depth_mm"] is not None else -1))
    struct = [h for h in hits if h["class"] == "structure x structure"]
    for h in struct:
        if h["depth_mm"] is None or h["depth_mm"] > 0.05:
            P("  %-44s x %-44s worst %s mm at frame %d (t=%.2f s), interfering in %d/%d frames"
              % (h["a"], h["b"], ("%.3f" % h["depth_mm"]) if h["depth_mm"] is not None else "CANNOT DETERMINE",
                 h["frame"], h["time_s"], h["frames_interfering"], h["frames_tested"]))
    # joint envelope actually posed, for the report
    env = {name: [round(float(np.degrees(qpos[sample, a].min())), 2), round(float(np.degrees(qpos[sample, a].max())), 2)]
           for name, a in zip(jn, qadr)}
    res = {"$what": "every cross-body pair measured at every sampled pose of the recorded %s trajectory, all joints together" % traj,
           "trajectory": TRAJ[traj], "policy": str(z["policy"]), "scene": os.path.relpath(str(z["scene"]), REPO),
           "frames_total": int(qpos.shape[0]), "frames_used": nF, "every": opts["every"], "frames_sampled_pass1": len(sample),
           "pass2_graded_pairs": len(graded), "pass2_frames": refined_frames, "screws_posed": bool(opts["screws"]),
           "ctrl_dt_s": float(z["ctrl_dt"]), "servo": opts["servo"], "substituted": subs,
           "joint_envelope_posed_deg": env, "rows": M.n, "rows_posed": len(rows_ok), "cross_body_pairs": len(cross), "pair_tests": tests,
           "pairs_ever_interfering": len(hits),
           "structure_above_0p3": [h for h in struct if h["depth_mm"] is not None and h["depth_mm"] > 0.3],
           "structure_0p05_to_0p3": [h for h in struct if h["depth_mm"] is not None and 0.05 < h["depth_mm"] <= 0.3],
           "structure_contact_le_0p05": [h for h in struct if h["depth_mm"] is not None and h["depth_mm"] <= 0.05],
           "structure_cannot_determine": [h for h in struct if h["depth_mm"] is None],
           "screw_x_other_body": [h for h in hits if h["class"] == "screw x other body"],
           "screw_x_driven_into": [h for h in hits if h["class"] == "screw x the part it is driven into"],
           "per_frame": per_frame, "seconds": round(time.time() - t0, 1)}
    json.dump(res, open(os.path.join(OUT, tag + ".json"), "w"), indent=1)
    P("DONE %s: %d structure pairs above 0.3 mm, %d in 0.05-0.3, %d contact, %d CANNOT DETERMINE; %d screw x other body; %.1f s"
      % (tag, len(res["structure_above_0p3"]), len(res["structure_0p05_to_0p3"]), len(res["structure_contact_le_0p05"]),
         len(res["structure_cannot_determine"]), len(res["screw_x_other_body"]), time.time() - t0))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        try:
            import prove_fit as pf
            pf.P("RAISED:\n" + traceback.format_exc())
        except Exception:
            pass
        raise
