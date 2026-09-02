#!/usr/bin/env python3
"""head_verdict.py — merge the head measurements into ONE data file with the
verdict, out/head/head.json, which tools/gen_head.py and tools/gen_comparison.py
both render (so HEAD-RECONSTRUCTION.html and COMPARISON.html §5 cannot disagree).

Inputs
  out/head/head_fit.json      tools/head_photomatch.py — per-photo scale, pose fit, size
  out/head/front_view.json    tools/head_frontview.py — scale-free face layout, true front view

The rule (docs/REBUILD-PROTOCOL.md §3, never loosened): a rebuilt part PASSES
when its bounding box is within 1.5 mm per axis of the reference and the p95
surface distance is <= 1.0 mm. Here the "reference" is the PRODUCT, measured
from photographs, and the candidate is Pollen's simulation mesh. A photograph
gives a deviation d with an uncertainty u, so the verdict is decided the only
honest way:
    PASS               |d| + u <= 1.5 mm     (inside the rule even at the edge of the uncertainty)
    FAIL               |d| - u >  1.5 mm     (outside the rule even at the edge of the uncertainty)
    CANNOT DETERMINE   otherwise             (the measurement cannot discriminate at the rule's level)
The per-photo deviations are combined inverse-variance weighted; a photo's
systematic errors (mask edges, pose) are inside its u, and the photos share no
scale feature measurement, so the combination is legitimate but the spread
between photos is also reported and, if larger than the combined u, replaces it.

    /Applications/FreeCAD.app/Contents/Resources/bin/python tools/head_verdict.py
"""
import os, sys, json, math, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "out", "head")
RULE_MM = 1.5
RULE_SRC = "docs/REBUILD-PROTOCOL.md §3: PASS = p95 <= 1.0 mm both ways AND bbox within 1.5 mm per axis AND 0 unmatched reference features"


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


def main():
    fit = json.load(open(os.path.join(OUT, "head_fit.json")))
    front = json.load(open(os.path.join(OUT, "front_view.json")))
    pf_path = os.path.join(OUT, "profile_frame.json")
    profile_frame = json.load(open(pf_path)) if os.path.exists(pf_path) else None
    # camera-distance sensitivity runs (tools/head_photomatch.py --D <mm> --tag _D<mm>): same photo, other distances
    sens = []
    for fn in sorted(os.listdir(OUT)):
        if fn.startswith("head_fit_") and "_D" in fn and fn.endswith(".json"):
            j = json.load(open(os.path.join(OUT, fn)))
            for p in j["photos"]:
                if p.get("size"):
                    sens.append(dict(file="out/head/" + fn, photo=p["id"], D_mm=p["fit"]["cam_distance_mm"], iou=p["fit"]["iou"],
                                     product_over_mesh=p["size"]["product_over_mesh"], unc=p["size"]["unc"],
                                     head_length_dev_mm=p["size"]["head_length_dev_mm"], yaw=p["fit"]["head_yaw_deg"], k=p["fit"]["k_photo_px_per_render_px"]))
    photos = []
    for p in fit["photos"]:
        s = p.get("size", {})
        row = dict(id=p["id"], title=p["title"], path=p["path"], colourway=p["colourway"], note=p["note"],
                   image_size_px=p["image_size_px"], scale=p["scale"], fit=p["fit"], eye=p["eye"], size=s, inputs=p["inputs"],
                   pictures=dict(pair="out/head/%s_pair.png" % p["id"], measure="out/head/%s_measure.png" % p["id"],
                                 overlay="out/head/%s_overlay.png" % p["id"], ours="out/head/%s_ours.png" % p["id"],
                                 real="out/head/%s_real.png" % p["id"], render_servo="out/head/%s_render_servo.png" % p["id"]))
        if s:
            row["verdicts"] = dict(length=grade(s["head_length_dev_mm"], s["head_length_dev_unc_mm"]),
                                   major=grade(s["dev_major_mm"], s["dev_major_unc_mm"]),
                                   minor=grade(s["dev_minor_mm"], s["dev_minor_unc_mm"]))
        if "dev_mm" in p["eye"]:
            e = p["eye"]
            row["verdicts_eye"] = grade(e["dev_mm"], e["diameter_unc_mm"])
        photos.append(row)
    # combined
    L = combine([(p["size"]["head_length_dev_mm"], p["size"]["head_length_dev_unc_mm"]) for p in photos if p.get("size")])
    MA = combine([(p["size"]["dev_major_mm"], p["size"]["dev_major_unc_mm"]) for p in photos if p.get("size")])
    MI = combine([(p["size"]["dev_minor_mm"], p["size"]["dev_minor_unc_mm"]) for p in photos if p.get("size")])
    R = combine([(p["size"]["product_over_mesh"], p["size"]["unc"]) for p in photos if p.get("size")])
    EY = combine([(p["eye"]["dev_mm"], p["eye"]["diameter_unc_mm"]) for p in photos if "dev_mm" in p["eye"]])
    EYR = combine([(p["eye"]["diameter_via_render_mm"] - 30.0, p["eye"]["diameter_unc_mm"]) for p in photos if "diameter_via_render_mm" in p["eye"]])
    fv = front["comparison"]
    combined = dict(n_photos=len([p for p in photos if p.get("size")]),
                    product_over_mesh=R[0], product_over_mesh_unc=R[1],
                    head_length_dev_mm=L[0], head_length_dev_unc_mm=L[1], head_length_spread_mm=L[2],
                    dev_major_mm=MA[0], dev_major_unc_mm=MA[1], dev_minor_mm=MI[0], dev_minor_unc_mm=MI[1],
                    eye_dev_mm=EY[0], eye_dev_unc_mm=EY[1], eye_dev_via_render_mm=EYR[0], eye_dev_via_render_unc_mm=EYR[1],
                    eye_front_view_dev_mm=fv["eye_od_over_width"]["dev_mm"],
                    eye_front_view_unc_mm=0.02 * 30.0,   # the flat-lay pose uncertainty (front_view.json 'uncertainty'), 2 % of the ring
                    verdicts=dict(length=grade(L[0], L[1]), major=grade(MA[0], MA[1]), minor=grade(MI[0], MI[1]),
                                  eye_profile=grade(EY[0], EY[1]), eye_front=grade(fv["eye_od_over_width"]["dev_mm"], 0.6)))
    v = combined["verdicts"]
    if v["length"] == "FAIL" or v["major"] == "FAIL" or v["minor"] == "FAIL": head = "FAIL"
    elif v["length"] == "PASS" and v["major"] == "PASS" and v["minor"] == "PASS": head = "PASS"
    else: head = "CANNOT DETERMINE"
    eye_vs = [v["eye_profile"], v["eye_front"]]
    eye = "FAIL" if "FAIL" in eye_vs else ("PASS" if all(x == "PASS" for x in eye_vs) else "CANNOT DETERMINE")
    # D-sensitivity: the spread of r across the sensitivity runs of the main photo is added to the combined uncertainty
    if sens:
        rs = [x["product_over_mesh"] for x in sens] + [p["size"]["product_over_mesh"] for p in photos if p.get("size") and p["id"] == sens[0]["photo"]]
        d_spread = 0.5 * (max(rs) - min(rs))
        combined["D_sensitivity_half_range"] = d_spread
        combined["D_sensitivity_note"] = ("camera distance is CANNOT DETERMINE from the store frames; the half-range of r over the sensitivity runs "
                                          "(%s) is added in quadrature to the length uncertainty" % ", ".join("%.0f mm: %.4f" % (x["D_mm"], x["product_over_mesh"]) for x in sens))
        if combined["head_length_dev_unc_mm"] is not None:
            combined["head_length_dev_unc_mm"] = math.sqrt(combined["head_length_dev_unc_mm"] ** 2 + (122.690 * d_spread) ** 2)
            combined["product_over_mesh_unc"] = math.sqrt(combined["product_over_mesh_unc"] ** 2 + d_spread ** 2)
            combined["verdicts"]["length"] = grade(combined["head_length_dev_mm"], combined["head_length_dev_unc_mm"])
            v = combined["verdicts"]
            if v["length"] == "FAIL" or v["major"] == "FAIL" or v["minor"] == "FAIL": head = "FAIL"
            elif v["length"] == "PASS" and v["major"] == "PASS" and v["minor"] == "PASS": head = "PASS"
            else: head = "CANNOT DETERMINE"
    settle = []
    if sens and combined.get("D_sensitivity_half_range") is not None and head != "PASS":
        settle.append("The camera distance of the store photographs: a 1 mm ruler in the frame, or the EXIF focal length + sensor (stripped from the "
                      "published files), would fix D and remove the ±%.4f the sensitivity runs put on r." % combined["D_sensitivity_half_range"])
    if head != "PASS":
        settle.append("A calliper on one product head: top_head_shell length (mesh 122.690 mm), width (91.760) and height (46.336) to 0.1 mm — "
                      "a 0.1 mm reading beats every photograph here by an order of magnitude and settles the 1.5 mm rule outright.")
        settle.append("Or one more photograph taken for the purpose: pure profile, beak closed, head level, a ruler or the XL330 label face in the "
                      "focal plane of the head, 4000+ px on the long side — the scale uncertainty then drops below 0.5 % (0.6 mm on the length).")
    if eye != "PASS":
        settle.append("The eye ring: a calliper across the ring's outer edge (mesh noenoeil 30.000 mm), or Pollen's part drawing; the front-view "
                      "photograph already puts it at +%.2f mm (implied) and the profiles at %s." % (
                          fv["eye_od_over_width"]["dev_mm"], ("%+.2f ± %.2f mm" % (EY[0], EY[1])) if EY[0] is not None else "CANNOT DETERMINE"))
    out = dict(generated=time.strftime("%Y-%m-%d %H:%M"), rule_mm=RULE_MM, rule_source=RULE_SRC, method=__doc__,
               profile_frame=profile_frame, sensitivity=sens,
               mesh=fit["mesh"], servo_source=fit["servo_source"], fit_method=fit["method"], front_method=front["method"],
               quick=fit.get("quick", False), photos=photos, front_view=front, combined=combined,
               verdict=dict(head=head, eye_bezel=eye,
                            basis=("head: %d photographs, each scaled by the XL330-M288-T case in the same frame (20.000 mm), posed and fitted "
                                   "with a perspective camera, size ratio product/mesh = k * W_render / W_photo; combined length deviation "
                                   "%s; per-axis %s / %s. Eye bezel: profile ring diameter vs the noenoeil mesh 30.000 mm, and the true-front-view "
                                   "ratio eye OD / head width (photo %.4f vs mesh %.4f)." % (
                                       combined["n_photos"],
                                       ("%+.3f ± %.3f mm" % (L[0], L[1])) if L[0] is not None else "CANNOT DETERMINE",
                                       ("%+.3f ± %.3f" % (MA[0], MA[1])) if MA[0] is not None else "—",
                                       ("%+.3f ± %.3f" % (MI[0], MI[1])) if MI[0] is not None else "—",
                                       fv["eye_od_over_width"]["photo"], fv["eye_od_over_width"]["mesh"])),
                            what_would_settle=settle))
    json.dump(out, open(os.path.join(OUT, "head.json"), "w"), indent=1, default=float)
    print(json.dumps(dict(combined=combined, verdict=out["verdict"]), indent=1, default=float))
    print("wrote out/head/head.json")


if __name__ == "__main__":
    main()
