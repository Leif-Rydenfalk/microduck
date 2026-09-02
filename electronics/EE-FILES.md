# EE files — the three deliverables (Leif, 2026-09-02)

Not one mixed diagram. Three files, each turning the previous into more detail,
all authored as clean vector SVG straight from the measured netlist
(`gen_ee.py` reads `netlist.graph.json` — the pin→net map for every device).
Regenerate: `python3 electronics/gen_ee.py`.

| # | file | what it shows |
|---|---|---|
| 1 | `1-block-diagram.svg` | **Block diagram** — how everything flows: functional blocks (compute, power, servo bus, sensors, audio, comms, NFC) and the buses between them, colour-coded. No pins. |
| 2 | `2-schematic-{radxa,hat,imu,sensors}.svg` | **Schematic** — every component, every pin, and the net each pin connects to. Power red · digital bus blue · I²C amber · UNKNOWN (unpublished) in amber. Trace a net name (e.g. `i2c3/SDA`) to every other pin that carries it. |
| 3 | `3-layout.svg` | **Layout** — the physical connection map: each board/device in its body region (head / neck / trunk / legs), and every cable run labelled with its measured length (mm). |

`wiring/designs/microduck/wiring.svg` is a graphic input; file 3 supersedes it.
A pin or net the published source does not give is drawn **UNKNOWN**, never guessed —
notably the HAT's regulators, the imu_to_dxl MCU/transceiver, and the NFC IC.
