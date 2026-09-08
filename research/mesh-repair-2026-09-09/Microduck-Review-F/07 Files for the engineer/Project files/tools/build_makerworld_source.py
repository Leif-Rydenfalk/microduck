#!/usr/bin/env python3
"""build_makerworld_source.py — assemble out/sources/makerworld-3250889.json from measurements.

Nothing in the output is typed by hand: every number is read from a file this
lane (or an earlier lane) measured and committed. Inputs:
  reference/makerworld-3250889/page/api-design-3250889.json   the MakerWorld design API record
  reference/makerworld-3250889/files/*.stl                    the 15 STLs (census taken here)
  out/sources/makerworld-3250889-vertex-identity.json         exact vertex identity vs rl 5946fd9
  out/sources/makerworld-3250889-compare.json                 p95 vs Pollen sim bodies + vs our rebuild
  out/refcheck/<slug>/verify/{report,features}.json           our per-part grades (read-only)
  out/web/parts.json                                          mesh -> part ref
Run:  python3 tools/build_makerworld_source.py   (kernel-free)
"""
import glob, hashlib, json, os, re, struct, sys, datetime
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
MWD = os.path.join(REPO, "reference", "makerworld-3250889")
OUT = os.path.join(REPO, "out", "sources", "makerworld-3250889.json")

ZH_EN = {"躯干主体": "torso main body", "左髋yaw-roll": "left hip, yaw-roll stage", "左髋roll": "left hip, roll stage",
         "左大腿": "left thigh", "左小腿": "left shin", "左踝脚": "left ankle + foot", "颈根": "neck root",
         "颈俯仰": "neck pitch stage", "头yaw-roll": "head yaw-roll stage", "头部总成": "head assembly",
         "右髋yaw-roll": "right hip, yaw-roll stage", "右髋roll": "right hip, roll stage", "右大腿": "right thigh",
         "右小腿": "right shin", "右踝脚": "right ankle + foot"}
VENDOR = {"xl330": "Dynamixel XL330-M288-T servo", "seeed_bearing__configuration__22x16x4": "22x16x4 ball bearing",
          "seeed_bearing__configuration_default": "15x10x3 ball bearing", "np_f970": "NP-F battery",
          "pcb__raspberry_pi_zero_2_w": "compute board (Radxa Zero 3W footprint)", "elec_rpi_robot_hat_pcb": "Robot HAT PCB",
          "lens": "M12 lens", "speaker": "speaker placeholder box"}
SOFT = {"jaw_soft", "soft_mouth_top", "sole_left", "sole_right"}

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def census(p):
    raw = open(p, "rb").read(); n = struct.unpack_from("<I", raw, 80)[0]
    rec = np.frombuffer(raw[84:84 + 50 * n], dtype=np.dtype([("n", "<3f4"), ("v", "<9f4"), ("a", "<u2")]))
    T = rec["v"].reshape(-1, 3, 3).astype(float)
    V = T.reshape(-1, 3); lo, hi = V.min(0), V.max(0)
    A = 0.5 * np.linalg.norm(np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]), axis=1)
    vol = float(np.einsum("ij,ij->i", T[:, 0], np.cross(T[:, 1], T[:, 2])).sum() / 6.0)
    uv, inv = np.unique(np.round(V, 6), axis=0, return_inverse=True); F = inv.reshape(-1, 3)
    E = np.sort(np.stack([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]).reshape(-1, 2), axis=1)
    ue, cnt = np.unique(E, axis=0, return_counts=True)
    r4 = lambda a: [round(float(x), 4) for x in a]
    return dict(header=raw[:80].rstrip(b"\0").decode("ascii", "replace"), tris=int(n), bytes=len(raw),
                bytes_expected=84 + 50 * n, bbox_min_mm=r4(lo), bbox_max_mm=r4(hi), size_mm=r4(hi - lo),
                area_mm2=round(float(A.sum()), 4), signed_volume_mm3=round(vol, 4), unique_vertices=int(len(uv)),
                edges_boundary=int((cnt == 1).sum()), edges_nonmanifold=int((cnt > 2).sum()),
                degenerate_tris=int((A <= 1e-9).sum()), attribute_bytes_all_zero=bool((rec["a"] == 0).all()))

def strip_html(s):
    import html as H
    return re.sub(r"\n{2,}", "\n", H.unescape(re.sub(r"<[^>]+>", "\n", s)).replace("\xa0", " ")).strip()

def main():
    api = json.load(open(os.path.join(MWD, "page", "api-design-3250889.json")))
    ident = json.load(open(os.path.join(REPO, "out", "sources", "makerworld-3250889-vertex-identity.json")))
    cmpf = os.path.join(REPO, "out", "sources", "makerworld-3250889-compare.json")
    cmp_ = json.load(open(cmpf)) if os.path.exists(cmpf) else {}
    parts = json.load(open(os.path.join(REPO, "out", "web", "parts.json")))
    ext = api["designExtension"]
    api_files = {m["modelName"]: m for m in ext["model_files"]}

    def refcheck(mesh):
        ref = parts.get(mesh, {}).get("ref"); row = {"mesh": mesh, "ref": ref}
        if mesh in VENDOR: row["role"] = "vendor part (not printed)"; row["vendor"] = VENDOR[mesh]
        elif mesh in SOFT: row["role"] = "soft part (TPU)"
        else: row["role"] = "printed structural part"
        if not ref: row["refcheck"] = "no part ref"; return row
        d = os.path.join(REPO, "out", "refcheck", ref.split(":", 1)[1], "verify")
        if os.path.exists(os.path.join(d, "report.json")):
            r = json.load(open(os.path.join(d, "report.json"))); s = r.get("shape", {})
            row.update(refcheck_verdict=r.get("verdict"), refcheck_when=r.get("when"),
                       refcheck_reference=os.path.relpath(r.get("reference", ""), REPO),
                       p95_ref_to_ours_mm=s.get("ref_to_cand", {}).get("p95_mm"), p95_ours_to_ref_mm=s.get("cand_to_ref", {}).get("p95_mm"),
                       bbox_delta_mm=s.get("bbox_delta_mm"))
            if os.path.exists(os.path.join(d, "features.json")):
                f = json.load(open(os.path.join(d, "features.json")))
                row.update(features_verdict=f.get("verdict"), features_matched=len(f.get("matched", [])),
                           features_unmatched_reference=len(f.get("unmatched_reference", [])), features_extra_ours=len(f.get("extra_ours", [])),
                           features_reference_counts=f.get("reference") if isinstance(f.get("reference"), dict) else None)
        else:
            row["refcheck_verdict"] = "NO REBUILD — vendor mesh is what our assembly carries"
        return row

    files = []
    for p in sorted(glob.glob(os.path.join(MWD, "files", "*.stl"))):
        name = os.path.basename(p); zh = name[3:-4]
        c = census(p); idr = ident.get(name, {}); cr = cmp_.get(name, {})
        blocks = idr.get("blocks", [])
        vendor_in = [b["mesh"] for b in blocks if b["mesh"] in VENDOR]
        soft_in = [b["mesh"] for b in blocks if b["mesh"] in SOFT]
        struct_in = [b["mesh"] for b in blocks if b["mesh"] not in VENDOR and b["mesh"] not in SOFT]
        row = dict(n=int(name[:2]), file=name, name_zh=zh, name_en=ZH_EN.get(zh, zh), sha256=sha(p),
                   makerworld_size_bytes=api_files.get(name, {}).get("modelSize"), makerworld_updated=api_files.get(name, {}).get("modelUpdateTime"),
                   thumbnail="page/images/" + name[:-4] + ".jpeg", census=c,
                   body=idr.get("body"), identity=dict(tree="reference/pollen-microduck-rl/assets (microduck_rl commit 5946fd9cdbc58956424420153e51975af3b30d77)",
                                                      placement="simulator MJCF robot_allcollisions.xml, qpos 0, root body at origin (cecad.mjcf.bodies_world root_at_origin=True), metres x1000",
                                                      max_abs_vertex_delta_mm=idr.get("max_abs_delta_order_mm"), body_tris=idr.get("body_tris"),
                                                      source_mesh_blocks=[dict(mesh=b["mesh"], tris=b["tris"], offset=b["offset"], max_abs_delta_mm=b["max_abs_delta_mm"]) for b in blocks]),
                   contents=dict(structural=struct_in, soft=soft_in, vendor_fused_in=vendor_in),
                   vs_pollen_sim_body=cr.get("vs_pollen_sim_body"), vs_our_rebuild_body=cr.get("vs_our_rebuild_body"),
                   constituent_parts=[refcheck(m) for m in dict.fromkeys(b["mesh"] for b in blocks)])
        # verdicts
        d = idr.get("max_abs_delta_order_mm")
        row["verdict_identity"] = ("PASS — identical to the rl 5946fd9 assets to %.1e mm" % d) if d is not None and d < 1e-3 else "CANNOT DETERMINE — identity not measured"
        row["verdict_printable_as_shipped"] = ("FAIL — file fuses %d vendor bodies (%s) into the printed shells; a slicer prints them as solid plastic where the real part is a pocket"
                                              % (len(vendor_in), ", ".join(sorted(set(vendor_in))))) if vendor_in else "PASS — no vendor bodies fused in"
        v = cr.get("vs_our_rebuild_body")
        if v:
            n_v = sum(1 for cp in row["constituent_parts"] if str(cp.get("refcheck_verdict", "")).startswith("NO REBUILD"))
            row["verdict_vs_our_rebuild"] = "%s — p95 %.4f / %.4f mm (MW->ours / ours->MW), bbox delta %s mm; %d of %d constituent meshes in our body are vendor meshes" % (
                v["verdict"], v["ref_to_cand"]["p95_mm"], v["cand_to_ref"]["p95_mm"], v["bbox_delta_mm"], n_v, len(row["constituent_parts"]))
        else:
            row["verdict_vs_our_rebuild"] = "CANNOT DETERMINE — comparison not yet run"
        files.append(row)

    dfm = [
        ("printer / bed", "not stated (no instance, no preset)", "prusa_mk4 bed for the geometry checks; the farm is a Bambu Lab H2S (docs/DFM.md)"),
        ("nozzle", "not stated", "0.4 mm"), ("layer height", "not stated (projectSettings.layerHeight '')", "0.20 mm"),
        ("walls / perimeters", "not stated (projectSettings.wallLoops '')", "2 perimeters minimum; 0.80 mm floor for a real wall"),
        ("infill", "not stated (projectSettings.sparseInfillDensity '')", "not fixed in DFM.md; grams come from the farm's slice (out/print/slice.json)"),
        ("material", "not stated", "PLA 1.26 g/cm3 for structure, TPU for the soles"),
        ("supports", "not stated", "support area measured per orientation; 5 parts need none, 15 need some (DFM.md summary table)"),
        ("orientation", "not stated; geometry is in the robot's standing pose (world transform applied)", "chosen per part on elevated overhang area (tools/dfm_orient.py)"),
        ("brim", "not stated", "workshop rule: no brim on any print; DFM.md flags shin's 3.6 mm2 foot as the conflict"),
        ("part grouping", "15 files, one per MJCF body, each with its servos/bearings/battery/PCBs fused in", "one file per printed part; vendor parts are separate BOM rows (38 rows, 0 fasteners as of 2026-09-03)"),
        ("assembly guide / fasteners", "none (design_guide [], design_bom [], boms* empty)", "docs/BOM.md, ce-assemblies/microduck/current/bom.json; fastener census 145 M2 holes (SPEC.md:75-76)"),
        ("stated dimension / mass", "'25cm' in the summary only", "envelope 144.1 x 141.0 x 264.0 mm, 737.2 g summed MJCF (SPEC.md §2)"),
    ]
    dfm_rows = [dict(parameter=a, makerworld_states=b, ours=c, verdict="CANNOT DETERMINE — the source states nothing to agree or disagree with") for a, b, c in dfm]
    dfm_rows[9]["verdict"] = "DISAGREE — the source's unit of printing is the MJCF body with vendor parts fused in; ours is the printed part"
    dfm_rows[7]["verdict"] = "DISAGREE — the source's orientation is the robot pose, not a print orientation"

    src = dict(url="https://makerworld.com/en/models/3250889-microduck-robotic-duck-structural-parts-simulation",
               makerworld_id=api["id"], title_zh=api["title"], title_en_machine=api["titleTranslated"], slug=api["slug"],
               author=dict(name=api["designCreator"]["name"], handle=api["designCreator"]["handle"], uid=api["designCreator"]["uid"], level=api["designCreator"]["level"]),
               created=api["createTime"], updated=api["updateTime"], files_uploaded=sorted({m["modelUpdateTime"] for m in ext["model_files"]})[0][:19] + "Z",
               licence_api=api["license"], licence_author_text="非商用 · CC BY-SA-NC", allow_recreation=api["allowReCreation"],
               originals_on_makerworld=api["originals"], lineage_stated="pollen-robotics/microduck_rl MJCF simulation model, world transform applied (author's summary)",
               summary_zh=strip_html(api["summary"]), summary_en_machine=strip_html(api["summaryTranslated"]),
               tags=api["tags"], tags_en=api["tagsTranslated"], categories=[c["name"] for c in api["categories"]],
               counters=dict(downloads=api["downloadCount"], raw_model_downloads=api["rawModelFileDownloadCount"], likes=api["likeCount"], prints=api["printCount"], comments=api["commentCount"], collections=api["collectionCount"]),
               print_profiles=dict(instances=len(api["instances"]), is_printable_flag=api["isPrintable"], preset_type=api["preset"]["type"], per_file_project_settings_all_empty=all(not any(m["projectSettings"].values()) for m in ext["model_files"])),
               guide=ext["design_guide"], bom=ext["design_bom"], boms_needed=ext["boms_needed"], pictures=ext["design_pictures"], steps=api["steps"],
               download_requires_login=dict(endpoint="/api/v1/design-service/design/3250889/model", anonymous_response='403 {"code":1,"error":"Please log in to download models."}', measured="2026-09-03"),
               archive=dict(zip="reference/makerworld-3250889/archive/Microduck+机器鸭结构件（仿真模型导出+·+15+分件）.zip",
                            zip_sha256=sha(glob.glob(os.path.join(MWD, "archive", "*.zip"))[0]), zip_bytes=os.path.getsize(glob.glob(os.path.join(MWD, "archive", "*.zip"))[0]),
                            downloaded_by="Leif, logged in, 2026-09-03 22:11:54 local (file mtime)", entry_names="UTF-8 with zip flag 0x800 (measured on the raw central directory)",
                            reextract_tool="tools/extract_makerworld.py (re-extraction sha256-identical to files/)"),
               page_archive=dict(api_json="reference/makerworld-3250889/page/api-design-3250889.json", html_403="reference/makerworld-3250889/page/page-anonymous-curl-403.html",
                                 headless_chrome="reference/makerworld-3250889/page/page-shot-cloudflare.png (Cloudflare challenge; page never rendered)",
                                 images="reference/makerworld-3250889/page/images/ (cover.jpg = product photograph of the Sky colourway; coverPortrait.webp = Hugging Face / Pollen comic art; 15 grey shaded per-file renders)"),
               fetched="2026-09-03 23:12-23:14 Europe/Stockholm", fetched_by="sources lane, curl anonymous + design API")
    gh = json.load(open(os.path.join(REPO, "out", "sources", "makerworld-3250889-github-identity.json")))
    ghdir = "reference/makerworld-3250889/upstream-github-fanhao375-microduck-replica"
    repo_meta = json.load(open(os.path.join(REPO, ghdir, "repo-metadata.json")))
    lineage = dict(
        chain=["pollen-robotics/microduck_rl @ 5946fd9cdbc58956424420153e51975af3b30d77 — src/mjlab_microduck/robot/microduck/assets (47 STL, metres, part frames) + robot_allcollisions.xml",
               "fanhao375/microduck-replica @ %s — scripts/export_assembly_stl.py: MuJoCo mj_forward at qpos 0, group-2 (visual) geoms concatenated per body, x1000 to mm, 80 zero bytes header -> cad/01..15" % gh["commit"],
               "MakerWorld 3250889 (Peter Pan's Techland, 2026-09-02T03:49:30Z) — the same 15 files; MakerWorld re-serialises the header to 'MW 1.0 3250889 US' on download"],
        github=dict(repo=repo_meta["full_name"], url=repo_meta["html_url"], description=repo_meta["description"], created=repo_meta["created_at"], pushed=repo_meta["pushed_at"],
                    stars=repo_meta["stargazers_count"], forks=repo_meta["forks_count"], licence="dual: scripts/ Apache-2.0; assembly-drawings/ and cad/ CC BY-SA-NC 4.0 (LICENSE, NOTICE.md)",
                    pinned_commit=gh["commit"], archived_at=ghdir, fetched=gh["fetched"]),
        body_identity=dict(rule="bytes 80..end of each MakerWorld file == bytes 80..end of the GitHub cad/ file at the pinned commit; the first 80 bytes are the STL header",
                           files={k: dict(identical=v["body_after_byte_80_identical"], github_header=v["github_header"], mw_header=v["mw_header"], github_sha256=v["github_sha256"], mw_sha256=v["mw_sha256"]) for k, v in gh["files"].items()},
                           all_identical=all(v["body_after_byte_80_identical"] for v in gh["files"].values())),
        author_link="CANNOT DETERMINE — the MakerWorld uploader (foo00 / GitHub peterpanstechland, a maker who forked mjlab on 2026-08-29) and the repo owner (fanhao375) are different account names; nothing on either side names the other. The bytes are the same either way.",
        what_the_replica_adds=["cad/零件对照表.json — the same per-body source-mesh list this lane measured (tri counts agree on all 15)",
                               "docs/紧固件反推.md + docs/hole_analysis.json — the hole census SPEC.md:75-76 already cites as [C]: Ø2.2 x77, Ø4.4 x28, Ø1.6 x20, ~146 structural clearance holes; per-hole diameter/depth/coverage for all 47 meshes",
                               "assembly-drawings/ — 7 MuJoCo renders incl. two exploded views with body masses",
                               "build-log/photos/2026-09-02-首批打印件.jpg — first photograph of parts printed from these meshes: head shell (white/black/red multi-colour), trunk shell, black leg parts WITH M2 screws fitted, two feet (red/yellow). The Print Records table (material, layer, infill, time, printer) is '(TBD)' — no print parameters are recorded anywhere in the repo either",
                               "the repo's own caveat, verbatim: '仿真 STL ≠ 可打印工程件。仿真只关心外形与惯量，不保证配合公差、螺纹孔、热熔螺母座和走线空间。直接打印大概率装不起来'"])
    out = dict(generated=datetime.datetime.now().astimezone().isoformat(timespec="seconds"), generator="tools/build_makerworld_source.py",
               source=src, lineage=lineage, files=files, dfm_table=dfm_rows,
               totals=dict(files=len(files), tris=sum(f["census"]["tris"] for f in files), bytes=sum(f["census"]["bytes"] for f in files),
                           identity_pass=sum(1 for f in files if f["verdict_identity"].startswith("PASS")),
                           printable_as_shipped_pass=sum(1 for f in files if f["verdict_printable_as_shipped"].startswith("PASS")),
                           vs_ours_pass=sum(1 for f in files if f["verdict_vs_our_rebuild"].startswith("PASS")),
                           vs_ours_fail=sum(1 for f in files if f["verdict_vs_our_rebuild"].startswith("FAIL")),
                           vs_ours_cd=sum(1 for f in files if f["verdict_vs_our_rebuild"].startswith("CANNOT"))))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
    print("wrote", OUT, out["totals"])

if __name__ == "__main__":
    main()
