#!/usr/bin/env python3
"""gen_test_plan.py — build TEST-PLAN.html from spec/test-plan.json.

Lane H of GOAL.md. The JSON is the data; every derived number (degrees,
encoder counts, the count tolerance) is computed HERE and shown with its
formula, so no derived figure is hand-maintained anywhere.

    python3 tools/gen_test_plan.py

Runs on the system python3 (no numpy, no FreeCAD): this generator does
arithmetic and string work only.
"""
import json, os, re, html, math

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
D = json.load(open(os.path.join(REPO, "spec", "test-plan.json")))

def _load(rel):
    """A measured artifact, or a loud failure. Nothing in this document is allowed to
    fall back to a typed copy of a number that lives in a generated file."""
    fp = os.path.join(REPO, rel)
    if not os.path.exists(fp):
        raise SystemExit("gen_test_plan: %s is missing; the gates that rest on it have no basis" % rel)
    return json.load(open(fp))

SIMREP  = _load("out/sim/report.json")
RUNTIME = _load("out/sim-evidence/battery-runtime.json")

E = lambda s: html.escape(str(s), quote=False)

_CODE = re.compile(r"`([^`]+)`")
def M(t):
    """Escape, then render `backticked` spans as <code>. Prose in the data file is
    written with backticks the way the source documents write them; this is the one
    place that turns them into markup, so no field carries HTML."""
    return _CODE.sub(lambda m: "<code>%s</code>" % m.group(1), E(t))

# ---- derived constants, computed not typed -------------------------------
RESOLUTION_PULSE_REV = 4096          # E1 §Specifications "Resolution | 4096 [pulse/rev]"
ZERO_COUNT           = 2048          # bus.rs: 2048 = 0 rad
DEG_PER_COUNT        = 360.0 / RESOLUTION_PULSE_REV
COUNT_PER_RAD        = RESOLUTION_PULSE_REV / (2.0 * math.pi)
TOL_DEG              = 1.0           # const.py backlash twins ±1°
TOL_COUNT            = int(math.floor(TOL_DEG / DEG_PER_COUNT))   # 11
LIMP_FALL_TILT_Z     = -0.90         # robotd.toml [safety]
FALL_GRAVITY_Z       = -0.50
LIMP_TILT_DEG        = math.degrees(math.acos(-LIMP_FALL_TILT_Z))
FALL_TILT_DEG        = math.degrees(math.acos(-FALL_GRAVITY_Z))
_WALK                = SIMREP["runs"]["walk_ours"]      # read, never typed
SIM_WALK_M           = _WALK["walked_m"]
SIM_WALK_S           = _WALK["seconds"]
SIM_WALK_TILT        = _WALK["max_tilt_deg"]
SIM_WALK_POLICY      = _WALK["policy_file"]
GATE_FRACTION        = 0.75          # decision of the plan; stated as such
GATE_WALK_M          = round(SIM_WALK_M * GATE_FRACTION, 3)
STANDBY_MA           = 17            # E1 "Standby Current | 17 [mA]"
N_SERVOS             = 15
STANDBY_TOTAL_A      = N_SERVOS * STANDBY_MA / 1000.0
STALL_5V_A           = 1.47
STALL_TOTAL_A        = N_SERVOS * STALL_5V_A

SECNUM = {sec["id"]: i + 2 for i, sec in enumerate(D["sections"])}
TAIL   = [("eol", "End-of-line checklist"), ("logs", "Logs"),
          ("open", "What this plan cannot test"), ("sources", "Sources")]
TAILNUM = {sid: len(D["sections"]) + 2 + i for i, (sid, _) in enumerate(TAIL)}

_tbl = [0]
def TN():
    """Table numbers count themselves, in the order the document renders them. Adding a
    section must not silently renumber a caption by hand."""
    _tbl[0] += 1
    return _tbl[0]

def rad2count(r):  return ZERO_COUNT + r * COUNT_PER_RAD
def rad2deg(r):    return math.degrees(r)

def link(href, text, note="not yet in the repository"):
    """A link is only written when the target is on disk. A cross-lane document that has
    not landed yet renders as plain text with the reason, so this page never ships a
    dead link and heals itself the moment the file appears."""
    if os.path.exists(os.path.join(REPO, href.split("#")[0])):
        return '<a href="%s">%s</a>' % (href, text)
    return '<span class="pending">%s <i>(%s)</i></span>' % (text, E(note))

# ---- source resolution ---------------------------------------------------
SRC = D["sources"]
def srcline(keys):
    if not keys: return ""
    out = []
    for k in keys:
        s = SRC.get(k)
        out.append('<span class="srcitem"><b>%s</b> %s</span>' % (E(k), E(s["label"] if s else k)))
    return '<div class="srcs">%s</div>' % "".join(out)

# ---- counters ------------------------------------------------------------
all_tests = [t for s in D["sections"] if s["kind"] == "tests" for t in s["tests"]]
n_tests   = len(all_tests)
n_notest  = len([t for t in all_tests if t["gate"]["PASS"] == "—"])
n_open    = len(D["open"])

# ---- fragments -----------------------------------------------------------
def equip_table():
    rows = []
    for name, what, why, sk in D["equipment"]:
        rows.append('<tr><td><b>%s</b></td><td>%s</td><td>%s</td><td class="sk">%s</td></tr>'
                    % (E(name), M(what), M(why), E(sk)))
    return "\n".join(rows)

def idmap_table():
    rows = []
    for sid, joint, body, rng, home in D["id_map"]:
        lo, hi = rng
        rows.append(
          '<tr><td class="n">%d</td><td><code>%s</code></td><td>%s</td>'
          '<td class="n">%.3f</td><td class="n">%.3f</td>'
          '<td class="n">%.3f</td><td class="n">%.4f</td><td class="n">%.1f</td></tr>'
          % (sid, E(joint), E(body), lo, hi, home, rad2deg(home), rad2count(home)))
    return "\n".join(rows)

def rails_table():
    rows = []
    for r in D["rails"]:
        band = r["band"]
        cls = "cd" if band.startswith("CANNOT") else ""
        rows.append(
          '<tr><td><code>%s</code></td><td>%s</td><td>%s</td>'
          '<td class="%s"><b>%s</b></td><td class="basis">%s</td><td class="sk">%s</td></tr>'
          % (E(r["net"]), M(r["where"]), M(r["nominal"]), cls, M(band),
             M(r["basis"]), E(" ".join(r["src"]))))
    return "\n".join(rows)

def reg_table():
    rows = []
    for r in D["registers"]:
        rows.append(
          '<tr><td class="n">%d</td><td class="n">%d</td><td><b>%s</b></td><td>%s</td>'
          '<td>%s</td><td><code>%s</code></td><td>%s</td><td class="basis">%s</td></tr>'
          % (r["addr"], r["size"], E(r["name"]), E(r["area"]), M(r["initial"]),
             M(r["write"]), M(r["means"]), M(r["why"])))
    return "\n".join(rows)

def padmap_table():
    return "\n".join('<tr><td><b>%s</b></td><td>%s</td></tr>' % (E(a), M(b))
                     for a, b in D["padmap"]["rows"])

def runtime_table():
    """The endurance expectation, read straight out of the lane-F2 study. Nothing here is
    retyped: change the study and this table changes with it."""
    rt = RUNTIME["outputs"]["runtime_table"]
    rows = []
    for i, w in enumerate(rt["walking"]["rows"]):
        st_ = rt["standing"]["rows"][i]
        idl = rt["idle_torque_off"]["rows"][i]
        rows.append('<tr><td class="n">%.1f</td><td class="n">%.4f</td><td class="n">%.1f</td>'
                    '<td class="n">%.1f</td><td class="n">%.1f</td><td class="n">%.4f</td></tr>'
                    % (w["compute_and_sensors_W"], w["total_W"], w["runtime_min"],
                       st_["runtime_min"], idl["runtime_min"], w["pack_current_A_at_7.4V"]))
    return "\n".join(rows)

def test_block(t):
    steps = []
    for i, s in enumerate(t["steps"], 1):
        cmd = ('<div class="cmd">%s</div>' % E(s["cmd"])) if s.get("cmd") else ""
        exp = ('<div class="exp">expect &rarr; %s</div>' % M(s["expect"])) if s.get("expect") and s["expect"] != "—" else ""
        steps.append('<li>%s%s%s</li>' % (M(s["do"]), cmd, exp))
    pre  = "".join('<li>%s</li>' % M(p) for p in t["pre"] if p != "—")
    tool = ", ".join(t["tool"]) if t["tool"] != ["—"] else "—"
    g = t["gate"]
    grows = []
    for k, cls in (("PASS","pass"), ("FAIL","fail"), ("CD","cd")):
        v = g.get(k, "—")
        if v == "—": continue
        lbl = "CANNOT DETERMINE" if k == "CD" else k
        grows.append('<tr><td class="v %s">%s</td><td>%s</td></tr>' % (cls, lbl, M(v)))
    return """
<article class="test" id="%(id)s">
  <h3><span class="tid">%(id)s</span>%(title)s</h3>
  <p class="purpose">%(purpose)s</p>
  <div class="meta">
    <div><span class="k">Tool</span>%(tool)s</div>
    <div><span class="k">Log</span><code>%(log)s</code></div>
  </div>
  %(prebox)s
  <h4>Procedure</h4>
  <ol class="steps">%(steps)s</ol>
  <h4>What is measured</h4>
  <p class="measure">%(measure)s</p>
  <h4>Gate</h4>
  <div class="tw"><table class="gate"><tbody>%(grows)s</tbody></table></div>
  <div class="basisbox"><span class="k">Basis of the gate</span>%(basis)s</div>
  %(srcs)s
</article>""" % dict(
      id=E(t["id"]), title=E(t["title"]), purpose=M(t["purpose"]),
      tool=M(tool), log=E(t["log"]),
      prebox=('<h4>Preconditions</h4><ul class="pre">%s</ul>' % pre) if pre else "",
      steps="".join(steps), measure=M(t["measure"]),
      grows="".join(grows), basis=M(t["gate_basis"]), srcs=srcline(t["src"]))

def sections_html():
    out = []
    for s in D["sections"]:
        if s["kind"] == "equip":
            out.append("""
<section id="%s">
  <h2><span class="n">%s</span>%s</h2>
  <p class="lede">Nothing on this list is optional for the test it serves. Where an instrument's
  resolution is named, it is because a gate below is stated to that resolution.</p>
  <div class="tw"><table class="data"><caption>Table %d. Equipment, and the gate each one serves.</caption>
  <thead><tr><th>Instrument or fixture</th><th>Used by</th><th>Why this and not something looser</th><th>Src</th></tr></thead>
  <tbody>%s</tbody></table></div>
</section>""" % (s["id"], SECNUM[s["id"]], E(s["title"]), TN(), equip_table()))
            continue
        extra = ""
        if s["id"] == "electrical":
            extra = """
<h3 class="sub">%d.1 Rails — what to measure, where, and against what</h3>
<div class="tw"><table class="data"><caption>Table %d. Every supply a fitted part needs, at the pin that needs it.
Bands are tightest-part-wins per rail. A band that reads CANNOT DETERMINE is not a pass.</caption>
<thead><tr><th>Net</th><th>Probe point</th><th>Nominal</th><th>Acceptance band</th><th>Basis</th><th>Src</th></tr></thead>
<tbody>%s</tbody></table></div>
<div class="note"><b>Two numbers worth carrying into section 3.</b>
Fifteen servos at the vendor's standby current draw <b>%.3f&nbsp;A</b> (15&nbsp;&times;&nbsp;%d&nbsp;mA) with torque off.
Fifteen servos stalled at 5.0&nbsp;V draw <b>%.2f&nbsp;A</b> (15&nbsp;&times;&nbsp;%.2f&nbsp;A) — a real number the vendor's
own stall row supports, and nothing in any source says what the pack or the HAT path can deliver.
Above 6.0&nbsp;V no vendor stall figure exists at all, which is exactly why EB-04 comes before EB-07.</div>
""" % (SECNUM["electrical"], TN(), rails_table(), STANDBY_TOTAL_A, STANDBY_MA, STALL_TOTAL_A, STALL_5V_A)
        if s["id"] == "servo":
            extra = """
<h3 class="sub">%d.1 The ID map, and the home pose in counts</h3>
<p>Encoder counts are computed here, not typed:
<code class="formula">count = %d + rad &times; %d / (2&pi;) = %d + rad &times; %.6f</code>,
from the vendor's 4096&nbsp;pulse/rev resolution and <code>bus.rs</code>'s 2048 = 0&nbsp;rad.
One count is <b>%.4f&nbsp;degrees</b>, so the &plusmn;%.1f&nbsp;degree calibration tolerance is
<b>&plusmn;%d&nbsp;counts</b>.</p>
<div class="tw"><table class="data idmap"><caption>Table %d. Servo ID to joint, the joint's MJCF range, and the home pose
in radians, degrees and encoder counts. Home values are <code>DEFAULT_POSITION</code> from <code>model.rs:39-55</code>;
ranges are the MJCF limits read back through our own simulation.</caption>
<thead><tr><th>ID</th><th>Joint</th><th>Body carrying the servo</th>
<th>range lo&nbsp;rad</th><th>range hi&nbsp;rad</th><th>home&nbsp;rad</th><th>home&nbsp;deg</th><th>home&nbsp;count</th></tr></thead>
<tbody>%s</tbody></table></div>
<div class="note"><b>ID 200 is not in this table.</b> The <code>imu_to_dxl</code> v2 board rides the same bus as a
sixteenth device and is <code>sync_read</code> first on every tick. It has no joint, no range and no home pose —
but SV-03 fails without it.</div>

<h3 class="sub">%d.2 The register set</h3>
<p>Every value below is quoted from the vendor control table in <code>ce-parts/xl330-m288-t/electrical.chip.json</code>.
<b>EEPROM writes are refused unless Torque&nbsp;Enable(64) is 0</b> — the vendor's own rule, and the reason it is the
first row of every write sequence.</p>
<div class="tw"><table class="data reg"><caption>Table %d. The XL330-M288-T registers this plan touches.</caption>
<thead><tr><th>Addr</th><th>Bytes</th><th>Name</th><th>Area</th><th>Vendor initial</th><th>We write</th><th>Meaning</th><th>Why</th></tr></thead>
<tbody>%s</tbody></table></div>
""" % (SECNUM["servo"], ZERO_COUNT, RESOLUTION_PULSE_REV, ZERO_COUNT, COUNT_PER_RAD,
       DEG_PER_COUNT, TOL_DEG, TOL_COUNT, TN(), idmap_table(),
       SECNUM["servo"], TN(), reg_table())
        if s["id"] == "walk":
            sr = D["surface"]
            rows = "".join('<tr><td><b>%s</b></td><td>%s</td><td>%s</td><td class="sk">%s</td></tr>'
                           % (E(a), M(b), M(c), E(d)) for a, b, c, d in sr["rows"])
            extra = """
<h3 class="sub">%d.1 %s</h3>
<div class="tw"><table class="data"><caption>Table %d. The acceptance surface.</caption>
<thead><tr><th>Property</th><th>Requirement</th><th>Why</th><th>Src</th></tr></thead>
<tbody>%s</tbody></table></div>
<div class="note"><b>Where the walk gate comes from.</b>
Our MuJoCo run of Pollen's <code>%s</code> walked <b>%.4f&nbsp;m in %.1f&nbsp;s</b> at a commanded
0.25&nbsp;m/s, with a maximum trunk tilt of <b>%.2f&nbsp;degrees</b> and no fall — and the stock-mesh and swapped-mesh
models produced bit-identical trajectories, so that figure is Pollen's physics, not ours.
The acceptance gate is <b>%.3f&nbsp;m</b>, which is <b>%.0f&nbsp;%%</b> of it. <b>That fraction is a decision of this
plan and not a measurement of anything</b>: no real-robot walk distance exists in this repository or in Pollen's
published material. The tilt gate, by contrast, is derived —
<code class="formula">acos(%.2f) = %.3f&nbsp;degrees</code> is <code>limp_fall_tilt_z</code>, the tilt at which
robotd itself decides a fall has started; the fall <i>report</i> threshold
<code>fall_gravity_z = %.1f</code> is <code class="formula">acos(%.1f) = %.3f&nbsp;degrees</code>.</div>
""" % (SECNUM["walk"], E(sr["title"]), TN(), rows,
       E(SIM_WALK_POLICY), SIM_WALK_M, SIM_WALK_S, SIM_WALK_TILT, GATE_WALK_M, GATE_FRACTION * 100,
       -LIMP_FALL_TILT_Z, LIMP_TILT_DEG, FALL_GRAVITY_Z, -FALL_GRAVITY_Z, FALL_TILT_DEG)
        if s["id"] == "radios":
            pm = D["padmap"]
            extra = """
<h3 class="sub">%d.1 %s</h3>
<div class="tw"><table class="data"><caption>Table %d. %s</caption>
<thead><tr><th>Control</th><th>What it does</th></tr></thead>
<tbody>%s</tbody></table></div>
""" % (SECNUM["radios"], E(pm["title"]), TN(), M(pm["note"]), padmap_table())
        if s["id"] == "endurance":
            rt = RUNTIME["outputs"]["runtime_table"]
            pc = RUNTIME["outputs"]["pollen_claim"]
            wh = RUNTIME["inputs"]["pack"]["Wh"]
            w_lo = rt["walking"]["rows"][-1]["runtime_min"]
            w_hi = rt["walking"]["rows"][0]["runtime_min"]
            extra = """
<h3 class="sub">%d.1 What EN-01 should find, and the number it settles</h3>
<div class="tw"><table class="data"><caption>Table %d. Runtime against compute draw, from
<code>out/sim-evidence/battery-runtime.json</code> &mdash; the measured MuJoCo torque and speed profile
through ROBOTIS's published XL330 rows, on a %.1f&nbsp;Wh pack. The compute-and-sensor column is SWEPT,
not known: no vendor states the Radxa ZERO&nbsp;3W's consumption, so EN-01 is what picks the row.</caption>
<thead><tr><th>compute + sensors&nbsp;W</th><th>total&nbsp;W walking</th><th>walking&nbsp;min</th>
<th>standing&nbsp;min</th><th>idle, torque off&nbsp;min</th><th>pack&nbsp;A at 7.4&nbsp;V</th></tr></thead>
<tbody>%s</tbody></table></div>
<div class="note"><b>Our model and Pollen's claim disagree by a factor of about two, and EN-01 is the
measurement that says which is wrong.</b> The press kit says <b>~%.1f&nbsp;h</b>; a %.1f&nbsp;Wh pack over
that hour is an average of <b>%.1f&nbsp;W</b> for the whole machine. This model puts walking servo draw at
<b>%.4f&nbsp;W</b>, which leaves <b>%.4f&nbsp;W</b> for everything else &mdash; %.1f&nbsp;%% of Radxa's entire
5&nbsp;V/2&nbsp;A adapter rating for the board, which is implausible for compute alone. So the missing power
is more likely the XL330's unpublished no-load current (set to zero here, and multiplied by fifteen), PWM-stage
loss (taken as zero), and pack energy below the 6.6&nbsp;V cut-off that is never delivered &mdash; or the
published hour is a mixed-use hour rather than an hour of walking. Our band for continuous walking is
<b>%.1f&ndash;%.1f&nbsp;min</b> across the compute sweep, and every figure in it is an UPPER bound.
One ammeter in the pack lead, plus <code>Present&nbsp;Current(126)</code> summed off the bus, separates the
servo half from the board half and closes all of it.</div>
""" % (SECNUM["endurance"], TN(), wh, runtime_table(),
       pc["claimed_h"], wh, pc["implied_total_average_W"],
       pc["measured_servo_average_W_walking"], pc["implied_compute_and_sensors_W"],
       100.0 * pc["implied_compute_and_sensors_W"] / 10.0, w_lo, w_hi)
        tests = "".join(test_block(t) for t in s["tests"])
        out.append("""
<section id="%s">
  <h2><span class="n">%s</span>%s</h2>
  <p class="lede">%s</p>
  %s
  %s
</section>""" % (s["id"], SECNUM[s["id"]], E(s["title"]), M(s.get("lede", "")), extra, tests))
    return "\n".join(out)

def eol_table():
    return "\n".join(
        '<tr><td class="box">&#9744;</td><td><a href="#%s"><code>%s</code></a></td><td>%s</td><td class="sk">%s</td></tr>'
        % (E(i), E(i), M(g), M(t)) for i, g, t in D["eol"])

def logs_table():
    return "\n".join('<tr><td><code>%s</code></td><td>%s</td><td class="sk">%s</td></tr>'
                     % (E(a), M(b), E(c)) for a, b, c in D["logs"])

def open_table():
    return "\n".join(
        '<tr><td>%s</td><td><a href="#%s"><code>%s</code></a></td><td>%s</td><td>%s</td></tr>'
        % (M(o["q"]), E(o["test"].split(",")[0].strip()), E(o["test"]), M(o["status"]), M(o["settles"]))
        for o in D["open"])

def sources_table():
    return "\n".join('<tr><td><code>%s</code></td><td>%s</td><td class="loc">%s</td></tr>'
                     % (E(k), M(v["label"]), M(v["loc"])) for k, v in D["sources"].items())

TOC = "".join('<a href="#%s"><span class="tn">%s</span>%s</a>' % (sec["id"], SECNUM[sec["id"]], E(sec["title"]))
              for sec in D["sections"])
TOC += "".join('<a href="#%s"><span class="tn">%s</span>%s</a>' % (sid, TAILNUM[sid], E(title))
               for sid, title in TAIL)

# 1.2, resolved against the sections that exist rather than typed
ORDER = "".join("<li><b>Section %d &mdash; %s.</b> %s</li>"
                % (SECNUM[sid], E([x for x in D["sections"] if x["id"] == sid][0]["title"]).lower(), M(text))
                for sid, text in D["order"])

def resolved_html():
    """What was open in an earlier revision and is now settled, with the evidence that
    settled it. A question that stops appearing looks like a question nobody asked."""
    out = []
    for r in D.get("resolved", []):
        out.append("""
<div class="resolved">
  <h4>%s</h4>
  <p><span class="k">Was</span>%s</p>
  <p><span class="k">Now</span>%s</p>
  <p><span class="k">So</span>%s</p>
  %s
</div>""" % (M(r["q"]), M(r["was"]), M(r["now"]), M(r["consequence"]), srcline(r.get("src", []))))
    return "".join(out)

DOC = D["doc"]
HTML = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Test &amp; Validation Plan</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opt_sz,wght@8..60,400;8..60,600;8..60,700&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="tools/doc.css">
<style>
  .srcs{{font-family:var(--sans);font-size:11px;color:var(--ink-2);margin-top:10px;
        display:flex;flex-wrap:wrap;gap:3px 16px;border-top:1px solid var(--hair);padding-top:7px}}
  .srcs b{{font-family:var(--mono);font-weight:500;color:var(--accent);margin-right:5px}}
  td.sk,.sk{{font-family:var(--mono);font-size:11px;color:var(--ink-2)}}
  td.basis,.basis{{font-size:12px;color:var(--ink-2);max-width:34em}}
  td.loc{{font-family:var(--mono);font-size:11px;color:var(--ink-2);word-break:break-all}}
  article.test{{border-top:1.5px solid var(--rule);padding:16px 0 20px;margin:0}}
  article.test h3{{font-size:16.5px;margin:0 0 4px;display:flex;gap:12px;align-items:baseline}}
  .tid{{font-family:var(--mono);font-size:13px;font-weight:600;color:var(--accent);
       border:1px solid var(--accent);padding:1px 7px;white-space:nowrap}}
  .purpose{{font-size:14.5px;color:var(--ink-2);margin:0 0 10px;max-width:44em}}
  article.test h4{{font-family:var(--sans);font-size:11px;letter-spacing:.06em;text-transform:uppercase;
                  color:var(--ink-2);font-weight:600;margin:14px 0 5px}}
  .meta{{display:flex;flex-wrap:wrap;gap:4px 30px;font-size:12.5px;font-family:var(--sans);
        color:var(--ink-2);border-left:2px solid var(--hair);padding-left:12px;margin:8px 0}}
  .meta .k{{display:inline-block;min-width:36px;font-size:10.5px;letter-spacing:.06em;
           text-transform:uppercase;color:var(--ink-2);margin-right:8px}}
  ul.pre,ol.steps{{margin:4px 0 0;padding-left:22px;font-size:14px;max-width:46em}}
  ol.steps>li{{margin:7px 0}}
  .cmd{{font-family:var(--mono);font-size:12px;background:var(--figbg);border:1px solid var(--hair);
       padding:5px 10px;margin:5px 0 3px;overflow-x:auto;white-space:pre}}
  .exp{{font-family:var(--sans);font-size:12px;color:var(--ink-2)}}
  p.measure{{font-size:14px;margin:0;max-width:46em}}
  table.gate{{width:auto;min-width:min(100%,640px)}}
  table.gate td{{border-bottom:1px solid var(--hair);font-size:13.5px}}
  table.gate td.v{{font-family:var(--sans);font-weight:600;font-size:11px;letter-spacing:.05em;
                  white-space:nowrap;width:1%;padding-right:18px;vertical-align:top}}
  td.v.pass{{color:var(--ready)}} td.v.fail{{color:var(--no)}} td.v.cd{{color:var(--partial)}}
  .basisbox{{border-left:2px solid var(--accent);background:var(--figbg);padding:9px 14px;
            margin:12px 0 0;font-size:12.5px;color:var(--ink);max-width:48em}}
  .basisbox .k{{display:block;font-family:var(--sans);font-size:10.5px;letter-spacing:.06em;
               text-transform:uppercase;color:var(--ink-2);font-weight:600;margin-bottom:4px}}
  h3.sub{{font-size:16px;margin:26px 0 6px;border-bottom:1px solid var(--hair);padding-bottom:4px}}
  code.formula{{background:var(--figbg);border:1px solid var(--hair);padding:1px 6px}}
  table.reg td{{font-size:12.5px}}
  td.box{{font-size:17px;width:1%;padding-right:2px;color:var(--ink-2)}}
  table.data caption{{caption-side:top;text-align:left;font-family:var(--sans);font-size:11.5px;
                     color:var(--ink-2);padding:0 0 7px;max-width:52em}}
  .cd{{color:var(--partial)}}
  .pending{{color:var(--ink-2)}} .pending i{{font-size:.9em}}
  table.idmap th,table.idmap td{{padding:5px 7px;font-size:12.5px}}
  table.idmap td:nth-child(2),table.idmap td:nth-child(3){{font-size:12px}}
  table.idmap th{{font-size:10px;letter-spacing:.03em}}
  nav.toc .tn{{font-family:var(--mono);color:var(--accent);margin-right:6px;font-size:11.5px}}
  section>h2 .n{{font-family:var(--mono);font-weight:600;color:var(--accent);font-size:18px;padding-right:14px}}
  .statbar .stat{{padding:12px 18px 12px 0;margin-right:14px}}
  .statbar .stat b{{font-size:20px}}
  .resolved{{border-left:2px solid var(--ready);background:var(--figbg);padding:10px 16px;margin:14px 0}}
  .resolved h4{{font-size:14.5px;margin:0 0 6px}}
  .resolved p{{font-size:13px;margin:5px 0;max-width:52em}}
  .resolved .k{{display:inline-block;min-width:44px;font-family:var(--sans);font-size:10.5px;
               letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2);font-weight:600;margin-right:8px}}
  @media(max-width:680px){{.meta{{flex-direction:column;gap:2px}}}}
</style>
</head>
<body>
<div class="wrap">
<p class="backlink">{link("RELEASE.html", "&larr; Release dossier")} &middot; {link("INDEX.html", "Document index")}</p>

<header class="hero">
  <p class="eyebrow">Microduck reverse-engineering &middot; {E(DOC['lane'])}</p>
  <h1>{E(DOC['title'])}</h1>
  <p class="sub">{E(DOC['sub'])}</p>
  <div class="rev">
    <span>{E(DOC['id'])} &middot; Rev {E(DOC['rev'])}</span><span>{E(DOC['date'])}</span>
    <span>units {E(DOC['units'])}</span>
    <span>generated by <code>tools/gen_test_plan.py</code> from <code>spec/test-plan.json</code></span>
  </div>
</header>

<div class="statbar">
  <div class="stat"><b>{n_tests}</b><span>numbered tests</span></div>
  <div class="stat"><b>{len(D['eol'])}</b><span>end-of-line gates</span></div>
  <div class="stat"><b>{n_notest}</b><span>subsystems with no test, and why</span></div>
  <div class="stat"><b>{n_open}</b><span>open questions, each with what settles it</span></div>
  <div class="stat"><b>{len(D['sources'])}</b><span>cited sources</span></div>
</div>

<nav class="toc">{TOC}</nav>

<section id="scope">
  <h2><span class="n">1</span>Scope, verdicts and order</h2>
  <p class="lede">This plan proves one built unit. It is not a design review and it is not a DFM check &mdash;
  those are {link("MANUFACTURING-PLAYBOOK.html", "the manufacturing playbook", "lane G, not yet in the repository")} and
  {link("out/drawings/INDEX.html", "the mechanical drawings", "lane B, not yet in the repository")}. It starts at a fully assembled robot that has never
  been powered and ends at a robot that has walked.</p>

  <h3 class="sub">1.1 Three verdicts</h3>
  <div class="tw"><table class="data"><caption>Table 1. Every gate in this document answers with exactly one of these.</caption>
  <thead><tr><th>Verdict</th><th>Means</th><th>What it does to the unit</th></tr></thead>
  <tbody>
    <tr><td><span class="chip pass">PASS</span></td><td>the stated quantity was measured and it is inside the stated band</td><td>proceed to the next test</td></tr>
    <tr><td><span class="chip rail">FAIL</span></td><td>the stated quantity was measured and it is outside the stated band</td><td>stop. The unit does not proceed and does not ship</td></tr>
    <tr><td><span class="chip cd">CANNOT DETERMINE</span></td><td>the quantity could not be measured, or no band exists to judge it against</td><td><b>not a pass.</b> Record the value that was seen, the reason it cannot be judged, and what would settle it</td></tr>
  </tbody></table></div>
  <div class="note"><b>Never loosen a gate to make a unit pass.</b> A gate that a good unit fails is a defect in
  this document and is fixed by regenerating it from
  <code>spec/test-plan.json</code> with the new basis written down &mdash; never by widening a band in the
  field. Every gate below carries a <i>basis</i> block naming whether the number came from a vendor
  datasheet, from Pollen's own source, from our simulation, or from a decision of this plan.</div>

  <h3 class="sub">1.2 Order, and why it is this order</h3>
  <ol class="steps">{ORDER}</ol>
  <div class="note"><b>The stand is not optional.</b> <code>robotctl robot init</code> powers the joints and
  ramps to the home pose over about two seconds &mdash; <b>it moves every joint</b>. Pollen's own cheat sheet
  says it plainly: have the robot on its stand. Every test before section 7 runs with both feet clear
  of the bench.</div>
</section>

{sections_html()}

<section id="eol">
  <h2><span class="n">{TAILNUM["eol"]}</span>End-of-line checklist</h2>
  <p class="lede">{M(D["eol_note"])}</p>
  <div class="tw"><table class="data"><caption>Table {TN()}. End-of-line gates, {len(D['eol'])} of them.</caption>
  <thead><tr><th></th><th>Test</th><th>Gate</th><th>Instrument</th></tr></thead>
  <tbody>{eol_table()}</tbody></table></div>
</section>

<section id="logs">
  <h2><span class="n">{TAILNUM["logs"]}</span>The log a unit leaves behind</h2>
  <p class="lede">A unit's record is a directory, and it is the only thing that survives the unit leaving
  the bench. Two of these files outlive a power cut and the rest do not &mdash; copy the volatile ones
  before the next boot.</p>
  <div class="tw"><table class="data"><caption>Table {TN()}. What is kept, and why it is kept.</caption>
  <thead><tr><th>Path</th><th>What it is</th><th>Src</th></tr></thead>
  <tbody>{logs_table()}</tbody></table></div>
</section>

<section id="open">
  <h2><span class="n">{TAILNUM["open"]}</span>What this plan cannot test, and what would change that</h2>
  <p class="lede">These {n_open} questions are open because a fact is missing, not because a test is
  missing. Each names the test that would answer it and exactly what has to exist first. Most are
  answered the first time a real unit is put on a bench &mdash; which is the point of writing them
  down here rather than leaving them out. The rest need a teardown or a Pollen release, and say so.</p>
  <div class="tw"><table class="data"><caption>Table {TN()}. Open questions, each with the test that closes it.</caption>
  <thead><tr><th>Question</th><th>Test</th><th>Status today</th><th>What settles it</th></tr></thead>
  <tbody>{open_table()}</tbody></table></div>

  <h3 class="sub">{TAILNUM["open"]}.1 What was open in Rev&nbsp;A and is settled now</h3>
  <p>A question that simply stops appearing looks like a question nobody asked. These were open, and
  each one is closed here by a source rather than by a decision.</p>
  {resolved_html()}
</section>

<section id="sources">
  <h2><span class="n">{TAILNUM["sources"]}</span>Sources</h2>
  <p class="lede">Pollen Robotics' firmware and software are Apache-2.0 and are read here line by line;
  their PCBs are not published. Vendor datasheets are stored in the shelf with their provenance.
  Everything below is either in this repository or was fetched on the date named.</p>
  <div class="tw"><table class="data"><caption>Table {TN()}. Every source cited by a gate in this document.</caption>
  <thead><tr><th>Key</th><th>What</th><th>Where</th></tr></thead>
  <tbody>{sources_table()}</tbody></table></div>
</section>

<footer>
  <span>{E(DOC['id'])} Rev {E(DOC['rev'])} &middot; {E(DOC['date'])}</span>
  <span>Regenerate: <code>python3 tools/gen_test_plan.py</code></span>
  <span>Data: <code>spec/test-plan.json</code></span>
  <span>Serve: <code>tools/serve.sh</code> &rarr; localhost:8842/TEST-PLAN.html</span>
</footer>

</div>
</body>
</html>
"""

out = os.path.join(REPO, "TEST-PLAN.html")
open(out, "w").write(HTML)
print("wrote TEST-PLAN.html  tests=%d eol=%d open=%d sources=%d  bytes=%d"
      % (n_tests, len(D["eol"]), n_open, len(D["sources"]), len(HTML)))
print("derived: 1 count = %.6f deg; tol %.1f deg = %d counts; "
      "limp tilt = %.4f deg; fall report tilt = %.4f deg; walk gate = %.3f m (%.0f%% of %.4f m)"
      % (DEG_PER_COUNT, TOL_DEG, TOL_COUNT, LIMP_TILT_DEG, FALL_TILT_DEG,
         GATE_WALK_M, GATE_FRACTION*100, SIM_WALK_M))
