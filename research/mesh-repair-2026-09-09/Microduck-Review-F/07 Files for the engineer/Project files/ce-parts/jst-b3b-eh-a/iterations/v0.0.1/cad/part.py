"""part:jst-b3b-eh-a — JST B3B-EH-A, 3-circuit EH top-entry Type A board header.

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. Imports only
cecad + stdlib. Takes no parameters: a header has one shape.

EVERY NUMBER BELOW IS READ OFF JST'S OWN DRAWING — eEH.pdf, "EH CONNECTOR"
(docs/fetched/eEH.pdf, fetched from jst-mfg.com/product/pdf/eng/eEH.pdf on
2026-09-04, sha256 9e35874bf27505bab79d6af783118fa926ceef7a91b7cb8421f108ff
69a1b7f2 — the same bytes the workshop's part:conn-jst-eh-2.5mm cites):

    p.4 "Header/ Type A", table row 3:  B3B-EH-A   A = 5.0   B = 10.0
    p.4 side view (top entry, 3 circuits or more): wafer thickness 3.8,
        height above board 6, post 3.3 above the wafer floor (Note 2:
        "The EH Type A header has a post length of 3.3 mm designed to
        improve mating workability"), 5.1 cavity, post 3.2 below the board,
        post section square 0.64, pin row (1.6) from the open face, pitch 2.5,
        (2.5) end margin: B = A + 2 x 2.5.
    p.2 "PC board layout": hole phi 0.9 +0.1/0, pitch 2.5 +-0.05, (8.1)
        mated assembly height, (1.6) row-to-outline.

Corroborated against KiCad's JST_EH_B3B-EH-A_1x03_P2.50mm_Vertical.step
(workshop part:conn-jst-eh-2.5mm/geometry, CC-BY-SA-4.0 Rene Poeschl 2019),
MEASURED 2026-09-04 with FreeCAD 1.1.3: bbox x -2.5..7.5 (10.0), y -2.2..1.6
(3.8), z -3.2..6.0 (9.2), volume 97.0168 mm3. Every extent agrees with the
drawing to 0.0000 mm; the KiCad body puts pin 1 at x = 0, this folder puts
the ROW CENTRE at x = 0 (the +2.5 shift is the only difference).

FRAME (cad/interfaces.json 'mate'): origin at the centre of the pin row ON
THE BOARD TOP SURFACE; +z is the mating direction (out of the board, the way
the housing arrives from); +x runs along the row from circuit No. 1 to No. 3;
+y is toward the wafer's closed back (pins sit 1.6 from the open/latch face
at -y, 2.2 from the back face at +y — the (1.6) on p.4 and the KiCad y
extent -2.2..1.6).

WHAT IS SIMPLIFIED, and it is said: the wafer is its outer envelope
10.0 x 3.8 x 6.0 with the cavity cut as 9.5 (the EHR-3 housing's B, p.3)
x 3.8 (through the thickness — no back wall modelled) x 5.1 deep from the
top, leaving a 0.9 floor and 0.25 end walls; the drawing's latch relief and
polarising rib are not modelled. Posts are square 0.64 as drawn. So the
envelope and the pin positions are exact; the internal detail is not, and
the CANNOT DETERMINE in component.json names that.
"""

CIRCUITS = 3
PITCH = 2.5          # eEH.pdf p.1 title "2.5 mm pitch"; p.4 drawing 2.5
A_MM = 5.0           # p.4 table, B3B-EH-A
B_MM = 10.0          # p.4 table, B3B-EH-A
THICK = 3.8          # p.4 side view
HEIGHT = 6.0         # p.4 front view "6"
CAVITY_DEPTH = 5.1   # p.4 side view "5.1"
POST_ABOVE_FLOOR = 3.3   # p.4 Note 2
POST_BELOW = 3.2     # p.4 front view "3.2"
POST_SQ = 0.64       # p.4 "□0.64"
ROW_FROM_OPEN_FACE = 1.6  # p.4 "(1.6)"
HOUSING_B = 9.5      # p.3 table EHR-3 B — the cavity the housing needs
FLOOR = HEIGHT - CAVITY_DEPTH          # 0.9
END_WALL = (B_MM - HOUSING_B) / 2.0    # 0.25
MATED_HEIGHT = 8.1   # p.2 "(8.1)" — used by connection:jst-eh-3pin, restated here


def pin_xs():
    """x of each post, circuit 1 first: -2.5, 0.0, +2.5."""
    return [(-A_MM / 2.0) + i * PITCH for i in range(CIRCUITS)]


def build(doc, params=None):
    from cecad.core import Part
    if params:
        raise ValueError("jst-b3b-eh-a takes no build parameters (got %s); "
                         "a 3-circuit header has one shape" % sorted(params))
    p = Part("jst-b3b-eh-a", material="NYLON")  # PA 66 per eEH.pdf p.4; cecad fits.py names it NYLON (1.14 g/cm3)
    y0 = -ROW_FROM_OPEN_FACE            # open face at y = -1.6, back at y = +2.2
    # wafer envelope 10.0 x 3.8 x 6.0 sitting on the board (z 0..6)
    p.box(B_MM, THICK, HEIGHT, at=(-B_MM / 2.0, y0, 0.0))
    # housing cavity from the top: 9.5 long, through the thickness, 5.1 deep
    p.box(HOUSING_B, THICK + 2.0, CAVITY_DEPTH + 0.01,
          at=(-HOUSING_B / 2.0, y0 - 1.0, FLOOR), op="cut")
    # three square posts: 3.2 below the board to 3.3 above the wafer floor
    for x in pin_xs():
        p.box(POST_SQ, POST_SQ, POST_BELOW + FLOOR + POST_ABOVE_FLOOR,
              at=(x - POST_SQ / 2.0, -POST_SQ / 2.0, -POST_BELOW))
    p.clean()
    p.connector("mate", at=(0.0, 0.0, 0.0), dir="+z", up="+x",
                spec="JST EH 3-circuit header row centre on the board plane; "
                     "+z mating direction, +x circuit 1 -> 3")
    p.connector("pcb_land", at=(0.0, 0.0, 0.0), dir="-z", up="+x",
                spec="3 x phi0.9 +0.1/0 holes on 2.5 +-0.05 pitch (eEH.pdf p.2)")
    return p
