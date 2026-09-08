"""A detail excludes remote radii but retains intersecting real arcs."""
from cecad.core import Part
from cecad.sheets import Sheet
p=Part('detail_radius_regression').cyl(4,3)
p.cyl(12,3,at=(8,0,0))
p.cyl(10,3,at=(40,0,0))
sh=Sheet(p,size='A0',scale=(1,1))
sh.view('top')
v=sh.detail('top',(0,0),4,scale=(4,1))
sh.build()
v.ox=200.;v.oy=200.;v.annotation_box=(50.,50.,sh.W-50.,sh.H-50.)
def labels():
 return {x['s'] for x in sh._radius_prims(v,[]) if x['k']=='text'}
actual=labels()
assert 'R2.00' in actual and 'R6.00' in actual, actual
assert 'R5.00' not in actual, actual
saved=v.detail
v.detail=None
assert 'R5.00' in labels(), 'Old unclipped selection must reproduce the remote leader'
v.detail=saved
sh._radius_prims(v,[(0,0,sh.W,sh.H)])
assert set(v._radii_missing)=={2.,6.}, v._radii_missing
print('PASS: in-detail and intersecting radii retained; remote radius excluded; old behavior reproduced; unplaceable real leaders remain failures')
