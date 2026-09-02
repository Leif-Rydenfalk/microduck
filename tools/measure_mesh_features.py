#!/usr/bin/env python3
"""measure_mesh_features.py — freeze every measurable feature of a reference mesh.

    ce-cad/bin/cad tools/measure_mesh_features.py [mesh ...]
    /Applications/FreeCAD.app/Contents/Resources/bin/python tools/measure_mesh_features.py [mesh ...]

Written 2026-09-02 for ce-designs/microduck lane T. The shelf had 21 parts whose
cad/interfaces.json declared ZERO interfaces, and `bin/triad check` is right to
call that CANNOT DETERMINE: an interfaces file exists to name the anchors other
things connect to, and an empty list names none.

An interface row needs a FRAME and a SOURCE. This script produces the source —
one JSON per mesh, under out/laneT/features/, holding every number a row can
cite and nothing it cannot:

    bbox_mm                 the mesh's own extent, mm (STL is metres, scale 1000)
    holes / bosses / arcs   cecad.meshfeatures.cylinders, classified, with the
                            fit residual and angular cover on every one
    placements              every MJCF body/geom that places this mesh, world
                            pos (mm) + quat (wxyz) at zero pose, from
                            spec/mesh-placements.json — the BODY FRAME an
                            interface row is expressed in
    groups                  holes of equal diameter clustered by axis, so a
                            4 x M2 pattern reads as one pattern and not four
                            unrelated rows

It measures. It does not decide which features are interfaces — a human or an
agent reads the file and authors the rows, citing it. A generator that promoted
every hole to an interface would produce noise with a source, which is worse
than nothing.

Exit 0 measured / 1 a mesh could not be read / 2 broken input.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, "/Users/leifrydenfalk/dev/ce-workshop/ce-cad")

import numpy as np                                   # noqa: E402
from cecad import meshfeatures, mjcf                 # noqa: E402

ASSETS = os.path.join(REPO, "reference", "pollen-microduck-rl", "assets")
OUT = os.path.join(REPO, "out", "laneT", "features")
PLACEMENTS = os.path.join(REPO, "ce-assemblies", "microduck", "current",
                          "placements.json")
MESH_TO_PART = os.path.join(REPO, "spec", "mesh-to-part.json")


def _placements(mesh):
    if not os.path.exists(PLACEMENTS):
        return []
    rows = json.load(open(PLACEMENTS, encoding="utf-8"))["record"]["rows"]
    return [{"body": r["body"], "geom_index": r["geom_index"], "part": r["part"],
             "world_pos_mm": r["world_pos_mm"], "world_quat_wxyz": r["world_quat_wxyz"],
             "source": r["source"]}
            for r in rows if r["mesh"] == mesh]


def _group(holes, tol_d=0.05, tol_ax=1e-3):
    """Cluster equal-diameter, parallel cylinders into patterns."""
    out = []
    for h in holes:
        for g in out:
            if abs(g["d_mm"] - h["d_mm"]) > tol_d:
                continue
            if 1.0 - abs(float(np.dot(g["axis"], h["axis"]))) > tol_ax:
                continue
            g["centres_mm"].append([round(x, 4) for x in h["center_mm"]])
            g["lengths_mm"].append(round(h["length_mm"], 4))
            break
        else:
            out.append({"d_mm": round(h["d_mm"], 4),
                        "axis": [round(x, 4) for x in h["axis"]],
                        "centres_mm": [[round(x, 4) for x in h["center_mm"]]],
                        "lengths_mm": [round(h["length_mm"], 4)]})
    for g in out:
        g["count"] = len(g["centres_mm"])
        C = np.array(g["centres_mm"])
        g["pattern_centroid_mm"] = [round(float(x), 4) for x in C.mean(axis=0)]
        if g["count"] > 1:
            r = np.linalg.norm(C - C.mean(axis=0), axis=1)
            g["pcd_mm"] = round(float(2 * r.mean()), 4)
            g["pcd_spread_mm"] = round(float(r.max() - r.min()), 5)
        else:
            g["pcd_mm"] = None
            g["pcd_spread_mm"] = None
    out.sort(key=lambda g: (-g["count"], g["d_mm"]))
    return out


def measure(mesh):
    path = os.path.join(ASSETS, mesh + ".stl")
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    T = np.asarray(mjcf.read_stl(path), dtype=float) * 1000.0
    V = T.reshape(-1, 3)
    r = meshfeatures.cylinders(path, scale=1000.0)

    def rows(key):
        return [{"d_mm": round(c["d_mm"], 4),
                 "center_mm": [round(x, 4) for x in c["center_mm"]],
                 "axis": [round(x, 4) for x in c["axis"]],
                 "length_mm": round(c["length_mm"], 4),
                 "cover_deg": round(c["cover_deg"], 2),
                 "residual_mm": round(c["residual_mm"], 5),
                 "faces": c["faces"]}
                for c in r[key]]

    return {
        "$what": "every measurable feature of %s.stl, frozen for the "
                 "interfaces.json rows that cite it" % mesh,
        "$generated_by": "tools/measure_mesh_features.py (ce-designs/microduck lane T)",
        "mesh": "reference/pollen-microduck-rl/assets/%s.stl" % mesh,
        "units": "mm (the STL is metres; every number here is x1000), degrees",
        "triangles": int(len(T)),
        "bbox_mm": {"min": [round(float(x), 4) for x in V.min(axis=0)],
                    "max": [round(float(x), 4) for x in V.max(axis=0)],
                    "size": [round(float(x), 4) for x in (V.max(axis=0) - V.min(axis=0))]},
        "instrument": {
            "cylinders": "cecad.meshfeatures.cylinders(scale=1000) — least-squares "
                         "cylinder fit per smooth patch; `residual_mm` is the fit "
                         "error and `cover_deg` the angular extent, so a partial "
                         "arc is visible as one and never reported as a bore",
            "patches": r["patches"],
            "params": r["params"],
        },
        "holes": rows("holes"),
        "bosses": rows("bosses"),
        "partial_arcs": rows("other"),
        "hole_groups": _group(r["holes"]),
        "boss_groups": _group(r["bosses"]),
        "placements": _placements(mesh),
    }


def main(argv):
    meshes = argv[1:]
    if not meshes:
        meshes = sorted(f[:-4] for f in os.listdir(ASSETS) if f.endswith(".stl"))
    os.makedirs(OUT, exist_ok=True)
    bad = 0
    for m in meshes:
        try:
            doc = measure(m)
        except Exception as exc:                        # noqa: BLE001
            print("FAIL  %s: %s" % (m, exc))
            bad += 1
            continue
        p = os.path.join(OUT, m + ".json")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=1)
        print("measured %-32s holes %2d  bosses %2d  arcs %2d  placements %d  -> %s"
              % (m, len(doc["holes"]), len(doc["bosses"]), len(doc["partial_arcs"]),
                 len(doc["placements"]), os.path.relpath(p, REPO)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
