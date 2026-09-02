#!/usr/bin/env python3
"""Microduck Deliverable 1 — functional block diagram (clean orthogonal SVG).
Functional blocks + labelled buses. No pins. Facts: docs/ELECTRONICS-AND-SOFTWARE.md.
Solid = read from Pollen source / datasheet. Dashed = inferred or CANNOT DETERMINE."""
import html

W, H = 1280, 900
OUT = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck/electronics/1-block-diagram.svg"

INK, SUB, PANEL, GRID, BG = "#1a1f26", "#5b6672", "#ffffff", "#e6e9ee", "#f7f8fa"
COL = {"power":"#d1541f","uart":"#7a3fb0","i2c":"#0f8a8a","i2s":"#2563c9",
       "csi":"#2f9e44","misc":"#6b7580","unk":"#9aa3ad"}

body = []
def esc(s): return html.escape(str(s), quote=True)
def cid(c): return c.replace('#','')

def box(x,y,w,h,title,lines,accent):
    body.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{PANEL}" stroke="{accent}" stroke-width="2"/>')
    body.append(f'<rect x="{x}" y="{y}" width="7" height="{h}" rx="3.5" fill="{accent}"/>')
    ty=y+23
    body.append(f'<text x="{x+18}" y="{ty}" font-size="15" font-weight="700" fill="{INK}">{esc(title)}</text>')
    ty+=20
    for ln in lines:
        body.append(f'<text x="{x+18}" y="{ty}" font-size="11.5" fill="{SUB}">{esc(ln)}</text>'); ty+=15

def poly(pts,color,dashed=False,lw=2.4,arrow=True):
    d="M "+" L ".join(f"{x} {y}" for x,y in pts)
    dash=' stroke-dasharray="7 5"' if dashed else ''
    mk=f' marker-end="url(#a-{cid(color)})"' if arrow else ''
    body.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{lw}"{dash} stroke-linejoin="round"{mk}/>')

def label(cx,cy,text,color,anchor="middle"):
    lines=text.split("\n"); lh=13.5
    tw=max(len(l) for l in lines)*6.3+14
    if anchor=="middle": bx=cx-tw/2
    elif anchor=="start": bx=cx-6
    else: bx=cx-tw+6
    body.append(f'<rect x="{bx:.1f}" y="{cy-12:.1f}" width="{tw:.1f}" height="{len(lines)*lh+5:.1f}" rx="4" fill="{BG}" stroke="{GRID}" stroke-width="1"/>')
    for i,l in enumerate(lines):
        body.append(f'<text x="{cx:.1f}" y="{cy+i*lh:.1f}" text-anchor="{anchor}" font-size="10.5" font-weight="600" fill="{color}">{esc(l)}</text>')

def dot(x,y,c): body.append(f'<circle cx="{x}" cy="{y}" r="3.6" fill="{c}"/>')

# ---------- BLOCKS ----------
# POWER (left)
box(34,150,228,78,"POWER — NP-F550 pack",["2S Li-ion · 2600 mAh","6.6–8.2 V under load (7.4 V nom)","no fuel gauge / no ADC"],COL["power"])
box(34,252,228,52,"Banana contact PCB",["removable-pack contacts → HAT"],COL["power"])
box(34,330,228,92,"RPI Robot HAT (power path)",["2S → 5 V (Radxa) + bus VDD (servos)","regulators / fusing: CANNOT DETERMINE","custom Pollen PCB, not published"],COL["power"])

# COMPUTE (centre) + COMMS above
box(360,110,280,64,"COMMS",["Wi-Fi 6 / BT 5.4 (on-module)","USB-C 5 V in · FUSB302 PD disabled"],COL["misc"])
box(360,250,280,128,"COMPUTE — Radxa Zero 3W",["RK3566 · quad Cortex-A55 · Mali-G52","1 GB LPDDR4 · 32 GB eMMC · 0.8-TOPS NPU","RPI Robot HAT on the 40-pin header","28 nets · /dev/ttyS2, /dev/i2c-3, i2s3"],COL["misc"])

# SERVO BUS (bottom centre)
box(320,600,340,100,"SERVO BUS — 16 devices",["TTL half-duplex · Dynamixel Protocol 2.0","15 × XL330-M288 servos","(IDs 10–14, 20–24, 30–34) + imu_to_dxl 200"],COL["uart"])

# RIGHT column peripherals
RX=740; RW=300
box(RX,150,RW,76,"VISION — camera",["Sony IMX219 + M12 wide lens","mounted upside-down (rotation 180)"],COL["csi"])
box(RX,268,RW,92,"AUDIO",["TI TLV320AIC3104 codec (on HAT)","mic (head) + speaker 35×25×7","I2S3 audio data + I2C3 control"],COL["i2s"])
box(RX,398,RW,76,"DEPTH — ToF",["VL53L8CX / VL53L5CX · 8×8 @ 15 Hz","HAT Stemma J5 · tofd daemon"],COL["i2c"])
box(RX,506,RW,100,"MOTION SENSING",["Control IMU: ST LSM6DSV16X — rides the","servo bus as imu_to_dxl (ID 200)","Head IMU: BMI088 on I2C3 (dormant)"],COL["uart"])
box(RX,638,RW,68,"NFC",["2 antennas (head + beak)","reader IC & bus: CANNOT DETERMINE"],COL["unk"])

# ---------- EDGES ----------
# power chain
poly([(148,228),(148,252)],COL["power"]); poly([(148,304),(148,330)],COL["power"])
# HAT -> compute 5V
poly([(262,352),(360,352)],COL["power"]); label(311,346,"5 V",COL["power"])
# HAT -> servo bus VDD (inferred, dashed)
poly([(148,422),(148,650),(320,650)],COL["power"],dashed=True); label(210,642,"bus VDD ~7.4 V (inferred)",COL["power"])

# compute -> COMMS (on-module, up)
poly([(500,250),(500,174)],COL["misc"]); label(500,206,"on-module\n+ USB-C",COL["misc"])

# compute -> servo bus (UART2, down)
poly([(500,378),(500,600)],COL["uart"]); label(500,494,"UART2 (M0) → /dev/ttyS2\n1 Mbps · 3.3 V TTL",COL["uart"])

# compute -> VISION (MIPI CSI): up over the top, into vision left
poly([(600,250),(600,188),(740,188)],COL["csi"]); label(662,182,"MIPI CSI 22-pin",COL["csi"])

# compute -> AUDIO (I2S3): straight horizontal
poly([(640,300),(740,300)],COL["i2s"]); label(690,294,"I2S3 · 12 MHz",COL["i2s"])

# I2C3 shared bus bar (one bus, three devices; addresses live in the schematic, not here)
BARX=700
body.append(f'<line x1="{BARX}" y1="345" x2="{BARX}" y2="546" stroke="{COL["i2c"]}" stroke-width="3.5"/>')
poly([(640,345),(BARX,345)],COL["i2c"],arrow=False); label(668,339,"I2C3 · 400 kHz",COL["i2c"])
# taps to codec, ToF, dormant head-IMU
for ty in (345,436,546):
    dot(BARX,ty,COL["i2c"]); poly([(BARX,ty),(740,ty)],COL["i2c"])

# servo bus -> MOTION (LSM6DSV16X on the bus)
poly([(660,610),(702,610),(702,560),(740,560)],COL["uart"]); label(701,594,"IMU on the bus",COL["uart"],anchor="middle")

# compute -> NFC (unknown bus, dashed)
poly([(640,365),(672,365),(672,672),(740,672)],COL["unk"],dashed=True); label(672,660,"bus\nunknown",COL["unk"])

# ---------- ASSEMBLE ----------
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter,Segoe UI,Helvetica,Arial,sans-serif">']
defs=['<defs>']
for c in set(COL.values()):
    defs.append(f'<marker id="a-{cid(c)}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{c}"/></marker>')
defs.append('</defs>'); svg.append(''.join(defs))
svg.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
svg.append(f'<text x="34" y="44" font-size="25" font-weight="800" fill="{INK}">Microduck — Electronics Block Diagram</text>')
svg.append(f'<text x="34" y="70" font-size="13" fill="{SUB}">Deliverable 1 of 3 — functional flow only, no pins.  Host: Radxa Zero 3W (RK3566).  Facts &amp; cites: docs/ELECTRONICS-AND-SOFTWARE.md.</text>')
svg.append(f'<line x1="34" y1="86" x2="{W-34}" y2="86" stroke="{GRID}" stroke-width="1.5"/>')
svg.extend(body)

# legend + how-it-flows
ly=736
svg.append(f'<rect x="34" y="{ly}" width="640" height="128" rx="9" fill="{PANEL}" stroke="{GRID}" stroke-width="1.5"/>')
svg.append(f'<text x="50" y="{ly+24}" font-size="13" font-weight="700" fill="{INK}">Legend — bus / net</text>')
items=[(COL["power"],"Power rail"),(COL["uart"],"Servo bus (UART / Dynamixel 2.0)"),(COL["i2c"],"I2C3 · 400 kHz"),(COL["i2s"],"I2S3 · audio data"),(COL["csi"],"MIPI CSI · camera"),(COL["misc"],"Comms / USB / power-in")]
for i,(c,t) in enumerate(items):
    col=i%2; row=i//2; ex=54+col*310; ey=ly+50+row*22
    svg.append(f'<line x1="{ex}" y1="{ey}" x2="{ex+32}" y2="{ey}" stroke="{c}" stroke-width="3"/>')
    svg.append(f'<text x="{ex+42}" y="{ey+4}" font-size="11.5" fill="{SUB}">{esc(t)}</text>')
ey=ly+50+3*22
svg.append(f'<line x1="54" y1="{ey}" x2="86" y2="{ey}" stroke="{COL["unk"]}" stroke-width="3" stroke-dasharray="7 5"/>')
svg.append(f'<text x="96" y="{ey+4}" font-size="11.5" fill="{SUB}">Dashed = inferred / CANNOT DETERMINE (never guessed)</text>')

nx=700
svg.append(f'<rect x="{nx}" y="{ly}" width="{W-34-nx}" height="128" rx="9" fill="{PANEL}" stroke="{GRID}" stroke-width="1.5"/>')
svg.append(f'<text x="{nx+16}" y="{ly+24}" font-size="13" font-weight="700" fill="{INK}">How it flows</text>')
notes=["Pack → banana PCB → HAT → 5 V (Radxa) + bus VDD (servos).",
 "One UART carries the whole 16-device servo chain; the control",
 "IMU (LSM6DSV16X) is one more device on that same bus.",
 "I2C3 is a single 400 kHz bus: codec, ToF, dormant BMI088.",
 "Camera is MIPI CSI; audio = I2S3 (data) + I2C3 (control)."]
for i,n in enumerate(notes):
    svg.append(f'<text x="{nx+16}" y="{ly+48+i*15}" font-size="11" fill="{SUB}">{esc(n)}</text>')

svg.append('</svg>')
open(OUT,"w").write("\n".join(svg))
print("wrote",OUT)
