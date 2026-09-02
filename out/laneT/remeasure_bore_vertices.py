#!/usr/bin/env python3
"""remeasure_bore_vertices.py — lane T fix pass, 2026-09-03.

The SKEPTIC's charge: the cradle bore was published as Ø14.9938–14.9978 and
the jaw flange as Ø11.9949. Both came from cecad.meshslice cross-section
circle fits whose point sets mix facet CORNERS (which lie on the design
cylinder) with points interpolated along facet EDGES (which lie inside it by
up to one sagitta). The same folder had already diagnosed and corrected that
artefact for its Ø16.8 relief and failed to apply it to its headline number.

This script measures the SAME surfaces off the mesh VERTICES only, fitting a
circle with its centre FREE (Kasa algebraic fit, then Gauss-Newton refine) so
nothing is assumed about where the axis is, and reports the residual of the
vertices to that fitted circle. A vertex residual of 0 means every vertex lies
exactly on one circle: that circle IS the design cylinder.

    ce-cad/bin/cad out/laneT/remeasure_bore_vertices.py
"""
import json, math, os, sys
sys.path.insert(0, "/Users/leifrydenfalk/dev/ce-workshop/ce-cad")
import numpy as np
from cecad import meshslice as ms

REPO = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck"
MS = os.path.join(REPO, "reference/pollen-microduck-rl/assets/motor_support.stl")
JAW = os.path.join(REPO, "reference/pollen-microduck-rl/assets/jaw.stl")


def verts(path):
    T = ms.load(path, scale=1000.0)
    return np.unique(np.round(T.reshape(-1, 3), 6), axis=0)


def fit_circle(P):
    """P: (n,2). Kasa algebraic fit then 20 Gauss-Newton steps on the
    geometric residual. Returns (cy, cz, r, resid_max, resid_rms)."""
    x, y = P[:, 0].astype(float), P[:, 1].astype(float)
    A = np.column_stack([x, y, np.ones_like(x)])
    b = x ** 2 + y ** 2
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    cx, cy = sol[0] / 2.0, sol[1] / 2.0
    r = math.sqrt(max(sol[2] + cx * cx + cy * cy, 0.0))
    for _ in range(40):
        dx, dy = x - cx, y - cy
        d = np.hypot(dx, dy)
        d = np.where(d == 0, 1e-12, d)
        J = np.column_stack([-dx / d, -dy / d, -np.ones_like(d)])
        res = d - r
        step, *_ = np.linalg.lstsq(J, -res, rcond=None)
        cx, cy, r = cx + step[0], cy + step[1], r + step[2]
        if np.max(np.abs(step)) < 1e-14:
            break
    d = np.hypot(x - cx, y - cy)
    return cx, cy, r, float(np.abs(d - r).max()), float(np.sqrt(((d - r) ** 2).mean()))


def band(V, xlo, xhi, rlo, rhi, cy0, cz0, label):
    r0 = np.hypot(V[:, 1] - cy0, V[:, 2] - cz0)
    m = (V[:, 0] > xlo) & (V[:, 0] < xhi) & (r0 > rlo) & (r0 < rhi)
    S = V[m]
    xs = sorted(set(np.round(S[:, 0], 4).tolist()))
    per = []
    for xv in xs:
        Q = S[np.abs(S[:, 0] - xv) < 1e-4][:, 1:3]
        Q = np.unique(np.round(Q, 6), axis=0)
        if len(Q) < 5:
            continue
        cy, cz, r, rmax, rrms = fit_circle(Q)
        ang = np.sort(np.degrees(np.arctan2(Q[:, 1] - cz, Q[:, 0] - cy)))
        dd = np.diff(ang); dd = dd[dd > 1e-9]
        per.append({
            "x_mm": round(float(xv), 4),
            "n_unique_vertices": int(len(Q)),
            "centre_yz_mm": [round(float(cy), 9), round(float(cz), 9)],
            "d_mm": round(float(2 * r), 8),
            "residual_max_mm": round(rmax, 8),
            "residual_rms_mm": round(rrms, 8),
            "arc_present_deg": round(float(ang[-1] - ang[0]), 4),
            "facet_step_deg": round(float(np.median(dd)), 4) if len(dd) else None,
        })
    return {"label": label, "x_window_mm": [xlo, xhi], "r_window_mm": [rlo, rhi],
            "stations": per,
            "d_mm_all_stations": sorted({p["d_mm"] for p in per}),
            "n_stations": len(per)}


def main():
    Vm, Vj = verts(MS), verts(JAW)
    out = {
        "$what": "the Ø15 cradle bore of motor_support.stl and the Ø10 journal / Ø12 flange "
                 "of jaw.stl, re-measured off MESH VERTICES with a free-centre circle fit "
                 "(Kasa + Gauss-Newton), 2026-09-03, lane T fix pass",
        "why": "cecad.meshslice cross-section fits mix facet corners with edge-interpolated "
               "points and read one half-sagitta small. The folder had already found that for "
               "its Ø16.8 relief and not applied it to the headline bore.",
        "method": "unique vertices of the binary STL (scale 1000), selected by x window and by "
                  "radius about a seed axis, then a circle fitted per x station with the centre "
                  "FREE. residual_max is the largest distance of any vertex from that circle.",
        "meshes": {"motor_support": os.path.relpath(MS, REPO), "jaw": os.path.relpath(JAW, REPO)},
        "cradle_bore": band(Vm, -39.9, -35.3, 7.40, 7.60, 0.0, 7.4995, "Ø15 cradle bore, both ring bands"),
        "cradle_relief": band(Vm, -37.6, -36.4, 8.30, 8.50, 0.0, 7.4995, "Ø16.8 relief between the bands"),
        "jaw_journal": band(Vj, -39.9, -36.9, 4.90, 5.10, 0.0, 7.5, "Ø10 jaw journal"),
        "cradle_outer": band(Vm, -39.9, -35.3, 8.50, 9.00, 0.0, 7.4995, "the outer surface of the arch"),
        "jaw_flange": band(Vj, -40.1, -39.6, 5.80, 6.20, 0.0, 7.5, "the flange behind the journal"),
    }
    d = os.path.join(REPO, "out/laneT")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "bore-vertex-remeasure.json")
    json.dump(out, open(p, "w"), indent=2)
    print("wrote", p)
    for k in ("cradle_bore", "cradle_relief", "cradle_outer", "jaw_journal", "jaw_flange"):
        b = out[k]
        print("\n==", b["label"], "==")
        for s in b["stations"]:
            print("  x %9.4f  n %3d  d %.6f  resid_max %.8f  rms %.8f  arc %.2f  step %s"
                  % (s["x_mm"], s["n_unique_vertices"], s["d_mm"], s["residual_max_mm"],
                     s["residual_rms_mm"], s["arc_present_deg"], s["facet_step_deg"]))
            print("       centre", s["centre_yz_mm"])


main()
