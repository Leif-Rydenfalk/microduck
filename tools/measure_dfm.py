"""measure_dfm.py — the DFM measurement pass behind MANUFACTURING-PLAYBOOK.html.

    ce-cad/bin/cad tools/measure_dfm.py            # writes out/dfm/dfm.json

Two measurements, one run, for EVERY printed slug in out/print/stl_manifest.json:

A. MESH DFM (all 30 slugs, read off the binary STL that was actually sliced —
   out/print/stl/<material>/<slug>.stl).
   * area, closed-mesh signed volume, bbox, triangle count
   * OVERHANG, measured, in six axis-aligned build directions. For a downward
     facing facet with unit normal n and build-up direction u, d = -(n.u) and
     the facet's angle to the build plate is beta = acos(d).  beta = 90 deg is a
     vertical wall (d = 0); beta = 0 is a horizontal down-face (d = 1).
     Reported per direction: area fraction with beta < 45 deg, beta < 30 deg
     (Bambu Studio's default support threshold) and beta < 10 deg (a bridge or a
     floating island), plus the XY-projected area of the beta < 30 group in mm^2
     — that is the support-material proxy — and the build height / layer count.
     `best` is the direction with the least beta<30 area; ties on beta<45, then
     on height.  NOTHING here is a guess: it is the STL's own facet normals.
     ce-cad has no overhang tool (cecad.printed.printability says so in as many
     words: "It does not guess at overhangs"), so this is the measurement that
     was missing from docs/DFM.md.
   * WALL THICKNESS, measured by ray casting inside the mesh: from each sampled
     facet centroid, step eps along -n and shoot -n; the nearest hit on a facet
     whose normal opposes the ray is the local wall.  Reported as min / p1 / p5 /
     median over the sample, because the MINIMUM of a triangulated shell is
     almost always a knife-edge chamfer (docs/DFM.md says the same of
     inspect.thinnest_wall) and p5 is the honest "thin wall" figure.
     Sample size and seed are recorded so the number reproduces.

B. SOLID DFM (the parametric rebuilds only, loaded through
   cecad.triad.load("part:<slug>")): cecad.printed.printability (bed fit, two
   perimeter floor, filament), cecad.inspect.thinnest_wall_detail (exact),
   cecad.inspect.holes (diameter, axis, depth, through/blind) and
   cecad.inspect.radius_values.  A mesh-backed slug gets none of these and says
   so — a decimated mesh has no callable dimension.

Every field carries its own basis. No defaults are invented: a value that could
not be measured is null with a `reason`.
"""
import json
import math
import os
import struct
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("CE_TRIAD_ROOT", ROOT + ":" + os.path.dirname(os.path.dirname(ROOT)))

SAMPLE_N = 4000          # wall-thickness rays per part
SEED = 20260902
EPS = 1e-3               # mm, ray start offset off the surface
OPPOSE = 0.20            # min |cos| between ray and hit-facet normal to count as a wall

DIRS = {
    "+X": (1.0, 0.0, 0.0), "-X": (-1.0, 0.0, 0.0),
    "+Y": (0.0, 1.0, 0.0), "-Y": (0.0, -1.0, 0.0),
    "+Z": (0.0, 0.0, 1.0), "-Z": (0.0, 0.0, -1.0),
}


def read_stl(path):
    """binary STL -> (V (n,3,3) float64 mm, N (n,3) unit normals from geometry)."""
    with open(path, "rb") as fh:
        head = fh.read(84)
        n = struct.unpack("<I", head[80:84])[0]
        buf = fh.read(n * 50)
    if len(buf) != n * 50:
        raise ValueError("truncated STL %s: %d of %d bytes" % (path, len(buf), n * 50))
    a = np.frombuffer(buf, dtype=np.uint8).reshape(n, 50)
    f = a[:, :48].copy().view("<f4").reshape(n, 4, 3).astype(np.float64)
    V = f[:, 1:4, :]
    e1 = V[:, 1] - V[:, 0]
    e2 = V[:, 2] - V[:, 0]
    cr = np.cross(e1, e2)
    ln = np.linalg.norm(cr, axis=1)
    keep = ln > 1e-12
    V, cr, ln = V[keep], cr[keep], ln[keep]
    return V, cr / ln[:, None], ln * 0.5


def mesh_volume(V):
    """Signed volume of a closed triangulated shell, mm^3 (divergence theorem)."""
    a, b, c = V[:, 0], V[:, 1], V[:, 2]
    return float(np.abs(np.einsum("ij,ij->i", a, np.cross(b, c)).sum()) / 6.0)


def overhang(V, N, A, u):
    """Overhang and height for one build-up direction u. All measured."""
    u = np.asarray(u, dtype=np.float64)
    d = -(N @ u)                       # 1 = horizontal down-face, 0 = vertical wall
    tot = float(A.sum())
    out = {}
    for tag, beta in (("lt45", 45.0), ("lt30", 30.0), ("lt10", 10.0)):
        m = d > math.cos(math.radians(beta))
        out["area_" + tag + "_mm2"] = round(float(A[m].sum()), 4)
        out["frac_" + tag] = round(float(A[m].sum() / tot), 6) if tot else None
    m30 = d > math.cos(math.radians(30.0))
    # XY-projected (i.e. footprint) area of the unsupported group = support proxy
    out["projected_lt30_mm2"] = round(float((A[m30] * d[m30]).sum()), 4)
    h = V.reshape(-1, 3) @ u
    out["height_mm"] = round(float(h.max() - h.min()), 4)
    out["layers_at_0p2"] = int(math.ceil((h.max() - h.min()) / 0.2))
    out["total_area_mm2"] = round(tot, 4)
    return out


def wall_rays(V, N, A, n_rays=SAMPLE_N, seed=SEED):
    """Wall thickness by internal ray casting. Moller-Trumbore, chunked."""
    rng = np.random.default_rng(seed)
    nf = len(V)
    if nf == 0:
        return None
    w = A / A.sum()
    k = min(n_rays, nf * 4)
    idx = rng.choice(nf, size=k, replace=True, p=w)
    # a random barycentric point on each chosen facet, not just the centroid
    r1 = np.sqrt(rng.random(k))
    r2 = rng.random(k)
    a, b, c = V[idx, 0], V[idx, 1], V[idx, 2]
    P = (1 - r1)[:, None] * a + (r1 * (1 - r2))[:, None] * b + (r1 * r2)[:, None] * c
    D = -N[idx]
    O = P + D * EPS

    v0, v1, v2 = V[:, 0], V[:, 1], V[:, 2]
    e1, e2 = v1 - v0, v2 - v0
    best = np.full(k, np.inf)
    CH = max(1, int(1_500_000 // max(nf, 1)))
    for s in range(0, k, CH):
        o, d = O[s:s + CH], D[s:s + CH]
        pv = np.cross(d[:, None, :], e2[None, :, :])           # (m, nf, 3)
        det = np.einsum("fj,mfj->mf", e1, pv)
        ok = np.abs(det) > 1e-12
        inv = np.where(ok, 1.0 / np.where(ok, det, 1.0), 0.0)
        tv = o[:, None, :] - v0[None, :, :]
        uu = np.einsum("mfj,mfj->mf", tv, pv) * inv
        qv = np.cross(tv, e1[None, :, :])
        vv = np.einsum("mj,mfj->mf", d, qv) * inv
        tt = np.einsum("fj,mfj->mf", e2, qv) * inv
        hit = ok & (uu >= 0) & (vv >= 0) & (uu + vv <= 1) & (tt > EPS)
        # only count a facet that FACES the ray (a true opposite wall surface)
        cosine = d @ N.T                                        # (m, nf)
        hit &= cosine > OPPOSE
        tt = np.where(hit, tt, np.inf)
        best[s:s + CH] = tt.min(axis=1)
    fin = best[np.isfinite(best)] + EPS
    if fin.size == 0:
        return {"rays": int(k), "hits": 0, "reason": "no ray found an opposing surface"}
    return {
        "rays": int(k), "hits": int(fin.size),
        "min_mm": round(float(fin.min()), 4),
        "p1_mm": round(float(np.percentile(fin, 1)), 4),
        "p5_mm": round(float(np.percentile(fin, 5)), 4),
        "median_mm": round(float(np.percentile(fin, 50)), 4),
        "seed": SEED, "eps_mm": EPS, "oppose_cos": OPPOSE,
    }


def solid_dfm(slug):
    """Parametric part: what the kernel can measure that a mesh cannot."""
    import FreeCAD
    from cecad import triad, inspect as insp, printed
    doc = FreeCAD.newDocument("dfm_" + slug.replace("-", "_"))
    try:
        part = triad.load(doc, "part:" + slug)
    except Exception as e:
        return {"ok": False, "reason": "triad.load failed: %s" % e}
    out = {"ok": True}
    try:
        d = insp.thinnest_wall_detail(part)
        out["thinnest_wall"] = {k: (round(v, 4) if isinstance(v, float) else v)
                                for k, v in dict(d).items()} if d else None
    except Exception as e:
        out["thinnest_wall"] = {"reason": "thinnest_wall_detail raised: %s" % e}
    try:
        hs = []
        for h in insp.holes(part):
            d = h._asdict() if hasattr(h, "_asdict") else dict(vars(h))
            hs.append({k: (round(v, 4) if isinstance(v, float) else
                           ([round(float(x), 4) for x in v]
                            if isinstance(v, (tuple, list)) else v))
                       for k, v in d.items() if not k.startswith("_")})
        out["holes"] = hs
    except Exception as e:
        out["holes"] = {"reason": "inspect.holes raised: %s" % e}
    try:
        out["radii_mm"] = [round(float(r), 4) for r in insp.radius_values(part)]
    except Exception as e:
        out["radii_mm"] = {"reason": "inspect.radius_values raised: %s" % e}
    try:
        rep = printed.printability(part)
        out["printability"] = json.loads(json.dumps(rep, default=str))
    except Exception as e:
        out["printability"] = {"reason": "printability raised: %s" % e}
    try:
        FreeCAD.closeDocument(doc.Name)
    except Exception:
        pass
    return out


def main():
    man = json.load(open(os.path.join(ROOT, "out/print/stl_manifest.json")))
    sl = {p["slug"]: p for p in json.load(open(os.path.join(ROOT, "out/print/slice.json")))["parts"]}
    res = {
        "$comment": (
            "DFM measured 2026-09-02 by tools/measure_dfm.py under ce-cad/bin/cad. "
            "Mesh block: read off the exact binary STL that ce-slice sliced. Overhang "
            "is facet-normal geometry, not an estimate; beta is the facet's angle to "
            "the build plate, beta<30 deg is BambuStudio's default support threshold. "
            "Wall is internal ray casting, min/p1/p5/median over a seeded sample; the "
            "MIN of a triangulated shell is usually a chamfer knife-edge, p5 is the "
            "honest wall. Solid block: cecad on the parametric rebuild only."),
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sample_rays": SAMPLE_N, "seed": SEED,
        "parts": {},
    }
    for slug, m in sorted(man.items()):
        p = os.path.join(ROOT, m["stl"])
        rec = {"material": m["material"], "qty": m["qty"], "stl": m["stl"],
               "stl_source": m["stl_source"], "mesh": m.get("mesh"),
               "orientation_rule_sliced": m.get("orientation_rule"),
               "parametric": m["stl_source"].startswith("our parametric")}
        if slug in sl:
            s = sl[slug]
            rec["sliced"] = {k: s[k] for k in
                             ("grams_per_piece", "seconds_per_piece", "grams_total",
                              "seconds_total", "layer_mm", "machine_preset",
                              "process_preset", "filament_preset", "density",
                              "slicer_warning", "orientation") if k in s}
        V, N, A = read_stl(p)
        mn = V.reshape(-1, 3).min(axis=0)
        mx = V.reshape(-1, 3).max(axis=0)
        rec["mesh_dfm"] = {
            "triangles": int(len(V)),
            "bbox_mm": [round(float(x), 4) for x in (mx - mn)],
            "surface_area_mm2": round(float(A.sum()), 4),
            "closed_volume_mm3": round(mesh_volume(V), 4),
            "overhang_by_build_dir": {k: overhang(V, N, A, u) for k, u in DIRS.items()},
            "wall_rays": wall_rays(V, N, A),
        }
        oh = rec["mesh_dfm"]["overhang_by_build_dir"]
        best = sorted(oh.items(), key=lambda kv: (kv[1]["area_lt30_mm2"],
                                                  kv[1]["area_lt45_mm2"],
                                                  kv[1]["height_mm"]))[0]
        rec["mesh_dfm"]["best_build_dir"] = best[0]
        rec["mesh_dfm"]["best_lt30_frac"] = best[1]["frac_lt30"]
        res["parts"][slug] = rec
        print("mesh  %-40s tri=%-6d best=%s lt30=%.4f wall_p5=%s"
              % (slug, len(V), best[0], best[1]["frac_lt30"],
                 rec["mesh_dfm"]["wall_rays"].get("p5_mm")), flush=True)

    for slug, rec in res["parts"].items():
        if rec["parametric"]:
            t0 = time.time()
            rec["solid_dfm"] = solid_dfm(slug)
            print("solid %-40s %.1fs ok=%s" % (slug, time.time() - t0,
                                               rec["solid_dfm"].get("ok")), flush=True)
        else:
            rec["solid_dfm"] = {"ok": False, "reason":
                                "vendor mesh, not a parametric solid — a decimated mesh "
                                "has no callable dimension (out/drawings/INDEX.md)"}

    outp = os.path.join(ROOT, "out/dfm/dfm.json")
    os.makedirs(os.path.dirname(outp), exist_ok=True)
    json.dump(res, open(outp, "w"), indent=1)
    print("wrote", outp, os.path.getsize(outp), "bytes")


main()
