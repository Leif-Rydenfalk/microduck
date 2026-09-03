#!/usr/bin/env python3
"""tools/upstream_render.py — render Pollen's OWN robot_walk.xml with its OWN
material colours, old pin (5946fd9) beside develop (29e887e), same camera,
STAND keyframe, white studio. Run as ce-cad/bin/cad tools/upstream_render.py.
The MJCF numbers are identical between the two (upstream_mjcfdiff.json); the
only thing that moved is <material rgba>, and this is what that looks like.
Writes out/sources/render-{old,new}-{front,left,iso}.png and a side-by-side
out/sources/render-colours-old-vs-new.png with labels.
"""
import os, sys
import numpy as np, mujoco
from PIL import Image, ImageDraw, ImageFont
R = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck"
TREES = {"old": (f"{R}/reference/pollen-microduck-rl", "5946fd9 (our pin, 2026-09-01)"),
         "new": (f"{R}/reference/pollen-microduck-rl-develop/microduck", "develop 29e887e (2026-09-02)")}
OUT = f"{R}/out/sources"
STAND = "0 0 0.12 1 0 0 0 0 -0.08726646259971647 -0.457924 -0.004940 0.452984 0.3490658503988659 0.3490658503988659 0 0 0 0.08726646259971647 0.457924 0.004940 -0.452984"
SCENE = """<mujoco model="scene"><include file="robot_walk.xml"/>
<visual><headlight diffuse="0.7 0.7 0.7" ambient="0.35 0.35 0.35" specular="0.1 0.1 0.1"/><rgba haze="1 1 1 1"/><global offwidth="1200" offheight="1200"/></visual>
<asset><texture type="skybox" builtin="flat" rgb1="1 1 1" rgb2="1 1 1" width="32" height="32"/></asset>
<worldbody><light pos="0.3 0.3 1" dir="-0.3 -0.3 -1" diffuse="0.6 0.6 0.6"/><light pos="-0.4 0.2 0.8" dir="0.4 -0.2 -0.8" diffuse="0.4 0.4 0.4"/></worldbody>
<keyframe><key name="STAND" qpos="%s"/></keyframe></mujoco>""" % STAND
CAMS = {"front": (180, -8), "left": (270, -8), "iso": (225, -14)}
H = W = 900
imgs = {}
for tag, (tree, label) in TREES.items():
    xml = os.path.join(tree, "_scene_render.xml")
    open(xml, "w").write(SCENE)
    try:
        model = mujoco.MjModel.from_xml_path(xml)
    finally:
        os.remove(xml)
    data = mujoco.MjData(model)
    mujoco.mj_resetDataKeyframe(model, data, 0); mujoco.mj_forward(model, data)
    r = mujoco.Renderer(model, H, W)
    cam = mujoco.MjvCamera(); cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    cam.lookat[:] = [0.0, 0.0, 0.15]; cam.distance = 0.50
    opt = mujoco.MjvOption(); opt.geomgroup[:] = 0; opt.geomgroup[0] = 1; opt.geomgroup[1] = 1; opt.geomgroup[2] = 1
    for cname, (az, el) in CAMS.items():
        cam.azimuth, cam.elevation = float(az), float(el)
        r.update_scene(data, cam, opt)
        px = r.render()
        im = Image.fromarray(px)
        im.save(f"{OUT}/render-{tag}-{cname}.png")
        arr = np.asarray(im).astype(int); ink = float(((arr.sum(axis=2)) < 740).mean())
        print(tag, cname, "ink %.4f" % ink, flush=True)
        imgs[(tag, cname)] = im
    r.close()
# composite: rows old/new, cols front/left/iso
pad = 40
font = ImageFont.load_default()
comp = Image.new("RGB", (3 * W + 4 * pad, 2 * H + 3 * pad + 60), "white")
d = ImageDraw.Draw(comp)
for i, tag in enumerate(("old", "new")):
    y = pad + 30 + i * (H + pad)
    d.text((pad, y - 22), f"{tag.upper()}: {TREES[tag][1]} — robot_walk.xml material rgba, STAND keyframe", fill="black", font=font)
    for j, cname in enumerate(CAMS):
        comp.paste(imgs[(tag, cname)], (pad + j * (W + pad), y))
        d.text((pad + j * (W + pad), y + H + 4), f"{cname} az={CAMS[cname][0]} el={CAMS[cname][1]}", fill="black", font=font)
comp.save(f"{OUT}/render-colours-old-vs-new.png")
print("wrote", f"{OUT}/render-colours-old-vs-new.png", comp.size, flush=True)
