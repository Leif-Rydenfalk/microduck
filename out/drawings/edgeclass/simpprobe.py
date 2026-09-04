"""How much does simplify_chains buy, and what does it cost in deviation?"""
import sys, os, json, math, time
os.environ.setdefault("CE_TRIAD_ROOT", "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck:/Users/leifrydenfalk/dev/ce-workshop")
OUT = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck/out/drawings/edgeclass"
LOG = open(os.path.join(OUT, "simplify-tradeoff.log"), "w", buffering=1)
def L(*a): LOG.write(" ".join(str(x) for x in a) + "\n")
import FreeCAD as App
from cecad import triad, drawing as D, edgeclass as EC

def segs(prims):
    out = []
    for p in prims:
        if p["k"] == "line":
            out.append((p["p1"], p["p2"]))
        elif p["k"] in ("arc", "circle"):
            c = p["c"]; r = p["r"]
            a0, a1 = (0.0, 360.0) if p["k"] == "circle" else (p["a0"], (p["a1"] - p["a0"]) % 360.0 + p["a0"])
            n = max(8, int(abs(a1 - a0) / 5.0))
            pts = [(c[0] + r*math.cos(math.radians(a0 + (a1-a0)*i/n)), c[1] + r*math.sin(math.radians(a0 + (a1-a0)*i/n))) for i in range(n+1)]
            out += list(zip(pts, pts[1:]))
    return out

def maxdev(a_prims, b_prims):
    """worst distance from a sampled point of a_prims to the nearest segment of b_prims"""
    B = segs(b_prims)
    if not B: return None
    worst = 0.0
    for p1, p2 in segs(a_prims):
        for t in (0.0, 0.25, 0.5, 0.75, 1.0):
            q = (p1[0]+t*(p2[0]-p1[0]), p1[1]+t*(p2[1]-p1[1]))
            worst = max(worst, min(EC._pt_seg(q, a, b) for a, b in B))
    return worst

res = {}
for slug, view in (("microduck-neck-plate", "right"), ("microduck-shin", "right"), ("microduck-foot-left", "top")):
    doc = App.newDocument("s_" + slug.replace("-", "_") + view)
    part = triad.load(doc, "part:" + slug)
    base, _, _ = EC.view_prims(part, view, hidden=False, simplify=0)
    row = {"simplify_0": len(base)}
    for tol in (0.005, 0.01, 0.02, 0.06):
        p, _, _ = EC.view_prims(part, view, hidden=False, simplify=tol)
        row["simplify_%g" % tol] = {"prims": len(p),
                                    "max_dev_mm": round(maxdev(p, base), 4),
                                    "max_dev_back_mm": round(maxdev(base, p), 4)}
    bef, _, _ = D.view_prims(part, view, hidden=False)
    row["before_unfiltered"] = len(bef)
    res["%s %s" % (slug, view)] = row
    L(slug, view, json.dumps(row))
    App.closeDocument(doc.Name)
json.dump(res, open(os.path.join(OUT, "simplify-tradeoff.json"), "w"), indent=1)
L("DONE")
