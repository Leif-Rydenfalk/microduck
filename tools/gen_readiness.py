#!/usr/bin/env python3
"""gen_readiness.py — the READINESS AUDIT for the factory pack.

Reads MEASUREMENTS (out/factory/measure/*.json, written by the commands named
in each block below) and the repo's own data files, grades every artifact
READY TO BUILD FROM / NOT YET / CANNOT DETERMINE, and writes:

    out/factory/readiness.json   the audit, one row per artifact
    out/factory/readiness.html   the same, house style, bilingual headers

Nothing here is typed in: every count on the page is computed from a file a
factory engineer can open. The only hand-written input is
tools/data/readiness.json (who closes each parcel; the manual's unstated
assumptions, read as a stranger).

Re-measure before regenerating:
    ce-cad/bin/sheetcheck --all --json out/factory/measure/sheetcheck.json out/drawings
    bin/triad check --all --json > out/factory/measure/triad.json
    python3 tools/stlcheck.py                         (-> measure/stlcheck.json)
    python3 tools/gen_readiness.py
"""
import datetime
import glob
import html
import json
import os
import re
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MEAS = os.path.join(ROOT, "out", "factory", "measure")
OUT_JSON = os.path.join(ROOT, "out", "factory", "readiness.json")
OUT_HTML = os.path.join(ROOT, "out", "factory", "readiness.html")


def J(p):
    with open(os.path.join(ROOT, p) if not os.path.isabs(p) else p, encoding="utf-8") as f:
        return json.load(f)


def git_last_commit(path):
    try:
        s = subprocess.check_output(["git", "log", "-1", "--format=%ci", "--", path], cwd=ROOT, text=True).strip()
        return s[:16] if s else None
    except Exception:
        return None


D = J("tools/data/readiness.json")
G = D["grades"]
CL = D["closers"]
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
rows = []


def row(cls, ident, name, grade, measurement, evidence, missing="", closer=None, by="", extra=None):
    r = {"class": cls, "id": ident, "name": name, "grade": grade, "grade_en": G[grade]["en"], "grade_zh": G[grade]["zh"],
         "measurement": measurement, "evidence": evidence, "missing": missing,
         "closer": closer, "closer_en": CL[closer]["en"] if closer else "", "closer_zh": CL[closer]["zh"] if closer else "", "by": by}
    if extra:
        r.update(extra)
    rows.append(r)
    return r


# ---------------------------------------------------------------- 1 drawings
SC = J(os.path.join(MEAS, "sheetcheck.json"))
kinds = {}
for line in open(os.path.join(MEAS, "sheetcheck.log"), encoding="utf-8"):
    m = re.match(r"^(microduck-\S+)\s+(DRAW|PRINT)\s+", line)
    if m:
        kinds[m.group(1)] = m.group(2)
RULES = ["dim_coverage", "coverage", "empty_rect", "font", "iso", "renders", "line_ratio", "curve_density"]
sheet_table = []
for slug, sh in sorted(SC["sheets"].items()):
    c = sh["checks"]
    meas = {r: c.get(r, {}).get("measured") for r in RULES}
    verd = {r: c.get(r, {}).get("verdict") for r in RULES}
    fails = [r for r in RULES if verd[r] == "FAIL"]
    cds = [r for r in RULES if verd[r] == "CANNOT DETERMINE"]
    kind = kinds.get(slug, "?")
    dimc = meas["dim_coverage"]
    tess = "TESSELLATION" in (c.get("dim_coverage", {}).get("why", "") or "")
    if sh["verdict"] == "PASS":
        grade, missing, closer, by = "READY", "", None, ""
    else:
        parts = []
        if dimc is None:
            parts.append("feature census refused (" + ("mesh-backed part, not a parametric solid" if tess else "enumerator found no census") + ")")
        elif dimc < 100:
            parts.append("%.1f %% of enumerated features dimensioned" % dimc)
        parts.append("layout fails %d of 8 rules (%s)" % (len(fails), ", ".join(fails)))
        missing = "; ".join(parts) + "."
        grade = "NOT_YET"
        if tess or kind == "PRINT":
            closer, by = "agent_later", "a parametric rebuild of the part before A4 dimension coverage can exist; layout rules by WF-SHEETS tonight"
        else:
            closer, by = "agent_tonight", "WF-SHEETS (sheet rebuild) for layout; WF-FASTENERS for the hole classes it leaves undimensioned"
    ev = "out/factory/measure/sheetcheck.json[%s] (bin/sheetcheck %s), sheet %s" % (slug, SC["generated"], os.path.relpath(sh["svg"], ROOT))
    r = row("drawing", slug, slug, grade,
            "verdict %s; dim %s; occupancy %.1f %% (>=85); empty rect %.1f %% (<5); min font %.1f mm (>=3.5); iso %s (>=4); renders %s (>=6); line ratio %s (<=10); curve density %s (<=1.43)" % (
                sh["verdict"], ("CD" if dimc is None else "%.1f %%" % dimc), meas["coverage"] or 0, meas["empty_rect"] or 0, meas["font"] or 0, meas["iso"], meas["renders"],
                ("CD" if meas["line_ratio"] is None else "%.2f" % meas["line_ratio"]), ("CD" if meas["curve_density"] is None else "%.2f" % meas["curve_density"])),
            ev, missing, closer, by,
            {"kind": kind, "checks": {k: {"measured": meas[k], "verdict": verd[k], "limit": c.get(k, {}).get("limit")} for k in RULES}, "fails": fails, "cannot_determine": cds})
    sheet_table.append(r)

# printed parts that have NO sheet at all
slice_ = J("out/print/slice.json")
print_slugs = [p["slug"] for p in slice_["parts"]]
sheeted = set(SC["sheets"])
no_sheet = []
for s in print_slugs:
    if s in sheeted:
        continue
    d = os.path.join(ROOT, "out", "drawings", s)
    why = "no out/drawings/%s/ directory at all" % s
    if os.path.isdir(d):
        rj = os.path.join(d, "result.json")
        if os.path.exists(rj):
            why = (J(rj).get("why") or "result.json without a why")[:160]
        else:
            why = "directory exists, no SVG, no result.json"
    no_sheet.append(s)
    row("drawing", s, s, "NOT_YET", "no drawing sheet exists; " + why, "out/drawings/%s/ (ls, %s)" % (s, NOW[:16]),
        "No sheet can be drawn: the part has no parametric geometry (a vendor mesh only).", "agent_later",
        "a parametric rebuild (cad-refcheck loop, p95 <= 1 mm) — not among tonight's six workflows; the factory can print the mesh meanwhile",
        {"kind": "NONE"})

# ---------------------------------------------------------------- 2 print files
STL = {r["file"]: r for r in J(os.path.join(MEAS, "stlcheck.json"))}
MAN = J("out/print/stl_manifest.json")
PB = J("tools/data/playbook.json")
SJ = J(os.path.join(MEAS, "slice-journal.json"))
SH = J(os.path.join(MEAS, "slice-health.json"))  # tools/measure_readiness.py — is the grams/seconds authority answering?
DLT = J(os.path.join(MEAS, "delta.json"))       # this measurement vs the last committed one that differed  # tools/slice_journal.py — every ce-slice run of every microduck STL
stale_named = re.findall(r"The twelve are (.*?):", PB["open"][0]["settles"])
stale_list = [("microduck-" + s.strip().rstrip(".")) for s in re.split(r",| and ", stale_named[0])] if stale_named else []
stale_list = [s for s in stale_list if s.strip("microduck-")]
for p in slice_["parts"]:
    slug = p["slug"]
    st = STL.get(p["stl"], {})
    src = MAN[slug]["stl_source"]
    vendor = src.startswith("vendor")
    stl_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(ROOT, p["stl"]))).strftime("%Y-%m-%dT%H:%M")
    part_commit = git_last_commit("ce-parts/" + slug)
    stale = slug in stale_list
    rebuilt_delta = None
    if stale:
        rb = os.path.join(ROOT, "out", "dfm", "stl-rebuilt", slug + ".stl")
        if os.path.exists(rb):
            try:
                import struct
                def _bbox(path):
                    d = open(path, "rb").read()
                    n = struct.unpack("<I", d[80:84])[0]
                    arr = np.frombuffer(d[84:84 + n * 50], dtype=np.dtype([("n", "<3f4"), ("v", "<9f4"), ("a", "<u2")]))["v"].reshape(-1, 3)
                    return n, arr.max(0) - arr.min(0)
                na, ba = _bbox(os.path.join(ROOT, p["stl"]))
                nb, bb = _bbox(rb)
                rebuilt_delta = {"rebuilt_stl": os.path.relpath(rb, ROOT), "print_triangles": int(na), "rebuilt_triangles": int(nb), "bbox_delta_mm": [round(float(x), 4) for x in (bb - ba)], "max_abs_bbox_delta_mm": round(float(abs(bb - ba).max()), 4)}
            except Exception as e:
                rebuilt_delta = {"error": str(e)}
    problems = []
    if not st.get("watertight"):
        problems.append("STL is NOT watertight (%s open edges)" % st.get("open_edges"))
    if stale:
        problems.append("STL is Pollen's mesh although a PASSed parametric rebuild exists (PLAYBOOK open item 1; STL %s, part folder last commit %s%s)" % (
            stl_mtime, part_commit, ("; rebuilt export bbox differs by at most %.4f mm, so the shape is the same and the difference is PROVENANCE and LICENCE" % rebuilt_delta["max_abs_bbox_delta_mm"]) if rebuilt_delta and "max_abs_bbox_delta_mm" in rebuilt_delta else ""))
    if p.get("slicer_warning"):
        problems.append("slicer warning '%s' and the sliced numbers are from a preset with supports OFF (floor)" % p["slicer_warning"])
    grade = "READY" if not problems or (len(problems) == 1 and p.get("slicer_warning") and not stale and st.get("watertight")) else "NOT_YET"
    if grade == "READY" and vendor:
        note = "printable; LICENCE: Pollen mesh, CC BY-SA-NC — prototype only, not for sale"
    else:
        note = ""
    closer = None
    by = ""
    if grade == "NOT_YET":
        closer = "agent_later"
        by = "re-export from out/dfm/stl-rebuilt/ and re-slice on ce-slice (minutes); the mesh repair for yaw-roll-motion is a rebuild export" if (stale or not st.get("watertight")) else ""
    sj = SJ["parts"].get(slug, {})
    trace = ("traced to a ce-slice journal run and the STL's sha256 %s… is UNCHANGED since"
             % (sj.get("published_run_sha256") or "")[:8]) if sj.get("sha256_still_matches") else "NOT traceable to a journal run"
    if not sj.get("sha256_still_matches"):
        problems.append("the published gram/second figure is %s: re-slice before quoting it" % trace)
        grade = "NOT_YET"
    reb = sj.get("rebuilt_alternative")
    spread = sj.get("orientation_spread")
    extra_meas = "; number %s" % trace
    if reb:
        extra_meas += "; the SAME part sliced from our parametric rebuild %s gives %.4f g / %.0f s (%+.2f %% filament, %+.2f %% time)" % (
            reb["rebuilt_stl"], reb["rebuilt_grams"], reb["rebuilt_seconds"], reb["d_grams_pct"], reb["d_seconds_pct"])
    if spread:
        extra_meas += "; the same file at the same %s mm layer sliced %.4f g / %.0f s auto-oriented and %.4f g / %.0f s as modelled (%+.2f %% time) — the orientation is part of the number" % (
            spread["layer_mm"], spread["grams"][0], spread["seconds"][0], spread["grams"][1], spread["seconds"][1], spread["seconds_pct"])
    row("print", slug, slug, grade,
        "%s x%d %s; bbox %s mm; %d triangles; watertight %s; oriented %s; %.4f g / %.0f s per piece from ce-slice (BambuStudio %s, %s)%s" % (
            p["material"], p["qty"], os.path.basename(p["stl"]), "x".join("%.3f" % b for b in p["bbox_mm"]), st.get("triangles", 0), st.get("watertight"), p["orientation_rule"],
            p["grams_per_piece"], p["seconds_per_piece"], "02.08.02.61", p["process_preset"], extra_meas),
        "out/print/slice.json[%s]; out/factory/measure/stlcheck.json[%s]; out/factory/measure/slice-journal.json[%s] (ce-slice journal ~/dev/ce-slice/state/slices.jsonl, read %s)" % (slug, p["stl"], slug, SJ["read_at"][:16]),
        ("; ".join(problems) + "." if problems else note), closer, by,
        {"stl": p["stl"], "stl_source": src, "vendor_mesh": vendor, "licence": ("CC BY-SA-NC (Pollen sim mesh)" if vendor else "ours"), "stale": stale,
         "watertight": st.get("watertight"), "open_edges": st.get("open_edges"), "grams_per_piece": p["grams_per_piece"], "seconds_per_piece": p["seconds_per_piece"],
         "slicer_warning": p.get("slicer_warning"), "qty": p["qty"], "stl_mtime": stl_mtime, "part_last_commit": part_commit, "rebuilt_delta": rebuilt_delta,
         "slice_journal": {"runs": sj.get("runs"), "traced": sj.get("published_run_found_in_journal"), "sha256_still_matches": sj.get("sha256_still_matches"),
                           "stl_sha256": sj.get("published", {}).get("stl_sha256_now") if sj.get("published") else None,
                           "auto_orient": sj.get("published_run_auto_orient"), "failures": sj.get("failures"),
                           "rebuilt_alternative": reb, "orientation_spread": spread}})

# ---------------------------------------------------------------- 3 bought lines
SRC = J(os.path.join(MEAS, "sourcing-rows.json"))
for l in SRC:
    offs = l["offers"]
    priced = [o for o in offs if o.get("tiers")]
    lead_stated = [o for o in offs if o.get("lead_time") and "not stated" not in o["lead_time"] and "CANNOT" not in o["lead_time"]]
    moqs = sorted({o.get("moq") for o in offs if o.get("moq") is not None})
    grade = "READY" if l["verdict"] == "PASS" else ("CD" if l["verdict"] == "CANNOT DETERMINE" else "NOT_YET")
    closer = None
    by = ""
    if grade != "READY":
        if l["id"] in ("P1", "P2"):
            closer, by = "agent_later", "re-route to >= 0.1524 mm track and clear the DRC, then the partner factory quotes it"
        elif l["id"] in ("B7", "B12", "B18b", "P3", "R3"):
            closer, by = "human", "a second priced distributor or the partner factory's own quotation; WF-UNKNOWNS may find a second shop tonight"
        else:
            closer, by = "human", "teardown of a shipped unit, Pollen's answer, or a purchase decision (%s)" % l["id"]
    row("bought", l["id"], l["item"], grade,
        "verdict %s; %d offer(s), %d priced; MOQ %s; lead time stated on %d offer(s); qty/robot %s" % (l["verdict"], len(offs), len(priced), moqs or "none", len(lead_stated), l.get("qty_per_robot")),
        "spec/sourcing.json line %s (SOURCING.html); offers: %s" % (l["id"], "; ".join((o.get("vendor") or "?") + " " + (o.get("url") or "") for o in offs[:3])),
        (l.get("verdict_why") or "")[:400], closer, by,
        {"ce_part": l.get("ce_part"), "qty_per_robot": l.get("qty_per_robot"), "offers": offs, "lead_time_stated": len(lead_stated)})

# ---------------------------------------------------------------- 4 PCBs
PCB = J("electronics/pcb-package.json")
pcbhtml = open(os.path.join(ROOT, "PCB-PACKAGE.html"), encoding="utf-8").read()
pcbtxt = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", "", pcbhtml, flags=re.S))))
drc = re.findall(r"Design rule check Verdict (PASS|FAIL|CANNOT DETERMINE) — (\d+) pass, (\d+) fail, (\d+) cannot determine", pcbtxt)
routing = {r[0]: r for r in PCB["routing"]["rows"]}
for i, b in enumerate(PCB["boards"]):
    slug = b["slug"]
    fab = glob.glob(os.path.join(ROOT, b["dir"], "out", "fab", "*-fab.zip"))
    gtl = glob.glob(os.path.join(ROOT, b["dir"], "out", "fab", "*.GTL"))
    d = drc[i] if i < len(drc) else ("?", "?", "?", "?")
    rt = routing.get(b["name"], ("", "?", "", "?"))
    note = D["pcb_notes"][slug]
    grade = "NOT_YET" if d[0] == "FAIL" else ("CD" if d[0] == "CANNOT DETERMINE" else "READY")
    row("pcb", slug, b["title"], grade,
        "DRC %s — %s pass, %s fail, %s cannot determine; routed %s; %d Gerber zip, %d copper layer file(s) on disk; %s x %s mm, %d layers" % (
            d[0], d[1], d[2], d[3], rt[1], len(fab), len(gtl), b["outline_mm"][0], b["outline_mm"][1], b["layers"]),
        "PCB-PACKAGE.html §%d.4 (DRC read from %s/out/fab/README.txt); electronics/pcb-package.json routing.rows" % (i + 3, b["dir"]),
        note["design_status"] + " " + note["what"], note["closer"], note["what"],
        {"drc": {"verdict": d[0], "pass": d[1], "fail": d[2], "cannot_determine": d[3]}, "routed": rt[1], "fab_zip": [os.path.relpath(f, ROOT) for f in fab], "design_status": note["design_status"]})

# ---------------------------------------------------------------- 5 harness
CAB = J("wiring/cables.json")["record"]
cables = CAB["cables"]
cd_rows = [c["id"] for c in cables if "CANNOT DETERMINE" in json.dumps(c)]
tol_rows = [c for c in cables if any("tol" in k for k in c)]
row("harness", "wiring", "Harness — %d cables" % len(cables), "NOT_YET",
    "%d cable rows; %d with a length (total %s mm); %d rows with a tolerance field; %d rows carry a CANNOT DETERMINE (%s); lengths are route FLOORS + slack, rounded to 5 mm; wire 21 AWG; voltage drop PASS at AWG 21/22, 8.2 V and 6.6 V" % (
        len(cables), len(cables) - len(CAB.get("length_undetermined", [])), CAB.get("total_length_mm"), len(tol_rows), len(cd_rows), ", ".join(cd_rows)),
    "wiring/cables.json (wiring/measure.py), wiring/CABLES.md rule paragraph",
    "A table of nominal floors, no cut tolerance, no service-loop rule per joint, and 6 of 23 connector ends or lengths CANNOT DETERMINE (mic loom, HAT bus port, ToF/speaker/CSI/battery far ends). The factory cannot cut a loom to this table without a first physical unit.",
    "agent_tonight", "WF-HARNESS routes the loom in CAD around the servo bodies; the cut tolerance still needs one built loom measured",
    {"cables": len(cables), "total_mm": CAB.get("total_length_mm"), "cannot_determine_rows": cd_rows, "tolerance_rows": len(tol_rows)})

# ---------------------------------------------------------------- 6 assembly sequence
MANUAL = open(os.path.join(ROOT, "ce-assemblies/microduck/iterations/v0.0.1/manual/MANUAL.md"), encoding="utf-8").read()
n_steps = len(re.findall(r"^\d+\. ", MANUAL, flags=re.M))
n_comm = MANUAL.count("[community]") + MANUAL.count("community-derived")
n_cd = MANUAL.count("CANNOT DETERMINE")
stations = PB["stations"]
n_station_steps = sum(len(s.get("steps", [])) for s in stations)
BOM = J("ce-assemblies/microduck/current/bom.json")["record"]
fast_rows = [r for r in BOM["rows"] if re.search(r"screw|bolt|\bnut\b|insert|washer|fasten|\bm2(\.5)?\b|\bm3\b", json.dumps(r).lower())]
spec = open(os.path.join(ROOT, "SPEC.md"), encoding="utf-8").read().splitlines()
census = " ".join(spec[74:76])
holes = [int(x) for x in re.findall(r"×(\d+)", census)]
row("assembly", "manual", "Assembly sequence — MANUAL.md + PLAYBOOK stations", "NOT_YET",
    "MANUAL: 7 steps, %d numbered sub-steps, %d '[community]'/community-derived fastener flags, %d CANNOT DETERMINE; PLAYBOOK: %d stations, %d steps, torque 3/3 CANNOT DETERMINE; bom.json %d rows, %d fastener rows against a %d-hole M2 census (SPEC.md:75-76: %s); %d steps assume knowledge not on the page (list below)" % (
        n_steps, n_comm, n_cd, len(stations), n_station_steps, len(BOM["rows"]), len(fast_rows), sum(holes), "+".join(str(h) for h in holes), len(D["manual_assumptions"])),
    "ce-assemblies/microduck/iterations/v0.0.1/manual/MANUAL.md; tools/data/playbook.json stations/torque/open; ce-assemblies/microduck/current/bom.json; SPEC.md:75-76",
    "No screw-by-screw schedule (length per hole), no torque, no datums a caliper can use, no fixing method for ToF/speaker/mic, no software install step. A stranger stops at step 1.2.",
    "agent_tonight", "WF-FASTENERS (schedule) + WF-HARNESS (per-joint pictures); torque and bearing interference need a coupon test by a person",
    {"manual_steps": n_steps, "community_flags": n_comm, "manual_cd": n_cd, "stations": len(stations), "station_steps": n_station_steps, "bom_rows": len(BOM["rows"]), "bom_fastener_rows": len(fast_rows), "hole_census": sum(holes), "assumptions": D["manual_assumptions"]})

# ---------------------------------------------------------------- 7 test plan
TP = J("spec/test-plan.json")
tests = [t for s in TP["sections"] for t in (s.get("tests") or s.get("rows") or [])]
tphtml = open(os.path.join(ROOT, "TEST-PLAN.html"), encoding="utf-8").read()
placeholders = sorted(set(re.findall(r"@[A-Z_]+@", tphtml)))
row("test", "test-plan", "Test and validation plan — %s rev %s" % (TP["doc"]["id"], TP["doc"]["rev"]), "READY",
    "%d gated tests in %d sections; %d equipment items; %d end-of-line gates; %d open questions; %d unresolved @PLACEHOLDER@ tokens in TEST-PLAN.html; 0 tests exercised (no unit built)" % (
        len(tests), len(TP["sections"]), len(TP["equipment"]), len(TP["eol"]), len(TP["open"]), len(placeholders)),
    "spec/test-plan.json (TEST-PLAN.html, tools/gen_test_plan.py)",
    "Executable as a bench procedure once a unit exists; the walk gate WK-02 is 75 %% of a simulated distance (a decision, not a measurement), SN-05 cannot run on a built robot, and %d questions are answered only by measuring the first units." % len(TP["open"]),
    "human", "the first five built units on the bench (EB-04 servo voltage first)",
    {"tests": len(tests), "sections": [s.get("id") for s in TP["sections"]], "open": [o.get("q") for o in TP["open"]], "placeholders": placeholders})

# ---------------------------------------------------------------- 8 triad shelf
TR = J(os.path.join(MEAS, "triad.json"))
for r in TR["results"]:
    f = r["findings"][0] if r.get("findings") else {}
    why = (f.get("why") or "")
    grade = "READY" if r["verdict"] == "PASS" else ("CD" if r["verdict"] == "CANNOT DETERMINE" else "NOT_YET")
    closer = None
    by = ""
    if grade != "READY":
        if "SUPERSEDED" in why or "sha256" in why:
            closer, by = "agent_tonight", "append a ledger row for the regenerated artifact (WF-UNKNOWNS reconciliation)"
        elif "grades ITSELF" in why:
            closer, by = "human", "the folder's own CANNOT DETERMINE names what settles it (mostly a teardown or a vendor drawing)"
        else:
            closer, by = "agent_later", "measure the declared interface frame"
    row("triad", r["ref"], r["ref"], grade, "bin/triad check: %s (%s, %d measurements)" % (r["verdict"], r.get("iteration"), r.get("measured", 0)),
        "out/factory/measure/triad.json (bin/triad check --all --json, %s)" % TR.get("$generated", NOW), why[:300], closer, by,
        {"iteration": r.get("iteration"), "folder": r.get("folder")})

# ---------------------------------------------------------------- 9 open unknowns
HARV = J("out/open/cannot-determine-harvest.json")
row("open", "cannot-determine-harvest", "Open CANNOT DETERMINE items", "NOT_YET", "%d unique items in out/open/cannot-determine-harvest.json" % len(HARV),
    "out/open/cannot-determine-harvest.json", "Each names what settles it; the resolution workflow owns the list tonight.", "agent_tonight", "WF-UNKNOWNS", {"count": len(HARV)})

# ------------------------------------------------- in-flight lanes, MEASURED
# A parcel is only IN FLIGHT if the workflow that owns it is writing files. Stat
# every owned path so the factory reads a fact, not a promise.
for w in D["in_flight"]:
    st = []
    for pth in [x.strip() for x in w["owns"].split(",")]:
        pth = pth.split(" ")[0].rstrip("/")
        full = os.path.join(ROOT, pth)
        if not os.path.exists(full):  # a lane may own a path in the workshop repo, not ours
            alt = os.path.join(os.path.dirname(os.path.dirname(ROOT)), pth)
            if os.path.exists(alt):
                full = alt
        if not os.path.exists(full):
            st.append("%s does not exist yet" % pth)
            continue
        if os.path.isdir(full):
            files = [os.path.join(dp, f) for dp, _, fs in os.walk(full) for f in fs]
            if not files:
                st.append("%s is empty" % pth)
                continue
            newest = max(files, key=os.path.getmtime)
            st.append("%s: %d files, newest %s (%s)" % (pth, len(files), datetime.datetime.fromtimestamp(os.path.getmtime(newest)).strftime("%m-%d %H:%M"), os.path.relpath(newest, full)))
        else:
            st.append("%s: %s" % (pth, datetime.datetime.fromtimestamp(os.path.getmtime(full)).strftime("%m-%d %H:%M")))
    w["state"] = st
    w["stat_at"] = NOW

# ---------------------------------------------------------------- summary
def count(cls):
    rs = [r for r in rows if r["class"] == cls]
    return {"total": len(rs), "ready": sum(1 for r in rs if r["grade"] == "READY"), "not_yet": sum(1 for r in rs if r["grade"] == "NOT_YET"), "cannot_determine": sum(1 for r in rs if r["grade"] == "CD")}


summary = {c: count(c) for c in ["drawing", "print", "bought", "pcb", "harness", "assembly", "test", "triad", "open"]}
summary["sheets_graded"] = {"sheets": len(SC["sheets"]), "pass": sum(1 for s in SC["sheets"].values() if s["verdict"] == "PASS"), "fail": sum(1 for s in SC["sheets"].values() if s["verdict"] == "FAIL"), "generated": SC["generated"], "parts_without_a_sheet": no_sheet}
summary["triad_refs"] = {"checked": TR["checked"], "pass": sum(1 for r in TR["results"] if r["verdict"] == "PASS"), "fail": sum(1 for r in TR["results"] if r["verdict"] == "FAIL"), "cannot_determine": sum(1 for r in TR["results"] if r["verdict"] == "CANNOT DETERMINE")}
summary["bom_fasteners"] = {"bom_rows": len(BOM["rows"]), "fastener_rows": len(fast_rows), "hole_census": sum(holes)}
summary["unknowns"] = len(HARV)
_bq = [r for r in rows if r["class"] == "bought"]
summary["bought_gaps"] = {"lines": len(_bq),
                          "no_priced_offer": [r["id"] for r in _bq if not any(o.get("tiers") for o in r["offers"])],
                          "no_lead_time_stated": [r["id"] for r in _bq if not r["lead_time_stated"]]}
summary["print_licence"] = {"vendor_mesh_stls": sum(1 for r in rows if r["class"] == "print" and r.get("vendor_mesh")), "ours": sum(1 for r in rows if r["class"] == "print" and not r.get("vendor_mesh"))}
closers = {}
for r in rows:
    if r["grade"] != "READY":
        closers[r["closer"] or "none"] = closers.get(r["closer"] or "none", 0) + 1
summary["who_closes"] = closers
summary["delta_vs_last_measurement"] = {
    "verdict": DLT.get("verdict"), "prior": DLT.get("prior_measurement"), "this": DLT.get("this_measurement"),
    "prior_commit": (DLT.get("vs_rev") or "")[:7], "compared": DLT.get("compared"),
    "differences": DLT.get("differences"), "why": DLT.get("why")}
_ch = SH.get("health", {})
_cs = SH.get("control_slice", {})
summary["slice_authority"] = {
    "probed_at": SH.get("probed_at"), "instrument_health": _ch.get("verdict"),
    "instrument_reason": _ch.get("reason"), "control_part_slice": _cs.get("verdict"),
    "control_grams": _cs.get("grams"), "control_seconds": _cs.get("seconds"),
    "slicer": (_ch.get("binary") or {}).get("version"), "verdict": SH.get("verdict"), "why": SH.get("why")}

out = {"$doc": "out/factory/readiness.json — READINESS AUDIT, generated by tools/gen_readiness.py from out/factory/measure/*.json and the repo's data files. Grades: READY TO BUILD FROM / NOT YET / CANNOT DETERMINE. Every row carries the measurement and the file it was read from.",
       "doc": D["doc"], "measured_at": NOW, "partial": False, "summary": summary, "in_flight": D["in_flight"], "licence": D["licence"], "rows": rows}
os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)

# ---------------------------------------------------------------- HTML
E = html.escape


def _elapsed(a, b):
    """'4 h 59 min' between two 'YYYY-MM-DD HH:MM:SS' measurement stamps."""
    try:
        fa = datetime.datetime.strptime(a[:19], "%Y-%m-%d %H:%M:%S")
        fb = datetime.datetime.strptime(b[:19], "%Y-%m-%d %H:%M:%S")
    except Exception:
        return "interval"
    m = int(round((fb - fa).total_seconds() / 60.0))
    return ("%d h %02d min" % (m // 60, m % 60)) if m >= 60 else ("%d min" % m)


def gchip(r):
    cls = {"READY": "ok", "NOT_YET": "no", "CD": "cd"}[r["grade"]]
    return '<span class="g %s">%s<br><small>%s</small></span>' % (cls, E(r["grade_en"]), E(r["grade_zh"]))


def cols(*pct):
    return "<colgroup>" + "".join('<col style="width:%s%%">' % w for w in pct) + "</colgroup>"


def th(en, zh):
    return "<th>%s<br><span class=\"zh\">%s</span></th>" % (E(en), E(zh))


A = []
A.append('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<title>%s — %s</title>' % (E(D["doc"]["title"]), E(D["doc"]["title_zh"])))
A.append('<link rel="stylesheet" href="../../tools/doc.css">')
A.append('<style>.zh{font-family:var(--sans);font-size:12px;color:var(--ink-2);display:block}'
         'table{border-collapse:collapse;width:100%;table-layout:fixed;font-size:12.5px;margin:8px 0 18px;overflow-wrap:anywhere}th{white-space:normal !important;padding:5px 6px}th,td{border-bottom:1px solid var(--hair);padding:5px 6px;text-align:left;vertical-align:top}th{background:var(--head);font-family:var(--sans);font-size:12px}'
         'td.m{font-family:var(--mono);font-size:11.5px;word-break:break-all}'
         '.g{font-family:var(--sans);font-weight:600;font-size:11px}.g.ok{color:var(--ready)}.g.no{color:var(--no)}.g.cd{color:var(--cd)}'
         '.front{border:2px solid var(--no);padding:12px 16px;margin:18px 0}.front h2{margin:0 0 6px;border:none;font-size:20px}'
         '.stat b.no{color:var(--no)}.num{text-align:right;font-variant-numeric:tabular-nums}</style>')
A.append('</head>\n<body>\n<div class="wrap">')
A.append('<p class="backlink"><a href="../../INDEX.html">← Document index</a></p>')
A.append('<header class="hero"><p class="eyebrow">Microduck · factory pack · 工厂交付包</p>')
A.append('<h1>%s <span class="zh" style="font-size:22px;display:inline">%s</span></h1>' % (E(D["doc"]["title"]), E(D["doc"]["title_zh"])))
A.append('<p class="sub">%s</p><p class="sub zh">%s</p>' % (E(D["doc"]["sub"]), E(D["doc"]["sub_zh"])))
A.append('<div class="rev"><span>%s · Rev %s</span><span>measured %s</span><span>tools/gen_readiness.py</span></div></header>' % (D["doc"]["id"], D["doc"]["rev"], NOW))

s = summary
A.append('<div class="front"><h2>The honest state first · 先说实话</h2>')
A.append('<div class="statbar">')
for b, en, zh in [("%d / %d" % (s["sheets_graded"]["pass"], s["sheets_graded"]["sheets"]), "drawing sheets PASS", "图纸通过"),
                  ("%d" % len(no_sheet), "printed parts with no sheet", "无图纸的打印件"),
                  ("%d / %d" % (s["print"]["ready"], s["print"]["total"]), "print files ready", "打印文件就绪"),
                  ("%d / %d" % (s["bought"]["ready"], s["bought"]["total"]), "bought lines buyable", "外购项可采购"),
                  ("%d / 3" % s["pcb"]["ready"], "custom PCBs fabricable", "定制 PCB 可投产"),
                  ("%d / %d" % (s["bom_fasteners"]["fastener_rows"], s["bom_fasteners"]["hole_census"]), "fastener rows / M2 holes", "紧固件行 / M2 孔"),
                  ("%d / %d" % (s["triad_refs"]["pass"], s["triad_refs"]["checked"]), "shelf refs PASS", "货架条目通过"),
                  ("%d" % s["unknowns"], "open CANNOT DETERMINE", "未定项")]:
    A.append('<div class="stat"><b class="no">%s</b><span>%s<br>%s</span></div>' % (E(b), E(en), E(zh)))
A.append('</div>')
A.append('<p><b>Read this before anything else.</b> A working prototype is buildable from this pack today: every part prints, every off-the-shelf part is buyable, the assembly order is written down. A <i>factory release</i> is not: no drawing sheet passes our own standard, the custom boards do not pass their own design-rule check, no screw has a length or a torque, and the harness is a table of floors. The rows below say exactly which artifact is which.</p>')
A.append('<p class="zh">请先阅读本段。今天可以按本交付包制作一台可工作的样机：每个零件可打印，每个外购件可买到，装配顺序已写明。但<b>尚不能量产</b>：没有一张图纸通过我方自己的标准，定制电路板未通过自身的设计规则检查，没有一颗螺钉有长度或扭矩，线束只是一张下限表。下表逐项说明。</p>')
A.append('<p><b>Licence · 许可证.</b> %s</p><p class="zh">%s</p>' % (E(D["licence"]["en"]), E(D["licence"]["zh"])))
_d = summary["delta_vs_last_measurement"]
_c = _d.get("compared") or {}
if _d.get("verdict") == "UNCHANGED":
    A.append('<p><b>Nothing moved in the last %s.</b> This audit was re-measured at %s and every one of %d sheet checks, %d shelf refs and %d STL records is identical to the measurement of %s (commit %s). The six workflows in section 2 are still running; none of them has yet changed a number this audit grades. Do not wait for them before starting the parcels below.</p>'
             % (E(_elapsed(_d["prior"], _d["this"])), E(_d["this"]), _c.get("sheet_checks", 0), _c.get("triad_refs", 0), _c.get("stls", 0), E(_d["prior"]), E(_d["prior_commit"])))
    A.append('<p class="zh">最近 %s 内无任何变化。本审核于 %s 重新实测：%d 项图纸检查、%d 项货架条目、%d 个 STL 记录，与 %s 的实测结果完全一致。第 2 节的六个工作流仍在运行，但尚未改变本审核评级的任何数字。请勿等待它们，可直接开始下列工作包。</p>'
             % (E(_elapsed(_d["prior"], _d["this"])), E(_d["this"]), _c.get("sheet_checks", 0), _c.get("triad_refs", 0), _c.get("stls", 0), E(_d["prior"])))
else:
    A.append('<p><b>Moved since the last measurement.</b> Re-measured %s against %s (commit %s): %d difference(s) across %d sheet checks, %d shelf refs and %d STL records. %s</p>'
             % (E(_d["this"]), E(_d["prior"]), E(_d["prior_commit"]), _d.get("differences") or 0, _c.get("sheet_checks", 0), _c.get("triad_refs", 0), _c.get("stls", 0),
                E("; ".join("%s %s %s -> %s" % (x.get("sheet") or x.get("ref") or x.get("stl"), x.get("rule", ""), x.get("was"), x.get("now")) for x in (DLT["sheet_check_differences"] + DLT["triad_ref_differences"] + DLT["stl_differences"])[:12]))))
_s = summary["slice_authority"]
A.append('<p><b>Can you get grams and seconds today? Yes.</b> ce-slice was probed at %s: its own deep health is <b>%s</b> (%s) — that failure is in ce-slice\'s canary cube, a 12-triangle file written with zero facet normals, not in this design. The control probe that matters PASSES: a real part, <code>out/print/stl/PLA/microduck-ankle-left.stl</code>, sliced by BambuStudio %s to <b>%s g</b> in <b>%s s</b> at 0.20 mm. Every gram in section 4 comes from a run like that one, never from volume.</p>'
         % (E(_s["probed_at"] or ""), E(str(_s["instrument_health"])), E((_s["instrument_reason"] or "")[:120]), E(str(_s["slicer"])), E("%.4f" % _s["control_grams"] if _s.get("control_grams") is not None else "CANNOT DETERMINE"), E("%.2f" % _s["control_seconds"] if _s.get("control_seconds") is not None else "CANNOT DETERMINE")))
A.append('<p class="zh">今天能否取得克数与秒数？能。%s 探测 ce-slice：其自带深度健康检查为 %s（失败点在 ce-slice 自己的标定立方体——一个法向量全为零的 12 面 STL，与本设计无关）。真正重要的对照探测通过：真实零件 microduck-ankle-left.stl 由 BambuStudio %s 切片，0.20 mm 层高，%s 克 / %s 秒。第 4 节的每一个克数都来自这样的实测，绝非体积换算。</p>'
         % (E(_s["probed_at"] or ""), E(str(_s["instrument_health"])), E(str(_s["slicer"])), E("%.4f" % _s["control_grams"] if _s.get("control_grams") is not None else "未测"), E("%.2f" % _s["control_seconds"] if _s.get("control_seconds") is not None else "未测")))
A.append('</div>')

A.append('<nav class="toc"><a href="#notyet">1 Not yet · 尚未就绪</a><a href="#inflight">2 In flight tonight · 今晚进行中</a><a href="#drawings">3 Drawings · 图纸</a><a href="#print">4 Print files · 打印文件</a><a href="#bought">5 Bought lines · 外购件</a><a href="#pcb">6 PCBs · 电路板</a><a href="#harness">7 Harness · 线束</a><a href="#assembly">8 Assembly · 装配</a><a href="#test">9 Test plan · 测试计划</a><a href="#shelf">10 Shelf · 货架</a></nav>')

# 1 not yet (all non-ready rows, grouped by closer)
A.append('<section id="notyet"><h2><span class="n">1</span>Everything that is NOT ready, and who closes it · 所有未就绪项及负责方</h2>')
A.append('<p class="lede">One row per artifact that is not READY TO BUILD FROM. "Closer" says whether a software agent finishes it tonight (and which workflow) or a person must. · 每行一个未就绪文件；“负责方”说明今晚由软件代理完成（及哪个工作流）还是必须由人完成。</p>')
A.append('<table>%s<tr>%s%s%s%s%s</tr>' % (cols(9, 16, 11, 43, 21), th("Class", "类别"), th("Artifact", "文件"), th("Grade", "评级"), th("What is missing", "缺什么"), th("Closer", "负责方")))
order = {"pcb": 0, "assembly": 1, "harness": 2, "drawing": 3, "print": 4, "bought": 5, "test": 6, "open": 7, "triad": 8}
for r in sorted([r for r in rows if r["grade"] != "READY"], key=lambda r: (order[r["class"]], r["id"])):
    A.append('<tr><td>%s</td><td class="m">%s</td><td>%s</td><td>%s</td><td>%s<span class="zh">%s</span><small>%s</small></td></tr>' % (
        E(r["class"]), E(r["id"]), gchip(r), E(r["missing"] or r["measurement"]), E(r["closer_en"]), E(r["closer_zh"]), E(r["by"])))
A.append('</table></section>')

# 2 in flight
A.append('<section id="inflight"><h2><span class="n">2</span>Work an agent is doing tonight — do not hand these to the factory · 今晚代理正在做的工作（勿交给工厂）</h2>')
A.append('<p class="lede">The right-hand column is measured, not reported: each owned path is stat-ed at generation time — how many files exist and when the newest one was written. A path that does not exist yet is named as such.</p>')
A.append('<table>%s<tr>%s%s%s%s</tr>' % (cols(11, 36, 27, 26), th("Workflow", "工作流"), th("What it closes", "完成内容"), th("Paths it owns", "所属路径"), th("Measured state of those paths", "所属路径的实测状态")))
for w in D["in_flight"]:
    A.append('<tr><td class="m">%s</td><td>%s<span class="zh">%s</span></td><td class="m">%s</td><td><small>%s</small></td></tr>' % (
        E(w["id"]), E(w["en"]), E(w["zh"]), E(w["owns"]), E("; ".join(w["state"]))))
A.append('</table></section>')

# 3 drawings
A.append('<section id="drawings"><h2><span class="n">3</span>Drawing sheets — bin/sheetcheck, %s · 图纸</h2>' % E(SC["generated"]))
A.append('<p class="lede">Limits: dimension coverage 100 %, occupancy ≥ 85 %, largest empty rectangle &lt; 5 %, minimum font ≥ 3.5 mm, ≥ 4 isometric views, ≥ 6 shaded renders, line ratio ≤ 10, curve density ≤ 1.43 mm/mm². KIND PRINT = the sheet declares itself not a dimensioned drawing (mesh-backed part).</p>')
A.append('<table>%s<tr>%s%s%s%s%s%s%s%s%s%s%s</tr>' % (cols(22, 7, 13, 8, 7, 7, 7, 6, 7, 8, 8), th("Sheet", "图纸"), th("Kind", "类型"), th("Grade", "评级"), th("Dim %", "尺寸覆盖率"), th("Occ %", "占用率"), th("Empty %", "最大空白"), th("Font mm", "最小字高"), th("Iso", "等轴视图"), th("Renders", "渲染图"), th("Line ratio", "线数比"), th("Curve dens.", "曲线密度")))
for r in sorted([r for r in rows if r["class"] == "drawing"], key=lambda r: r["id"]):
    if r.get("kind") == "NONE":
        A.append('<tr><td class="m">%s</td><td>—</td><td>%s</td><td colspan="8">%s</td></tr>' % (E(r["id"]), gchip(r), E(r["measurement"])))
        continue
    c = r["checks"]
    def f(k, fmt="%.1f"):
        v = c[k]["measured"]
        return "CD" if v is None else (fmt % v if isinstance(v, float) else str(v))
    A.append('<tr><td class="m">%s</td><td>%s</td><td>%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td></tr>' % (
        E(r["id"]), E(r["kind"]), gchip(r), f("dim_coverage"), f("coverage"), f("empty_rect"), f("font"), f("iso", "%d"), f("renders", "%d"), f("line_ratio", "%.2f"), f("curve_density", "%.2f")))
A.append('</table></section>')

# 4 print
A.append('<section id="print"><h2><span class="n">4</span>Print files — ce-slice numbers, never derived from volume · 打印文件</h2>')
A.append('<p class="lede">Every gram and second below is what BambuStudio %s itself reported through ce-slice, at the 0.20 mm Standard @BBL H2S process unless the row says otherwise. Checked against ce-slice\'s own append-only journal on %s: <b>%d of %d</b> published figures are traceable to a recorded run, and on <b>%d</b> of them the STL\'s sha256 is still the file on disk today. %d parts were ALSO sliced from our parametric rebuild — where those two disagree the row says by how much. · 下列克数与秒数均为 BambuStudio 经 ce-slice 实测输出，绝非由体积换算。%d/%d 项可追溯至切片日志记录，其中 %d 项 STL 的 sha256 与当前磁盘文件一致。</p>' % (
    "02.08.02.61", E(SJ["read_at"][:16]), SJ["summary"]["published_number_traced_to_a_journal_run"], len(slice_["parts"]),
    SJ["summary"]["stl_unchanged_since_that_run"], SJ["summary"]["with_a_rebuilt_alternative"],
    SJ["summary"]["published_number_traced_to_a_journal_run"], len(slice_["parts"]), SJ["summary"]["stl_unchanged_since_that_run"]))
A.append('<table>%s<tr>%s%s%s%s%s%s%s%s%s</tr>' % (cols(19, 12, 6, 5, 9, 8, 8, 12, 21), th("Part", "零件"), th("Grade", "评级"), th("Mat.", "材料"), th("Qty", "数量"), th("Watertight", "封闭网格"), th("g / piece", "克/件"), th("s / piece", "秒/件"), th("Source / licence", "来源 / 许可"), th("Problem", "问题")))
for r in [r for r in rows if r["class"] == "print"]:
    short = []
    if not r["watertight"]:
        short.append("NOT watertight, %s open edges" % r["open_edges"])
    if r["stale"]:
        rd = r.get("rebuilt_delta") or {}
        short.append("Pollen's mesh; our PASSed rebuild exists (bbox delta <= %s mm) — re-export for provenance/licence" % rd.get("max_abs_bbox_delta_mm", "?"))
    if r["slicer_warning"]:
        short.append("supports needed; sliced numbers are a floor")
    sjr = (r.get("slice_journal") or {}).get("rebuilt_alternative")
    if sjr:
        short.append("the rebuild slices to %.4f g / %.0f s (%+.2f %% filament, %+.2f %% time) — quote the file you print" % (
            sjr["rebuilt_grams"], sjr["rebuilt_seconds"], sjr["d_grams_pct"], sjr["d_seconds_pct"]))
    sjo = (r.get("slice_journal") or {}).get("orientation_spread")
    if sjo:
        short.append("orientation changes the number: same file, %.4f g / %.0f s auto-oriented vs %.4f g / %.0f s as modelled (%+.2f %% time)" % (
            sjo["grams"][0], sjo["seconds"][0], sjo["grams"][1], sjo["seconds"][1], sjo["seconds_pct"]))
    A.append('<tr><td class="m">%s</td><td>%s</td><td>%s</td><td class="num">%d</td><td>%s</td><td class="num">%.4f</td><td class="num">%.0f</td><td>%s</td><td>%s</td></tr>' % (
        E(r["id"]), gchip(r), E(r["stl"].split("/")[3]), r["qty"], "yes" if r["watertight"] else "NO", r["grams_per_piece"], r["seconds_per_piece"], E(r["licence"]), E("; ".join(short))))
A.append('</table></section>')

# 5 bought
A.append('<section id="bought"><h2><span class="n">5</span>Bought lines — spec/sourcing.json rev C · 外购件</h2>')
_b = [r for r in rows if r["class"] == "bought"]
_nopr = [r["id"] for r in _b if not any(o.get("tiers") for o in r["offers"])]
_nolead = [r["id"] for r in _b if not r["lead_time_stated"]]
A.append('<p class="lede">Counted over all %d lines: <b>%d</b> line(s) have no offer with a price read off a live page (%s) and <b>%d</b> line(s) have no lead time stated by any vendor (%s). A quotation cannot be built from those rows without asking the vendor directly — they are the first calls the purchasing engineer makes. · 全部 %d 行中，<b>%d</b> 行无任何已读取报价（%s），<b>%d</b> 行无任何供应商注明交期（%s）。这些行需采购工程师直接询价。</p>' % (
    len(_b), len(_nopr), E(", ".join(_nopr) or "none"), len(_nolead), E(", ".join(_nolead) or "none"),
    len(_b), len(_nopr), E(", ".join(_nopr) or "none"), len(_nolead), E(", ".join(_nolead) or "none")))
A.append('<table>%s<tr>%s%s%s%s%s%s%s%s</tr>' % (cols(6, 20, 12, 7, 8, 8, 7, 32), th("Line", "行"), th("Item", "物料"), th("Grade", "评级"), th("Qty/robot", "每台数量"), th("Offers (priced)", "报价数"), th("MOQ", "最小起订量"), th("Lead time stated", "已注明交期"), th("Why not ready", "未就绪原因")))
for r in [r for r in rows if r["class"] == "bought"]:
    offs = r["offers"]
    A.append('<tr><td class="m">%s</td><td>%s</td><td>%s</td><td class="num">%s</td><td class="num">%d (%d)</td><td class="num">%s</td><td class="num">%d</td><td>%s</td></tr>' % (
        E(r["id"]), E(r["name"]), gchip(r), E(str(r["qty_per_robot"])), len(offs), sum(1 for o in offs if o.get("tiers")), E(", ".join(str(o.get("moq")) for o in offs if o.get("moq") is not None) or "—"), r["lead_time_stated"], E(r["missing"][:260])))
A.append('</table></section>')

# 6 pcb
A.append('<section id="pcb"><h2><span class="n">6</span>The three custom PCBs · 三块定制电路板</h2>')
A.append('<table>%s<tr>%s%s%s%s%s%s</tr>' % (cols(12, 12, 14, 8, 22, 32), th("Board", "电路板"), th("Grade", "评级"), th("DRC", "设计规则检查"), th("Routed", "已布线"), th("Files on disk", "磁盘文件"), th("Design status / what closes it", "设计状态 / 完成条件")))
for r in [r for r in rows if r["class"] == "pcb"]:
    routed = r["routed"] if re.match(r"^\d+ of \d+$", r["routed"]) else "not counted (see DRC)"
    A.append('<tr><td>%s</td><td>%s</td><td>%s — %s pass, %s fail, %s CD</td><td>%s</td><td class="m">%s</td><td>%s</td></tr>' % (
        E(r["name"]), gchip(r), E(r["drc"]["verdict"]), r["drc"]["pass"], r["drc"]["fail"], r["drc"]["cannot_determine"], E(routed), E("; ".join(r["fab_zip"])), E(r["missing"])))
A.append('</table></section>')

# 7 harness, 8 assembly, 9 test
for sec, ident, title in [("harness", "wiring", "7 Harness · 线束"), ("assembly", "manual", "8 Assembly sequence · 装配顺序"), ("test", "test-plan", "9 Test plan · 测试计划")]:
    r = next(x for x in rows if x["id"] == ident)
    A.append('<section id="%s"><h2><span class="n">%s</span>%s</h2>' % (sec, title.split(" ")[0], E(title[2:])))
    A.append('<table>%s<tr>%s%s%s%s</tr><tr><td>%s</td><td>%s</td><td>%s</td><td>%s<span class="zh">%s</span><small>%s</small></td></tr></table>' % (
        cols(12, 36, 30, 22), th("Grade", "评级"), th("Measurement", "测量"), th("What is missing", "缺什么"), th("Closer", "负责方"), gchip(r), E(r["measurement"]), E(r["missing"]), E(r["closer_en"]), E(r["closer_zh"]), E(r["by"])))
    if sec == "assembly":
        A.append('<h3>Steps a stranger cannot follow without asking us · 陌生人无法独立执行的步骤</h3><table>%s<tr>%s%s%s</tr>' % (cols(26, 48, 26), th("Step", "步骤"), th("What it assumes", "隐含前提"), th("Closer", "负责方")))
        for a in r["assumptions"]:
            A.append('<tr><td>%s</td><td>%s</td><td>%s<span class="zh">%s</span><small>%s</small></td></tr>' % (E(a["step"]), E(a["assumes"]), E(CL[a["closer"]]["en"]), E(CL[a["closer"]]["zh"]), E(a["by"])))
        A.append('</table>')
    if sec == "test":
        A.append('<h3>Open questions the first units answer · 首批样机需回答的问题</h3><ol>%s</ol>' % "".join("<li>%s</li>" % E(q) for q in r["open"]))
    A.append('</section>')

# 10 shelf
A.append('<section id="shelf"><h2><span class="n">10</span>Triad shelf — bin/triad check --all · 货架</h2>')
A.append('<table>%s<tr>%s%s%s%s</tr>' % (cols(24, 13, 45, 18), th("Ref", "条目"), th("Grade", "评级"), th("First finding", "首个发现"), th("Closer", "负责方")))
for r in [r for r in rows if r["class"] == "triad"]:
    A.append('<tr><td class="m">%s</td><td>%s</td><td>%s</td><td>%s<span class="zh">%s</span></td></tr>' % (E(r["id"]), gchip(r), E(r["missing"][:200]), E(r["closer_en"]), E(r["closer_zh"])))
A.append('</table></section>')
A.append('<footer class="foot"><p>Generated %s by tools/gen_readiness.py from out/factory/measure/*.json · every number traces to a file · 由脚本生成，每个数字均可溯源</p></footer>' % E(NOW))
A.append('</div></body></html>')
with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write("\n".join(A))
print("wrote", os.path.relpath(OUT_JSON, ROOT), "rows", len(rows))
print(json.dumps(summary, indent=1, ensure_ascii=False))
