from pathlib import Path
exec(Path(__file__).with_name('analyze.py').read_text().split('# Independent software')[0])
import FreeCAD,Mesh
rows=[]
for name,m in meshes:
 fm=Mesh.Mesh(m.triangles.reshape((-1,3)).tolist());bad=fm.getSelfIntersections();r={'name':name,'self_intersection_output_count':len(bad),'self_intersections':repr(bad),'freecad_isSolid':fm.isSolid()};rows.append(r);print(json.dumps(r),flush=True)
(OUT/'freecad-intersections.json').write_text(json.dumps(rows,indent=2))
