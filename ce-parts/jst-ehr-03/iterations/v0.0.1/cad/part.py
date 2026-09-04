"""part:jst-ehr-03 — JST EHR-3 (ROBOTIS writes 'EHR-03'), 3-circuit EH cable housing.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. Imports only
cecad + stdlib. No parameters: a housing has one shape.

EVERY NUMBER IS READ OFF JST'S OWN DRAWING — eEH.pdf p.3 "Housing"
(docs/fetched/eEH.pdf, fetched jst-mfg.com 2026-09-04, sha256 9e35874b…):

    p.3 table row 3:   EHR-3   A = 5.0   B = 9.5
    p.3 drawing:       height 6.5, thickness 3.8, lock rib 0.6, pitch 2.5,
                       circuit No. 1 at (2.25) from the end (B = A + 2 x 2.25),
                       material PA 66, natural (white)
    p.1:               "The top entry type is 3.8 mm in thickness and 8.1 mm
                       in height" (the MATED stack, header + housing)
    p.2 layout:        (8.1) mated assembly height

FRAME (cad/interfaces.json 'mate'): origin at the centre of the contact row
ON THE HOUSING'S MATING FACE (the face that goes down onto the header);
+z is the INSERTION DIRECTION — pointing the way the housing travels to
seat, i.e. into the header and away from the wires; +x runs along the row
from circuit No. 1 to No. 3; +y toward the housing's closed back (the
lock/latch side is -y, matching the header's open face). The body
therefore occupies z in [-6.5, 0] and the wires leave the z = -6.5 face
toward -z. This is the same handedness as a screw whose axis points into
the hole, and it is what makes connection:jst-eh-3pin's transform a flip
about x plus a 1.6 mm seat.

SIMPLIFIED, and said: outer envelope 9.5 x 3.8 x 6.5 with three
through-cavities 1.8 x 1.8 for the contacts (SEH-001T-P0.6 is 1.6 wide on
p.2's contact drawing; 1.8 is the clearance chosen so the built solid does
not fuse to a crimp placed inside it — a MODELLING number, not a vendor
one) and three wire holes phi 1.9 at the wire face (the crimp's maximum
insulation O.D., p.2). The lock rib is a 0.6 x 0.6 bar along the -y face
as drawn. The latch window and the polarising key are not modelled.
"""

CIRCUITS = 3
PITCH = 2.5            # eEH.pdf p.3 "2.5"
A_MM = 5.0             # p.3 table EHR-3
B_MM = 9.5             # p.3 table EHR-3
THICK = 3.8            # p.3 drawing "3.8"
HEIGHT = 6.5           # p.3 drawing "6.5"
LOCK_RIB = 0.6         # p.3 drawing "0.6"
END_MARGIN = 2.25      # p.3 drawing "(2.25)"
CAVITY_SQ = 1.8        # modelling clearance around the 1.6 mm contact (p.2)
WIRE_HOLE_D = 1.9      # p.2 contact table: SEH-001T-P0.6 insulation O.D. max 1.9
ROW_FROM_OPEN_FACE = 1.6   # taken from the header (p.4 "(1.6)") so the rows align when mated
MATED_HEIGHT = 8.1     # p.1 / p.2


def pin_xs():
    return [(-A_MM / 2.0) + i * PITCH for i in range(CIRCUITS)]


def build(doc, params=None):
    from cecad.core import Part
    if params:
        raise ValueError("jst-ehr-03 takes no build parameters (got %s)" % sorted(params))
    p = Part("jst-ehr-03", material="NYLON")   # PA 66 per eEH.pdf p.3; cecad fits.py names it NYLON
    y0 = -ROW_FROM_OPEN_FACE
    # body: z from -6.5 (wire face) to 0 (mating face)
    p.box(B_MM, THICK, HEIGHT, at=(-B_MM / 2.0, y0, -HEIGHT))
    # lock rib along the open (-y) face, full length, at the mating end
    p.box(B_MM, LOCK_RIB, LOCK_RIB, at=(-B_MM / 2.0, y0 - LOCK_RIB, -HEIGHT + 2.0))
    for x in pin_xs():
        # contact cavity through the body
        p.box(CAVITY_SQ, CAVITY_SQ, HEIGHT + 2.0,
              at=(x - CAVITY_SQ / 2.0, -CAVITY_SQ / 2.0, -HEIGHT - 1.0), op="cut")
        # wire entry counterbore at the wire face
        p.cyl(WIRE_HOLE_D, 1.5, at=(x, 0.0, -HEIGHT - 0.5), axis="z", op="cut")
    p.clean()
    p.connector("mate", at=(0.0, 0.0, 0.0), dir="+z", up="+x",
                spec="EHR-3 contact row centre on the mating face; +z insertion direction; +x circuit 1 -> 3")
    p.connector("wire_face", at=(0.0, 0.0, -HEIGHT), dir="-z", up="+x",
                spec="where the three wires leave; 2.5 mm pitch")
    return p
