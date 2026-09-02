import sys
sys.path.insert(0, '/Users/leifrydenfalk/dev/ce-workshop/ce-cad')
import numpy as np
from cecad import meshslice

REF = '/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck/reference/pollen-microduck-rl/assets/'
def tris(p): return np.asarray(meshslice.load(REF+p+'.stl', 1000))

def sample_pts(T, n=2500, seed=0):
    rng = np.random.default_rng(seed)
    a,b,c = T[:,0],T[:,1],T[:,2]
    area = 0.5*np.linalg.norm(np.cross(b-a,c-a),axis=1)
    idx = rng.choice(len(T), size=n, p=area/area.sum())
    u=rng.random(n); v=rng.random(n); sw=u+v>1; u[sw]=1-u[sw]; v[sw]=1-v[sw]
    return a[idx]+u[:,None]*(b[idx]-a[idx])+v[:,None]*(c[idx]-a[idx])

def pt_tri_dist(P, T, chunk=60):
    # exact point-to-triangle distance, chunked over points
    A,B,C = T[:,0],T[:,1],T[:,2]
    E0 = B-A; E1 = C-A
    a = (E0*E0).sum(1); b=(E0*E1).sum(1); c=(E1*E1).sum(1)
    det = a*c-b*b; det[det<1e-12]=1e-12
    out = np.empty(len(P))
    for i in range(0,len(P),chunk):
        D = A[None,:,:]-P[i:i+chunk,None,:]        # (m,t,3)
        d = (E0[None]*D).sum(-1); e=(E1[None]*D).sum(-1)
        s = (b*e-c*d)/det; t=(b*d-a*e)/det
        s=np.clip(s,0,1); t=np.clip(t,0,1)
        # project back: clamp sum
        over = s+t>1
        # simple renormalise for clamped region (approximation avoided: do proper edge clamp)
        ss=s.copy(); tt=t.copy()
        ss[over]=s[over]/(s[over]+t[over]); tt[over]=t[over]/(s[over]+t[over])
        X = A[None]+ss[...,None]*E0[None]+tt[...,None]*E1[None]
        d1 = np.linalg.norm(X-P[i:i+chunk,None,:],axis=-1).min(1)
        out[i:i+chunk]=d1
    return out

def grade(Pa, Tb, tag):
    d = pt_tri_dist(Pa, Tb)
    print(tag, 'p95 %.3f max %.3f med %.3f'%(np.percentile(d,95), d.max(), np.median(d)))
    return d

for L,R in [('foot_left','foot_right'),('sole_left','sole_right')]:
    TL=tris(L); TR=tris(R)
    P=sample_pts(TL)
    for label, f in [
        ('mirX', lambda q: q*[-1,1,1]),
        ('mirX+mirY30', lambda q: (q*[-1,-1,1]+[0,30,0])),
        ('rot180z', lambda q: (q*[-1,-1,1])),  # rotation 180 about z through origin: x->-x, y->-y
        ('rot180z+y30', lambda q: (q*[-1,-1,1]+[0,30,0])),
    ]:
        grade(f(P).astype(np.float64), TR, '%s->%s %s'%(L,R,label))
