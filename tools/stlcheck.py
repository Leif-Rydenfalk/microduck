import struct, json, sys, os, glob
import numpy as np
def read_stl(p):
    with open(p,'rb') as f: data=f.read()
    if data[:5]==b'solid' and b'facet' in data[:400]:
        # ascii
        tris=[]; cur=[]
        for line in data.decode('ascii','ignore').splitlines():
            s=line.strip().split()
            if s and s[0]=='vertex': cur.append([float(x) for x in s[1:4]])
            if len(cur)==3: tris.append(cur); cur=[]
        return np.array(tris,dtype=np.float64), 'ascii'
    n=struct.unpack('<I',data[80:84])[0]
    arr=np.frombuffer(data[84:84+n*50],dtype=np.dtype([('n','<3f4'),('v','<9f4'),('a','<u2')]))
    return arr['v'].reshape(-1,3,3).astype(np.float64), 'binary'
def check(p):
    tris,fmt=read_stl(p)
    n=len(tris)
    v=tris.reshape(-1,3)
    # weld vertices exactly
    uniq,inv=np.unique(v,axis=0,return_inverse=True)
    f=inv.reshape(-1,3)
    degenerate=int(np.sum((f[:,0]==f[:,1])|(f[:,1]==f[:,2])|(f[:,0]==f[:,2])))
    edges=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]])
    key=edges[:,0]*len(uniq)+edges[:,1]
    rkey=edges[:,1]*len(uniq)+edges[:,0]
    und=np.minimum(key,rkey)
    u,c=np.unique(und,return_counts=True)
    open_edges=int(np.sum(c==1)); nonmanifold=int(np.sum(c>2))
    # orientation: each directed edge should appear exactly once
    du,dc=np.unique(key,return_counts=True)
    misoriented=int(np.sum(dc>1))
    bbox=(v.max(0)-v.min(0))
    # volume via divergence
    a=tris[:,0];b=tris[:,1];c3=tris[:,2]
    vol=float(np.sum(np.einsum('ij,ij->i',a,np.cross(b,c3)))/6.0)
    return dict(file=os.path.relpath(p),format=fmt,triangles=n,vertices=int(len(uniq)),degenerate=degenerate,open_edges=open_edges,nonmanifold_edges=nonmanifold,misoriented_edges=misoriented,
                watertight=(open_edges==0 and nonmanifold==0),consistently_oriented=(misoriented==0),signed_volume_mm3=round(vol,3),bbox_mm=[round(float(x),3) for x in bbox])
# ARGUMENTS (added 2026-09-05, own-geometry lane): the tool used to glob a
# single hard-coded directory and IGNORE argv, so `stlcheck.py <file>` printed
# the whole print folder and said nothing about the file asked for — a check
# that answers a question you did not ask. Named paths now win; with none, the
# old sweep runs unchanged. `--json <path>` moves the report; the default is
# still /private/tmp/factory-readiness/stlcheck.json, and the directory is
# created rather than raising FileNotFoundError. Exit 1 if any file is not
# watertight, consistently oriented and free of degenerate facets.
argv = [a for a in sys.argv[1:]]
report = '/private/tmp/factory-readiness/stlcheck.json'
if '--json' in argv:
    i = argv.index('--json'); report = argv[i+1]; del argv[i:i+2]
paths = []
for a in argv:
    paths.extend(sorted(glob.glob(a)) if any(c in a for c in '*?[') else [a])
if not paths:
    paths = sorted(glob.glob('out/print/stl/*/*.stl'))
out=[]
for p in paths:
    try: out.append(check(p))
    except Exception as e: out.append(dict(file=p,error=str(e)))
os.makedirs(os.path.dirname(report) or '.', exist_ok=True)
json.dump(out,open(report,'w'),indent=1)
bad=0
for r in out:
    if 'error' in r: print('ERR',r); bad+=1; continue
    if not (r['watertight'] and r['consistently_oriented'] and r['degenerate']==0): bad+=1
    name=r['file'].split('/')[-1]
    print(f"{name:45s} {r['format']:6s} tri={r['triangles']:6d} deg={r['degenerate']:3d} open={r['open_edges']:4d} nonman={r['nonmanifold_edges']:3d} misor={r['misoriented_edges']:4d} vol={r['signed_volume_mm3']:12.1f} bbox={r['bbox_mm']} {'WATERTIGHT' if r['watertight'] and r['consistently_oriented'] else 'NOT WATERTIGHT'}")
print(f"{len(out)} file(s), {bad} FAIL -> {report}")
sys.exit(1 if bad else 0)
