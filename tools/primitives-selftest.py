from cecad import *
import math
def circ(r, n=12): return [(r*math.cos(2*math.pi*i/n), r*math.sin(2*math.pi*i/n)) for i in range(n)]
q = Part("loft2", material="PLA")
q.loft([(circ(20), 0), (circ(35), 40), (circ(25), 70), (circ(1.5), 85)])
v0 = q.volume
q.shell(2.0, open=lambda f: abs(f.BoundBox.ZMax) < 1e-6)
print("shelled: vol", round(v0,1), "->", round(q.volume,1), "valid", q.shape.isValid(), "faces", len(q.shape.Faces))
r = Part("hollow", material="PLA").ellipsoid(50, 50, 70)
v0 = r.volume; r.ellipsoid(47, 47, 67, op="cut")
print("hollow ellipsoid vol", round(v0,1), "->", round(r.volume,1), "valid", r.shape.isValid())
r.scale(2.0, 1.0, 1.0); print("scaled bbox", r.bbox)
m = Part.from_mesh("/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck/reference/pollen-microduck-simulator/meshes/top_head_shell.stl", scale=1000)
print("mesh part", m.name, "bbox", m.bbox, "vol", round(m.volume,1), "faces", len(m.shape.Faces), "notes", m.notes)
a = Assembly("t"); a.add("q", q); a.add("r", r.move(100,0,0)); a.add("m", m.move(0,150,0))
render(a, "/private/tmp/claude-501/-Users-leifrydenfalk/191ca988-e752-45fb-a6f7-89dde34532e7/scratchpad/microduck/tooltest/prims.png", view="iso", title="new primitives")
