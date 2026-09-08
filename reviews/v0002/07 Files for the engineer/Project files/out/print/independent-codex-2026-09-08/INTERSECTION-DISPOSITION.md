# Small mesh diagnostics: what is and is not established

The HEAD-V7/V8 candidate retains the original coordinates/surfaces except rigid
print-pose changes. FreeCAD originally reported one bottom-shell intersection,
two jaw intersections and one yaw-roll intersection. The intersection-segment
lengths are approximately 0.0022, 0.1947, 0.0184 and 0.0547 mm respectively;
these do not by themselves establish an acceptable functional surface.

I independently sectioned the archived meshes at nearby actual print sampling
planes and compared them to actual model extrusion, excluding support. Four
neighborhoods of radius 1.5 mm were examined, with 0.03 mm sampling along sections
and toolpaths. The real path plots are
`v7-validation/intersection-functional-sections.png`; values are in the matching
JSON. These parts have identical poses in V8, though the final V8 path analysis
must use its own exact file when it becomes stable.

| Location | Sample plane / layer | Maximum contour-to-path-centerline distance |
|---|---|---|
| Bottom shell | Z9.9 / L50 | 0.211 mm |
| Jaw left | Z5.5 / L28 | 0.214 mm |
| Jaw right | Z5.5 / L28 | 0.210 mm |
| Yaw-roll side | Z7.1 / L36 | 0.468 mm |

The first three are consistent with the expected ~0.21 mm offset of a 0.42 mm
perimeter centerline from a geometric boundary. The viewed nearby sliced walls
remain continuous: no local missing-material gap was detected in these sampled
sections. This is local slice evidence, not proof that the mesh has no defect.

The yaw-roll side shows smoothing/filling of a small notch: the maximum is
about 0.26 mm beyond the nominal half-line-width offset. **Exact local shape is
not preserved in that neighborhood.** It has no missing-layer or unsupported
extrusion failure, but whether this area is a functional mating surface, and
whether the resulting local deviation meets its fit tolerance, is **CANNOT
DETERMINE** from the available evidence. A current interface drawing/physical
mating test is needed; the old reconstruction BOM is not fit evidence.

The yaw's extra six-face component is exactly coplanar, with zero enclosed volume
and 2.6085 mm² of double-sided surface area. It is not a printable volumetric
part. It was left unchanged to keep the export/pose experiments controlled.
No independent A/B slice after removal has been performed, so its complete
slicer effect is **not certified harmless**. It does not justify claiming the
mesh is a single clean solid merely because aggregate winding/watertightness
checks pass.

These observations allow specific layer continuity and local path statements.
They do not certify strength, whole-part dimensional accuracy, assembler fit,
material behavior, adhesion, or physical print success. They are not replaced
by a successful slicer exit code.

## HEAD-V9 follow-up

The avoidable six-face zero-volume component has now been removed. Main-body
volume is unchanged; no substantive triangle was added or changed. Winding
number is 1.0 at its centroid and at points ±0.01 mm in Y, establishing those
points lie inside the main body. Original/cleaned standalone checked slices
both have 112 layers; full-model path sampling differs by at most 0.0319 mm at
0.05 mm sample spacing. The A/B overlay was rendered and inspected. See
`experiments/yaw-cleanup-proof.json`, `yaw-ab-path-proof.json`, and
`yaw-zero-volume-ab.png`. The prior unresolved removal question is resolved
at this measured geometric/slicing scope.

All four tiny intersection diagnostics remain on the exact final V9 archive.
Its local functional-section audit was rerun, rendered and inspected under
`v9-validation/intersection-functional-sections.*`, with the same local
conclusions above. Continuous printable paths are established; exact mating
fit and mechanical strength remain unverified.
