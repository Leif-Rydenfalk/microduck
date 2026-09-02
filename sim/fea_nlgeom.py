#!/usr/bin/env python3
"""fea_nlgeom.py — geometrically NONLINEAR re-solve of the studies whose linear
answer left the small-deflection regime (F1 skeptic finding 10, 2026-09-03).

A linear static solve is a prediction only while the deflection is small:
for a plate, while w_max is small against the thickness (the customary limit
is t/2 — Timoshenko & Woinowsky-Krieger, Theory of Plates and Shells, the
small-deflection assumptions of ch. 1 against the large-deflection theory of
ch. 13); for a member, while the rotation is small (delta/L <= 0.1, tip slope
~0.15 rad for a cantilever, cos 0.15 = 0.989). Outside that regime the linear
peak stress is a BOUND, not a number — so this script takes the SAME deck
(same mesh, same held nodes, same nodal loads, same linear-elastic material)
and re-runs CalculiX with *STEP, NLGEOM: the stiffness is updated on the
deformed shape, the load is ramped in increments, and the last converged
increment's field is reduced exactly as the linear one was (peak nodal von
Mises, peak |u|). The material stays linear-elastic, so this measures the
GEOMETRIC effect alone; a peak still past yield is still a failure.

    python3 sim/fea_nlgeom.py [study-name ...]     (default: every flagged study)
Writes out/sim-evidence/fea_nlgeom_<study>.json, one ccx job at a time, and
appends to out/sim-evidence/fea/progress.txt. A solve that does not reach the
full load records the fraction it reached and is CANNOT DETERMINE — never a
number at a load it did not carry.
"""
import glob
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVID = os.path.join(ROOT, "out", "sim-evidence")
FEA = os.path.join(EVID, "fea")
CCX = os.environ.get("CAD_CCX") or "/Applications/FreeCAD.app/Contents/Resources/bin/ccx"
REQUIRE_SF = 2.0
# the regime rule, applied by sim/fea_rejudge.py to every study; the same numbers here so the two cannot disagree
PLATE_ASPECT = 0.15      # thinnest / middle bbox side <= this -> a plate: the t/2 rule applies
PLATE_W_OVER_T = 0.5     # small-deflection plate theory: w_max <= t/2
MEMBER_D_OVER_L = 0.1    # small rotation: delta <= L/10
INITIAL, TOTAL, DTMIN, DTMAX, INC = 0.05, 1.0, 1e-6, 0.1, 400


def frd_peak(path):
    """max nodal von Mises and |u| straight out of a CalculiX .frd — the LAST
    block of each kind wins, which for a multi-increment NLGEOM job is the last
    converged increment (blocks are written in time order)."""
    mode, vm, dm, n, blocks = None, 0.0, 0.0, 0, {"STRESS": 0, "DISP": 0}
    for line in open(path, errors="replace"):
        s = line.rstrip("\n")
        if len(s) > 5 and s[1:3] == "-4":
            name = s[5:13].strip()
            mode = "S" if name == "STRESS" else ("D" if name == "DISP" else None)
            if name in blocks:
                blocks[name] += 1
                if mode == "S":
                    vm, n = 0.0, 0          # start over: only the last block counts
                if mode == "D":
                    dm = 0.0
            continue
        if len(s) > 5 and s[1:3] == "-3":
            mode = None
            continue
        if mode and s.startswith(" -1"):
            body, vals = s[13:], []
            for i in range(0, len(body), 12):
                t = body[i:i + 12].strip()
                if t:
                    try:
                        vals.append(float(t))
                    except ValueError:
                        pass
            if mode == "S" and len(vals) >= 6:
                sxx, syy, szz, sxy, syz, szx = vals[:6]
                vm = max(vm, math.sqrt(0.5 * ((sxx - syy) ** 2 + (syy - szz) ** 2 + (szz - sxx) ** 2) + 3 * (sxy ** 2 + syz ** 2 + szx ** 2)))
                n += 1
            if mode == "D" and len(vals) >= 3:
                dm = max(dm, math.sqrt(sum(v * v for v in vals[:3])))
    return vm, dm, n, blocks


def bbox_of_inp(path):
    mn, mx, innode = [1e9] * 3, [-1e9] * 3, False
    for line in open(path):
        if line.startswith("*"):
            innode = line.upper().startswith("*NODE")
            continue
        if innode:
            f = line.split(",")
            if len(f) >= 4:
                try:
                    c = [float(f[1]), float(f[2]), float(f[3])]
                except ValueError:
                    continue
                for j in range(3):
                    mn[j] = min(mn[j], c[j]); mx[j] = max(mx[j], c[j])
    return sorted(round(mx[j] - mn[j], 4) for j in range(3))


def regime(bbox, disp):
    """(valid, plate?, d/t, d/L) — the one rule for every study."""
    t, mid, L = bbox
    plate = (t / mid) <= PLATE_ASPECT
    d_t, d_L = disp / t, disp / L
    valid = d_L <= MEMBER_D_OVER_L and (not plate or d_t <= PLATE_W_OVER_T)
    return valid, plate, d_t, d_L


def flagged_studies():
    out = []
    for p in sorted(glob.glob(os.path.join(EVID, "fea_microduck-*.json"))):
        r = json.load(open(p))
        o = r.get("outputs") or {}
        if o.get("max_displacement_mm") is None:
            continue
        wd = os.path.join(ROOT, r["artifacts"][0])
        inp = glob.glob(os.path.join(wd, "*_mesh.inp"))
        if not inp:
            continue
        valid, plate, d_t, d_L = regime(bbox_of_inp(inp[0]), o["max_displacement_mm"])
        if not valid:
            out.append(r["study"][4:])
    return out


def sta_progress(path):
    """(last TOT TIME reached, increments) from the .sta summary."""
    tot, inc = 0.0, 0
    if not os.path.exists(path):
        return tot, inc
    for line in open(path):
        f = line.split()
        if len(f) >= 7 and f[0].isdigit():
            try:
                tot = max(tot, float(f[4])); inc = int(f[1])
            except ValueError:
                pass
    return tot, inc


def run(name, timeout=3 * 3600):
    t0 = time.time()
    study = json.load(open(os.path.join(EVID, "fea_%s.json" % name)))
    o = study["outputs"]
    wd = os.path.join(ROOT, study["artifacts"][0])
    job = os.path.basename(wd)
    src = os.path.join(wd, job + ".inp")
    nl = job + "_nlgeom"
    deck = open(src).read()
    if "*STEP\n*STATIC\n" not in deck:
        raise RuntimeError("deck %s has no plain *STEP/*STATIC block to convert" % src)
    deck = deck.replace("*STEP\n*STATIC\n", "*STEP, NLGEOM, INC=%d\n*STATIC\n%g, %g, %g, %g\n" % (INC, INITIAL, TOTAL, DTMIN, DTMAX), 1)
    open(os.path.join(wd, nl + ".inp"), "w").write(deck)
    for ext in (".frd", ".sta", ".cvg", ".dat"):
        try:
            os.remove(os.path.join(wd, nl + ext))
        except OSError:
            pass
    env = dict(os.environ, OMP_NUM_THREADS="2")
    r = subprocess.run([CCX, "-i", nl], cwd=wd, env=env, capture_output=True, text=True, timeout=timeout)
    out = (r.stdout or "") + (r.stderr or "")
    frd = os.path.join(wd, nl + ".frd")
    tot, incs = sta_progress(os.path.join(wd, nl + ".sta"))
    bbox = bbox_of_inp(glob.glob(os.path.join(wd, "*_mesh.inp"))[0])
    valid_lin, plate, d_t, d_L = regime(bbox, o["max_displacement_mm"])
    rec = {"study": "fea_nlgeom_" + name, "part": study["part"], "case": study["case"], "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "script": "sim/fea_nlgeom.py",
           "inputs": {"linear_study": "out/sim-evidence/fea_%s.json" % name, "deck": os.path.relpath(os.path.join(wd, nl + ".inp"), ROOT),
                      "same_as_linear": "mesh, held node set, nodal loads, E/nu — only the *STEP line differs",
                      "step": "*STEP, NLGEOM, INC=%d / *STATIC %g, %g, %g, %g (initial, total, min, max increment)" % (INC, INITIAL, TOTAL, DTMIN, DTMAX),
                      "force_magnitude_N": study["inputs"]["force_magnitude_N"], "force_N_part_frame": study["inputs"]["force_N_part_frame"],
                      "force_source": study["inputs"]["force_source"], "material": study.get("material"),
                      "yield_mpa_used": o.get("yield_mpa_used"), "require_sf": REQUIRE_SF,
                      "regime_rule": {"plate_if_thin_over_mid_le": PLATE_ASPECT, "plate_w_over_t_le": PLATE_W_OVER_T, "member_d_over_L_le": MEMBER_D_OVER_L,
                                      "basis": "small-deflection plate theory (Timoshenko & Woinowsky-Krieger, Theory of Plates and Shells: w small against t; t/2 customary) and small rotation (delta/L 0.1 ~ 0.15 rad tip slope)"},
                      "bbox_sorted_mm": bbox, "linear": {"max_von_mises_mpa": o["max_von_mises_mpa"], "max_displacement_mm": o["max_displacement_mm"], "sf": o["sf"],
                                                          "plate": plate, "d_over_t": round(d_t, 4), "d_over_L": round(d_L, 4), "in_small_deflection_regime": valid_lin}},
           "method": "CalculiX *STATIC with NLGEOM (updated Lagrangian, load ramped in increments, materially linear-elastic) on the identical deck; the last converged increment reduced to peak nodal von Mises and |u|",
           "artifacts": [os.path.relpath(wd, ROOT), os.path.relpath(os.path.join(wd, nl + ".inp"), ROOT)], "looked_at": []}
    outputs = {"ccx_returncode": r.returncode, "load_fraction_reached": tot, "increments": incs, "seconds": round(time.time() - t0, 1),
               "ccx_tail": "\n".join(out.strip().splitlines()[-8:])}
    if os.path.isfile(frd):
        vm, dm, n, blocks = frd_peak(frd)
        outputs.update({"max_von_mises_mpa": vm, "max_displacement_mm": dm, "stress_nodes": n, "frd_blocks": blocks})
        rec["artifacts"].append(os.path.relpath(frd, ROOT))
        if vm > 0:
            y = o.get("yield_mpa_used") or 0
            outputs["sf"] = y / vm if y else None
            outputs["ratio_nonlinear_over_linear_vm"] = vm / o["max_von_mises_mpa"]
            outputs["ratio_nonlinear_over_linear_disp"] = dm / o["max_displacement_mm"]
            valid_nl, _, d_t2, d_L2 = regime(bbox, dm)
            outputs["nonlinear_d_over_t"], outputs["nonlinear_d_over_L"] = round(d_t2, 4), round(d_L2, 4)
    rec["outputs"] = outputs
    converged = abs(tot - TOTAL) < 1e-9 and r.returncode == 0 and "*ERROR" not in out and outputs.get("max_von_mises_mpa")
    if converged:
        sf = outputs["sf"]
        rec["verdict"] = "PASS" if sf is not None and sf >= REQUIRE_SF else "FAIL"
        rec["why"] = ("geometrically nonlinear peak %.3f MPa (linear %.3f, ratio %.3f) and |u| %.4f mm (linear %.4f) at the full %.4f N; SF %.3f against %g MPa, the case requires %g; "
                      "%d increments" % (outputs["max_von_mises_mpa"], o["max_von_mises_mpa"], outputs["ratio_nonlinear_over_linear_vm"], outputs["max_displacement_mm"],
                                         o["max_displacement_mm"], study["inputs"]["force_magnitude_N"], sf, o.get("yield_mpa_used") or 0, REQUIRE_SF, incs))
    else:
        rec["verdict"] = "CANNOT DETERMINE"
        rec["why"] = ("the nonlinear solve reached %.4f of the load in %d increments and stopped (ccx rc %d)%s — no stress at the full load exists; the linear bound stands as a bound. "
                      "What settles it: a material-nonlinear (plastic) solve, or a printed part on a bench" % (
                          tot, incs, r.returncode, ("; at that fraction the peak was %.3f MPa, |u| %.4f mm" % (outputs["max_von_mises_mpa"], outputs["max_displacement_mm"])) if outputs.get("max_von_mises_mpa") else ""))
    path = os.path.join(EVID, rec["study"] + ".json")
    json.dump(rec, open(path, "w"), indent=1)
    with open(os.path.join(FEA, "progress.txt"), "a") as fh:
        fh.write("%s NLGEOM %s %s vM=%s disp=%s frac=%s %ss\n" % (time.strftime("%H:%M:%S"), rec["verdict"], rec["study"], outputs.get("max_von_mises_mpa"),
                                                                    outputs.get("max_displacement_mm"), tot, outputs["seconds"]))
    print(rec["verdict"], rec["study"], rec["why"][:200]); sys.stdout.flush()
    return rec


def main():
    names = [a for a in sys.argv[1:] if not a.startswith("--")] or flagged_studies()
    print("flagged:", names); sys.stdout.flush()
    for n in names:
        if os.path.exists(os.path.join(EVID, "fea_nlgeom_%s.json" % n)) and "--force" not in sys.argv:
            print("skip (exists)", n); continue
        try:
            run(n)
        except Exception as e:  # noqa: BLE001
            print("CRASH", n, e); sys.stdout.flush()


if __name__ == "__main__":
    main()
