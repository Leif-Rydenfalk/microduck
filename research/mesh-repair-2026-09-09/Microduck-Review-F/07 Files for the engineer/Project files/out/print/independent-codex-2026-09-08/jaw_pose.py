from pathlib import Path
source=Path(__file__).with_name('analyze_v6.py').read_text();exec(source.split('# Independent software')[0])
import sys
sys.path.insert(0,str(OUT.parents[3]/'tools'))
from indexed_3mf import mesh_xml
m=meshes[2][1].copy();R=np.array([[0,0,1],[0,1,0],[-1,0,0]]);v=m.vertices@R.T;v-=v.min(0);v[:,:2]+=np.array([3,108.8]);verts=v[m.faces].reshape(-1,3);xml='<model unit="millimeter" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources><object id="1" name="microduck-jaw" type="model">'+mesh_xml(verts)+'</object></resources><build><item objectid="1"/></build></model>'
p=OUT.parent/'experiments/jaw-side.3mf';template=zipfile.ZipFile(OUT.parent/'experiments/eye-ring-indexed.3mf')
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as dst:
 for n in template.namelist():dst.writestr(n,xml if n=='3D/3dmodel.model' else template.read(n))
print('JAW BOUNDS',v.min(0),v.max(0))
