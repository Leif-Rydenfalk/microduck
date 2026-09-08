"""Original fastener identity audit, not a whole-assembly acceptance test.

Discovered by triad-test under TRIAD.md. No CAD build or hardware operation.
Mesh pilots cannot identify a helix/profile; modeled ISO identifiers are not
independent evidence. Other structural, electrical and placement gates remain
outside this script and must retain their own verdicts.
"""
import json
from pathlib import Path

OWNER = 'tools/place_fasteners.py'


def verify(placements, joints, bom):
    checks = []
    def add(name, verdict, why):
        checks.append({'check': name, 'verdict': verdict, 'why': why})
    ps = [r for r in placements['record']['rows'] if r.get('owned_by') == OWNER]
    js = [r for r in joints['record']['rows'] if r.get('owned_by') == OWNER]
    bs = [r for r in bom['record']['rows'] if r.get('owned_by') == OWNER]
    add('fastener_record_coverage', 'PASS' if len(ps) == len(js) == sum(r['qty'] for r in bs) == 64 else 'FAIL',
        {'placements': len(ps), 'joints': len(js), 'bom_pieces': sum(r['qty'] for r in bs)})
    servo = [r for r in js if r.get('b', {}).get('in_mesh') == 'xl330']
    add('servo_run_coverage', 'PASS' if len(servo) == 52 else 'FAIL', len(servo))
    for p in ps:
        v = p.get('verify', {})
        # Compare measured residuals to the original fixed tolerances, never
        # take a caller's PASS or a widened tolerance as proof.
        dp, da = v.get('head_point_error_mm'), v.get('axis_error_deg')
        ok = isinstance(dp, (int, float)) and isinstance(da, (int, float)) and 0 <= dp <= .001 and 0 <= da <= .01
        add(p['instance'] + ':nominal_placement', 'PASS' if ok else 'FAIL', {'error_mm': dp, 'error_deg': da})
        identity = p.get('thread_identity', {})
        labelled = identity.get('verdict') == 'CANNOT DETERMINE' and v.get('thread_identity_verdict') == 'CANNOT DETERMINE' and v.get('verdict') != 'PASS'
        add(p['instance'] + ':identity_annotation', 'PASS' if labelled else 'FAIL', 'Mesh-only identity must not be promoted to PASS.')
        add(p['instance'] + ':actual_thread_identity', 'CANNOT DETERMINE',
            'No original screw/profile/pitch evidence in the measured run. Nominal model is not identity proof.')
    for i, j in enumerate(js):
        end = j.get('b', {})
        matches = [p for p in placements['record']['rows'] if p.get('body') == end.get('in_body') and p.get('geom_index') == end.get('geom_index') and p.get('mesh') == end.get('in_mesh') and p.get('owned_by') != OWNER]
        target_ok = len(matches) == 1 and matches[0].get('part') == end.get('ref')
        if target_ok:
            target = matches[0]
            label = '%s/%s#%d' % (target['body'], target['part'].split(':')[1], placements['record']['rows'].index(target))
            target_ok = end.get('instance') == label
        add('joint_%d:exact_target_instance' % i, 'PASS' if target_ok else 'FAIL', 'Chosen source body/geom_index/mesh must identify exactly one part and its actual assembly label.')
        try:
            root = Path(__file__).resolve().parents[5]
            path = root / 'ce-parts' / end['ref'].split(':', 1)[1] / 'current/cad/interfaces.json'
            doc = json.loads(path.read_text())
            interfaces = doc.get('interfaces', doc.get('record', {}).get('interfaces', []))
            anchors = [a for a in interfaces if a.get('name') == end.get('interface')]
            anchor_ok = len(anchors) == 1 and anchors[0].get('source', {}).get('mesh') == end.get('in_mesh') and anchors[0].get('source', {}).get('feature_index') == end.get('mesh_feature_index') and anchors[0].get('thread_identity', {}).get('verdict') == 'CANNOT DETERMINE'
        except (KeyError, ValueError, OSError):
            anchor_ok = False
        add('joint_%d:measured_anchor_resolves' % i, 'PASS' if anchor_ok else 'FAIL', 'The named shelf anchor must exist and retain its chosen mesh feature and original-thread unknown.')
        add('joint_%d:identity_annotation' % i, 'PASS' if j.get('thread_identity', {}).get('verdict') == 'CANNOT DETERMINE' else 'FAIL', 'Joint must retain the original-thread unknown.')
    for i, b in enumerate(bs):
        add('bom_%d:identity_annotation' % i, 'PASS' if b.get('identity_verdict') == 'CANNOT DETERMINE' else 'FAIL', 'Nominal modeled hardware is not a released original purchase specification.')
    verdict = 'FAIL' if any(c['verdict'] == 'FAIL' for c in checks) else 'CANNOT DETERMINE'
    return {'verdict': verdict, 'scope': 'fastener nominal placement residuals and unresolved original thread identity only; other assembly gates are not evaluated', 'checks': checks}


