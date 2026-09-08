"""Read-only center-region samples of separate vendor solids; no identity inference."""
import hashlib
import json
from pathlib import Path
import FreeCAD as App
import Part

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
SOURCE = ROOT/'ce-parts/xl330-m288-t/iterations/v0.0.1/geometry/robotis-xl-xc-330.stp'
shape = Part.read(str(SOURCE))
rows = []
# local(X,Y,Z)=(vendorZ+8,vendorX,vendorY). Avoid exact faces in samples.
for x in (-14.6, -14.49, -14.29, -13.5, -12.5, -11.51,
          11.51, 12.5, 13.5, 14.29, 14.49, 14.6):
    for radius in (0, 1, 2, 2.7, 2.9, 3.5, 3.7, 4.5):
        # Both radial directions distinguish a screw slot from an axisymmetric bore.
        for direction in ('local_y', 'local_z'):
            local = (x, radius if direction == 'local_y' else 0,
                     radius if direction == 'local_z' else 0)
            vendor = App.Vector(local[1], local[2], local[0]-8)
            material = [i for i, solid in enumerate(shape.Solids)
                        if solid.isInside(vendor, 1e-7, True)]
            rows.append({'point_local_mm': local, 'radial_direction': direction,
                         'vendor_solid_indices_containing_point': material})
assert not any(r['vendor_solid_indices_containing_point'] for r in rows
               if abs(r['point_local_mm'][0]) > 14.5)
result = {'scope': 'Point samples of manufacturer STEP solids; not original robot identity, screw acceptance or continuous surface classification',
          'source': str(SOURCE.relative_to(ROOT)),
          'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'frame_mapping': 'local(X,Y,Z)=(vendorZ+8,vendorX,vendorY)',
          'rows': rows,
          'limits': 'Separate material occupancy by vendor solid index. Empty axis alone does not establish a bore; a radius alone does not establish a protruding hub. Additional shells are excluded from volumetric occupancy.'}
(OUT/'vendor-center-samples.json').write_text(json.dumps(result, indent=2)+'\n')
for x in sorted({r['point_local_mm'][0] for r in rows}):
    axis = next(r for r in rows if r['point_local_mm'] == (x, 0, 0))
    print('local X', x, 'axis material solid indices', axis['vendor_solid_indices_containing_point'])
print('Measured', len(rows), 'points; no sampled material beyond either nominal disc face')
