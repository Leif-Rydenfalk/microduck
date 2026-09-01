# reference/pollen-microduck-simulator — Pollen's own robot description

Copied 2026-09-01 from the Hugging Face space
`pollen-robotics/microduck-simulator` at commit (see SOURCE-COMMIT.txt),
path `app/public/robot/mjlab/`. The STL meshes and `microduck.glb` were
git-LFS pointers in the clone; the objects were fetched from
`https://huggingface.co/spaces/pollen-robotics/microduck-simulator/resolve/main/…`.

| file | what |
|---|---|
| `robot_allcollisions.xml` | MJCF, "Generated using onshape-to-robot" from Onshape document `804927696f06d877f3f1803e` (not publicly readable without a key — measured: API 403 anonymous, 2026-09-01) |
| `robot_allcollisions_rollers.xml` | the wheeled variant (rim / tire / roller_blade meshes) |
| `kinematics.json`, `kinematics_rollers.json` | the same tree as the simulator's three.js rig reads it |
| `meshes/*.stl` | 44 decimated visual meshes, METRES |
| `microduck.glb` | the whole robot as one GLB |
| `assembled/` | OUR OUTPUT from `ce-cad/bin/cad-mjcf assemble`: world-frame STL per body + whole robot in MILLIMETRES, `measured.json` (joint table, mesh stats, envelope), `ref_*.png` renders from `cecad.meshview` |

Licence: the simulator README does not state one for the assets; the
microduck_rl repo it cites is Apache-2.0 for code and the community reports
the sim assets as CC BY-SA-NC (research/01-product-and-specs.md §14). Used
here as reference material for a reverse-engineering study; nothing in this
folder is redistributed as our own work.
