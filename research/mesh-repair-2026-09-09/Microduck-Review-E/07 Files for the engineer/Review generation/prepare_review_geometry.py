from pathlib import Path
import json,struct,csv,itertools
import numpy as np
from scipy.spatial import cKDTree
from cecad.reviewpack import stl_mesh,write_mesh_stl,viewer,sha,csvwrite
project=Path(__file__).resolve().parents[1]
release=project/'research/review-release-2026-09-08';out=release/'Microduck-Review-C'
source=project/'out/print/stl/fixed/PLA/microduck-yaw-roll-motion.stl'
t=np.array(stl_mesh(source)['positions']).reshape(-1,3,3)
v,inv=np.unique(t.reshape(-1,3),axis=0,return_inverse=True);faces=inv.reshape(-1,3)
parent=list(range(len(faces)))
def root(i):
 while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
 return i
owners={}
for i,f in enumerate(faces):
 for a,b in ((f[0],f[1]),(f[1],f[2]),(f[2],f[0])):
  key=tuple(sorted((a,b)))
  if key in owners:parent[root(i)]=root(owners[key])
  else:owners[key]=i
components={}
for i in range(len(faces)):components.setdefault(root(i),[]).append(i)
assert sorted(map(len,components.values()))==[6,1270]
removed=t[min(components.values(),key=len)];main=t[max(components.values(),key=len)]
assert np.linalg.matrix_rank(removed.reshape(-1,3)-removed[0,0],tol=1e-5)==2
old=np.array(stl_mesh(project/'out/print/stl/PLA/microduck-yaw-roll-motion.stl')['positions']).reshape(-1,3)
local=main*np.array([1,-1,-1]);local+=old.min(0)-local.min((0,1))
newdir=project/'out/review-geometry';newdir.mkdir(exist_ok=True)
model={'parts':[{'positions':local.reshape(-1).tolist(),'indices':list(range(len(local)*3))}]}
fixed=newdir/'microduck-yaw-roll-motion.stl';write_mesh_stl(model,fixed)
# Topology measured again from the finished binary STL.
check=np.array(stl_mesh(fixed)['positions']).reshape(-1,3);vv,fi=np.unique(np.round(check,6),axis=0,return_inverse=True);ff=fi.reshape(-1,3)
ee=np.sort(np.concatenate([ff[:,[0,1]],ff[:,[1,2]],ff[:,[2,0]]]),axis=1);_,counts=np.unique(ee,axis=0,return_counts=True)
assert np.all(counts==2)
proof={'source':str(source.relative_to(project)),'source_sha256':sha(source),'repair':'Use existing head repair; remove its six-face coplanar component; restore original part frame. No generic filling of design apertures.','triangles_before':len(old)//3,'triangles_after':len(local),'boundary_edges_before':42,'boundary_edges_after':int(sum(counts==1)),'nonmanifold_edges_after':int(sum(counts>2)),'maximum_original_vertex_to_repaired_vertex_distance_mm':float(cKDTree(check).query(old)[0].max()),'output_sha256':sha(fixed),'limitations':'Existing local surface deviation and self-intersection diagnostics remain; mating fit and manufacturing approval are not established. See independent-codex-2026-09-08/INTERSECTION-DISPOSITION.md.'}
(newdir/'REPAIR.json').write_text(json.dumps(proof,indent=2))
# Select this revision in the review package without overwriting old source archives.
folder=out/'02 Look at the parts/29 Yaw Roll Motion';target=folder/'Yaw Roll Motion.stl';target.write_bytes(fixed.read_bytes());(folder/'REPAIR.json').write_text(json.dumps(proof,indent=2))
viewer(folder/'Look at this part.html',{'parts':[stl_mesh(target)],'units':'mm'},'Yaw Roll Motion','Repaired review mesh: open boundaries closed; mounting fit still unverified.','../../START HERE.html')
(folder/'READ ME.txt').write_text('Yaw Roll Motion — repaired review revision\nOpen mesh boundaries: 42 before, 0 after.\nUses the existing head repair with its six-face zero-volume fragment removed.\nSee REPAIR.json for exact source and measurement. Existing drawings are historical; mating fit is still unverified.\n')
rows=list(csv.DictReader((out/'SOURCE FILES.csv').open(encoding='utf-8-sig')))
for r in rows:
 if r['file']==target.relative_to(out).as_posix():r.update(source=str(fixed.relative_to(project)),bytes=target.stat().st_size,sha256=sha(target),note='Repaired review revision; see part REPAIR.json')
csvwrite(out/'SOURCE FILES.csv',rows)
rows=list(csv.DictReader((out/'PARTS.csv').open(encoding='utf-8-sig')))
for r in rows:
 if r['number']=='29':r.update(source_path=str(fixed.relative_to(project)),source_kind='Repaired reference mesh; fit unverified',triangles=len(local))
csvwrite(out/'PARTS.csv',rows)
# Rigidly place the same repaired part in the package's assembled snapshot.
mp=out/'01 See the robot/Published assembly mesh.json';original_mesh=release/'original-published-assembly.json'
if not original_mesh.exists():original_mesh.write_bytes((Path(__file__).resolve().parents[3]/'ce-cad/out/web/meshes/microduck.json').read_bytes())
assembly=json.loads(original_mesh.read_text());part=next(p for p in assembly['parts'] if 'microduck-yaw-roll-motion#' in p['name']);av=np.array(part['positions']).reshape(-1,3)
best=None
for perm in itertools.permutations(range(3)):
 for signs in itertools.product([-1,1],repeat=3):
  mat=np.eye(3)[:,perm]*signs
  if np.linalg.det(mat)<.5:continue
  q=old[:,perm]*signs;offset=av.min(0)-q.min(0);d=cKDTree(q+offset).query(av)[0];score=float(d.max())
  if best is None or score<best[0]:best=(score,perm,signs,offset)
assert best[0]<.05,best
q=local[:,:,best[1]]*best[2]+best[3];part.update(positions=q.reshape(-1).tolist(),indices=list(range(len(q)*3)),edges=[],tris=len(q))
proof['assembly_rigid_match_max_vertex_distance_mm']=best[0]
assembly['review_revision']='Yaw-roll mesh updated from repaired review geometry; other published components unchanged.'
mp.write_text(json.dumps(assembly,separators=(',',':')))
viewer(out/'01 See the robot/Turn the robot around.html',assembly,'Microduck — turn it around','Review snapshot with repaired yaw-roll mesh. Static geometry; fit and production not approved.','../START HERE.html')
export=write_mesh_stl(assembly,out/'01 See the robot/Whole robot - view only.stl');export['scope']='Published assembly snapshot with repaired yaw-roll review mesh; static viewing only.';(out/'01 See the robot/Whole robot export.json').write_text(json.dumps(export,indent=2));(out/'GEOMETRY REPAIR.json').write_text(json.dumps(proof,indent=2))
print(json.dumps(proof,indent=2))
