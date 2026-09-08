"""Envelope survey of the two head shells and the face plate — CALIPERS ONLY.

Kernel-free (FreeCAD python + numpy). Reads Pollen's published STLs the way a
person with a height gauge would: outline extents at a ladder of section
planes, wall thickness along named probe lines, and the split-line trace.
Writes out/own/measure/head-shells-survey.json. Nothing here copies a vertex;
every output is a DIMENSION.
"""
import json, os, sys
sys.path.insert(0, "/Users/leifrydenfalk/dev/ce-workshop/ce-cad")
import numpy as np
from cecad import meshslice

REF = "reference/pollen-microduck-rl/assets/%s.stl"
OUT = "out/own/measure/head-shells-survey.json"


def outline(T, axis, level):
    """(u,v) extents of the cut outline at axis=level, or None if no material."""
    S = meshslice.segments(T, axis, level)
    if len(S) == 0:
        return None
    P = S.reshape(-1, 2)
    return dict(u_min=round(float(P[:, 0].min()), 4), u_max=round(float(P[:, 0].max()), 4),
                v_min=round(float(P[:, 1].min()), 4), v_max=round(float(P[:, 1].max()), 4),
                n_seg=int(len(S)))


def survey(name):
    T = meshslice.load(REF % name, 1000.0)
    P = T.reshape(-1, 3)
    lo, hi = P.min(0), P.max(0)
    d = {"mesh": REF % name, "triangles": int(len(T)),
         "bbox_min": lo.round(4).tolist(), "bbox_max": hi.round(4).tolist(),
         "bbox_size": (hi - lo).round(4).tolist()}
    for axis, i in (("x", 0), ("y", 1), ("z", 2)):
        levels = np.linspace(lo[i] + 0.25, hi[i] - 0.25, 25)
        rows = []
        for L in levels:
            o = outline(T, axis, float(L))
            rows.append([round(float(L), 4), o])
        d["sections_" + axis] = {"uv": {"x": "(y,z)", "y": "(z,x)", "z": "(x,y)"}[axis],
                                 "rows": rows}
    return d


if __name__ == "__main__":
    names = sys.argv[1:] or ["top_head_shell", "bottom_head_shell", "face_part"]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    out = {"$what": "envelope survey (section extents) of the head shells — calipers on a published artifact",
           "$generated_by": "tools/own_measure_headshells.py", "units": "mm",
           "parts": {n: survey(n) for n in names}}
    json.dump(out, open(OUT, "w"), indent=1)
    print("wrote", OUT)
    for n, d in out["parts"].items():
        print(n, d["bbox_size"], d["triangles"], "tris")
