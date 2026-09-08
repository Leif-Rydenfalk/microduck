#!/usr/bin/env python3
"""electronics/banana-contact/board.py — OUR "banana" battery-contact PCB.

THIS IS NOT POLLEN'S BOARD. Pollen ships a mesh for the RETAINER that clamps
it (`banana_pcb_locker`) and for the CRADLE it sits in (`power_support`), but
no mesh, no drawing, no schematic and no BOM for the contact board itself.
docs/ELECTRONICS-AND-SOFTWARE.md §11 says only "battery | — | NP-F550 ->
banana contact PCB -> HAT -> 40-pin (5 V to Radxa) and bus VDD | path known;
regulators, fusing CANNOT DETERMINE", and electronics/netlist.py folds it
into a wire: "the 'banana' contact PCB ... which has no electrical record — a
passive board, folded into this wire."

So this file does the one thing that CAN be done honestly: it MEASURES the
pocket the board has to live in, off Pollen's own meshes, and draws a board
that fits it. Every dimension below is a number read off an STL today; every
electrical choice is ours, named B1..B6, with the alternative it beat.

Run:  python3 electronics/banana-contact/board.py             build/check/fab
      python3 electronics/banana-contact/board.py --self-test break a check

THE MEASUREMENTS (reference/pollen-microduck-rl/assets/*.stl, read
2026-09-02 with a plain-python STL sectioner; the STL is in metres, printed
here in mm; mesh frame = the Onshape assembly frame the MJCF places from)

  power_support.stl
    head plate .............. y 25.000 .. 27.000  (2.000 mm wall)
    head plate top edge ..... z 56.944 at x ~ +4, 55.51 at x +/-24 (CURVED,
                              and BEHIND the board, not above it — not a
                              constraint on the board's height)
    pocket floor (ledge) .... z 49.070 .. 50.930   (1.860 mm step)
    pocket clear width ...... x -22.930 .. +22.930 = 45.860
    locker key-tab slots .... 2.919 x 1.860 at x = +/-16.900, z 49.070..50.930
    screw posts ............. dia 4.104 x 4.053, x = +/-25.198, z 53.773,
                              y 25.000 -> 34.800, M2 tap dia 1.772
    window through the plate  x -9.990 .. +1.990  (12.000 wide, centre -4.000),
                              floor z 52.117, open to the top edge
  banana_pcb_locker.stl
    bar ..................... 54.041 x 6.672 x 1.500, y 35.000 .. 36.500
    eyes .................... dia 2.174 at x = +/-25.000, z 53.600
    key tabs ................ 2.470 x 2.300 x 1.970 at x = +/-16.900, y to 32.700
    its own window .......... 12.000 wide, centre x -4.000, floor z 52.117

  ray-cast solid/air map of power_support at y = 31.000 (mid-gap), 2 mm grid:
    z >= 56.0 ....... all air
    z 51.0..55.5 .... air everywhere except x = +/-25 (the two screw posts)
    z 49.5..50.5 .... solid x -15..+15, plus x +/-19, +/-21, +/-25;
                      AIR at x +/-17 (the locker's tab slots) and +/-23
    z <= 49.0 ....... all air

  => the space a board can occupy is x -23.146..+23.146 (46.292, the posts'
     inner faces), z 50.930 (rib top) .. 55.626 (locker bar top, because a
     board above that is a board the retainer does not cover) = 4.696, and
     y 27.000..35.000 (8.000).

OUR DECISIONS

  B1  Outline 45.800 x 4.600 mm, 1.6 mm FR-4. CORRECTED 2026-09-02 from
      45.800 x 5.100 after RAY-CASTING the power_support solid instead of
      reading section outlines: at y = 31.000, mid-gap, the only material
      above z = 51.000 is the two screw posts, so the pocket is bounded in x
      by their inner faces at x = +/-23.146 (clear 46.292, not the 45.860 the
      ledge outline suggested) and it is OPEN UPWARD — the head plate's top
      edge is behind the board, not above it, and using it was the wrong
      constraint. What actually bounds the top is the locker bar's own
      silhouette (x +/-27.025, z 48.974..55.626), because a board taller than
      that is a board the retainer does not cover. Floor is the rib top at
      z = 50.930. So the usable pocket is 46.292 x 4.696 and this board is
      45.800 x 4.600: 0.246 mm per side in x, 0.023 mm per side in z. 1.6 mm is one of JLCPCB's
      published thicknesses ('0.4/0.6/0.8/1.0/1.2/1.6/2.0 mm',
      jlcpcb.com/capabilities/pcb-capabilities re-read 2026-09-02) and the
      one their 2-layer default price covers.
      ALTERNATIVE IT BEAT: 54.041 x 6.672 (the locker bar's own outline) —
      rejected because the bar spans the two screw posts and the BOARD sits
      between the pocket walls 22.930 mm out, which is 8.2 mm narrower.
  B2  No mounting holes. The posts at x = +/-25.198 are OUTSIDE the pocket's
      45.860 mm clear width, so a board with holes over them could not enter
      the pocket at all. The board is captured by the pocket in x and z and
      clamped by the locker bar in y.
  B3  Three battery contact pads at 4.000 mm pitch. THE NP-F TERMINAL PITCH
      IS NOT PUBLISHED. Sony publishes no mechanical drawing of the pack's
      contact block; the only public description of the terminal set found is
      a forum thread that names them and gives no dimension — "from left to
      right, is the positive terminal, 'C' labelled contact pad and negative
      terminal" (candlepowerforums.com/threads/sony-np-f570-pinout.337813,
      fetched 2026-09-02) — and searching for a pitch returned nothing.
      So the pitch here is DERIVED, not measured: the plate's window is
      12.000 mm wide and is the only opening the terminals can reach through,
      and three equal cells in 12.000 mm put the pads on 4.000 mm centres.
      WHAT WOULD SETTLE IT: a caliper across the terminal block of a physical
      NP-F550. Until then this number is marked derived everywhere it appears.
      ALTERNATIVE IT BEAT: 3.500 mm (more margin to the window walls) —
      rejected because nothing supports it either and 4.000 is the value the
      window itself implies.
  B4  Contact style: flat gold pads, 2.400 x 2.400 mm, mask-opened, NO paste.
      The pack's own spring contacts land on them.
      Surface finish ENIG, not HASL — HASL is solder, and solder cold-flows
      and oxidises under a sliding spring contact. JLCPCB publishes 'HASL
      (leaded / lead-free), ENIG, OSP' for this process, so ENIG is orderable
      at the same fab.
      ALTERNATIVE IT BEAT: spring fingers on the PCB — rejected on the
      measurement: the pocket gives 8.000 mm in y and the contact block has
      to live in it, but the board itself is only 5.100 mm tall, and no
      through-hole spring contact we could confirm fits that strip.
  B5  Harness: three 0.800 mm plated holes on 4.000 mm centres for a SOLDERED
      three-wire tail, not a connector. Measured reason: every vertical JST
      header this project has confirmed is deeper than this board is tall —
      B2B-XH-A body 5.75, B3B-EH-A housing 10.0, B2B-PH-K-S 4.5 mm — so none
      of them can sit on a 5.100 mm strip. The tail terminates at the HAT end
      in the housing that mates the HAT's J2 (XHP-2), which is where the
      netlist's 'battery' wire lands.
  B6  The 'C' terminal is brought out on its own net BAT_T and goes nowhere.
      Nothing in Pollen's published source reads it: electronics/netlist.py
      wires the pack as {BAT+: VBAT, BAT-: GND} and no third conductor
      appears in wiring/CABLES.md. It is fitted because the pack HAS the
      terminal and a board that ignores it cannot later be told to read it.

CURRENT: not stated, on purpose. This board carries the whole robot's pack
current. wiring/CABLES.md's own basis is "1 A per moving servo, the lane's
stated basis ... the vendor publishes no running current — only standby
17 mA and stall 1.47 A at 5 V", i.e. an ASSUMPTION, and Sony publishes no
maximum continuous discharge current for the NP-F550. So check_current
reports CANNOT DETERMINE. What IS stated is the capacity of the copper
actually drawn: the two power tracks are 1.500 mm wide on 1 oz outer copper,
which IPC-2221 §6.2 (I = 0.048 * dT^0.44 * A^0.725, A in mil^2) puts at
3.21 A for a 10 degC rise — computed in this file, printed in the notes.
"""
import importlib.util
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

_spec = importlib.util.spec_from_file_location(
    "microduck_netlist", os.path.join(os.path.dirname(HERE), "netlist.py"))
_net = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_net)

from cecad.pcb import Board, Pad, custom                            # noqa: E402
from cecad.pcbcheck import check                                    # noqa: E402
from cecad.pcbfab import fab                                        # noqa: E402
from cecad.pcbview import plot, publish_pcb                         # noqa: E402

# ---------------------------------------------------------------------------
# PARAMETERS — the measured pocket, then the board that fits it
# ---------------------------------------------------------------------------
POCKET_W = 46.292        # between the two screw posts, x -23.146 .. +23.146
POCKET_H = 4.696         # z 50.930 (rib top) .. 55.626 (locker bar top)
POCKET_Y = 8.000         # y 27.000 .. 35.000, plate face to locker bar
W, H = 45.800, 4.600     # B1
THICK = 1.6

# mesh frame -> board frame (board origin = lower-left)
MESH_X0 = -22.900        # board x = mesh x + 22.900
MESH_Z0 = 50.930         # board y = mesh z - 50.930 (the rib top)
WINDOW_CENTRE = -4.000   # mesh x of the 12.000 mm window centre
WINDOW_W = 12.000
WINDOW_FLOOR = 52.117    # mesh z

CONTACT = 2.400          # B4 pad size
PITCH = 4.000            # B3 — DERIVED from WINDOW_W / 3, not measured
TAIL_DRILL = 0.800       # B5
TAIL_PITCH = 4.000

CX = WINDOW_CENTRE - MESH_X0                     # 18.900 in board x
CY = 3.200                                       # contact row, board y
TAIL_Y = 1.000                                   # wire-tail row, board y


def ipc2221_amps(width_mm, oz=1.0, dT=10.0, external=True):
    """IPC-2221 §6.2 current for a bare trace. Returns amps."""
    thick_mil = 1.378 * oz                       # 1 oz = 1.378 mil
    area_mil2 = (width_mm / 0.0254) * thick_mil
    k = 0.048 if external else 0.024
    return k * (dT ** 0.44) * (area_mil2 ** 0.725)


TRACK_W = 1.500
TRACK_A = ipc2221_amps(TRACK_W)


# ---------------------------------------------------------------------------
# footprints
# ---------------------------------------------------------------------------
def fp_contacts():
    """Three flat pads the pack's spring contacts land on (B3/B4).

    Pad order left-to-right in the BOARD frame follows the forum
    description read left-to-right on the pack: BAT+ , C , BAT- .
    """
    pads = []
    for i, name in enumerate(("BAT+", "T", "BAT-")):
        pads.append(Pad(name, (i - 1) * PITCH, 0.0, CONTACT, CONTACT,
                        shape="rect", paste=False, mask=0.0,
                        note="gold contact pad, no paste, no mask expansion "
                             "— a spring lands here, nothing is soldered"))
    return custom(
        "npf-contact-3", pads, courtyard=(2 * PITCH + CONTACT + 0.2,
                                          CONTACT + 0.2), height=0.0,
        why="B3/B4. Courtyard excess is 0.100 mm per side, not the 0.250 mm "
            "a placed component gets: nothing is placed here and nothing is "
            "reflowed here — these are bare landing areas for the pack's own "
            "springs, and the board is only 4.600 mm tall. "
            "Pitch 4.000 mm is DERIVED from the 12.000 mm window "
            "measured in power_support.stl (x -9.990..+1.990, centre "
            "-4.000), NOT from an NP-F550: Sony publishes no drawing of the "
            "terminal block and the only public description found "
            "(candlepowerforums.com/threads/sony-np-f570-pinout.337813, "
            "fetched 2026-09-02) names the three terminals '+', 'C', '-' and "
            "gives no dimension. A caliper across a real pack settles it. "
            "Pad 2.400 x 2.400 mm, mask opening 0.000 expansion so the gold "
            "area is exactly the drawn area.")


def fp_tail():
    """Three plated holes for a soldered 3-wire tail (B5)."""
    pads = [Pad(n, (i - 1) * TAIL_PITCH, 0.0, 1.4, 1.4,
                shape="rect" if i == 0 else "round",
                layer="*.Cu", drill=TAIL_DRILL)
            for i, n in enumerate(("BAT+", "T", "BAT-"))]
    return custom(
        "wire-tail-3", pads, courtyard=(2 * TAIL_PITCH + 1.7, 1.7),
        height=0.0,
        why="B5. Courtyard excess 0.100 mm per side (bare holes, nothing "
            "placed). 0.800 mm plated holes on 4.000 mm centres (the same pitch as "
            "the contacts, so every run is a straight hop and no two nets "
            "ever cross) take AWG24 tinned leads (0.511 mm conductor). Pad "
            "1.400 over the 0.800 drill = 0.300 mm annular ring, above JLCPCB's 'Recommended "
            "0.25 mm or above' for 1 oz 2-layer. Not a connector: the "
            "measured pocket is 5.150 mm tall and every JST header confirmed "
            "in this project is deeper than that.")


# ---------------------------------------------------------------------------
# the board
# ---------------------------------------------------------------------------
def build(self_test=None, publish=True, verbose=True):
    d = _net.electrical_design()

    b = Board("microduck_banana_contact", W, H, corner_r=0.5,
              rules="jlcpcb_2l_standard", stackup="jlcpcb-2layer-1.6mm",
              title="Microduck banana battery-contact PCB (reconstruction)",
              origin_note=(
                  "origin = board lower-left, mm, top view. Board frame maps "
                  "to the Pollen mesh frame by x_mesh = x_board - 22.900 and "
                  "z_mesh = y_board + 50.955, so the pocket measured in "
                  "power_support.stl (x -22.930..+22.930, z 50.930..56.080) "
                  "becomes x -0.030..45.830, y -0.025..5.125 here"))

    # The finish is an ORDER-FORM field, not a Gerber layer, so it has to be
    # stated where a fab will read it: the stackup line of out/fab/README.txt.
    b.stackup.finish = ("ENIG — REQUIRED, not the default. A sliding spring "
                        "contact on a HASL pad cold-flows and oxidises. "
                        "JLCPCB publishes 'HASL (leaded / lead-free), ENIG, "
                        "OSP' for this process (capabilities page, re-read "
                        "2026-09-02), so this is an order option.")

    b.add("P1", fp_contacts(), value="NP-F pack contacts", at=(CX, CY),
          note="B3/B4 — centred in the measured 12.000 mm window of the "
               "power_support head plate")
    b.add("P2", fp_tail(), value="3-wire tail to the HAT", at=(CX, TAIL_Y),
          note="B5 — soldered leads; the HAT end is the XHP-2 housing that "
               "mates robot-hat J2 (B2B-XH-A)")

    if self_test == "off-board":
        b.place("P2", at=(-1.0, TAIL_Y))     # hangs off the left edge

    # -- connectivity FROM the netlist ---------------------------------------
    # The robot netlist knows the pack as the owner `battery` with terminals
    # BAT+ and BAT-. They are the two contact pads of THIS board.
    b.bind(d, refs={"battery": "P1"},
           pins={"P1": {"BAT+": "BAT+", "BAT-": "BAT-"}}, strict=False)
    _resolve_offboard(b)

    b.attach("VBAT", "P2.BAT+")
    b.attach("GND", "P2.BAT-")
    b.net("BAT_T", "P1.T", "P2.T")

    # -- copper: three straight runs, hand-laid ------------------------------
    # No autorouter: three nets, three straight lines, and the two power runs
    # are 2.000 mm wide, which is 39% of the board's whole height. A router
    # would have nothing to decide.
    p1 = b.component("P1")
    p2 = b.component("P2")
    for net, pad, width in (("VBAT", "BAT+", TRACK_W),
                            ("GND", "BAT-", TRACK_W),
                            ("BAT_T", "T", 0.4)):
        a = p1.pad_xy(p1.fp.pad(pad))
        c = p2.pad_xy(p2.fp.pad(pad))
        b.track(net, [a, c], width=width)

    # Silk stays OFF the contact block: the pads are 2.600 mm on a 5.100 mm
    # board and there is no room between them for a legend.
    # F.Silk carries ONLY the polarity, and only where there is bare board:
    # the contact block is 10.6 mm of pad on a 5.1 mm strip and a legend
    # anywhere near it is silk on copper. The first plot of this board had
    # the name printed straight across the pads — looked at, and moved.
    b.text("+", (CX - PITCH - 3.4, CY), size=1.4)
    b.text("-", (CX + PITCH + 3.4, CY), size=1.4)
    b.text("banana contact PCB - NOT POLLEN'S",
           (8.0, 3.6), size=0.7, layer="B.Silk")
    b.text("pitch 4.000 DERIVED not measured",
           (10.0, 2.4), size=0.55, layer="B.Silk")

    # -- what nobody has published, said out loud ----------------------------
    b.notes.append(
        "THE `binding` CHECK REPORTS CANNOT DETERMINE, AND THAT IS CORRECT. "
        "BAT_T exists on this board and not in the robot netlist, because "
        "electronics/netlist.py wires the pack as {BAT+: VBAT, BAT-: GND} "
        "and nothing in Pollen's published source reads the pack's third "
        "terminal. Decision B6 fits it anyway. The check is right to say it "
        "cannot verify a net the netlist does not model.")
    b.notes.append(
        f"POCKET, MEASURED 2026-09-02 off Pollen's own meshes by RAY-CASTING "
        f"the power_support solid at y = 31.000 (mid-gap), not by reading "
        f"section outlines: clear width {POCKET_W:.3f} mm between the screw "
        f"posts' inner faces (x -23.146..+23.146), clear height "
        f"{POCKET_H:.3f} mm from the rib top z 50.930 to the locker bar's top "
        f"z 55.626, clear depth {POCKET_Y:.3f} mm (y 27.000 plate face .. "
        f"35.000 locker bar). This board is {W:.3f} x {H:.3f} x {THICK} mm, "
        f"so it enters with {(POCKET_W - W) / 2:.3f} mm per side in x and "
        f"{(POCKET_H - H) / 2:.3f} mm per side in z. The first cut of this "
        f"board was 5.100 mm tall because it used the head plate's top edge "
        f"as the ceiling; the plate is BEHIND the board, not above it.")
    b.notes.append(
        "WHAT IS ON EITHER SIDE OF THIS BOARD, MEASURED 2026-09-02. Placing "
        "this board's own box into the trunk_base body frame (x -24.600.."
        "-23.000, y -22.900..22.900, z 33.409..38.009 mm) and comparing it "
        "with every mesh placed in that body:\n"
        "  np_f970, the pack ....... 0.476 mm in x, 1.737 mm in z\n"
        "  banana_pcb_locker ....... 3.900 mm in x, on the other side\n"
        "  power_support ........... boxes overlap — the board is in its "
        "pocket, which is the point\n"
        "  left_shell / right_shell  boxes overlap — they enclose the trunk\n"
        "  xl330 (both hip yaws) ... 7.409 mm in z\n"
        "  trunk_base plate ........ 31.409 mm in z\n"
        "THE PACK IS 0.476 mm AWAY. That turns decision B4 from a preference "
        "into a requirement: the face toward the battery carries FLAT PADS "
        "and nothing else — no paste, no component, no protruding solder. "
        "The three tail wires must leave on the LOCKER side, where there is "
        "3.900 mm. Bounding boxes, not solids: a separation is a lower bound "
        "and an overlap is not proof of a collision.")
    b.notes.append(
        "CONTACT PITCH IS DERIVED, NOT MEASURED. 4.000 mm = the 12.000 mm "
        "window of the power_support head plate divided into three cells. "
        "Sony publishes no NP-F terminal drawing; a caliper across a "
        "physical NP-F550 pack settles it and nothing else does. Every "
        "document that repeats this number must repeat that sentence.")
    b.notes.append(
        f"COPPER CAPACITY: the two power tracks are {TRACK_W:.3f} mm wide on "
        f"1 oz outer copper. IPC-2221 §6.2 I = 0.048 * dT^0.44 * A^0.725 "
        f"(A in mil^2) gives {TRACK_A:.2f} A at a 10 degC rise "
        f"({ipc2221_amps(TRACK_W, dT=20.0):.2f} A at 20 degC). The DEMAND is "
        "CANNOT DETERMINE: wiring/CABLES.md's own worst case is an assumed "
        "1 A per moving servo (the vendor publishes only 17 mA standby and "
        "1.47 A stall at 5 V) and Sony publishes no maximum continuous "
        "discharge current for the pack.")
    b.confirm("P2", "There is no bought part behind this footprint to check "
              "a land pattern against: it is three plated holes for soldered "
              "wire. Drill 0.800 mm takes a stripped-and-tinned AWG24 lead "
              "(0.511 mm conductor); pad 1.400 mm "
              "gives a 0.300 mm annular ring against JLCPCB's 'Recommended "
              "0.25 mm or above; absolute minimum 0.18 mm' for 1 oz 2-layer "
              "(jlcpcb.com/capabilities/pcb-capabilities, re-read "
              "2026-09-02). P1 is deliberately NOT confirmed — its pitch is "
              "derived, and that CANNOT DETERMINE is the point.")
    b.notes.append(
        "SURFACE FINISH: ENIG, not the HASL default. A sliding spring "
        "contact on a solder-coated pad cold-flows and oxidises. JLCPCB "
        "publishes 'HASL (leaded / lead-free), ENIG, OSP' for this process "
        "(jlcpcb.com/capabilities/pcb-capabilities, re-read 2026-09-02), so "
        "this is an order option, not a special process. THE GERBERS DO NOT "
        "CARRY THE FINISH — it is an order-form field, and it is in the BOM "
        "and in the fab README because of that.")

    rep = check(b, verbose=verbose)
    if self_test:
        return b, rep

    os.makedirs(OUT, exist_ok=True)
    plot(b, os.path.join(OUT, "top.svg"), side="top", drc=rep, verbose=verbose)
    plot(b, os.path.join(OUT, "bottom.svg"), side="bottom", drc=rep,
         verbose=verbose)
    fab(b, os.path.join(OUT, "fab"), report=rep, verbose=verbose)
    write_order_notes(b, rep, os.path.join(OUT, "fab"))
    if publish:
        publish_pcb(b, rep, images=[os.path.join(OUT, "top.svg"),
                                    os.path.join(OUT, "bottom.svg")],
                    verbose=verbose)
    return b, rep


def _resolve_offboard(b):
    keep, dropped = [], []
    for owner, ref, net, why in b.unbound:
        if owner == "battery":
            keep.append((owner, ref, net, why))
        else:
            dropped.append(f"{owner}.{ref} (net {net}): not a pad of the "
                           f"contact board — this board is the pack's two "
                           f"terminals and the tail that leaves them")
    b.unbound = keep
    b.notes.append(
        f"_resolve_offboard(): {len(dropped)} netlist terminals resolved as "
        f"not-pads-of-this-board. The netlist is the WHOLE robot; this board "
        f"is a 45.800 x 5.100 mm contact strip.")



def write_order_notes(b, rep, outdir):
    """Put board.notes INTO the fab package.

    The fab README carries the rules, the footprints and the DRC verdict, but
    not the caveats the board author wrote — and a board gets emailed to a fab
    without the conversation that produced it. This file travels with the
    Gerbers.
    """
    p = os.path.join(outdir, "ORDER-NOTES.txt")
    os.makedirs(outdir, exist_ok=True)
    lines = [b.title, "=" * len(b.title), "",
             "These are the board author's own notes, shipped WITH the Gerbers",
             "because the fab README does not carry them. Read them before",
             "ordering; several are the reason a number is what it is.", "",
             f"DRC verdict: {rep.verdict}", ""]
    for i, n in enumerate(b.notes, 1):
        lines.append(f"{i}. {n}")
        lines.append("")
    open(p, "w", encoding="utf-8").write("\n".join(lines))
    # ...and into the zip, which is the file that actually gets emailed.
    z = os.path.join(outdir, f"{b.name}-fab.zip")
    if os.path.exists(z):
        import zipfile
        with zipfile.ZipFile(z, "a", zipfile.ZIP_DEFLATED) as zf:
            if "ORDER-NOTES.txt" not in zf.namelist():
                zf.write(p, "ORDER-NOTES.txt")
    return p


def main():
    if "--self-test" in sys.argv:
        print("--- self-test: off-board (expect a placement failure)")
        b, rep = build(self_test="off-board", publish=False, verbose=False)
        rows = [f for f in rep.findings
                if f.rule == "placement" and f.verdict != "PASS"]
        print(f"    {len(rows)} non-PASS placement findings")
        sys.exit(0 if rows else 1)
    b, rep = build(publish="--no-publish" not in sys.argv)
    print(b.describe())
    print(f"IPC-2221: {TRACK_W:.3f} mm on 1 oz external = {TRACK_A:.2f} A "
          f"at dT=10 degC")
    print("verdict:", rep.verdict)
    sys.exit({"PASS": 0, "FAIL": 2}.get(rep.verdict, 3))


if __name__ == "__main__":
    main()
