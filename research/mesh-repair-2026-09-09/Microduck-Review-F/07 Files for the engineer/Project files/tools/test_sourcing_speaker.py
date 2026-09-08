"""Keep historical speaker quotes while rejecting unsupported substitutions."""
import copy
import unittest
import gen_sourcing as s

class SpeakerSourcing(unittest.TestCase):
    def setUp(self):
        self.line = copy.deepcopy(next(x for x in s.DATA['lines'] if x['id'] == 'B12'))

    def test_only_conditional_abra_selected_for_each_batch(self):
        for offer in self.line['offers']:
            if offer.get('compatibility_status') == 'rejected':
                offer['tiers'] = [[1, 0.001]]
                offer['currency'] = 'USD'
                offer.pop('excluded_from_rollup', None)
        for count in [1, 100, 1000]:
            cost = s.line_cost(self.line, count)
            self.assertEqual(cost['vendor'], 'ABRA Electronics')
            self.assertAlmostEqual(cost['per_robot'], 2.95)
            self.assertEqual(cost['order_quantity'], count)
            self.assertTrue(cost['ceiling'])
        self.assertEqual(s.priced_domains(self.line), {'abra-electronics.com'})

    def test_identity_unknown_and_historical_quotes_preserved(self):
        self.assertEqual(self.line['verdict'], 'CANNOT DETERMINE')
        self.assertEqual(self.line['offers'][0]['tiers'][0], [1, 9.78])
        self.assertEqual(self.line['offers'][1]['tiers'][0], [1, 11.29])
        self.assertEqual(self.line['offers'][2]['tiers'][0], [1, 10.95])
        self.assertTrue(all(x['fetched'] == '2026-09-02' for x in self.line['offers'][:3]))
        self.assertIn('HOLD', self.line['alternates'][0]['why_equivalent'])
        self.assertIsNone(self.line['offers'][-1]['moq'])
        self.assertIsNone(self.line['offers'][-1]['lead_time'])

    def test_no_eligible_offer_without_conditional_candidate(self):
        self.line['offers'] = self.line['offers'][:3]
        self.assertIsNone(s.line_cost(self.line, 1))
        self.assertEqual(s.priced_domains(self.line), set())

if __name__ == '__main__':
    unittest.main()
