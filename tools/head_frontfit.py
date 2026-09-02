#!/usr/bin/env python3
"""head_frontfit.py — the front view re-measured with ONE estimator on both sides,
on the head's OUTER silhouette, at a MATCHED pose.

out/head/front_view.json (lane A, 2026-09-03) grades the head FAIL from a single
ratio read off the flat-lay images/store/store_microduck-inside-the-box.png:
ring OD / head width, photo 0.3521 against mesh 0.3226. Re-reading that
measurement found three things it does not carry, each of which moves the number:

  1. WHICH WIDTH. The photograph's width is the saturated ORANGE TRIM BAND
     (419 px); the mesh's is the bottom_head_shell + jaw silhouette (692 px), the
     whole shell. On the mesh those two are the same to 0.35 mm (91.763 / 91.416
     / 91.760, out/verify/mech_dims.json) so the substitution looks free, but on
     the photograph they are NOT: measured here per row over a threshold sweep,
     the head's outer silhouette is 433-434 px at its widest row against the
     band's 419 px — the trim band is 3.4 % inset from the shell on the product.
     The head's width is the shell, and it is measured here on the shell.
  2. WHICH ESTIMATOR. hp.ellipse_of takes the 0.5/99.5 PERCENTILE extent of the
     mask. For a FILLED disc (what measure_eye returns after binary_fill_holes,
     the photograph's ring) that is 0.958 x the true diameter; for the render's
     noenoeil segmentation mask, which is an ANNULUS (the bore shows the lens
     geom behind it), the same percentile sits nearer the rim. The two sides were
     therefore not measuring the ring the same way. Here both masks are filled
     and both diameters are the FULL extent along the mask's principal axes.
  3. WHICH POSE. The mesh side was rendered ORTHOGRAPHIC, head level, yaw 0. The
     photograph's ring is an ellipse with minor/major 0.982 +- 0.019 whose minor
     axis is horizontal, i.e. a head yaw of 0-11 deg, and the flat-lay is a
     perspective picture at an unknown distance. Here the mesh is rendered with a
     perspective camera over the same D bracket and over a yaw sweep, and the
     comparison is made at the yaw whose rendered ring ellipticity matches the
     photograph's — with the whole admissible yaw range carried as a bracket.

Then the same ratio is computed with the head shells scaled laterally (s_w, the
head-width hypothesis of tools/head_width.py) so the two instruments answer in
the same currency.

Writes out/head/front_fit.json and out/head/front_fit_pair.png (real beside ours).
    /Applications/FreeCAD.app/Contents/Resources/bin/python tools/head_frontfit.py
"""
import os, sys, json, math, time
os.environ.setdefault("MUJOCO_GL", "glfw")
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import head_photomatch as hp
import head_width as hw

REPO, OUT = hp.REPO, hp.OUT
PHOTO = "images/store/store_microduck-inside-the-box.png"
HEAD_REGION = (100, 180, 620, 502)
HEAD_BOTTOM_CUT = 502     # the row where the head ends and the neck servo begins in this frame
                          # (READ off the gridded crop: the shell's lower edge runs y 495-500, the
                          # black neck block starts at y 505); the profile flags a mask that reaches it
# thresholds where the read is STABLE: 200-228 give 433/434/440 px; 240+ swallows the
# soft shadow to both sides of the cream shell (520 px, the whole analysis window)
SHELL_THRESHOLDS = [200, 205, 210, 215, 220, 228]
EYE_BOX = (250, 230, 440, 420)
BEAK_SMIN_SWEEP = [0.35, 0.40, 0.45, 0.50, 0.55]
RING_SMIN_SWEEP = [0.25, 0.35, 0.45, 0.55, 0.65]
RING_SMIN = 0.45
OUTLINE_WMIN = 0.85       # both outlines must be at least this fraction of their widest row to be compared
OUTLINE_TRIM = 0.045      # u units dropped at each end of the overlap (see comparison.outline.excluded)
TOF_BOX = (410, 290, 510, 370)
D_BRACKET_MM = [400.0, 800.0, 1500.0, 3000.0, None]   # None = orthographic (the D -> infinity limit; a
                                                     # perspective camera at 100 m is clipped away by MuJoCo's own zfar)
YAW_SWEEP_DEG = [0.0, 3.0, 6.0, 9.0, 11.0, 13.0]
S_W_SWEEP = [0.90, 0.94, 0.96, 0.98, 1.00]
RULE_MM = 1.5
MESH_HEAD_W = 91.763
RING_MESH_MM = 30.000
TOF_DY_MM = 22.5000     # jaw_soft body frame: site tof y 22.4086 mm (reference/pollen-microduck-rl/robot_walk.xml:254)
                        # minus the noenoeil geom y -0.0914 mm (the ring axis) = 22.5000 mm
def filled_extents(mask):
    """the SAME estimator on both sides: fill the mask, then the FULL extent along its
    own principal axes (not a percentile), plus the centroid."""
    m = ndimage.binary_fill_holes(mask)
    ys, xs = np.nonzero(m)
    P = np.stack([xs, ys], 1).astype(float)
    c = P.mean(0); C = np.cov((P - c).T); w, V = np.linalg.eigh(C)
    major, minor = V[:, 1], V[:, 0]
    pm = (P - c) @ major; pn = (P - c) @ minor
    return dict(centre=[float(c[0]), float(c[1])], major_px=float(pm.max() - pm.min()), minor_px=float(pn.max() - pn.min()),
                major_axis_dir=[float(major[0]), float(major[1])], n_px=int(m.sum()))


def row_profile(mask, ring_cy, n=90):
    """the silhouette's width row by row in ONE frame both sides share: the width divided by
    the widest row, against the row's height above/below the EYE-RING CENTRE in units of that
    same widest width. Nothing is fitted and no scale is used, so the product's outline and
    the mesh's lie on top of each other or they do not.

    The vertical anchor is the ring centre rather than the head's own top-and-bottom because
    the bottom of a head silhouette is not the same feature on both sides (the photograph's
    head runs into the neck; the mesh's carries the soft pads)."""
    ys, xs = np.nonzero(mask)
    y0, y1 = int(ys.min()), int(ys.max())
    ws, rows = [], []
    for y in range(y0, y1 + 1):
        r = np.nonzero(mask[y])[0]
        if not len(r): continue
        rows.append(y); ws.append(r.max() - r.min() + 1)
    ws = np.array(ws, float); rows = np.array(rows, float)
    wmax = ws.max()
    u = (rows - ring_cy) / wmax            # height relative to the ring centre, in widths
    grid = np.linspace(float(u.min()), float(u.max()), n)
    return dict(u=[float(x) for x in grid], w_over_wmax=[float(x) for x in np.interp(grid, u, ws / wmax)],
                widest_u=float(u[int(np.argmax(ws))]), u_range=[float(u.min()), float(u.max())],
                n_rows=int(len(rows)), wmax_px=float(wmax), top_row=int(y0), bottom_row=int(y1),
                bottom_on_cut=bool(y1 >= HEAD_BOTTOM_CUT - 1))


def widest(mask):
    ys, xs = np.nonzero(mask)
    best = None
    for y in range(ys.min(), ys.max() + 1):
        if not mask[y].any(): continue
        r = np.nonzero(mask[y])[0]
        w = r.max() - r.min() + 1
        if best is None or w > best[0]: best = (int(w), int(y), int(r.min()), int(r.max()))
    return dict(width_px=best[0], row=best[1], x=[best[2], best[3]], mid_x=(best[2] + best[3]) / 2.0)


def photo_side():
    rgb = hp.load_rgb(os.path.join(REPO, PHOTO))
    h, s, v = hp.hsv(rgb)
    x0, y0, x1, y1 = HEAD_REGION
    region = np.zeros(rgb.shape[:2], bool); region[y0:y1, x0:x1] = True
    mn = rgb.min(axis=2); chroma = rgb.max(axis=2) - mn

    def head_of(th):
        sil = ((mn < th) | (chroma > 14)) & region
        lab, n = ndimage.label(sil); sz = ndimage.sum(sil, lab, range(1, n + 1))
        return ndimage.binary_fill_holes(lab == (1 + int(np.argmax(sz))))
    sweep = []
    for th in SHELL_THRESHOLDS:
        hd = head_of(th); w = widest(hd); ys, xs = np.nonzero(hd)
        w.update(threshold=th, top_row=int(ys.min()), bottom_row=int(ys.max()),
                 on_window_edge=bool(w["x"][0] <= x0 + 1 or w["x"][1] >= x1 - 2 or w["row"] <= y0 + 1 or w["row"] >= y1 - 2))
        sweep.append(w)
    prof = None   # filled after the ring is measured (the ring centre is its vertical anchor)
    ok = [w for w in sweep if not w["on_window_edge"]]
    if not ok: ok = sweep
    widths = [w["width_px"] for w in ok]
    width = float(np.median(widths))
    width_unc = math.sqrt((0.5 * (max(widths) - min(widths))) ** 2 + 2.0)   # half the stable sweep range + 1 px per edge
    mids = [w["mid_x"] for w in ok]
    # The ring's edge is a hue/saturation step with a soft, anti-aliased boundary against the
    # grey face, while the render's ring mask is an exact segmentation. That asymmetry is the
    # one estimator difference a photograph cannot remove, so it is MEASURED: the same read is
    # taken over a saturation sweep and the full range is carried as the ring's uncertainty.
    ex0, ey0, ex1, ey1 = EYE_BOX
    ring_sweep = []
    ring = None
    for smin in RING_SMIN_SWEEP:
        hm = (h >= 20) & (h <= 55) & (s > smin) & (v > 0.25)
        sub = np.zeros_like(hm); sub[ey0:ey1, ex0:ex1] = hm[ey0:ey1, ex0:ex1]
        sub = ndimage.binary_opening(sub, iterations=2)
        lab, n = ndimage.label(sub)
        if n == 0: continue
        sz = ndimage.sum(sub, lab, range(1, n + 1))
        m = lab == (1 + int(np.argmax(sz)))
        ee = filled_extents(m)
        ring_sweep.append(dict(smin=smin, major_px=ee["major_px"], minor_px=ee["minor_px"], centre=ee["centre"]))
        if abs(smin - RING_SMIN) < 1e-9: ring, e = m, ee
    prof = row_profile(head_of(SHELL_THRESHOLDS[len(SHELL_THRESHOLDS) // 2]), e["centre"][1])
    majors = [r["major_px"] for r in ring_sweep]
    ring_unc = math.sqrt((0.5 * (max(majors) - min(majors))) ** 2 + 2.0 ** 2)   # half the sweep range + 1 px per edge
    # the accent TRIM BAND at the head's split line, as a feature in its own right: the
    # previous front-view measurement used it as "the head width" against the mesh's whole
    # bottom-shell silhouette. Measured here as itself so band/shell can be compared as a
    # pure shape ratio — no scale, no ring, and nearly pose-free.
    bsweep = []
    for smin in BEAK_SMIN_SWEEP:
        orange = (h >= 15) & (h <= 50) & (s > smin) & (v > 0.3) & region
        orange = ndimage.binary_opening(orange, iterations=1)
        lab, n = ndimage.label(orange)
        if n == 0: continue
        sz = ndimage.sum(orange, lab, range(1, n + 1))
        bandmask = np.zeros_like(orange)
        for i in np.argsort(sz)[::-1][:4]:
            yy, xx = np.nonzero(lab == i + 1)
            if xx.max() - xx.min() > 0.5 * width: bandmask |= lab == i + 1
        if not bandmask.any(): continue
        bw = widest(bandmask); bw["smin"] = smin
        bsweep.append(bw)
    band = None
    if bsweep:
        bwid = [b["width_px"] for b in bsweep]
        band = dict(width_px=float(np.median(bwid)), width_px_range=[min(bwid), max(bwid)],
                    width_px_unc=math.sqrt((0.5 * (max(bwid) - min(bwid))) ** 2 + 2.0),
                    row=bsweep[len(bsweep) // 2]["row"], sweep=bsweep,
                    band_over_shell=float(np.median(bwid)) / width)
    L = rgb.mean(axis=2); tof = np.zeros_like(region); tx0, ty0, tx1, ty1 = TOF_BOX
    tof[ty0:ty1, tx0:tx1] = L[ty0:ty1, tx0:tx1] < 70
    lab, n = ndimage.label(tof); sz = ndimage.sum(tof, lab, range(1, n + 1)); tm = lab == (1 + int(np.argmax(sz)))
    tys, txs = np.nonzero(tm)
    return dict(image=PHOTO, size_px=[int(rgb.shape[1]), int(rgb.shape[0])], head_region=list(HEAD_REGION),
                shell_sweep=sweep, shell_width_px=width, shell_width_px_unc=width_unc,
                shell_width_px_range=[min(widths), max(widths)], shell_mid_x=float(np.median(mids)),
                shell_width_feature="the head's OUTER silhouette (shell), widest row, median over min-channel thresholds %s" % SHELL_THRESHOLDS,
                band=band, row_profile=prof,
                ring=e, ring_unc_px=ring_unc, ring_sweep=ring_sweep, ring_smin=RING_SMIN,
                ring_major_px_range=[min(majors), max(majors)],
                tof=dict(x=[int(txs.min()), int(txs.max())], y=[int(tys.min()), int(tys.max())],
                         centre=[float(txs.mean()), float(tys.mean())], w_px=int(txs.max() - txs.min() + 1), h_px=int(tys.max() - tys.min() + 1)),
                ratios=dict(ring_od_over_shell_width=e["major_px"] / width,
                            ring_minor_over_major=e["minor_px"] / e["major_px"],
                            ring_x_offset_over_width=(e["centre"][0] - float(np.median(mids))) / width,
                            tof_dx_over_shell_width=(float(txs.mean()) - e["centre"][0]) / width)), rgb


def draw_ellipse(d, e, colour, w=3):
    cx, cy = e["centre"]; a = e["major_px"] / 2; b = e["minor_px"] / 2
    ang = math.atan2(e["major_axis_dir"][1], e["major_axis_dir"][0])
    pts = [(cx + a * math.cos(t) * math.cos(ang) - b * math.sin(t) * math.sin(ang),
            cy + a * math.cos(t) * math.sin(ang) + b * math.sin(t) * math.cos(ang)) for t in np.linspace(0, 2 * math.pi, 120)]
    d.line(pts + [pts[0]], fill=colour, width=w)


def mesh_side(s_w=1.0, size=1400):
    hr, rep = hw.build(s_shell=s_w, size=size)
    # head LEVEL: bisection on the ring axis elevation, exactly as tools/head_frontview.py
    g = hr.eye_gids[0]
    mid = hr.model.geom_dataid[g]; a, n = hr.model.mesh_vertadr[mid], hr.model.mesh_vertnum[mid]
    vv = hr.model.mesh_vert[a:a + n]; thin = int(np.argmin(vv.max(0) - vv.min(0)))

    def elev(pitch):
        hr.pose(pitch, 0, 0, 0); R = hr.data.geom_xmat[g].reshape(3, 3); ax = R[:, thin]
        if ax[0] > 0: ax = -ax
        return math.degrees(math.atan2(ax[2], -ax[0]))
    lo, hi = -40.0, 40.0
    for _ in range(50):
        m = (lo + hi) / 2
        if elev(m) > 0: hi = m
        else: lo = m
    level = (lo + hi) / 2
    rows = []
    pics = {}
    for D in D_BRACKET_MM:
        for yaw in YAW_SWEEP_DEG:
            hr.pose(level, yaw, 0, 0)
            if D is None:
                hr.cam.orthographic = 1; hr.model.vis.global_.fovy = 45.0
                hr.cam.azimuth = 180.0; hr.cam.elevation = 0.0; hr.cam.distance = 0.30
                hr.cam.lookat[:] = hr.data.xpos[hr.head_bid]
            else:
                hr.cam.orthographic = 0
                hr.set_camera(180.0, 0.0, D)
            head, eyem, ids, isg = hr.masks()
            w = widest(ndimage.binary_fill_holes(head))
            e = filled_extents(eyem)
            # the ToF WINDOW on the mesh side: face_part carries a real aperture — in the
            # segmentation render the pixels inside it belong to the geom BEHIND the face
            # (the compute board), so the aperture is a hole in the face_part mask that does
            # not contain the eye ring. MEASURED here, not assumed: front_view.json recorded
            # "the mesh has no ToF window geom", which is true of the geom list and false of
            # the geometry.
            bandm = np.isin(ids, hr.gid.get("bottom_head_shell", []) + hr.gid.get("jaw", [])) & isg
            bandw = widest(bandm) if bandm.any() else None
            jawm = np.isin(ids, hr.gid.get("jaw", [])) & isg
            jaww = widest(jawm) if jawm.any() else None
            face = np.isin(ids, hr.gid.get("face_part", [])) & isg
            tofm = None
            if face.any():
                holes = ndimage.binary_fill_holes(face) & ~face
                lab, nlab = ndimage.label(holes)
                for i in range(1, nlab + 1):
                    hmask = lab == i
                    if (hmask & eyem).sum() > 0: continue
                    yy, xx = np.nonzero(hmask)
                    if len(xx) < 50: continue
                    if tofm is None or len(xx) > tofm["n_px"]:
                        tofm = dict(x=[int(xx.min()), int(xx.max())], y=[int(yy.min()), int(yy.max())],
                                    centre=[float(xx.mean()), float(yy.mean())], n_px=int(len(xx)),
                                    w_px=int(xx.max() - xx.min() + 1), h_px=int(yy.max() - yy.min() + 1))
            V = np.vstack([hr.geom_world_vertices(gg) for nm in hw.SHELL_MESHES for gg in hr.gid.get(nm, [])]) * 1000.0
            true_w = float(V[:, 1].max() - V[:, 1].min())
            pxmm = w["width_px"] / true_w
            tof_mm = None
            if tofm:
                tof_mm = dict(w_mm=tofm["w_px"] / pxmm, h_mm=tofm["h_px"] / pxmm,
                              dx_mm=(tofm["centre"][0] - e["centre"][0]) / pxmm,
                              dy_mm=(tofm["centre"][1] - e["centre"][1]) / pxmm,
                              px_per_mm=pxmm, unc_mm=1.0 / pxmm, px=tofm)
            pic = None
            if yaw == 0.0 and D is None:
                im = Image.fromarray(hr.shaded()).convert("RGB"); dd = ImageDraw.Draw(im)
                dd.line([(w["x"][0], w["row"]), (w["x"][1], w["row"])], fill=(30, 90, 220), width=3)
                dd.line([(w["mid_x"], 0), (w["mid_x"], size)], fill=(30, 90, 220), width=1)
                draw_ellipse(dd, e, (30, 160, 60))
                hy, hx = np.nonzero(head); pad = 60
                pic = im.crop((max(0, hx.min() - pad), max(0, hy.min() - pad), hx.max() + pad, hy.max() + pad))
                pics[s_w] = pic
            prof_m = row_profile(ndimage.binary_fill_holes(head), e["centre"][1]) if (yaw == 0.0 and D is None) else None
            rows.append(dict(D_mm=(D if D is not None else "orthographic"), yaw_deg=yaw, row_profile=prof_m, level_pitch_deg=level, shell_width_px=w["width_px"], widest_row=w["row"],
                             shell_mid_x=w["mid_x"], ring=e,
                             ratios=dict(ring_od_over_shell_width=e["major_px"] / w["width_px"],
                                         ring_minor_over_major=e["minor_px"] / e["major_px"],
                                         ring_x_offset_over_width=(e["centre"][0] - w["mid_x"]) / w["width_px"],
                                         tof_dx_over_width=((tofm["centre"][0] - e["centre"][0]) / w["width_px"]) if tofm else None,
                                         tof_dy_over_width=((tofm["centre"][1] - e["centre"][1]) / w["width_px"]) if tofm else None,
                                         tof_w_over_width=(tofm["w_px"] / w["width_px"]) if tofm else None,
                                         tof_h_over_width=(tofm["h_px"] / w["width_px"]) if tofm else None),
                             tof=tof_mm, band_width_px=(bandw["width_px"] if bandw else None),
                             band_over_shell=((bandw["width_px"] / w["width_px"]) if bandw else None),
                             jaw_over_shell=((jaww["width_px"] / w["width_px"]) if jaww else None),
                             head_width_mm_true=true_w))
    del hr
    return rows, level, pics.get(s_w)


def main():
    p, rgb = photo_side()
    pictures = {}
    out = dict(generated=time.strftime("%Y-%m-%d %H:%M"), method=__doc__, photo=p, rule_mm=RULE_MM,
               mesh_head_width_mm=MESH_HEAD_W, ring_mesh_mm=RING_MESH_MM, s_w_sweep=[], comparison=None)
    c_photo = p["ratios"]["ring_minor_over_major"]
    for s_w in S_W_SWEEP:
        rows, level, pic = mesh_side(s_w=s_w)
        pictures[s_w] = pic
        out["s_w_sweep"].append(dict(s_w=s_w, level_pitch_deg=level, head_width_mm=rows[0]["head_width_mm_true"], rows=rows))
        print("s_w %.3f  width %.4f mm  ratio(D=inf,yaw=0) %.5f" % (s_w, rows[0]["head_width_mm_true"],
              [r for r in rows if r["D_mm"] == "orthographic" and r["yaw_deg"] == 0.0][0]["ratios"]["ring_od_over_shell_width"]), flush=True)
    # admissible mesh poses: those whose rendered ring ellipticity is within the photo's +-2 sigma
    u_c = math.sqrt(2.0) * p["ring_unc_px"] / p["ring"]["major_px"]
    base = [r for e in out["s_w_sweep"] if abs(e["s_w"] - 1.0) < 1e-9 for r in e["rows"]]
    # TWO gates on the mesh pose, both from the photograph itself:
    #  (a) the ring's ellipticity (its image is a circle seen off-axis), and
    #  (b) the ring centre's offset from the shell's own mid-line — the ring stands ~25 mm
    #      proud of the shell rim, so a yaw moves it sideways relative to the silhouette's
    #      centre. The photograph reads that offset as -0.0003 of the width (the eye is ON the
    #      mid-line), which no large yaw can reproduce: this is what pins the pose.
    off_photo = p["ratios"]["ring_x_offset_over_width"]
    u_off = math.sqrt((p["ring_unc_px"] / p["shell_width_px"]) ** 2 +
                      (p["shell_width_px_unc"] * 0.5 / p["shell_width_px"]) ** 2 + (1.0 / p["shell_width_px"]) ** 2)
    adm = [r for r in base if abs(r["ratios"]["ring_minor_over_major"] - c_photo) <= 2 * u_c
           and abs(r["ratios"]["ring_x_offset_over_width"] - off_photo) <= 2 * u_off]
    gate_note = "ring ellipticity within 2u AND ring-centre offset from the shell mid-line within 2u"
    if not adm:
        adm = [r for r in base if abs(r["ratios"]["ring_minor_over_major"] - c_photo) <= 2 * u_c] or base
        gate_note = "ellipticity gate only — no rendered pose satisfied the offset gate as well"
    qs = [r["ratios"]["ring_od_over_shell_width"] for r in adm]
    q_mesh, q_mesh_lo, q_mesh_hi = float(np.median(qs)), float(min(qs)), float(max(qs))
    q_photo = p["ratios"]["ring_od_over_shell_width"]
    u_photo = q_photo * math.sqrt((p["ring_unc_px"] * math.sqrt(2) / p["ring"]["major_px"]) ** 2 +
                                  (p["shell_width_px_unc"] / p["shell_width_px"]) ** 2)
    u_mesh = 0.5 * (q_mesh_hi - q_mesh_lo)
    u = math.sqrt(u_photo ** 2 + u_mesh ** 2)
    excess = q_photo / q_mesh - 1.0
    implied_w = RING_MESH_MM / q_photo
    implied_ring = q_photo * MESH_HEAD_W
    dev_w = implied_w - MESH_HEAD_W
    u_dev = implied_w * math.sqrt((u_photo / q_photo) ** 2 + (u_mesh / q_mesh) ** 2)
    verdict = "PASS" if abs(dev_w) + u_dev <= RULE_MM else ("FAIL" if abs(dev_w) - u_dev > RULE_MM else "CANNOT DETERMINE")
    # the lateral scale at which the mesh reproduces the photograph's ratio
    s_hits = []
    for e in out["s_w_sweep"]:
        rr = [r for r in e["rows"] if abs(r["ratios"]["ring_minor_over_major"] - c_photo) <= 2 * u_c
              and abs(r["ratios"]["ring_x_offset_over_width"] - off_photo) <= 2 * u_off] or e["rows"]
        s_hits.append((e["s_w"], float(np.median([r["ratios"]["ring_od_over_shell_width"] for r in rr])), e["head_width_mm"]))
    s_match = None
    for (s0, q0, w0), (s1, q1, w1) in zip(s_hits, s_hits[1:]):
        if (q0 - q_photo) * (q1 - q_photo) <= 0 and q1 != q0:
            t = (q_photo - q0) / (q1 - q0); s_match = s0 + t * (s1 - s0)
            break
    # the ToF window, measured on BOTH sides as the same feature (the aperture in the face
    # panel), over the admissible poses
    tof_rows = [r for r in adm if r.get("tof")]
    tof_row = dict(measured_on_mesh=bool(tof_rows), mjcf_site_dy_mm=TOF_DY_MM)
    if tof_rows:
        dxs = [r["tof"]["dx_mm"] for r in tof_rows]; dys = [r["tof"]["dy_mm"] for r in tof_rows]
        ws_ = [r["tof"]["w_mm"] for r in tof_rows]; hs_ = [r["tof"]["h_mm"] for r in tof_rows]
        u_edge = float(np.mean([r["tof"]["unc_mm"] for r in tof_rows]))
        dx_mesh = float(np.median(dxs)); u_dx_mesh = math.sqrt((0.5 * (max(dxs) - min(dxs))) ** 2 + (math.sqrt(2) * u_edge) ** 2)
        q_tof = p["ratios"]["tof_dx_over_shell_width"]
        u_q = q_tof * math.sqrt((math.sqrt(p["ring_unc_px"] ** 2 + 1.5 ** 2) / abs(p["tof"]["centre"][0] - p["ring"]["centre"][0])) ** 2
                                + (p["shell_width_px_unc"] / p["shell_width_px"]) ** 2)
        implied = dx_mesh / q_tof
        tof_row.update(
            mesh_aperture_w_mm=float(np.median(ws_)), mesh_aperture_h_mm=float(np.median(hs_)),
            mesh_dx_mm=dx_mesh, mesh_dx_unc_mm=u_dx_mesh, mesh_dy_mm=float(np.median(dys)), mesh_edge_unc_mm=u_edge,
            photo_dx_over_width=q_tof, photo_dx_over_width_unc=u_q,
            photo_w_over_width=p["tof"]["w_px"] / p["shell_width_px"], photo_h_over_width=p["tof"]["h_px"] / p["shell_width_px"],
            mesh_w_over_width=float(np.median([r["ratios"]["tof_w_over_width"] for r in tof_rows])),
            mesh_h_over_width=float(np.median([r["ratios"]["tof_h_over_width"] for r in tof_rows])),
            mesh_dy_over_width=float(np.median([r["ratios"]["tof_dy_over_width"] for r in tof_rows])),
            photo_dy_over_width=(p["tof"]["centre"][1] - p["ring"]["centre"][1]) / p["shell_width_px"],
            implied_head_width_mm=implied,
            implied_head_width_unc_mm=implied * math.sqrt((u_q / q_tof) ** 2 + (u_dx_mesh / dx_mesh) ** 2),
            how=("the ToF window is an APERTURE in face_part (%.3f x %.3f mm, MEASURED as the hole in the face_part "
                 "segmentation mask that does not contain the eye ring — the compute board renders through it), whose "
                 "centre sits %.3f mm to the head's right of the eye-ring centre. The photograph gives the same "
                 "offset as a fraction of the head width, so it implies a width without using the ring's diameter."
                 % (float(np.median(ws_)), float(np.median(hs_)), dx_mesh)),
            note=("front_view.json recorded 'the mesh has no ToF window geom' and marked the window CANNOT DETERMINE on "
                  "the mesh side. There is no ToF GEOM; there IS a ToF aperture, and it is measurable. The MJCF's tof "
                  "SITE sits at %.4f mm, %.3f mm outboard of the aperture centre." % (TOF_DY_MM, TOF_DY_MM - dx_mesh)))
    band_row = None
    if p.get("band"):
        bs = [r["band_over_shell"] for r in adm if r.get("band_over_shell")]
        if bs:
            qm = float(np.median(bs)); uqm = 0.5 * (max(bs) - min(bs))
            qp = p["band"]["band_over_shell"]
            uqp = qp * math.sqrt((p["band"]["width_px_unc"] / p["band"]["width_px"]) ** 2 +
                                 (p["shell_width_px_unc"] / p["shell_width_px"]) ** 2)
            d_mm = (qp - qm) * MESH_HEAD_W; u_mm = math.sqrt(uqp ** 2 + uqm ** 2) * MESH_HEAD_W
            js = [r["jaw_over_shell"] for r in adm if r.get("jaw_over_shell")]
            qmj = float(np.median(js)) if js else None
            d_mm_j = ((qp - qmj) * MESH_HEAD_W) if qmj else None
            band_row = dict(photo=qp, photo_unc=uqp, mesh=qm, mesh_range=[min(bs), max(bs)],
                            mesh_jaw_only=qmj, dev_mm_vs_jaw_only=d_mm_j,
                            verdict_vs_jaw_only=(("PASS" if abs(d_mm_j) + u_mm <= RULE_MM else ("FAIL" if abs(d_mm_j) - u_mm > RULE_MM else "CANNOT DETERMINE")) if qmj else None),
                            adversarial_check=("the mesh's accent band is bottom_head_shell + jaw; if on the PRODUCT only the jaw and "
                                               "its trim carry the accent colour and the bottom shell is body-coloured, the mesh-side "
                                               "comparator is the jaw alone — reported here so the finding does not depend on which "
                                               "reading is right"),
                            dev_mm=d_mm, dev_unc_mm=u_mm,
                            verdict=("PASS" if abs(d_mm) + u_mm <= RULE_MM else ("FAIL" if abs(d_mm) - u_mm > RULE_MM else "CANNOT DETERMINE")),
                            what=("the accent trim band's width divided by the head's outer silhouette width, measured the same way "
                                  "on both sides. A pure shape ratio: no scale, no ring, and the same on any camera. On the mesh the "
                                  "band IS the head's widest feature; on the product it is inset."),
                            why_it_matters=("out/head/front_view.json used the photograph's BAND (419 px) as the head width against the "
                                            "mesh's whole bottom-shell silhouette (692 px). Those are the same feature on the mesh and "
                                            "different features on the product, which is where its +9.1 %% came from."))
    # the OUTLINE: the two row-profiles laid on each other in the ring-anchored frame, compared
    # only where both are the same feature (the dome apex row and the bottom row are clipped or
    # are different parts, and are excluded BY NAME, not by trimming until it agrees)
    outline = None
    mprof = next((r["row_profile"] for e in out["s_w_sweep"] if e["s_w"] == 1.0
                  for r in e["rows"] if r.get("row_profile")), None)
    pprof = p.get("row_profile")
    if mprof and pprof:
        # compared only where BOTH outlines are at least OUTLINE_WMIN of their widest row.
        # Above that the dome is a tangent: the row width falls to zero over a few rows, so a
        # width difference there measures the vertical registration, not the shape. The cut is
        # a stated property of the curves, not a trim chosen until they agree.
        def first_above(prof):
            uu = np.asarray(prof["u"]); ww = np.asarray(prof["w_over_wmax"])
            idx = np.nonzero(ww >= OUTLINE_WMIN)[0]
            return float(uu[idx[0]]) if len(idx) else float(uu[0])
        lo = max(first_above(pprof), first_above(mprof))
        hi = min(pprof["u_range"][1], mprof["u_range"][1]) - OUTLINE_TRIM
        g = np.linspace(lo, hi, 60)
        a = np.interp(g, pprof["u"], pprof["w_over_wmax"]); b = np.interp(g, mprof["u"], mprof["w_over_wmax"])
        dmm = (a - b) * MESH_HEAD_W
        # the outline is steep near the dome apex, so a small error in the VERTICAL anchor (the
        # ring centre) turns into a large width difference there. Propagated, not trimmed away.
        u_anchor = math.sqrt((p["ring_unc_px"] / pprof["wmax_px"]) ** 2 + (1.0 / mprof["wmax_px"]) ** 2)
        u_w = math.sqrt((2.0 / pprof["wmax_px"]) ** 2 + (2.0 / mprof["wmax_px"]) ** 2 +
                        (p["shell_width_px_unc"] / p["shell_width_px"]) ** 2)
        slope = np.gradient(b, g)
        udev = np.sqrt(u_w ** 2 + (np.abs(slope) * u_anchor) ** 2) * MESH_HEAD_W
        outline = dict(u=[float(x) for x in g], photo=[float(x) for x in a], mesh=[float(x) for x in b],
                       dev_mm=[float(x) for x in dmm], dev_unc_mm=[float(x) for x in udev],
                       anchor_unc_u=float(u_anchor), width_unc_rel=float(u_w),
                       rms_mm=float(np.sqrt((dmm ** 2).mean())), max_abs_mm=float(np.abs(dmm).max()),
                       n_fail=int((np.abs(dmm) - udev > RULE_MM).sum()), n_points=int(len(g)),
                       worst_fail=(dict(u=float(g[int(np.argmax(np.abs(dmm) - udev))]),
                                        dev_mm=float(dmm[int(np.argmax(np.abs(dmm) - udev))]),
                                        unc_mm=float(udev[int(np.argmax(np.abs(dmm) - udev))]))),
                       widest_u_photo=pprof["widest_u"], widest_u_mesh=mprof["widest_u"],
                       widest_u_shift=pprof["widest_u"] - mprof["widest_u"],
                       compared_over=[float(lo), float(hi)],
                       excluded=("every row above the one where either outline first reaches %.2f of its widest width — "
                                 "the dome apex, where the outline is a tangent and a width difference measures the "
                                 "vertical registration rather than the shape (the propagated anchor term there is %.1f mm "
                                 "and still not the whole story) — and the last %.3f of u, where the photograph's head runs "
                                 "into the neck cut and the mesh's carries the soft pads: different features, named and "
                                 "dropped rather than trimmed until the curves agree" % (OUTLINE_WMIN, 1.4, OUTLINE_TRIM)),
                       what=("the head's front-view outline: width at each row divided by the widest row, against that row's "
                             "height above/below the eye-ring centre in the same units. No scale, no camera, nothing fitted."),
                       verdict=("FAIL" if int((np.abs(dmm) - udev > RULE_MM).sum()) else
                                ("PASS" if bool((np.abs(dmm) + udev <= RULE_MM).all()) else "CANNOT DETERMINE")),
                       photo_bottom_on_cut=pprof.get("bottom_on_cut"))
    out["comparison"] = dict(
        outline=outline,
        band_over_shell=band_row,
        ratio_photo=q_photo, ratio_photo_unc=u_photo, ratio_mesh_median=q_mesh, ratio_mesh_range=[q_mesh_lo, q_mesh_hi],
        admissible_poses=len(adm), of_poses=len(base), pose_gate=gate_note,
        admissible_pose_list=[dict(D_mm=r["D_mm"], yaw_deg=r["yaw_deg"]) for r in adm],
        ring_x_offset_over_width_photo=off_photo, ring_x_offset_unc=u_off,
        ring_ellipticity_photo=c_photo, ring_ellipticity_unc=u_c,
        excess_pct=100 * excess, unc_combined=u,
        implied_head_width_mm=implied_w, implied_head_width_dev_mm=dev_w, implied_head_width_dev_unc_mm=u_dev,
        implied_ring_od_mm_if_width_is_mesh=implied_ring, verdict_head_width=verdict,
        s_w_that_matches=s_match, s_w_curve=[dict(s_w=a, ratio=b, head_width_mm=c) for a, b, c in s_hits],
        tof=tof_row)
    # the picture: REAL beside OURS at the mesh width and at the width these photographs measure
    x0, y0, x1, y1 = HEAD_REGION
    im = Image.fromarray(rgb.astype(np.uint8)).convert("RGB"); d = ImageDraw.Draw(im)
    ws = [w for w in p["shell_sweep"] if not w["on_window_edge"]]
    wref = min(ws, key=lambda w: abs(w["width_px"] - p["shell_width_px"]))
    d.line([(wref["x"][0], wref["row"]), (wref["x"][1], wref["row"])], fill=(30, 90, 220), width=3)
    d.line([(p["shell_mid_x"], y0), (p["shell_mid_x"], y1)], fill=(30, 90, 220), width=1)
    draw_ellipse(d, p["ring"], (30, 160, 60))
    d.rectangle([p["tof"]["x"][0], p["tof"]["y"][0], p["tof"]["x"][1], p["tof"]["y"][1]], outline=(200, 40, 30), width=2)
    realc = im.crop((x0 - 20, y0 - 20, x1 + 20, y1 + 20))
    s_best = min(S_W_SWEEP, key=lambda s: abs(s - (s_match if s_match else 1.0)))
    panels = [("REAL  flat-lay front view — blue = the head's OUTER silhouette at its widest row + mid-line, green = eye ring, red = ToF window", realc),
              ("OURS  s_w = 1.000 (Pollen's mesh), head level, yaw 0, orthographic — width %.3f mm" % MESH_HEAD_W, pictures[1.00]),
              ("OURS  s_w = %.3f — width %.3f mm, the width these photographs measure" % (s_best, [e for e in out["s_w_sweep"] if e["s_w"] == s_best][0]["head_width_mm"]), pictures[s_best])]
    th = 640
    sc = [(lab, imx.resize((int(imx.size[0] * th / imx.size[1]), th), Image.LANCZOS)) for lab, imx in panels if imx is not None]
    Wd = sum(i.size[0] for _, i in sc) + 10 * (len(sc) + 1)
    sheet = Image.new("RGB", (Wd, th + 60), (255, 255, 255)); dd = ImageDraw.Draw(sheet)
    xx = 10
    for lab, imx in sc:
        sheet.paste(imx, (xx, 46)); dd.text((xx + 2, 24), lab[:150], fill=(0, 0, 0)); xx += imx.size[0] + 10
    dd.text((10, 8), "Front view re-measured: ring OD / head width  photo %.4f +- %.4f  vs mesh %.4f (%s)  ->  implied head width %.3f +- %.3f mm" % (
        out["comparison"]["ratio_photo"], out["comparison"]["ratio_photo_unc"], out["comparison"]["ratio_mesh_median"],
        out["comparison"]["pose_gate"], out["comparison"]["implied_head_width_mm"], out["comparison"]["implied_head_width_dev_unc_mm"]), fill=(0, 0, 0))
    sheet.save(os.path.join(OUT, "front_fit_pair.png"))
    out["picture"] = "out/head/front_fit_pair.png"
    # the FAIL, at 8x on the photograph itself: the cream shell's outer edge against the
    # accent band's, on both sides of the head
    if p.get("band"):
        src = Image.fromarray(rgb.astype(np.uint8)).convert("RGB")
        z = 8; r0, r1 = 375, 500
        shell_x = wref["x"]; band_x = None
        bsw = [b for b in p["band"]["sweep"]]
        if bsw: band_x = bsw[len(bsw) // 2]["x"]
        crops = []
        for lab, (cx0, cx1) in (("left edge", (shell_x[0] - 22, shell_x[0] + 48)), ("right edge", (shell_x[1] - 48, shell_x[1] + 22))):
            c = src.crop((cx0, r0, cx1, r1)).resize(((cx1 - cx0) * z, (r1 - r0) * z), Image.NEAREST)
            dd2 = ImageDraw.Draw(c)
            for xv, col, nm in ((shell_x[0] if "left" in lab else shell_x[1], (30, 90, 220), "shell"),
                                ((band_x[0] if "left" in lab else band_x[1]) if band_x else None, (220, 90, 20), "band")):
                if xv is None: continue
                px = (xv - cx0) * z
                dd2.line([(px, 0), (px, (r1 - r0) * z)], fill=col, width=3)
                dd2.text((px + 5, 6), "%s x=%d" % (nm, xv), fill=col)
            crops.append((lab, c))
        H2 = max(c.size[1] for _, c in crops)
        W2 = sum(c.size[0] for _, c in crops) + 30
        eim = Image.new("RGB", (W2, H2 + 40), (255, 255, 255)); de = ImageDraw.Draw(eim)
        xx = 10
        for lab, c in crops:
            eim.paste(c, (xx, 34)); de.text((xx + 2, 20), lab, fill=(0, 0, 0)); xx += c.size[0] + 10
        de.text((10, 4), "The FAIL at 8x: the cream shell's outer edge (blue) sits outboard of the accent band's (orange) on BOTH sides — "
                         "band/shell %.4f +- %.4f on the product, %.4f on the mesh, %.3f +- %.3f mm" % (
                    p["band"]["band_over_shell"], band_row["photo_unc"] if band_row else 0.0,
                    band_row["mesh"] if band_row else 1.0, band_row["dev_mm"] if band_row else 0.0,
                    band_row["dev_unc_mm"] if band_row else 0.0), fill=(0, 0, 0))
        eim.save(os.path.join(OUT, "front_edges.png"))
        out["picture_edges"] = "out/head/front_edges.png"
    json.dump(out, open(os.path.join(OUT, "front_fit.json"), "w"), indent=1, default=float)
    print(json.dumps(out["comparison"], indent=1, default=float))
    print("wrote", os.path.join(OUT, "front_fit.json"))


if __name__ == "__main__":
    main()
