"""Shin-discovered drawing regressions. Run with ce-cad/bin/cad."""
import contextlib
import io
import os
from cecad.core import Part
from cecad import sheets, inspect
from cecad.sheets import Sheet, verify_sheet

out = os.path.dirname(os.path.abspath(__file__))
p = Part('annular_groove_regression')
p.cyl(40, 10)
cutter = Part('annular_channel').cyl(20, 3, at=(0, 0, 7))
cutter.cyl(10, 3, at=(0, 0, 7), op='cut')
p.merge(cutter, op='cut')
assert any(g.od == 20 for g in inspect.grooves(p)), 'Fixture must contain measured groove'
sh = Sheet(p, size='A3')
sh.view('top')
sh.note('ANNULAR GROOVE OUTER DIAMETER Ø20.00')
svg = sh.write(os.path.join(out, 'regression-groove'), quiet=True)['svg']

raw = open(svg).read()
raw = raw.replace('</svg>', '<text x="30" y="30" font-size="3.5">Ø20.00</text></svg>')
open(svg, 'w').write(raw)

def diameter_failure():
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        verify_sheet(sh, svg, p)
    return any('[FAIL]' in line and 'every Ø on the sheet' in line for line in log.getvalue().splitlines())

assert not diameter_failure(), 'Real groove diameter rejected'
raw = open(svg).read()
open(svg, 'w').write(raw.replace('Ø20.00', 'Ø21.00'))
assert diameter_failure(), 'Invented diameter must fail'
open(svg, 'w').write(raw)
old = sheets.measure_grooves
sheets.measure_grooves = lambda obj: []
assert diameter_failure(), 'Old missing-groove behavior must fail'
sheets.measure_grooves = old
sh.feature_schedule([{'what':'a feature', 'value_mm':1}], general_tolerance='CANNOT DETERMINE — measure a coupon before manufacture')
lines = sh._bottom_lines(120)
heads = [(payload,h) for kind,payload,h in lines if kind=='head']
assert all(sheets.text_width(t,h) <= 114.01 for t,h in heads), heads
assert any('FEATURE SCHEDULE' in t for t,h in heads)
print('PASS: measured groove accepted; invented diameter rejected; old behavior rejected; long heading fits column')
