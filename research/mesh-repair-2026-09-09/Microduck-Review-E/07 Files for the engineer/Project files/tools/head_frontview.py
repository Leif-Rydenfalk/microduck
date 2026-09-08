#!/usr/bin/env python3
"""head_frontview.py — the face layout, scale-free, from the one true FRONT view.

images/store/store_microduck-inside-the-box.png is a flat-lay: the robot lies on
its back and the camera looks straight at the face. The photo is a composite
(the battery in the same frame measures 268 px across = 70.8 mm and the gamepad
485 px = ~152 mm — two different mm/px, so it is NOT one scale), so nothing here
uses mm/px from another object. Instead every number is a RATIO inside the head
itself (one object, one depth), compared with the same ratio measured on our
mesh rendered in a true front view with the head LEVEL (eye-ring axis
horizontal: the head pitch found by bisection on the noenoeil geom axis, printed on the picture).

Measured on both sides with the same estimators:
  head width       widest row of the head silhouette (shell + beak), px
  eye ring OD      principal-axis extent of the accent-hue ring pixels, px
  eye centre       ring centroid; offset from the head's mid-column, and depth
                   below the shell's top edge, px
  ToF window       dark pill right of the eye (photo only; the mesh has no
                   separate ToF geom — its site is at y = +22.4 mm, PROPORTIONS.md)
Ratios: eyeOD/width, eye-below-top/width, eye-x-offset/width, tof-offset/width.
Converted to mm through the MESH head width (91.763 mm) so a reader sees the
implied product dimension if the head width is the mesh's.

Writes out/head/front_view.json and out/head/front_pair.png (real beside ours).
    /Applications/FreeCAD.app/Contents/Resources/bin/python tools/head_frontview.py
"""
import os, sys, json, math, time
os.environ.setdefault("MUJOCO_GL", "glfw")
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import head_photomatch as hp

REPO = hp.REPO; OUT = hp.OUT
PHOTO = "images/store/store_microduck-inside-the-box.png"
HEAD_REGION = (100, 180, 600, 500)     # x0,y0,x1,y1 in the photo: the head + beak (the beak ends at y ~482; the window used to end at 480
                                        # and the widest row sat on its edge — measured 2026-09-03, gridded crop)
SHELL_THRESHOLDS = [200, 210, 220, 228, 235, 240]   # min-channel thresholds swept for the shell silhouette width
BEAK_SMIN_SWEEP = [0.35, 0.40, 0.45, 0.50, 0.55]    # saturation thresholds swept for the beak band width
BEAK_SMIN = 0.45
RULE_MM = 1.5                          # docs/REBUILD-PROTOCOL.md: bbox within 1.5 mm per axis
D_BRACKET_MM = [400.0, 800.0, 1500.0, 1e9]   # flat-lay camera distance bracket (the photograph carries no EXIF and no ruler)
# (numerator feature depth key, width feature depth key) in mesh_side()['depths'] — the photograph's width is the beak band
FEATURE_DEPTH = {"eye_od_over_width": ("ring_front_face", "beak_width_edge"),      # the silhouette of a cylinder seen near end-on is its nearest rim
                 "eye_below_top_over_width": ("shell_top", "beak_width_edge"),        # the top row is the dome apex; its depth vs the beak edge
                 "eye_x_offset_over_width": (None, None),                            # an offset of ~0: magnification acts on the offset itself, nil
                 "tof_x_from_eye_over_width": ("face_front", "beak_width_edge"),
                 "first_beak_band_top_below_top_over_width": ("beak_width_edge", "beak_width_edge")}   # the band's visible top edge is its front lip, at the beak's depth
EYE_BOX = (250, 230, 440, 420)
TOF_BOX = (410, 290, 510, 370)
MESH_HEAD_W = 91.763                    # top_head_shell mesh y extent, mm (out/verify/mech_dims.json / head_probe)


def draw_ellipse(d, e, colour, w=3):
    cx, cy = e["centre"]; a = e["major_px"] / 2; b = e["minor_px"] / 2
    ang = math.atan2(e["major_axis_dir"][1], e["major_axis_dir"][0])
    pts = [(cx + a * math.cos(t) * math.cos(ang) - b * math.sin(t) * math.sin(ang),
            cy + a * math.cos(t) * math.sin(ang) + b * math.sin(t) * math.cos(ang)) for t in np.linspace(0, 2 * math.pi, 90)]
    d.line(pts + [pts[0]], fill=colour, width=w)


def widest_row(mask):
    ys, xs = np.nonzero(mask)
    rows = [(y, int(np.nonzero(mask[y])[0].min()), int(np.nonzero(mask[y])[0].max())) for y in range(ys.min(), ys.max() + 1) if mask[y].any()]
    w = max(rows, key=lambda r: r[2] - r[1])
    return w, rows


def photo_side():
    rgb = hp.load_rgb(os.path.join(REPO, PHOTO)); h, s, v = hp.hsv(rgb)
    x0, y0, x1, y1 = HEAD_REGION
    region = np.zeros(rgb.shape[:2], bool); region[y0:y1, x0:x1] = True
    mn = rgb.min(axis=2); mx = rgb.max(axis=2); chroma = mx - mn

    def head_of(sil):
        head = sil & region
        lab, n = ndimage.label(head); sizes = ndimage.sum(head, lab, range(1, n + 1)); head = lab == (1 + int(np.argmax(sizes)))
        return ndimage.binary_fill_holes(head)
    # (a) the shell silhouette, swept over the luminance threshold: the cream shell on a white ground with a soft shadow
    #     to its right has no single edge — the sweep IS the uncertainty of that read, and it is why (b) is the width used
    sweep = []
    for th in SHELL_THRESHOLDS:
        hd = head_of((mn < th) | (chroma > 14)); w, _ = widest_row(hd); yy, xx = np.nonzero(hd)
        sweep.append(dict(threshold=th, widest_row=int(w[0]), x=[w[1], w[2]], width_px=int(w[2] - w[1] + 1), mid_x=(w[1] + w[2]) / 2.0, top_row=int(yy.min())))
    head = head_of(hp.silhouette(rgb))          # the estimator every other picture uses (min channel < 228 or chroma > 14)
    ys, xs = np.nonzero(head); wrow, rows = widest_row(head)
    shell = dict(widest_row=int(wrow[0]), x=[wrow[1], wrow[2]], width_px=int(wrow[2] - wrow[1] + 1), mid_x=(wrow[1] + wrow[2]) / 2.0,
                 top_row=int(ys.min()), bottom_row=int(ys.max()),
                 widest_row_on_window_edge=bool(wrow[0] >= y1 - 2 or wrow[0] <= y0 + 1),
                 sweep=sweep, width_px_range=[min(x["width_px"] for x in sweep), max(x["width_px"] for x in sweep)],
                 mid_x_range=[min(x["mid_x"] for x in sweep), max(x["mid_x"] for x in sweep)])
    # (b) the beak band (jaw + bottom shell, orange, saturated): sharp accent edges on both sides, no shadow ambiguity.
    #     In the mesh the beak is as wide as the shell (bottom_head_shell 91.763, jaw 91.416, top_head_shell 91.760 mm —
    #     out/verify/mech_dims.json), so its width is the head width. Swept over the saturation threshold.
    bsweep = []
    for smin in BEAK_SMIN_SWEEP:
        orange = (h >= 15) & (h <= 50) & (s > smin) & (v > 0.3) & region
        orange = ndimage.binary_opening(orange, iterations=1)
        lab, n = ndimage.label(orange); sizes = ndimage.sum(orange, lab, range(1, n + 1))
        bands = []
        for i in np.argsort(sizes)[::-1][:4]:
            yy, xx = np.nonzero(lab == i + 1)
            if xx.max() - xx.min() > 0.5 * shell["width_px"]: bands.append([int(yy.min()), int(yy.max()), int(xx.min()), int(xx.max())])
        bands.sort()
        if not bands: continue
        bandmask = np.zeros_like(orange)
        for i in np.argsort(sizes)[::-1][:4]:
            yy, xx = np.nonzero(lab == i + 1)
            if xx.max() - xx.min() > 0.5 * shell["width_px"]: bandmask |= lab == i + 1
        w, _ = widest_row(bandmask)
        bsweep.append(dict(smin=smin, bands=bands, widest_row=int(w[0]), x=[w[1], w[2]], width_px=int(w[2] - w[1] + 1), mid_x=(w[1] + w[2]) / 2.0))
    beak = next(b for b in bsweep if abs(b["smin"] - BEAK_SMIN) < 1e-9)
    beak = dict(beak, sweep=bsweep, width_px_range=[min(x["width_px"] for x in bsweep), max(x["width_px"] for x in bsweep)],
                mid_x_range=[min(x["mid_x"] for x in bsweep), max(x["mid_x"] for x in bsweep)])
    beak["width_px_unc"] = math.sqrt((0.5 * (beak["width_px_range"][1] - beak["width_px_range"][0])) ** 2 + 2.0)   # half the sweep range + 1 px per edge
    beak["mid_x_unc"] = math.sqrt((0.5 * (beak["mid_x_range"][1] - beak["mid_x_range"][0])) ** 2 + 0.5)
    width = beak["width_px"]; mid = beak["mid_x"]
    bands = beak["bands"]
    eye = hp.measure_eye(rgb, EYE_BOX, (20, 55))
    L = rgb.mean(axis=2); tof = np.zeros_like(region); tx0, ty0, tx1, ty1 = TOF_BOX; tof[ty0:ty1, tx0:tx1] = L[ty0:ty1, tx0:tx1] < 70
    lab, n = ndimage.label(tof); sizes = ndimage.sum(tof, lab, range(1, n + 1)); tm = lab == (1 + int(np.argmax(sizes)))
    tys, txs = np.nonzero(tm)
    top = shell["top_row"]
    res = dict(image=PHOTO, size_px=[int(rgb.shape[1]), int(rgb.shape[0])], head_region=list(HEAD_REGION),
               head_top_row=int(top), head_top_row_unc_px=float(max(1.0, max(x["top_row"] for x in sweep) - min(x["top_row"] for x in sweep))),
               head_bottom_row=int(ys.max()), widest_row=int(beak["widest_row"]),
               head_width_px=int(width), head_width_px_unc=beak["width_px_unc"], head_width_feature="beak band (jaw + bottom shell) x extent at its widest row, saturation-thresholded accent hue",
               head_mid_x=mid, head_mid_x_unc=beak["mid_x_unc"], shell_silhouette=shell, beak=beak,
               beak_bands_rows=bands, eye=eye,
               tof=dict(x=[int(txs.min()), int(txs.max())], y=[int(tys.min()), int(tys.max())], centre=[float(txs.mean()), float(tys.mean())],
                        w_px=int(txs.max() - txs.min() + 1), h_px=int(tys.max() - tys.min() + 1)))
    # foreshortening: the ring is a circle, its image minor/major = c along the minor-axis direction m; a length along
    # image direction d is scaled by s(d) = sqrt(1 - (1 - c^2) (d . m)^2). Applied as an UNCERTAINTY on every ratio whose
    # numerator runs along a different direction than the width (the sign is known but the flat-lay pose is not fitted)
    c = eye["minor_px"] / eye["major_px"]; mj = np.array(eye["major_axis_dir"]); mnr = np.array([-mj[1], mj[0]])
    def fs(d): return math.sqrt(max(0.0, 1 - (1 - c * c) * float(np.dot(d, mnr)) ** 2))
    s_w, s_v = fs(np.array([1.0, 0.0])), fs(np.array([0.0, 1.0]))
    res["foreshortening"] = dict(ring_minor_over_major=c, view_angle_deg=math.degrees(math.acos(min(1, c))), minor_axis_dir=[float(mnr[0]), float(mnr[1])],
                                 scale_horizontal=s_w, scale_vertical=s_v,
                                 how="a length along image direction d is foreshortened by sqrt(1 - (1 - c^2)(d.m)^2), c = ring minor/major, m = ring minor-axis direction")
    ex, ey = eye["centre"]; ue = 2.0   # ring ellipse centre / axes: +-2 px (hp.measure_eye unc_px)
    uw = res["head_width_px_unc"]; utop = res["head_top_row_unc_px"]; umid = res["head_mid_x_unc"]
    def ratio(num, unum, s_num, s_den=s_w):
        q = num / width
        u_stat = abs(q) * math.sqrt((unum / num) ** 2 + (uw / width) ** 2) if num else unum / width
        u_sys = abs(q) * abs(s_num / s_den - 1)
        return dict(value=q, unc=math.sqrt(u_stat ** 2 + u_sys ** 2), unc_stat=u_stat, unc_foreshortening=u_sys)
    R = dict(eye_od_over_width=ratio(eye["major_px"], ue, 1.0),                      # the major axis is the true diameter, unforeshortened
             eye_minor_over_major=dict(value=c, unc=math.sqrt(2) * ue / eye["major_px"], dimensionless=True, unc_stat=math.sqrt(2) * ue / eye["major_px"], unc_foreshortening=0.0),
             eye_below_top_over_width=ratio(ey - top, math.sqrt(ue ** 2 + utop ** 2), s_v),
             eye_x_offset_over_width=ratio(ex - mid, math.sqrt(ue ** 2 + umid ** 2), s_w),
             tof_x_from_eye_over_width=ratio(res["tof"]["centre"][0] - ex, math.sqrt(ue ** 2 + 1.0), s_w),
             tof_y_from_eye_over_width=ratio(res["tof"]["centre"][1] - ey, math.sqrt(ue ** 2 + 1.0), s_v),
             tof_w_over_width=ratio(res["tof"]["w_px"], 1.5, s_w), tof_h_over_width=ratio(res["tof"]["h_px"], 1.5, s_v),
             first_beak_band_top_below_top_over_width=ratio(bands[0][0] - top, math.sqrt(1.0 + utop ** 2), s_v) if bands else None)
    res["ratios"] = {k: (v["value"] if v else None) for k, v in R.items()}
    res["ratios_unc"] = {k: v for k, v in R.items() if v}
    # picture
    im = Image.fromarray(rgb.astype(np.uint8)); d = ImageDraw.Draw(im)
    d.line([(beak["x"][0], beak["widest_row"]), (beak["x"][1], beak["widest_row"])], fill=(30, 90, 220), width=3)
    d.line([(shell["x"][0], shell["widest_row"]), (shell["x"][1], shell["widest_row"])], fill=(200, 120, 200), width=2)
    d.line([(mid, top), (mid, ys.max())], fill=(30, 90, 220), width=1)
    draw_ellipse(d, eye, (30, 160, 60))
    d.rectangle([txs.min(), tys.min(), txs.max(), tys.max()], outline=(200, 40, 30), width=2)
    d.rectangle([xs.min(), ys.min(), xs.max(), ys.max()], outline=(120, 60, 200), width=2)
    return res, im.crop((x0 - 20, y0 - 20, x1 + 20, y1 + 20)), rgb


def mesh_side():
    model, data = hp.load_model(); hr = hp.HeadRenderer(model, data, size=1400)
    g = hr.eye_gids[0]; mid = model.geom_dataid[g]; a, n = model.mesh_vertadr[mid], model.mesh_vertnum[mid]
    v = model.mesh_vert[a:a + n]; ext = v.max(0) - v.min(0); thin = int(np.argmin(ext))
    def elev(pitch):
        hr.pose(pitch, 0, 0, 0); R = data.geom_xmat[g].reshape(3, 3); ax = R[:, thin]
        if ax[0] > 0: ax = -ax
        return math.degrees(math.atan2(ax[2], -ax[0]))
    lo, hi = -40.0, 40.0
    for _ in range(50):
        m = (lo + hi) / 2
        if elev(m) > 0: hi = m
        else: lo = m
    level = (lo + hi) / 2
    hr.pose(level, 0, 0, 0)
    hr.cam.orthographic = 1; model.vis.global_.fovy = 45.0
    hr.cam.azimuth = 180; hr.cam.elevation = 0; hr.cam.distance = 0.30; hr.cam.lookat[:] = data.xpos[hr.head_bid]
    head, eye, ids, isg = hr.masks()
    ys, xs = np.nonzero(head)
    rows = [(y, int(np.nonzero(head[y])[0].min()), int(np.nonzero(head[y])[0].max())) for y in range(ys.min(), ys.max() + 1)]
    wrow = max(rows, key=lambda r: r[2] - r[1]); width = wrow[2] - wrow[1] + 1
    # px/mm from the head vertices' extent along the camera right axis (self-calibrating)
    c = hr.r.scene.camera[0]; fwd = np.array(c.forward, float); up = np.array(c.up, float)
    right = np.cross(fwd, up); right /= np.linalg.norm(right)
    pts = []
    for mname in hp.HEAD_GEOM_MESHES:
        for gg in hr.gid.get(mname, []):
            mid2 = model.geom_dataid[gg]; a2, n2 = model.mesh_vertadr[mid2], model.mesh_vertnum[mid2]
            vv = model.mesh_vert[a2:a2 + n2]; R = data.geom_xmat[gg].reshape(3, 3); t = data.geom_xpos[gg]; pts.append((R @ vv.T).T + t)
    V = np.vstack(pts) * 1000; pr = V @ right
    mm_w = float(pr.max() - pr.min()); pxmm = width / mm_w
    # DEPTH of every feature along the camera axis (mm, negative = nearer the camera): the flat-lay photograph is a
    # perspective picture and the ring stands ~25 mm nearer its camera than the shell rim, so a photo ratio between two
    # features at different depths is magnified by their depth ratio — carried into the comparison as a D bracket.
    def vert_of(names):
        return np.vstack([(data.geom_xmat[gg].reshape(3, 3) @ model.mesh_vert[model.mesh_vertadr[model.geom_dataid[gg]]:model.mesh_vertadr[model.geom_dataid[gg]] + model.mesh_vertnum[model.geom_dataid[gg]]].T).T + data.geom_xpos[gg]
                          for nm in names for gg in hr.gid.get(nm, [])]) * 1000
    def depth_at_extreme(names, axis, sign, band=0.5):
        Vv = vert_of(names); q = (Vv @ axis) * sign; sel = q > q.max() - band
        return float((Vv[sel] @ fwd).mean()), float((Vv[sel] @ fwd).min()), float((Vv[sel] @ fwd).max())
    ring = vert_of(["noenoeil"]); z_ring_front = float((ring @ fwd).min())
    depths = dict(ring_front_face=z_ring_front,
                  ring_outer_edge=depth_at_extreme(["noenoeil"], right, 1.0)[0],
                  beak_width_edge=0.5 * (depth_at_extreme(["bottom_head_shell"], right, 1.0)[0] + depth_at_extreme(["jaw"], right, 1.0, 5.0)[1]),
                  shell_width_edge=depth_at_extreme(["top_head_shell"], right, 1.0)[0],
                  shell_top=depth_at_extreme(["top_head_shell"], up, 1.0)[0],
                  bottom_shell_top_edge=depth_at_extreme(["bottom_head_shell"], up, 1.0)[0],
                  face_front=float((vert_of(["face_part"]) @ fwd).min()),
                  how="mean camera-axis depth (mm, negative = nearer) of the vertices within 0.5 mm of each feature's extreme in the level front view; jaw: its nearest generator")
    eys, exs = np.nonzero(eye); e = hp.ellipse_of(np.stack([exs, eys], 1).astype(float))
    def rows_of(name):
        m = np.isin(ids, hr.gid[name]) & isg; yy, xx = np.nonzero(m); return [int(yy.min()), int(yy.max()), int(xx.min()), int(xx.max())]
    parts = {k: rows_of(k) for k in ("top_head_shell", "bottom_head_shell", "jaw", "face_part", "noenoeil")}
    # the SAME feature as the photograph's beak band: the bottom shell + jaw masks' x extent at their widest row
    beakmask = (np.isin(ids, hr.gid["bottom_head_shell"] + hr.gid["jaw"])) & isg
    bw, _ = widest_row(beakmask); width = bw[2] - bw[1] + 1; wrow = bw
    midx = (wrow[1] + wrow[2]) / 2.0
    res = dict(level_pitch_total_deg=level, level_how="bisection on the noenoeil geom's thin axis (ring axis) elevation = 0 in world", depths=depths,
               render_px=1400, px_per_mm=pxmm, px_per_mm_how="head-mask widest row (px) / head vertices' extent along the camera right axis (mm)",
               head_width_px=int(width), head_width_mm=mm_w, head_top_row=int(ys.min()), head_bottom_row=int(ys.max()), widest_row=int(wrow[0]),
               head_mid_x=midx, parts_rows=parts, eye=e,
               eye_od_mm=e["major_px"] / pxmm, eye_below_top_mm=(e["centre"][1] - ys.min()) / pxmm)
    res["head_width_feature"] = "bottom_head_shell + jaw masks' x extent at their widest row (the beak band, as in the photograph)"
    res["ratios"] = dict(eye_od_over_width=e["major_px"] / width, eye_minor_over_major=e["minor_px"] / e["major_px"],
                         eye_below_top_over_width=(e["centre"][1] - ys.min()) / width,
                         eye_x_offset_over_width=(e["centre"][0] - midx) / width,
                         tof_x_from_eye_over_width=22.4 / MESH_HEAD_W, tof_y_from_eye_over_width=None,
                         tof_w_over_width=None, tof_h_over_width=None,
                         first_beak_band_top_below_top_over_width=(parts["bottom_head_shell"][0] - ys.min()) / width)
    # render-side uncertainty: +-1 px on each mask edge at 1400 px (an antialiased segmentation edge), no foreshortening (orthographic, level)
    u1 = math.sqrt(2.0) / width
    res["ratios_unc"] = {k: dict(value=v, unc=abs(v) * math.sqrt((u1 * width / max(1e-9, abs(v) * width)) ** 2 + (u1) ** 2) if v else u1) for k, v in res["ratios"].items() if v is not None}
    res["ratios_note"] = ("tof_x_from_eye: the MJCF 'tof' site sits 22.4 mm to the right of the eye axis (PROPORTIONS.md, from the MJCF); "
                          "the mesh has no ToF window geom, so its size and vertical offset are CANNOT DETERMINE on the mesh side")
    im = Image.fromarray(hr.shaded()); d = ImageDraw.Draw(im)
    d.line([(wrow[1], wrow[0]), (wrow[2], wrow[0])], fill=(30, 90, 220), width=3)
    d.line([(midx, ys.min()), (midx, ys.max())], fill=(30, 90, 220), width=1)
    draw_ellipse(d, e, (30, 160, 60))
    d.rectangle([xs.min(), ys.min(), xs.max(), ys.max()], outline=(120, 60, 200), width=2)
    pad = 60
    return res, im.crop((xs.min() - pad, ys.min() - pad, xs.max() + pad, ys.max() + pad))


def main():
    p, pim, rgb = photo_side()
    m, mim = mesh_side()
    comp = {}
    for key in p["ratios"]:
        a, b = p["ratios"][key], m["ratios"].get(key)
        pu = (p["ratios_unc"].get(key) or {}); mu = (m["ratios_unc"].get(key) or {})
        if a is None or b is None:
            comp[key] = dict(photo=a, photo_unc=pu.get("unc"), mesh=b, verdict="CANNOT DETERMINE", why="no mesh-side value: the mesh has no ToF window geom")
            continue
        if pu.get("dimensionless"):
            comp[key] = dict(photo=a, photo_unc=pu.get("unc"), mesh=b, diff=a - b, dimensionless=True, verdict="n/a",
                             why="a unitless axis ratio — the view tilt of each picture (photo %.1f deg, render %.1f deg off-axis), not a length; carries no mm" % (
                                 math.degrees(math.acos(min(1, a))), math.degrees(math.acos(min(1, b)))))
            continue
        u = math.sqrt((pu.get("unc") or 0.0) ** 2 + (mu.get("unc") or 0.0) ** 2)
        dev = (a - b) * MESH_HEAD_W; umm = u * MESH_HEAD_W
        grade = lambda dv: "PASS" if abs(dv) + umm <= RULE_MM else ("FAIL" if abs(dv) - umm > RULE_MM else "CANNOT DETERMINE")
        row = dict(photo=a, photo_unc=pu.get("unc"), photo_unc_stat=pu.get("unc_stat"), photo_unc_foreshortening=pu.get("unc_foreshortening"),
                   mesh=b, mesh_unc=mu.get("unc"), diff=a - b, diff_pct=(a - b) / b * 100 if b else None,
                   photo_mm_if_width_is_mesh=a * MESH_HEAD_W, mesh_mm=b * MESH_HEAD_W, dev_mm=dev, dev_unc_mm=umm, verdict_at_infinite_D=grade(dev))
        # PERSPECTIVE: the photograph's numerator feature and its width feature sit at different depths (mesh, m["depths"]);
        # a camera at distance D from the ring's front face magnifies each by 1/(D + z - z_ring). The store frame gives no D,
        # so the ratio is corrected over a bracket D = D_MIN .. infinity and graded at every point of it: one verdict only
        # if the bracket agrees, else CANNOT DETERMINE naming D as what settles it.
        zn, zw = FEATURE_DEPTH.get(key)
        if zn is not None:
            dz = m["depths"]; z0 = dz["ring_front_face"]; z_num = dz[zn]; z_w = dz[zw]
            pts = []
            for Dm in D_BRACKET_MM:
                q_true = a * (Dm + z_num - z0) / (Dm + z_w - z0)
                dv = (q_true - b) * MESH_HEAD_W
                pts.append(dict(D_mm=Dm, photo_corrected=q_true, dev_mm=dv, verdict=grade(dv)))
            vs = {x["verdict"] for x in pts}
            row.update(perspective=dict(numerator_depth=zn, numerator_depth_mm=z_num, width_depth=zw, width_depth_mm=z_w, bracket=pts,
                                        note="photo ratio corrected by (D + z_num - z_ring)/(D + z_w - z_ring) for D from %.0f mm (a product flat-lay cannot be nearer) to infinity" % D_BRACKET_MM[0]),
                       dev_mm_range=[min(x["dev_mm"] for x in pts), max(x["dev_mm"] for x in pts)],
                       verdict=(pts[0]["verdict"] if len(vs) == 1 else "CANNOT DETERMINE"),
                       verdict_why=("the same verdict at every camera distance from %.0f mm to infinity" % D_BRACKET_MM[0]) if len(vs) == 1 else
                                   ("the verdict changes with the flat-lay camera distance, which the photograph does not give: %s" % "; ".join(
                                       "D %s -> %+.2f mm %s" % (("%.0f mm" % x["D_mm"]) if x["D_mm"] < 1e8 else "inf", x["dev_mm"], x["verdict"]) for x in pts)))
        else:
            row["verdict"] = grade(dev); row["verdict_why"] = "numerator and width features at the same depth: no perspective term"
        comp[key] = row
    fsh = p["foreshortening"]
    out = dict(generated=time.strftime("%Y-%m-%d %H:%M"), method=__doc__, photo=p, mesh=m, comparison=comp,
               mesh_head_width_mm=MESH_HEAD_W, rule_mm=RULE_MM,
               uncertainty=("every ratio carries a propagated uncertainty: the head width from the beak band's saturation sweep %d-%d px (half-range) plus "
                            "1 px per edge, +-2 px on the ring ellipse, the shell top row's threshold spread, and the flat-lay foreshortening — the ring is "
                            "seen %.1f deg off-axis (minor/major %.4f), which scales vertical lengths by %.4f and horizontal by %.4f, taken as a systematic "
                            "on every ratio whose numerator and denominator run along different axes. The shell silhouette's own width sweeps %d-%d px "
                            "over min-channel thresholds %s (the soft shadow to the right of the shell), which is why the saturated beak band is the "
                            "width used. The photo's mm values assume the head width is the mesh's 91.763 mm — they are the implied product dimension, "
                            "not an independent measurement." % (
                                p["beak"]["width_px_range"][0], p["beak"]["width_px_range"][1], fsh["view_angle_deg"], fsh["ring_minor_over_major"],
                                fsh["scale_vertical"], fsh["scale_horizontal"], p["shell_silhouette"]["width_px_range"][0], p["shell_silhouette"]["width_px_range"][1],
                                SHELL_THRESHOLDS)))
    if p["shell_silhouette"]["widest_row_on_window_edge"]:
        out["window_warning"] = "the shell silhouette's widest row sits on the analysis window's edge — the window clips the head"
    json.dump(out, open(os.path.join(OUT, "front_view.json"), "w"), indent=1, default=float)
    # pair picture: real | ours, same height
    th = 700
    a = pim.resize((int(pim.size[0] * th / pim.size[1]), th), Image.LANCZOS)
    b = mim.resize((int(mim.size[0] * th / mim.size[1]), th), Image.LANCZOS)
    sheet = Image.new("RGB", (a.size[0] + b.size[0] + 30, th + 50), (255, 255, 255)); d = ImageDraw.Draw(sheet)
    sheet.paste(a, (10, 40)); sheet.paste(b, (a.size[0] + 20, 40))
    d.text((12, 12), "REAL  inside-the-box flat-lay (true front view)  blue = beak-band width + mid-line (the width used), violet = shell silhouette widest row (shadow-inflated), green = eye ring, red = ToF window", fill=(0, 0, 0))
    d.text((a.size[0] + 22, 12), "OURS  mesh, true front view, head level (pitch_total %.3f deg)" % m["level_pitch_total_deg"], fill=(0, 0, 0))
    sheet.save(os.path.join(OUT, "front_pair.png"))
    print(json.dumps(comp, indent=1, default=float)); print("wrote", os.path.join(OUT, "front_view.json"))


if __name__ == "__main__":
    main()
