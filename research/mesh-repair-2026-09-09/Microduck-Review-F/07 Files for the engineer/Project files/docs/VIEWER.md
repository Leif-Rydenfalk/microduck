# The microduck bench — open it, move it, play it

**http://localhost:8765/web/microduck.html**

One page that answers the three questions a render cannot: *what parts are in
there*, *what can it move*, and *does the policy actually walk*.

```bash
# the dashboard already runs under launchd; if it is not up:
~/dev/ce-workshop/ce-cad/bin/dash          # -> http://localhost:8765/web/
open -a "Google Chrome" http://localhost:8765/web/microduck.html
```

Nothing else to start. It is a second page on the ce-cad dashboard, so it
shares the dashboard's port, its vendored three.js and its theme — the
assembly card is one click away in the header, and every part row links back
to its own card and to `/api/files?id=part:...`.

## What it does

**See every part.** 70 placed parts over 15 bodies, 817,902 triangles, each
one pickable. Hover for its name, click for its card — body, the hinge that
drives it, triangle count, the mesh file on disk, its triad ref, and links to
its dashboard card and its files. The left panel lists them grouped by body;
`ours only` hides everything Pollen supplied and leaves the 33 parts this repo
rebuilt (they are orange in the scene and tagged OURS in the list). `explode`
pulls the assembly apart along each part's own outward direction; `x-ray the
shells` makes the trunk and head shells transparent so the XL330s, the battery
and the boards are visible without hiding anything.

**Move the mechanics.** One slider per actuated hinge, all fourteen, grouped
left leg / head+neck / right leg. Each is wired to the real axis and the real
range: the green band on the track is what the servo has, and the slider
deliberately travels 45° past each end so you can try to go further. It
clamps, and it says so — *"CLAMPED — commanded +88.0°, the hinge stops at
+30.0° (range −25…+30°)"*. Child links follow their parent, because the page
runs MuJoCo's own composition, `T(body.pos) · R(body.quat) · R(axis, θ)`, down
the same tree the MJCF declares. `hinge axes` draws all fourteen axes as
arrows attached to the bodies they turn, so they move with the mechanism.

Presets: **STAND · SIT · FOLD · INIT · ZERO** (keys 1, 2, 3, 0), read from the
MJCF's own `<keyframe>` block, not typed in here.

**Play the simulation.** Six recorded MuJoCo runs are on the transport, chosen
from the dropdown and scrubbable frame by frame:

| trajectory | frames | what it is |
|---|---|---|
| `walk_ours` | 401 @ 50 Hz | `BEST_alpha_walking.onnx`, vx 0.25 m/s, walked 0.7925 m |
| `sitstand_ours` | 401 | the sit/stand cycle |
| `stand_from_sit_ours` | 301 | standing up from SIT |
| `stand_from_fold_ours` | 301 | standing up from FOLD |
| `stand_hold_ours` | 201 | standing and holding |
| `walk_stock` | 401 | the same policy on Pollen's stock parts, for comparison |

Space plays and pauses. The sliders follow the sim while it runs, the root
position and orientation come from the free joint's own qpos, and the readout
carries the clock, the frame, the root x and z in metres, and the distance
walked. If any sample in a recording asks for an angle the hinge does not
have, the transport says how many and clamps them rather than drawing a pose
the robot cannot reach.

## Deep links — a pose is a URL

```
?pose=SIT
?traj=sitstand_ours&frame=250&play=1
?joint=left_knee:-45&joint=head_yaw:90
?part=microduck-hip-bracket&isolate=1
?explode=90     ?axes=1     ?xray=1
```

They compose. This is also how the proof shots are taken, so a picture in
`out/viewer-proof/` can be reproduced by opening its URL.

## Where the data comes from

Nothing on the page is authored. `tools/export_viewer.py` reads the files that
are already the truth and writes into the dashboard's served tree:

| written | from |
|---|---|
| `ce-cad/out/web/microduck/scene.json` (53 kB) | `sim/microduck_ours.xml` — tree, hinges, 70 visual geoms, materials; `spec/mesh-to-part.json` for the part refs; `out/sim/scene_walk_ours.xml` for the keyframes |
| `ce-cad/out/web/microduck/geom.bin` (5.46 MB) | the 38 distinct STLs, welded, float32 positions + uint16 indices |
| `ce-cad/out/web/microduck/traj-*.json` | `out/sim/*_traj.npz` — qpos, degrees per frame (the browser cannot open an npz) |

```bash
cd ~/dev/ce-workshop/ce-designs/microduck
python3 tools/export_viewer.py         # ~1 s, pure stdlib — no MuJoCo, no FreeCAD
node   tools/shoot_viewer.mjs          # re-take the proof shots
```

The exporter **cross-checks itself**: it walks the MJCF tree to the world pose
of every hinge and compares that against the MEASURED rows in
`ce-assemblies/microduck/current/joints.json`. Measured 2026-09-02: **14 of 14
AGREE** — worst origin delta 0.000 mm, every axis dot ±1.000000 — and the
header chip on the page states that count. A disagreement would be printed by
name, not swallowed.

## One thing that does not work, and why

`cecad.shots` / `cecad.vision.screenshot_url` **cannot photograph this page.**
Its long-lived Chrome is started with `--disable-gpu`
(`ce-cad/web/shotd.mjs:185`), so the browser hands out no WebGL context at
all. MEASURED 2026-09-02, same URL, same port: under shotd the page's ready
handshake never went true (`ready_ms` 45232, the entire budget); in a Chrome
launched without that flag it was ready in 9 s and drew 817,902 triangles.
This is not specific to microduck — it applies to any WebGL page on this
machine, the dashboard's own 3D viewer included.

Two things came out of that rather than a workaround:

1. **The page states the absence instead of hanging.** With no WebGL it still
   loads the data, still builds the parts list, the sliders and the
   transport, prints *"no WebGL in this browser"* with the reason across the
   stage, and sets `window.__mdReady.webgl = false` — so a prober gets a
   definite answer in a second instead of burning its whole budget on a page
   that will never be ready.
2. **`tools/shoot_viewer.mjs`** reuses ce-cad's own CDP driver
   (`ce-cad/web/_cdp.mjs`) and drops that one flag. It waits on the page's own
   ready handshake, refuses to file a PNG under 20 kB, and exits non-zero if
   any shot did not draw.
