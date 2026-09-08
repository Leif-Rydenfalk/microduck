#!/usr/bin/env python3
"""tools/upstream_meshdiff.py — mesh-by-mesh diff of two Pollen asset trees.

Run as: ce-cad/bin/cad tools/upstream_meshdiff.py  (needs numpy; writes the
JSON after EVERY mesh so a killed run loses one row, not the file).

For each STL present in both trees: bbox of each (mm, 4 dp), triangle count,
byte sha256, and cecad.meshcompare both ways (p95, max, mean) at the SPEC.md
§8 rule (p95 <= 1.0 mm both ways, bbox within 1.5 mm/axis). Both trees are
authored in METRES by onshape-to-robot, so both are scaled x1000. No
alignment: the two exports share the part frame, so a translation between
them IS a finding, not noise.
"""
import hashlib, json, os, sys, time
sys.path.insert(0, "/Users/leifrydenfalk/dev/ce-workshop/ce-cad")
import numpy as np
from cecad import meshcompare, mjcf

OLD = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck/reference/pollen-microduck-rl/assets"
NEW = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck/reference/pollen-microduck-rl-develop/microduck/assets"
OUT = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck/out/sources/upstream-develop-meshdiff.json"

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        h.update(f.read())
    return h.hexdigest()

def bbox(T):
    P = T.reshape(-1, 3)
    lo, hi = P.min(0), P.max(0)
    return {"min_mm": [round(float(v), 4) for v in lo], "max_mm": [round(float(v), 4) for v in hi],
            "size_mm": [round(float(v), 4) for v in (hi - lo)], "centre_mm": [round(float(v), 4) for v in ((hi + lo) / 2)]}

old = sorted(f for f in os.listdir(OLD) if f.endswith(".stl"))
new = sorted(f for f in os.listdir(NEW) if f.endswith(".stl"))
res = {"generated": time.strftime("%Y-%m-%d %H:%M:%S %z"), "old_tree": OLD, "new_tree": NEW,
       "old_commit": "5946fd9cdbc58956424420153e51975af3b30d77", "new_commit": "29e887ecfbf5d37144759e5a9f8a176dfb83d547",
       "rule": "SPEC.md §8: p95 surface distance <= 1.0 mm both ways AND bbox within 1.5 mm per axis; both trees x1000 (metres -> mm); no alignment",
       "only_in_old": [f for f in old if f not in new], "only_in_new": [f for f in new if f not in old],
       "meshes": {}}
if os.path.exists(OUT):
    try:
        res["meshes"] = json.load(open(OUT)).get("meshes", {})
    except Exception:
        pass

def save():
    tmp = OUT + ".tmp"
    json.dump(res, open(tmp, "w"), indent=1)
    os.replace(tmp, OUT)

for f in old:
    if f not in new or f in res["meshes"]:
        continue
    t0 = time.time()
    To = np.asarray(mjcf.read_stl(os.path.join(OLD, f)), dtype=float) * 1000.0
    Tn = np.asarray(mjcf.read_stl(os.path.join(NEW, f)), dtype=float) * 1000.0
    row = {"old": {"sha256": sha(os.path.join(OLD, f)), "bytes": os.path.getsize(os.path.join(OLD, f)), "tris": int(len(To)), "bbox": bbox(To)},
           "new": {"sha256": sha(os.path.join(NEW, f)), "bytes": os.path.getsize(os.path.join(NEW, f)), "tris": int(len(Tn)), "bbox": bbox(Tn)}}
    row["bbox_delta_mm"] = {k: [round(b - a, 4) for a, b in zip(row["old"]["bbox"][k], row["new"]["bbox"][k])] for k in ("min_mm", "max_mm", "size_mm", "centre_mm")}
    # identical triangle soup up to ordering/float noise?
    so = np.sort(To.reshape(-1, 3), axis=0); sn = np.sort(Tn.reshape(-1, 3), axis=0)
    row["vertex_set_identical"] = bool(len(To) == len(Tn) and np.allclose(so, sn, atol=1e-6))
    row["max_vertex_delta_mm_if_same_count"] = (round(float(np.abs(so - sn).max()), 6) if len(To) == len(Tn) else None)
    try:
        c = meshcompare.compare(Tn, To, cand_scale=1.0, ref_scale=1.0, samples=15000, tol_mm=1.0, bbox_tol_mm=1.5, align=False, seed=0)
        row["compare"] = {"verdict": c.get("verdict"), "why": c.get("why"),
                          "old_to_new": {k: (round(v, 4) if isinstance(v, float) else v) for k, v in c["ref_to_cand"].items()},
                          "new_to_old": {k: (round(v, 4) if isinstance(v, float) else v) for k, v in c["cand_to_ref"].items()},
                          "bbox": c.get("bbox")}
    except Exception as e:
        row["compare"] = {"verdict": "CANNOT DETERMINE", "why": f"meshcompare raised {type(e).__name__}: {e}"}
    row["seconds"] = round(time.time() - t0, 1)
    res["meshes"][f] = row
    save()
    print(f, row["compare"].get("verdict"), row["bbox_delta_mm"]["size_mm"], row["seconds"], flush=True)

# orphans: compare the 4 removed STLs against their likely survivors
pairs = [("left_upper_leg.stl", "upper_leg_left.stl"), ("right_upper_leg.stl", "upper_leg_right.stl"),
         ("trunk_shell_left.stl", "left_shell.stl"), ("trunk_shell_right.stl", "right_shell.stl")]
res["removed_vs_survivor"] = {}
for a, b in pairs:
    pa, pb = os.path.join(OLD, a), os.path.join(NEW, b)
    if not (os.path.exists(pa) and os.path.exists(pb)):
        continue
    Ta = np.asarray(mjcf.read_stl(pa), dtype=float) * 1000.0
    Tb = np.asarray(mjcf.read_stl(pb), dtype=float) * 1000.0
    c = meshcompare.compare(Tb, Ta, samples=15000, tol_mm=1.0, bbox_tol_mm=1.5, align=False)
    res["removed_vs_survivor"][a] = {"survivor_in_new": b, "removed_bbox": bbox(Ta), "survivor_bbox": bbox(Tb),
        "removed_tris": int(len(Ta)), "survivor_tris": int(len(Tb)),
        "verdict": c.get("verdict"), "why": c.get("why"),
        "removed_to_survivor_p95_mm": round(c["ref_to_cand"]["p95_mm"], 4), "survivor_to_removed_p95_mm": round(c["cand_to_ref"]["p95_mm"], 4)}
    save()
    print("orphan", a, "vs", b, c.get("verdict"), flush=True)
res["done"] = True
save()
print("DONE", len(res["meshes"]), flush=True)
