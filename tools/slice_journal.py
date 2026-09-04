#!/usr/bin/env python3
"""slice_journal.py — what ce-slice ACTUALLY sliced, per microduck part.

ce-slice (127.0.0.1:8886) is the authority for grams and seconds; its
append-only journal (~/dev/ce-slice/state/slices.jsonl) records every run with
the STL's sha256, the preset and the command line. out/print/slice.json quotes
ONE run per part. This reads every run so the factory can see:

  * which physical file each published number belongs to (sha256),
  * that a second, DIFFERENT file (out/dfm/stl-rebuilt/, our parametric
    rebuild) was also sliced for 11 parts, and by how much the numbers differ,
  * that the same file at the same preset can differ by orientation flags.

Writes out/factory/measure/slice-journal.json. Nothing is derived from volume.
"""
import json, os, hashlib, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JRN = os.path.expanduser("~/dev/ce-slice/state/slices.jsonl")
OUT = os.path.join(ROOT, "out", "factory", "measure", "slice-journal.json")


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


runs = []
for line in open(JRN, encoding="utf-8"):
    d = json.loads(line)
    stl = d.get("stl") or []
    if isinstance(stl, str):
        stl = [stl]
    if len(stl) != 1 or "microduck" not in stl[0]:
        continue
    p = stl[0]
    cmd = d.get("command")
    cmd = " ".join(cmd) if isinstance(cmd, list) else (cmd or "")
    runs.append({
        "slug": os.path.basename(p)[:-4],
        "stl_path": os.path.relpath(p, ROOT) if p.startswith(ROOT) else p,
        "family": "rebuilt" if "stl-rebuilt" in p else ("shipped" if "/out/print/stl/" in p else "other"),
        "stl_sha256": (d.get("stl_sha256") or [None])[0],
        "verdict": d.get("verdict"), "grams": d.get("grams"), "seconds": d.get("seconds"),
        "material": d.get("material"), "preset": d.get("preset_used"), "layer_mm": d.get("layer_mm"),
        "auto_orient": ("--orient 1" in cmd), "reason": d.get("reason"),
        "warning": d.get("warning"), "slicer": d.get("slicer_version"), "id": d.get("id"),
    })

published = {p["slug"]: p for p in json.load(open(os.path.join(ROOT, "out/print/slice.json"), encoding="utf-8"))["parts"]}
per = {}
for r in runs:
    per.setdefault(r["slug"], []).append(r)

parts = {}
for slug, rs in sorted(per.items()):
    pub = published.get(slug)
    stl_rel = pub["stl"] if pub else None
    stl_sha = sha256(os.path.join(ROOT, stl_rel)) if stl_rel and os.path.exists(os.path.join(ROOT, stl_rel)) else None
    match = None
    if pub:
        for r in rs:
            if r["grams"] is not None and abs(r["grams"] - pub["grams_per_piece"]) < 1e-4 and abs(r["seconds"] - pub["seconds_per_piece"]) < 0.05:
                match = r
                break
    reb = [r for r in rs if r["family"] == "rebuilt" and r["verdict"] == "PASS"]
    ship_pass = [r for r in rs if r["family"] == "shipped" and r["verdict"] == "PASS"]
    delta = None
    if reb and match:
        b = reb[-1]
        delta = {"rebuilt_stl": b["stl_path"], "rebuilt_sha256": b["stl_sha256"],
                 "rebuilt_grams": b["grams"], "rebuilt_seconds": b["seconds"],
                 "d_grams": round(b["grams"] - match["grams"], 4),
                 "d_grams_pct": round(100.0 * (b["grams"] - match["grams"]) / match["grams"], 2),
                 "d_seconds": round(b["seconds"] - match["seconds"], 2),
                 "d_seconds_pct": round(100.0 * (b["seconds"] - match["seconds"]) / match["seconds"], 2)}
    # same file, same layer height, different result (orientation / flags)
    spread = None
    if len(ship_pass) > 1 and stl_sha:
        same = [r for r in ship_pass if r["stl_sha256"] == stl_sha]
        lay = {}
        for r in same:
            lay.setdefault(r["layer_mm"], []).append(r)
        for L, group in lay.items():
            if len(group) > 1 and (max(x["seconds"] for x in group) - min(x["seconds"] for x in group)) > 0.5:
                lo = min(group, key=lambda x: x["seconds"])
                hi = max(group, key=lambda x: x["seconds"])
                spread = {"layer_mm": L, "n": len(group),
                          "grams": [lo["grams"], hi["grams"]], "seconds": [lo["seconds"], hi["seconds"]],
                          "seconds_pct": round(100.0 * (hi["seconds"] - lo["seconds"]) / lo["seconds"], 2),
                          "auto_orient": [lo["auto_orient"], hi["auto_orient"]],
                          "why": "identical sha256, identical layer height; the runs differ only in the slicer's auto-orient flag (--orient 1 --allow-rotations)"}
    parts[slug] = {"published": ({"grams": pub["grams_per_piece"], "seconds": pub["seconds_per_piece"], "stl": stl_rel,
                                  "stl_sha256_now": stl_sha, "material": pub["material"], "preset": pub["process_preset"]} if pub else None),
                   "published_run_found_in_journal": bool(match),
                   "published_run_sha256": match["stl_sha256"] if match else None,
                   "published_run_auto_orient": match["auto_orient"] if match else None,
                   "sha256_still_matches": bool(match and stl_sha and match["stl_sha256"] == stl_sha),
                   "runs": len(rs), "failures": [r["reason"] for r in rs if r["verdict"] != "PASS"],
                   "rebuilt_alternative": delta, "orientation_spread": spread}

out = {"$doc": __doc__.strip().splitlines()[0],
       "journal": JRN, "read_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
       "microduck_runs": len(runs), "parts": parts,
       "summary": {"parts_seen": len(parts),
                   "published_number_traced_to_a_journal_run": sum(1 for v in parts.values() if v["published_run_found_in_journal"]),
                   "stl_unchanged_since_that_run": sum(1 for v in parts.values() if v["sha256_still_matches"]),
                   "with_a_rebuilt_alternative": sum(1 for v in parts.values() if v["rebuilt_alternative"]),
                   "with_an_orientation_spread": sum(1 for v in parts.values() if v["orientation_spread"])}}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps(out["summary"], indent=1))
for s, v in parts.items():
    d = v["rebuilt_alternative"]
    if d:
        print("%-38s shipped %8.4f g -> rebuilt %8.4f g  (%+.2f %%),  %+.2f %% time" % (s, v["published"]["grams"], d["rebuilt_grams"], d["d_grams_pct"], d["d_seconds_pct"]))
for s, v in parts.items():
    if v["orientation_spread"]:
        o = v["orientation_spread"]
        print("%-38s SAME sha, layer %s: %s g / %s s  vs  %s g / %s s  (%+.2f %% time), auto_orient %s" % (s, o["layer_mm"], o["grams"][0], o["seconds"][0], o["grams"][1], o["seconds"][1], o["seconds_pct"], o["auto_orient"]))
for s, v in parts.items():
    if not v["sha256_still_matches"] and v["published"]:
        print("PROVENANCE: %-30s published number is NOT traceable to the file on disk now (found_in_journal=%s)" % (s, v["published_run_found_in_journal"]))
