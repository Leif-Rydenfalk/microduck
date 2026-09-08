"""Whole sets must satisfy every required item; interface rejects remain effective."""
import copy
import unittest
import gen_sourcing as s

class WholePackages(unittest.TestCase):
    def setUp(self):
        self.power = copy.deepcopy(next(x for x in s.DATA['lines'] if x['id'] == 'B4'))
        self.tof = copy.deepcopy(next(x for x in s.DATA['lines'] if x['id'] == 'B9'))

    def test_one_charger_per_robot_buys_whole_sets(self):
        for n in [1, 100, 1000]:
            c = s.line_cost(self.power, n)
            self.assertEqual(c['vendor'], 'NextBatteries')
            self.assertEqual(c['order_quantity'], n)
            self.assertEqual(c['received_items'], {'battery': 2*n, 'dual_charger': n})
            self.assertEqual(c['required_items'], {'battery': n, 'dual_charger': n})
            self.assertAlmostEqual(c['per_robot'], 49.9)
            self.assertIn('no shared chargers', c['quantity_basis'])

    def test_cheap_pack_only_cannot_satisfy_charger_requirement(self):
        o = self.power['offers'][1]
        o.pop('excluded_from_rollup', None)
        o['tiers'] = [[1, .01]]
        self.assertIsNone(s.purchase_quantity(self.power, 100, offer=o))
        self.assertEqual(s.line_cost(self.power, 100)['vendor'], 'NextBatteries')

    def test_missing_package_evidence_gets_no_bundle_credit(self):
        for o in self.power['offers']:
            o['package'].pop('fetched', None)
        self.assertIsNone(s.line_cost(self.power, 1))

    def test_alternate_kit_selected_on_full_price(self):
        self.power['offers'][0]['tiers'] = [[1, 60]]
        for n in [1, 100, 1000]:
            c = s.line_cost(self.power, n)
            self.assertEqual(c['vendor'], 'Neewer (charger set)')
            self.assertEqual(c['received_items']['dual_charger'], n)
            self.assertAlmostEqual(c['per_robot'], 49.99)

    def test_st_two_board_pack_rounds_entire_order(self):
        o = next(x for x in self.tof['offers'] if x['sku'].startswith('VL53L5CX-SATEL'))
        for n, count in [(1,1),(3,2),(100,50),(1000,500)]:
            c = s.purchase_quantity(self.tof, n, offer=o)
            self.assertEqual(c['order_quantity'], count)
            self.assertEqual(c['received_items']['tof_module'], count*2)
        self.assertEqual(o['tiers'], [[1,22.7]])
        self.assertFalse(s.usable(o))
        # Verify package-tier arithmetic independently of its actual rejection.
        o.pop('excluded_from_rollup', None);o['compatibility_status']='conditional'
        self.tof['offers']=[o]
        self.assertAlmostEqual(s.line_cost(self.tof,1)['per_robot'],22.7)
        self.assertAlmostEqual(s.line_cost(self.tof,100)['per_robot'],11.35)

    def test_interface_rejected_cheap_boards_never_selected(self):
        for o in self.tof['offers']:
            if o.get('compatibility_status')=='rejected':
                o['tiers']=[[1,.001]];o.pop('excluded_from_rollup',None)
        for n in [1,100,1000]:
            c=s.line_cost(self.tof,n)
            self.assertIn('SEN-19013',c['detail'])
            self.assertEqual(c['received_items']['tof_module'],n)
        self.assertEqual(s.priced_domains(self.tof),{'sparkfun.com'})
        self.assertEqual(self.tof['verdict'],'CANNOT DETERMINE')

    def test_moq_updates_delivered_package_contents(self):
        self.power['offers']=[self.power['offers'][0]]
        self.power['offers'][0]['moq']=3
        c=s.line_cost(self.power,1)
        self.assertEqual(c['order_quantity'],3)
        self.assertEqual(c['received_items'],{'battery':6,'dual_charger':3})
        self.assertAlmostEqual(c['per_robot'],149.7)
        self.assertTrue(c['moq_exceeds'])

    def test_rendered_totals_are_whole_kit_provenanced(self):
        self.assertIn('one battery and one dual charger per robot',s.line_block(self.power))
        self.assertIn('1000 whole kits',s.rollup_rows([self.power]))
        supplier=next(x for x in s.DATA['rfq_suppliers'] if 'B4' in x['lines'])
        self.assertIn('1 / 100 / 1,000 whole packages',s.rfq_line_table(supplier))

if __name__=='__main__':unittest.main()
