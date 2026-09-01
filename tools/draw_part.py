"""Draw one parametric part to out/drawings/<slug>/<slug>.{dxf,svg,pdf}, verified.

Run under bin/cad:  bin/cad tools/draw_part.py <slug>
Writes out/drawings/<slug>/result.json with scale, views, verified, holes, bbox.
"""
import sys, os, json, time
import FreeCAD
from cecad import triad, inspect
from cecad.autosheet import auto_blueprint
from cecad.sheets import verify_sheet

slug = sys.argv[-1]
root = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck"
stem = os.path.join(root, "out", "drawings", slug, slug)
os.makedirs(os.path.dirname(stem), exist_ok=True)

t0 = time.time()
doc = FreeCAD.newDocument("draw_" + slug.replace("-", "_"))
part = triad.load(doc, "part:" + slug)
shape = getattr(part, "shape", None) or getattr(part, "Shape", None)
bb = inspect.bbox_of(part)
try:
    hl = inspect.holes(part)
    nholes = len(hl)
except Exception as e:
    nholes = "CANNOT DETERMINE (%s)" % e
r = auto_blueprint(part, stem, source="ce-parts/%s/current/cad/part.py" % slug)
# independent read-back, as the task demands: verify_sheet on the file on disk
ok2 = verify_sheet(r["sheet"], r["svg"], part, verbose=False)
out = {
    "slug": slug, "dxf": r["dxf"], "svg": r["svg"], "pdf": r["pdf"],
    "size": r["size"], "scale": "%d:%d" % tuple(r["scale"]),
    "views": r["views"], "verified": bool(r["verified"]), "verify_sheet": bool(ok2),
    "attempts": len(r["attempts"]),
    "last_reason": r["attempts"][-1].get("reason", ""),
    "holes": nholes, "bbox": [round(float(x), 3) for x in bb] if hasattr(bb, "__iter__") else str(bb),
    "seconds": round(time.time() - t0, 1),
}
json.dump(out, open(os.path.join(os.path.dirname(stem), "result.json"), "w"), indent=1)
print("DRAW", json.dumps(out))
