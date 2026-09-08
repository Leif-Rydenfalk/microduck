#!/usr/bin/env python3
"""cables3d.py — the Microduck harness as 3-D GEOMETRY, routed through the
assembly, checked against the solids and the joint ranges, drawable by both
renderers.

Leif, 2026-09-03: "the wiring doesnt show up in ours". wiring/cables.json is a
LIST (22 cables, 1615 mm, floor-length rule); this tool turns every cable that
has two known endpoints into a route:

  endpoint  -> the device point wiring/cables.json already measured (servo
               socket on the XL330's side face, board centroid, MJCF site),
               attached to the body that carries the device;
  exit stub -> a straight stub out of the socket face for the JST EH housing
               (EH_STUB_MM, source stated below);
  waypoints -> authored here in WORLD mm at the INIT pose, each attached to
               the body it rides with (ROUTES below). A waypoint's numbers
               come from the per-geom world AABBs printed by this tool
               (--aabb) and from the product photographs listed in
               out/wiring/cables3d.json photo_observations;
  curve     -> Catmull-Rom through stub + waypoints + stub, sampled every
               SAMPLE_MM; a free span between two bodies is straight in the
               body-local sense at INIT and moves with both bodies.

At ANY pose (qpos) the world polyline is recomputed from the body frames, so
the pose-matched renders can carry the harness: `capsules_xml(model, data)`
returns MuJoCo capsule geoms for the current pose and
`studio_scene_with_cables(qpos)` a whole scene XML.

CHECKS (each PASS / FAIL / CANNOT DETERMINE, every number recorded):
  inside_solid  every sample point tested for being inside a visual mesh
                (ray-parity against the compiled mesh triangles in world);
                samples within EXEMPT_MM of an endpoint are exempt from that
                endpoint's own device geom (the socket IS in the case);
  clearance     nearest triangle of any geom on a body OTHER than the
                bodies the sample is anchored to (i.e. parts that move
                relative to the cable) — must be >= OD/2 + CLEAR_MM;
  bend_radius   circle through consecutive sample triplets, min radius must
                be >= BEND_RULE_X_OD x OD (rule declared, no vendor value:
                CANNOT DETERMINE the vendor minimum);
  slack         for every crossed hinge, sweep it through its MJCF range
                (others at INIT) and over the 2^n range corners; required
                length L(q) vs the CABLES.md allocation cable_mm; the first
                angle at which L(q) > cable_mm is the TAUT angle — a finding.

Run (stdout is buffered by bin/cad — read out/wiring/run.log):
  ce-cad/bin/cad sim/cables3d.py            routes + checks + renders
  ce-cad/bin/cad sim/cables3d.py --aabb     print every geom's world AABB
  ce-cad/bin/cad sim/cables3d.py --no-render
"""
import os, sys, json, math, time, itertools
os.environ.setdefault("MUJOCO_GL", "glfw")
import numpy as np
import mujoco
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WS = os.path.dirname(os.path.dirname(ROOT))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(WS, "ce-cad"))
import common            # noqa: E402
import compare_render    # noqa: E402

OUT = os.path.join(ROOT, "out", "wiring")
os.makedirs(OUT, exist_ok=True)
CABLES = os.path.join(ROOT, "wiring", "cables.json")
DATA = os.path.join(OUT, "cables3d.json")
LOG = open(os.path.join(OUT, "run.log"), "a")
W = H = 1400

def say(*a):
    s = " ".join(str(x) for x in a)
    print(s); LOG.write(s + "\n"); LOG.flush()

# ---------------------------------------------------------------- constants, each with its source
from cecad.harness import awg_diameter_mm, AWG_FORMULA_CITE  # noqa: E402
AWG_BUS = 21   # E1 §4.4 "Wire Gauge for DYNAMIXEL 21 AWG" (fetched 2026-09-04, cables3d.json wire_sources)
BARE_21AWG_MM = awg_diameter_mm(AWG_BUS)          # ASTM B258, exact
# Insulated OD of the bus wire: NOT published by ROBOTIS. The JST SEH-001T-P0.6
# crimp (E1 §4.4) accepts an insulation OD range that the JST EH datasheet
# states; the value below is the NOMINAL used for rendering and is labelled
# nominal everywhere. cables3d.json wire_sources carries the CANNOT DETERMINE.
INSUL_OD_NOMINAL_MM = 1.60
# a 3-conductor lead rendered as ONE tube: the circle circumscribing three
# touching wires of diameter d has D = d(1 + 2/sqrt(3)) — geometry, exact
BUNDLE3_FACTOR = 1.0 + 2.0 / math.sqrt(3.0)
OD = {  # rendered tube OD per group, mm, and its basis
    "dynamixel-chain": (round(INSUL_OD_NOMINAL_MM * BUNDLE3_FACTOR, 4),
                        "3 x 21 AWG (E1 §4.4) at NOMINAL insulated OD %.2f mm bundled: d(1+2/sqrt3) — jacket OD CANNOT DETERMINE" % INSUL_OD_NOMINAL_MM),
    "power": (round(INSUL_OD_NOMINAL_MM * 2.0, 4), "2 conductors side by side at the same NOMINAL %.2f mm — gauge and OD CANNOT DETERMINE (cables.json bat-hat)" % INSUL_OD_NOMINAL_MM),
    "hat-harness": (2.0, "NOMINAL 2.0 mm: JST-SH / GH 1.0-1.25 mm-pitch leads (28-32 AWG class) — gauge and OD CANNOT DETERMINE (cables.json)"),
}
OD_CSI = (1.0, "22-pin 0.5 mm FFC ribbon rendered as a Ø1.0 mm tube: NOMINAL; the ribbon is flat, ~13 mm wide")
EH_STUB_MM = 8.0     # straight stub out of the socket face for the JST EH housing + strain: NOMINAL (JST EH datasheet is a scanned PDF; see cables3d.json)
SAMPLE_MM = 1.0
EXEMPT_MM = 7.0      # samples this close to an endpoint are exempt from the endpoint device's own geom
CLEAR_MM = 1.0       # required clearance beyond OD/2 from parts that move relative to the cable — rule declared here
BEND_RULE_X_OD = 3.0  # minimum bend radius = 3 x OD — rule declared here (IPC/WHMA-A-620 style; vendor value CANNOT DETERMINE)
COLOUR = {"dynamixel-chain": (0.93, 0.55, 0.12, 1.0), "power": (0.80, 0.16, 0.14, 1.0), "hat-harness": (0.18, 0.44, 0.75, 1.0)}
COLOUR_NAME = {"dynamixel-chain": "amber = servo bus (VDD/GND/DATA)", "power": "red = battery feed", "hat-harness": "blue = sensors / speaker / camera"}

# ---------------------------------------------------------------- the routes
# Each entry: list of (body, [x, y, z] world mm at INIT). Endpoints and exit
# stubs are added by the tool from cables.json. Numbers were read off the
# --aabb table (out/wiring/aabb.txt) and the photographs; the checks below
# are what validates them, not this comment.
LEFT = {
    "dxl-hat-id34": [("jaw_soft", [55.0, 6.0, 254.0]), ("jaw_soft", [44.0, 16.0, 257.0])],
    "dxl-id34-id33": [("jaw_soft", [35.1, 18.65, 222.0]), ("jaw_soft", [18.0, 8.0, 220.5]), ("jaw_soft", [0.0, -4.0, 220.5])],
    "dxl-id33-id32": [("jaw_soft", [-13.25, -9.0, 250.0]), ("jaw_soft", [-2.0, -16.0, 250.0]), ("yaw_roll_motion", [10.0, -16.0, 247.0])],
    "dxl-id32-id31": [("yaw_roll_motion", [42.0, -14.0, 236.0]), ("yaw_roll_motion", [42.0, -21.0, 222.0]),
                      ("neck_pitch", [40.0, -22.0, 206.0]), ("neck", [30.0, -22.0, 196.0]), ("neck", [12.0, -16.0, 195.0])],
    "dxl-id31-id30": [("neck", [45.0, -6.85, 185.0]), ("neck", [45.0, -6.85, 170.0])],
    "dxl-id30-imu200": [("neck", [6.0, -8.0, 161.0]), ("trunk_base", [-2.0, -4.0, 150.0]), ("trunk_base", [19.5, -2.0, 128.0]),
                        ("trunk_base", [21.0, -1.0, 112.0]), ("trunk_base", [-8.0, 0.0, 106.0])],
    "dxl-imu200-id20": [("trunk_base", [-8.0, 2.0, 106.0]), ("trunk_base", [21.0, 2.0, 112.0]), ("trunk_base", [19.5, 2.0, 128.0]), ("trunk_base", [8.0, 1.0, 138.0])],
    "dxl-id20-id21": [("trunk_base", [4.0, 1.0, 136.0]), ("trunk_base", [19.5, 1.0, 128.0]), ("trunk_base", [21.0, 1.0, 112.0]), ("yaw2roll", [12.0, 2.0, 100.0])],
    "dxl-id21-id22": [("yaw2roll", [-6.0, 4.0, 84.0]), ("yaw2roll", [-6.0, 18.0, 74.0]), ("hip_l", [-6.0, 36.0, 76.0]),
                      ("upper_leg_left", [-6.0, 50.0, 96.0]), ("upper_leg_left", [-5.0, 58.0, 116.0])],
    "dxl-id22-id23": [("upper_leg_left", [-8.0, 66.0, 88.0]), ("upper_leg_left", [-14.0, 66.0, 86.0])],
    "dxl-id23-id24": [("upper_leg_left", [-14.0, 58.0, 78.0]), ("leg", [-15.0, 50.0, 62.0]), ("leg", [-14.0, 46.0, 52.0])],
}
# right leg = mirror of the left leg's leg cables (y -> -y), bodies renamed
MIRROR_BODY = {"yaw2roll": "bearing_roll", "hip_l": "hip_l_2", "upper_leg_left": "upper_leg_right", "leg": "leg_2", "ankle_left": "ankle_right", "trunk_base": "trunk_base"}
MIRROR_ID = {"dxl-imu200-id20": "dxl-imu200-id10", "dxl-id20-id21": "dxl-id10-id11", "dxl-id21-id22": "dxl-id11-id12", "dxl-id22-id23": "dxl-id12-id13", "dxl-id23-id24": "dxl-id13-id14"}
HEADHARNESS = {
    "tof-hat": [("jaw_soft", [55.0, 12.0, 258.0]), ("jaw_soft", [62.0, 34.0, 256.0]), ("jaw_soft", [74.0, 32.0, 252.0])],
    "spk-hat": [("jaw_soft", [55.0, -8.0, 258.0]), ("jaw_soft", [40.0, -14.0, 262.0]), ("jaw_soft", [15.0, -14.0, 262.0]), ("jaw_soft", [0.0, -8.0, 258.0])],
    "csi-radxa-camera": [("jaw_soft", [70.0, 0.0, 239.0]), ("jaw_soft", [76.0, 14.0, 240.0]), ("jaw_soft", [80.0, 14.0, 248.0])],
    "bat-hat": [("trunk_base", [-33.0, 0.0, 159.0]), ("trunk_base", [-10.0, -10.0, 159.0]), ("trunk_base", [8.0, -13.0, 160.0]),
                ("neck", [10.0, -19.0, 175.0]), ("neck", [12.0, -21.0, 195.0]), ("neck_pitch", [14.0, -22.0, 206.0]),
                ("yaw_roll_motion", [13.0, -22.0, 224.0]), ("yaw_roll_motion", [12.0, -21.0, 240.0]),
                ("jaw_soft", [10.0, -19.0, 253.0]), ("jaw_soft", [30.0, -20.0, 261.0]), ("jaw_soft", [52.0, -12.0, 260.0])],
}
def routes():
    r = dict(LEFT); r.update(HEADHARNESS)
    for lid, rid in MIRROR_ID.items():
        r[rid] = [(MIRROR_BODY[b], [p[0], -p[1], p[2]]) for b, p in LEFT[lid]]
    return r

# ---------------------------------------------------------------- model
class Model:
    def __init__(self):
        self.scene = compare_render.studio_scene(common.robot_file("ours"))
        self.m = mujoco.MjModel.from_xml_string(self.scene, {})
        self.d = mujoco.MjData(self.m)
        self.key("INIT")
        # explicit colours so alpha edits work
        for g in range(self.m.ngeom):
            mid = self.m.geom_matid[g]
            if mid >= 0:
                self.m.geom_rgba[g] = self.m.mat_rgba[mid]
        self.base_rgba = self.m.geom_rgba.copy()
        self.q0 = self.d.qpos.copy()
        self.bodies = {mujoco.mj_id2name(self.m, mujoco.mjtObj.mjOBJ_BODY, b): b for b in range(self.m.nbody)}
        self.joints = {}
        for j in range(self.m.njnt):
            if self.m.jnt_type[j] == mujoco.mjtJoint.mjJNT_HINGE:
                self.joints[mujoco.mj_id2name(self.m, mujoco.mjtObj.mjOBJ_JOINT, j)] = j
        # visual mesh geoms and their world triangle soups (rebuilt per pose)
        self.vis = [g for g in range(self.m.ngeom) if self.m.geom_type[g] == mujoco.mjtGeom.mjGEOM_MESH and self.m.geom_group[g] != 3]
        self.gname = {g: (mujoco.mj_id2name(self.m, mujoco.mjtObj.mjOBJ_BODY, self.m.geom_bodyid[g]),
                          mujoco.mj_id2name(self.m, mujoco.mjtObj.mjOBJ_MESH, self.m.geom_dataid[g])) for g in self.vis}
        # INIT-pose body frames for authoring: world -> local
        self.T0 = {b: (self.d.xpos[i].copy() * 1000.0, self.d.xmat[i].reshape(3, 3).copy()) for b, i in self.bodies.items()}

    def key(self, name):
        kid = mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_KEY, name)
        mujoco.mj_resetDataKeyframe(self.m, self.d, kid); mujoco.mj_forward(self.m, self.d)

    def set_qpos(self, q):
        self.d.qpos[:] = q; mujoco.mj_forward(self.m, self.d)

    def local(self, body, p_world_mm):
        pos, R = self.T0[body]
        return R.T @ (np.asarray(p_world_mm, float) - pos)

    def world(self, body, p_local_mm):
        i = self.bodies[body]
        return self.d.xmat[i].reshape(3, 3) @ np.asarray(p_local_mm, float) + self.d.xpos[i] * 1000.0

    def tris(self, g):
        """world triangles of geom g at the current pose (N,3,3) mm."""
        mid = self.m.geom_dataid[g]
        v0, nv = self.m.mesh_vertadr[mid], self.m.mesh_vertnum[mid]
        f0, nf = self.m.mesh_faceadr[mid], self.m.mesh_facenum[mid]
        V = self.m.mesh_vert[v0:v0 + nv]; F = self.m.mesh_face[f0:f0 + nf]
        Wv = (V @ self.d.geom_xmat[g].reshape(3, 3).T + self.d.geom_xpos[g]) * 1000.0
        return Wv[F]

    def aabb(self, g):
        t = self.tris(g).reshape(-1, 3)
        return t.min(0), t.max(0)

# ---------------------------------------------------------------- geometry helpers
def catmull_rom(P, step_mm):
    """centripetal Catmull-Rom through points P (n,3), resampled ~step_mm."""
    P = np.asarray(P, float)
    if len(P) < 2:
        return P
    if len(P) == 2:
        n = max(2, int(np.linalg.norm(P[1] - P[0]) / step_mm) + 1)
        return np.linspace(P[0], P[1], n)
    Q = np.vstack([P[0] + (P[0] - P[1]), P, P[-1] + (P[-1] - P[-2])])
    out = []
    for i in range(1, len(Q) - 2):
        p0, p1, p2, p3 = Q[i - 1], Q[i], Q[i + 1], Q[i + 2]
        n = max(2, int(np.linalg.norm(p2 - p1) / step_mm) + 1)
        # centripetal parametrisation (alpha 0.5) — no cusps, no overshoot
        def tj(ti, pi, pj):
            return ti + max(np.linalg.norm(pj - pi), 1e-9) ** 0.5
        t0 = 0.0; t1 = tj(t0, p0, p1); t2 = tj(t1, p1, p2); t3 = tj(t2, p2, p3)
        for t in np.linspace(t1, t2, n, endpoint=False):
            A1 = (t1 - t) / (t1 - t0) * p0 + (t - t0) / (t1 - t0) * p1
            A2 = (t2 - t) / (t2 - t1) * p1 + (t - t1) / (t2 - t1) * p2
            A3 = (t3 - t) / (t3 - t2) * p2 + (t - t2) / (t3 - t2) * p3
            B1 = (t2 - t) / (t2 - t0) * A1 + (t - t0) / (t2 - t0) * A2
            B2 = (t3 - t) / (t3 - t1) * A2 + (t - t1) / (t3 - t1) * A3
            out.append((t2 - t) / (t2 - t1) * B1 + (t - t1) / (t2 - t1) * B2)
    out.append(P[-1])
    return np.array(out)

def polyline_length(P):
    P = np.asarray(P, float)
    return float(np.sum(np.linalg.norm(np.diff(P, axis=0), axis=1))) if len(P) > 1 else 0.0

def min_bend_radius(P):
    """radius of the circle through each consecutive triplet; min over the curve."""
    P = np.asarray(P, float)
    if len(P) < 3:
        return None, None
    a = P[:-2]; b = P[1:-1]; c = P[2:]
    ab = np.linalg.norm(b - a, axis=1); bc = np.linalg.norm(c - b, axis=1); ca = np.linalg.norm(a - c, axis=1)
    cross = np.linalg.norm(np.cross(b - a, c - a), axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        R = ab * bc * ca / (2.0 * cross)
    R = np.where(cross < 1e-9, np.inf, R)
    i = int(np.argmin(R))
    return float(R[i]), b[i].tolist()

def points_inside(P, T):
    """ray-parity point-in-mesh: P (n,3) points, T (m,3,3) triangles. Ray along a fixed skew direction."""
    if len(P) == 0 or len(T) == 0:
        return np.zeros(len(P), bool)
    dirv = np.array([0.5773, 0.5774, 0.5775]); dirv /= np.linalg.norm(dirv)
    v0, v1, v2 = T[:, 0], T[:, 1], T[:, 2]
    e1 = v1 - v0; e2 = v2 - v0
    h = np.cross(dirv, e2)                     # (m,3)
    a = np.einsum("ij,ij->i", e1, h)           # (m,)
    ok = np.abs(a) > 1e-9
    inv = np.zeros_like(a); inv[ok] = 1.0 / a[ok]
    counts = np.zeros(len(P), int)
    for k in range(0, len(P), 64):
        p = P[k:k + 64]                                    # (b,3)
        s = p[:, None, :] - v0[None, :, :]                 # (b,m,3)
        u = np.einsum("bmj,mj->bm", s, h) * inv[None, :]
        q = np.cross(s, e1[None, :, :])
        v = np.einsum("bmj,j->bm", q, dirv) * inv[None, :]
        t = np.einsum("bmj,mj->bm", q, e2) * inv[None, :]
        hit = ok[None, :] & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-6)
        counts[k:k + 64] = hit.sum(1)
    return (counts % 2) == 1

def point_tri_dist(P, T):
    """min distance from each point to any triangle (Ericson, vectorised). P (n,3), T (m,3,3)."""
    if len(P) == 0 or len(T) == 0:
        return np.full(len(P), np.inf)
    out = np.full(len(P), np.inf)
    a, b, c = T[:, 0], T[:, 1], T[:, 2]
    ab = b - a; ac = c - a; bc = c - b
    for k in range(0, len(P), 32):
        p = P[k:k + 32][:, None, :]
        ap = p - a[None]; bp = p - b[None]; cp = p - c[None]
        d1 = np.einsum("bmj,mj->bm", ap, ab); d2 = np.einsum("bmj,mj->bm", ap, ac)
        d3 = np.einsum("bmj,mj->bm", bp, ab); d4 = np.einsum("bmj,mj->bm", bp, ac)
        d5 = np.einsum("bmj,mj->bm", cp, ab); d6 = np.einsum("bmj,mj->bm", cp, ac)
        vc = d1 * d4 - d3 * d2; vb = d5 * d2 - d1 * d6; va = d3 * d6 - d5 * d4
        # region tests -> closest point
        cl = np.empty(p.shape[0:1] + (len(T), 3))
        r_a = (d1 <= 0) & (d2 <= 0)
        r_b = (d3 >= 0) & (d4 <= d3)
        r_c = (d6 >= 0) & (d5 <= d6)
        r_ab = (vc <= 0) & (d1 >= 0) & (d3 <= 0)
        r_ac = (vb <= 0) & (d2 >= 0) & (d6 <= 0)
        r_bc = (va <= 0) & ((d4 - d3) >= 0) & ((d5 - d6) >= 0)
        with np.errstate(divide="ignore", invalid="ignore"):
            v_ab = np.nan_to_num(d1 / (d1 - d3)); w_ac = np.nan_to_num(d2 / (d2 - d6))
            w_bc = np.nan_to_num((d4 - d3) / ((d4 - d3) + (d5 - d6)))
            denom = 1.0 / (va + vb + vc); v_in = vb * denom; w_in = vc * denom
        cl[:] = a[None] + ab[None] * v_in[..., None] + ac[None] * w_in[..., None]
        cl = np.where(r_bc[..., None], b[None] + bc[None] * w_bc[..., None], cl)
        cl = np.where(r_ac[..., None], a[None] + ac[None] * w_ac[..., None], cl)
        cl = np.where(r_ab[..., None], a[None] + ab[None] * v_ab[..., None], cl)
        cl = np.where(r_c[..., None], c[None], cl)
        cl = np.where(r_b[..., None], b[None], cl)
        cl = np.where(r_a[..., None], a[None], cl)
        dist = np.linalg.norm(p - cl, axis=2).min(1)
        out[k:k + 32] = dist
    return out

# ---------------------------------------------------------------- cables
class Cable:
    def __init__(self, M, row, dev, waypoints):
        self.id = row["id"]; self.group = row["group"]; self.row = row
        self.od, self.od_basis = (OD_CSI if row["id"] == "csi-radxa-camera" else OD[row["group"]])
        fb, tb = dev[row["from"]]["body"], dev[row["to"]]["body"]
        self.from_body, self.to_body = fb, tb
        a = np.asarray(row["from_xyz_mm"], float); b = np.asarray(row["to_xyz_mm"], float)
        pts = [(fb, a)]
        sa = self.stub(M, row["from"], row.get("from_point"), a, dev)
        if sa is not None: pts.append((fb, sa))
        pts += [(bd, np.asarray(p, float)) for bd, p in waypoints]
        sb = self.stub(M, row["to"], row.get("to_point"), b, dev)
        if sb is not None: pts.append((tb, sb))
        pts.append((tb, b))
        # store body-local anchors
        self.anchors = [(bd, M.local(bd, p)) for bd, p in pts]
        self.crosses = list(row["crosses"])

    @staticmethod
    def stub(M, devname, pointname, p, dev):
        """straight exit stub out of a servo socket face (normal read off the device's geom AABB centre)."""
        d = dev[devname]
        if d["kind"] != "xl330" or pointname not in ("+y", "-y"):
            return None
        # the socket lies on a face of the servo case: the outward normal is the axis along which
        # the point sits on the AABB boundary of the nearest xl330 geom of that body
        best = None
        for g in M.vis:
            if M.gname[g] != (d["body"], "xl330"):
                continue
            lo, hi = M.aabb(g)
            c = (lo + hi) / 2
            if np.all(p >= lo - 1.5) and np.all(p <= hi + 1.5):
                off = np.abs(np.abs(p - c) - (hi - lo) / 2)      # distance to each face pair
                ax = int(np.argmin(off)); n = np.zeros(3); n[ax] = np.sign(p[ax] - c[ax]) or 1.0
                best = p + n * EH_STUB_MM
        return best

    def world_points(self, M):
        return np.array([M.world(bd, p) for bd, p in self.anchors])

    def curve(self, M):
        return catmull_rom(self.world_points(M), SAMPLE_MM)

    def sample_bodies(self, M, curve):
        """for each curve sample the (prev, next) anchor bodies — parts on those bodies ride with it."""
        P = self.world_points(M)
        # cumulative arc positions of anchors along the curve: nearest curve index to each anchor
        idx = [int(np.argmin(np.linalg.norm(curve - p, axis=1))) for p in P]
        owners = []
        k = 0
        for i in range(len(curve)):
            while k + 1 < len(idx) - 1 and i >= idx[k + 1]:
                k += 1
            owners.append((self.anchors[k][0], self.anchors[min(k + 1, len(self.anchors) - 1)][0]))
        return owners

# ---------------------------------------------------------------- checks
def check_geometry(M, cab, label):
    """inside-solid + clearance + bend radius at the CURRENT pose."""
    C = cab.curve(M); owners = cab.sample_bodies(M, C)
    a = C[0]; b = C[-1]
    near_a = np.linalg.norm(C - a, axis=1) < EXEMPT_MM
    near_b = np.linalg.norm(C - b, axis=1) < EXEMPT_MM
    inside = np.zeros(len(C), bool); inside_geoms = {}
    clear = np.full(len(C), np.inf); clear_geom = [None] * len(C)
    dev_from, dev_to = cab.from_body, cab.to_body
    for g in M.vis:
        lo, hi = M.aabb(g)
        body, mesh = M.gname[g]
        sel = np.all(C >= lo - 4.0, axis=1) & np.all(C <= hi + 4.0, axis=1)
        if not sel.any():
            continue
        T = M.tris(g)
        ii = np.where(sel)[0]
        ins = points_inside(C[ii], T)
        # exemption: endpoint device geom near its own endpoint (the socket is in the case)
        if body == dev_from: ins &= ~near_a[ii]
        if body == dev_to: ins &= ~near_b[ii]
        if ins.any():
            inside[ii[ins]] = True
            inside_geoms["%s/%s" % (body, mesh)] = int(ins.sum())
        # clearance against parts NOT on the bodies this stretch rides with
        mv = np.array([body not in owners[i] for i in ii])
        if mv.any():
            dd = point_tri_dist(C[ii[mv]], T)
            for j, dv in zip(ii[mv], dd):
                if dv < clear[j]:
                    clear[j] = dv; clear_geom[j] = "%s/%s" % (body, mesh)
    L = polyline_length(C)
    rmin, rat = min_bend_radius(C)
    kmin = int(np.argmin(clear)) if np.isfinite(clear).any() else None
    need = cab.od / 2 + CLEAR_MM
    return dict(
        pose=label, length_mm=round(L, 4), samples=len(C),
        inside_solid=dict(count=int(inside.sum()), geoms=inside_geoms,
                          verdict="PASS" if not inside.any() else "FAIL",
                          first_point_mm=[round(v, 3) for v in C[int(np.argmax(inside))]] if inside.any() else None),
        clearance=dict(min_mm=(round(float(clear[kmin]), 4) if kmin is not None else None),
                       against=(clear_geom[kmin] if kmin is not None else None),
                       at_mm=([round(v, 3) for v in C[kmin]] if kmin is not None else None),
                       required_mm=round(need, 4),
                       verdict=("CANNOT DETERMINE" if kmin is None else ("PASS" if clear[kmin] >= need else "FAIL"))),
        bend=dict(min_radius_mm=(round(rmin, 4) if rmin is not None and np.isfinite(rmin) else None), at_mm=rat,
                  required_mm=round(BEND_RULE_X_OD * cab.od, 4),
                  verdict=("CANNOT DETERMINE" if rmin is None else ("PASS" if rmin >= BEND_RULE_X_OD * cab.od else "FAIL"))),
    )

def check_slack(M, cab, steps=25):
    """sweep every crossed hinge over its range (others at INIT) + all range corners."""
    if not cab.crosses:
        return None
    M.set_qpos(M.q0); L0 = polyline_length(cab.curve(M))
    alloc = cab.row["cable_mm"]
    res = dict(allocated_mm_cables_json=alloc, length_init_mm=round(L0, 4), sweeps=[], corners=None)
    Lmax = L0; argmax = {}
    for jn in cab.crosses:
        j = M.joints[jn]; lo, hi = M.m.jnt_range[j]; adr = M.m.jnt_qposadr[j]
        taut = None; rows = []
        for q in np.linspace(lo, hi, steps):
            M.set_qpos(M.q0); M.d.qpos[adr] = q; mujoco.mj_forward(M.m, M.d)
            L = polyline_length(cab.curve(M)); rows.append((round(math.degrees(q), 3), round(L, 3)))
            if L > Lmax: Lmax = L; argmax = {jn: round(math.degrees(q), 3)}
            if alloc is not None and L > alloc and taut is None:
                taut = dict(joint=jn, angle_deg=round(math.degrees(q), 3), required_mm=round(L, 3), allocated_mm=alloc)
        res["sweeps"].append(dict(joint=jn, range_deg=[round(math.degrees(lo), 3), round(math.degrees(hi), 3)],
                                  length_min_mm=round(min(r[1] for r in rows), 3), length_max_mm=round(max(r[1] for r in rows), 3),
                                  taut=taut, samples=rows))
    # corners of the crossed joints' ranges together
    corners = []
    for signs in itertools.product((0, 1), repeat=len(cab.crosses)):
        M.set_qpos(M.q0)
        for s, jn in zip(signs, cab.crosses):
            j = M.joints[jn]; M.d.qpos[M.m.jnt_qposadr[j]] = M.m.jnt_range[j][s]
        mujoco.mj_forward(M.m, M.d)
        L = polyline_length(cab.curve(M))
        corners.append(dict(angles_deg={jn: round(math.degrees(M.m.jnt_range[M.joints[jn]][s]), 3) for s, jn in zip(signs, cab.crosses)}, length_mm=round(L, 3)))
        if L > Lmax: Lmax = L; argmax = corners[-1]["angles_deg"]
    res["corners"] = corners
    res["length_max_over_range_mm"] = round(Lmax, 4); res["length_max_at"] = argmax
    res["taut"] = [s["taut"] for s in res["sweeps"] if s["taut"]] + [dict(corner=c["angles_deg"], required_mm=c["length_mm"], allocated_mm=alloc) for c in corners if alloc is not None and c["length_mm"] > alloc]
    res["verdict"] = ("CANNOT DETERMINE" if alloc is None else ("FAIL" if res["taut"] else "PASS"))
    M.set_qpos(M.q0)
    return res

# ---------------------------------------------------------------- MuJoCo geometry for any pose
def capsules_xml(M, cables, step_mm=3.0):
    """<geom type=capsule fromto=...> for every cable at the CURRENT pose of M (worldbody, no contacts)."""
    parts = []
    for cab in cables:
        C = catmull_rom(cab.world_points(M), step_mm) / 1000.0
        r = cab.od / 2000.0
        rgba = " ".join("%.3f" % v for v in COLOUR[cab.group])
        for i in range(len(C) - 1):
            a, b = C[i], C[i + 1]
            parts.append('<geom name="cab_%s_%d" type="capsule" size="%.6f" fromto="%.6f %.6f %.6f %.6f %.6f %.6f" rgba="%s" contype="0" conaffinity="0" group="0"/>' % (
                cab.id, i, r, a[0], a[1], a[2], b[0], b[1], b[2], rgba))
    return "\n".join(parts)

def studio_scene_with_cables(M, cables, qpos=None):
    """the compare_render studio scene with the harness baked in at pose qpos (default INIT)."""
    if qpos is not None: M.set_qpos(qpos)
    root = ET.fromstring(M.scene)
    wb = root.find("worldbody")
    for el in ET.fromstring("<r>" + capsules_xml(M, cables) + "</r>"):
        wb.append(el)
    return ET.tostring(root, encoding="unicode")

# ---------------------------------------------------------------- rendering
def font(sz):
    for p in ("/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/Supplemental/Arial.ttf"):
        if os.path.exists(p): return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

SHELLS = {"left_shell", "right_shell", "top_head_shell", "bottom_head_shell", "face_part", "jaw", "jaw_soft", "soft_mouth_top", "noenoeil", "upper_leg_left__ours", "upper_leg_right__ours"}

def render_views(M, cables, views, qpos=None):
    xml = studio_scene_with_cables(M, cables, qpos)
    open(os.path.join(OUT, "scene_cables.xml"), "w").write(xml)
    m2 = mujoco.MjModel.from_xml_string(xml, {}); d2 = mujoco.MjData(m2)
    d2.qpos[:] = (qpos if qpos is not None else M.q0); mujoco.mj_forward(m2, d2)
    for g in range(m2.ngeom):
        mid = m2.geom_matid[g]
        if mid >= 0: m2.geom_rgba[g] = m2.mat_rgba[mid]
    base = m2.geom_rgba.copy()
    r = mujoco.Renderer(m2, H, W); cam = mujoco.MjvCamera(); cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    opt = mujoco.MjvOption(); opt.geomgroup[:] = 0; opt.geomgroup[0] = 1; opt.geomgroup[1] = 1; opt.geomgroup[2] = 1
    out = []
    for v in views:
        m2.geom_rgba[:] = base
        for g in range(m2.ngeom):
            if m2.geom_type[g] != mujoco.mjtGeom.mjGEOM_MESH: continue
            mesh = mujoco.mj_id2name(m2, mujoco.mjtObj.mjOBJ_MESH, m2.geom_dataid[g])
            body = mujoco.mj_id2name(m2, mujoco.mjtObj.mjOBJ_BODY, m2.geom_bodyid[g])
            if v.get("shell_alpha") is not None and mesh in SHELLS:
                m2.geom_rgba[g, 3] = v["shell_alpha"]
            if v.get("bodies") and body not in v["bodies"]:
                m2.geom_rgba[g, 3] = min(m2.geom_rgba[g, 3], v.get("other_alpha", 0.12))
        cam.lookat[:] = np.asarray(v["lookat_mm"], float) / 1000.0; cam.azimuth = v["az"]; cam.elevation = v["el"]; cam.distance = v["dist_m"]
        r.update_scene(d2, cam, opt)
        im = Image.fromarray(r.render().copy())
        # legend
        dr = ImageDraw.Draw(im, "RGBA"); f = font(20); ft = font(28); fs = font(15)
        dr.rectangle([0, 0, W, 60], fill=(255, 255, 255, 235))
        dr.text((22, 8), v["title"], fill=(28, 30, 34), font=ft)
        dr.text((22, 40), v["sub"], fill=(90, 90, 90), font=fs)
        y = H - 100
        for gname, col in COLOUR.items():
            c = tuple(int(255 * x) for x in col[:3])
            dr.line([(30, y), (80, y)], fill=c, width=6); dr.text((90, y - 11), COLOUR_NAME[gname], fill=(28, 30, 34), font=f); y += 30
        fn = v["file"]; im.save(os.path.join(OUT, fn))
        # non-blank check: count non-white pixels
        arr = np.asarray(im.convert("L")); nonwhite = int((arr < 245).sum())
        say("render %s  az %s el %s dist %s  non-white px %d (%.1f%%)" % (fn, v["az"], v["el"], v["dist_m"], nonwhite, 100.0 * nonwhite / arr.size))
        out.append(dict(file="out/wiring/" + fn, title=v["title"], camera=dict(az=v["az"], el=v["el"], dist_m=v["dist_m"], lookat_mm=v["lookat_mm"]),
                        shell_alpha=v.get("shell_alpha"), nonwhite_px=nonwhite, real_photo=v.get("real"), real_crop=v.get("real_crop")))
    return out

def pair(render_file, real_file, crop, out_file, cap_left, cap_right):
    """our render beside the real photo crop, same height."""
    A = Image.open(os.path.join(ROOT, render_file)).convert("RGB")
    B = Image.open(os.path.join(ROOT, real_file)).convert("RGB")
    l, t, rr, b = crop; Wb, Hb = B.size
    B = B.crop((int(l * Wb), int(t * Hb), int(rr * Wb), int(b * Hb)))
    h = 1000
    A = A.resize((int(A.width * h / A.height), h), Image.LANCZOS); B = B.resize((int(B.width * h / B.height), h), Image.LANCZOS)
    im = Image.new("RGB", (A.width + B.width + 30, h + 50), "white")
    im.paste(B, (0, 40)); im.paste(A, (B.width + 30, 40))
    dr = ImageDraw.Draw(im); f = font(20)
    dr.text((10, 8), "REAL — " + cap_right, fill=(28, 30, 34), font=f); dr.text((B.width + 40, 8), "OURS — " + cap_left, fill=(36, 59, 83), font=f)
    im.save(os.path.join(OUT, out_file))
    return "out/wiring/" + out_file

# ---------------------------------------------------------------- main
def main():
    t0 = time.time()
    M = Model()
    if "--aabb" in sys.argv:
        with open(os.path.join(OUT, "aabb.txt"), "w") as f:
            for g in M.vis:
                lo, hi = M.aabb(g)
                f.write("%-18s %-40s g%-3d x %8.2f..%8.2f  y %8.2f..%8.2f  z %8.2f..%8.2f\n" % (M.gname[g] + (g,) + tuple(v for pr in zip(lo, hi) for v in pr)))
        say("wrote aabb.txt"); return
    cab = json.load(open(CABLES))["record"]; dev = cab["devices"]
    R = routes()
    cables = []; unrouted = []
    for row in cab["cables"]:
        if "from_xyz_mm" not in row or "to_xyz_mm" not in row or row.get("qty", 1) == 0 or row["cable_mm"] == 0:
            unrouted.append(dict(id=row["id"], why=row["how"]))
            continue
        if row["id"] not in R:
            unrouted.append(dict(id=row["id"], why="no route authored")); continue
        cables.append(Cable(M, row, dev, R[row["id"]]))
    say("routed %d cables, unrouted %d" % (len(cables), len(unrouted)))
    doc = json.load(open(DATA)) if os.path.exists(DATA) else {"$triad": 1, "kind": "cables3d", "record": {}}
    rec = doc["record"]
    rec.update(dict(
        generated_by="sim/cables3d.py", generated=time.strftime("%Y-%m-%d %H:%M:%S"),
        rules=dict(sample_mm=SAMPLE_MM, exempt_mm=EXEMPT_MM, clearance_rule="min clearance from parts on other bodies >= OD/2 + %.1f mm (declared here)" % CLEAR_MM,
                   bend_rule="min bend radius >= %.0f x OD (declared here; vendor minimum CANNOT DETERMINE)" % BEND_RULE_X_OD,
                   eh_stub_mm=EH_STUB_MM, eh_stub_basis="NOMINAL straight exit for the JST EHR-03 housing; the housing drawing is a scanned PDF (cables3d.json wire_sources)",
                   bare_21awg_mm=round(BARE_21AWG_MM, 4), awg_formula=AWG_FORMULA_CITE, insulated_od_nominal_mm=INSUL_OD_NOMINAL_MM,
                   bundle3_factor=round(BUNDLE3_FACTOR, 6), od_by_group={k: dict(od_mm=v[0], basis=v[1]) for k, v in OD.items()}, od_csi=dict(od_mm=OD_CSI[0], basis=OD_CSI[1]),
                   colours={k: dict(rgba=list(v), meaning=COLOUR_NAME[k]) for k, v in COLOUR.items()}),
        unrouted=unrouted))
    rows = []; total_init = 0.0; total_alloc = 0
    for c in cables:
        M.set_qpos(M.q0)
        P0 = c.world_points(M)
        r = dict(id=c.id, group=c.group, od_mm=c.od, od_basis=c.od_basis, from_body=c.from_body, to_body=c.to_body,
                 conductors=c.row["conductors"], connector=c.row["connector"], pins=c.row["pins"],
                 anchors=[dict(body=b, local_mm=[round(v, 4) for v in p], world_init_mm=[round(v, 4) for v in M.world(b, p)]) for b, p in c.anchors],
                 polyline_world_init_mm=[[round(v, 3) for v in p] for p in c.curve(M)[::3]],
                 crosses=c.crosses, floor_mm_cables_json=c.row["floor_mm"], allocated_mm_cables_json=c.row["cable_mm"])
        geo = [check_geometry(M, c, "INIT")]
        M.key("PHOTO"); geo.append(check_geometry(M, c, "PHOTO")); M.key("STAND"); geo.append(check_geometry(M, c, "STAND")); M.set_qpos(M.q0)
        # crossed joints at their extremes
        for jn in c.crosses:
            j = M.joints[jn]
            for s, lab in ((0, "min"), (1, "max")):
                M.set_qpos(M.q0); M.d.qpos[M.m.jnt_qposadr[j]] = M.m.jnt_range[j][s]; mujoco.mj_forward(M.m, M.d)
                geo.append(check_geometry(M, c, "%s@%s(%.1f deg)" % (jn, lab, math.degrees(M.m.jnt_range[j][s]))))
        M.set_qpos(M.q0)
        r["geometry_checks"] = geo
        r["slack"] = check_slack(M, c)
        L0 = geo[0]["length_mm"]; r["length_init_mm"] = L0
        r["length_max_over_range_mm"] = r["slack"]["length_max_over_range_mm"] if r["slack"] else L0
        r["delta_vs_allocated_mm"] = round(r["length_max_over_range_mm"] - c.row["cable_mm"], 4)
        r["delta_init_vs_floor_mm"] = round(L0 - c.row["floor_mm"], 4)
        v = dict(inside_solid="PASS" if all(g["inside_solid"]["verdict"] == "PASS" for g in geo) else "FAIL",
                 clearance="FAIL" if any(g["clearance"]["verdict"] == "FAIL" for g in geo) else ("PASS" if all(g["clearance"]["verdict"] == "PASS" for g in geo) else "CANNOT DETERMINE"),
                 bend="FAIL" if any(g["bend"]["verdict"] == "FAIL" for g in geo) else "PASS",
                 slack=(r["slack"]["verdict"] if r["slack"] else "PASS (crosses no joint)"))
        r["verdicts"] = v
        total_init += L0; total_alloc += c.row["cable_mm"]
        rows.append(r)
        say("%-18s L0 %8.3f  Lmax %8.3f  alloc %4d  delta %+8.3f | inside %s (%d) clear %s (%.2f vs %s) bend %s (%.2f) slack %s %s" % (
            c.id, L0, r["length_max_over_range_mm"], c.row["cable_mm"], r["delta_vs_allocated_mm"],
            v["inside_solid"], sum(g["inside_solid"]["count"] for g in geo), v["clearance"], min((g["clearance"]["min_mm"] or 99) for g in geo), geo[0]["clearance"]["against"],
            v["bend"], min((g["bend"]["min_radius_mm"] or 99) for g in geo), v["slack"], [t for g in ([r["slack"]] if r["slack"] else []) for t in g["taut"]][:1]))
    rec["cables"] = rows
    rec["totals"] = dict(routed=len(rows), length_init_mm=round(total_init, 3), length_max_over_range_mm=round(sum(r["length_max_over_range_mm"] for r in rows), 3),
                         allocated_mm_cables_json=total_alloc, cables_md_total_mm=cab["total_length_mm"],
                         note="CABLES.md's 1615 mm counts 21 cables incl. hat-radxa-40pin at 0 mm; the routed set excludes it and the three with no endpoints/qty 0")
    rec["summary"] = {k: {vv: sum(1 for r in rows if r["verdicts"][k] == vv) for vv in ("PASS", "FAIL", "CANNOT DETERMINE")} for k in ("inside_solid", "clearance", "bend", "slack")}
    doc["status"] = "routes + checks written; renders %s" % ("skipped" if "--no-render" in sys.argv else "below")
    json.dump(doc, open(DATA, "w"), indent=1, ensure_ascii=False)
    say("checkpoint: cables3d.json written (%d cables) %.1f s" % (len(rows), time.time() - t0))
    if "--no-render" in sys.argv:
        return
    # ---- renders
    M.set_qpos(M.q0)
    views = [
        dict(file="whole-iso-fl.png", title="Harness — whole robot, front-left", sub="INIT pose, shells at 18 % so the runs inside the trunk and head read", lookat_mm=[0, 0, 150], az=225, el=-12, dist_m=0.56, shell_alpha=0.18),
        dict(file="whole-back-right.png", title="Harness — whole robot, rear-right", sub="INIT pose, shells at 18 %; the neck bundle and the battery feed run on the rear", lookat_mm=[0, 0, 150], az=45, el=-12, dist_m=0.56, shell_alpha=0.18,
             real="images/store/store_microduck-graphite-standing-back-three-quarter-right-02.jpg", real_crop=(0.12, 0.10, 0.88, 0.98)),
        dict(file="trunk.png", title="Trunk — hip-yaw servos, imu_to_dxl node, battery feed", sub="INIT pose, trunk shells at 15 %, other bodies dimmed; camera from the rear-left, low", lookat_mm=[-5, 0, 130], az=150, el=-8, dist_m=0.26, shell_alpha=0.15,
             bodies={"trunk_base", "neck", "yaw2roll", "bearing_roll"}, real="images/store/store_microduck-graphite-standing-back-three-quarter-right-02.jpg", real_crop=(0.22, 0.34, 0.72, 0.72)),
        dict(file="head.png", title="Head — HAT, roll/yaw servos, speaker, ToF, camera ribbon", sub="INIT pose, head shells at 15 %; camera from the left, slightly below", lookat_mm=[30, 0, 245], az=260, el=-14, dist_m=0.30, shell_alpha=0.15,
             bodies={"jaw_soft", "yaw_roll_motion", "neck_pitch", "neck"}, real="images/press/press_closeup.jpg", real_crop=(0.10, 0.02, 0.85, 0.50)),
        dict(file="neck.png", title="Neck — the bundle past the two pitch servos", sub="INIT pose; bus hops id30-id31-id32 and the battery feed; front sockets as in the photographs", lookat_mm=[26, 0, 190], az=300, el=-6, dist_m=0.24, shell_alpha=0.15,
             real="images/press/press_closeup.jpg", real_crop=(0.30, 0.35, 0.75, 0.65)),
        dict(file="leg-left.png", title="Left leg — hip yaw/roll/pitch, knee, ankle hops", sub="INIT pose, thigh plate at 15 %; camera from the left-front", lookat_mm=[-15, 40, 80], az=250, el=-10, dist_m=0.27, shell_alpha=0.15,
             bodies={"trunk_base", "yaw2roll", "hip_l", "upper_leg_left", "leg", "ankle_left"}, real="images/store/store_microduck-cream-standing-profile-left.jpg", real_crop=(0.28, 0.42, 0.82, 0.98)),
        dict(file="leg-right.png", title="Right leg — mirror of the left", sub="INIT pose, thigh plate at 15 %; camera from the right-front", lookat_mm=[-15, -40, 80], az=110, el=-10, dist_m=0.27, shell_alpha=0.15,
             bodies={"trunk_base", "bearing_roll", "hip_l_2", "upper_leg_right", "leg_2", "ankle_right"}, real="images/store/store_microduck-graphite-standing-profile-right-02.jpg", real_crop=(0.18, 0.42, 0.72, 0.98)),
        dict(file="stand-prof-left.png", title="STAND pose, left profile — the harness follows the joints", sub="STAND keyframe (hips -26.2 deg, knees, ankles), shells at 18 %", lookat_mm=[0, 0, 150], az=270, el=-8, dist_m=0.50, shell_alpha=0.18, qpos="STAND",
             real="images/store/store_microduck-cream-standing-profile-left.jpg", real_crop=(0.08, 0.05, 0.92, 0.98)),
    ]
    renders = []
    for v in views:
        q = None
        if v.get("qpos") == "STAND":
            M.key("STAND"); q = M.d.qpos.copy(); M.set_qpos(M.q0)
        renders += render_views(M, cables, [v], q)
    pairs = []
    for rv in renders:
        if rv.get("real_photo"):
            pf = pair(rv["file"], rv["real_photo"], rv["real_crop"], "pair-" + os.path.basename(rv["file"]), rv["title"], os.path.basename(rv["real_photo"]))
            rv["pair"] = pf; pairs.append(pf)
    M.set_qpos(M.q0)
    rec["renders"] = renders
    doc["status"] = "routes + checks + %d renders" % len(renders)
    json.dump(doc, open(DATA, "w"), indent=1, ensure_ascii=False)
    say("done: %d renders, %d pairs, %.1f s" % (len(renders), len(pairs), time.time() - t0))

if __name__ == "__main__":
    main()
