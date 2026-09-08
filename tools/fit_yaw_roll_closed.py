#!/usr/bin/env python3
"""fit_yaw_roll_closed.py — the four rest-pose pairs that prove_fit.py cannot
grade because reference/pollen-microduck-simulator/meshes/yaw_roll_motion.stl is
open (42 boundary edges), re-measured with the review lane's closed repair
out/review-geometry/microduck-yaw-roll-motion.stl (REPAIR.json: 1270 triangles,
0 boundary edges, same part frame — Kabsch on the 1242 shared triangles gives
identity to 1e-6 mm). placements.json is NOT changed; the substitution is made
in memory for this measurement only.

    ce-cad/bin/cad tools/fit_yaw_roll_closed.py   -> out/fit/yaw-roll-closed.json
"""
import json, os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.argv = [sys.argv[0], "yaw-roll-closed"]
sys.path.insert(0, os.path.join(REPO, "tools"))
import prove_fit as pf
from cecad import meshfit as mf

M = pf.Model()
FIX = os.path.join(REPO, "out/review-geometry/microduck-yaw-roll-motion.stl")
row = [i for i in range(M.n) if M.label[i] == "yaw_roll_motion/yaw_roll_motion"]
assert len(row) == 1, row
i = row[0]
r = M.rows[i]
T0 = mf.load_stl_tris(FIX)
assert np.ptp(T0.reshape(-1, 3), axis=0).max() > 1.0, "repaired mesh is in mm"
R = pf.quat_R(r["world_quat_wxyz"]); t = np.asarray(r["world_pos_mm"], float)
W = mf.transform_tris(T0, R, t).reshape(-1, 3, 3)
R0, t0 = M.zero[M.body_of[i]]
M.tris[i] = ((W.reshape(-1, 3) - t0) @ R0).reshape(-1, 3, 3)
closed = mf.is_closed(M.tris[i])
Wd = M.world(M.zero)
lo, hi = pf.boxes(Wd)
out = {"$what": "rest-pose pairs of yaw_roll_motion re-measured with the closed repaired mesh",
       "mesh": os.path.relpath(FIX, REPO), "closed": bool(closed), "pairs": []}
t1 = time.time()
for j in range(M.n):
    if j == i: continue
    if not (np.all(hi[i] >= lo[j]) and np.all(hi[j] >= lo[i])): continue
    res = mf.measure_pair(Wd[i], Wd[j], volume=True, depth=True)
    out["pairs"].append({"a": M.label[i], "b": M.label[j], "class": pf.pair_class(M, i, j),
                         "interferes": res.get("interferes"),
                         "intersecting_tri_pairs": res.get("intersecting_tri_pairs"),
                         "overlap": res.get("overlap_volume"), "penetration": res.get("penetration"),
                         "fully_contained": res.get("fully_contained")})
    pf.P("  %s x %s interferes=%s tri=%s vol=%s pen=%s" % (
        M.label[i], M.label[j], res.get("interferes"), res.get("intersecting_tri_pairs"),
        (res.get("overlap_volume") or {}).get("mm3"), res.get("penetration")))
out["seconds"] = round(time.time() - t1, 1)
json.dump(out, open(os.path.join(pf.OUT, "yaw-roll-closed.json"), "w"), indent=1)
pf.P("DONE %d pairs" % len(out["pairs"]))
