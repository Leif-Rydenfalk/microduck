"""Unverified cable bundle claims cannot erase connector kit requirements."""
import copy
import unittest
import gen_sourcing as s
class QwiicBundle(unittest.TestCase):
    def test_no_unverified_tof_credit_for_connector_kit(self):
        lines=copy.deepcopy(s.DATA['lines'])
        c=next(x for x in lines if x['id']=='C2')
        tof=next(x for x in lines if x['id']=='B9')
        before={n:s.line_cost(c,n,lines)['per_robot'] for n in [1,100,1000]}
        for offer in tof['offers']:
            offer['note']='Cable included (unverified test mutation)'
            offer['included_items']=[{'item_key':'qwiic_cable','qty_per_unit':999}]
        for n in [1,100,1000]:
            result=s.line_cost(c,n,lines)
            self.assertEqual(result['per_robot'],before[n])
            self.assertGreater(result['per_robot'],0)
            self.assertIn('SHR-04V-S-B x2',result['detail'])
            self.assertIn('GHR-02V-S x2',result['detail'])
        self.assertIn('lcsc.com',s.priced_domains(c))
        self.assertIn('No cable inclusion',s.alt_rows(c))
        self.assertNotIn('every ToF breakout',s.alt_rows(c))
if __name__=='__main__':unittest.main()
