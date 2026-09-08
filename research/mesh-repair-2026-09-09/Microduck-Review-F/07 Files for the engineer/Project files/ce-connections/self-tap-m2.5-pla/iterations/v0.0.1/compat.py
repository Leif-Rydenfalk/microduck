"""connection:self-tap-m2.5-pla -- is this pair actually matable, and is the pilot a
pilot?

Contract (TRIAD.md, ce-connections section):

    def compatible(a_iface, b_iface) -> dict
        {"verdict": "PASS"|"FAIL"|"CANNOT DETERMINE", "why": ..., "checks": [...]}

Three verdicts. CANNOT DETERMINE is NOT a pass, and the folder verdict is the
WORST of the checks -- the rule ce-parts/SCHEMA.md applies to a part.

WHAT THIS FILE GRADES THAT connection:threaded-m2.5's CANNOT
-----------------------------------------------------------------
threaded-m2.5 grades a CUT thread against ISO fits. There is no cut thread here.
What can be graded is:

  1. the interface NAMES -- 'thread_ext' and 'pilot'. A record named
     'thread_int' is a cut thread and belongs to the other folder; accepting it
     here is the silent-substitution failure this folder was split off to stop.
  2. the pilot DIAMETER, against the band MEASURED on the reference meshes:
     11 pilots of this size, 8 of them at exactly Ø2.05 mm
     (out/fasteners/features-by-mesh.json, cecad.meshfeatures.features(),
     2026-09-04). PILOT_MIN/MAX below IS that measured spread. It is not a
     tolerance class: a printed hole has no ISO class.
  3. the SCREW SIZE, against this folder's own size.
  4. the ENGAGEMENT, when both sides state their measured numbers: the screw
     must reach at least 1.5 d of thread and must not bottom in the pilot.
  5. the HOLDING -- and this one is always CANNOT DETERMINE, on purpose. No
     M2.5 screw has been pulled out of a printed Ø2.05 pilot in this
     workshop. compatible() therefore CANNOT return PASS for a real pair: the
     best available verdict is CANNOT DETERMINE with the coupon test named.
     That is not pessimism, it is the honest state of the evidence, and a
     folder that returned PASS here would be claiming a number nobody has.

Run it:  python3 compat.py

Units: mm, degrees, newtons.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "cad"))
from mate import (NOMINAL_MM, PITCH_MM, PILOT_NOMINAL_MM, PILOT_MEASURED_MIN_MM,  # noqa: E402
                  PILOT_MEASURED_MAX_MM, MIN_ENGAGE_D, EXTERNAL_PROVIDER_PART,
                  INTERNAL_PROVIDER_PART, _field, read_thread)

SIZE = "M2.5"
# The pilots this band was read off, MEASURED 2026-09-04. Listed so a reader can
# recompute the band instead of trusting two constants.
PILOTS_MEASURED_MM = [2.05, 2.05, 2.05, 2.05, 2.05, 2.05, 2.05, 2.05, 2.1, 2.1, 2.1]


def band():
    """Re-derive the accept band from the measurements, and check the constants."""
    lo, hi = min(PILOTS_MEASURED_MM), max(PILOTS_MEASURED_MM)
    return dict(measured_min_mm=lo, measured_max_mm=hi, n=len(PILOTS_MEASURED_MM),
                accept_min_mm=PILOT_MEASURED_MIN_MM, accept_max_mm=PILOT_MEASURED_MAX_MM,
                band_contains_every_measurement=(PILOT_MEASURED_MIN_MM <= lo
                                                 and hi <= PILOT_MEASURED_MAX_MM))


def compatible(a_iface, b_iface):
    checks = []

    def add(name, verdict, measured, note=None):
        checks.append({"check": name, "verdict": verdict, "measured": measured,
                        "note": note})

    names = (a_iface.get("name"), b_iface.get("name"))
    if names == ("thread_ext", "pilot"):
        add("interface_names", "PASS", "a=thread_ext, b=pilot")
    else:
        add("interface_names", "FAIL", "a=%r, b=%r" % names,
            "connection:self-tap-m2.5-pla mates thread_ext (the screw) to pilot (the PRINTED HOLE), "
            "in that order. 'thread_int' means a CUT thread and is connection:threaded-m2.5.")

    th = read_thread(a_iface, "a_iface")
    des = (th.get("designation") or "")
    if str(des).upper().replace(" ", "") in ("M2.5", "M2.5X0.45"):
        add("screw_size", "PASS", des)
    elif not des:
        add("screw_size", "CANNOT DETERMINE", None,
            "a_iface states no thread.designation; nothing is assumed")
    else:
        add("screw_size", "FAIL", des, "this folder is M2.5 only")

    d = _field(b_iface, "pilot_d_mm", "d_mm", "diameter_mm")
    if d is None:
        add("pilot_diameter", "CANNOT DETERMINE", None,
            "b_iface states no pilot_d_mm. A printed hole has no nominal to fall back on.")
    else:
        d = float(d)
        ok = PILOT_MEASURED_MIN_MM <= d <= PILOT_MEASURED_MAX_MM
        add("pilot_diameter", "PASS" if ok else "FAIL", d,
            "measured band [%.3f, %.3f] mm from %d pilots on the reference meshes; "
            "nominal Ø%.2f" % (PILOT_MEASURED_MIN_MM, PILOT_MEASURED_MAX_MM,
                               len(PILOTS_MEASURED_MM), PILOT_NOMINAL_MM))

    grip = _field(a_iface, "grip_length_mm")
    depth = _field(b_iface, "pilot_depth_mm", "depth_mm")
    length = _field(a_iface, "length_mm", "screw_length_mm")
    if grip is None or depth is None or length is None:
        add("engagement", "CANNOT DETERMINE",
            {"grip_length_mm": grip, "pilot_depth_mm": depth, "screw_length_mm": length},
            "all three are MEASUREMENTS somebody has to take; "
            "ce-designs/microduck/tools/fastener_runs.py takes the first two for every run "
            "in this robot. Nothing is defaulted.")
    else:
        engaged = float(length) - float(grip)
        need = MIN_ENGAGE_D * NOMINAL_MM
        if engaged < 0:
            add("engagement", "FAIL", round(engaged, 4),
                "the screw is SHORTER than the grip: it never reaches the pilot")
        elif engaged < need:
            add("engagement", "FAIL", round(engaged, 4),
                "%.4f mm of thread engaged, under the %g d = %.4f mm RULE (a rule, not a "
                "measurement of this robot)" % (engaged, MIN_ENGAGE_D, need))
        elif engaged > float(depth):
            add("engagement", "FAIL", round(engaged, 4),
                "the screw bottoms: %.4f mm of thread into a %.4f mm pilot, so the head never "
                "reaches the seat and the joint carries NO preload" % (engaged, float(depth)))
        else:
            add("engagement", "PASS", round(engaged, 4),
                "%.4f mm engaged, between the %g d rule (%.4f) and the measured pilot depth "
                "(%.4f)" % (engaged, MIN_ENGAGE_D, need, float(depth)))

    for side, iface, table in (("a", a_iface, EXTERNAL_PROVIDER_PART),
                               ("b", b_iface, INTERNAL_PROVIDER_PART)):
        prov = _field(iface, "provider")
        if prov is None:
            add("provider_%s" % side, "CANNOT DETERMINE", None,
                "no provider stated, so what the joint ADDS to the BOM is unknown")
        elif prov in table:
            add("provider_%s" % side, "PASS", prov)
        else:
            add("provider_%s" % side, "FAIL", prov, "not one of %s" % sorted(table))

    add("holding", "CANNOT DETERMINE", None,
        "Strip load, preload, tightening torque and re-insertion count are ALL unmeasured for a "
        "M2.5 screw thread-formed in FDM PLA at a Ø%.2f pilot. connection.json "
        "record.open_questions names the coupon test for each: printed sample of the real resin, "
        "layer height, wall count and infill; screw driven to a recorded torque; pulled to failure "
        "on a force gauge; n >= 5; report mean AND spread. Until that afternoon happens this check "
        "cannot pass, and this folder does not pretend otherwise." % PILOT_NOMINAL_MM)

    order = {"FAIL": 0, "CANNOT DETERMINE": 1, "PASS": 2}
    worst = min((c["verdict"] for c in checks), key=lambda v: order[v])
    return {"verdict": worst,
             "why": "worst of %d checks: %s" % (len(checks), ", ".join(
                 "%s=%s" % (c["check"], c["verdict"]) for c in checks)),
             "checks": checks}


if __name__ == "__main__":
    b = band()
    ok = fail = 0

    def check(label, cond, shown=""):
        global ok, fail
        if cond:
            ok += 1
            print("PASS  %-52s %s" % (label, shown))
        else:
            fail += 1
            print("FAIL  %-52s %s" % (label, shown))

    print("pilot band, re-derived from the %d measurements" % b["n"])
    check("accept band contains every measured pilot", b["band_contains_every_measurement"],
          "measured [%.3f, %.3f] inside accept [%.3f, %.3f]"
          % (b["measured_min_mm"], b["measured_max_mm"], b["accept_min_mm"], b["accept_max_mm"]))
    check("nominal Ø%.2f is inside the band" % PILOT_NOMINAL_MM,
          b["accept_min_mm"] <= PILOT_NOMINAL_MM <= b["accept_max_mm"])
    check("band is narrower than the screw's own diameter",
          (b["accept_max_mm"] - b["accept_min_mm"]) < NOMINAL_MM,
          "%.3f mm wide" % (b["accept_max_mm"] - b["accept_min_mm"]))

    good_a = {"name": "thread_ext", "thread": {"designation": SIZE, "pitch_mm": PITCH_MM},
              "provider": "socket_head_cap", "grip_length_mm": 3.0, "length_mm": 8.0}
    good_b = {"name": "pilot", "provider": "printed_pilot",
              "pilot_d_mm": PILOT_NOMINAL_MM, "pilot_depth_mm": 6.0}
    v = compatible(good_a, good_b)
    check("a fully-stated GOOD pair is CANNOT DETERMINE, never PASS",
          v["verdict"] == "CANNOT DETERMINE", v["why"][:70])
    check("...and the only non-PASS check is holding",
          [c["check"] for c in v["checks"] if c["verdict"] != "PASS"] == ["holding"])

    for label, a, bb in (
            ("a thread_int record", good_a, dict(good_b, name="thread_int")),
            ("a pilot 0.5 mm oversize", good_a, dict(good_b, pilot_d_mm=PILOT_NOMINAL_MM + 0.5)),
            ("the wrong screw size", dict(good_a, thread={"designation": "M8"}), good_b),
            ("a screw that bottoms", dict(good_a, length_mm=20.0), good_b),
            ("a screw too short to engage", dict(good_a, length_mm=3.5), good_b),
            ("an unmapped provider", dict(good_a, provider="button_head"), good_b)):
        r = compatible(a, bb)
        check("FAILs %s" % label, r["verdict"] == "FAIL", r["why"][:60])

    r = compatible({"name": "thread_ext"}, {"name": "pilot"})
    check("an empty pair is CANNOT DETERMINE, not FAIL and not PASS",
          r["verdict"] == "CANNOT DETERMINE")

    print("\n%d PASS, %d FAIL" % (ok, fail))
    raise SystemExit(1 if fail else 0)
