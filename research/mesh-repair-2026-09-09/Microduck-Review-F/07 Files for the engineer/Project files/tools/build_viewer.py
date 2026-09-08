#!/usr/bin/env python3
"""Build the interactive microduck viewer's data files.

Reads the ground-truth MJCF kinematic tree (reference/pollen-microduck-rl/robot_walk.xml)
and the recorded MuJoCo trajectories (out/sim/*_traj.npz), and writes, into every
output directory given on the command line:

  scene.json          the body tree: per body pos/quat (relative to parent),
                      its hinge joint (name/axis/range), and its visual geoms
                      (mesh file, local pos/quat, colour, triad part ref).
  traj/<name>.json    per-frame base pose + 14 joint angles for each policy run.
  assets/*.stl        the unique STL meshes the scene references, copied in.
  parts.json          mesh -> triad part ref + human label, for the parts panel.

Run under bin/cad (needs numpy):
  bin/cad tools/build_viewer.py OUTDIR [OUTDIR2 ...]

Everything the browser needs is plain JSON + STL; the page does the kinematics.
The MJCF is authoritative: joint angles here index the same qpos order MuJoCo
used to record the trajectories, so play-back is exact, not re-derived.
"""
import sys, os, json, math, shutil, struct
import xml.etree.ElementTree as ET
import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MJCF = os.path.join(HERE, "reference/pollen-microduck-rl/robot_walk.xml")
ASSETS = os.path.join(HERE, "reference/pollen-microduck-rl/assets")
MESH2PART = os.path.join(HERE, "spec/mesh-to-part.json")
SIMDIR = os.path.join(HERE, "out/sim")

# trajectories to export: (npz stem, label shown in the UI)
TRAJ = [
    ("walk_ours",           "Walk — our mesh (RL policy)"),
    ("sitstand_ours",       "Sit -> stand -> sit"),
    ("stand_from_sit_ours", "Stand up from sit"),
    ("walk_stock",          "Walk — stock (Pollen) mesh"),
]


def f3(s):
    return [float(x) for x in s.split()]


def load_materials(root):
    mats = {}
    for m in root.iter("material"):
        rgba = f3(m.get("rgba", "0.8 0.8 0.8 1"))
        mats[m.get("name")] = rgba
    return mats


def walk_bodies(body, parent_name, mats, out, joint_order):
    name = body.get("name")
    pos = f3(body.get("pos", "0 0 0"))
    quat = f3(body.get("quat", "1 0 0 0"))  # wxyz
    joint = None
    for j in body.findall("joint"):
        if j.get("type") == "hinge":
            rng = f3(j.get("range", "0 0"))
            joint = {
                "name": j.get("name"),
                "axis": f3(j.get("axis", "0 0 1")),
                "range_rad": rng,
                "range_deg": [math.degrees(rng[0]), math.degrees(rng[1])],
            }
            joint_order.append(j.get("name"))
    geoms = []
    for g in body.findall("geom"):
        if g.get("type") != "mesh":
            continue
        if g.get("class") != "visual":   # skip collision / self_collision_only duplicates
            continue
        mesh = g.get("mesh")
        matname = g.get("material", "")
        rgba = mats.get(matname, [0.8, 0.8, 0.8, 1])
        geoms.append({
            "mesh": mesh,
            "pos": f3(g.get("pos", "0 0 0")),
            "quat": f3(g.get("quat", "1 0 0 0")),
            "color": [round(rgba[0], 4), round(rgba[1], 4), round(rgba[2], 4)],
            "opacity": round(rgba[3], 3) if len(rgba) > 3 else 1.0,
        })
    out.append({
        "name": name,
        "parent": parent_name,
        "pos": [round(v, 6) for v in pos],
        "quat": [round(v, 6) for v in quat],
        "joint": joint,
        "geoms": geoms,
    })
    for child in body.findall("body"):
        walk_bodies(child, name, mats, out, joint_order)


def build_scene():
    tree = ET.parse(MJCF)
    root = tree.getroot()
    mats = load_materials(root)
    world = root.find("worldbody")
    trunk = world.find("body")  # single root body: trunk_base
    root_pos = f3(trunk.get("pos", "0 0 0"))
    root_quat = f3(trunk.get("quat", "1 0 0 0"))
    bodies = []
    joint_order = []
    walk_bodies(trunk, None, mats, bodies, joint_order)
    # meshes referenced
    meshes = sorted({g["mesh"] for b in bodies for g in b["geoms"]})
    return {
        "units": "meters",
        "up": "z",
        "root_pos": [round(v, 6) for v in root_pos],
        "root_quat": [round(v, 6) for v in root_quat],
        "bodies": bodies,
        "joint_order": joint_order,   # matches qpos[7:] order in the trajectories
        "meshes": meshes,
    }, joint_order


def build_parts():
    m2p = json.load(open(MESH2PART))["map"]
    parts = {}
    for mesh, ref in m2p.items():
        label = ref.replace("part:microduck-", "").replace("part:", "").replace("-", " ")
        parts[mesh] = {"ref": ref, "label": label}
    return parts


def export_traj(stem, label, joint_order):
    path = os.path.join(SIMDIR, f"{stem}_traj.npz")
    if not os.path.exists(path):
        return None
    d = np.load(path, allow_pickle=True)
    q = d["qpos"]            # (N, 21) = 3 pos + 4 quat(wxyz) + 14 hinge
    dt = float(d["ctrl_dt"])
    n = q.shape[0]
    base_pos = [[round(float(v), 5) for v in q[i, 0:3]] for i in range(n)]
    base_quat = [[round(float(v), 5) for v in q[i, 3:7]] for i in range(n)]
    joints = [[round(float(v), 5) for v in q[i, 7:7 + len(joint_order)]] for i in range(n)]
    return {
        "name": stem,
        "label": label,
        "dt": dt,
        "fps": round(1.0 / dt, 2),
        "nframes": n,
        "joint_order": joint_order,
        "base_pos": base_pos,
        "base_quat": base_quat,
        "joints": joints,
    }


def write_all(outdir, scene, parts, trajs):
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(os.path.join(outdir, "traj"), exist_ok=True)
    adir = os.path.join(outdir, "assets")
    os.makedirs(adir, exist_ok=True)
    json.dump(scene, open(os.path.join(outdir, "scene.json"), "w"), separators=(",", ":"))
    json.dump(parts, open(os.path.join(outdir, "parts.json"), "w"), indent=1)
    index = []
    for t in trajs:
        if t is None:
            continue
        json.dump(t, open(os.path.join(outdir, "traj", t["name"] + ".json"), "w"), separators=(",", ":"))
        index.append({"name": t["name"], "label": t["label"], "nframes": t["nframes"], "fps": t["fps"]})
    json.dump(index, open(os.path.join(outdir, "traj", "index.json"), "w"), indent=1)
    copied = 0
    for mesh in scene["meshes"]:
        src = os.path.join(ASSETS, mesh + ".stl")
        if os.path.exists(src):
            shutil.copyfile(src, os.path.join(adir, mesh + ".stl"))
            copied += 1
    return copied, len(index)


def main():
    outdirs = sys.argv[1:]
    if not outdirs:
        print("usage: build_viewer.py OUTDIR [OUTDIR2 ...]", file=sys.stderr)
        sys.exit(2)
    scene, joint_order = build_scene()
    parts = build_parts()
    trajs = [export_traj(s, l, joint_order) for s, l in TRAJ]
    print(f"scene: {len(scene['bodies'])} bodies, {len(joint_order)} joints, "
          f"{len(scene['meshes'])} unique meshes")
    print("joint order:", joint_order)
    for t in trajs:
        if t:
            print(f"traj {t['name']}: {t['nframes']} frames @ {t['fps']} Hz")
    for outdir in outdirs:
        copied, ntraj = write_all(outdir, scene, parts, trajs)
        print(f"wrote {outdir}: {copied} STL, {ntraj} trajectories, scene.json, parts.json")


if __name__ == "__main__":
    main()
