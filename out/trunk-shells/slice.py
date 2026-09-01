"""Cut a mesh with a plane and report the material intervals along probe lines.
usage: python slice.py mesh.stl axis value  [probe_axis probe_values...]
Prints the section's loops (as bbox + vertex count) and, for each probe line
(a line in the section plane at probe_axis=value), the material intervals."""
import sys, struct, numpy as np
sys.path.insert(0, '/Users/leifrydenfalk/dev/ce-workshop/ce-cad')

def load(path, scale=1000.0):
    with open(path,'rb') as f: data=f.read()
    n=struct.unpack('<I', data[80:84])[0]
    arr=np.frombuffer(data[84:84+n*50], dtype=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')]))
    return arr['v'].astype(np.float64)*scale

AX={'x':0,'y':1,'z':2}
def section(tris, axis, val):
    a=AX[axis]; segs=[]
    d=tris[:,:,a]-val
    for t,dd in zip(tris,d):
        s=np.sign(dd)
        if (s>=0).all() or (s<=0).all(): continue
        pts=[]
        for i in range(3):
            j=(i+1)%3
            if dd[i]*dd[j]<0:
                f=dd[i]/(dd[i]-dd[j]); pts.append(t[i]+f*(t[j]-t[i]))
            elif dd[i]==0: pts.append(t[i])
        if len(pts)>=2: segs.append((pts[0],pts[1]))
    return segs

def intervals(segs, axis, probe_axis, pval, tol=1e-6):
    """material intervals along the line probe_axis=pval within the plane."""
    a=AX[axis]; pa=AX[probe_axis]; fa=[i for i in range(3) if i not in (a,pa)][0]
    xs=[]
    for p,q in segs:
        d0=p[pa]-pval; d1=q[pa]-pval
        if d0*d1<0:
            f=d0/(d0-d1); xs.append(p[fa]+f*(q[fa]-p[fa]))
    xs=sorted(xs)
    out=[]
    for i in range(0,len(xs)-1,2): out.append((round(xs[i],2), round(xs[i+1],2)))
    return fa, out

if __name__=='__main__':
    path, axis, val = sys.argv[1], sys.argv[2], float(sys.argv[3])
    tris=load(path)
    segs=section(tris, axis, val)
    P=np.array([p for s in segs for p in s])
    print(f"section {axis}={val}: {len(segs)} segs, bbox x[{P[:,0].min():.2f},{P[:,0].max():.2f}] y[{P[:,1].min():.2f},{P[:,1].max():.2f}] z[{P[:,2].min():.2f},{P[:,2].max():.2f}]")
    if len(sys.argv)>4:
        pax=sys.argv[4]
        for pv in sys.argv[5:]:
            fa,iv=intervals(segs, axis, pax, float(pv))
            print(f"  {pax}={pv}: along {'xyz'[fa]}: {iv}")
