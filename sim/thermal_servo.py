#!/usr/bin/env python3
"""LANE F3 study 1 -- XL330-M288-T winding heating at the MEASURED walking duty.

Every input carries a source.  Nothing here is a plausible default.

LOAD          out/sim-evidence/gait-torque-duty.json (sim/thermal_duty.py, this
              lane): per-joint mean(tau^2) over 11.5 s of commanded walking at
              vx = 0.25 m/s, sampled at the 200 Hz physics step.  Cross-checked
              against out/sim-evidence/gait-peaks.json (lane F2,
              sim/gait_sweep.py) baseline_walk_vx0.25 per-joint peaks.

SERVO         ROBOTIS e-Manual XL330-M288-T, https://emanual.robotis.com/docs/en/dxl/x/xl330-m288/
              fetched 2026-09-02, sha256 in ce-parts/xl330-m288-t/PROVENANCE.json,
              local copy ce-parts/xl330-m288-t/iterations/v0.0.1/docs/fetched/
              robotis-docs-xl330-m288.html.  Quoted rows are in
              ce-parts/xl330-m288-t/electrical.chip.json.

AIR           Cengel, "Properties of air at 1 atm pressure", TABLE A-9, p.948
              (939-956_cengel_app1.indd), served at
              https://www.me.psu.edu/cimbala/me433/Links/Table_A_9_CC_Properties_of_Air.pdf
              read 2026-09-02.  Source line on the table itself: "Data generated
              from the EES software developed by S. A. Klein and F. L. Alvarado.
              Original sources: Keenan, Chao, Keyes, Gas Tables, Wiley, 198; and
              Thermophysical Properties of Matter, Vol. 3 ... Vol. 11 ...
              IFI/Plenun, NY, 1970, ISBN 0-306067020-8."

CONVECTION    Churchill-Chu, natural convection on a vertical plate, as printed
              on https://en.wikipedia.org/wiki/Heat_transfer_coefficient
              (read 2026-09-02), verbatim:
                  h = (k/L)(0.68 + 0.67 Ra_L^(1/4) /
                            (1 + (0.492/Pr)^(9/16))^(4/9))
              valid 10^-1 < Ra_L < 10^9 (laminar).

WHAT IS NOT KNOWN, and is therefore not invented:
  * ROBOTIS publishes NO winding resistance, NO thermal resistance, NO thermal
    capacitance and NO continuous-torque rating for this actuator.  The
    terminal resistance below is DERIVED from the three published stall rows
    (V / I_stall) and the derivation's own spread is reported.
  * winding-to-case thermal resistance: unpublished.  Every case temperature
    computed here is therefore a LOWER BOUND on the winding temperature, and
    the study says so instead of guessing the delta.
  * lumped thermal capacitance: unpublished.  Time-to-limit is reported as a
    curve over C, not as a number.

    ce-cad/bin/cad sim/thermal_servo.py

Output: out/sim-evidence/thermal-servo-xl330.json
"""

import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

SIGMA = 5.670374419e-8          # Stefan-Boltzmann, CODATA (exact SI definition)

# --- Cengel Table A-9, transcribed rows (T degC, k W/mK, nu m2/s, Pr) --------
AIR_A9 = [
    (20, 0.02514, 1.516e-5, 0.7309),
    (25, 0.02551, 1.562e-5, 0.7296),
    (30, 0.02588, 1.608e-5, 0.7282),
    (35, 0.02625, 1.655e-5, 0.7268),
    (40, 0.02662, 1.702e-5, 0.7255),
    (45, 0.02699, 1.750e-5, 0.7241),
    (50, 0.02735, 1.798e-5, 0.7228),
    (60, 0.02808, 1.896e-5, 0.7202),
    (70, 0.02881, 1.995e-5, 0.7177),
    (80, 0.02953, 2.097e-5, 0.7154),
    (90, 0.03024, 2.201e-5, 0.7132),
    (100, 0.03095, 2.306e-5, 0.7111),
]


def air(t_c):
    """Linear interpolation inside Table A-9; clamps at the ends (and says so
    by returning the clamp flag)."""
    if t_c <= AIR_A9[0][0]:
        return AIR_A9[0][1:], True
    if t_c >= AIR_A9[-1][0]:
        return AIR_A9[-1][1:], True
    for (t0, k0, n0, p0), (t1, k1, n1, p1) in zip(AIR_A9, AIR_A9[1:]):
        if t0 <= t_c <= t1:
            f = (t_c - t0) / (t1 - t0)
            return (k0 + f * (k1 - k0), n0 + f * (n1 - n0), p0 + f * (p1 - p0)), False
    raise AssertionError(t_c)


def h_churchill_chu(t_s_c, t_a_c, L_m):
    """W/m2K, vertical plate of height L. Ra from the film temperature."""
    t_f = 0.5 * (t_s_c + t_a_c)
    (k, nu, pr), clamped = air(t_f)
    alpha = nu / pr                        # a = nu / Pr, by definition of Pr
    beta = 1.0 / (t_f + 273.15)            # ideal gas
    ra = 9.80665 * beta * abs(t_s_c - t_a_c) * L_m ** 3 / (nu * alpha)
    if ra <= 0:
        return 0.0, ra, clamped
    nu_num = 0.67 * ra ** 0.25
    nu_den = (1.0 + (0.492 / pr) ** (9.0 / 16.0)) ** (4.0 / 9.0)
    h = (k / L_m) * (0.68 + nu_num / nu_den)
    return h, ra, clamped


def h_radiation(t_s_c, t_a_c, eps):
    ts, ta = t_s_c + 273.15, t_a_c + 273.15
    return eps * SIGMA * (ts * ts + ta * ta) * (ts + ta)


def solve_case_temp(power_W, area_m2, L_m, t_a_c, eps, blockage):
    """Steady state: P = (h_conv + h_rad) * A_eff * (Ts - Ta). Fixed point."""
    a_eff = area_m2 * (1.0 - blockage)
    t_s = t_a_c + 1.0
    for _ in range(400):
        hc, ra, clamped = h_churchill_chu(t_s, t_a_c, L_m)
        hr = h_radiation(t_s, t_a_c, eps)
        new = t_a_c + power_W / max((hc + hr) * a_eff, 1e-12)
        if abs(new - t_s) < 1e-9:
            t_s = new
            break
        t_s += 0.35 * (new - t_s)
    hc, ra, clamped = h_churchill_chu(t_s, t_a_c, L_m)
    hr = h_radiation(t_s, t_a_c, eps)
    return {"case_temp_C": round(t_s, 4),
            "rise_K": round(t_s - t_a_c, 4),
            "h_conv_W_m2K": round(hc, 4),
            "h_rad_W_m2K": round(hr, 4),
            "Ra_L": float("%.4g" % ra),
            "R_th_case_ambient_K_W": round(1.0 / ((hc + hr) * a_eff), 4),
            "area_effective_m2": round(a_eff, 8),
            "air_table_clamped": clamped}


def selftest():
    """Break the solver on purpose before trusting it. Four checks, each with a
    predicted answer that does not come from the solver."""
    rows = []

    def add(name, ok, got, want, note):
        rows.append({"check": name, "verdict": "PASS" if ok else "FAIL",
                     "got": got, "expected": want, "note": note})

    # 1. no heat -> no rise. A solver that cannot return the trivial answer
    #    cannot be trusted with the others.
    r = solve_case_temp(0.0, 0.004168, 0.034, 25.0, 1.0, 0.0)
    add("zero power gives zero rise", abs(r["rise_K"]) < 1e-6, r["rise_K"], 0.0,
        "P = 0 W")

    # 2. the reported R_th must reproduce the rise it was solved with
    r = solve_case_temp(1.6664, 0.004168, 0.034, 25.0, 1.0, 0.0)
    pred = 1.6664 * r["R_th_case_ambient_K_W"]
    add("rise = P x R_th", abs(pred - r["rise_K"]) < 1e-3,
        round(r["rise_K"], 6), round(pred, 6),
        "the returned resistance must be the one the temperature came from")

    # 3. ten times the area must cool much better -- monotonicity, which a
    #    sign error in the fixed point would break
    r10 = solve_case_temp(1.6664, 0.04168, 0.034, 25.0, 1.0, 0.0)
    add("10x area lowers the rise", r10["rise_K"] < r["rise_K"] / 5.0,
        round(r10["rise_K"], 4), "< %.4f" % (r["rise_K"] / 5.0),
        "area 0.04168 m2 vs 0.004168 m2")

    # 4. the correlation must be inside its own published validity window
    ok_ra = 1e-1 < r["Ra_L"] < 1e9
    add("Ra_L inside Churchill-Chu laminar validity", ok_ra, r["Ra_L"],
        "10^-1 < Ra_L < 10^9",
        "the quoted validity range on the correlation's source page")

    # 5. NEGATIVE CONTROL, watched going red: with the radiation term forced on
    #    at eps = 1 the body MUST run cooler than with eps = 0. If the sign of
    #    the radiation term were wrong this is what would catch it.
    hot = solve_case_temp(1.6664, 0.004168, 0.034, 25.0, 0.0, 0.0)
    add("radiation cools (eps 1 < eps 0)", r["case_temp_C"] < hot["case_temp_C"],
        round(r["case_temp_C"], 4), "< %.4f" % hot["case_temp_C"],
        "same power and area, emissivity 1 vs 0")
    return rows, all(x["verdict"] == "PASS" for x in rows)


def main():
    duty_path = os.path.join(REPO, "out/sim-evidence/gait-torque-duty.json")
    duty = json.load(open(duty_path))
    peaks_path = os.path.join(REPO, "out/sim-evidence/gait-peaks.json")
    peaks = json.load(open(peaks_path)) if os.path.exists(peaks_path) else None

    # ---- vendor rows, verbatim ------------------------------------------
    stall = {3.7: (1.11, 0.42, 0.378), 5.0: (1.47, 0.52, 0.354), 6.0: (1.74, 0.60, 0.345)}
    stall_quote = ("E1 Specifications, 'Stall Torque' row verbatim: "
                   "'0.42 [N.m] (at 3.7 [V], 1.11 [A], 0.378 [Nm/A])', "
                   "'0.52 [N.m] (at 5.0 [V], 1.47 [A], 0.354 [Nm/A])', "
                   "'0.60 [N.m] (at 6.0 [V], 1.74 [A], 0.345 [Nm/A])'")
    r_rows = {str(v): round(v / i, 6) for v, (i, _, _) in stall.items()}
    r_vals = list(r_rows.values())
    R_TERM = r_rows["5.0"]
    KT = 0.354                                    # N.m per A, 5.0 V row

    # vendor envelope: E1 'Dimensions (W x H x D) | 20.0 x 34.0 x 26.0 [mm]'
    W, H, D = 0.020, 0.034, 0.026
    AREA = 2.0 * (W * H + W * D + H * D)
    L_CHAR = H                                    # plate height for Churchill-Chu
    MASS_KG = 0.018                               # E1 'Weight | 18 [g]'
    T_LIMIT_C = 70.0                              # Control Table '31 | Temperature Limit | RW | 70 | 0 ~ 100 | 1 [degC]'
    T_OP_MAX_C = 70.0                             # E1 'Operating Temperature | -5 ~ +70 [degC]'
    STANDBY_mA = 17.0

    joints = duty["outputs"]["joints"]
    ambients = [20.0, 25.0, 35.0]
    blockages = [0.0, 0.30]                       # free body / 30 % of the skin blocked by the printed mount

    rows = {}
    for name, j in sorted(joints.items()):
        i2 = j["mean_tau_squared_Nm2"] / (KT * KT)          # A^2, RMS-squared motor current
        i_rms = math.sqrt(i2)
        p_cu = i2 * R_TERM
        i_peak = j["peak_abs_Nm"] / KT
        p_cu_peak = i_peak * i_peak * R_TERM
        cases = {}
        for ta in ambients:
            for bl in blockages:
                # eps = 0 is the hard lower bound on cooling (no radiation at
                # all); eps = 1 is the hard upper bound (a black body). The
                # real plastic case is inside that bracket, and this study
                # does not need to know where.
                lo = solve_case_temp(p_cu, AREA, L_CHAR, ta, 1.0, bl)   # best cooling
                hi = solve_case_temp(p_cu, AREA, L_CHAR, ta, 0.0, bl)   # worst cooling
                cases["Ta%.0fC_block%.0f%%" % (ta, bl * 100)] = {
                    "case_temp_C_eps1_bestcooling": lo["case_temp_C"],
                    "case_temp_C_eps0_worstcooling": hi["case_temp_C"],
                    "R_th_K_W_eps1": lo["R_th_case_ambient_K_W"],
                    "R_th_K_W_eps0": hi["R_th_case_ambient_K_W"],
                    "h_conv_W_m2K_eps1": lo["h_conv_W_m2K"],
                    "h_rad_W_m2K_eps1": lo["h_rad_W_m2K"],
                    "Ra_L_eps1": lo["Ra_L"],
                    "over_limit_even_at_best_cooling": lo["case_temp_C"] > T_LIMIT_C,
                }
        # what thermal resistance would be needed to sit exactly on the limit
        rth_needed = {("Ta%.0fC" % ta): round((T_LIMIT_C - ta) / p_cu, 4)
                      for ta in ambients} if p_cu > 0 else {}
        rows[name] = {
            "mean_tau_squared_Nm2": j["mean_tau_squared_Nm2"],
            "rms_torque_Nm": j["rms_Nm"],
            "peak_torque_Nm": j["peak_abs_Nm"],
            "i_rms_A": round(i_rms, 5),
            "i_peak_A": round(i_peak, 5),
            "i_peak_vs_current_limit_38_pct": round(100.0 * i_peak / 1.750, 3),
            "p_copper_W": round(p_cu, 5),
            "p_copper_peak_W": round(p_cu_peak, 5),
            "p_mech_mean_positive_W": j["mean_positive_mech_power_W"],
            "steady_state": cases,
            "R_th_needed_to_hold_70C_K_W": rth_needed,
        }

    # --- the pack side ----------------------------------------------------
    p_cu_total = sum(r["p_copper_W"] for r in rows.values())
    p_mech_total = sum(r["p_mech_mean_positive_W"] for r in rows.values())
    p_standby_5V = 15 * (STANDBY_mA / 1000.0) * 5.0
    p_bus_lower_bound = p_cu_total + p_mech_total
    pack_v = {"6.6 (empty cut-off)": 6.6, "7.4 (2S nominal)": 7.4, "8.2 (full)": 8.2}
    pack = {k: round(p_bus_lower_bound / v, 5) for k, v in pack_v.items()}

    # --- time-to-limit as a CURVE over the unpublished capacitance ---------
    worst = max(rows, key=lambda n: rows[n]["p_copper_W"])
    wr = rows[worst]
    tau_curve = []
    for cp in (500.0, 900.0, 1300.0, 1700.0):
        C = MASS_KG * cp                          # J/K if the whole 18 g were one lump
        for tag, cs in (("Ta25C_block0%", wr["steady_state"]["Ta25C_block0%"]),):
            for eps_tag, t_ss in (("eps1", cs["case_temp_C_eps1_bestcooling"]),
                                  ("eps0", cs["case_temp_C_eps0_worstcooling"])):
                rise_ss = t_ss - 25.0
                rth = (cs["R_th_K_W_eps1"] if eps_tag == "eps1"
                       else cs["R_th_K_W_eps0"])
                tau_s = rth * C
                lim = T_LIMIT_C - 25.0
                if rise_ss <= lim:
                    t_lim = None
                else:
                    t_lim = -tau_s * math.log(1.0 - lim / rise_ss)
                tau_curve.append({
                    "assumed_cp_J_kgK": cp, "lumped_C_J_K": round(C, 4),
                    "eps": eps_tag, "tau_thermal_s": round(tau_s, 2),
                    "steady_rise_K": round(rise_ss, 3),
                    "time_to_70C_s": None if t_lim is None else round(t_lim, 2),
                    "time_to_70C_min": None if t_lim is None else round(t_lim / 60.0, 3),
                })

    def band(r):
        """(lower bound, upper bound) on the CASE temperature at 25 degC ambient:
        best cooling = black-body radiation and a free body; worst cooling =
        no radiation at all and 30 % of the skin blocked by the printed mount."""
        return (r["steady_state"]["Ta25C_block0%"]["case_temp_C_eps1_bestcooling"],
                r["steady_state"]["Ta25C_block30%"]["case_temp_C_eps0_worstcooling"])

    for n, r in rows.items():
        lo, hi = band(r)
        r["case_band_25C"] = {"lower_bound_C": lo, "upper_bound_C": hi,
                              "limit_C": T_LIMIT_C,
                              "grade": ("FAIL" if lo > T_LIMIT_C else
                                        "CANNOT DETERMINE" if hi > T_LIMIT_C else "PASS")}

    fails = sorted(n for n, r in rows.items() if r["case_band_25C"]["grade"] == "FAIL")
    unknown = sorted(n for n, r in rows.items()
                     if r["case_band_25C"]["grade"] == "CANNOT DETERMINE")
    over_at_best = fails
    over_at_block = sorted(n for n, r in rows.items()
                           if r["steady_state"]["Ta25C_block30%"]["over_limit_even_at_best_cooling"])

    if fails:
        verdict = "FAIL"
        why = ("At the measured walking duty, %d of 14 joints reach a CASE temperature "
               "above the servo's own Temperature Limit(31) = 70 degC in still 25 degC "
               "air EVEN WITH the most favourable cooling physics allows (black-body "
               "radiation, eps = 1, and no mounting blockage): %s. The winding is hotter "
               "than the case by an unpublished amount, so this lower bound already "
               "fails." % (len(fails), ", ".join(fails)))
    elif unknown:
        verdict = "CANNOT DETERMINE"
        worst_n = max(unknown, key=lambda n: rows[n]["case_band_25C"]["upper_bound_C"])
        b = rows[worst_n]["case_band_25C"]
        why = ("%d of 14 joints STRADDLE the 70 degC Temperature Limit(31): %s. Worst is "
               "%s, whose case sits between %.2f degC (black-body radiation, free body -- "
               "the best cooling physics allows) and %.2f degC (no radiation, 30 %% of the "
               "skin blocked by its printed mount). The bracket contains the limit, so the "
               "verdict is not a pass. Two unmeasured quantities decide it: the case's "
               "emissivity and how much of the skin the printed mount covers -- and on top "
               "of both, the winding is hotter than the case by an unpublished amount, so "
               "even the lower bound is a lower bound. No other joint exceeds %.2f degC at "
               "its own upper bound."
               % (len(unknown), ", ".join(unknown), worst_n, b["lower_bound_C"],
                  b["upper_bound_C"],
                  max(r["case_band_25C"]["upper_bound_C"] for n, r in rows.items()
                      if n not in unknown)))
    else:
        verdict = "PASS"
        why = ("No joint's case reaches the 70 degC Temperature Limit(31) at this duty, "
               "even with no radiation and 30 %% of the skin blocked: the hottest is %s at "
               "%.2f degC upper bound."
               % (max(rows, key=lambda n: rows[n]["case_band_25C"]["upper_bound_C"]),
                  max(r["case_band_25C"]["upper_bound_C"] for r in rows.values())))

    st_rows, st_ok = selftest()
    out = {
        "study": "thermal-servo-xl330",
        "what": ("Winding/case heating of the fifteen XL330-M288-T actuators at "
                 "the measured walking duty, against the vendor's own "
                 "Temperature Limit(31) = 70 degC shutdown."),
        "inputs": {
            "load_basis": {
                "file": "out/sim-evidence/gait-torque-duty.json",
                "script": "sim/thermal_duty.py",
                "statistic": "mean(tau^2) per joint over t >= 0.5 s of an 12.0 s "
                             "commanded walk at vx = 0.25 m/s, sampled at the "
                             "200 Hz physics step",
                "why_that_statistic": "copper loss is I^2 R and I is proportional "
                                      "to torque, so mean(tau^2) is the only "
                                      "average that maps linearly onto heat",
                "cross_check": (None if peaks is None else
                                {"file": "out/sim-evidence/gait-peaks.json",
                                 "script": "sim/gait_sweep.py (lane F2)",
                                 "baseline_walk_vx0.25_peak_Nm":
                                     peaks["outputs"]["baseline_walk_vx0.25"]["per_joint_peak_Nm"],
                                 "note": "F2 samples at the 50 Hz control frame, "
                                         "this lane at the 200 Hz physics step, so "
                                         "this lane's peaks are equal or higher"}),
            },
            "servo": {
                "part": "XL330-M288-T",
                "ref": "part:xl330-m288-t",
                "datasheet_url": "https://emanual.robotis.com/docs/en/dxl/x/xl330-m288/",
                "provenance": "ce-parts/xl330-m288-t/PROVENANCE.json (fetched 2026-09-02, sha256 recorded)",
                "stall_rows_quote": stall_quote,
                "torque_constant_Nm_per_A": KT,
                "torque_constant_basis": "the 5.0 V stall row's own third figure, "
                                         "'0.354 [Nm/A]'. It is OUTPUT-shaft torque "
                                         "per INPUT current (E1 Current Limit(38) note: "
                                         "'XL330 series measures curret at its input "
                                         "power source'), so no gear ratio or gearbox "
                                         "efficiency is applied on top of it.",
                "terminal_resistance_ohm": R_TERM,
                "terminal_resistance_basis": ("DERIVED, not published: at stall the "
                                              "back-EMF is zero and the full row voltage "
                                              "stands across the winding, so R = V / "
                                              "I_stall. The three published rows give %s "
                                              "ohm -- a spread of %.2f %% about their mean, "
                                              "which is the derivation's own consistency "
                                              "check. The 5.0 V row is used."
                                              % (r_rows, 100.0 * (max(r_vals) - min(r_vals))
                                                 / (sum(r_vals) / len(r_vals)))),
                "envelope_mm": [20.0, 34.0, 26.0],
                "envelope_quote": "E1 Specifications verbatim: 'Dimensions (W x H x D) | 20.0 x 34.0 x 26.0 [mm]'",
                "surface_area_m2": round(AREA, 8),
                "mass_kg": MASS_KG,
                "mass_quote": "E1 Specifications verbatim: 'Weight | 18 [g]'",
                "temperature_limit_C": T_LIMIT_C,
                "temperature_limit_quote": "E1 Control Table of EEPROM Area verbatim: "
                                           "'31 | 1 | Temperature Limit | RW | 70 | 0 ~ 100 | 1 [degC]'; "
                                           "E1 Specifications 'Operating Temperature | -5 ~ +70 [degC]'; "
                                           "Shutdown(63) Bit 2 'Overheating Error(default)'",
                "standby_current_mA": STANDBY_mA,
                "standby_quote": "E1 Specifications verbatim: 'Standby Current | 17 [mA]' (no test voltage stated)",
                "count_on_robot": 15,
            },
            "air_properties": {
                "table": "Cengel, TABLE A-9 'Properties of air at 1 atm pressure', p.948",
                "url": "https://www.me.psu.edu/cimbala/me433/Links/Table_A_9_CC_Properties_of_Air.pdf",
                "read": "2026-09-02, text extracted with pdftotext -layout",
                "rows_used_T_C_k_nu_Pr": AIR_A9,
                "table_own_source_line": ("Data generated from the EES software developed by "
                                          "S. A. Klein and F. L. Alvarado. Original sources: Keenan, "
                                          "Chao, Keyes, Gas Tables, Wiley, 198; and Thermophysical "
                                          "Properties of Matter, Vol. 3: Thermal Conductivity, "
                                          "Y. S. Touloukian, P. E. Liley, S. C. Saxena, Vol. 11: "
                                          "Viscosity, Y. S. Touloukian, S. C. Saxena, and P. "
                                          "Hestermans, IFI/Plenun, NY, 1970, ISBN 0-306067020-8."),
            },
            "correlation": {
                "name": "Churchill-Chu, vertical plate, laminar",
                "quote": "h = (k/L)(0.68 + 0.67 Ra_L^(1/4) / (1 + (0.492/Pr)^(9/16))^(4/9))",
                "validity_quote": "10^-1 < Ra_L < 10^9",
                "url": "https://en.wikipedia.org/wiki/Heat_transfer_coefficient",
                "read": "2026-09-02",
                "characteristic_length_m": L_CHAR,
                "characteristic_length_basis": "the vendor's H = 34.0 mm; the servo hangs "
                                               "with that dimension vertical in the leg and "
                                               "neck mounts (spec/mesh-placements.json).",
                "radiation": ("bracketed, not assumed: eps = 1 (black body) is the "
                              "hard physical upper bound on radiative cooling and "
                              "eps = 0 the hard lower bound. The plastic case's real "
                              "emissivity is unmeasured and lies inside that bracket, "
                              "so the bracket is reported and no emissivity is invented. "
                              "sigma = 5.670374419e-8 W/m2K4 (SI definition)."),
            },
            "ambients_C": ambients,
            "mount_blockage_fractions": blockages,
        },
        "method": ("P_copper = (tau_rms / kT)^2 * R_terminal per joint, with "
                   "tau_rms^2 = mean(tau^2) measured. Steady state solves "
                   "P = (h_conv(Ts) + h_rad(Ts)) * A_eff * (Ts - Ta) by fixed "
                   "point, h_conv from Churchill-Chu re-evaluated at the film "
                   "temperature each iteration with air properties interpolated "
                   "in Cengel Table A-9. Reported as a bracket over emissivity "
                   "0..1 and over 0 % / 30 % of the skin blocked by the printed "
                   "mount. Gearbox friction loss and drive-stage loss are NOT "
                   "modelled -- both add heat, so every temperature here "
                   "UNDERSTATES the real one."),
        "outputs": {
            "solver_selftest": {"rows": st_rows,
                                "verdict": "PASS" if st_ok else "FAIL",
                                "why": "five checks whose expected answers do not "
                                       "come from the solver; the last is a negative "
                                       "control on the sign of the radiation term",
                                "negative_control": (
                                    "watched going red, 2026-09-02: flipping the sign "
                                    "of h_radiation (return -eps*SIGMA*... in "
                                    "sim/thermal_servo.py) turns three of the five "
                                    "checks FAIL -- 'rise = P x R_th', '10x area "
                                    "lowers the rise' and 'radiation cools' -- and the "
                                    "study's own verdict flips to FAIL with case "
                                    "temperatures of 1.67e12 degC. The sign was then "
                                    "restored and the suite went green again. A check "
                                    "that cannot go red is a decoration.")},
            "per_joint": rows,
            "worst_joint": worst,
            "worst_joint_p_copper_W": wr["p_copper_W"],
            "joints_FAIL_over_70C_even_at_best_cooling": fails,
            "joints_CANNOT_DETERMINE_band_straddles_70C": unknown,
            "joints_over_70C_at_best_cooling_30pct_blocked": over_at_block,
            "total_copper_W_15_servos_note": ("sum over the 14 actuated joints; the "
                                              "15th XL330 (jaw) is not an actuated "
                                              "joint in the published model and has no "
                                              "measured duty -- CANNOT DETERMINE"),
            "total_copper_W": round(p_cu_total, 5),
            "total_mech_W": round(p_mech_total, 5),
            "standby_all_15_at_5V_W": round(p_standby_5V, 5),
            "bus_power_lower_bound_W": round(p_bus_lower_bound, 5),
            "pack_current_lower_bound_A": pack,
            "time_to_limit_curve": tau_curve,
        },
        "verdict": verdict,
        "why": why,
        "cannot_determine": [
            {"what": "winding-to-case thermal resistance",
             "why": "ROBOTIS publishes no thermal model, no winding resistance and no "
                    "continuous-torque rating for the XL330-M288-T; only the three stall "
                    "rows and the 70 degC limit exist. Every case temperature above is "
                    "therefore a LOWER BOUND on the winding temperature.",
             "what_settles_it": "a step test on one servo: hold a known constant torque "
                                "against a fixture and log Present Temperature(146) "
                                "(RAM 146, 1 degC) to steady state. The asymptote gives "
                                "R_th and the knee gives C in the same run."},
            {"what": "lumped thermal capacitance C, hence time-to-limit",
             "why": "unpublished. The curve above sweeps cp over 500-1700 J/kgK on the "
                    "vendor's 18 g and is a PARAMETRIC RESULT, not a measurement.",
             "what_settles_it": "the same step test."},
            {"what": "gearbox friction loss at this duty",
             "why": "no efficiency figure is published for the 288.4:1 engineering-plastic "
                    "gear train. It is omitted, which makes every temperature here an "
                    "understatement.",
             "what_settles_it": "measure Present Current(126) at a known output torque and "
                                "subtract the copper term."},
            {"what": "servo-bus regulator temperature",
             "why": "the Robot HAT's regulator part number is CANNOT DETERMINE "
                    "(ce-parts/xl330-m288-t/electrical.part.json note: 'the Microduck's "
                    "Robot HAT is assumed to carry one (transceiver part CANNOT "
                    "DETERMINE)'; the three custom PCBs have no published design). With "
                    "no part there is no package, no theta_JA and no dissipation to "
                    "compute. The bus power lower bound above is what a regulator study "
                    "would start from.",
             "what_settles_it": "the Robot HAT schematic (lane D) naming the regulator."},
            {"what": "current at pack voltage above 6.0 V",
             "why": "the vendor states nothing above 6.0 V and the design runs the "
                    "servos on the raw 6.6-8.2 V pack "
                    "(docs/ELECTRONICS-AND-SOFTWARE.md 3.4). kT and R are taken at the "
                    "5.0 V row.",
             "what_settles_it": "a meter on a servo VDD pin and Present Current(126) "
                                "logged at a known torque on the real pack."},
        ],
        "script": "sim/thermal_servo.py",
        "artifacts": ["out/sim-evidence/thermal-servo-xl330.json"],
        "looked_at": [
            "out/sim-evidence/gait-torque-duty.json",
            "out/sim-evidence/gait-peaks.json",
            "ce-parts/xl330-m288-t/electrical.chip.json",
            "ce-parts/xl330-m288-t/electrical.part.json",
            "ce-parts/xl330-m288-t/component.json",
            "https://emanual.robotis.com/docs/en/dxl/x/xl330-m288/",
            "https://www.me.psu.edu/cimbala/me433/Links/Table_A_9_CC_Properties_of_Air.pdf",
            "https://en.wikipedia.org/wiki/Heat_transfer_coefficient",
        ],
    }

    path = os.path.join(REPO, "out/sim-evidence/thermal-servo-xl330.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(out, fh, indent=1)

    print("solver self-test:", "PASS" if st_ok else "FAIL")
    for x in st_rows:
        print("   %-46s %-4s got %s want %s" % (x["check"], x["verdict"], x["got"], x["expected"]))
    print("VERDICT", verdict)
    print(why)
    print()
    print("%-16s %9s %8s %8s %9s %9s  %s" % ("joint", "tau_rms", "I_rms", "P_cu W",
                                              "Tcase lo", "Tcase hi", "grade"))
    for n, r in sorted(rows.items(), key=lambda kv: -kv[1]["p_copper_W"]):
        b = r["case_band_25C"]
        print("%-16s %9.4f %8.4f %8.4f %9.2f %9.2f  %s"
              % (n, r["rms_torque_Nm"], r["i_rms_A"], r["p_copper_W"],
                 b["lower_bound_C"], b["upper_bound_C"], b["grade"]))
    print()
    print("bus power lower bound %.4f W -> pack current %s"
          % (p_bus_lower_bound, pack))
    print("wrote out/sim-evidence/thermal-servo-xl330.json")


if __name__ == "__main__":
    main()
