#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""leg_framing.py — PROVE the close-ups actually contain the servo and the bearing.

"with the servo and the bearing side both visible" is a claim about a camera, so
it is checked as one: for every close-up camera sim/leg_render.py uses, the world
position of every xl330 servo geom and every 22x16x4 bearing geom is projected
into that camera's frustum (free camera: pos = lookat - distance * forward,
vertical fov from model.vis.global_.fovy, aspect from the 400x500 panel) and the
ones inside are listed with their distance from the camera. Result goes into
out/motion/legs.json under "framing_check".

    /Applications/FreeCAD.app/Contents/Resources/bin/python sim/leg_framing.py
"""
import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("MUJOCO_GL", "glfw")
import numpy as np, mujoco
import common, leg_sweep as LS

ROOT, OUT = LS.ROOT, LS.OUT
PW, PH = 400, 500
SIDE = {"left": (270, 225), "right": (90, 45)}
JOINTS = LS.LEG_JOINTS


def cam_basis(az, el):
    a, e = math.radians(az), math.radians(el)
    fwd = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
    right = np.array([-math.sin(a), math.cos(a), 0.0])
    up = np.cross(right, fwd)
    return fwd, right, up


def main():
    m, d, _ = LS.build(tag="framing")
    kid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_KEY, "STAND")
    mujoco.mj_resetDataKeyframe(m, d, kid); mujoco.mj_forward(m, d)
    fovy = float(m.vis.global_.fovy)
    half_v = math.radians(fovy) / 2
    half_h = math.atan(math.tan(half_v) * PW / PH)
    want = []
    for i in range(m.ngeom):
        did = m.geom_dataid[i]
        mesh = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_MESH, did) if did >= 0 else ""
        if mesh and ("xl330" in mesh or "bearing" in mesh):
            want.append((i, mesh, mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, m.geom_bodyid[i])))
    res = dict(limitation="a frustum test, not an occlusion test: it proves the part lies inside the "
                          "camera cone and in the foreground (nearer than 1.5x the camera distance), "
                          "not that nothing is drawn in front of it. The rendered frames were also read "
                          "back by eye - see out/motion/frames/legs_*.png.",
               fovy_deg=fovy, panel_px=[PW, PH],
               half_fov_deg=[round(math.degrees(half_h), 3), round(math.degrees(half_v), 3)],
               pose="STAND keyframe",
               parts_looked_for=sorted({w[1] for w in want}), cameras={})
    for jn in JOINTS:
        paz, qaz = SIDE["left" if jn.startswith("left") else "right"]
        jid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, jn)
        look = np.array(d.xanchor[jid], float)
        for label, az, el, dist in (("profile", paz, -4, 0.20), ("three_quarter", qaz, -12, 0.22)):
            fwd, right, up = cam_basis(az, el)
            pos = look - dist * fwd
            inside = []
            for gi, mesh, body in want:
                v = np.array(d.geom_xpos[gi], float) - pos
                z = float(v @ fwd)
                if z <= 0:
                    continue
                ah = abs(math.atan2(float(v @ right), z)); av = abs(math.atan2(float(v @ up), z))
                if ah <= half_h and av <= half_v:
                    inside.append(dict(mesh=mesh, body=body, range_m=round(float(np.linalg.norm(v)), 4),
                                       off_axis_deg=[round(math.degrees(ah), 2), round(math.degrees(av), 2)]))
            inside.sort(key=lambda r: r["range_m"])
            fg = dist * 1.5          # foreground: nearer than 1.5x the camera distance
            servo = [r for r in inside if "xl330" in r["mesh"] and r["range_m"] <= fg]
            bear = [r for r in inside if "bearing" in r["mesh"] and r["range_m"] <= fg]
            res["cameras"]["%s/%s" % (jn, label)] = dict(
                azimuth=az, elevation=el, distance_m=dist,
                camera_pos_m=[round(float(x), 4) for x in pos],
                lookat_m=[round(float(x), 4) for x in look],
                foreground_cutoff_m=round(fg, 4),
                servos_in_foreground=len(servo), bearings_in_foreground=len(bear),
                nearest_servo=servo[0] if servo else None,
                nearest_bearing=bear[0] if bear else None,
                verdict=("PASS both" if servo and bear else
                         "PARTIAL servo only" if servo else
                         "PARTIAL bearing only" if bear else "FAIL neither in the foreground"),
                all_in_frustum=len(inside))
    n_both = sum(1 for v in res["cameras"].values() if v["verdict"] == "PASS both")
    n_none = sum(1 for v in res["cameras"].values() if v["verdict"].startswith("FAIL"))
    res["summary"] = dict(cameras=len(res["cameras"]), both=n_both, neither=n_none)
    p = os.path.join(OUT, "legs.json")
    j = json.load(open(p)); j["framing_check"] = res
    json.dump(j, open(p, "w"), indent=1)
    for k, v in res["cameras"].items():
        print("%-32s %-14s servo %-38s bearing %s" % (
            k, v["verdict"],
            ("%s @ %.3f m" % (v["nearest_servo"]["body"], v["nearest_servo"]["range_m"])) if v["nearest_servo"] else "-",
            ("%s @ %.3f m" % (v["nearest_bearing"]["body"], v["nearest_bearing"]["range_m"])) if v["nearest_bearing"] else "-"))
    print("%d cameras: %d with both a servo and a bearing in the foreground, %d with neither" %
          (len(res["cameras"]), n_both, n_none))


if __name__ == "__main__":
    main()
