#!/usr/bin/env python3
"""fatigue_walk.py — the walking-cycle fatigue check on EVERY part that has a
walk-peak FEA, not only the ankle (F1 skeptic finding 6, 2026-09-03: the brief
pointed at the ankle because a stale report had it at SF 2.02; after the
re-declaration it is the least loaded part, and the same design curve flags
eight others).

Same basis as sim/fatigue_ankle.py, applied uniformly:
  * cycles per km — sim/measure_loads.py (left-foot touchdowns, BEST_alpha_walking,
    vx 0.25 m/s): out/sim-evidence/loads_mujoco.json walk.gait
  * sigma_max     — each part's walk-peak FEA peak nodal von Mises
    (out/sim-evidence/fea_<part>_walk.json); the gait is pulsating on every
    part (stance loads, swing unloads) so R ~ 0 and sigma_max is the cycle max
  * S-N            — Ezeh & Susmel, Int J Fatigue 126 (2019) 319-326, FFF PLA
    printed flat, 100 % infill: the P_s >= 90 % DESIGN curve k = 5.5,
    sigma_MAX = 0.1 sigma_UTS at 2e6 (eqs 5-6), and Table 1's median R = 0
    row (theta_p 0: sigma_A50 6.1 MPa -> sigma_max 12.2 MPa at 2e6, k 7.4)
    as the P_s = 50 % estimate
  * UTS            — the paper's 42.6 MPa (theta_p 0) and the Prusament TDS 51 MPa
Life N = N_ref (sigma_endurance / sigma_max)^k, km = N / cycles_per_km.

Verdict per part (the lane's rule, stated because no requirement document sets
a walking life — docs/MANUFACTURING-REQUIREMENTS.md has none):
  PASS   sigma_max <= the design endurance on the least favourable basis
         (infinite life by the P_s >= 90 % curve)
  PASS   finite design life >= 10 km (the same threshold fatigue_ankle.py used)
  FAIL   design life < 10 km
  CANNOT DETERMINE  the walk FEA is itself a bound (sim/load_share.py), has no
         solve, or the material has no cited S-N curve (TPU)
Writes out/sim-evidence/fatigue_walk.json (one row per part). fatigue_ankle.json
(the ankle alone, with its mesh-scaled variant) is unchanged and still valid.
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EVID = os.path.join(ROOT, "out", "sim-evidence")
sys.path.insert(0, HERE)
from load_share import LOAD_SHARE  # noqa: E402

LIFE_KM_REQUIRED = 10.0
N_REF = 2e6
DESIGN_K = 5.5
MEDIAN_R0 = {"sigma_max_2e6_mpa": 12.2, "k": 7.4, "source": "Ezeh & Susmel 2019 Table 1, theta_p 0 deg, R = 0: sigma_A50 6.1 MPa (x2 for sigma_max), k 7.4"}
UTS = [("paper_theta0", 42.6, "Ezeh & Susmel 2019 Table 1, theta_p 0 deg (New Verbatim PLA, Ultimaker 2 Extended+)"),
       ("prusament_tds", 51.0, "research/tds/prusament-pla-tds-2021-10-en.pdf: 51 +- 3 MPa yield printed horizontal, used as UTS (brittle: yield and UTS coincide within tolerance)")]
SN = {"paper": "O.H. Ezeh, L. Susmel, 'Fatigue strength of additively manufactured polylactide (PLA): effect of raster angle and non-zero mean stresses', "
               "International Journal of Fatigue 126 (2019) 319-326, doi:10.1016/j.ijfatigue.2019.05.014",
      "file": "research/fatigue/ezeh-susmel-2019-ijfatigue-126-319-pla-fatigue.pdf",
      "sha256": "6539146573d830076e5f3b1ec0feca62fa64d08a255a1487da4e211404d7ae13",
      "design_curve": "P_s >= 90 %: k = 5.5, sigma_MAX = 0.1 sigma_UTS at N_ref = 2e6 cycles (eqs 5-6; 100 % infill printed flat; no notch factor)",
      "scatter": "T_sigma ~ 2.9 in terms of sigma_max across all angles and load ratios (Fig 9)"}


def life(sigma, s_end, k, cycles_per_km):
    if sigma <= 0:
        return float("inf"), float("inf")
    N = N_REF * (s_end / sigma) ** k
    return N, N / cycles_per_km


def main():
    L = json.load(open(os.path.join(EVID, "loads_mujoco.json")))
    g = L["walk"]["gait"]
    cpk = g["cycles_per_km"]
    rows = []
    for p in sorted(glob.glob(os.path.join(EVID, "fea_microduck-*_walk.json"))):
        r = json.load(open(p))
        o = r.get("outputs") or {}
        slug = r["part"].split(":", 1)[1]
        row = {"part": r["part"], "walk_study": os.path.relpath(p, ROOT), "material": r.get("material"), "force_N": r["inputs"].get("force_magnitude_N"),
               "sigma_max_mpa": o.get("max_von_mises_mpa"), "static_verdict": r.get("verdict"), "static_sf": (o.get("grading") or {}).get("sf_used", o.get("sf"))}
        if o.get("max_von_mises_mpa") is None:
            row.update(verdict="CANNOT DETERMINE", why="no walk solve exists (%s)" % r.get("why", "")[:160], what_settles_it="a mesh for the housing (fea_meshability) then the walk solve")
            rows.append(row); continue
        if (r.get("material") or "").upper() != "PLA":
            row.update(verdict="CANNOT DETERMINE",
                       why="no cited S-N curve for %s: the Ezeh & Susmel curve is PLA only, and no NinjaFlex 85A fatigue data was fetched; walk peak %.4f MPa against the TDS yield 4 MPa" % (
                           r.get("material"), o["max_von_mises_mpa"]),
                       what_settles_it="a cited TPU 85A S-N dataset (R = 0, 100 % infill), or a flex-fatigue coupon of the sole filament")
            rows.append(row); continue
        sigma = o["max_von_mises_mpa"]
        curves = []
        for label, uts, src in UTS:
            s_end = 0.1 * uts
            N, km = life(sigma, s_end, DESIGN_K, cpk)
            curves.append({"basis": label, "uts_mpa": uts, "uts_source": src, "design_endurance_sigma_max_2e6_mpa": round(s_end, 4), "k": DESIGN_K,
                           "sigma_over_endurance": round(sigma / s_end, 4), "cycles_design_Ps90": N, "life_km_design_Ps90": km})
        Nm, kmm = life(sigma, MEDIAN_R0["sigma_max_2e6_mpa"], MEDIAN_R0["k"], cpk)
        median = {"basis": "median_R0_theta0", "sigma_max_2e6_mpa": MEDIAN_R0["sigma_max_2e6_mpa"], "k": MEDIAN_R0["k"], "source": MEDIAN_R0["source"],
                  "sigma_over_endurance": round(sigma / MEDIAN_R0["sigma_max_2e6_mpa"], 4), "cycles_Ps50": Nm, "life_km_Ps50": kmm}
        worst = min(curves, key=lambda c: c["life_km_design_Ps90"])
        row.update(curves=curves, median_estimate=median, worst_basis=worst["basis"],
                   design_endurance_mpa_worst=worst["design_endurance_sigma_max_2e6_mpa"], sigma_over_endurance_worst=worst["sigma_over_endurance"],
                   life_km_design_Ps90_worst=(None if worst["cycles_design_Ps90"] > N_REF else worst["life_km_design_Ps90"]),
                   life_km_Ps50=(None if Nm > N_REF else kmm))
        if slug in LOAD_SHARE and r.get("verdict") == "CANNOT DETERMINE":
            row.update(verdict="CANNOT DETERMINE",
                       why="the walk stress %.4f MPa is itself a BOUND (100 %% of a shared force, sim/load_share.py): on the design curve it would be %s; nothing here measured the share" % (
                           sigma, ("infinite life" if worst["cycles_design_Ps90"] > N_REF else "%.4g km" % worst["life_km_design_Ps90"])),
                       what_settles_it=LOAD_SHARE[slug]["what_settles_it"])
        elif worst["cycles_design_Ps90"] > N_REF:
            row.update(verdict="PASS", why="walk peak %.4f MPa is %.1f %% of the P_s>=90 %% design endurance %.2f MPa (0.1 x UTS %.1f MPa) on the least favourable basis — infinite life by the design curve" % (
                sigma, 100 * worst["sigma_over_endurance"], worst["design_endurance_sigma_max_2e6_mpa"], worst["uts_mpa"]))
        else:
            km = worst["life_km_design_Ps90"]
            v = "PASS" if km >= LIFE_KM_REQUIRED else "FAIL"
            row.update(verdict=v, why="walk peak %.4f MPa is %.2fx the P_s>=90 %% design endurance %.2f MPa: design life %.4g cycles = %.4g km at %.1f cycles/km (median P_s 50 %% curve: %s km); "
                                       "lane threshold %g km -> %s" % (sigma, worst["sigma_over_endurance"], worst["design_endurance_sigma_max_2e6_mpa"], worst["cycles_design_Ps90"], km, cpk,
                                                                        ("%.4g" % kmm) if Nm <= N_REF else "infinite", LIFE_KM_REQUIRED, v))
        rows.append(row)
    n = {v: sum(1 for r in rows if r["verdict"] == v) for v in ("PASS", "FAIL", "CANNOT DETERMINE")}
    finite = [r for r in rows if r.get("life_km_design_Ps90_worst") is not None]
    worst = min(finite, key=lambda r: r["life_km_design_Ps90_worst"]) if finite else None
    verdict = "FAIL" if n["FAIL"] else ("CANNOT DETERMINE" if n["CANNOT DETERMINE"] else "PASS")
    out = {"study": "fatigue_walk", "generated": "2026-09-03", "script": "sim/fatigue_walk.py",
           "inputs": {"gait": {"period_s_mean": g["period_s_mean"], "period_s_min": g["period_s_min"], "period_s_max": g["period_s_max"], "n_cycles_measured": g["n_cycles"],
                               "stride_m_per_cycle": g["stride_m_per_cycle"], "cycles_per_km": cpk,
                               "source": "out/sim-evidence/loads_mujoco.json walk.gait (sim/measure_loads.py: left-foot touchdowns, BEST_alpha_walking vx 0.25 m/s, 8 s)"},
                      "sn_curve": SN, "median_R0": MEDIAN_R0, "uts_bases": [{"basis": a, "uts_mpa": b, "source": c} for a, b, c in UTS],
                      "load_ratio_R": "~0 on every part (stance loads, swing unloads)",
                      "life_km_required": {"value": LIFE_KM_REQUIRED, "source": "lane F1's own threshold (the one fatigue_ankle.py used); no requirement document sets a walking life — docs/MANUFACTURING-REQUIREMENTS.md has none"},
                      "stress_basis": "peak nodal von Mises of each part's walk-peak linear FEA — the worst point, unscaled for mesh (the ankle's convergence ratio 1.0221 is specific to its load path and is not applied to other parts)"},
           "method": "Basquin on the design curve: N = 2e6 (0.1 UTS / sigma_max)^5.5; life_km = N / cycles_per_km; median estimate N = 2e6 (12.2 / sigma_max)^7.4",
           "outputs": {"rows": rows, "counts": n, "worst_finite_life": ({"part": worst["part"], "life_km_design_Ps90": worst["life_km_design_Ps90_worst"]} if worst else None),
                       "cycles_for_10_km": round(cpk * 10), "cycles_for_100_km": round(cpk * 100)},
           "verdict": verdict,
           "why": "%d of %d parts with a walk solve pass the design endurance or the %g km threshold, %d FAIL, %d CANNOT DETERMINE; %s" % (
               n["PASS"], len(rows), LIFE_KM_REQUIRED, n["FAIL"], n["CANNOT DETERMINE"],
               ("the shortest design life is %s at %.4g km (P_s >= 90 %%)" % (worst["part"], worst["life_km_design_Ps90_worst"])) if worst else "no finite life"),
           "limits": ["isotropic linear FEA peak at a nodal point: mesh-sensitive at re-entrant corners (measured on the ankle only, +2.21 % finest vs first mesh); each other part's sensitivity is unmeasured",
                      "the S-N curve is for printed-FLAT 100 %-infill coupons; no part.py declares print orientation or infill (across-layer strength 17 +- 3 MPa per the Prusament TDS is the weaker axis)",
                      "the design curve has no notch factor; a screw hole edge or a fillet root is a notch and the FEA peak sits at one on most parts",
                      "gait measured in MuJoCo at 0.25 m/s on flat ground; the peak and the cycle count both change with gait and terrain",
                      "one stress level per part (the walk peak) — no rainflow over the cycle, so the count assumes every cycle reaches the peak (conservative)"],
           "what_settles_it": "tensile-fatigue coupons of THE filament on THE printer in each part's orientation (R = 0, 10 Hz, 4 levels x 2, run-out 2e6 as the paper did), and a walked-km log of a printed leg",
           "artifacts": [os.path.relpath(p, ROOT) for p in sorted(glob.glob(os.path.join(EVID, "fea_microduck-*_walk.json")))] + ["out/sim-evidence/loads_mujoco.json"],
           "looked_at": []}
    path = os.path.join(EVID, "fatigue_walk.json")
    json.dump(out, open(path, "w"), indent=1)
    for r in rows:
        print("%-40s %-17s sigma %8s MPa  life %s km" % (r["part"], r["verdict"], ("%.4f" % r["sigma_max_mpa"]) if r.get("sigma_max_mpa") else "—",
                                                      ("%.4g" % r["life_km_design_Ps90_worst"]) if r.get("life_km_design_Ps90_worst") is not None else "inf/—"))
    print(verdict, out["why"]); print("wrote", path)


if __name__ == "__main__":
    main()
