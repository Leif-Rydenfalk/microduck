"""connection:threaded-m2.5 -- place an internal M2.5 thread onto an external one.

Contract (TRIAD.md, ce-connections section):

    def mate(a_iface, b_iface, params=None) -> dict
        keys: transform (4x4 row-major list), dof_left (list), joint, adds

PURE PYTHON MATH. No `import FreeCAD` at module top and there must never be
one: this module has to run where no CAD kernel is installed.

Shaped after ce-connections/threaded-m3/current/cad/mate.py, the workshop's
worked example for a threaded joint; the frame arithmetic is deliberately
duplicated into each connection folder (TRIAD.md line 51: an iteration folder
is COMPLETE, never a diff). The numbers changed to the M2.5 row:

    NOMINAL 2.5 mm, coarse pitch 0.45 mm -- ISO 261 coarse for nominal
    diameter 2.5 mm, cross-checked against ce-cad/cecad/fasteners.py line 58,
    the M2.5 row this workshop already drills against:
      ("M2.5", 2.5, 0.45, 2.05, 2.70, 2.90, 3.10, 4.5, 2.5, 5.2, 5.0, 6.0, 0.5)

WHY THIS FOLDER EXISTS: the Microduck is an M2 system in three of its four
measured hole populations and an M2.5 system in the fourth. SPEC.md section 4's
census reads "Ø2.2 clearance x77, Ø4.4 c'bore x28, Ø1.6 tap x20, Ø2.7/2.8 x20"
off Pollen's meshes; the first three are the fasteners.py M2 close-clearance,
counterbore and tap-drill figures and the fourth is not an M2 figure at all --
Ø2.70 and Ø2.90 are the fasteners.py M2.5 close and normal clearances, and
docs/BOM.md section 4 buys "M2.5x6 x20" for exactly those twenty positions.
Two of those populations are measured, not inferred: the three head-close
screws at Ø2.695 into Ø2.100 x 11.200 printed posts
(out/verify/manufacturing_partial.json, bottom_head_shell / top_head_shell) and
the four compute-board mount holes at Ø2.8140 (part:radxa-zero-3w
cad/interfaces.json, measured off Radxa's own §4 drawing by
tools/measure_radxa_drawing.py). Before this folder existed those interfaces
had to write accepts: ["connection:threaded-m2"] -- naming a screw they carry
0.814 mm of diametral float on -- or leave accepts empty. REBUILD-PROTOCOL.md
section 4's rule applies unchanged: "a dangling ref is a FAIL that names the
work."

Frame convention, identical to the pilot connections:

    F(iface) = orthonormal 4x4 from origin_mm / z_axis / x_axis, mm, row-major
    transform = F(a) . J . F(b)^-1

where J for a threaded pair is a 180 degree rotation about x (the screw
enters the hole: the two +z run antiparallel) plus a translation along z by
the seating datum.

REFUSAL IS PART OF THE CONTRACT. mate() raises rather than returning a
plausible transform when a number it needs was never measured.

Units: mm and degrees, everywhere.
"""

import json as _json
import math
import os as _os

PITCH_MM = 0.45         # ISO 261 coarse pitch for nominal diameter 2.5 mm
NOMINAL_MM = 2.5
PROFILE = "ISO 68-1"

# Which ce-parts folder each thread-provider maps to. As in threaded-m2, most
# M2.5 fastener families have no folder on any reachable shelf (listed
# 2026-09-03: the workshop ce-parts/ carries screw-m2.5-iso4762 and nothing
# else in M2.5 -- no nut-m2.5, no insert-m2.5), and TRIAD.md makes a dangling
# ref a FAIL -- so only the providers whose folder EXISTS are mapped, and an
# unmapped provider is REFUSED BY NAME rather than resolved to a ref that does
# not resolve.
INTERNAL_PROVIDER_PART = {
    "tapped_hole": None,        # cut/tapped into part B itself: adds no part
    "self_tapped_boss": None,   # the Microduck's head-close case: the M2.5
                                # forms its own thread in a printed Ø2.100 x
                                # 11.200 post with a Ø2.800 x 0.800 lead-in
                                # (measured, top_head_shell)
}

EXTERNAL_PROVIDER_PART = {
    "socket_head_cap": "part:screw-m2.5-iso4762",  # exists, sourced, PASS
    "stud": None,               # part B is itself the threaded stud
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
    """The thread record as a DICT, accepting the 'M2.5x0.45' spelling too."""
    th = _field(iface, "thread")
    if th is None:
        return {}
    if isinstance(th, dict):
        return dict(th)
    if not isinstance(th, str):
        raise ValueError(
            "%s states thread as %s (%r) -- CANNOT DETERMINE. Object or 'M2.5x0.45' "
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
            "connection:threaded-m2.5: connection.json states no record.joint -- "
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
                "connection:threaded-m2.5 mate() returned the dof_left token %r, "
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


def _check_thread(iface, expect_name, what):
    if iface.get("name") != expect_name:
        raise ValueError("%s is named %r; connection:threaded-m2.5 mates the fixed "
                         "pilot interface names 'thread_ext' and 'thread_int'"
                         % (what, iface.get("name")))
    th = read_thread(iface, what)
    des = th.get("designation")
    if des is None:
        raise ValueError("%s %r states no thread.designation -- CANNOT DETERMINE "
                         "whether it is M2.5. Nothing is assumed."
                         % (what, iface.get("name")))
    if str(des).upper().replace(" ", "") not in ("M2.5", "M2.5X0.45", "M2.5X0,45"):
        raise ValueError("%s thread is %r, not M2.5 -- this connection folder is "
                         "M2.5 only. A different size is a different folder, which "
                         "is the point of one-folder-per-connection." % (what, des))
    p = th.get("pitch_mm")
    if p is not None and abs(float(p) - PITCH_MM) > 1e-9:
        raise ValueError("%s states pitch %r mm; ISO 261 coarse pitch for M2.5 is "
                         "%s mm. A fine-pitch M2.5 x 0.35 is a DIFFERENT joint and "
                         "needs its own folder." % (what, p, PITCH_MM))
    return th


def mate(a_iface, b_iface, params=None):
    """Mate an external M2.5 thread (a) to an internal M2.5 thread (b).

    a_iface  -- the screw/stud side, name "thread_ext". Expected fields:
                thread (object or "M2.5x0.45"), provider (see
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
    b_th = _check_thread(b_iface, "thread_int", "b_iface")

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
            "another M2.5 fastener family, put that family on a shelf first -- "
            "TRIAD.md makes a dangling ref a FAIL, so this folder maps only "
            "providers whose ce-parts folder exists (checked 2026-09-02: only "
            "screw-m2.5-iso4762 does)."
            % (a_prov, sorted(EXTERNAL_PROVIDER_PART)))
    if b_prov not in INTERNAL_PROVIDER_PART:
        raise ValueError("b_iface.provider %r is not one of %s"
                         % (b_prov, sorted(INTERNAL_PROVIDER_PART)))
    if EXTERNAL_PROVIDER_PART[a_prov]:
        adds.append(EXTERNAL_PROVIDER_PART[a_prov])
    if INTERNAL_PROVIDER_PART[b_prov]:
        adds.append(INTERNAL_PROVIDER_PART[b_prov])

    # --- the length the caller still has to choose ------------------------
    grip = _field(a_iface, "grip_length_mm")
    depth = _field(b_iface, "thread_depth_mm")
    if grip is None or depth is None:
        screw_length = None
        length_why = ("CANNOT DETERMINE the screw length: a_iface.grip_length_mm"
                      "=%r, b_iface.thread_depth_mm=%r. ce-parts/screw-m2.5-iso4762 "
                      "is a FAMILY on length (14 sourced lengths, 3-30 mm) and "
                      "the member is chosen by the joint, not by this folder."
                      % (grip, depth))
    else:
        t_len = _field(a_iface, "thread_length_mm")
        engage = min(float(depth), float(depth if t_len is None else t_len))
        screw_length = float(grip) + engage
        length_why = ("grip %.3f mm + engaged thread %.3f mm = %.3f mm of screw "
                      "below the head. Round UP to a stocked ISO 4762 length; "
                      "ce-parts/screw-m2.5-iso4762 has fetched-and-read offers at "
                      "3, 4, 5, 6, 8, 10, 12, 14, 15, 16, 18, 20, 25 and 30 mm."
                      % (float(grip), engage, screw_length))

    return {
        "transform": transform,
        "dof_left": dof_left,
        "joint": _joint(dof_left),
        "adds": adds,
        "connection": "connection:threaded-m2.5",
        "why": {
            "dof": dof_why,
            "datum": datum_source,
            "seat_dz_mm": dz,
            "screw_length_needed_mm": screw_length,
            "screw_length": length_why,
            "profile": "%s, M2.5 x %s coarse (ISO 261)" % (PROFILE, PITCH_MM),
            "preload": ("NOT COMPUTED HERE. mate() places geometry. Preload is "
                        "a friction problem with no measured inputs in this "
                        "workshop -- compat.py returns CANNOT DETERMINE for it "
                        "unless the caller supplies measured mu_thread and "
                        "mu_bearing."),
        },
        "thread": {"a": a_th, "b": b_th, "nominal_mm": NOMINAL_MM,
                   "pitch_mm": PITCH_MM},
    }


if __name__ == "__main__":
    fr = lambda o, z=(0, 0, 1): {"origin_mm": list(o), "z_axis": list(z),
                                 "x_axis": [1, 0, 0]}
    ext = {"name": "thread_ext", "frame": fr((0, 0, 0)),
           "thread": {"designation": "M2.5", "pitch_mm": 0.45},
           "provider": "socket_head_cap", "thread_length_mm": 8.0,
           "grip_length_mm": 2.5}
    inn = {"name": "thread_int", "frame": fr((0, 0, 2.5), (0, 0, -1)),
           "thread": "M2.5x0.45", "provider": "self_tapped_boss",
           "thread_depth_mm": 11.2, "pilot_d_mm": 2.1}
    m = mate(ext, inn)
    print("dof_left:", m["dof_left"], "| adds:", m["adds"])
    print("screw length:", m["why"]["screw_length_needed_mm"])
    print("loose dof:", mate(ext, inn, {"state": "loose"})["dof_left"])
    for label, a, b in (
            ("an M2 screw", dict(ext, thread={"designation": "M2"}), inn),
            ("a fine-pitch M2.5 x 0.35",
             dict(ext, thread={"designation": "M2.5", "pitch_mm": 0.35}), inn),
            ("no provider", {k: v for k, v in ext.items() if k != "provider"}, inn),
            ("an unmapped provider", dict(ext, provider="button_head"), inn)):
        try:
            mate(a, b)
            print("NOT REFUSED (defect):", label)
        except ValueError as exc:
            print("refused %-26s %s" % (label + ":", str(exc)[:100]))
