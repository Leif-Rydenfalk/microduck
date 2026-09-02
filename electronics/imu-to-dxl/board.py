#!/usr/bin/env python3
"""electronics/imu-to-dxl/board.py — OUR imu_to_dxl v2, as a ce-pcb board.

THIS IS NOT POLLEN'S BOARD. Pollen publishes the imu_to_dxl v2 board's
BEHAVIOUR and nothing else: an LSM6DSV16X presented on the Dynamixel bus as a
Protocol-2 slave, ID 200, serving a 12-byte block at register 124
(research/raw/duck-control_src_imu.rs:1-17; model.rs:78 'pub const
IMU_DXL_ID: u8 = 200;'). docs/ELECTRONICS-AND-SOFTWARE.md §4.1's last row is
explicit: "MCU, transceiver, schematic, firmware | CANNOT DETERMINE — not in
the repository". This file builds a board that carries those published
functions, with every unpublished choice made by us, named E1..E8, and the
alternative it beat recorded beside it.

Run:  python3 electronics/imu-to-dxl/board.py             build, check, plot, fab
      python3 electronics/imu-to-dxl/board.py --self-test break checks on purpose
      python3 electronics/imu-to-dxl/board.py --no-publish skip the dashboard

WHAT THE PUBLISHED FACTS FIX (these are not decisions)

  * The chip: ST LSM6DSV16X (imu.rs:1-6), LGA-14L 2.5 x 3.0 x 0.86 mm
    (DS13510 Rev 4, Figure 33, p.175/198).
  * The bus: one 3-wire TTL multidrop line, 'Pinout | 1 GND 2 VDD 3 DATA'
    (part:xl330-m288-t connector), 1 Mbps, Dynamixel Protocol 2.0
    (model.rs:80, 91).
  * The bus reaches this board three times. wiring/CABLES.md rows 6, 7 and 12
    are `dxl-id30-imu200` (head, 120 mm), `dxl-imu200-id20` (left hip yaw,
    40 mm) and `dxl-imu200-id10` (right hip yaw, 40 mm), each 'JST EH 3-pin
    (EHR-03 housing, SEH-001T-P0.6 crimp) both ends'.
    THE CONNECTOR COUNT IS STILL CANNOT DETERMINE, and this file does not
    claim otherwise. ce-parts/microduck-imu-to-dxl/component.json
    record.connector_count (corrected 2026-09-02) makes the point sharply: a
    DYNAMIXEL TTL bus is MULTIDROP, so the harness may fork at a Y-splice
    instead of at a device, and Open Duck Mini v2 — the design this descends
    from — does exactly that (its Waveshare Bus Servo Adapter has two ports
    and a T splits the legs). The record leaves option A (three connectors on
    this board) and option B (two connectors plus a Y-splice beside it)
    indistinguishable without a photograph, and rules out only option C.
    THIS BOARD FITS OPTION A, because option A is what wiring/cables.json
    already assumes and what wiring/CABLES.md's 22 cables are cut to. Option B
    is the alternative it beat, and the record states the consequence of
    being wrong exactly: "Only the assembly BOM: option B adds one Y-splitter
    and one short lead. No net changes, no length changes worth re-cutting."
    J3 is therefore a fitted-but-removable port: leave it unstuffed and the
    board becomes option B.
  * VDD is the servo bus rail SERVO_V — the raw pack on our reading of the
    HAT (robot-hat/board.py D2), 6.6 - 8.2 V under load
    (docs/ELECTRONICS-AND-SOFTWARE.md §3.4), and wiring/CABLES.md computes
    7.731 V delivered here at a full pack, 6.131 V at 6.6 V.

OUR RECONSTRUCTION DECISIONS (E1..E8) — each an unpublished fact

  E1  MCU: STM32G031F6P6, TSSOP-20. The community's own statement is the
      evidence: "any Protocol-2-slave MCU (STM32G0/CH32V) would do"
      (docs §4.1 [C-elec]); the STM32G0 is the first named. This part has two
      USARTs (USART2 on PA2/PA3) and SPI1 (PA4-PA7), which is exactly the pin
      set this circuit needs, in the only 20-pin package ST bonds it in
      (DS12992 Rev 4 Figure 5, p.32/126).
      ALTERNATIVE IT BEAT: CH32V003 (cheaper, SOP-8/TSSOP-20) — rejected only
      because the published sentence names STM32G0 first and no fact
      distinguishes them further. NOT a claim about Pollen's part.
  E2  Half-duplex: 74LVC1G125 (SOT753) driving DATA, its OE driven by an MCU
      GPIO (PA0), RX reading the line through a 0R link. ROBOTIS' own
      reference circuit is a 74LVC2G241 with a TX_Enable
      (part:xl330-m288-t communication_circuit) — and UNLIKE the host side
      (robot-hat D3, where robotd drives no direction GPIO at all), a SLAVE
      owns its own timing and CAN drive a direction pin, so the vendor's
      topology applies here. One gate is fitted rather than two because the
      second buffer of a 2G241 only isolates RX from the slave's own echo,
      which a Protocol-2 slave discards anyway.
      ALTERNATIVE IT BEAT: the literal 74LVC2G241.
  E3  3.3 V: TI LP2985A-33DBVR LDO, SOT-23-5. 'VIN range (new chip): 2.5V to
      16V', 'Output current: Up to 150mA', 'Package: 5-pin SOT-23 (DBV)'
      (SLVS522S, JULY 2004 - REVISED MAY 2025, p.1). 16 V covers the pack's
      8.4 V full-charge with margin; the board's own draw is milliamps, so an
      LDO's dissipation ((8.4-3.3) x ~10 mA = 51 mW) is not a thermal
      question.
      ALTERNATIVE IT BEAT: a switching regulator (better efficiency, more
      parts, and a noise source 3 mm from an IMU).
  E4  IMU interface: SPI 4-wire, not I2C. 'To select/exploit the I2C
      interface, the CS line must be tied high' (DS13510 §5.1) — so a driven
      CS selects SPI, and SPI needs no pull-ups and no address strap and runs
      at the sensor's full 10 MHz. Pollen's choice: CANNOT DETERMINE.
      ALTERNATIVE IT BEAT: I2C with two 10k pull-ups and SA0 strapped.
  E5  The DATA pull-up lives on the HOST side and is NOT duplicated here.
      ROBOTIS' circuit puts '10 kOhm pull-ups to 3.3V on RXD and on Data'
      (part:xl330-m288-t communication_circuit) at the controller; sixteen
      devices each adding a 10k would load the line to 625 ohm. R2 is a 0R
      link so the pull-up can be FITTED on this board if a bench measurement
      ever wants it.
  E6  Analog-hub / Qvar pins 2 and 3 tied to GND: 'Connect to Vdd_IO or GND
      if the analog hub and Qvar are disabled' (DS13510 Table 2, p.11/198).
      Pins 10 (OCS_Aux) and 11 (SDO_Aux) tied to Vdd_IO: 'Connect to Vdd_IO
      or leave unconnected' — tied, because a floating CMOS input on a
      board that has to survive a walking robot is a decision nobody wants
      to have made by accident.
  E7  SWD: PA13/PA14 (pins 18/19) brought out to four 1.5 mm test points
      with GND and 3V3. The firmware is CANNOT DETERMINE, so the board must
      at minimum be PROGRAMMABLE; a board that cannot be flashed is not a
      board.
  E8  Outline 40.000 x 22.000 mm, r2.0 corners, two M2 holes at
      (3.000, 18.500) and (37.000, 18.500). It grew from 34.000 x 24.000
      when E10 put all three bus connectors on one edge. Pollen ships no mesh for this board (the only PCB meshes
      in reference/pollen-microduck-rl/assets are elec_rpi_robot_hat_pcb.stl
      and pcb__raspberry_pi_zero_2_w.stl), so NOTHING measured constrains
      this outline. It is OUR choice, sized to the parts, and it must be
      checked against the trunk cavity before it is cut. Stated as CANNOT
      DETERMINE in the DRC notes rather than presented as Pollen's.

  E10 THE POWER PATH IS A PASS-THROUGH, AND IT IS HAND-LAID, NOT AUTOROUTED.
      This is a measured defect found and fixed on 2026-09-02. A DYNAMIXEL
      bus daisy-chains POWER as well as data: SERVO_V and GND arrive on J1
      and leave on J2 and J3, so this board's copper carries the supply of
      every device downstream of it — with the harness as
      wiring/CABLES.md cuts it, that is BOTH LEGS, ten XL330 servos.
      The first build let the autorouter draw that path at 0.400 mm.
      IPC-2221 §6.2 (I = 0.048 * dT^0.44 * A^0.725, A in mil^2) puts a
      0.400 mm 1 oz external trace at 1.29 A for a 10 degC rise, and
      wiring/CABLES.md's own worst case is an assumed 1 A per moving servo.
      The fix: all three connectors moved onto one edge and SERVO_V laid by
      hand as a 2.000 mm comb, mirrored on B.Cu with stitching vias, before
      the router runs. GND needs no track — it is the B.Cu pour, which is
      the width of the board.
      THE DEMAND IS STILL CANNOT DETERMINE. ROBOTIS publishes only 17 mA
      standby and 1.47 A stall at 5 V for the XL330 (part:xl330-m288-t
      current_mA), so 'ten servos' has no number behind it; what this file
      states is what the COPPER carries, computed and printed, not what the
      load draws.

Decoupling values are the vendor's own where one is published (100 nF on the
IMU's two supplies, DS13510 §7.1 Figure 28: 'Power supply decoupling
capacitors (C1, C2 = 100 nF ceramic)'; 1 uF in / 2.2 uF out on the LDO,
SLVS522S Table 5-3) and OUR practice where none is (100 nF on the MCU and on
the buffer) — each says which it is.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

_spec = importlib.util.spec_from_file_location(
    "microduck_netlist", os.path.join(os.path.dirname(HERE), "netlist.py"))
_net = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_net)

from cecad.pcb import (Board, Pad, custom, footprint,               # noqa: E402
                       test_point)
from cecad.pcbcheck import check                                    # noqa: E402
from cecad.pcbfab import fab                                        # noqa: E402
from cecad.pcbview import plot, publish_pcb                         # noqa: E402

# ---------------------------------------------------------------------------
# PARAMETERS — every driving number once, with the sentence it came from
# ---------------------------------------------------------------------------
W, H = 40.0, 22.0            # E8 — OUR outline, nothing measured fixes it
CORNER = 2.0
MOUNT = "M2"

# LSM6DSV16X LGA-14L. Figure 33 'LGA-14L 2.5 x 3.0 x 0.86 mm package outline
# and mechanical data', DS13510 Rev 4 p.175/198, BOTTOM VIEW read at 200 dpi:
#   OUTER DIMENSIONS   Length [L] 2.50 +/-0.1 · Width [W] 3.00 +/-0.1 ·
#                      Height [H] 0.86 MAX
#   pads               '14x 0.25+/-0.05' x '14x 0.475+/-0.05'
#   column pitch       '0.5', column span '1.5' (4 pads), row pitch '0.5',
#                      row span '1' (3 pads), edge inset '4x (0.1)'
# Column pad centres are DERIVED: 3.00/2 - 0.1 - 0.475/2 = 1.1625 from centre.
# Row pad centres: 2.50/2 - 0.1 - 0.475/2 = 0.9125.
# The figure is a BOTTOM view; the footprint below is the TOP view, so the
# pin order is mirrored in x (1..4 down the LEFT column here).
LGA_CITE = ("ST DS13510 Rev 4 (May 2023) Figure 33 'LGA-14L 2.5 x 3.0 x "
            "0.86 mm package outline and mechanical data', p.175/198: pads "
            "14x 0.25+/-0.05 by 14x 0.475+/-0.05, pitch 0.5, column span "
            "1.5, row span 1, edge inset 4x (0.1); body 2.50 x 3.00 +/-0.1. "
            "Column/row centres 1.1625 / 0.9125 are DERIVED from those "
            "callouts, not printed on the figure. Bottom view mirrored to a "
            "top-view land pattern. ce-parts/lsm6dsv16x/datasheet.pdf")

# LSM6DSV16X pin numbers, Table 2 'Pin description', DS13510 Rev 4 p.11/198,
# mode 1 column: 1 SDO/SA0, 2 SDx/AH1/Qvar1, 3 SCx/AH2/Qvar2, 4 INT1,
# 5 Vdd_IO, 6 GND, 7 GND, 8 Vdd, 9 INT2, 10 OCS_Aux, 11 SDO_Aux, 12 CS,
# 13 SCL/SPC, 14 SDA/SDI/SDO.
IMU_PINS = {"SDO": "1", "INT1": "4", "VDDIO": "5", "GND": "6", "VDD": "8",
            "CS": "12", "SCK": "13", "SDI": "14"}

# STM32G031F6P6 TSSOP20 pinout — ST DS12992 Rev 4 Figure 5 'STM32G031Fx
# TSSOP20 pinout' p.32/126, read at 170 dpi:
#   1 PB7/PB8            20 PB3/PB4/PB5/PB6
#   2 PB9/PC14-OSC32_IN  19 PA15/PA14-BOOT0
#   3 PC15-OSC32_OUT     18 PA13
#   4 VDD/VDDA           17 PA12[PA10]
#   5 VSS/VSSA           16 PA11[PA9]
#   6 PF2-NRST           15 PB0/PB1/PB2/PA8
#   7 PA0                14 PA7
#   8 PA1                13 PA6
#   9 PA2                12 PA5
#  10 PA3                11 PA4
# Alternate functions, Table 13 (same document): PA2 USART2_TX, PA3 USART2_RX,
# PA4 SPI1_NSS, PA5 SPI1_SCK, PA6 SPI1_MISO, PA7 SPI1_MOSI, PA13 SWDIO,
# PA14 SWCLK. 'Upon reset, these pins are configured as SWD alternate
# functions' (Table 12 note 5).
MCU_CITE = ("ST DS12992 Rev 4 (June 2025) Figure 5 p.32/126 for the TSSOP20 "
            "pin numbers and Table 13 for USART2 (PA2/PA3), SPI1 (PA4-PA7) "
            "and SWD (PA13/PA14); package outline §6.4 'TSSOP20 is a 20-lead, "
            "6.5 x 4.4 mm thin small-outline package with 0.65 mm pitch'")
MCU = {"VDD": "4", "VSS": "5", "NRST": "6", "DIR": "7", "IMU_INT1": "8",
       "TX": "9", "RX": "10", "NSS": "11", "SCK": "12", "MISO": "13",
       "MOSI": "14", "SWDIO": "18", "SWCLK": "19"}
MCU_UNUSED = ["1", "2", "3", "15", "16", "17", "20"]

# LP2985A-33DBVR, TI SLVS522S (JULY 2004 - REVISED MAY 2025), Figure 4-1
# 'DBV Package, 5-Pin SOT-23 (Top View)' + Table 4-1 Pin Functions p.3/33:
# 1 VIN, 2 GND, 3 ON/OFF ('Tie this pin to VIN if unused'), 4 BYPASS,
# 5 VOUT. Recommended Operating Conditions p.4: VIN 2.5..16 V, IOUT 0..150 mA,
# CIN >= 1 uF, COUT >= 2.2 uF nominal (>1 uF effective).
LDO_CITE = ("TI SLVS522S (rev. May 2025) Figure 4-1 + Table 4-1, p.3/33: "
            "1 VIN, 2 GND, 3 ON/OFF, 4 BYPASS, 5 VOUT in the DBV 5-pin "
            "SOT-23; Recommended Operating Conditions p.4 VIN 2.5-16 V, "
            "IOUT <= 150 mA, CIN >= 1 uF, COUT >= 2.2 uF")

# 74LVC1G125 GV = SOT753. Same figure the HAT reads: Nexperia 'SOT753 package
# information' 31 May 2022 Fig. 2 reflow footprint — lands 0.55 wide, pitch
# 0.95, outer extent 3.45, inner 1.95 (land length 0.75, row centres +/-1.35);
# pinning 74LVC1G125 Rev 17.1 §6.2: 1 OE, 2 A, 3 GND, 4 Y, 5 VCC; function
# table (Table 4) 'L L -> L; L H -> H; H X -> Z'.
LVC_CITE = ("Nexperia SOT753 package information (31 May 2022) Fig. 2 reflow "
            "footprint: lands 0.55 wide, pitch 0.95, outer 3.45 / inner 1.95 "
            "(length 0.75 and row centres +/-1.35 derived); pin order "
            "74LVC1G125 Rev 17.1 §6.2 Table 3")

# JST EH, the connector the XL330's own sheet names and the harness lane
# specifies: 'PCB Header | JST B3B-EH-A' (part:xl330-m288-t connector),
# 'JST EH 3-pin (EHR-03 housing, SEH-001T-P0.6 crimp) both ends'
# (wiring/CABLES.md rows 6/7/12). PC board layout, JST eEH.pdf (jst-mfg.com,
# fetched 2026-09-02): holes dia 0.9 +0.1/-0 at 2.5 +/-0.05.
EH_CITE = ("JST eEH.pdf 'PC board layout' (jst-mfg.com, fetched 2026-09-02): "
           "holes dia 0.9 +0.1/-0 at pitch 2.5 +/-0.05; B3B-EH-A body 5.0 "
           "(pin span) x 10.0 (housing). Named by part:xl330-m288-t "
           "connector 'PCB Header | JST B3B-EH-A' and by wiring/CABLES.md "
           "rows 6, 7, 12")

# E10: the pass-through power comb. 2.000 mm on 1 oz outer copper is
# 3.95 A at a 10 degC rise by IPC-2221 §6.2 (I = 0.048 * dT^0.44 * A^0.725,
# A in mil^2) — computed in ipc2221_amps() below and printed into the board
# notes, never asserted.
POWER_W = 2.000

DECOUPLE_VENDOR = "100n"     # DS13510 §7.1 Fig. 28 'C1, C2 = 100 nF ceramic'
DECOUPLE_OURS = "100n"       # OUR practice on the MCU and the buffer


# ---------------------------------------------------------------------------
# footprints not in packages.json
# ---------------------------------------------------------------------------
def ipc2221_amps(width_mm, oz=1.0, dT=10.0, external=True):
    """IPC-2221 §6.2 current for a bare trace, in amps. Geometry only."""
    thick_mil = 1.378 * oz                       # 1 oz = 1.378 mil
    area_mil2 = (width_mm / 0.0254) * thick_mil
    k = 0.048 if external else 0.024
    return k * (dT ** 0.44) * (area_mil2 ** 0.725)


def fp_lga14():
    """LSM6DSV16X LGA-14L, top view, origin at the package centre."""
    pads = []
    col_y = (0.75, 0.25, -0.25, -0.75)
    for i, y in enumerate(col_y):                       # 1..4 left column
        pads.append(Pad(str(1 + i), -1.1625, y, 0.475, 0.25))
    for i, x in enumerate((-0.5, 0.0, 0.5)):            # 5..7 bottom row
        pads.append(Pad(str(5 + i), x, -0.9125, 0.25, 0.475))
    for i, y in enumerate(reversed(col_y)):             # 8..11 right column
        pads.append(Pad(str(8 + i), 1.1625, y, 0.475, 0.25))
    for i, x in enumerate((0.5, 0.0, -0.5)):            # 12..14 top row
        pads.append(Pad(str(12 + i), x, 0.9125, 0.25, 0.475))
    return custom("lga-14l-2p5x3", pads, courtyard=(3.5, 3.0), height=0.86,
                  why=LGA_CITE + ". Land = terminal, one for one: ST publishes "
                      "no separate recommended land pattern in DS13510, so "
                      "these are the TERMINAL dimensions and no IPC toe/heel "
                      "fillet is added. That is deliberate for an LGA (the "
                      "terminal is flush) and it is the reason this footprint "
                      "is hand-drawn rather than computed.")


def fp_sot753():
    pads = [Pad("1", -0.95, -1.35, 0.55, 0.75),
            Pad("2", 0.0, -1.35, 0.55, 0.75),
            Pad("3", 0.95, -1.35, 0.55, 0.75),
            Pad("4", 0.95, 1.35, 0.55, 0.75),
            Pad("5", -0.95, 1.35, 0.55, 0.75)]
    return custom("sot753", pads, courtyard=(3.6, 3.95), height=1.1,
                  why=LVC_CITE)


def fp_eh3():
    pads = [Pad(str(i + 1), (i - 1) * 2.5, 0.0, 1.5, 1.5,
                shape="rect" if i == 0 else "round",
                layer="*.Cu", drill=0.9) for i in range(3)]
    return custom("jst-b3b-eh-a", pads, courtyard=(10.5, 4.3), height=6.5,
                  why=EH_CITE + ". Pad 1.5 mm over the 0.9 drill = 0.30 mm "
                      "annular ring, JLCPCB's 'Recommended 0.25 mm or above' "
                      "for 1 oz 2-layer.")


# ---------------------------------------------------------------------------
# the board
# ---------------------------------------------------------------------------
OFF_BOARD = {
    # every other owner in the robot netlist is somewhere else entirely
}


def build(self_test=None, publish=True, verbose=True):
    d = _net.electrical_design()

    b = Board("microduck_imu_to_dxl", W, H, corner_r=CORNER,
              rules="jlcpcb_2l_standard", stackup="jlcpcb-2layer-1.6mm",
              title="Microduck imu_to_dxl v2 (reconstruction)",
              origin_note="origin = board lower-left, mm, top view; the "
                          "outline is OUR choice (E8) — Pollen ships no mesh "
                          "and no drawing for this board")

    # -- parts -------------------------------------------------------------
    b.add("U1", fp_lga14(), value="LSM6DSV16X", at=(25.0, 12.5),
          note="the one published part on this board — imu.rs:1-6")
    b.add("U2", footprint("tssop-20"), value="STM32G031F6P6", at=(10.5, 12.5),
          note="decision E1")
    b.add("U3", fp_sot753(), value="74LVC1G125", at=(31.5, 12.5),
          note="decision E2 — OE driven by the MCU, unlike the HAT's D3")
    b.add("U4", footprint("sot-23-5"), value="LP2985A-33DBVR", at=(3.5, 11.0),
          rot=90, note="decision E3")
    # E10: all three bus ports on one edge, so the pass-through power path is
    # one straight comb instead of a diagonal the router has to invent.
    for ref, at in (("J1", (6.5, 2.6)), ("J2", (18.5, 2.6)),
                    ("J3", (30.5, 2.6))):
        b.add(ref, fp_eh3(), value="DXL bus (B3B-EH-A)", at=at,
              note=("the THIRD bus port. Option A of "
                    "ce-parts/microduck-imu-to-dxl/component.json "
                    "record.connector_count; leave it unstuffed and the "
                    "board is option B (two ports, the legs forked at a "
                    "Y-splice). The count is CANNOT DETERMINE and this "
                    "connector is where that shows on the board.")
                   if ref == "J3" else
                   ("bus in from the head (cable dxl-id30-imu200, 120 mm)"
                    if ref == "J1" else
                    "branch to the left hip yaw servo, ID 20 "
                    "(cable dxl-imu200-id20, 40 mm)"))
    b.add("C1", "0603", value="1u CIN", at=(3.5, 15.0),
          note="SLVS522S: 'Use a capacitor with a value of 1 uF or larger "
               "from this pin to ground'")
    b.add("C2", "0805", value="4u7 COUT", at=(8.0, 19.0),
          note="SLVS522S: COUT >= 2.2 uF nominal; 4u7 0805 gives >1 uF "
               "effective after the sheet's own 50% derating")
    b.add("C3", "0603", value="10n BYPASS", at=(12.0, 19.0),
          note="SLVS522S p.1: 'Low noise: 30 uVRMS with 10 nF bypass "
               "capacitor'")
    b.add("C4", "0603", value=DECOUPLE_VENDOR, at=(22.0, 16.5),
          note="IMU Vdd — DS13510 §7.1 Fig. 28 'C1, C2 = 100 nF ceramic ... "
               "as near as possible to the supply pin'")
    b.add("C5", "0603", value=DECOUPLE_VENDOR, at=(28.0, 16.5),
          note="IMU Vdd_IO — same figure")
    b.add("C6", "0603", value=DECOUPLE_OURS, at=(17.0, 12.5),
          note="MCU VDD/VDDA — OUR practice; DS12992 states no value")
    b.add("C7", "0603", value=DECOUPLE_OURS, at=(35.0, 12.5), rot=90,
          note="U3 VCC — OUR practice, matching ROBOTIS' '0.1uF' on the "
               "buffer VCC in part:xl330-m288-t communication_circuit")
    b.add("C8", "0603", value="100n NRST", at=(17.0, 9.5),
          note="NRST filter — OUR practice; AN2586 recommends it, not fetched")
    b.add("R1", "0603", value="0R DXL_DATA->U3.Y", at=(31.5, 8.5),
          note="link so the driver output can be lifted from the bus for a "
               "bench measurement without cutting copper")
    b.add("R2", "0603", value="0R DXL_DATA->RX", at=(35.0, 8.5),
          note="decision E5 — the RX tap; the site also takes the 10k "
               "pull-up ROBOTIS puts on the CONTROLLER, if one is ever wanted")
    for i, (ref, val) in enumerate((("TP1", "SWDIO"), ("TP2", "SWCLK"),
                                    ("TP3", "NRST"), ("TP4", "3V3"),
                                    ("TP5", "GND"))):
        b.add(ref, test_point(1.5), value=val, at=(16.5 + 2.6 * i, 19.5),
              note="decision E7 — the board must be flashable")
    b.mount_holes(MOUNT, corners=[(3.0, 18.5), (37.0, 18.5)])

    if self_test == "off-board":
        b.place("J2", at=(39.5, 2.6))       # hangs over the right edge

    # -- connectivity FROM the netlist ---------------------------------------
    # The robot netlist knows this board as the owner `imu200` with three
    # terminals; they land on J1 and are echoed onto J2/J3 below, because the
    # netlist models ONE bus node and the board realises it as three headers.
    refs = {"imu200": "J1"}
    pins = {"J1": {"GND": "1", "VDD": "2", "DATA": "3"}}
    b.bind(d, refs=refs, pins=pins, strict=False)
    _resolve_offboard(b)

    # -- the bus: three headers, one node ------------------------------------
    for ref in ("J2", "J3"):
        b.attach("GND", f"{ref}.1")
        b.attach("SERVO_V", f"{ref}.2")
        b.attach("dxl/DATA", f"{ref}.3")

    # -- E3: the 3.3 V rail --------------------------------------------------
    b.attach("SERVO_V", "U4.1")            # VIN
    b.attach("GND", "U4.2")
    b.attach("SERVO_V", "U4.3")            # ON/OFF — 'Tie this pin to VIN if unused'
    b.net("V3V3", "U4.5")
    b.attach("BYPASS", "U4.4")
    b.attach("SERVO_V", "C1.1"); b.attach("GND", "C1.2")
    b.attach("V3V3", "C2.1"); b.attach("GND", "C2.2")
    b.attach("BYPASS", "C3.1"); b.attach("GND", "C3.2")

    # -- E1: the MCU ---------------------------------------------------------
    b.attach("V3V3", f"U2.{MCU['VDD']}")
    b.attach("GND", f"U2.{MCU['VSS']}")
    b.net("NRST", f"U2.{MCU['NRST']}")
    b.attach("V3V3", "C6.1"); b.attach("GND", "C6.2")
    b.attach("NRST", "C8.1"); b.attach("GND", "C8.2")
    b.net("DIR", f"U2.{MCU['DIR']}")
    # MCU_TX is a BOARD-LOCAL net, not the robot's uart2/TX: the host's UART2
    # never reaches this board, it reaches the HAT (netlist.py declare_segment
    # 'uart2'). What arrives here is dxl/DATA, the one bus wire.
    b.net("MCU_TX", f"U2.{MCU['TX']}")
    b.net("MCU_RX", f"U2.{MCU['RX']}")
    b.net("SPI_NSS", f"U2.{MCU['NSS']}")
    b.net("SPI_SCK", f"U2.{MCU['SCK']}")
    b.net("SPI_MISO", f"U2.{MCU['MISO']}")
    b.net("SPI_MOSI", f"U2.{MCU['MOSI']}")
    b.net("IMU_INT1", f"U2.{MCU['IMU_INT1']}")
    b.net("SWDIO", f"U2.{MCU['SWDIO']}")
    b.net("SWCLK", f"U2.{MCU['SWCLK']}")
    b.no_connect(*[f"U2.{p}" for p in MCU_UNUSED],
                 why="TSSOP20 positions this circuit uses no signal on. Pins "
                     "1, 2, 3, 15, 16, 17 and 20 are multi-bonded groups "
                     "(DS12992 Figure 5: e.g. pin 15 is 'PB0/PB1/PB2/PA8') "
                     "and nothing in this design needs them; no crystal is "
                     "fitted because the Dynamixel 1 Mbps timing is met by "
                     "the HSI16 with the internal PLL.")

    # -- E2: the half-duplex driver -----------------------------------------
    b.attach("DIR", "U3.1")                # OE, active LOW
    b.attach("MCU_TX", "U3.2")             # A
    b.attach("GND", "U3.3")
    b.net("DXL_DRV", "U3.4")               # Y
    b.attach("V3V3", "U3.5")
    b.attach("V3V3", "C7.1"); b.attach("GND", "C7.2")
    b.attach("DXL_DRV", "R1.1")
    b.attach("dxl/DATA", "R1.2")
    b.attach("dxl/DATA", "R2.1")
    b.attach("MCU_RX", "R2.2")

    # -- E4/E6: the IMU ------------------------------------------------------
    b.attach("V3V3", f"U1.{IMU_PINS['VDD']}")
    b.attach("V3V3", f"U1.{IMU_PINS['VDDIO']}")
    b.attach("GND", f"U1.{IMU_PINS['GND']}")
    b.attach("GND", "U1.7")
    b.attach("SPI_NSS", f"U1.{IMU_PINS['CS']}")
    b.attach("SPI_SCK", f"U1.{IMU_PINS['SCK']}")
    b.attach("SPI_MOSI", f"U1.{IMU_PINS['SDI']}")
    b.attach("SPI_MISO", f"U1.{IMU_PINS['SDO']}")
    b.attach("IMU_INT1", f"U1.{IMU_PINS['INT1']}")
    b.attach("GND", "U1.2")                # E6 — AH1/Qvar1 disabled
    b.attach("GND", "U1.3")                # E6 — AH2/Qvar2 disabled
    b.attach("V3V3", "U1.10")              # E6 — OCS_Aux to Vdd_IO
    b.attach("V3V3", "U1.11")              # E6 — SDO_Aux to Vdd_IO
    b.no_connect("U1.9",
                 why="INT2/DEN — this design reads the SFLP quaternion over "
                     "SPI on INT1's data-ready; DS13510 Table 2 makes INT2 "
                     "'Programmable interrupt 2 (INT2) / Data enable (DEN)', "
                     "i.e. optional. Which interrupt Pollen uses is CANNOT "
                     "DETERMINE.")
    b.attach("V3V3", "C4.1"); b.attach("GND", "C4.2")
    b.attach("V3V3", "C5.1"); b.attach("GND", "C5.2")

    # -- E7: the SWD pads ----------------------------------------------------
    b.attach("SWDIO", "TP1.1")
    b.attach("SWCLK", "TP2.1")
    b.attach("NRST", "TP3.1")
    b.attach("V3V3", "TP4.1")
    b.attach("GND", "TP5.1")

    b.text("microduck imu_to_dxl v2", (7.0, 8.0), size=1.1)
    b.text("OUR RECONSTRUCTION - NOT POLLEN'S BOARD", (18.0, 8.0), size=0.9)
    b.text("DXL ID 200", (22.5, 20.6), size=0.9)

    # -- land patterns read against documents --------------------------------
    b.confirm("U1", LGA_CITE)
    b.confirm("U2", "ST DS12992 Rev 4 §6.4 read: 'TSSOP20 is a 20-lead, "
                    "6.5 x 4.4 mm thin small-outline package with 0.65 mm "
                    "pitch' — the JEDEC MO-153AC outline the calculator used "
                    "is the outline this part is bonded in (Table 76 "
                    "'TSSOP20 - Mechanical data')")
    b.confirm("U3", LVC_CITE)
    b.confirm("U4", "TI SLVS522S read: 'Package: 5-pin SOT-23 (DBV)', "
                    "'2.9mm x 2.8mm'; the JEDEC MO-178AA outline the "
                    "calculator used is the DBV body, and Figure 4-1 gives "
                    "the pin order the netlist above uses")
    b.confirm("J1", EH_CITE)
    b.confirm("J2", EH_CITE)
    b.confirm("J3", EH_CITE)

    # -- what nobody has published, said out loud ----------------------------
    b.notes.append(
        "OUTLINE IS NOT MEASURED. 40.000 x 22.000 mm r2.0 with two M2 holes "
        "at (3.000, 18.500) and (37.000, 18.500) is decision E8. Pollen ships "
        "no mesh, no drawing and no photograph of this board; the MJCF places "
        "only an `imu` SITE at trunk_base body (-21, 0.1, -14.7) -> world "
        "(-21, 0, 105.3) mm (docs/ELECTRONICS-AND-SOFTWARE.md §4.1). A "
        "clearance check of this rectangle against trunk_base is a mechanical "
        "task, not a PCB one, and it has not been run.")
    b.notes.append(
        f"E10 — THE POWER PATH IS A PASS-THROUGH. SERVO_V arrives on J1 and "
        f"leaves on J2 and J3, so this board's copper carries every device "
        f"downstream of it: with wiring/CABLES.md's harness that is both leg "
        f"chains, ten XL330 servos. It is hand-laid at {POWER_W:.3f} mm on "
        f"F.Cu AND mirrored on B.Cu with four stitching vias, claimed before "
        f"the router runs. IPC-2221 §6.2 gives "
        f"{ipc2221_amps(POWER_W):.2f} A per layer at a 10 degC rise "
        f"({ipc2221_amps(POWER_W, dT=20.0):.2f} A at 20 degC); whether the "
        f"pair carries twice that is NOT something IPC-2221 answers — the "
        f"two runs are 1.6 mm apart in one thermal mass — so the honest "
        f"figure is the per-layer one. The first build of this board let the "
        f"autorouter draw this net at 0.400 mm, which the same equation puts "
        f"at {ipc2221_amps(0.4):.2f} A. GND returns through the B.Cu pour, "
        f"which is the width of the board.")
    b.notes.append(
        "CURRENT: no net on this board has a documented total. The published "
        "figures are the chip's alone — 'IddHP | Gyroscope and accelerometer "
        "current consumption in high-performance mode | 0.65 | mA' (DS13510 "
        "Table 4 p.14/198) — and the record says so explicitly: 'The board's "
        "MCU and transceiver draw are unpublished, so the board total is "
        "CANNOT DETERMINE; this figure is a floor, not the board' "
        "(ce-parts/microduck-imu-to-dxl/electrical.part.json). check_current "
        "therefore reports CANNOT DETERMINE and no track is sized from a "
        "guess.")

    if self_test:
        rep = check(b, verbose=verbose)
        return b, rep

    # -- copper --------------------------------------------------------------
    # E10: SERVO_V FIRST, BY HAND, WIDE. This net is a pass-through — it
    # arrives on J1 and leaves on J2 and J3 to both leg chains — so its
    # copper carries every downstream servo, and the first build of this
    # board let the router draw it at 0.400 mm. The comb below claims the
    # lane between the connector row and the parts before anything else runs.
    #
    #   J1.2 (6.500, 2.600) -> up to y 6.500 -> across to x 30.500 -> down to
    #   J3.2, with a branch down to J2.2. The verticals pass 2.500 mm from
    #   each connector's pins 1 and 3, which at 2.000 mm wide leaves
    #   2.500 - 1.000 - 0.750 = 0.750 mm to the nearest pad — 7.5x the rule.
    def _p(ref, pad):
        c = b.component(ref)
        return c.pad_xy(c.fp.pad(pad))

    spine = [_p("J1", "2"), (6.5, 6.5), (30.5, 6.5), _p("J3", "2")]
    branch = [(18.5, 6.5), _p("J2", "2")]
    for layer in ("F.Cu", "B.Cu"):
        b.track("SERVO_V", spine, width=POWER_W, layer=layer)
        b.track("SERVO_V", branch, width=POWER_W, layer=layer)
    # Stitching vias tie the two runs together along the horizontal lane.
    for x in (9.0, 13.0, 22.5, 26.5):
        b.via("SERVO_V", (x, 6.5), pad=1.0)
    # Surface GND pads bond to the back plane through a stub + via; the
    # through-hole header GND pins reach B.Cu through their own barrels, and
    # GND itself is never routed — it is the pour, which is the width of the
    # board.
    for ref, pad, dx, dy in [
            ("U4", "2", -1.2, 0.0),
            ("U3", "3", 0.0, -1.2),
            ("C1", "2", 1.2, 0.0), ("C2", "2", 1.3, 0.0),
            ("C3", "2", 1.2, 0.0), ("C4", "2", 1.2, 0.0),
            ("C5", "2", 1.2, 0.0), ("C6", "2", 1.2, 0.0),
            ("C7", "2", 0.0, 1.2), ("C8", "2", 1.2, 0.0),
            ("TP5", "1", 0.0, -1.2)]:
        c = b.component(ref)
        x, y = c.pad_xy(c.fp.pad(pad))
        b.track("GND", [(x, y), (x + dx, y + dy)], width=0.25)
        b.via("GND", (x + dx, y + dy))
    # Pass budgets: one pass makes at most ONE join per net, so a net with
    # 13 pads needs at least 12 passes. V3V3 has 13 (measured), so effort 8
    # left it in 9 islands on the first run — that is the number this budget
    # is set from, not a guess.
    b.autoroute(nets=["V3V3"], width=0.3, effort=20, via_cost=3.0,
                verbose=verbose)
    signals = [n for n in b.net_names() if n not in ("GND", "SERVO_V", "V3V3")]
    b.autoroute(nets=signals, effort=14, verbose=verbose)
    b.pour("GND", "B.Cu")

    rep = check(b, verbose=verbose)

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
    """Everything in the robot netlist that is not a pad of THIS board.

    Dropping an unbound terminal is a claim, so every drop carries its reason
    into board.notes. This board is one device on a 16-device bus: the servos,
    the HAT, the Radxa, the codec, the camera and the battery are all other
    hardware, and their terminals are resolved out by name.
    """
    keep, dropped = [], []
    for owner, ref, net, why in b.unbound:
        if owner == "imu200":
            keep.append((owner, ref, net, why))
        elif b.nets.get(net):
            dropped.append(
                f"{owner}.{ref} (net {net}): another device on the same bus "
                f"node — its terminal lands on this board's own pads on that "
                f"net ({', '.join('.'.join(p) for p in b.nets[net][:3])})")
        else:
            dropped.append(f"{owner}.{ref} (net {net}): off-board — net "
                           f"{net} has no pad on the imu_to_dxl board")
    b.unbound = keep
    b.notes.append(
        f"_resolve_offboard(): {len(dropped)} netlist terminals resolved as "
        f"not-pads-of-this-board. The robot netlist is the WHOLE robot; this "
        f"board is one device on it. First ten reasons:\n  - "
        + "\n  - ".join(dropped[:10]))



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
        ok = True
        print("--- self-test: off-board (expect a placement failure)")
        b, rep = build(self_test="off-board", publish=False, verbose=False)
        rows = [f for f in rep.findings
                if f.rule == "placement" and f.verdict != "PASS"]
        print(f"    {len(rows)} non-PASS placement findings")
        if not rows:
            ok = False
            print("    SELF-TEST FAILED: the break was not caught")
        sys.exit(0 if ok else 1)
    b, rep = build(publish="--no-publish" not in sys.argv)
    print(b.describe())
    print(f"IPC-2221: SERVO_V {POWER_W:.3f} mm on 1 oz external = "
          f"{ipc2221_amps(POWER_W):.2f} A at dT=10 degC, per layer")
    print("verdict:", rep.verdict)
    sys.exit({"PASS": 0, "FAIL": 2}.get(rep.verdict, 3))


if __name__ == "__main__":
    main()
