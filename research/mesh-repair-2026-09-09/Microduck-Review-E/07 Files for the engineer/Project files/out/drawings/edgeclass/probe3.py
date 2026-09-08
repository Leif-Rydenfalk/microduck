"""Per-edge census: dihedral x face-type pair x length. And is encodeRegularity available?"""
import sys, os, json, math, collections
os.environ.setdefault("CE_TRIAD_ROOT", "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck:/Users/leifrydenfalk/dev/ce-workshop")
import FreeCAD as App, Part
from cecad import triad

slug = sys.argv[1]
doc = App.newDocument("r_" + slug.replace("-", "_"))
part = triad.load(doc, "part:" + slug)
sh = getattr(part, "shape", None) or part.Shape

print("encodeRegularity on Shape?", hasattr(sh, "encodeRegularity"), flush=True)
import Part as _P
print("Part module regularity syms:", [n for n in dir(_P) if 'egular' in n.lower()], flush=True)
try:
    from OCC import BRepLib
    print("OCC BRepLib importable", flush=True)
except Exception as ex:
    print("no OCC python:", ex, flush=True)
print("Shape methods with 'nify' or 'emoveS':", [n for n in dir(sh) if 'nify' in n or 'emoveS' in n], flush=True)

# --- adjacency
ef = {}
for i, f in enumerate(sh.Faces):
    for e in f.Edges:
        ef.setdefault(e.hashCode(), []).append(i)
# sanity: cross-check hashCode adjacency against ancestorsOfType on a sample
import random
random.seed(1)
bad = 0
samp = random.sample(range(len(sh.Edges)), min(40, len(sh.Edges)))
for k in samp:
    e = sh.Edges[k]
    a = sorted(ef.get(e.hashCode(), []))
    b = sorted(sh.Faces.index(f) if False else i for i, f in enumerate(sh.Faces) for x in [0] if any(x2.isSame(e) for x2 in f.Edges))
    if a != sorted(set(b)):
        bad += 1
print("hashCode-vs-isSame adjacency mismatches in %d samples: %d" % (len(samp), bad), flush=True)

def nrm(f, p):
    u, v = f.Surface.parameter(p)
    n = f.normalAt(u, v)
    if f.Orientation == "Reversed":
        n = n * -1.0
    return n

rows = []
for k, e in enumerate(sh.Edges):
    fs = ef.get(e.hashCode(), [])
    try: L = e.Length
    except Exception: L = 0.0
    ct = type(e.Curve).__name__
    if len(fs) != 2:
        rows.append({"i": k, "L": L, "ct": ct, "nf": len(fs), "ang": None, "ft": None})
        continue
    f1, f2 = sh.Faces[fs[0]], sh.Faces[fs[1]]
    t1, t2 = type(f1.Surface).__name__, type(f2.Surface).__name__
    ft = "|".join(sorted([t1[:4], t2[:4]]))
    amax = 0.0; ok = True
    for t in (0.2, 0.5, 0.8):
        p = e.valueAt(e.FirstParameter + t * (e.LastParameter - e.FirstParameter))
        try:
            n1, n2 = nrm(f1, p), nrm(f2, p)
            c = max(-1.0, min(1.0, n1.dot(n2)))
            a = math.degrees(math.acos(c))
        except Exception:
            ok = False; a = 0.0
        amax = max(amax, a)
    rows.append({"i": k, "L": round(L, 4), "ct": ct, "nf": 2, "ang": round(amax, 4), "ft": ft, "ok": ok,
                 "f": [fs[0], fs[1]], "a1": round(f1.Area, 4), "a2": round(f2.Area, 4)})

bins = [0, 0.01, 0.1, 0.5, 1, 2, 3, 5, 7, 10, 15, 20, 30, 45, 60, 90, 120, 180.1]
def bn(a):
    for lo, hi in zip(bins, bins[1:]):
        if lo <= a < hi: return "%g-%g" % (lo, hi)
    return ">180"
xt = collections.defaultdict(collections.Counter)
for r in rows:
    if r["ang"] is None: continue
    xt[r["ft"]][bn(r["ang"])] += 1
print("=== dihedral histogram BY FACE-TYPE PAIR ===", flush=True)
for ft in sorted(xt, key=lambda k: -sum(xt[k].values())):
    tot = sum(xt[ft].values())
    print("%-14s n=%4d  %s" % (ft, tot, json.dumps({b: xt[ft][b] for b in bins and [bn(x) for x in []] or sorted(xt[ft], key=lambda s: float(s.split('-')[0]))})), flush=True)

# length-weighted: how much INK is below various thresholds
tot_len = sum(r["L"] for r in rows)
for th in (0.5, 1, 2, 5, 8, 10, 12, 15, 20, 30):
    n = sum(1 for r in rows if r["ang"] is not None and r["ang"] < th)
    l = sum(r["L"] for r in rows if r["ang"] is not None and r["ang"] < th)
    print("below %5.1f deg: %4d edges (%5.1f%%)  %8.2f mm (%5.1f%% of edge length)" % (th, n, 100.0*n/len(rows), l, 100.0*l/tot_len), flush=True)

json.dump({"slug": slug, "n_faces": len(sh.Faces), "n_edges": len(sh.Edges), "rows": rows},
          open("/private/tmp/sheet-edgeclass/probe3-%s.json" % slug, "w"))
print("wrote probe3 json", flush=True)
