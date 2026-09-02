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
                the horn/label face — the same face as in the store photographs)
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
upper bound on the product head length if any yaw remains.

Writes out/head/profile_frame.json and out/head/profile_frame_pair.png.
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

HALVES = {
    "real": dict(region=(1600, 20, 2215, 330), mode="real",
                 servo=dict(rows=(275, 335), seed_x=1930, tilt_deg=-8.0, what="upper neck servo (head_pitch), horn/label face"),
                 note="real sky unit, right half of the frame"),
    "sim": dict(region=(330, 20, 720, 230), mode="sim",
                servo=dict(rows=(235, 300), seed_x=505, tilt_deg=-12.0, what="upper neck servo in Pollen's render"),
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


def main():
    rgb = hp.load_rgb(os.path.join(REPO, IMG))
    res = dict(generated=time.strftime("%Y-%m-%d %H:%M"), method=__doc__, image=IMG, size_px=[int(rgb.shape[1]), int(rgb.shape[0])],
               mesh_head_length_mm=MESH_LEN, servo_mm=SERVO_MM, servo_source=hp.XL330_SRC, halves={})
    im = Image.fromarray(rgb.astype(np.uint8)); d = ImageDraw.Draw(im)
    for key, half in HALVES.items():
        m = head_mask(rgb, half); ys, xs = np.nonzero(m)
        e = hp.ellipse_of(np.stack([xs, ys], 1).astype(float))
        sv = hp.measure_servo(rgb, dict(half["servo"], geom="neck_upper"), thresh=95)
        r = dict(note=half["note"], region=list(half["region"]), head=e, head_bbox=[int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
                 head_axis_deg=math.degrees(math.atan2(e["major_axis_dir"][1], e["major_axis_dir"][0])), servo=sv)
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
        for t in np.linspace(0, 2 * math.pi, 120):
            pass
        ux, uy = math.cos(ang), math.sin(ang); vx, vy = -uy, ux
        corners = [(cx + sx * a * ux + sy * b * vx, cy + sx * a * uy + sy * b * vy) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        d.polygon(corners, outline=(30, 90, 220), width=2)
        for (x, y, aa, bb) in sv.get("lines", []):
            t = math.radians(sv["tilt_deg"]); px, py = math.cos(t), -math.sin(t)
            d.line([(x - aa * px, y - aa * py), (x + bb * px, y + bb * py)], fill=(230, 90, 20), width=1)
        if "width_px" in sv:
            d.text((corners[1][0] + 4, corners[1][1]), "%s: head %.1f px, servo %.1f px -> %.1f mm" % (key, e["major_px"], sv["width_px"], r["head_length_mm"]), fill=(0, 0, 0))
    for key, r in res["halves"].items():
        e = r["head"]; r["aspect_major_over_minor"] = e["major_px"] / e["minor_px"]
        # the neck servo in this 884-px video frame is ~45 px wide and merges with the grey horn bracket and the cables in
        # luminance (scratchpad profile: an 80+ px dark run at every row) — the case edge is not resolvable, so no mm/px here
        sv = r["servo"]
        if "width_px" in sv and sv["width_px"] > 60:
            r["scale_verdict"] = "CANNOT DETERMINE"
            r["scale_why"] = ("dark run %.1f px is the servo + horn bracket + cables merged (a 20 mm case would be ~45 px at this "
                              "frame's scale); the frame cannot resolve the case edge" % sv["width_px"])
            for k in ("mm_per_px", "mm_per_px_unc", "head_length_mm", "head_length_unc_mm", "head_height_mm", "head_over_servo", "head_length_dev_mm"):
                r.pop(k, None)
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
    json.dump(res, open(os.path.join(OUT, "profile_frame.json"), "w"), indent=1, default=float)
    im.save(os.path.join(OUT, "profile_frame_pair.png"))
    print(json.dumps({k: v for k, v in res.items() if k not in ("method",)}, indent=1, default=float)[:3000])


if __name__ == "__main__":
    main()
