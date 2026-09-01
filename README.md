# microduck — a reverse-engineered Pollen Robotics Microduck

*A ce-designs machine (`design:microduck`) and a triad root. Started 2026-09-01.*

Pollen Robotics sells the Microduck (https://pollen-robotics.com/microduck/)
with its firmware and software open source and its **mechanics closed**. This
repo rebuilds the mechanics from everything that is public — the product
photos and video, the published specifications, the open firmware/software
(which encodes joint names, limits, servo IDs and the robot description), and
the open-source lineage it grew from (Open Duck Mini) — as parametric ce-cad
parts that match the images, on the triad shelf, with an evidence ledger.

Leif, 2026-09-01, verbatim: *"Reverse engineer this shit … Because they didn't
open source the mechanics. … It should match the images exactly."*

## What is where

```
README.md            this page
SPEC.md              THE specification we design against — every number sourced
docs/                PARTS.md (every part, one sourced row each) · ELECTRONICS-AND-SOFTWARE.md
                     (boards, bus, IMUs, pins, daemons, wiring diagram) · BOM.md (bought /
                     printed / soft / fasteners, cost vs Pollen $399 and ODM v2 €398) · REBUILD-PROTOCOL.md
                     · PRODUCTION.md (GOAL rung 7: cost per robot at 1/10/100/1000, make/buy and
                     print/mould with break-even, battery shipping + CE/FCC checklist, assembly
                     labour, top-10 unknowns; built from the three lenses in docs/production/ —
                     components.md, process.md, compliance-and-assembly.md)
research/            the dossiers: product page, code mining, images, lineage
images/              reference photos + CATALOG.md (what each shows) + PROPORTIONS.md
spec/                machine-readable spec: specs.json, kinematics.json, bom.json
design.py            the machine — `bin/cad ce-designs/microduck/design.py`
ce-parts/            triad shelf for THIS machine (bought + generated parts)
ce-connections/      connection kinds this machine adds
ce-assemblies/       assembly:microduck and its sub-assemblies (blueprint-first, P12)
out/                 renders, STEP, drawings, release packs — COMMITTED, they are data
tools/               tools written for this project (photo-match, mesh-measure)
firmware/ software/  pointers to the upstream open-source repos + our notes
evidence/            ledger.jsonl + artifacts, append-only
```

This folder is a **triad root**: `CE_TRIAD_ROOT=$PWD ~/dev/ce-workshop/bin/triad check --all`
resolves every `part:` / `connection:` / `assembly:` ref against it first.

## Method

1. **Research** — collect every public fact with its source and quote (research/).
2. **Specify** — SPEC.md: dimensions, DoF, actuators, electronics, materials,
   with confidence per number (published / measured-from-image / inferred).
3. **Blueprint** — `bin/triad-blueprint` boxes for body, head, legs, battery,
   compute, before any part is chosen (PROTOCOLS.md P12).
4. **Design** — one ce-cad part per box, matched against the photos with the
   photo-match tool, checked, rendered, delivered.
5. **Evidence** — every check and comparison lands in the ledger; the machine
   is born T0 and earns its tier.

## Status

See `SPEC.md` §Status and `evidence/ledger.jsonl`. Nothing here is a claim
that the design is correct — a number without a source is a defect.
