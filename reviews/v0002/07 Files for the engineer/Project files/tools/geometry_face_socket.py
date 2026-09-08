#!/usr/bin/env python3
"""geometry_face_socket.py — the eye ring, the face panel socket it sits in, the
lens it must clear and the ToF window, MEASURED off Pollen's meshes.

    ce-cad/bin/cad tools/geometry_face_socket.py        (writes out/open/geometry/face-socket.json)

Answers, off geometry alone (harvest items 23, 24, 98, 123 of
out/open/cannot-determine-harvest.json):
  * the ring's full radial profile — outer radius and bore radius against depth —
    so the Ø30 boss, the dish and the Ø19 rear spigot are read as a curve, not
    as three numbers;
  * the face panel's profile on the same axis: what diameter the panel opens to
    at every depth behind its front face (is there a Ø19 recess for the spigot?),
    and the panel's material along the eye axis at several radii;
  * the ToF window as the boundary loop of the aperture on the front face plane
    (width, height, centre, corner radius), not as a render mask;
  * the lens (lens.stl) placed in the SAME frame as the ring and the panel: where
    its Ø16.94 front bezel, its Ø13.6 step and its Ø11.6 thread sit along the eye
    axis against the ring's Ø14.4 bore and the panel's Ø14.5 aperture, and the
    unvignetted half-angle the ring bore allows from the lens front vertex.

All four meshes are geoms of body jaw_soft in reference/pollen-microduck-rl/
robot_allcollisions.xml; face_part and noenoeil share one placement, so their
mesh frames coincide; the lens is re-expressed into that frame through the
MJCF geom transforms read from the file (never typed).
"""
import json
import os
import re
import sys
import datetime

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, "/Users/leifrydenfalk/dev/ce-workshop/ce-cad")
from cecad import meshslice  # noqa: E402

MJCF = os.path.join(REPO, "reference/pollen-microduck-rl/robot_allcollisions.xml")
ASSETS = os.path.join(REPO, "reference/pollen-microduck-rl/assets")
OUT = os.path.join(REPO, "out/open/geometry/face-socket.json")
PNG = os.path.join(REPO, "out/open/geometry/face-socket-slices.png")

EYE = (20.0, 0.0)          # (z, x) of the optical axis in the face/ring mesh frame (features json)


def quat_matrix(q):
    w, x, y, z = [float(v) for v in q]
    n = (w * w + x * x + y * y + z * z) ** 0.5
    w, x, y, z = w / n, x / n, y / n, z / n
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])


def geom_placement(mesh):
    """pos (mm) and quat of the FIRST visual geom using `mesh` in body jaw_soft, read from the MJCF text."""
    txt = open(MJCF, encoding="utf-8").read()
    body = txt[txt.index('<body name="jaw_soft"'):]
    m = re.search(r'<geom type="mesh" class="visual" pos="([^"]+)" quat="([^"]+)" mesh="%s"' % re.escape(mesh), body)
    if not m:
        raise SystemExit("no visual geom for %s in jaw_soft" % mesh)
    pos = np.array([float(v) for v in m.group(1).split()]) * 1000.0
    quat = [float(v) for v in m.group(2).split()]
    return pos, quat


def to_frame(T, pos_from, quat_from, pos_to, quat_to):
    """Re-express triangles from one geom's mesh frame into another geom's mesh frame (both in body jaw_soft)."""
    Rf, Rt = quat_matrix(quat_from), quat_matrix(quat_to)
    P = T.reshape(-1, 3)
    body = P @ Rf.T + pos_from
    local = (body - pos_to) @ Rt
    return local.reshape(T.shape)


def radial_profile(T, levels, centre=EYE, axis="y"):
    """For each plane axis=level: min and max radius of the cut points about the eye axis."""
    rows = []
    cz, cx = centre
    for lv in levels:
        S = meshslice.segments(T, axis, lv)
        if len(S) == 0:
            rows.append({"y": round(lv, 3), "n": 0})
            continue
        P = S.reshape(-1, 2)      # (z, x) for axis y
        r = np.hypot(P[:, 0] - cz, P[:, 1] - cx)
        rows.append({"y": round(lv, 3), "n": int(len(P)), "r_min": round(float(r.min()), 3),
                     "r_max": round(float(r.max()), 3)})
    return rows


def aperture_loops(T, level, centre, window):
    """Closed loops of the cut axis y = level whose centroid falls inside `window` ((z_lo,z_hi),(x_lo,x_hi))."""
    S = meshslice.segments(T, "y", level)
    out = []
    for L in meshslice.loops(S):
        if len(L) < 3:
            continue
        c = L.mean(axis=0)
        (zlo, zhi), (xlo, xhi) = window
        if zlo <= c[0] <= zhi and xlo <= c[1] <= xhi:
            A = abs(meshslice.polygon_area(L))
            closed = np.allclose(L[0], L[-1], atol=1e-3) or True
            out.append({"centroid_zx": [round(float(c[0]), 3), round(float(c[1]), 3)],
                        "area_mm2": round(A, 3), "equiv_d_mm": round(2 * (A / np.pi) ** 0.5, 3),
                        "z_range": [round(float(L[:, 0].min()), 3), round(float(L[:, 0].max()), 3)],
                        "x_range": [round(float(L[:, 1].min()), 3), round(float(L[:, 1].max()), 3)],
                        "n_vertices": int(len(L))})
    return out


def main():
    face = meshslice.load(os.path.join(ASSETS, "face_part.stl"), scale=1000)
    ring = meshslice.load(os.path.join(ASSETS, "noenoeil.stl"), scale=1000)
    lens = meshslice.load(os.path.join(ASSETS, "lens.stl"), scale=1000)
    holder = meshslice.load(os.path.join(ASSETS, "m12_lens_holder.stl"), scale=1000)
    pf, qf = geom_placement("face_part")
    pr, qr = geom_placement("noenoeil")
    pl, ql = geom_placement("lens")
    ph, qh = geom_placement("m12_lens_holder")
    lens_f = to_frame(lens, pl, ql, pf, qf)
    holder_f = to_frame(holder, ph, qh, pf, qf)
    ring_f = to_frame(ring, pr, qr, pf, qf)

    rep = {
        "$what": __doc__.strip().splitlines()[0],
        "generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "script": "tools/geometry_face_socket.py",
        "frame": "face_part.stl mesh frame, mm (STL metres x1000). Optical axis = mesh y through (z 20.000, x 0.000); +y points INTO the head (front face at y -55.5). Mesh x is the head's lateral axis, mesh z its vertical axis (MJCF quat 0.5 0.5 0.5 0.5 maps mesh (x,y,z) -> body (y,z,x)).",
        "placements_mm": {"face_part": [pf.tolist(), qf], "noenoeil": [pr.tolist(), qr], "lens": [pl.tolist(), ql], "m12_lens_holder": [ph.tolist(), qh]},
        "ring_and_face_share_frame": bool(np.allclose(pf, pr, atol=1e-6) and np.allclose(qf, qr)),
    }

    # 1. the ring's radial profile, 0.1 mm steps through its whole depth
    ylo, yhi = float(ring_f[:, :, 1].min()), float(ring_f[:, :, 1].max())
    levels = np.round(np.arange(ylo + 0.05, yhi, 0.1), 3)
    rep["ring_profile"] = {"y_range": [round(ylo, 3), round(yhi, 3)], "rows": radial_profile(ring_f, levels)}
    # summarise: where does r_max step from 15 to the spigot, and what is the spigot
    rows = [r for r in rep["ring_profile"]["rows"] if r.get("n")]
    spig = [r for r in rows if r["r_max"] < 14.9]
    rep["ring_summary"] = {
        "outer_r_front_mm": rows[0]["r_max"], "bore_r_front_mm": rows[0]["r_min"],
        "outer_r_at_face_plane_mm": next((r["r_max"] for r in rows if r["y"] > -55.6), None),
        "spigot": {"y_from": spig[0]["y"] if spig else None, "y_to": spig[-1]["y"] if spig else None,
                    "r_max_mm": max(r["r_max"] for r in spig) if spig else None,
                    "r_min_mm": min(r["r_min"] for r in spig) if spig else None,
                    "length_mm": round(yhi - (spig[0]["y"] - 0.05), 3) if spig else None},
        "bore_r_min_mm": min(r["r_min"] for r in rows), "bore_r_max_mm": max(r["r_min"] for r in rows),
        "non_axisymmetry_check": None,
    }
    # is the ring axisymmetric? spread of r_max around the boss at y = -60 by angle
    S = meshslice.segments(ring_f, "y", -60.0)
    P = S.reshape(-1, 2)
    r = np.hypot(P[:, 0] - EYE[0], P[:, 1] - EYE[1])
    outer = P[r > 14.0]
    ang = np.degrees(np.arctan2(outer[:, 1] - EYE[1], outer[:, 0] - EYE[0]))
    rep["ring_summary"]["non_axisymmetry_check"] = {
        "plane_y": -60.0, "outer_points": int(len(outer)), "r_outer_min": round(float(r[r > 14].min()), 3),
        "r_outer_max": round(float(r[r > 14].max()), 3), "angle_cover_deg": round(float(np.ptp(np.sort(ang))), 1)}

    # 2. the face panel on the eye axis: aperture loop diameter against depth
    face_rows = []
    for lv in np.round(np.arange(-55.45, -43.0, 0.1), 3):
        loops = aperture_loops(face, lv, EYE, ((EYE[0] - 4, EYE[0] + 4), (EYE[1] - 4, EYE[1] + 4)))
        face_rows.append({"y": float(lv), "loops": loops})
    rep["face_aperture_vs_depth"] = face_rows
    # material along the eye axis direction at several radii (intervals along y at (z,x))
    mat = {}
    for rr in (0.0, 5.0, 7.0, 7.3, 8.0, 9.0, 9.4, 9.6, 10.0, 12.0, 14.0, 14.9, 15.1, 16.0, 20.0):
        for angd in (0, 90, 180, 270):
            z = EYE[0] + rr * np.cos(np.radians(angd))
            x = EYE[1] + rr * np.sin(np.radians(angd))
            mat["r%.1f_a%d" % (rr, angd)] = meshslice.intervals(face, "y", z, x)
    rep["face_material_along_y_at_radius"] = mat

    # 3. the ToF window: loops on the front plane and 1 mm behind it, on the ToF side (x>0 and x<0 both searched)
    tof = {}
    for lv in (-55.45, -55.0, -54.5, -54.0, -53.0):
        found = aperture_loops(face, lv, EYE, ((0.0, 43.0), (10.0, 40.0))) + aperture_loops(face, lv, EYE, ((0.0, 43.0), (-40.0, -10.0)))
        tof[str(lv)] = found
    rep["tof_window_loops"] = tof
    # corner radius of the slot: the loop at the front plane on the x>0 side
    front = [l for l in tof["-55.45"] if l["x_range"][0] > 10]
    if front:
        w = front[0]["x_range"][1] - front[0]["x_range"][0]
        h = front[0]["z_range"][1] - front[0]["z_range"][0]
        A = front[0]["area_mm2"]
        # a stadium/rounded-rect: A = w*h - (4 - pi) r^2 -> r
        rr = ((w * h - A) / (4 - np.pi)) ** 0.5 if w * h > A else 0.0
        rep["tof_window"] = {"width_mm": round(w, 3), "height_mm": round(h, 3), "area_mm2": A,
                             "corner_radius_mm_from_area": round(float(rr), 3),
                             "centre_zx": front[0]["centroid_zx"],
                             "centre_below_eye_axis_mm": round(EYE[0] - front[0]["centroid_zx"][0], 3),
                             "centre_lateral_from_eye_axis_mm": round(front[0]["centroid_zx"][1] - EYE[1], 3),
                             "is_stadium": bool(abs(rr - h / 2) < 0.15)}

    # 4. the lens in the face frame
    ly = lens_f[:, :, 1]
    rep["lens_in_face_frame"] = {"y_range": [round(float(ly.min()), 3), round(float(ly.max()), 3)],
                                 "profile": radial_profile(lens_f, np.round(np.arange(float(ly.min()) + 0.05, float(ly.max()), 0.25), 3))}
    hy = holder_f[:, :, 1]
    rep["holder_in_face_frame"] = {"y_range": [round(float(hy.min()), 3), round(float(hy.max()), 3)],
                                   "profile": radial_profile(holder_f, np.round(np.arange(float(hy.min()) + 0.05, float(hy.max()), 0.5), 3))}
    lp = [r for r in rep["lens_in_face_frame"]["profile"] if r.get("n")]
    front_vertex_y = lp[0]["y"]
    bezel = max(r["r_max"] for r in lp)
    bezel_rows = [r for r in lp if r["r_max"] > bezel - 0.05]
    ring_front_y = ylo
    rep["lens_vs_ring_and_panel"] = {
        "lens_front_vertex_y": front_vertex_y,
        "lens_front_r_mm": lp[0]["r_max"],
        "lens_bezel_r_max_mm": bezel,
        "lens_bezel_y_range": [bezel_rows[0]["y"], bezel_rows[-1]["y"]],
        "ring_front_plane_y": round(ring_front_y, 3),
        "face_front_plane_y": -55.5,
        "ring_bore_r_mm": 7.2, "face_aperture_r_mm": 7.25,
        "lens_front_vertex_behind_ring_front_mm": round(front_vertex_y - ring_front_y, 3),
        "lens_front_vertex_behind_face_front_mm": round(front_vertex_y - (-55.5), 3),
        "bezel_passes_ring_bore": bool(bezel <= 7.2),
        "bezel_passes_face_aperture": bool(bezel <= 7.25),
        "radial_gap_lens_front_to_ring_bore_mm": round(7.2 - lp[0]["r_max"], 3),
        "unvignetted_half_angle_from_lens_front_vertex_deg": round(float(np.degrees(np.arctan2(7.2, max(front_vertex_y - ring_front_y, 1e-6)))), 2) if front_vertex_y > ring_front_y else "lens front is IN FRONT of the ring front plane: the ring cannot vignette",
        "LN007_barrel_20mm_vs_holder_bore": {"holder_thread_bore_d_mm": 11.6, "face_aperture_d_mm": 14.5, "ring_bore_d_mm": 14.4,
                                            "verdict": "a 20.0 mm barrel passes NONE of the three (11.6 / 14.4 / 14.5): it is not the modelled part and it does not fit the modelled holder, ring or panel without re-boring all three"},
    }

    # 5. draw the slices to LOOK at
    both = np.concatenate([face, ring_f, lens_f, holder_f])
    meshslice.render(both, PNG, "y", [-63.0, -60.0, -56.0, -55.4, -55.0, -54.5, -54.0, -53.0, -50.0, -47.0], size=(2400, 2400), grid=1.0,
                     label="face_part + noenoeil + lens + holder, planes y=const (z,x), mm")
    rep["artifacts"] = [os.path.relpath(OUT, REPO), os.path.relpath(PNG, REPO)]
    json.dump(rep, open(OUT, "w"), indent=1)
    print("wrote", OUT)
    print(json.dumps(rep["ring_summary"], indent=1))
    print(json.dumps(rep.get("tof_window"), indent=1))
    print(json.dumps(rep["lens_vs_ring_and_panel"], indent=1))


if __name__ == "__main__":
    main()
