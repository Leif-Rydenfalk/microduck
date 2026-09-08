from pathlib import Path
import importlib.util,unittest,copy
D=Path(__file__).resolve().parent
def module(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
old=module(D/'baseline/cad/mate.py','old_mate');new=module(D/'cad/mate.py','candidate_mate');compat=module(D/'compat.py','candidate_compat')
def interfaces():
 return ({'name':'horn','frame':{'origin_mm':[14.5,0,0],'z_axis':[1,0,0],'x_axis':[0,0,1]},'pcd_mm':12,'screws':4,'tap_d_mm':1.6}, {'name':'horn_face','role':'horn_face','frame':{'origin_mm':[0,0,2],'z_axis':[0,0,1],'x_axis':[1,0,0]},'pcd_mm':12,'screws':4,'clearance_d_mm':2.2,'centre_d_mm':6})
class Candidate(unittest.TestCase):
 def test_32_nominal_transforms_equal_baseline(self):
  a,b=interfaces()
  for idx in range(4):
   for opposed in [False,True]:
    for clock in [0,45]:
     for dz in [0,1.25]:
      p={'index':idx,'opposed':opposed,'clock_deg':clock,'seat_dz_mm':dz};r=new.nominal_transform(a,b,p);self.assertEqual(r['nominal_transform'],old.mate(a,b,p)['transform']);self.assertFalse(set(r)&{'transform','joint','dof_left','adds'});self.assertEqual(r['required_hardware']['quantity'],4)
 def test_physical_mate_refuses_even_claimed_approval(self):
  a,b=interfaces()
  for p in [{},{'index':0},{'index':0,'hardware_verified':True,'part_ref':'part:screw-m2-iso4762'}]:
   with self.assertRaisesRegex(ValueError,'CANNOT DETERMINE'):new.mate(a,b,p)
 def test_old_six_mm_fails(self):
  a,b=interfaces();a['tap_depth_mm']=6;v=compat.compatible(a,b);self.assertEqual(v['verdict'],'FAIL');self.assertEqual(next(c for c in v['checks'] if c['check']=='manufacturer_depth_limit')['verdict'],'FAIL')
 def test_diameter_never_approves_metric_thread(self):
  a,b=interfaces();a['tap_depth_mm']=3;a['thread']='M2x0.4';v=compat.compatible(a,b);self.assertEqual(v['verdict'],'CANNOT DETERMINE');self.assertEqual(next(c for c in v['checks'] if c['check']=='tapping_hardware_identity')['verdict'],'CANNOT DETERMINE');self.assertNotIn('horn_tap',[c['check'] for c in v['checks']])
 def test_conflicting_depth_and_nonfinite_refused(self):
  a,b=interfaces();a['maximum_pilot_depth_mm']=3
  for bad in [6,float('nan'),float('inf'),0,-1,'unknown']:
   a['tap_depth_mm']=bad;v=compat.compatible(a,b);self.assertEqual(v['verdict'],'FAIL')
 def test_geometry_failure_preserved(self):
  a,b=interfaces();b['pcd_mm']=10;self.assertEqual(compat.compatible(a,b)['verdict'],'FAIL')
 def test_nominal_missing_index_refused(self):
  a,b=interfaces()
  with self.assertRaisesRegex(ValueError,'REQUIRED'):new.nominal_transform(a,b)
if __name__=='__main__':unittest.main()
