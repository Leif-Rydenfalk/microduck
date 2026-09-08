# connection:spline-xl330-horn — the XL330 horn-face joint

How every driven bracket on the Microduck hangs off its servo: the XL330's
Ø16 horn (or idler) disc bolted to a bracket face with 4 M2 screws on a Ø12
circle. "Spline" is in the slug because the XL330's output is splined
underneath; what the parts consume is the horn FACE, and that is what this
folder mates. Shaped after `~/dev/ce-workshop/ce-connections/spline-servo-25t`
(same rule inherited: **a horn mount is rigid — the rotation is the servo's,
never this joint's**).

## The pattern, measured on both sides

Servo side — `cecad.meshfeatures.cylinders` on
`reference/pollen-microduck-rl/assets/xl330.stl` (2026-09-01), constants
quoted in `ce-parts/xl330-m288-t/current/cad/part.py`:

| feature | value |
|---|---|
| disc | Ø16.0 × 3.0, both faces (horn +x at x 11.5..14.5, idler −x) |
| tapped holes | 4 × Ø1.6 × 6.0 deep per face, at (y,z) = (0,±6),(±6,0) |
| bolt circle | Ø12.0 (r 6.0) |
| Ø1.6 | = the M2 tap drill (`ce-cad/cecad/fasteners.py` M2 row) |

Bracket side — measured per consumer on the microduck shelf (each interface
quotes its own numbers): shin `knee` 4 × Ø2.2 on an 8.486 mm square — the
same Ø12 circle at the 45° positions (diagonal = 8.486 × √2 = 12.001);
yaw2roll `yaw_horn` 4 × Ø2.2 on r 6.0 at 0/90°; hip-bracket Ø2.4 on Ø12
with Ø4.84 c'bores; ankle, neck-pitch-bracket, yaw-roll-motion, trunk
shells the same family. The two phase spellings (0° vs 45°) are the
pattern's own 4-fold symmetry — the horn turns with the output, so phase is
`mate()`'s `params['index']` (0..3, REQUIRED, no default) plus the reported
`clock_deg` for the internal output spline.

## The contracts

- `cad/mate.py` — flips the bracket face onto the horn face
  (F(a)·J·F(b)⁻¹), clocks the pattern, returns `dof_left []`, `joint` (all
  locked, holds_by preload, driven FALSE — that field is doing the work),
  `adds ["part:screw-m2-iso4762"]` (qty 4 in `why.adds`; each screw is
  itself a `connection:threaded-m2` joint into the horn's Ø1.6 tap).
- `compat.py` — checks sides, bolt circle (accepts `pcd_mm` or the square
  spelling `screw_square_mm`), screw count 4, horn tap in the 1.5–1.7 band
  around the M2 tap drill, bracket clearance ≥ the 2.0 major; reports the
  centre pilot and strength as CANNOT DETERMINE.

## CANNOT DETERMINE, written down

- **Horn centre hub** — every bracket carries a Ø5–6 centre bore, but
  `xl330.stl` has *no* centre feature (axis probe solid −14.5..14.5,
  `cecad.meshslice.intervals`, 2026-09-02): Pollen's decimated export hid
  the hub. A ROBOTIS drawing of the XL330 horn would settle its diameter
  and whether it pilots in the bracket bore.
- **Clamp / strip torque** — 4 M2s in tapped plastic; nothing twisted off
  with a gauge in this workshop. The vendor's 0.52 N·m stall
  (ce-parts/xl330-m288-t) is the load to beat, not evidence it holds.
- **Output-spline clocking** — the internal spline is not in the mesh;
  `clock_deg` is carried verbatim as a build decision.
