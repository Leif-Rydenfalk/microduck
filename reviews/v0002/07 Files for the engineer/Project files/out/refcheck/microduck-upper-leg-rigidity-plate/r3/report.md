# refcheck part:microduck-upper-leg-rigidity-plate vs upper_leg_rigidity_plate.stl

**PASS** — p95 surface distance 0.01 mm <= 1.00 both ways; bbox within 0.00 mm

| | ref->ours | ours->ref |
|---|---|---|
| mean mm | 0.006 | 0.004 |
| p50 mm | 0.000 | 0.000 |
| p95 mm | 0.008 | 0.008 |
| max mm | 0.804 | 0.483 |
| within 1.0 mm | 100.0% | 100.0% |

bbox ours [1.0, 44.999, 58.06]  ref [1.0, 44.996, 58.058]  delta [0.0, 0.003, 0.002]
volume ratio ours/ref 0.9889 (closed-mesh figure, see compare.json)

## features

reference: 6 holes, 0 bosses · ours: 7 holes, 0 bosses · matched 6 · unmatched reference 0 · extra ours 1
- extra in ours: hole Ø19.12 at [43.0, -0.0, 13.611]

## renders

- overlay_front.png
- overlay_left.png
- overlay_top.png
- overlay_iso.png
- ours_iso.png
- ref_iso.png
