import copy,importlib.util,json,unittest,hashlib,tempfile
from unittest.mock import patch
from pathlib import Path
R=Path(__file__).resolve().parent.parent
sp=importlib.util.spec_from_file_location('fastener_runs',R/'tools/fastener_runs.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
class ServoLimits(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  fixture=R/'research/servo-fastener-restriction-2026-09-08/historical-runs.json'
  assert hashlib.sha256(fixture.read_bytes()).hexdigest()=='82f1403719d94f9c7dc890ebc3226b256d0e08d35e1927f2a77737f2d5ba8479'
  cls.runs=json.loads(fixture.read_text())['runs'];cls.servo=[r for r in cls.runs if r.get('pilot_mesh')=='xl330'];assert len(cls.servo)==52
 def classify(self,r):
  g=copy.deepcopy(r['features'])
  for h in g:h['axis_world']=r['axis_world']
  return m.classify(g)
 def test_all_real_servo_runs_withdraw_lengths_preserve_geometry(self):
  for old in self.servo:
   r=self.classify(old);self.assertEqual(r['verdict'],'CANNOT DETERMINE');self.assertIsNone(r['stocked_length_mm']);self.assertEqual(r['stocked_lengths_in_window_mm'],[]);self.assertIsNone(r['minimum_engagement_mm']);self.assertIsNone(r['engagement_available_mm']);self.assertEqual(r['engagement_maximum_mm'],3.0);self.assertEqual(r['mesh_pilot_depth_mm'],6.0)
   for k in ['features','head_point_world_mm','insertion_axis_world','pilot_endpoint','grip_mm']:self.assertEqual(r[k],old[k])
   self.assertEqual(r['historical_mesh_rule_proposal']['stocked_length_mm'],old['stocked_length_mm']);self.assertEqual(r['thread_requirement']['manufacturer_callout'],'M2 Tapping Screw')
 def test_shorter_mesh_span_not_expanded(self):
  r=copy.deepcopy(self.servo[0]);r['engagement_available_mm']=2.0;p=r['features'][-1];got=m.restrict_xl330_face(r,p);self.assertEqual(got['engagement_maximum_mm'],2.0);self.assertIsNone(got['stocked_length_mm'])
 def test_unrelated_holes_unchanged(self):
  for changes in [{'mesh':'other'},{'index':8},{'d_mm':2.0},{'cls':'clearance'}]:
   r=copy.deepcopy(self.servo[0]);p=dict(r['features'][-1],**changes);old=copy.deepcopy(r);self.assertEqual(m.restrict_xl330_face(r,p),old)
 def test_nonservo_real_lengths_unchanged(self):
  for old in self.runs:
   if old.get('stocked_length_mm') is not None and old.get('pilot_mesh')!='xl330':
    r=self.classify(old)
    for k in ['stocked_length_mm','length_window_mm','grip_mm','verdict','features']:self.assertEqual(r[k],old[k])
 def test_manufacturer_source_hash(self):self.assertEqual(hashlib.sha256((R/m.XL330_DRAWING).read_bytes()).hexdigest(),m.XL330_DRAWING_SHA256)
 def test_live_source_mapping_passes(self):
  meshes,_=m.load();self.assertEqual(len([f for f in meshes['xl330']['features'] if f['index'] in range(8) and f['d_mm']==1.6]),8)
 def test_changed_feature_or_drawing_fails_before_output_mutation(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);out=d/'runs.json';out.write_text('sentinel existing evidence')
   for kind in ['feature','drawing']:
    source=Path(m.FEAT) if kind=='feature' else R/m.XL330_DRAWING
    changed=d/(kind+'.source');changed.write_bytes(source.read_bytes()+b'changed')
    variable='FEAT' if kind=='feature' else 'XL330_DRAWING'
    with patch.object(m,variable,str(changed)),patch.object(m,'OUT',str(out)):
     with self.assertRaisesRegex(ValueError,'hash changed'):m.main()
    self.assertEqual(out.read_text(),'sentinel existing evidence')
 def test_preserved_historical_excess_count(self):
  excess=sum(r['stocked_length_mm']-r['grip_mm']>3.0+1e-6 for r in self.servo);self.assertEqual(excess,35)
if __name__=='__main__':unittest.main()
