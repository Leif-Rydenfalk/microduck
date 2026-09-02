import sys
sys.path.insert(0, '/Users/leifrydenfalk/dev/ce-workshop/ce-cad')
import numpy as np
from cecad import meshslice
REF='/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck/reference/pollen-microduck-rl/assets/'
T = meshslice.load(REF+'foot_left.stl',1000)
def iv(ax,a,b,tag=''):
    r = meshslice.intervals(T,ax,a,b)
    print('%s iv %s (%.2f,%.2f):'%(tag,ax,a,b), ' '.join('[%.3f,%.3f]'%(u,v) for u,v in r))
print('== A outer wall thickness (x probes) ==')
for z in (-19,-22,-25):
    iv('x',15.0,z,'A')
print('== B walls along y at x=50 ==')
for z in (-19,-22,-25):
    iv('y',50.0,z,'B')
print('== C vertical probes: flange/wall tops ==')
for x,y,tag in [(31,20,'sideL'),(69,20,'sideR'),(50,-11,'front-out'),(50,41,'back-out'),
                (50,-5,'front-deck'),(50,2,'front-deck2'),(50,8,'deck3'),(50,37,'back-deck'),
                (50,34.5,'back-deck-in'),(45,-1,'tab-front-edge'),(50,-1.0,'tab-front'),(50,37.5,'tab-back'),
                (35.5,36,'towerL'),(62.9,36,'towerR'),(38,-3.5,'front-blockL'),(62,-3.5,'front-blockR')]:
    iv('z',x,y,'C-'+tag)
print('== D bottom shell grid: intervals along z (outer bottom, thickness, rib tops) ==')
for x in (34,38,44,50,56,62,67):
    for y in (-8,-4,0,4,10,16,22,28,34,38):
        iv('z',x,y,'D')
print('== E ribs along y at z=-24, several x ==')
for x in (36,45,50,60,64):
    iv('y',x,-24.0,'E')
print('== F ribs along y at z=-27 ==')
for x in (40,50):
    iv('y',x,-27.0,'F')
print('== G slot bounds along y ==')
for z in (-18.0,-17.0,-16.0,-15.0,-14.0,-13.0,-12.5):
    iv('y',50.0,z,'G')
print('== H slot bounds along x ==')
for z in (-18.0,-16.5,-15.0,-14.0,-13.0,-12.5):
    iv('x',22.0,z,'H')
print('== I flange ring along x/y ==')
for z in (-17.0,-15.0,-14.5):
    iv('x',15.0,z,'I')
    iv('x',38.0,z,'I')
    iv('y',33.0,z,'I')
print('== J towers detail ==')
for z in (-19.0,-21.0,-16.0,-14.5):
    iv('x',36.0,z,'Jx')     # along x at y=36
for x in (34.5,35.5,37.5):
    iv('y',x,-20.0,'Jy')
print('== K front blocks detail ==')
for z in (-19.0,-17.0,-15.5,-14.5):
    iv('x',-3.5,z,'Kx')     # along x at y=-3.5
for x in (38,50,62):
    iv('y',x,-19.0,'Ky')
print('== L tabs detail ==')
for z in (-13.0,-12.6):
    iv('x',37.0,z,'Lx-back'); iv('x',0.0,z,'Lx-front')
iv('y',50.0,-12.6,'Ly')
print('== M corner fit z=-22 lower body ==')
segs = meshslice.segments(T,'z',-22.0)
P = np.asarray(segs).reshape(-1,2)
for cx,cy,qx,qy,name in [(63,35,1,1,'x+y+'),(37,35,-1,1,'x-y+'),(37,-5,-1,-1,'x-y-'),(63,-5,1,-1,'x+y-')]:
    m=(P[:,0]-cx)*qx>1; m&=(P[:,1]-cy)*qy>1
    Q=P[m]
    if len(Q)>6:
        A=np.c_[Q[:,0],Q[:,1],np.ones(len(Q))]
        b=(Q**2).sum(1)
        s=np.linalg.lstsq(A,b,rcond=None)[0]
        ccx,ccy=s[0]/2,s[1]/2; r=np.sqrt(s[2]+ccx**2+ccy**2)
        d=np.abs(np.sqrt((Q[:,0]-ccx)**2+(Q[:,1]-ccy)**2)-r)
        print('M corner %s: centre (%.3f,%.3f) R %.3f resid %.3f n %d'%(name,ccx,ccy,r,d.max(),len(Q)))
print('== N corner fit z=-15 flange ==')
segs = meshslice.segments(T,'z',-15.0)
P = np.asarray(segs).reshape(-1,2)
for cx,cy,qx,qy,name in [(64,36,1,1,'x+y+'),(36,36,-1,1,'x-y+'),(36,-6,-1,-1,'x-y-'),(64,-6,1,-1,'x+y-')]:
    m=(P[:,0]-cx)*qx>1; m&=(P[:,1]-cy)*qy>1; m&=np.abs(P[:,0]-50)<21; m&=(P[:,1]>-13)&(P[:,1]<43)
    Q=P[m]
    if len(Q)>6:
        A=np.c_[Q[:,0],Q[:,1],np.ones(len(Q))]
        b=(Q**2).sum(1)
        s=np.linalg.lstsq(A,b,rcond=None)[0]
        ccx,ccy=s[0]/2,s[1]/2; r=np.sqrt(s[2]+ccx**2+ccy**2)
        d=np.abs(np.sqrt((Q[:,0]-ccx)**2+(Q[:,1]-ccy)**2)-r)
        print('N corner %s: centre (%.3f,%.3f) R %.3f resid %.3f n %d'%(name,ccx,ccy,r,d.max(),len(Q)))
