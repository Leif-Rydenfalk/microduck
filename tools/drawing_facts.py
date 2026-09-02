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
    "TOLERANCE BASIS, OUTSOURCED: JLC3DP +/-0.3 mm FDM (jlc3dp.com, "
    "ce-machines/farm-jlc3dp); Hubs +/-0.5%, floor +/-0.5 mm "
    "(hubs.com/3d-printing/, ce-machines/farm-hubs). Apply the route's "
    "figure, not both. The +/-0.2 mm in cecad/machining.py fdm is a repo "
    "planning constant with no vendor cite and is NOT used here. One printed "
    "and measured coupon closes this note.",
    "NO ISO 286 CLASS IS DECLARED ON ANY BORE: FDM cannot be sized to one "
    "(H7/p6 at O3 is a 0.010 mm band). REAM bearing and press-fit bores after "
    "printing.",
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


def builder_source(slug):
    """The text of the folder's cad/part.py, or "" — the thing that decides
    what kind of document the part can carry."""
    for rel in ("current/cad/part.py", "cad/part.py"):
        p = os.path.join(ROOT, "ce-parts", slug, rel)
        if os.path.exists(p):
            return open(p, encoding="utf-8").read()
    return ""


#: tokens that mean "this builder LOADS a published mesh" rather than
#: "this builder constructs a solid". `meshshelve` writes the loader;
#: `from_mesh` is the call it makes.
_MESH_TOKENS = ("meshshelve", "from_mesh", "Part.from_mesh")


def mesh_geometry_of(slug):
    """Absolute path of the mesh a loader-backed part prints, or None."""
    src = builder_source(slug)
    for line in src.splitlines():
        if line.strip().startswith("GEOMETRY"):
            rel = line.split("=", 1)[-1].strip().strip('"\'')
            p = os.path.join(ROOT, "ce-parts", slug, rel)
            return p if os.path.exists(p) else None
    base = os.path.join(ROOT, "ce-parts", slug, "geometry")
    if os.path.isdir(base):
        for f in sorted(os.listdir(base)):
            if f.lower().endswith((".stl", ".step", ".stp")):
                return os.path.join(base, f)
    return None


def classify(slug, part=None):
    """("drawing" | "print-sheet", why) — MEASURED, in this order:

      1. the builder LOADS a mesh (meshshelve / from_mesh) -> print sheet,
         because §A.3 forbids dimensioning a decimated triangulation;
      2. the built shape has NO solids -> print sheet, for the same reason
         one level down: a shell has no measurable internal feature;
      3. otherwise -> drawing.

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
    return ("drawing", "cad/part.py constructs a parametric solid")


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
