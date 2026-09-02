"""connection:press-fit-tube-15 -- will this Ø15 body actually stay in this arch?

Contract (TRIAD.md, ce-connections section):

    def compatible(a_iface, b_iface) -> dict
        {"verdict": "PASS" | "FAIL" | "CANNOT DETERMINE", "why": ..., "checks": [...]}

Shaped after ce-connections/press-fit-bearing-15x10x3, with ONE deliberate
difference that is the reason this folder exists at all: that folder grades
a FIT, because a 360 deg pocket can have one. This one cannot. The arch
measured here is Ø14.9938-14.9978 swept 149.06 deg and cut off flat at
z 9.5000, with 210.94 deg of open air below. An open arch has no
interference and no grip, so `compatible` grades what geometry can settle --
diameter, angular capture, band length against ring width, coaxiality --
and REFUSES the retention question by name instead of grading it 0.

Every number below is MEASURED and frozen in
evidence/tube-15-geometry.json (cecad.meshslice circle fits,
cecad.meshfeatures.cylinders and .intervals on Pollen's own meshes,
2026-09-02). Nothing here is recalled.

Run it:

    python3 compat.py

Python 3 stdlib only. Units: mm unless a name ends in _deg.
"""

import json

BORE_D_MM = 14.9938
BORE_D_MM_SPAN = (14.9938, 14.9978)
BORE_CENTRE_YZ = (0.0, 7.4995)
RING_D_MM = 15.0
RING_B_MM = 3.0
ARC_DEG = 149.06
OPEN_DEG = 210.94
BANDS_X_MM = ((-39.5, -37.5), (-36.5, -35.5))
BAND_LENS_MM = (2.0, 1.0)
JOURNAL_CENTRE_YZ = (0.0, 7.5)
COAX_TO_JOURNAL_MM = 0.0005
COAX_TO_MJCF_GEOM_MM = 0.2005

CRADLE_NAMES = ("lens_tube", "cradle", "arch", "tube")
RING_NAMES = ("od", "ring", "tube_od")

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
    """a_iface is the Ø15 body; b_iface is the arch cradle."""
    checks = []

    def add(name, verdict, measured, note=None):
        checks.append({"check": name, "verdict": verdict, "measured": measured,
                       "note": note})

    a_name = _field(a_iface, "name")
    b_name, b_role = _field(b_iface, "name"), _field(b_iface, "role")

    if a_name not in RING_NAMES:
        add("interface_names", "FAIL", {"a": a_name, "b": b_name},
            "a_iface must be the Ø15 body laid in the cradle, named one of %s. "
            "The bearing's BORE side belongs to "
            "connection:press-fit-bearing-15x10x3."
            % ", ".join(repr(n) for n in RING_NAMES))
        return _finish(checks)
    if b_name not in CRADLE_NAMES and b_role not in ("cradle", "journal_cradle",
                                                     "lens_seat"):
        add("interface_names", "FAIL",
            {"a": a_name, "b": {"name": b_name, "role": b_role}},
            "b_iface must be the arch cradle: name one of %s, or role "
            "'cradle'/'journal_cradle'/'lens_seat'."
            % ", ".join(repr(n) for n in CRADLE_NAMES))
        return _finish(checks)
    add("interface_names", "PASS", {"a": a_name, "b": b_name, "b_role": b_role})

    # 1. diameter -------------------------------------------------------
    a_nom = _field(a_iface, "nominal_mm", "od_d_mm", "d_mm")
    b_nom = _field(b_iface, "nominal_mm", "bore_d_mm", "seat_d_mm")
    if a_nom is None or b_nom is None:
        add("diameter", "CANNOT DETERMINE", {"a": a_nom, "b": b_nom},
            "an interface that does not state its diameter cannot be fitted to "
            "anything. The slug is not a measurement.")
    elif abs(float(a_nom) - RING_D_MM) > 0.5:
        add("diameter", "FAIL", {"a": float(a_nom), "expected": RING_D_MM},
            "this folder cradles the Ø15 body only.")
    else:
        gap = float(b_nom) - float(a_nom)
        add("diameter", "PASS" if abs(gap) <= 0.10 else "FAIL",
            {"body_d_mm": float(a_nom), "cradle_d_mm": float(b_nom),
             "diametral_gap_mm": round(gap, 4),
             "cradle_measured_span_mm": list(BORE_D_MM_SPAN)},
            "the reference cradle reads Ø%.4f-%.4f across its clean stations "
            "against a Ø%.1f ring: -0.0062 to -0.0022 mm of NOMINAL "
            "interference. At that magnitude, on an FDM-printed 149.06 deg "
            "arch, it is a coincidence of modelling, not a press fit -- see "
            "the retention check."
            % (BORE_D_MM_SPAN[0], BORE_D_MM_SPAN[1], RING_D_MM))

    # 2. angular capture ------------------------------------------------
    arc = _field(b_iface, "arc_deg", "angular_capture_deg")
    arc = ARC_DEG if arc is None else float(arc)
    if arc >= 360.0 - 1e-9:
        add("angular_capture", "PASS", {"arc_deg": arc},
            "a full bore -- but then this is the wrong folder: use "
            "connection:press-fit-bearing-15x10x3, which grades an ISO 286 fit.")
    elif arc > 180.0:
        add("angular_capture", "PASS", {"arc_deg": arc, "open_deg": 360.0 - arc},
            "more than half the circle, so the arch closes over the body's "
            "centre and captures it radially in the closed directions.")
    else:
        add("angular_capture", "CANNOT DETERMINE",
            {"arc_deg": arc, "open_deg": round(360.0 - arc, 2),
             "chord_plane_z_mm": 9.5, "crown_z_mm": 15.0},
            "%.2f deg is LESS than a half-circle: the arch does not reach past "
            "the body's centre, so it locates the ring but captures nothing -- "
            "the ring lifts straight out through the open %.2f deg. Whether "
            "that is acceptable depends on what closes the cradle in the real "
            "product, and NOTHING in any of Pollen's four MJCF files does. "
            "Measure a real unit, or find the retaining part."
            % (arc, 360.0 - arc))

    # 3. band length against ring width ---------------------------------
    bands = _field(b_iface, "bands_x_mm")
    lens = ([abs(b[1] - b[0]) for b in bands] if bands else list(BAND_LENS_MM))
    total = sum(lens)
    add("band_length", "PASS" if total + 1e-9 >= RING_B_MM else "CANNOT DETERMINE",
        {"band_lengths_mm": [round(x, 4) for x in lens],
         "total_mm": round(total, 4), "ring_width_mm": RING_B_MM,
         "contact_with_mjcf_placement_mm": 2.0},
        "the two bands total %.4f mm against a %.1f mm ring -- but only the "
        "FIRST band touches the ring where Pollen's MJCF puts it "
        "(x -40.0000..-37.0000): 2.0000 mm, 66.7%% of the ring width. The "
        "second band clears the ring by 0.5000 mm. Which axial datum is "
        "intended is not stated anywhere in the reference."
        % (total, RING_B_MM))

    # 4. coaxiality with the journal the ring runs on --------------------
    add("coaxiality", "PASS",
        {"cradle_centre_yz_mm": list(BORE_CENTRE_YZ),
         "journal_centre_yz_mm": list(JOURNAL_CENTRE_YZ),
         "offset_mm": COAX_TO_JOURNAL_MM,
         "mjcf_bearing_geom_offset_mm": COAX_TO_MJCF_GEOM_MM},
        "the cradle and the jaw's Ø10.0000 journal are coaxial to %.4f mm -- "
        "the two PARTS agree. Recorded and not averaged away: Pollen's MJCF "
        "places the bearing GEOM %.4f mm above both axes and 0.3000 mm "
        "outboard of the journal's Ø11.9949 flange. That is the visual model's "
        "placement, not the parts'."
        % (COAX_TO_JOURNAL_MM, COAX_TO_MJCF_GEOM_MM))

    # 5. retention -- structurally open, said once and named -------------
    closer = _field(b_iface, "closed_by")
    if closer:
        add("retention", "CANNOT DETERMINE", {"closed_by": closer},
            "the cradle names a closing part, but no pull-out or drop-out "
            "force has been measured for it. State a bench result.")
    else:
        add("retention", "CANNOT DETERMINE",
            {"open_deg": OPEN_DEG, "closed_by": None, "retention_N": None},
            "NOTHING closes the open %.2f deg. Searched: all four of Pollen's "
            "MJCF files (robot_allcollisions, robot_walk, "
            "robot_allcollisions_rollers in both reference copies) -- no geom "
            "is placed below this cradle. So the holding force here is not a "
            "number waiting to be measured on a bench; it is zero unless a "
            "part nobody has published closes it. What settles it: a photo or "
            "teardown of a real Microduck head with the motor support in "
            "place, or Pollen publishing the head assembly." % OPEN_DEG)

    # 6. the CLAIM on the host interface --------------------------------
    # Keyed on the claim, not the label. `lens_tube` is a legacy NAME that the
    # part folder now explains in place (name_is_legacy); a name is not a
    # measurement and failing a folder for a label would be theatre. A live
    # claim -- role 'lens_seat', or a `what`/`claims` string still asserting a
    # lens -- is a different thing, and it FAILS against the measurement.
    claim = " ".join(str(_field(b_iface, k) or "") for k in ("claims", "what", "role"))
    if (b_role == "lens_seat") or ("lens" in claim.lower() and "not" not in claim.lower()):
        add("claims_a_lens_seat", "FAIL",
            {"host_interface": b_name, "host_role": b_role,
             "m12_lens_holder_y_mm": [-52.38, -37.58],
             "lens_y_mm": [-63.8, -44.88],
             "lens_barrel_d_mm": [11.6, 13.6, 16.94]},
            "MEASURED REFUTATION of a LIVE claim (the interface asserts a lens "
            "seat in its role or its own words): in the "
            "motor_support mesh frame the m12 lens holder occupies "
            "y -52.38..-37.58 and the lens y -63.8..-44.88, on a y-axis 37-64 "
            "mm from this feature, and neither carries any Ø15 surface. What "
            "IS on this axis is the 15x10x3 bearing (0.181 mm off-axis in "
            "world coordinates) and through it the jaw's Ø10.0000 journal "
            "(0.0005 mm). The interface name is a leftover; the geometry is "
            "the jaw pivot. Fix the claim in the part folder -- do not fix it "
            "by deleting this check.")
    elif b_name == "lens_tube":
        add("claims_a_lens_seat", "PASS",
            {"host_interface": b_name, "host_role": b_role,
             "name_is_legacy": True},
            "the interface still carries the legacy NAME 'lens_tube' (kept so "
            "that microduck-motor-support cad/part.py's connector of the same "
            "name does not dangle), but it no longer CLAIMS a lens: its role "
            "is %r and its own text states the measurement. A name is not a "
            "measurement; a claim is." % (b_role,))

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
            "connection": "connection:press-fit-tube-15"}


if __name__ == "__main__":
    ring = {"name": "od", "nominal_mm": 15.0}
    cradle_claimed = {"name": "lens_tube", "role": "lens_seat",
                      "nominal_mm": 14.9938, "arc_deg": 149.06,
                      "bands_x_mm": [[-39.5, -37.5], [-36.5, -35.5]]}
    cradle_honest = dict(cradle_claimed, role="journal_cradle",
                         what="Ø14.9938 arch swept 149.06 deg, the jaw journal cradle")
    for label, b in (("the claim this folder refuted", cradle_claimed),
                     ("the corrected row, legacy name kept", cradle_honest)):
        v = compatible(ring, b)
        print("== %s -> %s" % (label, v["verdict"]))
        for c in v["checks"]:
            print("   %-20s %-18s %s" % (c["check"], c["verdict"],
                                         json.dumps(c["measured"])[:76]))
    print("a Ø22 body:", compatible({"name": "od", "nominal_mm": 22.0},
                                    cradle_honest)["verdict"])
    print("a full 360 bore here:",
          [c["note"][:60] for c in compatible(ring, dict(cradle_honest, arc_deg=360.0,
                                                         nominal_mm=15.0))["checks"]
           if c["check"] == "angular_capture"])
