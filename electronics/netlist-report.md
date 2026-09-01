# Microduck netlist — three-verdict report

*Generated 2026-09-02 02:19 by `electronics/netlist.py` (GOAL.md rung 4). Host `radxa-zero-3w` (RK3566), 25 parts, 28 nets, 118 findings. Nothing here was measured on a robot; every figure is a quote from the file its cite names.*

## Verdict: **FAIL**

75 PASS · 15 FAIL · 28 CANNOT DETERMINE. `bool(report)` is False on either of the last two — the conservative answer.

| rule | PASS | FAIL | CANNOT DETERMINE |
|---|---|---|---|
| `cross/wiring` | 1 | 0 | 0 |
| `csi` | 1 | 0 | 0 |
| `current/HAT_1V8` | 0 | 0 | 2 |
| `current/HAT_3V3` | 0 | 0 | 2 |
| `current/J5_3V3` | 0 | 0 | 2 |
| `current/MICBIAS` | 0 | 0 | 2 |
| `current/SERVO_V` | 0 | 0 | 2 |
| `current/V5_HAT` | 0 | 0 | 2 |
| `current/VBAT` | 0 | 0 | 2 |
| `current/VCC_3V3_CSI` | 0 | 0 | 2 |
| `dxl/ids` | 2 | 0 | 0 |
| `gpio` | 1 | 0 | 0 |
| `host_power` | 2 | 0 | 0 |
| `i2c` | 3 | 0 | 0 |
| `i2c3/overlay` | 1 | 0 | 0 |
| `i2s` | 1 | 0 | 0 |
| `pin_directions` | 25 | 0 | 0 |
| `power/HAT_1V8` | 0 | 0 | 1 |
| `power/HAT_3V3` | 0 | 0 | 1 |
| `power/J5_3V3` | 1 | 0 | 0 |
| `power/MICBIAS` | 1 | 0 | 0 |
| `power/SERVO_V` | 1 | 0 | 0 |
| `power/V5_HAT` | 1 | 0 | 0 |
| `power/VBAT` | 1 | 0 | 0 |
| `power/VCC_3V3_CSI` | 1 | 0 | 0 |
| `span` | 25 | 0 | 0 |
| `uart` | 3 | 0 | 0 |
| `vocabulary/need` | 0 | 0 | 3 |
| `vocabulary/provision` | 0 | 0 | 3 |
| `volts/HAT_1V8` | 0 | 0 | 1 |
| `volts/HAT_3V3` | 0 | 0 | 1 |
| `volts/J5_3V3` | 1 | 0 | 0 |
| `volts/MICBIAS` | 0 | 0 | 1 |
| `volts/SERVO_V` | 0 | 15 | 1 |
| `volts/V5_HAT` | 1 | 0 | 0 |
| `volts/VBAT` | 1 | 0 | 0 |
| `volts/VCC_3V3_CSI` | 1 | 0 | 0 |

## The FAILs — what the published design contradicts

- **`volts/SERVO_V`** × 15 — id20.VDD, id21.VDD, id22.VDD, id23.VDD, id24.VDD, id30.VDD, id31.VDD, id32.VDD, id33.VDD, id34.VDD, id10.VDD, id11.VDD, id12.VDD, id13.VDD, id14.VDD
  - SERVO_V is 6.6..8.2 V (declared by the design); id20 (xl330-m288-t) states 3.7..6.0 V for VDD.
  - "Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])" (E1 §Specifications, row verbatim: 'Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])'. v_typ = 5.0 is the vendor's stated 'Recommended', not a characterisation point. NAMED CONFLICT WITH THE DESIGN, not with another source: Pollen's runtime maps the pack 6.6-8.2 V through this servo's own Present Input Voltage(144) (docs/ELECTRONICS-AND-SOFTWARE.md §3.4), 0.6-2.2 V above this v_max; and robotd writes Shutdown(63) = 52 = 0b00110100 where the vendor default is 53 = 0b00110101 - the one bit cleared is Bit 0 'Input Voltage Error', the fault that E1 says fires when Present Input Voltage(144) leaves the Min/Max Voltage Limit window (max 7.0 V). That is consistent with the servos seeing the raw pack and is recorded as an OBSERVATION on Pollen's code, not as a vendor figure. Whether a production Microduck runs stock XL330s over their rating stays CANNOT DETERMINE (a meter on servo VDD settles it).)

The SERVO_V FAIL is the design AS PUBLISHED against the vendor band: model.rs reads 6.6–8.2 V through the servos' own Present Input Voltage register and the XL330-M288-T's input band is 3.7–6.0 V (docs/ELECTRONICS-AND-SOFTWARE.md §3.4, open question 1). It is not a wiring error in this netlist; what settles it is a meter on a production servo's VDD pin, or Pollen naming a regulated bus or a custom variant. The checks this rung asked for — one controller per bus, unique I2C3 addresses (0x18/0x19/0x68/0x29), unique bus IDs (10–14, 20–24, 30–34, 200), no pin on two nets — PASS above.

## The CANNOT DETERMINEs — by name, with what settles each

- **`power/HAT_1V8` system** — codec@direct draws HAT_1V8 — NOT ONE part in the catalogue has a
- **`power/HAT_3V3` system** — codec@direct, bmi088@direct draw HAT_3V3 — NOT ONE part in the catalogue has a
- **`current/HAT_1V8` typical draw** — 1 of 1 part(s) drawing HAT_1V8 have no sourced typical current:
- **`current/HAT_1V8` peak draw** — 1 of 1 part(s) drawing HAT_1V8 have no sourced peak current:
- **`current/HAT_3V3` typical draw** — 1 of 2 part(s) drawing HAT_3V3 have no sourced typical current:
- **`current/HAT_3V3` peak draw** — 2 of 2 part(s) drawing HAT_3V3 have no sourced peak current:
- **`current/J5_3V3` typical draw** — J5_3V3 typical demand is 95 mA, from all 1 part(s) drawing it:
- **`current/J5_3V3` peak draw** — J5_3V3 peak demand is 150 mA, from all 1 part(s) drawing it:
- **`current/MICBIAS` typical draw** — 1 of 1 part(s) drawing MICBIAS have no sourced typical current:
- **`current/MICBIAS` peak draw** — 1 of 1 part(s) drawing MICBIAS have no sourced peak current:
- **`current/SERVO_V` typical draw** — 15 of 16 part(s) drawing SERVO_V have no sourced typical current:
- **`current/SERVO_V` peak draw** — 16 of 16 part(s) drawing SERVO_V have no sourced peak current:
- **`current/V5_HAT` typical draw** — 1 of 1 part(s) drawing V5_HAT have no sourced typical current:
- **`current/V5_HAT` peak draw** — 1 of 1 part(s) drawing V5_HAT have no sourced peak current:
- **`current/VBAT` typical draw** — 1 of 1 part(s) drawing VBAT have no sourced typical current:
- **`current/VBAT` peak draw** — 1 of 1 part(s) drawing VBAT have no sourced peak current:
- **`current/VCC_3V3_CSI` typical draw** — 1 of 1 part(s) drawing VCC_3V3_CSI have no sourced typical current:
- **`current/VCC_3V3_CSI` peak draw** — 1 of 1 part(s) drawing VCC_3V3_CSI have no sourced peak current:
- **`vocabulary/provision` hat.SPK+** — microduck-robot-hat-pcb terminal 'SPK+' states provision 'audio_output', which is not one of the three
- **`vocabulary/provision` hat.SPK-** — microduck-robot-hat-pcb terminal 'SPK-' states provision 'audio_output', which is not one of the three
- **`vocabulary/provision` hat.MIC_IN** — microduck-robot-hat-pcb terminal 'MIC_IN' states provision 'audio_input', which is not one of the three
- **`vocabulary/need` speaker.SPK+** — microduck-speaker terminal 'SPK+' states need 'audio_output', which is not one of the four kinds
- **`vocabulary/need` speaker.SPK-** — microduck-speaker terminal 'SPK-' states need 'audio_output', which is not one of the four kinds
- **`vocabulary/need` mic.MIC** — microduck-mic terminal 'MIC' states need 'audio_input', which is not one of the four kinds
- **`volts/HAT_1V8` source** — 1 sink(s) on HAT_1V8 and no stated voltage: no provision on this net states a nominal_v and the design declares no band.
- **`volts/HAT_3V3` source** — 4 sink(s) on HAT_3V3 and no stated voltage: no provision on this net states a nominal_v and the design declares no band.
- **`volts/MICBIAS` source** — 1 sink(s) on MICBIAS and no stated voltage: no provision on this net states a nominal_v and the design declares no band.
- **`volts/SERVO_V` imu200.VDD** — SERVO_V is 6.6..8.2 V (declared by the design); imu200 (microduck-imu-to-dxl) states no v_min/v_max for VDD.

What settles the ones that matter: the Robot HAT schematic (regulators, transceiver, rails, connectors) — Pollen publishing it or a teardown; a meter on a servo's VDD pin for the 6.6-8.2 V question; the dts pinctrl for the I2S3 mux; `i2cdetect -y 3` on a production HAT for the BMI088.

## Nets

```
  net         scope    kind    deg  terminals
  GND         host     ground   24  host.GND, battery.BAT-, hat.GND, codec.GND, bmi088.GND, tof.GND, imu200.GND, id20.GND, id21.GND, id22.GND, id23.GND, id24.GND, id30.GND, id31.GND, id32.GND, id33.GND, id34.GND, id10.GND, id11.GND, id12.GND, id13.GND, id14.GND, camera.GND, mic.GND
  MIC_IN      host     signal    2  hat.MIC_IN, mic.MIC
  SPK_N       host     signal    2  hat.SPK-, speaker.SPK-
  SPK_P       host     signal    2  hat.SPK+, speaker.SPK+
  csi/CLK     bus      signal    2  host.CLK, camera.CSI_CLK
  csi/D0      bus      signal    2  host.D0, camera.CSI_D0
  csi/D1      bus      signal    2  host.D1, camera.CSI_D1
  csi17       host     signal    1  camera.PDN
  dxl/DATA    bus      signal   18  host.DATA, hat.DXL_DATA, imu200.DATA, id20.DATA, id21.DATA, id22.DATA, id23.DATA, id24.DATA, id30.DATA, id31.DATA, id32.DATA, id33.DATA, id34.DATA, id10.DATA, id11.DATA, id12.DATA, id13.DATA, id14.DATA
  i2c2/SCL    bus      signal    2  host.SCL, camera.I2C2_SCL
  i2c2/SDA    bus      signal    2  host.SDA, camera.I2C2_SDA
  i2c3/SCL    bus      signal    6  host.SCL, hat.I2C3_SCL, codec.SCL, bmi088.SCL, bmi088.gyro.SCL, tof.SCL
  i2c3/SDA    bus      signal    6  host.SDA, hat.I2C3_SDA, codec.SDA, bmi088.SDA, bmi088.gyro.SDA, tof.SDA
  i2s3/BCLK   bus      signal    3  host.BCLK, hat.I2S3_SCLK, codec.BCLK
  i2s3/DIN    bus      signal    3  host.DIN, hat.I2S3_SDO, codec.DIN
  i2s3/DOUT   bus      signal    3  host.DOUT, hat.I2S3_SDI, codec.DOUT
  i2s3/MCLK   bus      signal    3  host.MCLK, hat.MCLK, codec.MCLK
  i2s3/WCLK   bus      signal    3  host.WCLK, hat.I2S3_LRCK, codec.WCLK
  uart2/RX    bus      signal    2  host.RX, hat.UART2_RX
  uart2/TX    bus      signal    2  host.TX, hat.UART2_TX
  HAT_1V8     host     supply    1  codec.DVDD
  HAT_3V3     host     supply    4  codec.AVDD, codec.IOVDD, bmi088.VDD, bmi088.VDDIO
  J5_3V3      host     supply    2  hat.J5_3V3, tof.3V3
  MICBIAS     host     supply    2  hat.MICBIAS, mic.BIAS
  SERVO_V     host     supply   17  hat.SERVO_V, imu200.VDD, id20.VDD, id21.VDD, id22.VDD, id23.VDD, id24.VDD, id30.VDD, id31.VDD, id32.VDD, id33.VDD, id34.VDD, id10.VDD, id11.VDD, id12.VDD, id13.VDD, id14.VDD
  V5_HAT      host     supply    2  host.5V, hat.V5_OUT
  VBAT        host     supply    2  battery.BAT+, hat.VBAT
  VCC_3V3_CSI host     supply    1  camera.VCC_3V3
```

## Every finding, in full

```

=== NET CHECK  microduck on radxa-zero-3w (RK3566) ===
  standards: none
  25 part(s), 0 of 0 port(s) used, 28 nets
  note  nothing here reserves a terminal, and no port carries an alternate function.
  note  nets carrying more than one device — a bus, not a collision:
          MIC_IN degree 2 (hat, mic)
          SPK_N degree 2 (hat, speaker)
          SPK_P degree 2 (hat, speaker)
          dxl/DATA degree 18 (hat, imu200, id20, id21, id22, id23, id24, id30, id31, id32, id33, id34, id10, id11, id12, id13, id14)
          i2c3/SCL degree 6 (hat, codec, bmi088, bmi088.gyro, tof)
          i2c3/SDA degree 6 (hat, codec, bmi088, bmi088.gyro, tof)
          i2s3/BCLK degree 3 (hat, codec)
          i2s3/DIN degree 3 (hat, codec)
          i2s3/DOUT degree 3 (hat, codec)
          i2s3/MCLK degree 3 (hat, codec)
          i2s3/WCLK degree 3 (hat, codec)
        The standard says these are shared, in as many words:
          
  note  host power: 2 of 2 stated host need(s) joined to a net.
        The host is a SINK on each of them, so an unfed one is the ordinary unsourced-supply
        finding in `power`, on the same net, from the same terminal.
  note  power: TOPOLOGY ONLY. This is who drives a net and who draws it. It
        cannot become a budget from this data, and none is implied. The DEMAND
        side comes from datasheets in cecad/data/chips.json and is check_current()'s
        question, not this one's.
  note  ground: GND.
        Directions on a return path are a modelling convention rather than a claim any
        document makes, so this rule does not judge them.
  note  current: the DEMAND side only, in mA, summed per NET over the parts
        attached here. Every figure comes from cecad/data/chips.json, read off
        a manufacturer datasheet, and is attributed to a net because a part's
        own `current_from` points at it — never because a rail name matched. A
        part with no sourced figure makes its net's TOTAL undetermined; it is
        never counted as zero, because a missing current is not a zero current
        and that is how a budget silently passes.
  note  peripheral demand in this system: CSI x1, GPIO x1, I2C x2, I2S x1, UART x1
        Counted per DISTINCT NET GROUP, not per part. Five devices daisy-chained on one
        segment want ONE peripheral, not five, and the per-part count is simply the wrong
        number.
        There is no wiring-level rule here to pass or fail, so this carries no verdict.
  note  bus nets and their degree — reported, never scored:
          csi/CLK                degree 2
          csi/D0                 degree 2
          csi/D1                 degree 2
          dxl/DATA               degree 18
          i2c2/SCL               degree 2
          i2c2/SDA               degree 2
          i2c3/SCL               degree 6
          i2c3/SDA               degree 6
          i2s3/BCLK              degree 3
          i2s3/DIN               degree 3
          i2s3/DOUT              degree 3
          i2s3/MCLK              degree 3
          i2s3/WCLK              degree 3
          uart2/RX               degree 2
          uart2/TX               degree 2
        Neither standard loaded here states pull-up ownership, value or a bus capacitance
        budget (pullups: null, with a stated reason), so nothing can be judged. The count is
        exactly the fact somebody needs when a document says to adjust the pull-ups "depending
        on what is connected".
  [PASS]              span           battery@direct
                      np-f550 is attached directly to named host terminals; there is no port for a span to mismatch.
                      A check that quietly does not run is indistinguishable from one that passed, so it says so.
  [PASS]              span           hat@direct
                      microduck-robot-hat-pcb is attached directly to named host terminals; there is no port for a span to mismatch.
                      A check that quietly does not run is indistinguishable from one that passed, so it says so.
  [PASS]              span           codec@direct
                      tlv320aic3104 is attached directly to named host terminals; there is no port for a span to mismatch.
                      A check that quietly does not run is indistinguishable from one that passed, so it says so.
  [PASS]              span           bmi088@direct
                      bmi088 is attached directly to named host terminals; there is no port for a span to mismatch.
                      A check that quietly does not run is indistinguishable from one that passed, so it says so.
  [PASS]              span           bmi088.gyro@direct
                      bmi088 is attached directly to named host terminals; there is no port for a span to mismatch.
                      A check that quietly does not run is indistinguishable from one that passed, so it says so.
  [PASS]              span           tof@direct
                      microduck-tof-module is attached directly to named host terminals; there is no port for a span to mismatch.
                      A check that quietly does not run is indistinguishable from one that passed, so it says so.
  [PASS]              span           imu200@direct
                      microduck-imu-to-dxl is attached directly to named host terminals; there is no port for a span to mismatch.
                      A check that quietly does not run is indistinguishable from one that passed, so it says so.
  [PASS]              span           id20@direct
                      xl330-m288-t is attached directly to named host terminals; there is no port for a span to mismatch.
                      A check that quietly does not run is indistinguishable from one that passed, so it says so.
  [PASS]              span           id21@direct
                      xl330-m288-t is attached directly to named host terminals; there is no port for a span to mismatch.
                      A check that quietly does not run is indistinguishable from one that passed, so it says so.
  [PASS]              span           id22@direct
                      xl330-m288-t is attached directly to named host terminals; there is no port for a span to mismatch.
                      A check that quietly does not run is indistinguishable from one that passed, so it says so.
  [PASS]              span           id23@direct
                      xl330-m288-t is attached directly to named host terminals; there is no port for a span to mismatch.
                      A check that quietly does not run is indistinguishable from one that passed, so it says so.
  [PASS]              span           id24@direct
                      xl330-m288-t is attached directly to named host terminals; there is no port for a span to mismatch.
                      A check that quietly does not run is indistinguishable from one that passed, so it says so.
  [PASS]              span           id30@direct
                      xl330-m288-t is attached directly to named host terminals; there is no port for a span to mismatch.
                      A check that quietly does not run is indistinguishable from one that passed, so it says so.
  [PASS]              span           id31@direct
                      xl330-m288-t is attached directly to named host terminals; there is no port for a span to mismatch.
                      A check that quietly does not run is indistinguishable from one that passed, so it says so.
  [PASS]              span           id32@direct
                      xl330-m288-t is attached directly to named host terminals; there is no port for a span to mismatch.
                      A check that quietly does not run is indistinguishable from one that passed, so it says so.
  [PASS]              span           id33@direct
                      xl330-m288-t is attached directly to named host terminals; there is no port for a span to mismatch.
                      A check that quietly does not run is indistinguishable from one that passed, so it says so.
  [PASS]              span           id34@direct
                      xl330-m288-t is attached directly to named host terminals; there is no port for a span to mismatch.
                      A check that quietly does not run is indistinguishable from one that passed, so it says so.
  [PASS]              span           id10@direct
                      xl330-m288-t is attached directly to named host terminals; there is no port for a span to mismatch.
                      A check that quietly does not run is indistinguishable from one that passed, so it says so.
  [PASS]              span           id11@direct
                      xl330-m288-t is attached directly to named host terminals; there is no port for a span to mismatch.
                      A check that quietly does not run is indistinguishable from one that passed, so it says so.
  [PASS]              span           id12@direct
                      xl330-m288-t is attached directly to named host terminals; there is no port for a span to mismatch.
                      A check that quietly does not run is indistinguishable from one that passed, so it says so.
  [PASS]              span           id13@direct
                      xl330-m288-t is attached directly to named host terminals; there is no port for a span to mismatch.
                      A check that quietly does not run is indistinguishable from one that passed, so it says so.
  [PASS]              span           id14@direct
                      xl330-m288-t is attached directly to named host terminals; there is no port for a span to mismatch.
                      A check that quietly does not run is indistinguishable from one that passed, so it says so.
  [PASS]              span           camera@direct
                      microduck-camera-module is attached directly to named host terminals; there is no port for a span to mismatch.
                      A check that quietly does not run is indistinguishable from one that passed, so it says so.
  [PASS]              span           speaker@direct
                      microduck-speaker is attached directly to named host terminals; there is no port for a span to mismatch.
                      A check that quietly does not run is indistinguishable from one that passed, so it says so.
  [PASS]              span           mic@direct
                      microduck-mic is attached directly to named host terminals; there is no port for a span to mismatch.
                      A check that quietly does not run is indistinguishable from one that passed, so it says so.
  [PASS]              gpio           board
                      19 distinct controller pin identifier(s) across 28 net(s), no identifier on two nets, and every signal net in use resolves to one.
  [ASSERTED]          host_power     radxa-zero-3w.5V
                      radxa-zero-3w's supply '5V' joins net 'V5_HAT' (supply, 2 terminal(s)).
                      Whether that net is FED is the same net's power/V5_HAT finding, asked once, there.
                      you asserted: "[brief] §5.1 '5V Power from the GPIO PIN 2 & 4'; the HAT makes it from the pack: i2c3.dts:22 'In-robot power comes from the battery via the HAT regardless'. The HAT's regulator is CANNOT DETERMINE. The USB-C OTG port is a second 5 V path when tethered (sch1.12 sheet 22) and is not on this netlist."
  [ASSERTED]          host_power     radxa-zero-3w.GND
                      radxa-zero-3w's ground 'GND' joins net 'GND' (ground, 24 terminal(s)).
                      Whether that net is FED is the same net's power/GND finding, asked once, there.
                      you asserted: "[brief] §5.1 '5V Power from the GPIO PIN 2 & 4'; the HAT makes it from the pack: i2c3.dts:22 'In-robot power comes from the battery via the HAT regardless'. The HAT's regulator is CANNOT DETERMINE. The USB-C OTG port is a second 5 V path when tethered (sch1.12 sheet 22) and is not on this netlist."
  [CANNOT DETERMINE]  power/HAT_1V8  system
                      codec@direct draws HAT_1V8 — NOT ONE part in the catalogue has a
                      HAT_1V8 terminal with direction 'output'.
                      Not a pass and not a fail. Connect it yourself, and find out where it comes from before
                      anything is powered up. That answer is not in this repository.
                      To assert it:  design.external_supply('HAT_1V8', "<what you measured>")
                      standard: "A bare host: pin identifiers come from the DESIGN FILE through
                      .wire() and .declare_segment(), recorded as the user's assertion — the
                      esp32s3_raw arrangement. The header_40pin and buses_the_microduck_uses
                      blocks below are the vendor's pin→function table those identifiers are
                      checked against by a reader, not by this loader."
                      (hosts[radxa-zero-3w].provides_basis)
  [CANNOT DETERMINE]  power/HAT_3V3  system
                      codec@direct, bmi088@direct draw HAT_3V3 — NOT ONE part in the catalogue has a
                      HAT_3V3 terminal with direction 'output'.
                      Not a pass and not a fail. Connect it yourself, and find out where it comes from before
                      anything is powered up. That answer is not in this repository.
                      To assert it:  design.external_supply('HAT_3V3', "<what you measured>")
                      standard: "A bare host: pin identifiers come from the DESIGN FILE through
                      .wire() and .declare_segment(), recorded as the user's assertion — the
                      esp32s3_raw arrangement. The header_40pin and buses_the_microduck_uses
                      blocks below are the vendor's pin→function table those identifiers are
                      checked against by a reader, not by this loader."
                      (hosts[radxa-zero-3w].provides_basis)
  [PASS]              power/J5_3V3   system
                      hat@direct sources J5_3V3 (terminal J5_3V3); 1 part(s) draw it: tof.
                      Every other terminal on this net states a direction, so nothing else may be driving it.
  [PASS]              power/MICBIAS  system
                      hat@direct sources MICBIAS (terminal MICBIAS); 1 part(s) draw it: mic.
                      Every other terminal on this net states a direction, so nothing else may be driving it.
  [PASS]              power/SERVO_V  system
                      hat@direct sources SERVO_V (terminal SERVO_V); 16 part(s) draw it: imu200, id20, id21, id22, id23, id24, id30, id31, id32, id33, id34, id10, id11, id12, id13, id14.
                      Every other terminal on this net states a direction, so nothing else may be driving it.
  [PASS]              power/V5_HAT   system
                      hat@direct sources V5_HAT (terminal V5_OUT); 1 part(s) draw it: host.
                      Every other terminal on this net states a direction, so nothing else may be driving it.
  [PASS]              power/VBAT     system
                      battery@direct sources VBAT (terminal BAT+); 1 part(s) draw it: hat.
                      Every other terminal on this net states a direction, so nothing else may be driving it.
  [ASSERTED]          power/VCC_3V3_CSIsystem
                      VCC_3V3_CSI is supplied from outside the documents, on your statement.
                      Drawn by: camera.
                      Every terminal on this net states a direction, so nothing here may also be driving it.
                      you asserted: "MIPI CSI pin 22 is the Radxa's own 3.3 V: [wiki] 22-pin table '22 VCC_3V3' (part:radxa-zero-3w buses_the_microduck_uses.mipi_csi). The host record states no supply provision, so this is asserted from the vendor table rather than routed by a record."
  [CANNOT DETERMINE]  current/HAT_1V8typical draw
                      1 of 1 part(s) drawing HAT_1V8 have no sourced typical current:
                        codec@direct           (no chip named) NOT SOURCED
                            the sheet's IDVDD rows (2.3 mA playback, 2.45 mA record, p.12 —
                            chips[tlv320aic3104].current_mA.typical_basis) are per mode and the
                            chip record records no single typical; carried as null rather than
                            picked.
                      NOTHING drawing HAT_1V8 here has a sourced typical figure, so there is no floor either —
                      not 0 mA, not any number. This net's demand is simply unknown.
                      To close it: fetch the datasheet and add the part to cecad/data/chips.json, or
                      measure it and record what you found.
                      datasheet: "the sheet's IDVDD rows (2.3 mA playback, 2.45 mA record, p.12 —
                      chips[tlv320aic3104].current_mA.typical_basis) are per mode and the chip
                      record records no single typical; carried as null rather than picked."
                      (chips[tlv320aic3104].supplies[1].cite (§8.3 p.7; pin 32))
  [CANNOT DETERMINE]  current/HAT_1V8peak draw
                      1 of 1 part(s) drawing HAT_1V8 have no sourced peak current:
                        codec@direct           (no chip named) NOT SOURCED
                            the sheet's IDVDD rows (2.3 mA playback, 2.45 mA record, p.12 —
                            chips[tlv320aic3104].current_mA.typical_basis) are per mode and the
                            chip record records no single typical; carried as null rather than
                            picked.
                      NOTHING drawing HAT_1V8 here has a sourced peak figure, so there is no floor either —
                      not 0 mA, not any number. This net's demand is simply unknown.
                      To close it: fetch the datasheet and add the part to cecad/data/chips.json, or
                      measure it and record what you found.
                      datasheet: "the sheet's IDVDD rows (2.3 mA playback, 2.45 mA record, p.12 —
                      chips[tlv320aic3104].current_mA.typical_basis) are per mode and the chip
                      record records no single typical; carried as null rather than picked."
                      (chips[tlv320aic3104].supplies[1].cite (§8.3 p.7; pin 32))
  [CANNOT DETERMINE]  current/HAT_3V3typical draw
                      1 of 2 part(s) drawing HAT_3V3 have no sourced typical current:
                        codec@direct           tlv320aic3104  NOT SOURCED
                            NOT A SINGLE NUMBER — the sheet gives per-mode rows, §8.x 'CURRENT
                            CONSUMPTION – DRVDD = AVDD = IOVDD = 3.3 V, DVDD = 1.8 V', p.12,
                            verbatim: 'IDRVDD + IAVDD | Stereo DAC playback to lineout, fS = 48
                            ksps, I2S slave, no signal | 4.9' mA and 'IDVDD | 2.3' mA; 'IDRVDD +
                            IAVDD | Stereo ADC record, fS = 48 ksps, I2S slave, AGC off, no signal
                            | 4.31(6)' mA and 'IDVDD | 2.45(6)' mA; 'IDRVDD + IAVDD | Stereo DAC
                            playback to stereo single-ended headphone, fS = 48 ksps, I2S slave, no
                            signal | 6.7' mA. All 'no signal' — the sheet gives no figure for
                            current INTO a speaker load, so speaker-drive current is CANNOT
                            DETERMINE.
                      sourced so far:
                        bmi088@direct          bmi088              5.15 mA
                      That comes to 5.15 mA, which is a FLOOR and NOT the total. The missing parts
                      are not drawing zero — nobody wrote down what they draw. Adding them in as 0 mA
                      is how a budget passes a net that browns out on the bench.
                      To close it: fetch the datasheet and add the part to cecad/data/chips.json, or
                      measure it and record what you found.
                      datasheet: "NOT A SINGLE NUMBER — the sheet gives per-mode rows, §8.x
                      'CURRENT CONSUMPTION – DRVDD = AVDD = IOVDD = 3.3 V, DVDD = 1.8 V', p.12,
                      verbatim: 'IDRVDD + IAVDD | Stereo DAC playback to lineout, fS = 48 ksps,
                      I2S slave, no signal | 4.9' mA and 'IDVDD | 2.3' mA; 'IDRVDD + IAVDD |
                      Stereo ADC record, fS = 48 ksps, I2S slave, AGC off, no signal | 4.31(6)' mA
                      and 'IDVDD | 2.45(6)' mA; 'IDRVDD + IAVDD | Stereo DAC playback to stereo
                      single-ended headphone, fS = 48 ksps, I2S slave, no signal | 6.7' mA. All
                      'no signal' — the sheet gives no figure for current INTO a speaker load, so
                      speaker-drive current is CANNOT DETERMINE."
                      (chips[tlv320aic3104].current_mA.typical_basis)
  [CANNOT DETERMINE]  current/HAT_3V3peak draw
                      2 of 2 part(s) drawing HAT_3V3 have no sourced peak current:
                        codec@direct           tlv320aic3104  NOT SOURCED
                            NOT TRANSCRIBED HERE. No peak figure was read out of the document this
                            block cites (see `cite`) when this record was written, and none is
                            asserted now (basis added 2026-09-02, wiring lane, so
                            cecad.electrical's loader can read the shelf: a null with no reason is
                            refused). Null means not looked up in this record — NOT zero. Re-read
                            the sheet's current-consumption table to fill it.
                        bmi088@direct          bmi088         NOT SOURCED
                            NOT TRANSCRIBED HERE. No peak figure was read out of the document this
                            block cites (see `cite`) when this record was written, and none is
                            asserted now (basis added 2026-09-02, wiring lane, so
                            cecad.electrical's loader can read the shelf: a null with no reason is
                            refused). Null means not looked up in this record — NOT zero. Re-read
                            the sheet's current-consumption table to fill it.
                      NOTHING drawing HAT_3V3 here has a sourced peak figure, so there is no floor either —
                      not 0 mA, not any number. This net's demand is simply unknown.
                      To close it: fetch the datasheet and add the part to cecad/data/chips.json, or
                      measure it and record what you found.
                      datasheet: "NOT TRANSCRIBED HERE. No peak figure was read out of the
                      document this block cites (see `cite`) when this record was written, and
                      none is asserted now (basis added 2026-09-02, wiring lane, so
                      cecad.electrical's loader can read the shelf: a null with no reason is
                      refused). Null means not looked up in this record — NOT zero. Re-read the
                      sheet's current-consumption table to fill it."
                      (chips[tlv320aic3104].current_mA.peak_basis)
  [CANNOT DETERMINE]  current/J5_3V3 typical draw
                      J5_3V3 typical demand is 95 mA, from all 1 part(s) drawing it:
                        tof@direct             vl53l5cx              95 mA
                      THE DEMAND IS KNOWN. THE SUPPLY IS NOT. No document read here puts a NUMBER on a
                      current limit for this net, for a port or for a connector, so there is nothing to
                      compare 95 mA against and no headroom can be reported. This is a demand figure,
                      not a pass.
                      standard: "A bare host: pin identifiers come from the DESIGN FILE through
                      .wire() and .declare_segment(), recorded as the user's assertion — the
                      esp32s3_raw arrangement. The header_40pin and buses_the_microduck_uses
                      blocks below are the vendor's pin→function table those identifiers are
                      checked against by a reader, not by this loader."
                      (hosts[radxa-zero-3w].provides_basis)
  [CANNOT DETERMINE]  current/J5_3V3 peak draw
                      J5_3V3 peak demand is 150 mA, from all 1 part(s) drawing it:
                        tof@direct             vl53l5cx             150 mA
                      THE DEMAND IS KNOWN. THE SUPPLY IS NOT. No document read here puts a NUMBER on a
                      current limit for this net, for a port or for a connector, so there is nothing to
                      compare 150 mA against and no headroom can be reported. This is a demand figure,
                      not a pass.
                      standard: "A bare host: pin identifiers come from the DESIGN FILE through
                      .wire() and .declare_segment(), recorded as the user's assertion — the
                      esp32s3_raw arrangement. The header_40pin and buses_the_microduck_uses
                      blocks below are the vendor's pin→function table those identifiers are
                      checked against by a reader, not by this loader."
                      (hosts[radxa-zero-3w].provides_basis)
  [CANNOT DETERMINE]  current/MICBIAStypical draw
                      1 of 1 part(s) drawing MICBIAS have no sourced typical current:
                        mic@direct             (no chip named) NOT SOURCED
                            no part, no figure.
                      NOTHING drawing MICBIAS here has a sourced typical figure, so there is no floor either —
                      not 0 mA, not any number. This net's demand is simply unknown.
                      To close it: fetch the datasheet and add the part to cecad/data/chips.json, or
                      measure it and record what you found.
                      standard: "no part, no figure."
                      (part:tlv320aic3104 pinout — an electret needs the bias; a MEMS mic needs a VDD instead. Which this is: CANNOT DETERMINE.)
  [CANNOT DETERMINE]  current/MICBIASpeak draw
                      1 of 1 part(s) drawing MICBIAS have no sourced peak current:
                        mic@direct             (no chip named) NOT SOURCED
                            no part, no figure.
                      NOTHING drawing MICBIAS here has a sourced peak figure, so there is no floor either —
                      not 0 mA, not any number. This net's demand is simply unknown.
                      To close it: fetch the datasheet and add the part to cecad/data/chips.json, or
                      measure it and record what you found.
                      standard: "no part, no figure."
                      (part:tlv320aic3104 pinout — an electret needs the bias; a MEMS mic needs a VDD instead. Which this is: CANNOT DETERMINE.)
  [CANNOT DETERMINE]  current/SERVO_Vtypical draw
                      15 of 16 part(s) drawing SERVO_V have no sourced typical current:
                        id20@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED. E1 §Specifications gives no running or no-load current
                            - only 'Standby Current | 17 [mA]' (recorded under idle) and the three
                            stall rows (under stall). A typical running draw for a walking-gait
                            duty cycle does not exist in any vendor document fetched; it would
                            have to be measured on the bus (Present Current(126)).
                        id21@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED. E1 §Specifications gives no running or no-load current
                            - only 'Standby Current | 17 [mA]' (recorded under idle) and the three
                            stall rows (under stall). A typical running draw for a walking-gait
                            duty cycle does not exist in any vendor document fetched; it would
                            have to be measured on the bus (Present Current(126)).
                        id22@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED. E1 §Specifications gives no running or no-load current
                            - only 'Standby Current | 17 [mA]' (recorded under idle) and the three
                            stall rows (under stall). A typical running draw for a walking-gait
                            duty cycle does not exist in any vendor document fetched; it would
                            have to be measured on the bus (Present Current(126)).
                        id23@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED. E1 §Specifications gives no running or no-load current
                            - only 'Standby Current | 17 [mA]' (recorded under idle) and the three
                            stall rows (under stall). A typical running draw for a walking-gait
                            duty cycle does not exist in any vendor document fetched; it would
                            have to be measured on the bus (Present Current(126)).
                        id24@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED. E1 §Specifications gives no running or no-load current
                            - only 'Standby Current | 17 [mA]' (recorded under idle) and the three
                            stall rows (under stall). A typical running draw for a walking-gait
                            duty cycle does not exist in any vendor document fetched; it would
                            have to be measured on the bus (Present Current(126)).
                        id30@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED. E1 §Specifications gives no running or no-load current
                            - only 'Standby Current | 17 [mA]' (recorded under idle) and the three
                            stall rows (under stall). A typical running draw for a walking-gait
                            duty cycle does not exist in any vendor document fetched; it would
                            have to be measured on the bus (Present Current(126)).
                        id31@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED. E1 §Specifications gives no running or no-load current
                            - only 'Standby Current | 17 [mA]' (recorded under idle) and the three
                            stall rows (under stall). A typical running draw for a walking-gait
                            duty cycle does not exist in any vendor document fetched; it would
                            have to be measured on the bus (Present Current(126)).
                        id32@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED. E1 §Specifications gives no running or no-load current
                            - only 'Standby Current | 17 [mA]' (recorded under idle) and the three
                            stall rows (under stall). A typical running draw for a walking-gait
                            duty cycle does not exist in any vendor document fetched; it would
                            have to be measured on the bus (Present Current(126)).
                        id33@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED. E1 §Specifications gives no running or no-load current
                            - only 'Standby Current | 17 [mA]' (recorded under idle) and the three
                            stall rows (under stall). A typical running draw for a walking-gait
                            duty cycle does not exist in any vendor document fetched; it would
                            have to be measured on the bus (Present Current(126)).
                        id34@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED. E1 §Specifications gives no running or no-load current
                            - only 'Standby Current | 17 [mA]' (recorded under idle) and the three
                            stall rows (under stall). A typical running draw for a walking-gait
                            duty cycle does not exist in any vendor document fetched; it would
                            have to be measured on the bus (Present Current(126)).
                        id10@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED. E1 §Specifications gives no running or no-load current
                            - only 'Standby Current | 17 [mA]' (recorded under idle) and the three
                            stall rows (under stall). A typical running draw for a walking-gait
                            duty cycle does not exist in any vendor document fetched; it would
                            have to be measured on the bus (Present Current(126)).
                        id11@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED. E1 §Specifications gives no running or no-load current
                            - only 'Standby Current | 17 [mA]' (recorded under idle) and the three
                            stall rows (under stall). A typical running draw for a walking-gait
                            duty cycle does not exist in any vendor document fetched; it would
                            have to be measured on the bus (Present Current(126)).
                        id12@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED. E1 §Specifications gives no running or no-load current
                            - only 'Standby Current | 17 [mA]' (recorded under idle) and the three
                            stall rows (under stall). A typical running draw for a walking-gait
                            duty cycle does not exist in any vendor document fetched; it would
                            have to be measured on the bus (Present Current(126)).
                        id13@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED. E1 §Specifications gives no running or no-load current
                            - only 'Standby Current | 17 [mA]' (recorded under idle) and the three
                            stall rows (under stall). A typical running draw for a walking-gait
                            duty cycle does not exist in any vendor document fetched; it would
                            have to be measured on the bus (Present Current(126)).
                        id14@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED. E1 §Specifications gives no running or no-load current
                            - only 'Standby Current | 17 [mA]' (recorded under idle) and the three
                            stall rows (under stall). A typical running draw for a walking-gait
                            duty cycle does not exist in any vendor document fetched; it would
                            have to be measured on the bus (Present Current(126)).
                      sourced so far:
                        imu200@direct          LSM6DSV16X          0.65 mA
                      That comes to 0.65 mA, which is a FLOOR and NOT the total. The missing parts
                      are not drawing zero — nobody wrote down what they draw. Adding them in as 0 mA
                      is how a budget passes a net that browns out on the bench.
                      conditions on the figures that were used — every one of these is the datasheet's
                      own caveat, not a doubt invented here:
                        - imu200@direct (LSM6DSV16X):
                            Table 4 states no characterisation voltage in its header (unlike the
                            LSM6DSOX sheet); Table 5 (Qvar) and Table 7 (SPI timing) are '@ Vdd_IO
                            = 1.8 V, T = 25 degC'. No current-vs-supply curve exists, so 0.65 mA
                            cannot be derated to 3.3 V from this document.
                        - imu200@direct (LSM6DSV16X):
                            The SFLP block's own current is not broken out; the figure is the
                            combo sensor in high-performance mode.
                      To close it: fetch the datasheet and add the part to cecad/data/chips.json, or
                      measure it and record what you found.
                      datasheet: "NOT PUBLISHED. E1 §Specifications gives no running or no-load
                      current - only 'Standby Current | 17 [mA]' (recorded under idle) and the
                      three stall rows (under stall). A typical running draw for a walking-gait
                      duty cycle does not exist in any vendor document fetched; it would have to
                      be measured on the bus (Present Current(126))."
                      (chips[XL330-M288-T].current_mA.typical_basis)
  [CANNOT DETERMINE]  current/SERVO_Vpeak draw
                      16 of 16 part(s) drawing SERVO_V have no sourced peak current:
                        imu200@direct          LSM6DSV16X     NOT SOURCED
                            NOT SPECIFIED. Every current row of Table 4 fills only the Typ. column
                            (Min./Max. empty) and footnote 1 reads 'Typical specifications are not
                            guaranteed.' No inrush figure; only 'Ton | Turn-on time - gyroscope |
                            30 | ms'.
                        id20@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED as a peak. The controller's ceiling is E1 §Control Table
                            'Current Limit(38) | RW | 1,750 | 0 ~ 1,750 | 1 [mA]' - the maximum
                            the firmware will command, not a measured peak; the vendor stall rows
                            top out at 1.74 A at 6.0 V. Kept out of `peak` so no budget sums a
                            limit as a draw.
                        id21@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED as a peak. The controller's ceiling is E1 §Control Table
                            'Current Limit(38) | RW | 1,750 | 0 ~ 1,750 | 1 [mA]' - the maximum
                            the firmware will command, not a measured peak; the vendor stall rows
                            top out at 1.74 A at 6.0 V. Kept out of `peak` so no budget sums a
                            limit as a draw.
                        id22@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED as a peak. The controller's ceiling is E1 §Control Table
                            'Current Limit(38) | RW | 1,750 | 0 ~ 1,750 | 1 [mA]' - the maximum
                            the firmware will command, not a measured peak; the vendor stall rows
                            top out at 1.74 A at 6.0 V. Kept out of `peak` so no budget sums a
                            limit as a draw.
                        id23@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED as a peak. The controller's ceiling is E1 §Control Table
                            'Current Limit(38) | RW | 1,750 | 0 ~ 1,750 | 1 [mA]' - the maximum
                            the firmware will command, not a measured peak; the vendor stall rows
                            top out at 1.74 A at 6.0 V. Kept out of `peak` so no budget sums a
                            limit as a draw.
                        id24@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED as a peak. The controller's ceiling is E1 §Control Table
                            'Current Limit(38) | RW | 1,750 | 0 ~ 1,750 | 1 [mA]' - the maximum
                            the firmware will command, not a measured peak; the vendor stall rows
                            top out at 1.74 A at 6.0 V. Kept out of `peak` so no budget sums a
                            limit as a draw.
                        id30@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED as a peak. The controller's ceiling is E1 §Control Table
                            'Current Limit(38) | RW | 1,750 | 0 ~ 1,750 | 1 [mA]' - the maximum
                            the firmware will command, not a measured peak; the vendor stall rows
                            top out at 1.74 A at 6.0 V. Kept out of `peak` so no budget sums a
                            limit as a draw.
                        id31@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED as a peak. The controller's ceiling is E1 §Control Table
                            'Current Limit(38) | RW | 1,750 | 0 ~ 1,750 | 1 [mA]' - the maximum
                            the firmware will command, not a measured peak; the vendor stall rows
                            top out at 1.74 A at 6.0 V. Kept out of `peak` so no budget sums a
                            limit as a draw.
                        id32@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED as a peak. The controller's ceiling is E1 §Control Table
                            'Current Limit(38) | RW | 1,750 | 0 ~ 1,750 | 1 [mA]' - the maximum
                            the firmware will command, not a measured peak; the vendor stall rows
                            top out at 1.74 A at 6.0 V. Kept out of `peak` so no budget sums a
                            limit as a draw.
                        id33@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED as a peak. The controller's ceiling is E1 §Control Table
                            'Current Limit(38) | RW | 1,750 | 0 ~ 1,750 | 1 [mA]' - the maximum
                            the firmware will command, not a measured peak; the vendor stall rows
                            top out at 1.74 A at 6.0 V. Kept out of `peak` so no budget sums a
                            limit as a draw.
                        id34@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED as a peak. The controller's ceiling is E1 §Control Table
                            'Current Limit(38) | RW | 1,750 | 0 ~ 1,750 | 1 [mA]' - the maximum
                            the firmware will command, not a measured peak; the vendor stall rows
                            top out at 1.74 A at 6.0 V. Kept out of `peak` so no budget sums a
                            limit as a draw.
                        id10@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED as a peak. The controller's ceiling is E1 §Control Table
                            'Current Limit(38) | RW | 1,750 | 0 ~ 1,750 | 1 [mA]' - the maximum
                            the firmware will command, not a measured peak; the vendor stall rows
                            top out at 1.74 A at 6.0 V. Kept out of `peak` so no budget sums a
                            limit as a draw.
                        id11@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED as a peak. The controller's ceiling is E1 §Control Table
                            'Current Limit(38) | RW | 1,750 | 0 ~ 1,750 | 1 [mA]' - the maximum
                            the firmware will command, not a measured peak; the vendor stall rows
                            top out at 1.74 A at 6.0 V. Kept out of `peak` so no budget sums a
                            limit as a draw.
                        id12@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED as a peak. The controller's ceiling is E1 §Control Table
                            'Current Limit(38) | RW | 1,750 | 0 ~ 1,750 | 1 [mA]' - the maximum
                            the firmware will command, not a measured peak; the vendor stall rows
                            top out at 1.74 A at 6.0 V. Kept out of `peak` so no budget sums a
                            limit as a draw.
                        id13@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED as a peak. The controller's ceiling is E1 §Control Table
                            'Current Limit(38) | RW | 1,750 | 0 ~ 1,750 | 1 [mA]' - the maximum
                            the firmware will command, not a measured peak; the vendor stall rows
                            top out at 1.74 A at 6.0 V. Kept out of `peak` so no budget sums a
                            limit as a draw.
                        id14@direct            XL330-M288-T   NOT SOURCED
                            NOT PUBLISHED as a peak. The controller's ceiling is E1 §Control Table
                            'Current Limit(38) | RW | 1,750 | 0 ~ 1,750 | 1 [mA]' - the maximum
                            the firmware will command, not a measured peak; the vendor stall rows
                            top out at 1.74 A at 6.0 V. Kept out of `peak` so no budget sums a
                            limit as a draw.
                      NOTHING drawing SERVO_V here has a sourced peak figure, so there is no floor either —
                      not 0 mA, not any number. This net's demand is simply unknown.
                      To close it: fetch the datasheet and add the part to cecad/data/chips.json, or
                      measure it and record what you found.
                      datasheet: "NOT SPECIFIED. Every current row of Table 4 fills only the Typ.
                      column (Min./Max. empty) and footnote 1 reads 'Typical specifications are
                      not guaranteed.' No inrush figure; only 'Ton | Turn-on time - gyroscope | 30
                      | ms'."
                      (chips[LSM6DSV16X].current_mA.peak_basis)
  [CANNOT DETERMINE]  current/V5_HAT typical draw
                      1 of 1 part(s) drawing V5_HAT have no sourced typical current:
                        host                   (no chip named) NOT SOURCED
                            Board-level current draw is NOT stated in any fetched document
                            (power[4], unknowns[1]) — a meter on the 5 V path settles it; nothing
                            is defaulted here.
                      NOTHING drawing V5_HAT here has a sourced typical figure, so there is no floor either —
                      not 0 mA, not any number. This net's demand is simply unknown.
                      To close it: fetch the datasheet and add the part to cecad/data/chips.json, or
                      measure it and record what you found.
                      standard: "Board-level current draw is NOT stated in any fetched document
                      (power[4], unknowns[1]) — a meter on the 5 V path settles it; nothing is
                      defaulted here."
                      ([brief] §5.1 p.5 — power[1] below; the path docs/ELECTRONICS-AND-SOFTWARE.md §9 infers for the HAT)
  [CANNOT DETERMINE]  current/V5_HAT peak draw
                      1 of 1 part(s) drawing V5_HAT have no sourced peak current:
                        host                   (no chip named) NOT SOURCED
                            Board-level current draw is NOT stated in any fetched document
                            (power[4], unknowns[1]) — a meter on the 5 V path settles it; nothing
                            is defaulted here.
                      NOTHING drawing V5_HAT here has a sourced peak figure, so there is no floor either —
                      not 0 mA, not any number. This net's demand is simply unknown.
                      To close it: fetch the datasheet and add the part to cecad/data/chips.json, or
                      measure it and record what you found.
                      standard: "Board-level current draw is NOT stated in any fetched document
                      (power[4], unknowns[1]) — a meter on the 5 V path settles it; nothing is
                      defaulted here."
                      ([brief] §5.1 p.5 — power[1] below; the path docs/ELECTRONICS-AND-SOFTWARE.md §9 infers for the HAT)
  [CANNOT DETERMINE]  current/VBAT   typical draw
                      1 of 1 part(s) drawing VBAT have no sourced typical current:
                        hat@direct             (no chip named) NOT SOURCED
                            The HAT's own draw (regulators, codec, transceiver) is unpublished —
                            CANNOT DETERMINE. Not zero.
                      NOTHING drawing VBAT here has a sourced typical figure, so there is no floor either —
                      not 0 mA, not any number. This net's demand is simply unknown.
                      To close it: fetch the datasheet and add the part to cecad/data/chips.json, or
                      measure it and record what you found.
                      standard: "The HAT's own draw (regulators, codec, transceiver) is
                      unpublished — CANNOT DETERMINE. Not zero."
                      (research/raw/deploy_audio_i2c3-pihat.dts:22 (via docs/ELECTRONICS-AND-SOFTWARE.md §9); the 6.6–8.2 V window is model.rs:99-128, the runtime's own, read through the servos)
  [CANNOT DETERMINE]  current/VBAT   peak draw
                      1 of 1 part(s) drawing VBAT have no sourced peak current:
                        hat@direct             (no chip named) NOT SOURCED
                            The HAT's own draw (regulators, codec, transceiver) is unpublished —
                            CANNOT DETERMINE. Not zero.
                      NOTHING drawing VBAT here has a sourced peak figure, so there is no floor either —
                      not 0 mA, not any number. This net's demand is simply unknown.
                      To close it: fetch the datasheet and add the part to cecad/data/chips.json, or
                      measure it and record what you found.
                      standard: "The HAT's own draw (regulators, codec, transceiver) is
                      unpublished — CANNOT DETERMINE. Not zero."
                      (research/raw/deploy_audio_i2c3-pihat.dts:22 (via docs/ELECTRONICS-AND-SOFTWARE.md §9); the 6.6–8.2 V window is model.rs:99-128, the runtime's own, read through the servos)
  [CANNOT DETERMINE]  current/VCC_3V3_CSItypical draw
                      1 of 1 part(s) drawing VCC_3V3_CSI have no sourced typical current:
                        camera@direct          imx219         NOT SOURCED
                            PER-RAIL ONLY. Table 45 Electrical Characteristics, p.86 (VANA = 3.0
                            V, VDDL = 1.3 V, VDIG = 1.98 V, Tj = 60 ˚C), verbatim: 'IVAVA_strm |
                            33 | 38 | mA | … CSI2 4 lanes, VANA current' and 'IVDDL_strm | 100 |
                            160 | mA | CSI2 4 lanes, VDDL current' for 'Current consumption
                            (Full,30 frame/s)'; standby 'ISTB_ana | 50 | µA', 'ISTB_dig | 10 |
                            µA', 'ISTB_Iddl | 50 | µA'. No VDIG streaming current is printed.
                      NOTHING drawing VCC_3V3_CSI here has a sourced typical figure, so there is no floor either —
                      not 0 mA, not any number. This net's demand is simply unknown.
                      To close it: fetch the datasheet and add the part to cecad/data/chips.json, or
                      measure it and record what you found.
                      datasheet: "PER-RAIL ONLY. Table 45 Electrical Characteristics, p.86 (VANA =
                      3.0 V, VDDL = 1.3 V, VDIG = 1.98 V, Tj = 60 ˚C), verbatim: 'IVAVA_strm | 33
                      | 38 | mA | … CSI2 4 lanes, VANA current' and 'IVDDL_strm | 100 | 160 | mA |
                      CSI2 4 lanes, VDDL current' for 'Current consumption (Full,30 frame/s)';
                      standby 'ISTB_ana | 50 | µA', 'ISTB_dig | 10 | µA', 'ISTB_Iddl | 50 | µA'.
                      No VDIG streaming current is printed."
                      (chips[imx219].current_mA.typical_basis)
  [CANNOT DETERMINE]  current/VCC_3V3_CSIpeak draw
                      1 of 1 part(s) drawing VCC_3V3_CSI have no sourced peak current:
                        camera@direct          imx219         NOT SOURCED
                            NOT TRANSCRIBED HERE. No peak figure was read out of the document this
                            block cites (see `cite`) when this record was written, and none is
                            asserted now (basis added 2026-09-02, wiring lane, so
                            cecad.electrical's loader can read the shelf: a null with no reason is
                            refused). Null means not looked up in this record — NOT zero. Re-read
                            the sheet's current-consumption table to fill it.
                      NOTHING drawing VCC_3V3_CSI here has a sourced peak figure, so there is no floor either —
                      not 0 mA, not any number. This net's demand is simply unknown.
                      To close it: fetch the datasheet and add the part to cecad/data/chips.json, or
                      measure it and record what you found.
                      datasheet: "NOT TRANSCRIBED HERE. No peak figure was read out of the
                      document this block cites (see `cite`) when this record was written, and
                      none is asserted now (basis added 2026-09-02, wiring lane, so
                      cecad.electrical's loader can read the shelf: a null with no reason is
                      refused). Null means not looked up in this record — NOT zero. Re-read the
                      sheet's current-consumption table to fill it."
                      (chips[imx219].current_mA.peak_basis)
  [PASS]              csi            csi
                      exactly one CSI controller on csi: host.
  [PASS]              i2c            i2c2
                      exactly one I2C controller on i2c2: host.
  [PASS]              i2c            i2c3
                      exactly one I2C controller on i2c3: host.
  [PASS]              i2c            system
                      5 device(s) declare a I2C address: camera (0x10), bmi088 (0x19), bmi088.gyro (0x68), codec (0x18), tof (0x29).
                      They sit in 2 net group(s) that cannot see each other: i2c2 (1 device(s)); i2c3 (4 device(s)).
                      A duplicate address is a conflict only between devices on ONE net group, and no two
                      of these share one.
  [PASS]              i2s            i2s3
                      exactly one I2S controller on i2s3: host.
  [PASS]              uart           dxl
                      exactly one UART controller on dxl: host.
  [PASS]              uart           uart2
                      exactly one UART controller on uart2: host.
  [PASS]              uart           system
                      16 device(s) declare a UART address: id10 (10), id11 (11), id12 (12), id13 (13), id14 (14), id20 (20), id21 (21), id22 (22), id23 (23), id24 (24), id30 (30), id31 (31), id32 (32), id33 (33), id34 (34), imu200 (200).
                      They sit in 1 net group(s) that cannot see each other: dxl (16 device(s)).
                      A duplicate address is a conflict only between devices on ONE net group, and no two
                      of these share one.
  [PASS]              pin_directions battery@direct
                      the documents record a direction and a bus for every signal terminal of np-f550.
                      Whether each was written down or inferred by the extraction is in that part's own
                      uncertainties — see the note above.
  [PASS]              pin_directions hat@direct
                      the documents record a direction and a bus for every signal terminal of microduck-robot-hat-pcb.
                      Whether each was written down or inferred by the extraction is in that part's own
                      uncertainties — see the note above.
  [PASS]              pin_directions codec@direct
                      the documents record a direction and a bus for every signal terminal of tlv320aic3104.
                      Whether each was written down or inferred by the extraction is in that part's own
                      uncertainties — see the note above.
  [PASS]              pin_directions bmi088@direct
                      the documents record a direction and a bus for every signal terminal of bmi088.
                      Whether each was written down or inferred by the extraction is in that part's own
                      uncertainties — see the note above.
  [PASS]              pin_directions bmi088.gyro@direct
                      the documents record a direction and a bus for every signal terminal of bmi088.
                      Whether each was written down or inferred by the extraction is in that part's own
                      uncertainties — see the note above.
  [PASS]              pin_directions tof@direct
                      the documents record a direction and a bus for every signal terminal of microduck-tof-module.
                      Whether each was written down or inferred by the extraction is in that part's own
                      uncertainties — see the note above.
  [PASS]              pin_directions imu200@direct
                      the documents record a direction and a bus for every signal terminal of microduck-imu-to-dxl.
                      Whether each was written down or inferred by the extraction is in that part's own
                      uncertainties — see the note above.
  [PASS]              pin_directions id20@direct
                      the documents record a direction and a bus for every signal terminal of xl330-m288-t.
                      Whether each was written down or inferred by the extraction is in that part's own
                      uncertainties — see the note above.
  [PASS]              pin_directions id21@direct
                      the documents record a direction and a bus for every signal terminal of xl330-m288-t.
                      Whether each was written down or inferred by the extraction is in that part's own
                      uncertainties — see the note above.
  [PASS]              pin_directions id22@direct
                      the documents record a direction and a bus for every signal terminal of xl330-m288-t.
                      Whether each was written down or inferred by the extraction is in that part's own
                      uncertainties — see the note above.
  [PASS]              pin_directions id23@direct
                      the documents record a direction and a bus for every signal terminal of xl330-m288-t.
                      Whether each was written down or inferred by the extraction is in that part's own
                      uncertainties — see the note above.
  [PASS]              pin_directions id24@direct
                      the documents record a direction and a bus for every signal terminal of xl330-m288-t.
                      Whether each was written down or inferred by the extraction is in that part's own
                      uncertainties — see the note above.
  [PASS]              pin_directions id30@direct
                      the documents record a direction and a bus for every signal terminal of xl330-m288-t.
                      Whether each was written down or inferred by the extraction is in that part's own
                      uncertainties — see the note above.
  [PASS]              pin_directions id31@direct
                      the documents record a direction and a bus for every signal terminal of xl330-m288-t.
                      Whether each was written down or inferred by the extraction is in that part's own
                      uncertainties — see the note above.
  [PASS]              pin_directions id32@direct
                      the documents record a direction and a bus for every signal terminal of xl330-m288-t.
                      Whether each was written down or inferred by the extraction is in that part's own
                      uncertainties — see the note above.
  [PASS]              pin_directions id33@direct
                      the documents record a direction and a bus for every signal terminal of xl330-m288-t.
                      Whether each was written down or inferred by the extraction is in that part's own
                      uncertainties — see the note above.
  [PASS]              pin_directions id34@direct
                      the documents record a direction and a bus for every signal terminal of xl330-m288-t.
                      Whether each was written down or inferred by the extraction is in that part's own
                      uncertainties — see the note above.
  [PASS]              pin_directions id10@direct
                      the documents record a direction and a bus for every signal terminal of xl330-m288-t.
                      Whether each was written down or inferred by the extraction is in that part's own
                      uncertainties — see the note above.
  [PASS]              pin_directions id11@direct
                      the documents record a direction and a bus for every signal terminal of xl330-m288-t.
                      Whether each was written down or inferred by the extraction is in that part's own
                      uncertainties — see the note above.
  [PASS]              pin_directions id12@direct
                      the documents record a direction and a bus for every signal terminal of xl330-m288-t.
                      Whether each was written down or inferred by the extraction is in that part's own
                      uncertainties — see the note above.
  [PASS]              pin_directions id13@direct
                      the documents record a direction and a bus for every signal terminal of xl330-m288-t.
                      Whether each was written down or inferred by the extraction is in that part's own
                      uncertainties — see the note above.
  [PASS]              pin_directions id14@direct
                      the documents record a direction and a bus for every signal terminal of xl330-m288-t.
                      Whether each was written down or inferred by the extraction is in that part's own
                      uncertainties — see the note above.
  [PASS]              pin_directions camera@direct
                      the documents record a direction and a bus for every signal terminal of microduck-camera-module.
                      Whether each was written down or inferred by the extraction is in that part's own
                      uncertainties — see the note above.
  [PASS]              pin_directions speaker@direct
                      the documents record a direction and a bus for every signal terminal of microduck-speaker.
                      Whether each was written down or inferred by the extraction is in that part's own
                      uncertainties — see the note above.
  [PASS]              pin_directions mic@direct
                      the documents record a direction and a bus for every signal terminal of microduck-mic.
                      Whether each was written down or inferred by the extraction is in that part's own
                      uncertainties — see the note above.
  [CANNOT DETERMINE]  vocabulary/provisionhat.SPK+
                      microduck-robot-hat-pcb terminal 'SPK+' states provision 'audio_output', which is not one of the three
                      kinds this layer can act on: supply, ground, signal.
                      This is not a claim the record is wrong — a reversing ESC's motor leads really are an
                      H-bridge output, and calling them a supply would be the false statement.
                      What was done with it: the net builder placed it on the graph as a SIGNAL terminal, which
                      is this loader's fallback and not the record's claim. So it is visible to check_gpio and
                      check_buses, and it is in NO per-rail total. If this terminal sources current, check_power's
                      and check_current's totals are short by an amount nobody here can name.
                      To close it: state the terminal as one of the three kinds, or add the kind to
                      PROVISION_KINDS together with what each check should do with it.
                      standard: "line out [C-elec]"
                      (docs/ELECTRONICS-AND-SOFTWARE.md §7 — community; whether an amplifier sits between the codec (HPLOUT/LEFT_LOP, part:tlv320aic3104 pinout) and the speaker is CANNOT DETERMINE)
  [CANNOT DETERMINE]  vocabulary/provisionhat.SPK-
                      microduck-robot-hat-pcb terminal 'SPK-' states provision 'audio_output', which is not one of the three
                      kinds this layer can act on: supply, ground, signal.
                      This is not a claim the record is wrong — a reversing ESC's motor leads really are an
                      H-bridge output, and calling them a supply would be the false statement.
                      What was done with it: the net builder placed it on the graph as a SIGNAL terminal, which
                      is this loader's fallback and not the record's claim. So it is visible to check_gpio and
                      check_buses, and it is in NO per-rail total. If this terminal sources current, check_power's
                      and check_current's totals are short by an amount nobody here can name.
                      To close it: state the terminal as one of the three kinds, or add the kind to
                      PROVISION_KINDS together with what each check should do with it.
                      standard: "line out [C-elec]"
                      (docs/ELECTRONICS-AND-SOFTWARE.md §7)
  [CANNOT DETERMINE]  vocabulary/provisionhat.MIC_IN
                      microduck-robot-hat-pcb terminal 'MIC_IN' states provision 'audio_input', which is not one of the three
                      kinds this layer can act on: supply, ground, signal.
                      This is not a claim the record is wrong — a reversing ESC's motor leads really are an
                      H-bridge output, and calling them a supply would be the false statement.
                      What was done with it: the net builder placed it on the graph as a SIGNAL terminal, which
                      is this loader's fallback and not the record's claim. So it is visible to check_gpio and
                      check_buses, and it is in NO per-rail total. If this terminal sources current, check_power's
                      and check_current's totals are short by an amount nobody here can name.
                      To close it: state the terminal as one of the three kinds, or add the kind to
                      PROVISION_KINDS together with what each check should do with it.
                      standard: "codec input Mic3R (mono, [C-elec])"
                      (docs/ELECTRONICS-AND-SOFTWARE.md §7 — community; the codec's MIC2R/LINE2R is pin 16 (part:tlv320aic3104 pinout))
  [CANNOT DETERMINE]  vocabulary/needspeaker.SPK+
                      microduck-speaker terminal 'SPK+' states need 'audio_output', which is not one of the four kinds
                      this layer can act on: supply, ground, signal, endpoint.
                      This is not a claim the record is wrong — a part really can have a terminal that is none
                      of the four. It is a claim that NOTHING HERE KNOWS WHICH ONE IT IS.
                      What was done with it: the net builder placed it on the graph as a SIGNAL terminal,
                      which is this loader's fallback and not the record's claim. So it is visible to
                      check_gpio and check_buses, and it is in NO per-rail total — if this terminal draws or
                      sources current, check_power's and check_current's totals are short by an amount nobody
                      here can name.
                      To close it: state the terminal as one of the four kinds, or add the kind to
                      NEED_KINDS together with what each check should do with it.
                      standard: "Impedance: 8 Ohm ± 15% at 1 kHz and 3.46V."
                      (docs/abra-spk-3525-2w-gh.html description, verbatim.)
  [CANNOT DETERMINE]  vocabulary/needspeaker.SPK-
                      microduck-speaker terminal 'SPK-' states need 'audio_output', which is not one of the four kinds
                      this layer can act on: supply, ground, signal, endpoint.
                      This is not a claim the record is wrong — a part really can have a terminal that is none
                      of the four. It is a claim that NOTHING HERE KNOWS WHICH ONE IT IS.
                      What was done with it: the net builder placed it on the graph as a SIGNAL terminal,
                      which is this loader's fallback and not the record's claim. So it is visible to
                      check_gpio and check_buses, and it is in NO per-rail total — if this terminal draws or
                      sources current, check_power's and check_current's totals are short by an amount nobody
                      here can name.
                      To close it: state the terminal as one of the four kinds, or add the kind to
                      NEED_KINDS together with what each check should do with it.
                      standard: "Impedance: 8 Ohm ± 15% at 1 kHz and 3.46V."
                      (docs/abra-spk-3525-2w-gh.html description, verbatim.)
  [CANNOT DETERMINE]  vocabulary/needmic.MIC
                      microduck-mic terminal 'MIC' states need 'audio_input', which is not one of the four kinds
                      this layer can act on: supply, ground, signal, endpoint.
                      This is not a claim the record is wrong — a part really can have a terminal that is none
                      of the four. It is a claim that NOTHING HERE KNOWS WHICH ONE IT IS.
                      What was done with it: the net builder placed it on the graph as a SIGNAL terminal,
                      which is this loader's fallback and not the record's claim. So it is visible to
                      check_gpio and check_buses, and it is in NO per-rail total — if this terminal draws or
                      sources current, check_power's and check_current's totals are short by an amount nobody
                      here can name.
                      To close it: state the terminal as one of the four kinds, or add the kind to
                      NEED_KINDS together with what each check should do with it.
                      standard: "mic on the head (pet_detect README); codec input Mic3R mono
                      [C-elec]"
                      (docs/ELECTRONICS-AND-SOFTWARE.md §7)
  [CANNOT DETERMINE]  volts/HAT_1V8  source
                      1 sink(s) on HAT_1V8 and no stated voltage: no provision on this net states a nominal_v and the design declares no band.
                      standard: "nominal_v: null"
                      (electronics/netlist.py declared / parts[].provides[].nominal_v_basis)
  [CANNOT DETERMINE]  volts/HAT_3V3  source
                      4 sink(s) on HAT_3V3 and no stated voltage: no provision on this net states a nominal_v and the design declares no band.
                      standard: "nominal_v: null"
                      (electronics/netlist.py declared / parts[].provides[].nominal_v_basis)
  [PASS]              volts/J5_3V3   tof.3V3
                      J5_3V3 is 3.3..3.3 V (hat (microduck-robot-hat-pcb) provision nominal_v); tof's 3V3 band is 3.0..3.6 V.
  [CANNOT DETERMINE]  volts/MICBIAS  source
                      1 sink(s) on MICBIAS and no stated voltage: no provision on this net states a nominal_v and the design declares no band.
                      standard: "the TLV320AIC3104 MICBIAS pin 15 (part:tlv320aic3104 pinout) —
                      programmable 2.0 / 2.5 V / AVDD per TI; which is set, and whether the fitted
                      mic uses it at all, is CANNOT DETERMINE."
                      (electronics/netlist.py declared / parts[].provides[].nominal_v_basis)
  [CANNOT DETERMINE]  volts/SERVO_V  imu200.VDD
                      SERVO_V is 6.6..8.2 V (declared by the design); imu200 (microduck-imu-to-dxl) states no v_min/v_max for VDD.
                      standard: "rides the Dynamixel bus; fetched in the same sync_read as the
                      servos, listed first"
                      (docs/ELECTRONICS-AND-SOFTWARE.md §4.1 (imu.rs:3-4; bus.rs:92). The board's input band and its regulator are CANNOT DETERMINE — MCU, transceiver, schematic, firmware are not in the repository (docs §4.1 last row).)
  [FAIL]              volts/SERVO_V  id20.VDD
                      SERVO_V is 6.6..8.2 V (declared by the design); id20 (xl330-m288-t) states 3.7..6.0 V for VDD.
                      Source: "pub const BATTERY_FULL_V: f64 = 8.2; ... pub const BATTERY_EMPTY_V: f64 = 6.6;" (research/raw/duck-control_src_model.rs:109,113 — model.rs:103-105: 'There is no fuel gauge and no ADC. The only measurement available is what the servos report as their own supply')
                      standard: "Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])"
                      (E1 §Specifications, row verbatim: 'Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])'. v_typ = 5.0 is the vendor's stated 'Recommended', not a characterisation point. NAMED CONFLICT WITH THE DESIGN, not with another source: Pollen's runtime maps the pack 6.6-8.2 V through this servo's own Present Input Voltage(144) (docs/ELECTRONICS-AND-SOFTWARE.md §3.4), 0.6-2.2 V above this v_max; and robotd writes Shutdown(63) = 52 = 0b00110100 where the vendor default is 53 = 0b00110101 - the one bit cleared is Bit 0 'Input Voltage Error', the fault that E1 says fires when Present Input Voltage(144) leaves the Min/Max Voltage Limit window (max 7.0 V). That is consistent with the servos seeing the raw pack and is recorded as an OBSERVATION on Pollen's code, not as a vendor figure. Whether a production Microduck runs stock XL330s over their rating stays CANNOT DETERMINE (a meter on servo VDD settles it).)
  [FAIL]              volts/SERVO_V  id21.VDD
                      SERVO_V is 6.6..8.2 V (declared by the design); id21 (xl330-m288-t) states 3.7..6.0 V for VDD.
                      Source: "pub const BATTERY_FULL_V: f64 = 8.2; ... pub const BATTERY_EMPTY_V: f64 = 6.6;" (research/raw/duck-control_src_model.rs:109,113 — model.rs:103-105: 'There is no fuel gauge and no ADC. The only measurement available is what the servos report as their own supply')
                      standard: "Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])"
                      (E1 §Specifications, row verbatim: 'Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])'. v_typ = 5.0 is the vendor's stated 'Recommended', not a characterisation point. NAMED CONFLICT WITH THE DESIGN, not with another source: Pollen's runtime maps the pack 6.6-8.2 V through this servo's own Present Input Voltage(144) (docs/ELECTRONICS-AND-SOFTWARE.md §3.4), 0.6-2.2 V above this v_max; and robotd writes Shutdown(63) = 52 = 0b00110100 where the vendor default is 53 = 0b00110101 - the one bit cleared is Bit 0 'Input Voltage Error', the fault that E1 says fires when Present Input Voltage(144) leaves the Min/Max Voltage Limit window (max 7.0 V). That is consistent with the servos seeing the raw pack and is recorded as an OBSERVATION on Pollen's code, not as a vendor figure. Whether a production Microduck runs stock XL330s over their rating stays CANNOT DETERMINE (a meter on servo VDD settles it).)
  [FAIL]              volts/SERVO_V  id22.VDD
                      SERVO_V is 6.6..8.2 V (declared by the design); id22 (xl330-m288-t) states 3.7..6.0 V for VDD.
                      Source: "pub const BATTERY_FULL_V: f64 = 8.2; ... pub const BATTERY_EMPTY_V: f64 = 6.6;" (research/raw/duck-control_src_model.rs:109,113 — model.rs:103-105: 'There is no fuel gauge and no ADC. The only measurement available is what the servos report as their own supply')
                      standard: "Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])"
                      (E1 §Specifications, row verbatim: 'Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])'. v_typ = 5.0 is the vendor's stated 'Recommended', not a characterisation point. NAMED CONFLICT WITH THE DESIGN, not with another source: Pollen's runtime maps the pack 6.6-8.2 V through this servo's own Present Input Voltage(144) (docs/ELECTRONICS-AND-SOFTWARE.md §3.4), 0.6-2.2 V above this v_max; and robotd writes Shutdown(63) = 52 = 0b00110100 where the vendor default is 53 = 0b00110101 - the one bit cleared is Bit 0 'Input Voltage Error', the fault that E1 says fires when Present Input Voltage(144) leaves the Min/Max Voltage Limit window (max 7.0 V). That is consistent with the servos seeing the raw pack and is recorded as an OBSERVATION on Pollen's code, not as a vendor figure. Whether a production Microduck runs stock XL330s over their rating stays CANNOT DETERMINE (a meter on servo VDD settles it).)
  [FAIL]              volts/SERVO_V  id23.VDD
                      SERVO_V is 6.6..8.2 V (declared by the design); id23 (xl330-m288-t) states 3.7..6.0 V for VDD.
                      Source: "pub const BATTERY_FULL_V: f64 = 8.2; ... pub const BATTERY_EMPTY_V: f64 = 6.6;" (research/raw/duck-control_src_model.rs:109,113 — model.rs:103-105: 'There is no fuel gauge and no ADC. The only measurement available is what the servos report as their own supply')
                      standard: "Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])"
                      (E1 §Specifications, row verbatim: 'Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])'. v_typ = 5.0 is the vendor's stated 'Recommended', not a characterisation point. NAMED CONFLICT WITH THE DESIGN, not with another source: Pollen's runtime maps the pack 6.6-8.2 V through this servo's own Present Input Voltage(144) (docs/ELECTRONICS-AND-SOFTWARE.md §3.4), 0.6-2.2 V above this v_max; and robotd writes Shutdown(63) = 52 = 0b00110100 where the vendor default is 53 = 0b00110101 - the one bit cleared is Bit 0 'Input Voltage Error', the fault that E1 says fires when Present Input Voltage(144) leaves the Min/Max Voltage Limit window (max 7.0 V). That is consistent with the servos seeing the raw pack and is recorded as an OBSERVATION on Pollen's code, not as a vendor figure. Whether a production Microduck runs stock XL330s over their rating stays CANNOT DETERMINE (a meter on servo VDD settles it).)
  [FAIL]              volts/SERVO_V  id24.VDD
                      SERVO_V is 6.6..8.2 V (declared by the design); id24 (xl330-m288-t) states 3.7..6.0 V for VDD.
                      Source: "pub const BATTERY_FULL_V: f64 = 8.2; ... pub const BATTERY_EMPTY_V: f64 = 6.6;" (research/raw/duck-control_src_model.rs:109,113 — model.rs:103-105: 'There is no fuel gauge and no ADC. The only measurement available is what the servos report as their own supply')
                      standard: "Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])"
                      (E1 §Specifications, row verbatim: 'Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])'. v_typ = 5.0 is the vendor's stated 'Recommended', not a characterisation point. NAMED CONFLICT WITH THE DESIGN, not with another source: Pollen's runtime maps the pack 6.6-8.2 V through this servo's own Present Input Voltage(144) (docs/ELECTRONICS-AND-SOFTWARE.md §3.4), 0.6-2.2 V above this v_max; and robotd writes Shutdown(63) = 52 = 0b00110100 where the vendor default is 53 = 0b00110101 - the one bit cleared is Bit 0 'Input Voltage Error', the fault that E1 says fires when Present Input Voltage(144) leaves the Min/Max Voltage Limit window (max 7.0 V). That is consistent with the servos seeing the raw pack and is recorded as an OBSERVATION on Pollen's code, not as a vendor figure. Whether a production Microduck runs stock XL330s over their rating stays CANNOT DETERMINE (a meter on servo VDD settles it).)
  [FAIL]              volts/SERVO_V  id30.VDD
                      SERVO_V is 6.6..8.2 V (declared by the design); id30 (xl330-m288-t) states 3.7..6.0 V for VDD.
                      Source: "pub const BATTERY_FULL_V: f64 = 8.2; ... pub const BATTERY_EMPTY_V: f64 = 6.6;" (research/raw/duck-control_src_model.rs:109,113 — model.rs:103-105: 'There is no fuel gauge and no ADC. The only measurement available is what the servos report as their own supply')
                      standard: "Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])"
                      (E1 §Specifications, row verbatim: 'Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])'. v_typ = 5.0 is the vendor's stated 'Recommended', not a characterisation point. NAMED CONFLICT WITH THE DESIGN, not with another source: Pollen's runtime maps the pack 6.6-8.2 V through this servo's own Present Input Voltage(144) (docs/ELECTRONICS-AND-SOFTWARE.md §3.4), 0.6-2.2 V above this v_max; and robotd writes Shutdown(63) = 52 = 0b00110100 where the vendor default is 53 = 0b00110101 - the one bit cleared is Bit 0 'Input Voltage Error', the fault that E1 says fires when Present Input Voltage(144) leaves the Min/Max Voltage Limit window (max 7.0 V). That is consistent with the servos seeing the raw pack and is recorded as an OBSERVATION on Pollen's code, not as a vendor figure. Whether a production Microduck runs stock XL330s over their rating stays CANNOT DETERMINE (a meter on servo VDD settles it).)
  [FAIL]              volts/SERVO_V  id31.VDD
                      SERVO_V is 6.6..8.2 V (declared by the design); id31 (xl330-m288-t) states 3.7..6.0 V for VDD.
                      Source: "pub const BATTERY_FULL_V: f64 = 8.2; ... pub const BATTERY_EMPTY_V: f64 = 6.6;" (research/raw/duck-control_src_model.rs:109,113 — model.rs:103-105: 'There is no fuel gauge and no ADC. The only measurement available is what the servos report as their own supply')
                      standard: "Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])"
                      (E1 §Specifications, row verbatim: 'Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])'. v_typ = 5.0 is the vendor's stated 'Recommended', not a characterisation point. NAMED CONFLICT WITH THE DESIGN, not with another source: Pollen's runtime maps the pack 6.6-8.2 V through this servo's own Present Input Voltage(144) (docs/ELECTRONICS-AND-SOFTWARE.md §3.4), 0.6-2.2 V above this v_max; and robotd writes Shutdown(63) = 52 = 0b00110100 where the vendor default is 53 = 0b00110101 - the one bit cleared is Bit 0 'Input Voltage Error', the fault that E1 says fires when Present Input Voltage(144) leaves the Min/Max Voltage Limit window (max 7.0 V). That is consistent with the servos seeing the raw pack and is recorded as an OBSERVATION on Pollen's code, not as a vendor figure. Whether a production Microduck runs stock XL330s over their rating stays CANNOT DETERMINE (a meter on servo VDD settles it).)
  [FAIL]              volts/SERVO_V  id32.VDD
                      SERVO_V is 6.6..8.2 V (declared by the design); id32 (xl330-m288-t) states 3.7..6.0 V for VDD.
                      Source: "pub const BATTERY_FULL_V: f64 = 8.2; ... pub const BATTERY_EMPTY_V: f64 = 6.6;" (research/raw/duck-control_src_model.rs:109,113 — model.rs:103-105: 'There is no fuel gauge and no ADC. The only measurement available is what the servos report as their own supply')
                      standard: "Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])"
                      (E1 §Specifications, row verbatim: 'Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])'. v_typ = 5.0 is the vendor's stated 'Recommended', not a characterisation point. NAMED CONFLICT WITH THE DESIGN, not with another source: Pollen's runtime maps the pack 6.6-8.2 V through this servo's own Present Input Voltage(144) (docs/ELECTRONICS-AND-SOFTWARE.md §3.4), 0.6-2.2 V above this v_max; and robotd writes Shutdown(63) = 52 = 0b00110100 where the vendor default is 53 = 0b00110101 - the one bit cleared is Bit 0 'Input Voltage Error', the fault that E1 says fires when Present Input Voltage(144) leaves the Min/Max Voltage Limit window (max 7.0 V). That is consistent with the servos seeing the raw pack and is recorded as an OBSERVATION on Pollen's code, not as a vendor figure. Whether a production Microduck runs stock XL330s over their rating stays CANNOT DETERMINE (a meter on servo VDD settles it).)
  [FAIL]              volts/SERVO_V  id33.VDD
                      SERVO_V is 6.6..8.2 V (declared by the design); id33 (xl330-m288-t) states 3.7..6.0 V for VDD.
                      Source: "pub const BATTERY_FULL_V: f64 = 8.2; ... pub const BATTERY_EMPTY_V: f64 = 6.6;" (research/raw/duck-control_src_model.rs:109,113 — model.rs:103-105: 'There is no fuel gauge and no ADC. The only measurement available is what the servos report as their own supply')
                      standard: "Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])"
                      (E1 §Specifications, row verbatim: 'Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])'. v_typ = 5.0 is the vendor's stated 'Recommended', not a characterisation point. NAMED CONFLICT WITH THE DESIGN, not with another source: Pollen's runtime maps the pack 6.6-8.2 V through this servo's own Present Input Voltage(144) (docs/ELECTRONICS-AND-SOFTWARE.md §3.4), 0.6-2.2 V above this v_max; and robotd writes Shutdown(63) = 52 = 0b00110100 where the vendor default is 53 = 0b00110101 - the one bit cleared is Bit 0 'Input Voltage Error', the fault that E1 says fires when Present Input Voltage(144) leaves the Min/Max Voltage Limit window (max 7.0 V). That is consistent with the servos seeing the raw pack and is recorded as an OBSERVATION on Pollen's code, not as a vendor figure. Whether a production Microduck runs stock XL330s over their rating stays CANNOT DETERMINE (a meter on servo VDD settles it).)
  [FAIL]              volts/SERVO_V  id34.VDD
                      SERVO_V is 6.6..8.2 V (declared by the design); id34 (xl330-m288-t) states 3.7..6.0 V for VDD.
                      Source: "pub const BATTERY_FULL_V: f64 = 8.2; ... pub const BATTERY_EMPTY_V: f64 = 6.6;" (research/raw/duck-control_src_model.rs:109,113 — model.rs:103-105: 'There is no fuel gauge and no ADC. The only measurement available is what the servos report as their own supply')
                      standard: "Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])"
                      (E1 §Specifications, row verbatim: 'Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])'. v_typ = 5.0 is the vendor's stated 'Recommended', not a characterisation point. NAMED CONFLICT WITH THE DESIGN, not with another source: Pollen's runtime maps the pack 6.6-8.2 V through this servo's own Present Input Voltage(144) (docs/ELECTRONICS-AND-SOFTWARE.md §3.4), 0.6-2.2 V above this v_max; and robotd writes Shutdown(63) = 52 = 0b00110100 where the vendor default is 53 = 0b00110101 - the one bit cleared is Bit 0 'Input Voltage Error', the fault that E1 says fires when Present Input Voltage(144) leaves the Min/Max Voltage Limit window (max 7.0 V). That is consistent with the servos seeing the raw pack and is recorded as an OBSERVATION on Pollen's code, not as a vendor figure. Whether a production Microduck runs stock XL330s over their rating stays CANNOT DETERMINE (a meter on servo VDD settles it).)
  [FAIL]              volts/SERVO_V  id10.VDD
                      SERVO_V is 6.6..8.2 V (declared by the design); id10 (xl330-m288-t) states 3.7..6.0 V for VDD.
                      Source: "pub const BATTERY_FULL_V: f64 = 8.2; ... pub const BATTERY_EMPTY_V: f64 = 6.6;" (research/raw/duck-control_src_model.rs:109,113 — model.rs:103-105: 'There is no fuel gauge and no ADC. The only measurement available is what the servos report as their own supply')
                      standard: "Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])"
                      (E1 §Specifications, row verbatim: 'Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])'. v_typ = 5.0 is the vendor's stated 'Recommended', not a characterisation point. NAMED CONFLICT WITH THE DESIGN, not with another source: Pollen's runtime maps the pack 6.6-8.2 V through this servo's own Present Input Voltage(144) (docs/ELECTRONICS-AND-SOFTWARE.md §3.4), 0.6-2.2 V above this v_max; and robotd writes Shutdown(63) = 52 = 0b00110100 where the vendor default is 53 = 0b00110101 - the one bit cleared is Bit 0 'Input Voltage Error', the fault that E1 says fires when Present Input Voltage(144) leaves the Min/Max Voltage Limit window (max 7.0 V). That is consistent with the servos seeing the raw pack and is recorded as an OBSERVATION on Pollen's code, not as a vendor figure. Whether a production Microduck runs stock XL330s over their rating stays CANNOT DETERMINE (a meter on servo VDD settles it).)
  [FAIL]              volts/SERVO_V  id11.VDD
                      SERVO_V is 6.6..8.2 V (declared by the design); id11 (xl330-m288-t) states 3.7..6.0 V for VDD.
                      Source: "pub const BATTERY_FULL_V: f64 = 8.2; ... pub const BATTERY_EMPTY_V: f64 = 6.6;" (research/raw/duck-control_src_model.rs:109,113 — model.rs:103-105: 'There is no fuel gauge and no ADC. The only measurement available is what the servos report as their own supply')
                      standard: "Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])"
                      (E1 §Specifications, row verbatim: 'Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])'. v_typ = 5.0 is the vendor's stated 'Recommended', not a characterisation point. NAMED CONFLICT WITH THE DESIGN, not with another source: Pollen's runtime maps the pack 6.6-8.2 V through this servo's own Present Input Voltage(144) (docs/ELECTRONICS-AND-SOFTWARE.md §3.4), 0.6-2.2 V above this v_max; and robotd writes Shutdown(63) = 52 = 0b00110100 where the vendor default is 53 = 0b00110101 - the one bit cleared is Bit 0 'Input Voltage Error', the fault that E1 says fires when Present Input Voltage(144) leaves the Min/Max Voltage Limit window (max 7.0 V). That is consistent with the servos seeing the raw pack and is recorded as an OBSERVATION on Pollen's code, not as a vendor figure. Whether a production Microduck runs stock XL330s over their rating stays CANNOT DETERMINE (a meter on servo VDD settles it).)
  [FAIL]              volts/SERVO_V  id12.VDD
                      SERVO_V is 6.6..8.2 V (declared by the design); id12 (xl330-m288-t) states 3.7..6.0 V for VDD.
                      Source: "pub const BATTERY_FULL_V: f64 = 8.2; ... pub const BATTERY_EMPTY_V: f64 = 6.6;" (research/raw/duck-control_src_model.rs:109,113 — model.rs:103-105: 'There is no fuel gauge and no ADC. The only measurement available is what the servos report as their own supply')
                      standard: "Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])"
                      (E1 §Specifications, row verbatim: 'Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])'. v_typ = 5.0 is the vendor's stated 'Recommended', not a characterisation point. NAMED CONFLICT WITH THE DESIGN, not with another source: Pollen's runtime maps the pack 6.6-8.2 V through this servo's own Present Input Voltage(144) (docs/ELECTRONICS-AND-SOFTWARE.md §3.4), 0.6-2.2 V above this v_max; and robotd writes Shutdown(63) = 52 = 0b00110100 where the vendor default is 53 = 0b00110101 - the one bit cleared is Bit 0 'Input Voltage Error', the fault that E1 says fires when Present Input Voltage(144) leaves the Min/Max Voltage Limit window (max 7.0 V). That is consistent with the servos seeing the raw pack and is recorded as an OBSERVATION on Pollen's code, not as a vendor figure. Whether a production Microduck runs stock XL330s over their rating stays CANNOT DETERMINE (a meter on servo VDD settles it).)
  [FAIL]              volts/SERVO_V  id13.VDD
                      SERVO_V is 6.6..8.2 V (declared by the design); id13 (xl330-m288-t) states 3.7..6.0 V for VDD.
                      Source: "pub const BATTERY_FULL_V: f64 = 8.2; ... pub const BATTERY_EMPTY_V: f64 = 6.6;" (research/raw/duck-control_src_model.rs:109,113 — model.rs:103-105: 'There is no fuel gauge and no ADC. The only measurement available is what the servos report as their own supply')
                      standard: "Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])"
                      (E1 §Specifications, row verbatim: 'Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])'. v_typ = 5.0 is the vendor's stated 'Recommended', not a characterisation point. NAMED CONFLICT WITH THE DESIGN, not with another source: Pollen's runtime maps the pack 6.6-8.2 V through this servo's own Present Input Voltage(144) (docs/ELECTRONICS-AND-SOFTWARE.md §3.4), 0.6-2.2 V above this v_max; and robotd writes Shutdown(63) = 52 = 0b00110100 where the vendor default is 53 = 0b00110101 - the one bit cleared is Bit 0 'Input Voltage Error', the fault that E1 says fires when Present Input Voltage(144) leaves the Min/Max Voltage Limit window (max 7.0 V). That is consistent with the servos seeing the raw pack and is recorded as an OBSERVATION on Pollen's code, not as a vendor figure. Whether a production Microduck runs stock XL330s over their rating stays CANNOT DETERMINE (a meter on servo VDD settles it).)
  [FAIL]              volts/SERVO_V  id14.VDD
                      SERVO_V is 6.6..8.2 V (declared by the design); id14 (xl330-m288-t) states 3.7..6.0 V for VDD.
                      Source: "pub const BATTERY_FULL_V: f64 = 8.2; ... pub const BATTERY_EMPTY_V: f64 = 6.6;" (research/raw/duck-control_src_model.rs:109,113 — model.rs:103-105: 'There is no fuel gauge and no ADC. The only measurement available is what the servos report as their own supply')
                      standard: "Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])"
                      (E1 §Specifications, row verbatim: 'Input Voltage | 3.7 ~ 6.0 [V] (Recommended : 5.0 [V])'. v_typ = 5.0 is the vendor's stated 'Recommended', not a characterisation point. NAMED CONFLICT WITH THE DESIGN, not with another source: Pollen's runtime maps the pack 6.6-8.2 V through this servo's own Present Input Voltage(144) (docs/ELECTRONICS-AND-SOFTWARE.md §3.4), 0.6-2.2 V above this v_max; and robotd writes Shutdown(63) = 52 = 0b00110100 where the vendor default is 53 = 0b00110101 - the one bit cleared is Bit 0 'Input Voltage Error', the fault that E1 says fires when Present Input Voltage(144) leaves the Min/Max Voltage Limit window (max 7.0 V). That is consistent with the servos seeing the raw pack and is recorded as an OBSERVATION on Pollen's code, not as a vendor figure. Whether a production Microduck runs stock XL330s over their rating stays CANNOT DETERMINE (a meter on servo VDD settles it).)
  [PASS]              volts/V5_HAT   host.5V
                      V5_HAT is 5.0 V (hat (microduck-robot-hat-pcb) provision nominal_v); host's 5V states a typical of 5.0 V and no band — equal, so PASS on the one number both sides state.
  [PASS]              volts/VBAT     hat.VBAT
                      VBAT is 6.6..8.2 V (battery (np-f550) provision v_min..v_max); hat's VBAT band is 6.6..8.2 V.
  [PASS]              volts/VCC_3V3_CSIcamera.VCC_3V3
                      VCC_3V3_CSI is 3.3 V (declared by the design); camera's VCC_3V3 states a typical of 3.3 V and no band — equal, so PASS on the one number both sides state.
  [PASS]              dxl/ids        range
                      16 ID(s) on dxl/DATA, all within 0..252 and none the broadcast ID 254: [10, 11, 12, 13, 14, 20, 21, 22, 23, 24, 30, 31, 32, 33, 34, 200].
  [PASS]              dxl/ids        published
                      the 16 IDs on dxl/DATA are exactly JOINT_IDS + IMU_DXL_ID read from research/raw/duck-control_src_model.rs:15-19, 78: [10, 11, 12, 13, 14, 20, 21, 22, 23, 24, 30, 31, 32, 33, 34, 200].
  [PASS]              i2c3/overlay   addresses
                      i2c3 carries ['0x18', '0x19', '0x29', '0x68'] = the overlay's ['0x18', '0x19', '0x29', '0x68']: research/raw/deploy_audio_aic3104-i2c3.dts 'codec@18' / 'reg = <0x18>'; research/raw/deploy_audio_i2c3-pihat.dts:11 'dormant BMI088 0x19/0x68'; research/raw/tof_src_main.rs:87 'ADDRESS_CANDIDATES: [u8; 2] = [0x29, 0x52]'
  [PASS]              cross/wiring   connectivity
                      86 terminal(s) are in both designs (18 only here: bmi088.GND, bmi088.SCL, bmi088.SDA, bmi088.VDD, bmi088.VDDIO, bmi088.gyro.SCL, bmi088.gyro.SDA, codec.AVDD...); all 3655 pair(s) agree on same-net / different-net.
=== ELECTRICAL CHECKS FAILED — 15 failed, 28 undetermined, 75 pass ===

```

## ce-elec

`bin/elec gpio electronics/elec-spec.json` → exit 1: `REFUSED: host 'radxa-zero-3w' names no pin_roster in hosts.json, so no document says which pins exist. Add the roster before solving over it — assignment over undocumented silicon is invention.`

ce-elec's solvers assign pins over a roster in cecad/data/controllers.json; there is no RK3566 roster, so `gpio` and `levels` refuse — the honest answer for a host whose pins Pollen's overlays already fixed. `bin/elec doctor` reports the toolchain present. The netlist above is the design; the spec is kept as the probe that records this refusal.

## Sources

- `ce-parts/radxa-zero-3w/electrical.host.json` — Radxa ZERO 3W Product Brief RAD-DOC-0084 Rev 1.10, schematic V1.12, docs.radxa.com hardware-interface page (fetched 2026-09-02)
- `ce-parts/xl330-m288-t`, `lsm6dsv16x`, `tlv320aic3104`, `bmi088`, `vl53l5cx`, `vl53l8cx`, `imx219`, `np-f550` — vendor datasheets, quoted verbatim, sha256 in each PROVENANCE.json
- `research/raw/duck-control_src_model.rs` (JOINT_IDS, IMU_DXL_ID, BATTERY_FULL_V/EMPTY_V), `deploy_audio_i2c3-pihat.dts`, `deploy_audio_aic3104-i2c3.dts`, `tof_src_main.rs`, `deploy_robotd.toml` — Pollen's Apache-2.0 sources
- `docs/ELECTRONICS-AND-SOFTWARE.md` — the synthesis every note above cites
- `wiring/designs/microduck/nets.json` — the rung-5 lane's derived nets, cross-checked here

## How to re-run and how to break it

```
python3 electronics/netlist.py             # exit 0 PASS · 2 FAIL · 3 CANNOT DETERMINE
python3 electronics/netlist.py --self-test # two servos at ID 10 -> FAIL; gyro at 0x18 -> FAIL;
                                           # SERVO_V 4.8-5.5 V -> PASS, unstated -> CANNOT DETERMINE;
                                           # host unpowered -> FAIL; HAT pass-throughs left on the bus -> CANNOT DETERMINE
```
