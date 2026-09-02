#!/usr/bin/env python3
"""mech_dims.py — measure real mechanical dimensions (mm) of every part off the
meshes, and the rebuild dimensional delta for the parts we re-modelled.
Reference assets are in METRES (x1000 -> mm); our rebuilds are already in mm.
"""
import os, json, glob
import Mesh
HERE=os.path.dirname(os.path.abspath(__file__)); REPO=os.path.dirname(HERE)
ASSETS=os.path.join(REPO,"reference","pollen-microduck-rl","assets")
OURS=os.path.join(HERE,"meshes_ours")
OUT=os.path.join(REPO,"out","verify"); os.makedirs(OUT,exist_ok=True)
REBUILT={os.path.splitext(os.path.basename(f))[0] for f in glob.glob(os.path.join(OURS,"*.stl"))}

def dims(path, to_mm):
    m=Mesh.Mesh(path); b=m.BoundBox; s=1000.0 if to_mm else 1.0
    return {"x":round(b.XLength*s,4),"y":round(b.YLength*s,4),"z":round(b.ZLength*s,4),
            "tris":m.CountFacets}

parts=[]
for f in sorted(glob.glob(os.path.join(ASSETS,"*.stl"))):
    name=os.path.splitext(os.path.basename(f))[0]
    ref=dims(f, to_mm=True)   # metres -> mm
    d={"mesh":name,"ref_mm":ref,"rebuilt":name in REBUILT}
    if name in REBUILT:
        our=dims(os.path.join(OURS,name+".stl"), to_mm=False)  # already mm
        d["our_mm"]=our
        d["delta_mm"]={k:round(our[k]-ref[k],4) for k in("x","y","z")}
        d["max_delta_mm"]=round(max(abs(our[k]-ref[k]) for k in("x","y","z")),4)
        d["dim_verdict"]="PASS" if d["max_delta_mm"]<=1.0 else ("CHECK" if d["max_delta_mm"]<=3 else "FAIL")
    parts.append(d)
    tail = ("  [REBUILT d=%.4fmm %s]"%(d["max_delta_mm"],d["dim_verdict"])) if name in REBUILT else ""
    print("%-40s %9.3f x %9.3f x %9.3f mm%s"%(name, ref["x"],ref["y"],ref["z"], tail))
json.dump({"generated":"2026-09-02","units":"mm",
           "tool":"FreeCAD Mesh.BoundBox; reference metres x1000, rebuilds native mm",
           "note":"bbox dimensional check; surface-distance p95 (<=1mm) lives in the refcheck ledger",
           "count":len(parts),"parts":parts}, open(os.path.join(OUT,"mech_dims.json"),"w"), indent=1)
reb=[p for p in parts if p["rebuilt"]]
print("\nrebuilds: %d, dim PASS %d/%d"%(len(reb),sum(1 for p in reb if p.get("dim_verdict")=="PASS"),len(reb)))
print("wrote out/verify/mech_dims.json (%d parts)"%len(parts))
