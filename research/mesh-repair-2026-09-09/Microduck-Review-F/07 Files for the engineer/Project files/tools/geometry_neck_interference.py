#!/usr/bin/env python3
"""geometry_neck_interference.py — does the neck-pitch bracket (and its 22x16x4
bearing) physically hit the bottom head shell / jaw / top head shell anywhere in
the head's joint range?  MEASURED on Pollen's own meshes, posed by MuJoCo.

    ce-cad/bin/cad tools/geometry_neck_interference.py      (writes out/open/geometry/neck-interference.json)

Why this exists: out/sim-evidence/gait-robustness.json known_limitations names the
excluded pair jaw_soft <-> neck_pitch: MuJoCo collides CONVEX HULLS, and the
hulls interpenetrate 2.117-4.472 mm in STAND because the bracket sits INSIDE the
concave shell — so the simulation cannot say whether the real parts touch.
Harvest item 38 asks for the solid-solid test. This is it, on the meshes.

Method (no convex hull anywhere):
  * the model is reference/pollen-microduck-rl/scene.xml (Pollen's robot + STAND
    keyframe). The pair's relative pose depends ONLY on head_yaw and head_roll
    (the two joints between body neck_pitch and body jaw_soft); neck_pitch and
    head_pitch move both bodies together. The sweep is therefore the full 2-D
    range of (head_yaw, head_roll) read from the model, on a grid, plus STAND.
  * geometry comes from mjModel.mesh_vert/mesh_face (the vertices MuJoCo itself
    loaded, in the geom frame it reports in data.geom_xpos/xmat) — so the pose
    used here is exactly the pose the simulator uses.
  * for each pose, for each (A geom of body neck_pitch) x (B geom in the head
    set): surface samples of A (vertices + face centroids + edge midpoints) are
    tested against B with a ray-parity point-in-mesh test along +x, +y and +z
    (majority of three, so a single unclosed face cannot flip the answer), and
    the distance from every sample to B's surface is measured exactly against
    B's triangles (point-triangle distance, vectorised). Both directions are run.
  * reported per pose: the minimum clearance (mm) if nothing is inside, or the
    maximum penetration depth (mm) and the number of penetrating samples if
    something is; the worst pose across the sweep; STAND separately.

Verdict: PASS if no pose in the joint range has any penetrating sample;
FAIL with the pose and the depth otherwise. Both are stated against the
1.5 mm rule the head measurements use elsewhere in this repo: a penetration
below the mesh decimation's own error is reported but not graded.
"""
import json
import os
import sys
import datetime

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SCENE = os.path.join(REPO, "reference/pollen-microduck-rl/scene.xml")
OUT = os.path.join(REPO, "out/open/geometry/neck-interference.json")
PNG = os.path.join(REPO, "out/open/geometry/neck-interference.png")

import mujoco  # noqa: E402

A_BODY = "neck_pitch"
B_MESHES = ["bottom_head_shell", "jaw", "top_head_shell"]
YAW_STEP_DEG = float(os.environ.get("NECK_YAW_STEP", "10"))
ROLL_STEP_DEG = float(os.environ.get("NECK_ROLL_STEP", "5"))


def mesh_tris(model, mesh_id):
    va, vn = model.mesh_vertadr[mesh_id], model.mesh_vertnum[mesh_id]
    fa, fn = model.mesh_faceadr[mesh_id], model.mesh_facenum[mesh_id]
    V = np.asarray(model.mesh_vert[va:va + vn], dtype=float) * 1000.0
    F = np.asarray(model.mesh_face[fa:fa + fn], dtype=int)
    return V, F


def surface_samples(V, F):
    P = [V, V[F].mean(axis=1)]
    for a, b in ((0, 1), (1, 2), (2, 0)):
        P.append(0.5 * (V[F[:, a]] + V[F[:, b]]))
    P = np.concatenate(P)
    return np.unique(np.round(P, 4), axis=0)


def point_tri_dist(P, T, chunk=64):
    """min distance from each point in P (N,3) to the triangle soup T (M,3,3). Exact, vectorised (Ericson)."""
    A, B, C = T[:, 0], T[:, 1], T[:, 2]
    ab, ac = B - A, C - A
    out = np.empty(len(P))
    for s in range(0, len(P), chunk):
        p = P[s:s + chunk][:, None, :]                  # (n,1,3)
        ap = p - A[None]                                 # (n,M,3)
        d1 = (ab[None] * ap).sum(-1); d2 = (ac[None] * ap).sum(-1)
        bp = p - B[None]; d3 = (ab[None] * bp).sum(-1); d4 = (ac[None] * bp).sum(-1)
        cp = p - C[None]; d5 = (ab[None] * cp).sum(-1); d6 = (ac[None] * cp).sum(-1)
        vc = d1 * d4 - d3 * d2; vb = d5 * d2 - d1 * d6; va = d3 * d6 - d5 * d4
        denom = 1.0 / np.where((va + vb + vc) == 0, 1e-30, va + vb + vc)
        v = vb * denom; w = vc * denom
        # candidate closest points
        q_face = A[None] + ab[None] * v[..., None] + ac[None] * w[..., None]
        t_ab = np.clip(d1 / np.where((d1 - d3) == 0, 1e-30, d1 - d3), 0, 1)
        q_ab = A[None] + ab[None] * t_ab[..., None]
        t_ac = np.clip(d2 / np.where((d2 - d6) == 0, 1e-30, d2 - d6), 0, 1)
        q_ac = A[None] + ac[None] * t_ac[..., None]
        t_bc = np.clip((d4 - d3) / np.where(((d4 - d3) + (d5 - d6)) == 0, 1e-30, (d4 - d3) + (d5 - d6)), 0, 1)
        q_bc = B[None] + (C - B)[None] * t_bc[..., None]
        inside = (va >= 0) & (vb >= 0) & (vc >= 0)
        q = np.where(inside[..., None], q_face, q_ab)
        d = ((p - q) ** 2).sum(-1)
        for qq in (q_ac, q_bc, A[None] + 0 * ab[None], B[None] + 0 * ab[None], C[None] + 0 * ab[None]):
            dd = ((p - qq) ** 2).sum(-1)
            d = np.minimum(d, dd)
        out[s:s + chunk] = np.sqrt(d.min(axis=1))
    return out


def inside_parity(P, T, axis, chunk=256):
    """ray from each point along +axis; count crossings with triangles (Moller-Trumbore)."""
    d = np.zeros(3); d[axis] = 1.0
    A, B, C = T[:, 0], T[:, 1], T[:, 2]
    e1, e2 = B - A, C - A
    h = np.cross(d, e2)                    # (M,3)
    a = (e1 * h).sum(-1)                   # (M,)
    ok = np.abs(a) > 1e-12
    f = np.where(ok, 1.0 / np.where(ok, a, 1.0), 0.0)
    q_ = np.cross(e1, d)                   # (M,3) — s x e1 needs s; do per chunk
    cnt = np.zeros(len(P), dtype=int)
    for s0 in range(0, len(P), chunk):
        p = P[s0:s0 + chunk]
        s = p[:, None, :] - A[None]        # (n,M,3)
        u = f[None] * (s * h[None]).sum(-1)
        qv = np.cross(s, e1[None])         # (n,M,3)
        v = f[None] * (qv * d).sum(-1)
        t = f[None] * (qv * e2[None]).sum(-1)
        hit = ok[None] & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-9)
        cnt[s0:s0 + chunk] = hit.sum(axis=1)
    return cnt % 2 == 1


def inside_majority(P, T):
    votes = np.zeros(len(P), dtype=int)
    for ax in range(3):
        votes += inside_parity(P, T, ax)
    return votes >= 2


def pair_check(PA, TA, PB, TB, near_mm=3.0):
    """samples of A against triangles of B and vice versa."""
    res = {}
    for name, P, T in (("A_in_B", PA, TB), ("B_in_A", PB, TA)):
        dist = point_tri_dist(P, T)
        near = dist < near_mm
        ins = np.zeros(len(P), dtype=bool)
        if near.any():
            ins[near] = inside_majority(P[near], T)
        res[name] = {"n_samples": int(len(P)), "min_dist_mm": round(float(dist.min()), 4),
                     "n_inside": int(ins.sum()),
                     "max_penetration_mm": round(float(dist[ins].max()), 4) if ins.any() else 0.0,
                     "inside_centroid_mm": [round(float(v), 3) for v in P[ins].mean(axis=0)] if ins.any() else None}
    return res


def main():
    model = mujoco.MjModel.from_xml_path(SCENE)
    data = mujoco.MjData(model)
    key = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, "STAND")
    mujoco.mj_resetDataKeyframe(model, data, key)
    jy = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, "head_yaw")
    jr = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, "head_roll")
    yaw_rng = np.degrees(model.jnt_range[jy]); roll_rng = np.degrees(model.jnt_range[jr])
    qy, qr = model.jnt_qposadr[jy], model.jnt_qposadr[jr]
    stand_yaw, stand_roll = float(np.degrees(data.qpos[qy])), float(np.degrees(data.qpos[qr]))

    bidA = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, A_BODY)
    A_geoms = [g for g in range(model.ngeom) if model.geom_bodyid[g] == bidA and model.geom_type[g] == mujoco.mjtGeom.mjGEOM_MESH]
    B_geoms = []
    for g in range(model.ngeom):
        if model.geom_type[g] != mujoco.mjtGeom.mjGEOM_MESH:
            continue
        mname = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_MESH, model.geom_dataid[g])
        if mname in B_MESHES and model.geom_group[g] != 3 and g not in B_geoms:
            # one geom per mesh (visual and collision share geometry)
            if not any(mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_MESH, model.geom_dataid[x]) == mname for x in B_geoms):
                B_geoms.append(g)
    local = {}
    for g in A_geoms + B_geoms:
        V, F = mesh_tris(model, model.geom_dataid[g])
        local[g] = (V, F, surface_samples(V, F))

    def posed(g):
        V, F, S = local[g]
        Rm = data.geom_xmat[g].reshape(3, 3); p = data.geom_xpos[g] * 1000.0
        Vw = V @ Rm.T + p
        return Vw[F], S @ Rm.T + p

    def gname(g):
        return "%s/%s" % (mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_BODY, model.geom_bodyid[g]),
                          mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_MESH, model.geom_dataid[g]))

    def run_pose(yaw_deg, roll_deg):
        data.qpos[qy] = np.radians(yaw_deg); data.qpos[qr] = np.radians(roll_deg)
        mujoco.mj_kinematics(model, data)
        rows = []
        for ga in A_geoms:
            TA, SA = posed(ga)
            for gb in B_geoms:
                TB, SB = posed(gb)
                # cheap reject: bbox gap
                gap = np.maximum(TA.reshape(-1, 3).min(0) - TB.reshape(-1, 3).max(0), TB.reshape(-1, 3).min(0) - TA.reshape(-1, 3).max(0)).max()
                if gap > 3.0:
                    rows.append({"A": gname(ga), "B": gname(gb), "bbox_gap_mm": round(float(gap), 3), "skipped": True})
                    continue
                r = pair_check(SA, TA, SB, TB)
                r["A"], r["B"] = gname(ga), gname(gb)
                rows.append(r)
        pen = [max(r["A_in_B"]["max_penetration_mm"], r["B_in_A"]["max_penetration_mm"]) for r in rows if not r.get("skipped")]
        nin = [r["A_in_B"]["n_inside"] + r["B_in_A"]["n_inside"] for r in rows if not r.get("skipped")]
        dmin = [min(r["A_in_B"]["min_dist_mm"], r["B_in_A"]["min_dist_mm"]) for r in rows if not r.get("skipped")]
        dmin += [r["bbox_gap_mm"] for r in rows if r.get("skipped")]
        return {"head_yaw_deg": round(yaw_deg, 3), "head_roll_deg": round(roll_deg, 3),
                "min_clearance_mm": round(min(dmin), 4) if dmin else None,
                "max_penetration_mm": round(max(pen), 4) if pen else 0.0,
                "n_penetrating_samples": int(sum(nin)) if nin else 0, "pairs": rows}

    log = open(OUT + ".log", "w")
    stand = run_pose(stand_yaw, stand_roll)
    print("STAND", json.dumps({k: v for k, v in stand.items() if k != "pairs"}), file=log, flush=True)
    yaws = np.arange(yaw_rng[0], yaw_rng[1] + 1e-6, YAW_STEP_DEG)
    if abs(yaws[-1] - yaw_rng[1]) > 1e-6:
        yaws = np.append(yaws, yaw_rng[1])
    rolls = np.arange(roll_rng[0], roll_rng[1] + 1e-6, ROLL_STEP_DEG)
    if abs(rolls[-1] - roll_rng[1]) > 1e-6:
        rolls = np.append(rolls, roll_rng[1])
    sweep = []
    for rl in rolls:
        for yw in yaws:
            r = run_pose(float(yw), float(rl))
            sweep.append({k: v for k, v in r.items() if k != "pairs"} | {"pairs_compact": [
                {"A": p["A"], "B": p["B"], "min_dist": p.get("bbox_gap_mm", None) if p.get("skipped") else min(p["A_in_B"]["min_dist_mm"], p["B_in_A"]["min_dist_mm"]),
                 "pen": 0.0 if p.get("skipped") else max(p["A_in_B"]["max_penetration_mm"], p["B_in_A"]["max_penetration_mm"]),
                 "n_in": 0 if p.get("skipped") else p["A_in_B"]["n_inside"] + p["B_in_A"]["n_inside"]} for p in r["pairs"]]})
            print(json.dumps({k: v for k, v in r.items() if k != "pairs"}), file=log, flush=True)
    worst = max(sweep, key=lambda s: (s["max_penetration_mm"], -s["min_clearance_mm"]))
    tight = min(sweep, key=lambda s: s["min_clearance_mm"])
    any_pen = any(s["n_penetrating_samples"] > 0 for s in sweep) or stand["n_penetrating_samples"] > 0
    rep = {
        "$what": __doc__.strip().splitlines()[0],
        "generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "script": "tools/geometry_neck_interference.py",
        "model": os.path.relpath(SCENE, REPO),
        "A_geoms": [gname(g) for g in A_geoms], "B_geoms": [gname(g) for g in B_geoms],
        "samples_per_geom": {gname(g): int(len(local[g][2])) for g in A_geoms + B_geoms},
        "triangles_per_geom": {gname(g): int(len(local[g][1])) for g in A_geoms + B_geoms},
        "joint_ranges_deg": {"head_yaw": [round(float(v), 3) for v in yaw_rng], "head_roll": [round(float(v), 3) for v in roll_rng]},
        "why_only_yaw_and_roll": "body neck_pitch and body jaw_soft are separated by exactly the joints head_yaw (neck_pitch -> yaw_roll_motion) and head_roll (yaw_roll_motion -> jaw_soft); neck_pitch and head_pitch move both bodies rigidly together, so the pair's relative pose is a function of (head_yaw, head_roll) only.",
        "grid": {"yaw_step_deg": YAW_STEP_DEG, "roll_step_deg": ROLL_STEP_DEG, "n_poses": len(sweep)},
        "stand": stand,
        "sweep": sweep,
        "worst_pose": {k: v for k, v in worst.items() if k != "pairs_compact"},
        "tightest_pose": {k: v for k, v in tight.items() if k != "pairs_compact"},
        "verdict": "FAIL" if any_pen else "PASS",
        "why": ("a penetrating sample exists: %.3f mm at head_yaw %.1f / head_roll %.1f deg" % (worst["max_penetration_mm"], worst["head_yaw_deg"], worst["head_roll_deg"])) if any_pen else
               ("no surface sample of the bracket or its bearing lies inside the bottom shell, jaw or top shell (nor vice versa) at any of %d poses over the full head_yaw x head_roll range; the tightest clearance is %.3f mm at head_yaw %.1f / head_roll %.1f deg; STAND clearance %.3f mm" % (len(sweep), tight["min_clearance_mm"], tight["head_yaw_deg"], tight["head_roll_deg"], stand["min_clearance_mm"])),
        "artifacts": [os.path.relpath(OUT, REPO), os.path.relpath(PNG, REPO)],
    }
    json.dump(rep, open(OUT, "w"), indent=1)
    # picture: clearance map
    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        Z = np.full((len(rolls), len(yaws)), np.nan)
        for s in sweep:
            i = int(np.argmin(np.abs(rolls - s["head_roll_deg"]))); j = int(np.argmin(np.abs(yaws - s["head_yaw_deg"])))
            Z[i, j] = -s["max_penetration_mm"] if s["n_penetrating_samples"] else s["min_clearance_mm"]
        fig, ax = plt.subplots(figsize=(12, 4.5))
        im = ax.imshow(Z, origin="lower", aspect="auto", extent=[yaws[0], yaws[-1], rolls[0], rolls[-1]], cmap="RdYlGn", vmin=-3, vmax=10)
        ax.set_xlabel("head_yaw (deg)"); ax.set_ylabel("head_roll (deg)")
        ax.set_title("neck_pitch bracket + 22x16x4 bearing vs bottom shell / jaw / top shell: clearance (mm, +) or penetration (-)\n%s — %s" % (rep["verdict"], rep["why"][:110]), fontsize=9)
        plt.colorbar(im, ax=ax, label="mm")
        ax.plot([stand_yaw], [stand_roll], "k+", ms=14, mew=2); ax.annotate("STAND %.2f mm" % stand["min_clearance_mm"], (stand_yaw, stand_roll), textcoords="offset points", xytext=(6, 6), fontsize=8)
        fig.tight_layout(); fig.savefig(PNG, dpi=130)
    except Exception as e:  # noqa: BLE001
        rep["plot_error"] = repr(e)
        json.dump(rep, open(OUT, "w"), indent=1)
    print("wrote", OUT, rep["verdict"], rep["why"], file=log, flush=True)
    print(rep["verdict"], rep["why"])


if __name__ == "__main__":
    main()
