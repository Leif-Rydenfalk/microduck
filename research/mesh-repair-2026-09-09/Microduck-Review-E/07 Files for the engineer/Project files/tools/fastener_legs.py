#!/usr/bin/env -S /Users/leifrydenfalk/dev/ce-workshop/ce-cad/bin/cad
"""tools/fastener_legs.py — the fastener census for region "legs".

Owned by the legs fastener lane (see out/fasteners/census-legs.json
$owned_paths).  Ten parts: shin (leg), ankle L/R, foot L/R, sole L/R,
upper-leg L/R, upper-leg rigidity plate.

Every stage writes its result to disk BEFORE the next one starts, so a kill
at any moment leaves the measurement taken so far on disk.

    bin/cad tools/fastener_legs.py world      -> out/fasteners/legs/world-placements-legs.json
    bin/cad tools/fastener_legs.py measure    -> out/fasteners/legs/raw/<mesh>.features.json
    bin/cad tools/fastener_legs.py pockets    -> out/fasteners/legs/raw/<mesh>.pockets.json
    bin/cad tools/fastener_legs.py rebuild    -> out/fasteners/legs/raw/<slug>.rebuild.json
    bin/cad tools/fastener_legs.py collect    -> census parts[] + features[]
    bin/cad tools/fastener_legs.py reconcile  -> census parts[].reconcile (mesh vs rebuild)
    bin/cad tools/fastener_legs.py mate       -> census mates[] + fasteners[]
    bin/cad tools/fastener_legs.py render     -> out/fasteners/legs/renders/<mesh>.png

Instruments
  cecad.meshfeatures.features()  cylinders (dihedral patches + least-squares
      cylinder fit), hole ends by 24 axis-parallel probe rays, coaxial
      counterbore relation, sphere fit for ball sockets/studs.
  cecad.meshpockets.pockets()    NON-circular pockets — hex captive-nut
      seats, slots, rectangular press-fit pockets.  meshfeatures fits
      cylinders and spheres only, so a hex nut trap is invisible to it;
      this module is this lane's promotion into the core.
  cecad.mjcf.bodies_world()      the world transform of every body at qpos=0.
      (The pre-existing out/fasteners/world-placements.json is body-local,
      not world — finding F-legs-001 — so this file recomputes it.)
"""
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, "/Users/leifrydenfalk/dev/ce-workshop/ce-cad")

CENSUS = os.path.join(ROOT, "out", "fasteners", "census-legs.json")
LEGS = os.path.join(ROOT, "out", "fasteners", "legs")
RAW = os.path.join(LEGS, "raw")
RENDERS = os.path.join(LEGS, "renders")
MJCF = os.path.join(ROOT, "reference", "pollen-microduck-rl", "robot_allcollisions.xml")

# part slug -> (mesh name, relative stl path)
PARTS = {
    "part:microduck-shin":                    ("leg",                      "reference/pollen-microduck-rl/assets/leg.stl"),
    "part:microduck-ankle-left":              ("ankle_left",               "reference/pollen-microduck-rl/assets/ankle_left.stl"),
    "part:microduck-ankle-right":             ("ankle_right",              "reference/pollen-microduck-rl/assets/ankle_right.stl"),
    "part:microduck-foot-left":               ("foot_left",                "reference/pollen-microduck-rl/assets/foot_left.stl"),
    "part:microduck-foot-right":              ("foot_right",               "reference/pollen-microduck-rl/assets/foot_right.stl"),
    "part:microduck-sole-left":               ("sole_left",                "reference/pollen-microduck-rl/assets/sole_left.stl"),
    "part:microduck-sole-right":              ("sole_right",               "reference/pollen-microduck-rl/assets/sole_right.stl"),
    "part:microduck-upper-leg-left":          ("upper_leg_left",           "reference/pollen-microduck-rl/assets/upper_leg_left.stl"),
    "part:microduck-upper-leg-right":         ("upper_leg_right",          "reference/pollen-microduck-rl/assets/upper_leg_right.stl"),
    "part:microduck-upper-leg-rigidity-plate":("upper_leg_rigidity_plate", "reference/pollen-microduck-rl/assets/upper_leg_rigidity_plate.stl"),
}
MESH2PART = {m: p for p, (m, _) in PARTS.items()}


# --------------------------------------------------------------------------
def load_census():
    with open(CENSUS) as f:
        return json.load(f)


def save_census(c, status=None, checkpoint=None):
    if status:
        c["status"] = status
    if checkpoint:
        c.setdefault("checkpoints", []).append(
            {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "what": checkpoint})
    c["generated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    tmp = CENSUS + ".tmp"
    with open(tmp, "w") as f:
        json.dump(c, f, indent=1)
    os.replace(tmp, CENSUS)


def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, path)


def stl_scale(path):
    """Pollen's STLs are in METRES; measure the bbox and say so, never assume."""
    import numpy as np
    from cecad import mjcf
    T = np.asarray(mjcf.read_stl(path), dtype=float)
    P = T.reshape(-1, 3)
    ext = P.max(0) - P.min(0)
    scale = 1000.0 if float(ext.max()) < 1.0 else 1.0
    return scale, [round(float(x) * scale, 4) for x in ext], int(len(T))


# --------------------------------------------------------------------------
def cmd_world(argv):
    """World transform of every leg-region geom at qpos=0, in mm."""
    import numpy as np
    from cecad import mjcf
    m = mjcf.load(MJCF)
    W = mjcf.bodies_world(m)                       # metres
    rows = []
    for bname in m.order:
        b = m.bodies[bname]
        Rb, tb = W[bname]
        for gi, g in enumerate(b.geoms):
            if g.mesh not in MESH2PART:
                continue
            Rg = mjcf.quat_to_mat(g.quat)
            R = (np.asarray(Rb, float) @ np.asarray(Rg, float))
            t = (np.asarray(Rb, float) @ np.asarray(g.pos, float) + np.asarray(tb, float)) * 1000.0
            rows.append({
                "body": bname, "mesh": g.mesh, "part": MESH2PART[g.mesh],
                "class": g.cls or "visual", "geom_index": gi,
                "R": [[round(float(x), 6) for x in r] for r in R],
                "t_mm": [round(float(x), 4) for x in t],
            })
    out = {
        "generated_by": "tools/fastener_legs.py world",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "source": os.path.relpath(MJCF, ROOT),
        "frame": ("MJCF world at qpos=0, millimetres. "
                  "p_world_mm = R @ (p_mesh_mm) + t_mm, where p_mesh_mm is the STL "
                  "point times its measured scale (Pollen's STLs are metres, x1000)."),
        "method": ("cecad.mjcf.bodies_world(model) composes each body's parent chain "
                   "(quat_to_mat(body.quat), body.pos) from the worldbody down; the geom's "
                   "own pos/quat is then composed on top. Verified below: the two thighs "
                   "must NOT share a transform."),
        "placements": rows,
    }
    # SELF-CHECK. The naive test "the two thighs must not share R and t" FAILS
    # here and that failure is not a bug: upper_leg_left.stl and
    # upper_leg_right.stl are MIRRORED meshes whose file origins land on the
    # same world point, so the placement rows are legitimately identical. The
    # honest test is therefore on the transformed GEOMETRY: push each mesh's
    # bbox through its placement and require the left and right thighs to sit
    # on opposite sides of y=0. (This retracts finding F-legs-001.)
    def wbbox(rr):
        T = np.asarray(mjcf.read_stl(os.path.join(ROOT, "reference/pollen-microduck-rl/assets",
                                                  rr["mesh"] + ".stl")), float).reshape(-1, 3)
        sc = 1000.0 if float((T.max(0) - T.min(0)).max()) < 1.0 else 1.0
        P = (np.asarray(rr["R"], float) @ (T * sc).T).T + np.asarray(rr["t_mm"], float)
        return P.min(0), P.max(0)
    checks = []
    for a, b in (("upper_leg_left", "upper_leg_right"), ("ankle_left", "ankle_right"),
                 ("foot_left", "foot_right"), ("sole_left", "sole_right")):
        ra = next(r for r in rows if r["mesh"] == a and r["class"] == "visual")
        rb = next(r for r in rows if r["mesh"] == b and r["class"] == "visual")
        ca = (lambda lo, hi: (lo + hi) / 2)(*wbbox(ra))
        cb = (lambda lo, hi: (lo + hi) / 2)(*wbbox(rb))
        checks.append({"pair": [a, b],
                       "world_bbox_centre_mm": [[round(float(x), 4) for x in ca],
                                                [round(float(x), 4) for x in cb]],
                       "y_sum_mm": round(float(ca[1] + cb[1]), 4),
                       "verdict": "PASS" if ca[1] * cb[1] < 0 and abs(ca[1] + cb[1]) < 0.01 else "FAIL"})
    out["selfcheck_mirror_pairs"] = {
        "rule": "left and right copies must land mirrored about y=0: y_L*y_R < 0 and |y_L+y_R| < 0.01 mm",
        "checks": checks,
        "verdict": "PASS" if all(c["verdict"] == "PASS" for c in checks) else "FAIL"}
    dump(os.path.join(LEGS, "world-placements-legs.json"), out)
    print("world: %d placements; mirror self-check %s" % (len(rows), out["selfcheck_mirror_pairs"]["verdict"]))
    for c in out["selfcheck_mirror_pairs"]["checks"]:
        print("   %-16s %-16s y %+9.4f / %+9.4f  sum %+.4f  %s" % (
            c["pair"][0], c["pair"][1], c["world_bbox_centre_mm"][0][1],
            c["world_bbox_centre_mm"][1][1], c["y_sum_mm"], c["verdict"]))


# --------------------------------------------------------------------------
def cmd_measure(argv):
    from cecad import meshfeatures
    names = set(argv)
    for part, (mesh, rel) in PARTS.items():
        if names and mesh not in names and part not in names:
            continue
        path = os.path.join(ROOT, rel)
        scale, ext, ntri = stl_scale(path)
        t0 = time.time()
        r = meshfeatures.features(path, scale=scale)
        r["mesh"] = mesh
        r["part"] = part
        r["stl"] = rel
        r["stl_scale_measured"] = scale
        r["bbox_mm"] = ext
        r["tris"] = ntri
        r["measured"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        r["secs"] = round(time.time() - t0, 2)
        dump(os.path.join(RAW, mesh + ".features.json"), r)
        print("%-26s %5d tris  holes %2d  bosses %2d  spheres %d  rejected %2d  %.1fs" % (
            mesh, ntri, len(r.get("holes", [])), len(r.get("bosses", [])),
            len(r.get("spheres", [])), len(r.get("rejected", [])), r["secs"]))
        sys.stdout.flush()


# --------------------------------------------------------------------------
def cmd_pockets(argv):
    from cecad import meshpockets
    names = set(argv)
    for part, (mesh, rel) in PARTS.items():
        if names and mesh not in names and part not in names:
            continue
        path = os.path.join(ROOT, rel)
        scale, ext, ntri = stl_scale(path)
        t0 = time.time()
        r = meshpockets.pockets(path, scale=scale)
        r["mesh"] = mesh
        r["part"] = part
        r["stl"] = rel
        r["measured"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        r["secs"] = round(time.time() - t0, 2)
        dump(os.path.join(RAW, mesh + ".pockets.json"), r)
        print("%-26s pockets %d (%s)  %.1fs" % (
            mesh, len(r.get("pockets", [])),
            ", ".join(sorted({p["kind"] for p in r.get("pockets", [])})) or "-", r["secs"]))
        sys.stdout.flush()


CMDS = {"world": cmd_world, "measure": cmd_measure, "pockets": cmd_pockets}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in CMDS:
        print(__doc__)
        return 2
    os.makedirs(RAW, exist_ok=True)
    os.makedirs(RENDERS, exist_ok=True)
    return CMDS[sys.argv[1]](sys.argv[2:]) or 0


if __name__ == "__main__":
    sys.exit(main())
