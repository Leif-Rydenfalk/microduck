"""part:jst-seh-001t-p0.6 — JST SEH-001T-P0.6 crimp contact for the EH housing.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. No parameters.

WHAT THE DRAWING GIVES (eEH.pdf p.2 "Contact", docs/fetched/eEH.pdf, sha256
9e35874b…): the contact drawing carries the figures 5.7, 2.85, 2.05, 1.1,
2, 1.6 and the table row "SEH-001T-P0.6 | #30 to #22 (0.05 to 0.33) |
insulation O.D. 1.0 to 1.9 | 9,000/reel", material "Phosphor bronze,
tin-plated". pdftotext loses the leader lines, so WHICH figure is which is
read as follows and stated as a reading, not a fact: 5.7 = overall length
(the longest figure on the drawing), 2.85 + 2.05 = contact box + wire
barrel lengths along that 5.7 (they lie side by side under the length
dimension), 1.6 = box width (it agrees with the square-post 0.64 header pin
needing a box under 1.8 to fit the EHR cavity), 2 = crimp barrel height,
1.1 = box height. The built solid is an ENVELOPE from those readings —
a 2.85 x 1.6 x 1.1 contact box and a 2.85 x 1.6 x 2.0 crimp barrel — and
the verdict in component.json is CANNOT DETERMINE on shape for exactly
that reason.

FRAME: origin at the contact-box tip (the end the header post enters),
+z toward the wire (the contact's length axis), +x across the width.
Inside an EHR-3 the contact points +z toward the wire face, i.e. the
housing's -z — the cable part orients it.
"""

LENGTH = 5.7           # eEH.pdf p.2 contact drawing (read as overall length)
BOX_L = 2.85           # p.2 drawing, read as the contact-box length
BARREL_L = 2.05        # p.2 drawing, read as the crimp barrel length
WIDTH = 1.6            # p.2 drawing, read as the box width
BOX_H = 1.1            # p.2 drawing, read as the box height
BARREL_H = 2.0         # p.2 drawing, read as the barrel height
WIRE_AWG_RANGE = (30, 22)         # p.2 table "#30 to #22 (0.05 to 0.33)"
WIRE_MM2_RANGE = (0.05, 0.33)
INSULATION_OD_RANGE = (1.0, 1.9)  # p.2 table "1.0 to 1.9"


def build(doc, params=None):
    from cecad.core import Part
    if params:
        raise ValueError("jst-seh-001t-p0.6 takes no build parameters (got %s)" % sorted(params))
    p = Part("jst-seh-001t-p0.6", material="BRASS")   # phosphor bronze per p.2; cecad fits.py has no
                                                      # phosphor bronze — BRASS (8.50 g/cm3) is the nearest
                                                      # named copper alloy and the mass is CANNOT DETERMINE anyway
    p.box(WIDTH, BOX_H, BOX_L, at=(-WIDTH / 2.0, -BOX_H / 2.0, 0.0))
    p.box(WIDTH, BARREL_H, LENGTH - BOX_L, at=(-WIDTH / 2.0, -BARREL_H / 2.0, BOX_L))
    p.clean()
    p.connector("post", at=(0.0, 0.0, 0.0), dir="-z", up="+x",
                spec="where the header's □0.64 post enters")
    p.connector("wire", at=(0.0, 0.0, LENGTH), dir="+z", up="+x",
                spec="crimp barrel: AWG #30..#22, insulation O.D. 1.0..1.9")
    return p
