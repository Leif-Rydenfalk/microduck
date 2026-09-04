"""Measure what feeds the projector and what the 9543 lines are made of."""
import sys, os, json, math, time
os.environ.setdefault("CE_TRIAD_ROOT", "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck:/Users/leifrydenfalk/dev/ce-workshop")
import FreeCAD as App, Part, TechDraw
from FreeCAD import Vector as V
from cecad import triad
from cecad.drawing import _view_rotation, projected_to2d, edge_prims, refit_arcs, drop_coincident_hidden

slug = sys.argv[1]
views = sys.argv[2:] or ["front", "top", "right"]
doc = App.newDocument("p_" + slug.replace("-", "_"))
part = triad.load(doc, "part:" + slug)
shape = getattr(part, "shape", None) or part.Shape
print("faces", len(shape.Faces), "edges", len(shape.Edges), "solids", len(shape.Solids), flush=True)
print("TechDraw", [n for n in dir(TechDraw) if not n.startswith("_")], flush=True)
print("Part regularity fns", [n for n in dir(Part) if 'egular' in n or 'ontinu' in n], [n for n in dir(shape) if 'egular' in n or 'ontinu' in n], flush=True)

# --- 3D edge classification by dihedral angle ---
def face_normal(f, p):
    u, v = f.Surface.parameter(p)
    n = f.normalAt(u, v)
    return n
edge_faces = {}
for i, f in enumerate(shape.Faces):
    for e in f.Edges:
        edge_faces.setdefault(e.hashCode(), []).append(i)
cls = {}
angles = []
for k, e in enumerate(shape.Edges):
    fs = edge_faces.get(e.hashCode(), [])
    if e.Length < 1e-6:
        cls[k] = ("DEGENERATE", 0.0); continue
    if len(fs) < 2:
        cls[k] = ("FREE" if len(fs) < 2 else "MULTI", 0.0); continue
    f1, f2 = shape.Faces[fs[0]], shape.Faces[fs[1]]
    amax = 0.0
    for t in (0.25, 0.5, 0.75):
        p = e.valueAt(e.FirstParameter + t * (e.LastParameter - e.FirstParameter))
        try:
            n1, n2 = face_normal(f1, p), face_normal(f2, p)
            c = max(-1.0, min(1.0, n1.dot(n2)))
            a = math.degrees(math.acos(c))
        except Exception:
            a = 999.0
        amax = max(amax, a)
    angles.append(amax)
    cls[k] = ("ANGLE", amax)
bins = [0, 0.01, 0.1, 0.5, 1, 2, 3, 5, 7, 10, 15, 20, 30, 45, 60, 90, 120, 180.1]
hist = {}
for a in angles:
    for lo, hi in zip(bins, bins[1:]):
        if lo <= a < hi:
            hist["%g-%g" % (lo, hi)] = hist.get("%g-%g" % (lo, hi), 0) + 1
            break
print("dihedral histogram (deg):", json.dumps(hist), flush=True)
nfree = sum(1 for v in cls.values() if v[0] == "FREE")
print("free/degenerate edges", nfree, sum(1 for v in cls.values() if v[0]=="DEGENERATE"), flush=True)

# --- HLR composition per view ---
names = ["V", "V1", "VN", "VO", "VI", "H", "H1", "HN", "HO", "HI"]
to2d = projected_to2d()
res_all = {}
for view in views:
    s = shape.copy()
    rot = _view_rotation(view)
    s.Placement = App.Placement(V(0, 0, 0), rot).multiply(s.Placement)
    t0 = time.time()
    res = TechDraw.projectEx(s, V(0, 0, -1))
    dt = time.time() - t0
    comp = {}
    for i, c in enumerate(res):
        n = 0; nl = 0
        if c is not None:
            try:
                es = c.Edges
            except Exception:
                es = []
            n = len(es)
            for e in es:
                nl += len(edge_prims(e, to2d, "X", 0.12))
        comp[names[i]] = {"edges": n, "prims": nl}
    # what view_prims produces (after refit + drop_coincident)
    vis = []; hid = []
    for i, c in enumerate(res):
        if c is None: continue
        try: es = c.Edges
        except Exception: continue
        (vis if i < 5 else hid).extend(es)
    vp = []
    for e in vis: vp += edge_prims(e, to2d, "VISIBLE", 0.12)
    vp = refit_arcs(vp)
    hp = []
    for e in hid: hp += edge_prims(e, to2d, "HIDDEN", 0.12)
    hp = drop_coincident_hidden(vp, refit_arcs(hp))
    comp["view_prims_visible"] = len(vp); comp["view_prims_hidden"] = len(hp)
    comp["hlr_seconds"] = round(dt, 2)
    res_all[view] = comp
    print(view, json.dumps(comp), flush=True)
json.dump({"slug": slug, "faces": len(shape.Faces), "edges": len(shape.Edges), "dihedral_hist": hist,
           "free_edges": nfree, "views": res_all},
          open("/private/tmp/sheet-edgeclass/probe1-%s.json" % slug, "w"), indent=1)
