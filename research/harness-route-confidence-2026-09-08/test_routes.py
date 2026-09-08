import contextlib
import copy
import io
import json
from pathlib import Path
import runpy
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
AUDIT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'wiring'),str(ROOT/'tools')]
from route_confidence import drop_verdict
from elec_close import hat_netlist
with contextlib.redirect_stdout(io.StringIO()):
    M=runpy.run_path(str(ROOT/'wiring/measure.py'))

class RouteEvidence(unittest.TestCase):
    def test_old_numeric_results_preserved_as_conditional(self):
        old=json.loads((AUDIT/'drop-before.json').read_text())
        for a,b in zip(old['runs'],M['drop']['runs']):
            self.assertEqual(a['total_drop_to_ankle_V'],b['total_drop_to_ankle_V'])
            self.assertEqual(a['received_at_ends_V'],b['received_at_ends_V'])
            self.assertEqual(b['verdict'],'CANNOT DETERMINE')
            for x,y in zip(a['hops'],b['hops']):
                for k in ('loop_ohm','drop_V','v_in','v_out'):self.assertEqual(x[k],y[k])
                self.assertEqual(x['cable_mm'],y['modeled_cable_mm'])
                self.assertIsNone(y['cable_mm'])

    def test_no_proxy_is_a_cut(self):
        for c in M['cables']:
            if c['id']=='hat-radxa-40pin':continue
            self.assertIsNone(c['cable_mm'])
            self.assertIsNone(c['floor_mm'])
            self.assertEqual(c['route_verdict'],'CANNOT DETERMINE')
        self.assertIsNone(M['out']['record']['total_length_mm'])
        before=json.loads((AUDIT/'cables-before.json').read_text())['record']['cables']
        for a,b in zip(before,M['cables']):
            if a['cable_mm'] is not None and a['id']!='hat-radxa-40pin':self.assertEqual(a['cable_mm'],b['modeled_cable_mm'])

    def test_missing_model_length_propagates_without_zero_default(self):
        cs=copy.deepcopy(M['cables']);cs[0]['modeled_cable_mm']=None
        d=M['calculate_drop'](cs)
        for r in d['runs']:
            self.assertEqual(r['verdict'],'CANNOT DETERMINE')
            self.assertIsNone(r['total_drop_to_ankle_V'])
            self.assertTrue(all(h['v_out'] is None for h in r['hops']))

    def test_calculated_and_upstream_failures_survive_uncertainty(self):
        self.assertEqual(drop_verdict('FAIL','CANNOT DETERMINE','PASS'),'FAIL')
        self.assertEqual(drop_verdict('PASS','CANNOT DETERMINE','FAIL'),'FAIL')
        cs=copy.deepcopy(M['cables']);cs[0]['modeled_cable_mm']=100000
        for r in M['calculate_drop'](cs)['runs']:
            self.assertEqual(r['verdict'],'FAIL')
            self.assertEqual(r['hops'][0]['modeled_verdict'],'FAIL')
            self.assertTrue(all(h['verdict']=='FAIL' for h in r['hops']))

    def test_public_audio_topology_against_actual_pcb(self):
        c,_=hat_netlist()
        self.assertEqual(c['U1']['value'],'PAM8406D')
        self.assertEqual(c['U1']['pads']['16'],c['FB3']['pads']['1'])
        self.assertEqual(c['J1']['pads']['1'],c['FB3']['pads']['2'])
        self.assertEqual(c['U1']['pads']['14'],c['FB2']['pads']['1'])
        self.assertEqual(c['J1']['pads']['2'],c['FB2']['pads']['2'])
        self.assertEqual(c['MK1']['pads']['1'],c['C10']['pads']['1'])
        self.assertEqual(c['C10']['pads']['2'],c['U2']['pads']['16'])
        mic=next(c for c in M['cables'] if c['id']=='mic-hat')
        self.assertEqual(mic['presence_verdict'],'CANNOT DETERMINE')
        self.assertIn('MK1',mic['pins'])

    def test_public_board_projections_not_as_built(self):
        d=json.loads((ROOT/'out/wiring/hat-connectors.json').read_text())['record']
        self.assertEqual(d['identity_verdict'],'CANNOT DETERMINE')
        self.assertEqual(len(d['connectors']),12)
        for c in d['connectors']:
            self.assertNotIn('as_built_world',c)
            self.assertEqual(c['public_c1_world']['identity_verdict'],'CANNOT DETERMINE')
            self.assertIn('not_wire_exit',c['public_c1_world']['point_kind'])

if __name__=='__main__':unittest.main()
