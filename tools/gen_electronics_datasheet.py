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


def dim_state(d):
    """'full' | 'partial' | 'none' — how much of an envelope a row actually has.

    THE DEFECT THIS FIXES: the coverage headline used to count a row as
    dimensioned if ANY of x/y/z was present (`any(...)`), so a package with a
    length and a width but no thickness was counted as measured and printed as
    "65 × 30 × ?". A partial measurement counted as a measurement is exactly
    what the house rules forbid, and it was the page's own coverage number.
    Measured over electronics/components.json when this was written: 16 rows
    had SOME dimension, only 9 had all three.
    """
    if not d:
        return "none"
    v = [d.get(k) for k in "xyz"]
    if all(x is not None for x in v):
        return "full"
    return "partial" if any(x is not None for x in v) else "none"


def dim_str(d):
    """The envelope, at the SOURCE's own precision (components.json precision_rule).

    Numbers are printed with %g, which strips trailing zeros — that is the rule
    working, not a bug: where a datasheet prints '5 x 5 mm' this page must not
    invent '5.000 x 5.000'. A missing axis prints '?' and the row is counted as
    PARTIAL, never as dimensioned.
    """
    st = dim_state(d)
    if st == "none":
        return '<span class="cd">CANNOT DETERMINE</span>' if d is not None else "—"
    v = [d.get("x"), d.get("y"), d.get("z")]
    dp = d.get("dp") or [None, None, None]
    def f(x, n):
        if x is None:
            return "?"
        # `dp` is the SOURCE's own decimal count, per axis. Without it %g would
        # print Radxa's '65. 0' as "65" while §1 printed "65.000" — the same
        # number at three precisions in one document. check() proves every dp
        # round-trips to the stored float, so no digit is invented or lost.
        return ("%.*f" % (n, x)) if isinstance(n, int) else ("%g" % x)
    s = " × ".join(f(x, n) for x, n in zip(v, dp))
    body = '<span class="mono">%s</span>' % E(s)
    if st == "partial":
        body += ' <span class="cd" title="one or more axes unpublished">partial</span>'
    return body


def mass_str(c, mark=True):
    """The mass, with a REPRESENTATIVE one marked everywhere it is printed.

    THE DEFECT THIS FIXES: Table 1 printed the battery's 99 g bare, while the
    same file says of that number "That is a shipping/product weight for THAT
    pack; the FITTED pack's mass is CANNOT DETERMINE." A caveat that lives only
    in §8 does not travel with the number.
    """
    if c.get("mass_g") is None:
        return '<span class="cd">CD</span>'
    s = "%g g" % c["mass_g"]
    if c.get("mass_total_g"):
        s += " (×%s = %g g)" % (c.get("qty"), c["mass_total_g"])
    out = '<span class="mono">%s</span>' % E(s)
    if mark and c.get("mass_is_representative"):
        out += ' <span class="cd" title="a representative part, not the fitted one">‡ repr.</span>'
    return out


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


PIN_META = {"$about", "verdict", "verdict_why", "cite", "source", "why",
            "quotes", "descriptions_quotes", "polarity_quote"}


def pin_maps(pin):
    """The (package_name, {pin: signal}) maps inside a folder's `pinout` record.

    Every folder writes its pin map under the PACKAGE's own name — 'DFN-10-3x3',
    'SOT-23-6', 'VQFN-32 RHB', 'two-wire-lead' — with the prose keys ($about,
    cite, verdict, quotes) alongside. So the maps are the dict-valued keys that
    are not prose.
    """
    if not isinstance(pin, dict):
        return []
    out = []
    for k, v in pin.items():
        if k in PIN_META or not isinstance(v, dict):
            continue
        if all(isinstance(x, str) for x in v.values()):
            out.append((k, v))
    return out


def _pin_sort(k):
    try:
        return (0, int(k), "")
    except (TypeError, ValueError):
        return (1, 0, str(k))


def pinout_block(sh):
    """§4's pinout row. Renders the map when a folder has one and the folder's
    own refusal when it has not — the brief asked for a pinout per component and
    the page never emitted one, while 7 of the 24 electrical.*.json records
    already carried a `pinout` array nobody read."""
    pin = elec_field(sh, "pinout")
    if not pin:
        return None
    h = []
    maps = pin_maps(pin) if isinstance(pin, dict) else []
    for pkg, m in maps:
        cells = "".join(
            '<span class="pin"><b>%s</b> %s</span>' % (E(str(k)), E(str(v)))
            for k, v in sorted(m.items(), key=lambda kv: _pin_sort(kv[0])))
        h.append('<div class="pinmap"><span class="pkg">%s</span>%s</div>'
                 % (E(str(pkg)), cells))
    if isinstance(pin, dict):
        v = (pin.get("verdict") or "").upper()
        if v.startswith("CANNOT") and not maps:
            h.append('<div class="src cd">PINOUT CANNOT DETERMINE — %s</div>'
                     % E(str(pin.get("why") or pin.get("$about") or "")))
        elif v:
            h.append('<div class="src">verdict: %s</div>' % E(str(pin.get("verdict"))))
        for key in ("$about", "verdict_why", "why"):
            if pin.get(key) and not (key == "why" and v.startswith("CANNOT")):
                h.append('<div class="src">%s</div>' % E(str(pin[key])))
        if pin.get("cite"):
            h.append('<div class="src">%s</div>' % E(str(pin["cite"])))
    elif isinstance(pin, list):
        h.append('<div class="src">%s</div>' % E(json.dumps(pin)[:600]))
    return "".join(h) or None


def _quantity_row(rec, unit):
    """A folder's {value|rated, quote, cite} number, printed with its quote."""
    if isinstance(rec, (int, float)):
        return '<span class="mono">%g %s</span>' % (rec, unit)
    if not isinstance(rec, dict):
        return None
    val = rec.get("value", rec.get("rated"))
    bits = []
    if val is not None:
        tol = rec.get("tolerance_pct")
        bits.append('<span class="mono">%g %s%s</span>'
                    % (val, unit, (" ±%g %%" % tol) if tol is not None else ""))
    if rec.get("max") is not None:
        bits.append('<span class="mono">max %g %s</span>' % (rec["max"], unit))
    for k in ("quote", "rated_quote", "max_quote", "cite", "source"):
        if rec.get(k):
            bits.append('<div class="src">%s</div>' % E(str(rec[k])))
    return " ".join(bits) or None


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
        # Some folders put PROSE in `manufacturer` (np-f550 and microduck-speaker
        # both explain there that no single maker is known). A table cell is not
        # the place for a paragraph: take the first clause and mark the cut, and
        # §4's `maker` row carries the WHOLE sentence — which it did not until
        # 2026-09-03, so the only place a reader met the speaker's refusal was
        # the mutilated fragment "CANNOT DETERMINE for the fitt…" in this table.
        mfr_cell = mfr.split(".")[0].split(",")[0].strip()
        cut = len(mfr_cell) < len(mfr.strip())
        if len(mfr_cell) > 30:
            # cut on a WORD boundary — "onsemi (Semiconductor Compone…" and
            # "CANNOT DETERMINE for the fitt…" were words broken in half.
            head = mfr_cell[:30]
            sp = head.rfind(" ")
            mfr_cell, cut = (head[:sp] if sp > 8 else head).rstrip(), True
        if cut:
            mfr_cell += " …"
        rows.append([
            '<b>%s</b><br><span class="tiny">%s · %s</span>'
            % (E(c["name"]), E(c["row"]), E(c["slug"])),
            (('<span class="cd">%s</span>' % E(mfr_cell))
             if mfr_cell.upper().startswith(("CANNOT DETERMINE", "NOT ONE"))
             else E(mfr_cell)) or "—",
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
                 "<code>ce-parts/&lt;slug&gt;/electrical.*.json</code>. "
                 "<b>Reading the envelope column:</b> dimensions are printed to the number of "
                 "decimals the SOURCE states and no further (that file\'s <code>precision_rule</code>), "
                 "so <span class=\'mono\'>5 × 5</span> is a datasheet that printed \'5 x 5 mm\' and "
                 "<span class=\'mono\'>38.6085</span> is a mesh measured to 4 dp — trailing zeros are "
                 "never invented to make a column look uniform. <span class=\'mono\'>?</span> is an "
                 "axis nobody published, and such a row is marked <b>partial</b> and is NOT counted as "
                 "dimensioned anywhere on this page. The tolerance basis is per-row and is printed with "
                 "the source in §4; where a row carries one it is stated there, and where it does not, "
                 "no tolerance has been published for it. A maker cell ending in \'…\' is a first "
                 "clause; §4 carries the whole sentence. "
                 "<b>‡</b> marks a mass that belongs to a REPRESENTATIVE part, not to the one fitted.",
                 cls="data roster")


def detail_block(c, sh):
    h = ['<div class="card comp" id="c-%s">' % E(c["slug"])]
    h.append('<h3>%s <span class="tiny">%s · %s</span></h3>'
             % (E(c["name"]), E(c["row"]), E(c["slug"])))
    h.append("<p>%s</p>" % E(c["role"]))
    kv = []
    # THE MAKER, WHOLE. Table 1 truncates this to a cell; §4 is where the
    # sentence lives. Before 2026-09-03 §4 emitted no manufacturer row at all,
    # so a folder whose `manufacturer` field is a paragraph of refusal
    # (microduck-speaker, np-f550) appeared in this document only as a cut-off
    # fragment in a table cell.
    mfr = elec_field(sh, "manufacturer")
    if mfr:
        kv.append(("maker", E(str(mfr))))
    kv.append(("fitted", E(c.get("fitted_where", "—"))))
    d = c.get("dimensions_mm") or {}
    kv.append(("envelope", dim_str(d) + (
        '<div class="src">%s</div>' % E(d.get("source")) if d.get("source") else "") + (
        '<div class="src">%s</div>' % E(d.get("dp_why")) if d.get("dp_why") else "") + (
        '<div class="src cd">%s</div>' % E(d.get("z_why")) if d.get("z_why") else "") + (
        '<div class="src">%s</div>' % E(d.get("z_note")) if d.get("z_note") else "")))
    if c.get("mount_pattern"):
        kv.append(("mount pattern", '<span class="mono">%s</span>' % E(c["mount_pattern"])))
    m = mass_str(c)
    if c.get("mass_representative_why"):
        m += '<div class="src cd">‡ %s</div>' % E(c["mass_representative_why"])
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
    pin = pinout_block(sh)
    if pin:
        kv.append(("pinout", pin))
    for key, unit, label in (("impedance_ohm", "Ω", "impedance"),
                             ("power_W", "W", "power")):
        row = _quantity_row(elec_field(sh, key), unit)
        if row:
            kv.append((label, row))
    ce = c.get("electrical")
    if isinstance(ce, dict):
        bits = []
        for k, v in ce.items():
            if k in ("source", "cite"):
                continue
            bits.append('<span class="mono">%s = %s</span>' % (E(str(k)), E(str(v))))
        for k in ("source", "cite"):
            if ce.get(k):
                bits.append('<div class="src">%s</div>' % E(str(ce[k])))
        if bits:
            kv.append(("electrical, this roster", " · ".join(bits)))
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
    # COVERAGE, COUNTED HONESTLY (corrected 2026-09-03). `any(...)` counted a
    # row with a length and a width but no thickness as dimensioned; seven rows
    # were being counted that way. A partial measurement is not a measurement.
    n_dim = sum(1 for c in comps if dim_state(c.get("dimensions_mm")) == "full")
    n_part = sum(1 for c in comps if dim_state(c.get("dimensions_mm")) == "partial")
    n_mass = sum(1 for c in comps
                 if c.get("mass_g") is not None and not c.get("mass_is_representative"))
    n_mass_repr = sum(1 for c in comps if c.get("mass_is_representative"))
    n_pin = sum(1 for sl in shelves
                if pin_maps(elec_field(shelves.get(sl), "pinout")))
    n_pin_cd = sum(1 for sl in shelves
                   if elec_field(shelves.get(sl), "pinout")
                   and not pin_maps(elec_field(shelves.get(sl), "pinout")))
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
      "p.statnote{font-family:var(--sans);font-size:12px;color:var(--ink-2);line-height:1.55;"
      "max-width:60em;margin:8px 0 0;border-left:2px solid var(--hair);padding-left:12px}\n"
      ".pinmap{display:flex;flex-wrap:wrap;gap:3px 5px;align-items:baseline;margin:2px 0 5px}\n"
      ".pinmap .pkg{font-family:var(--sans);font-size:10.5px;letter-spacing:.06em;"
      "text-transform:uppercase;color:var(--ink-2);margin-right:4px}\n"
      ".pinmap .pin{font-family:var(--mono);font-size:11px;border:1px solid var(--hair);"
      "background:var(--figbg);padding:1px 5px;white-space:nowrap}\n"
      ".pinmap .pin b{color:var(--ink-2);font-weight:500;margin-right:3px}\n"
      "td s,.note s{color:var(--ink-2);text-decoration-thickness:1px}\n"
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
                     (n_dim, "FULLY dimensioned (x, y and z)"),
                     (n_part, "partially — an axis nobody published"),
                     (n_pin, "with a pin map"),
                     (n_mass, "with a mass of the fitted part"),
                     (n_open, "open items across the roster"),
                     ("%g g" % mb["unaccounted_g"], "unaccounted, of 780 g")):
        A('<div class="stat"><b>%s</b><span>%s</span></div>' % (E(str(val)), E(lab)))
    A("</div>")
    A('<p class="statnote">Read those eight numbers with their caveats, because three of them '
      'used to be flattering. <b>%d fully dimensioned</b> counts a row only when x, y AND z are '
      'published; the %d <b>partial</b> rows have a package length and width and no thickness, and '
      'this page prints them as <span class="mono">65 × 30 × ?</span> and counts them nowhere. '
      '<b>%d with a pin map</b> means a folder carries pin-number → signal for its package; a '
      'further %d state a pinout record whose verdict is CANNOT DETERMINE and say which table they '
      'did not transcribe. <b>%d with a mass</b> counts only masses of the part actually fitted — '
      'the battery\'s 99 g is a vendor shipping weight for a DIFFERENT pack and is marked ‡ '
      'wherever it appears, so the %g g unaccounted is a floor, not a figure (§8).</p>'
      % (n_dim, n_part, n_pin, n_pin_cd, n_mass, mb["unaccounted_g"]))

    A('<nav class="toc">' + "".join(
        '<a href="#%s">%s</a>' % (i, t) for i, t in [
            ("overview", "§1 Architecture"), ("diagram", "§2 Diagrams"),
            ("roster", "§3 The roster"), ("detail", "§4 Every component"),
            ("bus", "§5 The servo bus"), ("registers", "§6 Control table"),
            ("power", "§7 Power tree"), ("mass", "§8 Mass budget"),
            ("boards", "§9 Custom boards"), ("pins", "§10 Pin map"),
            ("software", "§11 Software"), ("cables", "§12 Cables"),
            ("open", "§13 What is not published")]) + "</nav>")

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
    rows = [[E(a["what"]) + (' <span class="cd">‡</span>' if a.get("representative") else ""),
             '<span class="mono">%g</span>' % a["g"], E(a["basis"])]
            for a in mb["accounted"]]
    rows.append(["<b>accounted</b>", '<b class="mono">%g</b>' % mb["accounted_total_g"], ""])
    rows.append(['<b>unaccounted</b>', '<b class="mono">%g</b>' % mb["unaccounted_g"],
                 E(mb["unaccounted_note"])])
    rows.append(["<b>robot total (vendor claim)</b>",
                 '<b class="mono">%g</b>' % mb["robot_total_g"], E(mb["robot_total_source"])])
    A(table(["line", "g", "basis"], rows,
            "Table 4. What the roster can weigh and what it cannot. "
            "<b>‡</b> marks a line that is NOT a mass of this robot's own part."))
    if mb.get("representative_note"):
        A('<div class="note"><b>‡ One of the two accounted lines is borrowed.</b><br>%s</div>'
          % E(mb["representative_note"]))
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

    # §12 cables and connectors — read live out of the wiring lane's own file
    cj = os.path.join(REPO, "wiring", "cables.json")
    A('<section id="cables"><h2><span class="n">§12</span>Cables &amp; connectors</h2>')
    if os.path.exists(cj):
        W = json.load(open(cj))["record"]
        cab = W["cables"]
        n_len = sum(1 for x in cab if isinstance(x.get("cable_mm"), (int, float)))
        n_cd = len(cab) - n_len
        n_conn_cd = sum(1 for x in cab
                        if "CANNOT DETERMINE" in (x.get("connector") or ""))
        A('<p class="lede">The harness, read live out of <code>wiring/cables.json</code> — the '
          'wiring lane measures every run off the placements and this page does not restate it. '
          'A length is a ROUTE FLOOR through the crossed hinge origins plus the stated slack, not '
          'a straight line.</p>')
        # CORRECTIONS THIS DOCUMENT OWES ITS READER. wiring/cables.json belongs
        # to the wiring lane; a field there that contradicts this document's own
        # evidence is PRINTED as a contradiction rather than silently rewritten
        # in someone else's file. Each correction retires itself: it is only
        # rendered while `stale` still matches the live value, so the day the
        # wiring lane fixes the row, this note disappears on its own.
        corr = {k: v for k, v in (N.get("cable_corrections") or {}).items()
                if not k.startswith("$")}
        notes, seen_corr = [], []
        rows = []
        for x in cab:
            ln = x.get("cable_mm")
            pins = x.get("pins", "") or "—"
            pin_cell = '<span class="tiny">%s</span>' % E(pins)
            cx = corr.get(x["id"])
            if cx:
                live = x.get(cx["field"])
                if live == cx["stale"]:
                    n = len(seen_corr) + 1
                    pin_cell = ('<span class="tiny"><s>%s</s> → <b>%s</b> '
                                '<span class="cd">†%d</span></span>'
                                % (E(cx["stale"]), E(cx["correction"]), n))
                    seen_corr.append((n, x["id"], cx, "applied"))
                elif cx["correction"] not in str(live):
                    n = len(seen_corr) + 1
                    pin_cell += ' <span class="cd">†%d</span>' % n
                    seen_corr.append((n, x["id"], cx, "stale-correction"))
            rows.append([
                '<span class="mono">%s</span>' % E(x["id"]),
                "%s \u2192 %s" % (E(x.get("from", "?")), E(x.get("to", "?"))),
                ('<span class="mono">%g</span>' % ln) if isinstance(ln, (int, float))
                else '<span class="cd">CD</span>',
                ('<span class="mono">%g</span>' % x["floor_mm"])
                if isinstance(x.get("floor_mm"), (int, float)) else "—",
                pin_cell,
                '<span class="tiny">%s</span>' % E(x.get("connector", "") or "—"),
                '<span class="mono">%s</span>' % E(str(x.get("qty", "—"))),
            ])
        A(table(["cable", "from \u2192 to", "cut mm", "floor mm", "pins", "connector", "qty"],
                rows,
                "Table 7. Every cable in the machine, generated from the wiring lane's measured "
                "file. <b>CD</b> is CANNOT DETERMINE.", cls="data roster"))
        A('<p>%d cables, %d with a length totalling %s mm, %d with no length at all, and %d whose '
          'CONNECTOR is CANNOT DETERMINE. That last number is the one a shop feels: a cable you can '
          'cut to length but cannot terminate is not a cable. Every one of them is a HAT-side or '
          'module-side connector on a board nobody has published — the same wall as §13 row E1.</p>'
          % (len(cab), n_len, W.get("total_length_mm", "?"), n_cd, n_conn_cd))
        for n, cid, cx, state in seen_corr:
            if state == "applied":
                A('<div class="note"><b>† %d — cable <code>%s</code>, field '
                  '<code>%s</code>: this document corrects the wiring lane\'s file.</b><br>'
                  '<code>wiring/cables.json</code> still says <s>%s</s>; the current reading is '
                  '<b>%s</b>. %s<br><span class="src">%s</span></div>'
                  % (n, E(cid), E(cx["field"]), E(cx["stale"]), E(cx["correction"]),
                     E(cx["why"]), E(cx["owner"])))
            else:
                A('<div class="note"><b>† %d — cable <code>%s</code>: a correction this page '
                  'carried no longer applies.</b><br>It expected <code>%s</code> to read '
                  '"%s" and it does not, so the wiring lane has changed the row. Re-check the '
                  'correction in <code>electronics/datasheet-narrative.json</code> '
                  '<code>cable_corrections</code> against the new value before trusting either.</div>'
                  % (n, E(cid), E(cx["field"]), E(cx["stale"])))
        A('<p>Full schedule with the crossed joints and the per-hop voltage drop: '
          '<a href="wiring/CABLES.html">wiring/CABLES.html</a>.</p>')
    else:
        A('<p class="lede"><span class="cd">CANNOT DETERMINE</span> — '
          '<code>wiring/cables.json</code> is not in the repository, so no harness table could be '
          'generated. It is produced by <code>wiring/measure.py</code>.</p>')
    A("</section>")

    # §13 open
    A('<section id="open"><h2><span class="n">§13</span>What is not published</h2>')
    A('<p class="lede">Named honestly so no reader mistakes an inference for a fact. Each row is '
      'a measurement or a document away from resolution, and says which.</p>')
    rows = [[E(o["id"]), E(o["what"]),
             " ".join('<code>%s</code>' % E(w) for w in o["which"]),
             E(o["settles_it"])] for o in C["open_items"]]
    A(table(["#", "what is not known", "parts", "what settles it"], rows,
            "Table 8. Open items, each with the thing that would close it."))
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
    print("wrote %s  (%d components, %d with a folder, %d FULLY dimensioned + %d partial, "
          "%d with a pin map + %d pinout-CD, %d with a fitted-part mass + %d representative, "
          "%d per-part open items, %d cross-part open items)"
          % (out_path, n_total, n_folder, n_dim, n_part, n_pin, n_pin_cd,
             n_mass, n_mass_repr, n_open, len(C["open_items"])))
    return out


def check():
    """Every reference this page makes, followed. Exit 0 / 1 FAIL / 2 CANNOT DETERMINE.

    Three questions a page cannot answer about itself by rendering:

      1. Does every `ce-parts/<slug>` a roster row names actually exist? A row
         whose folder is gone renders as "NO FOLDER", which is honest — but it
         must be honest ON PURPOSE, not because someone renamed a directory.
      2. Does every repo path quoted inside a source/cite string resolve? These
         are the citations the whole document rests on. A citation that does not
         resolve is not a citation.
      3. Is any number stated twice? The roster's envelope must not also appear
         in a ce-parts `bbox_mm`, or the two will drift. Reported, not failed —
         a duplicate is sometimes the folder's own measurement and sometimes a
         copy, and only a reader can tell which.

    BREAK IT ON PURPOSE: rename ce-parts/bmi088 and re-run — question 1 goes
    red and names the row. Put a nonexistent path in a `source` string and
    question 2 goes red and quotes it.
    """
    import re as _re
    C = load("electronics", "components.json")
    fails, cds, notes = [], [], []

    for c in C["components"]:
        if not os.path.isdir(os.path.join(REPO, "ce-parts", c["slug"])):
            if c.get("no_shelf_folder"):
                cds.append("%s: no ce-parts folder, and the row says so — %s"
                           % (c["slug"], c["no_shelf_folder"][:90]))
            else:
                fails.append("%s: names a ce-parts folder that does not exist, and "
                             "the row does not admit it (no `no_shelf_folder`)" % c["slug"])

    # every repo path quoted anywhere in the data file
    pat = _re.compile(r"\b((?:ce-parts|electronics|tools|wiring|spec|research|out|docs|reference)"
                      r"/[A-Za-z0-9_./<>*-]+)")
    seen = set()
    # A URL contains path-looking text that is NOT a repo path
    # (https://dl.radxa.com/zero3/docs/hw/3w/... matched `docs/hw/3w/...` and
    # reported a FAIL for a file that was never claimed to be here). Strip
    # every URL before scanning; the URLs are checked by being fetched, not
    # by being stat'd.
    blob = _re.sub(r"https?://\S+", " ", json.dumps(C, ensure_ascii=False))
    for m in pat.finditer(blob):
        p = m.group(1).rstrip(".,);'\"")
        if p in seen or "<" in p or "*" in p:
            continue
        seen.add(p)
        if not os.path.exists(os.path.join(REPO, p)):
            fails.append("cited path does not resolve: %s" % p)

    # `dp` must not lose or invent a digit: formatting the stored float at the
    # source's stated precision has to give the stored float back.
    for c in C["components"]:
        d = c.get("dimensions_mm") or {}
        dp = d.get("dp")
        if not dp:
            if any(d.get(k) is not None for k in "xyz"):
                cds.append("%s: dimensions but no `dp` — printed with %%g, so the source's "
                           "own precision is not carried" % c["slug"])
            continue
        if not isinstance(dp, list) or len(dp) != 3:
            fails.append("%s: dp must be a 3-list [x,y,z], got %r" % (c["slug"], dp))
            continue
        for ax, n in zip("xyz", dp):
            v, has = d.get(ax), d.get(ax) is not None
            if has and n is None:
                cds.append("%s: %s = %g has no dp; printed with %%g"
                           % (c["slug"], ax, v))
            elif has and not isinstance(n, int):
                fails.append("%s: dp[%s] is %r, not an integer" % (c["slug"], ax, n))
            elif has and abs(float("%.*f" % (n, v)) - float(v)) > 5e-9:
                fails.append("%s: %s = %r does NOT round-trip at %d dp (prints %.*f) — the "
                             "stated source precision would drop a digit this file holds"
                             % (c["slug"], ax, v, n, n, v))
            elif (not has) and isinstance(n, int):
                fails.append("%s: dp[%s] = %d but the axis is null — a precision for a "
                             "dimension nobody published" % (c["slug"], ax, n))

    for c in C["components"]:
        sh = shelf(c["slug"])
        bb = (sh or {}).get("component", {}).get("bbox_mm") if sh else None
        d = c.get("dimensions_mm") or {}
        if bb and any(d.get(k) is not None for k in "xyz"):
            here = [d.get("x"), d.get("y"), d.get("z")]
            same = (len(bb) == 3 and all(
                a is not None and b is not None and abs(float(a) - float(b)) < 5e-4
                for a, b in zip(here, bb)))
            if same:
                notes.append("%s: envelope agrees with ce-parts bbox_mm %s "
                             "(stated twice on purpose — this check is the guard)"
                             % (c["slug"], bb))
            else:
                fails.append("%s: envelope DISAGREES — components.json %s vs "
                             "ce-parts bbox_mm %s. One of them is stale."
                             % (c["slug"], here, bb))

    for f in fails:
        print("FAIL             %s" % f)
    for c in cds:
        print("CANNOT DETERMINE %s" % c)
    for n in notes:
        print("note             %s" % n)
    print("--- %d paths followed, %d FAIL, %d CANNOT DETERMINE, %d notes"
          % (len(seen), len(fails), len(cds), len(notes)))
    return 1 if fails else (2 if cds else 0)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="ELECTRONICS-DATASHEET.html")
    ap.add_argument("--check", action="store_true",
                    help="follow every reference the page makes; exit 0/1/2")
    a = ap.parse_args()
    if a.check:
        raise SystemExit(check())
    build(a.out)
