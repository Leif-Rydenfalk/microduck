import sys, struct
import numpy as np
def load(p):
    d=open(p,'rb').read()
    if d[:5]==b'solid' and b'facet' in d[:300]:
        v=[]
        for line in d.decode(errors='ignore').splitlines():
            s=line.strip()
            if s.startswith('vertex'): v.append([float(x) for x in s.split()[1:4]])
        return np.array(v).reshape(-1,3,3)*1000
    n=struct.unpack('<I',d[80:84])[0]
    a=np.frombuffer(d[84:84+n*50],dtype=np.dtype([('n','<3f4'),('v','<9f4'),('a','<u2')]))
    return a['v'].reshape(-1,3,3).astype(float)*1000
def segs(tri, axis, c):
    out=[]
    keep=[i for i in range(3) if i!=axis]
    for t in tri:
        z=t[:,axis]
        if z.min()<=c<=z.max() and z.max()>z.min():
            pts=[]
            for i in range(3):
                p,q=t[i],t[(i+1)%3]
                if (p[axis]-c)*(q[axis]-c)<=0 and p[axis]!=q[axis]:
                    f=(c-p[axis])/(q[axis]-p[axis]); pts.append((p+f*(q-p))[keep])
            if len(pts)>=2: out.append((pts[0],pts[1]))
    return out
def ascii(tri, axis, c, res=0.5, lo=None, hi=None, w=None):
    s=segs(tri,axis,c)
    if not s: print("no cut at",c); return
    a=np.array(s)
    mn=a.reshape(-1,2).min(0) if lo is None else np.array(lo); mx=a.reshape(-1,2).max(0) if hi is None else np.array(hi)
    nx=int((mx[0]-mn[0])/res)+1; ny=int((mx[1]-mn[1])/res)+1
    keep=[i for i in range(3) if i!=axis]
    print(f"cut {'xyz'[axis]}={c}: horizontal={'xyz'[keep[0]]} {mn[0]:.2f}..{mx[0]:.2f}, vertical={'xyz'[keep[1]]} {mn[1]:.2f}..{mx[1]:.2f} (top row = max)")
    for j in range(ny-1,-1,-1):
        v=mn[1]+(j+0.5)*res
        # crossings of the scanline at height v
        xs=[]
        for p,q in s:
            if (p[1]-v)*(q[1]-v)<0:
                f=(v-p[1])/(q[1]-p[1]); xs.append(p[0]+f*(q[0]-p[0]))
        xs.sort()
        row=[]
        for i in range(nx):
            u=mn[0]+(i+0.5)*res
            inside=sum(1 for x in xs if x<u)%2==1
            row.append('#' if inside else '.')
        print(f"{v:8.2f} "+''.join(row))
