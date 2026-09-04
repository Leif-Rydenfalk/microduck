"""wire_channel — DOES THE CABLE GO THROUGH A CHANNEL THAT EXISTS, OR THROUGH
A CREVICE WE ONLY DISCOVERED BY SEARCHING?

    ce-cad/bin/cad sim/wire_channel.py

route3d.py proves a centreline pierces nothing and clears a stated floor. That
is not the same question as this one. A path can clear 1.0000 mm everywhere and
still be a path no assembler could ever lay a cable into: a 4 mm slot between
two shells that only exists because those two shells happen not to touch. A
DESIGNED channel is a hole in ONE part -- somebody drew it for a cable. An
incidental crevice is the gap BETWEEN parts. The difference is visible from
inside the hole, so this pass looks from inside it.

METHOD -- ray marching in the same 1.0000 mm occupancy the route was planned in
(/private/tmp/int-wire3d/occ.npz, route3d_grid.py), which also carries an OWNER
field naming the placed row every solid cell came from.

  THE STUBS ARE EXCLUDED, and the first run of this pass proves why. From the
  connector point the centreline runs straight out through the housing to the
  first clear cell -- stub_from_mm / stub_to_mm in cables3d.json -- and that
  length is INSIDE the servo case or the board by construction. Measured with
  the stubs in, eight runs reported a 0.5000 mm aperture: both antipodal rays
  hitting on their first 0.2500 mm step, i.e. the sample sitting in the
  connector's own housing. route3d_exact.py excludes the same stubs for the
  same reason and says so in its limits.

  At every sample along the centreline, 64 directions on a Fibonacci sphere
  (32 antipodal pairs) are marched at 0.2500 mm out to 15.0000 mm.
    enclosure   = the fraction of directions that hit something inside 15 mm.
    aperture    = min over antipodal PAIRS of (hit + hit): the narrowest free
                  width through that point, which is what the cable has to fit
                  in. Reported surface-to-surface against the bundle OD.
    who         = the placed parts the hits belong to.
  and the sample is classified:
    CHANNEL   enclosure >= 0.75 and ONE part owns >= 0.75 of the hits -- the
              cable is inside a hole in that part. Somebody drew this.
    CREVICE   enclosure >= 0.50 and the top two parts each own >= 0.20 -- the
              cable is in the gap between two parts, which is not a channel and
              nobody drew it.
    OPEN      anything else -- the cable is beside things, not inside anything.

AND THE SECOND QUESTION, which is where the modelling errors are. For every run
the STRAIGHT line between the two launch points is marched through the same
grid. Where it is inside material, the part and the thickness of what it goes
through are recorded, and the detour the router paid to get round it is the
difference between the routed length and that straight line. A run whose
ordered cable is far shorter than its route is a run where either the real part
has a pass-through our mesh set does not, or the connector we are launching
from is in the wrong place. This pass names the wall.
"""
import json, math, os, sys
from collections import Counter

import numpy as np

R = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck"
OUT = R + "/out/wiring/channel.json"
OCC = "/private/tmp/int-wire3d/occ.npz"
LABELS = "/private/tmp/int-wire3d/labels.json"

NDIR_PAIRS = 32
RAY_MAX = 15.0
RAY_STEP = 0.25
SAMPLE_MM = 1.0
ENCLOSED = 0.75
CREVICE_ENC = 0.50
DOMINANT = 0.75
SHARE = 0.20


def fib_pairs(n):
    """n antipodal direction PAIRS, from a Fibonacci hemisphere."""
    d = []
    ga = math.pi * (3.0 - math.sqrt(5.0))
    for i in range(n):
        z = 1.0 - (i + 0.5) / n          # 1 -> 0, upper hemisphere
        r = math.sqrt(max(0.0, 1.0 - z * z))
        th = ga * i
        d.append((r * math.cos(th), r * math.sin(th), z))
    return np.array(d, float)


class Grid:
    def __init__(self):
        z = np.load(OCC)
        self.g = z["grid"].astype(bool)
        self.own = z["owner"]
        self.edt = z["edt"]
        self.lo = z["lo"]
        self.cell = float(z["cell"][0])
        self.shape = np.array(self.g.shape)
        self.labels = json.load(open(LABELS))
        rows = json.load(open(R + "/ce-assemblies/microduck/current/placements.json"))["record"]["rows"]
        self.row_part = {i + 1: (r.get("part") or r.get("mesh") or "row%d" % i) for i, r in enumerate(rows)}
        self.row_mesh = {i + 1: (r.get("mesh") or r.get("part")) for i, r in enumerate(rows)}

    def idx(self, P):
        c = np.floor((np.asarray(P, float) - self.lo) / self.cell).astype(int)
        return np.clip(c, 0, self.shape - 1)

    def solid(self, P):
        c = self.idx(P)
        return self.g[c[..., 0], c[..., 1], c[..., 2]]

    def owner(self, P):
        c = self.idx(P)
        return self.own[c[..., 0], c[..., 1], c[..., 2]]

    def dist(self, P):
        c = self.idx(P)
        return self.edt[c[..., 0], c[..., 1], c[..., 2]]

    def march(self, p, dirs):
        """(hit distance per direction, owner row per direction). RAY_MAX = miss."""
        steps = np.arange(RAY_STEP, RAY_MAX + 1e-9, RAY_STEP)
        pts = p[None, None, :] + dirs[:, None, :] * steps[None, :, None]
        sol = self.solid(pts)                       # (ndir, nstep)
        own = self.owner(pts)
        hit = np.full(len(dirs), RAY_MAX)
        who = np.zeros(len(dirs), int)
        any_hit = sol.any(axis=1)
        first = np.argmax(sol, axis=1)
        hit[any_hit] = steps[first[any_hit]]
        who[any_hit] = own[np.arange(len(dirs))[any_hit], first[any_hit]]
        return hit, who


def resample(poly, step):
    P = np.asarray(poly, float)
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    P = np.vstack([P[0], P[1:][seg > 1e-9]])
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    s = np.concatenate([[0.0], np.cumsum(seg)])
    n = max(2, int(round(s[-1] / step)) + 1)
    t = np.linspace(0.0, s[-1], n)
    return np.stack([np.interp(t, s, P[:, k]) for k in range(3)], axis=1), float(s[-1])


def load_paths():
    out, prov = {}, {}
    for name in ("paths.json", "paths-hat.json"):
        p = os.path.join(R, "out/wiring", name)
        if os.path.exists(p):
            for k, v in json.load(open(p))["record"]["paths"].items():
                out[k], prov[k] = v, name
    return out, prov


def load_c3():
    prev = {}
    for name in ("cables3d.json", "cables3d-hat.json"):
        p = os.path.join(R, "out/wiring", name)
        if os.path.exists(p):
            for c in json.load(open(p))["record"]["cables"]:
                prev[c["id"]] = c
    return prev


def main():
    G = Grid()
    half = fib_pairs(NDIR_PAIRS)
    dirs = np.vstack([half, -half])
    paths, prov = load_paths()
    c3 = load_c3()
    cab = json.load(open(R + "/wiring/cables.json"))["record"]
    by_id = {c["id"]: c for c in cab["cables"]}

    rows = []
    for rid in sorted(paths):
        rec = paths[rid]
        od = float(rec["od_mm"])
        P, L = resample(rec["polyline_mm"], SAMPLE_MM)
        c = c3.get(rid) or {}
        sf = float(c.get("stub_from_mm") or 0.0)
        st = float(c.get("stub_to_mm") or 0.0)
        arc = np.arange(len(P)) * SAMPLE_MM
        keep = (arc >= sf) & (arc <= L - st)
        if keep.sum() < 3:
            keep = np.ones(len(P), bool)
            stub_note = "stubs NOT excluded: doing so would leave under 3 samples"
        else:
            stub_note = ("stubs excluded: %.4f mm at the %s end and %.4f mm at the %s end, "
                         "both inside a housing by construction" % (sf, by_id[rid]["from"] if rid in by_id else "from",
                                                                    st, by_id[rid]["to"] if rid in by_id else "to"))
        P = P[keep]
        cls, aps, encs = [], [], []
        detail = []
        for p in P:
            hit, who = G.march(p, dirs)
            enc = float((hit < RAY_MAX - 1e-9).mean())
            pair = hit[:NDIR_PAIRS] + hit[NDIR_PAIRS:]
            k = int(np.argmin(pair))
            ap = float(pair[k])
            parts = Counter(G.row_part.get(int(w)) for w, h in zip(who, hit) if h < RAY_MAX - 1e-9)
            tot = sum(parts.values()) or 1
            top = parts.most_common(2)
            if enc >= ENCLOSED and top and top[0][1] / tot >= DOMINANT:
                c = "CHANNEL"
            elif enc >= CREVICE_ENC and len(top) >= 2 and top[1][1] / tot >= SHARE:
                c = "CREVICE"
            else:
                c = "OPEN"
            cls.append(c); aps.append(ap); encs.append(enc)
            detail.append((ap, c, enc, [t[0] for t in top], p))
        cc = Counter(cls)
        i = int(np.argmin(aps))
        ap_min, c_min, enc_min, who_min, at_min = detail[i]
        # aperture is centre-to-surface both ways; the cable needs its own OD
        free_min = ap_min - od
        rows.append({
            "id": rid, "path_from": prov[rid], "od_mm": od, "length_mm": round(L, 4),
            "stub_from_mm": round(sf, 4), "stub_to_mm": round(st, 4), "stub_note": stub_note,
            "samples": len(P), "sample_step_mm": SAMPLE_MM,
            "rays_per_sample": int(len(dirs)), "ray_max_mm": RAY_MAX,
            "classes": dict(cc),
            "pct_CHANNEL": round(100.0 * cc.get("CHANNEL", 0) / len(P), 2),
            "pct_CREVICE": round(100.0 * cc.get("CREVICE", 0) / len(P), 2),
            "pct_OPEN": round(100.0 * cc.get("OPEN", 0) / len(P), 2),
            "min_aperture_mm": round(ap_min, 4),
            "min_aperture_minus_od_mm": round(free_min, 4),
            "min_aperture_at_mm": [round(float(x), 4) for x in at_min],
            "min_aperture_class": c_min,
            "min_aperture_bounded_by": who_min,
            "min_aperture_enclosure": round(enc_min, 3),
            "median_aperture_mm": round(float(np.median(aps)), 4),
        })

    # ---- the second question: what wall does the straight line hit? ---------
    walls = []
    for rid in sorted(paths):
        c = c3.get(rid) or {}
        ends = c.get("ends") or []
        if len(ends) != 2:
            continue
        a = np.array(ends[0].get("launch_mm") or ends[0].get("connector_xyz_mm"), float)
        b = np.array(ends[1].get("launch_mm") or ends[1].get("connector_xyz_mm"), float)
        Lst = float(np.linalg.norm(b - a))
        n = int(Lst / 0.25) + 2
        t = np.linspace(0, 1, n)
        pts = a[None, :] + (b - a)[None, :] * t[:, None]
        sol = G.solid(pts)
        own = G.owner(pts)
        runs_in = []
        k = 0
        while k < n:
            if sol[k]:
                j = k
                while j < n and sol[j]:
                    j += 1
                seg_owner = Counter(G.row_part.get(int(w)) for w in own[k:j])
                runs_in.append({"thickness_mm": round((j - k) * Lst / (n - 1), 4),
                                "at_mm": [round(float(x), 4) for x in pts[(k + j) // 2]],
                                "part": seg_owner.most_common(1)[0][0]})
                k = j
            else:
                k += 1
        routed = c.get("routed_length_mm")
        ordered = (by_id.get(rid) or {}).get("cable_mm")
        walls.append({
            "id": rid, "straight_launch_to_launch_mm": round(Lst, 4),
            "routed_length_mm": routed,
            "detour_mm": (None if routed is None else round(routed - Lst, 4)),
            "detour_ratio": (None if routed is None or Lst <= 0 else round(routed / Lst, 4)),
            "ordered_cable_mm": ordered,
            "straight_line_pierces": runs_in,
            "pierced_total_mm": round(sum(r["thickness_mm"] for r in runs_in), 4),
            "parts_pierced": sorted({r["part"] for r in runs_in}),
        })

    counts = {
        "runs": len(rows),
        "runs_with_any_CHANNEL_sample": sum(1 for r in rows if r["classes"].get("CHANNEL")),
        "runs_that_are_mostly_OPEN": sum(1 for r in rows if r["pct_OPEN"] >= 50),
        "runs_whose_TIGHTEST_point_is_a_CHANNEL": sum(1 for r in rows if r["min_aperture_class"] == "CHANNEL"),
        "runs_whose_TIGHTEST_point_is_a_CREVICE": sum(1 for r in rows if r["min_aperture_class"] == "CREVICE"),
        "runs_whose_TIGHTEST_point_is_OPEN": sum(1 for r in rows if r["min_aperture_class"] == "OPEN"),
        "runs_whose_tightest_aperture_is_under_the_bundle": sum(1 for r in rows if r["min_aperture_minus_od_mm"] < 0),
        "total_samples_classified": sum(r["samples"] for r in rows),
        "samples_CHANNEL": sum(r["classes"].get("CHANNEL", 0) for r in rows),
        "samples_CREVICE": sum(r["classes"].get("CREVICE", 0) for r in rows),
        "samples_OPEN": sum(r["classes"].get("OPEN", 0) for r in rows),
        "runs_whose_straight_line_pierces_material": sum(1 for w in walls if w["straight_line_pierces"]),
        "runs_with_a_detour_over_2x": sum(1 for w in walls if (w["detour_ratio"] or 0) >= 2.0),
    }
    out = {"$triad": 1, "kind": "wire-channel", "generated_by": "sim/wire_channel.py",
           "record": {"units": "mm", "method": __doc__.strip(), "counts": counts,
                      "runs": rows, "walls": walls}}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w"), indent=1)
    print(json.dumps(counts, indent=1))
    print()
    for r in rows:
        print("%-22s ap=%-9s -od=%-9s %-8s %-6s CH%%=%-6s CR%%=%-6s OP%%=%-6s %s" % (
            r["id"], r["min_aperture_mm"], r["min_aperture_minus_od_mm"], r["min_aperture_class"],
            r["min_aperture_enclosure"], r["pct_CHANNEL"], r["pct_CREVICE"], r["pct_OPEN"],
            ",".join(str(x) for x in r["min_aperture_bounded_by"])[:52]))
    print()
    for w in walls:
        print("%-22s straight=%-9s routed=%-9s x%-7s ordered=%-6s pierced=%-8s %s" % (
            w["id"], w["straight_launch_to_launch_mm"], w["routed_length_mm"], w["detour_ratio"],
            w["ordered_cable_mm"], w["pierced_total_mm"], ",".join(w["parts_pierced"])[:60]))
    print("wrote", OUT)


main()
