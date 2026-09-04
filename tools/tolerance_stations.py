#!/usr/bin/env python3
"""tolerance_stations.py -- every bearing station on ONE axial scale, measured.

    ce-cad/bin/cad tools/tolerance_stations.py            (numpy; stdlib otherwise)

Written 2026-09-04 for the class-4 (tolerances and fits) resolve lane of
ce-designs/microduck.  Three harvested CANNOT DETERMINE items -- the knee
seat length (harvest idx 12), the last 0.05 mm of the 4 mm ring at the six
hip joints (idx 25) and the coaxiality step between the printed boss and the
horn boss (idx 26) -- all come down to the same unmeasured thing: where,
along each joint's axis, the ring's bore actually sits relative to every
feature that could carry it.  sim/joint_geometry.py placed the bearing and
the servo on that axis; nothing placed the PRINTED features (the Ø16 boss,
the Ø19 shoulder, the shin's own Ø15.9 flange disc, the Ø22 pocket).  This
tool does, and reports the coverage arithmetic per joint.

Nothing here is recalled:
  * the joint tree, geom placements and the child-frame axis convention are
    sim/joint_geometry.py's own walk() (imported, not copied);
  * every feature is read from out/laneT/features/<mesh>.json, which
    tools/measure_mesh_features.py froze off Pollen's reference meshes with
    cecad.meshfeatures.cylinders (diameter, centre, axis, length, fit
    residual, face count) -- the same source the part folders' interfaces
    cite.  Our rebuilt meshes (`__ours`) sit at the identical geom placement
    (sim/swap_meshes.py re-pointed the file, not the pose), so the reference
    features are the ones placed;
  * a feature is 'on the station' only if its axis is parallel to the joint
    axis within AXIS_TOL_DEG and its centre is within RADIAL_TOL_MM of it.

Output: out/open/tolerance-stations.json.  Per joint: the bearing's bore and
OD spans, the servo's two Ø16 x 3.0 discs, every printed feature on the
axis, the bore coverage (which features carry which length of the ring's
bore, the uncovered remainder), the OD coverage, and the axial GAP between
the printed flange face and the horn face -- the number the 0.05 mm question
is actually about.  Exit 0 measured / 2 a required input is missing.
"""
import importlib.util
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
FEATURES = os.path.join(REPO, "out", "laneT", "features")
OUT = os.path.join(REPO, "out", "open", "tolerance-stations.json")
MJCF = os.path.join(REPO, "sim", "microduck_ours.xml")

AXIS_TOL_DEG = 0.5
RADIAL_TOL_MM = 0.3
BEARINGS = {
    "seeed_bearing__configuration__22x16x4": dict(bore=16.0, od=22.0, w=4.0,
                                                  conn="connection:press-fit-bearing-22x16x4"),
    "seeed_bearing__configuration_default": dict(bore=10.0, od=15.0, w=3.0,
                                                 conn="connection:press-fit-bearing-15x10x3"),
}
# diameters worth placing on a station (mm) and what they mean there
INTEREST = {16.0: "Ø16 (inner-race seat / horn disc diameter)",
            15.9: "Ø15.9 (shin knee flange disc)",
            19.0: "Ø19 (inner-race thrust shoulder)",
            22.0: "Ø22 (outer-race pocket)",
            10.0: "Ø10 (15x10x3 inner-race seat)",
            15.0: "Ø15 (15x10x3 outer-race pocket)",
            14.0: "Ø14 (ankle pocket window)",
            12.0: "Ø12 (through bore in a full-width seat)",
            6.0: "Ø6 (horn-face centre bore)"}


def _jg():
    spec = importlib.util.spec_from_file_location(
        "joint_geometry", os.path.join(REPO, "sim", "joint_geometry.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _features(mesh):
    p = os.path.join(FEATURES, mesh + ".json")
    if not os.path.exists(p):
        return None
    return json.load(open(p, encoding="utf-8"))


def _nearest(d):
    for k in INTEREST:
        if abs(d - k) <= 0.06:
            return k
    return None


def _span(c_z, axis_z, length):
    h = 0.5 * length * abs(axis_z)
    return [round(float(c_z - h), 4), round(float(c_z + h), 4)]


def _overlap(a, b):
    lo, hi = max(a[0], b[0]), min(a[1], b[1])
    return max(0.0, hi - lo)


def _union_length(spans):
    ss = sorted([list(s) for s in spans])
    total, cur = 0.0, None
    for s in ss:
        if cur is None or s[0] > cur[1]:
            if cur is not None:
                total += cur[1] - cur[0]
            cur = s
        else:
            cur[1] = max(cur[1], s[1])
    if cur is not None:
        total += cur[1] - cur[0]
    return total


def main():
    jg = _jg()
    import xml.etree.ElementTree as ET
    root = ET.parse(MJCF).getroot()
    tree = jg.walk(root)
    if not os.path.isdir(FEATURES):
        print("MISSING", FEATURES)
        return 2

    stations = {}
    for child, node in tree.items():
        j = node["joint"]
        if not j or j["type"] != "hinge":
            continue
        parent = node["parent"]
        pnode = tree[parent]
        Rc, pc = node["R"], node["pos_mm"]
        cands = []
        for mesh, gclass, gp, gR in node["geoms"]:
            if gclass == "self_collision_only":
                continue
            cands.append(("child:" + child, mesh, gp, gR))
        for mesh, gclass, gp, gR in pnode["geoms"]:
            if gclass == "self_collision_only":
                continue
            cands.append(("parent:" + parent, mesh, Rc.T @ (gp - pc), Rc.T @ gR))

        rows, bearings, discs = [], [], []
        for where, mesh, gp, gR in cands:
            ref = mesh.replace("__ours", "")
            feats = _features(ref)
            if feats is None:
                continue
            for kind in ("bosses", "holes"):
                for f in feats.get(kind, []):
                    k = _nearest(float(f["d_mm"]))
                    if k is None:
                        continue
                    c = gp + gR @ np.array(f["center_mm"], float)
                    a = gR @ np.array(f["axis"], float)
                    ang = float(np.degrees(np.arccos(np.clip(abs(a[2]), -1, 1))))
                    radial = float(np.hypot(c[0], c[1]))
                    if ang > AXIS_TOL_DEG or radial > RADIAL_TOL_MM:
                        continue
                    row = {"where": where, "mesh": ref, "feature": kind[:-1],
                           "d_mm": round(float(f["d_mm"]), 4), "class": INTEREST[k],
                           "span_axial_mm": _span(c[2], a[2], float(f["length_mm"])),
                           "length_mm": round(float(f["length_mm"]), 4),
                           "radial_off_axis_mm": round(radial, 4),
                           "fit_residual_mm": f.get("residual_mm"),
                           "faces": f.get("faces"), "cover_deg": f.get("cover_deg"),
                           "source": "out/laneT/features/%s.json (%s d=%.4f centre %s)"
                                     % (ref, kind[:-1], f["d_mm"],
                                        [round(v, 4) for v in f["center_mm"]])}
                    if ref in BEARINGS:
                        row["role"] = "bearing " + ("bore" if kind == "holes" else "od")
                        bearings.append(row)
                    elif ref == "xl330" and kind == "bosses" and k == 16.0:
                        row["role"] = "servo Ø16 x 3.0 disc (horn or idler)"
                        discs.append(row)
                    else:
                        row["role"] = "printed feature"
                    rows.append(row)

        # bore coverage per bearing on this station
        analyses = []
        for b in [r for r in bearings if r["role"] == "bearing bore"]:
            bs = b["span_axial_mm"]
            carriers = []
            for r in rows:
                if r is b or r["role"].startswith("bearing"):
                    continue
                if r["feature"] != "boss":
                    continue
                if abs(r["d_mm"] - b["d_mm"]) > 0.15:
                    continue
                ov = _overlap(bs, r["span_axial_mm"])
                if ov > 1e-6:
                    carriers.append({"mesh": r["mesh"], "where": r["where"],
                                     "d_mm": r["d_mm"], "role": r["role"],
                                     "span_axial_mm": r["span_axial_mm"],
                                     "overlap_with_bore_mm": round(ov, 4),
                                     "diametral_gap_to_bore_nominal_mm":
                                         round(float(b["d_mm"]) - r["d_mm"], 4)})
            covered = _union_length([c["span_axial_mm"] for c in carriers] and
                                    [[max(bs[0], c["span_axial_mm"][0]),
                                      min(bs[1], c["span_axial_mm"][1])]
                                     for c in carriers])
            width = bs[1] - bs[0]
            printed = [c for c in carriers if c["mesh"] != "xl330"]
            horn = [c for c in carriers if c["mesh"] == "xl330"]
            gap = None
            if printed and horn:
                # the axial GAP between the printed flange face (end of the
                # printed carrier nearest the horn) and the horn face
                p, h = printed[0]["span_axial_mm"], horn[0]["span_axial_mm"]
                if p[1] <= h[0] + 1e-9:
                    gap = round(h[0] - p[1], 4)
                elif h[1] <= p[0] + 1e-9:
                    gap = round(p[0] - h[1], 4)
                else:
                    gap = round(-_overlap(p, h), 4)   # negative = they interpenetrate
            analyses.append({
                "bearing": b["mesh"], "bore_d_mm": b["d_mm"],
                "bore_span_axial_mm": bs, "ring_width_mm": round(width, 4),
                "carriers": carriers,
                "covered_mm": round(covered, 4),
                "uncovered_mm": round(width - covered, 4),
                "covered_pct": round(100.0 * covered / width, 2) if width else None,
                "printed_carrier_mm": round(sum(c["overlap_with_bore_mm"] for c in printed), 4),
                "horn_disc_carrier_mm": round(sum(c["overlap_with_bore_mm"] for c in horn), 4),
                "flange_face_to_horn_face_gap_mm": gap,
                "gap_meaning": (None if gap is None else
                                "positive = the printed flange face and the servo's horn face "
                                "do NOT touch in the reference placement by this much; zero = "
                                "they touch; negative = the placements interpenetrate. A "
                                "bolted flange cannot hold a positive gap, so a positive value "
                                "is a placement offset in the reference export, not a feature.")})
        for b in [r for r in bearings if r["role"] == "bearing od"]:
            bs = b["span_axial_mm"]
            pockets = []
            for r in rows:
                if r["feature"] != "hole" or r["role"].startswith("bearing"):
                    continue
                if abs(r["d_mm"] - b["d_mm"]) > 0.15:
                    continue
                ov = _overlap(bs, r["span_axial_mm"])
                if ov > 1e-6:
                    pockets.append({"mesh": r["mesh"], "where": r["where"],
                                    "d_mm": r["d_mm"], "span_axial_mm": r["span_axial_mm"],
                                    "overlap_with_od_mm": round(ov, 4)})
            width = bs[1] - bs[0]
            covered = _union_length([[max(bs[0], p["span_axial_mm"][0]),
                                      min(bs[1], p["span_axial_mm"][1])] for p in pockets])
            analyses.append({"bearing": b["mesh"], "od_d_mm": b["d_mm"],
                             "od_span_axial_mm": bs, "ring_width_mm": round(width, 4),
                             "pockets": pockets, "covered_mm": round(covered, 4),
                             "uncovered_mm": round(width - covered, 4),
                             "covered_pct": round(100.0 * covered / width, 2) if width else None,
                             "note": ("no Ø%.0f pocket feature found on the axis -- the outer "
                                      "race's housing is either not a cylinder the feature "
                                      "extractor kept, or is a Ø19 window/face (bearing_roll)"
                                      % b["d_mm"]) if not pockets else None})

        stations[j["name"]] = {
            "child_body": child, "parent_body": parent,
            "on_axis_features": sorted(rows, key=lambda r: r["span_axial_mm"][0]),
            "servo_discs": [{"span_axial_mm": d["span_axial_mm"], "where": d["where"]}
                            for d in discs],
            "coverage": analyses,
        }

    doc = {
        "study": "tolerance-stations",
        "what": ("every bearing station on the robot on one axial scale: the ring's bore "
                 "and OD spans, the servo's Ø16 x 3.0 discs, and every printed feature on "
                 "the axis, with the coverage arithmetic per ring (tools/tolerance_stations.py)"),
        "inputs": {"mjcf": os.path.relpath(MJCF, REPO), "features": os.path.relpath(FEATURES, REPO),
                   "axis_tol_deg": AXIS_TOL_DEG, "radial_tol_mm": RADIAL_TOL_MM},
        "conventions": ("child-frame +z is the joint axis (sim/joint_geometry.py asserts it); "
                        "spans are along that axis in mm from the child body origin; a "
                        "parent-body geom is transformed by R_child^T (p - pos_child)"),
        "joints": stations,
        "n_joints": len(stations),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(doc, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("wrote", os.path.relpath(OUT, REPO), "joints", len(stations))
    for name, st in stations.items():
        for a in st["coverage"]:
            if "bore_d_mm" in a:
                print("%-16s bore Ø%.1f span %s covered %.4f/%.4f (printed %.4f + horn %.4f) "
                      "uncovered %.4f gap %s" % (name, a["bore_d_mm"], a["bore_span_axial_mm"],
                                                 a["covered_mm"], a["ring_width_mm"],
                                                 a["printed_carrier_mm"], a["horn_disc_carrier_mm"],
                                                 a["uncovered_mm"], a["flange_face_to_horn_face_gap_mm"]))
            else:
                print("%-16s od   Ø%.1f span %s covered %.4f/%.4f pockets %d"
                      % (name, a["od_d_mm"], a["od_span_axial_mm"], a["covered_mm"],
                         a["ring_width_mm"], len(a["pockets"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
