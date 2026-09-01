# refcheck part:microduck-shin vs leg.stl

**FAIL** — p95 surface distance 2.67 mm (tol 1.00) / bbox delta 0.34 mm (tol 1.50); 3 reference feature(s) have no match in ours

| | ref->ours | ours->ref |
|---|---|---|
| mean mm | 0.612 | 0.709 |
| p50 mm | 0.320 | 0.330 |
| p95 mm | 2.120 | 2.670 |
| max mm | 2.848 | 2.837 |
| within 1.0 mm | 74.8% | 71.7% |

bbox ours [8.29, 20.0, 58.0]  ref [7.95, 20.0, 58.0]  delta [0.34, -0.0, 0.0]
volume ratio ours/ref 1.3775 (closed-mesh figure, see compare.json)

## features

reference: 16 holes, 4 bosses · ours: 16 holes, 2 bosses · matched 17 · unmatched reference 3 · extra ours 1
- UNMATCHED hole Ø8.00 at [38.25, 22.0, -6.223] axis [1.0, 0.0, 0.0] len 0.50
- UNMATCHED boss Ø10.00 at [34.0, 22.0, -6.223] axis [1.0, 0.0, 0.0] len 3.00
- UNMATCHED boss Ø15.90 at [39.475, 22.0, 35.777] axis [1.0, -0.0, -0.0] len 1.95
- extra in ours: hole Ø15.90 at [39.475, 22.0, 35.777]

## renders

- overlay_front.png
- overlay_left.png
- overlay_top.png
- overlay_iso.png
- ours_iso.png
- ref_iso.png
