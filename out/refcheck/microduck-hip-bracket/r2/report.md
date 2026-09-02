# refcheck part:microduck-hip-bracket vs hip_l.stl

**PASS** — p95 surface distance 0.24 mm <= 1.00 both ways; bbox within 0.00 mm

| | ref->ours | ours->ref |
|---|---|---|
| mean mm | 0.026 | 0.038 |
| p50 mm | 0.001 | 0.001 |
| p95 mm | 0.162 | 0.242 |
| max mm | 0.785 | 1.031 |
| within 1.0 mm | 100.0% | 99.9% |

bbox ours [32.45, 34.5, 19.0]  ref [32.45, 34.5, 19.0]  delta [-0.0, -0.0, 0.0]
volume ratio ours/ref 0.9933 (closed-mesh figure, see compare.json)

## features

reference: 19 holes, 2 bosses · ours: 22 holes, 2 bosses · matched 21 · unmatched reference 0 · extra ours 3
- extra in ours: hole Ø4.84 at [17.5, -22.25, -6.0]
- extra in ours: hole Ø4.84 at [11.5, -22.25, 0.0]
- extra in ours: hole Ø5.22 at [34.275, 0.0, 6.0]

## renders

- overlay_front.png
- overlay_left.png
- overlay_top.png
- overlay_iso.png
- ours_iso.png
- ref_iso.png
