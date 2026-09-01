# microduck-banana-pcb-locker — the PCB retaining bar

**What it is.** Pollen's `banana_pcb_locker` mesh: a 1.5 mm PLA bar, 54.0
long and 6.6 tall, with a Ø4.03 eye round a Ø2.17 M2 clearance hole at each
end (x ±25, z 53.6), a lower edge that runs flat between x ±23 then rises at
47 deg to meet each eye tangentially, a 12 mm wide notch (centre x = -4,
floor z 52.12, R2 top rounds, R1 floor fillets) and two 2.47 x 2.3 x 1.97
key tabs on the -y face at x ±16.9. It bolts to the power_support's two
Ø3.9 screw pins and clamps the "banana" battery-contact PCB.

**Verdict: PASS** — `ce-cad/bin/cad-refcheck part:microduck-banana-pcb-locker
--ref reference/pollen-microduck-rl/assets/banana_pcb_locker.stl`, round 1:
p95 surface distance 0.013 mm both ways (max 0.227 at the notch fillets),
bbox delta [-0.035, 0.0, -0.026] mm, 2/2 reference holes matched, volume
ratio 0.9962. Report and overlays: `evidence/refcheck/<stamp>/` and
`out/refcheck/microduck-banana-pcb-locker/r1/`.

## How it was measured (2026-09-01)

- `cad-mjcf sections --axis x|y|z`: y 35.0..36.5 (tabs to 32.7), x ±27.02,
  z 48.99..55.61.
- `cecad.meshfeatures.cylinders`: 2 holes Ø2.174, axis y, at (±25, 53.6).
- `cad-mjcf probe`: eye radius from x extreme 26.973 at z 54 -> 2.013;
  lower edge x extreme 23.555 @ z 49.5, 25.164 @ 51, 26.236 @ 52 -> dx/dz
  1.072 (47 deg), tangent to the eye at (26.37, 52.13); notch gap x
  -9.99..1.99 at z 53..55, floor 52.117 (x -8..0), top rounds x -10 -> z
  54.3, -11 -> 55.53 (R2, mirrored about x = -4), floor fillet x -9 -> 52.203;
  tabs x 15.667..18.133, z 49.017..50.983, y 32.7..35.0.
- `cad-mjcf sections --at 35.75 --image`: `out/measure/bl/section_y_35.750.png`.

## CANNOT DETERMINE

- The 0.025 mm draft the y-sections show on the bar's outline (z 48.999 at
  y 35.1 vs 48.975 at y 36.4) — inside the decimation noise, not modelled.
- Whether the floor fillets are R1 or a chamfer: 4 rings in the mesh; the
  0.227 mm max distance is there.
- The tabs' 0.035 mm taper (1.930 tall at y 33, 1.966 at y 34) — modelled square.
