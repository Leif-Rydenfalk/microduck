#!/usr/bin/env python3
"""electronics/netlist.py — the Microduck as ONE cecad.netlist.Design, checked.

GOAL.md rung 4: "a `cecad.netlist.Design` of the robot that PASSes its checks".
This file builds that Design from the published facts in
docs/ELECTRONICS-AND-SOFTWARE.md and the shelf records under ce-parts/, runs
the nine cecad checks plus four of its own, and writes the three-verdict
report to electronics/netlist-report.md.

    python3 electronics/netlist.py              build, check, write the report
    python3 electronics/netlist.py --self-test  break every check on purpose
    python3 electronics/netlist.py --no-write   check only, print, no files

Exit codes are the verdicts, ce-wire's convention: 0 PASS · 2 FAIL ·
3 CANNOT DETERMINE · 1 refused (a duplicate slug across shelves, a missing
tool). The self-test exits 0 only when every deliberate break is caught.

WHAT IS IN IT

  host      radxa-zero-3w (ce-parts/radxa-zero-3w/electrical.host.json — the
            Radxa product brief + wiki pinout, fetched 2026-09-02)
  segments  i2c3 (header pins 3/5), uart2 (pins 8/10), dxl (the one DATA
            wire behind the HAT's transceiver), i2s3 (M0 pins, asserted),
            i2c2 + csi (the 22-pin MIPI CSI connector)
  parts     np-f550 pack -> HAT -> Radxa 5 V; HAT -> SERVO_V + DXL_DATA ->
            15 x xl330-m288-t (IDs 10-14, 20-24, 30-34) + imu_to_dxl (200);
            HAT I2C3: tlv320aic3104 @0x18, bmi088 @0x19/0x68, ToF @0x29 on
            Stemma J5; camera module on CSI (I2C2 @0x10); speaker, mic.

WHAT IS CANNOT DETERMINE, BY NAME (the HAT schematic is not published)

  - the 5 V regulator on the HAT (V5_HAT: nominal stated, capacity null)
  - the servo-bus path (SERVO_V: raw pack or regulated — model.rs says the
    servos SEE 6.6-8.2 V, which is above the XL330's 3.7-6.0 V band)
  - the half-duplex transceiver (DXL_DATA: reference layout 74LVC2G241 per
    ROBOTIS, but robotd drives no TX-enable GPIO, so the HAT is not that)
  - the codec's and BMI088's rails (HAT_3V3, HAT_1V8: no source on the shelf)
  - the I2S3 pin mux (M0 vs M1, both on the header; the dts pinctrl was not
    read), MCLK's origin, the mic input, the speaker amplifier

THREE THINGS THIS FILE DOES THAT THE RECORDS ALONE CANNOT

  1. Fifteen servos share one record and one record states no bus ID (the
     ID is an EEPROM register). Each servo is wired as a design-level VIEW
     of part:xl330-m288-t carrying its ID from model.rs:15-19 as the
     design's own assertion, so check_buses can ask "are the 16 IDs on the
     DATA wire unique?" — and `--self-test` proves it says FAIL when two
     servos are given ID 10.
  2. The BMI088 is ONE package with TWO I2C targets (0x19 accel, 0x68
     gyro). cecad.netlist reads one address per owner, so the package is
     wired as two views (bmi088, bmi088.gyro) and both addresses face the
     duplicate-address rule with the codec's 0x18 and the ToF's 0x29.
  3. The HAT record states its header pass-throughs (I2C3_SDA/SCL,
     UART2_TX/RX) with `bus: I2C` / `bus: UART`. On the netlist those are
     copper, not devices; left as bus terminals they become a "UART endpoint
     with no address" CANNOT DETERMINE that says nothing about the robot.
     The design wires a view with `bus: None` on those four needs and says
     so here; the terminals stay on the nets for the pin/collision checks.

SHELF UNION (tool gap P11, docs/ELECTRONICS-AND-SOFTWARE.md §13)

  cecad/shelf.py reads ONE $CE_PARTS_ROOT. This design's records live in
  ce-designs/microduck/ce-parts and the workshop's in ce-workshop/ce-parts.
  `shelf_union()` builds a symlink union of every ce-parts under
  $CE_TRIAD_ROOT (default: this repo, then the workshop) in
  ~/.cache/ce-workshop/shelf-union/<hash>/ and points CE_PARTS_ROOT at it.
  A slug present in two shelves is refused (exit 1), never merged.

Every quote below is verbatim from the file its cite names. Nothing here was
measured on a robot; the report says so.
"""
import argparse
import contextlib
import dataclasses
import hashlib
import io
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
WS_DEFAULT = os.path.dirname(os.path.dirname(REPO))

PASS, FAIL, CD = "PASS", "FAIL", "CANNOT DETERMINE"
EXIT = {PASS: 0, FAIL: 2, CD: 3}


# --------------------------------------------------------------------------
# the shelf union — before cecad is imported
# --------------------------------------------------------------------------
def triad_roots():
    env = os.environ.get("CE_TRIAD_ROOT")
    roots = [r for r in env.split(":") if r] if env else [REPO, WS_DEFAULT]
    return [os.path.abspath(r) for r in roots]


def shelf_union(roots=None):
    """One directory of symlinks, one per slug, over every ce-parts in roots.

    Rebuilt on every call (a few hundred symlinks, milliseconds) so a slug
    added to either shelf is seen without a cache to clear. Returns the path.
    """
    roots = roots or triad_roots()
    shelves = [os.path.join(r, "ce-parts") for r in roots
               if os.path.isdir(os.path.join(r, "ce-parts"))]
    if not shelves:
        sys.exit(f"refused: no ce-parts under any of {roots} (CE_TRIAD_ROOT)")
    key = hashlib.sha256("\n".join(shelves).encode()).hexdigest()[:12]
    union = os.path.join(os.path.expanduser("~"), ".cache", "ce-workshop",
                         "shelf-union", key)
    if os.path.isdir(union):
        for n in os.listdir(union):
            p = os.path.join(union, n)
            if os.path.islink(p):
                os.unlink(p)
    os.makedirs(union, exist_ok=True)
    seen = {}
    for shelf in shelves:
        for slug in sorted(os.listdir(shelf)):
            src = os.path.join(shelf, slug)
            if not os.path.isdir(src) or slug.startswith((".", "__")):
                continue
            if slug in seen:
                sys.exit(f"refused: slug {slug!r} exists in both {seen[slug]} "
                         f"and {shelf}. Two records under one key is two "
                         f"answers; this file merges nothing.")
            seen[slug] = shelf
            os.symlink(src, os.path.join(union, slug))
    with open(os.path.join(union, "UNION.txt"), "w") as fh:
        fh.write("symlink union built by electronics/netlist.py\n"
                 + "\n".join(shelves) + "\n")
    os.environ["CE_PARTS_ROOT"] = union
    cad = next((os.path.join(r, "ce-cad") for r in roots
                if os.path.isfile(os.path.join(r, "ce-cad", "cecad", "netlist.py"))),
               None)
    if cad is None:
        sys.exit(f"refused: ce-cad/cecad/netlist.py not under any of {roots}")
    os.environ.setdefault("CAD_ROOT", cad)
    if cad not in sys.path:
        sys.path.insert(0, cad)
    return union


UNION = shelf_union()

with contextlib.redirect_stderr(io.StringIO()):     # the FreeCAD banner
    from cecad import netlist as N
    from cecad.electrical import Finding, Report, _wrap
    from cecad import graph as G


# --------------------------------------------------------------------------
# the published facts this file asserts, each with the sentence it rests on
# --------------------------------------------------------------------------
RAW = os.path.join(REPO, "research", "raw")
MODEL_RS = os.path.join(RAW, "duck-control_src_model.rs")
I2C3_DTS = os.path.join(RAW, "deploy_audio_i2c3-pihat.dts")
AIC_DTS = os.path.join(RAW, "deploy_audio_aic3104-i2c3.dts")
TOF_RS = os.path.join(RAW, "tof_src_main.rs")
WIRING_NETS = os.path.join(REPO, "wiring", "designs", "microduck", "nets.json")

# Servo ID -> joint. IDs: model.rs:15-19 JOINT_IDS (quoted per row below).
# Joint names: duck-ipc-proto JOINT_NAMES via docs/ELECTRONICS-AND-SOFTWARE.md
# §3.2. Body: inferred from spec/mesh-placements.json (docs §3.2) — carried
# as a note, never as a fact the checks read.
SERVOS = [
    # id, joint, body, the model.rs row the ID is on
    (20, "left_hip_yaw", "trunk_base", "20, 21, 22, 23, 24, // left leg"),
    (21, "left_hip_roll", "yaw2roll", "20, 21, 22, 23, 24, // left leg"),
    (22, "left_hip_pitch", "upper_leg_left", "20, 21, 22, 23, 24, // left leg"),
    (23, "left_knee", "upper_leg_left", "20, 21, 22, 23, 24, // left leg"),
    (24, "left_ankle", "leg", "20, 21, 22, 23, 24, // left leg"),
    (30, "neck_pitch", "neck", "30, 31, 32, 33, 34, // neck, head, mouth"),
    (31, "head_pitch", "neck", "30, 31, 32, 33, 34, // neck, head, mouth"),
    (32, "head_yaw", "yaw_roll_motion", "30, 31, 32, 33, 34, // neck, head, mouth"),
    (33, "head_roll", "jaw_soft", "30, 31, 32, 33, 34, // neck, head, mouth"),
    (34, "mouth", "jaw_soft", "30, 31, 32, 33, 34, // neck, head, mouth"),
    (10, "right_hip_yaw", "trunk_base", "10, 11, 12, 13, 14, // right leg"),
    (11, "right_hip_roll", "bearing_roll", "10, 11, 12, 13, 14, // right leg"),
    (12, "right_hip_pitch", "upper_leg_right", "10, 11, 12, 13, 14, // right leg"),
    (13, "right_knee", "upper_leg_right", "10, 11, 12, 13, 14, // right leg"),
    (14, "right_ankle", "leg_2", "10, 11, 12, 13, 14, // right leg"),
]
IMU_ID = 200            # model.rs:78 'pub const IMU_DXL_ID: u8 = 200;'

# The servo-bus voltage AS THE RUNTIME DECLARES IT — read through the servos'
# own Present Input Voltage register. Not a vendor figure; Pollen's code.
SERVO_V_BAND = (6.6, 8.2)
SERVO_V_QUOTE = ("pub const BATTERY_FULL_V: f64 = 8.2; ... "
                 "pub const BATTERY_EMPTY_V: f64 = 6.6;")
SERVO_V_CITE = ("research/raw/duck-control_src_model.rs:109,113 — model.rs:103-105: "
                "'There is no fuel gauge and no ADC. The only measurement available "
                "is what the servos report as their own supply'")

# Header pins, the Radxa's own table (part:radxa-zero-3w header_40pin, [brief]
# §6.1.1 p.6 cross-checked with [wiki]); CSI pins from the [wiki] 22-pin table.
PIN = {
    "SDA3": "hdr3", "SCL3": "hdr5", "TX2": "hdr8", "RX2": "hdr10",
    "I2S_SCLK": "hdr12", "I2S_MCLK": "hdr13", "I2S_LRCK": "hdr35",
    "I2S_SDI": "hdr38", "I2S_SDO": "hdr40",
    "CSI_SDA": "csi21", "CSI_SCL": "csi20", "CSI_CLK": "csi8/9",
    "CSI_D0": "csi2/3", "CSI_D1": "csi5/6", "CSI_PDN": "csi17",
    "CSI_3V3": "csi22",
}


# --------------------------------------------------------------------------
# design-level views of shelf records (see the module docstring, 1-3)
# --------------------------------------------------------------------------
def _replace_need(spec, name, **changes):
    needs = tuple(dataclasses.replace(n, **changes) if n.name == name else n
                  for n in spec.requires)
    return dataclasses.replace(spec, requires=needs)


def servo_view(base, sid, joint, body, row):
    """part:xl330-m288-t with THIS servo's bus ID on its DATA need."""
    return dataclasses.replace(
        _replace_need(base, "DATA", address=str(sid),
                      address_quote=row,
                      address_cite="research/raw/duck-control_src_model.rs:15-19 "
                                   "JOINT_IDS (the design's assertion; the record "
                                   "states no ID — parts[xl330-m288-t].requires[]"
                                   ".address_basis)"),
        title=f"{base.title} — ID {sid}, joint {joint}",
        uncertainties=base.uncertainties + (
            f"Body carrying ID {sid} ({joint}) = {body}: inferred from the xl330 "
            f"mesh placements (docs/ELECTRONICS-AND-SOFTWARE.md §3.2), not read "
            f"off a harness.",),
        raw=dict(base.raw, servo_id=sid, joint=joint))


def bmi088_views(base):
    """(accel view, gyro view). The package's two I2C targets as two owners."""
    ends = [n for n in base.requires if n.need == "endpoint"]
    assert len(ends) == 2 and {e.address for e in ends} == {"0x19", "0x68"}, ends
    gyro = next(e for e in ends if e.address == "0x68")
    accel = dataclasses.replace(
        base, requires=tuple(n for n in base.requires if n is not gyro),
        title=base.title + " — accelerometer target (0x19), and the package's "
                           "supplies")
    gyro_v = dataclasses.replace(
        base, requires=(gyro,), provides=(),
        title=base.title + " — gyroscope target (0x68); supplies are on the "
                           "accelerometer view of the same package")
    return accel, gyro_v


def hat_view(base, keep_bus=False):
    """The HAT with its header pass-throughs marked as copper (bus None)."""
    if keep_bus:
        return base
    spec = base
    for nm in ("I2C3_SDA", "I2C3_SCL", "UART2_TX", "UART2_RX"):
        spec = _replace_need(spec, nm, bus=None)
    return dataclasses.replace(
        spec, uncertainties=spec.uncertainties + (
            "electronics/netlist.py wires I2C3_SDA/SCL and UART2_TX/RX with bus "
            "None: they are the HAT's header pass-throughs to the SoC, not "
            "addressed devices on the bus. The record's own bus words are kept "
            "in the record.",))


def _admit(design, *specs):
    """Put design-level views in front of the checks that scan the catalogue.

    `Design._catalogue` is what `check_buses` asks to decide whether a bus is
    ADDRESSED at all and what `check_power` asks for a source. A view that
    carries an address the record does not (a servo's ID) is the design's
    assertion, so the design admits it. Stated here rather than done by a
    record edit: a record cannot carry fifteen IDs.
    """
    design._catalogue = tuple(design._catalogue) + tuple(specs)
    return design


# --------------------------------------------------------------------------
# THE DESIGN
# --------------------------------------------------------------------------
def electrical_design(ids=None, gyro_addr="0x68", hat_keep_bus=False,
                      power_the_host=True, name="microduck"):
    """The robot. Keyword arguments exist for `--self-test` only."""
    ids = list(ids) if ids is not None else [s[0] for s in SERVOS]
    d = N.Design(name, host="radxa-zero-3w")

    # -- the buses the SoC drives, each pin the vendor's table -------------
    d.declare_segment(
        "i2c3", bus="I2C", controller="host",
        signals={"SDA": PIN["SDA3"], "SCL": PIN["SCL3"]},
        note="I2C3 in its M0 mux on header pins 3/5: [brief] p.6 'pin 3 "
             "I2C3_SDA_M0 | UART3_RX_M0 | GPIO1_A0', 'pin 5 I2C3_SCL_M0 | "
             "UART3_TX_M0 | GPIO1_A1' (part:radxa-zero-3w); Pollen's overlay "
             "research/raw/deploy_audio_i2c3-pihat.dts: 'pinctrl-0 = "
             "<&i2c3m0_xfer>', 'clock-frequency = <400000>'. Pull-ups: the HAT's "
             "R12/R13 10k (dts comment) in parallel with the board's own on pins "
             "3/5 ([wiki] tip) — values not judged here.")
    d.declare_segment(
        "uart2", bus="UART", controller="host",
        signals={"TX": PIN["TX2"], "RX": PIN["RX2"]},
        note="[wiki] 'The debug serial port of ZERO 3 uses UART2_M0 (40-pin GPIO "
             "Pin 8: TX, Pin 10: RX)' (part:radxa-zero-3w "
             "buses_the_microduck_uses.servo_bus_uart2_m0); robotd.toml [bus] "
             "port = \"/dev/ttyS2\"; 1 Mbps, Dynamixel Protocol 2.0 (model.rs:80, "
             "91). It is also the U-Boot console, which is why Pollen masks "
             "serial-getty@ttyS2.")
    d.declare_segment(
        "dxl", bus="UART", controller="host",
        signals={"DATA": "HAT:DXL_DATA"},
        note="THE ONE DATA WIRE. UART2 TX/RX reach it through a half-duplex "
             "transceiver on the HAT — inferred: 'no direction GPIO anywhere in "
             "the code' (docs/ELECTRONICS-AND-SOFTWARE.md §3.1, [C-elec]). The "
             "controller is the Radxa's UART2; the pin identifier HAT:DXL_DATA "
             "names the HAT-side node because the HAT's connector and "
             "transceiver part are CANNOT DETERMINE (ROBOTIS' reference is a "
             "74LVC2G241 with a TX-enable, chips[XL330-M288-T]"
             ".communication_circuit — which robotd never drives).")
    d.declare_segment(
        "i2s3", bus="I2S", controller="host",
        signals={"BCLK": PIN["I2S_SCLK"], "MCLK": PIN["I2S_MCLK"],
                 "WCLK": PIN["I2S_LRCK"], "DIN": PIN["I2S_SDO"],
                 "DOUT": PIN["I2S_SDI"]},
        note="i2s3_2ch, bit-clock and frame master on the SoC side "
             "(research/raw/deploy_audio_aic3104-i2c3.dts 'bitclock-master = "
             "<&pihat_cpu_dai>', 'frame-master = <&pihat_cpu_dai>', "
             "'system-clock-frequency = <12288000>'). Pins are the M0 mux "
             "([brief]/[wiki]: SCLK 12, MCLK 13, LRCK 35, SDI 38, SDO 40) — THIS "
             "FILE'S ASSERTION: the M1 mux (pins 19/21/23/24) is also on the "
             "header and the dts pinctrl was not read (part:radxa-zero-3w "
             "unknowns[3]). DIN = SoC SDO, DOUT = SoC SDI.")
    d.declare_segment(
        "i2c2", bus="I2C", controller="host",
        signals={"SDA": PIN["CSI_SDA"], "SCL": PIN["CSI_SCL"]},
        note="[wiki] MIPI CSI 22-pin table: '20 I2C2_SCL_M1, 21 I2C2_SDA_M1' "
             "(part:radxa-zero-3w buses_the_microduck_uses.mipi_csi); the camera "
             "probes as 'imx219 2-0010' = bus 2, address 0x10 (media:312).")
    d.declare_segment(
        "csi", bus="CSI", controller="host",
        signals={"CLK": PIN["CSI_CLK"], "D0": PIN["CSI_D0"], "D1": PIN["CSI_D1"]},
        note="[wiki] MIPI CSI table: '2 MIPI_CSI_RX_D0N, 3 D0P, ... 5 D1N, 6 D1P, "
             "... 8 CLK0N, 9 CLK0P'; two lanes as the radxa-zero3-rpi-camera-v2 "
             "overlay drives a Pi-Camera-v2-class module (media:51-65). Lanes "
             "D2/D3 unwired is the camera record's inference.")

    # -- the controller's own supply ---------------------------------------
    if power_the_host:
        d.power_host({"5V": "V5_HAT", "GND": "GND"},
                     note="[brief] §5.1 '5V Power from the GPIO PIN 2 & 4'; "
                          "the HAT makes it from the pack: i2c3.dts:22 'In-robot "
                          "power comes from the battery via the HAT regardless'. "
                          "The HAT's regulator is CANNOT DETERMINE. The USB-C OTG "
                          "port is a second 5 V path when tethered (sch1.12 sheet "
                          "22) and is not on this netlist.")

    # -- power: pack -> HAT ------------------------------------------------
    d.wire("np-f550", {"BAT+": "VBAT", "BAT-": "GND"}, label="battery",
           note="NP-F550-shape 2S pack in the trunk; contacts meet the 'banana' "
                "contact PCB (part:microduck-banana-pcb-locker clamps it), which "
                "has no electrical record — a passive board, folded into this "
                "wire. Contact pinout CANNOT DETERMINE (part:np-f550 pinout).")
    hat = hat_view(N.part("microduck-robot-hat-pcb"), keep_bus=hat_keep_bus)
    d.wire(hat, {
        "GND": "GND", "VBAT": "VBAT",
        "UART2_TX": "uart2/TX", "UART2_RX": "uart2/RX",
        "I2C3_SDA": "i2c3/SDA", "I2C3_SCL": "i2c3/SCL",
        "I2S3_SCLK": "i2s3/BCLK", "I2S3_LRCK": "i2s3/WCLK",
        "I2S3_SDO": "i2s3/DIN", "I2S3_SDI": "i2s3/DOUT", "MCLK": "i2s3/MCLK",
        "V5_OUT": "V5_HAT", "SERVO_V": "SERVO_V", "DXL_DATA": "dxl/DATA",
        "J5_3V3": "J5_3V3", "SPK+": "SPK_P", "SPK-": "SPK_N",
        "MIC_IN": "MIC_IN", "MICBIAS": "MICBIAS"},
        label="hat",
        note="Pollen RPI Robot HAT on the 40-pin header — PCB not published "
             "(docs §12 item 4). Provisions V5_HAT and SERVO_V carry null "
             "capacities and SERVO_V a null nominal by the record's own "
             "statement; the transceiver behind DXL_DATA is CANNOT DETERMINE.")

    # -- the HAT's I2C3 devices -------------------------------------------
    d.wire("tlv320aic3104", {
        "GND": "GND", "AVDD": "HAT_3V3", "DVDD": "HAT_1V8", "IOVDD": "HAT_3V3",
        "SDA": "i2c3/SDA", "SCL": "i2c3/SCL",
        "MCLK": "i2s3/MCLK", "BCLK": "i2s3/BCLK", "WCLK": "i2s3/WCLK",
        "DIN": "i2s3/DIN", "DOUT": "i2s3/DOUT"},
        label="codec",
        note="aic3104-i2c3.dts 'codec@18', 'reg = <0x18>', clocks = the 12 MHz "
             "fixed-clock. HAT_3V3 / HAT_1V8 are the rails the codec's three "
             "domains need; NOTHING on the shelf sources them — the HAT's "
             "regulators are unpublished, so those two nets are expected to "
             "come back CANNOT DETERMINE, by name.")
    accel, gyro = bmi088_views(N.part("bmi088"))
    if gyro_addr != "0x68":                       # --self-test only
        gyro = dataclasses.replace(gyro, requires=(dataclasses.replace(
            gyro.requires[0], address=gyro_addr),))
    d.wire(accel, {"GND": "GND", "VDD": "HAT_3V3", "VDDIO": "HAT_3V3",
                   "SDA": "i2c3/SDA", "SCL": "i2c3/SCL"},
           label="bmi088",
           note="i2c3.dts:11 'dormant BMI088 0x19/0x68', 'unused but still "
                "connected' (dts:31). Accelerometer target 0x19 and the "
                "package's VDD/VDDIO — on HAT_3V3 by this file's assertion that "
                "a 2.4-3.6 V part on a 3.3 V-I/O HAT sits on its 3.3 V; which "
                "rail is CANNOT DETERMINE (chips[bmi088].unknowns[1]).")
    d.wire(gyro, {"SDA": "i2c3/SDA", "SCL": "i2c3/SCL"}, label="bmi088.gyro",
           note="The same package's gyroscope target, 0x68 — a second owner so "
                "the duplicate-address rule sees both addresses (module "
                "docstring, item 2).")
    d.wire("microduck-tof-module", {"GND": "GND", "3V3": "J5_3V3",
                                    "SDA": "i2c3/SDA", "SCL": "i2c3/SCL"},
           label="tof",
           note="On the HAT's 'Stemma J5' (i2c3.dts:10); 0x29 factory default "
                "(tof_src_main.rs:80-87). VL53L5CX recorded; the L8CX has no "
                "3.3 V IOVDD configuration, so an L8CX breakout on a 3.3 V J5 "
                "must carry its own regulator — which generation ships is "
                "CANNOT DETERMINE (docs §6).")

    # -- the servo bus -----------------------------------------------------
    d.wire("microduck-imu-to-dxl", {"GND": "GND", "VDD": "SERVO_V",
                                    "DATA": "dxl/DATA"},
           label="imu200",
           note="imu_to_dxl v2, LSM6DSV16X, bus ID 200 (model.rs:78 'pub const "
                "IMU_DXL_ID: u8 = 200;'). Its input band and regulator are "
                "CANNOT DETERMINE (record).")
    base = N.part("xl330-m288-t")
    views = []
    for (sid, joint, body, row), use_id in zip(SERVOS, ids):
        v = servo_view(base, use_id, joint, body, row)
        views.append(v)
        d.wire(v, {"GND": "GND", "VDD": "SERVO_V", "DATA": "dxl/DATA"},
               label=f"id{use_id}" if use_id == sid else f"id{sid}x{use_id}",
               note=f"XL330-M288-T ID {use_id}, joint {joint}, body {body} "
                    f"(docs §3.2). Three wires: 'Pinout | 1 GND 2 VDD 3 DATA' "
                    f"(chips[XL330-M288-T].connector).")
    _admit(d, *views)

    # -- the camera on CSI -------------------------------------------------
    d.wire("microduck-camera-module", {
        "GND": "GND", "VCC_3V3": "VCC_3V3_CSI",
        "CSI_CLK": "csi/CLK", "CSI_D0": "csi/D0", "CSI_D1": "csi/D1",
        "I2C2_SDA": "i2c2/SDA", "I2C2_SCL": "i2c2/SCL", "PDN": PIN["CSI_PDN"]},
        label="camera",
        note="IMX219 board behind the M12 lens, upside down (media:335-357). "
             "Module part, regulators, ribbon: CANNOT DETERMINE (record).")
    d.external_supply(
        "VCC_3V3_CSI",
        "MIPI CSI pin 22 is the Radxa's own 3.3 V: [wiki] 22-pin table "
        "'22 VCC_3V3' (part:radxa-zero-3w buses_the_microduck_uses.mipi_csi). "
        "The host record states no supply provision, so this is asserted from "
        "the vendor table rather than routed by a record.")

    # -- audio transducers -------------------------------------------------
    d.wire("microduck-speaker", {"SPK+": "SPK_P", "SPK-": "SPK_N"},
           label="speaker",
           note="35x25x7 box speaker in the head; representative 8 ohm 2 W "
                "(part:microduck-speaker). Codec line-out or an amplifier on "
                "the HAT: CANNOT DETERMINE (docs §7).")
    d.wire("microduck-mic", {"GND": "GND", "MIC": "MIC_IN", "BIAS": "MICBIAS"},
           label="mic",
           note="Transducer, type, count and codec input: CANNOT DETERMINE "
                "(docs §12 item 11; the community's 'Mic3R' is not a pin of the "
                "TLV320AIC3104 — chips[tlv320aic3104].unknowns[0]).")
    return d


# --------------------------------------------------------------------------
# the design's own checks — three verdicts, quote + cite on every non-PASS
# --------------------------------------------------------------------------
def _sink_band(t, cs):
    """(v_min, v_max, quote, cite) a sink need states, through `from`."""
    nd = t.need
    if nd is None:
        return None
    lo, hi = nd.raw.get("v_min"), nd.raw.get("v_max")
    q, c = nd.quote, nd.cite
    m = re.match(r"^chips\[([^\]]+)\]\.supplies\[(\d+)\]", str(nd.from_ or ""))
    if (lo is None or hi is None) and m and m.group(1) in cs:
        sup = cs[m.group(1)].supplies[int(m.group(2))]
        lo, hi = sup.get("v_min"), sup.get("v_max")
        q, c = q or "", sup.get("cite", c)
    if lo is None or hi is None:
        return None
    return float(lo), float(hi), q, c


def check_supply_bands(design, declared=None, verbose=False):
    """Every supply net: the voltage the design puts on it vs every sink's
    stated band.

    The source voltage is, in order: a band DECLARED by the design (SERVO_V
    from model.rs), else the source provision's nominal_v. A sink with no
    stated band, or a net with no stated voltage, is CANNOT DETERMINE with
    the reason. cecad's own `_voltage_finding` only fires through connector
    slots, which this design has none of — so this is the rule that asks it.
    """
    declared = {"SERVO_V": (SERVO_V_BAND, SERVO_V_QUOTE, SERVO_V_CITE),
                "VCC_3V3_CSI": ((3.3, 3.3), "22 VCC_3V3",
                                "[wiki] MIPI CSI 22-pin table (part:radxa-zero-3w "
                                "buses_the_microduck_uses.mipi_csi) — the pin's "
                                "name; no tolerance is printed")} \
        if declared is None else declared
    cs = design.chips
    r = Report(design.name)
    for net in sorted(design.supply_nets(), key=lambda n: n.id):
        rule = f"volts/{net.id}"
        src = None
        if net.id in declared:
            (lo, hi), q, c = declared[net.id]
            src = (lo, hi, q, c, "declared by the design")
        else:
            for t in net.terminals:
                pr = getattr(t, "provision", None)
                if pr is None:
                    continue
                raw = pr.raw or {}
                if pr.nominal_v is not None:
                    src = (pr.nominal_v, pr.nominal_v, pr.quote or pr.nominal_v_basis,
                           pr.cite or f"parts[{t.part}].provides[{pr.name}]",
                           f"{t.owner} ({t.part}) provision nominal_v")
                    break
                if raw.get("v_min") is not None and raw.get("v_max") is not None:
                    # a provision that states a BAND and no nominal (the pack)
                    src = (float(raw["v_min"]), float(raw["v_max"]),
                           pr.quote or raw.get("v_range_cite", ""),
                           raw.get("v_range_cite") or pr.cite
                           or f"parts[{t.part}].provides[{pr.name}]",
                           f"{t.owner} ({t.part}) provision v_min..v_max")
                    break
        sinks = [t for t in net.sinks() if t.owner_kind == "part"] + \
                [t for t in net.terminals if t.owner_kind == "host"
                 and t.direction == "input"]
        if not sinks:
            continue
        if src is None:
            why = ""
            for t in net.terminals:
                pr = getattr(t, "provision", None)
                if pr is not None and pr.nominal_v_basis:
                    why = pr.nominal_v_basis
            r.findings.append(Finding(
                CD, rule, "source",
                f"{len(sinks)} sink(s) on {net.id} and no stated voltage: no "
                f"provision on this net states a nominal_v and the design "
                f"declares no band.",
                why or "nominal_v: null", f"electronics/netlist.py declared / "
                f"parts[].provides[].nominal_v_basis"))
            continue
        lo, hi, q, c, how = src
        for t in sinks:
            band = _sink_band(t, cs)
            where = f"{t.owner}.{t.ref}"
            if band is None:
                nd = t.need
                typ = (nd.raw.get("v_typ") if nd is not None else None)
                if typ is not None and lo == hi == float(typ):
                    r.findings.append(Finding(
                        PASS, rule, where,
                        f"{net.id} is {lo} V ({how}); {t.owner}'s {t.ref} states "
                        f"a typical of {typ} V and no band — equal, so PASS on "
                        f"the one number both sides state."))
                    continue
                r.findings.append(Finding(
                    CD, rule, where,
                    f"{net.id} is {lo}..{hi} V ({how}); {t.owner} ({t.part or design.host.slug}) "
                    f"states no v_min/v_max for {t.ref}.",
                    (nd.quote if nd is not None and nd.quote else "no band stated"),
                    (nd.cite if nd is not None and nd.cite else "parts[].requires[]")))
                continue
            blo, bhi, bq, bc = band
            if blo <= lo and hi <= bhi:
                r.findings.append(Finding(
                    PASS, rule, where,
                    f"{net.id} is {lo}..{hi} V ({how}); {t.owner}'s {t.ref} band "
                    f"is {blo}..{bhi} V."))
            else:
                r.findings.append(Finding(
                    FAIL, rule, where,
                    f"{net.id} is {lo}..{hi} V ({how}); {t.owner} ({t.part}) "
                    f"states {blo}..{bhi} V for {t.ref}.\nSource: \"{q}\" ({c})",
                    bq or f"{blo}..{bhi} V", bc))
    r.print(verbose, "\n--- volts: declared rail vs each sink's stated band ---")
    return r


def published_ids():
    """(ids, imu_id, cite) read out of model.rs, or None if it is not there."""
    if not os.path.isfile(MODEL_RS):
        return None
    txt = open(MODEL_RS).read()
    m = re.search(r"pub const JOINT_IDS: \[u8; NUM_JOINTS\] = \[(.*?)\];", txt, re.S)
    imu = re.search(r"pub const IMU_DXL_ID: u8 = (\d+);", txt)
    if not m or not imu:
        return None
    body = re.sub(r"//[^\n]*", "", m.group(1))
    ids = [int(x) for x in re.findall(r"\d+", body)]
    return ids, int(imu.group(1)), "research/raw/duck-control_src_model.rs:15-19, 78"


def check_bus_ids(design, verbose=False):
    """The IDs this design puts on dxl/DATA vs the runtime's, and the range
    the vendor allows. Uniqueness is cecad's rule (check_buses); this one
    asks what cecad cannot: are they the PUBLISHED ids, and legal ones."""
    r = Report(design.name)
    net = design.net("dxl/DATA")
    ids = {}
    for t in (net.terminals if net else ()):
        if t.owner_kind == "part" and t.address is not None:
            ids.setdefault(int(t.address), []).append(t.owner)
    q_range = "ID | RW | 1 | 0 ~ 252"
    c_range = "chips[XL330-M288-T].bus_id (E1 §Control Table); §ID(7): '254(0xFE) is occupied as a broadcast ID'"
    bad = [i for i in ids if not 0 <= i <= 252]
    if bad:
        r.findings.append(Finding(FAIL, "dxl/ids", "range",
                                  f"ID(s) outside 0..252 on the bus: {bad}.",
                                  q_range, c_range))
    else:
        r.findings.append(Finding(PASS, "dxl/ids", "range",
                                  f"{len(ids)} ID(s) on dxl/DATA, all within 0..252 "
                                  f"and none the broadcast ID 254: "
                                  f"{sorted(ids)}."))
    pub = published_ids()
    if pub is None:
        r.findings.append(Finding(
            CD, "dxl/ids", "published",
            f"{MODEL_RS} is not readable, so the design's IDs cannot be compared "
            f"with the runtime's.", "JOINT_IDS", "research/raw/duck-control_src_model.rs"))
    else:
        want = set(pub[0]) | {pub[1]}
        have = set(ids)
        if want == have and all(len(v) == 1 for v in ids.values()):
            r.findings.append(Finding(
                PASS, "dxl/ids", "published",
                f"the {len(have)} IDs on dxl/DATA are exactly JOINT_IDS + IMU_DXL_ID "
                f"read from {pub[2]}: {sorted(have)}."))
        else:
            r.findings.append(Finding(
                FAIL, "dxl/ids", "published",
                f"design has {sorted(have)}; model.rs states {sorted(want)}"
                + (f"; duplicated: {[i for i, v in ids.items() if len(v) > 1]}"
                   if any(len(v) > 1 for v in ids.values()) else ""),
                "pub const JOINT_IDS: [u8; NUM_JOINTS] = [ 20, 21, 22, 23, 24, // "
                "left leg 30, 31, 32, 33, 34, // neck, head, mouth 10, 11, 12, 13, "
                "14, // right leg ];", pub[2]))
    r.print(verbose, "\n--- dxl/ids: the bus IDs vs model.rs and the vendor range ---")
    return r


def overlay_addresses():
    """I2C3 addresses the deploy overlays and tofd name, read by regex."""
    out, cites = {}, {}
    if os.path.isfile(AIC_DTS):
        m = re.search(r"codec@([0-9a-f]+)\s*\{[^}]*?reg = <0x([0-9a-f]+)>", open(AIC_DTS).read(), re.S)
        if m:
            out["codec"] = int(m.group(2), 16)
            cites["codec"] = f"research/raw/deploy_audio_aic3104-i2c3.dts 'codec@{m.group(1)}' / 'reg = <0x{m.group(2)}>'"
    if os.path.isfile(I2C3_DTS):
        m = re.search(r"BMI088 0x([0-9a-f]+)/0x([0-9a-f]+)", open(I2C3_DTS).read())
        if m:
            out["bmi088.accel"], out["bmi088.gyro"] = int(m.group(1), 16), int(m.group(2), 16)
            cites["bmi088"] = f"research/raw/deploy_audio_i2c3-pihat.dts:11 'dormant BMI088 0x{m.group(1)}/0x{m.group(2)}'"
    if os.path.isfile(TOF_RS):
        m = re.search(r"ADDRESS_CANDIDATES: \[u8; 2\] = \[0x([0-9a-f]+), 0x([0-9a-f]+)\]", open(TOF_RS).read())
        if m:
            out["tof"] = int(m.group(1), 16)
            cites["tof"] = f"research/raw/tof_src_main.rs:87 'ADDRESS_CANDIDATES: [u8; 2] = [0x{m.group(1)}, 0x{m.group(2)}]'"
    return out, cites


def check_i2c3_vs_overlay(design, verbose=False):
    """The I2C3 address set of the netlist == the set Pollen's overlays name."""
    r = Report(design.name)
    want, cites = overlay_addresses()
    have = {}
    for g in design.bus_groups("I2C"):
        if g["id"] == "i2c3":
            for owner, addr in g["devices"]:
                if addr:
                    have[owner] = int(str(addr), 16)
    if len(want) < 4:
        r.findings.append(Finding(
            CD, "i2c3/overlay", "sources",
            f"only {sorted(want)} could be read from the deploy files under "
            f"research/raw; the comparison needs codec, BMI088 x2 and ToF.",
            "codec@18", "research/raw/deploy_audio_aic3104-i2c3.dts"))
    elif set(want.values()) == set(have.values()):
        r.findings.append(Finding(
            PASS, "i2c3/overlay", "addresses",
            f"i2c3 carries {sorted(hex(a) for a in have.values())} = the overlay's "
            f"{sorted(hex(a) for a in want.values())}: " + "; ".join(cites.values())))
    else:
        r.findings.append(Finding(
            FAIL, "i2c3/overlay", "addresses",
            f"i2c3 carries {sorted(hex(a) for a in have.values())}; the overlays "
            f"name {sorted(hex(a) for a in want.values())}.",
            "codec 0x18, dormant BMI088 0x19/0x68, ToF via Stemma J5",
            "research/raw/deploy_audio_i2c3-pihat.dts:11"))
    r.print(verbose, "\n--- i2c3/overlay: the netlist's addresses vs Pollen's device tree ---")
    return r


def _pairs(nets):
    """{(ownerA.ref, ownerB.ref)} for every two part terminals on one net."""
    out = set()
    for n in nets:
        terms = sorted(f"{t['owner']}.{t['ref']}" for t in n["terminals"]
                       if t["owner_kind"] == "part")
        for i in range(len(terms)):
            for j in range(i + 1, len(terms)):
                out.add((terms[i], terms[j]))
    return out


def check_against_wiring_lane(design, path=WIRING_NETS, verbose=False):
    """Two lanes, one robot. wiring/designs/microduck/nets.json was derived
    by the rung-5 lane from ITS design; this netlist was written from the
    documents. For every pair of part terminals both designs know, the two
    must agree on whether the pair shares a net."""
    r = Report(design.name)
    if not os.path.isfile(path):
        r.findings.append(Finding(
            CD, "cross/wiring", "nets.json",
            f"{os.path.relpath(path, REPO)} is not there; nothing to compare.",
            "wiring/ + bin/wire check", "GOAL.md rung 5"))
        r.print(verbose, "\n--- cross/wiring ---")
        return r
    theirs = json.load(open(path))["nets"]
    mine = [{"terminals": [{"owner": t.owner, "ref": t.ref, "owner_kind": t.owner_kind}
                           for t in n.terminals]} for n in design.nets()]
    tt = {f"{t['owner']}.{t['ref']}" for n in theirs for t in n["terminals"]
          if t["owner_kind"] == "part"}
    mt = {f"{t.owner}.{t.ref}" for n in design.nets() for t in n.terminals
          if t.owner_kind == "part"}
    common = tt & mt
    pa, pb = _pairs(theirs), _pairs(mine)
    disagree = []
    cl = sorted(common)
    for i in range(len(cl)):
        for j in range(i + 1, len(cl)):
            k = (cl[i], cl[j])
            if (k in pa) != (k in pb):
                disagree.append(f"{k[0]} -- {k[1]}: wiring says "
                                f"{'same' if k in pa else 'different'} net, "
                                f"this netlist says {'same' if k in pb else 'different'}")
    n_pairs = len(cl) * (len(cl) - 1) // 2
    if disagree:
        r.findings.append(Finding(
            FAIL, "cross/wiring", "connectivity",
            f"{len(disagree)} of {n_pairs} terminal pair(s) shared by both designs "
            f"disagree:\n  " + "\n  ".join(disagree[:12]),
            "nets.json", os.path.relpath(path, REPO)))
    else:
        r.findings.append(Finding(
            PASS, "cross/wiring", "connectivity",
            f"{len(common)} terminal(s) are in both designs ({len(mt - tt)} only "
            f"here: {', '.join(sorted(mt - tt)[:8])}{'...' if len(mt - tt) > 8 else ''}); "
            f"all {n_pairs} pair(s) agree on same-net / different-net."))
    r.print(verbose, "\n--- cross/wiring: this netlist vs the wiring lane's nets.json ---")
    return r


def check_all(design, verbose=False):
    rep = design.check(verbose=False)
    for fn in (check_supply_bands, check_bus_ids, check_i2c3_vs_overlay,
               check_against_wiring_lane):
        rep += fn(design, verbose=False)
    if verbose:
        rep.print(True, design._header() + "  + volts, dxl/ids, i2c3/overlay, "
                  "cross/wiring", group_pass=False)
    return rep


# --------------------------------------------------------------------------
# the report
# --------------------------------------------------------------------------
def _capture(fn, *a, **k):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fn(*a, **k)
    return buf.getvalue()


def write_report(design, rep, path):
    by_rule = {}
    for f in rep.findings:
        by_rule.setdefault(f.rule, {PASS: 0, FAIL: 0, CD: 0})[f.verdict] += 1
    lines = []
    w = lines.append
    w("# Microduck netlist — three-verdict report")
    w("")
    w(f"*Generated {time.strftime('%Y-%m-%d %H:%M')} by `electronics/netlist.py` "
      f"(GOAL.md rung 4). Host `{design.host.slug}` ({design.host.controller}), "
      f"{len(design.placements)} parts, {len(design.nets())} nets, "
      f"{len(rep.findings)} findings. Nothing here was measured on a robot; every "
      f"figure is a quote from the file its cite names.*")
    w("")
    w(f"## Verdict: **{rep.verdict}**")
    w("")
    w(f"{len(rep.passed)} PASS · {len(rep.failed)} FAIL · {len(rep.undetermined)} "
      f"CANNOT DETERMINE. `bool(report)` is False on either of the last two — the "
      f"conservative answer.")
    w("")
    w("| rule | PASS | FAIL | CANNOT DETERMINE |")
    w("|---|---|---|---|")
    for rule in sorted(by_rule):
        c = by_rule[rule]
        w(f"| `{rule}` | {c[PASS]} | {c[FAIL]} | {c[CD]} |")
    w("")
    w("## The FAILs — what the published design contradicts")
    w("")
    if not rep.failed:
        w("none.")
    grouped = {}
    for f in rep.failed:
        grouped.setdefault((f.rule, f.quote, f.cite), []).append(f)
    for (rule, quote, cite), fs in grouped.items():
        wheres = ", ".join(f.where for f in fs)
        w(f"- **`{rule}`** × {len(fs)} — {wheres}")
        w(f"  - {fs[0].message.splitlines()[0]}")
        if quote:
            w(f"  - \"{quote}\" ({cite})")
    w("")
    w("The SERVO_V FAIL is the design AS PUBLISHED against the vendor band: "
      "model.rs reads 6.6–8.2 V through the servos' own Present Input Voltage "
      "register and the XL330-M288-T's input band is 3.7–6.0 V (docs/"
      "ELECTRONICS-AND-SOFTWARE.md §3.4, open question 1). It is not a wiring "
      "error in this netlist; what settles it is a meter on a production servo's "
      "VDD pin, or Pollen naming a regulated bus or a custom variant. The checks "
      "this rung asked for — one controller per bus, unique I2C3 addresses "
      "(0x18/0x19/0x68/0x29), unique bus IDs (10–14, 20–24, 30–34, 200), no pin "
      "on two nets — PASS above.")
    w("")
    w("## The CANNOT DETERMINEs — by name, with what settles each")
    w("")
    for f in rep.undetermined:
        w(f"- **`{f.rule}` {f.where}** — {f.message.splitlines()[0]}")
    w("")
    w("What settles the ones that matter: the Robot HAT schematic (regulators, "
      "transceiver, rails, connectors) — Pollen publishing it or a teardown; a "
      "meter on a servo's VDD pin for the 6.6-8.2 V question; the dts pinctrl "
      "for the I2S3 mux; `i2cdetect -y 3` on a production HAT for the BMI088.")
    w("")
    w("## Nets")
    w("")
    w("```")
    w(design.netlist().table())
    w("```")
    w("")
    w("## Every finding, in full")
    w("")
    w("```")
    w(_capture(rep.print, True, design._header(), group_pass=False))
    w("```")
    w("")
    w("## ce-elec")
    w("")
    code, line = elec_probe()
    w(f"`bin/elec gpio electronics/elec-spec.json` → exit {code}: `{line}`")
    w("")
    w("ce-elec's solvers assign pins over a roster in cecad/data/controllers.json; "
      "there is no RK3566 roster, so `gpio` and `levels` refuse — the honest "
      "answer for a host whose pins Pollen's overlays already fixed. `bin/elec "
      "doctor` reports the toolchain present. The netlist above is the design; "
      "the spec is kept as the probe that records this refusal.")
    w("")
    w("## Sources")
    w("")
    w("- `ce-parts/radxa-zero-3w/electrical.host.json` — Radxa ZERO 3W Product "
      "Brief RAD-DOC-0084 Rev 1.10, schematic V1.12, docs.radxa.com hardware-"
      "interface page (fetched 2026-09-02)")
    w("- `ce-parts/xl330-m288-t`, `lsm6dsv16x`, `tlv320aic3104`, `bmi088`, "
      "`vl53l5cx`, `vl53l8cx`, `imx219`, `np-f550` — vendor datasheets, "
      "quoted verbatim, sha256 in each PROVENANCE.json")
    w("- `research/raw/duck-control_src_model.rs` (JOINT_IDS, IMU_DXL_ID, "
      "BATTERY_FULL_V/EMPTY_V), `deploy_audio_i2c3-pihat.dts`, "
      "`deploy_audio_aic3104-i2c3.dts`, `tof_src_main.rs`, `deploy_robotd.toml` "
      "— Pollen's Apache-2.0 sources")
    w("- `docs/ELECTRONICS-AND-SOFTWARE.md` — the synthesis every note above cites")
    w("- `wiring/designs/microduck/nets.json` — the rung-5 lane's derived nets, "
      "cross-checked here")
    w("")
    w("## How to re-run and how to break it")
    w("")
    w("```")
    w("python3 electronics/netlist.py             # exit 0 PASS · 2 FAIL · 3 CANNOT DETERMINE")
    w("python3 electronics/netlist.py --self-test # two servos at ID 10 -> FAIL; gyro at 0x18 -> FAIL;")
    w("                                           # SERVO_V 4.8-5.5 V -> PASS, unstated -> CANNOT DETERMINE;")
    w("                                           # host unpowered -> FAIL; HAT pass-throughs left on the bus -> CANNOT DETERMINE")
    w("```")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    return path


def elec_probe():
    """(exit code, first line) of `bin/elec gpio electronics/elec-spec.json`,
    run over the same shelf union — or (None, why) when the tool is absent."""
    import subprocess
    elec = next((os.path.join(r, "ce-elec", "bin", "elec") for r in triad_roots()
                 if os.path.isfile(os.path.join(r, "ce-elec", "bin", "elec"))), None)
    spec = os.path.join(HERE, "elec-spec.json")
    if elec is None or not os.path.isfile(spec):
        return None, "ce-elec/bin/elec or electronics/elec-spec.json not found — CANNOT DETERMINE"
    try:
        p = subprocess.run([elec, "gpio", spec], capture_output=True, text=True,
                           timeout=120, env=dict(os.environ, CE_PARTS_ROOT=UNION))
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, f"could not run: {e}"
    text = [l for l in (p.stdout + p.stderr).splitlines()
            if l.strip() and not l.startswith("[live capture")
            and "Run designs through" not in l and "kernel-free" not in l]
    return p.returncode, (text[0] if text else "(no output)")


def write_derived(design, rep):
    out = {}
    out["netlist"] = N.netlist_json(design, os.path.join(HERE, "netlist.json"))
    doc = G.to_graph(design, id="microduck",
                     title="Microduck — the robot netlist (electronics/netlist.py)")
    with open(os.path.join(HERE, "netlist.graph.json"), "w") as fh:
        json.dump(doc, fh, indent=1)
    out["graph"] = os.path.join(HERE, "netlist.graph.json")
    out["firmware"] = N.firmware_json(design, os.path.join(HERE, "firmware.json"),
                                      ignore_failures=True)
    with open(os.path.join(HERE, "report.json"), "w") as fh:
        json.dump({"design": design.name, "host": design.host.slug,
                   "verdict": rep.verdict,
                   "counts": {PASS: len(rep.passed), FAIL: len(rep.failed),
                              CD: len(rep.undetermined)},
                   "findings": [dataclasses.asdict(f) for f in rep.findings],
                   "notes": list(rep.notes),
                   "shelf_union": UNION, "generated": time.strftime("%Y-%m-%d %H:%M:%S")},
                  fh, indent=1)
    out["report.json"] = os.path.join(HERE, "report.json")
    return out


# --------------------------------------------------------------------------
# break it on purpose
# --------------------------------------------------------------------------
def self_test():
    ok = True

    def expect(name, cond, detail=""):
        nonlocal ok
        print(f"  [{'ok' if cond else 'FAILED'}] {name}" + (f" — {detail}" if detail else ""))
        ok = ok and cond

    print("=== netlist self-test: every check broken on purpose ===")
    base = electrical_design()
    rep = check_all(base)
    bus = base.check_buses(verbose=False)
    expect("baseline: I2C address rule ran and PASSed",
           any(f.rule == "i2c" and f.verdict == PASS and "address" in f.message
               for f in bus.findings),
           "; ".join(f"{f.where}" for f in bus.findings if f.rule == "i2c"))
    expect("baseline: UART (dxl) address rule ran and PASSed",
           any(f.rule == "uart" and f.verdict == PASS and "16 device(s)" in f.message
               for f in bus.findings))
    expect("baseline: SERVO_V vs XL330 band is FAIL (6.6-8.2 V vs 3.7-6.0 V)",
           sum(1 for f in rep.findings if f.rule == "volts/SERVO_V" and f.verdict == FAIL) == 15)

    ids = [s[0] for s in SERVOS]
    ids[ids.index(20)] = 10                          # two servos at ID 10
    dup = electrical_design(ids=ids)
    r2 = dup.check_buses(verbose=False)
    expect("two servos at ID 10 -> check_buses FAIL",
           any(f.rule == "uart" and f.verdict == FAIL for f in r2.findings))
    r2b = check_bus_ids(dup)
    expect("two servos at ID 10 -> dxl/ids FAIL (not the published set)",
           any(f.verdict == FAIL for f in r2b.findings))

    gy = electrical_design(gyro_addr="0x18")         # gyro on the codec's address
    r3 = gy.check_buses(verbose=False)
    expect("BMI088 gyro at 0x18 -> I2C FAIL naming the codec",
           any(f.rule == "i2c" and f.verdict == FAIL and "codec" in f.message
               for f in r3.findings))
    r3b = check_i2c3_vs_overlay(gy)
    expect("BMI088 gyro at 0x18 -> i2c3/overlay FAIL",
           any(f.verdict == FAIL for f in r3b.findings))

    r4 = check_supply_bands(base, declared={"SERVO_V": ((4.8, 5.5), "test", "test")})
    expect("SERVO_V declared 4.8-5.5 V -> servo band PASS",
           sum(1 for f in r4.findings if f.rule == "volts/SERVO_V" and f.verdict == PASS) == 15)
    r5 = check_supply_bands(base, declared={})
    expect("SERVO_V undeclared and provision nominal null -> CANNOT DETERMINE",
           any(f.rule == "volts/SERVO_V" and f.verdict == CD and f.where == "source"
               for f in r5.findings))

    unp = electrical_design(power_the_host=False)
    r6 = unp.check_host_power(verbose=False)
    expect("host not powered -> check_host_power FAIL",
           any(f.verdict == FAIL for f in r6.findings))

    keep = electrical_design(hat_keep_bus=True)
    r7 = keep.check_buses(verbose=False)
    expect("HAT pass-throughs left as bus endpoints -> a no-address CANNOT DETERMINE on hat",
           any(f.verdict == CD and f.where.startswith("hat") for f in r7.findings),
           "the reason the design wires a bus-None view (docstring item 3)")

    tmp = os.path.join(HERE, ".selftest-nets.json")
    try:
        doc = json.load(open(WIRING_NETS))
        for n in doc["nets"]:
            for t in n["terminals"]:
                if t["owner"] == "id10" and t["ref"] == "DATA":
                    t["ref"] = "VDD"                  # ID 10's DATA moved onto SERVO_V
        json.dump(doc, open(tmp, "w"))
        r8 = check_against_wiring_lane(base, path=tmp)
        expect("wiring nets.json with id10.DATA moved onto SERVO_V -> cross/wiring FAIL",
               any(f.verdict == FAIL for f in r8.findings))
    except FileNotFoundError:
        expect("cross/wiring with no nets.json -> CANNOT DETERMINE",
               any(f.verdict == CD for f in check_against_wiring_lane(base, path=tmp).findings))
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    print("=== self-test:", "PASS" if ok else "FAIL", "===")
    return 0 if ok else 1


# --------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    d = electrical_design()
    rep = check_all(d, verbose=not a.quiet)
    print(f"\n  shelf union: {UNION}")
    print(f"  {d.name}: {rep.verdict} — {len(rep.passed)} PASS, {len(rep.failed)} FAIL, "
          f"{len(rep.undetermined)} CANNOT DETERMINE over {len(rep.findings)} findings")
    if not a.no_write:
        p = write_report(d, rep, os.path.join(HERE, "netlist-report.md"))
        files = write_derived(d, rep)
        print(f"  wrote {os.path.relpath(p, REPO)}")
        for k, v in files.items():
            print(f"  wrote {os.path.relpath(v, REPO)}")
    return EXIT[rep.verdict]


if __name__ == "__main__":
    sys.exit(main())
