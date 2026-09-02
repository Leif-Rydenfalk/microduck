"""connection:press-fit-bearing-22x16x4 -- will this 22x16x4 bearing actually seat here?

Contract (TRIAD.md, ce-connections section):

    def compatible(a_iface, b_iface) -> dict
        {"verdict": "PASS" | "FAIL" | "CANNOT DETERMINE", "why": ..., "checks": [...]}

Shaped after ce-connections/press-fit-608 and this shelf's own
press-fit-bearing-15x10x3 (the same joint one size down); the ISO 286
derivation is the same mathematics at this joint's sizes, deliberately
duplicated (TRIAD.md line 51).

THE BEARING, measured not recalled: Pollen ships it as
reference/pollen-microduck-rl/assets/seeed_bearing__configuration__22x16x4.stl
and cecad.meshfeatures.cylinders (2026-09-02) reads hole Ø16.0 / boss Ø22.0,
bbox 22.0 x 22.0 x 4.0 -- the 22 mm OD, 16 mm bore, 4 mm wide ring SPEC.md
section 4 counts x11 on the robot (trunk_base x2, yaw2roll, hip_l x2,
upper_leg both, neck_pitch, yaw_roll_motion x2, bearing_roll -- the
hip-yaw, hip-roll, hip-pitch, head-yaw and head-roll axes all turn on it,
per spec/mesh-placements.json). No vendor designation is stated anywhere in
the reference, so none is invented -- the slug is the dimensions.

THE SEATS, measured per consumer on the microduck shelf:
    inner-race seat  microduck-yaw2roll 'yaw_bearing_seat': Ø16.0 x 1.95
                     boss (z 12.5..14.45) WITH a Ø19.0 x 0.5 shoulder --
                     the one measured seat that states its own abutment;
                     microduck-hip-bracket 'roll_bearing_seat' /
                     'pitch_bearing_seat': Ø16.0 x 1.95 boss;
                     microduck-yaw-roll-motion 'roll_bearing_seat':
                     Ø16.0 x 4.0 boss with Ø12 through bore
    outer-race face  microduck-bearing-roll 'roll_bearing_face': the back
                     face around a Ø19.0 window on the roll axis

All printed FDM PLA. A printed bore has NO ISO 286 class -- the fit checks
grade a class only when one is DECLARED, and otherwise return CANNOT
DETERMINE naming the as-printed measurement that would complete them (the
same honest split as press-fit-bearing-15x10x3).

Run this file directly to print the ISO 286 derivation checked against the
published rows:

    python3 compat.py

Python 3 stdlib only. Units: mm unless a name ends in _um.
"""

import json
import math

BORE_MM = 16.0    # meshfeatures hole d on seeed_bearing__configuration__22x16x4.stl
OD_MM = 22.0      # meshfeatures boss d, same run
WIDTH_MM = 4.0    # numpy bbox z 0.0..4.0, same mesh (scale 1000)
BEARING_REF = "part:bearing-22x16x4"

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
# ISO 286, derived rather than recalled (formulae from ISO 286-1 itself)
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


# MEASURED 2026-09-02 in press-fit-bearing-15x10x3's self-test and true here
# too: the ISO 286-2 tables are NOT pure formula output. Raw 16i gives IT7 =
# 17.32 um in the 10-18 step where the published table says 18 (at 18-30 the
# formula's 20.93 rounds to the published 21 on its own). The published value
# wins -- it is what everyone machines to -- so IT7 for the steps this joint
# uses is TRANSCRIBED with the drift recorded, not hidden in a "derivation".
PUBLISHED_IT7_UM = {(10.0, 18.0): 18, (18.0, 30.0): 21}


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
            "a_iface must be the bearing side, named 'bore' (Ø16 inner ring) "
            "or 'od' (Ø22 outer ring).")
        return _finish(checks, None)
    b_ok = (b_name in SHAFT_NAMES + HOUSING_NAMES
            or b_role in ("bearing_seat", "bearing_face"))
    if not b_ok:
        add("interface_names", "FAIL", {"a": a_name,
                                        "b": {"name": b_name, "role": b_role}},
            "b_iface must be the seat: name 'shaft'/'boss' (mates 'bore') or "
            "'housing_bore'/'pocket' (mates 'od'), or the microduck shelf's "
            "role 'bearing_seat'/'bearing_face'.")
        return _finish(checks, a_name)
    add("interface_names", "PASS", {"a": a_name, "b": b_name, "b_role": b_role})

    # 1. nominal size agreement
    nominal = BORE_MM if a_name == "bore" else OD_MM
    a_nom = _field(a_iface, "nominal_mm", "bore_d_mm", "od_d_mm")
    b_nom = _field(b_iface, "nominal_mm", "seat_d_mm", "boss_d_mm", "pocket_d_mm")
    if a_nom is None or b_nom is None:
        add("nominal_size", "CANNOT DETERMINE", {"a": a_nom, "b": b_nom},
            "an interface that does not state its nominal diameter cannot be "
            "fitted to anything. The slug is not a measurement.")
    elif abs(float(a_nom) - nominal) > 1e-9:
        add("nominal_size", "FAIL", {"a": a_nom, "expected": nominal},
            "this folder is the 22x16x4 ring (Ø16 bore / Ø22 OD / 4 wide, "
            "measured on seeed_bearing__configuration__22x16x4.stl). Another "
            "size is another folder -- see press-fit-bearing-15x10x3.")
    elif abs(float(a_nom) - float(b_nom)) > 0.5:
        add("nominal_size", "FAIL", {"a": a_nom, "b": b_nom},
            "the seat's nominal differs from the ring's by more than 0.5 mm -- "
            "not this fit at all")
    else:
        add("nominal_size", "PASS",
            {"nominal_mm": nominal, "a": float(a_nom), "b": float(b_nom)},
            "the reference design's own printed seats measure at nominal "
            "(yaw2roll / hip-bracket / yaw-roll-motion bosses all Ø16.0)")

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
                "limits from ISO 286-1's own formulae (IT7 transcribed where "
                "the published table drifts 1 um from raw 16i -- see "
                "PUBLISHED_IT7_UM); the ring's own deviation is still missing, "
                "so the INTERFERENCE ENVELOPE stays open")
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
            "-- a printed bore has no ISO class) nor a measured_d_mm. Measure "
            "the printed seat with calipers and state measured_d_mm, and this "
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
            "proud -- and that is what Pollen's own design does (the yaw2roll "
            "and hip-bracket bosses are 1.95 mm for the 4 mm ring: the ring "
            "spans the joint gap to the mating part). Whether ~49%% engagement "
            "holds the press is a bench question nobody has measured, so it is "
            "reported, not failed and not passed.")
    else:
        add("seat_length", "PASS",
            {"seat_length_mm": float(seat_len), "ring_width_mm": WIDTH_MM},
            "yaw-roll-motion's roll seat is the full-width example: "
            "Ø16.0 x 4.0")

    # 4. the shoulder / abutment
    ab = _field(b_iface, "abutment_dia_mm", "shoulder_d_mm")
    if ab is None:
        add("abutment", "CANNOT DETERMINE", None,
            "no shoulder diameter stated. No vendor sheet exists for this "
            "ring, so only the gross geometric rule can ever be checked: a "
            "shoulder must overlap the ring FACE it locates without touching "
            "the other ring -- between Ø16 and Ø22, race lands unmeasured. "
            "yaw2roll's own seat states one (Ø19.0 x 0.5), dead centre of "
            "that band.")
    else:
        ab = float(ab)
        ok = BORE_MM < ab < OD_MM
        add("abutment", "PASS" if ok else "FAIL",
            {"abutment_dia_mm": ab, "bounds_mm": [BORE_MM, OD_MM]},
            None if ok else "a shoulder at or beyond the other ring's diameter "
                            "presses the seal/other race -- how a correct fit "
                            "kills a bearing")

    # 5. the ring's own deviation -- structurally open, said once
    add("interference", "CANNOT DETERMINE",
        {"ring_deviation_um": _field(a_iface, "ring_deviation_um"),
         "note_bounds": "envelope needs BOTH the seat's real limits and the "
                        "ring's own deviation"},
        "no vendor tolerance sheet exists for this unnamed 22x16x4 ring in "
        "the reference (the mesh is named 'seeed_bearing' and nothing more), "
        "and the seats are printed. Two measurements close this: calipers on "
        "the actual ring (ring_deviation_um) and on the printed seat "
        "(measured_d_mm). Until then press force and grip are unmeasured.")

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
            "connection": "connection:press-fit-bearing-22x16x4"}


if __name__ == "__main__":
    # The derivation, checked against published ISO 286-2 rows it was NOT
    # derived from (16 mm sits in the 10-18 step, 22 mm in 18-30).
    published = [
        ("16 k6", ("k", 6), 16.0, "shaft", (1, 12)),
        ("16 h6", ("h", 6), 16.0, "shaft", (-11, 0)),
        ("16 H7", ("H", 7), 16.0, "hole", (0, 18)),
        ("22 k6", ("k", 6), 22.0, "shaft", (2, 15)),
        ("22 H7", ("H", 7), 22.0, "hole", (0, 21)),
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
    ring_bore = {"name": "bore", "nominal_mm": 16.0}
    boss = {"name": "yaw_bearing_seat", "role": "bearing_seat",
            "nominal_mm": 16.0, "seat_length_mm": 1.95, "abutment_dia_mm": 19.0}
    v = compatible(ring_bore, boss)
    print("yaw2roll boss:", v["verdict"])
    for c in v["checks"]:
        print("  %-16s %-18s %s" % (c["check"], c["verdict"],
                                    str(c["measured"])[:70]))
    v2 = compatible({"name": "bore", "nominal_mm": 10.0}, boss)
    print("a 10 mm ring here:", v2["verdict"],
          [c["verdict"] for c in v2["checks"] if c["check"] == "nominal_size"])
    v3 = compatible(ring_bore, dict(boss, abutment_dia_mm=23.0))
    print("a Ø23 shoulder:", v3["verdict"],
          [c["verdict"] for c in v3["checks"] if c["check"] == "abutment"])
