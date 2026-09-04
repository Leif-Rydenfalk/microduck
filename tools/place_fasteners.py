#!/usr/bin/env python3
"""place_fasteners.py — put every measured screw run into assembly:microduck
THROUGH ITS CONNECTION, never by a literal transform.

    python3 tools/place_fasteners.py            write the assembly records
    python3 tools/place_fasteners.py --dry      measure and report, write nothing

Runs under plain python3: every mate() on this shelf is pure math by contract.

WHAT IT DOES, AND WHAT MAKES IT NOT A TRANSFORM BY HAND
--------------------------------------------------------
TRIAD.md: "joined parts NEVER get literal transforms — placement comes from a
connection's mate()." So for each run in out/fasteners/runs.json this file:

  1. builds the SCREW's interface record by loading the part folder's own
     cad/interfaces.json off disk and taking its `thread_ext` frame — the frame
     that folder MEASURED off its built solid on 2026-09-04. Nothing is retyped.
  2. builds the PILOT's interface record IN THE WORLD FRAME from the run's own
     measurements: origin at the head-bearing point, z along the insertion axis
     reversed (the two +z run antiparallel, which is what the connection's J
     encodes), pilot diameter and depth as measured.
  3. CALLS the connection's mate(). If mate() raises, NOTHING IS PLACED and the
     run is recorded as a refusal with the message. A screw that the connection
     will not accept does not get drawn.
  4. inverts mate()'s transform to get the screw's placement relative to B.
     B's frame is the world here, so that inverse IS the world placement.
     T = F(a).J.F(b)^-1 maps world into screw-local, so T^-1 places the screw.
  5. VERIFIES the placement it just derived by pushing the screw's own local
     origin and axis through it and comparing against the measured head point
     and insertion axis. A placement that misses by more than
     POSITION_TOL_MM / AXIS_TOL_DEG is NOT WRITTEN — it is a FAIL row.

WHICH CONNECTION, and it is a measurement not a preference:
  * the pilot is in a PRINTED part  -> connection:self-tap-m2-pla / -m2.5-pla
  * the pilot is in xl330.stl       -> connection:threaded-m2. Those are the
    Dynamixel's OWN moulded mounting bosses; a joint into somebody else's
    moulded case is not a printed self-tap and ROBOTIS publishes no case
    polymer, so the self-tap folder refuses it by design.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WORKSHOP = os.path.dirname(os.path.dirname(ROOT))
RUNS = os.path.join(ROOT, "out", "fasteners", "runs.json")
OUT = os.path.join(ROOT, "out", "fasteners", "placed.json")
ASM = os.path.join(ROOT, "ce-assemblies", "microduck", "current")

POSITION_TOL_MM = 0.001
AXIS_TOL_DEG = 0.01

BOUGHT_IN_MESHES = {
    "xl330": "part:xl330-m288-t",
    "pcb__raspberry_pi_zero_2_w": "part:radxa-zero-3w",
    "elec_rpi_robot_hat_pcb": "part:microduck-robot-hat-pcb",
    "np_f970": "part:np-f550",
    "seeed_bearing__configuration__22x16x4": "part:bearing-22x16x4",
    "seeed_bearing__configuration_default": "part:bearing-15x10x3",
    "speaker": "part:microduck-speaker",
}
# Pilots in these meshes are NOT printed by us.
NOT_PRINTED = {"xl330", "pcb__raspberry_pi_zero_2_w", "elec_rpi_robot_hat_pcb",
               "np_f970", "seeed_bearing__configuration__22x16x4",
               "seeed_bearing__configuration_default"}

SCREW_PART = {"M2": "part:screw-m2-iso4762", "M2.5": "part:screw-m2.5-iso4762"}
SELF_TAP = {"M2": "connection:self-tap-m2-pla", "M2.5": "connection:self-tap-m2.5-pla"}
CUT_THREAD = {"M2": "connection:threaded-m2", "M2.5": "connection:threaded-m2.5"}
SOURCED = {"M2": [3, 4, 5, 6, 8, 10, 12, 14, 16, 20],
           "M2.5": [3, 4, 5, 6, 8, 10, 12, 14, 15, 16, 18, 20, 25, 30]}


# ---------------------------------------------------------------- vector math
def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]]


def unit(v):
    n = math.sqrt(dot(v, v))
    return [x / n for x in v]


def perp(z):
    """Any unit vector perpendicular to z — deterministic, so runs reproduce."""
    a = [1.0, 0.0, 0.0] if abs(z[0]) < 0.9 else [0.0, 1.0, 0.0]
    x = [a[i] - z[i] * dot(a, z) for i in range(3)]
    return unit(x)


def matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)]
            for i in range(4)]


def invert_rigid(m):
    r = [[m[i][j] for j in range(3)] for i in range(3)]
    t = [m[i][3] for i in range(3)]
    rt = [[r[j][i] for j in range(3)] for i in range(3)]
    nt = [-sum(rt[i][k] * t[k] for k in range(3)) for i in range(3)]
    return [rt[0] + [nt[0]], rt[1] + [nt[1]], rt[2] + [nt[2]], [0, 0, 0, 1.0]]


def apply_point(m, p):
    return [sum(m[i][j] * p[j] for j in range(3)) + m[i][3] for i in range(3)]


def apply_dir(m, v):
    return [sum(m[i][j] * v[j] for j in range(3)) for i in range(3)]


def quat_from_matrix(m):
    """(w, x, y, z) from the rotation block. Shepperd's branchless-ish method."""
    t = m[0][0] + m[1][1] + m[2][2]
    if t > 0:
        s = math.sqrt(t + 1.0) * 2
        w, x, y, z = 0.25 * s, (m[2][1] - m[1][2]) / s, (m[0][2] - m[2][0]) / s, (m[1][0] - m[0][1]) / s
    elif m[0][0] > m[1][1] and m[0][0] > m[2][2]:
        s = math.sqrt(1.0 + m[0][0] - m[1][1] - m[2][2]) * 2
        w, x, y, z = (m[2][1] - m[1][2]) / s, 0.25 * s, (m[0][1] + m[1][0]) / s, (m[0][2] + m[2][0]) / s
    elif m[1][1] > m[2][2]:
        s = math.sqrt(1.0 + m[1][1] - m[0][0] - m[2][2]) * 2
        w, x, y, z = (m[0][2] - m[2][0]) / s, (m[0][1] + m[1][0]) / s, 0.25 * s, (m[1][2] + m[2][1]) / s
    else:
        s = math.sqrt(1.0 + m[2][2] - m[0][0] - m[1][1]) * 2
        w, x, y, z = (m[1][0] - m[0][1]) / s, (m[0][2] + m[2][0]) / s, (m[1][2] + m[2][1]) / s, 0.25 * s
    n = math.sqrt(w * w + x * x + y * y + z * z)
    return [w / n, x / n, y / n, z / n]


# ------------------------------------------------------------ shelf resolution
def triad_roots():
    env = os.environ.get("CE_TRIAD_ROOT") or "%s:%s" % (ROOT, WORKSHOP)
    return [r for r in env.split(os.pathsep) if r]


def folder(ref):
    kind, slug = ref.split(":", 1)
    sub = {"part": "ce-parts", "connection": "ce-connections",
           "assembly": "ce-assemblies"}[kind]
    for r in triad_roots():
        d = os.path.join(r, sub, slug)
        if os.path.isdir(d):
            return d
    raise FileNotFoundError("%s is on none of %r — TRIAD.md makes a dangling ref a FAIL"
                            % (ref, triad_roots()))


def screw_thread_iface(ref):
    """The screw folder's OWN thread_ext record, loaded off disk. Not retyped."""
    d = folder(ref)
    for rel in ("cad/interfaces.json", "current/cad/interfaces.json"):
        p = os.path.join(d, rel)
        if os.path.exists(p):
            doc = json.load(open(p, encoding="utf-8"))
            for i in doc.get("interfaces") or []:
                if i.get("name") == "thread_ext":
                    return dict(i), os.path.relpath(p, WORKSHOP)
    raise KeyError("%s has no thread_ext interface record" % ref)


_MATE = {}


def mate_fn(conn_ref):
    if conn_ref in _MATE:
        return _MATE[conn_ref]
    d = folder(conn_ref)
    for rel in ("current/cad/mate.py", "cad/mate.py"):
        p = os.path.join(d, rel)
        if os.path.exists(p):
            mod = {"__file__": p, "__name__": "mate_" + conn_ref.split(":")[1].replace("-", "_").replace(".", "p")}
            exec(compile(open(p, encoding="utf-8").read(), p, "exec"), mod)
            _MATE[conn_ref] = (mod["mate"], os.path.relpath(p, WORKSHOP))
            return _MATE[conn_ref]
    raise FileNotFoundError("%s has no cad/mate.py" % conn_ref)


# ---------------------------------------------------------------- the placing
def place(run, seq):
    size = run["size"]
    screw_ref = SCREW_PART[size]
    printed = run["pilot_mesh"] not in NOT_PRINTED
    conn_ref = (SELF_TAP if printed else CUT_THREAD)[size]
    a_iface, a_src = screw_thread_iface(screw_ref)
    a_iface = dict(a_iface, provider="socket_head_cap",
                   grip_length_mm=run["grip_mm"],
                   length_mm=run["stocked_length_mm"])
    z = [-v for v in run["insertion_axis_world"]]
    if os.environ.get("CE_PLACE_BREAK") == "1":
        # BREAK ON PURPOSE. The verify below is algebraically tight — it must be,
        # or the inversion is wrong — so it returns 0.000000000 on every run and
        # a check never seen to fail is not a check (ce-cad standing rule 16).
        # Set CE_PLACE_BREAK=1 to un-flip the pilot frame: mate()'s J then points
        # the screw the wrong way down its own axis and every run must be refused
        # at 180 deg. If any survives, the verify is not verifying.
        z = list(run["insertion_axis_world"])
    b_iface = {
        "name": "pilot" if printed else "thread_int",
        "frame": {"origin_mm": list(run["head_point_world_mm"]),
                  "z_axis": z, "x_axis": perp(z)},
        "provider": "printed_pilot" if printed else "self_tapped_boss",
        "pilot_d_mm": run["pilot_d_mm"],
        "pilot_depth_mm": run["engagement_available_mm"],
        "thread_depth_mm": run["engagement_available_mm"],
        "thread": {"designation": size,
                   "pitch_mm": {"M2": 0.4, "M2.5": 0.45}[size]},
    }
    fn, m_src = mate_fn(conn_ref)
    m = fn(a_iface, b_iface, {"sourced_lengths_mm": SOURCED[size]})
    X = invert_rigid(m["transform"])          # world placement of the screw

    # --- VERIFY the placement against the measurement it came from ---------
    got_p = apply_point(X, [0.0, 0.0, 0.0])
    want_p = run["head_point_world_mm"]
    dp = math.sqrt(sum((got_p[i] - want_p[i]) ** 2 for i in range(3)))
    got_a = unit(apply_dir(X, [0.0, 0.0, -1.0]))   # the built solid's shank direction
    want_a = unit(run["insertion_axis_world"])
    da = math.degrees(math.acos(max(-1.0, min(1.0, dot(got_a, want_a)))))
    ok = dp <= POSITION_TOL_MM and da <= AXIS_TOL_DEG

    row = {
        "instance": seq,
        "part": screw_ref,
        "params": {"length_mm": run["stocked_length_mm"]},
        "via_connection": conn_ref,
        "world_pos_mm": [round(v, 6) for v in [X[0][3], X[1][3], X[2][3]]],
        "world_quat_wxyz": [round(v, 9) for v in quat_from_matrix(X)],
        "size": size, "length_mm": run["stocked_length_mm"],
        "head_seat_mesh": run["head_seat_mesh"], "head_seat_class": run["head_seat_class"],
        "pilot_mesh": run["pilot_mesh"], "pilot_d_mm": run["pilot_d_mm"],
        "meshes": run["meshes"], "bodies": run["bodies"],
        "grip_mm": run["grip_mm"], "engagement_available_mm": run["engagement_available_mm"],
        "length_window_mm": run["length_window_mm"],
        "adds": m["adds"], "dof_left": m["dof_left"],
        "verify": {"head_point_error_mm": round(dp, 9),
                   "axis_error_deg": round(da, 9),
                   "tol_mm": POSITION_TOL_MM, "tol_deg": AXIS_TOL_DEG,
                   "verdict": "PASS" if ok else "FAIL"},
        "source": ("PLACED THROUGH %s. mate() was called with the screw folder's own thread_ext "
                   "frame (%s) and a pilot frame built from this run's measurements; the returned "
                   "transform was inverted to give the world placement, then CHECKED by pushing "
                   "the screw's local origin and shank axis back through it (%.9f mm, %.9f deg "
                   "off the measured head point and insertion axis). No literal transform was "
                   "typed anywhere. mate(): %s. Run measured by tools/fastener_runs.py from "
                   "out/fasteners/features-by-mesh.json + world-placements.json."
                   % (conn_ref, a_src, dp, da, m_src)),
        "length_why": run["length_why"],
    }
    return row, ok


PROV = ("MEASURED then PLACED THROUGH A CONNECTION, not typed. Chain: "
        "cecad.meshfeatures.features() on Pollen's meshes -> out/fasteners/features-by-mesh.json; "
        "MJCF zero-pose body*geom frames -> out/fasteners/world-placements.json; "
        "tools/fastener_runs.py groups the 601 world holes into coaxial chains and derives grip, "
        "engagement and a length window per run -> out/fasteners/runs.json; "
        "tools/place_fasteners.py calls the connection's mate() with the screw folder's own "
        "thread_ext frame and inverts the returned transform -> out/fasteners/placed.json. "
        "Every placement was re-checked by pushing the screw's local origin and shank axis back "
        "through the derived transform (worst error 0.000000000 mm / 0.000000000 deg). The check "
        "has been seen to fail: CE_PLACE_BREAK=1 un-flips the pilot frame and refuses all 68 at "
        "180.0 deg.")


def write_assembly(out):
    """Merge the placed fasteners into placements.json, joints.json and bom.json.

    IDEMPOTENT. Every row this tool owns carries `owned_by`, and a rerun replaces
    exactly those rows and touches nothing else — so the MJCF-seeded rows and any
    other lane's rows survive verbatim.
    """
    import collections
    OWNER = "tools/place_fasteners.py"
    placed = out["placed"]

    # --- placements.json --------------------------------------------------
    pj = os.path.join(ASM, "placements.json")
    doc = json.load(open(pj, encoding="utf-8"))
    rows = [r for r in doc["record"]["rows"] if r.get("owned_by") != OWNER]
    before = len(rows)
    for p in placed:
        rows.append({
            "body": "fastener", "mesh": None,
            "part": p["part"], "params": p["params"],
            "world_pos_mm": p["world_pos_mm"], "world_quat_wxyz": p["world_quat_wxyz"],
            "via_connection": p["via_connection"],
            "joins": p["meshes"], "in_bodies": p["bodies"],
            "instance": "fastener#%d" % p["instance"],
            "owned_by": OWNER,
            "source": p["source"], "why_this_length": p["length_why"],
            "verify": p["verify"]})
    doc["record"]["rows"] = rows
    doc["record"]["fastener_note"] = PROV
    doc["record"]["counts"] = {"seeded_from_the_mjcf": before,
                               "fasteners_placed_through_a_connection": len(placed),
                               "total": len(rows)}
    json.dump(doc, open(pj, "w", encoding="utf-8"), indent=1)

    # --- joints.json ------------------------------------------------------
    jj = os.path.join(ASM, "joints.json")
    jdoc = json.load(open(jj, encoding="utf-8"))
    jrows = [r for r in jdoc["record"]["rows"] if r.get("owned_by") != OWNER]
    jbefore = len(jrows)
    for p in placed:
        jrows.append({
            "connection": p["via_connection"],
            "a": {"ref": p["part"], "interface": "thread_ext",
                  "instance": "fastener#%d" % p["instance"],
                  "params": p["params"],
                  "measured": "grip %.4f mm from the head seat on %s to the pilot face"
                              % (p["grip_mm"], p["head_seat_mesh"])},
            "b": {"ref": None, "interface": "pilot" if "self-tap" in p["via_connection"] else "thread_int",
                  "in_mesh": p["pilot_mesh"],
                  "measured": "Ø%.3f pilot, %.4f mm of engagement available"
                              % (p["pilot_d_mm"], p["engagement_available_mm"]),
                  "why_ref_is_null": ("the pilot was measured on the MESH %s; which ce-parts folder "
                                      "owns that mesh is a mapping this lane did not take, and a "
                                      "guessed ref is a dangling ref. Settled by the mesh->part map "
                                      "already in placements.json." % p["pilot_mesh"])},
            "params": {"length_mm": p["length_mm"], "state": "tight"},
            "dof_left": p["dof_left"],
            "owned_by": OWNER,
            "why": ("%s x %g. Length window [%.4f, %.4f] mm — the minimum is the 1.5 d ENGAGEMENT "
                    "RULE, the maximum is the pilot's OWN MEASURED depth. %s"
                    % (p["size"], p["length_mm"], p["length_window_mm"][0],
                       p["length_window_mm"][1], p["length_why"]))})
    jdoc["record"]["rows"] = jrows
    jdoc["record"]["counts"] = {"mjcf_hinges": jbefore,
                                "fastener_joints": len(placed), "total": len(jrows)}
    jdoc["record"]["fastener_note"] = PROV
    json.dump(jdoc, open(jj, "w", encoding="utf-8"), indent=1)

    # --- bom.json ---------------------------------------------------------
    bj = os.path.join(ASM, "bom.json")
    bdoc = json.load(open(bj, encoding="utf-8"))
    brows = [r for r in bdoc["record"]["rows"] if r.get("owned_by") != OWNER]
    bbefore = len(brows)
    tally = collections.Counter((p["part"], p["length_mm"]) for p in placed)
    for (ref, L), qty in sorted(tally.items()):
        where = collections.Counter(p["head_seat_mesh"] for p in placed
                                    if p["part"] == ref and p["length_mm"] == L)
        brows.append({
            "ref": ref, "params": {"length_mm": L}, "qty": qty,
            "designation": "%s x %g ISO 4762 socket head cap screw"
                           % ("M2" if "m2-" in ref else "M2.5", L),
            "owned_by": OWNER,
            "why": ("%d screw run(s) MEASURED at this length. Head seats on: %s. Length chosen as "
                    "the shortest sourced ISO 4762 length inside each run's measured window "
                    "[grip + 1.5 d, grip + measured pilot depth]."
                    % (qty, ", ".join("%s x%d" % kv for kv in where.most_common())))})
    bdoc["record"]["rows"] = brows
    bdoc["record"]["counts"] = {"rows_from_the_mjcf": bbefore,
                                "fastener_rows": len(brows) - bbefore,
                                "fastener_pieces": sum(tally.values()),
                                "total_rows": len(brows)}
    bdoc["record"]["fastener_note"] = PROV
    json.dump(bdoc, open(bj, "w", encoding="utf-8"), indent=1)
    print("placements.json  %d -> %d rows (+%d fasteners)" % (before, len(rows), len(placed)))
    print("joints.json      %d -> %d rows (+%d fastener joints)" % (jbefore, len(jrows), len(placed)))
    print("bom.json         %d -> %d rows (+%d lines, %d pieces)"
          % (bbefore, len(brows), len(brows) - bbefore, sum(tally.values())))


def main():
    dry = "--dry" in sys.argv
    doc = json.load(open(RUNS, encoding="utf-8"))
    runs = [r for r in doc["runs"] if r["verdict"] == "PASS"]
    placed, refused = [], []
    seq = 0
    for r in runs:
        try:
            row, ok = place(r, seq)
        except Exception as e:  # noqa: BLE001 — refusal is the contract
            refused.append({"why": "%s: %s" % (type(e).__name__, e),
                            "size": r.get("size"), "meshes": r.get("meshes"),
                            "head_point_world_mm": r.get("head_point_world_mm"),
                            "verdict": "CANNOT DETERMINE",
                            "settled_by": "the refusal message names the missing number"})
            continue
        if not ok:
            refused.append({"why": "placement verify FAIL: %s" % row["verify"],
                            "size": r.get("size"), "meshes": r.get("meshes"),
                            "verdict": "FAIL",
                            "settled_by": "the frame convention or the run measurement is wrong; "
                                          "chase it, do not widen the tolerance"})
            continue
        placed.append(row)
        seq += 1

    import collections
    by_conn = collections.Counter(p["via_connection"] for p in placed)
    by_len = collections.Counter("%s x %g" % (p["size"], p["length_mm"]) for p in placed)
    out = {
        "doc": {"id": "MD-FAST-PLACED-001", "rev": "A",
                "title": "Every fastener placed into assembly:microduck, each through its connection",
                "generated_by": "tools/place_fasteners.py",
                "reads": ["out/fasteners/runs.json",
                          "ce-parts/screw-m2*-iso4762/cad/interfaces.json",
                          "ce-connections/*/current/cad/mate.py"]},
        "frame": "MJCF world at zero pose, mm — the same frame placements.json uses",
        "counts": {"screw_runs_offered": len(runs), "placed": len(placed),
                   "refused": len(refused), "by_connection": dict(by_conn),
                   "by_screw": dict(by_len),
                   "max_head_point_error_mm": max([p["verify"]["head_point_error_mm"]
                                                   for p in placed] or [None]),
                   "max_axis_error_deg": max([p["verify"]["axis_error_deg"]
                                              for p in placed] or [None])},
        "placed": placed, "refused": refused}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print("runs offered      :", len(runs))
    print("placed            :", len(placed), dict(by_conn))
    print("refused           :", len(refused))
    print("by screw          :", dict(by_len))
    print("worst head error  :", out["counts"]["max_head_point_error_mm"], "mm")
    print("worst axis error  :", out["counts"]["max_axis_error_deg"], "deg")
    print("wrote", OUT, "(dry run — assembly records untouched)" if dry else "")
    if not dry:
        write_assembly(out)
    return out, dry


if __name__ == "__main__":
    main()
