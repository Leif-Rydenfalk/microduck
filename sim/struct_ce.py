#!/usr/bin/env python3
"""struct_ce.py — buckling and first-mode frequency of the slender members,
through ce-struct (:8099, voxel mesher + CalculiX), on OUR rebuilt meshes.

Lane F1, 2026-09-02. The static FEA (sim/stress_all.py) asks whether a part
yields; this asks whether it FOLDS first — a 1 mm plate or a 58 mm shin under
the landing load is a column, and yield can be far away while the buckling
load factor is not. Loads are the measured MuJoCo peaks (loads_mujoco.json);
the load is applied axially over the end face (at: min/max of the member's
long axis), the other end held. ce-struct rule: criticalFactor >= 2 PASS.

    python3 sim/struct_ce.py      -> out/sim-evidence/buckling_<part>.json
"""
import base64
import json
import os
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVID = os.path.join(ROOT, "out", "sim-evidence")
L = json.load(open(os.path.join(EVID, "loads_mujoco.json")))
DROP = next(d for d in L["drops"] if d["label"] == "drop_foot_rollm10_default_contact_dt5ms")
API = "http://127.0.0.1:8099/api/solve"

# member: (slug, mesh file, long axis, held end, loaded end, material, printNormal (ASSUMED flat = thickness axis), load N, source, cell mm)
MEMBERS = [
    ("microduck-shin", "leg.stl", "z", "max", "min", "PLA", "x",
     DROP["body_transmitted_force_max_N"]["leg"]["magnitude"], "drops[foot].body_transmitted_force_max_N.leg", 1.0),
    ("microduck-upper-leg-rigidity-plate", "upper_leg_rigidity_plate.stl", "z", "min", "max", "PLA", "x",
     DROP["body_transmitted_force_max_N"]["upper_leg_left"]["magnitude"], "drops[foot].body_transmitted_force_max_N.upper_leg_left (100 % through the plate: bounding)", 0.33),
    ("microduck-neck-plate", "../../out/sim-evidence/fea/microduck-neck-plate_ours.stl", "y", "min", "max", "PLA", "x",
     0.5 * DROP["body_transmitted_force_max_N"]["neck"]["magnitude"], "0.5 x drops[foot].body_transmitted_force_max_N.neck (two plates)", 0.4),
]


def solve(spec, study, stl_b64, options=None):
    body = json.dumps({"spec": spec, "study": study, "options": options or {}, "stlBase64": stl_b64}).encode()
    req = urllib.request.Request(API, data=body, headers={"content-type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=900) as r:
        out = json.loads(r.read().decode())
    out["_seconds"] = round(time.time() - t0, 2)
    return out


def main():
    for slug, stl, axis, held, loaded, mat, pn, F, src, cell in MEMBERS:
        prev = os.path.join(EVID, "buckling_" + slug + ".json")
        if os.path.exists(prev) and json.load(open(prev)).get("verdict") in ("PASS", "FAIL") and "--force" not in sys.argv:
            print("skip (done)", slug); continue
        path = os.path.normpath(os.path.join(ROOT, "sim", "meshes_ours", stl))
        rec = {"study": "buckling_" + slug, "part": "part:" + slug, "generated": time.strftime("%Y-%m-%dT%H:%M:%S"), "script": "sim/struct_ce.py",
               "inputs": {"mesh": os.path.relpath(path, ROOT), "cell_mm": cell, "long_axis": axis, "held_face": axis + "=" + held, "loaded_face": axis + "=" + loaded,
                          "force_N": round(F, 4), "force_source": "out/sim-evidence/loads_mujoco.json :: " + src, "material": mat,
                          "printNormal_ASSUMED": pn + " (the thickness axis — the part printed flat; no part.py declares print_up)",
                          "solver": "ce-struct /api/solve (voxel hex mesh + CalculiX *BUCKLE / *FREQUENCY)"},
               "method": "axial compression over the whole end face, the other end fixed xyz; buckling eigenvalue = load factor on the applied force; first natural frequency with the same support",
               "artifacts": [], "looked_at": []}
        if not os.path.exists(path):
            rec.update(verdict="CANNOT DETERMINE", why="no rebuilt mesh at %s" % rec["inputs"]["mesh"])
            json.dump(rec, open(os.path.join(EVID, rec["study"] + ".json"), "w"), indent=1); print(rec["verdict"], slug, rec["why"]); continue
        b64 = base64.b64encode(open(path, "rb").read()).decode()
        vec = [0.0, 0.0, 0.0]
        vec["xyz".index(axis)] = (F if loaded == "min" else -F)     # push the loaded end toward the held end
        spec = {"name": slug + " column", "cell": cell, "geometry": {"kind": "stl"},
                "bodies": [{"name": slug, "material": mat, "printNormal": pn}],
                "constraints": [{"name": "held", "face": {"axis": axis, "at": held}, "dirs": "xyz", "value": 0}],
                "loads": [{"name": "landing axial", "kind": "force", "face": {"axis": axis, "at": loaded}, "vector": vec}],
                "studies": ["buckle", "frequency"]}
        out = {}
        for study in ("buckle", "frequency"):
            try:
                out[study] = solve(spec, study, b64, {"modes": 3})
            except Exception as e:  # noqa: BLE001
                out[study] = {"error": str(e)[-400:]}
            print(slug, study, json.dumps({k: v for k, v in out[study].items() if k not in ("field", "fields", "mesh", "nodes", "cells_xyz")})[:400])
        rec["outputs"] = out
        b = out.get("buckle", {})
        crit = b.get("critical") or b.get("criticalFactor")
        if b.get("error") or crit is None:
            rec.update(verdict="CANNOT DETERMINE", why="buckle solve refused: %s" % (b.get("error") or json.dumps(b)[:300]))
        else:
            rec["outputs"]["critical_load_N"] = round(float(crit) * F, 4)
            rec.update(verdict="PASS" if float(crit) >= 2.0 else "FAIL",
                       why="buckling load factor %.4f on the %.4f N landing load (critical %.2f N); ce-struct rule factor >= 2" % (float(crit), F, float(crit) * F))
        fr = out.get("frequency", {})
        if not fr.get("error"):
            rec["outputs"]["first_mode_hz"] = fr.get("frequencies", fr.get("hz", fr.get("f1")))
        json.dump(rec, open(os.path.join(EVID, rec["study"] + ".json"), "w"), indent=1)
        print("  ->", rec["verdict"], rec["why"])


if __name__ == "__main__":
    main()
