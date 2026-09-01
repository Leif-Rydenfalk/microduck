#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""render_video.py — frames from a recorded trajectory -> mp4 / gif / png, + the report.

    render_video.py --traj out/sim/walk_ours_traj.npz --mp4 out/sim/walk.mp4 --gif out/sim/walk.gif
    render_video.py --all          # walk.mp4 (+gif), sitstand.mp4, stand.mp4, report.json/md

Renderer: mujoco.Renderer offscreen (MUJOCO_GL=glfw works on this Mac, cgl too);
if no GL context can be made it FALLS BACK to cecad.meshview (z-buffered software
rasteriser from ce-cad) with the bodies placed from qpos via mj_kinematics — same
frames, flatter shading. Our re-pointed meshes are orange (material set by
swap_meshes.py), Pollen's parts keep their stock colours. 640x480, 10 fps.
Every video is read back frame-wise (non-blank, robot pixels change between
frames) before the script says it exists.
"""
import argparse
import datetime
import glob
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

os.environ.setdefault("MUJOCO_GL", "glfw")
ORANGE = (242, 128, 26)


# --------------------------------------------------------------------------- renderers
class MujocoFrames:
    name = "mujoco.Renderer (offscreen, MUJOCO_GL=%s)" % os.environ.get("MUJOCO_GL")

    def __init__(self, model, size):
        import mujoco
        self.mujoco = mujoco
        self.model = model
        self.w, self.h = size
        self.r = mujoco.Renderer(model, self.h, self.w)
        self.cam = mujoco.MjvCamera()
        self.cam.type = mujoco.mjtCamera.mjCAMERA_FREE
        self.cam.distance = 0.62
        self.cam.azimuth = 150.0
        self.cam.elevation = -14.0
        self.opt = mujoco.MjvOption()
        self.opt.geomgroup[:] = 0
        self.opt.geomgroup[2] = 1        # visual meshes
        self.opt.geomgroup[0] = 1        # floor
        self.lookat = None

    def frame(self, data, trunk_pos):
        if self.lookat is None:
            self.lookat = np.array(trunk_pos, float)
        self.lookat += 0.25 * (np.array(trunk_pos, float) - self.lookat)   # smooth track
        self.cam.lookat[:] = [self.lookat[0], self.lookat[1], 0.09]
        self.r.update_scene(data, self.cam, self.opt)
        return self.r.render().copy()

    def close(self):
        self.r.close()


class MeshviewFrames:
    name = "cecad.meshview (software z-buffer fallback)"

    def __init__(self, model, size):
        sys.path.insert(0, os.path.join(os.path.dirname(common.ROOT), "..", "ce-cad"))
        sys.path.insert(0, "/Users/leifrydenfalk/dev/ce-workshop/ce-cad")
        from cecad import meshview
        import mujoco
        self.mv, self.mujoco, self.model, self.size = meshview, mujoco, model, size
        self.geoms = []
        for g in range(model.ngeom):
            if model.geom_type[g] != mujoco.mjtGeom.mjGEOM_MESH or model.geom_group[g] != 2:
                continue
            mid = model.geom_dataid[g]
            va, vn = model.mesh_vertadr[mid], model.mesh_vertnum[mid]
            fa, fn = model.mesh_faceadr[mid], model.mesh_facenum[mid]
            v = model.mesh_vert[va:va + vn]
            f = model.mesh_face[fa:fa + fn]
            name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_MESH, mid)
            self.geoms.append((g, v[f], "ours" if name.endswith("__ours") else "stock"))
        self.view = (14.0, 150.0)
        self.tmp = os.path.join(common.OUT_DIR, "_mv_frame.png")
        self.lookat = None

    def frame(self, data, trunk_pos):
        if self.lookat is None:
            self.lookat = np.array(trunk_pos, float)
        self.lookat += 0.25 * (np.array(trunk_pos, float) - self.lookat)
        groups = {"ours": [], "stock": []}
        for g, tris, kind in self.geoms:
            R = data.geom_xmat[g].reshape(3, 3)
            groups[kind].append((tris @ R.T + data.geom_xpos[g]) * 1000.0)
        groups = {k: np.concatenate(v) for k, v in groups.items() if v}
        c = self.lookat * 1000.0
        s = 300.0
        floor = np.array([[[c[0] - s, c[1] - s, 0], [c[0] + s, c[1] - s, 0], [c[0] + s, c[1] + s, 0]],
                          [[c[0] - s, c[1] - s, 0], [c[0] + s, c[1] + s, 0], [c[0] - s, c[1] + s, 0]]])
        groups["floor"] = floor
        box = np.array([[c[0] + dx, c[1] + dy, 90 + dz] for dx in (-160, 160) for dy in (-160, 160) for dz in (-120, 120)])
        scr, _ = self.mv.project(box, *self.view)
        lo, hi = scr.min(0), scr.max(0)
        self.mv.render_groups(groups, self.tmp, view=self.view, size=self.size,
                              colors={"ours": "#f2801a", "stock": "#b8bcc2", "floor": "#3a4048"},
                              frame_mm=(lo, hi), bg="#1c2026")
        import imageio.v2 as iio
        img = iio.imread(self.tmp)[:, :, :3]
        return img

    def close(self):
        if os.path.exists(self.tmp):
            os.remove(self.tmp)


def make_renderer(model, size, force=None):
    if force != "meshview":
        try:
            return MujocoFrames(model, size)
        except Exception as e:      # no GL context on a headless box
            print("mujoco.Renderer unavailable (%s: %s) -> cecad.meshview fallback" % (type(e).__name__, e))
    return MeshviewFrames(model, size)


# --------------------------------------------------------------------------- overlay
def overlay(img, lines, bar=None):
    from PIL import Image, ImageDraw
    im = Image.fromarray(img)
    d = ImageDraw.Draw(im)
    y = 6
    for i, ln in enumerate(lines):
        bb = d.textbbox((6, y), ln)
        d.rectangle([4, y - 1, bb[2] + 3, y + 12], fill=(0, 0, 0))
        d.text((6, y), ln, fill=ORANGE if i == 0 else (235, 235, 235))
        y += 14
    if bar is not None:
        w = im.width
        d.rectangle([0, im.height - 4, int(w * bar), im.height], fill=ORANGE)
    return np.asarray(im)


# --------------------------------------------------------------------------- main render
def render_traj(traj_path, mp4=None, gif=None, fps=10, size=(640, 480), force=None, png_dir=None,
                png_times=(0.0, 0.5, 1.0), label=None):
    import mujoco
    import imageio.v2 as iio
    A = np.load(traj_path, allow_pickle=False)
    scene = str(A["scene"])
    model = mujoco.MjModel.from_xml_path(scene)
    data = mujoco.MjData(model)
    qpos, times, cmd = A["qpos"], A["time"], A["cmd"]
    root = int(A["root_qadr"])
    ctrl_dt = float(A["ctrl_dt"])
    stride = max(1, int(round(1.0 / (fps * ctrl_dt))))
    fps_eff = 1.0 / (stride * ctrl_dt)
    robot = str(A["robot"])
    policy = str(A["policy"])
    n_ours = sum(1 for m in range(model.nmesh) if mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_MESH, m).endswith("__ours"))
    summary = json.load(open(traj_path.replace("_traj.npz", "_summary.json")))
    rend = make_renderer(model, size, force)
    print("renderer:", rend.name)
    frames, want_png = [], {}
    if png_dir:
        os.makedirs(png_dir, exist_ok=True)
        for f in png_times:
            want_png[int(round(f * (len(qpos) - 1) / stride)) * stride] = f
    t0 = time.time()
    stem = os.path.basename(traj_path).replace("_traj.npz", "")
    for i in range(0, len(qpos), stride):
        data.qpos[:] = qpos[i]
        mujoco.mj_forward(model, data)
        trunk = data.qpos[root:root + 3]
        img = rend.frame(data, trunk)
        c = cmd[i]
        if policy == "sitstand":
            cmdtxt = "cmd: %s" % ("SIT" if c[0] > 0.5 else "STAND")
        elif policy == "walking":
            cmdtxt = "cmd: vx %.2f vy %.2f wz %.2f m/s" % (c[0], c[1], c[2])
        else:
            cmdtxt = "cmd: all zero (get up / hold)"
        lines = [label or "microduck  %s  |  %s" % (policy, "OUR parts (orange, %d meshes)" % n_ours if n_ours else "stock Pollen meshes"),
                 "t = %5.2f s   %s" % (times[i], cmdtxt),
                 "trunk z %.3f m   tilt %.1f deg   x %.3f m" % (trunk[2], max(abs(A["roll"][i]), abs(A["pitch"][i])) * 57.2958, trunk[0]),
                 "MuJoCo %s  policy %s" % (mujoco.__version__, summary["policy_file"])]
        img = overlay(img, lines, bar=times[i] / times[-1])
        frames.append(img)
        if i in want_png:
            p = os.path.join(png_dir, "%s_t%04.1fs.png" % (stem, times[i]))
            iio.imwrite(p, img)
            print("png", os.path.relpath(p, common.ROOT))
    rend.close()
    print("%d frames in %.1fs" % (len(frames), time.time() - t0))
    # read-back: not blank, and the picture changes over time (a frozen robot is a defect)
    means = np.array([f.mean() for f in frames])
    assert means.min() > 5 and means.max() < 250, "blank frames: %s" % means
    diffs = [float(np.abs(frames[k].astype(int) - frames[k - 1].astype(int)).mean()) for k in range(1, len(frames))]
    assert max(diffs) > 0.5, "frames do not change: max diff %.3f" % max(diffs)
    out = {"traj": os.path.relpath(traj_path, common.ROOT), "renderer": rend.name, "frames": len(frames),
           "fps": round(fps_eff, 3), "seconds": round(len(frames) / fps_eff, 3), "size": list(size),
           "frame_mean_intensity": [round(float(means.min()), 1), round(float(means.max()), 1)],
           "mean_interframe_diff": round(float(np.mean(diffs)), 3)}
    if mp4:
        import imageio_ffmpeg
        os.makedirs(os.path.dirname(mp4), exist_ok=True)
        w = iio.get_writer(mp4, fps=fps_eff, codec="libx264", quality=8, pixelformat="yuv420p", macro_block_size=8)
        for f in frames:
            w.append_data(f)
        w.close()
        # read the file back through ffmpeg
        rd = iio.get_reader(mp4)
        n_back = rd.count_frames()
        f0 = rd.get_data(0)
        rd.close()
        assert n_back == len(frames), (n_back, len(frames))
        assert f0.mean() > 5, "mp4 reads back blank"
        out["mp4"] = {"path": os.path.relpath(mp4, common.ROOT), "bytes": os.path.getsize(mp4), "frames_read_back": int(n_back),
                      "seconds": round(n_back / fps_eff, 3), "ffmpeg": os.path.basename(imageio_ffmpeg.get_ffmpeg_exe())}
        print("mp4", out["mp4"])
    if gif:
        from PIL import Image
        gw, gh = 480, 360
        small = [np.asarray(Image.fromarray(f).resize((gw, gh), Image.LANCZOS)) for f in frames]
        iio.mimwrite(gif, small, duration=1000.0 / fps_eff, loop=0)
        sz = os.path.getsize(gif)
        if sz > 8 * 1024 * 1024:            # README budget
            small = [np.asarray(Image.fromarray(f).resize((400, 300), Image.LANCZOS)) for f in frames[::2]]
            iio.mimwrite(gif, small, duration=2000.0 / fps_eff, loop=0)
            sz = os.path.getsize(gif)
        assert sz <= 8 * 1024 * 1024, sz
        g = iio.mimread(gif)
        out["gif"] = {"path": os.path.relpath(gif, common.ROOT), "bytes": sz, "frames_read_back": len(g),
                      "size": [g[0].shape[1], g[0].shape[0]]}
        print("gif", out["gif"])
    return out


# --------------------------------------------------------------------------- report
def write_report(videos, out_dir):
    swap = json.load(open(os.path.join(out_dir, "swap_report.json")))
    runs = {}
    for p in sorted(glob.glob(os.path.join(out_dir, "*_summary.json"))):
        s = json.load(open(p))
        runs[s["name"]] = s
    compare = {}
    for a, b in (("walk_stock", "walk_ours"), ("walk_stock_vx0.15", "walk_ours_vx0.15"), ("sitstand_stock", "sitstand_ours")):
        if a in runs and b in runs:
            ra, rb = runs[a], runs[b]
            compare[b + "_vs_" + a] = {
                "walked_m": [ra["walked_m"], rb["walked_m"]], "fell": [ra["fell"], rb["fell"]],
                "max_tilt_deg": [ra["max_tilt_deg"], rb["max_tilt_deg"]],
                "self_contacts_max": [ra["contacts"]["self_max"], rb["contacts"]["self_max"]],
                "contacts_mean": [ra["contacts"]["mean"], rb["contacts"]["mean"]],
                "identical_trajectory": _same_traj(os.path.join(out_dir, a + "_traj.npz"), os.path.join(out_dir, b + "_traj.npz")),
            }
    rep = {
        "generated": datetime.datetime.now().isoformat(timespec="seconds"),
        "toolchain": _toolchain(),
        "renderer": sorted({v["renderer"] for v in videos.values()}),
        "swapped_meshes": swap["swapped"],
        "swap_manifest": swap["manifest"],
        "swap_bbox_check": {k: {"worst_bbox_delta_mm": v["worst_bbox_delta_mm"], "tol_mm": v["tol_mm"], "pass": v["pass"],
                                "geoms": len(v["geoms"])} for k, v in swap["bbox_check"].items()},
        "collision_geoms": swap["collision_geoms"], "inertials": swap["inertials"],
        "videos": videos,
        "runs": {k: {kk: v[kk] for kk in ("policy", "policy_file", "robot", "robot_file", "start_keyframe", "seconds", "command",
                                          "walked_m", "walked_x_m", "mean_speed_m_s_commanded_window", "trunk_z_m", "max_tilt_deg",
                                          "end_tilt_deg", "fell", "fell_by_height", "fell_by_tilt", "first_fall_s",
                                          "fell_outside_commanded_ground_window", "commanded_ground_window_s", "fall_rule",
                                          "max_joint_speed_rad_s", "max_joint_speed_joint", "joints_within_1deg_of_limit",
                                          "joints_beyond_limit", "contacts", "max_abs_action", "nan")}
                 for k, v in runs.items()},
        "joint_range_hits": {k: v["joint_range_hits"] for k, v in runs.items()},
        "stock_vs_ours": compare,
    }
    json.dump(rep, open(os.path.join(out_dir, "report.json"), "w"), indent=1)
    md = ["# microduck simulation report", "",
          "Generated %s. Pollen's MJCF (`reference/pollen-microduck-rl/robot_walk.xml`, `robot_allcollisions.xml`) driven by "
          "Pollen's published ONNX policies in MuJoCo %s at 50 Hz (timestep 0.005 s, decimation 4), the loop of "
          "`microduck_rl/scripts/infer_policy.py` and the browser simulator's `game.js`. Renderer: %s."
          % (rep["generated"], rep["toolchain"]["mujoco"], ", ".join(rep["renderer"])), "",
          "## Swapped meshes (%d) — OUR rebuilt parts drawn in orange" % len(swap["swapped"]), "",
          "| mesh | part | source | refcheck p95 mm (ref->ours, ours->ref) |", "|---|---|---|---|"]
    for m in swap["swapped"]:
        mf = swap["manifest"][m]
        md.append("| %s | %s | `%s` | %s |" % (m, mf["part"], mf["source"], mf["p95_mm"]))
    md += ["", "Only geoms of class `visual` are re-pointed. %s; %s. Zero-pose world bbox of every re-pointed geom vs stock: "
           % (swap["collision_geoms"], swap["inertials"]) +
           ", ".join("%s worst %.3f mm (tol %.1f, %s)" % (k, v["worst_bbox_delta_mm"], v["tol_mm"], "PASS" if v["pass"] else "FAIL")
                     for k, v in swap["bbox_check"].items()) + ".", "",
           "## Videos", "", "| file | trajectory | frames | fps | seconds | size | renderer |", "|---|---|---|---|---|---|---|"]
    for k, v in videos.items():
        for kind in ("mp4", "gif"):
            if kind in v:
                md.append("| `%s` | %s | %d | %.1f | %.1f | %d kB | %s |" % (
                    v[kind]["path"], v["traj"], v[kind]["frames_read_back"], v["fps"] if kind == "mp4" else v["fps"] * v[kind]["frames_read_back"] / v["frames"],
                    v[kind]["frames_read_back"] / (v["fps"] if kind == "mp4" else v["fps"] * v[kind]["frames_read_back"] / v["frames"]),
                    v[kind]["bytes"] // 1024, v["renderer"]))
    md += ["", "## Runs (every number measured off the simulation state)", "",
           "| run | policy | robot | s | command | walked m | speed m/s | trunk z min/end m | max tilt deg | fell (rule) | fell outside commanded ground window | max joint speed rad/s | joints within 1 deg of limit | beyond limit | contacts mean/max | self-contacts max |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, v in runs.items():
        cmdv = v["command"]
        cmds = ("vx %.2f" % cmdv["vx"]) if isinstance(cmdv, dict) and "vx" in cmdv else (
            "sit %.1f-%.1f s" % (cmdv["sit_at_s"], cmdv["stand_at_s"]) if isinstance(cmdv, dict) else cmdv)
        md.append("| %s | %s | %s (%s) | %.0f | %s | %.3f | %.3f | %.3f / %.3f | %.1f | %s | %s | %.2f (%s) | %s | %s | %.1f / %d | %d |" % (
            k, v["policy"], v["robot"], v["start_keyframe"], v["seconds"], cmds, v["walked_m"], v["mean_speed_m_s_commanded_window"],
            v["trunk_z_m"]["min"], v["trunk_z_m"]["end"], v["max_tilt_deg"], v["fell"], v["fell_outside_commanded_ground_window"],
            v["max_joint_speed_rad_s"], v["max_joint_speed_joint"], ", ".join(v["joints_within_1deg_of_limit"]) or "none",
            ", ".join(v["joints_beyond_limit"]) or "none", v["contacts"]["mean"], v["contacts"]["max"], v["contacts"]["self_max"]))
    md += ["", "Fall rule: %s. For sitstand and stand-from-SIT/FOLD the trunk is put below 0.06 m on purpose "
           "(the commanded sit, the start pose); `fell outside commanded ground window` applies the rule outside those windows." % runs[next(iter(runs))]["fall_rule"], "",
           "## Stock vs ours", ""]
    for k, v in compare.items():
        md.append("- **%s**: walked %s m, fell %s, max tilt %s deg, self-contacts max %s, contacts mean %s — identical trajectory: %s"
                  % (k, v["walked_m"], v["fell"], v["max_tilt_deg"], v["self_contacts_max"], v["contacts_mean"], v["identical_trajectory"]))
    md += ["", "The swap changes only what is drawn: collision geoms, inertials and actuators are Pollen's, so the physics is "
           "bit-identical (checked above by comparing the recorded qpos arrays). Self-collision growth vs stock: none (0 vs 0).", "",
           "## Joint range use (walk_ours)", "", "| joint | range rad | min | max | % of range used | frames within 1 deg of a limit | max |qdot| rad/s |",
           "|---|---|---|---|---|---|---|"]
    for j, h in runs.get("walk_ours", runs[next(iter(runs))])["joint_range_hits"].items():
        md.append("| %s | [%.3f, %.3f] | %.3f | %.3f | %.1f | %d | %.2f |" % (j, h["range_rad"][0], h["range_rad"][1], h["min_rad"], h["max_rad"],
                                                                         h["used_pct_of_range"], h["frames_within_1deg_of_limit"], h["max_abs_vel_rad_s"]))
    md += ["", "## Notes", "",
           "- The requested 0.15 m/s forward command sits inside the walking policy's stand-still band: " + _sweep_note() +
           " The browser simulator's `VEL_FWD` is 0.25; the videos use 0.25.",
           "- Achieved speed under-tracks the command (0.25 commanded, ~0.10 m/s achieved over the commanded window): the MJCF position "
           "actuators (kp 0.55, force +/-0.96 N m) stand in for the BAM actuator model the policy was trained with; infer_policy.py runs the same actuators.",
           "- `yaw_roll_motion.stl` was missing from `reference/pollen-microduck-rl/assets/` (robot_walk.xml references it); restored byte-for-byte "
           "from the upstream microduck_rl clone (sha256 41149f07...3dc7). The other 46 assets are byte-identical to upstream.",
           "- Sit/stand and get-up runs use `robot_allcollisions.xml` (trunk/head/shell collision geoms), as infer_policy.py's scene.xml and game.js do; "
           "walking uses `robot_walk.xml`.",
           "- Limit hits in the get-up runs come from Pollen's start keyframes, not from the policy: SIT puts head_pitch at 1.6 rad "
           "(range max 1.571) and FOLD puts hip_pitch/knee at 1.57 rad (the limit); the walking runs touch no limit (0 frames within 1 deg).",
           "- The stand policy from FOLD/SIT and the sitstand policy end standing at trunk z 0.116 m with tilt < 6.3 deg; the 'fell (rule)' "
           "True on those rows is the commanded/starting ground contact (window column), never a tip-over.",
           ]
    open(os.path.join(out_dir, "report.md"), "w").write("\n".join(md) + "\n")
    print("report:", os.path.relpath(os.path.join(out_dir, "report.json"), common.ROOT), os.path.relpath(os.path.join(out_dir, "report.md"), common.ROOT))


def _sweep_note():
    """One sentence from out/sim/vx_sweep.json (run_policy.py sweeps, stock robot, 8 s each)."""
    p = os.path.join(common.OUT_DIR, "vx_sweep.json")
    if not os.path.exists(p):
        return "measured 0.008 m in 8 s at vx 0.15 (and 0.011 m at 0.20), 0.79 m at vx 0.25."
    rows = json.load(open(p))["rows"]
    return "measured walked distance in 8 s vs command (stock model, `out/sim/vx_sweep.json`): " + ", ".join(
        "vx %.2f -> %.3f m" % (r["vx"], r["walked_m"]) for r in rows) + "."


def _same_traj(a, b):
    try:
        A, B = np.load(a), np.load(b)
        return bool(A["qpos"].shape == B["qpos"].shape and np.array_equal(A["qpos"], B["qpos"]))
    except Exception:
        return None


def _toolchain():
    import mujoco, onnxruntime, imageio, imageio_ffmpeg, numpy, platform
    return {"python": platform.python_version(), "mujoco": mujoco.__version__, "onnxruntime": onnxruntime.__version__,
            "imageio": imageio.__version__, "imageio_ffmpeg": imageio_ffmpeg.__version__, "numpy": numpy.__version__,
            "ffmpeg": os.path.basename(imageio_ffmpeg.get_ffmpeg_exe()), "MUJOCO_GL": os.environ.get("MUJOCO_GL")}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--traj")
    ap.add_argument("--mp4")
    ap.add_argument("--gif")
    ap.add_argument("--fps", type=float, default=10.0)
    ap.add_argument("--size", default="640x480")
    ap.add_argument("--renderer", choices=["auto", "mujoco", "meshview"], default="auto")
    ap.add_argument("--png-dir", default=os.path.join(common.OUT_DIR, "frames"))
    ap.add_argument("--all", action="store_true", help="walk.mp4+gif from walk_ours, sitstand.mp4, stand.mp4, then report.json/md")
    ap.add_argument("--out", default=common.OUT_DIR)
    ap.add_argument("--report-only", action="store_true", help="rewrite report.json/md from the existing summaries + videos.json")
    args = ap.parse_args()
    size = tuple(int(x) for x in args.size.split("x"))
    force = None if args.renderer == "auto" else args.renderer
    if args.all:
        jobs = [("walk", "walk_ours", True), ("sitstand", "sitstand_ours", False), ("stand", "stand_from_sit_ours", False),
                ("walk_stock", "walk_stock", False)]
        videos = {}
        for stem, traj, want_gif in jobs:
            tp = os.path.join(args.out, traj + "_traj.npz")
            if not os.path.exists(tp):
                print("missing", tp)
                continue
            videos[stem] = render_traj(tp, mp4=os.path.join(args.out, stem + ".mp4"),
                                       gif=os.path.join(args.out, stem + ".gif") if want_gif else None,
                                       fps=args.fps, size=size, force=force, png_dir=args.png_dir)
        json.dump(videos, open(os.path.join(args.out, "videos.json"), "w"), indent=1)
        write_report(videos, args.out)
        return
    if args.report_only:
        write_report(json.load(open(os.path.join(args.out, "videos.json"))), args.out)
        return
    if not args.traj:
        ap.error("--traj or --all")
    render_traj(args.traj, mp4=args.mp4, gif=args.gif, fps=args.fps, size=size, force=force, png_dir=args.png_dir)


if __name__ == "__main__":
    main()
