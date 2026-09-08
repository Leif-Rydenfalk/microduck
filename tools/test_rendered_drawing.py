"""Drawing regressions. Run through ce-cad/bin/cad after generating the shin.

Uses canonical artifacts and temporary synthetic fixtures. No scratch prototype
is needed. Deliberately corrupts every new source/serialization acceptance path.
"""
import contextlib
import io
import json
import re
import tempfile
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from cecad import inspect, sheets, sheetcheck, pdfsheet
from cecad.core import Part
from cecad.render import render
from cecad.sheets import Sheet, verify_sheet
sys.path.insert(0, str(Path(__file__).resolve().parent))
from rendered_drawing import verify_render_scales

ROOT = Path(__file__).resolve().parent.parent


def groove_regression(tmp):
    part = Part('groove_regression').cyl(40, 10)
    cutter = Part('groove_tool').cyl(20, 3, at=(0, 0, 7))
    cutter.cyl(10, 3, at=(0, 0, 7), op='cut')
    part.merge(cutter, op='cut')
    assert any(g.od == 20 for g in inspect.grooves(part))
    sheet = Sheet(part, size='A3')
    sheet.view('top')
    svg = Path(sheet.write(str(tmp/'groove'), quiet=True)['svg'])
    raw = svg.read_text().replace('</svg>', '<text x="30" y="30" font-size="3.5">Ø20.00</text></svg>')
    svg.write_text(raw)

    def rejected():
        log = io.StringIO()
        with contextlib.redirect_stdout(log):
            verify_sheet(sheet, str(svg), part)
        return any('[FAIL]' in line and 'every Ø on the sheet' in line for line in log.getvalue().splitlines())

    assert not rejected()
    svg.write_text(raw.replace('Ø20.00', 'Ø21.00'))
    assert rejected(), 'Invented groove diameter must fail'
    svg.write_text(raw)
    old = sheets.measure_grooves
    try:
        sheets.measure_grooves = lambda obj: []
        assert rejected(), 'Removing groove inspection must reproduce the defect'
    finally:
        sheets.measure_grooves = old
    sheet.feature_schedule([{'what':'feature', 'value_mm':1}], general_tolerance='CANNOT DETERMINE — measure coupon')
    assert all(sheets.text_width(text, height) <= 114.01 for kind, text, height in sheet._bottom_lines(120) if kind == 'head')
    print('PASS groove measurement, fabricated diameter, old defect and heading containment')


def detail_regression():
    part = Part('detail_regression').cyl(4, 3)
    part.cyl(12, 3, at=(8, 0, 0))
    part.cyl(10, 3, at=(40, 0, 0))
    sheet = Sheet(part, size='A0', scale=(1, 1))
    sheet.view('top')
    view = sheet.detail('top', (0, 0), 4, scale=(4, 1))
    sheet.build()
    view.ox = view.oy = 200.
    view.annotation_box = (50., 50., sheet.W-50., sheet.H-50.)
    labels = lambda: {p['s'] for p in sheet._radius_prims(view, []) if p['k']=='text'}
    assert {'R2.00', 'R6.00'} <= labels()
    assert 'R5.00' not in labels()
    saved = view.detail
    try:
        view.detail = None
        assert 'R5.00' in labels(), 'Unclipped selection must reproduce remote leader'
    finally:
        view.detail = saved
    sheet._radius_prims(view, [(0, 0, sheet.W, sheet.H)])
    assert set(view._radii_missing) == {2., 6.}, 'Unplaceable real leaders must remain failures'
    plain = Sheet(part, size='A0')
    plain.view('top', holes=False, dims=False)
    plain.build()  # A view without overall dimensions must still annotate.
    print('PASS clipped/intersecting/remote radius selection and missing-leader control')


def caption_regression(canonical, tmp):
    svg = canonical/'microduck-shin.svg'
    solid = json.loads((canonical/'sheetcheck-current.json').read_text())['solid']
    grade = lambda path: sheetcheck.grade_sheet(str(path), slug='microduck-shin', use_kernel=False, solid=solid)
    assert grade(svg)['checks']['iso']['verdict'] == 'PASS'
    old = sheetcheck._VIEW_LABEL_RE
    try:
        sheetcheck._VIEW_LABEL_RE = re.compile('.*')
        assert grade(svg)['checks']['iso']['verdict'] == 'FAIL'
    finally:
        sheetcheck._VIEW_LABEL_RE = old
    raw = svg.read_text()
    tag = re.search(r'<image\b[^>]*>', raw)
    small = re.sub(r'width="([\d.]+)"', lambda m:'width="'+str(float(m[1])/10)+'"', tag[0], count=1)
    bad = tmp/'undersized.svg'
    bad.write_text(raw[:tag.start()]+small+raw[tag.end():])
    result = grade(bad)
    assert result['checks']['iso']['verdict'] == 'FAIL'
    assert result['checks']['renders']['verdict'] == 'FAIL'
    print('PASS real captions, old any-text defect and undersized-render controls')


def scale_regression(canonical, tmp):
    part = Part('scale_fixture').box(20, 10, 4)
    raster = tmp/'box.png'
    frame = {}
    args = dict(view=(90, -90), W=220, H=220, ss=2, edges=False, bg=1., mode='cad', verbose=False)
    render(part, str(raster), framing=frame, **args)
    assert abs(frame['pixels_per_model_mm']-10.) < 1e-8
    def pixel_extent():
        a = np.asarray(Image.open(raster).convert('RGB'))
        ys, xs = np.where(a.min(axis=2) < 245)
        return xs.max()-xs.min()+1, ys.max()-ys.min()+1
    assert all(abs(a-b)<=3 for a,b in zip(pixel_extent(), (200,100)))
    cached = {}
    render(part, str(raster), framing=cached, **args)
    assert cached == frame
    render(part, str(raster), framing=cached, ortho_pixels_per_mm=5., **args)
    assert cached['pixels_per_model_mm'] == 5.
    assert all(abs(a-b)<=3 for a,b in zip(pixel_extent(), (100,50))), 'Explicit zoom must isolate cache and affect real pixels'
    fit_center=list(cached['center_projected_mm'])
    shifted=[fit_center[0]+4.,fit_center[1]+3.]
    render(part,str(raster),framing=cached,ortho_pixels_per_mm=5.,ortho_center_projected_mm=shifted,**args)
    assert cached['center_projected_mm']==shifted
    a=np.asarray(Image.open(raster).convert('RGB')); ys,xs=np.where(a.min(axis=2)<245)
    assert abs((xs.min()+xs.max())/2-(110-4*5))<2
    assert abs((ys.min()+ys.max())/2-(110+3*5))<2
    assert all(abs(a-b)<=3 for a,b in zip(pixel_extent(),(100,50))), 'Shift must not stretch either axis'
    hit={}
    render(part,str(raster),framing=hit,ortho_pixels_per_mm=5.,ortho_center_projected_mm=shifted,**args)
    assert hit==cached
    from radius_locators import paper_point
    panel={'box_mm':[0.,0.,220.,220.],'framing':hit}
    r,u=hit['camera_right'],hit['camera_up']
    feature=[shifted[0]*r[i]+shifted[1]*u[i] for i in range(3)]
    assert max(abs(v-110) for v in paper_point(feature,panel))<1e-8
    feature_part=Part('centre_feature_fixture').cyl(8.,2.,at=(7.,-3.,0.))
    render(feature_part,str(raster),framing=cached,ortho_pixels_per_mm=5.,
           ortho_center_projected_mm=(7.,-3.),**args)
    a=np.asarray(Image.open(raster).convert('RGB'));ys,xs=np.where(a.min(axis=2)<245)
    assert abs((xs.min()+xs.max())/2-110)<2 and abs((ys.min()+ys.max())/2-110)<2
    assert all(abs(a-b)<=3 for a,b in zip(pixel_extent(),(40,40))), 'Known circular feature must land at camera centre without stretching'
    for invalid in ((0.,), (0.,1.,2.), (float('nan'),0.),(0.,float('inf')), 3., '12', b'12'):
        try:
            render(part,str(raster),ortho_center_projected_mm=invalid,**args)
            raise AssertionError('Invalid camera centre accepted')
        except ValueError:pass
    for misuse in ({'projection':'perspective'},{'title':'Has title'}):
        try:
            render(part,str(raster),ortho_center_projected_mm=(0.,0.),**dict(args,**misuse))
            raise AssertionError('Unsupported centre projection accepted')
        except ValueError:pass
    for invalid in (0., -1., float('nan'), float('inf')):
        try:
            render(part, str(raster), ortho_pixels_per_mm=invalid, **args)
            raise AssertionError('Invalid scale accepted')
        except ValueError:
            pass
    source = canonical/'microduck-shin.svg'
    panels = json.loads((canonical/'layout-evidence.json').read_text())['panels']
    assert verify_render_scales(source, panels)['verdict'] == 'PASS'
    bad = tmp/'bad-scale.svg'
    raw = source.read_text()
    bad.write_text(re.sub(r'RENDER 1 / SCALE [0-9.]+:1', 'RENDER 1 / SCALE 0.00000:1', raw, count=1))
    assert verify_render_scales(bad, panels)['verdict'] == 'FAIL'
    import xml.etree.ElementTree as ET
    tree = ET.parse(source)
    image = next(e for e in tree.iter() if e.tag.endswith('}image'))
    image.set('width', str(float(image.get('width'))*1.1))
    tree.write(bad)
    assert verify_render_scales(bad, panels)['verdict'] == 'FAIL'
    print('PASS known solid pixel scale, cache isolation, invalid zoom, label and paper-width controls')


def supplemental_scale_regression(canonical,tmp):
    import xml.etree.ElementTree as ET
    source=canonical/'microduck-shin.svg'
    panels=json.loads((canonical/'layout-evidence.json').read_text())['panels']
    groups=[{'kind':'principal','renders':[1,2,3,4]}, {'kind':'detail','renders':[5,6]}]
    assert verify_render_scales(source,panels,groups)['verdict']=='FAIL', 'Unenlarged details must fail'
    tree=ET.parse(source)
    images=[e for e in tree.iter() if e.tag.endswith('}image')]
    for i in (4,5):
        for key in ('width','height'):
            images[i].set(key,str(float(images[i].get(key))*1.5))
        old=f"RENDER {i+1} / SCALE {panels[i]['paper_scale']:.5f}:1"
        for e in tree.iter():
            if e.tag.endswith('}text') and e.text==old:
                e.text=f"RENDER {i+1} / SCALE {panels[i]['paper_scale']*1.5:.5f}:1"
    path=tmp/'supplemental-scale.svg';tree.write(path)
    assert verify_render_scales(path,panels)['verdict']=='FAIL', 'Default shared-scale contract must remain unchanged'
    assert verify_render_scales(path,panels,groups)['verdict']=='PASS'
    assert verify_render_scales(path,panels,[groups[0],{'kind':'detail','renders':[4,5,6]}])['verdict']=='FAIL'
    raw=path.read_text();path.write_text(raw.replace('RENDER 5 / SCALE','ALTERED / SCALE'))
    assert verify_render_scales(path,panels,groups)['verdict']=='FAIL'
    tree.write(path)
    images[4].set('width',str(float(images[4].get('width'))*1.1));tree.write(path)
    assert verify_render_scales(path,panels,groups)['verdict']=='FAIL', 'Stretch must fail even with explicit scale groups'
    print('PASS supplemental explicit groups, unchanged default, unenlarged/duplicate/label/stretch negative controls')
    from rendered_details import verify_context
    import copy
    src=Path(panels[0]['raster']); actual=tmp/'context.png';actual.write_bytes(src.read_bytes())
    frame=panels[0]['framing']
    assert verify_context(src,actual,frame,copy.deepcopy(frame))['verdict']=='PASS'
    for kind in ('pixels','camera'):
        actual.write_bytes(src.read_bytes()); changed=copy.deepcopy(frame)
        if kind=='pixels':actual.write_bytes(actual.read_bytes()+b'changed')
        else:changed['center_projected_mm'][0]+=.1
        try:
            verify_context(src,actual,frame,changed)
            raise AssertionError('Stale context accepted: '+kind)
        except ValueError:pass
    print('PASS exact context pixels/camera and substituted-pixel/shifted-frame controls')


def filament_note_regression():
    from cecad.autosheet import _filament_note
    for value in (None,0.,-1.,float('nan'),float('inf')):
        text=_filament_note('PLA',{'filament_g':value,'layers':290})
        assert 'mass CANNOT DETERMINE' in text and '~0' not in text
        assert '290 modelled layers @ 0.2 mm' in text
    assert 'mass CANNOT DETERMINE' in _filament_note('PLA',{'layers':290})
    small=_filament_note('PLA',{'filament_g':.1,'layers':1})
    assert '~0.1 g' in small and '~0 g' not in small
    assert '~0.01 g' in _filament_note('PLA',{'filament_g':.01,'layers':1})
    positive=_filament_note('PLA',{'filament_g':4.2,'layers':290})
    assert '~4.2 g (shell/infill estimate, not weighed)' in positive
    print('PASS missing/null/zero/nonfinite mass refusal, nonzero small mass, explicit model estimate and sourced layer count')


def main():
    canonical = ROOT/'out/drawings/microduck-shin'
    with tempfile.TemporaryDirectory(prefix='microduck-drawing-tests-') as td:
        tmp = Path(td)
        groove_regression(tmp)
        detail_regression()
        caption_regression(canonical, tmp)
        scale_regression(canonical, tmp)
        supplemental_scale_regression(canonical,tmp)
        filament_note_regression()
        assert pdfsheet.self_test() is True
        cases,passed=sheetcheck.self_test(workdir=str(tmp/'sheetcheck'))
        assert passed, 'Core checker self-test failures: '+str([c['case'] for c in cases if not c['ok']])
    print('PASS all rendered drawing regressions')


if __name__ == '__main__':
    main()
