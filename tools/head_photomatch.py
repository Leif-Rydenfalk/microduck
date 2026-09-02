#!/usr/bin/env python3
"""head_photomatch.py — SETTLE the head question by measurement (GOAL.md handover
correction 1; Leif: "im not sure that the simulation meshes are the same as their
product meshes! you have to use the images as references").

For every usable product photograph the answer is built from four measurements,
each of which is drawn on the annotated picture so a reader can check it:

  1. SCALE  — mm per pixel from a feature of known size IN THE SAME FRAME: the
     XL330-M288-T servo case. ROBOTIS's specification table gives the case as
     "Dimensions (W x H x D) 20.0 x 34.0 x 26.0 [mm]" (XL330_SRC below). Which
     face the camera sees is READ off the published MJCF, not assumed: the servo
     mesh is 20.000 wide (mesh x) x 34.06 tall (mesh z) x 29.04 (mesh y = 26 case
     + 3.04 horn), and in the neck body mesh x = world -x, mesh z = world -z, so a
     profile camera sees the 20.000 x 34.0 horn/label face (tools/head_probe.py
     output, quoted in head.json). The case width is read as the MODE of the
     dark-run widths across many rows (label text and cables break single rows;
     the mode is the case). Uncertainty: +-1 px per edge plus the spread of the
     accepted rows.
  2. POSE   — our model (Pollen's published meshes in Pollen's kinematic tree,
     sim/microduck_ours.xml) is posed to the photograph with a PERSPECTIVE camera
     (MuJoCo free camera; distance D is a fitted parameter because the store shots
     are taken close enough that the near and far edges of the head differ in
     scale — 4 % at 0.5 m, measured below). Fitted: camera elevation, azimuth (for
     a 3/4 shot), distance, head pitch / yaw / roll, the jaw opening (the jaw is
     NOT a joint in the published model, so the jaw + jaw_soft geoms are rotated
     about the measured hinge line — body-frame y through (3.2, *, -18.0) mm, the
     15x10x3 bearing centre), and a similarity (k, tx, ty) between render pixels
     and photo pixels. The objective is silhouette IoU of the head region PLUS
     the eye-ring ellipse (centre, major, minor) — a circle's image pins yaw and
     pitch far better than a silhouette does.
  3. SIZE   — the same servo is measured in the RENDER at the fitted camera (the
     segmentation mask of that xl330 geom, same mode-of-runs estimator), so the
     product/mesh size ratio needs no px-per-mm calibration of the renderer:
        r = k * W_render / W_photo
     (one render px = k photo px; the servo is W_render render px and W_photo
     photo px; if the product head were the mesh head, W_photo would be
     k * W_render). The perspective camera puts the servo and the head at their
     real depths, so the depth difference is modelled, not assumed away.
     Head-length deviation = 122.690 * (r - 1) mm; per-axis deviations are the
     photo head extents along its own principal axes minus the render extents at
     the servo-anchored scale, in mm.
  4. EYE    — the eye ring is a circle in 3D, so its image is an ellipse whose
     MAJOR axis is the true diameter whatever the viewing angle. Measured from the
     accent-hue pixels (HSV hue + saturation, so the shaded rim counts) against
     the noenoeil mesh: a 30.000 mm cylinder 7.5 mm long standing proud of the
     face panel (cecad.meshfeatures on reference/pollen-microduck-rl/assets/
     noenoeil.stl: boss d 30.0 length 7.5; face_part carries only a 14.5 mm lens
     hole, so the whole 30 mm ring is visible).

Writes out/head/head.json and the overlays out/head/<id>_{pair,measure,overlay,
ours,real}.png (real beside ours, always). FreeCAD's python has mujoco, numpy,
PIL, scipy:
    /Applications/FreeCAD.app/Contents/Resources/bin/python tools/head_photomatch.py [--quick] [--only ID]
"""
import os, sys, json, math, time, argparse
os.environ.setdefault("MUJOCO_GL", "glfw")
import numpy as np
import mujoco
from PIL import Image, ImageDraw
from scipy import optimize, ndimage

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "sim"))
import common, compare_render

OUT = os.path.join(REPO, "out", "head")
os.makedirs(OUT, exist_ok=True)

# ----------------------------------------------------------------------------
# Known sizes, with their sources
XL330_FACE_W_MM = 20.000
XL330_SRC = ("ROBOTIS e-manual, XL330-M288-T, Specifications table: 'Dimensions (W x H x D) 20.0 x 34.0 x 26.0 [mm]', "
             "https://emanual.robotis.com/docs/en/dxl/x/xl330-m288/ (fetched 2026-09-02; the same table at "
             "https://docs.robotis.com/docs/dxl/model_reference/x_series/xl_series/xl330-m288/, which links XL330.pdf/.dwg/.stp). "
             "Face seen: the 20.000 x 34.0 horn/label face — the servo mesh in Pollen's MJCF is 20.000 (mesh x) x 34.06 (mesh z) x "
             "29.04 (mesh y = 26.0 case + 3.04 horn) and in the neck body mesh x = world -x, mesh z = world -z (tools/head_probe.py).")
HEAD_MESH_MM = {"top_head_shell": (91.7595, 122.69, 46.3361), "bottom_head_shell": (91.763, 116.7483, 20.1363),
                "noenoeil": (30.0, 9.5, 30.0), "jaw": (91.4158, 68.7105, 29.4477)}  # out/verify/mech_dims.json
HEAD_LEN_MM = 122.690      # top_head_shell mesh, front-to-back (out/verify/mech_dims.json)
EYE_RING_D_MM = 30.000     # noenoeil mesh: boss d 30.0 length 7.5 (cecad.meshfeatures, this session)
EYE_SRC = ("reference/pollen-microduck-rl/assets/noenoeil.stl via cecad.meshfeatures.cylinders(scale=1000): "
           "boss d_mm 30.0 length 7.5 axis y; hole d 14.4 length 6.0. face_part.stl: hole d 14.5 length 1.3 at the same axis, "
           "no 30 mm opening — the ring stands proud of the face panel (noenoeil y -63.5..-54.0, face_part front at y -55.5).")
HALF_FRAME_MM = 95.0       # the render frames +-95 mm about the head at every distance (fovy follows D)

# ----------------------------------------------------------------------------
# The photographs. Pixel coordinates are in the ORIGINAL image. Every seed /
# polygon below was read off a gridded crop of the photograph (scratchpad
# necks.png / grid crops) and is drawn on the *_measure.png so a reader can check.
PHOTOS = [
    dict(id="cream-profile-left",
         path="images/store/store_microduck-cream-standing-profile-left.jpg",
         title="Cream, standing, left profile (store)", colourway="cream",
         cam_az=270.0, az_free=False, el0=-8.0, D_mm=1100.0, D_source="camera distance to the head: not measurable from this frame to better than a factor 2 (the near ankle servo, 44.1 mm nearer than the neck servos, reads 136.2-145.5 px against the neck's 131.4 px depending on the scan tilt, i.e. D 700-1650 mm); 1100 mm is the centre of that range and the sensitivity runs at 700 and 1600 mm bracket it (out/head/head_fit_*_D700.json / _D1600.json)",
         servo_scans=[dict(rows=(760, 920), seed_x=1222, what="upper neck servo (head_pitch), horn/label face", geom="neck_upper"),
                      dict(rows=(925, 1070), seed_x=1218, what="lower neck servo (neck_pitch), horn/label face", geom="neck_lower")],
         eye_box=(735, 335, 1000, 585), eye_hue=(20, 55), eye_hue_note="orange-yellow ring on the cream unit",
         head_ycut=985,
         neck_poly=[(1120, 1150), (1120, 815), (1200, 790), (1280, 762), (1340, 745), (1420, 745), (1420, 1150)],
         jaw_open=True, note="head yawed towards the camera, jaw open"),
    dict(id="sky-three-quarter-front-left",
         path="images/store/store_microduck-sky-standing-three-quarter-left-02.jpg",
         title="Sky, standing, three-quarter front-left (store)", colourway="sky",
         cam_az=225.0, az_free=True, el0=-10.0, D_mm=1100.0, D_source="camera distance to the head: not measurable from this frame either; same store shoot, same value assumed to better than a factor 2 (the near ankle servo, 44.1 mm nearer than the neck servos, reads 136.2-145.5 px against the neck's 131.4 px depending on the scan tilt, i.e. D 700-1650 mm); 1100 mm is the centre of that range and the sensitivity runs at 700 and 1600 mm bracket it (out/head/head_fit_*_D700.json / _D1600.json)",
         servo_scans=[dict(rows=(880, 975), seed_x=1200, what="upper neck servo (head_pitch), label face + side face", geom="neck_upper"),
                      dict(rows=(1015, 1115), seed_x=1160, what="lower neck servo (neck_pitch), label face + side face", geom="neck_lower")],
         eye_box=(800, 320, 1030, 545), eye_hue=(20, 55), eye_hue_note="orange-yellow ring on the sky unit",
         head_ycut=1000,
         neck_poly=[(1060, 1300), (1060, 840), (1150, 830), (1250, 805), (1330, 790), (1440, 760), (1500, 760), (1500, 1300)],
         jaw_open=True, note="three-quarter view, jaw open; camera azimuth fitted"),
    dict(id="graphite-profile-right",
         path="images/store/store_microduck-graphite-standing-profile-right-02.jpg",
         title="Graphite, standing, right profile (store)", colourway="graphite",
         cam_az=90.0, az_free=False, el0=-8.0, D_mm=1100.0, D_source="camera distance to the head: not measurable from this frame either; same store shoot, same value assumed to better than a factor 2 (the near ankle servo, 44.1 mm nearer than the neck servos, reads 136.2-145.5 px against the neck's 131.4 px depending on the scan tilt, i.e. D 700-1650 mm); 1100 mm is the centre of that range and the sensitivity runs at 700 and 1600 mm bracket it (out/head/head_fit_*_D700.json / _D1600.json)",
         # the neck servos' faces are covered by the horn brackets in this shot; the near ankle servo's label face is clear
         servo_scans=[dict(rows=(1865, 1945), seed_x=950, what="near (right) ankle servo, label face; tilted with the shin",
                           geom="ankle_right", tilt_deg=35.0)],
         eye_box=(1270, 320, 1480, 535), eye_hue=(255, 300), eye_hue_note="lavender ring on the graphite unit", eye_smin=0.12,
         head_ycut=1000,
         neck_poly=[(1150, 1300), (1150, 800), (1200, 780), (1260, 758), (1320, 740), (1400, 720), (1520, 690), (1700, 600), (1700, 1300)],
         jaw_open=False, note="head yawed towards the camera, jaw closed; scale from the ankle servo (44 mm nearer the camera than the head — the perspective camera carries that)"),
]

HEAD_GEOM_MESHES = ["top_head_shell", "bottom_head_shell", "face_part", "noenoeil", "lens", "m12_lens_holder",
                    "jaw", "jaw_soft", "soft_mouth_top"]
JAW_MESHES = ["jaw", "jaw_soft"]
JAW_HINGE_BODY = np.array([0.0032, 0.0, -0.018])   # m, jaw_soft body frame; axis = body y (tools/head_probe.py: bearing bbox centre)
# servo geoms by role: (body, index among that body's xl330 geoms sorted by world z)
SERVO_GEOMS = {"neck_lower": ("neck", 0), "neck_upper": ("neck", 1), "ankle_right": ("leg_2", 0), "ankle_left": ("leg", 0)}


# ----------------------------------------------------------------------------
def load_model():
    scene = compare_render.studio_scene(common.robot_file("ours"))
    model = mujoco.MjModel.from_xml_string(scene, {})
    data = mujoco.MjData(model)
    kid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, "PHOTO")
    mujoco.mj_resetDataKeyframe(model, data, kid)
    mujoco.mj_forward(model, data)
    return model, data


class HeadRenderer:
    """Poses the head joints + jaw and renders segmentation masks with a
    PERSPECTIVE camera whose frame always spans +-HALF_FRAME_MM at the lookat."""

    def __init__(self, model, data, size=1000):
        self.model, self.data, self.size = model, data, size
        self.r = mujoco.Renderer(model, size, size)
        self.r.enable_segmentation_rendering()
        self.opt = mujoco.MjvOption()
        self.cam = mujoco.MjvCamera(); self.cam.type = mujoco.mjtCamera.mjCAMERA_FREE
        self.cam.orthographic = 0
        self.head_bid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "jaw_soft")
        self.gid = {}
        for g in range(model.ngeom):
            if model.geom_bodyid[g] != self.head_bid: continue
            mid = model.geom_dataid[g]
            if mid < 0: continue
            self.gid.setdefault(mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_MESH, mid), []).append(g)
        self.head_gids = sorted(g for m in HEAD_GEOM_MESHES for g in self.gid.get(m, []))
        self.jaw_gids = sorted(g for m in JAW_MESHES for g in self.gid.get(m, []))
        self.eye_gids = self.gid.get("noenoeil", [])
        self.jaw0 = {g: (model.geom_pos[g].copy(), model.geom_quat[g].copy()) for g in self.jaw_gids}
        self.jadr = {n: int(model.jnt_qposadr[mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, n)])
                     for n in ("neck_pitch", "head_pitch", "head_yaw", "head_roll")}
        self.q0 = data.qpos.copy()
        # servo geoms by role
        self.servo = {}
        for role, (body, idx) in SERVO_GEOMS.items():
            bid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, body)
            gs = [g for g in range(model.ngeom) if model.geom_bodyid[g] == bid and model.geom_dataid[g] >= 0
                  and mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_MESH, model.geom_dataid[g]).startswith("xl330")]
            gs.sort(key=lambda g: data.geom_xpos[g][2])
            self.servo[role] = gs[idx]

    def pose(self, pitch_deg, yaw_deg, roll_deg, jaw_deg, neck_pitch_deg=None):
        """pitch_deg = the head's pitch relative to the trunk, 0 = LEVEL (eye-ring axis horizontal),
        positive = face up. The neck_pitch and head_pitch hinges have OPPOSITE axes in the MJCF
        (world -y and +y, tools/head_probe.py), so the head orientation is head_pitch - neck_pitch:
        with neck_pitch at the STAND value the level head has head_pitch = neck_pitch (STAND: 20/20).
        Verified by bisection on the noenoeil geom's axis elevation (tools/head_frontview.py)."""
        d = self.data; m = self.model
        d.qpos[:] = self.q0
        npitch = math.radians(neck_pitch_deg) if neck_pitch_deg is not None else float(common.DEFAULT_POSE[5])
        d.qpos[self.jadr["neck_pitch"]] = npitch
        d.qpos[self.jadr["head_pitch"]] = npitch + math.radians(pitch_deg)
        d.qpos[self.jadr["head_yaw"]] = math.radians(yaw_deg)
        d.qpos[self.jadr["head_roll"]] = math.radians(roll_deg)
        th = math.radians(jaw_deg)
        Rj = np.array([[math.cos(th), 0, math.sin(th)], [0, 1, 0], [-math.sin(th), 0, math.cos(th)]])
        qj = np.zeros(4); mujoco.mju_axisAngle2Quat(qj, np.array([0.0, 1.0, 0.0]), th)
        for g, (p0, q0) in self.jaw0.items():
            m.geom_pos[g] = JAW_HINGE_BODY + Rj @ (p0 - JAW_HINGE_BODY)
            qn = np.zeros(4); mujoco.mju_mulQuat(qn, qj, q0); m.geom_quat[g] = qn
        mujoco.mj_forward(m, d)

    def set_camera(self, az, el, distance_mm):
        D = distance_mm / 1000.0
        self.cam.azimuth = float(az); self.cam.elevation = float(el); self.cam.distance = D
        self.cam.lookat[:] = self.data.xpos[self.head_bid]
        self.model.vis.global_.fovy = math.degrees(2.0 * math.atan(HALF_FRAME_MM / distance_mm))

    def seg(self):
        self.r.update_scene(self.data, self.cam, self.opt)
        s = self.r.render()
        return s[:, :, 0].astype(np.int64), s[:, :, 1]

    def masks(self):
        ids, types = self.seg()
        isg = types == int(mujoco.mjtObj.mjOBJ_GEOM)
        head = np.isin(ids, self.head_gids) & isg
        eye = np.isin(ids, self.eye_gids) & isg
        return head, eye, ids, isg

    def servo_mask(self, role, ids=None, isg=None):
        if ids is None: ids, isg = self.seg(); isg = isg == int(mujoco.mjtObj.mjOBJ_GEOM)
        return (ids == self.servo[role]) & isg

    def shaded(self):
        self.r.disable_segmentation_rendering()
        self.r.update_scene(self.data, self.cam, self.opt)
        im = self.r.render().copy()
        self.r.enable_segmentation_rendering()
        return im

    def servo_depths_mm(self, role):
        """camera-depth of the servo centre and of the head body origin, mm (for the report)."""
        c = self.r.scene.camera[0]
        fwd = np.array(c.forward, float); pos = np.array(c.pos, float)
        gs = self.data.geom_xpos[self.servo[role]]
        return float((gs - pos) @ fwd * 1000), float((self.data.xpos[self.head_bid] - pos) @ fwd * 1000)


# ----------------------------------------------------------------------------
# Photograph measurements
def load_rgb(path):
    return np.asarray(Image.open(path).convert("RGB")).astype(np.int16)


def hsv(rgb):
    r, g, b = [rgb[..., i].astype(float) / 255 for i in range(3)]
    mx = np.max(rgb, axis=2) / 255.; mn = np.min(rgb, axis=2) / 255.; d = mx - mn
    s = np.where(mx > 0, d / np.maximum(mx, 1e-6), 0)
    dd = np.maximum(d, 1e-6); m = d > 1e-6
    h = np.where(m & (mx == r), ((g - b) / dd) % 6, 0) + np.where(m & (mx == g) & (mx != r), (b - r) / dd + 2, 0) \
        + np.where(m & (mx == b) & (mx != r) & (mx != g), (r - g) / dd + 4, 0)
    return h * 60, s, mx


def silhouette(rgb):
    """non-white pixels: min channel below 228 or chroma above 14 (the cream shell
    is (247,230,203)-ish, so a plain luminance threshold loses it)."""
    mn = rgb.min(axis=2); mx = rgb.max(axis=2)
    return (mn < 228) | ((mx - mn) > 14)


def runs_along(L, p0, direction, thresh):
    """dark run through p0 along +-direction (unit vector) in the luminance image L: returns (a, b) in px."""
    H, W = L.shape
    def walk(sgn):
        t = 0.0
        while True:
            x = p0[0] + sgn * (t + 1) * direction[0]; y = p0[1] + sgn * (t + 1) * direction[1]
            xi, yi = int(round(x)), int(round(y))
            if xi < 0 or yi < 0 or xi >= W or yi >= H or L[yi, xi] >= thresh: return t
            t += 1.0
    if L[int(round(p0[1])), int(round(p0[0]))] >= thresh: return None
    return walk(-1), walk(+1)


def measure_servo(rgb, scan, thresh=110):
    """width of the servo case (px) as the MODE of the dark-run widths over many
    scan lines perpendicular to the servo's long axis (tilt_deg, 0 = vertical
    servo, runs horizontal). Rows through label text or a cable give short/long
    runs; the case gives the same width on every clean row, which is the mode."""
    L = rgb.mean(axis=2)
    r0, r1 = scan["rows"]; tilt = math.radians(scan.get("tilt_deg", 0.0))
    # scan lines: step along the servo axis (tilted), runs perpendicular to it
    axis = np.array([math.sin(tilt), math.cos(tilt)])      # image-down direction of the servo's long axis
    perp = np.array([math.cos(tilt), -math.sin(tilt)])     # across the case
    c0 = np.array([scan["seed_x"], (r0 + r1) / 2.0], float)
    n = int(r1 - r0); rows = []
    for i in range(n):
        p = c0 + (i - n / 2.0) * axis
        rr = runs_along(L, p, perp, thresh)
        if rr is None: continue
        a, b = rr
        rows.append((float(p[0]), float(p[1]), a, b, a + b + 1))
    if len(rows) < 5: return dict(verdict="CANNOT DETERMINE", why="fewer than 5 scan lines with a dark run at the seed", what=scan["what"])
    w = np.array([r[4] for r in rows])
    hist = np.bincount(np.round(w).astype(int))
    mode = int(np.argmax(hist))
    acc = [r for r in rows if abs(r[4] - mode) <= 2.0]
    wa = np.array([r[4] for r in acc])
    width = float(wa.mean())
    unc = math.sqrt(2.0 + wa.var())      # +-1 px per edge (2 px^2) + the accepted rows' spread
    return dict(what=scan["what"], geom=scan["geom"], rows=[r0, r1], seed_x=scan["seed_x"], tilt_deg=scan.get("tilt_deg", 0.0),
                n_lines=len(rows), n_accepted=len(acc), width_px_mode=mode, width_px=width, width_px_unc=unc,
                width_px_min=float(w.min()), width_px_max=float(w.max()),
                lines=[(r[0], r[1], r[2], r[3]) for r in acc[:: max(1, len(acc) // 12)]],
                mm_per_px=XL330_FACE_W_MM / width, mm_per_px_unc=XL330_FACE_W_MM / width * unc / width)


def measure_servo_mask(mask, tilt_deg=0.0):
    """same estimator on a render segmentation mask: mode of the run widths across the case."""
    ys, xs = np.nonzero(mask)
    if len(xs) < 50: return dict(verdict="CANNOT DETERMINE", why="servo not visible in the render (%d px)" % len(xs))
    tilt = math.radians(tilt_deg)
    axis = np.array([math.sin(tilt), math.cos(tilt)]); perp = np.array([math.cos(tilt), -math.sin(tilt)])
    P = np.stack([xs, ys], 1).astype(float); c = P.mean(0)
    ta = (P - c) @ axis
    widths = []
    for t in np.arange(np.percentile(ta, 15), np.percentile(ta, 85), 1.0):
        sel = np.abs(ta - t) < 0.5
        if sel.sum() < 2: continue
        tp = (P[sel] - c) @ perp
        widths.append(tp.max() - tp.min() + 1)
    w = np.array(widths)
    hist = np.bincount(np.round(w).astype(int)); mode = int(np.argmax(hist))
    wa = w[np.abs(w - mode) <= 2.0]
    return dict(n_lines=len(w), n_accepted=len(wa), width_px_mode=mode, width_px=float(wa.mean()),
                width_px_unc=math.sqrt(2.0 + wa.var()), width_px_min=float(w.min()), width_px_max=float(w.max()),
                centre_px=[float(c[0]), float(c[1])])


def ellipse_of(P):
    """principal-axis extents of a point cloud (px): centre, major, minor, major direction."""
    c = P.mean(0); C = np.cov((P - c).T); w, V = np.linalg.eigh(C)
    major = V[:, 1]; minor = V[:, 0]
    pm = (P - c) @ major; pn = (P - c) @ minor
    ext_major = float(np.percentile(pm, 99.5) - np.percentile(pm, 0.5))
    ext_minor = float(np.percentile(pn, 99.5) - np.percentile(pn, 0.5))
    return dict(centre=[float(c[0]), float(c[1])], major_px=ext_major, minor_px=ext_minor,
                major_axis_dir=[float(major[0]), float(major[1])])


def measure_eye(rgb, box, hue, smin=0.35, vmin=0.25):
    """accent-hue pixels in the box (HSV: hue window, saturation > smin so the shaded
    rim counts) -> ellipse. The MAJOR axis of a circle's image is its diameter."""
    x0, y0, x1, y1 = box
    sub = rgb[y0:y1, x0:x1]
    h, s, v = hsv(sub)
    m = (h >= hue[0]) & (h <= hue[1]) & (s > smin) & (v > vmin)
    m = ndimage.binary_opening(m, iterations=2)
    lab, n = ndimage.label(m)
    if n == 0: return dict(verdict="CANNOT DETERMINE", why="no accent-hue pixels in the eye box")
    sizes = ndimage.sum(m, lab, range(1, n + 1)); m = lab == (1 + int(np.argmax(sizes)))
    m = ndimage.binary_fill_holes(m)
    ys, xs = np.nonzero(m)
    if len(xs) < 200: return dict(verdict="CANNOT DETERMINE", why="fewer than 200 ring pixels", n=int(len(xs)))
    e = ellipse_of(np.stack([xs + x0, ys + y0], 1).astype(float))
    e.update(n_px=int(len(xs)), view_angle_deg=float(math.degrees(math.acos(max(-1, min(1, e["minor_px"] / e["major_px"]))))),
             unc_px=2.0, box=list(box), hue=list(hue))
    return e


def head_region_mask(rgb, ph):
    sil = silhouette(rgb)
    H, W = sil.shape
    sil[ph["head_ycut"]:, :] = False
    poly = Image.new("1", (W, H), 0); ImageDraw.Draw(poly).polygon(ph["neck_poly"], fill=1)
    sil &= ~np.asarray(poly, bool)
    lab, n = ndimage.label(sil)
    if n > 1:
        sizes = ndimage.sum(sil, lab, range(1, n + 1))
        sil = lab == (1 + int(np.argmax(sizes)))
    return ndimage.binary_fill_holes(sil)


# ----------------------------------------------------------------------------
# The fit
def transform_mask(mask_r, k, tx, ty, out_size):
    """render mask (px) -> photo-crop coords: x_p = k*x_r + tx. PIL wants the inverse."""
    im = Image.fromarray((mask_r * 255).astype(np.uint8))
    a = 1.0 / k
    out = im.transform(out_size, Image.AFFINE, (a, 0, -tx * a, 0, a, -ty * a), resample=Image.BILINEAR)
    return np.asarray(out) > 127


def iou(a, b):
    inter = np.logical_and(a, b).sum(); uni = np.logical_or(a, b).sum()
    return inter / uni if uni else 0.0


def fit_photo(ph, hr, rgb, eye, quick=False, w_eye=10.0):
    pm_full = head_region_mask(rgb, ph)
    ys, xs = np.nonzero(pm_full)
    pad = 40
    bx0, by0, bx1, by1 = max(0, xs.min() - pad), max(0, ys.min() - pad), xs.max() + pad, ys.max() + pad
    ds = 2
    crop = pm_full[by0:by1, bx0:bx1]
    small = crop[::ds, ::ds]
    HS, WS = small.shape
    area_p = small.sum(); cy_p, cx_p = np.nonzero(small)[0].mean(), np.nonzero(small)[1].mean()
    L_p = max(crop.shape)   # normaliser for the eye term (full-res px)
    eye_ok = "centre" in eye
    if eye_ok:
        ec = np.array(eye["centre"]) - np.array([bx0, by0]); e_maj, e_min = eye["major_px"], eye["minor_px"]

    D_mm = ph["D_mm"]

    neck = ph.get("neck_pitch_deg", 0.0)   # the store photographs show a vertical neck; STAND's leans 20 deg

    def render(p):
        el, az, pitch, yaw, roll, jaw = p
        hr.pose(pitch, yaw, roll, jaw if ph["jaw_open"] else 0.0, neck_pitch_deg=neck)
        hr.set_camera(az, el, D_mm)
        head, eyem, ids, isg = hr.masks()
        return head, eyem

    def eye_term(eyem, k, tx, ty):
        ys_, xs_ = np.nonzero(eyem)
        if len(xs_) < 40: return 1.0
        e = ellipse_of(np.stack([xs_, ys_], 1).astype(float))
        # render px -> full-res photo px: x_p = k_full*x_r + tx_full
        kf = k * ds; c = kf * np.array(e["centre"]) + np.array([tx * ds, ty * ds])
        return (((c - ec) ** 2).sum() + (kf * e["major_px"] - e_maj) ** 2 + (kf * e["minor_px"] - e_min) ** 2) / L_p ** 2

    def eval_params(p, return_all=False):
        p = np.clip(p, lo_b, hi_b)          # Nelder-Mead has no bounds: clip, so az stays fixed on a profile shot
        el, az, pitch, yaw, roll, jaw, k, tx, ty = p
        mr, eyem = render((el, az, pitch, yaw, roll, jaw))
        tm = transform_mask(mr, k, tx, ty, (WS, HS))
        v = iou(small, tm)
        et = eye_term(eyem, k, tx, ty) if eye_ok else 0.0
        if return_all: return v, et, mr, eyem, tm
        return (1.0 - v) + w_eye * et

    yaw_sign = 1.0 if ph["cam_az"] >= 180 else -1.0
    lo_b = hi_b = None
    mr0, _ = render((ph["el0"], ph["cam_az"], 0.0, 40.0 * yaw_sign, 0.0, 20.0))
    ry, rx = np.nonzero(mr0)
    k0 = math.sqrt(area_p / max(1, mr0.sum()))
    tx0 = cx_p - k0 * rx.mean(); ty0 = cy_p - k0 * ry.mean()
    bounds = [(ph["el0"] - 12, ph["el0"] + 12),
              (ph["cam_az"] - 25, ph["cam_az"] + 25) if ph["az_free"] else (ph["cam_az"] - 0.01, ph["cam_az"] + 0.01),
              (-40, 40), (0, 90) if yaw_sign > 0 else (-90, 0), (-25, 25),
              (0, 40) if ph["jaw_open"] else (0, 0.01),
              (k0 * 0.7, k0 * 1.4), (tx0 - 120, tx0 + 120), (ty0 - 120, ty0 + 120)]
    lo_b = np.array([b[0] for b in bounds]); hi_b = np.array([b[1] for b in bounds])
    t0 = time.time()
    res = optimize.differential_evolution(eval_params, bounds, maxiter=10 if quick else 22, popsize=6 if quick else 10,
                                          tol=1e-5, seed=1, polish=False, updating="immediate")
    res2 = optimize.minimize(eval_params, res.x, method="Nelder-Mead",
                             options=dict(xatol=0.01, fatol=1e-6, maxfev=500 if quick else 1500))
    p = res2.x if res2.fun < res.fun else res.x
    # fit-uncertainty of k: re-polish from perturbed starts, take the spread
    ks = []
    rng = np.random.default_rng(0)
    for i in range(2 if quick else 5):
        p1 = p.copy(); p1[6] *= 1 + rng.normal(0, 0.03); p1[2] += rng.normal(0, 3); p1[3] += rng.normal(0, 3)
        r3 = optimize.minimize(eval_params, p1, method="Nelder-Mead", options=dict(xatol=0.01, fatol=1e-6, maxfev=250 if quick else 600))
        ks.append((float(r3.fun), float(r3.x[7]), r3.x))
    best = min([(float(res2.fun if res2.fun < res.fun else res.fun), float(p[6]), p)] + ks, key=lambda t: t[0])
    p = np.clip(best[2], lo_b, hi_b)
    k_spread = float(np.std([t[1] for t in ks] + [best[1]]))
    best_iou, et, mr, eyem, tm = eval_params(p, True)
    el, az, pitch, yaw, roll, jaw, k, tx, ty = [float(x) for x in p]
    pys, pxs = np.nonzero(crop); rys, rxs = np.nonzero(mr)
    fit = dict(objective=float(best[0]), iou=float(best_iou), eye_term=float(et), seconds=round(time.time() - t0, 1),
               n_eval=int(res.nfev + res2.nfev),
               cam_el_deg=el, cam_az_deg=az, cam_distance_mm=D_mm, cam_distance_source=ph.get("D_source", ""),
               head_pitch_deg=pitch, head_yaw_deg=yaw, head_roll_deg=roll, jaw_open_deg=jaw if ph["jaw_open"] else 0.0,
               k_photo_px_per_render_px=k * ds, k_fit_spread=k_spread * ds, tx=tx * ds + bx0, ty=ty * ds + by0,
               crop_box=[int(bx0), int(by0), int(bx1), int(by1)],
               photo_head_extent_px=[int(pxs.max() - pxs.min() + 1), int(pys.max() - pys.min() + 1)],
               photo_head_area_px=int(crop.sum()),
               render_head_extent_px=[int(rxs.max() - rxs.min() + 1), int(rys.max() - rys.min() + 1)],
               render_head_area_px=int(mr.sum()))
    # principal-axis extents of both head masks (photo full-res px; render px)
    fit["photo_head_pca"] = ellipse_of(np.stack([pxs, pys], 1).astype(float))
    fit["render_head_pca"] = ellipse_of(np.stack([rxs, rys], 1).astype(float))
    # render eye ellipse (px) at the fitted pose
    ys_, xs_ = np.nonzero(eyem)
    fit["render_eye"] = ellipse_of(np.stack([xs_, ys_], 1).astype(float)) if len(xs_) >= 40 else None
    fit["_masks"] = (pm_full, mr, tm, crop, small, eyem)
    return fit


# ----------------------------------------------------------------------------
def overlay_pictures(ph, rgb, fit, servo, eye, hr, mm_per_px, rservo):
    pm_full, mr, tm, crop, small, eyem = fit["_masks"]
    bx0, by0, bx1, by1 = fit["crop_box"]
    H, W = pm_full.shape
    real = Image.fromarray(rgb.astype(np.uint8))
    # 1) annotated measurement picture
    ann = real.copy(); d = ImageDraw.Draw(ann)
    d.polygon(ph["neck_poly"], outline=(200, 40, 30), width=4)
    d.line([(0, ph["head_ycut"]), (W, ph["head_ycut"])], fill=(200, 40, 30), width=3)
    for s in servo:
        if "lines" not in s: continue
        for (x, y, a, b) in s["lines"]:
            t = math.radians(s["tilt_deg"]); px, py = math.cos(t), -math.sin(t)
            d.line([(x - a * px, y - a * py), (x + b * px, y + b * py)], fill=(30, 120, 220), width=2)
        x, y = s["lines"][0][0], s["lines"][0][1]
        d.text((x + 90, y), "%.1f px = 20.000 mm (mode of %d lines)" % (s["width_px"], s["n_accepted"]), fill=(30, 120, 220))
    if "centre" in eye:
        cx, cy = eye["centre"]; a = eye["major_px"] / 2; b = eye["minor_px"] / 2
        ang = math.atan2(eye["major_axis_dir"][1], eye["major_axis_dir"][0])
        pts = [(cx + a * math.cos(t) * math.cos(ang) - b * math.sin(t) * math.sin(ang),
                cy + a * math.cos(t) * math.sin(ang) + b * math.sin(t) * math.cos(ang)) for t in np.linspace(0, 2 * math.pi, 90)]
        d.line(pts + [pts[0]], fill=(30, 160, 60), width=4)
        d.rectangle(eye["box"], outline=(30, 160, 60), width=2)
        d.text((cx - 70, cy + b + 10), "eye major %.1f px = %.2f mm" % (eye["major_px"], eye["major_px"] * mm_per_px), fill=(30, 160, 60))
    ys, xs = np.nonzero(pm_full)
    d.rectangle([xs.min(), ys.min(), xs.max(), ys.max()], outline=(120, 60, 200), width=3)
    ann.crop((max(0, bx0 - 200), max(0, by0 - 100), min(W, bx1 + 300), min(H, by1 + 400))).save(os.path.join(OUT, "%s_measure.png" % ph["id"]))
    # 2) real | ours | overlay at the crop
    realc = real.crop((bx0, by0, bx1, by1))
    cw, chh = realc.size
    shaded = Image.fromarray(hr.shaded())
    k = fit["k_photo_px_per_render_px"]; tx = fit["tx"] - bx0; ty = fit["ty"] - by0
    a = 1.0 / k
    ours_full = shaded.transform((cw, chh), Image.AFFINE, (a, 0, -tx * a, 0, a, -ty * a), resample=Image.BILINEAR, fillcolor=(255, 255, 255))
    headmask_full = Image.fromarray((mr * 255).astype(np.uint8)).transform((cw, chh), Image.AFFINE, (a, 0, -tx * a, 0, a, -ty * a), resample=Image.BILINEAR)
    white = Image.new("RGB", (cw, chh), (255, 255, 255))
    ours = Image.composite(ours_full, white, headmask_full)
    ov = realc.copy().convert("RGBA")
    hm = np.asarray(headmask_full) > 127
    edge = hm ^ np.roll(hm, 1, 0) | hm ^ np.roll(hm, 1, 1)
    pe = crop ^ np.roll(crop, 1, 0) | crop ^ np.roll(crop, 1, 1)
    edge = ndimage.binary_dilation(edge, iterations=2); pe = ndimage.binary_dilation(pe, iterations=2)
    arr = np.asarray(ov).copy()
    arr[pe] = (30, 90, 220, 255)
    arr[edge] = (230, 90, 20, 255)
    # render eye outline (orange, thin) on the overlay
    em = Image.fromarray((eyem * 255).astype(np.uint8)).transform((cw, chh), Image.AFFINE, (a, 0, -tx * a, 0, a, -ty * a), resample=Image.BILINEAR)
    emb = np.asarray(em) > 127
    ee = ndimage.binary_dilation(emb ^ np.roll(emb, 1, 0) | emb ^ np.roll(emb, 1, 1), iterations=1)
    arr[ee] = (230, 90, 20, 255)
    ov = Image.fromarray(arr).convert("RGB")
    tile_h = 700; sc = tile_h / chh; tw = int(cw * sc)
    sheet = Image.new("RGB", (tw * 3 + 40, tile_h + 60), (255, 255, 255))
    dd = ImageDraw.Draw(sheet)
    labs = ["REAL  " + ph["title"],
            "OURS  same camera (D %.0f mm, el %.1f, az %.1f) + fitted pose (pitch %.1f yaw %.1f roll %.1f jaw %.1f)" % (
                fit["cam_distance_mm"], fit["cam_el_deg"], fit["cam_az_deg"], fit["head_pitch_deg"], fit["head_yaw_deg"], fit["head_roll_deg"], fit["jaw_open_deg"]),
            "OVERLAY  blue = photo head region, orange = our head + eye ring   IoU %.3f" % fit["iou"]]
    for i, (im, lab) in enumerate(zip([realc, ours, ov], labs)):
        sheet.paste(im.resize((tw, tile_h), Image.LANCZOS), (10 + i * (tw + 10), 40))
        dd.text((12 + i * (tw + 10), 12), lab, fill=(0, 0, 0))
    sheet.save(os.path.join(OUT, "%s_pair.png" % ph["id"]))
    ours.save(os.path.join(OUT, "%s_ours.png" % ph["id"]))
    realc.save(os.path.join(OUT, "%s_real.png" % ph["id"]))
    ov.save(os.path.join(OUT, "%s_overlay.png" % ph["id"]))
    # 3) the render's servo measurement, drawn
    if rservo and "centre_px" in rservo:
        sh = Image.fromarray(hr.shaded()); dd = ImageDraw.Draw(sh)
        cx, cy = rservo["centre_px"]; w = rservo["width_px"]
        dd.rectangle([cx - w / 2, cy - 30, cx + w / 2, cy + 30], outline=(30, 120, 220), width=2)
        dd.text((cx + w / 2 + 6, cy - 10), "%.1f px (render) = 20.000 mm" % w, fill=(30, 120, 220))
        sh.save(os.path.join(OUT, "%s_render_servo.png" % ph["id"]))


# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--quick", action="store_true"); ap.add_argument("--only")
    ap.add_argument("--D", type=float, help="override the camera distance (mm) for every photo — sensitivity runs")
    ap.add_argument("--tag", default="", help="suffix for the output json (sensitivity runs)")
    args = ap.parse_args()
    if args.D:
        for ph in PHOTOS: ph["D_mm"] = args.D; ph["D_source"] = "override --D %.0f mm (sensitivity run)" % args.D
    model, data = load_model()
    hr = HeadRenderer(model, data, size=640)
    results = []
    for ph in PHOTOS:
        if args.only and ph["id"] != args.only: continue
        print("==", ph["id"]); sys.stdout.flush()
        rgb = load_rgb(os.path.join(REPO, ph["path"]))
        servo = [measure_servo(rgb, s) for s in ph["servo_scans"]]
        eye = measure_eye(rgb, ph["eye_box"], ph["eye_hue"], smin=ph.get("eye_smin", 0.35))
        fit = fit_photo(ph, hr, rgb, eye, quick=args.quick)
        # re-pose at the fitted parameters and measure the servo(s) in the render
        hr.pose(fit["head_pitch_deg"], fit["head_yaw_deg"], fit["head_roll_deg"], fit["jaw_open_deg"], neck_pitch_deg=ph.get("neck_pitch_deg", 0.0))
        hr.set_camera(fit["cam_az_deg"], fit["cam_el_deg"], fit["cam_distance_mm"])
        ids, types = hr.seg(); isg = types == int(mujoco.mjtObj.mjOBJ_GEOM)
        ratios = []
        for s in servo:
            if "width_px" not in s: continue
            rs = measure_servo_mask(hr.servo_mask(s["geom"], ids, isg), s["tilt_deg"])
            s["render"] = rs
            dz_servo, dz_head = hr.servo_depths_mm(s["geom"])
            # ANALYTIC render width of the same case: the frame is exactly 2*HALF_FRAME_MM at the lookat depth,
            # the case is 20.000 along world x and 26.000 along world y (neck vertical, no yaw), seen from azimuth az,
            # and sits dz_servo/dz_head as deep as the lookat. Exact given the MJCF placement; the mask read is the cross-check.
            az = math.radians(fit["cam_az_deg"])
            w_face = XL330_FACE_W_MM * abs(math.sin(az)) + 26.0 * abs(math.cos(az))
            w_an = w_face * (hr.size / (2.0 * HALF_FRAME_MM)) * (dz_head / dz_servo)
            s["render_width_px_analytic"] = w_an
            s["render_width_analytic_how"] = "(20.000*|sin az| + 26.000*|cos az|) mm * %d px / %.1f mm * D_head/D_servo (%.4f)" % (hr.size, 2 * HALF_FRAME_MM, dz_head / dz_servo)
            if "width_px" in rs:
                s["render_mask_vs_analytic_pct"] = (rs["width_px"] / w_an - 1) * 100
            rr = fit["k_photo_px_per_render_px"] * w_an / s["width_px"]
            rel = math.sqrt((s["width_px_unc"] / s["width_px"]) ** 2 + (fit["k_fit_spread"] / fit["k_photo_px_per_render_px"]) ** 2)
            s["size_ratio"] = dict(product_over_mesh=rr, unc=rr * rel, servo_depth_mm=dz_servo, head_depth_mm=dz_head,
                                   how="k * W_render_analytic / W_photo; unc = photo width + fit spread of k (the analytic width is exact)")
            ratios.append((rr, rr * rel))
        r = dict(id=ph["id"], title=ph["title"], path=ph["path"], colourway=ph["colourway"], note=ph["note"],
                 image_size_px=[int(rgb.shape[1]), int(rgb.shape[0])],
                 scale=dict(feature="XL330-M288-T case, 20.000 mm across the horn/label face", source=XL330_SRC, servos=servo),
                 eye=eye, fit={k: v for k, v in fit.items() if not k.startswith("_")},
                 inputs=dict(head_ycut=ph["head_ycut"], neck_poly=ph["neck_poly"], eye_box=ph["eye_box"], eye_hue=ph["eye_hue"],
                             servo_scans=ph["servo_scans"], cam_az=ph["cam_az"], az_free=ph["az_free"]))
        good = [s for s in servo if "mm_per_px" in s]
        if good:
            mmpp = float(np.mean([s["mm_per_px"] for s in good]))
            spread = 0.5 * (max(s["mm_per_px"] for s in good) - min(s["mm_per_px"] for s in good)) if len(good) > 1 else 0.0
            mmpp_unc = math.sqrt(max(s["mm_per_px_unc"] for s in good) ** 2 + spread ** 2)
            r["scale"]["mm_per_px"] = mmpp; r["scale"]["mm_per_px_unc"] = mmpp_unc
        else:
            mmpp, mmpp_unc = None, None
        if ratios:
            wts = np.array([1 / u ** 2 for _, u in ratios]); vals = np.array([v for v, _ in ratios])
            rr = float((wts * vals).sum() / wts.sum()); ru = float(1 / math.sqrt(wts.sum()))
            k = fit["k_photo_px_per_render_px"]
            # per-axis: photo extents along the photo head's principal axes vs the render's, at the servo-anchored scale
            k_servo = k / rr     # photo px per render px if the product were exactly the mesh
            pp, rp = fit["photo_head_pca"], fit["render_head_pca"]
            dev_major = (pp["major_px"] - k_servo * rp["major_px"]) * mmpp
            dev_minor = (pp["minor_px"] - k_servo * rp["minor_px"]) * mmpp
            unc_axis = lambda e: math.sqrt((e * mmpp * ru / rr) ** 2 + (2 * 2.0 * mmpp) ** 2 + (e * mmpp_unc) ** 2)
            r["size"] = dict(product_over_mesh=rr, unc=ru, n_servos=len(ratios),
                             head_length_dev_mm=HEAD_LEN_MM * (rr - 1), head_length_dev_unc_mm=HEAD_LEN_MM * ru,
                             photo_head_extent_major_mm=pp["major_px"] * mmpp, photo_head_extent_minor_mm=pp["minor_px"] * mmpp,
                             mesh_head_extent_major_mm=k_servo * rp["major_px"] * mmpp, mesh_head_extent_minor_mm=k_servo * rp["minor_px"] * mmpp,
                             dev_major_mm=dev_major, dev_major_unc_mm=unc_axis(pp["major_px"]),
                             dev_minor_mm=dev_minor, dev_minor_unc_mm=unc_axis(pp["minor_px"]),
                             how="major/minor = principal axes of the photo head region (silhouette PCA, 0.5/99.5 percentile extents); "
                                 "mesh extents = the render head mask at the fitted pose scaled by k/r (the servo-anchored scale); "
                                 "unc = scale + 2 px edge on each mask + mm/px")
            if "major_px" in eye:
                r["eye"]["diameter_mm"] = eye["major_px"] * mmpp
                r["eye"]["diameter_unc_mm"] = math.sqrt((eye["major_px"] * mmpp_unc) ** 2 + (eye["unc_px"] * mmpp) ** 2)
                r["eye"]["mesh_diameter_mm"] = EYE_RING_D_MM
                r["eye"]["dev_mm"] = r["eye"]["diameter_mm"] - EYE_RING_D_MM
                if fit.get("render_eye"):
                    re_ = fit["render_eye"]
                    r["eye"]["render_major_px"] = re_["major_px"]; r["eye"]["render_minor_px"] = re_["minor_px"]
                    # ring diameter through the SAME servo anchor (independent of mm/px at the eye's depth):
                    r["eye"]["diameter_via_render_mm"] = EYE_RING_D_MM * eye["major_px"] / (k_servo * re_["major_px"])
                    c_r = k * np.array(re_["centre"]) + np.array([fit["tx"], fit["ty"]])
                    r["eye"]["centre_offset_photo_minus_render_mm"] = [float((eye["centre"][0] - c_r[0]) * mmpp), float((eye["centre"][1] - c_r[1]) * mmpp)]
        overlay_pictures(ph, rgb, fit, servo, eye, hr, mmpp or 0.0, next((s.get("render") for s in servo if s.get("render")), None))
        results.append(r)
        print(json.dumps({k: v for k, v in r.items() if k in ("scale", "size", "eye")}, indent=1, default=float)[:4000])
        print("fit:", json.dumps(r["fit"], default=float)); sys.stdout.flush()
    out = dict(generated=time.strftime("%Y-%m-%d %H:%M"), method=__doc__, quick=args.quick,
               mesh=dict(top_head_shell_mm=HEAD_MESH_MM["top_head_shell"], bottom_head_shell_mm=HEAD_MESH_MM["bottom_head_shell"],
                         noenoeil_mm=HEAD_MESH_MM["noenoeil"], jaw_mm=HEAD_MESH_MM["jaw"], source="out/verify/mech_dims.json",
                         eye_ring_source=EYE_SRC),
               servo_source=XL330_SRC, photos=results)
    path = os.path.join(OUT, ("head_fit%s.json" % args.tag) if not args.only else "head_fit_%s%s.json" % (args.only, args.tag))
    json.dump(out, open(path, "w"), indent=1, default=float)
    print("wrote", path)


if __name__ == "__main__":
    main()
