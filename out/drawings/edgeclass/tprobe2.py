"""Time EVERY step of EC.view_prims for one view, logging live to a file."""
import sys, os, json, time
os.environ.setdefault("CE_TRIAD_ROOT", "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck:/Users/leifrydenfalk/dev/ce-workshop")
LOG = open("/private/tmp/sheet-edgeclass/tprobe2.log", "w", buffering=1)
def L(*a): LOG.write(" ".join(str(x) for x in a) + "\n")
import FreeCAD as App, Part as P, TechDraw
from FreeCAD import Vector as V
from cecad import triad, drawing as D, edgeclass as EC
slug, view = sys.argv[1], sys.argv[2]
doc = App.newDocument("t2")
t = time.time(); part = triad.load(doc, "part:" + slug); L("load", round(time.time()-t,2))
sh = getattr(part, "shape", None) or part.Shape
t = time.time(); cl = EC.classify(sh, look=D.view_basis(view)[2]); L("classify", round(time.time()-t,2), json.dumps(cl["counts"]))
keep = [r["i"] for r in cl["rows"] if r["cls"] in EC.KEEP]; L("keep", len(keep))
t = time.time()
s = sh.copy(); s.Placement = App.Placement(V(0,0,0), D._view_rotation(view)).multiply(s.Placement)
L("rotate", round(time.time()-t,2))
t = time.time(); g, nseg = EC._keep_grid(s, keep, EC.model_to2d)
L("keep_grid", round(time.time()-t,2), "segments", nseg, "cells", len(g.g), "max per cell", max(len(v) for v in g.g.values()) if g.g else 0,
  "total insertions", sum(len(v) for v in g.g.values()))
t = time.time(); res = TechDraw.projectEx(s, V(0,0,-1)); L("hlr", round(time.time()-t,2))
def ce(i):
    c = res[i] if i < len(res) else None
    if c is None: return []
    try: return list(c.Edges)
    except Exception: return []
to2d = D.projected_to2d()
for idx, nm in ((0,"V"),(5,"H")):
    es = ce(idx); t = time.time(); kept = 0; dropped = 0
    for e in es:
        pts = EC._samples_of(e, to2d)
        if pts and all(g.near(p, EC.MATCH_TOL) <= EC.MATCH_TOL for p in pts): kept += 1
        else: dropped += 1
    L("filter", nm, len(es), round(time.time()-t,2), "kept", kept, "dropped", dropped)
L("DONE")
