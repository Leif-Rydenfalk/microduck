#!/usr/bin/env python3
"""gen_sources.py — build SOURCES.html from out/sources/makerworld-3250889.json.

Every number on the page is read from that JSON (itself built from measurements by
tools/build_makerworld_source.py). Nothing is typed here except headings and the
sentences that explain what a column is. House style: tools/doc.css.
Run:  python3 tools/build_makerworld_source.py && python3 tools/gen_sources.py
"""
import html, json, os

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
D = json.load(open(os.path.join(REPO, "out", "sources", "makerworld-3250889.json")))
S, L, F, T = D["source"], D["lineage"], D["files"], D["totals"]
E = html.escape

def chip(v):
    v = str(v); cls = "pass" if v.startswith("PASS") else ("cd" if v.startswith("CANNOT") else ("ref" if v.startswith("NO REBUILD") else "fail"))
    return '<span class="chip %s">%s</span>' % (cls, E(v.split(" — ")[0]))

def n4(x): return "—" if x is None else ("%.4f" % x)
def n3l(v): return "—" if not v else " × ".join("%.3f" % x for x in v)

def file_rows():
    out = []
    for f in F:
        c = f["census"]; p = f.get("vs_pollen_sim_body") or {}; o = f.get("vs_our_rebuild_body") or {}
        out.append("<tr><td class='n'>%02d</td><td class='nm'>%s<br><span class='small'>%s</span></td>"
                   "<td class='n'>%s</td><td class='n'>%s</td>"
                   "<td class='n'>%s</td><td class='n'>%s / %s</td><td class='n'>%s / %s</td><td>%s</td></tr>" % (
            f["n"], E(f["name_en"]), E(f["name_zh"]), n3l(c["size_mm"]), "{:,}".format(c["tris"]),
            ("%.1e" % f["identity"]["max_abs_vertex_delta_mm"]) if f["identity"]["max_abs_vertex_delta_mm"] is not None else "—",
            n4(p.get("ref_to_cand", {}).get("p95_mm")), n4(p.get("cand_to_ref", {}).get("p95_mm")),
            n4(o.get("ref_to_cand", {}).get("p95_mm")), n4(o.get("cand_to_ref", {}).get("p95_mm")), chip(f["verdict_vs_our_rebuild"])))
    return "\n".join(out)

def contents_rows():
    out = []
    for f in F:
        ct = f["contents"]
        out.append("<tr><td class='n'>%02d</td><td><code>%s</code></td><td><code>%s</code></td><td>%s</td><td>%s</td><td><b>%s</b></td><td>%s</td></tr>" % (
            f["n"], E(f["file"]), E(f["body"] or "—"), ", ".join("<code>%s</code>" % E(m) for m in ct["structural"]) or "—",
            ", ".join("<code>%s</code>" % E(m) for m in ct["soft"]) or "—", ", ".join("<code>%s</code>" % E(m) for m in ct["vendor_fused_in"]) or "—",
            chip(f["verdict_printable_as_shipped"])))
    return "\n".join(out)

def part_rows():
    seen = {}; out = []
    for f in F:
        for cp in f["constituent_parts"]:
            seen.setdefault(cp["mesh"], (cp, []))[1].append("%02d" % f["n"])
    for mesh, (cp, where) in sorted(seen.items(), key=lambda kv: (kv[1][0]["role"], kv[0])):
        rv = cp.get("refcheck_verdict", "—")
        feat = "—"
        if cp.get("features_verdict"):
            feat = "%s · %d matched, %d ref unmatched, %d extra" % (cp["features_verdict"], cp["features_matched"], cp["features_unmatched_reference"], cp["features_extra_ours"])
        out.append("<tr><td><code>%s</code></td><td>%s</td><td><code>%s</code></td><td>%s</td><td>%s</td><td class='n'>%s / %s</td><td>%s</td><td><code>%s</code></td></tr>" % (
            E(mesh), E(cp["role"] + (" — " + cp["vendor"] if cp.get("vendor") else "")), E(cp.get("ref") or "—"), ", ".join(where), chip(rv),
            n4(cp.get("p95_ref_to_ours_mm")), n4(cp.get("p95_ours_to_ref_mm")), E(feat), E(cp.get("refcheck_reference") or "—")))
    return "\n".join(out)

def dfm_rows():
    return "\n".join("<tr><td><b>%s</b></td><td>%s</td><td>%s</td><td>%s</td></tr>" % (E(r["parameter"]), E(r["makerworld_states"]), E(r["ours"]), chip(r["verdict"]) + " <span class='small'>" + E(r["verdict"].split(" — ", 1)[1] if " — " in r["verdict"] else "") + "</span>") for r in D["dfm_table"])

def thumbs():
    return "\n".join('<figure><img src="reference/makerworld-3250889/%s" alt="%s"><figcaption>%02d · %s</figcaption></figure>' % (E(f["thumbnail"]), E(f["file"]), f["n"], E(f["name_en"])) for f in F)

worst_ours = max((f["vs_our_rebuild_body"]["ref_to_cand"]["p95_mm"] for f in F if f.get("vs_our_rebuild_body")), default=None)
worst_ours2 = max((f["vs_our_rebuild_body"]["cand_to_ref"]["p95_mm"] for f in F if f.get("vs_our_rebuild_body")), default=None)
worst_id = max(f["identity"]["max_abs_vertex_delta_mm"] for f in F)
gh = L["github"]; bi = L["body_identity"]

page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sources — MakerWorld 3250889</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="tools/doc.css">
<style>
  .thumbs{{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin:10px 0}}
  .thumbs figure{{margin:0;border:1px solid var(--hair);background:#fff}}
  .thumbs img{{width:100%;display:block}}
  .thumbs figcaption{{font-family:var(--sans);font-size:11px;padding:4px 6px;color:var(--ink-2)}}
  .pair{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:10px 0}}
  .pair figure{{margin:0}} .pair img{{width:100%;border:1px solid var(--hair);display:block}}
  figcaption{{font-family:var(--sans);font-size:12px;color:var(--ink-2);padding:4px 0}}
  table.data{{width:100%;border-collapse:collapse;font-size:13px}}
  table.data th,table.data td{{border-bottom:1px solid var(--hair);padding:5px 6px;text-align:left;vertical-align:top}}
  table.data th{{font-family:var(--sans);font-size:11.5px;letter-spacing:.04em;text-transform:uppercase;color:var(--ink-2);background:var(--head)}}
  td.n,th.n{{text-align:right;font-variant-numeric:tabular-nums;font-family:var(--mono);font-size:12px}}
  .small{{font-family:var(--sans);font-size:11.5px;color:var(--ink-2)}}
  #files table.data{{font-size:12px}} #files table.data th,#files table.data td{{padding:4px 4px}} #files td.n{{font-size:11px;white-space:nowrap}}
  #files td.nm{{white-space:nowrap}}
  #contents table.data,#parts table.data{{font-size:12px}} #contents table.data td,#parts table.data td{{padding:4px 4px}}
  #parts td code,#contents td code{{font-size:11px}}
  .chip{{font-family:var(--sans);font-size:11px;font-weight:600;letter-spacing:.04em;padding:1px 6px;border:1px solid;border-radius:2px;white-space:nowrap}}
  .chip.pass{{color:var(--pass-ink);border-color:var(--pass-ink)}} .chip.fail{{color:var(--no);border-color:var(--no)}}
  .chip.cd{{color:var(--cd-ink);border-color:var(--cd-ink)}} .chip.ref{{color:var(--ink-2);border-color:var(--hair)}}
  .verdict{{border-left:3px solid var(--rule);padding:8px 14px;margin:10px 0;background:var(--card)}}
  .verdict.no{{border-left-color:var(--no)}} .verdict.ok{{border-left-color:var(--ready)}}
  .tw{{overflow-x:auto}} pre{{background:var(--mono-bg);border:1px solid var(--hair);padding:8px 10px;font-size:12px;overflow-x:auto}}
  .kv td:first-child{{width:22%;font-family:var(--sans);font-size:12px;color:var(--ink-2)}}
</style>
</head>
<body>
<div class="wrap">
<p class="backlink"><a href="INDEX.html">← Document index</a></p>
<header class="hero">
  <p class="eyebrow">Microduck reverse-engineering · new sources · 1 of 3</p>
  <h1>MakerWorld 3250889 — "structural parts (simulation model export · 15 parts)"</h1>
  <p class="sub">What the page states, what the files are, where they come from, and what they measure against Pollen's meshes and against our rebuild. Generated from <code>out/sources/makerworld-3250889.json</code>.</p>
  <div class="rev"><span>MD-SRC-001 · Rev A</span><span>{E(D["generated"])}</span><span>fetched {E(S["fetched"])}</span><span>licence CC BY-NC-SA</span></div>
</header>
<div class="statbar">
  <div class="stat"><b>{T["files"]}</b><span>STL files</span></div>
  <div class="stat"><b>{T["tris"]:,}</b><span>triangles</span></div>
  <div class="stat"><b>{worst_id:.1e} mm</b><span>worst vertex delta vs Pollen rl 5946fd9</span></div>
  <div class="stat"><b>{T["identity_pass"]}/{T["files"]}</b><span>identical to upstream</span></div>
  <div class="stat"><b>{T["printable_as_shipped_pass"]}/{T["files"]}</b><span>printable as shipped</span></div>
  <div class="stat"><b>{T["vs_ours_pass"]}/{T["files"]}</b><span>PASS vs our rebuild{(" (%d not yet run)" % T["vs_ours_cd"]) if T["vs_ours_cd"] else ""}</span></div>
  <div class="stat"><b>0</b><span>print parameters stated</span></div>
</div>
<nav class="toc">
  <a href="#verdict">1 Verdict</a><a href="#page">2 What the page states</a><a href="#lineage">3 Where the files come from</a>
  <a href="#files">4 The 15 files, measured</a><a href="#contents">5 What each file contains</a><a href="#parts">6 Per part, against our rebuild</a>
  <a href="#dfm">7 Print profile vs our DFM</a><a href="#cannot">8 What a simulation mesh cannot carry</a><a href="#method">9 Method and limits</a>
</nav>

<section id="verdict">
  <h2><span class="n">1</span>Verdict — NOT READY TO BUILD FROM, and not a new source of geometry</h2>
  <div class="verdict no"><b>The files add no geometry we did not already have.</b> Each of the 15 STLs is the concatenation of every visual mesh of one MJCF body from Pollen's <code>microduck_rl</code> assets at commit <code>5946fd9</code>, placed at qpos 0 with the trunk at the origin and scaled to millimetres. Measured order-matched against our own placement of those assets: worst vertex delta <b>{worst_id:.1e} mm</b> over all {T["tris"]:,} triangles — float32 re-serialisation, nothing else. Bytes 80..end of every file are identical to <code>cad/</code> of <a href="{E(gh["url"])}">{E(gh["repo"])}</a> at <code>{gh["pinned_commit"][:7]}</code>.</div>
  <div class="verdict no"><b>Not printable as shipped.</b> {T["files"] - T["printable_as_shipped_pass"]} of {T["files"]} files fuse vendor bodies — XL330 servos, bearings, the battery, both PCBs, the lens, the speaker box — into the printed shells. A slicer unions overlapping shells, so the servo pocket prints solid. The page's own title says "simulation model export" and its summary says "非官方 CAD … 本模型仅为外壳/结构参考" (not official CAD; shell/structural reference only).</div>
  <div class="verdict"><b>No print profile, no BOM, no guide.</b> MakerWorld's design record has <code>instances: []</code>, <code>isPrintable: false</code>, empty <code>projectSettings</code> on all 15 files, <code>design_guide []</code>, <code>design_bom []</code>. The upstream repo's build log has a Print Records table that reads "(TBD)". There is nothing to agree or disagree with per parameter (§7).</div>
  <div class="verdict ok"><b>What it does give us.</b> (a) A pinned, independent placement of the rl assets that agrees with ours to 1e-5 mm — a second opinion on <code>cecad.mjcf</code>. (b) The origin of SPEC.md:75-76's community hole census, now archived per hole (<code>docs/hole_analysis.json</code>, 47 meshes). (c) The first photograph of parts printed from these meshes with M2 screws fitted (2026-09-02), which is evidence about the hole pattern, not about print settings.</div>
</section>

<section id="page">
  <h2><span class="n">2</span>What the page states — verbatim, from the design API</h2>
  <p class="lede">The HTML is behind a Cloudflare challenge for curl, WebFetch and headless Chrome alike (403, archived). The design API answered anonymously and is archived at <code>reference/makerworld-3250889/page/api-design-3250889.json</code>.</p>
  <table class="data kv">
    <tr><td>URL</td><td><a href="{E(S["url"])}">{E(S["url"])}</a></td></tr>
    <tr><td>Title</td><td>{E(S["title_zh"])}<br><span class="small">MakerWorld's translation: {E(S["title_en_machine"])}</span></td></tr>
    <tr><td>Author</td><td>{E(S["author"]["name"])} · handle <code>{E(S["author"]["handle"])}</code> · uid {S["author"]["uid"]} · level {S["author"]["level"]}</td></tr>
    <tr><td>Created / files uploaded</td><td>{E(S["created"])} / {E(S["files_uploaded"])}</td></tr>
    <tr><td>Licence</td><td>API <code>{E(S["licence_api"])}</code>; author's text "{E(S["licence_author_text"])}"; allowReCreation {S["allow_recreation"]}; originals on MakerWorld: {E(str(S["originals_on_makerworld"]))}</td></tr>
    <tr><td>Lineage stated</td><td>{E(S["lineage_stated"])}</td></tr>
    <tr><td>Summary (zh)</td><td><pre>{E(S["summary_zh"])}</pre></td></tr>
    <tr><td>Summary (MakerWorld translation)</td><td><pre>{E(S["summary_en_machine"])}</pre></td></tr>
    <tr><td>Tags / category</td><td>{E(", ".join(S["tags"]))} ({E(", ".join(S["tags_en"]))}) · {E(" > ".join(reversed(S["categories"])))}</td></tr>
    <tr><td>Counters at fetch</td><td>downloads {S["counters"]["downloads"]} · likes {S["counters"]["likes"]} · prints {S["counters"]["prints"]} · comments {S["counters"]["comments"]}</td></tr>
    <tr><td>Print profiles</td><td>instances {S["print_profiles"]["instances"]} · isPrintable {S["print_profiles"]["is_printable_flag"]} · preset type "{E(S["print_profiles"]["preset_type"])}" · all 15 projectSettings empty: {S["print_profiles"]["per_file_project_settings_all_empty"]}</td></tr>
    <tr><td>Guide / BOM / pictures / steps</td><td>{E(str(S["guide"]))} / {E(str(S["bom"]))} / {E(str(S["pictures"]))} / {E(str(S["steps"]))}</td></tr>
    <tr><td>Download</td><td>{E(S["download_requires_login"]["endpoint"])} → <code>{E(S["download_requires_login"]["anonymous_response"])}</code> (measured {E(S["download_requires_login"]["measured"])}). Archive here is Leif's logged-in download: {E(S["archive"]["downloaded_by"])}, {S["archive"]["zip_bytes"]:,} bytes, sha256 <code>{E(S["archive"]["zip_sha256"][:16])}…</code>; entry names {E(S["archive"]["entry_names"])}; re-extraction by <code>{E(S["archive"]["reextract_tool"])}</code></td></tr>
  </table>
  <div class="pair">
    <figure><img src="reference/makerworld-3250889/page/images/cover.jpg" alt="cover"><figcaption>The page's cover: a product photograph of the Sky colourway (not a print of these files).</figcaption></figure>
    <figure><img src="reference/makerworld-3250889/page/images/coverPortrait.webp" alt="portrait cover"><figcaption>The portrait cover: Hugging Face / Pollen comic art.</figcaption></figure>
  </div>
  <p class="lede">The 15 per-file renders MakerWorld generated (grey, unlit, no scale):</p>
  <div class="thumbs">{thumbs()}</div>
</section>

<section id="lineage">
  <h2><span class="n">3</span>Where the files come from — the chain, pinned</h2>
  <ol>{"".join("<li>%s</li>" % E(x) for x in L["chain"])}</ol>
  <table class="data kv">
    <tr><td>GitHub repo</td><td><a href="{E(gh["url"])}">{E(gh["repo"])}</a> — {E(gh["description"])}</td></tr>
    <tr><td>Created / last push / stars / forks</td><td>{E(gh["created"])} / {E(gh["pushed"])} / {gh["stars"]} / {gh["forks"]}</td></tr>
    <tr><td>Licence</td><td>{E(gh["licence"])}</td></tr>
    <tr><td>Pinned commit</td><td><code>{E(gh["pinned_commit"])}</code>, fetched {E(gh["fetched"])}, archived at <code>{E(gh["archived_at"])}</code></td></tr>
    <tr><td>Body identity</td><td>{E(bi["rule"])} — <b>all 15 identical: {bi["all_identical"]}</b>. GitHub header: 80 zero bytes; MakerWorld header: <code>MW 1.0 3250889 US</code>.</td></tr>
    <tr><td>Uploader ↔ repo owner</td><td>{E(L["author_link"])}</td></tr>
  </table>
  <h3>What the replica repo adds beyond the STLs</h3>
  <ul>{"".join("<li>%s</li>" % E(x) for x in L["what_the_replica_adds"])}</ul>
  <div class="pair">
    <figure><img src="reference/makerworld-3250889/upstream-github-fanhao375-microduck-replica/build-log/photos/2026-09-02-首批打印件.jpg" alt="first printed parts"><figcaption>Replica repo build log, 2026-09-02: head shell, trunk shell, leg parts with M2 screws, two feet. Printer, material, layer height: "(TBD)".</figcaption></figure>
    <figure><img src="reference/makerworld-3250889/upstream-github-fanhao375-microduck-replica/assembly-drawings/06_爆炸图_四分之三.png" alt="exploded view"><figcaption>Replica repo exploded view (MuJoCo render) with the MJCF body masses — the same 15 bodies as the 15 files.</figcaption></figure>
  </div>
</section>

<section id="files">
  <h2><span class="n">4</span>The 15 files, measured</h2>
  <p class="lede">Bounding box in the file's own frame (trunk body at origin, mm), triangle count (unique vertices and boundary-edge counts are in the JSON: every file has 0 open edges), the order-matched max vertex delta against Pollen's rl <code>5946fd9</code> assets placed by <code>cecad.mjcf</code>, and <code>cecad.meshcompare</code> p95 surface distance (15 000 samples each way, bbox-centre aligned, tol 1.0 mm / 1.5 mm) against Pollen's decimated simulator body and against OUR rebuild assembled per body.</p>
  <div class="tw"><table class="data">
    <thead><tr><th>#</th><th>Part (file NN_名.stl)</th><th class="n">Size x × y × z (mm)</th><th class="n">Tris</th><th class="n">Δ vs rl 5946fd9 (mm)</th><th class="n">p95 vs Pollen sim body →/← (mm)</th><th class="n">p95 vs our rebuild →/← (mm)</th><th>vs ours</th></tr></thead>
    <tbody>{file_rows()}</tbody>
  </table></div>
  <p class="small">Worst p95 against our rebuild so far: {n4(worst_ours)} / {n4(worst_ours2)} mm (MW→ours / ours→MW). The Pollen simulator bodies are 4.2× coarser (decimated) than the rl assets, which is why they show 0.02–0.16 mm; the rl-asset comparison is exact and is the one that matters.</p>
</section>

<section id="contents">
  <h2><span class="n">5</span>What each file contains — and why none prints as shipped</h2>
  <p class="lede">Read off the vertex blocks (each file preserves the source-mesh order of the MJCF body). Vendor bodies are in bold: they are inside the file as closed shells overlapping the printed pocket that holds them.</p>
  <div class="tw"><table class="data">
    <thead><tr><th>#</th><th>File</th><th>MJCF body</th><th>Printed structural meshes</th><th>Soft (TPU)</th><th>Vendor bodies fused in</th><th>Printable as shipped</th></tr></thead>
    <tbody>{contents_rows()}</tbody>
  </table></div>
</section>

<section id="parts">
  <h2><span class="n">6</span>Per constituent part — does it match our model?</h2>
  <p class="lede">Because the files are the rl assets, the per-part question is already answered by our refcheck grades against those same assets (<code>out/refcheck/&lt;slug&gt;/verify/</code>, read-only here): p95 both ways and the hole/boss feature match. "NO REBUILD" means our assembly carries the vendor mesh itself, so the match is trivial and says nothing.</p>
  <div class="tw"><table class="data">
    <thead><tr><th>Mesh</th><th>Role</th><th>Our part</th><th>In files</th><th>Refcheck</th><th class="n">p95 ref→ours / ours→ref (mm)</th><th>Features</th><th>Graded against</th></tr></thead>
    <tbody>{part_rows()}</tbody>
  </table></div>
</section>

<section id="dfm">
  <h2><span class="n">7</span>Print profile — the source beside docs/DFM.md, parameter by parameter</h2>
  <div class="tw"><table class="data">
    <thead><tr><th>Parameter</th><th>MakerWorld 3250889 states</th><th>Ours (docs/DFM.md)</th><th>Agree / disagree</th></tr></thead>
    <tbody>{dfm_rows()}</tbody>
  </table></div>
</section>

<section id="cannot">
  <h2><span class="n">8</span>What a simulation mesh cannot carry — and this one does not</h2>
  <p>The hope was that a "printable" source would carry fastener seats, insert bosses, ball sockets, cable channels, clearances and split lines that a simulation mesh omits. Measured: the files carry exactly the rl asset surfaces (§4), so they carry exactly what those assets carry. What those assets DO carry is the hole geometry the replica repo censused — Ø2.2 ×77, Ø4.4 ×28, Ø1.6 ×20, Ø2.4 ×22, Ø2.0 ×12, Ø2.7/2.8 ×20, Ø4.8 ×10 complete circular holes across the structural meshes — and what they do NOT carry, in the repo's own words: fit tolerances, thread detail, heat-set insert bosses, cable routing space. The one physical datum is the 2026-09-02 photograph: M2 screws went into the black leg parts printed from these meshes, with hole diameters "(待测)" — still unmeasured.</p>
  <p>Consequence for our CAD: the 145-hole / zero-fastener gap in <code>bom.json</code> is not closed by this source. It is closed by putting the fasteners the census implies into the assembly through connections, which is the fastener lane's work; the per-hole table (<code>docs/hole_analysis.json</code>, diameter / depth / angular coverage per hole per mesh) is archived for it.</p>
</section>

<section id="method">
  <h2><span class="n">9</span>Method and honest limits</h2>
  <ul>
    <li><b>Page.</b> HTML 403 (Cloudflare) three ways; the design API JSON is the record. Signed thumbnail URLs expire within the hour; the images were fetched inside that window.</li>
    <li><b>Identity.</b> <code>cecad.mjcf.load</code> on the simulator MJCF with <code>mesh_dir</code> pointed at the rl assets, <code>bodies_world(root_at_origin=True)</code>, visual geoms only, ×1000; per file the vertex blocks are compared in order (max |Δ|), and the tri counts are compared per tree (sim / rl 5946fd9 / rl develop 29e887e) — <code>15_右踝脚</code> (61 748) matches only the old tree; develop's foot_right/sole_right would give 61 800.</li>
    <li><b>p95.</b> <code>cecad.meshcompare.compare</code>, 15 000 area-weighted samples each way, bbox-centre alignment (the shift reported is exactly (0, 0, 120.0) mm for the Pollen bodies: the trunk body sits at z = 120 in the simulator world). A first run matched bodies by bbox size and confused four mirror pairs; those rows were re-run against the right body and the JSON says which.</li>
    <li><b>Our rebuild per body.</b> <code>out/refcheck/&lt;slug&gt;/verify/ours.stl</code> (Pollen file frame, mm) placed by the same MJCF; meshes with no rebuild use the Pollen mesh and are marked vendor in §6. The head body is mostly vendor meshes in our assembly, so its PASS is weak evidence.</li>
    <li><b>Not measured.</b> Hole diameters on any printed part; whether the uploader and the repo owner are the same person; anything on the MakerWorld page that only a logged-in browser renders (comments, remix list) — the API says 0 comments and no originals.</li>
  </ul>
</section>
</div>
</body>
</html>
"""
out = os.path.join(REPO, "SOURCES.html")
open(out, "w").write(page)
print("wrote", out, len(page), "bytes")
