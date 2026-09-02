#!/usr/bin/env python3
"""head_probe.py — first look: frames of the head geoms, the jaw hinge axis, the
servo face that a profile camera sees, and one posed render (yaw/pitch/jaw open)."""
import os, sys, math, json
os.environ.setdefault("MUJOCO_GL", "glfw")
import numpy as np, mujoco
from PIL import Image
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "sim"))
import common, compare_render
OUT = os.path.join(REPO, "out", "head")

scene = compare_render.studio_scene(common.robot_file("ours"))
model = mujoco.MjModel.from_xml_string(scene, {})
data = mujoco.MjData(model)
kid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, "PHOTO")
mujoco.mj_resetDataKeyframe(model, data, kid)
mujoco.mj_forward(model, data)

def mesh_verts(gid):
    mid = model.geom_dataid[gid]
    a = model.mesh_vertadr[mid]; n = model.mesh_vertnum[mid]
    return model.mesh_vert[a:a+n].copy()

head_bid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "jaw_soft")
print("jaw_soft body id", head_bid)
for gid in range(model.ngeom):
    if model.geom_bodyid[gid] != head_bid: continue
    mid = model.geom_dataid[gid]
    name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_MESH, mid) if mid >= 0 else "?"
    v = mesh_verts(gid) * 1000.0  # mm in mesh frame (scale already applied by compiler)
    R = np.zeros(9); mujoco.mju_quat2Mat(R, model.geom_quat[gid]); R = R.reshape(3,3)
    vb = (R @ v.T).T + model.geom_pos[gid]*1000.0   # body frame, mm
    print("%-28s body-frame bbox mm  x[%8.3f %8.3f] y[%8.3f %8.3f] z[%8.3f %8.3f]" % (
        name, vb[:,0].min(), vb[:,0].max(), vb[:,1].min(), vb[:,1].max(), vb[:,2].min(), vb[:,2].max()))

# which mesh axis of the xl330 is the horn axis, and which face does a profile camera see?
# take the neck body's first xl330 geom (xl330_7)
neck_bid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "neck")
for gid in range(model.ngeom):
    if model.geom_bodyid[gid] != neck_bid: continue
    mid = model.geom_dataid[gid]
    name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_MESH, mid)
    if name != "xl330": continue
    v = mesh_verts(gid)*1000.0
    print("xl330 mesh-frame bbox mm", v.min(0).round(3), v.max(0).round(3))
    Rw = data.geom_xmat[gid].reshape(3,3)
    for ax, lab in enumerate("xyz"):
        print("  mesh %s axis in world: %s" % (lab, Rw[:,ax].round(3)))
    break
jid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, "neck_pitch")
print("neck_pitch axis world:", data.xaxis[jid].round(3))
for jn in ("head_pitch", "head_yaw", "head_roll"):
    jid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, jn)
    print(jn, "axis world:", data.xaxis[jid].round(3), "anchor:", (data.xanchor[jid]*1000).round(2))
