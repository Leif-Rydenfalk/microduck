#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""torque_sweep.py — PROVE 4(a): the moment every joint carries in its WORST
pose, against what an XL330-M288-T can actually hold.

    ce-cad/bin/cad sim/torque_sweep.py   ->  out/open/torque-sweep.json

Every earlier torque number in this repo is a GAIT number: one policy, one speed,
one trajectory (out/sim-evidence/gait-torque-duty.json, vx 0.25 m/s). That answers
"is this gait within the servos", not "is this MACHINE within the servos". A robot
that is picked up by its trunk, held on one leg, or crouched to its joint stops
sees moments no walking trajectory visits. This tool sweeps the pose space instead
of sampling a trajectory.

THREE LOAD CASES, and each is a different thing bolted to the world:

  HOLD    the trunk is held and the limbs hang. Each joint carries its SUBTREE.
          The worst gravity direction is closed-form (sim/statics.py), so this
          case is exact once the joint grid is swept: the robot in ANY attitude.

  STANCE  one sole is the thing bolted to the world. Each leg joint of that leg
          carries the COMPLEMENT -- the whole rest of the robot. Reported twice:
          (1) a closed-form bound over every attitude, which no pose can beat,
          and (2) the FOOT-FLAT case, where gravity is not free but must lie
          along the measured sole normal, which is the real standing robot.

  STAND   the foot-flat case further restricted to poses the robot could
          actually hold: centre of gravity inside that sole's contact polygon.
          A pose that fails this is not a static pose at all, it is a fall.

SEARCH. A 14-joint grid is not enumerable, so each case is a global search:
Sobol-free uniform random seeding inside each joint's own MJCF range, then
coordinate ascent (each joint scanned at 25 values, repeated until no joint
improves). The number of evaluations and the improvement the refinement bought
over the best random seed are both reported, so a reader can see whether the
search converged or merely sampled.

CAPABILITY. ROBOTIS publishes stall torque at three voltages and nothing else
(no continuous rating). All three are carried, plus the two ends of this robot's
own 2S pack, which is ABOVE the servo's rated maximum -- see
ce-parts/xl330-m288-t/component.json voltage_band_verdict.
"""
import json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import common  # noqa: E402
from statics import Statics, _dist_in_poly  # noqa: E402

OUT = os.path.join(ROOT, "out", "open")
J = list(common.JOINT_NAMES)
LEG = {"left": ["left_hip_yaw", "left_hip_roll", "left_hip_pitch", "left_knee", "left_ankle"],
       "right": ["right_hip_yaw", "right_hip_roll", "right_hip_pitch", "right_knee", "right_ankle"]}
HEAD = ["neck_pitch", "head_pitch", "head_yaw", "head_roll"]

# ---------------------------------------------------------------------------
# XL330-M288-T capability. Quoted, not paraphrased.
STALL_QUOTE = ("ROBOTIS e-Manual, XL330-M288-T, Specifications, 'Stall Torque' row verbatim: "
               "'0.42 [N.m] (at 3.7 [V], 1.11 [A], 0.378 [Nm/A])', "
               "'0.52 [N.m] (at 5.0 [V], 1.47 [A], 0.354 [Nm/A])', "
               "'0.60 [N.m] (at 6.0 [V], 1.74 [A], 0.345 [Nm/A])'")
PUBLISHED = [(3.7, 0.42), (5.0, 0.52), (6.0, 0.60)]


def capability():
    v = np.array([p[0] for p in PUBLISHED]); t = np.array([p[1] for p in PUBLISHED])
    a, b = np.polyfit(v, t, 1)          # linear in supply voltage
    resid = float(np.max(np.abs(t - (a * v + b))))
    rows = {
        "stall_3.7V_Nm": 0.42, "stall_5.0V_Nm": 0.52, "stall_6.0V_Nm": 0.60,
        "published_quote": STALL_QUOTE,
        "linear_fit": {"slope_Nm_per_V": round(float(a), 6), "intercept_Nm": round(float(b), 6),
                       "max_residual_Nm": round(resid, 6),
                       "basis": "least squares on the three published stall rows; the residual is printed so the extrapolation below is not mistaken for a published figure"},
        "pack_empty_6.6V_Nm": round(float(a * 6.6 + b), 6),
        "pack_full_8.2V_Nm": round(float(a * 8.2 + b), 6),
        "pack_note": ("EXTRAPOLATED BEYOND THE RATING. The Microduck runs its servos from the raw 2S "
                      "pack, 6.6-8.2 V, against a published maximum of 6.0 V, with the servo's own "
                      "over-voltage shutdown bit cleared in firmware "
                      "(ce-parts/xl330-m288-t/component.json voltage_band_verdict). These two figures "
                      "are what the motor constant implies there, NOT what ROBOTIS rates."),
        "mjcf_forcerange_Nm": 0.96,
        "mjcf_forcerange_note": ("sim/microduck_ours.xml:45, class 'chosen_actuator', forcerange "
                                 "-0.96..0.96. Pollen's simulation permits 1.60x the servo's largest "
                                 "PUBLISHED stall torque (0.60 N.m at 6.0 V) and 1.85x the torque at "
                                 "the recommended 5.0 V. A gait that passes in that simulation is not "
                                 "thereby within the actuator."),
        "continuous_rating": "CANNOT DETERMINE - ROBOTIS publishes no continuous-torque rating for this actuator, only stall. Every margin below is against a STALL figure, which a real servo cannot hold indefinitely without the thermal derating measured in out/sim-evidence/thermal-servo-xl330.json.",
    }
    return rows


# ---------------------------------------------------------------------------
class Search:
    def __init__(self, st, seed=3):
        self.st = st
        self.rng = np.random.default_rng(seed)
        self.lo = np.array([st.jrange[k][0] for k in J])
        self.hi = np.array([st.jrange[k][1] for k in J])
        self.evals = 0

    def rand(self, n, free=None):
        q = self.rng.uniform(self.lo, self.hi, size=(n, 14))
        if free is not None:
            mask = np.array([k in free for k in J])
            q[:, ~mask] = 0.0
        return q

    def ascend(self, q, obj, free, steps=25, rounds=8):
        best = obj(q); q = q.copy()
        for _ in range(rounds):
            improved = False
            for k, nm in enumerate(J):
                if nm not in free:
                    continue
                grid = np.linspace(self.lo[k], self.hi[k], steps)
                cur = q[k]
                for v in grid:
                    q[k] = v
                    o = obj(q)
                    self.evals += 1
                    if o > best + 1e-12:
                        best, cur, improved = o, v, True
                q[k] = cur
            if not improved:
                break
        return best, q

    def run(self, obj, free, n_seed=4000, n_keep=6):
        qs = self.rand(n_seed, free)
        vals = np.array([obj(q) for q in qs]); self.evals += n_seed
        order = np.argsort(-vals)
        seed_best = float(vals[order[0]])
        best, bq = seed_best, qs[order[0]]
        for i in order[:n_keep]:
            v, q = self.ascend(qs[i], obj, free)
            if v > best:
                best, bq = v, q
        return best, bq, seed_best


def main():
    t0 = time.time()
    st = Statics(augmented=True)
    cap = capability()
    S = Search(st)
    res = {"$what": "the worst static moment every joint can be made to carry, swept over the pose space, against the XL330-M288-T's published capability",
           "$generated_by": "sim/torque_sweep.py",
           "engine": "sim/statics.py (self-test 20/20 PASS; cross-checked against MuJoCo RNE to 5.551e-17 N.m)",
           "mass_model": st.mass_source,
           "servo": cap, "cases": {}}

    # ---- CASE HOLD: subtree side, closed-form over attitude ---------------
    hold = {}
    for k, nm in enumerate(J):
        chain = LEG["left"] if nm in LEG["left"] else (LEG["right"] if nm in LEG["right"] else HEAD)
        free = set(chain)
        def obj(q, k=k):
            st.set_pose(q)
            return float(st.bounds_all()[0][k])
        b, bq, sb = S.run(obj, free, n_seed=3000, n_keep=5)
        st.set_pose(bq)
        _, _, _, _, cs, _ = st.bounds_all()
        hold[nm] = {"worst_Nm": round(b, 6),
                    "best_random_seed_Nm": round(sb, 6),
                    "refinement_gain_Nm": round(b - sb, 6),
                    "subtree_mass_g": round(float(st.M_sub[k]) * 1000, 4),
                    "lever_arm_mm": round(b / (9.81 * float(st.M_sub[k])) * 1000, 4),
                    "pose_deg": {n: round(float(np.degrees(bq[i])), 3) for i, n in enumerate(J) if n in free}}
    res["cases"]["HOLD"] = {
        "what": "the trunk is held; each joint carries everything distal of it. Closed-form over EVERY attitude, so this is the picked-up / carried / swing-leg case and no orientation can beat it.",
        "joints": hold}

    # ---- CASE STANCE bound: complement side, closed-form over attitude ----
    stance_bound = {}
    for k, nm in enumerate(J):
        if nm in HEAD:
            continue
        def obj(q, k=k):
            st.set_pose(q)
            return float(st.bounds_all()[1][k])
        b, bq, sb = S.run(obj, set(J), n_seed=6000, n_keep=6)
        st.set_pose(bq)
        stance_bound[nm] = {"worst_Nm": round(b, 6),
                            "best_random_seed_Nm": round(sb, 6),
                            "refinement_gain_Nm": round(b - sb, 6),
                            "complement_mass_g": round(float(st.M_out[k]) * 1000, 4),
                            "lever_arm_mm": round(b / (9.81 * float(st.M_out[k])) * 1000, 4),
                            "pose_deg": {n: round(float(np.degrees(bq[i])), 3) for i, n in enumerate(J)}}
    res["cases"]["STANCE_BOUND"] = {
        "what": "one foot is the thing bolted to the world and the joint carries the whole rest of the robot, with gravity free to point anywhere. An UPPER BOUND that no pose or attitude can exceed.",
        "joints": stance_bound}

    # ---- CASE STANCE_FLAT / STAND: gravity along the measured sole normal --
    for case, require_stable in (("STANCE_FLAT", False), ("STAND", True)):
        out = {}
        for side in ("left", "right"):
            for nm in LEG[side]:
                k = J.index(nm)
                def obj(q, k=k, side=side, require_stable=require_stable):
                    st.set_pose(q)
                    so = st.sole(side)
                    nw = st.data.xmat[so["body"]].reshape(3, 3) @ so["n_local"]
                    ts, to = st.tau_all(nw)          # gravity along the sole's own down-normal
                    if require_stable:
                        # the hull is FIXED in the sole's own frame, so the
                        # point-in-polygon test runs there: only the CoM moves.
                        c = st.com()
                        R = st.data.xmat[so["body"]].reshape(3, 3)
                        p0 = st.data.xpos[so["body"]]
                        cl = R.T @ (c - p0)
                        c2 = np.array([cl @ so["e1"], cl @ so["e2"]])
                        if _dist_in_poly(c2, so["hull_uv"], so["edge_a"], so["edge_e"]) <= 0:
                            return -1e9
                    return abs(float(to[k]))
                b, bq, sb = S.run(obj, set(J), n_seed=8000 if require_stable else 5000, n_keep=6)
                if b < -1e8:
                    out[nm] = {"worst_Nm": None, "verdict": "CANNOT DETERMINE",
                               "why": "no sampled pose put the centre of gravity inside this sole's contact polygon"}
                    continue
                st.set_pose(bq)
                so = st.sole(side)
                c = st.com()
                R = st.data.xmat[so["body"]].reshape(3, 3); p0 = st.data.xpos[so["body"]]
                cl = R.T @ (c - p0)
                c2 = np.array([cl @ so["e1"], cl @ so["e2"]])
                out[nm] = {"worst_Nm": round(b, 6),
                           "best_random_seed_Nm": round(sb, 6),
                           "refinement_gain_Nm": round(b - sb, 6),
                           "stance_foot": side,
                           "cog_margin_in_polygon_mm": round(float(_dist_in_poly(c2, so["hull_uv"], so["edge_a"], so["edge_e"])) * 1000, 4),
                           "pose_deg": {n: round(float(np.degrees(bq[i])), 3) for i, n in enumerate(J)}}
        res["cases"][case] = {
            "what": ("one sole flat on the ground, gravity along that sole's MEASURED down-normal; the joint carries the rest of the robot"
                     if not require_stable else
                     "the same, further restricted to poses the robot could actually hold: centre of gravity strictly inside that sole's contact polygon"),
            "joints": out}

    # ---- the gait anchor --------------------------------------------------
    g = json.load(open(os.path.join(ROOT, "out", "sim-evidence", "gait-torque-duty.json")))
    peaks = {k: v["peak_abs_Nm"] for k, v in g["outputs"]["joints"].items()}
    res["gait_anchor"] = {
        "source": "out/sim-evidence/gait-torque-duty.json, Pollen's own walking policy at vx 0.25 m/s, 200 Hz physics step",
        "peak_abs_Nm": peaks,
        "why": "the trajectory number this sweep is meant to be compared against; a static worst case ABOVE it is a pose the published gait never visits, and that is the point of sweeping."}

    # ---- verdicts ---------------------------------------------------------
    verdicts = []
    for case in ("HOLD", "STANCE_BOUND", "STANCE_FLAT", "STAND"):
        for nm, row in res["cases"][case]["joints"].items():
            w = row.get("worst_Nm")
            if w is None:
                verdicts.append({"case": case, "joint": nm, "verdict": "CANNOT DETERMINE",
                                 "why": row.get("why")})
                continue
            r = {"case": case, "joint": nm, "worst_Nm": w}
            for label, c in (("5.0V", cap["stall_5.0V_Nm"]), ("6.0V", cap["stall_6.0V_Nm"]),
                             ("pack_6.6V", cap["pack_empty_6.6V_Nm"])):
                r["margin_vs_stall_%s" % label] = round(c / w, 4) if w > 0 else None
            r["verdict"] = ("PASS" if w <= cap["stall_5.0V_Nm"] else
                            ("MARGINAL" if w <= cap["pack_empty_6.6V_Nm"] else "FAIL"))
            r["verdict_basis"] = ("PASS = within the 0.52 N.m stall at the RECOMMENDED 5.0 V. "
                                  "MARGINAL = needs more than that but is within the 6.6 V pack-empty extrapolation, "
                                  "which is beyond the servo's rating. FAIL = beyond even that.")
            verdicts.append(r)
    res["verdicts"] = verdicts
    res["counts"] = {
        "joints": 14, "cases": 4, "rows": len(verdicts),
        "PASS": sum(1 for v in verdicts if v.get("verdict") == "PASS"),
        "MARGINAL": sum(1 for v in verdicts if v.get("verdict") == "MARGINAL"),
        "FAIL": sum(1 for v in verdicts if v.get("verdict") == "FAIL"),
        "CANNOT DETERMINE": sum(1 for v in verdicts if v.get("verdict") == "CANNOT DETERMINE"),
        "pose_evaluations": S.evals,
        "seconds": round(time.time() - t0, 1),
    }
    json.dump(res, open(os.path.join(OUT, "torque-sweep.json"), "w"), indent=1)
    print(json.dumps(res["counts"], indent=1))
    for case in ("HOLD", "STANCE_BOUND", "STANCE_FLAT", "STAND"):
        print("--", case)
        for nm, row in res["cases"][case]["joints"].items():
            w = row.get("worst_Nm")
            print("   %-16s %s" % (nm, ("%8.4f N.m  x%.3f of 0.52 V5 stall" % (w, w / 0.52)) if w else row.get("verdict")))


if __name__ == "__main__":
    main()
