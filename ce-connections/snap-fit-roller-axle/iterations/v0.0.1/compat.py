"""connection:snap-fit-roller-axle -- will this plate actually snap in, and stay?

Contract (TRIAD.md, ce-connections section):

    def compatible(a_iface, b_iface) -> dict
        {"verdict": "PASS" | "FAIL" | "CANNOT DETERMINE", "why": ..., "checks": [...]}

Shaped after ce-connections/press-fit-bearing-15x10x3. No ISO 286 module:
this is a cantilever snap between two printed parts, and the fit that
matters is a DEFLECTION, not a diameter band.

Cantilever snap-fit design has published guidance (the BASF and Bayer
snap-fit handbooks: permissible strain per material, the beam formula for
mating force). This module does NOT apply it, and the reason is measured
rather than stylistic: the formula needs the printed PLA's modulus and
permissible strain AT THIS LAYER ORIENTATION, and neither is in any file in
this repo. A handbook formula fed a guessed modulus produces a number with
a citation and no source, which is worse than an honest absence. So
`snap_force` is refused by name.

Every number is MEASURED and frozen in evidence/roller-slot-fit.json.

    python3 compat.py

Python 3 stdlib only. Units: mm unless a name ends in _deg or _N.
"""

import json

FINGER_RUN_MM = 10.0
FINGER_X_MM = (45.0, 55.0)
LEAD_IN_GAP_MM = 36.089
LEAD_IN_HALF_ANGLE_DEG = 33.47
BARB_LAND_GAP_MM = 34.7
BARB_LAND_HEIGHT_MM = 0.6
BARB_PROUD_PER_SIDE_MM = 1.0
POCKET_GAP_MM = 36.7
PLATE_WIDTH_MM = 36.5
CLEARANCE_PER_SIDE_MM = 0.1
DEFLECTION_PER_FINGER_MM = 0.9

FINGER_NAMES = ("roller_slot", "snap_fingers", "fingers")
PLATE_NAMES = ("foot_snap_plate", "snap_plate", "plate")

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
    """a_iface is the foot's finger pair; b_iface is the ankle's plate."""
    checks = []

    def add(name, verdict, measured, note=None):
        checks.append({"check": name, "verdict": verdict, "measured": measured,
                       "note": note})

    a_name, a_role = _field(a_iface, "name"), _field(a_iface, "role")
    b_name, b_role = _field(b_iface, "name"), _field(b_iface, "role")
    if a_name not in FINGER_NAMES and a_role != "snap":
        add("interface_names", "FAIL", {"a": {"name": a_name, "role": a_role}},
            "a_iface must be the foot's finger pair: name one of %s or role "
            "'snap'." % ", ".join(repr(n) for n in FINGER_NAMES))
        return _finish(checks)
    if b_name not in PLATE_NAMES and b_role != "snap_plate":
        add("interface_names", "FAIL", {"b": {"name": b_name, "role": b_role}},
            "b_iface must be the ankle's plate: name one of %s or role "
            "'snap_plate'." % ", ".join(repr(n) for n in PLATE_NAMES))
        return _finish(checks)
    add("interface_names", "PASS", {"a": a_name, "b": b_name})

    pocket = float(_field(a_iface, "pocket_gap_mm") or POCKET_GAP_MM)
    land = float(_field(a_iface, "barb_land_gap_mm") or BARB_LAND_GAP_MM)
    plate = _field(b_iface, "width_mm", "plate_width_mm")

    # 1. is anything captured at all? -------------------------------------
    if plate is None:
        add("capture", "CANNOT DETERMINE", {"plate_width_mm": None},
            "the plate does not state its width, so whether it is captured, "
            "clears the barbs, or will not enter at all is undecidable.")
        plate_f = None
    else:
        plate_f = float(plate)
        if plate_f > pocket:
            add("capture", "FAIL",
                {"plate_width_mm": plate_f, "pocket_gap_mm": pocket,
                 "interference_mm": round(plate_f - pocket, 4)},
                "the plate does not fit the pocket even once past the barbs. "
                "Nothing here is designed to be pressed.")
        elif plate_f <= land:
            add("capture", "FAIL",
                {"plate_width_mm": plate_f, "barb_land_gap_mm": land},
                "the plate passes straight through the barb land: NOTHING IS "
                "CAPTURED and the snap is a clearance hole. (The ankle is "
                "33.7000 mm wide above its shoulder, which is exactly why that "
                "part of it clears -- the capture happens on the 36.5000 mm "
                "part below.)")
        else:
            add("capture", "PASS",
                {"plate_width_mm": plate_f, "barb_land_gap_mm": land,
                 "pocket_gap_mm": pocket,
                 "overhang_per_side_mm": round((plate_f - land) / 2.0, 4),
                 "clearance_per_side_mm": round((pocket - plate_f) / 2.0, 4)})

    # 2. the deflection ----------------------------------------------------
    if plate_f is None:
        add("deflection", "CANNOT DETERMINE", None, "no plate width stated.")
    else:
        defl = (plate_f - land) / 2.0
        add("deflection", "PASS" if 0.0 < defl <= 1.5 else "CANNOT DETERMINE",
            {"deflection_per_finger_mm": round(defl, 4),
             "finger_run_mm": FINGER_RUN_MM,
             "lead_in_half_angle_deg": LEAD_IN_HALF_ANGLE_DEG},
            "each finger bends %.4f mm outward to let the plate pass, guided "
            "by a %.2f deg lead-in over a %.1f mm run. This grades the "
            "GEOMETRY of the snap -- whether the material survives that strain "
            "is the refused check below." % (defl, LEAD_IN_HALF_ANGLE_DEG,
                                             FINGER_RUN_MM))

    # 3. the barb ----------------------------------------------------------
    proud = float(_field(a_iface, "barb_proud_per_side_mm") or BARB_PROUD_PER_SIDE_MM)
    height = float(_field(a_iface, "barb_land_height_mm") or BARB_LAND_HEIGHT_MM)
    add("barb", "PASS" if proud > 0.2 else "CANNOT DETERMINE",
        {"proud_per_side_mm": proud, "land_height_mm": height},
        "%.4f mm proud over a %.4f mm land. Below about 0.2 mm a printed barb "
        "is inside the layer noise and stops being a feature."
        % (proud, height))

    # 4. what does it actually capture? ------------------------------------
    claim = " ".join(str(_field(a_iface, k) or "") for k in ("claims", "what"))
    low = claim.lower()
    if ("roller" in low or "wheel" in low) and "not" not in low:
        add("captures_what", "FAIL",
            {"claim": claim[:140]},
            "the row claims this slot takes a clip-on ROLLER. MEASURED against "
            "it: roller_blade, tire and rim appear in exactly ONE of Pollen's "
            "four MJCF files (robot_allcollisions_rollers.xml, both reference "
            "copies), and that file contains NO foot_left/foot_right/sole_left/"
            "sole_right geom at all -- the roller variant replaces the whole "
            "foot assembly and swaps the ankle for ankle_l_v1/ankle_r_v1, "
            "whose vertical Ø2.2/Ø3.5 at (50.1090, -5.5000) matches "
            "roller_blade's own Ø1.6 pilot at (50.1090, -5.5000, -18.8240) "
            "while ankle_left's is at (50.0000, 4.5020). What this snap "
            "captures is the ANKLE's 36.5000 mm plate at 0.1000 mm per side. "
            "Fix the claim -- do not fix it by deleting this check.")
    else:
        add("captures_what", "PASS",
            {"captures": "part:microduck-ankle-left/-right 36.5000 mm plate",
             "clearance_per_side_mm": CLEARANCE_PER_SIDE_MM},
            "the row does not claim a roller. The slug still says one; it is "
            "kept because both foot parts already `accept` it and renaming "
            "would dangle.")

    # 5. the force ----------------------------------------------------------
    for key, label in (("insertion_N", "insertion"), ("retention_N", "retention")):
        v = _field(a_iface, key) or _field(b_iface, key)
        if v is not None:
            add(label + "_force", "PASS", {key: float(v)},
                "a measured force was supplied.")
        else:
            add(label + "_force", "CANNOT DETERMINE",
                {key: None, "deflection_per_finger_mm": DEFLECTION_PER_FINGER_MM},
                "MISSING and it will not be computed: the beam formula needs "
                "the printed PLA's modulus and permissible strain at this "
                "layer orientation, and neither is in any file in this repo. A "
                "handbook formula fed a guessed modulus is a number with a "
                "citation and no source. What settles it: push a printed pair "
                "home on a gauge and record the peak, then pull it off and "
                "record that -- state insertion_N and retention_N.")

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
            "connection": "connection:snap-fit-roller-axle"}


if __name__ == "__main__":
    fingers = {"name": "roller_slot", "role": "snap", "pocket_gap_mm": 36.7,
               "barb_land_gap_mm": 34.7, "barb_proud_per_side_mm": 1.0,
               "barb_land_height_mm": 0.6,
               "what": "two barbed cantilevers over the ankle's 36.5000 mm plate"}
    plate = {"name": "foot_snap_plate", "role": "snap_plate", "width_mm": 36.5}
    v = compatible(fingers, plate)
    print("the reference pair ->", v["verdict"])
    for c in v["checks"]:
        print("   %-18s %-18s %s" % (c["check"], c["verdict"],
                                     json.dumps(c["measured"])[:74]))
    print()
    print("the roller claim:", compatible(
        dict(fingers, what="the clip-on roller drops between them"), plate)["verdict"])
    print("a plate that clears the barbs:",
          compatible(fingers, dict(plate, width_mm=33.7))["verdict"])
    print("a plate wider than the pocket:",
          compatible(fingers, dict(plate, width_mm=38.0))["verdict"])
    print("a barb inside the layer noise:",
          [c["verdict"] for c in compatible(dict(fingers, barb_proud_per_side_mm=0.1),
                                            plate)["checks"] if c["check"] == "barb"])
    print("with both forces measured:", compatible(
        dict(fingers, insertion_N=18.4, retention_N=26.1), plate)["verdict"])
