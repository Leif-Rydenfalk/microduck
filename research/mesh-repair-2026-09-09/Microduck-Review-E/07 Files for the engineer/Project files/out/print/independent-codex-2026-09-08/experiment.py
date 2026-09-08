from pathlib import Path
source=Path(__file__).with_name('analyze.py').read_text();exec(source.split('# Independent software')[0])
EXP=OUT/'experiments';EXP.mkdir(exist_ok=True)
m=meshes[6][1].copy();m.apply_translation([-m.bounds[0,0]+120,-m.bounds[0,1]+120,0]);m.export(EXP/'eye-ring-exact.stl')
# 3MF input uses a disconnected vertex per triangle: test that against indexed vertices, identical surfaces.
from xml.sax.saxutils import escape
for mode in ['indexed','soup']:
 mm=m.copy()
 if mode=='soup':v=mm.triangles.reshape(-1,3);f=np.arange(len(v)).reshape(-1,3)
 else:v=mm.vertices;f=mm.faces
 xml='<model unit="millimeter" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources><object id="1" type="model"><mesh><vertices>'+''.join(f'<vertex x="{x:.9f}" y="{y:.9f}" z="{zz:.9f}"/>' for x,y,zz in v)+'</vertices><triangles>'+''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a,b,c in f)+'</triangles></mesh></object></resources><build><item objectid="1"/></build></model>'
 with zipfile.ZipFile(EXP/f'eye-ring-{mode}.3mf','w',zipfile.ZIP_DEFLATED) as zz:
  zz.writestr('3D/3dmodel.model',xml);zz.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>');zz.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
print('EXPORTED',flush=True)
