import copy
import json
from pathlib import Path
import unittest
from testplan_power_guard import check, HELD
ROOT=Path(__file__).resolve().parents[1]

class PowerHold(unittest.TestCase):
    def setUp(self):self.doc=json.loads((ROOT/'spec/test-plan.json').read_text())
    def test_current_hold_and_eol_definitions(self):
        self.assertEqual(check(self.doc),[])
        self.assertEqual(len(self.doc['eol']),42)
        self.assertEqual(sum(len(s.get('tests') or s.get('rows') or []) for s in self.doc['sections']),44)
    def test_missing_hold_and_false_pass_rejected(self):
        self.doc['power_execution_hold']['status']='READY'
        self.assertTrue(check(self.doc))
        self.doc['power_execution_hold']['status']='HOLD'
        t=next(t for s in self.doc['sections'] for t in s.get('tests',[]) if t['id']=='EB-04')
        t['gate']['PASS']='Any recorded voltage is PASS'
        self.assertTrue(check(self.doc))
    def test_old_high_voltage_action_rejected(self):
        t=next(t for s in self.doc['sections'] for t in s.get('tests',[]) if t['id']=='EN-02')
        t['steps'].append({'do':'Stand at 7.400 V'})
        self.assertTrue(check(self.doc))
    def test_eol_cannot_hide_hold(self):
        e=next(e for e in self.doc['eol'] if e[0]=='EB-04');e[1]='measured all voltages'
        self.assertTrue(check(self.doc))
    def test_original_identity_and_local_criterion_guards(self):
        rows={t['id']:t for s in self.doc['sections'] for t in s.get('tests',[])}
        for ident, key, value in [('SV-01','execution_status','READY'),('SN-05','gate',{'CD':'No firmware exists'}),('WK-02','criterion_scope','ORIGINAL_ACCEPTANCE')]:
            old=copy.deepcopy(rows[ident][key]);rows[ident][key]=value
            self.assertTrue(check(self.doc))
            rows[ident][key]=old

    def test_generated_document_exposes_hold(self):
        html=(ROOT/'TEST-PLAN.html').read_text()
        self.assertIn('HOLD — original power configuration unresolved',html)
        self.assertIn('definitions, not completed tests',html)
        self.assertNotIn('Bench supply raised to 8.20 V',html)
        self.assertNotIn('walk the supply down slowly from 7.400 V',html)

if __name__=='__main__':unittest.main()
