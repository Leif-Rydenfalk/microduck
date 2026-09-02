#!/usr/bin/env python3
"""Export everything the interactive microduck viewer needs, from the files
that are already the truth on this machine:

  sim/microduck_ours.xml            the kinematic tree, the 14 hinges, 70 visual
                                    geoms, and which mesh each one draws
  ce-assemblies/.../joints.json     the MEASURED world origin + axis + range of
                                    every hinge (cross-checked against the MJCF)
  spec/mesh-to-part.json            mesh name -> triad part ref -> dashboard card
  out/sim/scene_walk_ours.xml       the STAND / SIT / FOLD / INIT keyframes
  out/sim/*_traj.npz                recorded MuJoCo qpos, 50 Hz

Writes into ce-cad/out/web/microduck/ (the dashboard's own served tree — the
same choice the publish step made, so every url the page emits is a url the
dashboard can actually answer):

  scene.json        bodies, hinges, geoms, poses, part links       (~60 kB)
  geom.bin          welded float32 positions + uint16 indices      (~5 MB)
  traj-<name>.json  per-frame root pose + 14 joint angles

Pure python3: xml.etree, struct, zipfile. No MuJoCo, no numpy, no FreeCAD, so
it runs in one second and anyone can re-run it.

  python3 tools/export_viewer.py [--out DIR]
"""
import argparse, json, math, os, struct, sys, time, zipfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from mjcf_scene import parse, read_stl  # noqa: E402

MJCF = os.path.join(DESIGN, "sim", "microduck_ours.xml")
JOINTS = os.path.join(DESIGN, "ce-assemblies", "microduck", "current", "joints.json")
MESH2PART = os.path.join(DESIGN, "spec", "mesh-to-part.json")
SCENE_KEY = os.path.join(DESIGN, "out", "sim", "scene_walk_ours.xml")
SIMDIR = os.path.join(DESIGN, "out", "sim")
DEFAULT_OUT = "/Users/leifrydenfalk/dev/ce-workshop/ce-cad/out/web/microduck"

# The trajectories worth carrying into the browser. Each is (file stem, label).
TRAJ = [
    ("walk_ours", "Walk — our parts, alpha_walking policy, vx 0.25 m/s"),
    ("sitstand_ours", "Sit / stand cycle — our parts"),
    ("stand_from_sit_ours", "Stand up from SIT"),
    ("stand_from_fold_ours", "Stand up from FOLD"),
    ("stand_hold_ours", "Stand and hold"),
    ("walk_stock", "Walk — Pollen's stock parts (comparison)"),
]


# ---------------------------------------------------------------- quaternions
def qmul(a, b):
    w1, x1, y1, z1 = a
    w2, x2, y2, z2 = b
    return (w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
            w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
            w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
            w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2)


def qrot(q, v):
    w, x, y, z = q
    vx, vy, vz = v
    # t = 2 * (q_vec x v);  v' = v + w*t + q_vec x t
    tx = 2 * (y * vz - z * vy)
    ty = 2 * (z * vx - x * vz)
    tz = 2 * (x * vy - y * vx)
    return (vx + w * tx + (y * tz - z * ty),
            vy + w * ty + (z * tx - x * tz),
            vz + w * tz + (x * ty - y * tx))


# --------------------------------------------------------------- .npy reading
def read_npy(blob):
    """Minimal .npy -> (shape, list of floats). Only the little-endian numeric
    dtypes these trajectories actually use."""
    if blob[:6] != b"\x93NUMPY":
        raise ValueError("not a .npy")
    major = blob[6]
    if major == 1:
        hlen = struct.unpack_from("<H", blob, 8)[0]
        start = 10
    else:
        hlen = struct.unpack_from("<I", blob, 8)[0]
        start = 12
    header = blob[start:start + hlen].decode("latin1")
    d = eval(header, {"__builtins__": {}}, {})  # a numpy header is a dict literal
    if d["fortran_order"]:
        raise ValueError("fortran-order array")
    descr = d["descr"]
    fmt = {"<f8": "d", "<f4": "f", "<i8": "q", "<i4": "i"}.get(descr)
    if fmt is None:
        return d["shape"], None  # a string/object array; the caller skips it
    body = blob[start + hlen:]
    n = len(body) // struct.calcsize(fmt)
    vals = struct.unpack("<" + fmt * n, body[:n * struct.calcsize(fmt)])
    return d["shape"], list(vals)


# ------------------------------------------------------------------ keyframes
def read_keyframes(path):
    src = open(path, "r", encoding="utf-8").read()
    # scene_walk_ours.xml is one long line; parse just the <keyframe> element.
    i = src.find("<keyframe>")
    if i < 0:
        return {}
    j = src.find("</keyframe>", i) + len("</keyframe>")
    el = ET.fromstring(src[i:j])
    out = {}
    for k in el.findall("key"):
        out[k.get("name")] = [float(x) for x in k.get("qpos").split()]
    return out


# ----------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    args = ap.parse_args()
    out = args.out
    os.makedirs(out, exist_ok=True)

    root, by_name, meshes, materials = parse(MJCF)
    mesh2part = json.load(open(MESH2PART))["map"]
    measured = json.load(open(JOINTS))["record"]["rows"]
    by_joint = {r["params"]["joint"]: r for r in measured}

    # ---- body list in MJCF tree order == MuJoCo qpos order -------------------
    bodies, jointrows, order = [], [], []

    def visit(b, parent_world_pos, parent_world_quat):
        wq = qmul(tuple(parent_world_quat), tuple(b.quat))
        wp = tuple(p + o for p, o in zip(parent_world_pos, qrot(tuple(parent_world_quat), tuple(b.pos))))
        hinge = None
        for j in b.joints:
            if j["type"] != "hinge":
                continue
            order.append(j["name"])
            axis_world = qrot(wq, tuple(j["axis"]))
            m = by_joint.get(j["name"])
            rng_deg = [math.degrees(x) for x in j["range"]] if j["range"] else None
            row = {
                "name": j["name"],
                "body": b.name,
                "parent_body": b.parent,
                "axis_local": [round(x, 6) for x in j["axis"]],
                "axis_world_zero": [round(x, 6) for x in axis_world],
                "origin_world_mm": [round(x * 1000, 3) for x in wp],
                "range_deg": [round(x, 3) for x in rng_deg] if rng_deg else None,
            }
            if m:
                p = m["params"]
                row["measured_origin_world_mm"] = p["world_origin_mm"]
                row["measured_axis_world"] = p["world_axis"]
                row["measured_range_deg"] = p["range_deg"]
                row["connection"] = m["connection"]
                row["driven_by"] = m["a"]["ref"]
                row["turns"] = m["b"]["ref"]
                # MEASURE, DON'T ASSERT: state the disagreement if there is one.
                # joints.json quotes the world pose with the robot's root at
                # z=+120 mm (the MJCF's own trunk_base pos); so does this walk.
                d = max(abs(a - bb) for a, bb in zip(row["origin_world_mm"], p["world_origin_mm"]))
                dot = sum(a * bb for a, bb in zip(axis_world, p["world_axis"]))
                row["agreement"] = {
                    "origin_max_delta_mm": round(d, 3),
                    "axis_dot": round(dot, 6),
                    "verdict": "AGREES" if d < 0.51 and abs(abs(dot) - 1) < 1e-3 else "DIFFERS",
                }
            hinge = row
            jointrows.append(row)
        bodies.append({
            "name": b.name,
            "parent": b.parent,
            "pos": [round(x, 9) for x in b.pos],
            "quat": [round(x, 9) for x in b.quat],
            "joint": hinge["name"] if hinge else None,
            "joint_axis": hinge["axis_local"] if hinge else None,
            "range_deg": hinge["range_deg"] if hinge else None,
        })
        for c in b.children:
            visit(c, wp, wq)

    visit(root, (0.0, 0.0, 0.0), (1.0, 0.0, 0.0, 0.0))

    # ---- geometry ----------------------------------------------------------
    used = []
    for b in bodies:
        for g in by_name[b["name"]].geoms:
            if g["mesh"] not in used:
                used.append(g["mesh"])

    buf = bytearray()
    meshindex = []
    for mname in used:
        path, scale = meshes[mname]
        verts, tris = read_stl(path, scale)
        nv, nt = len(verts) // 3, len(tris) // 3
        if nv > 65535:
            raise ValueError(f"{mname}: {nv} verts needs uint32 indices; not written")
        while len(buf) % 4:
            buf.append(0)
        pos_off = len(buf)
        buf += struct.pack("<%df" % len(verts), *verts)
        idx_off = len(buf)
        buf += struct.pack("<%dH" % len(tris), *tris)
        meshindex.append({
            "name": mname,
            "verts": nv, "tris": nt,
            "pos_off": pos_off, "idx_off": idx_off,
            "file": os.path.relpath(path, DESIGN),
            "ours": mname.endswith("__ours"),
        })
    mesh_id = {m["name"]: i for i, m in enumerate(meshindex)}

    geoms = []
    for b in bodies:
        for g in by_name[b["name"]].geoms:
            base = g["mesh"][:-6] if g["mesh"].endswith("__ours") else g["mesh"]
            ref = mesh2part.get(base)
            rgba = materials.get(g["material"], [0.7, 0.7, 0.7, 1.0])
            geoms.append({
                "id": f"{b['name']}.{len(geoms)}.{g['mesh']}",
                "body": b["name"],
                "mesh": mesh_id[g["mesh"]],
                "pos": [round(x, 9) for x in g["pos"]],
                "quat": [round(x, 9) for x in g["quat"]],
                "color": [round(x, 6) for x in rgba[:3]],
                "opacity": round(rgba[3], 4),
                "ref": ref,
                "model": ref.split(":", 1)[1] if ref else None,
                "label": (base.replace("__", " ").replace("_", " ")),
                "ours": g["mesh"].endswith("__ours"),
            })

    keys = read_keyframes(SCENE_KEY)
    poses = {}
    for name, q in keys.items():
        if len(q) != 7 + len(order):
            continue
        poses[name] = {
            "root_pos": [round(x, 6) for x in q[0:3]],
            "root_quat": [round(x, 6) for x in q[3:7]],
            "joints_deg": {order[i]: round(math.degrees(q[7 + i]), 4) for i in range(len(order))},
        }
    # ZERO is not in the MJCF; it is the definition of the slider home.
    poses["ZERO"] = {"root_pos": [0, 0, 0.12], "root_quat": [1, 0, 0, 0],
                     "joints_deg": {n: 0.0 for n in order}}

    scene = {
        "$comment": "generated by ce-designs/microduck/tools/export_viewer.py — "
                    "do not hand-edit; re-run the tool",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": {
            "mjcf": os.path.relpath(MJCF, DESIGN),
            "joints": os.path.relpath(JOINTS, DESIGN),
            "keyframes": os.path.relpath(SCENE_KEY, DESIGN),
            "mesh_to_part": os.path.relpath(MESH2PART, DESIGN),
            "design_root": DESIGN,
        },
        "units": {"length": "m in geometry and body pos, mm quoted in joint rows",
                  "angle": "deg in joints_deg and sliders, rad in the MJCF"},
        "bin": "geom.bin",
        "bin_bytes": len(buf),
        "meshes": meshindex,
        "bodies": bodies,
        "geoms": geoms,
        "joint_order": order,
        "joints": jointrows,
        "poses": poses,
        "totals": {
            "bodies": len(bodies), "hinges": len(jointrows), "geoms": len(geoms),
            "distinct_meshes": len(meshindex),
            "triangles": sum(m["tris"] for m in meshindex),
            "triangles_drawn": sum(meshindex[g["mesh"]]["tris"] for g in geoms),
        },
    }

    open(os.path.join(out, "geom.bin"), "wb").write(bytes(buf))
    json.dump(scene, open(os.path.join(out, "scene.json"), "w"), indent=1)

    # ---- trajectories -------------------------------------------------------
    manifest = []
    for stem, label in TRAJ:
        npz = os.path.join(SIMDIR, f"{stem}_traj.npz")
        if not os.path.exists(npz):
            manifest.append({"name": stem, "label": label, "status": "MISSING", "file": None})
            continue
        z = zipfile.ZipFile(npz)
        shape, qpos = read_npy(z.read("qpos.npy"))
        _, tsec = read_npy(z.read("time.npy"))
        nfr, nq = shape
        if nq != 7 + len(order):
            manifest.append({"name": stem, "label": label,
                             "status": f"SKIPPED — qpos width {nq}, tree needs {7+len(order)}",
                             "file": None})
            continue
        frames = []
        for f in range(nfr):
            row = qpos[f * nq:(f + 1) * nq]
            frames.append([round(row[0], 5), round(row[1], 5), round(row[2], 5),
                           round(row[3], 6), round(row[4], 6), round(row[5], 6), round(row[6], 6)]
                          + [round(math.degrees(x), 3) for x in row[7:]])
        summ_path = os.path.join(SIMDIR, f"{stem}_summary.json")
        summ = json.load(open(summ_path)) if os.path.exists(summ_path) else {}
        dt = (tsec[-1] - tsec[0]) / max(1, nfr - 1) if tsec else 0.02
        traj = {
            "name": stem, "label": label,
            "source": os.path.relpath(npz, DESIGN),
            "frames": nfr, "dt_s": round(dt, 6), "hz": round(1 / dt, 3) if dt else None,
            "duration_s": round(tsec[-1] - tsec[0], 4) if tsec else None,
            "layout": "per frame: [root_x_m, root_y_m, root_z_m, qw, qx, qy, qz, "
                      "then one degree value per joint in joint_order]",
            "joint_order": order,
            "summary": {k: summ.get(k) for k in
                        ("policy", "policy_file", "robot", "walked_m", "walked_x_m",
                         "walked_y_m", "mean_speed_m_s_commanded_window",
                         "final_yaw_deg", "trunk_z_m", "seconds", "control_hz",
                         "start_keyframe", "command", "verdict", "checks")
                        if k in summ},
            "data": frames,
        }
        fn = f"traj-{stem}.json"
        json.dump(traj, open(os.path.join(out, fn), "w"), separators=(",", ":"))
        manifest.append({"name": stem, "label": label, "status": "OK", "file": fn,
                         "frames": nfr, "hz": traj["hz"], "duration_s": traj["duration_s"],
                         "policy": summ.get("policy_file"), "robot": summ.get("robot"),
                         "walked_m": summ.get("walked_m")})
    json.dump({"trajectories": manifest}, open(os.path.join(out, "trajectories.json"), "w"), indent=1)

    # ---- what it wrote, out loud -------------------------------------------
    print(f"out: {out}")
    print(f"  geom.bin      {len(buf):>9,} B   {len(meshindex)} meshes, "
          f"{scene['totals']['triangles']:,} unique tris, "
          f"{scene['totals']['triangles_drawn']:,} drawn over {len(geoms)} geoms")
    print(f"  scene.json    {os.path.getsize(os.path.join(out,'scene.json')):>9,} B   "
          f"{len(bodies)} bodies, {len(jointrows)} hinges, poses: {', '.join(sorted(poses))}")
    bad = [r for r in jointrows if r.get("agreement", {}).get("verdict") == "DIFFERS"]
    ok = [r for r in jointrows if r.get("agreement", {}).get("verdict") == "AGREES"]
    print(f"  hinge cross-check vs joints.json: {len(ok)} AGREE, {len(bad)} DIFFER, "
          f"{len(jointrows)-len(ok)-len(bad)} not in joints.json")
    for r in bad:
        print(f"    DIFFERS {r['name']}: origin delta {r['agreement']['origin_max_delta_mm']} mm, "
              f"axis dot {r['agreement']['axis_dot']}  mjcf={r['origin_world_mm']} "
              f"measured={r['measured_origin_world_mm']}")
    for m in manifest:
        print(f"  {m['file'] or '-':<32} {m['status']:<10} {m.get('frames','')} frames  {m['label']}")


if __name__ == "__main__":
    main()
