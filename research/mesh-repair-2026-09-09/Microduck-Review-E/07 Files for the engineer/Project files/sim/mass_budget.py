#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""mass_budget.py — THE MASS MODEL THE ROBOT ACTUALLY HAS, per body.

    ce-cad/bin/cad sim/mass_budget.py   ->  out/open/mass-budget.json

Pollen's MJCF carries 0.737243 kg of link inertials and NOTHING ELSE: no screws,
no harness, no connector housings. Every static study in this repo -- torque
margin, centre of gravity, tipping -- has been run on that number. This tool
rebuilds the inertial model with the two populations the MJCF omits and that
this repo has since MEASURED:

  fasteners  64 placed screws (out/fasteners/placed.json), each one's mass read
             off its BUILT SOLID by tools/screw_mass.py -- not from an ISO table,
             because the part has a hex socket sunk in its head.
  harness    18 routed cables + 28 connector housings (out/wiring/solids.json,
             solids-hat.json), mass from the copper/jacket basis stated there.

ATTRIBUTION IS MEASURED, NOT ASSIGNED BY NAME. Every geom in the MJCF is expanded
to its mesh vertices in world at qpos0 and reduced to a world AABB per body. A
screw goes to the body whose AABB its head point is nearest (0.0 mm if inside).
A cable is resampled at 1.0 mm and EVERY SAMPLE is attributed separately, so a
run that crosses from the trunk into the head puts its mass on both -- which is
what a harness does.

Output per body: MJCF mass and com, added mass and its com, the augmented mass
and com in the BODY's own frame (so a pose change carries it correctly), and the
whole-robot totals. Nothing here is rounded to a plausible number; a body that
gains nothing says 0.0.
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import common  # noqa: E402
import mujoco  # noqa: E402

OUT = os.path.join(ROOT, "out", "open")
os.makedirs(OUT, exist_ok=True)
SAMPLE_MM = 1.0


def body_aabbs(model, data):
    """world AABB per body id, in mm, from every geom's real mesh vertices."""
    boxes = {}
    for g in range(model.ngeom):
        b = int(model.geom_bodyid[g])
        pos = data.geom_xpos[g] * 1000.0
        mat = data.geom_xmat[g].reshape(3, 3)
        did = int(model.geom_dataid[g])
        if model.geom_type[g] == mujoco.mjtGeom.mjGEOM_MESH and did >= 0:
            adr = int(model.mesh_vertadr[did]); n = int(model.mesh_vertnum[did])
            v = model.mesh_vert[adr:adr + n].astype(np.float64) * 1000.0
            w = v @ mat.T + pos
        else:
            sz = model.geom_size[g] * 1000.0
            c = np.array([[sx, sy, sz2] for sx in (-sz[0], sz[0])
                          for sy in (-sz[1], sz[1]) for sz2 in (-sz[2], sz[2])])
            w = c @ mat.T + pos
        lo, hi = w.min(0), w.max(0)
        if b in boxes:
            boxes[b] = (np.minimum(boxes[b][0], lo), np.maximum(boxes[b][1], hi))
        else:
            boxes[b] = (lo, hi)
    return boxes


def nearest_body(pt, boxes):
    best, bd = None, 1e18
    for b, (lo, hi) in boxes.items():
        d = np.linalg.norm(np.maximum(np.maximum(lo - pt, pt - hi), 0.0))
        if d < bd:
            bd, best = d, b
    return best, bd


def main():
    model = mujoco.MjModel.from_xml_path(common.robot_file("ours"))
    data = mujoco.MjData(model)
    mujoco.mj_resetData(model, data)
    mujoco.mj_forward(model, data)
    boxes = body_aabbs(model, data)
    names = [mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_BODY, i) for i in range(model.nbody)]

    add = {i: {"mass_g": 0.0, "moment": np.zeros(3), "items": 0} for i in range(model.nbody)}
    detail = {"fasteners": [], "cables": []}

    # ---- fasteners -------------------------------------------------------
    sv = json.load(open(os.path.join(ROOT, "out", "open", "screw-volumes.json")))
    mass_by_member = {(m["part"], round(float(m["params"]["length_mm"]), 4)):
                      m["mass_g_each"]["carbon_steel_8.8"] for m in sv["members"]}
    placed = json.load(open(os.path.join(ROOT, "out", "fasteners", "placed.json")))["placed"]
    far_screws = 0
    for r in placed:
        key = (r["part"], round(float(r["params"]["length_mm"]), 4))
        m = mass_by_member[key]
        pt = np.array(r["world_pos_mm"], float)
        b, d = nearest_body(pt, boxes)
        if d > 5.0:
            far_screws += 1
        add[b]["mass_g"] += m; add[b]["moment"] += m * pt; add[b]["items"] += 1
        detail["fasteners"].append({"instance": r["instance"], "part": r["part"],
                                    "length_mm": r["length_mm"], "mass_g": round(m, 6),
                                    "body": names[b], "dist_to_body_aabb_mm": round(float(d), 4),
                                    "pilot_mesh": r.get("pilot_mesh")})

    # ---- harness ---------------------------------------------------------
    cable_rows = []
    for sfile, pfile in (("solids.json", "paths.json"), ("solids-hat.json", "paths-hat.json")):
        sol = json.load(open(os.path.join(ROOT, "out", "wiring", sfile)))["record"]
        paths = json.load(open(os.path.join(ROOT, "out", "wiring", pfile)))["record"]["paths"]
        for c in sol["cables"]:
            cid = c["id"]
            poly = np.array(paths[cid]["polyline_mm"], float)
            seg = np.linalg.norm(np.diff(poly, axis=0), axis=1)
            L = float(seg.sum())
            n = max(2, int(round(L / SAMPLE_MM)))
            # arc-length resample
            cum = np.concatenate([[0.0], np.cumsum(seg)])
            s = np.linspace(0.0, L, n)
            pts = np.stack([np.interp(s, cum, poly[:, k]) for k in range(3)], axis=1)
            cable_mass = float(c["mass_total_g"])
            per = cable_mass / n
            hit = {}
            for pt in pts:
                b, d = nearest_body(pt, boxes)
                add[b]["mass_g"] += per; add[b]["moment"] += per * pt; add[b]["items"] += 0
                hit[b] = hit.get(b, 0) + 1
            add[max(hit, key=hit.get)]["items"] += 1
            hmass = 0.0
            for h in c.get("housings", []):
                # housings carry no published mass; they are counted, not weighed
                hmass += 0.0
            cable_rows.append({"id": cid, "file": sfile, "length_mm": round(L, 4),
                               "mass_g": round(cable_mass, 6), "samples": n,
                               "bodies": {names[b]: round(v / n * cable_mass, 6) for b, v in hit.items()},
                               "housings": len(c.get("housings", [])),
                               "housing_mass_g": "CANNOT DETERMINE - no vendor mass for the JST housings/contacts"})
    detail["cables"] = cable_rows

    # ---- assemble --------------------------------------------------------
    rows = []
    tot_mjcf = 0.0; tot_add = 0.0
    for i in range(model.nbody):
        if i == 0:
            continue
        m0 = float(model.body_mass[i]) * 1000.0            # g
        c0w = data.xipos[i] * 1000.0                        # world mm
        am = add[i]["mass_g"]
        acw = (add[i]["moment"] / am) if am > 0 else None
        m1 = m0 + am
        c1w = (m0 * c0w + (am * acw if am > 0 else 0.0)) / m1
        # body frame
        R = data.xmat[i].reshape(3, 3); p = data.xpos[i] * 1000.0
        c1b = R.T @ (c1w - p)
        c0b = R.T @ (c0w - p)
        rows.append({
            "body": names[i], "id": i,
            "mjcf_mass_g": round(m0, 6),
            "added_mass_g": round(am, 6),
            "added_pct": round(100.0 * am / m0, 4) if m0 > 0 else None,
            "augmented_mass_g": round(m1, 6),
            "mjcf_com_body_mm": [round(float(x), 5) for x in c0b],
            "augmented_com_body_mm": [round(float(x), 5) for x in c1b],
            "com_shift_mm": round(float(np.linalg.norm(c1b - c0b)), 5),
            "n_screws": sum(1 for f in detail["fasteners"] if f["body"] == names[i]),
        })
        tot_mjcf += m0; tot_add += am

    # whole-robot CoM at qpos0
    M0 = sum(r["mjcf_mass_g"] for r in rows)
    M1 = sum(r["augmented_mass_g"] for r in rows)
    com0 = np.zeros(3); com1 = np.zeros(3)
    for i in range(1, model.nbody):
        m0 = float(model.body_mass[i]) * 1000.0
        com0 += m0 * data.xipos[i] * 1000.0
        am = add[i]["mass_g"]
        com1 += m0 * data.xipos[i] * 1000.0 + (add[i]["moment"] if am > 0 else 0.0)
    com0 /= M0; com1 /= M1

    out = {
        "$what": "the augmented per-body inertial model: MJCF links + measured fasteners + measured harness",
        "$generated_by": "sim/mass_budget.py",
        "inputs": {
            "mjcf": "sim/microduck_ours.xml",
            "fasteners": "out/fasteners/placed.json x out/open/screw-volumes.json (built solids, class 8.8 steel 7.85 g/cm3)",
            "harness": "out/wiring/solids.json + solids-hat.json (copper 8.96 + PVC jacket 1.38 g/cm3, jacket OD nominal)",
            "attribution": "world AABB per body from every geom's mesh vertices at qpos0; nearest-AABB assignment; cables resampled at %.1f mm and attributed PER SAMPLE" % SAMPLE_MM,
        },
        "totals_g": {
            "mjcf_links": round(M0, 5),
            "fasteners": round(sum(f["mass_g"] for f in detail["fasteners"]), 5),
            "harness_cable": round(sum(c["mass_g"] for c in cable_rows), 5),
            "augmented": round(M1, 5),
            "delta_pct": round(100.0 * (M1 - M0) / M0, 4),
        },
        "counts": {
            "bodies": len(rows), "screws_attributed": len(detail["fasteners"]),
            "screws_further_than_5mm_from_any_body": far_screws,
            "cables_attributed": len(cable_rows),
            "connector_housings_counted_not_weighed": sum(c["housings"] for c in cable_rows),
        },
        "com_at_qpos0_world_mm": {
            "mjcf": [round(float(x), 5) for x in com0],
            "augmented": [round(float(x), 5) for x in com1],
            "shift_mm": round(float(np.linalg.norm(com1 - com0)), 5),
        },
        "missing_mass": [
            "JST EH/GH housings and crimp contacts: counted (%d) but no vendor mass is published; CANNOT DETERMINE"
            % sum(c["housings"] for c in cable_rows),
            "no nuts, washers or heat-set inserts exist in this design (out/fasteners/inserts.json: 0 surviving candidates of 355 bores)",
            "adhesive, thread-lock, labels and the battery's own wiring pigtail are not modelled",
        ],
        "bodies": rows,
        "detail": detail,
    }
    json.dump(out, open(os.path.join(OUT, "mass-budget.json"), "w"), indent=1)
    print("MJCF %.4f g + screws %.4f g + harness %.4f g = %.4f g  (+%.3f %%)"
          % (M0, out["totals_g"]["fasteners"], out["totals_g"]["harness_cable"], M1,
             out["totals_g"]["delta_pct"]))
    print("CoM at qpos0 shifts %.4f mm" % out["com_at_qpos0_world_mm"]["shift_mm"])
    print("screws further than 5 mm from any body AABB:", far_screws)


if __name__ == "__main__":
    main()
