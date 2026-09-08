"""wire_travel — DOES EACH CABLE STILL REACH WHEN THE JOINT MOVES?

    ce-cad/bin/cad sim/wire_travel.py

Nothing in this repo had ever asked that. wiring/cables.json orders a length
from a POSE-INVARIANT floor (a polyline bent through each hinge ORIGIN, which
by construction is the same length in every pose) plus a slack term. out/wiring/
cables3d.json routes a 3D path AT ONE POSE (all joints zero) and grades pierce,
clearance and bend. Neither one moves anything. A cable that clears everything
at zero and is torn out of its socket at full knee flexion passes both.

WHAT IS MEASURED HERE
  1. THE KINEMATIC CHAIN, read off the model and not off the cable record.
     For each run, the hinge joints on the tree path between the body carrying
     end A and the body carrying end B, from sim/microduck_ours.xml through
     MuJoCo. Where that disagrees with cables.json's own `crosses` list, the
     disagreement is REPORTED, not reconciled.
  2. REACH. Both connector points are fixed in their own body's frame (their
     world positions in wiring/cables.json are the zero pose, so the local
     point is inv(T_body(0)) applied to it). Sweep every crossed joint across
     its FULL published range and measure the straight-line separation. A
     cable shorter than max-over-poses of that separation cannot exist: no
     routing, no service loop and no cleverness makes a straight line longer.
     That is a NECESSARY condition and the only one a straight line can give.
  3. THE ROUTE, CARRIED. Each vertex of the routed centreline is attributed to
     the body whose surface is nearest it at zero pose (from the occupancy's
     owner field), the attribution is forced MONOTONE along the kinematic chain
     from A to B (a cable cannot hop back and forth between two bodies), and
     then the whole polyline is carried by its bodies through the same sweep.
     Its length at each pose is a much better estimate of what the cable must
     be than the straight line -- and unlike the straight line it is an
     ESTIMATE, because the carried polyline may drive into a body. Reported as
     an estimate and labelled one; the pinch pass is what checks it.

VERDICT RULE
  needed_mm = max(  max-over-poses straight separation ,
                    the routed length at zero pose )
  Both terms are lower bounds on the length a real cable must have -- it has to
  span the worst pose, and it has to follow a path that does not pass through
  material at rest. FAIL if the ordered cable_mm is under needed_mm. PASS is
  reach only, and says so: no published service-loop rule exists in this repo,
  so a margin is reported as a number and never converted into a pass.
"""
import json, math, os, sys

import numpy as np
import mujoco

R = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck"
XML = R + "/sim/microduck_ours.xml"
OUT = R + "/out/wiring/travel.json"
OCC = "/private/tmp/int-wire3d/occ.npz"
LABELS = "/private/tmp/int-wire3d/labels.json"

LEVELS = {1: 181, 2: 61, 3: 25, 4: 15}     # sweep levels per crossed joint


def load_paths():
    out, prov = {}, {}
    for name in ("paths.json", "paths-hat.json"):
        p = os.path.join(R, "out/wiring", name)
        if os.path.exists(p):
            for k, v in json.load(open(p))["record"]["paths"].items():
                out[k], prov[k] = v, name
    return out, prov


def load_c3():
    prev = {}
    for name in ("cables3d.json", "cables3d-hat.json"):
        p = os.path.join(R, "out/wiring", name)
        if os.path.exists(p):
            for c in json.load(open(p))["record"]["cables"]:
                if c.get("routed"):
                    prev[c["id"]] = c
    return prev


class Kin:
    def __init__(self):
        self.m = mujoco.MjModel.from_xml_path(XML)
        self.d = mujoco.MjData(self.m)
        self.body = {}
        for i in range(self.m.nbody):
            self.body[mujoco.mj_id2name(self.m, mujoco.mjtObj.mjOBJ_BODY, i)] = i
        self.parent = {i: int(self.m.body_parentid[i]) for i in range(self.m.nbody)}
        # hinge joint -> (body it moves, qpos address, range)
        self.jnt = {}
        for j in range(self.m.njnt):
            if self.m.jnt_type[j] != mujoco.mjtJoint.mjJNT_HINGE:
                continue
            nm = mujoco.mj_id2name(self.m, mujoco.mjtObj.mjOBJ_JOINT, j)
            self.jnt[nm] = {"body": int(self.m.jnt_bodyid[j]),
                            "qadr": int(self.m.jnt_qposadr[j]),
                            "range": (float(self.m.jnt_range[j][0]), float(self.m.jnt_range[j][1]))}
        self.bybody = {}
        for nm, v in self.jnt.items():
            self.bybody.setdefault(v["body"], []).append(nm)
        self.fk({})
        self.T0 = self.transforms()

    def fk(self, q):
        self.d.qpos[:] = self.m.qpos0
        for nm, v in q.items():
            self.d.qpos[self.jnt[nm]["qadr"]] = v
        mujoco.mj_kinematics(self.m, self.d)

    def transforms(self):
        T = np.zeros((self.m.nbody, 4, 4))
        T[:, 3, 3] = 1.0
        T[:, :3, :3] = self.d.xmat.reshape(-1, 3, 3)
        T[:, :3, 3] = self.d.xpos * 1000.0          # metres -> mm
        return T

    def chain(self, a, b):
        """hinge joints on the tree path from body a to body b (names)."""
        pa, i = [], self.body[a]
        while i != 0:
            pa.append(i)
            i = self.parent[i]
        pa.append(0)
        pb, i = [], self.body[b]
        while i != 0:
            pb.append(i)
            i = self.parent[i]
        pb.append(0)
        sa, sb = set(pa), set(pb)
        anc = next(x for x in pa if x in sb)
        js = []
        for chainside in (pa, pb):
            for i in chainside:
                if i == anc:
                    break
                js += self.bybody.get(i, [])
        return js


def to_local(T0, bid, world_pt):
    Ti = np.linalg.inv(T0[bid])
    p = np.array([world_pt[0], world_pt[1], world_pt[2], 1.0])
    return (Ti @ p)[:3]


def sweep_grid(k, ranges):
    n = LEVELS.get(k, 9)
    axes = [np.linspace(lo, hi, n) for lo, hi in ranges]
    return np.array(np.meshgrid(*axes, indexing="ij")).reshape(k, -1).T


def attribute(poly, owner_body_at):
    """body per polyline vertex, from the occupancy's nearest-owner field."""
    return [owner_body_at(p) for p in poly]


def monotone(bodies, chainA, chainB):
    """force the owner sequence to walk the kinematic chain A -> B once.

    order = the body order along the tree path from A to B. Any vertex whose
    nearest body is not on that path, or that would go backwards, is dragged
    forward to the last legal owner. The transition points are then the only
    free parameter and they are set where the raw attribution first says so.
    """
    order = chainA + chainB
    idx = {b: i for i, b in enumerate(order)}
    cur, out = 0, []
    for b in bodies:
        j = idx.get(b)
        if j is not None and j >= cur:
            cur = j
        out.append(order[cur])
    return out


def main():
    K = Kin()
    cab = json.load(open(R + "/wiring/cables.json"))["record"]
    devices, cables = cab["devices"], cab["cables"]
    paths, prov = load_paths()
    c3 = load_c3()

    # ---- nearest-owner field, for attributing a routed vertex to a body -----
    owner_body_at = None
    attribution_note = "not available"
    if os.path.exists(OCC):
        z = np.load(OCC)
        grid, own, lo, cell = z["grid"], z["owner"], z["lo"], float(z["cell"][0])
        labels = json.load(open(LABELS))
        rows = json.load(open(R + "/ce-assemblies/microduck/current/placements.json"))["record"]["rows"]
        from scipy import ndimage
        CACHE = "/private/tmp/int-wire2/nearowner.npz"
        if os.path.exists(CACHE):
            _z = np.load(CACHE)
            near_row, near_row2c = _z["a"], _z["b"]
        else:
            near_row = near_row2c = None
        if near_row is None:
            _, ind = ndimage.distance_transform_edt(~grid.astype(bool), return_indices=True)
            near_row = own[ind[0], ind[1], ind[2]]      # row index + 1 of the nearest solid
        row_body = {}
        for i, r in enumerate(rows):
            row_body[i + 1] = r.get("body")
        # a fastener row carries body "fastener": give it the body of the nearest
        # NON-fastener solid to its own centre, measured, and count how many.
        fast = [i + 1 for i, r in enumerate(rows) if (r.get("body") or "") == "fastener"]
        shape = np.array(grid.shape)

        def cell_of(p):
            c = np.floor((np.asarray(p, float) - lo) / cell).astype(int)
            return np.clip(c, 0, shape - 1)

        def raw_body(p):
            c = cell_of(p)
            return row_body.get(int(near_row[c[0], c[1], c[2]]))

        fastener_fixed = 0
        if fast:
            solid_only = grid.astype(bool).copy()
            for i, r in enumerate(rows):
                pass
            # cells owned by a fastener row are removed, so the second field
            # answers with a real body and never with "fastener"
            mask = np.isin(own, np.array(fast, dtype=own.dtype))
            if near_row2c is None:
                solid2 = solid_only & (~mask)
                _, ind2 = ndimage.distance_transform_edt(~solid2, return_indices=True)
                near_row2 = own[ind2[0], ind2[1], ind2[2]]
                os.makedirs("/private/tmp/int-wire2", exist_ok=True)
                np.savez_compressed(CACHE, a=near_row, b=near_row2)
            else:
                near_row2 = near_row2c

            def raw_body(p, _n2=near_row2):                      # noqa: F811
                c = cell_of(p)
                b = row_body.get(int(near_row[c[0], c[1], c[2]]))
                if b == "fastener":
                    return row_body.get(int(_n2[c[0], c[1], c[2]]))
                return b
            fastener_fixed = int(mask.sum())
        owner_body_at = raw_body
        attribution_note = ("nearest-solid owner from the 1.0000 mm occupancy "
                            "(/private/tmp/int-wire3d/occ.npz, route3d_grid.py), with a "
                            "second field that excludes the %d cells owned by the 64 "
                            "fastener rows so a vertex never attributes to \"fastener\"" % fastener_fixed)

    rows_out, disagree = [], 0
    for c in cables:
        rid = c["id"]
        a, b = c["from"], c["to"]
        da, db = devices.get(a), devices.get(b)
        rec = {"id": rid, "group": c["group"], "from": a, "to": b,
               "cable_mm_ordered": c.get("cable_mm"),
               "floor_mm_cables_json": c.get("floor_mm"),
               "slack_mm_cables_json": c.get("slack_mm")}
        if not da or not db or not da.get("body") or not db.get("body"):
            rec.update(verdict="CANNOT DETERMINE",
                       verdict_why="an end has no body in wiring/cables.json (%s / %s), so "
                                   "there is nothing to carry it with" % (da and da.get("body"),
                                                                          db and db.get("body")))
            rows_out.append(rec)
            continue
        ba, bb = da["body"], db["body"]
        js = K.chain(ba, bb)
        stated = list(c.get("crosses") or [])
        rec.update(body_a=ba, body_b=bb, joints_crossed_measured=js,
                   joints_crossed_stated=stated)
        if sorted(js) != sorted(stated):
            disagree += 1
            rec["chain_disagreement"] = ("MEASURED %s vs STATED %s -- reported, not reconciled"
                                         % (sorted(js), sorted(stated)))
        pa = c.get("from_xyz_mm")
        pb = c.get("to_xyz_mm")
        if pa is None or pb is None:
            rec.update(verdict="CANNOT DETERMINE",
                       verdict_why="an end has no world point in wiring/cables.json")
            rows_out.append(rec)
            continue
        la = to_local(K.T0, K.body[ba], pa)
        lb = to_local(K.T0, K.body[bb], pb)
        ia, ib = K.body[ba], K.body[bb]

        # --- reach sweep -----------------------------------------------------
        if not js:
            straight0 = float(np.linalg.norm(np.array(pa) - np.array(pb)))
            rec.update(straight_zero_mm=round(straight0, 4),
                       straight_max_mm=round(straight0, 4),
                       straight_min_mm=round(straight0, 4),
                       straight_max_pose_deg={},
                       poses_swept=1,
                       sweep_note="no hinge lies between these two bodies: the separation "
                                  "is the same in every pose, by construction")
        else:
            ranges = [K.jnt[j]["range"] for j in js]
            Q = sweep_grid(len(js), ranges)
            best, worst, bq = -1.0, 1e18, None
            for q in Q:
                K.fk(dict(zip(js, q)))
                Ta = K.T0 * 0
                Ta = np.zeros((4, 4)); Ta[3, 3] = 1
                Ra = K.d.xmat[ia].reshape(3, 3); pa_w = K.d.xpos[ia] * 1000.0
                Rb = K.d.xmat[ib].reshape(3, 3); pb_w = K.d.xpos[ib] * 1000.0
                A = Ra @ la + pa_w
                B = Rb @ lb + pb_w
                dist = float(np.linalg.norm(A - B))
                if dist > best:
                    best, bq = dist, q.copy()
                if dist < worst:
                    worst = dist
            K.fk({})
            straight0 = float(np.linalg.norm(np.array(pa) - np.array(pb)))
            rec.update(straight_zero_mm=round(straight0, 4),
                       straight_max_mm=round(best, 4),
                       straight_min_mm=round(worst, 4),
                       straight_max_pose_deg={j: round(math.degrees(v), 2)
                                              for j, v in zip(js, bq)},
                       poses_swept=int(len(Q)),
                       sweep_note="full factorial over the published range of every crossed "
                                  "hinge, %d levels per joint" % LEVELS.get(len(js), 9))

        # --- the routed polyline, carried through the same sweep -------------
        p3 = c3.get(rid)
        rec["routed"] = bool(p3)
        if p3:
            rec["routed_length_zero_mm"] = p3.get("routed_length_mm")
        carried = None
        if p3 and owner_body_at is not None and rid in paths and js:
            poly = np.asarray(paths[rid]["polyline_mm"], float)
            raw = [owner_body_at(p) for p in poly]
            # chain body order A -> ancestor -> B
            def up(x):
                out, i = [], K.body[x]
                while i != 0:
                    out.append(mujoco.mj_id2name(K.m, mujoco.mjtObj.mjOBJ_BODY, i))
                    i = K.parent[i]
                return out
            ua, ub = up(ba), up(bb)
            common = [x for x in ua if x in set(ub)]
            anc = common[0] if common else ub[-1]
            chainA = ua[:ua.index(anc) + 1]
            chainB = list(reversed(ub[:ub.index(anc)]))
            owners = monotone(raw, chainA, chainB)
            ids = [K.body[o] for o in owners]
            loc = np.array([to_local(K.T0, i, p) for i, p in zip(ids, poly)])
            ranges = [K.jnt[j]["range"] for j in js]
            Q = sweep_grid(len(js), ranges)
            if len(Q) > 4000:
                Q = Q[np.linspace(0, len(Q) - 1, 4000).astype(int)]
            bestL, bq2 = -1.0, None
            for q in Q:
                K.fk(dict(zip(js, q)))
                W = np.empty_like(loc)
                for k, i in enumerate(ids):
                    W[k] = K.d.xmat[i].reshape(3, 3) @ loc[k] + K.d.xpos[i] * 1000.0
                L = float(np.linalg.norm(np.diff(W, axis=0), axis=1).sum())
                if L > bestL:
                    bestL, bq2 = L, q.copy()
            K.fk({})
            W0 = np.empty_like(loc)
            for k, i in enumerate(ids):
                W0[k] = K.d.xmat[i].reshape(3, 3) @ loc[k] + K.d.xpos[i] * 1000.0
            L0 = float(np.linalg.norm(np.diff(W0, axis=0), axis=1).sum())
            from collections import Counter
            carried = {"carried_length_zero_mm": round(L0, 4),
                       "carried_length_max_mm": round(bestL, 4),
                       "carried_max_pose_deg": {j: round(math.degrees(v), 2)
                                                for j, v in zip(js, bq2)},
                       "poses_swept": int(len(Q)),
                       "owners_raw": dict(Counter(raw)),
                       "owners_monotone": dict(Counter(owners)),
                       "is_an_estimate": True,
                       "why_estimate": "the carried polyline may drive into a body; its length "
                                       "is what the cable would be if it stayed glued to those "
                                       "bodies. The pinch pass is what checks whether it can."}
            rec["carried"] = carried

        # --- verdict ---------------------------------------------------------
        need_terms = {"straight_max_mm": rec.get("straight_max_mm"),
                      "routed_length_zero_mm": rec.get("routed_length_zero_mm")}
        vals = [v for v in need_terms.values() if v is not None]
        cm = rec["cable_mm_ordered"]
        if not vals or cm is None:
            rec.update(verdict="CANNOT DETERMINE",
                       verdict_why="no ordered length and/or nothing measured to compare it with")
        else:
            need = max(vals)
            rec["needed_mm_lower_bound"] = round(need, 4)
            rec["needed_from"] = max(need_terms, key=lambda k: (need_terms[k] is not None, need_terms[k] or -1))
            rec["margin_mm"] = round(cm - need, 4)
            rec["margin_pct_of_needed"] = round(100.0 * (cm - need) / need, 2) if need > 0 else None
            if cm < need:
                rec["verdict"] = "FAIL"
                rec["verdict_why"] = ("ordered %.1f mm is SHORTER than the %.4f mm this run "
                                      "provably needs (%s). A cable cannot span a distance "
                                      "longer than itself." % (cm, need, rec["needed_from"]))
            else:
                rec["verdict"] = "PASS (reach only)"
                rec["verdict_why"] = ("ordered %.1f mm exceeds the %.4f mm lower bound by "
                                      "%.4f mm. This is REACH, not fit: no published "
                                      "service-loop rule exists in this repo, and pinch is "
                                      "graded by sim/wire_pinch.py."
                                      % (cm, need, cm - need))
        # --- the carried polyline gets its own verdict, never folded in -----
        cr = rec.get("carried")
        if cr and cm is not None:
            need2 = cr["carried_length_max_mm"]
            cr["margin_mm"] = round(cm - need2, 4)
            if cm < need2:
                cr["verdict"] = "FAIL (estimate)"
                cr["verdict_why"] = ("carried through its own joints' full range the routed "
                                     "centreline grows to %.4f mm, %.4f mm longer than the "
                                     "%.1f mm ordered. This is an ESTIMATE and is reported "
                                     "beside the hard verdict, never merged into it."
                                     % (need2, need2 - cm, cm))
            else:
                cr["verdict"] = "PASS (estimate)"
                cr["verdict_why"] = ("carried to %.4f mm at worst, %.4f mm inside the %.1f mm "
                                     "ordered" % (need2, cm - need2, cm))
        if rec.get("routed_length_zero_mm") is None and rec.get("straight_max_mm") is not None:
            rec["needed_basis_is_weak"] = True
            rec["needed_basis_why"] = ("this run has NO 3D route, so the only lower bound is "
                                       "the straight line between the two connectors. A real "
                                       "cable goes round the bodies, so the true need is "
                                       "higher by an unknown amount and this PASS is the "
                                       "weakest kind there is.")
        rows_out.append(rec)

    counts = {
        "cables_in_cables_json": len(cables),
        "with_both_ends_on_a_body": sum(1 for r in rows_out if r.get("body_a")),
        "crossing_at_least_one_hinge": sum(1 for r in rows_out if r.get("joints_crossed_measured")),
        "chain_disagreements_with_cables_json": disagree,
        "FAIL_reach": sum(1 for r in rows_out if r.get("verdict") == "FAIL"),
        "PASS_reach_only": sum(1 for r in rows_out if r.get("verdict") == "PASS (reach only)"),
        "CANNOT_DETERMINE": sum(1 for r in rows_out if r.get("verdict") == "CANNOT DETERMINE"),
        "carried_polyline_measured": sum(1 for r in rows_out if r.get("carried")),
        "carried_FAIL_estimate": sum(1 for r in rows_out
                                     if (r.get("carried") or {}).get("verdict") == "FAIL (estimate)"),
        "PASS_on_a_straight_line_only": sum(1 for r in rows_out if r.get("needed_basis_is_weak")),
        "poses_evaluated": sum(r.get("poses_swept", 0) for r in rows_out)
                           + sum((r.get("carried") or {}).get("poses_swept", 0) for r in rows_out),
    }
    rec = {"$triad": 1, "kind": "wire-travel", "generated_by": "sim/wire_travel.py",
           "record": {"units": "mm and degrees", "model": "sim/microduck_ours.xml",
                      "method": __doc__.strip(), "attribution": attribution_note,
                      "counts": counts, "runs": rows_out}}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(rec, open(OUT, "w"), indent=1)
    print(json.dumps(counts, indent=1))
    for r in rows_out:
        print("%-22s j=%-2d ord=%-6s s0=%-9s smax=%-9s route0=%-9s need=%-9s margin=%-9s %s" % (
            r["id"], len(r.get("joints_crossed_measured") or []), r.get("cable_mm_ordered"),
            r.get("straight_zero_mm"), r.get("straight_max_mm"), r.get("routed_length_zero_mm"),
            r.get("needed_mm_lower_bound"), r.get("margin_mm"), r.get("verdict")))
    print("wrote", OUT)


main()
