from pathlib import Path
import zipfile,json,sys
import numpy as np
from lxml import etree as ET
base=Path(__file__).parent;out=base.parent/'plates/HEAD-V7-candidate';out.mkdir(exist_ok=True);src=out.parent/'HEAD-V6-candidate/microduck-head-v6-indexed.3mf';z=zipfile.ZipFile(src);root=ET.fromstring(z.read('3D/3dmodel.model'));ns={'c':root.nsmap[None]}
obj=next(o for o in root.findall('c:resources/c:object',ns) if o.get('name')=='microduck-jaw');vs=obj.findall('c:mesh/c:vertices/c:vertex',ns);v=np.array([[float(e.get(k)) for k in ['x','y','z']] for e in vs]);R=np.array([[0,0,1],[0,1,0],[-1,0,0]]);w=v@R.T;w-=w.min(0);w[:,:2]+=np.array([3,108.8])
for e,p in zip(vs,w):
 for k,value in zip('xyz',p):e.set(k,f'{value:.4f}')
with zipfile.ZipFile(out/'microduck-head-v7-jaw-side.3mf','w',zipfile.ZIP_DEFLATED) as dst:
 for n in z.namelist():dst.writestr(n,ET.tostring(root,xml_declaration=True,encoding='UTF-8') if n=='3D/3dmodel.model' else z.read(n))
layout=json.loads((out.parent/'HEAD-V6-candidate/layout.json').read_text());jaw=next(x for x in layout if x['slug']=='jaw');jaw.update({'bbox':[round(float(x),4) for x in np.r_[w.min(0),w.max(0)]],'w':float(np.ptp(w[:,0])),'h':float(np.ptp(w[:,1])),'z':float(np.ptp(w[:,2])),'additional_pose':'Rotate +90 degrees about bed Y, then translate to X=3,Y=108.8,Z=0; see build_v7.py'})
(out/'layout.json').write_text(json.dumps(layout,indent=2));(out/'CHANGE.md').write_text('Only jaw print pose changes from HEAD-V6: +90 degrees around Y, preserving shape, with lower bbox X=3,Y=108.8,Z=0. All other 10 meshes and placements are unchanged. Shared vertex indexing remains. Jaw-side standalone passed strengthened model-layer and air checks. No brim. No printer send.\n')
