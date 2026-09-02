import sys
sys.path.insert(0, '/Users/leifrydenfalk/dev/ce-workshop/ce-cad')
import numpy as np
from cecad import meshslice

REF = '/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck/reference/pollen-microduck-rl/assets/'

def tris(path):
    T = meshslice.load(path, 1000)
    return np.asarray(T)

for name in ['foot_left','foot_right','sole_left','sole_right']:
    T = tris(REF + name + '.stl')
    V = T.reshape(-1,3)
    print(name, 'tris', len(T), 'bbox',
          ' '.join('%s %.3f..%.3f' % (ax, V[:,i].min(), V[:,i].max()) for i,ax in enumerate('xyz')))

# mirror tests: does foot_right equal foot_left mirrored?  try mirror about x = c
def sample_pts(T, n=4000, seed=0):
    # sample points on triangle surfaces, area-weighted
    rng = np.random.default_rng(seed)
    a,b,c = T[:,0],T[:,1],T[:,2]
    area = 0.5*np.linalg.norm(np.cross(b-a,c-a),axis=1)
    idx = rng.choice(len(T), size=n, p=area/area.sum())
    u = rng.random(n); v = rng.random(n)
    sw = u+v>1; u[sw]=1-u[sw]; v[sw]=1-v[sw]
    return a[idx] + u[:,None]*(b[idx]-a[idx]) + v[:,None]*(c[idx]-a[idx])

def dist_p95(P, Q):
    # nearest vertex distance (Q dense vertex cloud), chunked
    d = np.empty(len(P))
    for i in range(0, len(P), 200):
        d[i:i+200] = np.sqrt(((P[i:i+200,None,:]-Q[None,:,:])**2).sum(-1)).min(1)
    return np.percentile(d,95), d.max(), np.median(d)

for L,R in [('foot_left','foot_right'), ('sole_left','sole_right')]:
    TL = tris(REF+L+'.stl'); TR = tris(REF+R+'.stl')
    VL = TL.reshape(-1,3); VR = TR.reshape(-1,3)
    # candidate mirror: x -> (xLmin+xLmax) ... but frames may already coincide; test each axis mirror about combined centre
    P = sample_pts(TL, 3000)
    Qv = np.unique(VR.round(3), axis=0)
    for ax in [0,1,2]:
        c = (VL[:,ax].min()+VL[:,ax].max()+VR[:,ax].min()+VR[:,ax].max())/4
        Pm = P.copy(); Pm[:,ax] = 2*c - Pm[:,ax]
        p95, mx, med = dist_p95(Pm, Qv)
        print(L,'mirror axis',ated:='xyz'[ax],'about %.3f'%c,'p95 %.3f max %.3f med %.3f'%(p95,mx,med))
    # identity (are they the same mesh unmirrored?)
    p95, mx, med = dist_p95(P, Qv)
    print(L,'identity p95 %.3f max %.3f med %.3f'%(p95,mx,med))
