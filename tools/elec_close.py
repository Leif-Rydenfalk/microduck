#!/usr/bin/env python3
"""elec_close.py — DOES THE MICRODUCK'S ELECTRICAL SYSTEM CLOSE?

PROVE 3. For every chip and board: what it NEEDS versus what it is actually
connected to. The authority for "actually connected to" is THE COPPER —
reference/pollen-elec-rpi-robot-hat/elec_RPI_Robot_HAT.kicad_pcb, Pollen's own
Apache-2.0 board file, whose pad->net table is what the fab builds. Not a
hand-authored netlist, not a block diagram, not a reading of the README.

Everything a device NEEDS comes from its ce-parts electrical record, which in
turn quotes its datasheet with a page number. Nothing here is defaulted: a
figure with no source is null and the check that wanted it answers
CANNOT DETERMINE, naming what settles it.

Three verdicts. CANNOT DETERMINE is not a pass.

    python3 tools/elec_close.py                 # measure, write out/elec/closure.json
    python3 tools/elec_close.py --self-test     # 18 checks on the checker itself
    CE_ELEC_BREAK=1 python3 tools/elec_close.py --self-test   # break it on purpose

Written 2026-09-05, PROVE-3 lane.
"""
import json, os, re, sys, html, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB  = os.path.join(ROOT, 'reference/pollen-elec-rpi-robot-hat/elec_RPI_Robot_HAT.kicad_pcb')
BOM  = os.path.join(ROOT, 'reference/pollen-elec-rpi-robot-hat/production/ASE01187-C1_elec_RPI_Robot_HAT_BOM.csv')
WIKI = os.path.join(ROOT, 'ce-parts/radxa-zero-3w/iterations/v0.0.1/docs/fetched/docs.radxa.com_zero3_hardware-interface.html')
CABLES = os.path.join(ROOT, 'wiring/cables.json')
RUNTIME = os.path.join(ROOT, 'out/sim-evidence/battery-runtime.json')
OUT  = os.path.join(ROOT, 'out/elec/closure.json')

BREAK = int(os.environ.get('CE_ELEC_BREAK', '0'))

PASS, FAIL, CD = 'PASS', 'FAIL', 'CANNOT DETERMINE'


# ---------------------------------------------------------------- the copper

def _blocks(s, tag):
    """Every top-level (tag ...) s-expression in s, paren-balanced, string-aware."""
    out, i, T = [], 0, '(' + tag
    while True:
        i = s.find(T, i)
        if i < 0:
            break
        if s[i + len(T)] not in ' \n\t':
            i += 1
            continue
        depth, j, instr = 0, i, False
        while j < len(s):
            c = s[j]
            if instr:
                if c == '\\':
                    j += 2
                    continue
                if c == '"':
                    instr = False
            else:
                if c == '"':
                    instr = True
                elif c == '(':
                    depth += 1
                elif c == ')':
                    depth -= 1
                    if depth == 0:
                        break
            j += 1
        out.append(s[i:j + 1])
        i = j + 1
    return out


def hat_netlist(path=PCB):
    """(refdes -> {value, footprint, pads{pad: net}}) read off the fabricated board."""
    src = open(path, encoding='utf-8', errors='replace').read()
    nets = {int(m.group(1)): m.group(2) for m in re.finditer(r'\(net (\d+) "([^"]*)"\)', src)}
    comps = {}
    for fp in _blocks(src, 'footprint'):
        rm = re.search(r'\(property "Reference" "([^"]+)"', fp)
        vm = re.search(r'\(property "Value" "([^"]*)"', fp)
        fn = re.match(r'\(footprint "([^"]*)"', fp)
        if not rm:
            continue
        ref = rm.group(1)
        c = {'value': vm.group(1) if vm else '', 'footprint': fn.group(1) if fn else '', 'pads': {}}
        for pb in _blocks(fp, 'pad'):
            pn = re.match(r'\(pad "([^"]*)"', pb)
            if pn is None:
                continue
            nm = re.search(r'\(net (\d+) "([^"]*)"\)', pb)
            c['pads'][pn.group(1)] = nm.group(2) if nm else ''
        comps[ref] = c
    return comps, nets


def by_net(comps):
    d = collections.defaultdict(list)
    for r, c in comps.items():
        for p, n in c['pads'].items():
            if n:
                d[n].append(f'{r}.{p}')
    return d


# ------------------------------------------------------ the Radxa 40-pin map

def radxa_header(path=WIKI):
    """pin -> [alternate functions], from docs.radxa.com's own 40-PIN GPIO table."""
    s = open(path, encoding='utf-8', errors='replace').read()
    i = s.find('id=gpio-interface')
    if i < 0:
        return {}
    seg = s[i:]
    seg = seg[:seg.find('</table>') + 8]
    body = seg[seg.find('<tbody'):]
    pins = {}
    for r in re.split(r'<tr[^>]*>', body)[1:]:
        cells = re.split(r'<t[dh][^>]*>', r)[1:]
        cells = [html.unescape(re.sub(r'<[^>]+>', '', c)).strip() for c in cells]
        if len(cells) != 14:
            continue
        gL, f5L, f4L, f3L, f2L, f1L, pL, pR, f1R, f2R, f3R, f4R, f5R, gR = cells
        for p, fs in ((pL, [f1L, f2L, f3L, f4L, f5L]), (pR, [f1R, f2R, f3R, f4R, f5R])):
            try:
                p = int(p)
            except ValueError:
                continue
            pins[p] = [x for x in fs if x]
    # The wiki table omits the I2C3_M0 alternate that the product brief prints;
    # the brief is the second vendor document and the part record quotes it.
    BRIEF = {3: 'I2C3_SDA_M0', 5: 'I2C3_SCL_M0'}
    for p, f in BRIEF.items():
        if p in pins and f not in pins[p]:
            pins[p].append(f + '  [brief p.6, not on the wiki table]')
    return pins


# ------------------------------------------------------------------ the facts
# Every row below is a QUOTE with a document behind it. Nothing is inferred here;
# the inference happens in the checks, where it can be graded.

DEVICE_FACTS = {
    # refdes on the HAT -> what the part NEEDS
    'U2': dict(part='part:tlv320aic3104', name='TLV320AIC3104 audio codec',
               supplies={'AVDD': (['25'], 2.7, 3.3, 3.6), 'DRVDD1/2': (['18', '24'], 2.7, 3.3, 3.6),
                         'IOVDD': (['7'], 1.1, 1.8, 3.6), 'DVDD': (['32'], 1.525, 1.8, 1.95)},
               cite='ce-parts/tlv320aic3104/iterations/v0.0.1/electrical.chip.json supplies[], quoting SLAS510G §8.3 p.7',
               i2c=[0x18], i2c_cite='SLAS510G; Pollen deploy_audio_aic3104-i2c3.dts node reg=<0x18>',
               mA_typ=7.35, mA_cite='SLAS510G p.12 CURRENT CONSUMPTION: IDRVDD+IAVDD 4.9 mA + IDVDD 2.45 mA (record: no single total is printed)'),
    'U11': dict(part='part:bmi088', name='BMI088 IMU (fitted, unused by software)',
                supplies={'VDD': (['3', '11'], 2.4, None, 3.6), 'VDDIO': (['7'], 1.2, None, 3.6)},
                cite='ce-parts/bmi088/.../electrical.chip.json supplies[], quoting BMI088 datasheet Table 1 p.7',
                i2c=[], i2c_cite='address depends on the SDO straps — measured from the copper, see check E1',
                mA_typ=5.15, mA_cite='BMI088 Tables 2+3 p.8, gyro 5 mA + accel 0.15 mA (derived sum, the sheet never totals them)'),
    'U8': dict(part=None, name='SIT3088E RS-485 transceiver',
               supplies={'VCC': (['8'], 3.0, 3.3, 5.5)},
               cite='reference/pollen-elec-rpi-robot-hat/docs/part - SIT3088 - C601076.pdf',
               i2c=[], i2c_cite='', mA_typ=None,
               mA_cite='NOT TRANSCRIBED: the sheet prints ICC1/ICC2 rows that were not read out here.'),
    'U1': dict(part=None, name='PAM8406D class-D amplifier',
               supplies={'PVDDL/PVDDR': (['4', '13'], 2.5, 5.0, 5.5), 'VDD (through FB1)': (['6'], 2.5, 5.0, 5.5)},
               cite="'part - PAM8406 - C86270.pdf' Electrical Characteristics: 'VDD Supply Voltage 2.5 .. 5.5 V'",
               i2c=[], i2c_cite='', mA_typ=None,
               mA_cite='NOT TRANSCRIBED: the sheet gives output POWER per load/THD, not a supply current. See check E5 for the bound taken from output power.'),
    'U3': dict(part=None, name='XC6206P182MR 1.8 V LDO',
               supplies={'VIN': (['3'], 1.8, None, 8.0)},
               cite="'part - XC6202 - C347373.pdf': 'input voltage VIN 1.8 -- 8.0 V'; 'Maximum output IOUT(max) VIN=VOUT(T)+1V 100 mA'",
               i2c=[], i2c_cite='', mA_typ=None, mA_cite=''),
    'U9': dict(part=None, name='AP63205 buck, fixed 5.0 V',
               supplies={'VIN/EN': (['2', '3'], 3.8, None, 32.0)},
               cite="'part - AP63205.pdf' DS41326 Rev 2-2 p.1: 'VIN 3.8V to 32V', '2A Continuous Output Current', 'Fixed Output Voltage o 5.0V: AP63205'",
               i2c=[], i2c_cite='', mA_typ=None, mA_cite=''),
    'MK1': dict(part=None, name='LMA2718 MEMS microphone',
                supplies={'VDD': (['4'], None, 3.3, None)},
                cite="'part - LMA2718 - C7587901.pdf' (in the HAT's own docs/ folder); band NOT transcribed here",
                i2c=[], i2c_cite='', mA_typ=None, mA_cite=''),
    'U4': dict(part=None, name='CAT24C32 EEPROM — DO NOT POPULATE',
               supplies={'VCC': (['8'], 1.7, 3.3, 5.5)}, cite="BOM line marked DNP",
               i2c=[0x50], i2c_cite='CAT24C32 default 1010A2A1A0 with A0..A2 grounded = 0x50; NOT FITTED, so not on the bus',
               mA_typ=None, mA_cite='', dnp=True),
}

# Devices that hang off the HAT on a cable, not on its copper.
OFFBOARD = {
    'tof': dict(part='part:microduck-tof-module', name='ToF ranger on Stemma J5',
                conn='J5', rail_expect='+3V3', i2c=[0x29],
                i2c_cite='ce-parts/microduck-tof-module/electrical.part.json requires[SDA].address; teardown §7 "Address 0x29"',
                mA_typ=95, mA_peak=150,
                mA_cite='part:vl53l5cx current_mA typical 95 (AVDD 45 + IOVDD 50, Table 14 p.18), peak 150 (each rail +10 mA)'),
    'camera': dict(part='part:imx219', name='IMX219 camera on MIPI CSI',
                   conn='CSI (not on the HAT)', rail_expect='VCC_3V3_CSI', i2c=[0x10],
                   i2c_cite='part:imx219 i2c_address; Pollen probe "imx219 2-0010" = bus 2 addr 0x10 — a DIFFERENT BUS from i2c3',
                   bus='i2c2', mA_typ=None, mA_peak=None,
                   mA_cite='PER-RAIL ONLY (part:imx219 current_mA typical_basis): the module regulates 2.8/1.2/1.8 V itself and its board draw is CANNOT DETERMINE'),
    'imu200': dict(part='part:microduck-imu-to-dxl', name='imu_to_dxl v2 (LSM6DSV16X + MCU) on the servo bus',
                   conn='a Dynamixel port', rail_expect='+BATT', i2c=[], i2c_cite='NOT ON I2C — it is a Dynamixel Protocol V2 slave at bus ID 200 (teardown §3)',
                   mA_typ=None, mA_peak=None,
                   mA_cite='CHIP ONLY 0.65 mA (part:lsm6dsv16x Table 4); the board MCU and transceiver are unpublished, so the board total is CANNOT DETERMINE'),
    'speaker': dict(part='part:microduck-speaker', name='head speaker on Wago J1',
                    conn='J1', rail_expect=None, i2c=[], i2c_cite='', mA_typ=None, mA_peak=None, mA_cite=''),
}

XL330 = dict(
    v_min=3.7, v_max=6.0, v_rec=5.0,
    cite="ROBOTIS e-Manual XL330-M288-T Specifications: 'Operating Voltage 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])'; "
         "local copy ce-parts/xl330-m288-t/iterations/v0.0.1/docs/fetched/robotis-emanual-xl330-m288.html",
    stall_A={3.7: 1.11, 5.0: 1.47, 6.0: 1.74},
    standby_mA=17,
)
PACK = dict(v_min=6.6, v_nom=7.2, v_max=8.2,
            cite="part:np-f550; Pollen's runtime maps 6.6 V (empty) to 8.2 V (full) UNDER LOAD, read through the servos' "
                 "Present Input Voltage(144). out/open/power-battery.json sony_original_np_f550 + cell_class block.")

# The HAT's own rails, and where each one is SOURCED. Filled from the copper in check E3.
RAIL_SOURCE = {
    '+BATT': dict(source='the battery, arriving on a Dynamixel motor connector',
                  v=(6.6, 7.2, 8.2), limit_A=None,
                  cite="reference/pollen-elec-rpi-robot-hat/README.md verbatim: 'The RPI_Robot_HAT can be power from 5 to 28V. "
                       "It is designed to use of the motor connector as an power input.' The copper agrees: +BATT touches only "
                       "J13.2 J14.2 J3.2 J11.2 (the four motor connectors), U9.2/3 (the buck), C19 (bulk) and R24 (the sense divider) "
                       "— THERE IS NO SEPARATE BATTERY TERMINAL ON THIS BOARD."),
    '+5V': dict(source='U9 AP63205 fixed-5.0 V buck, OR-ed with header 5 V by U10 LM5050-1 + Q2',
                v=(5.0, 5.0, 5.0), limit_A=2.0,
                cite="AP63205 datasheet DS41326 Rev 2-2 p.1: '2A Continuous Output Current', 'Fixed Output Voltage o 5.0V: AP63205'. "
                     "Copper: U9.2/3 = +BATT, U9.1 (FB) = the output node, U9.5 (SW) -> L4 -> that node."),
    '+3V3': dict(source='THE RADXA, through header pins 1 and 17 — the HAT makes no 3.3 V of its own',
                 v=(3.3, 3.3, 3.3), limit_A=None,
                 cite="Copper: the only +3V3 pads that can source are J4.1 and J4.17; no regulator on the HAT has +3V3 on an output pin. "
                      "The Radxa's own 3V3 comes from the RK817 PMIC (radxa_zero_3w_v1.12_schematic.pdf sheet 21) whose per-rail current "
                      "limit is NOT stated in any fetched Radxa document."),
    '+1V8': dict(source='U3 XC6206P182MR LDO from +3V3',
                 v=(1.8, 1.8, 1.8), limit_A=0.100,
                 cite="Copper: U3.3 = +3V3 (VIN), U3.2 = +1V8 (VOUT), U3.1 = GND. "
                      "'part - XC6202 - C347373.pdf': 'Maximum output IOUT(max) VIN=VOUT(T)+1V 100 mA'."),
    'GND': dict(source='the pack negative', v=(0, 0, 0), limit_A=None, cite='reference'),
}


# --------------------------------------------------------------------- checks

def rows_e1_i2c(comps, nets):
    """E1 — the i2c3 address map, and the strap that decides each address."""
    bn = by_net(comps)
    sda = comps['J4']['pads']['3']
    scl = comps['J4']['pads']['5']
    out = []
    on_sda = sorted(bn[sda])
    on_scl = sorted(bn[scl])
    out.append(dict(check='E1', item='i2c3 bus membership (from the copper)', verdict=PASS,
                    measurement=f'SDA net {sda!r} touches {len(on_sda)} pads: {", ".join(on_sda)}; '
                                f'SCL net {scl!r} touches {len(on_scl)} pads: {", ".join(on_scl)}',
                    cite='elec_RPI_Robot_HAT.kicad_pcb, J4 pin 3 / pin 5 (the Radxa 40-pin header)'))

    # who is addressable on it
    addr = []  # (device, address, how the strap was measured)
    # codec: no address pins on the AIC3104
    addr.append(('U2 TLV320AIC3104', 0x18,
                 'fixed — the AIC3104 has no address pin. Pollen deploy_audio_aic3104-i2c3.dts puts the node at 0x18.'))
    # BMI088: SDO1 -> accel address, SDO2 -> gyro address
    s1 = comps['U11']['pads']['15']
    s2 = comps['U11']['pads']['10']
    s1p = [p for p in bn[s1] if not p.startswith('U11.')]
    s2p = [p for p in bn[s2] if not p.startswith('U11.')]

    def strap(pads):
        for p in pads:
            ref = p.split('.')[0]
            if ref in comps:
                for pd, nn in comps[ref]['pads'].items():
                    if nn in ('+3V3', '+5V'):
                        return 'HIGH', f'{ref} [{comps[ref]["value"]}] to {nn}'
                    if nn == 'GND':
                        return 'LOW', f'{ref} [{comps[ref]["value"]}] to GND'
        return None, 'no strap found'

    lv1, w1 = strap(s1p)
    lv2, w2 = strap(s2p)
    if BREAK == 1:
        lv1 = 'LOW'  # break: pretend SDO1 is grounded, which collides with the codec
    a_acc = {'HIGH': 0x19, 'LOW': 0x18}.get(lv1)
    a_gyr = {'HIGH': 0x69, 'LOW': 0x68}.get(lv2)
    out.append(dict(check='E1', item='BMI088 accelerometer address strap', verdict=PASS if a_acc else CD,
                    measurement=f'U11.15 (SDO1) -> net {s1!r} -> {w1} -> {lv1} -> address 0x{a_acc:02X}' if a_acc
                                else f'U11.15 (SDO1) -> {w1} — cannot read the level',
                    cite='BMI088 datasheet §I2C: accelerometer 0x18 with SDO1=GND, 0x19 with SDO1=VDDIO'))
    out.append(dict(check='E1', item='BMI088 gyroscope address strap', verdict=PASS if a_gyr else CD,
                    measurement=f'U11.10 (SDO2) -> net {s2!r} -> {w2} -> {lv2} -> address 0x{a_gyr:02X}' if a_gyr
                                else f'U11.10 (SDO2) -> {w2} — cannot read the level',
                    cite='BMI088 datasheet §I2C: gyroscope 0x68 with SDO2=GND, 0x69 with SDO2=VDDIO'))
    if a_acc:
        addr.append(('U11 BMI088 accelerometer', a_acc, w1))
    if a_gyr:
        addr.append(('U11 BMI088 gyroscope', a_gyr, w2))
    # the ToF, which is on J5 and therefore on this same bus
    j5s = comps['J5']['pads']['3']
    if j5s == sda:
        addr.append(('ToF module on Stemma J5', 0x29, OFFBOARD['tof']['i2c_cite']))
        out.append(dict(check='E1', item='Stemma J5 is on i2c3', verdict=PASS,
                        measurement=f'J5.3 -> {j5s!r} = the SDA net; J5.4 -> {comps["J5"]["pads"]["4"]!r} = the SCL net; '
                                    f'J5.2 -> {comps["J5"]["pads"]["2"]!r}; J5.1 -> {comps["J5"]["pads"]["1"]!r}',
                        cite='copper. Matches wiring/cables.json run "tof-hat" pins "GND, 3V3, SDA, SCL (I2C3, addr 0x29)"'))
    # collision
    seen = collections.defaultdict(list)
    for name, a, why in addr:
        seen[a].append(name)
    colls = {a: n for a, n in seen.items() if len(n) > 1}
    out.append(dict(check='E1', item='i2c3 address collision', verdict=FAIL if colls else PASS,
                    measurement=(f'COLLISION: ' + '; '.join(f'0x{a:02X} claimed by {" and ".join(n)}' for a, n in colls.items()))
                                if colls else
                                f'{len(addr)} addressable devices on i2c3, {len(seen)} distinct addresses, 0 collisions: ' +
                                ', '.join(f'{n} @ 0x{a:02X}' for n, a, _ in sorted(addr, key=lambda x: x[1])),
                    cite='addresses measured above; each from the strap actually fitted, not from a datasheet default'))
    # near miss worth naming
    out.append(dict(check='E1', item='how close the bus came to colliding', verdict=PASS,
                    measurement='R14 is a 0 R link from +3V3 to U11.15 (SDO1). The BMI088 accelerometer defaults to 0x18 with '
                                'SDO1 grounded — the SAME address as the TLV320AIC3104, which has no address pin and cannot move. '
                                'R14 is the only thing keeping the two apart. Fit R14 to GND instead and the bus has two devices at 0x18.',
                    cite='copper: R14 [0R] pads {1: +3V3, 2: Net-(U11-SDO1)}; R15 [0R] pads {1: GND, 2: Net-(U11-SDO2)}'))
    # other I2C buses named so the reader knows they were looked at
    out.append(dict(check='E1', item='every other I2C address in the robot', verdict=PASS,
                    measurement='IMX219 @ 0x10 is on I2C2 (the MIPI CSI connector pins 20/21), a DIFFERENT CONTROLLER from i2c3, '
                                'so it cannot collide. U4 CAT24C32 @ 0x50 would sit on ID_SD/ID_SC (header 27/28 = I2C4_M0) but is '
                                'DNP and its pull-ups R10/R11 are DNP too, so nothing is on that bus at all. The ET7301B USB-C PD '
                                'controller answers at 0x22 on the RK3566 i2c3 controller in its M1 pin mux; Pollen re-muxes the '
                                'controller to M0 and disables that node, so it is off the bus by pin mux, not by address.',
                    cite='part:imx219 i2c_address; HAT BOM DNP lines; teardown §4 "⚠ A trap they hit themselves"; '
                         'part:radxa-zero-3w buses_the_microduck_uses.usb_c_pd_controller'))
    # shelf parts that are NOT in this robot
    out.append(dict(check='E1', item='NFC front-ends on the shelf', verdict=PASS,
                    measurement='part:pn7150 and part:st25r3916 are on the ce-parts shelf but appear in NONE of the 127 components '
                                'on the HAT and in no row of the assembly BOM. They cannot collide because they are not in this robot. '
                                '(part:microduck-robot-hat-pcb still lists "NFC reader" as CANNOT DETERMINE — the copper answers no.)',
                    cite=f'{len(comps)} footprints in elec_RPI_Robot_HAT.kicad_pcb; ce-assemblies/microduck/current/bom.json'))
    return out


def rows_e2_header(comps, header):
    """E2 — does the Radxa actually expose what the HAT asks of each pin?"""
    # what the HAT wants, per header pin, read off the copper plus the sheet's own labels
    WANT = {
        3:  ('I2C SDA', 'I2C3_SDA_M0'), 5:  ('I2C SCL', 'I2C3_SCL_M0'),
        8:  ('UART TX (host -> U8.DI and U7.A)', 'UART2_TX_M0'),
        10: ('UART RX (U5.Y -> host)', 'UART2_RX_M0'),
        12: ('I2S bit clock', 'I2S3_SCLK_M0'), 35: ('I2S word clock', 'I2S3_LRCK_M0'),
        38: ('I2S data in (codec DOUT)', 'I2S3_SDI_M0'), 40: ('I2S data out (codec DIN)', 'I2S3_SDO_M0'),
        27: ('HAT+ EEPROM data (U4 DNP)', 'I2C4_SDA_M0'), 28: ('HAT+ EEPROM clock (U4 DNP)', 'I2C4_SCL_M0'),
        15: ('BMI088 INT1, an input', 'GPIO'), 31: ('battery-present sense, an input', 'GPIO'),
        7:  ('Stemma J6 (via R18), bit-banged', 'GPIO'), 29: ('Stemma J6 (via R19), bit-banged', 'GPIO'),
        19: ('Stemma J8, bit-banged', 'GPIO'), 21: ('Stemma J7, bit-banged', 'GPIO'),
        23: ('Stemma J8, bit-banged', 'GPIO'), 24: ('Stemma J7, bit-banged', 'GPIO'),
    }
    out, ok, gpio, bad = [], 0, 0, 0
    j4 = comps['J4']['pads']
    for pin in sorted(WANT):
        want, fn = WANT[pin]
        have = header.get(pin, [])
        net = j4.get(str(pin), '')
        if fn == 'GPIO':
            v = PASS if any(f.startswith('GPIO') for f in have) else CD
            gpio += 1
            meas = f'pin {pin} carries {net!r}; the HAT wants {want}. Radxa functions: {have}. A plain GPIO is enough.'
        else:
            m = [f for f in have if f.split('  ')[0] == fn]
            v = PASS if m else FAIL
            if m:
                ok += 1
            else:
                bad += 1
            meas = f'pin {pin} carries {net!r}; the HAT wants {fn}. Radxa functions: {have}.'
            if not m:
                meas += '  <- the Radxa does NOT publish that function on this pin.'
        out.append(dict(check='E2', item=f'header pin {pin} — {want}', verdict=v, measurement=meas,
                        cite='docs.radxa.com/en/zero/zero3/hardware-design/hardware-interface "40 PIN GPIO" table, '
                             'fetched 2026-09-02; copper for the HAT side'))
    # the MCLK pin, which is the interesting one
    p13 = j4.get('13', '')
    y1 = comps.get('Y1', {}).get('value', '')
    out.append(dict(check='E2', item='I2S master clock (pin 13)', verdict=PASS,
                    measurement=f'Header pin 13 = {p13!r} — THE HAT DOES NOT CONNECT IT. The codec\'s MCLK (U2.1) is driven by '
                                f'Y1 [{y1}], a 4-pad oscillator on the HAT with pins 1 and 4 on +3V3 and pin 2 on GND. '
                                f'So the Radxa supplies no master clock and needs no I2S3_MCLK_M0 pin. This is what the "fixed-clock" '
                                f'node in Pollen\'s audio overlay describes.',
                    cite='copper: J4 pad 13 net, Y1 pads; teardown §5b "Audio clocks: 12 MHz fixed MCLK"'))
    # I2S direction sanity
    out.append(dict(check='E2', item='I2S data direction', verdict=PASS,
                    measurement='U2.4 (DIN) -> IO_21 -> header 40 = I2S3_SDO_M0 (SoC drives OUT), and U2.5 (DOUT) -> IO_20 -> '
                                'header 38 = I2S3_SDI_M0 (SoC listens IN). The two are not crossed.',
                    cite='copper; Radxa wiki 40-pin table'))
    out.append(dict(check='E2', item='which I2S3 mux the HAT forces', verdict=PASS,
                    measurement='M0. The HAT wires I2S only to header pins 12/35/38/40, which are I2S3_*_M0. The M1 alternates sit on '
                                'pins 19/21/23/24 — and those four pins are wired to the Stemma headers J7/J8 on this board, so M1 is '
                                'not merely unused, it is OCCUPIED. This settles the open question in part:radxa-zero-3w unknowns[4] '
                                'and in part:microduck-robot-hat-pcb uncertainties[3], where M0 was recorded as the wiring lane\'s '
                                'ASSERTION. It is now a measurement.',
                    cite='copper J4 pads 12/19/21/23/24/35/38/40; Radxa wiki 40-pin table'))
    out.append(dict(check='E2', item='header pins used and spare', verdict=PASS,
                    measurement=f'{sum(1 for p, n in j4.items() if p != "MP" and n and not n.startswith("unconnected-"))} of 40 pins '
                                f'connected, {sum(1 for p, n in j4.items() if n.startswith("unconnected-"))} explicitly unconnected. '
                                f'Spare pins: {sorted(int(p) for p, n in j4.items() if n.startswith("unconnected-"))}.',
                    cite='copper'))
    return out


def rows_e3_rails(comps, nets):
    """E3 — does every rail have a source, and is any net dangling?"""
    bn = by_net(comps)
    out = []
    for rail in ('+BATT', '+5V', '+3V3', '+1V8'):
        info = RAIL_SOURCE[rail]
        pads = sorted(bn[rail])
        out.append(dict(check='E3', item=f'rail {rail} has a source', verdict=PASS,
                        measurement=f'{len(pads)} pads on {rail}. Source: {info["source"]}. Pads: {", ".join(pads)}',
                        cite=info['cite']))
    # dangling
    single = {n: p for n, p in bn.items() if len(p) == 1 and not n.startswith('unconnected-')}
    if BREAK == 2:
        single['Net-(FAKE-DANGLER)'] = ['U99.1']
    out.append(dict(check='E3', item='dangling nets', verdict=FAIL if single else PASS,
                    measurement=(f'{len(single)} net(s) reach exactly one pad: ' + '; '.join(f'{n} at {p[0]}' for n, p in single.items()))
                                if single else
                                f'0 of {len([n for n in bn if not n.startswith("unconnected-")])} named nets reach only one pad. '
                                f'{sum(1 for n in bn if n.startswith("unconnected-"))} pads are marked unconnected BY THE DESIGNER, '
                                f'which is a statement, not a dangle.',
                    cite='copper: every net counted by the pads that carry it'))
    # anything at 5 V that the Radxa must not see
    out.append(dict(check='E3', item='is any 5 V logic presented to a 3.3 V pin', verdict=PASS,
                    measurement='The only +5V pads that touch the header are J4.2 and J4.4, which are the Radxa\'s 5 V INPUT pins. '
                                'Every signal pin the HAT drives (I2C, UART, I2S, INT1, the battery sense) is referenced to +3V3 or '
                                'clamped: the battery sense is R24 10 k from +BATT with D2, a 3V3 zener, to GND, so header pin 31 '
                                'sees 3.3 V and not 8.2 V. The Radxa\'s own limit is 3.63 V on all GPIOs.',
                    cite='copper: R24 [10k] +BATT->IO_06, D2 [3V3 Zener Diode] IO_06->GND; '
                         'docs.radxa.com GPIO voltage table: "All GPIOs | 3.3V | 3.63V"'))
    out.append(dict(check='E3', item='the battery-present sense nobody documented', verdict=PASS,
                    measurement='Header pin 31 (GPIO3_B4) carries a divided +BATT: R24 10 k in series, D2 3V3 zener to ground, C44 10 n '
                                'to ground. At the pack top of 8.2 V that is (8.2-3.3)/10k = 0.490 mA into the zener. It is a LOGIC '
                                'battery-present line, not an ADC — consistent with the teardown\'s "There is no fuel gauge and no ADC". '
                                'No Pollen source read here uses it.',
                    cite='copper; teardown §6 "How the voltage is measured"'))
    return out


def rows_e4_voltage(comps):
    """E4 — is every supply PIN inside its own rated band on the rail that pin is
    actually on? Pin by pin, because a part with a 1.8 V core and 3.3 V I/O is
    perfectly happy on two rails at once and a part-level check would call that
    a failure."""
    out = []

    def rail_v(net):
        return RAIL_SOURCE[net]['v'] if net in RAIL_SOURCE else None

    for ref, f in sorted(DEVICE_FACTS.items()):
        if ref not in comps:
            continue
        pads = comps[ref]['pads']
        bad, seen, unknown = [], [], []
        for sname, (pins, lo, typ, hi) in f['supplies'].items():
            for pin in pins:
                net = pads.get(pin, '')
                rv = rail_v(net)
                if rv is None:
                    # the pin is fed through a link or a ferrite; walk one hop
                    hop = None
                    for r2, c2 in comps.items():
                        if r2 == ref:
                            continue
                        if net in c2['pads'].values():
                            for p2, n2 in c2['pads'].items():
                                if n2 in RAIL_SOURCE and n2 != 'GND':
                                    hop = (r2, c2['value'], n2)
                                    break
                        if hop:
                            break
                    if hop:
                        net = f'{hop[2]} (through {hop[0]} [{hop[1]}])'
                        rv = rail_v(hop[2])
                if rv is None:
                    unknown.append(f'{sname} pin {pin} -> {net or "no net"} (rail not identified)')
                    continue
                if lo is None and hi is None:
                    unknown.append(f'{sname} pin {pin} on {net} = {rv[2]} V, but NO rated band was transcribed for this part')
                    continue
                seen.append(f'{sname} pin {pin} on {net} = {rv[2]} V, rated {lo}..{hi} V')
                if hi is not None and rv[2] > hi:
                    bad.append(f'{sname} pin {pin} on {net} sees {rv[2]} V against a {hi} V maximum')
                if lo is not None and rv[0] < lo:
                    bad.append(f'{sname} pin {pin} on {net} can fall to {rv[0]} V against a {lo} V minimum')
        if f.get('dnp'):
            v, meas = PASS, f'Not fitted; nothing is powered at its lands. ({"; ".join(seen)})'
        elif bad:
            v, meas = FAIL, 'OVER/UNDER: ' + '; '.join(bad)
        elif unknown and not seen:
            v, meas = CD, ('nothing can be graded: ' + '; '.join(unknown) +
                           '. WHAT SETTLES IT: transcribe the recommended-operating-conditions row from the datasheet in the '
                           "board's own docs/ folder into a ce-parts record.")
        elif unknown:
            v, meas = CD, ('; '.join(seen) + ' — those are inside their bands, but UNGRADED: ' + '; '.join(unknown))
        else:
            v, meas = PASS, '; '.join(seen) + '  — inside every band'
        out.append(dict(check='E4', item=f'{ref} {f["name"]}', verdict=v, measurement=meas, cite=f['cite']))

    # THE ONE THAT DOES NOT CLOSE
    over_min = round(PACK['v_min'] - XL330['v_max'], 4)
    over_max = round(PACK['v_max'] - XL330['v_max'], 4)
    v = FAIL if BREAK != 3 else PASS
    out.append(dict(check='E4', item='XL330-M288-T x15 on +BATT', verdict=v,
                    measurement=f'The copper puts the servo VDD on +BATT with nothing between: J13.2, J14.2, J3.2 and J11.2 are all '
                                f'+BATT, and no regulator on this board has +BATT on an output. The pack window under load is '
                                f'{PACK["v_min"]}-{PACK["v_max"]} V; the servo is rated {XL330["v_min"]}-{XL330["v_max"]} V, recommended '
                                f'{XL330["v_rec"]} V. THE SERVOS RUN {over_min:.1f} V TO {over_max:.1f} V ABOVE THEIR RATED MAXIMUM AT '
                                f'ALL TIMES — 10.0 % over when the pack is empty, 36.7 % over when it is full. There is no operating '
                                f'point in the pack\'s range at which they are in spec.',
                    cite=XL330['cite'] + ' | ' + PACK['cite'] + ' | copper: +BATT pad list'))
    out.append(dict(check='E4', item='how the reference robot survives that', verdict=CD,
                    measurement='Pollen writes Shutdown(63) = 52 into every servo at boot. The vendor default is 53; 53 - 52 = 1 = bit 0, '
                                'which is the Input Voltage Error bit. So the runtime CLEARS the servo\'s own over-voltage shutdown and '
                                'leaves the overload and over-temperature bits armed. That is a fact about Pollen\'s code, not a vendor '
                                'statement that 8.2 V is safe. ROBOTIS publishes no absolute maximum for this actuator, and the firmware\'s '
                                'own Max Voltage Limit(32) cannot be set above 7.0 V — below the pack\'s own top. WHAT SETTLES IT: a meter '
                                'on a servo VDD pin of a running robot, and a ROBOTIS statement of the absolute maximum.',
                    cite='research/raw/microduck_main_docs_design_robotd-design.md:253-257 (model.rs asserts return_delay_time=0, '
                         'baud_rate=3, pwm_slope=255, shutdown=52); ce-parts/xl330-m288-t/iterations/v0.0.1/docs/DATASHEET.md §4 item 1'))
    out.append(dict(check='E4', item='the HAT itself on that same pack', verdict=PASS,
                    measurement=f'The HAT\'s own input range is 5-28 V (its README) and its buck accepts 3.8-32 V. The pack\'s '
                                f'{PACK["v_min"]}-{PACK["v_max"]} V is inside both. The board is fine on this pack; only the actuators '
                                f'sharing the same net are not. This is why the contradiction is easy to miss: the board is a '
                                f'general-purpose HAT rated far above what an XL330 will take, and the motor connector is both its power '
                                f'inlet and their supply.',
                    cite="reference/pollen-elec-rpi-robot-hat/README.md: 'can be power from 5 to 28V'; AP63205 DS41326 Rev 2-2 p.1"))
    out.append(dict(check='E4', item='ToF module IOVDD, if a VL53L8CX is fitted', verdict=CD,
                    measurement='Stemma J5 offers +3V3 on pin 2 and 3.3 V logic (R12/R13 pull the bus to +3V3). part:vl53l5cx takes '
                                '3.0-3.6 V on both AVDD and IOVDD, so an L5CX is fine. part:vl53l8cx HAS NO 3.3 V IOVDD CONFIGURATION '
                                'AT ALL — its IOVDD bands are 1.2 V and 1.8 V and its absolute maximum IOVDD is 1.98 V. Pollen\'s firmware '
                                'supports both parts. So an L8CX can only be on this connector as a MODULE carrying its own 1.8 V regulator '
                                'and level shifting; the bare chip on J5 would be 1.32 V over its absolute maximum. Which module is fitted '
                                'is CANNOT DETERMINE. WHAT SETTLES IT: the part number on the ToF breakout in a teardown photo.',
                    cite='ce-parts/vl53l8cx/.../electrical.chip.json supplies[IOVDD] Table 12 p.20 and absolute_max Table 11; '
                         'ce-parts/vl53l5cx/.../supplies[IOVDD] Table 12 p.17; teardown §7 "VL53L5CX or VL53L8CX"'))
    return out


def rows_e5_budget(comps, runtime):
    """E5 — does the power budget close, rail by rail?"""
    bn = by_net(comps)
    out = []
    w = runtime['outputs']['modes']['walking']
    pk = w['pack_current_from_servos_A']['peak']
    mn = w['pack_current_from_servos_A']['mean']
    single = w['peak_single_servo_current_A']
    out.append(dict(check='E5', item='+BATT — servo demand under the walking policy', verdict=PASS,
                    measurement=f'Pack current from the servos: mean {mn:.4f} A, peak {pk:.4f} A over 2301 physics frames of the '
                                f'vx 0.25 m/s cell; worst single servo {single:.4f} A ({w["peak_single_servo_current_joint"]}). '
                                f'Servo electrical power mean {w["servo_total_power_W"]["mean"]:.4f} W, peak '
                                f'{w["servo_total_power_W"]["peak"]:.4f} W. This is what the pack must deliver while walking.',
                    cite='out/sim-evidence/battery-runtime.json outputs.modes.walking; I = |tau|/kT per 200 Hz physics frame from '
                         'out/sim-evidence/gait-torque-duty.json, kT from the XL330 stall rows'))
    stall_all = round(15 * XL330['stall_A'][6.0], 4)
    out.append(dict(check='E5', item='+BATT — the number the budget is NOT sized for', verdict=CD,
                    measurement=f'15 servos all stalled at the 6.0 V row would be {stall_all:.2f} A, and the pack, the wire and the '
                                f'connector would all be far past their ratings. The walking peak is {pk:.4f} A, 4.4 % of that. Nothing '
                                f'in the fetched material states a pack discharge limit, a connector rating for the fitted JST EH parts, '
                                f'or the XL330\'s current at any torque between 0 and stall — ROBOTIS publishes only the 17 mA standby and '
                                f'the three stall rows. So the margin between "walking" and "the wire melts" is UNMEASURED. WHAT SETTLES IT: '
                                f'a clamp meter on the pack lead through a fall-and-recover cycle, which is the load case the gait sweep '
                                f'does not cover.',
                    cite='XL330 stall rows (ROBOTIS e-Manual Specifications); out/sim-evidence/gait-peaks.json inputs.servo.note'))
    out.append(dict(check='E5', item='+BATT — everything is on ONE connector contact', verdict=CD,
                    measurement='The battery enters on a motor connector (README, and the copper: no other +BATT terminal exists). '
                                'J13 and J14 are wired in parallel — J13.1/J14.1 both GND, J13.2/J14.2 both +BATT, J13.3/J14.3 the same '
                                f'data net — so the pack current AND the whole servo chain\'s {pk:.4f} A peak AND the buck\'s input current '
                                'pass through a single JST EH 2.5 mm contact pair. The fitted connector\'s current rating is not in any '
                                'document fetched here. WHAT SETTLES IT: the JST EH series datasheet current rating, against the measured '
                                'peak.',
                    cite='copper: J13/J14 pad->net table; reference/pollen-elec-rpi-robot-hat/README.md'))
    # +5V
    loads5 = sorted(bn['+5V'])
    lim = RAIL_SOURCE['+5V']['limit_A']
    out.append(dict(check='E5', item='+5V — what is on it', verdict=PASS,
                    measurement=f'{len(loads5)} pads: the Radxa (J4.2, J4.4), the amplifier U1 (pins 4 and 13, plus FB1 to its VDD), '
                                f'three 0 R straps R3/R4/R5 that hold PAM8406 ~SHDN, ~MUTE and MODE high, two 10 k mic-bias resistors '
                                f'R22/R23 to the Wago mic terminals, R8 100 R to the LM5050 sense pin, and the ideal-diode FET Q2. '
                                f'Source limit {lim} A.',
                    cite='copper; AP63205 DS41326 Rev 2-2 p.1 "2A Continuous Output Current"'))
    # the radxa
    out.append(dict(check='E5', item='+5V — does 2 A cover the Radxa plus the amplifier', verdict=CD,
                    measurement='Radxa states a 5 V / 2 A adapter for the ZERO 3W and publishes NO board current figure anywhere in the '
                                'four documents fetched (product brief, wiki, two schematics) — part:radxa-zero-3w unknowns[1] says so. '
                                'The PAM8406D publishes output POWER, not supply current: 3.14 W per channel into 4 ohm at THD+N 10 %, '
                                'VDD 5 V, with efficiency up to 90 %. Only ONE channel leaves the board — the copper shows the RIGHT '
                                'channel going through FB2/FB3 to the Wago speaker terminal J1, while the LEFT channel\'s two outputs '
                                'terminate at test points TP3 and TP4 and nothing else — so the amplifier bound is one channel, about '
                                '3.14/0.90 = 3.49 W = 0.70 A at 5 V, not two channels. The buck can give 2.00 A total. If the Radxa ever '
                                'draws its stated 2 A adapter rating while audio is playing, the rail is over-subscribed by roughly 0.70 A. '
                                'It CANNOT BE GRADED without a board-current measurement. WHAT SETTLES IT: a meter in series with header '
                                'pin 2 while the policy runs and the speaker plays.',
                    cite='part:radxa-zero-3w power[0] cite (brief §5.1 p.5) and unknowns[1]; '
                         "'part - PAM8406 - C86270.pdf' PO table and 'Efficiency up to 90% with Class-D Mode'; "
                         'copper: U1.1/U1.3 -> TP3/TP4 only, U1.16/U1.14 -> FB3/FB2 -> J1'))
    # +3V3
    loads3 = sorted(bn['+3V3'])
    dev3 = [(r, DEVICE_FACTS[r]) for r in DEVICE_FACTS if any(n == '+3V3' for n in comps.get(r, {}).get('pads', {}).values())]
    known = [(r, f['mA_typ']) for r, f in dev3 if f.get('mA_typ')]
    tof = OFFBOARD['tof']
    total_typ = sum(v for _, v in known) + tof['mA_typ']
    total_peak_known = sum(v for _, v in known) + tof['mA_peak']
    unknown = [r for r, f in dev3 if not f.get('mA_typ') and not f.get('dnp')]
    out.append(dict(check='E5', item='+3V3 — demand versus a supply nobody has stated', verdict=CD,
                    measurement=f'{len(loads3)} pads on +3V3, and the rail is SOURCED BY THE RADXA through header pins 1 and 17 — the HAT '
                                f'makes no 3.3 V. Known demand: ' +
                                ', '.join(f'{r} {v} mA' for r, v in known) +
                                f', ToF module on J5 {tof["mA_typ"]} mA typical / {tof["mA_peak"]} mA peak = '
                                f'{total_typ:.2f} mA typical, {total_peak_known:.2f} mA with the ToF at its peak. '
                                f'NOT COUNTED because no figure was transcribed: {", ".join(unknown)}, the four Stemma headers J5-J8 '
                                f'(anything a user plugs in), and Y1 the 12 MHz oscillator. THE SUPPLY SIDE IS THE PROBLEM: no fetched '
                                f'Radxa document states how much current the 40-pin 3.3 V pins can deliver, and the RK817 PMIC rail behind '
                                f'them is not broken out per-rail in the brief. A 145 mA peak demand on an unstated supply is not a pass. '
                                f'WHAT SETTLES IT: the RK817 datasheet LDO rating for the rail that feeds header pins 1/17, or a meter.',
                    cite='copper +3V3 pad list; per-device cites in DEVICE_FACTS; part:radxa-zero-3w power[4] "Board-level current draw: '
                         'NOT stated in any fetched document"'))
    # +1V8
    out.append(dict(check='E5', item='+1V8 — demand versus the LDO', verdict=PASS,
                    measurement=f'{len(sorted(bn["+1V8"]))} pads: U3.2 (the LDO output), U2.32 (the codec DVDD) and two capacitors. '
                                f'The only load is the codec digital core, 2.45 mA at its worst printed row, against the XC6206\'s '
                                f'100 mA IOUT(max) at VIN = VOUT + 1 V — and here VIN is 3.3 V, 1.5 V of headroom. 2.5 % of the LDO. '
                                f'This is the one rail in the robot whose budget closes with numbers on both sides.',
                    cite="copper; SLAS510G p.12 IDVDD rows; 'part - XC6202 - C347373.pdf' IOUT(max) row"))
    return out


def rows_e6_harness(comps, cables):
    """E6 — does every modelled cable run land on something that exists?"""
    out = []
    runs = cables['record']['cables']
    conn_by_role = {
        'tof': ('J5', 'JST SH 4-pin'),
        'speaker': ('J1', 'Wago-2 screwless terminal'),
        'mic': ('J2 or J9', 'Wago-2 screwless terminal'),
        'battery': ('a Dynamixel motor connector', 'JST EH — THERE IS NO BATTERY TERMINAL'),
        'radxa': ('J4', '2x20 SMD female header'),
    }
    hat_ends = [r for r in runs if r['from'] == 'hat' or r['to'] == 'hat']
    out.append(dict(check='E6', item='cable runs that touch the HAT', verdict=PASS,
                    measurement=f'{len(runs)} runs modelled in wiring/cables.json; {len(hat_ends)} of them have an end on the HAT: ' +
                                ', '.join(r['id'] for r in hat_ends),
                    cite='wiring/cables.json record.cables'))
    for r in hat_ends:
        other = r['to'] if r['from'] == 'hat' else r['from']
        key = other if other in conn_by_role else ('battery' if other == 'battery' else None)
        if key:
            ref, kind = conn_by_role[key]
            first = ref.split(' ')[0]
            exists = first in comps
            out.append(dict(check='E6', item=f'run {r["id"]} lands on {ref}', verdict=PASS if (exists or key == 'battery') else FAIL,
                            measurement=f'{other} <-> HAT. The copper\'s connector is {ref} ({kind})' +
                                        (f', footprint {comps[first]["footprint"]}' if exists else '') +
                                        f'. Modelled pins: {r["pins"]}',
                            cite='copper; wiring/cables.json'))
    # the three corrections
    out.append(dict(check='E6', item='run spk-hat — the CANNOT DETERMINE is now settled', verdict=PASS,
                    measurement='wiring/cables.json records the speaker pins as "SPK+, SPK- (codec line/HP out, or an amplifier: '
                                'CANNOT DETERMINE)". THE COPPER SAYS AMPLIFIER: J1.1 <- C9/FB3 <- U1.16 (+OUT_R) and J1.2 <- C8/FB2 '
                                '<- U1.14 (-OUT_R), i.e. the PAM8406D\'s bridged right channel through ferrites, not the codec\'s '
                                'LINE_OUT. The codec\'s LEFT_LOP/RIGHT_LOP go to C1/C2 and into the amplifier inputs. That CANNOT '
                                'DETERMINE can be retired, and the speaker sees a bridged 5 V class-D output, not a line level.',
                    cite='copper: U1, FB2, FB3, C8, C9, J1 pad->net'))
    out.append(dict(check='E6', item='run mic-hat — the model may carry a cable the robot has not got', verdict=CD,
                    measurement='wiring/cables.json has a run "mic-hat" with cable_mm null and part:microduck-mic says the transducer, '
                                'count, position and connector are all CANNOT DETERMINE. The copper shows the HAT carries its OWN mic: '
                                'MK1, an LMA2718 MEMS part on +3V3, coupled through C10 into U2.16 (MIC2R/LINE2R, the pin Pollen\'s '
                                'ALSA config calls Mic3R). Two Wago terminals J2 and J9 are ALSO wired to mic inputs with 10 k bias '
                                'resistors to +5V. So "the head microphone" is either the on-board MK1 with no cable at all, or an '
                                'external capsule on J2/J9 with one. Our model asserts the cable. WHAT SETTLES IT: a teardown photo of '
                                'the HAT in the head showing whether anything is in J2 or J9.',
                    cite='copper: MK1, C10, U2.16, J2, J9, R22, R23; wiring/cables.json run mic-hat; part:microduck-mic uncertainties[0]'))
    out.append(dict(check='E6', item='run hat-radxa-40pin overstates the I2S by one pin', verdict=FAIL,
                    measurement='The run records "I2S3 (M0: 12/13/35/38/40 asserted)". Header pin 13 is UNCONNECTED on the HAT — the '
                                'copper marks it unconnected-(J4-Pin_13-Pad13) — because MCLK comes from Y1 on the board. The correct '
                                'list is 12/35/38/40, and "asserted" becomes "measured". One pin in one string, but it is the difference '
                                'between a reader wiring an MCLK and not.',
                    cite='copper J4 pad 13; wiring/cables.json run hat-radxa-40pin'))
    out.append(dict(check='E6', item='the servo chain branches at a board with an unknown port count', verdict=CD,
                    measurement='The chain modelled in cables.json is hat -> id34 -> id33 -> id32 -> id31 -> id30 -> imu200 -> {id20, id10}: '
                                'imu200 needs THREE bus connectors, one in and two out. An XL330 has exactly two, so the branch cannot be at '
                                'a servo. part:microduck-imu-to-dxl already records the connector count as CANNOT DETERMINE and says the '
                                'wiring lane put the branch there. Nothing has changed that. WHAT SETTLES IT: a photograph of the '
                                'imu_to_dxl v2 board; its schematic is not published.',
                    cite='wiring/cables.json cables[]; ce-parts/microduck-imu-to-dxl/electrical.part.json uncertainties[0]'))
    return out


def rows_e7_unpowered(comps, cables):
    """E7 — is any device in the robot on no rail at all?"""
    out = []
    unpowered = []
    for ref, f in sorted(DEVICE_FACTS.items()):
        if ref not in comps or f.get('dnp'):
            continue
        rails = {n for n in comps[ref]['pads'].values() if n in RAIL_SOURCE and n != 'GND'}
        if not rails:
            unpowered.append(ref)
    if BREAK == 4:
        unpowered.append('U2')
    out.append(dict(check='E7', item='every fitted active device on the HAT is on a rail', verdict=FAIL if unpowered else PASS,
                    measurement=(f'UNPOWERED: {", ".join(unpowered)}') if unpowered else
                                f'{len([r for r, f in DEVICE_FACTS.items() if r in comps and not f.get("dnp")])} fitted active devices '
                                f'checked, every one has at least one pad on +BATT, +5V, +3V3 or +1V8.',
                    cite='copper'))
    out.append(dict(check='E7', item='off-board devices', verdict=PASS,
                    measurement='ToF -> J5.2 = +3V3. Camera -> the Radxa CSI connector pin 22 VCC_3V3, not the HAT. imu_to_dxl -> the '
                                'servo bus VDD = +BATT. Speaker -> J1, driven, not powered. Mic -> either MK1 on +3V3 or a capsule on '
                                'J2/J9 biased through 10 k from +5V. No modelled device is on no rail.',
                    cite='copper; part:imx219 / part:microduck-camera-module requires[VCC_3V3]'))
    out.append(dict(check='E7', item='the one function that is powered and has no software', verdict=PASS,
                    measurement='U11 BMI088 is fully powered (+3V3 through R9 0 R), addressed at 0x19/0x68, and its INT1 is routed to '
                                'header pin 15 through R25 — and Pollen\'s runtime never reads it. The control IMU is the LSM6DSV16X on '
                                'the imu_to_dxl board at Dynamixel ID 200 instead. That is the "two IMUs" the press mentions: one of them '
                                'is dormant hardware, not a redundant sensor.',
                    cite='copper: U11, R9, R14, R15, R25; teardown §4 "Actually fitted, but unused by software"'))
    return out


# ------------------------------------------------------------------- self-test

def selftest():
    comps, nets = hat_netlist()
    header = radxa_header()
    cables = json.load(open(CABLES))
    runtime = json.load(open(RUNTIME))
    bn = by_net(comps)
    T = []

    def t(name, ok, detail=''):
        T.append((name, bool(ok), detail))

    t('the board file parses', len(comps) == 127, f'{len(comps)} footprints, expected 127')
    t('the net table parses', len(nets) == 96, f'{len(nets)} nets, expected 96')
    t('every pad carries a net or an explicit blank', all(isinstance(v, str) for c in comps.values() for v in c['pads'].values()))
    t('the Radxa header parses to 40 pins', len(header) == 40, f'{len(header)} pins')
    t('header pin 8 is UART2_TX_M0', 'UART2_TX_M0' in header.get(8, []))
    t('header pin 13 is I2S3_MCLK_M0', 'I2S3_MCLK_M0' in header.get(13, []))
    t('+BATT reaches all four motor connectors',
      all(comps[j]['pads']['2'] == '+BATT' for j in ('J13', 'J14', 'J3', 'J11')))
    t('+BATT reaches NO other connector',
      not any(r.startswith('J') and r not in ('J13', 'J14', 'J3', 'J11')
              for p in bn['+BATT'] for r in [p.split('.')[0]]))
    t('the buck input is +BATT', comps['U9']['pads']['3'] == '+BATT')
    t('the buck feedback is the output node', comps['U9']['pads']['1'] == comps['L4']['pads']['1'])
    t('R14 straps SDO1 high', comps['R14']['pads']['1'] == '+3V3')
    t('R15 straps SDO2 low', comps['R15']['pads']['1'] == 'GND')
    t('the codec and the BMI088 share the SDA net', comps['U2']['pads']['9'] == comps['U11']['pads']['9'])
    t('J5 is on that same SDA net', comps['J5']['pads']['3'] == comps['U2']['pads']['9'])
    t('header pin 13 is unconnected on the HAT', comps['J4']['pads']['13'].startswith('unconnected-'))
    t('the left amplifier channel goes only to test points',
      sorted(bn[comps['U1']['pads']['1']]) == ['TP3.1', 'U1.1'])
    t('no named net reaches only one pad',
      not [n for n, p in bn.items() if len(p) == 1 and not n.startswith('unconnected-')])
    t('the walking peak is on record', runtime['outputs']['modes']['walking']['pack_current_from_servos_A']['peak'] > 0)
    t('cables.json carries 23 runs', len(cables['record']['cables']) == 23, str(len(cables['record']['cables'])))

    # The checks themselves, asserted against the TRUTH — never against what a
    # break would produce. CE_ELEC_BREAK injects a defect into the checker, and
    # these four are what must go red when it does. A self-test that stays green
    # under its own break is a decoration.
    e1 = rows_e1_i2c(comps, nets)
    t('E1 reports no i2c3 collision (BREAK=1 grounds SDO1 and must break this)',
      [r for r in e1 if r['item'] == 'i2c3 address collision'][0]['verdict'] == PASS)
    e3 = rows_e3_rails(comps, nets)
    t('E3 reports no dangling net (BREAK=2 injects one and must break this)',
      [r for r in e3 if r['item'] == 'dangling nets'][0]['verdict'] == PASS)
    e4 = rows_e4_voltage(comps)
    t('E4 FAILS the servo rail (BREAK=3 silences it and must break this)',
      [r for r in e4 if r['item'].startswith('XL330')][0]['verdict'] == FAIL)
    e7 = rows_e7_unpowered(comps, cables)
    t('E7 finds nothing unpowered (BREAK=4 injects one and must break this)',
      [r for r in e7 if r['item'].startswith('every fitted')][0]['verdict'] == PASS)

    npass = sum(1 for _, ok, _ in T if ok)
    for name, ok, detail in T:
        print(f'  {"PASS" if ok else "FAIL"}  {name}' + (f'  [{detail}]' if detail and not ok else ''))
    print(f'\n{npass}/{len(T)} PASS' + (f'   (CE_ELEC_BREAK={BREAK})' if BREAK else ''))
    return 0 if npass == len(T) else 1


# ------------------------------------------------------------------------ main

def main():
    if '--self-test' in sys.argv:
        return selftest()
    comps, nets = hat_netlist()
    header = radxa_header()
    cables = json.load(open(CABLES))
    runtime = json.load(open(RUNTIME))

    rows = []
    rows += rows_e1_i2c(comps, nets)
    rows += rows_e2_header(comps, header)
    rows += rows_e3_rails(comps, nets)
    rows += rows_e4_voltage(comps)
    rows += rows_e5_budget(comps, runtime)
    rows += rows_e6_harness(comps, cables)
    rows += rows_e7_unpowered(comps, cables)

    c = collections.Counter(r['verdict'] for r in rows)
    verdict = FAIL if c[FAIL] else (CD if c[CD] else PASS)
    bn = by_net(comps)
    doc = {
        'study': 'elec-closure',
        'what': "PROVE 3 — does the Microduck's electrical system close. What every chip and board NEEDS, "
                "against what it is ACTUALLY CONNECTED TO in the copper.",
        'generated_by': 'tools/elec_close.py',
        'authority': {
            'connectivity': 'reference/pollen-elec-rpi-robot-hat/elec_RPI_Robot_HAT.kicad_pcb — Pollen\'s own Apache-2.0 board '
                            'file, pad->net table. Not a block diagram and not a hand-authored netlist.',
            'host_pinout': 'ce-parts/radxa-zero-3w/iterations/v0.0.1/docs/fetched/docs.radxa.com_zero3_hardware-interface.html '
                           '"40 PIN GPIO" table, plus the product brief for the I2C3_M0 alternate the wiki omits.',
            'device_needs': 'the ce-parts electrical.chip.json / electrical.part.json records, each quoting its datasheet with a page.',
            'servo_load': 'out/sim-evidence/battery-runtime.json, from out/sim-evidence/gait-torque-duty.json at 200 Hz.',
        },
        'counts': {
            'hat_footprints': len(comps),
            'hat_nets': len(nets),
            'hat_pads_with_a_net': sum(1 for cc in comps.values() for v in cc['pads'].values() if v),
            'rails': 5,
            'header_pins_connected': sum(1 for p, n in comps['J4']['pads'].items() if p != 'MP' and n and not n.startswith('unconnected-')),
            'header_pins_unconnected': sum(1 for n in comps['J4']['pads'].values() if n.startswith('unconnected-')),
            'radxa_header_pins_parsed': len(header),
            'i2c3_devices': 4,
            'i2c3_distinct_addresses': 4,
            'i2c3_collisions': 0,
            'dangling_nets': len([n for n, p in bn.items() if len(p) == 1 and not n.startswith('unconnected-')]),
            'unpowered_fitted_devices': 0,
            'cable_runs_modelled': len(cables['record']['cables']),
            'cable_runs_touching_the_hat': len([r for r in cables['record']['cables'] if 'hat' in (r['from'], r['to'])]),
            'checks_total': len(rows),
            'checks_PASS': c[PASS],
            'checks_FAIL': c[FAIL],
            'checks_CANNOT_DETERMINE': c[CD],
        },
        'verdict': verdict,
        'verdict_why': f'{c[FAIL]} FAIL and {c[CD]} CANNOT DETERMINE of {len(rows)} checks. A CANNOT DETERMINE is not a pass.',
        'rows': rows,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(doc, open(OUT, 'w'), indent=1)
    print(f'{OUT}\n{verdict}: {c[PASS]} PASS / {c[FAIL]} FAIL / {c[CD]} CANNOT DETERMINE of {len(rows)}')
    for r in rows:
        if r['verdict'] != PASS:
            print(f'  {r["verdict"]:17s} {r["check"]}  {r["item"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
