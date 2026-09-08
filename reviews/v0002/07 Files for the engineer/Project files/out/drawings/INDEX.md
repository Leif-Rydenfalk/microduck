# microduck — engineering drawings index

Generated 2026-09-02 by `tools/draw_part.py` under `bin/cad` (FreeCAD kernel), via
`cecad.triad.load(doc, "part:<slug>")` -> `cecad.autosheet.auto_blueprint(part, "out/drawings/<slug>/<slug>")`.
Every row marked verified PASSED `cecad.sheets.verify_sheet` — the SVG on disk was re-read and checked
against the solid (stated scale, title-block bbox + volume, both overall dimensions on every view,
every hole-table row against `cecad.inspect`, no overlapping labels). All sheets are A3 third-angle,
DXF + SVG + PDF per part. Hole count is `len(cecad.inspect.holes(part))` on the built solid.

## Parametric rebuilds — drawn and verified (9)

| part | scale | views | verified | holes |
|---|---|---|---|---|
| microduck-banana-pcb-locker | 2:1 | front, top, SECTION A-A | PASS | 2 |
| microduck-bearing-roll | 2:1 | front, top, SECTION A-A | PASS | 5 |
| microduck-power-support | 1:2 | front, top, right, SECTION A-A | PASS | 14 |
| microduck-shin | 2:1 | right, front, SECTION A-A | PASS | 15 |
| microduck-trunk-base | 2:1 | top, front, SECTION A-A | PASS | 6 |
| microduck-upper-leg-left | 1:2 | front, top, right, SECTION A-A | PASS | 2 |
| microduck-upper-leg-right | 1:2 | front, top, right, SECTION A-A | PASS | 2 |
| microduck-upper-leg-rigidity-plate | 2:1 | right, front, SECTION A-A | PASS | 6 |
| microduck-yaw2roll | 1:1 | front, top, right, SECTION A-A | PASS | 16 |

The first eight have `component.json` `origin: generated` (upper-leg-rigidity-plate's record
still says CANNOT DETERMINE but its rebuild PASSed refcheck per `tools/watch-pass.log`
2026-09-01 23:04:56 and its `cad/part.py` is fully parametric — drawn on that evidence).
Per-part machine results: `out/drawings/<slug>/result.json`.

## Skipped — mesh-backed vendor parts: a decimated mesh has no dimensions to call out (CANNOT DETERMINE)

microduck-jaw, microduck-jaw-soft, microduck-soft-mouth-top, microduck-motor-support,
microduck-neck-pitch-bracket, microduck-neck-plate, microduck-top-head-shell,
microduck-trunk-shell-left, microduck-trunk-shell-right, microduck-yaw-roll-motion,
microduck-foot-left, microduck-foot-right, microduck-sole-left, microduck-sole-right,
microduck-speaker, xl330-m288-t, radxa-zero-3w, np-f550, bmi088, et7301b, fusb302, imx219,
lsm6dsv16x, mcp73213, pn7150, s-8252, st25r3916, tlv320aic3104, vl53l5cx, vl53l8cx
— `component.json` `origin: vendor`; their `cad/part.py` is a loader for Pollen's/the vendor's
published mesh (`cecad.meshshelve`), not a parametric solid.

## Skipped — no geometry yet (CANNOT DETERMINE)

bearing-15x10x3, bearing-22x16x4, microduck-ankle-right, microduck-bottom-head-shell,
microduck-eye-ring, microduck-face-part, microduck-m12-lens, microduck-m12-lens-holder
— 10-line `bin/triad new part` stubs, nothing measured yet.
microduck-camera-module, microduck-imu-to-dxl, microduck-mic, microduck-tof-module
— `origin: inferred`, no `cad/part.py` builder at all.

## Attempted extras (parametric builders whose component.json origin is still unset)

microduck-hip-bracket, microduck-robot-hat-pcb, microduck-ankle-left — see rows appended
below if their sheets verified; otherwise CANNOT DETERMINE with the reason.
