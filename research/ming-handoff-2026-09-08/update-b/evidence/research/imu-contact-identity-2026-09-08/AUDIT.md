# Original IMU bridge and battery-contact identity — 2026-09-08

**Neither board's exact original hardware identity is closed.** Current public discovery adds reproducible scope and rules out misleading neighboring projects; it does not establish a replacement design as a 1:1 original.

## What was inspected now

- Enumerated **215** public repositories returned by the paginated Pollen organization API; names and current push timestamps are saved in `org-repositories.json`.
- Captured complete, explicitly untruncated recursive trees and paginated release metadata for `microduck`, `microduck_rl`, `rustypot`, `elec_RPI_Robot_HAT`, `7V_converter` and `power-supply-board`.
- Ran official-organization code searches for `imu_to_dxl`, `LSM6DSV16X` and `banana_pcb`; saved the results. Search indexing can omit material and is not exhaustive proof of absence.
- Inspected the current runtime decoder, setup script and bring-up document. `microduck` has **28 releases / 184 named assets** in the observed metadata; none is named as an IMU/contact-board firmware image or schematic. Release archive contents were not downloaded or inspected.

Runtime revision: **5984efb770855432b03dafd3d879e9929981e45b**. RL revision: **2b25a48b08f1f17bc38c90bb03144c81fbd9ed07**. Public HAT revision remains **23eab11927f95ceca0dfa35bf182caeb7db39ea0**. Exact download URLs/hashes are in `PROVENANCE.json`.

## IMU-to-Dynamixel bridge

The current [official decoder](https://github.com/pollen-robotics/microduck/blob/5984efb770855432b03dafd3d879e9929981e45b/duck-control/src/imu.rs) identifies **imu_to_dxl v2 / LSM6DSV16X**. The host reads a 12-byte block at address **124**: three little-endian signed gyro values, then three half-precision SFLP quaternion components; it reconstructs the remaining component. The source describes a 20-byte diagnostic block, but the host consumes only 12. Its decoder applies the recorded sensor-to-trunk mounting transform and holds the last quaternion while startup samples remain uninitialized.

The [runtime model](https://github.com/pollen-robotics/microduck/blob/5984efb770855432b03dafd3d879e9929981e45b/duck-control/src/model.rs) identifies bus ID **200**. The current setup/bring-up files still treat the IMU as an already functioning device on the shared servo bus; they do not identify its MCU, transceiver, bootloader or board fabrication files.

| Requirement | Current evidence |
|---|---|
| Sensor family, v2 host packet interpretation, ID | Established as current official host contract |
| Exact MCU and transceiver | Unresolved; no supporting identity source found in this inspection |
| Input supply limits/regulator/current | Unresolved for the full bridge board |
| PCB revision/schematic/Gerbers/BOM | No matching source found in inspected trees/searches |
| Bridge firmware image/source/version and flashing method | Unresolved; host Rust decoder is not bridge firmware |
| Connector count and physical branch location | Unresolved; a shared bus does not establish a three-socket board |
| Match to target production unit | Requires original-board identity evidence |

STM32G0, CH32V or another protocol-compatible MCU remain hypothetical replacements, not established original components.

## Battery-contact board

The current [RL sidecar](https://github.com/pollen-robotics/microduck_rl/blob/2b25a48b08f1f17bc38c90bb03144c81fbd9ed07/src/mjlab_microduck/robot/microduck/assets/banana_pcb_locker.part) identifies **Banana_PCB_locker**, Onshape document `804927696f06d877f3f1803e`, element `d6fcdccc8b25aaa256e7e213`, part `RfDD`, microversion `2f167ea7efece4caa36b89eb`. This is traceability for the mechanical retaining part. It does not identify battery contacts, copper, a protection circuit or a PCB BOM.

No contact-board schematic, full part number, revision, contact manufacturer, plating/current rating or original harness pinout was located. Calling the board passive remains an unverified assumption unless its actual circuit is inspected.

The official [7V_converter](https://github.com/pollen-robotics/7V_converter/tree/e85671d8377555e14a6a0d8606484f43e245e0a3) is documented for Reachy's 12 V-to-7.5 V head-motor supply. [power-supply-board](https://github.com/pollen-robotics/power-supply-board/tree/74da26aec65a85a522a7bff72bc54a9aed362a9f) serves Reachy's power/NUC/Robus system. Neither source ties those boards to Microduck's battery contact board. Their existence is not a resolved Microduck power path.

## Exact evidence needed from the original unit or manufacturer

Request both sides of each original board with readable silkscreen and chip markings, PCB assembly revision, connector designators/count, scale and installed-location photo. For the bridge request exact MCU/transceiver/BOM and the matching firmware source or signed release with build/version and flashing documentation. Have an authorized technician capture ID-200 traffic using the known-good runtime, including raw 12-byte register-124 replies; do not interpret unsupported registers through a generic servo control table. For the battery board request its original schematic/netlist and contact part numbers, plus power-isolated continuity evidence identifying every harness terminal. No such operation was executed in this audit.

These requests seek original identity. A compatible bridge, replacement contact arrangement, or synthetic packet stream cannot close 1:1 recreation.
