# microduck simulation report

Generated 2026-09-02T00:24:16. Pollen's MJCF (`reference/pollen-microduck-rl/robot_walk.xml`, `robot_allcollisions.xml`) driven by Pollen's published ONNX policies in MuJoCo 3.12.0 at 50 Hz (timestep 0.005 s, decimation 4), the loop of `microduck_rl/scripts/infer_policy.py` and the browser simulator's `game.js`. Renderer: mujoco.Renderer (offscreen, MUJOCO_GL=glfw).

## Swapped meshes (9) — OUR rebuilt parts drawn in orange

| mesh | part | source | refcheck p95 mm (ref->ours, ours->ref) |
|---|---|---|---|
| banana_pcb_locker | part:microduck-banana-pcb-locker | `out/refcheck/microduck-banana-pcb-locker/verify/ours.stl` | [0.013, 0.0125] |
| bearing_roll | part:microduck-bearing-roll | `ce-parts/microduck-bearing-roll/iterations/v0.0.1/evidence/refcheck/2026-09-01T16-15-38Z/ours.stl` | [0.0017, 0.0018] |
| leg | part:microduck-shin | `ce-parts/microduck-shin/iterations/v0.0.1/evidence/refcheck/2026-09-01T14-05-50Z/ours.stl` | [1.0, 1.0] |
| power_support | part:microduck-power-support | `out/refcheck/microduck-power-support/verify/ours.stl` | [0.2133, 0.2281] |
| trunk_base | part:microduck-trunk-base | `out/refcheck/microduck-trunk-base/verify/ours.stl` | [0.0005, 0.0008] |
| upper_leg_left | part:microduck-upper-leg-left | `ce-parts/microduck-upper-leg-left/iterations/v0.0.1/evidence/refcheck/2026-09-01T14-56-45Z/ours.stl` | [0.2, 0.2] |
| upper_leg_right | part:microduck-upper-leg-right | `ce-parts/microduck-upper-leg-right/iterations/v0.0.1/evidence/refcheck/2026-09-01T15-14-32Z/ours.stl` | [0.2, 0.2] |
| upper_leg_rigidity_plate | part:microduck-upper-leg-rigidity-plate | `out/refcheck/microduck-upper-leg-rigidity-plate/r1/ours.stl` | [0.2562, 0.279] |
| yaw2roll | part:microduck-yaw2roll | `ce-parts/microduck-yaw2roll/iterations/v0.0.1/evidence/refcheck/2026-09-01T16-15-15Z/ours.stl` | [0.05, 0.05] |

Only geoms of class `visual` are re-pointed. stock (only class=visual geoms re-pointed); stock (explicit <inertial> per body, asserted equal). Zero-pose world bbox of every re-pointed geom vs stock: ours worst 0.504 mm (tol 1.5, PASS), ours_allcollisions worst 0.504 mm (tol 1.5, PASS).

## Videos

| file | trajectory | frames | fps | seconds | size | renderer |
|---|---|---|---|---|---|---|
| `out/sim/walk.mp4` | out/sim/walk_ours_traj.npz | 81 | 10.0 | 8.1 | 1468 kB | mujoco.Renderer (offscreen, MUJOCO_GL=glfw) |
| `out/sim/walk.gif` | out/sim/walk_ours_traj.npz | 81 | 10.0 | 8.1 | 4089 kB | mujoco.Renderer (offscreen, MUJOCO_GL=glfw) |
| `out/sim/sitstand.mp4` | out/sim/sitstand_ours_traj.npz | 81 | 10.0 | 8.1 | 872 kB | mujoco.Renderer (offscreen, MUJOCO_GL=glfw) |
| `out/sim/stand.mp4` | out/sim/stand_from_sit_ours_traj.npz | 61 | 10.0 | 6.1 | 439 kB | mujoco.Renderer (offscreen, MUJOCO_GL=glfw) |
| `out/sim/walk_stock.mp4` | out/sim/walk_stock_traj.npz | 81 | 10.0 | 8.1 | 1380 kB | mujoco.Renderer (offscreen, MUJOCO_GL=glfw) |

## Runs (every number measured off the simulation state)

| run | policy | robot | s | command | walked m | speed m/s | trunk z min/end m | max tilt deg | fell (rule) | fell outside commanded ground window | max joint speed rad/s | joints within 1 deg of limit | beyond limit | contacts mean/max | self-contacts max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sitstand_ours | sitstand | ours_allcollisions (STAND) | 8 | sit 1.0-4.5 s | 0.028 | 0.004 | 0.059 / 0.116 | 5.2 | True | False | 12.75 (right_knee) | none | none | 4.2 / 6 | 0 |
| sitstand_stock | sitstand | allcollisions (STAND) | 8 | sit 1.0-4.5 s | 0.028 | 0.004 | 0.059 / 0.116 | 5.2 | True | False | 12.75 (right_knee) | none | none | 4.2 / 6 | 0 |
| stand_from_fold_ours | stand | ours_allcollisions (FOLD) | 6 | all zero | 0.052 | 0.009 | 0.057 / 0.116 | 6.2 | True | False | 14.20 (right_hip_pitch) | left_hip_pitch, left_knee, right_hip_pitch, right_knee | none | 4.3 / 6 | 0 |
| stand_from_sit_ours | stand | ours_allcollisions (SIT) | 6 | all zero | 0.038 | 0.006 | 0.067 / 0.116 | 5.0 | False | False | 14.85 (right_ankle) | head_pitch | head_pitch | 4.4 / 6 | 0 |
| stand_hold_ours | stand | ours_allcollisions (STAND) | 4 | all zero | 0.003 | 0.001 | 0.115 / 0.116 | 1.4 | False | False | 1.11 (right_knee) | none | none | 4.9 / 6 | 0 |
| walk_ours | walking | ours (STAND) | 8 | vx 0.25 | 0.792 | 0.105 | 0.114 / 0.116 | 4.1 | False | False | 5.74 (left_knee) | none | none | 1.9 / 6 | 0 |
| walk_ours_vx0.15 | walking | ours (STAND) | 8 | vx 0.15 | 0.008 | 0.001 | 0.115 / 0.115 | 0.6 | False | False | 0.70 (left_hip_pitch) | none | none | 4.0 / 6 | 0 |
| walk_stock | walking | walk (STAND) | 8 | vx 0.25 | 0.792 | 0.105 | 0.114 / 0.116 | 4.1 | False | False | 5.74 (left_knee) | none | none | 1.9 / 6 | 0 |
| walk_stock_vx0.15 | walking | walk (STAND) | 8 | vx 0.15 | 0.008 | 0.001 | 0.115 / 0.115 | 0.6 | False | False | 0.70 (left_hip_pitch) | none | none | 4.0 / 6 | 0 |

Fall rule: trunk z < 0.06 m or |roll|,|pitch| > 60 deg. For sitstand and stand-from-SIT/FOLD the trunk is put below 0.06 m on purpose (the commanded sit, the start pose); `fell outside commanded ground window` applies the rule outside those windows.

## Stock vs ours

- **walk_ours_vs_walk_stock**: walked [0.7925, 0.7925] m, fell [False, False], max tilt [4.11, 4.11] deg, self-contacts max [0, 0], contacts mean [1.92, 1.92] — identical trajectory: True
- **walk_ours_vx0.15_vs_walk_stock_vx0.15**: walked [0.0077, 0.0077] m, fell [False, False], max tilt [0.57, 0.57] deg, self-contacts max [0, 0], contacts mean [3.98, 3.98] — identical trajectory: True
- **sitstand_ours_vs_sitstand_stock**: walked [0.0277, 0.0277] m, fell [True, True], max tilt [5.17, 5.17] deg, self-contacts max [0, 0], contacts mean [4.22, 4.22] — identical trajectory: True

The swap changes only what is drawn: collision geoms, inertials and actuators are Pollen's, so the physics is bit-identical (checked above by comparing the recorded qpos arrays). Self-collision growth vs stock: none (0 vs 0).

## Joint range use (walk_ours)

| joint | range rad | min | max | % of range used | frames within 1 deg of a limit | max |qdot| rad/s |
|---|---|---|---|---|---|---|
| left_hip_yaw | [-0.436, 0.524] | -0.143 | 0.005 | 15.4 | 0 | 0.91 |
| left_hip_roll | [-0.384, 0.384] | -0.137 | 0.047 | 23.9 | 0 | 1.80 |
| left_hip_pitch | [-1.571, 1.571] | -0.482 | -0.203 | 8.9 | 0 | 2.69 |
| left_knee | [-1.571, 1.571] | -0.257 | 0.386 | 20.5 | 0 | 5.74 |
| left_ankle | [-1.571, 1.571] | 0.139 | 0.481 | 10.9 | 0 | 3.17 |
| neck_pitch | [-1.571, 1.047] | 0.213 | 0.349 | 5.2 | 0 | 0.82 |
| head_pitch | [-1.571, 1.571] | 0.349 | 0.428 | 2.5 | 0 | 0.40 |
| head_yaw | [-2.967, 2.967] | -0.074 | 0.123 | 3.3 | 0 | 1.66 |
| head_roll | [-0.436, 0.436] | -0.092 | 0.010 | 11.7 | 0 | 0.99 |
| right_hip_yaw | [-0.524, 0.436] | 0.000 | 0.106 | 11.0 | 0 | 0.56 |
| right_hip_roll | [-0.384, 0.384] | 0.006 | 0.138 | 17.3 | 0 | 1.64 |
| right_hip_pitch | [-1.571, 1.571] | 0.190 | 0.481 | 9.3 | 0 | 3.32 |
| right_knee | [-1.571, 1.571] | -0.349 | 0.166 | 16.4 | 0 | 4.99 |
| right_ankle | [-1.571, 1.571] | -0.482 | -0.215 | 8.5 | 0 | 2.04 |

## Notes

- The requested 0.15 m/s forward command sits inside the walking policy's stand-still band: measured 0.008 m in 8 s at vx 0.15 (and 0.011 m at 0.20), 0.79 m at vx 0.25 — the browser simulator's `VEL_FWD`. The videos use 0.25.
- Achieved speed under-tracks the command (0.25 commanded, ~0.10 m/s achieved over the commanded window): the MJCF position actuators (kp 0.55, force +/-0.96 N m) stand in for the BAM actuator model the policy was trained with; infer_policy.py runs the same actuators.
- `yaw_roll_motion.stl` was missing from `reference/pollen-microduck-rl/assets/` (robot_walk.xml references it); restored byte-for-byte from the upstream microduck_rl clone (sha256 41149f07...3dc7). The other 46 assets are byte-identical to upstream.
- Sit/stand and get-up runs use `robot_allcollisions.xml` (trunk/head/shell collision geoms), as infer_policy.py's scene.xml and game.js do; walking uses `robot_walk.xml`.
