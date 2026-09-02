# connection:snap-fit-roller-axle — a real snap, onto the ankle, not a roller

Two barbed cantilever fingers on the foot close over the ankle's 36.5000 mm
plate. The slug promises a roller axle; **measurement says the roller is
never here.**

## The fingers, by height

Ray-cast calipers (`cecad.meshfeatures.intervals`) along y through
`foot_left.stl` at x 50, 2026-09-02 — the gap between the two inner faces:

| z (mm) | inner faces (mm) | gap (mm) | |
|---|---|---|---|
| −12.3500 | 0.3690 / 36.4580 | **36.0890** | top of the lead-in (the foot's own top face is z −12.3419) |
| −12.8000 | 0.6840 / 36.1430 | 35.4590 | |
| −13.2000 | 0.9640 / 35.8630 | 34.8990 | |
| −13.4000 | 1.0630 / 35.7630 | **34.7000** | barb land begins |
| −14.0000 | 1.0630 / 35.7630 | **34.7000** | barb land ends (0.6000 mm tall) |
| −14.5000 | 0.0630 / 36.7630 | **36.7000** | the pocket |
| −15.0000 | 0.0630 / 36.7630 | 36.7000 | |

Lead-in **0.6945 mm per side over 1.0500 mm** of rise — a 33.47° half angle.
Barbs **1.0000 mm proud per side** (36.7630 − 35.7630). The fingers run
along **x 45.0000…55.0000** (10.0000 mm) — that span reproduces exactly at
y 0.0 and y 37.0 and at z −12.5, −12.6, −13.0.

## What they capture

`ankle_left.stl` at x 50 spans **y 0.1632…36.6632 = 36.5000 mm** at
z −15.5000 and −15.0000, and narrows to 1.5630…35.2630 = **33.7000 mm** at
z −14.5000 and above. So:

| | mm |
|---|---|
| plate in the pocket | 36.5000 in 36.7000 → **0.1000 per side** |
| narrow part vs the barb land | 33.7000 in 34.7000 → 0.5000 per side clear |
| deflection to pass the barb | **0.9000 per finger** |
| barb overhang over the shoulder | **0.9000 per side** |

Three features on one part pair, each with a different job: the **blocks**
(`connection:snap-fit-ankle-blocks`) index, this **snap** retains, and the
single **M2** (`connection:threaded-m2`) secures.

## The roller reading is unsupported

The foot folder's row said *"…two x 45..55 snap fingers rising to z −12.342
with 1.0 mm barbs facing each other — the clip-on roller drops between
them."* **All three numbers reproduce exactly.** Only the last clause fails:

- `roller_blade`, `tire` and `rim` appear in **exactly one** of Pollen's
  four MJCF files — `robot_allcollisions_rollers.xml`, in both reference
  copies — and that file contains **no** `foot_left`, `foot_right`,
  `sole_left` or `sole_right` geom at all. The roller variant replaces the
  whole foot assembly.
- It swaps the ankle too: `ankle_l_v1` / `ankle_r_v1`, whose vertical
  Ø2.2 / Ø3.5 sits at **(50.1090, −5.5000)** — matching `roller_blade`'s own
  Ø1.6 pilot at (50.1090, −5.5000, −18.8240) — where `ankle_left`'s vertical
  Ø2.2 is at **(50.0000, 4.5020)**, the foot screw.

So in everything Pollen ships, no roller is anywhere near this slot, and
what *is* in it is the ankle's own plate. The slug is kept (both foot parts
already `accept` it and renaming would dangle); the claim was corrected in
the part folder and `compat.py` carries **`captures_what`** as the guard.

## What stays CANNOT DETERMINE

**The insertion and retention forces.** The deflection (0.9000 mm per
finger), the finger run (10.0000 mm) and the lead-in angle are all measured.
The beam formula that would turn them into newtons needs the printed PLA's
modulus and permissible strain **at this layer orientation**, and neither is
in any file in this repo. A handbook formula fed a guessed modulus is a
number with a citation and no source, so `compat.py` refuses it by name and
`mate()` states it in `why.force`. *What settles it:* push a printed pair
home on a gauge, record the peak, pull it off, record that — then state
`insertion_N` and `retention_N`.
