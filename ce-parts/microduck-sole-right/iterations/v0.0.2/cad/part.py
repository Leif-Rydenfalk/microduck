"""part:microduck-sole-right — the right TPU sole ("sole_right" in Pollen's MJCF).

MEASURED FACT (out/measure/foot/measure2.py, 2026-09-02): sole_right.stl IS
sole_left.stl mirrored about x = 0 — point-to-triangle p95 0.002 mm, max
0.008 mm, bboxes exact mirrors (x -70.554..-29.455 vs 29.455..70.554). So
this part is the left sole's geometry with HAND = -1: one source of measured
numbers, two hands. Every dimension lives in
../../../../microduck-sole-left/iterations/v0.0.2/cad/part.py with the probe
it came from; this file only flips the hand (the ankle-right part.py set
this pattern).

Frame: Pollen's sole_right.stl frame — x -70.554..-29.455, y -12..42,
z -31.250..-18.342. Graded against
reference/pollen-microduck-rl/assets/sole_right.stl by cad-refcheck.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. Imports cecad +
stdlib only (importlib is stdlib).
"""
import importlib.util
import os

_LEFT = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", "..", "microduck-sole-left", "iterations", "v0.0.2", "cad", "part.py"))


def _left_module():
    spec = importlib.util.spec_from_file_location("microduck_sole_left_part", _LEFT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build(doc, params=None):
    if params:
        raise ValueError("microduck-sole-right takes no build parameters (got %s)" % sorted(params))
    mod = _left_module()
    mod.HAND = -1              # mirror about x = 0 (measured: true mirror, p95 0.002 mm)
    return mod.build(doc)
