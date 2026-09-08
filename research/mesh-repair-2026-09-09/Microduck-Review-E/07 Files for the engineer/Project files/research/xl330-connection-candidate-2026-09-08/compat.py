"""Candidate: nominal geometry with unresolved required tapping hardware."""
import math

DISC_D_MM = 16.0        # meshfeatures bosses on xl330.stl: Ø16.0 x 3.0
DISC_L_MM = 3.0
PCD_MM = 12.0           # 4 nominal pilot holes on Ø12.0 (r 6.0 at (0,±6),(±6,0))
TAP_D_MM = 1.6          # nominal pilot only; no thread inference
TAP_DEPTH_MM = 3.0      # manufacturer maximum; minimum unknown
SCREWS = 4

A_NAMES = ("horn", "idler", "horn_face", "servo_horn")
B_ROLES = ("horn_face",)
B_NAMES = ("horn_face", "horn_recess")

WORST = {"PASS": 0, "CANNOT DETERMINE": 1, "FAIL": 2}


def _field(iface, key, *aliases):
    """One value off an interface record, flat first then under `measured`."""
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


def _is_a(iface):
    return _field(iface, "name") in A_NAMES or _field(iface, "role") in ("servo_horn",)


def _is_b(iface):
    return (_field(iface, "role") in B_ROLES or _field(iface, "name") in B_NAMES)


def compatible(a_iface, b_iface):
    checks = []

    def add(name, verdict, measured, note=None):
        checks.append({"check": name, "verdict": verdict, "measured": measured,
                       "note": note})

    a_name = _field(a_iface, "name")
    b_name, b_role = _field(b_iface, "name"), _field(b_iface, "role")

    # 1. the sides
    if not _is_a(a_iface) or not _is_b(b_iface):
        return {"verdict": "FAIL",
                "checks": [{"check": "interface_names", "verdict": "FAIL",
                            "measured": {"a": a_name, "b": {"name": b_name,
                                                            "role": b_role}},
                            "note": ("a must be the SERVO's horn/idler face "
                                     "(name one of %s) and b the driven bracket "
                                     "face (role 'horn_face' or name one of %s). "
                                     "A rename is a measurement the importer "
                                     "makes, not one this folder invents."
                                     % (" / ".join(A_NAMES),
                                        " / ".join(B_NAMES)))}],
                "why": "the pair is not this connection's pair.",
                "connection": "connection:spline-xl330-horn"}
    add("interface_names", "PASS", {"a": a_name, "b": b_name, "b_role": b_role})

    # 2. the bolt circle -- the joint's NAME in numbers
    a_pcd = _field(a_iface, "pcd_mm", "bolt_circle_mm")
    b_pcd = _field(b_iface, "pcd_mm", "bolt_circle_mm")
    # a square spacing is the same circle spelled differently: side * sqrt(2)
    if b_pcd is None:
        sq = _field(b_iface, "screw_square_mm")
        if sq is not None:
            b_pcd = float(sq) * 2.0 ** 0.5
    if a_pcd is None or b_pcd is None:
        add("bolt_circle", "CANNOT DETERMINE", {"a_pcd_mm": a_pcd, "b_pcd_mm": b_pcd},
            "both sides must state their bolt circle (pcd_mm, or the bracket's "
            "screw_square_mm -- side x sqrt(2) is the same measurement). This "
            "folder's reference is Ø%.1f, measured on xl330.stl, and it is NOT "
            "substituted for a missing value." % PCD_MM)
    elif abs(float(a_pcd) - float(b_pcd)) > 0.5:
        add("bolt_circle", "FAIL",
            {"a_pcd_mm": float(a_pcd), "b_pcd_mm": float(b_pcd),
             "delta_mm": abs(float(a_pcd) - float(b_pcd))},
            "the two patterns differ by more than the 0.5 mm feature-match "
            "tolerance this repo's refcheck uses -- the screws do not line up")
    else:
        add("bolt_circle", "PASS",
            {"a_pcd_mm": float(a_pcd), "b_pcd_mm": float(b_pcd),
             "reference_mm": PCD_MM},
            "phase is NOT checked: the pattern is 4-fold symmetric and the horn "
            "rotates with the output, so phase is an assembly choice "
            "(mate() params['index'])")

    # 3. screw count
    na = _field(a_iface, "screws", "screw_count")
    nb = _field(b_iface, "screws", "screw_count")
    if na is None or nb is None:
        add("screw_count", "CANNOT DETERMINE", {"a": na, "b": nb},
            "state `screws` on both sides; the measured pattern is 4 on both "
            "faces of xl330.stl")
    elif int(na) != SCREWS or int(nb) != SCREWS:
        add("screw_count", "FAIL", {"a": int(na), "b": int(nb)},
            "the XL330 horn face carries exactly 4 pilot holes in the reference pattern; a "
            "different count is a different joint")
    else:
        add("screw_count", "PASS", {"screws": SCREWS})

    # Pilot geometry never identifies thread pitch/profile or compatible screw.
    a_tap = _field(a_iface, "pilot_d_mm", "tap_d_mm", "hole_d_mm")
    add("pilot_diameter", "CANNOT DETERMINE" if a_tap is None else
        ("PASS" if abs(float(a_tap)-1.6)<1e-6 else "FAIL"),
        {"pilot_d_mm": a_tap, "drawing_nominal_mm": 1.6},
        "Nominal geometry only; no production tolerance or screw compatibility inferred.")
    depths = {k: _field(a_iface,k) for k in
              ("maximum_pilot_depth_mm", "tap_depth_mm", "pilot_depth_mm")}
    depths = {k:v for k,v in depths.items() if v is not None}
    try:
        bad_depth = any(not math.isfinite(float(v)) or float(v)>3.0 or float(v)<=0
                        for v in depths.values())
    except (TypeError, ValueError):
        bad_depth = True
    add("manufacturer_depth_limit", "FAIL" if bad_depth else
        ("PASS" if depths else "CANNOT DETERMINE"),
        {"stated_mm": depths, "maximum_mm": 3.0},
        "Manufacturer drawing maximum 3 mm; no conflicting depth field can override that. Not minimum-engagement or seating approval.")
    add("tapping_hardware_identity", "CANNOT DETERMINE", {"quantity": 4,
        "manufacturer_callout": "M2 Tapping Screw", "part_ref": None,
        "minimum_engagement_mm": None},
        "Exact screw profile/pitch/head/length and seating unknown. Four required screws remain unresolved; ISO4762 cannot be approved from pilot diameter.")
    b_clear = _field(b_iface, "clearance_d_mm", "hole_d_mm", "screw_d_mm")
    if b_clear is None:
        add("bracket_clearance", "CANNOT DETERMINE", None,
            "the bracket states no clearance diameter; the consumers measured "
            "so far carry Ø2.2-2.4 (ISO 273 close/normal for M2)")
    elif float(b_clear) < 2.0:
        add("bracket_clearance", "FAIL", {"clearance_d_mm": float(b_clear)},
            "smaller than the 2.0 mm major diameter: the screw does not pass")
    else:
        add("bracket_clearance", "PASS",
            {"clearance_d_mm": float(b_clear),
             "iso273_m2_mm": [2.2, 2.4, 2.6]},
            "at or above the major; the ISO 273 M2 clearance row is quoted for "
            "comparison, not enforced -- a snug 2.05 printed hole is a "
            "measurement, not a defect")

    # 5. the centre pilot -- structurally CANNOT DETERMINE on the horn side
    b_centre = _field(b_iface, "centre_d_mm", "bore_d_mm")
    add("centre_pilot", "CANNOT DETERMINE",
        {"horn_hub_d_mm": None, "bracket_centre_d_mm": b_centre},
        "every measured bracket carries a Ø5-6 centre bore/recess, but Pollen's "
        "xl330.stl has NO centre hub (axis probe solid -14.5..14.5, "
        "cecad.meshslice 2026-09-02) -- the decimated mesh hid it. Whether the "
        "real horn hub pilots in the bracket's bore is unmeasurable from this "
        "reference; a vendor drawing of the XL330 horn would settle it.")

    # 6. strength
    add("strength", "CANNOT DETERMINE",
        {"clamp_torque_Nm": None, "strip_torque_Nm": None},
        "4 M2s into tapped plastic: no clamp or strip torque has been measured "
        "in this workshop (connection:threaded-m2 records the same absence for "
        "one screw). The XL330-M288-T stalls at 0.52 N.m (vendor figure via "
        "ce-parts/xl330-m288-t) -- that is the LOAD, quoted so a bench test "
        "knows what to beat; it is not evidence the joint holds it.")

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
            "connection": "connection:spline-xl330-horn"}


