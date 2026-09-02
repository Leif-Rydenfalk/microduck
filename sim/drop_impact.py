#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""drop_impact.py — a 0.250 m fall onto one foot and onto the head: energy,
peak force and the model behind each number, analytic vs MuJoCo.

Lane F1, 2026-09-02. Every input is cited; the two models are compared and
the disagreement is the finding, not hidden.

  ENERGY      E = m g h with m read off the MJCF inertials (0.737243 kg,
              out/sim-evidence/loads_mujoco.json model.mass_kg_from_mjcf_inertials).
  MODEL A     rigid body on a linear contact spring K: F = v sqrt(K m).
              K from the cited modulus: TPU sole floor in compression
              (E A / t) and PLA head shell (through-thickness patch).
  MODEL B     Hertz contact of the struck curvature (sole heel arc R 7.204
              mm, sole part.py; head dome fitted below) on a rigid floor,
              energy balance: E = (8/15) E* sqrt(R) d^2.5, F = (4/3) E*
              sqrt(R) d^1.5 — reported with the bottoming-out check against
              the wall thickness (sole floor 2.000 mm; head shell measured
              here off the mesh with cecad.meshslice.intervals).
  MODEL C     MuJoCo (sim/measure_loads.py): default contact solref
              (0.02 s, 1) at 5 ms and 50 us steps, and the solref that
              encodes K of model A at 50 us — read from loads_mujoco.json.
  JOINT CAP   whether the XL330 torque limit (forcerange 0.96 N m,
              robot_walk.xml) can cap the transmitted force: the knee sits
              at -0.00494 rad in DEFAULT_POSE (common.py), i.e. straight, so
              the leg carries a landing axially and the torque limit does
              not bound it.

Writes out/sim-evidence/drop_impact.json.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(ROOT)), "ce-cad"))
from cecad import meshslice as ms  # noqa: E402

EVID = os.path.join(ROOT, "out", "sim-evidence")
L = json.load(open(os.path.join(EVID, "loads_mujoco.json")))
G = 9.81
H = 0.250
m = L["model"]["mass_kg_from_mjcf_inertials"]


def head_shell_measure():
    """Apex wall thickness and local dome radius of top_head_shell, off the mesh."""
    path = os.path.join(ROOT, "ce-parts", "microduck-top-head-shell", "current", "geometry", "top_head_shell.stl")
    T = np.asarray(ms.load(path), dtype=float)
    V = T.reshape(-1, 3)
    scale = 1000.0 if V.max() < 1.0 else 1.0        # Pollen's assets are metres
    T = T * scale; V = V * scale
    ext = V.max(0) - V.min(0)
    ax = "xyz"[int(np.argmin(ext))]                 # the 46 mm axis is the dome height
    zi = "xyz".index(ax)
    apex = V[np.argmax(V[:, zi])]
    ui, vi = {"x": (1, 2), "y": (2, 0), "z": (0, 1)}[ax]
    iv = ms.intervals(T, ax, apex[ui], apex[vi])
    top = sorted(iv, key=lambda s: -s[1])[0] if iv else None
    t_apex = (top[1] - top[0]) if top else None
    # local dome radius: sphere fit to the cap within 12 mm of the apex (planar distance)
    d = np.linalg.norm(np.delete(V, zi, axis=1) - np.delete(apex, zi), axis=1)
    cap = V[(d < 12.0) & (V[:, zi] > apex[zi] - 6.0)]
    A = np.c_[2 * cap, np.ones(len(cap))]; b = (cap ** 2).sum(1)
    c, *_ = np.linalg.lstsq(A, b, rcond=None)
    ctr = c[:3]; R = float(np.sqrt(c[3] + (ctr ** 2).sum()))
    rms = float(np.sqrt(((np.linalg.norm(cap - ctr, axis=1) - R) ** 2).mean()))
    return {"mesh": os.path.relpath(path, ROOT), "dome_axis": ax, "apex_mm": [round(float(x), 4) for x in apex],
            "intervals_along_axis_at_apex_mm": [[round(a, 4), round(b, 4)] for a, b in iv],
            "apex_wall_thickness_mm": round(t_apex, 4) if t_apex else None,
            "local_dome_radius_mm": round(R, 3), "sphere_fit_rms_mm": round(rms, 4), "cap_points": int(len(cap)),
            "how": "cecad.meshslice.intervals along the dome axis through the apex vertex (outer-most interval = the shell wall); "
                   "algebraic least-squares sphere on the vertices within 12 mm (in plan) and 6 mm (in height) of the apex"}


def hertz(E_star_MPa, R_mm, E_J):
    """rigid mass with energy E onto a Hertzian sphere-on-flat of radius R: (delta_mm, F_N)"""
    E_Nmm = E_J * 1000.0
    d = (15.0 * E_Nmm / (8.0 * E_star_MPa * np.sqrt(R_mm))) ** 0.4
    F = 4.0 / 3.0 * E_star_MPa * np.sqrt(R_mm) * d ** 1.5
    return float(d), float(F)


def main():
    E = m * G * H
    v = float(np.sqrt(2 * G * H))
    p = m * v
    head = head_shell_measure()

    # ---- material inputs (cited) ----------------------------------------------
    mats = {
        "TPU_table": {"E_MPa": 26.0, "nu": 0.48, "source": "ce-cad/cecad/fits.py MATERIALS['TPU'] youngs 0.026 GPa (class tier); nu 0.48 cecad.materials.poisson_for('TPU')"},
        "TPU_tds": {"E_MPa": 12.0, "nu": 0.48, "source": "research/tds/ninjaflex-tds.pdf: Tensile Modulus ASTM D638 12 MPa (NinjaFlex 85A)"},
        "PLA_table": {"E_MPa": 3500.0, "nu": 0.36, "source": "ce-cad/cecad/fits.py MATERIALS['PLA'] youngs 3.5 GPa (class tier); nu 0.36 cecad.materials.poisson_for('PLA')"},
        "PLA_tds": {"E_MPa": 2300.0, "nu": 0.36, "source": "research/tds/prusament-pla-tds-2021-10-en.pdf: Tensile Modulus ISO 527-1 2.3 +- 0.1 GPa (printed, horizontal)"},
    }
    sole = {"heel_arc_R_mm": 7.204, "floor_t_mm": 2.000, "floor_A_mm2": 41.1 * 54.0,
            "source": "ce-parts/microduck-sole-left/current/cad/part.py: heel arc R 7.204 c (36.653,-24.036) (out/measure/foot/fit_floor.py); FLOOR_T 2.0; bbox 41.1 x 54"}

    # ---- model A: rigid on a linear spring ----------------------------------------
    K_tpu = mats["TPU_table"]["E_MPa"] * sole["floor_A_mm2"] / sole["floor_t_mm"] * 1000.0     # N/m
    K_tpu_tds = mats["TPU_tds"]["E_MPa"] * sole["floor_A_mm2"] / sole["floor_t_mm"] * 1000.0
    t_head = head["apex_wall_thickness_mm"]
    K_pla_head = (mats["PLA_table"]["E_MPa"] * 20.0 / t_head * 1000.0) if t_head else None    # 20 mm^2 first-contact patch, stated assumption
    A = {
        "foot_rigid_on_tpu_floor_table": {"K_N_per_m": K_tpu, "F_peak_N": v * np.sqrt(K_tpu * m)},
        "foot_rigid_on_tpu_floor_tds": {"K_N_per_m": K_tpu_tds, "F_peak_N": v * np.sqrt(K_tpu_tds * m)},
        "head_rigid_on_pla_patch_table": ({"K_N_per_m": K_pla_head, "F_peak_N": v * np.sqrt(K_pla_head * m), "patch_mm2_ASSUMED": 20.0}
                                          if K_pla_head else {"verdict": "CANNOT DETERMINE", "why": "apex wall thickness not measured"}),
    }
    for k in A.values():
        if "F_peak_N" in k:
            k["F_peak_N"] = round(float(k["F_peak_N"]), 2); k["K_N_per_m"] = round(float(k["K_N_per_m"]), 1)

    # ---- model B: Hertz on the struck curvature, with bottoming-out ------------------
    B = {}
    dome_ok = head["sphere_fit_rms_mm"] <= 0.3     # a sphere that misses the cap by more than 0.3 mm rms is not the local curvature
    for label, mat, R, t in (("foot_heel_arc_tpu_table", "TPU_table", sole["heel_arc_R_mm"], sole["floor_t_mm"]),
                             ("foot_heel_arc_tpu_tds", "TPU_tds", sole["heel_arc_R_mm"], sole["floor_t_mm"]),
                             ("head_dome_pla_table", "PLA_table", head["local_dome_radius_mm"], t_head),
                             ("head_dome_pla_tds", "PLA_tds", head["local_dome_radius_mm"], t_head)):
        if label.startswith("head") and not dome_ok:
            B[label] = {"verdict": "CANNOT DETERMINE", "why": "the head shell is not spherical at its apex: least-squares sphere on the cap misses by %.3f mm rms "
                        "(> 0.3 mm), so no Hertz radius exists to use; what settles it: the head's true apex curvature from the graded head model (lane A)" % head["sphere_fit_rms_mm"],
                        "fitted_R_mm_unusable": R, "wall_mm": t}
            continue
        Em, nu = mats[mat]["E_MPa"], mats[mat]["nu"]
        Es = Em / (1 - nu ** 2)
        d, F = hertz(Es, R, E)
        B[label] = {"E_star_MPa": round(Es, 3), "R_mm": R, "delta_mm": round(d, 4), "F_peak_N": round(F, 2),
                    "wall_mm": t, "bottoms_out": (d > t) if t else None,
                    "note": ("indentation exceeds the wall — the Hertz half-space does not hold, the load goes into the structure behind "
                             "(foot ribs / shell bending); F is then a LOWER bound of the rigid-body impact" if (t and d > t) else
                             "indentation within the wall; half-space assumption marginal for a thin shell")}

    # ---- model C: MuJoCo ----------------------------------------------------------
    C = {}
    for d in L["drops"]:
        C[d["label"]] = {"peak_normal_force_N": d["peak_normal_force_N"], "peak_over_bodyweight": d["peak_over_bodyweight"],
                         "impulse_Ns": d["impulse_on_target_Ns"], "timestep_s": d["timestep_s"], "solref": d["solref"],
                         "struck": d["struck_geom"], "time_to_peak_after_contact_s": d["time_to_peak_after_contact_s"],
                         "peak_knee_torque_Nm": max(d["peak_abs_torque_Nm"]["left_knee"], d["peak_abs_torque_Nm"]["right_knee"]),
                         "knee_saturated_steps": d["torque_saturated_steps"]["left_knee"] + d["torque_saturated_steps"]["right_knee"],
                         "body_forces_N": {b: vv["magnitude"] for b, vv in d["body_transmitted_force_max_N"].items()}}
    # the stiffness MuJoCo's default contact actually represents
    tc, dr, dmax = 0.02, 1.0, 0.95
    k_default = m / (dmax * tc ** 2 * dr ** 2)

    # ---- joint cap ---------------------------------------------------------------
    from common import DEFAULT_POSE, JOINT_NAMES  # noqa: E402
    knee = float(DEFAULT_POSE[JOINT_NAMES.index("left_knee")])
    cap = {"knee_angle_default_pose_rad": knee, "knee_angle_deg": round(float(np.degrees(knee)), 4),
           "actuator_forcerange_Nm": L["model"]["actuator_class"],
           "finding": ("the DEFAULT_POSE knee is %.3f deg from straight, so a landing load passes through the shin and thigh almost axially; "
                       "the 0.96 N m torque limit bounds only the transverse component and cannot cap the axial impact force — the structure "
                       "sees whatever the contact compliance lets through" % abs(np.degrees(knee)))}

    # ---- verdict --------------------------------------------------------------------
    mj_soft = C["drop_foot_rollm10_default_contact_dt5ms"]["peak_normal_force_N"]
    mj_stiff = C["drop_foot_rollm10_stiff_tpu_whole_mass_dt50us"]["peak_normal_force_N"]
    ratioA = A["foot_rigid_on_tpu_floor_table"]["F_peak_N"] / mj_stiff
    out = {
        "study": "drop_impact",
        "generated": "2026-09-02", "script": "sim/drop_impact.py",
        "inputs": {"mass_kg": m, "mass_source": "loads_mujoco.json model.mass_kg_from_mjcf_inertials (sum of robot_walk.xml <inertial> masses)",
                   "height_m": H, "g_m_s2": G, "materials": mats, "sole": sole, "head_shell": head,
                   "mujoco_default_contact": {"solref": [tc, dr], "solimp_dmax": dmax, "equivalent_stiffness_N_per_m": round(k_default, 1),
                                              "note": "k = m/(dmax tc^2 dampratio^2): the default contact is ~%.0fx softer than the TPU floor" % (K_tpu / k_default)}},
        "method": "energy E = m g h; A rigid-on-spring F = v sqrt(K m); B Hertz energy balance with bottoming-out check; C MuJoCo runs (sim/measure_loads.py)",
        "outputs": {"energy_J": round(E, 5), "impact_speed_m_s": round(v, 5), "momentum_Ns": round(p, 5),
                    "model_A_rigid_spring": A, "model_B_hertz": B, "model_C_mujoco": C, "joint_torque_cap": cap,
                    "cross_check_A_vs_C_stiff": {"analytic_F_N": A["foot_rigid_on_tpu_floor_table"]["F_peak_N"], "mujoco_stiff_F_N": mj_stiff,
                                                 "ratio": round(ratioA, 4),
                                                 "note": "same K in both; MuJoCo adds critical damping (dampratio 1), which raises the peak above the undamped v sqrt(Km)"},
                    "bracket_foot_N": {"lower_mujoco_default": mj_soft,
                                       "hertz_heel_tds": B["foot_heel_arc_tpu_tds"]["F_peak_N"], "hertz_heel_table": B["foot_heel_arc_tpu_table"]["F_peak_N"],
                                       "upper_rigid_tds": A["foot_rigid_on_tpu_floor_tds"]["F_peak_N"], "upper_rigid_table": A["foot_rigid_on_tpu_floor_table"]["F_peak_N"]},
                    "bracket_head_N": {"lower_mujoco_default": C["drop_head_default_contact_dt5ms"]["peak_normal_force_N"],
                                       "hertz_dome_tds": B["head_dome_pla_tds"].get("F_peak_N"), "hertz_dome_table": B["head_dome_pla_table"].get("F_peak_N"),
                                       "upper_rigid_table": A["head_rigid_on_pla_patch_table"].get("F_peak_N")}},
        "verdict": "CANNOT DETERMINE",
        "why": ("the peak force of a 0.250 m fall spans %.0f N (MuJoCo's default, deliberately soft contact, ~%.0fx softer than the TPU floor) to "
                "%.0f N (rigid robot on the TPU floor stiffness); the Hertz heel-arc model gives %.0f-%.0f N but indents %.1f-%.1f mm, past the 2.000 mm "
                "sole floor, so the sole bottoms out onto the PLA foot ribs and the real peak sits between the Hertz and rigid figures. "
                "The structural studies use the MuJoCo default-contact peak (%.3f N) as the STATED LOWER BOUND and report each part's linear "
                "failure load beside it. What settles it: one instrumented drop (accelerometer on the trunk, or a force plate under the foot) "
                "of a printed unit from 0.250 m." % (mj_soft, K_tpu / k_default, A["foot_rigid_on_tpu_floor_table"]["F_peak_N"],
                                                     B["foot_heel_arc_tpu_tds"]["F_peak_N"], B["foot_heel_arc_tpu_table"]["F_peak_N"],
                                                     B["foot_heel_arc_tpu_tds"]["delta_mm"], B["foot_heel_arc_tpu_table"]["delta_mm"], mj_soft)),
        "what_settles_it": "instrumented 0.250 m drop of a printed unit: trunk accelerometer (>= 5 kHz) or a force plate; the peak force and its duration",
        "artifacts": ["out/sim-evidence/loads_mujoco.json", "out/sim-evidence/loads_mujoco.npz"],
        "looked_at": [],
    }
    path = os.path.join(EVID, "drop_impact.json")
    json.dump(out, open(path, "w"), indent=1)
    print(json.dumps(out["outputs"]["bracket_foot_N"], indent=0)); print(json.dumps(out["outputs"]["bracket_head_N"], indent=0))
    print("head shell:", head["apex_wall_thickness_mm"], "mm at apex, local R", head["local_dome_radius_mm"], "rms", head["sphere_fit_rms_mm"])
    print("wrote", path)


if __name__ == "__main__":
    main()
