#!/usr/bin/env python3
"""build_fastener_skeleton.py — build every PLACED fastener as a real solid at
its derived world position, and MEASURE them against each other.

    ce-cad/bin/cad tools/build_fastener_skeleton.py
        -> out/fasteners/skeleton.json
        -> out/fasteners/fastener-skeleton-{iso,front,right}.png
        -> log at out/fasteners/skeleton-build.log (bin/cad buffers stdout;
           override with MD_SKELETON_LOG)

WHY THIS EXISTS SEPARATELY FROM THE WHOLE ASSEMBLY. The full assembly loads 70
decimated reference meshes through the kernel and takes many minutes; the
fasteners are 7 parametric solids and 64 placements and take 15.7 s. That makes
this the fast loop for the question this lane has to keep answering: do the
screws we derived actually exist as geometry, in the right places, without
sharing space?

WHAT IT MEASURES, and it is EVERY pair rather than a sample:
    64 * 63 / 2 = 2016 boolean commons between the built screw solids.
    A single non-zero volume is a FAIL — two screws in one hole.

ONE TRAP, MEASURED: the cache key must carry the ref AND the params. This
folder's screws are a FAMILY on length_mm, so keying on the ref alone builds
every M2 screw at whichever length loaded first. 7 members come out of 6
lengths because M2 x 8 and M2.5 x 8 are different parts at the same number.

A SECOND TRAP, MEASURED: `Assembly.add(joint=)` takes a cecad.kinematics JOINT
MODEL name, not a triad connection ref — passing "connection:threaded-m2"
raises KeyError. "screwed" is the model (kinematics.py:160, "threaded directly
into one part - no nut, and the thread engagement in the softer material is the
weak link"), it is in stitch.RETAINS_HELD, and the connection ref stays on the
placement row where the provenance belongs.
"""
import os, json, traceback, time
ROOT="/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck"
os.environ.setdefault("CE_TRIAD_ROOT", ROOT+":/Users/leifrydenfalk/dev/ce-workshop")
# bin/cad buffers stdout, so this writes its own log and flushes every line.
# It used to hardcode /private/tmp/int-fast/, ONE agent's scratch directory,
# and the tool therefore died with FileNotFoundError for everyone else the
# moment that directory was gone. A tool promoted into tools/ may not depend
# on the scratch dir of the session that wrote it. Default is inside the repo;
# override with MD_SKELETON_LOG.
_LOGPATH = os.environ.get(
    "MD_SKELETON_LOG",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "out/fasteners/skeleton-build.log"))
os.makedirs(os.path.dirname(_LOGPATH), exist_ok=True)
LOG=open(_LOGPATH,"w",buffering=1)
def p(*a): LOG.write(" ".join(str(x) for x in a)+"\n"); LOG.flush()
try:
    t0=time.time()
    import FreeCAD as App
    from cecad.core import Assembly
    import cecad.triad as triad
    from cecad import render
    doc=App.newDocument("skel")
    rows=json.load(open(ROOT+"/ce-assemblies/microduck/current/placements.json"))["record"]["rows"]
    fast=[r for r in rows if r.get("via_connection")]
    p("fastener rows in placements.json:", len(fast))
    a=Assembly("microduck_fasteners")
    cache={}
    for i,r in enumerate(fast):
        ref=r["part"]; prm=r.get("params") or {}
        key=(ref,tuple(sorted(prm.items())))
        if key not in cache: cache[key]=triad.load(doc,ref,prm)
        w,x,y,z=r["world_quat_wxyz"]
        rot=App.Rotation(App.Vector(0,0,1),0); rot.Q=(x,y,z,w)
        a.add("%s#%d"%(ref.split(":")[1],i),cache[key],at=tuple(r["world_pos_mm"]),rot=rot,
              joint="screwed")   # cecad.kinematics model; the connection ref lives on the placement row
    doc.recompute()
    p("distinct screw members built:", len(cache), sorted(str(k[1]) for k in cache))
    p("instances placed:", len(a.items), "in %.1f s"%(time.time()-t0))
    # MEASURE: interference between screws
    from cecad.core import Part
    bads=0; pairs=0
    solids=[(l,s) for l,_,s,_ in a.items]
    for i in range(len(solids)):
        for j in range(i+1,len(solids)):
            pairs+=1
            c=solids[i][1].common(solids[j][1])
            if c.Volume>1e-6:
                bads+=1
                p("  SCREW-SCREW INTERFERENCE %s x %s  %.4f mm3"%(solids[i][0],solids[j][0],c.Volume))
    p("screw-screw pairs checked:",pairs,"interfering:",bads)
    bb=None
    for _,_,s,_ in a.items:
        bb = s.BoundBox if bb is None else (bb.add(s.BoundBox) or bb)
    p("fastener cloud bbox mm: X %.3f..%.3f  Y %.3f..%.3f  Z %.3f..%.3f"%(bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax))
    out=ROOT+"/out/fasteners/fastener-skeleton"
    for v in ("iso","front","right"):
        render(a,"%s-%s.png"%(out,v),view=v); p("rendered %s-%s.png"%(out,v))
    json.dump({"$what":"the 64 placed fasteners as solids, measured after building",
               "instances":len(a.items),"distinct_members":len(cache),
               "screw_screw_pairs_checked":pairs,"screw_screw_interferences":bads,
               "bbox_mm":{"x":[bb.XMin,bb.XMax],"y":[bb.YMin,bb.YMax],"z":[bb.ZMin,bb.ZMax]},
               "seconds":round(time.time()-t0,1)},
              open(ROOT+"/out/fasteners/skeleton.json","w"),indent=1)
    p("DONE")
except Exception:
    p("RAISED:\n"+traceback.format_exc())
