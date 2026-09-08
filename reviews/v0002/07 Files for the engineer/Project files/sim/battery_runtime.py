#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""battery_runtime.py — integrate per-servo ELECTRICAL power over a measured
MuJoCo gait and turn it into hours on the Microduck's pack.

THE MODEL, and where every constant comes from
----------------------------------------------
ROBOTIS publishes, for the XL330-M288-T, three stall rows and three no-load
speeds and nothing else electrical (verbatim, e-Manual Specifications table,
fetched 2026-09-02, local copy in ce-parts/xl330-m288-t/iterations/v0.0.1/
docs/fetched/robotis-emanual-xl330-m288.html):

    Stall Torque   0.42 [N.m] (at 3.7 [V], 1.11 [A], 0.378 [Nm/A])
                   0.52 [N.m] (at 5.0 [V], 1.47 [A], 0.354 [Nm/A])
                   0.60 [N.m] (at 6.0 [V], 1.74 [A], 0.345 [Nm/A])
    No Load Speed  76 / 103 / 123 [rev/min] (at 3.7 / 5.0 / 6.0 [V])
    Standby Current 17 [mA]

Each row fixes a complete linear DC-machine model referred to the OUTPUT shaft
(the 288.4:1 gearbox is inside the constants, which is what makes them usable
directly against a joint torque in N.m):

    kT = stall_torque / stall_current            [N.m per input amp]
    R  = V / stall_current                       [ohm, winding + drive]
    kE = V / no_load_speed_rad_s                 [V.s per rad]

    per frame, per joint:  I  = |tau| / kT
                           Vm = kE*|omega| + R*I
                           P_motor = min(Vm, V_pack) * I        [W]
                           P_servo = P_motor + V_pack * 0.017   [W]

    The min() is the pack rail: the drive cannot put more than the pack voltage
    across the winding, so a frame whose ideal Vm exceeds V_pack is a frame the
    real servo could not have produced at all. Clamping is the CONSERVATIVE
    reading (it under-counts power rather than inventing a rail that is not
    there) and the count of clamped frames is published per mode as
    frames_needing_more_than_pack_voltage — it is 0 in every mode of the
    committed run, so the clamp changes no number in this file; it is a guard,
    not a correction. (This line said "P_motor = Vm * I" until 2026-09-02; the
    code always had the min(), and the JSON `method` string always carried it.)

kE comes out at 0.4649 / 0.4636 / 0.4659 V.s/rad from the three independent
rows (spread 0.50 %), which is the check that the model is the right shape.
The 5.0 V row (ROBOTIS's own "Recommended") is primary; the 3.7 V and 6.0 V
rows are carried as the sensitivity band.

WHAT THIS MODEL DOES NOT KNOW, stated rather than defaulted:
  * ROBOTIS publishes NO no-load current. I = tau/kT is therefore exact at
    stall and ZERO at zero torque, so the motor term is a LOWER BOUND: the
    real servo also burns the current that spins its own gearbox. Only the
    17 mA controller standby is published and it is included.
  * The gearbox friction the MJCF models (joint frictionloss 0.0048 N.m,
    damping 0.053 N.m.s/rad) is already inside data.actuator_force, so that
    part of the loss IS counted.
  * The PWM stage is taken as loss-free: pack current = P_motor / V_pack.
    Any converter loss makes the real draw higher and the runtime shorter.
  * The compute + sensor + HAT draw is CANNOT DETERMINE (see below) and is
    swept, never assumed.

Run: /Applications/FreeCAD.app/Contents/Resources/bin/python sim/battery_runtime.py
"""
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
from common import CTRL_DT, JOINT_NAMES  # noqa: E402

ROOT = common.ROOT
SWEEP = os.path.join(ROOT, "out", "sim-sweep")
EVID = os.path.join(ROOT, "out", "sim-evidence")

SERVO_ROWS = {   # V : (stall_torque_Nm, stall_current_A, no_load_speed_rpm)
    "3.7": (0.42, 1.11, 76.0),
    "5.0": (0.52, 1.47, 103.0),
    "6.0": (0.60, 1.74, 123.0),
}
SERVO_CITE = ("ROBOTIS e-Manual XL330-M288-T, Specifications table, verbatim: "
              "'Stall Torque | 0.42 [N.m] (at 3.7 [V], 1.11 [A], 0.378 [Nm/A]) / 0.52 [N.m] (at 5.0 [V], "
              "1.47 [A], 0.354 [Nm/A]) / 0.60 [N.m] (at 6.0 [V], 1.74 [A], 0.345 [Nm/A])' ; "
              "'No Load Speed | 76 [rev/min] (at 3.7 [V]) / 103 [rev/min] (at 5.0 [V]) / 123 [rev/min] "
              "(at 6.0 [V])' ; 'Standby Current | 17 [mA]' ; 'Gear Ratio | 288.4 : 1'. "
              "https://emanual.robotis.com/docs/en/dxl/x/xl330-m288/ , fetched 2026-09-02, sha256 in "
              "ce-parts/xl330-m288-t/PROVENANCE.json, local copy ce-parts/xl330-m288-t/iterations/v0.0.1/"
              "docs/fetched/robotis-emanual-xl330-m288.html. Quoted in ce-parts/xl330-m288-t/"
              "electrical.chip.json current_mA.stall_basis and controller.no_load_speed.")
STANDBY_A = 0.017
# ASSUMPTION, FLAGGED — not a published figure. ROBOTIS prints "Standby Current | 17 [mA]"
# with NO voltage attached (verified verbatim in the local copy of the e-Manual page). This
# model bills that current against the PACK rail, because the servo is fed the raw pack
# (6.6-8.2 V, docs/ELECTRONICS-AND-SOFTWARE.md 3.4) and a constant-current standby load
# therefore draws 17 mA x V_pack from the pack. If instead the 17 mA is a figure measured on
# the 5.0 V "Recommended" row and the standby load is constant-POWER, the pack term is
# 17 mA x 5.0 V and the whole standby number is 32.4 % smaller. ROBOTIS states neither, so
# both are published side by side and the pack-rail figure is used because it is the
# conservative one for runtime.
STANDBY_V_BASIS = "pack rail"
STANDBY_ALT_V = 5.0
STANDBY_ASSUMPTION = (
    "ROBOTIS publishes 'Standby Current | 17 [mA]' with NO voltage attached "
    "(ce-parts/xl330-m288-t/iterations/v0.0.1/docs/fetched/robotis-emanual-xl330-m288.html, "
    "Specifications table). This model bills it at the PACK voltage, i.e. 15 x 0.017 A x V_pack, "
    "because the servos are fed the raw pack and a constant-current standby load draws that from "
    "the pack. If the 17 mA is instead a constant-POWER figure measured on the 5.0 V row, the "
    "pack term is 15 x 0.017 A x 5.0 V and the standby number is 32.4 % smaller. The pack-rail "
    "reading is used because it is conservative for runtime; both are reported. WHAT SETTLES IT: "
    "an ammeter on a powered XL330-M288-T with Torque Enable(64)=0, read at 5.0 V and at 7.4 V — "
    "or a ROBOTIS statement of the test condition. This assumption is the WHOLE of the "
    "'idle, torque off' mode and 1.887 W of every other mode.")
N_SERVOS_TOTAL = 15
N_SERVOS_SIMULATED = 14   # the MJCF has no mouth joint; ID 34 is standby-only here

PACK = {
    "part": "part:np-f550 (ce-parts/np-f550)",
    "Wh": 18.7,
    "Wh_quote": "Weight 99 g  Dimensions 70 x 38 x 20 mm  Watt Hours 18.7  Volts 7.2  Capacity 2600",
    "Wh_cite": "ce-parts/np-f550/electrical.part.json capacity.cite — Duracell 'Charge' SKU DR5 product page "
               "'Replacement Sony NP-F330/NP-F550 Battery 7.2V 2600mAh', "
               "https://www.duracellcharge.info/en/product/replacement-sony-np-f330-np-f550-battery/ , fetched "
               "2026-09-02, sha256 239e06510b5ca2725702a86467d7c327fe4436bcd40693ab03f364e8c2afe49d, local copy "
               "ce-parts/np-f550/docs/duracell-dr5-np-f550-2600mah.html. 7.2 V x 2.600 Ah = 18.72 Wh; the page's "
               "18.7 Wh is that product rounded.",
    "Wh_computed": round(7.2 * 2.600, 4),
    "mAh": 2600,
    "v_nominal": 7.2,
    "v_window": [6.6, 8.2],
    "v_window_cite": "ce-parts/np-f550/electrical.part.json provides[0].v_range_cite — Pollen's runtime maps "
                     "6.6 V (empty) to 8.2 V (full) under load, read through the servos' Present Input "
                     "Voltage(144) (duck-control model.rs:99-128; docs/ELECTRONICS-AND-SOFTWARE.md 9). "
                     "robotd shuts down on a ~10 s EMA at 6.6 V (robotd.toml [safety] "
                     "battery_empty_shutdown = true).",
    "v_used": 7.4,
    "v_used_why": "the midpoint of the runtime's own 6.6-8.2 V window. WHICH IS ABOVE THE SERVO'S RATED INPUT "
                  "(3.7-6.0 V, 'Recommended : 5.0 [V]'): the Microduck feeds the XL330s the raw pack "
                  "(docs/ELECTRONICS-AND-SOFTWARE.md 3.4, and robotd clears Shutdown bit 0 'Input Voltage "
                  "Error'). Applying the 5.0 V motor constants at 7.4 V is an EXTRAPOLATION and is flagged "
                  "as one; the 3.7 V and 6.0 V rows bracket how much the constants move.",
    "identity": "CANNOT DETERMINE which pack is fitted — 'NP-F550' is Sony's shape and Sony's own cell is "
                "1500 mAh / 10.8 Wh, so a 2600 mAh 'NP-F550' is necessarily third-party and no Pollen source "
                "names the maker (ce-parts/np-f550/component.json why). Duracell's DR5 is the representative "
                "2600 mAh part on the shelf, NOT a proven fit.",
    "usable_fraction_assumed": 1.0,
    "usable_fraction_note": "the whole 18.7 Wh is credited. The robot actually stops at a 6.6 V EMA, and how "
                            "much of a 2S pack's energy is still above 6.6 V under this load is CANNOT "
                            "DETERMINE (no discharge curve for the fitted cell). Every hour below is therefore "
                            "an UPPER bound on that account.",
}

COMPUTE = {
    "verdict": "CANNOT DETERMINE",
    "why": "No vendor document states the Radxa ZERO 3W's consumption. Radxa's own hardware page states only a "
           "supply REQUIREMENT — 'Requires 5V/2A power adapter' (https://docs.radxa.com/en/zero/zero3 , fetched "
           "2026-09-02) — which is a 10.0 W ceiling for the board and whatever hangs off it, not a draw. The "
           "product brief PDF (https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_product_brief.pdf, fetched "
           "2026-09-02) states no consumption figure either. Pollen publishes none, and neither does "
           "out/handover/elec-verify-wf_969f3a4c.json, whose Radxa row records the same 'DC +5 V ... 5V/2A' "
           "requirement and no current. Search-engine answer boxes quoting '0.35-0.45 A idle' were seen and are "
           "NOT recorded: an answer box is not a source. The HAT (codec, dormant BMI088, transceiver), the ToF, "
           "the IMX219 camera and the imu_to_dxl board add to it and have no published system-level figure "
           "either. WHAT SETTLES IT: a meter in the pack lead of a running unit, or Present Current(126) summed "
           "off the bus with the board draw taken by difference.",
    "swept_W": [1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0],
    "ceiling_W": 10.0,
    "ceiling_cite": "Radxa 'Requires 5V/2A power adapter' — an adapter rating, so an upper bound on the 5 V rail.",
}

POLLEN_CLAIM_H = 1.0
POLLEN_CLAIM_CITE = ("Pollen's press kit, via docs/ELECTRONICS-AND-SOFTWARE.md 9 and docs/PARTS.md row 35: "
                     "removable NP-F550, 2S Li-ion, 2600 mAh, '~1 h'. Recorded in "
                     "ce-parts/np-f550/electrical.part.json capacity.runtime_h_claimed_by_pollen with the note "
                     "'18.7 Wh / 1 h ~ 19 W average, a number nobody here measured'.")


def constants(v):
    tau_s, i_s, rpm0 = SERVO_ROWS[v]
    w0 = rpm0 * 2 * math.pi / 60.0
    return {"V": float(v), "stall_torque_Nm": tau_s, "stall_current_A": i_s, "no_load_speed_rpm": rpm0,
            "no_load_speed_rad_s": round(w0, 6),
            "kT_Nm_per_A": round(tau_s / i_s, 6),
            "R_ohm": round(float(v) / i_s, 6),
            "kE_V_s_per_rad": round(float(v) / w0, 6)}


def servo_power(tau, omega, k, v_pack):
    """tau, omega: (T, J) arrays. -> per-frame total motor electrical power (W) for the
    simulated joints, plus diagnostics. Regeneration is not credited: a negative
    mechanical power still costs the resistive term, which this model already gives."""
    I = np.abs(tau) / k["kT_Nm_per_A"]
    Vm = k["kE_V_s_per_rad"] * np.abs(omega) + k["R_ohm"] * I
    over = Vm > v_pack
    Vm_clipped = np.minimum(Vm, v_pack)
    P = Vm_clipped * I
    return P, I, Vm, int(over.sum()), Vm_clipped


def analyse(traj_path, label, k, v_pack, t_from=0.0):
    z = np.load(traj_path, allow_pickle=True)
    # torque and joint speed are recorded at the 200 Hz PHYSICS step, not at the 50 Hz
    # control frame — sampling only the control frame misses the intra-step peak.
    t = z["phys_time"]
    m = t >= t_from
    tau = z["tau"][m]
    jv = z["jv"][m]
    P, I, Vm, n_over, Vmc = servo_power(tau, jv, k, v_pack)
    P_motor_total = P.sum(axis=1)                              # W, 14 joints
    standby_total = N_SERVOS_TOTAL * STANDBY_A * v_pack        # W, all 15 controllers
    P_servos = P_motor_total + standby_total
    P_mech = (np.abs(tau) * np.abs(jv)).sum(axis=1)
    dur = float(t[m][-1] - t[m][0])
    return {
        "label": label,
        "traj": os.path.relpath(traj_path, ROOT),
        "window_s": [round(float(t[m][0]), 3), round(float(t[m][-1]), 3)],
        "duration_s": round(dur, 3),
        "frames": int(m.sum()),
        "servo_motor_power_W": {"mean": round(float(P_motor_total.mean()), 4),
                                "p50": round(float(np.percentile(P_motor_total, 50)), 4),
                                "p95": round(float(np.percentile(P_motor_total, 95)), 4),
                                "peak": round(float(P_motor_total.max()), 4)},
        "servo_controller_standby_W": round(standby_total, 4),
        "servo_controller_standby_W_ASSUMPTION": STANDBY_ASSUMPTION,
        "servo_controller_standby_W_if_billed_at_the_5.0V_row": round(
            N_SERVOS_TOTAL * STANDBY_A * STANDBY_ALT_V, 4),
        "servo_total_power_W_mean_if_standby_billed_at_the_5.0V_row": round(
            float(P_servos.mean()) - standby_total + N_SERVOS_TOTAL * STANDBY_A * STANDBY_ALT_V, 4),
        "servo_total_power_W": {"mean": round(float(P_servos.mean()), 4),
                                "p95": round(float(np.percentile(P_servos, 95)), 4),
                                "peak": round(float(P_servos.max()), 4)},
        "mechanical_output_power_W": {"mean": round(float(P_mech.mean()), 4),
                                      "peak": round(float(P_mech.max()), 4)},
        "electromechanical_efficiency_mean": round(float(P_mech.mean() / max(P_motor_total.mean(), 1e-12)), 4),
        "pack_current_from_servos_A": {"mean": round(float(P_servos.mean() / v_pack), 4),
                                       "peak": round(float(P_servos.max() / v_pack), 4)},
        "peak_single_servo_current_A": round(float(I.max()), 4),
        "peak_single_servo_current_joint": JOINT_NAMES[int(np.unravel_index(I.argmax(), I.shape)[1])],
        "frames_needing_more_than_pack_voltage": n_over,
        "frames_total_joint": int(I.size),
        "energy_Wh_per_hour_of_this_mode": round(float(P_servos.mean()), 4),
    }


def main():
    os.makedirs(EVID, exist_ok=True)
    v_pack = PACK["v_used"]
    ks = {v: constants(v) for v in SERVO_ROWS}
    k = ks["5.0"]

    modes = {}
    modes["walking"] = analyse(os.path.join(SWEEP, "base_walk_vx0.25_traj.npz"),
                               "walking, vx 0.25 m/s (cell base_walk_vx0.25), after the 0.5 s warm-up", k, v_pack,
                               t_from=0.5)
    modes["standing"] = analyse(os.path.join(SWEEP, "stand_hold_traj.npz"),
                                "standing, stand policy holding the pose (cell stand_hold)", k, v_pack, t_from=1.0)
    idle_servo_W = N_SERVOS_TOTAL * STANDBY_A * v_pack
    modes["idle_torque_off"] = {
        "label": "idle: torque disabled, no motion — the only published servo figure applies",
        "traj": None, "duration_s": None,
        "servo_motor_power_W": {"mean": 0.0, "p50": 0.0, "p95": 0.0, "peak": 0.0},
        "servo_controller_standby_W": round(idle_servo_W, 4),
        "servo_total_power_W": {"mean": round(idle_servo_W, 4), "p95": round(idle_servo_W, 4),
                                "peak": round(idle_servo_W, 4)},
        "note": "Torque Enable(64)=0 leaves the controller awake on the bus (ROBOTIS e-Manual: there is no "
                "sleep mode), so 15 x 17 mA is the floor. No mechanical power.",
        "ASSUMPTION_standby_voltage": STANDBY_ASSUMPTION,
        "servo_controller_standby_W_at_pack_rail": round(idle_servo_W, 4),
        "servo_controller_standby_W_at_the_5.0V_row": round(N_SERVOS_TOTAL * STANDBY_A * STANDBY_ALT_V, 4),
        "this_mode_is_entirely_that_assumption": True,
    }

    # sensitivity of the walking figure to which stall row the constants come from
    sens = {v: analyse(os.path.join(SWEEP, "base_walk_vx0.25_traj.npz"), "walking @ constants from the %s V row" % v,
                       ks[v], v_pack, t_from=0.5)["servo_total_power_W"]["mean"] for v in SERVO_ROWS}
    # and to the pack voltage (which sets the standby term and the clip)
    sens_vpack = {("%.1f" % vv): analyse(os.path.join(SWEEP, "base_walk_vx0.25_traj.npz"), "vp", k, vv,
                                         t_from=0.5)["servo_total_power_W"]["mean"] for vv in (6.6, 7.4, 8.2)}

    Wh = PACK["Wh"]
    table = {}
    for mode, d in modes.items():
        pservo = d["servo_total_power_W"]["mean"]
        rows = []
        for pc in COMPUTE["swept_W"]:
            tot = pservo + pc
            rows.append({"compute_and_sensors_W": pc, "total_W": round(tot, 4),
                         "runtime_h": round(Wh / tot, 4), "runtime_min": round(60.0 * Wh / tot, 2),
                         "pack_current_A_at_%.1fV" % PACK["v_used"]: round(tot / PACK["v_used"], 4)})
        table[mode] = {"servo_mean_W": round(pservo, 4), "rows": rows}

    # invert Pollen's claim
    walk_servo = modes["walking"]["servo_total_power_W"]["mean"]
    implied_total = Wh / POLLEN_CLAIM_H
    implied_compute = implied_total - walk_servo

    doc = {
        "study": "battery-runtime",
        "inputs": {
            "pack": PACK,
            "servo": {"part": "part:xl330-m288-t", "qty_per_robot": N_SERVOS_TOTAL,
                      "qty_actuated_in_the_MJCF": N_SERVOS_SIMULATED,
                      "qty_not_in_the_MJCF": "1 (ID 34, the mouth/jaw servo — the published model has no mouth "
                                             "joint, so it is carried at controller standby only)",
                      "published_rows": SERVO_ROWS, "cite": SERVO_CITE,
                      "derived_constants_per_row": ks,
                      "constants_used": k,
                      "kE_consistency_check": "kE from the three independent rows: %.6f / %.6f / %.6f V.s/rad "
                                              "(spread %.2f %%). kT: %.6f / %.6f / %.6f N.m/A (spread %.2f %%). "
                                              "R: %.6f / %.6f / %.6f ohm (spread %.2f %%)." % (
                                                  ks["3.7"]["kE_V_s_per_rad"], ks["5.0"]["kE_V_s_per_rad"],
                                                  ks["6.0"]["kE_V_s_per_rad"],
                                                  100 * (max(x["kE_V_s_per_rad"] for x in ks.values())
                                                         - min(x["kE_V_s_per_rad"] for x in ks.values()))
                                                  / ks["5.0"]["kE_V_s_per_rad"],
                                                  ks["3.7"]["kT_Nm_per_A"], ks["5.0"]["kT_Nm_per_A"],
                                                  ks["6.0"]["kT_Nm_per_A"],
                                                  100 * (max(x["kT_Nm_per_A"] for x in ks.values())
                                                         - min(x["kT_Nm_per_A"] for x in ks.values()))
                                                  / ks["5.0"]["kT_Nm_per_A"],
                                                  ks["3.7"]["R_ohm"], ks["5.0"]["R_ohm"], ks["6.0"]["R_ohm"],
                                                  100 * (max(x["R_ohm"] for x in ks.values())
                                                         - min(x["R_ohm"] for x in ks.values()))
                                                  / ks["5.0"]["R_ohm"]),
                      "no_load_current": {"verdict": "CANNOT DETERMINE",
                                          "why": "ROBOTIS publishes no no-load current for the XL330-M288-T; the "
                                                 "Specifications table carries only the three stall rows and "
                                                 "'Standby Current | 17 [mA]'. I = tau/kT therefore goes to zero "
                                                 "at zero torque, so every motor figure here is a LOWER bound. "
                                                 "WHAT SETTLES IT: Present Current(126) read off an unloaded "
                                                 "servo turning at speed, or a bench ammeter."}},
            "compute_and_sensors": COMPUTE,
            "torque_and_speed_source": "sim/gait_sweep.py, data.actuator_force and data.qvel recorded at every "
                                       "200 Hz PHYSICS step (MuJoCo timestep 0.005 s) of "
                                       "out/sim-sweep/base_walk_vx0.25_traj.npz and stand_hold_traj.npz, and "
                                       "read back here off the arrays' `phys_time` axis — NOT at the 50 Hz "
                                       "control frame. The peak-torque table is out/sim-evidence/"
                                       "gait-peaks.json, which samples the same 200 Hz record.",
            "assumptions_flagged": [
                {"what": "the voltage the XL330-M288-T's 17 mA standby current is billed at",
                 "used": "the pack rail (7.4 V) -> 15 x 0.017 x 7.4 = 1.887 W",
                 "alternative": "the 5.0 V row -> 15 x 0.017 x 5.0 = 1.275 W, 32.4 % smaller",
                 "why_this_one": "conservative for runtime, and the servos are fed the raw pack",
                 "detail": STANDBY_ASSUMPTION},
                {"what": "no-load current", "used": "zero (I = |tau|/kT)",
                 "alternative": "none publishable — ROBOTIS states no no-load current",
                 "why_this_one": "a missing value stays missing; every motor figure here is therefore a LOWER "
                                 "bound", "detail": "see servo.no_load_current"},
                {"what": "PWM-stage efficiency", "used": "1.00 (loss-free)",
                 "alternative": "any real efficiency < 1 raises the draw and shortens the runtime",
                 "why_this_one": "no vendor figure exists for the XL330's internal drive",
                 "detail": "stated in method"},
            ],
            "control_dt_s": CTRL_DT,
            "integration_dt_s": 0.005,
            "integration_rate_note": "power is integrated at the 200 Hz physics step (MuJoCo timestep 0.005 s), "
                                     "not at the 50 Hz control frame.",
        },
        "method": "Per 200 Hz PHYSICS frame and per actuated joint: I = |tau|/kT ; Vm = kE*|omega| + R*I ; "
                  "P_motor = min(Vm, V_pack)*I — the min() is the pack rail, and "
                  "frames_needing_more_than_pack_voltage reports how often it binds (0 in every mode of this "
                  "run, so it changes no number here). Sum over the 14 simulated joints, add "
                  "15 x 17 mA x V_pack of controller standby — SEE inputs.assumptions_flagged: ROBOTIS gives "
                  "that 17 mA no voltage, and billing it at the 5.0 V row instead makes the standby term "
                  "32.4 %% smaller — average over the mode's window, then add the swept compute+sensor draw "
                  "and divide the pack's 18.7 Wh by the total. Regeneration is not credited and the PWM stage is "
                  "taken as loss-free, both of which make the stated hours optimistic.",
        "outputs": {
            "modes": modes,
            "runtime_table": table,
            "sensitivity_servo_constants_walking_mean_W": sens,
            "sensitivity_pack_voltage_walking_mean_W": sens_vpack,
            "pollen_claim": {
                "claimed_h": POLLEN_CLAIM_H, "cite": POLLEN_CLAIM_CITE,
                "implied_total_average_W": round(implied_total, 4),
                "measured_servo_average_W_walking": round(walk_servo, 4),
                "implied_compute_and_sensors_W": round(implied_compute, 4),
                "reading": "This model puts walking at %.3f W of servo draw, so the pack's 18.7 Wh would run "
                           "%.2f h of continuous walking with 1.0 W of compute and %.2f h with 2.0 W — roughly "
                           "TWICE Pollen's published ~1 h. The gap is the model's own stated omissions, and it "
                           "points at the servos rather than at compute: for the whole machine to average the "
                           "%.3f W that ~1 h implies, everything that is not modelled here would have to draw "
                           "%.3f W — %s Radxa's entire 5 V/2 A (10.0 W) adapter rating for the board, which "
                           "makes it an implausible figure for compute alone. The missing power is more "
                           "likely (a) the XL330's unpublished no-load current, which this model sets to zero "
                           "and which fifteen servos multiply, (b) PWM-stage loss, taken here as zero, and "
                           "(c) pack energy below the 6.6 V cutoff that is never delivered — in some "
                           "combination. It is also possible the press-kit hour is a mixed-use hour rather "
                           "than an hour of walking. EVERY ONE OF THOSE IS SETTLED BY THE SAME MEASUREMENT: "
                           "an ammeter in the pack lead, plus Present Current(126) summed off the bus so the "
                           "servo and board halves separate."
                           % (walk_servo, Wh / (walk_servo + 1.0), Wh / (walk_servo + 2.0),
                              implied_total, implied_compute,
                              "ABOVE" if implied_compute > COMPUTE["ceiling_W"] else
                              "%.1f %% of" % (100.0 * implied_compute / COMPUTE["ceiling_W"])),
            },
        },
        "verdict": "CANNOT DETERMINE",
        "why": "The SERVO half is measured and cited: walking draws %.3f W mean / %.3f W peak at the pack "
               "(%.3f A / %.3f A at 7.4 V), standing %.3f W, idle-with-torque-off %.3f W, all from MuJoCo "
               "torque and speed through ROBOTIS's own published stall and no-load rows. The COMPUTE half is "
               "not: no vendor states the Radxa ZERO 3W's consumption, so a single runtime number cannot be "
               "given without inventing one. What CAN be stated: at a compute+sensor draw of 1.0 W the pack "
               "gives %.2f h of walking, at 2.0 W %.2f h, at 3.0 W %.2f h, at 5.0 W %.2f h; standing at 2.0 W "
               "gives %.2f h. Pollen's published ~1 h implies %.3f W total, i.e. %.3f W for everything that is "
               "not a servo. WHAT SETTLES IT: an ammeter in the pack lead of a running unit — one measurement "
               "closes both this and the pack's usable-energy question."
               % (modes["walking"]["servo_total_power_W"]["mean"], modes["walking"]["servo_total_power_W"]["peak"],
                  modes["walking"]["pack_current_from_servos_A"]["mean"],
                  modes["walking"]["pack_current_from_servos_A"]["peak"],
                  modes["standing"]["servo_total_power_W"]["mean"],
                  modes["idle_torque_off"]["servo_total_power_W"]["mean"],
                  table["walking"]["rows"][0]["runtime_h"], table["walking"]["rows"][2]["runtime_h"],
                  table["walking"]["rows"][4]["runtime_h"], table["walking"]["rows"][6]["runtime_h"],
                  table["standing"]["rows"][2]["runtime_h"],
                  implied_total, implied_compute),
        "script": "sim/battery_runtime.py",
        "artifacts": ["out/sim-sweep/base_walk_vx0.25_traj.npz", "out/sim-sweep/stand_hold_traj.npz",
                      "out/sim-evidence/gait-peaks.json"],
        "looked_at": [
            "ce-parts/xl330-m288-t/electrical.chip.json",
            "ce-parts/xl330-m288-t/iterations/v0.0.1/docs/fetched/robotis-emanual-xl330-m288.html",
            "ce-parts/np-f550/electrical.part.json", "ce-parts/np-f550/component.json",
            "ce-parts/np-f550/docs/duracell-dr5-np-f550-2600mah.html",
            "out/handover/elec-verify-wf_969f3a4c.json (Radxa Zero 3W row: '5V/2A', no consumption figure)",
            "ELECTRONICS-DATASHEET.html", "docs/ELECTRONICS-AND-SOFTWARE.md 3.4, 6, 9",
            "https://docs.radxa.com/en/zero/zero3 (fetched 2026-09-02)",
            "https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_product_brief.pdf (fetched 2026-09-02)",
        ],
    }
    p = os.path.join(EVID, "battery-runtime.json")
    json.dump(doc, open(p, "w"), indent=1)
    print("wrote", os.path.relpath(p, ROOT), doc["verdict"])
    for mode, d in modes.items():
        print("  %-16s servo mean %7.3f W  peak %7.3f W" % (mode, d["servo_total_power_W"]["mean"],
                                                            d["servo_total_power_W"]["peak"]))
    print("  walking runtime h:", [(r["compute_and_sensors_W"], r["runtime_h"]) for r in table["walking"]["rows"]])
    print("  standing runtime h:", [(r["compute_and_sensors_W"], r["runtime_h"]) for r in table["standing"]["rows"]])
    print("  sensitivity by stall row:", sens, " by pack V:", sens_vpack)
    print("  Pollen 1 h implies %.3f W total, %.3f W non-servo" % (implied_total, implied_compute))


if __name__ == "__main__":
    main()
