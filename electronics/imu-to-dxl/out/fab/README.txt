Microduck imu_to_dxl v2 (reconstruction)
========================================

40.0 x 22.0 mm, 876.49 mm2, 2 copper layers
stackup   JLCPCB 2-layer 1.6 mm, 1 oz — the commodity default
finish    
rules     JLCPCB 2-layer, standard process — tighter, and single-sourced
parts     24   nets 17   tracks 272   vias 27   drills 38

READ THIS BEFORE ORDERING
-------------------------

1. THE DESIGN RULES WERE CONFIRMED AGAINST THE FAB'S OWN CAPABILITY PAGE.

   Profile: jlcpcb_2l_standard   confirmed 2026-08-20

   CONFIRMED 2026-08-20 against https://jlcpcb.com/capabilities/pcb-capabilities, read that day, for the 2-layer FR-4 1.6 mm 1 oz process. What the page said, verbatim, and what it changed here:
     track / space, 1 oz .... '0.10 / 0.10 mm (4 / 4 mil)'  (2 oz: '0.16 / 0.16 mm (6.5 / 6.5 mil)') -> min_track_mm and min_clearance_mm 0.127 -> 0.10. The old numbers were TIGHTER than the fab, so no board was ever wrongly passed by them.
     plated hole diameter ... '0.15 - 6.3 mm' -> min_via_drill_mm LEFT AT 0.30. The page's floor is the drill the fab owns; over a 1.6 mm board the 8:1 aspect rule on this same profile floors it at 0.20 mm, and 0.30 mm is the size this profile hands the router as a DEFAULT via drill. Lowering it would shrink every via the autorouter places for no gain.
     PTH annular ring, 1 oz . 'Recommended 0.25 mm or above; absolute minimum 0.18 mm' (2 oz: '0.254 mm or above') -> min_annular_ring_mm 0.125 -> 0.25, and min_via_pad_mm 0.55 -> 0.80 (0.30 drill + 2 x 0.25). THIS IS THE CORRECTION THAT MATTERED. The transcribed 0.125 was LOOSER than the fab's own absolute minimum of 0.18, so it passed boards JLCPCB will not build: floorctl rev A had 55 vias at a 0.150 mm ring and a green annular-ring line under it.
     pad hole-to-hole ....... '0.45 mm' -> min_hole_to_hole_mm 0.50 -> 0.45.
     routed edge clearance .. '>= 0.2 mm' -> min_edge_clearance_mm 0.30 -> 0.20.
     maximum board size ..... '670 x 600 mm'.
     outer copper ........... '1 oz / 2 oz / 2.5 oz / 3.5 oz / 4.5 oz'.
     surface finish ......... 'HASL (leaded / lead-free), ENIG, OSP'.
   STILL TRANSCRIBED, NOT ON THAT PAGE: min_hole_to_copper_mm, min_silk_width_mm, min_silk_height_mm, min_silk_to_pad_mm, min_mask_sliver_mm, min_text_to_edge_mm and max_aspect_ratio. Each says so in its own statement. Confirm those against JLCPCB's silkscreen and solder-mask notes before relying on one of them alone.
   MULTILAYER (4-layer), read off the same page the same day and NOT the rules in this profile — this profile is the 2-LAYER process and a board built on it that goes out as 4-layer must be re-read against these: outer track/space '0.10 / 0.10 mm (4 / 4 mil)', inner track/space '0.09 / 0.09 mm (3.5 / 3.5 mil)', inner copper '0.5 oz / 1 oz / 2 oz' with '0.5oz by default', plated hole '0.15 - 6.3 mm', and PTH annular ring at 1 oz 'Recommended 0.20 mm or above; absolute minimum 0.15 mm' — LOOSER than the 2-layer 0.25 / 0.18, so a via that clears the 2-layer rule clears the 4-layer one.

   A capability page changes. Re-read it if this date is old.

3. PACKAGE DIMENSIONS ARE TRANSCRIBED, NOT MEASURED.

   NOT ONE DIMENSION IN THIS FILE WAS MEASURED FROM A PART IN SOMEBODY'S HAND. They are transcriptions of published outlines. That is a much stronger position than cecad/data/atech_footprint.json (which is authored from nothing), and a much weaker one than a micrometer. Before a board is ORDERED, the footprint of every part whose confidence is not `standard` must be checked against the datasheet of the exact orderable part number — `pcbcheck.check_footprints()` prints that list and refuses to go quiet about it.

4. WHAT THE DESIGN RULE CHECK DID NOT CHECK.

   Signal integrity, impedance, return paths, EMC, thermal design beyond a
   bare-trace current figure, and whether the circuit works at all. A board
   that passes DRC is a board that can be MANUFACTURED.

DRC RESULT
----------

   verdict: FAIL
   36 pass, 3 fail, 3 cannot determine

   [FAIL] unrouted GND
   [FAIL] unrouted IMU_INT1
   [FAIL] unrouted V3V3
   [CANNOT DETERMINE] binding microduck_imu_to_dxl
   [CANNOT DETERMINE] current microduck_imu_to_dxl
   [CANNOT DETERMINE] via microduck_imu_to_dxl

FILES
-----
   microduck_imu_to_dxl-F.Cu.GTL
   microduck_imu_to_dxl-B.Cu.GBL
   microduck_imu_to_dxl-F.Mask.GTS
   microduck_imu_to_dxl-B.Mask.GBS
   microduck_imu_to_dxl-F.Silk.GTO
   microduck_imu_to_dxl-B.Silk.GBO
   microduck_imu_to_dxl-F.Paste.GTP
   microduck_imu_to_dxl-B.Paste.GBP
   microduck_imu_to_dxl-Edge.Cuts.GKO
   microduck_imu_to_dxl-PTH.drl
   microduck_imu_to_dxl-NPTH.drl
   microduck_imu_to_dxl-positions.csv
   microduck_imu_to_dxl-bom.csv
   microduck_imu_to_dxl.kicad_pcb
