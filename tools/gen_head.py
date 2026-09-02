#!/usr/bin/env python3
"""gen_head.py — build HEAD-RECONSTRUCTION.html from out/head/head.json
(tools/head_verdict.py). Every table here is generated from that file; nothing
is hand-maintained. Same academic style as COMPARISON.html (tools/doc.css).
"""
import json, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
D = json.load(open(os.path.join(REPO, "out", "head", "head.json")))
C = D["combined"]; V = D["verdict"]; FV = D["front_view"]; M = D["mesh"]


def _opt(name):
    q = os.path.join(REPO, "out", "head", name)
    return json.load(open(q)) if os.path.exists(q) else None


FF = _opt("front_fit.json")           # tools/head_frontfit.py — the front view re-measured
RW = _opt("head_width_verdict.json")  # tools/head_width_verdict.py — the two unknowns solved


def f(x, nd=3, sign=False):
    if x is None: return "—"
    return ("%+." + str(nd) + "f") % x if sign else ("%." + str(nd) + "f") % x


def pm(v, u, nd=3):
    if v is None: return "CANNOT DETERMINE"
    return "%s&nbsp;±&nbsp;%s" % (f(v, nd, True), f(u, nd))


def chip(v):
    cls = {"PASS": "pass", "FAIL": "no", "CANNOT DETERMINE": "cd"}.get(v, "cd")
    return '<span class="chip %s">%s</span>' % (cls, html.escape(v))


def esc(s): return html.escape(str(s))


# ---------------------------------------------------------------- per-photo blocks
def scale_rows():
    rows = []
    for p in D["photos"]:
        for s in p["scale"]["servos"]:
            if "width_px" not in s:
                rows.append("<tr><td>%s</td><td>%s</td><td colspan=6>%s — %s</td></tr>" % (esc(p["title"]), esc(s.get("what", "")), chip("CANNOT DETERMINE"), esc(s.get("why", ""))))
                continue
            sr = s.get("size_ratio", {}); xc = s.get("crosscheck") or {}
            if "mask_vs_analytic_pct" in xc:
                cross = "%s / %s px: <b>%s %%</b>, %s %% of the box visible" % (f(xc["mask"]["width_px"], 1), f(xc["analytic_px"], 1), f(xc["mask_vs_analytic_pct"], 2, True), f(100 * (xc.get("mask_fill_of_projected_bbox") or 0), 0))
                cross_chip = chip("PASS" if abs(xc["mask_vs_analytic_pct"]) <= D.get("xc_pct", 5.0) else "FAIL")
            else:
                cross = esc(xc.get("why", "not read")); cross_chip = chip("CANNOT DETERMINE")
            rows.append(
                "<tr><td>%s</td><td>%s</td><td class=n>%s<br><small>%d of %d lines</small></td><td class=n>%s</td>"
                "<td class=n>%s</td><td class=n>%s</td><td>%s %s</td><td class=n>%s</td></tr>" % (
                    esc(p["title"]), esc(s["what"]), f(s["width_px"], 2), s["n_accepted"], s["n_lines"],
                    pm(s["mm_per_px"], s["mm_per_px_unc"], 5),
                    f(s.get("render_width_px_analytic"), 2), f(s.get("render_silhouette_mm"), 2), cross_chip, cross,
                    pm(sr.get("product_over_mesh"), sr.get("unc"), 4) if sr else "—"))
            notes = ["<b>face evidence:</b> " + esc(s.get("face_evidence", ""))]
            if s.get("render_face_note"): notes.append("<b>model servo:</b> " + esc(s["render_face_note"]))
            rows.append('<tr class="sub"><td></td><td colspan=7><small>%s</small></td></tr>' % " · ".join(notes))
    return "\n".join(rows)


def fit_rows():
    rows = []
    for p in D["photos"]:
        t = p["fit"]; ab = t.get("at_bound", [])
        bound = ("%s %s" % (chip("FAIL"), esc(", ".join("%s on [%s, %s]" % (b["param"], f(b["bounds"][0], 1), f(b["bounds"][1], 1)) for b in ab)))) if ab else chip("PASS")
        rows.append("<tr><td>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td>"
                    "<td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td>%s</td></tr>" % (
                        esc(p["title"]), f(t["iou"], 4), f(t["eye_term"], 5), f(t["cam_distance_mm"], 0), f(t["cam_az_deg"], 2), f(t["cam_el_deg"], 2),
                        f(t["head_pitch_deg"], 2), f(t["head_yaw_deg"], 2), f(t["head_roll_deg"], 2) + ("" if t.get("head_roll_within_joint_range", True) else "<br><small>beyond the joint's ±%s°</small>" % f(t.get("head_roll_joint_range_deg", 25), 0)),
                        f(t["jaw_open_deg"], 2), pm(t["k_photo_px_per_render_px"], t["k_fit_spread"], 4), bound))
    return "\n".join(rows)


def dim_rows():
    rows = []
    for p in D["photos"]:
        s = p.get("size")
        if not s:
            x = p.get("size_excluded")
            rows.append("<tr><td>%s</td><td colspan=8>%s — scale excluded: %s%s</td></tr>" % (
                esc(p["title"]), chip("CANNOT DETERMINE"), esc(p.get("scale_why", "no scale feature measured")),
                (" (the excluded read would have been r = %s, %s mm)" % (pm(x["product_over_mesh"], x["unc"], 4), pm(x["head_length_dev_mm"], x["head_length_dev_unc_mm"], 2))) if x else "")); continue
        v = p["verdicts"]
        rows.append("<tr><td>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td>"
                    "<td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td>%s</td></tr>" % (
                        esc(p["title"]), pm(s["product_over_mesh"], s["unc"], 4), pm(s["head_length_dev_mm"], s["head_length_dev_unc_mm"]),
                        f(s["photo_head_extent_major_mm"]), f(s["mesh_head_extent_major_mm"]), pm(s["dev_major_mm"], s["dev_major_unc_mm"]),
                        f(s["photo_head_extent_minor_mm"]), f(s["mesh_head_extent_minor_mm"]), pm(s["dev_minor_mm"], s["dev_minor_unc_mm"]) + " " +
                        chip(v["length"]) + (("<br><small>%s</small>" % esc(p["verdict_why"])) if p.get("verdict_why") else "")))
    rows.append("<tr class=total><td><b>Combined (inverse-variance; spread %s mm)</b></td><td class=n><b>%s</b></td><td class=n><b>%s</b></td>"
                "<td class=n>—</td><td class=n>—</td><td class=n><b>%s</b></td><td class=n>—</td><td class=n>—</td><td><b>%s</b> %s</td></tr>" % (
                    f(C["head_length_spread_mm"]), pm(C["product_over_mesh"], C["product_over_mesh_unc"], 4),
                    pm(C["head_length_dev_mm"], C["head_length_dev_unc_mm"]), pm(C["dev_major_mm"], C["dev_major_unc_mm"]),
                    pm(C["dev_minor_mm"], C["dev_minor_unc_mm"]), chip(C["verdicts"]["length"])))
    return "\n".join(rows)


def eye_rows():
    rows = []
    for p in D["photos"]:
        e = p["eye"]
        if "diameter_mm" not in e:
            rows.append("<tr><td>%s</td><td colspan=6>%s</td></tr>" % (esc(p["title"]), chip("CANNOT DETERMINE"))); continue
        off = e.get("centre_offset_photo_minus_render_mm")
        rows.append("<tr><td>%s</td><td class=n>%s × %s</td><td class=n>%s / %s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td>%s</td></tr>" % (
            esc(p["title"]), f(e["major_px"], 1), f(e["minor_px"], 1), f(e.get("ring_over_head_photo"), 4), f(e.get("ring_over_head_render"), 4),
            pm(e.get("dev_scale_free_mm"), e.get("dev_scale_free_unc_mm"), 2), pm(e["diameter_mm"], e["diameter_unc_mm"], 2),
            ("%s / %s" % (f(off[0], 2, True), f(off[1], 2, True))) if off else "—",
            chip(p.get("verdicts_eye", "CANNOT DETERMINE")) + ("<br><small>%s</small>" % esc(e.get("ring_read_why", "")))))
    return "\n".join(rows)


def front_rows():
    names = {"eye_od_over_width": "eye ring OD / head width", "eye_minor_over_major": "eye ring minor / major (view tilt)",
             "eye_below_top_over_width": "eye centre below shell top / head width", "eye_x_offset_over_width": "eye centre off the mid-line / head width",
             "tof_x_from_eye_over_width": "ToF window centre right of the eye / head width", "tof_y_from_eye_over_width": "ToF window centre below the eye / head width",
             "tof_w_over_width": "ToF window width / head width", "tof_h_over_width": "ToF window height / head width",
             "first_beak_band_top_below_top_over_width": "beak lip (bottom shell) top edge below shell top / head width"}
    rows = []
    for k, c in FV["comparison"].items():
        if c.get("dimensionless"):
            rows.append("<tr><td>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>—</td><td class=n>—</td><td class=n>—</td><td>n/a — %s</td></tr>" % (
                names.get(k, k), pm(c["photo"], c.get("photo_unc") or 0, 4), f(c["mesh"], 4), f(c["diff"], 4, True), esc(c["why"]))); continue
        if c.get("mesh") is None:
            rows.append("<tr><td>%s</td><td class=n>%s</td><td class=n>—</td><td class=n>—</td><td class=n>%s</td><td class=n>—</td><td class=n>—</td><td>%s %s</td></tr>" % (
                names.get(k, k), pm(c["photo"], c.get("photo_unc") or 0, 4), f(c["photo"] * FV["mesh_head_width_mm"], 2), chip("CANNOT DETERMINE"), esc(c["why"]))); continue
        rng = c.get("dev_mm_range")
        rows.append("<tr><td>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s%s</td><td>%s<br><small>%s</small></td></tr>" % (
            names.get(k, k), pm(c["photo"], c.get("photo_unc") or 0, 4), f(c["mesh"], 4), (f(c["diff_pct"], 2, True) + " %") if abs(c["mesh"]) > 0.01 else "— (mesh ≈ 0)", f(c["photo_mm_if_width_is_mesh"], 2),
            f(c["mesh_mm"], 2), pm(c["dev_mm"], c["dev_unc_mm"], 2),
            ("<br><small>D bracket %s..%s</small>" % (f(rng[0], 2, True), f(rng[1], 2, True))) if rng else "",
            chip(c["verdict"]), esc(c.get("verdict_why", ""))))
    return "\n".join(rows)


def photo_sections():
    out = []
    for i, p in enumerate(D["photos"], 1):
        t = p["fit"]; s = p.get("size") or p.get("size_excluded") or {}
        wide = p["pictures"].get("render_servo_wide")
        if wide and os.path.exists(os.path.join(REPO, wide)):
            servo_pic = '<img src="%s" alt="%s render servo, wide frame"><figcaption>The ±250 mm cross-check frame at the fitted camera: the servo geom\'s mask (box) read across its own axis against its projected width.</figcaption>' % (wide, esc(p["id"]))
        else:
            servo_pic = '<p class="note">No cross-check picture: the servo was not visible even in the ±250 mm frame (Table 2 says why).</p>'
        tests = "".join("<li>%s %s — %s</li>" % (chip(x["verdict"]) if x["verdict"] != "NOTE" else "<b>note</b>", esc(x["test"]), esc(x["value"])) for x in p.get("scale_tests", []))
        excl = ""
        if p.get("size_excluded"):
            x = p["size_excluded"]
            excl = " The read this scale would have given — r = %s, %s mm — is recorded but not used." % (pm(x["product_over_mesh"], x["unc"], 4), pm(x["head_length_dev_mm"], x["head_length_dev_unc_mm"], 2))
        out.append(f"""
  <h3>4.{i} {esc(p["title"])}</h3>
  <p class="paircap">{esc(p["note"])} · <code>{esc(p["path"])}</code> {p["image_size_px"][0]}×{p["image_size_px"][1]} px ·
    camera distance <b>{f(t["cam_distance_mm"], 0)} mm</b> (assumed, §6b), IoU <b>{f(t["iou"], 3)}</b>,
    head pitch {f(t["head_pitch_deg"], 1)}° yaw {f(t["head_yaw_deg"], 1)}° roll {f(t["head_roll_deg"], 1)}° jaw {f(t["jaw_open_deg"], 1)}°</p>
  <figure class="wide"><img src="{p["pictures"]["pair"]}" alt="{esc(p["id"])} real | ours | overlay">
    <figcaption>Real (left), ours at the same camera and fitted pose (centre), overlay (right; blue = photograph's head region, orange = our head silhouette and eye ring).</figcaption></figure>
  <div class="pair">
    <figure><span class="tag">Real · the measurements drawn</span><img src="{p["pictures"]["measure"]}" alt="{esc(p["id"])} measurement">
      <figcaption>Blue lines: the servo-case scan lines that set the scale; green: the eye-ring ellipse; red: the neck cut; purple: the head region.</figcaption></figure>
    <figure><span class="tag ours">Ours · the same servo in the render, cross-checked</span>{servo_pic}</figure>
  </div>
  <p class="note"><b>Scale tests</b>, each run:</p><ul class="tests">{tests}</ul>
  <p class="note">Scale {chip(p.get("scale_verdict", "CANNOT DETERMINE"))} — {esc(p.get("scale_why", ""))}.{excl}
    {("Size ratio product/mesh <b>%s</b> (%s) → head length %s mm %s%s; along the head's own axes: major %s mm, minor %s mm." % (
        pm(s.get("product_over_mesh"), s.get("unc"), 4), esc(s.get("D_note", "")), pm(s.get("head_length_dev_mm"), s.get("head_length_dev_unc_mm")),
        chip(p.get("verdicts", {}).get("length", "CANNOT DETERMINE")), (" — " + esc(p["verdict_why"])) if p.get("verdict_why") else "",
        pm(s.get("dev_major_mm"), s.get("dev_major_unc_mm")), pm(s.get("dev_minor_mm"), s.get("dev_minor_unc_mm")))) if p.get("size") else ""}</p>""")
    return "\n".join(out)


settle = "".join("<li>%s</li>" % esc(x) for x in V["what_would_settle"]) or "<li>Nothing — every check PASSES.</li>"
PF = D.get("profile_frame")


def sens_rows():
    rows = []
    for x in D.get("sensitivity", []):
        rows.append("<tr><td>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s / %s</td><td class=n>%s</td><td class=n>%s</td><td><code>%s</code>%s</td></tr>" % (
            esc(x["photo"]), f(x["D_mm"], 0), f(x["iou"], 4), f(x["yaw"], 1), f(x.get("roll"), 1), pm(x["product_over_mesh"], x["unc"], 4), f(x["head_length_dev_mm"], 2, True), esc(x["file"]),
            (" <small>on a bound: %s — not used</small>" % esc(", ".join(x["at_bound"]))) if x.get("at_bound") else ""))
    for p in D["photos"]:
        if p.get("size"):
            rows.append("<tr><td>%s (main run)</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s / %s</td><td class=n>%s</td><td class=n>%s</td><td><code>out/head/head_fit.json</code></td></tr>" % (
                esc(p["id"]), f(p["fit"]["cam_distance_mm"], 0), f(p["fit"]["iou"], 4), f(p["fit"]["head_yaw_deg"], 1), f(p["fit"]["head_roll_deg"], 1), pm(p["size"]["product_over_mesh"], p["size"].get("unc_fit_only", p["size"]["unc"]), 4), f(p["size"]["head_length_dev_mm"], 2, True)))
    return "\n".join(rows)
n_photos = C["n_photos"]
quick = " <b>(quick fit — rerun without --quick before release)</b>" if D.get("quick") else ""


# ---------------------------------------------------------------- section 7: attribution
def attrib_line_rows():
    if not RW: return "<tr><td colspan=5>out/head/head_width_verdict.json not on disk</td></tr>"
    out = []
    for l in RW["lines"]:
        v = l.get("head_width_mm"); u = l.get("head_width_unc_mm")
        out.append("<tr><td>%s</td><td>%s</td><td class=n>%s</td><td class=n>%s</td><td>%s</td></tr>" % (
            esc(l["name"]), "yes" if l.get("ring_free") else "<b>no</b>",
            f(v, 3) if v is not None else "—", ("± " + f(u, 3)) if u else "—",
            esc(l.get("what") or "")))
    r = RW["result"]
    out.append('<tr class="total"><td><b>Head width — the ring-free lines combined</b></td><td>yes</td>'
               '<td class=n><b>%s</b></td><td class=n><b>± %s</b></td><td>%s vs the mesh 91.763 mm; &chi;&sup2; %s on %d dof</td></tr>' % (
                   f(r["head_width_mm"], 3), f(r["head_width_unc_mm"], 3),
                   f(r["head_width_dev_mm"], 3, True) + " mm " + chip(r["verdict_head_width"]), f(r["chi2"], 4), r["dof"]))
    out.append('<tr class="total"><td><b>Eye ring OD — the front view\u2019s ratio at that width</b></td><td>—</td>'
               '<td class=n><b>%s</b></td><td class=n><b>± %s</b></td><td>%s vs the mesh 30.000 mm</td></tr>' % (
                   f(r["ring_od_mm"], 3), f(r["ring_od_unc_mm"], 3),
                   f(r["ring_od_dev_mm"], 3, True) + " mm " + chip(r["verdict_ring_od"])))
    return "\n".join(out)


def sweep_rows():
    if not RW: return ""
    out = []
    for sw in RW["sweeps"]:
        cells = " ".join("%s&thinsp;/&thinsp;%s" % (f(a, 4), f(b, 5)) for a, b in zip(sw["swept"], sw["objective"]))
        best = sw.get("quad_minimiser")
        out.append("<tr><td><code>%s</code></td><td>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td><td>%s</td></tr>" % (
            esc(sw["photo"]), "lateral scale <i>s<sub>w</sub></i>" if sw["parameter"] == "s_w" else "ring scale <i>s<sub>r</sub></i>",
            f(best, 4) if best else "—", f(sw.get("sigma"), 4) if sw.get("sigma") else "—", f(sw["objective_noise"], 5),
            ("<b>minimum on the end of the swept range</b> (runs %s) &mdash; a refusal, not a measurement" % esc(sw["runs_to"] or ""))
            if sw["min_on_sweep_edge"] else ("grid %s, local-3 %s, IoU peak at %s" % (f(sw["grid_best_s"], 4), f(sw.get("quad_minimiser_local3"), 4), f(sw["best_iou_s"], 4)))))
        out.append('<tr class="sub"><td colspan=6><small>s / objective: %s</small></td></tr>' % cells)
    return "\n".join(out)


def outline_svg():
    o = (FF or {}).get("comparison", {}).get("outline")
    if not o: return ""
    W, H, ml, mt, mr, mb = 760, 300, 54, 16, 16, 34
    u = o["u"]; a = o["photo"]; b = o["mesh"]
    x0, x1 = min(u), max(u); y0, y1 = 0.82, 1.01
    X = lambda t: ml + (t - x0) / (x1 - x0) * (W - ml - mr)
    Y = lambda w: mt + (y1 - w) / (y1 - y0) * (H - mt - mb)
    def path(vals, col, dash=""):
        d = " ".join(("M" if i == 0 else "L") + "%.1f %.1f" % (X(u[i]), Y(vals[i])) for i in range(len(u)))
        return '<path d="%s" fill="none" stroke="%s" stroke-width="2"%s/>' % (d, col, (' stroke-dasharray="%s"' % dash) if dash else "")
    ticks = []
    for t in [x for x in (-0.1, 0.0, 0.1, 0.2, 0.3) if x0 <= x <= x1]:
        ticks.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#c9c4bb"/><text x="%.1f" y="%.1f" font-size="10" text-anchor="middle" fill="#6b665e">%+.1f</text>' % (
            X(t), mt, X(t), H - mb, X(t), H - mb + 13, t))
    for w in (0.85, 0.90, 0.95, 1.00):
        ticks.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#eae6df"/><text x="%.1f" y="%.1f" font-size="10" text-anchor="end" fill="#6b665e">%.2f</text>' % (
            ml, Y(w), W - mr, Y(w), ml - 6, Y(w) + 3, w))
    return ('<svg viewBox="0 0 %d %d" width="100%%" role="img" aria-label="head outline, product against mesh">'
            '%s%s%s'
            '<text x="%.1f" y="%.1f" font-size="10" fill="#6b665e" text-anchor="middle">height above/below the eye-ring centre, in head widths</text>'
            '<text x="12" y="%.1f" font-size="10" fill="#6b665e" transform="rotate(-90 12 %.1f)" text-anchor="middle">width / widest row</text>'
            '<g font-size="11"><rect x="%.1f" y="%.1f" width="14" height="3" fill="#b3541e"/><text x="%.1f" y="%.1f">product</text>'
            '<rect x="%.1f" y="%.1f" width="14" height="3" fill="#2f5d9e"/><text x="%.1f" y="%.1f">Pollen mesh</text></g></svg>') % (
        W, H, "".join(ticks), path(a, "#b3541e"), path(b, "#2f5d9e"),
        (ml + W - mr) / 2, H - 2, H / 2, H / 2,
        ml + 14, mt + 8, ml + 32, mt + 12, ml + 14, mt + 26, ml + 32, mt + 30)


def tof_rows():
    t = (C.get("tof_window") or {})
    if not t.get("measured_on_mesh"): return "<tr><td colspan=4>not measured</td></tr>"
    rows = [("window width / head width", t["photo_w_over_width"], t["mesh_w_over_width"]),
            ("window height / head width", t["photo_h_over_width"], t["mesh_h_over_width"]),
            ("centre offset from the eye axis / head width", t["photo_dx_over_width"], t["mesh_dx_mm"] / 91.763),
            ("centre offset below the eye axis / head width", t["photo_dy_over_width"], t["mesh_dy_over_width"])]
    return "\n".join("<tr><td>%s</td><td class=n>%s</td><td class=n>%s</td><td class=n>%s</td></tr>" % (
        esc(nm), f(pv, 5), f(mv, 5), f((pv - mv) * 91.763, 3, True)) for nm, pv, mv in rows)

# ---------------------------------------------------------------- section 7 values
B = C.get("band_over_shell") or {}
O = (FF or {}).get("comparison", {}).get("outline") or {}
T = C.get("tof_window") or {}
P = C.get("front_pair") or {}
R = (RW or {}).get("result") or {}
_cls = lambda v: "warn" if v == "FAIL" else ("cd" if v == "CANNOT DETERMINE" else "")
retraction = esc(R.get("retraction") or "no retraction recorded")
retr_cls = "cd"
band_cls = _cls(B.get("verdict"))
band_photo = f(B.get("photo"), 4); band_unc = f(B.get("photo_unc"), 4); band_mesh = f(B.get("mesh"), 4)
band_dev = f(B.get("dev_mm"), 3, True); band_chip = chip(B.get("verdict", "CANNOT DETERMINE"))
band_sigma = f(abs(B["dev_mm"]) / B["dev_unc_mm"], 1) if B.get("dev_unc_mm") else "—"
band_dev_jaw = f(B.get("dev_mm_vs_jaw_only"), 3, True); band_chip_jaw = chip(B.get("verdict_vs_jaw_only", "CANNOT DETERMINE"))
band_per_side = f(abs(B["dev_mm"]) / 2.0, 2) if B.get("dev_mm") else "—"
_fc = (FF or {}).get("comparison", {})
adm = _fc.get("admissible_poses", "—"); ofp = _fc.get("of_poses", "—"); gate = esc(_fc.get("pose_gate", ""))
s_best = f(_fc.get("s_w_that_matches"), 3) if _fc.get("s_w_that_matches") else "—"
attrib_rows = attrib_line_rows()
_att = R.get("attribution", "") or ""
attribution_short = esc(_att.split(":")[0])
attribution = esc(_att.split(":", 1)[1].strip() if ":" in _att else _att)
attribution_why = esc(R.get("attribution_evidence", ""))
sweep_rows = sweep_rows()
pic_cw = "out/head/width_cream-profile-left_s_w_tight.png"
pic_gw = "out/head/width_graphite-profile-right_s_w_tight.png"
outline_rms = f(O.get("rms_mm"), 3); outline_max = f(O.get("max_abs_mm"), 3)
outline_n_fail = O.get("n_fail", "—"); outline_n = O.get("n_points", "—")
outline_chip = chip(O.get("verdict", "CANNOT DETERMINE"))
outline_shift = f(abs(O.get("widest_u_shift", 0.0)), 4)
outline_svg = outline_svg()
outline_excluded = esc(O.get("excluded", ""))
tof_note = esc(T.get("note", "")); tof_w = f(T.get("mesh_aperture_w_mm"), 3); tof_h = f(T.get("mesh_aperture_h_mm"), 3)
tof_dx = f(T.get("mesh_dx_mm"), 3); tof_site = f(T.get("mjcf_site_dy_mm"), 4)
tof_site_off = f((T.get("mjcf_site_dy_mm") or 0) - (T.get("mesh_dx_mm") or 0), 3)
tof_rows = tof_rows()


HTML = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Head Reconstruction</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="tools/doc.css">
<style>
  .pair{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:10px 0 4px}}
  .pair figure{{margin:0;padding:8px}}
  .pair figure img{{width:100%;object-fit:contain;background:#fff}}
  figure.wide{{margin:10px 0 4px;padding:8px}} figure.wide img{{width:100%;background:#fff}}
  figcaption{{font-family:var(--sans);font-size:12px;color:var(--ink-2);margin-top:4px}}
  .tag{{font-family:var(--sans);font-size:10.5px;font-weight:600;letter-spacing:.07em;text-transform:uppercase;display:inline-block;padding:2px 8px;margin-bottom:6px;border:1px solid var(--hair);color:var(--ink-2)}}
  .tag.ours{{color:var(--accent);border-color:var(--accent)}}
  .paircap{{font-family:var(--sans);font-size:12.5px;color:var(--ink-2);margin:0 0 2px}}
  .note{{font-size:13.5px;color:var(--ink-2);margin:2px 0 18px;max-width:54em}}
  .verdict{{border-left:3px solid var(--accent);padding:2px 0 2px 18px;margin:14px 0;font-size:15.5px}}
  .verdict b{{color:var(--accent)}} .verdict.warn{{border-left-color:var(--no)}} .verdict.warn b{{color:var(--no)}}
  .verdict.cd{{border-left-color:var(--cd)}} .verdict.cd b{{color:var(--cd)}}
  .chip.no{{color:var(--no);border-color:var(--no)}}
  .statbar{{display:flex;flex-wrap:wrap;gap:0;border-bottom:1px solid var(--hair);margin:8px 0 2px}}
  .stat{{padding:12px 26px 12px 0;margin-right:22px}}
  .stat b{{display:block;font-weight:700;font-size:22px;font-variant-numeric:tabular-nums}}
  .stat span{{font-family:var(--sans);font-size:12px;color:var(--ink-2)}}
  table.data td.n,table.data th.n{{text-align:right;font-variant-numeric:tabular-nums}}
  table.data{{font-size:12px;table-layout:auto}} table.data th{{white-space:normal;padding:6px 8px 5px;font-size:10.5px}} table.data td{{padding:5px 8px}}
  table.data td code,table.data td a{{overflow-wrap:anywhere}}
  table.data td:first-child code{{white-space:nowrap}} table.data small{{font-size:11px;color:var(--ink-2)}}
  table.data td.n{{white-space:normal;overflow-wrap:normal;word-break:keep-all}} table.data tr.sub td{{border-bottom:1px solid var(--hair);padding-top:0;line-height:1.35}}
  ul.tests{{font-size:13px;margin:0 0 10px 0;padding-left:22px;max-width:70em}} ul.tests li{{margin:3px 0}}
  .chip{{white-space:nowrap}}
  tr.total td{{border-top:2px solid var(--rule)}}
  @media(max-width:640px){{.pair{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<div class="wrap">
<p class="backlink"><a href="RELEASE.html">← Release dossier</a> · <a href="COMPARISON.html">Reference match</a></p>

<header class="hero">
  <p class="eyebrow">Microduck reverse-engineering · lane A · head conformance</p>
  <h1>Is the simulation head the product head? Measured from the photographs.</h1>
  <p class="sub">GOAL.md finding 1 said the simulation head is "far longer front-to-back than the compact domed head in every product photo"
  and its eye bezel is missing; the handover correction demoted that to CANNOT DETERMINE. Leif: <em>"im not sure that the simulation
  meshes are the same as their product meshes! you have to use the images as references"</em>. This document settles it by measurement:
  every product photograph is scaled by the XL330-M288-T servo visible in the same frame, our model is posed to the photograph with a
  perspective camera, and the head shell is compared in millimetres against the mesh's 91.760 × 122.690 × 46.336 mm under the rebuild
  rule (1.5 mm per axis), never loosened.</p>
  <div class="rev"><span>MD-HEAD-001 · Rev A</span><span>{esc(D["generated"])}</span><span>data: <code>out/head/head.json</code></span><span>generator: <code>tools/gen_head.py</code></span></div>
</header>

<div class="statbar">
  <div class="stat"><b>{n_photos}</b><span>photographs measured</span></div>
  <div class="stat"><b>{pm(C["product_over_mesh"], C["product_over_mesh_unc"], 4)}</b><span>product / mesh size ratio</span></div>
  <div class="stat"><b>{pm(C["head_length_dev_mm"], C["head_length_dev_unc_mm"], 2)} mm</b><span>head length, product − mesh</span></div>
  <div class="stat"><b>{chip(V["head"])}</b><span>head verdict at the 1.5 mm rule</span></div>
  <div class="stat"><b>{chip(C["front_pair"]["verdict"])}</b><span>front view: ring OD / head width</span></div>
  <div class="stat"><b>{chip(V["eye_bezel"])}</b><span>eye bezel</span></div>
  <div class="stat"><b>{chip((C.get("band_over_shell") or {}).get("verdict", "CANNOT DETERMINE"))}</b><span>trim band ÷ the head&rsquo;s widest row (§7)</span></div>
  <div class="stat"><b>{f((C.get("head_width") or {}).get("value_mm"), 3)} mm</b><span>head width measured (mesh 91.763)</span></div>
</div>

<nav class="toc">
  <a href="#answer">1 Verdict</a><a href="#rule">2 The question and the rule</a><a href="#scale">3 Scale</a>
  <a href="#photos">4 Photographs, posed and overlaid</a><a href="#dims">5 Measured dimensions</a><a href="#eye">6 Eye bezel</a>
  <a href="#sens">6b Camera distance</a><a href="#attrib">7 Attribution</a><a href="#settle">8 What would settle the rest</a><a href="#method">9 Method and limits</a>
</nav>

<section id="answer">
  <h2><span class="n">1</span>Verdict</h2>
  <div class="verdict {'warn' if V['head']=='FAIL' else ('cd' if V['head']=='CANNOT DETERMINE' else '')}">
    <b>Head: {esc(V["head"])}.</b>{quick} {" ".join(esc(x[0].upper() + x[1:]) + "." for x in V["head_why"])}
    Across {n_photos} admitted profile photograph{"s" if n_photos != 1 else ""} ({esc(", ".join(C["photos_used"]) or "none")}) the product head is
    <b>{pm(C["product_over_mesh"], C["product_over_mesh_unc"], 4)}</b> times the simulation mesh in length (a deviation of
    <b>{pm(C["head_length_dev_mm"], C["head_length_dev_unc_mm"], 2)} mm</b> on 122.690 mm; along the head's own principal axes
    {pm(C["dev_major_mm"], C["dev_major_unc_mm"], 2)} mm and {pm(C["dev_minor_mm"], C["dev_minor_unc_mm"], 2)} mm).
    The "far longer" head of finding 1 is not in the photographs: the length agrees to the stated uncertainty, and the silhouettes
    overlay (§4) once the jaw is posed open and the head is yawed as in the shot.
  </div>
  <div class="verdict {'warn' if C['front_pair']['verdict']=='FAIL' else ('cd' if C['front_pair']['verdict']=='CANNOT DETERMINE' else '')}">
    <b>Front view, ring OD / head width: {esc(C["front_pair"]["verdict"])}.</b> In the one true front view the eye ring's outer diameter is
    <b>{f(C["front_pair"]["ratio_photo"], 4)}</b> of the head&rsquo;s outer silhouette width against <b>{f(C["front_pair"]["ratio_mesh"], 4)}</b> on the mesh
    ({f(C["front_pair"]["excess_pct"], 1, True)} %; {pm(C["front_pair"]["dev_mm"], C["front_pair"]["unc_mm"], 2)} mm at the mesh width, and between
    {f(C["front_pair"]["dev_range_mm"][0], 2, True) if C["front_pair"]["dev_range_mm"] else "—"} and {f(C["front_pair"]["dev_range_mm"][1], 2, True) if C["front_pair"]["dev_range_mm"] else "—"} mm over every
    camera distance from 400 mm to infinity). Which member of the pair is off is <b>CANNOT DETERMINE</b> from a ratio: {esc(C["front_pair"]["attribution_why"])}.
    Implied, if the ring is the mesh's 30.000 mm: head width <b>{f(C["front_pair"]["implied_head_width_mm_if_ring_is_mesh"], 2)} mm</b> ({f(C["front_pair"]["implied_head_width_mm_if_ring_is_mesh"] - FV["mesh_head_width_mm"], 2, True)} mm);
    if the width is the mesh's {f(FV["mesh_head_width_mm"], 3)} mm: ring OD <b>{f(C["front_pair"]["implied_ring_od_mm_if_width_is_mesh"], 2)} mm</b>.
  </div>
  <div class="verdict {'warn' if V['eye_bezel']=='FAIL' else ('cd' if V['eye_bezel']=='CANNOT DETERMINE' else '')}">
    <b>Eye bezel: {esc(V["eye_bezel"])}.</b> The bezel is <em>not</em> missing from the mesh: <code>noenoeil.stl</code> is a Ø30.000 mm ring,
    7.5 mm long, standing proud of the face panel (whose only opening is the Ø14.5 mm lens hole) — exactly the accent-colour ring in the
    photographs ({chip(V["eye_bezel_parts"]["exists_in_mesh"])} exists). Its diameter at the head's own length scale (ring over head extent, photograph
    against render, scale-free) reads {pm(C["eye_dev_mm"], C["eye_dev_unc_mm"], 2)} mm in the store photographs whose ring is seen whole (Table 5) {chip(V["eye_bezel_parts"]["diameter_vs_length_profiles"])};
    the front view's ring/width pair is {chip(V["eye_bezel_parts"]["ring_width_pair"])} and its attribution to the ring {chip(V["eye_bezel_parts"]["attribution_to_ring"])}.
    Face layout in the front view (Table 6, each graded): {", ".join("%s %s mm %s" % (esc(nm), f(FV["comparison"][k]["dev_mm"], 2, True), chip(FV["comparison"][k]["verdict"])) for k, nm in (("eye_below_top_over_width", "eye centre below the shell top"), ("eye_x_offset_over_width", "eye centre off the mid-line"), ("tof_x_from_eye_over_width", "ToF window from the MJCF site")))}.
  </div>
  {('<div class="verdict warn"><b>Re-model?</b> ' + esc(V["remodel"]) + '</div>') if V.get("remodel") else ""}
  <p class="note">{esc(V["basis"])}</p>
</section>

<section id="rule">
  <h2><span class="n">2</span>The question and the rule</h2>
  <p>COMPARISON.html §5.1 could only compare scale-free silhouette ratios, and the one photograph it used has the beak open and the head
  pitched and yawed — so its +69 % aspect-ratio difference was confounded and it stopped at CANNOT DETERMINE, naming photogrammetric
  scaling against the servo as the evidence that would settle it. That is what this document does. The grading rule is the one every
  rebuilt part on this shelf is held to — <b>{esc(D["rule_source"])}</b> — applied to the product as the reference and Pollen's mesh as the
  candidate. Because a photograph yields a deviation <i>d</i> with an uncertainty <i>u</i>, the verdict is decided the only honest way:
  PASS when |d| + u ≤ 1.5 mm, FAIL when |d| − u &gt; 1.5 mm, otherwise CANNOT DETERMINE. Nothing is loosened; a measurement that cannot
  discriminate at 1.5 mm says so.</p>
  <div class="tw"><table class="data">
    <caption>Table 1. The mesh under test (out/verify/mech_dims.json, mm, file frame) and the known-size features used for scale.</caption>
    <thead><tr><th>Item</th><th>Value</th><th>Source</th></tr></thead>
    <tbody>
      <tr><td><code>top_head_shell</code></td><td class=n>{f(M["top_head_shell_mm"][0],3)} × {f(M["top_head_shell_mm"][1],3)} × {f(M["top_head_shell_mm"][2],3)}</td><td><code>{esc(M["source"])}</code> (length = 122.690 along the mesh's second axis)</td></tr>
      <tr><td><code>bottom_head_shell</code></td><td class=n>{f(M["bottom_head_shell_mm"][0],3)} × {f(M["bottom_head_shell_mm"][1],3)} × {f(M["bottom_head_shell_mm"][2],3)}</td><td><code>{esc(M["source"])}</code></td></tr>
      <tr><td><code>jaw</code></td><td class=n>{f(M["jaw_mm"][0],3)} × {f(M["jaw_mm"][1],3)} × {f(M["jaw_mm"][2],3)}</td><td><code>{esc(M["source"])}</code></td></tr>
      <tr><td><code>noenoeil</code> (eye ring)</td><td class=n>Ø30.000 × 7.5 boss, Ø14.4 bore</td><td>{esc(M["eye_ring_source"])}</td></tr>
      <tr><td>XL330-M288-T case width</td><td class=n>20.000 mm</td><td>{esc(D["servo_source"])}</td></tr>
    </tbody>
  </table></div>
</section>

<section id="scale">
  <h2><span class="n">3</span>Scale — millimetres per pixel from the servo in the same frame</h2>
  <p>The XL330-M288-T is the only object of independently known size in every store photograph. Its case width is read as the mode of the
  dark-run widths over many scan lines across the case (label text and cables break single lines; the case gives the same width on every
  clean line). The width the same 20.000 mm face has in our render at the fitted camera is W<sub>render</sub> = 20.000 mm × f / z — the exact pinhole the
  frame was drawn with (f from its field of view, z the servo geom's mean vertex depth in the fitted camera, MuJoCo's stereo pair averaged as
  its mono render does). The model's servo therefore fixes the <em>depth</em>; the face the photograph shows is identified on the photograph
  (the label text sits on the 20 × 34 face — Table 2's evidence column) and, for the ankle, checked against the neck-servo scale of the same
  shoot. The size ratio product/mesh = k · W<sub>render</sub> / W<sub>photo</sub> carries the servo-to-head depth difference through the camera
  model rather than assuming it away. The projection is cross-checked for <em>every</em> servo: in a second ±250 mm / 1600 px frame at the same
  camera the servo geom's segmentation mask is read across its own axis with the same mode-of-runs estimator and compared with its projected
  width (Table 2; the first release of this page skipped that read for the ankle and still printed PASS — a defect found by review and
  fixed 2026-09-03). Uncertainty per servo: ±1 px per edge plus the accepted lines' spread, the fit's spread of k, and the camera-distance
  term of §6b.</p>
  <div class="tw"><table class="data">
    <caption>Table 2. Scale features. mm/px is at the servo's depth. W<sub>render</sub> = 20.000 mm × f / z through the head frame's pinhole (Table 3's D). The cross-check reads the servo geom's segmentation mask across its own axis in a frame wide enough to hold it (the ankle included) against the geom's projected-vertex width; a servo without that read is never graded PASS.</caption>
    <thead><tr><th>Photograph</th><th>Feature</th><th class=n>Width in photo (px)</th><th class=n>mm / px</th><th class=n>W<sub>render</sub> (px): 20.000 mm at the servo's depth</th><th class=n>Model servo silhouette (mm)</th><th>Cross-check: mask vs projected width, ±250 mm frame</th><th class=n>Size ratio product/mesh</th></tr></thead>
    <tbody>
{scale_rows()}
    </tbody>
  </table></div>
</section>

<section id="photos">
  <h2><span class="n">4</span>Photographs, posed and overlaid — real beside ours, always</h2>
  <p>For each photograph the model is posed by fitting camera elevation, azimuth (3/4 shots), distance, head pitch / yaw / roll, the jaw opening
  and a similarity transform, maximising silhouette IoU of the head region plus the eye-ring ellipse match. The jaw is not a joint in the
  published model; its geoms are rotated about the measured hinge (the 15×10×3 bearing centre). Head pitch is the head's orientation relative to the trunk, 0 = level (eye-ring axis horizontal, bisected on the mesh), positive = face up.</p>
  <div class="tw"><table class="data">
    <caption>Table 3. Fitted pose per photograph. k = photo px per render px (fit spread from re-polishing). Search boxes: el ±12°, pitch ±40°, yaw 0..±90°, roll ±45° (wider than the head_roll joint's ±25° so the fit cannot sit on the joint limit unreported — the first run's cream fit did, at exactly −25.00°), jaw 0..40°, k ×0.7..1.4; a parameter on its box edge is a constrained solution and fails the scale.</caption>
    <thead><tr><th>Photograph</th><th class=n>IoU</th><th class=n>eye term</th><th class=n>D (mm)</th><th class=n>az (°)</th><th class=n>el (°)</th><th class=n>pitch (°)</th><th class=n>yaw (°)</th><th class=n>roll (°)</th><th class=n>jaw (°)</th><th class=n>k</th><th>On a bound?</th></tr></thead>
    <tbody>
{fit_rows()}
    </tbody>
  </table></div>
{photo_sections()}
</section>

<section id="dims">
  <h2><span class="n">5</span>Measured dimensions — product against mesh, in millimetres</h2>
  <p>Head length deviation = 122.690 × (r − 1). Major / minor are the extents of the head region along its own principal axes in the photograph
  (0.5 / 99.5 percentile, so a stray pixel cannot set them) against the render's extents at the servo-anchored scale — the shape residual left
  after the size ratio. Uncertainty per axis: the scale uncertainty, ±2 px on each mask edge, and the mm/px uncertainty, in quadrature.</p>
  <div class="tw"><table class="data">
    <caption>Table 4. Deviations product − mesh, mm ± uncertainty; verdict per the 1.5 mm rule (PASS |d|+u ≤ 1.5; FAIL |d|−u &gt; 1.5; else CANNOT DETERMINE).</caption>
    <thead><tr><th>Photograph</th><th class=n>r = product/mesh</th><th class=n>Length dev (mm)</th><th class=n>Major photo (mm)</th><th class=n>Major mesh (mm)</th><th class=n>Δ major (mm)</th><th class=n>Minor photo (mm)</th><th class=n>Minor mesh (mm)</th><th>Δ minor (mm) · verdict</th></tr></thead>
    <tbody>
{dim_rows()}
    </tbody>
  </table></div>
</section>

<section id="eye">
  <h2><span class="n">6</span>Eye bezel — does the product have a part the mesh lacks?</h2>
  <p>No. The mesh has it: <code>noenoeil</code> is a Ø30.000 mm × 7.5 mm ring in front of the face panel (Table 1). The shelf part
  <code>ce-parts/microduck-eye-ring</code> (v0.0.1, the noenoeil mesh loaded unchanged by <code>tools/head_eye_ring_shelve.py</code>) carries the numbers below in its evidence ledger. Two independent
  reads of the product ring: (a) in each profile photograph the accent-hue ring pixels give an ellipse whose major axis is the ring diameter,
  scaled by the servo (and, more robustly, by the same ring in the render through the fitted similarity — "via render", which needs no mm/px);
  (b) the flat-lay <em>inside-the-box</em> photograph is a true front view, so every face feature is a scale-free ratio to the head width, compared
  with our mesh rendered in a true front view with the head level.</p>
  <div class="tw"><table class="data">
    <caption>Table 5. Eye ring in the profile photographs (mesh 30.000 mm). The scale-free column is the ring's diameter over the head's extent, photograph against render at the fitted pose — independent of the servo, of mm/px and of the camera distance; Δ Ø = 30 × (ratio − 1). Centre offset = photo ring centre − render ring centre, mm (x right, y down).</caption>
    <thead><tr><th>Photograph</th><th class=n>Ellipse major × minor (px)</th><th class=n>ring / head extent, photo / render</th><th class=n>Δ Ø scale-free (mm)</th><th class=n>Ø via servo (mm, carries the D question)</th><th class=n>Centre offset (mm)</th><th>Verdict</th></tr></thead>
    <tbody>
{eye_rows()}
    </tbody>
  </table></div>
  <figure class="wide"><img src="out/head/front_pair.png" alt="front view: real flat-lay beside our mesh">
    <figcaption>True front view: the flat-lay photograph (left; a composite — the battery and gamepad in it carry two different mm/px, so no other object is used for scale) beside our mesh rendered front-on with the head level. Blue = the beak-band width and mid-line (the width used); violet = the shell silhouette's widest row, which the soft shadow to the right of the shell inflates ({FV["photo"]["shell_silhouette"]["width_px_range"][0]}–{FV["photo"]["shell_silhouette"]["width_px_range"][1]} px over the threshold sweep — the first release used it and read the eye 2.13 mm off the mid-line; the beak band puts it at {f(FV["comparison"]["eye_x_offset_over_width"]["dev_mm"], 2, True)} mm); green = eye-ring ellipse; red = ToF window.</figcaption></figure>
  <div class="tw"><table class="data">
    <caption>Table 6. Face layout as ratios to the head width (the beak band, {FV["photo"]["head_width_px"]} px in the photograph, {esc(FV["photo"]["head_width_feature"])}), photo vs mesh, each with its propagated uncertainty and graded at the 1.5 mm rule; mm columns assume the head width is the mesh's {f(FV["mesh_head_width_mm"],3)} mm. Rows whose two features sit at different depths are corrected over a camera-distance bracket 400 mm..∞ and graded at every point of it. Source <code>out/head/front_view.json</code>.</caption>
    <thead><tr><th>Ratio</th><th class=n>Photo ± u</th><th class=n>Mesh</th><th class=n>Diff</th><th class=n>Photo (mm, implied)</th><th class=n>Mesh (mm)</th><th class=n>Δ (mm) ± u</th><th>Verdict</th></tr></thead>
    <tbody>
{front_rows()}
    </tbody>
  </table></div>
  <p class="note">{esc(FV["uncertainty"])}{"" if FV["uncertainty"].rstrip().endswith(".") else "."} The ToF window (a rounded slot {f(FV["photo"]["tof"]["w_px"] / FV["photo"]["head_width_px"] * FV["mesh_head_width_mm"], 1)} × {f(FV["photo"]["tof"]["h_px"] / FV["photo"]["head_width_px"] * FV["mesh_head_width_mm"], 1)} mm implied) has no geom in the mesh — the face panel's slot is CANNOT DETERMINE on the mesh side and is a feature the face-part rebuild must carry.</p>
</section>

<section id="sens">
  <h2><span class="n">6b</span>Camera distance — the one thing the store frames do not give</h2>
  <p>The store photographs carry no EXIF and no ruler; the near ankle servo reads 136–146 px against the neck's 131.4 px (44.1 mm nearer)
  depending on the scan tilt, which brackets D only between ~700 and ~1650 mm. Because the head is yawed ~50° towards the camera, its face is
  ~45 mm nearer than the servo and the head-to-servo ratio moves with D. The fit was therefore repeated at other distances; the half-range of
  r over these runs is added to the uncertainty of the verdict.</p>
  <div class="tw"><table class="data">
    <caption>Table 7. Sensitivity of the size ratio to the assumed camera distance (same photograph, same method, quick fits).</caption>
    <thead><tr><th>Photograph</th><th class=n>D (mm)</th><th class=n>IoU</th><th class=n>fitted yaw / roll (°)</th><th class=n>r = product/mesh (fit u only)</th><th class=n>head length dev (mm)</th><th>file</th></tr></thead>
    <tbody>
{sens_rows()}
    </tbody>
  </table></div>
  <p class="note">{esc(C.get("D_sensitivity_note", "no sensitivity runs found"))}. {" ".join("<b>%s</b>: %s." % (esc(p["id"]), esc(p["size"].get("D_note", ""))) for p in D["photos"] if p.get("size"))}</p>
  <h3>The pure-profile frame — scale-free check</h3>
  <p>{esc(PF["aspect_reading"]) if PF else "images/github/gh_readme_7.png not analysed"}. Neither half yields a mm/px. Real half: {esc(PF["halves"]["real"]["scale_why"]) if PF else ""}. Simulator half: {esc(PF["halves"]["sim"]["scale_why"]) if PF else ""}. Both scans are bounded to the drawn region and a run that reaches the bound is refused; the zoom below shows every accepted run. The frame is kept because it is the only published view with the head un-yawed, real beside Pollen's own render.</p>
  <figure class="wide"><img src="out/head/profile_frame_pair.png" alt="pure profile frame, sim beside real"><figcaption>Pollen's README frame: their simulator render (left) beside the real unit (right); blue = the head silhouette's principal-axis box on each; orange = the bounded servo scan region and its accepted runs.</figcaption></figure>
  <figure class="wide"><img src="out/head/profile_frame_servo_zoom.png" alt="the two servo regions at 4x"><figcaption>The two servo regions at 4×, real (left) and simulator (right): the accepted scan runs in blue span the case plus the horn bracket (real) and the case plus the grey neck plate (simulator) — the reason each half is CANNOT DETERMINE, visible rather than asserted.</figcaption></figure>
</section>

<section id="attrib">
  <h2><span class="n">7</span>Attribution — which of {{ring, head width}} is wrong, re-measured like for like</h2>
  <p>§6 leaves one thing open and it is the important one: the front view fixes the <i>ratio</i> eye-ring&nbsp;OD ÷ head width, and a ratio
  cannot say which member of the pair is off. Re-reading that measurement found that it was also not comparing the same feature on the two
  sides. Both are settled here — the first by measuring the pair with one estimator, the second by measuring the head width twice with
  instruments that never touch the ring at all.</p>

  <div class="verdict {retr_cls}"><b>Retraction.</b> {retraction}</div>

  <div class="verdict {band_cls}"><b>What does FAIL: the accent trim band is inset on the product and flush on the mesh.</b>
  Band width ÷ the head&rsquo;s own widest row is <b>{band_photo} ± {band_unc}</b> on the product against <b>{band_mesh}</b> on the mesh —
  <b>{band_dev} mm</b> at the mesh width, {band_sigma}σ, {band_chip}. It survives the adversarial reading in which only the jaw carries the
  accent colour ({band_dev_jaw} mm against the jaw alone, {band_chip_jaw}). This ratio uses no scale, no camera model and no ring: it is two
  widths on the same object in the same photograph.</p></div>

  <figure class="wide"><img src="out/head/front_edges.png" alt="the head's shell edge against the trim band's, at 8x, both sides">
    <figcaption>The FAIL at 8× on the photograph itself. Blue = the cream shell&rsquo;s outer edge at the head&rsquo;s widest row
    (x&nbsp;129 and 561); orange = the accent band&rsquo;s edge (x&nbsp;137 and 555). The shell overhangs the band by about
    {band_per_side} mm per side. On Pollen&rsquo;s mesh <code>top_head_shell</code> (91.760), <code>bottom_head_shell</code> (91.763) and
    <code>jaw</code> (91.416 mm) are flush to 0.35 mm.</figcaption></figure>

  <figure class="wide"><img src="out/head/front_fit_pair.png" alt="front view, real beside ours at two lateral scales">
    <figcaption>The front view re-measured: the flat-lay with the head&rsquo;s <em>outer</em> silhouette, the ring ellipse and the ToF window
    marked, beside our mesh rendered head-level at the mesh width and at a lateral scale of {s_best}. Both sides now use the same estimator
    (masks filled, full principal extents) and the mesh pose is gated by the ring&rsquo;s ellipticity <i>and</i> by its offset from the
    shell mid-line ({adm} of {ofp} rendered poses admitted: {gate}).</figcaption></figure>

  <div class="tw"><table class="data">
    <caption>Table 7. The head width, measured three ways, and the ring that follows. A line is <i>ring-free</i> when its value does not
    depend on the eye ring&rsquo;s diameter — only those are combined, so the answer is not assumed into existence.</caption>
    <thead><tr><th>Line</th><th>Ring-free</th><th class=n>Head width (mm)</th><th class=n>u</th><th>What it is</th></tr></thead>
    <tbody>{attrib_rows}</tbody>
  </table></div>
  <div class="verdict cd"><b>Attribution: {attribution_short}</b> {attribution}</div>
  <p class="note">{attribution_why}</p>

  <div class="tw"><table class="data">
    <caption>Table 8. The profile-likelihood sweeps behind the first line. The head is rebuilt at a swept lateral scale (shells, face panel,
    jaw and soft pads scaled about the head&rsquo;s own mid-plane — MEASURED as body <i>y</i> to 0.0000°, the eye ring left at 30.000 mm) or
    at a swept ring scale, and the full pose is refitted at each. σ is the displacement at which the parabola rises by the fit&rsquo;s own
    measured noise (the spread of its restarts).</caption>
    <thead><tr><th>Photograph</th><th>Parameter</th><th class=n>minimiser</th><th class=n>σ</th><th class=n>fit noise</th><th>Reading</th></tr></thead>
    <tbody>{sweep_rows}</tbody>
  </table></div>
  <div class="pair">
    <figure><span class="tag">Real vs ours</span><img src="{pic_cw}" alt="cream profile, lateral-scale sweep"><figcaption>Cream, left profile: the photograph with our silhouette at <i>s<sub>w</sub></i> = 1 (red) and at the fitted scale (blue), then our render at both.</figcaption></figure>
    <figure><span class="tag">Real vs ours</span><img src="{pic_gw}" alt="graphite profile, lateral-scale sweep"><figcaption>Graphite, right profile: the same, from the other side and a different colourway.</figcaption></figure>
  </div>

  <h3>7.1 The outline itself, with nothing fitted</h3>
  <p>The head&rsquo;s front-view outline, width at each row ÷ the widest row, against that row&rsquo;s height above or below the
  <em>eye-ring centre</em> in the same units. No scale, no camera, no pose fit — if the product and the mesh are the same shape the two
  curves lie on each other. Over the compared range they agree to <b>{outline_rms} mm rms</b> (worst {outline_max} mm, {outline_n_fail} of
  {outline_n} sample rows outside the rule by more than their own uncertainty): {outline_chip}. The systematic that remains is the same
  finding as above — the product is wider above its widest row and narrower below it, and its widest row sits {outline_shift} head-widths
  higher than the mesh&rsquo;s.</p>
  <figure class="wide">{outline_svg}<figcaption>Excluded and why: {outline_excluded}</figcaption></figure>

  <h3>7.2 The ToF window — the mesh has one, and it is measurable</h3>
  <p>{tof_note} The aperture measures <b>{tof_w} × {tof_h} mm</b> and its centre sits <b>{tof_dx} mm</b> to the head&rsquo;s right of the
  eye-ring axis.</p>
  <div class="tw"><table class="data">
    <caption>Table 9. The ToF window, both sides, as fractions of the head width (the photograph carries no scale of its own).</caption>
    <thead><tr><th>Ratio</th><th class=n>Product</th><th class=n>Mesh</th><th class=n>Δ at the mesh width (mm)</th></tr></thead>
    <tbody>{tof_rows}</tbody>
  </table></div>
</section>

<section id="settle">
  <h2><span class="n">8</span>What would settle the remaining CANNOT DETERMINEs</h2>
  <ul>{settle}</ul>
</section>

<section id="method">
  <h2><span class="n">9</span>Method and honest limits</h2>
  <ul>
    <li><b>Scripts.</b> <code>tools/head_photomatch.py</code> (scale, pose fit, size — writes <code>out/head/head_fit.json</code> and every overlay),
      <code>tools/head_frontview.py</code> (front-view ratios with propagated uncertainty and verdicts — <code>out/head/front_view.json</code>), <code>tools/head_profile_frame.py</code> (the README frame — <code>out/head/profile_frame.json</code>), <code>tools/head_frontfit.py</code> (the front view re-measured like for like — <code>out/head/front_fit.json</code>),
      <code>tools/head_width.py</code> (the head rebuilt at a swept lateral or ring scale and refitted — <code>out/head/width_tight.json</code>),
      <code>tools/head_width_verdict.py</code> (the two unknowns solved — <code>out/head/head_width_verdict.json</code>),
      <code>tools/head_verdict.py</code> (merge + verdict —
      <code>out/head/head.json</code>), <code>tools/gen_head.py</code> (this page), <code>tools/shot_page.py</code> (the read-back in <code>out/head/readback/</code>). Renderer: MuJoCo offscreen segmentation at 1000², perspective free camera whose
      field of view follows the fitted distance so the head always spans the same frame.</li>
    <li><b>Which servo face.</b> Read off the published MJCF: the servo mesh is 20.000 (mesh x) × 34.06 (mesh z) × 29.04 (mesh y, case + horn) and in the neck body
      mesh x = world −x, mesh z = world −z, so a profile camera sees the 20.000 × 34 horn/label face (<code>tools/head_probe.py</code>). The photographs show the
      label on that face, as the drawing does.</li>
    <li><b>Perspective.</b> The store shots are close (D in Table 3 is an assumption inside a measured 700–1650 mm bracket, §6b); the near and far edges of the head differ in scale by up to 4 % at 0.5 m, which is why
      the camera is perspective and the fit is repeated over D. The flat-lay front view is perspective too: its ring stands 4.4 mm nearer the camera than the beak edge (mesh depths in <code>front_view.json</code>), carried as the D bracket of Table 6.</li>
    <li><b>Constrained fits.</b> A fitted parameter on the edge of its search box means the optimum is outside the box; Table 3 lists every such parameter and the photograph's scale is then refused. The first release's cream fit sat on the roll bound at −25.00° and was published without saying so; the roll box is now ±45° and the check is automatic.</li>
    <li><b>Defects found by review on the first release, all fixed 2026-09-03:</b> a PASS printed for a cross-check that was never read (graphite's ankle servo); a section contradicting its own table on that point; a citation to sensitivity files that did not exist (D700/D1600 — the runs are D600/D2000) and a mis-stated bracket centre; a unitless ratio printed in millimetres; the largest front-view deviation (eye off the mid-line, −2.13 mm) reported as a match — a shadow artefact, now {f(FV["comparison"]["eye_x_offset_over_width"]["dev_mm"], 2, True)} mm on the beak band; a front-view uncertainty typed as 2 % instead of propagated; a profile-frame scan that ran into the background and blamed a bracket; a D-sensitivity note that described a different number than the one used; a licence version that the source does not state; a missing full stop; and tables wider than the page.</li>
    <li><b>What §7 supersedes, and what it does not.</b> §6 and Table 6 are the FIRST front-view measurement and are kept as published: they
      are what §7 corrects, and a reader who cannot see the old number cannot check the correction. Where the two disagree, §7 governs — it
      measures the same feature on both sides. §5 (head length, from the profiles) and §3 (scale) are untouched by it.</li>
    <li><b>The lateral-scale instrument, and how it was broken on purpose.</b> <code>tools/head_width.py</code> edits the head meshes&rsquo;
      vertices before the renderer is built (MuJoCo uploads mesh data to its GL context once, at construction) and scales them about the head
      body&rsquo;s own lateral axis, which is MEASURED as body <i>y</i> to 0.0000°. Self-test: a shell scale of 0.5 halves the rendered head
      mask (442 → 222 px) and leaves the ring mask at 146 px; a ring scale of 1.5 takes the ring mask 146 → 219 px (×1.500) and leaves the
      head mask at 442 px.</li>
    <li><b>What the numbers are not.</b> Bounding-box level agreement between the product and the mesh. Not a p95 surface-distance check (that needs a scan
      of a product head), not a manufacturing tolerance. Every number is from published photographs and published digital assets; no physical unit has
      been callipered.</li>
    <li><b>Mask edges.</b> The head region is the non-white silhouette above a neck cut, minus a neck polygon drawn by hand and shown on every measurement picture;
      the cream shell against the white background is segmented by chroma as well as luminance. Edge uncertainty ±2 px is carried into every mm.</li>
  </ul>
</section>

</div>
</body>
</html>
"""
open(os.path.join(REPO, "HEAD-RECONSTRUCTION.html"), "w").write(HTML)
print("wrote HEAD-RECONSTRUCTION.html  photos=%d head=%s eye=%s" % (n_photos, V["head"], V["eye_bezel"]))
