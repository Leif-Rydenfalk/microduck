# part:microduck-eye-ring — the eye bezel, REBUILT PARAMETRICALLY (ours)

**Status, 2026-09-05: OURS, and graded PASS.** This folder no longer ships Pollen
Robotics' mesh. `cad/part.py` is a solid of revolution generated from ten caliper
readings and three locating tabs; `geometry/noenoeil.stl` (CC BY-SA-NC) has been
deleted and `geometry/eye-ring.stl` is exported from our own build.

**How the geometry was authored.** `tools/own_measure_eyering.py` ray-casts the
published artifact at 0.1 mm pitch along two orthogonal probe lines and freezes the
readings in `out/own/measure/eye-ring.json` — a list of DIMENSIONS, not geometry.
`cad/part.py` quotes ten of them by probe line and revolves a six-point (r, y)
profile about the optical axis, then adds three annular-sector prisms for the tabs.
Every driving number is a fit dimension: the Ø14.400 bore is clearance for
`part:microduck-m12-lens`' barrel, the rear face at y -55.500 butts on
`part:microduck-face-part`'s front plane, and the three tabs enter that panel and
locate the bezel on the optical axis. Measuring a published artifact to establish
dimensions is ordinary reverse engineering; no vertex, facet or decimated outline of
Pollen's mesh survives here.

**The grade (`ce-cad/bin/cad-refcheck`, evidence/refcheck/2026-09-04T19-21-10Z/).**

| leg of docs/REBUILD-PROTOCOL.md | required | measured | verdict |
|---|---|---|---|
| p95 surface distance reference → ours | ≤ 1.0 mm | **0.0109 mm** | PASS |
| p95 surface distance ours → reference | ≤ 1.0 mm | **0.0109 mm** | PASS |
| bbox delta per axis | ≤ 1.5 mm | **-0.009 / 0.000 / 0.000 mm** | PASS |
| unmatched reference holes/bosses | 0 | **0** (2 of 2 matched) | PASS |

Median 0.0009 mm, max 0.0140 mm, 100.0 % of 6000 samples inside 1.0 mm both ways.
One round. Built solid MEASURED off the finished shape: 1 solid, 1 shell, 87 faces,
valid, volume 4255.615 mm³, bbox 30.000 × 9.500 × 30.000 mm. Exported STL WATERTIGHT
(2076 triangles, 0 open / 0 non-manifold / 0 misoriented edges,
`out/own/stlcheck/eye-ring.json`).

**What is still CANNOT DETERMINE.** The ring's OD on the PRODUCT, as opposed to on
the published mesh. The photogrammetry below stands unchanged: solving ring OD and
head width together off the one true front view gives **31.239 ± 1.065 mm** against
the 30.000 modelled here — CANNOT DETERMINE at the 1.5 mm rule, and a calliper across
one product ring settles it. This rebuild is graded against the MESH, which is what
the licence question needs; it is not a claim about the retail part's diameter.

---

## The earlier measurement record (kept)


**What it is.** The accent-colour ring around the camera lens on the Microduck's face. GOAL.md
finding 1 said the product's eye bezel is *missing* from the simulation meshes. It is not: Pollen's
mesh `noenoeil` (spec/mesh-to-part.json maps it here) is a **Ø30.000 mm ring, 7.5 mm long** (the boss),
with a **Ø14.400 bore** for the M12 lens, standing **proud of the face panel** — the face panel's only
opening on this axis is the Ø14.5 lens hole, so the whole ring is visible, exactly as in the
photographs. Measured with cecad.meshfeatures / meshslice on `reference/pollen-microduck-rl/assets/noenoeil.stl`
(this iteration's `geometry/noenoeil.stl`, sha256 in `evidence/ledger.jsonl`).

**Against the product (out/head/head.json, HEAD-RECONSTRUCTION.html §6).**
- True front view (flat-lay, ratio to head width, scale-free): eye OD / head width photo 0.3353 vs mesh 0.3226
  → **+1.16 mm** on the Ø30.000 ring if the head is the mesh's 91.763 mm wide. Ring centre +0.93 mm below the
  shell top and -2.13 mm off the mid-line against the mesh; ToF window +0.13 mm from the MJCF site.
- Profile photographs, ring diameter over head extent, photograph against the render at the fitted pose
  (scale-free): cream-profile-left: ring/head 0.3119 (photo) vs 0.2663 (render) → +5.15 ± 0.49 mm; sky-three-quarter-front-left: ring/head 0.2796 (photo) vs 0.2804 (render) → -0.09 ± 0.44 mm; graphite-profile-right: ring/head 0.2421 (photo) vs 0.2417 (render) → +0.05 ± 0.46 mm → combined **-0.02 ± 0.32 mm**.
- Verdict at the 1.5 mm rule: **CANNOT DETERMINE**. The eye ring: a calliper across the ring's outer edge (mesh noenoeil 30.000 mm), or Pollen's part drawing; the front-view photograph already puts it at +1.16 mm (implied) and the profiles at -0.02 ± 0.32 mm.

**Radial profile of the mesh (y = const cuts, r about the axis), mm.** y -63.25: r 14.75; y -62.75: r 15.00; y -62.25: r 15.00; y -61.75: r 15.00; y -61.25: r 15.00; y -60.75: r 15.00; y -60.25: r 15.00; y -59.75: r 15.00; y -59.25: r 15.00; y -58.75: r 15.00; y -58.25: r 15.00; y -57.75: r 15.00; y -57.25: r 15.00; y -56.75: r 15.00; y -56.25: r 15.00; y -55.75: r 15.00; y -55.25: r 9.50; y -54.75: r 9.50; y -54.25: r 9.50

**Iteration.** v0.0.1 is the loader; a parametric rebuild (revolve: Ø30 × 7.5 boss, Ø14.4 bore, rear spigot)
graded by cad-refcheck against this mesh may replace it in v0.0.2, the slug stays.
