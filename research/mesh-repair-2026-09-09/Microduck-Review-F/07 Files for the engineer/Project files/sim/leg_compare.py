#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""leg_compare.py — our leg renders beside the real product photo, same posture.

Leif's rule: a render of ours sits next to the real thing wherever a photo of the
same motion exists. Two exist for the legs:
  images/store/store_microduck-cream-standing-profile-left.jpg  (standing, full leg chain)
  images/store/store_microduck-cream-sitting-three-quarter_1.png (sitting)
There is NO product photo of a single joint mid-sweep, of a squat, or of a
one-leg lift — those clips are stated as having no photographic counterpart
rather than being paired with an unrelated image.
"""
import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("MUJOCO_GL", "glfw")
import numpy as np, mujoco
from PIL import Image, ImageDraw
import common, leg_sweep as LS, leg_render as LR

ROOT = LS.ROOT
OUT = LS.OUT
IMG = os.path.join(ROOT, "images", "store")


def autocrop(im, thr=244, pad=0.03):
    """crop to the non-white content so ours and the photo are compared at the same
    subject size instead of at whatever margin each happens to carry."""
    a = np.asarray(im.convert("L"))
    ys, xs = np.where(a < thr)
    if len(xs) == 0:
        return im
    px = int(pad * im.size[0]); py = int(pad * im.size[1])
    return im.crop((max(0, xs.min() - px), max(0, ys.min() - py),
                    min(im.size[0], xs.max() + px), min(im.size[1], ys.max() + py)))


def tile(px, cap, W, H=None):
    im = Image.fromarray(px) if isinstance(px, np.ndarray) else px
    im = autocrop(im.convert("RGB"))
    if H:                                   # match subject HEIGHT across the pair
        s = H / im.size[1]
        im = im.resize((max(1, int(im.size[0] * s)), H), Image.LANCZOS)
        pad = Image.new("RGB", (W, H), (255, 255, 255))
        pad.paste(im, ((W - im.size[0]) // 2, 0))
        im = pad
    else:
        s = W / im.size[0]
        im = im.resize((W, int(im.size[1] * s)), Image.LANCZOS)
    out = Image.new("RGB", (W, im.size[1] + 34), (255, 255, 255))
    out.paste(im, (0, 0))
    d = ImageDraw.Draw(out)
    d.rectangle([0, im.size[1], W, im.size[1] + 34], fill=(28, 30, 34))
    d.text((8, im.size[1] + 9), cap, font=LR.F_TAG, fill=(245, 245, 245))
    return out


def side_by_side(name, ours, photo_path, cap_l, cap_r, title, W=620, H=760):
    a = tile(ours, cap_l, W, H)
    b = tile(Image.open(photo_path), cap_r, W, H)
    H = max(a.size[1], b.size[1])
    im = Image.new("RGB", (W * 2 + 12, H + 46), (255, 255, 255))
    d = ImageDraw.Draw(im)
    d.text((10, 12), title, font=LR.F_SUB, fill=(20, 20, 24))
    im.paste(a, (0, 46)); im.paste(b, (W + 12, 46))
    p = os.path.join(OUT, name)
    im.save(p)
    print("wrote", p)
    return os.path.relpath(p, ROOT)


def main():
    out = []
    st = LR.Studio(floor=False, tag="cmp")
    # --- standing profile, at the STAND keyframe ---
    kid = mujoco.mj_name2id(st.m, mujoco.mjtObj.mjOBJ_KEY, "STAND")
    mujoco.mj_resetDataKeyframe(st.m, st.d, kid); mujoco.mj_forward(st.m, st.d)
    q = st.d.qpos.copy(); q[7 + 5] = 0.02; q[7 + 6] = 0.0     # head level, like the photo
    st.set_q(q)
    px = st.shot([0, 0, 0.155], 270, -4, 0.44)
    out.append(dict(what="standing, left profile: the whole leg chain (hip yaw/roll bracket, thigh, "
                         "knee servo, shin, ankle servo, foot)",
                    png=side_by_side("compare_standing_profile.png", px,
                                     os.path.join(IMG, "store_microduck-cream-standing-profile-left.jpg"),
                                     "OURS — MuJoCo studio, our rebuilt meshes, az 270 el -4 d 0.44 m",
                                     "REAL — store_microduck-cream-standing-profile-left.jpg",
                                     "Standing, left profile — our CAD vs the product photo. Leg chain matches part for part: "
                                     "hip bracket, thigh + rigidity plate, knee servo, shin, ankle servo, two-plate foot. "
                                     "Colours are Pollen's MJCF material palette (dev-unit teal/yellow), not the retail "
                                     "cream/orange. The HEAD shape difference is the open finding of COMPARISON.html \u00a75 "
                                     "item 1 (lane A), not a leg finding.")))
    # --- sitting: the deepest-trunk frame of the sit-stand policy run ---
    ss = np.load(os.path.join(ROOT, "out", "sim", "sitstand_ours_traj.npz"))
    k = int(np.argmin(ss["trunk_z"]))
    st.set_q(ss["qpos"][k])
    best = None
    for az in (135, 150, 200, 225, 315):
        p = st.shot([0, 0, 0.085], az, -6, 0.40)
        Image.fromarray(p).save(os.path.join(LR.FRAMES, "compare_sitting_az%d.png" % az))
        if az == 225:
            best = p
    out.append(dict(what="sitting: frame %d of the sit-stand run (t = %.2f s, trunk z %.1f mm, the "
                         "deepest of the run)" % (k, ss["time"][k], ss["trunk_z"][k] * 1000),
                    png=side_by_side("compare_sitting.png", best,
                                     os.path.join(IMG, "store_microduck-cream-sitting-three-quarter_1.png"),
                                     "OURS — sit-stand policy at its deepest, az 225 el -6 d 0.40 m",
                                     "REAL — store_microduck-cream-sitting-three-quarter_1.png",
                                     "Sitting — our sit-stand simulation vs the product photo. Same posture: hips rolled out, knees "
                                     "folded forward, soles flat on the floor either side of the trunk, thigh plate outboard.")))
    json.dump(out, open(os.path.join(OUT, "legs_compare.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
