# connection:press-fit-tube-15 — the jaw pivot's cradle end

A **Ø15.0 open arch, 149.06° of circle, cut off flat at its chord** — the
motor support's `-x` face holding the outer race of the 15×10×3 bearing
that the jaw's Ø10.0000 journal turns in.

Shaped after `ce-connections/press-fit-bearing-15x10x3`. It is a separate
folder because it is a separate *kind* of joint: that one grades an ISO 286
fit in a 360° pocket; **this one has no fit to grade**, because 210.94° of
its circle is open air.

## The cradle, measured — and re-measured

**The diameters on this page were re-measured on 2026-09-03 and the first
set was wrong.** A `cecad.meshslice` cross-section fit does not read a
cylinder: its point set mixes facet **corners**, which lie *on* the design
cylinder, with points interpolated along facet **edges**, which lie *inside*
it by up to one sagitta (0.00773 mm here). Each fit below reports
`n_pts` 61 = 31 corners + 30 edge points, so it reads about half a sagitta —
**0.0039 mm** — small. That is exactly the shortfall from Ø15.0000, and it
is the same defect this folder had already diagnosed for its Ø16.8 relief on
2026-09-02 and failed to apply to its own headline number.

A free-centre circle fitted to the mesh **vertices** at each of the four x
stations that carry them (`out/laneT/remeasure_bore_vertices.py`, frozen in
`evidence/tube-15-geometry.json` → `vertex_remeasure_2026_09_03`):

| x (mm) | Ø (mm) | centre (y, z) mm | residual max (mm) | vertices | arc (°) |
|---|---|---|---|---|---|
| −39.5000 | **15.000000** | 0.000000, 7.500000 | 0.0000007 | 31 | 149.07 |
| −37.5000 | **15.000000** | 0.000000, 7.500000 | 0.0000007 | 31 | 149.07 |
| −36.5000 | **15.000000** | 0.000000, 7.500000 | 0.0000007 | 31 | 149.07 |
| −35.5000 | **15.000000** | 0.000000, 7.500000 | 0.0000007 | 31 | 149.07 |

Every station returns the identical fit to 8 dp (Ø15.00000018). Tolerance
basis: the spread *across* stations is 0.0 mm; the spread *within* one is
0.0000007 mm, which is the STL's float32 storage. The superseded chord fits
read Ø14.9954 / 14.9938 / 14.9978 at x −39.00 / −38.50 / −36.40, with two
further stations at the arch's ends (Ø15.0121, Ø15.0179) where the section
also picks up the chamfer.

The chord plane is **z 9.5000** and the crown **z 15.0000** at every
station; the section at x −38.5 spans z 9.5000..16.1919 and nothing else,
so **there is no material below the chord.** Outer surface **Ø17.400000**
(vertex fit, 32 vertices at each of x −39.5000 / −38.5000, residual max
0.0000006 mm; the chord fit read Ø17.3926).

Ring bands, read by ray-cast (`cecad.meshfeatures.intervals`) along x at
radius 8.100 mm from the axis — inside the Ø17.40 outer wall, outside the
Ø15 bore, so material exists exactly where a band does. The band **ends**
are what a ray reads honestly; the band **diameters** are vertex figures:

    x −39.5000 .. −37.5000     2.0000 mm
    x −36.5000 .. −35.5000     1.0000 mm      (Ø16.800000 relief between)

A note on the relief, because it is the second correction on the same
surface: the 2026-09-02 fix pass re-measured it off vertices — the right
method — but took a mean radius about a **fixed** seed axis at z 7.4995,
itself a chord number, and read Ø16.8007. Over an arc of 152.4451° centred
on +z, a seed 0.0005 mm below the true axis biases the mean radius by
0.0005 × ⟨cos⟩ = 0.000366 mm, i.e. **+0.00073 mm on the diameter** — the
whole of the +0.0007 mm that row attributed to "the STL's float32 storage".
With the centre free the same vertices read Ø16.800000 and put the axis at
z 7.500000. **That explanation is refuted; float32 stores 15.0 exactly.**

## The other side

| what | measured |
|---|---|
| the ring | **Ø15.000000** OD (vertex fit, 72 vertices at each of z 0.3000 / 2.7000, residual max 0.0000006 mm) / Ø10.000000 bore / 3.0 wide — `part:bearing-15x10x3`, re-measured here so the comparison is like-for-like |
| the journal in its bore | the jaw's **Ø10.000000** boss, centre (y 0.000000, z 7.500000), residual max 0.0000006 mm, x −39.7000..−37.0000 (2.7000 mm), behind a **Ø12.000000** × 0.3000 flange (the 0.00254 mm quoted before was the *instrument's* residual, not the surface's; the flange read Ø11.9949 by the same chord artefact) |
| cradle ↔ ring | **line-to-line: diametral gap 0.0000 mm.** Zero clearance, zero interference, both sides measured the same way |
| coaxiality | cradle ↔ journal **better than 0.0000010 mm** — the two fitted axes differ by 0.000000031 mm, below either fit's own residual, so this is bounded by the instrument rather than resolved by it. The 0.0005 mm published before was the difference between two *chord*-fit centres |

## Two measured facts kept rather than smoothed

1. **Pollen's MJCF places the bearing geom 0.2000 mm high** (axis at z 7.7000
   against the parts' 7.500000) and 0.3000 mm outboard of the jaw's flange.
   The two *parts* agree to better than 0.0000010 mm; the *visual model's*
   placement does not.
2. **The host interface was named `lens_tube` and called itself a lens seat,
   and that is false.** In this same frame the m12 lens holder is at
   y −52.38..−37.58 and the lens at y −63.8..−44.88 — a different axis
   37–64 mm away, with no Ø15 surface on either (barrel Ø11.6 / 13.6 /
   16.94). What *is* on this axis is the bearing (0.181 mm off-axis in
   world) and through it the jaw journal (coaxial to < 0.0000010 mm).
   `compat.py` carries
   `claims_a_lens_seat` as a permanent regression guard: it FAILs a row that
   claims a lens, and PASSes the corrected row that keeps the legacy *name*
   (so `part.py`'s connector does not dangle) while stating the measurement.

## What the checks can and cannot grade

- **Diameter** — graded, and it is **line-to-line**: Ø15.000000 cradle
  against a Ø15.000000 ring, diametral gap **0.0000 mm**. There is no
  interference here and none is claimed. Until 2026-09-03 this check printed
  −0.0062 to −0.0022 mm of "nominal interference"; that came of
  chord-fitting the cradle and vertex-measuring the ring, and it was not
  real. The verdict never rested on it — an arch open over 210.94° cannot
  grip at any interference.
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
