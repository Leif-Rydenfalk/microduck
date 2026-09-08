"""Audit existing nominal placements without changing their historical bytes."""
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT/'out/fasteners/placed.json'
PDF = ROOT/'ce-parts/xl330-m288-t/iterations/v0.0.1/docs/fetched/XL,XC-330.pdf'
rows = []
for item in json.loads(SOURCE.read_text())['placed']:
    if item['pilot_mesh'] != 'xl330':
        continue
    penetration = round(item['length_mm'] - item['grip_mm'], 4)
    rows.append({'instance': item['instance'], 'endpoint': item['pilot_endpoint'],
                 'screw_mm': item['length_mm'], 'modeled_grip_mm': item['grip_mm'],
                 'modeled_penetration_mm': penetration,
                 'over_vendor_max_mm': round(max(0, penetration-3), 4)})
result = {'scope': 'Model screw length minus model grip compared with manufacturer 3 mm maximum; not physical measurement or approval of these ISO screws',
          'source': str(SOURCE.relative_to(ROOT)),
          'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'manufacturer_drawing': str(PDF.relative_to(ROOT)),
          'manufacturer_drawing_sha256': hashlib.sha256(PDF.read_bytes()).hexdigest(),
          'modeled_servo_face_screws': len(rows),
          'exceeding_manufacturer_maximum': sum(r['over_vendor_max_mm'] > 1e-8 for r in rows),
          'rows': rows}
(OUT/'nominal-engagement-comparison.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k != 'rows'}))
