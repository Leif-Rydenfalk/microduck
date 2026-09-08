# refcheck part:microduck-shin vs leg.stl

**FAIL** — p95 surface distance 1.10 mm (tol 1.00) / bbox delta 0.01 mm (tol 1.50); 3 reference feature(s) have no match in ours

| | ref->ours | ours->ref |
|---|---|---|
| mean mm | 0.239 | 0.260 |
| p50 mm | 0.014 | 0.024 |
| p95 mm | 1.011 | 1.099 |
| max mm | 2.848 | 2.445 |
| within 1.0 mm | 91.6% | 91.1% |

bbox ours [7.94, 20.0, 58.0]  ref [7.95, 20.0, 58.0]  delta [-0.01, -0.0, 0.0]
volume ratio ours/ref 1.0245 (closed-mesh figure, see compare.json)

## features

reference: 16 holes, 4 bosses · ours: 14 holes, 3 bosses · matched 17 · unmatched reference 3 · extra ours 0
- UNMATCHED hole Ø4.84 at [34.8, 30.0, 16.277] axis [1.0, 0.0004, 0.0] len 2.80
- UNMATCHED hole Ø4.84 at [34.8, 14.0, 16.277] axis [1.0, -0.0004, -0.0] len 2.80
- UNMATCHED boss Ø15.90 at [39.475, 22.0, 35.777] axis [1.0, -0.0, -0.0] len 1.95

## renders

- overlay_front.png
- overlay_left.png
- overlay_top.png
- overlay_iso.png
- ours_iso.png
- ref_iso.png
