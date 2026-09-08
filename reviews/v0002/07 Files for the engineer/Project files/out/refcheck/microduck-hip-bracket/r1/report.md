# refcheck part:microduck-hip-bracket vs hip_l.stl

**FAIL** — p95 surface distance 15.35 mm (tol 1.00) / bbox delta 30.49 mm (tol 1.50); 21 reference feature(s) have no match in ours

| | ref->ours | ours->ref |
|---|---|---|
| mean mm | 10.623 | 7.510 |
| p50 mm | 10.886 | 8.795 |
| p95 mm | 15.348 | 10.755 |
| max mm | 17.075 | 10.969 |
| within 1.0 mm | 0.2% | 1.4% |

bbox ours [1.96, 15.995, 16.0]  ref [32.45, 34.5, 19.0]  delta [-30.49, -18.505, -3.0]
volume ratio ours/ref 0.067 (closed-mesh figure, see compare.json)

## features

reference: 19 holes, 2 bosses · ours: 5 holes, 1 bosses · matched 0 · unmatched reference 21 · extra ours 6
- UNMATCHED hole Ø2.40 at [17.5, -18.025, 6.0] axis [0.0, 1.0, 0.0] len 2.95
- UNMATCHED hole Ø2.40 at [23.5, -18.025, -0.0] axis [0.0, 1.0, 0.0] len 2.95
- UNMATCHED hole Ø2.40 at [17.5, -18.025, -6.0] axis [0.0, -1.0, 0.0] len 2.95
- UNMATCHED hole Ø2.40 at [11.5, -18.025, -0.0] axis [0.0, 1.0, 0.0] len 2.95
- UNMATCHED hole Ø2.40 at [38.975, 6.0, 0.0] axis [1.0, 0.0, 0.0] len 2.95
- UNMATCHED hole Ø2.40 at [38.975, -0.0, -6.0] axis [1.0, -0.0, -0.0] len 2.95
- UNMATCHED hole Ø2.40 at [38.975, -6.0, 0.0] axis [1.0, 0.0, 0.0] len 2.95
- UNMATCHED hole Ø2.40 at [38.975, -0.0, 6.0] axis [1.0, -0.0, -0.0] len 2.95
- UNMATCHED hole Ø4.84 at [35.837, 0.0, 6.0] axis [1.0, -0.0, -0.0] len 3.33
- UNMATCHED hole Ø4.84 at [35.85, -0.0, -6.0] axis [1.0, -0.0, -0.0] len 3.30
- UNMATCHED hole Ø4.84 at [35.85, -6.0, 0.0] axis [1.0, 0.0, -0.0] len 3.30
- UNMATCHED hole Ø4.84 at [23.5, -22.163, 0.0] axis [-0.0001, 1.0, 0.0001] len 5.33
- UNMATCHED hole Ø4.84 at [17.499, -22.158, 6.001] axis [-0.0002, -1.0, 0.0003] len 5.32
- UNMATCHED hole Ø4.84 at [35.841, 6.001, 0.002] axis [1.0, -0.0007, -0.0013] len 3.33
- UNMATCHED hole Ø5.22 at [34.088, 6.002, 0.002] axis [0.9969, 0.0749, 0.0226] len 0.58
- UNMATCHED hole Ø5.22 at [34.074, -0.002, -5.997] axis [0.9991, 0.0074, -0.0411] len 0.37
- UNMATCHED hole Ø5.23 at [34.098, -5.999, 0.0] axis [1.0, -0.0033, -0.0001] len 0.21
- UNMATCHED hole Ø6.00 at [17.5, -17.525, -0.0] axis [-0.0, 1.0, 0.0] len 1.95
- UNMATCHED hole Ø6.00 at [39.475, -0.0, 0.0] axis [1.0, -0.0, 0.0] len 1.95
- UNMATCHED boss Ø16.00 at [17.5, -17.525, -0.0] axis [-0.0, 1.0, 0.0] len 1.95
- UNMATCHED boss Ø16.00 at [39.475, -0.0, -0.0] axis [1.0, 0.0, 0.0] len 1.95
- extra in ours: hole Ø2.40 at [39.47, 6.0, 0.0]
- extra in ours: hole Ø2.40 at [39.47, 0.0, -6.0]
- extra in ours: hole Ø2.40 at [39.47, 0.0, 6.0]
- extra in ours: hole Ø2.40 at [39.47, -6.0, -0.0]
- extra in ours: hole Ø6.00 at [39.475, 0.0, -0.0]
- extra in ours: boss Ø16.00 at [39.47, 0.0, 0.0]

## renders

- overlay_front.png
- overlay_left.png
- overlay_top.png
- overlay_iso.png
- ours_iso.png
- ref_iso.png
