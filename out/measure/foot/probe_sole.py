import sys
sys.path.insert(0, '/Users/leifrydenfalk/dev/ce-workshop/ce-cad')
import numpy as np
from cecad import meshslice
REF='/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck/reference/pollen-microduck-rl/assets/'
T = meshslice.load(REF+'sole_left.stl',1000)
def iv(ax,a,b,tag=''):
    r = meshslice.intervals(T,ax,a,b)
    print('%s iv %s (%.2f,%.2f):'%(tag,ax,a,b), ' '.join('[%.3f,%.3f]'%(u,v) for u,v in r))
print('== A wall thickness along x at y=15 ==')
for z in (-19,-20.5,-22,-24,-26,-27.5):
    iv('x',15.0,z,'A')
print('== B wall thickness along y at x=50 ==')
for z in (-19,-20.5,-22,-24,-26,-27.5):
    iv('y',50.0,z,'B')
print('== C bottom grid: intervals along z ==')
for x in (32,35,38,44,50,56,62,66,69):
    for y in (-9,-5,0,5,10,15,20,25,30,35,39):
        iv('z',x,y,'C')
print('== D rim top: z of top face ==')
for x,y in [(30.2,15),(70.2,15),(50,-11.7),(50,41.7),(31,-9),(69,40)]:
    iv('z',x,y,'D')
print('== E outer profile: x extents vs z at y=15 (sections numeric) ==')
for z in np.arange(-31.0,-18.2,0.5):
    r = meshslice.intervals(T,'x',15.0,float(z))
    if r: print('E z %.2f x %.3f..%.3f'%(z,r[0][0],r[-1][1]))
print('== F outer profile: y extents vs z at x=50 ==')
for z in np.arange(-31.0,-18.2,0.5):
    r = meshslice.intervals(T,'y',50.0,float(z))
    if r: print('F z %.2f y %.3f..%.3f'%(z,r[0][0],r[-1][1]))
print('== G corner fit z=-22 outer+inner ==')
segs = meshslice.segments(T,'z',-22.0)
P = np.asarray(segs).reshape(-1,2)
for cx,cy,name in [(64,36,'x+y+'),(36,36,'x-y+'),(36,-6,'x-y-'),(64,-6,'x+y-')]:
    qx=1 if cx>50 else -1; qy=1 if cy>15 else -1
    m=(P[:,0]-cx)*qx>1; m&=(P[:,1]-cy)*qy>1
    Q=P[m]
    # split outer/inner by radius from corner guess
    if len(Q)>10:
        d0=np.sqrt((Q[:,0]-cx)**2+(Q[:,1]-cy)**2)
        for lbl,S in [('outer',Q[d0>d0.mean()]),('inner',Q[d0<=d0.mean()])]:
            if len(S)<6: continue
            A=np.c_[S[:,0],S[:,1],np.ones(len(S))]
            b=(S**2).sum(1)
            s=np.linalg.lstsq(A,b,rcond=None)[0]
            ccx,ccy=s[0]/2,s[1]/2; r=np.sqrt(s[2]+ccx**2+ccy**2)
            dd=np.abs(np.sqrt((S[:,0]-ccx)**2+(S[:,1]-ccy)**2)-r)
            print('G %s %s: centre (%.3f,%.3f) R %.3f resid %.3f n %d'%(name,lbl,ccx,ccy,r,dd.max(),len(S)))
