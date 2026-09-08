"""part:bearing-15x10x3 — deep-groove ball bearing, 15 OD x 10 ID x 3 W (61700 / MR6700).

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. Imports only
cecad + stdlib. A BOUGHT part (61700 family, sourcing.json); the geometry
here is a datasheet-faithful envelope of Pollen's published mesh
`reference/pollen-microduck-rl/assets/seeed_bearing__configuration_default.stl`
(metres, 20970 tris), measured 2026-09-02 with `cecad.meshfeatures.cylinders`
and `cecad.meshslice.intervals`, and graded against that mesh by
`cad-refcheck` (evidence/refcheck/).

FRAME — Pollen's mesh frame: axis = z, faces at z = 0 and z = 3, centred on
the origin in x/y (numpy bbox x,y -7.5..7.5, z 0..3).

WHAT THE MESH SHOWS (every number a measurement):
  meshfeatures: bore hole D10.0 len 2.6 (chamfered 0.2 each end),
                OD boss  D15.0 len 2.4 (chamfered 0.3 each end).
  meshslice x-intervals at y=0:
    z=0.5..2.5 : (5.0,5.75) and (6.75,7.5)      -> inner ring r 5..5.75, outer ring r 6.75..7.5
    z=1.5      : extra (6.099,6.402)            -> cage band r 6.1..6.4
    z=0.05     : (5.15,5.75),(6.75,7.25)        -> bore chamfer 0.2, OD chamfer 0.3
  meshslice z-intervals: (6.25,0): 1.0..2.0 (cage 1 mm tall); (5.6,0): 0..3;
    (7.4,0): 0.2..2.8. Cage ring closed all round (72/72 probe angles hit).
"""

# ---- measured (mm) ----------------------------------------------------------
W = 3.0                 # width, z 0..3 (bbox)
BORE_R = 5.0            # bore Ø10.0 (meshfeatures hole)
IR_OUT_R = 5.75         # inner-ring outer radius (x-intervals 5..5.75)
OR_IN_R = 6.75          # outer-ring inner radius (x-intervals 6.75..7.5)
OD_R = 7.5              # OD Ø15.0 (meshfeatures boss)
CH_BORE = 0.2           # bore-edge chamfer (z=0.05 cut: r starts 5.15; hole len 2.6)
CH_OD = 0.3             # OD-edge chamfer (z=0.05 cut: r ends 7.25; boss len 2.4)
CAGE_R = (6.1, 6.4)     # cage band radii (z=1.5 cut: 6.099..6.402)
CAGE_Z = (1.0, 2.0)     # cage band height (z-intervals at r 6.25)

MATERIAL = "steel"      # chrome bearing steel per the sourced offer (sourcing.json)


def build(doc, params=None):
    from cecad.core import Part
    if params:
        raise ValueError("bearing-15x10x3 takes no build parameters (got %s)" % sorted(params))
    p = Part("bearing-15x10x3", material=MATERIAL)
    # inner ring: bore chamfered CH_BORE at both faces
    p.revolve([(BORE_R + CH_BORE, 0.0), (IR_OUT_R, 0.0), (IR_OUT_R, W),
               (BORE_R + CH_BORE, W), (BORE_R, W - CH_BORE), (BORE_R, CH_BORE)])
    # outer ring: OD chamfered CH_OD at both faces
    p.revolve([(OR_IN_R, 0.0), (OD_R - CH_OD, 0.0), (OD_R, CH_OD),
               (OD_R, W - CH_OD), (OD_R - CH_OD, W), (OR_IN_R, W)])
    # cage band (the mesh's stand-in for balls + cage: a closed rectangular ring)
    p.revolve([(CAGE_R[0], CAGE_Z[0]), (CAGE_R[1], CAGE_Z[0]),
               (CAGE_R[1], CAGE_Z[1]), (CAGE_R[0], CAGE_Z[1])])
    p.clean()
    p.connector("bore", at=(0, 0, W / 2), dir="+z")     # rides a Ø10 shaft/boss
    p.connector("od", at=(0, 0, W / 2), dir="+z")       # press-fits a Ø15 housing
    return p
