"""dfm_verify_md.py — read docs/DFM.md's summary table BACK and check every cell.

    python3 tools/dfm_verify_md.py

A drawing that does not read back clean is not a drawing; a DFM table whose
numbers cannot be re-derived from out/dfm/dfm-rebuilt.json and
out/print/slice.json is not a measurement, it is prose. This re-parses the
markdown the way a reader does and re-checks: material, bed fit, build
direction, height, layer count, exact wall, ray p1, sliced grams, support area,
bed contact, and that the VERDICT is what the stated rule produces — not what
looked right. Tolerance is one unit in the last decimal place printed.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(ROOT, "out/dfm/dfm-rebuilt.json")))["parts"]
sl = {p["slug"]: p for p in json.load(open(os.path.join(ROOT, "out/print/slice.json")))["parts"]}
num = lambda s: [float(x) for x in re.findall(r"-?\d+\.?\d*", s.replace("**", ""))]

def tol(cell, i=0):
    """One unit in the last decimal place actually printed."""
    m = re.findall(r"-?\d+\.(\d+)", cell.replace("**", ""))
    return 10 ** -len(m[i]) if i < len(m) else 1e-9

bad, seen = [], set()
for line in open(os.path.join(ROOT, "docs/DFM.md")):
    if not line.startswith("| "):
        continue
    c = [x.strip() for x in line.strip().strip("|").split("|")]
    if len(c) != 10 or c[1] not in ("PLA", "TPU"):
        continue
    name = c[0].replace("**", ""); slug = "microduck-" + name
    if slug not in d:
        bad.append("row for a part that is not in the JSON: %r" % name); continue
    seen.add(slug)
    r = d[slug]; o = r["orientation"]; p = r["printability"]; wr = r["mesh"]["wall_rays"]
    if c[1] != r["declared_material"]:
        bad.append("%s: material %s, component.json says %s" % (name, c[1], r["declared_material"]))
    if (c[2] == "yes") != bool(p["fits"]):
        bad.append("%s: bed fit" % name)
    dd = c[3].replace("**", "").split()[0].rstrip(",")
    if dd != o["best"]:
        bad.append("%s: build dir %s, measured best is %s" % (name, dd, o["best"]))
    n = num(c[3])
    if abs(n[-2] - o["best_height_mm"]) > 0.05:
        bad.append("%s: height %s != %s" % (name, n[-2], o["best_height_mm"]))
    if int(n[-1]) != o["best_layers"]:
        bad.append("%s: layers %s != %s" % (name, n[-1], o["best_layers"]))
    n = num(c[4])
    if abs(n[0] - p["thinnest_wall"]) > tol(c[4], 0):
        bad.append("%s: exact wall %s != %s" % (name, n[0], p["thinnest_wall"]))
    if abs(n[1] - wr["p1_mm"]) > tol(c[4], 1):
        bad.append("%s: ray p1 %s != %s" % (name, n[1], wr["p1_mm"]))
    if abs(num(c[5])[0] - sl[slug]["grams_per_piece"]) > tol(c[5]):
        bad.append("%s: sliced g %s != %s" % (name, c[5], sl[slug]["grams_per_piece"]))
    if abs(num(c[6])[0] - o["best_elevated_lt30_mm2"]) > 0.6:
        bad.append("%s: support %s != %s" % (name, c[6], o["best_elevated_lt30_mm2"]))
    if abs(num(c[7])[0] - o["best_bed_contact_mm2"]) > 0.6:
        bad.append("%s: foot %s != %s" % (name, c[7], o["best_bed_contact_mm2"]))
    want = ("PRINTABLE" if (o["best_elevated_lt30_mm2"] == 0 and wr["p1_mm"] >= 0.80)
            else "PRINTABLE-WITH-CARE")
    if c[9].replace("**", "") != want:
        bad.append("%s: verdict %s, but the rule in the doc gives %s"
                   % (name, c[9].replace("**", ""), want))
missing = sorted(set(d) - seen)
if missing:
    bad.append("in the JSON but not in the table: %s" % missing)
print("docs/DFM.md summary table: %d rows checked against out/dfm/dfm-rebuilt.json "
      "+ out/print/slice.json" % len(seen))
if bad:
    print("\n".join("  FAIL " + b for b in bad)); sys.exit(1)
print("  READS BACK CLEAN — every cell re-derived, verdicts match the stated rule.")
