"""Prevent withdrawn hardware from disappearing during a generated rebuild."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('place_fasteners', Path(__file__).with_name('place_fasteners.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PlacementPreservation(unittest.TestCase):
    def test_withdrawal_stops_before_any_output_or_placement(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root/'runs.json'
            source.write_text(json.dumps({'runs': [{'verdict': 'CANNOT DETERMINE',
                'historical_mesh_rule_proposal': {'stocked_length_mm': 10}}]}))
            output = root/'placed.json'
            output.write_bytes(b'preserved original output')
            with patch.object(module, 'RUNS', str(source)), patch.object(module, 'OUT', str(output)), \
                 patch.object(module, 'place') as place, patch.object(module, 'write_assembly') as write:
                with self.assertRaisesRegex(ValueError, 'historical screw proposals were withdrawn'):
                    module.main()
                place.assert_not_called()
                write.assert_not_called()
            self.assertEqual(output.read_bytes(), b'preserved original output')

    def test_dry_run_does_not_overwrite_report_or_assembly(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root/'runs.json'
            source.write_text(json.dumps({'runs': []}))
            output = root/'placed.json'
            output.write_bytes(b'preserved original output')
            with patch.object(module, 'RUNS', str(source)), patch.object(module, 'OUT', str(output)), \
                 patch.object(module.sys, 'argv', ['place_fasteners.py', '--dry']), \
                 patch.object(module, 'write_assembly') as write:
                result, dry = module.main()
                self.assertTrue(dry)
                write.assert_not_called()
            self.assertEqual(output.read_bytes(), b'preserved original output')


if __name__ == '__main__':
    unittest.main()
