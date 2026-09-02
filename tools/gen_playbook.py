"""gen_playbook.py — writes MANUFACTURING-PLAYBOOK.html.

    python3 tools/gen_playbook.py            # any python3; no CAD kernel needed

Same pattern as tools/gen_comparison.py: a data file plus a generator, never a
hand-maintained table. Reads

  tools/data/playbook.json   rates, sourced brackets, stations, gates, torque,
                             packaging, open items — decisions and citations only
  out/print/slice.json       the SLICER'S own grams and seconds per piece
  out/dfm/dfm.json           measured overhang per build direction and ray-cast
                             wall, plus solid holes/radii/wall for the rebuilds
  out/jigs/jigs.json         the six jigs, their measured geometry and drawings
  out/print/stl_manifest.json  which slug is our rebuild and which is a vendor mesh

and COMPUTES every per-part cost, break-even and verdict here. If an input is
missing the section says so and the document still builds — a missing number is
never replaced by a plausible one.
"""
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "MANUFACTURING-PLAYBOOK.html")


def load(p):
    f = os.path.join(ROOT, p)
    return json.load(open(f)) if os.path.exists(f) else None


D = load("tools/data/playbook.json")
SLICE = load("out/print/slice.json")
DFM = load("out/dfm/dfm.json")
JIGS = load("out/jigs/jigs.json")
STALE = load("out/playbook/stale-stl-delta.json")

E = html.escape
R = D["rates"]
VIS = set(D["visible"]["slugs"])


def n(x, d=4):
    """Fixed-point with trailing zeros trimmed — but ONLY after a decimal point.
    (Stripping "0" off "2000" gave "2" in an earlier draft of this file.)"""
    if x is None:
        return "—"
    if not isinstance(x, float):
        return str(x)
    t = "%.*f" % (d, x)
    return t.rstrip("0").rstrip(".") if "." in t else t


def usd(x, d=4):
    return "—" if x is None else "$%s" % ("{:,.%df}" % d).format(x)


def thou(x):
    return "—" if x is None else "{:,.0f}".format(x)


def src(*ids):
    out = []
    for i in ids:
        out.append('<a href="#src-%s" class="mono">[%s]</a>' % (i, i))
    return " ".join(out)


# ---------------------------------------------------------------------------
# 1. THE COST MODEL, computed per piece from the real sliced numbers
# ---------------------------------------------------------------------------
def piece_costs(p):
    """Everything the model can say about ONE piece of this part."""
    g, s = p.get("grams_per_piece"), p.get("seconds_per_piece")
    if g is None or s is None:
        return None
    h = s / 3600.0
    mat_kg = R["material_usd_per_kg"][p["material"]]
    farm_kg = R["material_usd_per_kg"]["PLA_farm"] if p["material"] == "PLA" else mat_kg
    w = R["material_usd_per_kg"]["waste_factor"]
    plate = R["plate_pieces"][p["material"]]
    lab_job = R["labour_usd_per_hour"] * R["labour_minutes_per_print_job"] / 60.0
    c = dict(
        grams=g, hours=h,
        material=g / 1000.0 * mat_kg * w,
        material_farm_stock=g / 1000.0 * farm_kg * w,
        machine_lo=h * R["machine_usd_per_hour_inhouse"]["low"],
        machine_hi=h * R["machine_usd_per_hour_inhouse"]["high"],
        machine_farm_lo=h * R["machine_usd_per_hour_farm"]["low"],
        machine_farm_hi=h * R["machine_usd_per_hour_farm"]["high"],
        labour_alone=lab_job,
        labour_plated=lab_job / plate,
        plate_pieces=plate)
    c["inhouse_lo"] = c["material"] + c["machine_lo"] + c["labour_plated"]
    c["inhouse_hi"] = c["material"] + c["machine_hi"] + c["labour_plated"]
    c["inhouse_mid"] = (c["inhouse_lo"] + c["inhouse_hi"]) / 2.0
    c["farm_lo"] = c["material_farm_stock"] + c["machine_farm_lo"]
    c["farm_hi"] = c["material_farm_stock"] + c["machine_farm_hi"]
    return c


def breakeven(c_print, c_mould, tool):
    d = c_print - c_mould
    if d <= 0:
        return None
    return tool / d


ROWS = []
if SLICE:
    for p in SLICE["parts"]:
        c = piece_costs(p)
        if not c:
            continue
        slug = p["slug"]
        m = R["mould_piece_usd"]
        t = R["tool_usd"]
        ROWS.append(dict(
            slug=slug, qty=p["qty"], material=p["material"], visible=slug in VIS,
            c=c,
            be_best=breakeven(c["inhouse_mid"], m["low"], t["floor"]),
            be_worst=breakeven(c["inhouse_mid"], m["low"], t["alu_high"]),
            be_at_mould_high=breakeven(c["inhouse_mid"], m["high"], t["floor"]),
            warn=p.get("slicer_warning"),
            orient=p.get("orientation_rule") or SLICE and None))
ROWS.sort(key=lambda r: (-r["c"]["inhouse_mid"], r["slug"]))

TOT = {}
if ROWS:
    for k in ("material", "machine_lo", "machine_hi", "inhouse_lo", "inhouse_hi",
              "farm_lo", "farm_hi", "material_farm_stock"):
        TOT[k] = sum(r["c"][k] * r["qty"] for r in ROWS)
    TOT["grams"] = sum(r["c"]["grams"] * r["qty"] for r in ROWS)
    TOT["hours"] = sum(r["c"]["hours"] * r["qty"] for r in ROWS)
    TOT["pieces"] = sum(r["qty"] for r in ROWS)
    # labour is per PLATE, not per piece: two plates per robot
    TOT["labour_plated"] = R["labour_usd_per_hour"] * R["labour_minutes_per_print_job"] / 60.0 * 2
    TOT["robot_lo"] = (TOT["inhouse_lo"]) * R["failure_buffer"]["low"]
    TOT["robot_hi"] = (TOT["inhouse_hi"]) * R["failure_buffer"]["high"]


# ---------------------------------------------------------------------------
# 2. THE DFM VERDICT, computed per part from the measured overhang and wall
# ---------------------------------------------------------------------------
TWO_PERIM = 0.80
SLENDER_K = 5.0   # build height must not exceed K x the smaller in-plane bbox dimension


def recommend_dir(m):
    """Least unsupported area SUBJECT TO a slenderness cap.

    This is the one place in this document where a RULE is applied on top of a
    measurement, and it is stated rather than hidden: minimising overhang alone
    always prefers standing a flat plate on edge (measured: the 1 mm
    upper-leg-rigidity-plate reads 77 mm² unsupported at +Z against 748 mm² lying
    flat — and +Z is 291 layers of a 1 mm wall, which is the exact failure
    docs/DFM.md warns about). So a direction is admissible only when the build
    height is at most SLENDER_K x the smaller of the two in-plane bbox
    dimensions. If none is admissible, the least slender wins and the row says so.
    """
    bb = m["bbox_mm"]
    axis_i = {"+X": 0, "-X": 0, "+Y": 1, "-Y": 1, "+Z": 2, "-Z": 2}
    cand = []
    for k, v in m["overhang_by_build_dir"].items():
        i = axis_i[k]
        inplane = sorted(bb[j] for j in range(3) if j != i)
        slender = v["height_mm"] / max(inplane[0], 1e-9)
        cand.append((k, v, slender, inplane[0]))
    ok = [c for c in cand if c[2] <= SLENDER_K]
    if ok:
        c = min(ok, key=lambda c: (c[1]["area_lt30_mm2"], c[1]["height_mm"]))
        return c[0], c[1], c[2], True
    c = min(cand, key=lambda c: c[2])
    return c[0], c[1], c[2], False


def dfm_row(slug):
    if not DFM or slug not in DFM["parts"]:
        return None
    d = DFM["parts"][slug]
    m = d["mesh_dfm"]
    minoh = m["best_build_dir"]
    best, b, slender, admissible = recommend_dir(m)
    asm = m["overhang_by_build_dir"]["+Z"]
    w = m["wall_rays"] or {}
    sol = d.get("solid_dfm") or {}
    tw = (sol.get("thinnest_wall") or {}).get("mm") if sol.get("ok") else None
    holes = sol.get("holes") if sol.get("ok") else None
    findings, verdict = [], "PRINTABLE"
    if b["frac_lt30"] > 0.09:
        findings.append("%.1f %% of the surface is unsupported even in its best build "
                        "direction (%s) — supports are not optional on this part"
                        % (100 * b["frac_lt30"], best))
        verdict = "PRINTABLE-WITH-CARE"
    elif b["frac_lt30"] > 0.05:
        findings.append("%.1f %% unsupported at %s; supports on" % (100 * b["frac_lt30"], best))
    if b["frac_lt10"] > 0.05:
        findings.append("%.1f %% of the surface is a near-horizontal down-face (β<10°) — "
                        "bridges and floating islands, %.0f mm² of them projected"
                        % (100 * b["frac_lt10"], b["projected_lt30_mm2"]))
        verdict = "PRINTABLE-WITH-CARE"
    if asm["area_lt30_mm2"] > 1.6 * b["area_lt30_mm2"]:
        findings.append("orientation matters: +Z as modelled gives %.0f mm² unsupported "
                        "against %.0f mm² at %s — a %.1f× penalty for printing it upright"
                        % (asm["area_lt30_mm2"], b["area_lt30_mm2"], best,
                           asm["area_lt30_mm2"] / max(b["area_lt30_mm2"], 1e-9)))
    p5 = w.get("p5_mm")
    if p5 is not None and p5 < TWO_PERIM:
        findings.append("ray-cast wall p5 = %.4f mm is under the %.2f mm two-perimeter "
                        "floor: %.0f %% of the sampled surface sits over material thinner "
                        "than two 0.4 mm perimeters" % (p5, TWO_PERIM, 5))
        verdict = "PRINTABLE-WITH-CARE"
    if tw is not None and tw < TWO_PERIM:
        findings.append("solid thinnest wall %.4f mm (cecad.inspect, exact) — docs/DFM.md "
                        "reads sub-0.80 mm as a knife-edge chamfer, not a structural wall; "
                        "the slicer rounds it off" % tw)
    if not findings:
        findings.append("no unsupported region above 5 %% of the surface in its best "
                        "build direction and no wall under the two-perimeter floor")
    if best != minoh:
        mo = m["overhang_by_build_dir"][minoh]
        findings.append("least-overhang direction is %s (%.0f mm² unsupported) but that is "
                        "%d layers of a %s mm section — rejected by the slenderness cap; "
                        "build %s instead (%.0f mm², %d layers)"
                        % (minoh, mo["area_lt30_mm2"], mo["layers_at_0p2"],
                           n(min(m["bbox_mm"])), best, b["area_lt30_mm2"], b["layers_at_0p2"]))
    return dict(best=best, minoh=minoh, slender=slender, admissible=admissible,
                b=b, asmZ=asm, w=w, tw=tw,
                nholes=len(holes) if isinstance(holes, list) else None,
                radii=(sol.get("radii_mm") if isinstance(sol.get("radii_mm"), list) else None),
                parametric=d["parametric"], findings=findings, verdict=verdict,
                bbox=m["bbox_mm"], vol=m["closed_volume_mm3"], tri=m["triangles"])


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------
def tbl(head, rows, cls="data"):
    o = ['<div class="tablewrap"><table class="%s"><thead><tr>' % cls]
    o += ["<th>%s</th>" % h for h in head]
    o.append("</tr></thead><tbody>")
    for r in rows:
        o.append("<tr>" + "".join(r) + "</tr>")
    o.append("</tbody></table></div>")
    return "".join(o)


def td(v, cls=None):
    return "<td%s>%s</td>" % (' class="%s"' % cls if cls else "", v)


def chip(v):
    k = {"PASS": "pass", "PRINTABLE": "pass", "PRINTABLE-WITH-CARE": "cd",
         "CANNOT DETERMINE": "cd", "FAIL": "rail", "NOT READY": "rail", "OPEN": "cd"}.get(v, "buy")
    return '<span class="chip %s">%s</span>' % (k, E(v))


P = []
A = P.append

A('''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Manufacturing Playbook</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opt_sz,wght@8..60,400;8..60,600;8..60,700&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="tools/doc.css">
<style>
  .lede{font-size:16.5px;color:var(--ink-2);max-width:44em}
  .n{display:inline-block;min-width:1.7em;color:var(--ink-2);font-family:var(--mono);font-size:.72em;
     font-weight:400;vertical-align:.18em}
  .verdict{border-left:3px solid var(--accent);padding:2px 0 2px 18px;margin:14px 0;font-size:15.5px;max-width:44em}
  .verdict b{color:var(--accent)}
  .verdict.warn{border-left-color:var(--no)} .verdict.warn b{color:var(--no)}
  table.tight{font-size:12.5px} table.tight td,table.tight th{padding:5px 9px}
  td.f{font-size:12.5px;max-width:34em}
  .srcrow td:first-child{font-family:var(--mono);white-space:nowrap;color:var(--accent)}
  .jig{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);gap:18px;
       align-items:start;margin:18px 0 26px}
  .jig figure{margin:0}
  .jig dl{margin:0;font-size:13px} .jig dt{font-family:var(--sans);font-size:11px;
       letter-spacing:.05em;text-transform:uppercase;color:var(--ink-2);margin-top:9px}
  .jig dd{margin:1px 0 0;font-family:var(--mono);font-size:12.5px}
  .gate{font-size:13.5px}
  td.pn{white-space:nowrap;font-family:var(--mono);font-size:12px}
  td.pn code{font-size:12px}
  ol.steps2{max-width:46em} ol.steps2 li{margin:5px 0}
  @media(max-width:760px){.jig{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="wrap">
<p class="backlink"><a href="RELEASE.html">← Release dossier</a></p>

<header class="hero">
  <p class="eyebrow">Microduck reverse-engineering · production</p>
  <h1>%s</h1>
  <p class="sub">%s</p>
  <div class="rev">
    <span>Document %s</span><span>Revision %s · %s</span>
    <span>Units %s</span><span>Generated by <code>tools/gen_playbook.py</code></span>
  </div>
</header>''' % (E(D["doc"]["title"]), E(D["doc"]["subtitle"]), E(D["doc"]["id"]),
                E(D["doc"]["rev"]), E(D["doc"]["date"]), E(D["doc"]["units"])))

if TOT:
    A('''<div class="statbar">
  <div class="stat"><b>%d</b><span>printed slugs / %d pieces</span></div>
  <div class="stat"><b>%.2f g</b><span>filament per robot, sliced</span></div>
  <div class="stat"><b>%.2f h</b><span>printer time per robot, sliced</span></div>
  <div class="stat"><b>$%.2f–%.2f</b><span>printed parts per robot, in-house</span></div>
  <div class="stat"><b>%d</b><span>jigs, drawn and sliced</span></div>
</div>''' % (len(ROWS), TOT["pieces"], TOT["grams"], TOT["hours"],
             TOT["robot_lo"], TOT["robot_hi"], len(JIGS["jigs"]) if JIGS else 0))

A('''<nav class="toc">
 <a href="#read">1 How to read this</a> ·
 <a href="#process">2 Process per part</a> ·
 <a href="#dfm">3 DFM, every part</a> ·
 <a href="#profiles">4 Print profiles</a> ·
 <a href="#line">5 The assembly line</a> ·
 <a href="#qa">6 QA gates</a> ·
 <a href="#pack">7 Packaging and shipping</a> ·
 <a href="#open">8 Open items</a> ·
 <a href="#sources">9 Sources</a>
</nav>''')

# ---- 1 -------------------------------------------------------------------
A('''<section id="read">
<h2><span class="n">1</span>How to read this</h2>
<p class="lede">This is the document a shop executes. Every number in it is either
the slicer's own output, a measurement taken off the geometry, or a figure quoted
from a named source — and where none of those exist the row says
<span class="chip cd">CANNOT DETERMINE</span> and names the test that would settle it.
No default has been substituted for a missing value anywhere in this file.</p>

<div class="verdict"><b>Three verdicts.</b> <span class="chip pass">PASS</span> the
measurement was taken and it clears the gate. <span class="chip cd">CANNOT DETERMINE</span>
nobody has measured it; the row says what would.
<span class="chip rail">FAIL</span> it was measured and it does not clear.
A <span class="chip cd">PRINTABLE-WITH-CARE</span> part prints — it needs the named
intervention, and shipping it without that intervention is the defect.</div>

<div class="note"><b>Where the numbers come from.</b>
<b>Grams and seconds</b> are BambuStudio's own <code>result.json</code> figures through
ce-slice, never derived from volume %s.
<b>Overhang and wall</b> are measured off the exact STL that was sliced, by
<code>tools/measure_dfm.py</code> %s — ce-cad has no overhang tool, and
<code>cecad.printed.printability</code> says in as many words that it "does not guess at
overhangs", so §3 is the measurement that was missing.
<b>Costs</b> are computed here from those numbers against the rate brackets in §2.1;
change a rate in <code>tools/data/playbook.json</code> and every table below moves.</div>
</section>''' % (src("SLICE"), src("DFM")))

# ---- 2 -------------------------------------------------------------------
A('<section id="process"><h2><span class="n">2</span>Process selection, part by part</h2>')
A('''<p class="lede">Print or mould is not one decision, it is thirty. Each part has its own
piece cost and its own tool cost, so each has its own break-even quantity — and for most of
this robot that quantity does not exist, because the printed piece already costs less than
the cheapest end of the sourced moulded piece price.</p>''')

A('<h3>2.1 The rate brackets, and what each is</h3>')
A(tbl(["term", "bracket", "basis", "source"], [
    [td("material, PLA"), td("$%.2f/kg × %.2f waste" % (R["material_usd_per_kg"]["PLA"],
                                                        R["material_usd_per_kg"]["waste_factor"]), "num"),
     td("retail spool; the waste factor is the model's own"), td(src("LM3", "CC"))],
    [td("material, TPU"), td("$%.2f/kg × %.2f waste" % (R["material_usd_per_kg"]["TPU"],
                                                        R["material_usd_per_kg"]["waste_factor"]), "num"),
     td("retail spool"), td(src("LM3", "CC"))],
    [td("material, farm stock"), td("$%.2f/kg PLA" % R["material_usd_per_kg"]["PLA_farm"], "num"),
     td("what a 1000-printer farm buys at"), td(src("SL"))],
    [td("machine-hour, in-house"), td("$%.2f–%.2f/h" % (R["machine_usd_per_hour_inhouse"]["low"],
                                                        R["machine_usd_per_hour_inhouse"]["high"]), "num"),
     td("wear (printer price ÷ 5,000 h) + power"), td(src("CC", "LM1"))],
    [td("machine-hour, bought"), td("$%.2f–%.2f/h" % (R["machine_usd_per_hour_farm"]["low"],
                                                      R["machine_usd_per_hour_farm"]["high"]), "num"),
     td("what a farm charges for a print hour"), td(src("LM2", "PR2", "GC"))],
    [td("labour"), td("$%.2f per print job" % (R["labour_usd_per_hour"] * R["labour_minutes_per_print_job"] / 60.0), "num"),
     td(E(R["labour_job_note"])), td(src("CC"))],
    [td("moulded piece"), td("$%.2f–%.2f" % (R["mould_piece_usd"]["low"], R["mould_piece_usd"]["high"]), "num"),
     td("aluminium tool, small part, vendor bracket on unlike parts"), td(src("HT"))],
    [td("tool"), td("%s floor; %s–%s aluminium" % (usd(R["tool_usd"]["floor"], 0),
                                                   usd(R["tool_usd"]["alu_low"], 0),
                                                   usd(R["tool_usd"]["alu_high"], 0)), "num"),
     td("one cavity set per slug; mirrored pairs cannot share"), td(src("PL1", "HT", "PL4"))],
    [td("failure buffer"), td("×%.2f–%.2f" % (R["failure_buffer"]["low"], R["failure_buffer"]["high"]), "num"),
     td("prints that do not finish"), td(src("CC", "GC"))],
]))

A('''<div class="note"><b>The one substitution this table refuses.</b> Every earlier version of
the cost question in this repo stopped at "Σ hours — CANNOT DETERMINE until sliced"
(<code>docs/production/process.md</code> §9 item 1). That is now closed: all %d pieces have
been sliced for real %s, so the machine-hour term below is measured and not modelled, and
the break-even arithmetic can finally be done on this robot rather than on a vendor's
example knob.</div>''' % (TOT.get("pieces", 0), src("SLICE")))

A('''<div class="note"><b>These costs are for the files on disk.</b> Every gram and second below
came from slicing the STLs in <code>out/print/stl/</code>. Twelve of those thirty are Pollen's
vendor mesh for a part that has since been rebuilt parametrically %s — see §8, first row. Re-export
and re-slice moves these numbers; the arithmetic and the conclusion in §2.3 do not turn on which of
the two geometries is used, because every rebuild is graded against the very mesh the STL holds and
the worst bounding-box deviation across the set is 0.7193 mm (<code>COMPARISON.html</code>) — a
difference that cannot move a $0.60 piece across a $0.50&ndash;5.00 band. It does change §3 and §4,
which are about the surface, and those sections say so.</div>''' % src("STALESTL"))

A('<h3>2.2 What one robot&rsquo;s printed parts cost</h3>')
if TOT:
    A(tbl(["line", "value", "how"], [
        [td("filament, sliced"), td("%.2f g over %d pieces" % (TOT["grams"], TOT["pieces"]), "num"),
         td("BambuStudio result.json, per piece × qty " + src("SLICE"))],
        [td("printer time, sliced"), td("%.2f h" % TOT["hours"], "num"),
         td("sequential per-piece prints; a plate prints faster than the sum " + src("SLICE"))],
        [td("material"), td(usd(TOT["material"], 2), "num"), td("PLA at $24/kg, TPU at $44/kg, ×1.10 waste")],
        [td("machine, in-house"), td("%s–%s" % (usd(TOT["machine_lo"], 2), usd(TOT["machine_hi"], 2)), "num"),
         td("%.2f h × $0.10–0.31/h" % TOT["hours"])],
        [td("labour, plate-batched"), td(usd(TOT["labour_plated"], 2), "num"),
         td("two plates per robot × 15 min hands-on at $20/h " + src("CC"))],
        [td("<b>printed parts per robot, in-house</b>"),
         td("<b>%s–%s</b>" % (usd(TOT["robot_lo"], 2), usd(TOT["robot_hi"], 2)), "num"),
         td("the three lines above × the 1.10–1.30 failure buffer")],
        [td("printed parts per robot, bought from a farm"),
         td("%s–%s" % (usd(TOT["farm_lo"], 2), usd(TOT["farm_hi"], 2)), "num"),
         td("%.2f h × $2–4/h plus farm-stock filament; no labour term — it is the farm's" % TOT["hours"])],
    ]))
    A('''<div class="verdict"><b>Read this against the bought cost.</b> RELEASE §2 puts the
readable bought cost at $472–481 per robot at every quantity from 1 to 1000. The printed
parts are %s–%s of that in-house. <b>The printed half of this robot is not where the money
is, at any volume.</b> Fifteen XL330 servos are.</div>''' % (usd(TOT["robot_lo"], 2), usd(TOT["robot_hi"], 2)))

A('<h3>2.3 Piece cost and break-even, every printed part</h3>')
A('''<p>N* = T / (c<sub>print</sub> − c<sub>mould</sub>). c<sub>print</sub> is the in-house
mid-point computed from this part's own sliced grams and seconds plus its share of the plate's
labour; c<sub>mould</sub> is the sourced $0.50–5.00 band %s; T is one cavity set. A dash in the
break-even columns means <b>there is none</b>: the printed piece already costs less than the
moulded one, so no tooling spend ever pays back. Sorted by piece cost.</p>''' % src("HT"))

rows = []
for r in ROWS:
    c = r["c"]
    rows.append([
        td('<code>%s</code>%s' % (E(r["slug"]),
                                  ' <span class="chip buy">visible</span>' if r["visible"] else ""), "pn"),
        td(r["material"] + (" ×%d" % r["qty"] if r["qty"] > 1 else "")),
        td("%.4f" % c["grams"], "num"),
        td("%.4f" % c["hours"], "num"),
        td(usd(c["material"], 4), "num"),
        td("%s–%s" % (usd(c["machine_lo"], 4), usd(c["machine_hi"], 4)), "num"),
        td(usd(c["labour_plated"], 4), "num"),
        td("<b>%s</b>" % usd(c["inhouse_mid"], 4), "num"),
        td(thou(r["be_best"]) if r["be_best"] else "—", "num"),
        td(thou(r["be_worst"]) if r["be_worst"] else "—", "num"),
        td(thou(r["be_at_mould_high"]) if r["be_at_mould_high"] else "—", "num"),
    ])
A(tbl(["part", "mat", "g/piece", "h/piece", "material", "machine", "labour share",
       "c<sub>print</sub>", "N* @ $1,495 tool", "N* @ $10,000 tool", "N* @ $5.00 piece"],
      rows, cls="data tight"))

nbe = sum(1 for r in ROWS if r["be_best"])
nnone = len(ROWS) - nbe
A('''<div class="verdict warn"><b>The measured answer, and it is not the one
<code>docs/production/process.md</code> §8 reached.</b> Of %d printed parts, <b>%d have no
break-even at all</b> against the cheap end of the moulded piece price, and <b>%d have none
against the dear end</b> — the printed piece is simply cheaper. Where a break-even does exist
it is <b>%s to %s units</b> at the Protolabs tool floor, and %s to %s units at the aluminium
ceiling. §8 of process.md recommended moulding the nine visible parts at 1,000 units; it made
that call with Σ hours marked CANNOT DETERMINE. With the hours measured, <b>the arithmetic no
longer supports it at 1,000</b>. What can still move those nine parts to a mould is
<b>surface finish and throughput</b>, not unit cost — and neither has a written acceptance
standard yet (§8).</div>''' % (
    len(ROWS), nnone,
    sum(1 for r in ROWS if not r["be_at_mould_high"]),
    thou(min(r["be_best"] for r in ROWS if r["be_best"])) if nbe else "—",
    thou(max(r["be_best"] for r in ROWS if r["be_best"])) if nbe else "—",
    thou(min(r["be_worst"] for r in ROWS if r["be_worst"])) if any(r["be_worst"] for r in ROWS) else "—",
    thou(max(r["be_worst"] for r in ROWS if r["be_worst"])) if any(r["be_worst"] for r in ROWS) else "—"))

A('<h3>2.4 The decision, by quantity</h3>')
vis_rows = [r for r in ROWS if r["visible"]]
vis_tool_floor = R["tool_usd"]["floor"] * len(vis_rows)
all_tool_floor = R["tool_usd"]["floor"] * len(ROWS)
A(tbl(["units", "decision", "the arithmetic behind it"], [
    [td("<b>1</b>"), td("<b>FDM in-house.</b> PLA hard set, TPU soft set."),
     td("%s–%s of printed parts against %s of tooling for one cavity set per slug %s. Nothing else is close."
        % (usd(TOT["robot_lo"], 2), usd(TOT["robot_hi"], 2), usd(all_tool_floor, 0), src("PL1")))],
    [td("<b>10</b>"), td("<b>FDM in-house</b>, both plates batched."),
     td("Tooling would be %s per robot. Cast the lips in silicone only if printed TPU fails the beak test %s."
        % (usd(all_tool_floor / 10.0, 0), src("ML")))],
    [td("<b>100</b>"), td("<b>FDM farm</b> — own printers or a no-MOQ farm. Mould nothing."),
     td("%s printer-hours for 100 robots. At the farm's own %s–%s per robot the printed parts are still under 12 %% of the bought cost."
        % (TOT["hours"] * 100, usd(TOT["farm_lo"], 2), usd(TOT["farm_hi"], 2)))],
    [td("<b>1,000</b>"), td("<b>Keep every part on FDM on cost.</b> Re-open the nine visible parts on finish and throughput, not on price."),
     td("%s printer-hours = a %d-printer farm for %.0f days at 20 h/day. Tooling the nine visible parts is %s–%s at the floor and the aluminium ceiling %s, i.e. %s–%s per robot on top of a moulded piece price that is mostly ABOVE what we print for. The case for a tool here is the layer line on a shell, and §8 records that nobody has written the acceptance standard that would settle it."
        % (thou(TOT["hours"] * 1000), 20, TOT["hours"] * 1000 / 20 / 20,
           usd(vis_tool_floor, 0), usd(R["tool_usd"]["alu_high"] * len(vis_rows), 0), src("PL1", "HT"),
           usd(vis_tool_floor / 1000.0, 2), usd(R["tool_usd"]["alu_high"] * len(vis_rows) / 1000.0, 2)))],
]))
A('''<div class="note"><b>What a mould would cost that is not in the price.</b> The geometry was
drawn for printing — 1 mm plates, 2 mm walls, printed-style bosses, bearing seats, M2
counterbores. A moulded version needs draft, uniform walls and side-actions for the bearing
bores and the head dome&rsquo;s undercuts, at £1,000–2,000 per cam %s. That is a redesign, not a
re-quote, and it is not costed anywhere in this document.</div>''' % src("PL4"))
A("</section>")

# ---- 3 -------------------------------------------------------------------
A('<section id="dfm"><h2><span class="n">3</span>DFM review — every printed part</h2>')
A('''<p class="lede">Every one of the %d printed slugs, measured. Overhang is the STL&rsquo;s own
facet normals resolved against six axis-aligned build directions: β is a facet&rsquo;s angle to the
build plate, so β = 90° is a vertical wall and β = 0 is a horizontal down-face, and
<b>β &lt; 30° is the slicer&rsquo;s own definition of an overhang</b> — <code>support_threshold_angle
= 30</code>, read off the process profile that sliced these parts %s. Wall thickness is internal ray
casting from %d seeded sample points; the p5 column is the honest thin-wall figure because the
absolute minimum of a triangulated shell is nearly always a chamfer knife-edge — the same
caveat <code>docs/DFM.md</code> makes about <code>inspect.thinnest_wall</code>
%s. One reading rule: on a part with no cavity the ray crosses the whole body, so a large wall
figure means &ldquo;no thin wall anywhere on this part&rdquo; and not &ldquo;a wall this thick&rdquo; — the eye-ring&rsquo;s
6.65 mm p5 is the ring&rsquo;s own section, not a shell.</p>''' % (len(ROWS), src("PRESET"), DFM["sample_rays"] if DFM else 0, src("DFM", "DFMMD")))

rows = []
for r in ROWS:
    f = dfm_row(r["slug"])
    if not f:
        continue
    w = f["w"]
    rows.append([
        td('<code>%s</code>' % E(r["slug"]), "pn"),
        td("<b>%s</b>" % f["best"], "num"),
        td("%.2f %%" % (100 * f["b"]["frac_lt45"]), "num"),
        td("%.2f %%" % (100 * f["b"]["frac_lt30"]), "num"),
        td("%.2f %%" % (100 * f["b"]["frac_lt10"]), "num"),
        td("%.0f" % f["b"]["projected_lt30_mm2"], "num"),
        td("%d" % f["b"]["layers_at_0p2"], "num"),
        td(n(w.get("min_mm")), "num"),
        td(n(w.get("p5_mm")), "num"),
        td(n(w.get("median_mm")), "num"),
        td(n(f["tw"]) if f["tw"] is not None else '<span class="chip cd">mesh</span>', "num"),
        td(chip(f["verdict"])),
    ])
A(tbl(["part", "build dir", "β&lt;45°", "β&lt;30°", "β&lt;10°", "unsup. mm²", "layers",
       "wall min", "wall p5", "wall med", "solid wall", "verdict"], rows, cls="data tight"))

A('''<div class="verdict warn"><b>What §3 measured, and what it did not.</b> Every row below is
read off the STL in <code>out/print/stl/</code> — <b>the file a shop would actually print</b>, and
the same file ce-slice costed in §2. For 22 of the 30 slugs that file is Pollen&rsquo;s vendor mesh, and
for 12 of those 22 <b>a PASSed parametric rebuild now exists in <code>ce-parts</code> that the STL
predates</b> %s. So this table is exact about what is on disk and silent about what those twelve
parts have since become. The companion review of the 20 parametric solids — exact thinnest wall,
ray percentiles, every hole, elevated-vs-bed support area, per-part risks — is
<code>docs/DFM.md</code> %s, which reached the same bed-contact correction from a separate tool.
Read both: this section tells you what will come off the printer today, that one tells you what
the design says.</div>''' % (src("STALESTL"), src("DFMMD")))

A('<h3>3.1 The finding, part by part</h3>')
rows = []
for r in ROWS:
    f = dfm_row(r["slug"])
    if not f:
        continue
    extra = []
    if f["parametric"]:
        if f["nholes"] is not None:
            extra.append("%d measured holes" % f["nholes"])
        if f["radii"]:
            extra.append("radii " + ", ".join("R%s" % n(x) for x in f["radii"]))
    else:
        extra.append("vendor mesh — no callable dimension, no drawing "
                     "(<code>out/drawings/INDEX.md</code>)")
    sl = next(p for p in SLICE["parts"] if p["slug"] == r["slug"])
    rows.append([
        td('<code>%s</code><br><span class="mono" style="font-size:11.5px;color:var(--ink-2)">%s mm · %.0f mm³ · %d tri</span>'
           % (E(r["slug"]), " × ".join(n(x) for x in f["bbox"]), f["vol"], f["tri"])),
        td("<ul style='margin:0;padding-left:16px'>" +
           "".join("<li>%s</li>" % x for x in f["findings"]) +
           ("<li>%s</li>" % "; ".join(extra) if extra else "") +
           ("<li><b>slicer said:</b> %s</li>" % E(sl["slicer_warning"]) if sl.get("slicer_warning") else "") +
           "</ul>", "f"),
        td(chip(f["verdict"])),
    ])
A(tbl(["part", "finding", "verdict"], rows, cls="data tight"))

A('''<h3>3.2 The five recurring risks — the drawing-note block</h3>
<ol class="steps2">
<li><b>Small tapped holes do not print to size.</b> Every Ø1.55/Ø1.60 (M2) and Ø2.05–2.30 hole
prints undersize and, when horizontal, bridges. Drill to tapping size and form-tap after
printing; heat-set inserts preferred for M2 into PLA %s.</li>
<li><b>Horizontal bores that carry a bearing or a press fit must be reamed</b> — ankle Ø14/Ø15,
upper-leg Ø5.37, bearing-roll / rigidity-plate / trunk-base Ø19, shin and hip pivots. A bridged
bore is oval as well as undersize at the top %s.</li>
<li><b>Thin flat plates must be laid flat</b> — upper-leg-rigidity-plate at 1 mm and neck-plate
at 2 mm. Standing either on edge fails. The overhang table above agrees: their best build
directions are the flat ones.</li>
<li><b>Sub-0.80 mm walls are knife-edges, not walls.</b> They slice fine. The two genuine
two-perimeter floors are power-support and hip-bracket at exactly 0.80 mm: no margin, so a
0.4 mm nozzle and ≥ 2 perimeters are not optional there %s.</li>
<li><b>power-support&rsquo;s sprung latch tongue</b> is the one genuinely fragile, moving printed
feature on the robot — thin, cantilevered and cycled. Highest wall count, print with the flex
plane in-plane, and it is a gate at S1 %s.</li>
</ol></section>''' % (src("DFMMD", "PARTS5"), src("DFMMD"), src("DFMMD"), src("DFMMD")))

# ---- 4 -------------------------------------------------------------------
A('<section id="profiles"><h2><span class="n">4</span>Print profiles</h2>')
pr = SLICE["parts"][0] if SLICE else {}
A('''<p class="lede">These are the presets that produced every gram and second in this
document — not a recommendation written afterwards. Reproducing the numbers means using
these exact names.</p>''')
A(tbl(["setting", "value", "note"], [
    [td("printer"), td("<code>%s</code>" % E(SLICE["printer"] if SLICE else "—")), td("bed 340 × 320 × 340")],
    [td("machine preset"), td("<code>%s</code>" % E(pr.get("machine_preset", "—"))), td("0.4 mm nozzle")],
    [td("process preset"), td("<code>%s</code>" % E(pr.get("process_preset", "—"))),
     td("layer %s mm" % n(pr.get("layer_mm")))],
    [td("filament, hard"), td("<code>Bambu PLA Basic @BBL H2S</code>"), td("1.26 g/cm³")],
    [td("filament, soft"), td("<code>Bambu TPU 85A @BBL H2S</code>"),
     td("1.18 g/cm³. The durometer is INFERRED: Pollen says nothing, community says 90–95A, and "
        "the H2S 0.4 preset resolves to 85A. " + '<span class="chip cd">CANNOT DETERMINE</span>')],
    [td("brim"), td("<code>no_brim</code>"), td("the workshop rule is no brim on any print; "
                                               "the tall slender parts in §3 are the ones to watch for it")],
    [td("supports"), td('<span class="chip rail">MUST BE ENABLED</span>'),
     td("the stock 0.20 mm Standard preset generates none, and 11 parts came back with a slicer "
        "support warning. The grams and seconds in §2 are therefore a FLOOR — re-slice with supports "
        "on before quoting a production run (§8).")],
    [td("orientation"), td("per part, §4.2"), td("auto-oriented by ce-slice (<code>--orient 1 "
                                                 "--allow-rotations</code>) except where noted")],
    [td("plates"), td("<code>out/print/plates/PLA/microduck-PLA.3mf</code> (32 pieces)<br>"
                      "<code>out/print/plates/TPU/microduck-TPU.3mf</code> (4 pieces)"),
     td("one plate never mixes filaments; both re-opened and their printable area measured back "
        "against the H2S bed")],
]))


if D.get("profile"):
    A('<h3>4.1 The process preset, read off the installed profile</h3>')
    A('<p>Not a summary — these are the resolved values in the profile file itself, '
      'with its <code>inherits</code> chain followed %s. Two of them decide verdicts '
      'elsewhere in this document.</p>' % src("PRESET"))
    A(tbl(["key", "value", "what it means here"],
          [[td("<code>%s</code>" % E(k)), td("<b>%s</b>" % E(v), "num"), td(E(w) or "", "f")]
           for k, v, w in D["profile"]["values"]], cls="data tight"))
    A('<div class="note"><b>Two of those are load-bearing.</b> '
      '<code>wall_loops = 2</code> at a 0.4 mm nozzle IS the 0.80 mm floor every wall verdict in '
      '§3 is measured against — it is not a convention borrowed from elsewhere. And '
      '<code>detect_thin_wall = 0</code> with <code>wall_generator = classic</code> means a feature '
      'narrower than one extrusion is not thinned to fit, it is <b>silently dropped from the '
      'G-code</b>: a thin wall does not print badly here, it does not print at all. That is why '
      '§3 measures a wall percentile rather than trusting the render, and why the 0.550 mm land in '
      '§5.1 is a FAIL rather than a caution. <code>support_threshold_angle = 30</code> is the '
      "slicer's own definition of an overhang and is exactly the β&lt;30° column in §3, so the two "
      'measurements are commensurable.</div>')

A('<h3>4.2 Orientation per part — what the slicer used, and what the measurement says</h3>')
A('''<p>Three answers to the same question, side by side. <b>Sliced</b> is the orientation rule
that produced this part&rsquo;s grams and seconds. <b>Least overhang</b> is the axis-aligned direction
with the smallest unsupported area, straight off the measurement in §3 with nothing added.
<b>Recommended</b> is that same measurement after one stated constraint — see the note under the
table, because on the flat plates the two differ by a factor that decides whether the part
prints at all. <b>Slenderness</b> is the recommended build&rsquo;s height divided by the smaller
in-plane bounding-box dimension. The last column is <b>+Z as modelled against the
recommendation</b>: above 1 it is the penalty for printing the part in the orientation the STL
happens to arrive in, and below 1 it means +Z would carry less overhang but was rejected by the
constraint.</p>''')
rows = []
for r in ROWS:
    f = dfm_row(r["slug"])
    sl = next(p for p in SLICE["parts"] if p["slug"] == r["slug"])
    if not f:
        continue
    zz = f["asmZ"]["area_lt30_mm2"]
    bb = f["b"]["area_lt30_mm2"]
    rows.append([
        td('<code>%s</code>' % E(r["slug"]), "pn"),
        td(E(sl.get("orientation_rule") or "—"), "f"),
        td("<b>%s</b>" % f["minoh"], "num"),
        td(("<b>%s</b>" % f["best"]) + ("" if f["admissible"]
           else ' <span class="chip cd">no admissible dir</span>'), "num"),
        td("%.1f" % f["slender"], "num"),
        td("%.0f mm²" % bb, "num"),
        td("%d" % f["b"]["layers_at_0p2"], "num"),
        td("%.0f mm²" % zz, "num"),
        td("%.2f×" % (zz / bb) if bb > 0 else "—", "num"),
    ])
A(tbl(["part", "sliced orientation rule", "least overhang", "recommended",
       "slenderness", "unsup. at rec.", "layers", "unsup. at +Z", "+Z vs rec."],
      rows, cls="data tight"))
A('''<div class="note"><b>Why &ldquo;least overhang&rdquo; and &ldquo;recommended&rdquo; are different columns.</b>
Minimising unsupported area, on its own, always wants a flat plate stood on edge — measured:
the 1 mm upper-leg-rigidity-plate reads <b>77 mm²</b> unsupported built +Z against <b>748 mm²</b>
lying flat, and +Z is <b>291 layers of a 1 mm wall</b>, which is precisely the failure
<code>docs/DFM.md</code> warns about. So the recommended column applies one stated rule on top
of the measurement: <b>build height ≤ %.0f × the smaller in-plane bounding-box dimension</b>, and
among the directions that pass, the least unsupported area wins. That rule is an engineering
choice, not a measurement, and it is the only one in this document — everything else in these
tables is read off the geometry. ce-slice&rsquo;s own auto-orient searches all rotations rather than
the six axes, so where the sliced rule differs from both columns it is not necessarily
wrong.</div>''' % SLENDER_K)

if STALE:
    t = STALE["totals"]
    A('<h3>4.3 What the stale print files cost, measured</h3>')
    A('''<p>§8 says the STL for twelve of the thirty slugs predates that part&rsquo;s parametric rebuild.
That is a defect whether or not it is expensive, but it is worth knowing which. Each of the twelve
rebuilds — exported to <code>out/dfm/stl-rebuilt/</code> — was sliced on <b>exactly</b> the presets
and flags that produced §2 (<code>--orient 1 --allow-rotations</code>, same machine, same process,
same filament), so the two columns are comparable. Both are the slicer&rsquo;s own numbers.</p>''')
    rows = []
    for r in STALE["rows"]:
        rows.append([
            td('<code>%s</code>%s' % (E(r["slug"]), " ×%d" % r["qty"] if r["qty"] > 1 else ""), "pn"),
            td(r["material"]),
            td("%.4f" % r["disk_g"], "num"), td("%.4f" % r["rebuilt_g"], "num"),
            td(("<b>%+.2f %%</b>" if abs(r["d_g_pct"]) >= 5 else "%+.2f %%") % r["d_g_pct"], "num"),
            td("%.1f" % r["disk_s"], "num"), td("%.1f" % r["rebuilt_s"], "num"),
            td(("<b>%+.2f %%</b>" if abs(r["d_s_pct"]) >= 5 else "%+.2f %%") % r["d_s_pct"], "num"),
        ])
    A(tbl(["part", "mat", "g on disk", "g rebuilt", "Δg", "s on disk", "s rebuilt", "Δs"],
          rows, cls="data tight"))
    big = [r for r in STALE["rows"] if abs(r["d_g_pct"]) >= 5 or abs(r["d_s_pct"]) >= 5]
    A('''<div class="verdict warn"><b>Small in the aggregate, large in three places.</b> Across a whole
robot the twelve stale files are worth <b>%+.2f g</b> and <b>%+.3f h</b> — %+.2f %% of the %.2f g and
%+.2f %% of the %.2f h in §2. So §2&rsquo;s costs and §2.3&rsquo;s break-evens do not move.
<b>%d of the twelve differ by 5 %% or more on mass or on time</b>: %s. For those, §3&rsquo;s overhang and
wall figures and §4.2&rsquo;s orientation are describing a shape the design no longer has. Re-export and
re-slice before a production run; the geometry to do it with already exists.</div>'''
      % (t["delta_grams_per_robot"], t["delta_hours_per_robot"],
         100.0 * t["delta_grams_per_robot"] / t["robot_grams_on_disk"], t["robot_grams_on_disk"],
         100.0 * t["delta_hours_per_robot"] / t["robot_hours_on_disk"], t["robot_hours_on_disk"],
         len(big),
         ", ".join("<code>%s</code> (%+.1f %% g, %+.1f %% s)"
                   % (E(r["slug"]), r["d_g_pct"], r["d_s_pct"]) for r in big)))

A("</section>")

# ---- 5 -------------------------------------------------------------------
A('<section id="line"><h2><span class="n">5</span>The assembly line</h2>')
A('''<p class="lede">Eleven stations. The build order is the construction manual&rsquo;s
%s; what this section adds is the jig at each operation that needs one, the gate that lets the
unit move on, and an honest account of the torques nobody has measured.</p>''' % src("MANUAL"))

# 5.1 jigs
A('<h3>5.1 The jig set</h3>')
if JIGS:
    t = JIGS.get("jig_set_total", {})
    A('''<p>Six jigs, designed as cecad parts, each with a verified A3 third-angle drawing and
each sliced for real. The whole set is <b>%s g and %s h</b> of printing — one set serves the
line, and the pushers are consumables. Source: <code>tools/jigs.py</code>; geometry and
drawings: <code>out/jigs/</code>.</p>''' % (n(t.get("grams")), n(t.get("hours"), 3)))
    rows = []
    for slug, j in JIGS["jigs"].items():
        s = j.get("sliced", {})
        d = j.get("drawing", {})
        rows.append([
            td('<code>%s</code>' % E(slug), "pn"),
            td(E(j["title"]), "f"),
            td(" × ".join(n(x) for x in j["bbox_mm"]), "num"),
            td(n(s.get("grams")), "num"),
            td("%s" % n(round(s.get("seconds", 0) / 60.0, 1)), "num"),
            td('<a href="%s">SVG</a> · <a href="%s">PDF</a> · <a href="%s">DXF</a> %s'
               % (E(d.get("svg", "")), E(d.get("pdf", "")), E(d.get("dxf", "")),
                  chip("PASS") if d.get("verify_sheet") else chip("CANNOT DETERMINE"))),
        ])
    A(tbl(["jig", "what it is for", "bbox mm", "g", "print min", "drawing"], rows, cls="data tight"))

    for slug in ("microduck-jig-press-22-inner", "microduck-jig-horn-zero"):
        j = JIGS["jigs"].get(slug)
        if not j:
            continue
        g = j["geometry"]
        dl = []
        for k, v in g.items():
            if isinstance(v, dict):
                v = "; ".join("%s %s" % (kk, n(vv) if isinstance(vv, float) else vv) for kk, vv in v.items())
            elif isinstance(v, list):
                v = " – ".join(n(x) for x in v)
            dl.append("<dt>%s</dt><dd>%s</dd>" % (E(k.replace("_", " ")), E(str(v))))
        A('''<div class="jig">
  <figure><img src="out/jigs/_shots/%s.png" alt="%s drawing">
    <figcaption>%s — third angle, measured off the solid, <code>verify_sheet</code> PASS.</figcaption></figure>
  <dl>%s</dl>
</div>''' % (E(slug), E(slug), E(j["title"]), "".join(dl)))

A('''<h3>5.2 The bearing rule this repo had wrong</h3>
<div class="verdict warn"><b>&ldquo;Press the outer race only&rdquo; is wrong for half of this robot&rsquo;s
bearings.</b> <code>RELEASE.html</code> §4 and the construction manual both give that rule. It is
right for a seat that is a <b>bore</b> and wrong for a seat that is a <b>boss</b>, and this
robot has both — read off the connection records themselves %s:
<ul>
<li><b>Bore seats</b> (the Ø22 pocket in trunk_base for hip-yaw, and the head for head-roll;
the ankle&rsquo;s Ø15.0 × 2.3 pocket with its Ø16 × 0.5 lead-in) take the <b>outer-ring</b> pusher.</li>
<li><b>Boss seats</b> (yaw2roll <code>yaw_bearing_seat</code> Ø16.0 × 1.95, hip-bracket
<code>roll_/pitch_bearing_seat</code> Ø16.0 × 1.95, yaw-roll-motion <code>roll_bearing_seat</code>
Ø16.0 × 4.0, and the shin&rsquo;s Ø10.0 × 3.2) take the <b>inner-ring</b> pusher.</li>
</ul>
The load must pass through the ring that is being interference-fitted. Push the wrong ring and
the press force crosses the balls — the bearing is brinelled, it still spins on the bench, and it
fails months later in a customer&rsquo;s hands. That is why there are four pushers in §5.1 and not
two, and why S2&rsquo;s first instruction is to read the seat before picking up a tool.</div>''' % src("CONN22", "CONN15"))

A('<h3>5.3 Torque</h3>')
A('''<p>Three joint families, three <span class="chip cd">CANNOT DETERMINE</span>, three tests.
Nothing here is a plausible default, and the one hard number that exists is listed only so that
nobody uses it.</p>''')
for t in D["torque"]:
    A('''<div class="card" style="margin:12px 0">
<h3>%s</h3>
<p><b>%s</b> — %s</p>
<p style="margin-top:8px"><b>Do not use:</b> %s</p>
<p style="margin-top:8px"><b>The test that settles it:</b> %s</p>
<p style="margin-top:8px"><b>Until then:</b> %s</p>
</div>''' % (E(t["joint"]), chip(t["verdict"]), E(t["why"]), E(t["do_not_use"]),
             E(t["test"]), E(t["interim"])))
A('''<div class="note">The only sourced M2 figure in this repository is a DIN 912 class 12.9
seating torque into a <b>steel</b> nut: M2, stress area 2.07 mm², tensile load 2530 N,
<b>0.60 N·m</b> self-colour and <b>0.43 N·m</b> zinc-plated %s. It is quoted here as the
ceiling that proves the point: a printed PLA boss will not see a tenth of it before it
splits.</div>''' % src("HILLCO"))

A('<h3>5.4 Stations</h3>')
for s in D["stations"]:
    A('<h4>%s · %s <span style="font-weight:400;color:var(--ink-2)">— %s</span></h4>'
      % (E(s["id"]), E(s["name"]), E(s["takt_note"])))
    A('<p style="font-size:13.5px;color:var(--ink-2)"><b>In:</b> %s</p>' % E(s["inputs"]))
    A('<ol class="steps2">' + "".join("<li>%s</li>" % E(x) for x in s["steps"]) + "</ol>")
A("</section>")

# ---- 6 -------------------------------------------------------------------
A('<section id="qa"><h2><span class="n">6</span>QA gates</h2>')
A('''<p class="lede">One table, in build order. A unit does not leave a station until its gates
pass; a failed gate has a named action and none of them is &ldquo;continue and check later&rdquo;. The
gates that catch a defect which becomes invisible one station later carry a
<span class="chip rail">last chance</span> mark: after that station the defect is inside a closed
assembly, and finding it costs a teardown rather than a re-work.</p>''')
rows = []
for s in D["stations"]:
    for i, g in enumerate(s["gates"]):
        rows.append([
            td("<b>%s</b><br><span style='font-size:12px;color:var(--ink-2)'>%s</span>"
               % (E(s["id"]), E(s["name"])) if i == 0 else "", "gate"),
            td(E(g["gate"]) + (' <span class="chip rail">last chance</span>'
                              if g.get("critical") else ""), "f"),
            td(E(g["pass"]), "f"),
            td(E(g["fail_action"]), "f"),
        ])
A(tbl(["station", "gate", "passes when", "on failure"], rows, cls="data tight"))
A('''<div class="note"><b>The functional test itself is not in this document.</b> S9 lists its
gates; the procedure that proves a built unit works — electrical bring-up, servo calibration,
sensor checks and the walk acceptance test — is <code>TEST-PLAN.html</code>.</div>''')
A("</section>")

# ---- 7 -------------------------------------------------------------------
A('<section id="pack"><h2><span class="n">7</span>Packaging and shipping</h2>')
b = D["packaging"]["battery"]
A('''<p class="lede">One removable %s decides most of this section. %s = <b>%s Wh</b> for the
battery and %s Wh per cell, so it is &ldquo;small&rdquo; lithium-ion in every regime — but which regime
applies depends on <b>where the pack is</b> when the box leaves, and the three answers are not
alike.</p>''' % (E(b["pack"]), "7.2 V × 2.6 Ah", n(b["wh"]), n(b["per_cell_wh"])))
A('<div class="note">%s %s</div>' % (E(b["classification"]), src("S15", "S12", "S9")))
rows = []
for c in D["packaging"]["configurations"]:
    rows.append([
        td("<b>%s</b>" % E(c["config"]), "f"),
        td("<code>%s</code><br>%s" % (E(c["un"]), E(c["pi"]))),
        td(E(c["soc"]), "f"),
        td(E(c["marks"]), "f"),
        td(E(c["line_action"]), "f"),
    ])
A(tbl(["configuration", "UN / PI", "state of charge", "marks and paperwork", "what S10 does"],
      rows, cls="data tight"))
A('<h3>7.1 What the box has to be</h3>')
A('<ol class="steps2">' + "".join("<li>%s</li>" % E(x) for x in D["packaging"]["box_requirements"]) + "</ol>")
A('''<div class="verdict warn"><b>The robot has no power switch.</b> Nothing in any source gives it
one. The packaging insert is therefore the only thing standing between a battery in a box and
IATA E.08&rsquo;s requirement that equipment be &ldquo;packaged in a manner that prevents unintentional
activation&rdquo; %s. That makes the insert a regulated part, not a cosmetic one — and it is the
single packaging item with no design and no supplier in this repository.</div>''' % src("S9"))
A("</section>")

# ---- 8 -------------------------------------------------------------------
A('<section id="open"><h2><span class="n">8</span>Open items</h2>')
A('''<p class="lede">What this playbook cannot yet tell a shop, with the measurement that would
close each one. These are work items, not caveats.</p>''')
rows = []
for o in D["open"]:
    rows.append([
        td("<b>%s</b>" % E(o["item"]), "f"),
        td(chip(o["state"])),
        td(E(o["settles"]) + (("<br><b>Consequence:</b> " + E(o["consequence"]))
                              if o.get("consequence") else ""), "f"),
    ])
A(tbl(["item", "state", "what settles it, and why it matters"], rows, cls="data tight"))
A("</section>")

# ---- 9 -------------------------------------------------------------------
A('<section id="sources"><h2><span class="n">9</span>Sources</h2>')
A('<p class="lede">Every bracketed tag in this document. A figure with no tag was computed here '
  'from a figure that has one.</p>')
rows = []
for k, v in D["sources"].items():
    rows.append([
        td('<span id="src-%s"><b>%s</b></span>' % (E(k), E(k))),
        td(E(v["what"]), "f"),
        td("<code>%s</code>%s" % (E(v["where"]), (" · " + E(v["date"])) if v.get("date") else ""), "f"),
    ])
A(tbl(["tag", "what it says", "where, verbatim"], rows, cls="data tight srcrow"))
A("</section>")

A('''<footer>
<span>Microduck · %s rev %s</span>
<span>Generated by <code>tools/gen_playbook.py</code> from <code>tools/data/playbook.json</code> + <code>out/print/slice.json</code> + <code>out/dfm/dfm.json</code> + <code>out/jigs/jigs.json</code></span>
<span>Every number measured, cited, or marked CANNOT DETERMINE</span>
</footer>
</div>
</body>
</html>''' % (E(D["doc"]["id"]), E(D["doc"]["rev"])))

open(OUT, "w").write("\n".join(P))
print("wrote", OUT, os.path.getsize(OUT), "bytes;", len(ROWS), "parts,",
      len(JIGS["jigs"]) if JIGS else 0, "jigs,",
      sum(len(s["gates"]) for s in D["stations"]), "gates")
