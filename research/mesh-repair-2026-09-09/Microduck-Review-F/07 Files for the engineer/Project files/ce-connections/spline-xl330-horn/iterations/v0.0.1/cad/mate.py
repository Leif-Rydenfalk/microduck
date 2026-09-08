"""connection:spline-xl330-horn -- bolt a bracket onto an XL330 horn/idler face.

Contract (TRIAD.md, ce-connections section):

    def mate(a_iface, b_iface, params=None) -> dict
        keys: transform (4x4 row-major list), dof_left, joint, adds

PURE PYTHON MATH. No `import FreeCAD` at module top and there must never be
one. Shaped after ce-connections/spline-servo-25t (the workshop's worked
example for a servo output joint); the frame arithmetic is deliberately
duplicated into each connection folder (TRIAD.md line 51).

WHAT THIS JOINT IS, measured off Pollen's meshes (2026-09-01/02):
"spline" is in the slug because the XL330's output IS splined, but what the
Microduck's parts consume is the HORN FACE -- a Ø16.0 x 3.0 disc on each
face of the servo (horn +x, idler -x: cecad.meshfeatures bosses on
xl330.stl, quoted as DISC_D/DISC_L in ce-parts/xl330-m288-t/current/cad/
part.py) carrying 4 x Ø1.6 tapped holes 6.0 deep on a Ø12.0 bolt circle
(FACE_D/FACE_PCD/FACE_AT in the same file; Ø1.6 = the cecad fasteners.py M2
tap drill). The bracket brings 4 x Ø2.2-2.4 clearance holes on the same
Ø12 circle (measured per consumer: shin 'knee' 8.486 mm square = the Ø12
circle at 45 deg, yaw2roll r 6.0 at 0/90 deg, hip-bracket / neck-pitch /
yaw-roll-motion the same pattern) and 4 M2 screws close the joint.

THE THING MOST LIKELY TO BE GOT WRONG, stated first (the spline-servo-25t
rule): a horn mount is RIGID. The hip/knee/head rotation is the SERVO'S,
declared by the part (ce-parts/xl330-m288-t), not by this joint. mate()
returns dof_left [] with the screws fitted and never a rotation.

Frame convention: F(iface) from origin_mm / z_axis / x_axis; the interface
frames sit ON THE HORN FACE PLANE, +z out of the face along the joint axis
(the shin's 'knee' and the xl330's 'horn' connector are both stated that
way). transform = F(a) . J . F(b)^-1 with J a flip about x (the bracket
face looks back down the horn axis) plus the pattern clocking.

Units: mm and degrees.
"""

import json as _json
import math
import os as _os

DISC_D_MM = 16.0        # meshfeatures bosses on xl330.stl: Ø16.0, axis x, length 3.0
DISC_L_MM = 3.0
PCD_MM = 12.0           # 4 x Ø1.6 tapped at (y,z) = (0,±6),(±6,0) -> Ø12 circle
TAP_D_MM = 1.6          # = M2 tap drill, cecad/fasteners.py M2 row
TAP_DEPTH_MM = 6.0      # meshfeatures hole length on xl330.stl
SCREWS = 4
INDEX_STEP_DEG = 360.0 / SCREWS     # 90.0 -- the pattern's own symmetry

A_NAMES = ("horn", "idler", "horn_face", "servo_horn")
B_ROLES = ("horn_face",)
B_NAMES = ("horn_face", "horn_recess")

SCREW_REF = "part:screw-m2-iso4762"   # the only M2 fastener family on a
                                      # reachable shelf (checked 2026-09-02);
                                      # resolves, so it may be named here.


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


def spin_z(deg, dz_mm=0.0):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [[c, -s, 0.0, 0.0], [s, c, 0.0, 0.0],
            [0.0, 0.0, 1.0, float(dz_mm)], [0.0, 0.0, 0.0, 1.0]]


def flip_z(deg, dz_mm=0.0):
    """The two +z run antiparallel: the bracket face looks down the horn axis."""
    return matmul(spin_z(deg), [[1.0, 0.0, 0.0, 0.0],
                                [0.0, -1.0, 0.0, 0.0],
                                [0.0, 0.0, -1.0, float(dz_mm)],
                                [0.0, 0.0, 0.0, 1.0]])


# ---------------------------------------------------------------------------
# THE JOINT, read from this folder's connection.json (record.joint) -- one
# definition, read rather than copied (the 2026-08-27 rule: dof_left alone
# cannot select a joint model, and an unnamed token reads as a weld).
# ---------------------------------------------------------------------------

_AXIS_OF = {
    "translation_along_x": "tx", "translation_along_y": "ty",
    "translation_along_z": "tz", "rotation_about_x": "rx",
    "rotation_about_y": "ry", "rotation_about_z": "rz",
}


def _declared_joint():
    p = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
                      "connection.json")
    with open(p, encoding="utf-8") as fh:
        rec = _json.load(fh)["record"]
    j = rec.get("joint")
    if not isinstance(j, dict):
        raise ValueError("connection:spline-xl330-horn: connection.json states no "
                         "record.joint -- CANNOT DETERMINE what this joint DOES.")
    return j


def _joint(dof_left, **over):
    j = dict(_declared_joint())
    declared = dict(j.get("axes") or {})
    axes = {a: "locked" for a in ("tx", "ty", "tz", "rx", "ry", "rz")}
    for tok in dof_left:
        ent = _AXIS_OF.get(tok)
        if ent is None:
            raise ValueError(
                "connection:spline-xl330-horn mate() returned dof_left token %r, "
                "which is not one of the six axes and is not in _AXIS_OF -- an "
                "unnamed token reads as a WELD that solves silently." % (tok,))
        axes[ent] = declared.get(ent) if declared.get(ent) in ("free", "limited") else "free"
    j["axes"] = axes
    j["couples"] = [dict(c) for c in (j.get("couples") or [])]
    j["dof_left"] = list(dof_left)
    j.update(over)
    return j


def mate(a_iface, b_iface, params=None):
    """Bolt a bracket face (b) onto an XL330 horn or idler face (a).

    a_iface -- the SERVO's disc face. Name `horn` / `idler` / `horn_face` /
               `servo_horn`. Frame ON the disc face plane, +z out of the face
               along the axis (ce-parts/xl330-m288-t's `horn` connector is at
               (14.5, 0, 0) dir +x in the mesh frame, i.e. exactly this).
    b_iface -- the driven bracket face. Role `horn_face` (the microduck shelf's
               spelling: shin `knee`, yaw2roll `yaw_horn`, ankle `ankle_horn`,
               hip-bracket `roll_horn`/`pitch_horn`, ...). Frame on the mating
               face, +z toward the servo.
    params  -- {"index": int      REQUIRED, no default. Which of the 4
                                  discrete 90-degree seatings of the bolt
                                  pattern the bracket takes. See below.
                "clock_deg": float default 0.0 -- additional continuous
                                  clocking carried by the servo OUTPUT under
                                  the horn (the internal spline the mesh does
                                  not show). This is the servo-zero choice, a
                                  build decision reported back verbatim.
                "seat_dz_mm": float default 0.0 -- face-to-face offset; the
                                  faces touch at 0 (both frames on the plane).
                "opposed": bool   default True -- the bracket looks down the
                                  horn axis, which is how a bracket goes on.}

    REFUSES a missing frame and a missing index. Reports (never grades) the
    unmeasured horn hub.
    """
    params = dict(params or {})
    a_name = _field(a_iface, "name")
    b_name, b_role = _field(b_iface, "name"), _field(b_iface, "role")
    if a_name not in A_NAMES:
        raise ValueError(
            "a_iface is named %r; connection:spline-xl330-horn mates the SERVO's "
            "horn/idler face on the a side, named one of %s. A rename is a "
            "measurement the importer has to make, not one this folder invents."
            % (a_name, " / ".join(repr(x) for x in A_NAMES)))
    if b_role not in B_ROLES and b_name not in B_NAMES:
        raise ValueError(
            "b_iface is named %r with role %r; the b side is the driven bracket "
            "face -- role %r (the microduck shelf's spelling) or name one of %s."
            % (b_name, b_role, B_ROLES[0], " / ".join(repr(x) for x in B_NAMES)))

    idx = params.get("index")
    if idx is None:
        raise ValueError(
            "params['index'] is REQUIRED and has NO DEFAULT. The 4-hole pattern "
            "has 4 discrete seatings %g deg apart, and which one the bracket is "
            "on is a build decision, not a property of either part -- shin's "
            "holes sit at the 45-deg positions and yaw2roll's at 0 deg on the "
            "SAME Ø12 circle, so a silent 0 here would cross-thread one of them. "
            "Defaulting it would choose for you." % INDEX_STEP_DEG)
    idx = int(idx)
    if not (0 <= idx < SCREWS):
        raise ValueError("params['index'] = %d is outside 0..%d -- a %d-hole "
                         "pattern has %d seatings and no more."
                         % (idx, SCREWS - 1, SCREWS, SCREWS))
    clock_deg = idx * INDEX_STEP_DEG + float(params.get("clock_deg", 0.0))

    dz = float(params.get("seat_dz_mm", 0.0))
    opposed = params.get("opposed", True)
    j = (flip_z if opposed else spin_z)(clock_deg, dz)
    transform = matmul(matmul(frame_of(a_iface, "a_iface"), j),
                       invert_rigid(frame_of(b_iface, "b_iface")))

    dof_left = []
    dof_why = ("NONE. Four M2 screws through the bracket's Ø2.2 clearance holes "
               "into the horn's Ø1.6 tapped holes clamp the two faces; the "
               "centre pilot and the screws remove the rest. THE SERVO'S "
               "ROTATION IS NOT THIS JOINT'S -- it belongs to the part "
               "(part:xl330-m288-t; the MJCF's hip/knee/head joints live at the "
               "servo, not at its mount). Typing a revolute here is the exact "
               "mistake connection:spline-servo-25t documents on the rc car.")

    return {
        "transform": transform,
        "dof_left": dof_left,
        "joint": _joint(dof_left),
        "adds": [SCREW_REF],
        "connection": "connection:spline-xl330-horn",
        "why": {
            "dof": dof_why,
            "pattern": {"disc_d_mm": DISC_D_MM, "disc_l_mm": DISC_L_MM,
                        "pcd_mm": PCD_MM, "screws": SCREWS,
                        "tap_d_mm": TAP_D_MM, "tap_depth_mm": TAP_DEPTH_MM,
                        "cite": "cecad.meshfeatures.cylinders on xl330.stl, "
                                "2026-09-01; constants quoted in "
                                "ce-parts/xl330-m288-t/current/cad/part.py"},
            "index": idx,
            "clocking_deg": clock_deg,
            "clock_note": ("index picks one of 4 discrete 90-deg pattern "
                           "seatings; params['clock_deg'] carries the servo-"
                           "zero choice on the internal output spline, which "
                           "Pollen's mesh does not model -- it is reported "
                           "back verbatim, never invented."),
            "seat_dz_mm": dz,
            "opposed": bool(opposed),
            "adds": ("4 x M2 cap screw per joint -- ONE ref, part:screw-m2-"
                     "iso4762 (qty is the pattern's 4). Each screw is itself a "
                     "connection:threaded-m2 joint (thread_ext = the screw, "
                     "thread_int = the horn's Ø1.6 tapped hole); an assembly "
                     "that wants the screws as joints routes them there."),
            "hub_pilot": ("CANNOT DETERMINE. Every measured bracket carries a "
                          "Ø5-6 centre bore, but xl330.stl has no centre hub "
                          "(axis probe solid -14.5..14.5, cecad.meshslice "
                          "2026-09-02). The seating DEPTH is therefore taken "
                          "from the FACES, which both meshes do carry."),
        },
    }


if __name__ == "__main__":
    horn = {"name": "horn",
            "frame": {"origin_mm": [14.5, 0, 0], "z_axis": [1, 0, 0],
                      "x_axis": [0, 0, 1]},
            "pcd_mm": 12.0, "screws": 4, "tap_d_mm": 1.6}
    knee = {"name": "knee", "role": "horn_face",
            "frame": {"origin_mm": [40.45, 22.0, 35.777], "z_axis": [1, 0, 0],
                      "x_axis": [0, 0, 1]},
            "screw_square_mm": 8.486, "screws": 4, "clearance_d_mm": 2.2,
            "centre_d_mm": 6.0}
    m = mate(horn, knee, {"index": 1})
    print("dof_left:", m["dof_left"], "| adds:", m["adds"])
    print("clocking:", m["why"]["clocking_deg"], "deg")
    print("joint.axes:", m["joint"]["axes"])
    for label, a, b, p in (
            ("no index", horn, knee, {}),
            ("index 4 of a 4-hole pattern", horn, knee, {"index": 4}),
            ("a side not a horn", dict(horn, name="spline"), knee, {"index": 0}),
            ("b side not a horn_face", horn,
             dict(knee, role="bearing_seat", name="ankle"), {"index": 0})):
        try:
            mate(a, b, p)
            print("NOT REFUSED (defect):", label)
        except ValueError as exc:
            print("refused %-28s %s" % (label + ":", str(exc)[:96]))
