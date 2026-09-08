"""Refresh an unissued review from explicit revised CAD meshes and MJCF frames."""
import argparse,csv,json,shutil,sys,hashlib,re
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parents[1]/'ce-cad'))
from cecad.reviewpack import stl_mesh,viewer,write_mesh_stl,csvwrite,sha

def refresh(out):
 fixes={'microduck-upper-leg-left':'research/mesh-repair-2026-09-09/indexed-cavity','microduck-upper-leg-right':'research/mesh-repair-2026-09-09/indexed-cavity','microduck-yaw-roll-motion':'research/mesh-repair-2026-09-09/yaw-rebuild','microduck-hip-bracket':'research/mesh-quality-2026-09-09','microduck-power-support':'research/mesh-quality-2026-09-09'}
 rows=list(csv.DictReader((out/'PARTS.csv').open(encoding='utf-8-sig')));sources=list(csv.DictReader((out/'SOURCE FILES.csv').open(encoding='utf-8-sig')))
 placements=json.loads((ROOT/'ce-assemblies/microduck/current/placements.json').read_text())['record']['rows'];assembly=json.loads((out/'01 See the robot/Published assembly mesh.json').read_text());proof=[]
 for row in rows:
  slug=row['slug']
  if slug not in fixes:continue
  src=ROOT/fixes[slug]/(slug+'.stl');target=out/row['stl'];shutil.copyfile(src,target);shutil.copyfile(src.with_suffix('.step'),target.with_suffix('.step'));m=stl_mesh(target);vertices=np.array(m['positions']).reshape(-1,3)
  viewer(target.parent/'Look at this part.html',{'parts':[m],'units':'mm'},row['part'],'Part for engineering review / 工程评审零件','../../START HERE.html')
  row.update(source_kind='Current CAD revision',source_path=str(src.relative_to(ROOT)),triangles=len(vertices)//3,measured_bbox_mm=str(np.ptp(vertices,axis=0).tolist()),manifest_bounds_match='Superseded by current CAD revision')
  for s in sources:
   if s['file']==row['stl']:s.update(source=str(src.relative_to(ROOT)),bytes=target.stat().st_size,sha256=sha(target),note='Current CAD export; revision details in engineer appendix')
  for i,place in enumerate(placements):
   if place['part']!='part:'+slug:continue
   name=place['body']+'/'+slug+'#'+str(i);part=next(p for p in assembly['parts'] if p['name']==name)
   w,x,y,z=np.array(place['world_quat_wxyz'])/np.linalg.norm(place['world_quat_wxyz']);rot=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
   world=vertices@rot.T+place['world_pos_mm'];part.update(positions=world.reshape(-1).tolist(),indices=list(range(len(vertices))),edges=[],tris=len(vertices)//3)
  proof.append({'part':slug,'source':str(src.relative_to(ROOT)),'sha256':sha(src),'triangles':len(vertices)//3})
 csvwrite(out/'PARTS.csv',rows);csvwrite(out/'SOURCE FILES.csv',sources)
 assembly['review_revision']='Five current CAD exports placed through source MJCF frames';(out/'01 See the robot/Published assembly mesh.json').write_text(json.dumps(assembly,separators=(',',':')))
 viewer(out/'01 See the robot/Turn the robot around.html',assembly,'Microduck — look around','Engineering review / 工程评审','../START HERE.html');write_mesh_stl(assembly,out/'01 See the robot/Whole robot - view only.stl')
 appendix=out/'07 Files for the engineer/Geometry revisions';appendix.mkdir(exist_ok=True);(appendix/'Current revisions.json').write_text(json.dumps(proof,indent=2));shutil.copyfile(ROOT/'research/mesh-repair-2026-09-09/THIGH-REPAIR-CHECK.json',appendix/'Upper leg checks.json')
 for name in ['START HERE.html','PARTS.html']:
  p=out/name;s=p.read_text();s=re.sub(r'<section><h2>Part 29: mesh gaps repaired.*?</section>','',s,flags=re.S);s=s.replace('Microduck Review C','Microduck Review D');p.write_text(s)
 print(json.dumps(proof,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);refresh(p.parse_args().out)
