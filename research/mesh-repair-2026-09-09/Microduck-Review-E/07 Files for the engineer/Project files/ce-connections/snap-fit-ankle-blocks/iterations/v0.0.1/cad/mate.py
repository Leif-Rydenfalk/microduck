"""connection:snap-fit-ankle-blocks -- drop the ankle's two blocks into the foot.

Contract (TRIAD.md, ce-connections section):

    def mate(a_iface, b_iface, params=None) -> dict
        keys: transform (4x4 row-major list), dof_left, joint, adds

PURE PYTHON MATH. No `import FreeCAD` at module top, ever. Shaped after
ce-connections/press-fit-bearing-15x10x3; the frame arithmetic is
deliberately duplicated into each connection folder (TRIAD.md line 51).

WHAT THIS JOINT IS, measured 2026-09-02 and frozen in
evidence/ankle-blocks-fit.json:

    the blocks   ankle_left.stl, two spigots x 34.1000..39.1000 and
                 60.9000..65.9000 (5.0000 mm each, 26.8000 mm apart), each a
                 pair of 1.5000 mm ribs at y 31.6630..33.1630 and
                 34.1630..35.6630 with a 1.0000 mm gap -- envelope 4.0000 mm.
    the pockets  foot_left.stl, x 34.0000..39.2000 and 60.8000..66.0000
                 (5.2000 mm), y 31.5630..35.7630 (4.2000 mm), OPEN top to
                 bottom in z.
    the fit      0.1000 mm PER SIDE on both axes. A clearance.
    the cradle   the ankle's R16.3018-16.3058 under-hull on the foot's R16.3
                 end ledges, coaxial with the ankle axis to 0.007-0.011 mm.

NOTHING SNAPS. No undercut, barb, lip or lead-in is on either side, a
through-pocket has no lip for a barb to pass, and a 0.1000 mm clearance
cannot snap into anything. `snap-fit` is the slug the parts' `accepts`
lists already carried; the geometry is a two-spigot LOCATION pair, and the
foot is retained by the single M2 at (x 50.0000, y 4.5020) through
connection:threaded-m2. mate() therefore returns adds=[] and says so, and
REFUSES a params['snap_force_N'] rather than let a number in for a feature
that does not exist.

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
BLOCK_X_MM = ((34.1, 39.1), (60.9, 65.9))
BLOCK_LEN_X_MM = 5.0
BLOCK_LEN_Y_MM = 4.0
BLOCK_SPACING_MM = 26.8
POCKET_X_MM = ((34.0, 39.2), (60.8, 66.0))
POCKET_LEN_X_MM = 5.2
POCKET_LEN_Y_MM = 4.2
CLEARANCE_PER_SIDE_MM = 0.1
CRADLE_R_MM = 16.3018
RETAINED_BY = "connection:threaded-m2"

BLOCK_NAMES = ("foot_blocks", "ankle_blocks", "blocks", "spigots")
POCKET_NAMES = ("ankle_cradle", "block_pockets", "pockets", "seat")


def translate_z(dz_mm, flip=False):
    """No spin: a PAIR of rectangular spigots 26.8000 mm apart has exactly one
    seating rotation, plus the 180 deg flip that swaps heel for toe -- and that
    flip is a different assembly, not a free parameter."""
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
        raise ValueError("connection:snap-fit-ankle-blocks: connection.json "
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
                "connection:snap-fit-ankle-blocks mate() returned dof_left "
                "token %r, not one of the six axes and not in _AXIS_OF -- an "
                "unnamed token reads as a WELD that solves silently." % (tok,))
        axes[ent] = declared.get(ent) if declared.get(ent) in ("free", "limited") else "free"
    j["axes"] = axes
    j["couples"] = [dict(c) for c in (j.get("couples") or [])]
    j["dof_left"] = list(dof_left)
    j.update(over)
    return j


def mate(a_iface, b_iface, params=None):
    """Seat the ankle's block pair (a_iface) in the foot's pocket pair (b_iface).

    a_iface -- the BLOCKS: name 'foot_blocks'/'ankle_blocks'/'blocks'/
               'spigots', or role 'spigot_pair'. Frame origin on the block
               root plane, +z out of the pockets.
    b_iface -- the POCKETS: name 'ankle_cradle'/'block_pockets'/'pockets'/
               'seat', or role 'seat'. Same frame convention.
    params  -- {"seat_dz_mm": float (default 0.0 -- the cradle datum: the
                              ankle's R16.3 hull landing on the foot's R16.3
                              end ledges. THIS joint has a real datum, the
                              cylinder, so 0.0 is a measurement),
                "flip": bool (default False -- heel for toe, a different
                              assembly)}
                "snap_force_N" is REFUSED: nothing here snaps.

    Raises when a snap force is passed, when the pair spacing disagrees, or
    when either interface carries no frame.
    """
    params = dict(params or {})
    if "snap_force_N" in params or "snap" in params:
        raise ValueError(
            "params['snap_force_N'] is not a parameter of this joint and no "
            "number will be accepted for it. MEASURED on both meshes: no "
            "undercut, barb, lip or lead-in exists on either side, the pockets "
            "are open top to bottom in z (so there is no lip for a barb to "
            "pass), and the fit is a %.4f mm per-side CLEARANCE. What retains "
            "the foot is %s -- put the number there."
            % (CLEARANCE_PER_SIDE_MM, RETAINED_BY))

    a_name, a_role = _field(a_iface, "name"), _field(a_iface, "role")
    b_name, b_role = _field(b_iface, "name"), _field(b_iface, "role")
    if a_name not in BLOCK_NAMES and a_role != "spigot_pair":
        raise ValueError("a_iface must be the ankle's block pair: name one of "
                         "%s, or role 'spigot_pair'; got name %r role %r"
                         % (", ".join(repr(n) for n in BLOCK_NAMES), a_name, a_role))
    if b_name not in POCKET_NAMES and b_role != "seat":
        raise ValueError("b_iface must be the foot's pocket pair: name one of "
                         "%s, or role 'seat'; got name %r role %r"
                         % (", ".join(repr(n) for n in POCKET_NAMES), b_name, b_role))

    sp_a = _field(a_iface, "spacing_mm", "block_spacing_mm")
    sp_b = _field(b_iface, "spacing_mm", "pocket_spacing_mm")
    for side, sp in (("a_iface", sp_a), ("b_iface", sp_b)):
        if sp is not None and abs(float(sp) - BLOCK_SPACING_MM) > 0.5:
            raise ValueError(
                "%s states a pair spacing of %r mm; this joint's pair is "
                "%.4f mm apart (block roots x 34.1000 and 60.9000). A pair at "
                "another pitch is another joint." % (side, sp, BLOCK_SPACING_MM))
    if sp_a is not None and sp_b is not None and abs(float(sp_a) - float(sp_b)) > 0.05:
        raise ValueError(
            "a_iface spacing %r and b_iface spacing %r differ by more than "
            "0.05 mm. Two spigots at one pitch in two pockets at another do "
            "not both seat -- the pair is what makes this an anti-rotation "
            "feature, and a mismatch destroys it." % (sp_a, sp_b))

    dz = float(params.get("seat_dz_mm", 0.0))
    datum_source = (
        "params['seat_dz_mm']" if params.get("seat_dz_mm") is not None else
        "the CRADLE datum: the ankle's R%.4f under-hull landing on the foot's "
        "R16.3 end ledges (x 32.9000..34.1500 and 65.8500..67.1000). Unlike a "
        "press fit this joint HAS a self-locating datum -- a cylinder on a "
        "cylinder -- so 0.0 here is a measurement, not an invented default. "
        "The blocks do not set the height: their pockets are through."
        % CRADLE_R_MM)

    transform = matmul(matmul(frame_of(a_iface, "a_iface"),
                              translate_z(dz, bool(params.get("flip", False)))),
                       invert_rigid(frame_of(b_iface, "b_iface")))

    return {
        "transform": transform,
        "dof_left": [],
        "joint": _joint([], holds_by="form"),
        "adds": [],
        "connection": "connection:snap-fit-ankle-blocks",
        "why": {
            "dof": ("Two rectangular spigots %.4f mm apart in matching pockets "
                    "remove every rotation and both cross-axis translations; "
                    "the cylindrical cradle takes the third. Nothing is left "
                    "FREE -- but tz is locked only once the M2 is driven, "
                    "because the pockets are open top to bottom. That "
                    "qualification is in joint.axes_cannot_determine."
                    % BLOCK_SPACING_MM),
            "datum": datum_source,
            "seat_dz_mm": dz,
            "flip": bool(params.get("flip", False)),
            "fit": {"clearance_per_side_mm": CLEARANCE_PER_SIDE_MM,
                    "block_mm": [BLOCK_LEN_X_MM, BLOCK_LEN_Y_MM],
                    "pocket_mm": [POCKET_LEN_X_MM, POCKET_LEN_Y_MM],
                    "cite": "cecad.meshfeatures.intervals on both meshes, "
                            "2026-09-02, frozen in "
                            "evidence/ankle-blocks-fit.json"},
            "adds_nothing": ("the M2 that actually retains the foot belongs to "
                             "%s on its own joint row; adding it here would "
                             "double-count it" % RETAINED_BY),
            "retention": ("NOT THIS JOINT'S. It transmits shear and nothing "
                          "else: the pockets are open in z and no undercut "
                          "exists. %s carries the retention." % RETAINED_BY),
        },
    }


if __name__ == "__main__":
    fr = lambda o: {"origin_mm": list(o), "z_axis": [0, 0, 1], "x_axis": [1, 0, 0]}
    blocks = {"name": "foot_blocks", "role": "spigot_pair", "spacing_mm": 26.8,
              "frame": fr((34.1, 31.663, -21.342))}
    pockets = {"name": "ankle_cradle", "role": "seat", "spacing_mm": 26.8,
               "frame": fr((34.0, 31.563, -21.342))}
    m = mate(blocks, pockets)
    print("dof_left:", m["dof_left"], "| adds:", m["adds"],
          "| holds_by:", m["joint"]["holds_by"])
    print("tz caveat:", m["joint"]["axes_cannot_determine"]["tz"][:70], "...")
    for label, a, b, p in (
            ("a snap force on a joint with no snap", blocks, pockets,
             {"snap_force_N": 12.0}),
            ("a pair at another pitch", blocks, dict(pockets, spacing_mm=40.0), {}),
            ("pitches 0.4 mm apart", dict(blocks, spacing_mm=27.2), pockets, {}),
            ("the pockets passed as the blocks", pockets, pockets, {}),
            ("no frame", {"name": "foot_blocks"}, pockets, {})):
        try:
            mate(a, b, p)
            print("mated ok:", label)
        except (ValueError, TypeError) as exc:
            print("refused %-40s %s" % (label + ":", str(exc)[:88]))
