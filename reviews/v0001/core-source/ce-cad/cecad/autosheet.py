# ce-cad — Copyright (c) 2026 Leif Rydenfalk. All rights reserved.
# Proprietary and confidential. Use only under a written licence; see LICENSE.

"""Automatic blueprint generation — a drawing for any Part, chosen by measuring.

    from cecad.autosheet import auto_blueprint
    auto_blueprint(part, "out/release/parts/con_rod/con_rod")

`sheets.Sheet` gives full control and expects a human to say which views, where
to cut, and what to dimension. That is right when someone is drawing one part.
It does not scale to "draw all twelve parts of this machine and send them to a
supplier", which is what `release.py` needs.

Everything here is a decision made from the solid:

    VIEWS       from the bounding box. A plate gets the two views that show it;
                a shaft gets two; anything with three meaningful extents gets
                three. Drawing a 5 mm plate in three views wastes two thirds of
                the paper on a pair of identical lines.
    THE SECTION from the hole axes. The cutting plane is placed where it crosses
                the most hole axes at once, because that is the plane that
                explains the most about the part. A part with no internal
                feature gets no section — a hatched circle through solid bar is
                not information.
    ITS CELL    in the SAME ROW as the primary view. Left to place itself a
                section takes the free cell above, and a 147 mm part stacked
                twice is 294 mm of model on a 297 mm sheet: the scale picker
                then has to choose 1:5 for something that fits at 1:1.
    BACKGROUND  dropped when the part has a ring of a dozen or more identical
                holes. Gear teeth and pulley grooves seen edge-on behind the
                cut print as a black bar over the rim, web and bore the section
                exists to show.
    A DIMENSION between the two connectors furthest apart in the primary view,
                which on a linkage is the dimension the part exists to hold.
                Skipped when it would restate the overall size — the same
                number twice is how a drawing comes to disagree with itself.
    THE SHEET   the smallest ISO size that draws the part at a scale worth
                printing, escalated when the sheet does not verify.

Then it is READ BACK. `sheets.verify_sheet` parses the finished SVG and checks
every number on it against `cecad.inspect`. If a sheet fails, the next strategy
is tried; a sheet that never verifies is returned marked, never silently.
"""
import math
import os

from .inspect import bbox_of, holes, thinnest_wall_detail
from .sheets import Sheet, verify_sheet, SHEETS, _pick_detail_scale

#: sheet sizes to escalate through. A2 exists here because a 400 mm part on A3
#: is legible only at 1:5. A0 is the LAST RESORT and it exists because the
#: search's own refusal demanded it: MEASURED 2026-09-03 on
#: `part:microduck-hip-bracket`, every one of 21 attempts ended in
#: "the notes column fits on the paper — 77.92 mm of notes below the frame —
#: the sheet cannot hold what it was told to say; it needs bigger paper, not
#: fewer facts", and the ladder had no bigger paper to reach for, so the part
#: shipped FAIL with a sheet nobody could use. docs/MANUFACTURING-REQUIREMENTS
#: §A.8 is explicit that a dense part goes on bigger paper rather than
#: shrinking to an unreadable scale. A0 is only ever reached when A1 has
#: already failed, so nothing that fits today moves.
LADDER = ("A3", "A2", "A1", "A0")

#: below this the drawing is too small to measure off and the sheet should grow
MIN_SCALE = 1.0 / 5.0

#: a ring of this many identical holes is a tooth form, not a feature set
TOOTH_RING = 10

#: a dimension this close to the view's overall size is that overall size
DUPLICATE_TOL = 0.5

# ---- manufacturing mode ---------------------------------------------------
#: feature density (holes + sections + detail callouts) above which a part is
#: too dense to draw legibly at a printable scale on A3 — it starts on A2.
#: MEASURED off the solid, so a busy part earns the paper it needs and a plate
#: does not. 8 was the point at which the shin's 15-hole sheet and the
#: power-support's 14-hole sheet stopped reading at any A3 scale.
_A2_DENSITY = 8

#: a hole appears as a CIRCLE in a view when its axis is within this of the
#: view normal — only those are worth ringing for a detail bubble.
_CIRCLE_DOT = 0.94

#: single-linkage radius that groups small circle-holes into a boss/flange
#: cluster, and the fewest holes that make a cluster worth enlarging.
_CLUSTER_R = 16.0
_CLUSTER_MIN = 2

#: a hole this small or smaller is a fastener / tapped hole — the smudge a
#: machinist cannot read at sheet scale and the reason for a detail bubble.
_SMALL_HOLE = 3.0

#: a wall at or below this (near the two-perimeter FDM floor) earns a detail
#: bubble at its measured location — the place a print is most likely to fail.
_THIN_WALL_NOTE = 1.2

#: model radius of the thinnest-wall detail bubble.
_WALL_DETAIL_R = 8.0

#: detail bubbles a single manufacturing sheet carries in its extras band.
_MAX_DETAILS = 3

_PRIMARY = {"top": (1, 0), "front": (1, 1), "right": (2, 1)}


def _extents(part):
    bb = bbox_of(part)
    return float(bb[0]), float(bb[1]), float(bb[2])


def choose_views(part):
    """(views, primary) for a part, from its bounding box.

    A view is worth paper only if it shows something the others do not. The
    plane holding the two largest extents always earns one; the third is
    dropped when the part is flat enough that it would be a pair of lines.
    """
    ex, ey, ez = _extents(part)
    e = (ex, ey, ez)
    thin = min(e) / max(max(e), 1e-9)
    # which axis is the thin one decides which plane shows the part
    thin_axis = min(range(3), key=lambda i: e[i])
    plane = {2: "top", 1: "front", 0: "right"}[thin_axis]
    edge = {2: "front", 1: "top", 0: "front"}[thin_axis]

    if thin < 0.15:
        # plate, blade, con-rod: two views say all of it
        return [plane, edge], plane

    # a shaft or rod — two extents nearly equal and both small against the third
    srt = sorted(range(3), key=lambda i: e[i])
    if e[srt[1]] / max(e[srt[2]], 1e-9) < 0.25 and \
            abs(e[srt[0]] - e[srt[1]]) < 0.15 * max(e[srt[1]], 1e-9):
        long_axis = srt[2]
        views = {0: ["top", "front"], 1: ["top", "front"],
                 2: ["front", "right"]}[long_axis]
        return views, views[0]

    return ["front", "top", "right"], "front"


def choose_section(part, primary, rank=0):
    """The `rank`-th best cutting plane, or None.

    Rank 0 is the plane that crosses the most hole axes. The others exist
    because a plane can be the most informative one and still be undrawable:
    the reference base plate's best plane put its cutting-plane letter exactly
    where a hole callout had to go, and no sheet size fixes that — the letter
    and the callout scale together. Moving the plane does.
    """
    cands = section_candidates(part, primary)
    return cands[rank] if rank < len(cands) else None


def section_candidates(part, primary):
    """Cutting planes worth drawing, best first: [(axis, coord, background)].

    A plane whose normal is a hole's own axis tells you nothing about that
    hole, so those are not counted for it.
    """
    hs = holes(part)
    if not hs:
        return []

    # a ring of identical holes is a tooth form: draw the cut without what is
    # behind it, or the teeth seen edge-on bury the section
    by_d = {}
    for h in hs:
        by_d.setdefault(round(h.d, 2), 0)
        by_d[round(h.d, 2)] += 1
    background = max(by_d.values()) < TOOTH_RING

    scored = []
    for n in range(3):                       # candidate plane normal
        # holes this plane can say something about: the ones not along it
        coords = [h.center[n] for h in hs
                  if abs(h.axis[n]) < 0.9]
        if not coords:
            continue
        # group by the coordinate shared by hole axes, to 0.05 mm
        buckets = {}
        for c in coords:
            buckets.setdefault(round(c / 0.05) * 0.05, []).append(c)
        for _, members in buckets.items():
            scored.append((len(members), "xyz"[n],
                           round(sum(members) / len(members), 4)))

    if not scored:
        return []
    # Best first, at most `_PER_AXIS` planes per axis. Not one per axis: the
    # belt mast has two equally-scoring x planes — through the bearing seats
    # and through the foot inserts — and a tie broken by dict order is not a
    # reason to discard the other one. Not all of them either: parallel cuts a
    # few mm apart are the same drawing twice.
    scored.sort(key=lambda s: -s[0])
    out, per_axis = [], {}
    for score, axis, coord in scored:
        if per_axis.get(axis, 0) >= _PER_AXIS:
            continue
        if any(a == axis and abs(c - coord) < _PLANE_APART
               for a, c, _ in out):
            continue                          # too close to one already taken
        per_axis[axis] = per_axis.get(axis, 0) + 1
        out.append((axis, coord, background))
    return out


def section_cell(views, primary, taken):
    """A free cell in the primary view's ROW — never a new row.

    This is the difference between 1:1 and 1:5 on a tall part, and no check
    catches it: a sheet drawn at 1:5 passes every dimension test and is still
    the wrong drawing.
    """
    row = _PRIMARY.get(primary, (1, 1))[1]
    used = {c for c in taken}
    cols = [c for c, r in used if r == row]
    order = ([max(cols) + 1] if cols else [2]) + [3, 2, 0]
    for c in order:
        if 0 <= c <= 3 and (c, row) not in used:
            return (c, row)
    return None


def choose_dimension(part, primary):
    """(c1, c2, axis) between the two connectors furthest apart, or None.

    The house rule is that a part is placed by its connectors, and it applies
    to drawings: reading the two connectors measures the same thing the
    assembly measures, off the same source. A number typed from the parameter
    block agrees with the parameter block by construction.
    """
    conns = getattr(part, "_connectors", None) or {}
    if len(conns) < 2:
        return None
    from .drawing import to2d_fn
    to2d = to2d_fn(primary)
    pts = {n: to2d(c.pos) for n, c in conns.items()}
    names = sorted(pts)
    best = None
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            pa, pb = pts[a], pts[b]
            for ax, sep in (("x", abs(pb[0] - pa[0])), ("y", abs(pb[1] - pa[1]))):
                if best is None or sep > best[0]:
                    best = (sep, a, b, ax)
    if best is None:
        return None
    sep, a, b, ax = best
    ex, ey, ez = _extents(part)
    hi, vi = _view_axes(primary)
    overall = (ex, ey, ez)[hi if ax == "x" else vi]
    if sep < 0.05 * max(overall, 1e-9):
        return None                      # too small to dimension usefully
    if abs(sep - overall) < DUPLICATE_TOL:
        return None                      # this IS the overall size, already drawn
    return a, b, ax


def _view_axes(view):
    from .sheets import _view_axis_indices
    return _view_axis_indices(view)


# ==========================================================================
# Manufacturing mode: the regions worth a detail view, the DFM note block and
# the paper size — every one MEASURED off the solid, none hand-listed.
# ==========================================================================
def _circle_holes(part, view):
    """Holes that read as CIRCLES in `view` — axis within `_CIRCLE_DOT` of the
    view normal — as [(x2d, y2d, r, d)] in the view's own 2D frame. A hole
    seen edge-on is a line and cannot be ringed usefully, so it is dropped."""
    from .drawing import view_basis, to2d_fn
    _r, _u, look = view_basis(view)
    to2d = to2d_fn(view)
    out = []
    for h in holes(part):
        ax = h.axis
        dot = abs(ax[0] * look[0] + ax[1] * look[1] + ax[2] * look[2])
        if dot >= _CIRCLE_DOT:
            x, y = to2d(h.center)
            out.append((float(x), float(y), h.d / 2.0, float(h.d)))
    return out


def _cluster(points, eps):
    """Single-linkage connected components of 2D `points`, grouped when any
    two are within `eps`. Returns lists of indices."""
    n = len(points)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    e2 = eps * eps
    for i in range(n):
        for j in range(i + 1, n):
            dx = points[i][0] - points[j][0]
            dy = points[i][1] - points[j][1]
            if dx * dx + dy * dy <= e2:
                parent[find(i)] = find(j)
    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    return list(groups.values())


def detail_regions(part, primary, max_n=_MAX_DETAILS,
                   thin_wall_max=_THIN_WALL_NOTE):
    """Regions of `part` worth an enlarged DETAIL view, MEASURED, best first:
    [{center, radius, n, why}] in the PRIMARY view's 2D frame so each ring
    lands on the metal it enlarges.

    Two measured sources, in manufacturing order:
      1. CLUSTERED SMALL HOLES seen as circles in the primary view (a boss or
         flange fastener pattern) — the dense smudge no sheet scale can hold.
         Grouped by `inspect.holes` position, ranked by how many holes.
      2. THE THINNEST-WALL LOCATION (`inspect.thinnest_wall_detail`) when the
         wall is at or below the FDM floor — the place a print fails first.

    A region is kept only if it actually ENLARGES: if the largest ISO ratio
    that still fits the extras column is 1:1 the "detail" is the same size as
    the view and buys nothing, so it is dropped (this is what excludes two
    fastener pins 50 mm apart that are not a cluster)."""
    regions = []
    chs = [c for c in _circle_holes(part, primary) if c[3] <= _SMALL_HOLE]
    for idxs in _cluster(chs, _CLUSTER_R):
        if len(idxs) < _CLUSTER_MIN:
            continue
        xs = [chs[i][0] for i in idxs]
        ys = [chs[i][1] for i in idxs]
        cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
        r = max(math.hypot(chs[i][0] - cx, chs[i][1] - cy) + chs[i][2]
                for i in idxs) + 1.5
        if _pick_detail_scale(r)[0] < 2:
            continue                     # would not enlarge — not a detail
        ds = sorted({round(chs[i][3], 2) for i in idxs})
        why = "%dx \u00d8%s cluster" % (len(idxs),
                                   "/".join("%.2f" % d for d in ds))
        regions.append(dict(center=(cx, cy), radius=r, n=len(idxs), why=why,
                            _rank=(0, -len(idxs), -r)))

    tw = thinnest_wall_detail(part)
    if (tw.get("mm") is not None and tw.get("where")
            and tw["mm"] <= thin_wall_max):
        from .drawing import to2d_fn
        cx, cy = to2d_fn(primary)(tw["where"])
        cx, cy = float(cx), float(cy)
        inside = any(math.hypot(cx - g["center"][0], cy - g["center"][1])
                     < g["radius"] for g in regions)
        if not inside:
            regions.append(dict(center=(cx, cy), radius=_WALL_DETAIL_R, n=0,
                                why="thinnest wall %.2f mm" % tw["mm"],
                                _rank=(1, 0, 0)))

    regions.sort(key=lambda g: g["_rank"])
    return regions[:max_n]


def hidden_choice(part, views, tol=0.35):
    """Per view: may the hidden lines be SUPPRESSED without losing a feature?

    `docs/MANUFACTURING-REQUIREMENTS.md` A.1 (Leif): *"Hidden lines that are
    not a manufacturing feature — no dashed forest behind a face."* Turning
    them off everywhere is the obvious reading and it is WRONG, measured
    2026-09-02 on `part:microduck-trunk-base`'s top view: with hidden lines
    off, TechDraw's visible set omits **12 edges — the two end circles and the
    seam of each of four Ø1.80/Ø1.59 tapered bores** — and `projection_agrees`
    finds 36 edge samples with no ink within reach, worst 2.34 mm. Nothing
    occludes them (a boolean cut of the sight line returns 0.000 mm of
    material), so they are edges the observer can see and the drawing does not
    have. A shop cannot make a feature that is not on the sheet; a dashed line
    it does not need is only untidy.

    So the choice is MEASURED, per view, by the same check that reads the
    finished sheet back: draw it without hidden lines, ask whether any visible
    sharp edge went missing, and keep them only where the answer is yes. The
    reason is returned so the sheet can print it.
    """
    from .sheets import projection_agrees
    out = {}
    for v in views:
        try:
            # view_prims returns (prims, n_visible, n_hidden) — taking the
            # tuple whole handed `projection_agrees` a 3-tuple where it wanted
            # a primitive list, and the AttributeError was swallowed by the
            # guard below into "the probe could not run", which is exactly the
            # shape of a bug that hides: every view came back "hidden lines
            # KEPT" with a reason that looked like an honest refusal.
            # PROBE THE VIEW THE SHEET WILL DRAW, not a raw projection of
            # the same solid. `_View` refits arcs, drops coincident hidden
            # lines, substitutes a gear blank and applies the view's own
            # tolerance; `view_prims` does none of that, so the two disagree
            # about what ink exists. Measured 2026-09-02 on
            # `part:microduck-trunk-base`: the raw probe reported 0 missing
            # and the sheet's own read-back then failed the top view with 36
            # samples with no ink — 69 attempts, 14 185 s, on a decision the
            # probe had already got wrong.
            probe = Sheet(part, size="A3")
            pv = probe.view(v, hidden=False, holes=False, dims=False,
                            marks=False)
            r = projection_agrees(pv.obj, pv.view, pv.prims, hidden=False,
                                  tol=tol)
        except Exception as e:                                # noqa: BLE001
            # A probe that will not run is not evidence that suppression is
            # safe. Keep the hidden lines and say why.
            out[v] = {"hidden": True, "missing": None,
                      "why": "the suppression probe could not run (%s: %s), "
                             "so hidden lines are KEPT" % (type(e).__name__, e)}
            continue
        miss = int(r.get("missing") or 0)
        out[v] = {
            "hidden": miss > 0, "missing": miss,
            "worst": round(float(r.get("missing_worst") or 0.0), 4),
            "samples": int(r.get("edge_samples") or 0),
            "why": ("hidden lines KEPT: without them %d of %d edge samples "
                    "have no ink within %.2f mm (worst %.3f mm) and the "
                    "feature would be missing from the sheet"
                    % (miss, r.get("edge_samples") or 0, tol,
                       r.get("missing_worst") or 0.0)) if miss else
                   ("hidden lines SUPPRESSED: all %d edge samples still land "
                    "on drawn ink without them"
                    % (r.get("edge_samples") or 0))}
    return out


def feature_density(part):
    """How much a sheet of `part` has to carry: holes + section candidates +
    detail regions. The number the paper-size decision is measured against."""
    primary = choose_views(part)[1]
    n_holes = len(holes(part))
    n_sec = len(section_candidates(part, primary))
    n_det = len(detail_regions(part, primary))
    return n_holes + n_sec + n_det


def _wall_reason(part):
    """Why `thinnest_wall` came back None, in the words the measurement used —
    never "unknown"."""
    try:
        from .inspect import thinnest_wall_detail
        return (thinnest_wall_detail(part) or {}).get("reason") \
            or "cecad.inspect.thinnest_wall_detail returned no measurement " \
               "and no reason"
    except Exception as e:                                    # noqa: BLE001
        return "the measurement could not run (%s: %s)" % (type(e).__name__, e)


def _filament_note(material, info):
    """A filament estimate is not a weighed part; absent mass is not zero."""
    grams=info.get('filament_g')
    try:
        grams=float(grams)
    except (TypeError,ValueError):
        grams=None
    if grams is None or not math.isfinite(grams) or grams<=0:
        mass='mass CANNOT DETERMINE; no positive model mass, qualify density or weigh'
    else:
        shown='%.1f'%grams if grams>=.1 else '%.3g'%grams
        mass='~%s g (shell/infill estimate, not weighed)'%shown
    layers=info.get('layers')
    layer_note=('%d modelled layers @ 0.2 mm'%layers if isinstance(layers,int) and layers>0
                else 'layer count CANNOT DETERMINE')
    return 'FILAMENT: %s, %s, %s'%(material,mass,layer_note)


def dfm_lines(part):
    """The print / DFM note block for `part`, MEASURED — orientation, thinnest
    wall against the two-perimeter floor, which small holes print undersize,
    which bores bridge, filament and layer count. Built from
    `printed.printability` and `inspect.holes`; every number comes off the
    solid so `verify_sheet` reads each line straight back."""
    from .printed import printability
    _ok, info = printability(part, verbose=False)
    bb = info["bbox"]
    tallest = bb[2] >= max(bb) - 1e-6
    lines = ["ORIENTATION: %s (%.0f x %.0f x %.0f mm)"
             % ("upright, Z-up" if tallest else "laid flat",
                bb[0], bb[1], bb[2])]
    # THE WALL, IN FULL PRECISION AND WITH A VERDICT. This line used to print
    # "THINNEST WALL: 0.03 mm (floor 0.80 mm)" and stop — two decimals, no
    # verdict, and the figure was the whole-solid RAY minimum, which at an edge
    # or a fillet run-out is a real distance through material and not a wall
    # anybody prints to. MEASURED 2026-09-03 over the microduck shelf: 11 of 21
    # parametric sheets printed a number below the floor, all of them prints
    # that succeed, beside a note elsewhere on the same sheet saying the number
    # is not a wall. Both figures now, each named, and the printable one — the
    # smallest neighbourhood-median thickness, `inspect.printable_wall_detail`
    # — carries the PASS / FAIL / CANNOT DETERMINE.
    floor = info["min_wall"]
    w = info.get("thinnest_wall")
    if w is not None:
        lines.append("THINNEST WALL, WHOLE SOLID (RAY MINIMUM): %.4f mm — a "
                     "distance through material, NOT a printable wall where "
                     "it falls on an edge, a fillet run-out or a chamfer tip. "
                     "Printability is judged on the next line." % w)
    else:
        lines.append("THINNEST WALL, WHOLE SOLID (RAY MINIMUM): CANNOT "
                     "DETERMINE — %s"
                     % _wall_reason(part))
    try:
        from .inspect import printable_wall_detail
        pw = printable_wall_detail(part) or {}
    except Exception as e:                                    # noqa: BLE001
        pw = {"mm": None, "reason": "the measurement could not run (%s: %s)"
                                    % (type(e).__name__, e)}
    if pw.get("mm") is None:
        lines.append("PRINTABLE MINIMUM WALL: CANNOT DETERMINE — %s. Floor is "
                     "%.4f mm (2 perimeters @ 0.4 mm nozzle, "
                     "cecad/printed.py:801). What settles it: a printed and "
                     "sectioned coupon of the thinnest feature."
                     % (pw.get("reason") or "no reason recorded", floor))
    else:
        pmm = float(pw["mm"])
        lines.append("PRINTABLE MINIMUM WALL: %.4f mm (smallest median wall "
                     "over a %.4f mm neighbourhood, cecad.inspect."
                     "printable_wall_detail) against a %.4f mm floor "
                     "(2 perimeters @ 0.4 mm nozzle): VERDICT %s%s"
                     % (pmm, float(pw.get("neigh_mm") or 0.0), floor,
                        "PASS" if pmm >= floor - 1e-9 else "FAIL",
                        "" if pmm >= floor - 1e-9 else
                        " — thicken this region or print it with a smaller "
                        "nozzle and say so on the route card."))
    hs = holes(part)
    small = sorted({round(h.d, 2) for h in hs if h.d < 2.0})
    if small:
        lines.append("SMALL HOLES \u00d8%s PRINT UNDERSIZE: drill to tapping size "
                     "and form-tap after printing; heat-set inserts for M2 "
                     "into PLA" % "/".join("%.2f" % d for d in small))
    n_horiz = sum(1 for h in hs if abs(h.axis[2]) < 0.1)
    if n_horiz:
        lines.append("%d horizontal bore(s) bridge at the crown: ream any "
                     "bearing or press-fit bore to size" % n_horiz)
    mat = getattr(part, "material", None) or "PLA"
    lines.append(_filament_note(mat,info))
    return lines


def build_sheet(part, size="A3", source=None, section=True, dim=True,
                views=None, scale=None, sec_rank=0, holes=True,
                hidden=True, radii=False, reference_iso=False,
                details=None, dfm=None, reference_image=None,
                reference_caption=None, mosaic=None, schedule=None):
    """One candidate sheet. `auto_sheet` calls this until one verifies.

    The manufacturing extras are opt-in and backward compatible: `hidden`
    False suppresses the dashed hidden-line forest (the section carries the
    internals instead); `radii` True dimensions every fillet the views draw;
    `reference_iso`, `details` and `dfm` add the isometric reference, the
    enlarged detail bubbles and the print/DFM note block.
    """
    vs, primary = choose_views(part)
    if views is not None:
        vs, primary = list(views), views[0]
    sh = Sheet(part, size=size, scale=scale, source=source)
    for v in vs:
        h = hidden.get(v, {}).get("hidden", True) \
            if isinstance(hidden, dict) else hidden
        sh.view(v, hidden=h, holes=holes, radii=radii)
    if isinstance(hidden, dict):
        for v in vs:
            w = hidden.get(v, {}).get("why")
            if w:
                sh.note("%s VIEW: %s." % (v.upper(), w))

    if dim:
        d = choose_dimension(part, primary)
        if d is not None:
            try:
                sh.dim_conn(primary, d[0], d[1], axis=d[2])
            except (KeyError, AttributeError):
                pass

    if section:
        sec = choose_section(part, primary, rank=sec_rank)
        if sec is not None:
            axis, coord, background = sec
            taken = [v.cell for v in sh.views if v.cell is not None]
            cell = section_cell(vs, primary, taken)
            # `on=None`, NOT the primary view. A cutting-plane line can
            # only be drawn on a view that sees the plane EDGE-ON, and
            # naming the primary view asks for it on a view that often
            # cannot. `Sheet.section` then redirects it correctly and
            # warns — "section A is parallel to view 'front', so its
            # cutting-plane line is on 'top' instead" — which was true
            # of 10 of the 84 sheets in the shipped packages. The
            # drawings were right; the request was wrong, and nobody
            # was reading the warning that said so. Left to choose,
            # sheets.py picks a view that can show it.
            sh.section("A", axis=axis, coord=coord, keep="min",
                       walls=2, cell=cell, background=background)

    if reference_iso:
        sh.reference_iso()
    if reference_image:
        sh.reference_image(reference_image, caption=reference_caption)
    if mosaic:
        sh.render_mosaic(mosaic)
    if schedule is not None:
        sh.feature_schedule(schedule["features"],
                            schedule.get("cannot_determine", ()),
                            general_tolerance=schedule.get("tolerance"),
                            census_note=schedule.get("note"))
    for d in (details or []):
        # the MEASURED reason this region earned a bubble travels with the
        # view, so the package reports what the paper actually carries
        sh.detail(primary, d["center"], d["radius"]).detail["why"] = d["why"]
    if dfm:
        sh.dfm_note(dfm)
    return sh, vs, primary


def auto_sheet(part, size=None, source=None, verbose=False,
               manufacturing=False, reference_image=None,
               reference_caption=None, mosaic=None, schedule=None):
    """A verified Sheet for `part`, or the best attempt with `.warnings` set.

    Returns (sheet, attempts) where attempts is the list of what was tried and
    what happened, so a package can report that a sheet needed three goes
    instead of quietly shipping the third one.

    `manufacturing=True` draws the shop sheet: hidden-line clutter suppressed,
    every radius dimensioned, an isometric reference, enlarged detail bubbles
    on the dense regions (`detail_regions`), a measured print/DFM note block,
    and A2 paper when the feature density earns it — all MEASURED.
    """
    mfg = _mfg_extras(part) if manufacturing else None
    return _search(part, size=size, source=source, stem=None, verbose=verbose,
                   mfg=mfg, reference_image=reference_image,
                   reference_caption=reference_caption, mosaic=mosaic,
                   schedule=schedule)


def auto_blueprint(part, stem, size=None, source=None, verbose=False,
                   manufacturing=False, reference_image=None,
                   reference_caption=None, dfm_extra=(), mosaic=None,
                   schedule=None):
    """Draw `part` to `stem`.dxf + `stem`.svg, verified. Returns a dict:

        {"dxf":, "svg":, "size":, "scale":, "views":, "verified":,
         "attempts": [...], "manufacturing":, "details":, "dfm":}

    `manufacturing=True` is the dense-part shop drawing — see `auto_sheet`.
    """
    os.makedirs(os.path.dirname(os.path.abspath(stem)) or ".", exist_ok=True)
    mfg = _mfg_extras(part) if manufacturing else None
    if mfg is not None and dfm_extra:
        # PROGRAMME FACTS THE PART CANNOT KNOW. `dfm_lines` measures the
        # solid; the tolerance basis, the machine and the filament this
        # product is actually made on are decisions of the programme, and
        # they belong on the sheet with their source named. Appended, never
        # substituted — a caller may not overwrite a measurement.
        mfg = dict(mfg, dfm=list(mfg["dfm"]) + [str(x) for x in dfm_extra])
    sh, attempts = _search(part, size=size, source=source, stem=stem,
                           verbose=verbose, mfg=mfg,
                           reference_image=reference_image,
                           reference_caption=reference_caption,
                           mosaic=mosaic, schedule=schedule)
    res = attempts[-1]
    out = {"dxf": res.get("dxf"), "svg": res.get("svg"),
           "pdf": res.get("pdf"),
           "size": sh.size, "scale": sh.scale,
           "views": [v.key for v in sh.views],
           "verified": res["verified"], "attempts": attempts,
           "sheet": sh, "manufacturing": bool(manufacturing),
           "reference_image": (os.path.abspath(reference_image)
                               if reference_image else None),
           # WHAT THE RENDER BAND ACTUALLY BOUGHT, in A3 rule 1's own units
           # (per cent of SHEET area), measured off the boxes that were laid
           # out — never the boxes that were asked for.
           "mosaic_tiles": sh.mosaic_facts(),
           "schedule_rows": len(sh._schedule),
           "schedule_cannot_determine": len(sh._schedule_cds)}
    if mfg is not None:
        out["hidden_lines"] = {k: v for k, v in mfg["hidden"].items()}
        # WHAT IS ON THE PAPER, not what was asked for. `Sheet._rescale_details`
        # drops a bubble that cannot be drawn bigger than the view it points
        # at, and a package that reported the requested list would claim a
        # detail the shop cannot find on the sheet.
        out["details"] = ["%s: %s" % (v.detail["letter"], v.detail.get("why", ""))
                          for v in sh.views if getattr(v, "detail", None)]
        out["details_requested"] = [d["why"] for d in mfg["details"]]
        out["details_dropped"] = list(getattr(sh, "_detail_dropped", []))
        out["dfm"] = list(mfg["dfm"])
        out["density"] = mfg["density"]
    return out


def _mfg_extras(part):
    """Measure everything the manufacturing sheet needs, once: the detail
    regions, the DFM note lines and the feature density that sizes the paper.
    """
    vs, primary = choose_views(part)
    return {"primary": primary,
            "details": detail_regions(part, primary),
            "dfm": dfm_lines(part),
            "hidden": hidden_choice(part, vs),
            "density": feature_density(part)}


#: What to give up, in order, when a sheet will not read back clean, as
#: (section, connector dimension, hole callouts + table).
#:
#: The drawing is worth keeping and the section is worth keeping, so the
#: connector dimension goes first. THE HOLE TABLE GOES NEXT, before the
#: section, because of parts like the clock's minute dial: 112 identical Ø1.4
#: tick slots are DECORATION, and calling out and tabulating every one of them
#: buries the sheet — its callouts landed on the title block at every size from
#: A3 to A1 and at every scale, 55 attempts, none of which could ever have
#: fitted. A machinist needs "112x Ø1.40 on a Ø56 circle" and the outline, not
#: 112 rows of coordinates. The section, which shows the tick DEPTH, survives.
#:
#: The fourth column is the DETAIL BUBBLES, and it is shed FIRST of all —
#: before even the connector dimension. A bubble is an enlargement of
#: something the sheet already draws and already dimensions, so losing one
#: costs legibility and no information; every other rung on this ladder costs
#: a number. It is still tried first on every paper size, so a sheet only ever
#: loses its details when no paper could hold them.
_GIVE_UP = ((True, True, True, True), (True, True, True, False),
            (True, False, True, False), (True, False, False, False),
            (False, False, False, False))

#: how many standard scales below the automatic one to try before reaching for
#: a bigger sheet. ONE. A crowded drawing is fixed by drawing one size smaller,
#: which is what a draughtsman does; escalating the paper first ships an A2 for
#: a 60 mm part. But shrinking further always "works" — fewer labels collide the
#: smaller you draw — and at two steps the 140 mm reference base plate verified
#: at 1:5, which is 28 mm of drawing on a sheet of paper. Past one step the
#: sheet is genuinely too small and the paper has to grow.
_STEPS_DOWN = 1

#: how many different cutting planes to try before changing the paper. Trying a
#: plane costs one sheet and often fixes what no sheet size can.
_SECTION_TRIES = 4

#: how many candidate planes to keep per axis, and how far apart two planes on
#: the same axis have to be to count as different drawings.
_PER_AXIS = 2
_PLANE_APART = 3.0


def _plan(ladder, n_sec, section_ok=True):
    """(section, dim, holes, size, sec_rank) in the order worth trying.

    Cheapest change first: a different cutting plane costs nothing and often
    fixes a collision that no sheet size can. Then bigger paper. Only then does
    the sheet start losing content — the connector dimension, then the section.
    """
    for section, dim, holes, details in _GIVE_UP:
        ranks = range(min(n_sec, _SECTION_TRIES)) if (section and section_ok) \
            else range(1)
        for sz in ladder:
            for rank in ranks:
                yield section, dim, holes, details, sz, rank


def _search(part, size=None, source=None, stem=None, verbose=False, mfg=None,
            reference_image=None, reference_caption=None, mosaic=None,
            schedule=None):
    ladder = [size] if size else list(LADDER)
    # a dense part is illegible at any A3 scale — start it on A2, MEASURED off
    # its own feature density, and keep A1 above for the densest.
    if mfg is not None and not size and mfg["density"] >= _A2_DENSITY:
        ladder = [s for s in LADDER if SHEETS[s][0] >= SHEETS["A2"][0]] or ["A2"]
    extras = (dict(hidden=mfg["hidden"], radii=True, reference_iso=True,
                   details=mfg["details"], dfm=mfg["dfm"])
              if mfg is not None else {})
    if reference_image:
        extras = dict(extras, reference_image=reference_image,
                      reference_caption=reference_caption)
    if mosaic:
        extras = dict(extras, mosaic=mosaic)
    if schedule is not None:
        extras = dict(extras, schedule=schedule)
    # A SHEET CARRYING BOTH BANDS STARTS ON BIGGER PAPER. The render mosaic
    # takes a measured share of the frame height and the feature schedule
    # takes whatever its rows need; on A3 what is left of the frame is a
    # strip the orthographic block cannot be drawn in at any scale, and the
    # search would prove that one full build at a time. Measured on
    # `part:microduck-banana-pcb-locker`, 23 features: A3 leaves 61 mm.
    if (mosaic or schedule) and not size:
        ladder = [s for s in LADDER if SHEETS[s][0] >= SHEETS["A1"][0]] or ["A1"]
    attempts = []
    best = None

    # how many different cutting planes to try before changing the paper. A
    # sheet can fail because the cutting-plane letter lands exactly where a
    # hole callout must go, and no sheet size fixes that — the letter and the
    # callout scale together. A different plane does.
    n_sec = max(1, len(section_candidates(part, choose_views(part)[1])))

    # A DIFFERENT CUTTING PLANE ONLY FIXES A FAILURE THE CUTTING PLANE CAUSES.
    # Measured 2026-09-02 on `part:microduck-shin`: A2 failed four ranks in a
    # row with the identical reason — a note line printed over the section
    # letter — and each rank costs a full build, write and read-back. Eight of
    # its eleven attempts were that. When the reason does not move between two
    # ranks at the same paper size, the plane is not what is wrong: stop trying
    # planes there and grow the paper.
    tried, spent = {}, set()
    # ...AND BIGGER PAPER ONLY FIXES A FAILURE THE PAPER CAUSES. The rule
    # above stops trying cutting PLANES when the reason does not move; this is
    # its sibling for paper SIZE. MEASURED 2026-09-03 on
    # `part:microduck-foot-left`: 31 attempts, 2 754.5 s, every one of them
    # A3/A2/A1 at six different scales, and every one failing with the
    # IDENTICAL first reason ("front: overall X = 40.09 — no dimension reading
    # 40.09 on the sheet"). No sheet size could have fixed it — the sheet was
    # printing the ink's extent where the solid measures 0.01 mm more — and
    # the search spent three quarters of an hour proving that one size at a
    # time. When one reason survives three DIFFERENT paper sizes, this content
    # combination is not a layout problem: stop and report it.
    heads, dead = {}, set()
    for section, dim, holes, want_det, sz, sec_rank in _plan(
            ladder, n_sec, section_ok=True):
        if extras and not want_det:
            extras = dict(extras, details=[])
        key = (section, dim, holes, want_det, sz)
        content = (section, dim, holes, want_det)
        if key in spent or content in dead:
            continue
        for step in range(_STEPS_DOWN + 1):
            scale = None
            if step:
                # one step below whatever the PREVIOUS attempt drew at, so
                # two steps down is two single steps, not a double one
                scale = _step_down(attempts[-1].get("scale"), 1)
                if scale is None:
                    break                     # nothing smaller worth printing
            sh, _, _ = build_sheet(part, size=sz, source=source,
                                   section=section, dim=dim, scale=scale,
                                   sec_rank=sec_rank, holes=holes, **extras)
            rec = dict(size=sz, section=section, dim=dim, holes=holes,
                       details=bool(extras.get("details")) if extras else False,
                       asked=scale, sec_rank=sec_rank, verified=False,
                       reason="")

            if stem is None:
                sh._layout()
                rec["scale"] = sh.scale
                attempts.append(rec)
                if _scale_ok(sh) or sz == ladder[-1]:
                    return sh, attempts
                rec["reason"] = f"{sh.scale[0]}:{sh.scale[1]} is too small"
                best = best or (sh, rec)
                break

            out = sh.write(stem, quiet=not verbose)
            rec.update(dxf=out["dxf"], svg=out["svg"], pdf=out.get("pdf"),
                       scale=sh.scale)
            attempts.append(rec)

            if not _scale_ok(sh):
                rec["reason"] = (f"{sh.scale[0]}:{sh.scale[1]} is too small "
                                 f"to measure off")
                best = best or (sh, rec)
                break                         # smaller will not help; grow it
            ok, failed = _verify(sh, out["svg"], part, verbose)
            if ok:
                rec["verified"] = True
                return sh, attempts
            # name the checks that failed. "the sheet disagreed with the
            # solid" is not a bug report: the whole point of reading the
            # drawing back is to say WHICH number was wrong.
            rec["failed"] = failed
            rec["reason"] = "; ".join(failed[:3]) or "verification failed"
            best = best or (sh, rec)
            head = (failed or ["?"])[0].split("—")[0].strip()
            if tried.get(key) == head:
                spent.add(key)           # this plane is not the problem
                rec["plane_ruled_out"] = True
            tried[key] = head
            seen_sizes = heads.setdefault(content, {}).setdefault(head, set())
            seen_sizes.add(sz)
            if len(seen_sizes) >= 3:
                dead.add(content)        # nor is the paper
                rec["paper_ruled_out"] = (
                    "the same failure at %s — %s: this is not a layout "
                    "problem and a bigger sheet cannot fix it"
                    % ("/".join(sorted(seen_sizes)), head))

    # Nothing read back clean. Re-emit the first attempt so the files on disk
    # are the ones being reported on, and say so rather than shipping quietly.
    sh, rec = best
    if stem is not None:
        out = sh.write(stem, quiet=True)
        rec = dict(rec, dxf=out["dxf"], svg=out["svg"], pdf=out.get("pdf"))
    sh.warnings.append("no strategy produced a sheet that reads back clean")
    attempts.append(dict(rec, final=True, verified=False))
    return sh, attempts


def _verify(sh, svg, part, verbose):
    """(ok, [failing check names]).

    `verify_sheet` returns a bool and prints its detail, so the detail is
    captured off its own output rather than duplicated here — one description
    of each check, in the module that owns it.
    """
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with redirect_stdout(buf):
        ok = verify_sheet(sh, svg, part, verbose=True)
    text = buf.getvalue()
    if verbose:
        print(text, end="")
    failed = [ln.split("[FAIL]", 1)[1].strip()
              for ln in text.splitlines() if "[FAIL]" in ln]
    return bool(ok), failed


def _step_down(scale, steps):
    """`steps` entries further down the ISO 5455 series, or None if that is
    smaller than anything worth measuring off."""
    from .sheets import SCALES
    if scale is None or tuple(scale) not in SCALES:
        return None
    i = SCALES.index(tuple(scale)) + steps
    if i >= len(SCALES):
        return None
    cand = SCALES[i]
    return cand if (cand[0] / float(cand[1])) >= MIN_SCALE - 1e-9 else None


def _scale_ok(sh):
    if sh.scale is None:
        return False
    n, d = sh.scale
    return (n / float(d)) >= MIN_SCALE - 1e-9


# ==========================================================================
def self_test(verbose=True):
    """Draw the totem's parts with nobody choosing anything, and check them.

    The point is not that ten sheets come out — it is that they come out
    verified, at a scale worth printing, with the same view and section
    choices a person would have made. The expectations below were written
    against the hand-authored sheets in examples/blueprints/.
    """
    import sys
    root = os.environ.get("CAD_ROOT", ".")
    sys.path.insert(0, os.path.join(root, "examples", "kinetic_totem"))
    import design                                          # noqa: E402

    # `views` is the set of view counts a competent drawing of this part could
    # have, not the one the hand-drawn sheet in examples/blueprints happened to
    # use. Three views of a chunky square part is a judgement call, not a bug;
    # a section through solid bar is a bug, and a sheet that does not read back
    # is a bug. The test asserts the second two and leaves the first open.
    want = [
        # part builder                views    section   sheet must stay
        (design.build_foot,           (2, 3),  True,     ("A3",)),
        (design.build_bearing_block,  (3,),    True,     ("A3",)),
        (design.build_rod,            (2,),    True,     ("A3",)),
        (design.build_rocker,         (2,),    True,     ("A3",)),
        (design.build_tower,          (3,),    True,     ("A3",)),
        (design.build_motor_mount,    (3,),    True,     ("A3",)),
        (design.build_layshaft,       (2,),    False,    ("A3",)),   # solid bar
        # WAS A2, now A3 at 1:2, and checked by eye as well as by the
        # read-back. Both reasons it needed A2 were F19: at 1:1 the annotation
        # ran 40 mm outside the frame, and at 1:2 "30.00" printed over
        # "FRONT VIEW". `sheets._annotate` now clamps the callout stack and
        # the view label to the paper that is actually free and slides the
        # block in when a label falls off, so neither happens and the drawing
        # reads on A3. Smaller paper for the same drawing is the direction
        # this test's own note asks for.
        (design.build_mast,           (3,),    True,     ("A3",)),
        (design.build_spinner,        (2, 3),  True,     ("A3",)),
    ]
    tmp = os.path.join(root, "out", "autosheet_selftest")
    os.makedirs(tmp, exist_ok=True)
    checks = []
    for build, n_views, want_sec, sizes in want:
        p = build()
        r = auto_blueprint(p, os.path.join(tmp, p.name), verbose=False)
        n = len([v for v in r["views"] if not v.startswith("SEC")])
        has_sec = any(v.startswith("SEC") for v in r["views"])
        checks.append((f"{p.name}: reads back clean", r["verified"],
                       (r["attempts"][-1] or {}).get("reason", "")))
        checks.append((f"{p.name}: {n} views", n in n_views,
                       f"wanted one of {n_views}, drew {n}"))
        checks.append((f"{p.name}: section {'yes' if want_sec else 'no'}",
                       has_sec == want_sec,
                       f"wanted {want_sec}, got {has_sec}"))
        checks.append((f"{p.name}: scale {r['scale'][0]}:{r['scale'][1]}",
                       _ok_scale_tuple(r["scale"]), "smaller than 1:5"))
        checks.append((f"{p.name}: fits {'/'.join(sizes)}",
                       r["size"] in sizes,
                       f"needed {r['size']}, wanted one of {sizes} — growing "
                       f"the paper is only right when the sheet genuinely "
                       f"cannot hold the drawing"))

    bad = [(n, d) for n, ok, d in checks if not ok]
    if verbose:
        print(f"\n  AUTOSHEET SELF-TEST — {len(checks)} checks on "
              f"{len(want)} parts, nothing chosen by hand")
        for n, ok, d in checks:
            if not ok:
                print(f"    [FAIL] {n:44s} — {d}")
        print(f"    {len(checks) - len(bad)}/{len(checks)} passed")
    return not bad


def _ok_scale_tuple(s):
    n, d = s
    return (n / float(d)) >= MIN_SCALE - 1e-9


if __name__ == "__main__":
    self_test()
