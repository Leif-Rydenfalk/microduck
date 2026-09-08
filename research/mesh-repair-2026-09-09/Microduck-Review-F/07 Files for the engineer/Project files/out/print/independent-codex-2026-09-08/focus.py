from pathlib import Path
exec(Path(__file__).with_name('analyze.py').read_text().split('# Independent software')[0])
from matplotlib.collections import LineCollection
fig,axes=plt.subplots(2,4,figsize=(17,9))
for ax,h in zip(axes.flat,[.1,.3,.5,.7,1.1,1.5,1.9,2.3]):
 m=meshes[6][1];segs=trimesh.intersections.mesh_plane(m,[0,0,1],[0,0,h]);ax.add_collection(LineCollection(segs[:,:,:2],linewidths=1));ax.set(xlim=(76,110),ylim=(157,191),aspect='equal',title=f'Actual mesh section at Z {h} mm')
fig.tight_layout();fig.savefig(OUT/'eye-ring-mesh-sections.png',dpi=160)
m=meshes[5][1];components=m.split(only_watertight=False);d={'components':[]}
for c in components:
 d['components'].append({'faces':len(c.faces),'bounds':c.bounds.tolist(),'volume':float(c.volume),'area':float(c.area),'vertices':c.vertices.tolist() if len(c.faces)<20 else None,'triangles':c.faces.tolist() if len(c.faces)<20 else None})
(OUT/'yaw-zero-volume.json').write_text(json.dumps(d,indent=2));print(json.dumps(d),flush=True)
