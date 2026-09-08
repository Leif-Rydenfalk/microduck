import zipfile,hashlib,json,re,math
from pathlib import Path
import numpy as np,trimesh
from lxml import etree as ET
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from scipy.spatial import cKDTree
OUT=Path(__file__).parent/'v6-validation'
OUT.mkdir(exist_ok=True)
SRC=OUT.parent.parent/'plates/HEAD-V6-candidate/microduck-head-v6-indexed.gate.gcode.3mf'
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
axes.flat[-1].axis('off');fig.suptitle('Exact HEAD-V6 archive meshes — independent z-buffer render');fig.tight_layout();fig.savefig(OUT/'exact-meshes.png',dpi=150);plt.close(fig)
# Parse actual motion including G2/G3 arcs (0.15 mm max chord), relative/absolute E and coordinate modes.
text=z.read('Metadata/plate_1.gcode').decode();layers=[];state={'X':0.,'Y':0.,'Z':0.,'E':0.};relative_e=False;absolute=True;obj=None;feature='';width=.45;arc_count=0
for line in text.splitlines():
 if line.startswith('; CHANGE_LAYER'):layers.append({'z':None,'moves':[]});continue
 if line.startswith('; Z_HEIGHT:'):
  if layers:layers[-1]['z']=float(line.split(':')[1]);continue
 if line.startswith('; start printing object, unique label id:'):obj=int(line.split(':')[-1]);continue
 if line.startswith('; stop printing object'):obj=None;continue
 if line.startswith('; FEATURE:'):feature=line.split(':',1)[1].strip();continue
 if line.startswith('; LINE_WIDTH:'):width=float(line.split(':')[1]);continue
 code=line.split(';')[0].strip();p=code.split();
 if not p:continue
 cmd=p[0]
 if cmd=='M83':relative_e=True
 if cmd=='M82':relative_e=False
 if cmd=='G90':absolute=True
 if cmd=='G91':absolute=False
 if cmd not in ['G0','G1','G2','G3','G92']:continue
 vals={k:float(v) for k,v in re.findall(r'([XYZEFIJP])([-+]?\d*\.?\d+)',code)}
 if cmd=='G92':
  state.update({k:v for k,v in vals.items() if k in state});continue
 new=state.copy()
 for k in 'XYZ':
  if k in vals:new[k]=vals[k] if absolute else state[k]+vals[k]
 de=vals.get('E',0) if relative_e else vals.get('E',state['E'])-state['E'];new['E']=state['E']+de
 if layers and de>1e-8 and obj is not None and any(k in vals for k in 'XY'):
  a=np.array([state['X'],state['Y']]);b=np.array([new['X'],new['Y']]);points=np.array([a,b])
  if cmd in ['G2','G3']:
   arc_count+=1;center=a+np.array([vals.get('I',0),vals.get('J',0)]);r=np.linalg.norm(a-center);s=math.atan2(*(a-center)[::-1]);e=math.atan2(*(b-center)[::-1]);delta=(e-s)%(2*math.pi) if cmd=='G3' else -((s-e)%(2*math.pi));n=max(2,int(abs(delta)*r/.15)+1);ang=np.linspace(s,s+delta,n);points=center+np.column_stack([np.cos(ang),np.sin(ang)])*r;points[-1]=b
  seg=np.stack([points[:-1],points[1:]],axis=1)
  layers[-1]['moves'].append((obj,feature,width,new['Z'],seg))
 state=new
print('Parsed',len(layers),'layers',arc_count,'extrusion arcs',flush=True)
report['gcode']={'layers':len(layers),'arc_extrusions':arc_count,'header_layers':int(re.search(r'total layer number: (\d+)',text)[1]),'z':[l['z'] for l in layers]}
objlayers={};issues=[];samples=[];prev=None
for i,l in enumerate(layers):
 chunks=[];modelchunks=[]
 for obj,feat,w,zv,seg in l['moves']:
  if abs(zv-l['z'])>0.001:issues.append({'layer':i+1,'z_mismatch':zv,'declared':l['z']})
  if not feat.startswith('Support'):objlayers.setdefault(obj,set()).add(i+1)
  for a,b in seg:
   n=max(2,int(np.linalg.norm(b-a)/.25)+1);pts=np.linspace(a,b,n);chunks.append(pts)
   if not feat.startswith('Support'):modelchunks.append(pts)
 pts=np.concatenate(chunks) if chunks else np.zeros((0,2));model=np.concatenate(modelchunks) if modelchunks else np.zeros((0,2));bad=np.zeros((0,2))
 if prev is not None and len(prev) and len(model):
  d=cKDTree(prev).query(model,workers=2)[0];bad=model[d>.65]
 samples.append((pts,bad));prev=pts
 if i%40==0:print('support sampling',i+1,len(bad),flush=True)
report['gcode']['objects']={str(k):{'first':min(v),'last':max(v),'missing':sorted(set(range(min(v),max(v)+1))-v)} for k,v in objlayers.items()};report['gcode']['empty_layers']=[i+1 for i,l in enumerate(layers) if not l['moves']];report['gcode']['z_mismatches']=issues;report['gcode']['unsupported_samples_0_65mm']=[{'layer':i+1,'z':layers[i]['z'],'samples':len(b)} for i,(p,b) in enumerate(samples) if len(b)]
(OUT/'analysis.json').write_text(json.dumps(report,indent=2))
worst=sorted(range(1,len(samples)),key=lambda i:len(samples[i][1]),reverse=True)[:4];chosen=[0,17]+worst
fig,axes=plt.subplots(2,3,figsize=(17,11))
for ax,i in zip(axes.flat,chosen):
 for obj,feat,w,zv,seg in layers[i]['moves']:ax.add_collection(LineCollection(seg,colors='#aaa' if feat.startswith('Support') else '#135e99',linewidths=.35))
 bad=samples[i][1]
 if len(bad):ax.scatter(bad[:,0],bad[:,1],s=.6,c='red')
 ax.set(xlim=(0,305),ylim=(0,320),aspect='equal',title=f'Layer {i+1}, Z={layers[i]["z"]} mm; {len(bad)} flagged samples')
fig.suptitle('Actual extrusion paths: model blue, support grey; red >0.65 mm from prior deposition\nRed includes legal bridges / support separation: candidates, not automatic failures');fig.tight_layout();fig.savefig(OUT/'actual-toolpaths.png',dpi=160);plt.close(fig)
# Detailed eye-ring first layers and top shell previous suspect region.
fig,axes=plt.subplots(2,4,figsize=(17,9))
for ax,i in zip(axes.flat,[0,1,2,3,15,16,17,18]):
 for obj,feat,w,zv,seg in layers[i]['moves']:ax.add_collection(LineCollection(seg,colors='#aaa' if feat.startswith('Support') else '#135e99',linewidths=1))
 ax.set(xlim=(76,110),ylim=(157,191),aspect='equal',title=f'Eye ring, layer {i+1}, Z {layers[i]["z"]}')
fig.tight_layout();fig.savefig(OUT/'eye-ring-layers.png',dpi=160)
print('DONE',flush=True)
