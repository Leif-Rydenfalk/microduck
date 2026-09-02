"""part:microduck-ankle-right — the right ankle bracket ("ankle_right" in Pollen's MJCF).

MEASURED FACT (out/measure/ankle/mirror-test.json, 2026-09-01): ankle_right.stl
IS ankle_left.stl mirrored about x = 0 — p95 surface distance 0.000 mm, max
0.0087 mm, bbox delta 0.000 mm, no shift. So this part is the left bracket's
geometry with HAND = -1: one source of measured numbers, two hands. Every
dimension lives in ../../../../microduck-ankle-left/iterations/v0.0.1/cad/part.py
with the probe it came from; this file only flips the hand.

Frame: Pollen's ankle_right.stl frame — x -69.854..-30.364 (the mirror of the
left's +x range), y 0.163..36.663, z -22.523..2.977. Graded against
reference/pollen-microduck-rl/assets/ankle_right.stl by cad-refcheck.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. Imports cecad +
stdlib only (importlib is stdlib).
"""
import importlib.util
import os

_LEFT = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", "..", "microduck-ankle-left", "iterations", "v0.0.1", "cad", "part.py"))


def _left_module():
    spec = importlib.util.spec_from_file_location("microduck_ankle_left_part", _LEFT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build(doc, params=None):
    if params:
        raise ValueError("microduck-ankle-right takes no build parameters (got %s)" % sorted(params))
    mod = _left_module()
    mod.HAND = -1                      # mirror about x = 0 (measured: true mirror, max dev 0.0087 mm)
    return mod.build(doc)
