"""Independent finished-BRep probes; research candidate only, no shelf mutation."""
import hashlib
import importlib.util
import json
from pathlib import Path
import FreeCAD as App
import Part as Kernel
from cecad import check, contact_sheet

OUT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('servo_candidate', OUT / 'candidate_part.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
part = module.build(None)
# PA is an unresolved legacy material label. Suppress mass formatting only;
# retain the standard topology checks and explicitly do not estimate mass.
assert check(part, verbose=False)
print('ALL CHECKS PASSED — candidate topology only; material/mass unknown')
shape = part.shape
rows = []

def probe(label, xyz, expected):
    actual = shape.isInside(App.Vector(*xyz), 1e-7, True)
    rows.append({'label': label, 'point_mm': xyz, 'expected_material': expected,
                 'actual_material': actual, 'pass': actual == expected})

# Independent drawing/STEP values, deliberately not candidate module constants.
for side in (-1, 1):
    for y, z in ((0, 6), (0, -6), (6, 0), (-6, 0)):
        for depth, material in ((0.1, False), (2.85, False), (2.95, True), (3.1, True)):
            probe('face pilot axis', (side * (14.5-depth), y, z), material)
        probe('face pilot radial wall', (side*13, y+0.85, z), True)
for y in (-8, 8):
    for z in (-22.5, 7.5):
        for x in (-11.4, -7.1, -6.9, 0, 7.9, 8.1, 11.4):
            probe('case hole axis', (x, y, z), False)
            probe('case step annulus', (x, y+0.9, z), -7 < x < 8)
        probe('case outer wall', (0, y+1.1, z), True)

assert all(row['pass'] for row in rows), [r for r in rows if not r['pass']]
assert shape.isValid() and shape.isClosed() and len(shape.Solids) == 1
shape.exportBrep(str(OUT/'candidate.brep'))
result = {'status': 'PASS', 'scope': 'Candidate hole geometry only; exterior remains simplified and original identity unverified',
          'candidate_sha256': hashlib.sha256((OUT/'candidate_part.py').read_bytes()).hexdigest(),
          'valid': shape.isValid(), 'closed': shape.isClosed(), 'solids': len(shape.Solids),
          'volume_mm3': shape.Volume, 'probes': rows}
(OUT/'candidate-verification.json').write_text(json.dumps(result, indent=2)+'\n')
contact_sheet(part, str(OUT/'candidate.png'), title='XL330 source correction candidate — simplified exterior')
print(json.dumps({'status': result['status'], 'probes': len(rows), 'solids': len(shape.Solids)}))
