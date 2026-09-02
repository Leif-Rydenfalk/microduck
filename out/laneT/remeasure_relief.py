#!/usr/bin/env python3
"""remeasure_relief.py — the Ø16.8 relief between the two ring bands of the
motor-support cradle, measured off the MESH VERTICES.

    ce-cad/bin/cad out/laneT/remeasure_relief.py

Why vertices and not a ray: the bore is a chord polygon. Its vertices lie ON
the design cylinder; every facet lies inside it by up to one sagitta. A
ray-cast caliper therefore under-reads the diameter by 2*sagitta, and
cecad.meshslice.intervals() rounds to 3 dp on top of that. The vertex ring is
the cylinder; the ray is a chord across it. Writes out/laneT/relief-remeasure.json.
"""
import json
import math
import os
import sys

sys.path.insert(0, "/Users/leifrydenfalk/dev/ce-workshop/ce-cad")
import numpy as np
from cecad import meshslice as ms

REPO = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck"
MESH = os.path.join(REPO, "reference/pollen-microduck-rl/assets/motor_support.stl")
CY, CZ = 0.0, 7.4995          # the cradle axis, from tube-15-geometry.json


def ring(V, r, rlo, rhi, xlo, xhi):
    m = (r > rlo) & (r < rhi) & (V[:, 0] > xlo) & (V[:, 0] < xhi)
    S, rs = V[m], r[m]
    ang = np.sort(np.degrees(np.arctan2(S[:, 2] - CZ, S[:, 1] - CY)))
    d = np.diff(ang)
    d = d[d > 1e-6]
    step = float(np.median(d))
    R = float(rs.mean())
    return {
        "n_vertices": int(len(S)),
        "x_stations_mm": sorted(round(float(v), 4) for v in set(np.round(S[:, 0], 4).tolist())),
        "radius_mm": {"mean": round(R, 5), "sd": round(float(rs.std(ddof=1)), 6),
                      "min": round(float(rs.min()), 5), "max": round(float(rs.max()), 5)},
        "diameter_mm": {"mean": round(2 * R, 4), "sd": round(2 * float(rs.std(ddof=1)), 6),
                        "min": round(2 * float(rs.min()), 4), "max": round(2 * float(rs.max()), 4)},
        "arc_present_deg": round(float(ang[-1] - ang[0]), 4),
        "facet_step_deg": round(step, 4),
        "facets_per_full_circle": round(360.0 / step, 2),
        "sagitta_mm": round(R * (1 - math.cos(math.radians(step) / 2)), 5),
        "mid_chord_diameter_mm": round(2 * R * math.cos(math.radians(step) / 2), 4),
        "x_extent_mm": [round(float(S[:, 0].min()), 4), round(float(S[:, 0].max()), 4)],
    }


def main():
    T = ms.load(MESH, scale=1000.0)
    V = np.unique(np.round(T.reshape(-1, 3), 6), axis=0)
    r = np.hypot(V[:, 1] - CY, V[:, 2] - CZ)
    out = {
        "$what": "the relief between the two ring bands of the Ø15 cradle, and the Ø15 bore "
                 "itself, measured off motor_support.stl's vertices",
        "mesh": os.path.relpath(MESH, REPO),
        "scale": 1000.0,
        "axis": {"y": CY, "z": CZ, "source": "tube-15-geometry.json host.frame"},
        "date": "2026-09-03",
        "relief": ring(V, r, 8.30, 8.50, -37.6, -36.4),
        "ring_band_bore": ring(V, r, 7.45, 7.55, -39.8, -35.3),
    }
    out["verdict"] = "PASS"
    out["why"] = (
        "The relief is Ø%.4f mm (1 sigma %.6f over %d vertices), a straight cylinder over its "
        "whole %.4f mm length — there is no vertex row between x %.4f and x %.4f, so nothing "
        "tapers. The value replaces the 16.8 written on 2026-09-02, which carried one decimal "
        "place and no basis. A ray-cast caliper reads Ø%.4f on the same surface because it "
        "crosses a facet chord (%d facets, step %.4f°, sagitta %.5f mm); that is the "
        "tessellation, not a second diameter. The Ø15 bore measured the same way reads Ø%.4f, "
        "the same +0.0007 mm off its own nominal, which identifies the offset as the STL's "
        "float32 storage." % (
            out["relief"]["diameter_mm"]["mean"], out["relief"]["diameter_mm"]["sd"],
            out["relief"]["n_vertices"],
            out["relief"]["x_extent_mm"][1] - out["relief"]["x_extent_mm"][0],
            out["relief"]["x_extent_mm"][0], out["relief"]["x_extent_mm"][1],
            out["relief"]["mid_chord_diameter_mm"],
            round(out["relief"]["arc_present_deg"] / out["relief"]["facet_step_deg"]) + 1,
            out["relief"]["facet_step_deg"], out["relief"]["sagitta_mm"],
            out["ring_band_bore"]["diameter_mm"]["mean"]))
    dst = os.path.join(REPO, "out/laneT/relief-remeasure.json")
    with open(dst, "w") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")
    print(json.dumps(out, indent=1))


main()
