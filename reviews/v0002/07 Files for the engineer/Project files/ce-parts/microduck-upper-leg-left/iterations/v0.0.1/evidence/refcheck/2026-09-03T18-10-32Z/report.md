# refcheck part:microduck-upper-leg-left vs upper_leg_left.stl

**FAIL** — p95 surface distance 1.31 mm (tol 1.00) / bbox delta 0.01 mm (tol 1.50)

| | ref->ours | ours->ref |
|---|---|---|
| mean mm | 0.045 | 0.273 |
| p50 mm | 0.007 | 0.011 |
| p95 mm | 0.219 | 1.307 |
| max mm | 1.006 | 16.521 |
| within 1.0 mm | 99.9% | 94.5% |

bbox ours [28.0, 47.661, 60.983]  ref [28.0, 47.659, 60.997]  delta [-0.0, 0.001, -0.013]
volume ratio ours/ref 1.037 (closed-mesh figure, see compare.json)

## features

reference: 4 holes, 8 bosses · ours: 4 holes, 8 bosses · matched 12 · unmatched reference 0 · extra ours 0

## renders

- overlay_front.png
- overlay_left.png
- overlay_top.png
- overlay_iso.png
- ours_iso.png
- ref_iso.png
