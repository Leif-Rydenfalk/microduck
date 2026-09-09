"""FreeCAD side of export_bundles.py. Run under freecadcmd, never plain python3.

    freecadcmd tools/export_assembly_step.py <job.json>

The job names candidate STEP files per part slug, the placed pieces of the
published assembly mesh (world mm) and the scene tree. It verifies every
candidate STEP against the STL Ming already has (bounding box and volume),
writes verified single-part STEPs, and writes one positioned assembly STEP of
the verified solids. Results go to job['result'] as JSON. Unverified parts are
reported, never substituted with mesh-derived solids.
"""
import json, math, os, sys
import FreeCAD, Part, Import

job = json.load(open(sys.argv[-1]))
TOL_BBOX = job.get('tol_bbox_mm', 0.5)
TOL_VOL = job.get('tol_volume_fraction', 0.03)


def tight(shape):
    """OCC's BoundBox is loose around B-spline faces; use the optimal box when available."""
    try:
        return shape.optimalBoundingBox(True, False)
    except Exception:
        return shape.BoundBox


def stl_stats(path):
    m = __import__('Mesh').Mesh(path)
    b = m.BoundBox
    return [b.XLength, b.YLength, b.ZLength], m.Volume, [b.XMin, b.YMin, b.ZMin]


def quat_matrix(q):  # MuJoCo w,x,y,z -> 3x3
    w, x, y, z = q
    n = math.sqrt(w*w+x*x+y*y+z*z) or 1.0
    w, x, y, z = w/n, x/n, y/n, z/n
    return [[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
            [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
            [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]]


def compose(a, b):  # a ∘ b, each (R, t)
    Ra, ta = a; Rb, tb = b
    R = [[sum(Ra[i][k]*Rb[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    t = [sum(Ra[i][k]*tb[k] for k in range(3))+ta[i] for i in range(3)]
    return R, t


def placement(R, t):
    M = FreeCAD.Matrix(R[0][0], R[0][1], R[0][2], t[0],
                       R[1][0], R[1][1], R[1][2], t[1],
                       R[2][0], R[2][1], R[2][2], t[2], 0, 0, 0, 1)
    return FreeCAD.Placement(M)


result = {'parts': {}, 'assembly': None}
shapes = {}
for slug, cand in job['candidates'].items():
    rec = {'step': cand['step'], 'stl': cand['stl'], 'verified': False}
    try:
        sh = Part.read(cand['step'])
        bb = tight(sh)
        sb, sv, _ = stl_stats(cand['stl'])
        rec.update(step_bbox=[bb.XLength, bb.YLength, bb.ZLength], stl_bbox=sb,
                   step_volume=sh.Volume, stl_volume=sv, solids=len(sh.Solids), valid=sh.isValid())
        dbb = max(abs(a-b) for a, b in zip(rec['step_bbox'], sb))
        dvol = abs(sh.Volume-sv)/max(sv, 1e-9)
        rec.update(bbox_delta_mm=dbb, volume_delta_fraction=dvol)
        if dbb <= TOL_BBOX and dvol <= TOL_VOL and sh.isValid() and sh.Solids:
            rec['verified'] = True
            shapes[slug] = sh
            out = os.path.join(job['step_dir'], cand['out_name'])
            doc = FreeCAD.newDocument('p_'+slug.replace('-', '_'))
            o = doc.addObject('Part::Feature', 'part'); o.Shape = sh; o.Label = slug
            Import.export([o], out)
            FreeCAD.closeDocument(doc.Name)
            rec['written'] = out
        else:
            rec['reason'] = 'STEP does not match the STL in the package (bbox delta %.2f mm, volume delta %.1f%%)' % (dbb, 100*dvol)
    except Exception as e:  # keep going; report
        rec['reason'] = 'FreeCAD could not verify: '+str(e)
    result['parts'][slug] = rec

# Scene tree -> world pose of every geom, in the order the published mesh lists them.
scene = job['scene']
bodies = {b['name']: b for b in scene['bodies']}
world = {}
def body_world(name):
    if name in world: return world[name]
    b = bodies[name]
    local = (quat_matrix(b['quat']), [1000*v for v in b['pos']])
    world[name] = compose(body_world(b['parent']), local) if b['parent'] else local
    return world[name]

pieces = job['pieces']  # [{name, bbox_min, bbox_max}] index-aligned with geoms
doc = FreeCAD.newDocument('assembly')
placed, skipped, checks = [], [], []
i = 0
for b in scene['bodies']:
    bw = body_world(b['name'])
    for g in b['geoms']:
        piece = pieces[i]; i += 1
        slug = piece['name'].split('/')[1].split('#')[0]
        if slug not in shapes:
            skipped.append(piece['name']); continue
        R, t = compose(bw, (quat_matrix(g['quat']), [1000*v for v in g['pos']]))
        sh = shapes[slug].copy(); sh.Placement = placement(R, t)
        bb = tight(sh)
        got = [bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax]
        exp = piece['bbox_min']+piece['bbox_max']
        d = max(abs(a-c) for a, c in zip(got, exp))
        checks.append({'piece': piece['name'], 'bbox_delta_mm': d})
        if d > TOL_BBOX:
            skipped.append(piece['name']+' (placed bbox off by %.2f mm)' % d); continue
        o = doc.addObject('Part::Feature', 'p%d' % i); o.Shape = sh; o.Label = piece['name']
        placed.append(piece['name'])
if placed:
    out = job['assembly_step']
    Import.export([o for o in doc.Objects], out)
    rb = Part.read(out)
    result['assembly'] = {'file': out, 'placed': placed, 'skipped': skipped, 'checks': checks,
                          'readback_solids': len(rb.Solids), 'bytes': os.path.getsize(out)}
else:
    result['assembly'] = {'file': None, 'placed': [], 'skipped': skipped, 'checks': checks}
json.dump(result, open(job['result'], 'w'), indent=1)
print('EXPORT_ASSEMBLY_DONE', len(placed), 'placed', len(skipped), 'skipped')
