#!/usr/bin/env python3
"""hat_connectors.py — LOCATE every connector on the Robot HAT in assembly world
coordinates, under both revisions of the board, and measure the difference.

    python3 tools/hat_connectors.py      -> out/wiring/hat-connectors.json

WHY. out/wiring/cables3d.json records five HAT-end cable runs whose endpoint is
the *mesh centroid* with the reason "connector positions unpublished". That
reason is now false: Pollen published the board (Apache-2.0) and this repo has
it at reference/pollen-elec-rpi-robot-hat. The connector positions are a
MEASUREMENT and this tool takes it.

THE TRAP THIS TOOL EXISTS TO KEEP IN VIEW. out/pcb/hat/mesh-revision.json (lane
internals-build2) settled that the HAT mesh in our assembly is the PRE-RELEASE
revision fbd885d, which Pollen never produced, and that its connector bank sits
at the other end of the board. So there are two answers to "where does the servo
cable plug in", and this tool reports BOTH:

    as_modelled  the position on the board that is actually in our CAD
    as_built     the position on the board that is in the real robot (C1)

and the vector between them. Nothing here picks one. Picking one is
part:microduck-robot-hat-pcb's iteration, not the harness's.

FRAMES. The mesh's own local frame and the KiCad board frame are the SAME
coordinates: the STL bbox is checked against the board outline in this tool and
the check is written into the output. Board z = 0 is the bottom substrate face
(the mesh spans z 0..0.840 = 0.770 dielectric + 2 x 0.035 inner copper), so the
top surface a vertical connector seats on is z = 0.960 (0.840 + 0.070 outer
copper + 0.010 mask + 0.040 -- read off the fitted component z_range in
out/pcb/hat/components.json, whose top-side parts all start at 0.960).
"""
import json, math, os, re, struct, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLACEMENTS = R + "/ce-assemblies/microduck/current/placements.json"
COMPONENTS = R + "/out/pcb/hat/components.json"
MESHREV = R + "/out/pcb/hat/mesh-revision.json"
KICAD = R + "/reference/pollen-elec-rpi-robot-hat/elec_RPI_Robot_HAT.kicad_pcb"
MESH = R + "/reference/pollen-microduck-rl/assets/elec_rpi_robot_hat_pcb.stl"
OUT = R + "/out/wiring/hat-connectors.json"

TOP_SURFACE_Z = 0.96      # board mm; see the docstring
# the dev-revision (fbd885d) 0.95 mm connector-hole columns, read off the MESH by
# lane internals-build2 and quoted verbatim in out/pcb/hat/mesh-revision.json
DEV_COLS = {"3pin": [53.500, 58.300], "4pin": [43.850, 48.650]}


def qmat(q):
    w, x, y, z = q
    n = math.sqrt(w * w + x * x + y * y + z * z)
    w, x, y, z = w / n, x / n, y / n, z / n
    return [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]


def mul(M, v):
    return [sum(M[i][k] * v[k] for k in range(3)) for i in range(3)]


def add(a, b):
    return [a[i] + b[i] for i in range(3)]


def stl_bbox_mm(path, scale=1000.0):
    with open(path, "rb") as f:
        head = f.read(84)
        n = struct.unpack("<I", head[80:84])[0]
        lo = [1e9] * 3
        hi = [-1e9] * 3
        for _ in range(n):
            rec = f.read(50)
            for k in range(3):
                px, py, pz = struct.unpack("<3f", rec[12 + 12 * k:24 + 12 * k])
                for j, val in enumerate((px, py, pz)):
                    val *= scale
                    lo[j] = min(lo[j], val)
                    hi[j] = max(hi[j], val)
    return n, [round(v, 4) for v in lo], [round(v, 4) for v in hi]


def kicad_footprints(path):
    """{refdes: {"at":(x,y,rot), "pads":[(name,lx,ly)], "nets":{pad:net}}} in KiCad mm."""
    s = open(path).read()
    out = {}
    i = 0
    while True:
        i = s.find("(footprint ", i)
        if i < 0:
            break
        depth, j = 0, i
        while j < len(s):
            if s[j] == "(":
                depth += 1
            elif s[j] == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        blk = s[i:j + 1]
        i = j + 1
        m = re.search(r'\(property "Reference" "([^"]+)"', blk)
        if not m:
            continue
        ref = m.group(1)
        a = re.search(r'\(at ([\-0-9.]+) ([\-0-9.]+)(?: ([\-0-9.]+))?\)', blk)
        at = (float(a.group(1)), float(a.group(2)), float(a.group(3) or 0.0)) if a else None
        pads = []
        for pm in re.finditer(r'\(pad "([^"]+)"[^\n]*\n?\s*\(at ([\-0-9.]+) ([\-0-9.]+)', blk):
            pads.append((pm.group(1), float(pm.group(2)), float(pm.group(3))))
        nets = {}
        for pm in re.finditer(r'\(pad "([^"]+)".{0,600}?\(net \d+ "([^"]*)"', blk, re.S):
            nets.setdefault(pm.group(1), pm.group(2))
        out[ref] = {"at": at, "pads": pads, "nets": nets}
    return out


def main():
    rows = json.load(open(PLACEMENTS))["record"]["rows"]
    hat = [r for r in rows if r.get("mesh") == "elec_rpi_robot_hat_pcb"]
    if len(hat) != 1:
        raise SystemExit("expected exactly one HAT placement row, found %d" % len(hat))
    hat = hat[0]
    Rm = qmat(hat["world_quat_wxyz"])
    t = hat["world_pos_mm"]

    ntri, lo, hi = stl_bbox_mm(MESH)
    comp = json.load(open(COMPONENTS))
    outline = comp["board"]["outline_bbox_mm"]
    frame_check = {
        "question": "is the mesh's own local frame the same as the KiCad board frame?",
        "mesh_stl": MESH.replace(R + "/", ""), "mesh_triangles": ntri,
        "mesh_bbox_mm": {"lo": lo, "hi": hi},
        "board_outline_bbox_mm": outline,
        "note": "the mesh is the fbd885d outline 65.025 x 30.025 and components.json's "
                "outline is the C1 outline 65.000 x 30.900, so the two bboxes are NOT "
                "expected to be identical; what is checked is that they share an origin.",
        "origin_delta_mm": [round(lo[0] - outline["x"][0], 4), round(hi[1] - outline["y"][1], 4)],
        "x_max_delta_mm": round(hi[0] - outline["x"][1], 4),
        "y_min_delta_mm": round(lo[1] - outline["y"][0], 4),
    }
    frame_check["verdict"] = ("PASS — the +x and -y extremes agree to 0.005 mm, so the two "
                              "revisions are drawn on one origin and a board coordinate is a "
                              "mesh coordinate"
                              if abs(frame_check["x_max_delta_mm"]) < 0.01
                              and abs(frame_check["y_min_delta_mm"]) < 0.02
                              else "FAIL — the frames do not share an origin: %s"
                              % frame_check)

    fps = kicad_footprints(KICAD)
    ox, oy = comp["board"]["origin_offset_kicad_mm"]
    by_ref = {c["refdes"]: c for c in comp["components"]}

    # the mirror the two revisions differ by, SOLVED not assumed
    dev_all = DEV_COLS["3pin"] + DEV_COLS["4pin"]
    built = []
    for ref in ("J13", "J14", "J11", "J3"):
        built.append(round(by_ref[ref]["pos_mm"][0], 4))
    # pair each dev column with the built column that a single mirror plane would send it to
    plane = None
    for d in dev_all:
        for b in built:
            p = (d + b) / 2.0
            ok = all(any(abs(2 * p - dd - bb) < 0.006 for bb in built) for dd in dev_all)
            if ok:
                plane = round(p, 4)
                break
        if plane:
            break
    mirror = {"plane_x_mm": plane,
              "residual_mm": (max(min(abs(2 * plane - d - b) for b in built) for d in dev_all)
                              if plane else None),
              "dev_columns_mm": dev_all,
              "built_columns_mm": sorted(built),
              "meaning": ("every 0.95 mm connector column of the pre-release mesh maps onto a "
                          "C1 column by ONE reflection about board x = %s mm, to the residual "
                          "given. It is a mirror, not a translation: the 3-pin bank moves "
                          "%.4f mm and the 4-pin bank %.4f mm, and the pin order reverses."
                          % (plane, DEV_COLS["3pin"][0] - min(built),
                             DEV_COLS["4pin"][0] - sorted(built)[2])) if plane else
                         "no single reflection maps the two revisions onto each other"}

    wanted = {"J13": ("EH 3-pin", 3, "Dynamixel TTL 3P — the XL330 bus"),
              "J14": ("EH 3-pin", 3, "Dynamixel TTL 3P — the XL330 bus"),
              "J3": ("EH 4-pin", 4, "RS-485 4P (U8 SIT3088E)"),
              "J11": ("EH 4-pin", 4, "RS-485 4P (U8 SIT3088E)"),
              "J5": ("SH 4-pin", 4, "Stemma/Qwiic I2C — the ToF board"),
              "J6": ("SH 4-pin", 4, "Stemma/Qwiic I2C"),
              "J7": ("SH 4-pin", 4, "Stemma/Qwiic I2C"),
              "J8": ("SH 4-pin", 4, "Stemma/Qwiic I2C"),
              "J4": ("2x20 header", 40, "40-pin GPIO to the Radxa Zero 3W"),
              "J1": ("Wago 2059-302", 2, "spring terminal"),
              "J2": ("Wago 2059-302", 2, "spring terminal"),
              "J9": ("Wago 2059-302", 2, "spring terminal")}

    conns = []
    for ref, (series, ncirc, what) in sorted(wanted.items()):
        c = by_ref.get(ref)
        fp = fps.get(ref)
        if c is None or fp is None:
            conns.append({"refdes": ref, "verdict": "CANNOT DETERMINE",
                          "why": "not present in %s" % ("components.json" if c is None else "the kicad_pcb")})
            continue
        # pad 1 in BOARD coordinates, from the footprint origin + its rotation
        ax, ay, arot = fp["at"]
        th = math.radians(arot)
        pad1 = [p for p in fp["pads"] if p[0] == "1"]
        p1b = None
        if pad1:
            lx, ly = pad1[0][1], pad1[0][2]
            kx = ax + lx * math.cos(th) - ly * math.sin(th)
            ky = ay + lx * math.sin(th) + ly * math.cos(th)
            p1b = [round(kx - ox, 4), round(-(ky - oy), 4)]
        centre = [round(c["pos_mm"][0], 4), round(c["pos_mm"][1], 4)]
        zr = c.get("z_range_mm")
        side = c.get("side")
        zsurf = TOP_SURFACE_Z if side == "top" else 0.0
        origin_b = [centre[0], centre[1], zsurf]
        zaxis_b = [0.0, 0.0, 1.0 if side == "top" else -1.0]
        xaxis_b = None
        if p1b:
            d = [centre[0] - p1b[0], centre[1] - p1b[1]]
            n = math.hypot(*d)
            if n > 1e-6:
                xaxis_b = [round(d[0] / n, 6), round(d[1] / n, 6), 0.0]
        row = {"refdes": ref, "series": series, "circuits": ncirc, "what": what,
               "side": side, "nets_by_pin": fp["nets"],
               "board_frame": {"origin_mm": origin_b, "z_axis": zaxis_b, "x_axis": xaxis_b,
                               "x_axis_meaning": "pin 1 -> pin N along the row" if xaxis_b else None,
                               "pin1_board_mm": p1b,
                               "body_mm": c.get("body_mm"), "z_range_mm": zr},
               "as_modelled": None}
        w_o = add(mul(Rm, origin_b), t)
        w_z = mul(Rm, zaxis_b)
        w_x = mul(Rm, xaxis_b) if xaxis_b else None
        row["as_built_world"] = {"origin_mm": [round(v, 4) for v in w_o],
                                 "z_axis": [round(v, 6) for v in w_z],
                                 "x_axis": [round(v, 6) for v in w_x] if w_x else None,
                                 "basis": "C1 (release) placement from out/pcb/hat/components.json "
                                          "(manufacturer POS) put through the HAT placement row of "
                                          "ce-assemblies/microduck/current/placements.json"}
        if plane and ref in ("J13", "J14", "J3", "J11"):
            ob = [round(2 * plane - centre[0], 4), centre[1], zsurf]
            wo2 = add(mul(Rm, ob), t)
            row["as_modelled"] = {
                "board_mm": ob,
                "world_origin_mm": [round(v, 4) for v in wo2],
                "delta_to_as_built_mm": round(math.dist(wo2, w_o), 4),
                "basis": "the position this connector occupies on the board that is ACTUALLY in "
                         "our CAD (pre-release fbd885d), obtained by reflecting the C1 position "
                         "about board x = %s mm — the plane solved above from the mesh's own "
                         "0.95 mm hole columns" % plane}
        conns.append(row)

    doc = {"$triad": 1, "kind": "hat-connector-frames",
           "generated_by": "tools/hat_connectors.py",
           "record": {
               "ref": "part:microduck-robot-hat-pcb",
               "units": "mm",
               "frame": "assembly world = MJCF world at the zero pose, the frame of "
                        "wiring/cables.json and out/wiring/cables3d.json",
               "hat_placement_row": {"body": hat["body"], "world_pos_mm": hat["world_pos_mm"],
                                     "world_quat_wxyz": hat["world_quat_wxyz"],
                                     "source": hat.get("source")},
               "board_frame_check": frame_check,
               "revision_mirror": mirror,
               "top_surface_z_mm": TOP_SURFACE_Z,
               "counts": {"connectors_located": sum(1 for c in conns if c.get("as_built_world")),
                          "connectors_asked_for": len(wanted),
                          "with_both_revisions": sum(1 for c in conns if c.get("as_modelled"))},
               "what_this_replaces": "out/wiring/cables3d.json records five HAT-end runs with "
                                     "why_unlocated 'HAT mesh centroid (bbox centre through the "
                                     "placement) — connector positions unpublished'. They are "
                                     "published and they are here.",
               "connectors": conns}}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(doc, open(OUT, "w"), indent=1)
    print("frame check:", frame_check["verdict"])
    print("mirror plane x = %s mm, residual %s mm" % (mirror["plane_x_mm"], mirror["residual_mm"]))
    for c in conns:
        if c.get("as_built_world"):
            am = c.get("as_modelled")
            print("%-4s %-14s as-built world %s%s" % (
                c["refdes"], c["series"],
                c["as_built_world"]["origin_mm"],
                ("   as-modelled %s  delta %.4f mm" % (am["world_origin_mm"], am["delta_to_as_built_mm"]))
                if am else ""))
        else:
            print("%-4s CANNOT DETERMINE %s" % (c["refdes"], c.get("why")))
    print("wrote", OUT)


main()
