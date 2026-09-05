#!/usr/bin/env python3
"""plate_for_printer.py — bin-pack printed parts onto plates that FIT a given
machine, slice each plate for real, and refuse rather than silently overflow.

Why this exists: out/print/plates/*.3mf were sliced for a Bambu H2S (340x320).
The machine actually on the LAN is an X1 Carbon (256x256). Handing the H2S plate
to the X1C returns BambuStudio error -52, "Some objects are located over the
boundary of the heated bed" — a real failure, not a warning.

Strategy: greedy bin-pack by projected footprint under a fill target, slice each
group, and on -52 SPLIT that group and retry. The fill target is a search
parameter, not a constant: auto-orient rotates parts, so a pre-orientation
footprint is an estimate and the slicer is the only authority.
"""
import json, os, struct, subprocess, sys, tempfile

BS = "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"
PROF = "/Applications/BambuStudio.app/Contents/Resources/profiles/BBL"


def footprint(path):
    with open(path, "rb") as f:
        f.read(80); n = struct.unpack("<I", f.read(4))[0]
        xs = []; ys = []
        for _ in range(n):
            d = f.read(50)
            for i in range(3):
                x, y, _z = struct.unpack("<3f", d[12 + i * 12:24 + i * 12])
                xs.append(x); ys.append(y)
    return (max(xs) - min(xs)) * (max(ys) - min(ys))


def slice_group(files, machine, process, filament, out3mf, outdir):
    os.makedirs(outdir, exist_ok=True)
    cmd = [BS,
           "--load-settings", "%s;%s" % (machine, process),
           "--load-filaments", filament,
           "--arrange", "1", "--orient", "1", "--allow-rotations", "--ensure-on-bed",
           "--slice", "0", "--export-3mf", out3mf, "--outputdir", outdir] + files
    subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    rj = os.path.join(outdir, "result.json")
    if not os.path.exists(rj):
        return None, "no result.json"
    r = json.load(open(rj))
    made = os.path.join(outdir, out3mf)
    if r.get("return_code") == 0 and os.path.exists(made):
        return r, None
    return None, r.get("error_string", "return_code %s" % r.get("return_code"))


def pack(files, bed_area, fill):
    items = sorted(((footprint(f), f) for f in files), reverse=True)
    plates = []
    for a, f in items:
        for p in plates:
            if p["area"] + a <= bed_area * fill:
                p["files"].append(f); p["area"] += a; break
        else:
            plates.append({"files": [f], "area": a})
    return [p["files"] for p in plates]


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--stl-dir", required=True)
    ap.add_argument("--machine", required=True)
    ap.add_argument("--process", required=True)
    ap.add_argument("--filament", required=True)
    ap.add_argument("--bed", required=True, help="WxH in mm, e.g. 256x256")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--prefix", default="plate")
    ap.add_argument("--dup", default="", help="comma-separated slugs to place twice")
    ap.add_argument("--fill", type=float, default=0.50)
    a = ap.parse_args()

    W, H = (float(x) for x in a.bed.lower().split("x"))
    files = sorted(os.path.join(a.stl_dir, f) for f in os.listdir(a.stl_dir) if f.endswith(".stl"))
    for slug in [s for s in a.dup.split(",") if s]:
        p = os.path.join(a.stl_dir, slug + ".stl")
        if os.path.exists(p): files.append(p)
    print("%d objects, bed %.0fx%.0f = %.0f mm2, fill target %.0f%%"
          % (len(files), W, H, W * H, 100 * a.fill))

    queue = pack(files, W * H, a.fill)
    done = []; n = 0
    while queue:
        grp = queue.pop(0)
        n += 1
        name = "%s-%02d.3mf" % (a.prefix, len(done) + 1)
        r, err = slice_group(grp, a.machine, a.process, a.filament, name, a.outdir)
        if err:
            if len(grp) == 1:
                print("  REFUSED %s: a single object does not fit — %s" % (os.path.basename(grp[0]), err))
                continue
            mid = len(grp) // 2
            print("  plate of %d overflowed (%s) -> splitting %d/%d" % (len(grp), err, mid, len(grp) - mid))
            queue.insert(0, grp[mid:]); queue.insert(0, grp[:mid])
            continue
        done.append((name, grp, r))
        print("  %s  %2d objects  layer %.2f mm  OK" % (name, len(grp), r.get("layer_height", 0)))
    print("\n%d plate(s) sliced into %s after %d attempts" % (len(done), a.outdir, n))
    for name, grp, r in done:
        print("  %s: %s" % (name, ", ".join(os.path.basename(g)[:28] for g in grp)))
    json.dump({"plates": [{"file": nm, "objects": [os.path.basename(g) for g in grp]} for nm, grp, _ in done]},
              open(os.path.join(a.outdir, "plates.json"), "w"), indent=2)
    return 0 if done else 1


if __name__ == "__main__":
    sys.exit(main())
