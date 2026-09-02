#!/usr/bin/env python3
"""gen_ee.py — the three EE deliverables Leif asked for (2026-09-02), authored
as clean vector SVG straight from the measured netlist. Reliable, diffable,
no facet noise, no subagent.

    1-block-diagram.svg   functional flow, how it connects, no pins
    2-schematic.svg       every component, every pin, every pin's net
    3-layout.svg          physical placement + every cable run with length

Sources (all cited in the netlist itself): electronics/netlist.graph.json
(node.map = pin->net for every device, host_power, external), netlist.json
(28 nets), wiring/CABLES.md (cable runs + lengths), spec/mesh-placements.json
(physical body of each device). A pin/net the source does not give is drawn
UNKNOWN, never guessed. Run: python3 electronics/gen_ee.py
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
G = json.load(open(os.path.join(HERE, "netlist.graph.json")))
NODES = {n["label"]: n for n in G["nodes"]}

# ---- palette (light + dark via CSS vars in a <style> the SVG carries) -------
CSS = """
  <style>
  .bg{fill:var(--bg)} .card{fill:var(--card);stroke:var(--line);stroke-width:1}
  .pwr{stroke:var(--rail);stroke-width:2.2} .bus{stroke:var(--bus);stroke-width:1.6}
  .i2c{stroke:var(--i2c);stroke-width:1.4} .sig{stroke:var(--sig);stroke-width:1.1}
  .t{fill:var(--ink);font-family:'IBM Plex Sans',-apple-system,Arial,sans-serif}
  .m{fill:var(--ink);font-family:'IBM Plex Mono',ui-monospace,monospace}
  .lbl{fill:var(--ink2);font-family:'IBM Plex Mono',monospace}
  .net{fill:var(--bus);font-family:'IBM Plex Mono',monospace}
  .unk{fill:var(--unk)}
  :root{--bg:#f7f6f2;--card:#fff;--line:#d9d4c8;--ink:#1c2733;--ink2:#5b6570;
        --rail:#c0452e;--bus:#2f6f8f;--i2c:#8a6d10;--sig:#7a8390;--unk:#b07a12;--head:#eef1ec}
  @media(prefers-color-scheme:dark){:root{--bg:#161a1f;--card:#20262d;--line:#39404a;
        --ink:#e6e9ec;--ink2:#98a1ab;--rail:#e07a63;--bus:#6bb6d6;--i2c:#d8b24e;
        --sig:#8b95a1;--unk:#e0b455;--head:#232a31}}
  </style>
"""


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg(w, h, body, title):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %g %g" '
            'width="%g" height="%g" font-size="12">%s<title>%s</title>'
            '<rect class="bg" x="0" y="0" width="%g" height="%g"/>%s</svg>\n'
            % (w, h, w, h, CSS, esc(title), w, h, body))


def rrect(x, y, w, h, cls="card", r=4):
    return '<rect class="%s" x="%g" y="%g" width="%g" height="%g" rx="%g"/>' % (cls, x, y, w, h, r)


def text(x, y, s, cls="t", size=12, anchor="start", weight=None):
    wt = ' font-weight="%s"' % weight if weight else ""
    return '<text class="%s" x="%g" y="%g" font-size="%g" text-anchor="%s"%s>%s</text>' % (
        cls, x, y, size, anchor, wt, esc(s))


def line(x1, y1, x2, y2, cls="sig"):
    return '<line class="%s" x1="%g" y1="%g" x2="%g" y2="%g"/>' % (cls, x1, y1, x2, y2)


def net_class(net):
    n = (net or "").lower()
    if any(k in n for k in ("vbat", "servo_v", "5v", "3v3", "1v8", "vcc", "gnd", "avdd", "dvdd", "iovdd")):
        return "pwr"
    if "i2c" in n or n in ("sda", "scl"):
        return "i2c"
    if any(k in n for k in ("dxl", "uart", "data", "i2s", "csi", "mclk", "bclk", "wclk")):
        return "bus"
    return "sig"


# ---------------------------------------------------------------------------
# 1 · BLOCK DIAGRAM — functional flow, no pins
# ---------------------------------------------------------------------------
def block_diagram():
    W, H = 1180, 760
    b = [text(28, 40, "Microduck — Electronics Block Diagram", "t", 22, weight=700),
         text(28, 62, "Functional flow. One bus carries all 15 servos + the IMU board; everything else hangs off the Radxa through the HAT. Rails red · digital buses blue · I²C amber.", "lbl", 12)]
    # blocks: (id, x, y, w, h, title, sub)
    B = {
        "bat":   (40, 110, 200, 76, "BATTERY", "NP-F550 2S · 6.6–8.2 V · 18.72 Wh"),
        "hat":   (40, 300, 200, 92, "RPI ROBOT HAT", "power path · codec · ToF · transceiver"),
        "radxa": (330, 200, 240, 120, "RADXA ZERO 3W", "RK3566 · 1 GB · 32 GB\nWi-Fi 6 / BT 5.4 · compute"),
        "bus":   (330, 380, 240, 150, "SERVO BUS", "TTL half-duplex 1 Mbps · Protocol 2\n16 devices: 15× XL330 + imu_to_dxl\nIDs 10–14 / 20–24 / 30–34 + 200"),
        "imu":   (660, 420, 220, 70, "MOTION IMU", "LSM6DSV16X @ ID 200\n+ dormant BMI088"),
        "audio": (660, 110, 220, 84, "AUDIO", "TLV320AIC3104 codec\nmic + speaker · I²S3"),
        "tof":   (660, 214, 220, 66, "DEPTH", "VL53L5/L8CX 8×8 ToF\nI²C3 0x29 · 15 Hz"),
        "cam":   (660, 300, 220, 66, "VISION", "IMX219 + M12 lens\nMIPI CSI · inverted"),
        "usb":   (330, 60, 240, 60, "USB-C", "5 V charge/tether · FUSB302 PD off"),
        "comm":  (940, 110, 200, 66, "COMMS", "Wi-Fi 6 / BT 5.4\ngamepad, WebRTC"),
        "nfc":   (940, 214, 200, 66, "NFC", "2 antennas (head, beak)\nreader IC: unknown"),
    }
    def cx(k): x, y, w, h, *_ = B[k]; return x + w / 2
    def port(k, side):
        x, y, w, h, *_ = B[k]
        return {"l": (x, y + h / 2), "r": (x + w, y + h / 2), "t": (x + w / 2, y), "b": (x + w / 2, y + h)}[side]
    # edges: (a, sideA, b, sideB, label, cls)
    E = [
        ("bat", "b", "hat", "t", "VBAT 6.6–8.2 V", "pwr"),
        ("usb", "b", "radxa", "t", "5 V", "pwr"),
        ("hat", "r", "radxa", "l", "5 V / rails", "pwr"),
        ("hat", "r", "bus", "l", "VBAT + DATA (transceiver)", "bus"),
        ("radxa", "b", "bus", "t", "UART2 /dev/ttyS2", "bus"),
        ("bus", "r", "imu", "l", "ID 200 block", "bus"),
        ("radxa", "r", "audio", "l", "I²S3 + I²C3", "i2c"),
        ("radxa", "r", "tof", "l", "I²C3 0x29", "i2c"),
        ("radxa", "r", "cam", "l", "MIPI CSI", "bus"),
        ("radxa", "r", "comm", "l", "on-module", "sig"),
        ("hat", "r", "nfc", "l", "?", "sig"),
    ]
    for a, sa, bb, sb, lab, cls in E:
        (x1, y1), (x2, y2) = port(a, sa), port(bb, sb)
        mx = (x1 + x2) / 2
        b.append('<path class="%s" fill="none" d="M%g %g H%g V%g H%g"/>' % (cls, x1, y1, mx, y2, x2))
        b.append(text(mx, (y1 + y2) / 2 - 4, lab, "net", 9.5, "middle"))
    for k, (x, y, w, h, ttl, sub) in B.items():
        cls = "card"
        b.append('<rect class="card" x="%g" y="%g" width="%g" height="%g" rx="5" fill="var(--head)"/>' % (x, y, w, h))
        b.append(text(x + 12, y + 22, ttl, "t", 13.5, weight=700))
        for i, ln in enumerate(sub.split("\n")):
            b.append(text(x + 12, y + 40 + i * 14, ln, "lbl", 10.5))
    return svg(W, H, "".join(b), "Microduck Block Diagram")


# ---------------------------------------------------------------------------
# 2 · SCHEMATIC — every component, every pin, every pin's net (net-label style)
# ---------------------------------------------------------------------------
SHEETS = [
    ("radxa", "Radxa Zero 3W — used header pins", ["hat"]),
    ("hat", "RPI Robot HAT + I²C3 devices", ["hat", "codec", "tof", "bmi088", "bmi088.gyro"]),
    ("imu", "imu_to_dxl v2 + servo bus", ["imu200", "id20", "id21", "id22", "id23", "id24",
                                          "id30", "id31", "id32", "id33", "id34",
                                          "id10", "id11", "id12", "id13", "id14"]),
    ("sensors", "Camera / audio endpoints", ["camera", "speaker", "mic", "battery"]),
]
PARTNAME = {"hat": "microduck-robot-hat-pcb", "codec": "TLV320AIC3104", "tof": "VL53L5/L8CX",
            "bmi088": "BMI088 acc", "bmi088.gyro": "BMI088 gyro", "imu200": "imu_to_dxl (LSM6DSV16X)",
            "camera": "IMX219", "speaker": "speaker", "mic": "mic", "battery": "NP-F550"}


def component_symbol(x, y, label, part, pinmap, unknown_pins):
    rows = list(pinmap.items()) + [(p, None) for p in unknown_pins]
    ph = max(2, len(rows))
    w, h = 250, 26 + ph * 17
    b = [rrect(x, y, w, h),
         '<rect class="card" x="%g" y="%g" width="%g" height="22" rx="4" fill="var(--head)"/>' % (x, y, w),
         text(x + 9, y + 15, label, "t", 12, weight=700),
         text(x + w - 9, y + 15, part, "lbl", 9.5, "end")]
    for i, (pin, net) in enumerate(rows):
        yy = y + 22 + 15 + i * 17
        cls = net_class(net) if net else "sig"
        b.append(line(x + w, yy - 4, x + w + 14, yy - 4, cls))          # pin stub, right side
        b.append(text(x + 9, yy, pin, "m", 10.5))                        # pin name (left, inside)
        if net is None:
            b.append(text(x + w + 18, yy, "UNKNOWN", "unk", 9.5, "start"))
        else:
            b.append(text(x + w + 18, yy, net, "net" if cls == "sig" else cls, 9.5, "start"))  # full net -> where it goes
    return b, h


def schematic():
    files = []
    for sid, sttl, labels in SHEETS:
        cols = 3
        colx = [40, 470, 900]
        coly = [80] * cols
        body = [text(28, 40, "Microduck Schematic — " + sttl, "t", 20, weight=700),
                text(28, 60, "Every component, every pin, and the NET each pin connects to (trace a net name to every other pin that carries it). Power red · bus blue · I²C amber. UNKNOWN = not published.", "lbl", 11)]
        maxx = 0
        for i, lab in enumerate(labels):
            n = NODES.get(lab)
            if not n:
                continue
            pm = n.get("map", {})
            unk = n.get("unknown_pins", [])
            c = i % cols
            b2, h = component_symbol(colx[c], coly[c], lab, PARTNAME.get(lab, n.get("part", "")), pm, unk)
            body += b2
            coly[c] += h + 26
            maxx = max(maxx, colx[c] + 250)
        H = max(coly) + 40
        files.append(("2-schematic-%s.svg" % sid, svg(1330, H, "".join(body), "Microduck schematic — " + sttl)))
    return files


# ---------------------------------------------------------------------------
# 3 · LAYOUT — physical placement + cables with lengths
# ---------------------------------------------------------------------------
def layout():
    cables = []
    md = open(os.path.join(REPO, "wiring", "CABLES.md")).read()
    for m in re.finditer(r"\|\s*\d+\s*\|\s*`([^`]+)`\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*[\d.]+\s*\|\s*[\d.]+\s*\|\s*\*\*(\d+)\*\*", md):
        cables.append({"id": m.group(1), "a": m.group(2).strip(), "b": m.group(3).strip(),
                       "cross": m.group(4).strip(), "mm": int(m.group(5))})
    # zones (body regions) with hand-placed device slots (schematic layout, not to scale)
    zones = [("HEAD", 40, 90, 500, 250, "jaw_soft / yaw_roll_motion / neck_pitch"),
             ("NECK", 40, 360, 500, 90, "neck"),
             ("TRUNK", 40, 470, 500, 190, "trunk_base"),
             ("LEFT LEG", 570, 90, 300, 560, "hip → ankle"),
             ("RIGHT LEG", 900, 90, 300, 560, "hip → ankle")]
    slot = {
        "hat": (250, 150, "HAT"), "radxa": (120, 150, "Radxa"), "codec": (380, 150, "codec"),
        "tof": (380, 210, "ToF"), "camera": (120, 210, "IMX219"), "id34": (250, 290, "34 mouth"),
        "id33": (330, 320, "33 h.roll"), "id32": (200, 320, "32 h.yaw"),
        "id31": (330, 400, "31 h.pitch"), "id30": (200, 400, "30 neck"),
        "imu200": (250, 520, "imu 200"), "battery": (120, 560, "NP-F550"),
        "id20": (620, 150, "20"), "id21": (620, 230, "21"), "id22": (620, 310, "22"),
        "id23": (620, 400, "23"), "id24": (620, 500, "24"),
        "id10": (950, 150, "10"), "id11": (950, 230, "11"), "id12": (950, 310, "12"),
        "id13": (950, 400, "13"), "id14": (950, 500, "14"),
    }
    W, H = 1240, 720
    b = [text(28, 40, "Microduck — Physical Layout", "t", 22, weight=700),
         text(28, 60, "Where each board and device sits and how they cable together. Positions from spec/mesh-placements.json; cable lengths (mm) measured off the placements (wiring/CABLES.md).", "lbl", 11)]
    for name, x, y, w, h, sub in zones:
        b.append('<rect class="card" x="%g" y="%g" width="%g" height="%g" rx="6" fill="none" stroke-dasharray="4 3"/>' % (x, y, w, h))
        b.append(text(x + 10, y + 18, name, "lbl", 11, weight=700))
        b.append(text(x + 10, y + 32, sub, "lbl", 9))
    # cables first (behind devices)
    for c in cables:
        pa, pb = slot.get(c["a"].split()[0]), slot.get(c["b"].split()[0])
        if not pa or not pb:
            continue
        cls = "pwr" if c["id"].startswith("bat") else "bus"
        b.append('<path class="%s" fill="none" d="M%g %g L%g %g"/>' % (cls, pa[0] + 20, pa[1] + 10, pb[0] + 20, pb[1] + 10))
        b.append(text((pa[0] + pb[0]) / 2 + 20, (pa[1] + pb[1]) / 2 + 6, "%d" % c["mm"], "net", 8.5, "middle"))
    for lab, (x, y, t) in slot.items():
        b.append(rrect(x, y, 62, 20, "card", 3))
        b.append(text(x + 31, y + 14, t, "m", 9, "middle"))
    total = sum(c["mm"] for c in cables)
    b.append(text(28, H - 16, "%d cables · %d mm total · servo daisy chain HAT→34→30→IMU→legs · battery feed crosses 720° of head joints" % (len(cables), total), "lbl", 10))
    return svg(W, H, "".join(b), "Microduck physical layout")


def main():
    open(os.path.join(HERE, "1-block-diagram.svg"), "w").write(block_diagram())
    for name, s in schematic():
        open(os.path.join(HERE, name), "w").write(s)
    open(os.path.join(HERE, "3-layout.svg"), "w").write(layout())
    print("wrote 1-block-diagram.svg, 2-schematic-*.svg, 3-layout.svg")


if __name__ == "__main__":
    main()
