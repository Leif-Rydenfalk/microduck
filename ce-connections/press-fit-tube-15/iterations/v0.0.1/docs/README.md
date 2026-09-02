# connection:press-fit-tube-15 — the jaw pivot's cradle end

A **Ø15.0 open arch, 149.06° of circle, cut off flat at its chord** — the
motor support's `-x` face holding the outer race of the 15×10×3 bearing
that the jaw's Ø10.0000 journal turns in.

Shaped after `ce-connections/press-fit-bearing-15x10x3`. It is a separate
folder because it is a separate *kind* of joint: that one grades an ISO 286
fit in a 360° pocket; **this one has no fit to grade**, because 210.94° of
its circle is open air.

## The cradle, measured

`cecad.meshslice` cross-sections of `motor_support.stl`, circle-fitted to
the points in the 7.2–7.9 mm annulus about the axis (2026-09-02, frozen in
`evidence/tube-15-geometry.json`):

| x (mm) | Ø fit (mm) | centre (y, z) mm | residual mean (mm) | span (°) |
|---|---|---|---|---|
| −39.00 | 14.9954 | 0.0001, 7.4996 | 0.00264 | 149.06 |
| −38.50 | 14.9938 | −0.0000, 7.4995 | 0.00352 | 149.06 |
| −36.40 | 14.9978 | 0.0000, 7.4998 | 0.00127 | 149.07 |

The chord plane is **z 9.5000** and the crown **z 15.0000** at every
station; the section at x −38.5 spans z 9.5000..16.1919 and nothing else,
so **there is no material below the chord.** Outer surface Ø17.3926
(residual max 0.0263).

Ring bands, read by ray-cast (`cecad.meshfeatures.intervals`) along x at
radius 8.100 mm from the axis — inside the Ø17.39 outer wall, outside the
Ø15 bore, so material exists exactly where a band does:

    x −39.5000 .. −37.5000     2.0000 mm
    x −36.5000 .. −35.5000     1.0000 mm      (Ø16.8 relief between)

## The other side

| what | measured |
|---|---|
| the ring | Ø15.0 OD / Ø10.0 bore / 3.0 wide — `part:bearing-15x10x3`, its own frozen evidence |
| the journal in its bore | the jaw's **Ø10.0000** boss, centre (y 0.0000, z 7.5000), residual max 0.00254 mm, x −39.7000..−37.0000 (2.7000 mm), behind a Ø11.9949 × 0.3000 flange |
| coaxiality | cradle ↔ journal **0.0005 mm** |

## Two measured facts kept rather than smoothed

1. **Pollen's MJCF places the bearing geom 0.2005 mm high** (axis at z 7.7000
   against 7.4995 / 7.5000) and 0.3000 mm outboard of the jaw's flange. The
   two *parts* agree to 0.0005 mm; the *visual model's* placement does not.
2. **The host interface was named `lens_tube` and called itself a lens seat,
   and that is false.** In this same frame the m12 lens holder is at
   y −52.38..−37.58 and the lens at y −63.8..−44.88 — a different axis
   37–64 mm away, with no Ø15 surface on either (barrel Ø11.6 / 13.6 /
   16.94). What *is* on this axis is the bearing (0.181 mm off-axis in
   world) and through it the jaw journal (0.0005 mm). `compat.py` carries
   `claims_a_lens_seat` as a permanent regression guard: it FAILs a row that
   claims a lens, and PASSes the corrected row that keeps the legacy *name*
   (so `part.py`'s connector does not dangle) while stating the measurement.

## What the checks can and cannot grade

- **Diameter** — graded. −0.0062 to −0.0022 mm of nominal interference
  against a Ø15.0 ring. On an FDM-printed 149° arch that is a modelling
  coincidence, not a press fit, and it is not called one.
- **Angular capture** — graded, and it is **CANNOT DETERMINE at 149.06°**:
  less than a half-circle, so the arch never reaches past the ring's centre.
  It locates; it does not capture.
- **Band length** — graded: 3.0000 mm of band for a 3.0000 mm ring, but only
  **2.0000 mm (66.7 %)** touches it where the MJCF puts it.
- **Retention** — **refused by name.** An open cradle's holding force is
  whatever closes it, and **nothing closes this one** in any of Pollen's four
  MJCF files. That is not a bench measurement waiting to happen; it is a
  missing part. *What settles it:* a photograph or teardown of a real
  Microduck head with the motor support in place, or Pollen publishing the
  head assembly.

## Why `mate()` raises instead of seating at 0.0

No groove, shoulder or end stop exists on either band, so nothing in the
geometry locates the ring along the axis. `mate()` demands `seat_dz_mm` or
`shoulder_z_mm` and refuses otherwise — the `press-fit-608` rule this shelf
inherited: *a bearing 2 mm from where the drawing says looks correct in
every render.*
