"""connection:snap-fit-roller-axle -- snap the foot's barbed fingers over the ankle plate.

Contract (TRIAD.md, ce-connections section):

    def mate(a_iface, b_iface, params=None) -> dict
        keys: transform (4x4 row-major list), dof_left, joint, adds

PURE PYTHON MATH. No `import FreeCAD` at module top, ever. Shaped after
ce-connections/press-fit-bearing-15x10x3; the frame arithmetic is
deliberately duplicated into each connection folder (TRIAD.md line 51).

WHAT THIS JOINT IS, measured 2026-09-02 and frozen in
evidence/roller-slot-fit.json:

    the fingers  foot_left.stl, two cantilevers running along x
                 45.0000..55.0000 (10.0000 mm) at y ~0.5 and ~36.5, topped
                 at z -12.3419. Inner gap by height:
                     lead-in    36.0890 (z -12.3500) -> 34.7000 (-13.4000)
                                0.6945 mm per side over 1.0500 mm, 33.47 deg
                     barb land  34.7000, z -13.4000..-14.0000 (0.6000 tall)
                     pocket     36.7000, from z -14.5000 down
                 barbs 1.0000 mm proud per side.
    the plate    ankle_left.stl, y 0.1632..36.6632 = 36.5000 mm wide at
                 z -15.5000..-15.0000, narrowing to 33.7000 above -14.5000.
    the fit      0.1000 mm per side in the pocket; 0.9000 mm of deflection
                 per finger to pass the barb; 0.9000 mm of overhang after.

IT IS NOT A ROLLER MOUNT, whatever the slug says. roller_blade, tire and
rim appear in exactly one of Pollen's four MJCF files, and that file
contains no foot or sole geom at all -- it swaps the whole foot assembly
and the ankle too (ankle_l_v1 / ankle_r_v1). The slug is kept because both
foot parts already `accept` it; the claim is corrected in the part folder.

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
FINGER_X_MM = (45.0, 55.0)
FINGER_RUN_MM = 10.0
TOP_Z_MM = -12.3419
LEAD_IN_GAP_MM = 36.089
BARB_LAND_GAP_MM = 34.7
BARB_LAND_Z_MM = (-14.0, -13.4)
BARB_PROUD_PER_SIDE_MM = 1.0
POCKET_GAP_MM = 36.7
PLATE_WIDTH_MM = 36.5
CLEARANCE_PER_SIDE_MM = 0.1
DEFLECTION_PER_FINGER_MM = 0.9
LEAD_IN_HALF_ANGLE_DEG = 33.47

FINGER_NAMES = ("roller_slot", "snap_fingers", "fingers")
PLATE_NAMES = ("foot_snap_plate", "snap_plate", "plate")


def translate_z(dz_mm, flip=False):
    """No spin: two fingers 10.0000 mm long running along x accept the plate
    one way, or flipped 180 deg with heel for toe -- a different assembly."""
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
        raise ValueError("connection:snap-fit-roller-axle: connection.json "
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
                "connection:snap-fit-roller-axle mate() returned dof_left "
                "token %r, not one of the six axes and not in _AXIS_OF -- an "
                "unnamed token reads as a WELD that solves silently." % (tok,))
        axes[ent] = declared.get(ent) if declared.get(ent) in ("free", "limited") else "free"
    j["axes"] = axes
    j["couples"] = [dict(c) for c in (j.get("couples") or [])]
    j["dof_left"] = list(dof_left)
    j.update(over)
    return j


def mate(a_iface, b_iface, params=None):
    """Snap the finger pair (a_iface) over the plate (b_iface).

    a_iface -- the FINGERS: name 'roller_slot'/'snap_fingers'/'fingers', or
               role 'snap'. Frame origin on the barb land plane, on the pair
               centreline, +z along the insertion direction.
    b_iface -- the PLATE: name 'foot_snap_plate'/'snap_plate'/'plate', or
               role 'snap_plate'. Same convention.
    params  -- {"seat_dz_mm": float (default 0.0 -- the BARB SHOULDER datum:
                              home is where the plate's shoulder meets the
                              barb underside. This joint HAS a hard datum,
                              so 0.0 is a measurement),
                "flip": bool (default False -- heel for toe),
                "state": "home" (default) | "passing" -- 'passing' returns
                              the joint mid-insertion, with tz free and the
                              deflection stated}

    Raises when the plate is wider than the pocket, when it is narrower than
    the barb land (nothing to capture), or when either frame is missing.
    """
    params = dict(params or {})
    a_name, a_role = _field(a_iface, "name"), _field(a_iface, "role")
    b_name, b_role = _field(b_iface, "name"), _field(b_iface, "role")
    if a_name not in FINGER_NAMES and a_role != "snap":
        raise ValueError("a_iface must be the foot's finger pair: name one of "
                         "%s, or role 'snap'; got name %r role %r"
                         % (", ".join(repr(n) for n in FINGER_NAMES), a_name, a_role))
    if b_name not in PLATE_NAMES and b_role != "snap_plate":
        raise ValueError("b_iface must be the ankle's plate: name one of %s, "
                         "or role 'snap_plate'; got name %r role %r"
                         % (", ".join(repr(n) for n in PLATE_NAMES), b_name, b_role))

    pocket = float(_field(a_iface, "pocket_gap_mm") or POCKET_GAP_MM)
    land = float(_field(a_iface, "barb_land_gap_mm") or BARB_LAND_GAP_MM)
    plate = _field(b_iface, "width_mm", "plate_width_mm")
    if plate is None:
        raise ValueError("b_iface states no width_mm -- CANNOT DETERMINE "
                         "whether this plate is captured, clears the barbs, or "
                         "will not go in at all. The slug is not a measurement.")
    plate = float(plate)
    if plate > pocket:
        raise ValueError(
            "the plate is %.4f mm across and the pocket behind the barbs is "
            "%.4f mm: it does not fit even once it is past. Interference of "
            "%.4f mm total, and nothing here is designed to be pressed."
            % (plate, pocket, plate - pocket))
    if plate <= land:
        raise ValueError(
            "the plate is %.4f mm across and the barb land is %.4f mm: it "
            "passes straight through and NOTHING IS CAPTURED. A snap that does "
            "not deflect is a clearance hole. (The ankle is 33.7000 mm wide "
            "above its shoulder, which is exactly why that part of it clears.)"
            % (plate, land))

    state = params.get("state", "home")
    if state not in ("home", "passing"):
        raise ValueError("params['state'] must be 'home' or 'passing', got %r"
                         % (state,))

    dz = float(params.get("seat_dz_mm", 0.0))
    datum_source = (
        "params['seat_dz_mm']" if params.get("seat_dz_mm") is not None else
        "the BARB SHOULDER datum: home is where the plate's shoulder meets the "
        "barb underside (barb land z %.4f..%.4f, plate shoulder between "
        "z -15.0000 and -14.5000). This joint has a hard stop, so 0.0 here is "
        "a measurement." % BARB_LAND_Z_MM)

    transform = matmul(matmul(frame_of(a_iface, "a_iface"),
                              translate_z(dz, bool(params.get("flip", False)))),
                       invert_rigid(frame_of(b_iface, "b_iface")))

    deflection = (plate - land) / 2.0
    overhang = (plate - land) / 2.0
    dof_left = ["translation_along_z"] if state == "passing" else []

    return {
        "transform": transform,
        "dof_left": dof_left,
        "joint": _joint(dof_left, holds_by="form"),
        "adds": [],
        "connection": "connection:snap-fit-roller-axle",
        "why": {
            "dof": ("home: nothing free -- the pocket takes the plate at %.4f mm "
                    "per side and the barbs close tz. passing: tz free, which "
                    "IS the assembly move."
                    % ((pocket - plate) / 2.0)),
            "state": state,
            "datum": datum_source,
            "seat_dz_mm": dz,
            "flip": bool(params.get("flip", False)),
            "snap": {"deflection_per_finger_mm": round(deflection, 4),
                     "overhang_per_side_mm": round(overhang, 4),
                     "clearance_per_side_mm": round((pocket - plate) / 2.0, 4),
                     "lead_in_half_angle_deg": LEAD_IN_HALF_ANGLE_DEG,
                     "finger_run_mm": FINGER_RUN_MM,
                     "cite": "cecad.meshfeatures.intervals on both meshes, "
                             "2026-09-02, frozen in "
                             "evidence/roller-slot-fit.json"},
            "not_a_roller": ("roller_blade, tire and rim appear in exactly one "
                             "of Pollen's four MJCF files, and that file has no "
                             "foot or sole geom at all. What this snap captures "
                             "is the ANKLE's 36.5000 mm plate."),
            "force": ("CANNOT DETERMINE. Deflection (%.4f mm per finger) and "
                      "the finger section are measured; the printed PLA's "
                      "modulus and permissible strain at this layer "
                      "orientation are in no file here, and a cantilever "
                      "formula fed a guessed modulus would be a number with no "
                      "source. Push one home on a gauge." % deflection),
        },
    }


if __name__ == "__main__":
    fr = lambda o: {"origin_mm": list(o), "z_axis": [0, 0, 1], "x_axis": [1, 0, 0]}
    fingers = {"name": "roller_slot", "role": "snap", "pocket_gap_mm": 36.7,
               "barb_land_gap_mm": 34.7, "frame": fr((50.0, 18.413, -13.7))}
    plate = {"name": "foot_snap_plate", "role": "snap_plate", "width_mm": 36.5,
             "frame": fr((50.0, 18.413, -14.75))}
    m = mate(fingers, plate)
    print("home     dof_left:", m["dof_left"], "| snap:", m["why"]["snap"])
    print("passing  dof_left:", mate(fingers, plate, {"state": "passing"})["dof_left"])
    for label, a, b, p in (
            ("a plate wider than the pocket", fingers, dict(plate, width_mm=38.0), {}),
            ("a plate that clears the barbs", fingers, dict(plate, width_mm=33.7), {}),
            ("a plate with no width", fingers, {k: v for k, v in plate.items()
                                                if k != "width_mm"}, {}),
            ("a nonsense state", fingers, plate, {"state": "wobbling"}),
            ("the plate passed as the fingers", plate, plate, {})):
        try:
            mate(a, b, p)
            print("mated ok:", label)
        except (ValueError, TypeError) as exc:
            print("refused %-34s %s" % (label + ":", str(exc)[:92]))
