#!/usr/bin/env python3
"""assembly_steps_mj.py — clean cumulative assembly-step renders via MuJoCo.
Leif, 2026-09-02: "step3.png looks shit." The old meshview steps z-fought on the
decimated meshes. This uses the same clean MuJoCo studio path as compare_render:
straight INIT pose, white studio, and for each step the not-yet-added bodies are
made transparent while the parts added THIS step are tinted orange and the ones
already placed are light grey. One clean shaded frame per step.
"""
import os, sys
os.environ.setdefault("MUJOCO_GL", "glfw")
import numpy as np, mujoco
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from compare_render import studio_scene

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out", "assembly")
os.makedirs(OUT, exist_ok=True)

STEPS = [
    ("1 · Trunk",  ["trunk_base"]),
    ("2 · Hips",   ["yaw2roll", "hip_l", "bearing_roll", "hip_l_2"]),
    ("3 · Legs",   ["upper_leg_left", "leg", "ankle_left", "upper_leg_right", "leg_2", "ankle_right"]),
    ("4 · Neck",   ["neck", "neck_pitch"]),
    ("5 · Head",   ["yaw_roll_motion", "jaw_soft"]),
]
GREY = (0.70, 0.72, 0.76, 1.0)
ORANGE = (0.93, 0.52, 0.13, 1.0)
HIDE = (0.0, 0.0, 0.0, 0.0)

def main():
    scene = studio_scene(common.robot_file("ours"))
    model = mujoco.MjModel.from_xml_string(scene, {})
    data = mujoco.MjData(model)
    kid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, "INIT")
    mujoco.mj_resetDataKeyframe(model, data, kid)
    mujoco.mj_forward(model, data)
    # every geom forced to explicit rgba (ignore its material) so we can recolour
    model.geom_matid[:] = -1
    W = H = 1400
    r = mujoco.Renderer(model, H, W)
    cam = mujoco.MjvCamera(); cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    cam.lookat[:] = [0.0, 0.0, 0.14]; cam.distance = 0.5
    cam.azimuth = 135.0; cam.elevation = -16.0
    opt = mujoco.MjvOption()
    bid = lambda n: mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, n)
    placed = set()
    for i, (title, bodies) in enumerate(STEPS, 1):
        new = {bid(b) for b in bodies}
        placed |= new
        for g in range(model.ngeom):
            b = model.geom_bodyid[g]
            model.geom_rgba[g] = ORANGE if b in new else (GREY if b in placed else HIDE)
        r.update_scene(data, cam, opt)
        Image.fromarray(r.render().copy()).save(os.path.join(OUT, "step%d.png" % i))
        print("wrote step%d.png (%s) new=%s" % (i, title, bodies))
    # fully assembled, all in product-ish grey/white
    for g in range(model.ngeom):
        model.geom_rgba[g] = GREY
    r.update_scene(data, cam, opt)
    Image.fromarray(r.render().copy()).save(os.path.join(OUT, "assembled.png"))
    print("wrote assembled.png")

if __name__ == "__main__":
    main()
