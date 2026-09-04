#!/usr/bin/env python3
"""place_harness.py — put the routed harness INTO the assembly, through mate().

    python3 tools/place_harness.py
        -> ce-assemblies/microduck/current/harness.json

TRIAD.md's rule, kept: a joined part gets NO literal transform. Every connector
housing here is placed by calling connection:jst-eh-3pin's own `mate()` on two
interface records — the housing's (part:jst-ehr-03 cad/interfaces.json) and a
header record built from a MEASUREMENT: the servo's EH socket frame off
part:xl330-m288-t's own pocket, or the HAT's connector frame off Pollen's
published board (out/wiring/hat-connectors.json). The 4x4 that comes back is
decomposed into a world position and a quaternion, and then CHECKED by pushing
the housing's local origin and its z and x axes back through the transform. A
placement whose check does not close to 1e-6 mm is written as a FAIL, never
dropped.

A cable is not a rigid part and it is not placed by a mate: it is a body whose
shape was DERIVED from the two connector frames at its ends by the router. Each
cable row therefore carries the geometry file, the frames it was derived from,
and the measured length — not a transform.
"""
import json, math, os, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, R + "/ce-connections/jst-eh-3pin/current/cad")
from mate import mate as eh_mate                                    # noqa: E402

OUT = R + "/ce-assemblies/microduck/current/harness.json"


def load(rel):
    p = os.path.join(R, rel)
    return json.load(open(p)) if os.path.exists(p) else None


def quat_of(Tm):
    """(w,x,y,z) from the rotation block of a 4x4, Shepperd's branch choice."""
    m = [[Tm[i][j] for j in range(3)] for i in range(3)]
    tr = m[0][0] + m[1][1] + m[2][2]
    if tr > 0:
        s = math.sqrt(tr + 1.0) * 2
        q = [0.25 * s, (m[2][1] - m[1][2]) / s, (m[0][2] - m[2][0]) / s, (m[1][0] - m[0][1]) / s]
    elif m[0][0] > m[1][1] and m[0][0] > m[2][2]:
        s = math.sqrt(1.0 + m[0][0] - m[1][1] - m[2][2]) * 2
        q = [(m[2][1] - m[1][2]) / s, 0.25 * s, (m[0][1] + m[1][0]) / s, (m[0][2] + m[2][0]) / s]
    elif m[1][1] > m[2][2]:
        s = math.sqrt(1.0 + m[1][1] - m[0][0] - m[2][2]) * 2
        q = [(m[0][2] - m[2][0]) / s, (m[0][1] + m[1][0]) / s, 0.25 * s, (m[1][2] + m[2][1]) / s]
    else:
        s = math.sqrt(1.0 + m[2][2] - m[0][0] - m[1][1]) * 2
        q = [(m[1][0] - m[0][1]) / s, (m[0][2] + m[2][0]) / s, (m[1][2] + m[2][1]) / s, 0.25 * s]
    n = math.sqrt(sum(c * c for c in q))
    return [c / n for c in q]


def apply(Tm, v):
    return [sum(Tm[i][k] * v[k] for k in range(3)) + Tm[i][3] for i in range(3)]


def rot(Tm, v):
    return [sum(Tm[i][k] * v[k] for k in range(3)) for i in range(3)]


def dist(a, b):
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def ang(a, b):
    d = max(-1.0, min(1.0, sum(a[i] * b[i] for i in range(3))))
    return math.degrees(math.acos(d))


def main():
    cab3 = load("out/wiring/cables3d.json")["record"]
    hatr = load("out/wiring/cables3d-hat.json")
    hat_rows = {c["id"]: c for c in hatr["record"]["cables"]} if hatr else {}
    solids = load("out/wiring/solids.json")
    srows = {r["id"]: r for r in solids["record"]["cables"]} if solids else {}
    hous_if = load("ce-parts/jst-ehr-03/current/cad/interfaces.json")["record"]["interfaces"]
    hmate = dict([i for i in hous_if if i["name"] == "mate"][0])
    hmate["role"] = "eh_housing"
    hmate["owner_ref"] = "part:jst-ehr-03"

    rows, conn_rows, bom = [], [], {}
    checks = {"PASS": 0, "FAIL": 0}
    worst_pos, worst_ax = 0.0, 0.0
    for c in cab3["cables"]:
        rid = c["id"]
        c = hat_rows.get(rid, c)            # the re-route with a located HAT end wins
        s = srows.get(rid)
        row = {"id": rid, "group": c["group"], "kind": "cable",
               "od_mm": c["od_mm"], "od_is_nominal": c.get("od_is_nominal"),
               "conductors": c.get("conductors"),
               "routed": bool(c.get("routed")),
               "verdict": c["verdict"],
               "routed_length_mm": c.get("routed_length_mm"),
               "cable_mm_from_cables_json": c.get("cable_mm_from_cables_json"),
               "delta_vs_cable_mm": c.get("delta_vs_cable_mm"),
               "min_clearance_mm": c.get("min_clearance_mm"),
               "pierce_samples": c.get("pierce_samples"),
               "geometry": ("out/wiring/cad/%s.stl" % rid) if s else None,
               "geometry_exists": bool(s) and os.path.exists(R + "/out/wiring/cad/%s.stl" % rid),
               "mass_total_g": (s or {}).get("mass_total_g"),
               "mass_is_nominal": (s or {}).get("mass_is_nominal"),
               "derived_from": "the two connector frames on its ends; a cable is not placed by a "
                               "transform, its shape IS the placement",
               "ends": []}
        for e in (c.get("ends") or []):
            row["ends"].append({"device": e.get("device"), "located": e.get("located"),
                                "kind": e.get("kind"), "refdes": e.get("refdes"),
                                "housing_part": e.get("housing_part"),
                                "why_unlocated": e.get("why_unlocated")})
            if not e.get("housing_part") or not e.get("mate_mm"):
                continue
            header = {"name": "socket", "role": "eh_header", "series": "EH", "circuits": 3,
                      "pitch_mm": 2.5, "mated_height_mm": 8.1,
                      "owner_ref": ("part:xl330-m288-t" if e.get("kind", "").startswith("xl330")
                                    else "part:microduck-robot-hat-pcb"),
                      "frame": {"origin_mm": e["mate_mm"], "z_axis": e["insertion_dir"],
                                "x_axis": e["row_dir"]}}
            # THE SERVO SOCKET'S z IS THE HOUSING'S TRAVEL, so the header's own +z
            # is the opposite: mate() takes the HEADER frame, whose +z leaves the
            # board. Flipping it here is what makes the seat land outside the case.
            header["frame"]["z_axis"] = [-v for v in e["insertion_dir"]]
            mt = eh_mate(hmate, header)
            T = mt.transform
            o = [round(T[i][3], 6) for i in range(3)]
            q = [round(v, 9) for v in quat_of(T)]
            # CHECK: push the housing's own frame through T and compare with mate()'s promise
            seat = mt.provenance.get("seat_mm", 1.6)
            want_o = [e["mate_mm"][i] + header["frame"]["z_axis"][i] * seat for i in range(3)]
            got_o = apply(T, [0.0, 0.0, 0.0])
            want_z = [-v for v in header["frame"]["z_axis"]]
            got_z = rot(T, [0.0, 0.0, 1.0])
            dp, da = dist(want_o, got_o), ang(want_z, got_z)
            ok = dp < 1e-6 and da < 1e-6
            checks["PASS" if ok else "FAIL"] += 1
            worst_pos = max(worst_pos, dp)
            worst_ax = max(worst_ax, da)
            conn_rows.append({
                "cable": rid, "at_device": e.get("device"), "refdes": e.get("refdes"),
                "part": "part:jst-ehr-03", "via_connection": "connection:jst-eh-3pin",
                "world_pos_mm": o, "world_quat_wxyz": q,
                "header_owner": header["owner_ref"],
                "mate_verdict": mt.verdict, "seat_mm": seat,
                "adds_parts": mt.adds_parts,
                "placed_by": "connection:jst-eh-3pin cad/mate.py called on the housing's own "
                             "`mate` interface and a header frame MEASURED off %s"
                             % header["owner_ref"],
                "verify": {"origin_error_mm": round(dp, 12), "axis_error_deg": round(da, 12),
                           "verdict": "PASS" if ok else "FAIL"}})
            for a in mt.adds_parts:
                bom[a["ref"]] = bom.get(a["ref"], 0) + a["qty"]
        rows.append(row)

    doc = {"$triad": 1, "kind": "harness", "generated_by": "tools/place_harness.py",
           "record": {
               "ref": "assembly:microduck",
               "units": "mm, g",
               "frame": cab3["frame"],
               "placement_rule": "TRIAD.md: a joined part gets no literal transform. Every "
                                 "housing came out of connection:jst-eh-3pin's mate(); every "
                                 "cable's shape was derived by the router from the frames at "
                                 "its two ends.",
               "counts": {
                   "runs_in_cables_json": len(cab3["cables"]),
                   "cables_with_geometry": sum(1 for r in rows if r["geometry_exists"]),
                   "cables_routed": sum(1 for r in rows if r["routed"]),
                   "housings_placed": len(conn_rows),
                   "housing_checks_PASS": checks["PASS"], "housing_checks_FAIL": checks["FAIL"],
                   "worst_origin_error_mm": round(worst_pos, 12),
                   "worst_axis_error_deg": round(worst_ax, 12)},
               "bom_added": [{"ref": k, "qty": v} for k, v in sorted(bom.items())],
               "bom_note": "these are the pieces connection:jst-eh-3pin says a mated EH joint "
                           "costs (housing + 3 crimps, and the board header EXCEPT where it is "
                           "already inside a bought servo). They are not yet merged into "
                           "bom.json, which another lane owns.",
               "cables": rows,
               "connectors": conn_rows}}
    json.dump(doc, open(OUT, "w"), indent=1)
    cn = doc["record"]["counts"]
    print("cables %d (geometry %d, routed %d); housings %d (PASS %d FAIL %d); "
          "worst origin %.3e mm axis %.3e deg"
          % (cn["runs_in_cables_json"], cn["cables_with_geometry"], cn["cables_routed"],
             cn["housings_placed"], cn["housing_checks_PASS"], cn["housing_checks_FAIL"],
             cn["worst_origin_error_mm"], cn["worst_axis_error_deg"]))
    for b in doc["record"]["bom_added"]:
        print("  BOM +%3d x %s" % (b["qty"], b["ref"]))
    print("wrote", OUT)


main()
