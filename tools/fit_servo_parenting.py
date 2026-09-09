#!/usr/bin/env python3
"""fit_servo_parenting.py — for every hinge, which neighbouring part HOLDS the
servo case and which part is DRIVEN off its horn/idler discs, and whether the
MJCF body that carries the servo geom is the holder.

    ce-cad/bin/cad tools/fit_servo_parenting.py   -> out/fit/servo-parenting.json (+ .log)
    (also runs under the system python3: it needs only numpy, placements.json,
     out/fit/vendor-xl330-local.stl, out/fit/axis-check.log and
     out/fit/rest-vendor-servo.json)

WHY. The single-joint sweep reports "ankle bracket into the shin servo from
+-0.3 deg" on both ankles. Ray-casting from the ankle axis in the servo's own
frame (2026-09-09) shows the ankle bracket is a channel hugging the case's
short side with 0.12-0.17 mm of clearance over the case's full length and
width, while the shin touches the servo only on the horn disc. A channel that
fits the case that closely is a servo HOLDER: the case is fixed to the
bracket and the shin is what the horn turns. Pollen's MJCF puts that servo's
visual geom under the shin body, so the collision test rotates the bracket
about a case that in reality moves with it. That finding is a parenting
artefact of the collision model, not a design collision, and every other
servo may be parented the same way. This tool measures all fourteen.

HOW. For each hinge the driving servo is the xl330 row whose horn axis is
nearest the hinge axis (rest-vendor-servo.json servo_axis_check, all 0.087
mm). In that servo's own frame (horn +x, width y, height z, horn axis at the
origin) the parts of the hinge's parent body and child body are probed:
  case clearance   rays from the axis outward at x = -8, 0, +8 (inside the
                   case's 23 mm length), phi 0..360 in 2 deg steps: the part's
                   first hit minus the case's own outer radius on the same
                   ray. A part whose minimum clearance is under 0.5 mm over
                   more than 60 deg of arc is holding the case.
  disc contact     part vertices within 0.05 mm of the horn face plane
                   (x = +14.5) or idler face plane (x = -14.5) at r <= 8.1,
                   and part vertices strictly inside the disc slabs.
The verdict per hinge: holder body, driven body, MJCF body of the servo geom,
and consistent / INVERTED. Nothing is changed; placements.json is read only.
"""
import json
import os
import re
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSHOP = os.path.dirname(os.path.dirname(REPO))
OUT = os.path.join(REPO, "out", "fit")
try:
    sys.path.insert(0, os.path.join(WORKSHOP, "ce-cad"))
    from cecad import meshfit as mf
except Exception:
    import importlib.util
    _spec = importlib.util.spec_from_file_location("meshfit", os.path.join(WORKSHOP, "ce-cad/cecad/meshfit.py"))
    mf = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(mf)

LOG = open(os.path.join(OUT, "servo-parenting.log"), "w", buffering=1)


def P(*a):
    LOG.write(" ".join(str(x) for x in a) + "\n")
    print(*a)


def quat_R(q):
    w, x, y, z = q
    n = (w * w + x * x + y * y + z * z) ** 0.5
    w, x, y, z = w / n, x / n, y / n, z / n
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def raycast_min(T, o, d):
    """Moller-Trumbore: smallest positive hit distance along d from o, or inf."""
    v0, v1, v2 = T[:, 0], T[:, 1], T[:, 2]
    e1, e2 = v1 - v0, v2 - v0
    p = np.cross(d, e2)
    det = (e1 * p).sum(1)
    ok = np.abs(det) > 1e-12
    inv = np.where(ok, 1.0 / np.where(ok, det, 1.0), 0.0)
    s = o - v0
    u = (s * p).sum(1) * inv
    q = np.cross(s, e1)
    v = (d * q).sum(1) * inv
    t = (e2 * q).sum(1) * inv
    m = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-9)
    return float(t[m].min()) if m.any() else np.inf


def main():
    rows = json.load(open(os.path.join(REPO, "ce-assemblies/microduck/current/placements.json")))["record"]["rows"]
    T_servo = mf.load_stl_tris(os.path.join(OUT, "vendor-xl330-local.stl"))
    axis_log = open(os.path.join(OUT, "axis-check.log")).read()
    joints = {}
    for m in re.finditer(r"JOINT\s+(\S+)\s+body=(\S+)\s+parent=(\S+)", axis_log):
        joints[m.group(1)] = {"child": m.group(2), "parent": m.group(3)}
    vend = json.load(open(os.path.join(OUT, "rest-vendor-servo.json")))["servo_axis_check"]["vendor"]
    drive = {}
    for a in vend:
        if a["ring_vertices"] and (a["joint"] not in drive or a["horn_axis_off_joint_axis_mm"] < drive[a["joint"]]["horn_axis_off_joint_axis_mm"]):
            drive[a["joint"]] = a
    cache = {}

    def tris(r):
        f = r["mesh_file"]
        if f not in cache:
            T = mf.load_stl_tris(f)
            cache[f] = T * 1000.0 if np.ptp(T.reshape(-1, 3), axis=0).max() < 1.0 else T
        return cache[f]

    def world(r, T):
        return mf.transform_tris(T, quat_R(r["world_quat_wxyz"]), np.asarray(r["world_pos_mm"], float)).reshape(-1, 3, 3)

    phis = np.arange(0.0, 360.0, 2.0)
    xs = (-8.0, 0.0, 8.0)
    # the case's own outer radius per ray, in its own frame (once)
    case_r = np.array([[raycast_min(T_servo, np.array([x, 0.0, 0.0]),
                                    np.array([0.0, np.cos(np.radians(ph)), np.sin(np.radians(ph))]))
                        for ph in phis] for x in xs])
    # a ray from the axis inside the case first hits the case's INNER surface
    # (the vendor solid is hollow); what matters is the outer envelope, so take
    # the LAST hit: cast from far outside inward instead
    case_outer = np.zeros_like(case_r)
    for ix, x in enumerate(xs):
        for ip, ph in enumerate(phis):
            d = np.array([0.0, np.cos(np.radians(ph)), np.sin(np.radians(ph))])
            far = np.array([x, 0.0, 0.0]) + d * 60.0
            t = raycast_min(T_servo, far, -d)
            case_outer[ix, ip] = 60.0 - t if np.isfinite(t) else np.nan
    out = {"$what": "per hinge: which part holds the servo case and which is driven off its discs, vs the MJCF body carrying the servo geom",
           "servo_mesh": "out/fit/vendor-xl330-local.stl", "ray_x_mm": list(xs), "ray_step_deg": 2.0, "hinges": []}
    inverted = 0
    for jn, jb in joints.items():
        srow = rows[drive[jn]["row"]]
        R = quat_R(srow["world_quat_wxyz"])
        t = np.asarray(srow["world_pos_mm"], float)
        rec = {"joint": jn, "servo_row": drive[jn]["row"], "servo_mjcf_body": srow["body"],
               "parent_body": jb["parent"], "child_body": jb["child"], "parts": []}
        for body in (jb["parent"], jb["child"]):
            for i, r in enumerate(rows):
                if r.get("body") != body or not r.get("mesh_file") or i == drive[jn]["row"] or r.get("mesh") == "xl330":
                    continue
                W = world(r, tris(r))
                Lc = ((W.reshape(-1, 3) - t) @ R).reshape(-1, 3, 3)      # into the servo frame
                V = np.unique(Lc.reshape(-1, 3), axis=0)
                # quick reject: nothing within 30 mm of the case
                if np.abs(V[:, 0]).min() > 30 or np.hypot(V[:, 1], V[:, 2]).min() > 30:
                    continue
                clear = np.full(case_outer.shape, np.inf)
                for ix, x in enumerate(xs):
                    for ip, ph in enumerate(phis):
                        d = np.array([0.0, np.cos(np.radians(ph)), np.sin(np.radians(ph))])
                        far = np.array([x, 0.0, 0.0]) + d * 60.0
                        tt = raycast_min(Lc, far, -d)          # part's OUTER-most... no: nearest to the case from outside
                        # we want the part's surface nearest the case along the ray: cast from the case outward
                        o = np.array([x, 0.0, 0.0]) + d * (case_outer[ix, ip] + 1e-3 if np.isfinite(case_outer[ix, ip]) else 0.0)
                        th = raycast_min(Lc, o, d)
                        clear[ix, ip] = th
                fin = np.isfinite(clear)
                hug = fin & (clear < 0.5)
                arc = float(hug.any(axis=0).sum() * 2.0)          # degrees of arc with <0.5 mm at any x
                rr = np.hypot(V[:, 1], V[:, 2])
                horn_face = int(((np.abs(V[:, 0] - 14.5) < 0.05) & (rr <= 8.1)).sum())
                idler_face = int(((np.abs(V[:, 0] + 14.5) < 0.05) & (rr <= 8.1)).sum())
                horn_slab = int(((V[:, 0] > 8.9) & (V[:, 0] < 14.45) & (rr <= 8.1)).sum())
                idler_slab = int(((V[:, 0] < -10.35) & (V[:, 0] > -14.45) & (rr <= 8.1)).sum())
                prec = {"body": body, "mesh": r["mesh"], "min_case_clearance_mm": (round(float(clear[fin].min()), 3) if fin.any() else None),
                        "arc_deg_under_0p5mm": arc,
                        "arc_deg_under_0p5mm_per_x": [float(hug[ix].sum() * 2.0) for ix in range(len(xs))],
                        "vertices_on_horn_face": horn_face, "vertices_on_idler_face": idler_face,
                        "vertices_in_horn_disc_slab": horn_slab, "vertices_in_idler_disc_slab": idler_slab}
                rec["parts"].append(prec)
                P("  %-16s %-14s %-32s clearance min %s mm over %5.0f deg (%s per x)  horn face %4d idler face %4d  in horn slab %4d idler slab %4d"
                  % (jn, body, r["mesh"], prec["min_case_clearance_mm"], arc, prec["arc_deg_under_0p5mm_per_x"], horn_face, idler_face, horn_slab, idler_slab))
        holders = [p for p in rec["parts"] if p["arc_deg_under_0p5mm"] >= 60.0]
        driven = [p for p in rec["parts"] if (p["vertices_on_horn_face"] + p["vertices_on_idler_face"] + p["vertices_in_horn_disc_slab"] + p["vertices_in_idler_disc_slab"]) > 20]
        rec["holder_bodies"] = sorted(set(p["body"] for p in holders))
        rec["driven_bodies"] = sorted(set(p["body"] for p in driven))
        if not holders:
            rec["verdict"] = "CANNOT DETERMINE: no part holds the case within 0.5 mm over 60 deg"
        elif srow["body"] in rec["holder_bodies"] and srow["body"] not in [b for b in rec["driven_bodies"] if b not in rec["holder_bodies"]]:
            rec["verdict"] = "consistent: the MJCF body carrying the servo geom holds the case"
        else:
            rec["verdict"] = "INVERTED: the case is held by %s but the servo geom sits in %s" % (rec["holder_bodies"], srow["body"])
            inverted += 1
        P("%-16s servo geom in %-16s holder %-28s driven %-28s -> %s" % (jn, srow["body"], rec["holder_bodies"], rec["driven_bodies"], rec["verdict"]))
        out["hinges"].append(rec)
    out["inverted"] = inverted
    json.dump(out, open(os.path.join(OUT, "servo-parenting.json"), "w"), indent=1)
    P("DONE: %d of %d hinges have the servo geom parented to a body that does not hold the case" % (inverted, len(joints)))


if __name__ == "__main__":
    main()
