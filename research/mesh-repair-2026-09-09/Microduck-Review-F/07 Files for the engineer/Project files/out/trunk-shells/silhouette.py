"""Measure the trunk-shell skin silhouettes off Pollen's mesh: for each z, the
outer x extent (side wall), the front y (min) and back y (max) of the skin
outboard of the ear (x >= 18.5, so the ear plate at x 14.6..17.9 and the
parting tongue at x < 0 never pollute the numbers). Plane cuts, not vertex
bins, so the fillet zones are not biased by the bin width."""
import sys, json, numpy as np
sys.path.insert(0, '/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck/out/trunk-shells')
from slice import load, section
path = sys.argv[1]; sgn = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
T = load(path); T[:, :, 0] *= sgn
rows = []
for z in list(np.arange(17.9, 59.6, 0.5)) + [59.45]:
    segs = section(T, 'z', float(z))
    if not segs: continue
    P = np.array([p for s in segs for p in s])
    body = P[P[:, 1] > -18.6]
    outb = P[P[:, 0] >= 18.5]
    if len(outb) == 0: outb = body
    rows.append((round(float(z), 2), round(float(body[:, 0].max()), 2), round(float(outb[:, 1].min()), 2), round(float(outb[:, 1].max()), 2)))
print(json.dumps(rows))
