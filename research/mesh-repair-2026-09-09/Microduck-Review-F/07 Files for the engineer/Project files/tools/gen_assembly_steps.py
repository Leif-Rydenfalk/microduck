"""gen_assembly_steps.py — a render per assembly step for the release manual:
the robot grows step by step, the parts ADDED this step in orange, everything
already built in light grey, on white. Clean (back-face cull). Leif, 2026-09-02:
"assembly must be with generated drawings with visuals for how to assemble."
"""
import os, sys, json
sys.path.insert(0, '/Users/leifrydenfalk/dev/ce-workshop/ce-cad')
from cecad import mjcf, meshview
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
place = json.load(open(root + '/spec/mesh-placements.json'))
# cumulative body sets per step (MJCF body names)
STEPS = [
    ("1 · Trunk", ["trunk_base"]),
    ("2 · Hips", ["yaw2roll", "bearing_roll", "hip_l", "hip_l_2"]),
    ("3 · Legs", ["upper_leg_left", "upper_leg_right", "leg", "leg_2", "ankle_left", "ankle_right"]),
    ("4 · Neck", ["neck"]),
    ("5 · Head", ["neck_pitch", "yaw_roll_motion", "jaw_soft"]),
]
# gather tris per body (mesh + placement)
def tris_of(body):
    out = []
    for mesh, rows in place.items():
        for r in rows:
            if r["body"] != body:
                continue
            for d in ("reference/pollen-microduck-rl/assets", "reference/pollen-microduck-simulator/meshes"):
                p = f"{root}/{d}/{mesh}.stl"
                if os.path.exists(p):
                    R = mjcf.quat_to_mat(r["quat_wxyz"]); t = [x/1000.0 for x in r["pos_mm"]]
                    out.append(mjcf._xform_tris(mjcf.read_stl(p), R, t)); break
    return [tri for m in out for tri in m]
cache = {}
def body_tris(b):
    if b not in cache: cache[b] = tris_of(b)
    return cache[b]
built = []
os.makedirs(root + '/out/assembly', exist_ok=True)
for i, (title, bodies) in enumerate(STEPS, 1):
    groups, colors = {}, {}
    for b in built:
        groups["old/"+b] = body_tris(b); colors["old/"+b] = "#c8ccd0"
    for b in bodies:
        groups["new/"+b] = body_tris(b); colors["new/"+b] = "#e8871a"
    groups = {k: v for k, v in groups.items() if v}
    r = meshview.render_groups(groups, f"{root}/out/assembly/step{i}.png", view="iso",
                               colors=colors, size=(1000, 1000), bg="#ffffff", cull=True,
                               title=f"Assembly {title} — new parts in orange")
    print("step", i, title, r["tris"])
    built += bodies
# a final full assembly on white + an exploded-ish separated view
allb = [b for _, bs in STEPS for b in bs]
groups = {b: body_tris(b) for b in allb}
groups = {k: v for k, v in groups.items() if v}
mats = {m: (rows[0].get("material_rgba") or [.75,.75,.75,1]) for m, rows in place.items()}
# colour whole robot by material per body's first mesh
bcol = {}
for m, rows in place.items():
    bcol.setdefault(rows[0]["body"], m)
def hexof(b):
    m = bcol.get(b); r = mats.get(m) or [.75,.75,.75,1]
    return "#%02x%02x%02x" % tuple(int(255*c) for c in r[:3])
r = meshview.render_groups(groups, f"{root}/out/assembly/assembled.png", view="iso",
                           colors={b: hexof(b) for b in groups}, size=(1100,1100),
                           bg="#ffffff", cull=True, title="Assembled — Microduck")
print("assembled", r["tris"])
