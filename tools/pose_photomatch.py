#!/usr/bin/env python3
"""pose_photomatch.py — recover the FULL articulated pose of every usable product
photograph as joint angles, and prove each pose is mechanically reachable.

Leif, 2026-09-03: "the cad render of the microduck shoukd have the exact same
mechanical pose as teh reference image with the mouth and legs and neck and all
servos should move properly in our renders to show that its mechanically feasable."

This EXTENDS tools/head_photomatch.py (the working per-photo camera+pose fitter)
to the whole body. Reused from it, not rewritten: the photograph silhouette rule,
the render->photo similarity (k, tx, ty), the IoU, the eye-ring ellipse measure,
the jaw hinge (body-frame y through (3.2, *, -18.0) mm, tools/head_probe.py) and
the perspective MuJoCo free camera whose frame spans +-HALF_FRAME_MM at the lookat.

What is fitted, per photograph (differential evolution then Nelder-Mead, exactly
as the head fitter):
  camera      elevation, azimuth, distance D (mm; whole-body perspective now
              carries near/far leg information, so D is fitted inside 600-2500 mm)
  base        trunk pitch and roll of the free joint (yaw is the camera azimuth)
  joints      ALL 14 MJCF hinges — left/right hip yaw, hip roll, hip pitch, knee,
              ankle; neck_pitch, head_pitch, head_yaw, head_roll — each searched
              ONLY inside its own MJCF range (sim/microduck_ours.xml), so a fitted
              pose is reachable by construction; a joint that runs to its bound is
              reported by name (at_bound), never silently accepted.
  jaw         the jaw opening in degrees. The jaw is NOT an actuated joint in
              Pollen's published model (no <joint> for it; the jaw + jaw_soft
              geoms are rigid in body jaw_soft). It is posed here by rotating those
              two geoms about the measured hinge line — a MODELLING CHOICE for the
              render, not a policy output — and the angle is reported as such.
  similarity  k, tx, ty between render pixels and photo pixels.

Objective = (1 - IoU of the WHOLE-ROBOT silhouettes)
          + w_land * sum |projected landmark - photo landmark|^2 / L^2
          + w_floor * ((z_sole_left - z_sole_right) / 10 mm)^2   [standing photos only]
where the landmarks are joint anchors (knee bearing, ankle horn, the two neck
horns) and the eye-ring centre, whose photo pixels were read off gridded crops
(+-15 px) and are drawn on the *_measure.png so a reader can check them, and
the floor term states that a standing robot's two soles share one plane.

For every fitted pose the tool then reports:
  * the range check per joint: MJCF range (deg) and the fitted value, PASS/FAIL
  * the self-collision census in that pose on the honest model
    sim/microduck_ours_selfcontact.xml (every geom contype/conaffinity 2, floor
    excluded) — every penetrating robot-robot contact pair with its depth
  * the residual silhouette IoU and the landmark residuals in mm at the photo scale
  * the fit's uncertainty per parameter: a profile-likelihood scan — how far each
    parameter can move (others fixed) before the objective rises by DELTA; a
    parameter that reaches its search box is reported UNCONSTRAINED by the photo
    (a hidden far leg in a profile shot is the expected case)
and renders OUR CAD in the studio (sim/compare_render.py's scene) at the fitted
camera + pose beside the real photograph with the silhouette overlay.

Checkpointing: out/pose/poses.json is rewritten after EVERY photo (entries merge
by id), so a killed run leaves every finished photo on disk.

    /Applications/FreeCAD.app/Contents/Resources/bin/python tools/pose_photomatch.py [--quick] [--only ID,ID] [--skip-done]
"""
import os, sys, json, math, time, argparse
os.environ.setdefault("MUJOCO_GL", "glfw")
import numpy as np
import mujoco
from PIL import Image, ImageDraw
from scipy import optimize, ndimage

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "sim")); sys.path.insert(0, os.path.join(REPO, "tools"))
import common, compare_render
import head_photomatch as hp     # the working fitter: reused, not rewritten

OUT = os.path.join(REPO, "out", "pose")
os.makedirs(OUT, exist_ok=True)
POSES_JSON = os.path.join(OUT, "poses.json")

HALF_FRAME_MM = 200.0      # the fit frame spans +-200 mm about the trunk: the whole 250 mm robot at any pose
JOINTS = list(common.JOINT_NAMES)          # 14, MJCF order (sim/common.py)
JAW_NOTE = ("the jaw is NOT an actuated joint in Pollen's published model (sim/microduck_ours.xml has no jaw <joint>; "
            "the jaw + jaw_soft geoms are rigid in body jaw_soft). It is posed for the render by rotating those two geoms "
            "about the hinge line measured in tools/head_probe.py (body-frame y through (3.2, *, -18.0) mm, the 15x10x3 "
            "bearing centre) — a modelling choice for the picture, not a policy output. The real jaw is driven by the "
            "mouth XL330 seen in press_desk.jpg (out/sources/internals/real_desk_head_jaw_off.png).")
DELTA_OBJ = 0.01           # profile-likelihood tolerance: objective rise that defines the +- of a parameter (1 % IoU)

# ----------------------------------------------------------------------------
# The photographs. Landmark pixels are in the ORIGINAL image, read off gridded
# crops (/private/tmp/pose-fit/grid_*.png, 100 px grid) at +-15 px; each is drawn
# on <id>_measure.png. Landmark keys: joint name -> that joint's anchor; "eye" ->
# the noenoeil geom centre (photo value from hp.measure_eye's ellipse centre).
LM_UNC_PX = 15.0
PHOTOS = [
    dict(id="cream-profile-left", path="images/store/store_microduck-cream-standing-profile-left.jpg",
         title="Cream, standing, left profile (store)", colourway="cream", standing=True,
         cam_az=270.0, az_free=5.0, el0=-3.0, jaw_open=True,
         eye_box=(735, 335, 1000, 585), eye_hue=(20, 55),
         landmarks={"head_pitch": (1227, 789), "neck_pitch": (1212, 1126), "left_knee": (1439, 1836), "left_ankle": (1498, 1975)},
         landmark_evidence="head_pitch = upper neck servo horn (screw circle at the top of the servo labelled DYNAMIXEL XL330-M288-T); "
                           "neck_pitch = the 4-screw bracket at the foot of the lower neck servo where it meets the trunk; left_knee = the "
                           "flanged bearing on the near shin at the top of the ankle servo; left_ankle = the horn screw circle on the orange "
                           "foot bracket",
         seed=dict(neck_pitch=0.0, head_pitch=-7.0, head_yaw=64.0, head_roll=-25.0, jaw=23.5,
                   left_hip_pitch=-26.0, left_knee=-0.3, left_ankle=26.0, right_hip_pitch=26.0, right_knee=0.3, right_ankle=-26.0)),
    dict(id="graphite-profile-right", path="images/store/store_microduck-graphite-standing-profile-right-02.jpg",
         title="Graphite, standing, right profile (store)", colourway="graphite", standing=True,
         cam_az=90.0, az_free=5.0, el0=3.0, jaw_open=False,
         eye_box=(1270, 320, 1480, 535), eye_hue=(255, 300), eye_smin=0.12,
         landmarks={"head_pitch": (1259, 839), "neck_pitch": (1223, 1165), "right_knee": (1071, 1866), "right_ankle": (992, 2011)},
         landmark_evidence="as cream-profile-left, mirrored: upper neck horn, lower neck bracket at the trunk, the near (right) shin's "
                           "flanged bearing, the near foot bracket's horn screw circle",
         seed=dict(neck_pitch=0.0, head_pitch=-21.0, head_yaw=-49.0, head_roll=9.4, jaw=0.0,
                   left_hip_pitch=-26.0, left_knee=-0.3, left_ankle=26.0, right_hip_pitch=26.0, right_knee=0.3, right_ankle=-26.0)),
    dict(id="sky-three-quarter-front-left", path="images/store/store_microduck-sky-standing-three-quarter-left-02.jpg",
         title="Sky, standing, three-quarter front-left, jaw open (store)", colourway="sky", standing=True,
         cam_az=240.0, az_free=25.0, el0=-7.0, jaw_open=True,
         eye_box=(800, 320, 1030, 545), eye_hue=(20, 55),
         landmarks={"head_pitch": (1157, 861), "right_knee": (1262, 1854), "left_ankle": (1486, 1976)},
         landmark_evidence="head_pitch = upper neck horn; right_knee = the far (right) shin's flanged bearing seen between the legs; "
                           "left_ankle = the near foot bracket's horn screw circle",
         seed=dict(neck_pitch=0.0, head_pitch=-21.0, head_yaw=38.6, head_roll=-19.6, jaw=21.5,
                   left_hip_pitch=-26.0, left_knee=-0.3, left_ankle=26.0, right_hip_pitch=26.0, right_knee=0.3, right_ankle=-26.0)),
    dict(id="graphite-back-three-quarter-right", path="images/store/store_microduck-graphite-standing-back-three-quarter-right-02.jpg",
         title="Graphite, standing, three-quarter back-right (store)", colourway="graphite", standing=True,
         cam_az=45.0, az_free=25.0, el0=-10.0, jaw_open=False, eye_box=None,
         landmarks={"left_knee": (994, 1873), "right_ankle": (1328, 1982)},
         landmark_evidence="left_knee = the far (left) shin's flanged bearing; right_ankle = the near foot bracket's horn screw circle; "
                           "no eye ring visible from behind, the neck horns are hidden by the head",
         seed=dict(neck_pitch=0.0, head_pitch=-10.0, head_yaw=0.0, head_roll=0.0, jaw=0.0,
                   left_hip_pitch=-26.0, left_knee=-0.3, left_ankle=26.0, right_hip_pitch=26.0, right_knee=0.3, right_ankle=-26.0)),
    dict(id="cream-sitting-three-quarter", path="images/store/store_microduck-cream-sitting-three-quarter_1.png",
         title="Cream, SITTING, three-quarter front-left, jaw open (store, alpha PNG)", colourway="cream", standing=False,
         cam_az=235.0, az_free=30.0, el0=-5.0, jaw_open=True,
         eye_box=(863, 403, 1098, 667), eye_hue=(20, 55),
         landmarks={"head_pitch": (1186, 990), "neck_pitch": (1142, 1313), "right_knee": (863, 1871), "left_ankle": (1435, 1930)},
         landmark_evidence="head_pitch = upper neck horn bracket; neck_pitch = lower neck bracket on the trunk; right_knee = the far "
                           "(right) shin's flanged bearing; left_ankle = the near foot bracket's horn screw circle",
         seed=dict(neck_pitch=5.0, head_pitch=-10.0, head_yaw=30.0, head_roll=-10.0, jaw=20.0,
                   left_hip_pitch=-80.0, left_knee=85.0, left_ankle=-10.0, right_hip_pitch=80.0, right_knee=-85.0, right_ankle=10.0)),
    dict(id="lavender-sitting-three-quarter-left", path="images/store/store_microduck-lavender-sitting-three-quarter-left-04.jpg",
         title="Lavender, SITTING, three-quarter front-left, jaw open (store)", colourway="lavender", standing=False,
         cam_az=235.0, az_free=30.0, el0=-5.0, jaw_open=True,
         eye_box=(920, 345, 1194, 618), eye_hue=(175, 215), eye_smin=0.12,
         landmarks={"head_pitch": (1209, 1059), "neck_pitch": (1178, 1279), "right_knee": (852, 1856), "left_ankle": (1474, 1924)},
         landmark_evidence="as cream-sitting-three-quarter",
         seed=dict(neck_pitch=5.0, head_pitch=-10.0, head_yaw=30.0, head_roll=-10.0, jaw=25.0,
                   left_hip_pitch=-80.0, left_knee=85.0, left_ankle=-10.0, right_hip_pitch=80.0, right_knee=-85.0, right_ankle=10.0)),
]


# ----------------------------------------------------------------------------
class BodyRenderer:
    """Poses the WHOLE robot (free-joint base + 14 hinges + the jaw geoms) and renders
    segmentation masks / shaded frames with the head fitter's perspective camera."""

    def __init__(self, model, data, size=400, half_frame_mm=HALF_FRAME_MM):
        self.model, self.data, self.size, self.half_frame = model, data, size, half_frame_mm
        self.r = mujoco.Renderer(model, size, size)
        self.r.enable_segmentation_rendering()
        self.opt = mujoco.MjvOption()
        self.cam = mujoco.MjvCamera(); self.cam.type = mujoco.mjtCamera.mjCAMERA_FREE
        self.trunk_bid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "trunk_base")
        self.head_bid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "jaw_soft")
        self.jid = {n: mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, n) for n in JOINTS}
        self.jadr = {n: int(model.jnt_qposadr[self.jid[n]]) for n in JOINTS}
        self.jrange_deg = {n: [float(math.degrees(v)) for v in model.jnt_range[self.jid[n]]] for n in JOINTS}
        self.gid = {}
        for g in range(model.ngeom):
            if model.geom_bodyid[g] != self.head_bid: continue
            mid = model.geom_dataid[g]
            if mid < 0: continue
            self.gid.setdefault(mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_MESH, mid), []).append(g)
        self.jaw_gids = sorted(g for m in hp.JAW_MESHES for g in self.gid.get(m, []))
        self.eye_gids = self.gid.get("noenoeil", [])
        self.jaw0 = {g: (model.geom_pos[g].copy(), model.geom_quat[g].copy()) for g in self.jaw_gids}
        self.robot_gids = np.array([g for g in range(model.ngeom) if model.geom_bodyid[g] != 0])
        self.sole = {}
        for g in range(model.ngeom):
            mid = model.geom_dataid[g]
            if mid < 0: continue
            nm = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_MESH, mid)
            if nm in ("sole_left", "sole_right") and nm not in self.sole: self.sole[nm] = g
        self.q0 = data.qpos.copy()

    def pose(self, joints_deg, jaw_deg, base_pitch_deg=0.0, base_roll_deg=0.0):
        d, m = self.data, self.model
        d.qpos[:] = self.q0
        d.qpos[0:3] = [0.0, 0.0, 0.30]          # base position is irrelevant (the camera tracks the trunk); high, clear of any floor
        q = np.zeros(4); qp = np.zeros(4); qr = np.zeros(4)
        mujoco.mju_axisAngle2Quat(qp, np.array([0.0, 1.0, 0.0]), math.radians(base_pitch_deg))
        mujoco.mju_axisAngle2Quat(qr, np.array([1.0, 0.0, 0.0]), math.radians(base_roll_deg))
        mujoco.mju_mulQuat(q, qp, qr); d.qpos[3:7] = q
        for n in JOINTS: d.qpos[self.jadr[n]] = math.radians(joints_deg[n])
        th = math.radians(jaw_deg)
        Rj = np.array([[math.cos(th), 0, math.sin(th)], [0, 1, 0], [-math.sin(th), 0, math.cos(th)]])
        qj = np.zeros(4); mujoco.mju_axisAngle2Quat(qj, np.array([0.0, 1.0, 0.0]), th)
        for g, (p0, q0) in self.jaw0.items():
            m.geom_pos[g] = hp.JAW_HINGE_BODY + Rj @ (p0 - hp.JAW_HINGE_BODY)
            qn = np.zeros(4); mujoco.mju_mulQuat(qn, qj, q0); m.geom_quat[g] = qn
        mujoco.mj_forward(m, d)

    def set_camera(self, az, el, distance_mm):
        D = distance_mm / 1000.0
        self.cam.azimuth = float(az); self.cam.elevation = float(el); self.cam.distance = D
        self.cam.lookat[:] = self.data.xpos[self.trunk_bid]
        self.model.vis.global_.fovy = math.degrees(2.0 * math.atan(self.half_frame / distance_mm))

    # the pinhole / projection code is the head fitter's, applied to this renderer
    pinhole = hp.HeadRenderer.pinhole
    project_points = hp.HeadRenderer.project_points

    def seg(self):
        self.r.update_scene(self.data, self.cam, self.opt)
        s = self.r.render()
        return s[:, :, 0].astype(np.int64), s[:, :, 1]

    def masks(self):
        ids, types = self.seg()
        isg = types == int(mujoco.mjtObj.mjOBJ_GEOM)
        robot = isg & (ids >= 0) & np.isin(ids, self.robot_gids)
        eye = np.isin(ids, self.eye_gids) & isg
        return robot, eye

    def shaded(self):
        self.r.disable_segmentation_rendering()
        self.r.update_scene(self.data, self.cam, self.opt)
        im = self.r.render().copy()
        self.r.enable_segmentation_rendering()
        return im

    def landmark_world(self, name):
        if name == "eye":
            return np.mean([self.data.geom_xpos[g] for g in self.eye_gids], axis=0)
        return np.array(self.data.xanchor[self.jid[name]], float)

    def sole_zmin(self, which):
        g = self.sole["sole_" + which]; m = self.model; mid = m.geom_dataid[g]
        a, n = m.mesh_vertadr[mid], m.mesh_vertnum[mid]
        v = m.mesh_vert[a:a + n]; R = self.data.geom_xmat[g].reshape(3, 3); t = self.data.geom_xpos[g]
        return float(((R @ v.T).T + t)[:, 2].min() * 1000)


# ----------------------------------------------------------------------------
def load_model():
    scene = compare_render.studio_scene(common.robot_file("ours"))
    model = mujoco.MjModel.from_xml_string(scene, {})
    data = mujoco.MjData(model)
    kid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, "PHOTO")
    mujoco.mj_resetDataKeyframe(model, data, kid); mujoco.mj_forward(model, data)
    return model, data


def photo_mask(path):
    """whole-robot silhouette of a store photograph: alpha when the PNG has one, else the head fitter's non-white rule
    tightened against the soft floor shadow (grey, low chroma, luminance > 200): a pixel is robot when its darkest
    channel is below 200 OR its chroma exceeds 20. Largest connected component, holes filled."""
    im = Image.open(path)
    if im.mode == "RGBA":
        a = np.asarray(im)[:, :, 3]; m = a > 127; rule = "alpha > 127 (RGBA PNG)"
        rgb = np.asarray(im.convert("RGB")).astype(np.int16)
    else:
        rgb = np.asarray(im.convert("RGB")).astype(np.int16)
        mn = rgb.min(axis=2); mx = rgb.max(axis=2)
        m = (mn < 200) | ((mx - mn) > 20); rule = "min channel < 200 or chroma > 20 (floor shadow excluded)"
    m = ndimage.binary_opening(m, iterations=1)
    lab, n = ndimage.label(m)
    if n > 1:
        sizes = ndimage.sum(m, lab, range(1, n + 1)); m = lab == (1 + int(np.argmax(sizes)))
    return ndimage.binary_fill_holes(m), rgb, rule


def param_names(ph):
    return ["cam_el", "cam_az", "cam_D", "base_pitch", "base_roll"] + JOINTS + ["jaw", "k", "tx", "ty"]


def unpack(p, ph):
    names = param_names(ph)
    d = dict(zip(names, [float(v) for v in p]))
    joints = {n: d[n] for n in JOINTS}
    return d, joints


def fit_photo(ph, br, pm_full, eye, quick=False, w_land=20.0, w_floor=0.01):
    ys, xs = np.nonzero(pm_full)
    pad = 60
    bx0, by0, bx1, by1 = max(0, xs.min() - pad), max(0, ys.min() - pad), xs.max() + pad, ys.max() + pad
    crop = pm_full[by0:by1, bx0:bx1]
    ds = max(1, int(round(max(crop.shape) / float(br.size))))     # photo px per fit px, so the photo robot ~ the render frame
    small = crop[::ds, ::ds]; HS, WS = small.shape
    area_p = small.sum(); cy_p, cx_p = np.nonzero(small)[0].mean(), np.nonzero(small)[1].mean()
    L_p = float(ys.max() - ys.min() + 1)                          # the robot's height in photo px, the landmark normaliser
    lms = dict(ph.get("landmarks", {}))
    if eye and "centre" in eye: lms["eye"] = tuple(eye["centre"])
    lm_names = sorted(lms); lm_px = np.array([lms[n] for n in lm_names], float) if lm_names else np.zeros((0, 2))

    def render(d, joints):
        br.pose(joints, d["jaw"] if ph["jaw_open"] else 0.0, d["base_pitch"], d["base_roll"])
        br.set_camera(d["cam_az"], d["cam_el"], d["cam_D"])
        return br.masks()

    def land_term(d):
        if not lm_names: return 0.0, None
        P = np.stack([br.landmark_world(n) for n in lm_names])
        uv, z = br.project_points(P)
        kf = d["k"] * ds
        pp = kf * uv + np.array([d["tx"] * ds + bx0, d["ty"] * ds + by0])
        res = pp - lm_px
        return float((res ** 2).sum() / L_p ** 2), res

    def floor_term():
        if not ph["standing"]: return 0.0, None
        dz = br.sole_zmin("left") - br.sole_zmin("right")
        return (dz / 10.0) ** 2, dz

    def eval_params(p, return_all=False):
        p = np.clip(p, lo_b, hi_b)
        d, joints = unpack(p, ph)
        mr, eyem = render(d, joints)
        tm = hp.transform_mask(mr, d["k"], d["tx"], d["ty"], (WS, HS))
        v = hp.iou(small, tm)
        lt, res = land_term(d); ft, dz = floor_term()
        obj = (1.0 - v) + w_land * lt + w_floor * ft
        if return_all: return obj, v, lt, res, ft, dz, mr, eyem, tm
        return obj

    # bounds: the joints get EXACTLY their MJCF ranges
    seed = ph.get("seed", {})
    bounds = [(ph["el0"] - 15, ph["el0"] + 15), (ph["cam_az"] - ph["az_free"], ph["cam_az"] + ph["az_free"]), (600.0, 2500.0),
              (-35.0, 35.0), (-20.0, 20.0)]
    for n in JOINTS: bounds.append(tuple(br.jrange_deg[n]))
    bounds.append((0.0, 40.0) if ph["jaw_open"] else (0.0, 1e-3))
    # k, tx, ty seeds from a first render at the seed pose
    j0 = {n: seed.get(n, math.degrees(common.DEFAULT_POSE[i])) for i, n in enumerate(JOINTS)}
    d0 = dict(cam_el=ph["el0"], cam_az=ph["cam_az"], cam_D=1100.0, base_pitch=0.0, base_roll=0.0, jaw=seed.get("jaw", 20.0))
    mr0, _ = render(d0, j0)
    ry, rx = np.nonzero(mr0)
    k0 = math.sqrt(area_p / max(1, mr0.sum()))
    tx0 = cx_p - k0 * rx.mean(); ty0 = cy_p - k0 * ry.mean()
    bounds += [(k0 * 0.6, k0 * 1.6), (tx0 - 100, tx0 + 100), (ty0 - 100, ty0 + 100)]
    lo_b = np.array([b[0] for b in bounds]); hi_b = np.array([b[1] for b in bounds])
    x0 = np.array([d0["cam_el"], d0["cam_az"], d0["cam_D"], 0.0, 0.0] + [j0[n] for n in JOINTS] + [d0["jaw"] if ph["jaw_open"] else 0.0, k0, tx0, ty0])
    x0 = np.clip(x0, lo_b, hi_b)
    t0 = time.time()
    res = optimize.differential_evolution(eval_params, bounds, maxiter=8 if quick else 30, popsize=6 if quick else 8,
                                          tol=1e-7, seed=1, polish=False, updating="immediate", x0=x0)
    res2 = optimize.minimize(eval_params, res.x, method="Nelder-Mead", options=dict(xatol=0.01, fatol=1e-7, maxfev=600 if quick else 3000))
    p = np.clip(res2.x if res2.fun < res.fun else res.x, lo_b, hi_b)
    best = float(min(res2.fun, res.fun))
    n_eval = int(res.nfev + res2.nfev)
    # re-polish from perturbed starts: the best of them is the answer, their spread is part of the uncertainty
    rng = np.random.default_rng(0); polishes = [(best, p)]
    for i in range(1 if quick else 3):
        p1 = p.copy(); p1[5:19] += rng.normal(0, 3.0, 14); p1[0] += rng.normal(0, 1.5)
        r3 = optimize.minimize(eval_params, np.clip(p1, lo_b, hi_b), method="Nelder-Mead", options=dict(xatol=0.01, fatol=1e-7, maxfev=300 if quick else 1200))
        polishes.append((float(r3.fun), np.clip(r3.x, lo_b, hi_b))); n_eval += int(r3.nfev)
    best, p = min(polishes, key=lambda t: t[0])
    obj, v, lt, lres, ft, dz, mr, eyem, tm = eval_params(p, True)
    d, joints = unpack(p, ph)
    names = param_names(ph)
    # profile-likelihood uncertainty: move each parameter alone until the objective rises by DELTA_OBJ
    unc = {}
    for i, nm in enumerate(names):
        if nm == "cam_az" and ph["az_free"] <= 0.01: continue
        if nm == "jaw" and not ph["jaw_open"]: continue
        lo, hi = bounds[i]; out = {}
        for sgn, lim, key in ((-1, lo, "minus"), (+1, hi, "plus")):
            step = max((hi - lo) / 60.0, 1e-3); x = p[i]; reached = False
            for _ in range(60):
                x2 = x + sgn * step
                if (sgn < 0 and x2 < lim) or (sgn > 0 and x2 > lim): x = lim; reached = True; break
                q = p.copy(); q[i] = x2
                if eval_params(q) - obj > DELTA_OBJ: break
                x = x2
            out[key] = float(abs(x - p[i])); out[key + "_hits_bound"] = bool(reached)
        unc[nm] = out
    at_bound = []
    for i, nm in enumerate(names):
        if nm == "cam_az" and ph["az_free"] <= 0.01: continue
        if nm == "jaw" and not ph["jaw_open"]: continue
        lo, hi = bounds[i]; span = hi - lo
        if span > 0 and min(abs(p[i] - lo), abs(hi - p[i])) <= 0.005 * span:
            at_bound.append(dict(param=nm, value=float(p[i]), bounds=[float(lo), float(hi)]))
    fit = dict(objective=float(obj), iou=float(v), landmark_term=float(lt), floor_term=float(ft), sole_dz_mm=dz,
               seconds=round(time.time() - t0, 1), n_eval=n_eval, polishes=[round(t[0], 5) for t in polishes],
               params=d, joints_deg={n: round(joints[n], 4) for n in JOINTS}, jaw_deg=round(d["jaw"], 4) if ph["jaw_open"] else 0.0,
               k_photo_px_per_render_px=d["k"] * ds, tx=d["tx"] * ds + bx0, ty=d["ty"] * ds + by0, ds=ds,
               bounds=dict(zip(names, [[float(a), float(b)] for a, b in bounds])), at_bound=at_bound, uncertainty=unc,
               crop_box=[int(bx0), int(by0), int(bx1), int(by1)], photo_height_px=L_p,
               landmarks=dict(names=lm_names, photo_px=lm_px.tolist(), residual_px=lres.tolist() if lres is not None else None,
                              unc_px=LM_UNC_PX))
    fit["_masks"] = (pm_full, mr, tm, crop, small, eyem)
    return fit


# ----------------------------------------------------------------------------
def range_check(br, joints):
    rows = []
    for n in JOINTS:
        lo, hi = br.jrange_deg[n]; v = joints[n]
        rows.append(dict(joint=n, fitted_deg=round(v, 4), range_deg=[round(lo, 4), round(hi, 4)],
                         verdict="PASS" if lo - 1e-6 <= v <= hi + 1e-6 else "FAIL",
                         margin_deg=round(min(v - lo, hi - v), 4),
                         source="sim/microduck_ours.xml joint %s range" % n))
    return rows


class SelfCollision:
    """the honest census model: every geom of every body contype/conaffinity 2 (sim/collision_model.py --write),
    posed to the fitted joints, robot-robot penetrations listed by body pair and depth."""
    def __init__(self):
        xml = common.scene_xml(common.robot_file("ours_selfcontact"))
        self.model = mujoco.MjModel.from_xml_string(xml, {})
        self.data = mujoco.MjData(self.model)
        self.jadr = {n: int(self.model.jnt_qposadr[mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_JOINT, n)]) for n in JOINTS}

    def check(self, joints):
        m, d = self.model, self.data
        mujoco.mj_resetData(m, d); d.qpos[0:3] = [0, 0, 0.5]; d.qpos[3:7] = [1, 0, 0, 0]
        for n in JOINTS: d.qpos[self.jadr[n]] = math.radians(joints[n])
        mujoco.mj_forward(m, d)
        pairs = []
        for i in range(d.ncon):
            c = d.contact[i]
            b1, b2 = m.geom_bodyid[c.geom1], m.geom_bodyid[c.geom2]
            if b1 == 0 or b2 == 0: continue
            if c.dist >= 0: continue
            pairs.append(dict(body1=mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, b1), body2=mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, b2),
                              geom1=int(c.geom1), geom2=int(c.geom2), depth_mm=round(-c.dist * 1000, 4)))
        return dict(model="sim/microduck_ours_selfcontact.xml (every geom contype=conaffinity=2; floor excluded, base at z 0.5 m)",
                    n_contacts_total=int(d.ncon), n_penetrating_robot_pairs=len(pairs), pairs=pairs,
                    verdict="PASS" if not pairs else "FAIL",
                    note="the jaw geoms are rigid in body jaw_soft in this model, so the posed jaw is NOT part of this census (same-body geoms never collide)")


# ----------------------------------------------------------------------------
def pictures(ph, rgb, fit, eye, br, hr_shaded):
    pm_full, mr, tm, crop, small, eyem = fit["_masks"]
    bx0, by0, bx1, by1 = fit["crop_box"]; H, W = pm_full.shape
    real = Image.fromarray(rgb.astype(np.uint8))
    # 1) measure picture: landmarks and the silhouette bbox on the photograph
    ann = real.copy(); d = ImageDraw.Draw(ann)
    for n, (x, y) in zip(fit["landmarks"]["names"], fit["landmarks"]["photo_px"]):
        d.ellipse([x - LM_UNC_PX, y - LM_UNC_PX, x + LM_UNC_PX, y + LM_UNC_PX], outline=(30, 120, 220), width=3)
        d.text((x + LM_UNC_PX + 4, y - 6), n, fill=(30, 120, 220))
    if fit["landmarks"]["residual_px"]:
        for (x, y), (rx, ry) in zip(fit["landmarks"]["photo_px"], fit["landmarks"]["residual_px"]):
            d.line([(x, y), (x + rx, y + ry)], fill=(230, 90, 20), width=3)
    if eye and "box" in eye: d.rectangle(eye["box"], outline=(30, 160, 60), width=2)
    ys, xs = np.nonzero(pm_full); d.rectangle([xs.min(), ys.min(), xs.max(), ys.max()], outline=(120, 60, 200), width=3)
    ann.crop((bx0, by0, bx1, by1)).save(os.path.join(OUT, "%s_measure.png" % ph["id"]))
    # 2) real | ours (studio, same camera + pose) | overlay
    realc = real.crop((bx0, by0, bx1, by1)); cw, chh = realc.size
    k = fit["k_photo_px_per_render_px"] * (hr_shaded.size / float(br.size))   # the shaded frame is rendered larger than the fit frame
    kk = fit["k_photo_px_per_render_px"]; tx = fit["tx"] - bx0; ty = fit["ty"] - by0
    a = 1.0 / (kk * br.size / float(hr_shaded.size))
    shaded = Image.fromarray(hr_shaded.shaded())
    ours = shaded.transform((cw, chh), Image.AFFINE, (a, 0, -tx * a, 0, a, -ty * a), resample=Image.BILINEAR, fillcolor=(255, 255, 255))
    ds = fit["ds"]; a2 = 1.0 / kk
    rm = Image.fromarray((mr * 255).astype(np.uint8)).transform((cw, chh), Image.AFFINE, (a2, 0, -tx * a2, 0, a2, -ty * a2), resample=Image.BILINEAR)
    hm = np.asarray(rm) > 127
    arr = np.asarray(realc.convert("RGBA")).copy()
    edge = ndimage.binary_dilation(hm ^ np.roll(hm, 1, 0) | hm ^ np.roll(hm, 1, 1), iterations=2)
    pe = ndimage.binary_dilation(crop ^ np.roll(crop, 1, 0) | crop ^ np.roll(crop, 1, 1), iterations=2)
    arr[pe] = (30, 90, 220, 255); arr[edge] = (230, 90, 20, 255)
    ov = Image.fromarray(arr).convert("RGB")
    tile_h = 900; sc = tile_h / chh; tw = int(cw * sc)
    sheet = Image.new("RGB", (tw * 3 + 40, tile_h + 70), (255, 255, 255)); dd = ImageDraw.Draw(sheet)
    J = fit["joints_deg"]
    labs = ["REAL  " + ph["title"],
            "OURS  studio, same camera (az %.1f el %.1f D %.0f mm) + fitted pose: L hip y/r/p %.1f/%.1f/%.1f knee %.1f ankle %.1f | R %.1f/%.1f/%.1f knee %.1f ankle %.1f" % (
                fit["params"]["cam_az"], fit["params"]["cam_el"], fit["params"]["cam_D"], J["left_hip_yaw"], J["left_hip_roll"], J["left_hip_pitch"], J["left_knee"], J["left_ankle"],
                J["right_hip_yaw"], J["right_hip_roll"], J["right_hip_pitch"], J["right_knee"], J["right_ankle"]),
            "OVERLAY  blue = photo silhouette, orange = ours   IoU %.4f | neck %.1f head p/y/r %.1f/%.1f/%.1f jaw %.1f (posed, not a joint)" % (
                fit["iou"], J["neck_pitch"], J["head_pitch"], J["head_yaw"], J["head_roll"], fit["jaw_deg"])]
    for i, (im, lab) in enumerate(zip([realc, ours, ov], labs)):
        sheet.paste(im.resize((tw, tile_h), Image.LANCZOS), (10 + i * (tw + 10), 50))
        dd.text((12 + i * (tw + 10), 10), lab[:int(tw / 6.2)], fill=(0, 0, 0))
        if len(lab) > int(tw / 6.2): dd.text((12 + i * (tw + 10), 26), lab[int(tw / 6.2):], fill=(0, 0, 0))
    sheet.save(os.path.join(OUT, "%s_pair.png" % ph["id"]))
    ours.save(os.path.join(OUT, "%s_ours.png" % ph["id"])); realc.save(os.path.join(OUT, "%s_real.png" % ph["id"]))
    ov.save(os.path.join(OUT, "%s_overlay.png" % ph["id"]))


def save_json(entries, quick):
    prev = {}
    if os.path.exists(POSES_JSON):
        try: prev = {e["id"]: e for e in json.load(open(POSES_JSON)).get("photos", [])}
        except Exception: prev = {}
    for e in entries: prev[e["id"]] = e
    order = [p["id"] for p in PHOTOS]
    photos = [prev[i] for i in order if i in prev] + [v for k, v in prev.items() if k not in order]
    out = dict(generated=time.strftime("%Y-%m-%d %H:%M"), method=__doc__, quick=quick, jaw_note=JAW_NOTE,
               joints=JOINTS, delta_obj=DELTA_OBJ, n_photos=len(photos),
               n_complete=sum(1 for p in photos if p.get("status") == "complete"), photos=photos)
    tmp = POSES_JSON + ".tmp"; json.dump(out, open(tmp, "w"), indent=1, default=float); os.replace(tmp, POSES_JSON)
    return POSES_JSON


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--quick", action="store_true"); ap.add_argument("--only")
    ap.add_argument("--skip-done", action="store_true", help="skip photos already complete in poses.json")
    args = ap.parse_args()
    done = set()
    if args.skip_done and os.path.exists(POSES_JSON):
        done = {e["id"] for e in json.load(open(POSES_JSON)).get("photos", []) if e.get("status") == "complete" and not e.get("quick")}
    model, data = load_model()
    br = BodyRenderer(model, data, size=300)
    hr_shaded = BodyRenderer(model, data, size=1600)
    sc = SelfCollision()
    for ph in PHOTOS:
        if args.only and ph["id"] not in args.only.split(","): continue
        if ph["id"] in done: print("skip (done)", ph["id"]); continue
        print("==", ph["id"]); sys.stdout.flush()
        pm_full, rgb, rule = photo_mask(os.path.join(REPO, ph["path"]))
        eye = hp.measure_eye(rgb, ph["eye_box"], ph["eye_hue"], smin=ph.get("eye_smin", 0.35)) if ph.get("eye_box") else None
        fit = fit_photo(ph, br, pm_full, eye, quick=args.quick)
        joints = fit["joints_deg"]
        rc = range_check(br, joints)
        col = sc.check(joints)
        # studio frame at the fitted camera + pose, for the pictures
        hr_shaded.pose(joints, fit["jaw_deg"], fit["params"]["base_pitch"], fit["params"]["base_roll"])
        hr_shaded.set_camera(fit["params"]["cam_az"], fit["params"]["cam_el"], fit["params"]["cam_D"])
        # landmark residuals in mm at the photo scale: k * (frame mm per render px)
        mm_per_photo_px = (2 * HALF_FRAME_MM / br.size) / fit["k_photo_px_per_render_px"]
        lres_mm = [[round(v * mm_per_photo_px, 3) for v in r] for r in fit["landmarks"]["residual_px"]] if fit["landmarks"]["residual_px"] else None
        pictures(ph, rgb, fit, eye, br, hr_shaded)
        entry = dict(id=ph["id"], title=ph["title"], path=ph["path"], colourway=ph["colourway"], standing=ph["standing"],
                     status="complete", quick=args.quick, image_size_px=[int(rgb.shape[1]), int(rgb.shape[0])],
                     silhouette_rule=rule,
                     camera=dict(azimuth_deg=round(fit["params"]["cam_az"], 4), elevation_deg=round(fit["params"]["cam_el"], 4),
                                 distance_mm=round(fit["params"]["cam_D"], 2), lookat="trunk_base body origin", frame_half_mm=HALF_FRAME_MM,
                                 note="MuJoCo free camera (compare_render.studio_scene); azimuth 270 = pure left profile, 90 = right, 180 = front"),
                     base=dict(pitch_deg=round(fit["params"]["base_pitch"], 4), roll_deg=round(fit["params"]["base_roll"], 4),
                               note="trunk_base free-joint orientation (yaw absorbed by the camera azimuth)"),
                     joints_deg=joints, jaw_deg=fit["jaw_deg"], jaw_note=JAW_NOTE,
                     range_check=rc, range_verdict="PASS" if all(r["verdict"] == "PASS" for r in rc) else "FAIL",
                     self_collision=col,
                     fit=dict(iou=round(fit["iou"], 4), objective=round(fit["objective"], 5), landmark_term=round(fit["landmark_term"], 6),
                              floor_term=round(fit["floor_term"], 6), sole_dz_mm=round(fit["sole_dz_mm"], 3) if fit["sole_dz_mm"] is not None else None,
                              seconds=fit["seconds"], n_eval=fit["n_eval"], polishes=fit["polishes"], at_bound=fit["at_bound"],
                              k_photo_px_per_render_px=fit["k_photo_px_per_render_px"], mm_per_photo_px=round(mm_per_photo_px, 5),
                              tx=fit["tx"], ty=fit["ty"], crop_box=fit["crop_box"], photo_height_px=fit["photo_height_px"], bounds=fit["bounds"]),
                     uncertainty=fit["uncertainty"],
                     landmarks=dict(names=fit["landmarks"]["names"], photo_px=fit["landmarks"]["photo_px"], residual_px=fit["landmarks"]["residual_px"],
                                    residual_mm=lres_mm, read_unc_px=LM_UNC_PX, evidence=ph.get("landmark_evidence", ""),
                                    how="photo px read off a 100 px gridded crop of the original; model point = the joint's MuJoCo anchor "
                                        "(xanchor) or the noenoeil geom centre, projected through the fit frame's pinhole and the fitted similarity"),
                     eye=eye if eye else dict(verdict="CANNOT DETERMINE", why="no eye ring visible in this view"),
                     pictures=dict(pair="out/pose/%s_pair.png" % ph["id"], overlay="out/pose/%s_overlay.png" % ph["id"],
                                   measure="out/pose/%s_measure.png" % ph["id"], ours="out/pose/%s_ours.png" % ph["id"]),
                     inputs=dict(cam_az=ph["cam_az"], az_free=ph["az_free"], el0=ph["el0"], jaw_open=ph["jaw_open"], eye_box=ph.get("eye_box"),
                                 eye_hue=ph.get("eye_hue"), seed=ph.get("seed")))
        path = save_json([entry], args.quick)
        print(json.dumps({k: entry[k] for k in ("camera", "base", "joints_deg", "jaw_deg", "range_verdict")}, indent=None, default=float))
        print("self-collision:", col["verdict"], col["n_penetrating_robot_pairs"], "iou %.4f obj %.5f at_bound %s" % (fit["iou"], fit["objective"], fit["at_bound"]))
        print("wrote", path); sys.stdout.flush()


if __name__ == "__main__":
    main()
