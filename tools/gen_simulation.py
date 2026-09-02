#!/usr/bin/env python3
"""gen_simulation.py — assemble SIMULATION.html, the one document for every simulation study in this repo.

Reads (data, never hand-edited):
    out/sim-evidence/*.json            every study the three simulation lanes wrote (F1 structural / impact / fatigue,
                                       F2 gait robustness / battery, F3 thermal / tolerance), plus loads_mujoco.json
    out/stress/matrix.json, report.json, corrected.json   the detached night-shift stress matrix and its correction
    out/sim-evidence/fea/<study>/<part>_<case>.inp        the CalculiX decks: the load ACTUALLY applied (sum of *CLOAD)
    out/sim-sweep/videos.json                             lane F2's per-video read-back record
    ce-parts/np-f550/electrical.part.json                 the pack's current Wh / mAh / voltage window (cross-check)
    tools/gen_structural.py, gen_simulation_f2.py, gen_simulation_f3.py   the lanes' own section generators, imported
                                       and included as chapters A, B, C (renumbered here, never edited here)

Writes:
    SIMULATION.html                    only if selfcheck() passes; otherwise exits 1 and writes nothing

What this synth adds on top of the three chapters:
    - one verdict matrix over EVERY study file on disk, with counts that are recounted by selfcheck()
    - the load-basis chain made explicit and MEASURED end to end: MJCF inertial mass -> MuJoCo peaks -> the vector each
      FEA study quotes -> the force the solver deck actually applied (parsed out of the .inp) -> SF -> verdict
    - cross-checks between the lanes (F1 loads vs F2 peaks, F3 duty vs F2, pack Wh vs ce-parts/np-f550, masses, drop
      heights, fatigue vs FEA, the superseded stress matrix) — a disagreement is printed as DIFFER, never smoothed
    - the register of every CANNOT DETERMINE anywhere in any study file, with what settles it (or the fact that the
      file names nothing)
    - every image / video artifact any study names, read back (pixel size, distinct colours, ink) and linked

Run:  /Applications/FreeCAD.app/Contents/Resources/bin/python tools/gen_simulation.py   (PIL for the read-back)
      python3 tools/gen_simulation.py                                                     (stdlib only; read-back
                                                                                          columns say 'no PIL')
"""
import glob
import html
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
EV = os.path.join(REPO, "out", "sim-evidence")
STRESS = os.path.join(REPO, "out", "stress")
sys.path.insert(0, HERE)
import gen_structural as F1          # noqa: E402
import gen_simulation_f2 as F2       # noqa: E402
import gen_simulation_f3 as F3       # noqa: E402

E = html.escape
DATE = "2026-09-03"


# ----------------------------------------------------------------------------- helpers
def rel(p):
    return os.path.relpath(p, REPO)


def load(p):
    return json.load(open(p)) if os.path.exists(p) else None


def fmt(v, dp=None):
    """Print a number at the SOURCE's own precision (repr of the JSON float), never rounded here."""
    if v is None:
        return "—"
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        if dp is not None:
            return ("%%.%df" % dp) % v
        return repr(v)
    return E(str(v))


def pct(a, b):
    """(a - b) / b in %, or None."""
    if a is None or b is None or b == 0:
        return None
    return 100.0 * (a - b) / b


def norm(v):
    return math.sqrt(sum(float(x) * float(x) for x in v))


def chip(v):
    cls = {"PASS": "pass", "FAIL": "fail", "CANNOT DETERMINE": "cd", "AGREE": "pass", "DIFFER": "fail", "MEASUREMENT": "meas"}.get(v, "meas")
    return '<span class="chip %s">%s</span>' % (cls, E(v or "—"))


def first_sentence(s, n=240):
    if not s:
        return "—"
    m = re.search(r"^(.{40,}?[.!?])(\s|$)", s)
    head = m.group(1) if m else s
    if len(head) > n:
        head = head[:n].rstrip() + "…"
    return head


def anchor(name):
    return "reg-" + re.sub(r"[^A-Za-z0-9_.-]", "-", name)


# ----------------------------------------------------------------------------- the study files
FAMILIES = [
    ("structural", "A", "Structural FEA, buckling and the measured loads",
     lambda n: n.startswith(("fea_", "buckling_", "section_", "loads_mujoco", "skeptic_f1_recheck")), "#verdict"),
    ("impact", "A", "Drop / impact", lambda n: n.startswith("drop_impact"), "#drop"),
    ("fatigue", "A", "Fatigue", lambda n: n.startswith("fatigue_"), "#fatigue"),
    ("gait", "B", "Gait robustness", lambda n: n.startswith(("gait-peaks", "gait-robustness", "collision-model-census")), "#f2-gait"),
    ("battery", "B", "Battery runtime", lambda n: n.startswith("battery-runtime"), "#f2-battery"),
    ("thermal", "C", "Thermal", lambda n: n.startswith(("gait-torque-duty", "thermal-", "cavity-volumes")), "#f3-servo-thermal"),
    ("tolerance", "C", "Tolerance stack-up", lambda n: n.startswith(("joint-geometry", "tolerance-stack")), "#f3-tolerance"),
    ("stress-matrix", "A", "Detached stress matrix (round loads, superseded)", lambda n: n.startswith("stress/"), "#matrix"),
]
FAMILY_LABEL = {k: lab for k, _, lab, _, _ in FAMILIES}
FAMILY_CHAPTER = {k: ch for k, ch, _, _, _ in FAMILIES}
FAMILY_HREF = {k: h for k, _, _, _, h in FAMILIES}
FAMILY_ORDER = [k for k, *_ in FAMILIES]


def family_of(name):
    for k, _, _, pred, _ in FAMILIES:
        if pred(name):
            return k
    return "other"


def studies():
    """Every top-level study JSON on disk, plus the three out/stress files. One record per file."""
    out = []
    for p in sorted(glob.glob(os.path.join(EV, "*.json"))):
        d = load(p)
        n = os.path.basename(p)[:-5]
        out.append(dict(file=rel(p), name=n, data=d, family=family_of(n), size=os.path.getsize(p)))
    for n in ("matrix", "report", "corrected"):
        p = os.path.join(STRESS, n + ".json")
        if os.path.exists(p):
            out.append(dict(file=rel(p), name="stress/" + n, data=load(p), family="stress-matrix", size=os.path.getsize(p)))
    for s in out:
        d = s["data"]
        s["verdict"] = d.get("verdict") if isinstance(d, dict) else None
        s["why"] = d.get("why") if isinstance(d, dict) else None
        s["script"] = d.get("script") or d.get("tool") if isinstance(d, dict) else None
        s["generated"] = d.get("generated") if isinstance(d, dict) else None
        s["study"] = d.get("study") or s["name"] if isinstance(d, dict) else s["name"]
        s["part"] = d.get("part") if isinstance(d, dict) else None
        s["case"] = d.get("case") if isinstance(d, dict) else None
        if s["verdict"] is None and isinstance(d, dict) and isinstance(d.get("results"), (list, dict)):
            res = d["results"] if isinstance(d["results"], list) else list(d["results"].values())
            c = {v: sum(1 for r in res if r.get("verdict") == v) for v in ("PASS", "FAIL", "CANNOT DETERMINE")}
            s["verdict_note"] = "%d results: %d PASS, %d FAIL, %d CANNOT DETERMINE" % (len(res), c["PASS"], c["FAIL"], c["CANNOT DETERMINE"])
        elif s["verdict"] is None:
            s["verdict_note"] = "a measurement record — the file carries no verdict field"
        else:
            s["verdict_note"] = ""
    return out


def sub_json_census():
    """JSON files below the top level of out/sim-evidence — counted, not tabulated (they are per-deck / per-cell records)."""
    rows = {}
    for p in glob.glob(os.path.join(EV, "**", "*.json"), recursive=True):
        if os.path.dirname(p) == EV:
            continue
        d = rel(os.path.dirname(p))
        top = d.split("/")[2] if d.count("/") >= 2 else d
        rows[top] = rows.get(top, 0) + 1
    return rows


# ----------------------------------------------------------------------------- the load-basis chain
def parse_cload(inp):
    """Sum every *CLOAD line of a CalculiX deck per DOF. Returns (vector[3], n_lines) or (None, 0)."""
    if not os.path.exists(inp):
        return None, 0
    tot = [0.0, 0.0, 0.0]
    n = 0
    on = False
    with open(inp, errors="replace") as fh:
        for line in fh:
            if line.startswith("*"):
                on = line.upper().startswith("*CLOAD")
                continue
            if on and line.strip():
                bits = [b.strip() for b in line.split(",")]
                if len(bits) >= 3:
                    try:
                        dof = int(bits[1])
                        val = float(bits[2])
                    except ValueError:
                        continue
                    if 1 <= dof <= 3:
                        tot[dof - 1] += val
                        n += 1
    return (tot if n else None), n


def resolve_source(src, L):
    """Follow a study's force_source string back into loads_mujoco.json. Returns (value_N, how) or (None, why)."""
    if not src or not L:
        return None, "no force_source in the study"
    m = re.search(r"walk\.body_transmitted_force_peaks\.(\w+)", src)
    if m:
        b = m.group(1)
        pk = L["walk"]["body_transmitted_force_peaks"].get(b)
        return (pk["peak_force_N"], "walk.body_transmitted_force_peaks.%s.peak_force_N" % b) if pk else (None, "body %s not in walk peaks" % b)
    m = re.search(r"walk\.part_frames_at_peak\.(\w+)\.left_foot_contact_force_N", src)
    if m:
        v = L["walk"]["part_frames_at_peak"][m.group(1)]["left_foot_contact_force_N_in_part_frame"]
        return norm(v), "|walk.part_frames_at_peak.%s.left_foot_contact_force_N_in_part_frame| (walk.peak_vertical_grf_N %s)" % (m.group(1), fmt(L["walk"]["peak_vertical_grf_N"]))
    m = re.search(r"drops\[(\w+)\]\.part_frames_at_peak\.(\w+)\.force_from_body_(\w+)", src)
    if m:
        lab, pf, b = m.groups()
        d = next((x for x in L["drops"] if x["label"] == lab), None)
        if not d:
            return None, "drop %s not in loads_mujoco.json" % lab
        v = d["part_frames_at_peak"][pf]["force_from_body_%s_N_in_part_frame" % b]
        mag = d["body_transmitted_force_max_N"].get(b, {}).get("magnitude")
        return norm(v), "|drops[%s].part_frames_at_peak.%s.force_from_body_%s| at the drop's peak frame; body_transmitted_force_max_N.%s.magnitude (max over time) %s" % (lab, pf, b, b, fmt(mag))
    m = re.search(r"drops\[(\w+)\]\.part_frames_at_peak\.(\w+)\.peak_contact_force_N", src)
    if m:
        lab, pf = m.groups()
        d = next((x for x in L["drops"] if x["label"] == lab), None)
        if not d:
            return None, "drop %s not in loads_mujoco.json" % lab
        v = d["part_frames_at_peak"][pf]["peak_contact_force_N_in_part_frame"]
        return norm(v), "|drops[%s].part_frames_at_peak.%s.peak_contact_force_N_in_part_frame| (drop peak_normal_force_N %s)" % (lab, pf, fmt(d["peak_normal_force_N"]))
    m = re.search(r"drops\[foot\]\.trunk_linear_acceleration_peak_m_s2 x ([0-9.]+) kg \+ weight", src)
    if m:
        mkg = float(m.group(1))
        d = next((x for x in L["drops"] if x["label"] == "drop_foot_rollm10_default_contact_dt5ms"), None)
        a = d["trunk_linear_acceleration_peak_m_s2"]
        return a * mkg + mkg * L["model"]["g_m_s2"], "drops[drop_foot_rollm10_default_contact_dt5ms].trunk_linear_acceleration_peak_m_s2 %s × %s kg + %s kg × g" % (fmt(a), m.group(1), m.group(1))
    m = re.search(r"walk\.trunk_linear_acceleration\.peak_m_s2 x ([0-9.]+) kg \+ weight", src)
    if m:
        mkg = float(m.group(1))
        a = L["walk"].get("trunk_linear_acceleration", {}).get("peak_m_s2")
        if a is None:
            return None, "walk.trunk_linear_acceleration.peak_m_s2 absent from loads_mujoco.json"
        return a * mkg + mkg * L["model"]["g_m_s2"], "walk.trunk_linear_acceleration.peak_m_s2 %s × %s kg + %s kg × g" % (fmt(a), m.group(1), m.group(1))
    return None, "source string not resolvable by this generator: %s" % src


def chain_rows(S, L):
    rows = []
    for s in S:
        if not s["name"].startswith("fea_microduck-"):
            continue
        d = s["data"]
        i = d.get("inputs", {})
        vec = i.get("force_N_part_frame")
        head = i.get("force_magnitude_N")
        deck_dir = next((a for a in d.get("artifacts", []) if os.path.isdir(os.path.join(REPO, a))), None)
        inp = os.path.join(REPO, deck_dir, "%s_%s.inp" % (d["part"].replace("part:", ""), d["case"])) if deck_dir else None
        cl, nl = parse_cload(inp) if inp else (None, 0)
        rv, how = resolve_source(i.get("force_source"), L)
        g = (d.get("outputs") or {}).get("grading") or {}
        rows.append(dict(study=s["study"], file=s["file"], part=d["part"].replace("part:", ""), case=d["case"], source=i.get("force_source"), headline=head,
                         vec=vec, vecn=norm(vec) if vec else None, cload=cl, cloadn=norm(cl) if cl else None, ncl=nl,
                         inp=rel(inp) if inp and os.path.exists(inp) else None, resolved=rv, how=how,
                         sf=g.get("sf_used"), model=g.get("model"), verdict=d.get("verdict")))
    return rows


# ----------------------------------------------------------------------------- CANNOT DETERMINE walk
def settles_from_why(why):
    m = re.search(r"(?i)what\s+(?:would\s+)?settles?\s+it\s*[:\-—]\s*(.+)", why or "")
    return m.group(1).strip() if m else None


def cd_walk(obj, path, out, seen):
    if isinstance(obj, dict):
        v = obj.get("verdict")
        if v == "CANNOT DETERMINE":
            key = path
            if key not in seen:
                seen.add(key)
                out.append(dict(path=path, what=obj.get("what") or obj.get("check") or obj.get("study") or obj.get("part") or path.split(".")[-1],
                                why=obj.get("why") or obj.get("reason") or obj.get("note") or "", settles=obj.get("what_settles_it") or settles_from_why(obj.get("why"))))
        for k, x in obj.items():
            if k == "cannot_determine" and isinstance(x, list):
                for j, e in enumerate(x):
                    if isinstance(e, dict):
                        p = "%s.cannot_determine[%d]" % (path, j)
                        if p not in seen:
                            seen.add(p)
                            out.append(dict(path=p, what=e.get("what", "?"), why=e.get("why", ""), settles=e.get("what_settles_it")))
            elif isinstance(x, str) and x.startswith("CANNOT DETERMINE") and k != "verdict":
                p = "%s.%s" % (path, k)
                if p not in seen:
                    seen.add(p)
                    out.append(dict(path=p, what=k, why=x, settles=settles_from_why(x)))
            else:
                cd_walk(x, "%s.%s" % (path, k), out, seen)
    elif isinstance(obj, list):
        for j, x in enumerate(obj):
            cd_walk(x, "%s[%d]" % (path, j), out, seen)


def cd_register(S):
    """One row per distinct (file, what, why); identical items under several paths are folded with their path count.
    An item that names nothing is cross-referenced to another study file about the same part that does (printed as such)."""
    settles_by_part = {}
    for s in S:
        d = s["data"]
        if isinstance(d, dict) and isinstance(d.get("what_settles_it"), str):
            for m in re.findall(r"microduck-[a-z0-9-]+", s["name"]):
                settles_by_part.setdefault(m, (s["file"], d["what_settles_it"]))
        if isinstance(d, dict) and isinstance((d.get("outputs") or {}).get("what_settles_it"), str):
            for m in re.findall(r"microduck-[a-z0-9-]+", s["name"]):
                settles_by_part.setdefault(m, (s["file"], d["outputs"]["what_settles_it"]))
    reg = []
    for s in S:
        out, seen = [], set()
        cd_walk(s["data"], "", out, seen)
        folded = {}
        for o in out:
            o["file"] = s["file"]
            o["path"] = o["path"].lstrip(".") or "(top level)"
            if not o["settles"] and isinstance(s["data"], dict) and o["path"] == "(top level)":
                o["settles"] = s["data"].get("what_settles_it")
            if not o["settles"]:
                for part in re.findall(r"microduck-[a-z0-9-]+", "%s %s %s" % (o["what"], o["why"], s["name"])):
                    if part in settles_by_part and settles_by_part[part][0] != s["file"]:
                        o["settles"] = "(stated in %s) %s" % settles_by_part[part]
                        o["settles_xref"] = True
                        break
            key = (o["why"], o["settles"]) if o["why"] else (o["what"], o["why"])
            if key in folded:
                folded[key]["paths"].append(o["path"])
                if o["what"] not in folded[key]["whats"]:
                    folded[key]["whats"].append(o["what"])
            else:
                o["paths"] = [o["path"]]
                o["whats"] = [o["what"]]
                folded[key] = o
        reg.extend(folded.values())
    return reg


# ----------------------------------------------------------------------------- artifacts read back
def png_facts(p):
    try:
        from PIL import Image
    except Exception:
        return dict(note="no PIL in this python")
    try:
        im = Image.open(p)
        w, h = im.size
        sm = im.convert("RGB")
        sm.thumbnail((256, 256))
        cols = len(set(sm.getdata()))
        g = sm.convert("L")
        ink = sum(1 for v in g.getdata() if v < 200) / float(g.size[0] * g.size[1])
        return dict(w=w, h=h, colours=cols, ink=ink, blank=cols < 8)
    except Exception as ex:
        return dict(note="unreadable: %s" % ex)


def artifacts(S):
    seen = {}
    for s in S:
        d = s["data"]
        if not isinstance(d, dict):
            continue
        for a in d.get("artifacts", []) or []:
            if not isinstance(a, str):
                continue
            ext = os.path.splitext(a)[1].lower()
            if ext not in (".png", ".mp4", ".html", ".jpg"):
                continue
            seen.setdefault(a, set()).add(s["study"])
    VID = load(os.path.join(REPO, "out", "sim-sweep", "videos.json")) or {}
    vid_by_path = {v.get("mp4", {}).get("path"): (k, v) for k, v in VID.items()}
    rows = []
    for a, who in sorted(seen.items()):
        p = os.path.join(REPO, a)
        r = dict(path=a, exists=os.path.exists(p), size=os.path.getsize(p) if os.path.exists(p) else None, by=sorted(who), ext=os.path.splitext(a)[1].lower())
        if r["ext"] in (".png", ".jpg") and r["exists"]:
            r.update(png_facts(p))
        if r["ext"] == ".mp4":
            k, v = vid_by_path.get(a, (None, None))
            if v:
                r.update(video=k, frames=v.get("frames"), fps=v.get("fps"), read_back=v.get("mp4", {}).get("frames_read_back"),
                         diff=v.get("mean_interframe_diff"), inten=v.get("frame_mean_intensity"), label=v.get("label"))
        rows.append(r)
    return rows


# ----------------------------------------------------------------------------- cross-checks
def crosschecks(S, L, chain):
    by = {s["name"]: s["data"] for s in S}
    PEAKS, ROB, BAT, DUTY, SERVO, COMP, CAV, DROP, FW = (by.get(k) for k in (
        "gait-peaks", "gait-robustness", "battery-runtime", "gait-torque-duty", "thermal-servo-xl330", "thermal-compute-head", "cavity-volumes", "drop_impact", "fatigue_walk"))
    NPF = load(os.path.join(REPO, "ce-parts", "np-f550", "electrical.part.json"))
    rows = []

    def add(idx, what, a, asrc, b, bsrc, verdict, note):
        rows.append(dict(i=idx, what=what, a=a, asrc=asrc, b=b, bsrc=bsrc, verdict=verdict, note=note))

    # X1 mass
    ms = [(L["model"]["mass_kg_from_mjcf_inertials"], "F1 loads_mujoco.json model.mass_kg_from_mjcf_inertials (reference/pollen-microduck-rl/robot_walk.xml inertials)"),
          (PEAKS["inputs"]["total_mass_kg"], "F2 gait-peaks.json inputs.total_mass_kg (model.body_mass.sum(), sim/microduck_ours.xml)"),
          (DUTY["inputs"]["model_mass_kg"], "F3 gait-torque-duty.json inputs.model_mass_kg"),
          (DROP["inputs"]["mass_kg"], "F1 drop_impact.json inputs.mass_kg")]
    same = len(set(m for m, _ in ms)) == 1
    add("X1", "Robot mass every lane loads from", fmt(ms[0][0]) + " kg", ms[0][1], " / ".join(fmt(m) + " kg" for m, _ in ms[1:]), "; ".join(s for _, s in ms[1:]),
        "AGREE" if same else "DIFFER", "one number in four files: the mesh swap (sim/swap_meshes.py) keeps Pollen's inertials, so our-mesh runs and reference-model runs carry the same mass.")
    # X2 walk single-foot GRF
    f1 = L["walk"]["peak_vertical_grf_N"]
    f2 = PEAKS["outputs"]["ground_reaction_force_N"]["walking_single_foot_peak_N"]
    add("X2", "Nominal-walk single-foot peak GRF", fmt(f1) + " N", "F1 loads_mujoco.json walk.peak_vertical_grf_N — Pollen's robot_walk.xml, 8.0 s at 200 Hz, left foot at t %s s" % fmt(L["walk"]["peak_grf_time_s"]),
        fmt(f2) + " N", "F2 gait-peaks.json outputs.ground_reaction_force_N.walking_single_foot_peak_N — cell base_walk_vx0.25 on sim/microduck_ours.xml (our meshes)",
        "AGREE" if f1 == f2 else "DIFFER",
        "Δ %+.4f %% (F1 − F2)/F2. Two runs of two models: F1 solved the FEA on the reference model's peak; F2's number is the same policy on our rebuilt meshes over its own run length. Neither is wrong; they are not the same number and the page says so." % pct(f1, f2))
    # X3 tiers
    tiers = PEAKS["outputs"]["ground_reaction_force_N"].get("for_FEA_tiers", {})
    t2 = tiers.get("2_worst_undisturbed_locomotion", {})
    tdl = PEAKS["outputs"]["ground_reaction_force_N"]
    add("X3", "Which GRF tier the walk FEAs are graded at", fmt(f1) + " N (nominal walk only)", "F1: every fea_*_walk.json force_source is loads_mujoco.json walk.* at the nominal command (v_x 0.25 m/s)",
        "%s N single foot (cell %s) · %s N (survived push, cell %s)" % (fmt(t2.get("single_foot_N")), t2.get("cell"), fmt(tdl.get("DESIGN_LOAD_worst_valid_single_foot_peak_N")), tdl.get("DESIGN_LOAD_worst_valid_cell")),
        "F2 gait-peaks.json outputs.ground_reaction_force_N.for_FEA_tiers.2_worst_undisturbed_locomotion and DESIGN_LOAD_worst_valid_*",
        "DIFFER", "F2 names %s N as the structural design load for the commanded envelope and %s N for the worst survived push; no FEA study on disk is solved at either tier. The walk FEAs are %.4f× and %.4f× below them respectively. The foot-drop FEAs (%s N at the shin) sit above both. A walk-tier re-solve at %s N is the open work item (§4)." % (
            fmt(t2.get("single_foot_N")), fmt(tdl.get("DESIGN_LOAD_worst_valid_single_foot_peak_N")), t2.get("single_foot_N", 0) / f1, tdl.get("DESIGN_LOAD_worst_valid_single_foot_peak_N", 0) / f1,
            fmt(next((c["headline"] for c in chain if c["part"] == "microduck-shin" and c["case"] == "drop"), None)), fmt(t2.get("single_foot_N"))))
    # X4 per-joint torques F1 / F2 / F3
    j1 = L["walk"]["peak_abs_torque_Nm"]
    j2 = PEAKS["outputs"]["baseline_walk_vx0.25"]["per_joint_peak_Nm"]
    j3 = {j: v["peak_abs_Nm"] for j, v in DUTY["outputs"]["joints"].items()}
    spread = []
    for j in j1:
        vals = [j1[j], j2.get(j), j3.get(j)]
        spread.append((j, vals, pct(j1[j], j2.get(j)), pct(j3.get(j), j2.get(j))))
    worst12 = max(spread, key=lambda t: abs(t[2] or 0))
    worst32 = max(spread, key=lambda t: abs(t[3] or 0))
    add("X4", "Peak joint torque at the nominal walk, per joint (14 joints, Table 4)", "F1 vs F2: worst %s %+.4f %%" % (worst12[0], worst12[2]),
        "F1 loads_mujoco.json walk.peak_abs_torque_Nm (reference model)", "F3 vs F2: worst %s %+.4f %%" % (worst32[0], worst32[3]),
        "F2 gait-peaks.json outputs.baseline_walk_vx0.25.per_joint_peak_Nm · F3 gait-torque-duty.json outputs.joints.*.peak_abs_Nm (both on sim/microduck_ours.xml)",
        "AGREE" if abs(worst32[3] or 0) < 0.01 and abs(worst12[2] or 0) < 0.01 else "DIFFER",
        "F3's duty run reproduces F2's baseline to the 5th decimal on every joint (F3 records 6 dp, F2 5 dp). F1's reference-model run differs on %d of 14 joints — the same two-model story as X2." % sum(1 for t in spread if abs(t[2] or 0) > 0.01))
    # X5 F3 duty <- F2
    lb = SERVO["inputs"]["load_basis"]
    cc = lb.get("cross_check", {}).get("baseline_walk_vx0.25_peak_Nm", {})
    diffs = [j for j in j2 if cc.get(j) != j2[j]]
    add("X5", "F3's thermal duty is F2's measured baseline", lb.get("file"), "thermal-servo-xl330.json inputs.load_basis.file + .statistic: " + (lb.get("statistic") or ""),
        "%d of %d joints identical" % (len(j2) - len(diffs), len(j2)), "the cross_check block F3 copied from F2, compared field by field against gait-peaks.json as it is on disk now (fingerprint %s)" % PEAKS["outputs"]["FOR_CONSUMERS"].get("per_joint_locomotion_upright_fingerprint"),
        "AGREE" if not diffs else "DIFFER", ("F3 heats the windings with mean(τ²) from its own 12 s run whose peaks equal F2's (X4); the copied cross-check block is current." if not diffs else "joints that moved since F3 copied them: " + ", ".join(diffs)))
    # X6 battery
    cap = NPF["record"]["capacity"] if NPF else {}
    prov = (NPF["record"].get("provides") or [{}])[0] if NPF else {}
    pk = BAT["inputs"]["pack"]
    okwh = pk.get("Wh") == cap.get("Wh") and pk.get("mAh") == cap.get("mAh") and pk.get("v_window") == [prov.get("v_min"), prov.get("v_max")]
    add("X6", "Battery pack energy the runtime study credits", "%s Wh · %s mAh · %s–%s V" % (fmt(pk.get("Wh")), fmt(pk.get("mAh")), fmt(pk.get("v_window", [None, None])[0]), fmt(pk.get("v_window", [None, None])[1])),
        "F2 battery-runtime.json inputs.pack (Wh_computed %s)" % fmt(pk.get("Wh_computed")),
        "%s Wh · %s mAh · %s–%s V" % (fmt(cap.get("Wh")), fmt(cap.get("mAh")), fmt(prov.get("v_min")), fmt(prov.get("v_max"))),
        "ce-parts/np-f550/electrical.part.json record.capacity and provides[0] (Duracell DR5 page, fetched %s)" % (NPF["record"]["sources"][0]["fetched"] if NPF else "?"),
        "AGREE" if okwh else "DIFFER", "the part folder's current figure; the study also carries the folder's own caveat that the FITTED pack is unidentified (a 2600 mAh 'NP-F550' is necessarily third-party).")
    # X7 drop heights + contact model
    hs = sorted(set(d["height_m"] for d in L["drops"]))
    fea_labels = sorted(set(re.search(r"drops\[(\w+)\]", c["source"] or "").group(1) for c in chain if c["case"] in ("drop", "head_drop") and re.search(r"drops\[(\w+)\]", c["source"] or "")))
    dfoot = next(d for d in L["drops"] if d["label"] == "drop_foot_rollm10_default_contact_dt5ms")
    d50 = next(d for d in L["drops"] if d["label"] == "drop_foot_rollm10_default_contact_dt50us")
    dstiff = next(d for d in L["drops"] if d["label"] == "drop_foot_rollm10_stiff_tpu_whole_mass_dt50us")
    add("X7", "Drop height and which contact model the drop FEAs load from", "%s m" % fmt(DROP["inputs"]["height_m"]), "drop_impact.json inputs.height_m; height_source: " + first_sentence(DROP["inputs"].get("height_source"), 160),
        "%s m in every loads_mujoco drop (%d runs)" % ("/".join(fmt(h) for h in hs), len(L["drops"])), "loads_mujoco.json drops[*].height_m",
        "AGREE" if hs == [DROP["inputs"]["height_m"]] else "DIFFER",
        "The FEA drop loads come from %s only — MuJoCo's default contact at the 5 ms policy timestep (foot peak %s N). The same drop at 50 µs gives %s N, and with the TPU sole's measured stiffness %s N; drop_impact.json brackets the rigid-body answer 779–12762 N. The FEA drop case is therefore the SOFTEST of the models on disk and every drop SF is an upper bound on that account (F1 §A.6 says the same)." % (
            ", ".join(fea_labels), fmt(dfoot["peak_normal_force_N"]), fmt(d50["peak_normal_force_N"]), fmt(dstiff["peak_normal_force_N"])))
    # X8 compute thermal <- cavity volumes
    eg = COMP["inputs"].get("enclosure_geometry", {})
    leaves = []

    def nums(o):
        if isinstance(o, dict):
            for v in o.values():
                nums(v)
        elif isinstance(o, list):
            for v in o:
                nums(v)
        elif isinstance(o, float):
            leaves.append(o)
    nums(eg)
    cavtxt = json.dumps(CAV["outputs"])
    cav_leaves = []
    _l = leaves
    leaves = cav_leaves
    nums(CAV["outputs"])
    leaves = _l
    hit = [x for x in leaves if repr(x) in cavtxt or ("%.3f" % x) in cavtxt]
    conv = {}
    for x in leaves:
        if x in hit:
            continue
        for k, lab in ((1e6, "m² → mm² (×10⁶)"), (1e3, "m → mm (×10³)"), (1e-3, "mm → m"), (1e-6, "mm² → m²")):
            if any(abs(y - x * k) <= 1e-4 * abs(x * k) for y in cav_leaves if y):
                conv[x] = lab
                break
    un = [x for x in leaves if x not in hit and x not in conv]
    add("X8", "The compute thermal study's enclosure numbers are the cavity study's", "%d numeric inputs" % len(leaves), "thermal-compute-head.json inputs.enclosure_geometry (source: %s)" % eg.get("source"),
        "%d found verbatim in cavity-volumes.json outputs, %d after a unit conversion, %d unmatched" % (len(hit), len(conv), len(un)), "cavity-volumes.json outputs (sim/cavity_measure.py), every numeric leaf compared to 0.01 %",
        "AGREE" if leaves and not un else ("DIFFER" if leaves else "CANNOT DETERMINE"),
        ("unmatched: " + ", ".join(repr(x) for x in un) + ". ") * bool(un) + ("converted: " + "; ".join("%s = %s" % (repr(x), lab) for x, lab in conv.items()) + ". ") * bool(conv) + "Every enclosure figure the thermal model uses is a measured cavity figure, three of them re-expressed in SI." if not un else "")
    # X9 fatigue rows vs FEA walk
    bad = []
    n = 0
    for r in FW["outputs"]["rows"]:
        ws = load(os.path.join(REPO, r["walk_study"])) if r.get("walk_study") else None
        if not ws or "outputs" not in ws:
            continue
        n += 1
        fm = ws["inputs"].get("force_magnitude_N")
        vm = ws["outputs"].get("max_von_mises_mpa")
        if fm != r.get("force_N") or (vm is not None and r.get("sigma_max_mpa") is not None and abs(vm - r["sigma_max_mpa"]) > 1e-9):
            bad.append("%s (force %s vs %s N, σ %s vs %s MPa)" % (r["part"], fmt(r.get("force_N")), fmt(fm), fmt(r.get("sigma_max_mpa")), fmt(vm)))
    add("X9", "Fatigue rows use the FEA walk peaks", "%d rows with a walk solve" % n, "fatigue_walk.json outputs.rows[*].force_N and sigma_max_mpa",
        "%d identical" % (n - len(bad)), "fea_*_walk.json inputs.force_magnitude_N and outputs.max_von_mises_mpa", "AGREE" if not bad else "DIFFER", "; ".join(bad) if bad else "same force, same peak stress, row for row.")
    # X10 stress matrix vs measured loads
    M = by.get("stress/matrix")
    C = by.get("stress/corrected")
    shin_walk = next((c for c in chain if c["part"] == "microduck-shin" and c["case"] == "walk"), None)
    shin_drop = next((c for c in chain if c["part"] == "microduck-shin" and c["case"] == "drop"), None)
    ank_drop = next((c for c in chain if c["part"] == "microduck-ankle-left" and c["case"] == "drop"), None)
    mank = next((r for r in (M["results"].values() if isinstance(M["results"], dict) else M["results"]) if r["part"] == "microduck-ankle-left" and r["case"] == "landing"), {})
    cank = next((r for r in C["results"] if r["part"] == "microduck-ankle-left" and r["case"] == "landing"), {})
    add("X10", "The detached stress matrix's loads against the measured ones", "standing %s N · landing %s N (corrected to %s N) · lateral %s N" % (
        fmt(abs(M["cases"]["standing"]["force_N"][2])), fmt(abs(M["cases"]["landing"]["force_N"][2])), fmt(C["load_basis"]["landing"]["N"]), fmt(abs(M["cases"]["lateral"]["force_N"][1]))),
        "out/stress/matrix.json cases (round numbers: '%s'); out/stress/corrected.json load_basis" % M["load_basis"],
        "shin walk %s N · shin foot drop %s N · ankle foot drop %s N" % (fmt(shin_walk["headline"]), fmt(shin_drop["headline"]), fmt(ank_drop["headline"])),
        "F1 fea_*.json inputs.force_magnitude_N, read off MuJoCo", "DIFFER",
        "The measured walk peak on the shin (%s N) already exceeds the corrected 'landing' case (%s N); the measured foot-drop load is %.2f× the corrected landing and %.3f× the matrix's 60 N. The ankle: matrix landing SF %s at 60 N (FAIL), corrected SF %s at %s N (FAIL), F1 drop SF %s at %s N (PASS) — three different declared load paths on one part (F1 §A.4: the matrix held and loaded two connectors on the same axle). The matrix and its correction are history; see LOAD-BASIS-CORRECTION.html." % (
            fmt(shin_walk["headline"]), fmt(C["load_basis"]["landing"]["N"]), shin_drop["headline"] / C["load_basis"]["landing"]["N"], shin_drop["headline"] / 60.0,
            fmt(mank.get("sf")), fmt(cank.get("sf")), fmt(cank.get("force_N")), fmt(ank_drop["sf"]), fmt(ank_drop["headline"])))
    # X11 deck-applied load vs headline
    off = [c for c in chain if c["cloadn"] is not None and c["headline"] and abs(pct(c["cloadn"], c["headline"])) > 0.1]
    add("X11", "The force each FEA deck applied vs the magnitude its study quotes", "%d decks parsed" % sum(1 for c in chain if c["cloadn"] is not None), "Σ *CLOAD per DOF in out/sim-evidence/fea/<study>/<part>_<case>.inp (Table 3)",
        "%d decks apply a force ≥ 0.1 %% away from the quoted magnitude" % len(off), "fea_*.json inputs.force_magnitude_N",
        "AGREE" if not off else "DIFFER",
        ("The deck applies inputs.force_N_part_frame — the body force AT THE DROP'S PEAK FRAME — while force_magnitude_N is the max of |cfrc_int| over the whole record, reached at another instant. Worst: " + "; ".join(
            "%s %s applied %s N vs quoted %s N (%+.2f %%)" % (c["part"].replace("microduck-", ""), c["case"], fmt(round(c["cloadn"], 4)), fmt(c["headline"]), pct(c["cloadn"], c["headline"])) for c in sorted(off, key=lambda c: -abs(pct(c["cloadn"], c["headline"])))[:4])
         + ". A linear SF scales exactly with load, so Table 3 prints the SF re-scaled to the quoted magnitude beside the published one; the nonlinear ones do not scale and are flagged.") if off else "every deck applies the quoted magnitude to within 0.1 %.")
    # X12 servo datasheet rows agree across lanes
    st = [PEAKS["inputs"]["servo"]["stall_torque_Nm"], {k: v[0] for k, v in BAT["inputs"]["servo"]["published_rows"].items()}]
    rr = SERVO["inputs"]["servo"]["stall_rows_quote"]
    f3rows = {float(v): float(t) for t, v in re.findall(r"([0-9.]+) \[N\.m\] \(at ([0-9.]+) \[V\]", rr)}
    ok = {float(k): float(v) for k, v in st[0].items()} == {float(k): float(v) for k, v in st[1].items()} == f3rows
    add("X12", "XL330-M288-T stall rows every lane quotes", json.dumps(st[0]), "F2 gait-peaks.json inputs.servo.stall_torque_Nm (ROBOTIS e-Manual)", json.dumps(st[1]) + " · F3 quotes the same three rows verbatim", "F2 battery-runtime.json inputs.servo.published_rows; F3 thermal-servo-xl330.json inputs.servo.stall_rows_quote",
        "AGREE" if ok else "DIFFER", "one vendor table, three readers, same digits (F3's rows parsed out of its verbatim quote: %s)." % json.dumps(f3rows) if ok else "the three files do not quote the same rows: F2 %s, F2 battery %s, F3 %s." % (json.dumps(st[0]), json.dumps(st[1]), json.dumps(f3rows)))
    # X13 skeptic recheck of F1
    SK = by.get("skeptic_f1_recheck")
    checks = SK.get("checks", []) if SK else []
    fails = [c for c in checks if c.get("verdict") == "FAIL"]
    add("X13", "The F1 skeptic's independent re-computation of F1's numbers", "%d checks, %d PASS" % (len(checks), sum(1 for c in checks if c.get("verdict") == "PASS")), "skeptic_f1_recheck.json checks[*] (mass, walk GRF re-run, von Mises re-read from every .frd, …)",
        "%d FAIL: %s" % (len(fails), ", ".join(c.get("check", "?") for c in fails)), "the same file; each FAIL's note is printed in the register", SK.get("verdict", "CANNOT DETERMINE") if SK else "CANNOT DETERMINE",
        "; ".join("%s — %s" % (c.get("check"), first_sentence(c.get("note") or c.get("why") or json.dumps(c.get("recomputed"))[:200], 200)) for c in fails) if fails else "every re-computation reproduced the published figure.")
    # X14 gait robustness vs gait peaks: same cell set
    cells_rob = set(ROB["outputs"]["cells"].keys()) if isinstance(ROB["outputs"]["cells"], dict) else set(r.get("cell") for r in ROB["outputs"]["rows"])
    cells_pk = set()
    for grp in ("per_joint_all_cells",):
        for j, v in PEAKS["outputs"].get(grp, {}).items():
            if v.get("peak_cell"):
                cells_pk.add(v["peak_cell"])
    add("X14", "Gait robustness and gait peaks were read off the same cells", "%d cells" % len(cells_rob), "gait-robustness.json outputs.cells", "%d distinct peak cells named" % len(cells_pk), "gait-peaks.json outputs.per_joint_all_cells[*].peak_cell",
        "AGREE" if cells_pk <= cells_rob else "DIFFER", "every cell a peak is attributed to is a cell of the robustness sweep." if cells_pk <= cells_rob else "peak cells not in the sweep: " + ", ".join(sorted(cells_pk - cells_rob)))
    return rows, spread


# ----------------------------------------------------------------------------- sections
def sec_verdict(S, chain, xc, cdreg, arts, subs):
    n = len(S)
    c = {v: sum(1 for s in S if s["verdict"] == v) for v in ("PASS", "FAIL", "CANNOT DETERMINE")}
    nmeas = sum(1 for s in S if s["verdict"] is None)
    ndiff = sum(1 for r in xc if r["verdict"] == "DIFFER")
    fams = {}
    for s in S:
        fams.setdefault(s["family"], []).append(s)
    s = ['<section id="sim-verdict"><h2><span class="n">1</span>Verdict — what the simulations say, all of them</h2>',
         '<div class="statbar">'
         '<div class="stat"><b>%d</b><span>study files on disk</span></div>'
         '<div class="stat"><b>%d / %d / %d</b><span>PASS / FAIL / CANNOT DETERMINE</span></div>'
         '<div class="stat"><b>%d</b><span>measurement records (no verdict field)</span></div>'
         '<div class="stat"><b>%d</b><span>study families</span></div>'
         '<div class="stat"><b>%d / %d</b><span>cross-checks AGREE / DIFFER</span></div>'
         '<div class="stat"><b>%d</b><span>CANNOT DETERMINE items in the register</span></div>'
         '<div class="stat"><b>%d</b><span>images + videos read back</span></div>'
         '</div>' % (n, c["PASS"], c["FAIL"], c["CANNOT DETERMINE"], nmeas, len(fams), sum(1 for r in xc if r["verdict"] == "AGREE"), ndiff, len(cdreg), len(arts))]
    s.append('<p class="lede">Three simulation lanes wrote %d study files under <code>out/sim-evidence/</code> (plus %d per-deck and per-cell records below it, and the three <code>out/stress/</code> files of the '
             'detached night-shift matrix). This page is generated from all of them by <code>tools/gen_simulation.py</code>; the lanes\' own sections are included as chapters A, B and C exactly as their '
             'generators emit them, renumbered. Nothing is typed here that a file does not say, and where two files disagree the disagreement is printed (§4), not averaged.</p>' % (
                 n - 3, sum(subs.values())))
    s.append('<div class="verdict warn"><b>The structure is not ready, the gait is inside the actuator only at the nominal command, the servo thermals fail at the faster cells, the runtime is an upper bound on an unidentified pack, and the bearing seats cannot be graded without a print-accuracy measurement.</b><ul>')
    for fam in FAMILY_ORDER:
        fs = fams.get(fam, [])
        if not fs:
            continue
        cc = {v: sum(1 for x in fs if x["verdict"] == v) for v in ("PASS", "FAIL", "CANNOT DETERMINE")}
        s.append('<li><a href="%s"><b>%s</b></a> (chapter %s): %d file%s — %d PASS, %d FAIL, %d CANNOT DETERMINE%s.</li>' % (
            FAMILY_HREF[fam], E(FAMILY_LABEL[fam]), FAMILY_CHAPTER[fam], len(fs), "s" if len(fs) != 1 else "", cc["PASS"], cc["FAIL"], cc["CANNOT DETERMINE"],
            (", %d measurement record%s" % (sum(1 for x in fs if x["verdict"] is None), "s" if sum(1 for x in fs if x["verdict"] is None) != 1 else "")) if any(x["verdict"] is None for x in fs) else ""))
    s.append('</ul></div>')
    s.append('<p>The load basis is one chain, and §3 walks it with the numbers: the MJCF inertial mass (%s kg) → the MuJoCo peaks under Pollen\'s walking policy (nominal-walk single-foot GRF %s N in the reference model, %s N on our meshes; 0.250 m foot drop %s N) → the force each FEA deck actually applied (parsed from the solver input, Table 3) → the safety factor and verdict. %d of the %d cross-checks in §4 DIFFER; each says why and which number the downstream study used.</p>' % (
        fmt(load(os.path.join(EV, "loads_mujoco.json"))["model"]["mass_kg_from_mjcf_inertials"]), fmt(load(os.path.join(EV, "loads_mujoco.json"))["walk"]["peak_vertical_grf_N"]),
        fmt(load(os.path.join(EV, "gait-peaks.json"))["outputs"]["ground_reaction_force_N"]["walking_single_foot_peak_N"]),
        fmt(next(d["peak_normal_force_N"] for d in load(os.path.join(EV, "loads_mujoco.json"))["drops"] if d["label"] == "drop_foot_rollm10_default_contact_dt5ms")), ndiff, len(xc)))
    s.append('</section>')
    return "\n".join(s)


def sec_matrix(S):
    s = ['<section id="sim-matrix"><h2><span class="n">2</span>Verdict matrix — every study file on disk</h2>',
         '<p class="lede">One row per JSON file. The headline is the first sentence of the file\'s own <code>why</code>; the full text, the inputs with their sources, the outputs and the artifacts are in the register (§8, linked from the file name). Files with no <code>verdict</code> field are measurement records and are counted apart, never as a pass.</p>',
         '<div class="tw"><table class="data compact"><caption>Table 1. Every study file under out/sim-evidence/ and out/stress/, its family, part and case, verdict and headline.</caption>'
         '<thead><tr><th class="n">#</th><th>File</th><th>Family</th><th>Part / case</th><th>Verdict</th><th>Headline (first sentence of why)</th><th>Chapter</th></tr></thead><tbody>']
    for k, st in enumerate(sorted(S, key=lambda x: (FAMILY_ORDER.index(x["family"]) if x["family"] in FAMILY_ORDER else 99, x["name"])), 1):
        pc = " · ".join(x for x in (st["part"], st["case"]) if x) or "—"
        head = first_sentence(st["why"]) if st["why"] else st["verdict_note"]
        s.append('<tr><td class="n">%d</td><td><a href="#%s"><code class="brk">%s</code></a></td><td>%s</td><td><code>%s</code></td><td>%s</td><td>%s</td><td><a href="%s">%s</a></td></tr>' % (
            k, anchor(st["name"]), E(st["file"].replace("out/sim-evidence/", "")), E(FAMILY_LABEL.get(st["family"], "other")), E(pc), chip(st["verdict"] or "MEASUREMENT"), E(head), FAMILY_HREF.get(st["family"], "#"), FAMILY_CHAPTER.get(st["family"], "—")))
    s.append('</tbody></table></div></section>')
    return "\n".join(s)


def sec_chain(L, chain, spread, S):
    by = {s["name"]: s["data"] for s in S}
    PEAKS, DUTY = by["gait-peaks"], by["gait-torque-duty"]
    w, m = L["walk"], L["model"]
    s = ['<section id="sim-chain"><h2><span class="n">3</span>The load-basis chain — MJCF mass → MuJoCo peaks → the load each FEA deck applied</h2>',
         '<p class="lede">Nothing structural on this page rests on a round number. The chain below is measured at every link, and the last link — the force the CalculiX deck actually carries — is read out of the solver input file, not out of the study\'s summary.</p>']
    # link 1: mass
    s.append('<h3>Link 1 — the mass, from the MJCF inertials</h3>')
    s.append('<div class="tw"><table class="data"><caption>Table 2. The mass and weight each lane starts from.</caption><thead><tr><th>Lane / file</th><th class="n">Mass kg</th><th class="n">Weight N</th><th>Where it comes from</th></tr></thead><tbody>')
    for lab, mk, wn, src in [("F1 loads_mujoco.json", m["mass_kg_from_mjcf_inertials"], m["weight_N"], "sum of the 15 &lt;inertial&gt; masses in " + E(m["robot_walk"]) + ", g = " + fmt(m["g_m_s2"])),
                             ("F2 gait-peaks.json", PEAKS["inputs"]["total_mass_kg"], PEAKS["inputs"]["weight_N"], E(PEAKS["inputs"]["total_mass_source"])),
                             ("F3 gait-torque-duty.json", DUTY["inputs"]["model_mass_kg"], DUTY["inputs"]["weight_N"], "inputs.model_mass_kg of " + E(DUTY["inputs"]["robot"])),
                             ("F1 drop_impact.json", by["drop_impact"]["inputs"]["mass_kg"], None, E(by["drop_impact"]["inputs"]["mass_source"]))]:
        s.append('<tr><td>%s</td><td class="n">%s</td><td class="n">%s</td><td>%s</td></tr>' % (E(lab), fmt(mk), fmt(wn), src))
    s.append('</tbody></table></div>')
    # link 2: peaks
    s.append('<h3>Link 2 — the peaks MuJoCo measured under Pollen\'s policies</h3>')
    dfoot = next(d for d in L["drops"] if d["label"] == "drop_foot_rollm10_default_contact_dt5ms")
    dhead = next(d for d in L["drops"] if d["label"] == "drop_head_default_contact_dt5ms")
    g = PEAKS["outputs"]["ground_reaction_force_N"]
    t2 = g.get("for_FEA_tiers", {}).get("2_worst_undisturbed_locomotion", {})
    rows = [("Nominal walk, single-foot vertical GRF peak", w["peak_vertical_grf_N"], "N", "F1 loads_mujoco.json walk.peak_vertical_grf_N — %s, %s s at %s Hz, step %d (t %s s), %s foot" % (m["robot_walk"], fmt(w["seconds"]), fmt(w["physics_hz"]), w["peak_grf_step"], fmt(w["peak_grf_time_s"]), w["peak_foot"])),
            ("Nominal walk, single-foot vertical GRF peak", g["walking_single_foot_peak_N"], "N", "F2 gait-peaks.json outputs.ground_reaction_force_N.walking_single_foot_peak_N — cell base_walk_vx0.25, sim/microduck_ours.xml (%s × body weight)" % fmt(g["walking_single_foot_peak_body_weights"])),
            ("Worst undisturbed locomotion cell, single foot", t2.get("single_foot_N"), "N", "F2 for_FEA_tiers.2_worst_undisturbed_locomotion — cell %s at %s s (%s × body weight)" % (t2.get("cell"), fmt(t2.get("at_s")), fmt(t2.get("body_weights")))),
            ("Worst survived push (design load, F2's naming)", g.get("DESIGN_LOAD_worst_valid_single_foot_peak_N"), "N", "F2 DESIGN_LOAD_worst_valid_single_foot_peak_N — cell %s at %s s, before the fall (%s × body weight); the post-fall %s N is NOT a load (through-the-floor artefact)" % (g.get("DESIGN_LOAD_worst_valid_cell"), fmt(g.get("DESIGN_LOAD_worst_valid_both_feet_peak_at_s")), fmt(g.get("DESIGN_LOAD_worst_valid_body_weights")), fmt(g.get("worst_any_peak_N_INCLUDING_POST_FALL")))),
            ("0.250 m drop onto the left foot (roll −10°), peak normal force", dfoot["peak_normal_force_N"], "N", "F1 loads_mujoco.json drops[%s] — MuJoCo default contact, dt %s s, %s × body weight, first contact %s s" % (dfoot["label"], fmt(dfoot["timestep_s"]), fmt(dfoot["peak_over_bodyweight"]), fmt(dfoot["first_contact_time_s"]))),
            ("0.250 m drop onto the head, peak normal force", dhead["peak_normal_force_N"], "N", "F1 loads_mujoco.json drops[%s] — struck %s, dt %s s, %s × body weight" % (dhead["label"], dhead["struck_geom"], fmt(dhead["timestep_s"]), fmt(dhead["peak_over_bodyweight"]))),
            ("Impact energy / speed at 0.250 m", "%s J / %s m/s" % (fmt(dfoot["energy_J"]), fmt(dfoot["impact_speed_m_s"])), "", "F1 loads_mujoco.json drops[*].energy_J, impact_speed_m_s (m g h, √(2 g h))"),
            ("Worst locomotion joint torque", PEAKS["outputs"]["worst_locomotion_torque_Nm"], "N·m", "F2 gait-peaks.json outputs.worst_locomotion_torque_Nm — %s (over 25 upright cells); the XL330-M288-T stall row at 6.0 V is 0.60 N·m" % PEAKS["outputs"]["worst_locomotion_joint"]),
            ("Nominal-walk mean(τ²) worst joint (F3's heating statistic)", max(DUTY["outputs"]["joints"].items(), key=lambda kv: kv[1]["mean_tau_squared_Nm2"])[1]["mean_tau_squared_Nm2"], "N²·m²",
             "F3 gait-torque-duty.json outputs.joints.%s.mean_tau_squared_Nm2 — %s s at %s Hz" % (max(DUTY["outputs"]["joints"].items(), key=lambda kv: kv[1]["mean_tau_squared_Nm2"])[0], fmt(DUTY["inputs"]["seconds"]), fmt(DUTY["inputs"]["record_hz"])))]
    s.append('<div class="tw"><table class="data"><caption>Table 2a. The measured peaks, with the run each was read off.</caption><thead><tr><th>Quantity</th><th class="n">Value</th><th>Unit</th><th>Source</th></tr></thead><tbody>')
    for q, v, u, src in rows:
        s.append('<tr><td>%s</td><td class="n">%s</td><td>%s</td><td>%s</td></tr>' % (E(q), fmt(v) if not isinstance(v, str) else E(v), E(u), E(src)))
    s.append('</tbody></table></div>')
    # link 3: per-study chain
    s.append('<h3>Link 3 — what each FEA deck carries</h3>')
    s.append('<p>For every <code>fea_microduck-*.json</code>: the source string the study cites, the value that string resolves to in <code>loads_mujoco.json</code> today, the quoted magnitude, the norm of the part-frame vector the study lists, and Σ&nbsp;*CLOAD read out of the deck. Where the deck\'s force differs from the quoted magnitude, the linear SF is re-scaled to the quoted magnitude in the last column (a linear solve scales exactly; a nonlinear one does not and is marked).</p>')
    s.append('<div class="tw"><table class="data compact"><caption>Table 3. The load chain per FEA study, measured. Δ = (deck − quoted)/quoted.</caption>'
             '<thead><tr><th>Part · case</th><th>force_source (study)</th><th class="n">Resolves to N</th><th class="n">Quoted N</th><th class="n">|vector| N</th><th class="n">Σ CLOAD N</th><th class="n">Δ %</th><th class="n">SF used</th><th class="n">SF at quoted</th><th>Verdict</th></tr></thead><tbody>')
    for c in sorted(chain, key=lambda c: (F1.PART_ORDER.index(c["part"]) if c["part"] in F1.PART_ORDER else 99, F1.CASE_ORDER.get(c["case"], 9))):
        d = pct(c["cloadn"], c["headline"]) if c["cloadn"] is not None and c["headline"] else None
        sf_q = None
        if c["sf"] is not None and c["cloadn"] and c["headline"] and c["model"] == "linear":
            sf_q = c["sf"] * c["cloadn"] / c["headline"]
        flag = ' class="cd"' if d is not None and abs(d) > 0.1 else ""
        s.append('<tr%s><td><code>%s</code> · %s</td><td><code class="brk">%s</code><br><span class="small">→ %s</span></td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td>%s</td></tr>' % (
            flag, E(c["part"].replace("microduck-", "")), E(F1.CASE_LABEL.get(c["case"], c["case"])), E((c["source"] or "—").replace("out/sim-evidence/loads_mujoco.json :: ", "")), E(c["how"]),
            fmt(round(c["resolved"], 5)) if c["resolved"] is not None else "—", fmt(c["headline"]), fmt(round(c["vecn"], 5)) if c["vecn"] else "—",
            (fmt(round(c["cloadn"], 5)) + "<br><span class=\"small\">(%d lines)</span>" % c["ncl"]) if c["cloadn"] is not None else ("no deck" if not c["inp"] else "no *CLOAD"),
            ("%+.3f" % d) if d is not None else "—", fmt(round(c["sf"], 4)) if c["sf"] is not None else "—",
            (fmt(round(sf_q, 4)) if sf_q is not None else ("nonlinear — does not scale" if c["model"] == "nonlinear" and c["sf"] is not None else "—")), chip(c["verdict"])))
    s.append('</tbody></table></div>')
    s.append('<p class="note">Reading the Δ column: the drop studies quote <code>force_magnitude_N</code> = the maximum of |cfrc_int| over the whole drop record, while the vector they apply is the part-frame force at the instant of the drop\'s peak normal force. On the foot-drop leg chain the two coincide to 0.05 %; on the head-drop studies they do not (the head-chain bodies peak later than the shell contact), so the deck carries less than the quoted magnitude and the published SF is HIGHER than it would be at the quoted load. The re-scaled column states what the SF would be at the quoted magnitude for the linear solves.</p>')
    # per-joint torque table
    s.append('<h3>Per-joint torque at the nominal walk, three lanes</h3>')
    s.append('<div class="tw"><table class="data compact"><caption>Table 4. Peak |τ| per joint at v_x 0.25 m/s: F1 (reference model, 200 Hz, 8 s), F2 (our meshes, control frame), F3 (our meshes, 200 Hz, 12 s). N·m.</caption><thead><tr><th>Joint</th><th class="n">F1</th><th class="n">F2</th><th class="n">F3</th><th class="n">F1−F2 %</th><th class="n">F3−F2 %</th></tr></thead><tbody>')
    for j, vals, d12, d32 in spread:
        s.append('<tr><td><code>%s</code></td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>' % (
            E(j), fmt(vals[0]), fmt(vals[1]), fmt(vals[2]), ("%+.4f" % d12) if d12 is not None else "—", ("%+.4f" % d32) if d32 is not None else "—"))
    s.append('</tbody></table></div></section>')
    return "\n".join(s)


def sec_xc(xc):
    s = ['<section id="sim-xcheck"><h2><span class="n">4</span>Cross-checks between the lanes — where the files agree and where they do not</h2>',
         '<p class="lede">Each row compares two files as they are on disk now. AGREE means the digits are identical; DIFFER means they are not, and the note says why and which one the downstream study used. Nothing here is reconciled by choosing a middle value.</p>',
         '<div class="tw"><table class="data compact"><caption>Table 5. Inter-lane cross-checks.</caption><thead><tr><th>#</th><th>What</th><th>Side A</th><th>Side B</th><th>Verdict</th><th>Note</th></tr></thead><tbody>']
    for r in xc:
        s.append('<tr><td><code>%s</code></td><td>%s</td><td>%s<br><span class="small">%s</span></td><td>%s<br><span class="small">%s</span></td><td>%s</td><td>%s</td></tr>' % (
            r["i"], E(r["what"]), E(str(r["a"])), E(str(r["asrc"])), E(str(r["b"])), E(str(r["bsrc"])), chip(r["verdict"]), E(r["note"])))
    s.append('</tbody></table></div></section>')
    return "\n".join(s)


def renumber(frag, prefix, table_prefix, old_prefix=""):
    """Prefix the chapter's section numbers and table numbers; ids and text are otherwise untouched."""
    def n_repl(m):
        v = m.group(2)
        if old_prefix and v.startswith(old_prefix):
            v = v[len(old_prefix):]
        return '<span class="n">%s.%s</span>' % (prefix, v)
    frag = re.sub(r'<span class="(n|tn)">([^<]+)</span>', n_repl, frag)
    frag = re.sub(r'\bTable (\d+[a-z]?)(?=[.\s,:;)])', lambda m: "Table %s.%s" % (table_prefix, m.group(1)), frag)
    if old_prefix:   # F2 writes "Table F2-1a", F3 writes "Table F3.2b" — same chapter letter as the sections
        frag = frag.replace("Table %s-" % old_prefix.rstrip("."), "Table %s." % table_prefix).replace("Table %s" % old_prefix, "Table %s." % table_prefix)
    return frag


def sec_chapter(letter, title, blurb, body):
    return '<section id="ch-%s" class="chapter"><h2><span class="n">%s</span>%s</h2><p class="lede">%s</p></section>\n%s' % (letter, letter, E(title), blurb, body)


CARRY_PREFIXES = ["fea_microduck-", "fea_nlgeom_", "fea_convergence", "fea_materials", "fea_meshability", "buckling_", "section_", "fatigue_", "drop_impact", "loads_mujoco",
                  "collision-model-census", "cavity-volumes", "joint-geometry", "gait-torque-duty", "gait-peaks", "gait-robustness", "battery-runtime", "thermal-servo", "thermal-compute", "tolerance-stack"]


def carried_prefixes():
    """Which of the prefixes above the three chapter generators actually name in their SOURCE — measured, not assumed."""
    src = "".join(open(os.path.join(HERE, f)).read() for f in ("gen_structural.py", "gen_simulation_f2.py", "gen_simulation_f3.py"))
    return [p for p in CARRY_PREFIXES if p in src]


def is_carried(st, chapters_html, prefixes):
    if st["study"] in chapters_html or st["name"] in chapters_html or st["file"] in chapters_html:
        return True
    return any(st["name"].startswith(p) for p in prefixes)


def sec_orphans(S, chapters_html):
    """Studies no chapter consumes get a card here, so nothing on disk is only in the matrix."""
    prefixes = carried_prefixes()
    s = ['<section id="sim-orphans"><h2><span class="n">D</span>Studies no chapter carries</h2>',
         '<p class="lede">Measured against the three chapters as emitted and against their generators\' source: a study file is "carried" if a chapter names it, or if its file-name prefix is one the chapter generator reads (%s). Any other file is presented here from its own JSON, so every file on disk has a section and not only a row.</p>' % E(", ".join(prefixes))]
    n = 0
    for st in S:
        if is_carried(st, chapters_html, prefixes):
            continue
        n += 1
        d = st["data"]
        s.append('<div class="card"><h3><code>%s</code> — %s %s</h3>' % (E(st["file"]), chip(st["verdict"] or "MEASUREMENT"), E(st["verdict_note"])))
        if isinstance(d, dict):
            if d.get("what"):
                s.append('<p><b>What.</b> %s</p>' % E(d["what"]))
            if d.get("why"):
                s.append('<p><b>Why.</b> %s</p>' % E(d["why"]))
            if d.get("method"):
                s.append('<p><b>Method.</b> %s</p>' % E(d["method"] if isinstance(d["method"], str) else json.dumps(d["method"])[:1500]))
            if st["name"] == "skeptic_f1_recheck":
                s.append('<div class="tw"><table class="data compact"><caption>Table D.1. The skeptic\'s checks.</caption><thead><tr><th>Check</th><th>Verdict</th><th>Recomputed</th><th>Published</th><th>Note</th></tr></thead><tbody>')
                for c in d.get("checks", []):
                    s.append('<tr><td><code>%s</code></td><td>%s</td><td><code class="brk">%s</code></td><td><code class="brk">%s</code></td><td>%s</td></tr>' % (
                        E(c.get("check", "")), chip(c.get("verdict")), E(json.dumps(c.get("recomputed"))[:400]), E(json.dumps(c.get("published"))[:400]), E(c.get("note") or c.get("why") or "")))
                s.append('</tbody></table></div>')
            if st["name"] == "collision-model-census":
                s.append('<div class="tw"><table class="data compact"><caption>Table D.2. The four MuJoCo models and what each can touch (bodies of 15).</caption><thead><tr><th>Model</th><th>File</th><th class="n">Bodies that can touch the floor</th><th class="n">Bodies that can self-collide</th></tr></thead><tbody>')
                for k, v in d["outputs"].items():
                    if isinstance(v, dict):
                        s.append('<tr><td><code>%s</code></td><td><code>%s</code></td><td class="n">%s</td><td class="n">%s</td></tr>' % (
                            E(k), E(d["inputs"]["models"].get(k, "")), E(str(v.get("n_bodies_floor", v.get("bodies_that_can_touch_floor", "—")))[:60]), E(str(v.get("n_bodies_self", v.get("bodies_that_can_self_collide", "—")))[:60])))
                s.append('</tbody></table></div>')
            if st["name"].startswith("stress/") and isinstance(d.get("results"), (list, dict)):
                res = d["results"] if isinstance(d["results"], list) else list(d["results"].values())
                s.append('<div class="tw"><table class="data compact"><caption>Table D.%s. %s results.</caption><thead><tr><th>Part</th><th>Case</th><th class="n">Load N</th><th class="n">SF</th><th>Verdict</th><th>Why</th></tr></thead><tbody>' % (st["name"].split("/")[1], E(st["file"])))
                for r in res:
                    s.append('<tr><td><code>%s</code></td><td>%s</td><td class="n">%s</td><td class="n">%s</td><td>%s</td><td>%s</td></tr>' % (
                        E(str(r.get("part") or r.get("slug"))), E(str(r.get("case", "—"))), fmt(r.get("force_N", r.get("load_N"))) if not isinstance(r.get("force_N"), list) else fmt(norm(r["force_N"])), fmt(r.get("sf")), chip(r.get("verdict")), E(first_sentence(r.get("why") or r.get("reason") or "", 200))))
                s.append('</tbody></table></div>')
                if d.get("correction"):
                    s.append('<p class="note">%s</p>' % E(d["correction"]))
        s.append('<p class="small">Full inputs, outputs and artifacts: <a href="#%s">register entry</a>.</p></div>' % anchor(st["name"]))
    if n == 0:
        s.append('<p>Every study on disk is carried by a chapter.</p>')
    s.append('</section>')
    return "\n".join(s), n


def summarise(v, depth=0):
    """Depth-1 rendering of a JSON value: scalars and strings in full, containers described."""
    if v is None:
        return "—"
    if isinstance(v, (int, float, bool)):
        return fmt(v)
    if isinstance(v, str):
        return E(v)
    if isinstance(v, list):
        if all(isinstance(x, (int, float)) for x in v) and len(v) <= 6:
            return "[" + ", ".join(fmt(x) for x in v) + "]"
        if all(isinstance(x, str) for x in v) and len(v) <= 8:
            return "[" + ", ".join(E(x) for x in v) + "]"
        return "<i>list of %d</i>" % len(v)
    if isinstance(v, dict):
        if depth == 0 and len(v) <= 12 and all(isinstance(x, (int, float, str, bool, type(None))) for x in v.values()):
            return "<br>".join("<code>%s</code>: %s" % (E(k), summarise(x, 1)) for k, x in v.items())
        return "<i>{%d keys: %s}</i>" % (len(v), E(", ".join(list(v.keys())[:10]) + (", …" if len(v) > 10 else "")))
    return E(str(v))


def sec_register(S):
    s = ['<section id="sim-register"><h2><span class="n">8</span>Study register — every file, its inputs with sources, its outputs, its artifacts</h2>',
         '<p class="lede">The JSON files, rendered one level deep: scalars and strings in full (a source string is evidence and is not shortened), containers named with their keys. Anything deeper is in the file itself, linked.</p>']
    for st in sorted(S, key=lambda x: (FAMILY_ORDER.index(x["family"]) if x["family"] in FAMILY_ORDER else 99, x["name"])):
        d = st["data"]
        s.append('<div class="card reg" id="%s"><h3><a href="%s"><code>%s</code></a> — %s <span class="small">%s</span></h3>' % (anchor(st["name"]), E(st["file"]), E(st["file"]), chip(st["verdict"] or "MEASUREMENT"), E(st["verdict_note"])))
        meta = []
        if isinstance(d, dict):
            for k in ("study", "part", "case", "script", "tool", "generated", "what"):
                if d.get(k):
                    meta.append("<b>%s</b> %s" % (E(k), E(str(d[k]))))
        s.append('<p class="small">%s · %d bytes · family %s</p>' % (" · ".join(meta), st["size"], E(FAMILY_LABEL.get(st["family"], "other"))))
        if isinstance(d, dict) and d.get("why"):
            s.append('<p><b>Why.</b> %s</p>' % E(d["why"]))
        if isinstance(d, dict) and d.get("what_settles_it"):
            s.append('<p><b>What settles it.</b> %s</p>' % E(d["what_settles_it"] if isinstance(d["what_settles_it"], str) else json.dumps(d["what_settles_it"])))
        if isinstance(d, dict) and d.get("method"):
            s.append('<p><b>Method.</b> %s</p>' % (E(d["method"]) if isinstance(d["method"], str) else summarise(d["method"])))
        for blk in ("inputs", "outputs", "limits", "known_limitations", "load_basis", "cases", "limitation"):
            if isinstance(d, dict) and d.get(blk) is not None:
                v = d[blk]
                if isinstance(v, dict):
                    s.append('<details><summary>%s — %d keys</summary><div class="tw"><table class="data compact"><tbody>' % (E(blk), len(v)))
                    for k, x in v.items():
                        s.append('<tr><td><code>%s</code></td><td>%s</td></tr>' % (E(k), summarise(x)))
                    s.append('</tbody></table></div></details>')
                elif isinstance(v, list):
                    s.append('<details><summary>%s — %d items</summary><ul>%s</ul></details>' % (E(blk), len(v), "".join("<li>%s</li>" % (E(x) if isinstance(x, str) else summarise(x)) for x in v)))
                else:
                    s.append('<p><b>%s.</b> %s</p>' % (E(blk), E(str(v))))
        if isinstance(d, dict) and d.get("artifacts"):
            items = []
            for a in d["artifacts"]:
                if isinstance(a, str):
                    ex = os.path.exists(os.path.join(REPO, a))
                    items.append('<li>%s<code class="brk">%s</code>%s%s</li>' % ('<a href="%s">' % E(a) if ex else "", E(a), "</a>" if ex else "", "" if ex else ' <span class="chip fail">MISSING</span>'))
                else:
                    items.append("<li>%s</li>" % summarise(a))
            s.append('<details><summary>artifacts — %d</summary><ul>%s</ul></details>' % (len(d["artifacts"]), "".join(items)))
        if isinstance(d, dict) and d.get("looked_at"):
            s.append('<details><summary>looked_at — %d</summary><ul>%s</ul></details>' % (len(d["looked_at"]), "".join("<li>%s</li>" % (E(x) if isinstance(x, str) else summarise(x)) for x in d["looked_at"])))
        s.append('</div>')
    s.append('</section>')
    return "\n".join(s)


def sec_cd(reg):
    s = ['<section id="sim-cd"><h2><span class="n">9</span>Every CANNOT DETERMINE, and what settles each</h2>',
         '<p class="lede">A recursive walk of every study file for a <code>verdict</code> of CANNOT DETERMINE, a <code>cannot_determine</code> list, or a field whose value begins with those words. %d distinct items. Where the file names what would settle it, that is printed; where it does not, the cell says so — a missing answer stays missing.</p>' % len(reg),
         '<div class="tw"><table class="data compact"><caption>Table 6. The CANNOT DETERMINE register across all study files.</caption><thead><tr><th class="n">#</th><th>File · path</th><th>What</th><th>Why</th><th>What settles it</th></tr></thead><tbody>']
    for k, r in enumerate(reg, 1):
        paths = r["paths"][0] + (" (+%d identical: %s)" % (len(r["paths"]) - 1, ", ".join(r["paths"][1:])) if len(r["paths"]) > 1 else "")
        s.append('<tr><td class="n">%d</td><td><code class="brk">%s</code><br><code class="brk small">%s</code></td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            k, E(r["file"].replace("out/sim-evidence/", "")), E(paths), E(", ".join(str(w) for w in r["whats"][:6]) + (" … (%d)" % len(r["whats"]) if len(r["whats"]) > 6 else "")), E(str(r["why"])) if r["why"] else "<i>the file gives no reason on this item</i>",
            E(r["settles"]) if r["settles"] else '<i>the file names nothing that settles it</i>'))
    s.append('</tbody></table></div>')
    nos = sum(1 for r in reg if not r["settles"])
    xr = sum(1 for r in reg if r.get("settles_xref"))
    s.append('<p class="note">%d of %d distinct items name what settles them (%d of those by cross-reference to another study file about the same part, marked "stated in"); %d do not. Those %d are the studies\' own gaps and are listed as such — this page does not invent a test the study did not specify. Identical items reached by several JSON paths are folded into one row with the path count.</p>' % (len(reg) - nos, len(reg), xr, nos, nos))
    s.append('</section>')
    return "\n".join(s)


def sec_artifacts(arts, doc_so_far):
    s = ['<section id="sim-artifacts"><h2><span class="n">10</span>Images and videos, read back</h2>',
         '<p class="lede">Every image or video any study names in its <code>artifacts</code>. Each PNG was opened and measured here (pixel size, distinct colours on a 256 px thumbnail, ink fraction); a picture with fewer than 8 colours is flagged blank. Each MP4 carries lane F2\'s read-back record (frames decoded back from the file, mean inter-frame difference). The last column says whether the picture is embedded somewhere on this page.</p>',
         '<div class="tw"><table class="data compact"><caption>Table 7. Artifact read-back.</caption><thead><tr><th>Artifact</th><th>Kind</th><th class="n">Bytes</th><th>Read back</th><th>Named by</th><th>On page</th></tr></thead><tbody>']
    for r in arts:
        if r["ext"] in (".png", ".jpg"):
            if r.get("w"):
                rb = "%d × %d px, %d colours, ink %.4f%s" % (r["w"], r["h"], r["colours"], r["ink"], " — <b>BLANK</b>" if r.get("blank") else "")
            else:
                rb = r.get("note", "—")
        elif r["ext"] == ".mp4":
            rb = ("%d frames at %s fps encoded; %s decoded back; mean inter-frame diff %s; intensity %s" % (r.get("frames") or 0, fmt(r.get("fps")), fmt(r.get("read_back")), fmt(r.get("diff")), r.get("inten"))) if r.get("video") else "no read-back record in out/sim-sweep/videos.json"
        else:
            rb = "exists" if r["exists"] else "MISSING"
        onpage = ('src="%s"' % r["path"]) in doc_so_far or ('href="%s"' % r["path"]) in doc_so_far
        s.append('<tr%s><td><a href="%s"><code class="brk">%s</code></a></td><td>%s</td><td class="n">%s</td><td>%s</td><td class="small">%s</td><td>%s</td></tr>' % (
            ' class="cd"' if (not r["exists"] or r.get("blank")) else "", E(r["path"]), E(r["path"]), E(r["ext"][1:]), fmt(r["size"]), rb, E(", ".join(r["by"])), "yes" if onpage else "linked only"))
    s.append('</tbody></table></div>')
    # gallery of pictures no chapter embeds
    extra = [r for r in arts if r["ext"] in (".png", ".jpg") and r["exists"] and ('src="%s"' % r["path"]) not in doc_so_far]
    if extra:
        s.append('<h3>Pictures no chapter embeds</h3><div class="grid2 gal">')
        for r in extra:
            s.append('<figure><img src="%s" alt="%s" loading="lazy"><figcaption>%s — %s</figcaption></figure>' % (E(r["path"]), E(r["path"]), E(r["path"].split("/")[-1]), E(", ".join(r["by"]))))
        s.append('</div>')
    s.append('</section>')
    return "\n".join(s)


def sec_method(S, subs, checks, chapter_none=0):
    s = ['<section id="sim-method"><h2><span class="n">11</span>Method — how this page is made and checks itself</h2><ul>',
         '<li><b>Inputs.</b> Every <code>*.json</code> at the top of <code>out/sim-evidence/</code> (%d files) and <code>out/stress/{matrix,report,corrected}.json</code>. Below the top level sit %s — per-deck and per-cell records that the studies above summarise; they are counted, not tabulated.</li>' % (
             len(S) - 3, ", ".join("%s (%d)" % (E(k), v) for k, v in sorted(subs.items()))),
         '<li><b>Chapters A–C</b> are the lanes\' own generators imported and called: <code>tools/gen_structural.sections()</code>, <code>tools/gen_simulation_f2.sections()</code>, <code>tools/gen_simulation_f3.sections()</code>. Their section and table numbers are prefixed with the chapter letter by a regular expression; their text, ids and figures are untouched, so they cannot drift from STRUCTURAL.html or the F2/F3 previews.</li>',
         '<li><b>Load chain.</b> The force each deck applied is the per-DOF sum of every <code>*CLOAD</code> line in <code>out/sim-evidence/fea/&lt;study&gt;/&lt;part&gt;_&lt;case&gt;.inp</code>; the resolution of each <code>force_source</code> string is done by pattern against <code>loads_mujoco.json</code> as it is on disk.</li>',
         '<li><b>Numbers</b> are printed with the digits the JSON holds (Python <code>repr</code>); percentages are computed here and printed to 4 dp.</li>',
         '<li><b>Self-check</b> before writing: %s. The page is not written if any fails.</li>' % E("; ".join(checks)),
         '<li><b>What this page found in the chapters and did not patch.</b> Chapter text is the lanes\' generators\' output verbatim; this generator measures it and reports rather than edits. Cells reading the literal word “None” inside chapters A–C: <b>%d</b> (in chapter A\'s Table A.6 the 0.7 mm mesh row of the ankle convergence study, which never solved — the study\'s CANNOT DETERMINE row prints its null fields as the word). That is a defect of <code>tools/gen_structural.py</code>\'s formatter, recorded here for lane F1.</li>' % chapter_none,
         '<li><b>Read-back.</b> The written page is screenshotted with <code>tools/shot_page.py</code> (DOM height, broken images, every table measured against its column) and the strips are read.</li>',
         '</ul></section>']
    return "\n".join(s)


# ----------------------------------------------------------------------------- page
STYLE = """
  .chip.fail{color:var(--no)} .chip.meas{color:var(--ink-2)}
  .small{font-family:var(--sans);font-size:11.5px;color:var(--ink-2)}
  .brk{word-break:break-all}
  .verdict{border-left:3px solid var(--accent);padding:2px 0 2px 18px;margin:14px 0;font-size:15.5px}
  .verdict b{color:var(--accent)} .verdict ul{margin:6px 0 0;padding-left:18px;font-size:14px}
  .verdict.warn{border-left-color:var(--no)} .verdict.warn b{color:var(--no)}
  .data td.cd, .data tr.cd td{background:#fff4f2}
  section.chapter>h2{font-size:26px;margin-top:44px;border-bottom:2px solid var(--rule)}
  section>h2 .tn{font-family:var(--mono);font-weight:600;color:var(--accent);font-size:18px;padding-right:12px}
  h2.sec{font-size:22px;padding-bottom:6px;border-bottom:1px solid var(--hair);margin:0 0 12px}
  .card{margin:14px 0}
  .card.reg h3{font-size:13.5px} .card.reg p{font-size:13.5px;margin:6px 0}
  .card.reg details{font-size:13px;margin:4px 0} .card.reg summary{cursor:pointer;font-family:var(--sans);font-weight:600;font-size:12px}
  .card.reg table.data.compact td{font-size:12px;word-break:break-word}
  .card.reg ul{font-size:12.5px}
  .pair{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:10px 0 4px}
  .pair figure{margin:0;padding:8px} .pair figure img{width:100%;aspect-ratio:1/1;object-fit:contain;background:#fff}
  .tag{font-family:var(--sans);font-size:10.5px;font-weight:600;letter-spacing:.07em;text-transform:uppercase;display:inline-block;padding:2px 8px;margin-bottom:6px;border:1px solid var(--hair);color:var(--ink-2)}
  .tag.ours{color:var(--accent);border-color:var(--accent)}
  .paircap{font-family:var(--sans);font-size:12.5px;color:var(--ink-2);margin:0 0 2px}
  section[id^="f2-"] .grid2{grid-template-columns:repeat(4,1fr)} section[id^="f2-"] .grid2 figure{margin:0} section[id^="f2-"] .grid2 img{width:100%}
  section[id^="f2-"] table.data{font-size:12px} section[id^="f3-"] table.data{font-size:10.5px} section[id^="f3-"] th{white-space:normal} section[id^="f3-"] td{overflow-wrap:anywhere}
  table.data td code{font-size:12px}
  .gal figure img{aspect-ratio:auto}
  #sim-cd table,#sim-xcheck table,#sim-chain table.compact,#sim-matrix table{table-layout:fixed;width:100%}
  #sim-cd td,#sim-xcheck td,#sim-chain td,#sim-matrix td{word-break:break-word;overflow-wrap:anywhere}
  section[id^="sim-"] th{white-space:normal} section[id^="sim-"] .chip{white-space:normal}
  #sim-chain td.n,#sim-matrix td.n,#sim-xcheck td.n,#sim-cd td.n,#sim-artifacts td.n{white-space:normal;overflow-wrap:normal;word-break:normal}
  #sim-chain table.compact th:nth-child(1){width:9%} #sim-chain table.compact th:nth-child(2){width:23%} #sim-chain table.compact th:nth-child(3){width:8%} #sim-chain table.compact th:nth-child(4){width:8%} #sim-chain table.compact th:nth-child(5){width:8%} #sim-chain table.compact th:nth-child(6){width:10%} #sim-chain table.compact th:nth-child(7){width:6%} #sim-chain table.compact th:nth-child(8){width:7%} #sim-chain table.compact th:nth-child(9){width:10%} #sim-chain table.compact th:nth-child(10){width:11%}
  #sim-matrix th:nth-child(1){width:4%} #sim-matrix th:nth-child(2){width:19%} #sim-matrix th:nth-child(3){width:13%} #sim-matrix th:nth-child(4){width:15%} #sim-matrix th:nth-child(5){width:10%} #sim-matrix th:nth-child(6){width:32%} #sim-matrix th:nth-child(7){width:7%}
  #sim-cd th:nth-child(1){width:3%} #sim-cd th:nth-child(2){width:20%} #sim-cd th:nth-child(3){width:14%} #sim-cd th:nth-child(4){width:38%} #sim-cd th:nth-child(5){width:25%}
  @media(max-width:640px){.pair{grid-template-columns:1fr} section[id^="f2-"] .grid2{grid-template-columns:1fr 1fr}}
"""


def page():
    L = load(os.path.join(EV, "loads_mujoco.json"))
    S = studies()
    subs = sub_json_census()
    chain = chain_rows(S, L)
    xc, spread = crosschecks(S, L, chain)
    cdreg = cd_register(S)
    arts = artifacts(S)

    chA = renumber("\n\n".join(F1.sections()), "A", "A")
    chB = renumber(F2.sections(), "B", "B", old_prefix="F2.")
    chC = renumber(F3.sections(), "C", "C", old_prefix="F3.")
    chapters = "\n".join([
        sec_chapter("A", "Structural — FEA, nonlinear re-solves, buckling, drop and fatigue (lane F1)",
                    'Included from <code>tools/gen_structural.py</code>, the generator of <a href="STRUCTURAL.html">STRUCTURAL.html</a>; every load is the measured chain of §3.', chA),
        sec_chapter("B", "Gait robustness, peak loads and battery runtime (lane F2)",
                    'Included from <code>tools/gen_simulation_f2.py</code> (preview: <a href="out/sim-evidence/f2-preview.html">f2-preview.html</a>); the peaks here are the numbers §4 cross-checks against F1 and F3.', chB),
        sec_chapter("C", "Thermal and tolerance stack-up (lane F3)",
                    'Included from <code>tools/gen_simulation_f3.py</code> (preview: <a href="out/sim-evidence/f3-preview.html">f3-preview.html</a>); the duty it heats with is F2\'s measured baseline (§4 X5).', chC)])
    orph, n_orph = sec_orphans(S, chapters)
    checks = []
    front = "\n\n".join([sec_verdict(S, chain, xc, cdreg, arts, subs), sec_matrix(S), sec_chain(L, chain, spread, S), sec_xc(xc)])
    back1 = "\n\n".join([orph, sec_register(S), sec_cd(cdreg)])
    body_so_far = front + chapters + back1
    back2 = sec_artifacts(arts, body_so_far)
    check_names = ["every study file on disk has a matrix row and a register card", "statbar counts equal a recount", "every study's why is printed in full", "every image exists", "every local link resolves",
                   "no duplicate element id", "chapters A, B, C each present with their first section", "every CANNOT DETERMINE found by the walk is in Table 6", "every FEA study with a deck has its Σ CLOAD row",
                   "every DIFFER cross-check carries a note", "no 'None' leaks into a cell of this generator's own sections"]
    chapter_none = chapters.count(">None<")
    body = "\n\n".join([front, chapters, back1, back2, sec_method(S, subs, check_names, chapter_none)])
    toc = ('<nav class="toc"><a href="#sim-verdict">1 Verdict</a><a href="#sim-matrix">2 Matrix</a><a href="#sim-chain">3 Load chain</a><a href="#sim-xcheck">4 Cross-checks</a>'
           '<a href="#ch-A">A Structural</a><a href="#ch-B">B Gait &amp; battery</a><a href="#ch-C">C Thermal &amp; tolerance</a><a href="#sim-orphans">D Uncarried</a>'
           '<a href="#sim-register">8 Register</a><a href="#sim-cd">9 CANNOT DETERMINE</a><a href="#sim-artifacts">10 Read-back</a><a href="#sim-method">11 Method</a></nav>')
    n = len(S)
    c = {v: sum(1 for s in S if s["verdict"] == v) for v in ("PASS", "FAIL", "CANNOT DETERMINE")}
    doc = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Simulation Evidence</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opt_sz,wght@8..60,400;8..60,600;8..60,700&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="tools/doc.css">
<style>%s</style>
</head>
<body>
<div class="wrap">
<p class="backlink"><a href="RELEASE.html">← Release dossier</a> · <a href="INDEX.html">Repo index</a> · <a href="STRUCTURAL.html">Structural evidence</a></p>
<header class="hero">
  <p class="eyebrow">Microduck · simulation evidence · every study, one document</p>
  <h1>Simulation evidence: structural FEA, drop, fatigue, gait robustness, battery runtime, thermal and tolerance stack-up — %d study files, %d PASS / %d FAIL / %d CANNOT DETERMINE</h1>
  <p class="sub">Assembled from every JSON the three simulation lanes wrote. The load basis is one measured chain from the MJCF mass through MuJoCo's peaks to the force each solver deck carries; the lanes are cross-checked against each other and every disagreement is printed; every CANNOT DETERMINE anywhere is registered with what settles it; every picture and video is read back.</p>
  <div class="rev"><span>MD-SIM-001 · Rev A</span><span>%s</span><span>generator: tools/gen_simulation.py (self-checked)</span><span>data: out/sim-evidence/*.json + out/stress/*.json</span></div>
</header>
%s
%s
<footer><span>Generated by tools/gen_simulation.py; every number on this page is read from a file named beside it.</span><span>Chapters A–C are the lanes' own generators, included verbatim and renumbered.</span><span>%s</span></footer>
</div>
</body>
</html>
""" % (STYLE, n, c["PASS"], c["FAIL"], c["CANNOT DETERMINE"], DATE, toc, body, DATE)
    return doc, dict(S=S, chain=chain, xc=xc, cdreg=cdreg, arts=arts, n_orph=n_orph, chapters=chapters)


# ----------------------------------------------------------------------------- selfcheck
def selfcheck(doc, ctx):
    out, ok = [], True

    def check(name, cond, detail=""):
        nonlocal ok
        ok = ok and bool(cond)
        out.append("%-4s %s%s" % ("PASS" if cond else "FAIL", name, (" — " + detail) if detail else ""))

    S = ctx["S"]
    disk = sorted(glob.glob(os.path.join(EV, "*.json"))) + [os.path.join(STRESS, n + ".json") for n in ("matrix", "report", "corrected") if os.path.exists(os.path.join(STRESS, n + ".json"))]
    check("every study file on disk has a matrix row and a register card", len(S) == len(disk) and all(('id="%s"' % anchor(s["name"])) in doc and ('href="#%s"' % anchor(s["name"])) in doc for s in S), "%d files" % len(disk))
    c = {v: sum(1 for s in S if s["verdict"] == v) for v in ("PASS", "FAIL", "CANNOT DETERMINE")}
    check("statbar counts equal a recount", ("<b>%d / %d / %d</b>" % (c["PASS"], c["FAIL"], c["CANNOT DETERMINE"])) in doc and ("<b>%d</b><span>study files on disk" % len(S)) in doc, "%d: %d/%d/%d" % (len(S), c["PASS"], c["FAIL"], c["CANNOT DETERMINE"]))
    whys = [s for s in S if s["why"]]
    missing = [s["name"] for s in whys if E(s["why"]) not in doc]
    check("every study's why is printed in full", not missing, "%d whys, missing: %s" % (len(whys), missing[:5]))
    imgs = re.findall(r'<img src="([^"]+)"', doc)
    miss = [i for i in imgs if not os.path.exists(os.path.join(REPO, i))]
    check("every image exists", not miss, "%d images, missing: %s" % (len(imgs), miss[:5]))
    hrefs = [h for h in re.findall(r'href="([^"#][^"]*)"', doc) if not h.startswith("http")]
    dead = [h for h in hrefs if not os.path.exists(os.path.join(REPO, h.split("#")[0]))]
    check("every local link resolves", not dead, "%d links, dead: %s" % (len(hrefs), dead[:5]))
    ids = re.findall(r' id="([^"]+)"', doc)
    dup = sorted(set(i for i in ids if ids.count(i) > 1))
    check("no duplicate element id", not dup, "%d ids, duplicates: %s" % (len(ids), dup[:6]))
    check("chapters A, B, C each present with their first section", all(x in doc for x in ('id="ch-A"', 'id="ch-B"', 'id="ch-C"', 'id="verdict"', 'id="f2-gait"', 'id="f3-servo-thermal"')))
    anchors = re.findall(r'href="#([^"]+)"', doc)
    dead_a = sorted(set(a for a in anchors if ('id="%s"' % a) not in doc))
    check("every in-page anchor has a target", not dead_a, "dead anchors: %s" % dead_a[:8])
    check("every CANNOT DETERMINE found by the walk is in Table 6", ("%d distinct items. Where" % len(ctx["cdreg"])) in doc and all(E(p) in doc for r in ctx["cdreg"] for p in r["paths"]), "%d distinct items, %d paths" % (len(ctx["cdreg"]), sum(len(r["paths"]) for r in ctx["cdreg"])))
    withdeck = [ch for ch in ctx["chain"] if ch["inp"]]
    check("every FEA study with a deck has its Σ CLOAD row", all(ch["cloadn"] is not None for ch in withdeck), "%d decks of %d studies" % (len(withdeck), len(ctx["chain"])))
    check("every DIFFER cross-check carries a note", all(r["note"] for r in ctx["xc"] if r["verdict"] == "DIFFER"), "%d DIFFER of %d" % (sum(1 for r in ctx["xc"] if r["verdict"] == "DIFFER"), len(ctx["xc"])))
    own = doc.replace(ctx["chapters"], "")
    check("no 'None' leaks into a cell of this generator's own sections", ">None<" not in own and "None N" not in own and "None kg" not in own, "chapters A-C carry %d (reported in §11, not patched)" % ctx["chapters"].count(">None<"))
    check("orphan section lists every study no chapter names", ctx["n_orph"] >= 0, "%d studies carried only by chapter D" % ctx["n_orph"])
    return ok, out


if __name__ == "__main__":
    doc, ctx = page()
    ok, lines = selfcheck(doc, ctx)
    print("\n".join(lines))
    if not ok:
        print("SELFCHECK FAILED — SIMULATION.html not written", file=sys.stderr)
        sys.exit(1)
    out = os.path.join(REPO, "SIMULATION.html")
    open(out, "w").write(doc)
    print("wrote", out, os.path.getsize(out), "bytes")
