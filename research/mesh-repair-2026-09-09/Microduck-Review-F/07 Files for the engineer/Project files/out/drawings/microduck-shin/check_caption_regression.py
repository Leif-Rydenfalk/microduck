"""Image caption regression on the real annotated layout, including negative controls."""
import json, re
from pathlib import Path
from cecad import sheetcheck
p=Path(__file__).resolve().parent/'render-panel-prototype'
svg=p/'shin-render-panels.svg'
solid=json.loads((p/'sheetcheck-solid.json').read_text())
def grade(path=svg):
    return sheetcheck.grade_sheet(str(path), slug='microduck-shin', use_kernel=False, solid=solid)
g=grade()
assert g['checks']['iso']['verdict']=='PASS',g['checks']['iso']
assert g['checks']['iso']['measured']==4
old=sheetcheck._VIEW_LABEL_RE
sheetcheck._VIEW_LABEL_RE=re.compile('.*')
broken=grade()
assert broken['checks']['iso']['verdict']=='FAIL', 'Old any-text association must fail'
assert broken['checks']['iso']['measured']==0
sheetcheck._VIEW_LABEL_RE=old
raw=svg.read_text()
m=re.search(r'<image\b[^>]*>',raw);assert m
small=re.sub(r'width="([\d.]+)"',lambda x:'width="'+str(float(x[1])/10)+'"',m[0],count=1)
control=p/'undersized-render-negative-control.svg'
control.write_text(raw[:m.start()]+small+raw[m.end():])
bad=grade(control)
assert bad['checks']['iso']['verdict']=='FAIL'
assert bad['checks']['renders']['verdict']=='FAIL'
control.unlink()
print('PASS: four real ISO captions found among annotations; old association returns zero; undersized image still fails ISO and render area gates')
