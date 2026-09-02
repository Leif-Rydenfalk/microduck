import sys, os, numpy as np, math
sys.path.insert(0,"/Users/leifrydenfalk/dev/ce-workshop/ce-cad")
from cecad import meshslice as ms
REPO="/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck"
V=np.unique(np.round(ms.load(os.path.join(REPO,"reference/pollen-microduck-rl/assets/motor_support.stl"),scale=1000.0).reshape(-1,3),6),axis=0)
r=np.hypot(V[:,1]-0.0,V[:,2]-7.5)
m=(V[:,0]>-39.9)&(V[:,0]<-35.3)&(r>7.40)&(r<7.60)
S=V[m]
import collections
c=collections.Counter(np.round(S[:,0],4).tolist())
print("bore-radius vertex rows by x:", sorted(c.items()))
# outer arch surface
m2=(V[:,0]>-39.9)&(V[:,0]<-35.3)&(r>8.5)&(r<9.0)
S2=V[m2]
c2=collections.Counter(np.round(S2[:,0],4).tolist())
print("outer 8.5-9.0 rows by x:", sorted(c2.items()))
print("outer radius stats mean %.6f min %.6f max %.6f n %d"%(r[m2].mean(), r[m2].min(), r[m2].max(), m2.sum()))
