#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""fatigue_ankle.py — fatigue life of the PLA ankle bracket under the walking
load, from the measured gait and a CITED S-N curve.

Lane F1, 2026-09-02. Inputs, each with its source:
  * cycles per km   — sim/measure_loads.py: left-foot touchdowns of the
                       BEST_alpha_walking policy at vx 0.25 m/s (period, stride)
  * peak stress     — sim/stress_all.py: fea_microduck-ankle-left_walk.json
                       (CalculiX, the walk-peak transmitted force through the
                       real load path), plus the converged-mesh figure when the
                       convergence study has run
  * S-N curve       — Ezeh & Susmel, Int J Fatigue 126 (2019) 319-326,
                       doi 10.1016/j.ijfatigue.2019.05.014 (accepted manuscript,
                       CC BY-NC-ND, research/fatigue/ezeh-susmel-2019-ijfatigue-
                       126-319-pla-fatigue.pdf): FFF PLA, 100 % infill, printed
                       flat, R = -1 / -0.5 / 0 / 0.3 at 10 Hz. Unifying DESIGN
                       curve (P_s >= 90 %), in terms of the MAXIMUM stress in the
                       cycle: k = 5.5, sigma_MAX = 0.1 sigma_UTS at 2e6 cycles.
                       Table 1 (theta_p = 0 deg, UTS 42.6 MPa): median endurance
                       amplitudes at 2e6, R = -1: 10.4 MPa, R = 0: 6.1 MPa.
  * UTS             — the paper's own 42.6 MPa (theta_p 0 deg, New Verbatim
                       PLA), and the Prusament PLA TDS 51 +- 3 MPa printed
                       horizontal (research/tds/prusament-pla-tds-2021-10-en.pdf)
The gait cycle on the ankle is pulsating (stance loads it, swing unloads it):
R = sigma_min / sigma_max ~ 0 — the paper's R = 0 rows apply directly.

Basquin form of the design curve: N = N_ref (sigma_A / sigma_max)^k with
N_ref = 2e6, sigma_A = 0.1 UTS, k = 5.5. Life in km = N / cycles_per_km.
Writes out/sim-evidence/fatigue_ankle.json.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EVID = os.path.join(ROOT, "out", "sim-evidence")


def main():
    L = json.load(open(os.path.join(EVID, "loads_mujoco.json")))
    g = L["walk"]["gait"]
    fea = json.load(open(os.path.join(EVID, "fea_microduck-ankle-left_walk.json")))
    conv_path = os.path.join(EVID, "fea_convergence_microduck-ankle-left_drop.json")
    conv = json.load(open(conv_path)) if os.path.exists(conv_path) else None

    sigma_walk = fea["outputs"]["max_von_mises_mpa"]          # peak nodal von Mises at the walk-peak force
    force_walk = fea["inputs"]["force_magnitude_N"]
    # mesh sensitivity of the peak: the convergence study is on the drop case (same load path, linear) —
    # scale its finest/first ratio onto the walk peak
    scale_note, sigma_conv = "convergence study not available", None
    if conv and conv["outputs"]["rows"]:
        rows = [r for r in conv["outputs"]["rows"] if r.get("max_von_mises_mpa")]
        if len(rows) >= 2:
            ratio = rows[-1]["max_von_mises_mpa"] / rows[0]["max_von_mises_mpa"]
            sigma_conv = sigma_walk * ratio
            scale_note = ("peak scaled by the finest/first-mesh ratio %.4f of the drop-case convergence study (linear elasticity: the ratio is "
                          "independent of the load level for the same load path)" % ratio)

    curves = []
    for label, uts, src in (("paper_theta0", 42.6, "Ezeh & Susmel 2019 Table 1, theta_p 0 deg"),
                            ("prusament_tds", 51.0, "Prusament PLA TDS, printed horizontal, 51 +- 3 MPa yield (used as UTS: PLA's yield and UTS coincide within the TDS tolerance — brittle)")):
        for sname, sig in (("fea_peak", sigma_walk),) + ((("fea_peak_mesh_scaled", sigma_conv),) if sigma_conv else ()):
            sA = 0.1 * uts
            k = 5.5
            N = 2e6 * (sA / sig) ** k if sig > 0 else float("inf")
            km = N / g["cycles_per_km"]
            endurance_ratio = sA / sig
            curves.append({"uts_basis": label, "uts_mpa": uts, "uts_source": src, "stress_basis": sname, "sigma_max_mpa": round(sig, 4),
                           "design_endurance_sigma_max_2e6_mpa": round(sA, 4), "k": k,
                           "cycles_to_failure_design_Ps90": ("> 2e6 (below the design endurance limit)" if N > 2e6 else round(N, 1)),
                           "cycles_numeric": N, "life_km_design_Ps90": ("infinite by the design curve" if N > 2e6 else round(km, 3)),
                           "endurance_margin": round(endurance_ratio, 4),
                           "median_R0_amplitude_2e6_mpa_theta0": 6.1, "median_R0_sigma_max_2e6_mpa_theta0": 12.2,
                           "note": "median (P_s 50 %%) R = 0 endurance in terms of sigma_max = 2 x 6.1 = 12.2 MPa (Table 1); the design curve (0.1 UTS = %.2f MPa) is the P_s >= 90 %% floor" % sA})
    worst = min(curves, key=lambda c: c["endurance_margin"])
    best = max(curves, key=lambda c: c["endurance_margin"])
    infinite = worst["cycles_numeric"] > 2e6
    # a walk of 1 km is 22461 cycles; state the design life for 10 km and 100 km
    verdict = "PASS" if infinite else ("FAIL" if worst["cycles_numeric"] < g["cycles_per_km"] * 10 else "PASS")
    why = ("peak walk-cycle von Mises %.3f MPa on the ankle (walk-peak force %.4f N) is %.1f %% of the P_s>=90 %% design endurance limit "
           "%.2f MPa (0.1 x UTS %.1f MPa, Ezeh & Susmel 2019) even on the least favourable basis — infinite life by the design curve at %.0f cycles/km "
           "(period %.3f s, stride %.4f m)" % (worst["sigma_max_mpa"], force_walk, 100.0 / worst["endurance_margin"] if worst["endurance_margin"] else 0,
                                              worst["design_endurance_sigma_max_2e6_mpa"], worst["uts_mpa"], g["cycles_per_km"], g["period_s_mean"], g["stride_m_per_cycle"])
           if infinite else
           "peak walk-cycle von Mises %.3f MPa EXCEEDS the design endurance %.2f MPa: design life %s cycles = %s km at %.0f cycles/km" % (
               worst["sigma_max_mpa"], worst["design_endurance_sigma_max_2e6_mpa"], worst["cycles_to_failure_design_Ps90"], worst["life_km_design_Ps90"], g["cycles_per_km"]))
    out = {
        "study": "fatigue_ankle", "part": "part:microduck-ankle-left", "generated": "2026-09-02", "script": "sim/fatigue_ankle.py",
        "inputs": {
            "gait": {"period_s_mean": g["period_s_mean"], "period_s_min": g["period_s_min"], "period_s_max": g["period_s_max"], "n_cycles_measured": g["n_cycles"],
                     "stride_m_per_cycle": g["stride_m_per_cycle"], "cycles_per_km": g["cycles_per_km"], "left_stance_fraction": g["left_stance_fraction"],
                     "source": "out/sim-evidence/loads_mujoco.json walk.gait (sim/measure_loads.py: left-foot touchdowns, BEST_alpha_walking vx 0.25 m/s, 8 s)"},
            "stress": {"sigma_max_walk_mpa": sigma_walk, "force_N": force_walk, "source": "out/sim-evidence/fea_microduck-ankle-left_walk.json outputs.max_von_mises_mpa",
                       "mesh": fea["outputs"].get("mesh"), "sigma_max_mesh_scaled_mpa": round(sigma_conv, 4) if sigma_conv else None, "mesh_scaling": scale_note,
                       "load_ratio_R": "~0 (pulsating: stance loads, swing unloads; the paper's R = 0 rows apply)"},
            "sn_curve": {"paper": "O.H. Ezeh, L. Susmel, 'Fatigue strength of additively manufactured polylactide (PLA): effect of raster angle and non-zero mean stresses', "
                                  "International Journal of Fatigue 126 (2019) 319-326, doi:10.1016/j.ijfatigue.2019.05.014",
                         "file": "research/fatigue/ezeh-susmel-2019-ijfatigue-126-319-pla-fatigue.pdf",
                         "sha256": "6539146573d830076e5f3b1ec0feca62fa64d08a255a1487da4e211404d7ae13",
                         "design_curve": "P_s >= 90 %: k = 5.5, sigma_MAX = 0.1 sigma_UTS at N_ref = 2e6 cycles (eqs 5-6, valid for 100 % infill printed flat)",
                         "table1_theta0": {"uts_mpa": 42.6, "R-1": {"k": 7.7, "sigma_A50_mpa": 10.4, "T": 1.185}, "R-0.5": {"k": 8.9, "sigma_A50_mpa": 10.1, "T": 1.266},
                                           "R0": {"k": 7.4, "sigma_A50_mpa": 6.1, "T": 1.592}, "R0.3": {"k": 7.0, "sigma_A50_mpa": 5.1, "T": 1.216}},
                         "specimens": "Ultimaker 2 Extended+, New Verbatim PLA 2.85 mm, 240/60 C, 30 mm/s, 100 % infill, 0.1 mm layers, 0.4 mm shell; 6 mm x 3/5 mm dog-bones, 10 Hz, run-out 2e6",
                         "scatter": "T_sigma ~ 2.9 in terms of sigma_max across all angles and load ratios (Fig 9)"},
        },
        "method": "Basquin: N = 2e6 (0.1 UTS / sigma_max)^5.5; life_km = N / cycles_per_km; sigma_max = peak nodal von Mises of the walk-peak FEA (worst point, R ~ 0)",
        "outputs": {"curves": curves, "worst_basis": worst["uts_basis"] + "/" + worst["stress_basis"], "best_basis": best["uts_basis"] + "/" + best["stress_basis"],
                    "cycles_for_10_km": round(g["cycles_per_km"] * 10), "cycles_for_100_km": round(g["cycles_per_km"] * 100),
                    "stress_headroom_to_design_endurance": round(1 / worst["endurance_margin"], 4) if worst["endurance_margin"] else None},
        "limits": ["isotropic linear FEA peak at a nodal point (mesh-sensitive at re-entrant corners — see the convergence study)",
                   "the S-N curve is for printed-FLAT 100 %-infill coupons; this bracket's print orientation and infill are not declared in its part.py (across-layer strength 17 +- 3 MPa per the Prusament TDS is the weaker axis)",
                   "the design curve has no notch factor; a screw hole edge is a notch (PMC12787623: smooth ~49,000 vs central-hole ~24,000 cycles at 12 MPa amplitude)",
                   "gait measured in MuJoCo at the browser simulator's VEL_FWD 0.25 m/s; a different gait or terrain changes both the peak and the cycle count"],
        "what_settles_it": "a tensile-fatigue coupon set of THE filament on THE printer in the bracket's orientation (R = 0, 10 Hz, 4 stress levels x 2, run-out 2e6 per JSME as the paper did), and a walked-km log of one printed ankle",
        "verdict": verdict, "why": why,
        "artifacts": ["out/sim-evidence/fea_microduck-ankle-left_walk.json", "out/sim-evidence/loads_mujoco.json"] + (["out/sim-evidence/fea_convergence_microduck-ankle-left_drop.json"] if conv else []),
        "looked_at": [],
    }
    path = os.path.join(EVID, "fatigue_ankle.json")
    json.dump(out, open(path, "w"), indent=1)
    print(verdict, why)
    print("wrote", path)


if __name__ == "__main__":
    main()
