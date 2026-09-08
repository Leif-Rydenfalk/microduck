from pathlib import Path
source=Path(__file__).with_name('analyze_v9.py').read_text();exec(source.split('# Independent software')[0]);parser=source[source.index('# Parse actual motion'):source.index("print('Parsed'")];full=z.read('Metadata/plate_1.gcode').decode().split('; CHANGE_LAYER');fig,axes=plt.subplots(2,4,figsize=(17,12))
for ax,(mi,oid,li,kind) in zip(axes.flat,[(7,36,1,'bracket'),(7,36,2,'bracket'),(7,36,89,'bracket'),(7,36,90,'bracket'),(2,16,1,'jaw'),(2,16,2,'jaw'),(5,28,57,'yaw'),(5,28,60,'yaw')]):
 textpart='G90\nM83\n; CHANGE_LAYER'+full[li];exec(parser.replace("text=z.read('Metadata/plate_1.gcode').decode()",'text=textpart'));l=layers[0];segs=trimesh.intersections.mesh_plane(meshes[mi][1],[0,0,1],[0,0,l['z']-.1]);ax.add_collection(LineCollection(segs[:,:,:2],colors='#e87900',linewidths=1.1,linestyles='dashed'))
 for o,f,w,zv,s in l['moves']:
  if o==oid:ax.add_collection(LineCollection(s,colors='#aaa' if f.startswith('Support') else '#156499',linewidths=.65))
 if kind=='bracket':ax.set(xlim=(148,192),ylim=(118,162),aspect='equal')
 elif kind=='jaw':ax.set(xlim=(0,36),ylim=(106,203),aspect='equal')
 else:ax.set(xlim=(109,116),ylim=(113,119),aspect='equal')
 ax.set_title(f'{kind} L{li} Z{l["z"]} mm')
fig.suptitle('Exact final HEAD-V9: mesh sections orange; actual model paths blue, support grey\nBracket final slab present; jaw on side; yaw zero-volume component removed');fig.tight_layout();fig.savefig(OUT/'changed-parts-layer-proof.png',dpi=170)
