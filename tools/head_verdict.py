#!/usr/bin/env python3
"""head_verdict.py — merge the head measurements into ONE data file with the
verdict, out/head/head.json, which tools/gen_head.py and tools/gen_comparison.py
both render (so HEAD-RECONSTRUCTION.html and COMPARISON.html §5 cannot disagree).

Inputs
  out/head/head_fit.json         tools/head_photomatch.py — per-photo scale, pose fit, size
  out/head/head_fit_D*.json      the same at other camera distances (sensitivity runs)
  out/head/front_view.json       tools/head_frontview.py — face layout, true front view, per-row verdicts
  out/head/profile_frame.json    tools/head_profile_frame.py — the README pure-profile frame

The rule (docs/REBUILD-PROTOCOL.md §3, never loosened): a rebuilt part PASSES
when its bounding box is within 1.5 mm per axis of the reference and the p95
surface distance is <= 1.0 mm. Here the "reference" is the PRODUCT, measured
from photographs, and the candidate is Pollen's simulation mesh. A photograph
gives a deviation d with an uncertainty u, so the verdict is decided the only
honest way:
    PASS               |d| + u <= 1.5 mm     (inside the rule even at the edge of the uncertainty)
    FAIL               |d| - u >  1.5 mm     (outside the rule even at the edge of the uncertainty)
    CANNOT DETERMINE   otherwise             (the measurement cannot discriminate at the rule's level)

A photograph's SCALE is admitted only when every test on it was RUN and none
failed: (a) the render-mask-vs-analytic cross-check of the servo (measured for
every servo in a frame wide enough to hold it — a servo without that read is
CANNOT DETERMINE, never PASS); (b) when two servos were read, their size ratios
agree within 3 sigma; (c) no fitted pose parameter sits on its search bound.
The per-photo deviations are combined inverse-variance weighted; the spread
between photos is also reported and, if larger than the combined u, replaces it.

    /Applications/FreeCAD.app/Contents/Resources/bin/python tools/head_verdict.py
"""
import os, sys, json, math, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "out", "head")
RULE_MM = 1.5
RULE_SRC = "docs/REBUILD-PROTOCOL.md §3: PASS = p95 <= 1.0 mm both ways AND bbox within 1.5 mm per axis AND 0 unmatched reference features"
XC_PCT = 5.0        # render mask vs analytic width must agree within this
HEAD_LEN_MM = 122.690


def REMODEL(pair, combined):
    """What a FAIL actually asks for here, said in full rather than as 're-model the head'."""
    band = combined.get("band_over_shell") or {}
    hw = combined.get("head_width") or {}
    ro = combined.get("ring_od") or {}
    out = []
    if band.get("verdict") == "FAIL":
        out.append("What FAILS is one feature, and it is the only one the photographs resolve at the rule: the accent trim band at the "
                   "split line is %.3f +- %.3f mm narrower than the head's widest row on the product and flush with it on the mesh. "
                   "Modelling that means the top shell's lower rim overhangs the band by about %.2f mm per side — an EXTERNAL feature, "
                   "so it is modelled, not guessed." % (abs(band["dev_mm"]), band["dev_unc_mm"], abs(band["dev_mm"]) / 2.0))
    if hw:
        out.append("What does NOT justify a re-model: the head's overall WIDTH (%.3f \u00b1 %.3f mm against 91.763, %s) and the eye ring's OD "
                   "(%.3f \u00b1 %.3f mm against 30.000, %s). Both point the same way as the front view's ratio and neither clears the 1.5 mm "
                   "rule, so scaling the shells to either number would be a plausible default written into tooling — refused." % (
                       hw["value_mm"], hw["unc_mm"], hw["verdict"], ro.get("value_mm", float("nan")), ro.get("unc_mm", float("nan")),
                       ro.get("verdict", "CANNOT DETERMINE")))
    out.append("What a lateral scale would break, MEASURED: part:microduck-jaw's hinge interfaces sit at x +42.068 (mouth_horn, the servo "
               "horn face) and x -39.700 (bearing_journal) in the mesh frame; the XL330 that drives them does not scale, so a 3 % lateral "
               "scale of the shells moves the horn face 1.26 mm off the servo. Where a width change comes out of the section is CANNOT "
               "DETERMINE from photographs (a thinner side wall, a narrower core and a different shell profile all give the same "
               "silhouette), so the shells stay Pollen's geometry until a calliper says otherwise.")
    return " ".join(out)


def load_opt(name):
    q = os.path.join(OUT, name)
    return json.load(open(q)) if os.path.exists(q) else None


def grade(d, u):
    if d is None or u is None: return "CANNOT DETERMINE"
    if abs(d) + u <= RULE_MM: return "PASS"
    if abs(d) - u > RULE_MM: return "FAIL"
    return "CANNOT DETERMINE"


def combine(vals):
    """inverse-variance weighted mean of (value, unc) pairs -> (mean, unc, spread)"""
    vals = [(v, u) for v, u in vals if v is not None and u]
    if not vals: return None, None, None
    w = np.array([1 / u ** 2 for _, u in vals]); x = np.array([v for v, _ in vals])
    m = float((w * x).sum() / w.sum()); u = float(1 / math.sqrt(w.sum()))
    spread = float(np.sqrt(((x - m) ** 2 * w).sum() / w.sum())) if len(vals) > 1 else 0.0
    return m, max(u, spread), spread


def fmt(x, nd=2, sign=True):
    return ("%+." + str(nd) + "f") % x if sign else ("%." + str(nd) + "f") % x


def main():
    fit = json.load(open(os.path.join(OUT, "head_fit.json")))
    front = json.load(open(os.path.join(OUT, "front_view.json")))
    pf_path = os.path.join(OUT, "profile_frame.json")
    profile_frame = json.load(open(pf_path)) if os.path.exists(pf_path) else None
    # camera-distance sensitivity runs (tools/head_photomatch.py --D <mm> --tag _D<mm> --only a,b): same photos, other distances
    sens = []
    for fn in sorted(os.listdir(OUT)):
        if fn.startswith("head_fit_") and "_D" in fn and fn.endswith(".json"):
            j = json.load(open(os.path.join(OUT, fn)))
            for p in j["photos"]:
                if p.get("size"):
                    sens.append(dict(file="out/head/" + fn, photo=p["id"], D_mm=p["fit"]["cam_distance_mm"], iou=p["fit"]["iou"],
                                     product_over_mesh=p["size"]["product_over_mesh"], unc=p["size"]["unc"],
                                     head_length_dev_mm=p["size"]["head_length_dev_mm"], yaw=p["fit"]["head_yaw_deg"], roll=p["fit"]["head_roll_deg"],
                                     k=p["fit"]["k_photo_px_per_render_px"], at_bound=[b["param"] for b in p["fit"].get("at_bound", [])]))
    photos = []
    for p in fit["photos"]:
        s = dict(p.get("size", {}))
        row = dict(id=p["id"], title=p["title"], path=p["path"], colourway=p["colourway"], note=p["note"],
                   image_size_px=p["image_size_px"], scale=p["scale"], fit=p["fit"], eye=p["eye"], size=s, inputs=p["inputs"],
                   pictures=dict(pair="out/head/%s_pair.png" % p["id"], measure="out/head/%s_measure.png" % p["id"],
                                 overlay="out/head/%s_overlay.png" % p["id"], ours="out/head/%s_ours.png" % p["id"],
                                 real="out/head/%s_real.png" % p["id"], render_servo="out/head/%s_render_servo.png" % p["id"],
                                 render_servo_wide=next((x["crosscheck"]["picture"] for x in p["scale"]["servos"] if x.get("crosscheck", {}).get("picture")), None)))
        # ---- the scale tests, each RUN and each with its own verdict; the scale is admitted only if none failed and none was skipped
        tests = []; reasons = []
        svs = [x for x in p["scale"]["servos"] if x.get("size_ratio")]
        for x in svs:
            xc = x.get("crosscheck") or {}
            if "mask_vs_analytic_pct" in xc:
                pct = xc["mask_vs_analytic_pct"]; ok = abs(pct) <= XC_PCT
                tests.append(dict(test="render mask vs analytic width (%s)" % x["what"], verdict="PASS" if ok else "FAIL",
                                  value="%+.2f %% (mask %.1f px, analytic %.1f px, %.0f %% of the projected box visible, frame ±%.0f mm at %d px)" % (
                                      pct, xc["mask"]["width_px"], xc["analytic_px"], 100 * (xc.get("mask_fill_of_projected_bbox") or 0), xc["frame_half_mm"], xc["frame_px"])))
                if not ok:
                    reasons.append("%s: the render's mask read of the servo is %.1f %% off its projected width, so what the render shows at this azimuth is not the clean case face the photo scan assumes" % (x["what"], pct))
            else:
                tests.append(dict(test="render mask vs analytic width (%s)" % x["what"], verdict="CANNOT DETERMINE", value=xc.get("why", "no cross-check read")))
                reasons.append("%s: the render-mask cross-check was not read (%s) — an unrun test is not a PASS" % (x["what"], xc.get("why", "no cross-check")))
            if x.get("render_face_note"):
                tests.append(dict(test="face the model's servo presents (%s)" % x["what"], verdict="NOTE", value=x["render_face_note"]))
        if len(svs) >= 2:
            a, b = svs[0]["size_ratio"], svs[1]["size_ratio"]
            gap = abs(a["product_over_mesh"] - b["product_over_mesh"]); sig = math.sqrt(a["unc"] ** 2 + b["unc"] ** 2)
            ok = gap <= 3 * sig
            tests.append(dict(test="two servos agree", verdict="PASS" if ok else "FAIL", value="%.4f vs %.4f, %.1f sigma apart" % (a["product_over_mesh"], b["product_over_mesh"], gap / sig)))
            if not ok:
                reasons.append("the two servos read in this photo give size ratios %.4f and %.4f — %.1f sigma apart (their dark runs are not the same face)" % (a["product_over_mesh"], b["product_over_mesh"], gap / sig))
        elif svs:
            tests.append(dict(test="two servos agree", verdict="CANNOT DETERMINE", value="one servo readable in this photograph — nothing to compare; the cross-check above is the only test of its scale"))
        ab = p["fit"].get("at_bound", [])
        if ab:
            tests.append(dict(test="no fitted parameter on its search bound", verdict="FAIL",
                              value="; ".join("%s = %.3f on [%.2f, %.2f]" % (b_["param"], b_["value"], b_["bounds"][0], b_["bounds"][1]) for b_ in ab)))
            reasons.append("the pose fit is pinned on its search box (%s): the optimum lies outside the box, so k and r are a constrained solution" % ", ".join(b_["param"] for b_ in ab))
        else:
            tests.append(dict(test="no fitted parameter on its search bound", verdict="PASS", value="all %d free parameters inside their boxes" % len([n for n in p["fit"].get("bounds", {})])))
        if "head_roll_within_joint_range" in p["fit"] and not p["fit"]["head_roll_within_joint_range"]:
            tests.append(dict(test="fitted head roll vs the MJCF joint range", verdict="NOTE",
                              value="roll %.2f deg exceeds the head_roll joint's ±%.0f deg (sim/microduck_ours.xml:215): the photographed pose includes a camera roll or a hand-posed unit; a geometric fit parameter, not a joint command" % (
                                  p["fit"]["head_roll_deg"], p["fit"]["head_roll_joint_range_deg"])))
        row["scale_tests"] = tests
        row["scale_verdict"] = "CANNOT DETERMINE" if reasons else "PASS"
        row["scale_why"] = "; ".join(reasons) if reasons else "every scale test ran and passed: " + "; ".join("%s %s" % (t["test"], t["value"]) for t in tests if t["verdict"] == "PASS")
        # ---- camera-distance sensitivity of THIS photo: half-range of r over its runs, added in quadrature to its own u
        mine = [x for x in sens if x["photo"] == p["id"] and not x["at_bound"]]
        if s and mine:
            rs = [x["product_over_mesh"] for x in mine] + [s["product_over_mesh"]]
            dD = 0.5 * (max(rs) - min(rs))
            s["D_sensitivity_half_range"] = dD; s["D_runs"] = [(x["D_mm"], x["product_over_mesh"]) for x in mine] + [(p["fit"]["cam_distance_mm"], s["product_over_mesh"])]
            s["unc_fit_only"] = s["unc"]; s["unc"] = math.sqrt(s["unc"] ** 2 + dD ** 2)
            s["head_length_dev_unc_mm"] = HEAD_LEN_MM * s["unc"]
            s["dev_major_unc_mm"] = math.sqrt(s["dev_major_unc_mm"] ** 2 + (s["mesh_head_extent_major_mm"] * dD) ** 2)
            s["dev_minor_unc_mm"] = math.sqrt(s["dev_minor_unc_mm"] ** 2 + (s["mesh_head_extent_minor_mm"] * dD) ** 2)
            s["D_note"] = "camera distance is CANNOT DETERMINE from the store frame; the half-range of r over this photo's runs at D = %s mm (%.4f) is added in quadrature" % (
                ", ".join("%.0f" % d for d, _ in s["D_runs"]), dD)
        elif s:
            s["D_note"] = "no sensitivity run at another camera distance for this photo (or its runs sat on a bound): the D term is not in its uncertainty"
        row["size"] = s
        if s and not reasons:
            row["verdicts"] = dict(length=grade(s["head_length_dev_mm"], s["head_length_dev_unc_mm"]),
                                   major=grade(s["dev_major_mm"], s["dev_major_unc_mm"]),
                                   minor=grade(s["dev_minor_mm"], s["dev_minor_unc_mm"]))
        elif s:
            row["size_excluded"] = s; row["size"] = {}
            row["verdicts"] = dict(length="CANNOT DETERMINE", major="CANNOT DETERMINE", minor="CANNOT DETERMINE")
        # ---- eye ring, scale-free (ring / head extent, photo vs render at the fitted pose)
        e = p["eye"]; t = p["fit"]
        if "major_px" in e and t.get("render_eye") and t.get("render_head_pca") and t.get("photo_head_pca"):
            q = (e["major_px"] / t["photo_head_pca"]["major_px"]) / (t["render_eye"]["major_px"] / t["render_head_pca"]["major_px"])
            e["ring_over_head_photo"] = e["major_px"] / t["photo_head_pca"]["major_px"]
            e["ring_over_head_render"] = t["render_eye"]["major_px"] / t["render_head_pca"]["major_px"]
            e["ring_over_head_ratio"] = q
            e["dev_scale_free_mm"] = 30.0 * (q - 1)
            e["dev_scale_free_unc_mm"] = 30.0 * q * math.sqrt((2.0 / e["major_px"]) ** 2 + (1.0 / t["render_eye"]["major_px"]) ** 2
                                                              + (2.0 / t["photo_head_pca"]["major_px"]) ** 2 + (2.0 / t["render_head_pca"]["major_px"]) ** 2)
            e["dev_scale_free_how"] = "30.000 mm * ((photo ring major / photo head major) / (render ring major / render head major) - 1): the ring at the head's own scale (the head's major axis, its LENGTH in these yawed profiles)"
            ar_p = e["minor_px"] / e["major_px"]; ar_r = t["render_eye"]["minor_px"] / t["render_eye"]["major_px"]
            e["axis_ratio_photo"] = ar_p; e["axis_ratio_render"] = ar_r
            if abs(ar_p - ar_r) > 0.10:
                e["ring_read_verdict"] = "CANNOT DETERMINE"
                e["ring_read_why"] = "ring axis ratio photo %.3f vs render %.3f: the render's ring is partly hidden at this pose, the two extents are not the same feature" % (ar_p, ar_r)
                row["verdicts_eye"] = "CANNOT DETERMINE"
            else:
                e["ring_read_verdict"] = "PASS"; e["ring_read_why"] = "ring axis ratio photo %.3f vs render %.3f agree" % (ar_p, ar_r)
                row["verdicts_eye"] = grade(e["dev_scale_free_mm"], e["dev_scale_free_unc_mm"])
        elif "dev_mm" in e:
            row["verdicts_eye"] = "CANNOT DETERMINE"
        photos.append(row)
    # ---- combined
    used = [p for p in photos if p.get("size")]
    L = combine([(p["size"]["head_length_dev_mm"], p["size"]["head_length_dev_unc_mm"]) for p in used])
    if L[2] is not None and L[2] > max([p["size"]["head_length_dev_unc_mm"] for p in used] + [0]):
        for p in used:
            p["verdicts"] = dict(length="CANNOT DETERMINE", major="CANNOT DETERMINE", minor="CANNOT DETERMINE")
            p["verdict_why"] = ("the photographs disagree by %.2f mm rms, more than this photo's own ±%.2f mm — a systematic error "
                                "the per-photo uncertainty does not contain; only the combined row grades" % (L[2], p["size"]["head_length_dev_unc_mm"]))
    MA = combine([(p["size"]["dev_major_mm"], p["size"]["dev_major_unc_mm"]) for p in used])
    MI = combine([(p["size"]["dev_minor_mm"], p["size"]["dev_minor_unc_mm"]) for p in used])
    R = combine([(p["size"]["product_over_mesh"], p["size"]["unc"]) for p in used])
    EY = combine([(p["eye"]["dev_scale_free_mm"], p["eye"]["dev_scale_free_unc_mm"]) for p in photos if p["eye"].get("ring_read_verdict") == "PASS"])
    EYS = combine([(p["eye"]["dev_mm"], p["eye"]["diameter_unc_mm"]) for p in photos if "dev_mm" in p["eye"] and p.get("size")])
    EYR = combine([(p["eye"]["diameter_via_render_mm"] - 30.0, p["eye"]["diameter_unc_mm"]) for p in photos if "diameter_via_render_mm" in p["eye"] and p.get("size")])
    fv = front["comparison"]; fe = fv["eye_od_over_width"]
    combined = dict(n_photos=len(used), photos_used=[p["id"] for p in used], photos_excluded=[dict(id=p["id"], why=p["scale_why"]) for p in photos if not p.get("size")],
                    product_over_mesh=R[0], product_over_mesh_unc=R[1],
                    head_length_dev_mm=L[0], head_length_dev_unc_mm=L[1], head_length_spread_mm=L[2],
                    dev_major_mm=MA[0], dev_major_unc_mm=MA[1], dev_minor_mm=MI[0], dev_minor_unc_mm=MI[1],
                    eye_dev_mm=EY[0], eye_dev_unc_mm=EY[1], eye_dev_how="scale-free ring/head-length ratio, profiles (see photos[].eye.dev_scale_free_how)",
                    eye_dev_via_servo_mm=EYS[0], eye_dev_via_servo_unc_mm=EYS[1], eye_dev_via_render_mm=EYR[0], eye_dev_via_render_unc_mm=EYR[1],
                    eye_front_view_dev_mm=fe["dev_mm"], eye_front_view_unc_mm=fe["dev_unc_mm"], eye_front_view_dev_range_mm=fe.get("dev_mm_range"),
                    eye_front_view_how="true front view: ring OD / beak width, photo vs mesh, propagated u (out/head/front_view.json), perspective bracketed over D",
                    D_sensitivity_note="per photo: the half-range of r over that photo's runs at other camera distances is in its own uncertainty (photos[].size.D_note); the combined row inherits it",
                    verdicts=dict(length=grade(L[0], L[1]), major=grade(MA[0], MA[1]), minor=grade(MI[0], MI[1]),
                                  eye_profile=grade(EY[0], EY[1]), eye_front=fe["verdict"]))
    v = combined["verdicts"]
    # the front-view ring/width FAIL is a verdict on the PAIR (ring OD, head width): the photograph cannot say which member is off.
    # The profiles' scale-free ring / head-LENGTH ratio agrees with the mesh, so the best-supported reading is the width; a calliper settles it.
    FF = load_opt("front_fit.json")          # tools/head_frontfit.py — the front view RE-MEASURED
    RW = load_opt("head_width_verdict.json")  # tools/head_width_verdict.py — the two unknowns solved
    superseded = dict(
        verdict=fe["verdict"], dev_mm=fe["dev_mm"], unc_mm=fe["dev_unc_mm"], ratio_photo=fe["photo"],
        ratio_mesh=fe["mesh"], excess_pct=fe["diff_pct"],
        why_superseded=((RW["result"]["retraction"] if RW and RW["result"].get("retraction") else
                         "superseded by out/head/front_fit.json") if (FF and RW) else None))
    if FF and RW:
        r = RW["result"]; C2 = FF["comparison"]
        pair = dict(verdict=r["verdict_ring_over_width_pair"], dev_mm=r["pair_dev_mm"], unc_mm=r["pair_dev_unc_mm"],
                    dev_range_mm=[C2["ratio_mesh_range"][0] * front["mesh_head_width_mm"] - C2["ratio_mesh_median"] * front["mesh_head_width_mm"] + r["pair_dev_mm"],
                                  C2["ratio_mesh_range"][1] * front["mesh_head_width_mm"] - C2["ratio_mesh_median"] * front["mesh_head_width_mm"] + r["pair_dev_mm"]],
                    ratio_photo=C2["ratio_photo"], ratio_mesh=C2["ratio_mesh_median"], excess_pct=r["pair_excess_pct"],
                    excess_unc_pct=r["pair_excess_unc_pct"],
                    implied_ring_od_mm_if_width_is_mesh=C2["ratio_photo"] * front["mesh_head_width_mm"] * ((30.0 / front["mesh_head_width_mm"]) / C2["ratio_mesh_median"]),
                    implied_head_width_mm_if_ring_is_mesh=C2["implied_head_width_mm"],
                    head_width_mm=r["head_width_mm"], head_width_unc_mm=r["head_width_unc_mm"],
                    head_width_verdict=r["verdict_head_width"],
                    ring_od_mm=r["ring_od_mm"], ring_od_unc_mm=r["ring_od_unc_mm"], ring_od_verdict=r["verdict_ring_od"],
                    attribution=r["attribution"], attribution_why=r["attribution_evidence"],
                    source="out/head/front_fit.json + out/head/head_width_verdict.json",
                    superseded_front_view=superseded)
        combined["band_over_shell"] = C2.get("band_over_shell")
        combined["outline"] = {k: v for k, v in (C2.get("outline") or {}).items() if k not in ("u", "photo", "mesh", "dev_mm", "dev_unc_mm")}
        combined["tof_window"] = C2.get("tof")
        combined["head_width"] = dict(value_mm=r["head_width_mm"], unc_mm=r["head_width_unc_mm"],
                                      dev_mm=r["head_width_dev_mm"], verdict=r["verdict_head_width"],
                                      lines=r["head_width_lines"], chi2=r["chi2"], dof=r["dof"])
        combined["ring_od"] = dict(value_mm=r["ring_od_mm"], unc_mm=r["ring_od_unc_mm"],
                                   dev_mm=r["ring_od_dev_mm"], verdict=r["verdict_ring_od"])
    else:
        pair = dict(verdict=fe["verdict"], dev_mm=fe["dev_mm"], unc_mm=fe["dev_unc_mm"], dev_range_mm=fe.get("dev_mm_range"),
                    ratio_photo=fe["photo"], ratio_mesh=fe["mesh"], excess_pct=fe["diff_pct"],
                    implied_ring_od_mm_if_width_is_mesh=fe["photo_mm_if_width_is_mesh"],
                    implied_head_width_mm_if_ring_is_mesh=None,
                    attribution="CANNOT DETERMINE",
                    attribution_why="out/head/front_fit.json and out/head/head_width_verdict.json are not on disk: run tools/head_frontfit.py then tools/head_width_verdict.py")
    combined["front_pair"] = pair
    band = combined.get("band_over_shell")
    fails = [k for k in ("length", "major", "minor") if v[k] == "FAIL"]
    if fails or pair["verdict"] == "FAIL" or (band and band.get("verdict") == "FAIL"): head = "FAIL"
    elif all(v[k] == "PASS" for k in ("length", "major", "minor")) and pair["verdict"] == "PASS": head = "PASS"
    else: head = "CANNOT DETERMINE"
    head_why = []
    if band and band.get("verdict") == "FAIL":
        head_why.append("the accent trim band at the head's split line is %.3f mm narrower than the head's own widest row on the product "
                        "(%.4f ± %.4f of it) and exactly as wide on the mesh (%.4f); the same finding survives the adversarial reading in "
                        "which only the jaw carries the accent colour (%s mm vs the jaw alone, %s) — a shape difference that needs no "
                        "scale, no camera and no ring, MEASURED at %.1f sigma and confirmed at 8x on both edges (the cream shell's outer "
                        "edge sits at x 130 / 557 in the flat-lay while the band's sits at 138 / 551)" % (
                            abs(band["dev_mm"]), band["photo"], band["photo_unc"], band["mesh"],
                            abs(band.get("dev_mm_vs_jaw_only") or 0.0), band.get("verdict_vs_jaw_only"),
                            abs(band["dev_mm"]) / band["dev_unc_mm"] if band["dev_unc_mm"] else float("nan")))
    if pair.get("head_width_verdict"):
        head_why.append("head WIDTH, from the two lines that never use the ring's diameter (the profile silhouettes refitted at a swept "
                        "lateral scale, and the ToF aperture's offset from the eye axis): %s mm against the mesh's 91.763 (%s). Eye ring OD "
                        "%s mm against 30.000 (%s). The front view's ring/width pair is %+.1f ± %.1f %% (%s)" % (
                            fmt(pair["head_width_mm"], 3, False) + " ± " + fmt(pair["head_width_unc_mm"], 3, False),
                            pair["head_width_verdict"],
                            fmt(pair["ring_od_mm"], 3, False) + " ± " + fmt(pair["ring_od_unc_mm"], 3, False), pair["ring_od_verdict"],
                            pair["excess_pct"], pair.get("excess_unc_pct", 0.0), pair["verdict"]))
    if pair["verdict"] == "FAIL" and not pair.get("head_width_verdict"):
        head_why.append("the true front view rules the mesh out at every camera distance: ring OD / head width is %.4f ± %.4f in the photograph against %.4f on the mesh "
                        "(%+.1f %%, %s mm at the mesh width, bracket %s..%s mm over D) — at least one of {ring OD, head width} is more than %.1f mm from the mesh; which one is CANNOT DETERMINE (see front_pair)" % (
                            fe["photo"], fe["photo_unc"], fe["mesh"], fe["diff_pct"], fmt(fe["dev_mm"]), fmt(pair["dev_range_mm"][0]) if pair["dev_range_mm"] else "—",
                            fmt(pair["dev_range_mm"][1]) if pair["dev_range_mm"] else "—", RULE_MM))
    head_why.append("head length from the servo-scaled profiles: %s mm (%s), per-axis major %s / minor %s" % (
        ("%+.2f ± %.2f" % (L[0], L[1])) if L[0] is not None else "CANNOT DETERMINE", v["length"],
        ("%+.2f ± %.2f" % (MA[0], MA[1])) if MA[0] is not None else "—", ("%+.2f ± %.2f" % (MI[0], MI[1])) if MI[0] is not None else "—"))
    # eye bezel: it exists in the mesh (noenoeil), its diameter at the head's length scale agrees (profiles); the front pair cannot be attributed to it
    eye_parts = dict(exists_in_mesh="PASS", diameter_vs_length_profiles=v["eye_profile"], ring_width_pair=pair["verdict"],
                     attribution_to_ring=(pair.get("ring_od_verdict") or "CANNOT DETERMINE"),
                     ring_od_measured_mm=pair.get("ring_od_mm"), ring_od_measured_unc_mm=pair.get("ring_od_unc_mm"))
    if v["eye_profile"] == "FAIL": eye = "FAIL"
    elif v["eye_profile"] == "PASS" and pair["verdict"] == "PASS": eye = "PASS"
    else: eye = "CANNOT DETERMINE"
    settle = []
    settle.append("A calliper on one product head: top_head_shell length (mesh 122.690 mm), WIDTH across the beak and across the shell rim (mesh 91.763 / 91.760) and "
                  "height (46.336) to 0.1 mm, and the eye ring's outer diameter (mesh 30.000) — a 0.1 mm reading beats every photograph here by an order of magnitude, "
                  "settles the 1.5 mm rule outright and attributes the front-view ring/width excess to the ring or to the width.")
    settle.append("Or one photograph taken for the purpose: a true front view with a ruler in the plane of the face (fixes the ring/width pair in mm), and one pure "
                  "profile, beak closed, head level, the XL330 label face in the focal plane of the head, 4000+ px on the long side (the length to 0.6 mm).")
    settle.append("The camera distance of the store photographs (EXIF focal length + sensor, stripped from the published files, or a ruler in the frame) would remove the "
                  "D term from every servo-scaled ratio (photos[].size.D_note).")
    if profile_frame:
        settle.append("A cleaner pure-profile frame from Pollen's video (the README frame's neck servo is merged with its horn bracket and cables at 4x, out/head/profile_frame_servo_zoom.png).")
    out = dict(generated=time.strftime("%Y-%m-%d %H:%M"), rule_mm=RULE_MM, rule_source=RULE_SRC, xc_pct=XC_PCT, method=__doc__,
               profile_frame=profile_frame, sensitivity=sens,
               mesh=fit["mesh"], servo_source=fit["servo_source"], fit_method=fit["method"], front_method=front["method"],
               quick=fit.get("quick", False), photos=photos, front_view=front, combined=combined,
               verdict=dict(head=head, head_why=head_why, eye_bezel=eye, eye_bezel_parts=eye_parts,
                            basis=("head: %d photographs admitted (%s), each scaled by the XL330-M288-T case in the same frame (20.000 mm), posed and fitted "
                                   "with a perspective camera, size ratio product/mesh = k * W_render / W_photo; combined length deviation "
                                   "%s; per-axis %s / %s. Front view: ring OD / beak width, photo %.4f vs mesh %.4f (%s). Eye bezel: profile ring diameter at the head's "
                                   "length scale %s mm vs the noenoeil mesh 30.000 mm." % (
                                       combined["n_photos"], ", ".join(combined["photos_used"]) or "none",
                                       ("%+.3f ± %.3f mm" % (L[0], L[1])) if L[0] is not None else "CANNOT DETERMINE",
                                       ("%+.3f ± %.3f" % (MA[0], MA[1])) if MA[0] is not None else "—",
                                       ("%+.3f ± %.3f" % (MI[0], MI[1])) if MI[0] is not None else "—",
                                       fe["photo"], fe["mesh"], fe["verdict"],
                                       ("%+.2f ± %.2f" % (EY[0], EY[1])) if EY[0] is not None else "CANNOT DETERMINE")),
                            what_would_settle=settle,
                            remodel=(REMODEL(pair, combined) if head == "FAIL" else None)))
    json.dump(out, open(os.path.join(OUT, "head.json"), "w"), indent=1, default=float)
    print(json.dumps(dict(combined={k: combined[k] for k in combined if k != "front_pair"}, front_pair=pair, verdict=out["verdict"]), indent=1, default=float))
    for p in photos:
        print(p["id"], p["scale_verdict"], "|", p["scale_why"][:300])
        for t in p["scale_tests"]: print("   ", t["verdict"], t["test"], "|", str(t["value"])[:160])
    print("wrote out/head/head.json")


if __name__ == "__main__":
    main()
