"""What ARE the 1058 faces / 2796 edges? Face-type + edge-type census."""
import sys, os, json, math, collections
os.environ.setdefault("CE_TRIAD_ROOT", "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck:/Users/leifrydenfalk/dev/ce-workshop")
import FreeCAD as App, Part
from cecad import triad

slug = sys.argv[1]
doc = App.newDocument("q_" + slug.replace("-", "_"))
part = triad.load(doc, "part:" + slug)
shape = getattr(part, "shape", None) or part.Shape
print("solids", len(shape.Solids), "shells", len(shape.Shells), "faces", len(shape.Faces), "edges", len(shape.Edges), "verts", len(shape.Vertexes), flush=True)

ft = collections.Counter()
area_by = collections.Counter()
for f in shape.Faces:
    n = type(f.Surface).__name__
    ft[n] += 1
    area_by[n] += f.Area
print("FACE TYPES:", json.dumps(dict(ft)), flush=True)
print("FACE AREA mm2:", json.dumps({k: round(v,2) for k,v in area_by.items()}), flush=True)

ct = collections.Counter()
len_by = collections.Counter()
for e in shape.Edges:
    n = type(e.Curve).__name__
    ct[n] += 1
    try: len_by[n] += e.Length
    except Exception: pass
print("EDGE CURVE TYPES:", json.dumps(dict(ct)), flush=True)
print("EDGE LENGTH mm:", json.dumps({k: round(v,2) for k,v in len_by.items()}), flush=True)

# per-face-type: how many BSplineSurface faces, and are they ruled/planar-ish?
bs = [f for f in shape.Faces if type(f.Surface).__name__ == "BSplineSurface"]
print("BSpline faces:", len(bs), flush=True)
if bs:
    degs = collections.Counter()
    for f in bs[:400]:
        s = f.Surface
        degs[(s.UDegree, s.VDegree, s.NbUPoles, s.NbVPoles)] += 1
    print("BSpline (udeg,vdeg,nu,nv) top:", json.dumps({str(k): v for k, v in degs.most_common(12)}), flush=True)

# Are the many faces a LOFT ladder? check faces sharing a smooth edge
