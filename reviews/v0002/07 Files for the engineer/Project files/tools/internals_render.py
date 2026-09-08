#!/usr/bin/env python3
"""internals_render.py — the INTERNALS DIAGRAM of our own CAD, measured off the
MuJoCo model (sim/microduck_ours.xml wrapped by sim/compare_render.studio_scene).

Leif, 2026-09-03: "an new image covering the components of the microduck
internals". No public photograph of a full internal layout exists (see
out/sources/internals.json search_log), so this tool draws ours: see-through,
shells-off and exploded views of the TRUNK and the HEAD, every internal
component labelled with its triad ref, its measured world position and its
function, plus a see-through whole-robot view carrying the cable routes from
wiring/cables.json.

Everything drawn on a picture is MEASURED here, not typed:
  * component positions are d.geom_xpos / d.site_xpos of the compiled model at
    the INIT (zero) keyframe — the same frame as SPEC.md §3 (trunk_base at
    (0, 0, 120) mm, +x beak, +y left, +z up);
  * label anchors are those points projected through the very camera that
    rendered the frame (the renderer's own mjvGLCamera frustum), so a leader
    ends on the geom it names;
  * cable polylines are cables.json from_xyz_mm -> joint anchor(s) -> to_xyz_mm,
    the same rule wiring/measure.py used for the floor length.

Run: ce-cad/bin/cad tools/internals_render.py  (stdout is buffered; read
out/sources/internals/render.log). Writes out/sources/internals/*.png and
merges `renders`, `components`, `sites`, `not_in_cad` into
out/sources/internals.json (search_log etc. are preserved).
"""
import os, sys, json, math, time
os.environ.setdefault("MUJOCO_GL", "glfw")
import numpy as np
import mujoco
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "sim"))
import common            # noqa: E402
import compare_render    # noqa: E402

OUT = os.path.join(ROOT, "out", "sources", "internals")
os.makedirs(OUT, exist_ok=True)
DATA = os.path.join(ROOT, "out", "sources", "internals.json")
CABLES = os.path.join(ROOT, "wiring", "cables.json")
M2P = json.load(open(os.path.join(ROOT, "spec", "mesh-to-part.json")))["map"]
W = H = 1400

# --- what each internal thing IS (label, function). Ref comes from spec/mesh-to-part.json.
# key = (body, mesh). Sub-index picks the n-th geom of that mesh in that body (servo pairs).
COMPONENTS = {
    # trunk
    ("trunk_base", "xl330", 0):  ("hip-yaw servo R (ID 10)", "drives right_hip_yaw about -z"),
    ("trunk_base", "xl330", 1):  ("hip-yaw servo L (ID 20)", "drives left_hip_yaw about -z"),
    ("trunk_base", "np_f970", 0): ("battery NP-F550 (mesh named np_f970)", "2S Li-ion 2600 mAh, removable, 6.6-8.2 V"),
    ("trunk_base", "power_support__ours", 0): ("power_support (battery cradle)", "holds the pack; carries the contact board"),
    ("trunk_base", "banana_pcb_locker__ours", 0): ("banana_pcb_locker", "retaining bar for the battery-contact PCB"),
    ("trunk_base", "trunk_base__ours", 0): ("trunk_base plate", "chassis plate both hip-yaw servos hang from; neck servo bolts on top"),
    ("trunk_base", "left_shell", 0): ("trunk shell L", "colourway half-shell"),
    ("trunk_base", "right_shell", 0): ("trunk shell R", "colourway half-shell"),
    ("trunk_base", "seeed_bearing__configuration__22x16x4", 0): ("bearing 22x16x4 (hip-yaw idler L)", "idler opposite the yaw horn"),
    ("trunk_base", "seeed_bearing__configuration__22x16x4", 1): ("bearing 22x16x4 (hip-yaw idler R)", "idler opposite the yaw horn"),
    # neck
    ("neck", "xl330", 0): ("neck-pitch servo (ID 30)", "neck_pitch about -y, at the trunk"),
    ("neck", "xl330", 1): ("head-pitch servo (ID 31)", "head_pitch about +y, top of the neck"),
    ("neck", "neck", 0): ("neck plate (one of two)", "2 mm plate spanning the 50 mm neck"),
    ("neck_pitch", "neck_pitch", 0): ("neck_pitch bracket", "head-pitch output bracket"),
    ("yaw_roll_motion", "xl330", 0): ("head-yaw servo (ID 32)", "head_yaw about +z"),
    ("yaw_roll_motion", "yaw_roll_motion", 0): ("yaw_roll_motion", "head-yaw output carrying the roll servo"),
    # head
    ("jaw_soft", "xl330", 0): ("mouth servo (ID 34)", "opens the lower beak -5..+30 deg"),
    ("jaw_soft", "xl330", 1): ("head-roll servo (ID 33)", "head_roll about -x"),
    ("jaw_soft", "pcb__raspberry_pi_zero_2_w", 0): ("compute (Radxa Zero 3W; mesh is a Pi Zero 2 W proxy)", "RK3566 host, 65 x 30 mm, camera CSI, /dev/ttyS2 servo UART"),
    ("jaw_soft", "elec_rpi_robot_hat_pcb", 0): ("RPI Robot HAT", "audio codec, ToF I2C, half-duplex DXL transceiver, battery power in"),
    ("jaw_soft", "lens", 0): ("M12 lens", "wide-angle lens over the IMX219"),
    ("jaw_soft", "m12_lens_holder", 0): ("M12 lens holder", "seats the lens; the IMX219 board sits behind it"),
    ("jaw_soft", "noenoeil", 0): ("eye ring (noenoeil)", "accent-colour bezel around the lens"),
    ("jaw_soft", "face_part", 0): ("face_part", "front plate: lens aperture + ToF window"),
    ("jaw_soft", "speaker", 0): ("speaker (35 x 25 x 7 placeholder)", "voice out; placeholder box in the source"),
    ("jaw_soft", "motor_support", 0): ("motor_support", "plate carrying the roll + mouth servos and the boards"),
    ("jaw_soft", "top_head_shell", 0): ("top head shell", "colourway dome"),
    ("jaw_soft", "bottom_head_shell", 0): ("bottom head shell", "accent underside, carries the upper beak"),
    ("jaw_soft", "jaw", 0): ("jaw (lower beak)", "mouth DoF, hinged at the rear sides"),
    ("jaw_soft", "seeed_bearing__configuration_default", 0): ("bearing 15x10x3 (jaw idler)", "jaw hinge opposite the mouth servo"),
}
SITES = {   # MJCF sites = things the source places without a mesh
    "imu":        ("trunk IMU LSM6DSV16X on imu_to_dxl (DXL ID 200)", "part:microduck-imu-to-dxl", "control IMU; the DXL bus branch point"),
    "head_camera": ("camera IMX219 (site)", "part:microduck-camera-module", "front camera, mounted upside down"),
    "tof":        ("ToF VL53L5CX/L8CX 8x8 (site)", "part:microduck-tof-module", "depth matrix behind the pill window"),
    "head_imu":   ("head IMU (site; BMI088 on the HAT, dormant)", "part:bmi088", "second IMU, in the head"),
    "mouth_tip":  ("mouth tip (site)", None, "beak tip reference"),
}
NOT_IN_CAD = [
    ("microphone(s)", "part:microduck-mic", "Pollen: 'mic + speaker'; no mesh, no site — CANNOT DETERMINE placement"),
    ("NFC antenna, head", "part:st25r3916", "Pollen: two NFC antennas (head + beak); no mesh — CANNOT DETERMINE"),
    ("NFC antenna, beak", "part:st25r3916", "as above"),
    ("battery contact board (banana)", None, "the locker implies a PCB; no mesh — CANNOT DETERMINE outline"),
    ("imu_to_dxl board outline", "part:microduck-imu-to-dxl", "only the IMU site exists; board size/connector count CANNOT DETERMINE"),
    ("power switch / USB-C / status LED", None, "trunk top rear holes seen in photos (CATALOG.md); nothing in the MJCF"),
    ("every fastener, insert, cable", None, "GOAL.md standing order 1: bom.json 38 rows, zero fasteners"),
]
SHELL_MESHES = {"left_shell", "right_shell", "top_head_shell", "bottom_head_shell", "face_part", "jaw", "jaw_soft", "soft_mouth_top", "noenoeil"}

def font(sz):
    for p in ("/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/Supplemental/Arial.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

def quat_to_mat(q):
    w, x, y, z = q
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                     [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                     [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])

class Studio:
    def __init__(self):
        scene = compare_render.studio_scene(common.robot_file("ours"))
        self.m = mujoco.MjModel.from_xml_string(scene, {})
        self.d = mujoco.MjData(self.m)
        kid = mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_KEY, "INIT")
        mujoco.mj_resetDataKeyframe(self.m, self.d, kid)
        mujoco.mj_forward(self.m, self.d)
        # make every geom's colour explicit so alpha edits take effect uniformly
        for g in range(self.m.ngeom):
            mid = self.m.geom_matid[g]
            if mid >= 0:
                self.m.geom_rgba[g] = self.m.mat_rgba[mid]
        self.base_rgba = self.m.geom_rgba.copy()
        self.base_pos = self.m.geom_pos.copy()
        self.r = mujoco.Renderer(self.m, H, W)
        self.cam = mujoco.MjvCamera(); self.cam.type = mujoco.mjtCamera.mjCAMERA_FREE
        self.opt = mujoco.MjvOption()
        self.index()

    def index(self):
        """(body, mesh, n) -> geom id, in XML order; collision-class copies skipped."""
        self.geoms = {}
        count = {}
        for g in range(self.m.ngeom):
            if self.m.geom_type[g] != mujoco.mjtGeom.mjGEOM_MESH or self.m.geom_group[g] == 3:
                continue
            body = mujoco.mj_id2name(self.m, mujoco.mjtObj.mjOBJ_BODY, self.m.geom_bodyid[g])
            mesh = mujoco.mj_id2name(self.m, mujoco.mjtObj.mjOBJ_MESH, self.m.geom_dataid[g])
            n = count.get((body, mesh), 0); count[(body, mesh)] = n + 1
            self.geoms[(body, mesh, n)] = g

    def reset(self):
        self.m.geom_rgba[:] = self.base_rgba
        self.m.geom_pos[:] = self.base_pos
        mujoco.mj_forward(self.m, self.d)

    def set_alpha(self, pred, a):
        for (body, mesh, n), g in self.geoms.items():
            if pred(body, mesh):
                self.m.geom_rgba[g, 3] = a
        # collision copies are group 3: never drawn (opt.geomgroup) — leave them

    def explode(self, moves):
        """moves: {(body, mesh, n): world offset mm}. geom_pos is in the body frame."""
        for key, dmm in moves.items():
            g = self.geoms[key]
            bid = self.m.geom_bodyid[g]
            R = self.d.xmat[bid].reshape(3, 3)
            self.m.geom_pos[g] = self.base_pos[g] + R.T @ (np.asarray(dmm, float) / 1000.0)
        mujoco.mj_forward(self.m, self.d)

    def shoot(self, lookat_mm, az, el, dist):
        self.cam.lookat[:] = np.asarray(lookat_mm, float) / 1000.0
        self.cam.azimuth = float(az); self.cam.elevation = float(el); self.cam.distance = float(dist)
        self.opt.geomgroup[:] = 0; self.opt.geomgroup[2] = 1; self.opt.geomgroup[0] = 1; self.opt.geomgroup[1] = 1
        self.r.update_scene(self.d, self.cam, self.opt)
        px = self.r.render().copy()
        # the renderer's own camera (two eyes for stereo; average them)
        cams = self.r.scene.camera
        pos = (np.array(cams[0].pos) + np.array(cams[1].pos)) / 2
        fwd = np.array(cams[0].forward); up = np.array(cams[0].up)
        fwd /= np.linalg.norm(fwd); up /= np.linalg.norm(up)
        right = np.cross(fwd, up)
        c0 = cams[0]
        near = c0.frustum_near
        half_h = (c0.frustum_top - c0.frustum_bottom) / 2
        aspect = W / H
        half_w = half_h * aspect
        self.proj = dict(pos=pos, fwd=fwd, up=up, right=right, near=near, half_w=half_w, half_h=half_h)
        return Image.fromarray(px)

    def project(self, p_mm):
        P = self.proj
        c = np.asarray(p_mm, float) / 1000.0 - P["pos"]
        z = float(c @ P["fwd"]); x = float(c @ P["right"]); y = float(c @ P["up"])
        if z <= 1e-6:
            return None
        u = W / 2 + (x / z) * P["near"] / P["half_w"] * (W / 2)
        v = H / 2 - (y / z) * P["near"] / P["half_h"] * (H / 2)
        return (u, v)

    def gpos(self, key):
        return (self.d.geom_xpos[self.geoms[key]] * 1000.0).tolist()

    def gaabb(self, key):
        """world axis-aligned bounding box of a mesh geom, mm, off the mesh vertices themselves"""
        g = self.geoms[key]; mid = self.m.geom_dataid[g]
        a = self.m.mesh_vertadr[mid]; n = self.m.mesh_vertnum[mid]
        v = self.m.mesh_vert[a:a + n]
        R = self.d.geom_xmat[g].reshape(3, 3); t = self.d.geom_xpos[g]
        w = (v @ R.T + t) * 1000.0
        return w.min(axis=0).tolist(), w.max(axis=0).tolist()

    def spos(self, name):
        sid = mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_SITE, name)
        return (self.d.site_xpos[sid] * 1000.0).tolist()

    def jpos(self, name):
        jid = mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_JOINT, name)
        return (self.d.xanchor[jid] * 1000.0).tolist()

# ---------------------------------------------------------------- drawing
INK = (28, 30, 34); ACC = (178, 74, 30); LEAD = (60, 60, 60); SITE = (30, 100, 170)
def draw_labels(im, items, title, subtitle):
    """items: list of dict(n, text, uv, kind). Labels are laid in two columns
    left/right of the frame, sorted by their anchor's v, leaders drawn to the
    anchor with a small ring at the anchor."""
    dr = ImageDraw.Draw(im, "RGBA")
    f = font(20); fs = font(15); ft = font(30)
    dr.rectangle([0, 0, W, 64], fill=(255, 255, 255, 235))
    dr.text((22, 12), title, fill=INK, font=ft)
    dr.text((22, 44), subtitle, fill=(90, 90, 90), font=fs)
    left = sorted([it for it in items if it["uv"] and it["uv"][0] < W / 2], key=lambda t: t["uv"][1])
    right = sorted([it for it in items if it["uv"] and it["uv"][0] >= W / 2], key=lambda t: t["uv"][1])
    def column(col, x_text, anchor_right):
        n = len(col)
        if not n: return
        top, bottom = 90, H - 40
        step = min(46, (bottom - top) / max(n, 1))
        ys = [top + i * step for i in range(n)]
        # pull each label toward its anchor's v while keeping order and spacing
        for _ in range(60):
            for i, it in enumerate(col):
                target = it["uv"][1]
                lo = top if i == 0 else ys[i-1] + step
                hi = bottom if i == n-1 else ys[i+1] - step
                ys[i] = min(max(target, lo), hi)
        # leaders first (under every box), then the boxes, so no leader strikes through a label
        boxes = []
        for it, y in zip(col, ys):
            u, v = it["uv"]
            col_ink = SITE if it["kind"] == "site" else INK
            txt = "%d  %s" % (it["n"], it["text"])
            tw = dr.textlength(txt, font=f)
            if anchor_right:
                x0 = x_text - tw - 10
                dr.line([(x0 - 4, y), (u, v)], fill=LEAD, width=2)
                boxes.append((x0 - 4, y - 14, x_text + 4, y + 14, x0, txt, col_ink))
            else:
                dr.line([(x_text + tw + 8, y), (u, v)], fill=LEAD, width=2)
                boxes.append((x_text - 4, y - 14, x_text + tw + 8, y + 14, x_text, txt, col_ink))
            dr.ellipse([u - 6, v - 6, u + 6, v + 6], outline=col_ink, width=2, fill=(255, 255, 255, 160))
        for (a, b, c, e, xt, txt, col_ink) in boxes:
            dr.rectangle([a, b, c, e], fill=(255, 255, 255, 225), outline=(200, 200, 200, 255))
            dr.text((xt, b + 3), txt, fill=col_ink, font=f)
    column(left, 30, False)
    column(right, W - 30, True)
    return im

def draw_polyline(im, pts_uv, colour, width=4):
    dr = ImageDraw.Draw(im, "RGBA")
    pts = [p for p in pts_uv if p]
    if len(pts) >= 2:
        dr.line(pts, fill=colour, width=width, joint="curve")
        for p in pts:
            dr.ellipse([p[0]-4, p[1]-4, p[0]+4, p[1]+4], fill=colour)

def draw_axes(im, st, origin_mm, L=25):
    """a measured frame gnomon: +x beak, +y left, +z up, projected through the same camera"""
    dr = ImageDraw.Draw(im, "RGBA")
    o = st.project(origin_mm)
    if not o: return
    for ax, col, name in (((L, 0, 0), (200, 40, 40), "+x"), ((0, L, 0), (40, 160, 60), "+y"), ((0, 0, L), (40, 80, 220), "+z")):
        e = st.project(np.asarray(origin_mm) + np.asarray(ax))
        if e:
            dr.line([o, e], fill=col, width=3); dr.text((e[0]+4, e[1]-8), name, fill=col, font=font(16))

# ---------------------------------------------------------------- views
def label_items(st, keys, sites=()):
    items = []; n = 0; comp_rows = []
    for key in keys:
        if key not in st.geoms:
            continue
        n += 1
        label, func = COMPONENTS.get(key, (key[1], ""))
        p = st.gpos(key)
        ref = M2P.get(key[1].replace("__ours", ""), None)
        items.append(dict(n=n, text=label, uv=st.project(p), kind="geom"))
        lo, hi = st.gaabb(key)
        comp_rows.append(dict(n=n, body=key[0], mesh=key[1], instance=key[2], ref=ref, label=label, function=func,
                              pos_world_mm=[round(v, 3) for v in p], aabb_min_mm=[round(v, 3) for v in lo],
                              aabb_max_mm=[round(v, 3) for v in hi], size_mm=[round(b - a, 3) for a, b in zip(lo, hi)]))
    for s in sites:
        n += 1
        label, ref, func = SITES[s]
        p = st.spos(s)
        items.append(dict(n=n, text=label, uv=st.project(p), kind="site"))
        comp_rows.append(dict(n=n, body=None, mesh=None, instance=None, site=s, ref=ref, label=label, function=func,
                              pos_world_mm=[round(v, 3) for v in p]))
    return items, comp_rows

TRUNK_KEYS = [("trunk_base", "xl330", 0), ("trunk_base", "xl330", 1), ("trunk_base", "np_f970", 0),
              ("trunk_base", "power_support__ours", 0), ("trunk_base", "banana_pcb_locker__ours", 0),
              ("trunk_base", "trunk_base__ours", 0), ("trunk_base", "left_shell", 0), ("trunk_base", "right_shell", 0),
              ("trunk_base", "seeed_bearing__configuration__22x16x4", 0), ("trunk_base", "seeed_bearing__configuration__22x16x4", 1),
              ("neck", "xl330", 0)]
HEAD_KEYS = [("jaw_soft", "pcb__raspberry_pi_zero_2_w", 0), ("jaw_soft", "elec_rpi_robot_hat_pcb", 0),
             ("jaw_soft", "lens", 0), ("jaw_soft", "m12_lens_holder", 0), ("jaw_soft", "noenoeil", 0),
             ("jaw_soft", "face_part", 0), ("jaw_soft", "speaker", 0), ("jaw_soft", "motor_support", 0),
             ("jaw_soft", "xl330", 0), ("jaw_soft", "xl330", 1), ("yaw_roll_motion", "xl330", 0),
             ("yaw_roll_motion", "yaw_roll_motion", 0), ("jaw_soft", "top_head_shell", 0),
             ("jaw_soft", "bottom_head_shell", 0), ("jaw_soft", "jaw", 0),
             ("jaw_soft", "seeed_bearing__configuration_default", 0), ("neck", "xl330", 1), ("neck_pitch", "neck_pitch", 0)]
HEAD_SITES = ("head_camera", "tof", "head_imu")
TRUNK_SITES = ("imu",)

def is_trunk_shell(b, m): return b == "trunk_base" and m in ("left_shell", "right_shell")
def is_head_shell(b, m): return b == "jaw_soft" and m in ("top_head_shell", "bottom_head_shell", "face_part", "jaw", "jaw_soft", "soft_mouth_top", "noenoeil")
def is_structure(b, m): return not (m.startswith("xl330") or "pcb" in m or m in ("np_f970", "speaker", "lens", "m12_lens_holder"))

def main():
    t0 = time.time()
    st = Studio()
    log = open(os.path.join(OUT, "render.log"), "w")
    def say(*a):
        s = " ".join(str(x) for x in a); print(s); log.write(s + "\n"); log.flush()
    say("model: ngeom %d, nbody %d, INIT pose; frame +x beak +y left +z up; trunk_base at %s mm" %
        (st.m.ngeom, st.m.nbody, np.round(st.d.xpos[mujoco.mj_name2id(st.m, mujoco.mjtObj.mjOBJ_BODY, 'trunk_base')]*1000, 3).tolist()))
    renders = []; components = {}
    trunk_c = [-8, 0, 122]; head_c = [40, 0, 240]
    views = [
        # name, region, keys, sites, prepare(st), lookat, az, el, dist, title, real pair
        ("trunk-seethrough-iso", "trunk", TRUNK_KEYS, TRUNK_SITES, lambda: st.set_alpha(is_trunk_shell, 0.16),
         trunk_c, 225, -14, 0.26, "Trunk, see-through — shells at 16 % opacity", None),
        ("trunk-shells-off-iso", "trunk", TRUNK_KEYS[:6] + TRUNK_KEYS[8:], TRUNK_SITES, lambda: st.set_alpha(is_trunk_shell, 0.0),
         trunk_c, 225, -14, 0.26, "Trunk, shells removed", "real_desk_trunk_shells_off.png"),
        ("trunk-shells-off-rear", "trunk", TRUNK_KEYS[:6] + TRUNK_KEYS[8:], TRUNK_SITES, lambda: st.set_alpha(is_trunk_shell, 0.0),
         trunk_c, 30, -10, 0.26, "Trunk, shells removed — from the rear (battery side)", None),
        ("trunk-exploded", "trunk", TRUNK_KEYS, TRUNK_SITES,
         lambda: st.explode({("trunk_base", "left_shell", 0): (0, 55, 0), ("trunk_base", "right_shell", 0): (0, -55, 0),
                             ("trunk_base", "np_f970", 0): (-55, 0, 0), ("trunk_base", "power_support__ours", 0): (-25, 0, 0),
                             ("trunk_base", "banana_pcb_locker__ours", 0): (-25, 0, -18)}),
         trunk_c, 225, -14, 0.34, "Trunk, exploded — shells ±55 mm y, battery −55 mm x, cradle −25 mm x", None),
        ("head-seethrough-iso", "head", HEAD_KEYS, HEAD_SITES, lambda: st.set_alpha(is_head_shell, 0.14),
         head_c, 210, -12, 0.30, "Head, see-through — shells, face, beak at 14 % opacity", None),
        ("head-shells-off-iso", "head", [k for k in HEAD_KEYS if not is_head_shell(k[0], k[1])], HEAD_SITES, lambda: st.set_alpha(is_head_shell, 0.0),
         head_c, 210, -12, 0.30, "Head, shells removed", "real_desk_head_jaw_off.png"),
        ("head-shells-off-rear-low", "head", [k for k in HEAD_KEYS if not is_head_shell(k[0], k[1])], HEAD_SITES, lambda: st.set_alpha(is_head_shell, 0.0),
         head_c, 20, -25, 0.28, "Head, shells removed — from behind and below (the press_morning view)", "real_morning_head_rear_open.png"),
        ("head-seethrough-profile", "head", HEAD_KEYS, HEAD_SITES, lambda: st.set_alpha(is_head_shell, 0.14),
         head_c, 270, 0, 0.30, "Head, see-through — true left profile", None),
        ("head-exploded", "head", HEAD_KEYS, HEAD_SITES,
         lambda: st.explode({("jaw_soft", "top_head_shell", 0): (0, 0, 55), ("jaw_soft", "bottom_head_shell", 0): (0, 0, -40),
                             ("jaw_soft", "jaw", 0): (0, 0, -70), ("jaw_soft", "jaw_soft", 0): (0, 0, -70), ("jaw_soft", "soft_mouth_top", 0): (0, 0, -40),
                             ("jaw_soft", "face_part", 0): (45, 0, 0), ("jaw_soft", "noenoeil", 0): (70, 0, 0), ("jaw_soft", "lens", 0): (95, 0, 0),
                             ("jaw_soft", "m12_lens_holder", 0): (25, 0, 0), ("jaw_soft", "speaker", 0): (-40, 0, 0),
                             ("jaw_soft", "elec_rpi_robot_hat_pcb", 0): (0, -45, 15), ("jaw_soft", "pcb__raspberry_pi_zero_2_w", 0): (0, -45, -10)}),
         head_c, 210, -12, 0.40, "Head, exploded — dome +55 z, bottom −40 z, beak −70 z, face/eye/lens +45/+70/+95 x, boards −45 y", None),
    ]
    for name, region, keys, sites, prep, look, az, el, dist, title, real in views:
        st.reset(); prep()
        im = st.shoot(look, az, el, dist)
        items, rows = label_items(st, keys, sites)
        sub = "our CAD, INIT pose, camera az %g° el %g° dist %.2f m, lookat (%g, %g, %g) mm — %d labelled" % (az, el, dist, look[0], look[1], look[2], len(items))
        draw_labels(im, items, title, sub)
        draw_axes(im, st, look)
        fn = name + ".png"; im.save(os.path.join(OUT, fn))
        off = [it for it in items if it["uv"] is None or not (0 <= it["uv"][0] < W and 0 <= it["uv"][1] < H)]
        say("wrote %s  labels %d  off-frame %d" % (fn, len(items), len(off)))
        renders.append(dict(file="out/sources/internals/" + fn, region=region, title=title, camera=dict(az=az, el=el, dist_m=dist, lookat_mm=look),
                            labels=[dict(n=it["n"], text=it["text"], px=[round(it["uv"][0], 1), round(it["uv"][1], 1)] if it["uv"] else None) for it in items],
                            off_frame=len(off), real_photo=("out/sources/internals/" + real) if real else None))
        components.setdefault(region, rows)
    # ---- whole robot see-through with cable routes (zero pose = cables.json frame)
    st.reset(); st.set_alpha(is_structure, 0.10)
    im = st.shoot([10, 0, 150], 235, -10, 0.50)
    cab = json.load(open(CABLES))["record"]
    palette = [(200, 90, 20, 230), (30, 110, 200, 230), (120, 40, 160, 230), (20, 140, 90, 230), (90, 90, 90, 230)]
    groups = {g: palette[i % len(palette)] for i, g in enumerate(sorted(set(c["group"] for c in cab["cables"])))}
    cable_rows = []
    undetermined = []
    for c in cab["cables"]:
        if "from_xyz_mm" not in c or "to_xyz_mm" not in c:
            undetermined.append(dict(id=c["id"], why=c.get("why") or c.get("note") or "no endpoint coordinates in cables.json (length_undetermined)"))
            continue
        pts = [c["from_xyz_mm"]] + [st.jpos(j) for j in c["crosses"]] + [c["to_xyz_mm"]]
        col = groups.get(c["group"], (90, 90, 90, 230))
        draw_polyline(im, [st.project(p) for p in pts], col)
        cable_rows.append(dict(id=c["id"], group=c["group"], points_mm=[[round(v, 3) for v in p] for p in pts], cable_mm=c["cable_mm"], floor_mm=c["floor_mm"]))
    dr = ImageDraw.Draw(im, "RGBA")
    f = font(20); ft = font(30); fs = font(15)
    dr.rectangle([0, 0, W, 64], fill=(255, 255, 255, 235))
    dr.text((22, 12), "Cable routes — whole robot, structure at 10 % opacity", fill=INK, font=ft)
    dr.text((22, 44), "%d cables from wiring/cables.json (from-point → joint anchor(s) → to-point, the floor-length rule), zero pose, total %s mm" % (
        cab["cable_count"], cab["total_length_mm"]), fill=(90, 90, 90), font=fs)
    y = 90
    for gname, col in groups.items():
        dr.line([(30, y), (80, y)], fill=col, width=5); dr.text((90, y - 12), gname, fill=INK, font=f); y += 30
    fn = "cables-seethrough.png"; im.save(os.path.join(OUT, fn)); say("wrote", fn, "cables drawn", len(cable_rows), "undetermined", len(undetermined))
    renders.append(dict(file="out/sources/internals/" + fn, region="cables", title="Cable routes, see-through", camera=dict(az=235, el=-10, dist_m=0.50, lookat_mm=[10, 0, 150]),
                        labels=[], off_frame=0, real_photo=None, cables=cable_rows, cables_undetermined=undetermined))
    # ---- joint anchors in this pose, for the record
    joints = {}
    for j in range(st.m.njnt):
        nm = mujoco.mj_id2name(st.m, mujoco.mjtObj.mjOBJ_JOINT, j)
        if st.m.jnt_type[j] == mujoco.mjtJoint.mjJNT_HINGE:
            joints[nm] = [round(v, 3) for v in (st.d.xanchor[j] * 1000).tolist()]
    # ---- checks: things the layout must satisfy, measured off the same model
    def aabb(key): return st.gaabb(key)
    def inside(p, lo, hi): return all(lo[i] <= p[i] <= hi[i] for i in range(3))
    def overlap(a, b):
        lo = [max(a[0][i], b[0][i]) for i in range(3)]; hi = [min(a[1][i], b[1][i]) for i in range(3)]
        d = [hi[i] - lo[i] for i in range(3)]
        return d if all(x > 0 for x in d) else None
    checks = []
    bat = aabb(("trunk_base", "np_f970", 0)); imu = st.spos("imu")
    checks.append(dict(name="trunk IMU site outside the battery envelope", verdict="FAIL" if inside(imu, *bat) else "PASS",
                       measured=dict(imu_site_mm=[round(v, 3) for v in imu], battery_aabb_mm=[[round(v, 3) for v in bat[0]], [round(v, 3) for v in bat[1]]]),
                       why="a board carrying the IMU cannot occupy the same space as the battery pack; both come from the source MJCF (site 'imu' on trunk_base, mesh np_f970)"))
    pi = aabb(("jaw_soft", "pcb__raspberry_pi_zero_2_w", 0)); hat = aabb(("jaw_soft", "elec_rpi_robot_hat_pcb", 0)); holder = aabb(("jaw_soft", "m12_lens_holder", 0))
    ov = overlap(pi, hat)
    checks.append(dict(name="compute board and Robot HAT do not interpenetrate", verdict="FAIL" if ov else "PASS",
                       measured=dict(compute_aabb_mm=[[round(v, 3) for v in pi[0]], [round(v, 3) for v in pi[1]]], hat_aabb_mm=[[round(v, 3) for v in hat[0]], [round(v, 3) for v in hat[1]]],
                                     overlap_mm=[round(v, 3) for v in ov] if ov else None, board_gap_x_mm=round(pi[0][0] - hat[1][0], 3)),
                       why="two rigid PCBs stacked on a 40-pin header: their AABBs may touch, not cross; the x gap is the header stack height available"))
    ov2 = overlap(pi, holder)
    checks.append(dict(name="room for a camera PCB between the M12 lens holder and the compute board", verdict="FAIL" if (ov2 or (holder[0][0] - pi[1][0]) < 1.0) else "PASS",
                       measured=dict(holder_aabb_mm=[[round(v, 3) for v in holder[0]], [round(v, 3) for v in holder[1]]], gap_x_mm=round(holder[0][0] - pi[1][0], 3),
                                     overlap_mm=[round(v, 3) for v in ov2] if ov2 else None),
                       why="press_desk.jpg shows a separate green camera PCB standing behind the face with the lens holder on it (out/sources/internals/real_desk_head_jaw_off.png); an IMX219 module board is ~1.0 mm FR4 plus its connector, so < 1.0 mm of x between holder and compute means our head has no place for the board the product has"))
    doc_checks = checks
    # ---- merge into internals.json
    doc = json.load(open(DATA)) if os.path.exists(DATA) else {}
    doc["renders"] = renders
    doc["components"] = components
    doc["sites"] = {s: dict(label=SITES[s][0], ref=SITES[s][1], function=SITES[s][2], pos_world_mm=[round(v, 3) for v in st.spos(s)]) for s in SITES}
    doc["not_in_cad"] = [dict(what=w, ref=r, why=y) for w, r, y in NOT_IN_CAD]
    doc["joint_anchors_mm"] = joints
    doc["checks"] = doc_checks
    doc["render_meta"] = dict(model="sim/microduck_ours.xml via sim/compare_render.studio_scene", keyframe="INIT (zero pose, trunk_base z 120 mm)",
                              frame="+x beak, +y left, +z up (SPEC.md §3)", px=[W, H], fovy_deg=float(st.m.vis.global_.fovy),
                              generated=time.strftime("%Y-%m-%d %H:%M:%S"), seconds=round(time.time() - t0, 1))
    json.dump(doc, open(DATA, "w"), indent=1, ensure_ascii=False)
    for c in doc_checks: say("check:", c["verdict"], c["name"], json.dumps(c["measured"]))
    say("internals.json merged: %d renders, %d trunk + %d head component rows, %d sites, %d not-in-CAD; %.1f s" % (
        len(renders), len(components.get("trunk", [])), len(components.get("head", [])), len(SITES), len(NOT_IN_CAD), time.time() - t0))

if __name__ == "__main__":
    main()
