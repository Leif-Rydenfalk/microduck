#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""head_compare.py — our simulated head beside the real robot's, at the same
camera and over the same measured band of motion.

Leif's standing rule: our renders sit beside the real product. The only public
footage in which a single Microduck head can be tracked frame by frame is
`images/gallery_chorale.mp4` (CATALOG.md:98). sim/head_real_video.py measured
17.018 deg of head-pitch travel and 62.19 deg/s peak there; this page shows
that band next to what OUR model does on the same joint.

    .../bin/python sim/head_compare.py
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio.v2 as iio
import mujoco

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("MUJOCO_GL", "glfw")
import common, compare_render, head_sweep

ROOT = head_sweep.ROOT
OUT = head_sweep.OUT
TILE = (420, 380)


def font(sz):
    for p in ("/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Helvetica.ttc"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()


def real_tiles():
    j = json.load(open(os.path.join(OUT, "head_real_video.json")))
    tr = [r for r in j["trace"] if r[1] is not None]
    box = j["summary"]["crop_xyxy_px"]; fps = j["summary"]["fps"]
    a = np.array([r[1] for r in tr]); t = np.array([r[0] for r in tr])
    picks = [int(a.argmin()), int(np.abs(a - a.mean()).argmin()), int(a.argmax())]
    want = {int(round(t[i] * fps)): a[i] for i in picks}
    rd = iio.get_reader(os.path.join(ROOT, j["summary"]["source_video"]))
    tiles = []
    for i, fr in enumerate(rd):
        if i in want:
            im = Image.fromarray(fr[box[1]:box[3], box[0]:box[2]]).resize(TILE, Image.LANCZOS)
            tiles.append((i / fps, want[i], im))
    rd.close()
    tiles.sort(key=lambda x: x[1])
    return tiles, j["summary"]


def our_tiles(pitches_deg):
    model = head_sweep.studio_model()
    data = mujoco.MjData(model)
    mujoco.mj_resetDataKeyframe(model, data, mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, "STAND"))
    jid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, "head_pitch")
    adr = int(model.jnt_qposadr[jid])
    r = mujoco.Renderer(model, TILE[1] * 2, TILE[0] * 2)
    cam = mujoco.MjvCamera(); cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    cam.azimuth, cam.elevation, cam.distance = 270, -4, 0.29
    opt = mujoco.MjvOption()
    tiles = []
    for pd in pitches_deg:
        data.qpos[adr] = np.radians(pd)
        mujoco.mj_forward(model, data)
        bid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "jaw_soft")
        cam.lookat[:] = data.xpos[bid]
        r.update_scene(data, cam, opt)
        px = r.render().copy()
        assert px.std() > 1.0, "blank render at head_pitch %.2f" % pd
        tiles.append((pd, Image.fromarray(px).resize(TILE, Image.LANCZOS)))
    return tiles


def main():
    tiles, summ = real_tiles()
    band = summ["travel_deg"]
    neutral = 20.0    # DEFAULT_POSE head_pitch = 0.3491 rad (common.py:33)
    ours = our_tiles([neutral - band / 2, neutral, neutral + band / 2, 90.0])
    cols = 4
    W, H = TILE[0] * cols, TILE[1] * 2 + 132
    sh = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(sh)
    f14, f18, f11 = font(15), font(21), font(12)
    d.text((14, 12), "Head pitch: the real Microduck (Pollen's own video) and ours (Pollen's MJCF, our meshes)",
           fill=(15, 15, 15), font=f18)
    d.text((14, 40), "REAL — %s, one robot near profile, beak/trim band tracked frame by frame "
                     "(sim/head_real_video.py). Travel over the whole 12 s clip: %.3f deg, "
                     "peak rate %.2f deg/s." % (summ["source_video"], band, summ["peak_rate_deg_s_smoothed3"]),
           fill=(40, 40, 40), font=f14)
    y0 = 64
    for i, (t, ang, im) in enumerate(tiles[:3]):
        sh.paste(im, (i * TILE[0], y0))
        d.rectangle([i * TILE[0], y0, (i + 1) * TILE[0] - 1, y0 + TILE[1] - 1], outline=(200, 200, 200))
        d.text((i * TILE[0] + 8, y0 + 8), "t = %.2f s   band angle %.2f deg" % (t, ang),
               fill=(220, 20, 20), font=f14)
    d.rectangle([3 * TILE[0], y0, W - 1, y0 + TILE[1] - 1], fill=(246, 246, 246), outline=(200, 200, 200))
    d.text((3 * TILE[0] + 12, y0 + 20),
           "No public video shows the real\nrobot's head driven to its limits,\n"
           "so this band is a LOWER BOUND,\nnot the real robot's capability.\n\n"
           "What would settle it: a Dynamixel\npresent-position/present-velocity\nlog off a real unit, or footage of\n"
           "a known head command.", fill=(60, 60, 60), font=f14)
    y1 = y0 + TILE[1] + 34
    d.text((14, y1 - 26), "OURS — sim/microduck_ours.xml, same left-profile camera (az 270, dist 0.29 m). "
                          "head_pitch posed to the ends of that same band, then to the MJCF limit.",
           fill=(40, 40, 40), font=f14)
    for i, (pd, im) in enumerate(ours):
        sh.paste(im, (i * TILE[0], y1))
        d.rectangle([i * TILE[0], y1, (i + 1) * TILE[0] - 1, y1 + TILE[1] - 1], outline=(200, 200, 200))
        lbl = "head_pitch = %+.2f deg" % pd
        if i == 3:
            lbl += "  (MJCF limit)"
        d.text((i * TILE[0] + 8, y1 + 8), lbl, fill=(20, 90, 190), font=f14)
    d.text((14, H - 26), "Same-band panels are POSE matches, not a motion match: the real clip is a "
                         "scripted animation and its camera is hand-held. sim/head_compare.py",
           fill=(90, 90, 90), font=f11)
    p = os.path.join(OUT, "head_vs_real.png")
    sh.save(p)
    print("wrote", p, sh.size)


if __name__ == "__main__":
    main()
