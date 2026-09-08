import sys, os, json, math, numpy as np
sys.path.insert(0,"/Users/leifrydenfalk/dev/ce-workshop/ce-cad")
from cecad import meshslice as ms
sys.path.insert(0,"/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck/out/laneT")
REPO="/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck"
M=os.path.join(REPO,"reference/pollen-microduck-rl/assets/seeed_bearing__configuration_default.stl")
def fit_circle(P):
    x,y=P[:,0].astype(float),P[:,1].astype(float)
    A=np.column_stack([x,y,np.ones_like(x)]); b=x**2+y**2
    sol,*_=np.linalg.lstsq(A,b,rcond=None)
    cx,cy=sol[0]/2,sol[1]/2; r=math.sqrt(max(sol[2]+cx*cx+cy*cy,0))
    for _ in range(40):
        dx,dy=x-cx,y-cy; d=np.hypot(dx,dy); d=np.where(d==0,1e-12,d)
        J=np.column_stack([-dx/d,-dy/d,-np.ones_like(d)])
        st,*_=np.linalg.lstsq(J,-(d-r),rcond=None); cx,cy,r=cx+st[0],cy+st[1],r+st[2]
        if np.max(np.abs(st))<1e-14: break
    d=np.hypot(x-cx,y-cy)
    return cx,cy,r,float(np.abs(d-r).max())
T=ms.load(M,scale=1000.0); V=np.unique(np.round(T.reshape(-1,3),6),axis=0)
r=np.hypot(V[:,0],V[:,1])
res={}
for lab,lo,hi in (("od",7.3,7.7),("bore",4.8,5.2)):
    S=V[(r>lo)&(r<hi)]
    zs=sorted(set(np.round(S[:,2],4).tolist()))
    for zv in zs:
        Q=np.unique(np.round(S[np.abs(S[:,2]-zv)<1e-4][:,0:2],6),axis=0)
        if len(Q)<5: continue
        cx,cy,rr,rmax=fit_circle(Q)
        ang=np.sort(np.degrees(np.arctan2(Q[:,1]-cy,Q[:,0]-cx))); dd=np.diff(ang); dd=dd[dd>1e-9]
        print("%-5s z %8.4f n %3d  d %.6f  centre (%.6f, %.6f) resid_max %.8f arc %.3f step %.4f"
              %(lab,zv,len(Q),2*rr,cx,cy,rmax,ang[-1]-ang[0],np.median(dd)))
        res.setdefault(lab,[]).append({"z_mm":round(float(zv),4),"n":int(len(Q)),
            "d_mm":round(float(2*rr),6),"centre_xy_mm":[round(float(cx),6),round(float(cy),6)],
            "residual_max_mm":round(rmax,8),"arc_deg":round(float(ang[-1]-ang[0]),4),
            "facet_step_deg":round(float(np.median(dd)),4)})
json.dump({"$what":"part:bearing-15x10x3 OD and bore re-measured off mesh VERTICES with a "
           "free-centre circle fit, 2026-09-03 lane T fix pass — so the cradle/ring comparison "
           "is like-for-like (both vertex-based) rather than chord-vs-vertex",
           "mesh":os.path.relpath(M,REPO),"scale":1000.0,"rings":res},
          open(os.path.join(REPO,"out/laneT/bearing-od-vertex-remeasure.json"),"w"),indent=2)
