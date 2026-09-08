"""tools/render_fastener_regions.py — the 64 screws IN SITU, region by region.

tools/build_fastener_skeleton.py renders all 64 screws alone and
cecad.render.verify_render REFUSES the picture, correctly: 64 objects ~4 mm
across in a 300 mm frame leave no continuous mark over 10 % of the frame, so
by that check the image is indistinguishable from lettering on an empty
canvas. The previous run recorded the refusal and said the PNG had been read
by eye anyway. That is a picture nobody's instrument agrees is a picture.

The fix is not to switch the check off. It is to render what a person
actually needs to see — each screw beside the parts it fastens, at a scale
where both are legible. cecad's own rule is to inspect a connection as a
PAIR, and a region view is that rule applied to fastening: the frame is the
region's own bounding box, so the screws are large in it and the check
passes on its own terms.

Every region render is then READ BACK by verify_render, and the verdict per
region goes into out/fasteners/regions.json with the counts behind it.

Run:  ce-cad/bin/cad tools/render_fastener_regions.py
      log -> out/fasteners/regions-render.log   (bin/cad buffers stdout)
"""
import json
import os
import time
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("CE_TRIAD_ROOT",
                      ROOT + ":/Users/leifrydenfalk/dev/ce-workshop")
LOGPATH = os.environ.get("MD_REGION_LOG",
                         os.path.join(ROOT, "out/fasteners/regions-render.log"))
os.makedirs(os.path.dirname(LOGPATH), exist_ok=True)
LOG = open(LOGPATH, "w", buffering=1)


def p(*a):
    LOG.write(" ".join(str(x) for x in a) + "\n")
    LOG.flush()


# The regions are named by the MESHES in them, taken from the assembly's own
# placement rows — not by typed coordinates. A screw belongs to a region when
# either the mesh its head seats on or the mesh its pilot is in belongs there.
REGIONS = {
    "hip-left": ["hip_l", "yaw2roll", "upper_leg_left", "xl330"],
    # "legs" covers BOTH legs. It was "leg-left" and the coverage count
    # caught the gap: 5 of the 64 screws join ankle_right / foot_right and no
    # region named those meshes, so 5 screws would have appeared in no
    # picture at all. Widened rather than left undrawn.
    "legs": ["leg", "ankle_left", "foot_left", "sole_left",
             "ankle_right", "foot_right", "sole_right",
             "upper_leg_rigidity_plate", "xl330"],
    "head": ["top_head_shell", "bottom_head_shell", "face_part", "neck_pitch",
             "neck", "m12_lens_holder", "noenoeil", "jaw", "xl330"],
    "trunk": ["trunk_base", "power_support", "left_shell", "right_shell",
              "motor_support", "yaw_roll_motion", "bearing_roll", "xl330"],
}


def main():
    import FreeCAD as App
    from cecad import triad
    from cecad.core import Assembly, Part
    from cecad.render import render, verify_render

    t0 = time.time()
    doc = App.newDocument("regions")
    place = json.load(open(os.path.join(
        ROOT, "ce-assemblies/microduck/current/placements.json")))["record"]
    rows = place["rows"]
    parts = [r for r in rows if r.get("mesh")]
    fast = [r for r in rows if r.get("part", "").startswith("part:screw-")]
    p("placement rows %d  = part rows %d + fastener rows %d"
      % (len(rows), len(parts), len(fast)))

    def d2(a, b):
        return sum((a[k] - b[k]) ** 2 for k in (0, 1, 2))

    anchors = {reg: [r["world_pos_mm"] for r in parts
                     if r["mesh"] in set(ms) - {"xl330"}]
               for reg, ms in REGIONS.items()}
    servo_region = {}
    for r in parts:
        if r["mesh"] != "xl330":
            continue
        best, bestd = None, None
        for reg, pts in anchors.items():
            if not pts:
                continue
            dd = min(d2(r["world_pos_mm"], q) for q in pts)
            if bestd is None or dd < bestd:
                best, bestd = reg, dd
        servo_region[id(r)] = best
    p("servos assigned by nearest anchor: " + json.dumps(
        {reg: sum(1 for v in servo_region.values() if v == reg)
         for reg in REGIONS}) + "  total %d" % len(servo_region))

    out = {}
    shown = set()
    scache, mcache = {}, {}
    for region, meshes in REGIONS.items():
        a = Assembly("region_" + region.replace("-", "_"))
        want = set(meshes)
        np_ = ns = 0
        # THE SERVO ASSIGNMENT, and why it is not a tuned radius. Every
        # region has servos in it and the robot places the ONE xl330 mesh 15
        # times, so filtering part rows by mesh NAME alone drew all 15 servos
        # in all four regions — the first hip-left render spread boxes over
        # the whole height of the machine. A padded bounding box would work
        # but the pad is a knob, and sweeping it to the count that "looks
        # right" is fitting to expectation. Instead every servo instance is
        # assigned to the region whose non-servo parts it is CLOSEST to. That
        # partitions the 15 exactly: each servo appears once, in one region,
        # and the four counts sum to 15 by construction rather than by choice.
        for r in parts:
            if r["mesh"] not in want:
                continue
            if r["mesh"] == "xl330" and servo_region.get(id(r)) != region:
                continue
            f = r.get("mesh_file")
            if not f or not os.path.exists(f):
                p("  %s: mesh file missing for %s" % (region, r["mesh"]))
                continue
            if f not in mcache:
                mcache[f] = Part.from_mesh(f, scale=1000.0)
            w, x, y, z = r["world_quat_wxyz"]
            rot = App.Rotation(App.Vector(0, 0, 1), 0)
            rot.Q = (x, y, z, w)
            a.add("%s#%d" % (r["mesh"], r.get("geom_index", 0)), mcache[f],
                  at=tuple(r["world_pos_mm"]), rot=rot)
            np_ += 1
        for i, r in enumerate(fast):
            # placements.json names the meshes a screw joins in `joins`.
            # The first draft read head_seat_mesh / pilot_mesh / meshes —
            # the key names out/fasteners/placed.json uses, not the ones the
            # assembly record uses — so the filter matched nothing and the
            # run drew 0 of 64 screws while reporting four PASSing renders.
            # A render that passes every check and shows none of the subject
            # is exactly the failure the counts exist to catch.
            touch = set(r.get("joins") or [])
            touch |= {r.get("head_seat_mesh"), r.get("pilot_mesh")}
            touch |= set(r.get("meshes") or [])
            touch.discard(None)
            # a screw counts for this region only when it touches a mesh that
            # is NOT the xl330 — every region lists the servo, so keying on it
            # would put all 52 servo screws in all four regions.
            if not (touch & (want - {"xl330"})):
                continue
            ref, prm = r["part"], (r.get("params") or {})
            key = (ref, tuple(sorted(prm.items())))
            if key not in scache:
                scache[key] = triad.load(doc, ref, prm)
            w, x, y, z = r["world_quat_wxyz"]
            rot = App.Rotation(App.Vector(0, 0, 1), 0)
            rot.Q = (x, y, z, w)
            a.add("screw#%d" % i, scache[key], at=tuple(r["world_pos_mm"]),
                  rot=rot, joint="screwed")
            ns += 1
            shown.add(i)
        doc.recompute()
        png = os.path.join(ROOT, "out/fasteners/region-%s.png" % region)
        rec = {"parts_placed": np_, "screws_placed": ns, "png": png}
        try:
            render(a, png, view="iso")
            rec["render_verdict"] = "PASS"
            rec["verified"] = verify_render(png)
        except Exception as e:                       # noqa: BLE001
            rec["render_verdict"] = "FAIL"
            rec["render_refusal"] = "%s: %s" % (type(e).__name__, e)
        p("%-10s parts %2d screws %2d -> %s" % (region, np_, ns,
                                                rec["render_verdict"]))
        if rec.get("render_refusal"):
            p("           %s" % rec["render_refusal"][:160])
        out[region] = rec

    doc_json = {
        "doc": {"id": "MD-FASTREGION-001", "rev": "A",
                "title": "The 64 placed screws IN SITU, four regions, each "
                         "render read back by the instrument that refused the "
                         "whole-machine one",
                "generated_by": "tools/render_fastener_regions.py"},
        "a_misreading_recorded": "The first hip-left render was read as '20 "
            "coarse boxes, no real geometry' — i.e. as a broken render. That "
            "reading was WRONG and a two-part control settled it: the hip "
            "bracket draws as a real curved bracket with its bores, and the "
            "XL330 servo genuinely IS a rectangular box with a round output "
            "horn on one face. The boxes were correct parts. What the picture "
            "did show was a defect in THIS tool, not in the kernel: all 15 "
            "servo instances were drawn in all four regions because every "
            "region names the mesh. Hence the proximity filter above.",
        "why": "cecad.render.verify_render REFUSED the all-64-screws render "
               "and was right to: a cloud of 4 mm objects in a 300 mm frame "
               "has no continuous mark over 10 % of the frame. The answer is "
               "not to disable the check but to frame the picture a reader "
               "needs — screws beside the parts they fasten, at a scale where "
               "both are legible.",
        "regions": out,
        "counts": {
            "regions": len(out),
            "renders_PASS": sum(1 for r in out.values()
                                if r["render_verdict"] == "PASS"),
            "renders_FAIL": sum(1 for r in out.values()
                                if r["render_verdict"] == "FAIL"),
            "screws_shown": sum(r["screws_placed"] for r in out.values()),
            "screws_total": len(fast),
            "distinct_screws_shown": len(shown),
            "screws_in_no_region": len(fast) - len(shown),
        },
        "seconds": round(time.time() - t0, 1),
    }
    with open(os.path.join(ROOT, "out/fasteners/regions.json"), "w") as fh:
        json.dump(doc_json, fh, indent=1)
    p("COUNTS " + json.dumps(doc_json["counts"]))
    p("DONE in %.1f s" % (time.time() - t0))


try:
    main()
except Exception:
    p("RAISED:\n" + traceback.format_exc())
