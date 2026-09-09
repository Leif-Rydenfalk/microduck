#!/usr/bin/env python3
"""fit_vendor_servo.py — the ROBOTIS XL330 vendor solid in place of Pollen's
29 mm visual servo mesh, substituted IN MEMORY for every xl330 row, and the rest
census rerun. placements.json is not changed.

    ce-cad/bin/cad tools/fit_vendor_servo.py build  -> out/fit/vendor-xl330-local.stl
                                                      out/fit/vendor-servo-frame.json
    ce-cad/bin/cad tools/fit_vendor_servo.py rest   -> out/fit/rest-vendor-servo.json
    (bin/cad buffers stdout: both stages also write out/fit/vendor-servo-<stage>.log)

WHY. Every servo-related finding in out/fit/REST-CENSUS-2026-09-09.md carries
the caveat that penetration was measured against Pollen's visual mesh
(reference/pollen-microduck-rl/assets/xl330.stl, 4126 triangles). The vendor
STEP ce-parts/xl330-m288-t/iterations/v0.0.1/geometry/robotis-xl-xc-330.stp
(sha256 e2f7b060..., research/xl330-geometry-revision-2026-09-08/) is the
manufacturer's own geometry: 15 solids plus 6 open shells. This tool makes the
15 solids one closed triangle set and reruns the census with it.

THE FRAME, and the proof of it. research/xl330-geometry-revision-2026-09-08
records local(X,Y,Z) = (vendorZ + 8, vendorX, vendorY): the xl330 mesh frame
Pollen's MJCF places (horn axis = +x, horn side +x, 20 mm width along y, 34 mm
height along z with the horn axis at z = 0). `build` applies that mapping and
then MEASURES it rather than trusting it: the horn disc (vendor solid 3) and
idler disc (solid 10) are fitted for centre and normal in the local frame and
compared with the Pollen mesh's own discs; in the assembly every servo row's
horn axis is compared with the hinge axis it drives, the same centroid /
axis check tools/fit_axis_check.py does for bearings. A mapping error of one
axis swap or one sign shows up as a disc normal tilted 90 deg or a horn on
the wrong side, and the stage refuses to write the STL.

THE UNION. FreeCAD's multiFuse of the 15 solids returned 6299 mm3 for a
15864 mm3 sum (measured 2026-09-09; the sequential fuse returned 1652 mm3),
so booleans are not trusted blind: the solids are fused one at a time and
after every step the union's volume is checked against
(previous + solid - measured common volume); a step that loses volume is
retried with a fuzzy tolerance and, failing that, the stage stops with the
solid index named. The 6 open shells (four 18.3 mm2, two 54.0 mm2 surfaces)
carry no volume and are excluded; that is stated in the frame JSON.

`rest` reuses prove_fit.Model and prove_fit.main_rest unchanged apart from
the in-memory substitution, so the two census files differ only in the servo
geometry. The comparison table names, for each of the 16 above-0.3 mm rest
pairs in rest.json, the depth with Pollen's mesh, the depth with the vendor
solid, and whether the pair survives. Pair labels stay "xl330" so the rows
line up; `substituted` in the JSON says what geometry the label meant.
"""
import hashlib
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
os.makedirs(OUT, exist_ok=True)

STEP = os.path.join(REPO, "ce-parts/xl330-m288-t/iterations/v0.0.1/geometry/robotis-xl-xc-330.stp")
POLLEN = os.path.join(REPO, "reference/pollen-microduck-rl/assets/xl330.stl")
STL = os.path.join(OUT, "vendor-xl330-local.stl")
FRAME_JSON = os.path.join(OUT, "vendor-servo-frame.json")
DEFLECTION = 0.1      # mm chord error of the tessellation, below the 0.3 mm grading floor
ANGULAR_DEG = 30.0    # angular deflection: keeps the r 0.8 mm screw threads from costing 13k triangles each
HORN_SOLID, IDLER_SOLID = 3, 10   # vendor-geometry.json: r 8 discs at vendor z 0.9..6.5 and -22.5..-18.35


def vendor_to_local(V):
    """local(X,Y,Z) = (vendorZ + 8, vendorX, vendorY) — a cyclic axis
    permutation (det +1) plus 8 mm along the horn axis."""
    V = np.asarray(V, float)
    return np.stack([V[:, 2] + 8.0, V[:, 0], V[:, 1]], axis=1)


def write_stl(path, T):
    n = T.shape[0]
    rec = np.zeros(n, dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))
    nrm = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    nrm /= np.maximum(np.linalg.norm(nrm, axis=1)[:, None], 1e-12)
    rec["n"] = nrm
    rec["v"] = T
    with open(path, "wb") as fh:
        fh.write(b"vendor xl330 fused, LOCAL xl330 frame, mm".ljust(80, b"\0"))
        fh.write(np.asarray([n], dtype="<u4").tobytes())
        fh.write(rec.tobytes())


def mesh_volume(T):
    a, b, c = T[:, 0], T[:, 1], T[:, 2]
    return float(np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6.0)


def disc_fit(V):
    """centre and unit normal of a thin disc's vertex cloud (SVD smallest axis)."""
    c = V.mean(axis=0)
    _, s, vt = np.linalg.svd(V - c, full_matrices=False)
    return c, vt[2], s


def stage_build(P):
    import Part
    from cecad import meshfit as mf
    t0 = time.time()
    shp = Part.read(STEP)
    sol = shp.Solids
    sha = hashlib.sha256(open(STEP, "rb").read()).hexdigest()
    P("STEP %s sha256 %s: %d solids, %d shells, sum of solid volumes %.1f mm3"
      % (os.path.relpath(STEP, REPO), sha[:12], len(sol), len(shp.Shells), sum(s.Volume for s in sol)))

    # -- union, one solid at a time, volume-checked at every step --------------
    def tess(s, tol):
        v, f = s.tessellate(tol)
        V = np.asarray([[p.x, p.y, p.z] for p in v], float)
        return V[np.asarray(f, int)]

    union = sol[0]
    vol = union.Volume
    steps = []
    for i in range(1, len(sol)):
        common = union.common(sol[i]).Volume
        expect = vol + sol[i].Volume - common
        got = union.fuse(sol[i])
        how = "fuse"
        if abs(got.Volume - expect) > 0.5:
            got2 = union.fuse(sol[i], 0.001)
            how = "fuse fuzzy 0.001"
            if abs(got2.Volume - expect) > 0.5:
                raise RuntimeError("fusing vendor solid %d lost volume: expected %.2f, fuse gave %.2f, fuzzy gave %.2f"
                                   % (i, expect, got.Volume, got2.Volume))
            got = got2
        steps.append({"solid": i, "solid_mm3": round(sol[i].Volume, 3), "common_mm3": round(common, 3),
                      "expected_mm3": round(expect, 3), "union_mm3": round(got.Volume, 3), "how": how})
        union, vol = got, got.Volume
        P("  + solid %2d %8.1f mm3, common %6.2f -> union %.1f mm3 (expected %.1f) %s"
          % (i, sol[i].Volume, common, vol, expect, how))
    union = union.removeSplitter()
    P("union: %d solid(s), valid=%s, closed=%s, %.1f mm3 (removeSplitter), %.1f s"
      % (len(union.Solids), union.isValid(), union.isClosed(), union.Volume, time.time() - t0))
    # the union may legitimately be more than one solid (vendor solid 4, a
    # 31.6 mm3 block, shares no volume with anything); disjoint closed shells
    # voxelise correctly by ray parity, OVERLAPPING ones do not, so prove disjoint
    us = union.Solids
    for i in range(len(us)):
        for j in range(i + 1, len(us)):
            cv = us[i].common(us[j]).Volume
            if cv > 0.01:
                raise RuntimeError("union solids %d and %d share %.3f mm3: parity would be wrong there" % (i, j, cv))
    P("union solids pairwise disjoint: %d solid(s), volumes %s" % (len(us), [round(s.Volume, 1) for s in us]))

    # Shape.tessellate(0.1) gave 142004 triangles (measured): linear deflection
    # alone puts ~22 segments on every r 0.8 mm thread. MeshPart with an angular
    # deflection keeps the r 8 discs at 0.1 mm chord error and the small
    # cylinders at 12 segments: 13314 triangles, mesh volume 15687.7 vs 15692.6.
    import math
    import MeshPart
    mesh = MeshPart.meshFromShape(Shape=union, LinearDeflection=DEFLECTION,
                                  AngularDeflection=math.radians(ANGULAR_DEG), Relative=False)
    pts, fac = mesh.Topology
    T_vendor = np.asarray(pts, float)[np.asarray(fac, int)]
    closed = mf.is_closed(T_vendor)
    mvol = mesh_volume(T_vendor)
    P("tessellated at %.2f mm / %.0f deg: %d triangles, closed=%s, mesh volume %.1f mm3 vs BRep %.1f mm3"
      % (DEFLECTION, ANGULAR_DEG, T_vendor.shape[0], closed, mvol, union.Volume))
    if not closed:
        raise RuntimeError("fused vendor mesh is not closed")
    if abs(mvol - union.Volume) > 0.01 * union.Volume:  # coarse chords underestimate cylinders
        raise RuntimeError("mesh volume %.1f differs from BRep %.1f by more than 1%%" % (mvol, union.Volume))

    # -- into the local frame ---------------------------------------------------
    T = vendor_to_local(T_vendor.reshape(-1, 3)).reshape(-1, 3, 3)
    # the mapping is a proper rotation, so orientation is preserved; prove it
    if mesh_volume(T) < 0:
        raise RuntimeError("frame mapping flipped orientation (negative volume)")
    lo, hi = T.reshape(-1, 3).min(axis=0), T.reshape(-1, 3).max(axis=0)
    TP = mf.load_stl_tris(POLLEN)
    if np.ptp(TP.reshape(-1, 3), axis=0).max() < 1.0:
        TP = TP * 1000.0
    plo, phi = TP.reshape(-1, 3).min(axis=0), TP.reshape(-1, 3).max(axis=0)
    P("local bbox vendor  x %.2f..%.2f  y %.2f..%.2f  z %.2f..%.2f" % (lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]))
    P("local bbox pollen  x %.2f..%.2f  y %.2f..%.2f  z %.2f..%.2f" % (plo[0], phi[0], plo[1], phi[1], plo[2], phi[2]))

    # discs: vendor horn (solid 3) and idler (solid 10) in the local frame
    discs = {}
    for name, idx in (("horn", HORN_SOLID), ("idler", IDLER_SOLID)):
        Vd = np.unique(vendor_to_local(tess(sol[idx], DEFLECTION).reshape(-1, 3)), axis=0)
        # the outer face ring: vertices at the extreme x of the disc
        c, n, s = disc_fit(Vd)
        r = float(np.sqrt(((Vd[:, 1] - c[1]) ** 2 + (Vd[:, 2] - c[2]) ** 2).max()))
        discs[name] = {"solid": idx, "centre_local_mm": [round(float(v), 3) for v in c],
                       "normal_local": [round(float(v), 4) for v in n],
                       "tilt_from_x_deg": round(float(np.degrees(np.arccos(min(1.0, abs(n[0]))))), 3),
                       "axis_offset_from_origin_yz_mm": round(float(np.hypot(c[1], c[2])), 3),
                       "x_extent_local_mm": [round(float(Vd[:, 0].min()), 3), round(float(Vd[:, 0].max()), 3)],
                       "radius_mm": round(r, 3)}
        P("vendor %s disc: centre %s normal %s tilt %.2f deg, off-axis %.3f mm, x %.2f..%.2f, r %.2f"
          % (name, np.round(c, 3), np.round(n, 3), discs[name]["tilt_from_x_deg"],
             discs[name]["axis_offset_from_origin_yz_mm"], Vd[:, 0].min(), Vd[:, 0].max(), r))
    # the same two discs read off the Pollen mesh: vertices with |x| in 11.5..14.5 and r <= 8.1
    VP = np.unique(TP.reshape(-1, 3), axis=0)
    rP = np.hypot(VP[:, 1], VP[:, 2])
    for name, sel in (("horn", (VP[:, 0] > 11.6) & (rP <= 8.1)), ("idler", (VP[:, 0] < -11.6) & (rP <= 8.1))):
        c, n, s = disc_fit(VP[sel])
        discs["pollen_" + name] = {"centre_local_mm": [round(float(v), 3) for v in c],
                                   "normal_local": [round(float(v), 4) for v in n],
                                   "tilt_from_x_deg": round(float(np.degrees(np.arccos(min(1.0, abs(n[0]))))), 3),
                                   "axis_offset_from_origin_yz_mm": round(float(np.hypot(c[1], c[2])), 3),
                                   "x_extent_local_mm": [round(float(VP[sel][:, 0].min()), 3), round(float(VP[sel][:, 0].max()), 3)],
                                   "radius_mm": round(float(rP[sel].max()), 3)}
        P("pollen %s disc: centre %s normal %s tilt %.2f deg, off-axis %.3f mm"
          % (name, np.round(c, 3), np.round(n, 3), discs["pollen_" + name]["tilt_from_x_deg"],
             discs["pollen_" + name]["axis_offset_from_origin_yz_mm"]))
    bad = [k for k, d in discs.items() if d["tilt_from_x_deg"] > 1.0 or d["axis_offset_from_origin_yz_mm"] > 0.5]
    if bad:
        raise RuntimeError("disc axis check failed for %s: the frame mapping is wrong" % bad)
    if not (discs["horn"]["centre_local_mm"][0] > 0 > discs["idler"]["centre_local_mm"][0]):
        raise RuntimeError("horn is not on +x / idler on -x after mapping")

    write_stl(STL, T)
    # read it back through the same loader every consumer uses
    Tb = mf.load_stl_tris(STL)
    if Tb.shape != T.shape or not mf.is_closed(Tb):
        raise RuntimeError("STL read-back failed")
    frame = {"$what": "vendor XL330 solid fused and tessellated in the xl330 (Pollen mesh) frame; the frame proven by disc fits",
             "step": os.path.relpath(STEP, REPO), "step_sha256": sha,
             "frame_mapping": "local(X,Y,Z) = (vendorZ + 8, vendorX, vendorY)",
             "excluded": "6 open shells of the STEP compound (four 18.3 mm2, two 54.0 mm2): surfaces with no volume",
             "union_steps": steps, "union_mm3": round(union.Volume, 3),
             "deflection_mm": DEFLECTION, "angular_deflection_deg": ANGULAR_DEG,
             "triangles": int(T.shape[0]), "closed": True,
             "mesh_volume_mm3": round(mesh_volume(T), 3),
             "bbox_local_mm": {"vendor": [[round(float(v), 3) for v in lo], [round(float(v), 3) for v in hi]],
                               "pollen": [[round(float(v), 3) for v in plo], [round(float(v), 3) for v in phi]]},
             "discs": discs, "stl": os.path.relpath(STL, REPO),
             "pollen_mesh": os.path.relpath(POLLEN, REPO), "pollen_triangles": int(TP.shape[0]),
             "seconds": round(time.time() - t0, 1)}
    json.dump(frame, open(FRAME_JSON, "w"), indent=1)
    P("wrote %s (%d triangles) and %s in %.1f s" % (STL, T.shape[0], FRAME_JSON, time.time() - t0))


def vendor_tris():
    """The fused vendor solid in the local xl330 frame, mm. Built by `build`."""
    from cecad import meshfit as mf
    if not os.path.exists(STL):
        raise FileNotFoundError("%s missing: run  ce-cad/bin/cad tools/fit_vendor_servo.py build" % STL)
    T = mf.load_stl_tris(STL)
    if not mf.is_closed(T):
        raise ValueError("%s is not closed" % STL)
    return T


def substitute(M, P=print):
    """Replace, in memory, every xl330 row's triangles in prove_fit.Model M
    with the vendor solid placed by the row's own world transform, re-expressed
    in the parent body frame exactly as Model.__init__ does. Returns the row
    indices replaced."""
    import prove_fit as pf
    from cecad import meshfit as mf
    T = vendor_tris()
    done = []
    for i in range(M.n):
        r = M.rows[i]
        if r.get("mesh") != "xl330":
            continue
        R = pf.quat_R(r["world_quat_wxyz"])
        t = np.asarray(r["world_pos_mm"], float)
        W = mf.transform_tris(T, R, t).reshape(-1, 3, 3)
        R0, t0 = M.zero[M.body_of[i]]
        M.tris[i] = ((W.reshape(-1, 3) - t0) @ R0).reshape(-1, 3, 3)
        M.closed[M.label[i]] = mf.is_closed(M.tris[i])
        done.append(i)
    M.substituted = {"xl330": os.path.relpath(STL, REPO), "rows": done}
    P("substituted vendor solid (%d triangles) for %d xl330 rows" % (T.shape[0], len(done)))
    return done


def servo_axis_check(M, P):
    """For every hinge, the horn axis of each xl330 row in the joint's body or
    parent: off-axis distance of the disc centre and tilt against the hinge
    axis, at the zero pose. The vendor horn disc is the vertex ring at local
    x >= 14.4 with r <= 8.1 (the outer face of solid 3)."""
    m, d, mj = M.m, M.d, M.mujoco
    d.qpos[:] = M.qpos_for({})
    mj.mj_forward(m, d)
    W = M.world(M.zero)
    out = []
    for i in range(m.njnt):
        if m.jnt_type[i] != mj.mjtJoint.mjJNT_HINGE:
            continue
        jn = mj.mj_id2name(m, mj.mjtObj.mjOBJ_JOINT, i)
        b = m.jnt_bodyid[i]
        Rb = np.asarray(d.xmat[b]).reshape(3, 3)
        tb = np.asarray(d.xpos[b]) * 1000.0
        p = Rb @ (np.asarray(m.jnt_pos[i]) * 1000.0) + tb
        a = Rb @ np.asarray(m.jnt_axis[i])
        a /= np.linalg.norm(a)
        body, parent = M.bname[b], M.bname[m.body_parentid[b]]
        for k in range(M.n):
            if M.body_of[k] not in (body, parent) or M.rows[k].get("mesh") != "xl330":
                continue
            r = M.rows[k]
            R = pf_quat(r["world_quat_wxyz"])
            t = np.asarray(r["world_pos_mm"], float)
            # horn axis of this row in world: local +x through the local origin
            axis = R @ np.array([1.0, 0, 0])
            V = np.unique(W[k].reshape(-1, 3), axis=0)
            L = (V - t) @ R            # back to the local frame
            rr = np.hypot(L[:, 1], L[:, 2])
            ring = V[(L[:, 0] >= 14.4) & (rr <= 8.1)]
            c = ring.mean(axis=0) if ring.shape[0] else t
            v = c - p
            dist = float(np.linalg.norm(v - np.dot(v, a) * a))
            tilt = float(np.degrees(np.arccos(min(1.0, abs(np.dot(axis, a))))))
            out.append({"joint": jn, "row": k, "label": M.label[k], "body": M.body_of[k],
                        "horn_face_centre_mm": [round(float(x), 3) for x in c],
                        "horn_axis_off_joint_axis_mm": round(dist, 3),
                        "horn_axis_tilt_deg": round(tilt, 3), "ring_vertices": int(ring.shape[0])})
            P("  %-16s %-28s horn face centre %s off-axis %6.2f mm tilt %5.1f deg (%d ring verts)"
              % (jn, M.label[k], np.round(c, 2), dist, tilt, ring.shape[0]))
    return out


def pf_quat(q):
    import prove_fit as pf
    return pf.quat_R(q)


def depth_of(h):
    p = h.get("penetration") or {}
    if isinstance(p, dict) and "a_in_b_mm" in p:
        return max(p.get("a_in_b_mm") or 0.0, p.get("b_in_a_mm") or 0.0)
    return None


def stage_rest(P):
    sys.argv = [sys.argv[0], "rest-vendor-servo"]
    import prove_fit as pf
    # prove_fit.main_rest writes <pf.OUT>/rest.json; point it at a scratch dir so
    # the Pollen-mesh census out/fit/rest.json is never overwritten
    pf.OUT = os.path.join(OUT, "_vendor_tmp")
    os.makedirs(pf.OUT, exist_ok=True)
    M = pf.Model()
    P("model: %d rows, %d hinges" % (M.n, len(M.joints)))
    P("servo horn axes vs hinge axes, POLLEN mesh:")
    before = servo_axis_check(M, P)
    substitute(M, P)
    P("servo horn axes vs hinge axes, VENDOR solid:")
    after = servo_axis_check(M, P)
    # per hinge, the servo that drives it is the one whose horn axis is nearest;
    # the other servo rows in the same body/parent are listed for completeness
    drive = {}
    for a in after:
        if a["ring_vertices"] and (a["joint"] not in drive or a["horn_axis_off_joint_axis_mm"] < drive[a["joint"]]["horn_axis_off_joint_axis_mm"]):
            drive[a["joint"]] = a
    worst = max(drive.values(), key=lambda a: a["horn_axis_off_joint_axis_mm"])
    P("driving servo per hinge, vendor solid: worst horn-face centre off its joint axis %.3f mm (%s), worst tilt %.2f deg"
      % (worst["horn_axis_off_joint_axis_mm"], worst["joint"], max(a["horn_axis_tilt_deg"] for a in drive.values())))
    # rerun the census through prove_fit's own loop; it writes rest.json in pf.OUT,
    # so point it at a scratch name and move the result
    t0 = time.time()
    pf.main_rest(M)
    res = json.load(open(os.path.join(pf.OUT, "rest.json")))
    import shutil
    shutil.rmtree(pf.OUT, ignore_errors=True)   # rest.json and the _robot_abs.xml abs_mjcf() wrote there
    pollen = json.load(open(os.path.join(OUT, "rest.json")))
    assert pollen["$what"] == res["$what"] and pollen["rows"] == res["rows"]
    res["substituted"] = M.substituted
    res["servo_axis_check"] = {"pollen": before, "vendor": after, "driving_servo_per_hinge_vendor": drive}

    def keyed(hits):
        out = {}
        for h in hits:
            k = (h["a"], h["b"])
            v = depth_of(h)
            if k not in out or (v or 0) > (out[k][0] or 0):
                out[k] = (v, h)
        return out
    kp, kv = keyed(pollen["hits"]), keyed(res["hits"])
    rows = []
    for (a, b), (dp, hp) in sorted(kp.items(), key=lambda kv_: -(kv_[1][0] or 0)):
        if hp["class"] != "structure x structure" or (dp or 0) <= 0.3:
            continue
        dv, hv = kv.get((a, b), (None, None))
        servo = "xl330" in a or "xl330" in b
        rows.append({"a": a, "b": b, "involves_servo": servo,
                     "pollen_depth_mm": dp, "pollen_overlap_mm3": (hp.get("overlap") or {}).get("mm3"),
                     "vendor_depth_mm": dv, "vendor_overlap_mm3": ((hv or {}).get("overlap") or {}).get("mm3"),
                     "vendor_interferes": bool(hv) and bool(hv.get("intersecting_tri_pairs") or hv.get("fully_contained")),
                     "survives_above_0p3": (dv is not None and dv > 0.3)})
        P("  %-44s x %-44s pollen %.3f -> vendor %s mm  %s"
          % (a, b, dp, ("%.3f" % dv) if dv is not None else "clear",
             "SURVIVES" if rows[-1]["survives_above_0p3"] else ("below 0.3" if dv else "CLEAR")))
    new = []
    for (a, b), (dv, hv) in kv.items():
        if (a, b) not in kp and hv["class"] == "structure x structure" and (dv or 0) > 0.3:
            new.append({"a": a, "b": b, "vendor_depth_mm": dv, "vendor_overlap_mm3": (hv.get("overlap") or {}).get("mm3")})
            P("  NEW with vendor solid: %s x %s %.3f mm" % (a, b, dv))
    res["comparison_above_0p3"] = rows
    res["new_above_0p3_with_vendor"] = new
    res["vendor_census_seconds"] = round(time.time() - t0, 1)
    json.dump(res, open(os.path.join(OUT, "rest-vendor-servo.json"), "w"), indent=1)
    P("DONE: %d of %d above-0.3 rest pairs survive with the vendor solid; %d new. %.1f s"
      % (sum(1 for r in rows if r["survives_above_0p3"]), len(rows), len(new), time.time() - t0))


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "build"
    LOG = open(os.path.join(OUT, "vendor-servo-%s.log" % stage), "w", buffering=1)

    def P(*a):
        LOG.write(" ".join(str(x) for x in a) + "\n")
        LOG.flush()
        print(*a)
    P("stage:", stage)
    try:
        if stage == "build":
            stage_build(P)
        elif stage == "rest":
            stage_rest(P)
        else:
            P("unknown stage %s" % stage)
            sys.exit(2)
    except Exception:
        import traceback
        P("RAISED:\n" + traceback.format_exc())
        raise
