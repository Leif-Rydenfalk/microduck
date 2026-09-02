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
the bearing's bore support lets the boss cock in the bore.  Which of the two
governs is computed, not assumed.

CORRECTION, 2026-09-02 (this version).  The first version of this study divided
the printed boss length by the ring width and called the answer "engagement" --
48.75 % on the four Ø16 x 1.95 seats -- and reported "7 of 14 joints seat the
ring on less than its own width" as a FAIL.  That is wrong, and the file the
study itself listed in looked_at says so verbatim:
ce-parts/microduck-yaw2roll/current/cad/interfaces.json 'yaw_bearing_seat' --
"the bearing mesh spans 0..4 along its own axis, so it occupies z 12.5..16.5
here - the upper 2.05 mm of its bore rides the horn's Ø16 x 3 boss."  The bore
is carried by TWO parts.  horn_bore_share() below measures the split off
joint-geometry.json at every joint and cross-checks it against the seat length
the part folder declares; support is 4.000 of 4.000 mm, not 1.95.  Three
consequences, all corrected here:
  * the engagement FAIL is withdrawn (the flags now carry both fractions);
  * bearing_cock is computed over the SUPPORTED length, not the printed boss;
  * the clearance is ONE band, not two -- a +/-t shaft in a bore held at
    nominal gives t of diametral clearance, and the steel bore's own tolerance
    stays an open term instead of being silently assumed equal and opposite.
  * and the risk that IS real at those joints -- the coaxiality STEP between
    the printed boss and the horn boss that share one bore -- is now computed.

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
  FDM-D  a MEASURED print-accuracy study, which is the alternative the lane
         brief allowed: Wei et al. (2025), Polymers 17(3):416,
         doi 10.3390/polym17030416, archived at
         research/fetched/wei2025-polymers-17-416-gear-accuracy.html.
         "deviations for large and pinion gears ranging between -0.045 and
         0.060 mm, and -0.150 and 0.078 mm" on a MakerBot Replicator 2X in
         PLA, CMM-measured, the authors grading their own features
         "within the IT09-IT11 range".  Half-band 0.150 mm.  NOT our printer
         and NOT our part -- it does not set the verdict, it bounds what a
         tuned FDM machine has been shown to do.
  ISO286 PUBLISHED, not derived and not recalled: ISO 286-1:2010(E) standard
         tolerance grades read off the archived table
         research/fetched/engineersedge-iso286-1-it-grades.html.  The
         0.45*cbrt(D)+0.001*D derivation the connection folders carry is kept
         only as a SELF-TEST against those rows, across IT5..IT16 -- the first
         version validated IT7 alone and then graded printed bands at IT14-16
         with an unchecked formula.

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
# ISO 286-1:2010(E) standard tolerance grades, TRANSCRIBED from the archived
# copy of the published table, not derived and not recalled:
#   research/fetched/engineersedge-iso286-1-it-grades.html
#   https://www.engineersedge.com/international_tol.htm  (fetched 2026-09-02,
#   sha256 in research/fetched/PROVENANCE.json).  The page's own reference
#   line, verbatim: "ISO - International Organization for Standardization
#   ISO 286-1 - 2010(E)".  IT12..IT16 are printed there in mm; they are stored
#   here in um so every grade is one unit.
# The 0.45*cbrt(D)+0.001*D derivation the connection folders carry is KEPT, but
# demoted to a self-test against these published rows (it drifts by up to 4 %
# at IT16 and the published row wins).
# --------------------------------------------------------------------------
SIZE_STEPS = [(0.0, 3.0), (3.0, 6.0), (6.0, 10.0), (10.0, 18.0), (18.0, 30.0),
              (30.0, 50.0), (50.0, 80.0), (80.0, 120.0), (120.0, 180.0)]
IT_MULTIPLE = {5: 7, 6: 10, 7: 16, 8: 25, 9: 40, 10: 64, 11: 100,
               12: 160, 13: 250, 14: 400, 15: 640, 16: 1000}
# published ISO 286-1:2010(E) rows, um, in SIZE_STEPS order
PUBLISHED_IT_UM = {
    5:  [4, 5, 6, 8, 9, 11, 13, 15, 18],
    6:  [6, 8, 9, 11, 13, 16, 19, 22, 25],
    7:  [10, 12, 15, 18, 21, 25, 30, 35, 40],
    8:  [14, 18, 22, 27, 33, 39, 46, 54, 63],
    9:  [25, 30, 36, 43, 52, 62, 74, 87, 100],
    10: [40, 48, 58, 70, 84, 100, 120, 140, 160],
    11: [60, 75, 90, 110, 130, 160, 190, 220, 250],
    12: [100, 120, 150, 180, 210, 250, 300, 350, 400],
    13: [140, 180, 220, 270, 330, 390, 460, 540, 630],
    14: [250, 300, 360, 430, 520, 620, 740, 870, 1000],
    15: [400, 480, 580, 700, 840, 1000, 1200, 1400, 1600],
    16: [600, 750, 900, 1100, 1300, 1600, 1900, 2200, 2500],
}
PUBLISHED_QUOTE = ("ISO 286-1:2010(E) Standard Tolerance Grades, as printed on "
                   "https://www.engineersedge.com/international_tol.htm and archived "
                   "at research/fetched/engineersedge-iso286-1-it-grades.html. Row "
                   "'10 18' reads IT6 11, IT7 18, IT8 27, IT9 43, IT10 70, IT11 110 "
                   "(um) and IT12 0,18 IT13 0,27 IT14 0,43 IT15 0,7 IT16 1,1 (mm). "
                   "Row '6 10' reads IT7 15 ... IT16 0,9 mm.")


def size_step(d):
    for lo, hi in SIZE_STEPS:
        if lo < d <= hi:
            return lo, hi
    raise ValueError("%r mm is outside the ISO 286 size steps carried here" % d)


def step_index(d):
    lo, hi = size_step(d)
    return SIZE_STEPS.index((lo, hi))


def it_um(d, grade):
    """The PUBLISHED ISO 286-1:2010(E) band, um. No formula."""
    return PUBLISHED_IT_UM[grade][step_index(d)]


def it_um_derived(d, grade):
    """The 0.45*cbrt(D)+0.001*D derivation, kept only to be checked against the
    published rows above."""
    lo, hi = size_step(d)
    d_geo = math.sqrt(lo * hi) if lo > 0 else hi
    i_um = 0.45 * d_geo ** (1.0 / 3.0) + 0.001 * d_geo
    return int(math.floor(IT_MULTIPLE[grade] * i_um + 0.5))


def grade_of(total_band_um, d):
    """The finest published IT grade whose band is >= the given total band, i.e.
    what ISO 286 grade this printed feature would be if it were a machined one."""
    for g in sorted(PUBLISHED_IT_UM):
        if it_um(d, g) >= total_band_um:
            return "IT%d" % g, it_um(d, g)
    return "coarser than IT16", it_um(d, 16)


# --------------------------------------------------------------------------
# the sourced FDM bands: half-band (+/-) in mm for a nominal d
# --------------------------------------------------------------------------
BANDS = {
    "FDM-A prototyping": lambda d: max(0.005 * d, 0.5),
    "FDM-B industrial": lambda d: max(0.003 * d, 0.3),
    "FDM-D measured study": lambda d: 0.150,
}
BAND_CITE = {
    "FDM-A prototyping": ("Protolabs Network manufacturing standards, Prototyping "
                          "FDM, verbatim: '± 0.5% with a lower limit of ± 0.5 mm "
                          "(± 0.02\")'. https://www.hubs.com/manufacturing-standards/ "
                          ", read 2026-09-02, ARCHIVED at "
                          "research/fetched/hubs-manufacturing-standards.html "
                          "(324055 bytes, sha256 954ac49106f245819b9bcb1c2365f0e0d6d"
                          "2110e4f33cbab68f0f8fe86716d8a) so it can be re-read offline."),
    "FDM-B industrial": ("Same page, same archived file, Industrial FDM, verbatim: "
                         "'± 0.3% with a lower limit: ± 0.3 mm (±0.012\" in)'."),
    "FDM-D measured study": (
        "NOT a service tolerance: a MEASURED band from a published print-accuracy "
        "study, which is what the lane brief asked for as the alternative to a "
        "vendor spec. Wei, Zhang, Sun, Zhao, Sun, Yu, Zhou & Li (2025), 'Geometric "
        "Accuracy and Dimensional Precision in 3D Printing-Based Gear Manufacturing: "
        "A Study on Interchangeability and Forming Precision', Polymers 17(3):416, "
        "doi 10.3390/polym17030416. Archived at "
        "research/fetched/wei2025-polymers-17-416-gear-accuracy.html (206065 bytes, "
        "sha256 f1366277e1efaf4f55733764feb58a15a24d840f4fa1a3a1a38291a0a047777b). "
        "Abstract, verbatim: 'deviations for large and pinion gears ranging between "
        "-0.045 and 0.060 mm, and -0.150 and 0.078 mm, respectively'. The widest "
        "single-sided deviation on the small (pinion) features, 0.150 mm, is used as "
        "the half-band, flat in mm -- our features are small ones. Machine and "
        "material, verbatim: 'The FDM process was performed using the MakerBot(R) "
        "Replicator(TM) 2X 3D printer' with 'Polylactic acid (PLA) polymer (model: "
        "6252D...)', measured on a CMM. The authors' own ISO grading of their parts, "
        "verbatim: 'all geometric feature tolerances fell within the IT09-IT11 "
        "range'. THIS IS NOT OUR PRINTER AND NOT OUR PART: it is evidence of what a "
        "tuned FDM machine achieved on a benchmark, carried here so the two service "
        "bands are not the only evidence in the study. It does NOT set the verdict."),
}
GOVERNING_BANDS = ["FDM-A prototyping", "FDM-B industrial"]   # the two SERVICE bands

M2_MAJOR = 2.0          # fasteners.py:57
PCD = 12.0              # spline-xl330-horn: 4 holes on Ø12.0
PCD_R = PCD / 2.0
# connection:spline-xl330-horn, cad/mate.py:43-44 and compat.py:51-52 --
# DISC_D_MM = 16.0, DISC_L_MM = 3.0, measured off Pollen's xl330.stl by
# cecad.meshfeatures. The servo's own horn disc is Ø16.0 x 3.0.
HORN_DISC_D = 16.0
HORN_DISC_L = 3.0

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


def horn_bore_share(spec, on_axis):
    """MEASURE how much of the bearing's bore rides the SERVO's own Ø16.0 x 3.0
    horn disc instead of the printed boss.

    Why this exists: ce-parts/microduck-yaw2roll/current/cad/interfaces.json
    'yaw_bearing_seat' says it verbatim -- "the bearing mesh spans 0..4 along its
    own axis, so it occupies z 12.5..16.5 here - the upper 2.05 mm of its bore
    rides the horn's Ø16 x 3 boss."  A study that divides the printed boss length
    by the ring width alone reports HALF the support the ring actually has.

    Measured, not assumed, from out/sim-evidence/joint-geometry.json:
      * the bearing's own span along the joint axis (span_axial_mm),
      * the DRIVING servo's two disc faces (disc_face_axial_mm) and its body
        centre (axial_mm), which give the direction the Ø16 x 3.0 disc extends,
      * the overlap of that disc with the bearing bore.
    The printed remainder is then cross-checked against the seat length the part
    folder declares; a disagreement over 0.1 mm makes the share CANNOT DETERMINE.
    """
    ring_w = spec.get("ring_w")
    seat_len = spec.get("seat_len")
    if not ring_w or not seat_len or seat_len >= ring_w:
        return None
    drivers = [e for e in on_axis
               if e.get("kind") == "servo" and e.get("drives_this_joint")]
    bearings = [e for e in on_axis
                if e.get("kind") == "bearing" and e.get("span_axial_mm")
                and abs((e.get("width_mm") or 0) - ring_w) < 1e-6]
    for drv in drivers:
        faces = drv.get("disc_face_axial_mm") or []
        centre = drv.get("axial_mm")
        for b in bearings:
            s0, s1 = sorted(float(v) for v in b["span_axial_mm"])
            for f in (float(v) for v in faces):
                if not (s0 - 1e-9 <= f <= s1 + 1e-9):
                    continue
                direction = 1.0 if centre is not None and centre > f else -1.0
                h0, h1 = sorted((f, f + direction * HORN_DISC_L))
                overlap = max(0.0, min(s1, h1) - max(s0, h0))
                printed_measured = (s1 - s0) - overlap
                agrees = abs(printed_measured - seat_len) <= 0.1
                return {
                    "bearing_span_axial_mm": [round(s0, 4), round(s1, 4)],
                    "driving_servo_disc_faces_axial_mm": [round(float(v), 4) for v in faces],
                    "driving_servo_body_centre_axial_mm": (
                        None if centre is None else round(float(centre), 4)),
                    "horn_disc_d_mm": HORN_DISC_D,
                    "horn_disc_l_mm": HORN_DISC_L,
                    "horn_disc_span_axial_mm": [round(h0, 4), round(h1, 4)],
                    "horn_share_of_bore_mm": round(overlap, 4),
                    "printed_share_of_bore_mm_measured": round(printed_measured, 4),
                    "printed_seat_length_declared_mm": seat_len,
                    "cross_check": ("PASS: the measured printed remainder %.4f mm "
                                    "agrees with the seat length %s '%s' declares "
                                    "(%.4f mm) to %.4f mm"
                                    % (printed_measured, spec["seat_part"],
                                       spec["seat_iface"], seat_len,
                                       abs(printed_measured - seat_len))
                                    if agrees else
                                    "CANNOT DETERMINE: the measured printed remainder "
                                    "%.4f mm disagrees with the declared seat length "
                                    "%.4f mm by %.4f mm"
                                    % (printed_measured, seat_len,
                                       abs(printed_measured - seat_len))),
                    "verdict": "PASS" if agrees else "CANNOT DETERMINE",
                    "source_quote": (
                        "ce-parts/microduck-yaw2roll/current/cad/interfaces.json "
                        "'yaw_bearing_seat', verbatim: 'the bearing mesh spans 0..4 "
                        "along its own axis, so it occupies z 12.5..16.5 here - the "
                        "upper 2.05 mm of its bore rides the horn's Ø16 x 3 boss.' "
                        "Horn disc Ø16.0 x 3.0 from connection:spline-xl330-horn "
                        "(cad/mate.py:43-44 DISC_D_MM/DISC_L_MM, measured off "
                        "xl330.stl by cecad.meshfeatures)."),
                }
    return None


def stack(name, spec, geom, band_name, share):
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
    theta_cock_printed_only = None
    supported = None
    c = None
    t_seat = None
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
            # DIAMETRAL clearance the PRINTED band alone can open up.  A +/-t
            # band on a printed Ø_d shaft against a bore held at its nominal Ø_d
            # leaves at most t of DIAMETRAL clearance (shaft at its lower limit).
            # It is NOT 2t: 2t would be the shaft band added to an equal and
            # opposite band on the bore, and the steel ring's own bore tolerance
            # is an OPEN TERM in this study (no designation, no vendor sheet), so
            # it is left open rather than silently set to +/-t.
            c = t_seat
            # The bore is supported over the printed boss PLUS whatever of it
            # rides the servo's own Ø16 x 3 horn disc -- measured per joint.
            supported = seat_len + (share["horn_share_of_bore_mm"] if share else 0.0)
            theta_cock = math.degrees(math.atan2(c, supported))
            theta_cock_printed_only = math.degrees(math.atan2(c, seat_len))
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
        governs, theta_wc = "bearing bore support", theta_cock

    # ---- the COAXIALITY STEP between the two bosses that share the bore ----
    # When the ring's bore is carried partly by the printed boss and partly by
    # the servo's own horn disc, the thing that can bind or preload it is not
    # the length of either boss but how far their axes are apart.  Two sourced
    # terms and one bounded one:
    coax = None
    if share:
        step_terms = [
            {"term": "M2 screw clearance in the printed flange",
             "radial_mm": round(dr_bolt, 4), "kind": "deterministic",
             "source": "(%.2f - %.2f)/2 -- clearance hole Ø off %s '%s', M2 major "
                       "Ø2.0 off ce-cad/cecad/fasteners.py:57. This is how far the "
                       "printed part can slide on the horn before the screws bear."
                       % (hd, M2_MAJOR, spec["flange_part"], spec["flange_iface"])},
            {"term": "printed position of the boss relative to its own bolt circle",
             "radial_mm": round(t_seat, 4), "kind": "UPPER BOUND, not a measurement",
             "source": "no published FDM standard states a POSITIONAL tolerance -- "
                       "Protolabs Network's rows are DIMENSIONAL accuracy. The %s "
                       "dimensional half-band at Ø%.1f is applied here as if it were "
                       "position, which bounds it above by an unknown margin."
                       % (band_name, seat_d)},
        ]
        step_wc = sum(t["radial_mm"] for t in step_terms)
        coax = {
            "what": ("the radial STEP between the printed Ø%.1f boss and the servo's "
                     "Ø%.1f horn disc, which together carry one %.1f mm bore"
                     % (seat_d, HORN_DISC_D, ring_w)),
            "terms": step_terms,
            "worst_case_mm": round(step_wc, 4),
            "rss_mm": round(math.sqrt(sum(t["radial_mm"] ** 2 for t in step_terms)), 4),
            "available_radial_clearance_mm": round(c / 2.0, 4),
            "step_over_available_clearance": round(step_wc / (c / 2.0), 4),
            "binds": step_wc > c / 2.0,
            "consequence": (
                "a step larger than the ring's radial clearance cannot be taken up by "
                "the clearance: the ring is forced onto both bosses at once, which "
                "preloads the balls, raises the running torque and puts a bending "
                "moment into the printed boss. A step smaller than the clearance is "
                "simply taken up and the ring rides on whichever boss it touches."),
            "verdict": "CANNOT DETERMINE",
            "why": ("the second term is a bound, not a measurement (no published FDM "
                    "positional tolerance exists), and the ring's own radial internal "
                    "clearance is an open term -- the reference names the bearing only "
                    "'seeed_bearing'. Both would have to be measured before this step "
                    "can be graded PASS or FAIL. This is the real risk at these joints, "
                    "and it is NOT the 'short engagement' the first version of this "
                    "study reported."),
            "what_settles_it": (
                "print one bracket, put it on a real XL330 horn, and read the runout of "
                "the printed boss against the horn boss with a dial indicator on the "
                "assembled pair; and micrometer the ring's bore and both bosses."),
        }

    return {
        "flange": {"part": spec["flange_part"], "interface": spec["flange_iface"],
                   "disc_d_mm": fd, "clearance_hole_d_mm": hd,
                   "screws": 4, "pcd_mm": PCD},
        "bearing": ({"connection": geom.get("connection"),
                     "bore_mm": geom.get("bore_mm"), "od_mm": geom.get("od_mm"),
                     "width_mm": geom.get("width_mm"),
                     "seat_part": spec["seat_part"], "seat_interface": spec["seat_iface"],
                     "seat_d_mm": seat_d, "seat_length_mm": seat_len,
                     "printed_seat_engagement_fraction":
                         None if engagement is None else round(engagement, 4),
                     "printed_seat_engagement_pct":
                         None if engagement is None else round(100 * engagement, 2),
                     "horn_disc_share_of_bore": share,
                     "total_bore_support_mm": None if supported is None else round(supported, 4),
                     "total_bore_support_pct": (
                         None if supported is None or not ring_w
                         else round(100.0 * supported / ring_w, 2)),
                     "support_basis": (
                         "printed boss + the servo's own Ø16.0 x 3.0 horn disc, both "
                         "measured. The printed-seat fraction alone is NOT the ring's "
                         "support and must not be read as one."
                         if share else
                         "the printed seat is the whole of the ring's support at this "
                         "joint (no servo horn disc lies inside the bore)"),
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
                "engaged_length_mm": round(supported, 4),
                "engaged_length_basis": ("printed boss %.2f mm + horn disc %.2f mm, "
                                         "both measured"
                                         % (seat_len, share["horn_share_of_bore_mm"]))
                                        if share else
                                        "the printed boss alone (%.2f mm); no horn "
                                        "disc lies inside this bore" % seat_len,
                "printed_boss_only_length_mm": seat_len,
                "worst_case_fraction_of_engagement": round(axial_wc / supported, 4),
                "rss_fraction_of_engagement": round(axial_rss / supported, 4),
                "exceeds_engagement": axial_wc >= supported,
                "worst_case_fraction_of_printed_boss_only": round(axial_wc / seat_len, 4),
                "exceeds_printed_boss_only": axial_wc >= seat_len,
                "why": ("the axial stack is compared against the length the ring is "
                        "actually supported over -- the printed boss PLUS the servo "
                        "horn disc that carries the rest of the same bore. A stack "
                        "that reaches the support can walk the ring off its seat; "
                        "below it the ring stays on but with less land than the "
                        "nominal already gives. The printed-boss-only figure is kept "
                        "beside it because that is the part WE print.")}),
        "radial_eccentricity_mm": {"worst_case": round(radial_wc, 4),
                                   "rss": round(radial_rss, 4)},
        "angular_misalignment_deg": {
            "bearing_cock_upper_bound": None if theta_cock is None else round(theta_cock, 4),
            "bearing_cock_verdict": None if theta_cock is None else "CANNOT DETERMINE",
            "bearing_cock_basis": (
                None if theta_cock is None else
                "UPPER BOUND: atan(diametral clearance / SUPPORTED length) = "
                "atan(%.4f mm / %.4f mm). The clearance is the %s half-band on the "
                "printed Ø%.1f seat -- ONE band, not two: a shaft %.4f mm under "
                "nominal in a bore AT nominal gives %.4f mm of diametral clearance, "
                "and the steel ring's own bore tolerance is an open term rather than "
                "an assumed equal-and-opposite band. The supported length is MEASURED: "
                "%s. This is an upper bound and not the joint's real freedom, because "
                "%.4f mm of that support is the servo's own horn disc, whose diameter "
                "tolerance ROBOTIS does not publish (drawing D1 is stamped '[FOR "
                "REFERENCE ONLY]'); if that disc is a snug fit the ring is located by "
                "it and the printed boss's slop does not reach the joint angle at all."
                % (c, supported, band_name, seat_d, t_seat, c,
                   ("printed boss %.4f mm + servo horn disc %.4f mm"
                    % (seat_len, share["horn_share_of_bore_mm"])) if share else
                   ("the printed boss alone, %.4f mm, off %s '%s'"
                    % (seat_len, spec["seat_part"], spec["seat_iface"])),
                   share["horn_share_of_bore_mm"] if share else 0.0)),
            "bearing_cock_if_horn_disc_were_absent": (
                None if theta_cock_printed_only is None else
                round(theta_cock_printed_only, 4)),
            "bearing_cock_if_horn_disc_were_absent_note": (
                None if not share else
                "atan(%.4f / %.4f) -- the same clearance over the PRINTED boss only. "
                "It is %.4f deg, %.2fx the real figure, and it is the number a study "
                "that forgets the horn disc reports. Kept here so the difference is "
                "visible rather than silently corrected."
                % (c, seat_len, theta_cock_printed_only,
                   theta_cock_printed_only / theta_cock)),
            "bearing_cock_what_settles_it": (
                None if theta_cock is None else
                "a micrometer on a real XL330 horn disc (its Ø and its runout) and on "
                "the ring's bore, plus the printed boss off a real print; then the "
                "clearance is measured on both bosses instead of bounded on one."),
            "coaxiality_step_between_the_two_bosses": coax,
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
                          if governs == "flange"
                          else "the bearing's bore support, by an unmeasured margin"),
            "worst_case": round(theta_wc, 4),
            "worst_case_meaning": ("the TIGHTER of the two upper bounds above. Both "
                                   "are bounds of unknown tightness -- one applies a "
                                   "dimensional band as parallelism, the other treats "
                                   "the servo horn disc as if it had the printed "
                                   "part's tolerance -- so this is the angle the joint "
                                   "is guaranteed NOT to exceed from these terms, not "
                                   "the angle it has.")},
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

    # ISO 286: the PUBLISHED rows are the input. The old cube-root derivation is
    # now the thing under test, and the test reports how far it drifts.
    selftest = []
    for d in (6.0, 10.0, 16.0, 22.0):
        for g in (5, 7, 9, 11, 14, 16):
            pub, der = it_um(d, g), it_um_derived(d, g)
            drift = 100.0 * (der - pub) / pub
            selftest.append({"nominal_mm": d, "grade": "IT%d" % g,
                             "published_iso286_1_um": pub, "derived_um": der,
                             "derivation_drift_pct": round(drift, 3),
                             "verdict": "PASS" if abs(drift) <= 10.0 else "FAIL"})
    selftest_ok = all(r["verdict"] == "PASS" for r in selftest)

    # the bore share: measured once per joint, band-independent (pure geometry)
    shares = {jname: horn_bore_share(spec, gj[jname]["on_axis"])
              for jname, spec in JOINTS.items()}

    results = {}
    for band_name in BANDS:
        for jname, spec in JOINTS.items():
            bearings = [e for e in gj[jname]["on_axis"] if e.get("kind") == "bearing"]
            geom = bearings[0] if bearings else {}
            results.setdefault(jname, {})[band_name] = stack(
                jname, spec, geom, band_name, shares[jname])

    # bore-support flags (band-independent -- pure geometry)
    flags = []
    for jname, spec in JOINTS.items():
        sh = shares[jname]
        if spec["seat_len"] and spec["ring_w"]:
            f = spec["seat_len"] / spec["ring_w"]
            total = spec["seat_len"] + (sh["horn_share_of_bore_mm"] if sh else 0.0)
            tf = total / spec["ring_w"]
            if f < 1.0:
                flags.append({
                    "joint": jname,
                    "ring_width_mm": spec["ring_w"],
                    "printed_seat_length_mm": spec["seat_len"],
                    "printed_seat_engagement_pct": round(100 * f, 2),
                    "horn_disc_share_mm": None if not sh else sh["horn_share_of_bore_mm"],
                    "total_bore_support_mm": round(total, 4),
                    "total_bore_support_pct": round(100 * tf, 2),
                    "residual_unsupported_mm": round(spec["ring_w"] - total, 4),
                    "residual_note": (
                        None if not sh else
                        "the %.4f mm residual is the difference between the %.4f mm "
                        "seat the part folder declares and the %.4f mm the servo "
                        "placement in joint-geometry.json measures for the same boss. "
                        "It is BELOW the resolution of the decimated xl330 mesh those "
                        "placements come from, so whether the last %.4f mm of ring is "
                        "carried cannot be told from these meshes -- it is not a "
                        "measured gap."
                        % (spec["ring_w"] - total, spec["seat_len"],
                           sh["printed_share_of_bore_mm_measured"],
                           spec["ring_w"] - total)),
                    "verdict": "PASS" if tf >= 0.999 else (
                        "FAIL" if not sh else "CANNOT DETERMINE"),
                    "why": ("the printed boss is shorter than the ring, but the rest "
                            "of the SAME bore rides the servo's own Ø16.0 x 3.0 horn "
                            "disc -- measured, %s. Support is %.4f of %.2f mm "
                            "(%.2f %%), not the %.2f %% the printed boss alone gives. "
                            "The concern at this joint is therefore the COAXIALITY "
                            "STEP between the two bosses, not the length of either."
                            % (sh["cross_check"], total, spec["ring_w"],
                               100 * tf, 100 * f))
                           if sh else
                           ("the printed boss is shorter than the ring and NO servo "
                            "horn disc lies inside this bore, so part of the ring "
                            "stands proud and its angular constraint acts over only "
                            "%.2f mm of %.2f mm." % (spec["seat_len"], spec["ring_w"]))})
        elif spec["seat_len"] is None and spec["seat_d"] is not None:
            flags.append({"joint": jname, "printed_seat_length_mm": None,
                          "printed_seat_engagement_pct": None,
                          "total_bore_support_pct": None,
                          "verdict": "CANNOT DETERMINE",
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

    exceed = {}
    for band_name in BANDS:
        exceed[band_name] = sorted(
            n for n in results
            if (results[n][band_name]["axial_play_vs_bearing_engagement"] or {})
            .get("exceeds_engagement"))
    exceed["why"] = (
        "the lane brief's own flag: does the axial stack exceed the length the ring "
        "is supported over? Every band has its own list and every list is written out "
        "even when it is empty -- an empty list means NO joint's stack reaches its "
        "support at that band, which is the case at all three bands here. The "
        "per-joint fractions are in axial_play_vs_bearing_engagement, together with "
        "the same comparison against the printed boss alone.")
    exceed["printed_boss_only"] = {
        band_name: sorted(
            n for n in results
            if (results[n][band_name]["axial_play_vs_bearing_engagement"] or {})
            .get("exceeds_printed_boss_only"))
        for band_name in BANDS}
    worst_axial = max(results, key=lambda n: results[n]["FDM-A prototyping"]["axial_play_mm"]["worst_case"])
    worst_ang = max(results, key=lambda n: results[n]["FDM-A prototyping"]["angular_misalignment_deg"]["worst_case"])
    coax_binding = {
        band_name: sorted(
            n for n in results
            if (results[n][band_name]["angular_misalignment_deg"]
                .get("coaxiality_step_between_the_two_bosses") or {}).get("binds"))
        for band_name in BANDS}

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
            "iso286": PUBLISHED_QUOTE,
            "iso286_archive": ("research/fetched/engineersedge-iso286-1-it-grades.html "
                               "(58811 bytes, sha256 in research/fetched/PROVENANCE.json); "
                               "the page's own reference line reads 'ISO - International "
                               "Organization for Standardization ISO 286-1 - 2010(E)'. "
                               "Every IT band used in this study is READ OFF that table. "
                               "The cube-root derivation the connection folders carry is "
                               "kept only as a self-test against it."),
            "fdm_band_D_search_record": (
                "The lane brief named 'Bambu H2S/PLA spec' first -- this farm's own "
                "printers. SEARCHED 2026-09-02: bambulab.com/en-us/h2s and "
                "us.store.bambulab.com/products/h2s are behind Cloudflare and refuse a "
                "direct fetch (the archived research/fetched/bambulab-h2s.html is the "
                "'Just a moment...' challenge page, 5761 bytes, sha256 "
                "a741d9af38e1b67026751cf3205fd2ce8a18e85feee57cbb408110a8cfa5738c -- "
                "kept as the record of the attempt, NOT as a source); "
                "wiki.bambulab.com/en/h2s/manual/h2s-specifications returns 'Page Not "
                "Found'. What Bambu does publish for the H2S is MOTION accuracy -- "
                "'distance-independent motion accuracy under 50 um' WITH the optional "
                "Vision Encoder, plus 'Auto Hole/Contour Compensation' and 0.3 mm "
                "preview alignment. None of those is a part dimensional tolerance: "
                "motion accuracy is the machine's positioning, not the printed feature's "
                "size after shrinkage and die swell. Bambu states NO part dimensional "
                "tolerance, so FDM-C stays CANNOT DETERMINE and the published measured "
                "study (FDM-D) is carried in its place."),
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
            "iso286_selftest": {
                "rows": selftest,
                "verdict": "PASS" if selftest_ok else "FAIL",
                "what_is_under_test": (
                    "the PUBLISHED ISO 286-1:2010(E) rows are now the input to every "
                    "grading in this study (see inputs.iso286). What is checked here "
                    "is the 0.45*cbrt(D)+0.001*D DERIVATION the connection folders "
                    "carry, across IT5..IT16 at the four sizes this robot uses, "
                    "against those published rows. It passes within 10 % everywhere "
                    "and is not used for any number in this study. The earlier "
                    "version of this study validated IT7 ONLY and then graded printed "
                    "bands at IT14-IT16 with an unchecked formula; that is fixed."),
            },
            "band_to_iso286_equivalence": equivalence,
            "per_joint": results,
            "bearing_bore_support_flags": flags,
            "joints_whose_axial_stack_reaches_the_bearing_support": exceed,
            "joints_where_the_coaxiality_step_exceeds_the_radial_clearance": {
                **coax_binding,
                "why": ("the step between the printed boss and the servo horn disc "
                        "that share one bore, against the radial clearance available "
                        "to take it up. Where it binds, the ring is forced onto both "
                        "bosses. Both terms carry bounds rather than measurements, so "
                        "the per-joint verdict is CANNOT DETERMINE, not FAIL."),
            },
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
            "research/fetched/hubs-manufacturing-standards.html",
            "research/fetched/engineersedge-iso286-1-it-grades.html",
            "research/fetched/wei2025-polymers-17-416-gear-accuracy.html",
            "research/fetched/bambulab-h2s.html",
            "research/fetched/PROVENANCE.json",
            "ce-parts/microduck-yaw2roll/current/cad/interfaces.json",
            "ce-parts/microduck-hip-bracket/current/cad/interfaces.json",
            "ce-parts/microduck-neck-pitch-bracket/current/cad/interfaces.json",
            "ce-connections/spline-xl330-horn/iterations/v0.0.1/cad/mate.py",
        ],
    }

    a = results[worst_ang]["FDM-A prototyping"]
    b = results[worst_ang]["FDM-B industrial"]
    dd = results[worst_ang]["FDM-D measured study"]
    eq16A = equivalence["FDM-A prototyping"]["16.0"]
    eq16B = equivalence["FDM-B industrial"]["16.0"]
    eq10A = equivalence["FDM-A prototyping"]["10.0"]
    eq16D = equivalence["FDM-D measured study"]["16.0"]
    hy = results["left_hip_yaw"]["FDM-A prototyping"]
    hyB = results["left_hip_yaw"]["FDM-B industrial"]
    supported_flags = [f for f in flags if f.get("total_bore_support_pct") is not None]
    out["verdict"] = "CANNOT DETERMINE"
    out["why"] = (
        "The stack cannot be closed because the band it rests on is not measured for "
        "the machine that will print these parts. At FDM-A (Protolabs prototyping, "
        "±0.5 mm floor) the Ø16 printed seat's total band is %.0f um, which grades %s "
        "on the published ISO 286-1:2010(E) table (%s = %d um at that size); at FDM-B "
        "(industrial, ±0.3 mm floor) it is %.0f um, %s (%d um). The Ø10 ankle seat is "
        "the only feature that is genuinely COARSER THAN IT16 at FDM-A: %.0f um "
        "against IT16's %d um. A ball bearing seat is normally an IT6-IT7 feature, so "
        "both service bands are far too coarse for a press fit -- but a MEASURED "
        "print-accuracy study on a tuned FDM machine (Wei et al. 2025, Polymers "
        "17(3):416, archived) reports ±0.150 mm on its small features and grades its "
        "own parts IT09-IT11; at that band the Ø16 seat is %.0f um, %s. So the "
        "question is not whether FDM can hold a bearing seat -- it is what OUR "
        "machine holds, and print_fits.json is empty. "
        "THE BEARING ENGAGEMENT FLAG IS WITHDRAWN AND REPLACED. %d of 14 joints put "
        "the ring on a printed boss shorter than the ring (Ø16.0 x 1.90-1.95 mm in a "
        "4.0 mm ring, 47.50-48.75 %%), but the rest of the SAME bore rides the servo's "
        "own Ø16.0 x 3.0 horn disc: measured support is %.4f of 4.0000 mm, %.2f %%, at "
        "every one of them (ce-parts/microduck-yaw2roll/.../interfaces.json says so "
        "verbatim; out/sim-evidence/joint-geometry.json measures it at all four). The "
        "real, previously unstudied risk at those joints is the COAXIALITY STEP "
        "between the two bosses that share the bore: %.4f mm worst case at FDM-A "
        "against %.4f mm of radial clearance to absorb it, so the ring binds; %s at "
        "FDM-B. That is CANNOT DETERMINE, not FAIL, because no published FDM standard "
        "states a POSITIONAL tolerance and the ring's own internal clearance is "
        "unknown. "
        "The worst joint for angle is %s: %.4f deg upper bound at FDM-A, %.4f deg at "
        "FDM-B, %.4f deg at the measured-study band, governed by %s. 2 joints (%s) "
        "have a bearing on the axis that NO part folder declares a seat for. No "
        "joint's axial stack reaches its support at ANY band -- the two hip-yaws come "
        "closest at %.4f mm of stack against %.4f mm of supported ring, %.1f %% "
        "consumed at FDM-A and %.1f %% at FDM-B. "
        "What settles the whole study is one printed coupon: cecad.coupon.coupon() at "
        "the Ø10 and Ø16 rungs, printed, measured with calipers and stored with "
        "record_measurements() -- print_fits.json is {\"machines\": {}} today. Bambu "
        "publishes no part dimensional tolerance for the H2S to use instead (see "
        "inputs.fdm_band_C)."
        % (eq16A["total_band_um"], eq16A["nearest_iso286_grade_at_or_above"],
           eq16A["nearest_iso286_grade_at_or_above"], eq16A["that_grade_band_um"],
           eq16B["total_band_um"], eq16B["nearest_iso286_grade_at_or_above"],
           eq16B["that_grade_band_um"],
           eq10A["total_band_um"], it_um(10.0, 16),
           eq16D["total_band_um"], eq16D["nearest_iso286_grade_at_or_above"],
           len(supported_flags),
           supported_flags[0]["total_bore_support_mm"] if supported_flags else 0.0,
           supported_flags[0]["total_bore_support_pct"] if supported_flags else 0.0,
           hy["angular_misalignment_deg"]["coaxiality_step_between_the_two_bosses"]["worst_case_mm"],
           hy["angular_misalignment_deg"]["coaxiality_step_between_the_two_bosses"]["available_radial_clearance_mm"],
           ("it still binds" if hyB["angular_misalignment_deg"]
            ["coaxiality_step_between_the_two_bosses"]["binds"] else "it does not bind"),
           worst_ang, a["angular_misalignment_deg"]["worst_case"],
           b["angular_misalignment_deg"]["worst_case"],
           dd["angular_misalignment_deg"]["worst_case"],
           a["angular_misalignment_deg"]["governing"],
           ", ".join(f["joint"] for f in flags
                     if f.get("total_bore_support_pct") is None),
           hy["axial_play_mm"]["worst_case"],
           hy["axial_play_vs_bearing_engagement"]["engaged_length_mm"],
           100 * hy["axial_play_vs_bearing_engagement"]["worst_case_fraction_of_engagement"],
           100 * hyB["axial_play_vs_bearing_engagement"]["worst_case_fraction_of_engagement"]))

    path = os.path.join(REPO, "out/sim-evidence/tolerance-stack-hinges.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(out, open(path, "w"), indent=1)

    print("ISO 286 self-test:", "PASS" if selftest_ok else "FAIL", selftest)
    print()
    hdr = "%-16s %8s %8s %8s %8s %9s %9s %7s %7s"
    print(hdr % ("joint", "axialWC", "axialRSS", "radWC", "radRSS", "angWC",
                 "backlWC", "print%", "supp%"))
    for n in JOINTS:
        r = results[n]["FDM-A prototyping"]
        e = r["bearing"].get("printed_seat_engagement_pct")
        t = r["bearing"].get("total_bore_support_pct")
        print(hdr % (n, "%.4f" % r["axial_play_mm"]["worst_case"],
                     "%.4f" % r["axial_play_mm"]["rss"],
                     "%.4f" % r["radial_eccentricity_mm"]["worst_case"],
                     "%.4f" % r["radial_eccentricity_mm"]["rss"],
                     "%.4f" % r["angular_misalignment_deg"]["worst_case"],
                     "%.4f" % r["rotational_backlash_deg"]["worst_case"],
                     "-" if e is None else "%.2f" % e,
                     "-" if t is None else "%.2f" % t))
    print()
    print(out["why"])


if __name__ == "__main__":
    main()
