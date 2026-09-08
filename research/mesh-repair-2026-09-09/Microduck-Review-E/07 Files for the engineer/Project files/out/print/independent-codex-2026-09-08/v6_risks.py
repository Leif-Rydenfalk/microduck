from pathlib import Path
source=Path(__file__).with_name('analyze_v6.py').read_text();exec(source.split('# Independent software')[0]);exec(source[source.index('# Parse actual motion'):source.index("print('Parsed'")])
fig,axes=plt.subplots(2,4,figsize=(17,11))
for ax,(mi,i) in zip(axes.flat,[(2,0),(2,1),(2,2),(2,3),(7,197),(7,198),(7,199),(7,200)]):
 m=meshes[mi][1];segs=trimesh.intersections.mesh_plane(m,[0,0,1],[0,0,layers[i]['z']-.1]);ax.add_collection(LineCollection(segs[:,:,:2],colors='#e87900',linewidths=1,linestyles='dashed'))
 for o,f,w,zv,s in layers[i]['moves']:ax.add_collection(LineCollection(s,colors='#aaa' if f.startswith('Support') else ('#ce263e' if 'Bridge' in f else '#156499'),linewidths=.6))
 if mi==2:ax.set(xlim=(0,76),ylim=(105,204),aspect='equal',title=f'Jaw layer{i+1} Z{layers[i]["z"]}')
 else:ax.set(xlim=(272,295),ylim=(37,49),aspect='equal',title=f'Bracket layer{i+1} Z{layers[i]["z"]}')
fig.suptitle('HEAD-V6 unresolved checks: mesh orange, model blue, bridges red, support grey');fig.tight_layout();fig.savefig(OUT/'jaw-bracket-risks.png',dpi=170)
m=meshes[2][1];idx=np.argsort(m.area_faces)[-15:];print('LARGEST JAW FACES',[(float(m.area_faces[i]),m.triangles[i].tolist()) for i in idx],flush=True)
for i in [0,1,2,3]:
 from collections import Counter
 print('JAW',i+1,Counter(f for o,f,w,zv,s in layers[i]['moves'] if o==16),flush=True)
