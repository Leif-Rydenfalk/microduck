#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""motion_render.py — the mechanics of OUR Microduck walking, filmed.

Leif, 2026-09-02: "show me renders of the mechanics like our cad system walking,
zoom in on joints as they move and the head kmvoing around and the legs moving
around."

Replays the recorded walk trajectory (out/sim/walk_ours_traj.npz, written by
sim/run_policy.py: Pollen's BEST_alpha_walking.onnx at vx 0.25 m/s on
sim/microduck_ours.xml, OUR rebuilt meshes) frame by frame through MuJoCo's
offscreen renderer in the compare_render.py studio (white sky, real product
materials per geom) and films:

  walk_body          full body, 3/4 front-left, camera tracking trunk_base
  walk_knee_prof     left knee (body `leg`), profile-left, tracking the knee
  walk_knee_34       left knee, 3/4 front-left
  walk_hip_prof      left hip cluster (yaw/roll/pitch), profile-left
  walk_hip_34        left hip cluster, 3/4 front-left
  walk_ankle_prof    left ankle + foot, profile-left
  walk_ankle_34      left ankle + foot, 3/4 front-left
  walk_composite     2x2: body + knee + hip + ankle on one timeline, live angles
  walk_slowmo        0.25x of ONE measured gait cycle + joint-angle traces

and MEASURES, off the same qpos/qvel arrays, every joint's MJCF range, the
travel actually used, and the peak angular velocity with the frame it happened
on -> out/motion/walk.json.

    /Applications/FreeCAD.app/Contents/Resources/bin/python sim/motion_render.py --probe
    /Applications/FreeCAD.app/Contents/Resources/bin/python sim/motion_render.py --all
"""
import argparse
import json
import os
import sys

os.environ.setdefault("MUJOCO_GL", "glfw")
import numpy as np
import xml.etree.ElementTree as ET
import mujoco
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import common                      # noqa: E402
import compare_render              # noqa: E402

OUT = os.path.join(ROOT, "out", "motion")
FRAMES = os.path.join(OUT, "frames")
TRAJ = os.path.join(ROOT, "out", "sim", "walk_ours_traj.npz")
FPS = 30

# ---------------------------------------------------------------- scene -----

def studio_walk_scene():
    """compare_render's studio (white sky, product materials, headlight
    0.45/ambient 0.28) plus a pale ground plane and one shadow-casting light,
    because a walk with no ground reads as a hovering duck."""
    xml = compare_render.studio_scene(common.robot_file("ours"))
    root = ET.fromstring(xml)
    asset = root.find("asset")
    # visible grid: without ground texture a tracked camera makes a walk look like
    # marching on the spot. 20 squares/m = 50 mm squares against a 0.52 m field.
    ET.SubElement(asset, "texture", type="2d", name="studiofloor", builtin="checker", mark="edge",
                  rgb1="0.985 0.985 0.99", rgb2="0.735 0.750 0.785", markrgb="0.52 0.55 0.60",
                  width="512", height="512")
    ET.SubElement(asset, "material", name="studiofloor", texture="studiofloor", texuniform="true",
                  texrepeat="20 20", reflectance="0.04")
    wb = root.find("worldbody")
    ET.SubElement(wb, "geom", name="floor", size="0 0 0.05", pos="0 0 0", type="plane",
                  material="studiofloor")
    ET.SubElement(wb, "light", pos="0.6 -0.5 1.1", dir="-0.35 0.32 -1", directional="true",
                  diffuse="0.30 0.30 0.30", castshadow="true")
    for v in root.findall("visual"):
        q = v.find("quality")
        if q is not None:
            q.set("shadowsize", "4096")
        g = v.find("global")
        if g is not None:
            g.set("offwidth", "1920")
            g.set("offheight", "1440")
    txt = ET.tostring(root, encoding="unicode")
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "_studio_walk_scene.xml")
    open(path, "w").write(txt)
    return path


class Replay:
    """The recorded trajectory put back on the model. qpos is the simulation
    state; mj_forward gives the exact body kinematics for that state."""

    def __init__(self, traj_path=TRAJ, scene_path=None):
        self.d = np.load(traj_path, allow_pickle=True)
        self.t = np.asarray(self.d["time"], float)
        self.Q = np.asarray(self.d["qpos"], float)
        self.V = np.asarray(self.d["qvel"], float)
        self.ctrl_dt = float(self.d["ctrl_dt"])
        self.root_qadr = int(self.d["root_qadr"])
        self.scene_path = scene_path or studio_walk_scene()
        self.model = mujoco.MjModel.from_xml_path(self.scene_path)
        self.data = mujoco.MjData(self.model)
        self.jid = {n: mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_JOINT, n)
                    for n in common.JOINT_NAMES}
        self.jadr = {n: int(self.model.jnt_qposadr[self.jid[n]]) for n in common.JOINT_NAMES}
        self.jdof = {n: int(self.model.jnt_dofadr[self.jid[n]]) for n in common.JOINT_NAMES}
        self.jrange = {n: np.degrees(self.model.jnt_range[self.jid[n]]).tolist()
                       for n in common.JOINT_NAMES}
        self._ren = {}

    def qpos_at(self, t):
        """linear interpolation between recorded 50 Hz frames; the free-joint
        quaternion is lerped then renormalised (steps are <= 0.02 s)."""
        t = float(np.clip(t, self.t[0], self.t[-1]))
        i = int(np.clip(np.searchsorted(self.t, t) - 1, 0, len(self.t) - 2))
        f = (t - self.t[i]) / (self.t[i + 1] - self.t[i])
        q = (1 - f) * self.Q[i] + f * self.Q[i + 1]
        a = self.root_qadr + 3
        n = np.linalg.norm(q[a:a + 4])
        if n > 0:
            q[a:a + 4] /= n
        return q, i, f

    def set_time(self, t):
        q, i, f = self.qpos_at(t)
        self.data.qpos[:] = q
        self.data.qvel[:] = 0
        mujoco.mj_forward(self.model, self.data)
        return i

    def bpos(self, name):
        bid = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_BODY, name)
        assert bid >= 0, name
        return np.array(self.data.xpos[bid], float)

    def walked(self, t):
        """world-frame distance the trunk free joint has covered by time t (m)."""
        q, _, _ = self.qpos_at(t)
        a = self.root_qadr
        return float(np.linalg.norm(q[a:a + 2] - self.Q[0, a:a + 2]))

    def angle_deg(self, joint, t=None):
        if t is None:
            return float(np.degrees(self.data.qpos[self.jadr[joint]]))
        q, _, _ = self.qpos_at(t)
        return float(np.degrees(q[self.jadr[joint]]))

    def renderer(self, w, h):
        key = (w, h)
        if key not in self._ren:
            self._ren[key] = mujoco.Renderer(self.model, height=h, width=w)
        return self._ren[key]

    def shot(self, spec, t, w, h):
        """spec = (track_body, azimuth, elevation, distance, z_offset)"""
        body, az, el, dist, dz = spec
        self.set_time(t)
        cam = mujoco.MjvCamera()
        cam.type = mujoco.mjtCamera.mjCAMERA_FREE
        p = self.bpos(body)
        cam.lookat[:] = [p[0], p[1], p[2] + dz]
        cam.azimuth, cam.elevation, cam.distance = float(az), float(el), float(dist)
        r = self.renderer(w, h)
        r.update_scene(self.data, cam, mujoco.MjvOption())
        return r.render().copy()


# ------------------------------------------------------------- cameras ------
# (track_body, azimuth deg, elevation deg, distance m, lookat z offset m)
# azimuth convention from sim/compare_render.py: 225 = 3/4 front-left, 270 =
# profile-left. distance >= 0.16 m on every zoom or the near plane clips
# (GOAL.md handover correction 6).
CAMS = {
    "walk_body":       ("trunk_base",      225, -10, 0.52,  0.00),
    "walk_knee_prof":  ("leg",             270,  -6, 0.170, 0.005),
    "walk_knee_34":    ("leg",             225,  -8, 0.185, 0.005),
    "walk_hip_prof":   ("upper_leg_left",  270,  -6, 0.190, 0.010),
    "walk_hip_34":     ("upper_leg_left",  225,  -8, 0.200, 0.010),
    "walk_ankle_prof": ("ankle_left",      270,  -4, 0.160, 0.000),
    "walk_ankle_34":   ("ankle_left",      225,  -8, 0.170, 0.000),
}
WHAT = {
    "walk_body": "full body, 3/4 front-left, camera tracking trunk_base",
    "walk_knee_prof": "left knee (left_knee, body `leg`), profile-left, tracked",
    "walk_knee_34": "left knee, 3/4 front-left, tracked",
    "walk_hip_prof": "left hip cluster (yaw/roll/pitch, body `upper_leg_left`), profile-left",
    "walk_hip_34": "left hip cluster, 3/4 front-left",
    "walk_ankle_prof": "left ankle + foot (body `ankle_left`), profile-left",
    "walk_ankle_34": "left ankle + foot, 3/4 front-left",
}
# what each close-up reads out, live, in the composite
READOUT = {
    "walk_body": ["left_hip_pitch", "left_knee", "left_ankle"],
    "walk_knee_prof": ["left_knee"], "walk_knee_34": ["left_knee"],
    "walk_hip_prof": ["left_hip_yaw", "left_hip_roll", "left_hip_pitch"],
    "walk_hip_34": ["left_hip_yaw", "left_hip_roll", "left_hip_pitch"],
    "walk_ankle_prof": ["left_ankle"], "walk_ankle_34": ["left_ankle"],
}

# ---------------------------------------------------------------- draw ------

def font(sz):
    for p in ("/System/Library/Fonts/Supplemental/Arial.ttf",
              "/System/Library/Fonts/Helvetica.ttc",
              "/System/Library/Fonts/SFNSMono.ttf"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()


def caption(px, title, lines, t=None, frame=None):
    """Bottom-left caption block on a rendered frame (white studio -> dark ink)."""
    im = Image.fromarray(px)
    d = ImageDraw.Draw(im)
    W, H = im.size
    f1, f2 = font(max(13, W // 44)), font(max(11, W // 56))
    y = H - (len(lines) + 1) * (f2.size + 4) - 12
    d.rectangle([8, y - 6, 8 + max(len(title) * f1.size * 0.60,
                                   max([len(l) for l in lines] + [1]) * f2.size * 0.58) + 16,
                 H - 8], fill=(255, 255, 255, 235))
    d.text((16, y), title, font=f1, fill=(20, 22, 28))
    for i, l in enumerate(lines):
        d.text((16, y + f1.size + 4 + i * (f2.size + 4)), l, font=f2, fill=(60, 64, 74))
    if t is not None:
        s = "t = %6.3f s   frame %3d" % (t, frame)
        d.rectangle([W - len(s) * f2.size * 0.58 - 20, 8, W - 8, 8 + f2.size + 10],
                    fill=(255, 255, 255, 235))
        d.text((W - len(s) * f2.size * 0.58 - 12, 13), s, font=f2, fill=(60, 64, 74))
    return np.asarray(im.convert("RGB"))


def contact_sheet(frames_idx_t, path, cols=4):
    """8 frames, labelled, one PNG. frames_idx_t = [(px, idx, t), ...]"""
    n = len(frames_idx_t)
    rows = (n + cols - 1) // cols
    h0, w0 = frames_idx_t[0][0].shape[:2]
    tw = 360
    th = int(round(tw * h0 / w0))
    pad, top = 6, 26
    sheet = Image.new("RGB", (cols * (tw + pad) + pad, rows * (th + pad + top) + pad), (246, 246, 248))
    d = ImageDraw.Draw(sheet)
    f = font(14)
    for k, (px, idx, t) in enumerate(frames_idx_t):
        r, c = divmod(k, cols)
        x = pad + c * (tw + pad)
        y = pad + r * (th + pad + top)
        d.text((x + 2, y + 4), "frame %d   t = %.3f s" % (idx, t), font=f, fill=(30, 32, 38))
        sheet.paste(Image.fromarray(px).resize((tw, th), Image.LANCZOS), (x, y + top))
    sheet.save(path)
    return path


def write_video(name, frames_iter, n_total, fps=FPS, gif_max_mb=8.0, cols=4):
    """Stream frames to mp4, keep 8 for a contact sheet and a subsample for the
    GIF, then read the mp4 back and refuse blank or frozen frames."""
    import imageio
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(FRAMES, exist_ok=True)
    mp4 = os.path.join(OUT, name + ".mp4")
    sheet_idx = set(np.linspace(0, n_total - 1, 8).round().astype(int).tolist())
    gif_stride = max(1, int(round(n_total / 90.0)))
    keep, gif_frames = [], []
    gif_w = 520                                   # GIF long edge, before the size loop
    w = imageio.get_writer(mp4, fps=fps, quality=8, macro_block_size=8,
                           ffmpeg_params=["-pix_fmt", "yuv420p"])
    for i, (px, t) in enumerate(frames_iter):
        w.append_data(px)
        if i in sheet_idx:
            keep.append((px, i, t))
        if i % gif_stride == 0:
            im = Image.fromarray(px)
            sc = min(1.0, gif_w / im.size[0])
            gif_frames.append(im.resize((int(im.size[0] * sc), int(im.size[1] * sc)), Image.LANCZOS))
    w.close()
    sheet = contact_sheet(keep, os.path.join(OUT, name + "_sheet.png"), cols=cols)
    # three individual frames on disk at full size, for reading back
    for px, i, t in (keep[0], keep[len(keep) // 2], keep[-1]):
        Image.fromarray(px).save(os.path.join(FRAMES, "%s_f%03d.png" % (name, i)))
    gif = os.path.join(OUT, name + ".gif")
    scale = 1.0
    for _ in range(5):
        gf = [p if scale == 1.0 else p.resize((max(8, int(p.size[0] * scale)),
                                               max(8, int(p.size[1] * scale))), Image.LANCZOS)
              for p in gif_frames]
        gf[0].save(gif, save_all=True, append_images=gf[1:], optimize=True,
                   duration=int(1000 * gif_stride / fps), loop=0)
        mb = os.path.getsize(gif) / 1e6
        if mb <= gif_max_mb:
            break
        scale *= 0.75
    verdict = verify_video(mp4)
    return {"path": os.path.relpath(mp4, ROOT), "gif": os.path.relpath(gif, ROOT),
            "contact_sheet": os.path.relpath(sheet, ROOT),
            "gif_mb": round(os.path.getsize(gif) / 1e6, 2),
            "mp4_mb": round(os.path.getsize(mp4) / 1e6, 2),
            "frames": n_total, "fps": fps, "seconds": round(n_total / fps, 3),
            "verify": verdict}


def verify_video(mp4):
    """Read the encoded file back. A blank/near-white frame or a frozen pair is
    a defect, not a video."""
    import imageio
    rd = imageio.get_reader(mp4)
    stds, diffs, prev, n = [], [], None, 0
    for i, fr in enumerate(rd):
        n += 1
        g = fr.astype(np.float32).mean(axis=2)
        stds.append(float(g.std()))
        if prev is not None:
            diffs.append(float(np.abs(g - prev).mean()))
        prev = g
    rd.close()
    stds = np.asarray(stds); diffs = np.asarray(diffs) if diffs else np.zeros(1)
    ok = bool(stds.min() > 4.0 and diffs.max() > 0.5 and np.median(diffs) > 0.05)
    return {"frames_read": n, "min_frame_std": round(float(stds.min()), 3),
            "max_interframe_delta": round(float(diffs.max()), 4),
            "median_interframe_delta": round(float(diffs.mean()), 4),
            "blank_frames": int((stds < 4.0).sum()),
            "frozen_pairs": int((diffs < 1e-3).sum()),
            "verdict": "PASS" if ok else "FAIL"}


# ------------------------------------------------------------ measuring -----

def measure(rp):
    """Per joint, off out/sim/walk_ours_traj.npz: MJCF range, travel used, peak
    angular velocity, with the frame index each extreme happened on."""
    out = {}
    for jn in common.JOINT_NAMES:
        q = np.degrees(rp.Q[:, rp.jadr[jn]])
        v = np.degrees(rp.V[:, rp.jdof[jn]])
        lo, hi = rp.jrange[jn]
        imin, imax = int(q.argmin()), int(q.argmax())
        iv = int(np.abs(v).argmax())
        out[jn] = {
            "mjcf_range_deg": [round(lo, 4), round(hi, 4)],
            "mjcf_range_span_deg": round(hi - lo, 4),
            "min_deg": round(float(q[imin]), 4), "min_at_frame": imin,
            "min_at_s": round(float(rp.t[imin]), 3),
            "max_deg": round(float(q[imax]), 4), "max_at_frame": imax,
            "max_at_s": round(float(rp.t[imax]), 3),
            "travel_deg": round(float(q[imax] - q[imin]), 4),
            "travel_pct_of_mjcf_range": round(float((q[imax] - q[imin]) / (hi - lo) * 100), 2),
            "peak_abs_vel_deg_s": round(float(np.abs(v[iv])), 3),
            "peak_vel_signed_deg_s": round(float(v[iv]), 3),
            "peak_vel_at_frame": iv, "peak_vel_at_s": round(float(rp.t[iv]), 3),
            "closest_approach_to_limit_deg": round(float(min(q.min() - lo, hi - q.max())), 4),
        }
    return out


def gait_cycle(rp, jn="left_knee", lo_s=1.5, hi_s=7.0):
    """Stride period from the autocorrelation of one joint's angle over the
    commanded window; returns (period_s, t_start, corr_peak, lag_frames)."""
    m = (rp.t >= lo_s) & (rp.t <= hi_s)
    x = np.degrees(rp.Q[m, rp.jadr[jn]])
    x = x - x.mean()
    ac = np.correlate(x, x, mode="full")[len(x) - 1:]
    ac = ac / ac[0]
    lo_lag = int(round(0.25 / rp.ctrl_dt))          # ignore lags below 0.25 s
    hi_lag = int(round(1.60 / rp.ctrl_dt))
    seg = ac[lo_lag:hi_lag]
    lag = int(np.argmax(seg)) + lo_lag
    period = lag * rp.ctrl_dt
    # start the cycle at a maximum of the signal, so the clip begins at a clean pose
    t0i = int(np.argmax(x[:lag])) + int(np.argmax(m))
    return float(period), float(rp.t[t0i]), float(ac[lag]), lag


# ------------------------------------------------------------- renders ------

def render_single(rp, name, W=960, H=720, fps=FPS):
    spec = CAMS[name]
    n = int(round((rp.t[-1] - rp.t[0]) * fps)) + 1
    lines = []

    def gen():
        for k in range(n):
            t = rp.t[0] + k / fps
            px = rp.shot(spec, t, W, H)
            rd = ["%s %+7.2f deg" % (j, rp.angle_deg(j)) for j in READOUT[name]]
            if name == "walk_body":
                rd.append("walked %.3f m   (50 mm floor squares)" % rp.walked(t))
            yield caption(px, WHAT[name], rd, t=t, frame=k), t
    info = write_video(name, gen(), n, fps=fps)
    info["what"] = WHAT[name]
    info["camera"] = "track %s, azimuth %d deg, elevation %d deg, distance %.3f m" % (
        spec[0], spec[1], spec[2], spec[3])
    return info


def render_composite(rp, name="walk_composite", TW=640, TH=480, fps=FPS):
    tiles = ["walk_body", "walk_knee_prof", "walk_hip_prof", "walk_ankle_prof"]
    n = int(round((rp.t[-1] - rp.t[0]) * fps)) + 1
    gap = 6

    def gen():
        for k in range(n):
            t = rp.t[0] + k / fps
            canvas = Image.new("RGB", (2 * TW + 3 * gap, 2 * TH + 3 * gap), (232, 233, 238))
            for j, nm in enumerate(tiles):
                px = rp.shot(CAMS[nm], t, TW, TH)
                rd = ["%s %+7.2f deg" % (a, rp.angle_deg(a)) for a in READOUT[nm]]
                px = caption(px, WHAT[nm], rd, t=t if j == 0 else None, frame=k if j == 0 else None)
                r, c = divmod(j, 2)
                canvas.paste(Image.fromarray(px), (gap + c * (TW + gap), gap + r * (TH + gap)))
            yield np.asarray(canvas), t
    info = write_video(name, gen(), n, fps=fps, cols=2)
    info["what"] = "2x2 composite on one timeline: %s" % ", ".join(tiles)
    info["camera"] = "; ".join("%s: az %d el %d d %.3f" % (nm, CAMS[nm][1], CAMS[nm][2], CAMS[nm][3])
                               for nm in tiles)
    return info


def trace_panel(rp, t0, t1, joints, W, H):
    """Static matplotlib panel of the joint angle traces over the clip window."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    m = (rp.t >= t0 - 1e-9) & (rp.t <= t1 + 1e-9)
    tt = rp.t[m]
    fig = plt.figure(figsize=(W / 100.0, H / 100.0), dpi=100)
    ax = fig.add_axes([0.055, 0.17, 0.925, 0.76])
    colors = {"left_hip_pitch": "#2f6fb2", "left_knee": "#c2521f",
              "left_ankle": "#2f7d52", "left_hip_roll": "#8a56a8", "left_hip_yaw": "#a08b2a"}
    for jn in joints:
        y = np.degrees(rp.Q[m, rp.jadr[jn]])
        ax.plot(tt, y, lw=2.0, color=colors.get(jn, "#444"), label="%s (travel %.2f deg)" % (
            jn, y.max() - y.min()))
    ax.set_xlim(t0, t1)
    ax.grid(True, color="#dcdde2", lw=0.7)
    ax.set_xlabel("simulation time (s)  —  out/sim/walk_ours_traj.npz, 50 Hz", fontsize=9)
    ax.set_ylabel("joint angle (deg)", fontsize=9)
    ax.tick_params(labelsize=8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(loc="upper right", fontsize=8, framealpha=0.9)
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())[:, :, :3].copy()
    plt.close(fig)
    return buf, t0, t1


def render_slowmo(rp, name="walk_slowmo", rate=0.25, fps=FPS, TW=640, TH=480):
    period, t0, corr, lag = gait_cycle(rp)
    lead = 0.08
    a, b = max(rp.t[0], t0 - lead), min(rp.t[-1], t0 + period + lead)
    dt = rate / fps                                  # 0.25x: 1/120 s of sim per frame
    n = int(round((b - a) / dt)) + 1
    PW = 2 * TW + 18
    PH = 380
    panel, _, _ = trace_panel(rp, a, b, ["left_hip_pitch", "left_knee", "left_ankle"], PW, PH)

    def gen():
        for k in range(n):
            t = a + k * dt
            top_l = caption(rp.shot(CAMS["walk_body"], t, TW, TH), "full body, 3/4 front-left",
                            ["gait cycle %.4f s, played at %.2fx" % (period, rate)], t=t, frame=k)
            top_r = caption(rp.shot(CAMS["walk_knee_prof"], t, TW, TH), WHAT["walk_knee_prof"],
                            ["left_knee %+7.2f deg" % rp.angle_deg("left_knee"),
                             "left_ankle %+7.2f deg" % rp.angle_deg("left_ankle")])
            canvas = Image.new("RGB", (PW, TH + PH + 18), (232, 233, 238))
            canvas.paste(Image.fromarray(top_l), (6, 6))
            canvas.paste(Image.fromarray(top_r), (12 + TW, 6))
            pan = Image.fromarray(panel).copy()
            d = ImageDraw.Draw(pan)
            # time cursor in the axes box set in trace_panel (left 0.055, width 0.925)
            x = (0.055 + 0.925 * (t - a) / (b - a)) * PW
            d.line([(x, 0.07 * PH), (x, 0.83 * PH)], fill=(200, 40, 40), width=3)
            canvas.paste(pan, (0, TH + 12))
            yield np.asarray(canvas), t
    info = write_video(name, gen(), n, fps=fps, cols=4)
    info["what"] = ("0.25x slow motion of one measured gait cycle (%.4f s, autocorrelation peak "
                    "%.4f at lag %d frames of left_knee) with the hip/knee/ankle angle traces and a "
                    "time cursor beneath" % (period, corr, lag))
    info["camera"] = "walk_body (az 225) + walk_knee_prof (az 270), both tracked"
    info["gait"] = {"period_s": round(period, 4), "cycle_start_s": round(a, 4),
                    "cycle_end_s": round(b, 4), "autocorr_peak": round(corr, 4),
                    "lag_frames_at_50hz": lag, "playback_rate": rate,
                    "sim_seconds_per_video_frame": round(dt, 6)}
    return info


# ---------------------------------------------------------------- main ------

def probe(rp):
    d = os.path.join(OUT, "probe")
    os.makedirs(d, exist_ok=True)
    for nm, spec in CAMS.items():
        for t in (1.0, 2.35):
            px = rp.shot(spec, t, 640, 480)
            rd = ["%s %+7.2f deg" % (j, rp.angle_deg(j)) for j in READOUT[nm]]
            px = caption(px, WHAT[nm], rd, t=t, frame=int(t * FPS))
            p = os.path.join(d, "%s_t%.2f.png" % (nm, t))
            Image.fromarray(px).save(p)
            g = px.astype(np.float32).mean(axis=2)
            print("%-16s t=%.2f std=%6.2f mean=%6.1f -> %s" % (nm, t, g.std(), g.mean(), p))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--only", default=None)
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    rp = Replay()
    if args.probe:
        probe(rp)
        return
    videos = {}
    todo = list(CAMS) if args.only is None else args.only.split(",")
    for nm in todo:
        if nm in CAMS:
            W, H = (960, 720) if nm == "walk_body" else (640, 480)
            print("=== %s" % nm, flush=True)
            videos[nm] = render_single(rp, nm, W, H)
            print(json.dumps(videos[nm]["verify"]), flush=True)
    if args.only is None or "walk_composite" in todo:
        print("=== walk_composite", flush=True)
        videos["walk_composite"] = render_composite(rp)
        print(json.dumps(videos["walk_composite"]["verify"]), flush=True)
    if args.only is None or "walk_slowmo" in todo:
        print("=== walk_slowmo", flush=True)
        videos["walk_slowmo"] = render_slowmo(rp)
        print(json.dumps(videos["walk_slowmo"]["verify"]), flush=True)

    period, t0, corr, lag = gait_cycle(rp)
    summ = json.load(open(os.path.join(ROOT, "out", "sim", "walk_ours_summary.json")))
    doc = {
        "what": "Pollen's BEST_alpha_walking policy on OUR rebuilt meshes, filmed and measured",
        "source_trajectory": "out/sim/walk_ours_traj.npz",
        "trajectory_written_by": "sim/run_policy.py --policy walking --robot ours --seconds 8 --vx 0.25",
        "rendered_by": "sim/motion_render.py --all",
        "scene": os.path.relpath(rp.scene_path, ROOT),
        "model": "sim/microduck_ours.xml (Pollen MJCF verbatim, our meshes on the visual geoms)",
        "walk": {"seconds": summ["seconds"], "control_hz": summ["control_hz"],
                 "commanded_vx_m_s": summ["command"]["vx"],
                 "walked_m": summ["walked_m"], "walked_x_m": summ["walked_x_m"],
                 "walked_y_m": summ["walked_y_m"],
                 "mean_speed_m_s": summ["mean_speed_m_s_commanded_window"],
                 "final_yaw_deg": summ["final_yaw_deg"], "max_tilt_deg": summ["max_tilt_deg"],
                 "trunk_z_m": summ["trunk_z_m"], "fell": summ["fell"],
                 "trajectory_frames": int(len(rp.t)), "frame_dt_s": rp.ctrl_dt},
        "gait": {"cycle_period_s": round(period, 4),
                 "cycle_frames_at_50hz": lag,
                 "autocorr_peak_of_left_knee": round(corr, 4),
                 "cadence_steps_per_min": round(2 * 60.0 / period, 2),
                 "stride_length_m": round(summ["walked_m"] / max(
                     (summ["seconds"] - 0.5) / period, 1e-9), 4),
                 "method": "autocorrelation of left_knee angle over t in [1.5, 7.0] s, "
                           "lags 0.25-1.60 s (sim/motion_render.py gait_cycle())"},
        "joints": measure(rp),
        "videos": videos,
    }
    json.dump(doc, open(os.path.join(OUT, "walk.json"), "w"), indent=1)
    print("wrote", os.path.join(OUT, "walk.json"))
    for nm, v in videos.items():
        print("%-16s %s  %s  gif %.2f MB  %s" % (nm, v["path"], v["verify"]["verdict"],
                                                 v["gif_mb"], v["contact_sheet"]))


if __name__ == "__main__":
    main()
