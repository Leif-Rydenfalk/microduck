"""Before/after on one part with timing breakdown."""
import sys, os, json, time, math
os.environ.setdefault("CE_TRIAD_ROOT", "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck:/Users/leifrydenfalk/dev/ce-workshop")
import FreeCAD as App
from cecad import triad, drawing as D, edgeclass as EC

OUT = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck/out/drawings/edgeclass"
os.makedirs(OUT, exist_ok=True)
slug = sys.argv[1]
views = (sys.argv[2].split(",") if len(sys.argv) > 2 else ["front", "top", "right"])
selftest = os.environ.get("EC_SELFTEST", "1") == "1"

doc = App.newDocument("b_" + slug.replace("-", "_"))
part = triad.load(doc, "part:" + slug)
sh = getattr(part, "shape", None) or part.Shape
print(slug, "faces", len(sh.Faces), "edges", len(sh.Edges), flush=True)

t0 = time.time()
geom = EC.edge_geometry(sh)
print("edge_geometry: %.2f s for %d edges" % (time.time()-t0, len(geom)), flush=True)
cl = EC.classify(sh, look=D.view_basis("top")[2])
print("classify counts (top look):", json.dumps(cl["counts"]), "gap", json.dumps(cl["gap"]), flush=True)

def count(prims):
    c = {"line": 0, "circle": 0, "arc": 0}
    for p in prims: c[p["k"]] = c.get(p["k"], 0) + 1
    return c

def svg(prims, path, title):
    b = D.bbox(prims)
    if not b: b = (0, 0, 1, 1)
    w, h = max(b[2]-b[0], 1e-6), max(b[3]-b[1], 1e-6)
    pad = max(w, h)*0.06 + 2
    S = 1000.0/max(w, h)
    W, H = (w+2*pad)*S, (h+2*pad)*S + 34
    X = lambda x: (x-b[0]+pad)*S
    Y = lambda y: H-34-(y-b[1]+pad)*S
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%.0f" height="%.0f" viewBox="0 0 %.0f %.0f"><rect width="100%%" height="100%%" fill="#fff"/>' % (W, H, W, H)]
    for p in prims:
        hid = p.get("layer","") == "HIDDEN"
        st = ' stroke="#aaa" stroke-width="0.7" stroke-dasharray="4,3"' if hid else ' stroke="#111" stroke-width="1.2"'
        if p["k"] == "line":
            o.append('<line x1="%.3f" y1="%.3f" x2="%.3f" y2="%.3f"%s/>' % (X(p["p1"][0]),Y(p["p1"][1]),X(p["p2"][0]),Y(p["p2"][1]),st))
        elif p["k"] == "circle":
            o.append('<circle cx="%.3f" cy="%.3f" r="%.3f" fill="none"%s/>' % (X(p["c"][0]),Y(p["c"][1]),p["r"]*S,st))
        elif p["k"] == "arc":
            c=p["c"]; r=p["r"]; a0=math.radians(p["a0"]); a1=math.radians(p["a1"])
            x0,y0=c[0]+r*math.cos(a0),c[1]+r*math.sin(a0); x1,y1=c[0]+r*math.cos(a1),c[1]+r*math.sin(a1)
            sw=(p["a1"]-p["a0"])%360.0
            o.append('<path d="M %.3f %.3f A %.3f %.3f 0 %d 0 %.3f %.3f" fill="none"%s/>' % (X(x0),Y(y0),r*S,r*S,1 if sw>180 else 0,X(x1),Y(y1),st))
    o.append('<text x="10" y="%.0f" font-family="Helvetica" font-size="22" fill="#000">%s</text></svg>' % (H-9, title))
    open(path,"w").write("".join(o))

res = {"slug": slug, "faces": len(sh.Faces), "edges": len(sh.Edges),
       "classify_seconds": round(time.time()-t0, 2), "views": {}}
for view in views:
    r = {}
    t = time.time()
    before, nv, nh = D.view_prims(part, view, hidden=True)
    r["before"] = {"prims": len(before), "counts": count(before), "hlr_vis": nv, "hlr_hid": nh, "sec": round(time.time()-t,2)}
    svg(before, os.path.join(OUT, "%s-%s-before.svg" % (slug,view)), "%s  %s  BEFORE  %d prims" % (slug,view,len(before)))
    st = {}; t = time.time()
    after, _, _ = EC.view_prims(part, view, hidden=True, stats=st)
    r["after"] = {"prims": len(after), "counts": count(after), "sec": round(time.time()-t,2), "stats": st}
    svg(after, os.path.join(OUT, "%s-%s-after.svg" % (slug,view)), "%s  %s  AFTER  %d prims" % (slug,view,len(after)))
    # visible-only versions, which is what a shop reads
    vb, _, _ = D.view_prims(part, view, hidden=False)
    va, _, _ = EC.view_prims(part, view, hidden=False)
    r["visible_only"] = {"before": len(vb), "after": len(va)}
    svg(vb, os.path.join(OUT, "%s-%s-before-vis.svg" % (slug,view)), "%s  %s  BEFORE visible-only  %d prims" % (slug,view,len(vb)))
    svg(va, os.path.join(OUT, "%s-%s-after-vis.svg" % (slug,view)), "%s  %s  AFTER visible-only  %d prims" % (slug,view,len(va)))
    bb, ab = D.bbox(vb), D.bbox(va)
    r["extent"] = {"before": [round(x,4) for x in bb], "after": [round(x,4) for x in ab],
                   "max_dev": round(max(abs(x-y) for x,y in zip(bb,ab)), 4)}
    if selftest:
        st2 = {}
        EC.view_prims(part, view, hidden=True, keep_all=True, simplify=0, stats=st2)
        r["keep_all_selftest"] = {"dropped_visible": st2["dropped_visible"], "dropped_hidden": st2["dropped_hidden"],
                                  "hlr_V": st2["hlr"]["V"], "hlr_H": st2["hlr"]["H"]}
    res["views"][view] = r
    print(view, json.dumps(r, default=str), flush=True)

json.dump(res, open(os.path.join(OUT, "bench-%s.json" % slug), "w"), indent=1, default=str)
print("OK", flush=True)
