"""Staged major-revision candidate. Physical mate refuses unresolved hardware.
nominal_transform retains historical face-frame math only; no joint/DOF/adds
contract is returned by that helper. No fitted original identity is established.
"""
import math
SCREWS = 4
INDEX_STEP_DEG = 90.0
A_NAMES = ("horn", "idler", "horn_face", "servo_horn")
B_ROLES = ("horn_face",)
B_NAMES = ("horn_face", "horn_recess")
REQUIRED_HARDWARE = {
    "quantity": 4, "manufacturer_callout": "M2 Tapping Screw",
    "part_ref": None, "length_mm": None, "pitch_mm": None, "profile": None,
    "minimum_engagement_mm": None, "maximum_pilot_depth_mm": 3.0,
    "verdict": "CANNOT DETERMINE",
    "why": "Exact tapping screw, original head seating and minimum engagement unresolved; ISO4762 is not established equivalent.",
    "source": "ROBOTIS X330 drawing28-May-20,4-Ø1.6 HOLE DP3.0(Max.),PCDØ12",
    "source_sha256": "948b707cb26a64501c03fc45b1a9557b69a554dd5d6934f02e8e6f86cf2b46c2"}

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

def nominal_transform(a_iface, b_iface, params=None):
    """Historical geometry diagnostic only, never physical mate or hardware approval."""
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

    return {"nominal_transform": transform,
            "scope": "Historical face-frame transform only; not a physical joint, mating approval or installed pose proof",
            "verdict": "CANNOT DETERMINE",
            "required_hardware": dict(REQUIRED_HARDWARE),
            "index": idx, "clocking_deg": clock_deg,
            "seat_dz_mm": dz, "opposed": bool(opposed)}


def mate(a_iface, b_iface, params=None):
    """Fail closed: existing assembly consumers do not enforce unresolved adds.

    No caller-supplied boolean or invented ref unlocks this. A future reviewed
    source-backed hardware contract must implement proof validation explicitly.
    """
    raise ValueError("CANNOT DETERMINE: physical XL330 horn mate requires 4 identified M2 tapping screws, verified head seating/profile/length and minimum engagement; maximum pilot depth 3 mm. ISO4762 additions withdrawn. Use nominal_transform only for labelled historical geometry diagnostics; it is not a physical mate.")
