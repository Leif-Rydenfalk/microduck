#!/usr/bin/env python3
"""measure.py — every Microduck cable length, MEASURED off the assembly placements.

    CE_PARTS_ROOT=ce-parts python3 wiring/measure.py        # writes cables.json, drop.json, CABLES.md

Inputs (nothing else is read):
  ce-assemblies/microduck/current/placements.json   every part's world pose, mm, zero pose
  ce-assemblies/microduck/current/joints.json       the 14 hinges: origin, axis, range
  ce-parts/xl330-m288-t/current/cad/part.py         the servo's mesh frame and the
                                                    connector pockets, measured off Pollen's mesh
  reference/pollen-microduck-rl/assets/*.stl        bounding boxes, to put a board's
                                                    centroid where its mesh origin is not

What a length IS here, stated once:
  A cable length is a ROUTE FLOOR: the straight line from connector A to
  connector B, bent only through the origin of every hinge the cable crosses
  (a polyline A -> hinge -> ... -> B). Because a hinge origin sits on its own
  axis, that polyline is the same length in every pose of the joint, so it is
  a floor over the whole range. A real loom is longer: it goes AROUND the
  servo body and the bearing, not through the axis, and it carries a service
  loop. Nothing here is that loom. A PASS on a floor is necessary, not
  sufficient.

  SLACK RULE (the only non-measured term, and it is stated, not hidden):
  slack_mm = sum over crossed hinges of  span_rad x R_BYPASS, with
  R_BYPASS = 10.0 mm = half the XL330's 20 mm width (part.py BODY_Y), i.e.
  the cable is assumed to pass the axis at the servo's flank, so a full sweep
  of the joint's range pays out an arc of that radius. cable_mm =
  ceil5(floor + slack). ROBOTIS' stock cable lengths are not on any fetched
  vendor page (part:xl330-m288-t connector.x3p), so no "nearest stock length"
  is claimed.

Where a device's connector is:
  XL330: two JST EH 3-pin sockets in pockets on the +/-y side faces, opening
  at y = +/-10 (mesh frame, part.py POCKET_*; the XL,XC-330.pdf side views
  show them). The cable exit point used is the pocket centre on the side
  face: (6.85, +/-10.0, -9.0) mm in the mesh frame, transformed by the
  placement. The side (+y or -y) is chosen per hop as the one giving the
  shorter floor — a servo has one socket on each flank and a chain uses
  both.
  HAT, Radxa, speaker, battery: connector positions are UNPUBLISHED (the
  HAT's PCB is not public; the battery contact drawing does not exist). The
  reference point is the mesh CENTROID (bbox centre through the placement),
  and every such row says "centroid" in `ref`. The mic has no mesh: null.
  IMU / ToF / camera: the MJCF sites (docs/ELECTRONICS-AND-SOFTWARE.md).

Voltage drop: cecad.harness.check_drop over a hand-built Harness per hop —
the tool's own arithmetic (ASTM B258 diameter, IEC 60228 copper), with the
bases stated in the call. cecad.harness.wire(asm, a, b) could not be used:
it resolves ELECTRICAL connectors declared on the parts, and
part:xl330-m288-t declares none (component.json: "cad/interfaces.json still
declares no interfaces"). That is a tool gap (P11) named in README.md, not
worked around by typing a length.
"""
import json
import math
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WS = os.path.dirname(os.path.dirname(ROOT))
sys.path.insert(0, os.path.join(WS, "ce-cad"))

ASM = os.path.join(ROOT, "ce-assemblies", "microduck", "current")
MESH = os.path.join(ROOT, "reference", "pollen-microduck-rl", "assets")

R_BYPASS_MM = 10.0          # part.py BODY_Y = (-10, 10): half the servo width
CONN_LOCAL = (6.85, 10.0, -9.0)   # pocket centre on the +y side face, mesh frame
CONN_BASIS = ("XL330 mesh frame (part.py): pocket x 2.2..11.5, y 6..10 to the "
              "face, z -14.3..-3.7 -> cable exit at the side face (6.85, "
              "+/-10.0, -9.0); XL,XC-330.pdf side views show the two sockets")


# ---------------------------------------------------------------------------
# geometry helpers
# ---------------------------------------------------------------------------
def qrot(q, v):
    """Rotate v by unit quaternion q = (w, x, y, z)."""
    w, x, y, z = q
    vx, vy, vz = v
    # q * v * q^-1, expanded
    tx = 2 * (y * vz - z * vy)
    ty = 2 * (z * vx - x * vz)
    tz = 2 * (x * vy - y * vx)
    return (vx + w * tx + (y * tz - z * ty),
            vy + w * ty + (z * tx - x * tz),
            vz + w * tz + (x * ty - y * tx))


def add(a, b):
    return tuple(p + q for p, q in zip(a, b))


def dist(a, b):
    return math.sqrt(sum((p - q) ** 2 for p, q in zip(a, b)))


def polyline(pts):
    return sum(dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def ceil5(x):
    return int(math.ceil(x / 5.0) * 5)


def stl_bbox_mm(name):
    """Bounding box of a Pollen mesh (metres on disk), in mm, in its own frame."""
    f = os.path.join(MESH, name + ".stl")
    d = open(f, "rb").read()
    n = struct.unpack("<I", d[80:84])[0]
    xs, ys, zs = [], [], []
    for i in range(n):
        o = 84 + i * 50
        for j in range(3):
            x, y, z = struct.unpack("<fff", d[o + 12 + j * 12:o + 24 + j * 12])
            xs.append(x); ys.append(y); zs.append(z)
    s = 1000.0
    return ((min(xs) * s, max(xs) * s), (min(ys) * s, max(ys) * s), (min(zs) * s, max(zs) * s))


def centroid_world(row):
    bb = stl_bbox_mm(row["mesh"])
    c = tuple((lo + hi) / 2.0 for lo, hi in bb)
    return add(tuple(row["world_pos_mm"]), qrot(tuple(row["world_quat_wxyz"]), c))


# ---------------------------------------------------------------------------
# the facts
# ---------------------------------------------------------------------------
P = json.load(open(os.path.join(ASM, "placements.json")))["record"]
J = json.load(open(os.path.join(ASM, "joints.json")))["record"]
ROWS = P["rows"]
JOINT = {r["params"]["joint"]: r["params"] for r in J["rows"]}


def servo_conns(row_i):
    """Both cable-exit points of the XL330 at placements row i, world mm."""
    r = ROWS[row_i]
    assert r["mesh"] == "xl330", (row_i, r["mesh"])
    pos, q = tuple(r["world_pos_mm"]), tuple(r["world_quat_wxyz"])
    plus = add(pos, qrot(q, CONN_LOCAL))
    minus = add(pos, qrot(q, (CONN_LOCAL[0], -CONN_LOCAL[1], CONN_LOCAL[2])))
    return {"+y": plus, "-y": minus}


# device -> (kind, reference points {name: xyz}, basis)
DEV = {}
SERVO_ROW = {34: 39, 33: 43, 32: 34, 31: 29, 30: 28,
             20: 4, 21: 11, 22: 20, 23: 17, 24: 22,
             10: 7, 11: 54, 12: 63, 13: 59, 14: 64}
SERVO_JOINT = {34: "mouth", 33: "head_roll", 32: "head_yaw", 31: "head_pitch", 30: "neck_pitch",
               20: "left_hip_yaw", 21: "left_hip_roll", 22: "left_hip_pitch", 23: "left_knee", 24: "left_ankle",
               10: "right_hip_yaw", 11: "right_hip_roll", 12: "right_hip_pitch", 13: "right_knee", 14: "right_ankle"}
for sid, row in SERVO_ROW.items():
    DEV["id%d" % sid] = {"kind": "xl330", "row": row, "body": ROWS[row]["body"],
                         "pts": servo_conns(row), "ref": "servo side-face socket (" + CONN_BASIS + ")"}

hat_row = next(i for i, r in enumerate(ROWS) if r["mesh"] == "elec_rpi_robot_hat_pcb")
radxa_row = next(i for i, r in enumerate(ROWS) if r["mesh"] == "pcb__raspberry_pi_zero_2_w")
spk_row = next(i for i, r in enumerate(ROWS) if r["mesh"] == "speaker")
bat_row = next(i for i, r in enumerate(ROWS) if r["mesh"] == "np_f970")
locker_row = next(i for i, r in enumerate(ROWS) if r["mesh"] == "banana_pcb_locker")

DEV["hat"] = {"kind": "board", "row": hat_row, "body": ROWS[hat_row]["body"],
              "pts": {"centroid": centroid_world(ROWS[hat_row])},
              "ref": "HAT mesh centroid (bbox centre through the placement) — connector positions unpublished"}
DEV["radxa"] = {"kind": "board", "row": radxa_row, "body": ROWS[radxa_row]["body"],
                "pts": {"centroid": centroid_world(ROWS[radxa_row])},
                "ref": "Radxa mesh centroid — the CSI connector's place on the 65x30 board is at one short edge (Radxa wiki) but not located here"}
DEV["speaker"] = {"kind": "transducer", "row": spk_row, "body": ROWS[spk_row]["body"],
                  "pts": {"centroid": centroid_world(ROWS[spk_row])},
                  "ref": "speaker mesh centroid — terminal side unknown"}
# battery: contacts are at ONE end of the 70.8 mm pack; take the end nearer the banana contact-PCB locker
bat = ROWS[bat_row]
bb = stl_bbox_mm(bat["mesh"])
ends = [add(tuple(bat["world_pos_mm"]), qrot(tuple(bat["world_quat_wxyz"]), (0.0, 0.0, e)))
        for e in (bb[2][0], bb[2][1])]
locker_c = centroid_world(ROWS[locker_row])
bat_end = min(ends, key=lambda e: dist(e, locker_c))
DEV["battery"] = {"kind": "pack", "row": bat_row, "body": bat["body"],
                  "pts": {"contact_end": bat_end},
                  "ref": "the pack's end face nearer the banana_pcb_locker centroid (%.1f, %.1f, %.1f); the NP-F contact "
                         "layout has no vendor drawing (part:np-f550 pinout)" % locker_c}
DEV["banana_pcb"] = {"kind": "board", "row": locker_row, "body": ROWS[locker_row]["body"],
                     "pts": {"centroid": locker_c}, "ref": "banana_pcb_locker mesh centroid (the contact PCB sits in it)"}
DEV["imu200"] = {"kind": "board", "row": None, "body": "trunk_base", "pts": {"site": (-21.0, 0.0, 105.3)},
                 "ref": "MJCF imu site, world (docs/ELECTRONICS-AND-SOFTWARE.md §4.1) — the board's connector is not located"}
DEV["tof"] = {"kind": "sensor", "row": None, "body": "jaw_soft", "pts": {"site": (81.4, 22.4, 249.1)},
              "ref": "MJCF tof site, world (docs §6)"}
DEV["camera"] = {"kind": "sensor", "row": None, "body": "jaw_soft", "pts": {"site": (81.4, 0.0, 251.1)},
                 "ref": "MJCF head_camera site, world (docs §5)"}
DEV["mic"] = {"kind": "transducer", "row": None, "body": None, "pts": {}, "ref": "no mesh, no site: CANNOT DETERMINE"}


# ---------------------------------------------------------------------------
# the cables
# ---------------------------------------------------------------------------
def hinge_pts(names):
    return [tuple(JOINT[n]["world_origin_mm"]) for n in names]


def span_rad(names):
    return sum(math.radians(JOINT[n]["range_deg"][1] - JOINT[n]["range_deg"][0]) for n in names)


def route(a, b, hinges):
    """Best (shortest) polyline a -> hinges -> b over the devices' candidate points."""
    best = None
    for an, ap in DEV[a]["pts"].items():
        for bn, bp in DEV[b]["pts"].items():
            L = polyline([ap] + hinge_pts(hinges) + [bp])
            if best is None or L < best[0]:
                best = (L, an, ap, bn, bp)
    return best


# The Dynamixel daisy chain, in physical order. Hinges = every MJCF hinge on
# the kinematic path between the two devices' bodies (joints.json parent/child).
CHAIN = [
    ("hat", "id34", [], "same body jaw_soft"),
    ("id34", "id33", [], "same body jaw_soft"),
    ("id33", "id32", ["head_roll"], "jaw_soft -> yaw_roll_motion"),
    ("id32", "id31", ["head_yaw", "head_pitch"], "yaw_roll_motion -> neck_pitch -> neck"),
    ("id31", "id30", [], "same body neck"),
    ("id30", "imu200", ["neck_pitch"], "neck -> trunk_base"),
    ("imu200", "id20", [], "same body trunk_base"),
    ("id20", "id21", ["left_hip_yaw"], "trunk_base -> yaw2roll"),
    ("id21", "id22", ["left_hip_roll", "left_hip_pitch"], "yaw2roll -> hip_l -> upper_leg_left"),
    ("id22", "id23", [], "same body upper_leg_left"),
    ("id23", "id24", ["left_knee"], "upper_leg_left -> leg"),
    ("imu200", "id10", [], "same body trunk_base"),
    ("id10", "id11", ["right_hip_yaw"], "trunk_base -> bearing_roll"),
    ("id11", "id12", ["right_hip_roll", "right_hip_pitch"], "bearing_roll -> hip_l_2 -> upper_leg_right"),
    ("id12", "id13", [], "same body upper_leg_right"),
    ("id13", "id14", ["right_knee"], "upper_leg_right -> leg_2"),
]
# servos downstream of each hop (for the 1 A-per-moving-servo drop), derived from CHAIN
def downstream(a, b):
    kids = {}
    for x, y, _, _ in CHAIN:
        kids.setdefault(x, []).append(y)
    out, stack = [], [b]
    while stack:
        n = stack.pop()
        if n.startswith("id"):
            out.append(n)
        stack.extend(kids.get(n, []))
    return sorted(out)


cables = []
for a, b, hinges, path in CHAIN:
    L, an, ap, bn, bp = route(a, b, hinges)
    slack = span_rad(hinges) * R_BYPASS_MM
    n_down = len(downstream(a, b))
    cables.append({
        "id": "dxl-%s-%s" % (a, b), "group": "dynamixel-chain",
        "from": a, "from_point": an, "from_xyz_mm": [round(v, 2) for v in ap],
        "to": b, "to_point": bn, "to_xyz_mm": [round(v, 2) for v in bp],
        "path": path, "crosses": hinges,
        "range_span_deg": round(math.degrees(span_rad(hinges)), 1),
        "floor_mm": round(L, 1), "slack_mm": round(slack, 1), "cable_mm": ceil5(L + slack),
        "pins": "1 GND, 2 VDD, 3 DATA", "conductors": 3,
        "connector": "JST EH 3-pin (EHR-03 housing, SEH-001T-P0.6 crimp) both ends — ROBOTIS' 'X3P' lead",
        "wire": "21 AWG (E1 'Wire Gauge for DYNAMIXEL | 21 AWG', part:xl330-m288-t connector.wire)",
        "qty": 1, "servos_downstream": n_down,
        "how": "polyline from-point -> hinge origin(s) -> to-point; floor over the joints' full range; slack = span_rad x %.0f mm" % R_BYPASS_MM,
    })

# The HAT harness
def simple(cid, group, a, b, hinges, path, pins, conductors, connector, note):
    if not DEV[a]["pts"] or not DEV[b]["pts"]:
        cables.append({"id": cid, "group": group, "from": a, "to": b, "path": path, "crosses": hinges,
                       "floor_mm": None, "slack_mm": None, "cable_mm": None, "pins": pins,
                       "conductors": conductors, "connector": connector, "qty": 1,
                       "how": "CANNOT DETERMINE: " + note})
        return
    L, an, ap, bn, bp = route(a, b, hinges)
    slack = span_rad(hinges) * R_BYPASS_MM
    cables.append({"id": cid, "group": group,
                   "from": a, "from_point": an, "from_xyz_mm": [round(v, 2) for v in ap],
                   "to": b, "to_point": bn, "to_xyz_mm": [round(v, 2) for v in bp],
                   "path": path, "crosses": hinges, "range_span_deg": round(math.degrees(span_rad(hinges)), 1),
                   "floor_mm": round(L, 1), "slack_mm": round(slack, 1), "cable_mm": ceil5(L + slack),
                   "pins": pins, "conductors": conductors, "connector": connector, "qty": 1,
                   "how": "polyline from-point -> hinge origin(s) -> to-point; " + note})

simple("tof-hat", "hat-harness", "hat", "tof", [], "same body jaw_soft",
       "GND, 3V3, SDA, SCL (I2C3, addr 0x29)", 4,
       "JST-SH 4-pin 1.0 mm (Stemma/Qwiic) at the HAT's J5; the ToF board's end CANNOT DETERMINE",
       "HAT end is the board centroid (J5's place unpublished)")
simple("spk-hat", "hat-harness", "hat", "speaker", [], "same body jaw_soft",
       "SPK+, SPK- (codec line/HP out, or an amplifier: CANNOT DETERMINE)", 2,
       "representative 3525 speaker ships with a JST GH 1.25 mm 2-pin lead (part:microduck-speaker); HAT end CANNOT DETERMINE",
       "both ends are centroids")
simple("mic-hat", "hat-harness", "hat", "mic", [], "head", "MIC, BIAS, GND (codec Mic3R, community)", 3,
       "CANNOT DETERMINE", "the mic has no mesh and no site; length is null, not a guess")
simple("csi-radxa-camera", "hat-harness", "radxa", "camera", [], "same body jaw_soft — the ribbon crosses NO joint",
       "22-pin MIPI CSI: 2 data lanes + clock (differential pairs), I2C2 SDA/SCL, CAMERAB_PDN_L, VCC_3V3, GND", 22,
       "22-pin 0.5 mm FFC at the Radxa (Radxa wiki); the camera-board end CANNOT DETERMINE (22-pin 0.5 mm or 15-pin 1.0 mm + adapter)",
       "Radxa end is the board centroid; the CSI connector sits at a short edge, up to ~32 mm from it either way")
simple("bat-hat", "power", "battery", "hat",
       ["neck_pitch", "head_pitch", "head_yaw", "head_roll"],
       "trunk_base -> neck -> neck_pitch -> yaw_roll_motion -> jaw_soft: the ONLY cable that crosses all four head/neck hinges",
       "BAT+, BAT- (via the banana contact PCB)", 2,
       "battery contacts -> banana contact PCB (spring contacts, part unknown) -> HAT battery input (connector CANNOT DETERMINE)",
       "pack contact end -> four hinge origins -> HAT centroid; slack for 150 + 180 + 340 + 50 deg of joint range")
cables.append({"id": "hat-radxa-40pin", "group": "power", "from": "hat", "to": "radxa", "path": "same body jaw_soft",
               "crosses": [], "floor_mm": 0.0, "slack_mm": 0.0, "cable_mm": 0,
               "pins": "40-pin header: 5 V (pins 2/4), GND, UART2 (8/10), I2C3 (3/5), I2S3 (M0: 12/13/35/38/40 asserted)",
               "conductors": 40, "connector": "2x20 0.1 in header, board-to-board — not a cable", "qty": 1,
               "how": "HAT-to-Radxa board stack: 0 mm cable by construction (docs §2 'on the 40-pin header')"})
cables.append({"id": "hat-dxl-port", "group": "power", "from": "hat", "to": "id34", "path": "see dxl-hat-id34",
               "crosses": [], "floor_mm": None, "slack_mm": None, "cable_mm": None,
               "pins": "SERVO_V + DXL_DATA + GND leave the HAT on the first chain cable", "conductors": 3,
               "connector": "the HAT's bus header: JST EH 3-pin assumed (the servo end is EH); HAT end CANNOT DETERMINE", "qty": 0,
               "how": "not a separate cable — 'HAT -> bus power' IS the first hop dxl-hat-id34; qty 0 so it is not double-counted"})


# ---------------------------------------------------------------------------
# voltage drop on the servo bus — cecad.harness.check_drop, cascaded hop by hop
# ---------------------------------------------------------------------------
from cecad.harness import Harness, Route, check_drop, awg_resistance_ohm_per_m, AWG_FORMULA_CITE  # noqa: E402
from cecad.electrical import Report  # noqa: E402

I_PER_SERVO_MA = 1000.0
I_BASIS = ("1 A per moving servo, the lane's stated basis (GOAL.md rung 5 brief); the vendor publishes no running "
           "current — only standby 17 mA and stall 1.47 A at 5 V (part:xl330-m288-t current_mA) — so this is an "
           "assumption between them, applied to EVERY servo downstream of the hop (all 15 moving = the worst case)")
SUPPLY = {8.2: "8.2 V = the pack 'full' figure the runtime itself uses, read through the servos' present_input_voltage "
               "(model.rs:99-128, docs §9); bus VDD assumed to be the pack passed through the HAT (docs §3.4 open question 1)",
          6.6: "6.6 V = the pack 'empty' threshold at which robotd sits the robot down (model.rs:99-128; robotd.toml "
               "[safety] battery_empty_shutdown), i.e. the lowest bus voltage the robot is meant to walk at"}
MIN_V = 3.7
MIN_BASIS = ("3.7 V = the XL330's published lower supply bound, E1 'Input Voltage | 3.7 ~ 6.0 [V]' "
             "(part:xl330-m288-t supplies[0]) — the only vendor minimum there is; the design's own 6.6 V empty "
             "threshold is reported beside it, not used as min_v, because it is a threshold on the servo's OWN reading")


def harness_for(c, awg, mA):
    leads = [{"circuit": "VDD+", "current_mA": mA, "awg": awg, "current_basis": I_BASIS,
              "awg_basis": "AWG %d: %s" % (awg, "vendor figure, E1 'Wire Gauge for DYNAMIXEL | 21 AWG'" if awg == 21
                                            else "the brief's assumption ('use 22 AWG as ROBOTIS' cable'); the vendor page says 21")},
             {"circuit": "VDD-", "current_mA": mA, "awg": awg, "current_basis": I_BASIS, "awg_basis": "return leg, same wire"}]
    r = Route(a_path=c["from"], b_path=c["to"], a_pos_mm=tuple(c["from_xyz_mm"]), b_pos_mm=tuple(c["to_xyz_mm"]),
              length_mm=float(c["cable_mm"]), leads=leads,
              basis="cable_mm from cables.json = polyline floor through the crossed hinge origins + the stated slack; "
                    "a real loom with a service loop is longer")
    return Harness(name=c["id"], a_path=c["from"], b_path=c["to"], lead_map=[], rows=[], route=r,
                   report=Report("measured"))


drop = {"basis": {"current": I_BASIS, "supply": SUPPLY, "min_v": MIN_BASIS, "formula": AWG_FORMULA_CITE,
                  "length": "cable_mm (floor + slack), so the drop is over the full cable, not the floor alone"},
        "runs": []}
chain = [c for c in cables if c["group"] == "dynamixel-chain"]
by_id = {c["id"]: c for c in chain}
for awg in (21, 22):
    for V0, vbasis in SUPPLY.items():
        received = {"hat": V0}
        rows = []
        for c in chain:
            mA = c["servos_downstream"] * I_PER_SERVO_MA
            h = harness_for(c, awg, mA)
            vin = received[c["from"]]
            rep = check_drop(h, supply_v=vin,
                             supply_basis=vbasis + ("" if c["from"] == "hat" else
                                                    "; minus the upstream hops' drops, same formula"),
                             min_v=MIN_V, min_v_basis=MIN_BASIS)
            loop_ohm = 2 * awg_resistance_ohm_per_m(awg) * c["cable_mm"] / 1000.0
            dv = mA / 1000.0 * loop_ohm
            received[c["to"]] = vin - dv
            f = rep.findings[0]
            rows.append({"cable": c["id"], "servos_downstream": c["servos_downstream"], "I_A": mA / 1000.0,
                         "cable_mm": c["cable_mm"], "loop_ohm": round(loop_ohm, 5), "drop_V": round(dv, 4),
                         "v_in": round(vin, 4), "v_out": round(received[c["to"]], 4),
                         "verdict": f.verdict, "message": f.message})
        far = {k: v for k, v in received.items() if k in ("id24", "id14", "id30", "imu200")}
        drop["runs"].append({"awg": awg, "supply_v": V0, "verdict":
                             ("FAIL" if any(r["verdict"] == "FAIL" for r in rows) else
                              "CANNOT DETERMINE" if any(r["verdict"] == "CANNOT DETERMINE" for r in rows) else "PASS"),
                             "received_at_ends_V": {k: round(v, 4) for k, v in far.items()},
                             "total_drop_to_ankle_V": round(V0 - min(received["id24"], received["id14"]), 4),
                             "reads_empty_early_note": ("at %.1f V a far ankle servo reports %.3f V, i.e. %.0f mV below the "
                                                        "6.6 V empty threshold that robotd reads FROM the servos (model.rs:99-128); "
                                                        "the farthest device trips 'empty' first by that margin"
                                                        % (V0, min(received["id24"], received["id14"]),
                                                           (6.6 - min(received["id24"], received["id14"])) * 1000)) if V0 == 6.6 else "",
                             "hops": rows})


# ---------------------------------------------------------------------------
# outputs
# ---------------------------------------------------------------------------
n_cables = sum(c["qty"] for c in cables)
total_mm = sum(c["cable_mm"] for c in cables if c["cable_mm"] is not None and c["qty"])
undetermined = [c["id"] for c in cables if c["cable_mm"] is None and c["qty"]]
out = {"$triad": 1, "kind": "cables", "generated_by": "wiring/measure.py",
       "record": {"ref": "assembly:microduck", "units": "mm", "frame": P["frame"],
                  "inputs": {"placements": "ce-assemblies/microduck/current/placements.json",
                             "joints": "ce-assemblies/microduck/current/joints.json"},
                  "rule": __doc__.split("What a length IS here, stated once:")[1].split("Where a device's connector is:")[0].strip(),
                  "devices": {k: {"kind": v["kind"], "body": v["body"], "placements_row": v["row"],
                                  "points_mm": {n: [round(x, 2) for x in p] for n, p in v["pts"].items()},
                                  "ref": v["ref"]} for k, v in DEV.items()},
                  "cables": cables,
                  "cable_count": n_cables, "total_length_mm": total_mm,
                  "length_undetermined": undetermined}}
json.dump(out, open(os.path.join(HERE, "cables.json"), "w"), indent=1)
json.dump(drop, open(os.path.join(HERE, "drop.json"), "w"), indent=1)

# the table, for a person
L = []
L.append("# CABLES — measured off placements.json, generated by wiring/measure.py\n")
L.append("Do not edit: `python3 wiring/measure.py` rewrites this file, cables.json and drop.json. "
         "Every length is a ROUTE FLOOR through the crossed hinge origins plus the stated slack "
         "(rule in measure.py's docstring and cables.json `rule`).\n")
L.append("| # | cable | from (point) | to (point) | crosses (span deg) | floor mm | slack mm | **cable mm** | pins | connector | qty |")
L.append("|---|---|---|---|---|---|---|---|---|---|---|")
for i, c in enumerate(cables, 1):
    fm = "%s (%s)" % (c["from"], c.get("from_point", "-"))
    to = "%s (%s)" % (c["to"], c.get("to_point", "-"))
    cr = (", ".join(c["crosses"]) + " (%s)" % c.get("range_span_deg", 0)) if c["crosses"] else "none"
    f = lambda v: "CANNOT DETERMINE" if v is None else ("%.1f" % v if isinstance(v, float) else str(v))
    L.append("| %d | `%s` | %s | %s | %s | %s | %s | **%s** | %s | %s | %d |"
             % (i, c["id"], fm, to, cr, f(c["floor_mm"]), f(c["slack_mm"]), f(c["cable_mm"]), c["pins"], c["connector"], c["qty"]))
L.append("\n**%d cables, %d mm total over the %d with a length; undetermined: %s.**\n"
         % (n_cables, total_mm, n_cables - len(undetermined), ", ".join(undetermined) or "none"))
L.append("## Servo-bus voltage drop — cecad.harness.check_drop, hop by hop\n")
L.append("Bases: " + I_BASIS + "; min_v " + MIN_BASIS + ".\n")
for run in drop["runs"]:
    L.append("### AWG %d, %.1f V at the HAT — %s\n" % (run["awg"], run["supply_v"], run["verdict"]))
    L.append("| cable | servos downstream | I A | cable mm | loop ohm | drop V | V in | V out | verdict |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for r in run["hops"]:
        L.append("| `%s` | %d | %.0f | %d | %.4f | %.4f | %.3f | %.3f | %s |"
                 % (r["cable"], r["servos_downstream"], r["I_A"], r["cable_mm"], r["loop_ohm"], r["drop_V"], r["v_in"], r["v_out"], r["verdict"]))
    L.append("\nreceived at the ends: %s; total drop HAT -> farthest ankle **%.3f V**. %s\n"
             % (", ".join("%s %.3f V" % kv for kv in run["received_at_ends_V"].items()), run["total_drop_to_ankle_V"],
                run["reads_empty_early_note"]))
open(os.path.join(HERE, "CABLES.md"), "w").write("\n".join(L) + "\n")
print("cables %d, total %d mm, undetermined %s" % (n_cables, total_mm, undetermined))
for run in drop["runs"]:
    print("drop AWG%d @ %.1f V: %s, to ankle %.3f V" % (run["awg"], run["supply_v"], run["verdict"], run["total_drop_to_ankle_V"]))
