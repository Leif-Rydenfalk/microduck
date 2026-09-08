#!/usr/bin/env python3
"""head_width.py — ATTRIBUTE the front-view ring/width excess: is the product's
head NARROWER than Pollen's mesh, or is its eye ring LARGER?

out/head/head.json (lane A, 2026-09-03) grades the head FAIL on one measurement:
in the one true front view (images/store/store_microduck-inside-the-box.png) the
ring OD / head width reads 0.3521 +- 0.0080 against 0.3226 on the mesh (+9.1 %).
A ratio does not say WHICH of the two is wrong: it is satisfied by a head 8.4 %
narrower (91.763 -> 84.098 mm) with the mesh's 30.000 mm ring, and equally by a
32.306 mm ring on a mesh-width head. head.json records that as
front_pair.attribution = CANNOT DETERMINE.

This tool settles it by MEASUREMENT rather than by argument, on the two
photographs the head measurement already admits (the profiles, where the head is
yawed 50-64 deg so its WIDTH is most of the silhouette's short axis and the eye
ring is seen whole):

  * the head is rebuilt at a sweep of LATERAL scales s_w (top/bottom head shell,
    face panel, jaw, jaw soft pad, soft mouth top scaled about the head's own
    mid-plane, body y; the eye ring, lens and lens holder left at mesh size), and
  * at a sweep of RING scales s_r (noenoeil only, scaled uniformly; the shells
    left at mesh size),

and at each scale the FULL photomatch fit is re-run (camera elevation/azimuth,
head pitch/yaw/roll, jaw opening, and the similarity k, tx, ty), so the pose is
free to absorb what it can. The fit objective is (1 - silhouette IoU) + 10 * the
eye-ring ellipse term; the ring's ellipse pins the yaw independently of the
silhouette, which is what breaks the width/yaw degeneracy.

The profile of the objective against s (a profile likelihood) has its minimum at
the scale the photograph actually shows. Read against the front view's own
prediction:
    s_w = 0.3226/0.3521 = 0.9163  (the head-width hypothesis)
    s_r = 0.3521/0.3226 = 1.0914  (the ring hypothesis)
one of the two is confirmed by photographs that never entered the front-view
measurement, or both are excluded and the front-view read is the thing at fault.

Writes out/head/width_attribution.json and, per photograph, the picture strip
out/head/width_<id>.png (the real photograph beside our render at s = 1 and at
the fitted s, with the fitted silhouette drawn on the photograph).

    /Applications/FreeCAD.app/Contents/Resources/bin/python tools/head_width.py [--quick] [--only ID] [--sweep w|r|both]
"""
import os, sys, json, math, time, argparse, copy
os.environ.setdefault("MUJOCO_GL", "glfw")
import numpy as np
import mujoco
from PIL import Image, ImageDraw
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import head_photomatch as hp

REPO, OUT = hp.REPO, hp.OUT

# the geoms that carry the head's WIDTH (everything but the optics on the eye axis)
SHELL_MESHES = ["top_head_shell", "bottom_head_shell", "face_part", "jaw", "jaw_soft", "soft_mouth_top"]
RING_MESHES = ["noenoeil"]
FRONT_RATIO_PHOTO = 0.35205707462343566   # out/head/front_view.json photo.ratios.eye_od_over_width
FRONT_RATIO_MESH = 0.3226489826660788     # out/head/front_view.json mesh.ratios.eye_od_over_width
S_W_SWEEP = [0.90, 0.94, 0.97, 1.00, 1.04]
S_R_SWEEP = [0.96, 1.00, 1.04, 1.08, 1.12]


def body_lateral_axis(model, data, head_bid):
    """the head body's own lateral (width) axis, as a unit vector in the body frame,
    and its world direction — MEASURED, not assumed: the head is symmetric about world
    y at the reference pose (head_yaw = head_roll = 0), so body y is the width axis."""
    Rb = data.xmat[head_bid].reshape(3, 3)
    ey_world = np.array([0.0, 1.0, 0.0])
    e_body = Rb.T @ ey_world
    return e_body, Rb


def build(s_shell=1.0, s_ring=1.0, size=1000):
    """a HeadRenderer whose head shells are scaled by s_shell and whose eye ring is
    scaled by s_ring, about the head's own mid-plane. The mesh vertices are edited
    BEFORE the renderer is constructed, because mujoco.Renderer uploads the mesh data
    to its GL context once, at construction."""
    model, data = hp.load_model()
    head_bid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "jaw_soft")
    e_body, Rb = body_lateral_axis(model, data, head_bid)
    report = dict(lateral_axis_body=[float(x) for x in e_body],
                  lateral_axis_is_body_y_to_deg=float(math.degrees(math.acos(min(1.0, abs(float(e_body[1])))))))
    gid = {}
    for g in range(model.ngeom):
        if model.geom_bodyid[g] != head_bid: continue
        mid = model.geom_dataid[g]
        if mid < 0: continue
        gid.setdefault(mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_MESH, mid), []).append(g)

    def apply(names, s, uniform=False):
        if abs(s - 1.0) < 1e-12: return
        for nm in names:
            for g in gid.get(nm, []):
                mid = model.geom_dataid[g]
                a, n = model.mesh_vertadr[mid], model.mesh_vertnum[mid]
                v = model.mesh_vert[a:a + n]
                if uniform:
                    model.mesh_vert[a:a + n] = v * s
                    model.geom_pos[g] = model.geom_pos[g] * 1.0     # a uniform ring scale about its own centre
                else:
                    Rg = data.geom_xmat[g].reshape(3, 3)             # mesh -> world at the reference pose
                    Rmb = Rb.T @ Rg                                  # mesh -> body
                    S = np.diag([1.0, s, 1.0])                       # scale body y
                    M = Rmb.T @ S @ Rmb
                    model.mesh_vert[a:a + n] = (M @ v.T).T
                    p = model.geom_pos[g].copy(); p[1] *= s; model.geom_pos[g] = p
    apply(SHELL_MESHES, s_shell, uniform=False)
    apply(RING_MESHES, s_ring, uniform=True)
    hr = hp.HeadRenderer(model, data, size=size)
    return hr, report


def measured_width_mm(hr):
    """the scaled head's actual width, MEASURED off the vertices in world y (mm)."""
    V = np.vstack([hr.geom_world_vertices(g) for nm in SHELL_MESHES for g in hr.gid.get(nm, [])]) * 1000.0
    return float(V[:, 1].max() - V[:, 1].min())


def measured_ring_od_mm(hr):
    V = np.vstack([hr.geom_world_vertices(g) for g in hr.gid.get("noenoeil", [])]) * 1000.0
    return float(max(V[:, 1].max() - V[:, 1].min(), V[:, 2].max() - V[:, 2].min()))


def fit_local(ph, hr, rgb, eye, x0, w_eye=10.0, restarts=4, maxfev=300, seed=0):
    """A LOCAL fit in a tight box around a known pose — the same objective as
    hp.fit_photo ((1 - silhouette IoU) + 10 x the eye-ellipse term) and the same
    renderer, but no global search.

    Why: with a global differential-evolution search the run-to-run basin noise
    measured 0.05 in the objective (out/head/width_quick.log: graphite s_w 0.96
    returned 0.1019 between 0.0511 at 0.92 and 0.0598 at 1.00 — a basin failure,
    not a scale effect), which is the size of the whole signal. The pose at a
    neighbouring lateral scale is near the pose at s = 1, so a local fit seeded
    from the published solution answers the same question with a noise this tool
    MEASURES and reports (the spread of the restarts that reached the minimum).
    """
    from scipy import optimize
    pm_full = hp.head_region_mask(rgb, ph)
    ys, xs = np.nonzero(pm_full)
    pad = 40
    bx0, by0, bx1, by1 = max(0, xs.min() - pad), max(0, ys.min() - pad), xs.max() + pad, ys.max() + pad
    ds = 2
    crop = pm_full[by0:by1, bx0:bx1]
    small = crop[::ds, ::ds]
    HS, WS = small.shape
    area_p = small.sum(); cy_p, cx_p = np.nonzero(small)[0].mean(), np.nonzero(small)[1].mean()
    L_p = max(crop.shape)
    ec = np.array(eye["centre"]) - np.array([bx0, by0]); e_maj, e_min = eye["major_px"], eye["minor_px"]
    D_mm = ph["D_mm"]; neck = ph.get("neck_pitch_deg", 0.0)

    def render(p):
        el, az, pitch, yaw, roll, jaw = p
        hr.pose(pitch, yaw, roll, jaw if ph["jaw_open"] else 0.0, neck_pitch_deg=neck)
        hr.set_camera(az, el, D_mm)
        head, eyem, ids, isg = hr.masks()
        return head, eyem

    def eye_term(eyem, k, tx, ty):
        ys_, xs_ = np.nonzero(eyem)
        if len(xs_) < 40: return 1.0
        e = hp.ellipse_of(np.stack([xs_, ys_], 1).astype(float))
        kf = k * ds; c = kf * np.array(e["centre"]) + np.array([tx * ds, ty * ds])
        return (((c - ec) ** 2).sum() + (kf * e["major_px"] - e_maj) ** 2 + (kf * e["minor_px"] - e_min) ** 2) / L_p ** 2

    # a starting k from the areas, then the published pose
    mr0, _ = render((x0["el"], x0["az"], x0["pitch"], x0["yaw"], x0["roll"], x0.get("jaw", 0.0)))
    ry, rx = np.nonzero(mr0)
    k0 = math.sqrt(area_p / max(1, mr0.sum()))
    tx0 = cx_p - k0 * rx.mean(); ty0 = cy_p - k0 * ry.mean()
    p0 = np.array([x0["el"], x0["az"], x0["pitch"], x0["yaw"], x0["roll"], x0.get("jaw", 0.0) if ph["jaw_open"] else 0.0, k0, tx0, ty0])
    span = np.array([6.0, 0.02 if not ph["az_free"] else 8.0, 8.0, 8.0, 10.0, 8.0 if ph["jaw_open"] else 0.005, 0.12 * k0, 40.0, 40.0])
    lo_b, hi_b = p0 - span, p0 + span

    def eval_params(p, return_all=False):
        p = np.clip(p, lo_b, hi_b)
        el, az, pitch, yaw, roll, jaw, k, tx, ty = p
        mr, eyem = render((el, az, pitch, yaw, roll, jaw))
        tm = hp.transform_mask(mr, k, tx, ty, (WS, HS))
        v = hp.iou(small, tm)
        et = eye_term(eyem, k, tx, ty)
        if return_all: return v, et, mr, eyem, tm
        return (1.0 - v) + w_eye * et
    t0 = time.time(); rng = np.random.default_rng(seed); nfev = 0
    runs = []
    for i in range(restarts + 1):
        st = p0.copy()
        if i:
            st = st + rng.normal(0, 1, 9) * np.array([2.0, 0.0 if not ph["az_free"] else 2.0, 3.0, 3.0, 4.0, 2.0 if ph["jaw_open"] else 0.0, 0.03 * k0, 12.0, 12.0])
        st = np.clip(st, lo_b, hi_b)
        r = optimize.minimize(eval_params, st, method="Nelder-Mead", options=dict(xatol=0.01, fatol=1e-7, maxfev=maxfev))
        nfev += int(r.nfev)
        runs.append((float(r.fun), np.clip(r.x, lo_b, hi_b)))
    runs.sort(key=lambda t: t[0])
    best_f, p = runs[0]
    good = [f for f, _ in runs if f <= best_f + 0.01]
    noise = float(np.std([f for f, _ in runs])) if len(runs) > 1 else 0.0
    best_iou, et, mr, eyem, tm = eval_params(p, True)
    el, az, pitch, yaw, roll, jaw, k, tx, ty = [float(x) for x in p]
    names = ["cam_el", "cam_az", "head_pitch", "head_yaw", "head_roll", "jaw", "k", "tx", "ty"]
    fixed = {"cam_az"} if not ph["az_free"] else set()
    if not ph["jaw_open"]: fixed.add("jaw")
    at_bound = [dict(param=nm, value=float(v), bounds=[float(a), float(b)])
                for nm, v, a, b in zip(names, p, lo_b, hi_b)
                if nm not in fixed and min(abs(v - a), abs(b - v)) <= 0.005 * (b - a)]
    fit = dict(objective=float(best_f), iou=float(best_iou), eye_term=float(et), seconds=round(time.time() - t0, 1),
               n_eval=nfev, restarts_reaching_min=len(good), objective_spread=noise,
               all_restart_objectives=[round(f, 6) for f, _ in runs],
               cam_el_deg=el, cam_az_deg=az, cam_distance_mm=D_mm, head_pitch_deg=pitch, head_yaw_deg=yaw,
               head_roll_deg=roll, jaw_open_deg=jaw if ph["jaw_open"] else 0.0,
               k_photo_px_per_render_px=k * ds, tx=tx * ds + bx0, ty=ty * ds + by0,
               at_bound=at_bound, crop_box=[int(bx0), int(by0), int(bx1), int(by1)],
               local_box=dict(zip(names, [[float(a), float(b)] for a, b in zip(lo_b, hi_b)])))
    fit["_masks"] = (pm_full, mr, tm, crop, small, eyem)
    return fit


def run_one(ph, hr, rgb, eye, quick, tight_x0=None):
    if tight_x0 is not None:
        fit = fit_local(ph, hr, rgb, eye, tight_x0)
    else:
        fit = hp.fit_photo(ph, hr, rgb, eye, quick=quick)
    masks = fit.pop("_masks")
    return fit, masks


def strip(rgb, ph, results, path, title):
    """the real photograph beside our render at s = 1 and at the best s, with the fitted
    silhouette outline drawn on the photograph (Leif's rule: every render of ours sits
    beside the real one)."""
    th = 620
    panels = []
    for lab, r in results:
        im = Image.fromarray(r["shaded"]).convert("RGB")
        m = r["mask_render"]
        ys, xs = np.nonzero(m)
        pad = 30
        im = im.crop((max(0, xs.min() - pad), max(0, ys.min() - pad), xs.max() + pad, ys.max() + pad))
        panels.append((lab, im))
    real = Image.fromarray(rgb.astype(np.uint8)).convert("RGB")
    d = ImageDraw.Draw(real)
    for (lab, r), col in zip(results, [(210, 60, 40), (30, 110, 220)]):
        tm = r["mask_in_photo"]
        ed = tm ^ ndimage.binary_erosion(tm, iterations=2)
        yy, xx = np.nonzero(ed)
        for x, y in zip(xx[::3], yy[::3]):
            d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=col)
    bx0, by0, bx1, by1 = results[0][1]["crop_box"]
    pad = 60
    realc = real.crop((max(0, bx0 - pad), max(0, by0 - pad), bx1 + pad, by1 + pad))
    ims = [("REAL  " + ph["title"] + "   red = ours at s=1.000, blue = ours at the fitted s", realc)] + panels
    scaled = [(lab, im.resize((int(im.size[0] * th / im.size[1]), th), Image.LANCZOS)) for lab, im in ims]
    W = sum(im.size[0] for _, im in scaled) + 10 * (len(scaled) + 1)
    sheet = Image.new("RGB", (W, th + 60), (255, 255, 255)); dd = ImageDraw.Draw(sheet)
    x = 10
    for lab, im in scaled:
        sheet.paste(im, (x, 48))
        dd.text((x + 2, 26), lab[:120], fill=(0, 0, 0))
        x += im.size[0] + 10
    dd.text((10, 8), title[:260], fill=(0, 0, 0))
    sheet.save(path)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--only", default=None)
    ap.add_argument("--sweep", default="both", choices=["w", "r", "both"])
    ap.add_argument("--tight", action="store_true",
                    help="local fits seeded from the published pose in out/head/head.json (low optimiser noise, MEASURED and reported)")
    ap.add_argument("--out", default="width_attribution.json")
    a = ap.parse_args()
    published = {}
    hj = os.path.join(OUT, "head.json")
    if os.path.exists(hj):
        for ph in json.load(open(hj)).get("photos", []):
            f = ph.get("fit") or {}
            if "head_yaw_deg" in f:
                published[ph["id"]] = dict(el=f["cam_el_deg"], az=f["cam_az_deg"], pitch=f["head_pitch_deg"],
                                           yaw=f["head_yaw_deg"], roll=f["head_roll_deg"], jaw=f.get("jaw_open_deg", 0.0))
    photos = [p for p in hp.PHOTOS if p["id"] in ("cream-profile-left", "graphite-profile-right")]
    if a.only: photos = [p for p in photos if p["id"] == a.only]
    out = dict(generated=time.strftime("%Y-%m-%d %H:%M"), method=__doc__, quick=bool(a.quick),
               front_ratio_photo=FRONT_RATIO_PHOTO, front_ratio_mesh=FRONT_RATIO_MESH,
               s_w_predicted=FRONT_RATIO_MESH / FRONT_RATIO_PHOTO, s_r_predicted=FRONT_RATIO_PHOTO / FRONT_RATIO_MESH,
               photos=[])
    for ph in photos:
        rgb = hp.load_rgb(os.path.join(REPO, ph["path"]))
        eye = hp.measure_eye(rgb, ph["eye_box"], ph["eye_hue"], smin=ph.get("eye_smin", 0.35))
        rec = dict(id=ph["id"], title=ph["title"], path=ph["path"], sweeps={})
        for which, sweep in (("s_w", S_W_SWEEP), ("s_r", S_R_SWEEP)):
            if a.sweep == "w" and which != "s_w": continue
            if a.sweep == "r" and which != "s_r": continue
            rows = []
            keep = {}
            for s in sweep:
                t0 = time.time()
                hr, rep = build(s_shell=s if which == "s_w" else 1.0, s_ring=s if which == "s_r" else 1.0)
                w_mm = measured_width_mm(hr); r_mm = measured_ring_od_mm(hr)
                fit, masks = run_one(ph, hr, rgb, eye, a.quick,
                                     tight_x0=published.get(ph["id"]) if a.tight else None)
                pm_full, mr, tm, crop, small, eyem = masks
                row = dict(s=s, objective=fit["objective"], iou=fit["iou"], eye_term=fit["eye_term"],
                           head_width_mm=w_mm, ring_od_mm=r_mm,
                           head_pitch_deg=fit["head_pitch_deg"], head_yaw_deg=fit["head_yaw_deg"],
                           head_roll_deg=fit["head_roll_deg"], cam_el_deg=fit["cam_el_deg"], cam_az_deg=fit["cam_az_deg"],
                           jaw_open_deg=fit["jaw_open_deg"], k=fit["k_photo_px_per_render_px"],
                           at_bound=fit["at_bound"], seconds=round(time.time() - t0, 1), n_eval=fit["n_eval"],
                           objective_spread=fit.get("objective_spread"),
                           restart_objectives=fit.get("all_restart_objectives"))
                rows.append(row)
                print("[%s %s] s=%.4f  obj=%.5f iou=%.4f eye=%.5f  width=%.3f ring=%.3f  spread=%s  (%.0f s)" % (
                    ph["id"], which, s, row["objective"], row["iou"], row["eye_term"], w_mm, r_mm,
                    ("%.5f" % row["objective_spread"]) if row["objective_spread"] is not None else "-", row["seconds"]), flush=True)
                if abs(s - 1.0) < 1e-9 or True:
                    # keep the masks for the s=1 panel and (later) the best panel
                    hrsh = hr.shaded()
                    keep[s] = dict(shaded=hrsh, mask_render=mr, mask_in_photo=np.zeros(pm_full.shape, bool), crop_box=fit["crop_box"])
                    bx0, by0, bx1, by1 = fit["crop_box"]
                    full = np.zeros(pm_full.shape, bool)
                    up = np.kron(tm, np.ones((2, 2), bool))
                    hgt = min(up.shape[0], full.shape[0] - by0); wid = min(up.shape[1], full.shape[1] - bx0)
                    full[by0:by0 + hgt, bx0:bx0 + wid] = up[:hgt, :wid]
                    keep[s]["mask_in_photo"] = full
                del hr
            best = min(rows, key=lambda r: r["objective"])
            # a parabola through the three points around the minimum -> the sub-grid minimiser
            xs = [r["s"] for r in rows]; ys = [r["objective"] for r in rows]
            i = xs.index(best["s"])
            sub = None
            if 0 < i < len(xs) - 1:
                x0, x1, x2 = xs[i - 1], xs[i], xs[i + 1]; y0, y1, y2 = ys[i - 1], ys[i], ys[i + 1]
                den = (x0 - x1) * (x0 - x2) * (x1 - x2)
                if abs(den) > 1e-12:
                    A = (x2 * (y1 - y0) + x1 * (y0 - y2) + x0 * (y2 - y1)) / den
                    B = (x2 * x2 * (y0 - y1) + x1 * x1 * (y2 - y0) + x0 * x0 * (y1 - y2)) / den
                    if A > 0: sub = float(-B / (2 * A))
            rec["sweeps"][which] = dict(rows=rows, best_s=best["s"], best_objective=best["objective"],
                                        parabola_min_s=sub,
                                        predicted_s=out["s_w_predicted"] if which == "s_w" else out["s_r_predicted"])
            # picture: s = 1 beside the best s
            try:
                res = [("OURS  s = 1.000 (Pollen's mesh)  width %.3f mm, ring %.3f mm" % (
                            [r for r in rows if abs(r["s"] - 1.0) < 1e-9][0]["head_width_mm"],
                            [r for r in rows if abs(r["s"] - 1.0) < 1e-9][0]["ring_od_mm"]), keep[1.00]),
                       ("OURS  %s = %.4f  width %.3f mm, ring %.3f mm" % (which, best["s"], best["head_width_mm"], best["ring_od_mm"]), keep[best["s"]])]
                p = strip(rgb, ph, res, os.path.join(OUT, "width_%s_%s%s.png" % (ph["id"], which, "_tight" if a.tight else "")),
                          "%s — objective vs %s: %s" % (ph["title"], which,
                          "  ".join("%.4f:%.5f" % (r["s"], r["objective"]) for r in rows)))
                rec["sweeps"][which]["picture"] = os.path.relpath(p, REPO)
            except Exception as e:
                rec["sweeps"][which]["picture_error"] = repr(e)
        out["photos"].append(rec)
        json.dump(out, open(os.path.join(OUT, a.out), "w"), indent=1, default=float)
    out["tight"] = bool(a.tight)
    json.dump(out, open(os.path.join(OUT, a.out), "w"), indent=1, default=float)
    print("wrote", os.path.join(OUT, a.out))


if __name__ == "__main__":
    main()
