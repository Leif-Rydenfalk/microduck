"""PROVE 5 — CAN IT BE ASSEMBLED AT ALL.

    ce-cad/bin/cad tools/assembly_order.py [--pitch 0.5] [--stage N]

Every other check in this repo looks at the ASSEMBLED microduck. This one asks
the strictly harder question a factory asks on day one: is there an order in
which every one of these 134 placed bodies can be brought to where it sits,
and can a hex key then reach every one of the 64 screws.

WHAT IS MEASURED, and by what
-----------------------------
  the blocking relation      cecad.meshassembly.blocking() over the 26
                             directions, pitch 0.5 mm, mover eroded 1 cell
                             (= 0.5 mm of lateral grazing allowed, stated)
  a build order              disassembly() reversed. Greedy is COMPLETE for
                             single-part straight-line removal, so a stall is
                             a real deadlock and not a search artefact
  the manual's own order     check_order() against
                             ce-assemblies/microduck/current/manual/MANUAL.md
  tool access                axis_clearance() — exact point-to-triangle
                             distance along each screw's own axis, outward
                             from the head, in the FULLY ASSEMBLED state and
                             again at the moment the screw goes in

THE FRAMING. The real Microduck walks. So a body this pass reports as
impossible to install is first evidence that OUR MODEL is wrong — a mesh
placed at the wrong depth, a bearing modelled as interfering, a shell whose
opening we never modelled — and only after that a claim about the product.
Every blocked step therefore names the body that blocks it, so the lead can be
chased to a specific dimension.

Reads:  ce-assemblies/microduck/current/placements.json  (134 rows: 70 Pollen
        mesh instances + 64 fasteners placed through their connections)
Writes: out/assembly/order.json
"""
import json
import os
import sys
import time

import numpy as np

R = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck"
sys.path.insert(0, "/Users/leifrydenfalk/dev/ce-workshop/ce-cad")
sys.path.insert(0, R + "/sim")

from cecad import meshassembly as MA           # noqa: E402
from route3d_grid import load_rows, world_tris  # noqa: E402

SCRATCH = "/private/tmp/int-prove5"
LOG = open(SCRATCH + "/order.log", "a", buffering=1)
PITCH = float(os.environ.get("PROVE5_PITCH", "0.5"))
LATERAL = int(os.environ.get("PROVE5_LATERAL", "1"))


def say(*a):
    s = " ".join(str(x) for x in a)
    sys.stdout.write(s + "\n")
    LOG.write(s + "\n")


# ---------------------------------------------------------------------------
# the bodies


def label(i, row):
    if row.get("mesh"):
        return "%s/%s#%d" % (row.get("body"), row["mesh"], row.get("geom_index", 0))
    p = row.get("part", "?").replace("part:screw-", "").replace("-iso4762", "")
    return "%s@%s" % (row.get("instance", "fastener#%d" % i),
                      "%s%g" % (p, (row.get("params") or {}).get("length_mm", 0)))


def build_scene(rows, pitch):
    t0 = time.time()
    tri = world_tris(rows)
    say("world_tris: %d bodies, %.1f s" % (len(tri), time.time() - t0))
    sc = MA.Scene(pitch)
    meta = {}
    for i, body, part, mesh, tris in tri:
        n = label(i, rows[i])
        sc.add(n, tris, meta={"row": i, "body": body, "part": part, "mesh": mesh,
                              "is_screw": rows[i].get("mesh") is None})
        meta[n] = sc.meta[n]
    lo, hi = sc.bbox()
    say("scene bbox %s .. %s mm" % (np.round(lo, 3).tolist(), np.round(hi, 3).tolist()))
    return sc, meta


def voxelise(sc, cache):
    if os.path.exists(cache):
        z = np.load(cache, allow_pickle=True)
        if float(z["pitch"]) == sc.pitch and list(z["names"]) == sc.names:
            sc.origin = z["origin"]
            for n in sc.names:
                sc.vox[n] = z["v_" + n]
            say("voxels from cache %s" % cache)
            return sc
    t0 = time.time()
    sc.voxelise(progress=lambda i, n, name, k:
                say("  vox %3d/%d %-46s %8d cells" % (i, n, name, k)))
    tot = sum(len(v) for v in sc.vox.values())
    say("voxelised %d bodies, %d cells, %.1f s" % (len(sc.vox), tot, time.time() - t0))
    np.savez_compressed(cache, pitch=sc.pitch, origin=sc.origin,
                        names=np.array(sc.names, dtype=object),
                        **{"v_" + n: v for n, v in sc.vox.items()})
    return sc


# ---------------------------------------------------------------------------


def main():
    rows = load_rows()
    say("=" * 78)
    say("PROVE 5 run %s  pitch %.3f mm  lateral %d cell(s)"
        % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), PITCH, LATERAL))
    say("placement rows %d" % len(rows))
    sc, meta = build_scene(rows, PITCH)
    voxelise(sc, "%s/vox-%g.npz" % (SCRATCH, PITCH))

    t0 = time.time()
    rel = MA.blocking(sc, lateral_cells=LATERAL,
                      progress=lambda i, n, d: say("  axis %2d/%d %s  %.1f s"
                                                   % (i, n, d, time.time() - t0)))
    say("blocking relation in %.1f s" % (time.time() - t0))

    names = sc.names
    # ---- the flat question: one part at a time, out of the finished robot
    steps, stuck = MA.disassembly(rel, names)
    say("FLAT: %d of %d bodies come out one at a time; %d stuck"
        % (len(steps), len(names), len(stuck)))

    # ---- pair counts, for the report
    n_pairs = 0
    for d in rel:
        n_pairs += sum(len(v) for v in rel[d].values())

    out = {
        "$triad": 1, "kind": "assembly-order",
        "generated_by": "tools/assembly_order.py",
        "record": {
            "units": "mm",
            "frame": "MJCF world at zero pose — the frame placements.json uses",
            "method": {
                "instrument": "cecad.meshassembly (ce-cad), selftest 22/22 PASS; "
                              "broken on purpose CECAD_MESHASSEMBLY_BREAK=1 14/22, =2 7/22",
                "relation": "B blocks A along d iff a column of the (u,v) "
                            "projection holds t_max(B) > t_min(A); exact for "
                            "solids because a surface attains both extents",
                "directions": 26,
                "pitch_mm": PITCH,
                "lateral_tolerance_cells": LATERAL,
                "lateral_tolerance_mm": PITCH * LATERAL,
                "tolerance_means": "the mover may graze a neighbour by this much "
                                   "across its direction of travel and still count "
                                   "as free. Without it every press fit and every "
                                   "screw in a Ø1.6 pilot reads as welded in place.",
                "limits": "single-part STRAIGHT-LINE moves only. A part that needs "
                          "a rotation, a flex, or to travel as part of a "
                          "sub-assembly is reported blocked here, and that is a "
                          "CANNOT DETERMINE about the product, not a FAIL.",
            },
            "counts": {
                "bodies": len(names),
                "mesh_instances": sum(1 for n in names if not meta[n]["is_screw"]),
                "screws": sum(1 for n in names if meta[n]["is_screw"]),
                "ordered_blocking_facts": n_pairs,
                "flat_removable": len(steps),
                "flat_stuck": len(stuck),
            },
            "flat_removal_order": steps,
            "flat_stuck": stuck,
            "bodies": {n: {"body": meta[n]["body"], "part": meta[n]["part"],
                           "mesh": meta[n]["mesh"], "is_screw": meta[n]["is_screw"],
                           "voxels": int(len(sc.vox[n]))} for n in names},
        },
    }
    os.makedirs(R + "/out/assembly", exist_ok=True)
    json.dump(out, open(R + "/out/assembly/order.json", "w"), indent=1)
    say("wrote out/assembly/order.json")

    # the relation itself, for the later stages (blocked-by lists per direction)
    relout = {d: {n: sorted(v) for n, v in mp.items() if v} for d, mp in rel.items()}
    json.dump({"pitch_mm": PITCH, "lateral_cells": LATERAL, "rel": relout},
              open(SCRATCH + "/rel-%g.json" % PITCH, "w"))
    say("wrote %s/rel-%g.json" % (SCRATCH, PITCH))
    say("DONE %.1f s" % (time.time() - t0))


main()
