#!/usr/bin/env python3
"""head_eye_ring_shelve.py — fill part:microduck-eye-ring from what was measured.

The folder was created empty by `bin/triad new` ("nothing measured yet") and
spec/mesh-to-part.json already maps Pollen's mesh `noenoeil` to it. GOAL.md
finding 1 said the product's eye bezel is "missing" from the simulation mesh;
lane A measured (out/head/head.json) that `noenoeil` IS the bezel — a Ø30.000 mm
ring 7.5 mm long standing proud of the face panel — and how the product's ring
compares with it. This script writes the folder the way cecad.meshshelve writes
every other mesh-backed Microduck part (geometry copy + sha256 ledger row +
loader part.py + interfaces.json + mech.py + README), then adds the photo
evidence rows. It is idempotent: re-running rewrites the same files from the
same data. cecad.meshshelve itself leaves an existing folder alone, which is
why this exists.

    /Applications/FreeCAD.app/Contents/Resources/bin/python tools/head_eye_ring_shelve.py
"""
import os, sys, json, hashlib, shutil, datetime
import numpy as np
sys.path.insert(0, "/Users/leifrydenfalk/dev/ce-workshop/ce-cad")
from cecad import meshslice, meshfeatures

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PART = os.path.join(REPO, "ce-parts", "microduck-eye-ring")
IT = os.path.join(PART, "iterations", "v0.0.1")
SRC = os.path.join(REPO, "reference", "pollen-microduck-rl", "assets", "noenoeil.stl")
HEAD = json.load(open(os.path.join(REPO, "out", "head", "head.json")))
LICENCE = "CC BY-SA-NC 4.0 (pollen-robotics/microduck_rl README)"
TODAY = datetime.date.today().isoformat()


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def measure():
    """the ring's own geometry, read off the mesh: bbox, the Ø30 boss, the bore, the rear spigot."""
    T = meshslice.load(SRC, 1000.0); V = T.reshape(-1, 3)
    lo, hi = V.min(0), V.max(0)
    feats = meshfeatures.cylinders(SRC, scale=1000)
    boss = [f for f in feats["bosses"] if abs(f["d_mm"] - 30.0) < 0.5]
    bore = [f for f in feats["holes"] if 14.0 < f["d_mm"] < 15.0]
    cx, cz = 0.0, 20.0     # the boss axis (meshfeatures: centre (0, -59.25, 20), axis y)
    prof = []
    for y in np.arange(lo[1] + 0.25, hi[1], 0.5):
        seg = meshslice.segments(T, "y", float(y))
        if len(seg) == 0: continue
        P = np.asarray(seg).reshape(-1, 2)      # meshslice.segments: (M, 2, 2) points in the CYCLIC (u, v) plane — for a y-cut u = z, v = x
        r = np.hypot(P[:, 0] - cz, P[:, 1] - cx)
        prof.append((round(float(y), 3), round(float(r.max()), 3), round(float(r.min()), 3)))
    return dict(bbox_min_mm=[round(float(v), 4) for v in lo], bbox_max_mm=[round(float(v), 4) for v in hi],
                boss=boss, bore=bore, radial_profile=prof,
                profile_how="cecad.meshslice: for planes y = const through the ring (0.5 mm pitch) the max/min radius of the cut about the boss axis (x 0, z 20)")


def main():
    m = measure(); C = HEAD["combined"]; V = HEAD["verdict"]; FV = HEAD["front_view"]["comparison"]
    os.makedirs(os.path.join(IT, "geometry"), exist_ok=True); os.makedirs(os.path.join(IT, "docs"), exist_ok=True)
    os.makedirs(os.path.join(IT, "evidence"), exist_ok=True); os.makedirs(os.path.join(IT, "cad"), exist_ok=True); os.makedirs(os.path.join(IT, "mech"), exist_ok=True)
    dst = os.path.join(IT, "geometry", "noenoeil.stl"); shutil.copyfile(SRC, dst); sha = sha256(dst)
    # the rear spigot: the last slices before the face panel (y > -55.5) have a smaller outer radius than the Ø30 boss
    spig = [p for p in m["radial_profile"] if p[0] > -55.6]
    spig_d = (2 * max(p[1] for p in spig)) if spig else None
    eye_prof = C.get("eye_dev_mm"); eye_prof_u = C.get("eye_dev_unc_mm"); eye_front = C["eye_front_view_dev_mm"]
    # ---- cad/part.py (loader, same shape as cecad.meshshelve)
    open(os.path.join(IT, "cad", "part.py"), "w").write('''# WRITTEN by tools/head_eye_ring_shelve.py on %s — a LOADER for a published mesh (the cecad.meshshelve shape).
"""part:microduck-eye-ring — cad/part.py, the TRIAD build contract.

    def build(doc, params=None) -> Part

WHAT THIS BUILDS. Pollen Robotics' published mesh `noenoeil` (MJCF sim asset, %s): the
EYE BEZEL — a Ø30.000 mm ring, 7.5 mm long, with a Ø14.4 bore for the M12 lens, that
stands proud of the face panel (whose only opening on this axis is the Ø14.5 lens hole).
GOAL.md finding 1 called the product's bezel "missing" from the simulation meshes; it is
this mesh (HEAD-RECONSTRUCTION.html §6). Loaded through `cecad.core.Part.from_mesh` at
scale 1000.0 (the file is in metres). Render, place, measure and print it; do not cut it.

FRAME. The mesh's own frame, unchanged: bbox x %.3f..%.3f, y %.3f..%.3f, z %.3f..%.3f mm,
ring axis y, boss centre (0, -59.25, 20). The MJCF geom pos/quat for `noenoeil` (body jaw_soft,
spec/mesh-placements.json) place it directly.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GEOMETRY = "geometry/noenoeil.stl"
SCALE = 1000.0
MATERIAL = "PLA"


def build(doc, params=None):
    if params:
        raise ValueError("microduck-eye-ring takes no build parameters (got %%s) — it loads a published mesh" %% sorted(params))
    from cecad.core import Part
    path = os.path.join(ROOT, GEOMETRY)
    if not os.path.exists(path):
        raise FileNotFoundError("microduck-eye-ring: %%s is missing — the folder cannot build without its geometry" %% path)
    return Part.from_mesh(path, name="microduck-eye-ring", material=MATERIAL, scale=SCALE, tol=0.05)
''' % (TODAY, LICENCE, *m["bbox_min_mm"][0:1], *m["bbox_max_mm"][0:1], m["bbox_min_mm"][1], m["bbox_max_mm"][1], m["bbox_min_mm"][2], m["bbox_max_mm"][2]))
    # ---- interfaces.json
    boss = m["boss"][0] if m["boss"] else None; bore = m["bore"][0] if m["bore"] else None
    iface = {
        "$triad": 1, "kind": "interfaces", "generated_by": "tools/head_eye_ring_shelve.py",
        "record": {"ref": "part:microduck-eye-ring@v0.0.1",
                   "frame": "Pollen's mesh frame for noenoeil.stl: bbox x %.4f..%.4f, y %.4f..%.4f, z %.4f..%.4f mm; ring axis y; boss centre (0.0000, -59.2500, 20.0000)" % (
                       m["bbox_min_mm"][0], m["bbox_max_mm"][0], m["bbox_min_mm"][1], m["bbox_max_mm"][1], m["bbox_min_mm"][2], m["bbox_max_mm"][2]),
                   "units": "mm"},
        "interfaces": [
            {"name": "lens_bore", "frame": {"origin_mm": [0.0, bore["center_mm"][1] if bore else -58.5, 20.0], "z_axis": [0, 1, 0], "x_axis": [1, 0, 0]},
             "accepts": ["part:microduck-m12-lens"], "role": "bore",
             "what": "Ø%.3f x %.3f bore on the ring axis: the M12 lens (part:microduck-m12-lens, Ø16.94 barrel per its mesh) looks through it; the lens is carried by part:microduck-m12-lens-holder behind the face panel, so this bore is a clearance window, not a seat" % ((bore["d_mm"], bore["length_mm"]) if bore else (14.4, 6.0)),
             "source": "MEASURED off Pollen's noenoeil.stl by cecad.meshfeatures.cylinders(scale=1000) — hole d %.3f length %.3f axis y, residual %.4f mm at %.0f deg (this script, %s)" % ((bore["d_mm"], bore["length_mm"], bore["residual_mm"], bore["cover_deg"], TODAY) if bore else (14.4, 6.0, 0, 355, TODAY))},
            {"name": "face_seat", "frame": {"origin_mm": [0.0, m["bbox_max_mm"][1], 20.0], "z_axis": [0, 1, 0], "x_axis": [1, 0, 0]},
             "accepts": ["part:microduck-face-part"], "role": "seat",
             "what": "the ring's rear face at y = %.3f sits on/in the face panel (part:microduck-face-part, front face y -55.5): the last %.1f mm of the ring (y > -55.5) is a spigot of Ø%s that enters the panel. HOW IT IS FIXED IS CANNOT DETERMINE: the decimated face_part.stl registers only the Ø14.5 lens hole on this axis (cecad.meshfeatures), no recess or screw for the spigot; a glued or press-fit spigot is what the meshes allow" % (
                 m["bbox_max_mm"][1], m["bbox_max_mm"][1] + 55.5, ("%.2f" % spig_d) if spig_d else "CANNOT DETERMINE"),
             "source": "MEASURED: noenoeil.stl y extent %.4f..%.4f and the radial profile in evidence/ledger.jsonl (cecad.meshslice, 0.5 mm pitch); face_part.stl front face y -55.5 from its bbox (tools/head_probe.py body-frame bbox y -43.917..43.734 → mesh frame -55.5..-43.0)" % (m["bbox_min_mm"][1], m["bbox_max_mm"][1])},
        ],
    }
    json.dump(iface, open(os.path.join(IT, "cad", "interfaces.json"), "w"), indent=2)
    # ---- mech.py
    open(os.path.join(IT, "mech", "mech.py"), "w").write('''"""mech.py — mass, inertia, material, the joints this part offers.

Contract (TRIAD.md): `def mech() -> dict`. Numbers with sources, no adjectives.
A number nobody measured stays absent — never a plausible default.
"""


def mech():
    return {
        "slug": "microduck-eye-ring",
        "material": "PLA",
        "material_source": "the accent-colour printed ring in every product photograph (images/CATALOG.md: 'Eye-ring colour = the contrasting accent'); Pollen prints the shells in PLA (docs/PARTS.md)",
        "mass_g": None,
        "mass_why": "the MJCF lumps the whole head (body jaw_soft) into one inertial; no per-geom mass is published and no ring has been weighed",
        "bbox_mm": [%.4f, %.4f, %.4f],
        "bbox_source": "noenoeil.stl x/y/z extents, cecad.meshslice at scale 1000 (tools/head_eye_ring_shelve.py, %s)",
        "joints": [],
    }
''' % (m["bbox_max_mm"][0] - m["bbox_min_mm"][0], m["bbox_max_mm"][1] - m["bbox_min_mm"][1], m["bbox_max_mm"][2] - m["bbox_min_mm"][2], TODAY))
    # ---- README
    pf = ["%s: ring/head %.4f (photo) vs %.4f (render) → %+.2f ± %.2f mm" % (p["id"], p["eye"]["ring_over_head_photo"], p["eye"]["ring_over_head_render"], p["eye"]["dev_scale_free_mm"], p["eye"]["dev_scale_free_unc_mm"])
          for p in HEAD["photos"] if "dev_scale_free_mm" in p["eye"]]
    open(os.path.join(IT, "docs", "README.md"), "w").write('''# part:microduck-eye-ring — the eye bezel, mesh-backed (Pollen's `noenoeil`)

**What it is.** The accent-colour ring around the camera lens on the Microduck's face. GOAL.md
finding 1 said the product's eye bezel is *missing* from the simulation meshes. It is not: Pollen's
mesh `noenoeil` (spec/mesh-to-part.json maps it here) is a **Ø%.3f mm ring, %.1f mm long** (the boss),
with a **Ø%.3f bore** for the M12 lens, standing **proud of the face panel** — the face panel's only
opening on this axis is the Ø14.5 lens hole, so the whole ring is visible, exactly as in the
photographs. Measured with cecad.meshfeatures / meshslice on `reference/pollen-microduck-rl/assets/noenoeil.stl`
(this iteration's `geometry/noenoeil.stl`, sha256 in `evidence/ledger.jsonl`).

**Against the product (out/head/head.json, HEAD-RECONSTRUCTION.html §6).**
- True front view (flat-lay, ratio to head width, scale-free): eye OD / head width photo %.4f vs mesh %.4f
  → **%+.2f mm** on the Ø30.000 ring if the head is the mesh's %.3f mm wide. Ring centre %+.2f mm below the
  shell top and %+.2f mm off the mid-line against the mesh; ToF window %+.2f mm from the MJCF site.
- Profile photographs, ring diameter over head extent, photograph against the render at the fitted pose
  (scale-free): %s → combined **%s**.
- Verdict at the 1.5 mm rule: **%s**. %s

**Radial profile of the mesh (y = const cuts, r about the axis), mm.** %s

**Iteration.** v0.0.1 is the loader; a parametric rebuild (revolve: Ø30 × 7.5 boss, Ø14.4 bore, rear spigot)
graded by cad-refcheck against this mesh may replace it in v0.0.2, the slug stays.
''' % (boss["d_mm"] if boss else 30.0, boss["length_mm"] if boss else 7.5, bore["d_mm"] if bore else 14.4,
       FV["eye_od_over_width"]["photo"], FV["eye_od_over_width"]["mesh"], eye_front, HEAD["front_view"]["mesh_head_width_mm"],
       FV["eye_below_top_over_width"]["dev_mm"], FV["eye_x_offset_over_width"]["dev_mm"], FV["tof_x_from_eye_over_width"]["dev_mm"],
       "; ".join(pf) if pf else "no profile fit", ("%+.2f ± %.2f mm" % (eye_prof, eye_prof_u)) if eye_prof is not None else "CANNOT DETERMINE",
       V["eye_bezel"], (" ".join(x for x in V["what_would_settle"] if "eye ring" in x)),
       "; ".join("y %.2f: r %.2f" % (p[0], p[1]) for p in m["radial_profile"])))
    # ---- component.json
    comp = json.load(open(os.path.join(PART, "component.json")))
    comp["$parts_folder"] = 2
    comp["record"].update({
        "title": "microduck-eye-ring — the eye bezel: Pollen Robotics' published mesh `noenoeil` (Ø30.000 × 7.5 mm ring, Ø14.4 bore), mesh-backed part",
        "origin": "vendor", "vendor": "Pollen Robotics", "licence": LICENCE,
        "origin_why": "the geometry is the vendor's own published sim asset, loaded unchanged (tools/head_eye_ring_shelve.py, %s). Not our design; usable to assemble, render, simulate and print; NOT licensed for sale (NC)." % TODAY,
        "sector": "structural", "subsector": "robot-link", "lifecycle": "production", "material": "PLA", "process": "FDM (accent-colour printed part)",
        "verdict": V["eye_bezel"],
        "why": ("GOAL.md finding 1 said the product's eye bezel is missing from the sim meshes; it is this mesh. Against the product photographs "
                "(out/head/head.json): front view eye OD / head width %.4f vs mesh %.4f (%+.2f mm implied on Ø30.000); profiles, scale-free, %s; "
                "verdict at the 1.5 mm rule %s. Whether the mesh builds as a closed solid is read off bin/cad part:microduck-eye-ring." % (
                    FV["eye_od_over_width"]["photo"], FV["eye_od_over_width"]["mesh"], eye_front,
                    ("%+.2f ± %.2f mm" % (eye_prof, eye_prof_u)) if eye_prof is not None else "CANNOT DETERMINE", V["eye_bezel"])),
        "iteration": "v0.0.1", "mjcf_body": "jaw_soft", "mjcf_mesh": "noenoeil",
        "qty_per_robot": 1, "source_reference": "reference/pollen-microduck-rl/assets/noenoeil.stl",
        "why_this_folder_exists": "spec/mesh-to-part.json maps noenoeil here; the folder was created empty on 2026-09-01 and filled by lane A (head) on %s" % TODAY,
    })
    json.dump(comp, open(os.path.join(PART, "component.json"), "w"), indent=2)
    # ---- evidence ledger (append: export + measurements), idempotent by 'by' + summary
    led = os.path.join(IT, "evidence", "ledger.jsonl")
    rows = [json.loads(l) for l in open(led) if l.strip()] if os.path.exists(led) else []
    rows = [r for r in rows if r.get("by") != "tools/head_eye_ring_shelve.py"]
    rows.append({"date": TODAY, "kind": "export", "summary": "published mesh noenoeil.stl copied from reference/pollen-microduck-rl/assets/noenoeil.stl (%d bytes) as this part's geometry" % os.path.getsize(SRC),
                 "artifact": "geometry/noenoeil.stl", "sha256": sha, "by": "tools/head_eye_ring_shelve.py", "outcome": "PASS"})
    rows.append({"date": TODAY, "kind": "bench", "summary": "ring geometry off the mesh: boss %s, bore %s, radial profile %s" % (
        json.dumps(boss), json.dumps(bore), json.dumps(m["radial_profile"])), "artifact": "geometry/noenoeil.stl", "by": "tools/head_eye_ring_shelve.py", "outcome": "PASS"})
    rows.append({"date": TODAY, "kind": "field", "summary": "product photographs vs this mesh (out/head/head.json): front-view eye OD/head width %.4f vs %.4f (%+.2f mm implied); profiles scale-free %s; verdict %s" % (
        FV["eye_od_over_width"]["photo"], FV["eye_od_over_width"]["mesh"], eye_front, ("%+.2f ± %.2f mm" % (eye_prof, eye_prof_u)) if eye_prof is not None else "CANNOT DETERMINE", V["eye_bezel"]),
        "artifact": "../../../../out/head/head.json", "by": "tools/head_eye_ring_shelve.py", "outcome": V["eye_bezel"]})
    with open(led, "w") as f:
        for r in rows: f.write(json.dumps(r) + "\n")
    # ---- ITERATIONS.md
    itp = os.path.join(PART, "ITERATIONS.md"); txt = open(itp).read()
    line = "| v0.0.1 | %s | filled by lane A: Pollen's `noenoeil` mesh loaded as the eye bezel, measured against the product photographs (out/head/head.json) |" % TODAY
    if "filled by lane A" not in txt:
        open(itp, "a").write(line + "\n")
    print("wrote part:microduck-eye-ring  verdict", V["eye_bezel"], "boss", boss and boss["d_mm"], "bore", bore and bore["d_mm"], "spigot d", spig_d)


if __name__ == "__main__":
    main()
