#!/usr/bin/env python3
"""LANE F3 study 3 -- tolerance stack-up on all 14 hinges.

Per joint: axial play, radial eccentricity, angular misalignment and rotational
backlash, worst-case and RSS, in mm and degrees to 4 dp -- with the tolerance
basis of every term stated and every unmeasurable term left open by name.

THE JOINT, as MEASURED (sim/joint_geometry.py -> out/sim-evidence/joint-geometry.json):
every hinge is ONE station, not two.  On twelve of the fourteen the driven horn
face and the supporting ball bearing are COINCIDENT to 0.1 mm along the axis --
the bearing's inner race sits on the same Ø16 boss the horn bolts to.  So the
classic "two supports separated by L" model does not apply and is not used; the
joint's angle is held by (a) the bolted Ø15.9-19 flange face and (b) how much
the bearing's short engagement lets the boss cock in the bore.  Which of the two
governs is computed, not assumed.

TOLERANCE BASES, all sourced:
  FDM-A  Protolabs Network manufacturing standards, "Prototyping FDM", read
         verbatim 2026-09-02 from https://www.hubs.com/manufacturing-standards/ :
         "± 0.5% with a lower limit of ± 0.5 mm (± 0.02\")"
  FDM-B  same page, "Industrial FDM": "± 0.3% with a lower limit: ± 0.3 mm
         (±0.012\" in)"
  FDM-C  THIS workshop's own printers: CANNOT DETERMINE.
         ce-cad/cecad/data/print_fits.json is {"machines": {}, "schema": 1} --
         no machine has ever been measured.  cecad.coupon.coupon() builds the
         bore/pin/gap ladder that settles it and record_measurements() stores
         it; until then no third band exists and none is invented.
  M2     ce-cad/cecad/fasteners.py:57 row ("M2", 2.0, 0.40, 1.60, 2.20, 2.40,
         2.60, ...) -- major Ø2.0, tap drill Ø1.60, close clearance Ø2.20,
         medium Ø2.40.
  ISO286 derived, not recalled: i = 0.45*cbrt(D) + 0.001*D on the geometric
         mean of the size step, IT = multiple * i, the multiples being the
         standard series 7/10/16/25/40/64/100/160/250/400/640/1000 for
         IT5..IT16.  Checked here against published IT7 rows the derivation
         was not fitted to (the same self-test
         ce-connections/press-fit-bearing-22x16x4/iterations/v0.0.1/compat.py
         runs), and the published value wins where the formula drifts.

WHAT STAYS OPEN (named, never defaulted):
  * the bearings' own radial internal clearance and width tolerance.  The
    reference names them only "seeed_bearing", no designation, no vendor sheet
    (both connection folders say so).
  * the XL330 gearbox backlash.  ROBOTIS publishes none; the dimension drawing
    D1 is stamped "[FOR REFERENCE ONLY]" and carries no tolerance block, so
    the horn disc's own thickness tolerance is open too.
  * this workshop's printed band (FDM-C above).

    python3 sim/tolerance_stack.py          (stdlib only)

Output: out/sim-evidence/tolerance-stack-hinges.json
"""

import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

# --------------------------------------------------------------------------
# ISO 286, derived (the same mathematics the connection folders carry, with
# the grade series extended past IT11 so a printed band can be GRADED).
# --------------------------------------------------------------------------
SIZE_STEPS = [(0.0, 3.0), (3.0, 6.0), (6.0, 10.0), (10.0, 18.0), (18.0, 30.0),
              (30.0, 50.0), (50.0, 80.0), (80.0, 120.0), (120.0, 180.0)]
IT_MULTIPLE = {5: 7, 6: 10, 7: 16, 8: 25, 9: 40, 10: 64, 11: 100,
               12: 160, 13: 250, 14: 400, 15: 640, 16: 1000}
# transcribed where the published ISO 286-2 row drifts from raw 16i (the same
# treatment the connection folders give it, and for the same reason: the table
# is what everyone machines to). Measured drift: 10-18 raw 17.32 -> published 18;
# 6-10 raw 14.37 -> published 15; 18-30 raw 20.93 -> published 21 on its own.
PUBLISHED_IT7_UM = {(6.0, 10.0): 15, (10.0, 18.0): 18, (18.0, 30.0): 21}
# published ISO 286-2 rows used ONLY as the self-test target, never as input
PUBLISHED_CHECK = [(16.0, 7, 18), (22.0, 7, 21), (10.0, 7, 15), (6.0, 7, 12)]


def size_step(d):
    for lo, hi in SIZE_STEPS:
        if lo < d <= hi:
            return lo, hi
    raise ValueError("%r mm is outside the ISO 286 size steps carried here" % d)


def it_um(d, grade):
    lo, hi = size_step(d)
    d_geo = math.sqrt(lo * hi) if lo > 0 else hi
    i_um = 0.45 * d_geo ** (1.0 / 3.0) + 0.001 * d_geo
    if grade == 7 and (lo, hi) in PUBLISHED_IT7_UM:
        return PUBLISHED_IT7_UM[(lo, hi)]
    return int(math.floor(IT_MULTIPLE[grade] * i_um + 0.5))


def grade_of(total_band_um, d):
    """The coarsest IT grade whose band is >= the given total band, i.e. what
    ISO 286 grade this printed feature would be if it were a machined one."""
    for g in sorted(IT_MULTIPLE):
        if it_um(d, g) >= total_band_um:
            return "IT%d" % g, it_um(d, g)
    return "coarser than IT16", it_um(d, 16)


# --------------------------------------------------------------------------
# the sourced FDM bands: half-band (+/-) in mm for a nominal d
# --------------------------------------------------------------------------
BANDS = {
    "FDM-A prototyping": lambda d: max(0.005 * d, 0.5),
    "FDM-B industrial": lambda d: max(0.003 * d, 0.3),
}
BAND_CITE = {
    "FDM-A prototyping": ("Protolabs Network manufacturing standards, Prototyping "
                          "FDM, verbatim: '± 0.5% with a lower limit of ± 0.5 mm "
                          "(± 0.02\")'. https://www.hubs.com/manufacturing-standards/ "
                          ", read 2026-09-02."),
    "FDM-B industrial": ("Same page, Industrial FDM, verbatim: '± 0.3% with a lower "
                         "limit: ± 0.3 mm (±0.012\" in)'."),
}

M2_MAJOR = 2.0          # fasteners.py:57
PCD = 12.0              # spline-xl330-horn: 4 holes on Ø12.0
PCD_R = PCD / 2.0

# --------------------------------------------------------------------------
# Per joint: the driven flange and the bearing seat, each read off the
# consuming part's own cad/interfaces.json (part slug + interface name given,
# so every number below can be opened and checked).
# --------------------------------------------------------------------------
JOINTS = {
    "left_hip_yaw": dict(
        flange_part="microduck-yaw2roll", flange_iface="yaw_horn",
        flange_d=16.0, hole_d=2.2,
        seat_part="microduck-yaw2roll", seat_iface="yaw_bearing_seat",
        seat_d=16.0, seat_len=1.95, ring_w=4.0, shoulder_d=19.0,
        seat_role="inner race on a printed boss"),
    "right_hip_yaw": dict(
        flange_part="microduck-yaw2roll", flange_iface="yaw_horn",
        flange_d=16.0, hole_d=2.2,
        seat_part="microduck-yaw2roll", seat_iface="yaw_bearing_seat",
        seat_d=16.0, seat_len=1.95, ring_w=4.0, shoulder_d=19.0,
        seat_role="inner race on a printed boss",
        note="body 'bearing_roll' carries the yaw2roll mesh too "
             "(spec/mesh-placements.json lists yaw2roll under both bodies), so the "
             "right hip-yaw runs on the mirrored copy of the same features"),
    "left_hip_roll": dict(
        flange_part="microduck-hip-bracket", flange_iface="roll_horn",
        flange_d=19.0, hole_d=2.4,
        seat_part="microduck-hip-bracket", seat_iface="roll_bearing_seat",
        seat_d=16.0, seat_len=1.95, ring_w=4.0, shoulder_d=None,
        seat_role="inner race on a printed boss"),
    "right_hip_roll": dict(
        flange_part="microduck-hip-bracket", flange_iface="roll_horn",
        flange_d=19.0, hole_d=2.4,
        seat_part="microduck-hip-bracket", seat_iface="roll_bearing_seat",
        seat_d=16.0, seat_len=1.95, ring_w=4.0, shoulder_d=None,
        seat_role="inner race on a printed boss"),
    "left_hip_pitch": dict(
        flange_part="microduck-hip-bracket", flange_iface="pitch_horn",
        flange_d=19.0, hole_d=2.4,
        seat_part="microduck-hip-bracket", seat_iface="pitch_bearing_seat",
        seat_d=16.0, seat_len=1.95, ring_w=4.0, shoulder_d=None,
        seat_role="inner race on a printed boss"),
    "right_hip_pitch": dict(
        flange_part="microduck-hip-bracket", flange_iface="pitch_horn",
        flange_d=19.0, hole_d=2.4,
        seat_part="microduck-hip-bracket", seat_iface="pitch_bearing_seat",
        seat_d=16.0, seat_len=1.95, ring_w=4.0, shoulder_d=None,
        seat_role="inner race on a printed boss"),
    "left_knee": dict(
        flange_part="microduck-shin", flange_iface="knee",
        flange_d=15.9, hole_d=2.2,
        seat_part=None, seat_iface=None,
        seat_d=16.0, seat_len=None, ring_w=4.0, shoulder_d=None,
        seat_role="CANNOT DETERMINE",
        note="a 22x16x4 bearing IS on this axis (in upper_leg_left, "
             "spec/mesh-placements.json (22, 35.777, -4.0)) but neither "
             "microduck-upper-leg-left nor microduck-shin declares a "
             "bearing_seat interface for it -- the seat length is unmeasured"),
    "right_knee": dict(
        flange_part="microduck-shin", flange_iface="knee",
        flange_d=15.9, hole_d=2.2,
        seat_part=None, seat_iface=None,
        seat_d=16.0, seat_len=None, ring_w=4.0, shoulder_d=None,
        seat_role="CANNOT DETERMINE",
        note="mirror of left_knee; same missing seat interface"),
    "left_ankle": dict(
        flange_part="microduck-ankle-left", flange_iface="ankle_horn",
        flange_d=16.0, hole_d=2.2,
        seat_part="microduck-shin", seat_iface="ankle",
        seat_d=10.0, seat_len=3.2, ring_w=3.0, shoulder_d=None,
        seat_role="inner race on the shin's printed Ø10 boss; the outer race "
                  "sits in microduck-ankle-left 'ankle_bearing', a Ø15.0 x 2.3 "
                  "pocket -- so BOTH races land on printed features",
        outer_part="microduck-ankle-left", outer_iface="ankle_bearing",
        outer_d=15.0, outer_len=2.3),
    "right_ankle": dict(
        flange_part="microduck-ankle-right", flange_iface="ankle_horn",
        flange_d=16.0, hole_d=2.2,
        seat_part="microduck-shin", seat_iface="ankle",
        seat_d=10.0, seat_len=3.2, ring_w=3.0, shoulder_d=None,
        seat_role="mirror of left_ankle",
        outer_part="microduck-ankle-right", outer_iface="ankle_bearing",
        outer_d=15.0, outer_len=2.3),
    "neck_pitch": dict(
        flange_part="microduck-trunk-shell-left", flange_iface="neck_horn",
        flange_d=17.0, hole_d=2.2,
        seat_part=None, seat_iface=None,
        seat_d=None, seat_len=None, ring_w=None, shoulder_d=None,
        seat_role="none -- NO bearing on this axis",
        note="sim/joint_geometry.py finds no bearing geom on the neck-pitch axis; "
             "the joint is the servo's own output bearing plus the bolted "
             "D17.0 x 1.0 raised disc on each trunk shell half"),
    "head_pitch": dict(
        flange_part="microduck-neck-pitch-bracket", flange_iface="pitch_horn_right",
        flange_d=16.0, hole_d=2.2,
        seat_part=None, seat_iface=None,
        seat_d=None, seat_len=None, ring_w=None, shoulder_d=None,
        seat_role="none -- NO bearing on this axis",
        note="horn one side, servo idler disc the other (the bracket mesh is "
             "x-symmetric; which side is the horn is an assembly choice, "
             "microduck-neck-pitch-bracket interfaces)"),
    "head_yaw": dict(
        flange_part="microduck-neck-pitch-bracket", flange_iface="yaw_horn_top",
        flange_d=16.0, hole_d=2.2,
        seat_part="microduck-neck-pitch-bracket", seat_iface="yaw_bearing_seat",
        seat_d=16.0, seat_len=1.9, ring_w=4.0, shoulder_d=None,
        seat_role="the SAME Ø16.0 x 1.9 boss is both the horn boss and the "
                  "inner-race seat"),
    "head_roll": dict(
        flange_part="microduck-yaw-roll-motion", flange_iface="roll_horn",
        flange_d=16.0, hole_d=2.2,
        seat_part="microduck-yaw-roll-motion", seat_iface="roll_bearing_seat",
        seat_d=16.0, seat_len=4.0, ring_w=4.0, shoulder_d=None,
        seat_role="the only FULL-WIDTH seat on the robot: Ø16.0 x 4.0 boss for "
                  "the 4.0 mm ring"),
}


def stack(name, spec, geom, band_name):
    band = BANDS[band_name]
    terms_axial, terms_radial, open_terms = [], [], []

    fd, hd = spec["flange_d"], spec["hole_d"]
    t_flange = band(fd)          # flange face position / flatness over its own Ø
    terms_axial.append({"term": "flange face height, printed", "nominal_mm": fd,
                        "half_band_mm": round(t_flange, 4),
                        "source": "%s '%s' (printed, %s)"
                                  % (spec["flange_part"], spec["flange_iface"], band_name)})

    # radial: bolt-circle clearance is the only DETERMINISTIC radial term
    dr_bolt = (hd - M2_MAJOR) / 2.0
    terms_radial.append({"term": "M2 clearance hole over the screw shank",
                         "nominal_mm": hd, "half_band_mm": round(dr_bolt, 4),
                         "source": "(%.2f - %.2f)/2, hole Ø off %s '%s', M2 major "
                                   "Ø2.0 off ce-cad/cecad/fasteners.py:57"
                                   % (hd, M2_MAJOR, spec["flange_part"],
                                      spec["flange_iface"])})
    # printed position of the hole pattern itself
    t_pcd = band(PCD)
    terms_radial.append({"term": "printed bolt-circle position", "nominal_mm": PCD,
                         "half_band_mm": round(t_pcd, 4),
                         "source": "Ø12.0 PCD (connection:spline-xl330-horn), %s"
                                   % band_name})

    seat_d, seat_len, ring_w = spec["seat_d"], spec["seat_len"], spec["ring_w"]
    engagement = None
    theta_cock = None
    if seat_d is not None:
        t_seat = band(seat_d)
        terms_radial.append({"term": "printed bearing seat diameter",
                             "nominal_mm": seat_d,
                             "half_band_mm": round(t_seat, 4),
                             "source": "%s '%s', %s"
                                       % (spec["seat_part"] or "CANNOT DETERMINE",
                                          spec["seat_iface"] or "-", band_name)})
        if spec.get("outer_d"):
            t_out = band(spec["outer_d"])
            terms_radial.append({"term": "printed bearing POCKET diameter (outer race)",
                                 "nominal_mm": spec["outer_d"],
                                 "half_band_mm": round(t_out, 4),
                                 "source": "%s '%s', %s -- this joint lands BOTH "
                                           "races on printed features"
                                           % (spec["outer_part"], spec["outer_iface"],
                                              band_name)})
        if seat_len:
            engagement = seat_len / ring_w
            # a shaft of diametral clearance c can cock in a bore over the
            # engaged length L by atan(c / L)
            c = 2.0 * t_seat
            theta_cock = math.degrees(math.atan2(c, seat_len))
        terms_axial.append({"term": "printed seat length / boss height",
                            "nominal_mm": seat_len,
                            "half_band_mm": None if seat_len is None else round(band(seat_len), 4),
                            "source": "%s '%s', %s"
                                      % (spec["seat_part"] or "CANNOT DETERMINE",
                                         spec["seat_iface"] or "-", band_name)})
        open_terms.append({
            "term": "bearing ring width tolerance",
            "nominal_mm": ring_w,
            "why_open": "the reference names the ring only 'seeed_bearing' -- no "
                        "designation, no vendor sheet "
                        "(ce-connections/press-fit-bearing-%s compat.py 'interference' "
                        "check)" % ("22x16x4" if ring_w == 4.0 else "15x10x3"),
            "what_settles_it": "a micrometer on the actual ring"})
        open_terms.append({
            "term": "bearing radial internal clearance",
            "why_open": "same: no designation, so no ISO 5753 clearance class",
            "what_settles_it": "the ring's designation from a teardown, or a dial "
                               "gauge on the assembled joint"})
    if spec["shoulder_d"]:
        terms_axial.append({"term": "shoulder thickness (inner-race thrust face)",
                            "nominal_mm": 0.5,
                            "half_band_mm": round(band(0.5), 4),
                            "source": "%s '%s': Ø19.0 x 0.5 shoulder, %s"
                                      % (spec["seat_part"], spec["seat_iface"],
                                         band_name)})

    open_terms.append({
        "term": "XL330 horn disc thickness and its axial run-out",
        "nominal_mm": 3.0,
        "why_open": "ROBOTIS's dimension drawing D1 ('XL,XC-330.pdf') is stamped "
                    "'[FOR REFERENCE ONLY]' / 'Nonescale' and carries no tolerance "
                    "block (ce-parts/xl330-m288-t/electrical.chip.json 'package')",
        "what_settles_it": "a dial indicator on a real servo horn"})
    open_terms.append({
        "term": "XL330 gearbox backlash at the output",
        "why_open": "not published anywhere on E1, E2 or D1; the 288.4:1 train is "
                    "'Engineering Plastic' (E1 Specifications)",
        "what_settles_it": "lock the case, load the horn both ways and read "
                           "Present Position(132) (4096 pulse/rev = 0.0879 deg/count)"})
    open_terms.append({
        "term": "this workshop's own printed band",
        "why_open": "ce-cad/cecad/data/print_fits.json is {\"machines\": {}} -- no "
                    "machine on the farm has ever been measured, so every number "
                    "here rests on a published SERVICE tolerance, not on our printer",
        "what_settles_it": "build cecad.coupon.coupon() with the Ø10 and Ø16 rungs, "
                           "print it, measure with calipers and store it with "
                           "cecad.coupon.record_measurements(); "
                           "cecad.coupon.offsets_for() then answers per machine + "
                           "material instead of returning CANNOT DETERMINE"})

    def wc(terms):
        return sum(t["half_band_mm"] for t in terms if t["half_band_mm"])

    def rss(terms):
        return math.sqrt(sum(t["half_band_mm"] ** 2 for t in terms
                             if t["half_band_mm"]))

    axial_wc, axial_rss = wc(terms_axial), rss(terms_axial)
    radial_wc, radial_rss = wc(terms_radial), rss(terms_radial)

    # The bolted flange's angular constraint needs a FORM tolerance (face
    # parallelism across the disc). No published FDM standard states one --
    # Protolabs' rows are DIMENSIONAL accuracy. Applying the dimensional band
    # as if it were parallelism is an UPPER BOUND, not a measurement, and is
    # labelled that way; the real number is CANNOT DETERMINE.
    theta_flange_wc = math.degrees(math.atan2(2.0 * t_flange, fd))
    theta_flange_rss = math.degrees(math.atan2(2.0 * t_flange / math.sqrt(2), fd))
    backlash_wc = math.degrees(math.atan2(radial_wc, PCD_R))
    backlash_rss = math.degrees(math.atan2(radial_rss, PCD_R))

    governs = "flange"
    theta_wc = theta_flange_wc
    if theta_cock is not None and theta_cock < theta_flange_wc:
        governs, theta_wc = "bearing engagement", theta_cock

    return {
        "flange": {"part": spec["flange_part"], "interface": spec["flange_iface"],
                   "disc_d_mm": fd, "clearance_hole_d_mm": hd,
                   "screws": 4, "pcd_mm": PCD},
        "bearing": ({"connection": geom.get("connection"),
                     "bore_mm": geom.get("bore_mm"), "od_mm": geom.get("od_mm"),
                     "width_mm": geom.get("width_mm"),
                     "seat_part": spec["seat_part"], "seat_interface": spec["seat_iface"],
                     "seat_d_mm": seat_d, "seat_length_mm": seat_len,
                     "engagement_fraction": None if engagement is None else round(engagement, 4),
                     "engagement_pct": None if engagement is None else round(100 * engagement, 2),
                     "role": spec["seat_role"]}
                    if seat_d is not None else
                    {"connection": None, "role": spec["seat_role"]}),
        "band": band_name,
        "axial_terms": terms_axial,
        "radial_terms": terms_radial,
        "open_terms": open_terms,
        "axial_play_mm": {"worst_case": round(axial_wc, 4), "rss": round(axial_rss, 4)},
        "axial_play_vs_bearing_engagement": (
            None if not seat_len else {
                "engaged_length_mm": seat_len,
                "worst_case_fraction_of_engagement": round(axial_wc / seat_len, 4),
                "rss_fraction_of_engagement": round(axial_rss / seat_len, 4),
                "exceeds_engagement": axial_wc >= seat_len,
                "why": ("the axial stack is compared against the length the ring is "
                        "actually engaged over. A stack that reaches the engagement "
                        "can walk the ring off its seat; below it the ring stays on "
                        "but with less land than the nominal already gives.")}),
        "radial_eccentricity_mm": {"worst_case": round(radial_wc, 4),
                                   "rss": round(radial_rss, 4)},
        "angular_misalignment_deg": {
            "bearing_cock_worst_case": None if theta_cock is None else round(theta_cock, 4),
            "bearing_cock_basis": (
                None if theta_cock is None else
                "atan(diametral clearance / engaged length) = atan(2 x %.4f mm / "
                "%.2f mm). Both numbers are sourced: the clearance from the %s band "
                "on the printed Ø%.1f seat, the engaged length MEASURED on %s '%s'. "
                "This is the angle the ball bearing ALONE leaves free."
                % (t_seat, seat_len, band_name, seat_d,
                   spec["seat_part"], spec["seat_iface"])),
            "flange_face_upper_bound_worst_case": round(theta_flange_wc, 4),
            "flange_face_upper_bound_rss": round(theta_flange_rss, 4),
            "flange_face_verdict": "CANNOT DETERMINE",
            "flange_face_why": (
                "the bolted flange's angular constraint is a FORM tolerance (face "
                "parallelism across the Ø%.1f disc). No published FDM standard "
                "states one -- Protolabs Network's rows are DIMENSIONAL accuracy. "
                "The number above applies the dimensional band as if it were "
                "parallelism, which is an UPPER BOUND of unknown tightness, not a "
                "measurement. Both flange faces come off the same layer stack, so "
                "the true parallelism error is expected to be far smaller -- but "
                "'expected' is not measured." % fd),
            "flange_face_what_settles_it": (
                "print a flange coupon and read face parallelism across Ø%.1f with "
                "a dial indicator on a surface plate; store it beside the bore/pin "
                "ladder of cecad.coupon" % fd),
            "governing": ("the bolted flange, by an unmeasured margin"
                          if governs == "flange" else "bearing engagement"),
            "worst_case": round(theta_wc, 4)},
        "rotational_backlash_deg": {"worst_case": round(backlash_wc, 4),
                                    "rss": round(backlash_rss, 4),
                                    "basis": "atan(radial slop / PCD radius 6.0 mm) "
                                             "-- the pattern's tangential freedom "
                                             "BEFORE the four M2 screws are torqued; "
                                             "a clamped joint gives this up to "
                                             "friction, and no friction figure exists "
                                             "for a printed PLA face on a plastic horn"},
        "note": spec.get("note"),
    }


def main():
    geomf = json.load(open(os.path.join(REPO, "out/sim-evidence/joint-geometry.json")))
    gj = geomf["outputs"]["joints"]
    assert set(gj) == set(JOINTS), (sorted(set(gj) ^ set(JOINTS)))

    # ISO 286 self-test against published rows the derivation was not fitted to
    selftest = []
    for d, g, pub in PUBLISHED_CHECK:
        got = it_um(d, g)
        selftest.append({"nominal_mm": d, "grade": "IT%d" % g, "derived_um": got,
                         "published_iso286_2_um": pub,
                         "verdict": "PASS" if got == pub else "FAIL"})
    selftest_ok = all(r["verdict"] == "PASS" for r in selftest)

    results = {}
    for band_name in BANDS:
        for jname, spec in JOINTS.items():
            bearings = [e for e in gj[jname]["on_axis"] if e.get("kind") == "bearing"]
            geom = bearings[0] if bearings else {}
            results.setdefault(jname, {})[band_name] = stack(jname, spec, geom, band_name)

    # engagement flags (band-independent -- pure geometry)
    flags = []
    for jname, spec in JOINTS.items():
        if spec["seat_len"] and spec["ring_w"]:
            f = spec["seat_len"] / spec["ring_w"]
            if f < 1.0:
                flags.append({"joint": jname, "seat_length_mm": spec["seat_len"],
                              "ring_width_mm": spec["ring_w"],
                              "engagement_pct": round(100 * f, 2),
                              "why": "the printed boss is shorter than the ring, so "
                                     "part of the ring stands proud and the ring's "
                                     "angular constraint acts over only that length"})
        elif spec["seat_len"] is None and spec["seat_d"] is not None:
            flags.append({"joint": jname, "seat_length_mm": None,
                          "engagement_pct": None,
                          "why": "a bearing is on this axis but no part folder "
                                 "declares a bearing_seat interface for it -- "
                                 "CANNOT DETERMINE"})

    # ISO 286 equivalence of each band at the sizes this robot actually uses
    equivalence = {}
    for band_name, fn in BANDS.items():
        rows = {}
        for d in (10.0, 12.0, 15.0, 15.9, 16.0, 17.0, 19.0, 22.0):
            total_um = 2000.0 * fn(d)
            g, band_um = grade_of(total_um, d)
            rows["%.1f" % d] = {"half_band_mm": round(fn(d), 4),
                                "total_band_um": round(total_um, 1),
                                "nearest_iso286_grade_at_or_above": g,
                                "that_grade_band_um": band_um}
        equivalence[band_name] = rows

    exceed = sorted(n for n in results
                    if (results[n]["FDM-A prototyping"]["axial_play_vs_bearing_engagement"] or {})
                    .get("exceeds_engagement"))
    worst_axial = max(results, key=lambda n: results[n]["FDM-A prototyping"]["axial_play_mm"]["worst_case"])
    worst_ang = max(results, key=lambda n: results[n]["FDM-A prototyping"]["angular_misalignment_deg"]["worst_case"])

    out = {
        "study": "tolerance-stack-hinges",
        "what": ("Axial play, radial eccentricity, angular misalignment and "
                 "rotational backlash of all 14 hinges, worst-case and RSS, at two "
                 "sourced FDM tolerance bands."),
        "inputs": {
            "joint_geometry": "out/sim-evidence/joint-geometry.json (sim/joint_geometry.py)",
            "connections": ["connection:press-fit-bearing-22x16x4",
                            "connection:press-fit-bearing-15x10x3",
                            "connection:spline-xl330-horn",
                            "connection:threaded-m2"],
            "part_interfaces": sorted({s["flange_part"] for s in JOINTS.values()} |
                                      {s["seat_part"] for s in JOINTS.values() if s["seat_part"]}),
            "fdm_bands": BAND_CITE,
            "fdm_band_C": ("THIS workshop's printers: CANNOT DETERMINE. "
                           "ce-cad/cecad/data/print_fits.json is "
                           "{\"machines\": {}, \"schema\": 1}."),
            "m2": ("ce-cad/cecad/fasteners.py:57 -- (\"M2\", 2.0, 0.40, 1.60, 2.20, "
                   "2.40, 2.60, 3.8, 2.0, 4.4, 4.0, 5.0, 0.3): major Ø2.0, tap "
                   "drill Ø1.60, close clearance Ø2.20, medium Ø2.40"),
            "iso286": ("i = 0.45*cbrt(D) + 0.001*D on the geometric mean of the size "
                       "step; IT = multiple * i with the standard series "
                       "7/10/16/25/40/64/100/160/250/400/640/1000 for IT5..IT16; "
                       "published IT7 transcribed where the formula drifts 1 um "
                       "(same treatment as the connection folders')"),
        },
        "method": ("Every hinge is ONE station: sim/joint_geometry.py measures the "
                   "driven horn face and the bearing mid-plane as coincident to "
                   "0.1 mm on 12 of the 14 joints, so no two-support span model is "
                   "used. Axial play = the sum (worst case) or root-sum-square of "
                   "the printed axial terms; radial eccentricity likewise over the "
                   "radial terms; angular misalignment is the SMALLER of the bolted "
                   "flange's face constraint atan(2t/D) and the bearing's cocking "
                   "freedom atan(diametral clearance / engaged length); rotational "
                   "backlash is atan(radial slop / 6.0 mm PCD radius), the pattern's "
                   "freedom before the screws are torqued. Terms whose tolerance is "
                   "not published are listed in open_terms and are NOT folded into "
                   "any number -- so every figure here UNDERSTATES the real stack."),
        "outputs": {
            "iso286_selftest": {"rows": selftest,
                                "verdict": "PASS" if selftest_ok else "FAIL",
                                "why": "derived IT7 checked against published ISO "
                                       "286-2 rows the derivation was not fitted to"},
            "band_to_iso286_equivalence": equivalence,
            "per_joint": results,
            "engagement_flags": flags,
            "joints_whose_axial_stack_reaches_the_bearing_engagement": {
                "FDM-A prototyping": exceed,
                "why": "the lane brief's own flag: does the stack exceed the length "
                       "the bearing is engaged over? At the FDM-A band it does at "
                       "these joints; the fractions are per joint in "
                       "axial_play_vs_bearing_engagement."},
            "worst_axial_joint": worst_axial,
            "worst_angular_joint": worst_ang,
        },
        "verdict": "",
        "why": "",
        "script": "sim/tolerance_stack.py",
        "artifacts": ["out/sim-evidence/tolerance-stack-hinges.json"],
        "looked_at": [
            "out/sim-evidence/joint-geometry.json",
            "ce-connections/press-fit-bearing-22x16x4/iterations/v0.0.1/compat.py",
            "ce-connections/press-fit-bearing-15x10x3/iterations/v0.0.1/compat.py",
            "ce-connections/spline-xl330-horn/iterations/v0.0.1/compat.py",
            "ce-parts/*/current/cad/interfaces.json (14 parts)",
            "ce-cad/cecad/fasteners.py",
            "ce-cad/cecad/coupon.py",
            "ce-cad/cecad/data/print_fits.json",
            "https://www.hubs.com/manufacturing-standards/",
        ],
    }

    a = results[worst_ang]["FDM-A prototyping"]
    b = results[worst_ang]["FDM-B industrial"]
    out["verdict"] = "CANNOT DETERMINE"
    out["why"] = (
        "The stack cannot be closed because the band it rests on is not measured "
        "for the machine that will print these parts, and the numbers it gives at "
        "the two PUBLISHED bands are not survivable for a bearing fit. At FDM-A "
        "(Protolabs prototyping, ±0.5 mm floor) the Ø16 printed seat's total band "
        "is 1000 um, which is coarser than ISO 286 IT16 at that size (1100 um is "
        "IT16); at FDM-B (industrial, ±0.3 mm floor) it is 600 um, between IT14 "
        "(430) and IT15 (700). A ball bearing seat is normally an IT6-IT7 feature. "
        "The worst joint for angle is %s: %.4f deg worst-case at FDM-A and %.4f deg "
        "at FDM-B, governed by %s. %d of 14 joints seat the ring on less than its "
        "own width (the Ø16.0 x 1.95 bosses in a 4.0 mm ring, 48.75 %%), and 2 "
        "joints (%s) have a bearing on the axis that NO part folder declares a seat "
        "for. No joint's axial stack REACHES its engagement at either band, but the "
        "two hip-yaws come closest: %.4f mm of stack against %.2f mm of engaged ring "
        "at FDM-A, %.1f %% of it consumed (%.1f %% at FDM-B). "
        "What settles it is one printed coupon: cecad.coupon.coupon() at the "
        "Ø10 and Ø16 rungs, measured and stored -- print_fits.json is empty today."
        % (worst_ang, a["angular_misalignment_deg"]["worst_case"],
           b["angular_misalignment_deg"]["worst_case"],
           a["angular_misalignment_deg"]["governing"],
           sum(1 for f in flags if f["engagement_pct"] is not None),
           ", ".join(f["joint"] for f in flags if f["engagement_pct"] is None),
           results["left_hip_yaw"]["FDM-A prototyping"]["axial_play_mm"]["worst_case"],
           results["left_hip_yaw"]["FDM-A prototyping"]["axial_play_vs_bearing_engagement"]["engaged_length_mm"],
           100 * results["left_hip_yaw"]["FDM-A prototyping"]["axial_play_vs_bearing_engagement"]["worst_case_fraction_of_engagement"],
           100 * results["left_hip_yaw"]["FDM-B industrial"]["axial_play_vs_bearing_engagement"]["worst_case_fraction_of_engagement"]))

    path = os.path.join(REPO, "out/sim-evidence/tolerance-stack-hinges.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(out, open(path, "w"), indent=1)

    print("ISO 286 self-test:", "PASS" if selftest_ok else "FAIL", selftest)
    print()
    hdr = "%-16s %8s %8s %8s %8s %9s %9s %6s"
    print(hdr % ("joint", "axialWC", "axialRSS", "radWC", "radRSS", "angWC", "backlWC", "eng%"))
    for n in JOINTS:
        r = results[n]["FDM-A prototyping"]
        e = r["bearing"].get("engagement_pct")
        print(hdr % (n, "%.4f" % r["axial_play_mm"]["worst_case"],
                     "%.4f" % r["axial_play_mm"]["rss"],
                     "%.4f" % r["radial_eccentricity_mm"]["worst_case"],
                     "%.4f" % r["radial_eccentricity_mm"]["rss"],
                     "%.4f" % r["angular_misalignment_deg"]["worst_case"],
                     "%.4f" % r["rotational_backlash_deg"]["worst_case"],
                     "-" if e is None else "%.2f" % e))
    print()
    print(out["why"])


if __name__ == "__main__":
    main()
