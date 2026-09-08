"""Place the two repaired TPU meshes without changing their surfaces."""
from pathlib import Path
import sys,struct,json,zipfile,hashlib
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'tools'))
from indexed_3mf import mesh_xml
out=Path(__file__).parent
flat="--flat" in sys.argv
flip="--flip" in sys.argv
if flip:out=out/"flipped"
if flat:out=out/"flat"
out.mkdir(exist_ok=True)
objects=[];items=[];settings=[];proof=[]
for index,(name,xy) in enumerate([('microduck-jaw-soft',(40,40)),('microduck-soft-mouth-top',(40,95))],1):
 p=ROOT/'out/print/stl/fixed/TPU'/f'{name}.stl';b=p.read_bytes();n=struct.unpack_from('<I',b,80)[0]
 vertices=[struct.unpack_from('<fff',b,84+i*50+12+j*12) for i in range(n) for j in range(3)]
 if flip:vertices=[(x,-y,-z) for x,y,z in vertices]
 if flat:
  import math
  angle=math.radians(179.5);c=math.cos(angle);s=math.sin(angle)
  vertices=[(x,c*y-s*z,s*y+c*z) for x,y,z in vertices]
 mins=[min(v[k] for v in vertices) for k in range(3)];offset=[xy[0]-mins[0],xy[1]-mins[1],-mins[2]]
 placed=[tuple(v[k]+offset[k] for k in range(3)) for v in vertices]
 objects.append(f'<object id="{index}" type="model">{mesh_xml(placed)}</object>')
 items.append(f'<item objectid="{index}" printable="1"/>')
 settings.append(f'<object id="{index}"><metadata key="name" value="{name}"/><metadata key="extruder" value="1"/></object>')
 proof.append(dict(name=name,source=str(p),sha256=hashlib.sha256(b).hexdigest(),triangles=n,translation_mm=offset,bounds_mm=[(min(v[k] for v in placed),max(v[k] for v in placed)) for k in range(3)],operation=('179.5 degrees about X to seat measured broad planar face, then translation' if flat else ('180 degrees about X, then translation' if flip else 'Rigid translation only'))+'; shared vertex indices at 0.0001mm serialization precision'))
model='<model unit="millimeter" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources>'+''.join(objects)+'</resources><build>'+''.join(items)+'</build></model>'
source=ROOT/'out/print/plates/HEAD-V5/microduck-head-v5.gcode.3mf'
with zipfile.ZipFile(source) as z:
 cfg=json.loads(z.read('Metadata/project_settings.config'))
 cfg.update(filament_type=['TPU'],filament_settings_id=['Generic TPU @BBL H2D'],filament_map=['2'],filament_map_mode='Manual',nozzle_diameter=['0.4','0.6'],printer_settings_id='Bambu Lab H2D 0.6 nozzle',print_settings_id='0.18mm Balanced Quality @BBL H2D 0.6 nozzle')
 with zipfile.ZipFile(out/'microduck-mouth-tpu.3mf','w',zipfile.ZIP_DEFLATED) as w:
  for n in ('[Content_Types].xml','_rels/.rels'):w.writestr(n,z.read(n))
  w.writestr('3D/3dmodel.model',model)
  w.writestr('Metadata/project_settings.config',json.dumps(cfg))
  w.writestr('Metadata/model_settings.config','<config>'+''.join(settings)+'<plate><metadata key="plater_id" value="1"/></plate></config>')
(out/'geometry-proof.json').write_text(json.dumps(proof,indent=2))
print(json.dumps(proof,indent=2))
