# part:microduck-foot-right — the right foot cap

foot_right.stl IS foot_left.stl mirrored about x = 0 (point-to-triangle
p95 0.000 mm, max 0.005 mm — out/measure/foot/measure2.py), so this folder
holds no geometry of its own: cad/part.py loads the left part.py and sets
HAND = -1. All measurements and the CANNOT DETERMINE list live in
ce-parts/microduck-foot-left/iterations/v0.0.2/docs/README.md.

Graded on its own mesh: cad-refcheck vs foot_right.stl PASS —
p95 0.37/0.26 mm, bbox delta <= 0.004 mm, 2/2 holes matched
(evidence/refcheck/, out/refcheck/microduck-foot-right/r1/).
