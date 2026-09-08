# sim — the Microduck walking, sitting and standing in MuJoCo, with OUR parts on it

Pollen's stock MJCF (`reference/pollen-microduck-rl/robot_walk.xml`,
`robot_allcollisions.xml`) driven by Pollen's own published ONNX policies
(`BEST_alpha_walking`, `BEST_alpha_sitstand`, `BEST_alpha_stand`) in MuJoCo,
reproducing the 50 Hz loop of `microduck_rl/scripts/infer_policy.py` and the
browser simulator's `game.js`, with every PASSed rebuilt part's mesh swapped in
for Pollen's. Every number in `out/sim/report.md` is read off the simulation.

## Run it (three commands)

```bash
PY=/Applications/FreeCAD.app/Contents/Resources/bin/python   # has mujoco 3.12, onnxruntime 1.29, imageio(-ffmpeg)
$PY sim/swap_meshes.py        # sim/microduck_ours*.xml: OUR meshes for every PASSed part; compiles + bbox check (exit 0)
$PY sim/run_policy.py --all   # 9 runs: walk (stock, ours; vx 0.25 and 0.15), sitstand (stock, ours), stand (hold / from SIT / from FOLD)
$PY sim/render_video.py --all # out/sim/walk.mp4 + walk.gif, sitstand.mp4, stand.mp4, walk_stock.mp4, frames/*.png, report.json + report.md
```

The system `python3` has none of the toolchain; use FreeCAD's python for all
three. `sim/policies/*.onnx` are the browser simulator's files (fetched from
the Hugging Face space; sha256 equal to the git-lfs pointers in the clone).

## What each script does

| script | in | out |
|---|---|---|
| `swap_meshes.py` | `tools/watch-pass.log` (PASSed slugs), `spec/mesh-to-part.json` (mesh -> part), the newest PASS refcheck `report.json` + `ours.stl` per part | `sim/meshes_ours/<mesh>.stl` (binary STL, mm), `sim/microduck_ours.xml`, `sim/microduck_ours_allcollisions.xml`, `out/sim/swap_report.json`. Only geoms of class `visual` are re-pointed (asset `<mesh>__ours`, scale 0.001); collision geoms and every `<inertial>` stay Pollen's, so the physics is the stock physics. Fails unless both models compile and every re-pointed geom's zero-pose world bbox is within 1.5 mm of the stock geom. |
| `run_policy.py` | a robot (`walk` / `allcollisions` / `ours` / `ours_allcollisions` / a path), a policy, a command | `out/sim/<name>_traj.npz` (qpos, qvel, ctrl, action, obs, cmd, contacts per 50 Hz frame) + `<name>_summary.json` (walked distance, speed, min trunk height, max tilt, fell rule `trunk z < 0.06 m or |roll|,|pitch| > 60 deg`, joint range hits vs the MJCF limits, contact counts, max joint speed). `--all` runs the standard nine. |
| `render_video.py` | a `_traj.npz` | 640x480 frames at 10 fps through `mujoco.Renderer` offscreen (`MUJOCO_GL=glfw` works on this Mac); falls back to `cecad.meshview` (software z-buffer, bodies placed from qpos via `mj_forward`) when no GL context can be made. Encodes mp4 (libx264 via imageio-ffmpeg) and the README GIF (<= 8 MB), reads every video back frame-wise and refuses blank or frozen frames, writes three PNGs per run to `out/sim/frames/`, then `report.json` / `report.md`. |
| `common.py` | — | the constants both scripts share (joint order, DEFAULT_POSE, the STAND/INIT/SIT/FOLD keyframes, timestep 0.005 x decimation 4) and `scene_xml()` which wraps a robot file with a floor, light and keyframes the way Pollen's `scene.xml` does. |

## The loop, and where it comes from

- obs (61) = `[gyro 3 | projected gravity 3 | q - DEFAULT_POSE 14 | qdot 14 | last action 14 | command 13]` — `infer_policy.py get_observations()` and `game.js buildObs()`; the ONNX metadata names the same blocks (`observation_names`).
- action (14) -> `ctrl = DEFAULT_POSE + action * action_scale` (1.0, from the ONNX metadata), then 4 x `mj_step` at 0.005 s = 50 Hz.
- command slots: `[vx vy wz | neck_pitch head_pitch head_yaw head_roll | body x y z roll pitch yaw]`; the sitstand policy uses slot 0 as the sit flag (1 = sit) and is held standing for a moment before the sit is commanded, as `game.js` does; the head slots are EMA-smoothed (alpha 0.2) like the runtime.
- start pose: the STAND keyframe (`0 0 0.12 1 0 0 0` + DEFAULT_POSE), injected as `game.js` injects it.

## Measured (2026-09-02, see `out/sim/report.md`)

- The walking policy's stand-still band ends between 0.20 and 0.25 m/s: walked in 8 s at vx 0.15 = 0.008 m, 0.20 = 0.011 m, 0.25 = 0.79 m, 0.40 = 1.28 m (`out/sim/vx_sweep.json`). The videos use 0.25, the browser simulator's `VEL_FWD`.
- Stock vs ours: identical qpos arrays for every paired run (the swap draws different meshes on the same collision geoms and inertials). Self-contacts: 0 in both.
- The `fell` rule fires on the sitstand and stand-from-FOLD rows only where the trunk is put on the floor on purpose (the commanded sit, the folded start pose); outside those windows nothing fell.
