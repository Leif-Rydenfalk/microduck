"""wire_pinch — IS THE CABLE CRUSHED OR CUT ANYWHERE IN THE JOINT'S TRAVEL?

    ce-cad/bin/cad sim/wire_pinch.py

Every clearance number this repo publishes for the harness was taken at ONE
pose, all joints zero (route3d.py, route3d_exact.py). A harness is not at rest.
This pass carries the routed centreline on the bodies it lies against and moves
the machine.

HOW A SAMPLE IS CARRIED. sim/wire_travel.py's attribution is reused: each
vertex belongs to the body whose surface is nearest it at zero pose (from the
occupancy's owner field, fasteners resolved to their host body), forced monotone
along the kinematic chain between the two connectors. A vertex is then a point
FIXED in that body -- it moves with it, exactly as a cable cable-tied to a
bracket does. That is a model of the harness, and it is the strong version of
the model: a real cable is free to slide and would relieve some of what is
measured here. So an interference found here is a place to look, and a
clearance found here is not a promise.

WHAT IS MEASURED. For every body OTHER than the sample's own, the sample is
mapped into that body's frame and asked how far it is from that body's
material. The body's material is the set of occupied cells the 1.0000 mm
occupancy attributes to it, taken to that body's local frame once, in a cKDTree.
So the distance is a distance to the nearest occupied CELL CENTRE, which
OVERSTATES the true clearance by up to half a cell diagonal, 0.8660 mm --
the same bias route3d_exact.py measured and corrected for the static case, and
it is stated here rather than hidden. Any hit that matters is re-measured
against the actual triangles.

  clearance = distance - OD/2, surface of the bundle to surface of the body.
  FAIL is clearance < 0: that body is inside the cable.

THE STUBS ARE EXCLUDED, for the third time in this lane and for the same
reason: from the connector the centreline runs through the housing by
construction, so those samples are inside a servo case and always "interfere".
"""
import json, math, os, sys
from collections import Counter

import numpy as np
import mujoco
from scipy.spatial import cKDTree

R = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck"
sys.path.insert(0, R + "/sim")
OUT = R + "/out/wiring/pinch.json"
OCC = "/private/tmp/int-wire3d/occ.npz"
XML = R + "/sim/microduck_ours.xml"
OD = 3.1243
FLOOR = 1.0
SAMPLE_MM = 0.5
LEVELS = {1: 61, 2: 21, 3: 11, 4: 7}
CELL_BIAS = 0.8660


def main():
    m = mujoco.MjModel.from_xml_path(XML)
    d = mujoco.MjData(m)
    name = lambda i: mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, i)
    bid = {name(i): i for i in range(m.nbody)}
    parent = {i: int(m.body_parentid[i]) for i in range(m.nbody)}
    jnt, bybody = {}, {}
    for j in range(m.njnt):
        if m.jnt_type[j] != mujoco.mjtJoint.mjJNT_HINGE:
            continue
        nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, j)
        jnt[nm] = {"body": int(m.jnt_bodyid[j]), "qadr": int(m.jnt_qposadr[j]),
                   "range": (float(m.jnt_range[j][0]), float(m.jnt_range[j][1]))}
        bybody.setdefault(int(m.jnt_bodyid[j]), []).append(nm)

    def fk(q):
        d.qpos[:] = m.qpos0
        for k, v in (q or {}).items():
            d.qpos[jnt[k]["qadr"]] = v
        mujoco.mj_kinematics(m, d)

    fk({})
    T0 = np.zeros((m.nbody, 4, 4)); T0[:, 3, 3] = 1
    T0[:, :3, :3] = d.xmat.reshape(-1, 3, 3); T0[:, :3, 3] = d.xpos * 1000.0

    def chain(a, b):
        pa, i = [], bid[a]
        while i != 0: pa.append(i); i = parent[i]
        pa.append(0)
        pb, i = [], bid[b]
        while i != 0: pb.append(i); i = parent[i]
        pb.append(0)
        sb = set(pb)
        anc = next(x for x in pa if x in sb)
        js = []
        for side in (pa, pb):
            for i in side:
                if i == anc: break
                js += bybody.get(i, [])
        return js

    # ---- each body's material, in its OWN frame, as a cKDTree ---------------
    z = np.load(OCC)
    grid, own, lo, cell = z["grid"].astype(bool), z["owner"], z["lo"], float(z["cell"][0])
    rows = json.load(open(R + "/ce-assemblies/microduck/current/placements.json"))["record"]["rows"]
    nz = np.array(np.nonzero(grid)).T
    centres = lo + (nz + 0.5) * cell
    orow = own[nz[:, 0], nz[:, 1], nz[:, 2]]
    row_body = {i + 1: r.get("body") for i, r in enumerate(rows)}
    # a fastener row is given the body of the nearest non-fastener cell centre
    nonf = np.array([row_body.get(int(v)) not in (None, "fastener") for v in orow])
    tre_nonf = cKDTree(centres[nonf])
    body_of = np.empty(len(orow), object)
    for k, v in enumerate(orow):
        b = row_body.get(int(v))
        body_of[k] = b
    fmask = np.array([b == "fastener" or b is None for b in body_of])
    if fmask.any():
        _, ii = tre_nonf.query(centres[fmask], k=1)
        src = np.array(body_of[nonf])[ii]
        body_of[fmask] = src
    trees, counts_body = {}, {}
    for b in sorted({x for x in body_of if x}):
        if b not in bid:
            continue
        sel = np.array([x == b for x in body_of])
        P = centres[sel]
        Ti = np.linalg.inv(T0[bid[b]])
        L = (P @ Ti[:3, :3].T) + Ti[:3, 3]
        trees[b] = cKDTree(L)
        counts_body[b] = int(sel.sum())

    # ---- the routes, attributed --------------------------------------------
    paths = {}
    for nm in ("paths.json", "paths-hat.json"):
        p = os.path.join(R, "out/wiring", nm)
        if os.path.exists(p):
            paths.update(json.load(open(p))["record"]["paths"])
    c3 = {}
    for nm in ("cables3d.json", "cables3d-hat.json"):
        p = os.path.join(R, "out/wiring", nm)
        if os.path.exists(p):
            for c in json.load(open(p))["record"]["cables"]:
                c3[c["id"]] = c
    trav = {r["id"]: r for r in json.load(open(R + "/out/wiring/travel.json"))["record"]["runs"]}
    cab = json.load(open(R + "/wiring/cables.json"))["record"]
    devs, by_id = cab["devices"], {c["id"]: c for c in cab["cables"]}

    # nearest-owner field (cached by sim/wire_travel.py)
    CACHE = "/private/tmp/int-wire2/nearowner.npz"
    zz = np.load(CACHE)
    near_row, near_row2 = zz["a"], zz["b"]
    shape = np.array(grid.shape)

    def owner_body(p):
        c = np.clip(np.floor((np.asarray(p, float) - lo) / cell).astype(int), 0, shape - 1)
        b = row_body.get(int(near_row[c[0], c[1], c[2]]))
        if b == "fastener" or b is None:
            b = row_body.get(int(near_row2[c[0], c[1], c[2]]))
        return b

    def resample(poly, step):
        P = np.asarray(poly, float)
        s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
        n = max(2, int(round(s[-1] / step)) + 1)
        t = np.linspace(0, s[-1], n)
        return np.stack([np.interp(t, s, P[:, k]) for k in range(3)], axis=1), float(s[-1])

    def monotone(bodies, order):
        idx = {b: i for i, b in enumerate(order)}
        cur, out = 0, []
        for b in bodies:
            j = idx.get(b)
            if j is not None and j >= cur:
                cur = j
            out.append(order[cur])
        return out

    def up(x):
        out, i = [], bid[x]
        while i != 0:
            out.append(name(i)); i = parent[i]
        return out

    rows_out = []
    for rid in sorted(paths):
        c = by_id.get(rid) or {}
        da, db = devs.get(c.get("from")), devs.get(c.get("to"))
        if not da or not db or not da.get("body") or not db.get("body"):
            continue
        ba, bb = da["body"], db["body"]
        P, L = resample(paths[rid]["polyline_mm"], SAMPLE_MM)
        sf = float((c3.get(rid) or {}).get("stub_from_mm") or 0.0)
        st = float((c3.get(rid) or {}).get("stub_to_mm") or 0.0)
        arc = np.arange(len(P)) * SAMPLE_MM
        keep = (arc >= sf) & (arc <= L - st)
        if keep.sum() < 3:
            keep = np.ones(len(P), bool)
        P = P[keep]
        ua, ub = up(ba), up(bb)
        anc = next((x for x in ua if x in set(ub)), ub[-1])
        order = ua[:ua.index(anc) + 1] + list(reversed(ub[:ub.index(anc)]))
        raw = [owner_body(p) for p in P]
        owners = monotone(raw, order)
        oids = np.array([bid[o] for o in owners])
        loc = np.empty_like(P)
        for k in range(len(P)):
            Ti = np.linalg.inv(T0[oids[k]])
            loc[k] = Ti[:3, :3] @ P[k] + Ti[:3, 3]

        js = chain(ba, bb)
        if js:
            n = LEVELS.get(len(js), 7)
            axes = [np.linspace(*jnt[j]["range"], n) for j in js]
            Q = np.array(np.meshgrid(*axes, indexing="ij")).reshape(len(js), -1).T
        else:
            Q = np.zeros((1, 0))
        others = [b for b in trees if b not in (None,)]
        best = {"clear": 1e18}
        rest = {"clear": 1e18}
        for qi, q in enumerate(Q if len(Q) else [np.zeros(0)]):
            fk(dict(zip(js, q)) if js else {})
            X = d.xmat.reshape(-1, 3, 3)
            Pw = np.empty_like(loc)
            for k in range(len(loc)):
                i = oids[k]
                Pw[k] = X[i] @ loc[k] + d.xpos[i] * 1000.0
            for b in others:
                ib = bid[b]
                Ti = np.linalg.inv(np.block([[X[ib], (d.xpos[ib] * 1000.0)[:, None]],
                                             [np.zeros((1, 3)), np.ones((1, 1))]]))
                Lp = Pw @ Ti[:3, :3].T + Ti[:3, 3]
                dist, _ = trees[b].query(Lp, k=1)
                mask = np.array([o != b for o in owners])
                dist = np.where(mask, dist, np.inf)
                k = int(np.argmin(dist))
                cl = float(dist[k]) - OD / 2.0
                if cl < best["clear"]:
                    best = {"clear": cl, "body": b, "sample": k, "owner": owners[k],
                            "pose": {jj: round(math.degrees(vv), 2) for jj, vv in zip(js, q)},
                            "at_mm": [round(float(x), 4) for x in Pw[k]],
                            "qi": qi}
                if not js or np.allclose(q, 0.0):
                    if cl < rest["clear"]:
                        rest = {"clear": cl, "body": b, "sample": k, "owner": owners[k]}
        rows_out.append({
            "id": rid, "body_a": ba, "body_b": bb, "joints_crossed": js,
            "poses_swept": int(len(Q)) if js else 1,
            "samples": int(len(P)), "sample_step_mm": SAMPLE_MM,
            "owners": dict(Counter(owners)),
            "min_clearance_over_travel_mm": round(best["clear"], 4),
            "worst_body": best.get("body"), "worst_owner": best.get("owner"),
            "worst_pose_deg": best.get("pose"), "worst_at_mm": best.get("at_mm"),
            "min_clearance_at_rest_mm": (None if rest["clear"] > 1e17 else round(rest["clear"], 4)),
            "clearance_lost_to_travel_mm": (None if rest["clear"] > 1e17 else
                                            round(rest["clear"] - best["clear"], 4)),
            "rest_body": rest.get("body"),
            "grid_bias_mm": CELL_BIAS,
            "verdict": ("FAIL" if best["clear"] < 0 else
                        ("CANNOT DETERMINE" if best["clear"] < CELL_BIAS else "PASS")),
            "verdict_why": (
                "a body other than the one the cable lies on comes %.4f mm INSIDE the bundle "
                "at %s" % (-best["clear"], best.get("pose")) if best["clear"] < 0 else
                ("%.4f mm is inside the %.4f mm the cell-centre distance can overstate by, so "
                 "this cannot be called clear without an exact re-measurement"
                 % (best["clear"], CELL_BIAS) if best["clear"] < CELL_BIAS else
                 "%.4f mm clear of every other body over %d poses, and that is more than the "
                 "%.4f mm the grid can overstate by" % (best["clear"], len(Q) if js else 1, CELL_BIAS))),
        })
        print("%-22s j=%d poses=%-6d rest=%-9s travel=%-9s lost=%-9s %-16s %s" % (
            rid, len(js), len(Q) if js else 1, rows_out[-1]["min_clearance_at_rest_mm"],
            rows_out[-1]["min_clearance_over_travel_mm"], rows_out[-1]["clearance_lost_to_travel_mm"],
            str(best.get("body")), rows_out[-1]["verdict"]))
        sys.stdout.flush()

    counts = {
        "runs": len(rows_out),
        "runs_crossing_a_hinge": sum(1 for r in rows_out if r["joints_crossed"]),
        "poses_evaluated": sum(r["poses_swept"] for r in rows_out),
        "sample_body_queries": sum(r["poses_swept"] * r["samples"] * len(trees) for r in rows_out),
        "bodies_with_material": len(trees),
        "FAIL": sum(1 for r in rows_out if r["verdict"] == "FAIL"),
        "CANNOT_DETERMINE": sum(1 for r in rows_out if r["verdict"] == "CANNOT DETERMINE"),
        "PASS": sum(1 for r in rows_out if r["verdict"] == "PASS"),
        "runs_that_lose_clearance_when_moved": sum(
            1 for r in rows_out if (r["clearance_lost_to_travel_mm"] or 0) > 0),
    }
    rec = {"$triad": 1, "kind": "wire-pinch", "generated_by": "sim/wire_pinch.py",
           "record": {"units": "mm and degrees", "method": __doc__.strip(),
                      "od_mm": OD, "cells_per_body": counts_body,
                      "counts": counts, "runs": rows_out}}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(rec, open(OUT, "w"), indent=1)
    print(json.dumps(counts, indent=1))
    print("wrote", OUT)


main()
