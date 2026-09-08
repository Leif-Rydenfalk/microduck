"""connection:self-tap-m2-pla -- place a M2 cap screw into an FDM-PRINTED PILOT
HOLE, the joint where the screw forms its own thread on first insertion.

Contract (TRIAD.md, ce-connections section):

    def mate(a_iface, b_iface, params=None) -> dict
        keys: transform (4x4 row-major list), dof_left (list), joint, adds

PURE PYTHON MATH. No `import FreeCAD` at module top and there must never be
one: this module has to run where no CAD kernel is installed.

The frame arithmetic below is DELIBERATELY DUPLICATED from
connection:self-tap-m2-pla/current/cad/mate.py -- TRIAD.md line 51: an iteration
folder is COMPLETE, never a diff. What is NOT duplicated is the joint's
meaning, and that is the whole reason this folder exists:

  * b_iface is named `pilot`, not `thread_int`. There is no internal thread
    until the screw makes one. Accepting the name `thread_int` here would let
    a caller mate a printed hole to a tapped-hole record and never notice.
  * the pilot DIAMETER is checked against what was MEASURED on the reference
    meshes (33 pilots of this size, 23 of them at Ø1.6 mm
    exactly -- ce-designs/microduck/out/fasteners/features-by-mesh.json), not
    against an ISO tap-drill row, because no standard governs a printed pilot.
  * mate() returns the length WINDOW, not one length: the minimum is a stated
    RULE (1.5 d of engagement) and the maximum is a MEASUREMENT (the pilot's
    own depth, the point the screw bottoms out). A single number would hide
    which half of it was measured.
  * every strength question returns None. Nobody has pulled a M2 screw out
    of a printed Ø1.6 pilot in this workshop and written the load down.

Units: mm and degrees, everywhere.
"""

import json as _json
import math
import os as _os

PITCH_MM = 0.40         # ISO 261 coarse pitch for nominal diameter 2 mm
NOMINAL_MM = 2
PROFILE = "ISO 68-1 (the SCREW's profile; the formed thread in PLA has no profile standard)"

# MEASURED on the reference meshes 2026-09-04 by cecad.meshfeatures.features():
# 33 pilots of this size, 23 of them at Ø1.60 mm to 0.000 mm. The accept band below
# is the measured spread, not a tolerance class -- a printed hole has no ISO class.
PILOT_NOMINAL_MM = 1.60
PILOT_MEASURED_MIN_MM = 1.450
PILOT_MEASURED_MAX_MM = 1.700

# A RULE, labelled as one wherever it appears: 1.5 x nominal diameter is the usual
# floor for thread engagement into a softer material. It is NOT a measurement of
# this robot and it is NOT a standard.
MIN_ENGAGE_D = 1.5


# Which ce-parts folder each thread-provider maps to. UNLIKE threaded-m3,
# most M2 fastener families have no folder on any reachable shelf yet
# (checked 2026-09-02: ce-parts/ has screw-m2-iso4762 and nothing else in
# M2), and TRIAD.md makes a dangling ref a FAIL -- so only the providers
# whose folder EXISTS are mapped, and an unmapped provider is REFUSED BY
# NAME rather than resolved to a ref that does not resolve.
INTERNAL_PROVIDER_PART = {
    # ONE provider, and the name says what it physically is. `tapped_hole` is
    # NOT accepted here on purpose: a hole somebody tapped is
    # connection:threaded-m2's joint, with a thread class and a cut flank.
    "printed_pilot": None,      # the thread is formed in part B itself: adds no part
}

EXTERNAL_PROVIDER_PART = {
    "socket_head_cap": "part:screw-m2-iso4762",
}


# --------------------------------------------------------------------------
# 4x4 rigid-transform arithmetic. Stdlib only, deliberately duplicated.
# --------------------------------------------------------------------------

def _field(iface, key, *aliases):
    """One scalar off an interface record, flat first then under `measured`."""
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
    """The thread record as a DICT, accepting the 'M2x0.4' string spelling too."""
    th = _field(iface, "thread")
    if th is None:
        return {}
    if isinstance(th, dict):
        return dict(th)
    if not isinstance(th, str):
        raise ValueError(
            "%s states thread as %s (%r) -- CANNOT DETERMINE. Object or 'M2x0.4' "
            "string only." % (what, type(th).__name__, th))
    s = th.upper().replace(" ", "").replace(",", ".")
    if "X" in s:
        des, _, pitch = s.partition("X")
        try:
            return {"designation": des, "pitch_mm": float(pitch), "spelling": th}
        except ValueError:
            raise ValueError("%s states thread %r -- the text after the 'x' is "
                             "not a pitch in mm. Nothing is assumed." % (what, th))
    return {"designation": s, "spelling": th}


def _sub(a, b):
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]


def _scale(v, k):
    return [v[0] * k, v[1] * k, v[2] * k]


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]]


def _unit(v, what):
    n = math.sqrt(_dot(v, v))
    if n < 1e-12:
        raise ValueError("%s is a zero-length vector %r -- an interface with no "
                         "axis cannot be mated" % (what, v))
    return _scale(v, 1.0 / n)


def frame_of(iface, what="interface"):
    """Orthonormal 4x4 (row-major) from an interface record."""
    if not isinstance(iface, dict):
        raise TypeError("%s must be an interface dict, got %r" % (what, type(iface)))
    fr = iface.get("frame")
    if not fr:
        raise ValueError("%s %r carries no 'frame' -- CANNOT DETERMINE a "
                         "transform. TRIAD.md: a missing value stays missing."
                         % (what, iface.get("name")))
    for key in ("origin_mm", "z_axis", "x_axis"):
        if fr.get(key) is None:
            raise ValueError("%s %r frame is missing %r -- CANNOT DETERMINE a "
                             "transform" % (what, iface.get("name"), key))
    o = [float(v) for v in fr["origin_mm"]]
    z = _unit([float(v) for v in fr["z_axis"]], "%s z_axis" % what)
    x_raw = [float(v) for v in fr["x_axis"]]
    x = _sub(x_raw, _scale(z, _dot(x_raw, z)))
    if math.sqrt(_dot(x, x)) < 1e-9:
        raise ValueError("%s %r: x_axis is parallel to z_axis -- no frame exists "
                         "and none is invented" % (what, iface.get("name")))
    x = _unit(x, "%s x_axis" % what)
    y = _cross(z, x)
    return [[x[0], y[0], z[0], o[0]],
            [x[1], y[1], z[1], o[1]],
            [x[2], y[2], z[2], o[2]],
            [0.0, 0.0, 0.0, 1.0]]


def matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)]
            for i in range(4)]


def invert_rigid(m):
    r = [[m[i][j] for j in range(3)] for i in range(3)]
    t = [m[i][3] for i in range(3)]
    rt = [[r[j][i] for j in range(3)] for i in range(3)]
    nt = [-sum(rt[i][k] * t[k] for k in range(3)) for i in range(3)]
    return [[rt[0][0], rt[0][1], rt[0][2], nt[0]],
            [rt[1][0], rt[1][1], rt[1][2], nt[1]],
            [rt[2][0], rt[2][1], rt[2][2], nt[2]],
            [0.0, 0.0, 0.0, 1.0]]


def flip_and_offset(dz_mm, spin_deg=0.0):
    """J for a threaded pair: rotate 180 deg about x, then translate dz along z."""
    c, s = math.cos(math.radians(spin_deg)), math.sin(math.radians(spin_deg))
    spin = [[c, -s, 0.0, 0.0], [s, c, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]
    flip = [[1.0, 0.0, 0.0, 0.0],
            [0.0, -1.0, 0.0, 0.0],
            [0.0, 0.0, -1.0, float(dz_mm)],
            [0.0, 0.0, 0.0, 1.0]]
    return matmul(spin, flip)


# ---------------------------------------------------------------------------
# THE JOINT, read from this folder's own connection.json (record.joint) --
# ONE definition, read here rather than copied. The rule and its measured
# history: threaded-m3/cad/mate.py, 2026-08-27 (dof_left alone cannot select
# a joint model; a token that is not an axis reads as a WELD that solves).
# ---------------------------------------------------------------------------

_AXIS_OF = {
    "translation_along_x": "tx", "translation_along_y": "ty",
    "translation_along_z": "tz", "rotation_about_x": "rx",
    "rotation_about_y": "ry", "rotation_about_z": "rz",
    "helical_about_z": ("rz", {"of": "tz", "per": "rz", "mm_per_rev": PITCH_MM,
                               "cite": "ISO 261 coarse pitch for nominal "
                                       "diameter 2 mm; PITCH_MM in this module"}),
}


def _declared_joint():
    p = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
                      "connection.json")
    with open(p, encoding="utf-8") as fh:
        rec = _json.load(fh)["record"]
    j = rec.get("joint")
    if not isinstance(j, dict):
        raise ValueError(
            "connection:self-tap-m2-pla: connection.json states no record.joint -- "
            "CANNOT DETERMINE what this joint DOES. Nothing is assumed here.")
    return j


def _joint(dof_left, **over):
    j = dict(_declared_joint())
    declared = dict(j.get("axes") or {})
    axes = {a: "locked" for a in ("tx", "ty", "tz", "rx", "ry", "rz")}
    couples = [dict(c) for c in (j.get("couples") or [])]
    for tok in dof_left:
        ent = _AXIS_OF.get(tok)
        if ent is None:
            raise ValueError(
                "connection:self-tap-m2-pla mate() returned the dof_left token %r, "
                "which is not one of the six axes and is not named in _AXIS_OF. "
                "An unnamed token reads as the EMPTY SET -- zero DOF -- a WELD "
                "that solves silently. Name it, or stop returning it." % (tok,))
        if isinstance(ent, tuple):
            ent, couple = ent
            couples.append(dict(couple))
        axes[ent] = declared.get(ent) if declared.get(ent) in ("free", "limited") else "free"
    j["axes"] = axes
    j["couples"] = couples
    j["dof_left"] = list(dof_left)
    j.update(over)
    return j


def check_pilot(iface, what="b_iface"):
    """The PRINTED side. Checked on its measured diameter, not on a thread name."""
    if iface.get("name") != "pilot":
        raise ValueError(
            "%s is named %r; connection:self-tap-m2-pla mates the interface names "
            "'thread_ext' (the screw) and 'pilot' (the PRINTED HOLE). A record named "
            "'thread_int' describes a CUT thread and belongs to connection:threaded-m2; "
            "accepting it here would let a tapped hole and a printed hole mate without "
            "anyone noticing they are different joints."
            % (what, iface.get("name")))
    d = _field(iface, "pilot_d_mm", "d_mm", "diameter_mm")
    if d is None:
        raise ValueError(
            "%s states no pilot_d_mm -- CANNOT DETERMINE whether a M2 screw can form a "
            "thread in it. Nothing is assumed: a printed hole has no nominal to fall back on."
            % what)
    d = float(d)
    if not (PILOT_MEASURED_MIN_MM <= d <= PILOT_MEASURED_MAX_MM):
        raise ValueError(
            "%s pilot is Ø%.4f mm, outside the MEASURED band [%.3f, %.3f] mm that every M2 "
            "pilot on the reference meshes falls in. Too small and the screw splits the boss; "
            "too large and it spins. This folder refuses rather than widening its own band."
            % (what, d, PILOT_MEASURED_MIN_MM, PILOT_MEASURED_MAX_MM))
    depth = _field(iface, "pilot_depth_mm", "thread_depth_mm", "depth_mm")
    return {"pilot_d_mm": d, "pilot_depth_mm": None if depth is None else float(depth)}


def _check_thread(iface, expect_name, what):
    if iface.get("name") != expect_name:
        raise ValueError("%s is named %r; connection:self-tap-m2-pla mates the fixed "
                         "pilot interface names 'thread_ext' and 'thread_int'"
                         % (what, iface.get("name")))
    th = read_thread(iface, what)
    des = th.get("designation")
    if des is None:
        raise ValueError("%s %r states no thread.designation -- CANNOT DETERMINE "
                         "whether it is M2. Nothing is assumed."
                         % (what, iface.get("name")))
    if str(des).upper().replace(" ", "") not in ("M2", "M2X0.4", "M2X0,4"):
        raise ValueError("%s thread is %r, not M2 -- this connection folder is "
                         "M2 only. A different size is a different folder, which "
                         "is the point of one-folder-per-connection." % (what, des))
    p = th.get("pitch_mm")
    if p is not None and abs(float(p) - PITCH_MM) > 1e-9:
        raise ValueError("%s states pitch %r mm; ISO 261 coarse pitch for M2 is "
                         "%s mm. A fine-pitch M2 x 0.25 is a DIFFERENT joint and "
                         "needs its own folder." % (what, p, PITCH_MM))
    return th


def mate(a_iface, b_iface, params=None):
    """Mate an external M2 thread (a) to an internal M2 thread (b).

    a_iface  -- the screw/stud side, name "thread_ext". Expected fields:
                thread (object or "M2x0.4"), provider (see
                EXTERNAL_PROVIDER_PART), and grip_length_mm /
                thread_length_mm for the length arithmetic.
    b_iface  -- the internal side, name "thread_int". Expected fields:
                thread, provider (see INTERNAL_PROVIDER_PART),
                thread_depth_mm.
    params   -- {"state": "tight"|"loose" (default "tight"),
                 "spin_deg": float (default 0.0),
                 "seat_dz_mm": float (overrides the derived datum)}

    Returns the contract dict. Raises when a number it needs was never
    measured -- it never substitutes one.
    """
    params = dict(params or {})
    a_th = _check_thread(a_iface, "thread_ext", "a_iface")
    b_pilot = check_pilot(b_iface, "b_iface")
    b_th = {"designation": None,
            "why": "THERE IS NO THREAD ON SIDE B until the screw forms one. Reporting a "
                   "designation here would be the laundering this folder exists to prevent."}

    # --- the seating datum: both frames defined at the first full thread ---
    dz = 0.0
    datum_source = ("frames coincide at the first full thread, the datum both "
                    "pilot interfaces are defined at; no offset applied")
    for iface in (a_iface, b_iface):
        if _field(iface, "datum_offset_mm") is not None:
            dz += float(_field(iface, "datum_offset_mm"))
            datum_source = "sum of the interfaces' own declared datum_offset_mm"
    if params.get("seat_dz_mm") is not None:
        dz = float(params["seat_dz_mm"])
        datum_source = "params['seat_dz_mm'], supplied by the caller"

    transform = matmul(matmul(frame_of(a_iface, "a_iface"),
                              flip_and_offset(dz, float(params.get("spin_deg", 0.0)))),
                       invert_rigid(frame_of(b_iface, "b_iface")))

    # --- degrees of freedom ----------------------------------------------
    state = params.get("state", "tight")
    if state == "tight":
        dof_left = []
        dof_why = ("A tightened threaded joint is a friction clamp: preload "
                   "closes all six DOF between the joined faces. True only "
                   "while preload is maintained -- and on this robot the "
                   "internal thread is usually SELF-TAPPED PLA, whose creep "
                   "under preload is unmeasured (ledger).")
    elif state == "loose":
        dof_left = ["helical_about_z"]
        dof_why = ("Untightened, the pair leaves ONE helical DOF: rotation "
                   "about z coupled to translation along z at %s mm per turn "
                   "(ISO 261 coarse pitch). One DOF, not two -- the helix "
                   "couples them." % PITCH_MM)
    else:
        raise ValueError("params['state'] must be 'tight' or 'loose', got %r"
                         % (state,))

    # --- the BOM this joint adds -----------------------------------------
    adds = []
    a_prov = _field(a_iface, "provider")
    b_prov = _field(b_iface, "provider")
    if a_prov is None or b_prov is None:
        raise ValueError(
            "mate() needs a 'provider' on BOTH interfaces to know what the joint "
            "ADDS to the BOM. a_iface.provider=%r (one of %s), b_iface.provider="
            "%r (one of %s). CANNOT DETERMINE otherwise, and a guessed fastener "
            "is a wrong purchase order."
            % (a_prov, sorted(EXTERNAL_PROVIDER_PART), b_prov,
               sorted(INTERNAL_PROVIDER_PART)))
    if a_prov not in EXTERNAL_PROVIDER_PART:
        raise ValueError(
            "a_iface.provider %r is not one of %s. If the joint really uses "
            "another M2 fastener family, put that family on a shelf first -- "
            "TRIAD.md makes a dangling ref a FAIL, so this folder maps only "
            "providers whose ce-parts folder exists (checked 2026-09-02: only "
            "screw-m2-iso4762 does)."
            % (a_prov, sorted(EXTERNAL_PROVIDER_PART)))
    if b_prov not in INTERNAL_PROVIDER_PART:
        raise ValueError("b_iface.provider %r is not one of %s"
                         % (b_prov, sorted(INTERNAL_PROVIDER_PART)))
    if EXTERNAL_PROVIDER_PART[a_prov]:
        adds.append(EXTERNAL_PROVIDER_PART[a_prov])
    if INTERNAL_PROVIDER_PART[b_prov]:
        adds.append(INTERNAL_PROVIDER_PART[b_prov])

    # --- the length: a WINDOW, half measured and half a stated rule --------
    grip = _field(a_iface, "grip_length_mm")
    depth = b_pilot["pilot_depth_mm"]
    if grip is None or depth is None:
        window = None
        screw_length = None
        length_why = ("CANNOT DETERMINE the screw length: a_iface.grip_length_mm=%r, "
                      "b_iface.pilot_depth_mm=%r. Both are MEASUREMENTS somebody has to take "
                      "off the geometry (ce-designs/microduck/tools/fastener_runs.py takes "
                      "them for every run in this robot); neither is defaulted here."
                      % (grip, depth))
    else:
        l_min = float(grip) + MIN_ENGAGE_D * NOMINAL_MM
        l_max = float(grip) + float(depth)
        window = [round(l_min, 4), round(l_max, 4)]
        stock = list(params.get("sourced_lengths_mm") or [])
        inside = [L for L in stock if l_min - 1e-9 <= L <= l_max + 1e-9]
        screw_length = inside[0] if inside else None
        length_why = (
            "MIN %.4f mm = grip %.4f + %g d (A RULE: minimum engagement in a softer material, "
            "not a measurement of this robot, not a standard). MAX %.4f mm = grip + the pilot's "
            "OWN MEASURED depth %.4f mm, the point the screw bottoms and stops clamping. "
            "Sourced lengths inside the window: %s."
            % (l_min, float(grip), MIN_ENGAGE_D, l_max, float(depth),
               inside if stock else "none offered to mate(); pass params['sourced_lengths_mm']"))

    return {
        "transform": transform,
        "dof_left": dof_left,
        "joint": _joint(dof_left),
        "adds": adds,
        "connection": "connection:self-tap-m2-pla",
        "why": {
            "dof": dof_why,
            "datum": datum_source,
            "seat_dz_mm": dz,
            "screw_length_mm": screw_length,
            "screw_length_window_mm": window,
            "screw_length": length_why,
            "strip_load_N": None,
            "strip_load_why": ("CANNOT DETERMINE. No %s screw has been pulled out of a printed "
                               "Ø%.2f pilot in this workshop. connection.json record.open_questions "
                               "names the coupon test that settles it." % (NOMINAL_MM, PILOT_NOMINAL_MM)),
            "reinsertions_before_failure": None,
            "reinsertions_why": ("CANNOT DETERMINE, and it is a DIFFERENT question from strip load: "
                                 "a formed thread is re-cut on every re-insertion. Same coupon, "
                                 "cycle by cycle."),
            "profile": "%s, M2 x %s coarse (ISO 261)" % (PROFILE, PITCH_MM),
            "preload": ("NOT COMPUTED HERE. mate() places geometry. Preload is "
                        "a friction problem with no measured inputs in this "
                        "workshop -- compat.py returns CANNOT DETERMINE for it "
                        "unless the caller supplies measured mu_thread and "
                        "mu_bearing."),
        },
        "thread": {"a": a_th, "b": b_th, "nominal_mm": NOMINAL_MM,
                   "pitch_mm": PITCH_MM},
        "pilot": b_pilot,
    }


if __name__ == "__main__":
    fr = lambda o, z=(0, 0, 1): {"origin_mm": list(o), "z_axis": list(z),
                                 "x_axis": [1, 0, 0]}
    ext = {"name": "thread_ext", "frame": fr((0, 0, 0)),
           "thread": {"designation": "M2", "pitch_mm": PITCH_MM},
           "provider": "socket_head_cap", "grip_length_mm": 3.0}
    pil = {"name": "pilot", "frame": fr((0, 0, 3.0), (0, 0, -1)),
           "provider": "printed_pilot", "pilot_d_mm": PILOT_NOMINAL_MM,
           "pilot_depth_mm": 6.0}
    m = mate(ext, pil, {"sourced_lengths_mm": [3, 4, 5, 6, 8, 10, 12, 14, 16, 20]})
    ok = fail = 0

    def check(label, cond):
        global ok, fail
        if cond:
            ok += 1
            print("PASS  %s" % label)
        else:
            fail += 1
            print("FAIL  %s" % label)

    check("adds exactly the screw", m["adds"] == [EXTERNAL_PROVIDER_PART["socket_head_cap"]])
    check("tight leaves no DOF", m["dof_left"] == [])
    check("loose leaves one helical DOF",
          mate(ext, pil, {"state": "loose"})["dof_left"] == ["helical_about_z"])
    check("length window is [grip+1.5d, grip+depth]",
          m["why"]["screw_length_window_mm"] == [round(3.0 + 1.5 * NOMINAL_MM, 4), 9.0])
    check("strip load refused", m["why"]["strip_load_N"] is None)
    check("reinsertions refused", m["why"]["reinsertions_before_failure"] is None)
    check("side B claims no thread designation", m["thread"]["b"]["designation"] is None)

    def refuses(label, a, b, params=None):
        global ok, fail
        try:
            mate(a, b, params)
        except ValueError as exc:
            ok += 1
            print("PASS  refuses %-34s %s" % (label, str(exc)[:80]))
            return
        fail += 1
        print("FAIL  DID NOT REFUSE %s" % label)

    refuses("a thread_int record", ext, dict(pil, name="thread_int"))
    refuses("a pilot with no diameter", ext,
            {k: v for k, v in pil.items() if k != "pilot_d_mm"})
    refuses("a pilot 0.5 mm oversize", ext, dict(pil, pilot_d_mm=PILOT_NOMINAL_MM + 0.5))
    refuses("a pilot 0.5 mm undersize", ext, dict(pil, pilot_d_mm=PILOT_NOMINAL_MM - 0.5))
    refuses("an unmapped provider", dict(ext, provider="button_head"), pil)
    refuses("a tapped_hole provider", ext, dict(pil, provider="tapped_hole"))
    print("\n%d PASS, %d FAIL" % (ok, fail))
    raise SystemExit(1 if fail else 0)
