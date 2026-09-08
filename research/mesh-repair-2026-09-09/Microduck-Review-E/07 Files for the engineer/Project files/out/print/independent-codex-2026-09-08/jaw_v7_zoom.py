from pathlib import Path
source=Path(__file__).with_name('analyze_v7.py').read_text();exec(source.split('# Independent software')[0]);parser=source[source.index('# Parse actual motion'):source.index("print('Parsed'")];parser=parser.replace("text=z.read('Metadata/plate_1.gcode').decode()", "text=z.read('Metadata/plate_1.gcode').decode().split('; CHANGE_LAYER')[0]+'; CHANGE_LAYER'+'; CHANGE_LAYER'.join(z.read('Metadata/plate_1.gcode').decode().split('; CHANGE_LAYER')[1:5])");exec(parser)
fig,axes=plt.subplots(1,4,figsize=(13,11));m=meshes[2][1]
for ax,i in zip(axes,range(4)):
 seg=trimesh.intersections.mesh_plane(m,[0,0,1],[0,0,layers[i]['z']-.1]);ax.add_collection(LineCollection(seg[:,:,:2],colors='#e87900',linewidths=1,linestyles='dashed'))
 for o,f,w,zv,s in layers[i]['moves']:
  if o==16:ax.add_collection(LineCollection(s,colors='#aaa' if f.startswith('Support') else '#156499',linewidths=.7))
 ax.set(xlim=(-1,37),ylim=(105,204),aspect='equal',title=f'Side jaw L{i+1} Z{layers[i]["z"]}')
fig.suptitle('HEAD-V7: jaw on its side; mesh orange, actual model blue, support grey\nNo unsupported broad layer-2 underside expansion');fig.tight_layout();fig.savefig(OUT/'jaw-first-layers-v7.png',dpi=170)
