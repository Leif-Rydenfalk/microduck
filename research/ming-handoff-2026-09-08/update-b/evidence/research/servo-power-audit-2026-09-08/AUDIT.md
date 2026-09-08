# Servo power audit — 2026-09-08

**The mismatch exists in the published source combination; it is not merely a local voltage typo.** It still does not prove what is fitted or measured on an original production Microduck. Keep the 15 modeled servo-voltage failures open.

## Evidence

1. Current official runtime commit **5984efb770855432b03dafd3d879e9929981e45b**, freshly fetched for this audit, defines battery empty/full as 6.6/8.2 V. Its description identifies servo supply telemetry as the battery observation. [model.rs lines 101–128](https://github.com/pollen-robotics/microduck/blob/5984efb770855432b03dafd3d879e9929981e45b/duck-control/src/model.rs#L101).
2. The implementation reads address 144, decodes a little-endian 16-bit value at 0.1 V/count, rejects zero readings and averages the remaining servo voltages. There is no pack-voltage conversion or voltage-doubling factor in this path. This is code behavior, not a logged measurement. [bus.rs](https://github.com/pollen-robotics/microduck/blob/5984efb770855432b03dafd3d879e9929981e45b/duck-control/src/bus.rs#L348).
3. The official public HAT PCB at **23eab11927f95ceca0dfa35bf182caeb7db39ea0** places all four motor connectors J3/J11/J13/J14 pad 2 directly on **+BATT**. U9's buck path produces +5V for the compute stack, not a separately regulated servo supply. This establishes the public board's net topology, not the installed robot's harness or revision. [Pinned PCB](https://github.com/pollen-robotics/elec_RPI_Robot_HAT/blob/23eab11927f95ceca0dfa35bf182caeb7db39ea0/elec_RPI_Robot_HAT.kicad_pcb).
4. Both standard variants have a specified input range of **3.7–6.0 V**, recommended **5 V**. Selecting M077 instead of M288 therefore does not resolve the supply conflict. Register 0 identifies standard M288 as **1200**, M077 as **1190**. Configurable voltage-fault thresholds are not an extension of rated supply voltage. [ROBOTIS M288 manual](https://emanual.robotis.com/docs/en/dxl/x/xl330-m288/), [M077 manual](https://emanual.robotis.com/docs/en/dxl/x/xl330-m077/).

## Separate upstream protection discrepancy

The runtime sets `shutdown = 52` and its startup routine writes that value when a motor differs. Decimal 52 is **0x34**, with bits 2, 4 and 5 set and bit 0 clear. The source comment says input-voltage protection is included; the manual's Shutdown table places that protection at bit 0. Thus the comment is inconsistent with the configured mask. The manual's voltage-limit subsection also contains conflicting bit wording; this audit uses the explicit Shutdown table and its 0x05 example, and records that discrepancy instead of concealing it. [Runtime mask](https://github.com/pollen-robotics/microduck/blob/5984efb770855432b03dafd3d879e9929981e45b/duck-control/src/model.rs#L82), [startup writes](https://github.com/pollen-robotics/microduck/blob/5984efb770855432b03dafd3d879e9929981e45b/duck-control/src/bus.rs#L129), [Shutdown reference](https://emanual.robotis.com/docs/en/dxl/x/xl330-m288/#shutdown63).

This is not evidence that raising thresholds or disabling protection makes an overvoltage supply acceptable. No mask, runtime setting or modeled rail was changed by this audit.

## What remains undecidable without original hardware evidence

- Exact per-joint M288/M077 identity, firmware and any manufacturer-qualified custom electrical variant.
- Whether the target robot has an additional power stage or a different HAT/harness revision.
- Actual voltage at the first and last servo, including startup and load transients.
- Whether the published battery mapping represents the delivered hardware accurately.

A generic 5 V regulator is a redesign proposal, not evidence of a 1:1 original. It would also make the present 6.6 V empty threshold incompatible with servo-side telemetry. Obtain the original configuration and measurements before choosing that route.

## Factory evidence procedure — not executed

1. Identify the original robot by serial/revision and photograph every servo label, HAT silkscreen, battery label and the full battery-to-servo harness, including any intervening board. Return original-resolution files and identify each joint.
2. Have the responsible technician isolate drive power and support the mechanism. First inspect routing and continuity with power removed. Do not energize an unidentified servo chain from the 2S pack to resolve this question.
3. Using a known compatible interface and verified supply appropriate to the identified servo, with robotd absent from the bus and no torque/motion commands, perform **read-only Protocol 2.0** identification. Record per-ID raw bytes, decoded values, communication errors and timestamps. Do not launch robotd for this capture: its initialization can rewrite EEPROM.

| Address | Bytes | Capture |
|---|---:|---|
| 0 | 2 | Model number |
| 6 | 1 | Firmware version |
| 7 | 1 | ID |
| 8 | 1 | Baud setting |
| 11 | 1 | Operating mode |
| 32, 34 | 2 each | Maximum/minimum voltage thresholds |
| 63 | 1 | Shutdown mask |
| 64 | 1 | Torque-enable state |
| 70 | 1 | Hardware error status |
| 144 | 2 | Present input voltage, 0.1 V/count |
| 146 | 1 | Present temperature |

4. Capture all 15 IDs (10–14, 20–24, 30–34); keep ID 200's IMU record separate. An absent device remains absent, never inferred from the others. Compare label identity with register 0, and escalate any nonstandard model/firmware to the supplier for its exact rating document.
5. Only after the supply path and ratings are established, a qualified technician can capture simultaneous battery voltage and actual VDD-to-GND at first/last servo with a meter and oscilloscope during an approved operating test. Record idle, startup extrema and representative load extrema, probe points, instrument settings and firmware build. Stop if measured supply exceeds the identified device's rated range. Return raw traces, not only a battery percentage screenshot.

The register addresses and encodings above come from the manufacturer's control tables. This procedure requests evidence; it neither authorizes operation nor claims a completed physical test. Source downloads and SHA-256 values are recorded in `PROVENANCE.json`.
