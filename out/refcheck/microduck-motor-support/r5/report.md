# refcheck part:microduck-motor-support vs motor_support.stl

**FAIL** — p95 surface distance 0.47 mm <= 1.00 both ways; bbox within 0.00 mm; 2 reference feature(s) have no match in ours

| | ref->ours | ours->ref |
|---|---|---|
| mean mm | 0.093 | 0.111 |
| p50 mm | 0.013 | 0.015 |
| p95 mm | 0.345 | 0.471 |
| max mm | 2.417 | 2.400 |
| within 1.0 mm | 99.4% | 99.1% |

bbox ours [73.5, 54.2, 18.8]  ref [73.5, 54.2, 18.8]  delta [-0.0, -0.0, -0.0]
volume ratio ours/ref 1.0461 (closed-mesh figure, see compare.json)

## features

reference: 5 holes, 1 bosses · ours: 5 holes, 1 bosses · matched 4 · unmatched reference 2 · extra ours 2
- UNMATCHED hole Ø17.84 at [-32.308, 0.023, 6.749] axis [1.0, -0.0001, 0.0001] len 6.39
- UNMATCHED boss Ø20.69 at [-33.467, 0.005, 7.144] axis [1.0, -0.0001, 0.0002] len 6.07
- extra in ours: hole Ø17.69 at [-32.269, 0.015, 7.188]
- extra in ours: boss Ø20.87 at [-32.307, 0.076, 7.069]

## renders

- overlay_front.png
- overlay_left.png
- overlay_top.png
- overlay_iso.png
- ours_iso.png
- ref_iso.png
