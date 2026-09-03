"""The facts every microduck sheet carries that the SOLID cannot know, each
with the file, page or URL it came from.

Imported by tools/draw_part.py and tools/gen_drawings_index.py. Plain stdlib —
no FreeCAD — so the index generator can read it without the kernel.

THE TOLERANCE BASIS. `docs/MANUFACTURING-REQUIREMENTS.md` and the night's
brief both require a stated basis and forbid a guessed number. Measured
2026-09-02, three sources, in the order a shop would ask:

 1. THE FARM'S OWN MACHINES DECLARE NONE.
    ce-machines/bambu-h2s-0938BC612100527/capabilities.json  record.tolerance_mm = null
    ce-machines/bambu-h2s-0938BC5C1800794/capabilities.json  record.tolerance_cite =
        "CANNOT DETERMINE — no coupon printed yet"
    ce-machines/bambu-h2d-0947BJ610900152/capabilities.json  record.tolerance_cite =
        "CANNOT DETERMINE — no coupon printed and measured on this machine"
    (all eight in-house Bambu rows read the same way.)

 2. THE VENDOR PUBLISHES NONE EITHER. Bambu Lab's own H2D Pro technical
    specification (the PDF linked from bambulab.com, fetched 2026-09-02 from
    dynamism.com/learn/wp-content/uploads/2025/10/Bambu-Lab-H2D-Pro-Tech-Spec.pdf)
    lists Build Volume, Nozzle, Speed, Chassis, Sensors and 40 other rows and
    carries NO dimensional-accuracy, tolerance or precision line at all. The
    ±0.05 mm figures in circulation are review measurements on a calibration
    cube, not a specification anybody stands behind.

 3. THE OUTSOURCED ROUTES DO PUBLISH ONE, and those are cited numbers a shop
    can be held to:
    ce-machines/farm-jlc3dp/capabilities.json  per_process.fff.tolerance_mm = 0.3
        cite: https://jlc3dp.com/  "±0.3mm" (MJF, SLM, FDM, SLS)
    ce-machines/farm-hubs/capabilities.json    per_process.3dp_fdm.accuracy =
        "±0.5%, floor ±0.5 mm"
        cite: https://www.hubs.com/3d-printing/  FDM "± 0.5% with a lower
        limit: ± 0.5 mm"

So the sheet states CANNOT DETERMINE for the in-house route and prints the two
cited outsourced figures beside it. `cecad/machining.py` PROCESSES["fdm"]
.tolerance_mm is 0.2 and is a REPO PLANNING CONSTANT with no vendor cite; it is
named on the sheet as that and is not used as the general tolerance.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSHOP = "/Users/leifrydenfalk/dev/ce-workshop"

#: what `Sheet._fit_notes` prints as "GENERAL TOLERANCE <this> UNLESS STATED."
#: Short on purpose — the basis is three note lines and does not fit a caption.
GENERAL_TOLERANCE = "CANNOT DETERMINE — SEE PRINT / DFM NOTES"

#: appended to the measured print/DFM block on every parametric sheet
TOLERANCE_DFM = (
    "TOLERANCE BASIS, IN-HOUSE: CANNOT DETERMINE. Every Bambu on this farm "
    "records tolerance_mm: null, cite \"no coupon printed and measured on this "
    "machine\" (ce-machines/bambu-h2s-*, bambu-h2d-*/capabilities.json, read "
    "2026-09-02), and Bambu Lab's own H2D Pro spec sheet carries no "
    "dimensional-accuracy line. DIMENSIONS HERE ARE NOMINAL AS MODELLED.",
    "TOLERANCE BASIS, OUTSOURCED: JLC3DP \u00b10.3 mm FDM (jlc3dp.com, "
    "ce-machines/farm-jlc3dp); Hubs \u00b10.5%, floor \u00b10.5 mm "
    "(hubs.com/3d-printing/, ce-machines/farm-hubs). Apply the route's "
    "figure, not both. The \u00b10.2 mm in cecad/machining.py fdm is a repo "
    "planning constant with no vendor cite and is NOT used here. One printed "
    "and measured coupon closes this note.",
    "NO ISO 286 CLASS IS DECLARED ON ANY BORE: FDM cannot be sized to one "
    "(H7/p6 at \u00d83 is a 0.010 mm band). REAM bearing and press-fit bores "
    "after printing.",
)


def part_record(slug):
    """The part's own component.json `record`, or {}."""
    p = os.path.join(ROOT, "ce-parts", slug, "component.json")
    if not os.path.exists(p):
        return {}
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:                                         # noqa: BLE001
        return {}
    r = d.get("record")
    return r if isinstance(r, dict) else {}


def builder_path(slug):
    """Absolute path of the folder's cad/part.py, or None.

    `current/` is a SYMLINK to the selected iteration, so the file it resolves
    to lives under `iterations/<version>/` — and every relative path inside
    that builder (its `GEOMETRY = "geometry/jaw.stl"`) is relative to THAT
    directory, not to the slug folder. Resolving the symlink is what makes
    `mesh_geometry_of` find the mesh; joining the slug folder does not.
    """
    for rel in ("current/cad/part.py", "cad/part.py"):
        p = os.path.join(ROOT, "ce-parts", slug, rel)
        if os.path.exists(p):
            return os.path.realpath(p)
    return None


def builder_source(slug):
    """The text of the folder's cad/part.py, or "" — the thing that decides
    what kind of document the part can carry."""
    p = builder_path(slug)
    return open(p, encoding="utf-8").read() if p else ""


#: tokens that mean "this builder LOADS a published mesh" rather than
#: "this builder constructs a solid". `meshshelve` writes the loader;
#: `from_mesh` is the call it makes.
_MESH_TOKENS = ("meshshelve", "from_mesh", "Part.from_mesh")


def mesh_geometry_of(slug):
    """Absolute path of the mesh a loader-backed part prints, or None.

    Resolved exactly the way the builder resolves it — `ROOT` in a
    `meshshelve` loader is `os.path.dirname(os.path.dirname(part.py))`, i.e.
    the ITERATION folder — so this finds the same bytes the part is built
    from. Joining `ce-parts/<slug>/geometry/...` finds nothing: measured
    2026-09-02, all four microduck mesh parts keep their STL under
    `iterations/v0.0.1/geometry/`, and the print sheet was about to print
    "CANNOT DETERMINE - file not on disk" beside a file that is on disk.
    """
    bp = builder_path(slug)
    if bp is None:
        return None
    base = os.path.dirname(os.path.dirname(bp))       # the iteration folder
    for line in builder_source(slug).splitlines():
        if line.strip().startswith("GEOMETRY"):
            rel = line.split("=", 1)[-1].strip().strip('"\'')
            p = os.path.join(base, rel)
            if os.path.exists(p):
                return p
    for d in (os.path.join(base, "geometry"),
              os.path.join(ROOT, "ce-parts", slug, "geometry")):
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                if f.lower().endswith((".stl", ".step", ".stp")):
                    return os.path.join(d, f)
    return None


def classify(slug, part=None):
    """("drawing" | "print-sheet", why) — MEASURED, in this order:

      1. the builder LOADS a mesh (meshshelve / from_mesh) -> print sheet,
         because §A.3 forbids dimensioning a decimated triangulation;
      2. the built shape has NO solids -> print sheet, for the same reason
         one level down: a shell has no measurable internal feature;
      3. the solid has NOTHING TO DIMENSION (no hole, no arc radius in the
         leaderable band) and an outline nobody can read (> EDGE_FOREST
         visible edges in the primary view) -> print sheet; see
         `_seam_forest`, which measures both halves;
      4. otherwise -> drawing.

    The component.json `origin` is reported but does not decide: measured
    2026-09-02, `microduck-trunk-shell-left` is `origin: vendor` and its
    builder is a 355-line parametric rebuild with every number sourced to the
    probe that measured it — a real drawing, mislabelled by the record.
    """
    src = builder_source(slug)
    hit = [t for t in _MESH_TOKENS if t in src]
    if hit:
        return ("print-sheet",
                "cad/part.py is a published-mesh loader (%s); a decimated "
                "triangulation carries no dimension a shop can work to "
                "(docs/MANUFACTURING-REQUIREMENTS.md A.3)" % ", ".join(hit))
    if part is not None:
        shape = getattr(part, "shape", None) or getattr(part, "Shape", None)
        n = len(getattr(shape, "Solids", []) or [])
        if n == 0:
            return ("print-sheet",
                    "the builder returned %d solids (an open shell), so no "
                    "internal feature can be measured off it"
                    % n)
        forest = _seam_forest(part)
        if forest is not None:
            return ("print-sheet", forest)
    return ("drawing", "cad/part.py constructs a parametric solid")


#: Visible projected edges in the primary view above which the OUTLINE is the
#: document. See `_seam_forest`.
EDGE_FOREST = 300


def _seam_forest(part):
    """The reason this solid cannot carry a DIMENSIONED drawing, or None.

    §A.3 of docs/MANUFACTURING-REQUIREMENTS.md refuses a drawing off geometry
    that has no dimension a shop can work to, and states the case it was
    written for (a decimated vendor mesh). MEASURED 2026-09-03, there is a
    second case on this shelf and it is worse, because it looks like a
    drawing: `part:microduck-sole-left` is a parametric solid whose floor is
    lofted station to station through a measured 27 x 31 table
    (ce-parts/microduck-sole-left/current/cad/part.py FLOOR_ZB), so it has
    1363 visible edges in its top view — against 131 for `microduck-shin`, 78
    for `microduck-trunk-base`, 4 for `microduck-speaker` (TechDraw.projectEx,
    counted). It also has ZERO holes and ZERO arc radii in the leaderable
    band, so there is nothing on it to dimension and 1363 lines to draw: the
    sheet that shipped on 2026-09-03 carried exactly three numbers over a
    forest of seams, which is precisely the "unusable detail ... random lines"
    §A.1-A.2 orders removed.

    That part is made by printing its mesh, and the document it needs is the
    PRINT SHEET: envelope, orientation, support, material and the file. The
    rule is MEASURED on the solid, never chosen per part — nothing to
    dimension AND an outline nobody can read.
    """
    try:
        from cecad import inspect as _ins
        from cecad.drawing import project
        from cecad.autosheet import choose_views
    except Exception:                                         # noqa: BLE001
        return None
    try:
        if len(_ins.holes(part)):
            return None
        if len([o for o in _ins.arc_radii(part) if 0.2 <= float(o.r) <= 60.0]):
            return None
        primary = choose_views(part)[1]
        vis, _hid = project(part, primary)
        n = len(vis)
    except Exception:                                         # noqa: BLE001
        return None
    if n <= EDGE_FOREST:
        return None
    return ("MEASURED off the solid: 0 holes, 0 arc radii in the R0.2..R60 "
            "band — nothing to dimension — and %d visible edges in the '%s' "
            "view (TechDraw.projectEx), against 4-131 for a clean shop view "
            "on this shelf. The outline is a forest of construction seams "
            "from a station-to-station loft through a measured table, not "
            "features to manufacture, so a dimensioned drawing off it would "
            "be the 'unusable detail / random lines' "
            "docs/MANUFACTURING-REQUIREMENTS.md A.1-A.2 forbids. This part is "
            "made by printing its geometry." % (n, primary))


_R_TOKEN = re.compile(r"\bR(\d+(?:\.\d+)?)\b")


def design_radii(slug):
    """Every `R<number>` the part's OWN builder names, in mm, sorted.

    MEASURED 2026-09-03: `ce-parts/microduck-sole-left/current/cad/part.py`
    lines 25-26 name "heel arc R7.2, toe arc R6.9, side fillets R7.9" and
    `cecad.inspect.arc_radii` finds ZERO arcs in the R0.2..R60 band on the
    solid those lines build — because the surface is a loft through a measured
    27 x 31 station table, so the blends exist as sampled points and not as
    circular edges. Neither fact is wrong and the sheet has to carry both, or
    a reader comparing the builder to the paper concludes the drawing dropped
    three radii. This finds the first fact; `arc_radii` measures the second.
    """
    src = builder_source(slug)
    out = {float(m) for m in _R_TOKEN.findall(src)}
    # A HANDED PART INHERITS ITS TWIN'S NUMBERS. `microduck-sole-right`'s
    # builder is eleven lines that import the left sole's module and flip
    # HAND (measured mirror, p95 0.002 mm, stated in its own docstring), so
    # its radii live in the file it imports. Reading only its own text would
    # report "none named" for a part whose blends are the left sole's.
    m = re.search(r'"([^"]*microduck-[a-z0-9-]+)"\s*,\s*"iterations"', src)
    if not m and "microduck-" in src:
        m = re.search(r'\.\./(microduck-[a-z0-9-]+)/', src)
    if m and m.group(1) != slug:
        twin = os.path.basename(m.group(1))
        if twin != slug:
            out |= {float(x) for x in
                    _R_TOKEN.findall(builder_source(twin))}
    return sorted(out)


#: appended to a sheet for a BOUGHT part we merely modelled
VENDOR_DFM = (
    "THIS IS OUR MODEL OF A BOUGHT PART, NOT A PART WE MAKE. The solid was "
    "built parametrically in this repo from the vendor's published figures; "
    "the vendor's own drawing governs every dimension, and this sheet exists "
    "so the assembly can be checked against a real envelope. Do not send it "
    "to a shop as a part to manufacture. Its component.json states "
    "origin: vendor and names the source it was measured from.",
)


def is_bought(slug):
    """True when the part's own record says `origin: vendor` — a part we buy,
    whatever its builder does."""
    return (part_record(slug).get("origin") or "").lower() == "vendor"
