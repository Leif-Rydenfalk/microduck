"""microduck — the whole robot as ONE deliverable design (GOAL.md rung 6).

    bin/deliver ce-designs/microduck/design.py --zip     # the package
    bin/cad ce-designs/microduck/design.py               # just build it

WHY THIS FILE EXISTS. `bin/deliver` consumes a `cecad.pipeline.Registry`
(`system()` returning a BUILT one); the triad shelf exposes
`assembly:microduck` through `cecad.triad.load()`, which returns an
Assembly — one type short of what deliver needs (bin/_refsubject.py names
this exact gap and exits 4 on a bare ref). This file is the bridge: a
one-component Registry whose builder IS `triad.load('assembly:microduck')`.
Geometry is never re-derived here — every solid comes off the shelf, either
a PASSed parametric rebuild or Pollen's own published mesh (the fallback
the assembly builder reports by name in its notes).

WHAT IS ADDED HERE, AND WHY IT IS LEGITIMATE. The delivery standard reads
`material` and `blueprint.describe(category=, process=)` off every placed
part. The parametric part builders set material but none call describe();
the mesh-fallback parts come back as bare `Part.from_mesh` objects with the
from_mesh DEFAULT material ("PLA") — right for Pollen's printed shells,
WRONG for a steel bearing or a Li-ion pack. ANNOT below stamps those facts
on, sourced from each part's own ce-parts/<slug>/component.json record and
docs/PARTS.md — a re-statement of the shelf, not an invention. Nothing
already declared is overwritten.
"""
import os
import sys

# The triad roots this design reads its parts from. Set defensively so the
# subprocesses deliver spawns (bin/manual re-runs this file) resolve too.
_DESIGN_ROOT = os.path.dirname(os.path.abspath(__file__))
_WORKSHOP = os.path.dirname(os.path.dirname(_DESIGN_ROOT))
os.environ.setdefault("CE_TRIAD_ROOT", _DESIGN_ROOT + ":" + _WORKSHOP)

from cecad.pipeline import Registry

N_PLACEMENTS = 70   # placements.json record.rows — the datum this build must reproduce

# --------------------------------------------------------------------------
# What each part IS, for the standard: material (only where the shelf object
# carries none or a from_mesh default that is wrong), category (what
# separates a part we print from a catalogue item we buy — release.py's
# NO_DRAWING and manual.py's BOUGHT_CATEGORIES read it), and the process or
# standard a supplier quotes against. Keys are Part.name as built: the slug
# names the parametric builders use, plus the raw MESH names the assembly's
# vendor-mesh fallback uses for the folders whose part.py is still a stub.
# Sources: ce-parts/<slug>/component.json, docs/PARTS.md, SPEC.md.
# --------------------------------------------------------------------------
_PLA = dict(category="bracket", process="FDM, PLA")
_SHELL = dict(category="shell", process="FDM, PLA")
_PLATE = dict(category="plate", process="FDM, PLA")
_TPU = dict(category="cover", process="FDM, TPU")

ANNOT = {
    # --- printed, parametric rebuilds (material already set by part.py) ---
    "microduck-shin": _PLA,
    "microduck-ankle-left": _PLA,
    "microduck-ankle-right": _PLA,
    "microduck-banana-pcb-locker": _PLA,
    "microduck-bearing-roll": _PLA,
    "microduck-hip-bracket": _PLA,
    "microduck-power-support": _PLATE,
    "microduck-trunk-base": _PLATE,
    "microduck-upper-leg-left": _PLA,
    "microduck-upper-leg-right": _PLA,
    "microduck-upper-leg-rigidity-plate": _PLATE,
    "microduck-yaw2roll": _PLA,
    # --- printed, mesh-backed vendor parts (Pollen's own STL, printed) ----
    "microduck-foot-left": _PLA,
    "microduck-foot-right": _PLA,
    "microduck-jaw": _SHELL,
    "microduck-motor-support": _PLA,
    "microduck-neck-pitch-bracket": _PLA,
    "microduck-neck-plate": _PLATE,
    "microduck-top-head-shell": _SHELL,
    "microduck-trunk-shell-left": _SHELL,
    "microduck-trunk-shell-right": _SHELL,
    "microduck-yaw-roll-motion": dict(category="linkage",
                                      process="FDM, PLA"),
    # mesh-name fallbacks for the printed folders whose part.py is a stub
    "ankle_right": dict(material="PLA", **_PLA),
    "top_head_shell": dict(material="PLA", **_SHELL),
    "bottom_head_shell": dict(material="PLA", **_SHELL),
    "microduck-bottom-head-shell": _SHELL,
    "face_part": dict(material="PLA", **_SHELL),
    "microduck-face-part": _SHELL,
    "noenoeil": dict(material="PLA", category="ring", process="FDM, PLA"),
    "microduck-eye-ring": dict(category="ring", process="FDM, PLA"),
    # --- printed, TPU -----------------------------------------------------
    "microduck-jaw-soft": _TPU,
    "microduck-soft-mouth-top": _TPU,
    "microduck-sole-left": dict(category="sole", process="FDM, TPU"),
    "microduck-sole-right": dict(category="sole", process="FDM, TPU"),
    # --- bought: catalogue items, never drawn, never printed --------------
    "seeed_bearing__configuration_default": dict(
        material="GCr15 bearing steel", category="bearing",
        standard="deep-groove ball bearing 15x10x3 (docs/PARTS.md; Seeed "
                 "listing per Pollen's BOM)"),
    "seeed_bearing__configuration__22x16x4": dict(
        material="GCr15 bearing steel", category="bearing",
        standard="deep-groove ball bearing 22x16x4 (docs/PARTS.md; Seeed "
                 "listing per Pollen's BOM)"),
    "xl330-m288-t": dict(category="motor",
                         standard="ROBOTIS Dynamixel XL330-M288-T"),
    "xl330": dict(material="PA", category="motor",
                  standard="ROBOTIS Dynamixel XL330-M288-T"),
    "radxa-zero-3w": dict(category="electronics",
                          standard="Radxa ZERO 3W (RAD-DOC-0084)"),
    "pcb__raspberry_pi_zero_2_w": dict(
        material="FR4", category="electronics",
        standard="Radxa ZERO 3W (RAD-DOC-0084)"),
    "microduck-robot-hat-pcb": dict(
        category="electronics",
        process="PCB fab, FR4 — gerbers in electronics/ (rung 4)"),
    "elec_rpi_robot_hat_pcb": dict(
        material="FR4", category="electronics",
        process="PCB fab, FR4 — gerbers in electronics/ (rung 4)"),
    "microduck-speaker": dict(
        category="electronics",
        standard="bought speaker unit (docs/ELECTRONICS-AND-SOFTWARE.md)"),
    "microduck-m12-lens": dict(category="electronics",
                               standard="M12 board lens (bought)"),
    "lens": dict(material="glass/aluminium (bought M12 lens)",
                 category="electronics", standard="M12 board lens (bought)"),
    "microduck-m12-lens-holder": dict(
        category="electronics", standard="M12 lens holder (bought)"),
    "m12_lens_holder": dict(material="aluminium (bought)",
                            category="electronics",
                            standard="M12 lens holder (bought)"),
    "np_f970": dict(material="Li-ion cells in ABS case (bought pack)",
                    category="electronics",
                    standard="Sony NP-F550/F970-compatible pack"),
}


def _annotate(asm):
    """Stamp material / category / process from ANNOT onto every distinct
    part in the assembly. setdefault semantics: a fact the builder already
    declared wins; only ABSENT facts (and from_mesh's default 'PLA' on the
    named bought parts) are filled in."""
    done = set()
    for _label, part, _shape, _color in asm.items:
        if id(part) in done:
            continue
        done.add(id(part))
        a = ANNOT.get(getattr(part, "name", ""))
        if not a:
            continue
        if a.get("material") and getattr(part, "material", "") in ("", "PLA"):
            # only the mesh-fallback names carry a material override, and for
            # those "PLA" is from_mesh's default, not a declaration
            if "material" in a:
                part.material = a["material"]
        bp = part.blueprint
        meta = bp.meta
        if not meta.get("category") and a.get("category"):
            bp.describe(category=a["category"])
        if not (meta.get("process") or meta.get("standard")):
            if a.get("process"):
                bp.describe(process=a["process"])
            elif a.get("standard"):
                bp.describe(standard=a["standard"])
        if not meta.get("material"):
            bp.describe(material=part.material)


def build_microduck(deps=None):
    """The shelf assembly, loaded through the triad door and annotated."""
    import FreeCAD as App
    import cecad.triad as triad
    doc = App.newDocument("microduck_deliver")
    asm = triad.load(doc, "assembly:microduck")
    _annotate(asm)
    return asm


def check_microduck(obj):
    """The check this design can honestly make CHEAPLY: the build reproduced
    placements.json — all N_PLACEMENTS instances placed, zero reported
    missing, every placed solid non-empty. Interference/connectivity of the
    zero-pose MJCF port is graded by the assembly folder's own evidence
    (ce-assemblies/microduck, rung 2), not re-run per package build."""
    if obj is None:
        return False, "builder returned nothing"
    items = list(obj.items)
    if len(items) != N_PLACEMENTS:
        return False, (f"{len(items)} of {N_PLACEMENTS} placements built — "
                       f"placements.json not reproduced")
    for note in getattr(obj, "notes", []):
        s = str(note)
        if "missing" in s and "missing 0" not in s:
            return False, f"assembly reports missing parts: {s[:200]}"
    empty = [lb for lb, _p, sh, _c in items
             if sh is None or float(getattr(sh, "Volume", 0.0)) <= 0.0]
    if empty:
        return False, (f"{len(empty)} placed solid(s) empty: "
                       f"{', '.join(empty[:5])}")
    return True, (f"all {N_PLACEMENTS} placements from placements.json "
                  f"built and non-empty; assembly notes report missing 0")


def _registry():
    reg = Registry("microduck")
    reg.register("microduck", build_microduck, check=check_microduck,
                 notes="the whole Microduck at zero pose — 70 placements, "
                       "38 distinct parts, from assembly:microduck")
    return reg


def system():
    """A BUILT registry — the entry point bin/deliver, bin/manual and
    bin/print all resolve."""
    reg = _registry()
    reg.build_all()
    return reg


def publish(out=None, zip=True):
    """Build AND package, programmatically — the same path bin/deliver
    drives. Returns deliver()'s report dict; read report['exit']."""
    from cecad.deliver import deliver
    reg = system()
    return deliver(reg, mod=sys.modules[__name__],
                   out=out or os.path.join(_DESIGN_ROOT, "out", "release"),
                   source=os.path.abspath(__file__), zip=zip)


if __name__ == "__main__":
    system()
