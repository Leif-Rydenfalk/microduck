"""Reject incompatible modules without deleting historical price evidence."""
import copy,json,unittest
from pathlib import Path
import gen_sourcing as s
class CameraCompatibility(unittest.TestCase):
 def setUp(self):self.line=copy.deepcopy(next(x for x in s.DATA['lines'] if x['id']=='B6'))
 def test_rejected_cheap_offer_never_selected(self):
  rejected=next(x for x in self.line['offers'] if x['sku']=='102110719')
  rejected['tiers']=[[1,0.01]]
  for n in [1,100,1000]:self.assertEqual(s.line_cost(self.line,n)['vendor'],'UCTRONICS (Arducam\'s US shop)')
  self.assertNotIn('seeedstudio.com',s.priced_domains(self.line))
 def test_compatibility_rejection_independent_of_rollup_note(self):
  for o in self.line['offers']:o['compatibility_status']='rejected';o.pop('excluded_from_rollup',None)
  self.assertIsNone(s.line_cost(self.line,1));self.assertEqual(s.priced_domains(self.line),set())
 def test_no_original_identity_pass_or_deleted_price(self):
  self.assertEqual(self.line['verdict'],'CANNOT DETERMINE')
  rejected=next(x for x in self.line['offers'] if x['sku']=='102110719')
  self.assertEqual(rejected['tiers'],[[1,15.9],[10,12.5]])
  self.assertIn('REJECTED',s.offer_rows(self.line))
 def test_nonselected_valid_second_source_still_counts(self):
  for line_id in ["C1","C2"]:
   line=next(x for x in s.DATA["lines"] if x["id"]==line_id)
   self.assertIn("lcsc.com",s.priced_domains(line))
   self.assertTrue(any(o.get("excluded_from_rollup") for o in line["offers"]))
 def test_camera_proxy_is_not_cut_length(self):
  d=json.loads((Path(s.REPO)/'wiring/cables.json').read_text())
  def find(v):
   if isinstance(v,dict):
    if v.get('id')=='csi-radxa-camera':return v
    for x in v.values():
     r=find(x)
     if r:return r
   if isinstance(v,list):
    for x in v:
     r=find(x)
     if r:return r
  row=find(d)
  self.assertIsNone(row['cable_mm']);self.assertIsNone(row['floor_mm'])
  self.assertEqual(row['proxy_distance_mm'],13.3);self.assertEqual(row['historical_rounded_proxy_mm'],15)
if __name__=='__main__':unittest.main()
