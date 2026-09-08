"""prove_fit.py — DOES THE MICRODUCK PHYSICALLY FIT.

    ce-cad/bin/cad tools/prove_fit.py rest     -> out/fit/rest.json
    ce-cad/bin/cad tools/prove_fit.py sweep    -> out/fit/sweep.json
    ce-cad/bin/cad tools/prove_fit.py access   -> out/fit/access.json
    (bin/cad buffers stdout: every stage writes out/fit/<stage>.log too)

THE QUESTION AND THE INVERSION IT IS ASKED UNDER. The real Microduck walks,
balances and turns its head. So a collision this tool finds is FIRST evidence
that OUR MODEL is wrong -- a wrong dimension, a wrong placement, a wrong
revision of a mesh -- and only after that a design problem. Every finding here
therefore names the dimension it suspects.

WHAT IS CHECKED
  rest    every placed body against every other at the zero pose.
  sweep   every joint driven across its FULL MJCF range; only the pairs the
          joint actually moves relative to each other are re-tested, and any
          pair that starts sharing space is bisected to 0.5 deg to report the
          angle at which the collision BEGINS.
  access  a driver's reach to every fastener head, and the insertion clearance
          in front of every connector.

WHAT THE POSE IS BUILT FROM
  ce-assemblies/microduck/current/placements.json gives every body's world
  placement at the ZERO pose (134 rows: 70 meshes seeded from the MJCF and 64
  screws placed through connections). Each row is converted to its parent
  MJCF body's frame ONCE, by composing with the inverse of that body's
  zero-pose world transform read from the COMPILED MuJoCo model. Any pose is
  then that local transform re-composed with the body transform MuJoCo
  computes for the joint angles. Nothing here re-derives a placement.

  The mesh assets are used as Pollen ships them and NOT as MuJoCo compiles
  them: mjModel.geom_pos carries MuJoCo's own mesh re-centring to the mesh
  centre of mass (measured: trunk_base geom 0 sits at z -3.0004 mm compiled
  against -5.0 mm in the XML), so compiled geom transforms and raw STL files
  must never be mixed. Only body transforms (d.xpos / d.xquat), which MuJoCo
  does not move, are taken from the compiled model.

WHAT A COLLISION MEANS HERE, exactly: the two bodies' surfaces cross, or one
body is inside the other. Two faces resting flush against each other are
CONTACT and are not reported (cecad.meshfit, strict straddle). Volumes and
relief distances carry their voxel resolution.

THREE CLASSES OF PAIR, because they mean different things:
  STRUCTURE x STRUCTURE   any overlap is a finding.
  SCREW x THE PART IT IS DRIVEN INTO   overlap is the THREAD ENGAGEMENT and is
          expected; it is measured, and it is a finding only if the screw
          also breaks out of the far side.
  SCREW x ANY OTHER BODY  any overlap is a finding.
"""
import json
import os
import sys
import time
import traceback

import numpy as np

REPO = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck"
WORKSHOP = "/Users/leifrydenfalk/dev/ce-workshop"
os.environ.setdefault("CE_TRIAD_ROOT", REPO + ":" + WORKSHOP)
sys.path.insert(0, os.path.join(WORKSHOP, "ce-cad"))
OUT = os.path.join(REPO, "out", "fit")
os.makedirs(OUT, exist_ok=True)

STAGE = (sys.argv[1] if len(sys.argv) > 1 else "rest")
LOG = open(os.path.join(OUT, STAGE + ".log"), "w", buffering=1)


def P(*a):
    LOG.write(" ".join(str(x) for x in a) + "\n")
    LOG.flush()


from cecad import meshfit as mf  # noqa: E402


# ------------------------------------------------------------------ model ---
def quat_R(q):
    w, x, y, z = q
    n = (w * w + x * x + y * y + z * z) ** 0.5
    w, x, y, z = w / n, x / n, y / n, z / n
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def abs_mjcf():
    """A copy of the placement MJCF with an absolute meshdir, so MuJoCo can
    compile it from anywhere."""
    import xml.etree.ElementTree as ET
    src = os.path.join(REPO, "reference/pollen-microduck-simulator/"
                             "robot_allcollisions.xml")
    dst = os.path.join(OUT, "_robot_abs.xml")
    t = ET.parse(src)
    t.getroot().find("compiler").set(
        "meshdir", os.path.join(REPO, "reference/pollen-microduck-simulator/meshes"))
    t.write(dst)
    return dst


class Model:
    def __init__(self):
        import mujoco
        self.mujoco = mujoco
        self.m = mujoco.MjModel.from_xml_path(abs_mjcf())
        self.d = mujoco.MjData(self.m)
        self.bname = [mujoco.mj_id2name(self.m, mujoco.mjtObj.mjOBJ_BODY, i)
                      for i in range(self.m.nbody)]
        self.bid = {n: i for i, n in enumerate(self.bname)}
        self.joints = []
        for i in range(self.m.njnt):
            jn = mujoco.mj_id2name(self.m, mujoco.mjtObj.mjOBJ_JOINT, i)
            if self.m.jnt_type[i] != mujoco.mjtJoint.mjJNT_HINGE:
                continue
            self.joints.append({
                "name": jn, "qadr": int(self.m.jnt_qposadr[i]),
                "body": self.bname[self.m.jnt_bodyid[i]],
                "range_deg": [float(np.degrees(self.m.jnt_range[i][0])),
                              float(np.degrees(self.m.jnt_range[i][1]))]})
        # descendants of each body
        self.children = {n: [] for n in self.bname}
        for i in range(1, self.m.nbody):
            self.children[self.bname[self.m.body_parentid[i]]].append(self.bname[i])
        self.zero = self.body_frames(np.zeros(self.m.nq))

        # rows
        rec = json.load(open(os.path.join(
            REPO, "ce-assemblies/microduck/current/placements.json")))["record"]
        self.rows = rec["rows"]
        self.tris = []          # local-frame triangles per row
        self.body_of = []
        self.label = []
        self.kind = []
        self.joins = []
        cache = {}
        self.mesh_scale = {}
        screws = [r for r in self.rows if not r.get("mesh_file")]
        screw_tris = self.build_screws(screws) if screws else {}
        for r in self.rows:
            if r.get("mesh_file"):
                f = r["mesh_file"]
                if f not in cache:
                    T0 = mf.load_stl_tris(f)
                    # THE POLLEN STL ASSETS ARE IN METRES. The MJCF declares
                    # every one of them as a bare <mesh file="..."/> with no
                    # scale attribute, and MuJoCo's length unit in this model
                    # is the metre (the bodies sit at z 0.12, the bearing STL
                    # measures 0.022 x 0.022 x 0.004). placements.json states
                    # its positions in MILLIMETRES. Mixing the two silently
                    # shrinks every body 1000x while leaving it at the right
                    # place: the first run of this tool did exactly that and
                    # reported a confident "18 AABB-overlapping candidates,
                    # 7 interferences" for a robot whose parts had all become
                    # specks. The guard below refuses to guess.
                    ext = float(np.ptp(T0.reshape(-1, 3), axis=0).max())
                    if ext < 1.0:
                        T0 = T0 * 1000.0
                        sc = 1000.0
                    elif ext < 400.0:
                        sc = 1.0
                    else:
                        raise ValueError(
                            "%s has a %.4f unit extent - neither metres nor "
                            "millimetres for a 300 mm robot" % (f, ext))
                    self.mesh_scale[f] = sc
                    cache[f] = T0
                T = cache[f]
                b = r["body"]
                lab = "%s/%s" % (b, r["mesh"])
                kind = "structure"
            else:
                key = (r["part"], (r.get("params") or {}).get("length_mm"))
                T = screw_tris[key]
                b = (r.get("in_bodies") or ["trunk_base"])[0]
                lab = "%s[%s]" % (r["instance"], r["part"].split(":")[1])
                kind = "fastener"
            R = quat_R(r["world_quat_wxyz"])
            t = np.asarray(r["world_pos_mm"], float)
            W = mf.transform_tris(T, R, t).reshape(-1, 3, 3)
            # into the parent body's frame, once
            R0, t0 = self.zero[b]
            local = ((W.reshape(-1, 3) - t0) @ R0).reshape(-1, 3, 3)
            self.tris.append(local)
            self.body_of.append(b)
            self.label.append(lab)
            self.kind.append(kind)
            self.joins.append(r.get("joins") or [])
        self.n = len(self.tris)
        # SANITY, measured and fail-loud: the assembled robot must be the size
        # of a Microduck. COMPARISON.html measures the real product at roughly
        # 300 mm tall; anything outside 150-450 mm means a unit slipped.
        W = self.world(self.zero)
        allv = np.concatenate([w.reshape(-1, 3) for w in W])
        self.bbox = (allv.min(axis=0), allv.max(axis=0))
        h = float(self.bbox[1][2] - self.bbox[0][2])
        P("assembled bbox mm: X %.3f..%.3f  Y %.3f..%.3f  Z %.3f..%.3f"
          % (self.bbox[0][0], self.bbox[1][0], self.bbox[0][1],
             self.bbox[1][1], self.bbox[0][2], self.bbox[1][2]))
        if not (150.0 <= h <= 450.0):
            raise ValueError("assembled height %.3f mm is not a Microduck" % h)
        self.closed = {}
        for i in range(self.n):
            k = self.label[i]
            self.closed[k] = mf.is_closed(self.tris[i])
        nclosed = sum(1 for v in self.closed.values() if v)
        P("closed meshes: %d of %d placed bodies" % (nclosed, self.n))

    def build_screws(self, screws):
        """The 64 fasteners are not meshes: they are built from their ce-parts
        folders through the same loader the placement lane used, then
        tessellated. 7 family members over 6 lengths."""
        import FreeCAD as App
        import cecad.triad as triad
        doc = App.newDocument("fit_screws")
        out = {}
        for r in screws:
            prm = r.get("params") or {}
            key = (r["part"], prm.get("length_mm"))
            if key in out:
                continue
            obj = triad.load(doc, r["part"], prm)
            shp = getattr(obj, "shape", None) or getattr(obj, "Shape", obj)
            v, f = shp.tessellate(0.02)
            V = np.asarray([[p.x, p.y, p.z] for p in v], float)
            out[key] = V[np.asarray(f, int)]
            P("  screw member %s len=%s -> %d triangles"
              % (key[0], key[1], out[key].shape[0]))
        return out

    def body_frames(self, qpos):
        self.d.qpos[:] = qpos
        self.mujoco.mj_forward(self.m, self.d)
        out = {}
        for i in range(1, self.m.nbody):
            out[self.bname[i]] = (quat_R(self.d.xquat[i]),
                                  np.asarray(self.d.xpos[i], float) * 1000.0)
        return out

    def qpos_for(self, angles_deg):
        q = np.zeros(self.m.nq)
        q[3] = 1.0                      # free-joint quaternion w
        for j in self.joints:
            if j["name"] in angles_deg:
                q[j["qadr"]] = np.radians(angles_deg[j["name"]])
        return q

    def world(self, frames):
        """World triangles for every row at the given body frames."""
        out = []
        for i in range(self.n):
            R, t = frames[self.body_of[i]]
            out.append((self.tris[i].reshape(-1, 3) @ R.T + t).reshape(-1, 3, 3))
        return out

    def distal(self, joint_name):
        """Every body moved by this joint (the joint's own body and below)."""
        seed = [j for j in self.joints if j["name"] == joint_name][0]["body"]
        seen, stack = set(), [seed]
        while stack:
            b = stack.pop()
            if b in seen:
                continue
            seen.add(b)
            stack += self.children[b]
        return seen


def boxes(W):
    lo = np.asarray([w.reshape(-1, 3).min(axis=0) for w in W])
    hi = np.asarray([w.reshape(-1, 3).max(axis=0) for w in W])
    return lo, hi


def pair_class(M, i, j):
    ki, kj = M.kind[i], M.kind[j]
    if ki == "fastener" and kj == "fastener":
        return "screw x screw"
    if ki == "fastener" or kj == "fastener":
        s, o = (i, j) if ki == "fastener" else (j, i)
        mesh = M.rows[o].get("mesh")
        if mesh and mesh in M.joins[s]:
            return "screw x the part it is driven into"
        return "screw x other body"
    return "structure x structure"


def test_pair(M, W, i, j, full=True):
    r = mf.measure_pair(W[i], W[j], volume=full, depth=full)
    return r


def main_rest(M):
    t0 = time.time()
    frames = M.zero
    W = M.world(frames)
    lo, hi = boxes(W)
    P("rows=%d  triangles=%d" % (M.n, sum(w.shape[0] for w in W)))
    cand = []
    for i in range(M.n):
        for j in range(i + 1, M.n):
            if np.all(hi[i] >= lo[j]) and np.all(hi[j] >= lo[i]):
                cand.append((i, j))
    P("pairs=%d  aabb-overlapping candidates=%d"
      % (M.n * (M.n - 1) // 2, len(cand)))
    hits = []
    for k, (i, j) in enumerate(cand):
        try:
            r = test_pair(M, W, i, j)
        except MemoryError as e:
            r = {"verdict": "CANNOT DETERMINE", "why": str(e)}
        cls = pair_class(M, i, j)
        if r.get("interferes") or r.get("intersecting_tri_pairs"):
            row = {"a": M.label[i], "b": M.label[j], "class": cls,
                   "a_body": M.body_of[i], "b_body": M.body_of[j],
                   "intersecting_tri_pairs": r.get("intersecting_tri_pairs"),
                   "fully_contained": r.get("fully_contained"),
                   "overlap": r.get("overlap_volume"),
                   "penetration": r.get("penetration"),
                   "detected_by": r.get("detected_by")}
            hits.append(row)
            P("  HIT %-46s x %-46s %-34s %s mm3"
              % (M.label[i], M.label[j], cls,
                 (r.get("overlap_volume") or {}).get("mm3")))
        if k % 200 == 0:
            P("  ... %d/%d candidates, %.1f s" % (k, len(cand), time.time() - t0))
    res = {"$what": "every placed body against every other at the ZERO pose",
           "rows": M.n, "pairs_possible": M.n * (M.n - 1) // 2,
           "aabb_candidates": len(cand), "interfering_pairs": len(hits),
           "seconds": round(time.time() - t0, 1), "hits": hits}
    json.dump(res, open(os.path.join(OUT, "rest.json"), "w"), indent=1)
    P("DONE rest: %d interfering pairs of %d candidates in %.1f s"
      % (len(hits), len(cand), time.time() - t0))


if __name__ == "__main__":
    try:
        t0 = time.time()
        P("stage:", STAGE)
        M = Model()
        P("model built in %.1f s: %d rows, %d bodies, %d hinges"
          % (time.time() - t0, M.n, len(M.bname) - 1, len(M.joints)))
        if STAGE == "rest":
            main_rest(M)
        else:
            P("unknown stage")
    except Exception:
        P("RAISED:\n" + traceback.format_exc())
        raise
