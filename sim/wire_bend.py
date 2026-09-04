"""wire_bend — the bend radius of every routed centreline, measured at the scale
a cable can actually respond to, as a SECOND OPINION on cables3d.json.

    ce-cad/bin/cad sim/wire_bend.py

WHY A SECOND OPINION EXISTS. out/wiring/cables3d.json reports
min_bend_radius_mm from cecad.route.discrete_bend_radius with bend_window_mm
3.0000 -- the circumscribed circle of three samples 1.5 mm apart. That is a
POINT measurement on a curve that came out of a 1.0000 mm voxel plan, so a
single 1 mm stair step reads as a very tight radius whether or not the cable
would feel one. A cable of outside diameter D cannot be bent at a wavelength
shorter than D: the jacket bridges it. So the honest instrument measures
TURNING ANGLE OVER ARC LENGTH at a stated window and reports the window.

METHOD, and it is a bound rather than a fit:
  a cable whose minimum bend radius is R cannot accumulate more than s/R
  radians of turning over an arc length s. So over every window of arc length
  s along the resampled centreline, theta(s) = the total turning angle, and
  R(s) = min over windows of s / theta. That is an UPPER bound on the radius
  the cable achieves at that scale -- the curve turns at least that hard
  somewhere -- and it is immune to a stair step, because a stair step that
  turns +90 then -90 accumulates 180 degrees of |turning| in the sum only if
  you sum |angles|, which is what a cable feels.

  TWO FLAVOURS, AND ONLY ONE OF THEM IS A PROOF:
    NET   theta_net = the angle between the tangent entering the window and the
          tangent leaving it. A cable that must change heading by theta over an
          arc s MUST have bent to at least s/theta somewhere in there, whatever
          shape it actually took. This is a NECESSARY condition and it is the
          one GRADED.
    TOTAL theta_total = the sum of |turn| at every interior vertex in the
          window. This is the curvature of the DRAWN POLYLINE, and the drawn
          polyline came out of a 1.0000 mm voxel plan, so it carries stair-step
          zigzag a real jacket would simply bridge. Reported, never graded --
          it describes our model, not the cable.

THE ONE ABSOLUTE FLOOR, and it needs no vendor. A cable bent to a centreline
radius below OD/2 has its inner surface at a negative radius: the jacket would
have to pass through itself. R >= OD/2 = 1.5622 mm is geometry, not practice,
and a route under it is a FAIL nobody can argue with. Above it and below the
3 x OD target this lane routed to, the verdict stays CANNOT DETERMINE because
ROBOTIS publishes no bend radius for the X3P (route3d.py header).
"""
import json, math, os, sys

import numpy as np

R = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck"
OUT = R + "/out/wiring/bend.json"
RESAMPLE_MM = 0.20      # resampling step; windows are integer multiples of it


def load_paths():
    """paths.json plus paths-hat.json, the later file winning per run id.

    route3d.py writes a re-route of a subset to paths-<tag>.json and does NOT
    rewrite paths.json, so a pass that reads only paths.json measures a route
    that nothing carries. route3d_exact.py records having been bitten by this.
    """
    out, prov = {}, {}
    for name in ("paths.json", "paths-hat.json"):
        p = os.path.join(R, "out/wiring", name)
        if not os.path.exists(p):
            continue
        d = json.load(open(p))["record"]["paths"]
        for k, v in d.items():
            out[k] = v
            prov[k] = name
    return out, prov


def resample(poly, step):
    P = np.asarray(poly, float)
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    keep = seg > 1e-9
    P = np.vstack([P[0], P[1:][keep]])
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    s = np.concatenate([[0.0], np.cumsum(seg)])
    total = float(s[-1])
    n = max(2, int(round(total / step)) + 1)
    t = np.linspace(0.0, total, n)
    out = np.empty((n, 3))
    for k in range(3):
        out[:, k] = np.interp(t, s, P[:, k])
    return out, total


def turning(P):
    """per-vertex turning angle (radians) and the arc length of each segment."""
    d = np.diff(P, axis=0)
    L = np.linalg.norm(d, axis=1)
    u = d / np.maximum(L, 1e-12)[:, None]
    dot = np.clip(np.einsum("ij,ij->i", u[:-1], u[1:]), -1.0, 1.0)
    ang = np.arccos(dot)                       # >= 0, the turn AT each interior vertex
    return ang, L


def unit_tangents(P):
    d = np.diff(P, axis=0)
    L = np.linalg.norm(d, axis=1)
    return d / np.maximum(L, 1e-12)[:, None]


def radius_at_window(P, window_mm, step_mm):
    """(R_net, deg_net, at, R_total, deg_total) over every window of that arc.

    R_net    arc / (angle between the window's entry and exit tangents) -- the
             heading change the cable HAS to make, so a necessary bound.
    R_total  arc / (sum of |turn| inside) -- the drawn polyline's own curvature.
    """
    ang, L = turning(P)
    u = unit_tangents(P)
    if len(ang) == 0:
        return (None,) * 5
    w = max(1, int(round(window_mm / step_mm)))
    if w > len(ang):
        w = len(ang)
    arc = w * step_mm
    c = np.concatenate([[0.0], np.cumsum(ang)])
    tot = c[w:] - c[:-w] if w < len(c) else np.array([c[-1]])
    # net: tangent u[i] entering, u[i+w] leaving
    n = len(u) - w
    if n <= 0 or tot.size == 0:
        return (None,) * 5
    dot = np.clip(np.einsum("ij,ij->i", u[:n], u[w:w + n]), -1.0, 1.0)
    net = np.arccos(dot)
    i = int(np.argmax(net))
    th_net = float(net[i])
    j = int(np.argmax(tot))
    th_tot = float(tot[j])
    at = P[min(i + w // 2, len(P) - 1)]
    R_net = float("inf") if th_net <= 1e-9 else arc / th_net
    R_tot = float("inf") if th_tot <= 1e-9 else arc / th_tot
    return (R_net, math.degrees(th_net), [round(float(x), 4) for x in at],
            R_tot, math.degrees(th_tot))


def main():
    paths, prov = load_paths()
    # SAME TRAP AS THE PATHS: a re-route writes cables3d-<tag>.json and leaves
    # cables3d.json alone, so a comparison that reads only cables3d.json puts
    # the NEW route's radius beside the OLD route's published number. Merge in
    # the same order as the paths, later file winning.
    prev, prev_from = {}, {}
    for name in ("cables3d.json", "cables3d-hat.json"):
        f = os.path.join(R, "out/wiring", name)
        if not os.path.exists(f):
            continue
        for c in json.load(open(f))["record"]["cables"]:
            if c.get("routed"):
                prev[c["id"]] = c
                prev_from[c["id"]] = name
    rows = []
    for rid in sorted(paths):
        rec = paths[rid]
        od = float(rec["od_mm"])
        P, total = resample(rec["polyline_mm"], RESAMPLE_MM)
        windows = {}
        for w in (0.5, 1.0, 2.0, od, 2 * od, 3 * od):
            r, deg, at, rt, degt = radius_at_window(P, w, RESAMPLE_MM)
            fin = lambda x: None if x is None else (None if math.isinf(x) else round(x, 4))
            windows["%.4f" % w] = {"window_mm": round(w, 4),
                                   "R_net_mm": fin(r), "turn_net_deg": (None if deg is None else round(deg, 3)),
                                   "R_total_mm": fin(rt), "turn_total_deg": (None if degt is None else round(degt, 3)),
                                   "at_mm": at}
        head = windows["%.4f" % od]
        floor = od / 2.0
        prevR = prev.get(rid, {}).get("min_bend_radius_mm")
        Rh = head["R_net_mm"]
        Rt = head["R_total_mm"]
        if Rh is None:
            v, why = "CANNOT DETERMINE", "the centreline is too short to hold one %.4f mm window" % od
        elif Rh < floor:
            v = "FAIL"
            why = ("R %.4f mm at the %.4f mm window is below OD/2 = %.4f mm: the inner "
                   "surface of the jacket would have a negative radius, which is "
                   "self-intersection and needs no vendor limit to refuse" % (Rh, od, floor))
        elif Rh < od:
            v = "CANNOT DETERMINE"
            why = ("R %.4f mm is above the absolute floor OD/2 = %.4f mm but BELOW one "
                   "outside diameter (%.4f mm). No published minimum exists for the X3P, so "
                   "this is not graded FAIL -- but no bundle of three 21 AWG wires is "
                   "routinely bent tighter than its own thickness, and this is where a "
                   "measurement on the real cable would settle it" % (Rh, floor, od))
        elif Rh < 3 * od:
            v = "CANNOT DETERMINE"
            why = ("R %.4f mm clears one OD and is under this lane's own 3 x OD target "
                   "(%.4f mm); ROBOTIS publishes no minimum, so there is nothing to "
                   "grade it against" % (Rh, 3 * od))
        else:
            v = "CANNOT DETERMINE"
            why = ("R %.4f mm meets this lane's 3 x OD target (%.4f mm). Still CANNOT "
                   "DETERMINE and not PASS: the target is this lane's rule, not a "
                   "published limit" % (Rh, 3 * od))
        rows.append({
            "id": rid, "path_from": prov[rid], "od_mm": od,
            "length_mm": round(total, 4), "resample_mm": RESAMPLE_MM,
            "R_at_OD_window_mm": Rh, "R_total_at_OD_window_mm": Rt,
            "absolute_floor_mm": round(floor, 4),
            "lane_target_mm": round(3 * od, 4),
            "R_prev_3sample_mm": prevR,
            "R_prev_from": prev_from.get(rid),
            "prev_window_is_3_SAMPLES_not_mm": True,
            "prev_minus_new_mm": (None if (Rh is None or prevR is None) else round(prevR - Rh, 4)),
            "windows": windows, "verdict": v, "verdict_why": why,
        })
    counts = {
        "runs": len(rows),
        "below_absolute_floor": sum(1 for r in rows if r["verdict"] == "FAIL"),
        "below_one_OD": sum(1 for r in rows if r["R_at_OD_window_mm"] is not None
                            and r["R_at_OD_window_mm"] < r["od_mm"]),
        "below_lane_target": sum(1 for r in rows if r["R_at_OD_window_mm"] is not None
                                 and r["R_at_OD_window_mm"] < r["lane_target_mm"]),
        "meets_lane_target": sum(1 for r in rows if r["R_at_OD_window_mm"] is not None
                                 and r["R_at_OD_window_mm"] >= r["lane_target_mm"]),
        "new_tighter_than_3sample": sum(1 for r in rows if r["prev_minus_new_mm"] is not None
                                        and r["prev_minus_new_mm"] > 0),
        "new_looser_than_3sample": sum(1 for r in rows if r["prev_minus_new_mm"] is not None
                                       and r["prev_minus_new_mm"] < 0),
    }
    rec = {"$triad": 1, "kind": "wire-bend", "generated_by": "sim/wire_bend.py",
           "record": {"units": "mm", "method": __doc__.strip(), "counts": counts, "runs": rows}}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(rec, open(OUT, "w"), indent=1)
    print(json.dumps(counts, indent=1))
    for r in rows:
        print("%-22s Rnet(OD)=%-10s Rtot(OD)=%-10s prev3s=%-10s d=%-9s %s" % (
            r["id"], r["R_at_OD_window_mm"], r["R_total_at_OD_window_mm"],
            r["R_prev_3sample_mm"], r["prev_minus_new_mm"], r["verdict"]))
    print("wrote", OUT)


main()
