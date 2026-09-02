#!/usr/bin/env python3
"""gen_test_plan.py — build TEST-PLAN.html from spec/test-plan.json.

Lane H of GOAL.md. The JSON is the data; every derived number (degrees,
encoder counts, the count tolerance) is computed HERE and shown with its
formula, so no derived figure is hand-maintained anywhere.

    python3 tools/gen_test_plan.py       # exits 0, or non-zero having written nothing

selfcheck() runs before a byte is written and REFUSES to publish a document
the data does not support: an unresolved source key, an end-of-line row that
names no test, a gated test on neither the checklist nor the exemption list,
an @TOKEN@ that nothing filled, an id_map range that disagrees with the MJCF.
Every one of those was broken on purpose once and watched to fire.

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

def _mjcf_ranges(rel="sim/microduck_ours.xml"):
    """Joint limits are READ off the MJCF MuJoCo actually loaded, never retyped. The copy in
    spec/test-plan.json is a cross-check, and selfcheck() fails if the two disagree."""
    fp = os.path.join(REPO, rel)
    if not os.path.exists(fp):
        raise SystemExit("gen_test_plan: %s is missing; the ID map has no range source" % rel)
    src = open(fp).read()
    return {m.group(1): (float(m.group(2)), float(m.group(3))) for m in
            re.finditer(r'<joint[^>]*name="([^"]+)"[^>]*range="([-\d.eE+]+) ([-\d.eE+]+)"', src)}

MJCF_RANGE = _mjcf_ranges()
MJCF_FILE  = "sim/microduck_ours.xml"
# The mouth is the one id_map row with no MJCF joint: the jaw is not actuated in the published
# model. Its limits are model.rs:63-64 MOUTH_CLOSED / MOUTH_OPEN, in degrees, converted here.
RANGE_EXEMPT = {"mouth": ("model.rs:63-64 MOUTH_CLOSED = -5 deg, MOUTH_OPEN = +30 deg; "
                          "the jaw is not a joint in the published MJCF")}

E = lambda s: html.escape(str(s), quote=False)

# ---- @TOKEN@ substitution -------------------------------------------------
# A number a gate rests on is never typed into the data file. The data writes @NAME@ and the
# value is filled here from a measured artifact or a computed constant. An unresolved token is
# a hard failure, not a literal "@NAME@" shipped to the reader.
TOK = {}
_TOKRE = re.compile(r"@([A-Z0-9_]+)@")
def _fill(t):
    def sub(m):
        k = m.group(1)
        if k not in TOK:
            raise SystemExit("gen_test_plan: unresolved token @%s@ in the data file" % k)
        return str(TOK[k])
    return _TOKRE.sub(sub, str(t))

_CODE = re.compile(r"`([^`]+)`")
_BOLD = re.compile(r"\*\*([^*]+)\*\*")
def M(t):
    """Fill @TOKEN@s, then escape, then render `backticked` spans as <code> and **starred**
    spans as <b>. Prose in the data file is written the way the source documents write it; this
    is the one place that turns it into markup, so NO field ever carries raw HTML — a field that
    did would either be escaped and shown as tags to the reader, or trusted and able to
    break the page."""
    return _BOLD.sub(lambda m: "<b>%s</b>" % m.group(1),
                     _CODE.sub(lambda m: "<code>%s</code>" % m.group(1), E(_fill(t))))

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

_SV01 = None
for _s in D["sections"]:
    if _s["kind"] == "tests":
        for _t in _s["tests"]:
            if _t["id"] == "SV-01": _SV01 = _t
if _SV01 is None or "readback" not in _SV01:
    raise SystemExit("gen_test_plan: SV-01 has no readback[] - the read-back count cannot be derived")
_RB = _SV01["readback"]
_WORDS = {0:"no",1:"one",2:"two",3:"three",4:"four",5:"five",6:"six",7:"seven",8:"eight",
          9:"nine",10:"ten",11:"eleven",12:"twelve"}

_WARM = float(_WALK["command"]["warmup_s"])
TOK.update({
  "SIM_WALK_POLICY":       SIM_WALK_POLICY,
  "SIM_WALK_M":            "%.4f" % SIM_WALK_M,
  "SIM_WALK_S":            "%.1f" % SIM_WALK_S,
  "SIM_WALK_X":            "%.4f" % _WALK["walked_x_m"],
  "SIM_WALK_SPEED_WINDOW": "%.4f" % _WALK["mean_speed_m_s_commanded_window"],
  "SIM_WALK_WARMUP_S":     "%.1f" % _WARM,
  "SIM_WALK_WINDOW_S":     "%.1f" % (SIM_WALK_S - _WARM),
  "SIM_WALK_MEAN_ALL":     "%.4f" % (SIM_WALK_M / SIM_WALK_S),
  "SIM_WALK_TILT":         "%.2f" % SIM_WALK_TILT,
  "GATE_WALK_M":           "%.3f" % GATE_WALK_M,
  "GATE_PCT":              "%.0f" % (GATE_FRACTION * 100),
  "LIMP_TILT_DEG":         "%.3f" % LIMP_TILT_DEG,
  "TOL_COUNT":             "%d"   % TOL_COUNT,
  "TOL_DEG_OF_COUNT":      "%.4f" % (TOL_COUNT * DEG_PER_COUNT),
  "SV01_READBACK_N":       "%d"   % len(_RB),
  "SV01_READBACK_WORD":    _WORDS[len(_RB)],
  "SV01_SCAN_N":           _WORDS[len([r for r in _RB if r[1] == "scan"])],
  "SV01_WRITTEN_N":        _WORDS[len([r for r in _RB if r[1] == "written"])],
  "SV01_VERIFY_N":         _WORDS[len([r for r in _RB if r[1] == "verify"])],
  "N_RAILS":               "%d" % len(D["rails"]),
})

SECNUM = {sec["id"]: i + 2 for i, sec in enumerate(D["sections"])}
# Section numbers as tokens, so a cross-reference in the data file cannot go stale when a
# section is inserted: "section @SEC_WALK@.1" survives what "section 7.1" did not.
TOK.update({("SEC_%s" % sec["id"].upper()): SECNUM[sec["id"]] for sec in D["sections"]})
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

LINKS = []      # (href, resolved?) — every cross-document link this page tried to make
def link(href, text, note="not yet in the repository"):
    """A link is only written when the target is on disk. A cross-lane document that has
    not landed yet renders as plain text with the reason, so this page never ships a
    dead link and heals itself the moment the file appears — but only on the next run, so
    every one is recorded here and the run prints the tally. A committed page whose tally
    disagrees with the repository is a page that needs regenerating, and now says so."""
    ok = os.path.exists(os.path.join(REPO, href.split("#")[0]))
    LINKS.append((href, ok))
    if ok:
        return '<a href="%s">%s</a>' % (href, text)
    return '<span class="pending">%s <i>(%s)</i></span>' % (text, E(note))

# ---- source resolution ---------------------------------------------------
SRC      = D["sources"]
SRC_USED = {}        # key -> [what cited it], filled as the document renders
_CITER   = ["the document"]
def srcline(keys):
    if not keys: return ""
    out = []
    for k in keys:
        s = SRC.get(k)
        if s is None:
            # A citation that renders its own key as its label looks like a source and is not
            # one. Refuse, name the key, and let selfcheck() list every offender at once.
            raise SystemExit("gen_test_plan: source key %r is cited but not in sources{}" % k)
        SRC_USED.setdefault(k, []).append(_CITER[0])
        out.append('<span class="srcitem"><b>%s</b> %s</span>' % (E(k), E(s["label"])))
    return '<div class="srcs">%s</div>' % "".join(out)

# ---- counters ------------------------------------------------------------
all_tests = [t for s in D["sections"] if s["kind"] == "tests" for t in s["tests"]]
TESTBYID  = {t["id"]: t for t in all_tests}
n_tests   = len(all_tests)
n_notest  = len([t for t in all_tests if t["gate"]["PASS"] == "—"])
n_open    = len(D["open"])

# ---- fragments -----------------------------------------------------------
def tools_of(tid, seen=None):
    """A test's instruments, resolving an `as WK-02` delegation rather than treating the
    literal string as an instrument. Used by the equipment cross-check."""
    seen = seen or set()
    if tid in seen or tid not in TESTBYID: return []
    seen.add(tid)
    out = []
    for x in TESTBYID[tid]["tool"]:
        m = re.fullmatch(r"as ([A-Z]{2}-\d{2})", str(x).strip())
        if m and m.group(1) in TESTBYID: out += tools_of(m.group(1), seen)
        else: out.append(x)
    return out

def equip_table():
    """The 'serves' column is a list of test ids in the data, rendered as links, and
    selfcheck() requires the row's tool_key to appear literally in each of those tests'
    tool lists. Prose used to carry the test numbers and three of them had gone stale
    (the ToF target said SN-05, which is the LSM6DSV16X)."""
    rows = []
    for row in D["equipment"]:
        name, what, why, sk = row[0], row[1], row[2], row[3]
        serves = row[4] if len(row) > 4 else []
        links = " ".join('<a href="#%s"><code>%s</code></a>' % (E(i), E(i)) for i in serves)
        rows.append('<tr><td><b>%s</b></td><td>%s</td><td>%s<div class="sk">%s</div></td>'
                    '<td class="sk">%s</td></tr>'
                    % (E(name), M(what), M(why), links, E(sk)))
    return "\n".join(rows)

def idmap_table():
    """Ranges come from MJCF_RANGE, i.e. off sim/microduck_ours.xml, not from the data file.
    They are shown in radians AND degrees because every one of them is an exact whole number
    of degrees, which rounding to 3 dp in radians hid."""
    rows = []
    for sid, joint, body, rng, home in D["id_map"]:
        lo, hi = MJCF_RANGE.get(joint, tuple(rng))
        rows.append(
          '<tr><td class="n">%d</td><td><code>%s</code></td><td>%s</td>'
          '<td class="n">%.4f</td><td class="n">%.4f</td>'
          '<td class="n">%.4f</td><td class="n">%.4f</td>'
          '<td class="n">%.4f</td><td class="n">%.4f</td><td class="n">%.1f</td></tr>'
          % (sid, E(joint), E(body), lo, hi, rad2deg(lo), rad2deg(hi),
             home, rad2deg(home), rad2count(home)))
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
    _CITER[0] = t["id"]          # so the sources table can say who cited what
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
  <thead><tr><th>Instrument or fixture</th><th>Used by</th><th>Why this and not something looser, and the gates it serves</th><th>Src</th></tr></thead>
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
            # Table numbers are taken before the string is built so SV-01 can cite the register
            # table by number through @T_REG@ without anyone typing "Table 5".
            _t_idmap, _t_reg = TN(), TN()
            TOK["T_IDMAP"], TOK["T_REG"] = _t_idmap, _t_reg
            extra = """
<h3 class="sub" id="idmap">%d.1 The ID map, and the home pose in counts</h3>
<p>Encoder counts are computed here, not typed:
<code class="formula">count = %d + rad &times; %d / (2&pi;) = %d + rad &times; %.6f</code>,
from the vendor's 4096&nbsp;pulse/rev resolution and <code>bus.rs</code>'s 2048 = 0&nbsp;rad.
One count is <b>%.4f&nbsp;degrees</b>, so the &plusmn;%.1f&nbsp;degree calibration tolerance is
<b>&plusmn;%d&nbsp;counts</b>.</p>
<div class="tw"><table class="data idmap"><caption>Table %d. Servo ID to joint, the joint's MJCF range, and the home pose
in radians, degrees and encoder counts. Home values are <code>DEFAULT_POSITION</code> from <code>model.rs:39-55</code>;
ranges are read here directly out of <code>sim/microduck_ours.xml</code> at full double precision, and every one of
them turns out to be an exact whole number of degrees &mdash; which is why the degree columns are here and why the
data file&rsquo;s 3&nbsp;dp copies were wrong to keep. The mouth (ID&nbsp;34) is the one row with no MJCF joint: the
jaw is not actuated in the published model, and its limits are <code>model.rs:63-64</code>.</caption>
<thead><tr><th>ID</th><th>Joint</th><th>Body carrying the servo</th>
<th>range lo&nbsp;rad</th><th>range hi&nbsp;rad</th><th>range lo&nbsp;deg</th><th>range hi&nbsp;deg</th>
<th>home&nbsp;rad</th><th>home&nbsp;deg</th><th>home&nbsp;count</th></tr></thead>
<tbody>%s</tbody></table></div>
<div class="note"><b>ID 200 is not in this table.</b> The <code>imu_to_dxl</code> v2 board rides the same bus as a
sixteenth device and is <code>sync_read</code> first on every tick. It has no joint, no range and no home pose —
but SV-03 fails without it.</div>

<h3 class="sub" id="registers">%d.2 The register set</h3>
<p>Every value below is quoted from the vendor control table in <code>ce-parts/xl330-m288-t/electrical.chip.json</code>.
<b>EEPROM writes are refused unless Torque&nbsp;Enable(64) is 0</b> — the vendor's own rule, and the reason it is the
first row of every write sequence.</p>
<div class="tw"><table class="data reg"><caption>Table %d. The XL330-M288-T registers this plan touches.</caption>
<thead><tr><th>Addr</th><th>Bytes</th><th>Name</th><th>Area</th><th>Vendor initial</th><th>We write</th><th>Meaning</th><th>Why</th></tr></thead>
<tbody>%s</tbody></table></div>
""" % (SECNUM["servo"], ZERO_COUNT, RESOLUTION_PULSE_REV, ZERO_COUNT, COUNT_PER_RAD,
       DEG_PER_COUNT, TOL_DEG, TOL_COUNT, _t_idmap, idmap_table(),
       SECNUM["servo"], _t_reg, reg_table())
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
measurement that says which is wrong.</b> The press kit says <b>~%.1f&nbsp;h</b>, and %.1f&nbsp;Wh delivered over
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
    """The cited-by column is measured, not claimed: SRC_USED is filled by srcline() as the
    document renders, so a source nothing rests on says so in its own row."""
    rows = []
    for k, v in D["sources"].items():
        who = SRC_USED.get(k, [])
        seen, ordered = set(), []
        for w in who:
            if w not in seen:
                seen.add(w); ordered.append(w)
        if ordered:
            cite = ", ".join(ordered[:6]) + ("&hellip;" if len(ordered) > 6 else "")
            cls = "sk"
        else:
            cite = "<i>recorded, cited by no gate</i>"
            cls = "sk cd"
        rows.append('<tr><td><code>%s</code></td><td>%s</td><td class="%s">%s</td><td class="loc">%s</td></tr>'
                    % (E(k), M(v["label"]), cls, cite, M(v["loc"])))
    return "\n".join(rows)

def eol_exempt_table():
    return "\n".join(
        '<tr><td><a href="#%s"><code>%s</code></a></td><td>%s</td><td>%s</td></tr>'
        % (E(i), E(i), M(why), M(what)) for i, why, what in D.get("eol_exempt", []))

def corrections_html():
    out = []
    for c in D.get("corrections", []):
        _CITER[0] = "&sect;1.3"
        out.append("""
<div class="resolved">
  <h4>%s</h4>
  <p><span class="k">Measured</span>%s</p>
  <p><span class="k">Now</span>%s</p>
  %s
</div>""" % (M(c["what"]), M(c["measured"]), M(c["now"]), srcline(c.get("src", []))))
    return "".join(out)

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
        _CITER[0] = "&sect;%d.1" % TAILNUM["open"]
        out.append("""
<div class="resolved">
  <h4>%s</h4>
  <p><span class="k">Was</span>%s</p>
  <p><span class="k">Now</span>%s</p>
  <p><span class="k">So</span>%s</p>
  %s
</div>""" % (M(r["q"]), M(r["was"]), M(r["now"]), M(r["consequence"]), srcline(r.get("src", []))))
    return "".join(out)

# ---- the refusals ---------------------------------------------------------
CHECKS = [
 ("every eol row names a real test",
  "an end-of-line row that points at no test is a box nobody can tick"),
 ("every test with a PASS gate is on the eol list or on the exemption list",
  "this is the check that was missing: 10 gated tests, including the only safety-behaviour "
  "test in the plan, were absent from the ship checklist and nothing noticed"),
 ("every eol exemption names a real test, and that test is NOT also on the eol list",
  "an exemption for a row that is on the list is a contradiction, not a decision"),
 ("every source key cited anywhere resolves in sources{}",
  "srcline() used to print the raw key as its own label, so a broken citation rendered as a "
  "plausible-looking source"),
 ("every test id is unique",
  "two tests sharing an id give the checklist an ambiguous anchor"),
 ("every open-question row names a real test",
  "section on what cannot be tested must point at the test that would close it"),
 ("every id_map joint's stored range equals the MJCF range to 1e-9 rad, or is exempt with a reason",
  "the data file used to carry them rounded to 3 dp, which discarded exact whole-degree limits"),
 ("every SV-01 read-back address exists in the register table",
  "the read-back count is derived from that list, so the list has to be real"),
 ("every equipment row's tool_key appears literally in the tool list of every test it says it serves",
  "the instrument table named its gates in prose and three had gone stale: the 88 % reflectance "
  "target said it served SN-05, which is the LSM6DSV16X chip self-test, not the ToF ranging test"),
 ("every register address is unique",
  "a duplicated address in Table 5 would be quoted twice with different values"),
 ("no unfilled at-sign token survives into the finished HTML",
  "the data file writes a measured number as an at-sign token that this generator fills; an "
  "unfilled one would ship to the reader as literal punctuation where a number belongs"),
 ("the finished HTML contains every test id and every eol id as an anchor",
  "a checklist link that scrolls nowhere is a checklist nobody uses"),
]

def selfcheck(doc=None):
    """Refuse to publish what the data does not support. Returns a list of failures; the caller
    exits non-zero on any. Run twice: once before rendering, once on the finished HTML."""
    bad = []
    ids = [t["id"] for t in all_tests]
    byid = {t["id"]: t for t in all_tests}
    eol_ids = [e[0] for e in D["eol"]]
    ex_ids  = [e[0] for e in D.get("eol_exempt", [])]

    if doc is None:
        for i in eol_ids:
            if i not in byid: bad.append("eol row %r names no test" % i)
        gated = [t["id"] for t in all_tests if t["gate"].get("PASS", "—") != "—"]
        for i in gated:
            if i not in eol_ids and i not in ex_ids:
                bad.append("test %s has a PASS gate but is on neither the end-of-line list nor the "
                           "exemption list" % i)
        for i in ex_ids:
            if i not in byid: bad.append("eol_exempt row %r names no test" % i)
            if i in eol_ids:  bad.append("%s is both exempt and on the checklist" % i)
        seen = set()
        for i in ids:
            if i in seen: bad.append("duplicate test id %s" % i)
            seen.add(i)
        for o in D["open"]:
            for i in [x.strip() for x in o["test"].split(",")]:
                if i not in byid: bad.append("open question points at %r, which is no test" % i)
        for t in all_tests:
            for k in t["src"]:
                if k not in SRC: bad.append("%s cites unknown source key %r" % (t["id"], k))
        for r in D.get("resolved", []) + D.get("corrections", []):
            for k in r.get("src", []):
                if k not in SRC: bad.append("a section-1.3/11.1 block cites unknown source key %r" % k)
        for sid, joint, body, rng, home in D["id_map"]:
            if joint in MJCF_RANGE:
                lo, hi = MJCF_RANGE[joint]
                if abs(lo - rng[0]) > 1e-9 or abs(hi - rng[1]) > 1e-9:
                    bad.append("id_map %s range %r disagrees with %s %r"
                               % (joint, rng, MJCF_FILE, (lo, hi)))
            elif joint not in RANGE_EXEMPT:
                bad.append("id_map %s has no MJCF joint and no stated exemption" % joint)
        for n, row in enumerate(D["equipment"]):
            serves = row[4] if len(row) > 4 else []
            key    = row[5] if len(row) > 5 else None
            if not serves:
                bad.append("equipment row %d (%s) names no test it serves" % (n, row[0][:40]))
            for tid in serves:
                if tid not in TESTBYID:
                    bad.append("equipment row %d names no test %r" % (n, tid)); continue
                if key is not None and key.lower() not in " | ".join(tools_of(tid)).lower():
                    bad.append("equipment row %d (%s) says it serves %s, but %r is not in that "
                               "test's tool list %r" % (n, row[0][:40], tid, key, tools_of(tid)))
        addrs = [r["addr"] for r in D["registers"]]
        if len(set(addrs)) != len(addrs): bad.append("duplicate register address in registers[]")
        for a, kind, why in _RB:
            if a not in addrs: bad.append("SV-01 reads back register %d, which is not in Table 5" % a)
            if kind not in ("scan", "written", "verify"):
                bad.append("SV-01 read-back %d has unknown kind %r" % (a, kind))
    else:
        left = _TOKRE.findall(doc)
        if left: bad.append("unfilled tokens in the output: %s" % sorted(set(left)))
        for i in ids + eol_ids + ex_ids:
            if ('id="%s"' % i) not in doc: bad.append("no anchor id=%r in the output" % i)
    return bad

TOK["N_CHECKS"] = len(CHECKS)

_pre = selfcheck()
if _pre:
    for b in _pre: print("SELFCHECK FAIL:", b)
    raise SystemExit("gen_test_plan: %d self-check failure(s); nothing written" % len(_pre))

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
  <div class="stat"><b>{len(D.get("resolved", []))}</b><span>questions open in Rev&nbsp;A, settled here</span></div>
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
  <div class="tw"><table class="data"><caption>Table {TN()}. Every gate in this document answers with exactly one of these.</caption>
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
  says it plainly: have the robot on its stand. Every test before section {SECNUM["walk"]} runs with both feet clear
  of the bench.</div>

  <h3 class="sub" id="corrections">1.3 Corrections in Rev&nbsp;C</h3>
  <p>An independent read of Rev&nbsp;B found {len(D.get("corrections", []))} places where a number, a citation or a
  claim of completeness did not survive its own source. Each is below with the measurement that settled it.
  A correction is published, never quietly overwritten &mdash; a document whose errors disappear is a document
  nobody can audit.</p>
  {corrections_html()}

  <h3 class="sub" id="refusals">1.4 What this generator refuses to publish</h3>
  <p><code>tools/gen_test_plan.py</code> runs {len(CHECKS)} checks before it writes a byte and exits non-zero,
  having written nothing, on any failure. Two of them run again on the finished page. They exist because every
  correction in 1.3 was possible only in a generator that checked nothing, and each check below was broken on
  purpose once in a sandbox copy of the repository and watched to fire before it was trusted &mdash;
  {len(CHECKS)} of {len(CHECKS)} did.</p>
  <div class="tw"><table class="data"><caption>Table {TN()}. The refusals, and the defect each one exists to catch.</caption>
  <thead><tr><th>The check</th><th>Why it is there</th></tr></thead>
  <tbody>{"".join("<tr><td>%s</td><td class='basis'>%s</td></tr>" % (M(a), M(b)) for a, b in CHECKS)}</tbody></table></div>
</section>

{sections_html()}

<section id="eol">
  <h2><span class="n">{TAILNUM["eol"]}</span>End-of-line checklist</h2>
  <p class="lede">{M(D["eol_note"])}</p>
  <div class="tw"><table class="data"><caption>Table {TN()}. End-of-line gates, {len(D['eol'])} of them.</caption>
  <thead><tr><th></th><th>Test</th><th>Gate</th><th>Instrument</th></tr></thead>
  <tbody>{eol_table()}</tbody></table></div>

  <h3 class="sub" id="eol-exempt">{TAILNUM["eol"]}.1 The gated tests deliberately NOT on the list</h3>
  <p>{len(all_tests)} tests carry a PASS gate or state why they carry none. {len(D["eol"])} of them are on the
  checklist above. The {len(D.get("eol_exempt", []))} below are not, and the generator will not write this document
  unless each one appears here with its reason &mdash; a test can leave the ship checklist, but it cannot leave
  quietly.</p>
  <div class="tw"><table class="data"><caption>Table {TN()}. Exemptions, each with what would put it back on the list.</caption>
  <thead><tr><th>Test</th><th>Why it is not an end-of-line gate</th><th>What would put it back</th></tr></thead>
  <tbody>{eol_exempt_table()}</tbody></table></div>
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
  <div class="tw"><table class="data"><caption>Table {TN()}. All {len(D["sources"])} sources on the record.
  The <b>cited by</b> column is measured as this page renders, not asserted: it lists the gates and blocks that
  actually name each key, and a source nothing rests on says so.</caption>
  <thead><tr><th>Key</th><th>What</th><th>Cited by</th><th>Where</th></tr></thead>
  <tbody>__SOURCES_TABLE__</tbody></table></div>
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

_CITER[0] = "the document"
HTML = HTML.replace("__SOURCES_TABLE__", sources_table())

_post = selfcheck(HTML)
if _post:
    for b in _post: print("SELFCHECK FAIL:", b)
    raise SystemExit("gen_test_plan: %d self-check failure(s) in the rendered page; nothing written"
                     % len(_post))

out = os.path.join(REPO, "TEST-PLAN.html")
open(out, "w", encoding="utf-8").write(HTML)
# len(HTML) is CHARACTERS. The em dashes and times signs in this page are 2-3 bytes each in
# UTF-8, so the two differ by ~100 and reporting the character count as "bytes" was itself a
# number that did not survive its own measurement. Stat the file that was actually written.
_bytes = os.path.getsize(out)
print("wrote TEST-PLAN.html  tests=%d eol=%d exempt=%d open=%d sources=%d  chars=%d  bytes=%d (stat)"
      % (n_tests, len(D["eol"]), len(D.get("eol_exempt", [])), n_open, len(D["sources"]),
         len(HTML), _bytes))
print("selfcheck: %d checks, 0 failures" % len(CHECKS))
_res = [h for h, ok in LINKS if ok]
_pen = [h for h, ok in LINKS if not ok]
print("cross-document links: %d resolved (%s)%s"
      % (len(_res), ", ".join(sorted(set(_res))),
         ("; %d STILL PENDING: %s — re-run this generator when they land"
          % (len(_pen), ", ".join(sorted(set(_pen))))) if _pen else "; none pending"))
print("derived: 1 count = %.6f deg; tol %.1f deg = %d counts; "
      "limp tilt = %.4f deg; fall report tilt = %.4f deg; walk gate = %.3f m (%.0f%% of %.4f m)"
      % (DEG_PER_COUNT, TOL_DEG, TOL_COUNT, LIMP_TILT_DEG, FALL_TILT_DEG,
         GATE_WALK_M, GATE_FRACTION*100, SIM_WALK_M))
