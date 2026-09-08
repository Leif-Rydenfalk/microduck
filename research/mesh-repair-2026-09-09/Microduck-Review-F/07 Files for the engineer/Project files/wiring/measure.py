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
  Historical model numbers use a polyline through selected endpoint proxies
  and crossed hinge origins, plus span_rad x 10 mm assumed slack, rounded up
  to 5 mm. They are preserved as modeled_* values for conditional analysis.
  They are not proven route floors: proxy points are not actual connector
  exits, and routing through joint centers is not an obstacle-aware loom.
  All physical wire cuts remain null until exact endpoints, socket allocation,
  insertion depth, bend radius, obstacles and service slack are established.

Where a device's connector is:
  XL330: two JST EH 3-pin sockets in pockets on the +/-y side faces, opening
  at y = +/-10 (mesh frame, part.py POCKET_*; the XL,XC-330.pdf side views
  show them). The proxy point used is the pocket centre on the side
  face: (6.85, +/-10.0, -9.0) mm in the mesh frame, transformed by the
  placement. The side (+y or -y) is chosen per hop as the one giving the
  shorter polyline. This independently selected side is not a verified
  ingress/egress socket allocation for a real chain.
  HAT: public family PCB/pad coordinates are available, but the installed
  revision and actual wire-exit coordinates are unresolved. Radxa, speaker
  and battery endpoints are also not established in this model. The
  reference point is the mesh CENTROID (bbox centre through the placement),
  and every such row says "centroid" in `ref`. The mic has no mesh: null.
  IMU / ToF / camera: the MJCF sites (docs/ELECTRONICS-AND-SOFTWARE.md).

Voltage drop: cecad.harness.check_drop over a hand-built Harness per hop —
the tool's own arithmetic (ASTM B258 diameter, IEC 60228 copper), with the
bases stated in the call. cecad.harness.wire(asm, a, b) could not be used:
it resolves ELECTRICAL connectors declared on the parts, and
the present model has no verified original connector-exit geometry.
The manually assembled Route is conditional arithmetic, not a measured loom.
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


def shown(value, places=3):
    return "CANNOT DETERMINE" if value is None else ("%.*f" % (places, value))


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
# joints.json carries 78 rows: 14 joint rows (params.joint) and 64 fastener-run
# rows (params = length_mm/state). Indexing every row with r["params"]["joint"]
# crashed with KeyError on the first fastener row (measured 2026-09-05). Only
# joint rows can be joints; the skipped ones are counted and printed, never
# dropped silently.
_joint_rows = [r for r in J["rows"] if "joint" in (r.get("params") or {})]
_skipped_rows = len(J["rows"]) - len(_joint_rows)
if _skipped_rows:
    print("joints.json: %d rows indexed as joints, %d non-joint rows skipped (fastener runs, params carry no joint)"
          % (len(_joint_rows), _skipped_rows), flush=True)
JOINT = {r["params"]["joint"]: r["params"] for r in _joint_rows}


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
              "ref": "HAT mesh centroid proxy; public PCB pad centers exist in out/wiring/hat-connectors.json, but installed revision and wire exits are unresolved"}
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


# None of these points is a measured wire exit on the original assembled unit.
for name, device in DEV.items():
    kind = ('socket_pocket_center_proxy' if device['kind'] == 'xl330' else
            'device_site_proxy' if name in ('imu200','tof','camera') else
            'inferred_contact_end_proxy' if name == 'battery' else
            'unlocated' if name == 'mic' else 'mesh_centroid_proxy')
    device['endpoint_evidence'] = {'kind': kind, 'verdict': 'CANNOT DETERMINE',
        'scope': 'Reference model point; exact original wire exit/contact/insertion datum unverified.'}
DEV['hat']['endpoint_evidence']['public_source'] = 'out/wiring/hat-connectors.json (public family footprint centers; target revision unresolved)'
DEV['mic']['endpoint_evidence']['public_source'] = 'Pinned public HAT PCB MK1 onboard MEMS; J2/J9 optional external inputs, not evidence of fitted external cable.'


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
        "how": "Historical proxy polyline through hinge origins; not a verified route floor; assumed slack = span_rad x %.0f mm" % R_BYPASS_MM,
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
       "HAT centroid proxy; J5 public-family pad coordinates published, exact installed wire exit and ToF module unknown")
simple("spk-hat", "hat-harness", "hat", "speaker", [], "same body jaw_soft",
       "Public HAT J1: differential SPK+/SPK- from PAM8406D U1 via FB2/FB3; original fitted speaker/termination unconfirmed", 2,
       "Representative speaker lead is not original proof; public HAT J1 Wago terminal footprint, target termination unknown",
       "both ends are centroids")
simple("mic-hat", "hat-harness", "hat", "mic", [], "head", "Optional external microphone path via public J2/J9; public board already has onboard MEMS MK1", 3,
       "CANNOT DETERMINE", "External mic cable presence unverified. Public PCB has onboard MEMS MK1 and optional J2/J9 inputs; installed target audio path unresolved. No extra external lead established.")
simple("csi-radxa-camera", "hat-harness", "radxa", "camera", [], "same body jaw_soft — the ribbon crosses NO joint",
       "22-pin MIPI CSI: 2 data lanes + clock (differential pairs), I2C2 SDA/SCL, CAMERAB_PDN_L, VCC_3V3, GND", 22,
       "22-pin 0.5 mm FFC at the Radxa (Radxa wiki); the camera-board end CANNOT DETERMINE (22-pin 0.5 mm or 15-pin 1.0 mm + adapter)",
       "Radxa end is the board centroid; the CSI connector sits at a short edge, up to ~32 mm from it either way")
# Camera endpoints are centroid/site proxies, not connector exits. Preserve the
# historical geometry observation separately; do not publish a manufacturable cut.
camera_cable = cables[-1]
assert camera_cable["id"] == "csi-radxa-camera"
camera_cable["proxy_distance_mm"] = camera_cable["floor_mm"]
camera_cable["historical_rounded_proxy_mm"] = camera_cable["cable_mm"]
camera_cable.update(floor_mm=None, slack_mm=None, cable_mm=None,
    how="CANNOT DETERMINE actual connector route/cut: historical13.3mm Radxa-centroid to camera-site distance rounded15mm is a proxy only. Measure connector exits, contact faces, insertion depths, bend radius and service slack on the exact module/host. Original ribbon unidentified.")
simple("bat-hat", "power", "battery", "hat",
       ["neck_pitch", "head_pitch", "head_yaw", "head_roll"],
       "trunk_base -> neck -> neck_pitch -> yaw_roll_motion -> jaw_soft: the ONLY cable that crosses all four head/neck hinges",
       "BAT+, BAT- (via the banana contact PCB)", 2,
       "battery contacts -> banana contact PCB (spring contacts, part unknown) -> HAT battery input (connector CANNOT DETERMINE)",
       "pack contact end -> four hinge origins -> HAT centroid; slack for 150 + 180 + 340 + 50 deg of joint range")
cables.append({"id": "hat-radxa-40pin", "group": "power", "from": "hat", "to": "radxa", "path": "same body jaw_soft",
               "crosses": [], "floor_mm": 0.0, "slack_mm": 0.0, "cable_mm": 0,
               "pins": "40-pin header: 5 V (pins 2/4), GND, UART2 (8/10), I2C3 (3/5), I2S3 (M0: 12/35/38/40 measured on pinned public HAT; pin 13 NC; MCLK from local Y1 12 MHz; installed revision unconfirmed)",
               "conductors": 40, "connector": "2x20 0.1 in header, board-to-board — not a cable", "qty": 1,
               "how": "HAT-to-Radxa board stack: 0 mm cable by construction (docs §2 'on the 40-pin header'); I2S connectivity measured 2026-09-08 from reference/pollen-elec-rpi-robot-hat/elec_RPI_Robot_HAT.kicad_pcb, commit 23eab11927f95ceca0dfa35bf182caeb7db39ea0 (PROVENANCE.json): J4.12/35/38/40 to U2.2/3/5/4; J4.13 unconnected; Y1.3 to U2.1 MCLK. Public board-family evidence only; exact board revision fitted to the target Microduck remains CANNOT DETERMINE."})
cables.append({"id": "hat-dxl-port", "group": "power", "from": "hat", "to": "id34", "path": "see dxl-hat-id34",
               "crosses": [], "floor_mm": None, "slack_mm": None, "cable_mm": None,
               "pins": "SERVO_V + DXL_DATA + GND leave the HAT on the first chain cable", "conductors": 3,
               "connector": "Public HAT J13/J14 3-pin DXL footprints; original chosen port, termination and revision unresolved", "qty": 0,
               "how": "not a separate cable — 'HAT -> bus power' IS the first hop dxl-hat-id34; qty 0 so it is not double-counted"})


from route_confidence import qualify, drop_verdict
for cable in cables:
    qualify(cable, DEV)
    if cable['id'] == 'mic-hat':
        cable['presence_verdict'] = 'CANNOT DETERMINE'
        cable['qty_scope'] = 'Historical modeled quantity only; external microphone lead is not established. Onboard MK1 is already part of the public HAT PCBA.'

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
              length_mm=float(c["modeled_cable_mm"]), leads=leads,
              basis="CONDITIONAL modeled_cable_mm from proxy polyline and assumed slack; actual cut unknown; "
                    "a real loom with a service loop is longer")
    return Harness(name=c["id"], a_path=c["from"], b_path=c["to"], lead_map=[], rows=[], route=r,
                   report=Report("measured"))


def calculate_drop(cables):
    drop = {"basis": {"current": I_BASIS, "supply": SUPPLY, "min_v": MIN_BASIS, "formula": AWG_FORMULA_CITE,
                      "length": "Historical modeled_cable_mm only; all actual routes/cuts unknown. Numeric results are conditional; uncertainty propagates downstream. Supply limits/conflict remain in research/servo-power-audit-2026-09-08/AUDIT.md."},
            "runs": []}
    chain = [c for c in cables if c["group"] == "dynamixel-chain"]
    by_id = {c["id"]: c for c in chain}
    for awg in (21, 22):
        for V0, vbasis in SUPPLY.items():
            received = {"hat": V0}
            confidence = {"hat": "PASS"}
            rows = []
            for c in chain:
                mA = c["servos_downstream"] * I_PER_SERVO_MA
                vin = received[c["from"]]
                modeled_length = c.get('modeled_cable_mm')
                if modeled_length is None or vin is None:
                    received[c['to']] = None
                    confidence[c['to']] = drop_verdict('CANNOT DETERMINE', c['route_verdict'], confidence[c['from']])
                    rows.append({'cable': c['id'], 'servos_downstream': c['servos_downstream'], 'I_A': mA/1000.,
                        'cable_mm': None, 'modeled_cable_mm': modeled_length, 'loop_ohm': None, 'drop_V': None,
                        'v_in': vin, 'v_out': None, 'verdict': confidence[c['to']], 'modeled_verdict': 'CANNOT DETERMINE',
                        'route_verdict': c['route_verdict'], 'message': 'No modeled length or upstream voltage; cannot compute, no default zero length.'})
                    continue
                h = harness_for(c, awg, mA)
                rep = check_drop(h, supply_v=vin,
                                 supply_basis=vbasis + ("" if c["from"] == "hat" else
                                                        "; minus the upstream hops' drops, same formula"),
                                 min_v=MIN_V, min_v_basis=MIN_BASIS)
                loop_ohm = 2 * awg_resistance_ohm_per_m(awg) * modeled_length / 1000.0
                dv = mA / 1000.0 * loop_ohm
                received[c["to"]] = vin - dv
                f = rep.findings[0]
                confidence[c["to"]] = drop_verdict(f.verdict, c["route_verdict"], confidence[c["from"]])
                rows.append({"cable": c["id"], "servos_downstream": c["servos_downstream"], "I_A": mA / 1000.0,
                             "cable_mm": None, "modeled_cable_mm": modeled_length, "loop_ohm": round(loop_ohm, 5), "drop_V": round(dv, 4),
                             "v_in": round(vin, 4), "v_out": round(received[c["to"]], 4),
                             "verdict": confidence[c["to"]], "modeled_verdict": f.verdict, "route_verdict": c["route_verdict"], "message": "Conditional model only; actual route unknown. " + f.message})
            ankle = [received.get("id24"), received.get("id14")]
            ankle_min = min(ankle) if all(v is not None for v in ankle) else None
            far = {k: v for k, v in received.items() if k in ("id24", "id14", "id30", "imu200")}
            drop["runs"].append({"awg": awg, "supply_v": V0, "verdict":
                                 ("FAIL" if any(r["verdict"] == "FAIL" for r in rows) else
                                  "CANNOT DETERMINE" if any(r["verdict"] == "CANNOT DETERMINE" for r in rows) else "PASS"),
                                 "received_at_ends_V": {k: round(v, 4) if v is not None else None for k, v in far.items()},
                                 "total_drop_to_ankle_V": round(V0 - ankle_min, 4) if ankle_min is not None else None,
                                 "reads_empty_early_note": ("at %.1f V a far ankle servo reports %.3f V, i.e. %.0f mV below the "
                                                            "6.6 V empty threshold that robotd reads FROM the servos (model.rs:99-128); "
                                                            "the farthest device trips 'empty' first by that margin"
                                                            % (V0, ankle_min,
                                                               (6.6 - ankle_min) * 1000)) if V0 == 6.6 and ankle_min is not None else "",
                                 "hops": rows})
    return drop


drop = calculate_drop(cables)


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
                                  "ref": v["ref"], "endpoint_evidence": v["endpoint_evidence"]} for k, v in DEV.items()},
                  "cables": cables,
                  "cable_count": n_cables, "total_length_mm": None,
                  "known_nonwire_length_mm": total_mm,
                  "modeled_total_length_mm": sum(c.get("modeled_cable_mm") or 0 for c in cables if c["qty"]),
                  "length_scope": "Actual cut lengths unknown; modeled total is historical arithmetic only, not a cutting list.",
                  "length_undetermined": undetermined}}
json.dump(out, open(os.path.join(HERE, "cables.json"), "w"), indent=1)
json.dump(drop, open(os.path.join(HERE, "drop.json"), "w"), indent=1)

# the table, for a person
L = []
L.append("# CABLES — measured off placements.json, generated by wiring/measure.py\n")
L.append("Do not edit: `python3 wiring/measure.py` rewrites this file, cables.json and drop.json. "
         "All wire cuts are CANNOT DETERMINE. Historical modeled numbers remain in JSON; proxy distances are not actual route floors. "
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
L.append("\n**%d modeled connections, %d mm known nonwire contribution over %d numeric nonwire rows; total wire cut length CANNOT DETERMINE; undetermined: %s.**\n"
         % (n_cables, total_mm, n_cables - len(undetermined), ", ".join(undetermined) or "none"))
L.append("## Conditional modeled servo-bus voltage drop — actual routes unknown\n")
L.append("Bases: " + I_BASIS + "; min_v " + MIN_BASIS + ".\n")
for run in drop["runs"]:
    L.append("### AWG %d, %.1f V at the HAT — %s\n" % (run["awg"], run["supply_v"], run["verdict"]))
    L.append("| cable | servos downstream | I A | modeled mm | loop ohm | drop V | V in | V out | verdict |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for r in run["hops"]:
        L.append("| `%s` | %d | %.0f | %s | %s | %s | %s | %s | %s |"
                 % (r["cable"], r["servos_downstream"], r["I_A"], shown(r["modeled_cable_mm"], 0), shown(r["loop_ohm"], 4), shown(r["drop_V"], 4), shown(r["v_in"]), shown(r["v_out"]), r["verdict"]))
    L.append("\nreceived at the ends: %s; total drop HAT -> farthest ankle **%s V**. %s\n"
             % (", ".join("%s %s V" % (kv[0], shown(kv[1])) for kv in run["received_at_ends_V"].items()), shown(run["total_drop_to_ankle_V"]),
                run["reads_empty_early_note"]))
open(os.path.join(HERE, "CABLES.md"), "w").write("\n".join(L) + "\n")
print("modeled connections %d, known nonwire contribution %d mm; wire total unknown; undetermined %s" % (n_cables, total_mm, undetermined))
for run in drop["runs"]:
    print("drop AWG%d @ %.1f V: %s, to ankle %s V" % (run["awg"], run["supply_v"], run["verdict"], shown(run["total_drop_to_ankle_V"])))
