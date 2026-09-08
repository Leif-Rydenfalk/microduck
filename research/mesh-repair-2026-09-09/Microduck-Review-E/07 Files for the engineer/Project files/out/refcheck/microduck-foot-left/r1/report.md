# refcheck part:microduck-foot-left vs foot_left.stl

**PASS** — p95 surface distance 0.45 mm <= 1.00 both ways; bbox within 0.00 mm

| | ref->ours | ours->ref |
|---|---|---|
| mean mm | 0.067 | 0.050 |
| p50 mm | 0.000 | 0.000 |
| p95 mm | 0.450 | 0.327 |
| max mm | 2.428 | 1.887 |
| within 1.0 mm | 97.9% | 99.1% |

bbox ours [40.085, 54.0, 16.905]  ref [40.086, 54.0, 16.909]  delta [-0.001, 0.0, -0.004]
volume ratio ours/ref 0.9593 (closed-mesh figure, see compare.json)

## features

reference: 2 holes, 0 bosses · ours: 2 holes, 0 bosses · matched 2 · unmatched reference 0 · extra ours 0

## renders

- overlay_front.png
- overlay_left.png
- overlay_top.png
- overlay_iso.png
- ours_iso.png
- ref_iso.png
