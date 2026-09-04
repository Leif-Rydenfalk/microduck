"""tools/hat_step_harvest.py — run under ce-cad/bin/cad (FreeCAD python).

Opens Pollen's OFFICIAL production STEP of the RPI Robot HAT once and harvests
everything geometric from it:

  1. out/pcb/hat/step_components.json  — every component solid in the assembly,
     matched to its designator by position against the manufacturer's own
     pick-and-place, with its MEASURED body bbox and z range.
  2. out/pcb/hat/geometry/<slug>.step  — ONE representative real solid per BOM
     line, moved to a local frame (body centre at x=y=0, board face at z=0,
     placement rotation removed) so it can be a ce-parts geometry file.
  3. out/pcb/hat/geometry/microduck-robot-hat-pcb.step — the bare board body.

MEASURED, NOT MODELLED: every dimension written here is read off the vendor's
own 3D model. Nothing is a nominal from a datasheet table.

Source: reference/pollen-elec-rpi-robot-hat/production/ASE01187-C1_..._STEP.step
(Apache-2.0, commit 23eab119...). The STEP also carries a Raspberry Pi Zero 2 W
below the HAT as context; it is identified and excluded by name.

Run:  ce-cad/bin/cad tools/hat_step_harvest.py   (writes a log; read the log)
"""
import json, math, os, re, time
import FreeCAD as App
import Import
import Part

REPO = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck"
STEP = "/private/tmp/int-pcbchips/step/ASE01187-C1_elec_RPI_Robot_HAT_STEP.step"
OUT = os.path.join(REPO, "out", "pcb", "hat")
GEO = os.path.join(OUT, "geometry")


def slugify(s):
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return re.sub(r"-+", "-", s)


def main():
    os.makedirs(GEO, exist_ok=True)
    comps = json.load(open(os.path.join(OUT, "components.json")))
    # candidates for matching = every footprint that has a body: the 117 fitted
    # placements AND the 9 DNP lands (KiCad exports a 3D model for a DNP part too,
    # so an unmatched DNP model would otherwise be mis-assigned to its neighbour).
    fitted = [c for c in comps["components"] if c["fitted"] or c["dnp"]]

    t0 = time.time()
    doc = App.newDocument("hat")
    Import.insert(STEP, doc.Name)
    doc.recompute()
    print("import seconds", round(time.time() - t0, 1), flush=True)

    shaped = [o for o in doc.Objects if hasattr(o, "Shape") and o.Shape and not o.Shape.isNull()
              and o.Shape.BoundBox.XLength < 1e50]
    # hierarchy: the root is the object no shaped object lists as a child
    child_names = set()
    for o in shaped:
        for c in o.OutList:
            child_names.add(c.Name)
    roots = [o for o in shaped if o.Name not in child_names]
    print("shaped", len(shaped), "roots", [r.Label for r in roots], flush=True)
    root = max(roots, key=lambda o: len(o.Shape.Solids))
    top = [c for c in root.OutList if hasattr(c, "Shape") and c.Shape and not c.Shape.isNull()]
    print("top-level children", len(top), flush=True)

    board = None
    pi = None
    parts = []
    for o in top:
        lab = o.Label
        if lab.startswith("elec_RPI_Robot_HAT_PCB"):
            board = o
        elif "rasp_pi_zero" in lab or "Raspberry" in lab:
            pi = o
        else:
            parts.append(o)
    print("board", board.Label if board else None, "pi", pi.Label if pi else None,
          "component objects", len(parts), flush=True)

    bb = board.Shape.BoundBox
    print("board bbox", [round(v, 4) for v in (bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax)], flush=True)

    # ---- match every component object to a designator ------------------------
    rows = []
    for o in parts:
        s = o.Shape
        b = s.BoundBox
        cx, cy = (b.XMin + b.XMax) / 2.0, (b.YMin + b.YMax) / 2.0
        if b.ZMin >= 0.84:
            side = "top"
        elif b.ZMax <= 0.001:
            side = "bottom"
        else:
            side = "through"
        best, bd = None, 1e9
        for c in fitted:
            if side != "through" and c["pos_side"] != side:
                continue
            d = math.hypot(cx - c["pos_mm"][0], cy - c["pos_mm"][1])
            if d < bd:
                bd, best = d, c
        rows.append(dict(label=o.Label, name=o.Name, side=side,
                         centre=[round(cx, 4), round(cy, 4)],
                         bbox_min=[round(b.XMin, 4), round(b.YMin, 4), round(b.ZMin, 4)],
                         bbox_max=[round(b.XMax, 4), round(b.YMax, 4), round(b.ZMax, 4)],
                         size=[round(b.XLength, 4), round(b.YLength, 4), round(b.ZLength, 4)],
                         solids=len(s.Solids), volume=round(s.Volume, 4) if s.Solids else None,
                         refdes=best["refdes"] if best else None,
                         match_dist_mm=round(bd, 4) if best else None))
    by_ref = {}
    for r in rows:
        if r["refdes"] and r["match_dist_mm"] is not None and r["match_dist_mm"] < 3.5:
            by_ref.setdefault(r["refdes"], []).append(r)
    dup = {k: len(v) for k, v in by_ref.items() if len(v) > 1}
    print("designators matched", len(by_ref), "of", len(fitted), "duplicates", dup, flush=True)
    unmatched = [c["refdes"] for c in fitted if c["refdes"] not in by_ref]
    far = [(r["label"], r["refdes"], r["match_dist_mm"]) for r in rows
           if r["match_dist_mm"] is None or r["match_dist_mm"] > 0.6]
    print("objects further than 0.6 mm from their designator:", far, flush=True)
    print("unmatched designators", unmatched, flush=True)

    json.dump(dict(_generated="tools/hat_step_harvest.py",
                   board_bbox=[round(v, 4) for v in (bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax)],
                   board_thickness_mm=round(bb.ZLength, 4),
                   n_component_objects=len(parts), objects=rows),
              open(os.path.join(OUT, "step_components.json"), "w"), indent=1)

    # ---- export the bare board ----------------------------------------------
    Import.export([board], os.path.join(GEO, "microduck-robot-hat-pcb.step"))
    print("exported board", flush=True)

    # ---- one representative solid per (footprint, value) --------------------
    bomkey = {}
    for c in fitted:
        if c["dnp"]:
            continue
        key = slugify((c.get("bom_value") or c.get("value") or "part") + "-" +
                      (c["footprint"].split(":")[-1]))
        bomkey.setdefault(key, []).append(c)

    exported = {}
    for key, cs in sorted(bomkey.items()):
        c = cs[0]
        objs = by_ref.get(c["refdes"])
        if not objs:
            exported[key] = dict(refdes=c["refdes"], exported=False,
                                 reason="no solid matched this designator in the STEP")
            continue
        o = doc.getObject(objs[0]["name"])
        sh = o.Shape.copy()
        # LOCALISE, with ONE matrix and no Shape.rotate(). The placement that puts a
        # component on the board is P = T(px,py,zref) . Rz(rot) (the z shift commutes
        # with a z rotation), so the local body is P^-1 . X = Rz(-rot) . (X - p - z).
        # Mixing transformShape() with Shape.rotate() writes a file whose geometry is
        # NOT in the local frame — measured, and the reason this block is spelled out.
        rot = c["pos_rot_deg"] or 0.0
        px, py = c["pos_mm"]
        zref = 0.84 if c["pos_side"] == "top" else 0.0
        mt = App.Matrix(); mt.move(App.Vector(-px, -py, -zref))
        mr = App.Matrix(); mr.rotateZ(math.radians(-rot))
        sh.transformShape(mr.multiply(mt), True)
        b3 = sh.BoundBox
        obj = doc.addObject("Part::Feature", "exp_" + key.replace("-", "_")[:40])
        obj.Shape = sh
        obj.Placement = App.Placement()
        path = os.path.join(GEO, key + ".step")
        Import.export([obj], path)
        # READ IT BACK. A file that exists is not a file that is correct.
        chk = Part.Shape(); chk.read(path)
        cb2 = chk.BoundBox
        dev = max(abs(cb2.XMin - b3.XMin), abs(cb2.YMin - b3.YMin), abs(cb2.ZMin - b3.ZMin),
                  abs(cb2.XMax - b3.XMax), abs(cb2.YMax - b3.YMax), abs(cb2.ZMax - b3.ZMax))
        # and put it back where it came from: it must land on the manufacturer's bbox
        back = chk.copy()
        mr2 = App.Matrix(); mr2.rotateZ(math.radians(rot))
        mt2 = App.Matrix(); mt2.move(App.Vector(px, py, zref))
        back.transformShape(mt2.multiply(mr2), True)
        rb = back.BoundBox
        ob = objs[0]
        rt = max(abs(rb.XMin - ob["bbox_min"][0]), abs(rb.YMin - ob["bbox_min"][1]),
                 abs(rb.ZMin - ob["bbox_min"][2]), abs(rb.XMax - ob["bbox_max"][0]),
                 abs(rb.YMax - ob["bbox_max"][1]), abs(rb.ZMax - ob["bbox_max"][2]))
        exported[key] = dict(refdes=c["refdes"], exported=True,
                             instances=[x["refdes"] for x in cs],
                             qty=len(cs), side=c["pos_side"], rot_deg=rot,
                             footprint=c["footprint"], value=c.get("bom_value"),
                             lcsc=c.get("bom_lcsc"),
                             local_bbox=[round(v, 4) for v in (b3.XMin, b3.YMin, b3.ZMin,
                                                               b3.XMax, b3.YMax, b3.ZMax)],
                             size_mm=[round(b3.XLength, 4), round(b3.YLength, 4), round(b3.ZLength, 4)],
                             volume_mm3=round(sh.Volume, 4) if sh.Solids else None,
                             solids=len(sh.Solids),
                             file_readback_dev_mm=round(dev, 6),
                             round_trip_dev_mm=round(rt, 6))
        print("exported", key, exported[key]["size_mm"], "qty", len(cs),
              "readback", exported[key]["file_readback_dev_mm"],
              "roundtrip", exported[key]["round_trip_dev_mm"], flush=True)

    json.dump(dict(_generated="tools/hat_step_harvest.py", parts=exported),
              open(os.path.join(OUT, "geometry_index.json"), "w"), indent=1)
    worst_rt = max((v.get("round_trip_dev_mm", 0) for v in exported.values() if v["exported"]), default=None)
    print("DONE parts exported", sum(1 for v in exported.values() if v["exported"]),
          "of", len(exported), "worst round trip mm", worst_rt, flush=True)
    open(os.path.join(OUT, "harvest.log"), "w").write(
        "exported %d of %d; worst file-readback dev %.6f mm; worst round-trip dev %.6f mm\n"
        % (sum(1 for v in exported.values() if v["exported"]), len(exported),
           max((v.get("file_readback_dev_mm", 0) for v in exported.values() if v["exported"]), default=-1),
           worst_rt if worst_rt is not None else -1))


main()
