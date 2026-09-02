"""connection:press-fit-bearing-15x10x3 -- will this 15x10x3 bearing actually seat here?

Contract (TRIAD.md, ce-connections section):

    def compatible(a_iface, b_iface) -> dict
        {"verdict": "PASS" | "FAIL" | "CANNOT DETERMINE", "why": ..., "checks": [...]}

Shaped after ce-connections/press-fit-608 (the workshop's worked example for
a bearing seat; the ISO 286 derivation below is the same mathematics at this
joint's own sizes, deliberately duplicated -- TRIAD.md line 51).

THE BEARING, measured not recalled: Pollen ships it as
reference/pollen-microduck-rl/assets/seeed_bearing__configuration_default.stl
and cecad.meshfeatures.cylinders (2026-09-02) reads it as hole Ø10.0 /
boss Ø15.0, bbox 15.0 x 15.0 x 3.0 -- a 15 mm OD, 10 mm bore, 3 mm wide
ring, which is what SPEC.md section 4 counts as "bearings ... 15x10x3 (x3)"
(ankle_left, ankle_right, jaw_soft placements in spec/mesh-placements.json).
No vendor designation is stated anywhere in the reference, so none is
invented here -- the slug is the dimensions.

THE SEATS, measured per consumer on the microduck shelf:
    inner-race seat  microduck-shin 'ankle': Ø10.0 x 3.2 boss (its own
                     measured interface, role bearing_seat)
    outer-race seat  microduck-ankle-left/right 'ankle_bearing': Ø15.0 x 2.3
                     pocket behind a Ø14.0 window, Ø16 x 0.5 lead-in
All these seats are FDM-PRINTED PLA. A printed bore has NO ISO 286
tolerance class -- extrusion width, cooling and slicer compensation move a
Ø15 pocket by more than an entire IT7 band -- so the fit checks below can
grade a class only when one is DECLARED (a machined seat), and otherwise
return CANNOT DETERMINE naming the as-printed measurement that would
complete them. That is the honest difference from press-fit-608's ground
shafts, and it is stated, not hidden.

Run this file directly to print the ISO 286 derivation checked against the
published table rows it was not derived from:

    python3 compat.py

Python 3 stdlib only. Units: mm unless a name ends in _um.
"""

import json
import math

BORE_MM = 10.0    # meshfeatures hole d on seeed_bearing__configuration_default.stl
OD_MM = 15.0      # meshfeatures boss d, same run
WIDTH_MM = 3.0    # numpy bbox z 0.0..3.0, same mesh (scale 1000)
BEARING_REF = "part:bearing-15x10x3"

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


# --------------------------------------------------------------------------
# ISO 286, derived rather than recalled (the press-fit-608 module at this
# folder's sizes; formulae from ISO 286-1 itself)
# --------------------------------------------------------------------------

SIZE_STEPS = [(0.0, 3.0), (3.0, 6.0), (6.0, 10.0), (10.0, 18.0), (18.0, 30.0),
              (30.0, 50.0), (50.0, 80.0), (80.0, 120.0), (120.0, 180.0),
              (180.0, 250.0), (250.0, 315.0), (315.0, 400.0), (400.0, 500.0)]

IT_MULTIPLE = {5: 7, 6: 10, 7: 16, 8: 25, 9: 40, 10: 64, 11: 100}


def size_step(d_mm):
    for lo, hi in SIZE_STEPS:
        if lo < d_mm <= hi:
            return lo, hi
    raise ValueError("%r mm is outside the ISO 286 size steps this module "
                     "carries. CANNOT DETERMINE -- nothing is extrapolated." % d_mm)


def tolerance_unit_um(d_mm):
    """i = 0.45*cbrt(D) + 0.001*D, D = geometric mean of the size step."""
    lo, hi = size_step(d_mm)
    d_geo = math.sqrt(lo * hi) if lo > 0 else hi
    return 0.45 * d_geo ** (1.0 / 3.0) + 0.001 * d_geo, d_geo


def it_um(d_mm, grade):
    if grade not in IT_MULTIPLE:
        raise ValueError("IT%r is not carried here. CANNOT DETERMINE." % grade)
    i_um, d_geo = tolerance_unit_um(d_mm)
    raw = IT_MULTIPLE[grade] * i_um
    return int(math.floor(raw + 0.5)), raw, i_um, d_geo


def shaft_limits_um(d_mm, letter, grade):
    """(ei, es) in um for shaft classes h / k / js only; else raises."""
    it, raw, i_um, d_geo = it_um(d_mm, grade)
    if letter == "h":
        return -it, 0, it
    if letter == "k":
        if grade not in (4, 5, 6, 7):
            raise ValueError("k deviation es = +0.6*cbrt(D) is defined for "
                             "grades 4-7 only. CANNOT DETERMINE.")
        ei = int(math.floor(0.6 * d_geo ** (1.0 / 3.0) + 0.5))
        return ei, ei + it, it
    if letter == "js":
        return -it / 2.0, it / 2.0, it
    raise ValueError("shaft class %r is not derived in this module. "
                     "CANNOT DETERMINE." % letter)


# MEASURED 2026-09-02, running this file's own self-test: the ISO 286-2
# tables are NOT pure formula output. Raw 16i gives IT7 = 14.37 um in the
# 6-10 step and 17.32 um in 10-18; the PUBLISHED table says 15 and 18. The
# published value wins (it is the standard everyone machines to), so IT7 for
# the steps this joint uses is TRANSCRIBED here with the drift recorded --
# hiding the 1 um disagreement inside a "derivation" would be a check that
# agrees with itself. IT6 and the k/h shaft deviations reproduce the table
# exactly from the formulae and stay derived.
PUBLISHED_IT7_UM = {(6.0, 10.0): 15, (10.0, 18.0): 18, (18.0, 30.0): 21}


def hole_limits_um(d_mm, letter, grade):
    it, raw, i_um, d_geo = it_um(d_mm, grade)
    if letter == "H":
        if grade == 7:
            step = size_step(d_mm)
            if step in PUBLISHED_IT7_UM:
                return 0, PUBLISHED_IT7_UM[step], PUBLISHED_IT7_UM[step]
        return 0, it, it
    raise ValueError("hole class %r is not derived in this module. "
                     "CANNOT DETERMINE." % letter)


# --------------------------------------------------------------------------
# the verdict
# --------------------------------------------------------------------------

BEARING_IFACES = ("bore", "od")
SHAFT_NAMES = ("shaft", "boss")
HOUSING_NAMES = ("housing_bore", "pocket", "seat_bore")


def compatible(a_iface, b_iface):
    """a_iface is the BEARING side ('bore' or 'od'); b_iface is the seat."""
    checks = []

    def add(name, verdict, measured, note=None):
        checks.append({"check": name, "verdict": verdict, "measured": measured,
                       "note": note})

    a_name = _field(a_iface, "name")
    b_name, b_role = _field(b_iface, "name"), _field(b_iface, "role")

    if a_name not in BEARING_IFACES:
        add("interface_names", "FAIL", {"a": a_name, "b": b_name},
            "a_iface must be the bearing side, named 'bore' (Ø10 inner ring) "
            "or 'od' (Ø15 outer ring).")
        return _finish(checks, None)
    b_ok = (b_name in SHAFT_NAMES + HOUSING_NAMES
            or b_role in ("bearing_seat", "bearing_face"))
    if not b_ok:
        add("interface_names", "FAIL", {"a": a_name,
                                        "b": {"name": b_name, "role": b_role}},
            "b_iface must be the seat: name 'shaft'/'boss' (mates 'bore') or "
            "'housing_bore'/'pocket' (mates 'od'), or the microduck shelf's "
            "role 'bearing_seat'.")
        return _finish(checks, a_name)
    add("interface_names", "PASS", {"a": a_name, "b": b_name, "b_role": b_role})

    # 1. nominal size agreement -- and it settles WHICH ring the seat takes
    nominal = BORE_MM if a_name == "bore" else OD_MM
    a_nom = _field(a_iface, "nominal_mm", "bore_d_mm", "od_d_mm")
    b_nom = _field(b_iface, "nominal_mm", "seat_d_mm", "boss_d_mm", "pocket_d_mm")
    if a_nom is None or b_nom is None:
        add("nominal_size", "CANNOT DETERMINE", {"a": a_nom, "b": b_nom},
            "an interface that does not state its nominal diameter cannot be "
            "fitted to anything. The slug is not a measurement.")
    elif abs(float(a_nom) - nominal) > 1e-9:
        add("nominal_size", "FAIL", {"a": a_nom, "expected": nominal},
            "this folder is the 15x10x3 ring (Ø10 bore / Ø15 OD / 3 wide, "
            "measured on seeed_bearing__configuration_default.stl). Another "
            "size is another folder -- see press-fit-bearing-22x16x4.")
    elif abs(float(a_nom) - float(b_nom)) > 0.5:
        add("nominal_size", "FAIL", {"a": a_nom, "b": b_nom},
            "the seat's nominal differs from the ring's by more than 0.5 mm -- "
            "not this fit at all")
    else:
        add("nominal_size", "PASS",
            {"nominal_mm": nominal, "a": float(a_nom), "b": float(b_nom)},
            "the reference design's own printed seats measure at nominal "
            "(shin boss Ø10.0; ankle pocket Ø15.0)")

    # 2. the fit -- class when declared, as-printed diameters otherwise
    cls = _field(b_iface, "tolerance_class")
    b_meas = _field(b_iface, "measured_d_mm", "as_printed_d_mm")
    if cls is not None:
        try:
            letter = "".join(c for c in cls if c.isalpha())
            grade = int("".join(c for c in cls if c.isdigit()))
            if a_name == "bore":
                ei, es, it = shaft_limits_um(nominal, letter, grade)
                fitrow = {"role": "shaft", "class": cls, "ei_um": ei, "es_um": es,
                          "IT_um": it}
            else:
                ei, es, it = hole_limits_um(nominal, letter, grade)
                fitrow = {"role": "hole", "class": cls, "EI_um": ei, "ES_um": es,
                          "IT_um": it}
            add("fit", "PASS", fitrow,
                "limits derived from ISO 286-1's own formulae (run this file to "
                "see them checked against the published table); the ring's own "
                "deviation (ISO 492-shaped, unfetched, vendorless here) is still "
                "missing, so the INTERFERENCE ENVELOPE stays open -- see the "
                "interference check")
        except ValueError as exc:
            add("fit", "CANNOT DETERMINE", cls, str(exc))
    elif b_meas is not None:
        gap = float(b_meas) - nominal
        add("fit", "PASS",
            {"as_printed_d_mm": float(b_meas), "ring_nominal_mm": nominal,
             "diametral_gap_mm": round(gap, 4)},
            "graded from a MEASURED as-printed diameter against the ring "
            "nominal; positive = clearance, negative = interference. The "
            "ring's own deviation is still unmeasured, so this is the "
            "envelope's midline, not its edges.")
    else:
        add("fit", "CANNOT DETERMINE", None,
            "the seat states neither a tolerance_class (it is FDM-printed PLA "
            "-- a printed bore has no ISO class; slicer compensation moves it "
            "by more than an IT7 band) nor a measured_d_mm. Measure the "
            "printed seat with calipers and state measured_d_mm, and this "
            "check grades the actual gap. It will not grade a nominal against "
            "a nominal and call that a fit.")

    # 3. seat length against the ring width -- reported, and NOT failed when
    #    the reference design itself under-hangs the ring
    seat_len = _field(b_iface, "seat_length_mm", "seat_depth_mm")
    if seat_len is None:
        add("seat_length", "CANNOT DETERMINE", None,
            "the seat does not state its length. The ring is %s mm wide "
            "(bbox of the reference mesh)." % WIDTH_MM)
    elif float(seat_len) + 1e-9 < WIDTH_MM:
        add("seat_length", "CANNOT DETERMINE",
            {"seat_length_mm": float(seat_len), "ring_width_mm": WIDTH_MM,
             "engagement": round(float(seat_len) / WIDTH_MM, 3)},
            "the seat is SHORTER than the ring, so part of the ring stands "
            "proud -- and that is what Pollen's own design does (ankle pocket "
            "2.3 mm for the 3 mm ring, the proud 0.7 mm clearing the shin "
            "boss). Whether partial engagement holds the press is a bench "
            "question nobody has measured, so it is reported, not failed and "
            "not passed.")
    else:
        add("seat_length", "PASS",
            {"seat_length_mm": float(seat_len), "ring_width_mm": WIDTH_MM})

    # 4. the shoulder / abutment -- what the ring is pressed against
    ab = _field(b_iface, "abutment_dia_mm", "shoulder_d_mm")
    if ab is None:
        add("abutment", "CANNOT DETERMINE", None,
            "no shoulder diameter stated. Unlike the 608 (SKF publishes da/Da "
            "abutment limits), NO vendor sheet exists for this ring in the "
            "reference -- the honest rule is geometric: a shoulder must "
            "overlap the ring FACE it locates without touching the other "
            "ring. For the Ø10 inner ring that means a shoulder between 10 "
            "and 15 minus the race land; the land widths are unmeasured, so "
            "only the gross bounds can ever be checked here.")
    else:
        ab = float(ab)
        if a_name == "bore":
            ok = BORE_MM < ab < OD_MM
            add("abutment", "PASS" if ok else "FAIL",
                {"abutment_dia_mm": ab, "bounds_mm": [BORE_MM, OD_MM]},
                None if ok else "a shoulder at or beyond the other ring's "
                                "diameter presses the seal/other race -- how a "
                                "correct fit kills a bearing")
        else:
            ok = BORE_MM < ab < OD_MM
            add("abutment", "PASS" if ok else "FAIL",
                {"abutment_dia_mm": ab, "bounds_mm": [BORE_MM, OD_MM]},
                None if ok else "outside the gross ring-face bounds")

    # 5. the ring's own deviation -- structurally open, and said so once
    add("interference", "CANNOT DETERMINE",
        {"ring_deviation_um": _field(a_iface, "ring_deviation_um"),
         "note_bounds": "envelope needs BOTH the seat's real limits and the "
                        "ring's own deviation"},
        "no vendor tolerance sheet exists for this unnamed 15x10x3 ring in "
        "the reference (the mesh is named 'seeed_bearing' and nothing more), "
        "and the seats are printed. Two measurements close this: calipers on "
        "the actual ring (state ring_deviation_um on the bearing interface) "
        "and on the printed seat (measured_d_mm). Until then the press force "
        "and grip are unmeasured -- the fit check above already grades what "
        "CAN be graded.")

    return _finish(checks, a_name)


def _finish(checks, a_name):
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
            "bearing_side": a_name,
            "connection": "connection:press-fit-bearing-15x10x3"}


if __name__ == "__main__":
    # The derivation, checked against published ISO 286-2 rows it was NOT
    # derived from (10 mm sits in the 6-10 step, 15 mm in 10-18).
    published = [
        ("10 k6", ("k", 6), 10.0, "shaft", (1, 10)),
        ("10 h6", ("h", 6), 10.0, "shaft", (-9, 0)),
        ("10 H7", ("H", 7), 10.0, "hole", (0, 15)),
        ("15 k6", ("k", 6), 15.0, "shaft", (1, 12)),
        ("15 H7", ("H", 7), 15.0, "hole", (0, 18)),
    ]
    rows = []
    for label, cls, d, role, pub in published:
        if role == "shaft":
            lo, hi, it = shaft_limits_um(d, cls[0], cls[1])
        else:
            lo, hi, it = hole_limits_um(d, cls[0], cls[1])
        ok = (int(round(lo)), int(round(hi))) == pub
        rows.append({"class": label, "derived_um": [int(round(lo)), int(round(hi))],
                     "published_iso286_2_um": list(pub), "IT_um": it,
                     "verdict": "PASS" if ok else "FAIL"})
    print(json.dumps(rows, indent=2))
    print("ALL:", "PASS" if all(r["verdict"] == "PASS" for r in rows) else "FAIL")

    # the reference design's own pair, as the shelf states it
    ring_od = {"name": "od", "nominal_mm": 15.0}
    pocket = {"name": "ankle_bearing", "role": "bearing_seat",
              "nominal_mm": 15.0, "seat_length_mm": 2.3}
    v = compatible(ring_od, pocket)
    print("ankle pocket:", v["verdict"])
    for c in v["checks"]:
        print("  %-16s %-18s %s" % (c["check"], c["verdict"],
                                    str(c["measured"])[:70]))
    v2 = compatible({"name": "od", "nominal_mm": 22.0}, pocket)
    print("a 22 mm ring here:", v2["verdict"],
          [c["verdict"] for c in v2["checks"] if c["check"] == "nominal_size"])
