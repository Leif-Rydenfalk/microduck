# connection:snap-fit-ankle-blocks — and nothing snaps

Two rectangular spigots on the ankle drop through two matching pockets in
the foot while the ankle's **R16.3** under-hull lands on the foot's two
**R16.3** end ledges. **0.1000 mm of clearance per side, on both axes.**

## The pair, measured with one instrument on both meshes

`cecad.meshfeatures.intervals` ray-casts through each mesh on the same
lines (2026-09-02, frozen in `evidence/ankle-blocks-fit.json`):

| | ankle blocks | foot pockets | per side |
|---|---|---|---|
| x | 34.1000…39.1000 and 60.9000…65.9000 → **5.0000** | 34.0000…39.2000 and 60.8000…66.0000 → **5.2000** | **0.1000** |
| y | 31.6630…35.6630 → **4.0000** (two 1.5000 ribs, 1.0000 gap) | 31.5630…35.7630 → **4.2000** | **0.1000** |
| z | −21.3420…−15.2810 (inner rib, 6.0610) and −21.3420…−13.3420 (outer rib, 8.0000) | **open top to bottom** | — |

Pair pitch **26.8000 mm** (block roots x 34.1000 and 60.9000) — that pitch is
what makes the pair an *anti-rotation* feature rather than a single peg.

## The cradle that actually carries the load

The ankle's under-hull circle-fits to **R16.3058** (residual mean 0.00432,
49 pts) at x 40 and **R16.3018** (0.00396, 48 pts) at x 60, about a centre
0.007–0.011 mm from the declared ankle axis (y 22.0000, z −6.2230). The
foot's own folder measured its R16.3 ledges at x 32.9000…34.1500 and
65.8500…67.1000 and an R16.5 relief band across the rib tops — so the ribs
stand **0.2000 mm clear** and the load lands on the two end ledges.

*(Lane T did not re-measure the foot ledges: its own fits at x 33.5 and 66.5
came back R16.556–16.646 with residual mean 0.031–0.044 mm because the
annulus window catches the relief band with the ledge. A worse instrument
does not overwrite a better one.)*

## Nothing snaps — and that is the finding

Searched on both meshes for an undercut, barb, lip or lead-in. There is
none:

- the pockets are **open top to bottom in z** — five stations inside them
  return no material at all, so there is no lip for a barb to pass;
- the blocks are prismatic over their whole height (x span constant across
  y 31.8…35.5; the z intervals are single unbroken spans);
- and the fit is a **0.1000 mm per-side clearance**, which cannot snap into
  anything.

What retains the foot is the single **M2 at (x 50.0000, y 4.5020)** —
ankle `foot_screw` (Ø2.2 through a 2.5 mm plate, Ø4.4 × 1.0 counterbore)
into foot `ankle_screw` (Ø1.6 × 5.5 thread-forming pilot, Ø3.0 × 0.5 relief
on a Ø5 boss) — `connection:threaded-m2`.

`snap-fit-ankle-blocks` is the slug the parts' `accepts` lists already
carried. The slug is kept so nothing dangles; the *claim* is corrected.
`compat.py` carries **`claims_a_snap`**, which FAILs any row asserting a
snap or a barb without a number, and `mate()` **refuses**
`params['snap_force_N']` outright.

## What stays CANNOT DETERMINE

- **The as-printed fit.** 0.1000 mm per side is a *quarter* of a 0.4 mm FDM
  extrusion width. Slicer compensation, elephant's foot and the nozzle's
  corner radius all move a printed pocket by that much. *What settles it:*
  calipers on a printed block and pocket — state `measured_pocket_mm`.
- **The load share** between the two end ledges and the R16.5 relief band —
  a contact question, not a geometry one.
