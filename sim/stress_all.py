#!/usr/bin/env python3
"""stress_all.py — FEA on EVERY structural Microduck part, loaded with what
MuJoCo measured (sim/measure_loads.py -> out/sim-evidence/loads_mujoco.json).

Lane F1, 2026-09-02. Supersedes the round-number cases of sim/stress_evidence.py
(20 N "design load") and extends sim/stress_matrix.py (4 parts) to the parts it
did not cover: soles (TPU), feet, ankle (re-declared through its real load
path), shin, thigh + rigidity plate, hip bracket, yaw2roll, trunk base, the
neck chain (neck plate, neck-pitch bracket, yaw-roll cage, motor support) and
the power support. The right-hand parts are measured mirrors of the left
(p95 0.000-0.002 mm, each part.py header) and inherit the left verdicts.

LOAD BASIS — nothing round. For a part bridging MuJoCo body B, the force it
carries is the force B transmits to its parent (MuJoCo cfrc_int, world frame),
expressed in the part's own mesh frame by measure_loads.py. The load applied
at the part's DISTAL connectors is the force the far side exerts on it, which
by equilibrium of B (its own inertia neglected) is  -cfrc_int(B). Verified:
in stance the ankle's -cfrc_int is (-5.94, -3.97, +20.83) N in the ankle frame
where the ground reaction reads (-5.46, -4.02, +22.24) — up, as it must be.
  * walk   — BEST_alpha_walking at vx 0.25 m/s, the body's own peak inside
             the commanded window (per-body peaks differ by < 5 %)
  * drop   — 0.250 m fall onto the left foot (roll -10 deg), the peak frame
  * head   — 0.250 m fall onto the head (the neck chain only)
Foot and sole are loaded with the contact force itself (-GRF at the cradle /
cavity floor, ground side held).

MATERIAL — ce-cad/cecad/fits.py MATERIALS (PLA 50 MPa / 3.5 GPa, TPU 25 MPa /
0.026 GPa: class-tier, no datasheet, both "yield" values are ULTIMATES per the
table's own comment). Every study also reports SF against a FETCHED TDS
(research/tds/): Prusament PLA printed horizontal 51 +- 3 MPa yield, 2.3 GPa,
interlayer adhesion 17 +- 3 MPa; NinjaFlex TPU 85A yield 4 MPa / ultimate
26 MPa / modulus 12 MPa. The headline verdict is the MORE conservative of the
two. Orientation is NOT modelled (isotropic linear elastic); the interlayer
figure is the across-layer bound.

Run (one solver job at a time, buffered — read the log):
    ce-cad/bin/cad ce-designs/microduck/sim/stress_all.py > out/sim-evidence/fea/run.log
Each (part, case) writes out/sim-evidence/fea_<slug>_<case>.json + a von
Mises PNG (cecad.feaimage, read back). Existing JSONs are skipped (resume).
"""
import json
import os
import subprocess
import sys
import time
import traceback

from cecad.core import Assembly  # noqa: F401  (kernel import path)
import cecad.triad as triad
import cecad.stress as st
from cecad.stress import check_load, compare_materials
import cecad.feaimage as feaimage
import FreeCAD

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVID = os.path.join(REPO, "out", "sim-evidence")
FEA = os.path.join(EVID, "fea")
os.makedirs(FEA, exist_ok=True)
os.environ.setdefault("CE_TRIAD_ROOT", REPO + os.pathsep + os.path.expanduser("~/dev/ce-workshop"))
FORCE = "--force" in sys.argv
ONLY = [a for a in sys.argv[1:] if not a.startswith("--")]

L = json.load(open(os.path.join(EVID, "loads_mujoco.json")))
LOADS_SRC = "out/sim-evidence/loads_mujoco.json"
DROP_FOOT = next(d for d in L["drops"] if d["label"] == "drop_foot_rollm10_default_contact_dt5ms")
DROP_HEAD = next(d for d in L["drops"] if d["label"] == "drop_head_default_contact_dt5ms")
REQUIRE_SF = 2.0

# fetched datasheets (research/tds/, sha256 in the study JSON)
TDS = {
    "PLA": {"file": "research/tds/prusament-pla-tds-2021-10-en.pdf",
            "what": "Prusament PLA TDS v1.1 (16-02-2022), 3D-printed specimens, horizontal print direction",
            "yield_mpa": 51.0, "yield_tol": 3.0, "modulus_gpa": 2.3, "interlayer_mpa": 17.0, "interlayer_tol": 3.0,
            "method": "ISO 527-1 (tensile), interlayer adhesion Prusa Polymers method"},
    "TPU": {"file": "research/tds/ninjaflex-tds.pdf",
            "what": "NinjaTek NinjaFlex 85A TDS, ASTM D638 dogbone IV, 100 % fill",
            "yield_mpa": 4.0, "ultimate_mpa": 26.0, "modulus_mpa": 12.0, "method": "ASTM D638"},
}


def sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


# ---------------------------------------------------------------------------
# meshing: the size fallback + healing strategies for gmsh's sliver-face refusal
# ---------------------------------------------------------------------------
_orig_mesh_part = st.mesh_part
GMSH_STRATEGIES = [
    ("raw", None, []),
    ("removeSplitter", "rs", []),
    ("removeSplitter+occfix", "rs", ["-string", "Geometry.OCCFixSmallEdges=1;Geometry.OCCFixSmallFaces=1;Geometry.OCCSewFaces=1;"]),
]
MESH_STRATEGY_USED = {}


class _ShapeProxy:
    def __init__(self, name, shape):
        self.name, self.shape = name, shape


def mesh_part_ext(part, workdir, size=None, order=2, verbose=False):
    """gmsh with a strategy chain. The first strategy is exactly cecad's; the
    next two mesh the same solid after Part.removeSplitter() (merges faces
    split by the modelling history — geometry unchanged, topology tidied;
    volume compared and refused if it moves > 1e-6 relative) and with gmsh's
    OCC healing switched on. Raises like the original so the size fallback in
    the caller keeps going."""
    shape = getattr(part, "shape", part)
    name = getattr(part, "name", "shape")
    last = None
    for label, kind, extra in GMSH_STRATEGIES:
        shp = shape
        if kind == "rs":
            shp = shape.removeSplitter()
            if abs(shp.Volume - shape.Volume) > 1e-6 * shape.Volume or not shp.isValid():
                last = RuntimeError("removeSplitter changed the volume %.6f -> %.6f or made it invalid" % (shape.Volume, shp.Volume))
                continue
        try:
            m = _mesh_with(name, shp, workdir, size, order, extra)
            MESH_STRATEGY_USED[name] = {"strategy": label, "size": m.size, "nodes": len(m.nodes), "elements": len(m.elements),
                                         "eltype": m.eltype, "gmsh_extra": extra}
            return m
        except Exception as e:  # noqa: BLE001
            last = e
    raise RuntimeError("gmsh failed on %s after %d strategies: %s" % (name, len(GMSH_STRATEGIES), str(last)[-600:]))


def _mesh_with(name, shape, workdir, size, order, extra):
    os.makedirs(workdir, exist_ok=True)
    step = os.path.join(workdir, f"{name}.step")
    shape.exportStep(step)
    if size is None:
        b = shape.BoundBox
        thin = min(d for d in (b.XLength, b.YLength, b.ZLength) if d > 1e-9)
        size = max(thin / 3.0, 0.2)
    inp = os.path.join(workdir, f"{name}_mesh.inp")
    if os.path.exists(inp):
        os.remove(inp)
    cmd = [st.gmsh_path(), "-3", "-order", str(order), "-format", "inp",
           "-clmax", f"{size:g}", "-clmin", f"{size / 3.0:g}", "-optimize_ho"] + extra + ["-o", inp, step]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    if r.returncode != 0 or not os.path.isfile(inp):
        raise RuntimeError(f"gmsh failed on {name}: {(r.stderr or r.stdout)[-800:]}")
    m = st._parse_inp_mesh(inp)
    m.size = size
    if not m.elements:
        raise RuntimeError(f"gmsh produced no volume elements for {name}")
    return m


st.mesh_part = mesh_part_ext          # prepare() looks the name up at call time


def sizes_for(shape):
    """cecad's default (thinnest bbox side / 3) is a PLATE heuristic: on the ankle
    (bbox 39.5 x 36.5 x 25.5, walls 2.5) it puts 8.5 mm elements on 2.5 mm walls
    and a 4-face 'patch' covers 289 mm^2 of skin. Measured 2026-09-02 on the
    first run of this script. So the first size is clamp(thin/3, 0.8, 1.5) mm —
    at least one quadratic tet through a 1 mm plate, never more than 1.5 mm on
    a bracket — then the coarser/finer fallbacks."""
    b = shape.BoundBox
    thin = min(d for d in (b.XLength, b.YLength, b.ZLength) if d > 1e-9)
    first = max(0.8, min(1.5, thin / 3.0))
    out = [round(first, 3)]
    for s in (2.0, 1.2, 1.0):
        if abs(s - first) > 1e-6:
            out.append(s)
    return out


# parts whose mesher refusal is already diagnosed to the face — do not burn 20 min per case on them again
SKIP = {"microduck-upper-leg-left": "out/sim-evidence/fea_meshability_microduck-upper-leg-left.json"}


# ---------------------------------------------------------------------------
# the studies
# ---------------------------------------------------------------------------
def neg(v):
    return [-float(x) for x in v]


def walk_body(mesh, body):
    """(-cfrc_int at the body's own walk peak, in the part frame; magnitude; the JSON key path)"""
    pk = L["walk"]["body_transmitted_force_peaks"][body]
    v = pk["part_frames"][mesh]["force_from_body_%s_N_in_part_frame" % body]
    return neg(v), pk["peak_force_N"], "walk.body_transmitted_force_peaks.%s (step %d, t %.3f s)" % (body, pk["step"], pk["time_s"])


def drop_body(drop, mesh, body):
    v = drop["part_frames_at_peak"][mesh]["force_from_body_%s_N_in_part_frame" % body]
    return neg(v), drop["body_transmitted_force_max_N"][body]["magnitude"], "drops[%s].part_frames_at_peak.%s.force_from_body_%s (t %.3f s)" % (
        drop["label"], mesh, body, drop["peak_time_s"])


def walk_contact(mesh):
    v = L["walk"]["part_frames_at_peak"][mesh]["left_foot_contact_force_N_in_part_frame"]
    return neg(v), L["walk"]["peak_vertical_grf_N"], "walk.part_frames_at_peak.%s.left_foot_contact_force_N (GRF peak, step %d)" % (mesh, L["walk"]["peak_grf_step"])


def drop_contact(drop, mesh):
    v = drop["part_frames_at_peak"][mesh]["peak_contact_force_N_in_part_frame"]
    return neg(v), drop["peak_normal_force_N"], "drops[%s].part_frames_at_peak.%s.peak_contact_force_N" % (drop["label"], mesh)


def scaled(vec, factor):
    return [x * factor for x in vec]


HULL_SEAT_Z = -6.223 - 16.3     # ankle axis z (ankle part.py ZA) minus HULL_R: the hull bottom, 33..67 in x


def add_connectors(slug, p):
    """Connectors the part files do not declare but the load path needs.
    Every coordinate is one the part.py header measured (quoted)."""
    added = []
    if slug == "microduck-ankle-left":
        # the foot's cradle ledges (foot part.py: x 32.9..34.15 / 65.85..67.1) bear on the R16.3 hull
        p.connector("hull_seat_b", at=(33.5, 22.0, HULL_SEAT_Z), dir="-z")
        p.connector("hull_seat_h", at=(66.5, 22.0, HULL_SEAT_Z), dir="-z")
        added = ["hull_seat_b (33.5, 22, %.3f) -z" % HULL_SEAT_Z, "hull_seat_h (66.5, 22, %.3f) -z" % HULL_SEAT_Z]
    elif slug == "microduck-foot-left":
        p.connector("cradle_b", at=(33.5, 22.0, HULL_SEAT_Z), dir="+z")   # R16.3 seat about (y 22, z -6.223), on the ledges
        p.connector("cradle_h", at=(66.5, 22.0, HULL_SEAT_Z), dir="+z")
        # rib bottoms sit on the sole cavity floor = outer floor + 2.000 (foot + sole part.py); at x 52:
        # sole FLOOR_ZB row x=52 -> y 5: -29.875, y 10: -30.214, y 15: -30.259, y 20: -30.258, y 25: -29.917 (+2.000)
        for k, (y, z) in enumerate(((5.0, -27.875), (10.0, -28.214), (15.0, -28.259), (20.0, -28.258), (25.0, -27.917))):
            p.connector("ground_%d" % (k + 1), at=(52.0, y, z), dir="-z")
        added = ["cradle_b/h (33.5|66.5, 22, %.3f) +z" % HULL_SEAT_Z, "ground_1..5 at x 52, y 5..25 on the measured cavity floor + 2.000"]
    elif slug == "microduck-sole-left":
        p.connector("ground", at=(52.0, 15.0, -30.259), dir="-z")        # outer floor table, x 52 / y 15
        p.connector("cavity_floor", at=(52.0, 15.0, -28.259), dir="+z")  # + FLOOR_T 2.000
        added = ["ground (52, 15, -30.259) -z", "cavity_floor (52, 15, -28.259) +z"]
    return added


def harden_connectors(p, names):
    """A connector placed on an axis (bearing seat, horn centre, axle) sits in
    the VOID of its bore, and cecad's load_patch reaches only 3 x element size
    from it: at 8.5 mm elements the ankle's bearing_seat 'worked' by grabbing
    the nearest skin 6.98 mm away, at 1.5 mm it is refused as 'not on the
    part' (measured 2026-09-02). So every connector the case names is measured
    against the solid: if its point is more than 1.0 mm off the skin it is
    re-declared as kind 'bore' with spec d = 2 x that gap, which makes
    load_patch take the cylindrical WALL at that radius — the seat itself.
    Returns the list of what was changed, for the study JSON."""
    import Part
    changed = []
    for n in names:
        c = p.connectors.get(n)
        if c is None:
            continue
        try:
            gap = p.shape.distToShape(Part.Vertex(*c.pos))[0]
        except Exception as e:  # noqa: BLE001
            changed.append("%s: distToShape failed (%s)" % (n, e))
            continue
        if gap > 1.0 and (c.kind not in st._AXIAL_KINDS or not c.spec):
            p.connector(n, at=c.pos, dir=c.dir, up=c.up, kind="bore", spec="d%.3f" % (2.0 * gap))
            changed.append("%s: %.3f mm off the skin -> kind bore, spec d%.3f (wall at r %.3f)" % (n, gap, 2.0 * gap, gap))
    return changed


def plate_ends(p):
    """rigidity plate: the two screws nearest the hip axis A0 (0,0) are held, the two nearest the knee A1 are loaded."""
    cons = {n: c for n, c in p.connectors.items() if n.startswith("screw_")}
    def d0(c):
        return (c.pos[1] ** 2 + c.pos[2] ** 2) ** 0.5
    names = sorted(cons, key=lambda n: d0(cons[n]))
    return names[:2], names[2:]


def studies():
    """[(slug, mesh, cases)] with cases = [(case_name, fixed, load, force_vec, magnitude, source, why)]"""
    S = []
    # ---- leg chain -----------------------------------------------------------
    for slug, mesh, body, fixed, load in (
        ("microduck-ankle-left", "ankle_left", "ankle_left", ["bearing_seat", "horn_face"], ["foot_screw", "hull_seat_b", "hull_seat_h"]),
        ("microduck-shin", "leg", "leg", ["knee"], ["ankle"]),
        ("microduck-upper-leg-left", "upper_leg_left", "upper_leg_left", ["hip_pitch_axle", "hip_pitch_servo_seat"], ["knee_axle", "knee_servo_seat"]),
        ("microduck-hip-bracket", "hip_l", "hip_l", ["roll_boss"], ["pitch_boss"]),
        ("microduck-yaw2roll", "yaw2roll", "yaw2roll", ["yaw_horn", "yaw_bearing_seat"], ["roll_idler", "servo_screw_a", "servo_screw_b"]),
    ):
        w, wm, ws = walk_body(mesh, body)
        d, dm, ds = drop_body(DROP_FOOT, mesh, body)
        S.append((slug, mesh, [
            ("walk", fixed, load, w, wm, ws, "peak force body %s transmits during the measured walk" % body),
            ("drop", fixed, load, d, dm, ds, "0.250 m fall onto this foot, MuJoCo default contact, peak frame"),
        ]))
    # thigh rigidity plate: bounding case — the WHOLE thigh force through the plate (its true share depends on
    # plate-vs-housing stiffness, which nothing here measured; if it passes at 100 % it passes at any share)
    w, wm, ws = walk_body("upper_leg_rigidity_plate", "upper_leg_left")
    d, dm, ds = drop_body(DROP_FOOT, "upper_leg_rigidity_plate", "upper_leg_left")
    S.append(("microduck-upper-leg-rigidity-plate", "upper_leg_rigidity_plate", [
        ("walk", "PLATE_HIP", "PLATE_KNEE", w, wm, ws, "bounding: 100 % of the thigh's walk-peak force through the 1 mm plate"),
        ("drop", "PLATE_HIP", "PLATE_KNEE", d, dm, ds, "bounding: 100 % of the thigh's drop-peak force through the 1 mm plate"),
    ]))
    # foot + sole: contact force
    w, wm, ws = walk_contact("foot_left")
    d, dm, ds = drop_contact(DROP_FOOT, "foot_left")
    S.append(("microduck-foot-left", "foot_left", [
        ("walk", ["ground_1", "ground_2", "ground_3", "ground_4", "ground_5"], ["cradle_b", "cradle_h"], w, wm, ws, "the ankle hull presses the cradle with the walk-peak GRF; rib bottoms held on the sole floor"),
        ("drop", ["ground_1", "ground_2", "ground_3", "ground_4", "ground_5"], ["cradle_b", "cradle_h"], d, dm, ds, "0.250 m fall: the peak contact force through the cradle"),
    ]))
    w, wm, ws = walk_contact("sole_left")
    d, dm, ds = drop_contact(DROP_FOOT, "sole_left")
    S.append(("microduck-sole-left", "sole_left", [
        ("walk", ["ground"], ["cavity_floor"], w, wm, ws, "the foot presses the 2.000 mm cavity floor with the walk-peak GRF; outer floor on the ground"),
        ("drop", ["ground"], ["cavity_floor"], d, dm, ds, "0.250 m fall: peak contact force through the 2.000 mm floor"),
    ]))
    # trunk base: left stance, the swing (right) leg hangs off hip_yaw_right
    pf = L["walk"]["part_frames_at_peak"]["trunk_base"]
    w = neg(pf["force_from_body_bearing_roll_N_in_part_frame"])
    wm = L["walk"]["part_frames_at_peak"]["_body_force_N"]["bearing_roll"]["magnitude"]
    d = neg(DROP_FOOT["part_frames_at_peak"]["trunk_base"]["force_from_body_bearing_roll_N_in_part_frame"])
    dm = DROP_FOOT["part_frames_at_peak"]["_body_force_N_at_peak"]["bearing_roll"]["magnitude"]
    S.append(("microduck-trunk-base", "trunk_base", [
        ("walk", ["hip_yaw_left"], ["hip_yaw_right"], w, wm, "walk.part_frames_at_peak._body_force_N.bearing_roll (left GRF peak)",
         "left stance at the GRF peak: the plate spans from the loaded hip to the swing leg's hip"),
        ("drop", ["hip_yaw_left"], ["hip_yaw_right"], d, dm, "drops[foot].part_frames_at_peak._body_force_N_at_peak.bearing_roll",
         "landing on the left foot: the swing leg's inertial pull on the far hip"),
    ]))
    # ---- head chain -----------------------------------------------------------
    for slug, mesh, body, fixed, load, share in (
        ("microduck-neck-plate", "neck", "neck", ["servo_a_case"], ["servo_b_case"], 0.5),
        ("microduck-neck-pitch-bracket", "neck_pitch", "neck_pitch", ["pitch_horn_left", "pitch_horn_right"], ["yaw_horn_top"], 1.0),
        ("microduck-yaw-roll-motion", "yaw_roll_motion", "yaw_roll_motion", ["yaw_servo_case"], ["roll_horn", "roll_bearing_seat"], 1.0),
        ("microduck-motor-support", "motor_support", "jaw_soft", ["head_roll"], ["mouth_servo", "lens_tube"], 1.0),
    ):
        w, wm, ws = walk_body(mesh, body)
        d, dm, ds = drop_body(DROP_FOOT, mesh, body)
        h, hm, hs = drop_body(DROP_HEAD, mesh, body)
        note = " (HALF: two identical plates share it)" if share != 1.0 else ""
        S.append((slug, mesh, [
            ("walk", fixed, load, scaled(w, share), wm * share, ws, "head-side force during the measured walk" + note),
            ("drop", fixed, load, scaled(d, share), dm * share, ds, "0.250 m fall onto the foot: the head's inertia on the neck" + note),
            ("head_drop", fixed, load, scaled(h, share), hm * share, hs, "0.250 m fall onto the head: the trunk decelerating through the neck" + note),
        ]))
    # ---- power support: battery x trunk acceleration -----------------------------
    mb = 0.099   # kg — Duracell DR5 2600 mAh NP-F550-form pack, "Weight 99 g" (ce-parts/np-f550/electrical.part.json:74);
                 # the FITTED pack is CANNOT DETERMINE (part:np-f550), so this is the representative class figure
    g = 9.81
    a_walk = L["walk"]["trunk_linear_acceleration"]["peak_m_s2"]
    a_drop = DROP_FOOT["trunk_linear_acceleration_peak_m_s2"]
    gu = L["walk"]["part_frames_at_peak"]["power_support"]["gravity_unit_in_part_frame"]
    S.append(("microduck-power-support", "power_support", [
        ("walk", ["trunk_screw_low_left", "trunk_screw_low_right"], ["locker_screw_left", "locker_screw_right"],
         scaled(gu, mb * (g + a_walk)), mb * (g + a_walk), "walk.trunk_linear_acceleration.peak_m_s2 x 0.099 kg + weight, along gravity in the part frame",
         "battery weight + peak trunk acceleration during the walk, through the latch/locker screws (bounding direction: along gravity)"),
        ("drop", ["trunk_screw_low_left", "trunk_screw_low_right"], ["locker_screw_left", "locker_screw_right"],
         scaled(gu, mb * (g + a_drop)), mb * (g + a_drop), "drops[foot].trunk_linear_acceleration_peak_m_s2 x 0.099 kg + weight",
         "battery inertia at the landing deceleration, through the locker screws"),
    ]))
    return S


# ---------------------------------------------------------------------------
# run one case
# ---------------------------------------------------------------------------
def report_dict(rep):
    d = {}
    for a in ("verdict", "why", "sf", "max_vm", "max_disp", "yield_mpa", "material", "assumptions", "notes"):
        v = getattr(rep, a, None)
        if v is not None:
            d[a] = v
    return d


def build(slug):
    doc = FreeCAD.newDocument(slug.replace("-", "_") + "_%d" % int(time.time() * 1000 % 1e6))
    p = triad.load(doc, "part:" + slug)
    return doc, p


def run_case(slug, mesh, case, fixed, load, force, magnitude, source, why, size=None, material=None, tag=""):
    t0 = time.time()
    name = "%s_%s%s" % (slug, case, tag)
    rec = {"study": "fea_" + name, "part": "part:" + slug, "mjcf_mesh": mesh, "case": case,
           "generated": time.strftime("%Y-%m-%dT%H:%M:%S"), "script": "sim/stress_all.py",
           "inputs": {"force_N_part_frame": [round(float(x), 5) for x in force], "force_magnitude_N": round(float(magnitude), 5),
                      "force_source": LOADS_SRC + " :: " + source, "fixed": fixed, "load": load, "require_sf": REQUIRE_SF,
                      "mesh_size_requested_mm": size, "why": why}}
    try:
        doc, p = build(slug)
    except Exception as e:  # noqa: BLE001
        rec.update(verdict="CANNOT DETERMINE", why="build failed: %s" % e)
        return rec
    if material:
        p.material = material
    rec["material"] = str(p.material)
    added = add_connectors(slug, p)
    if fixed == "PLATE_HIP":
        fixed, load = plate_ends(p)
        rec["inputs"]["fixed"], rec["inputs"]["load"] = fixed, load
    rec["inputs"]["connectors_added"] = added
    rec["inputs"]["connectors_hardened"] = harden_connectors(p, list(fixed) + list(load))
    rec["inputs"]["connectors_available"] = sorted(p.connectors)
    from cecad.fits import MATERIALS
    m = MATERIALS.get(str(p.material).upper())
    rec["inputs"]["material_props"] = {
        "table": "ce-cad/cecad/fits.py MATERIALS[%r]" % m.name, "yield_mpa": m.yield_mpa, "youngs_gpa": m.youngs_gpa, "density": m.density,
        "tier": "class (no datasheet behind the row; the table's own comment says every polymer 'yield' is an ultimate)"}
    tds = TDS.get(str(p.material).upper())
    if tds:
        rec["inputs"]["tds"] = dict(tds, sha256=sha256(os.path.join(REPO, tds["file"])))
    try:
        p.load_case(case, fixed=fixed, load=load, force=tuple(force), require_sf=REQUIRE_SF, why=why)
    except Exception as e:  # noqa: BLE001
        rec.update(verdict="CANNOT DETERMINE", why="load_case refused: %s" % e)
        return rec
    workdir = os.path.join(FEA, name)
    tried = []
    rep = None
    for sz in ([size] if size is not None else sizes_for(p.shape)):
        MESH_STRATEGY_USED.pop(p.name, None)
        try:
            rep = check_load(p, case=case, size=sz, workdir=workdir, verbose=False, accept_class=True)
            tried.append({"size": sz, "ok": True, "strategy": MESH_STRATEGY_USED.get(p.name)})
            break
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            tried.append({"size": sz, "ok": False, "error": msg[-300:]})
            if "gmsh" not in msg and "mesh" not in msg.lower():
                break
    rec["mesh_attempts"] = tried
    if rep is None:
        rec.update(verdict="CANNOT DETERMINE", why="no mesh solved: " + tried[-1].get("error", "?")[-300:])
        rec["seconds"] = round(time.time() - t0, 1)
        return rec
    rd = report_dict(rep)
    out = {"verdict_cecad": rd.get("verdict"), "sf": rd.get("sf"), "max_von_mises_mpa": rd.get("max_vm"),
           "max_displacement_mm": rd.get("max_disp"), "yield_mpa_used": rd.get("yield_mpa"),
           "mesh": MESH_STRATEGY_USED.get(p.name), "assumptions": rd.get("assumptions", []), "notes": rd.get("notes", [])}
    if rd.get("sf") is not None and rd.get("max_vm"):
        vm = rd["max_vm"]
        out["failure_load_N_linear"] = round(float(magnitude) * rd["sf"], 4)   # load at which peak vM reaches the table yield (linear)
        if tds:
            y = tds["yield_mpa"]
            out["sf_vs_tds_yield"] = round(y / vm, 4)
            out["tds_yield_mpa"] = y
            if "interlayer_mpa" in tds:
                out["sf_vs_tds_interlayer_across_layers"] = round(tds["interlayer_mpa"] / vm, 4)
            if "ultimate_mpa" in tds:
                out["sf_vs_tds_ultimate"] = round(tds["ultimate_mpa"] / vm, 4)
    rec["outputs"] = out
    # headline verdict: the more conservative of the table verdict and the TDS-yield verdict
    v = rd.get("verdict")
    why = rd.get("why", "")
    if v == "PASS" and tds and out.get("sf_vs_tds_yield") is not None and out["sf_vs_tds_yield"] < REQUIRE_SF:
        v = "FAIL"
        why = "passes the class table (SF %.3f vs %g MPa) but FAILS against the fetched TDS yield %g MPa: SF %.3f < %g" % (
            rd["sf"], rd["yield_mpa"], tds["yield_mpa"], out["sf_vs_tds_yield"], REQUIRE_SF)
    rec["verdict"] = v
    rec["why"] = why or ("SF %.3f >= %g against %s yield %g MPa (class tier, accepted by the caller); TDS yield gives SF %s" % (
        rd["sf"], REQUIRE_SF, rec["material"], rd["yield_mpa"], out.get("sf_vs_tds_yield")))
    # the picture, read back
    rec["artifacts"] = [os.path.relpath(workdir, REPO)]
    try:
        rpt = {"part": p.name, "case": case, "verdict": rd.get("verdict"), "sf": rd.get("sf"), "max_von_mises_mpa": rd.get("max_vm"),
               "max_displacement_mm": rd.get("max_disp"), "material": rec["material"], "decks": workdir}
        rpath = os.path.join(workdir, "report.json")
        json.dump(rpt, open(rpath, "w"), indent=1)
        png = os.path.join(FEA, "%s.png" % name)
        fea = feaimage.produce(rpath, out_png=png, annotate=False)
        rec["artifacts"] += [os.path.relpath(png, REPO), os.path.relpath(rpath, REPO)]
        rec["looked_at"] = [{"image": os.path.relpath(png, REPO), "facts": fea["image_facts"],
                             "check": "peak von Mises recomputed from the .frd agrees with the report to 0.5 % (cecad.feaimage)"}]
    except Exception as e:  # noqa: BLE001
        rec["looked_at"] = [{"image": None, "error": "feaimage failed: %s" % str(e)[-300:]}]
    rec["seconds"] = round(time.time() - t0, 1)
    try:
        FreeCAD.closeDocument(doc.Name)
    except Exception:
        pass
    return rec


def write(rec):
    path = os.path.join(EVID, rec["study"] + ".json")
    json.dump(rec, open(path, "w"), indent=1)
    print("  -> %s  %s  SF=%s  vM=%s MPa  disp=%s mm  (%s s)" % (
        rec["verdict"], rec["study"], (rec.get("outputs") or {}).get("sf"), (rec.get("outputs") or {}).get("max_von_mises_mpa"),
        (rec.get("outputs") or {}).get("max_displacement_mm"), rec.get("seconds")))
    if rec["verdict"] == "CANNOT DETERMINE":
        print("     why:", rec.get("why", "")[:300])
    sys.stdout.flush()
    with open(os.path.join(FEA, "progress.txt"), "a") as fh:      # freecadcmd buffers stdout; this file does not
        fh.write("%s %s %s SF=%s vM=%s %ss %s\n" % (time.strftime("%H:%M:%S"), rec["verdict"], rec["study"], (rec.get("outputs") or {}).get("sf"),
                                                    (rec.get("outputs") or {}).get("max_von_mises_mpa"), rec.get("seconds"), (rec.get("why") or "")[:120]))
    return path


def main():
    print("=" * 78); print("stress_all — FEA with MuJoCo-measured loads"); print("=" * 78)
    for slug, mesh, cases in studies():
        if ONLY and slug not in ONLY and not any(o in slug for o in ONLY):
            continue
        for case, fixed, load, force, mag, src, why in cases:
            name = "fea_%s_%s" % (slug, case)
            if not FORCE and os.path.exists(os.path.join(EVID, name + ".json")):
                print("skip (exists)", name)
                continue
            print("=== %s / %s  |F|=%.4f N  F=%s" % (slug, case, mag, [round(x, 3) for x in force]))
            sys.stdout.flush()
            if slug in SKIP:
                rec = {"study": name, "part": "part:" + slug, "mjcf_mesh": mesh, "case": case, "script": "sim/stress_all.py",
                       "inputs": {"force_N_part_frame": [round(float(x), 5) for x in force], "force_magnitude_N": round(float(mag), 5),
                                  "force_source": LOADS_SRC + " :: " + src, "fixed": fixed, "load": load, "require_sf": REQUIRE_SF, "why": why},
                       "verdict": "CANNOT DETERMINE", "why": "no tetrahedral mesh exists for this solid — see " + SKIP[slug],
                       "artifacts": [SKIP[slug]], "looked_at": []}
                write(rec)
                continue
            try:
                rec = run_case(slug, mesh, case, fixed, load, force, mag, src, why)
            except Exception as e:  # noqa: BLE001
                rec = {"study": name, "part": "part:" + slug, "case": case, "verdict": "CANNOT DETERMINE",
                       "why": "runner crashed: %s" % e, "traceback": traceback.format_exc()[-1500:], "script": "sim/stress_all.py"}
            write(rec)

    # ---- mesh convergence + material sweep on the governing part: ankle / drop -----
    if not ONLY or any("ankle" in o for o in ONLY):
        conv_path = os.path.join(EVID, "fea_convergence_microduck-ankle-left_drop.json")
        if FORCE or not os.path.exists(conv_path):
            rows = []
            fixed, load = ["bearing_seat", "horn_face"], ["foot_screw", "hull_seat_b", "hull_seat_h"]
            d, dm, ds = drop_body(DROP_FOOT, "ankle_left", "ankle_left")
            for sz in (None, 1.5, 1.0, 0.7):
                print("=== convergence ankle/drop size", sz); sys.stdout.flush()
                r = run_case("microduck-ankle-left", "ankle_left", "drop", fixed, load, d, dm, ds,
                             "mesh convergence on the governing case", size=sz, tag="_h%s" % (sz if sz else "auto"))
                o = r.get("outputs") or {}
                rows.append({"size_mm": sz, "size_used_mm": (o.get("mesh") or {}).get("size"), "nodes": (o.get("mesh") or {}).get("nodes"),
                             "elements": (o.get("mesh") or {}).get("elements"), "sf": o.get("sf"), "max_von_mises_mpa": o.get("max_von_mises_mpa"),
                             "max_displacement_mm": o.get("max_displacement_mm"), "verdict": r.get("verdict"), "seconds": r.get("seconds"),
                             "image": next((a for a in r.get("artifacts", []) if a.endswith(".png")), None)})
                print("    size %s -> SF %s vM %s" % (sz, o.get("sf"), o.get("max_von_mises_mpa"))); sys.stdout.flush()
            ok = [r for r in rows if r["sf"]]
            verdict, why = "CANNOT DETERMINE", "fewer than two sizes solved"
            if len(ok) >= 2:
                a, b = ok[-2], ok[-1]
                drift = abs(b["max_von_mises_mpa"] - a["max_von_mises_mpa"]) / max(b["max_von_mises_mpa"], 1e-9)
                disp_drift = abs(b["max_displacement_mm"] - a["max_displacement_mm"]) / max(b["max_displacement_mm"], 1e-9)
                if drift < 0.10:
                    verdict, why = "PASS", "peak von Mises moved %.2f %% between the two finest meshes (< 10 %%); deflection moved %.2f %%" % (100 * drift, 100 * disp_drift)
                else:
                    verdict, why = "FAIL", ("peak von Mises still moves %.2f %% between the two finest meshes — a mesh-driven peak (re-entrant corner / point patch), "
                                            "the SF is not converged; deflection moved %.2f %%" % (100 * drift, 100 * disp_drift))
            json.dump({"study": "fea_convergence_microduck-ankle-left_drop", "part": "part:microduck-ankle-left", "case": "drop",
                       "inputs": {"sizes_mm": [None, 1.5, 1.0, 0.7], "force_N_part_frame": d, "force_source": LOADS_SRC + " :: " + ds},
                       "method": "same solid, same case, gmsh characteristic length swept; C3D10 quadratic tets; CalculiX linear static",
                       "outputs": {"rows": rows}, "verdict": verdict, "why": why, "script": "sim/stress_all.py",
                       "artifacts": [r["image"] for r in rows if r["image"]], "looked_at": []}, open(conv_path, "w"), indent=1)
            print("  -> convergence", verdict, why); sys.stdout.flush()

        mat_path = os.path.join(EVID, "fea_materials_microduck-ankle-left_drop.json")
        if FORCE or not os.path.exists(mat_path):
            print("=== material sweep ankle/drop"); sys.stdout.flush()
            rec = {"study": "fea_materials_microduck-ankle-left_drop", "part": "part:microduck-ankle-left", "case": "drop", "script": "sim/stress_all.py",
                   "method": "cecad.stress.compare_materials: one mesh, one load, every candidate's E/nu solved and judged against its table yield (class tier)"}
            try:
                doc, p = build("microduck-ankle-left")
                add_connectors("microduck-ankle-left", p)
                d, dm, ds = drop_body(DROP_FOOT, "ankle_left", "ankle_left")
                p.load_case("drop", fixed=["bearing_seat", "horn_face"], load=["foot_screw", "hull_seat_b", "hull_seat_h"], force=tuple(d),
                            require_sf=REQUIRE_SF, why="material trade on the governing case")
                ts = compare_materials(p, case="drop", candidates=("PLA", "PETG", "ABS", "ASA", "NYLON", "PCTG", "PA6CF", "AL6061"),
                                       workdir=os.path.join(FEA, "materials_ankle_drop"), verbose=False, accept_class=True)
                cands = []
                for c in getattr(ts, "candidates", []):
                    cands.append({a: getattr(c, a, None) for a in ("material", "verdict", "why", "sf", "max_vm", "max_disp", "mass_g", "yield_mpa", "youngs_gpa")})
                rec["inputs"] = {"force_N_part_frame": d, "force_magnitude_N": dm, "force_source": LOADS_SRC + " :: " + ds}
                rec["outputs"] = {"candidates": cands, "lightest_passing": str(getattr(ts, "lightest_passing", lambda: None)())}
                passing = [c for c in cands if c.get("verdict") == "PASS"]
                rec["verdict"] = "PASS" if passing else "FAIL"
                rec["why"] = ("%d of %d candidates reach SF %g on the measured drop load: %s" % (len(passing), len(cands), REQUIRE_SF, ", ".join(c["material"] for c in passing))
                              if passing else "no candidate in the table reaches SF %g on the measured drop load — the geometry, not the material, is the limit" % REQUIRE_SF)
            except Exception as e:  # noqa: BLE001
                rec.update(verdict="CANNOT DETERMINE", why="compare_materials failed: %s" % e, traceback=traceback.format_exc()[-1200:])
            rec["artifacts"] = [os.path.relpath(os.path.join(FEA, "materials_ankle_drop"), REPO)]
            rec["looked_at"] = []
            json.dump(rec, open(mat_path, "w"), indent=1)
            print("  ->", rec["verdict"], rec["why"]); sys.stdout.flush()
    print("DONE")


if __name__ == "__main__":
    main()
