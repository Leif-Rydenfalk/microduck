"""head_sweep — prove the neck is alive: same mechanics, non-zero head commands.

Leif, 2026-09-02: "its neck looks a little stiff is it the same mechanically
exactly as the real thing?" The MJCF is Pollen's verbatim (axes, ranges, gains,
masses; stock-vs-ours trajectories bit-identical), and the stiffness in the
walk video is the COMMAND: schedule() drives twist only, head_pose cmd[3:7]
stays zero, and the policy holds the head level — exactly what the real robot
does with no gamepad head input. This script drives the head slots with sine
sweeps under the stand policy and MEASURES which joint answers each slot.

    /Applications/FreeCAD.app/Contents/Resources/bin/python sim/head_sweep.py
"""
import os, sys, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("MUJOCO_GL", "glfw")
import numpy as np
import common
from run_policy import Policy, Runner, POLICY_FILES, CTRL_DT, DECIMATION, NUM_JOINTS

import mujoco
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out", "sim")
model, scene_path = common.load_model("ours", os.path.join(OUT, "scene_head_sweep.xml"))
data = mujoco.MjData(model)
kid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, "STAND")
mujoco.mj_resetDataKeyframe(model, data, kid)
mujoco.mj_forward(model, data)
pol = Policy(os.path.join(common.POLICY_DIR, POLICY_FILES["stand"]))
run = Runner(model, data)

SECONDS = 10.0
n = int(SECONDS / CTRL_DT)
names = ["neck_pitch", "head_pitch", "head_yaw", "head_roll"]
jadr = {nm: int(model.jnt_qposadr[mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, nm)]) for nm in names}
frames, qlog, clog = [], [], []
ren = mujoco.Renderer(model, height=480, width=640)
cam = mujoco.MjvCamera(); cam.azimuth, cam.elevation, cam.distance = 135, -12, 0.62
cam.lookat[:] = [0.02, 0, 0.16]
for k in range(n):
    t = k * CTRL_DT
    # sweep one slot at a time, 2.5 s each: [0]=?, [1]=?, [2]=?, [3]=? — measured below
    ht = np.zeros(4, np.float32)
    slot = int(t // 2.5)
    amp = [0.5, 0.6, 1.2, 0.35][min(slot, 3)]
    ht[min(slot, 3)] = amp * math.sin(2 * math.pi * (t % 2.5) / 2.5)
    run.head_target = ht
    o = run.obs((0.0, 0.0, 0.0), None)
    a = pol(o)
    run.apply(a, pol.action_scale)
    for _ in range(DECIMATION):
        mujoco.mj_step(model, data)
    qlog.append([float(data.qpos[jadr[nm]]) for nm in names]); clog.append(ht.copy())
    if k % 5 == 0:
        ren.update_scene(data, cam)
        frames.append(ren.render().copy())
q = np.asarray(qlog); c = np.asarray(clog)
print("slot -> joint responses (peak |deg| per 2.5 s window):")
for slot in range(4):
    w = slice(int(slot*2.5/CTRL_DT), int((slot+1)*2.5/CTRL_DT))
    peaks = np.abs(np.degrees(q[w] - q[w][0])).max(axis=0)
    print("  cmd slot %d -> %s" % (slot, ", ".join("%s %.1f°" % (nm, p) for nm, p in zip(names, peaks))))
import imageio
mp4 = os.path.join(OUT, "head_sweep.mp4")
imageio.mimwrite(mp4, frames, fps=10, quality=8)
for i in (0, len(frames)//3, 2*len(frames)//3):
    imageio.imwrite(os.path.join(OUT, "frames", "head_sweep_%02d.png" % i), frames[i])
print("wrote", mp4, len(frames), "frames; trunk stayed up:", float(data.qpos[run.root_qadr+2]) > 0.09)
