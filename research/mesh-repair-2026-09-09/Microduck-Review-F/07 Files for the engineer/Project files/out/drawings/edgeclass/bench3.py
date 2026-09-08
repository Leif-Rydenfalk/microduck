"""Before/after over every part, written to disk after EVERY view."""
import sys, os, json, time, math
os.environ.setdefault("CE_TRIAD_ROOT", "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck:/Users/leifrydenfalk/dev/ce-workshop")
OUT = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck/out/drawings/edgeclass"
os.makedirs(OUT, exist_ok=True)
LOG = open(os.path.join(OUT, "bench.log"), "a", buffering=1)
def L(*a):
    LOG.write(" ".join(str(x) for x in a) + "\n")
import FreeCAD as App
from cecad import triad, drawing as D, edgeclass as EC

TABLE = os.path.join(OUT, "before-after.json")
table = json.load(open(TABLE)) if os.path.exists(TABLE) else {}

def count(prims):
    c = {}
    for p in prims:
        c[p["k"]] = c.get(p["k"], 0) + 1
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
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%.0f" height="%.0f" viewBox="0 0 %.0f %.0f"><rect width="100%%" height="100%%" fill="#fff"/>' % (W,H,W,H)]
    for p in prims:
        hid = p.get("layer","") == "HIDDEN"
        st = ' stroke="#bbb" stroke-width="0.7" stroke-dasharray="4,3"' if hid else ' stroke="#111" stroke-width="1.2"'
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

VIEWS = ["front", "top", "right"]
for slug in sys.argv[1:]:
    doc = App.newDocument("x_" + slug.replace("-", "_"))
    t = time.time(); part = triad.load(doc, "part:" + slug)
    sh = getattr(part, "shape", None) or part.Shape
    L("=== %s  faces %d edges %d  (load %.1f s)" % (slug, len(sh.Faces), len(sh.Edges), time.time()-t))
    ft = {}
    for f in sh.Faces:
        ft[type(f.Surface).__name__] = ft.get(type(f.Surface).__name__, 0) + 1
    ruled = sum(1 for f in sh.Faces if EC.is_ruled(f))
    rec = table.setdefault(slug, {})
    rec.update({"faces": len(sh.Faces), "edges": len(sh.Edges),
                "face_types": ft, "ruled_faces": ruled, "views": rec.get("views", {})})
    for view in VIEWS:
        r = {}
        t = time.time(); bh, nv, nh = D.view_prims(part, view, hidden=True); tb = time.time()-t
        t = time.time(); bv, _, _ = D.view_prims(part, view, hidden=False); tbv = time.time()-t
        st = {}; t = time.time(); ah, _, _ = EC.view_prims(part, view, hidden=True, stats=st); ta = time.time()-t
        st2 = {}; t = time.time(); av, _, _ = EC.view_prims(part, view, hidden=False, stats=st2); tav = time.time()-t
        st3 = {}; EC.view_prims(part, view, hidden=True, keep_all=True, simplify=0, stats=st3)
        bb, ab = D.bbox(bv), D.bbox(av)
        r = {"with_hidden": {"before": len(bh), "after": len(ah)},
             "visible_only": {"before": len(bv), "after": len(av)},
             "counts_before": count(bv), "counts_after": count(av),
             "classes": st["counts"], "gap": st["gap"],
             "hlr": st["hlr"],
             "kept_visible": st["kept_visible"], "dropped_visible": st["dropped_visible"],
             "kept_hidden": st["kept_hidden"], "dropped_hidden": st["dropped_hidden"],
             "extent_before": [round(x,4) for x in bb], "extent_after": [round(x,4) for x in ab],
             "extent_max_dev": round(max(abs(x-y) for x,y in zip(bb,ab)), 4),
             "selftest_keep_all_dropped": [st3["dropped_visible"], st3["dropped_hidden"]],
             "selftest_hlr": [st3["hlr"]["V"], st3["hlr"]["H"]],
             "seconds": {"before": round(tb,2), "before_vis": round(tbv,2), "after": round(ta,2), "after_vis": round(tav,2)}}
        svg(bv, os.path.join(OUT, "%s-%s-before-vis.svg" % (slug,view)), "%s  %s  BEFORE visible-only  %d prims" % (slug,view,len(bv)))
        svg(av, os.path.join(OUT, "%s-%s-after-vis.svg" % (slug,view)), "%s  %s  AFTER visible-only  %d prims" % (slug,view,len(av)))
        svg(bh, os.path.join(OUT, "%s-%s-before.svg" % (slug,view)), "%s  %s  BEFORE +hidden  %d prims" % (slug,view,len(bh)))
        svg(ah, os.path.join(OUT, "%s-%s-after.svg" % (slug,view)), "%s  %s  AFTER +hidden  %d prims" % (slug,view,len(ah)))
        rec["views"][view] = r
        json.dump(table, open(TABLE, "w"), indent=1)
        L("  %-6s vis %5d -> %5d   +hidden %5d -> %5d   extent dev %.4f   selftest %s   %s" %
          (view, len(bv), len(av), len(bh), len(ah), r["extent_max_dev"], r["selftest_keep_all_dropped"], json.dumps(st["counts"])))
    App.closeDocument(doc.Name)
L("ALLDONE")
