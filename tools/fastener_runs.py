#!/usr/bin/env python3
"""fastener_runs.py — every FASTENER RUN in the assembled robot, measured.

    python3 tools/fastener_runs.py     ->  out/fasteners/runs.json  + a table

Runs under plain python3; no CAD kernel needed.

WHAT A "RUN" IS AND WHY IT IS THE UNIT THAT MATTERS
---------------------------------------------------
A hole is not a screw. A SCREW is a coaxial chain of holes through one or more
parts, entered at a head seat and terminated by something the thread bites into.
Counting holes double-counts (a counterbore and its clearance hole are one
screw) and cannot give a LENGTH. Counting RUNS gives both, and it is the only
way to say "M2 x 6" rather than "an M2 somewhere here".

The replica author's own reconstruction says the same thing in its Limitations
section 3 — "Counterbores and clearance holes may be double-counted (two
features of the same screw)" —
reference/makerworld-3250889/upstream-github-fanhao375-microduck-replica/docs/fastener-reconstruction.en.md:96-98.

WHAT IT READS, and it invents nothing:
    out/fasteners/features-by-mesh.json   cecad.meshfeatures.features() of every
                                          placed mesh, in the mesh's own frame:
                                          d_mm, class, size, depth, axis,
                                          center, extent along the axis
    out/fasteners/world-placements.json   the MJCF zero-pose world frame (R, t)
                                          of every placed mesh

THE ARITHMETIC, stated so it can be checked:
    A point p in a mesh frame lands at  p_w = R p + t.
    An axis a lands at  a_w = R a  (R is a rotation, so |a_w| = |a| = 1).
    features-by-mesh records extent_along_axis_mm as the scalar s = p . a of the
    cylinder's two ends. In world that becomes  s_w = s + t . a_w, because
    (R p + t) . (R a) = p . a + t . R a. No approximation anywhere.

WHAT IT REFUSES:
    A run with no thread-taking feature gets NO length and NO screw. It is a
    named CANNOT DETERMINE that says what would settle it. A guessed length is a
    wrong purchase order and, once rendered, a believed one.
"""
import collections
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FEAT = os.path.join(ROOT, "out", "fasteners", "features-by-mesh.json")
WORLD = os.path.join(ROOT, "out", "fasteners", "world-placements.json")
OUT = os.path.join(ROOT, "out", "fasteners", "runs.json")

# Two axes are the same axis when they are parallel to better than this and
# their lines pass this close. 0.9997 is 1.40 deg; 0.30 mm is under half an FDM
# extrusion width, so two features this close cannot be separate screws.
PARALLEL_MIN = 0.9997
OFFAXIS_MAX_MM = 0.30

# Lengths with a fetched-and-read offer on ce-parts/screw-m2-iso4762 and
# screw-m2.5-iso4762 (component.json family.lengths_mm_verified_on_a_fetched_page).
STOCKED_MM = {"M2": [3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 20.0],
              "M2.5": [3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 20.0]}
NOMINAL_MM = {"M2": 2.0, "M2.5": 2.5, "M1.6": 1.6, "M3": 3.0, "M4": 4.0}

# A coaxial LINE can carry more than one screw. Two features on the same line
# separated by more air than the LONGEST SOURCED SCREW cannot be one screw, so
# the line is cut there. The threshold is not a taste: it is
# max(STOCKED_MM) = 20 mm, the longest length either family has an offer for.
CHAIN_BREAK_MM = 20.0

# Minimum thread engagement. This is a RULE, not a measurement of this robot,
# and it is labelled as one everywhere it appears: 1.5 x nominal diameter is
# the usual floor for a screw threading into a softer material (here PLA or the
# XL330's own engineering-plastic case). The BOTTOMING limit beside it IS a
# measurement — the pilot's own measured depth.
MIN_ENGAGE_D = 1.5

# What each measured hole class DOES in a run.
PASSES_THROUGH = {"clearance", "ambiguous"}   # the screw's shank passes
HEAD_SEAT = {"counterbore", "insert"}         # the head (or an insert) seats
TAKES_THREAD = {"pilot"}                      # the thread bites


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def matvec(R, v):
    return [dot(R[0], v), dot(R[1], v), dot(R[2], v)]


def add(a, b):
    return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]


def sub(a, b):
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]


def scale(v, k):
    return [v[0] * k, v[1] * k, v[2] * k]


def norm(v):
    return math.sqrt(dot(v, v))


def unit(v):
    n = norm(v)
    if n < 1e-12:
        raise ValueError("zero-length axis %r" % (v,))
    return scale(v, 1.0 / n)


def canonical(a):
    """Same line, one direction: first component of magnitude > 1e-6 made +."""
    for c in a:
        if abs(c) > 1e-6:
            return (a, 1) if c > 0 else (scale(a, -1.0), -1)
    return (a, 1)


def load():
    with open(FEAT, encoding="utf-8") as f:
        meshes = json.load(f)["meshes"]
    with open(WORLD, encoding="utf-8") as f:
        w = json.load(f)
    return meshes, w


def collect(meshes, world):
    """Every hole of every VISUALLY placed mesh, in the world frame."""
    holes, skipped = [], collections.Counter()
    for pl in world["placements"]:
        if pl.get("class") != "visual":
            skipped["not a visual placement (collision geometry duplicates it)"] += 1
            continue
        m = pl["mesh"]
        rec = meshes.get(m)
        if rec is None:
            skipped["mesh %s has no feature record" % m] += 1
            continue
        R, t = pl["R"], pl["t_mm"]
        for f in rec["features"]:
            if f.get("feature") != "hole":
                continue
            a_w = unit(matvec(R, f["axis"]))
            c_w = add(matvec(R, f["center_mm"]), t)
            ds = dot(t, a_w)
            lo, hi = f["extent_along_axis_mm"]
            a_c, sign = canonical(a_w)
            s_lo, s_hi = lo + ds, hi + ds
            if sign < 0:
                s_lo, s_hi = -s_hi, -s_lo
            holes.append(dict(
                mesh=m, body=pl["body"], geom_index=pl["geom_index"],
                index=f["index"], role=f.get("role"), d_mm=f.get("d_mm"),
                size=f.get("size"), cls=f.get("class"), reads_as=f.get("reads_as"),
                depth_mm=f.get("depth_mm"), through=f.get("through"),
                entry=f.get("entry"), counterbore_d_mm=f.get("counterbore"),
                axis_world=a_c, center_world=c_w, s_lo=s_lo, s_hi=s_hi,
                cover_deg=(f.get("fit") or {}).get("cover_deg"),
                residual_mm=(f.get("fit") or {}).get("residual_mm")))
    return holes, skipped


def split_chain(g):
    """One coaxial LINE -> one or more contiguous chains, cut at CHAIN_BREAK_MM."""
    g = sorted(g, key=lambda h: h["s_lo"])
    chains, cur, reach = [], [g[0]], g[0]["s_hi"]
    for h in g[1:]:
        if h["s_lo"] - reach > CHAIN_BREAK_MM:
            chains.append(cur)
            cur = []
        cur.append(h)
        reach = max(reach, h["s_hi"])
    chains.append(cur)
    return chains


def group(holes):
    """Union-find over the coaxiality relation. O(n^2) on 300-odd holes."""
    n = len(holes)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        a, b = find(i), find(j)
        if a != b:
            parent[b] = a

    for i in range(n):
        ai, ci = holes[i]["axis_world"], holes[i]["center_world"]
        for j in range(i + 1, n):
            aj, cj = holes[j]["axis_world"], holes[j]["center_world"]
            if abs(dot(ai, aj)) < PARALLEL_MIN:
                continue
            d = sub(cj, ci)
            perp = norm(sub(d, scale(ai, dot(d, ai))))
            if perp <= OFFAXIS_MAX_MM:
                union(i, j)
    out = collections.defaultdict(list)
    for i in range(n):
        out[find(i)].append(holes[i])
    return list(out.values())


def classify(g):
    """One coaxial group -> one run record with a verdict."""
    g = sorted(g, key=lambda h: h["s_lo"])
    meshes = sorted({h["mesh"] for h in g})
    bodies = sorted({h["body"] for h in g})
    sizes = collections.Counter(h["size"] for h in g if h["size"])
    seats = [h for h in g if h["cls"] in HEAD_SEAT]
    threads = [h for h in g if h["cls"] in TAKES_THREAD]
    passes = [h for h in g if h["cls"] in PASSES_THROUGH]
    run = dict(
        n_features=len(g), meshes=meshes, bodies=bodies,
        axis_world=g[0]["axis_world"],
        span_mm=[round(g[0]["s_lo"], 4), round(max(h["s_hi"] for h in g), 4)],
        # residual_mm and cover_deg travel with every feature: a downstream
        # check that compares a deficit against the fit's OWN noise cannot do it
        # without them, and dropping them made tools/fastener_audit.py call a
        # 0.012 mm interference a FAIL against a 0.0316 mm residual it could not
        # see (measured 2026-09-04).
        features=[{k: h[k] for k in ("mesh", "index", "role", "d_mm", "size",
                                     "cls", "depth_mm", "through", "s_lo", "s_hi",
                                     "center_world", "reads_as", "residual_mm",
                                     "cover_deg")} for h in g],
        size=(sizes.most_common(1)[0][0] if sizes else None),
        has_seat=bool(seats), has_thread=bool(threads), n_pass=len(passes))

    if not sizes:
        run.update(verdict="CANNOT DETERMINE", kind="unsized",
                   why="no feature in this coaxial group read as a fastener size; "
                       "it is a bore, a shaft seat or a cable pass-through, not a screw",
                   settled_by="a caliper on the printed part, or a section view naming what the bore is for")
        return run
    if not threads:
        # No pilot anywhere on the line: nothing to take a thread.
        run.update(verdict="CANNOT DETERMINE", kind="no thread partner",
                   why=("%d %s feature(s) on this line across %d mesh(es) %s, and NOT ONE "
                        "reads as a tap pilot. A screw needs something to bite: this run is "
                        "either a nut/insert position whose seat is not in the mesh, a "
                        "clearance for a shaft, or the mating part's pilot went undetected."
                        % (len(g), run["size"], len(meshes), ", ".join(meshes))),
                   settled_by=("look for a nut pocket or an insert boss on the far side in the "
                               "mesh, or measure the real part: does a screw thread into it?"))
        return run

    # THE SCREW. It enters from the end AWAY from the pilot it threads into.
    lo_end, hi_end = g[0]["s_lo"], max(h["s_hi"] for h in g)
    pilot_hi = max(threads, key=lambda h: h["s_hi"])
    pilot_lo = min(threads, key=lambda h: h["s_lo"])
    # which end of the chain is the thread at? the screw enters from the other.
    up = (pilot_lo["s_lo"] - lo_end) >= (hi_end - pilot_hi["s_hi"])
    pilot = pilot_lo if up else pilot_hi
    entry_side = [h for h in g if h["cls"] != "pilot"]
    if not entry_side:
        run.update(verdict="CANNOT DETERMINE", kind="pilot with no clearance",
                   why=("the only features on this chain are tap pilots (%d). A pilot with "
                        "nothing to clamp is a self-tapped boss waiting for a mating part "
                        "whose clearance hole was not detected." % len(threads)),
                   settled_by="the mating part's clearance hole, or a photo of what screws in here")
        return run
    if up:
        seat = min(entry_side, key=lambda h: h["s_lo"])
        # THE HEAD BEARS ON THE COUNTERBORE FLOOR, not on its mouth. A head seated
        # at the mouth costs the whole counterbore depth in screw length and was
        # this tool's first measured defect (2026-09-04: every run came out 2 mm
        # long and the servo screws read M2x14 against the reference's M2x6/8).
        s_head = seat["s_hi"] if seat["cls"] in HEAD_SEAT else seat["s_lo"]
        s_thread_start = pilot["s_lo"]
        s_thread_end = pilot["s_hi"]
        direction = list(run["axis_world"])
    else:
        seat = max(entry_side, key=lambda h: h["s_hi"])
        s_head = seat["s_lo"] if seat["cls"] in HEAD_SEAT else seat["s_hi"]
        s_thread_start = pilot["s_hi"]
        s_thread_end = pilot["s_lo"]
        direction = scale(run["axis_world"], -1.0)
    grip = abs(s_thread_start - s_head)
    engage_avail = abs(s_thread_end - s_thread_start)
    # ---- WHICH SCREW, AND IT IS DERIVED FROM THE HOLES, NOT VOTED ON ----
    # The first version took the commonest `size` label in the chain. That is a
    # majority vote among independent per-hole classifications and it produced a
    # screw that could not physically exist: MEASURED 2026-09-04, four runs
    # bearing_roll -> yaw2roll came out M2.5 from one Ø2.05 pilot outvoting one
    # Ø2.2 clearance — an M2.5 shank is Ø2.50 and cannot pass a Ø2.2 hole.
    # The geometry states the constraint directly: the shank must CLEAR every
    # clearance hole on the chain and must be LARGER than the pilot it forms a
    # thread in. Take the largest standard size that satisfies both, or refuse.
    clearances = [h["d_mm"] for h in g
                  if h["cls"] in PASSES_THROUGH and h["d_mm"] is not None]
    d_pilot = pilot["d_mm"]
    min_clear = min(clearances) if clearances else None
    cands = []
    for nm, dn in sorted(NOMINAL_MM.items(), key=lambda kv: -kv[1]):
        if nm not in STOCKED_MM:
            continue
        if min_clear is not None and dn >= min_clear:
            continue
        if d_pilot is not None and dn <= d_pilot:
            continue
        cands.append(nm)
    if not cands:
        run.update(verdict="CANNOT DETERMINE", kind="no screw fits this chain",
                   why=("NO standard screw satisfies this chain's own geometry. The shank must "
                        "clear the tightest clearance hole (Ø%s mm) and must be LARGER than the "
                        "pilot it forms a thread in (Ø%s mm); with the pilot that wide there is "
                        "nothing for a thread that also passes the clearance to bite. The per-hole "
                        "classifier labelled this chain %r by diameter alone; that label is not a "
                        "screw. Most likely the blind Ø%s feature is not a pilot at all — a "
                        "locating-pin bore or a boss seat reads the same to a diameter table."
                        % (min_clear, d_pilot, run["size"], d_pilot)),
                   settled_by=("a section view or a caliper on that blind feature: is a screw "
                               "threaded into it, or is it a pin seat? THE REAL ROBOT WORKS, so "
                               "this is a reading error somewhere, not a broken joint."),
                   size_candidates=[], min_clearance_mm=min_clear, pilot_d_mm=d_pilot)
        return run
    size = cands[0]
    d = NOMINAL_MM[size]
    run["size"] = size
    run["size_why"] = ("largest standard size whose shank Ø%.2f mm clears the tightest clearance "
                       "hole on the chain (Ø%s mm) and exceeds the pilot it bites (Ø%s mm). "
                       "Candidates that satisfy both: %s. Derived from the holes, not voted on."
                       % (d, min_clear, d_pilot, cands))
    l_min = grip + MIN_ENGAGE_D * d          # rule: 1.5d of thread, stated as a rule
    l_max = grip + engage_avail              # measurement: bottoming on the pilot floor
    stock = STOCKED_MM.get(size, [])
    window = [L for L in stock if l_min - 1e-9 <= L <= l_max + 1e-9]
    chosen = window[0] if window else None
    head_point = add(seat["center_world"],
                     scale(run["axis_world"],
                           s_head - dot(seat["center_world"], run["axis_world"])))
    run.update(
        verdict="PASS", kind="screw run",
        grip_mm=round(grip, 4), engagement_available_mm=round(engage_avail, 4),
        length_window_mm=[round(l_min, 4), round(l_max, 4)],
        length_window_why=("min = grip + %g d (RULE: minimum thread engagement in a softer "
                           "material, not a measurement of this robot). max = grip + the "
                           "pilot's own MEASURED depth %.4f mm, the point the screw bottoms."
                           % (MIN_ENGAGE_D, engage_avail)),
        cross_part=len({h["mesh"] for h in g}) > 1,
        head_seat_mesh=seat["mesh"], head_seat_class=seat["cls"],
        pilot_mesh=pilot["mesh"], pilot_d_mm=pilot["d_mm"],
        head_point_world_mm=[round(v, 4) for v in head_point],
        insertion_axis_world=[round(v, 6) for v in direction],
        stocked_length_mm=chosen,
        stocked_lengths_in_window_mm=window,
        length_why=("grip %.4f mm from the head seat on %s to the pilot face; the window "
                    "[%.4f, %.4f] mm holds the sourced %s lengths %s; the shortest is taken."
                    % (grip, seat["mesh"], l_min, l_max, size,
                       window if window else "NONE")),
        why=("%s: head seats on %s (%s), thread bites a Ø%s pilot on %s"
             % (size, seat["mesh"], seat["cls"], pilot["d_mm"], pilot["mesh"])))
    if chosen is None:
        run["verdict"] = "CANNOT DETERMINE"
        run["kind"] = "no sourced length inside the measured window"
        run["settled_by"] = ("a sourced offer inside [%.3f, %.3f] mm, or a re-measurement of "
                             "the grip / pilot depth that widens it" % (l_min, l_max))
    return run


def main():
    meshes, world = load()
    holes, skipped = collect(meshes, world)
    groups = group(holes)
    chains = [c for gp in groups for c in split_chain(gp)]
    runs = [classify(c) for c in chains]
    runs.sort(key=lambda r: (r["verdict"] != "PASS", -r["n_features"]))
    by_verdict = collections.Counter(r["verdict"] for r in runs)
    by_kind = collections.Counter(r["kind"] for r in runs)
    screws = [r for r in runs if r["verdict"] == "PASS"]
    by_len = collections.Counter("%s x %g" % (r["size"], r["stocked_length_mm"]) for r in screws)
    cross = sum(1 for r in screws if r["cross_part"])
    doc = dict(
        doc=dict(id="MD-FAST-RUN-001", rev="A",
                 title="Fastener runs — coaxial chains in the assembled world frame",
                 generated_by="tools/fastener_runs.py",
                 reads=["out/fasteners/features-by-mesh.json",
                        "out/fasteners/world-placements.json"]),
        method=dict(
            parallel_min=PARALLEL_MIN,
            parallel_min_deg=round(math.degrees(math.acos(PARALLEL_MIN)), 4),
            offaxis_max_mm=OFFAXIS_MAX_MM,
            chain_break_mm=CHAIN_BREAK_MM,
            min_engagement_d=MIN_ENGAGE_D,
            frame="MJCF world at zero pose, mm",
            world_transform="p_w = R p + t ; a_w = R a ; s_w = s + t . a_w",
            length_window="min = grip + 1.5 d (a RULE, labelled as one); "
                          "max = grip + the pilot's own measured depth (a MEASUREMENT). "
                          "Every sourced length inside the window is listed; the shortest is taken.",
            stocked_lengths=STOCKED_MM),
        counts=dict(
            holes_in_world=len(holes),
            visual_placements=sum(1 for p in world["placements"] if p.get("class") == "visual"),
            coaxial_groups=len(groups),
            chains_after_the_20_mm_cut=len(chains),
            runs=len(runs),
            screw_runs=len(screws),
            screw_runs_crossing_two_meshes=cross,
            by_verdict=dict(by_verdict), by_kind=dict(by_kind),
            by_screw=dict(by_len)),
        skipped={k: v for k, v in skipped.items()},
        runs=runs)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1)
    print("holes placed in world      :", len(holes))
    print("coaxial lines              :", len(groups), "-> chains after the %g mm cut: %d" % (CHAIN_BREAK_MM, len(chains)))
    print("screw runs (PASS)          :", len(screws), "of which cross two meshes:", cross)
    for k, v in by_kind.most_common():
        print("  %-32s %d" % (k, v))
    print("screws by size x length    :", dict(by_len))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
