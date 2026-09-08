from pathlib import Path
source=Path(__file__).with_name('analyze_v6.py').read_text()
exec(source.split('# Independent software')[0])
exec(source[source.index('# Parse actual motion'):source.index("print('Parsed'")])
fig,axes=plt.subplots(2,4,figsize=(17,10))
for ax,i in zip(axes.flat,[0,17,40,45,94,95,97,98]):
 mid=6 if i in [0,17,40,45] else 1;m=meshes[mid][1];segs=trimesh.intersections.mesh_plane(m,[0,0,1],[0,0,layers[i]['z']-.1]);ax.add_collection(LineCollection(segs[:,:,:2],colors='#df7900',linewidths=1.3,linestyles='dashed'))
 for obj,feat,w,zv,seg in layers[i]['moves']:ax.add_collection(LineCollection(seg,colors='#bbb' if feat.startswith('Support') else '#126296',linewidths=1))
 if mid==6:ax.set(xlim=(76,110),ylim=(157,191),aspect='equal',title=f'Eye ring layer {i+1}, Z {layers[i]["z"]}')
 else:ax.set(xlim=(188,211),ylim=(11,20),aspect='equal',title=f'Bottom shell layer {i+1}, Z {layers[i]["z"]}')
fig.suptitle('HEAD-V6: exact mesh section (orange dashed) versus actual model extrusion (blue), support grey\nShared-vertex candidate; compare repaired eye-ring and bottom-shell layers');fig.tight_layout();fig.savefig(OUT/'mesh-versus-extrusion-v6.png',dpi=180)
# Per-object material volume comes from actual E, not a mass estimate; here use path count/length for clear omissions.
for oid in [32,12]:
 rows=[]
 for i,l in enumerate(layers):
  model=[s for o,f,w,z,s in l['moves'] if o==oid and not f.startswith('Support')]
  if model:rows.append({'layer':i+1,'model_path_mm':float(sum(np.linalg.norm(s[:,1]-s[:,0],axis=1).sum() for s in model))})
 (OUT/f'object-{oid}-actual-model-paths.json').write_text(json.dumps(rows,indent=2))
print('DONE')
