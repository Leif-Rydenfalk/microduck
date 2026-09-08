# part:microduck-sole-right — the right TPU sole

sole_right.stl IS sole_left.stl mirrored about x = 0 (point-to-triangle
p95 0.002 mm, max 0.008 mm — out/measure/foot/measure2.py), so this folder
holds no geometry of its own: cad/part.py loads the left part.py and sets
HAND = -1. All measurements and the CANNOT DETERMINE list live in
ce-parts/microduck-sole-left/iterations/v0.0.2/docs/README.md.

Graded on its own mesh: cad-refcheck vs sole_right.stl PASS —
p95 0.05/0.06 mm, bbox delta <= 0.03 mm
(evidence/refcheck/, out/refcheck/microduck-sole-right/r1/).
