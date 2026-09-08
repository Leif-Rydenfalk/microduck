from pathlib import Path
import zipfile,json,collections
from lxml import etree as ET
base=Path(__file__).parent;out=base.parent/'plates/HEAD-V9-candidate';out.mkdir(exist_ok=True);old=out.parent/'HEAD-V8-candidate';z=zipfile.ZipFile(old/'microduck-head-v8-bracket-flat.3mf');root=ET.fromstring(z.read('3D/3dmodel.model'));ns={'c':root.nsmap[None]};obj=next(o for o in root.findall('c:resources/c:object',ns) if o.get('name')=='microduck-yaw-roll-motion');mesh=obj.find('c:mesh',ns)
clean=ET.fromstring(zipfile.ZipFile(base/'experiments/yaw-cleaned.3mf').read('3D/3dmodel.model')).find('.//c:mesh',ns)
def tris(m):
 v=[tuple(round(float(x.get(k)),4) for k in ['x','y','z']) for x in m.find('c:vertices',ns)];return collections.Counter(tuple(v[int(t.get(k))] for k in ['v1','v2','v3']) for t in m.find('c:triangles',ns))
a,b=tris(mesh),tris(clean);assert not b-a, 'Cleanup must not add or change any oriented triangle';removed=list((a-b).elements());assert len(removed)==6
obj.replace(mesh,clean)
with zipfile.ZipFile(out/'microduck-head-v9-clean.3mf','w',zipfile.ZIP_DEFLATED) as dst:
 for n in z.namelist():dst.writestr(n,ET.tostring(root,xml_declaration=True,encoding='UTF-8') if n=='3D/3dmodel.model' else z.read(n))
(out/'layout.json').write_bytes((old/'layout.json').read_bytes());(out/'removed-faces-proof.json').write_text(json.dumps({'removed_triangle_count':6,'added_or_changed_triangle_count':0,'removed_triangles':removed},indent=2))
