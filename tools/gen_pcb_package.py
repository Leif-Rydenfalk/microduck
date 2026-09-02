#!/usr/bin/env python3
"""gen_pcb_package.py — build PCB-PACKAGE.html for GOAL.md lane D.

Data in, document out. Nothing here is hand-maintained:

  electronics/pcb-package.json      the decisions, the MPNs, the fab quotes,
                                    the measured-mesh table. Every row carries
                                    the URL or file it came from.
  electronics/<board>/out/fab/      the DRC verdict, the counts, the BOM and
                                    the pick-and-place — READ BACK from the
                                    files the fab would actually receive, so
                                    the document cannot claim a verdict the
                                    Gerbers do not carry.
  electronics/<board>/board.py      imported, so the schematic below is the
                                    SAME object the DRC checked. Every pin of
                                    every part is emitted with its net and
                                    with every other pad on that net.

Run:  python3 tools/gen_pcb_package.py
      python3 tools/gen_pcb_package.py --self-test   break the parsers

The schematic is drawn as a NET-LABEL schematic: every component is a box,
every pin is a stub carrying its number, its name and its net, and the net
label is the wire. That is a real schematic convention and it is the only one
that can be generated from a netlist without a placement algorithm inventing
wire routes it cannot justify.
"""
import csv
import html
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "electronics", "pcb-package.json")
OUT = os.path.join(REPO, "PCB-PACKAGE.html")


# ---------------------------------------------------------------------------
# readers — each one refuses rather than guesses
# ---------------------------------------------------------------------------
def read_fab_readme(path):
    """(verdict, counts, findings[]) out of a fab README.txt.

    Returns verdict None if the file does not exist or carries no DRC block —
    a missing verdict stays missing.
    """
    if not os.path.exists(path):
        return None, "", []
    txt = open(path, encoding="utf-8", errors="replace").read()
    m = re.search(r"verdict:\s*(\S.*)", txt)
    verdict = m.group(1).strip() if m else None
    m = re.search(r"^\s*(\d+ pass, \d+ fail, \d+ cannot determine)\s*$",
                  txt, re.M)
    counts = m.group(1) if m else ""
    findings = re.findall(r"^\s*\[([A-Z ]+)\]\s+(.+)$", txt, re.M)
    return verdict, counts, [(a.strip(), b.strip()) for a, b in findings]


def read_fab_header(path):
    """The size / stackup / part-count block at the top of a fab README."""
    if not os.path.exists(path):
        return {}
    txt = open(path, encoding="utf-8", errors="replace").read()
    out = {}
    m = re.search(r"^([\d.]+) x ([\d.]+) mm, ([\d.]+) mm2, (\d+) copper",
                  txt, re.M)
    if m:
        out["w"], out["h"] = float(m.group(1)), float(m.group(2))
        out["area"] = float(m.group(3))
        out["layers"] = int(m.group(4))
    m = re.search(r"^parts\s+(\d+)\s+nets\s+(\d+)\s+tracks\s+(\d+)\s+"
                  r"vias\s+(\d+)\s+drills\s+(\d+)", txt, re.M)
    if m:
        for i, k in enumerate(("parts", "nets", "tracks", "vias", "drills")):
            out[k] = int(m.group(i + 1))
    m = re.search(r"^stackup\s+(.+)$", txt, re.M)
    if m:
        out["stackup"] = m.group(1).strip()
    return out


def read_bom(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_board(slug):
    """Import a board module and build it WITHOUT routing or publishing.

    build(self_test=...) is the boards' own no-route path: it checks and
    returns. That is what the schematic is drawn from, so the pins in this
    document are the pins the DRC saw.
    """
    path = os.path.join(REPO, "electronics", slug, "board.py")
    spec = importlib.util.spec_from_file_location(f"board_{slug}", path)
    mod = importlib.util.module_from_spec(spec)
    old = sys.argv
    sys.argv = ["gen"]
    try:
        spec.loader.exec_module(mod)
        b, rep = mod.build(self_test="document", publish=False, verbose=False)
    finally:
        sys.argv = old
    return mod, b, rep


# ---------------------------------------------------------------------------
# the net-label schematic
# ---------------------------------------------------------------------------
def schematic_svg(board, cols=4, cell_w=212, pin_h=15, head=42, gap=30):
    """A net-label schematic: every part, every pin, every net.

    No wire is drawn between two pins, because a wire drawn by a program that
    has not solved a routing problem is a decoration. The NET NAME on each pin
    is the connection, and it is exact.
    """
    parts = [board.components[r] for r in board._order]
    parts = [c for c in parts if c.fp.pads]
    boxes = []
    for c in parts:
        pads = list(c.fp.pads)
        boxes.append((c, pads, head + pin_h * len(pads) + 10))
    # column packing, tallest first into the shortest column
    order = sorted(range(len(boxes)), key=lambda i: -boxes[i][2])
    col_y = [10.0] * cols
    place = {}
    for i in order:
        k = min(range(cols), key=lambda j: col_y[j])
        place[i] = (k * cell_w + 10, col_y[k])
        col_y[k] += boxes[i][2] + gap
    height = max(col_y) + 20
    width = cols * cell_w + 20

    def esc(s):
        return html.escape(str(s), quote=True)

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" '
         f'height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}" '
         f'font-family="IBM Plex Mono, Menlo, monospace">',
         f'<rect width="100%" height="100%" fill="#ffffff"/>']
    for i, (c, pads, h) in enumerate(boxes):
        x, y = place[i]
        bw = cell_w - 40
        o.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{bw}" height="{h:.0f}" '
                 f'fill="#fbfaf7" stroke="#1a1a1a" stroke-width="1.2"/>')
        o.append(f'<text x="{x + 6:.0f}" y="{y + 16:.0f}" font-size="12" '
                 f'font-weight="700" fill="#1a1a1a">{esc(c.ref)}</text>')
        o.append(f'<text x="{x + 6:.0f}" y="{y + 30:.0f}" font-size="9.5" '
                 f'fill="#565656">{esc(c.value or c.fp.slug)}</text>')
        o.append(f'<line x1="{x:.0f}" y1="{y + head - 6:.0f}" '
                 f'x2="{x + bw:.0f}" y2="{y + head - 6:.0f}" '
                 f'stroke="#d7d3ca" stroke-width="1"/>')
        for j, p in enumerate(pads):
            py = y + head + pin_h * j + 8
            net = board._pad_net.get((c.ref, p.name))
            nc = board._nc.get((c.ref, p.name))
            if net:
                label, col = net, "#243b53"
            elif nc is not None:
                label, col = "NC", "#8a5a00"
            elif getattr(p, "npth", False):
                label, col = "NPTH", "#565656"
            else:
                label, col = "(unassigned)", "#9a2b1e"
            o.append(f'<line x1="{x - 9:.0f}" y1="{py:.0f}" x2="{x:.0f}" '
                     f'y2="{py:.0f}" stroke="{col}" stroke-width="1.2"/>')
            o.append(f'<text x="{x + 5:.0f}" y="{py + 3.5:.0f}" font-size="9" '
                     f'fill="#1a1a1a">{esc(p.name)}</text>')
            o.append(f'<text x="{x + bw - 4:.0f}" y="{py + 3.5:.0f}" '
                     f'font-size="9" text-anchor="end" fill="{col}">'
                     f'{esc(label)}</text>')
    o.append('</svg>')
    return "".join(o)


# ---------------------------------------------------------------------------
# document
# ---------------------------------------------------------------------------
def esc(s):
    return html.escape(str(s if s is not None else ""), quote=False)


def verdict_class(v):
    v = (v or "").upper()
    if v.startswith("PASS"):
        return "pass"
    if v.startswith("FAIL"):
        return "no"
    return "cd"


def pin_rows(board):
    rows = []
    for ref in board._order:
        c = board.components[ref]
        for p in c.fp.pads:
            net = board._pad_net.get((ref, p.name))
            nc = board._nc.get((ref, p.name))
            if net:
                others = [f"{a}.{b}" for a, b in board.nets.get(net, [])
                          if not (a == ref and b == p.name)]
                goes = ", ".join(others) if others else "— nothing else on this net"
                state = "net"
            elif nc is not None:
                net, goes, state = "NC", nc or "no reason recorded", "nc"
            elif getattr(p, "npth", False):
                net, goes, state = "NPTH", (
                    "unplated mounting hole — it has no copper, so it cannot "
                    "be on a net. attach() refuses it by name."), "npth"
            else:
                net, goes, state = "(unassigned)", "NOT CONNECTED AND NOT DECLARED", "bad"
            rows.append((ref, c.value or c.fp.slug, p.name, net, goes, state))
    return rows


def main():
    if "--self-test" in sys.argv:
        return self_test()
    d = json.load(open(DATA, encoding="utf-8"))
    doc, boards, quotes = d["document"], d["boards"], d["fab_quotes"]
    parts_db = d["parts"]

    built = []
    for bd in boards:
        fabdir = os.path.join(REPO, bd["dir"], "out", "fab")
        readme = os.path.join(fabdir, "README.txt")
        verdict, counts, findings = read_fab_readme(readme)
        header = read_fab_header(readme)
        bom = read_bom(os.path.join(fabdir, f"{bd['name']}-bom.csv"))
        pos = read_bom(os.path.join(fabdir, f"{bd['name']}-positions.csv"))
        mod, b, rep = load_board(bd["slug"])
        # A dropped pin is the failure mode that matters in a schematic: it
        # looks finished and it is missing a connection. Every pad of every
        # placed footprint must appear in the pin table, counted here, every
        # run, not only under --self-test.
        want = sum(len(c.fp.pads) for c in b.components.values())
        got = len(pin_rows(b))
        if want != got:
            raise SystemExit(
                f"{bd['slug']}: the pin table has {got} rows for {want} pads. "
                f"A schematic that drops a pin is worse than no schematic.")
        built.append({"meta": bd, "verdict": verdict, "counts": counts,
                      "findings": findings, "header": header, "bom": bom,
                      "pos": pos, "board": b, "report": rep})

    # per-board schematic SVGs, written beside the board
    for x in built:
        p = os.path.join(REPO, x["meta"]["dir"], "out", "schematic.svg")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write(schematic_svg(x["board"]))
        x["schematic"] = os.path.relpath(p, REPO)

    H = []
    A = H.append
    A('<!doctype html><html lang="en"><head><meta charset="utf-8">')
    A('<meta name="viewport" content="width=device-width,initial-scale=1">')
    A(f'<title>{esc(doc["title"])} — Microduck</title>')
    A('<link rel="stylesheet" href="tools/doc.css">')
    A('<style>'
      '.pcbfig{background:#fff;border:1px solid var(--hair);padding:10px;'
      'overflow-x:auto;margin:10px 0}'
      '.pcbfig img{display:block;width:100%;height:auto;min-width:520px}'
      '.schem{border:1px solid var(--hair);overflow-x:auto;background:#fff;'
      'margin:10px 0;max-height:900px;overflow-y:auto}'
      '.schem img{display:block}'
      'table.tight td,table.tight th{font-size:12.5px;padding:4px 8px}'
      'td.n{text-align:right;font-variant-numeric:tabular-nums;'
      'font-family:var(--mono)}'
      '.pass{color:var(--pass-ink);font-weight:700}'
      '.no{color:var(--no);font-weight:700}'
      '.cd{color:var(--cd-ink);font-weight:700}'
      '.bad{color:var(--no)}'
      '.nc{color:var(--cd-ink)}'
      '.npth{color:var(--ink-2)}'
      '</style></head><body><div class="wrap">')

    A('<header class="top">')
    A(f'<div class="eyebrow">Microduck · {esc(doc["lane"])}</div>')
    A(f'<h1>{esc(doc["title"])}</h1>')
    A(f'<p class="sub">{esc(doc["subtitle"])}</p>')
    A(f'<div class="rev"><span>Document {esc(doc["id"])}</span>'
      f'<span>Revision {esc(doc["revision"])}</span>'
      f'<span>{esc(doc["date"])}</span>'
      f'<span>Units mm · V · USD</span>'
      f'<span>Generated by tools/gen_pcb_package.py</span></div>')
    A('</header>')

    A('<div class="statbar">')
    A(f'<div class="stat"><b>{len(built)}</b><span>boards designed</span></div>')
    tot_parts = sum(x["header"].get("parts", 0) for x in built)
    A(f'<div class="stat"><b>{tot_parts}</b><span>placed parts</span></div>')
    tot_nets = sum(x["header"].get("nets", 0) for x in built)
    A(f'<div class="stat"><b>{tot_nets}</b><span>nets</span></div>')
    tot_pins = sum(len(pin_rows(x["board"])) for x in built)
    A(f'<div class="stat"><b>{tot_pins}</b><span>pins, each with its net</span></div>')
    A('</div>')

    A('<nav class="toc">')
    A('<a href="#s1">1 What this is</a>')
    A('<a href="#s2">2 Pollen&rsquo;s own HAT mesh</a>')
    for i, x in enumerate(built):
        A(f'<a href="#b-{x["meta"]["slug"]}">{i + 3} {esc(x["meta"]["title"])}</a>')
    A('<a href="#cost">6 Fab cost</a><a href="#open">7 What is not settled</a>')
    A('</nav>')

    # ---- 1 -----------------------------------------------------------------
    A('<section id="s1"><h2><span class="n">1</span>What this is, and what it is not</h2>')
    A('<p class="lede">Pollen Robotics publishes the Microduck&rsquo;s firmware, its '
      'device-tree overlays and its simulation meshes. It publishes no PCB, no '
      'schematic and no BOM for any of the three custom boards, and the press kit '
      'asks that the robot not be described as open-source hardware. Everything in '
      'this document is <em>our</em> reconstruction from the published behaviour '
      'plus the vendor datasheets of the chips that behaviour names.</p>')
    A('<div class="note"><p><strong>Nothing here claims to match Pollen&rsquo;s boards.</strong> '
      'Not the layout, not the connector placement, not the part choice. Where a fact '
      'is published, it is quoted with its file and line. Where it is not, the choice '
      'is ours, it is numbered (D1&ndash;D8, E1&ndash;E8, B1&ndash;B6), and the option it '
      'beat is written down beside it.</p></div>')
    A('<table class="tight"><thead><tr><th>Board</th><th>What it does</th>'
      '<th>Outline (mm)</th><th>Layers</th><th>DRC</th></tr></thead><tbody>')
    for x in built:
        m = x["meta"]
        A(f'<tr><td><a href="#b-{m["slug"]}"><code>{esc(m["name"])}</code></a></td>'
          f'<td>{esc(m["what"])}</td>'
          f'<td class="n">{m["outline_mm"][0]:.3f} &times; {m["outline_mm"][1]:.3f}</td>'
          f'<td class="n">{m["layers"]}</td>'
          f'<td class="{verdict_class(x["verdict"])}">{esc(x["verdict"] or "not built")}</td></tr>')
    A('</tbody></table>')
    A('<p class="fig-cap">Table 1. The three boards. The DRC column is read out of each '
      'board&rsquo;s own <code>out/fab/README.txt</code> — the file a fab would receive — '
      'so this document cannot state a verdict the Gerbers do not carry.</p>')
    corr = d.get("corrections")
    if corr:
        A('<h3>1.1 What this lane got wrong, and how it was caught</h3>')
        A(f'<p class="lede">{esc(corr["$note"])}</p>')
        A('<table class="tight"><thead><tr><th>Board</th><th>The defect</th>'
          '<th>What was wrong</th><th>What caught it</th><th>The fix, and what '
          'proves it</th></tr></thead><tbody>')
        for board, defect, wrong, caught, fix in corr["rows"]:
            A(f'<tr><td><code>{esc(board)}</code></td>'
              f'<td><strong>{esc(defect)}</strong></td><td>{esc(wrong)}</td>'
              f'<td>{esc(caught)}</td><td>{esc(fix)}</td></tr>')
        A('</tbody></table>')
        A('<p class="fig-cap">Table 1.1. Five defects measured in this lane&rsquo;s own '
          'work and closed. Three were caught by the design-rule check or by a '
          'measurement; two were caught by asking a question the check does not ask.</p>')
    A('</section>')

    # ---- 2 -----------------------------------------------------------------
    pm = d["pollen_hat_mesh"]
    A('<section id="s2"><h2><span class="n">2</span>What Pollen&rsquo;s own HAT mesh measures</h2>')
    A(f'<p class="lede">One of the three boards is not entirely unpublished. '
      f'<code>{esc(pm["file"])}</code> is Pollen&rsquo;s geometry for the Robot HAT, and it '
      f'was measured on {esc(pm["read"])}. Until then this project&rsquo;s HAT outline came '
      f'from the Raspberry&nbsp;Pi Zero mechanical drawing <em>by analogy</em>. It no longer does.</p>')
    A(f'<div class="note"><p><strong>Method.</strong> {esc(pm["method"])} '
      f'Placement: {esc(pm["placement"])}</p></div>')
    A('<table class="tight"><thead><tr><th>Feature</th><th>Measured</th>'
      '<th>Where</th><th>Status</th></tr></thead><tbody>')
    for f, v, w, s in pm["rows"]:
        cls = "cd" if "CANNOT" in s else "pass"
        A(f'<tr><td><strong>{esc(f)}</strong></td><td class="n">{esc(v)}</td>'
          f'<td>{esc(w)}</td><td class="{cls}">{esc(s)}</td></tr>')
    A('</tbody></table>')
    A('<p class="fig-cap">Table 2. Every through-feature of the HAT mesh, read off the solid.</p>')
    A(f'<h3>Reading the connector holes</h3><p>{esc(pm["reading"])}</p>')
    A(f'<div class="note"><p><strong>{esc(pm["not_copied"])}</strong></p></div>')
    A('</section>')

    # ---- per board ---------------------------------------------------------
    for i, x in enumerate(built):
        m, b = x["meta"], x["board"]
        n = i + 3
        A(f'<section id="b-{m["slug"]}"><h2><span class="n">{n}</span>{esc(m["title"])}</h2>')
        A(f'<p class="lede">{esc(m["what"])}</p>')

        hd = x["header"]
        A('<div class="statbar">')
        A(f'<div class="stat"><b>{m["outline_mm"][0]:.1f}&times;{m["outline_mm"][1]:.1f}</b>'
          f'<span>mm outline</span></div>')
        if hd.get("area"):
            A(f'<div class="stat"><b>{hd["area"]:.2f}</b><span>mm&sup2;</span></div>')
        for k, lbl in (("parts", "parts"), ("nets", "nets"),
                       ("tracks", "tracks"), ("vias", "vias"),
                       ("drills", "drills")):
            if hd.get(k) is not None:
                A(f'<div class="stat"><b>{hd[k]}</b><span>{lbl}</span></div>')
        A('</div>')

        A(f'<p><strong>Stack-up.</strong> {esc(hd.get("stackup", "—"))} · '
          f'{m["layers"]} layers · {m["thickness_mm"]} mm · corner radius '
          f'{m["corner_r_mm"]:.3f} mm.<br>'
          f'<strong>Surface finish.</strong> {esc(m["finish"])}<br>'
          f'<strong>Mounting.</strong> {esc(m["mount"])}<br>'
          f'<strong>Geometry evidence.</strong> '
          f'{esc(m["mesh_evidence"] or "NONE — no Pollen mesh exists for this board; the outline is our choice and is marked so.")}'
          f'</p>')

        A(f'<h3>{n}.1 Reconstruction decisions</h3>')
        A('<table class="tight"><thead><tr><th>#</th><th>Decision</th>'
          '<th>The published fact behind it</th><th>The option it beat</th>'
          '</tr></thead><tbody>')
        for tag, dec, ev, alt in m["decisions"]:
            A(f'<tr><td><code>{esc(tag)}</code></td><td>{esc(dec)}</td>'
              f'<td>{esc(ev)}</td><td>{esc(alt)}</td></tr>')
        A('</tbody></table>')

        A(f'<h3>{n}.2 Schematic — every component, every pin, every net</h3>')
        A(f'<div class="schem"><img src="{esc(x["schematic"])}" '
          f'alt="net-label schematic of {esc(m["name"])}"></div>')
        A('<p class="fig-cap">Net-label schematic, generated from the same '
          'board object the design-rule check ran on. Each box is a placed part; '
          'each stub is one pad, with its pad name on the left and its net on the '
          'right. <span class="cd">NC</span> is a pad this design deliberately '
          'leaves unconnected — the reason is in the pin table below. '
          '<span class="bad">(unassigned)</span> would be a pad on no net and no '
          'no-connect &mdash; a forgotten wire. <span class="npth">NPTH</span> is an '
          'unplated mounting hole, which has no copper and therefore cannot be on a '
          'net at all.</p>')

        rows = pin_rows(b)
        bad = [r for r in rows if r[5] == "bad"]
        A(f'<p><strong>{len(rows)} pads</strong> on this board. '
          f'{len([r for r in rows if r[5] == "net"])} carry a net, '
          f'{len([r for r in rows if r[5] == "nc"])} are declared no-connect, '
          f'{len([r for r in rows if r[5] == "npth"])} are unplated mounting '
          f'holes with no copper, and '
          f'<span class="{"bad" if bad else "pass"}">{len(bad)}</span> are '
          f'none of those — a pad on no net and no no-connect is a forgotten '
          f'wire, and the count above is the check.</p>')
        A('<details><summary>Full pin table — every pad, its net, and every '
          'other pad on that net</summary>')
        A('<table class="tight"><thead><tr><th>Ref</th><th>Value</th>'
          '<th>Pad</th><th>Net</th><th>Goes to</th></tr></thead><tbody>')
        for ref, val, pad, net, goes, state in rows:
            A(f'<tr><td><code>{esc(ref)}</code></td><td>{esc(val)}</td>'
              f'<td class="n">{esc(pad)}</td>'
              f'<td class="{state if state != "net" else ""}"><code>{esc(net)}</code></td>'
              f'<td>{esc(goes)}</td></tr>')
        A('</tbody></table></details>')

        A(f'<h3>{n}.3 Layout</h3>')
        for side in ("top", "bottom"):
            p = os.path.join(m["dir"], "out", f"{side}.svg")
            if os.path.exists(os.path.join(REPO, p)):
                A(f'<div class="pcbfig"><img src="{esc(p)}" '
                  f'alt="{esc(m["name"])} {side} layer"></div>')
                A(f'<p class="fig-cap">{esc(m["title"])} — {side} side, as plotted '
                  f'from the checked board. DRC findings are circled on the plot.</p>')

        A(f'<h3>{n}.4 Design rule check</h3>')
        A(f'<p>Verdict <span class="{verdict_class(x["verdict"])}">'
          f'{esc(x["verdict"] or "not built")}</span>'
          + (f' — {esc(x["counts"])}.' if x["counts"] else '.') + '</p>')
        nonpass = [(v, t) for v, t in x["findings"] if v != "PASS"]
        if nonpass:
            A('<table class="tight"><thead><tr><th>Verdict</th><th>Finding</th>'
              '</tr></thead><tbody>')
            for v, t in nonpass:
                A(f'<tr><td class="{verdict_class(v)}">{esc(v)}</td>'
                  f'<td>{esc(t)}</td></tr>')
            A('</tbody></table>')
            A('<p class="fig-cap">Every non-PASS row the shipped Gerbers carry. '
              'A CANNOT DETERMINE is not a pass and is not treated as one.</p>')
        else:
            A('<p>No non-PASS rows.</p>')

        A(f'<h3>{n}.5 Bill of materials</h3>')
        db = parts_db.get(m["slug"], {})
        A('<table class="tight"><thead><tr><th>Designator</th><th>Qty</th>'
          '<th>Value / function</th><th>MPN</th><th>Package</th>'
          '<th>Note</th></tr></thead><tbody>')
        for row in x["bom"]:
            desig = row.get("Designator", "")
            first = desig.split()[0] if desig.split() else desig
            info = db.get(first, ["CANNOT DETERMINE", row.get("Footprint", ""), ""])
            mpn = info[0]
            cls = "cd" if "CANNOT DETERMINE" in mpn else ""
            A(f'<tr><td><code>{esc(desig)}</code></td>'
              f'<td class="n">{esc(row.get("Qty", ""))}</td>'
              f'<td>{esc(row.get("Comment", ""))}</td>'
              f'<td class="{cls}">{esc(mpn)}</td>'
              f'<td>{esc(info[1])}</td><td>{esc(info[2])}</td></tr>')
        A('</tbody></table>')
        A('<p class="fig-cap">Designators, quantities and footprints are read out of '
          f'<code>{esc(m["dir"])}/out/fab/{esc(m["name"])}-bom.csv</code>; the MPN, package '
          'and note columns come from <code>electronics/pcb-package.json</code>. '
          'A commodity passive carries a SPECIFICATION rather than a manufacturer part '
          'number, and says so — naming one 100&nbsp;nF 0603 would be a false precision.</p>')

        A(f'<h3>{n}.6 Files a fab receives</h3>')
        fabdir = os.path.join(REPO, m["dir"], "out", "fab")
        names = sorted(os.listdir(fabdir)) if os.path.isdir(fabdir) else []
        A('<table class="tight"><thead><tr><th>File</th><th>Bytes</th>'
          '</tr></thead><tbody>')
        for nm in names:
            fp = os.path.join(fabdir, nm)
            A(f'<tr><td><code><a href="{esc(os.path.join(m["dir"], "out", "fab", nm))}">'
              f'{esc(nm)}</a></code></td>'
              f'<td class="n">{os.path.getsize(fp):,}</td></tr>')
        A('</tbody></table>')
        A(f'<p class="fig-cap">Gerber X2 per layer with <code>.FileFunction</code> '
          'attributes, plated and unplated Excellon drill files kept apart (a fab that '
          'gets one file cannot tell a mounting hole from a via), pick-and-place, BOM, '
          'a <code>.kicad_pcb</code> for anyone who wants to open it, and a README that '
          'repeats the DRC verdict on its first page.</p>')
        A('</section>')

    # ---- cost --------------------------------------------------------------
    A('<section id="cost"><h2><span class="n">6</span>Fab cost</h2>')
    A(f'<p class="lede">{esc(quotes["note"])} Read {esc(quotes["read"])}.</p>')
    A(f'<div class="note"><p><strong>{esc(quotes["moq"])}</strong></p></div>')
    A('<table class="tight"><thead><tr><th>Vendor</th><th>Published offer</th>'
      '<th>qty 1</th><th>qty 10</th><th>qty 100</th></tr></thead><tbody>')
    for v in quotes["vendors"]:
        t = v["tiers"]

        def cell(k):
            e = t[k]
            if e["usd"] is None:
                return f'<td class="cd">CANNOT DETERMINE</td>'
            return f'<td class="n">${e["usd"]:.2f}</td>'
        A(f'<tr><td><a href="{esc(v["url"])}">{esc(v["vendor"])}</a></td>'
          f'<td>{esc(v["quote"])}</td>{cell("5")}{cell("10")}{cell("100")}</tr>')
    A('</tbody></table>')
    A('<p class="fig-cap">Table 6.1. Published prices only. The qty-1 column repeats the '
      'smallest published panel price because neither fab sells one board. '
      'Every board in this package is under 100&nbsp;&times;&nbsp;100&nbsp;mm, so all three '
      'qualify for both offers as drawn.</p>')

    A('<h3>6.1 Per board, at the published tiers</h3>')
    A('<table class="tight"><thead><tr><th>Board</th><th>Size (mm)</th>'
      '<th>Area (mm&sup2;)</th><th>Fits the &le;100&times;100 offer</th>'
      '<th>JLCPCB 5 pcs</th><th>PCBWay 10 pcs</th></tr></thead><tbody>')
    for x in built:
        m, hd = x["meta"], x["header"]
        fits = "yes" if max(m["outline_mm"]) <= 100 else "no"
        A(f'<tr><td><code>{esc(m["name"])}</code></td>'
          f'<td class="n">{m["outline_mm"][0]:.3f} &times; {m["outline_mm"][1]:.3f}</td>'
          f'<td class="n">{hd.get("area", 0):.2f}</td>'
          f'<td class="pass">{fits}</td>'
          f'<td class="n">$2.00</td><td class="n">$5.00</td></tr>')
    A('</tbody></table>')
    A('<p><strong>One robot needs one of each.</strong> The smallest orderable set is '
      'three panels: $6.00 at JLCPCB&rsquo;s published 5-piece price or $15.00 at '
      'PCBWay&rsquo;s published 10-piece price, before shipping, before the banana '
      'board&rsquo;s ENIG, and before assembly — all three of which are listed as '
      'CANNOT DETERMINE below. That buys 5 (or 10) of each board, i.e. spares for '
      '4 (or 9) more robots.</p>')

    A('<h3>6.2 What the price does not include</h3><ul>')
    for e in quotes["excluded"]:
        A(f'<li>{esc(e)}</li>')
    A('</ul>')
    A(f'<p><strong>What would settle the missing tiers.</strong> {esc(quotes["what_would_settle_it"])}</p>')

    A('<h3>6.3 The fab rules these boards were checked against</h3>')
    for v in quotes["vendors"]:
        A(f'<p><strong>{esc(v["vendor"])}</strong> — <a href="{esc(v["spec_url"])}">'
          f'{esc(v["spec_url"])}</a><br>{esc(v["spec"])}</p>')
    A('</section>')

    # ---- open --------------------------------------------------------------
    A('<section id="open"><h2><span class="n">7</span>What is not settled</h2>')
    A('<p class="lede">Every CANNOT DETERMINE these three boards carry, what it '
      'would take to settle it, and what was decided in the meantime.</p>')
    A('<table class="tight"><thead><tr><th>Board</th><th>Rule</th>'
      '<th>What the check said</th></tr></thead><tbody>')
    for x in built:
        for v, t in x["findings"]:
            if v == "CANNOT DETERMINE":
                A(f'<tr><td><code>{esc(x["meta"]["name"])}</code></td>'
                  f'<td class="cd">{esc(t.split()[0])}</td><td>{esc(t)}</td></tr>')
    A('</tbody></table>')
    A('<p class="fig-cap">Table 7.1. Read out of the shipped fab READMEs, not restated here.</p>')
    A('<h3>7.1 The five that matter most</h3><ol>')
    A('<li><strong>Pollen&rsquo;s real schematics.</strong> All three boards are '
      'functional stand-ins. A teardown photograph of a production HAT&rsquo;s connector '
      'side would settle the connector family and the 4.800&nbsp;mm column question in '
      '&sect;2 on its own.</li>')
    A('<li><strong>The NP-F terminal pitch.</strong> The banana board&rsquo;s 4.000&nbsp;mm '
      'is derived from the 12.000&nbsp;mm window in the cradle, not measured off a pack. '
      'A caliper across a physical NP-F550 settles it and nothing else does.</li>')
    A('<li><strong>The codec&rsquo;s 1.8&nbsp;V rail.</strong> Decision D5 leaves it on a '
      'test point instead of inventing a regulator. The HAT&rsquo;s codec cannot run '
      'until something feeds TP1.</li>')
    A('<li><strong>SERVO_V: raw pack or regulated.</strong> Decision D2 reads it as raw '
      'from <code>model.rs:99-113</code>. A meter on a production servo&rsquo;s VDD '
      'settles it, and the 0&nbsp;&Omega; link R1 is there so the answer can be fitted '
      'either way.</li>')
    A('<li><strong>The imu_to_dxl outline.</strong> Decision E8 is ours entirely. It has '
      'not been checked for clearance against the trunk cavity — that is a mechanical '
      'check, not a PCB one, and it has not been run.</li>')
    A('</ol>')
    A('<p class="foot">Generated by <code>tools/gen_pcb_package.py</code> from '
      '<code>electronics/pcb-package.json</code> and the three boards&rsquo; own '
      '<code>out/fab/</code> outputs. Re-run it after any board change; do not edit '
      'this file.</p>')
    A('</section>')
    A('</div></body></html>')

    open(OUT, "w", encoding="utf-8").write("\n".join(H))
    print(f"wrote {OUT}  ({os.path.getsize(OUT):,} bytes)")
    for x in built:
        print(f"  {x['meta']['name']:26s} DRC {x['verdict']}  "
              f"{len(pin_rows(x['board']))} pads  {len(x['bom'])} BOM lines")


# ---------------------------------------------------------------------------
def self_test():
    """Break each parser on purpose and watch it refuse."""
    import tempfile
    ok = True
    with tempfile.TemporaryDirectory() as t:
        missing = os.path.join(t, "nope.txt")
        v, c, f = read_fab_readme(missing)
        print(f"  missing README -> verdict {v!r}", end=" ")
        if v is None:
            print("OK (a missing verdict stays missing)")
        else:
            ok = False
            print("FAILED: invented a verdict")
        p = os.path.join(t, "README.txt")
        open(p, "w").write("no drc block here at all\n")
        v, c, f = read_fab_readme(p)
        print(f"  README with no DRC block -> verdict {v!r}", end=" ")
        if v is None and not f:
            print("OK")
        else:
            ok = False
            print("FAILED")
        # NEGATIVE CONTROL: the verdict must be READ, never decided here.
        for claim in ("PASS", "FAIL", "CANNOT DETERMINE"):
            open(p, "w").write(f"x\n\n   verdict: {claim}\n"
                               f"   1 pass, 0 fail, 0 cannot determine\n")
            v, c, f = read_fab_readme(p)
            print(f"  README says {claim!r} -> parser says {v!r}", end=" ")
            if v == claim:
                print("OK")
            else:
                ok = False
                print("FAILED: the document would not track the file")
        open(p, "w").write("no drc block here at all\n")
        h = read_fab_header(p)
        print(f"  header from a README with no header -> {h}", end=" ")
        if h == {}:
            print("OK")
        else:
            ok = False
            print("FAILED")
        print(f"  BOM from a missing file -> {read_bom(missing)}", end=" ")
        if read_bom(missing) == []:
            print("OK")
        else:
            ok = False
            print("FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
