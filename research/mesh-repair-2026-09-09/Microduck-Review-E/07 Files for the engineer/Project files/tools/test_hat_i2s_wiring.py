"""Check the public HAT cable claim against PCB pads, not hand-written closure text."""
import ast
import copy
import json
from pathlib import Path
import re
import unittest
import importlib.util
from types import SimpleNamespace

from elec_close import hat_netlist

ROOT = Path(__file__).resolve().parents[1]


def verify(row, components):
    header = components['J4']['pads']
    codec = components['U2']['pads']
    oscillator = components['Y1']
    match = re.search(r'I2S3 \(M0: ([0-9/]+)', row['pins'])
    assert match, 'missing I2S pin list'
    claimed = set(match[1].split('/'))
    measured = {p for p, net in header.items()
                if net in {codec[n] for n in ('2', '3', '4', '5')}}
    assert claimed == measured == {'12', '35', '38', '40'}, (claimed, measured)
    assert header['13'] == 'unconnected-(J4-Pin_13-Pad13)'
    assert codec['1'] == oscillator['pads']['3'] != header['13']
    assert oscillator['value'] == '12 MHz'
    assert oscillator['pads']['1'] == oscillator['pads']['4'] == '+3V3'
    assert oscillator['pads']['2'] == 'GND'
    assert 'installed revision unconfirmed' in row['pins']


class HatI2SWiring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.components, _ = hat_netlist()
        data = json.loads((ROOT / 'wiring/cables.json').read_text())
        cls.row = next(r for r in data['record']['cables'] if r['id'] == 'hat-radxa-40pin')

    def test_pcb_connectivity(self):
        verify(self.row, self.components)

    def test_old_fifth_pin_is_rejected(self):
        broken = dict(self.row, pins=self.row['pins'].replace('12/35/38/40', '12/13/35/38/40'))
        with self.assertRaises(AssertionError):
            verify(broken, self.components)

    def test_disconnected_local_clock_is_rejected(self):
        broken = copy.deepcopy(self.components)
        broken['Y1']['pads']['3'] = 'unconnected'
        with self.assertRaises(AssertionError):
            verify(self.row, broken)

    def test_source_and_rendered_row_match(self):
        tree = ast.parse((ROOT / 'wiring/measure.py').read_text())
        literals = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Dict):
                try:
                    row = ast.literal_eval(node)
                except (ValueError, TypeError):
                    continue
                if row.get('id') == 'hat-radxa-40pin':
                    literals.append(row)
        self.assertEqual(len(literals), 1)
        self.assertEqual(literals[0], {k: self.row[k] for k in literals[0]})
        self.assertEqual(set(self.row) - set(literals[0]),
                         {'route_verdict', 'cut_verdict', 'endpoint_evidence', 'length_scope'})
        self.assertEqual(self.row['cut_verdict'], 'CANNOT DETERMINE')
        self.assertEqual(self.row['cable_mm'], 0)  # board-to-board, not a cut

        rendered = next(line for line in (ROOT / 'wiring/CABLES.md').read_text().splitlines()
                        if '`hat-radxa-40pin`' in line)
        self.assertIn(self.row['pins'], rendered)

    def test_wiring_sources_and_generated_nets_have_no_header_mclk(self):
        source = json.loads((ROOT / 'wiring/designs/microduck/design.json').read_text())
        hat = next(n for n in source['nodes'] if n['label'] == 'hat')
        self.assertNotIn('MCLK', hat['map'])
        record = json.loads((ROOT / 'ce-parts/microduck-robot-hat-pcb/electrical.part.json').read_text())
        self.assertNotIn('MCLK', [n['name'] for n in record['record']['requires']])
        for relative in ('electronics/netlist.json', 'wiring/designs/microduck/nets.json'):
            doc = json.loads((ROOT / relative).read_text())
            for net in doc['nets']:
                self.assertNotIn(net['id'], ('hdr13', 'hdr13_I2S3_MCLK_M0'))
                self.assertFalse(any(t['owner'] == 'hat' and t['ref'] == 'MCLK'
                                     for t in net['terminals']))

    def test_actual_netlist_clock_gate_and_negative_control(self):
        spec = importlib.util.spec_from_file_location('microduck_netlist', ROOT / 'electronics/netlist.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        design = module.electrical_design()
        self.assertEqual(module.check_local_mclk(design).verdict, 'CANNOT DETERMINE')
        placed = {t.ref: n.id for n in design.nets() for t in n.terminals if t.owner == 'hat_y1'}
        self.assertEqual(placed, {'GND': 'GND', 'VDD': 'HAT_3V3',
                                  'TRISTATE': 'HAT_3V3', 'OUT': 'HAT:Y1_OUT'})
        bom = (ROOT / 'reference/pollen-elec-rpi-robot-hat/production/ASE01187-C1_elec_RPI_Robot_HAT_BOM.csv').read_text()
        self.assertIn('Y1,Oscillator_SMD_Abracon_ASDMB-4Pin_2.5x2.0mm,1,12 MHz,C7425459', bom)
        nets = [SimpleNamespace(id='hdr13', terminals=[SimpleNamespace(owner='codec', ref='MCLK')])]
        broken = SimpleNamespace(name='wrong-header-clock', nets=lambda: nets)
        self.assertEqual(module.check_local_mclk(broken).verdict, 'FAIL')
        nets[0].id = 'HAT:Y1_OUT'
        self.assertEqual(module.check_local_mclk(broken).verdict, 'FAIL', 'a named local net without a provider is not sufficient')


if __name__ == '__main__':
    unittest.main()
