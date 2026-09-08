import copy
import importlib.util
import json
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
AUDIT = Path(__file__).resolve().parent

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

V = module('audit_verify', ROOT/'ce-assemblies/microduck/current/evidence/thread_identity.py')
P = module('place_fasteners', ROOT/'tools/place_fasteners.py')

class ThreadIdentity(unittest.TestCase):
    def docs(self):
        return [json.loads((ROOT/'ce-assemblies/microduck/current'/f'{n}.json').read_text()) for n in ('placements','joints','bom')]

    def test_actual_records_are_unknown(self):
        result = V.verify(*self.docs())
        self.assertEqual(result['verdict'], 'CANNOT DETERMINE')
        self.assertFalse(any(c['verdict'] == 'FAIL' for c in result['checks']))

    def test_false_identity_pass_is_rejected(self):
        docs = self.docs()
        row = next(r for r in docs[0]['record']['rows'] if r.get('owned_by') == V.OWNER)
        row['thread_identity']['verdict'] = 'PASS'
        self.assertEqual(V.verify(*docs)['verdict'], 'FAIL')

    def test_missing_identity_and_missing_run_are_rejected(self):
        docs = self.docs()
        row = next(r for r in docs[1]['record']['rows'] if r.get('owned_by') == V.OWNER)
        del row['thread_identity']
        self.assertEqual(V.verify(*docs)['verdict'], 'FAIL')
        docs[1]['record']['rows'].remove(row)
        self.assertEqual(V.verify(*docs)['verdict'], 'FAIL')

    def test_placement_failure_not_hidden_by_unknown(self):
        docs = self.docs()
        row = next(r for r in docs[0]['record']['rows'] if r.get('owned_by') == V.OWNER)
        row['verify']['axis_error_deg'] = 180
        self.assertEqual(V.verify(*docs)['verdict'], 'FAIL')

    def test_geometry_and_unowned_records_unchanged(self):
        before = json.loads((AUDIT/'placed-before.json').read_text())['placed']
        after = json.loads((ROOT/'out/fasteners/placed.json').read_text())['placed']
        fields = ('instance','part','params','via_connection','world_pos_mm','world_quat_wxyz','size','length_mm','adds','dof_left')
        self.assertEqual([{k:r[k] for k in fields} for r in before], [{k:r[k] for k in fields} for r in after])
        for n, doc in zip(('placements','joints','bom'),self.docs()):
            old = json.loads((AUDIT/f'{n}-before.json').read_text())
            self.assertEqual(old['record']['counts'],doc['record']['counts'])
            self.assertEqual([r for r in old['record']['rows'] if r.get('owned_by') != V.OWNER], [r for r in doc['record']['rows'] if r.get('owned_by') != V.OWNER])

    def test_broken_axis_still_refused_by_actual_placer(self):
        run = next(r for r in json.loads((ROOT/'out/fasteners/runs.json').read_text())['runs'] if r['verdict'] == 'PASS' and r['pilot_mesh'] == 'xl330')
        row, ok = P.place(run,0)
        self.assertTrue(ok)
        self.assertEqual(row['verify']['verdict'],'CANNOT DETERMINE')
        os.environ['CE_PLACE_BREAK']='1'
        try:
            row, ok = P.place(run,0)
            self.assertFalse(ok)
            self.assertEqual(row['verify']['verdict'],'FAIL')
        finally:
            os.environ.pop('CE_PLACE_BREAK',None)

if __name__ == '__main__':
    unittest.main()
