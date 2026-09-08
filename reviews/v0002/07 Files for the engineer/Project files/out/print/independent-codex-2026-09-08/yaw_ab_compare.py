import zipfile,json,re,math
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
out=Path(__file__).parent/'experiments';src=Path(__file__).with_name('analyze.py').read_text();parser=src[src.index('# Parse actual motion'):src.index("print('Parsed'")];runs=[]
for name in ['yaw-original','yaw-cleaned']:
 z=zipfile.ZipFile(out/(name+'-3mf')/(name+'.gate.gcode.3mf'));exec(parser);runs.append(layers)
rows=[]
for i,(a,b) in enumerate(zip(*runs)):
 clouds=[]
 for l in [a,b]:
  pts=[]
  for o,f,w,zv,s in l['moves']:
   if not f.startswith('Support'):
    for x,y in s:pts.extend(np.linspace(x,y,max(2,int(np.linalg.norm(y-x)/.05)+1)))
  clouds.append(np.array(pts))
 pa,pb=clouds;ab=cKDTree(pb).query(pa)[0];ba=cKDTree(pa).query(pb)[0];rows.append({'layer':i+1,'z':a['z'],'model_max_symmetric_sample_distance_mm':float(max(ab.max(),ba.max()))})
proof={'layers':[len(r) for r in runs],'max_model_path_distance_mm':max(r['model_max_symmetric_sample_distance_mm'] for r in rows),'layers_detail':rows};(out/'yaw-ab-path-proof.json').write_text(json.dumps(proof,indent=2))
fig,axes=plt.subplots(1,3,figsize=(14,5))
for ax,i in zip(axes,[56,59,62]):
 for ri,r in enumerate(runs):
  for o,f,w,zv,s in r[i]['moves']:
   if not f.startswith('Support'):ax.add_collection(LineCollection(s,colors='#e87900' if ri==0 else '#156499',linewidths=1.7 if ri==0 else .7))
 ax.set(xlim=(109,116),ylim=(113,119),aspect='equal',title=f'Yaw layer{i+1}, Z{runs[0][i]["z"]}')
fig.suptitle('Zero-volume component removal A/B: original paths orange, cleaned blue\nBoth checked slices; no geometry added to the volumetric body');fig.tight_layout();fig.savefig(out/'yaw-zero-volume-ab.png',dpi=170);print('MAX PATH DISTANCE',proof['max_model_path_distance_mm'])
