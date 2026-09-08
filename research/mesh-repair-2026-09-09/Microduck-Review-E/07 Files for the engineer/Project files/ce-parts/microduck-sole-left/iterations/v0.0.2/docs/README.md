# part:microduck-sole-left — the left TPU sole, rebuilt parametrically

**What it is.** The mint TPU boot (41.069 x 54.0 x 12.905 mm measured off the
rebuild; Pollen's mesh 41.099 x 54.0 x 12.907) — the robot's left ground
contact. v0.0.1 (kept) loaded Pollen's mesh as-is; v0.0.2 is the parametric
rebuild, graded PASS by cad-refcheck vs sole_left.stl: p95 0.05/0.05 mm,
bbox delta <= 0.03 mm (evidence/refcheck/, out/refcheck/microduck-sole-left/r2/;
r1 FAILed at 2.24 mm from a folded non-ruled loft — fixed by ruled=True).

**How it was measured.** `cecad.meshslice` probes throughout
(out/measure/foot/probe_sole.txt, probe_sole2.txt):
- shell: floor 2.000 mm thick vertically (every C-grid interval 2.000
  +- 0.005); walls 1.6..2.1 (outer bulges, inner faces vertical);
- cavity = the foot cap's lower body exactly: x 31.6..68.4, y -9.9..39.9,
  corners R3.4 back (centres (65, 36.5)) / R4.9 front (centres (36.5, -5)),
  zero clearance measured on both meshes;
- outer floor: the 27 x 31 measured table in part.py (floor_table.py);
  behind it: plane z = 0.08697x - 34.4395 (residuals <= 0.007 mm), heel arc
  R7.204, toe arc R6.884, side fillets R7.87-7.91 (fit_floor.py) — the
  corner blends fit no single arc, hence the table;
- rim plane z -18.342, ring 1.5-1.7 mm wide.

**CANNOT DETERMINE:** the TPU shore hardness and infill Pollen prints with
(not published); whether the cavity is a friction fit or glued.

**Mirror.** sole_right.stl is this mesh mirrored about x = 0 (p95 0.002 mm,
max 0.008 mm) — the right folder flips HAND only.
