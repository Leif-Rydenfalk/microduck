#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""swap_meshes.py — Pollen's MJCF with OUR rebuilt meshes for every PASSed part.

Writes
  sim/meshes_ours/<mesh>.stl        copies of the PASSed ours.stl (mm, Pollen's mesh frame)
  sim/meshes_ours/manifest.json     where each came from (refcheck report, sha256)
  sim/microduck_ours.xml            robot_walk.xml with the VISUAL geoms re-pointed
  sim/microduck_ours_allcollisions.xml   same for robot_allcollisions.xml (sit/stand)

Rules:
  * a part is swapped only if tools/watch-pass.log says PASS for its slug and a
    refcheck report.json with verdict PASS exists for that part against that mesh;
  * the mesh is added under a NEW asset name (<mesh>__ours, scale 0.001 mm->m) and
    only geoms of class "visual" are re-pointed. Collision geoms (soles, the
    self_collision_only copies of leg/power_support, and every collision geom of
    robot_allcollisions.xml) keep Pollen's meshes, and every body keeps its explicit
    <inertial>, so the dynamics are the stock dynamics — only what is DRAWN changes;
  * after writing, both models are compiled and the world-frame bbox of every
    re-pointed geom at the zero pose is compared with the stock geom: must agree
    within --tol mm (default 1.5) or the script fails.
"""
import argparse
import glob
import hashlib
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

ROOT = common.ROOT
MESH_OUT = os.path.join(common.HERE, "meshes_ours")
ORANGE = "0.95 0.50 0.10 1"


def passed_slugs():
    slugs = []
    log = os.path.join(ROOT, "tools", "watch-pass.log")
    for line in open(log):
        parts = line.split()
        if len(parts) >= 3 and parts[1] == "PASS" and parts[2] not in slugs:
            slugs.append(parts[2])
    return slugs


def mesh_map():
    m = json.load(open(os.path.join(ROOT, "spec", "mesh-to-part.json")))["map"]
    by_ref = {}
    for mesh, ref in m.items():
        by_ref.setdefault(ref, []).append(mesh)
    return m, by_ref


def resolve_ref(slug, by_ref):
    for cand in ("part:" + slug, "part:microduck-" + slug):
        if cand in by_ref:
            return cand
    return None


def newest_pass_report(ref, mesh):
    """Newest refcheck report.json with verdict PASS for this part ref against
    this mesh, searched in out/refcheck/*/ and ce-parts/*/.../evidence/refcheck/."""
    pats = [os.path.join(ROOT, "out", "refcheck", "*", "*", "report.json"),
            os.path.join(ROOT, "ce-parts", "*", "iterations", "*", "evidence", "refcheck", "*", "report.json")]
    best = None
    for pat in pats:
        for p in glob.glob(pat):
            try:
                r = json.load(open(p))
            except Exception:
                continue
            if r.get("target") != ref:
                continue
            if os.path.basename(r.get("reference", "")) != mesh + ".stl":
                continue
            if r.get("shape", {}).get("verdict") != "PASS":
                continue
            ours = r.get("ours")
            if not ours or not os.path.exists(ours):
                continue
            key = r.get("when", "")
            if best is None or key > best[0]:
                best = (key, p, r)
    return best


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_stl_tris(path):
    """ASCII or binary STL -> (N,3,3) float array in the file's units (mm here)."""
    import struct
    b = open(path, "rb").read()
    if b[:5] == b"solid" and b"facet" in b[:4000]:
        v = re.findall(rb"vertex\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)", b)
        a = np.array(v, dtype=np.float64)
        if len(a) == 0 or len(a) % 3:
            raise ValueError("%s: bad ASCII STL (%d vertices)" % (path, len(a)))
        return a.reshape(-1, 3, 3)
    n = struct.unpack_from("<I", b, 80)[0]
    rec = np.frombuffer(b, dtype=np.dtype([("n", "<3f4"), ("v", "<9f4"), ("a", "<u2")]), count=n, offset=84)
    return rec["v"].astype(np.float64).reshape(-1, 3, 3)


def to_binary_stl(src, dst):
    """Write tris as binary STL (facet normals recomputed). Returns the count."""
    import struct
    t = read_stl_tris(src)
    n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    ln = np.linalg.norm(n, axis=1)
    ln[ln == 0] = 1.0
    n = (n / ln[:, None]).astype("<f4")
    rec = np.zeros(len(t), dtype=np.dtype([("n", "<3f4"), ("v", "<9f4"), ("a", "<u2")]))
    rec["n"] = n
    rec["v"] = t.reshape(-1, 9).astype("<f4")
    with open(dst, "wb") as f:
        f.write(("ce-workshop microduck ours: " + os.path.basename(src)).encode()[:80].ljust(80, b"\0"))
        f.write(struct.pack("<I", len(t)))
        f.write(rec.tobytes())
    return int(len(t))


def write_swapped(src_xml, dst_xml, swapped):
    """swapped: {mesh_name: stl_path_in_sim/meshes_ours}. Returns list of re-pointed geom indices (document order)."""
    tree = ET.parse(src_xml)
    root = tree.getroot()
    comp = root.find("compiler")
    meshdir_abs = os.path.normpath(os.path.join(os.path.dirname(src_xml), comp.get("meshdir", "assets")))
    comp.set("meshdir", os.path.relpath(meshdir_abs, os.path.dirname(dst_xml)))
    asset = root.find("asset")
    for mesh, stl in swapped.items():
        rel = os.path.relpath(stl, meshdir_abs)   # MuJoCo joins meshdir + file as a string
        ET.SubElement(asset, "mesh", name=mesh + "__ours", file=rel, scale="0.001 0.001 0.001")
    ET.SubElement(asset, "material", name="ours_material", rgba=ORANGE)
    repointed = []
    for i, g in enumerate(root.iter("geom")):
        if g.get("class") == "visual" and g.get("mesh") in swapped:
            g.set("mesh", g.get("mesh") + "__ours")
            g.set("material", "ours_material")
            repointed.append(i)
    text = ET.tostring(root, encoding="unicode")
    head = ('<?xml version="1.0" ?>\n<!-- generated by sim/swap_meshes.py from %s: visual geoms of %s re-pointed to '
            'OUR meshes (sim/meshes_ours, mm scaled 0.001). Collision geoms and inertials are Pollen\'s. -->\n'
            % (os.path.relpath(src_xml, ROOT), ", ".join(sorted(swapped))))
    with open(dst_xml, "w") as f:
        f.write(head + text)
    return repointed


def geom_world_bbox(model, data, gid):
    import mujoco
    mid = model.geom_dataid[gid]
    assert model.geom_type[gid] == mujoco.mjtGeom.mjGEOM_MESH
    a = model.mesh_vertadr[mid]
    n = model.mesh_vertnum[mid]
    v = model.mesh_vert[a:a + n]
    R = data.geom_xmat[gid].reshape(3, 3)
    w = v @ R.T + data.geom_xpos[gid]
    return w.min(0), w.max(0), n


def compare(stock_name, ours_name, tol_mm):
    """Compile both, put both at the INIT keyframe (zero joints), compare the world
    bbox of each re-pointed visual geom with the stock geom at the same index."""
    import mujoco
    ms, _ = common.load_model(stock_name)
    mo, _ = common.load_model(ours_name)
    assert ms.ngeom == mo.ngeom, (ms.ngeom, mo.ngeom)
    assert ms.nbody == mo.nbody and np.allclose(ms.body_mass, mo.body_mass) and np.allclose(ms.body_inertia, mo.body_inertia), \
        "masses/inertias differ — they must not (explicit <inertial> in every body)"
    ds, do = mujoco.MjData(ms), mujoco.MjData(mo)
    kid = mujoco.mj_name2id(ms, mujoco.mjtObj.mjOBJ_KEY, "INIT")
    mujoco.mj_resetDataKeyframe(ms, ds, kid)
    mujoco.mj_resetDataKeyframe(mo, do, kid)
    mujoco.mj_forward(ms, ds)
    mujoco.mj_forward(mo, do)
    rows = []
    worst = 0.0
    for g in range(ms.ngeom):
        if ms.geom_type[g] != mujoco.mjtGeom.mjGEOM_MESH:
            continue
        mesh_o = mujoco.mj_id2name(mo, mujoco.mjtObj.mjOBJ_MESH, mo.geom_dataid[g])
        mesh_s = mujoco.mj_id2name(ms, mujoco.mjtObj.mjOBJ_MESH, ms.geom_dataid[g])
        if not mesh_o.endswith("__ours"):
            assert mesh_o == mesh_s, (g, mesh_o, mesh_s)
            continue
        lo_s, hi_s, n_s = geom_world_bbox(ms, ds, g)
        lo_o, hi_o, n_o = geom_world_bbox(mo, do, g)
        d = np.abs(np.concatenate([lo_o - lo_s, hi_o - hi_s])) * 1000.0
        worst = max(worst, float(d.max()))
        body = mujoco.mj_id2name(ms, mujoco.mjtObj.mjOBJ_BODY, ms.geom_bodyid[g])
        rows.append({"geom": int(g), "body": body, "mesh": mesh_s, "stock_verts": int(n_s), "ours_verts": int(n_o),
                     "bbox_delta_mm": [round(float(x), 3) for x in d], "max_delta_mm": round(float(d.max()), 3),
                     "contype": int(ms.geom_contype[g]), "conaffinity": int(ms.geom_conaffinity[g])})
    bad = [r for r in rows if r["max_delta_mm"] > tol_mm]
    return rows, worst, bad


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tol", type=float, default=1.5, help="bbox tolerance per swapped geom, mm")
    ap.add_argument("--report", default=os.path.join(common.OUT_DIR, "swap_report.json"))
    args = ap.parse_args()

    os.makedirs(MESH_OUT, exist_ok=True)
    os.makedirs(common.OUT_DIR, exist_ok=True)
    m2p, by_ref = mesh_map()
    slugs = passed_slugs()
    swapped, manifest, skipped = {}, {}, []
    for slug in slugs:
        ref = resolve_ref(slug, by_ref)
        if ref is None:
            skipped.append({"slug": slug, "why": "no mesh maps to this part in spec/mesh-to-part.json"})
            continue
        for mesh in by_ref[ref]:
            best = newest_pass_report(ref, mesh)
            if best is None:
                skipped.append({"slug": slug, "mesh": mesh, "why": "PASS in watch-pass.log but no PASS refcheck report.json found"})
                continue
            when, rpt, r = best
            dst = os.path.join(MESH_OUT, mesh + ".stl")
            ntri = to_binary_stl(r["ours"], dst)   # MuJoCo's decoder wants binary STL
            swapped[mesh] = dst
            manifest[mesh] = {"slug": slug, "part": ref, "source": os.path.relpath(r["ours"], ROOT),
                              "report": os.path.relpath(rpt, ROOT), "when": when,
                              "p95_mm": [r["shape"]["ref_to_cand"]["p95_mm"], r["shape"]["cand_to_ref"]["p95_mm"]],
                              "refcheck_bbox_delta_mm": r["shape"].get("bbox_delta_mm"),
                              "triangles": ntri, "source_sha256": sha256(r["ours"]),
                              "sha256": sha256(dst), "bytes": os.path.getsize(dst)}
    if not swapped:
        raise SystemExit("nothing to swap")
    json.dump(manifest, open(os.path.join(MESH_OUT, "manifest.json"), "w"), indent=1)

    outs = {}
    for base, dst in (("walk", common.ROBOT_FILES["ours"]),
                      ("allcollisions", common.ROBOT_FILES["ours_allcollisions"])):
        rep = write_swapped(common.ROBOT_FILES[base], dst, swapped)
        outs[base] = {"file": os.path.relpath(dst, ROOT), "repointed_geoms": len(rep)}
        print("wrote %s: %d visual geoms re-pointed" % (os.path.relpath(dst, ROOT), len(rep)))

    print("swapped meshes (%d):" % len(swapped))
    for mesh in sorted(swapped):
        mf = manifest[mesh]
        print("  %-26s <- %s  (%s, p95 %s mm)" % (mesh, mf["source"], mf["slug"], mf["p95_mm"]))
    if skipped:
        print("skipped:")
        for s in skipped:
            print("  ", s)

    results = {}
    ok = True
    for stock, ours in (("walk", "ours"), ("allcollisions", "ours_allcollisions")):
        rows, worst, bad = compare(stock, ours, args.tol)
        results[ours] = {"stock": stock, "geoms": rows, "worst_bbox_delta_mm": round(worst, 3),
                         "tol_mm": args.tol, "pass": not bad}
        print("%s vs %s: %d re-pointed geoms compile, worst zero-pose bbox delta %.3f mm (tol %.1f) -> %s"
              % (ours, stock, len(rows), worst, args.tol, "PASS" if not bad else "FAIL"))
        for r in bad:
            print("   OVER TOL:", r)
            ok = False
    report = {"swapped": sorted(swapped), "manifest": manifest, "skipped": skipped, "models": outs,
              "bbox_check": results, "collision_geoms": "stock (only class=visual geoms re-pointed)",
              "inertials": "stock (explicit <inertial> per body, asserted equal)"}
    json.dump(report, open(args.report, "w"), indent=1)
    print("report:", os.path.relpath(args.report, ROOT))
    if not ok:
        raise SystemExit("bbox check failed")


if __name__ == "__main__":
    main()
