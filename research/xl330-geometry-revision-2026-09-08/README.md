# XL330 mechanical correction candidate — 2026-09-08

ROBOTIS's reference drawing specifies eight horn/idler Ø1.6 pilots, a
3 mm maximum hole depth and M2 tapping screws. The existing simplified model
uses 6 mm depth. The vendor STEP cylindrical faces span 2.9 mm. Its stepped
case mounting holes have Ø2 clearance for 3.5 mm at the front and 4.5 mm at
the rear, surrounding a Ø1.6 central pilot. The old model has straight Ø2 holes.

`candidate_part.py` corrects these holes in isolation. It does not replace the
published shelf iteration. The remainder of the exterior is still simplified;
material, original servo identity and production fit remain unresolved.
The vendor compound includes 15 solids and additional shells and must not be
treated as a single closed manufactured part. Frame mapping is
local(X,Y,Z) = (vendorZ + 8, vendorX, vendorY).

`verify_candidate.py`, run through `ce-cad/bin/cad`, passed standard topology
validation and 100 independent material/void probes of the finished BRep.
The candidate is one valid closed solid. The four-view image was inspected
and opened. First execution stopped on the legacy undefined material `PA`
while formatting mass. The rerun suppresses verbose mass formatting, retains
all standard geometry checks, and leaves mass unknown. No material was guessed.

`compare_engagement.py` hashes the unchanged placement source and drawing.
35 of 52 nominal servo-face screw penetrations exceed the drawing's 3 mm
maximum. This arithmetic uses modeled seating/grip, not physical measurements.
The remaining 17 are not thereby approved: M2 tapping geometry, seating and
original per-joint hardware remain unverified. Do not purchase these nominal
ISO screw lengths from this comparison.

Sources: `vendor-geometry.json` records the manufacturer STEP hash and measured
cylinders; `../xl330-mechanical-source-2026-09-08/REPORT.html` records the
official download route and drawing interpretation. Historical sources and
published geometry remain unchanged. Full assembly/interface revalidation is
still required before promoting any corrected shelf iteration.
