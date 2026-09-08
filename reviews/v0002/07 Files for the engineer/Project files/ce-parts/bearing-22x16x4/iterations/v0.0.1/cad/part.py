"""part:bearing-22x16x4 — thin-section deep-groove ball bearing, 22 OD x 16 ID x 4 W.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. Imports only
cecad + stdlib. A BOUGHT part (MR1622-ZZ family, sourcing.json); the
geometry here is a datasheet-faithful envelope of Pollen's published mesh
`reference/pollen-microduck-rl/assets/seeed_bearing__configuration__22x16x4.stl`
(metres, 20970 tris), measured 2026-09-02 with `cecad.meshfeatures.cylinders`
and `cecad.meshslice.intervals`, and graded against that mesh by
`cad-refcheck` (evidence/refcheck/).

FRAME — Pollen's mesh frame: axis = z, faces at z = 0 and z = 4, centred on
the origin in x/y (numpy bbox x,y -11..11, z 0..4).

WHAT THE MESH SHOWS (every number a measurement):
  meshfeatures: bore hole D16.0 len 3.6 (chamfered 0.2 each end),
                OD boss  D22.0 len 3.4 (chamfered 0.3 each end).
  meshslice x-intervals at y=0:
    z=0.5..3.5 : (8.0,9.0) and (10.0,11.0)      -> inner ring r 8..9, outer ring r 10..11
    z=2.0      : extra (9.345,9.645)            -> cage band r 9.35..9.65
    z=0.05     : (8.15,9.0),(10.0,10.75)        -> bore chamfer 0.2, OD chamfer 0.3
  meshslice z-intervals: (9.5,0): 1.5..2.5 (cage 1 mm tall); (8.2,0): 0..4;
    (10.9,0): 0.2..3.8. Cage ring closed all round (72/72 probe angles hit).
"""

# ---- measured (mm) ----------------------------------------------------------
W = 4.0                 # width, z 0..4 (bbox)
BORE_R = 8.0            # bore Ø16.0 (meshfeatures hole)
IR_OUT_R = 9.0          # inner-ring outer radius (x-intervals 8..9)
OR_IN_R = 10.0          # outer-ring inner radius (x-intervals 10..11)
OD_R = 11.0             # OD Ø22.0 (meshfeatures boss)
CH_BORE = 0.2           # bore-edge chamfer (z=0.05 cut: r starts 8.15; hole len 3.6)
CH_OD = 0.3             # OD-edge chamfer (z=0.05 cut: r ends 10.75; boss len 3.4)
CAGE_R = (9.35, 9.65)   # cage band radii (z=2 cut: 9.345..9.645)
CAGE_Z = (1.5, 2.5)     # cage band height (z-intervals at r 9.5)

MATERIAL = "steel"      # GCR15 bearing steel per the sourced offer (sourcing.json)


def build(doc, params=None):
    from cecad.core import Part
    if params:
        raise ValueError("bearing-22x16x4 takes no build parameters (got %s)" % sorted(params))
    p = Part("bearing-22x16x4", material=MATERIAL)
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
    p.connector("bore", at=(0, 0, W / 2), dir="+z")     # press-fits a Ø16 shaft/boss
    p.connector("od", at=(0, 0, W / 2), dir="+z")       # press-fits a Ø22 housing
    return p
