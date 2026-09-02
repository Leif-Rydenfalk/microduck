#!/usr/bin/env python3
"""struct_ce.py — buckling and first-mode frequency of the slender members,
through ce-struct (:8099, voxel mesher + CalculiX), on OUR rebuilt meshes.

Lane F1, 2026-09-02; revised 2026-09-03 after the F1 skeptic (findings 8, 9):
  * the shin's first version applied the landing-force MAGNITUDE (118.8160 N)
    as pure axial compression — the measured axial component is 99.11399 N
    (fea_microduck-shin_drop.json inputs.force_N_part_frame[2]), a 20 % error
    on the factor. Now every member is solved twice: with the measured
    AXIAL COMPONENT alone (the classical column number) and with the FULL
    measured vector in the part frame (the honest landing load, lateral
    components included — the eigen-solver's geometric stiffness carries the
    whole pre-stress state);
  * no mesh convergence existed and no localisation test: the factor is now
    swept over cell sizes, its drift between the two finest cells reported,
    the eigen-factor separation checked (three factors within 1 % = a local
    end-face mode, the artefact measured on the rigidity plate), and for the
    shin the eigen-solver is held against an Euler bracket from the section
    properties read off the mesh (sim/member_section.py).

The static FEA (sim/stress_all.py) asks whether a part yields; this asks
whether it FOLDS first. Loads are the measured MuJoCo peaks
(loads_mujoco.json), applied over the member's end face (at: min/max of the
long axis), the other end held. ce-struct rule: criticalFactor >= 2 PASS.

    python3 sim/struct_ce.py [--force] [slug ...]  -> out/sim-evidence/buckling_<part>.json
"""
import base64
import json
import os
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVID = os.path.join(ROOT, "out", "sim-evidence")
L = json.load(open(os.path.join(EVID, "loads_mujoco.json")))
DROP = next(d for d in L["drops"] if d["label"] == "drop_foot_rollm10_default_contact_dt5ms")
API = "http://127.0.0.1:8099/api/solve"
DRIFT_OK = 0.05          # factor drift between the two finest cells: converged below this
SEPARATION_MIN = 1.01    # factors 1..3 within 1 % of each other = a localised end-face mode


def fea_vector(slug, case="drop"):
    """The measured force vector the static FEA applied to this part (part frame, N) and its source string."""
    r = json.load(open(os.path.join(EVID, "fea_%s_%s.json" % (slug, case))))
    return r["inputs"]["force_N_part_frame"], r["inputs"]["force_source"], r["inputs"]["force_magnitude_N"]


# member: (slug, mesh file, long axis, held end, loaded end, material, printNormal (ASSUMED flat = thickness axis), share, cells mm)
MEMBERS = [
    ("microduck-shin", "leg.stl", "z", "max", "min", "PLA", "x", 1.0, [1.0, 0.7, 0.5]),
    ("microduck-neck-plate", "../../out/sim-evidence/fea/microduck-neck-plate_ours.stl", "y", "min", "max", "PLA", "x", 0.5, [0.4, 0.3]),
    ("microduck-upper-leg-rigidity-plate", "upper_leg_rigidity_plate.stl", "z", "min", "max", "PLA", "x", 1.0, [0.33]),
]


def solve(spec, study, stl_b64, options=None):
    body = json.dumps({"spec": spec, "study": study, "options": options or {}, "stlBase64": stl_b64}).encode()
    req = urllib.request.Request(API, data=body, headers={"content-type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=1800) as r:
        out = json.loads(r.read().decode())
    out["_seconds"] = round(time.time() - t0, 2)
    return out


def spec_for(slug, cell, axis, held, loaded, mat, pn, vec):
    return {"name": slug + " column", "cell": cell, "geometry": {"kind": "stl"},
            "bodies": [{"name": slug, "material": mat, "printNormal": pn}],
            "constraints": [{"name": "held", "face": {"axis": axis, "at": held}, "dirs": "xyz", "value": 0}],
            "loads": [{"name": "landing", "kind": "force", "face": {"axis": axis, "at": loaded}, "vector": vec}],
            "studies": ["buckle", "frequency"]}


def run_member(slug, stl, axis, held, loaded, mat, pn, share, cells):
    path = os.path.normpath(os.path.join(ROOT, "sim", "meshes_ours", stl))
    ai = "xyz".index(axis)
    vec_full, src, mag = fea_vector(slug)          # the static study's vector already carries the share (stress_all.py scaled it)
    axial = vec_full[ai]
    # compression is the load pushing the loaded end TOWARD the held end
    toward_held = (+1.0 if loaded == "min" else -1.0)
    compressive = axial * toward_held > 0
    vec_axial = [0.0, 0.0, 0.0]
    vec_axial[ai] = axial
    rec = {"study": "buckling_" + slug, "part": "part:" + slug, "generated": time.strftime("%Y-%m-%dT%H:%M:%S"), "script": "sim/struct_ce.py",
           "inputs": {"mesh": os.path.relpath(path, ROOT), "cells_mm": cells, "long_axis": axis, "held_face": axis + "=" + held, "loaded_face": axis + "=" + loaded,
                      "force_vector_part_frame_N": [round(x, 5) for x in vec_full], "force_magnitude_N": round(mag, 4),
                      "axial_component_N": round(axial, 5), "axial_is_compressive": compressive, "share": share,
                      "force_source": src + (" (already x %g: two identical plates share it — stress_all.py)" % share if share != 1.0 else ""),
                      "material": mat, "printNormal_ASSUMED": pn + " (the thickness axis — the part printed flat; no part.py declares print_up)",
                      "solver": "ce-struct /api/solve (voxel hex mesh + CalculiX *BUCKLE / *FREQUENCY)"},
           "method": "load over the whole loaded end face, the other end fixed xyz; buckling eigenvalue = load factor on the applied load; solved with the AXIAL component "
                     "alone and with the FULL measured vector, at each cell size; first natural frequency with the same support",
           "artifacts": [], "looked_at": []}
    if not os.path.exists(path):
        rec.update(verdict="CANNOT DETERMINE", why="no rebuilt mesh at %s" % rec["inputs"]["mesh"])
        return rec
    if not compressive:
        rec.update(verdict="CANNOT DETERMINE", why="the measured axial component %.4f N is TENSILE on this member at the drop peak (loaded %s, held %s) — no buckling case exists for it" % (axial, loaded, held))
        return rec
    b64 = base64.b64encode(open(path, "rb").read()).decode()
    rows = []
    for cell in cells:
        for label, vec in (("axial", vec_axial), ("full", vec_full)):
            spec = spec_for(slug, cell, axis, held, loaded, mat, pn, vec)
            row = {"cell_mm": cell, "load": label}
            try:
                b = solve(spec, "buckle", b64, {"modes": 3})
                row.update(cells=b.get("cells"), nodes=b.get("nodes"), factors=b.get("factors"), critical=b.get("critical") or b.get("criticalFactor"), seconds=b["_seconds"], error=b.get("error"))
            except Exception as e:  # noqa: BLE001
                row["error"] = str(e)[-300:]
            if label == "full":
                try:
                    fr = solve(spec, "frequency", b64, {"modes": 3})
                    row["first_mode_hz"] = fr.get("first_Hz"); row["modes_hz"] = [m.get("hz") for m in fr.get("modes", [])]
                except Exception as e:  # noqa: BLE001
                    row["frequency_error"] = str(e)[-200:]
            print("  %s cell %.2f %-5s -> %s (%s s)" % (slug, cell, label, row.get("factors"), row.get("seconds"))); sys.stdout.flush()
            rows.append(row)
    rec["outputs"] = {"rows": rows}
    judge(rec)
    return rec


def judge(rec):
    """PASS/FAIL on the ce-struct rule (factor >= 2) using the finest-cell FULL-vector factor, with three refusals:
    the three lowest factors within 1 % (local end-face mode), no converged pair, or the finest two cells still drifting > 5 %."""
    i, o = rec["inputs"], rec["outputs"]
    rows = o["rows"]
    ok = lambda r: r.get("factors") and not r.get("error")
    full = [r for r in rows if r["load"] == "full" and ok(r)]
    axial = [r for r in rows if r["load"] == "axial" and ok(r)]
    if not full and not axial:
        rec.update(verdict="CANNOT DETERMINE", why="buckle solve refused at every cell: %s" % "; ".join(str(r.get("error"))[:120] for r in rows)); return
    fin = (full or axial)[-1]
    facs = fin["factors"]
    crit = float(fin["critical"])
    o["critical_factor_full_finest"] = float(full[-1]["critical"]) if full else None
    o["critical_factor_axial_finest"] = float(axial[-1]["critical"]) if axial else None
    o["critical_load_N_full"] = round(o["critical_factor_full_finest"] * i["force_magnitude_N"], 4) if full else None
    o["critical_axial_load_N"] = round(o["critical_factor_axial_finest"] * abs(i["axial_component_N"]), 4) if axial else None
    fr = [r for r in rows if r.get("first_mode_hz")]
    o["first_mode_hz"] = fr[-1]["first_mode_hz"] if fr else None
    o["modes_hz"] = fr[-1].get("modes_hz") if fr else None
    drift = None
    if len(full) >= 2:
        a, b = float(full[-2]["critical"]), float(full[-1]["critical"])
        drift = abs(b - a) / max(b, 1e-12)
    o["convergence"] = {"cells_solved": [r["cell_mm"] for r in full], "factor_by_cell_full": [float(r["critical"]) for r in full],
                        "factor_by_cell_axial": [float(r["critical"]) for r in axial], "drift_finest_pair": (round(drift, 4) if drift is not None else None), "rule": "drift < %g" % DRIFT_OK}
    separation = (facs[2] / max(facs[0], 1e-12)) if len(facs) >= 3 else None
    o["mode_separation_f3_over_f1"] = round(separation, 6) if separation else None
    # Euler cross-check from the section table when it exists (the shin)
    sec_path = os.path.join(EVID, "section_%s.json" % rec["part"].split(":", 1)[1])
    euler = None
    if os.path.exists(sec_path) and axial:
        S = json.load(open(sec_path))["outputs"]
        e = S["euler_critical_N"]["table_3500"]
        crit_ax = o["critical_axial_load_N"]
        inside = e["K_2"] <= crit_ax <= e["K_0.7"]
        euler = {"section_study": os.path.relpath(sec_path, ROOT), "I_min_mm4_weakest": S["weakest_station"]["I_min_mm4"], "euler_N_K2_fixed_free": e["K_2"],
                 "euler_N_K1_pinned": e["K_1"], "euler_N_K0.7_fixed_pinned": e["K_0.7"], "eigen_axial_critical_N": crit_ax, "inside_bracket": inside,
                 "note": "E 3500 MPa (class table); the member is not prismatic, so this is an order-of-magnitude bracket — an eigen-solver answer inside it is a MEMBER mode, one far below it is a local one"}
    o["euler_crosscheck"] = euler
    if separation is not None and separation < SEPARATION_MIN:
        rec.update(verdict="CANNOT DETERMINE",
                   why="the three lowest eigen-factors %s lie within 1 %% of each other — a localised mode at the loaded end face (voxel edge crushing), not a member mode; "
                       "no buckling load of the member was found. What settles it: a shell/solid model loaded through the screw holes instead of the end face, or a printed part compressed in a rig" % [round(x, 6) for x in facs])
        return
    if drift is not None and drift > DRIFT_OK:
        rec.update(verdict="CANNOT DETERMINE",
                   why="the factor still moves %.2f %% between the two finest cells (%s) — not converged; what settles it: a finer cell or a tetrahedral mesh of the same case" % (
                       100 * drift, o["convergence"]["factor_by_cell_full"]))
        return
    if len(full) < 2 and len(axial) < 2:
        rec.update(verdict="CANNOT DETERMINE", why="one cell size only (%s) — no convergence evidence; factor %.4f" % (fin["cell_mm"], crit)); return
    v = "PASS" if crit >= 2.0 else "FAIL"
    rec.update(verdict=v, why=("buckling load factor %.4f on the FULL measured landing vector |F| %.4f N (critical %.2f N) at cell %s mm, drift %.2f %% from cell %s; "
                               "on the measured AXIAL component %.4f N alone the factor is %.4f (critical axial %.2f N)%s; ce-struct rule factor >= 2 -> %s; higher factors %s; "
                               "the first version (2026-09-02) applied the vector magnitude as axial and read 0.9262 — superseded" % (
                                   crit, i["force_magnitude_N"], crit * i["force_magnitude_N"], fin["cell_mm"], 100 * (drift or 0), full[-2]["cell_mm"] if len(full) >= 2 else "—",
                                   abs(i["axial_component_N"]), o["critical_factor_axial_finest"] or 0, o["critical_axial_load_N"] or 0,
                                   ("; Euler bracket %.1f-%.1f N (K 2..0.7) %s the eigen answer" % (euler["euler_N_K2_fixed_free"], euler["euler_N_K0.7_fixed_pinned"], "CONTAINS" if euler["inside_bracket"] else "does NOT contain")) if euler else "",
                                   v, [round(x, 4) for x in facs[1:]])))


def main():
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    for slug, stl, axis, held, loaded, mat, pn, share, cells in MEMBERS:
        if only and slug not in only:
            continue
        prev = os.path.join(EVID, "buckling_" + slug + ".json")
        if os.path.exists(prev) and "--force" not in sys.argv and (json.load(open(prev)).get("outputs") or {}).get("rows"):
            print("exists (v2 rows present)", slug); continue
        print("===", slug); sys.stdout.flush()
        rec = run_member(slug, stl, axis, held, loaded, mat, pn, share, cells)
        json.dump(rec, open(prev, "w"), indent=1)
        print("  ->", rec["verdict"], rec["why"][:300]); sys.stdout.flush()


if __name__ == "__main__":
    main()
