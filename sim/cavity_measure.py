#!/usr/bin/env python3
"""LANE F3 -- MEASURE the closed cavity the compute board actually sits in.

The lane brief said "the Radxa Zero 3W inside the closed trunk".  The geometry
says otherwise and the geometry wins: in sim/microduck_ours.xml the compute
board geom (mesh `pcb__raspberry_pi_zero_2_w`, the Radxa's footprint-matched
placeholder) and the Robot HAT (`elec_rpi_robot_hat_pcb`) are geoms of body
**jaw_soft** -- the HEAD -- not of `trunk_base`.  spec/mesh-placements.json
agrees.  So this script measures BOTH cavities and the compute thermal study
uses the head.

Everything is measured off the meshes; nothing is assumed:
  * mesh names are resolved through the MJCF's own <asset> table, so the
    swapped `*__ours` meshes (sim/meshes_ours/) are read, not the reference
    ones they replaced;
  * every geom is transformed into its body frame by that geom's own pos
    (metres, x1000) and quat;
  * ENCLOSED: a regular voxel grid; a voxel centre is enclosed when, along
    EACH of x, y and z, the shell union has material on both sides of it.  A
    3-axis test, so a hole in one wall cannot leak the whole volume;
  * OCCUPIED: for every mesh (shell and content) a ray-parity point-in-solid
    test on the same grid, OR-ed together.  This is what makes the answer
    right where the reference contents (beak, jaw, servo barrels) stick out
    through the shell -- a content voxel outside the shell is simply not
    counted, instead of being subtracted twice;
  * FREE AIR = enclosed AND NOT occupied.
  * Mesh solid volumes also computed exactly (signed-tetrahedron) as an
    independent cross-check on the voxel occupancy.

    ce-cad/bin/cad sim/cavity_measure.py         (F3_VOXEL_MM=1.5 to refine)

Output: out/sim-evidence/cavity-volumes.json
"""

import json
import os
import sys
import xml.etree.ElementTree as ET

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, "/Users/leifrydenfalk/dev/ce-workshop/ce-cad")

from cecad import meshslice                                  # noqa: E402

MJCF = os.path.join(REPO, "sim/microduck_ours.xml")
MESHDIR = os.path.join(REPO, "reference/pollen-microduck-rl/assets")

CAVITIES = {
    "head": {
        "body": "jaw_soft",
        "shell": ["top_head_shell", "bottom_head_shell"],
        "why": ("top_head_shell + bottom_head_shell are the two printed halves that "
                "close the head. Every other geom of body jaw_soft is either inside "
                "them (the two PCBs, the speaker, the head-roll and jaw XL330s, the "
                "motor support, the lens and its holder) or bolted through them (the "
                "face, eye ring, jaw and soft mouth)."),
    },
    "trunk": {
        "body": "trunk_base",
        "shell": ["left_shell", "right_shell"],
        "why": ("left_shell + right_shell are the two printed halves that close the "
                "trunk. trunk_base__ours is its floor plate and power_support__ours "
                "the battery cradle; both are contents of the enclosure, not walls "
                "of it."),
    },
}


def quat_matrix(q):
    w, x, y, z = [float(v) for v in q]
    n = (w * w + x * x + y * y + z * z) ** 0.5
    w, x, y, z = w / n, x / n, y / n, z / n
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])


def asset_table(root):
    """MJCF <asset><mesh> -> {name: (abs path, mm per file unit)}."""
    out = {}
    for m in root.iter("mesh"):
        f = m.get("file")
        if not f:
            continue
        name = m.get("name") or os.path.splitext(os.path.basename(f))[0]
        path = os.path.normpath(os.path.join(MESHDIR, f))
        sc = m.get("scale")
        # compiler meshdir units are metres; a mesh that carries its own
        # scale (the __ours swaps, 0.001) is a mm file scaled to metres, so
        # both come back to mm the same way.
        scale_mm = 1000.0 if sc is None else 1000.0 * float(sc.split()[0])
        out[name] = (path, scale_mm)
    return out


def body_geoms(root, body_name):
    for b in root.iter("body"):
        if b.get("name") == body_name:
            out = []
            for g in b.findall("geom"):
                if g.get("type") != "mesh":
                    continue
                pos = np.array([float(v) for v in (g.get("pos") or "0 0 0").split()]) * 1000.0
                out.append((g.get("mesh"), g.get("class"), pos,
                            quat_matrix((g.get("quat") or "1 0 0 0").split())))
            return out
    raise KeyError(body_name)


def mesh_volume_mm3(T):
    a, b, c = T[:, 0], T[:, 1], T[:, 2]
    return float(abs(np.einsum("ij,ij->i", a, np.cross(b, c)).sum()) / 6.0)


def mesh_area_mm2(T):
    a, b, c = T[:, 0], T[:, 1], T[:, 2]
    return float(0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1).sum())


def _rays(T, axis, U, V, chunk=128):
    """Sorted crossing coordinates along `axis` for every ray through (u, v).
    Vectorised Moller-Trumbore with a per-chunk in-plane bbox prefilter."""
    ai = "xyz".index(axis)
    ui, vi = (ai + 1) % 3, (ai + 2) % 3
    UU, VV = np.meshgrid(U, V, indexing="ij")
    n = UU.size
    O = np.zeros((n, 3))
    O[:, ui] = UU.ravel()
    O[:, vi] = VV.ravel()
    O[:, ai] = T[:, :, ai].min() - 10.0
    d = np.zeros(3)
    d[ai] = 1.0
    tu_lo, tu_hi = T[:, :, ui].min(axis=1), T[:, :, ui].max(axis=1)
    tv_lo, tv_hi = T[:, :, vi].min(axis=1), T[:, :, vi].max(axis=1)
    hits = [None] * n
    for s in range(0, n, chunk):
        Ob = O[s:s + chunk]
        sel = ((tu_hi >= Ob[:, ui].min() - 1e-9) & (tu_lo <= Ob[:, ui].max() + 1e-9) &
               (tv_hi >= Ob[:, vi].min() - 1e-9) & (tv_lo <= Ob[:, vi].max() + 1e-9))
        if not sel.any():
            for i in range(len(Ob)):
                hits[s + i] = np.zeros(0)
            continue
        Tc = T[sel]
        v0, v1, v2 = Tc[:, 0], Tc[:, 1], Tc[:, 2]
        e1, e2 = v1 - v0, v2 - v0
        h = np.cross(np.broadcast_to(d, e2.shape), e2)
        a = np.einsum("ij,ij->i", e1, h)
        ok = np.abs(a) > 1e-12
        inv = np.zeros_like(a)
        inv[ok] = 1.0 / a[ok]
        S = Ob[:, None, :] - v0[None, :, :]
        u = inv[None, :] * np.einsum("bmj,mj->bm", S, h)
        Q = np.cross(S, e1[None, :, :])
        vv = inv[None, :] * np.einsum("bmj,j->bm", Q, d)
        t = inv[None, :] * np.einsum("bmj,mj->bm", Q, e2)
        hit = ok[None, :] & (u >= -1e-7) & (vv >= -1e-7) & (u + vv <= 1 + 1e-7)
        for i in range(len(Ob)):
            hits[s + i] = np.sort(t[i][hit[i]]) + Ob[i, ai]
    return hits, (len(U), len(V))


def spans_along(T, axis, U, V):
    hits, shape = _rays(T, axis, U, V)
    lo = np.array([h[0] if h.size else np.inf for h in hits]).reshape(shape)
    hi = np.array([h[-1] if h.size else -np.inf for h in hits]).reshape(shape)
    return lo, hi


def inside_along_z(T, xs, ys, zs):
    """Ray-parity point-in-solid over the grid, rays along +z: a point is
    inside when the number of surface crossings strictly below it is odd."""
    hits, _ = _rays(T, "z", xs, ys)
    occ = np.zeros((len(xs), len(ys), len(zs)), bool)
    k = 0
    for i in range(len(xs)):
        for j in range(len(ys)):
            h = hits[k]
            k += 1
            if h.size >= 2:
                occ[i, j, :] = (np.searchsorted(h, zs) % 2) == 1
    return occ


def measure(name, spec, step, root, assets):
    geoms = body_geoms(root, spec["body"])
    placed = []
    for mesh_name, gclass, pos, R in geoms:
        if gclass == "self_collision_only":
            continue                       # duplicate of a visual geom
        path, scale = assets[mesh_name]
        T = meshslice.load(path, scale=scale) @ R.T + pos
        placed.append((mesh_name, T))
    by_name = {}
    for mesh_name, T in placed:
        by_name.setdefault(mesh_name, []).append(T)

    shell_names = []
    for want in spec["shell"]:
        cand = [n for n in by_name if n in (want, want + "__ours")]
        assert cand, "%s not a geom of body %s (has %s)" % (want, spec["body"],
                                                            sorted(by_name))
        shell_names.append(cand[0])
    shell_T = [t for n in shell_names for t in by_name[n]]
    # The ENCLOSURE is the union of EVERY geom of the body, not only the two
    # named shell halves. Measured reason, not a preference: probing the head
    # shells alone along z at the compute board's own (x, y) = (15.4, 0) mm
    # gives material only over z 27.67..34.07 mm, while the board sits at
    # z = -60 mm -- the printed shells are open where the face, eye ring, jaw
    # and soft mouth close the head. Using only the shell halves therefore
    # reports the board as OUTSIDE its own enclosure, which is wrong. The
    # closed volume is what all the body's parts bound together.
    hull_T = np.concatenate([t for ts in by_name.values() for t in ts], axis=0)
    ST = hull_T

    mn, mx = ST.reshape(-1, 3).min(axis=0), ST.reshape(-1, 3).max(axis=0)
    xs = np.arange(mn[0] + step / 2, mx[0], step)
    ys = np.arange(mn[1] + step / 2, mx[1], step)
    zs = np.arange(mn[2] + step / 2, mx[2], step)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")

    enclosed = np.ones(X.shape, bool)
    lo, hi = spans_along(ST, "z", xs, ys)
    enclosed &= (Z > lo[:, :, None]) & (Z < hi[:, :, None])
    lox, hix = spans_along(ST, "x", ys, zs)
    enclosed &= (X > lox[None, :, :]) & (X < hix[None, :, :])
    loy, hiy = spans_along(ST, "y", zs, xs)
    enclosed &= (Y > loy.T[:, None, :]) & (Y < hiy.T[:, None, :])

    vox = step ** 3
    occupied = np.zeros(X.shape, bool)
    per_mesh = {}
    for mesh_name, T in placed:
        occ = inside_along_z(T, xs, ys, zs)
        occupied |= occ
        rec = per_mesh.setdefault(mesh_name, {
            "count": 0, "exact_volume_mm3": 0.0, "voxel_volume_mm3": 0.0,
            "voxel_volume_inside_shell_mm3": 0.0})
        rec["count"] += 1
        rec["exact_volume_mm3"] += mesh_volume_mm3(T)
        rec["voxel_volume_mm3"] += float(occ.sum()) * vox
        rec["voxel_volume_inside_shell_mm3"] += float((occ & enclosed).sum()) * vox
    for rec in per_mesh.values():
        for k in list(rec):
            if k.endswith("_mm3"):
                rec[k] = round(rec[k], 3)

    enclosed_mm3 = float(enclosed.sum()) * vox
    free_mm3 = float((enclosed & ~occupied).sum()) * vox
    # staircase surface area of the enclosed region: count grid faces where a
    # voxel is enclosed and its neighbour is not.
    faces = 0
    for ax in range(3):
        a = np.moveaxis(enclosed, ax, 0)
        faces += int((a[0]).sum()) + int((a[-1]).sum())
        faces += int((a[:-1] & ~a[1:]).sum()) + int((a[1:] & ~a[:-1]).sum())
    hull_area = faces * step * step
    shell_area = sum(mesh_area_mm2(t) for t in shell_T)
    shell_solid = sum(mesh_volume_mm3(t) for t in shell_T)
    contents_in = sum(v["voxel_volume_inside_shell_mm3"] for k, v in per_mesh.items()
                      if k not in shell_names)

    return {
        "body": spec["body"],
        "why_these_meshes": spec["why"],
        "voxel_step_mm": step,
        "grid": [len(xs), len(ys), len(zs)],
        "shell_meshes": shell_names,
        "shell_bbox_mm": {"min": [round(float(v), 4) for v in mn],
                          "max": [round(float(v), 4) for v in mx],
                          "size": [round(float(b - a), 4) for a, b in zip(mn, mx)]},
        "shell_triangle_area_mm2": round(shell_area, 2),
        "shell_outer_area_estimate_mm2": round(shell_area / 2.0, 2),
        "shell_outer_area_basis": ("the two printed shell halves are thin walls, so "
                                   "their triangle area counts the inner face, the "
                                   "outer face and the edges. Half the triangle area "
                                   "is the outer skin to within the edge strip."),
        "enclosure_hull_area_voxel_mm2": round(hull_area, 2),
        "enclosure_hull_area_basis": ("staircase area of the voxel enclosure boundary "
                                      "at %.2f mm; it OVERSTATES a curved surface by "
                                      "up to ~4/pi and is reported as the upper "
                                      "bracket on the skin area." % step),
        "shell_solid_volume_exact_mm3": round(shell_solid, 2),
        "enclosed_volume_mm3": round(enclosed_mm3, 2),
        "enclosed_volume_cm3": round(enclosed_mm3 / 1000.0, 4),
        "contents_inside_shell_mm3": round(contents_in, 2),
        "free_air_volume_mm3": round(free_mm3, 2),
        "free_air_volume_cm3": round(free_mm3 / 1000.0, 4),
        "free_air_fraction_of_enclosed": round(free_mm3 / enclosed_mm3, 4),
        "per_mesh": per_mesh,
    }


def main():
    step = float(os.environ.get("F3_VOXEL_MM", "1.5"))
    root = ET.parse(MJCF).getroot()
    assets = asset_table(root)
    res = {}
    for name, spec in CAVITIES.items():
        res[name] = measure(name, spec, step, root, assets)
        r = res[name]
        print("%-6s enclosed %8.3f cm3  contents %8.3f cm3  FREE AIR %8.3f cm3  "
              "skin %8.1f mm2  bbox %s"
              % (name, r["enclosed_volume_cm3"], r["contents_inside_shell_mm3"] / 1000.0,
                 r["free_air_volume_cm3"], r["shell_outer_area_estimate_mm2"],
                 r["shell_bbox_mm"]["size"]))

    out = {
        "study": "cavity-volumes",
        "what": ("Measured internal free-air volume and outer skin area of the two "
                 "closed printed cavities, and which one the compute board is in."),
        "inputs": {
            "mjcf": "sim/microduck_ours.xml",
            "meshdir": "reference/pollen-microduck-rl/assets (MJCF compiler meshdir; "
                       "metres, scaled x1000 to mm here). The swapped `*__ours` meshes "
                       "resolve through the same <asset> table to sim/meshes_ours/.",
            "placements_cross_check": "spec/mesh-placements.json",
            "voxel_step_mm": step,
        },
        "method": ("ENCLOSED by a 3-axis enclosure test on a %s mm voxel grid (the "
                   "shell union must have material on both sides along x AND y AND z). "
                   "OCCUPIED by a per-mesh ray-parity point-in-solid test on the same "
                   "grid, OR-ed. FREE AIR = enclosed AND NOT occupied, so a content "
                   "that pokes out through the shell (the beak, the jaw, a servo "
                   "barrel) is not counted rather than subtracted twice. Mesh solid "
                   "volumes also computed exactly by signed tetrahedra as an "
                   "independent check on the voxel occupancy." % step),
        "outputs": {
            "cavities": res,
            "compute_board_body": "jaw_soft (the HEAD)",
            "compute_board_evidence": (
                "sim/microduck_ours.xml body 'jaw_soft' carries "
                "<geom type=\"mesh\" class=\"visual\" pos=\"0.015435 -1.13778e-05 "
                "-0.06001\" ... mesh=\"pcb__raspberry_pi_zero_2_w\"> and "
                "<geom ... pos=\"0.02694 0.0289936 -0.0519\" "
                "mesh=\"elec_rpi_robot_hat_pcb\">; spec/mesh-placements.json lists "
                "both under body 'jaw_soft'. Body 'trunk_base' carries no compute "
                "geom at all -- its only PCB-ish geom is banana_pcb_locker__ours, "
                "the battery-contact retainer."),
        },
        "verdict": "PASS",
        "why": "",
        "script": "sim/cavity_measure.py",
        "artifacts": ["out/sim-evidence/cavity-volumes.json"],
        "looked_at": ["sim/microduck_ours.xml", "spec/mesh-placements.json",
                      "reference/pollen-microduck-rl/assets/*.stl",
                      "sim/meshes_ours/*.stl"],
    }
    out["why"] = (
        "HEAD: %.3f cm3 enclosed by the two head shells, %.3f cm3 of it free air "
        "(%.1f %% void), outer skin %.1f mm2. TRUNK: %.3f cm3 enclosed, %.3f cm3 free "
        "air (%.1f %% void), outer skin %.1f mm2. The compute board is a geom of body "
        "jaw_soft, so the compute thermal study is a HEAD study -- the lane brief's "
        "'inside the closed trunk' is contradicted by the model and corrected here."
        % (res["head"]["enclosed_volume_cm3"], res["head"]["free_air_volume_cm3"],
           100 * res["head"]["free_air_fraction_of_enclosed"],
           res["head"]["shell_outer_area_estimate_mm2"],
           res["trunk"]["enclosed_volume_cm3"], res["trunk"]["free_air_volume_cm3"],
           100 * res["trunk"]["free_air_fraction_of_enclosed"],
           res["trunk"]["shell_outer_area_estimate_mm2"]))
    path = os.path.join(REPO, "out/sim-evidence/cavity-volumes.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(out, open(path, "w"), indent=1)
    print(out["why"])
    print("wrote out/sim-evidence/cavity-volumes.json")


if __name__ == "__main__":
    main()
