from pathlib import Path
source=Path(__file__).with_name('analyze_v7.py').read_text();exec(source.split('# Independent software')[0]);parser=source[source.index('# Parse actual motion'):source.index("print('Parsed'")];full=z.read('Metadata/plate_1.gcode').decode().split('; CHANGE_LAYER');fig,axes=plt.subplots(2,2,figsize=(12,10));rows=[]
patches=[('bottom-shell',1,12,50,(191.62,89.88)),('jaw-left',2,16,28,(5.33,113.9)),('jaw-right',2,16,28,(5.33,195.08)),('yaw-roll',5,28,36,(107.355,112.8))]
for ax,(name,mi,oid,li,patch_xy) in zip(axes.flat,patches):
 textpart='G90\nM83\n; CHANGE_LAYER'+full[li]
 code=parser.replace("text=z.read('Metadata/plate_1.gcode').decode()",'text=textpart');exec(code);l=layers[0];plane=l['z']-.1;segments=trimesh.intersections.mesh_plane(meshes[mi][1],[0,0,1],[0,0,plane]);ax.add_collection(LineCollection(segments[:,:,:2],colors='#e87900',linewidths=1.5,linestyles='dashed'));points=[]
 for o,f,w,zv,s in l['moves']:
  if o==oid and not f.startswith('Support'):
   ax.add_collection(LineCollection(s,colors='#156499',linewidths=1));
   for a,b in s:points.extend(np.linspace(a,b,max(2,int(np.linalg.norm(b-a)/.03)+1)))
 contours=[]
 for a,b in segments[:,:,:2]:contours.extend(np.linspace(a,b,max(2,int(np.linalg.norm(b-a)/.03)+1)))
 contours=np.array(contours);center=np.array(patch_xy);local=contours[np.linalg.norm(contours-center,axis=1)<1.5];dist=cKDTree(np.array(points)).query(local)[0] if len(local) else np.array([])
 rows.append({'part':name,'layer':li,'mesh_sample_z':plane,'intersection_xy':center.tolist(),'section_samples_within_1_5mm':len(local),'max_section_to_model_centerline_mm':float(dist.max()) if len(dist) else None,'median_mm':float(np.median(dist)) if len(dist) else None})
 ax.scatter(*center,c='red',s=45,marker='x');ax.set(xlim=(center[0]-2,center[0]+2),ylim=(center[1]-2,center[1]+2),aspect='equal',title=f'{name}: L{li}, section Z{plane:.1f} mm')
fig.suptitle('Tiny self-intersection neighborhoods: mesh section orange; actual model paths blue\nRed marker: diagnostic intersection location projected into section; finite nozzle resolution remains');fig.tight_layout();fig.savefig(OUT/'intersection-functional-sections.png',dpi=180);(OUT/'intersection-functional-sections.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
