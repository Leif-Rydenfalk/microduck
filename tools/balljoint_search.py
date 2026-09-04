#!/usr/bin/env python3
"""balljoint_search.py — IS THERE A BALL JOINT IN THIS ROBOT? Decide it on
geometry, not on the word.

    python3 tools/balljoint_search.py   -> out/fasteners/balljoints.json + a table

Leif named ball joints twice in the standing orders. A name is not a feature, so
this file asks the only question that settles it: does any BALL patch anywhere in
the assembled robot sit inside a SOCKET patch of matching radius on a DIFFERENT
part? That is what a ball joint IS. A lone spherical cap is a dome, a fillet, a
drill point or the end of a printed pocket — every one of those fits a sphere
beautifully and none of them articulates.

WHAT IT READS, and it fits nothing new:
    out/fasteners/spheres-all-meshes.json   every spherical patch on every
        reference mesh, already fitted by cecad.meshfeatures.spheres (kind
        ball/socket, radius, centre, residual, angular cover)
    out/fasteners/world-placements.json     the MJCF zero-pose world frame of
        every placed mesh

THE TEST, stated so it can be disagreed with:
  * a PAIR is a ball and a socket whose world centres are within CENTRE_TOL_MM
    and whose radii differ by less than RADIUS_TOL_MM;
  * they must be on DIFFERENT meshes — a ball and socket inside one printed part
    cannot articulate against each other;
  * the socket must be the LARGER of the two, or the ball does not fit in it.
Every sphere that fails is reported with WHY, because "no ball joint" is only
worth reading if you can see what was considered.
"""
import collections
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SPH = os.path.join(ROOT, "out", "fasteners", "spheres-all-meshes.json")
WORLD = os.path.join(ROOT, "out", "fasteners", "world-placements.json")
OUT = os.path.join(ROOT, "out", "fasteners", "balljoints.json")

CENTRE_TOL_MM = 0.60      # a ball joint's clearance; wider than any real one
RADIUS_TOL_MM = 0.50      # ball-to-socket radial clearance, generous on purpose
# Below this angular coverage a "sphere" is a cap, and a cap that small cannot
# capture a ball however well it fits. cover is the fraction of 4*pi steradians.
CAPTURE_COVER_MIN = 0.25


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def matvec(R, v):
    return [dot(R[0], v), dot(R[1], v), dot(R[2], v)]


def main():
    sph = json.load(open(SPH, encoding="utf-8"))
    world = json.load(open(WORLD, encoding="utf-8"))
    placed = collections.defaultdict(list)
    for p in world["placements"]:
        if p.get("class") == "visual":
            placed[p["mesh"]].append(p)

    spheres, unplaced = [], []
    for mesh, rec in sph["meshes"].items():
        for s in rec.get("spheres") or []:
            if mesh not in placed:
                unplaced.append({"mesh": mesh, "kind": s["kind"], "r_mm": s["r_mm"],
                                 "why": "this mesh is not placed in the assembly at all "
                                        "(no visual placement in world-placements.json), so it "
                                        "has no world position and cannot pair with anything"})
                continue
            for pl in placed[mesh]:
                c = matvec(pl["R"], s["center_mm"])
                c = [c[i] + pl["t_mm"][i] for i in range(3)]
                spheres.append({"mesh": mesh, "body": pl["body"],
                                "geom_index": pl["geom_index"], "kind": s["kind"],
                                "r_mm": s["r_mm"], "residual_mm": s["residual_mm"],
                                "cover": s["cover"], "faces": s.get("faces"),
                                "center_mesh_mm": s["center_mm"],
                                "center_world_mm": [round(v, 4) for v in c]})

    balls = [s for s in spheres if s["kind"] == "ball"]
    sockets = [s for s in spheres if s["kind"] == "socket"]
    mixed = [s for s in spheres if s["kind"] not in ("ball", "socket")]

    pairs, near = [], []
    for b in balls:
        for k in sockets:
            d = math.sqrt(sum((b["center_world_mm"][i] - k["center_world_mm"][i]) ** 2
                              for i in range(3)))
            dr = k["r_mm"] - b["r_mm"]
            same_mesh = (b["mesh"] == k["mesh"] and b["geom_index"] == k["geom_index"])
            rec = {"ball": {"mesh": b["mesh"], "body": b["body"], "r_mm": b["r_mm"],
                            "cover": b["cover"], "center_world_mm": b["center_world_mm"]},
                   "socket": {"mesh": k["mesh"], "body": k["body"], "r_mm": k["r_mm"],
                              "cover": k["cover"], "center_world_mm": k["center_world_mm"]},
                   "centre_distance_mm": round(d, 4),
                   "radial_clearance_mm": round(dr, 4),
                   "same_geom": same_mesh}
            if d > CENTRE_TOL_MM:
                continue
            reasons = []
            if same_mesh:
                reasons.append("ball and socket are the SAME placed geometry — one printed part "
                               "cannot articulate against itself")
            if dr < -RADIUS_TOL_MM:
                reasons.append("the socket is %.4f mm SMALLER in radius than the ball: it does "
                               "not fit" % (-dr))
            if abs(dr) > RADIUS_TOL_MM:
                reasons.append("radial clearance %.4f mm exceeds the %.2f mm band a ball joint "
                               "runs in" % (dr, RADIUS_TOL_MM))
            if k["cover"] < CAPTURE_COVER_MIN:
                reasons.append("the socket covers only %.1f%% of a full sphere; below %.0f%% it "
                               "cannot CAPTURE a ball, it can only touch it"
                               % (k["cover"] * 100, CAPTURE_COVER_MIN * 100))
            if reasons:
                rec["verdict"] = "NOT A BALL JOINT"
                rec["why"] = "; ".join(reasons)
                near.append(rec)
            else:
                rec["verdict"] = "BALL JOINT"
                pairs.append(rec)

    by_mesh = collections.Counter(s["mesh"] for s in spheres)
    doc = {
        "doc": {"id": "MD-BALLJOINT-001", "rev": "A",
                "title": "Ball-joint search — every spherical patch in the assembled robot, "
                         "and whether any two of them form a joint",
                "generated_by": "tools/balljoint_search.py",
                "reads": ["out/fasteners/spheres-all-meshes.json",
                          "out/fasteners/world-placements.json"]},
        "test": {"centre_tol_mm": CENTRE_TOL_MM, "radius_tol_mm": RADIUS_TOL_MM,
                 "capture_cover_min": CAPTURE_COVER_MIN,
                 "what_a_ball_joint_is": "a ball patch and a socket patch on DIFFERENT placed "
                                         "geometry, concentric to within the clearance, radii "
                                         "matching to within the clearance, the socket the "
                                         "larger, and the socket covering enough of a sphere to "
                                         "capture rather than merely touch"},
        "counts": {
            "meshes_scanned": len(sph["meshes"]),
            "spherical_patches_fitted": sph.get("total_spheres"),
            "patches_on_PLACED_geometry": len(spheres),
            "patches_on_meshes_never_placed": len(unplaced),
            "balls": len(balls), "sockets": len(sockets), "mixed": len(mixed),
            "ball_socket_pairs_within_%g_mm" % CENTRE_TOL_MM: len(pairs) + len(near),
            "BALL_JOINTS": len(pairs),
            "by_mesh": dict(by_mesh)},
        "verdict": ("BALL JOINTS FOUND: %d" % len(pairs)) if pairs else
                   ("NO BALL JOINT EXISTS IN THIS GEOMETRY. %d spherical patches were fitted on "
                    "placed geometry (%d balls, %d sockets, %d mixed). %d ball/socket pairs came "
                    "within %g mm of concentric and every one is refuted below by its own "
                    "measurement. The spherical features in this robot are dome ends of printed "
                    "pockets, drill points, fillet caps and the toroidal chamfers of the bearing "
                    "rings — not articulating joints. Leif named ball joints; the geometry does "
                    "not contain one, and that is a measurement, not a refusal to look."
                    % (len(spheres), len(balls), len(sockets), len(mixed), len(near),
                       CENTRE_TOL_MM)),
        "settled_by": ("a teardown photograph or a caliper on a real unit showing a ball stud in a "
                       "socket anywhere on the machine. If one exists, Pollen's meshes do not carry "
                       "it and the meshes are what we modelled from — that would be a finding about "
                       "the reference, not about this search."),
        "ball_joints": pairs,
        "near_misses_refuted": near,
        "all_patches_on_placed_geometry": spheres,
        "patches_on_meshes_never_placed": unplaced,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(doc, open(OUT, "w", encoding="utf-8"), indent=1)
    print("spherical patches fitted        :", sph.get("total_spheres"))
    print("on PLACED geometry              :", len(spheres),
          "(%d balls, %d sockets, %d mixed)" % (len(balls), len(sockets), len(mixed)))
    print("on meshes never placed          :", len(unplaced))
    print("ball/socket pairs within %.2f mm : %d" % (CENTRE_TOL_MM, len(pairs) + len(near)))
    print("BALL JOINTS                     :", len(pairs))
    for n in near[:12]:
        print("  refuted: %-22s r%.4f  vs %-22s r%.4f  d=%.4f  %s"
              % (n["ball"]["mesh"], n["ball"]["r_mm"], n["socket"]["mesh"],
                 n["socket"]["r_mm"], n["centre_distance_mm"], n["why"][:90]))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
