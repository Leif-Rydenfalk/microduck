"""Run with ce-cad/bin/cad; measured locator controls, then optional shin ledger."""
import json
import copy
import tempfile
import sys
from pathlib import Path
import FreeCAD as App
import Part
sys.path.insert(0, str(Path(__file__).resolve().parent))
from radius_locators import paper_point, visible, occurrences, locate, verify_candidates, annotate, coordinate_locators, verify_printed

panel = {'box_mm':[10.,20.,200.,100.], 'framing':{
    'projection':'ortho','image_px':[1000,500],'pixels_per_model_mm':10.,
    'camera_right':[1.,0.,0.],'camera_up':[0.,1.,0.],
    'center_projected_mm':[0.,0.]}}
assert paper_point([2.,3.,4.], panel) == [114.,76.]
bad = dict(panel, box_mm=[10.,20.,201.,100.])
try:
    paper_point([2.,3.,4.], bad)
    raise AssertionError('Stretched raster accepted')
except ValueError:
    pass
cylinder = Part.makeCylinder(3.,10.)
assert visible(cylinder,[0.,0.,10.],[0.,0.,1.]) is True
assert visible(cylinder,[0.,0.,0.],[0.,0.,1.]) is False
thin = Part.makeBox(10.,10.,.028,App.Vector(-5.,-5.,1.))
assert visible(thin,[0.,0.,0.],[0.,0.,1.]) is False, 'Thin wall must occlude'
class Broken:
    BoundBox = thin.BoundBox
    def common(self, other):
        raise RuntimeError('Deliberate failed boolean')
assert visible(Broken(),[0.,0.,0.],[0.,0.,1.]) is None
rows = occurrences(cylinder)
assert len(rows) == 2 and all(r['radius_mm'] == 3. for r in rows)
assert len({r['source_edge'] for r in rows}) == 2, 'Equal radii must remain separate occurrences'
for row in rows:
    edge = cylinder.Edges[int(row['source_edge'][4:])-1]
    for point in row['samples_mm']:
        assert edge.distToShape(Part.Vertex(App.Vector(*point)))[0] < 1e-8
ledger = locate(cylinder,[panel])
assert ledger['visible_candidates'] == 1 and len(ledger['unresolved']) == 1
preferred=locate(cylinder,[panel,panel],[2,1])
assert next(r['locator']['panel'] for r in preferred['occurrences'] if r['locator'])==2
try:
    locate(cylinder,[panel,panel],[1,1])
    raise AssertionError('Duplicate view selection must fail')
except ValueError:pass
assert verify_candidates(cylinder,[panel],ledger)['verdict'] == 'PASS'
for mutation in ('radius','paper','point','coverage','trim','axis'):
    bad = copy.deepcopy(ledger)
    row = next(r for r in bad['occurrences'] if r['locator'])
    if mutation == 'radius': row['radius_mm'] += .1
    if mutation == 'paper': row['locator']['paper_mm'][0] += .1
    if mutation == 'point': row['locator']['point_mm'][0] += .1
    if mutation == 'coverage': bad['occurrences'].pop()
    if mutation == 'trim': row['start_mm'][0] += .1
    if mutation == 'axis': row['axis'][0] += .1
    assert verify_candidates(cylinder,[panel],bad)['verdict'] == 'FAIL', mutation
from PIL import Image
from cecad import drawing as D
with tempfile.TemporaryDirectory() as tmp:
    raster=Path(tmp)/'white.png'; Image.new('RGB',(1000,500),'white').save(raster)
    printed_panel=dict(panel,raster=str(raster))
    annotations=annotate([], [printed_panel], ledger)
    assert ledger['printed_count']==1
    annotations+=coordinate_locators(annotations,ledger,[0.,0.,0.],(10.,130.,290.,195.))
    assert ledger['coordinate_count']==1 and not ledger['unlocated']
    path=Path(tmp)/'locators.svg'
    D.write_svg(annotations,str(path),page=(300.,200.),quiet=True)
    assert verify_printed(path,ledger,200.)['verdict']=='PASS'
    raw=path.read_text()
    path.write_text(raw.replace('E001','OMITTED').replace('E002','OMITTED'))
    assert verify_printed(path,ledger,200.)['verdict']=='FAIL'
    path.write_text(raw.replace('CENTRE','CORRUPTED'))
    assert verify_printed(path,ledger,200.)['verdict']=='FAIL'
    path.write_text(raw.replace('<line ','<notline '))
    assert verify_printed(path,ledger,200.)['verdict']=='FAIL'
print('PASS locator projection, aspect rejection, front/back/thin-wall visibility, unknown boolean, equal-radius occurrences and trimmed-edge points')

if '--shin' in sys.argv:
    from cecad import triad
    root = Path(__file__).resolve().parent.parent
    out = root/'out/drawings/microduck-shin'
    part = triad.load(App.newDocument('shin_locator_audit'),'part:microduck-shin')
    panels = json.loads((out/'layout-evidence.json').read_text())['panels']
    result = locate(part.shape,panels)
    result['candidate_readback'] = verify_candidates(part.shape,panels,result)
    assert result['candidate_readback']['verdict'] == 'PASS'
    result['source'] = 'part:microduck-shin live BRep; edge indices valid only for this topology'
    (out/'radius-locator-candidates.json').write_text(json.dumps(result,indent=1))
    print('SHIN',result['visible_candidates'],'/',result['count'],'visible candidates; unresolved',result['unresolved'])
