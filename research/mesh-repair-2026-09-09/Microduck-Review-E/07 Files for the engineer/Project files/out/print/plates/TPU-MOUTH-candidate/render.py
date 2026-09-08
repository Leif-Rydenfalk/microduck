from pathlib import Path
import sys,zipfile,json
import numpy as np,trimesh,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
sys.path.insert(0,'/Users/leifrydenfalk/dev/ce-workshop/ce-print-scheduler')
from scheduler.validate import _embedded_meshes,_parse_gcode
from scheduler.meshdoctor import census
out=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).parent
proof=json.loads((out/'geometry-proof.json').read_text())
(out/'meshdoctor.json').write_text(json.dumps([census(p['source']) for p in proof],indent=2))
with zipfile.ZipFile(out/'microduck-mouth-tpu.3mf') as z:meshes=_embedded_meshes(z)
fig=plt.figure(figsize=(12,5))
for i,m in enumerate(meshes):
 a=np.array(m['triangles']);v=a.reshape(-1,3);f=np.arange(len(v)).reshape(-1,3)
 ax=fig.add_subplot(1,2,i+1,projection='3d');ax.plot_trisurf(v[:,0],v[:,1],v[:,2],triangles=f,color='#498caf',linewidth=0,antialiased=False)
 ax.set_box_aspect(np.ptp(v,axis=0));ax.view_init(elev=40,azim=-80);ax.set_title(proof[i]['name']);ax.set_xlabel('X mm');ax.set_ylabel('Y mm');ax.set_zlabel('Z mm')
fig.suptitle('Actual repaired TPU mouth meshes — positioned on H2D bed, no shape changes');fig.tight_layout();fig.savefig(out/'mouth-meshes.png',dpi=140);plt.close(fig)
plates=list((out/'sliced').glob('*.gcode.3mf'))
if plates:
 with zipfile.ZipFile(plates[0]) as z:
  code=z.read('Metadata/plate_1.gcode').decode();cfg,hdr,layers=_parse_gcode(code)
 fig,axs=plt.subplots(2,4,figsize=(16,9))
 for ax,i in zip(axs.flat,[0,1,2,3,7,15,len(layers)//2,len(layers)-1]):
  layer=layers[i]
  for label,segs in layer['objects'].items():ax.add_collection(LineCollection(np.array(segs).reshape(-1,2,2),colors='#b0b0b0',linewidths=.5))
  for label,segs in layer['model_objects'].items():ax.add_collection(LineCollection(np.array(segs).reshape(-1,2,2),colors='#126296',linewidths=.7))
  ax.set(xlim=(30,140),ylim=(30,140),aspect='equal',title=f'Layer {i+1} / {len(layers)}, Z {layer["z"]}')
 fig.suptitle('Actual TPU toolpaths: model blue, support grey. Source archive, not slicer thumbnail.');fig.tight_layout();fig.savefig(out/'mouth-toolpaths.png',dpi=150)
