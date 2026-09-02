#!/usr/bin/env python3
"""head_profile_frame.py — the one published PURE-PROFILE view with the head un-yawed:
images/github/gh_readme_7.png (Pollen's README, 2215 x 884), Pollen's own simulator
render on the left and the real sky unit on the right, both in profile, jaw closed,
eye ring not visible (so head yaw ~ 0). Why it matters: in the store photographs the
head is yawed 50 deg towards the camera, and the head-to-servo size ratio then depends
on the camera distance (the face is ~45 mm nearer than the servo) — a distance the
store frames do not reveal (HEAD-RECONSTRUCTION.html §3). In a pure profile the head's
silhouette extremes (crest of the dome, front face, rear) and the neck servos all sit
on the robot's centre plane, so ONE mm/px serves both, to first order independent of
the camera distance.

Measured, both halves with the same estimators:
  servo width   mode of the dark-run widths across the upper neck servo case (20.000 mm,
                the horn/label face — the same face as in the store photographs). The
                scan is BOUNDED to the half's region and a run that reaches the bound is
                refused (it measured the region, not a case). On the simulator half the
                background is a saturated blue, darker than the luminance threshold, so
                saturated pixels are forced bright before the scan (the servo is grey).
  head extents  principal-axis extents of the head silhouette (colour-segmented: sky
                blue + orange on the real unit; white + yellow on the render), 0.5/99.5
                percentile; the major axis is the head length (shell + closed beak), the
                minor the head height at that pitch.
Result: head length in mm for the real unit; the same for Pollen's render (which uses
these very meshes, so it must read ~122.7 mm — that is the method's check); and the
ratio real/sim, which is scale-free.

Limits (stated, not hidden): a video frame — the servo is ~45 px wide, so +-1.5 px is
+-3.3 %, i.e. +-4 mm on the head; motion blur; a residual head yaw of 10 deg would
lengthen the silhouette by ~11 % (yaw only ever makes it LONGER), so the real value is an
upper bound on the product head length if any yaw remains. Every refusal below names
what the scan met, and out/head/profile_frame_servo_zoom.png shows both servo regions at
4x with the scan lines drawn, so a reader can see it.

Writes out/head/profile_frame.json, out/head/profile_frame_pair.png and
out/head/profile_frame_servo_zoom.png.
    /Applications/FreeCAD.app/Contents/Resources/bin/python tools/head_profile_frame.py
"""
import os, sys, json, math, time
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import head_photomatch as hp

REPO = hp.REPO; OUT = hp.OUT
IMG = "images/github/gh_readme_7.png"
MESH_LEN = 122.690      # top_head_shell length (out/verify/mech_dims.json)
SERVO_MM = 20.000       # XL330-M288-T case width (hp.XL330_SRC)
CASE_PX_EXPECTED = 45.0 # what a 20 mm case would be at this frame's scale (head 293-317 px for a ~123 mm head -> ~2.4 px/mm)

HALVES = {
    "real": dict(region=(1600, 20, 2215, 330), mode="real",
                 servo=dict(rows=(275, 335), seed_x=1930, tilt_deg=-8.0, what="upper neck servo (head_pitch), horn/label face"),
                 servo_region=(1880, 240, 2010, 345),
                 zoom=(1800, 180, 2100, 400),
                 note="real sky unit, right half of the frame"),
    "sim": dict(region=(330, 20, 720, 230), mode="sim",
                servo=dict(rows=(235, 300), seed_x=545, tilt_deg=-12.0, what="upper neck servo in Pollen's render"),
                servo_region=(480, 215, 620, 320),
                zoom=(380, 150, 680, 370),
                note="Pollen's own simulator render, left half of the frame (same meshes)"),
}


def head_mask(rgb, half):
    x0, y0, x1, y1 = half["region"]
    sub = rgb[y0:y1, x0:x1]; h, s, v = hp.hsv(sub)
    if half["mode"] == "real":
        m = ((h >= 175) & (h <= 215) & (s > 0.25) & (v > 0.35)) | ((h >= 5) & (h <= 40) & (s > 0.45) & (v > 0.35))
    else:
        m = ((s < 0.18) & (v > 0.72)) | ((h >= 35) & (h <= 65) & (s > 0.4) & (v > 0.5))
    m = ndimage.binary_opening(m, iterations=2)
    lab, n = ndimage.label(m); sizes = ndimage.sum(m, lab, range(1, n + 1))
    m = lab == (1 + int(np.argmax(sizes)))
    m = ndimage.binary_fill_holes(ndimage.binary_closing(m, iterations=3))
    full = np.zeros(rgb.shape[:2], bool); full[y0:y1, x0:x1] = m
    return full


def scan_luminance(rgb, half):
    """the image the servo scan walks: luminance, with saturated pixels forced bright on the simulator half so its
    blue background (luminance ~60, below any case threshold) ends a run instead of swallowing it."""
    L = rgb.mean(axis=2).astype(float)
    if half["mode"] == "sim":
        h, s, v = hp.hsv(rgb)
        L = L.copy(); L[s > 0.30] = 255.0
    return L


def main():
    rgb = hp.load_rgb(os.path.join(REPO, IMG))
    res = dict(generated=time.strftime("%Y-%m-%d %H:%M"), method=__doc__, image=IMG, size_px=[int(rgb.shape[1]), int(rgb.shape[0])],
               mesh_head_length_mm=MESH_LEN, servo_mm=SERVO_MM, servo_source=hp.XL330_SRC, halves={})
    im = Image.fromarray(rgb.astype(np.uint8)); d = ImageDraw.Draw(im)
    zooms = []
    for key, half in HALVES.items():
        m = head_mask(rgb, half); ys, xs = np.nonzero(m)
        e = hp.ellipse_of(np.stack([xs, ys], 1).astype(float))
        L = scan_luminance(rgb, half)
        x0, y0, x1, y1 = half["servo_region"]
        bg = float(L[y0:y1, x0:x1].max()); bg_lum = float(rgb.mean(axis=2)[y0:y1, x0:x1].mean())
        sv = hp.measure_servo(rgb, dict(half["servo"], geom="neck_upper"), thresh=95, L=L, region=half["servo_region"])
        r = dict(note=half["note"], region=list(half["region"]), head=e, head_bbox=[int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
                 head_axis_deg=math.degrees(math.atan2(e["major_axis_dir"][1], e["major_axis_dir"][0])), servo=sv,
                 servo_region=list(half["servo_region"]), servo_region_mean_luminance=bg_lum,
                 scan_image="luminance; saturated (s > 0.30) pixels forced to 255 so the blue background ends a run" if half["mode"] == "sim" else "luminance")
        if "width_px" in sv:
            mmpp = SERVO_MM / sv["width_px"]; unc = mmpp * sv["width_px_unc"] / sv["width_px"]
            r["mm_per_px"] = mmpp; r["mm_per_px_unc"] = unc
            r["head_length_mm"] = e["major_px"] * mmpp
            r["head_length_unc_mm"] = math.sqrt((e["major_px"] * unc) ** 2 + (3.0 * mmpp) ** 2)   # +-1.5 px per silhouette edge
            r["head_height_mm"] = e["minor_px"] * mmpp
            r["head_over_servo"] = e["major_px"] / sv["width_px"]
            r["head_length_dev_mm"] = r["head_length_mm"] - MESH_LEN
        res["halves"][key] = r
        # draw
        cx, cy = e["centre"]; a = e["major_px"] / 2; b = e["minor_px"] / 2
        ang = math.atan2(e["major_axis_dir"][1], e["major_axis_dir"][0])
        ux, uy = math.cos(ang), math.sin(ang); vx, vy = -uy, ux
        corners = [(cx + sx * a * ux + sy * b * vx, cy + sx * a * uy + sy * b * vy) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        d.polygon(corners, outline=(30, 90, 220), width=2)
        d.rectangle(half["servo_region"], outline=(230, 90, 20), width=1)
        for (x, y, aa, bb) in sv.get("lines", []):
            t = math.radians(sv["tilt_deg"]); px, py = math.cos(t), -math.sin(t)
            d.line([(x - aa * px, y - aa * py), (x + bb * px, y + bb * py)], fill=(230, 90, 20), width=1)
        if "width_px" in sv:
            d.text((corners[1][0] + 4, corners[1][1]), "%s: head %.1f px, servo %.1f px -> %.1f mm" % (key, e["major_px"], sv["width_px"], r["head_length_mm"]), fill=(0, 0, 0))
        else:
            d.text((corners[1][0] + 4, corners[1][1]), "%s: head %.1f px, servo width CANNOT DETERMINE (see json)" % (key, e["major_px"]), fill=(0, 0, 0))
        # the zoom: 4x crop with scan lines and the servo region, so the refusal can be checked by eye
        zx0, zy0, zx1, zy1 = half["zoom"]
        z = Image.fromarray(rgb.astype(np.uint8)).crop((zx0, zy0, zx1, zy1)).resize((4 * (zx1 - zx0), 4 * (zy1 - zy0)), Image.NEAREST)
        dz = ImageDraw.Draw(z)
        dz.rectangle([4 * (x0 - zx0), 4 * (y0 - zy0), 4 * (x1 - zx0), 4 * (y1 - zy0)], outline=(230, 90, 20), width=2)
        for (x, y, aa, bb) in sv.get("lines", []):
            t = math.radians(sv["tilt_deg"]); px, py = math.cos(t), -math.sin(t)
            dz.line([(4 * (x - aa * px - zx0), 4 * (y - aa * py - zy0)), (4 * (x + bb * px - zx0), 4 * (y + bb * py - zy0))], fill=(30, 120, 220), width=2)
        dz.text((6, 6), "%s  4x  orange = scan region, blue = accepted scan runs" % key, fill=(0, 0, 0))
        zooms.append(z)
    for key, r in res["halves"].items():
        e = r["head"]; r["aspect_major_over_minor"] = e["major_px"] / e["minor_px"]
        sv = r["servo"]
        if sv.get("verdict") == "CANNOT DETERMINE":
            r["scale_verdict"] = "CANNOT DETERMINE"; r["scale_why"] = sv["why"]
        elif "width_px" in sv and abs(sv["width_px"] - CASE_PX_EXPECTED) > 0.5 * CASE_PX_EXPECTED:
            # the run stopped at a bright pixel but is not a 20 mm case at this frame's scale: what it met is stated, and shown at 4x
            r["scale_verdict"] = "CANNOT DETERMINE"
            r["scale_why"] = ("the dark run of %.1f px ends on bright pixels inside the region, but a 20 mm case is ~%.0f px at this frame's scale "
                              "(head %.0f px ~ 123 mm): the run is more than the case — out/head/profile_frame_servo_zoom.png shows what it spans"
                              % (sv["width_px"], CASE_PX_EXPECTED, e["major_px"]))
            if key == "real":
                r["scale_why"] += (" — at 4x the left case edge is visible at x ~1905 but the right edge is behind the grey horn bracket "
                                   "(x ~1950-1995) and the cables, so the run is case + bracket")
            if key == "sim":
                r["scale_why"] += (" — at 4x the run spans the servo case AND the grey neck plate beside it: both are unsaturated greys of the "
                                   "same luminance in this render, so no threshold separates them")
            for k in ("mm_per_px", "mm_per_px_unc", "head_length_mm", "head_length_unc_mm", "head_height_mm", "head_over_servo", "head_length_dev_mm"):
                r.pop(k, None)
        elif "width_px" in sv:
            r["scale_verdict"] = "PASS"; r["scale_why"] = "run of %.1f px ends on bright pixels on both sides inside the region, %d of %d lines at the mode" % (sv["width_px"], sv["n_accepted"], sv["n_lines"])
    a, b = res["halves"].get("real", {}), res["halves"].get("sim", {})
    if "aspect_major_over_minor" in a and "aspect_major_over_minor" in b:
        res["aspect_real"] = a["aspect_major_over_minor"]; res["aspect_sim"] = b["aspect_major_over_minor"]
        res["aspect_real_over_sim"] = a["aspect_major_over_minor"] / b["aspect_major_over_minor"]
        res["aspect_reading"] = ("scale-free: head silhouette major/minor, real %.4f vs Pollen's render of these meshes %.4f (ratio %.4f); "
                                 "the two halves are not the same pose (head pitch %.1f vs %.1f deg in the image), so this is a coarse "
                                 "check, not a dimension" % (res["aspect_real"], res["aspect_sim"], res["aspect_real_over_sim"], a["head_axis_deg"], b["head_axis_deg"]))
    if "head_over_servo" in a and "head_over_servo" in b:
        res["real_over_sim"] = a["head_over_servo"] / b["head_over_servo"]
        res["real_over_sim_unc"] = res["real_over_sim"] * math.sqrt((a["servo"]["width_px_unc"] / a["servo"]["width_px"]) ** 2 + (b["servo"]["width_px_unc"] / b["servo"]["width_px"]) ** 2 + 2 * (3.0 / a["head"]["major_px"]) ** 2)
        res["reading"] = ("real/sim head-length-to-servo ratio %.4f ± %.4f; real head length %.2f ± %.2f mm against the mesh's %.3f "
                          "(Pollen's own render reads %.2f mm by the same method — the method's check)" % (
                              res["real_over_sim"], res["real_over_sim_unc"], a["head_length_mm"], a["head_length_unc_mm"], MESH_LEN, b["head_length_mm"]))
    elif "head_length_mm" in b:
        res["method_check"] = ("Pollen's own render of these meshes reads %.2f ± %.2f mm by this method against the mesh's %.3f mm (%+.2f mm): the "
                               "estimator's check on a frame whose head length is known; the real half stays CANNOT DETERMINE (%s)" % (
                                   b["head_length_mm"], b["head_length_unc_mm"], MESH_LEN, b["head_length_mm"] - MESH_LEN, a.get("scale_why", "")))
    json.dump(res, open(os.path.join(OUT, "profile_frame.json"), "w"), indent=1, default=float)
    im.save(os.path.join(OUT, "profile_frame_pair.png"))
    # zoom sheet: real | sim
    W = sum(z.size[0] for z in zooms) + 30; H = max(z.size[1] for z in zooms) + 10
    sheet = Image.new("RGB", (W, H), (255, 255, 255)); x = 10
    for z in zooms: sheet.paste(z, (x, 5)); x += z.size[0] + 10
    sheet.save(os.path.join(OUT, "profile_frame_servo_zoom.png"))
    print(json.dumps({k: v for k, v in res.items() if k not in ("method",)}, indent=1, default=float)[:3500])


if __name__ == "__main__":
    main()
