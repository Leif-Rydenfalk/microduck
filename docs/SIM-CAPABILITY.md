# Simulation capability — measured against SolidWorks

Every number in section 1 marked **measured** was produced by running the tool on
this Mac (8-core, macOS) on 2026-09-02; **cited** numbers name the file or URL they
come from. Toolchain state as measured today: `cargo 1.97.1` on PATH; `gmsh` and
`ccx` NOT on PATH but found at runtime inside FreeCAD.app (proven working by the
passing FEA runs below); MuJoCo 3.12.0 + onnxruntime 1.29.0 in FreeCAD's python;
`MUJOCO_GL=glfw` offscreen rendering works.

## 1. Feature matrix — our stack vs the SolidWorks feature set

Column key: ce-cad = `~/dev/ce-workshop/ce-cad` (FreeCAD/OCC kernel, Python),
ce-struct = voxel FEA + CalculiX, ce-motion = torque/margin studies,
MuJoCo lane = `ce-designs/microduck/sim/`.

### 1.1 CAD core (SolidWorks Standard)

| SolidWorks feature | ours | evidence |
|---|---|---|
| Parametric solid modeling | YES, code-parametric (Python over the OCC kernel), no sketch UI | **measured**: `examples/nema_mount/design.py` — bracket + NEMA17 + 4 stock screws, build + 9-check verification in 5.3 s (6.8 s wall) |
| Assemblies with mates | YES — declared connectors, `mate()`/`fasten()`/`connect()`, standard interfaces (NEMA faces, ISO screws); a wrong-size mate is REFUSED with the number | **measured**: same nema_mount run prints per-bolt engagement (M3x10 through 6 mm, 4 mm engaged); joint models spec'd in `ce-cad/CLAUDE.md` §Connections |
| Engineering drawings | YES — third-angle views, sections, hole tables, title block, DXF+SVG, and every dimension is READ BACK against the solid | **measured**: `examples/blueprints/make.py` — 3 real parts to verified sheets in 57.0 s wall; 40/40 read-back checks agree with the solid |
| Interactive sketching / feature tree UI | NO — everything is a script; the browser viewer is view + transport + physics-poke only | by design; nearest equivalent is re-running the script (5–60 s, above) |
| Configurations / design tables | PARTIAL — parameters are Python variables; sweeps are shell loops; no configuration manager | `ce-struct` `--set bodies.0.material=PETG` style overrides exist per study |
| CAM / toolpaths | NO — `cecad/machining.py` + `dfm.py` judge manufacturability and cost, they do not emit G-code. 3D-print plating exists (cad-print skill) | cited: `ce-cad/CLAUDE.md` §Manufacturing, §DFM |
| PDM / versioning | PARTIAL — git + a published catalog; known gap: nothing auto-retracts a stale catalog entry | cited: `ce-cad/CLAUDE.md` §KNOWN BROKEN (19 stale `atech_actuator_*` entries measured 2026-08-13) |
| Electrical/PCB | YES beyond SolidWorks Standard — `cecad/electrical.py`, `pins.py`, `pcb.py`, voltage drop over the measured loom | cited: `ce-cad/CLAUDE.md` §Electrical/§PCB |

### 1.2 Motion (SolidWorks Motion)

| SolidWorks Motion does | ours | evidence |
|---|---|---|
| Kinematic mechanism solve | YES — Newton on C(q)=0 from the assembly's own declared joints, verified against closed forms only (never solver-vs-solver) | **measured**: `cecad.physics.self_test()` 28 checks ALL PASSED, 23.5 s wall; scotch yoke vs x=r·cos t to 4.6e-14 mm; leadscrew vs lead/360·turns to 0.0 mm |
| Rigid-body dynamics (forces, springs, gravity) | PARTIAL — ONE integrated coordinate (the driver); springs/gravity/stops reflected through the real mechanism; mass/COM/inertia measured off the solids; a doc with no measured inertia REFUSES to tick | **measured**: `tests/test_dynamics.py` 11/11 passed (69.3 s wall incl. builds); pendulum period to 0.18% of 2π√(J/mgd) (cited, CLAUDE.md §97) |
| Real-time interactive dynamics | YES, and SolidWorks does not have this — the Rust kernel (`kernel/src/dynamics.rs`) ticks live in the viewer and from Python | **measured**: 10.05 µs/tick over 10,000 ticks on `rotary_pointer.mech.json` = 99.5x real time at dt=1 ms; viewer live solve worst 0.17 ms/frame (cited, CLAUDE.md §96) |
| 3D contact between bodies | NO contact solver — a pin leaves its slot by declared `pin_slot`/`dwell_lock` regimes, not by collision response. MuJoCo covers this (below) | cited: CLAUDE.md §97 "no contact solver"; §pin_slot |
| Friction | NO — viscous `damping` only, no Coulomb friction | cited: CLAUDE.md §97 |
| Spatial (3D) linkages solved live | PARTIAL — planar mechanisms solve live; trains and spatial linkages fall back to the baked (pre-checked) track, and the transport badge says which you are watching | cited: CLAUDE.md §96 |
| Event-based motion, motor curves | PARTIAL — motor torque is a DECLARED number (`motion={"torque_Nmm": ...}`); deriving it from chip data is an open item. ce-motion does torque budgets/actuator margins from part-folder facts | cited: CLAUDE.md §97; `ce-motion/README.md` |
| Full mechanism audit | YES — `bin/connections`, collision sweep, mobility, loop closure; refusals are verdicts | **measured**: `examples/kinetic_totem/motion.py --quick` 81.4 s wall — 17 checks passed, 1 CANNOT DETERMINE (the example declares no keep-out zones, so keepout refuses rather than passes; the parent gate correctly BLOCKS on it) |

### 1.3 FEA (SolidWorks Simulation Standard/Professional/Premium)

| SolidWorks study | ours | evidence |
|---|---|---|
| Linear static | YES, twice, in two independent codebases that cross-check: ce-cad (gmsh quadratic tets + CalculiX) and ce-struct (own hex8 voxel solver + CalculiX) | **measured**: `cecad.stress.self_test()` 26/26 in 13.3 s (tension bar 99.999 vs 100.000 MPa closed form); `ce-struct bin/struct bracket` 7,080 cells, PASS SF 5.74, 1.57 s wall. Cited: the two lanes agree on stiffness to 0.052%, differ 13.9% on singular peak stress (ce-cad CLAUDE.md §Stress, measured 2026-08-30) |
| Frequency (modal) | YES — ce-struct modal study via CalculiX | cited: proven vs cantilever f₁ to 0.40%, mode ratio 0.33% (`ce-struct/README.md`, part of the 612-check `npm test`, measured 2026-08-30) |
| Buckling | YES — ce-struct via CalculiX | **measured**: `bin/struct bracket --study buckle` PASS, folds at 108.71x, 6.0 s wall; cited: Euler closed form to 0.41% |
| Nonlinear (plasticity, large deformation) | YES in ce-struct only — yield study with hardening curve + NLGEOM; ce-cad's lane is strictly linear/static/isotropic/one-part | cited: hardening curve reproduced to 0.00%; NLGEOM changes plastic strain 3.5x on the necking bar (`ce-struct/README.md`) |
| Contact | PARTIAL — ce-struct's contact study (separation/sliding via CalculiX, proven to 0.06% + zero-tension check); ce-cad has none | cited: `ce-struct/README.md` five studies table |
| Thermal | NO — CalculiX can, nothing here drives it | gap |
| Fatigue | NO | gap |
| Drop test / explicit dynamics | NO — OpenRadioss is named in ce-struct's survey, not wired | gap; cited `ce-struct/README.md` |
| CFD (Flow Simulation) | NO (ce-fluid exists in the workshop but is not part of this measured lane) | gap |
| Linear dynamic (transient/harmonic/random vibration) | NO | gap |
| Multi-part assembly FEA | NO in ce-cad (one part at a time); ce-struct takes multi-body studies with contact | cited: ce-cad CLAUDE.md §Stress "What it is NOT" |
| Printed-material anisotropy | AHEAD of SolidWorks defaults — ce-struct REQUIRES `printNormal`, transversely isotropic deformation + separate failure allowables; refuses a guess | cited: `ce-struct/README.md` §Materials |

SolidWorks study list used for comparison: [GoEngineer package comparison](https://www.goengineer.com/blog/comparing-all-solidworks-simulation-packages-basic-to-advanced), [MLC-CAD study-type overview](https://www.mlc-cad.com/resources/solidworks/overview-of-solidworks-simulation-study-types/), [solidworks.com Simulation](https://www.solidworks.com/product/solidworks-simulation).

### 1.4 What actually runs in real time (SolidWorks: nothing in this class)

| lane | measured rate | real-time factor |
|---|---|---|
| Rust kernel live tick (single mechanism, 1 coordinate) | 10.05 µs/tick (10,000-tick bench) | **99.5x** real time at dt=1 ms; also runs as wasm in the browser viewer |
| Viewer live kinematic solve | worst 0.17 ms/frame over 241 frames, 8 machines (cited, CLAUDE.md §96) | comfortably 60 fps |
| MuJoCo, microduck, pure physics (`mj_step`, dt=5 ms, full contact) | 33.8 µs/step (2,000-step bench) | **148x** real time |
| MuJoCo + ONNX policy at 50 Hz (the real control stack's loop shape) | 10 s walk in 0.13 s loop wall (1.08 s process wall incl. model+policy load); walked 1.0045 m at vx 0.25, did not fall | **~77x** real time |
| ce-struct in-tab static solve | 1.57 s for 7,080 cells (re-solves while a slider moves) | interactive, not real-time physics |

### 1.5 Testing microduck's REAL software against simulation (the Isaac Sim question)

| layer | state today | evidence |
|---|---|---|
| The shipped ONNX policies in physics | YES — `sim/run_policy.py` reproduces the 50 Hz obs/action loop of `infer_policy.py` and the browser sim, on Pollen's MJCF with OUR meshes swapped in (collision geoms + inertials stay stock, qpos verified bit-identical stock-vs-ours) | **measured**: `out/sim/report.md` — 9 standard runs; walk 0.79 m/8 s at vx 0.25; stand-still band ends between 0.20 and 0.25 m/s |
| The real Rust daemons (robotd et al.) in the loop | NO physics-in-the-loop bridge exists. What exists: `duck-control`'s `RobotIo` trait with a `FakeIo` backend (`--fake`) — the daemon runs without hardware, against CANNED sensors, not simulated dynamics | read from the clone: `duck-control/src/io.rs` (`pub trait RobotIo`, `FakeIo`, "simulated failure" error) |
| The robot's kinematics code vs physics ground truth | YES — Pollen's own Rust FK crate is tested against MuJoCo's `mj_kinematics` on 64 random poses to 1e-6 m | read: `kinematics/tests/fk_against_mujoco.rs` |
| What a robotd↔MuJoCo bridge would need | a `RobotIo` impl that answers `sync_read` (15 servos + the id-200 IMU register block) from `mj_step` state and applies goal positions as `data.ctrl` — the trait seam already exists; the work is the Dynamixel register model + real-time pacing | gap, not measured |
| Isaac Sim's actual add | GPU-parallel RL at scale (thousands of concurrent envs), RTX sensor simulation (camera/depth/lidar/radar, segmentation, synthetic data), USD scenes, ROS 2 integration | cited: [NVIDIA Isaac Sim paper (arXiv 2606.03551)](https://arxiv.org/html/2606.03551v1), [Isaac Lab](https://github.com/isaac-sim/IsaacLab), [NVIDIA/HF state of simulation](https://huggingface.co/blog/nvidia/state-of-simulation-for-physical-ai). None of that is needed to RUN Pollen's already-trained policies (measured above at 77x real time on CPU); it becomes relevant if we TRAIN policies or need camera/lidar sensor realism |

## 2. Is it like SolidWorks?

No — it is not feature-parity with SolidWorks, and it is not trying to be the
same shape of tool. Where we are behind: there is no interactive sketch/feature
UI at all (every part is a script and a rebuild costs 5–60 s, measured above);
motion has no contact solver, no Coulomb friction, and integrates one coordinate,
where SolidWorks Motion does full 3D rigid-body contact; FEA has no thermal,
fatigue, drop-test, linear-dynamic or CFD lane, and ce-cad's own FEA is
linear-static one-part-at-a-time (nonlinear plasticity, buckling, modal and
contact live only in ce-struct); there is no CAM and no real PDM. Where we are
ahead of SolidWorks: everything is scriptable and git-diffable, so an agent can
build, verify and sweep designs unattended; evidence discipline — every solver is
proven against closed forms it did not compute, drawings are read back against
the solid (40/40 checks, measured), and a missing fact is a named CANNOT
DETERMINE rather than a silent pass (the totem run above blocks its own gate for
an undeclared keep-out); real-time — the Rust kernel ticks a live mechanism at
~100x real time and MuJoCo runs the microduck's actual shipped ONNX policies with
full contact at ~77–148x real time on this 8-core CPU, a software-in-the-loop
lane SolidWorks simply does not have. On the Isaac Sim question: we already do
the part of Isaac Sim that matters for microduck today — physics-accurate
policy-in-the-loop simulation on our own rebuilt geometry — but only at the
policy level; the real Rust daemons (robotd) can run hardware-free against a
FakeIo stub, not against physics, and closing that gap is a bounded piece of work
(a `RobotIo` impl backed by `mj_step`), while Isaac Sim's genuine additions —
GPU-parallel training, RTX camera/lidar rendering, ROS 2 — are things nothing in
this stack provides.
