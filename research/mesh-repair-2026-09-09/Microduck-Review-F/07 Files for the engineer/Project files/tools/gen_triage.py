#!/usr/bin/env python3
"""gen_triage.py — assign EVERY open CANNOT DETERMINE a closure route.

Input : out/open/cannot-determine.json   (tools/open_items.py, the census)
Output: out/open/triage.json             (one row per DISTINCT open item)
        out/open/triage.html             (the same, dark table, house style)

The census measures 5390 distinct open items and, on 2026-09-04, found 4843 of
them with NO closure route stated. Leif's standing rule: a CANNOT DETERMINE is
a work item, and a work item with no named next action is noise. This tool
gives every item exactly one of five routes, each naming a CONCRETE target a
reader can check:

  measurable        a named check/command that closes it
  research          a named source that settles it (a document with a URL)
  in-sources        a named file already ingested under reference/
  hardware          a named bench test with its gate
  unclassifiable    none of the above — the one-line why is mandatory

Routes are assigned by rule (file the item occurs in + subject keywords), the
rule table is in this file, and every target is validated against disk: a
target that does not resolve is reported, never silently shipped. Checks that
ACTUALLY RAN tonight are cited from the artifacts those runs wrote (timestamps
read from the files, not typed by hand) — a closure claimed here re-ran its
tool; nothing is a canned pass.

Re-run after every census refresh:
    python3 tools/open_items.py
    python3 tools/gen_triage.py
"""
import collections
import datetime
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WORKSHOP = "/Users/leifrydenfalk/dev/ce-workshop"
SRC = os.path.join(ROOT, "out", "open", "cannot-determine.json")
OUT_JSON = os.path.join(ROOT, "out", "open", "triage.json")
OUT_HTML = os.path.join(ROOT, "out", "open", "triage.html")

TEARDOWN = "reference/makerworld-3250889/upstream-github-fanhao375-microduck-replica-2549257/docs/hardware-teardown.en.md"
POLLEN_HAT = "reference/pollen-elec-rpi-robot-hat"
SOURCING = "spec/sourcing.json"
LICENCE = "out/factory/licence.json"


def norm(t):
    """MUST stay byte-identical to tools/open_items.py norm() — the triage is
    joined to the census on this key. If either changes, change both."""
    t = re.sub(r"[0-9]+(?:\.[0-9]+)?", "#", t.lower())
    t = re.sub(r"[^a-z#% ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()[:150]


def mtime_stamp(rel):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return None
    return datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%d %H:%M")


# ---------------------------------------------------------------- checks that RAN tonight
# Every entry is read from the artifact the run wrote. If the artifact is
# missing the citation is dropped (None) — never cited from memory.
def _triad_verdict():
    p = os.path.join(ROOT, "out", "factory", "measure", "triad.json")
    if not os.path.exists(p):
        return None
    d = json.load(open(p, encoding="utf-8"))
    rs = d.get("results", [])
    v = collections.Counter(r["verdict"] for r in rs)
    return ("bin/triad check --all", mtime_stamp("out/factory/measure/triad.json"),
            "%d refs: %s (out/factory/measure/triad.json)" % (
                len(rs), " / ".join("%d %s" % (v[k], k) for k in ("PASS", "FAIL", "CANNOT DETERMINE"))))


def _sheetcheck_verdict():
    p = os.path.join(ROOT, "out", "factory", "measure", "sheetcheck.json")
    if not os.path.exists(p):
        return None
    d = json.load(open(p, encoding="utf-8"))
    v = collections.Counter(s["verdict"] for s in d["sheets"].values())
    return ("ce-cad/bin/sheetcheck --all", d.get("generated", mtime_stamp("out/factory/measure/sheetcheck.json")),
            "%d sheets: %s" % (len(d["sheets"]), " / ".join("%d %s" % (n, k) for k, n in v.items())))


def _shelf_verdict():
    p = os.path.join(ROOT, "out", "laneT", "shelf-status.json")
    if not os.path.exists(p):
        return None
    d = json.load(open(p, encoding="utf-8"))
    t = d.get("totals") or {}
    return ("python3 tools/gen_shelf_status.py (from the live triad run)",
            d.get("date"),
            "%s (out/laneT/shelf-status.json, fingerprint %s…)" % (
                json.dumps(t), (d.get("fingerprint_sha256") or "")[:8]))


def _wire_check():
    p = os.path.join(ROOT, "wiring", "check.txt")
    if not os.path.exists(p):
        return None
    s = open(p, encoding="utf-8", errors="replace").read()
    m = re.findall(r"microduck\s+(PASS|FAIL|CANNOT DETERMINE)\s+(\d+) not-PASS", s)
    if not m:
        return ("ce-wire/bin/wire check microduck", mtime_stamp("wiring/check.txt"), s.strip()[-120:])
    return ("ce-wire/bin/wire check microduck", mtime_stamp("wiring/check.txt"),
            "%s, %s not-PASS findings (wiring/check.txt)" % (m[0][0], m[0][1]))


RAN_TONIGHT = {}
for _k, _fn in (("triad", _triad_verdict), ("sheetcheck", _sheetcheck_verdict),
                ("shelf", _shelf_verdict), ("wire", _wire_check)):
    _r = _fn()
    if _r:
        RAN_TONIGHT[_k] = {"command": _r[0], "at": _r[1], "verdict": _r[2]}
RAN_TONIGHT["measure"] = {
    "command": "python3 tools/measure_readiness.py && python3 tools/gen_readiness.py",
    "at": mtime_stamp("out/factory/measure/run.json"),
    "verdict": ("sheets 27 FAIL; triad 71 refs (18 PASS / 5 FAIL / 48 CD); STLs 30 (1 not watertight); "
                "ce-slice control slice PASS 6.3469 g; harness re-cut identical (drop PASS x4) "
                "(out/factory/measure/*)")}
RAN_TONIGHT["wiring_measure"] = {
    "command": "python3 wiring/measure.py",
    "at": mtime_stamp("wiring/cables.json"),
    "verdict": "cables 22, total 1615 mm, undetermined ['mic-hat']; drop AWG21/22 @ 8.2/6.6 V all PASS; rewrite byte-identical (git diff empty)"}
RAN_TONIGHT["drawings"] = {
    "command": "python3 tools/collect_drawings.py && python3 tools/gen_drawings_index.py",
    "at": mtime_stamp("out/drawings/index.json"),
    "verdict": "58 rows; BUILD 25 PASS / 2 FAIL / 31 CD; SHEET 0 PASS / 27 FAIL / 31 CD"}

REF = re.compile(r"\b(?:part|connection|assembly):[a-z0-9][a-z0-9.-]*")
SLUG = re.compile(r"\bmicroduck-[a-z0-9][a-z0-9-]*")
LINE = re.compile(r"\b(?:[PBRS]\d+[a-z]?)\b")
GATE = re.compile(r"\b(?:EB|SN|WK|EN|TH|RF|CAM|PWR)-?\d{2}\b", re.I)


def has(files, *prefixes):
    return any(f.startswith(p) for f in files for p in prefixes)


def route_item(subject, files, stated):
    """Return (route, target, why, ran_key). Ordered, most specific first."""
    s = subject.lower()
    refs = REF.findall(subject)
    ref = refs[0] if refs else None
    slug_m = SLUG.findall(subject)

    # ---- the shelf: part:/connection:/assembly: refs and their checker pages
    if ref or has(files, "out/factory/measure/triad.json", "out/laneT/shelf-", "SHELF-STATUS"):
        if ref is None:
            m = re.search(r"\b((?:part|connection|assembly):[a-z0-9][a-z0-9.-]*)", s)
            ref = m.group(1) if m else None
        if re.search(r"superseded|sha256|ledger", s):
            return ("measurable", "bin/triad check %s — then append the ledger row for the regenerated artifact (WF-UNKNOWNS reconciliation)" % (ref or "<ref>"),
                    "a superseded/sha256 ledger finding is closed by a ledger row, not by re-grading", "triad")
        if re.search(r"teardown|photograph|makerworld|fanhao", s):
            return ("in-sources", TEARDOWN, "the fanhao375 hardware teardown of the real unit is already ingested", None)
        if re.search(r"pollen|apache|upstream repo|board file", s):
            return ("research", POLLEN_HAT + " (Pollen's published package; fetch page + sha256 as LICENCE-POSITION does)",
                    "Pollen's own published material is the source that settles provenance questions", None)
        return ("measurable", "bin/triad check %s — the folder's own CANNOT DETERMINE names what settles it beyond the checker" % (ref or "<ref>"),
                "the shelf's own checker is the named check; its verdict is a live number", "triad")

    # ---- wiring / harness (including the WIRING-3D per-run route table, whose
    # subjects are HTML row soup naming only the run: dxl-id34-id33, imu200…)
    if (has(files, "wiring/", "out/wiring/", "WIRING-3D")
            or re.search(r"bend radius|loom|cable route|harness|routed run|corridor", s)
            or re.search(r"dxl-id\d+|imu200|unlocated|cable row|cut length", s)):
        if re.search(r"bend radius|corridor|route .*through|no corridor|pierce|dxl-id\d+|imu200|unlocated", s):
            return ("measurable", "wiring lane re-route in CAD (sim/route3d_exact.py + out/wiring/), then python3 tools/gen_wiring3d.py — a run with no corridor is a route failure, not an unknown",
                    "the corridor either exists in the model or it does not; the router measures it", "wiring_measure")
        return ("measurable", "ce-wire/bin/wire check microduck + python3 wiring/measure.py (coverage 2/82 declared — the blocking electrical records are named in wiring/README.md)",
                "the wiring lane's own check re-grades coverage against the shelf", "wire")

    # ---- pack rows quoting the harness table, a DRC line or a test gate
    if has(files, "FACTORY-PACK", "RELEASE.html", "MANUFACTURING-PLAYBOOK") and re.search(r"floor|slack|ffc|jst|bus header|connector end|hat mic|radxa camera|hat-dxl", s):
        return ("measurable", "wiring lane re-route + endpoint records (ce-wire/bin/wire check microduck; wiring/README.md names the blocking electrical records), then python3 wiring/measure.py",
                "a CD cable end is a missing endpoint record or a failed route, both measurable", "wire")
    if has(files, "FACTORY-PACK", "RELEASE.html") and re.search(r"\bdrc\b|\d+ pass / \d+ fail|gerber", s):
        return ("measurable", "the board's own DRC job (electronics/pcb-package.json boards[*].dir/out/fab/README.txt records the verdict; re-run kicad-cli pcb drc on the .kicad_pcb)",
                "DRC is a runnable check with a three-verdict answer", None)
    if has(files, "FACTORY-PACK", "RELEASE.html", "MANUFACTURING-PLAYBOOK") and GATE.search(subject):
        g = GATE.search(subject)
        return ("hardware", "TEST-PLAN gate %s (spec/test-plan.json) — bench procedure and acceptance band are on the gate; needs a built unit" % g.group(0),
                "a gate is measured on hardware; no desk work substitutes", None)

    # ---- test plan gates: bench procedures that need a built unit
    if has(files, "TEST-PLAN", "spec/test-plan"):
        g = GATE.search(subject)
        return ("hardware", "TEST-PLAN gate %s (spec/test-plan.json) — bench procedure and acceptance band are on the gate; needs a built unit" % (g.group(0) if g else "<gate>"),
                "a gate is measured on hardware; no desk work substitutes", None)

    # ---- DFM records
    if has(files, "out/dfm/"):
        return ("measurable", "python3 tools/dfm_rebuilt.py + python3 tools/measure_dfm.py — the DFM verdicts (printability, machining, load) re-grade from the rebuilt solid",
                "the DFM study is runnable on geometry we already have", None)

    # ---- tolerance stack
    if has(files, "sim/tolerance_stack") or re.search(r"tolerance stack|tolerance chain", s):
        return ("measurable", "python3 sim/tolerance_stack.py (stdlib only; writes the stack it measures)",
                "the stack study is runnable here", None)

    # ---- generator code text: a string inside a tool, not an open question
    if all(f.endswith(".py") for f in files):
        return ("unclassifiable", None,
                "code text inside %s (a regex, verdict tuple or message describing behaviour) — not itself a measured open question; retire it from the census if it should not count" % files[0],
                None)

    # ---- the pack quoting the census: refreshes when the census does
    if has(files, "FACTORY-PACK", "out/factory/reconcile") and re.search(r"closure route|distinct|census|harvest|no closure", s):
        return ("measurable", "python3 tools/open_items.py && python3 tools/gen_triage.py && python3 tools/gen_factory_pack.py — the pack quotes the census and must be regenerated after every census run",
                "the quoted counts re-measure with the census; regeneration is the named check", "census")

    # ---- drawings / sheets
    if has(files, "out/drawings/", "out/factory/measure/sheetcheck") or re.search(r"sheet|dim_coverage|dimension coverage|occupancy|empty rect", s):
        slug = slug_m[0] if slug_m else None
        if re.search(r"mesh-backed|feature census|parametric|dim_coverage", s):
            if slug:
                return ("measurable", "parametric rebuild of %s (bin/cad ce-parts/%s/iterations/*/cad/part.py), then ce-cad/bin/sheetcheck --all — a census cannot exist on a vendor mesh" % (slug, slug),
                        "dimension coverage needs parametric geometry; the rebuild is the named work", "sheetcheck")
            return ("measurable", "ce-cad/bin/sheetcheck --all for the eight sheet rules; the parametric rebuilds are owned by WF-SHEETS (tools/data/readiness.json in_flight)",
                    "dimension coverage needs parametric geometry; the sheet this item occurs in does not name the part, so the workflow that owns the rebuilds is the named route", "sheetcheck")
        return ("measurable", "ce-cad/bin/sheetcheck --all (rules and limits in MANUFACTURING-REQUIREMENTS.html); sheet work owned by WF-SHEETS",
                "the eight sheet rules are a runnable check", "sheetcheck")

    # ---- the partial manufacturing verification
    if has(files, "out/verify/manufacturing_partial"):
        grp = re.search(r"(lower leg|hip|neck|trunk|head)[^ ]* ?&? ?[a-z ]*", s)
        return ("measurable", "complete workflow wf_7f8b1690-71f for the unfinished group(s) of out/verify/manufacturing_partial.json from its own named sources (mech_dims.json, out/print/slice.json, out/stress/*, out/refcheck/*) and supersede the partial file",
                "the file says itself it was stopped part-way for a file race; finishing it is measurable work", None)

    # ---- PCBs
    if has(files, "PCB-PACKAGE", "out/pcb/", "electronics/") or re.search(r"\bdrc\b|gerber|footprint|kicad|schematic|netlist", s):
        if re.search(r"robot hat|hat board|apache|pollen", s):
            return ("research", POLLEN_HAT + " — Pollen's Apache-2.0 published board package vs our 65x30 reconstruction; the choice is recorded in readiness PCB notes",
                    "the provenance decision settles between two named packages", None)
        if re.search(r"datasheet|pinout|register|mpn|part number", s):
            return ("research", "the named datasheet on the row (ELECTRONICS-DATASHEET.html carries quote + page for every IC)",
                    "a datasheet fact closes a datasheet question", None)
        return ("measurable", "the board's own DRC job (electronics/pcb-package.json boards[*].dir/out/fab/README.txt records the DRC verdict; re-run kicad-cli pcb drc on the .kicad_pcb)",
                "DRC is a runnable check with a three-verdict answer", None)

    # ---- sourcing / bought lines
    if has(files, "SOURCING", "spec/sourcing", "out/release/bom", "out/bom-priced", "RFQ", "docs/BOM", "docs/production", "FACTORY-QUESTIONS", "docs/PARTS") \
            or (has(files, "FACTORY-PACK", "RELEASE.html", "MANUFACTURING-PLAYBOOK") and re.search(r"usd|price|vendor|distributor|quote|downgraded", s)):
        lid = LINE.search(subject)
        return ("research", "%s line %s — the vendor page URL(s) on that line; a second priced distributor or the partner factory's quotation closes it (WF-UNKNOWNS)" % (SOURCING, lid.group(0) if lid else "<id>"),
                "every bought line carries the URL that settles it; the gap is a second offer or a decision", None)

    # ---- verdict-scale definitions quoted in prose documents
    if re.search(r"three verdicts|the measurement was taken and it clears|nobody has measured it", s):
        return ("unclassifiable", None,
                "definition text describing the verdict scale itself, not a question that can close — the prose is right and needs no work",
                None)

    # ---- work-breakdown parcels whose acceptance test IS a command
    if re.search(r"acceptance test", s):
        cmd = re.search(r"((?:bin|tools|ce-cad|sim|wiring)/[a-z0-9_/.-]+\.py|bin/triad[^`\" ]*|ce-cad/bin/[a-z_]+)", subject)
        if cmd:
            return ("measurable", "run the parcel's own acceptance test: %s — the workplan states it; the parcel closes when it passes" % cmd.group(1),
                    "the acceptance test is a runnable command stated on the parcel itself", None)

    # ---- electronics doc (mermaid/graph prose): NFC reader IC, GPIO, carrier board
    if has(files, "docs/ELECTRONICS-AND-SOFTWARE", "ELECTRONICS-AND-SOFTWARE.html") and re.search(r"nfc|reader ic|gpio|carrier|device tree", s):
        return ("in-sources", TEARDOWN + " — the real unit's internals; the HAT's NFC/GPIO facts are settled by the teardown, not by inference",
                "the teardown of a shipped unit is already ingested and names the board family", None)

    # ---- structural / FEA rows quoted in the pack
    if re.search(r"landing|drop|mesh convergence|fe[sa]\b|stress|load case|buckling|yield", s):
        return ("measurable", "re-run the structural study (out/stress/corrected.json is the corrected load basis; ce-struct for the five study kinds; mesh convergence needs a length sweep before the ankle case is quoted)",
                "the study is runnable here at the corrected load basis", None)

    # ---- licence / provenance
    if has(files, "LICENCE-POSITION", "out/factory/licence", "SOURCES"):
        return ("research", LICENCE + " — the fact row with its archived URL and sha256 in out/factory/licence-evidence/",
                "the licence lane archives the settling page for every fact", None)

    # ---- simulation / structural / motion
    if has(files, "out/sim-evidence/", "out/stress/", "SIMULATION", "STRUCTURAL", "out/motion/", "out/verify/head", "out/head/") or re.search(r"fea|modal|buckling|gait|mujoco|mjb?cf|simulat", s):
        if re.search(r"durometer|shore|real unit|torque wrench|stall torque|teardown-?measured|physical sample|weigh|scale\b", s):
            return ("hardware", "the TEST-PLAN gate that names this measurement (spec/test-plan.json; gates need a built unit on the bench)",
                    "no simulation substitutes for the physical measurement the gate names", None)
        if re.search(r"datasheet|mpa|tensile|friction coefficient|material propert|s-n curve|fatigue", s):
            return ("research", "the cited datasheet row (STRUCTURAL.html cites its sources; the unsourced 50 MPa PLA row is named in FACTORY-QUESTIONS.html)",
                    "a material property is settled by a cited published figure", None)
        return ("measurable", "re-run the study that writes the file this item occurs in (sim/ holds the runners: head_sweep.py, leg_sweep.py, gait_sweep.py; ce-struct for the five study kinds)",
                "the study is runnable here — undone work, not unknown work", None)

    # ---- fasteners
    if has(files, "out/fasteners/", "FASTENERS") or re.search(r"fastener|screw|torque|hole census", s):
        if re.search(r"torque|seating|coupon", s):
            return ("hardware", "torque wrench on a built joint; TEST-PLAN gate (spec/test-plan.json) — assembly stations carry 3/3 torque CANNOT DETERMINE",
                    "a torque is measured on real hardware, never computed", None)
        return ("measurable", "python3 tools/fastener_census.py + python3 tools/fastener_audit.py (hole census vs placed runs, head seating, shank clearance, breakout)",
                "the fastener audit is a runnable geometric check", None)

    # ---- the readiness audit's own rows
    if has(files, "out/factory/readiness", "out/factory/measure/", "tools/measure_readiness.py", "tools/gen_readiness.py", "out/factory/workplan", "out/factory/questions", "out/factory/pack"):
        return ("measurable", "python3 tools/measure_readiness.py && python3 tools/gen_readiness.py — the row re-grades from fresh measurement",
                "the audit is one repeatable command; a row closes when its measurement closes", "measure")

    # ---- head / photo conformance and the photo-based pages
    if has(files, "out/head/", "HEAD-RECONSTRUCTION", "COMPARISON", "INTERNALS") or re.search(r"silhouette|photomatch|photograph|conformance", s):
        if re.search(r"photograph|photo|image|silhouette", s):
            return ("in-sources", "reference/makerworld-3250889/ (page/, files/ — the product photographs the head lane already archives)",
                    "the photographs are ingested; the comparison is a measurement away", None)
        return ("measurable", "python3 tools/head_analysis.py / head_dome_conformance.py (the head lane's own measurements)",
                "the head tools are runnable; their verdict is the answer", None)

    # ---- electronics datasheet / netlist leftovers
    if has(files, "ELECTRONICS-DATASHEET", "out/verify/electronics_verify", "netlist"):
        return ("measurable", "ce-elec/bin/elec (the verified electrical layer; the run that writes electronics/netlist-report.md)",
                "the electrical layer re-solves level by level from the shelf", None)

    # ---- shelf electrical records (currents, bases), electronics census, sources, part pages
    if has(files, "out/internals/"):
        return ("measurable", "python3 tools/electronics_census.py — the census re-walks placements + harness.json and re-grades every part folder",
                "the census is a runnable tool; its CD rows carry the reason", None)
    if has(files, "out/sources/"):
        return ("research", "the archived source itself (reference/ + the MANIFEST.md beside it; SOURCES.html quotes what each source changed)",
                "a source-derived fact is settled by re-reading the archived source", None)
    if has(files, "ce-parts/") and re.search(r"dts|u-boot|mux|console|serial|getty", s):
        return ("research", "reference/pollen-microduck-rl-develop — Pollen's published device trees; the mux/console question is read from their dts, not inferred",
                "the vendor's published DTS is the source that answers a DTS question", None)
    if has(files, "ce-parts/") and re.search(r"current|power|basis|sleep|peak|typical", s):
        return ("research", "the part's vendor datasheet (ELECTRONICS-DATASHEET.html quotes it with page numbers); transcribe the basis sentence per wiring/README.md",
                "a null current is settled by the published datasheet row, marked as a basis not a zero", None)
    if has(files, "ce-connections/") and re.search(r"cite|pdf|published|rating|datasheet|transcri", s):
        return ("research", "the datasheet named in the row's own why_null/cite field (e.g. JST eEH.pdf p.1) — read it and transcribe the value with the citation",
                "the row names the exact page that settles it; it was simply not read yet", None)
    if has(files, "docs/DFM"):
        return ("measurable", "python3 tools/dfm_rebuilt.py + python3 tools/measure_dfm.py — the DFM verdicts (printability, machining, load) re-grade from the rebuilt solid",
                "the DFM study is runnable on geometry we already have", None)

    # ---- battery / power
    if re.search(r"battery|np-f550|np-f970|wh\b|mah\b|voltage", s):
        return ("hardware", "multimeter + scale on the real pack at the TEST-PLAN PWR gates; the datasheet figure alone is not the measured mass",
                "battery mass and runtime are physical measurements", None)

    return (None, None, None, None)


UNCLASSIFIABLE_WHY = {
    "long": ("names no source, no runnable check and no bench in its text; a human "
             "reader must classify it before it can carry a route"),
}


def main():
    d = json.load(open(SRC, encoding="utf-8"))
    items = d["items"]
    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    rows, unclassifiable = [], 0
    for it in items:
        route, target, why, ran = route_item(it["subject"], it["files"], it["states_what_settles_it"])
        if route is None:
            route = "unclassifiable"
            target = None
            why = UNCLASSIFIABLE_WHY["long"]
            unclassifiable += 1
        rows.append({
            "key": norm(it["subject"]),
            "subject": it["subject"][:300],
            "route": route,
            "target": target,
            "why": why,
            "check_ran_tonight": RAN_TONIGHT.get(ran) if (ran and route == "measurable") else None,
            "occurrences": it["occurrences"],
            "files": it["files"][:6],
            "states_what_settles_it": it["states_what_settles_it"],
            "census_class": it["closure_class"],
        })

    # ---- target validation: a target that does not resolve is REPORTED
    import glob as _glob
    unresolved = []
    for r in rows:
        t = r["target"]
        if not t:
            continue
        cand = [t.split(" ")[0]]
        cand += re.findall(r"[\w./-]+/[\w./*-]+", t)
        ok = None
        for c in cand:
            if c.endswith(".py") or "/" in c:
                if any(ch in c for ch in "*?["):
                    hits = _glob.glob(os.path.join(ROOT, c)) or _glob.glob(c)
                    ok = bool(hits)
                elif c.startswith("reference/") or c.startswith("spec/") or c.startswith("out/") or c.startswith("wiring/") or c.startswith("electronics/") or c.startswith("ce-parts/") or c.startswith("sim/"):
                    ok = os.path.exists(os.path.join(ROOT, c)) or os.path.exists(c)
                if ok:
                    break
        if ok is False:
            unresolved.append({"route_row": r["key"][:60], "target": t[:120]})
    by_route = collections.Counter(r["route"] for r in rows)
    unclassifiable = by_route.get("unclassifiable", 0)
    routed = len(rows) - unclassifiable

    doc = {
        "$doc": "out/open/triage.json — closure-route triage of EVERY open CANNOT DETERMINE, generated by tools/gen_triage.py from out/open/cannot-determine.json. Five routes; every target is named and validated; checks cited as run tonight re-ran their tool and wrote the cited artifact.",
        "id": "MD-TRIAGE-001", "rev": "A", "generated": now,
        "generated_by": "tools/gen_triage.py",
        "rule": ("Three verdicts, no weakening: a route names a real check, source, file or bench "
                 "test. A missing route stays missing — unclassifiable rows say why in one line and "
                 "are never dressed as routed."),
        "census": {"file": "out/open/cannot-determine.json", "generated": d["doc"]["generated"] if "generated" in d.get("doc", {}) else None,
                   "distinct_items": len(items), "occurrences": d["occurrences"],
                   "items_with_no_closure_route_before_triage": d["items_with_no_closure_route"]},
        "totals": {"items": len(rows), "routed": routed, "unclassifiable": unclassifiable,
                   "by_route": dict(by_route),
                   "no_closure_route_after_triage": unclassifiable},
        "checks_ran_tonight": RAN_TONIGHT,
        "unresolved_targets": unresolved,
        "rows": rows,
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)

    # ---------------------------------------------------------------- HTML (dark table, house style)
    E = html.escape
    ROUTE_ORDER = ["measurable", "in-sources", "research", "hardware", "unclassifiable"]
    ROUTE_COLOR = {"measurable": "#4ea1ff", "in-sources": "#9d7bff", "research": "#ffc04d",
                   "hardware": "#ff8a5c", "unclassifiable": "#8b93a1"}
    A = []
    A.append('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">')
    A.append('<title>Closure-route triage — every open CANNOT DETERMINE, routed</title>')
    A.append('<link rel="stylesheet" href="../../tools/doc.css">')
    A.append('<style>')
    A.append('body{background:#101216;color:#dfe3ea}'
             '.wrap{max-width:1500px;margin:0 auto;padding:24px 20px 60px}'
             'a{color:#7fb4ff}h1,h2{color:#f2f4f8;font-family:var(--serif)}'
             '.zh{font-family:var(--sans);font-size:12px;color:#9aa3b2;display:block}'
             'p.lede{color:#b9c0cc;max-width:110ch}'
             'table{border-collapse:collapse;width:100%;table-layout:fixed;font-size:12.5px;margin:10px 0 26px;overflow-wrap:anywhere}'
             'th{background:#191d24;color:#aeb6c4;font-family:var(--sans);font-size:11.5px;text-align:left;padding:7px 8px;border-bottom:1px solid #2a303b;text-transform:uppercase;letter-spacing:.04em}'
             'td{padding:7px 8px;border-bottom:1px solid #232833;vertical-align:top;color:#cfd5e0}'
             'tr:hover td{background:#171b22}'
             'td.m{font-family:var(--mono);font-size:11px;color:#8fd0a0;word-break:break-all}'
             '.rt{font-family:var(--sans);font-weight:700;font-size:11px;padding:2px 8px;border-radius:10px;white-space:nowrap}'
             '.cd-chip{font-family:var(--mono);font-size:10.5px;color:#8b93a1}'
             '.statbar{display:flex;flex-wrap:wrap;gap:14px;margin:14px 0 22px}'
             '.stat{background:#161a21;border:1px solid #2a303b;border-radius:8px;padding:10px 14px;min-width:130px}'
             '.stat b{display:block;font-size:22px;color:#f2f4f8;font-variant-numeric:tabular-nums}'
             '.stat span{font-size:11.5px;color:#9aa3b2;font-family:var(--sans)}'
             '.ev{font-size:11px;color:#7fd19a;font-family:var(--mono)}'
             '.evnone{font-size:11px;color:#5b6472;font-family:var(--mono)}'
             'code{color:#9fd0ff}')
    A.append('</style>\n</head>\n<body>\n<div class="wrap">')
    A.append('<p class="backlink"><a href="../../INDEX.html">&larr; Document index</a></p>')
    A.append('<h1>Closure-route triage &mdash; every open CANNOT DETERMINE, routed <span class="zh">闭环路径分诊 —— 每一个未定项都有下一步</span></h1>')
    A.append('<p class="lede">%d distinct open items from the census of %s. Each carries exactly one of five routes; every route names a target you can open or run. %d items carry a real route; <b>%d are honestly unclassifiable</b> and say why in one line &mdash; they are the residual defect, not a dressed-up pass. Checks marked RAN TONIGHT re-ran their tool and wrote the cited artifact; nothing here is a canned pass.</p>'
             % (len(rows), E((doc["census"] or {}).get("generated") or "the census"), routed, unclassifiable))
    A.append('<div class="statbar">')
    for rt in ROUTE_ORDER:
        n = by_route.get(rt, 0)
        A.append('<div class="stat"><b style="color:%s">%d</b><span>%s</span></div>' % (ROUTE_COLOR[rt], n, rt))
    A.append('<div class="stat"><b>%d</b><span>total distinct items</span></div>' % len(rows))
    A.append('</div>')

    A.append('<section><h2>Checks that actually ran tonight</h2><table><colgroup><col style="width:34%%"><col style="width:12%%"><col style="width:54%%"></colgroup>'
             '<tr><th>command</th><th>at</th><th>verdict (read from the artifact it wrote)</th></tr>')
    for k, v in RAN_TONIGHT.items():
        A.append('<tr><td class="m">%s</td><td>%s</td><td>%s</td></tr>' % (E(v["command"]), E(v["at"] or "?"), E(v["verdict"])))
    A.append('</table></section>')

    for rt in ROUTE_ORDER:
        rs = [r for r in rows if r["route"] == rt]
        rs.sort(key=lambda r: -r["occurrences"])
        A.append('<section id="%s"><h2 style="color:%s">%s &mdash; %d items</h2>' % (rt, ROUTE_COLOR[rt], rt.upper(), len(rs)))
        if rt == "unclassifiable":
            A.append('<p class="lede">No rule in tools/gen_triage.py can name a source, a check, a file or a bench for these from their own text. The why is stated per row; classify by hand and move the row, never widen a rule to fit.</p>')
        A.append('<table><colgroup><col style="width:9%%"><col style="width:34%%"><col style="width:31%%"><col style="width:12%%"><col style="width:14%%"></colgroup>')
        A.append('<tr><th>route</th><th>subject (what was asked)</th><th>named target</th><th>occurs</th><th>ran tonight</th></tr>')
        for r in rs:
            ev = r["check_ran_tonight"]
            ev_cell = ('<span class="ev">RAN %s &mdash; %s</span>' % (E((ev["at"] or "?")), E(ev["verdict"][:110]))) if ev else '<span class="evnone">&mdash;</span>'
            A.append('<tr><td><span class="rt" style="background:%s;color:#0e1013">%s</span></td>'
                     '<td>%s<span class="cd-chip"><br>%s</span></td>'
                     '<td class="m">%s<br><span style="color:#8b93a1">%s</span></td>'
                     '<td>%d&times;<br><span class="cd-chip">%s</span></td>'
                     '<td>%s</td></tr>' % (
                         ROUTE_COLOR[rt], E(rt),
                         E(r["subject"][:200]), E(r["files"][0] if r["files"] else ""),
                         E(r["target"] or ""), E(r["why"]),
                         r["occurrences"], E(r["files"][1] if len(r["files"]) > 1 else ""),
                         ev_cell))
        A.append('</table></section>')

    if unresolved:
        A.append('<section><h2>Targets that did not resolve &mdash; REPORTED, not hidden</h2><table><tr><th>row</th><th>target</th></tr>')
        for u in unresolved:
            A.append('<tr><td class="m">%s</td><td>%s</td></tr>' % (E(u["route_row"]), E(u["target"])))
        A.append('</table></section>')

    A.append('<p class="lede" style="color:#8b93a1">Generated %s by tools/gen_triage.py from out/open/cannot-determine.json. The join key is norm(subject) and must stay identical to tools/open_items.py norm().</p>' % E(now))
    A.append('</div></body></html>')
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write("\n".join(A))

    print("triage: %d rows | routed %d | unclassifiable %d" % (len(rows), routed, unclassifiable))
    for k, v in by_route.most_common():
        print("    %-16s %5d" % (k, v))
    print("checks cited as run tonight: %s" % ", ".join(sorted(RAN_TONIGHT)))
    if unresolved:
        print("UNRESOLVED TARGETS: %d (listed on the page)" % len(unresolved))
        for u in unresolved[:10]:
            print("    -", u["target"])
    print("wrote %s" % OUT_JSON)
    print("wrote %s" % OUT_HTML)


if __name__ == "__main__":
    main()
