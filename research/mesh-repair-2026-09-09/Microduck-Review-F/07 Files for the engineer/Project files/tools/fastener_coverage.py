"""tools/fastener_coverage.py — WHICH parts are held on by nothing.

64 screws are placed in assembly:microduck. SPEC.md's community census counts
145 holes in the machine. The gap has been stated as a number for a while;
this names WHERE it is, per mesh, so it is a work list instead of a shortfall.

The framing this repo works under: THE REAL MICRODUCK WALKS. So a part our
model fastens with nothing is not a design flaw to solve creatively — it is a
place OUR model is missing a screw run, and the measured clearance holes in
that part say how many. Each row is a lead pointing at a specific mesh.

Run:  python3 tools/fastener_coverage.py
"""
import collections
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLACE = os.path.join(REPO, "ce-assemblies/microduck/current/placements.json")
FEAT = os.path.join(REPO, "out/fasteners/features-by-mesh.json")
OUT = os.path.join(REPO, "out/fasteners/coverage.json")


def main():
    rows = json.load(open(PLACE))["record"]["rows"]
    parts = [r for r in rows if r.get("mesh")]
    fast = [r for r in rows if str(r.get("part", "")).startswith("part:screw-")]
    uses = collections.Counter(r["mesh"] for r in parts)
    joined = collections.Counter()
    for r in fast:
        for m in (r.get("joins") or []):
            joined[m] += 1

    feat = json.load(open(FEAT))["meshes"]

    def measured(mesh):
        f = (feat.get(mesh) or {}).get("features") or []
        h = [x for x in f if x.get("feature") == "hole"]
        return {
            "clearance": sum(1 for x in h if x.get("class") == "clearance"),
            "pilot": sum(1 for x in h if x.get("class") in ("pilot", "tap")),
            "counterbore": sum(1 for x in h if x.get("role") == "counterbore"),
            "holes_total": len(h),
        }

    held, unheld = [], []
    for m in sorted(uses):
        rec = {"mesh": m, "uses": uses[m], "screws_joining_it": joined[m],
               "measured": measured(m)}
        (held if joined[m] else unheld).append(rec)

    gap = [r for r in unheld if r["measured"]["clearance"] > 0]
    no_holes = [r for r in unheld if r["measured"]["clearance"] == 0]
    missing = sum(r["measured"]["clearance"] * r["uses"] for r in gap)

    doc = {
        "doc": {"id": "MD-FASTCOVER-001", "rev": "A",
                "title": "Fastener coverage — which placed parts are held on "
                         "by nothing, and how many measured holes say they "
                         "should not be",
                "generated_by": "tools/fastener_coverage.py",
                "reads": [PLACE, FEAT]},
        "framing": "THE REAL MICRODUCK WALKS. A part this model fastens with "
                   "nothing is a gap in OUR model, not a flaw in the design. "
                   "Every row below is a lead pointing at one mesh.",
        "counts": {
            "meshes_placed": len(uses),
            "meshes_with_at_least_one_screw": len(held),
            "meshes_with_zero_screws": len(unheld),
            "zero_screw_meshes_that_HAVE_measured_clearance_holes": len(gap),
            "zero_screw_meshes_with_no_clearance_hole_measured": len(no_holes),
            "screws_placed": len(fast),
            "clearance_holes_with_no_screw_weighted_by_uses": missing,
            "community_census_holes": 145,
            "community_census_source": "SPEC.md:75-76, from "
                "reference/makerworld-3250889/upstream-github-fanhao375-"
                "microduck-replica/docs/fastener-reconstruction.en.md",
        },
        "THE_GAP_these_are_the_leads": sorted(
            gap, key=lambda r: -r["measured"]["clearance"] * r["uses"]),
        "zero_screws_and_no_clearance_hole": [
            {"mesh": r["mesh"], "uses": r["uses"],
             "note": "no M2/M2.5 clearance hole was measured on this mesh, so "
                     "the absence of a screw is consistent with it. It is "
                     "bought-in, bonded, press-fit, soft, or a sub-feature — "
                     "which of those is NOT settled here."}
            for r in no_holes],
        "held": held,
    }
    with open(OUT, "w") as fh:
        json.dump(doc, fh, indent=1)
    c = doc["counts"]
    print(json.dumps(c, indent=1))
    print("\nTHE GAP — placed, has clearance holes, has no screw:")
    for r in doc["THE_GAP_these_are_the_leads"]:
        print("  %-30s uses %d  clearance holes %d  -> %d unfastened"
              % (r["mesh"], r["uses"], r["measured"]["clearance"],
                 r["measured"]["clearance"] * r["uses"]))
    print("\nwrote", OUT)


if __name__ == "__main__":
    main()
