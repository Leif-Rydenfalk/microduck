import sys
sys.path.insert(0, '/Users/leifrydenfalk/dev/ce-workshop/ce-cad')
import numpy as np
from cecad import meshslice
from cecad.meshslice import _UV
REF='/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck/reference/pollen-microduck-rl/assets/'
T = meshslice.load(REF+'sole_left.stl',1000)
def iv(tag, **kw):
    axis = kw.pop('axis'); ui,vi = _UV[axis]
    names='xyz'
    u = kw[names[ui]]; v = kw[names[vi]]
    r = meshslice.intervals(T,axis,u,v)
    print('%s iv along %s at %s:'%(tag,axis,','.join('%s=%.2f'%(k,kw[k]) for k in sorted(kw))), ' '.join('[%.3f,%.3f]'%(a,b) for a,b in r))
print('== P outer/inner y profile vs z at x=50 ==')
for z in np.arange(-31.0,-18.2,0.5):
    r = meshslice.intervals(T,'y',float(z),50.0)
    if r: print('P z %.2f y %.3f..%.3f walls %s'%(z,r[0][0],r[-1][1],' '.join('[%.2f,%.2f]'%(a,b) for a,b in r)))
print('== Q wall probes along y ==')
for x in (40,50,60):
    for z in (-19.0,-22.0,-24.0):
        iv('Q', axis='y', x=x, z=z)
print('== R corner fits at several z (outer + inner) ==')
for zc in (-19.0,-24.0,-26.0,-27.5,-28.5,-29.5,-30.4):
    segs = meshslice.segments(T,'z',zc)
    P = np.asarray(segs).reshape(-1,2)
    if len(P)<20: print('R z %.1f: too few'%zc); continue
    xmid,ymid = (P[:,0].min()+P[:,0].max())/2,(P[:,1].min()+P[:,1].max())/2
    print('R z %.2f extents x %.3f..%.3f y %.3f..%.3f'%(zc,P[:,0].min(),P[:,0].max(),P[:,1].min(),P[:,1].max()))
    for name,cx,cy in [('x+y+',P[:,0].max()-5,P[:,1].max()-5),('x-y+',P[:,0].min()+5,P[:,1].max()-5),('x-y-',P[:,0].min()+5,P[:,1].min()+5),('x+y-',P[:,0].max()-5,P[:,1].min()+5)]:
        qx=1 if cx>xmid else -1; qy=1 if cy>ymid else -1
        mm=(P[:,0]-cx)*qx>0; mm&=(P[:,1]-cy)*qy>0
        Q=P[mm]
        if len(Q)>10:
            d0=np.sqrt((Q[:,0]-cx)**2+(Q[:,1]-cy)**2)
            for lbl,S in [('outer',Q[d0>d0.mean()]),('inner',Q[d0<=d0.mean()])]:
                if len(S)<6: continue
                A=np.c_[S[:,0],S[:,1],np.ones(len(S))]
                b=(S**2).sum(1)
                s=np.linalg.lstsq(A,b,rcond=None)[0]
                ccx,ccy=s[0]/2,s[1]/2; rr=np.sqrt(s[2]+ccx**2+ccy**2)
                dd=np.abs(np.sqrt((S[:,0]-ccx)**2+(S[:,1]-ccy)**2)-rr)
                print('R z %.1f %s %s: centre (%.3f,%.3f) R %.3f resid %.3f n %d'%(zc,name,lbl,ccx,ccy,rr,dd.max(),len(S)))
print('== S rim: top-face ring extents at z=-18.35 ==')
segs = meshslice.segments(T,'z',-18.40)
P = np.asarray(segs).reshape(-1,2)
print('S rim ring x %.3f..%.3f y %.3f..%.3f'%(P[:,0].min(),P[:,0].max(),P[:,1].min(),P[:,1].max()))
print('== U inner wall y faces vs z at x=50 ==')
# inner faces from P above; also explicit
for z in (-19.0,-21.0,-23.0):
    r = meshslice.intervals(T,'y',float(z),50.0)
    if len(r)>=2:
        print('U z %.1f: front wall %.3f..%.3f back wall %.3f..%.3f'%(z,r[0][0],r[0][1],r[-1][0],r[-1][1]))
