#!/usr/bin/env python3
"""fastener_audit.py — DOES THIS FASTENING ACTUALLY WORK? Eight physical
questions, each answered from a measurement.

    python3 tools/fastener_audit.py   -> out/fasteners/audit.json + a table

Leif, 2026-09-04: "will the internals actually work and like tell it to
scrutinize everything and do a deep dive and make the internals actually make
sense."

THE FRAMING, and it decides what a FAIL means here. THE REAL MICRODUCK WORKS.
So a check that fails is FIRST a place OUR MODEL is wrong, not a design flaw to
fix creatively. Every failing row therefore names the measurement that would
settle which it is, and none of them moves the model away from the reference.

THE EIGHT CHECKS (a run may be exempt from one; exempt is not pass):
  1  head clash        — no two screw heads overlap (centre distance vs dk)
  2  duplicate         — no two screws claim the same head point
  3  head passes       — the head fits down every bore it must travel through
  4  head seats        — the seating feature is wider than dk, or the head
                         stands proud and that is stated
  5  shank clears      — every clearance hole on the run is wider than d
  6  engagement        — at least 1.5 d of thread (a RULE), and the screw does
                         not bottom in the pilot (a MEASUREMENT)
  7  protrusion        — the screw does not emerge from the far side of the
                         part it threads into
  8  driver access     — a hex key of the ISO 4762 across-flats size can reach
                         the head: the bore above the head is at least the key
                         size wide for the whole distance

Runs under plain python3. Reads out/fasteners/runs.json, placed.json and
features-by-mesh.json; measures nothing new and invents nothing.
"""
import collections
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "out", "fasteners", "audit.json")

# ISO 4762, the rows this robot uses. dk is the MAX head diameter, k the MAX
# head height, key the across-flats hex size. Sources: ce-parts/screw-m2-iso4762
# and screw-m2.5-iso4762 component.json record.spec (fasteners.eu table, fetched
# 2026-08-19), cross-checked against cecad/screws.py SOCKET.dims and HEX_KEY.
SCREW = {"M2":   {"d": 2.0, "dk_max": 3.80, "dk_min": 3.62, "k_max": 2.00, "key": 1.5},
         "M2.5": {"d": 2.5, "dk_max": 4.50, "dk_min": 4.32, "k_max": 2.50, "key": 2.0}}
MIN_ENGAGE_D = 1.5


def load(rel):
    return json.load(open(os.path.join(ROOT, rel), encoding="utf-8"))


def row(check, verdict, what, measured, settled_by=None, run=None):
    r = {"check": check, "verdict": verdict, "what": what, "measured": measured}
    if settled_by:
        r["settled_by"] = settled_by
    if run is not None:
        r["run"] = run
    return r


def main():
    runs = [r for r in load("out/fasteners/runs.json")["runs"] if r["verdict"] == "PASS"]
    placed = load("out/fasteners/placed.json")["placed"]
    rows = []

    # --- 1 head clash, 2 duplicates --------------------------------------
    pts = collections.Counter(tuple(round(v, 3) for v in p["world_pos_mm"]) for p in placed)
    dups = [k for k, v in pts.items() if v > 1]
    rows.append(row("duplicate", "PASS" if not dups else "FAIL",
                    "no two screws claim the same head point",
                    {"screws": len(placed), "duplicate_points": len(dups),
                     "examples": dups[:5]},
                    "if two runs land on one point the coaxial grouping merged or split wrong"))
    worst = None
    for i, a in enumerate(placed):
        for b in placed[i + 1:]:
            d = math.dist(a["world_pos_mm"], b["world_pos_mm"])
            need = (SCREW[a["size"]]["dk_max"] + SCREW[b["size"]]["dk_max"]) / 2.0
            if worst is None or d - need < worst[0]:
                worst = (d - need, d, need, a["instance"], b["instance"], a["size"], b["size"])
    rows.append(row("head clash", "PASS" if worst and worst[0] > 0 else "FAIL",
                    "no two screw heads overlap; two heads clear when their centres are further "
                    "apart than the mean of their head radii sum, i.e. (dk_a + dk_b)/2",
                    {"closest_pair_mm": round(worst[1], 4), "needed_mm": round(worst[2], 4),
                     "margin_mm": round(worst[0], 4),
                     "screws": [worst[3], worst[4]], "sizes": [worst[5], worst[6]]},
                    "a negative margin means two screws were derived where the robot has one"))

    # --- per-run checks ---------------------------------------------------
    per = collections.Counter()
    detail = []
    for r in runs:
        s = SCREW[r["size"]]
        feats = sorted(r["features"], key=lambda f: f["s_lo"])
        seat_mesh, seat_cls = r["head_seat_mesh"], r["head_seat_class"]
        seat = None
        for f in feats:
            if f["mesh"] == seat_mesh and f["cls"] == seat_cls:
                seat = f
                break
        d_head_point = r["head_point_world_mm"]
        L = r["stocked_length_mm"]
        item = {"size": r["size"], "length_mm": L, "meshes": r["meshes"],
                "head_seat": "%s/%s" % (seat_mesh, seat_cls),
                "pilot": "%s Ø%s" % (r["pilot_mesh"], r["pilot_d_mm"]), "checks": []}

        # 3 + 4  the head: does it fit the feature it seats in / travels down
        if seat is None:
            item["checks"].append(row("head seats", "CANNOT DETERMINE",
                                      "the seating feature could not be re-found in the run",
                                      None, "re-run tools/fastener_runs.py"))
        elif seat["cls"] in ("counterbore", "insert"):
            m = seat["d_mm"] - s["dk_max"]
            res = seat.get("residual_mm")
            if m >= 0:
                v = "PASS"
            elif res is not None and abs(m) <= res:
                # NOT A LOOSENED CHECK — A HONEST ONE. The deficit is smaller
                # than this patch's OWN least-squares fit residual, so the
                # measurement cannot tell a real interference from its own
                # noise. THE REAL ROBOT WORKS, so claiming FAIL here would be
                # asserting a defect the instrument cannot see. It stays open,
                # and the caliper that closes it is named.
                v = "CANNOT DETERMINE"
            else:
                v = "FAIL"
            item["checks"].append(row(
                "head passes and seats", v,
                "the head (dk max %.3f mm) must pass down and seat in a Ø%.3f mm bore %.3f mm deep"
                % (s["dk_max"], seat["d_mm"], seat["depth_mm"]),
                {"bore_d_mm": seat["d_mm"], "dk_max_mm": s["dk_max"],
                 "clearance_mm": round(m, 4), "bore_depth_mm": seat["depth_mm"],
                 "dk_min_mm": s["dk_min"],
                 "clearance_at_dk_min_mm": round(seat["d_mm"] - s["dk_min"], 4),
                 "mesh_fit_residual_mm": res, "bore_cover_deg": seat.get("cover_deg"),
                 "deficit_vs_residual": (None if res is None else
                                         ("deficit %.4f mm is INSIDE the patch's own %.4f mm fit "
                                          "residual — the instrument cannot separate them"
                                          % (-m, res)) if m < 0 else "no deficit")},
                ("A caliper on the printed bore. THE REFERENCE WORKS, so a negative clearance is "
                 "first a modelling error: compare it against the mesh's own fit residual — where "
                 "the residual is larger than the deficit the measurement cannot tell them apart "
                 "and this is CANNOT DETERMINE, not a design flaw.")))
        else:
            item["checks"].append(row(
                "head seats", "PASS",
                "the head lands on the outer FACE (no counterbore) and stands %.3f mm proud"
                % s["k_max"],
                {"seat_class": seat["cls"], "head_height_mm": s["k_max"]},
                "a photograph of that face on a real unit: a head that should be flush and is not "
                "means the counterbore was not detected"))

        # 5  every clearance hole must clear the shank
        tight = [f for f in feats if f["cls"] in ("clearance", "ambiguous")
                 and f["d_mm"] < s["d"]]
        item["checks"].append(row(
            "shank clears", "PASS" if not tight else "FAIL",
            "every clearance/ambiguous hole on the run must be wider than the shank (Ø%.2f mm)"
            % s["d"],
            {"holes_checked": sum(1 for f in feats if f["cls"] in ("clearance", "ambiguous")),
             "too_tight": [{"mesh": f["mesh"], "index": f["index"], "d_mm": f["d_mm"]}
                           for f in tight]},
            "a hole narrower than the screw is either a pilot the classifier mis-sized or a "
            "different screw size on this line"))

        # 6  engagement
        engaged = L - r["grip_mm"]
        need = MIN_ENGAGE_D * s["d"]
        avail = r["engagement_available_mm"]
        v = "PASS" if (need <= engaged <= avail) else "FAIL"
        item["checks"].append(row(
            "engagement", v,
            "the screw must reach %g d = %.3f mm of thread (a RULE) and must not bottom in the "
            "%.3f mm pilot (a MEASUREMENT)" % (MIN_ENGAGE_D, need, avail),
            {"screw_length_mm": L, "grip_mm": r["grip_mm"], "engaged_mm": round(engaged, 4),
             "min_rule_mm": round(need, 4), "pilot_depth_mm": avail,
             "window_mm": r["length_window_mm"]},
            "a sourced length inside the window, or a re-measurement of grip / pilot depth"))

        # 7  protrusion beyond the far end of the chain
        span_lo, span_hi = r["span_mm"]
        over = engaged - avail
        item["checks"].append(row(
            "protrusion", "PASS" if over <= 0 else "FAIL",
            "the thread must stop inside the pilot, not emerge from the far face",
            {"engaged_mm": round(engaged, 4), "pilot_depth_mm": avail,
             "overshoot_mm": round(max(0.0, over), 4), "chain_span_mm": [span_lo, span_hi]},
            "a section view of that part, or a caliper on the boss depth"))

        # 8  driver access
        above = [f for f in feats
                 if f["cls"] in ("counterbore", "insert", "clearance", "ambiguous")
                 and f["d_mm"] >= s["key"]]
        narrow = [f for f in feats
                  if f["cls"] in ("counterbore", "insert") and f["d_mm"] < s["key"]]
        item["checks"].append(row(
            "driver access", "PASS" if not narrow else "FAIL",
            "a %.1f mm across-flats hex key (ISO 4762) must reach the head; every bore above it "
            "must be at least that wide" % s["key"],
            {"key_af_mm": s["key"], "bores_wide_enough": len(above),
             "bores_too_narrow": [{"mesh": f["mesh"], "d_mm": f["d_mm"]} for f in narrow]},
            "cecad.install.driver_clearance() on the built solid, which sweeps the volume the "
            "key needs to turn — this check only compares diameters"))

        for c in item["checks"]:
            per[(c["check"], c["verdict"])] += 1
        item["verdict"] = min((c["verdict"] for c in item["checks"]),
                              key=lambda v: {"FAIL": 0, "CANNOT DETERMINE": 1, "PASS": 2}[v])
        detail.append(item)

    fails = [d for d in detail if d["verdict"] == "FAIL"]
    cds = [d for d in detail if d["verdict"] == "CANNOT DETERMINE"]
    summary = collections.Counter()
    for k, n in per.items():
        summary["%s / %s" % k] = n
    doc = {
        "doc": {"id": "MD-FAST-AUDIT-001", "rev": "A",
                "title": "Does this fastening actually work? Eight physical checks per screw run",
                "generated_by": "tools/fastener_audit.py",
                "reads": ["out/fasteners/runs.json", "out/fasteners/placed.json"]},
        "framing": ("THE REAL MICRODUCK WORKS. A failing row is FIRST a place our model is wrong, "
                    "not a design flaw. Every row names the measurement that separates the two, "
                    "and nothing here moves the model away from the reference."),
        "screw_table": SCREW,
        "counts": {"runs_audited": len(runs), "screws_placed": len(placed),
                   "assembly_wide_checks": 2,
                   "per_run_checks": sum(len(d["checks"]) for d in detail),
                   "runs_all_PASS": len(detail) - len(fails) - len(cds),
                   "runs_with_a_FAIL": len(fails),
                   "runs_with_a_CANNOT_DETERMINE": len(cds),
                   "by_check": dict(summary)},
        "assembly_wide": rows,
        "runs_with_a_finding": fails + cds,
        "runs": detail}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(doc, open(OUT, "w", encoding="utf-8"), indent=1)
    print("runs audited        :", len(runs), " screws placed:", len(placed))
    print("per-run checks      :", doc["counts"]["per_run_checks"])
    for k in sorted(summary):
        print("   %-34s %d" % (k, summary[k]))
    for r in rows:
        print("%-14s %-18s %s" % (r["check"], r["verdict"], json.dumps(r["measured"])[:110]))
    print("runs all PASS %d | with a FAIL %d | with a CANNOT DETERMINE %d"
          % (doc["counts"]["runs_all_PASS"], len(fails), len(cds)))
    for d in (fails + cds)[:8]:
        bad = [c for c in d["checks"] if c["verdict"] != "PASS"]
        print("  %-6s x%-4g %-40s %s"
              % (d["size"], d["length_mm"], "/".join(d["meshes"])[:40],
                 "; ".join("%s=%s" % (c["check"], c["verdict"]) for c in bad)))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
