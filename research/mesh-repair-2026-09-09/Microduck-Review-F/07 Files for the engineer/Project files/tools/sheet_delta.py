"""Did the sheets get BETTER? Two sheetcheck runs, differenced.

    python3 tools/sheet_delta.py <before.json> <after.json>

Leif, 2026-09-04: "it must put workflows on ITERATING on these blueprints."
An iteration loop needs one thing a single run cannot give: a comparison. This
is it. It reads two `ce-cad/bin/sheetcheck --all --json` outputs and answers,
per rule, per section and per sheet, what improved, what regressed and what
did not move.

Exit codes, so the loop can be driven by a script:
  0  something improved and nothing regressed
  1  something REGRESSED — a rule that passed on a sheet now fails
  2  nothing moved at all (the iteration bought nothing)

A regression is never rounded away and never averaged out: the sheet and the
rule are named.
"""
import json
import os
import sys

ORDER = {"PASS": 2, "CANNOT DETERMINE": 1, "FAIL": 0}


def load(p):
    d = json.load(open(p, encoding="utf-8"))
    return d, {r["slug"]: r for r in d["sheets"]}


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    bpath, apath = sys.argv[1], sys.argv[2]
    B, b = load(bpath)
    A, a = load(apath)
    rules = A.get("rules") or []
    secs = ["A", "A2", "A3", "A4"]

    print("BEFORE %s  %s" % (B.get("generated"), os.path.relpath(bpath)))
    print("AFTER  %s  %s" % (A.get("generated"), os.path.relpath(apath)))
    print()

    gone = sorted(set(b) - set(a))
    new = sorted(set(a) - set(b))
    if gone:
        print("SHEETS THAT VANISHED (%d): %s" % (len(gone), ", ".join(gone)))
    if new:
        print("SHEETS THAT APPEARED (%d): %s" % (len(new), ", ".join(new)))
    if gone or new:
        print()

    both = sorted(set(a) & set(b))
    print("%-14s %s" % ("rule", "PASS before -> after   FAIL before -> after"))
    print("-" * 62)
    for k in rules:
        pb = sum(1 for s in both if (b[s].get("rules") or {}).get(k) == "PASS")
        pa = sum(1 for s in both if (a[s].get("rules") or {}).get(k) == "PASS")
        fb = sum(1 for s in both if (b[s].get("rules") or {}).get(k) == "FAIL")
        fa = sum(1 for s in both if (a[s].get("rules") or {}).get(k) == "FAIL")
        mark = "  BETTER" if pa > pb else ("  WORSE" if pa < pb else "")
        print("%-14s %11d -> %-5d %11d -> %-5d%s" % (k, pb, pa, fb, fa, mark))
    print()
    print("%-14s %s" % ("section", "PASS before -> after"))
    print("-" * 40)
    for k in secs:
        pb = sum(1 for s in both
                 if (b[s].get("sections") or {}).get(k) == "PASS")
        pa = sum(1 for s in both
                 if (a[s].get("sections") or {}).get(k) == "PASS")
        print("%-14s %11d -> %-5d%s"
              % (k, pb, pa, "  BETTER" if pa > pb else
                 ("  WORSE" if pa < pb else "")))

    fb_ = sum(b[s].get("features_enumerated") or 0 for s in both)
    fa_ = sum(a[s].get("features_enumerated") or 0 for s in both)
    db_ = sum(b[s].get("features_dimensioned") or 0 for s in both)
    da_ = sum(a[s].get("features_dimensioned") or 0 for s in both)
    lb = sum(b[s].get("colour_and_shadow_render_count") or 0 for s in both)
    la = sum(a[s].get("colour_and_shadow_render_count") or 0 for s in both)
    print()
    print("features enumerated  %d -> %d" % (fb_, fa_))
    print("features dimensioned %d -> %d  (%.1f %% -> %.1f %%)"
          % (db_, da_, 100.0 * db_ / max(1, fb_), 100.0 * da_ / max(1, fa_)))
    print("colour+shadow renders %d -> %d" % (lb, la))

    ups, downs = [], []
    for s in both:
        for k in rules:
            vb = (b[s].get("rules") or {}).get(k)
            va = (a[s].get("rules") or {}).get(k)
            if vb == va or vb is None or va is None:
                continue
            (ups if ORDER.get(va, 0) > ORDER.get(vb, 0) else downs).append(
                (s, k, vb, va))
    print()
    print("PER SHEET: %d rule verdict(s) improved, %d REGRESSED"
          % (len(ups), len(downs)))
    for (s, k, vb, va) in sorted(downs):
        print("  REGRESSION  %-34s %-14s %s -> %s" % (s, k, vb, va))
    for (s, k, vb, va) in sorted(ups):
        print("  improved    %-34s %-14s %s -> %s" % (s, k, vb, va))

    if downs:
        return 1
    if not ups and fa_ == fb_ and da_ == db_ and la == lb:
        print("\nNOTHING MOVED. This iteration bought nothing measurable.")
        return 2
    return 0


sys.exit(main())
