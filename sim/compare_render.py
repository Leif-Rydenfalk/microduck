#!/usr/bin/env python3
"""compare_render.py — render OUR cad (the swapped __ours meshes) at the exact
STAND keyframe, on a white background, from a sweep of camera angles, so each
can be placed next to the official Pollen product photos at the same view.
Leif, 2026-09-02: "show renders of our cad version next to the same camera angle
of the official advertisement images ... for easy compare."

MuJoCo offscreen renderer (proper depth, no meshview speckle). White skybox, no
floor, headlight — a clean studio shot like the store photos.
"""
import os, sys
os.environ.setdefault("MUJOCO_GL", "glfw")
import numpy as np
import xml.etree.ElementTree as ET
import mujoco
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "out", "compare")
os.makedirs(OUT, exist_ok=True)

def studio_scene(robot_xml):
    """Like common.scene_xml but a clean white studio: white skybox, NO floor."""
    tree = ET.parse(robot_xml); root = tree.getroot()
    comp = root.find("compiler")
    meshdir = comp.get("meshdir", "assets") if comp is not None else "assets"
    robot_dir = os.path.dirname(os.path.abspath(robot_xml))
    if not os.path.isabs(meshdir):
        meshdir = os.path.normpath(os.path.join(robot_dir, meshdir))
    # give each rebuilt __ours geom its REAL product material (not the orange tag)
    mats = {m.get("name") for m in root.iter("material")}
    for g in root.iter("geom"):
        mesh = g.get("mesh") or ""
        if mesh.endswith("__ours") and g.get("material") == "ours_material":
            base = mesh[:-6] + "_material"
            if base in mats:
                g.set("material", base)
    if comp is None: comp = ET.SubElement(root, "compiler")
    comp.set("meshdir", meshdir); comp.set("angle", "radian"); comp.set("autolimits", "true")
    if root.find("option") is None: ET.SubElement(root, "option", timestep=str(common.TIMESTEP))
    vis = ET.SubElement(root, "visual")
    ET.SubElement(vis, "headlight", diffuse="0.85 0.85 0.85", ambient="0.55 0.55 0.55", specular="0.15 0.15 0.15")
    ET.SubElement(vis, "rgba", haze="1 1 1 1")
    ET.SubElement(vis, "quality", shadowsize="4096")
    ET.SubElement(vis, "global", offwidth="1600", offheight="1600")
    asset = root.find("asset") or ET.SubElement(root, "asset")
    ET.SubElement(asset, "texture", type="skybox", builtin="flat", rgb1="1 1 1", rgb2="1 1 1",
                  width="512", height="512")
    wb = root.find("worldbody")
    ET.SubElement(wb, "light", pos="0.5 -0.6 1.2", dir="-0.4 0.5 -1", directional="true",
                  diffuse="0.7 0.7 0.7", castshadow="false")
    ET.SubElement(wb, "light", pos="-0.5 0.4 0.9", dir="0.4 -0.3 -1", directional="true",
                  diffuse="0.4 0.4 0.4", castshadow="false")
    kf = ET.SubElement(root, "keyframe")
    # PHOTO pose: STAND legs, but the head only gently down (store photo gaze,
    # not STAND's 40deg forward tilt). neck_pitch idx5, head_pitch idx6.
    import numpy as _np
    pp = common.DEFAULT_POSE.copy(); pp[5] = 0.12; pp[6] = 0.10
    qp = "0 0 0.12 1 0 0 0 " + " ".join("%.10g" % v for v in pp)
    ET.SubElement(kf, "key", name="PHOTO", qpos=qp, ctrl=" ".join("%.10g" % v for v in pp))
    for name, (qpos, ctrl) in common.KEYFRAMES.items():
        ET.SubElement(kf, "key", name=name, qpos=qpos, ctrl=ctrl)
    return ET.tostring(root, encoding="unicode")

def main():
    scene = studio_scene(common.robot_file("ours"))
    open(os.path.join(OUT, "_studio_scene.xml"), "w").write(scene)
    model = mujoco.MjModel.from_xml_string(scene, {})  # meshes via meshdir on disk
    data = mujoco.MjData(model)
    kid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, "PHOTO")
    mujoco.mj_resetDataKeyframe(model, data, kid)
    mujoco.mj_forward(model, data)
    W = H = 1400
    r = mujoco.Renderer(model, H, W)
    cam = mujoco.MjvCamera(); cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    # frame the whole standing robot: it spans roughly z 0.02..0.30, x -0.1..0.1
    cam.lookat[:] = [0.0, 0.0, 0.16]; cam.distance = 0.46
    opt = mujoco.MjvOption()
    views = {"front": (0, -8), "prof-right": (90, -8), "back": (180, -8),
             "prof-left": (270, -8), "iso-fl": (45, -18), "iso-fr": (135, -18),
             "iso-bl": (315, -18), "top": (0, -80)}
    for name, (az, el) in views.items():
        cam.azimuth = float(az); cam.elevation = float(el)
        r.update_scene(data, cam, opt)
        px = r.render().copy()
        Image.fromarray(px).save(os.path.join(OUT, "ours-%s.png" % name))
        print("wrote ours-%s.png az=%s el=%s" % (name, az, el))
    # --- joint close-ups: proof the constraint detail is real, aimed at a joint ---
    def bpos(name):
        bid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, name)
        return np.array(data.xpos[bid], float)
    joints = {
        "joint-knee":  ("leg",            90, -6, 0.17),   # left_knee: XL330 + horn + leg/ankle
        "joint-hip":   ("upper_leg_left", 60, -10, 0.19),  # hip pitch cluster
        "joint-ankle": ("ankle_left",     90, -4, 0.16),
        "joint-neck":  ("neck",           75, -2, 0.17),
    }
    for name, (body, az, el, dist) in joints.items():
        cam.lookat[:] = bpos(body); cam.azimuth = float(az); cam.elevation = float(el)
        cam.distance = float(dist)
        r.update_scene(data, cam, opt)
        Image.fromarray(r.render().copy()).save(os.path.join(OUT, "ours-%s.png" % name))
        print("wrote ours-%s.png (lookat %s)" % (name, body))
    print("done ->", OUT)

if __name__ == "__main__":
    main()
