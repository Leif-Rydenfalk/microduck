from pathlib import Path
source=Path(__file__).with_name('analyze_v6.py').read_text();exec(source.split('# Independent software')[0]);parser=source[source.index('# Parse actual motion'):source.index("print('Parsed'")];parser=parser.replace("text=z.read('Metadata/plate_1.gcode').decode()", "text='G90\\nM83\\n; CHANGE_LAYER'+ '; CHANGE_LAYER'.join(z.read('Metadata/plate_1.gcode').decode().split('; CHANGE_LAYER')[198:202])");exec(parser)
fig,axes=plt.subplots(1,4,figsize=(16,5));m=meshes[7][1]
for ax,i in zip(axes,range(4)):
 seg=trimesh.intersections.mesh_plane(m,[0,0,1],[0,0,layers[i]['z']-.1]);ax.add_collection(LineCollection(seg[:,:,:2],colors='#e87900',linewidths=1.2,linestyles='dashed'))
 for o,f,w,zv,s in layers[i]['moves']:
  if o==36:ax.add_collection(LineCollection(s,colors='#aaa' if f.startswith('Support') else '#156499',linewidths=1.2))
 ax.set(xlim=(278,289),ylim=(20,25),aspect='equal',title=f'Bracket L{i+198}, Z{layers[i]["z"]}')
fig.suptitle('Terminal bracket wedge: mesh orange; actual model blue. Last section width0.118mm <0.4mm nozzle');fig.tight_layout();fig.savefig(OUT/'bracket-terminal-wedge.png',dpi=170)
