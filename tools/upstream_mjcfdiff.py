#!/usr/bin/env python3
"""tools/upstream_mjcfdiff.py — numeric diff of Pollen's robot_walk.xml
(pinned 5946fd9 copy vs develop 29e887e) and of ours (sim/microduck_ours.xml),
plus what SPEC.md §3 publishes. Pure stdlib. Writes
out/sources/upstream-develop-mjcfdiff.json. Angles in degrees, lengths in mm,
masses in g. A difference below `eps` is float noise from onshape-to-robot's
re-export and is reported as such, not hidden.
"""
import json, math, os, re, sys, time
import xml.etree.ElementTree as ET

R = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck"
FILES = {
    "old_5946fd9": f"{R}/reference/pollen-microduck-rl/robot_walk.xml",
    "new_29e887e": f"{R}/reference/pollen-microduck-rl-develop/microduck/robot_walk.xml",
    "ours": f"{R}/sim/microduck_ours.xml",
}
EPS_DEG, EPS_MM, EPS_G = 1e-6, 1e-4, 1e-4

def floats(s):
    return [float(x) for x in s.split()] if s else []

def walk(body, parent, acc, depth=0):
    name = body.get("name")
    acc["bodies"][name] = {"parent": parent, "pos_mm": [round(v*1000, 4) for v in floats(body.get("pos", "0 0 0"))],
                           "quat": floats(body.get("quat", "1 0 0 0"))}
    inert = body.find("inertial")
    if inert is not None:
        acc["inertials"][name] = {"mass_g": round(float(inert.get("mass"))*1000, 4),
                                  "com_mm": [round(v*1000, 4) for v in floats(inert.get("pos"))],
                                  "fullinertia_kgm2": floats(inert.get("fullinertia"))}
    for j in body.findall("joint"):
        rng = floats(j.get("range", ""))
        acc["joints"][j.get("name")] = {"body": name, "axis": floats(j.get("axis", "0 0 1")),
                                        "range_deg": [round(math.degrees(v), 6) for v in rng], "class": j.get("class")}
    for g in body.findall("geom"):
        acc["geoms"].append({"body": name, "mesh": g.get("mesh"), "class": g.get("class"), "type": g.get("type"),
                             "pos_mm": [round(v*1000, 4) for v in floats(g.get("pos", "0 0 0"))], "quat": floats(g.get("quat", "1 0 0 0")),
                             "material": g.get("material")})
    for s in body.findall("site"):
        acc["sites"][s.get("name")] = {"body": name, "pos_mm": [round(v*1000, 4) for v in floats(s.get("pos", "0 0 0"))]}
    for b in body.findall("body"):
        walk(b, name, acc, depth+1)

def load(path):
    root = ET.parse(path).getroot()
    acc = {"file": path, "bodies": {}, "inertials": {}, "joints": {}, "geoms": [], "sites": {}, "materials": {}, "meshes": [],
           "defaults": {}, "actuators": {}, "keyframes": {}, "option": {}}
    for wb in root.find("worldbody").findall("body"):
        walk(wb, None, acc)
    a = root.find("asset")
    if a is not None:
        for m in a.findall("material"):
            acc["materials"][m.get("name")] = m.get("rgba")
        for m in a.findall("mesh"):
            acc["meshes"].append(m.get("file"))
    def defaults(d, prefix=""):
        for c in d.findall("default"):
            nm = c.get("class") or "(root)"
            acc["defaults"][nm] = {ch.tag: dict(ch.attrib) for ch in c if ch.tag != "default"}
            defaults(c, nm)
    for d in root.findall("default"):
        defaults(d)
    act = root.find("actuator")
    if act is not None:
        for m in act:
            acc["actuators"][m.get("name")] = dict(m.attrib)
    kf = root.find("keyframe")
    if kf is not None:
        for k in kf.findall("key"):
            acc["keyframes"][k.get("name")] = dict(k.attrib)
    o = root.find("option")
    if o is not None:
        acc["option"] = dict(o.attrib)
    acc["counts"] = {k: len(acc[k]) for k in ("bodies", "inertials", "joints", "geoms", "sites", "materials", "meshes")}
    acc["mesh_names_used"] = sorted(set(g["mesh"] for g in acc["geoms"] if g["mesh"]))
    return acc

def d(a, b, eps):
    if a is None or b is None:
        return None
    if isinstance(a, list):
        return [round(y - x, 6) for x, y in zip(a, b)]
    return round(b - a, 6)

def maxabs(v):
    if v is None:
        return None
    if isinstance(v, list):
        return max(abs(x) for x in v) if v else 0.0
    return abs(v)

models = {k: load(p) for k, p in FILES.items() if os.path.exists(p)}
out = {"generated": time.strftime("%Y-%m-%d %H:%M:%S %z"), "files": FILES, "eps": {"deg": EPS_DEG, "mm": EPS_MM, "g": EPS_G},
       "counts": {k: m["counts"] for k, m in models.items()}, "joints": {}, "inertials": {}, "bodies": {}, "materials": {}, "sites": {},
       "meshes_used": {}, "defaults": {}, "actuators": {}, "keyframes": {}, "option": {}}
O, N = models["old_5946fd9"], models["new_29e887e"]
U = models.get("ours")
for j in sorted(set(O["joints"]) | set(N["joints"])):
    o, n = O["joints"].get(j), N["joints"].get(j)
    u = U["joints"].get(j) if U else None
    row = {"old_deg": o and o["range_deg"], "new_deg": n and n["range_deg"], "ours_deg": u and u["range_deg"]}
    dd = d(o and o["range_deg"], n and n["range_deg"], EPS_DEG)
    row["new_minus_old_deg"] = dd
    row["verdict_old_vs_new"] = "MISSING" if dd is None else ("SAME" if maxabs(dd) <= EPS_DEG else "CHANGED")
    du = d(u and u["range_deg"], n and n["range_deg"], EPS_DEG)
    row["new_minus_ours_deg"] = du
    row["verdict_ours_vs_new"] = "MISSING" if du is None else ("SAME" if maxabs(du) <= EPS_DEG else "CHANGED")
    out["joints"][j] = row
for b in sorted(set(O["inertials"]) | set(N["inertials"])):
    o, n = O["inertials"].get(b), N["inertials"].get(b)
    u = U["inertials"].get(b) if U else None
    row = {"old_mass_g": o and o["mass_g"], "new_mass_g": n and n["mass_g"], "ours_mass_g": u and u["mass_g"],
           "old_com_mm": o and o["com_mm"], "new_com_mm": n and n["com_mm"]}
    dm = d(o and o["mass_g"], n and n["mass_g"], EPS_G); dc = d(o and o["com_mm"], n and n["com_mm"], EPS_MM)
    row["new_minus_old_mass_g"] = dm; row["new_minus_old_com_mm"] = dc
    di = d(o and o["fullinertia_kgm2"], n and n["fullinertia_kgm2"], 0)
    row["new_minus_old_fullinertia_kgm2"] = di
    row["max_rel_inertia_change"] = (max(abs(x)/max(abs(y), 1e-12) for x, y in zip(di, o["fullinertia_kgm2"])) if di and o else None)
    row["verdict"] = "MISSING" if dm is None else ("SAME" if maxabs(dm) <= EPS_G and maxabs(dc) <= EPS_MM else "CHANGED")
    row["verdict_ours_vs_new"] = "MISSING" if (u is None or n is None) else ("SAME" if abs(u["mass_g"] - n["mass_g"]) <= EPS_G else "CHANGED")
    out["inertials"][b] = row
out["total_mass_g"] = {k: round(sum(v["mass_g"] for v in m["inertials"].values()), 4) for k, m in models.items()}
for b in sorted(set(O["bodies"]) | set(N["bodies"])):
    o, n = O["bodies"].get(b), N["bodies"].get(b)
    dp = d(o and o["pos_mm"], n and n["pos_mm"], EPS_MM)
    qo = o and [abs(x) for x in o["quat"]]; qn = n and [abs(x) for x in n["quat"]]
    out["bodies"][b] = {"old_pos_mm": o and o["pos_mm"], "new_pos_mm": n and n["pos_mm"], "new_minus_old_mm": dp,
                        "old_quat": o and o["quat"], "new_quat": n and n["quat"],
                        "quat_sign_only": bool(o and n and all(abs(x-y) < 1e-6 for x, y in zip(qo, qn)) and o["quat"] != n["quat"]),
                        "verdict": "MISSING" if dp is None else ("SAME" if maxabs(dp) <= EPS_MM else "CHANGED")}
for s in sorted(set(O["sites"]) | set(N["sites"])):
    o, n = O["sites"].get(s), N["sites"].get(s)
    dp = d(o and o["pos_mm"], n and n["pos_mm"], EPS_MM)
    out["sites"][s] = {"old_pos_mm": o and o["pos_mm"], "new_pos_mm": n and n["pos_mm"], "new_minus_old_mm": dp,
                       "verdict": "MISSING" if dp is None else ("SAME" if maxabs(dp) <= EPS_MM else "CHANGED")}
for m in sorted(set(O["materials"]) | set(N["materials"])):
    o, n = O["materials"].get(m), N["materials"].get(m)
    def hexof(s):
        if not s: return None
        v = floats(s)[:3]; return "#%02x%02x%02x" % tuple(int(round(x*255)) for x in v)
    out["materials"][m] = {"old_rgba": o, "new_rgba": n, "old_hex": hexof(o), "new_hex": hexof(n),
                           "ours_rgba": (U["materials"].get(m) if U else None),
                           "verdict": "MISSING" if (o is None or n is None) else ("SAME" if o == n else "CHANGED")}
out["meshes_used"] = {"old": O["mesh_names_used"], "new": N["mesh_names_used"], "ours": U and U["mesh_names_used"],
                      "only_old": sorted(set(O["mesh_names_used"]) - set(N["mesh_names_used"])),
                      "only_new": sorted(set(N["mesh_names_used"]) - set(O["mesh_names_used"]))}
# geom placements (visual): match by (body, mesh, class) and diff pos
def gkey(g): return (g["body"], g["mesh"], g["class"])
og = {}; ng = {}
for g in O["geoms"]: og.setdefault(gkey(g), []).append(g)
for g in N["geoms"]: ng.setdefault(gkey(g), []).append(g)
gd = []
for k in sorted(set(og) | set(ng), key=str):
    a, b = og.get(k, []), ng.get(k, [])
    if len(a) != len(b):
        gd.append({"body": k[0], "mesh": k[1], "class": k[2], "old_count": len(a), "new_count": len(b), "verdict": "COUNT_CHANGED"}); continue
    for x, y in zip(a, b):
        dp = d(x["pos_mm"], y["pos_mm"], EPS_MM)
        qs = [abs(p) for p in x["quat"]] != [abs(p) for p in y["quat"]] and not all(abs(abs(p)-abs(q)) < 1e-6 for p, q in zip(x["quat"], y["quat"]))
        if maxabs(dp) > EPS_MM or qs:
            gd.append({"body": k[0], "mesh": k[1], "class": k[2], "old_pos_mm": x["pos_mm"], "new_pos_mm": y["pos_mm"], "new_minus_old_mm": dp,
                       "old_quat": x["quat"], "new_quat": y["quat"], "verdict": "CHANGED"})
out["geom_placement_changes"] = gd
out["geom_count"] = {"old": len(O["geoms"]), "new": len(N["geoms"]), "ours": U and len(U["geoms"])}
for k in ("defaults", "actuators", "keyframes", "option"):
    out[k] = {"old": O[k], "new": N[k], "ours": U and U[k], "same_old_new": O[k] == N[k]}
summary = {
    "joints_changed_beyond_eps": [j for j, r in out["joints"].items() if r["verdict_old_vs_new"] == "CHANGED"],
    "joints_max_abs_change_deg": max((maxabs(r["new_minus_old_deg"]) or 0) for r in out["joints"].values()),
    "inertials_changed": [b for b, r in out["inertials"].items() if r["verdict"] == "CHANGED"],
    "mass_max_abs_change_g": max((maxabs(r["new_minus_old_mass_g"]) or 0) for r in out["inertials"].values()),
    "com_max_abs_change_mm": max((maxabs(r["new_minus_old_com_mm"]) or 0) for r in out["inertials"].values()),
    "bodies_moved": [b for b, r in out["bodies"].items() if r["verdict"] == "CHANGED"],
    "sites_moved": [s for s, r in out["sites"].items() if r["verdict"] == "CHANGED"],
    "materials_changed": [m for m, r in out["materials"].items() if r["verdict"] == "CHANGED"],
    "materials_same": [m for m, r in out["materials"].items() if r["verdict"] == "SAME"],
    "geom_placement_changes": len(gd),
    "ours_vs_new_joints_changed": [j for j, r in out["joints"].items() if r["verdict_ours_vs_new"] == "CHANGED"],
    "ours_vs_new_mass_changed": [b for b, r in out["inertials"].items() if r["verdict_ours_vs_new"] == "CHANGED"],
}
out["summary"] = summary
os.makedirs(f"{R}/out/sources", exist_ok=True)
json.dump(out, open(f"{R}/out/sources/upstream-develop-mjcfdiff.json", "w"), indent=1)
print(json.dumps(summary, indent=1))
print("total_mass_g", out["total_mass_g"])
print("counts", out["counts"])
print("meshes only_old", out["meshes_used"]["only_old"], "only_new", out["meshes_used"]["only_new"])
for j, r in out["joints"].items():
    print("J", j, r["old_deg"], "->", r["new_deg"], "d=", r["new_minus_old_deg"], "ours", r["ours_deg"], r["verdict_ours_vs_new"])
for b, r in out["inertials"].items():
    print("I", b, r["old_mass_g"], "->", r["new_mass_g"], "dcom", r["new_minus_old_com_mm"], "relI", r["max_rel_inertia_change"], "ours", r["ours_mass_g"])
for m, r in out["materials"].items():
    print("M", m, r["old_hex"], "->", r["new_hex"], r["verdict"], "ours", r["ours_rgba"])
for g in gd: print("G", g)
print("defaults same:", out["defaults"]["same_old_new"], "actuators same:", out["actuators"]["same_old_new"], "keyframes same:", out["keyframes"]["same_old_new"], "option same:", out["option"]["same_old_new"])
