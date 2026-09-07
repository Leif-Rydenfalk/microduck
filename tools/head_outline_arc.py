#!/usr/bin/env python3
"""head_outline_arc.py — WHERE on the head's front-view outline the deviation sits,
and whether the worst ray is a feature or the instrument.

out/head/front_fit.json (tools/head_frontfit.py) compares the product's front-view
outline with Pollen's mesh row by row: RMS 1.185 mm, worst |dev| 2.326 mm, 0 rays
clearing the 1.5 mm rule -> CANNOT DETERMINE. It does not say WHERE on the outline
that sits, and it leaves three things unbracketed:

  1. The mesh's row profile is rendered at ONE pose only (orthographic, yaw 0,
     head level). Every other quantity in that file is bracketed over
     D in {400, 800, 1500, 3000, inf} x yaw in {0..13 deg}; the outline is not.
  2. The comparison is anchored on the EYE-RING CENTRE. A vertical registration
     error between the two ring centres turns straight into a width difference
     wherever the outline has slope. That term is propagated as an uncertainty but
     never FITTED, so a registration offset and a shape difference are not separated.
  3. Everything above the row where either outline first reaches 0.85 of its widest
     width is dropped by name (the dome apex, where the outline is a tangent). That
     is the top 14.2 mm of a 60.7 mm silhouette: the DOME CAP is not measured at all.

This tool measures all three.

  * the mesh's row profile is re-rendered over the SAME D x yaw bracket the rest of
    front_fit.json uses, plus a head-PITCH sweep about level, so the outline
    deviation carries a pose bracket like everything else;
  * the photo/mesh registration offset is FITTED (one parameter, a shift in u) and
    the residual reported, so "the two curves sit at different heights" and "the two
    curves are different shapes" are separated;
  * an ANCHOR-FREE dome statistic is measured on both sides with one estimator:
        A = (widest row - apex row) / widest width
    the dome's rise over its own width. It uses no ring, no scale and no camera, and
    a vertical registration error cannot touch it.

Every deviation is reported at its polar angle theta about the eye-ring centre in
the front view (aspect-preserving: both axes in units of the widest width),
theta = atan2(-u, w/2), so +90 deg is the dome apex, 0 deg the head's widest point,
and negative angles run down the flank towards the split line.

Photograph: images/store/store_microduck-inside-the-box.png (the only published true
front view). Threshold sweep [200, 205, 210, 215, 220] — 228 is REFUSED here and the
refusal is measured, not asserted: at 228 the right-hand edge below the split line
runs out to x 574 against 551-556 at every lower threshold, i.e. it swallows the soft
shadow beside the jaw; above the split line all six agree to 1 px.

    /Applications/FreeCAD.app/Contents/Resources/bin/python tools/head_outline_arc.py
Writes out/head/outline_arc.json.
"""
import os, sys, json, math, time
os.environ.setdefault("MUJOCO_GL", "glfw")
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import head_photomatch as hp
import head_width as hw
import head_frontfit as ff

REPO, OUT = hp.REPO, hp.OUT
PHOTO = ff.PHOTO
HEAD_REGION = ff.HEAD_REGION
STABLE_TH = [200, 205, 210, 215, 220]          # 228 refused, see the header
ALL_TH = ff.SHELL_THRESHOLDS
MESH_W = ff.MESH_HEAD_W                        # 91.763 mm, out/verify/mech_dims.json
D_BRACKET = [400.0, 800.0, 1500.0, 3000.0, None]
YAW_SWEEP = [0.0, 3.0, 6.0, 9.0, 11.0, 13.0]
PITCH_SWEEP = [-8.0, -4.0, 0.0, 4.0, 8.0, 12.0, 16.0, 20.0, 24.0]   # about LEVEL
RULE_MM = 1.5
# the POSE GATE is front_fit.json's own, applied there to every quantity except the outline:
# the rendered ring's ellipticity within 2u of the photograph's AND the rendered ring centre's
# offset from the shell mid-line within 2u of the photograph's. It is independent of the
# outline, so using it here is not circular. It admits yaw <= 6 deg and rejects yaw >= 9.
GATE_SRC = "out/head/front_fit.json comparison.pose_gate"


def dome_stats(p):
    """the DOME CAP — the arc front_fit.json drops entirely. Two shape numbers, both
    invariant to an independent x- and y-scale (so a head yaw, which stretches the
    front-view silhouette sideways, cannot make them on its own):
      fullness F = (silhouette area above the widest row) / (widest width x rise)
      the half-width profile sampled at fixed fractions of the rise, apex = 0."""
    rows, ws = p["rows"], p["ws"]
    wr = p["widest_row"]; top = rows[0]; rise = wr - top
    sel = rows <= wr
    F = float(ws[sel].sum()) / (p["wmax"] * rise)
    t = np.linspace(0.05, 0.95, 19)
    prof = np.interp(top + t * rise, rows, ws) / p["wmax"]
    return float(F), float(rise), prof, t


def widest_run(ws, rows):
    """the widest row, as the MIDPOINT of the run of rows within 0.5 px of the maximum —
    the same rule on both sides, because the top of this silhouette is flat over several
    rows and 'argmax' picks an arbitrary one of them."""
    wmax = float(ws.max())
    idx = np.nonzero(ws >= wmax - 0.5)[0]
    return wmax, float(rows[idx].mean()), int(len(idx))


def profile(mask):
    ys, xs = np.nonzero(mask)
    rows, ws, ls, rs = [], [], [], []
    for y in range(int(ys.min()), int(ys.max()) + 1):
        r = np.nonzero(mask[y])[0]
        if not len(r): continue
        rows.append(y); ws.append(r.max() - r.min() + 1); ls.append(r.min()); rs.append(r.max())
    rows = np.array(rows, float); ws = np.array(ws, float)
    wmax, wrow, nflat = widest_run(ws, rows)
    return dict(rows=rows, ws=ws, ls=np.array(ls, float), rs=np.array(rs, float),
                wmax=wmax, widest_row=wrow, n_flat_rows=nflat,
                top_row=float(rows[0]), bottom_row=float(rows[-1]),
                dome_rise_over_width=(wrow - rows[0]) / wmax)


def photo_masks():
    rgb = hp.load_rgb(os.path.join(REPO, PHOTO))
    x0, y0, x1, y1 = HEAD_REGION
    region = np.zeros(rgb.shape[:2], bool); region[y0:y1, x0:x1] = True
    mn = rgb.min(axis=2); chroma = rgb.max(axis=2) - mn
    out = {}
    for th in ALL_TH:
        sil = ((mn < th) | (chroma > 14)) & region
        lab, n = ndimage.label(sil); sz = ndimage.sum(sil, lab, range(1, n + 1))
        out[th] = ndimage.binary_fill_holes(lab == (1 + int(np.argmax(sz))))
    return rgb, out


def main():
    t0 = time.time()
    ff_json = json.load(open(os.path.join(REPO, "out", "head", "front_fit.json")))
    C = ff_json["comparison"]
    c_ph, u_c = C["ring_ellipticity_photo"], C["ring_ellipticity_unc"]
    o_ph, u_o = C["ring_x_offset_over_width_photo"], C["ring_x_offset_unc"]

    rgb, masks = photo_masks()
    ph = {}
    for th, m in masks.items():
        p = profile(m); F, rise, prof, tgrid = dome_stats(p)
        ph[th] = dict(wmax=p["wmax"], widest_row=p["widest_row"], top_row=p["top_row"],
                      bottom_row=p["bottom_row"], n_flat_rows=p["n_flat_rows"],
                      A=p["dome_rise_over_width"], dome_fullness=F, dome_profile=[float(x) for x in prof])
    refusal = {}
    for row in (443, 455, 466):
        refusal[row] = {th: [int(np.nonzero(masks[th][row])[0].min()), int(np.nonzero(masks[th][row])[0].max())]
                        for th in ALL_TH}
    A_ph = [ph[t]["A"] for t in STABLE_TH]; F_ph = [ph[t]["dome_fullness"] for t in STABLE_TH]
    P_ph = np.mean([ph[t]["dome_profile"] for t in STABLE_TH], 0)
    pmid = profile(masks[ALL_TH[len(ALL_TH) // 2]])
    pside, _ = ff.photo_side()
    ring_cy = pside["ring"]["centre"][1]; ring_cx = pside["ring"]["centre"][0]
    ring_unc = pside["ring_unc_px"]
    pu = (pmid["rows"] - ring_cy) / pmid["wmax"]; pw = pmid["ws"] / pmid["wmax"]

    hr, rep = hw.build(s_shell=1.0, size=1400)
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

    poses = []
    for D in D_BRACKET:
        for yaw in YAW_SWEEP:
            for dp in (PITCH_SWEEP if (yaw == 0.0 and D is None) else [0.0]):
                hr.pose(level + dp, yaw, 0, 0)
                if D is None:
                    hr.cam.orthographic = 1; hr.model.vis.global_.fovy = 45.0
                    hr.cam.azimuth = 180.0; hr.cam.elevation = 0.0; hr.cam.distance = 0.30
                    hr.cam.lookat[:] = hr.data.xpos[hr.head_bid]
                else:
                    hr.cam.orthographic = 0; hr.set_camera(180.0, 0.0, D)
                head, eyem, ids, isg = hr.masks()
                head = ndimage.binary_fill_holes(head)
                p = profile(head); ee = ff.filled_extents(eyem)
                el = ee["minor_px"] / ee["major_px"]
                xoff = (ee["centre"][0] - (p["ls"] + p["rs"])[np.argmax(p["ws"])] / 2.0) / p["wmax"]
                admit = bool(abs(el - c_ph) <= 2 * u_c and abs(xoff - o_ph) <= 2 * u_o)
                mu = (p["rows"] - ee["centre"][1]) / p["wmax"]; mw = p["ws"] / p["wmax"]
                lo_u = max(float(pu[np.nonzero(pw >= ff.OUTLINE_WMIN)[0][0]]),
                           float(mu[np.nonzero(mw >= ff.OUTLINE_WMIN)[0][0]]))
                hi_u = min(float(pu.max()), float(mu.max())) - ff.OUTLINE_TRIM
                gu = np.linspace(lo_u, hi_u, 60)
                A_ = np.interp(gu, pu, pw); B_ = np.interp(gu, mu, mw)
                dev = (A_ - B_) * MESH_W
                theta = np.degrees(np.arctan2(-gu, B_ / 2.0))
                u_anchor = math.hypot(ring_unc / pmid["wmax"], 1.0 / p["wmax"])
                u_w = math.sqrt((2.0 / pmid["wmax"]) ** 2 + (2.0 / p["wmax"]) ** 2 +
                                (pside["shell_width_px_unc"] / pside["shell_width_px"]) ** 2)
                udev = np.sqrt(u_w ** 2 + (np.abs(np.gradient(B_, gu)) * u_anchor) ** 2) * MESH_W
                best = None
                for dsh in np.arange(-0.08, 0.0801, 0.0002):
                    dd = (np.interp(gu, pu - dsh, pw) - B_) * MESH_W
                    r = float(np.sqrt((dd ** 2).mean()))
                    if best is None or r < best[0]: best = (r, float(dsh), dd)
                rms_fit, delta_u, dev_fit = best
                i = len(dev) - 1; low = None
                if dev[i] < 0:
                    while i > 0 and dev[i - 1] < 0: i -= 1
                    j = i + int(np.argmax(np.abs(dev[i:])))
                    low = dict(theta_deg=[float(theta[i]), float(theta[-1])], n=int(len(dev) - i),
                               mean_dev_mm=float(dev[i:].mean()), worst_dev_mm=float(dev[j]),
                               worst_theta_deg=float(theta[j]), worst_unc_mm=float(udev[j]),
                               mean_after_registration_mm=float(dev_fit[i:].mean()))
                F, rise, prof, tgrid = dome_stats(p)
                # the ToF aperture: a hole in the face_part mask that does not contain the ring.
                # It is the ONE feature in this frame whose vertical offset from the ring centre
                # responds to head PITCH (the ring boss stands proud of the face, so a pitch moves
                # the two apart), which is why it is measured here.
                face = np.isin(ids, hr.gid.get("face_part", [])) & isg
                tof_dy = None
                if face.any():
                    holes = ndimage.binary_fill_holes(face) & ~face
                    lab, nl = ndimage.label(holes); bestn = 0
                    for i2 in range(1, nl + 1):
                        hm = lab == i2
                        if (hm & eyem).sum() > 0: continue
                        yy, xx = np.nonzero(hm)
                        if len(xx) < 50 or len(xx) <= bestn: continue
                        bestn = len(xx); tof_dy = float((yy.mean() - ee["centre"][1]) / p["wmax"])
                k = int(np.argmax(np.abs(dev)))
                poses.append(dict(D_mm=(D if D is not None else "orthographic"), yaw_deg=yaw, dpitch_deg=dp,
                                  admitted=admit, ring_ellipticity=el, ring_x_offset_over_width=xoff,
                                  wmax_px=p["wmax"], widest_row=p["widest_row"], top_row=p["top_row"],
                                  bottom_row=p["bottom_row"], A=p["dome_rise_over_width"], dome_fullness=F,
                                  dome_profile=[float(x) for x in prof],
                                  rms_mm=float(np.sqrt((dev ** 2).mean())), max_abs_mm=float(np.abs(dev).max()),
                                  worst_theta_deg=float(theta[k]),
                                  n_rays_clearing_rule=int((np.abs(dev) - udev > RULE_MM).sum()),
                                  registration_delta_mm=delta_u * MESH_W, rms_after_registration_mm=rms_fit,
                                  tof_dy_over_width=tof_dy, ring_od_over_width=ee["major_px"] / p["wmax"],
                                  lower_lobe=low,
                                  compared_theta_deg=[float(theta[0]), float(theta[-1])]))
    adm = [r for r in poses if r["admitted"]]

    def band(vals):
        return dict(mean=float(np.mean(vals)), min=float(min(vals)), max=float(max(vals)),
                    half_spread=float(0.5 * (max(vals) - min(vals))))

    def verdict(dmm, umm):
        return "FAIL" if abs(dmm) - umm > RULE_MM else ("PASS" if abs(dmm) + umm <= RULE_MM else "CANNOT DETERMINE")

    F_m = [r["dome_fullness"] for r in adm]
    dF = (float(np.mean(F_ph)) - float(np.mean(F_m)))
    uF = math.hypot(0.5 * (max(F_ph) - min(F_ph)), 0.5 * (max(F_m) - min(F_m)))
    P_m = np.array([r["dome_profile"] for r in adm])
    dome_curve = []
    tgrid = np.linspace(0.05, 0.95, 19)
    for i in range(len(tgrid)):
        d_ = (P_ph[i] - P_m[:, i].mean()) * MESH_W
        u_ = math.hypot(P_m[:, i].std(), 2.0 / pmid["wmax"]) * MESH_W
        dome_curve.append(dict(t_apex_to_widest=float(tgrid[i]), photo=float(P_ph[i]),
                               mesh_mean=float(P_m[:, i].mean()), pose_sd_mm=float(P_m[:, i].std() * MESH_W),
                               dev_mm=float(d_), unc_mm=float(u_), verdict=verdict(d_, u_)))
    lows = [r["lower_lobe"] for r in adm if r["lower_lobe"]]
    lo_mean = band([l["mean_dev_mm"] for l in lows]); lo_worst = band([l["worst_dev_mm"] for l in lows])
    lo_th0 = band([l["theta_deg"][0] for l in lows]); lo_th1 = band([l["theta_deg"][1] for l in lows])
    d_lobe = lo_mean["mean"]; u_lobe = math.hypot(lo_mean["half_spread"], float(np.mean([l["worst_unc_mm"] for l in lows])))
    d_worst = lo_worst["mean"]; u_worst = math.hypot(lo_worst["half_spread"], float(np.mean([l["worst_unc_mm"] for l in lows])))
    res = dict(
        generated=time.strftime("%Y-%m-%d %H:%M"), method=__doc__, rule_mm=RULE_MM,
        pose_gate=dict(source=GATE_SRC, gate=C["pose_gate"], n_admitted=len(adm), n_poses=len(poses),
                       ring_ellipticity_photo=[c_ph, u_c], ring_x_offset_photo=[o_ph, u_o],
                       admitted=[dict(D_mm=r["D_mm"], yaw_deg=r["yaw_deg"], dpitch_deg=r["dpitch_deg"]) for r in adm]),
        photo=dict(image=PHOTO, thresholds_used=STABLE_TH, thresholds_refused=[228],
                   refusal_evidence=dict(what="left/right edge x per threshold at three rows below the split line",
                                         rows=refusal,
                                         reading=("at 228 the RIGHT edge runs to 566-574 px against 551-556 at every "
                                                  "lower threshold, i.e. it swallows the soft shadow beside the jaw; "
                                                  "the LEFT edge is 134-136 at every threshold and above the split "
                                                  "line all six agree to 1 px. 228 also moves the apex row 214 -> 195 "
                                                  "and the widest row 411 -> 467, so it is refused for the dome too")),
                   per_threshold=ph, ring_centre=[ring_cx, ring_cy], ring_unc_px=ring_unc),
        poses=poses,
        published=dict(source="out/head/front_fit.json comparison.outline",
                       rms_mm=C["outline"]["rms_mm"], max_abs_mm=C["outline"]["max_abs_mm"],
                       n_fail=C["outline"]["n_fail"], verdict=C["outline"]["verdict"],
                       mesh_pose="orthographic, yaw 0, head level — ONE pose, unbracketed"),
        pose_sensitivity=dict(
            what=("the SAME outline comparison recomputed with the mesh at every pose front_fit.json's own gate "
                  "admits. The published numbers are one pose out of this set."),
            rms_mm=band([r["rms_mm"] for r in adm]), max_abs_mm=band([r["max_abs_mm"] for r in adm]),
            n_rays_clearing_rule=[min(r["n_rays_clearing_rule"] for r in adm), max(r["n_rays_clearing_rule"] for r in adm)],
            reading=("the headline statistics are NOT pose-robust: over the admitted poses the RMS runs %.2f-%.2f mm, "
                     "the worst ray %.2f-%.2f mm and the count of rays clearing the 1.5 mm rule %d-%d. The published "
                     "'0 rays failing' is a property of the single pose that was rendered." % (
                         min(r["rms_mm"] for r in adm), max(r["rms_mm"] for r in adm),
                         min(r["max_abs_mm"] for r in adm), max(r["max_abs_mm"] for r in adm),
                         min(r["n_rays_clearing_rule"] for r in adm), max(r["n_rays_clearing_rule"] for r in adm)))),
        lower_lobe=dict(
            what=("the one part of the outline that IS pose-robust: over every admitted pose the product's silhouette "
                  "is NARROWER than the mesh's on the arc below the widest row. Sign never changes."),
            arc_theta_deg=[lo_th0["mean"], lo_th1["mean"]], arc_theta_range=[lo_th0["min"], lo_th1["max"]],
            n_poses=len(lows), mean_dev_mm=d_lobe, mean_dev_unc_mm=u_lobe, mean_verdict=verdict(d_lobe, u_lobe),
            worst_dev_mm=d_worst, worst_dev_unc_mm=u_worst, worst_verdict=verdict(d_worst, u_worst),
            per_pose_mean=lo_mean, per_pose_worst=lo_worst,
            mean_after_registration_mm=float(np.mean([l["mean_after_registration_mm"] for l in lows])),
            what_it_is=("the same physical feature head.json already grades FAIL: below the split line the product's "
                        "accent trim band is inset from the top shell's rim, and on the mesh it is flush "
                        "(band/shell 0.9666 +- 0.0090 product vs 1.0000 mesh). This is that feature seen a second "
                        "way, on the silhouette rather than on the band's own chroma mask.")),
        registration=dict(
            what=("ONE free parameter: the photograph's row profile slid vertically against the mesh's, in u. It "
                  "absorbs a difference in where the eye ring sits relative to the shell (or a residual head pitch); "
                  "what survives it is shape."),
            delta_mm=band([r["registration_delta_mm"] for r in adm]),
            rms_before_mm=band([r["rms_mm"] for r in adm]), rms_after_mm=band([r["rms_after_registration_mm"] for r in adm]),
            reading=("a single vertical shift of %.2f mm removes most of the outline residual (RMS %.3f -> %.3f mm at "
                     "the published pose). The UPPER arc is entirely absorbed by it; the LOWER arc is not." % (
                         [r["registration_delta_mm"] for r in adm if r["D_mm"] == "orthographic" and r["yaw_deg"] == 0.0 and r["dpitch_deg"] == 0.0][0],
                         [r["rms_mm"] for r in adm if r["D_mm"] == "orthographic" and r["yaw_deg"] == 0.0 and r["dpitch_deg"] == 0.0][0],
                         [r["rms_after_registration_mm"] for r in adm if r["D_mm"] == "orthographic" and r["yaw_deg"] == 0.0 and r["dpitch_deg"] == 0.0][0]))),
        dome_cap=dict(
            what=("the arc front_fit.json excludes by name: everything above the row where either outline first "
                  "reaches 0.85 of its widest width. That is the top 14.2 mm of a 60.7 mm silhouette. Measured here "
                  "with two statistics that a lateral stretch cannot make."),
            fullness=dict(photo=float(np.mean(F_ph)), photo_range=[min(F_ph), max(F_ph)],
                          mesh=float(np.mean(F_m)), mesh_range=[min(F_m), max(F_m)],
                          dev=dF, dev_unc=uF,
                          as_half_width_mm=dF * MESH_W / 2.0, as_half_width_unc_mm=uF * MESH_W / 2.0,
                          verdict=verdict(dF * MESH_W / 2.0, uF * MESH_W / 2.0)),
            rise_over_width=dict(photo=float(np.mean(A_ph)), mesh=float(np.mean([r["A"] for r in adm])),
                                 mesh_range=[min(r["A"] for r in adm), max(r["A"] for r in adm)],
                                 dev_mm=(float(np.mean(A_ph)) - float(np.mean([r["A"] for r in adm]))) * MESH_W,
                                 dev_unc_mm=math.hypot(0.5 * (max(A_ph) - min(A_ph)),
                                                       0.5 * (max(r["A"] for r in adm) - min(r["A"] for r in adm))) * MESH_W,
                                 verdict=verdict((float(np.mean(A_ph)) - float(np.mean([r["A"] for r in adm]))) * MESH_W,
                                                 math.hypot(0.5 * (max(A_ph) - min(A_ph)),
                                                            0.5 * (max(r["A"] for r in adm) - min(r["A"] for r in adm))) * MESH_W)),
            profile=dome_curve),
        head_pitch=dict(
            what=("the head's PITCH in this flat-lay is measured NOWHERE in the repository, and it is the term "
                  "that moves every outline statistic. front_fit.json's pose gate cannot see it: over pitch -8 to "
                  "+24 deg the rendered ring's ellipticity stays %.4f-%.4f (the photograph's is %.4f +- %.4f) and "
                  "its offset from the shell mid-line stays flat, because the eye ring is a thick boss and not a "
                  "flat disc. The one feature in this frame that DOES respond is the ToF aperture's vertical "
                  "offset from the ring centre." % (
                      min(r["ring_ellipticity"] for r in poses if r["yaw_deg"] == 0.0 and r["D_mm"] == "orthographic"),
                      max(r["ring_ellipticity"] for r in poses if r["yaw_deg"] == 0.0 and r["D_mm"] == "orthographic"),
                      c_ph, u_c)),
            photo_tof_dy_over_width=C["tof"]["photo_dy_over_width"],
            photo_tof_dy_unc_over_width=1.0 / pmid["wmax"],
            mesh_by_pitch=[dict(dpitch_deg=r["dpitch_deg"], tof_dy_over_width=r["tof_dy_over_width"],
                                ring_od_over_width=r["ring_od_over_width"], rms_mm=r["rms_mm"],
                                max_abs_mm=r["max_abs_mm"], n_rays_clearing_rule=r["n_rays_clearing_rule"],
                                dome_fullness=r["dome_fullness"], A=r["A"])
                           for r in poses if r["D_mm"] == "orthographic" and r["yaw_deg"] == 0.0],
            caveat=("this does NOT prove the head is pitched. A ToF aperture modelled ~2 mm from where the product "
                    "puts it gives the same reading. The two are degenerate in one photograph, which is exactly why "
                    "the outline cannot carry a verdict.")),
        seconds=round(time.time() - t0, 1))
    os.makedirs(os.path.join(REPO, "out", "head"), exist_ok=True)
    with open(os.path.join(REPO, "out", "head", "outline_arc.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k not in ("method", "poses", "photo")}, indent=1)[:9000])


if __name__ == "__main__":
    main()
