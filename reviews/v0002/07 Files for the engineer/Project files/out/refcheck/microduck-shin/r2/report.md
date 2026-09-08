# refcheck part:microduck-shin vs leg.stl

**FAIL** — p95 surface distance 1.33 mm (tol 1.00) / bbox delta 0.34 mm (tol 1.50); 5 reference feature(s) have no match in ours

| | ref->ours | ours->ref |
|---|---|---|
| mean mm | 0.339 | 0.354 |
| p50 mm | 0.170 | 0.170 |
| p95 mm | 1.330 | 1.330 |
| max mm | 2.848 | 2.718 |
| within 1.0 mm | 89.4% | 89.4% |

bbox ours [8.29, 20.0, 58.0]  ref [7.95, 20.0, 58.0]  delta [0.34, -0.0, 0.0]
volume ratio ours/ref 1.1459 (closed-mesh figure, see compare.json)

## features

reference: 16 holes, 4 bosses · ours: 14 holes, 1 bosses · matched 15 · unmatched reference 5 · extra ours 0
- UNMATCHED hole Ø4.84 at [34.8, 30.0, 16.277] axis [1.0, 0.0004, 0.0] len 2.80
- UNMATCHED hole Ø4.84 at [34.8, 14.0, 16.277] axis [1.0, -0.0004, -0.0] len 2.80
- UNMATCHED boss Ø10.00 at [38.25, 22.0, -6.223] axis [1.0, 0.0, 0.0] len 0.50
- UNMATCHED boss Ø10.00 at [34.0, 22.0, -6.223] axis [1.0, 0.0, 0.0] len 3.00
- UNMATCHED boss Ø15.90 at [39.475, 22.0, 35.777] axis [1.0, -0.0, -0.0] len 1.95

## renders

- overlay_front.png
- overlay_left.png
- overlay_top.png
- overlay_iso.png
- ours_iso.png
- ref_iso.png
