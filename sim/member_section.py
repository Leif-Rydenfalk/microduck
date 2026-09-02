#!/usr/bin/env python3
"""member_section.py — cross-section properties of a slender member along its
long axis, read off OUR rebuilt mesh with FreeCAD's Mesh.crossSections, for an
independent Euler cross-check of the ce-struct buckling factor (F1 skeptic
finding 9, 2026-09-03: the shin's factor had no localisation test).

    ce-cad/bin/cad sim/member_section.py   -> out/sim-evidence/section_microduck-shin.json

At each of N stations along the axis the section loops are chained into a face
(FaceMakerBullseye: outer loop + holes), and area, centroid and the principal
second moments about the centroid are read off the face. Euler: P_cr = pi^2 E
I_min / (K L)^2 with the WEAKEST station's I_min, for K = 0.7 (fixed-pinned),
1 (pinned-pinned) and 2 (fixed-free) — a bracket, not a number: the shin is
neither a prismatic column nor ideally supported, and the point is only
whether the eigen-solver's factor is of the order a member mode must have.
"""
import json
import math
import os
import time

import FreeCAD
import Mesh
import Part

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVID = os.path.join(ROOT, "out", "sim-evidence")
E_PLA_TABLE = 3500.0     # MPa, ce-cad/cecad/fits.py MATERIALS['PLA'] youngs 3.5 GPa (class tier)
E_PLA_TDS = 2300.0       # MPa, research/tds/prusament-pla-tds-2021-10-en.pdf, ISO 527-1, printed horizontal
MEMBERS = [("microduck-shin", "sim/meshes_ours/leg.stl", "z", 24)]


def section(m, axis, at):
    ai = "xyz".index(axis)
    base = FreeCAD.Vector(0, 0, 0); base[ai] = at
    nrm = FreeCAD.Vector(0, 0, 0); nrm[ai] = 1
    loops = m.crossSections([(base, nrm)], 0.00001, False)[0]
    wires = []
    for loop in loops:
        pts = [FreeCAD.Vector(p) for p in loop]
        if len(pts) < 3:
            continue
        if (pts[0] - pts[-1]).Length > 1e-6:
            pts.append(pts[0])
        try:
            w = Part.makePolygon(pts)
            Part.Face(w)
            wires.append(w)
        except Exception:  # noqa: BLE001
            continue
    if not wires:
        return None
    face = Part.makeFace(wires, "Part::FaceMakerBullseye")
    faces = face.Faces if face.ShapeType != "Face" else [face]
    # several disjoint faces at one station (ribs): sum area, combine inertia about the common centroid
    A = sum(f.Area for f in faces)
    cx = sum(f.Area * f.CenterOfMass.x for f in faces) / A
    cy = sum(f.Area * f.CenterOfMass.y for f in faces) / A
    cz = sum(f.Area * f.CenterOfMass.z for f in faces) / A
    C = FreeCAD.Vector(cx, cy, cz)
    # inertia about the common centroid: parallel axis from each face's own centroid
    u, v = [j for j in range(3) if j != ai]
    Iuu = Ivv = Iuv = 0.0
    for f in faces:
        M = f.MatrixOfInertia          # about the face's own centre of mass
        d = f.CenterOfMass - C
        du, dv = d[u], d[v]
        Iuu += M.A[u * 4 + u] + f.Area * dv * dv
        Ivv += M.A[v * 4 + v] + f.Area * du * du
        Iuv += M.A[u * 4 + v] - f.Area * du * dv
    # principal values of the 2x2 tensor [[Iuu, Iuv],[Iuv, Ivv]] (MatrixOfInertia off-diagonals are -integral(uv))
    mean = 0.5 * (Iuu + Ivv); r = math.sqrt((0.5 * (Iuu - Ivv)) ** 2 + Iuv ** 2)
    return {"at_mm": round(at, 4), "loops": len(loops), "faces": len(faces), "area_mm2": round(A, 4),
            "centroid_mm": [round(cx, 4), round(cy, 4), round(cz, 4)], "I_uu_mm4": round(Iuu, 4), "I_vv_mm4": round(Ivv, 4), "I_uv_mm4": round(Iuv, 4),
            "I_min_mm4": round(mean - r, 4), "I_max_mm4": round(mean + r, 4)}


def main():
    for slug, stl, axis, n in MEMBERS:
        m = Mesh.Mesh(os.path.join(ROOT, stl))
        bb = m.BoundBox
        ai = "xyz".index(axis)
        lo, hi = [bb.XMin, bb.YMin, bb.ZMin][ai], [bb.XMax, bb.YMax, bb.ZMax][ai]
        L = hi - lo
        stations = []
        for k in range(n):
            at = lo + (k + 0.5) * L / n
            s = section(m, axis, at)
            if s:
                stations.append(s)
        weakest = min(stations, key=lambda s: s["I_min_mm4"])
        euler = {}
        for E_name, E in (("table_3500", E_PLA_TABLE), ("tds_2300", E_PLA_TDS)):
            euler[E_name] = {("K_%g" % K): round(math.pi ** 2 * E * weakest["I_min_mm4"] / (K * L) ** 2, 4) for K in (0.7, 1.0, 2.0)}
        rec = {"study": "section_" + slug, "part": "part:" + slug, "generated": time.strftime("%Y-%m-%dT%H:%M:%S"), "script": "sim/member_section.py",
               "inputs": {"mesh": stl, "long_axis": axis, "length_mm": round(L, 4), "stations": n, "bbox_mm": [round(bb.XLength, 4), round(bb.YLength, 4), round(bb.ZLength, 4)],
                          "E_MPa": {"table_3500": {"value": E_PLA_TABLE, "source": "ce-cad/cecad/fits.py MATERIALS['PLA'] youngs 3.5 GPa (class tier)"},
                                    "tds_2300": {"value": E_PLA_TDS, "source": "research/tds/prusament-pla-tds-2021-10-en.pdf ISO 527-1 tensile modulus 2.3 +- 0.1 GPa printed horizontal"}}},
               "method": "Mesh.crossSections at %d equally spaced stations; loops -> FaceMakerBullseye face(s); area, centroid, principal second moments about the station centroid; Euler P_cr = pi^2 E I_min/(K L)^2 on the weakest station" % n,
               "outputs": {"stations": stations, "weakest_station": weakest, "euler_critical_N": euler,
                           "note": "a BRACKET for the order of magnitude only: the member is not prismatic (area %.1f-%.1f mm2 along z) and the real end conditions are screws and a servo horn, not ideal pins" % (
                               min(s["area_mm2"] for s in stations), max(s["area_mm2"] for s in stations))},
               "verdict": "PASS", "why": "measured; a section table has no pass/fail of its own — it is consumed by sim/struct_ce.py as the Euler cross-check of the eigen-solver",
               "artifacts": [], "looked_at": []}
        path = os.path.join(EVID, rec["study"] + ".json")
        json.dump(rec, open(path, "w"), indent=1)
        print("wrote", path, "weakest I_min %.4f mm4 at %s=%.3f, Euler K=2 table %.2f N / K=1 %.2f N" % (
            weakest["I_min_mm4"], axis, weakest["at_mm"], euler["table_3500"]["K_2"], euler["table_3500"]["K_1"]))


if __name__ == "__main__":
    main()
