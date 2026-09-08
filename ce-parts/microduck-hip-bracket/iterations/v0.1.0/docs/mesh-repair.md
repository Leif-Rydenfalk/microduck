# Geometry correction, 2026-09-09

This iteration preserves v0.0.1. Finished STEP solids and STL meshes were independently read back. See evidence/BUILD.json and evidence/INDEPENDENT-CHECK.json. This is geometry evidence, not physical fit or strength validation.

Exact circular arcs replace polygon arcs. The straight roll plate ends at the actual outer R8 tangent. R2 root fillets now build after redundant seams are removed. Bounding-box guards measure actual surfaces, not B-spline control poles. All eight mounting bore probes remain empty; shifted negative-control probe collides. Optional R1 outer rib rounding remains omitted because its apparently valid kernel result self-intersects near counterbores. The edge is sharp; this is explicit remaining shape deviation from reference.
