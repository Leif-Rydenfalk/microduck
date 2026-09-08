"""route3d_grid — build the assembly's OCCUPANCY GRID once and cache it.

Every triangle of every placed mesh in ce-assemblies/microduck/current/placements.json,
scaled x1000 (Pollen's assets are in METRES — GOAL.md handover note 5) and put through
its placement, rasterised into a 1.0 mm voxel grid. The grid is the free space the
cable router plans in, and its Euclidean distance transform is the ONE array every
clearance number in this lane comes from.

Run: ce-cad/bin/cad sim/route3d_grid.py   (writes /private/tmp/int-wire3d/occ.npz)
"""
import json, os, sys, time
import numpy as np
import Mesh

R = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck"
sys.path.insert(0, "/Users/leifrydenfalk/dev/ce-workshop/ce-cad")
from cecad.route import Occupancy

CELL = 1.0
OUT = "/private/tmp/int-wire3d/occ.npz"


def quat_matrix(q):
    w, x, y, z = q
    n = (w * w + x * x + y * y + z * z) ** 0.5
    w, x, y, z = w / n, x / n, y / n, z / n
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]], float)


def load_rows():
    return json.load(open(R + "/ce-assemblies/microduck/current/placements.json"))["record"]["rows"]


SCREW_TESS_MM = 0.20     # tessellation deviation for a built fastener solid, mm


def _screw_tris(doc, ref, params):
    """A PLACED fastener as triangles, built from its own part folder.

    placements.json grew 64 fastener rows (commit 3f3fda3) that carry no
    mesh_file: they are parametric solids placed through a connection's mate().
    A screw is material, so the router must see it — a cable through a screw
    head is exactly the interference this lane exists to catch. Built with
    cecad.triad.load (the same call tools/build_fastener_skeleton.py makes),
    tessellated at %.4f mm, and cached on (ref, params) because these screws are
    a FAMILY on length_mm (that trap is recorded in build_fastener_skeleton.py).
    """ % SCREW_TESS_MM
    import cecad.triad as triad
    part = triad.load(doc, ref, dict(params or {}))
    vts, fcs = part.shape.tessellate(SCREW_TESS_MM)
    pts = np.array([[v.x, v.y, v.z] for v in vts], float)
    fac = np.array(fcs, int)
    return pts, fac


def world_tris(rows):
    """[(row_index, body, part, mesh, tris_mm_world)] — the x1000 is applied here, once.

    Mesh rows are Pollen STLs in METRES and get the x1000. Fastener rows are
    parametric solids already in mm and get NO scale: the scale is applied per
    row from the row's own kind, never globally.
    """
    cache = {}
    out = []
    doc = None
    for i, r in enumerate(rows):
        f = r.get("mesh_file")
        if not f:
            ref = r.get("part")
            if not ref:
                raise ValueError("placements row %d has neither mesh_file nor part" % i)
            import FreeCAD as App
            if doc is None:
                doc = App.newDocument("route3d_grid_parts")
            key = (ref, tuple(sorted((r.get("params") or {}).items())))
            if key not in cache:
                cache[key] = _screw_tris(doc, ref, r.get("params"))
            pts, fac = cache[key]
            Rm = quat_matrix(r["world_quat_wxyz"])
            p = np.asarray(r["world_pos_mm"], float)
            wp = pts @ Rm.T + p
            out.append((i, r.get("body") or "fastener", ref,
                        r.get("instance") or ref, wp[fac]))
            continue
        if f not in cache:
            m = Mesh.Mesh(f)
            pts = np.array([[p.x, p.y, p.z] for p in m.Points], float) * 1000.0
            fac = np.array([list(fa.PointIndices) for fa in m.Facets], int)
            cache[f] = (pts, fac)
        pts, fac = cache[f]
        Rm = quat_matrix(r["world_quat_wxyz"])
        p = np.asarray(r["world_pos_mm"], float)
        wp = pts @ Rm.T + p
        out.append((i, r["body"], r.get("part"), r["mesh"], wp[fac]))
    return out


def main():
    t0 = time.time()
    rows = load_rows()
    tri = world_tris(rows)
    allp = np.concatenate([t[4].reshape(-1, 3) for t in tri], axis=0)
    lo, hi = allp.min(0), allp.max(0)
    n_mesh = sum(1 for r in rows if r.get("mesh_file"))
    print("placed rows %d (%d mesh, %d built fastener solids)  vertices %d"
          % (len(rows), n_mesh, len(rows) - n_mesh, len(allp)))
    print("assembly bbox mm  lo %s  hi %s" % (np.round(lo, 4).tolist(), np.round(hi, 4).tolist()))
    occ = Occupancy(lo, hi, CELL, pad_mm=20.0)
    print("grid shape", occ.shape, "cells", int(np.prod(occ.shape)))
    marked = 0
    for i, body, part, mesh, tris in tri:
        marked += occ.add_triangles(tris, body_id=i + 1, label="%s/%s" % (body, mesh))
    occ.finish()
    occ_cells = int(occ.grid.sum())
    print("marked samples %d  occupied cells %d (%.3f%% of grid)"
          % (marked, occ_cells, 100.0 * occ_cells / np.prod(occ.shape)))
    print("edt max %.4f mm" % float(occ.edt.max()))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    np.savez_compressed(OUT, grid=occ.grid, owner=occ.owner, edt=occ.edt.astype(np.float32),
                        lo=occ.lo, cell=np.array([CELL]))
    json.dump({str(k): v for k, v in occ.labels.items()},
              open("/private/tmp/int-wire3d/labels.json", "w"), indent=1)
    print("wrote %s  %.1f MB  in %.1f s" % (OUT, os.path.getsize(OUT) / 1e6, time.time() - t0))


main()
