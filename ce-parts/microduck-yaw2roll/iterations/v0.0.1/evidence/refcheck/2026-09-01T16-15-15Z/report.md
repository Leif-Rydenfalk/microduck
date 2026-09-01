# refcheck part:microduck-yaw2roll vs yaw2roll.stl

**PASS** — p95 surface distance 0.05 mm <= 1.00 both ways; bbox within 0.00 mm

| | ref->ours | ours->ref |
|---|---|---|
| mean mm | 0.020 | 0.025 |
| p50 mm | 0.000 | 0.000 |
| p95 mm | 0.050 | 0.050 |
| max mm | 1.220 | 1.465 |
| within 1.0 mm | 99.9% | 99.8% |

bbox ours [23.0, 25.8, 20.5]  ref [23.0, 25.8, 20.5]  delta [0.0, 0.0, 0.0]
volume ratio ours/ref 1.0055 (closed-mesh figure, see compare.json)

## features

reference: 16 holes, 3 bosses · ours: 16 holes, 3 bosses · matched 19 · unmatched reference 0 · extra ours 0

## renders

- overlay_front.png
- overlay_left.png
- overlay_top.png
- overlay_iso.png
- ours_iso.png
- ref_iso.png
