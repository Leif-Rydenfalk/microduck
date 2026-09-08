#!/usr/bin/env -S /Users/leifrydenfalk/dev/ce-workshop/ce-cad/bin/cad
"""tools/fastener_hips_trunk.py — the fastener census for region hips-trunk.

Owned by the hips-trunk fastener lane (see out/fasteners/census-hips-trunk.json
$owned_paths). Every step writes its result to disk BEFORE the next starts so
a kill leaves the measurements on disk (three previous runs of this lane were
lost to restarts).

    bin/cad tools/fastener_hips_trunk.py measure   [mesh ...]  -> out/fasteners/raw/<mesh>.features.json
    bin/cad tools/fastener_hips_trunk.py rebuild   [slug ...]  -> out/fasteners/raw/<slug>.rebuild-holes.json
    bin/cad tools/fastener_hips_trunk.py reconcile            -> census parts[].features (mesh vs rebuild)
    bin/cad tools/fastener_hips_trunk.py mate                 -> census mates + fasteners
    bin/cad tools/fastener_hips_trunk.py render               -> out/fasteners/hips-trunk/<mesh>-features.png

Instrument: cecad.meshfeatures.features() (dihedral patches + cylinder fit +
24 axis-parallel probe rays per hole for through/blind, coaxial counterbore
relation, sphere fit for ball sockets). Every number in the output carries
"method" so a stranger can re-take it.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "..", "ce-cad"))
sys.path.insert(0, "/Users/leifrydenfalk/dev/ce-workshop/ce-cad")

CENSUS = os.path.join(ROOT, "out", "fasteners", "census-hips-trunk.json")
RAW = os.path.join(ROOT, "out", "fasteners", "raw")
OUTDIR = os.path.join(ROOT, "out", "fasteners", "hips-trunk")

# part -> (mesh name, stl paths to measure; the first is the assembly's)
PARTS = {
    "part:microduck-hip-bracket": ("hip_l", ["reference/pollen-microduck-rl/assets/hip_l.stl"]),
    "part:microduck-yaw2roll": ("yaw2roll", ["reference/pollen-microduck-rl/assets/yaw2roll.stl"]),
    "part:microduck-yaw-roll-motion": ("yaw_roll_motion", ["reference/pollen-microduck-rl/assets/yaw_roll_motion.stl",
                                                            "reference/pollen-microduck-simulator/meshes/yaw_roll_motion.stl"]),
    "part:microduck-bearing-roll": ("bearing_roll", ["reference/pollen-microduck-rl/assets/bearing_roll.stl"]),
    "part:microduck-trunk-base": ("trunk_base", ["reference/pollen-microduck-rl/assets/trunk_base.stl"]),
    "part:microduck-trunk-shell-left": ("left_shell", ["reference/pollen-microduck-rl/assets/left_shell.stl"]),
    "part:microduck-trunk-shell-right": ("right_shell", ["reference/pollen-microduck-rl/assets/right_shell.stl"]),
    "part:microduck-power-support": ("power_support", ["reference/pollen-microduck-rl/assets/power_support.stl"]),
    "part:microduck-banana-pcb-locker": ("banana_pcb_locker", ["reference/pollen-microduck-rl/assets/banana_pcb_locker.stl"]),
}


def load_census():
    with open(CENSUS) as f:
        return json.load(f)


def save_census(c, status=None, checkpoint=None):
    if status:
        c["status"] = status
    if checkpoint:
        c.setdefault("checkpoints", []).append({"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "what": checkpoint})
    tmp = CENSUS + ".tmp"
    with open(tmp, "w") as f:
        json.dump(c, f, indent=1)
    os.replace(tmp, CENSUS)


def stl_scale(path):
    """Pollen's STLs are in metres; a bbox under 1 unit says so. MEASURED, not assumed."""
    import numpy as np
    from cecad import mjcf
    T = np.asarray(mjcf.read_stl(path), dtype=float)
    ext = T.reshape(-1, 3).max(0) - T.reshape(-1, 3).min(0)
    return (1000.0 if ext.max() < 1.0 else 1.0), [round(float(x), 6) for x in ext], int(len(T))


def cmd_measure(names):
    from cecad import meshfeatures
    todo = [(p, m, s) for p, (m, stls) in PARTS.items() for s in stls if not names or m in names or p in names]
    for part, mesh, rel in todo:
        path = os.path.join(ROOT, rel)
        tag = mesh if "microduck-rl" in rel else mesh + ".simulator"
        out = os.path.join(RAW, tag + ".features.json")
        t0 = time.time()
        scale, ext, ntri = stl_scale(path)
        print("measuring %s (%d tris, scale x%g, extent %s)" % (rel, ntri, scale, [round(e * scale, 3) for e in ext]), flush=True)
        r = meshfeatures.features(path, scale=scale)
        r["$what"] = "cecad.meshfeatures.features() on %s — every cylindrical patch (dihedral < 35 deg) fitted, ends probed by 24 rays, counterbores as coaxial relations, spheres fitted" % rel
        r["$source_stl"] = rel
        r["$scale"] = scale
        r["$extent_mm"] = [round(e * scale, 4) for e in ext]
        r["$part"] = part
        r["$measured_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        r["$seconds"] = round(time.time() - t0, 1)
        with open(out, "w") as f:
            json.dump(r, f, indent=1)
        print("  -> %s: %d holes, %d bosses, %d partial arcs, %d spheres, %d rejected (%.1fs)" % (
            os.path.relpath(out, ROOT), len(r["holes"]), len(r["bosses"]), len(r["partial_arcs"]),
            len(r["spheres"]), len(r["rejected"]), r["$seconds"]), flush=True)
        for h in r["holes"]:
            print("    hole d=%.3f len=%.3f axis=%s c=%s %s | %s" % (h["d_mm"], h["length_mm"], h["axis"], h["center_mm"], h["role"], h["reading"]["reads_as"]))
        for b in r["bosses"]:
            print("    boss d=%.3f len=%.3f axis=%s c=%s %s" % (b["d_mm"], b["length_mm"], b["axis"], b["center_mm"], b["role"]))
        for s in r["spheres"]:
            print("    SPHERE %s r=%.4f c=%s resid=%.4f cover=%.3f" % (s["kind"], s["r_mm"], s["center_mm"], s["residual_mm"], s["cover"]))
        # checkpoint into the census straight away
        c = load_census()
        pc = c["parts"].setdefault(part, {})
        pc.setdefault("raw", {})[tag] = os.path.relpath(out, ROOT)
        pc["mesh_counts_%s" % tag] = r["counts"]
        pc["status"] = "mesh measured (%s); rebuild/reconcile/mate pending" % tag
        save_census(c, status="measuring Pollen meshes: %s done" % tag,
                    checkpoint="measured %s: %d holes %d bosses %d spheres" % (tag, len(r["holes"]), len(r["bosses"]), len(r["spheres"])))


REBUILD_SLUG = {p: p.split(":", 1)[1] for p in PARTS}


def cmd_rebuild(names):
    """Build each part's OWN parametric solid and measure its internal
    cylinders and external bosses with cecad.inspect — the B side of the
    reconciliation. A feature in the mesh and not in the rebuild (or the
    other way round) is a FINDING, not a rounding error."""
    import FreeCAD
    from cecad import triad, inspect as insp
    todo = [(p, m) for p, (m, _s) in PARTS.items() if not names or m in names or p in names
            or p.split(":", 1)[1] in names]
    for part_ref, mesh in todo:
        slug = part_ref.split(":", 1)[1]
        out = os.path.join(RAW, slug + ".rebuild-holes.json")
        t0 = time.time()
        rec = {"$what": "cecad.inspect.holes/shafts on the PARAMETRIC rebuild %s"
                        " (ce-parts/%s/current/cad/part.py), for reconciliation against"
                        " Pollen's mesh %s" % (part_ref, slug, mesh),
               "$part": part_ref, "$mesh": mesh,
               "$builder": "ce-parts/%s/current/cad/part.py" % slug,
               "$measured_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
        try:
            doc = FreeCAD.newDocument("fx_" + slug.replace("-", "_"))
            obj = triad.load(doc, part_ref)
            shape = getattr(obj, "shape", None) or getattr(obj, "Shape", None)
            bb = shape.BoundBox
            rec["bbox_mm"] = {"min": [round(bb.XMin, 4), round(bb.YMin, 4), round(bb.ZMin, 4)],
                              "max": [round(bb.XMax, 4), round(bb.YMax, 4), round(bb.ZMax, 4)],
                              "size": [round(bb.XLength, 4), round(bb.YLength, 4), round(bb.ZLength, 4)]}
            rec["volume_mm3"] = round(shape.Volume, 4)
            rec["faces"] = len(shape.Faces)
            rec["valid"] = bool(shape.isValid())
            hs = []
            for h in insp.holes(obj, min_d=0.8, max_d=60.0, round_to=4):
                hs.append({"d_mm": round(h.d, 4), "axis": [round(x, 6) for x in h.axis],
                           "center_mm": [round(x, 4) for x in h.center],
                           "depth_mm": round(h.depth, 4), "through_envelope": bool(h.through),
                           "kind": h.kind, "ends": list(h.ends),
                           "blind": h.blind, "coverage_deg": round(h.coverage_deg, 2),
                           "span_mm": (round(h.span, 4) if h.span else None),
                           "of_group": h.of_group,
                           "csk": ([round(h.csk[0], 4), round(h.csk[1], 2)] if h.csk else None),
                           "text": str(h)})
            rec["holes"] = hs
            ss = []
            for sh in insp.shafts(obj, min_d=0.8, max_d=60.0, round_to=4):
                ss.append({"d_mm": round(sh.d, 4), "axis": [round(x, 6) for x in sh.axis],
                           "center_mm": [round(x, 4) for x in sh.center],
                           "length_mm": round(sh.length, 4),
                           "coverage_deg": round(sh.coverage_deg, 2), "text": str(sh)})
            rec["shafts"] = ss
            rec["method"] = ("cecad.inspect.holes(min_d=0.8) — every internal cylindrical FACE of"
                             " the B-rep, coaxial runs split at air, ends classified open/closed/"
                             "obstructed by solid probes; cecad.inspect.shafts for external cylinders")
            rec["ok"] = True
            FreeCAD.closeDocument(doc.Name)
        except Exception as exc:  # a failed rebuild is itself the finding
            import traceback
            rec["ok"] = False
            rec["error"] = "%s: %s" % (type(exc).__name__, exc)
            rec["traceback"] = traceback.format_exc()[-2000:]
        rec["$seconds"] = round(time.time() - t0, 1)
        with open(out, "w") as f:
            json.dump(rec, f, indent=1)
        print("%s -> %s (%s, %d holes, %d shafts, %.1fs)" % (
            slug, os.path.relpath(out, ROOT), "OK" if rec["ok"] else rec.get("error", "FAIL"),
            len(rec.get("holes", [])), len(rec.get("shafts", [])), rec["$seconds"]), flush=True)
        c = load_census()
        pc = c["parts"].setdefault(part_ref, {})
        pc.setdefault("raw", {})["rebuild"] = os.path.relpath(out, ROOT)
        pc["rebuild_ok"] = rec["ok"]
        save_census(c, checkpoint="rebuild measured %s: %s" % (
            slug, ("%d holes %d shafts" % (len(rec.get("holes", [])), len(rec.get("shafts", []))))
            if rec["ok"] else rec.get("error")))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "measure"
    if cmd == "measure":
        cmd_measure(sys.argv[2:])
    elif cmd == "rebuild":
        cmd_rebuild(sys.argv[2:])
    else:
        print("unknown command", cmd)
        sys.exit(2)
