# refcheck part:microduck-sole-left vs sole_left.stl

**FAIL** — p95 surface distance 2.24 mm (tol 1.00) / bbox delta 0.60 mm (tol 1.50)

| | ref->ours | ours->ref |
|---|---|---|
| mean mm | 0.208 | 0.432 |
| p50 mm | 0.281 | 0.298 |
| p95 mm | 0.335 | 2.244 |
| max mm | 0.417 | 5.499 |
| within 1.0 mm | 100.0% | 92.2% |

bbox ours [41.529, 54.0, 13.504]  ref [41.099, 54.0, 12.907]  delta [0.43, 0.0, 0.596]
volume ratio ours/ref 1.0063 (closed-mesh figure, see compare.json)

## features

reference: 0 holes, 0 bosses · ours: 0 holes, 0 bosses · matched 0 · unmatched reference 0 · extra ours 0

## renders

- overlay_front.png
- overlay_left.png
- overlay_top.png
- overlay_iso.png
- ours_iso.png
- ref_iso.png
