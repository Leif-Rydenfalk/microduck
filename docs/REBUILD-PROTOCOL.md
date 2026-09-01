# REBUILD PROTOCOL — how one Microduck part is rebuilt, graded and shelved

*The loop every part agent runs. Written 2026-09-01 after the first part
(`part:microduck-shin`) went FAIL 2.67 mm → PASS 1.00 mm p95 in four rounds.
Every command below was run; the numbers quoted are from those runs.*

## The setting

```bash
cd ~/dev/ce-workshop/ce-designs/microduck
export CE_TRIAD_ROOT="$PWD:$HOME/dev/ce-workshop"     # this repo first, the workshop shelf second
CAD=~/dev/ce-workshop/ce-cad/bin/cad
TRIAD=~/dev/ce-workshop/bin/triad
REF=reference/pollen-microduck-rl/assets                # the denser mesh set (reference/which-mesh-is-denser.json)
```

The reference for every custom part is Pollen's own decimated STL (metres).
`reference/pollen-microduck-simulator/assembled/measured.json` has every
mesh's bbox, the joint table and each geom's placement. SPEC.md §4 names
what each mesh is.

## 1. Measure the reference — never eyeball a number

```bash
~/dev/ce-workshop/ce-cad/bin/cad-mjcf sections $REF/<mesh>.stl --axis z --n 20 --metres   # widths along an axis
```

```python
# FreeCAD's python has numpy: /Applications/FreeCAD.app/Contents/Resources/bin/python
import sys; sys.path.insert(0, '/Users/leifrydenfalk/dev/ce-workshop/ce-cad')
from cecad import meshfeatures, meshview, mjcf
r = meshfeatures.cylinders('reference/pollen-microduck-rl/assets/<mesh>.stl', scale=1000)
for h in r['holes'] + r['bosses']: print(h)          # Ø, axis, centre, length, coverage
meshview.render_stl('...<mesh>.stl', 'out/ref_<mesh>_iso.png', view='iso', scale=1000, edge=True)
```

For the fine structure (ribs, walls, steps) cut planes and list the
material intervals — the shin's 1 mm rim walls and its 2.3/2.8 mm stepped
plate were only visible that way. Since the thigh (2026-09-01) that is a
cecad module, `cecad.meshslice` (kernel-free, FreeCAD's python):

```python
from cecad import meshslice
T = meshslice.load('reference/pollen-microduck-rl/assets/<mesh>.stl', 1000)
meshslice.intervals(T, 'x', 2.0, 0.0)     # material along x at (y,z)=(2,0): [(64.7, 68.0)]
meshslice.segments(T, 'z', 20.0)          # the plane cut as (M,2,2) segments
meshslice.render(T, 'out/measure/<mesh>_slices_z.png', 'z', [-10, 0, 10, 20, 30, 40])
```

`render` draws a sheet of cuts on a 1 mm grid — read it with the Read
tool; `intervals` is the caliper: a 1 mm wall, a stepped boss, a
counterbore floor and a drafted face all fall out as numbers with the
probe line that produced them (the thigh's part.py quotes them by probe
letter). Read the renders
with the Read tool: a number you cannot see in the picture is a number to
re-measure.

## 2. The folder

```bash
$TRIAD new part microduck-<slug>          # skeleton at v0.0.1, born T0
```

Write `iterations/v0.0.1/cad/part.py`: `def build(doc, params=None) -> Part`,
imports only `cecad` + stdlib, **every driving number in a parameter block
with the measurement it came from in a comment**. Model in **Pollen's mesh
frame** (the STL's own coordinates, mm) — then the MJCF geom `pos`/`quat`
place the part in the assembly with no re-derivation and refcheck needs no
alignment. Copy the shin's shape: `ce-parts/microduck-shin/current/cad/part.py`.

cecad primitives for these parts: `box cyl cone sphere prism revolve torus`
and, added for this project, `ellipsoid loft shell scale from_mesh`
(`cecad/core.py`). A loft with an apex cannot be `shell()`ed — end it with a
small cap, or cut an explicit inner loft. Holes: `cyl(..., op="cut")` with
the measured diameter; fastener sizes through `M("M2")`.

## 3. Build → grade → look → fix — one command

```bash
~/dev/ce-workshop/ce-cad/bin/cad-refcheck part:microduck-<slug> --ref $REF/<mesh>.stl --out out/refcheck/<slug>/r1
```

It builds through `bin/cad`, runs `cecad.meshcompare` (p95 surface distance
both ways, bbox, volume), matches every reference hole/boss to yours
(axis, ≤ 0.5 mm, ≤ 0.15 mm Ø) and writes overlay renders. **Read
`report.md` and LOOK at `overlay_iso.png` / `overlay_front.png`** (orange =
yours, grey = theirs). The unmatched-feature lines and the overlay tell you
what to fix. Iterate r2, r3 … until:

**PASS = p95 ≤ 1.0 mm both ways AND bbox within 1.5 mm per axis AND 0
unmatched reference features.** (1.0 mm is the decimation floor of their
export; do not loosen it.)

Shin history, for calibration: r1 2.67 mm (recess where a disc belonged),
r2 1.33 (rib found), r3 1.10 (stepped face + ring), r4 **1.00 PASS**,
median 0.001 mm, 20/20 features.

## 4. Evidence and identity

```bash
~/dev/ce-workshop/ce-cad/bin/cad-refcheck part:microduck-<slug> --ref $REF/<mesh>.stl --evidence   # -> evidence/refcheck/<stamp>/ + ledger row
$TRIAD trust part:microduck-<slug>                                                                   # T1 simulated
$TRIAD check part:microduck-<slug>                                                                   # exit 0
```

Then fill, by hand and with sources:
- `component.json` `record`: title, verdict/why (quote the refcheck
  numbers), sector, material `PLA` (or `TPU` for jaw_soft / soft_mouth_top
  / soles), process `FDM`, `origin: "generated"` + `origin_why`,
  `source_reference` (the mesh), `qty_per_robot`, `why_this_folder_exists`.
- `cad/interfaces.json`: one interface per place another part joins —
  frame (origin, z_axis, x_axis) in the part's frame, `accepts:
  ["connection:<slug>"]`, `what`, `source: "MEASURED …"`. Connection kinds
  on this shelf so far: `spline-xl330-horn`, `press-fit-bearing-15x10x3`,
  and the workshop's `threaded-m3` (we need `threaded-m2` — say so in
  `accepts` and it will be created; a dangling ref is a FAIL that names
  the work).
- `mech/mech.py`: numbers with sources or `None` with the reason.
- `docs/README.md`: what it is, what was measured how, what is still
  CANNOT DETERMINE (e.g. wall thickness their decimation hid).

## 5. Report

Return: slug, PASS/FAIL with the four numbers (p95 ref→ours, ours→ref,
bbox delta, features matched/total), rounds taken, the refcheck folder
path, the interfaces you declared, and anything you could not settle
(named, with what would settle it). Never report a part done without the
PASS line from `cad-refcheck`.

## Rules that bind

- Measure, never assert; a number without its source line is a defect.
- Three verdicts. CANNOT DETERMINE is written down, not rounded to PASS.
- Never loosen `--tol` to pass. Fix the geometry.
- Out-dirs are committed. Leave `out/refcheck/<slug>/` in place.
- Improve the tools when they fall short (P11): a missing primitive or a
  refcheck blind spot is part of the task — add it to `ce-cad/cecad/`
  with a docstring that names the measurement, and say so in the report.
