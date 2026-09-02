# part:microduck-eye-ring — the eye bezel, mesh-backed (Pollen's `noenoeil`)

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
