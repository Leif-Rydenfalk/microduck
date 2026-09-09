"""FreeCAD side of export_bundles.py. Run under freecadcmd, never plain python3.

    freecadcmd tools/export_assembly_step.py <job.json>

Writes the STEP variants Ming can pick from (Leif, 2026-09-09: "make different
versions so he can grab whatever he needs with clear labeling"):

  step_all        every placed piece of the published robot, one file
  step_flat       every printed part side by side, one file
  step_solids     only the parts that have real solid CAD, assembled
  per-part dir    one STEP per printed part

Where a part has verified solid CAD it is used; the manufacturer servo solid is
placed with the frame proven in out/fit/vendor-servo-frame.json; bearings are
simplified rings of catalogue size; everything else is a faceted body made
from the very mesh Ming already has, and is labelled "(mesh body)". Every
placement is checked against the published piece's bounding box.
"""
import json, math, os, sys, time
import FreeCAD, Part, Import, Mesh

job = json.load(open(sys.argv[-1]))
TOL = job.get('tol_bbox_mm', 0.5)
TOL_VOL = job.get('tol_volume_fraction', 0.03)
LOG = open(job['log'], 'a')
def log(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); LOG.write(s+'\n'); LOG.flush()


def tight(shape):
    try: return shape.optimalBoundingBox(True, False)
    except Exception: return shape.BoundBox


def box6(bb): return [bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax]


def stl_stats(path):
    m = Mesh.Mesh(path); b = m.BoundBox
    return [b.XLength, b.YLength, b.ZLength], m.Volume


def quat_matrix(q):
    w, x, y, z = q; n = math.sqrt(w*w+x*x+y*y+z*z) or 1.0; w, x, y, z = w/n, x/n, y/n, z/n
    return [[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)], [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)], [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]]


def compose(a, b):
    Ra, ta = a; Rb, tb = b
    return [[sum(Ra[i][k]*Rb[k][j] for k in range(3)) for j in range(3)] for i in range(3)], [sum(Ra[i][k]*tb[k] for k in range(3))+ta[i] for i in range(3)]


def placement(R, t):
    return FreeCAD.Placement(FreeCAD.Matrix(R[0][0], R[0][1], R[0][2], t[0], R[1][0], R[1][1], R[1][2], t[1], R[2][0], R[2][1], R[2][2], t[2], 0, 0, 0, 1))


def facet(V, F):
    """Faceted body from triangles: a solid when the mesh closes, else the sewn shell/compound."""
    sh = Part.Shape(); sh.makeShapeFromMesh((V, F), 0.01)
    try:
        if len(sh.Shells) == 1:
            so = Part.Solid(sh.Shells[0])
            if so.isValid() and so.Volume > 0: return so, 'mesh body (closed)'
    except Exception: pass
    return sh, 'mesh body (open shell)'


def facet_stl(path):
    m = Mesh.Mesh(path); V, F = m.Topology
    return facet([tuple(v) for v in V], [tuple(f) for f in F])


def facet_piece(p):
    V = [tuple(p['positions'][3*i:3*i+3]) for i in range(len(p['positions'])//3)]
    F = [tuple(p['indices'][i:i+3]) for i in range(0, len(p['indices']), 3)]
    return facet(V, F)


def export(objs, path):
    Import.export(objs, path); return os.path.getsize(path)


result = {'parts': {}, 'pieces': [], 'files': {}}
t_start = time.time()

# ---- 1. one shape per printed part: verified solid CAD, else faceted from the STL Ming has
shapes, kinds = {}, {}
docp = FreeCAD.newDocument('parts')
flat_objs = []
for slug, rec_in in job['printed'].items():
    rec = {'stl': rec_in['stl'], 'kind': None}
    cand = job['candidates'].get(slug)
    if cand:
        try:
            sh = Part.read(cand['step']); bb = tight(sh); sb, sv = stl_stats(rec_in['stl'])
            dbb = max(abs(a-b) for a, b in zip([bb.XLength, bb.YLength, bb.ZLength], sb)); dvol = abs(sh.Volume-sv)/max(sv, 1e-9)
            rec.update(step=cand['step'], bbox_delta_mm=dbb, volume_delta_fraction=dvol, solids=len(sh.Solids), valid=sh.isValid())
            if dbb <= TOL and dvol <= TOL_VOL and sh.isValid() and sh.Solids:
                shapes[slug] = sh; rec['kind'] = 'solid CAD (verified against the STL)'
            else:
                rec['step_rejected'] = 'bbox delta %.2f mm, volume delta %.1f%%' % (dbb, 100*dvol)
        except Exception as e:
            rec['step_rejected'] = 'FreeCAD could not read/verify: '+str(e)
    if slug not in shapes:
        t0 = time.time(); sh, kind = facet_stl(rec_in['stl']); shapes[slug] = sh; rec['kind'] = kind; rec['facet_seconds'] = round(time.time()-t0, 1)
    kinds[slug] = rec['kind']
    o = docp.addObject('Part::Feature', 'p_'+slug.replace('-', '_')); o.Shape = shapes[slug]; o.Label = rec_in['label']+('' if 'solid' in rec['kind'] else ' (mesh body)')
    out = os.path.join(job['part_dir'], rec_in['out_name'] + ('' if 'solid' in rec['kind'] else ' (mesh body)') + '.stp')
    rec['file'] = out; rec['bytes'] = export([o], out)
    # side-by-side copy
    lo = rec_in['stl_min']; x, y = rec_in['cell']
    o2 = docp.addObject('Part::Feature', 'f_'+slug.replace('-', '_')); s2 = shapes[slug].copy(); s2.Placement = FreeCAD.Placement(FreeCAD.Vector(x-lo[0], y-lo[1], -lo[2]), FreeCAD.Rotation()); o2.Shape = s2; o2.Label = o.Label
    flat_objs.append(o2)
    result['parts'][slug] = rec
    log('PART', slug, rec['kind'], '%.0fs' % (time.time()-t_start))
result['files']['step_flat'] = {'file': job['step_flat'], 'bytes': export(flat_objs, job['step_flat']), 'parts': len(flat_objs)}
log('FLAT written', result['files']['step_flat'])

# ---- 2. vendor servo solid in the mesh frame, bearings as rings
servo = None
if job.get('servo_step'):
    vs = Part.read(job['servo_step']); servo = Part.makeCompound(vs.Solids)
    # local(X,Y,Z) = (vendorZ + 8, vendorX, vendorY): bake the proven frame into the geometry once
    servo.transformShape(FreeCAD.Matrix(0, 0, 1, 8.0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1))
    bb = tight(servo); result['servo'] = {'solids': len(vs.Solids), 'open_shells_dropped': len(vs.Shells)-sum(len(s.Shells) for s in vs.Solids), 'local_bbox': box6(bb)}
    log('SERVO', result['servo'])

def bearing_ring(dims, bbox_min, bbox_max):
    od, idm, w = dims; size = [bbox_max[i]-bbox_min[i] for i in range(3)]
    axis = min(range(3), key=lambda i: abs(size[i]-w)); c = [(bbox_min[i]+bbox_max[i])/2 for i in range(3)]
    d = FreeCAD.Vector(*[1.0 if i == axis else 0.0 for i in range(3)]); p = FreeCAD.Vector(*c) - d*(w/2)
    return Part.makeCylinder(od/2, w, p, d).cut(Part.makeCylinder(idm/2, w, p, d))

# ---- 3. assembled: walk the scene tree in published piece order
scene = job['scene']; bodies = {b['name']: b for b in scene['bodies']}; world = {}
def body_world(name):
    if name in world: return world[name]
    b = bodies[name]; local = (quat_matrix(b['quat']), [1000*v for v in b['pos']])
    world[name] = compose(body_world(b['parent']), local) if b['parent'] else local; return world[name]

robot = json.load(open(job['mesh_json']))['parts']
doca = FreeCAD.newDocument('assembly'); all_objs, solid_objs = [], []
i = 0
for b in scene['bodies']:
    bw = body_world(b['name'])
    for g in b['geoms']:
        p = robot[i]; i += 1; name = p['name']; slug = name.split('/')[1].split('#')[0]
        R, t = compose(bw, (quat_matrix(g['quat']), [1000*v for v in g['pos']]))
        V = p['positions']; exp = [min(V[k::3]) for k in range(3)]+[max(V[k::3]) for k in range(3)]
        rec = {'piece': name, 'slug': slug}; sh = None; kind = None
        if slug in shapes:
            sh = shapes[slug].copy(); sh.Placement = placement(R, t); kind = kinds[slug]
        elif slug == 'xl330-m288-t' and servo is not None:
            sh = servo.copy(); sh.Placement = placement(R, t); kind = 'manufacturer servo solid (frame per out/fit/vendor-servo-frame.json)'
        elif slug in job['bearings']:
            sh = bearing_ring(job['bearings'][slug], exp[:3], exp[3:]); kind = 'simplified bearing ring %sx%sx%s' % tuple(job['bearings'][slug])
        if sh is not None:
            got = box6(tight(sh)); d = max(abs(a-c) for a, c in zip(got, exp)); rec['bbox_delta_mm'] = d
            tol = TOL if slug in shapes or slug in job['bearings'] else job.get('tol_servo_mm', 6.0)
            if d > tol:
                rec['fallback'] = '%s placed %.2f mm off the published piece; faceted the published mesh instead' % (kind, d); sh = None
        if sh is None:
            sh, kind = facet_piece(p); kind += ' from the published placed mesh'
            got = box6(tight(sh)); rec['bbox_delta_mm'] = max(abs(a-c) for a, c in zip(got, exp))
        rec['kind'] = kind
        o = doca.addObject('Part::Feature', 'a%d' % i); o.Shape = sh; o.Label = name + ('' if kind.startswith('solid CAD') else ' (%s)' % kind.split(' (')[0])
        all_objs.append(o)
        if kind.startswith('solid CAD'): solid_objs.append(o)
        result['pieces'].append(rec); log('PIECE', i, name, kind, 'delta %.2f' % rec['bbox_delta_mm'], '%.0fs' % (time.time()-t_start))
result['files']['step_all'] = {'file': job['step_all'], 'bytes': export(all_objs, job['step_all']), 'pieces': len(all_objs)}
log('ALL written', result['files']['step_all'])
result['files']['step_solids'] = {'file': job['step_solids'], 'bytes': export(solid_objs, job['step_solids']), 'pieces': len(solid_objs)}
log('SOLIDS written', result['files']['step_solids'])
for key in ('step_all', 'step_flat', 'step_solids'):
    r = Part.read(job[key]); result['files'][key].update(readback_solids=len(r.Solids), readback_shells=len(r.Shells), readback_faces=len(r.Faces))
result['seconds'] = round(time.time()-t_start, 1)
json.dump(result, open(job['result'], 'w'), indent=1)
log('EXPORT_ASSEMBLY_DONE', result['seconds'], 's')
