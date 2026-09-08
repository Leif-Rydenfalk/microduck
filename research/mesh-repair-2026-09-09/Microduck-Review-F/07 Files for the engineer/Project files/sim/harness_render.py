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
from cecad import render as _cecad_render

# MODE, chosen by LOOKING at both: "pbr" lights the scene but shades every body
# from its material and the three groups come out the same grey, so the cables
# cannot be told from the boxes they pass. "cad" is flat with hidden-line edges
# and the routes read immediately. The picture's job here is to show WHERE THE
# CABLES GO, so it is drawn in the mode that shows that.
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


# THE PICTURE IS BUILT FROM COARSE TUBES, AND HERE IS WHY, MEASURED. Reading the
# 16 exported cable STLs back with makeShapeFromMesh gives ~64 000 planar faces
# and the fifteen XL330 meshes several times that; the renderer did not reach its
# first log line in five minutes. A picture needs the SHAPE of the route, not the
# 16-gon, so the tube is rebuilt here at RENDER_SIDES around RENDER_STATION_MM
# stations — about 480 triangles a cable instead of 4 000 — from the SAME routed
# waypoints the measured solids were swept along. The exported solids are what
# the numbers were taken on; this is what the eye is shown, and the difference
# between them is one number: the 8-gon sits r(1-cos(pi/8)) = 0.2378 mm inside
# the 3.1243 mm cable, which is smaller than a pixel at this framing.
RENDER_SIDES = 8
RENDER_STATION_MM = 3.0
CTX_MAX_TRIS = 60000       # a context body bigger than this is named and skipped


def _resample(pts, step):
    P = [[float(c) for c in q] for q in pts]
    seg = [math.dist(P[i], P[i + 1]) for i in range(len(P) - 1)]
    total = sum(seg)
    if total <= 0:
        return P
    n = max(2, int(round(total / step)) + 1)
    out, si, acc = [P[0]], 0, 0.0
    for k in range(1, n - 1):
        target = total * k / (n - 1)
        while si < len(seg) - 1 and acc + seg[si] < target:
            acc += seg[si]
            si += 1
        f = 0.0 if seg[si] <= 0 else (target - acc) / seg[si]
        out.append([P[si][j] + (P[si + 1][j] - P[si][j]) * f for j in range(3)])
    out.append(P[-1])
    return out


def _sub(a, b):
    return [a[i] - b[i] for i in range(3)]


def _cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def _norm(v):
    n = math.sqrt(sum(c * c for c in v))
    return [c / n for c in v] if n > 1e-12 else [0.0, 0.0, 1.0]


def tube_shape(poly, od, sides=RENDER_SIDES, station=RENDER_STATION_MM):
    """A cable as a coarse parallel-transport tube, as a Part.Shape."""
    P = _resample(poly, station)
    r = od / 2.0
    T = [_norm(_sub(P[min(len(P) - 1, i + 1)], P[max(0, i - 1)])) for i in range(len(P))]
    seed = [0.0, 0.0, 1.0]
    if abs(sum(seed[i] * T[0][i] for i in range(3))) > 0.9:
        seed = [1.0, 0.0, 0.0]
    d = sum(seed[i] * T[0][i] for i in range(3))
    N = [_norm([seed[i] - d * T[0][i] for i in range(3)])]
    for i in range(1, len(P)):
        d = sum(N[i - 1][j] * T[i][j] for j in range(3))
        N.append(_norm([N[i - 1][j] - d * T[i][j] for j in range(3)]))
    pts, ring, fac = [], [], []
    for i in range(len(P)):
        b = _cross(T[i], N[i])
        ring.append(len(pts))
        for k in range(sides):
            th = 2.0 * math.pi * k / sides
            pts.append(tuple(P[i][j] + N[i][j] * (r * math.cos(th)) + b[j] * (r * math.sin(th))
                             for j in range(3)))
    for i in range(len(P) - 1):
        a, c = ring[i], ring[i + 1]
        for k in range(sides):
            k2 = (k + 1) % sides
            fac.append((a + k, a + k2, c + k2))
            fac.append((a + k, c + k2, c + k))
    c0 = len(pts); pts.append(tuple(P[0]))
    for k in range(sides):
        fac.append((c0, ring[0] + (k + 1) % sides, ring[0] + k))
    c1 = len(pts); pts.append(tuple(P[-1]))
    for k in range(sides):
        fac.append((c1, ring[-1] + k, ring[-1] + (k + 1) % sides))
    sh = Part.Shape()
    sh.makeShapeFromMesh((pts, fac), 1e-4)
    return sh, len(fac)


def main():
    t0 = time.time()
    from mate import mate as eh_mate
    doc = App.newDocument("harness")
    items, counts = [], {"cables": 0, "housings": 0, "context": 0, "cable_files_missing": 0}

    solids = json.load(open(R + "/out/wiring/solids.json"))["record"]
    paths = json.load(open(R + "/out/wiring/paths.json"))["record"]["paths"]
    tris = 0
    for row in solids["cables"]:
        p = R + "/out/wiring/cad/%s.stl" % row["id"]
        if not os.path.exists(p):
            counts["cable_files_missing"] += 1
            say("MISSING cable solid:", p)
            continue
        sh, nt = tube_shape(paths[row["id"]]["waypoints_mm"], row["od_mm"])
        items.append((sh, CABLE_COL, "PVC"))
        tris += nt
        counts["cables"] += 1
    say("cable tubes: %d bodies, %d triangles" % (counts["cables"], tris))

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

    # CONTEXT AS MEASURED BOUNDING BOXES, AND SAID SO. Converting the 19 context
    # meshes with makeShapeFromMesh gives tens of thousands of planar faces and
    # the renderer did not finish ONE view in fifteen minutes (measured, twice).
    # A box is not the body: it is the body's own world extent, computed by
    # pushing every vertex of that mesh through that placement, and it is
    # labelled a PROXY here, in render.json and in the caption. The cables and
    # the housings are the real geometry; the grey boxes only say where the
    # things they plug into are.
    rows = json.load(open(R + "/ce-assemblies/microduck/current/placements.json"))["record"]["rows"]
    cache = {}
    ctx = []
    for r in rows:
        f = r.get("mesh_file")
        if not f or not any(k in (r.get("mesh") or "") or k in (r.get("part") or "")
                            for k in CTX_MESHES):
            continue
        if f not in cache:
            m0 = Mesh.Mesh(f)
            cache[f] = [[p.x, p.y, p.z] for p in m0.Points]
        Rm = quat_matrix(r["world_quat_wxyz"])
        t = r["world_pos_mm"]
        lo = [1e18] * 3
        hi = [-1e18] * 3
        for p in cache[f]:
            q = [sum(Rm[i][k] * p[k] * 1000.0 for k in range(3)) + t[i] for i in range(3)]
            for i in range(3):
                lo[i] = min(lo[i], q[i]); hi[i] = max(hi[i], q[i])
        b = Part.makeBox(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2],
                         App.Vector(lo[0], lo[1], lo[2]))
        items.append((b, CTX_COL, "ABS"))
        ctx.append({"body": r.get("body"), "mesh": r.get("mesh"), "part": r.get("part"),
                    "world_bbox_lo_mm": [round(v, 4) for v in lo],
                    "world_bbox_hi_mm": [round(v, 4) for v in hi]})
        counts["context"] += 1
    counts["context_is"] = ("the MEASURED world axis-aligned bounding box of each placed mesh, "
                            "not its outline — a proxy, drawn only to say where the body is")
    say("drawing %d cables, %d housings, %d context bodies (%d cable files missing)"
        % (counts["cables"], counts["housings"], counts["context"], counts["cable_files_missing"]))

    out = {}
    for view in ("iso", "front", "right", "top"):
        p = R + "/out/wiring/harness-%s.png" % view
        t_r = time.time()
        _cecad_render(items, p, view=view, title="Microduck harness — %s" % view,
                  W=1200, H=850, mode="cad", verbose=False)
        say("   %s rendered in %.1f s" % (view, time.time() - t_r))
        out[view] = os.path.getsize(p) if os.path.exists(p) else 0
        say("  %-6s %s %d bytes" % (view, p, out[view]))
    json.dump({"$triad": 1, "kind": "harness-render", "generated_by": "sim/harness_render.py",
               "record": {"counts": counts, "images": out,
                          "colours": {"cable": CABLE_COL, "housing": HOUSING_COL,
                                      "context": CTX_COL},
                          "context_meshes": list(CTX_MESHES),
                          "context_boxes": ctx}},
              open(R + "/out/wiring/render.json", "w"), indent=1)
    say("done in %.1f s" % (time.time() - t0))


main()
