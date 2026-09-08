#!/usr/bin/env python3
"""Add only source-measured pilot anchors; leave all existing interfaces intact.

Inputs are classified chosen pilots and frozen mesh features. Coordinates are
reference mesh-local, not a measurement of reconstructed CAD or physical hardware.
No thread form, pitch, material or compatible connection is invented.
"""
import hashlib
import json
from pathlib import Path
import place_fasteners as P

ROOT = Path(__file__).resolve().parents[1]
OWNER = 'tools/gen_pilot_interfaces.py'
FEATURES = ROOT / 'out/fasteners/features-by-mesh.json'


def interface_list(doc):
    if isinstance(doc.get('interfaces'), list):
        return doc['interfaces']
    return doc['record']['interfaces']


def generate():
    data = json.loads(FEATURES.read_text())['meshes']
    runs = json.loads((ROOT/'out/fasteners/runs.json').read_text())['runs']
    groups = {}
    for run in runs:
        if run['verdict'] != 'PASS':
            continue
        end = P.resolve_pilot_endpoint(run)
        mesh, idx = end['in_mesh'], end['mesh_feature_index']
        groups.setdefault(end['ref'], {})[idx] = mesh
    report = []
    for ref, selected in sorted(groups.items()):
        folder = Path(P.folder(ref))
        path = folder / 'current/cad/interfaces.json'
        if not path.exists():
            path = folder / 'cad/interfaces.json'
        doc = json.loads(path.read_text())
        frame = doc['record'].get('frame', '')
        # These are the declared mesh-local coordinate contracts, not a CAD-fit claim.
        if 'mesh' not in frame.lower() or any(mesh + '.stl' not in frame for mesh in selected.values()):
            raise ValueError('CANNOT DETERMINE: declared coordinate frame does not identify the source mesh: ' + ref)
        rows = interface_list(doc)
        keep = [r for r in rows if r.get('owned_by') != OWNER]
        added = []
        for idx, mesh in sorted(selected.items()):
            fs = [f for f in data[mesh]['features'] if f.get('feature') == 'hole' and f.get('index') == idx]
            if len(fs) != 1:
                raise ValueError('Pilot feature is not unique: %s %s' % (mesh, idx))
            f = fs[0]
            name = 'mesh_pilot_%d' % idx
            if any(r['name'] == name for r in keep):
                raise ValueError('Refusing to overwrite existing interface: ' + ref + '#' + name)
            z = P.unit(f['axis'])
            added.append({
                'name': name, 'owned_by': OWNER, 'role': 'measured_mesh_pilot',
                'frame': {'origin_mm': f['center_mm'], 'z_axis': z, 'x_axis': P.perp(z)},
                'accepts': [], 'accepts_why': 'Actual screw/thread and mating datum unresolved; retained nominal assembly connection is not compatibility evidence.',
                'pilot_d_mm': f['d_mm'], 'pilot_depth_mm': f['depth_mm'],
                'extent_along_axis_mm': f['extent_along_axis_mm'],
                'verdict': 'CANNOT DETERMINE',
                'verdict_scope': 'Reference mesh anchor measured; rebuilt CAD correspondence and original hardware compatibility unverified.',
                'source': {'path': str(FEATURES.relative_to(ROOT)), 'sha256': hashlib.sha256(FEATURES.read_bytes()).hexdigest(),
                           'mesh': mesh, 'feature_index': idx, 'method': f['method'], 'fit': f['fit'], 'declared_shelf_frame': frame},
                'thread_identity': {'verdict': 'CANNOT DETERMINE', 'why': 'Smooth mesh pilot cannot establish original screw profile/pitch or mating strength.'},
                'what': 'Local center and axis of the selected reference-mesh hole. This center is not a claimed screw seating datum; no rebuilt solid or physical unit was measured.'})
        rows[:] = keep + added
        path.write_text(json.dumps(doc, indent=2) + '\n')
        report.append({'ref': ref, 'path': str(path.resolve().relative_to(ROOT)), 'added': len(added), 'preserved': len(keep)})
    return report


if __name__ == '__main__':
    print(json.dumps(generate(), indent=2))
