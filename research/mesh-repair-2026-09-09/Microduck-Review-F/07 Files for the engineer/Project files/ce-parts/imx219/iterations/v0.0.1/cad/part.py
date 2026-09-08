"""part.py — build or load this part's geometry. cecad-native.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. Load
geometry/*.step when it is there; construct parametrically when it is not.
Imports cecad + stdlib, nothing else.
"""


def build(doc, params=None):
    raise NotImplementedError("imx219: no geometry yet")
