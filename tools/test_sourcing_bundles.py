"""Bundle accounting must follow the selected offer and whole-batch shortfall."""
import copy
import unittest
import gen_sourcing as sourcing


class BundleQuantities(unittest.TestCase):
    def setUp(self):
        self.lines = copy.deepcopy(sourcing.DATA['lines'])
        self.servo = next(x for x in self.lines if x['id'] == 'B1')
        self.cables = next(x for x in self.lines if x['id'] == 'B2')

    def cost(self, robots):
        return sourcing.line_cost(self.cables, robots, self.lines)

    def test_verified_retail_bundle_and_batch_rounding(self):
        for robots, packs, per_robot in [(1, 1, 15.5), (100, 10, 1.55), (1000, 100, 1.55)]:
            with self.subTest(robots=robots):
                c = self.cost(robots)
                self.assertEqual(c['order_quantity'], packs)
                self.assertEqual(c['included_pieces'], 15 * robots)
                self.assertEqual(c['required_pieces'], 16 * robots)
                self.assertAlmostEqual(c['per_robot'], per_robot)
                self.assertIn('2026-09-08', c['quantity_basis'])

    def test_unverified_selected_vendor_gets_no_credit(self):
        # Retain the verified offer but make the other USD offer cheaper.
        self.servo['offers'][1]['tiers'] = [[1, 20]]
        for robots, packs in [(1, 2), (100, 160), (1000, 1600)]:
            with self.subTest(robots=robots):
                c = self.cost(robots)
                self.assertEqual(c['included_pieces'], 0)
                self.assertEqual(c['order_quantity'], packs)
                self.assertIn('no verified bundle', c['quantity_basis'])

    def test_zero_shortfall_needs_no_purchase_or_moq(self):
        self.cables['quantity_rule']['required_pieces_per_robot'] = 15
        for robots in (1, 100, 1000):
            c = self.cost(robots)
            self.assertEqual(c['order_quantity'], 0)
            self.assertEqual(c['per_robot'], 0)
            self.assertFalse(c['moq_exceeds'])

    def test_missing_evidence_date_gets_no_credit(self):
        del self.servo['offers'][0]['included_items'][0]['fetched']
        self.assertEqual(self.cost(100)['order_quantity'], 160)

    def test_rendered_quantity_is_net_not_legacy_ceiling(self):
        row = sourcing.rollup_rows([self.cables])
        self.assertIn('batch-dependent', row)
        self.assertIn('@100: 1600 - 1500 = 100 leads; 10 packs', row)
        self.assertIn('100 robots: 1600 leads required - 1500 verified bundled',
                      sourcing.line_block(self.cables))
        supplier = next(x for x in sourcing.DATA['rfq_suppliers'] if x['key'] == 'robotis')
        self.assertIn('1 / 10 / 100 packs', sourcing.rfq_line_table(supplier))

    def test_existing_guard(self):
        self.assertEqual(sourcing.selfcheck(), 16)


if __name__ == '__main__':
    unittest.main()
