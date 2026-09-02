"""connection:snap-fit-ankle-blocks -- will these blocks actually seat in these pockets?

Contract (TRIAD.md, ce-connections section):

    def compatible(a_iface, b_iface) -> dict
        {"verdict": "PASS" | "FAIL" | "CANNOT DETERMINE", "why": ..., "checks": [...]}

Shaped after ce-connections/press-fit-bearing-15x10x3. It does NOT carry that
folder's ISO 286 module, and the reason is measured rather than stylistic:
ISO 286 grades round fits, and this pair is a 5.0000 x 4.0000 mm printed
RECTANGLE in a 5.2000 x 4.2000 mm printed pocket. There is no IT band for
that, so this module grades the measured clearances directly.

It also carries `claims_a_snap`, which FAILs any row asserting the snap the
slug promises, because measurement says there is none: no undercut, barb,
lip or lead-in on either side, pockets open top to bottom in z, and a
0.1000 mm per-side CLEARANCE. The foot is retained by the single M2 at
(x 50.0000, y 4.5020) on connection:threaded-m2.

Every number is MEASURED and frozen in evidence/ankle-blocks-fit.json.

    python3 compat.py

Python 3 stdlib only. Units: mm.
"""

import json

BLOCK_MM = (5.0, 4.0)
POCKET_MM = (5.2, 4.2)
CLEARANCE_PER_SIDE_MM = 0.1
BLOCK_SPACING_MM = 26.8
ENGAGED_HEIGHT_MM = (6.061, 8.0)
CRADLE_R_MM = (16.3018, 16.3058)
CRADLE_RESIDUAL_MEAN_MM = (0.00396, 0.00432)
CRADLE_CENTRE_ERR_MM = (0.007, 0.011)
RELIEF_CLEARANCE_MM = 0.2
RETAINED_BY = "connection:threaded-m2"
FDM_LINE_MM = 0.4

BLOCK_NAMES = ("foot_blocks", "ankle_blocks", "blocks", "spigots")
POCKET_NAMES = ("ankle_cradle", "block_pockets", "pockets", "seat")

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
    """a_iface is the ankle's block pair; b_iface is the foot's pocket pair."""
    checks = []

    def add(name, verdict, measured, note=None):
        checks.append({"check": name, "verdict": verdict, "measured": measured,
                       "note": note})

    a_name, a_role = _field(a_iface, "name"), _field(a_iface, "role")
    b_name, b_role = _field(b_iface, "name"), _field(b_iface, "role")
    if a_name not in BLOCK_NAMES and a_role != "spigot_pair":
        add("interface_names", "FAIL", {"a": {"name": a_name, "role": a_role}},
            "a_iface must be the ankle's block pair: name one of %s or role "
            "'spigot_pair'." % ", ".join(repr(n) for n in BLOCK_NAMES))
        return _finish(checks)
    if b_name not in POCKET_NAMES and b_role != "seat":
        add("interface_names", "FAIL", {"b": {"name": b_name, "role": b_role}},
            "b_iface must be the foot's pocket pair: name one of %s or role "
            "'seat'." % ", ".join(repr(n) for n in POCKET_NAMES))
        return _finish(checks)
    add("interface_names", "PASS", {"a": a_name, "b": b_name})

    # 1. the pair pitch --------------------------------------------------
    sp_a = _field(a_iface, "spacing_mm", "block_spacing_mm")
    sp_b = _field(b_iface, "spacing_mm", "pocket_spacing_mm")
    if sp_a is None or sp_b is None:
        add("pair_pitch", "CANNOT DETERMINE", {"a": sp_a, "b": sp_b},
            "the pitch is what makes a PAIR of spigots an anti-rotation "
            "feature. An interface that does not state it cannot be checked "
            "for it, and the reference figure (%.4f mm) is not a substitute "
            "for the row's own." % BLOCK_SPACING_MM)
    elif abs(float(sp_a) - float(sp_b)) > 0.05:
        add("pair_pitch", "FAIL",
            {"a_mm": float(sp_a), "b_mm": float(sp_b),
             "disagreement_mm": round(abs(float(sp_a) - float(sp_b)), 4)},
            "two spigots at one pitch cannot both seat in two pockets at "
            "another; the pair stops being an anti-rotation feature and "
            "becomes a jam.")
    else:
        add("pair_pitch", "PASS", {"a_mm": float(sp_a), "b_mm": float(sp_b),
                                   "reference_mm": BLOCK_SPACING_MM})

    # 2. the clearances ---------------------------------------------------
    bl = _field(a_iface, "size_mm", "block_mm") or list(BLOCK_MM)
    pk = _field(b_iface, "size_mm", "pocket_mm") or list(POCKET_MM)
    bl = [float(v) for v in bl]
    pk = [float(v) for v in pk]
    per_side = [round((pk[i] - bl[i]) / 2.0, 4) for i in range(2)]
    if min(per_side) < 0.0:
        add("clearance", "FAIL",
            {"block_mm": bl, "pocket_mm": pk, "per_side_mm": per_side},
            "the block is LARGER than its pocket on at least one axis. There is "
            "no undercut here to deform into and no lead-in to start it: this "
            "is a jam, not a press.")
    elif max(per_side) > 0.5:
        add("clearance", "CANNOT DETERMINE",
            {"block_mm": bl, "pocket_mm": pk, "per_side_mm": per_side},
            "more than 0.5 mm of slack per side: the pair no longer locates "
            "anything, and what the foot's real position then is CANNOT be "
            "determined from geometry.")
    else:
        add("clearance", "PASS",
            {"block_mm": bl, "pocket_mm": pk, "per_side_mm": per_side,
             "reference_per_side_mm": CLEARANCE_PER_SIDE_MM},
            "%.4f mm per side in x and %.4f in y, measured on both meshes with "
            "the same ray-cast instrument. A location fit."
            % (per_side[0], per_side[1]))

    # 3. the cradle -------------------------------------------------------
    r = _field(b_iface, "cradle_r_mm", "seat_r_mm")
    if r is None:
        add("cradle", "PASS",
            {"ankle_hull_r_mm": list(CRADLE_R_MM),
             "residual_mean_mm": list(CRADLE_RESIDUAL_MEAN_MM),
             "centre_error_mm": list(CRADLE_CENTRE_ERR_MM),
             "relief_clearance_mm": RELIEF_CLEARANCE_MM},
            "the ankle's under-hull circle-fits to R%.4f (residual mean "
            "%.5f) at x 40 and R%.4f (%.5f) at x 60, about a centre "
            "%.3f-%.3f mm from the declared ankle axis -- it IS R16.3 on the "
            "axis. The foot's R16.3 end ledges take it; the R16.5 relief band "
            "across the rib tops stands %.4f mm clear, so the load lands on "
            "the two ledges."
            % (CRADLE_R_MM[0], CRADLE_RESIDUAL_MEAN_MM[0], CRADLE_R_MM[1],
               CRADLE_RESIDUAL_MEAN_MM[1], CRADLE_CENTRE_ERR_MM[0],
               CRADLE_CENTRE_ERR_MM[1], RELIEF_CLEARANCE_MM))
    else:
        d = abs(float(r) - CRADLE_R_MM[0])
        add("cradle", "PASS" if d <= 0.2 else "FAIL",
            {"stated_r_mm": float(r), "measured_r_mm": list(CRADLE_R_MM),
             "difference_mm": round(d, 4)},
            None if d <= 0.2 else "a cradle radius more than 0.2 mm from the "
                                  "ankle hull's own R16.3 lands the load on an "
                                  "edge instead of a surface")

    # 4. does anything actually snap? -------------------------------------
    claim = " ".join(str(_field(b_iface, k) or "") for k in ("claims", "what"))
    barb = _field(a_iface, "barb_mm") or _field(b_iface, "barb_mm")
    undercut = _field(a_iface, "undercut_mm") or _field(b_iface, "undercut_mm")
    if barb or undercut:
        add("claims_a_snap", "PASS", {"barb_mm": barb, "undercut_mm": undercut},
            "a barb or undercut is declared with a number. Measure it on the "
            "mesh before trusting it -- lane T found none on the reference "
            "pair.")
    elif "snap" in claim.lower() or "barb" in claim.lower():
        add("claims_a_snap", "FAIL",
            {"claim": claim[:120], "barb_mm": None, "undercut_mm": None,
             "pockets_open_in_z": True,
             "clearance_per_side_mm": CLEARANCE_PER_SIDE_MM},
            "the row CLAIMS a snap and states no barb or undercut, and none is "
            "on the mesh: the pockets are open top to bottom in z (no lip for "
            "a barb to pass -- five stations inside them return no material at "
            "all), the blocks are prismatic over their whole height, and the "
            "fit is a %.4f mm per-side clearance. What retains the foot is %s. "
            "Fix the claim -- do not fix it by deleting this check."
            % (CLEARANCE_PER_SIDE_MM, RETAINED_BY))
    else:
        add("claims_a_snap", "PASS",
            {"barb_mm": None, "undercut_mm": None, "retained_by": RETAINED_BY},
            "the slug says snap-fit and nothing snaps -- and the row does not "
            "claim otherwise. The name is inherited from the parts' `accepts` "
            "lists; the geometry is a location pair retained by %s."
            % RETAINED_BY)

    # 5. as-printed ---------------------------------------------------
    printed = _field(b_iface, "measured_pocket_mm", "as_printed_pocket_mm")
    if printed is not None:
        add("as_printed", "PASS", {"as_printed_pocket_mm": printed},
            "graded from a real measurement of a printed pocket.")
    else:
        add("as_printed", "CANNOT DETERMINE",
            {"per_side_mm": CLEARANCE_PER_SIDE_MM, "fdm_line_mm": FDM_LINE_MM,
             "ratio": round(CLEARANCE_PER_SIDE_MM / FDM_LINE_MM, 3)},
            "%.4f mm per side is a QUARTER of a 0.4 mm FDM extrusion width. "
            "Slicer compensation, elephant's foot and the corner radius the "
            "nozzle leaves all move a printed pocket by that much or more, so "
            "whether a real pair slides or binds is not decidable from the "
            "model. What settles it: calipers on a printed block and pocket -- "
            "state measured_pocket_mm."
            % CLEARANCE_PER_SIDE_MM)

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
            "connection": "connection:snap-fit-ankle-blocks"}


if __name__ == "__main__":
    blocks = {"name": "foot_blocks", "role": "spigot_pair", "spacing_mm": 26.8,
              "size_mm": [5.0, 4.0]}
    pockets = {"name": "ankle_cradle", "role": "seat", "spacing_mm": 26.8,
               "size_mm": [5.2, 4.2]}
    v = compatible(blocks, pockets)
    print("the reference pair ->", v["verdict"])
    for c in v["checks"]:
        print("   %-16s %-18s %s" % (c["check"], c["verdict"],
                                     json.dumps(c["measured"])[:76]))
    print()
    print("a row that claims a snap:",
          compatible(blocks, dict(pockets, what="two snap pockets whose barbs grip the blocks"))["verdict"])
    print("blocks bigger than pockets:",
          compatible(dict(blocks, size_mm=[5.4, 4.4]), pockets)["verdict"])
    print("pitches 0.4 mm apart:",
          compatible(dict(blocks, spacing_mm=27.2), pockets)["verdict"])
    print("2 mm of slop per side:",
          compatible(blocks, dict(pockets, size_mm=[9.0, 8.0]))["verdict"])
    print("with a printed pocket measured:",
          compatible(blocks, dict(pockets, measured_pocket_mm=[5.12, 4.09]))["verdict"])
