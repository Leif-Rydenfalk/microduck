# microduck-trunk-base — the chassis plate

**What it is.** Pollen's `trunk_base` mesh: a 57 x 36 x 1 mm PLA plate with
R2 corners, two Ø19.0 holes on a 35 mm pitch (the hip-yaw servo hubs pass
through; the joint axes of the MJCF), four Ø2.3 M2 clearance holes along one
long edge (the inner pair takes the power_support's flange), a 6 x 12 mm R2
cable slot in the middle and four Ø1.8 tapered locating pins 2 mm proud of
the top face along the other long edge.

**Verdict: PASS** — `ce-cad/bin/cad-refcheck part:microduck-trunk-base --ref
reference/pollen-microduck-rl/assets/trunk_base.stl`, round 1: p95 surface
distance 0.001 mm ref->ours and ours->ref (max 0.009), bbox delta 0.00 mm on
every axis, 6/6 reference holes matched (2 x Ø19.0, 4 x Ø2.3), volume ratio
0.9996. Report and overlays: `evidence/refcheck/<stamp>/`, and
`out/refcheck/microduck-trunk-base/r1/`.

## How it was measured (2026-09-01)

- `cad-mjcf sections trunk_base.stl --axis x|y|z --n 20 --metres`: outline
  57.0 x 36.0, plate z 16.5..17.5, pins to 19.5; corner shrink 0.086 at
  1.425 mm in and 0.331 at 0.9 mm in -> R2.
- `cecad.meshfeatures.cylinders`: 2 holes Ø19.0 at (±17.5, -2.0), 4 holes
  Ø2.3 at (±9.5, 20.5) and (±25.5, 20.5), all axis z, coverage 355 deg.
- `cad-mjcf probe` (material intervals along a line; added to cecad for this
  group): slot x -3..3 at y -2..5, y -2..10 at x 0, and y -1.732..9.732 at
  x ±2 -> R2 corners; pins 1.696 wide at z 18.5 on (±9.5, -9.5) / (±25.5,
  -9.5), material z 16.5..19.5; the z-sections give Ø1.787 at z 17.625 and
  Ø1.598 at z 19.425 -> a 0.105 mm/mm taper, Ø1.80 -> Ø1.59.
- `cad-mjcf sections --at 17 --image` (gridded section picture, added too):
  `out/measure/tb/section_z_17.000.png`.

## CANNOT DETERMINE

- Which part the four locating pins enter (a shell half? the pcb?) — not one
  of this group's meshes. What would settle it: probe the shells' meshes
  for Ø1.8-2.0 blind holes at (±9.5, -9.5) / (±25.5, -9.5) in this frame.
- What the four M2 screws thread into (nut or a printed boss) — the plate is
  clearance both sides.
- Whether the pin taper is a draft or a chamfer: the decimated mesh has 4
  rings per pin; 0.1 mm either way.
