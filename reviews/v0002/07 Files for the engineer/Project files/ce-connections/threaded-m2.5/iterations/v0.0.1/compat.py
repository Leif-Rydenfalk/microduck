"""connection:threaded-m2.5 -- is this pair of M2.5 interfaces actually matable?

Contract (TRIAD.md, ce-connections section):

    def compatible(a_iface, b_iface) -> dict
        {"verdict": "PASS" | "FAIL" | "CANNOT DETERMINE", "why": ..., "checks": [...]}

Three verdicts, and CANNOT DETERMINE is not a pass. The folder verdict is the
WORST of the checks -- the same rule ce-parts/SCHEMA.md applies to a part.

Shaped after ce-connections/threaded-m2 in this same repo (which is itself
shaped after the workshop's threaded-m3; that header says the arithmetic is
deliberately duplicated into each folder -- TRIAD.md line 51, an iteration
folder is COMPLETE, never a diff). The numbers are the M2.5 row of the ISO
tables, DERIVED here from the ISO 68-1 basic profile rather than recalled, and
checked against two independent statements of the same row:

  - the published M2.5 tensile stress area, 3.39 mm2 (the figure ISO 898-1
    tables carry for M2.5; quoted, not used in the derivation), and
  - ce-cad/cecad/fasteners.py line 58, the M2.5 row of the ISO 273 / ISO 4762
    table this workshop already builds against:
      ("M2.5", 2.5, 0.45, 2.05, 2.70, 2.90, 3.10, 4.5, 2.5, 5.2, 5.0, 6.0, 0.5)
    (name, d, coarse pitch, tap drill, close/normal/loose clearance, head_d,
    head_h, cbore_d, hex_af, washer_od, washer_t).

WHY M2.5 EXISTS ALONGSIDE threaded-m2: the Microduck is an M2 system almost
everywhere, but not everywhere. SPEC.md section 4's hole census reads FOUR hole
populations off Pollen's meshes -- "Ø2.2 clearance x77, Ø4.4 c'bore x28, Ø1.6
tap x20, Ø2.7/2.8 x20" -- and the fourth is not an M2 population. Ø2.70 is the
fasteners.py M2.5 CLOSE clearance and Ø2.90 its M2.5 NORMAL clearance, exactly
the pair bracketing that Ø2.7/2.8 group; docs/BOM.md section 4 buys "M2.5x6 x20"
for it, one screw per hole. This folder exists so those twenty positions -- the
three head-close screws measured at Ø2.695 (out/verify/manufacturing_partial.json,
bottom_head_shell) and the four compute-board mount holes measured at Ø2.8140
(part:radxa-zero-3w cad/interfaces.json, tools/measure_radxa_drawing.py) -- can
name a connection that resolves instead of borrowing the M2 one they are loose
in. Ø2.814 on an M2 screw is 0.814 mm of diametral float; on an M2.5 it is
0.314 mm.

Run this file directly to print the derivation:

    python3 compat.py
"""

import json
import math

PITCH_MM = 0.45         # ISO 261 coarse pitch for nominal diameter 2.5 mm
                        # (cross-check: cecad/fasteners.py M2.5 row, pitch 0.45)
NOMINAL_MM = 2.5

WORST = {"PASS": 0, "CANNOT DETERMINE": 1, "FAIL": 2}


# --------------------------------------------------------------------------
# reading an interface record -- FLAT or ce-parts-NESTED
# (duplicated from ce-connections/threaded-m2, same defect history applies)
# --------------------------------------------------------------------------

def _field(iface, key, *aliases):
    """One scalar off an interface record, flat first then under `measured`.

    Returns None when nothing carries the key: a missing value stays missing
    and the caller still refuses.
    """
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


def read_thread(iface, what="interface"):
    """The thread record as a DICT, in either shelf spelling.

    Accepts the object {designation, pitch_mm, ...} and the shelf's string
    spelling "M2.5x0.45" (ce-parts writes both; the string crash is documented in
    ce-connections/threaded-m3/compat.py's read_thread and the same reader is
    carried here). A spelling it cannot split RAISES, naming the value --
    nothing is defaulted.
    """
    th = _field(iface, "thread")
    if th is None:
        return {}
    if isinstance(th, dict):
        return dict(th)
    if not isinstance(th, str):
        raise ValueError(
            "%s states thread as %s (%r) -- CANNOT DETERMINE. This folder reads a "
            "thread record as an object {designation, pitch_mm, ...} or as the "
            "string spelling 'M2.5x0.45'. Nothing else is interpreted."
            % (what, type(th).__name__, th))
    s = th.upper().replace(" ", "").replace(",", ".")
    if "X" in s:
        des, _, pitch = s.partition("X")
        try:
            return {"designation": des, "pitch_mm": float(pitch), "spelling": th}
        except ValueError:
            raise ValueError(
                "%s states thread %r -- the text after the 'x' is not a pitch in mm "
                "and CANNOT DETERMINE. Nothing is assumed." % (what, th))
    return {"designation": s, "spelling": th}


# --------------------------------------------------------------------------
# ISO 68-1 basic profile, derived rather than recalled
# --------------------------------------------------------------------------

def thread_geometry(d_mm=NOMINAL_MM, p_mm=PITCH_MM):
    """Derive the M-profile diameters and the tensile stress area.

    ISO 68-1 fixes a 60 degree symmetric triangular basic profile, from which:
        H  = P * sqrt(3) / 2          height of the fundamental triangle
        d2 = d - 2 * (3/8) H          basic pitch diameter      = d - 0.649519 P
        d3 = d - 2 * (17/24) H        bolt minor (rounded root) = d - 1.226869 P
        D1 = d - 2 * (5/8) H          nut minor diameter        = d - 1.082532 P
        As = (pi/4) * ((d2 + d3)/2)^2 tensile stress area (the ISO 898-1 definition)

    The coefficients are computed from H here, not typed in, so a typo in one
    would show up as a disagreement with the published As (3.39 mm2 for M2.5).
    """
    h = p_mm * math.sqrt(3.0) / 2.0
    d2 = d_mm - 2.0 * (3.0 / 8.0) * h
    d3 = d_mm - 2.0 * (17.0 / 24.0) * h
    d1_nut = d_mm - 2.0 * (5.0 / 8.0) * h
    ds = (d2 + d3) / 2.0
    a_s = math.pi / 4.0 * ds * ds
    return {
        "designation": "M%g x %g" % (d_mm, p_mm),
        "profile": "ISO 68-1, 60 degree basic profile",
        "P_mm": p_mm,
        "H_mm": h,
        "d_major_mm": d_mm,
        "d2_pitch_mm": d2,
        "d3_bolt_minor_mm": d3,
        "D1_nut_minor_mm": d1_nut,
        "ds_stress_dia_mm": ds,
        "As_tensile_stress_area_mm2": a_s,
    }


def preload_from_torque(torque_Nm, mu_thread, mu_bearing, d_km_mm,
                        d2_mm=None, p_mm=PITCH_MM):
    """Preload F (N) from tightening torque, the long-form relation.

        T = F * ( P/(2*pi) + mu_th * d2 / (2*cos(30 deg)) + mu_b * D_km / 2 )

    EVERY ARGUMENT IS REQUIRED AND NONE HAS A DEFAULT. An assumed friction
    coefficient moves the answer by more than 2x (see threaded-m3 ledger row
    0004); nobody in this workshop has measured one for an M2.5 either.
    """
    for name, val in (("torque_Nm", torque_Nm), ("mu_thread", mu_thread),
                      ("mu_bearing", mu_bearing), ("d_km_mm", d_km_mm)):
        if val is None:
            raise ValueError("preload_from_torque: %s is None. No defaults, on "
                             "purpose -- an unmeasured friction coefficient makes "
                             "the answer a guess with a unit on it." % name)
    if d2_mm is None:
        d2_mm = thread_geometry(NOMINAL_MM, p_mm)["d2_pitch_mm"]
    k = (p_mm / (2.0 * math.pi)
         + mu_thread * d2_mm / (2.0 * math.cos(math.radians(30.0)))
         + mu_bearing * d_km_mm / 2.0)
    return {"preload_N": torque_Nm * 1000.0 / k, "k_effective_mm": k,
            "inputs": {"torque_Nm": torque_Nm, "mu_thread": mu_thread,
                       "mu_bearing": mu_bearing, "d_km_mm": d_km_mm,
                       "d2_mm": d2_mm}}


# --------------------------------------------------------------------------
# the verdict
# --------------------------------------------------------------------------

def _norm_designation(x):
    return str(x).upper().replace(" ", "").replace(",", ".")


def compatible(a_iface, b_iface):
    checks = []

    def add(name, verdict, measured, note=None):
        checks.append({"check": name, "verdict": verdict, "measured": measured,
                       "note": note})

    # 1. the interface names are the fixed pilot names
    names = (a_iface.get("name"), b_iface.get("name"))
    if names == ("thread_ext", "thread_int"):
        add("interface_names", "PASS", "a=thread_ext, b=thread_int")
    else:
        add("interface_names", "FAIL", "a=%r, b=%r" % names,
            "connection:threaded-m2.5 mates thread_ext (external) to thread_int "
            "(internal), in that order -- the same pilot names threaded-m3 fixed.")

    # 2. both sides declare a thread, and it is M2.5
    geo = thread_geometry()
    for side, iface in (("a", a_iface), ("b", b_iface)):
        th = read_thread(iface, "%s_iface" % side)
        des = th.get("designation")
        if des is None:
            add("%s_thread_designation" % side, "CANNOT DETERMINE", None,
                "no thread.designation on the interface. Nothing is assumed.")
        elif _norm_designation(des) in ("M2.5", "M2.5X0.45"):
            add("%s_thread_designation" % side, "PASS", des)
        else:
            add("%s_thread_designation" % side, "FAIL", des,
                "this folder is M2.5 coarse only; another size is another folder")

    # 3. pitches agree with each other AND with ISO 261 coarse
    pa = read_thread(a_iface, "a_iface").get("pitch_mm")
    pb = read_thread(b_iface, "b_iface").get("pitch_mm")
    if pa is None or pb is None:
        add("pitch_match", "CANNOT DETERMINE", {"a": pa, "b": pb},
            "an interface that does not state its pitch cannot be checked against "
            "the other. M2.5 x 0.35 fine exists and will not mate with "
            "M2.5 x 0.45.")
    elif abs(float(pa) - float(pb)) > 1e-9:
        add("pitch_match", "FAIL", {"a": pa, "b": pb},
            "pitches differ: the pair cannot be assembled at all")
    elif abs(float(pa) - PITCH_MM) > 1e-9:
        add("pitch_match", "FAIL", {"a": pa, "b": pb},
            "both are %s mm, which is not the ISO 261 coarse pitch %s mm for M2.5"
            % (pa, PITCH_MM))
    else:
        add("pitch_match", "PASS", {"a": pa, "b": pb, "iso261_coarse_mm": PITCH_MM})

    # 4. handedness
    ha = read_thread(a_iface, "a_iface").get("hand", "right")
    hb = read_thread(b_iface, "b_iface").get("hand", "right")
    if ha == hb:
        add("hand", "PASS", {"a": ha, "b": hb})
    else:
        add("hand", "FAIL", {"a": ha, "b": hb}, "left-hand will not enter right-hand")

    # 5. thread engagement length -- REPORTED, not graded (threaded-m3 rule:
    #    the 1.0xd/2.0xd/2.5xd thresholds are unsourced rules of thumb)
    depth = _field(b_iface, "thread_depth_mm")
    a_len = _field(a_iface, "thread_length_mm")
    if depth is None or a_len is None:
        add("engagement", "CANNOT DETERMINE",
            {"b_thread_depth_mm": depth, "a_thread_length_mm": a_len},
            "engagement length is the number that decides whether the joint "
            "strips the internal thread before the screw yields. Neither side "
            "stated enough to compute it. On this robot the internal side is "
            "usually a SELF-TAPPED PLA pilot (Ø2.100 measured on the head-close "
            "posts, out/verify/manufacturing_partial.json) "
            "and no pull-out has been measured, so the threshold question is "
            "doubly open.")
    else:
        engage = min(float(depth), float(a_len))
        add("engagement", "PASS", {"engaged_mm": engage,
                                   "engagement_over_d": engage / NOMINAL_MM},
            "reported, not graded against a threshold -- the classic multiples "
            "are unsourced rules of thumb (threaded-m3 ledger row 0005).")

    # 6. the internal side's pilot/tap diameter, when it is stated.
    #    The M2.5 tap drill for ~65-70%% engagement is 2.05 mm
    #    (cecad/fasteners.py M2.5 row). Pollen's printed head-close posts
    #    measure Ø2.100 x 11.200 with a Ø2.800 x 0.800 lead-in -- 0.05 mm above
    #    the tap drill, a thread-forming pilot. A pilot at or above the 2.5
    #    major has no material to cut a thread in: FAIL.
    pilot = _field(b_iface, "pilot_d_mm", "tap_d_mm")
    if pilot is not None:
        p = float(pilot)
        if p >= NOMINAL_MM:
            add("pilot_diameter", "FAIL", {"pilot_d_mm": p},
                "pilot >= the 2.5 mm major diameter: the screw has nothing to "
                "thread into")
        elif p < geo["D1_nut_minor_mm"] - 0.3:
            add("pilot_diameter", "CANNOT DETERMINE", {"pilot_d_mm": p},
                "pilot well below the derived D1 %.3f mm: a forming screw may "
                "still enter PLA but the torque and split risk are unmeasured"
                % geo["D1_nut_minor_mm"])
        else:
            add("pilot_diameter", "PASS",
                {"pilot_d_mm": p, "tap_drill_mm": 2.05,
                 "D1_derived_mm": geo["D1_nut_minor_mm"]},
                "within the band between the derived nut minor D1 and the major; "
                "2.05 is the fasteners.py M2.5 tap drill")

    # 7. preload / torque -- structurally CANNOT DETERMINE
    mu_t = (_field(a_iface, "friction") or {}).get("mu_thread")
    mu_b = (_field(a_iface, "friction") or {}).get("mu_bearing")
    d_km = _field(a_iface, "d_km_mm")
    if None in (mu_t, mu_b, d_km):
        add("preload", "CANNOT DETERMINE",
            {"mu_thread": mu_t, "mu_bearing": mu_b, "d_km_mm": d_km,
             "As_mm2": geo["As_tensile_stress_area_mm2"]},
            "Torque-to-preload needs two measured friction coefficients and the "
            "mean under-head bearing diameter. None has been measured in this "
            "workshop for any size (threaded-m3 records the same refusal). "
            "Supply measured values on a_iface['friction'] and a_iface['d_km_mm'] "
            "and this check computes a number. It will not invent one.")
    else:
        add("preload", "PASS",
            preload_from_torque(_field(a_iface, "torque_Nm") or 1.0, mu_t, mu_b,
                                d_km, geo["d2_pitch_mm"]),
            "computed from the caller's OWN measured friction")

    worst = max((c["verdict"] for c in checks), key=lambda v: WORST[v])
    fails = [c["check"] for c in checks if c["verdict"] == "FAIL"]
    unknown = [c["check"] for c in checks if c["verdict"] == "CANNOT DETERMINE"]
    if worst == "PASS":
        why = ("all %d checks PASS. M2.5 x %s, ISO 68-1 profile, As = %.4f mm2 "
               "derived." % (len(checks), PITCH_MM,
                             geo["As_tensile_stress_area_mm2"]))
    elif worst == "FAIL":
        why = "FAILING checks: %s. (also CANNOT DETERMINE: %s)" % (
            ", ".join(fails), ", ".join(unknown) or "none")
    else:
        why = ("no check FAILS, but %d could not be measured: %s. CANNOT "
               "DETERMINE is not a pass." % (len(unknown), ", ".join(unknown)))
    return {"verdict": worst, "why": why, "checks": checks,
            "derived_thread_geometry": geo,
            "connection": "connection:threaded-m2.5"}


if __name__ == "__main__":
    g = thread_geometry()
    print(json.dumps(g, indent=2))
    published_as = 3.39     # the ISO 898-1 M2.5 figure this derivation is CHECKED AGAINST
    err = abs(g["As_tensile_stress_area_mm2"] - published_as)
    print("As derived = %.6f mm2; published M2.5 tensile stress area = %.2f mm2; "
          "delta = %.6f mm2 -> %s"
          % (g["As_tensile_stress_area_mm2"], published_as, err,
             "PASS" if err < 0.005 else "FAIL"))
    # published ISO 261/724 basic diameters for M2.5 x 0.45, quoted as the check:
    published = {"d2": 2.208, "d3": 1.948, "D1": 2.013}
    for key, pub in (("d2_pitch_mm", published["d2"]),
                     ("d3_bolt_minor_mm", published["d3"]),
                     ("D1_nut_minor_mm", published["D1"])):
        print("%s derived %.6f vs published %.3f -> %s"
              % (key, g[key], pub,
                 "PASS" if abs(g[key] - pub) <= 0.0009 else "FAIL"))
