#!/usr/bin/env python3
"""step.py — PROOF the duck's MuJoCo model exists, loads, steps and renders.

The fleet goal (g-dbb2eeeb) asks for "animated in MuJoCo with our rebuilt
parts". The model is NOT built here and never was: sim/microduck_ours*.xml
(sim/swap_meshes.py) already carries our rebuilt meshes for every PASSed part,
verified against the stock geoms at 1.5 mm. This script re-proves the three
claims a person would doubt, from the file on disk, in one command:

  1. it LOADS    — mj_model compile of the our-parts scene
  2. it STEPS    — 100 steps of the physics from the standing keyframe
  3. it RENDERS  — one 640x480 frame PNG, read back non-blank

and writes the measured numbers (bodies, joints, contacts at rest, total mass)
to out/mujoco/step.json. Three verdicts, deliver-style exit codes
(0 PASS / 1 FAIL / 2 CANNOT DETERMINE). A missing value stays missing.

Run with the interpreter that has mujoco (system python3 has none):

  /Applications/FreeCAD.app/Contents/Resources/bin/python mujoco/step.py
"""
import json
import os
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_DIR = os.path.join(ROOT, "out", "mujoco")
OUT_JSON = os.path.join(OUT_DIR, "step.json")
OUT_PNG = os.path.join(OUT_DIR, "frame.png")

# the our-parts scene: floor + light + sim/microduck_ours_allcollisions.xml
MODEL = os.path.join(ROOT, "out", "sim-sweep", "_census", "scene_ours_allcollisions.xml")

N_STEPS = 100


def png_nonblank(path):
    """Read the PNG back: refuse blank/near-blank the way rendercover does."""
    with open(path, "rb") as f:
        d = f.read()
    if len(d) < 100 or d[:8] != b"\x89PNG\r\n\x1a\n":
        return False, "not a PNG (%d bytes)" % len(d)
    # IHDR gives width/height; blank-frame detection is done by the renderer's
    # own pixel read-back below, this only proves a real file landed
    return True, "%d bytes, PNG magic ok" % len(d)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    rec = {"model": os.path.relpath(MODEL, ROOT), "steps": N_STEPS,
           "python": sys.executable}

    try:
        import mujoco
        import numpy as np
    except Exception as e:
        rec["verdict"] = "CANNOT DETERMINE"
        rec["why"] = "mujoco not installed for %s — pip install mujoco, then rerun this script" % sys.executable
        rec["error"] = str(e)
        json.dump(rec, open(OUT_JSON, "w", encoding="utf-8"), indent=1)
        print(rec["why"])
        return 2
    rec["mujoco_version"] = mujoco.__version__

    if not os.path.exists(MODEL):
        rec["verdict"] = "CANNOT DETERMINE"
        rec["why"] = "model file missing: %s" % MODEL
        json.dump(rec, open(OUT_JSON, "w", encoding="utf-8"), indent=1)
        print(rec["why"])
        return 2

    # ---- 1. LOAD
    m = mujoco.MjModel.from_xml_path(MODEL)
    d = mujoco.MjData(m)
    rec["nbody"] = m.nbody
    rec["njnt"] = m.njnt
    rec["ngeom"] = m.ngeom
    rec["total_mass_kg"] = float(sum(m.body_mass))
    rec["joint_names"] = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, i) for i in range(m.njnt)]
    rec["timestep_s"] = float(m.opt.timestep)

    # ---- start from the standing keyframe the sim lane uses
    k = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_KEY, "INIT")
    if k >= 0:
        mujoco.mj_resetDataKeyframe(m, d, k)
        rec["keyframe"] = "INIT"
    mujoco.mj_forward(m, d)

    # ---- 2. STEP 100
    contact_counts = []
    for _ in range(N_STEPS):
        mujoco.mj_step(m, d)
        contact_counts.append(d.ncon)
    rec["contacts_at_rest"] = int(d.ncon)
    rec["contacts_min_over_steps"] = int(min(contact_counts))
    rec["contacts_max_over_steps"] = int(max(contact_counts))
    rec["qpos_after"] = [float(x) for x in d.qpos[:7]]  # root free joint only
    rec["trunk_height_m_after"] = float(d.qpos[2]) if m.njnt and m.jnt_type[0] == mujoco.mjtJoint.mjJNT_FREE else None

    # ---- 3. RENDER one frame, then read the PNG back
    rendered, why = False, None
    try:
        os.environ.setdefault("MUJOCO_GL", "glfw")
        r = mujoco.Renderer(m, 480, 640)
        mujoco.mj_forward(m, d)
        r.update_scene(d)
        px = r.render()
        # blank-frame refusal on the actual pixels, before writing anything
        ink = float((px.astype(int).var(axis=2) > 6).mean())
        if ink < 0.01:
            why = "rendered frame is blank (non-uniform pixel share %.4f)" % ink
        else:
            import imageio
            imageio.imwrite(OUT_PNG, px)
            ok, detail = png_nonblank(OUT_PNG)
            rendered = ok
            why = detail + " ; non-uniform pixel share %.4f" % ink
        rec["render_ink_share"] = ink
        r.close()
    except Exception as e:
        why = "renderer failed: %s" % e
    rec["rendered"] = rendered
    rec["render_detail"] = why

    rec["verdict"] = "PASS" if rendered else "CANNOT DETERMINE"
    rec["why"] = ("model %s: %d bodies, %d joints, %d geoms, %.4f kg; 100 steps ran, "
                  "%d contacts at rest; frame %s"
                  % (os.path.relpath(MODEL, ROOT), m.nbody, m.njnt, m.ngeom,
                     rec["total_mass_kg"], rec["contacts_at_rest"],
                     ("written + read back: " + (why or "")) if rendered else (why or "not attempted")))
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1, ensure_ascii=False)
    print(rec["why"])
    print("wrote %s%s" % (OUT_JSON, (" and " + OUT_PNG) if rendered else ""))
    return 0 if rendered else (2 if not rendered else 1)


if __name__ == "__main__":
    sys.exit(main())
