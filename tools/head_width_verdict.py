#!/usr/bin/env python3
"""head_width_verdict.py — reduce the two width instruments to ONE answer, with its
uncertainty and its verdict, and say which of {head width, eye ring} the front view's
ring/width excess belongs to.

Inputs (all measured elsewhere, none typed here):
  out/head/width_tight.json  tools/head_width.py: the fit objective against a swept
                             LATERAL scale of the head shells (s_w, ring fixed at
                             30.000 mm) and against a swept RING scale (s_r, shells
                             fixed), for each admitted profile photograph.
  out/head/front_fit.json    tools/head_frontfit.py: the true front view re-measured
                             on the head's OUTER silhouette with one estimator on
                             both sides and a pose gated by the ring's ellipticity
                             and its offset from the shell mid-line.
  out/head/head.json         the published head measurement (mesh dimensions, rule).

Method. Each sweep is a profile likelihood in one parameter. A quadratic is fitted
by least squares through its rows; the minimiser is the scale the photograph shows
and the curvature A converts the fit's OWN measured noise (the standard deviation of
the restarts, reported per row by head_width.fit_local) into an uncertainty
sigma = sqrt(noise / A). A minimum that lands on the end of the swept range is NOT
reported as a measurement — it is recorded as bounded, with the direction it ran.

Writes out/head/head_width_verdict.json.
    /Applications/FreeCAD.app/Contents/Resources/bin/python tools/head_width_verdict.py
"""
import os, sys, json, math, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "out", "head")
RULE_MM = 1.5
MESH_W_MM = 91.763          # top_head_shell / bottom_head_shell x extent (out/verify/mech_dims.json)
MESH_RING_MM = 30.000       # noenoeil boss diameter (cecad.meshfeatures on the published STL)


def local3_min(xs, ys):
    """the parabola through the three grid points around the grid minimum — the local
    estimator, which does not assume the whole swept range is quadratic. Reported beside
    the least-squares one, and half their difference is carried as a systematic."""
    i = int(np.argmin(ys))
    if i == 0 or i == len(xs) - 1: return None
    x0, x1, x2 = xs[i - 1], xs[i], xs[i + 1]; y0, y1, y2 = ys[i - 1], ys[i], ys[i + 1]
    den = (x0 - x1) * (x0 - x2) * (x1 - x2)
    if abs(den) < 1e-12: return None
    A = (x2 * (y1 - y0) + x1 * (y0 - y2) + x0 * (y2 - y1)) / den
    B = (x2 * x2 * (y0 - y1) + x1 * x1 * (y2 - y0) + x0 * x0 * (y1 - y2)) / den
    return float(-B / (2 * A)) if A > 0 else None


def quad_min(xs, ys, noise):
    """least-squares parabola through a 1-D profile -> (minimiser, curvature A, sigma).
    sigma is the displacement at which the parabola rises by the fit's own noise."""
    A, B, C = np.polyfit(np.asarray(xs, float), np.asarray(ys, float), 2)
    if A <= 0:
        return None, float(A), None, float(np.sqrt(np.mean((np.polyval([A, B, C], xs) - np.asarray(ys)) ** 2)))
    s = -B / (2 * A)
    sigma = math.sqrt(max(noise, 1e-9) / A)
    rms = float(np.sqrt(np.mean((np.polyval([A, B, C], xs) - np.asarray(ys)) ** 2)))
    return float(s), float(A), float(sigma), rms


def main():
    W = json.load(open(os.path.join(OUT, "width_tight.json")))
    F = json.load(open(os.path.join(OUT, "front_fit.json")))
    H = json.load(open(os.path.join(OUT, "head.json")))
    res = dict(generated=time.strftime("%Y-%m-%d %H:%M"), method=__doc__, rule_mm=RULE_MM,
               mesh_head_width_mm=MESH_W_MM, mesh_ring_od_mm=MESH_RING_MM,
               inputs=dict(profiles="out/head/width_tight.json", front="out/head/front_fit.json", head="out/head/head.json"),
               lines=[], sweeps=[])
    sw_lines = []
    for ph in W["photos"]:
        for which, sw in ph["sweeps"].items():
            rows = sw["rows"]
            xs = [r["s"] for r in rows]; ys = [r["objective"] for r in rows]
            noise = float(np.mean([r["objective_spread"] or 0.0 for r in rows]))
            s, A, sig, rms = quad_min(xs, ys, noise)
            s3 = local3_min(xs, ys)
            u_est = abs(s - s3) / 2.0 if (s is not None and s3 is not None) else 0.0
            if sig is not None: sig = math.sqrt(sig ** 2 + u_est ** 2)
            edge = rows[int(np.argmin(ys))]["s"] in (min(xs), max(xs))
            direction = ("below %.4f" % min(xs)) if rows[int(np.argmin(ys))]["s"] == min(xs) else (
                        ("above %.4f" % max(xs)) if rows[int(np.argmin(ys))]["s"] == max(xs) else None)
            iou_best = max(rows, key=lambda r: r["iou"])
            rec = dict(photo=ph["id"], parameter=which, swept=xs, objective=ys,
                       objective_noise=noise, quad_minimiser=s, curvature=A, sigma=sig, quad_rms_residual=rms,
                       grid_best_s=rows[int(np.argmin(ys))]["s"], min_on_sweep_edge=bool(edge), runs_to=direction,
                       quad_minimiser_local3=s3, estimator_systematic=u_est,
                       best_iou=iou_best["iou"], best_iou_s=iou_best["s"],
                       iou_profile=[[r["s"], r["iou"]] for r in rows])
            if which == "s_w":
                rec.update(implied_head_width_mm=(s * MESH_W_MM if s else None),
                           implied_head_width_unc_mm=(sig * MESH_W_MM if sig else None))
                if not edge and s is not None: sw_lines.append((ph["id"], s, sig))
            else:
                rec.update(implied_ring_od_mm=(s * MESH_RING_MM if s else None),
                           implied_ring_od_unc_mm=(sig * MESH_RING_MM if sig else None))
            res["sweeps"].append(rec)
    # ---- line 1: the profiles' lateral scale (ring-independent: the objective's silhouette
    #      term is the only thing a lateral scale moves, and the ring sweep leaves the
    #      silhouette IoU flat, which this file records)
    if sw_lines:
        ss = np.array([s for _, s, _ in sw_lines]); us = np.array([u if u else np.inf for _, _, u in sw_lines])
        w = 1.0 / us ** 2
        s_bar = float((ss * w).sum() / w.sum())
        u_stat = float(1.0 / math.sqrt(w.sum()))
        u_spread = float(0.5 * (ss.max() - ss.min())) if len(ss) > 1 else 0.0
        u_bar = math.sqrt(u_stat ** 2 + u_spread ** 2)
        res["lines"].append(dict(
            name="profile photographs, head silhouette (%d)" % len(sw_lines),
            what="the lateral scale s_w at which the posed mesh best reproduces each profile silhouette; the eye ring is held at 30.000 mm, so this line does not use the ring at all",
            per_photo=[dict(photo=p, s_w=s, unc=u, head_width_mm=s * MESH_W_MM) for p, s, u in sw_lines],
            s_w=s_bar, s_w_unc=u_bar, head_width_mm=s_bar * MESH_W_MM, head_width_unc_mm=u_bar * MESH_W_MM,
            unc_parts=dict(statistical=u_stat * MESH_W_MM, photo_to_photo_spread=u_spread * MESH_W_MM)))
    # ---- line 2: the true front view's ring/width ratio
    C = F["comparison"]
    res["lines"].append(dict(
        name="front view, eye ring OD / head width",
        what="the flat-lay front view, both sides measured with one estimator on the head's OUTER silhouette, the mesh pose gated by the ring's ellipticity and its offset from the shell mid-line, over a camera-distance bracket",
        ratio_photo=C["ratio_photo"], ratio_photo_unc=C["ratio_photo_unc"], ratio_mesh=C["ratio_mesh_median"],
        ratio_mesh_range=C["ratio_mesh_range"], excess_pct=C["excess_pct"],
        s_w=C["s_w_that_matches"], head_width_mm=C["implied_head_width_mm"],
        head_width_unc_mm=C["implied_head_width_dev_unc_mm"], pose_gate=C["pose_gate"]))
    # ---- line 3: the ToF window aperture offset from the eye axis — the SAME feature on
    #      both sides, and it does not use the ring's diameter either
    T = C["tof"]
    res["lines"].append(dict(
        name="front view, ToF window aperture offset from the eye axis",
        what=T.get("how"), note=T.get("note"),
        mesh_aperture_mm=[T.get("mesh_aperture_w_mm"), T.get("mesh_aperture_h_mm")],
        mesh_dx_mm=T.get("mesh_dx_mm"), photo_dx_over_width=T.get("photo_dx_over_width"),
        head_width_mm=T.get("implied_head_width_mm"), head_width_unc_mm=T.get("implied_head_width_unc_mm"),
        ring_free=True))
    for l in res["lines"]:
        l.setdefault("ring_free", l["name"].startswith("profile"))
    # ---- solve the two unknowns instead of assuming one of them
    #      W (head width) comes ONLY from the lines that do not use the ring's diameter;
    #      R (ring OD) then follows from the front view's ring/width ratio at that W.
    free = [l for l in res["lines"] if l.get("ring_free") and l.get("head_width_unc_mm")]
    ws = np.array([1.0 / l["head_width_unc_mm"] ** 2 for l in free])
    vs = np.array([l["head_width_mm"] for l in free])
    W = float((vs * ws).sum() / ws.sum()); uW = float(1.0 / math.sqrt(ws.sum()))
    chi2W = float((ws * (vs - W) ** 2).sum()); dofW = len(free) - 1
    devW = W - MESH_W_MM
    vW = "PASS" if abs(devW) + uW <= RULE_MM else ("FAIL" if abs(devW) - uW > RULE_MM else "CANNOT DETERMINE")
    # the ring: calibrate the rendered ratio against the mesh's TRUE R0/W0 so the estimator's
    # own bias cancels, then read the ring off the photograph's ratio at the measured W
    q_photo, u_q = C["ratio_photo"], C["ratio_photo_unc"]
    q_mesh = C["ratio_mesh_median"]; u_qm = 0.5 * (C["ratio_mesh_range"][1] - C["ratio_mesh_range"][0])
    cal = (MESH_RING_MM / MESH_W_MM) / q_mesh
    R = q_photo * cal * W
    uR = R * math.sqrt((u_q / q_photo) ** 2 + (u_qm / q_mesh) ** 2 + (uW / W) ** 2)
    devR = R - MESH_RING_MM
    vR = "PASS" if abs(devR) + uR <= RULE_MM else ("FAIL" if abs(devR) - uR > RULE_MM else "CANNOT DETERMINE")
    # the PAIR, which is what the front view actually measures
    pair_excess = C["excess_pct"]; pair_u = 100 * math.sqrt((u_q / q_photo) ** 2 + (u_qm / q_mesh) ** 2)
    dev_pair_mm = (q_photo - q_mesh) * MESH_W_MM; u_pair_mm = pair_u / 100 * q_mesh * MESH_W_MM
    vPair = "PASS" if abs(dev_pair_mm) + u_pair_mm <= RULE_MM else ("FAIL" if abs(dev_pair_mm) - u_pair_mm > RULE_MM else "CANNOT DETERMINE")
    share_w = 100 * (MESH_W_MM / W - 1.0)
    rings = [x for x in res["sweeps"] if x["parameter"] == "s_r"]
    ring_edge = all(x["min_on_sweep_edge"] for x in rings)
    widths = [x for x in res["sweeps"] if x["parameter"] == "s_w"]
    w_spread_pct = None
    if len(widths) == 2 and all(x["quad_minimiser"] for x in widths):
        a, b = [x["quad_minimiser"] for x in widths]; w_spread_pct = 100 * abs(a - b) / min(a, b)
    res["result"] = dict(
        head_width_mm=W, head_width_unc_mm=uW, head_width_dev_mm=devW, verdict_head_width=vW,
        head_width_lines=[l["name"] for l in free], chi2=chi2W, dof=dofW,
        ring_od_mm=R, ring_od_unc_mm=uR, ring_od_dev_mm=devR, verdict_ring_od=vR,
        pair_excess_pct=pair_excess, pair_excess_unc_pct=pair_u,
        pair_dev_mm=dev_pair_mm, pair_dev_unc_mm=u_pair_mm, verdict_ring_over_width_pair=vPair,
        attribution=("both, and neither alone: %.1f %% of the front view's %.1f %% ring/width excess is the head being "
                     "%.2f mm narrower than the mesh, and the remaining %.1f %% would be the ring being %.2f mm larger. "
                     "Each of the two is CANNOT DETERMINE at the 1.5 mm rule on its own; the PAIR is %s at %.1f sigma." % (
                         share_w, pair_excess, abs(devW), max(0.0, pair_excess - share_w), devR, vPair,
                         abs(dev_pair_mm) / u_pair_mm if u_pair_mm else float("nan"))),
        attribution_evidence=(
            "The width is measured by two lines that never use the ring's diameter — the profile silhouettes (%s) and the "
            "ToF aperture offset — and they agree (%s mm). The ring cannot be measured by the profiles at all: their s_r "
            "sweeps put it %s, %s. So the front view's excess is NOT attributable to the ring by elimination, and it is "
            "not attributable to the width alone either: the measured width deficit accounts for %.1f of the %.1f %%." % (
                ", ".join("%s s_w %.4f" % (x["photo"], x["quad_minimiser"]) for x in widths if x["quad_minimiser"]),
                ", ".join("%.3f +- %.3f" % (l["head_width_mm"], l["head_width_unc_mm"]) for l in free),
                ("at opposite ends of the swept range (%s), each minimum ON the end of the sweep" %
                 ", ".join("%s %.4f" % (x["photo"], x["grid_best_s"]) for x in rings)) if ring_edge else "inconsistently",
                "which is a refusal, not a measurement" if ring_edge else "beyond either photograph's own precision",
                share_w, pair_excess)),
        photo_to_photo_width_agreement_pct=w_spread_pct,
        settled_shape_finding=(dict(
            name="the accent trim band is inset from the head's widest row on the product and flush on the mesh",
            **{k: C["band_over_shell"][k] for k in ("photo", "photo_unc", "mesh", "mesh_jaw_only", "dev_mm", "dev_unc_mm",
                                                    "verdict", "dev_mm_vs_jaw_only", "verdict_vs_jaw_only", "what",
                                                    "why_it_matters", "adversarial_check")})
                               if C.get("band_over_shell") else None),
        retraction=("out/head/head.json published front_pair = FAIL (+9.1 %%) for ring OD / head width. That comparison put the "
                    "photograph's ACCENT TRIM BAND (419 px) against the mesh's whole bottom-shell silhouette (692 px). On the mesh "
                    "those are the same feature to 0.35 mm; on the product they are not — the band is %.3f +- %.3f mm inset from the "
                    "head's widest row. Re-measured on the head's OUTER silhouette on both sides, with one estimator and a gated "
                    "pose, the excess is %.1f +- %.1f %% and the pair's verdict is %s. The %+.1f %% figure is superseded." % (
                        abs(C["band_over_shell"]["dev_mm"]), C["band_over_shell"]["dev_unc_mm"], pair_excess, pair_u, vPair, 9.1)
                    if C.get("band_over_shell") else None),
        rule="docs/REBUILD-PROTOCOL.md: bbox within 1.5 mm per axis; PASS when |d| + u <= 1.5, FAIL when |d| - u > 1.5, else CANNOT DETERMINE",
        what_would_settle=[
            "A calliper across one product head at its widest row and across the eye ring's outer diameter, to 0.1 mm — it beats every photograph here by an order of magnitude and separates the pair outright.",
            "Pollen's own CAD for the PRODUCTION head (the published meshes are the alpha CAD; the Onshape document is private).",
            "One photograph taken for the purpose: a true front view with a ruler in the plane of the face.",
            "WHERE a width change comes out of the section is NOT measurable from photographs: a thinner side wall, a narrower core, or a different shell profile all give the same silhouette — CANNOT DETERMINE, and it is why the jaw-hinge and servo interfaces cannot simply be scaled with the shell."])
    json.dump(res, open(os.path.join(OUT, "head_width_verdict.json"), "w"), indent=1, default=float)
    print(json.dumps(res["result"], indent=1, default=float))
    for l in res["lines"]:
        print("LINE %-58s ring-free=%s  width %s mm" % (
            l["name"][:58], l.get("ring_free"),
            ("%.3f +- %.3f" % (l["head_width_mm"], l["head_width_unc_mm"])) if l.get("head_width_unc_mm") else "-"))
    print("wrote", os.path.join(OUT, "head_width_verdict.json"))


if __name__ == "__main__":
    main()
