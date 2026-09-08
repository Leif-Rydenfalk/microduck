from pathlib import Path
source=Path(__file__).with_name('analyze_v7.py').read_text();exec(source.split('# Independent software')[0])
import sys
sys.path.insert(0,str(OUT.parents[3]/'tools'))
from indexed_3mf import mesh_xml
import FreeCAD,Mesh
m=meshes[5][1];cs=m.split(only_watertight=False);main=max(cs,key=lambda c:abs(c.volume));extra=min(cs,key=lambda c:abs(c.volume));assert len(extra.faces)==6 and extra.volume==0;assert np.isclose(main.volume,m.volume,rtol=1e-12)
fm=Mesh.Mesh(main.triangles.reshape((-1,3)).tolist());c=extra.vertices.mean(0);inside=[]
for dy in [-.01,0,.01]:
 p=c+np.array([0,dy,0]);a,b,d=(main.triangles-p).transpose(1,0,2);na,nb,nd=[np.linalg.norm(q,axis=1) for q in [a,b,d]];num=np.einsum('ij,ij->i',a,np.cross(b,d));den=na*nb*nd+np.einsum('ij,ij->i',a,b)*nd+np.einsum('ij,ij->i',b,d)*na+np.einsum('ij,ij->i',d,a)*nb;winding=float(np.arctan2(num,den).sum()/(2*np.pi));inside.append({'point':p.tolist(),'main_generalized_winding_number':winding})
proof={'original_faces':len(m.faces),'cleaned_faces':len(main.faces),'removed_faces':len(extra.faces),'original_volume':float(m.volume),'cleaned_volume':float(main.volume),'removed_volume':float(extra.volume),'removed_bounds':extra.bounds.tolist(),'extra_centroid_probes':inside,'main_watertight':bool(main.is_watertight),'main_winding_consistent':bool(main.is_winding_consistent)}
exp=OUT.parent/'experiments';template=zipfile.ZipFile(exp/'eye-ring-indexed.3mf')
for name,mm in [('yaw-original',m),('yaw-cleaned',main)]:
 xml='<model unit="millimeter" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources><object id="1" name="microduck-yaw-roll-motion" type="model">'+mesh_xml(mm.triangles.reshape(-1,3))+'</object></resources><build><item objectid="1"/></build></model>'
 with zipfile.ZipFile(exp/(name+'.3mf'),'w',zipfile.ZIP_DEFLATED) as dst:
  for n in template.namelist():dst.writestr(n,xml if n=='3D/3dmodel.model' else template.read(n))
(exp/'yaw-cleanup-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof,indent=2))
