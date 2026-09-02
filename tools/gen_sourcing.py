#!/usr/bin/env python3
"""gen_sourcing.py - build SOURCING.html and RFQ.html from spec/sourcing.json.

Lane E deliverable (GOAL.md). Neither page is ever hand-edited: this script owns
both. The cost roll-up follows spec/sourcing.json's own `rules` block:

  * A price enters a total only if a human-readable vendor page carried it and
    the fetch date is recorded. A price nobody read is CANNOT DETERMINE.
  * No FX rate was fetched, so nothing is converted. Only USD offers enter the
    USD subtotal; EUR/GBP/NZD/AUD/INR lines are reported unconverted beside it.
  * An unknown is NEVER summed as zero. The roll-up publishes the readable
    subtotal and the CANNOT DETERMINE list as two separate numbers.
  * For N robots the order quantity of a line is qty_per_robot x N; the unit
    price used is the vendor's largest published tier <= that quantity. A
    vendor with no tier table keeps its @1 price at every quantity, as a
    CEILING.

Run:  python3 tools/gen_sourcing.py       (stdlib only; no FreeCAD needed)
"""
import json, os, html, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = json.load(open(os.path.join(REPO, "spec", "sourcing.json")))
ROBOT_COUNTS = [1, 100, 1000]

E = lambda s: html.escape(str(s))


def clip(text, n):
    """Truncate on a word boundary so a table cell never ends mid-word."""
    text = str(text)
    if len(text) <= n:
        return text
    cut = text[:n].rsplit(" ", 1)[0]
    return (cut or text[:n]) + "\u2026"


def qty_txt(v):
    """Order quantity as a person writes it: integers with separators, and a
    fractional kilogram stays fractional rather than becoming 1.5e+04."""
    return f"{v:,.0f}" if abs(v - round(v)) < 1e-9 else f"{v:,.4f}".rstrip("0").rstrip(".")


# ---------------------------------------------------------------- pricing ---
def tier_price(offer, order_qty):
    """Unit price at `order_qty` pieces from one offer's own tier table.
    Returns (unit_price, tier_qty, moq_exceeds_need) or (None, None, None)."""
    tiers = offer.get("tiers") or []
    if not tiers:
        return None, None, None
    tiers = sorted(tiers, key=lambda t: t[0])
    moq = offer.get("moq") or tiers[0][0]
    if order_qty < moq:
        return tiers[0][1], tiers[0][0], True
    pick = tiers[0]
    for q, p in tiers:
        if q <= order_qty:
            pick = (q, p)
    return pick[1], pick[0], False


def usable(offer):
    return (offer.get("confidence") == "read"
            and not offer.get("excluded_from_rollup")
            and (offer.get("tiers") or []))


def line_cost(line, n_robots):
    """Cheapest READ USD offer for one line at N robots.
    Returns dict or None when nothing is readable in USD."""
    qpr = line.get("qty_per_robot")
    if not qpr:                                   # None or 0
        return None
    if line.get("excluded_from_rollup"):
        return None

    if line.get("kit"):                            # offers are components
        total, parts, ceiling, moqflag = 0.0, [], False, False
        for k in line["kit"]:
            off = line["offers"][k["offer"]]
            if off.get("currency") != "USD" or not usable(off):
                return None
            need = k["qty_per_robot"] * n_robots
            up, tq, mo = tier_price(off, need)
            if up is None:
                return None
            total += up * k["qty_per_robot"]
            ceiling |= bool(off.get("no_tiers"))
            moqflag |= bool(mo)
            parts.append(f'{k["what"]} x{k["qty_per_robot"]} @ ${up:.5f}')
        return {"vendor": "DigiKey (kit)", "unit": None, "per_robot": total,
                "tier_qty": None, "ceiling": ceiling, "moq_exceeds": moqflag,
                "detail": " + ".join(parts), "range_high": False,
                "caveat": None, "stock": None, "page_kind": None, "url": None}

    best = None
    for off in line["offers"]:
        if off.get("currency") != "USD" or not usable(off):
            continue
        need = qpr * n_robots
        up, tq, mo = tier_price(off, need)
        if up is None:
            continue
        cand = {"vendor": off["vendor"], "unit": up, "per_robot": up * qpr,
                "tier_qty": tq, "ceiling": bool(off.get("no_tiers")),
                "moq_exceeds": bool(mo), "detail": off.get("sku") or "",
                "range_high": bool(off.get("price_is_range_high")),
                "caveat": off.get("rollup_caveat"), "stock": off.get("stock"),
                "page_kind": off.get("page_kind"), "url": off["url"]}
        if best is None or cand["per_robot"] < best["per_robot"]:
            best = cand
    return best


def native_lines():
    """Lines with NO readable USD price but a readable price in another
    currency. Reported unconverted; never added to anything."""
    out = []
    for ln in DATA["lines"]:
        qpr = ln.get("qty_per_robot")
        if not qpr or ln.get("excluded_from_rollup"):
            continue
        if line_cost(ln, 1):
            continue
        for off in ln["offers"]:
            if off.get("currency") == "USD" or not usable(off):
                continue
            row = {}
            for n in ROBOT_COUNTS:
                up, tq, mo = tier_price(off, qpr * n)
                row[n] = (up * qpr) if up is not None else None
            if row[1] is not None:
                out.append((ln, off, row))
                break
    return out


READ = {}      # id -> {n: costdict}
for ln in DATA["lines"]:
    READ[ln["id"]] = {n: line_cost(ln, n) for n in ROBOT_COUNTS}

SUBTOTAL = {n: sum(READ[l["id"]][n]["per_robot"]
                   for l in DATA["lines"] if READ[l["id"]][n]) for n in ROBOT_COUNTS}
PRICED = [l for l in DATA["lines"] if READ[l["id"]][1]]
# A price being readable does not make the line buyable. Split the roll-up by
# the verdict this document itself gives the line, so that money coming from a
# line graded FAIL or CANNOT DETERMINE is never inside the headline number.
PRICED_OK = [l for l in PRICED if l["verdict"] == "PASS"]
PRICED_QUAL = [l for l in PRICED if l["verdict"] != "PASS"]
SUB_OK = {n: sum(READ[l["id"]][n]["per_robot"] for l in PRICED_OK) for n in ROBOT_COUNTS}
SUB_QUAL = {n: sum(READ[l["id"]][n]["per_robot"] for l in PRICED_QUAL) for n in ROBOT_COUNTS}
QUAL_PCT = (100.0 * SUB_QUAL[1] / SUBTOTAL[1]) if SUBTOTAL[1] else 0.0
NATIVE = native_lines()
NATIVE_IDS = {ln["id"] for ln, _, _ in NATIVE}
UNKNOWN = [l for l in DATA["lines"]
           if not READ[l["id"]][1] and l["id"] not in NATIVE_IDS
           and not l.get("excluded_from_rollup")]
REFERENCE = [l for l in DATA["lines"] if l.get("qty_per_robot") == 0
             or l.get("excluded_from_rollup")]
UNKNOWN = [l for l in UNKNOWN if l not in REFERENCE]

# Two-label suffixes seen on this lane's vendor pages. Not a public-suffix
# list: a host whose suffix is not listed keeps its last two labels, which is
# the conservative answer (it can only MERGE two shops, never split one).
MULTI_SUFFIX = {
    "co.uk", "org.uk", "ac.uk", "co.nz", "com.au", "net.au", "co.in", "co.jp",
    "com.cn", "com.br", "com.mx", "co.za", "com.sg", "com.hk", "com.tw",
}


def reg_domain(url):
    """The registered domain a URL belongs to - the thing a buyer would call
    'a shop'. This is what counts as a distributor, NOT the vendor name string:
    'DigiKey', 'DigiKey (cut tape)' and 'DigiKey (cut tape / Digi-Reel)' are
    three names and one shop, and counting names let one shop priced three ways
    look like three distributors. Measured defect, 2026-09-03."""
    host = url.split("//", 1)[-1].split("/", 1)[0].split("?", 1)[0]
    host = host.split("@")[-1].split(":")[0].lower().rstrip(".")
    if host.startswith("www."):
        host = host[4:]
    parts = [p for p in host.split(".") if p]
    if len(parts) <= 2:
        return ".".join(parts)
    if ".".join(parts[-2:]) in MULTI_SUFFIX:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def read_domains(line):
    return {reg_domain(o["url"]) for o in line["offers"]
            if o.get("confidence") == "read"}


def n_read(line):
    """DISTINCT distributors with a price read on a page, counted as REGISTERED
    DOMAINS. Counting offers would let one shop priced four ways look like four
    distributors; counting vendor NAME STRINGS - what this did until
    2026-09-03 - let the same shop entered under two spellings do it too."""
    return len(read_domains(line))


ALL_DOMAINS = sorted({d for l in DATA["lines"] for d in read_domains(l)})
ALL_VENDOR_NAMES = sorted({o["vendor"] for l in DATA["lines"] for o in l["offers"]
                           if o.get("confidence") == "read"})

VERDICTS = {"PASS": 0, "FAIL": 0, "CANNOT DETERMINE": 0}
for l in DATA["lines"]:
    VERDICTS[l["verdict"]] = VERDICTS.get(l["verdict"], 0) + 1

def selfcheck():
    """The verdict in the data must agree with what the data actually holds.
    A PASS with fewer than two distinct read distributors, or a PASS whose
    line has no price at any of the three quantities, is a defect in the DATA
    and this refuses to publish it. Broken on purpose once (a PASS forced onto
    B13, which has no offers) and it went red naming the line."""
    bad = []
    for l in DATA["lines"]:
        if l["verdict"] != "PASS":
            continue
        if n_read(l) < 2:
            bad.append(f'{l["id"]}: PASS with {n_read(l)} distinct read distributor(s)')
        priced = READ[l["id"]][1] or l.get("basket") or any(
            o.get("confidence") == "read" and (o.get("tiers") or []) for o in l["offers"])
        if not priced:
            bad.append(f'{l["id"]}: PASS with no price read anywhere')
    # A price read off a listing / search page is not a durable citation: the
    # listing reflows and the number is gone. Three of them were found on
    # 2026-09-03 (B4 Neewer, B7 The Pi Hut, B11 VXB); all three were replaced
    # with the product page and re-read. This refuses to let a fourth in.
    for l in DATA["lines"]:
        for o in l["offers"]:
            if o.get("confidence") == "read" and o.get("page_kind") == "listing":
                bad.append(f'{l["id"]}: price read off a listing page - {o["url"]}')
    if bad:
        raise SystemExit("REFUSING TO PUBLISH - verdicts disagree with the data:\n  "
                         + "\n  ".join(bad))
    return len([l for l in DATA["lines"] if l["verdict"] == "PASS"])


def unknown_sentence():
    """The unpriced lines, named from the data. A hand-typed list beside a
    computed len(UNKNOWN) drifts: until 2026-09-03 this sentence named the
    camera ribbon, which is line B8 and IS priced, and omitted the LED, the
    gamepad and the USB-C cable. There is nothing to keep in step now."""
    names = [f'{l["id"]} {clip(l["item"], 52)}' for l in UNKNOWN]
    if not names:
        return "none"
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


UNKNOWN_SENTENCE = unknown_sentence()

CHIP = {"PASS": "pass", "FAIL": "rail", "CANNOT DETERMINE": "cd"}
GEN = datetime.date.today().isoformat()


# -------------------------------------------------------------- SOURCING ----
def offer_rows(line):
    rows = []
    for off in line["offers"]:
        tiers = off.get("tiers") or []
        if tiers:
            ts = ", ".join(f"{q:,}+ {off['currency']} {p:g}" for q, p in sorted(tiers))
        else:
            ts = "<span class='cdtxt'>no price read</span>"
        flags = []
        if off.get("no_tiers"):
            flags.append("no tier table published &mdash; @1 is a ceiling")
        if off.get("price_is_range_high"):
            flags.append("vendor states a RANGE; the HIGH end is recorded")
        if off.get("excluded_from_rollup"):
            flags.append("excluded from the roll-up: " + off["excluded_from_rollup"])
        if off.get("page_kind") == "family-table":
            flags.append("the URL is the vendor&#39;s family price table, not a per-size "
                         "product page &mdash; the size and its price are printed on it, "
                         "but there is no page for this size alone")
        if off.get("page_kind") == "listing":
            flags.append("the URL is a listing / search page, NOT a product page")
        if off.get("rollup_caveat"):
            flags.append("carried into Table&nbsp;1 with this caveat: " + off["rollup_caveat"])
        conf = "read" if off.get("confidence") == "read" else "NOT READ"
        dom = reg_domain(off["url"])
        rows.append(f"""<tr>
  <td>{E(off['vendor'])}<br><span class="sub2"><a href="{E(off['url'])}">{E(off.get('sku') or off['url'][:58])}</a></span></td>
  <td class="n">{ts}</td>
  <td class="n">{E(off.get('moq') if off.get('moq') is not None else '&mdash;')}</td>
  <td>{E(off.get('lead_time') or '&mdash;')}</td>
  <td>{E(off.get('stock') or '&mdash;')}</td>
  <td><span class="chip {'pass' if conf=='read' else 'cd'}">{conf}</span> {E(off.get('fetched') or '')}
      <div class="sub2">counts as distributor <code>{E(dom)}</code></div>
      {'<div class="sub2">' + E(off['note']) + '</div>' if off.get('note') else ''}
      {''.join('<div class="flag">' + f + '</div>' for f in flags)}</td>
</tr>""")
    if not rows:
        rows.append('<tr><td colspan="6" class="cdtxt">No offer with a price read on any page.</td></tr>')
    return "\n".join(rows)


def alt_rows(line):
    if not line.get("alternates"):
        return ""
    r = []
    for a in line["alternates"]:
        u = f'<a href="{E(a["url"])}">{E(a["vendor"] or "source")}</a>' if a.get("url") else E(a.get("vendor") or "&mdash;")
        r.append(f"""<tr><td><code>{E(a['mpn'])}</code></td><td>{E(a['why_equivalent'])}</td>
        <td>{u}<div class="sub2">{E(a.get('price_note') or '')}</div></td></tr>""")
    return f"""<div class="tablewrap"><table class="alt">
<thead><tr><th>Alternate</th><th>Why it is (or is not) equivalent</th><th>Where / price</th></tr></thead>
<tbody>{''.join(r)}</tbody></table></div>"""


def basket_block(line):
    """A line whose sizes are priced individually and cannot share one unit
    price. Rendered in its own currency, outside every subtotal."""
    b = line.get("basket")
    if not b:
        return ""
    rows, tot = [], 0.0
    for r in b["rows"]:
        tot += r["qty"] * r["unit"]
        rows.append(f'<tr><td>{E(r["what"])}</td><td class="n">{r["qty"]:g}</td>'
                    f'<td class="n">{b["currency"]} {r["unit"]:.4f}</td>'
                    f'<td class="n">{b["currency"]} {r["qty"]*r["unit"]:.4f}</td></tr>')
    for m in b.get("missing", []):
        rows.append(f'<tr><td>{E(m["what"])}</td><td class="n">{m["qty"]:g}</td>'
                    f'<td class="cdtxt">CANNOT DETERMINE</td>'
                    f'<td class="cdtxt">{E(m["why"])}</td></tr>')
    return f"""<p class="lab">Priced size by size &mdash; {E(b['currency'])}, outside every subtotal</p>
<div class="tablewrap"><table class="data">
<thead><tr><th>Size</th><th>Qty/robot</th><th>Unit</th><th>Per robot</th></tr></thead>
<tbody>{''.join(rows)}
<tr class="totalrow"><td>FLOOR for the priced sizes only</td><td class="n"></td><td class="n"></td>
<td class="n">{E(b['currency'])} {tot:.4f}</td></tr></tbody></table></div>
<p class="note">{E(b['note'])}</p>"""


def line_block(line):
    q = line.get("qty_per_robot")
    qtxt = ("<span class='cdtxt'>CANNOT DETERMINE</span>" if q is None
            else ("0 <span class='sub2'>(reference line &mdash; arrives inside another purchase)</span>"
                  if q == 0 else f"{q:g} {E(line.get('qty_unit') or '')}"))
    unk = "".join(f"<li>{E(u)}</li>" for u in line.get("unknowns", []))
    blk = "".join(f'<li><a href="{E(b["url"])}">{E(b["url"][:88])}</a> &mdash; {E(b["reason"])}</li>'
                  for b in line.get("blocked", []))
    ce = f' &middot; <code>{E(line["ce_part"])}</code>' if line.get("ce_part") else ""
    vw = f'<p class="verdict {"warn" if line["verdict"]!="PASS" else ""}"><b>{E(line["verdict"])}</b> &mdash; {E(line["verdict_why"])}</p>' if line.get("verdict_why") else ""
    mn = f'<p class="note">{E(line["mpn_note"])}</p>' if line.get("mpn_note") else ""
    return f"""
<h3 id="line-{E(line['id'])}"><span class="lid">{E(line['id'])}</span> {E(line['item'])}
  <span class="chip {CHIP.get(line['verdict'],'cd')}">{E(line['verdict'])}</span></h3>
<p class="meta">Qty per robot {qtxt} &middot; basis: {E(line['qty_basis'])}{ce}</p>
<p class="meta">MPN <code>{E(line['mpn'])}</code> &middot; <i>{E(line['mpn_status'])}</i>
  &middot; {n_read(line)} distinct distributor(s) with a price read</p>
{mn}{vw}
<div class="tablewrap"><table class="data offers">
<thead><tr><th>Distributor</th><th>Unit price at the vendor's own tiers</th><th>MOQ</th>
<th>Lead time (as printed)</th><th>Stock, on this offer&#39;s own fetch date</th><th>Read?</th></tr></thead>
<tbody>{offer_rows(line)}</tbody></table></div>
{basket_block(line)}
{alt_rows(line)}
{'<p class="lab">Open on this line</p><ul class="tight">' + unk + '</ul>' if unk else ''}
{'<p class="lab">Pages that refused a price</p><ul class="tight small">' + blk + '</ul>' if blk else ''}
"""


DEAD_STOCK = ("sold out", "out of stock", "0 in stock", "unavailable", "backorder")


def rollup_rows(lines):
    out = []
    for l in sorted(lines, key=lambda x: -READ[x["id"]][1]["per_robot"]):
        c = {n: READ[l["id"]][n] for n in ROBOT_COUNTS}
        marks = []
        if c[1]["ceiling"]:
            marks.append("ceiling &mdash; vendor publishes no tier table")
        if c[1]["moq_exceeds"]:
            marks.append("MOQ &gt; need")
        if c[1]["range_high"]:
            marks.append("range high end")
        if c[1].get("page_kind") == "family-table":
            marks.append("price read off the vendor&#39;s family price table, "
                         "not a per-size product page")
        st = (c[1].get("stock") or "")
        if any(k in st.lower() for k in DEAD_STOCK):
            marks.append(f"stock on the fetch date: {E(st)}")
        if c[1].get("caveat"):
            marks.append(E(c[1]["caveat"]))
        chip = f'<span class="chip {CHIP.get(l["verdict"], "cd")}">{E(l["verdict"])}</span>'
        out.append(f"""<tr><td><a href="#line-{E(l['id'])}">{E(l['id'])}</a> {E(clip(l['item'], 62))}</td>
<td>{chip}</td>
<td class="n">{l['qty_per_robot']:g}</td><td>{E(c[1]['vendor'])}</td>
<td class="n">${c[1]['per_robot']:,.4f}</td><td class="n">${c[100]['per_robot']:,.4f}</td>
<td class="n">${c[1000]['per_robot']:,.4f}</td>
<td class="sub2">{'; '.join(marks) if marks else '&mdash;'}</td></tr>""")
    return "\n".join(out)


def native_rows():
    out = []
    for ln, off, row in NATIVE:
        out.append(f"""<tr><td><a href="#line-{E(ln['id'])}">{E(ln['id'])}</a> {E(clip(ln['item'], 62))}</td>
<td class="n">{ln['qty_per_robot']:g}</td><td>{E(off['vendor'])}</td><td class="n">{E(off['currency'])}</td>
<td class="n">{row[1]:,.4f}</td><td class="n">{row[100]:,.4f}</td><td class="n">{row[1000]:,.4f}</td></tr>""")
    return "\n".join(out)


def unknown_rows():
    out = []
    for l in UNKNOWN:
        why = l.get("verdict_why") or (l["unknowns"][0] if l.get("unknowns") else "")
        out.append(f"""<tr><td><a href="#line-{E(l['id'])}">{E(l['id'])}</a> {E(clip(l['item'], 62))}</td>
<td class="n">{'&mdash;' if l.get('qty_per_robot') is None else f"{l['qty_per_robot']:g}"}</td>
<td>{E(why)}</td></tr>""")
    return "\n".join(out)


HEAD = """<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="tools/doc.css">
<style>
  .lid{font-family:var(--mono);font-size:.72em;color:var(--accent);border:1px solid var(--hair);
       padding:1px 6px;margin-right:8px;vertical-align:2px}
  h3{margin:30px 0 4px}
  .meta{font-family:var(--sans);font-size:12.5px;color:var(--ink-2);margin:2px 0}
  .sub2{font-family:var(--sans);font-size:11.5px;color:var(--ink-2);line-height:1.4}
  .flag{font-family:var(--sans);font-size:11.5px;color:var(--partial);margin-top:3px}
  .cdtxt{color:var(--partial);font-family:var(--sans);font-size:12px;font-weight:600}
  .note{font-size:13.5px;color:var(--ink-2);max-width:46em;margin:6px 0}
  .verdict{border-left:3px solid var(--ready);padding:2px 0 2px 16px;margin:10px 0;font-size:14.5px;max-width:48em}
  .verdict b{color:var(--ready)}
  .verdict.warn{border-left-color:var(--partial)} .verdict.warn b{color:var(--partial)}
  .lab{font-family:var(--sans);font-size:11px;letter-spacing:.08em;text-transform:uppercase;
       color:var(--ink-2);margin:14px 0 2px}
  ul.tight{margin:2px 0 6px;padding-left:20px} ul.tight li{font-size:13.5px;margin:3px 0}
  ul.small li{font-size:12px;font-family:var(--sans);color:var(--ink-2)}
  table.alt{table-layout:fixed}
  table.alt td,table.alt th{overflow-wrap:anywhere;white-space:normal}
  table.alt th:nth-child(1),table.alt td:nth-child(1){width:29%}
  table.alt th:nth-child(2),table.alt td:nth-child(2){width:46%}
  table.alt th:nth-child(3),table.alt td:nth-child(3){width:25%}
  table.offers{table-layout:fixed}
  table.offers th:nth-child(1),table.offers td:nth-child(1){width:16%}
  table.offers th:nth-child(2),table.offers td:nth-child(2){width:21%;font-family:var(--mono);font-size:11px;white-space:normal;word-break:break-word}
  table.offers th:nth-child(3),table.offers td:nth-child(3){width:6%}
  table.offers th:nth-child(4),table.offers td:nth-child(4){width:17%;font-size:12.5px}
  table.offers th:nth-child(5),table.offers td:nth-child(5){width:14%;font-size:12.5px}
  table.offers th:nth-child(6),table.offers td:nth-child(6){width:26%}
  table.offers td{word-break:break-word}
  table.offers th{white-space:normal}
  table.rollup{table-layout:fixed}
  table.rollup td.n{font-size:11.5px}
  table.rollup th{white-space:normal;vertical-align:bottom}
  table.rollup td{overflow-wrap:break-word}
  table.rollup td .chip{font-size:9.5px;letter-spacing:.02em;white-space:normal;display:inline-block}
  table.rollup th:nth-child(1),table.rollup td:nth-child(1){width:16%}
  table.rollup th:nth-child(2),table.rollup td:nth-child(2){width:9%}
  table.rollup th:nth-child(3),table.rollup td:nth-child(3){width:10%}
  table.rollup th:nth-child(4),table.rollup td:nth-child(4){width:14%;font-size:12px}
  table.rollup th:nth-child(5),table.rollup td:nth-child(5){width:11%}
  table.rollup th:nth-child(6),table.rollup td:nth-child(6){width:11%}
  table.rollup th:nth-child(7),table.rollup td:nth-child(7){width:11%}
  table.rollup th:nth-child(8),table.rollup td:nth-child(8){width:18%;overflow-wrap:anywhere}
  tr.grouprow td{background:var(--head);font-family:var(--sans);font-size:12px;
       color:var(--ink-2);padding-top:9px;padding-bottom:9px}
  .totalrow td{border-top:1.5px solid var(--rule);font-weight:700}
  .warnbox{border:1.5px solid var(--no);padding:14px 18px;margin:18px 0}
  .warnbox h3{margin:0 0 6px;font-family:var(--sans);font-size:13px;letter-spacing:.06em;
       text-transform:uppercase;color:var(--no)}
  .rfq{border:1px solid var(--rule);padding:22px 26px;margin:26px 0;background:var(--paper)}
  .rfq h3{margin:0 0 2px;font-size:18px}
  .ph{background:var(--head);border:1px dashed var(--partial);padding:1px 6px;
      font-family:var(--mono);font-size:12px;color:var(--partial)}
  .rfq pre{white-space:pre-wrap;font-family:var(--serif);font-size:14px;line-height:1.55;margin:10px 0}
</style>"""


SOURCING = f"""<!doctype html>
<html lang="en"><head>{HEAD}
<title>Microduck Sourcing</title></head>
<body><div class="wrap">
<p class="backlink"><a href="RELEASE.html">&larr; Release dossier</a> &middot; <a href="RFQ.html">Requests for quotation &rarr;</a></p>

<header class="hero">
  <p class="eyebrow">Microduck reverse-engineering &middot; procurement</p>
  <h1>Sourcing: every bought line, with the vendor page it was read from</h1>
  <p class="sub">One record per purchased line of the bill of materials: at least two real
  distributors wherever two exist, the unit price at the vendor's own tiers, MOQ, lead time,
  and an alternate with the reason it is or is not equivalent. Nothing here is estimated.
  A price nobody read is <b>CANNOT DETERMINE</b>, printed with the URL that refused it.</p>
  <div class="rev">
    <span>MD-SRC-001 &middot; Rev {DATA['revision']}</span><span>generated {GEN}</span>
    <span>pages fetched {', '.join(DATA['fetch_dates'])}</span>
    <span>source: <code>spec/sourcing.json</code> &rarr; <code>tools/gen_sourcing.py</code></span>
  </div>
</header>

<div class="statbar">
  <div class="stat"><b>{len(DATA['lines'])}</b><span>bought lines</span></div>
  <div class="stat"><b>{VERDICTS.get('PASS',0)}</b><span>PASS &mdash; two or more shops read</span></div>
  <div class="stat"><b>{VERDICTS.get('CANNOT DETERMINE',0)}</b><span>CANNOT DETERMINE</span></div>
  <div class="stat"><b>{VERDICTS.get('FAIL',0)}</b><span>FAIL &mdash; unbuyable as specified</span></div>
  <div class="stat"><b>${SUB_OK[1]:,.4f}</b><span>USD / robot @1, lines graded PASS</span></div>
  <div class="stat"><b>${SUB_QUAL[1]:,.4f}</b><span>readable, but from lines graded FAIL / CD</span></div>
  <div class="stat"><b>{len(UNKNOWN)}</b><span>lines with no price at all</span></div>
  <div class="stat"><b>{len(ALL_DOMAINS)}</b><span>distinct distributors read (registered domains)</span></div>
  <div class="stat"><b>{sum(len(l.get("blocked", [])) for l in DATA["lines"])}</b><span>pages that refused a price</span></div>
</div>

<nav class="toc">
  <a href="#rules">1 How to read this</a><a href="#rollup">2 Cost roll-up</a>
  <a href="#unknown">3 What has no price</a><a href="#lines">4 Every line</a>
  <a href="#method">5 Method &amp; retry list</a>
</nav>

<section id="rules"><h2><span class="n">1</span> How to read this</h2>
<p class="lede">Five rules decide every number on this page. They are stored beside the data in
<code>spec/sourcing.json</code>, not in this prose, so the generator and the reader cannot drift apart.</p>
<div class="grid2">
  <div class="card"><h3>A price is a reading</h3><p>{E(DATA['rules']['price_basis'])}</p></div>
  <div class="card"><h3>Quantity model</h3><p>{E(DATA['rules']['quantity_model'])}</p></div>
  <div class="card"><h3>No currency is converted</h3><p>{E(DATA['rules']['currency'])}</p></div>
  <div class="card"><h3>An unknown is never zero</h3><p>{E(DATA['rules']['readable_vs_unknown'])}</p></div>
  <div class="card"><h3>The three verdicts</h3><p>{E(DATA['rules']['verdict'])}</p></div>
  <div class="card"><h3>The page refuses to publish a verdict it cannot support</h3>
  <p>Before either page is written, <code>selfcheck()</code> re-derives every PASS from the data: two or
  more <i>distinct</i> distributors with a price read, and a price at every quantity. It caught four
  wrong verdicts on the first run (B12, B19a, C1, C2 &mdash; three of them one shop counted twice) and
  refused to write. Broken on purpose afterwards by forcing PASS onto B13, which has no offers at all:
  it went red naming the line and wrote nothing.</p>
  <p><b>It counted the wrong thing until 2026-09-03.</b> &ldquo;Distinct&rdquo; meant distinct vendor
  <i>name strings</i>, so the defect the check exists to catch could walk straight past it: one shop
  entered under two names is two names and one shop. Demonstrated by rewriting B11&#39;s second offer to
  a second listing on <code>bearingsdirect.com</code> &mdash; the old generator published B11 as PASS with
  &ldquo;2 distinct distributor(s)&rdquo; and exited 0. It now counts <b>registered domains</b>, and the
  same mutation makes it exit 1 with <code>B11: PASS with 1 distinct read distributor(s)</code>, having
  written nothing. A second guard was added at the same time: a price read off a listing or search page
  rather than a product page refuses to publish, because a listing reflows and the number is gone.
  {VERDICTS.get('PASS',0)} PASS lines survive both.</p></div>
  <div class="card"><h3>Nothing was sent</h3><p>No supplier was contacted, no order was placed and no
  money was spent producing this document. <a href="RFQ.html">RFQ.html</a> is written and ready; sending it
  is a human decision.</p></div>
</div></section>

<section id="rollup"><h2><span class="n">2</span> Cost roll-up</h2>
<p class="lede">Per robot, at 1, 100 and 1&nbsp;000 robots. Each line takes the cheapest distributor
whose price was <i>read</i>, at the tier the order quantity reaches. <b>ceiling</b> marks a vendor
with no tier table, whose &#64;1 price is carried forward unchanged; <b>MOQ&nbsp;&gt;&nbsp;need</b> marks
a vendor whose minimum exceeds what one robot needs.</p>

<p class="lab">Table 1. USD lines with a read price &mdash; cost per robot</p>
<div class="tablewrap"><table class="data rollup">
<thead><tr><th>Line</th><th>Verdict</th><th>Qty /<br>robot</th><th>Cheapest<br>read vendor</th>
<th>@ 1<br>robot</th><th>@ 100<br>robots</th><th>@ 1 000<br>robots</th><th>Flags</th></tr></thead>
<tbody>
{rollup_rows(PRICED_OK)}
<tr class="totalrow"><td>SUBTOTAL &mdash; {len(PRICED_OK)} lines graded PASS</td><td></td><td class="n"></td><td></td>
<td class="n">${SUB_OK[1]:,.4f}</td><td class="n">${SUB_OK[100]:,.4f}</td>
<td class="n">${SUB_OK[1000]:,.4f}</td><td></td></tr>
<tr class="grouprow"><td colspan="8">Priced, but this document does not grade the line buyable
&mdash; the flag on each row says why. These {len(PRICED_QUAL)} lines are shown because their prices were read,
and are kept OUT of the subtotal above.</td></tr>
{rollup_rows(PRICED_QUAL)}
<tr class="totalrow"><td>SUBTOTAL &mdash; {len(PRICED_QUAL)} lines graded FAIL or CANNOT DETERMINE</td><td></td><td class="n"></td><td></td>
<td class="n">${SUB_QUAL[1]:,.4f}</td><td class="n">${SUB_QUAL[100]:,.4f}</td>
<td class="n">${SUB_QUAL[1000]:,.4f}</td><td></td></tr>
<tr class="totalrow"><td>EVERY READABLE USD LINE &mdash; {len(PRICED)} lines</td><td></td><td class="n"></td><td></td>
<td class="n">${SUBTOTAL[1]:,.4f}</td><td class="n">${SUBTOTAL[100]:,.4f}</td>
<td class="n">${SUBTOTAL[1000]:,.4f}</td><td></td></tr>
</tbody></table></div>

<p class="note"><b>Why the table has three totals and not one.</b> A price being readable does not make the
line buyable. {len(PRICED_QUAL)} of the {len(PRICED)} priced lines are graded FAIL or CANNOT DETERMINE by
this same document &mdash; <b>${SUB_QUAL[1]:,.4f} of the ${SUBTOTAL[1]:,.4f} readable at one robot,
{QUAL_PCT:,.2f}&nbsp;% of it</b> &mdash; and until 2026-09-03 that money sat inside a single headline
subtotal with nothing in the row to say so. It is now split out, and the flag on every such row carries the
reason from the line&#39;s own record: the wrong SKU, sold out on the fetch date, a part that does not fit
the cavity, or an unfixed specification.</p>

<p class="note"><b>Two things this table does on purpose.</b> A line whose need is smaller than the
vendor's minimum &mdash; 0.2183&nbsp;kg of a 1&nbsp;kg filament spool, 60 of a 100-piece insert pack, 11
of a 1&nbsp;000-piece bearing lot &mdash; is <i>prorated</i>: the per-robot figure is the unit price times the
per-robot quantity, so the remainder of the pack is charged to the next robot rather than to this one.
At a build of exactly one robot you pay the whole pack, and the <b>MOQ&nbsp;&gt;&nbsp;need</b> flag is
where that is said. And the cheapest read vendor is chosen per line and per quantity independently, so a
line can change supplier between the @1 and the @100 column &mdash; B9 moves from DigiKey to Pololu, B6
from Seeed's @1 to Seeed's 10+ tier. Nothing is blended.</p>

<p class="lab">Table 2. Lines readable only in another currency &mdash; NOT converted, NOT added</p>
<div class="tablewrap"><table class="data">
<thead><tr><th>Line</th><th>Qty/robot</th><th>Vendor</th><th>Cur</th>
<th>@ 1</th><th>@ 100</th><th>@ 1 000</th></tr></thead>
<tbody>{native_rows() or '<tr><td colspan="7">none</td></tr>'}</tbody></table></div>

<p class="lab">Table 3. The second subtotal &mdash; what the readable subtotal does NOT contain</p>
<div class="tablewrap"><table class="data">
<thead><tr><th>Line</th><th>Qty/robot</th><th>Why it carries no price</th></tr></thead>
<tbody>{unknown_rows()}
<tr class="totalrow"><td>CANNOT DETERMINE SUBTOTAL &mdash; {len(UNKNOWN)} lines</td><td class="n"></td>
<td>Not a number. These lines are unpriced, and summing them as zero would state that they are free.</td></tr>
</tbody></table></div>

<p class="verdict warn"><b>Read this before quoting a unit cost.</b>
The subtotal of the lines graded PASS is <b>${SUB_OK[1]:,.4f}</b> at one robot and <b>${SUB_OK[1000]:,.4f}</b> at a
thousand &mdash; it moves by ${SUB_OK[1]-SUB_OK[1000]:,.4f} across a factor of a thousand in volume,
because the servos are the majority of it and ROBOTIS publishes no tier at any quantity. A further
${SUB_QUAL[1]:,.4f} at one robot is readable but comes from {len(PRICED_QUAL)} line(s) this document grades FAIL
or CANNOT DETERMINE, and is kept separate. The subtotal excludes {len(UNKNOWN)} unpriced lines
&mdash; {UNKNOWN_SENTENCE} &mdash; and every non-USD line in Table&nbsp;2. It is a floor, not a cost.</p>
</section>

<section id="unknown"><h2><span class="n">3</span> What has no price, and what would settle it</h2>
<p class="lede">Each of these is a work item with a named next step, not a shrug.</p>
<ul class="tight">
{''.join('<li><b>' + E(l['id']) + ' ' + E(l['item']) + '</b> &mdash; ' + E((l.get('verdict_why') or '')) + ' ' + ' '.join(E(u) for u in l.get('unknowns', [])) + '</li>' for l in UNKNOWN)}
</ul>
</section>

<section id="lines"><h2><span class="n">4</span> Every line, in full</h2>
<p class="lede">Distributors, tier tables as the vendor prints them, MOQ, lead time, stock on the fetch
date, alternates with the equivalence argument, the open questions, and every page that refused.</p>
{''.join(line_block(l) for l in DATA['lines'])}
</section>

<section id="method"><h2><span class="n">5</span> Method, and the pages that must be retried</h2>
<p>Every figure above was read from a vendor page fetched on {', '.join(DATA['fetch_dates'])}, or from
a page a prior lane fetched the same day and cited in <code>docs/production/components.md</code>. Where a
page answered 403, 402, 500, a closed socket or a body with no price, that URL is printed on its own
line so the next attempt starts where this one stopped &mdash; a browser session reads most of them.</p>
<p class="lab">Every blocked URL on this page, collected</p>
<ul class="tight small">
{''.join('<li><b>' + E(l['id']) + '</b> <a href="' + E(b['url']) + '">' + E(b['url'][:96]) + '</a> &mdash; ' + E(b['reason']) + '</li>' for l in DATA['lines'] for b in l.get('blocked', []))}
</ul>
<p class="lab">What counts as a distributor</p>
<p class="note">{len(ALL_DOMAINS)} distinct distributors were read, counted as <b>registered domains</b>.
They are entered in the data under {len(ALL_VENDOR_NAMES)} vendor name strings, because the same shop is
named differently where the packaging differs &mdash; DigiKey appears as <code>DigiKey</code>,
<code>DigiKey (cut tape)</code> and <code>DigiKey (cut tape / Digi-Reel)</code>, and Neewer, ROBOTIS US,
Pollen Robotics and UCTRONICS under two names each. Until 2026-09-03 this page counted the 41 names and
called them 41 distributors. The domains, in full:</p>
<p class="note"><code>{', '.join(E(d) for d in ALL_DOMAINS)}</code></p>
<p class="note">Regenerate with <code>python3 tools/gen_sourcing.py</code>. The data is
<code>spec/sourcing.json</code>; this page, <a href="RFQ.html">RFQ.html</a> and
<a href="out/release/bom.csv"><code>out/release/bom.csv</code></a> are all outputs and are never edited by
hand. <code>bom.csv</code> became an output on 2026-09-03: it had been hand-written by an earlier
workflow and had drifted on four lines &mdash; it still read CANNOT DETERMINE for the NFC reader (B14) and
the camera ribbon (B8), both of which are PASS here, and priced the ToF and the camera at vendors this
roll-up had since beaten. Two bills of materials that disagree is one too many.</p>
</section>

<footer class="foot">
  <span>Every price traces to a vendor URL and a fetch date &middot; {GEN}</span>
</footer>
</div></body></html>"""


# ------------------------------------------------------------------- RFQ ----
def rfq_line_table(supplier):
    rows = []
    for lid in supplier["lines"]:
        l = next(x for x in DATA["lines"] if x["id"] == lid)
        q = l.get("qty_per_robot")
        per = "CANNOT DETERMINE" if q is None else f"{q:g} {l.get('qty_unit') or ''}"
        tiers = "&mdash;" if q in (None, 0) else " / ".join(qty_txt(q * n) for n in ROBOT_COUNTS)
        rows.append(f"""<tr><td><code>{E(l['id'])}</code></td><td>{E(l['item'])}</td>
<td><code>{E(l['mpn'])}</code></td><td class="n">{E(per)}</td><td class="n">{tiers}</td></tr>""")
    return "\n".join(rows)


def rfq_block(s):
    l_specs = "".join(
        f'<p class="lab">{E(lid)} &mdash; specification</p><p class="note">'
        + E(next(x for x in DATA["lines"] if x["id"] == lid)["rfq_spec"]) + "</p>"
        for lid in s["lines"])
    also = "".join(f"<li>{E(a)}</li>" for a in s.get("also_ask", []))
    contacts = ", ".join(E(c) for c in (s.get("contacts") or [])) or "&mdash;"
    return f"""
<div class="rfq" id="rfq-{E(s['key'])}">
<h3>Request for quotation &mdash; {E(s['name'])}</h3>
<p class="meta">Covers lines {', '.join(E(x) for x in s['lines'])} &middot; known contact points: {contacts}
{'<br>' + E(s['address']) if s.get('address') else ''}</p>

<pre>To:      <span class="ph">[supplier contact name]</span>, {E(s['name'])}
From:    <span class="ph">[your name]</span>, <span class="ph">[your company]</span>
         <span class="ph">[email]</span> &middot; <span class="ph">[phone]</span> &middot; <span class="ph">[shipping address]</span>
Date:    <span class="ph">[date of sending]</span>
Subject: Request for quotation &mdash; Microduck bipedal robot, lines {', '.join(E(x) for x in s['lines'])}

Dear <span class="ph">[contact]</span>,

We are pricing a production run of a small bipedal robot and would like a written
quotation for the parts listed below. Quantities are given per robot and at build
volumes of 1, 100 and 1 000 robots. Please quote each quantity separately, in your
own currency, and state for every line: unit price, minimum order quantity, lead
time from receipt of order, packaging, and the incoterm your price assumes.

Where a part number below is marked as unresolved, we are asking you to tell us
which part you would supply, not to guess what we meant.
</pre>

<p class="lab">Lines and quantities</p>
<div class="tablewrap"><table class="data">
<thead><tr><th>Line</th><th>Item</th><th>Part number as we have it</th>
<th>Per robot</th><th>Order qty at 1 / 100 / 1 000 robots</th></tr></thead>
<tbody>{rfq_line_table(s)}</tbody></table></div>

{l_specs}

<p class="lab">The question that matters most on this quotation</p>
<p class="note">{E(s['ask'])}</p>

{'<p class="lab">Also please answer</p><ul class="tight">' + also + '</ul>' if also else ''}

<pre>Target lead time: <span class="ph">[state your need, e.g. 6 weeks for the pilot build]</span>
Target first delivery date: <span class="ph">[date]</span>
Quotation validity requested: 90 days.

Please also confirm whether you are the authorised channel for these parts, and
state date codes or batch provenance where the line is a semiconductor.

Kind regards,
<span class="ph">[your name]</span>
<span class="ph">[your title, company]</span>
</pre>
</div>"""


RFQ = f"""<!doctype html>
<html lang="en"><head>{HEAD}
<title>Microduck RFQ Pack</title></head>
<body><div class="wrap">
<p class="backlink"><a href="RELEASE.html">&larr; Release dossier</a> &middot; <a href="SOURCING.html">&larr; Sourcing evidence</a></p>

<header class="hero">
  <p class="eyebrow">Microduck reverse-engineering &middot; procurement</p>
  <h1>Requests for quotation, ready to send</h1>
  <p class="sub">One request per supplier, each covering the lines that supplier can actually quote,
  with the specification, the quantity tiers, and the specific question that closes an open
  <b>CANNOT DETERMINE</b> in <a href="SOURCING.html">SOURCING.html</a>. Your contact details are the
  only thing missing: everything marked <span class="ph">[like this]</span> is a placeholder for a
  person to fill in.</p>
  <div class="rev">
    <span>MD-RFQ-001 &middot; Rev {DATA['revision']}</span><span>generated {GEN}</span>
    <span>{len(DATA['rfq_suppliers'])} suppliers</span>
    <span>source: <code>spec/sourcing.json</code></span>
  </div>
</header>

<div class="warnbox">
  <h3>Nothing here has been sent</h3>
  <p>No supplier was contacted, no enquiry was submitted and no money was spent producing this
  document. These are drafts on a page. Sending them &mdash; and disclosing what the robot is, which
  several of these questions do &mdash; is a decision for a person, not for the tool that wrote them.
  Fill in the placeholders, read each one, then send.</p>
</div>

<nav class="toc">
{''.join(f'<a href="#rfq-{E(s["key"])}">{E(s["name"].split("(")[0].strip()[:26])}</a>' for s in DATA['rfq_suppliers'])}
</nav>

<section id="idx"><h2><span class="n">1</span> Which request answers which open question</h2>
<p class="lede">Each request exists because a specific number could not be read from a public page.
The right-hand column is what the reply is expected to close.</p>
<div class="tablewrap"><table class="data">
<thead><tr><th>Supplier</th><th>Lines</th><th>What the reply settles</th></tr></thead>
<tbody>
{''.join(f'<tr><td><a href="#rfq-{E(s["key"])}">{E(s["name"])}</a></td><td><code>{", ".join(E(x) for x in s["lines"])}</code></td><td>{E(clip(s["ask"], 260))}</td></tr>' for s in DATA['rfq_suppliers'])}
</tbody></table></div>
</section>

<section id="reqs"><h2><span class="n">2</span> The requests</h2>
{''.join(rfq_block(s) for s in DATA['rfq_suppliers'])}
</section>

<footer class="foot">
  <span>Drafts only &mdash; nothing sent, nothing ordered &middot; {GEN}</span>
</footer>
</div></body></html>"""


def bom_csv():
    """out/release/bom.csv, regenerated from the same data as the pages.

    It was hand-written by an earlier workflow and had drifted: on 2026-09-03 it
    still read CANNOT DETERMINE for the NFC reader (B14, PASS at $5.3997) and
    for the camera ribbon (B8, PASS at $3.9500), and priced the ToF at Pololu's
    $24.95 and the camera at $23.99 where the roll-up had found $22.70 and
    $15.90. Two BOMs that disagree on four lines is one BOM too many."""
    import csv, io
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["line_id", "section", "item", "qty_per_robot", "qty_unit", "verdict",
                "unit_price", "currency", "per_robot_cost", "price_basis",
                "vendor", "source_url", "fetched", "note"])
    native = {ln["id"]: (off, row) for ln, off, row in NATIVE}
    for l in DATA["lines"]:
        c = READ[l["id"]][1]
        q = l.get("qty_per_robot")
        qtxt = "CANNOT DETERMINE" if q is None else f"{q:g}"
        if c:
            o = next((x for x in l["offers"] if x["url"] == c.get("url")), None)
            unit = "see kit detail" if c["unit"] is None else f'{c["unit"]:.5f}'
            basis = (f'cheapest READ USD offer at the tier a 1-robot order reaches'
                     + (f' (tier {c["tier_qty"]}+)' if c.get("tier_qty") else ''))
            if c.get("ceiling"):
                basis += "; vendor publishes no tier table, so @1 is a CEILING"
            if c.get("detail"):
                basis += "; " + c["detail"]
            if c.get("caveat"):
                basis += "; " + c["caveat"]
            if l["verdict"] != "PASS":
                basis += (f'; THIS LINE IS GRADED {l["verdict"]} - the price is readable, '
                          f'the line is not graded buyable')
            row = [unit, "USD", f'{c["per_robot"]:.4f}', basis, c["vendor"],
                   (o or {}).get("url", ""), (o or {}).get("fetched", "")]
        elif l["id"] in native:
            o, r = native[l["id"]]
            row = [f'{r[1] / q:.5f}', o["currency"], f'{r[1]:.4f}',
                   "no USD price was read; the vendor's own currency at the tier a "
                   "1-robot order reaches, NOT converted (no FX rate was fetched)",
                   o["vendor"], o["url"], o.get("fetched", "")]
        elif l in REFERENCE:
            why = (l.get("excluded_from_rollup") or
                   "reference line: qty per robot is 0 - the part arrives fitted "
                   "inside another purchase and is never ordered separately")
            row = ["NOT ORDERED", "", "NOT ORDERED",
                   "deliberately outside every subtotal: " + why, "", "", ""]
        else:
            row = ["CANNOT DETERMINE", "", "CANNOT DETERMINE",
                   (l.get("verdict_why") or (l["unknowns"][0] if l.get("unknowns") else
                                             "no price was read on any page")),
                   "", "", ""]
        w.writerow([l["id"], l["category"], l["item"], qtxt, l.get("qty_unit") or "",
                    l["verdict"]] + row + [l.get("mpn_note") or l.get("mpn_status") or ""])
    p = os.path.join(REPO, "out", "release", "bom.csv")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(buf.getvalue())
    return p, len(DATA["lines"])


def main():
    ok = selfcheck()
    print(f"selfcheck: {ok} PASS lines, each with >=2 distinct read distributors and a read price")
    print(f"distinct distributors: {len(ALL_DOMAINS)} registered domains, "
          f"entered under {len(ALL_VENDOR_NAMES)} vendor name strings")
    for name, doc in (("SOURCING.html", SOURCING), ("RFQ.html", RFQ)):
        p = os.path.join(REPO, name)
        open(p, "w").write(doc)
        print(f"wrote {p}  {len(doc):,} bytes")
    print(f"readable USD subtotal/robot: @1 ${SUBTOTAL[1]:,.4f}  "
          f"@100 ${SUBTOTAL[100]:,.4f}  @1000 ${SUBTOTAL[1000]:,.4f}")
    print(f"  of which graded PASS  @1 ${SUB_OK[1]:,.4f}  @100 ${SUB_OK[100]:,.4f}  @1000 ${SUB_OK[1000]:,.4f}")
    print(f"  of which graded FAIL/CD @1 ${SUB_QUAL[1]:,.4f}  ({QUAL_PCT:.2f} % of the readable total)")
    print(f"priced lines {len(PRICED)}  native-currency-only {len(NATIVE)}  "
          f"no price {len(UNKNOWN)}  reference/excluded {len(REFERENCE)}")
    p, n = bom_csv()
    print(f"wrote {p}  {n} lines")


if __name__ == "__main__":
    main()
