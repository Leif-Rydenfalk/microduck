"""connection:press-fit-sole-foot -- push the TPU sole onto the printed foot cap.

Contract (TRIAD.md, ce-connections section):

    def mate(a_iface, b_iface, params=None) -> dict
        keys: transform (4x4 row-major list), dof_left, joint, adds

PURE PYTHON MATH. No `import FreeCAD` at module top, ever. Shaped after
ce-connections/press-fit-bearing-15x10x3; the frame arithmetic is
deliberately duplicated into each connection folder (TRIAD.md line 51).

WHAT THIS JOINT IS, measured 2026-09-02 and frozen in
evidence/sole-foot-fit.json:

    the plug     part:microduck-foot-left 'sole_skirt' -- a vertical prism
                 x 31.6000..68.4000, y -9.9000..39.9000 (36.8000 x 49.8000),
                 identical at every z section from -18.342 to -24.0, under a
                 flange that overhangs the sole rim.
    the socket   part:microduck-sole-left 'foot_socket' -- the same prism as
                 a cavity. Wall mean 2.0165 mm, floor 2.000 +/- 0.001 mm,
                 depth 7.9170 (toe) .. 10.6550 (heel) mm.
    the fit      ZERO. 150 gaps measured on 75 caliper lines run through both
                 meshes: -0.0020 .. +0.0020 mm, mean -0.000007 mm.

A PRISM IS NOT A CYLINDER, and that changes the contract in one visible way:
`spin_deg` does not exist here. A rectangular plug has exactly one seating
rotation about its axis (plus the 180 deg flip, which puts the toe at the
heel), so mate() takes no spin and REFUSES one if it is passed. Where the
bearing folders ask "how far along the axis", this one asks nothing: the
plug bottoms out, and `seat_dz_mm` defaults to 0.0 at the rim datum both
interfaces already declare (z -18.3420 in the shared ankle-group frame).

Units: mm and degrees.
"""

import json as _json
import math
import os as _os

SECTION_MM = (36.8, 49.8)
SECTION_X_MM = (31.6, 68.4)
SECTION_Y_MM = (-9.9, 39.9)
RIM_Z_MM = -18.3419
DEPTH_MM = (7.917, 10.655)
CLEARANCE_MM = 0.0
CLEARANCE_SPAN_MM = (-0.002, 0.002)

PLUG_NAMES = ("sole_skirt", "skirt", "plug")
SOCKET_NAMES = ("foot_socket", "socket", "cavity")


def _field(iface, key, *aliases):
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


def translate_z(dz_mm, flip=False):
    """No spin: a rectangular plug has one seating rotation, and its 180 deg
    flip (toe at the heel) is a DIFFERENT assembly, not a free parameter."""
    if flip:
        return [[-1.0, 0.0, 0.0, 0.0], [0.0, -1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, float(dz_mm)], [0.0, 0.0, 0.0, 1.0]]
    return [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0],
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
        raise ValueError("connection:press-fit-sole-foot: connection.json "
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
                "connection:press-fit-sole-foot mate() returned dof_left token "
                "%r, not one of the six axes and not in _AXIS_OF -- an unnamed "
                "token reads as a WELD that solves silently." % (tok,))
        axes[ent] = declared.get(ent) if declared.get(ent) in ("free", "limited") else "free"
    j["axes"] = axes
    j["couples"] = [dict(c) for c in (j.get("couples") or [])]
    j["dof_left"] = list(dof_left)
    j.update(over)
    return j


def mate(a_iface, b_iface, params=None):
    """Seat the sole socket (b_iface) onto the foot's plug (a_iface).

    a_iface -- the PLUG: name 'sole_skirt'/'skirt'/'plug', or role 'skirt'.
               Frame origin on the rim plane, +z out of the socket.
    b_iface -- the SOCKET: name 'foot_socket'/'socket'/'cavity', or role
               'socket'. Same frame convention.
    params  -- {"seat_dz_mm": float (default 0.0 -- the rim datum BOTH
                              interfaces already declare; unlike a bearing
                              seat this joint HAS a self-locating datum, so
                              a default here is a measurement, not a guess),
                "flip": bool (default False -- the 180 deg assembly, toe at
                              the heel; it is a different build, not a spin)}
                "spin_deg" is REFUSED: a rectangular plug has no free spin.

    Raises when the sections disagree, when a spin is passed, or when either
    interface carries no frame.
    """
    params = dict(params or {})
    if "spin_deg" in params:
        raise ValueError(
            "params['spin_deg'] is not a parameter of this joint. The plug is "
            "a %s x %s mm RECTANGLE, not a circle: it seats one way, or "
            "flipped 180 deg with the toe at the heel, and that flip is a "
            "different assembly. Pass params['flip']=True if you mean it."
            % SECTION_MM)

    a_name, a_role = _field(a_iface, "name"), _field(a_iface, "role")
    b_name, b_role = _field(b_iface, "name"), _field(b_iface, "role")
    if a_name not in PLUG_NAMES and a_role != "skirt":
        raise ValueError("a_iface must be the foot's plug: name one of %s, or "
                         "role 'skirt'; got name %r role %r"
                         % (", ".join(repr(n) for n in PLUG_NAMES), a_name, a_role))
    if b_name not in SOCKET_NAMES and b_role != "socket":
        raise ValueError("b_iface must be the sole's socket: name one of %s, "
                         "or role 'socket'; got name %r role %r"
                         % (", ".join(repr(n) for n in SOCKET_NAMES), b_name, b_role))

    # the sections must be the same rectangle, or this is not this joint
    sects = {}
    for iface, side in ((a_iface, "a_iface"), (b_iface, "b_iface")):
        s = _field(iface, "section_mm", "size_mm")
        if s is not None:
            s = sorted(float(v) for v in s)
            sects[side] = s
    want = sorted(SECTION_MM)
    for side, s in sects.items():
        if max(abs(s[i] - want[i]) for i in range(2)) > 0.5:
            raise ValueError(
                "%s states section %s mm; connection:press-fit-sole-foot joins "
                "the %s x %s mm foot prism only. Another size is another "
                "folder." % (side, s, SECTION_MM[0], SECTION_MM[1]))
    if len(sects) == 2 and max(abs(sects["a_iface"][i] - sects["b_iface"][i])
                               for i in range(2)) > 0.05:
        raise ValueError(
            "a_iface section %s and b_iface section %s differ by more than "
            "0.05 mm. The reference pair is coincident to 0.002 mm (150 gaps "
            "measured on 75 caliper lines); a pair that does not agree at that "
            "scale is not this joint."
            % (sects["a_iface"], sects["b_iface"]))

    dz = float(params.get("seat_dz_mm", 0.0))
    datum_source = (
        "params['seat_dz_mm']" if params.get("seat_dz_mm") is not None else
        "the RIM DATUM both interfaces declare (z %.4f in the shared ankle-group "
        "frame, the sole's own bbox maximum). This joint self-locates: the plug "
        "bottoms on the socket floor and the flange lands on the rim, so 0.0 "
        "here is a measurement, not the invented default that "
        "connection:press-fit-bearing-15x10x3 refuses." % RIM_Z_MM)

    transform = matmul(matmul(frame_of(a_iface, "a_iface"),
                              translate_z(dz, bool(params.get("flip", False)))),
                       invert_rigid(frame_of(b_iface, "b_iface")))

    return {
        "transform": transform,
        "dof_left": [],
        "joint": _joint([], holds_by="friction"),
        "adds": [],
        "connection": "connection:press-fit-sole-foot",
        "why": {
            "dof": ("A prism in a prism leaves nothing free: the rectangular "
                    "section locks both cross-axis translations and all three "
                    "rotations by FORM, and the plug bottoming plus the flange "
                    "landing lock the last translation."),
            "datum": datum_source,
            "seat_dz_mm": dz,
            "flip": bool(params.get("flip", False)),
            "section_mm": list(SECTION_MM),
            "clearance": {"mm": CLEARANCE_MM, "span_mm": list(CLEARANCE_SPAN_MM),
                          "cite": "150 gaps on 75 cecad.meshfeatures.intervals "
                                  "caliper lines through both meshes, "
                                  "2026-09-02, frozen in "
                                  "evidence/sole-foot-fit.json"},
            "depth_mm": {"toe": DEPTH_MM[0], "heel": DEPTH_MM[1],
                         "why": "the outer floor slopes 0.087 toe-to-heel and "
                                "the inner floor follows it at a constant "
                                "2.000 +/- 0.001 mm of TPU"},
            "adds_nothing": ("no screw, clip or adhesive exists on either mesh; "
                             "the ankle group's single M2 hangs the FOOT from "
                             "the ankle and does not pass through the sole"),
            "retention": ("CANNOT DETERMINE. A zero modelled clearance in a TPU "
                          "socket over a printed PLA plug is an interference of "
                          "whatever the two processes deliver. mate() places "
                          "geometry; it does not certify grip. Pull a real sole "
                          "off on a gauge."),
        },
    }


if __name__ == "__main__":
    fr = lambda o: {"origin_mm": list(o), "z_axis": [0, 0, 1], "x_axis": [1, 0, 0]}
    plug = {"name": "sole_skirt", "role": "skirt", "section_mm": [36.8, 49.8],
            "frame": fr((50.0, 15.0, -18.342))}
    sock = {"name": "foot_socket", "role": "socket", "section_mm": [36.8, 49.8],
            "frame": fr((50.0, 15.0, -18.342))}
    m = mate(plug, sock)
    print("dof_left:", m["dof_left"], "| adds:", m["adds"],
          "| holds_by:", m["joint"]["holds_by"], "| axes:", m["joint"]["axes"])
    print("flipped:", mate(plug, sock, {"flip": True})["why"]["flip"])
    for label, a, b, p in (
            ("a spin on a rectangle", plug, sock, {"spin_deg": 90.0}),
            ("a different footprint", plug, dict(sock, section_mm=[30.0, 40.0]), {}),
            ("sections that disagree by 0.6 mm", dict(plug, section_mm=[37.4, 49.8]),
             sock, {}),
            ("the socket passed as the plug", sock, sock, {}),
            ("no frame", {"name": "sole_skirt", "section_mm": [36.8, 49.8]}, sock, {})):
        try:
            mate(a, b, p)
            print("mated ok:", label)
        except (ValueError, TypeError) as exc:
            print("refused %-36s %s" % (label + ":", str(exc)[:92]))
