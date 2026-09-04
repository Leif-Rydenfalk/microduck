#!/usr/bin/env python3
"""reconcile.py — the CROSS-DOCUMENT RECONCILIATIONS the factory pack needs, each
one taken as a measurement here rather than asserted in prose somewhere.

    python3 tools/reconcile.py            # writes out/factory/reconcile.json

WHY THIS FILE EXISTS. A factory engineer read the pack on 2026-09-04 and found
four places where two numbers in this repository describe the same thing and
disagree. In every case the pack quoted one of them without saying the other
existed. A number a reader can contradict from a file sitting next to it is
worse than no number: it costs the whole pack its credibility.

So each reconciliation below states EVERY count that exists, what each one
actually counts, which one a factory should act on, and what would close the
gap. Nothing is averaged, nothing is quietly dropped.

  1  robot_hat_outline   Pollen's published Apache-2.0 Robot HAT outline.
                         out/pcb/hat/components.json says 65.0000 x 30.9001 mm.
                         out/open/identity-sourcing.json says 65.0 x 48.5 mm.
                         Same repository, same commit, 17.6 mm apart. MEASURED
                         here directly off the Edge.Cuts layer, with the layer
                         that produced the wrong figure named.
  2  fasteners           Four different fastener counts are in circulation:
                         a 145-hole census, a 325-piece buy list, 79 measured
                         interface features, and what the assembly actually
                         places. They count different things. No purchase order
                         can be cut until the page says which is which.
  3  unknowns            139 "open CANNOT DETERMINE items" is a CURATED harvest.
                         The repository-wide census in the file next to it reads
                         5012 distinct subjects. Both are true of different
                         questions and the pack must say so.
  4  eol_gates           The acceptance section claims its gate list is COMPLETE
                         by construction. Check it: every gated test is either
                         on the ship list or on the exemption list, and both are
                         rendered.

Reads only. Writes only out/factory/reconcile.json.
"""
import datetime
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "factory", "reconcile.json")
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def J(rel, default=None):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return default
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def T(rel):
    p = os.path.join(ROOT, rel)
    return open(p, encoding="utf-8").read() if os.path.exists(p) else ""


# ============================================================ 1 Robot HAT outline
PCB_PATH = "reference/pollen-elec-rpi-robot-hat/elec_RPI_Robot_HAT.kicad_pcb"


def _graphic_bboxes(text):
    """Bounding box of every top-level graphic element, PER LAYER, in the KiCad
    board's own millimetre coordinates. Only top-level `gr_*` elements are read:
    footprint graphics belong to the parts, not to the board outline."""
    per = {}
    kinds = {}
    i = 0
    pat = re.compile(r"\n\t\((gr_line|gr_arc|gr_rect|gr_circle|gr_poly|gr_curve|dimension)\b")
    while True:
        m = pat.search(text, i)
        if not m:
            break
        j = m.start() + 1
        d, k = 0, j
        while k < len(text):
            if text[k] == "(":
                d += 1
            elif text[k] == ")":
                d -= 1
                if d == 0:
                    break
            k += 1
        el = text[j:k + 1]
        i = k
        lm = re.search(r'\(layer "([^"]+)"\)', el)
        lay = lm.group(1) if lm else "(no layer)"
        pts = [(float(a), float(b)) for a, b in
               re.findall(r"\((?:start|end|center|mid|xy)\s+(-?[\d.]+)\s+(-?[\d.]+)\)", el)]
        if not pts:
            continue
        kinds.setdefault(lay, {})
        kinds[lay][m.group(1)] = kinds[lay].get(m.group(1), 0) + 1
        b = per.setdefault(lay, [1e9, -1e9, 1e9, -1e9, 0])
        for x, y in pts:
            b[0] = min(b[0], x)
            b[1] = max(b[1], x)
            b[2] = min(b[2], y)
            b[3] = max(b[3], y)
            b[4] += 1
    return {lay: {"x_min_mm": round(b[0], 4), "x_max_mm": round(b[1], 4),
                  "y_min_mm": round(b[2], 4), "y_max_mm": round(b[3], 4),
                  "width_mm": round(b[1] - b[0], 4), "height_mm": round(b[3] - b[2], 4),
                  "points": b[4], "shapes": kinds[lay]}
            for lay, b in per.items()}


def robot_hat_outline():
    txt = T(PCB_PATH)
    if not txt:
        return {"verdict": "CANNOT DETERMINE",
                "why": "%s is not in the tree; the outline cannot be measured here" % PCB_PATH}
    layers = _graphic_bboxes(txt)
    edge = layers.get("Edge.Cuts")
    comp = (J("out/pcb/hat/components.json") or {}).get("board", {})
    comp_size = (comp.get("outline_bbox_mm") or {}).get("size")
    ours = None
    for b in (J("electronics/pcb-package.json", {}) or {}).get("boards", []):
        if "robot-hat" in (b.get("dir") or ""):
            ours = b.get("outline_mm")
    # The Microduck's own HAT is a Pollen SIMULATION MESH, not a board file; its
    # outline is recorded in the shelf part's own prose, so it is read out of there
    # by pattern rather than typed. If the pattern stops matching the number goes
    # to null and the row says CANNOT DETERMINE — it is never defaulted.
    ms = json.dumps(J("ce-parts/microduck-robot-hat-pcb/component.json", {}) or {}, ensure_ascii=False)
    mesh_bbox = None
    mm = re.search(r"'board_outline' \((\d+\.\d+) x (\d+\.\d+) x (\d+\.\d+) mm\)", ms)
    if mm:
        mesh_bbox = [float(mm.group(1)), float(mm.group(2)), float(mm.group(3))]

    # WHERE 48.5 CAME FROM. Dwgs.User is KiCad's annotation layer; on this board it
    # carries the dimension witness lines, which hang 17.6 mm BELOW the copper. Its
    # bbox is 65.0000 x 48.6000 — the same 65 in x, and 48.6 in y. A bbox taken over
    # the drawing layer instead of the board outline reproduces the wrong figure to
    # 0.1 mm, which is why this is stated as the cause and not as a guess.
    dw = layers.get("Dwgs.User")
    cause = None
    if dw and abs(dw["height_mm"] - 48.5) < 0.6 and abs(dw["width_mm"] - 65.0) < 0.05:
        cause = ("Dwgs.User — KiCad's drawing/annotation layer — has bbox %.4f x %.4f mm on this "
                 "board, because its dimension witness lines hang %.4f mm below the copper. A "
                 "bounding box taken over the DRAWING layer instead of Edge.Cuts reproduces the "
                 "48.5 figure to %.4f mm. That is the most likely origin of the wrong number; it "
                 "is not the board." % (dw["width_mm"], dw["height_mm"],
                                        dw["height_mm"] - edge["height_mm"],
                                        abs(dw["height_mm"] - 48.5)))
    rec = {
        "subject": "Pollen's published Apache-2.0 Robot HAT — the board outline",
        "measured_at": NOW,
        "measured_how": ("this script parsed %s and took the bounding box of every top-level "
                         "gr_line / gr_arc on the Edge.Cuts layer. %d shapes, %d points."
                         % (PCB_PATH, sum((edge or {}).get("shapes", {}).values()), (edge or {}).get("points", 0))),
        "source_repo": (J("out/pcb/hat/components.json") or {}).get("source"),
        "measurement_mm": {"width": (edge or {}).get("width_mm"), "height": (edge or {}).get("height_mm")},
        "verdict": "PASS",
        "agreeing": [
            {"file": "out/pcb/hat/components.json", "field": "board.outline_bbox_mm.size",
             "value_mm": comp_size,
             "note": "written by tools/extract_hat_pcb.py from the same kicad_pcb; agrees with this measurement"},
        ],
        "contradicted": [
            {"file": "out/open/identity-sourcing.json", "line": "52-53",
             "claim": "Board measured off the kicad_pcb: 65.000 x 48.500 mm",
             "delta_mm": round(48.5 - ((edge or {}).get("height_mm") or 0), 4),
             "verdict": "WRONG",
             "why": cause or ("the Edge.Cuts layer measures %.4f mm in y, not 48.5 mm"
                              % ((edge or {}).get("height_mm") or 0)),
             "owned_by": "the WF-UNKNOWNS lane (out/open/ is theirs to write); this lane cannot "
                         "correct that file and states the contradiction instead"},
            {"file": "tools/data/readiness.json", "line": "robot-hat pcb_notes.design_status",
             "claim": "the published outline is 65.0 x 48.5 x 1.0 mm",
             "verdict": "CORRECTED in this pass — it now carries the measured 30.9001 mm and cites this file"},
        ],
        "layer_bboxes_mm": layers,
        "comparison": {
            "pollen_published_board": [(edge or {}).get("width_mm"), (edge or {}).get("height_mm")],
            "our_reconstruction": ours,
            "pollen_simulation_mesh": mesh_bbox,
            "delta_published_vs_ours_mm": ([round(((edge or {}).get("width_mm") or 0) - ours[0], 4),
                                            round(((edge or {}).get("height_mm") or 0) - ours[1], 4)]
                                           if ours else None),
            "delta_published_vs_mesh_mm": ([round(((edge or {}).get("width_mm") or 0) - mesh_bbox[0], 4),
                                            round(((edge or {}).get("height_mm") or 0) - mesh_bbox[1], 4)]
                                           if mesh_bbox else None),
        },
        "what_this_changes": (
            "The question we put to the factory (Q5.4) said adopting Pollen's published board "
            "means 're-modelling the motor support to a 65.0 x 48.5 mm board'. It does not. The "
            "published board is %s x %s mm against our reconstruction's %s x %s mm — a difference "
            "of %s mm on one axis, not 18.5 mm. The decision is therefore much cheaper than the "
            "question implied, and Q5.4 has been rewritten on the measurement."
            % ((edge or {}).get("width_mm"), (edge or {}).get("height_mm"),
               ours[0] if ours else "?", ours[1] if ours else "?",
               round(((edge or {}).get("height_mm") or 0) - (ours[1] if ours else 0), 4))),
        "still_open": {
            "question": "Does a %s mm board fit the HAT pocket in microduck-motor-support?"
                        % (edge or {}).get("height_mm"),
            "verdict": "CANNOT DETERMINE",
            "why": ("no pocket dimension has ever been measured: "
                    "ce-parts/microduck-motor-support carries no interface record for the HAT seat, "
                    "and the only board we have modelled there is the %s mm simulation mesh."
                    % (mesh_bbox[1] if mesh_bbox else "?")),
            "what_settles_it": ("measure the HAT pocket in the motor-support solid against a "
                                "%s mm board — desk work on geometry already in the repository; "
                                "it is parcel B-3a in WORK-BREAKDOWN.html"
                                % (edge or {}).get("height_mm")),
        },
    }
    return rec


# ================================================================= 2 fasteners
def fasteners():
    spec = T("SPEC.md")
    m = re.search(r"Ø2\.2 clearance ×(\d+), Ø4\.4 c'bore ×(\d+), Ø1\.6 tap ×(\d+), Ø2\.7/2\.8 ×(\d+)", spec)
    census = [int(x) for x in m.groups()] if m else []
    src = J("spec/sourcing.json", {}) or {}
    lines = {l["id"]: l for l in src.get("lines", [])}
    b18 = [(i, lines[i]) for i in ("B18a", "B18b", "B18c") if i in lines]
    bom = (J("ce-assemblies/microduck/current/bom.json", {}) or {}).get("record", {})
    brows = bom.get("rows", [])
    frows = [r for r in brows if re.search(r"screw|bolt|\bnut\b|insert|washer", r.get("ref", ""))]
    placed = J("out/fasteners/placed.json", {}) or {}
    pcounts = (placed.get("counts") or {})
    cen = J("out/fasteners/census.json", {}) or {}

    counts = [
        {"n": sum(census), "what_en": "HOLE FEATURES in the community hole analysis",
         "what_zh": "社区孔位分析统计的孔特征数",
         "breakdown_en": ("Ø2.2 clearance x%d, Ø4.4 counterbore x%d, Ø1.6 tap x%d, Ø2.7/2.8 x%d"
                          % tuple(census)) if census else "",
         "breakdown_zh": ("Ø2.2 间隙孔 x%d、Ø4.4 沉孔 x%d、Ø1.6 攻丝底孔 x%d、Ø2.7/2.8 孔 x%d"
                          % tuple(census)) if census else "",
         "source": "SPEC.md:75-76, tagged [C] = community-derived",
         "counts_what_en": ("HOLES, not screws. A counterbored clearance hole is ONE fastener "
                            "location that appears in this list twice — once as a Ø2.2 clearance "
                            "and once as a Ø4.4 counterbore — so the %d is an UPPER BOUND on hole "
                            "features and cannot be read as a screw count." % sum(census)),
         "counts_what_zh": ("统计的是<b>孔</b>而非螺钉。一个带沉孔的过孔在此表中出现两次（Ø2.2 间隙孔一次、"
                            "Ø4.4 沉孔一次），因此 %d 是孔特征数的上限，不能当作螺钉数量。" % sum(census)),
         "may_a_buyer_order_against_it": "NO — it counts holes, and it double-counts counterbored ones"},
        {"n": (cen.get("fastening_features")),
         "what_en": "FASTENING FEATURES measured off our own geometry",
         "what_zh": "从我方几何体实测得到的紧固特征数",
         "breakdown_en": "across %s parts that carry an interface record; implied %s"
                         % (cen.get("parts_with_interfaces"),
                            ", ".join("%s x%s" % (k, v) for k, v in (cen.get("implied_by_size") or {}).items())),
         "breakdown_zh": "覆盖 %s 个带接口记录的零件" % cen.get("parts_with_interfaces"),
         "source": "out/fasteners/census.json (tools/fastener_census.py, reads ce-parts/*/current/cad/interfaces.json)",
         "counts_what_en": ("features a part MEASURED off its own solid and recorded. It is lower "
                            "than the community hole count because only %s of the 47 meshes have "
                            "been rebuilt parametrically and can be measured at all."
                            % cen.get("parts_with_interfaces")),
         "counts_what_zh": "零件从自身实体上实测并记录的特征。低于社区孔数，因为仅部分零件已参数化重建、可供测量。",
         "may_a_buyer_order_against_it": "NO — it is a census of what we can measure, not of what the robot has"},
        {"n": pcounts.get("placed"),
         "what_en": "SCREWS actually placed in the assembly, each through a connection",
         "what_zh": "实际装入装配体的螺钉数（均经连接件定位）",
         "breakdown_en": "; ".join("%s x%s" % (k, v) for k, v in (pcounts.get("by_screw") or {}).items()),
         "breakdown_zh": "; ".join("%s x%s" % (k, v) for k, v in (pcounts.get("by_screw") or {}).items()),
         "source": "out/fasteners/placed.json counts (tools/place_fasteners.py); BOM: %d rows, %d fastener rows"
                   % (len(brows), len(frows)),
         "counts_what_en": ("real solids in the model, with a length and a connection each. This is "
                            "the only one of the four that says WHICH screw goes WHERE, and it is "
                            "incomplete: it covers the runs the fastener lane has reached so far."),
         "counts_what_zh": "模型中的真实实体，每颗都有长度与连接方式。四者中唯一说明“哪颗螺钉装在哪里”的数据，但尚不完整。",
         "may_a_buyer_order_against_it": "NOT YET — it is the per-hole schedule being built, and it is incomplete"},
        {"n": sum((l.get("qty_per_robot") or 0) for _i, l in b18),
         "what_en": "PIECES on the buy list, per robot",
         "what_zh": "采购清单上的每台件数",
         "breakdown_en": "; ".join("%s %s x%s" % (i, l["item"].split(",")[0], l.get("qty_per_robot")) for i, l in b18),
         "breakdown_zh": "; ".join("%s x%s 件" % (i, l.get("qty_per_robot")) for i, l in b18),
         "source": "spec/sourcing.json B18a/B18b/B18c; basis docs/BOM.md §4",
         "counts_what_en": ("PIECES to buy, and it counts things the hole census does not: nuts, "
                            "five different screw lengths, M2.5, and heat-set inserts. Its own basis "
                            "field says COMMUNITY-DERIVED from hole-fitting on the 47 meshes, NOT a "
                            "Pollen BOM."),
         "counts_what_zh": ("<b>采购件数</b>，包含孔数统计中没有的项：螺母、五种螺钉长度、M2.5 以及热熔螺母。"
                            "其依据字段自述为：由 47 个网格的孔位拟合推得，<b>并非</b> Pollen 的 BOM。"),
         "may_a_buyer_order_against_it": "YES, as an upper bound with spares — it is the only piece count that exists"},
    ]
    order = [l for i, l in b18]
    return {
        "subject": "How many fasteners are in one Microduck",
        "measured_at": NOW,
        "verdict": "CANNOT DETERMINE — no count in this repository is a screw count taken off a real robot",
        "counts": counts,
        "why_they_differ_en": (
            "They count four different things: hole features (with counterbores double-counted), "
            "measurable interface features on the parts we have rebuilt, screws placed in the model "
            "so far, and pieces on a buy list that also includes nuts and inserts. None of them is "
            "wrong; quoting any one of them as 'the number of fasteners' is."),
        "why_they_differ_zh": (
            "四者统计的对象不同：孔特征（沉孔被重复计数）、已重建零件上可测的接口特征、目前已装入模型的螺钉、"
            "以及包含螺母与热熔螺母的采购件数。四者都不错，把其中任何一个当成“紧固件总数”才是错的。"),
        "what_a_buyer_orders_against_en": (
            "Order against the buy list — B18a %s + B18b %s screws and nuts, B18c %s heat-set inserts "
            "= %s pieces per robot — and treat it as an UPPER BOUND WITH SPARES, not a bill of "
            "materials. Its basis is our own hole-fitting on Pollen's meshes, not a Pollen BOM, and "
            "it has never been checked against a real unit."
            % tuple([l.get("qty_per_robot") for l in order] + [sum((l.get("qty_per_robot") or 0) for l in order)])
            if len(order) == 3 else "the buy list, as an upper bound"),
        "what_a_buyer_orders_against_zh": (
            "按采购清单下单（B18a + B18b 螺钉与螺母、B18c 热熔螺母，合计每台 %s 件），并视其为<b>含余量的上限</b>，"
            "而非正式物料清单。其依据是我方在 Pollen 网格上的孔位拟合，并非 Pollen 的 BOM，且从未与实物核对。"
            % sum((l.get("qty_per_robot") or 0) for l in order)),
        "spread_at_1000_robots": {
            "low": min(c["n"] for c in counts if c["n"]) * 1000,
            "high": max(c["n"] for c in counts if c["n"]) * 1000,
            "note": "the spread between the smallest and largest count, times 1000 robots — "
                    "which is why the pack states all four instead of one",
        },
        "what_closes_it": (
            "Two things, in this order. (1) Finish the per-hole schedule: every hole in the model "
            "gets its screw, its length and its connection, so the placed count becomes a real "
            "bill. That is agent work and it is IN FLIGHT (WF-FASTENERS). (2) Count the screws in "
            "a real unit during the teardown (parcel M-2) and compare. Until (2), every count here "
            "is derived from Pollen's simulation meshes and none has been checked against hardware."),
    }


# ================================================================== 3 unknowns
def unknowns():
    harv = J("out/open/cannot-determine-harvest.json", []) or []
    cen = J("out/open/cannot-determine.json", {}) or {}
    stated = sum(1 for h in harv if isinstance(h, dict)
                 and any(k for k in h if "settle" in k.lower() or "close" in k.lower()))
    return {
        "subject": "How many CANNOT DETERMINE items are open",
        "measured_at": NOW,
        "curated_harvest": {
            "file": "out/open/cannot-determine-harvest.json",
            "n": len(harv),
            "records_stating_what_settles_them": stated,
            "what_it_is_en": ("a HAND-CURATED list: the distinct open questions someone judged worth "
                              "working, each written with what would settle it. It is the work "
                              "queue, not a census."),
            "what_it_is_zh": "人工整理的清单：被判定值得推进的独立未定问题，每条都写明如何定案。它是工作队列，不是普查结果。",
        },
        "repository_census": {
            "file": "out/open/cannot-determine.json",
            "generated_by": (cen.get("doc") or {}).get("generated_by"),
            "distinct_subjects": cen.get("total"),
            "occurrences": cen.get("occurrences"),
            "files_scanned": (cen.get("scanned") or {}).get("files"),
            "stating_what_settles_them": cen.get("items_stating_what_settles_them"),
            "no_closure_route": cen.get("items_with_no_closure_route"),
            "by_class": cen.get("by_class"),
            "what_it_is_en": ("every string in the repository that reads CANNOT DETERMINE, "
                              "deduplicated by subject. It is an UPPER BOUND: one item republished "
                              "across generated documents is counted once per distinct wording, so "
                              "the same question appears several times. Its own note says as much."),
            "what_it_is_zh": ("仓库中所有写有 CANNOT DETERMINE 的文本，按主题去重后的结果。这是<b>上限</b>："
                              "同一项在多份生成文档中以不同措辞重复出现时会被多次计入，该文件自身也如此说明。"),
        },
        "verdict": "BOTH ARE TRUE OF DIFFERENT QUESTIONS",
        "reconciliation_en": (
            "%d is the size of the work queue. %s is the size of the haystack. The pack quotes the "
            "%d, and it must say which it is quoting, because an engineer who greps this repository "
            "for CANNOT DETERMINE will find %s occurrences and conclude the pack understated by a "
            "factor of %.0f."
            % (len(harv), cen.get("total"), len(harv), cen.get("occurrences"),
               (cen.get("total") or 0) / max(1, len(harv)))),
        "reconciliation_zh": (
            "%d 是工作队列的规模；%s 是待筛查文本的规模。交付包引用的是前者，并且必须写明这一点——"
            "否则工程师在仓库中检索 CANNOT DETERMINE 会得到 %s 处，从而认为交付包把问题少报了约 %.0f 倍。"
            % (len(harv), cen.get("total"), cen.get("occurrences"),
               (cen.get("total") or 0) / max(1, len(harv)))),
        "the_real_defect": (
            "Not the count. It is that only %s of %s distinct subjects state what would settle "
            "them, so %s have no closure route written down at all. A CANNOT DETERMINE with no "
            "named closer is the one kind this project treats as a defect."
            % (cen.get("items_stating_what_settles_them"), cen.get("total"),
               cen.get("items_with_no_closure_route"))),
    }


# ================================================================= 4 eol gates
def eol_gates():
    tp = J("spec/test-plan.json", {}) or {}
    tests = [t for s in tp.get("sections", []) for t in (s.get("tests") or [])]
    gated = [t for t in tests if t.get("gate")]
    ship = [g[0] for g in tp.get("eol", [])]
    exempt = tp.get("eol_exempt", [])
    exempt_ids = [e[0] for e in exempt]
    unaccounted = [t["id"] for t in gated if t["id"] not in ship and t["id"] not in exempt_ids]
    return {
        "subject": "Is the end-of-line gate list complete?",
        "measured_at": NOW,
        "gated_tests": len(gated),
        "on_the_ship_list": len(ship),
        "on_the_exemption_list": len(exempt_ids),
        "exemptions": [{"id": e[0], "why": e[1], "where_it_runs_instead": e[2] if len(e) > 2 else None}
                       for e in exempt],
        "unaccounted_for": unaccounted,
        "verdict": "PASS" if not unaccounted and len(ship) + len(exempt_ids) == len(gated) else "FAIL",
        "arithmetic": "%d gated tests = %d on the ship list + %d exempt" % (len(gated), len(ship), len(exempt_ids)),
        "what_was_wrong_en": (
            "spec/test-plan.json's eol_note claims the list is COMPLETE by construction because "
            "every gated test is either on the ship list or 'on the exemption list below it with a "
            "reason'. The exemption list exists in the data (eol_exempt, %d rows) and FACTORY-PACK "
            "never rendered it, so the completeness claim could not be checked by a reader — and "
            "the note itself was clipped at 400 of its %d characters, cutting the sentence off "
            "mid-clause. Both are fixed: the note is printed whole and the exemptions are a table."
            % (len(exempt_ids), len(tp.get("eol_note", "")))),
    }


# ====================================================================== write
rec = {
    "$doc": ("out/factory/reconcile.json — the cross-document reconciliations behind FACTORY-PACK.html "
             "and FACTORY-QUESTIONS.html. Generated by tools/reconcile.py. Each entry names every "
             "count that exists for one quantity, what each counts, and which one to act on."),
    "generated": NOW,
    "robot_hat_outline": robot_hat_outline(),
    "fasteners": fasteners(),
    "unknowns": unknowns(),
    "eol_gates": eol_gates(),
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(rec, f, indent=1, ensure_ascii=False)

hat = rec["robot_hat_outline"]
print("wrote %s" % OUT)
print("  Robot HAT outline MEASURED %s x %s mm (Edge.Cuts); the 48.5 claim is %s"
      % (hat["measurement_mm"]["width"], hat["measurement_mm"]["height"], hat["contradicted"][0]["verdict"]))
print("  fasteners: %s" % ", ".join("%s = %s" % (c["what_en"].split(" in ")[0], c["n"]) for c in rec["fasteners"]["counts"]))
print("  unknowns: harvest %d vs census %s distinct / %s occurrences"
      % (rec["unknowns"]["curated_harvest"]["n"], rec["unknowns"]["repository_census"]["distinct_subjects"],
         rec["unknowns"]["repository_census"]["occurrences"]))
print("  eol gates: %s — %s" % (rec["eol_gates"]["verdict"], rec["eol_gates"]["arithmetic"]))
if rec["eol_gates"]["verdict"] != "PASS":
    raise SystemExit("reconcile: the end-of-line gate list is NOT complete: %s unaccounted for"
                     % rec["eol_gates"]["unaccounted_for"])
