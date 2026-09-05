#!/usr/bin/env python3
"""plate_for_printer.py — plate the printed parts for a given machine with
BambuStudio, driven the way ce-slice drives it.

DO NOT hand a leaf preset to `--load-filaments`. ce_slice.py's own header says why,
and this file exists because I did it anyway:

    "The CLI applies only the keys literally present in the file it is handed. It
     does NOT resolve `inherits`. ... Hand the leaf straight to --load-filaments and
     the slicer reports filament_settings_id = <leaf> (the preset WAS loaded) with
     filament_density = 0 ... That is the entire root cause of every 0.00 g slice."

Six plates were sliced that way. Every one carried `tray_info_idx=""` and
`used_g="0.00"`, the printer had no filament identity to bind an AMS tray to, and
the job ran at temperature with tray_now=255 and fed nothing. The slicer reported
success throughout.

So: presets are flattened through `ce_slice.presets().flatten()` — the project's
own resolver — and BambuStudio does the arranging across as many plates as it
needs. Nothing here reimplements slicing or packing.
"""
import argparse, json, os, re, subprocess, sys, tempfile, zipfile

BS = "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"
CE_SLICE = os.path.expanduser("~/dev/ce-slice")


def flat_presets(work, machine, process, filament):
    sys.path.insert(0, CE_SLICE)
    import ce_slice as CS
    globals()['CS'] = CS
    idx = CS.presets()
    try: idx.build()
    except Exception: pass
    out = {}
    for kind, name in (("machine", machine), ("process", process), ("filament", filament)):
        d = idx.flatten(kind, name)
        if not d:
            raise SystemExit("preset not found: %s / %s" % (kind, name))
        d = dict(d); d["name"] = name; d["from"] = "system"
        dens = d.get("filament_density")
        if kind == "filament":
            v = dens[0] if isinstance(dens, list) else dens
            if not v or float(v) <= 0:
                raise SystemExit("REFUSED: %s flattens to density %r — a 0 g slice would follow" % (name, dens))
            print("  filament %s  id=%s density=%s" % (name, d.get("filament_id"), v))
        out["_" + kind] = d
        p = os.path.join(work, kind + ".json")
        json.dump(d, open(p, "w"), indent=1)
        out[kind] = p

    # SECOND documented trap, also from ce_slice.py's header: no shipped process
    # preset carries `curr_bed_type`, so the slicer assumes Cool Plate and refuses
    # PETG/ABS/PA with return_code -61 "Filaments are not compatible with the plate
    # type." ce-slice's _bed_type reads the plate temperatures out of the FILAMENT
    # preset instead of hardcoding one, and distinguishes "declares zero for every
    # plate" from "declares no plate at all" — the second is our flattening bug, not
    # an unprintable filament.
    bed, why = CS._bed_type(out["_filament"])
    if bed is None:
        raise SystemExit("REFUSED: no plate type for %s — %s" % (filament, why))
    proc = dict(out["_process"]); proc["curr_bed_type"] = bed
    json.dump(proc, open(out["process"], "w"), indent=1)
    print("  bed type %s  (%s)" % (bed, why))
    return out


def verify(path):
    """A slicer exit code of 0 is a claim. The evidence is inside the 3mf."""
    z = zipfile.ZipFile(path)
    si = [n for n in z.namelist() if n.endswith("slice_info.config")]
    if not si: return [("no slice_info.config", False)]
    t = z.read(si[0]).decode("utf-8", "ignore")
    rows = []
    for m in re.finditer(r'<filament\s+id="(\d+)"\s+tray_info_idx="([^"]*)"[^>]*used_m="([^"]*)"\s+used_g="([^"]*)"', t):
        idx, um, ug = m.group(2), float(m.group(3)), float(m.group(4))
        rows.append((("tray_info_idx=%r used_m=%.2f used_g=%.2f" % (idx, um, ug)), bool(idx) and ug > 0))
    plates = len(set(re.findall(r'<plate>', t))) or len([n for n in z.namelist() if re.search(r'plate_\d+\.gcode$', n)])
    return rows, plates


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stl-dir", required=True)
    ap.add_argument("--machine", default="Bambu Lab X1 Carbon 0.4 nozzle")
    ap.add_argument("--process", default="0.20mm Standard @BBL X1C")
    ap.add_argument("--filament", required=True, help="preset NAME, flattened here")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--out", default="plate.3mf")
    ap.add_argument("--dup", default="")
    ap.add_argument("--orient", type=int, default=1)
    ap.add_argument("--only", default="", help="comma-separated slugs; default all")
    a = ap.parse_args()

    files = sorted(os.path.join(a.stl_dir, f) for f in os.listdir(a.stl_dir) if f.endswith(".stl"))
    if a.only:
        keep = set(a.only.split(","))
        files = [f for f in files if os.path.basename(f)[:-4] in keep]
    for slug in [s for s in a.dup.split(",") if s]:
        p = os.path.join(a.stl_dir, slug + ".stl")
        if os.path.exists(p) and p in files: files.append(p)

    os.makedirs(a.outdir, exist_ok=True)
    work = tempfile.mkdtemp(prefix="plate-")
    print("%d objects -> %s" % (len(files), a.out))
    pr = flat_presets(work, a.machine, a.process, a.filament)
    cmd = [BS, "--load-settings", "%s;%s" % (pr["machine"], pr["process"]),
           "--load-filaments", pr["filament"], "--arrange", "1", "--ensure-on-bed",
           "--slice", "0", "--export-3mf", a.out, "--outputdir", a.outdir]
    if a.orient: cmd += ["--orient", "1", "--allow-rotations"]
    cmd += files
    subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    rj = os.path.join(a.outdir, "result.json")
    r = json.load(open(rj)) if os.path.exists(rj) else {}
    made = os.path.join(a.outdir, a.out)
    if r.get("return_code") != 0 or not os.path.exists(made):
        print("  SLICER REFUSED: %s (rc=%s)" % (r.get("error_string"), r.get("return_code")))
        return 1
    rows, plates = verify(made)
    print("  sliced: %d plate(s) inside the 3mf" % plates)
    ok = True
    for desc, good in rows:
        print("   %s  %s" % ("OK  " if good else "BAD ", desc)); ok &= good
    print("  VERDICT: %s" % ("PASS — filament identity and mass are both present"
                             if ok else "FAIL — the plate would print with no filament bound"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
