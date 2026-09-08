#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""collision_model.py — what CAN collide in the Microduck MJCF, measured, and two
derived model variants that make the missing questions answerable.

WHY THIS EXISTS (lane F2 skeptic findings 2 and 3, 2026-09-02)
--------------------------------------------------------------
Two F2 claims were measured to be weaker than they read:

  * "the walk on the model that has EVERY body's collision geom enabled"
    (out/sim-sweep/walk_allcollisions.json field `note`) is FALSE for
    sim/microduck_ours_allcollisions.xml — only some bodies carry a
    class="collision" geom there.
  * "no self-collision occurred" in the upright locomotion cells was measured on
    sim/microduck_ours.xml, where only THREE geoms are allowed to self-collide
    at all (class="self_collision_only", contype/conaffinity 2). Head, feet,
    hips, ankles, trunk and the two upper legs cannot self-collide in that
    model, so the census answered a much smaller question than it stated.

This module answers both by MEASURING the compiled model rather than reading the
XML by eye, and by generating two variants in which the question is real:

  ours_selfcontact  every geom of every body gets contype=2 conaffinity=2, i.e.
                    it can touch any other body but NOT the floor. The floor
                    interaction (floor contype=1/conaffinity=1 vs the two soles
                    contype=1/conaffinity=1) is left EXACTLY as in
                    sim/microduck_ours.xml, so the gait is unchanged unless the
                    robot genuinely touches itself. This is the honest census
                    model.

  ours_fullcontact  every geom gets contype=3 conaffinity=3, i.e. it collides
                    with the floor AND with the rest of the robot. Used to ask
                    what a fall actually does when the body cannot pass through
                    the floor plane.

MuJoCo's collision filter (Computation -> Collision detection):
  a pair is checked iff  (contype1 & conaffinity2) || (contype2 & conaffinity1),
  the two geoms are not in the same body, and (flag filterparent, enabled by
  default) they are not in a parent/child body pair.
Both conditions are evaluated here from the COMPILED model, not from the XML
text, so a class default that the compiler resolved differently cannot hide.

Run:
  ce-cad/bin/cad sim/collision_model.py --write          # write the two variants
  ce-cad/bin/cad sim/collision_model.py --census         # census every model
"""
import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

ROOT = common.ROOT
HERE = os.path.dirname(os.path.abspath(__file__))
EVID = os.path.join(ROOT, "out", "sim-evidence")

VARIANTS = {
    # name: (source xml, contype, conaffinity, what it is for)
    "microduck_ours_selfcontact.xml": (
        "microduck_ours.xml", 2, 2,
        "every geom can touch every other non-adjacent body; floor contact left exactly as "
        "microduck_ours.xml (only the two soles). The self-collision census model."),
    "microduck_ours_fullcontact.xml": (
        "microduck_ours.xml", 3, 3,
        "every geom collides with the floor AND with the rest of the robot. Answers what a fall "
        "does when the body cannot pass through the floor plane."),
}
# the two geoms that must keep floor contact in the selfcontact variant
FLOOR_GEOMS = ("left_foot_collision", "right_foot_collision")


def write_variants(verbose=True, excludes=None):
    """Rewrite every <geom> under <worldbody> with an explicit contype/conaffinity.

    An explicit attribute on the element overrides the class default, so this needs
    no change to the <default> blocks and leaves meshes, poses, materials, inertials,
    joints and actuators byte-for-byte identical.

    `excludes` maps a variant filename to a list of (body1, body2) pairs to write into
    a <contact><exclude/></contact> block. It is not a guess: it is filled from the
    MEASURED rest-pose overlap in the first pass of write_and_clean()."""
    excludes = excludes or {}
    written = []
    for dst, (src, ct, ca, why) in VARIANTS.items():
        tree = ET.parse(os.path.join(HERE, src))
        root = tree.getroot()
        wb = root.find("worldbody")
        n = 0
        for g in wb.iter("geom"):
            name = g.get("name")
            if dst.endswith("selfcontact.xml") and name in FLOOR_GEOMS:
                g.set("contype", "3")        # floor (1) + self (2)
                g.set("conaffinity", "3")
            else:
                g.set("contype", str(ct))
                g.set("conaffinity", str(ca))
            n += 1
        exc = sorted(set(tuple(sorted(e)) for e in excludes.get(dst, [])))
        if exc:
            for old_c in root.findall("contact"):
                root.remove(old_c)
            cn = ET.SubElement(root, "contact")
            for i, (b1, b2) in enumerate(exc):
                ET.SubElement(cn, "exclude", name="hull_artifact_%d" % i, body1=b1, body2=b2)
        out = os.path.join(HERE, dst)
        txt = ET.tostring(root, encoding="unicode")
        txt = ('<?xml version="1.0" ?>\n<!-- GENERATED by sim/collision_model.py from sim/%s — '
               'do not hand-edit.\n     %s\n     %d worldbody geoms given explicit '
               'contype/conaffinity. -->\n' % (src, why, n)) + txt
        with open(out, "w") as f:
            f.write(txt)
        written.append({"file": "sim/" + dst, "from": "sim/" + src, "geoms_rewritten": n,
                        "contype": ct, "conaffinity": ca, "purpose": why,
                        "contact_excludes": ["%s <-> %s" % e for e in exc]})
        if verbose:
            print("wrote sim/%s  (%d geoms, contype=%d conaffinity=%d)" % (dst, n, ct, ca))
    return written


def write_and_clean(verbose=True):
    """Two passes, so the exclusion list is MEASURED and not asserted.

    Pass 1 writes the variants with every geom collidable and measures which body pairs
    are ALREADY interpenetrating in the STAND rest pose. Those are convex-hull overlap
    between neighbouring parts (MuJoCo collides the convex hull of a mesh, so a part
    correctly nested inside another part's concave shell reads as penetration) and they
    inject a large spurious contact force — measured at up to 179.73 N on the head in
    pass 1, which would make the variant a different robot rather than the same robot
    with a bigger question asked of it.

    Pass 2 rewrites the variants with a <contact><exclude/></contact> for exactly those
    body pairs, then RE-MEASURES and refuses to return unless the rest pose is clean."""
    write_variants(verbose=verbose)
    found, exc = {}, {}
    for dst, robot in (("microduck_ours_selfcontact.xml", "ours_selfcontact"),
                       ("microduck_ours_fullcontact.xml", "ours_fullcontact")):
        r = rest_pose_overlap(robot)
        found[robot] = r
        pairs = []
        for k in r["settled"]["pairs"]:
            b1, b2 = [side.split("/")[0] for side in k.split(" <-> ")]
            pairs.append((b1, b2))
        exc[dst] = pairs
        if verbose:
            print("pass 1 %-18s rest-pose overlapping body pairs: %s"
                  % (robot, sorted(set(tuple(sorted(p)) for p in pairs)) or "none"))
    written = write_variants(verbose=verbose, excludes=exc)
    clean = {}
    for robot in ("ours_selfcontact", "ours_fullcontact"):
        r = rest_pose_overlap(robot)
        clean[robot] = r
        left = r["settled"]["pairs"]
        if verbose:
            print("pass 2 %-18s rest-pose overlap after exclusion: %s"
                  % (robot, list(left) or "none — clean"))
        assert not left, ("rest-pose overlap survived the exclusion in %s: %s" % (robot, left))
    return {"written": written, "pass1_rest_overlap": found, "pass2_rest_overlap": clean}


def census(robot):
    """Compile the model and MEASURE, per geom, what it is allowed to touch."""
    import mujoco
    model, scene = common.load_model(robot, os.path.join(ROOT, "out", "sim-sweep", "_census",
                                                         "scene_%s.xml" % robot))
    gname = [mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_GEOM, i) for i in range(model.ngeom)]
    bname = [mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_BODY, int(model.geom_bodyid[i]))
             for i in range(model.ngeom)]
    floor = gname.index("floor")
    fct, fca = int(model.geom_contype[floor]), int(model.geom_conaffinity[floor])

    geoms, bodies = [], {}
    for i in range(model.ngeom):
        if i == floor:
            continue
        ct, ca = int(model.geom_contype[i]), int(model.geom_conaffinity[i])
        hits_floor = bool((ct & fca) or (fct & ca))
        self_cap = bool(ct & ca) or ct != 0 or ca != 0
        # a geom can take part in a robot-robot contact iff it can pair with SOME other
        # robot geom under the mask rule; measured pairwise below rather than assumed
        geoms.append({"geom": gname[i] or "(unnamed #%d)" % i, "body": bname[i],
                      "contype": ct, "conaffinity": ca,
                      "can_contact_floor": hits_floor})
        b = bodies.setdefault(bname[i], {"geoms": 0, "floor_capable": 0, "self_capable": 0})
        b["geoms"] += 1
        b["floor_capable"] += int(hits_floor)

    # pairwise mask test between robot geoms in different, non-parent/child, non-EXCLUDED bodies
    pairs = 0
    self_capable_bodies = set()
    par = model.body_parentid
    excluded = set()
    for e in range(int(model.nexclude)):
        sig = int(model.exclude_signature[e])
        excluded.add(tuple(sorted(((sig >> 16) & 0xFFFF, sig & 0xFFFF))))
    for i in range(model.ngeom):
        if i == floor:
            continue
        for j in range(i + 1, model.ngeom):
            if j == floor:
                continue
            bi, bj = int(model.geom_bodyid[i]), int(model.geom_bodyid[j])
            if bi == bj:
                continue
            if par[bi] == bj or par[bj] == bi:      # filterparent (enabled by default)
                continue
            if tuple(sorted((bi, bj))) in excluded:  # <contact><exclude/></contact>
                continue
            ci, ai = int(model.geom_contype[i]), int(model.geom_conaffinity[i])
            cj, aj = int(model.geom_contype[j]), int(model.geom_conaffinity[j])
            if (ci & aj) or (cj & ai):
                pairs += 1
                self_capable_bodies.add(bname[i])
                self_capable_bodies.add(bname[j])
    for b in bodies:
        bodies[b]["self_capable"] = int(b in self_capable_bodies)

    all_bodies = [mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_BODY, i) for i in range(model.nbody)]
    robot_bodies = [b for b in all_bodies if b not in (None, "world")]
    return {
        "robot": robot,
        "robot_file": os.path.relpath(common.robot_file(robot), ROOT),
        "scene_file": os.path.relpath(scene, ROOT),
        "compiled_geoms_total": model.ngeom,
        "compiled_geoms_robot": model.ngeom - 1,
        "bodies_total": len(robot_bodies),
        "floor": {"contype": fct, "conaffinity": fca},
        "geoms_that_can_contact_the_floor": sorted(g["geom"] for g in geoms if g["can_contact_floor"]),
        "n_geoms_that_can_contact_the_floor": sum(g["can_contact_floor"] for g in geoms),
        "bodies_that_can_contact_the_floor": sorted(b for b, v in bodies.items() if v["floor_capable"]),
        "bodies_that_CANNOT_contact_the_floor": sorted(b for b in robot_bodies
                                                       if b not in bodies or not bodies[b]["floor_capable"]),
        "self_collision_candidate_geom_pairs": pairs,
        "excluded_body_pairs": sorted("%s <-> %s" % (mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_BODY, a),
                                                     mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_BODY, b))
                                      for a, b in excluded),
        "bodies_that_can_self_collide": sorted(self_capable_bodies),
        "bodies_that_CANNOT_self_collide": sorted(b for b in robot_bodies if b not in self_capable_bodies),
        "per_body": {b: bodies.get(b, {"geoms": 0, "floor_capable": 0, "self_capable": 0})
                     for b in robot_bodies},
        "per_geom": geoms,
    }


def rest_pose_overlap(robot="ours_selfcontact", key="STAND", settle_s=1.0):
    """MEASURE which geom pairs already interpenetrate in the rest pose, by how much, and
    with what contact force — because a census that counts those as 'self-collision' is
    counting a convex-hull artifact, and a census that silently drops them is hiding a
    force that perturbs the gait."""
    import mujoco
    model, scene = common.load_model(robot, os.path.join(ROOT, "out", "sim-sweep", "_census",
                                                         "scene_rest_%s.xml" % robot))
    data = mujoco.MjData(model)
    kid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, key)
    mujoco.mj_resetDataKeyframe(model, data, kid)
    mujoco.mj_forward(model, data)
    floor = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, "floor")

    def gm(i):
        mid = int(model.geom_dataid[i])
        return (mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_MESH, mid) if mid >= 0 else "(prim)")

    def scan(tag):
        rows = {}
        w = np.zeros(6)
        for i in range(data.ncon):
            c = data.contact[i]
            if c.geom1 == floor or c.geom2 == floor:
                continue
            b1 = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_BODY, int(model.geom_bodyid[c.geom1]))
            b2 = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_BODY, int(model.geom_bodyid[c.geom2]))
            k = " <-> ".join(sorted(["%s/%s" % (b1, gm(c.geom1)), "%s/%s" % (b2, gm(c.geom2))]))
            mujoco.mj_contactForce(model, data, i, w)
            r = rows.setdefault(k, {"contact_points": 0, "max_penetration_mm": 0.0, "total_force_N": 0.0})
            r["contact_points"] += 1
            r["max_penetration_mm"] = round(max(r["max_penetration_mm"], -float(c.dist) * 1000.0), 4)
            r["total_force_N"] = round(r["total_force_N"] + float(np.linalg.norm(w[:3])), 5)
        return {"when": tag, "pairs": rows}

    at_reset = scan("immediately after mj_resetDataKeyframe(%s) + mj_forward" % key)
    n = int(round(settle_s / float(model.opt.timestep)))
    for _ in range(n):
        mujoco.mj_step(model, data)
    settled = scan("after %.2f s of free settling with ctrl held at the keyframe" % settle_s)
    return {"robot": robot, "keyframe": key, "scene_file": os.path.relpath(scene, ROOT),
            "at_reset": at_reset, "settled": settled,
            "meaning": "MuJoCo collides the CONVEX HULL of a mesh. A part correctly nested inside another "
                       "part's concave shell therefore reads as penetration and generates a real contact "
                       "force in the simulation. These pairs are named and excluded from the "
                       "'did the motion cause a self-collision' count; the force they inject is why the "
                       "selfcontact model is a census instrument and not a dynamics model."}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--census", action="store_true")
    ap.add_argument("--models", default="ours,ours_allcollisions,ours_selfcontact,ours_fullcontact")
    a = ap.parse_args()
    build = write_and_clean() if (a.write or a.census) else {"written": [], "pass1_rest_overlap": {},
                                                             "pass2_rest_overlap": {}}
    written = build["written"]
    if not a.census:
        return
    os.makedirs(EVID, exist_ok=True)
    out = {}
    for m in a.models.split(","):
        c = census(m)
        out[m] = c
        print("%-22s geoms=%-4d floor-capable=%-3d self-pairs=%-6d bodies self-capable=%d/%d" % (
            m, c["compiled_geoms_robot"], c["n_geoms_that_can_contact_the_floor"],
            c["self_collision_candidate_geom_pairs"], len(c["bodies_that_can_self_collide"]),
            c["bodies_total"]))
    doc = {
        "study": "collision-model-census",
        "inputs": {
            "models": {m: out[m]["robot_file"] for m in out},
            "generated_variants": written,
            "mujoco_filter_rule": "a geom pair is checked iff (contype1 & conaffinity2) || "
                                  "(contype2 & conaffinity1), the geoms are in different bodies, and "
                                  "(flag filterparent, enabled by default) the bodies are not a "
                                  "parent/child pair. Evaluated here on the COMPILED model.",
        },
        "method": "sim/collision_model.py compiles each scene through sim/common.py load_model() and reads "
                  "model.geom_contype / model.geom_conaffinity / model.geom_bodyid / model.body_parentid "
                  "off the compiled MjModel. Nothing is read from the XML text.",
        "outputs": out,
        "rest_pose_hull_overlap": {
            "$why": "MuJoCo collides the CONVEX HULL of a mesh, so a part correctly nested inside another "
                    "part's concave shell reads as penetration and injects a spurious contact force. Pass 1 "
                    "MEASURES which body pairs do this in the STAND rest pose; pass 2 writes a "
                    "<contact><exclude/></contact> for exactly those pairs and re-measures until the rest "
                    "pose is clean. The excluded pairs are named on each variant in inputs.generated_variants, "
                    "and a genuine collision between an excluded pair is the one thing these variants cannot "
                    "see — that pair's clearance is a CAD question, not a simulation one.",
            "pass1_before_exclusion": build["pass1_rest_overlap"],
            "pass2_after_exclusion": build["pass2_rest_overlap"],
        },
        "verdict": "PASS",
        "why": "The census is a measurement of the models, not a check of the robot; it exists so that every "
               "self-collision and floor-contact statement in lane F2 can name the model it is true of. "
               + "; ".join("%s: %d of %d bodies can contact the floor, %d of %d can self-collide"
                           % (m, len(out[m]["bodies_that_can_contact_the_floor"]), out[m]["bodies_total"],
                              len(out[m]["bodies_that_can_self_collide"]), out[m]["bodies_total"]) for m in out),
        "script": "sim/collision_model.py",
        "artifacts": ["sim/microduck_ours_selfcontact.xml", "sim/microduck_ours_fullcontact.xml"]
        + [out[m]["scene_file"] for m in out],
        "looked_at": ["sim/microduck_ours.xml", "sim/microduck_ours_allcollisions.xml",
                      "reference/pollen-microduck-rl/robot_walk.xml",
                      "reference/pollen-microduck-rl/robot_allcollisions.xml",
                      "https://mujoco.readthedocs.io/en/stable/computation/index.html#collision-detection"],
    }
    p = os.path.join(EVID, "collision-model-census.json")
    json.dump(doc, open(p, "w"), indent=1)
    print("wrote", os.path.relpath(p, ROOT))


if __name__ == "__main__":
    main()
