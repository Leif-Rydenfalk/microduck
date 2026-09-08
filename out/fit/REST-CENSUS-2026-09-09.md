# Rest-pose interference census — 2026-09-09

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

## Not done

`sweep` (joint-range) and `access` (driver reach) stages are documented in the
tool and not implemented; only the zero pose is measured. No physical part was
measured. No placement, mesh or drawing was changed by this census.
