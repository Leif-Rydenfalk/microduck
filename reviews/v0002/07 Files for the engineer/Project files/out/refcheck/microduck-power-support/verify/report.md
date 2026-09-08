# refcheck part:microduck-power-support vs power_support.stl

**PASS** — p95 surface distance 0.23 mm <= 1.00 both ways; bbox within 0.36 mm

| | ref->ours | ours->ref |
|---|---|---|
| mean mm | 0.050 | 0.054 |
| p50 mm | 0.000 | 0.000 |
| p95 mm | 0.213 | 0.228 |
| max mm | 0.716 | 0.824 |
| within 1.0 mm | 100.0% | 100.0% |

bbox ours [54.466, 17.0, 83.13]  ref [54.5, 17.0, 83.49]  delta [-0.034, -0.0, -0.36]
volume ratio ours/ref 1.0273 (closed-mesh figure, see compare.json)

## features

reference: 12 holes, 2 bosses · ours: 14 holes, 7 bosses · matched 14 · unmatched reference 0 · extra ours 7
- extra in ours: hole Ø1.55 at [-25.0, 30.9, 53.6]
- extra in ours: hole Ø1.55 at [25.0, 30.9, 53.6]
- extra in ours: boss Ø0.80 at [0.0, 26.6, -20.06]
- extra in ours: boss Ø0.80 at [0.0, 26.6, -18.56]
- extra in ours: boss Ø0.80 at [0.0, 26.6, -17.06]
- extra in ours: boss Ø0.80 at [0.0, 26.6, -15.56]
- extra in ours: boss Ø0.80 at [0.0, 26.6, -14.06]

## renders

- overlay_front.png
- overlay_left.png
- overlay_top.png
- overlay_iso.png
- ours_iso.png
- ref_iso.png
