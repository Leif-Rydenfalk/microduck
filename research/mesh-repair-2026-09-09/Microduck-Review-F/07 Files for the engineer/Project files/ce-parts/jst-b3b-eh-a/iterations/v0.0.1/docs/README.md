# part:jst-b3b-eh-a — JST B3B-EH-A, 3-circuit EH Type A header

The socket on every DYNAMIXEL X-series TTL servo and on the Robot HAT's bus
port. ROBOTIS e-Manual XL330-M288-T §Connector Information, verbatim:
"Housing JST EHR-03 / PCB Header JST B3B-EH-A / Crimp Terminal JST
SEH-001T-P0.6 / Wire Gauge for DYNAMIXEL 21 AWG".

Every dimension in `cad/part.py` names the page of `docs/fetched/eEH.pdf` it
was read from (p.4 Header/Type A; p.2 layout). The mate frame is the pin-row
centre on the board plane, +z out of the board, +x circuit 1 → 3.

Mates with `part:jst-ehr-03` through `connection:jst-eh-3pin`, whose seating
datum is the (8.1) mated assembly height on p.2 minus the housing's 6.5 on
p.3 = 1.6 mm housing-face-to-board.

What is NOT here: internal latch/rib detail (envelope only), a vendor mass,
an offer for this member. See component.json `why`.
