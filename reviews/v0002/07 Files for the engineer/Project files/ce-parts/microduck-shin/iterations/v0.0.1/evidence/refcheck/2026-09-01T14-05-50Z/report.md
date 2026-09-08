# refcheck part:microduck-shin vs leg.stl

**PASS** — p95 surface distance 1.00 mm <= 1.00 both ways; bbox within 0.00 mm

| | ref->ours | ours->ref |
|---|---|---|
| mean mm | 0.144 | 0.165 |
| p50 mm | 0.001 | 0.002 |
| p95 mm | 1.000 | 1.000 |
| max mm | 2.848 | 2.223 |
| within 1.0 mm | 98.6% | 97.5% |

bbox ours [7.95, 20.0, 58.0]  ref [7.95, 20.0, 58.0]  delta [-0.0, -0.0, 0.0]
volume ratio ours/ref 0.9939 (closed-mesh figure, see compare.json)

## features

reference: 16 holes, 4 bosses · ours: 16 holes, 5 bosses · matched 20 · unmatched reference 0 · extra ours 1
- extra in ours: boss Ø12.87 at [34.45, 22.0, 11.516]

## renders

- overlay_front.png
- overlay_left.png
- overlay_top.png
- overlay_iso.png
- ours_iso.png
- ref_iso.png
