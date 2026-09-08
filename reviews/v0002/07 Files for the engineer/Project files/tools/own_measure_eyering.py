"""Caliper pass on the eye bezel: radial profile of noenoeil.stl.

Kernel-free (FreeCAD python, numpy). Writes out/own/measure/eye-ring.json.
Every number here is a CALIPER READING on a published artifact — ordinary
reverse engineering — and the rebuilt part.py quotes them by probe name.
"""
import json, os, sys
sys.path.insert(0, "/Users/leifrydenfalk/dev/ce-workshop/ce-cad")
import numpy as np
from cecad import meshslice

REF = "reference/pollen-microduck-rl/assets/noenoeil.stl"
T = meshslice.load(REF, 1000.0)
P = T.reshape(-1, 3)
out = {"mesh": REF, "units": "mm",
       "bbox": {"min": P.min(0).round(4).tolist(), "max": P.max(0).round(4).tolist(),
                "size": (P.max(0) - P.min(0)).round(4).tolist()}}

# axis is y; ring centre (x,z) = (0,20) per the fitted boss.
CX, CZ = 0.0, 20.0
# A: outer and inner radius as a function of y, from a radial ray cast in the
# x direction at z = CZ (the ring's own equator), both signs.
rows = []
ys = np.arange(-63.4, -53.9, 0.1)
for y in ys:
    iv = meshslice.intervals(T, "x", float(y), CZ)     # material along x at (y,z)
    rows.append([round(float(y), 3), [[round(a, 4), round(b, 4)] for a, b in iv]])
out["probe_A_radial_x_at_z20"] = {
    "what": "material along x at (y, z=20) every 0.1 mm of y — outer radius, wall, bore",
    "rows": rows}

# B: the same in z at x = CX (perpendicular ray) to confirm the ring is round
rows_b = []
for y in ys:
    iv = meshslice.intervals(T, "z", CX, float(y))     # careful: axis z, (u,v)=(x,y)
    rows_b.append([round(float(y), 3), [[round(a, 4), round(b, 4)] for a, b in iv]])
out["probe_B_radial_z_at_x0"] = {
    "what": "material along z at (x=0, y) every 0.1 mm of y",
    "rows": rows_b}

# C: axial extent of material along y at a set of radii (r from the axis, +x side)
rows_c = []
for r in [0.0, 4.0, 6.0, 7.0, 7.2, 7.4, 8.0, 9.0, 9.4, 9.5, 9.6, 10.0, 12.0, 14.0, 14.5, 14.9, 15.0]:
    iv = meshslice.intervals(T, "y", CZ, CX + r)   # axis y -> (u,v) = (z,x)
    rows_c.append([r, [[round(a, 4), round(b, 4)] for a, b in iv]])
out["probe_C_axial_y_by_radius"] = {
    "what": "material along y at x = r, z = 20 — the ring's axial faces at each radius",
    "rows": rows_c}

os.makedirs("out/own/measure", exist_ok=True)
json.dump(out, open("out/own/measure/eye-ring.json", "w"), indent=1)
print("wrote out/own/measure/eye-ring.json")
for k in ("probe_A_radial_x_at_z20",):
    for y, iv in out[k]["rows"][::5]:
        print(k, y, iv)
print("--- C ---")
for r, iv in out["probe_C_axial_y_by_radius"]["rows"]:
    print("r=", r, iv)
