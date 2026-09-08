import sys
sys.path.insert(0, '/Users/leifrydenfalk/dev/ce-workshop/ce-cad')
import numpy as np
from cecad import meshslice
from cecad.meshslice import _UV
REF='/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck/reference/pollen-microduck-rl/assets/'
T = meshslice.load(REF+'foot_left.stl',1000)
def iv(tag, **kw):
    # call with e.g. iv('t', axis='y', x=50, z=-24) — order-safe
    axis = kw.pop('axis'); ui,vi = _UV[axis]
    names='xyz'
    u = kw[names[ui]]; v = kw[names[vi]]
    r = meshslice.intervals(T,axis,u,v)
    print('%s iv along %s at %s:'%(tag,axis,','.join('%s=%.2f'%(k,kw[k]) for k in sorted(kw))), ' '.join('[%.3f,%.3f]'%(a,b) for a,b in r))
print('== R ribs: along y ==')
for x in (38,45,50,56,62):
    for z in (-24.0,-27.0):
        iv('R', axis='y', x=x, z=z)
print('== S slot: along y at x=50 ==')
for z in (-18.0,-17.0,-16.0,-15.0,-14.0,-13.0,-12.5):
    iv('S', axis='y', x=50.0, z=z)
print('== S2 slot: along y at x=40 ==')
for z in (-18.0,-16.0,-15.0,-14.5):
    iv('S2', axis='y', x=40.0, z=z)
print('== T front/back outer roundover: y extents vs z at x=50 ==')
for z in np.arange(-18.4,-12.2,0.35):
    r = meshslice.intervals(T,'y',float(z),50.0) if _UV['y']==(2,0) else meshslice.intervals(T,'y',50.0,float(z))
    if r: print('T z %.2f y %.3f..%.3f  all: %s'%(z,r[0][0],r[-1][1],' '.join('[%.2f,%.2f]'%(a,b) for a,b in r)))
print('== U towers/pockets: along y at z=-20,-19,-16.5 ==')
for x in (34.5,36.5,40.0,44.0,60.0,63.5,66.0):
    for z in (-20.0,-16.5):
        iv('U', axis='y', x=x, z=z)
print('== V front clip: along y ==')
for x in (45.0,50.0):
    for z in (-22.5,-20.0,-18.5,-16.5,-14.0,-13.0,-12.6):
        iv('V', axis='y', x=x, z=z)
print('== W screw boss ==')
for y in (2.0,4.5,7.0):
    iv('W', axis='z', x=48.5, y=y)
iv('W', axis='z', x=50.0, y=6.2)
iv('W', axis='z', x=50.0, y=2.8)
iv('W', axis='y', x=50.0, z=-19.0)
iv('W', axis='x', y=4.5, z=-19.0)
iv('W', axis='y', x=50.0, z=-25.0)
print('== X wall top ring / step deck extents ==')
for y in (12.0,20.0,28.0):
    iv('X', axis='z', x=33.0, y=y)
    iv('X', axis='z', x=67.5, y=y)
for x in (36.0,42.0,48.0):
    iv('X', axis='z', x=x, y=6.5)
print('== Y cradle ledges: along x ==')
for z in (-20.0,-21.0):
    for y in (18.0,22.0,26.0):
        iv('Y', axis='x', y=y, z=z)
print('== Z lower-body corner fit z=-19.5 (outer ring only) ==')
segs = meshslice.segments(T,'z',-19.5)
P = np.asarray(segs).reshape(-1,2)
# keep only points near the outer boundary (outside inner rect 33.2..66.8 / -8.3..38.3)
m = (P[:,0]<33.2)|(P[:,0]>66.8)|(P[:,1]<-8.3)|(P[:,1]>38.3)
P=P[m]
for cx,cy,name in [(64,35,'x+y+'),(36,35,'x-y+'),(36,-5,'x-y-'),(64,-5,'x+y-')]:
    qx=1 if cx>50 else -1; qy=1 if cy>15 else -1
    mm=(P[:,0]-cx)*qx>0.5; mm&=(P[:,1]-cy)*qy>0.5
    Q=P[mm]
    if len(Q)>6:
        A=np.c_[Q[:,0],Q[:,1],np.ones(len(Q))]
        b=(Q**2).sum(1)
        s=np.linalg.lstsq(A,b,rcond=None)[0]
        ccx,ccy=s[0]/2,s[1]/2; rr=np.sqrt(s[2]+ccx**2+ccy**2)
        d=np.abs(np.sqrt((Q[:,0]-ccx)**2+(Q[:,1]-ccy)**2)-rr)
        print('Z corner %s: centre (%.3f,%.3f) R %.3f resid %.3f n %d'%(name,ccx,ccy,rr,d.max(),len(Q)))
print('== ZZ through-slot bounds ==')
for y in (16.0,18.0,20.0,30.0,31.5,33.0):
    iv('ZZ', axis='x', y=y, z=-26.0)
for x in (40.0,50.0,60.0):
    iv('ZZ', axis='y', x=x, z=-26.0)
