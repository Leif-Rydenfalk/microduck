#!/usr/bin/env python3
"""LANE F3 -- which bearing, which servo, which horn face, for each of the 14 hinges.

The tolerance stack-up needs, per joint, the physical elements ON that joint's
axis.  Nothing here is recalled: every element is a geom in sim/microduck_ours.xml
whose position is projected onto the joint's own axis line and kept only if it is
within `--radial` mm of it.

Conventions read out of the model, not assumed:
  * every hinge in this MJCF has axis="0 0 1" in its own child body's frame, so
    the joint axis is the line through the child body origin along the child
    frame's +z (checked, and the script FAILS if any joint disagrees);
  * a joint's supports may sit in the PARENT body (placed at the child's own
    origin) or in the CHILD body (placed at its origin) -- both are searched,
    each transformed into the child's frame;
  * the XL330 mesh's two horn/idler discs are Ø16.0 x 3.0 with centres at
    x = +/-13.0 in the mesh frame (cecad.meshfeatures.cylinders on xl330.stl,
    quoted in ce-connections/spline-xl330-horn/iterations/v0.0.1/compat.py),
    so the two outer disc FACES are +/-14.5 mm from the servo geom origin
    along the servo's own axis;
  * the bearing meshes span 0..W along their own +z from the geom origin
    (ce-connections/press-fit-bearing-22x16x4 compat.py: 'the bearing mesh
    spanning 0..4 along that axis'), W = 4.0 for the 22x16x4 and 3.0 for the
    15x10x3.

    ce-cad/bin/cad sim/joint_geometry.py     (plain python3 works too: stdlib + numpy)

Output: out/sim-evidence/joint-geometry.json
"""

import json
import os
import xml.etree.ElementTree as ET

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
MJCF = os.path.join(REPO, "sim/microduck_ours.xml")

DISC_HALF_SPAN_MM = 14.5     # servo geom origin -> outer horn/idler face
BEARING_W = {"seeed_bearing__configuration__22x16x4": 4.0,
             "seeed_bearing__configuration_default": 3.0}
BEARING_BORE = {"seeed_bearing__configuration__22x16x4": 16.0,
                "seeed_bearing__configuration_default": 10.0}
BEARING_OD = {"seeed_bearing__configuration__22x16x4": 22.0,
              "seeed_bearing__configuration_default": 15.0}
BEARING_CONN = {"seeed_bearing__configuration__22x16x4":
                "connection:press-fit-bearing-22x16x4",
                "seeed_bearing__configuration_default":
                "connection:press-fit-bearing-15x10x3"}


def quat_matrix(q):
    w, x, y, z = [float(v) for v in q]
    n = (w * w + x * x + y * y + z * z) ** 0.5
    w, x, y, z = w / n, x / n, y / n, z / n
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])


def walk(root):
    """{body: {parent, pos_mm, R, joint, geoms:[(mesh, pos_mm, R)]}}"""
    tree = {}

    def rec(el, parent):
        for b in el.findall("body"):
            name = b.get("name")
            pos = np.array([float(v) for v in (b.get("pos") or "0 0 0").split()]) * 1000.0
            R = quat_matrix((b.get("quat") or "1 0 0 0").split())
            j = b.find("joint")
            geoms = []
            for g in b.findall("geom"):
                if g.get("type") != "mesh":
                    continue
                gp = np.array([float(v) for v in (g.get("pos") or "0 0 0").split()]) * 1000.0
                geoms.append((g.get("mesh"), g.get("class"), gp,
                              quat_matrix((g.get("quat") or "1 0 0 0").split())))
            tree[name] = {
                "parent": parent, "pos_mm": pos, "R": R, "geoms": geoms,
                "joint": None if j is None else {
                    "name": j.get("name"), "type": j.get("type"),
                    "axis": [float(v) for v in (j.get("axis") or "0 0 1").split()],
                    "range_rad": [float(v) for v in (j.get("range") or "0 0").split()],
                    "class": j.get("class")},
            }
            rec(b, name)
    rec(root.find("worldbody"), None)
    return tree


def main():
    root = ET.parse(MJCF).getroot()
    tree = walk(root)
    radial_tol = 3.0            # mm: a geom this far off the axis is not on it

    joints = {}
    for child, node in tree.items():
        j = node["joint"]
        if not j or j["type"] != "hinge":
            continue
        assert j["axis"] == [0.0, 0.0, 1.0], (j["name"], j["axis"])
        parent = node["parent"]
        pnode = tree[parent]
        axis_c = np.array([0.0, 0.0, 1.0])          # in the CHILD frame

        cands = []
        # child's own geoms are already in the child frame
        for mesh, gclass, gp, gR in node["geoms"]:
            if gclass == "self_collision_only":
                continue
            cands.append(("child:" + child, mesh, gp, gR))
        # parent's geoms: p_child = R_child^T (p_parent - pos_child)
        Rc, pc = node["R"], node["pos_mm"]
        for mesh, gclass, gp, gR in pnode["geoms"]:
            if gclass == "self_collision_only":
                continue
            cands.append(("parent:" + parent, mesh, Rc.T @ (gp - pc), Rc.T @ gR))

        on_axis = []
        for where, mesh, p, R in cands:
            radial = float(np.hypot(p[0], p[1]))
            if radial > radial_tol:
                continue
            entry = {"where": where, "mesh": mesh,
                     "axial_mm": round(float(p[2]), 4),
                     "radial_off_axis_mm": round(radial, 4),
                     "mesh_z_vs_joint_axis_deg": round(float(np.degrees(
                         np.arccos(np.clip(abs((R @ axis_c) @ axis_c), -1, 1)))), 4)}
            if mesh in BEARING_W:
                w = BEARING_W[mesh]
                d = R @ np.array([0.0, 0.0, 1.0])
                entry.update({
                    "kind": "bearing",
                    "connection": BEARING_CONN[mesh],
                    "bore_mm": BEARING_BORE[mesh], "od_mm": BEARING_OD[mesh],
                    "width_mm": w,
                    "span_axial_mm": [round(float(p[2]), 4),
                                      round(float(p[2] + w * d[2]), 4)],
                    "mid_axial_mm": round(float(p[2] + 0.5 * w * d[2]), 4)})
            elif mesh == "xl330":
                # the XL330 mesh's OUTPUT axis is its own +x (the two Ø16 x 3
                # discs sit at x = +/-13.0), NOT its +z. cecad.meshfeatures on
                # xl330.stl, quoted in spline-xl330-horn/compat.py.
                dx = R @ np.array([1.0, 0.0, 0.0])
                align = float(abs(dx @ axis_c))
                entry.update({
                    "kind": "servo",
                    "connection": "connection:spline-xl330-horn",
                    "output_axis_alignment": round(align, 6),
                    "drives_this_joint": align > 0.999,
                    "disc_face_axial_mm": sorted(
                        [round(float(p[2] - DISC_HALF_SPAN_MM * align), 4),
                         round(float(p[2] + DISC_HALF_SPAN_MM * align), 4)])})
            else:
                entry["kind"] = "link"
            on_axis.append(entry)

        bearings = [e for e in on_axis if e.get("kind") == "bearing"]
        servos = [e for e in on_axis
                  if e.get("kind") == "servo" and e.get("drives_this_joint")]
        span = None
        if bearings and servos:
            b = min(bearings, key=lambda e: abs(e["mid_axial_mm"]))
            faces = [f for s in servos for f in s["disc_face_axial_mm"]]
            d = [abs(f - b["mid_axial_mm"]) for f in faces]
            span = {"bearing_mid_axial_mm": b["mid_axial_mm"],
                    "horn_faces_axial_mm": sorted(set(faces)),
                    "nearest_face_span_mm": round(min(d), 4),
                    "farthest_face_span_mm": round(max(d), 4)}

        joints[j["name"]] = {
            "child_body": child, "parent_body": parent,
            "range_rad": j["range_rad"],
            "range_deg": [round(float(np.degrees(v)), 4) for v in j["range_rad"]],
            "actuator_class": j["class"],
            "on_axis": sorted(on_axis, key=lambda e: e["axial_mm"]),
            "n_bearings": len(bearings),
            "n_servos": len(servos),
            "flange_to_bearing_span": span,
        }

    out = {
        "study": "joint-geometry",
        "what": ("For each of the 14 hinges: every geom that lies on that joint's "
                 "axis, its axial station, and the flange-to-bearing span the "
                 "tolerance stack needs."),
        "inputs": {"mjcf": "sim/microduck_ours.xml",
                   "radial_tolerance_mm": radial_tol,
                   "disc_half_span_mm": DISC_HALF_SPAN_MM,
                   "disc_basis": ("cecad.meshfeatures.cylinders on xl330.stl: bosses "
                                  "d 16.0 x 3.0 with centres x +/-13.0, quoted as "
                                  "DISC_D/DISC_L in ce-connections/spline-xl330-horn/"
                                  "iterations/v0.0.1/compat.py; outer faces at "
                                  "13.0 + 3.0/2 = 14.5 from the mesh centre"),
                   "bearing_widths_mm": BEARING_W,
                   "bearing_basis": ("cecad.meshfeatures + numpy bbox on "
                                     "seeed_bearing__configuration__22x16x4.stl "
                                     "(hole 16.0 / boss 22.0 / 4.0 wide) and "
                                     "seeed_bearing__configuration_default.stl "
                                     "(hole 10.0 / boss 15.0 / 3.0 wide), quoted in "
                                     "each connection folder's compat.py header")},
        "method": ("Body tree walked from <worldbody>; every hinge asserted to have "
                   "axis 0 0 1 in its own child frame; parent geoms transformed into "
                   "the child frame by R_child^T (p_parent - pos_child); a geom is "
                   "'on the axis' when its origin is within %s mm of it radially."
                   % radial_tol),
        "outputs": {"joints": joints, "n_joints": len(joints)},
        "verdict": "PASS" if len(joints) == 14 else "FAIL",
        "why": "%d hinges found; %d carry a bearing on the axis, %d carry a servo."
               % (len(joints), sum(1 for v in joints.values() if v["n_bearings"]),
                  sum(1 for v in joints.values() if v["n_servos"])),
        "script": "sim/joint_geometry.py",
        "artifacts": ["out/sim-evidence/joint-geometry.json"],
        "looked_at": ["sim/microduck_ours.xml",
                      "ce-connections/press-fit-bearing-22x16x4/iterations/v0.0.1/compat.py",
                      "ce-connections/press-fit-bearing-15x10x3/iterations/v0.0.1/compat.py",
                      "ce-connections/spline-xl330-horn/iterations/v0.0.1/compat.py"],
    }
    path = os.path.join(REPO, "out/sim-evidence/joint-geometry.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(out, open(path, "w"), indent=1)
    for n, v in joints.items():
        s = v["flange_to_bearing_span"]
        print("%-16s %-16s bearings %d servos %d  span %s"
              % (n, v["child_body"], v["n_bearings"], v["n_servos"],
                 "-" if not s else "%.3f..%.3f mm" % (s["nearest_face_span_mm"],
                                                      s["farthest_face_span_mm"])))
    print(out["why"])


if __name__ == "__main__":
    main()
