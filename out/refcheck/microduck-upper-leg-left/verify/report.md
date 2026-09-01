# refcheck part:microduck-upper-leg-left vs upper_leg_left.stl

**PASS** — p95 surface distance 0.20 mm <= 1.00 both ways; bbox within 0.01 mm

| | ref->ours | ours->ref |
|---|---|---|
| mean mm | 0.036 | 0.030 |
| p50 mm | 0.002 | 0.002 |
| p95 mm | 0.200 | 0.200 |
| max mm | 0.867 | 1.004 |
| within 1.0 mm | 100.0% | 100.0% |

bbox ours [28.0, 47.661, 60.991]  ref [28.0, 47.659, 60.997]  delta [-0.0, 0.001, -0.006]
volume ratio ours/ref 0.9247 (closed-mesh figure, see compare.json)

## features

reference: 2 holes, 4 bosses · ours: 2 holes, 4 bosses · matched 6 · unmatched reference 0 · extra ours 0

## renders

- overlay_front.png
- overlay_left.png
- overlay_top.png
- overlay_iso.png
- ours_iso.png
- ref_iso.png
