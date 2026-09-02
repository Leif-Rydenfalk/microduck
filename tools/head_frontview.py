#!/usr/bin/env python3
"""head_frontview.py — the face layout, scale-free, from the one true FRONT view.

images/store/store_microduck-inside-the-box.png is a flat-lay: the robot lies on
its back and the camera looks straight at the face. The photo is a composite
(the battery in the same frame measures 268 px across = 70.8 mm and the gamepad
485 px = ~152 mm — two different mm/px, so it is NOT one scale), so nothing here
uses mm/px from another object. Instead every number is a RATIO inside the head
itself (one object, one depth), compared with the same ratio measured on our
mesh rendered in a true front view with the head LEVEL (eye-ring axis
horizontal: pitch_total = 40.000 deg, bisected on the noenoeil geom axis).

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
HEAD_REGION = (100, 180, 600, 480)     # x0,y0,x1,y1 in the photo: the head + beak, nothing else
EYE_BOX = (250, 230, 440, 420)
TOF_BOX = (410, 290, 510, 370)
MESH_HEAD_W = 91.763                    # top_head_shell mesh y extent, mm (out/verify/mech_dims.json / head_probe)


def draw_ellipse(d, e, colour, w=3):
    cx, cy = e["centre"]; a = e["major_px"] / 2; b = e["minor_px"] / 2
    ang = math.atan2(e["major_axis_dir"][1], e["major_axis_dir"][0])
    pts = [(cx + a * math.cos(t) * math.cos(ang) - b * math.sin(t) * math.sin(ang),
            cy + a * math.cos(t) * math.sin(ang) + b * math.sin(t) * math.cos(ang)) for t in np.linspace(0, 2 * math.pi, 90)]
    d.line(pts + [pts[0]], fill=colour, width=w)


def photo_side():
    rgb = hp.load_rgb(os.path.join(REPO, PHOTO)); h, s, v = hp.hsv(rgb)
    x0, y0, x1, y1 = HEAD_REGION
    sil = hp.silhouette(rgb); region = np.zeros_like(sil); region[y0:y1, x0:x1] = True
    head = sil & region
    lab, n = ndimage.label(head); sizes = ndimage.sum(head, lab, range(1, n + 1)); head = lab == (1 + int(np.argmax(sizes)))
    head = ndimage.binary_fill_holes(head)
    ys, xs = np.nonzero(head)
    rows = [(y, int(np.nonzero(head[y])[0].min()), int(np.nonzero(head[y])[0].max())) for y in range(ys.min(), ys.max() + 1)]
    wrow = max(rows, key=lambda r: r[2] - r[1])
    width = wrow[2] - wrow[1] + 1
    # the cream shell (low saturation) vs the accent beak bands: shell top edge = head top; beak bands = rows of accent hue
    orange = (h >= 15) & (h <= 50) & (s > 0.45) & (v > 0.3) & region
    lab, n = ndimage.label(orange); sizes = ndimage.sum(orange, lab, range(1, n + 1))
    bands = []
    for i in np.argsort(sizes)[::-1][:4]:
        yy, xx = np.nonzero(lab == i + 1)
        if xx.max() - xx.min() > 0.5 * width: bands.append([int(yy.min()), int(yy.max()), int(xx.min()), int(xx.max())])
    bands.sort()
    eye = hp.measure_eye(rgb, EYE_BOX, (20, 55))
    L = rgb.mean(axis=2); tof = np.zeros_like(sil); tx0, ty0, tx1, ty1 = TOF_BOX; tof[ty0:ty1, tx0:tx1] = L[ty0:ty1, tx0:tx1] < 70
    lab, n = ndimage.label(tof); sizes = ndimage.sum(tof, lab, range(1, n + 1)); tm = lab == (1 + int(np.argmax(sizes)))
    tys, txs = np.nonzero(tm)
    mid = (wrow[1] + wrow[2]) / 2.0
    res = dict(image=PHOTO, size_px=[int(rgb.shape[1]), int(rgb.shape[0])], head_region=list(HEAD_REGION),
               head_top_row=int(ys.min()), head_bottom_row=int(ys.max()), widest_row=int(wrow[0]), head_width_px=int(width),
               head_mid_x=mid, beak_bands_rows=bands, eye=eye,
               tof=dict(x=[int(txs.min()), int(txs.max())], y=[int(tys.min()), int(tys.max())], centre=[float(txs.mean()), float(tys.mean())],
                        w_px=int(txs.max() - txs.min() + 1), h_px=int(tys.max() - tys.min() + 1)))
    res["ratios"] = dict(eye_od_over_width=eye["major_px"] / width, eye_minor_over_major=eye["minor_px"] / eye["major_px"],
                         eye_below_top_over_width=(eye["centre"][1] - ys.min()) / width,
                         eye_x_offset_over_width=(eye["centre"][0] - mid) / width,
                         tof_x_from_eye_over_width=(res["tof"]["centre"][0] - eye["centre"][0]) / width,
                         tof_y_from_eye_over_width=(res["tof"]["centre"][1] - eye["centre"][1]) / width,
                         tof_w_over_width=res["tof"]["w_px"] / width, tof_h_over_width=res["tof"]["h_px"] / width,
                         first_beak_band_top_below_top_over_width=((bands[0][0] - ys.min()) / width) if bands else None)
    # picture
    im = Image.fromarray(rgb.astype(np.uint8)); d = ImageDraw.Draw(im)
    d.line([(wrow[1], wrow[0]), (wrow[2], wrow[0])], fill=(30, 90, 220), width=3)
    d.line([(mid, ys.min()), (mid, ys.max())], fill=(30, 90, 220), width=1)
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
    lo, hi = 0.0, 80.0
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
    eys, exs = np.nonzero(eye); e = hp.ellipse_of(np.stack([exs, eys], 1).astype(float))
    def rows_of(name):
        m = np.isin(ids, hr.gid[name]) & isg; yy, xx = np.nonzero(m); return [int(yy.min()), int(yy.max()), int(xx.min()), int(xx.max())]
    parts = {k: rows_of(k) for k in ("top_head_shell", "bottom_head_shell", "jaw", "face_part", "noenoeil")}
    midx = (wrow[1] + wrow[2]) / 2.0
    res = dict(level_pitch_total_deg=level, level_how="bisection on the noenoeil geom's thin axis (ring axis) elevation = 0 in world",
               render_px=1400, px_per_mm=pxmm, px_per_mm_how="head-mask widest row (px) / head vertices' extent along the camera right axis (mm)",
               head_width_px=int(width), head_width_mm=mm_w, head_top_row=int(ys.min()), head_bottom_row=int(ys.max()), widest_row=int(wrow[0]),
               head_mid_x=midx, parts_rows=parts, eye=e,
               eye_od_mm=e["major_px"] / pxmm, eye_below_top_mm=(e["centre"][1] - ys.min()) / pxmm)
    res["ratios"] = dict(eye_od_over_width=e["major_px"] / width, eye_minor_over_major=e["minor_px"] / e["major_px"],
                         eye_below_top_over_width=(e["centre"][1] - ys.min()) / width,
                         eye_x_offset_over_width=(e["centre"][0] - midx) / width,
                         tof_x_from_eye_over_width=22.4 / MESH_HEAD_W, tof_y_from_eye_over_width=None,
                         tof_w_over_width=None, tof_h_over_width=None,
                         first_beak_band_top_below_top_over_width=(parts["bottom_head_shell"][0] - ys.min()) / width)
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
        if a is None or b is None:
            comp[key] = dict(photo=a, mesh=b, verdict="CANNOT DETERMINE", why="no mesh-side value")
            continue
        comp[key] = dict(photo=a, mesh=b, diff=a - b, diff_pct=(a - b) / b * 100 if b else None,
                         photo_mm_if_width_is_mesh=a * MESH_HEAD_W, mesh_mm=b * MESH_HEAD_W, dev_mm=(a - b) * MESH_HEAD_W)
    out = dict(generated=time.strftime("%Y-%m-%d %H:%M"), method=__doc__, photo=p, mesh=m, comparison=comp,
               mesh_head_width_mm=MESH_HEAD_W,
               uncertainty="the flat-lay ring is seen 11 deg off-axis (minor/major %.4f), so ratios along the face are good to ~2 %%; "
                           "the photo's mm values assume the head width is the mesh's 91.763 mm — they are the implied product dimension, "
                           "not an independent measurement" % p["ratios"]["eye_minor_over_major"])
    json.dump(out, open(os.path.join(OUT, "front_view.json"), "w"), indent=1, default=float)
    # pair picture: real | ours, same height
    th = 700
    a = pim.resize((int(pim.size[0] * th / pim.size[1]), th), Image.LANCZOS)
    b = mim.resize((int(mim.size[0] * th / mim.size[1]), th), Image.LANCZOS)
    sheet = Image.new("RGB", (a.size[0] + b.size[0] + 30, th + 50), (255, 255, 255)); d = ImageDraw.Draw(sheet)
    sheet.paste(a, (10, 40)); sheet.paste(b, (a.size[0] + 20, 40))
    d.text((12, 12), "REAL  inside-the-box flat-lay (true front view)  blue = widest row, green = eye ring, red = ToF window", fill=(0, 0, 0))
    d.text((a.size[0] + 22, 12), "OURS  mesh, true front view, head level (pitch_total %.3f deg)" % m["level_pitch_total_deg"], fill=(0, 0, 0))
    sheet.save(os.path.join(OUT, "front_pair.png"))
    print(json.dumps(comp, indent=1, default=float)); print("wrote", os.path.join(OUT, "front_view.json"))


if __name__ == "__main__":
    main()
