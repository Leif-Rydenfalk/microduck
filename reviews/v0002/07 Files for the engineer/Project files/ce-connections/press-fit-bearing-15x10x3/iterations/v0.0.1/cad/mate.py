"""connection:press-fit-bearing-15x10x3 -- seat the 15x10x3 bearing on a boss or in a pocket.

Contract (TRIAD.md, ce-connections section):

    def mate(a_iface, b_iface, params=None) -> dict
        keys: transform (4x4 row-major list), dof_left, joint, adds

PURE PYTHON MATH. No `import FreeCAD` at module top, ever. Shaped after
ce-connections/press-fit-608 (the workshop's worked example for a bearing
seat); the frame arithmetic is deliberately duplicated into each connection
folder (TRIAD.md line 51).

THE BEARING, measured not recalled: cecad.meshfeatures.cylinders on
reference/pollen-microduck-rl/assets/seeed_bearing__configuration_default.stl
(2026-09-02) reads hole Ø10.0 / boss Ø15.0, bbox 15.0 x 15.0 x 3.0 -- the
15 mm OD x 10 mm bore x 3 mm ring SPEC.md section 4 counts x3 on the robot
(ankle_left, ankle_right, jaw_soft in spec/mesh-placements.json). No vendor
designation exists in the reference; the slug is the dimensions.

THE SEATS this joint was written against, each with its own measured
interface on the microduck shelf:
    inner ring on a boss     microduck-shin 'ankle': Ø10.0 x 3.2 boss
    outer ring in a pocket   microduck-ankle-left/right 'ankle_bearing':
                             Ø15.0 x 2.3 pocket behind a Ø14.0 window,
                             Ø16 x 0.5 45-deg lead-in

For a press fit J is a pure translation along z: the two axes are COAXIAL
and CO-DIRECTED (nothing flips) and the only freedom is where along the
axis the ring lands. That is fixed by the shoulder it is pressed against;
if no shoulder is declared this module RAISES rather than seating the ring
at 0.0 -- a bearing 2 mm from where the drawing says looks correct in every
render (the press-fit-608 rule, kept verbatim).

Units: mm and degrees.
"""

import json as _json
import math
import os as _os

BORE_MM = 10.0    # meshfeatures hole d on the reference bearing mesh
OD_MM = 15.0      # meshfeatures boss d, same run
WIDTH_MM = 3.0    # numpy bbox z 0..3 of the same mesh
BEARING_REF = "part:bearing-15x10x3"

BEARING_IFACES = ("bore", "od")
SHAFT_NAMES = ("shaft", "boss")
HOUSING_NAMES = ("housing_bore", "pocket", "seat_bore")


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
        raise ValueError("%s is a zero-length vector %r" % (what, v))
    return _scale(v, 1.0 / n)


def frame_of(iface, what="interface"):
    if not isinstance(iface, dict):
        raise TypeError("%s must be an interface dict, got %r" % (what, type(iface)))
    fr = iface.get("frame")
    if not fr:
        raise ValueError("%s %r carries no 'frame' -- CANNOT DETERMINE a "
                         "transform" % (what, iface.get("name")))
    for key in ("origin_mm", "z_axis", "x_axis"):
        if fr.get(key) is None:
            raise ValueError("%s %r frame is missing %r -- CANNOT DETERMINE a "
                             "transform" % (what, iface.get("name"), key))
    o = [float(v) for v in fr["origin_mm"]]
    z = _unit([float(v) for v in fr["z_axis"]], "%s z_axis" % what)
    x_raw = [float(v) for v in fr["x_axis"]]
    x = _sub(x_raw, _scale(z, _dot(x_raw, z)))
    if math.sqrt(_dot(x, x)) < 1e-9:
        raise ValueError("%s %r: x_axis is parallel to z_axis -- no frame "
                         "exists and none is invented" % (what, iface.get("name")))
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


def translate_z(dz_mm, spin_deg=0.0):
    c, s = math.cos(math.radians(spin_deg)), math.sin(math.radians(spin_deg))
    return [[c, -s, 0.0, 0.0], [s, c, 0.0, 0.0],
            [0.0, 0.0, 1.0, float(dz_mm)], [0.0, 0.0, 0.0, 1.0]]


# ---------------------------------------------------------------------------
# THE JOINT, read from this folder's connection.json (record.joint).
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
        raise ValueError("connection:press-fit-bearing-15x10x3: connection.json "
                         "states no record.joint -- CANNOT DETERMINE what this "
                         "joint DOES.")
    return j


def _joint(dof_left, **over):
    j = dict(_declared_joint())
    declared = dict(j.get("axes") or {})
    axes = {a: "locked" for a in ("tx", "ty", "tz", "rx", "ry", "rz")}
    for tok in dof_left:
        ent = _AXIS_OF.get(tok)
        if ent is None:
            raise ValueError(
                "connection:press-fit-bearing-15x10x3 mate() returned dof_left "
                "token %r, not one of the six axes and not in _AXIS_OF -- an "
                "unnamed token reads as a WELD that solves silently." % (tok,))
        axes[ent] = declared.get(ent) if declared.get(ent) in ("free", "limited") else "free"
    j["axes"] = axes
    j["couples"] = [dict(c) for c in (j.get("couples") or [])]
    j["dof_left"] = list(dof_left)
    j.update(over)
    return j


def mate(a_iface, b_iface, params=None):
    """Seat the 15x10x3 (a_iface: 'bore' or 'od') onto a seat (b_iface).

    a_iface -- the BEARING side. Name 'bore' (Ø10 inner ring) or 'od' (Ø15
               outer ring), nominal_mm, frame. Frame origin at the ring's
               SEATED FACE, on the axis, +z along the axis into the bearing
               -- the datum, stated not inferred.
    b_iface -- the seat: 'shaft'/'boss' (mates 'bore') or 'housing_bore'/
               'pocket' (mates 'od'); the microduck shelf's role
               'bearing_seat' with either name also serves. Needs frame,
               nominal_mm, and either shoulder_z_mm or params['seat_dz_mm'].
    params  -- {"spin_deg": float (default 0.0 -- a ring has no index),
                "seat_dz_mm": float (overrides the shoulder datum),
                "spans_bearing": bool (default False -- see dof_left),
                "axial_retention": None | "shoulder_both_sides" | "clamped"
                                   | "glued"}

    Raises when the seating depth was never stated.
    """
    params = dict(params or {})
    a_name = a_iface.get("name")
    if a_name not in BEARING_IFACES:
        raise ValueError("a_iface must be the bearing side; the interface names "
                         "are fixed as 'bore' (Ø10) and 'od' (Ø15), got %r"
                         % (a_name,))
    b_name, b_role = b_iface.get("name"), _field(b_iface, "role")
    if b_name not in SHAFT_NAMES + HOUSING_NAMES and b_role not in (
            "bearing_seat", "bearing_face"):
        raise ValueError("b_iface must be the seat: 'shaft'/'boss' (mates "
                         "'bore') or 'housing_bore'/'pocket' (mates 'od'), or "
                         "role 'bearing_seat'; got name %r role %r"
                         % (b_name, b_role))

    nominal = BORE_MM if a_name == "bore" else OD_MM
    for iface, side, aliases in (
            (a_iface, "a_iface", ("bore_d_mm",) if a_name == "bore" else ("od_d_mm",)),
            (b_iface, "b_iface", ("seat_d_mm", "boss_d_mm", "pocket_d_mm"))):
        nom = _field(iface, "nominal_mm", *aliases)
        if nom is None:
            raise ValueError("%s states no nominal_mm -- CANNOT DETERMINE. The "
                             "slug is not a measurement." % side)
        if abs(float(nom) - nominal) > 0.5:
            raise ValueError("%s nominal_mm is %r; connection:press-fit-bearing-"
                             "15x10x3 seats %s mm on the '%s' side. A 22x16x4 "
                             "seat is connection:press-fit-bearing-22x16x4."
                             % (side, nom, nominal, a_name))

    # --- the seating datum -------------------------------------------------
    if params.get("seat_dz_mm") is not None:
        dz = float(params["seat_dz_mm"])
        datum_source = "params['seat_dz_mm'], supplied by the caller"
    elif _field(b_iface, "shoulder_z_mm") is not None:
        dz = float(_field(b_iface, "shoulder_z_mm"))
        datum_source = ("b_iface['shoulder_z_mm'] -- the ring is pressed until "
                        "its seated face touches the shoulder")
    else:
        raise ValueError(
            "Neither b_iface['shoulder_z_mm'] nor params['seat_dz_mm'] is "
            "given, so the axial position of the ring on this seat is CANNOT "
            "DETERMINE. mate() will not place it at 0.0: an interference fit "
            "has no self-locating feature along its axis. (The ankle pocket's "
            "own floor is such a shoulder -- state it.)")

    transform = matmul(matmul(frame_of(a_iface, "a_iface"),
                              translate_z(dz, float(params.get("spin_deg", 0.0)))),
                       invert_rigid(frame_of(b_iface, "b_iface")))

    # --- degrees of freedom ------------------------------------------------
    if params.get("spans_bearing"):
        dof_left = ["rotation_about_z"]
        dof_why = ("The mated pair spans the bearing (params['spans_bearing']), "
                   "so the relative freedom between the two bodies is the "
                   "bearing's own revolute DOF about its axis -- on this robot "
                   "that is the ankle hinge (MJCF left_ankle/right_ankle) and "
                   "the jaw pivot, where this ring sits.")
    else:
        dof_left = []
        dof_why = ("ONE SEAT considered alone -- ring on boss, or ring in "
                   "pocket -- and an interference fit is rigid: no DOF left. "
                   "The revolute freedom lives across the two seats. Pass "
                   "params['spans_bearing']=True to express boss-to-housing.")

    # --- axial retention ---------------------------------------------------
    adds = [BEARING_REF]
    retention = params.get("axial_retention")
    if retention not in (None, "shoulder_both_sides", "clamped", "glued"):
        raise ValueError("params['axial_retention'] %r is not one of None, "
                         "'shoulder_both_sides', 'clamped', 'glued'. No circlip "
                         "option here: no circlip groove exists on any measured "
                         "microduck seat and no circlip part folder is on this "
                         "shelf -- naming one would dangle." % (retention,))

    return {
        "transform": transform,
        "dof_left": dof_left,
        "joint": _joint(dof_left,
                        holds_by=("form" if params.get("spans_bearing")
                                  else "friction"),
                        holds_by_why=(
                            "form -- the pair spans the bearing and the open "
                            "rotation is the rolling elements'"
                            if params.get("spans_bearing") else
                            "friction -- one seat alone, held by whatever "
                            "interference the printed bore actually delivers, "
                            "which is unmeasured (compat)")),
        "adds": adds,
        "connection": "connection:press-fit-bearing-15x10x3",
        "why": {
            "dof": dof_why,
            "datum": datum_source,
            "seat_dz_mm": dz,
            "seat": "%s (Ø%s) into %s" % (a_name, nominal, b_name),
            "retention": "axial_retention = %r" % (retention,),
            "ring": {"d_mm": BORE_MM, "D_mm": OD_MM, "B_mm": WIDTH_MM,
                     "cite": "cecad.meshfeatures + bbox on seeed_bearing__"
                             "configuration_default.stl, 2026-09-02"},
            "interference": ("CANNOT DETERMINE here and in compat.py until "
                             "someone measures the as-printed seat "
                             "(measured_d_mm) and the actual ring "
                             "(ring_deviation_um) -- an FDM bore has no ISO "
                             "class and this unnamed ring has no vendor "
                             "sheet. mate() places geometry; it does not "
                             "certify grip."),
        },
    }


if __name__ == "__main__":
    fr = lambda o, z: {"origin_mm": list(o), "z_axis": list(z), "x_axis": [0, 0, 1]}
    ring = {"name": "od", "nominal_mm": 15.0,
            "frame": fr((32.5, 22.0, -6.223), (-1, 0, 0))}
    pocket = {"name": "ankle_bearing", "role": "bearing_seat", "nominal_mm": 15.0,
              "seat_length_mm": 2.3, "shoulder_z_mm": 0.0,
              "frame": fr((32.5, 22.0, -6.223), (-1, 0, 0))}
    m = mate(ring, pocket)
    print("dof_left:", m["dof_left"], "| adds:", m["adds"],
          "| holds_by:", m["joint"]["holds_by"])
    print("spanning:", mate(ring, pocket, {"spans_bearing": True})["dof_left"])
    for label, a, b, p in (
            ("no shoulder and no seat_dz", ring,
             {k: v for k, v in pocket.items() if k != "shoulder_z_mm"}, {}),
            ("a 22 mm seat", ring, dict(pocket, nominal_mm=22.0), {}),
            ("bore side into a pocket-named seat is fine by role",
             dict(ring, name="bore", nominal_mm=10.0),
             dict(pocket, nominal_mm=10.0, name="boss"), {}),
            ("a circlip nobody stocks", ring, pocket,
             {"axial_retention": "circlip_internal"})):
        try:
            mate(a, b, p)
            print("mated ok:", label)
        except ValueError as exc:
            print("refused %-34s %s" % (label + ":", str(exc)[:90]))
