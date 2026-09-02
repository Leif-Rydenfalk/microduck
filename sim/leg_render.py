#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""leg_render.py — the videos for out/motion/legs.json.

Every clip is a three-panel composite drawn with the studio renderer
(compare_render.studio_scene: white sky, real product materials on OUR rebuilt
meshes, headlight 0.45 / ambient 0.28):

    [ profile close-up on the joint ] [ 3/4 close-up ] [ full body ]

The two close-ups track the joint's own anchor (data.xanchor), so the camera
follows the joint as it moves, and both cameras are >= 0.16 m out (closer than
that and MuJoCo's near plane clips the frame to blank white). The header carries
the live joint angle, the MJCF range and the phase of the motion.

Outputs per clip: out/motion/<name>.mp4, <name>.gif (<= 8 MB),
<name>_sheet.png (8 frames) and two individual frames in out/motion/frames/.
Every clip is read back frame-wise and a blank frame is a hard failure.

    /Applications/FreeCAD.app/Contents/Resources/bin/python sim/leg_render.py
"""
import os, sys, math, json, glob
sys.stdout.reconfigure(line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("MUJOCO_GL", "glfw")
import numpy as np
import mujoco
import imageio
from PIL import Image, ImageDraw, ImageFont
import common
import leg_sweep as LS

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "out", "motion")
FRAMES = os.path.join(OUT, "frames")
TRAJ = os.path.join(OUT, "traj")
os.makedirs(FRAMES, exist_ok=True)
PW, PH = 400, 500          # panel size
HDR = 74                   # header strip height
FPS = 25
D = math.degrees

_FONTS = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf",
          "/System/Library/Fonts/Supplemental/Arial.ttf",
          "/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/Menlo.ttc"]


def font(sz):
    for p in _FONTS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()


F_TITLE, F_SUB, F_TAG = font(25), font(17), font(15)


class Studio:
    def __init__(self, floor=False, tag="render"):
        self.m, self.d, self.path = LS.build(floor=floor, tag=tag)
        self.r = mujoco.Renderer(self.m, PH, PW)
        self.opt = mujoco.MjvOption()
        self.cam = mujoco.MjvCamera()
        self.cam.type = mujoco.mjtCamera.mjCAMERA_FREE

    def set_q(self, q):
        self.d.qpos[:] = q
        self.d.qvel[:] = 0
        mujoco.mj_forward(self.m, self.d)

    def anchor(self, jname):
        jid = mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_JOINT, jname)
        return np.array(self.d.xanchor[jid], float)

    def shot(self, lookat, az, el, dist):
        assert dist >= 0.16, "cam.distance %.3f < 0.16 clips to blank white" % dist
        self.cam.lookat[:] = lookat
        self.cam.azimuth, self.cam.elevation, self.cam.distance = float(az), float(el), float(dist)
        self.r.update_scene(self.d, self.cam, self.opt)
        return self.r.render().copy()


def panel(px, label):
    im = Image.fromarray(px)
    dr = ImageDraw.Draw(im)
    dr.rectangle([0, 0, PW - 1, PH - 1], outline=(206, 206, 210), width=1)
    dr.rectangle([0, PH - 26, PW, PH], fill=(28, 30, 34))
    dr.text((9, PH - 22), label, font=F_TAG, fill=(245, 245, 245))
    return im


def compose(shots, title, sub, right=""):
    W = PW * len(shots)
    im = Image.new("RGB", (W, HDR + PH), (255, 255, 255))
    for i, (px, lab) in enumerate(shots):
        im.paste(panel(px, lab), (i * PW, HDR))
    dr = ImageDraw.Draw(im)
    dr.rectangle([0, 0, W, HDR], fill=(255, 255, 255))
    dr.line([0, HDR - 1, W, HDR - 1], fill=(28, 30, 34), width=2)
    dr.text((12, 9), title, font=F_TITLE, fill=(20, 20, 24))
    dr.text((12, 43), sub, font=F_SUB, fill=(90, 92, 100))
    if right:
        w = dr.textlength(right, font=F_SUB)
        dr.text((W - w - 12, 15), right, font=F_SUB, fill=(90, 92, 100))
    return np.asarray(im)


# ------------------------------------------------------------------ writing
def check_frames(name, frames):
    """a blank / frozen clip is a defect, not a deliverable."""
    bad = []
    for i, f in enumerate(frames):
        body = f[HDR:, :, :]
        if body.std() < 3.0:
            bad.append((i, "flat std %.2f" % body.std()))
        if body.min() > 245:
            bad.append((i, "all-white min %d" % body.min()))
    diffs = [float(np.abs(frames[i].astype(int) - frames[i - 1].astype(int)).mean())
             for i in range(1, len(frames))]
    if bad:
        raise SystemExit("BLANK FRAMES in %s: %s" % (name, bad[:5]))
    if max(diffs) < 0.05:
        raise SystemExit("FROZEN clip %s (max inter-frame diff %.4f)" % (name, max(diffs)))
    return dict(frames=len(frames), mean_interframe_diff=round(float(np.mean(diffs)), 4),
                max_interframe_diff=round(float(max(diffs)), 4),
                min_pixel=int(min(f.min() for f in frames)),
                mean_std=round(float(np.mean([f.std() for f in frames])), 3))


def write_clip(name, frames, fps=FPS):
    stats = check_frames(name, frames)
    mp4 = os.path.join(OUT, name + ".mp4")
    imageio.mimwrite(mp4, frames, fps=fps, quality=8, macro_block_size=8)
    # gif: half rate, scaled so it stays well under 8 MB
    gif = os.path.join(OUT, name + ".gif")
    sc = 0.40
    small = [np.asarray(Image.fromarray(f).resize((int(f.shape[1] * sc), int(f.shape[0] * sc)),
                                                  Image.LANCZOS)) for f in frames[::2]]
    imageio.mimwrite(gif, small, fps=fps / 2, loop=0)
    if os.path.getsize(gif) > 8 * 1024 * 1024:
        small = small[::2]
        imageio.mimwrite(gif, small, fps=fps / 4, loop=0)
    # contact sheet: 8 frames, 4 x 2
    idx = np.linspace(0, len(frames) - 1, 8).astype(int)
    tw = 470
    th = int(tw * frames[0].shape[0] / frames[0].shape[1])
    sheet = Image.new("RGB", (tw * 4, th * 2 + 30), (255, 255, 255))
    dr = ImageDraw.Draw(sheet)
    dr.text((8, 6), "%s — 8 frames of %d" % (name, len(frames)), font=F_SUB, fill=(20, 20, 24))
    for k, i in enumerate(idx):
        t = Image.fromarray(frames[i]).resize((tw, th), Image.LANCZOS)
        sheet.paste(t, ((k % 4) * tw, 30 + (k // 4) * th))
    sheetp = os.path.join(OUT, name + "_sheet.png")
    sheet.save(sheetp)
    keep = []
    for i in (idx[1], idx[4]):
        p = os.path.join(FRAMES, "%s_%03d.png" % (name, i))
        Image.fromarray(frames[i]).save(p); keep.append(p)
    return dict(name=name, mp4=os.path.relpath(mp4, ROOT), gif=os.path.relpath(gif, ROOT),
                sheet=os.path.relpath(sheetp, ROOT),
                frames_png=[os.path.relpath(p, ROOT) for p in keep],
                fps=fps, seconds=round(len(frames) / fps, 3),
                mp4_bytes=os.path.getsize(mp4), gif_bytes=os.path.getsize(gif), **stats)


# ------------------------------------------------------------------- clips
SIDE_CAM = {"left": (270, 225), "right": (90, 45)}      # (profile az, three-quarter az)


def joint_clip(st, jname, tr, ranges, stride=3):
    """one joint's dynamic sweep: profile close-up + 3/4 close-up + full body."""
    paz, qaz = SIDE_CAM["left" if jname.startswith("left") else "right"]
    R = ranges[jname]
    frames = []
    q, ph, t, tgt = tr["q"], tr["phase"], tr["t"], tr["tgt"]
    for k in range(0, len(t), stride):
        st.set_q(tr["qpos"][k])
        a = st.anchor(jname)
        shots = [(st.shot(a, paz, -4, 0.20), "profile close-up  az %d  d 0.20 m" % paz),
                 (st.shot(a, qaz, -12, 0.22), "three-quarter close-up  az %d  d 0.22 m" % qaz),
                 (st.shot([0, 0, 0.15], paz - 18, -8, 0.46), "full body  d 0.46 m")]
        frames.append(compose(
            shots, "%s — %+7.2f deg" % (jname, D(q[k])),
            "MJCF range %.3f to %.3f deg (%s)  ·  commanded %+7.2f deg  ·  %s phase" %
            (R["lo_deg"], R["hi_deg"], R["cite"], D(tgt[k]), ph[k]),
            "t = %5.2f s   ·   our rebuilt meshes on Pollen's MJCF" % t[k]))
    return frames


def pair_clip(st, jbase, ranges, stride=3):
    """left then right of the same joint, concatenated -> one clip per joint type."""
    fr = []
    for side in ("left", "right"):
        jn = "%s_%s" % (side, jbase)
        tr = dict(np.load(os.path.join(TRAJ, "dyn_%s.npz" % jn)))
        fr += joint_clip(st, jn, tr, ranges, stride)
    return fr


def seq_clip(st, name, qpos, title, subs, joints, stride=3, full_az=252, per_frame=None):
    """a sequence (squat / sit-stand / leg lift): knee close-up, hip close-up, full body."""
    frames = []
    for k in range(0, len(qpos), stride):
        st.set_q(qpos[k])
        a1 = st.anchor(joints[0]); a2 = st.anchor(joints[1])
        shots = [(st.shot(a1, 270, -4, 0.20), "%s  profile az 270  d 0.20 m" % joints[0]),
                 (st.shot(a2, 225, -12, 0.22), "%s  three-quarter az 225  d 0.22 m" % joints[1]),
                 (st.shot([0, 0, 0.13], full_az, -6, 0.46), "full body  d 0.46 m")]
        extra = per_frame(k) if per_frame else ""
        frames.append(compose(shots, title, subs, extra))
    return frames


def main():
    legs = json.load(open(os.path.join(OUT, "legs.json")))
    R = legs["mjcf_ranges"]
    vids = []
    st = Studio(floor=False, tag="render_air")
    stf = Studio(floor=True, tag="render_floor")

    # --- 1..5  one clip per joint type, left leg then right leg ---
    for jb in ("hip_yaw", "hip_roll", "hip_pitch", "knee", "ankle"):
        fr = pair_clip(st, jb, R, stride=3)
        vids.append(dict(what="%s swept through its full MJCF range, left leg then right leg, "
                              "policy paused, trunk pinned; close-ups track the joint anchor" % jb,
                         camera="profile az 270/90 d 0.20 m; three-quarter az 225/45 d 0.22 m; full body d 0.46 m", **write_clip("legs_" + jb, fr)))
        print("wrote legs_%s" % jb)

    # --- 6  squat under Pollen's stand policy ---
    sq = dict(np.load(os.path.join(TRAJ, "squat.npz")))
    kj = [int(stf.m.jnt_qposadr[mujoco.mj_name2id(stf.m, mujoco.mjtObj.mjOBJ_JOINT, j)])
          for j in ("left_knee", "left_hip_pitch")]
    fr = seq_clip(stf, "legs_squat", sq["qpos"],
                  "squat — Pollen BEST_alpha_stand policy, body-z command 0 -> 0.10 -> 0",
                  "trunk %.1f mm -> %.1f mm  ·  every joint angle is the policy's own output" %
                  (sq["trunk_z"][0] * 1000, sq["trunk_z"].min() * 1000),
                  ("left_knee", "left_hip_pitch"),
                  per_frame=lambda k: "knee %+6.2f deg   hip pitch %+6.2f deg   trunk z %5.1f mm" %
                  (D(sq["qpos"][k][kj[0]]), D(sq["qpos"][k][kj[1]]), sq["trunk_z"][k] * 1000))
    vids.append(dict(what="squat and rise, twice, under Pollen's stand policy driven through its "
                          "body-z command slot; on the floor, physics on",
                     camera="knee profile az 270 d 0.20 m; hip-pitch three-quarter az 225 d 0.22 m; full body d 0.46 m", **write_clip("legs_squat", fr)))
    print("wrote legs_squat")

    # --- 7  sit-stand, Pollen's sitstand policy (the existing run, re-rendered close) ---
    ss = np.load(os.path.join(ROOT, "out", "sim", "sitstand_ours_traj.npz"))
    qp = ss["qpos"]
    fr = seq_clip(stf, "legs_sitstand", qp,
                  "sit -> stand — Pollen BEST_alpha_sitstand policy (out/sim/sitstand_ours_traj.npz)",
                  "sit commanded at 1.0 s, stand at 4.5 s  ·  8.0 s at 50 Hz",
                  ("left_knee", "left_hip_pitch"), stride=3,
                  per_frame=lambda k: "t %4.2f s   knee %+6.2f deg   trunk z %5.1f mm" %
                  (ss["time"][k], D(qp[k][kj[0]]), ss["trunk_z"][k] * 1000))
    vids.append(dict(what="the sit-stand policy re-rendered with joint close-ups",
                     camera="knee profile az 270 d 0.20 m; hip-pitch three-quarter az 225 d 0.22 m; full body d 0.46 m", **write_clip("legs_sitstand", fr)))
    print("wrote legs_sitstand")

    # --- 8  one-leg lift, hoisted ---
    ll = dict(np.load(os.path.join(TRAJ, "leglift.npz")))
    fr = seq_clip(st, "legs_leglift", ll["qpos"],
                  "leg lift — hoisted (trunk pinned), policy paused, direct joint targets",
                  "left leg lifts and folds, then the right; hip pitch 0.85 rad + knee 1.05 rad commanded",
                  ("left_knee", "left_hip_pitch"), stride=3,
                  per_frame=lambda k: "left knee %+6.2f deg   left hip pitch %+6.2f deg" %
                  (D(ll["qpos"][k][kj[0]]), D(ll["qpos"][k][kj[1]])))
    vids.append(dict(what="alternating single-leg lift with the duck held (trunk pinned)",
                     camera="knee profile az 270 d 0.20 m; hip-pitch three-quarter az 225 d 0.22 m; full body d 0.46 m", **write_clip("legs_leglift", fr)))
    print("wrote legs_leglift")

    # --- 9  the self-collision case: both hip rolls driven opposed until the soles touch ---
    mp = os.path.join(TRAJ, "mirror_left_hip_roll_opp.npz")
    mz = np.load(mp)
    us, qs = mz["us"], mz["qpos"]
    sel = np.arange(0, len(us), max(1, len(us) // 150))
    onset = None
    for k, v in legs["self_collision"]["both_legs_mirrored"]["cases"].items():
        if "opposed" in k and v["pairs"]:
            onset = list(v["pairs"].values())[0]["onset_deg"]
            pairname = list(v["pairs"].keys())[0]
    frames = []
    for k in sel:
        st.set_q(qs[k])
        a = st.anchor("left_ankle")
        touch = us[k] <= onset
        shots = [(st.shot(a, 180, -6, 0.20), "front close-up az 180  d 0.20 m"),
                 (st.shot([0, 0, 0.06], 180, -20, 0.24), "soles, front az 180  d 0.24 m"),
                 (st.shot([0, 0, 0.13], 252, -6, 0.46), "full body  d 0.46 m")]
        frames.append(compose(shots,
                              "self-collision — both hip rolls driven opposed  (offset %+6.2f deg)" % us[k],
                              "MuJoCo contact %s at offset %.1f deg" % ("PRESENT" if touch else "none", onset),
                              pairname if touch else ""))
    vids.append(dict(what="the one self-collision a both-leg sweep finds: the two soles meet when both "
                          "hip rolls are driven inward together",
                     camera="front az 180 d 0.20 m; soles az 180 el -20 d 0.24 m; full body d 0.46 m",
                     **write_clip("legs_selfcollision", frames)))
    print("wrote legs_selfcollision")

    # --- 10  composite: four motions playing at once, full body ---
    srcs = [("knee sweep", np.load(os.path.join(TRAJ, "dyn_left_knee.npz"))["qpos"], st, 270),
            ("hip pitch sweep", np.load(os.path.join(TRAJ, "dyn_left_hip_pitch.npz"))["qpos"], st, 252),
            ("squat (stand policy)", sq["qpos"], stf, 252),
            ("sit -> stand (sitstand policy)", qp, stf, 252)]
    n = max(len(s[1]) for s in srcs)
    step = 4
    frames = []
    for k in range(0, n, step):
        shots = []
        for lab, q, s, az in srcs:
            s.set_q(q[min(k, len(q) - 1)])
            shots.append((s.shot([0, 0, 0.13], az, -6, 0.46), lab))
        top = compose(shots[:2], "Microduck legs — composite", "our rebuilt meshes on Pollen's MJCF")
        bot = compose(shots[2:], " ", " ")
        im = Image.new("RGB", (top.shape[1], top.shape[0] + bot.shape[0] - HDR), (255, 255, 255))
        im.paste(Image.fromarray(top), (0, 0))
        im.paste(Image.fromarray(bot[HDR:]), (0, top.shape[0]))
        frames.append(np.asarray(im))
    vids.append(dict(what="four leg motions side by side: knee sweep, hip-pitch sweep, squat, sit-stand",
                     camera="full body d 0.46 m, az 270/252", **write_clip("legs_composite", frames)))
    print("wrote legs_composite")

    json.dump(vids, open(os.path.join(OUT, "legs_videos.json"), "w"), indent=1)
    print("wrote", os.path.join(OUT, "legs_videos.json"))


if __name__ == "__main__":
    main()
