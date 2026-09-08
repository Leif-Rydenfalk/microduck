"""RFQ questions must not reinstate rejected hardware or proxy cut lengths."""
import copy
import json
import re
import unittest
from pathlib import Path
import gen_sourcing as s


def contradictions(data):
    bad = []
    rows = {r['key']: r for r in data['rfq_suppliers']}
    for key in ('camera', 'radxa', 'robotis'):
        text = ' '.join([rows[key]['ask']] + rows[key]['also_ask'])
        if re.search(r'(?:at|in|need|matching|length of)\s+(?:a\s+)?(?:~|about\s+)?15\s*mm', text, re.I):
            bad.append(key + ': proxy requested as cut')
    camera = rows['camera']['ask']
    if 'Reject Seeed 102110719' not in camera or 'do not extend its historical price tier' not in camera:
        bad.append('camera: rejected module treated as quote candidate')
    if 'physical' not in ' '.join(rows['camera']['also_ask']).lower() or 'unknown' not in ' '.join(rows['camera']['also_ask']).lower():
        bad.append('camera: cut uncertainty omitted')
    fastener = rows['fasteners']['ask'] + ' '.join(rows['fasteners']['also_ask'])
    for required in ('52 servo ISO length proposals have been withdrawn', 'M2 tapping screws', '3 mm maximum pilot-hole depth', 'not an ISO M2 thread'):
        if required not in fastener:
            bad.append('fasteners: ' + required)
    return bad


class RfqEvidence(unittest.TestCase):
    def test_current_questions_match_recorded_restrictions(self):
        self.assertEqual(contradictions(s.DATA), [])

    def test_old_camera_and_proxy_requests_are_detected(self):
        before = json.loads((Path(s.REPO) / 'research/rfq-source-corrections-2026-09-08/sourcing-before.json').read_text())
        problems = contradictions(before)
        self.assertIn('camera: proxy requested as cut', problems)
        self.assertIn('camera: rejected module treated as quote candidate', problems)
        self.assertIn('radxa: proxy requested as cut', problems)

    def test_new_acceptance_clause_cannot_hide_behind_correct_qualifier(self):
        data = copy.deepcopy(s.DATA)
        row = next(r for r in data['rfq_suppliers'] if r['key'] == 'camera')
        row['also_ask'].append('We need ~15 mm FFC for manufacture.')
        self.assertIn('camera: proxy requested as cut', contradictions(data))

    def test_prices_quantities_contacts_and_other_records_unchanged(self):
        before = json.loads((Path(s.REPO) / 'research/rfq-source-corrections-2026-09-08/sourcing-before.json').read_text())
        after = copy.deepcopy(s.DATA)
        old_rows = {r['key']: r for r in before['rfq_suppliers']}
        for row in after['rfq_suppliers']:
            if row['key'] in ('robotis', 'radxa', 'camera', 'fasteners'):
                row['ask'] = old_rows[row['key']]['ask']
                row['also_ask'] = old_rows[row['key']]['also_ask']
        old_b8 = next(r for r in before['lines'] if r['id'] == 'B8')
        new_b8 = next(r for r in after['lines'] if r['id'] == 'B8')
        for old, new in zip(old_b8['offers'], new_b8['offers']):
            if '20x our 15 mm cut length' in old.get('note', ''):
                new['note'] = old['note']
        self.assertEqual(after, before)

    def test_rendered_request_keeps_rejection_and_unknown_route(self):
        self.assertIn('Reject Seeed 102110719', s.RFQ)
        self.assertIn('Physical CSI cut length is unknown', s.RFQ)
        self.assertNotIn('20x our 15 mm cut length', s.SOURCING)


if __name__ == '__main__':
    unittest.main()
