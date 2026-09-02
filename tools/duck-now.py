"""duck-now — the whole duck in its CURRENT form: every part that has a
PASSing refcheck drawn in orange from its latest passing round, everything
else drawn as Pollen's reference mesh in grey, all placed by spec/mesh-
placements via placements.json. Kernel-free (FreeCAD python for numpy).
Leif, 2026-09-01: "can you show me the current version of it? the whole
duck in its current form."
"""
import sys, os, json, glob
sys.path.insert(0, '/Users/leifrydenfalk/dev/ce-workshop/ce-cad')
from cecad import mjcf, meshview
import numpy as np
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
place = json.load(open(root + '/ce-assemblies/microduck/current/placements.json'))['record']['rows']
m2p = json.load(open(root + '/spec/mesh-to-part.json'))['map']
def latest_pass(slug):
    best = None
    for rep in glob.glob(root + f'/out/refcheck/{slug}/r*/report.md') + glob.glob(root + f'/ce-parts/{slug}/iterations/*/evidence/refcheck/*/report.md'):
        if open(rep).read().startswith('# refcheck') and '**PASS**' in open(rep).read():
            stl = os.path.join(os.path.dirname(rep), 'ours.stl')
            if os.path.exists(stl) and (best is None or os.path.getmtime(stl) > os.path.getmtime(best)):
                best = stl
    return best
ours, ref, passed = {}, {}, set()
cache = {}
for i, p in enumerate(place):
    mesh = p['mesh']; slug = (p['part'] or 'part:?').split(':')[1]
    R = mjcf.quat_to_mat(p['world_quat_wxyz']); t = [x / 1000.0 for x in p['world_pos_mm']]
    stl = latest_pass(slug)
    if stl:
        key = ('ours', stl)
        if key not in cache: cache[key] = [tuple(tuple(c / 1000.0 for c in v) for v in tri) for tri in mjcf.read_stl(stl)]
        ours[f'{slug}#{i}'] = mjcf._xform_tris(cache[key], R, t); passed.add(slug)
    else:
        for d in ('reference/pollen-microduck-simulator/meshes', 'reference/pollen-microduck-rl/assets'):
            pth = f'{root}/{d}/{mesh}.stl'
            if os.path.exists(pth):
                key = ('ref', pth)
                if key not in cache: cache[key] = mjcf.read_stl(pth)
                ref[f'{mesh}#{i}'] = mjcf._xform_tris(cache[key], R, t); break
groups = {}; colors = {}; alphas = {}
for k, v in ref.items(): groups[k] = v; colors[k] = '#8c9298'
for k, v in ours.items(): groups[k] = v; colors[k] = '#f28c28'
out = root + '/out/render'
os.makedirs(out, exist_ok=True)
title = f'Microduck NOW — {len(passed)} parts rebuilt & PASS (orange), rest = Pollen reference (grey): ' + ', '.join(sorted(passed))
for v in ('iso', 'left', 'front'):
    r = meshview.render_groups(groups, f'{out}/duck-now_{v}.png', view=v, colors=colors, size=(1200, 1200), title=title[:140])
    print(v, r['tris'])
json.dump({'passed': sorted(passed), 'placements_ours': len(ours), 'placements_ref': len(ref)}, open(f'{out}/duck-now.json', 'w'), indent=1)
print('passed', sorted(passed))
