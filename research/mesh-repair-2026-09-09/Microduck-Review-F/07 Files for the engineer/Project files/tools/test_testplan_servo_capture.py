"""Offline ingestion regression; all input is explicitly synthetic."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import testplan_servo_capture as C


class Capture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        sample = C.ROOT / 'research/servo-capture-tooling-2026-09-08/synthetic'
        self.doc = json.loads((sample / 'manifest.json').read_text())
        self.snapshot = json.loads((sample / 'servo10.json').read_text())

    def tearDown(self):
        self.tmp.cleanup()

    def run_doc(self):
        raw = json.dumps(self.snapshot).encode()
        (self.root / 'servo10.json').write_bytes(raw)
        self.doc['artifacts'][0]['sha256'] = C.digest(raw)
        path = self.root / 'manifest.json'
        path.write_text(json.dumps(self.doc))
        return C.validate(path)

    @staticmethod
    def codes(result):
        return {f['code'] for f in result['findings']}

    def test_missing_ids_and_original_provenance_never_pass(self):
        result = self.run_doc()
        self.assertEqual(result['verdict'], 'CANNOT DETERMINE')
        self.assertTrue({'missing_id', 'provenance_missing', 'servo_photo', 'imu_missing'} <= self.codes(result))
        self.assertEqual(result['observations'][0]['decoded_model'], 'XL330-M288-T')
        self.assertEqual(result['original_identity'], 'CANNOT DETERMINE')
        missing = {f['where'] for f in result['findings'] if f['code'] == 'provenance_missing'}
        self.assertTrue({'original_robot_serial', 'original_robot_revision'} <= missing)

    def test_all_runtime_ids_and_separate_imu_still_cannot_accept_hardware(self):
        for ident in json.loads(C.CONTRACT.read_text())['expected_runtime_ids'][1:]:
            snapshot = copy.deepcopy(self.snapshot)
            snapshot['observed_id'] = ident
            next(r for r in snapshot['registers'] if r['address'] == 7).update(raw=ident, raw_hex=bytes([ident]).hex(), value=ident)
            key = 'servo%d' % ident
            raw = json.dumps(snapshot).encode()
            (self.root / (key + '.json')).write_bytes(raw)
            self.doc['artifacts'].append(dict(id=key, kind='register_snapshot', label='SYNTHETIC', sample_id=self.doc['sample_id'], path=key+'.json', sha256=C.digest(raw)))
            servo = copy.deepcopy(self.doc['servos'][0]);servo.update(observed_id=ident, snapshot=key)
            self.doc['servos'].append(servo)
        imu = dict(observed_id=200, sample_id=self.doc['sample_id'], captured_at=self.doc['captured_at'], communication_errors=[], read_only=True, synthetic=True, raw_observation='SYNTHETIC BYTES, NOT HARDWARE', format_source='synthetic test, not bridge firmware')
        raw = json.dumps(imu).encode();(self.root/'imu.json').write_bytes(raw)
        self.doc['artifacts'].append(dict(id='imu', kind='imu_snapshot', label='SYNTHETIC', sample_id=self.doc['sample_id'], path='imu.json', sha256=C.digest(raw)))
        self.doc['imu'] = dict(observed_id=200, snapshot='imu')
        self.doc.update(original_robot_serial='SYNTHETIC serial', original_robot_revision='SYNTHETIC revision')
        result = self.run_doc()
        self.assertEqual(len(result['observations']), 15)
        self.assertFalse({'missing_id', 'imu_missing', 'register_encoding'} & self.codes(result))
        self.assertEqual(result['verdict'], 'CANNOT DETERMINE')
        self.assertEqual(result['physical_acceptance'], 'CANNOT DETERMINE')

    def imu_result(self, **overrides):
        payload = dict(observed_id=200, sample_id=self.doc['sample_id'],
                       captured_at=self.doc['captured_at'], communication_errors=[],
                       read_only=True, synthetic=True, raw_observation='SYNTHETIC',
                       format_source='synthetic test, not bridge firmware')
        payload.update(overrides)
        # None is a test request to omit a field entirely.
        payload = {k: v for k, v in payload.items() if v is not None}
        raw = json.dumps(payload).encode()
        (self.root / 'imu.json').write_bytes(raw)
        self.doc['artifacts'] = [a for a in self.doc['artifacts'] if a['id'] != 'imu']
        self.doc['artifacts'].append(dict(id='imu', kind='imu_snapshot', label='SYNTHETIC',
                                         sample_id=self.doc['sample_id'], path='imu.json', sha256=C.digest(raw)))
        self.doc['imu'] = dict(observed_id=200, snapshot='imu')
        return self.run_doc()

    def test_imu_nonempty_or_missing_communication_errors_add_gap(self):
        for value in (['timeout reading ID200'], None):
            result = self.imu_result(communication_errors=value)
            self.assertTrue(any(f['where'] == 'imu' and f['code'] == 'communication_errors'
                                and f['level'] == 'CANNOT DETERMINE' for f in result['findings']))
            self.assertEqual(result['physical_acceptance'], 'CANNOT DETERMINE')

    def test_imu_synthetic_mismatch_is_failure(self):
        self.doc['synthetic'] = False
        self.snapshot['synthetic'] = False
        result = self.imu_result()
        self.assertEqual(result['verdict'], 'FAIL')
        self.assertTrue(any(f['where'] == 'imu' and f['code'] == 'synthetic_mismatch'
                            and f['level'] == 'FAIL' for f in result['findings']))

    def test_imu_missing_or_false_read_only_adds_gap(self):
        for value in (False, None):
            result = self.imu_result(read_only=value)
            self.assertTrue(any(f['where'] == 'imu' and f['code'] == 'capture_method'
                                and f['level'] == 'CANNOT DETERMINE' for f in result['findings']))
        result = self.imu_result(read_only=True)
        self.assertFalse(any(f['where'] == 'imu' and f['code'] in ('capture_method', 'communication_errors')
                             for f in result['findings']))
        self.assertEqual(result['original_identity'], 'CANNOT DETERMINE')

    def test_duplicate_id_and_unexpected_observation_preserved(self):
        self.doc['servos'].append(copy.deepcopy(self.doc['servos'][0]))
        self.assertIn('duplicate_id', self.codes(self.run_doc()))
        self.doc['servos'][1]['observed_id'] = 99
        result = self.run_doc()
        self.assertIn('unexpected_id', self.codes(result))
        self.assertEqual(len(result['observations']), 2)

    def test_voltage_unit_mismatch_and_unsafe_reading(self):
        reg = next(r for r in self.snapshot['registers'] if r['address'] == 144)
        reg['unit'] = 'mV'
        self.assertIn('register_encoding', self.codes(self.run_doc()))
        reg.update(unit='V', raw=82, raw_hex='5200', value=8.2)
        result = self.run_doc()
        self.assertIn('voltage_rating_conflict', self.codes(result))
        self.assertEqual(result['verdict'], 'FAIL')

    def test_little_endian_width_and_decoded_mismatch(self):
        reg = self.snapshot['registers'][0]
        reg['raw_hex'] = '04b0'
        self.assertIn('register_encoding', self.codes(self.run_doc()))
        reg['raw_hex'] = 'b0'
        self.assertIn('register_encoding', self.codes(self.run_doc()))

    def test_changed_hash_refused(self):
        self.run_doc()
        (self.root / 'servo10.json').write_text('changed')
        self.assertIn('artifact_hash', self.codes(C.validate(self.root / 'manifest.json')))

    def test_m077_is_recognized_without_original_acceptance(self):
        self.snapshot['registers'][0].update(raw=1190, raw_hex='a604', value=1190)
        result = self.run_doc()
        self.assertEqual(result['observations'][0]['decoded_model'], 'XL330-M077-T')
        self.assertEqual(result['verdict'], 'CANNOT DETERMINE')

    def test_unknown_model_does_not_inherit_xl330_voltage_decode(self):
        self.snapshot['registers'][0].update(raw=999, raw_hex='e703', value=999)
        next(r for r in self.snapshot['registers'] if r['address'] == 144).update(unit='vendor_unknown')
        result = self.run_doc()
        self.assertIn('model_unknown', self.codes(result))
        self.assertNotIn('register_encoding', self.codes(result))

    def test_missing_register_duplicate_and_wrong_sample(self):
        self.snapshot['registers'].pop()
        self.snapshot['registers'].append(copy.deepcopy(self.snapshot['registers'][0]))
        self.snapshot['sample_id'] = 'DIFFERENT'
        self.assertTrue({'register_missing', 'register_duplicate', 'sample_mismatch'} <= self.codes(self.run_doc()))

    def test_path_escape_and_cli_no_write(self):
        self.doc['artifacts'][0]['path'] = '/dev/null'
        self.assertIn('artifact_unreadable', self.codes(self.run_doc()))
        before = {p.name: C.digest(p.read_bytes()) for p in self.root.iterdir()}
        run = subprocess.run([sys.executable, str(Path(C.__file__)), str(self.root / 'manifest.json')], capture_output=True, text=True)
        self.assertEqual(run.returncode, 1)
        self.assertEqual(before, {p.name: C.digest(p.read_bytes()) for p in self.root.iterdir()})

    def test_contract_matches_pinned_runtime_and_manufacturer_table_widths(self):
        import re
        import html
        contract = json.loads(C.CONTRACT.read_text())
        audit = C.ROOT / 'research/servo-power-audit-2026-09-08'
        runtime = (audit / 'duck-control_src_model.rs').read_text()
        block = runtime.split('pub const JOINT_IDS:', 1)[1].split('= [', 1)[1].split('];', 1)[0]
        block = re.sub(r'//[^\n]*', '', block)
        self.assertEqual(sorted(map(int, re.findall(r'\d+', block))), contract['expected_runtime_ids'])
        for filename in ('robotis-xl330-m288.html', 'robotis-xl330-m077.html'):
            table = {}
            for row in re.findall(r'<tr[^>]*>(.*?)</tr>', (audit / filename).read_text(), re.S):
                cells = [html.unescape(re.sub('<[^>]+>', '', c)).strip() for c in re.findall(r'<td[^>]*>(.*?)</td>', row, re.S)]
                if len(cells) == 7 and cells[0].isdigit() and cells[1].isdigit():
                    table.setdefault(int(cells[0]), cells)
            for rule in contract['registers']:
                self.assertEqual(int(table[rule['address']][1]), rule['bytes'], (filename, rule))
            for address in (32, 34, 144):
                self.assertIn('0.1', table[address][6])
                self.assertIn('[V]', table[address][6])


if __name__ == '__main__':
    unittest.main()
