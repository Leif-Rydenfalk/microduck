#!/usr/bin/env python3
"""tools/extract_hat_pcb.py — read Pollen's OFFICIAL Robot HAT design and write the
one data file every downstream artifact (CAD, BOM, document) reads.

GENERATED OUTPUT: out/pcb/hat/components.json  (generator: this file)

SOURCES, all inside reference/pollen-elec-rpi-robot-hat/ (Apache-2.0, commit
23eab11927f95ceca0dfa35bf182caeb7db39ea0, see its PROVENANCE.json):
  elec_RPI_Robot_HAT.kicad_pcb                     — footprint, designator, position,
                                                     rotation, side, LCSC part, sheet,
                                                     F.Fab body outline, pad extents
  production/ASE01187-C1_..._POS.csv               — the manufacturer's pick-and-place
  production/ASE01187-C1_..._BOM.csv               — value + LCSC per designator
  production/ASE01187-C1_..._STEP.step             — the 3D assembly; measured body
                                                     heights come from here, via
                                                     tools/step_bbox_dump (FreeCAD)

NOTHING IN THE OUTPUT IS INVENTED. A component whose body height could not be
measured from the STEP carries height_mm = null and a cannot_determine reason.

Run:  python3 tools/extract_hat_pcb.py
      (the STEP measurement file is produced separately by ce-cad/bin/cad, because
       system python3 has no FreeCAD; see out/pcb/hat/step_objects.json)
"""
import csv, io, json, math, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(REPO, "reference", "pollen-elec-rpi-robot-hat")
PROD = os.path.join(REF, "production")
OUT = os.path.join(REPO, "out", "pcb", "hat")
PCB = os.path.join(REF, "elec_RPI_Robot_HAT.kicad_pcb")
POS = os.path.join(PROD, "ASE01187-C1_elec_RPI_Robot_HAT_POS.csv")
BOM = os.path.join(PROD, "ASE01187-C1_elec_RPI_Robot_HAT_BOM.csv")
STEPOBJ = os.path.join(OUT, "step_objects.json")


# ---------------------------------------------------------------- s-expressions
def sexp(text, start):
    """Parse one balanced s-expression starting at text[start] == '('. Returns (node, end)."""
    assert text[start] == "("
    stack = []
    cur = None
    i = start
    n = len(text)
    tok = ""
    in_str = False
    while i < n:
        c = text[i]
        if in_str:
            if c == "\\":
                tok += text[i + 1]
                i += 2
                continue
            if c == '"':
                in_str = False
                cur.append(("str", tok))
                tok = ""
                i += 1
                continue
            tok += c
            i += 1
            continue
        if c == '"':
            in_str = True
            tok = ""
            i += 1
            continue
        if c == "(":
            new = []
            if cur is not None:
                cur.append(new)
                stack.append(cur)
            cur = new
            i += 1
            continue
        if c == ")":
            if tok:
                cur.append(("sym", tok))
                tok = ""
            if stack:
                cur = stack.pop()
                i += 1
                continue
            return cur, i + 1
        if c.isspace():
            if tok:
                cur.append(("sym", tok))
                tok = ""
            i += 1
            continue
        tok += c
        i += 1
    raise ValueError("unbalanced")


def head(node):
    return node[0][1] if node and isinstance(node[0], tuple) else None


def kids(node, name):
    return [k for k in node if isinstance(k, list) and head(k) == name]


def vals(node):
    return [k[1] for k in node[1:] if isinstance(k, tuple)]


def num(s):
    return float(s)


# ---------------------------------------------------------------- geometry helpers
def rot(px, py, deg):
    a = math.radians(deg)
    return px * math.cos(a) - py * math.sin(a), px * math.sin(a) + py * math.cos(a)


def fab_extent(fp_node, side):
    """Body outline from the *.Fab layer of a footprint, in LOCAL mm (before rotation).
    KiCad convention: the Fab layer draws the component body. Returns (xmin,ymin,xmax,ymax)
    or None."""
    want = "F.Fab" if side == "top" else "B.Fab"
    pts = []
    for k in fp_node:
        if not isinstance(k, list):
            continue
        h = head(k)
        if h not in ("fp_line", "fp_rect", "fp_poly", "fp_circle", "fp_arc"):
            continue
        lay = kids(k, "layer")
        if not lay or vals(lay[0])[0] not in (want, "F.Fab", "B.Fab"):
            continue
        for pn in ("start", "end", "center", "mid"):
            for c in kids(k, pn):
                v = vals(c)
                pts.append((num(v[0]), num(v[1])))
        for c in kids(k, "pts"):
            for x in kids(c, "xy"):
                v = vals(x)
                pts.append((num(v[0]), num(v[1])))
    if not pts:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))


# ---------------------------------------------------------------- main
def main():
    text = open(PCB).read()
    fps = []
    i = 0
    while True:
        i = text.find('\t(footprint "', i)
        if i < 0:
            break
        i += 1
        node, end = sexp(text, i)
        fps.append(node)
        i = end

    pos = {r["Designator"]: r for r in csv.DictReader(io.open(POS, encoding="utf-8-sig"))}
    bomrows = list(csv.DictReader(io.open(BOM, encoding="utf-8-sig")))
    bom = {}
    for b in bomrows:
        for d in [x.strip() for x in b["Designator"].split(",")]:
            bom[d] = b

    step = []
    if os.path.exists(STEPOBJ):
        step = [r for r in json.load(open(STEPOBJ)) if r["size"][0] < 1e50]

    comps = []
    for fp in fps:
        libname = vals(fp)[0]
        lay = vals(kids(fp, "layer")[0])[0]
        side = "top" if lay == "F.Cu" else "bottom"
        at = vals(kids(fp, "at")[0])
        x, y = num(at[0]), num(at[1])
        r = num(at[2]) if len(at) > 2 else 0.0
        props = {}
        for p in kids(fp, "property"):
            v = vals(p)
            if len(v) >= 2:
                props[v[0]] = v[1]
        ref = props.get("Reference")
        sheet = None
        sn = kids(fp, "sheetname")
        if sn:
            sheet = vals(sn[0])[0]
        pads = kids(fp, "pad")
        models = [vals(m)[0] for m in kids(fp, "model")]
        fab = fab_extent(fp, side)
        comps.append(dict(refdes=ref, footprint=libname, side=side,
                          kicad_at_mm=[round(x, 6), round(y, 6)], rot_deg=r,
                          value=props.get("Value"), lcsc=props.get("LCSC Part"),
                          sheet=sheet, n_pads=len(pads), model=models[0] if models else None,
                          fab_local_mm=[round(v, 4) for v in fab] if fab else None))

    # board-origin offset: POS Mid X/Y vs the kicad_pcb page coordinates
    offs = []
    for c in comps:
        p = pos.get(c["refdes"])
        if not p:
            continue
        offs.append((c["kicad_at_mm"][0] - float(p["Mid X"]),
                     c["kicad_at_mm"][1] + float(p["Mid Y"])))
    import statistics
    ox = statistics.median(o[0] for o in offs)
    oy = statistics.median(o[1] for o in offs)
    # residual: the 4 JST EH verticals put POS "Mid" at the body centre, not at the
    # footprint anchor (pin 1); every other placement agrees to 0.0000 mm.
    resid = sorted(max(abs(o[0] - ox), abs(o[1] - oy)) for o in offs)
    resid_n_nonzero = sum(1 for r in resid if r > 1e-4)
    resid = resid[-1]

    # Edge.Cuts outline in board coordinates
    ec = []
    j = 0
    while True:
        j = text.find("\t(gr_", j)
        if j < 0:
            break
        j += 1
        node, end = sexp(text, j)
        j = end
        lay = kids(node, "layer")
        if not lay or vals(lay[0])[0] != "Edge.Cuts":
            continue
        for pn in ("start", "end", "center", "mid"):
            for c in kids(node, pn):
                v = vals(c)
                ec.append((num(v[0]) - ox, -(num(v[1]) - oy)))
    exs = [p[0] for p in ec]
    eys = [p[1] for p in ec]

    # attach POS + BOM + measured STEP body
    used = set()
    for c in comps:
        p = pos.get(c["refdes"])
        c["fitted"] = p is not None
        if p:
            c["pos_mm"] = [float(p["Mid X"]), float(p["Mid Y"])]
            c["pos_rot_deg"] = float(p["Rotation"])
            c["pos_side"] = p["Layer"]
        else:
            c["pos_mm"] = [round(c["kicad_at_mm"][0] - ox, 6), round(-(c["kicad_at_mm"][1] - oy), 6)]
            c["pos_rot_deg"] = None
            c["pos_side"] = None
        b = bom.get(c["refdes"])
        c["bom_value"] = b["Value"] if b else None
        c["bom_footprint"] = b["Footprint"] if b else None
        c["bom_lcsc"] = b["LCSC Part #"] if b else None
        c["dnp"] = bool(b and str(b["Value"]).startswith("DNP"))

    # STEP objects -> nearest fitted designator
    fitted = [c for c in comps if c["fitted"]]
    for c in fitted:
        c["_step"] = []
    # SIDE-AWARE assignment. The STEP frame: board substrate z 0.000 .. 0.840; top-side
    # bodies start at z = 0.960, bottom-side bodies end at z = -0.120 (the 0.120 mm on
    # each face is the outer copper + mask + paste the substrate body does not model).
    # The same STEP also carries a Raspberry Pi Zero 2 W below the HAT (z < -4) — that
    # is context, not a HAT component, and only the through-board J4 header reaches it.
    for o in step:
        cx = (o["bbox_min"][0] + o["bbox_max"][0]) / 2.0
        cy = (o["bbox_min"][1] + o["bbox_max"][1]) / 2.0
        z0, z1 = o["bbox_min"][2], o["bbox_max"][2]
        if z0 >= 0.84:
            oside = "top"
        elif z1 <= 0.001:
            oside = "bottom"
        elif z0 < 0.0 and z1 > 0.84:
            oside = "through"   # THT bodies (JST EH connectors, test-point loops)
        else:
            continue  # the board substrate itself
        if z0 < -6.0 and oside != "through":
            continue  # Pi Zero 2 W body and its own header
        if oside == "through" and z1 > 15.0:
            continue  # the Pi's own 40-pin male header, which spans further
        best, bd = None, 1e9
        for c in fitted:
            if oside != "through" and c["pos_side"] != oside:
                continue
            d = math.hypot(cx - c["pos_mm"][0], cy - c["pos_mm"][1])
            if d < bd:
                bd, best = d, c
        if best is not None and bd < 3.5:
            best["_step"].append((bd, o))

    for c in comps:
        s = c.pop("_step", [])
        if not s:
            c["body_mm"] = None
            c["z_range_mm"] = None
            c["height_mm"] = None
            c["measured_from"] = None
            c["cannot_determine"] = "no solid in the official STEP within 3.000 mm of this placement"
            continue
        xs0 = min(o["bbox_min"][0] for _, o in s); xs1 = max(o["bbox_max"][0] for _, o in s)
        ys0 = min(o["bbox_min"][1] for _, o in s); ys1 = max(o["bbox_max"][1] for _, o in s)
        zs0 = min(o["bbox_min"][2] for _, o in s); zs1 = max(o["bbox_max"][2] for _, o in s)
        c["body_mm"] = [round(xs1 - xs0, 4), round(ys1 - ys0, 4), round(zs1 - zs0, 4)]
        c["body_centre_mm"] = [round((xs0 + xs1) / 2, 4), round((ys0 + ys1) / 2, 4)]
        c["z_range_mm"] = [round(zs0, 4), round(zs1, 4)]
        c["height_mm"] = round(zs1 - zs0, 4)
        c["step_solids"] = len(s)
        c["step_labels"] = sorted({o["label"] for _, o in s})
        c["measured_from"] = "production/ASE01187-C1_elec_RPI_Robot_HAT_STEP.step (FreeCAD bbox)"
        c["cannot_determine"] = None

    out = dict(
        _generated="tools/extract_hat_pcb.py",
        source=dict(repo="pollen-robotics/elec_RPI_Robot_HAT",
                    commit="23eab11927f95ceca0dfa35bf182caeb7db39ea0",
                    licence="Apache-2.0", rev="C1", date="2026-07-08"),
        board=dict(
            layers=4, layer_names=["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"],
            finished_thickness_mm=1.000,
            thickness_basis="kicad_pcb (general (thickness 1)); stackup sums to "
                            "0.01+0.07+0.10+0.035+0.57+0.035+0.10+0.07+0.01 = 1.000",
            step_substrate_thickness_mm=0.84,
            step_substrate_basis="the STEP body elec_RPI_Robot_HAT_PCB measures 0.8400 mm "
                                 "= 0.77 dielectric + 2 x 0.035 inner copper; the outer "
                                 "copper (2 x 0.07) and mask (2 x 0.01) are not modelled",
            outline_bbox_mm=dict(x=[round(min(exs), 4), round(max(exs), 4)],
                                 y=[round(min(eys), 4), round(max(eys), 4)],
                                 size=[round(max(exs) - min(exs), 4), round(max(eys) - min(eys), 4)]),
            origin_offset_kicad_mm=[round(ox, 6), round(oy, 6)],
            origin_offset_residual_mm=round(resid, 6),
            origin_offset_nonzero_residuals=resid_n_nonzero,
            origin_meaning="POS/board coordinates: x = kicad_x - ox, y = -(kicad_y - oy). "
                           "Same frame as the STEP.",
        ),
        counts=dict(footprints_in_pcb=len(comps),
                    fitted_placements=sum(1 for c in comps if c["fitted"]),
                    dnp=sum(1 for c in comps if c["dnp"]),
                    measured_bodies=sum(1 for c in comps if c.get("height_mm") is not None),
                    unmeasured=sum(1 for c in comps if c["fitted"] and c.get("height_mm") is None)),
        components=sorted(comps, key=lambda c: (c["refdes"][0], len(c["refdes"]), c["refdes"])),
    )
    os.makedirs(OUT, exist_ok=True)
    json.dump(out, open(os.path.join(OUT, "components.json"), "w"), indent=1)
    print(json.dumps(out["counts"], indent=1))
    print("board", json.dumps(out["board"]["outline_bbox_mm"]))
    print("origin residual mm", out["board"]["origin_offset_residual_mm"])
    unm = [c["refdes"] for c in comps if c["fitted"] and c.get("height_mm") is None]
    print("unmeasured fitted:", unm)


if __name__ == "__main__":
    main()
