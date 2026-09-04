#!/usr/bin/env python3
"""screw_mass.py — MEASURE the mass of every placed fastener from its BUILT SOLID.

    ce-cad/bin/cad tools/screw_mass.py   ->  out/open/screw-volumes.json

Why measured and not computed from the ISO table: the part is a real solid with
a hex socket sunk into its head and a chamfer under it, so head cylinder + shank
cylinder OVERSTATES it. The kernel's Shape.Volume is the only figure that knows
what the geometry actually is. Density is the one number that is NOT measured
here and it says so on the row.
"""
import os, json, traceback, time
ROOT = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck"
os.environ.setdefault("CE_TRIAD_ROOT", ROOT + ":/Users/leifrydenfalk/dev/ce-workshop")
LOG = open(os.environ.get("MD_SCREWMASS_LOG", ROOT + "/out/open/screw-volumes.log"), "w", buffering=1)
def p(*a): LOG.write(" ".join(str(x) for x in a) + "\n"); LOG.flush()

# ISO 4762 is a steel fastener. Property class 8.8 / A2-70 are both steel; the
# density band below is the ONE unmeasured input and both ends are carried
# through to a mass band rather than averaged into a single figure.
DENSITY = {
    "carbon_steel_8.8":  7.85,   # g/cm3, ISO 898-1 class 8.8 plain steel, the default fastener material
    "stainless_A2":      7.90,   # g/cm3, ISO 3506-1 A2-70 austenitic
}

try:
    t0 = time.time()
    import FreeCAD as App
    import cecad.triad as triad
    doc = App.newDocument("screwmass")
    rows = json.load(open(ROOT + "/ce-assemblies/microduck/current/placements.json"))["record"]["rows"]
    fast = [r for r in rows if r.get("via_connection")]
    p("fastener rows:", len(fast))
    members = {}
    for r in fast:
        ref = r["part"]; prm = r.get("params") or {}
        key = (ref, tuple(sorted(prm.items())))
        members.setdefault(key, 0)
        members[key] += 1
    p("distinct members:", len(members))
    out = {"$what": "volume of every placed fastener member, read off the built solid",
           "$generated_by": "tools/screw_mass.py",
           "density_g_cm3": DENSITY,
           "density_note": "NOT measured here. Both ends of the steel band are carried to a mass band.",
           "members": [], "totals": {}}
    tot_v = 0.0; n = 0
    for (ref, prm), count in sorted(members.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        s = triad.load(doc, ref, dict(prm))
        doc.recompute()
        shp = s
        for attr in ("Shape", "shape", "solid", "obj"):
            if hasattr(shp, attr):
                cand = getattr(shp, attr)
                if hasattr(cand, "Volume"):
                    shp = cand; break
        if not hasattr(shp, "Volume"):
            p("  NO VOLUME on %r; dir=%s" % (ref, [a for a in dir(s) if not a.startswith("_")][:40]))
            raise SystemExit(0)
        v = shp.Volume            # mm3
        bb = shp.BoundBox
        row = {"part": ref, "params": dict(prm), "instances": count,
               "volume_mm3": round(v, 6),
               "bbox_mm": [round(bb.XLength, 4), round(bb.YLength, 4), round(bb.ZLength, 4)],
               "mass_g_each": {k: round(v * d / 1000.0, 6) for k, d in DENSITY.items()},
               "mass_g_total": {k: round(v * d / 1000.0 * count, 6) for k, d in DENSITY.items()}}
        out["members"].append(row)
        tot_v += v * count; n += count
        p("  %-28s %-20s x%-3d  V=%.4f mm3  m=%.5f g (8.8)" % (ref, prm, count, v, v * 7.85 / 1000.0))
    out["totals"] = {"instances": n, "volume_mm3": round(tot_v, 4),
                     "mass_g": {k: round(tot_v * d / 1000.0, 5) for k, d in DENSITY.items()}}
    p("TOTAL %d fasteners, %.4f mm3, %.5f g (8.8) .. %.5f g (A2)"
      % (n, tot_v, tot_v * 7.85 / 1000.0, tot_v * 7.90 / 1000.0))
    os.makedirs(ROOT + "/out/open", exist_ok=True)
    json.dump(out, open(ROOT + "/out/open/screw-volumes.json", "w"), indent=1)
    p("DONE in %.1f s" % (time.time() - t0))
except Exception:
    p("RAISED:\n" + traceback.format_exc())
