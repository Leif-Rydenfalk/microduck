#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""duckview.py -- render the Pollen MJCF (the CLAIM) in a photo-matching pose.

Photos are the authority on the shipped product; this draws what the sim
meshes say, so the two can be compared region by region (MESH-VS-PRODUCT.md).
"""
import sys, os, json, argparse, math
sys.path.insert(0, '/Users/leifrydenfalk/dev/ce-workshop/ce-cad')
from cecad import mjcf, meshview

ROOT = '/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck'
XML = ROOT + '/reference/pollen-microduck-rl/robot_walk.xml'
ASSETS = ROOT + '/reference/pollen-microduck-rl/assets'

D = math.pi / 180.0
POSES = {
 'INIT': {},
 'STAND': {
   'left_hip_yaw': 0.0, 'left_hip_roll': -0.08726646259971647,
   'left_hip_pitch': -0.457924, 'left_knee': -0.004940, 'left_ankle': 0.452984,
   'neck_pitch': 0.3490658503988659, 'head_pitch': 0.3490658503988659,
   'head_yaw': 0.0, 'head_roll': 0.0,
   'right_hip_yaw': 0.0, 'right_hip_roll': 0.08726646259971647,
   'right_hip_pitch': 0.457924, 'right_knee': 0.004940, 'right_ankle': -0.452984,
 },
 'SIT': {
   'left_hip_yaw': 0.0, 'left_hip_roll': 0.0, 'left_hip_pitch': -0.5236,
   'left_knee': 1.0472, 'left_ankle': 0.0,
   'neck_pitch': 0.5, 'head_pitch': 1.6, 'head_yaw': 0.0, 'head_roll': 0.0,
   'right_hip_yaw': 0.0, 'right_hip_roll': 0.0, 'right_hip_pitch': 0.5236,
   'right_knee': -1.0472, 'right_ankle': 0.0,
 },
}

BODY_SETS = {
 'all': None,
 'head': {'neck', 'neck_pitch', 'yaw_roll_motion', 'jaw_soft'},
 'headonly': {'yaw_roll_motion', 'jaw_soft'},
 'trunk': {'trunk_base'},
 'trunkhips': {'trunk_base', 'yaw2roll', 'bearing_roll', 'hip_l', 'hip_l_2'},
 'legL': {'yaw2roll', 'hip_l', 'upper_leg_left', 'leg', 'ankle_left'},
 'legR': {'bearing_roll', 'hip_l_2', 'upper_leg_right', 'leg_2', 'ankle_right'},
 'legs': {'yaw2roll', 'hip_l', 'upper_leg_left', 'leg', 'ankle_left',
          'bearing_roll', 'hip_l_2', 'upper_leg_right', 'leg_2', 'ankle_right'},
 'feet': {'ankle_left', 'ankle_right'},
}

def build(pose='STAND', bodies='all', drop_meshes=(), only_meshes=None):
    m = mjcf.load(XML, mesh_dir=ASSETS)
    W = mjcf.bodies_world(m, qpos=POSES[pose])
    keep = BODY_SETS[bodies]
    groups, colors = {}, {}
    cache = {}
    i = 0
    for bname in m.order:
        if keep is not None and bname not in keep:
            continue
        b = m.bodies[bname]
        for g in b.geoms:
            if g.cls != 'visual' or not g.mesh:
                continue
            if g.mesh in drop_meshes:
                continue
            if only_meshes is not None and g.mesh not in only_meshes:
                continue
            if g.mesh not in cache:
                cache[g.mesh] = mjcf.read_stl(m.meshes[g.mesh])
            R, t = mjcf.compose(W[bname], (mjcf.quat_to_mat(g.quat), list(g.pos)))
            key = '%s#%d' % (g.mesh, i); i += 1
            groups[key] = mjcf._xform_tris(cache[g.mesh], R, t)
            rgba = m.materials.get(g.material, (0.7, 0.7, 0.7, 1))
            colors[key] = '#%02x%02x%02x' % tuple(int(255 * c) for c in rgba[:3])
    return groups, colors

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--pose', default='STAND')
    ap.add_argument('--view', default='left')  # name or "elev,azim"
    ap.add_argument('--bodies', default='all')
    ap.add_argument('--silhouette', action='store_true')
    ap.add_argument('--size', type=int, default=1400)
    ap.add_argument('--drop', default='')      # comma list of mesh names to hide
    ap.add_argument('--only', default=None)
    ap.add_argument('--title', default=None)
    a = ap.parse_args()
    view = a.view
    if ',' in view:
        view = tuple(float(x) for x in view.split(','))
    groups, colors = build(a.pose, a.bodies,
                           drop_meshes=set(a.drop.split(',')) if a.drop else (),
                           only_meshes=set(a.only.split(',')) if a.only else None)
    import numpy as np
    allpts = np.concatenate([np.asarray(t).reshape(-1, 3) for t in groups.values()])
    r = meshview.render_groups(groups, a.out, view=view, colors=colors,
                               size=(a.size, a.size), silhouette=a.silhouette,
                               bg='#f0f0ee', title=a.title)
    print(json.dumps({'out': a.out, 'tris': r['tris'], 'screen_mm': r['screen_mm'],
                      'zmin': float(allpts[:, 2].min()), 'zmax': float(allpts[:, 2].max()),
                      'screen_lo': r['screen_lo'], 'screen_hi': r['screen_hi']}))

if __name__ == '__main__':
    main()
