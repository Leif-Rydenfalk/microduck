"""connection:press-fit-sole-foot -- will this sole actually stay on this foot?

Contract (TRIAD.md, ce-connections section):

    def compatible(a_iface, b_iface) -> dict
        {"verdict": "PASS" | "FAIL" | "CANNOT DETERMINE", "why": ..., "checks": [...]}

Shaped after ce-connections/press-fit-bearing-15x10x3, and it inherits that
folder's honesty about printed parts without inheriting its ISO 286 module,
which does not apply here for two measured reasons:

  1. the socket is TPU -- an ELASTOMER. An IT grade describes a rigid
     body's size, and an elastomer's grip is set by its modulus and its
     as-printed wall, neither of which is a tolerance class.
  2. the modelled clearance is EXACTLY ZERO. 150 gaps measured on 75
     caliper lines run through both meshes span -0.0020..+0.0020 mm about
     a mean of -0.000007 mm. There is no allowance to grade.

So this module grades what geometry CAN settle -- that the two sections are
the same rectangle, that the walls are coincident, that the socket is deep
enough, that the floor is there -- and refuses the pull-off force by name.

Every number is MEASURED and frozen in evidence/sole-foot-fit.json
(cecad.meshfeatures.intervals ray-cast calipers and cecad.meshslice
sections on Pollen's own meshes, 2026-09-02). Nothing here is recalled.

    python3 compat.py

Python 3 stdlib only. Units: mm.
"""

import json

SECTION_MM = (36.8, 49.8)
CLEARANCE_SPAN_MM = (-0.002, 0.002)
CLEARANCE_MEAN_MM = -0.000007
CLEARANCE_STATIONS = 75
CLEARANCE_GAPS = 150
STL_RESOLUTION_MM = 0.002
WALL_MEAN_MM = 2.0165
WALL_SPAN_MM = (1.594, 2.479)
FLOOR_MM = (1.999, 2.001)
DEPTH_MM = (7.917, 10.655)
RIM_Z_MM = -18.3419
RIB_OVERLAP_MM = 0.2539

PLUG_NAMES = ("sole_skirt", "skirt", "plug")
SOCKET_NAMES = ("foot_socket", "socket", "cavity")

WORST = {"PASS": 0, "CANNOT DETERMINE": 1, "FAIL": 2}


def _field(iface, key, *aliases):
    if not isinstance(iface, dict):
        return None
    measured = iface.get("measured")
    if not isinstance(measured, dict):
        measured = {}
    for k in (key,) + aliases:
        v = iface.get(k)
        if v is not None:
            return v
        v = measured.get(k)
        if v is not None:
            return v
    return None


def compatible(a_iface, b_iface):
    """a_iface is the foot's plug; b_iface is the sole's socket."""
    checks = []

    def add(name, verdict, measured, note=None):
        checks.append({"check": name, "verdict": verdict, "measured": measured,
                       "note": note})

    a_name, a_role = _field(a_iface, "name"), _field(a_iface, "role")
    b_name, b_role = _field(b_iface, "name"), _field(b_iface, "role")
    if a_name not in PLUG_NAMES and a_role != "skirt":
        add("interface_names", "FAIL", {"a": {"name": a_name, "role": a_role}},
            "a_iface must be the foot's plug: name one of %s or role 'skirt'."
            % ", ".join(repr(n) for n in PLUG_NAMES))
        return _finish(checks)
    if b_name not in SOCKET_NAMES and b_role != "socket":
        add("interface_names", "FAIL", {"b": {"name": b_name, "role": b_role}},
            "b_iface must be the sole's socket: name one of %s or role 'socket'."
            % ", ".join(repr(n) for n in SOCKET_NAMES))
        return _finish(checks)
    add("interface_names", "PASS", {"a": a_name, "b": b_name})

    # 1. same rectangle ---------------------------------------------------
    sa = _field(a_iface, "section_mm", "size_mm")
    sb = _field(b_iface, "section_mm", "size_mm")
    if sa is None or sb is None:
        add("section", "CANNOT DETERMINE", {"a": sa, "b": sb},
            "an interface that does not state its section cannot be fitted to "
            "anything. The slug is not a measurement.")
    else:
        sa = sorted(float(v) for v in sa)
        sb = sorted(float(v) for v in sb)
        want = sorted(SECTION_MM)
        d_self = max(abs(sa[i] - sb[i]) for i in range(2))
        d_ref = max(max(abs(sa[i] - want[i]), abs(sb[i] - want[i])) for i in range(2))
        if d_ref > 0.5:
            add("section", "FAIL", {"a_mm": sa, "b_mm": sb, "reference_mm": want},
                "this folder joins the %s x %s mm foot prism only."
                % SECTION_MM)
        elif d_self > 0.05:
            add("section", "FAIL", {"a_mm": sa, "b_mm": sb,
                                    "disagreement_mm": round(d_self, 4)},
                "the two sections differ by more than 0.05 mm. The reference "
                "pair is coincident to %.3f mm; a pair that does not agree at "
                "that scale is not this joint." % STL_RESOLUTION_MM)
        else:
            add("section", "PASS", {"a_mm": sa, "b_mm": sb,
                                    "disagreement_mm": round(d_self, 4)})

    # 2. the fit ----------------------------------------------------------
    gap = _field(b_iface, "measured_gap_mm", "as_printed_gap_mm")
    if gap is not None:
        gap = float(gap)
        add("fit", "PASS" if gap <= 0.0 else "CANNOT DETERMINE",
            {"as_built_gap_mm": gap},
            "graded from a MEASURED as-built gap. Negative is interference "
            "(the sole stretches on); positive is clearance, and a positive "
            "clearance on a joint with no fastener means the sole is held by "
            "nothing -- which this module will not call a pass.")
    else:
        add("fit", "PASS",
            {"modelled_gap_span_mm": list(CLEARANCE_SPAN_MM),
             "modelled_gap_mean_mm": CLEARANCE_MEAN_MM,
             "stations": CLEARANCE_STATIONS, "gaps": CLEARANCE_GAPS,
             "stl_resolution_mm": STL_RESOLUTION_MM},
            "ZERO CLEARANCE, measured on both sides on the SAME lines: %d gaps "
            "from %d ray-cast caliper stations span %.3f..%.3f mm about a mean "
            "of %.6f mm -- the two walls are one surface to the resolution the "
            "decimated STL can express. This grades the MODEL. It does not "
            "grade an as-built pair: state measured_gap_mm on the socket and "
            "this check grades the real one."
            % (CLEARANCE_GAPS, CLEARANCE_STATIONS, CLEARANCE_SPAN_MM[0],
               CLEARANCE_SPAN_MM[1], CLEARANCE_MEAN_MM))

    # 3. depth of engagement ----------------------------------------------
    depth = _field(b_iface, "depth_mm", "socket_depth_mm")
    dmin = min(DEPTH_MM) if depth is None else float(depth)
    ratio = dmin / min(SECTION_MM)
    add("engagement_depth", "PASS" if dmin >= 5.0 else "CANNOT DETERMINE",
        {"depth_mm": round(dmin, 4), "depth_span_mm": list(DEPTH_MM),
         "short_side_mm": min(SECTION_MM), "depth_over_short_side": round(ratio, 4)},
        "%.4f mm at the toe rising to %.4f mm at the heel (the outer floor "
        "slopes 0.087 and the inner floor follows it), against a %.1f mm short "
        "side -- a depth-to-width ratio of %.3f. Deep enough that the joint is "
        "a socket and not a lip; how much it matters for retention is the "
        "pull-off question this module refuses."
        % (DEPTH_MM[0], DEPTH_MM[1], min(SECTION_MM), ratio))

    # 4. the wall and the floor -------------------------------------------
    add("socket_section", "PASS",
        {"wall_mean_mm": WALL_MEAN_MM, "wall_span_mm": list(WALL_SPAN_MM),
         "floor_mm": list(FLOOR_MM), "rim_z_mm": RIM_Z_MM},
        "wall %.4f mm mean (2.1000 plateau on the long walls), floor 2.000 "
        "+/- 0.001 mm of TPU at nine independent stations -- which agrees with "
        "the sole folder's own 27x31 floor grid measured a different way. Two "
        "instruments, one number." % WALL_MEAN_MM)

    # 5. the rib overlap ---------------------------------------------------
    add("rib_landing", "CANNOT DETERMINE",
        {"overlap_mm": RIB_OVERLAP_MM,
         "foot_lowest_z_mm": -29.2509, "sole_floor_top_z_mm": -28.997},
        "the foot's ribs reach %.4f mm BELOW the sole's inner floor at the "
        "deepest station (x 35, y 15). Two readings fit: deliberate squeeze "
        "into the elastomer, or an overlap in the visual meshes. Nothing "
        "separates them here -- the MJCF holds two rigid geoms and resolves no "
        "penetration. What settles it: measure a real pair, or ask whether the "
        "sole's floor is compressed when the foot is home."
        % RIB_OVERLAP_MM)

    # 6. retention ---------------------------------------------------------
    pull = _field(b_iface, "pull_off_N")
    if pull is not None:
        add("retention", "PASS", {"pull_off_N": float(pull)},
            "a measured pull-off force was supplied.")
    else:
        add("retention", "CANNOT DETERMINE",
            {"pull_off_N": None, "fasteners": 0, "socket_material": "TPU",
             "plug_material": "PLA"},
            "NO fastener, barb, groove or adhesive exists on either mesh "
            "(cecad.meshfeatures.cylinders finds no hole through the socket "
            "wall or floor; the ankle group's single M2 at x 50.0000, y 4.5020 "
            "hangs the FOOT from the ankle and never enters the sole). So the "
            "sole is held by friction alone, at a modelled clearance of zero, "
            "between a printed elastomer and a printed rigid part -- a grip "
            "set by two processes' as-built dimensions and the TPU's modulus, "
            "none of which is in any file here. What settles it: pull a real "
            "sole off a real foot on a gauge and state pull_off_N.")

    return _finish(checks)


def _finish(checks):
    worst = max((c["verdict"] for c in checks), key=lambda v: WORST[v])
    fails = [c["check"] for c in checks if c["verdict"] == "FAIL"]
    unknown = [c["check"] for c in checks if c["verdict"] == "CANNOT DETERMINE"]
    if worst == "PASS":
        why = "all %d checks PASS" % len(checks)
    elif worst == "FAIL":
        why = "FAILING: %s. (CANNOT DETERMINE: %s)" % (", ".join(fails),
                                                       ", ".join(unknown) or "none")
    else:
        why = ("no check FAILS, but %d could not be measured: %s. CANNOT "
               "DETERMINE is not a pass." % (len(unknown), ", ".join(unknown)))
    return {"verdict": worst, "why": why, "checks": checks,
            "connection": "connection:press-fit-sole-foot"}


if __name__ == "__main__":
    plug = {"name": "sole_skirt", "role": "skirt", "section_mm": [36.8, 49.8]}
    sock = {"name": "foot_socket", "role": "socket", "section_mm": [36.8, 49.8]}
    v = compatible(plug, sock)
    print("the reference pair ->", v["verdict"])
    for c in v["checks"]:
        print("   %-18s %-18s %s" % (c["check"], c["verdict"],
                                     json.dumps(c["measured"])[:78]))
    print()
    print("a 30x40 sole:", compatible(plug, dict(sock, section_mm=[30.0, 40.0]))["verdict"])
    print("sections 0.6 mm apart:",
          compatible(plug, dict(sock, section_mm=[37.4, 49.8]))["verdict"])
    print("with a real pull-off on the bench:",
          compatible(plug, dict(sock, pull_off_N=41.2, measured_gap_mm=-0.08))["verdict"])
    print("an as-built pair that came out LOOSE:",
          compatible(plug, dict(sock, measured_gap_mm=0.15))["verdict"])
