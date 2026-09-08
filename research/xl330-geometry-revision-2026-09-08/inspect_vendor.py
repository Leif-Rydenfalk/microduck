"""Read unchanged manufacturer STEP; no shelf or assembly mutation."""
import json
import hashlib
from pathlib import Path
import Part

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / 'ce-parts/xl330-m288-t/iterations/v0.0.1/geometry/robotis-xl-xc-330.stp'

def box(shape):
    b = shape.BoundBox
    return {'min': [b.XMin, b.YMin, b.ZMin],
            'max': [b.XMax, b.YMax, b.ZMax],
            'size': [b.XLength, b.YLength, b.ZLength]}

shape = Part.read(str(SOURCE))
result = {'source': str(SOURCE.relative_to(ROOT)),
          'sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'scope': 'Manufacturer STEP geometry, not installed original robot identity',
          'valid': shape.isValid(), 'closed': shape.isClosed(),
          'solids': len(shape.Solids), 'shells': len(shape.Shells),
          'volume_mm3': shape.Volume, 'bbox_mm': box(shape), 'bodies': []}
for i, solid in enumerate(shape.Solids):
    cylinders = []
    for face in solid.Faces:
        s = face.Surface
        if isinstance(s, Part.Cylinder):
            cylinders.append({'radius_mm': s.Radius, 'center_mm': list(s.Center),
                              'axis': list(s.Axis), 'bbox_mm': box(face)})
    result['bodies'].append({'index': i, 'valid': solid.isValid(),
                            'volume_mm3': solid.Volume, 'bbox_mm': box(solid),
                            'cylinders': cylinders})
(OUT / 'vendor-geometry.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: v for k, v in result.items() if k != 'bodies'}, indent=2))
for b in result['bodies']:
    print('body', b['index'], 'volume', b['volume_mm3'], 'bbox', b['bbox_mm'])
