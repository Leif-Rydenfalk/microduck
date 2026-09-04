#!/usr/bin/env python3
"""fastener_census.py — measure every fastening feature of a set of Pollen meshes.

    ce-cad/bin/cad tools/fastener_census.py measure <mesh> [...]   -> out/fasteners/head-neck/raw/<mesh>.features.json

Stage 1 of the head-neck fastener census (Leif 2026-09-03: "all everything
including ball joints and it must match exactly"). For each mesh it runs BOTH
instruments the workshop has and writes both readings side by side so the
census can reconcile them:

    cecad.meshfeatures.features   (core; through/blind by 24 probe rays,
                                   counterbore relation, insert/pilot naming,
                                   spheres by normal-line fit; self-tested)
    cecad.meshfasteners.features  (this lane's layer; pairs lead-ins vs
                                   counterbores, pilot/insert bosses, spheres
                                   by algebraic fit + cap angle)

Every file is written the moment the mesh is measured, so a kill leaves the
meshes done so far on disk. Exit 0 measured / 1 a mesh failed.
"""
import json
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, "/Users/leifrydenfalk/dev/ce-workshop/ce-cad")
import numpy as np                                     # noqa: E402
from cecad import meshfeatures, meshfasteners          # noqa: E402

ASSETS = os.path.join(REPO, "reference", "pollen-microduck-rl", "assets")
RAW = os.path.join(REPO, "out", "fasteners", "head-neck", "raw")


def _clean(o):
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, (np.floating,)):
        return round(float(o), 4)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.ndarray):
        return _clean(o.tolist())
    if isinstance(o, float):
        return round(o, 4)
    return o


def measure(mesh):
    stl = os.path.join(ASSETS, mesh + ".stl")
    t0 = time.time()
    T = np.asarray(meshfeatures.mjcf.read_stl(stl), dtype=float) * 1000.0
    bb = [T.reshape(-1, 3).min(axis=0).tolist(), T.reshape(-1, 3).max(axis=0).tolist()]
    mf = meshfeatures.features(T, scale=1.0)
    t1 = time.time()
    mfa = meshfasteners.features(T, scale=1.0)
    t2 = time.time()
    out = {"$what": "raw fastening-feature readings of Pollen's %s.stl by two instruments; mm in the mesh's own frame (STL metres x1000)" % mesh,
           "$generated_by": "tools/fastener_census.py measure", "mesh": mesh,
           "stl": os.path.relpath(stl, REPO), "tris": int(len(T)),
           "bbox_mm": _clean(bb), "size_mm": _clean((np.array(bb[1]) - np.array(bb[0])).tolist()),
           "measured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "seconds": {"meshfeatures": round(t1 - t0, 2), "meshfasteners": round(t2 - t1, 2)},
           "meshfeatures": _clean(mf), "meshfasteners": _clean(mfa)}
    os.makedirs(RAW, exist_ok=True)
    path = os.path.join(RAW, mesh + ".features.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    return path, out


def main(argv):
    if len(argv) < 2 or argv[0] != "measure":
        print(__doc__)
        return 2
    rc = 0
    for mesh in argv[1:]:
        try:
            path, out = measure(mesh)
            print("%-32s tris %6d  holes %3d bosses %3d spheres %2d  %.1fs+%.1fs -> %s" % (
                mesh, out["tris"], len(out["meshfeatures"]["holes"]), len(out["meshfeatures"]["bosses"]),
                len(out["meshfeatures"]["spheres"]), out["seconds"]["meshfeatures"], out["seconds"]["meshfasteners"], os.path.relpath(path, REPO)), flush=True)
        except Exception:
            rc = 1
            print("FAILED", mesh, flush=True)
            traceback.print_exc()
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
