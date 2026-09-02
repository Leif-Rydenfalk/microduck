#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""render_sweep_videos.py — one video per cell family of the lane-F2 gait sweep,
rendered from the SAVED TRAJECTORY of that cell and read back frame by frame.

Why this file exists: out/sim-sweep/videos.json used to be produced by an ad-hoc
invocation that lived only in a shell history, so it could not be regenerated and
it silently went stale when the sweep was re-run. It is a generated artifact now.

Each entry records what render_video.render_traj() MEASURED off its own output —
frame count, mean intensity of the first and last frame, mean interframe
difference, and the byte size and frame count read back out of the .mp4 — so a
blank or truncated video cannot be filed as a success.

Run:  ce-cad/bin/cad sim/render_sweep_videos.py            # every family
      ce-cad/bin/cad sim/render_sweep_videos.py --only walk_selfcontact
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import render_video  # noqa: E402

ROOT = common.ROOT
SWEEP = os.path.join(ROOT, "out", "sim-sweep")
VID = os.path.join(SWEEP, "video")

# one cell per family — the cell whose _traj.npz sim/gait_sweep.py saves
CELLS = [
    ("base_walk_vx0.25", "walk vx 0.25 m/s - the reference cell"),
    ("vx_0.60", "vx 0.60 m/s - fastest command that stayed upright"),
    ("mass_m110", "total mass +10 %"),
    ("mu_0.40", "foot+floor sliding friction 0.40"),
    ("slope5_up", "5 deg slope, uphill commanded - it turns and walks DOWN"),
    ("push_5N_lat", "5 N lateral push for 0.2 s at t=6.0 s - falls at 6.46 s"),
    ("sitstand", "sit at 1.0 s, stand at 4.5 s"),
    ("stand_hold", "stand policy holding the pose"),
    ("walk_selfcontact", "self-collision census model - all 15 bodies collidable, 2187 candidate pairs"),
    ("push_5N_lat_fullcontact", "5 N push on the model where every geom also meets the floor"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None, help="comma-separated cell names")
    ap.add_argument("--fps", type=float, default=10.0)
    ap.add_argument("--size", default="640x480")
    a = ap.parse_args()
    size = tuple(int(x) for x in a.size.split("x"))
    want = set(a.only.split(",")) if a.only else None
    os.makedirs(VID, exist_ok=True)
    path = os.path.join(SWEEP, "videos.json")
    videos = json.load(open(path)) if os.path.exists(path) else {}
    for cell, label in CELLS:
        if want and cell not in want:
            continue
        tp = os.path.join(SWEEP, cell + "_traj.npz")
        if not os.path.exists(tp):
            print("MISSING trajectory, skipped:", os.path.relpath(tp, ROOT))
            continue
        # purge this cell's OLD frames first: a frame left behind by an earlier render has a
        # different trajectory's provenance even when the physics is deterministic, and the
        # page lists whatever is on disk.
        fdir = os.path.join(SWEEP, "frames")
        for f in (os.listdir(fdir) if os.path.isdir(fdir) else []):
            if f.startswith(cell + "_t") and f.endswith(".png"):
                os.remove(os.path.join(fdir, f))
        rec = render_video.render_traj(tp, mp4=os.path.join(VID, cell + ".mp4"), fps=a.fps, size=size,
                                       png_dir=os.path.join(SWEEP, "frames"), label=label)
        rec["label"] = label
        rec["traj"] = os.path.relpath(tp, ROOT)
        videos[cell] = rec
        mp4 = rec.get("mp4") or {}
        print("%-26s frames=%-4s read_back=%-4s bytes=%-9s mean_diff=%s"
              % (cell, rec.get("frames"), mp4.get("frames_read_back"), mp4.get("bytes"),
                 rec.get("mean_interframe_diff")))
        assert rec.get("frames", 0) > 1, cell
        assert rec.get("mean_interframe_diff", 0) > 0.05, (cell, "video does not move")
    json.dump(videos, open(path, "w"), indent=1)
    print("wrote", os.path.relpath(path, ROOT), "-", len(videos), "cells")


if __name__ == "__main__":
    main()
