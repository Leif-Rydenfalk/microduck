# refcheck part:np-f550 vs np_f970.stl

**PASS** — p95 surface distance 0.81 mm <= 1.00 both ways; bbox within 0.11 mm

| | ref->ours | ours->ref |
|---|---|---|
| mean mm | 0.114 | 0.082 |
| p50 mm | 0.033 | 0.033 |
| p95 mm | 0.812 | 0.581 |
| max mm | 2.096 | 2.166 |
| within 1.0 mm | 96.1% | 98.0% |

bbox ours [38.5, 20.5, 70.7]  ref [38.608, 20.576, 70.809]  delta [-0.108, -0.076, -0.109]
volume ratio ours/ref 0.9964 (closed-mesh figure, see compare.json)

## features

reference: 6 holes, 0 bosses · ours: 6 holes, 0 bosses · matched 6 · unmatched reference 0 · extra ours 0

## renders

- overlay_front.png
- overlay_left.png
- overlay_top.png
- overlay_iso.png
- ours_iso.png
- ref_iso.png
