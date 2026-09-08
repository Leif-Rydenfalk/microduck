# part:microduck-foot-left — the left foot cap, rebuilt parametrically

**What it is.** The yellow printed cap (40.085 x 54.0 x 16.905 mm measured off
the rebuild; Pollen's mesh 40.086 x 54.0 x 16.909) between the ankle bracket
and the TPU sole. v0.0.1 (kept) loaded Pollen's mesh as-is; v0.0.2 is the
parametric rebuild, graded PASS by cad-refcheck vs foot_left.stl:
p95 0.45/0.33 mm, median 0.000, bbox delta <= 0.004 mm, 2/2 holes matched
(evidence/refcheck/, out/refcheck/microduck-foot-left/r1/).

**How it was measured.** Everything with `cecad.meshslice.intervals` /
`.segments` and `cecad.meshfeatures.cylinders` on the mesh — the probe
scripts and raw numbers are in out/measure/foot/ (probe_foot.txt,
probe_foot2.txt, floor_table.txt). Highlights:
- rib comb: 10 ribs, pitch 3.500, thickness 1.750, y 1.288..34.538, open
  between ribs — the sole closes the bottom; rib bottoms = sole outer floor
  + 2.000 mm (5 stations checked, max dev 0.005);
- ankle cradle R16.3 about (y 22, z -6.223) = the ankle's under-hull radius
  and bottom (-22.523) exactly; rib tops relieved to R16.5 in y 12.9..31.1;
- flange sides drafted 0.1134 mm/mm, front/back rolled over (T-probe table);
- snap fingers x 45..55 with 1.0 mm barbs, tabs to z -12.342;
- pockets x 34.0..39.2 / 60.8..66.0 for the ankle's +y blocks (0.1 mm fit);
- M2 pilot Ø1.6 x 5.5 at (50, 4.502) under the ankle's foot screw.

**CANNOT DETERMINE** (decimation hides it; a physical part would settle it):
- the exact y-extent of the R16.5 relief band (12.9..31.1 chosen to match
  the rib truncation at z -20; the band edges could sit +-0.5 mm away);
- corner blends where the flange roll-over meets the drafted sides (the
  overlay shows ~0.5 mm of reference material proud at the four top
  corners — inside tolerance, shape unresolved at mesh resolution);
- whether the pilot hole is threaded or plain in Pollen's print.

**Mirror.** foot_right.stl is this mesh mirrored about x = 0 (point-to-
triangle p95 0.000 mm, max 0.005 mm) — the right folder flips HAND only.
