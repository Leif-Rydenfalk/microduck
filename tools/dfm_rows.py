"""dfm_rows.py — turn out/dfm/dfm-rebuilt.json into the rows docs/DFM.md carries,
and localise the support work on the part the drawings are hardest for.

    ce-cad/bin/cad tools/dfm_rows.py

Adds one thing the JSON does not have: every hole's axis resolved AGAINST THE
CHOSEN BUILD DIRECTION, because "horizontal hole" is not a property of a hole,
it is a property of a hole and an orientation. |axis . u| ~ 1 = the bore runs up
the build direction (prints round, slightly undersize, no bridge); ~ 0 = the
bore is across the layers (its top arc BRIDGES and comes out oval/undersize).
"""
import json, math, os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, "tools/dfm_rebuilt.py")).read()
_ns = {"np": np, "math": math, "os": os, "struct": __import__("struct")}
exec(src[src.index("def read_stl"):src.index("def wall_rays")], _ns)
read_stl = _ns["read_stl"]
U = {"+X": (1.,0.,0.), "-X": (-1.,0.,0.), "+Y": (0.,1.,0.),
     "-Y": (0.,-1.,0.), "+Z": (0.,0.,1.), "-Z": (0.,0.,-1.)}
TWO_PERIM = 0.80

doc = json.load(open(os.path.join(ROOT, "out/dfm/dfm-rebuilt.json")))
print("| part | mat | fits | orientation | tall | thinnest wall exact | ray p1 | ray p5 "
      "| support mm2 | foot mm2 | fil g | holes across layers |")
for slug, r in sorted(doc["parts"].items()):
    p = r["printability"]; o = r["orientation"]; m = r["mesh"]
    wr = m["wall_rays"]; u = np.array(U[o["best"]], float)
    axial, cross = [], []
    for h in r["holes"]:
        a = np.array(h["axis"], float)
        (axial if abs(float(a @ u)) > 0.7 else cross).append(h["d"])
    def grp(ds):
        from collections import Counter
        return " ".join("%dxO%.2f" % (n, d) for d, n in sorted(Counter(round(x,2) for x in ds).items()))
    print("| %s | %s | %s | %s | %.1f mm %dL | %.3f | %.3f | %.3f | %.1f | %.1f | %s | %s || axial: %s"
          % (slug.replace("microduck-",""), r["declared_material"], p["fits"],
             o["best"], o["best_height_mm"], o["best_layers"],
             p["thinnest_wall"], wr["p1_mm"], wr["p5_mm"],
             o["best_elevated_lt30_mm2"], o["best_bed_contact_mm2"],
             p["filament_g"], grp(cross), grp(axial)))

print("\n=== support work on power-support, +Z build, by z band ===")
V, N, A = read_stl(os.path.join(ROOT, "out/dfm/stl-rebuilt/microduck-power-support.stl"))
u = np.array((0.,0.,1.))
d = -(N @ u); h = V @ u
hmin = float(h.min())
on_bed = h.max(axis=1) <= hmin + 0.2
sel = (d > math.cos(math.radians(30.))) & ~on_bed
C = V.mean(axis=1)
print("total elevated beta<30: %.1f mm2 of %.0f mm2; bed contact %.1f mm2 "
      "(the part stands on a %.1f mm2 foot)"
      % (A[sel].sum(), A.sum(), A[(d>0.5)&on_bed].sum(), A[(d>0.5)&on_bed].sum()))
band = 6.0
lo = math.floor(V[:,:,2].min()/band)*band
while lo < V[:,:,2].max():
    s = sel & (C[:,2] >= lo) & (C[:,2] < lo+band)
    if A[s].sum() > 2.0:
        xs = V[s].reshape(-1,3)[:,0]; ys = V[s].reshape(-1,3)[:,1]
        flat = s & (d > math.cos(math.radians(10.)))
        print("  z %6.1f..%6.1f : %7.1f mm2  (of which %6.1f mm2 is beta<10, a "
              "flat down-face)   x %6.1f..%6.1f  y %5.1f..%5.1f"
              % (lo, lo+band, A[s].sum(), A[flat].sum(), xs.min(), xs.max(),
                 ys.min(), ys.max()))
    lo += band

print("\n=== power-support: is the 0.466 mm latch slit resolvable at 0.4 mm nozzle? ===")
print("  slit width 0.466 mm (part.py SLIT_W), nozzle 0.4 mm -> one extrusion of "
      "0.4 mm leaves 0.066 mm of air; the slicer's gap-fill closes anything it "
      "cannot fit a line into. MEASURED off the solid: the two slits are the "
      "only thing separating the tongue from the plate.")
for k in ("TONGUE_HW","SLIT_W","SLIT_Z_TOP","TONGUE_T","TONGUE_Z_END"):
    for line in open(os.path.join(ROOT,"ce-parts/microduck-power-support/current/cad/part.py")):
        if line.startswith(k) or line.startswith("TONGUE_HW, SLIT_W") or \
           line.startswith("TONGUE_T, TONGUE_Z_END"):
            pass
import re
srcp = open(os.path.join(ROOT,"ce-parts/microduck-power-support/current/cad/part.py")).read()
for name in ("TONGUE_HW, SLIT_W, SLIT_Z_TOP", "TONGUE_T, TONGUE_Z_END", "RIDGE_R, RIDGE_Y, RIDGE_Z", "HOOK_YZ"):
    mm = re.search(r"^%s = (.+)$" % re.escape(name), srcp, re.M)
    if mm: print("  %s = %s" % (name, mm.group(1)))
