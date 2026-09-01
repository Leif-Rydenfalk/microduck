# TOOLCHAIN — what this repo needs to reproduce every file in it

*Leif, 2026-09-01: "add all screenshots and everything to the git repo this
should be everything anyone needs to reproduce this design."* This repo holds
the DESIGN and its evidence. The TOOLS that build and grade it are ce-cad,
which is proprietary (Leif Rydenfalk, all rights reserved) and lives in the
ce-workshop monorepo — deliberately NOT vendored here. What is pinned:

| component | version | where |
|---|---|---|
| ce-workshop (ce-cad + bin/triad) | commit `65042d5` or later on `main` (github.com/Leif-Rydenfalk/ce-workshop, private) | `~/dev/ce-workshop` |
| FreeCAD (the geometry kernel ce-cad drives) | 1.1.3, `/Applications/FreeCAD.app` (its bundled python has numpy 1.26.4 + matplotlib 3.10.8) | `bin/cad --doctor` |
| python for kernel-free tools | FreeCAD's `Contents/Resources/bin/python` (system python3 3.14 has no numpy) | |
| ce-cad modules written for this project | `cecad/mjcf.py`, `meshview.py`, `meshcompare.py`, `meshfeatures.py`, `meshslice.py`, `mjcfseed.py`; `bin/cad-mjcf`, `bin/cad-refcheck`; `Part.ellipsoid/loft/shell/scale/from_mesh` | ce-workshop `a9cca94`..`65042d5` |
| reference data | Pollen's MJCF + meshes, copied into `reference/` with SOURCE-COMMIT.txt | this repo |

Environment for every command in this repo:

```bash
export CE_TRIAD_ROOT="$HOME/dev/ce-workshop/ce-designs/microduck:$HOME/dev/ce-workshop"
```

`tools/` holds only scripts that belong to THIS design (the PASS watcher, the
whole-duck render); anything reusable is promoted into ce-cad and cited above.
