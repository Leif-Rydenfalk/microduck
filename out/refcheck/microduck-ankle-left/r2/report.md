# refcheck part:microduck-ankle-left vs ankle_left.stl

**FAIL** — p95 surface distance 5.88 mm (tol 1.00) / bbox delta 1.64 mm (tol 1.50); 13 reference feature(s) have no match in ours

| | ref->ours | ours->ref |
|---|---|---|
| mean mm | 0.213 | 0.832 |
| p50 mm | 0.010 | 0.104 |
| p95 mm | 0.741 | 5.885 |
| max mm | 0.823 | 11.729 |
| within 1.0 mm | 100.0% | 89.4% |

bbox ours [39.49, 38.137, 25.5]  ref [39.489, 36.5, 25.5]  delta [0.001, 1.637, 0.0]
volume ratio ours/ref 1.0189 (closed-mesh figure, see compare.json)

## features

reference: 13 holes, 0 bosses · ours: 13 holes, 0 bosses · matched 0 · unmatched reference 13 · extra ours 13
- UNMATCHED hole Ø2.20 at [50.0, 4.502, -15.092] axis [0.0, 0.0, 1.0] len 1.50
- UNMATCHED hole Ø2.20 at [65.6, 22.0, -12.223] axis [1.0, 0.0, 0.0] len 1.80
- UNMATCHED hole Ø2.20 at [65.6, 22.0, -0.223] axis [1.0, 0.0, 0.0] len 1.80
- UNMATCHED hole Ø2.20 at [65.6, 28.0, -6.223] axis [1.0, 0.0, 0.0] len 1.80
- UNMATCHED hole Ø2.20 at [65.6, 16.0, -6.223] axis [1.0, 0.0, 0.0] len 1.80
- UNMATCHED hole Ø4.40 at [50.0, 4.502, -13.842] axis [0.0, 0.0, 1.0] len 1.00
- UNMATCHED hole Ø4.40 at [68.088, 22.0, -12.223] axis [1.0, 0.0, 0.0] len 3.18
- UNMATCHED hole Ø4.40 at [67.713, 28.0, -6.223] axis [1.0, 0.0, 0.0] len 2.43
- UNMATCHED hole Ø4.40 at [67.713, 16.0, -6.223] axis [1.0, 0.0, 0.0] len 2.43
- UNMATCHED hole Ø4.40 at [67.338, 22.0, -0.223] axis [1.0, 0.0, 0.0] len 1.68
- UNMATCHED hole Ø5.00 at [66.832, 22.0, -6.223] axis [1.0, 0.0, -0.0] len 4.26
- UNMATCHED hole Ø14.00 at [31.581, 22.0, -6.223] axis [1.0, 0.0, -0.0] len 1.84
- UNMATCHED hole Ø15.00 at [33.65, 22.0, -6.223] axis [1.0, 0.0, 0.0] len 2.30
- extra in ours: hole Ø2.20 at [50.0, 4.502, -15.092]
- extra in ours: hole Ø2.20 at [65.595, 22.0, -12.223]
- extra in ours: hole Ø2.20 at [65.595, 16.0, -6.223]
- extra in ours: hole Ø2.20 at [65.595, 28.0, -6.223]
- extra in ours: hole Ø2.20 at [65.595, 22.0, -0.223]
- extra in ours: hole Ø4.40 at [68.088, 22.0, -12.223]
- extra in ours: hole Ø4.40 at [67.713, 28.0, -6.223]
- extra in ours: hole Ø4.40 at [67.713, 16.0, -6.223]
- extra in ours: hole Ø4.40 at [67.338, 22.0, -0.223]
- extra in ours: hole Ø4.40 at [50.0, 4.502, -13.842]
- extra in ours: hole Ø5.00 at [66.827, 22.0, -6.223]
- extra in ours: hole Ø14.00 at [31.581, 22.0, -6.223]
- extra in ours: hole Ø15.00 at [33.65, 22.0, -6.223]

## renders

- overlay_front.png
- overlay_left.png
- overlay_top.png
- overlay_iso.png
- ours_iso.png
- ref_iso.png
