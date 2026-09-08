import zipfile,hashlib,json,re,math
from pathlib import Path
import numpy as np,trimesh
from lxml import etree as ET
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from scipy.spatial import cKDTree
OUT=Path(__file__).parent/'v8-validation'
OUT.mkdir(exist_ok=True)
SRC=OUT.parent.parent/'plates/HEAD-V8-candidate/microduck-head-v8-bracket-flat.gate.gcode.3mf'
z=zipfile.ZipFile(SRC); root=ET.fromstring(z.read('3D/3dmodel.model'));ns={'c':root.nsmap[None]}
objects={o.get('id'):o for o in root.findall('c:resources/c:object',ns)}
report={'sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'mesh':[]}
meshes=[]
for item in root.findall('c:build/c:item',ns):
 comp=objects[item.get('objectid')].find('c:components/c:component',ns);path=comp.get('{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}path').lstrip('/')
 xml=ET.fromstring(z.read(path));v=np.array([[float(e.get(k)) for k in ['x','y','z']] for e in xml.findall('.//c:vertex',ns)]);f=np.array([[int(e.get(k)) for k in ['v1','v2','v3']] for e in xml.findall('.//c:triangle',ns)])
 for tf in [comp.get('transform'),item.get('transform')]:
  a=np.array(list(map(float,tf.split()))).reshape(4,3);v=v@a[:3]+a[3]
 m=trimesh.Trimesh(v,f,process=False);m.merge_vertices(); name=Path(path).stem;meshes.append((name,m))
 comps=m.split(only_watertight=False);lens=m.edges_unique_length
 r={'name':name,'vertices':len(m.vertices),'faces':len(m.faces),'watertight':bool(m.is_watertight),'winding_consistent':bool(m.is_winding_consistent),'components':len(comps),'component_volumes_mm3':[float(c.volume) for c in comps],'volume_mm3':float(m.volume),'bounds_mm':m.bounds.tolist(),'min_edge_mm':float(lens.min()),'degenerate_faces_area_lt_1e-10':int((m.area_faces<1e-10).sum())};report['mesh'].append(r);print(json.dumps(r),flush=True)
(OUT/'mesh.json').write_text(json.dumps(report,indent=2))
# Independent software z-buffer render; no slicer thumbnail and no generative images.
fig,axes=plt.subplots(3,4,figsize=(16,12));R=np.array([[.707,-.707,0],[.354,.354,-.866],[.612,.612,.5]])
for ax,(name,m) in zip(axes.flat,meshes):
 v=m.vertices@R.T;v-=v.min(0);sc=350/max(v[:,:2].ptp(axis=0) if hasattr(v[:,:2],'ptp') else np.ptp(v[:,:2],axis=0));v[:,:2]=v[:,:2]*sc+15;W=380;H=380;depth=np.full((H,W),-np.inf);rgb=np.ones((H,W,3));norm=m.face_normals@R.T
 for face,n in zip(m.faces,norm):
  tri=v[face];lo=np.maximum(np.floor(tri[:,:2].min(0)).astype(int),0);hi=np.minimum(np.ceil(tri[:,:2].max(0)).astype(int),W-1)
  if np.any(hi<lo):continue
  x,y=np.meshgrid(np.arange(lo[0],hi[0]+1),np.arange(lo[1],hi[1]+1));a,b,c=tri;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
  if abs(den)<1e-10:continue
  u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den;w=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den;t=1-u-w;d=u*a[2]+w*b[2]+t*c[2];mask=(u>=0)&(w>=0)&(t>=0)&(d>depth[y,x]);depth[y[mask],x[mask]]=d[mask];shade=.35+.65*abs(float(n@np.array([.3,-.4,.866])));rgb[y[mask],x[mask]]=np.array([.25,.58,.78])*shade
 ax.imshow(rgb);ax.set_title(name.replace('microduck-',''),fontsize=10);ax.axis('off')
axes.flat[-1].axis('off');fig.suptitle('Exact HEAD-V8 archive meshes — independent z-buffer render');fig.tight_layout();fig.savefig(OUT/'exact-meshes.png',dpi=150);plt.close(fig)
