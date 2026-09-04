"""harness_render — LOOK at the harness: the routed cables and their connector
housings, drawn inside the bodies they actually connect.

    ce-cad/bin/cad sim/harness_render.py
        -> out/wiring/harness-{iso,front,right,top}.png
        -> out/wiring/render.json (what was drawn, counted)

A number that is never looked at is a number nobody checked. This draws the
cable solids the sweep exported (out/wiring/cad/*.stl, one file per run, so a
cable that failed to export cannot silently appear), the EH housings rebuilt
from part:jst-ehr-03 and placed through connection:jst-eh-3pin's mate() — the
same transforms tools/place_harness.py writes into the assembly — and the
context bodies the runs land on: every XL330, the Robot HAT, the Radxa, the
speaker and the battery, in grey.
"""
import json, math, os, sys, time

R = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck"
sys.path.insert(0, "/Users/leifrydenfalk/dev/ce-workshop")
sys.path.insert(0, "/Users/leifrydenfalk/dev/ce-workshop/ce-cad")
sys.path.insert(0, R + "/ce-connections/jst-eh-3pin/current/cad")
LOG = open("/private/tmp/int-wiresolids/render.log", "a", buffering=1)


def say(*a):
    m = " ".join(str(x) for x in a)
    sys.stdout.write(m + "\n")
    LOG.write(m + "\n")


import FreeCAD as App
import Part
import Mesh
from cecad import render as R3

CABLE_COL = "#c0392b"      # the harness
HOUSING_COL = "#f0a30a"    # the connector housings
CTX_COL = "#9aa4ad"        # everything it plugs into
CTX_MESHES = ("xl330-m288-t", "elec_rpi_robot_hat_pcb", "pcb__raspberry_pi_zero_2_w",
              "speaker", "np_f970")


def quat_matrix(q):
    w, x, y, z = q
    n = math.sqrt(w * w + x * x + y * y + z * z)
    w, x, y, z = w / n, x / n, y / n, z / n
    return [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]


def mat4(Rm, t, scale=1.0):
    return App.Matrix(Rm[0][0] * scale, Rm[0][1] * scale, Rm[0][2] * scale, t[0],
                      Rm[1][0] * scale, Rm[1][1] * scale, Rm[1][2] * scale, t[1],
                      Rm[2][0] * scale, Rm[2][1] * scale, Rm[2][2] * scale, t[2],
                      0, 0, 0, 1)


def shape_of_stl(path, tol=0.05):
    m = Mesh.Mesh(path)
    s = Part.Shape()
    s.makeShapeFromMesh(m.Topology, tol)
    return s


def main():
    t0 = time.time()
    from mate import mate as eh_mate
    doc = App.newDocument("harness")
    items, counts = [], {"cables": 0, "housings": 0, "context": 0, "cable_files_missing": 0}

    solids = json.load(open(R + "/out/wiring/solids.json"))["record"]
    for row in solids["cables"]:
        p = R + "/out/wiring/cad/%s.stl" % row["id"]
        if not os.path.exists(p):
            counts["cable_files_missing"] += 1
            say("MISSING cable solid:", p)
            continue
        items.append((shape_of_stl(p), CABLE_COL, "PVC"))
        counts["cables"] += 1

    # the housings, rebuilt and placed through the connection, not read back
    sys.path.insert(0, R + "/ce-parts/jst-ehr-03/current/cad")
    import importlib
    hm = importlib.import_module("part")
    base = hm.build(doc).shape.copy()
    for row in solids["cables"]:
        for h in row.get("housings", []):
            T = h.get("transform")
            if not T:
                continue
            s = base.copy()
            s.transformShape(App.Matrix(T[0][0], T[0][1], T[0][2], T[0][3],
                                        T[1][0], T[1][1], T[1][2], T[1][3],
                                        T[2][0], T[2][1], T[2][2], T[2][3],
                                        0, 0, 0, 1), True)
            items.append((s, HOUSING_COL, "NYLON"))
            counts["housings"] += 1

    rows = json.load(open(R + "/ce-assemblies/microduck/current/placements.json"))["record"]["rows"]
    cache = {}
    for r in rows:
        f = r.get("mesh_file")
        if not f or not any(k in (r.get("mesh") or "") or k in (r.get("part") or "")
                            for k in CTX_MESHES):
            continue
        if f not in cache:
            cache[f] = Mesh.Mesh(f)
        m = Mesh.Mesh(cache[f])
        m.transform(mat4(quat_matrix(r["world_quat_wxyz"]), r["world_pos_mm"], 1000.0))
        s = Part.Shape()
        s.makeShapeFromMesh(m.Topology, 0.2)
        items.append((s, CTX_COL, "ABS"))
        counts["context"] += 1
    say("drawing %d cables, %d housings, %d context bodies (%d cable files missing)"
        % (counts["cables"], counts["housings"], counts["context"], counts["cable_files_missing"]))

    out = {}
    for view in ("iso", "front", "right", "top"):
        p = R + "/out/wiring/harness-%s.png" % view
        R3.render(items, p, view=view, title="Microduck harness — %s" % view,
                  W=1400, H=1000, mode="pbr", ao=True, verbose=False)
        out[view] = os.path.getsize(p) if os.path.exists(p) else 0
        say("  %-6s %s %d bytes" % (view, p, out[view]))
    json.dump({"$triad": 1, "kind": "harness-render", "generated_by": "sim/harness_render.py",
               "record": {"counts": counts, "images": out,
                          "colours": {"cable": CABLE_COL, "housing": HOUSING_COL,
                                      "context": CTX_COL},
                          "context_meshes": list(CTX_MESHES)}},
              open(R + "/out/wiring/render.json", "w"), indent=1)
    say("done in %.1f s" % (time.time() - t0))


main()
