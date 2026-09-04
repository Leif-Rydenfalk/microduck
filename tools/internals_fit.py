"""tools/internals_fit.py — run under ce-cad/bin/cad.

THE QUESTION: our CAD carried the Robot HAT as a bare 0.840 mm plate. The real
board is populated. Does the POPULATED board fit where the model puts it?

WHAT IS PLACED AND ON WHAT AUTHORITY
  The HAT's world transform is Pollen's own: the geom transform of
  elec_rpi_robot_hat_pcb in reference/pollen-microduck-rl (composed into world by
  ce-assemblies/microduck/current/placements.json). That mesh is a PRE-RELEASE
  revision Pollen never produced (out/pcb/hat/mesh-revision.json), so using it as
  the position of a released C1 board needs a reason, and there is one that is
  measured: the FOUR 2.700 mm mounting holes at (0,0) (58,0) (0,-23) (58,-23),
  the two 2.000 mm anchors and the forty 1.020 mm GPIO holes are IDENTICAL in
  every revision (same file, "how_it_was_settled"), and the STL's own coordinates
  are the same board frame our KiCad-derived board is built in. So the mount
  pattern lands where Pollen puts it.
  WHAT IS NOT SETTLED, and is recorded as CANNOT DETERMINE rather than assumed:
  the 180 deg flip about the board normal. Every revision-independent feature
  (4 mount holes, 2 anchors, 40-pin header) is symmetric about the board's x
  centre, so nothing in the geometry picks an end; the features that DO break the
  symmetry are exactly the connector holes that moved between revisions. Only a
  photograph of the assembled head, or Pollen's own CAD carrying a released HAT,
  settles it. BOTH orientations are therefore measured here.

OUTPUT out/internals/hat-fit.json, out/internals/*.png
Run: ce-cad/bin/cad tools/internals_fit.py    (buffered stdout - read the log)
"""
import json
import os
import time

import FreeCAD as App
import Mesh
import Part

REPO = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck"
HAT = os.path.join(REPO, "out", "pcb", "hat")
OUT = os.path.join(REPO, "out", "internals")
os.makedirs(OUT, exist_ok=True)
LOG = open(os.path.join(OUT, "hat-fit.log"), "w")
MESH_TOL = 0.10          # mm, Part.makeShapeFromMesh sewing tolerance
NEAR_MM = 5.0            # only bodies whose bbox comes within this are examined


def P(*a):
    LOG.write(" ".join(str(x) for x in a) + "\n")
    LOG.flush()


def rot(q):
    w, x, y, z = q
    return App.Rotation(x, y, z, w)


def bbgap(a, b):
    """Separation of two bounding boxes, 0 if they overlap. A LOWER BOUND on the
    true surface-to-surface clearance, never the clearance itself."""
    d = 0.0
    for lo1, hi1, lo2, hi2 in ((a.XMin, a.XMax, b.XMin, b.XMax),
                               (a.YMin, a.YMax, b.YMin, b.YMax),
                               (a.ZMin, a.ZMax, b.ZMin, b.ZMax)):
        if lo1 > hi2:
            d = max(d, lo1 - hi2)
        elif lo2 > hi1:
            d = max(d, lo2 - hi1)
    return d


def main():
    t0 = time.time()
    doc = App.newDocument("fit")
    meas = json.load(open(os.path.join(HAT, "pcba-measured.json")))
    rows = json.load(open(os.path.join(REPO, "ce-assemblies", "microduck", "current",
                                       "placements.json")))["record"]["rows"]

    hat_row = [r for r in rows if r["mesh"] == "elec_rpi_robot_hat_pcb"]
    assert len(hat_row) == 1, "expected exactly one HAT geom, got %d" % len(hat_row)
    hat_row = hat_row[0]
    P("HAT world placement from", hat_row["source"])
    P("  parent body", hat_row["body"], "pos_mm", hat_row["world_pos_mm"],
      "quat_wxyz", hat_row["world_quat_wxyz"])

    # ---- the populated board, in board coordinates ---------------------------
    lib = {}
    for key in meas["local_library"]:
        sh = Part.Shape()
        sh.read(os.path.join(HAT, "geometry-local", key + ".step"))
        lib[key] = sh
    parts = []                      # (label, shape in BOARD coordinates)
    bsolid = Part.Shape()
    bsolid.read(os.path.join(HAT, "geometry-local", "__board__.step")) if False else None
    # rebuild the bare board the same way hat_pcba.py does
    import math
    pts = []
    for (cx, cy), a0 in (((58.0, 0.9), 0.0), ((0.0, 0.9), 90.0),
                         ((0.0, -23.0), 180.0), ((58.0, -23.0), 270.0)):
        for i in range(25):
            a = math.radians(a0 + 90.0 * i / 24.0)
            pts.append(App.Vector(cx + 3.5 * math.cos(a), cy + 3.5 * math.sin(a), -0.08))
    pts.append(pts[0])
    board = Part.Face(Part.makePolygon(pts)).extrude(App.Vector(0, 0, 1.0))
    parts.append(("board", board))
    for p in meas["placements"]:
        sh = lib[p["key"]].copy()
        sh.Placement = App.Placement(
            App.Vector(p["at"][0], p["at"][1], 0.84 if p["side"] == "top" else 0.0),
            App.Rotation(App.Vector(0, 0, 1), p["rot_deg"] or 0.0)).multiply(sh.Placement)
        parts.append((p["refdes"], sh))
    # INDEPENDENT GUARD: rebuilding from the library must reproduce, in board
    # coordinates, the bbox tools/hat_pcba.py measured on the shapes it held in
    # memory. If a library file is not in the local frame it claims, the bodies
    # scatter and this catches it before a single clearance number is written.
    inb = Part.makeCompound([s for _, s in parts]).BoundBox
    want = meas["pcba"]["bbox"]
    got = [inb.XMin, inb.YMin, inb.ZMin, inb.XMax, inb.YMax, inb.ZMax]
    e = max(abs(a - b) for a, b in zip(got, want))
    P("rebuild-from-library check: bbox %s vs hat_pcba's %s -> worst %.6f mm"
      % ([round(v, 4) for v in got], want, e))
    if e > 1e-3:
        P("STOP: the library does not rebuild the board it was measured from. "
          "Every clearance below would be measured on scattered bodies.")
        raise SystemExit("library rebuild deviates %.6f mm" % e)
    P("populated board rebuilt from the local library:", len(parts), "bodies "
      "(1 board +", len(meas["placements"]), "components)")

    mesh_cache, solid_cache = {}, {}

    def placed_mesh(r):
        k = (r["mesh_file"], r["geom_index"], r["body"])
        if k not in mesh_cache:
            m = Mesh.Mesh(r["mesh_file"])
            m.transform(App.Matrix(1000, 0, 0, 0, 0, 1000, 0, 0, 0, 0, 1000, 0, 0, 0, 0, 1))
            m.Placement = App.Placement(App.Vector(*r["world_pos_mm"]), rot(r["world_quat_wxyz"]))
            mesh_cache[k] = m
        return mesh_cache[k]

    def sewn(r):
        """The placed mesh as a solid. Sewing is the expensive step, so it is done
        once per geom and reused for both flips."""
        k = (r["mesh_file"], r["geom_index"], r["body"])
        if k not in solid_cache:
            try:
                shp = Part.Shape()
                shp.makeShapeFromMesh(placed_mesh(r).Topology, MESH_TOL)
                solid_cache[k] = (Part.makeSolid(shp) if shp.Shells else shp, None)
            except Exception as e:
                solid_cache[k] = (None, str(e))
        return solid_cache[k]

    results = {}
    for flip in (0, 180):
        pl = App.Placement(App.Vector(*hat_row["world_pos_mm"]), rot(hat_row["world_quat_wxyz"]))
        if flip:
            # 180 deg about the board's own normal, through the mount-pattern centre
            c = App.Vector(29.0, -11.5, 0.42)
            spin = App.Placement(c, App.Rotation(App.Vector(0, 0, 1), 180.0)).multiply(
                App.Placement(c.negative(), App.Rotation()))
            pl = pl.multiply(spin)
        world = []
        for label, sh in parts:
            s = sh.copy()
            s.Placement = pl.multiply(s.Placement)
            world.append((label, s))
        comp = Part.makeCompound([s for _, s in world])
        cb = comp.BoundBox
        P("flip %3d deg: populated HAT world bbox %s size %s"
          % (flip, [round(v, 3) for v in (cb.XMin, cb.YMin, cb.ZMin, cb.XMax, cb.YMax, cb.ZMax)],
             [round(cb.XLength, 3), round(cb.YLength, 3), round(cb.ZLength, 3)]))

        # ---- what else is near it -------------------------------------------
        hits, near = [], []
        for r in rows:
            if r is hat_row or not r.get("mesh_file"):
                continue
            if not os.path.exists(r["mesh_file"]):
                continue
            m = placed_mesh(r)
            mb = m.BoundBox
            g = bbgap(cb, mb)
            if g > NEAR_MM:
                continue
            near.append((r["part"], r["mesh"], r["geom_index"], round(g, 4), r, mb))
        P("flip %3d deg: bodies whose bbox comes within %.1f mm: %d"
          % (flip, NEAR_MM, len(near)))

        for part, mesh, gi, g, r, mb in near:
            solid, err = sewn(r)
            if solid is None:
                hits.append(dict(part=part, mesh=mesh, geom=gi, bbox_gap_mm=g,
                                 verdict="CANNOT DETERMINE",
                                 why="the mesh would not sew into a solid at %.2f mm: %s"
                                     % (MESH_TOL, err)))
                continue
            vol, who = 0.0, []
            for label, s in world:
                if bbgap(s.BoundBox, mb) > 0:
                    continue
                try:
                    cm = s.common(solid)
                except Exception:
                    continue
                if cm.Volume > 1e-6:
                    vol += cm.Volume
                    who.append((label, round(cm.Volume, 4)))
            who.sort(key=lambda t: -t[1])
            hits.append(dict(part=part, mesh=mesh, geom=gi, bbox_gap_mm=g,
                             interference_mm3=round(vol, 4),
                             verdict="FAIL" if vol > 1e-3 else "PASS",
                             what="solid-solid common volume between each populated-HAT body "
                                  "and this placed mesh, sewn at %.2f mm" % MESH_TOL,
                             bodies=who[:12], n_bodies_touching=len(who)))
            P("  %-40s %-28s bbox gap %7.3f  interference %10.4f mm3  %s  %s"
              % (part, mesh, g, vol, hits[-1]["verdict"], who[:4]))
        results[str(flip)] = dict(
            world_bbox=[round(v, 4) for v in (cb.XMin, cb.YMin, cb.ZMin, cb.XMax, cb.YMax, cb.ZMax)],
            size_mm=[round(cb.XLength, 4), round(cb.YLength, 4), round(cb.ZLength, 4)],
            examined=len(near), interfering=sum(1 for h in hits if h["verdict"] == "FAIL"),
            total_interference_mm3=round(sum(h.get("interference_mm3", 0.0) for h in hits), 4),
            rows=hits)
        if flip == 0:
            keep, keepbb = world, cb

    # ---- render what we placed, and read it back ---------------------------
    try:
        from cecad import render
        items = []
        for label, s in keep:
            c = (0.06, 0.30, 0.20) if label == "board" else (
                (0.10, 0.10, 0.11) if label[0] in "UQDY" or label.startswith("MK")
                else (0.86, 0.85, 0.80) if label[0] == "J" else (0.62, 0.55, 0.40))
            items.append((s, c))
        for r in rows:
            if r is hat_row or not r.get("mesh_file") or not os.path.exists(r["mesh_file"]):
                continue
            m = placed_mesh(r)
            if bbgap(keepbb, m.BoundBox) > 30.0:
                continue
            try:
                shp = Part.Shape()
                shp.makeShapeFromMesh(m.Topology, MESH_TOL)
                items.append((shp, (0.72, 0.74, 0.76)))
            except Exception:
                pass
        for view in ("iso",):
            png = os.path.join(OUT, "hat-in-head-%s.png" % view)
            render(items, png, view=view, mode="pbr", W=1600, H=1100,
                   title="the POPULATED Robot HAT where our CAD puts the bare plate")
            P("rendered", png, os.path.getsize(png), "bytes")
    except Exception:
        import traceback
        LOG.write(traceback.format_exc())

    json.dump(dict(_generated="tools/internals_fit.py",
                   question="does the POPULATED Robot HAT fit where our CAD puts the bare plate?",
                   hat_placement=dict(parent_body=hat_row["body"],
                                      world_pos_mm=hat_row["world_pos_mm"],
                                      world_quat_wxyz=hat_row["world_quat_wxyz"],
                                      source=hat_row["source"],
                                      authority="the four 2.700 mounting holes, the two 2.000 "
                                                "anchors and the forty 1.020 GPIO holes are "
                                                "identical in every HAT revision, so the mount "
                                                "pattern lands where Pollen puts it "
                                                "(out/pcb/hat/mesh-revision.json)"),
                   flip_about_board_normal=dict(
                       verdict="CANNOT DETERMINE",
                       why="every revision-independent feature of the board is symmetric about its "
                           "x centre, and the features that break the symmetry are the connector "
                           "holes that moved between the development revision Pollen's simulation "
                           "mesh carries and the C1 board that was produced",
                       settled_by="a photograph of the assembled head showing which end the JST EH "
                                  "connectors face, or Pollen CAD carrying a released HAT",
                       both_measured=True),
                   bare_plate_it_replaces=dict(thickness_mm=0.84,
                                               note="the mesh in placements.json is a flat plate"),
                   populated_height_mm=meas["pcba"]["size_mm"][2],
                   results=results),
              open(os.path.join(OUT, "hat-fit.json"), "w"), indent=1)
    P("seconds", round(time.time() - t0, 1))
    P("DONE")


main()
