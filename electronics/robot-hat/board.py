#!/usr/bin/env python3
"""electronics/robot-hat/board.py — OUR Robot HAT, re-created as a ce-pcb board.

THIS IS NOT POLLEN'S BOARD. Pollen has published no PCB, no schematic and no
BOM for the RPI Robot HAT (docs/ELECTRONICS-AND-SOFTWARE.md §12 open question
4). This file re-creates a board that carries the HAT's PUBLISHED functions —
battery in, 5 V to the Radxa, the servo bus behind a half-duplex buffer, the
TLV320AIC3104 codec, the dormant BMI088, the Stemma J5, speaker and mic
connectors — on the Pi-Zero 65 x 30 mm outline the mesh and the MJCF carry.
Where Pollen's choice is unpublished, this file makes OUR choice and says so
out loud; the DRC's CANNOT DETERMINE rows are the honest remainder.

Connectivity comes from electronics/netlist.py (the rung-4 Design) through
board.bind() — the nets are never retyped here. Terminals of that Design that
are NOT on this board (the Radxa itself, the camera on its CSI ribbon) are
dropped from the unbound list by _resolve_offboard() with the reason recorded
in board.notes; the HAT's own provisions resolve to this board's connectors
the same way. Anything else left unbound stays a CANNOT DETERMINE finding.

Run:  python3 electronics/robot-hat/board.py            build, check, plot, fab
      python3 electronics/robot-hat/board.py --self-test  break checks on purpose
      python3 electronics/robot-hat/board.py --no-publish  skip the dashboard

OUR RECONSTRUCTION DECISIONS (each one a fact Pollen has not published):

  D1  5 V rail: a Pololu D30V30F5 buck module (U2) makes V5_HAT from the pack.
      Documented reference: part:buck-module-d30v30f5 (vendor's own spec page,
      'Output voltage: 5 V', 'Continuous output current: 3.4 A'). Pollen's
      regulator: CANNOT DETERMINE.
  D2  Servo bus VDD: VBAT passed straight to SERVO_V through R1 (0 ohm link),
      because the runtime reads the pack THROUGH the servos' own Present Input
      Voltage ('There is no fuel gauge and no ADC...', model.rs:99-113). The
      XL330 band is 'Input Voltage | 3.7 ~ 6.0 [V]' — docs §3.4 open question
      1 stands; the 0R makes the assumption a fitted, removable part.
  D3  Half-duplex: ROBOTIS' recommended circuit is a 74LVC2G241 with a
      TX_Enable (part:xl330-m288-t communication_circuit) — which robotd never
      drives ('no direction GPIO anywhere in the code', docs §3.1). So this
      board fits the DIRECTION-LESS variant: one 74LVC1G125 (U4) with A tied
      LOW and OE driven by UART2 TX. Function table (Nexperia 74LVC1G125
      Rev. 17.1, Table 4): 'L L -> L; L H -> H; H X -> Z' — TX low pulls DATA
      low through the buffer, TX high (idle) releases it to the 10 k pull-up.
      RX reads the line through R4 (0R). This TOPOLOGY is our proposal; the
      fitted transceiver stays CANNOT DETERMINE.
  D4  3.3 V rails: HAT_3V3 from 40-pin pin 1 and J5_3V3 from pin 17 — both
      '+3.3V' per [brief] p.6 / part:radxa-zero-3w header_40pin. Whether the
      real HAT does this or regulates its own: CANNOT DETERMINE.
  D5  1.8 V: NOT SOLVED. The codec's DVDD (1.525-1.95 V) lands on test point
      TP1. The real HAT must carry a 1.8 V regulator nobody has published;
      this board says so instead of inventing one. The codec will not run
      until a 1.8 V source is fitted to TP1.
  D6  Audio: speaker on HPLOUT/HPLCOM (pins 19/20 — the drivers TI specifies
      into 16 ohm; line-out is specified into 10 k), mic on MIC2R (pin 16).
      The community's 'Mic3R' does not exist on this chip (0 hits in SLAS510G).
      Amplifier and actual input: CANNOT DETERMINE.
  D7  J5 pin order GND/3V3/SDA/SCL follows the STEMMA QT / Qwiic convention
      the connector family names ('the connector on the end of a STEMMA QT /
      Qwiic cable', part:conn-jst-sh-1mm). Pollen's J5 pinout: CANNOT
      DETERMINE.
  D8  Servo connector: JST B3B-EH-A — the PCB header the XL330's own sheet
      names ('PCB Header | JST B3B-EH-A', part:xl330-m288-t connector). The
      name 'X3P' appears on no vendor page fetched; 1 GND, 2 VDD, 3 DATA
      ('Pinout | 1 GND 2 VDD 3 DATA').

Every dimension below quotes the document it came from. Decoupling values
(100 nF) are OUR practice where no source states one, and say so.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

# electronics/netlist.py builds the shelf union, puts ce-cad on sys.path and
# holds the ONE Design this board binds to. Loading it is the setup.
_spec = importlib.util.spec_from_file_location(
    "microduck_netlist", os.path.join(os.path.dirname(HERE), "netlist.py"))
_net = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_net)

from cecad.pcb import (Board, Footprint, Pad, custom, header,        # noqa: E402
                       mounting_hole, qfn, test_point)
from cecad.pcbcheck import check                                     # noqa: E402
from cecad.pcbfab import fab                                         # noqa: E402
from cecad.pcbview import plot, publish_pcb                          # noqa: E402

# ---------------------------------------------------------------------------
# PARAMETERS — every driving number once, each with its sentence
# ---------------------------------------------------------------------------
# Board outline and mounting: the Raspberry Pi Zero mechanical drawing
# RPI-ZERO-V1_2 (datasheets.raspberrypi.com/rpizero/raspberry-pi-zero-
# mechanical-drawing.pdf, fetched 2026-09-02): board 65 x 30, 'CORNER RADIUS =
# 3.0mm', hole pattern 58 x 23 at 3.5 from each edge, '4x M2.5 MOUNTING HOLES
# DRILLED TO 2.75 +/- 0.05mm'. The Microduck head carries exactly this
# footprint: the MJCF still uses the pcb__raspberry_pi_zero_2_w mesh
# (65.0 x 1.6 x 30.0), docs/ELECTRONICS-AND-SOFTWARE.md §2.
W, H = 65.0, 30.0
# CORNER was 3.0 (the Pi Zero drawing's 'CORNER RADIUS = 3.0mm'). MEASURED
# 2026-09-02 off POLLEN'S OWN HAT MESH and corrected to 3.5: see POLLEN_MESH
# below. Pollen's board is not a Pi Zero and its corner arc is centred on the
# mounting hole, not offset from it.
CORNER = 3.5
HOLE_INSET = 3.5
MOUNT = "M2.5"

# ---------------------------------------------------------------------------
# WHAT POLLEN'S OWN HAT MESH MEASURES — read 2026-09-02, lane D
# ---------------------------------------------------------------------------
# reference/pollen-microduck-rl/assets/elec_rpi_robot_hat_pcb.stl is Pollen's
# geometry for THIS board (placed by spec/mesh-placements.json in body
# jaw_soft at (26.940, 28.994, -51.900) mm, quat wxyz (0.7071, 0, 0,
# -0.7071)). Until this measurement the board's outline came from the
# Raspberry Pi Zero drawing by analogy. It no longer does.
#
# Method: binary-STL reader in plain python3; every triangle whose normal is
# +Z and whose vertices all lie on the top face (z = 0.840 mm) was taken, the
# edges that appear exactly once were walked into closed loops, and each loop
# was fitted for roundness. 62 boundary loops, no fitting tolerance loosened.
# Datum: the mesh's own origin, which sits on the first mounting hole.
#
#   outline ......... 65.000 x 30.000 mm, x -3.500..61.500, y -26.500..3.500
#   thickness ....... 0.840 - 0.000 = 0.840 mm   <-- NOT 1.6
#   corner arcs ..... R3.5000 (36 arc points fitted about the mounting-hole
#                     centre: r min 3.5000, r max 3.5001). An R3.0 arc offset
#                     0.5 mm inboard would fit the same corner to 3.04 with
#                     0.4 mm of scatter; it does not.
#   mounting holes .. 4 x dia 2.7000 at (0.000, 0.000), (58.000, 0.000),
#                     (0.000, -23.000), (58.000, -23.000)  ->  58 x 23 pattern,
#                     3.5 mm inset. Matches RPI-ZERO-V1_2's '4x M2.5 MOUNTING
#                     HOLES DRILLED TO 2.75 +/- 0.05mm'.
#   40-pin header ... 40 x dia 1.0200 at y = +/-1.270, x = 4.870 to 53.130 in
#                     2.540 steps (20 columns). Field centre x = 29.000 =
#                     board centre. So the header IS the full 2x20 and it IS
#                     centred, which is what J1_AT below already assumed.
#   header pegs ..... 2 x dia 2.0000 at (6.140, 0.000) and (51.860, 0.000),
#                     i.e. 1.270 inboard of the outer pin columns, on the
#                     header centre line. FUNCTION CANNOT DETERMINE: no
#                     2x20 socket this project has a drawing for has locating
#                     pegs there.
#   connectors ...... 14 x dia 0.9500 through-holes in FOUR groups, all on a
#                     2.500 mm pitch:
#                       x 43.850, y -23.000/-20.500/-18.000/-15.500  (4)
#                       x 48.650, y -23.000/-20.500/-18.000/-15.500  (4)
#                       x 53.500, y -17.450/-14.950/-12.450          (3)
#                       x 58.300, y -17.450/-14.950/-12.450          (3)
#                     The 2.500 pitch and the 0.950 hole are the JST XH/EH
#                     signature (eXH 'dia 1' at 2.5; eEH 'dia 0.9 +0.1/0' at
#                     2.5 — 0.950 is exactly between them), and the community
#                     HAT for the same robot says 'The connectors are XH
#                     2.54mm' (github.com/blublear/open-duck-mini-hat README,
#                     fetched 2026-09-02). What is NOT determinable is the
#                     4.800 mm spacing between the two columns of each pair:
#                     it is too tight for two same-side vertical JST headers
#                     (B*B-XH-A body 5.75 deep, B3B-EH-A housing 10.0 long),
#                     and it is not one dual-row part either: the nearest
#                     2.5 mm dual-row through-hole family is JST's JFA J2000
#                     (B08B-J21DK-GGXR, '8 Contact(s), 2.5 mm Pitch, 2 Row,
#                     Shrouded') and its ROW PITCH IS 2.5 mm, not 4.8 —
#                     searched 2026-09-02 across JST, Molex and distributor
#                     listings, nothing with a 2.5 x 4.8 grid came back.
#                     Best-supported reading: one fitted
#                     header per pair plus a duplicate solder-only row at
#                     4.800 mm, i.e. 'connector OR wires'. Second reading it
#                     beat: two headers on opposite FACES of the board.
#                     WHAT WOULD SETTLE IT: one photograph of a production
#                     HAT's connector side.
#   single hole ..... 1 x dia 1.0000 at (31.200, -11.900). CANNOT DETERMINE.
#
# THIS BOARD DOES NOT COPY THAT CONNECTOR PATTERN. Our connectors are placed
# from the netlist's needs and each one's own JST drawing (J2 XH-2 battery,
# J3 EH-3 bus, J5 SH-4 Stemma, J6/J7 PH speaker/mic), which is a different
# claim from "this is where Pollen put them". The measurement is recorded so
# the difference is visible, not hidden.
POLLEN_MESH = {
    "file": "reference/pollen-microduck-rl/assets/elec_rpi_robot_hat_pcb.stl",
    "read": "2026-09-02",
    "outline_mm": [65.000, 30.000],
    "thickness_mm": 0.840,
    "corner_r_mm": 3.5000,
    "mount_dia_mm": 2.7000,
    "mount_xy_mm": [[0.0, 0.0], [58.0, 0.0], [0.0, -23.0], [58.0, -23.0]],
    "header_dia_mm": 1.0200,
    "header_rows_y_mm": [1.270, -1.270],
    "header_x_mm": [4.870 + 2.54 * i for i in range(20)],
    "peg_dia_mm": 2.0000,
    "peg_xy_mm": [[6.140, 0.0], [51.860, 0.0]],
    "conn_dia_mm": 0.9500,
    "conn_pitch_mm": 2.500,
    "conn_column_gap_mm": 4.800,
    "conn_groups": [
        {"x": 43.850, "y": [-23.0, -20.5, -18.0, -15.5]},
        {"x": 48.650, "y": [-23.0, -20.5, -18.0, -15.5]},
        {"x": 53.500, "y": [-17.45, -14.95, -12.45]},
        {"x": 58.300, "y": [-17.45, -14.95, -12.45]},
    ],
    "lone_hole": {"dia_mm": 1.0000, "xy_mm": [31.200, -11.900]},
}

# 40-pin header: 2 x 20 on 2.54 mm. Centre on the '+' datum the RPI-ZERO-V1_2
# drawing marks 29 mm from the left hole centre on the 3.5 mm hole line:
# x = 3.5 + 29 = 32.5 (board centre), y = 30 - 3.5 = 26.5. The drawing does
# not dimension the header outline; centring the pin field on that datum with
# the odd row inboard is OUR reading of it, stated here.
J1_AT = (32.5, 26.5)

# Codec package: TI SLAS510G p.1 'TLV320AIC3104 | VQFN (32) | 5.00 mm x
# 5.00 mm'; outline RHB0032E (4223442/B 08/2019, PDF p.100-101): body
# 4.9-5.1 sq, '28X 0.5' pitch, lead '32X 0.5/0.3' long x '32X 0.3/0.2' wide,
# 'EXPOSED THERMAL PAD ... 3.45 +/- 0.1'.
AIC_CITE = ("TI SLAS510G RHB0032E package outline (4223442/B 08/2019), PDF "
            "p.100-101: body 4.9-5.1 sq, pitch 28X 0.5, lead 0.3-0.5 x "
            "0.2-0.3, exposed pad 3.45+/-0.1; ce-parts/tlv320aic3104/"
            "datasheet.pdf sha256 17ce38b2...")

# TLV320AIC3104 pin map, Table 7-1 'Pin Functions' p.5-6 of SLAS510G, read
# 2026-09-02 (extends the shelf record, which had not transcribed BCLK/DIN/
# DOUT): 1 MCLK, 2 BCLK, 3 WCLK, 4 DIN, 5 DOUT, 6 DVSS, 7 IOVDD, 8 SCL,
# 9 SDA, 10-14 analog inputs, 15 MICBIAS, 16 MIC2R/LINE2R, 17 AVSS1,
# 18 DRVDD, 19 HPLOUT, 20 HPLCOM, 21 DRVSS, 22 HPRCOM, 23 HPROUT, 24 DRVDD,
# 25 AVDD, 26 AVSS2, 27 LEFT_LOP, 28 LEFT_LOM, 29 RIGHT_LOP, 30 RIGHT_LOM,
# 31 RESET, 32 DVDD. 'NOTE: Connect device thermal pad to DRVSS.'
AIC_PINS = {"MCLK": "1", "BCLK": "2", "WCLK": "3", "DIN": "4", "DOUT": "5",
            "GND": "6", "IOVDD": "7", "SCL": "8", "SDA": "9",
            "AVDD": "25", "DVDD": "32"}

# BMI088: landing pattern is Bosch's OWN recommendation — BST-BMI088-DS000-19
# Rev 1.9, §8.2 Fig. 11 (p.55): lands 0.675 x 0.25 at 0.5 pitch, pattern
# outer extents 3.0 x 4.5, two columns of 7 (pins 1-7 right, 9-15 left) plus
# pin 16 top-centre and pin 8 bottom-centre, rotated 90 deg. Column centres
# are DERIVED: (3.0 - 0.675)/2 = 1.1625 from centre; row 16/8 centres
# (4.5 - 0.675)/2 = 1.9125. The figure's 0.925 and 1.675 callouts were not
# resolved to this construction and are named in the provenance.
BMI_CITE = ("Bosch BST-BMI088-DS000-19 Rev 1.9 §8.2 Fig. 11 'Landing pattern "
            "recommendation' (p.55): lands 0.675 x 0.25, pitch 0.5, extents "
            "3.0 x 4.5; ce-parts/bmi088/datasheet.pdf sha256 53ab734d...")

# BMI088 pin table (Table 14 p.52-53, I2C-mode column): 1 INT2(DNC), 2 NC->
# GND, 3 VDD, 4 GNDA->GND, 5 CSB2->'DNC (float)', 6 GNDIO->GND, 7 PS->VDDIO
# ('GND = SPI, VDDIO = I2C'), 8 SCL, 9 SDA, 10 SDO2->'GND for default addr.',
# 11 VDDIO, 12 INT3(DNC), 13 INT4(DNC), 14 CSB1->'VDDIO or DNC (float)',
# 15 SDO1->'GND for default addr.', 16 INT1(DNC). '* If INT are not used, do
# not connect them (DNC)!'
BMI_PINS = {"GND": "4", "VDD": "3", "VDDIO": "11", "SDA": "9", "SCL": "8"}

# 74LVC1G125 GV = SOT753 (SC-74A). Nexperia 'SOT753 package information'
# 31 May 2022: 'Footprint dimensions (mm) 3.45 x 3.3', pitch 0.95; Fig. 2
# reflow footprint: solder lands 0.55 wide (paste 0.45), outer extent 3.45,
# inner 1.95 -> land length (3.45-1.95)/2 = 0.75, row centres +/-1.35.
# Pinning (74LVC1G125 Rev 17.1 §6.1 GV package): 1 OE, 2 A, 3 GND bottom row;
# 4 Y, 5 VCC top row. Function table (Table 4): 'L L -> L; L H -> H; H X -> Z'.
LVC_CITE = ("Nexperia SOT753 package information (31 May 2022) Fig. 2 reflow "
            "footprint: lands 0.55 wide, pitch 0.95, outer 3.45 / inner 1.95 "
            "(length and row centres derived: 0.75, +/-1.35); pin order "
            "74LVC1G125 Rev 17.1 §6.2 Table 3")

# Pololu D30V30F5 module: dimension drawing (doc:buck-module-d30v30f5/docs/
# d30v30fx-dimensions.pdf): board 17.8 x 20.3 [700 x 800 mil], '6x dia 1.02
# [40]' holes on the 2.54 grid, 1.27 from the edges, drill location tolerance
# +/-0.1; pinout photo 0J12273 (vendor caption 'Step-Down Voltage Regulator
# D30V30Fx pinout.'): along the pin edge PG (inset), EN, VIN, GND, GND, VOUT.
BUCK_CITE = ("Pololu D30V30Fx dimension drawing (docs/d30v30fx-dimensions.pdf"
             ", 20 October 2023, dev code reg32a): 17.8 x 20.3 board, 6x "
             "dia1.02 holes on the 2.54/1.27 grid; pin names/order from the "
             "vendor pinout photo 0J12273")

# JST PCB layouts, each from JST's own datasheet (jst-mfg.com, fetched
# 2026-09-02): eEH.pdf 'PC board layout': holes dia 0.9 +0.1/0 at 2.5+/-0.05;
# eXH.pdf: '2 circuits: dia 1' at 2.5; ePH.pdf: dia 0.7 +0.1/0 at 2+/-0.05;
# eSH.pdf side entry: signal lands 0.6+/-0.05 at 1.0+/-0.05, anchors 1.2+/-
# 0.1, 'Dimension A' for 4 circuits = 3.0 ('4 | BM04B-SRSS-TB | SM04B-SRSS-TB
# | 3.0 | 6.0').

I2C_PULLUP = "10k"       # 'one 10 kOhm pull-up pair R12/R13' — i2c3-pihat.dts
DATA_PULLUP = "10k"      # ROBOTIS TTL circuit: '10 kOhm pull-ups to 3.3V on
                         # RXD and on Data' (part:xl330-m288-t
                         # communication_circuit)
DECOUPLE = "100n"        # OUR practice — no fetched source states the HAT's
                         # decoupling values; the ROBOTIS circuit's '0.1uF' on
                         # the buffer VCC is the one cited figure.


# ---------------------------------------------------------------------------
# footprints that are not in packages.json — every figure cited above
# ---------------------------------------------------------------------------
def fp_bmi088():
    pads = []
    for i in range(7):                       # pins 1..7, right column, top->bottom
        pads.append(Pad(str(i + 1), 1.1625, 1.5 - 0.5 * i, 0.675, 0.25))
    pads.append(Pad("8", 0.0, -1.9125, 0.25, 0.675))       # bottom centre
    for i in range(7):                       # pins 9..15, left column, bottom->top
        pads.append(Pad(str(9 + i), -1.1625, -1.5 + 0.5 * i, 0.675, 0.25))
    pads.append(Pad("16", 0.0, 1.9125, 0.25, 0.675))       # top centre
    return custom(
        "bmi088-lga16", pads, courtyard=(4.0, 5.5), height=0.95,
        why=BMI_CITE + ". Figure callouts 0.925 and 1.675 were not resolved "
        "into this construction (columns derive from the 3.0/4.5 extents and "
        "the 0.675 land length); Bosch also recommends 'A wiring no-go area "
        "in the top layer of the PCB below the sensor' — noted, not enforced, "
        "because pins 8 and 16 route through it.")


def fp_sot753():
    pads = [Pad("1", -0.95, -1.35, 0.55, 0.75),
            Pad("2", 0.0, -1.35, 0.55, 0.75),
            Pad("3", 0.95, -1.35, 0.55, 0.75),
            Pad("4", 0.95, 1.35, 0.55, 0.75),
            Pad("5", -0.95, 1.35, 0.55, 0.75)]
    return custom("sot753", pads, courtyard=(3.6, 3.95), height=1.1,
                  why=LVC_CITE)


def fp_buck():
    # Module 17.8 (x) x 20.3 (y), pins along its left edge; origin = centre.
    xs = -17.8 / 2 + 1.27
    y0 = -20.3 / 2 + 1.27
    names = ["VOUT", "GND2", "GND1", "VIN", "EN"]           # bottom -> top
    pads = [Pad(n, xs, y0 + 2.54 * i, 1.8, 1.8, shape="round",
                layer="*.Cu", drill=1.02) for i, n in enumerate(names)]
    pads.append(Pad("PG", xs + 1.27, y0 + 2.54 * 4 + 2.54, 1.8, 1.8,
                    shape="round", layer="*.Cu", drill=1.02,
                    note="PG hole 1.27 inboard / 2.54 above EN — the drawing's "
                         "1.27/2.54 callouts read with the pinout photo"))
    return custom("pololu-d30v30f5", pads, courtyard=(18.4, 20.9), height=7.7,
                  why=BUCK_CITE + ". Pad 1.8 mm over the 1.02 drill (0.39 "
                  "ring); the module's two dia 2.18 M2 holes are not "
                  "reproduced — it hangs on its six pins here.")


def fp_jst_th(slug, n, pitch, drill, cite, body_w, body_d):
    pads = [Pad(str(i + 1), (i - (n - 1) / 2.0) * pitch, 0.0,
                drill + 0.6, drill + 0.6,
                shape="rect" if i == 0 else "round",
                layer="*.Cu", drill=drill) for i in range(n)]
    return custom(slug, pads, courtyard=(body_w + 0.5, body_d + 0.5),
                  height=7.0, why=cite)


def fp_jst_sh4():
    # SM04B-SRSS-TB side entry, top view: 4 signal lands at 1.0 pitch plus
    # two anchor lands. A (signal span over centres) = 3.0 for 4 circuits.
    pads = [Pad(str(i + 1), -1.5 + 1.0 * i, 0.0, 0.6, 1.2) for i in range(4)]
    for j, x in ((1, -2.8), (2, 2.8)):
        pads.append(Pad(f"MP{j}", x, 0.0, 1.2, 1.8,
                        note="anchor / strain-relief land"))
    return custom(
        "jst-sh4-smt-side", pads, courtyard=(7.4, 4.7), height=4.2,
        why="JST eSH.pdf (jst-mfg.com, fetched 2026-09-02) 'PC board layout', "
            "side entry: signal lands 0.6+/-0.05 at 1.0+/-0.05 pitch, anchor "
            "lands 1.2+/-0.1, land length 1.2+/-0.1; 'Dimension A' = 3.0 for "
            "4 circuits ('4 | BM04B-SRSS-TB | SM04B-SRSS-TB | 3.0 | 6.0'). "
            "The 5.55/4.0/1.8 callouts of the figure were NOT fully resolved "
            "— anchor positions here are constructed at 0.7 clear of the "
            "outer signal land. UNCONFIRMED on purpose; the DRC says so.")


# ---------------------------------------------------------------------------
# the board
# ---------------------------------------------------------------------------
OFF_BOARD = {
    "host": "the Radxa Zero 3W itself — it plugs onto J1; its pins are the "
            "other side of the 40-pin connector, not pads of this board",
    "camera": "the IMX219 module rides the Radxa's own 22-pin CSI connector "
              "(docs §5); no CSI signal touches the HAT",
}


def build(self_test=None, publish=True, verbose=True):
    d = _net.electrical_design()

    b = Board("microduck_robot_hat", W, H, corner_r=CORNER,
              rules="jlcpcb_2l_standard", stackup="jlcpcb-2layer-1.6mm",
              title="Microduck Robot HAT (reconstruction)",
              origin_note="origin = board lower-left, mm, top view; outline "
                          "and holes from RPI-ZERO-V1_2")

    # -- parts -------------------------------------------------------------
    b.add("J1", header(20, rows=2,
                       names=[str(2 * i + 1) for i in range(20)]
                             + [str(2 * i + 2) for i in range(20)]),
          value="40-pin GPIO", at=J1_AT, rot=90,
          note="2x20 on 2.54; odd row inboard, pin 1 at the x~8.4 end — OUR "
               "reading of the RPI-ZERO-V1_2 '+' datum (29 from the left "
               "hole on the 3.5 line)")
    b.add("U1", qfn(32, body=5.0, pitch=0.5, term_len=0.4, term_width=0.25,
                    ep=3.45, ep_vias=2, ep_via_pad=0.80, cite=AIC_CITE),
          value="TLV320AIC3104", at=(11.0, 15.0))
    b.add("U2", fp_buck(), value="Pololu D30V30F5", at=(49.6, 12.0),
          note="reconstruction decision D1 — the published-fact HAT names no "
               "regulator")
    b.add("U3", fp_bmi088(), value="BMI088 (dormant)", at=(19.0, 15.0),
          note="'dormant BMI088 0x19/0x68', 'unused but still connected' "
               "(i2c3-pihat.dts:11,31) — footprint fitted, straps for I2C "
               "0x19/0x68")
    b.add("U4", fp_sot753(), value="74LVC1G125", at=(38.5, 14.0),
          note="reconstruction decision D3 — direction-less half-duplex")
    b.add("J2", fp_jst_th("jst-b2b-xh-a", 2, 2.5, 1.0,
                          "JST eXH.pdf PC board layout: '2 circuits: dia 1' "
                          "+0.05, pitch 2.5+/-0.05; B2B-XH-A dims 2.5/7.4",
                          7.4, 5.75),
          value="VBAT in (B2B-XH-A)", at=(10.2, 4.2))
    b.add("J3", fp_jst_th("jst-b3b-eh-a", 3, 2.5, 0.9,
                          "JST eEH.pdf PC board layout: holes dia 0.9 +0.1/0 "
                          "at 2.5+/-0.05; B3B-EH-A dims 5.0/10.0; XL330 "
                          "'PCB Header | JST B3B-EH-A'",
                          10.0, 3.8),
          value="DXL bus (B3B-EH-A)", at=(28.35, 3.6),
          note="'Pinout | 1 GND 2 VDD 3 DATA' — the whole 16-device bus "
               "daisy-chains from this one header")
    b.add("J5", fp_jst_sh4(), value="Stemma J5 (SM04B-SRSS-TB)",
          at=(4.5, 15.0), rot=90,
          note="'Stemma J5' (i2c3-pihat.dts:10); pin order GND/3V3/SDA/SCL "
               "is the Qwiic convention — decision D7")
    b.add("J6", fp_jst_th("jst-b2b-ph-k-s", 2, 2.0, 0.7,
                          "JST ePH.pdf PC board layout: dia 0.7 +0.1/0 at "
                          "2+/-0.05; B2B-PH-K-S dims 2.0/5.9",
                          5.9, 4.5),
          value="speaker (B2B-PH-K-S)", at=(37.0, 3.6))
    b.add("J7", fp_jst_th("jst-b3b-ph-k-s", 3, 2.0, 0.7,
                          "JST ePH.pdf PC board layout: dia 0.7 +0.1/0 at "
                          "2+/-0.05; B3B-PH-K-S dims 4.0/7.9",
                          7.9, 4.5),
          value="mic (B3B-PH-K-S)", at=(18.65, 3.6),
          note="pin order GND/MIC/BIAS is OUR choice — the transducer and "
               "its wiring are CANNOT DETERMINE (docs §12 item 11)")
    b.add("R1", "1206", value="0R link VBAT->SERVO_V", at=(24.0, 8.5),
          note="decision D2 — the pass-through the runtime implies, fitted "
               "as a removable part")
    b.add("R2", "0603", value=DATA_PULLUP, at=(31.5, 11.5), rot=90,
          note="DATA pull-up: ROBOTIS TTL circuit '10 kOhm pull-ups to 3.3V "
               "... on Data'")
    b.add("R4", "0603", value="0R DATA->RX", at=(39.0, 9.0), rot=90,
          note="decision D3 — RX reads the bus line directly; 0R keeps "
               "dxl/DATA and uart2/RX the two nets the netlist draws")
    b.add("R12", "0603", value=I2C_PULLUP, at=(26.0, 21.5), rot=90,
          note="'one 10 kOhm pull-up pair R12/R13' (i2c3-pihat.dts via docs "
               "§11) — designators kept")
    b.add("R13", "0603", value=I2C_PULLUP, at=(29.0, 21.5), rot=90)
    b.add("C1", "0603", value="100n SERVO_V", at=(29.0, 8.5),
          note="ROBOTIS TTL circuit: 'DXL_PWR with a bulk + 0.1uF'")
    b.add("C2", "1210", value="bulk (value CANNOT DETERMINE)", at=(33.5, 8.2),
          note="the reference circuit names a bulk capacitor and no value; "
               "fitted as a 1210 site, value deliberately unstated")
    b.add("C3", "0603", value="100n U4 VCC", at=(35.5, 14.0), rot=90,
          note="ROBOTIS TTL circuit: 'VCC pin 8 = 3.3V with 0.1uF' — same "
               "practice on our buffer")
    b.add("C4", "0603", value=DECOUPLE, at=(11.0, 10.5))
    b.add("C5", "0603", value=DECOUPLE, at=(15.0, 11.5), rot=90)
    b.add("C6", "0603", value=DECOUPLE, at=(7.6, 9.5))
    b.add("C7", "0603", value=DECOUPLE, at=(16.5, 19.5))
    b.add("C8", "0603", value=DECOUPLE, at=(22.0, 19.5))
    b.add("TP1", test_point(1.5), value="HAT_1V8 (unsourced)", at=(11.0, 21.5),
          note="decision D5 — the codec's 1.525-1.95 V DVDD has NO published "
               "source; it ends on this pad, on purpose")
    b.mount_holes(MOUNT, inset=HOLE_INSET)

    if self_test == "off-board":
        b.place("J3", at=(63.0, 3.6))        # hangs over the right edge

    # -- connectivity FROM the netlist ---------------------------------------
    refs = {"codec": "U1", "bmi088": "U3", "bmi088.gyro": "U3", "tof": "J5",
            "battery": "J2", "speaker": "J6", "mic": "J7", "hat": "J1",
            "imu200": "J3"}
    for sid, _j, _b, _r in _net.SERVOS:
        refs[f"id{sid}"] = "J3"
    pins = {
        "U1": AIC_PINS,
        "U3": BMI_PINS,
        "J1": {"I2C3_SDA": "3", "I2C3_SCL": "5", "UART2_TX": "8",
               "UART2_RX": "10", "I2S3_SCLK": "12", "MCLK": "13",
               "I2S3_LRCK": "35", "I2S3_SDI": "38", "I2S3_SDO": "40",
               "GND": "6", "V5_OUT": "2"},
        "J2": {"BAT+": "1", "BAT-": "2"},
        "J3": {"GND": "1", "VDD": "2", "DATA": "3"},
        "J5": {"GND": "1", "3V3": "2", "SDA": "3", "SCL": "4"},
        "J6": {"SPK+": "1", "SPK-": "2"},
        "J7": {"GND": "1", "MIC": "2", "BIAS": "3"},
    }
    if self_test == "unbound":
        del pins["J2"]
    b.bind(d, refs=refs, pins=pins, strict=False)
    _resolve_offboard(b)

    # -- board-only attaches: each one a decision documented above -----------
    # Radxa supply/ground pins beyond the one bind() placed: [brief] §5.1
    # '5V Power from the GPIO PIN 2 & 4'; GND on pins 6, 9, 14, 20, 25, 30,
    # 34, 39 (part:radxa-zero-3w header_40pin / requires.GND).
    b.attach("V5_HAT", "J1.4")
    for p in (9, 14, 20, 25, 30, 34, 39):
        b.attach("GND", f"J1.{p}")
    # D4: 3.3 V from the Radxa's own pins 1 and 17 ('1: +3.3V', '17: +3.3V',
    # part:radxa-zero-3w header_40pin).
    b.attach("HAT_3V3", "J1.1")
    b.attach("J5_3V3", "J1.17")
    # D1: the buck.
    b.attach("VBAT", "U2.VIN")
    b.attach("GND", "U2.GND1")
    b.attach("GND", "U2.GND2")
    b.attach("V5_HAT", "U2.VOUT")
    b.no_connect("U2.EN", why="'enabled by default' via the module's own "
                 "100k pull-up to VIN (part:buck-module-d30v30f5 "
                 "uncertainties[5])")
    b.no_connect("U2.PG", why="power-good left unread — the record calls "
                 "this 'a live design choice nobody has made'; open is "
                 "electrically safe")
    # D2: the pack pass-through.
    b.attach("VBAT", "R1.1")
    b.attach("SERVO_V", "R1.2")
    # D3: the direction-less buffer. 74LVC1G125 §6.2: 1 OE, 2 A, 3 GND, 4 Y,
    # 5 VCC.
    b.attach("uart2/TX", "U4.1")
    b.attach("GND", "U4.2")
    b.attach("GND", "U4.3")
    b.attach("dxl/DATA", "U4.4")
    b.attach("HAT_3V3", "U4.5")
    b.attach("dxl/DATA", "R4.1")
    b.attach("uart2/RX", "R4.2")
    b.attach("dxl/DATA", "R2.1")
    b.attach("HAT_3V3", "R2.2")
    # I2C pull-ups R12/R13.
    b.attach("i2c3/SDA", "R12.1")
    b.attach("HAT_3V3", "R12.2")
    b.attach("i2c3/SCL", "R13.1")
    b.attach("HAT_3V3", "R13.2")
    # Codec pins bind() had no terminal for — Table 7-1 p.5-6:
    b.attach("GND", "U1.17")                 # AVSS1
    b.attach("GND", "U1.21")                 # DRVSS
    b.attach("GND", "U1.26")                 # AVSS2
    b.attach("GND", "U1.EP")                 # 'Connect device thermal pad to DRVSS.'
    b.attach("HAT_3V3", "U1.18")             # DRVDD — one band with AVDD, §8.3
    b.attach("HAT_3V3", "U1.24")             # DRVDD
    b.attach("MICBIAS", "U1.15")             # 'MICBIAS | 15 | O'
    b.attach("MIC_IN", "U1.16")              # D6: MIC2R/LINE2R, pin 16
    b.attach("SPK_P", "U1.19")               # D6: HPLOUT
    b.attach("SPK_N", "U1.20")               # D6: HPLCOM
    b.attach("HAT_1V8", "TP1.1")             # D5
    # decoupling
    b.attach("HAT_3V3", "C4.1"); b.attach("GND", "C4.2")     # AVDD/DRVDD
    b.attach("HAT_1V8", "C5.1"); b.attach("GND", "C5.2")     # DVDD
    b.attach("HAT_3V3", "C6.1"); b.attach("GND", "C6.2")     # IOVDD
    b.attach("HAT_3V3", "C7.1"); b.attach("GND", "C7.2")     # BMI088 VDD
    b.attach("HAT_3V3", "C8.1"); b.attach("GND", "C8.2")     # BMI088 VDDIO
    b.attach("HAT_3V3", "C3.1"); b.attach("GND", "C3.2")     # U4 VCC
    b.attach("SERVO_V", "C1.1"); b.attach("GND", "C1.2")
    b.attach("SERVO_V", "C2.1"); b.attach("GND", "C2.2")
    # BMI088 straps, Table 14 I2C-mode column (quotes in the parameter block):
    b.attach("GND", "U3.2")                  # 'NC ... GND' (I2C column)
    b.attach("GND", "U3.6")                  # GNDIO
    b.attach("HAT_3V3", "U3.7")              # PS = VDDIO -> I2C
    b.attach("GND", "U3.10")                 # SDO2 'GND for default addr.' (0x68)
    b.attach("HAT_3V3", "U3.14")             # CSB1 'VDDIO or DNC' — tied
    b.attach("GND", "U3.15")                 # SDO1 'GND for default addr.' (0x19)
    b.no_connect("U3.1", "U3.12", "U3.13", "U3.16",
                 why="'* If INT are not used, do not connect them (DNC)!' — "
                     "Table 14; nothing in the published runtime reads the "
                     "dormant BMI088's interrupts")
    b.no_connect("U3.5", why="CSB2 is 'DNC (float)' in I2C mode — Table 14")
    # Codec inputs/outputs this reconstruction does not use:
    b.no_connect("U1.10", "U1.11", "U1.12", "U1.13", "U1.14",
                 why="MIC1L/MIC1R/MIC2L input pins — D6 puts the one mic on "
                     "MIC2R (pin 16); which input Pollen uses is CANNOT "
                     "DETERMINE ('Mic3R' exists nowhere in SLAS510G)")
    b.no_connect("U1.22", "U1.23", "U1.27", "U1.28", "U1.29", "U1.30",
                 why="right-channel HP outputs and both line-output pairs — "
                     "decision D6 drives the one mono speaker (35x25x7, docs "
                     "§7) from HPLOUT/HPLCOM, the drivers TI specifies into "
                     "16 ohm; line-out is specified into 10 k")
    # RESET (pin 31, 'RESET | 31 | I | Reset', Table 7-1): tied permanently
    # high on HAT_3V3 — OUR choice; the HAT's reset wiring is unpublished
    # (no reset-gpio appears in aic3104-i2c3.dts).
    b.attach("HAT_3V3", "U1.31")
    # J5 anchors:
    b.no_connect("J5.MP1", "J5.MP2",
                 why="anchor / strain-relief lands; the eSH figure draws no "
                     "signal on them")
    # Header positions the HAT passes through and uses nothing on:
    for p in (7, 11, 15, 16, 18, 19, 21, 22, 23, 24, 26, 27, 28, 29,
              31, 32, 33, 36, 37):
        b.no_connect(f"J1.{p}",
                     why="40-pin position the HAT mechanically passes through "
                         "and uses no signal on ([brief] p.6 table; nothing "
                         "in the overlays or robotd touches it)")

    b.notes.append(
        "POWER PATH: VBAT, SERVO_V and V5_HAT are routed at 0.800 mm on 1 oz "
        "outer copper, which IPC-2221 §6.2 puts at 2.03 A for a 10 degC rise "
        "and 3.05 A at 20 degC. They used to be 0.400 mm = 1.29 A. The "
        "DEMAND is CANNOT DETERMINE: the XL330's published figures are 17 mA "
        "standby and 1.47 A stall at 5 V with no running current, so the "
        "16-device bus total has no number behind it, and wiring/CABLES.md's "
        "own 1 A-per-moving-servo worst case is stated there as an "
        "assumption. 0.800 mm is the widest track this board's lattice can "
        "thread between 2.54 mm header pins — measured on this board, run 2: "
        "1.0 mm gave a 1.56 mm lattice that could not thread the bottom "
        "connector row.")
    b.notes.append(
        "POLLEN'S OWN HAT MESH WAS MEASURED (2026-09-02) and this board's "
        "outline follows it: 65.000 x 30.000 mm, corner radius 3.5000 mm "
        "fitted to 36 arc points about the mounting-hole centre (r min "
        "3.5000, r max 3.5001) — NOT the Raspberry Pi Zero drawing's 3.0 mm, "
        "which was what this file used until today. The mesh also carries the "
        "full 2x20 header (40 x dia 1.0200 at y +/-1.270, x 4.870..53.130 on "
        "2.540, field centre 29.000 = board centre), 4 x dia 2.7000 mounting "
        "holes on the 58 x 23 pattern, 2 x dia 2.0000 pegs at (6.140, 0.000) "
        "and (51.860, 0.000), 14 x dia 0.9500 connector holes on a 2.500 mm "
        "pitch in four groups, and one dia 1.0000 hole at (31.200, -11.900). "
        "The mesh's thickness is 0.840 mm; this board is built on the 1.6 mm "
        "stackup, because 0.840 is not a thickness JLCPCB lists ('0.4/0.6/"
        "0.8/1.0/1.2/1.6/2.0 mm') and a 0.84 mm visual mesh is more likely a "
        "modelling simplification than a fab order. THE CONNECTOR HOLES ARE "
        "NOT COPIED HERE — see POLLEN_MESH in this file for the full table "
        "and for what about them is CANNOT DETERMINE.")
    b.text("microduck robot-hat", (32.5, 19.5), size=1.2)
    b.text("OUR RECONSTRUCTION - NOT POLLEN'S BOARD", (32.5, 17.5), size=1.0)

    # -- the person's two statements: land patterns read against documents ---
    b.confirm("U1", "TI SLAS510G RHB0032E package outline read (PDF p.100-101"
              ", 4223442/B): body 4.9-5.1, pitch 0.5, lead 0.3-0.5 x 0.2-0.3,"
              " EP 3.45+/-0.1 — the qfn() arguments are those figures")
    b.confirm("U2", "Pololu D30V30Fx dimension drawing (20 Oct 2023, reg32a) "
              "read: 6x dia1.02 on the 2.54/1.27 grid, board 17.8 x 20.3; pin"
              " order from the vendor's own pinout photo 0J12273")
    b.confirm("U3", "Bosch BST-BMI088-DS000-19 Fig. 11 read: the vendor's own"
              " recommended landing pattern (0.675 x 0.25 lands, 0.5 pitch, "
              "3.0 x 4.5 extents); two callouts (0.925/1.675) unresolved and "
              "named in the footprint provenance")
    b.confirm("U4", "Nexperia SOT753 package information Fig. 2 reflow "
              "footprint read: 0.55 lands, 0.95 pitch, 3.45/1.95 extents; "
              "pin order 74LVC1G125 Rev 17.1 Table 3")
    b.confirm("J2", "JST eXH.pdf PC board layout read: '2 circuits: dia 1', "
              "pitch 2.5+/-0.05")
    b.confirm("J3", "JST eEH.pdf PC board layout read: dia 0.9 +0.1/0 at "
              "2.5+/-0.05")
    b.confirm("J6", "JST ePH.pdf PC board layout read: dia 0.7 +0.1/0 at "
              "2+/-0.05")
    b.confirm("J7", "JST ePH.pdf PC board layout read: dia 0.7 +0.1/0 at "
              "2+/-0.05")
    # J5 is left UNCONFIRMED on purpose — the eSH side-entry figure's
    # 5.55/4.0/1.8 callouts were not resolved; the DRC row is the record.

    # -- copper --------------------------------------------------------------
    # Route FIRST with both layers open, pour LAST: a zone declared before
    # autoroute() removes its layer from routing_layers() and the board
    # becomes single-layer — measured on this board: 42/84 routed with the
    # pour first, fully routed without it. The pour flows around the routed
    # B.Cu tracks; LOOK AT THE PLOT for sliced islands (the check is
    # optimistic about pours and says so).
    # Strategy, measured across three routing attempts on this board:
    #   run 1  pour declared first -> B.Cu became a plane, single-layer
    #          routing, 42/84.
    #   run 2  1.0 mm power tracks -> a 1.56 mm lattice that cannot thread
    #          the bottom connector row; GND's 34 pads starved the router.
    #   run 3  GND autorouted last -> 27 of its joins still open.
    # So: GND never meets the router. Every surface GND pad is BONDED to the
    # back layer by an explicit stub + via below, the through-hole GND pins
    # reach B.Cu through their own barrels, and the pour poured LAST unifies
    # them. The islands check treats a pour optimistically (its own note says
    # so) — the bottom plot is the verification, and the rails pass keeps
    # via_cost moderate so B.Cu stays mostly plane.
    # U1's four ground pins bond STRAIGHT INTO the exposed pad ('Connect
    # device thermal pad to DRVSS.' — SLAS510G Figure 7-1 note), whose 2x2
    # thermal vias reach the plane; no via fence around the QFN, so every
    # signal lane stays open. A fifth-run lesson: a ring of 0.8 mm stub vias
    # 1.1 mm off the package walled the part in and 18 of 19 HAT_3V3 joins
    # failed; tracks into the EP cost nothing.
    for pad, ex, ey in [("6", -1.6, -0.75), ("17", 1.6, -1.75),
                        ("21", 1.6, 0.25), ("26", 1.25, 1.6)]:
        c = b.component("U1")
        x, y = c.pad_xy(c.fp.pad(pad))
        b.track("GND", [(x, y), (c.x + ex, c.y + ey)], width=0.2)
    # Surface GND pads elsewhere bond to the back plane with a stub + via.
    for ref, pad, dx, dy in [
            ("U4", "2", 0, -1.0),
            ("C1", "2", 0.9, 0), ("C2", "2", 1.0, 0), ("C3", "2", 0, 1.15),
            ("C4", "2", 0, -1.2), ("C5", "2", 1.1, 0), ("C6", "2", 0, -1.1),
            ("C7", "2", 0, 1.1), ("C8", "2", 0, 1.1)]:
        c = b.component(ref)
        x, y = c.pad_xy(c.fp.pad(pad))
        b.track("GND", [(x, y), (x + dx, y + dy)], width=0.25)
        b.via("GND", (x + dx, y + dy))
    # U4.3 (GND) bridges to its neighbour pad 2 on the surface.
    c = b.component("U4")
    x2, y2 = c.pad_xy(c.fp.pad("2")); x3, y3 = c.pad_xy(c.fp.pad("3"))
    b.track("GND", [(x2, y2), (x3, y3)], width=0.25)
    if self_test:
        # The self-test breaks placement/binding and reads the check —
        # routing at these pass budgets would cost tens of minutes and
        # proves nothing about the break.
        rep = check(b, verbose=verbose)
        return b, rep
    # Two hand-laid spines, claimed before the router runs:
    #  - HAT_3V3 rides B.Cu from J1 pin 1 (a through-hole pad reaches the
    #    back layer through its own barrel) along y=23.3, under the corridor
    #    south of the header, so eighteen 3.3 V joins become short hops.
    #    One deliberate cost: it slices the eventual GND pour along that
    #    line; the pour reconnects around x>41 — checked on the bottom plot.
    #  - i2s3/DIN goes the long way: J1 pin 38 escapes upward into the lane
    #    between the header's outer row and the board edge, west along
    #    y=29.0, down the west flank of the header, then to codec DIN
    #    (pin 4). The router failed this join twice ('no legal path');
    #    the lane is real and this claims it.
    c1 = b.component("J1")
    b.track("HAT_3V3", [c1.pad_xy(c1.fp.pad("1")),
                        (c1.pad_xy(c1.fp.pad("1"))[0], 23.3),
                        (41.0, 23.3)], width=0.4, layer="B.Cu")
    # MEASURED DEFECT, fixed 2026-09-02 (lane D): this spine used to start at
    # J1 pad 38 while carrying net i2s3/DIN. Pad 38 is I2S3_SDI = i2s3/DOUT
    # (see `pins` above); the DIN pad is 40. The DRC caught it as three
    # 0.000 mm clearance failures — 'track i2s3/DIN on F.Cu / pad J1.38' plus
    # two codec pads the old diagonal approach cut across (U1.2 BCLK, U1.3
    # WCLK). The track now leaves the RIGHT pad and comes into the codec's
    # pin 4 horizontally, along pin 4's own y, so it never crosses 2 or 3.
    p40 = c1.pad_xy(c1.fp.pad("40"))
    u1 = b.component("U1")
    din = u1.pad_xy(u1.fp.pad("4"))
    b.track("i2s3/DIN", [p40, (p40[0], 29.0), (6.3, 29.0), (6.3, din[1]),
                         din], width=0.15)
    # Pass budgets: one pass makes at most ONE join per net, so a budget is
    # the worst island count in the group plus slack — effort 30 across the
    # board re-proved the same impossible joins for half an hour (run 7).
    # POWER WIDTH, raised 0.400 -> 0.800 mm (lane D, 2026-09-02). VBAT,
    # SERVO_V and V5_HAT are the whole robot's supply path: VBAT is the pack,
    # SERVO_V feeds all 16 bus devices through J3, and V5_HAT feeds the Radxa
    # through header pins 2 and 4. IPC-2221 §6.2 (I = 0.048 * dT^0.44 *
    # A^0.725, A in mil^2) on 1 oz outer copper:
    #     0.400 mm -> 1.29 A at dT 10 degC     (what this board used to draw)
    #     0.800 mm -> 2.03 A at dT 10, 3.05 A at dT 20
    #     1.200 mm -> 2.73 A at dT 10
    # 0.800 and not 1.200 because the lattice pitch is (width + clearance) *
    # sqrt(2), and this board's own run 2 is on record: "1.0 mm power tracks
    # -> a 1.56 mm lattice that cannot thread the bottom connector row".
    # 0.800 gives 1.27 mm, which fits between 2.54 mm header pins; 1.200
    # gives 1.84 mm, which does not.
    # THE DEMAND IS CANNOT DETERMINE and stays that way: ROBOTIS publishes
    # 17 mA standby and 1.47 A stall at 5 V for the XL330 and no running
    # figure (part:xl330-m288-t current_mA), so "16 devices" has no number
    # behind it. What is stated here is what the COPPER carries. A supply
    # path that had to carry ten amps would need 2 oz copper or a plane, and
    # this 2-layer stackup spends its back layer on the GND pour.
    b.autoroute(nets=["VBAT", "SERVO_V", "V5_HAT"], width=0.8,
                effort=10, via_cost=2.0, verbose=verbose)
    rails = ("HAT_3V3", "J5_3V3", "HAT_1V8")
    signals = [n for n in b.net_names()
               if n not in ("GND", "VBAT", "SERVO_V", "V5_HAT") + rails]
    # Budget raised 12 -> 20 (lane D, 2026-09-02): the run before this one
    # left i2s3/BCLK, i2s3/WCLK and i2s3/DOUT unrouted, and those three are
    # the longest signal joins on the board (J1's far row to the codec). One
    # pass makes at most ONE join per net, so a budget below the worst island
    # count cannot finish however long it runs.
    b.autoroute(nets=signals, effort=20, verbose=verbose)
    # The three rails were one call at effort 22, which HAT_3V3's 19 joins
    # then had to share with two other nets' passes; split so each gets its
    # own budget, HAT_3V3 the largest.
    b.autoroute(nets=["HAT_3V3"], width=0.3, effort=26, via_cost=4.0,
                verbose=verbose)
    b.autoroute(nets=["J5_3V3", "HAT_1V8"], width=0.3, effort=10,
                via_cost=4.0, verbose=verbose)
    b.autoroute(nets=["GND"], effort=20, via_cost=3.0, verbose=verbose)
    b.pour("GND", "B.Cu")

    rep = check(b, verbose=verbose)

    os.makedirs(OUT, exist_ok=True)
    plot(b, os.path.join(OUT, "top.svg"), side="top", drc=rep, verbose=verbose)
    plot(b, os.path.join(OUT, "bottom.svg"), side="bottom", drc=rep,
         verbose=verbose)
    fab(b, os.path.join(OUT, "fab"), report=rep, verbose=verbose)
    if publish:
        publish_pcb(b, rep, images=[os.path.join(OUT, "top.svg"),
                                    os.path.join(OUT, "bottom.svg")],
                    verbose=verbose)
    return b, rep


def _resolve_offboard(b):
    """Sort bind()'s unbound terminals into 'not on this board' and real gaps.

    Dropping an unbound entry is a claim, so each drop carries its reason into
    board.notes: OFF_BOARD owners are other hardware entirely, and the 'hat'
    owner IS this board — its provisions are this board's connectors, checked
    here to be on a net that reaches at least one pad.
    """
    keep, dropped = [], []
    for owner, ref, net, why in b.unbound:
        if owner in OFF_BOARD:
            dropped.append(f"{owner}.{ref} (net {net}): off-board — "
                           f"{OFF_BOARD[owner]}")
        elif owner == "hat":
            if b.nets.get(net):
                dropped.append(
                    f"hat.{ref} (net {net}): the HAT is THIS BOARD — the "
                    f"provision lands on the board pads already on that net "
                    f"({', '.join('.'.join(p) for p in b.nets[net][:4])})")
            else:
                keep.append((owner, ref, net,
                             why + " [hat provision with NO pad on its net]"))
        else:
            keep.append((owner, ref, net, why))
    b.unbound = keep
    b.notes.append(
        f"_resolve_offboard(): {len(dropped)} netlist terminals resolved as "
        f"not-pads-of-this-board, each with its reason:\n  - "
        + "\n  - ".join(dropped))


def main():
    st = None
    if "--self-test" in sys.argv:
        ok = True
        for mode, expect in (("off-board", "placement"), ("unbound", "binding")):
            print(f"--- self-test: {mode} (expect a {expect} failure)")
            b, rep = build(self_test=mode, publish=False, verbose=False)
            rows = [f for f in rep.findings
                    if f.rule == expect and f.verdict != "PASS"]
            if mode == "unbound":
                rows = [f for f in rep.findings
                        if f.rule == "binding" and f.verdict != "PASS"]
            print(f"    {len(rows)} non-PASS {expect} findings")
            if not rows:
                ok = False
                print("    SELF-TEST FAILED: the break was not caught")
        sys.exit(0 if ok else 1)
    b, rep = build(self_test=st, publish="--no-publish" not in sys.argv)
    print(b.describe())
    print("verdict:", rep.verdict)
    sys.exit({"PASS": 0, "FAIL": 2}.get(rep.verdict, 3))


if __name__ == "__main__":
    main()
