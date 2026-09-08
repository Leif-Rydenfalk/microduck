"""Pinned public HAT rail nets vs actual design; not an installed-board verdict."""
import importlib.util
from pathlib import Path
import unittest

from elec_close import hat_netlist

ROOT = Path(__file__).resolve().parents[1]


def verify_rails(comps):
    pads = lambda ref: comps[ref]['pads']
    assert pads('J4')['1'] == pads('J4')['17'] == pads('J5')['2'] == '+3V3'
    assert pads('U3') == {'1': 'GND', '2': '+1V8', '3': '+3V3'}
    assert comps['U3']['value'] == 'XC6206P182MR'
    assert pads('U2')['32'] == pads('U3')['2']
    assert all(pads('U2')[n] == '+3V3' for n in ('7', '18', '24', '25'))
    assert pads('U11')['7'] == '+3V3'
    assert pads('U11')['3'] == pads('U11')['11'] == pads('R9')['1']
    assert comps['R9']['value'] == '0R' and pads('R9')['2'] == '+3V3'
    assert comps['U9']['value'] == 'AP63205'
    assert pads('U9')['2'] == pads('U9')['3'] == '+BATT'
    assert pads('U9')['5'] == pads('L4')['2']
    assert pads('L4')['1'] == pads('U10')['4'] == pads('Q2')['2']
    assert pads('U10')['5'] == pads('Q2')['1']
    assert pads('Q2')['3'] == pads('J4')['2'] == pads('J4')['4'] == '+5V'


class RailTopology(unittest.TestCase):
    def test_public_pads_and_broken_ldo(self):
        comps, _ = hat_netlist()
        verify_rails(comps)
        comps['U3']['pads']['2'] = '+3V3'
        with self.assertRaises(AssertionError):
            verify_rails(comps)

    def test_actual_model_and_voltage_failures(self):
        spec = importlib.util.spec_from_file_location('md_netlist_rails', ROOT / 'electronics/netlist.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        d = module.electrical_design()
        terms = {(t.owner, t.ref): n.id for n in d.nets() for t in n.terminals}
        self.assertEqual(terms['hat', 'V1V8_OUT'], terms['codec', 'DVDD'])
        for terminal in [('hat', 'J5_3V3'), ('hat', 'V3V3_IN'), ('tof', '3V3'),
                         ('codec', 'AVDD'), ('codec', 'IOVDD'), ('hat_y1', 'VDD')]:
            self.assertEqual(terms[terminal], 'HAT_3V3')
        report = module.check_all(d)
        self.assertEqual(sum(f.rule == 'volts/SERVO_V' and f.verdict == 'FAIL'
                             for f in report.findings), 15)
        self.assertTrue(any(f.rule == 'cross/wiring' and f.verdict == 'PASS'
                            for f in report.findings))


if __name__ == '__main__':
    unittest.main()
