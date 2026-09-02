# refcheck part:microduck-yaw-roll-motion vs yaw_roll_motion.stl

**PASS** — p95 surface distance 0.93 mm <= 1.00 both ways; bbox within 0.03 mm

| | ref->ours | ours->ref |
|---|---|---|
| mean mm | 0.061 | 0.103 |
| p50 mm | 0.017 | 0.017 |
| p95 mm | 0.422 | 0.934 |
| max mm | 1.784 | 2.585 |
| within 1.0 mm | 99.5% | 97.6% |

bbox ours [34.0, 35.89, 22.5]  ref [34.0, 35.9, 22.466]  delta [0.0, -0.01, 0.034]
volume ratio ours/ref 1.0151 (closed-mesh figure, see compare.json)

## features

reference: 5 holes, 1 bosses · ours: 16 holes, 3 bosses · matched 6 · unmatched reference 0 · extra ours 13
- extra in ours: hole Ø2.20 at [-6.0, 16.245, 4.5]
- extra in ours: hole Ø2.20 at [0.0, 16.245, 10.5]
- extra in ours: hole Ø2.20 at [6.0, 16.245, 4.5]
- extra in ours: hole Ø2.50 at [-22.5, -8.0, 17.0]
- extra in ours: hole Ø2.50 at [-22.5, 8.0, 17.0]
- extra in ours: hole Ø2.50 at [7.5, 8.0, 16.75]
- extra in ours: hole Ø4.40 at [-6.0, 13.3, 4.5]
- extra in ours: hole Ø4.40 at [0.0, 13.3, 10.5]
- extra in ours: hole Ø4.40 at [6.0, 13.3, 4.5]
- extra in ours: hole Ø4.60 at [7.5, 8.0, 17.75]
- extra in ours: hole Ø4.60 at [7.5, -8.0, 17.75]
- extra in ours: boss Ø16.00 at [0.0, 16.945, 4.5]
- extra in ours: boss Ø18.14 at [0.057, 14.0, 4.6]

## renders

- overlay_front.png
- overlay_left.png
- overlay_top.png
- overlay_iso.png
- ours_iso.png
- ref_iso.png
