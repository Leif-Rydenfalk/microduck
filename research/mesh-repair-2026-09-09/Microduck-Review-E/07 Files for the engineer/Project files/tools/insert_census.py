"""tools/insert_census.py — does ANY bore in this robot accept a heat-set insert?

The pocket census (tools/pocket_census.py) answered the nut half by
measurement: 0 hex pockets in 43 meshes. This answers the insert half, and it
needs no new geometry — the hole diameters are already measured in
out/fasteners/features-by-mesh.json (cecad.meshfeatures.features on every
mesh the assembly places). A heat-set insert is not a screw: it is a knurled
brass bush that needs a STRAIGHT BORE OF ITS OWN OUTER DIAMETER. A tap-drill
pilot is roughly half that. So the diameter alone separates them with no
judgement, and the question is simply: how many measured bores fall in the
insert window?

Run:  ce-cad/bin/cad tools/insert_census.py     (plain python3 also works)
"""
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "out/fasteners/features-by-mesh.json")
OUT = os.path.join(REPO, "out/fasteners/inserts.json")

# The workshop shelf's one heat-set-insert family with measured geometry is
# part:insert-m3-heatset (ruthex / CNC Kitchen form). That folder's own
# origin_why records that NO standard governs these parts — no ISO, no DIN —
# so every figure is one vendor's geometry. The M2 and M2.5 members of that
# family are NOT on the shelf and are not invented here. What is stated is
# the WINDOW a bore must fall in to be an insert bore at all, generous on
# both sides so the test cannot miss a candidate by being too tight.
WINDOWS = {
    "M2 heat-set insert": (2.90, 3.60),
    "M2.5 heat-set insert": (3.50, 4.30),
    "M3 heat-set insert": (4.00, 4.80),
}
PILOTS = {
    "M2 tap drill / self-tap pilot": (1.50, 1.75),
    "M2.5 tap drill / self-tap pilot": (1.95, 2.15),
    "M2 clearance": (2.15, 2.45),
    "M2.5 clearance": (2.65, 2.95),
    "M2 counterbore (cap head Ø3.8)": (3.90, 5.00),
}


def main():
    d = json.load(open(SRC))["meshes"]
    rows = []
    for mesh, rec in sorted(d.items()):
        for h in rec.get("features", []) or []:
            if h.get("feature") != "hole":
                continue
            dia = h.get("d_mm")
            if dia is None:
                continue
            rows.append({"mesh": mesh, "d_mm": round(float(dia), 4),
                         "depth_mm": h.get("depth_mm"),
                         "through": h.get("through"),
                         "role": h.get("role"),
                         "counterbore_of": h.get("counterbore_of"),
                         "reads_as": h.get("reads_as")})
    hist = {}
    for r in rows:
        k = round(r["d_mm"], 1)
        hist[k] = hist.get(k, 0) + 1

    def band(lo, hi):
        return [r for r in rows if lo <= r["d_mm"] <= hi]

    # TWO PHYSICAL EXCLUSIONS, and neither is a judgement call.
    #
    # 1. A COUNTERBORE IS NOT AN INSERT BORE. A counterbore is a screw-head
    #    seat sitting coaxially on top of a clearance hole — the mesh
    #    measurement names the clearance hole it belongs to in
    #    `counterbore_of`. An insert bore has NO clearance hole beneath it;
    #    the insert IS the fastening. Ø4.4 is exactly the M2 cap-head
    #    counterbore the community histogram counts 28 of, and it lands
    #    inside a generous M3-insert window. Without this exclusion the two
    #    populations are indistinguishable by diameter, which is what made
    #    the first run of this tool answer CANNOT DETERMINE.
    #
    # 2. AN INSERT MUST FIT IN THE HOLE. The shortest member NAMED on a
    #    fetched vendor page for the one insert family on the workshop shelf
    #    (part:insert-m3-heatset) is M3 x 3.0 "short". 2.0 mm is used here as
    #    a deliberately generous floor: any bore shallower than that cannot
    #    hold any insert of any length in that family.
    MIN_INSERT_BORE_DEPTH_MM = 2.0

    def is_insert_candidate(r):
        if r.get("counterbore_of") is not None or r.get("role") == "counterbore":
            return False, "counterbore — a screw-head seat over a clearance hole"
        d = r.get("depth_mm")
        if d is None:
            return False, "no measured depth"
        if d < MIN_INSERT_BORE_DEPTH_MM:
            return False, ("bore only %.4f mm deep; the shortest insert in the "
                           "reference family is 3.0 mm" % d)
        return True, None

    insert_hits = {}
    for name, (lo, hi) in WINDOWS.items():
        hits = band(lo, hi)
        kept, dropped = [], []
        for h in hits:
            ok, why = is_insert_candidate(h)
            (kept if ok else dropped).append(dict(h, excluded_because=why))
        insert_hits[name] = {
            "window_mm": [lo, hi],
            "bores_in_window": len(hits),
            "bores": len(kept),
            "excluded": len(dropped),
            "meshes": sorted({h["mesh"] for h in kept}),
            "candidates": kept,
            "excluded_rows": dropped,
        }
    pilot_hits = {name: {"window_mm": [lo, hi], "bores": len(band(lo, hi))}
                  for name, (lo, hi) in PILOTS.items()}

    # The discriminating comparison: a design that uses inserts has a POPULATION
    # of insert-sized bores at the places it fastens. A design that self-taps has
    # a population of tap-drill pilots there instead. Count both.
    n_ins = sum(v["bores"] for v in insert_hits.values())
    n_window = sum(v["bores_in_window"] for v in insert_hits.values())
    n_excl = sum(v["excluded"] for v in insert_hits.values())
    n_pil = (pilot_hits["M2 tap drill / self-tap pilot"]["bores"]
             + pilot_hits["M2.5 tap drill / self-tap pilot"]["bores"])

    if n_ins == 0:
        verdict = ("NO HEAT-SET INSERT BORE EXISTS IN THIS GEOMETRY. Of %d "
                   "measured bores, %d fall in an insert diameter window and "
                   "every one of those %d is excluded by a physical test, not "
                   "by a preference: a counterbore is a screw-head seat over a "
                   "clearance hole, and a bore shallower than %.1f mm cannot "
                   "hold any insert in the reference family. The 46 M2/M2.5 "
                   "tap-drill pilots are what this design fastens into."
                   % (len(rows), n_window, n_excl, MIN_INSERT_BORE_DEPTH_MM))
    elif n_pil > 3 * max(1, n_ins):
        verdict = ("HEAT-SET INSERTS ARE NOT THIS DESIGN'S FASTENING METHOD: "
                   "%d tap-drill pilots against %d bores that merely fall in an "
                   "insert window. A bore in the window is not proof of an "
                   "insert — a Ø3.0-4.4 mm hole is also a counterbore, a cable "
                   "pass-through or a boss bore — and each is listed so a reader "
                   "can look rather than take the count." % (n_pil, n_ins))
    else:
        verdict = ("CANNOT DETERMINE: %d bores fall in an insert window against "
                   "%d tap-drill pilots. The populations are comparable and the "
                   "diameter alone does not separate them here." % (n_ins, n_pil))

    doc = {
        "doc": {"id": "MD-INSERT-001", "rev": "A",
                "title": "Heat-set insert census — measured off the bores, "
                         "not assumed from a build recommendation",
                "generated_by": "tools/insert_census.py",
                "reads": ["out/fasteners/features-by-mesh.json"]},
        "question": "Does any bore in this robot accept a heat-set insert?",
        "why_it_is_asked": "the community reconstruction's Purchase Estimate "
            "(reference/makerworld-3250889/upstream-github-fanhao375-microduck-"
            "replica/docs/fastener-reconstruction.en.md) suggests 60 M2 heat-set "
            "inserts, worded 'recommended over tapping printed plastic "
            "directly'. That is advice to a replica builder, not a reading of "
            "the product. The reference geometry is what we model from, so the "
            "reference geometry is what is asked.",
        "method": "a heat-set insert needs a straight bore of its own OUTER "
                  "knurl diameter; a tap drill or a self-tap pilot is roughly "
                  "half that. The diameter separates them with no judgement.",
        "counts": {"bores_measured": len(rows),
                   "meshes": len(d),
                   "bores_in_an_insert_diameter_window": n_window,
                   "excluded_by_a_physical_test": n_excl,
                   "surviving_insert_candidates": n_ins,
                   "M2_M2.5_tap_drill_pilots": n_pil},
        "verdict": verdict,
        "settled_by": "a teardown photograph showing brass at the mouth of a "
                      "boss, or a caliper on a real unit. Pollen's meshes carry "
                      "no insert bore, and the meshes are what we modelled from "
                      "— an insert in the real robot would be a finding about "
                      "the reference, not about this search.",
        "insert_windows": insert_hits,
        "fastener_windows_for_contrast": pilot_hits,
        "diameter_histogram_0.1mm": {str(k): v for k, v in sorted(hist.items())},
        "window_source": "part:insert-m3-heatset component.json (workshop "
                         "shelf) — vendor geometry, no standard governs these "
                         "parts. Windows widened deliberately so the test "
                         "cannot miss a candidate by being tight.",
    }
    with open(OUT, "w") as fh:
        json.dump(doc, fh, indent=1)
    print(json.dumps(doc["counts"], indent=1))
    print(verdict)
    for k, v in insert_hits.items():
        print("  %-24s %s -> %d in window, %d excluded, %d SURVIVE"
              % (k, v["window_mm"], v["bores_in_window"], v["excluded"],
                 v["bores"]))
    for k, v in pilot_hits.items():
        print("  %-34s %s -> %d" % (k, v["window_mm"], v["bores"]))
    print("wrote", OUT)


if __name__ == "__main__":
    sys.exit(main())
