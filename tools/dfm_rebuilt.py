"""dfm_rebuilt.py — DFM pass over EVERY rebuilt (origin=generated, PASS) part.

    ce-cad/bin/cad tools/dfm_rebuilt.py [slug ...]   -> out/dfm/dfm-rebuilt.json

For each part, from the PARAMETRIC SOLID (not a vendor mesh):
  * cecad.printed.printability   — bed fit, upright, thinnest wall vs 2 perimeters, filament
  * cecad.dfm.measure(slice=False) — figures + verdict roll-up
  * cecad.machining.plan          — subtractive plan (expect CANNOT DETERMINE)
  * cecad.inspect.thinnest_wall_detail / holes / radius_values
  * OVERHANG, measured off this solid's own tessellation, in six axis-aligned
    build directions. ce-cad has no overhang tool (printability says so in as
    many words), so it is computed here from facet normals: for a facet with
    unit normal n and build-up direction u, d = -(n.u), beta = acos(d) is the
    facet's angle to the build plate. beta<30 deg is BambuStudio's default
    support threshold; beta<10 deg is a bridge / floating island.
Nothing is invented. A value that could not be measured is null with a reason.
"""
import json, math, os, struct, sys, time
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("CE_TRIAD_ROOT",
                      ROOT + ":" + os.path.dirname(os.path.dirname(ROOT)))

DIRS = {"+X": (1.,0.,0.), "-X": (-1.,0.,0.), "+Y": (0.,1.,0.),
        "-Y": (0.,-1.,0.), "+Z": (0.,0.,1.), "-Z": (0.,0.,-1.)}
SAMPLE_N, SEED, EPS, OPPOSE = 4000, 20260902, 1e-3, 0.20
LAYER = 0.2


def read_stl(path):
    with open(path, "rb") as fh:
        n = struct.unpack("<I", fh.read(84)[80:84])[0]
        buf = fh.read(n * 50)
    if len(buf) != n * 50:
        raise ValueError("truncated STL %s" % path)
    a = np.frombuffer(buf, dtype=np.uint8).reshape(n, 50)
    f = a[:, :48].copy().view("<f4").reshape(n, 4, 3).astype(np.float64)
    V = f[:, 1:4, :]
    cr = np.cross(V[:,1]-V[:,0], V[:,2]-V[:,0])
    ln = np.linalg.norm(cr, axis=1)
    keep = ln > 1e-12
    V, cr, ln = V[keep], cr[keep], ln[keep]
    return V, cr / ln[:, None], ln * 0.5


def overhang(V, N, A, u):
    u = np.asarray(u, dtype=np.float64)
    d = -(N @ u)
    tot = float(A.sum())
    out = {}
    for tag, beta in (("lt45", 45.), ("lt30", 30.), ("lt10", 10.)):
        m = d > math.cos(math.radians(beta))
        out["area_"+tag+"_mm2"] = round(float(A[m].sum()), 4)
        out["frac_"+tag] = round(float(A[m].sum()/tot), 6) if tot else None
    m30 = d > math.cos(math.radians(30.))
    out["projected_lt30_mm2"] = round(float((A[m30]*d[m30]).sum()), 4)
    h = V.reshape(-1,3) @ u
    out["height_mm"] = round(float(h.max()-h.min()), 4)
    out["layers_at_0p2"] = int(math.ceil((h.max()-h.min())/LAYER))
    out["total_area_mm2"] = round(tot, 4)
    return out


def wall_rays(V, N, A, n_rays=SAMPLE_N, seed=SEED):
    rng = np.random.default_rng(seed)
    nf = len(V)
    if nf == 0:
        return None
    w = A / A.sum()
    k = min(n_rays, nf*4)
    idx = rng.choice(nf, size=k, replace=True, p=w)
    r1 = np.sqrt(rng.random(k)); r2 = rng.random(k)
    a, b, c = V[idx,0], V[idx,1], V[idx,2]
    P = (1-r1)[:,None]*a + (r1*(1-r2))[:,None]*b + (r1*r2)[:,None]*c
    D = -N[idx]; O = P + D*EPS
    v0, v1, v2 = V[:,0], V[:,1], V[:,2]
    e1, e2 = v1-v0, v2-v0
    best = np.full(k, np.inf)
    CH = max(1, int(1_200_000 // max(nf, 1)))
    for s in range(0, k, CH):
        o, d = O[s:s+CH], D[s:s+CH]
        pv = np.cross(d[:,None,:], e2[None,:,:])
        det = np.einsum("fj,mfj->mf", e1, pv)
        ok = np.abs(det) > 1e-12
        inv = np.where(ok, 1.0/np.where(ok, det, 1.0), 0.0)
        tv = o[:,None,:] - v0[None,:,:]
        uu = np.einsum("mfj,mfj->mf", tv, pv)*inv
        qv = np.cross(tv, e1[None,:,:])
        vv = np.einsum("mj,mfj->mf", d, qv)*inv
        tt = np.einsum("fj,mfj->mf", e2, qv)*inv
        hit = ok & (uu>=0) & (vv>=0) & (uu+vv<=1) & (tt>EPS)
        hit &= (d @ N.T) > OPPOSE
        best[s:s+CH] = np.where(hit, tt, np.inf).min(axis=1)
    fin = best[np.isfinite(best)] + EPS
    if fin.size == 0:
        return {"rays": int(k), "hits": 0,
                "reason": "no ray found an opposing surface"}
    return {"rays": int(k), "hits": int(fin.size),
            "min_mm": round(float(fin.min()), 4),
            "p1_mm": round(float(np.percentile(fin,1)), 4),
            "p5_mm": round(float(np.percentile(fin,5)), 4),
            "median_mm": round(float(np.percentile(fin,50)), 4),
            "seed": SEED, "eps_mm": EPS, "oppose_cos": OPPOSE}


def _j(v):
    if isinstance(v, float): return round(v, 4)
    if isinstance(v, (int, bool, str)) or v is None: return v
    if isinstance(v, (tuple, list)): return [_j(x) for x in v]
    if isinstance(v, dict): return {str(k): _j(x) for k, x in v.items()}
    try: return round(float(v), 4)
    except Exception: return str(v)


def generated_pass_slugs():
    out = []
    base = os.path.join(ROOT, "ce-parts")
    for d in sorted(os.listdir(base)):
        f = os.path.join(base, d, "component.json")
        if not os.path.exists(f): continue
        r = json.load(open(f)).get("record", {})
        if r.get("origin") == "generated" and r.get("verdict") == "PASS":
            out.append((d, r.get("material"), r.get("process"), r.get("title","")))
    return out


def one(slug, material):
    import FreeCAD
    from cecad import triad, inspect as insp, printed, dfm, machining
    rec = {"slug": slug, "declared_material": material}
    doc = FreeCAD.newDocument("dfm_" + slug.replace("-", "_"))
    try:
        part = triad.load(doc, "part:" + slug)
    except Exception as e:
        return {**rec, "ok": False, "reason": "triad.load failed: %s" % e}
    rec["ok"] = True
    rec["part_material"] = str(getattr(part, "material", "") or "")
    try:
        ok_p, info = printed.printability(part, verbose=False)
        rec["printability"] = json.loads(json.dumps(_j(info), default=str))
        rec["printability"]["ok"] = bool(ok_p)
    except Exception as e:
        rec["printability"] = {"reason": "printability raised: %s" % e}
    try:
        d = insp.thinnest_wall_detail(part)
        rec["thinnest_wall_detail"] = _j(dict(d)) if d else None
    except Exception as e:
        rec["thinnest_wall_detail"] = {"reason": "raised: %s" % e}
    try:
        hs = []
        for h in insp.holes(part):
            hd = h._asdict() if hasattr(h, "_asdict") else dict(vars(h))
            hs.append({k: _j(v) for k, v in hd.items() if not k.startswith("_")})
        rec["holes"] = hs
    except Exception as e:
        rec["holes"] = {"reason": "inspect.holes raised: %s" % e}
    try:
        rec["radii_mm"] = sorted({round(float(r), 4) for r in insp.radius_values(part)})
    except Exception as e:
        rec["radii_mm"] = {"reason": "raised: %s" % e}
    # machining
    try:
        pl = machining.plan(part, verbose=False)
        rec["machining"] = {"verdict": _j(getattr(pl, "verdict", None)),
                            "process": (getattr(pl.process, "slug", None)
                                        if getattr(pl, "process", None) else None),
                            "why": _j(getattr(pl, "why", None)),
                            "setups": len(getattr(pl, "setups", []) or []),
                            "minutes": _j(getattr(pl, "minutes", None)),
                            "fails": [_j(f.rule) + " — " + _j(f.detail)
                                      for f in (getattr(pl, "fails", []) or [])]}
    except Exception as e:
        rec["machining"] = {"reason": "machining.plan raised: %s" % e}
    # dfm.measure — no slicer (slice=False), the farm's slicer is the authority
    try:
        m = dfm.measure(part, slice=False, verbose=False)
        rec["dfm_measure"] = {"verdicts": _j(m.get("verdicts")),
                              "notes": _j(m.get("notes")),
                              "figures": {k: _j(v) for k, v in m["figures"].items()}}
    except Exception as e:
        rec["dfm_measure"] = {"reason": "dfm.measure raised: %s" % e}
    # overhang / wall, off this solid's own tessellation
    stl = os.path.join(ROOT, "out/dfm/stl-rebuilt", slug + ".stl")
    os.makedirs(os.path.dirname(stl), exist_ok=True)
    try:
        part.export_stl(stl)
        V, N, A = read_stl(stl)
        mn = V.reshape(-1,3).min(axis=0); mx = V.reshape(-1,3).max(axis=0)
        oh = {k: overhang(V, N, A, u) for k, u in DIRS.items()}
        best = sorted(oh.items(), key=lambda kv: (kv[1]["area_lt30_mm2"],
                                                  kv[1]["area_lt45_mm2"],
                                                  kv[1]["height_mm"]))[0]
        rec["mesh"] = {"stl": os.path.relpath(stl, ROOT),
                       "triangles": int(len(V)),
                       "bbox_mm": [round(float(x), 4) for x in (mx-mn)],
                       "surface_area_mm2": round(float(A.sum()), 4),
                       "overhang_by_build_dir": oh,
                       "best_build_dir": best[0],
                       "best_lt30_frac": best[1]["frac_lt30"],
                       "best_lt30_mm2": best[1]["area_lt30_mm2"],
                       "best_lt10_frac": best[1]["frac_lt10"],
                       "best_height_mm": best[1]["height_mm"],
                       "best_layers": best[1]["layers_at_0p2"],
                       "z_up_lt30_frac": oh["+Z"]["frac_lt30"],
                       "z_up_layers": oh["+Z"]["layers_at_0p2"],
                       "wall_rays": wall_rays(V, N, A)}
    except Exception as e:
        rec["mesh"] = {"reason": "tessellation/overhang failed: %s" % e}
    try:
        FreeCAD.closeDocument(doc.Name)
    except Exception:
        pass
    return rec


def main():
    want = [a for a in sys.argv[1:] if not a.startswith("-")]
    slugs = generated_pass_slugs()
    if want:
        slugs = [s for s in slugs if s[0] in want or s[0].replace("microduck-","") in want]
    res = {"$comment": (
        "DFM over every rebuilt part (component.json record.origin=generated, "
        "verdict=PASS). Solid block: cecad on the parametric rebuild loaded by "
        "cecad.triad.load. Mesh block: this solid's own tessellation — overhang "
        "is facet-normal geometry (beta = angle of a down-facing facet to the "
        "build plate; beta<30 deg is BambuStudio's default support threshold), "
        "wall is internal ray casting reported as min/p1/p5/median because the "
        "MIN of a triangulated shell is usually a chamfer knife-edge. Slicer "
        "NOT asked (slice=False): the print farm's slicer is the authority on "
        "grams and seconds."),
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "bed": "prusa_mk4 250x210x220", "nozzle_mm": 0.4, "layer_mm": LAYER,
        "two_perimeter_min_mm": 0.8, "sample_rays": SAMPLE_N, "seed": SEED,
        "parts": {}}
    for slug, mat, proc, title in slugs:
        t0 = time.time()
        r = one(slug, mat)
        r["declared_process"] = proc
        r["title"] = title
        res["parts"][slug] = r
        pr = r.get("printability") or {}
        me = r.get("mesh") or {}
        print("%-40s %5.1fs fits=%s wall=%s best=%s lt30=%s p5=%s mach=%s"
              % (slug, time.time()-t0, pr.get("fits"), pr.get("thinnest_wall"),
                 me.get("best_build_dir"), me.get("best_lt30_frac"),
                 (me.get("wall_rays") or {}).get("p5_mm"),
                 (r.get("machining") or {}).get("verdict")), flush=True)
    outp = os.path.join(ROOT, "out/dfm/dfm-rebuilt.json")
    os.makedirs(os.path.dirname(outp), exist_ok=True)
    json.dump(res, open(outp, "w"), indent=1)
    print("wrote", outp, os.path.getsize(outp), "bytes")


main()
