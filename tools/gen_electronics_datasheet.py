#!/usr/bin/env python3
"""gen_electronics_datasheet.py — build ELECTRONICS-DATASHEET.html from data.

Revision A of that page was 90 KB of hand-maintained HTML with no generator, so
every number in it was a copy of a number that lives somewhere else. This reads
the three places the facts actually live and renders them:

  electronics/components.json          the roster: envelope, mass, qty, role,
                                       where fitted, per-row open items
  electronics/datasheet-narrative.json the bus, the control table, the power
                                       tree, the pin map, the software map
  ce-parts/<slug>/component.json       the folder's own verdict and why
  ce-parts/<slug>/electrical.*.json    manufacturer, package quote, datasheet
                                       URL + revision, supplies, current, I2C
                                       address, interface — read LIVE, never
                                       copied, because TRIAD.md says apps do
                                       not hold product truth

A component named in components.json whose ce-parts folder is missing is
rendered as a row that SAYS SO, not skipped: a part with no folder is the gap
this page exists to show.

Run:  python3 tools/gen_electronics_datasheet.py [--out ELECTRONICS-DATASHEET.html]
Then LOOK at it — tools/serve.sh on :8842, or cecad.vision.screenshot_url().
"""
import argparse
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
E = html.escape


def load(*p):
    with open(os.path.join(REPO, *p)) as fh:
        return json.load(fh)


def shelf(slug):
    """Everything ce-parts/<slug>/ says about itself, or None."""
    base = os.path.join(REPO, "ce-parts", slug)
    if not os.path.isdir(base):
        return None
    out = {"slug": slug, "folder": "ce-parts/%s" % slug}
    cj = os.path.join(base, "component.json")
    if os.path.exists(cj):
        out["component"] = json.load(open(cj)).get("record", {})
    for name in os.listdir(base):
        if name.startswith("electrical.") and name.endswith(".json"):
            d = json.load(open(os.path.join(base, name)))
            out.setdefault("electrical", {})[d.get("kind", name)] = d.get("record", {})
    tj = os.path.join(base, "current", "trust.json")
    if os.path.exists(tj):
        out["trust"] = json.load(open(tj)).get("record", {})
    return out


def elec_field(sh, *keys):
    """First of `keys` present in any electrical.* record."""
    if not sh:
        return None
    for _kind, rec in (sh.get("electrical") or {}).items():
        for k in keys:
            if k in rec and rec[k] not in (None, "", [], {}):
                return rec[k]
    return None


def dim_str(d):
    if not d:
        return "—"
    v = [d.get("x"), d.get("y"), d.get("z")]
    if all(x is None for x in v):
        return '<span class="cd">CANNOT DETERMINE</span>'
    def f(x):
        return "?" if x is None else ("%g" % x)
    s = " × ".join(f(x) for x in v)
    return '<span class="mono">%s</span>' % E(s)


def mass_str(c):
    if c.get("mass_g") is None:
        return '<span class="cd">CD</span>'
    s = "%g g" % c["mass_g"]
    if c.get("mass_total_g"):
        s += " (×%s = %g g)" % (c.get("qty"), c["mass_total_g"])
    return '<span class="mono">%s</span>' % E(s)


def _supply_rows(sh):
    """Every shape a folder states a supply in, in the order they are trusted.

    `supplies` is the chip records' shape (min/typ/max). A HOST folder states
    `power` instead (an input, one nominal), and a PART that SOURCES power
    states `provides`. Reading only `supplies` printed CANNOT DETERMINE for the
    Radxa and for the battery — for the two rows whose voltage is the least
    uncertain thing on the whole page.
    """
    for key in ("supplies", "power", "provides"):
        v = elec_field(sh, key)
        if not v:
            continue
        rows = [v] if isinstance(v, dict) else list(v)
        out = []
        for s in rows:
            if not isinstance(s, dict):
                continue
            lo, ty, hi = s.get("v_min"), s.get("v_typ"), s.get("v_max")
            nom = s.get("v_nom", s.get("v_nominal"))
            if lo is None and hi is None and nom is None:
                continue
            out.append((s.get("name") or "", lo,
                        ty if ty is not None else nom, hi, s.get("cite")))
        if out:
            return out
    return []


def supply_str(sh):
    rows = _supply_rows(sh)
    if not rows:
        return '<span class="cd">CD</span>'
    bits = []
    for name, lo, ty, hi, _cite in rows[:3]:
        n = name.split(" ")[0]
        if lo is None and hi is None:
            bits.append("%s %s" % (n, ty))
        else:
            bits.append("%s %s/%s/%s" % (n, "?" if lo is None else lo,
                                         "?" if ty is None else ty,
                                         "?" if hi is None else hi))
    return '<span class="mono">%s</span>' % E("; ".join(bits))


def current_str(c, sh):
    cur = c.get("current_mA")
    if isinstance(cur, dict):
        bits = ["%s %s" % (k, v) for k, v in cur.items()
                if not k.endswith("_why") and k != "source" and isinstance(v, (int, float))]
        if bits:
            return '<span class="mono">%s</span>' % E(", ".join(bits) + " mA")
    ec = elec_field(sh, "current_mA")
    if isinstance(ec, dict):
        t = ec.get("typical")
        if t is not None:
            extra = " (peak %g)" % ec["peak"] if ec.get("peak") is not None else ""
            return '<span class="mono">%g mA%s</span>' % (t, extra)
    return '<span class="cd">CD</span>'


def verdict_chip(sh, short=False):
    if not sh or "component" not in sh:
        return '<span class="chip rail">%s</span>' % ("NO FOLDER" if not short else "NONE")
    v = (sh["component"].get("verdict") or "").upper()
    cls = {"PASS": "pass", "FAIL": "rail"}.get(v, "cd")
    label = v or "\u2014"
    if short and label == "CANNOT DETERMINE":
        label = "CD"
    return '<span class="chip %s">%s</span>' % (cls, E(label))


def qty_str(c):
    q = c.get("qty")
    if q is None:
        return '<span class="cd">CD</span>'
    return '<span class="mono">%d</span>' % q


# ───────────────────────────────────────────────────────── page pieces
def table(cols, rows, caption=None, cls="data"):
    # Caption goes ABOVE the scroll container, never inside it: a caption inside
    # an overflow-x box takes the TABLE's width and gets clipped with it.
    h = []
    if caption:
        h.append('<p class="cap">%s</p>' % caption)
    h.append('<div class="tw"><table class="%s">' % cls)
    h.append("<thead><tr>%s</tr></thead><tbody>"
             % "".join("<th>%s</th>" % E(c) for c in cols))
    for r in rows:
        h.append("<tr>%s</tr>" % "".join("<td>%s</td>" % c for c in r))
    h.append("</tbody></table></div>")
    return "\n".join(h)


def roster_table(comps, shelves):
    rows = []
    for c in comps:
        sh = shelves.get(c["slug"])
        mfr = elec_field(sh, "manufacturer") or ""
        # Some folders put PROSE in `manufacturer` (np-f550 explains there that no
        # single maker is known). A table cell is not the place for a paragraph:
        # take the first clause, and let §4 carry the whole sentence.
        mfr_cell = mfr.split(".")[0].split(",")[0].strip()
        if len(mfr_cell) > 30:
            mfr_cell = mfr_cell[:29] + "…"
        rows.append([
            '<b>%s</b><br><span class="tiny">%s · %s</span>'
            % (E(c["name"]), E(c["row"]), E(c["slug"])),
            E(mfr_cell) or "—",
            qty_str(c),
            dim_str(c.get("dimensions_mm")),
            mass_str(c),
            supply_str(sh),
            current_str(c, sh),
            verdict_chip(sh, short=True),
        ])
    return table(["component", "maker", "qty", "envelope mm", "mass",
                  "supply V min/typ/max", "current mA", "verdict"],
                 rows,
                 "Table 1. The roster. Every electronic line in the machine. "
                 "<b>CD</b> is CANNOT DETERMINE and is a real answer — it means "
                 "nobody published the number and this document will not invent one. "
                 "Envelope, mass and quantity come from <code>electronics/components.json</code>; "
                 "manufacturer, supply and current are read live out of "
                 "<code>ce-parts/&lt;slug&gt;/electrical.*.json</code>.",
                 cls="data roster")


def detail_block(c, sh):
    h = ['<div class="card comp" id="c-%s">' % E(c["slug"])]
    h.append('<h3>%s <span class="tiny">%s · %s</span></h3>'
             % (E(c["name"]), E(c["row"]), E(c["slug"])))
    h.append("<p>%s</p>" % E(c["role"]))
    kv = []
    kv.append(("fitted", E(c.get("fitted_where", "—"))))
    d = c.get("dimensions_mm") or {}
    kv.append(("envelope", dim_str(d) + (
        '<div class="src">%s</div>' % E(d.get("source")) if d.get("source") else "") + (
        '<div class="src cd">%s</div>' % E(d.get("z_why")) if d.get("z_why") else "") + (
        '<div class="src">%s</div>' % E(d.get("z_note")) if d.get("z_note") else "")))
    if c.get("mount_pattern"):
        kv.append(("mount pattern", '<span class="mono">%s</span>' % E(c["mount_pattern"])))
    m = mass_str(c)
    if c.get("mass_source"):
        m += '<div class="src">%s</div>' % E(c["mass_source"])
    if c.get("mass_why"):
        m += '<div class="src cd">%s</div>' % E(c["mass_why"])
    if c.get("mass_note"):
        m += '<div class="src">%s</div>' % E(c["mass_note"])
    kv.append(("mass", m))
    cur = current_str(c, sh)
    for key in ("current_why",):
        if c.get(key):
            cur += '<div class="src cd">%s</div>' % E(c[key])
    if isinstance(c.get("current_mA"), dict) and c["current_mA"].get("source"):
        cur += '<div class="src">%s</div>' % E(c["current_mA"]["source"])
    ec = elec_field(sh, "current_mA")
    if isinstance(ec, dict) and ec.get("typical_basis"):
        cur += '<div class="src">%s</div>' % E(ec["typical_basis"])
    kv.append(("current", cur))
    kv.append(("supply", supply_str(sh) + "".join(
        '<div class="src">%s</div>' % E(cite)
        for _n, _lo, _ty, _hi, cite in _supply_rows(sh) if cite)))
    pkg = elec_field(sh, "package")
    if pkg:
        kv.append(("package, verbatim", '<div class="src">%s</div>' % E(pkg)))
    addr = elec_field(sh, "i2c_address")
    if addr:
        kv.append(("I²C address", '<div class="src">%s</div>' % E(str(addr))))
    iface = elec_field(sh, "interface")
    if iface:
        kv.append(("interface", E(str(iface))))
    conn = elec_field(sh, "connector")
    if isinstance(conn, dict):
        kv.append(("connector", '<div class="src">%s</div>'
                   % E("; ".join("%s: %s" % (k, v) for k, v in conn.items()
                                 if isinstance(v, str) and len(v) < 200))))
    url = elec_field(sh, "datasheet_url")
    rev = elec_field(sh, "datasheet_rev")
    if url:
        kv.append(("datasheet", '<a href="%s">%s</a>%s' % (
            E(url), E(url[:90]),
            '<div class="src">%s</div>' % E(rev) if rev else "")))
    if sh and sh.get("component"):
        kv.append(("folder verdict", verdict_chip(sh)
                   + '<div class="src">%s</div>' % E(sh["component"].get("why", ""))))
    elif c.get("no_shelf_folder"):
        kv.append(("folder", '<span class="chip rail">NO ce-parts FOLDER</span>'
                   '<div class="src cd">%s</div>' % E(c["no_shelf_folder"])))
    h.append('<dl class="kv">')
    for k, v in kv:
        h.append("<dt>%s</dt><dd>%s</dd>" % (E(k), v))
    h.append("</dl>")
    if c.get("open"):
        h.append('<div class="openlist"><b>Open on this part</b><ul>%s</ul></div>'
                 % "".join("<li>%s</li>" % E(o) for o in c["open"]))
    h.append("</div>")
    return "\n".join(h)


def build(out_path):
    C = load("electronics", "components.json")
    N = load("electronics", "datasheet-narrative.json")
    comps = C["components"]
    shelves = {c["slug"]: shelf(c["slug"]) for c in comps}

    n_total = len(comps)
    n_folder = sum(1 for s in shelves.values() if s and s.get("component"))
    n_pass = sum(1 for s in shelves.values()
                 if s and (s.get("component") or {}).get("verdict") == "PASS")
    n_dim = sum(1 for c in comps
                if any((c.get("dimensions_mm") or {}).get(k) is not None for k in "xyz"))
    n_mass = sum(1 for c in comps if c.get("mass_g") is not None)
    n_open = sum(len(c.get("open") or []) for c in comps)
    mb = C["mass_budget"]

    rev = N["revision"]
    S = []
    A = S.append

    A('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">')
    A('<meta name="viewport" content="width=device-width, initial-scale=1">')
    A("<title>Microduck Electronics Datasheet</title>")
    A('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opt_sz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">')
    A('<link rel="stylesheet" href="tools/doc.css">')
    A("<style>\n"
      ".tiny{font-family:var(--sans);font-size:11px;color:var(--ink-2);letter-spacing:.03em}\n"
      "p.cap{font-style:italic;color:var(--ink-2);font-size:13px;margin:14px 0 2px;max-width:52em}\n"
      ".cd{color:var(--cd-ink);font-family:var(--sans);font-size:11.5px;font-weight:600}\n"
      "td .cd,.src.cd{font-weight:400}\n"
      ".src{font-family:var(--sans);font-size:11.5px;color:var(--ink-2);margin-top:3px;line-height:1.45}\n"
      "dl.kv{display:grid;grid-template-columns:150px 1fr;gap:6px 16px;margin:10px 0 4px;font-size:13.5px}\n"
      "dl.kv dt{font-family:var(--sans);font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2);padding-top:2px}\n"
      "dl.kv dd{margin:0}\n"
      ".card.comp{border:1px solid var(--hair);background:var(--figbg);padding:16px 18px;margin:16px 0}\n"
      ".card.comp h3{margin:0 0 4px;font-size:17px}\n"
      ".openlist{margin-top:10px;border-left:2px solid var(--cd-ink);padding:6px 0 6px 12px}\n"
      ".openlist b{font-family:var(--sans);font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--cd-ink)}\n"
      ".openlist ul{margin:4px 0 0;padding-left:18px;font-size:13px}\n"
      ".openlist li{margin:3px 0}\n"
      "table.data td{font-size:12.5px}\n"
      "table.roster th,table.roster td{padding:5px 7px;font-size:11.5px;line-height:1.4}\n"
      "table.roster .mono{font-size:11px}\n"
      "figure svg,figure img{width:100%;height:auto}\n"
      ".gen{font-family:var(--mono);font-size:11px;color:var(--ink-2);border:1px solid var(--hair);"
      "background:var(--figbg);padding:9px 13px;margin:14px 0}\n"
      "</style>\n</head>\n<body>\n<div class=\"wrap\">")

    # masthead
    A('<header class="top">')
    A('<div class="eyebrow">Reverse-engineering datasheet · ce-designs/microduck</div>')
    A("<h1>Microduck Electronics</h1>")
    A('<p class="sub">Every electronic component in the machine: exact part where one is '
      'published, physical envelope, supply, current, mass — and, where nobody published a '
      'number, the words CANNOT DETERMINE and what would settle it.</p>')
    A('<div class="rev"><span>%s</span><span>Revision %s · %s</span><span>Units mm · g · mA · V</span>'
      '<span>Generated by tools/gen_electronics_datasheet.py</span></div>'
      % (E(rev["document"]), E(rev["revision"]), E(rev["date"])))
    A("</header>")

    A('<div class="gen">This page is GENERATED. Data: <code>electronics/components.json</code> '
      '(roster) + <code>electronics/datasheet-narrative.json</code> (the bus, registers, power '
      'tree, pin map) + <code>ce-parts/&lt;slug&gt;/</code> read live for every vendor fact. '
      'Edit the data, re-run the generator. %s</div>' % E(rev["supersedes"]))

    # stat bar
    A('<div class="statbar">')
    for val, lab in ((n_total, "components in the roster"),
                     ("%d / %d" % (n_folder, n_total), "with a ce-parts folder"),
                     (n_dim, "with a dimensioned envelope"),
                     (n_mass, "with a mass"),
                     (n_open, "open items across the roster"),
                     ("%g g" % mb["unaccounted_g"], "of 780 g unaccounted")):
        A('<div class="stat"><b>%s</b><span>%s</span></div>' % (E(str(val)), E(lab)))
    A("</div>")

    A('<nav class="toc">' + "".join(
        '<a href="#%s">%s</a>' % (i, t) for i, t in [
            ("overview", "§1 Architecture"), ("diagram", "§2 Diagrams"),
            ("roster", "§3 The roster"), ("detail", "§4 Every component"),
            ("bus", "§5 The servo bus"), ("registers", "§6 Control table"),
            ("power", "§7 Power tree"), ("mass", "§8 Mass budget"),
            ("boards", "§9 Custom boards"), ("pins", "§10 Pin map"),
            ("software", "§11 Software"), ("open", "§12 What is not published")]) + "</nav>")

    # §1
    A('<section id="overview"><h2><span class="n">§1</span>Architecture at a glance</h2>')
    A('<div class="grid2">')
    for c in N["architecture_cards"]:
        A('<div class="card"><h3>%s</h3><p>%s</p></div>' % (E(c["title"]), E(c["body"])))
    A("</div></section>")

    # §2 diagrams
    A('<section id="diagram"><h2><span class="n">§2</span>Block diagram, schematics, layout</h2>')
    A('<p class="lede">Three files, each turning the previous into more detail '
      '(<code>docs/MANUFACTURING-REQUIREMENTS.md</code> §B). They are real vector files in this '
      'repository, not pictures of a diagram.</p>')
    for path, cap in [
            ("electronics/1-block-diagram.svg",
             "<b>Block diagram.</b> How everything flows: the functional blocks and the buses between them. No pins."),
            ("electronics/2-schematic-hat.svg",
             "<b>Schematic — Robot HAT.</b> Every component and every pin, with each pin's net."),
            ("electronics/2-schematic-radxa.svg",
             "<b>Schematic — Radxa header.</b>"),
            ("electronics/2-schematic-imu.svg",
             "<b>Schematic — imu_to_dxl.</b> Reconstructed from the protocol, because no schematic is published."),
            ("electronics/2-schematic-sensors.svg",
             "<b>Schematic — sensors.</b>"),
            ("electronics/3-layout.svg",
             "<b>Layout.</b> Where each device physically is and what cable joins it to what, from spec/mesh-placements.json and wiring/CABLES.md.")]:
        if os.path.exists(os.path.join(REPO, path)):
            note = (N.get("figure_notes") or {}).get(path)
            A('<figure><img src="%s" alt="%s"><figcaption>%s <a href="%s">%s</a>%s</figcaption></figure>'
              % (E(path), E(path), cap, E(path), E(path),
                 ('<div class="src cd">%s</div>' % E(note)) if note else ""))
    A("</section>")

    # §3 roster
    A('<section id="roster"><h2><span class="n">§3</span>The roster</h2>')
    A(roster_table(comps, shelves))
    A('<p>%d of %d rows have a <code>ce-parts</code> folder; %d of those grade themselves PASS. '
      'A folder that grades itself CANNOT DETERMINE is not a failure of the folder — it is the '
      'folder refusing to claim what it did not measure, and this page inherits that refusal '
      'rather than papering over it (TRIAD.md, "Coverage is part of the verdict").</p>'
      % (n_folder, n_total, n_pass))
    A("</section>")

    # §4 detail
    A('<section id="detail"><h2><span class="n">§4</span>Every component</h2>')
    A('<p class="lede">One block per line of the roster. Every vendor figure is read live out of '
      'the part folder that owns it, with the folder\'s own citation shown beneath it.</p>')
    for c in comps:
        A(detail_block(c, shelves.get(c["slug"])))
    A("</section>")

    # §5 bus
    b = N["servo_bus"]
    A('<section id="bus"><h2><span class="n">§5</span>The servo bus</h2>')
    A('<p class="lede">%s</p>' % E(b["lede"]))
    A(table(b["columns"], [[E(x) for x in r] for r in b["rows"]],
            "Table 2. Bus IDs and what each one moves."))
    for n in b["notes"]:
        A("<p>%s</p>" % E(n))
    A("</section>")

    # §6 registers
    r = N["registers"]
    A('<section id="registers"><h2><span class="n">§6</span>Control-table registers &amp; the tick</h2>')
    A('<div class="grid2">')
    for key in ("boot", "tick"):
        blk = r[key]
        A('<div class="card"><h3>%s</h3><pre class="code">%s</pre><p>%s</p></div>'
          % (E(blk["title"]), E(blk["code"]), E(blk["note"])))
    A("</div></section>")

    # §7 power
    p = N["power_tree"]
    A('<section id="power"><h2><span class="n">§7</span>Power tree</h2>')
    A(table(p["columns"], [[E(x) for x in row] for row in p["rows"]],
            "Table 3. Rails, and what each one feeds."))
    A('<div class="note"><b>%s</b><br>%s</div>'
      % (E(p["resolved_note"]["title"]), E(p["resolved_note"]["body"])))
    A("<p>%s</p>" % E(p["drop_note"]))
    A("</section>")

    # §8 mass
    A('<section id="mass"><h2><span class="n">§8</span>Mass budget</h2>')
    rows = [[E(a["what"]), '<span class="mono">%g</span>' % a["g"], E(a["basis"])]
            for a in mb["accounted"]]
    rows.append(["<b>accounted</b>", '<b class="mono">%g</b>' % mb["accounted_total_g"], ""])
    rows.append(['<b>unaccounted</b>', '<b class="mono">%g</b>' % mb["unaccounted_g"],
                 E(mb["unaccounted_note"])])
    rows.append(["<b>robot total (vendor claim)</b>",
                 '<b class="mono">%g</b>' % mb["robot_total_g"], E(mb["robot_total_source"])])
    A(table(["line", "g", "basis"], rows,
            "Table 4. What the roster can weigh and what it cannot."))
    A("<p>%s</p>" % E("What would close it: " + mb["what_would_close_it"]))
    A("</section>")

    # §9 boards
    A('<section id="boards"><h2><span class="n">§9</span>The three custom boards</h2>')
    A('<div class="grid2">')
    for bd in N["custom_boards"]:
        A('<div class="card"><h3>%s</h3><p class="tiny">%s</p><p>%s</p></div>'
          % (E(bd["name"]), E(bd["size"]), E(bd["body"])))
    A("</div></section>")

    # §10 pins
    pm = N["pin_map"]
    A('<section id="pins"><h2><span class="n">§10</span>Pin &amp; connector map</h2>')
    A(table(pm["columns"], [[E(x) for x in row] for row in pm["rows"]],
            "Table 5. Every interface the host presents and what is on the other end."))
    A("<p>%s</p>" % E(pm["note"]))
    A('<div class="note"><b>The mechanical interface</b><br>%s</div>'
      % E(pm["mount_frame_note"]))
    A("</section>")

    # §11 software
    sw = N["software"]
    A('<section id="software"><h2><span class="n">§11</span>How the software reaches each device</h2>')
    A(table(sw["columns"], [[E(x) for x in row] for row in sw["rows"]],
            "Table 6. Daemon to device."))
    A("<p>%s</p>" % E(sw["note"]))
    A("</section>")

    # §12 open
    A('<section id="open"><h2><span class="n">§12</span>What is not published</h2>')
    A('<p class="lede">Named honestly so no reader mistakes an inference for a fact. Each row is '
      'a measurement or a document away from resolution, and says which.</p>')
    rows = [[E(o["id"]), E(o["what"]),
             " ".join('<code>%s</code>' % E(w) for w in o["which"]),
             E(o["settles_it"])] for o in C["open_items"]]
    A(table(["#", "what is not known", "parts", "what settles it"], rows,
            "Table 7. Open items, each with the thing that would close it."))
    A('<p>Per-part open items are listed under each component in §4 — %d of them across the '
      'roster. They are not repeated here; this table carries only what spans more than one part.</p>'
      % n_open)
    A("</section>")

    A('<footer><span>%s rev %s · %s</span>'
      '<span>Generated: <code>python3 tools/gen_electronics_datasheet.py</code></span>'
      '<span>Data: <code>electronics/components.json</code>, '
      '<code>electronics/datasheet-narrative.json</code>, <code>ce-parts/</code></span>'
      '<span>Every claim measured, cited, or marked CANNOT DETERMINE</span></footer>'
      % (E(rev["document"]), E(rev["revision"]), E(rev["date"])))
    A("</div>\n</body>\n</html>")

    out = os.path.join(REPO, out_path)
    with open(out, "w") as fh:
        fh.write("\n".join(S) + "\n")
    print("wrote %s  (%d components, %d with a folder, %d dimensioned, %d with a mass, "
          "%d per-part open items, %d cross-part open items)"
          % (out_path, n_total, n_folder, n_dim, n_mass, n_open, len(C["open_items"])))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="ELECTRONICS-DATASHEET.html")
    build(ap.parse_args().out)
