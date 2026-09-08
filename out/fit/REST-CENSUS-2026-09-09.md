# Interference census — 2026-09-09 (rest pose and joint-range sweep)

`tools/prove_fit.py rest` rerun on the current
`ce-assemblies/microduck/current/placements.json` (134 rows: 70 Pollen meshes
seeded from the MJCF + 64 nominal screws), on 2026-09-09 01:30 CST.
Result: `out/fit/rest.json` (this run) and `out/fit/rest.log`.
Previous result preserved unchanged in `out/fit/baseline-2026-09-05/`.

## The previous result was wrong, and it was shipped

The 2026-09-05 `rest.json` (18 AABB candidates, 7 interfering pairs) was the
run the tool's own docstring describes as the metre/millimetre mix-up: every
Pollen mesh shrank 1000x to a speck, so almost nothing could overlap. The
guard that catches this was added to the tool afterwards, but the result file
was never regenerated. That stale file is inside the review snapshots
`research/review-release-2026-09-08/Microduck-Review-C/07 Files for the
engineer/Project files/out/fit/rest.json`, the `parallel-engineering-review`
Review-C snapshot, and the `mesh-repair-2026-09-09/Microduck-Review-F`
manifest. Issued `reviews/vNNNN` packages are immutable; the correction
belongs in the next numbered version, citing this file.

## Measured now

| bucket | pairs | meaning |
|---|---|---|
| screw × the part it is driven into | 93 | thread engagement modelled as overlap; expected. These are the 64 nominal screws whose 52 servo-face proposals are already withdrawn (see `docs/RECREATION-2026-09-08.md`). |
| contact ≤ 0.05 mm | 47 | mating faces and bearing seats touching; expected. |
| 0.05–0.3 mm | 8 | below the mesh decimation floor; reported, not graded. |
| **> 0.3 mm penetration** | **20** (16 distinct pairs) | listed below. |
| screw × a body it is not driven into | 2 | fastener #58 into `left_shell` 0.71 mm, #59 into `right_shell` 0.58 mm. |
| CANNOT DETERMINE | 4 | every pair involving `yaw_roll_motion` (open mesh, 42 boundary edges — the known part-29 defect). |

Assembled bbox 144 × 141 × 264 mm. 399 AABB candidates of 8911 pairs, 287 s.

### Penetrations above 0.3 mm (deduplicated, worst first)

| a | b | depth mm | shared volume mm³ | relief axis / mm |
|---|---|---|---|---|
| upper_leg_left | xl330 (hip-pitch servo) | 4.45 | 99.1 | y 4.95 |
| upper_leg_right | xl330 | 4.45 | 99.1 | y 4.95 |
| yaw2roll | xl330 | 4.33 | 405.6 | x 4.96 |
| bearing_roll/yaw2roll | xl330 | 4.33 | 405.6 | x 4.96 |
| leg (left shin) | xl330 (knee servo) | 4.33 | 379.6 | y 4.71 |
| leg_2 (right shin) | xl330 | 4.33 | 379.6 | y 4.71 |
| motor_support | speaker | 1.70 | 412.5 | z 1.69 |
| top_head_shell | xl330 (head servo) | 1.07 | 24.4 | x 1.24 |
| xl330 (trunk) | left_shell | 1.02 | 10.1 | y 3.04 |
| power_support | np_f970 (battery) | 0.95 | 20.6 | x 0.85 |
| lens | noenoeil (eye) | 0.90 | 359.5 | x 5.94 |
| xl330 (jaw) | bottom_head_shell | 0.90 | 20.2 | z 8.80 |
| yaw_roll_motion bearing | speaker | 0.78 | 6.2 | z 1.00 |
| right_shell | xl330 (trunk) | 0.66 | 4.8 | y 2.17 |
| m12_lens_holder | pcb (Pi Zero 2 W) | 0.44 | 83.6 | x 1.60 |
| np_f970 (battery) | left_shell | 0.33 | 5.8 | z 0.41 |

## Reading, under the tool's own inversion

The real Microduck walks with these meshes, so a collision here is first
evidence that the model is wrong, and only then a design problem.

1. **The six 4.3–4.5 mm servo × host-part hits are one systematic thing, not
   six.** They are identical left/right to the micron, and the relief axis is
   always the servo's horn axis. The Pollen `xl330.stl` visual mesh measures
   29 × 20 × 34 mm; the XL330-M288-T body is 23 mm across the horn axis, so
   the visual mesh carries about 6 mm of horn/idler stack. Where a bracket's
   bearing or horn seat wraps that stack, the overlap volume is the seat itself.
   This is consistent with, and not yet distinguished from, the servo-geometry
   discrepancies already on record in
   `research/xl330-geometry-revision-2026-09-08/` (6 mm modelled pilot vs
   3 mm specified; vendor centre region hollow where the simplified candidate is
   solid). Deciding it needs the vendor STEP servo in place of the visual mesh,
   which that lane owns. Nothing here should change a bracket.
2. **Pocket-seated parts** (speaker in `motor_support`, lens in the eye
   `noenoeil`, lens holder against the Pi Zero board) show large shared
   volumes with sub-2 mm depth: the seat is modelled solid where the real part
   is press-fitted or the pocket is a visual simplification. Lens holder × Pi
   board (0.44 mm, 1.6 mm relief) is the one worth a look in the head, because
   a board cannot be pressed into.
3. **Shell × servo and shell × battery** (0.3–1.1 mm) are within what
   decimated organic shells plus a 23-vs-29 mm servo mesh can produce. They
   are not graded as design collisions; they are graded as unresolved until the
   servo mesh question above is settled.
4. **`yaw_roll_motion` cannot be graded at all** until a closed mesh is used;
   the review lane's repaired 1270-triangle mesh exists but `placements.json`
   still points at the open simulator STL.

Ten of the 38 unique meshes are non-manifold (power_support, np_f970, both
soles and feet, jaw_soft, soft_mouth_top, jaw); one is open (yaw_roll_motion).
Ray-parity volumes on the non-manifold ones are reported but carry that caveat.

## Part 29 (yaw_roll_motion) graded with the closed mesh — added 01:50 CST

`tools/fit_yaw_roll_closed.py` substitutes, in memory only, the review lane's
closed repair `out/review-geometry/microduck-yaw-roll-motion.stl` (same part
frame as the reference: Kabsch on the 1242 shared triangles is identity to
1e-6 mm) and re-measures every AABB-overlapping pair. Result
`out/fit/yaw-roll-closed.json`:

| pair | result |
|---|---|
| yaw_roll_motion × its own xl330 (head-yaw servo) | 404.0 mm³ shared, 0.92 mm depth — the same servo-seat family as yaw2roll (405.6 mm³) and the legs; see reading 1 |
| × both 22×16×4 bearings | 0.02 mm; seated contact |
| × jaw_soft/xl330 | 0.0002 mm³; touching |
| × motor_support, top_head_shell, jaw, bottom_head_shell | clear, zero crossing triangles |
| × fasteners #38–#41 | thread engagement 1.5–2.5 mm; the part they are driven into |

So the opening in part 29 does not put the part into any shell, the jaw or the
motor support at rest. The only overlap it has is the servo-seat overlap every
servo-carrying part has. Range-of-motion is the sweep stage, below.

## Joint-range sweep — added 02:55 CST

`tools/prove_fit.py sweep` is now implemented: each of the 14 hinges is driven
across its full MJCF range in 5° samples with every other joint at zero; only
pairs with exactly one member distal to the joint are re-tested; a pair that is
clear at zero and interferes at a sample is bisected to 0.5° for the angle at
which the collision begins. `tools/fit_sweep_depth.py` then re-poses every
such pair at the edge of the envelope the published policies actually use
(walking + sit/stand joint extremes from `out/motion/legs.json`; head sine
amplitude and slot-crosstalk peaks from `out/motion/head.json`) and measures
penetration depth there. Results: `out/fit/sweep.json`, `out/fit/sweep-depth.json`.

**A defect found and fixed on the way.** The first sweep rotated every part about
the wrong centre: `prove_fit.py` built its zero pose from an all-zero qpos, which
puts the free-joint root at the origin, while `placements.json` is composed with
the trunk at z = 120 mm (the MJCF body pos, i.e. `qpos0`). At rest that cancels;
under rotation every horizontal hinge anchor sat 118–122 mm from its bearing.
`tools/fit_axis_check.py` measures this (`out/fit/axis-check.log`): after the
fix every carrying bearing is 0.02 mm off its joint axis with 0.0° tilt. The
wrong-centre sweep was discarded, not published.

### What the corrected sweep finds

54 clear-at-rest pairs start interfering somewhere in the ranges. Depth at the
used-envelope edge, or at the range end when the collision only begins beyond
the envelope:

| joint | used envelope | first structure collision | depth | verdict |
|---|---|---|---|---|
| hip roll (both) | −8/+11°, −12/+8° | none in ±22° | — | clear |
| hip pitch (both) | −46..0°, 0..32° | none in ±90° | — | clear |
| neck pitch | ±37° | none in −90..60° | — | clear |
| head yaw | ±148° | none in ±170° | — | clear |
| hip yaw (both) | −9/+6°, −4/+13° | shin into battery from ±18.1° | 4.4 mm at ±25° | outside envelope; a single-joint pose the gait never reaches |
| knee (both) | up to 75° / −80° | hip bracket into foot from 70.9° | 2.1 mm (L, 75°), 3.7 mm (R, −80°) | inside the sit/stand extreme, but only with hip pitch and ankle at zero; in the real squat all three move. Needs the sit/stand trajectory posed jointly. |
| head pitch | ±88° (crosstalk peak) | head shells into trunk shells from −66°, power support from −71° | 1.1 / 2.75 mm at −88° | the MuJoCo hull probe in head.json already said self-contact beyond −54°; exact meshes say −66°. Inside the crosstalk envelope, outside the 42° sine amplitude. |
| ankle right | −33..0° | ankle bracket into the shin servo from −0.3° | 2.5 mm at −33° | **asymmetric**: the mirrored motion on the left (0..46°) is clear. Rest census shows both shin servos seated identically, so suspect the right servo mesh's horn side or the ankle_right mesh, not the bracket. |
| ankle left | 0..46° | (−side only) | 2.9 mm at −90° | outside envelope |
| head roll | ±25° | part 29 × roll servo from −7.5° | closed-mesh check: 0.76 mm at −12.5°, 1.0 mm at −25° | within the servo-mesh overwidth (see reading 1); the bearings and shells stay clear |

Screws: 6 nominal screws enter a body they are not driven into inside the
envelope (all in the hip-yaw/knee/ankle groups); these are the withdrawn
servo-face proposals and are not graded.

### Caveats that bound these numbers

- One joint at a time from the zero pose. Coupled poses (squat, walking stance)
  are not swept; the knee finding in particular needs the recorded trajectories
  posed jointly. The MuJoCo hull probe is the only coupled evidence so far.
- Penetration is measured against Pollen's visual meshes including the 29 mm
  servo mesh; a 1 mm depth against a servo is inside that uncertainty.
- `yaw_roll_motion` pairs use the closed repaired mesh only where stated.

## Not done

`access` (driver reach) is documented in the tool and not implemented. The sweep
is single-joint from zero; coupled trajectories are not posed. No physical part was
measured. No placement, mesh or drawing was changed by this census.
