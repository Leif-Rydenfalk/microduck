#!/usr/bin/env python3
"""fit_sweep_depth.py — how DEEP is each range collision that prove_fit.py sweep
found, at the angle the robot actually uses?

sweep.json reports the angle at which a clear-at-rest pair first shares space.
A crossing-triangle test cannot tell a faceted bearing turning in its bore
(contact, depth ~0.01 mm) from a servo driving into a shell (depth in mm).
This tool re-poses every sweep hit at two angles and measures penetration:

  sample   the first sampled angle past onset (onset + at most 5 deg)
  used     the edge of the motion envelope the published policies drive on
           that side, from out/motion/legs.json (walking + sit/stand union) and
           out/motion/head.json (sine amplitude and slot crosstalk peaks).
           If the collision only begins beyond that edge, `used` is measured at
           the MJCF range end instead and the row is flagged outside_envelope.

    ce-cad/bin/cad tools/fit_sweep_depth.py   -> out/fit/sweep-depth.json
"""
import json, os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.argv = [sys.argv[0], "sweep-depth"]
sys.path.insert(0, os.path.join(REPO, "tools"))
import prove_fit as pf
from cecad import meshfit as mf

legs = json.load(open(os.path.join(REPO, "out/motion/legs.json")))
head = json.load(open(os.path.join(REPO, "out/motion/head.json")))
env = {}
for key in ("walking_policy", "sitstand_policy"):
    for jn, v in legs[key]["joints"].items():
        lo, hi = env.get(jn, (0.0, 0.0))
        env[jn] = (min(lo, v["min_deg"]), max(hi, v["max_deg"]))
for j in head["joints"]:
    amp = j.get("sine_achieved_amp_deg", 0.0)
    for s in head.get("slot_crosstalk", []):
        amp = max(amp, s["peak_deg_per_joint"].get(j["joint"], 0.0))
    lo, hi = j["mjcf_range_deg"]
    env[j["joint"]] = (max(lo, -amp), min(hi, amp))
env_src = {"legs": "out/motion/legs.json walking_policy + sitstand_policy joints min/max (union)",
           "head": "out/motion/head.json joints[].sine_achieved_amp_deg and slot_crosstalk peaks (max), clamped to MJCF range"}

M = pf.Model()
idx = {lab: i for i, lab in enumerate(M.label)}
sweep = json.load(open(os.path.join(pf.OUT, "sweep.json")))
t0 = time.time()
rows = []
for J in sweep["joints"]:
    jn = J["joint"]; rlo, rhi = J["range_deg"]; elo, ehi = env[jn]
    # group by angle so each pose is built once
    plan = {}
    for h in J["collisions_begin"]:
        side = h["side"]; b = h["begins_deg"]
        edge = ehi if side == "+" else elo
        outside = (b > ehi) if side == "+" else (b < elo)
        used_angle = (rhi if side == "+" else rlo) if outside else edge
        for tag, ang in (("sample", h["sample_deg"]), ("used", used_angle)):
            plan.setdefault(float(ang), []).append((h, tag, outside))
    for ang, items in sorted(plan.items()):
        Wf = M.world(M.body_frames(M.qpos_for({jn: ang})))
        for h, tag, outside in items:
            a, b = idx[h["a"]], idx[h["b"]]
            # labels can repeat (two xl330 in one body); fall back to first match
            r = mf.measure_pair(Wf[a], Wf[b], volume=False, depth=True)
            pen = r.get("penetration") or {}
            dep = max(pen.get("a_in_b_mm", 0.0) or 0.0, pen.get("b_in_a_mm", 0.0) or 0.0) \
                if isinstance(pen, dict) and "a_in_b_mm" in pen else None
            rows.append({"joint": jn, "a": h["a"], "b": h["b"], "class": h["class"],
                         "side": h["side"], "begins_deg": h["begins_deg"],
                         "at": tag, "angle_deg": ang, "outside_envelope": outside,
                         "envelope_deg": [elo, ehi],
                         "interferes": r.get("interferes"),
                         "intersecting_tri_pairs": r.get("intersecting_tri_pairs"),
                         "depth_mm": dep, "penetration": pen if isinstance(pen, dict) else {"verdict": str(pen)}})
            pf.P("  %s %s x %s @%s %+.2f deg depth=%s%s" % (jn, h["a"], h["b"], tag, ang, dep, " (outside envelope)" if outside else ""))
    pf.P("joint %s done, %.1f s" % (jn, time.time() - t0))
out = {"$what": "penetration depth of every sweep range collision at the first sampled angle past onset and at the used-envelope edge",
       "envelope_deg": env, "envelope_sources": env_src, "rows": rows, "seconds": round(time.time() - t0, 1)}
json.dump(out, open(os.path.join(pf.OUT, "sweep-depth.json"), "w"), indent=1)
pf.P("DONE %d rows" % len(rows))
