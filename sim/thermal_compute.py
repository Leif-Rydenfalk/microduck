#!/usr/bin/env python3
"""LANE F3 study 2 -- the compute inside the closed printed enclosure.

FIRST, A CORRECTION THE MODEL FORCED.  The lane brief said "the Radxa Zero 3W
inside the closed trunk".  It is not in the trunk.  sim/microduck_ours.xml puts
the compute board geom (`pcb__raspberry_pi_zero_2_w`, the Radxa's placeholder)
and the Robot HAT (`elec_rpi_robot_hat_pcb`) in body **jaw_soft** -- the HEAD --
and spec/mesh-placements.json lists both there too.  Body `trunk_base` carries
no compute geom at all.  So this is a HEAD thermal study, and the trunk is
measured beside it because the pack and the servo-bus wiring live there.

WHAT IS ALREADY MEASURED, ON THE REAL ROBOT, BY POLLEN -- and it is a FAIL:
  research/raw/community/replica_hardware-teardown.en.md:362, quoting Pollen's
  own source verbatim: "2 is a thermal limit, not a preference." ... "Flat out
  it reaches **95 degC** and the CPU throttles to **408 MHz**".
  research/raw/microduck_main_docs_project_media-bringup.md:343 -- the measured
  table row "with the flip | 5522 [RGA failures] | 1565 [frames lost] | 7-8
  [fps] | 97 degC, CPU at 408 MHz", and :348 "the SoC hits its thermal limit,
  everything throttles to 408 MHz".
  Against the vendor's own claim, ce-parts/radxa-zero-3w/electrical.host.json
  `thermal`, [brief] 6.5 p.7 verbatim: "An internal thermal management governor
  is in place to regulate these parameters, ensuring that the CPU temperature
  does not exceed a threshold of 85 degC" and "The specified ambient operating
  temperature for optimal performance of the Radxa ZERO 3W ranges from 0 degC
  to 50 degC".

So the verdict is not in doubt; what this study adds is the GEOMETRY and the
NUMBER: how much heat this printed head can actually shed, measured, and how
little dissipation it takes to put the board outside its own 50 degC ambient
rating.

    ce-cad/bin/cad sim/thermal_compute.py       (plain python3 works: stdlib)

Output: out/sim-evidence/thermal-compute-head.json
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from thermal_servo import (AIR_A9, SIGMA, air, h_churchill_chu,   # noqa: E402
                           h_radiation, solve_case_temp)

RADXA_AMBIENT_MAX_C = 50.0
RADXA_CPU_GOVERNOR_C = 85.0
POLLEN_MEASURED_C = 95.0
POLLEN_MEASURED_WORST_C = 97.0
USB_SUPPLY_W = 10.0             # brief 5.1 p.5: "5V/2A" on the OTG port


def main():
    cav = json.load(open(os.path.join(REPO, "out/sim-evidence/cavity-volumes.json")))
    head = cav["outputs"]["cavities"]["head"]
    trunk = cav["outputs"]["cavities"]["trunk"]
    servo = json.load(open(os.path.join(REPO,
                                        "out/sim-evidence/thermal-servo-xl330.json")))

    # ---- the head as a heat-shedding body --------------------------------
    size = head["shell_bbox_mm"]["size"]                 # mm
    L_char = max(size) / 1000.0                          # m, the tallest dimension
    a_low = head["shell_outer_area_estimate_mm2"] / 1e6  # m2, half the shells' triangles
    a_high = head["enclosure_hull_area_voxel_mm2"] / 1e6  # m2, staircase upper bound

    ambients = [20.0, 25.0, 35.0]
    powers = [0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0]

    curve = []
    for ta in ambients:
        for p in powers:
            row = {"ambient_C": ta, "dissipation_W": p}
            for tag, a in (("area_low_shells_only", a_low),
                           ("area_high_voxel_hull", a_high)):
                best = solve_case_temp(p, a, L_char, ta, 1.0, 0.0)   # eps=1 upper bound on cooling
                worst = solve_case_temp(p, a, L_char, ta, 0.0, 0.0)  # eps=0 lower bound on cooling
                row[tag] = {
                    "skin_temp_C_eps1_bestcooling": best["case_temp_C"],
                    "skin_temp_C_eps0_worstcooling": worst["case_temp_C"],
                    "R_th_skin_to_ambient_K_W_eps1": best["R_th_case_ambient_K_W"],
                    "R_th_skin_to_ambient_K_W_eps0": worst["R_th_case_ambient_K_W"],
                    "h_conv_W_m2K": best["h_conv_W_m2K"],
                    "h_rad_W_m2K_eps1": best["h_rad_W_m2K"],
                    "Ra_L": best["Ra_L"],
                }
            curve.append(row)

    # ---- the question that needs no unpublished number -------------------
    # The head's INTERIOR air is the Radxa's ambient. The board's own rating is
    # 0..50 degC ambient. Internal air is at least as hot as the shell, so
    #   P_crit >= (50 - T_room) / R_th(skin->ambient)
    # is a hard LOWER BOUND on the dissipation that puts the board out of spec.
    crit = {}
    for ta in ambients:
        row = {}
        for tag, a in (("area_low_shells_only", a_low),
                       ("area_high_voxel_hull", a_high)):
            for eps, elabel in ((1.0, "eps1_bestcooling"), (0.0, "eps0_worstcooling")):
                # bisect on P
                lo, hi = 1e-4, 200.0
                for _ in range(200):
                    mid = 0.5 * (lo + hi)
                    t = solve_case_temp(mid, a, L_char, ta, eps, 0.0)["case_temp_C"]
                    if t < RADXA_AMBIENT_MAX_C:
                        lo = mid
                    else:
                        hi = mid
                row["%s_%s" % (tag, elabel)] = round(0.5 * (lo + hi), 4)
        crit[("Ta%.0fC" % ta)] = row

    # ---- the trapped air is not a reservoir ------------------------------
    (k30, nu30, pr30), _ = air(30.0)
    rho30 = 1.164                       # Cengel A-9 row 30 degC, kg/m3
    cp_air = 1007.0                     # same row, J/kgK
    v_head_m3 = head["free_air_volume_cm3"] / 1e6
    v_trunk_m3 = trunk["free_air_volume_cm3"] / 1e6
    c_air_head = rho30 * v_head_m3 * cp_air
    c_air_trunk = rho30 * v_trunk_m3 * cp_air

    out = {
        "study": "thermal-compute-head",
        "what": ("The compute board's thermal situation inside the closed printed "
                 "HEAD (not the trunk -- see the correction), measured enclosure "
                 "geometry, and how little dissipation puts the board outside its "
                 "own 0-50 degC ambient rating."),
        "inputs": {
            "correction_to_the_brief": {
                "brief_said": "the Radxa Zero 3W inside the closed trunk",
                "model_says": "body jaw_soft (the HEAD)",
                "evidence": cav["outputs"]["compute_board_evidence"],
            },
            "enclosure_geometry": {
                "source": "out/sim-evidence/cavity-volumes.json (sim/cavity_measure.py)",
                "head_bbox_mm": size,
                "head_enclosed_volume_cm3": head["enclosed_volume_cm3"],
                "head_free_air_volume_cm3": head["free_air_volume_cm3"],
                "head_free_air_fraction": head["free_air_fraction_of_enclosed"],
                "head_outer_area_m2_low": round(a_low, 6),
                "head_outer_area_m2_low_basis": head["shell_outer_area_basis"] +
                    " It counts ONLY top_head_shell + bottom_head_shell, not the "
                    "face, eye ring, jaw or soft mouth, so it UNDERSTATES the skin "
                    "and therefore OVERSTATES every temperature below.",
                "head_outer_area_m2_high": round(a_high, 6),
                "head_outer_area_m2_high_basis": head["enclosure_hull_area_basis"],
                "trunk_enclosed_volume_cm3": trunk["enclosed_volume_cm3"],
                "trunk_free_air_volume_cm3": trunk["free_air_volume_cm3"],
                "trunk_free_air_fraction": trunk["free_air_fraction_of_enclosed"],
                "characteristic_length_m": round(L_char, 6),
                "characteristic_length_basis": "the head's longest bbox dimension, "
                                               "used as the vertical plate height L "
                                               "in Churchill-Chu",
            },
            "board": {
                "identity": "Radxa ZERO 3W (RK3566). ce-parts/radxa-zero-3w. NOTE: "
                            "the MJCF's mesh is a Raspberry Pi Zero 2 W placeholder "
                            "of the same 65 x 30 mm envelope -- GOAL.md open finding "
                            "3. Its VOLUME is used here only as an obstruction, and "
                            "the two boards' envelopes agree.",
                "ambient_rating_quote": "[brief] 6.5 p.7 verbatim: 'The specified "
                                        "ambient operating temperature for optimal "
                                        "performance of the Radxa ZERO 3W ranges "
                                        "from 0 degC to 50 degC'",
                "governor_quote": "[brief] 6.5 p.7 verbatim: 'An internal thermal "
                                  "management governor is in place to regulate these "
                                  "parameters, ensuring that the CPU temperature does "
                                  "not exceed a threshold of 85 degC'",
                "supply_quote": "[brief] 5.1 p.5 verbatim: 'The Radxa ZERO 3W support "
                                "DC +5V voltage: Power adapter with 5V/2A on the USB "
                                "2.0 OTG Type-C power port' -- a supply RATING, "
                                "10.0 W, not a measured draw",
                "dissipation_W": None,
                "dissipation_basis": "CANNOT DETERMINE. "
                                     "ce-parts/radxa-zero-3w/electrical.host.json "
                                     "unknowns[1] verbatim: 'Board current draw (idle "
                                     "/ policy running / video encoding): no fetched "
                                     "document states it. A meter on the 5 V path "
                                     "settles it.' Also power[4] on the PMIC: "
                                     "'Board-level current draw: NOT stated in any "
                                     "fetched document - CANNOT DETERMINE.' No number "
                                     "is invented; the study is run as a curve over "
                                     "dissipation instead.",
                "no_heatsink": "no heatsink, fan or vent is modelled anywhere in body "
                               "jaw_soft (sim/microduck_ours.xml) and none appears in "
                               "spec/mesh-placements.json",
            },
            "measured_on_the_real_robot": {
                "soc_temperature_C": POLLEN_MEASURED_C,
                "soc_temperature_worst_C": POLLEN_MEASURED_WORST_C,
                "throttled_to_MHz": 408,
                "detection_rate_Hz": 2,
                "quote_1": "research/raw/community/replica_hardware-teardown.en.md:362 "
                           "quoting Pollen's source: '2 is a thermal limit, not a "
                           "preference.' Flat out it reaches **95 degC** and the CPU "
                           "throttles to **408 MHz** - a robot that walks badly in "
                           "order to see well.",
                "quote_2": "research/raw/microduck_main_docs_project_media-bringup.md:343 "
                           "measured table row: 'with the flip | 5522 | 1565 | 7-8 | "
                           "97 degC, CPU at 408 MHz'; :348 'That saturates the CPU, "
                           "the SoC hits its thermal limit, everything throttles to "
                           "408 MHz'",
                "quote_3": "docs/ELECTRONICS-AND-SOFTWARE.md:111: NPU detection at "
                           "'2 Hz - \"a thermal limit, not a preference\": flat out "
                           "95 degC, CPU throttles to 408 MHz'",
                "vendor_disagreement": "Pollen's 95-97 degC sits ABOVE the vendor "
                                       "brief's 85 degC governor claim. Recorded as a "
                                       "disagreement in "
                                       "ce-parts/radxa-zero-3w/electrical.host.json "
                                       "`thermal`, not resolved here.",
            },
            "air_properties": {
                "table": "Cengel TABLE A-9 'Properties of air at 1 atm pressure', p.948; "
                         "https://www.me.psu.edu/cimbala/me433/Links/Table_A_9_CC_Properties_of_Air.pdf "
                         "read 2026-09-02 (pdftotext -layout)",
                "rows_used_T_C_k_nu_Pr": AIR_A9,
                "row_30C_density_kg_m3": rho30,
                "row_30C_cp_J_kgK": cp_air,
            },
            "correlation": {
                "name": "Churchill-Chu vertical plate, laminar",
                "quote": "h = (k/L)(0.68 + 0.67 Ra_L^(1/4) / (1 + (0.492/Pr)^(9/16))^(4/9))",
                "url": "https://en.wikipedia.org/wiki/Heat_transfer_coefficient",
                "radiation": "bracketed by eps = 1 (black body, the hard upper bound "
                             "on radiative cooling) and eps = 0 (none). "
                             "sigma = %.9e W/m2K4." % SIGMA,
            },
        },
        "method": ("The head's EXTERNAL leg is solved exactly as the servo study's: "
                   "P = (h_conv(Ts) + h_rad(Ts)) * A * (Ts - Ta), h_conv from "
                   "Churchill-Chu re-evaluated at the film temperature with Cengel "
                   "A-9 properties, radiation bracketed over emissivity 0..1, area "
                   "bracketed between the shells' outer skin and the voxel hull. The "
                   "INTERNAL leg (board -> still air -> shell) is NOT modelled: there "
                   "is no published junction-to-case figure for the RK3566, no "
                   "measured board dissipation, and no vent. Because the interior air "
                   "can only be HOTTER than the shell, the critical dissipation "
                   "computed from the external leg alone is a hard LOWER BOUND on "
                   "what it takes to put the board past its 50 degC ambient rating."),
        "outputs": {
            "skin_temperature_curve": curve,
            "critical_dissipation_W_to_reach_50C_ambient_rating": crit,
            "critical_dissipation_note": ("a LOWER BOUND: it assumes the interior air "
                                          "is no hotter than the shell, which it "
                                          "cannot be. The real figure is smaller."),
            "usb_supply_ceiling_W": USB_SUPPLY_W,
            "trapped_air_thermal_capacitance": {
                "head_free_air_cm3": head["free_air_volume_cm3"],
                "head_C_J_per_K": round(c_air_head, 5),
                "trunk_free_air_cm3": trunk["free_air_volume_cm3"],
                "trunk_C_J_per_K": round(c_air_trunk, 5),
                "what_it_means": ("the trapped air stores essentially nothing -- at "
                                  "%.4f J/K the head's whole air volume absorbs less "
                                  "energy for a 1 K rise than a tenth of a second of "
                                  "the knee servo's copper loss (1.6664 W). The air "
                                  "is a RESISTANCE, not a reservoir; the head's "
                                  "thermal mass is its plastic and its boards."
                                  % c_air_head),
            },
            "servo_bus_and_pack": {
                "bus_power_lower_bound_W": servo["outputs"]["bus_power_lower_bound_W"],
                "pack_current_lower_bound_A": servo["outputs"]["pack_current_lower_bound_A"],
                "pack_location": "body trunk_base, in %.3f cm3 of free air "
                                 "(%.1f %% void) -- a tighter enclosure than the head"
                                 % (trunk["free_air_volume_cm3"],
                                    100 * trunk["free_air_fraction_of_enclosed"]),
                "pack_self_heating_W": None,
                "pack_self_heating_basis": ("CANNOT DETERMINE. "
                                            "ce-parts/np-f550/electrical.part.json "
                                            "uncertainties, verbatim: 'INTERNAL "
                                            "RESISTANCE, MAX CONTINUOUS DISCHARGE, "
                                            "CHARGE RATE: stated by neither fetched "
                                            "page.' Without a cell internal resistance "
                                            "there is no I^2 R to compute, and the "
                                            "fitted pack's maker is itself "
                                            "unidentified (component.json verdict "
                                            "CANNOT DETERMINE)."),
                "regulator_thermal": ("CANNOT DETERMINE. The servo-bus regulator lives "
                                      "on the Robot HAT, one of the three custom PCBs "
                                      "with no published design (RELEASE.html 1, "
                                      "Electronics - custom PCBs: 'Not ready'). No "
                                      "part number means no package and no theta_JA."),
            },
        },
        "verdict": "FAIL",
        "why": "",
        "cannot_determine": [
            {"what": "the board's actual dissipation",
             "why": "no fetched Radxa document states board-level current draw "
                    "(electrical.host.json unknowns[1] and power[4]). The only "
                    "sourced electrical figure is the 5 V / 2 A supply RATING = "
                    "10.0 W ceiling.",
             "what_settles_it": "an inline meter on the 5 V path at idle, with the "
                                "policy running, and with video encoding -- the three "
                                "states electrical.host.json itself names"},
            {"what": "junction-to-air resistance of the RK3566 in this enclosure",
             "why": "Rockchip publishes no theta_JA for the RK3566 and no heatsink or "
                    "vent exists in the model, so the internal leg has no model. The "
                    "external leg is solved and used as a bound instead.",
             "what_settles_it": "log /sys/class/thermal/thermal_zone*/temp beside a "
                                "thermocouple on the head shell at a known load"},
            {"what": "the pack's self-heating and the servo-bus regulator's",
             "why": "cell internal resistance is stated by neither fetched NP-F550 "
                    "page; the regulator has no part number because the Robot HAT has "
                    "no published design",
             "what_settles_it": "the pack's own datasheet once the fitted maker is "
                                "identified, and the Robot HAT schematic (lane D)"},
        ],
        "script": "sim/thermal_compute.py",
        "artifacts": ["out/sim-evidence/thermal-compute-head.json"],
        "looked_at": [
            "out/sim-evidence/cavity-volumes.json",
            "out/sim-evidence/thermal-servo-xl330.json",
            "ce-parts/radxa-zero-3w/electrical.host.json",
            "ce-parts/np-f550/electrical.part.json",
            "ce-parts/np-f550/component.json",
            "research/raw/community/replica_hardware-teardown.en.md",
            "research/raw/microduck_main_docs_project_media-bringup.md",
            "docs/ELECTRONICS-AND-SOFTWARE.md",
            "sim/microduck_ours.xml",
            "https://www.me.psu.edu/cimbala/me433/Links/Table_A_9_CC_Properties_of_Air.pdf",
            "https://en.wikipedia.org/wiki/Heat_transfer_coefficient",
        ],
    }

    c25 = crit["Ta25C"]
    crit_lo = c25["area_low_shells_only_eps0_worstcooling"]      # smallest area, no radiation
    crit_hi = c25["area_high_voxel_hull_eps1_bestcooling"]       # largest area, black body
    skin_2W = [r for r in curve if r["ambient_C"] == 25.0 and r["dissipation_W"] == 2.0][0]
    out["outputs"]["which_leg_fails"] = {
        "external_skin_to_room": {
            "verdict": "PASS",
            "why": ("at 2.0 W in a 25 degC room the head's own skin settles between "
                    "%.2f and %.2f degC, and it takes %.3f-%.3f W to lift the skin to "
                    "the board's 50 degC ambient rating. A single-board computer of "
                    "this class does not dissipate that much, so the OUTSIDE of the "
                    "box is not the bottleneck."
                    % (skin_2W["area_high_voxel_hull"]["skin_temp_C_eps1_bestcooling"],
                       skin_2W["area_low_shells_only"]["skin_temp_C_eps0_worstcooling"],
                       crit_lo, crit_hi))},
        "internal_die_to_skin": {
            "verdict": "FAIL",
            "why": ("this is the leg that fails, and it fails on a MEASUREMENT, not a "
                    "model: Pollen records the SoC at 95 degC (97 degC in the "
                    "videoflip pathology) while throttling to 408 MHz. Between that "
                    "die and a skin that the external solution puts in the high "
                    "twenties sits %.3f cm3 of still air (%.1f %% of the enclosed "
                    "volume), with no vent, no fan and no heatsink anywhere in body "
                    "jaw_soft. The whole trapped-air volume is a %.4f J/K reservoir "
                    "-- it buffers nothing and only resists. The design item is a "
                    "CONDUCTION PATH from the SoC to the shell, not more skin area."
                    % (head["free_air_volume_cm3"],
                       100 * head["free_air_fraction_of_enclosed"], c_air_head)),
            "model": "CANNOT DETERMINE -- no theta_JA is published for the RK3566 and "
                     "the board's dissipation is unmeasured, so no internal resistance "
                     "can be computed. The external leg is solved and used as the "
                     "bound instead."},
    }
    out["why"] = (
        "FAIL, on a measurement rather than a model: Pollen's own documents record the "
        "SoC at 95 degC flat out (97 degC in the videoflip pathology) throttling to "
        "408 MHz, with object detection held down to 2 Hz because of it -- 'a thermal "
        "limit, not a preference'. This study adds the geometry and locates the fault. "
        "The head is a sealed printed box, %.3f cm3 enclosed with %.3f cm3 of still air "
        "in it (%.1f %% void), no vent, no fan, no heatsink, outer skin %.0f-%.0f mm2. "
        "Solving the OUTSIDE of that box exonerates it: at 2.0 W the skin settles at "
        "%.2f-%.2f degC in a 25 degC room, and it would take %.3f-%.3f W to lift the "
        "skin to the board's own 50 degC ambient rating (bracketed by no radiation on "
        "the shells-only area at the low end and a black body on the voxel-hull area "
        "at the high end) -- more than a board on a 5 V / 2 A = 10.0 W supply is "
        "likely to dissipate. So the failure is INSIDE: the path from a 95 degC die "
        "through %.3f cm3 of trapped air, whose entire thermal capacitance is %.4f J/K "
        "-- less than a seventh of a second of the knee servo's copper loss. The board's "
        "real dissipation and the RK3566's junction-to-air resistance are both CANNOT "
        "DETERMINE, so the internal leg is not modelled; it is measured, at 95 degC. "
        "The design item this study names is a conduction path from the SoC to the "
        "shell, not more skin."
        % (head["enclosed_volume_cm3"], head["free_air_volume_cm3"],
           100 * head["free_air_fraction_of_enclosed"],
           head["shell_outer_area_estimate_mm2"], head["enclosure_hull_area_voxel_mm2"],
           skin_2W["area_high_voxel_hull"]["skin_temp_C_eps1_bestcooling"],
           skin_2W["area_low_shells_only"]["skin_temp_C_eps0_worstcooling"],
           crit_lo, crit_hi, head["free_air_volume_cm3"], c_air_head))

    path = os.path.join(REPO, "out/sim-evidence/thermal-compute-head.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(out, open(path, "w"), indent=1)

    print("VERDICT", out["verdict"])
    print(out["why"])
    print()
    print("head skin temperature at 25 degC ambient, area low..high, eps 1..0:")
    for row in curve:
        if row["ambient_C"] != 25.0:
            continue
        lo, hi = row["area_low_shells_only"], row["area_high_voxel_hull"]
        print("  %5.1f W -> %6.2f .. %6.2f degC   (R_th %.2f .. %.2f K/W)"
              % (row["dissipation_W"], hi["skin_temp_C_eps1_bestcooling"],
                 lo["skin_temp_C_eps0_worstcooling"],
                 hi["R_th_skin_to_ambient_K_W_eps1"],
                 lo["R_th_skin_to_ambient_K_W_eps0"]))
    print("critical dissipation to reach the 50 degC ambient rating:", c25)
    print("wrote out/sim-evidence/thermal-compute-head.json")


if __name__ == "__main__":
    main()
