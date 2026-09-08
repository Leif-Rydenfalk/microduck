import zipfile,json,sys
from pathlib import Path
from lxml import etree as ET
sys.path.insert(0,str(Path(__file__).parents[3]/'tools'))
from indexed_3mf import mesh_xml
out=Path(__file__).parent.parent/'plates/HEAD-V6-candidate';out.mkdir(exist_ok=True)
src=out.parent/'HEAD-V5/microduck-head-v5.3mf';z=zipfile.ZipFile(src);root=ET.fromstring(z.read('3D/3dmodel.model'));ns={'c':root.nsmap[None]};rows=[]
for obj in root.findall('c:resources/c:object',ns):
 mesh=obj.find('c:mesh',ns)
 if mesh is None:raise RuntimeError('Expected baked direct meshes')
 verts=[tuple(float(v.get(k)) for k in ['x','y','z']) for v in mesh.find('c:vertices',ns)];faces=[tuple(int(v.get(k)) for k in ['v1','v2','v3']) for v in mesh.find('c:triangles',ns)];soup=[verts[i] for f in faces for i in f]
 new=ET.fromstring(mesh_xml(soup));vnew=[tuple(float(v.get(k)) for k in ['x','y','z']) for v in new.find('vertices')];fnew=[tuple(int(v.get(k)) for k in ['v1','v2','v3']) for v in new.find('triangles')]
 assert soup==[vnew[i] for f in fnew for i in f], 'Vertex indexing must not change any oriented triangle'
 for e in new.iter():e.tag='{'+ns['c']+'}'+e.tag
 obj.replace(mesh,new);rows.append({'object':obj.get('name'),'old_vertices':len(verts),'new_vertices':len(vnew),'triangles':len(faces),'oriented_surface_identical':True})
with zipfile.ZipFile(out/'microduck-head-v6-indexed.3mf','w',zipfile.ZIP_DEFLATED) as dst:
 for n in z.namelist():dst.writestr(n,ET.tostring(root,xml_declaration=True,encoding='UTF-8') if n=='3D/3dmodel.model' else z.read(n))
(out/'reindex-proof.json').write_text(json.dumps(rows,indent=2));(out/'layout.json').write_bytes((out.parent/'HEAD-V5/layout.json').read_bytes());print(json.dumps(rows,indent=2))
