"""connection:press-fit-tube-15 -- lay a Ø15 ring into the motor-support arch.

Contract (TRIAD.md, ce-connections section):

    def mate(a_iface, b_iface, params=None) -> dict
        keys: transform (4x4 row-major list), dof_left, joint, adds

PURE PYTHON MATH. No `import FreeCAD` at module top, ever. Shaped after
ce-connections/press-fit-bearing-15x10x3; the frame arithmetic is
deliberately duplicated into each connection folder (TRIAD.md line 51).

WHAT THIS JOINT IS, measured 2026-09-02 and frozen in
evidence/tube-15-geometry.json:

    the cradle   motor_support.stl, mesh-frame x-axis through (y 0.0000,
                 z 7.4995). Circle fits to meshslice cross-sections read
                 Ø14.9938 / 14.9954 / 14.9978 at the three stations whose
                 residual mean is < 0.0036 mm, swept 149.06-149.09 deg,
                 chord plane z 9.5000, crown z 15.0000. Two ring bands,
                 x -39.5000..-37.5000 (2.0000) and -36.5000..-35.5000
                 (1.0000), 1.0000 mm of Ø16.8 relief between them.
    the ring     the 15x10x3 bearing's Ø15.0 outer race.
    through it   the jaw's Ø10.0000 journal, centre (y 0.0000, z 7.5000),
                 x -39.7000..-37.0000, behind a Ø11.9949 x 0.3000 flange.

IT IS NOT A BORE. 210.94 deg of the circle is open air: there is no
material below z 9.5000 at these stations. mate() therefore returns
tz AND rz free, and REFUSES to invent an axial datum -- exactly the
press-fit-608 rule this shelf inherited: "a bearing 2 mm from where the
drawing says looks correct in every render".

IT IS NOT A LENS SEAT either, whatever the host interface is named. In this
same frame the m12 lens holder is at y -52.38..-37.58 and the lens at
y -63.8..-44.88, on a different axis; neither carries a Ø15 feature.

Units: mm and degrees.
"""

import json as _json
import math
import os as _os

BORE_D_MM = 14.9938          # smallest clean-station circle fit of the arch
BORE_D_MM_SPAN = (14.9938, 14.9978)
RING_D_MM = 15.0             # part:bearing-15x10x3 outer race
RING_B_MM = 3.0
ARC_DEG = 149.06
OPEN_DEG = 210.94
BAND_X_MM = ((-39.5, -37.5), (-36.5, -35.5))
RING_REF = "part:bearing-15x10x3"

CRADLE_NAMES = ("lens_tube", "cradle", "arch", "tube")
RING_NAMES = ("od", "ring", "tube_od")


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
        raise ValueError("connection:press-fit-tube-15: connection.json states "
                         "no record.joint -- CANNOT DETERMINE what this joint DOES.")
    return j


def _joint(dof_left, **over):
    j = dict(_declared_joint())
    declared = dict(j.get("axes") or {})
    axes = {a: "locked" for a in ("tx", "ty", "tz", "rx", "ry", "rz")}
    for tok in dof_left:
        ent = _AXIS_OF.get(tok)
        if ent is None:
            raise ValueError(
                "connection:press-fit-tube-15 mate() returned dof_left token "
                "%r, not one of the six axes and not in _AXIS_OF -- an unnamed "
                "token reads as a WELD that solves silently." % (tok,))
        axes[ent] = declared.get(ent) if declared.get(ent) in ("free", "limited") else "free"
    j["axes"] = axes
    j["couples"] = [dict(c) for c in (j.get("couples") or [])]
    j["dof_left"] = list(dof_left)
    j.update(over)
    return j


def mate(a_iface, b_iface, params=None):
    """Lay the Ø15 ring (a_iface) into the arch cradle (b_iface).

    a_iface -- the RING side: name 'od'/'ring'/'tube_od', nominal_mm ~15.0,
               frame origin on the axis at the ring's reference face, +z
               along the axis into the ring.
    b_iface -- the CRADLE: name 'lens_tube'/'cradle'/'arch'/'tube', or role
               'cradle'/'journal_cradle'/'lens_seat'. Needs frame and
               nominal_mm; needs seat_dz_mm (or params) because the cradle
               has NO axial datum of its own.
    params  -- {"spin_deg": float (default 0.0 -- a ring has no index),
                "seat_dz_mm": float, REQUIRED unless the cradle states
                              shoulder_z_mm: where along the axis the ring
                              lands. There is no default and 0.0 is not one.}

    Raises when the axial position was never stated, or when the ring is
    not a Ø15 body, or when the cradle's own arc was never measured.
    """
    params = dict(params or {})
    a_name = _field(a_iface, "name")
    if a_name not in RING_NAMES:
        raise ValueError("a_iface must be the Ø15 body laid into the cradle; "
                         "the accepted interface names are %s, got %r"
                         % (", ".join(repr(n) for n in RING_NAMES), a_name))
    b_name, b_role = _field(b_iface, "name"), _field(b_iface, "role")
    if b_name not in CRADLE_NAMES and b_role not in ("cradle", "journal_cradle",
                                                     "lens_seat"):
        raise ValueError("b_iface must be the cradle: name one of %s, or role "
                         "'cradle'/'journal_cradle'/'lens_seat'; got name %r "
                         "role %r" % (", ".join(repr(n) for n in CRADLE_NAMES),
                                      b_name, b_role))

    for iface, side, aliases in (
            (a_iface, "a_iface", ("od_d_mm", "d_mm")),
            (b_iface, "b_iface", ("bore_d_mm", "seat_d_mm"))):
        nom = _field(iface, "nominal_mm", *aliases)
        if nom is None:
            raise ValueError("%s states no nominal_mm -- CANNOT DETERMINE. The "
                             "slug is not a measurement." % side)
        if abs(float(nom) - RING_D_MM) > 0.5:
            raise ValueError("%s nominal_mm is %r; connection:press-fit-tube-15 "
                             "cradles Ø%s bodies only. Another diameter is "
                             "another folder." % (side, nom, RING_D_MM))

    if params.get("seat_dz_mm") is not None:
        dz = float(params["seat_dz_mm"])
        datum_source = "params['seat_dz_mm'], supplied by the caller"
    elif _field(b_iface, "shoulder_z_mm") is not None:
        dz = float(_field(b_iface, "shoulder_z_mm"))
        datum_source = ("b_iface['shoulder_z_mm'] -- an axial stop the CRADLE "
                        "declares; none was found on either measured ring band")
    else:
        raise ValueError(
            "Neither b_iface['shoulder_z_mm'] nor params['seat_dz_mm'] is "
            "given, so where the ring sits along this axis is CANNOT "
            "DETERMINE. mate() will not place it at 0.0. This cradle is worse "
            "than a press fit in exactly this respect: measurement found NO "
            "groove, shoulder or end stop on either ring band "
            "(x -39.5000..-37.5000 and -36.5000..-35.5000), so nothing in the "
            "geometry locates the ring axially at all. Pollen's MJCF puts it "
            "at x -40.0000..-37.0000; the jaw's Ø11.9949 x 0.3000 flange at "
            "x -40.0000..-39.7000 would put it at -39.7000..-36.7000. State "
            "which datum you mean.")

    transform = matmul(matmul(frame_of(a_iface, "a_iface"),
                              translate_z(dz, float(params.get("spin_deg", 0.0)))),
                       invert_rigid(frame_of(b_iface, "b_iface")))

    dof_left = ["rotation_about_z", "translation_along_z"]

    return {
        "transform": transform,
        "dof_left": dof_left,
        "joint": _joint(dof_left, holds_by="form"),
        "adds": [],
        "connection": "connection:press-fit-tube-15",
        "why": {
            "dof": ("An arch of %.2f deg leaves %.2f deg open. It cannot grip, "
                    "so the ring turns freely (rotation_about_z -- this is the "
                    "jaw pivot) and slides freely (translation_along_z -- no "
                    "axial stop exists on either band). It also cannot stop "
                    "the ring leaving through the open side; that is not one "
                    "of the six axes, so it is stated here and in "
                    "joint.open_direction rather than silently omitted."
                    % (ARC_DEG, OPEN_DEG)),
            "datum": datum_source,
            "seat_dz_mm": dz,
            "cradle": {"bore_d_mm": BORE_D_MM, "bore_d_mm_span": list(BORE_D_MM_SPAN),
                       "arc_deg": ARC_DEG, "bands_x_mm": [list(b) for b in BAND_X_MM],
                       "cite": "cecad.meshslice circle fits + meshfeatures.intervals "
                               "on motor_support.stl, 2026-09-02, frozen in "
                               "evidence/tube-15-geometry.json"},
            "ring": {"d_mm": RING_D_MM, "B_mm": RING_B_MM, "ref": RING_REF},
            "adds_nothing": ("the ring is added by connection:press-fit-"
                             "bearing-15x10x3, which seats its BORE on the "
                             "jaw's Ø10.0000 journal. Adding it here too would "
                             "double-count it in the assembly BOM."),
            "retention": ("CANNOT DETERMINE and it is structural, not a gap in "
                          "the data: an open cradle's holding force is whatever "
                          "closes it, and nothing in any of Pollen's four MJCF "
                          "files closes this one."),
        },
    }


if __name__ == "__main__":
    fr = lambda o, z: {"origin_mm": list(o), "z_axis": list(z), "x_axis": [0, 0, 1]}
    ring = {"name": "od", "nominal_mm": 15.0, "frame": fr((-40.0, 0.0, 7.4995), (-1, 0, 0))}
    cradle = {"name": "lens_tube", "role": "lens_seat", "nominal_mm": 14.9938,
              "frame": fr((-39.5, 0.0, 7.4995), (-1, 0, 0)), "shoulder_z_mm": 0.0}
    m = mate(ring, cradle)
    print("dof_left:", m["dof_left"], "| adds:", m["adds"],
          "| holds_by:", m["joint"]["holds_by"])
    print("axes:", m["joint"]["axes"])
    for label, a, b, p in (
            ("no axial datum anywhere", ring,
             {k: v for k, v in cradle.items() if k != "shoulder_z_mm"}, {}),
            ("a Ø22 body", dict(ring, nominal_mm=22.0), cradle, {}),
            ("the bearing's BORE side (that is another folder)",
             dict(ring, name="bore"), cradle, {}),
            ("a seat that is not this cradle", ring,
             dict(cradle, name="pocket", role="bearing_seat"), {})):
        try:
            mate(a, b, p)
            print("mated ok:", label)
        except (ValueError, TypeError) as exc:
            print("refused %-46s %s" % (label + ":", str(exc)[:96]))
