# part:jst-ehr-03 — JST EHR-3, 3-circuit EH cable housing

The plug on both ends of every DYNAMIXEL X3P lead (ROBOTIS e-Manual
XL330-M288-T §Connector Information: "Housing JST EHR-03"). JST's own table
writes EHR-3.

Dimensions: `docs/fetched/eEH.pdf` p.3 — A 5.0, B 9.5, 3.8 thick, 6.5 high,
0.6 lock rib, circuit 1 at (2.25) from the end. Mated stack with a B3B-EH-A
header is 8.1 high (p.1, p.2), so the housing face sits 1.6 above the board.

Frame: contact-row centre on the mating face; +z = insertion direction
(into the header, away from the wires); +x circuit 1 → 3. Body in z ∈ [−6.5, 0].

Loaded with three `part:jst-seh-001t-p0.6` crimp contacts ("Contacts Sold
Separately"). Joins a header through `connection:jst-eh-3pin`.
