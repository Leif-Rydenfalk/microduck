# refcheck part:microduck-m12-lens-holder vs m12_lens_holder.stl

**FAIL** — p95 surface distance 2.00 mm (tol 1.00) / bbox delta 4.00 mm (tol 1.50); 4 reference feature(s) have no match in ours

| | ref->ours | ours->ref |
|---|---|---|
| mean mm | 0.670 | 0.664 |
| p50 mm | 0.409 | 0.404 |
| p95 mm | 2.000 | 2.000 |
| max mm | 2.002 | 2.008 |
| within 1.0 mm | 67.8% | 68.5% |

bbox ours [20.0, 14.8, 16.0]  ref [24.0, 14.8, 16.0]  delta [-4.0, 0.0, -0.0]
volume ratio ours/ref 0.9407 (closed-mesh figure, see compare.json)

## features

reference: 4 holes, 0 bosses · ours: 3 holes, 0 bosses · matched 0 · unmatched reference 4 · extra ours 3
- UNMATCHED hole Ø2.00 at [-10.0, 1.8, 0.0] axis [0.0, 1.0, 0.0] len 3.60
- UNMATCHED hole Ø2.00 at [10.0, 1.8, -0.0] axis [0.0, 1.0, 0.0] len 3.60
- UNMATCHED hole Ø2.00 at [-0.0, 12.0, 6.657] axis [0.0, 0.0, 1.0] len 1.89
- UNMATCHED hole Ø11.60 at [0.0, 10.549, 0.0] axis [-0.0, 1.0, 0.0] len 7.50
- extra in ours: hole Ø2.00 at [0.0, 12.0, 6.657]
- extra in ours: hole Ø2.00 at [10.0, 1.8, 0.0]
- extra in ours: hole Ø11.60 at [-0.0, 10.55, -0.0]

## renders

- overlay_front.png
- overlay_left.png
- overlay_top.png
- overlay_iso.png
- ours_iso.png
- ref_iso.png
