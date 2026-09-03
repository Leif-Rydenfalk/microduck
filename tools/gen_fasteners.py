#!/usr/bin/env python3
"""gen_fasteners.py — the fastener census: measure, mate, reconcile, render, document.

    ce-cad/bin/cad tools/gen_fasteners.py measure  [--region hips-trunk]   # features off Pollen's meshes
    ce-cad/bin/cad tools/gen_fasteners.py spheres                           # ball-joint search, ALL meshes
    ce-cad/bin/cad tools/gen_fasteners.py mate     [--region hips-trunk]   # coaxial partners across the assembly
    ce-cad/bin/cad tools/gen_fasteners.py rebuilt  [--region hips-trunk]   # same detector on OUR rebuild STLs
    ce-cad/bin/cad tools/gen_fasteners.py render   [--region hips-trunk]   # markers on every feature
    ce-cad/bin/cad tools/gen_fasteners.py html                               # FASTENERS.html from the JSON

Written 2026-09-04 (fastener lane, region hips-trunk). Leif, 2026-09-03: "lots
of details like joints and screws and bolts are missing from our cad everything
must be there. all everything including ball joints and it must match exactly".
The assembly BOM had 38 rows and ZERO fasteners because it was seeded from
Pollen's MJCF (visual + collision geometry only). SPEC.md:75-76's 145-hole M2
census is COMMUNITY-DERIVED; this script re-measures it with
cecad.meshfeatures.features() (self-tested, `python -m cecad.meshfeatures
--selftest`) and never inherits a count.

Every step rewrites out/fasteners/census-<region>.json after EVERY part so a kill
leaves the work so far on disk (this lane's first phase was destroyed three
times by restarts). Owns: out/fasteners/, FASTENERS.html, this file.
"""
import datetime as _dt
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
WS = os.path.dirname(os.path.dirname(REPO))
sys.path.insert(0, os.path.join(WS, "ce-cad"))

import numpy as np                                    # noqa: E402
from cecad import meshfeatures, mjcf                  # noqa: E402

ASSETS_RL = os.path.join(REPO, "reference", "pollen-microduck-rl", "assets")
ASSETS_SIM = os.path.join(REPO, "reference", "pollen-microduck-simulator", "meshes")
OUT = os.path.join(REPO, "out", "fasteners")
PLACEMENTS = os.path.join(REPO, "ce-assemblies", "microduck", "current", "placements.json")

REGIONS = {
    "hips-trunk": {
        "hip_l": "part:microduck-hip-bracket",
        "yaw2roll": "part:microduck-yaw2roll",
        "yaw_roll_motion": "part:microduck-yaw-roll-motion",
        "bearing_roll": "part:microduck-bearing-roll",
        "trunk_base": "part:microduck-trunk-base",
        "left_shell": "part:microduck-trunk-shell-left",
        "right_shell": "part:microduck-trunk-shell-right",
        "power_support": "part:microduck-power-support",
        "banana_pcb_locker": "part:microduck-banana-pcb-locker",
    },
}


def census_path(region):
    return os.path.join(OUT, "census-%s.json" % region)


def load_census(region):
    p = census_path(region)
    if os.path.exists(p):
        return json.load(open(p, encoding="utf-8"))
    return {"region": region, "parts": {}, "checkpoints": []}


def save_census(region, doc, note):
    doc["checkpoints"].append({"at": _dt.datetime.now().isoformat(timespec="seconds"), "note": note})
    doc["status"] = note
    os.makedirs(OUT, exist_ok=True)
    tmp = census_path(region) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1)
    os.replace(tmp, census_path(region))


def mesh_paths(mesh):
    """Every copy of the mesh we hold: the rl assets first, the simulator copy
    when it differs (reference/which-mesh-is-denser.json says which is denser)."""
    out = []
    for label, d in (("rl", ASSETS_RL), ("sim", ASSETS_SIM)):
        p = os.path.join(d, mesh + ".stl")
        if os.path.exists(p):
            out.append((label, p))
    return out


def _round(x, n=4):
    if isinstance(x, float):
        return round(x, n)
    if isinstance(x, list):
        return [_round(v, n) for v in x]
    if isinstance(x, dict):
        return {k: _round(v, n) for k, v in x.items()}
    return x


# ----------------------------------------------------------------- measure

def measure_mesh(path):
    t0 = time.time()
    T = np.asarray(mjcf.read_stl(path), dtype=float) * 1000.0
    V = T.reshape(-1, 3)
    r = meshfeatures.features(T, scale=1.0)
    rows = []
    for h in r["holes"]:
        rows.append(_round({
            "feature": "hole", "index": h["index"], "role": h["role"], "d_mm": h["d_mm"],
            "reads_as": h["reading"]["reads_as"], "size": h["reading"]["size"], "class": h["reading"]["class"],
            "delta_to_table_mm": h["reading"]["delta_mm"], "alternatives": h["reading"]["alternatives"],
            "depth_mm": h["depth_mm"], "through": h["through"], "entry": h["entry"],
            "ends": h["ends"], "axis": h["axis"], "center_mm": h["center_mm"],
            "extent_along_axis_mm": h["extent_along_axis_mm"],
            "counterbore": h["counterbore"], "counterbore_of": h["counterbore_of"],
            "entry_from_counterbore": h.get("entry_from_counterbore"),
            "fit": {"faces": h["faces"], "cover_deg": h["cover_deg"], "residual_mm": h["residual_mm"]},
            "method": "cecad.meshfeatures.features: dihedral patch (35 deg) -> least-squares cylinder; ends by 24 axis-parallel probe rays (0.55/0.75/0.95 r x 8 angles, probe 0.15 mm); counterbore = coaxial relation",
        }))
    for b in r["bosses"]:
        rows.append(_round({
            "feature": "boss", "index": b["index"], "role": b["role"], "d_mm": b["d_mm"],
            "reads_as": b["reading"]["reads_as"], "size": b["reading"]["size"], "class": b["reading"]["class"],
            "height_mm": b["length_mm"], "axis": b["axis"], "center_mm": b["center_mm"],
            "hole": b["hole"],
            "fit": {"faces": b["faces"], "cover_deg": b["cover_deg"], "residual_mm": b["residual_mm"]},
            "method": "cecad.meshfeatures.features: cylinder fit, normals AWAY from the axis; coaxial hole named",
        }))
    for s in r["spheres"]:
        rows.append(_round({
            "feature": "sphere", "role": s["kind"], "r_mm": s["r_mm"], "d_mm": s["d_mm"],
            "center_mm": s["center_mm"], "residual_mm": s["residual_mm"], "cover": s["cover"],
            "fit": {"faces": s["faces"]},
            "method": "cecad.meshfeatures.spheres: normal-line least squares; cylinders refused (coplanar normals)",
        }))
    counts = {}
    for row in rows:
        k = "%s: %s %s" % (row["feature"], row["role"], row.get("reads_as", ""))
        counts[k] = counts.get(k, 0) + 1
    return {
        "triangles": int(len(T)),
        "bbox_mm": {"min": _round(V.min(axis=0).tolist()), "max": _round(V.max(axis=0).tolist()),
                    "size": _round((V.max(axis=0) - V.min(axis=0)).tolist())},
        "features": rows, "counts": counts,
        "partial_arcs": _round(r["partial_arcs"]),
        "rejected_cylinders": r["rejected"], "rejected_spheres": r["sphere_rejected"][:40],
        "params": r["params"], "seconds": round(time.time() - t0, 1),
    }


def cmd_measure(region):
    doc = load_census(region)
    doc.setdefault("parts", {})
    for mesh, ref in REGIONS[region].items():
        part = doc["parts"].setdefault(ref, {"mesh": mesh})
        part["pollen"] = {}
        for label, path in mesh_paths(mesh):
            print("measuring %-20s [%s] ..." % (mesh, label), flush=True)
            m = measure_mesh(path)
            m["stl"] = os.path.relpath(path, REPO)
            part["pollen"][label] = m
            print("   %d tris  %d features  %.1fs  counts: %s" % (m["triangles"], len(m["features"]), m["seconds"],
                                                                 json.dumps(m["counts"])), flush=True)
        part["status"] = "measured off Pollen's mesh(es): " + ", ".join(k for k in part["pollen"])
        save_census(region, doc, "measure: %s done (partial)" % mesh)
    save_census(region, doc, "measure: all %d parts measured off Pollen's meshes" % len(REGIONS[region]))


# ----------------------------------------------------------------- spheres (all meshes)

def cmd_spheres():
    out = {"$what": "Ball-joint search: every spherical patch on EVERY reference mesh (socket or ball), fitted by cecad.meshfeatures.spheres — Leif named ball joints; this is the measurement, not the assumption",
           "$generated_by": "tools/gen_fasteners.py spheres", "meshes": {}}
    p = os.path.join(OUT, "spheres-all-meshes.json")
    names = sorted(f[:-4] for f in os.listdir(ASSETS_RL) if f.endswith(".stl"))
    for m in names:
        path = os.path.join(ASSETS_RL, m + ".stl")
        t0 = time.time()
        r = meshfeatures.spheres(path, scale=1000.0)
        out["meshes"][m] = {"tris": r["tris"], "spheres": _round(r["spheres"]), "n_rejected": len(r["rejected"]),
                            "rejected_reasons": sorted(set(x["why"].split("(")[0].strip() for x in r["rejected"])),
                            "seconds": round(time.time() - t0, 1)}
        print("%-40s %d spheres  %s" % (m, len(r["spheres"]), [(s["kind"], s["r_mm"], s["cover"]) for s in r["spheres"]]), flush=True)
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1)
    tot = sum(len(v["spheres"]) for v in out["meshes"].values())
    out["total_spheres"] = tot
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print("total spherical patches across %d meshes: %d" % (len(names), tot))


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    cmd = argv[1]
    region = "hips-trunk"
    if "--region" in argv:
        region = argv[argv.index("--region") + 1]
    if cmd == "measure":
        cmd_measure(region)
    elif cmd == "spheres":
        cmd_spheres()
    else:
        from gen_fasteners_steps import run_step   # later steps live beside this file
        return run_step(cmd, region, argv)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
