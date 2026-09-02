#!/usr/bin/env python3
"""measure_battery_bay.py — CLOSE FINDING 2 by measurement, not by argument.

The finding: Pollen's simulator ships the battery as `np_f970.stl`, but every
word Pollen writes about the product says NP-F550. Those are two different
Sony L-series packs and only one of them fits in a 25 cm robot.

This measures the bay, in Pollen's own trunk frame, off Pollen's own meshes:

  1. Reads `spec/mesh-placements.json` — the pos_mm + quat_wxyz the MJCF gives
     every mesh parented to body `trunk_base` — and puts each mesh into that
     frame (STL units are metres, so x1000).
  2. Takes the battery mesh's own axis-aligned box in ITS OWN frame as the
     pack envelope, and expresses every other trunk part in that frame.
  3. For each of the pack's three axes, finds the nearest neighbouring surface
     beyond each face, considering only points that lie inside the pack's
     footprint on the other two axes. That is the bay: the pack plus the gap
     that is actually there.
  4. Prints which published pack bodies fit that bay and which do not.

Everything is stdlib: a binary-STL reader and a quaternion. No FreeCAD needed.

Run:  python3 tools/measure_battery_bay.py [--json out/measure/battery-bay.json]
"""
import argparse
import json
import os
import struct

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MESHES = os.path.join(REPO, "reference", "pollen-microduck-simulator", "meshes")
PLACEMENTS = os.path.join(REPO, "spec", "mesh-placements.json")
BATTERY_MESH = "np_f970"          # Pollen's filename. The point of this tool.
PARENT_BODY = "trunk_base"

# Published bodies, all read 2026-09-02 from the same vendor's identically
# formatted spec table so the two are comparable. Sony's own product pages
# answered HTTP 403 to every fetch attempt from this machine.
CANDIDATES = {
    "NP-F550 (L-series slim)": {
        "mm": (70.80, 38.50, 21.00),
        "cite": "nextbatteries.com/products/sony-np-f550-battery, spec table "
                "'70.80 x 38.50 x 21.00mm', 7.4 V, 2000 mAh, Li-ion, $17.90 "
                "(fetched 2026-09-02)"},
    "NP-F970 (L-series tall)": {
        "mm": (70.85, 38.40, 58.56),
        "cite": "nextbatteries.com/products/sony-np-f970-battery, spec table "
                "'70.85 x 38.40 x 58.56mm', 7.4 V, 6600 mAh, Li-ion "
                "(fetched 2026-09-02)"},
}


def read_stl_mm(path):
    """Binary STL -> list of (x, y, z) in mm. Refuses an ASCII/short file."""
    size = os.path.getsize(path)
    with open(path, "rb") as fh:
        fh.read(80)
        n = struct.unpack("<I", fh.read(4))[0]
        if 84 + n * 50 != size:
            raise SystemExit("%s is not a binary STL of %d triangles "
                             "(%d bytes)" % (path, n, size))
        out = []
        for _ in range(n):
            v = struct.unpack("<12fH", fh.read(50))
            for k in (3, 6, 9):
                out.append((v[k] * 1000.0, v[k + 1] * 1000.0, v[k + 2] * 1000.0))
    return out


def qmat(q):
    w, x, y, z = q
    return ((1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)),
            (2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)),
            (2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)))


def rot(M, p):
    return tuple(sum(M[i][j] * p[j] for j in range(3)) for i in range(3))


def rotT(M, p):
    return tuple(sum(M[j][i] * p[j] for j in range(3)) for i in range(3))


def bbox(pts):
    return [(min(p[i] for p in pts), max(p[i] for p in pts)) for i in range(3)]


def measure():
    P = json.load(open(PLACEMENTS))
    bp = P[BATTERY_MESH][0]
    if bp.get("body") != PARENT_BODY:
        raise SystemExit("%s is not parented to %s in the MJCF"
                         % (BATTERY_MESH, PARENT_BODY))
    Rb, tb = qmat(bp["quat_wxyz"]), bp["pos_mm"]

    def in_battery_frame(name, placement):
        R, t = qmat(placement["quat_wxyz"]), placement["pos_mm"]
        pts = read_stl_mm(os.path.join(MESHES, name + ".stl"))
        world = [tuple(rot(R, p)[k] + t[k] for k in range(3)) for p in pts]
        return [rotT(Rb, [p[k] - tb[k] for k in range(3)]) for p in world]

    bat = in_battery_frame(BATTERY_MESH, bp)
    bb = bbox(bat)
    ext = [round(hi - lo, 4) for lo, hi in bb]

    # every other trunk_base-parented mesh, in the battery's frame
    neigh = {}
    for name, pls in sorted(P.items()):
        if name == BATTERY_MESH:
            continue
        for pl in pls:
            if pl.get("body") != PARENT_BODY:
                continue
            if not os.path.exists(os.path.join(MESHES, name + ".stl")):
                continue
            neigh.setdefault(name, []).extend(in_battery_frame(name, pl))

    axes = ("pack_X_width", "pack_Y_depth", "pack_Z_length")
    bay = {}
    for a in range(3):
        other = [i for i in range(3) if i != a]
        lo, hi = bb[a]
        best = {"below": None, "above": None}
        for name, pts in neigh.items():
            sel = [p for p in pts
                   if all(bb[i][0] - 1.0 <= p[i] <= bb[i][1] + 1.0 for i in other)]
            if not sel:
                continue
            below = [p[a] for p in sel if p[a] < lo]
            above = [p[a] for p in sel if p[a] > hi]
            if below:
                g = lo - max(below)
                if best["below"] is None or g < best["below"]["gap_mm"]:
                    best["below"] = {"by": name, "gap_mm": round(g, 4)}
            if above:
                g = min(above) - hi
                if best["above"] is None or g < best["above"]["gap_mm"]:
                    best["above"] = {"by": name, "gap_mm": round(g, 4)}
        gb = best["below"]["gap_mm"] if best["below"] else None
        ga = best["above"]["gap_mm"] if best["above"] else None
        bay[axes[a]] = {
            "pack_mm": ext[a],
            "bounded_below_by": best["below"],
            "bounded_above_by": best["above"],
            "bay_mm": None if gb is None or ga is None else round(ext[a] + gb + ga, 4),
            "open": gb is None or ga is None,
        }

    bay_dims = sorted(v["bay_mm"] for v in bay.values() if v["bay_mm"] is not None)
    fits = {}
    for name, c in CANDIDATES.items():
        body = sorted(c["mm"])
        ok = len(bay_dims) == 3 and all(b <= d for b, d in zip(body, bay_dims))
        worst = None
        if len(bay_dims) == 3:
            worst = round(max(b - d for b, d in zip(body, bay_dims)), 4)
        fits[name] = {"body_mm_sorted": body, "fits": ok,
                      "worst_interference_mm": worst, "cite": c["cite"]}

    return {
        "$about": "MEASURED by tools/measure_battery_bay.py, %s. Every number "
                  "is read off Pollen's own meshes placed by Pollen's own MJCF "
                  "transforms; nothing here is a vendor claim except the "
                  "CANDIDATES table, which is cited per row." % "2026-09-02",
        "battery_mesh": {
            "file": os.path.relpath(os.path.join(MESHES, BATTERY_MESH + ".stl"), REPO),
            "named": BATTERY_MESH,
            "measured_bbox_mm": {"X_width": ext[0], "Y_depth": ext[1], "Z_length": ext[2]},
            "placement": bp,
        },
        "bay": bay,
        "bay_sorted_mm": bay_dims,
        "candidates": fits,
        "verdict": ("the mesh named np_f970 has an NP-F550 body and the bay it "
                    "sits in accepts only an NP-F550-class pack"
                    if fits["NP-F550 (L-series slim)"]["fits"]
                    and not fits["NP-F970 (L-series tall)"]["fits"]
                    else "INCONCLUSIVE — read the numbers"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    a = ap.parse_args()
    m = measure()
    print(json.dumps(m, indent=1))
    if a.json:
        os.makedirs(os.path.dirname(os.path.abspath(a.json)), exist_ok=True)
        with open(a.json, "w") as fh:
            json.dump(m, fh, indent=1)
            fh.write("\n")
        print("wrote", a.json)


if __name__ == "__main__":
    main()
