"""part:microduck-foot-right — the right foot cap ("foot_right" in Pollen's MJCF).

MEASURED FACT (out/measure/foot/measure2.py, 2026-09-02): foot_right.stl IS
foot_left.stl mirrored about x = 0 — point-to-triangle p95 0.000 mm, max
0.005 mm, bboxes exact mirrors (x -70.166..-30.081 vs 30.081..70.166). So
this part is the left foot cap's geometry with HAND = -1: one source of
measured numbers, two hands. Every dimension lives in
../../../../microduck-foot-left/iterations/v0.0.2/cad/part.py with the probe
it came from; this file only flips the hand (the ankle-right part.py set
this pattern).

Frame: Pollen's foot_right.stl frame — x -70.166..-30.081, y -12..42,
z -29.251..-12.342. Graded against
reference/pollen-microduck-rl/assets/foot_right.stl by cad-refcheck.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. Imports cecad +
stdlib only (importlib is stdlib).
"""
import importlib.util
import os

_LEFT = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", "..", "microduck-foot-left", "iterations", "v0.0.2", "cad", "part.py"))


def _left_module():
    spec = importlib.util.spec_from_file_location("microduck_foot_left_part", _LEFT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build(doc, params=None):
    if params:
        raise ValueError("microduck-foot-right takes no build parameters (got %s)" % sorted(params))
    mod = _left_module()
    mod.HAND = -1              # mirror about x = 0 (measured: true mirror, p95 0.000 mm)
    return mod.build(doc)
