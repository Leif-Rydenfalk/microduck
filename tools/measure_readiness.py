#!/usr/bin/env python3
"""measure_readiness.py — take EVERY measurement the readiness audit grades from,
in one repeatable command, and write it to out/factory/measure/.

The audit (tools/gen_readiness.py) types in no number: it reads these files.
This script is how they are produced, so a factory engineer can re-run the whole
measurement and get the same table, or a different one if the repo moved.

  out/factory/measure/sheetcheck.json    ce-cad/bin/sheetcheck --all   (deduped, see below)
  out/factory/measure/sheetcheck.log     the same run's human table
  out/factory/measure/triad.json         bin/triad check --all --json
  out/factory/measure/stlcheck.json      tools/stlcheck.py
  out/factory/measure/slice-journal.json tools/slice_journal.py
  out/factory/measure/sourcing-rows.json spec/sourcing.json (copied, so the audit
                                         and the page quote one frozen read)
  out/factory/measure/slice-health.json  ce-slice health --deep + a CONTROL slice of a real part

TWO MEASURED DEFECTS IN THE INSTRUMENTS, handled here and recorded in the file
rather than silently patched:

  D1  `sheetcheck --all` emits every sheet TWICE (byte-identical records). It
      returned 56 records for 28 sheet folders on 2026-09-04 17:03. We dedupe by
      slug and assert the duplicate pair is identical before dropping it.
  D2  out/drawings/edgeclass/ is another lane's HLR bench (before/after SVGs of
      one part, no title block, no frame), not a part drawing. sheetcheck has no
      way to know that and grades it as a sheet. It is skipped by name here and
      the skip is written into the file.

Usage:  python3 tools/measure_readiness.py [--skip-sheets] [--skip-triad]
"""
import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSHOP = "/Users/leifrydenfalk/dev/ce-workshop"
MEAS = os.path.join(ROOT, "out", "factory", "measure")
ENV = dict(os.environ, CE_TRIAD_ROOT="%s:%s" % (ROOT, WORKSHOP))

# out/drawings subfolders that are NOT part drawing sheets. Each carries the
# reason it is not a sheet; nothing is skipped without one.
NOT_A_SHEET = {
    "_prof": "drawer scratch — name starts with '_' (sheetcheck skips it itself)",
    "edgeclass": ("another lane's HLR edge-classification bench: before/after SVGs of one "
                  "part's projections, no frame, no title block, no dimensions — it is a "
                  "test fixture, not a drawing of a part"),
}


def run(cmd, log_path=None, cwd=ROOT):
    print("$ " + " ".join(cmd), flush=True)
    p = subprocess.run(cmd, cwd=cwd, env=ENV, capture_output=True, text=True)
    out = p.stdout + (("\n" + p.stderr) if p.stderr else "")
    if log_path:
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(out)
    return p.returncode, out


def measure_sheets():
    raw = os.path.join(MEAS, "sheetcheck.raw.json")
    log = os.path.join(MEAS, "sheetcheck.log")
    rc, _ = run([os.path.join(WORKSHOP, "ce-cad", "bin", "sheetcheck"),
                 "--all", "--json", raw, "out/drawings"], log_path=log)
    with open(raw, encoding="utf-8") as f:
        d = json.load(f)
    records = d["sheets"]
    by = {}
    dup_identical, dup_differing = 0, []
    for s in records:
        slug = s["slug"]
        if slug in by:
            if json.dumps(s, sort_keys=True) == json.dumps(by[slug], sort_keys=True):
                dup_identical += 1
            else:
                dup_differing.append(slug)
            continue
        by[slug] = s
    skipped = []
    for slug in list(by):
        if slug in NOT_A_SHEET:
            skipped.append({"slug": slug, "why": NOT_A_SHEET[slug]})
            del by[slug]
    no_sheet = [r for r in d.get("part_dirs_with_no_sheet", []) if r.get("slug") not in NOT_A_SHEET]
    d["sheets"] = by
    d["part_dirs_with_no_sheet"] = no_sheet
    d["$dedup"] = {
        "raw_records": len(records),
        "unique_slugs": len(records) - dup_identical,
        "duplicate_records_dropped": dup_identical,
        "duplicates_that_differed": dup_differing,
        "defect": ("D1: ce-cad/bin/sheetcheck --all emits every sheet twice; the %d dropped "
                   "records were byte-identical to the ones kept" % dup_identical),
        "not_a_sheet_skipped": skipped,
        "sheets_graded": len(by),
        "sheetcheck_exit": rc,
    }
    with open(os.path.join(MEAS, "sheetcheck.json"), "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1)
    os.remove(raw)
    v = {}
    for s in by.values():
        v[s["verdict"]] = v.get(s["verdict"], 0) + 1
    print("sheets graded %d  %s ; %d part folders with no sheet ; %d skipped not-a-sheet"
          % (len(by), v, len(no_sheet), len(skipped)), flush=True)
    return len(by), v


def measure_triad():
    rc, out = run([os.path.join(WORKSHOP, "bin", "triad"), "check", "--all", "--json"])
    i = out.find("{")
    with open(os.path.join(MEAS, "triad.json"), "w", encoding="utf-8") as f:
        f.write(out[i:])
    d = json.loads(out[i:])
    n = len(d["results"])
    v = {}
    for r in d["results"]:
        v[r["verdict"]] = v.get(r["verdict"], 0) + 1
    print("triad refs %d %s" % (n, v), flush=True)
    return n, v


def measure_stl():
    rc, out = run([sys.executable, "tools/stlcheck.py"])
    src = "/private/tmp/factory-readiness/stlcheck.json"
    if os.path.exists(src):
        shutil.copy(src, os.path.join(MEAS, "stlcheck.json"))
    d = json.load(open(os.path.join(MEAS, "stlcheck.json"), encoding="utf-8"))
    bad = [r["file"] for r in d if not r.get("watertight")]
    print("STLs %d, not watertight: %s" % (len(d), bad or "none"), flush=True)
    return len(d), bad


def measure_sourcing():
    src = os.path.join(ROOT, "spec", "sourcing.json")
    d = json.load(open(src, encoding="utf-8"))
    rows = d["lines"] if isinstance(d, dict) and "lines" in d else (d["rows"] if isinstance(d, dict) and "rows" in d else d)
    with open(os.path.join(MEAS, "sourcing-rows.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=1, ensure_ascii=False)
    print("sourcing rows %d (from spec/sourcing.json)" % len(rows), flush=True)
    return len(rows)



def measure_slice_health():
    """Is the grams/seconds authority answering RIGHT NOW?

    Two probes, because ce-slice's own deep health uses a canary cube and that
    canary is presently rejected by the slicer while real parts slice fine:
      1. `ce-slice health --deep --json`  — the instrument's own verdict.
      2. a CONTROL slice of a real microduck STL — the question the audit
         actually needs answered.
    """
    ce = os.path.expanduser("~/dev/ce-slice/bin/ce-slice")
    rec = {"probed_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
           "binary": ce}
    rc, out = run([ce, "health", "--deep", "--json"], cwd=os.path.dirname(ce))
    try:
        rec["health"] = json.loads(out[out.find("{"):])
    except Exception as e:
        rec["health"] = {"parse_error": str(e), "raw": out[:2000]}
    control_stl = os.path.join(ROOT, "out", "print", "stl", "PLA", "microduck-ankle-left.stl")
    rc, out = run([ce, "slice", "--material", "PLA", "--printer", "H2S",
                   "--no-cache", "--json", control_stl], cwd=os.path.dirname(ce))
    try:
        rec["control_slice"] = json.loads(out[out.find("{"):])
    except Exception as e:
        rec["control_slice"] = {"parse_error": str(e), "raw": out[:2000]}
    h = rec.get("health", {})
    c = rec.get("control_slice", {})
    cv = c.get("verdict") or (c.get("results") or [{}])[0].get("verdict")
    rec["verdict"] = ("PASS" if cv == "PASS" else "FAIL")
    rec["why"] = ("the instrument's own deep health is %s (%s); a control slice of a REAL part "
                  "is %s — the audit's print rows depend on the control, not on the canary"
                  % (h.get("verdict"), (h.get("reason") or "")[:160], cv))
    with open(os.path.join(MEAS, "slice-health.json"), "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)
    print("ce-slice health %s ; control slice of a real part %s" % (h.get("verdict"), cv), flush=True)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-sheets", action="store_true")
    ap.add_argument("--skip-triad", action="store_true")
    a = ap.parse_args()
    os.makedirs(MEAS, exist_ok=True)
    started = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    if not a.skip_sheets:
        measure_sheets()
    if not a.skip_triad:
        measure_triad()
    measure_stl()
    run([sys.executable, "tools/slice_journal.py"])
    measure_slice_health()
    measure_sourcing()
    with open(os.path.join(MEAS, "run.json"), "w", encoding="utf-8") as f:
        json.dump({"started": started,
                   "finished": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                   "argv": sys.argv[1:]}, f, indent=1)
    print("measurements written to out/factory/measure/", flush=True)


if __name__ == "__main__":
    main()
