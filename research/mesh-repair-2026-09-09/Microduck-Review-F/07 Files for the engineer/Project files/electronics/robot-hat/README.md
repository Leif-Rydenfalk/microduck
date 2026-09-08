# Robot HAT — OUR reconstruction as a ce-pcb board

**This is not Pollen's board.** Pollen has published no PCB, no schematic and
no BOM for the RPI Robot HAT — the press kit asks that the robot *not* be
described as open-source hardware, and docs/ELECTRONICS-AND-SOFTWARE.md §12
carries the HAT schematic as open question 4. What exists in public is the
HAT's *behaviour*: the device-tree overlays, the runtime that talks through
it, and the vendor datasheets of the chips those files name. This board is a
re-creation **from those published facts only**, with every unpublished
choice made by us, named, and marked. It has never been compared against a
physical HAT; nothing here claims layout, connector placement, or even part
choice matches Pollen's.

    python3 electronics/robot-hat/board.py              build, DRC, plots, gerbers
    python3 electronics/robot-hat/board.py --self-test  break the checks on purpose

## What it carries (the published functions)

| block | on this board | the published fact it answers |
|---|---|---|
| 40-pin header J1 | 2x20 through-hole at the Pi-Zero '+' datum | the HAT sits on the Radxa's 40-pin; I2C3 on pins 3/5, UART2 on 8/10, I2S3 on 12/13/35/38/40 ([brief] p.6; overlays) |
| TLV320AIC3104 U1 | VQFN-32 RHB, IPC-7351B pattern from RHB0032E | `codec@18` on I2C3, I2S3 target, 12 MHz MCLK (aic3104-i2c3.dts) |
| BMI088 U3 | Bosch's own Fig. 11 landing pattern, straps for 0x19/0x68 | "dormant BMI088 0x19/0x68", "unused but still connected" (i2c3-pihat.dts:11,31) |
| ToF J5 | JST SM04B-SRSS-TB (side entry) | the HAT's "Stemma J5" (i2c3-pihat.dts:10), ToF at 0x29 |
| Servo bus J3 | JST B3B-EH-A + 74LVC1G125 half-duplex (U4) + 10 k DATA pull-up | one TTL bus, 16 devices, no direction GPIO anywhere in robotd (docs §3.1); the XL330's own sheet names B3B-EH-A |
| Battery in J2 | JST B2B-XH-A | pack -> banana PCB -> HAT (i2c3-pihat.dts:22) |
| 5 V buck U2 | Pololu D30V30F5 module, VBAT -> V5 -> header pins 2/4 | "In-robot power comes from the battery via the HAT regardless"; the regulator itself is unpublished |
| Servo VDD | R1 0-ohm link VBAT -> SERVO_V | the runtime reads the pack through the servos' own Present Input Voltage (model.rs:99-113) |
| Speaker J6 / mic J7 | JST B2B-PH-K-S / B3B-PH-K-S | speaker and mic exist (docs §7); everything else about them is CANNOT DETERMINE |
| I2C pull-ups | R12/R13 10 k (designators kept from the dts comment) | "one 10 kOhm pull-up pair R12/R13" |
| Mount | 65 x 30 mm, r3.0 corners, 4x M2.5 at the 58 x 23 / 3.5 mm pattern | RPI-ZERO-V1_2 mechanical drawing; the MJCF still carries the Pi-Zero PCB mesh |

Connectivity is **bound from `electronics/netlist.py`** (the rung-4 Design)
via `board.bind()` — no net was retyped. Terminals of the robot netlist that
are not pads of this board (the Radxa itself, the CSI camera) are resolved
out with their reasons recorded in `board.notes`; the code and the DRC
binding check keep the two models honest against each other.

## The eight reconstruction decisions (D1-D8)

Each is a fact Pollen has not published, decided by us and stated in
`board.py`'s header: **D1** Pololu D30V30F5 as the 5 V regulator; **D2** the
pack passed raw to SERVO_V through a 0-ohm link (the XL330 band is 3.7-6.0 V
— docs §3.4 open question 1 stands, the link makes the assumption removable);
**D3** direction-less half-duplex from one 74LVC1G125 (OE = TX, A = GND,
Y = DATA, RX through a 0-ohm) since robotd drives no TX-enable; **D4** 3.3 V
taken from header pins 1 and 17; **D5** the codec's 1.8 V DVDD deliberately
NOT solved — it ends on test point TP1, because inventing a regulator would
fake a fact; **D6** speaker on HPLOUT/HPLCOM, mic on MIC2R ("Mic3R" exists
nowhere in SLAS510G); **D7** J5 pin order per the Qwiic convention; **D8**
JST EH as the servo connector ("X3P" appears on no vendor page fetched).

## Verdict (2026-09-02 build)

See `out/fab/README.txt` for the shipped verdict. Fill pattern:

- DRC: __VERDICT__ — __COUNTS__
- routed __ROUTED__ connections; GND poured on B.Cu after routing (the
  islands check treats a pour optimistically — the bottom plot was looked at)
- self-test: a part moved off the outline is caught by `placement`; a dropped
  pin map is caught by `binding` (run `--self-test`)

## CANNOT DETERMINE (what a teardown or Pollen would settle)

- The real HAT's schematic, layout, connector types and positions — all of
  it. This board is a functional stand-in, not a copy.
- SERVO_V: raw pack vs regulated (D2 is our reading of model.rs; a meter on
  a production servo VDD settles it — docs §3.4 open question 1).
- The fitted half-duplex transceiver (D3 is our topology; ROBOTIS' reference
  is a 74LVC2G241 with a TX-enable robotd never drives).
- The 1.8 V rail for the codec's DVDD (TP1 is the honest gap, D5). The codec
  cannot run until it is fed.
- Which codec input the mic uses, whether an amplifier drives the speaker,
  MICBIAS level, decoupling values (100 nF is our practice, unsourced).
- J5 pinout, ToF generation (L5CX vs L8CX), NFC (absent here — no published
  code names a reader IC), REC LED (absent here — no GPIO named anywhere).
- J5's land pattern is deliberately UNCONFIRMED: the eSH side-entry figure's
  5.55/4.0/1.8 callouts were not fully resolved into the construction.
- Current draws: no net on this board has a documented figure (the HAT's own
  draw, the Radxa's draw and the servo bus total are all unpublished), so
  `check_current` reports CANNOT DETERMINE rather than a blessing.
- Fab rules: `jlcpcb_2l_standard` was confirmed against a 2026-08 snapshot
  of JLCPCB's capability page — re-read the live page before ordering (the
  fab README repeats this).

## Files

- `board.py` — the whole board, parameters first, every figure cited
- `out/top.svg`, `out/bottom.svg` — the plots with DRC findings circled
- `out/fab/` — Gerber X2, Excellon (plated/unplated split), BOM with
  provenance, pick-and-place, `.kicad_pcb`, README.txt, zip
