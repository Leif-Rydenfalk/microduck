"""load_share.py — the ONE place that says which single-part studies are a BOUND
rather than the part's own load (F1 skeptic finding 12, 2026-09-03: the
CANNOT DETERMINE grading must be a declared property of the study, applied
by one rule to every study, never a per-part override written after the
numbers were known).

Every FEA study in sim/stress_all.py solves ONE part between its connectors.
For a part that is the SOLE member between them (a bracket, the shin, the
ankle, the foot, the neck stack, the motor support, the power support) the
force MuJoCo measured passes through it entirely — the single-part solve is
the load path, and a FAIL is a FAIL. Two parts are different in kind: they
sit in PARALLEL with another body over their whole span, so the measured
force is shared in a proportion nothing here measured. Their studies apply
100 % of the force as an upper bound: a PASS at 100 % is a PASS at any
share; a FAIL at 100 % says only that the bound is not enough — CANNOT
DETERMINE, with the bound printed. Plain data so both the kernel-side runner
(stress_all.py) and the plain-python grader (fea_rejudge.py) read the same
declaration.
"""

LOAD_SHARE = {
    "microduck-upper-leg-rigidity-plate": {
        "kind": "parallel: closes the thigh housing (part:microduck-upper-leg-left) across its whole span; four screws each end",
        "share_applied": 1.0,
        "why_unmeasured": "the plate-vs-housing stiffness ratio was never solved (the housing does not mesh: fea_meshability_microduck-upper-leg-left.json)",
        "what_settles_it": "a housing that meshes plus a two-body (plate + housing, bolted) solve in cecad.stress / ce-struct, or a printed thigh loaded to the walk peak on a bench with the plate strain-gauged",
    },
    "microduck-trunk-base": {
        "kind": "parallel: a 1 mm plate clamped over its whole area between the two trunk shells (part:microduck-trunk-shell-left / -right) and the hip-yaw XL330 case",
        "share_applied": 1.0,
        "why_unmeasured": "the shells and the servo case are not in the model; held at its four screw holes alone the plate is a 35 mm span it never sees in the assembly",
        "what_settles_it": "a two-body solve (shells + base, bolted) in cecad.stress / ce-struct, or a printed trunk loaded to the walk peak at one hip on a bench",
    },
}
