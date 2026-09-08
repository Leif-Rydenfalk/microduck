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


def main():
    canonical = ROOT/'out/drawings/microduck-shin'
    with tempfile.TemporaryDirectory(prefix='microduck-drawing-tests-') as td:
        tmp = Path(td)
        groove_regression(tmp)
        detail_regression()
        caption_regression(canonical, tmp)
        scale_regression(canonical, tmp)
        pdfsheet.self_test()
        sheetcheck.self_test(workdir=str(tmp/'sheetcheck'))
    print('PASS all rendered drawing regressions')


if __name__ == '__main__':
    main()
