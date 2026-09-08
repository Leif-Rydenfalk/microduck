# ce-cad — Copyright (c) 2026 Leif Rydenfalk. All rights reserved.
# Proprietary and confidential. Use only under a written licence; see LICENSE.

"""Offscreen renderer with real hidden-line removal.

Why this exists: FreeCAD's own saveImage() returns a blank white PNG when
there is no visible GL window, and matplotlib's 3D painter algorithm sorts
triangles wrongly and shreds flat faces. So we rasterize ourselves:
a z-buffer for the shaded solid, then FreeCAD's true B-rep edges drawn on
top with a depth test. Output looks like a CAD viewport and is always correct.

    render(part, "out/bracket.png", view="iso")
    render(assembly, "out/asm.png", view="front", title="front elevation")

Two independent axes, because they answer different questions:

    mode="cad"          flat shading + hidden-line edges. Reads dimensions.
    mode="pbr"          Cook-Torrance metal/roughness. Reads as an object.
    mode="wire"         edges only. Reads the structure THROUGH the model.

    projection="ortho"        parallel. Equal lengths measure equal. The default.
    projection="perspective"  converging. Shows how big a thing feels.

`mode` decides how a surface is drawn; `projection` decides where it lands on
screen. They compose — `mode="pbr", projection="perspective"` is the hero
shot, `mode="cad", projection="ortho"` is the drawing. Never send an
engineering view out in perspective: two features the same size measure
differently on the page, which is the entire reason orthographic exists.

    render(a, "out/hero.png", mode="pbr", projection="perspective", fov=32)
    render(p, "out/wire.png", mode="wire", hidden=True)

Wireframe still rasterizes the solid — it just never shades it. The depth
buffer is what separates a visible edge from an obscured one, and without it
"wireframe" is every edge at once with no way to tell front from back.
`hidden=True` then draws the obscured edges dashed, the drafting convention,
so you can read an internal feature without cutting a section for it.

`CAD_RENDER_MODE` and `CAD_RENDER_PROJECTION` set the defaults for a whole
run, so `bin/watch` can rebuild a dashboard in PBR without editing any design.
"""
import hashlib
import math
import os
import shutil
import time

import numpy as np
import FreeCAD as App
import Part as _PartMod

# Views: (elevation, azimuth) in degrees.
VIEWS = {
    "iso":       (26, -52),
    "iso2":      (26, -128),
    "iso_rear":  (26, 128),
    "dimetric":  (20, -60),
    "front":     (0, -90),
    "back":      (0, 90),
    "right":     (0, 0),
    "left":      (0, 180),
    "top":       (89.5, -90),
    "bottom":    (-89.5, -90),
}

PALETTE = {
    "blue":   (0.32, 0.52, 0.80),
    "orange": (0.91, 0.56, 0.16),
    "steel":  (0.70, 0.73, 0.78),
    "green":  (0.36, 0.66, 0.42),
    "red":    (0.82, 0.34, 0.31),
    "purple": (0.55, 0.44, 0.76),
    "gold":   (0.85, 0.70, 0.28),
    "grey":   (0.62, 0.64, 0.67),
    "teal":   (0.27, 0.62, 0.66),
}
_CYCLE = ["blue", "orange", "steel", "green", "purple", "gold", "teal", "red"]

_LIGHT = np.array([0.5, -0.62, 0.6])
_LIGHT /= np.linalg.norm(_LIGHT)

MODES = ("cad", "pbr", "wire")
PROJECTIONS = ("ortho", "perspective")

# Wireframe ink. Visible edges near-black, obscured ones light enough to read
# as "behind" at a glance without disappearing.
WIRE_VISIBLE = 0.12
WIRE_HIDDEN = 0.66
WIRE_DASH = (11.0, 0.55)        # period in pixels, fraction drawn


def default_mode():
    m = os.environ.get("CAD_RENDER_MODE", "cad").strip().lower()
    return m if m in MODES else "cad"


def default_projection():
    p = os.environ.get("CAD_RENDER_PROJECTION", "ortho").strip().lower()
    p = {"orthographic": "ortho", "persp": "perspective"}.get(p, p)
    return p if p in PROJECTIONS else "ortho"


# ---------------------------------------------------------------------------
# PBR material response.
#
# Metallic is not a dial — it is a yes or no. A metal has no diffuse term and
# its albedo IS its specular colour; a dielectric reflects 4% white and shows
# its colour in diffuse. Values in between describe no real substance, and are
# only ever right on a boundary pixel between the two.
#
# Roughness is the honest per-material number: a printed PETG part is glossier
# along its layer lines than a milled aluminium one is anywhere.
# ---------------------------------------------------------------------------
PBR_MATERIALS = {
    "STEEL":   (1.0, 0.38), "SS304":  (1.0, 0.26), "BRASS": (1.0, 0.30),
    "AL6061":  (1.0, 0.44), "AL7075": (1.0, 0.44), "TI6AL4V": (1.0, 0.48),
    # copper is a metal like the rest; drawn tube and enamelled wire are
    # smoother than a milled aluminium face and duller than polished brass
    "COPPER":  (1.0, 0.28),
    "PLA":     (0.0, 0.45), "PETG":   (0.0, 0.32), "ABS":   (0.0, 0.52),
    "ASA":     (0.0, 0.55), "PCTG":   (0.0, 0.34), "NYLON": (0.0, 0.62),
    "PA6CF":   (0.0, 0.74), "PPS":    (0.0, 0.56), "DELRIN": (0.0, 0.40),
    "TPU":     (0.0, 0.80),
    # A PCB is a dielectric — the copper is under the mask, not on the surface
    # a camera sees — and liquid photoimageable solder mask is SEMI-GLOSS, well
    # below the 0.50 default every board in this repo was falling back to.
    # `atech.py` registers FR4 in fits.MATERIALS for its density and nothing
    # ever registered it here, so every populated board rendered as generic
    # mid-rough plastic. Matte mask exists and is nearer 0.55; this is the
    # ordinary glossy green a prototyping line comes back as.
    "FR4":     (0.0, 0.35),
}
DEFAULT_PBR = (0.0, 0.50)

# Studio environment, in WORLD space. Fixed while the camera moves, so a
# contact sheet lights every view the same way.
#
# `cards` are the reason metal reads as metal. A smooth gradient gives a flat
# metal face one single constant reflection, which is indistinguishable from
# matte paint — the first PBR pass here looked exactly like white plastic. What
# the eye actually uses to identify metal is the reflected SHAPE of the light:
# a bright softbox streaked across the surface, moving as the face turns. Each
# card is (direction, colour, brightness, tightness).
ENV = {
    "sky":     (0.52, 0.63, 0.80),
    "horizon": (0.72, 0.73, 0.76),
    "ground":  (0.22, 0.21, 0.20),
    "intensity": 1.0,
    "cards": (
        ((0.20, -0.38,  0.90), (1.00, 0.98, 0.94), 2.2, 16.0),   # overhead box
        ((-0.86, 0.22,  0.46), (0.86, 0.91, 1.00), 1.3,  6.0),   # side card
        ((0.62,  0.70,  0.10), (1.00, 0.95, 0.88), 1.0,  8.0),   # kicker
    ),
}

# Three-point rig, expressed in CAMERA space (right, up, toward-camera) so it
# follows the view. A rig fixed in world space leaves the back of the model
# unlit the moment you ask for `iso_rear`.
LIGHT_RIG = (
    ((-0.42,  0.52,  0.74), (1.00, 0.97, 0.92), 2.1),   # key, warm, upper left
    (( 0.82, -0.12,  0.46), (0.78, 0.85, 1.00), 0.6),   # fill, cool, right
    ((-0.22,  0.40, -0.89), (1.00, 0.94, 0.86), 1.1),   # rim, from behind
)

# Ambient diffuse is an approximation of a full hemisphere of incoming light,
# so it arrives at full strength from every direction at once. Left unscaled it
# swamps the rig and every surface flattens to the same value.
AMBIENT = 0.42
EXPOSURE = 0.72


def _basis(elev, azim):
    e, a = math.radians(elev), math.radians(azim)
    c = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
    r = np.cross(np.array([0, 0, 1.0]), c)
    n = np.linalg.norm(r)
    if n < 1e-9:                       # looking straight down
        r = np.array([1.0, 0, 0])
    else:
        r = r / n
    return r, np.cross(c, r), c


def _color(spec, i):
    if spec is None:
        spec = _CYCLE[i % len(_CYCLE)]
    if isinstance(spec, str):
        return PALETTE.get(spec, PALETTE["grey"])
    return tuple(spec)


def _renderable(obj):
    """The `Part.Shape` inside `obj`, or None — never a guess.

    MEASURED 2026-08-30, why this function exists: of the 111 `ce-parts`
    folders whose `cad/part.py` loads, **62 return a `cecad.core.Part` and 49
    return the raw FreeCAD document object** (`Part::Feature`, plus one
    `Mesh::Feature`). TRIAD.md fixes `build(doc, params=None) -> Part`; those
    49 authors read it as "return the object you put in the doc", and nothing
    ever told them otherwise.

    What that cost: the old fallback was `getattr(obj, "shape", obj)`. A
    FreeCAD document object has **`.Shape`, capital S** — so the lowercase
    lookup missed, the OBJECT ITSELF was handed on as if it were a shape, and
    it died three frames later inside `_mesh` on `shape.copy()` with
    `AttributeError: 'Part.Feature' object has no attribute 'copy'`. An
    attribute error on a private helper is not a diagnosis, which is why
    nobody traced it: `pico`'s render dates from Aug 18 and could not be
    remade after Aug 23.

    So: read `.Shape` too, convert a mesh document object, pass a bare
    `Part.Shape` straight through — and when none of those is true, REFUSE BY
    NAME rather than return something that will crash elsewhere.
    """
    for attr in ("shape", "Shape"):                # cecad Part, then Part::Feature
        s = getattr(obj, attr, None)
        if s is not None and hasattr(s, "BoundBox") and hasattr(s, "copy"):
            return s
    m = getattr(obj, "Mesh", None)                 # Mesh::Feature
    if m is not None and hasattr(m, "Topology"):
        try:
            s = _PartMod.Shape()
            s.makeShapeFromMesh(m.Topology, 0.05)
            return s
        except Exception:
            return None
    if hasattr(obj, "BoundBox") and hasattr(obj, "copy"):
        return obj                                 # already a Part.Shape
    return None


def _refuse(obj):
    return TypeError(
        "render(): cannot draw a %s.%s. render() takes a cecad Part or "
        "Assembly, a Part.Shape, a FreeCAD Part::Feature/Mesh::Feature, or a "
        "list of those. A triad folder's build(doc, params=None) is "
        "contracted by TRIAD.md to return a cecad Part."
        % (type(obj).__module__, type(obj).__name__))


def _collect(obj):
    """Normalise Part / Assembly / raw shapes / lists into [(shape, color, material)]."""
    from .core import Part, Assembly
    if isinstance(obj, Assembly):
        return [(s, _color(c, i), p.material)
                for i, ((_, p, s, c)) in enumerate(obj.items)]
    if isinstance(obj, Part):
        return [(obj.shape, _color(None, 0), obj.material)]
    if isinstance(obj, (list, tuple)):
        out = []
        for i, it in enumerate(obj):
            if isinstance(it, (list, tuple)) and len(it) in (2, 3) and not hasattr(it[0], "x"):
                shp, col = it[0], it[1]
                mat = it[2] if len(it) == 3 else None
                if isinstance(shp, Part):
                    mat = mat or shp.material
                    shp = shp.shape
                out.append((shp, _color(col, i), mat))
            else:
                mat = it.material if isinstance(it, Part) else None
                shp = it.shape if isinstance(it, Part) else _renderable(it)
                if shp is None:
                    raise _refuse(it)
                out.append((shp, _color(None, i), mat))
        return out
    shp = _renderable(obj)
    if shp is None:
        raise _refuse(obj)
    return [(shp, _color(None, 0), getattr(obj, "material", None))]


def view_for_section(section, elev=26.0):
    """Pick a camera that can actually SEE the cut face.

    A section is useless if you view it from the side the material was kept
    on — you just see the intact outside. The cut face normal points along
    +axis when keep="min" (and -axis when keep="max"), so the camera must sit
    on that side. Returns (elev, azim).
    """
    axis = str(section[0]).lower()
    keep = section[2] if len(section) > 2 else "min"
    sign = 1.0 if keep == "min" else -1.0
    if axis == "z":
        # camera above for keep="min", below for keep="max"
        return (abs(elev) * sign, -52.0)
    if axis == "y":
        # need camera-direction y-component to have `sign`: sin(azim) * sign > 0
        return (elev, 128.0 if sign > 0 else -52.0)
    # axis == "x": need cos(azim) * sign > 0
    return (elev, -52.0 if sign > 0 else -128.0)


def _section_cut(shape, spec):
    """Cut a solid open so internals are visible.

    spec is (axis, coord) or (axis, coord, keep):
        ("x", 30)         remove everything with x > 30
        ("x", 30, "max")  remove everything with x < 30 instead
    """
    axis, coord = spec[0], float(spec[1])
    keep = spec[2] if len(spec) > 2 else "min"
    b = shape.BoundBox
    pad = max(b.XLength, b.YLength, b.ZLength) * 2 + 10
    ai = {"x": 0, "y": 1, "z": 2}[axis.lower()]
    lo = [b.XMin, b.YMin, b.ZMin][ai] - pad
    origin = [b.XMin - pad, b.YMin - pad, b.ZMin - pad]
    size = [b.XLength + 2 * pad] * 3
    if keep == "min":
        origin[ai] = coord                      # box covers coord .. +inf
    else:
        origin[ai] = lo
        size[ai] = coord - lo                   # box covers -inf .. coord
    tool = _PartMod.makeBox(size[0], size[1], size[2], App.Vector(*origin))
    try:
        return shape.cut(tool)
    except Exception:
        return shape


# ---------------------------------------------------------------------------
# Tessellation
# ---------------------------------------------------------------------------
#: Angular deflection for meshing, RADIANS. 0.7 is 40 degrees, and it is the
#: number the rest of this repo already meshes at (`catalog._mesh_of`,
#: `catalog._stl_per_part`). `Shape.tessellate` uses OCCT's own default, which
#: is far tighter, and THAT is where a whole-car mesh explodes:
#:
#:     rc_car, 278 solids, the SAME shape and a COARSER linear deflection
#:       Shape.tessellate(0.08)                             2 594 632 tris
#:       MeshPart.meshFromShape(0.06, AngularDeflection=0.7)  166 408 tris
#:
#: 15.6x, and the linear tolerance is not what separates them — sweeping
#: `tessellate`'s tolerance from 0.08 to 1.0 (a 12x change) moved the count by
#: 21%. It is the ANGLE that decides how finely a curved face is cut up, and
#: nothing in this renderer ever set it.
MESH_ANGULAR = 0.7


_MESH_MEMO = {}
_MESH_KEEP = []


def _mesh(shape, tol):
    """Triangles off a shape, meshed the way the rest of the repo meshes.

    NOT `Shape.tessellate`, for the two reasons `catalog._mesh_of` already
    records against the same call:

    1. **It hands back whatever triangulation is already STORED on the shape**,
       at whatever tolerance stored it, ignoring the one you asked for.
       Measured here on the car's own STEP, one tolerance per fresh process
       against repeated calls in one process: the first call meshes and stores,
       and every later call returns that mesh — 2 594 632 triangles whether you
       ask for 0.08 or 2.0, in 2.7 s instead of 12 s. A tolerance that is
       silently ignored is worse than one that is wrong.
    2. **It sets no angular deflection**, which is what actually drives the
       count on curved faces and small features. See MESH_ANGULAR.

    `.copy()` is what dodges (1) — the stored mesh belongs to the original.
    """
    # A CONTACT SHEET IS FOUR RENDERS OF ONE SHAPE, and an exploded view is
    # one more. Meshing is 1.9 s of the car's 5.7 s and it does not depend on
    # the camera, so doing it once per shape per tolerance instead of once per
    # PICTURE is four views for the price of one. Keyed by the shape's identity
    # within this process — never by geometry, which would have to tessellate
    # to hash and would then be the very trap this function exists to dodge.
    key = (id(shape), round(float(tol), 6))
    hit = _MESH_MEMO.get(key)
    if hit is not None:
        return hit
    try:
        import MeshPart
        m = MeshPart.meshFromShape(Shape=shape.copy(), LinearDeflection=tol,
                                   AngularDeflection=MESH_ANGULAR,
                                   Relative=False)
        out = ([p.Vector for p in m.Points],
               [f.PointIndices for f in m.Facets])
    except ImportError:                                        # pragma: no cover
        out = shape.tessellate(tol)
    # `id()` is only unique while the object is ALIVE, so hold a reference to
    # the shape alongside its mesh. Without it a freed shape's address can be
    # handed to a new one and this returns another part's triangles.
    if len(_MESH_MEMO) < 512:
        _MESH_MEMO[key] = out
        _MESH_KEEP.append(shape)
    return out


_EDGE_MEMO = {}


def _edge_polylines(shp):
    """Every B-rep edge of a shape as a world-space polyline.

    MEMOISED for the same reason the mesh is: an edge does not depend on the
    camera, and this is 0.52 s of a 2.4 s repeat view on the car — 23 604
    `discretize` calls plus 23 604 little `np.array`s over Python point
    objects. A contact sheet paid it four times over for identical answers.

    Keyed on the shape's identity within this process, with a reference held
    alongside so a freed shape's address cannot be reissued to another part.
    """
    hit = _EDGE_MEMO.get(id(shp))
    if hit is not None:
        return hit
    out = []
    for e in shp.Edges:
        try:
            n = max(2, min(200, int(e.Length / 0.35) + 2))
            pts = e.discretize(Number=n)
        except Exception:
            continue
        out.append(np.array([[p.x, p.y, p.z] for p in pts]))
    if len(_EDGE_MEMO) < 512:
        _EDGE_MEMO[id(shp)] = out
        _MESH_KEEP.append(shp)
    return out


def _tris_flat(shp, tol):
    """Triangles only — what flat CAD shading needs."""
    vs, fs = _mesh(shp, tol)
    if not fs:
        return None
    v = np.array([[p.x, p.y, p.z] for p in vs])
    return v[np.array(fs, dtype=int)]


def _tris_smooth(shp, tol, view_dir):
    """Triangles plus per-vertex normals, averaged WITHIN each B-rep face.

    Tessellating the whole shape and smoothing everything rounds off every box
    corner; tessellating face by face keeps a cylinder smooth and a corner
    sharp, because a crease in CAD is exactly a face boundary. No angle
    threshold to tune — the topology already says where the creases are.

    Orientation: only triangles facing the camera contribute to a vertex's
    normal. FreeCAD's per-face winding is not reliably outward, and we only
    ever shade front-facing pixels anyway, so "the triangles you can see" is
    both the robust rule and the visually correct one.
    """
    faces = shp.Faces
    if not faces:
        t = _tris_flat(shp, tol)
        return (None if t is None else (t, None))

    tri_out, nrm_out = [], []
    for face in faces:
        try:
            vs, fs = _mesh(face, tol)
        except Exception:
            continue
        if not fs:
            continue
        v = np.array([[p.x, p.y, p.z] for p in vs], dtype=np.float64)
        f = np.array(fs, dtype=int)
        t = v[f]

        fn = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
        area = np.linalg.norm(fn, axis=1)
        good = area > 1e-12
        if not good.any():
            continue
        unit = np.zeros_like(fn)
        unit[good] = fn[good] / area[good, None]

        # front-facing set defines the orientation for this face
        toward = unit @ view_dir
        flip = np.where(toward < 0, -1.0, 1.0)[:, None]
        contrib = unit * flip * area[:, None]        # area-weighted
        seen = np.abs(toward) > 1e-9

        acc = np.zeros_like(v)
        for k in range(3):
            np.add.at(acc, f[seen, k], contrib[seen])
        ln = np.linalg.norm(acc, axis=1)
        flat_fallback = ln < 1e-12
        acc[~flat_fallback] /= ln[~flat_fallback, None]

        vn = acc[f]
        # a vertex no triangle could orient falls back to its face normal
        bad = flat_fallback[f]
        if bad.any():
            vn[bad] = (unit * flip)[:, None, :].repeat(3, axis=1)[bad]
        tri_out.append(t)
        nrm_out.append(vn)

    if not tri_out:
        return None
    return np.vstack(tri_out), np.vstack(nrm_out).astype(np.float32)


# ---------------------------------------------------------------------------
# PBR shading
# ---------------------------------------------------------------------------
def _srgb_to_linear(c):
    return np.power(np.clip(c, 0.0, 1.0), 2.2)


def _env_sample(d, env, blur=0.0):
    """Sky / horizon / ground gradient, sampled along a direction.

    `blur` flattens it toward the horizon colour, which is how a rough surface
    sees an environment: it integrates over a wide cone and loses the detail.
    It is per-pixel — every surface has its own roughness — so it stays an
    array here rather than being collapsed to a scalar.
    """
    sky = np.array(env["sky"], dtype=np.float32)
    hor = np.array(env["horizon"], dtype=np.float32)
    gnd = np.array(env["ground"], dtype=np.float32)
    b = np.clip(np.asarray(blur, dtype=np.float32), 0.0, 1.0)
    t = d[:, 2]

    # The HORIZON is what identifies metal. A mirror shows a hard line where
    # sky meets ground; a rough surface smears that line into a gradient. Make
    # the transition width scale with roughness and both fall out of the same
    # expression. A smooth gradient at every roughness — the first version
    # here — measured 0.72..0.81 across the whole sky, so a metal reflected the
    # same value whichever way it faced and read as matte paint.
    w = 0.03 + 0.80 * b
    q = np.clip(t / w, -1.0, 1.0)
    s = (0.5 + 0.5 * q * (1.5 - 0.5 * q * q))[:, None]
    col = gnd[None, :] + (sky - gnd)[None, :] * s

    # a bright band along the horizon itself, the way a studio floor bounces
    glow = np.exp(-np.square(t / (w * 1.6)))[:, None]
    boost = np.clip(hor - 0.5 * (sky + gnd), 0.0, None)
    col = col + boost[None, :] * glow * 1.7

    # The light cards. A rough surface integrates over a wide cone, so its
    # cards spread out and dim rather than vanishing — hence the exponent and
    # the brightness both scaling with blur, which is what keeps a sandblasted
    # part from showing a mirror-sharp highlight.
    soft = 1.0 - 0.70 * b
    for cdir, ccol, bright, tight in env.get("cards", ()):
        cd = np.asarray(cdir, dtype=np.float32)
        cd = cd / np.linalg.norm(cd)
        lobe = np.clip(d @ cd, 0.0, 1.0)
        k = np.maximum(tight * soft, 1.0)
        gain = np.broadcast_to(bright * np.power(lobe, k) * soft, lobe.shape)
        col = col + np.asarray(ccol, dtype=np.float32)[None, :] * gain[:, None]
    return col * float(env.get("intensity", 1.0))


def _env_brdf(NoV, rough):
    """Karis' analytic fit to the split-sum environment BRDF — the (scale, bias)
    that turn F0 into the correct ambient specular for a given roughness."""
    c0 = np.array([-1.0, -0.0275, -0.572, 0.022], dtype=np.float32)
    c1 = np.array([1.0, 0.0425, 1.04, -0.04], dtype=np.float32)
    rx = rough * c0[0] + c1[0]
    ry = rough * c0[1] + c1[1]
    rz = rough * c0[2] + c1[2]
    rw = rough * c0[3] + c1[3]
    a004 = np.minimum(rx * rx, np.exp2(-9.28 * NoV)) * rx + ry
    return -1.04 * a004 + rz, 1.04 * a004 + rw


def _shade_pbr(N, V, albedo, metallic, rough, env, rig, ambient=AMBIENT):
    """Cook-Torrance: GGX distribution, Smith geometry, Schlick Fresnel."""
    rough = np.clip(rough, 0.045, 1.0)
    a = rough * rough
    a2 = a * a
    NoV = np.clip(np.einsum("ij,ij->i", N, V), 1e-4, 1.0)

    F0 = 0.04 * (1.0 - metallic)[:, None] + albedo * metallic[:, None]
    kD_base = (1.0 - metallic)[:, None]
    out = np.zeros_like(albedo)

    for d, col, power in rig:
        L = np.asarray(d, dtype=np.float32)
        L = L / np.linalg.norm(L)
        radiance = np.asarray(col, dtype=np.float32) * float(power)
        NoL = np.einsum("ij,j->i", N, L)
        lit = NoL > 0.0
        if not lit.any():
            continue
        NoL = np.clip(NoL, 0.0, 1.0)
        Hv = L[None, :] + V
        Hv = Hv / np.maximum(np.linalg.norm(Hv, axis=1, keepdims=True), 1e-9)
        NoH = np.clip(np.einsum("ij,ij->i", N, Hv), 0.0, 1.0)
        VoH = np.clip(np.einsum("ij,ij->i", V, Hv), 0.0, 1.0)

        denom = NoH * NoH * (a2 - 1.0) + 1.0
        D = a2 / np.maximum(math.pi * denom * denom, 1e-9)
        k = (rough + 1.0) ** 2 / 8.0
        G = (NoL / (NoL * (1 - k) + k)) * (NoV / (NoV * (1 - k) + k))
        F = F0 + (1.0 - F0) * np.power(1.0 - VoH, 5.0)[:, None]

        spec = (D * G / np.maximum(4.0 * NoL * NoV, 1e-9))[:, None] * F
        diff = kD_base * (1.0 - F) * albedo / math.pi
        out += (diff + spec) * radiance[None, :] * NoL[:, None]

    # ambient: irradiance for diffuse, a reflection probe for specular
    irr = _env_sample(N, env, blur=1.0)
    R = 2.0 * NoV[:, None] * N - V
    R = R / np.maximum(np.linalg.norm(R, axis=1, keepdims=True), 1e-9)
    refl = _env_sample(R, env, blur=rough)
    sA, sB = _env_brdf(NoV, rough)
    out += kD_base * albedo * irr * ambient
    out += refl * (F0 * sA[:, None] + sB[:, None])
    return out


def _tonemap(x):
    """ACES filmic, Narkowicz's fit. Without it the highlights clip flat white
    and every metal reads as painted plastic."""
    x = np.clip(x, 0.0, None)
    y = (x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14)
    return np.clip(y, 0.0, 1.0)


def _ssao(zbuf, mask, radius_px, depth_scale, strength=0.55, samples=12):
    """Screen-space ambient occlusion off the depth buffer.

    Cheap, and it does the one thing the light rig cannot: darken the inside
    of a bore and the seam where two parts meet, which is exactly where the
    eye looks to judge whether something fits.
    """
    if radius_px < 1.0:
        return np.ones_like(zbuf, dtype=np.float32)
    occ = np.zeros(zbuf.shape, dtype=np.float32)
    rings = (0.35, 0.7, 1.0)
    n = 0
    for ring in rings:
        rr = max(1, int(round(radius_px * ring)))
        for k in range(samples // len(rings)):
            ang = 2.0 * math.pi * (k / (samples / len(rings))) + ring * 1.7
            dx, dy = int(round(rr * math.cos(ang))), int(round(rr * math.sin(ang)))
            if dx == 0 and dy == 0:
                continue
            nz = np.roll(np.roll(zbuf, dy, axis=0), dx, axis=1)
            nm = np.roll(np.roll(mask, dy, axis=0), dx, axis=1)
            # positive = the neighbour is nearer the camera, i.e. an occluder
            diff = (nz - zbuf) / depth_scale
            w = np.clip(diff, 0.0, 1.0) * np.clip(2.0 - diff, 0.0, 1.0)
            occ += np.where(nm & mask, w, 0.0).astype(np.float32)
            n += 1
    if not n:
        return np.ones_like(zbuf, dtype=np.float32)
    return np.clip(1.0 - strength * occ / n, 0.0, 1.0)


#: The background is IDENTICAL for a given canvas and mode, and it was rebuilt
#: from scratch on every render — a (1680, 2480, 3) float32 array is ~50 MB, so
#: a contact sheet of four views allocated and filled 200 MB of pixels that
#: never differ. Measured on a 12-triangle part, where the model itself is
#: nothing and the canvas is everything: 0.55 s per render at ss=2.
#:
#: Cached by (w, h, mode, bg, env) and handed out as a COPY, because the caller
#: writes the model into it pixel by pixel. A copy of 50 MB is a memcpy;
#: building it is linspace, broadcast, power and repeat.
_BG_CACHE = {}
_BG_CACHE_MAX = 6            # a handful of canvas sizes, not an unbounded map


# ==========================================================================
# The render cache — content-addressed, so a hit is provably the same picture
# ==========================================================================
#: A build's time is its renders: 13 of them were 7.9 s of shaft_support's
#: 10.9 s CPU, and one render of a 2044-triangle block is 0.93 s against
#: 0.028 s to tessellate it. The geometry is cheap and the PIXELS are not —
#: 1240x840 at ss=2 is 4.2 M of them — so the thing worth not doing twice is
#: the painting, and iterating on a design repaints every part that did not
#: change. `bin/watch` is worse: a one-line edit in `cecad/` rebuilds every
#: design there is.
#:
#: The key is a SHA-256 over the ACTUAL RASTERIZER INPUTS — the triangle
#: array, the per-face colours and materials, the smooth normals, every edge
#: polyline, and every parameter that reaches the pixels — plus a token for
#: `render.py`'s own source. Two things follow, and both are load-bearing:
#:
#:   - equal key means equal inputs, so a hit is the same image BY
#:     CONSTRUCTION rather than by assumption. This is not an mtime check and
#:     it cannot be fooled by a file that was touched, moved or rebuilt: a
#:     part rebuilt from identical parameters hashes identically and SHOULD
#:     hit, and a part whose bore moved 0.01 mm cannot.
#:   - a changed renderer invalidates everything, because the token is the
#:     source's own hash. Editing this file cannot leave stale pictures
#:     behind, which is the one failure that would poison every check that
#:     reads a PNG.
#:
#: The geometry still has to be tessellated to be hashed. That is the 3% we
#: keep paying and it is what makes the key honest — a cheaper key would be a
#: claim about the geometry rather than a measurement of it.
#:
#: `CAD_NO_RENDER_CACHE=1` turns it off. `tests/test_render_cache.py` is the
#: specification: every cached answer is compared byte for byte against the
#: same render made with the cache off, and nine deliberate mutations — a
#: hole moved 0.01 mm, one degree of view, one pixel of height — must each
#: MISS.
_SRC_TOKEN = None
_CACHE_MAX_FILES = 3000      # ~1.5 GB of 620x430 PNGs at the outside


def _src_token():
    """A hash of this module's own source, so editing the renderer cannot
    leave stale pictures in the cache. Falls back to a value that disables
    caching entirely if the source cannot be read — an unknown renderer
    version must never share a namespace with a known one."""
    global _SRC_TOKEN
    if _SRC_TOKEN is None:
        try:
            with open(os.path.abspath(__file__), "rb") as fh:
                _SRC_TOKEN = hashlib.sha256(fh.read()).hexdigest()[:16]
        except Exception:
            _SRC_TOKEN = None
    return _SRC_TOKEN


def render_cache_dir():
    """Where cached PNGs live: `out/.rendercache` beside everything else
    generated. Never inside the source tree."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(root, "out", ".rendercache")


def _cache_enabled():
    return os.environ.get("CAD_NO_RENDER_CACHE", "").lower() \
        not in ("1", "true", "yes")


def _render_key(parts):
    """SHA-256 over every input the pixels are drawn from.

    `parts` is a list of numpy arrays and plain values. Arrays contribute
    their raw bytes AND their shape and dtype — two different arrays can
    share a byte string at different shapes, and that would be a collision
    between two genuinely different pictures.
    """
    h = hashlib.sha256()
    tok = _src_token()
    if tok is None:
        return None                      # unknown renderer: never cache
    h.update(tok.encode())
    for item in parts:
        if isinstance(item, np.ndarray):
            h.update(b"\x01")
            h.update(str(item.shape).encode())
            h.update(str(item.dtype).encode())
            h.update(np.ascontiguousarray(item).tobytes())
        else:
            h.update(b"\x02")
            h.update(repr(item).encode())
    return h.hexdigest()


def _cache_get(key, path):
    """Copy the cached PNG into `path`. True if it was there."""
    if key is None:
        return False
    src = os.path.join(render_cache_dir(), key + ".png")
    try:
        if not os.path.exists(src):
            return False
        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".",
                    exist_ok=True)
        shutil.copyfile(src, path)
        return True
    except Exception:
        return False                     # a broken cache is a miss, never a fail


def _cache_put(key, path):
    """File the freshly rendered PNG under its key. Written to a temp name
    and renamed, because other sessions run against this same repo and a
    half-written PNG read as a hit would be a corrupt picture nobody could
    explain."""
    if key is None:
        return
    d = render_cache_dir()
    try:
        os.makedirs(d, exist_ok=True)
        dst = os.path.join(d, key + ".png")
        if os.path.exists(dst):
            return
        tmp = dst + f".{os.getpid()}.tmp"
        shutil.copyfile(path, tmp)
        os.replace(tmp, dst)             # atomic within the filesystem
        _cache_prune(d)
    except Exception:
        pass                             # caching is an optimisation, not a duty


def _cache_prune(d):
    """Keep the cache bounded. Only ever deletes; a deleted entry is a miss
    and costs one render, so an unlink losing a race with another session is
    harmless."""
    try:
        names = os.listdir(d)
        if len(names) <= _CACHE_MAX_FILES:
            return
        paths = []
        for n in names:
            p = os.path.join(d, n)
            try:
                paths.append((os.path.getmtime(p), p))
            except OSError:
                continue
        paths.sort()
        for _, p in paths[:max(1, len(paths) // 4)]:
            try:
                os.unlink(p)
            except OSError:
                pass
    except Exception:
        pass


def _background(w, h, mode, bg, env):
    # NOT keyed on env: id() is reused after garbage collection, so a freed
    # environment's id could serve its cached background to a different one —
    # a wrong picture that renders perfectly. env is rare and the default is
    # None, so anything with one simply builds fresh rather than risk it.
    if env is not None:
        return _background_build(w, h, mode, bg, env)
    key = (w, h, mode,
           tuple(np.ravel(bg).tolist()) if isinstance(bg, (list, tuple, np.ndarray))
           else bg)
    hit = _BG_CACHE.get(key)
    if hit is not None:
        return hit.copy()
    base = _background_build(w, h, mode, bg, env)
    if len(_BG_CACHE) >= _BG_CACHE_MAX:
        _BG_CACHE.clear()    # simplest bound that cannot leak across sizes
    _BG_CACHE[key] = base
    return base.copy()


def _background_build(w, h, mode, bg, env):
    if bg is not None and not isinstance(bg, (list, tuple, np.ndarray)):
        return np.full((h, w, 3), float(bg), dtype=np.float32)
    if mode != "pbr":
        return np.full((h, w, 3), 1.0, dtype=np.float32)
    top = np.array(bg[0] if bg else (0.93, 0.94, 0.96), dtype=np.float32)
    bot = np.array(bg[1] if bg else (0.74, 0.75, 0.78), dtype=np.float32)
    t = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None, None] ** 1.15
    grad = bot[None, None, :] + (top - bot)[None, None, :] * t
    # broadcast_to gives a read-only (h, 1, 3) view; the image is written into
    # pixel by pixel, so it has to be a real (h, w, 3) array
    return np.repeat(grad.astype(np.float32), w, axis=1)


# ---------------------------------------------------------------------------
# The title strip. A CAPTION THAT IS CLIPPED IS NOT A CAPTION.
# ---------------------------------------------------------------------------
# MEASURED 2026-08-30: the first provenance-carrying render came out reading
# `0  ·  part:SG90 · built by build() in ce-parts/SG90/cad/part.py · loads
# geometry/SG90.step  —  iso  —  2026-08-30 17:28` — the leading "SG9" and the
# trailing ":16" fell off both ends of the canvas, because the title was drawn
# centred at a fixed 13.5 pt with no measurement of how wide it actually is.
# A half-cited picture is exactly the decoration the house rule forbids, so the
# band MEASURES the text and wraps or shrinks until the whole line fits.
_TXT_MEMO = {}


def _text_px(s, fs, dpi=100):
    """Width of `s` in PIXELS at `fs` points — measured off the real glyphs."""
    key = (s, round(fs, 2))
    hit = _TXT_MEMO.get(key)
    if hit is not None:
        return hit
    try:
        from matplotlib.textpath import TextPath
        from matplotlib.font_manager import FontProperties
        w = TextPath((0, 0), s, size=fs,
                     prop=FontProperties(weight="bold")).get_extents().width
        w = w * dpi / 72.0
    except Exception:                                   # pragma: no cover
        w = len(s) * fs * 0.85                          # never crash on a caption
    if len(_TXT_MEMO) < 4096:
        _TXT_MEMO[key] = w
    return w


#: Where a caption may be broken, most-preferred first. These are the
#: separators docs/part-docs.md's cite grammar is built from, so a wrap lands
#: between two facts instead of inside a file path.
_WRAP_ON = ("  —  ", "  ·  ", " · ", " — ", ", ", " ")


def _wrap_title(text, w_px, fs):
    """[line, ...] each fitting `w_px`, breaking on the cite grammar."""
    if _text_px(text, fs) <= w_px:
        return [text]
    for sep in _WRAP_ON:
        if sep not in text:
            continue
        parts = text.split(sep)
        lines, cur = [], parts[0]
        for nxt in parts[1:]:
            trial = cur + sep.rstrip() + " " + nxt.lstrip()
            if _text_px(trial, fs) <= w_px:
                cur = trial
            else:
                lines.append(cur)
                cur = nxt.lstrip()
        lines.append(cur)
        if all(_text_px(l, fs) <= w_px for l in lines):
            return lines
    return [text]


def title_band(text, w_px, fs=13.5, min_fs=7.0, max_lines=3):
    """(lines, fontsize, band_height_px) that shows ALL of `text`.

    Shrinks first (one line reads better), then wraps, then shrinks again —
    and never returns a layout that clips. A caption too long even for
    `max_lines` at `min_fs` still comes back COMPLETE, on more lines than
    asked for: losing the end of a provenance line is the one outcome this
    function exists to prevent.
    """
    text = " ".join(str(text).split())
    w = w_px * 0.985
    f = fs
    while f > min_fs and _text_px(text, f) > w:
        f = max(min_fs, f - 0.5)
    lines = _wrap_title(text, w, f)
    while len(lines) > max_lines and f > min_fs:
        f = max(min_fs, f - 0.5)
        lines = _wrap_title(text, w, f)
    band = int(round(len(lines) * f * 1.60 + 16))
    return lines, f, band


def _draw_title(fig, lines, fs, band_px, fig_h_px):
    """Draw the band's lines from the top down, in figure coordinates."""
    step = fs * 1.60 / fig_h_px
    top = 1.0 - (fs * 1.05 + 6) / fig_h_px
    for i, ln in enumerate(lines):
        fig.text(0.5, top - i * step, ln, ha="center", va="center",
                 fontsize=fs, fontweight="bold", color="#141414")


# ---------------------------------------------------------------------------
def render(obj, path, view="iso", title=None, W=1240, H=840, ss=2, tol=0.08,
           edges=None, bg=None, section=None, connectors=None, verbose=True,
           mode=None, projection=None, fov=30.0, pbr=None, env=None,
           ao=True, exposure=EXPOSURE, hidden=False, overlay_lines=None,
           framing=None, ortho_pixels_per_mm=None, ortho_center_projected_mm=None):
    """Render a Part, Assembly, or list of them to a PNG.

    mode        "cad" (flat + hidden-line, the default), "pbr", or "wire".
    projection  "ortho" (the default) or "perspective".
    fov         vertical field of view in degrees, perspective only.
    hidden      also draw the edges the solid obscures, dashed.
    pbr         (metallic, roughness) forced on everything, instead of taking
                it from each part's material.
    ao          screen-space occlusion in PBR mode.
    exposure    scales radiance before tone mapping. Raise it for a dark
                model, lower it if the highlights clip.
    framing     optional dict filled with the actual orthographic camera
                transform and output pixels/mm. Supported for untitled ortho
                images; title bands and perspective have no such sheet scale.
                The usual returned path and rendering behavior are unchanged.
    ortho_pixels_per_mm  optional positive output-pixel scale, instead of
                automatic fit. Untitled orthographic renders only; geometry
                is projected at this scale without stretching either axis.
    ortho_center_projected_mm optional (right, up) camera-plane centre in model
                mm. Untitled orthographic renders only. This changes framing,
                not geometry; portions outside the raster are clipped.

    overlay_lines is [(p0, p1, color), ...] — world-space reference lines
    drawn dashed on top of the model (an exploded view's leader lines from
    each part back to its assembled place). Reference ink, never geometry.

    section=("z", 25) cuts the model open on that plane before rendering, so
    bores, pockets and wall thicknesses become visible. Cut faces are shaded
    distinctly. An external view can look perfect while the inside is wrong —
    this is how you catch that.

    CAD_NO_RENDER=1 skips the render entirely, for iterate loops where the
    geometry is the question and the picture is not: shaft_support spends
    ~88% of its own CPU in 13 renders (measured, CLAUDE.md "Speed"). It
    prints one line per skip so a missing PNG is never a mystery — and any
    PNG already on disk is STALE, which is why this is opt-in per run and
    never a default.
    """
    if framing is not None:
        framing.clear()
    if os.environ.get("CAD_NO_RENDER", "").lower() in ("1", "true", "yes"):
        if verbose:
            print(f"  [render skipped] {path} (CAD_NO_RENDER=1 — "
                  "any existing PNG there is stale)")
        return None
    mode = (mode or default_mode()).lower()
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}, got {mode!r}")
    projection = (projection or default_projection()).lower()
    projection = {"orthographic": "ortho", "persp": "perspective"}.get(
        projection, projection)
    if projection not in PROJECTIONS:
        raise ValueError(f"projection must be one of {PROJECTIONS}, "
                         f"got {projection!r}")
    if framing is not None and (projection != 'ortho' or title):
        raise ValueError('framing metadata requires an untitled orthographic render')
    if ortho_pixels_per_mm is not None:
        if projection != 'ortho' or title:
            raise ValueError('explicit pixel scale requires an untitled orthographic render')
        ortho_pixels_per_mm = float(ortho_pixels_per_mm)
        if not math.isfinite(ortho_pixels_per_mm) or ortho_pixels_per_mm <= 0:
            raise ValueError('ortho_pixels_per_mm must be finite and positive')
    if ortho_center_projected_mm is not None:
        if projection != 'ortho' or title:
            raise ValueError('explicit camera centre requires an untitled orthographic render')
        if isinstance(ortho_center_projected_mm,(str,bytes)):
            raise ValueError('ortho_center_projected_mm must be a two-value coordinate sequence')
        try:
            ortho_center_projected_mm = tuple(float(v) for v in ortho_center_projected_mm)
        except (TypeError,ValueError):
            raise ValueError('ortho_center_projected_mm must contain two finite values') from None
        if len(ortho_center_projected_mm)!=2 or not all(math.isfinite(v) for v in ortho_center_projected_mm):
            raise ValueError('ortho_center_projected_mm must contain two finite values')
    is_pbr = mode == "pbr"
    is_wire = mode == "wire"
    if edges is None:
        # PBR earns its look from shading; a hard black wireframe over it just
        # reads as a CAD render with a gradient behind it.
        edges = not is_pbr
    if is_wire:
        edges = True                       # they are the entire picture
    env = dict(ENV, **(env or {}))

    if isinstance(view, str):
        if view not in VIEWS:
            raise KeyError(f"view must be one of {sorted(VIEWS)} or (elev, azim)")
        elev, azim = VIEWS[view]
    else:
        elev, azim = view

    items = _collect(obj)
    if section is not None:
        items = [(_section_cut(s, section), col, mat)
                 for s, col, mat in items if s is not None]
    w, h = W * ss, H * ss
    r, u, c = _basis(elev, azim)

    tris, cols, mats, norms, edge_pts = [], [], [], [], []
    for shp, col, mat in items:
        if shp is None:
            continue
        if is_pbr:
            got = _tris_smooth(shp, tol, c)
            if got is None:
                continue
            t, vn = got
            norms.append(vn if vn is not None else np.zeros_like(t, dtype=np.float32))
        else:
            t = _tris_flat(shp, tol)
            if t is None:
                continue
        tris.append(t)
        cols.append(np.repeat(np.array(col, dtype=float)[None, :], len(t), axis=0))
        m, rg = PBR_MATERIALS.get(str(mat).upper(), DEFAULT_PBR) if pbr is None \
            else (float(pbr[0]), float(pbr[1]))
        mats.append(np.repeat(np.array([m, rg], dtype=np.float32)[None, :],
                              len(t), axis=0))
        if edges:
            edge_pts.extend(_edge_polylines(shp))
    if not tris:
        raise ValueError("nothing to render")
    tris = np.vstack(tris)
    cols = np.vstack(cols)
    mats = np.vstack(mats)
    vnorm = np.vstack(norms).astype(np.float32) if is_pbr else None

    def projection_frame():
        allv = tris.reshape(-1, 3)
        sx, sy, sz = allv @ r, allv @ u, allv @ c
        cx, cy = (sx.max() + sx.min()) / 2, (sy.max() + sy.min()) / 2
        if ortho_center_projected_mm is not None:
            cx,cy=ortho_center_projected_mm
        span = max(sx.max() - sx.min(), sy.max() - sy.min()) * 1.10
        scale = (min(w, h) / span if ortho_pixels_per_mm is None
                 else ortho_pixels_per_mm * ss)
        return cx, cy, span, scale, sz

    if framing is not None:
        cx, cy, span, scale, sz = projection_frame()
        framing.update(projection='ortho', image_px=[int(W), int(H)],
                       pixels_per_model_mm=float(scale/ss),
                       camera_right=list(map(float,r)), camera_up=list(map(float,u)),
                       center_projected_mm=[float(cx),float(cy)],
                       model_window_mm=[float(w/scale),float(h/scale)],
                       camera_elev_azim=[float(elev),float(azim)])

    # THE CACHE, keyed on everything below this line and nothing above it.
    # Placed here because this is the first point at which the picture is
    # fully determined: the geometry has become triangles, colours and edge
    # polylines, and what remains is arithmetic on them. Anything that could
    # still change the image — the camera, the canvas, the mode, the title —
    # is a parameter and goes in the key.
    key = None
    if _cache_enabled():
        key = _render_key([
            tris, cols, mats,
            vnorm if vnorm is not None else np.zeros(0, dtype=np.float32),
            len(edge_pts), *edge_pts,
            elev, azim, W, H, ss, tol, mode, projection, fov, edges, hidden,
            is_pbr, is_wire, ao, exposure, title,
            None if pbr is None else (float(pbr[0]), float(pbr[1])),
            bg, sorted(env.items()) if isinstance(env, dict) else env,
            section if section is None else
            (str(section[0]), float(section[1]),
             *(section[2:] if len(section) > 2 else ())),
            None if not connectors else
            [(tuple(cn.pos), tuple(cn.dir), tuple(cn.up)) for cn in connectors],
            None if not overlay_lines else
            [(tuple(float(x) for x in p0), tuple(float(x) for x in p1),
              tuple(float(x) for x in lc)) for p0, p1, lc in overlay_lines],
            *([] if ortho_pixels_per_mm is None else
              [('ortho_pixels_per_mm', ortho_pixels_per_mm)]),
            *([] if ortho_center_projected_mm is None else
              [('ortho_center_projected_mm', ortho_center_projected_mm)]),
        ])
        if _cache_get(key, path):
            if verbose:
                print(f"  rendered {path}  ({len(tris)} tris, view={view}, "
                      f"cached)")
            return path

    if framing is None:
        # Keep the existing cache-hit fast path unchanged for ordinary renders.
        cx, cy, span, scale, sz = projection_frame()
    depth_span = max(sz.max() - sz.min(), 1e-6)

    focal = nxc = nyc = 0.0
    if projection == "perspective":
        # Pull the camera back until `span` subtends `fov`, measured at the
        # model's MID depth — that is where its apparent size is set.
        half = math.tan(math.radians(max(1.0, min(120.0, fov)) / 2.0))
        eye_d = max(span / (2.0 * half) - depth_span * 0.5,
                    depth_span * 0.2 + span * 0.05)
        near_ref = sz.max()

        def _norm(P):
            dz = np.maximum(eye_d - (P @ c - near_ref), 1e-6)
            return (P @ r - cx) / dz, (P @ u - cy) / dz, dz

        # Then FIT rather than trust the estimate: under perspective the near
        # face projects larger than the far one, by an amount that depends on
        # the model's own depth, so a computed camera distance always mis-frames
        # something. Measuring the projected extent costs one pass and is exact.
        _nx, _ny, _ = _norm(allv)
        nxc = float((_nx.max() + _nx.min()) / 2.0)
        nyc = float((_ny.max() + _ny.min()) / 2.0)
        fx = (w / 2.0) / max(float(np.abs(_nx - nxc).max()), 1e-9)
        fy = (h / 2.0) / max(float(np.abs(_ny - nyc).max()), 1e-9)
        focal = min(fx, fy) / 1.06

        def proj(P):
            a, b, dz = _norm(P)
            return ((a - nxc) * focal + w / 2.0,
                    (b - nyc) * focal + h / 2.0,
                    -dz)                          # larger = nearer, as before
    else:
        def proj(P):
            return ((P @ r - cx) * scale + w / 2,
                    (P @ u - cy) * scale + h / 2,
                    P @ c)

    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    ln = np.linalg.norm(n, axis=1)
    ln[ln == 0] = 1
    n = n / ln[:, None]

    on_plane = None
    if section is not None:
        ai = {"x": 0, "y": 1, "z": 2}[str(section[0]).lower()]
        coord = float(section[1])
        on_plane = np.all(np.abs(tris[:, :, ai] - coord) < 1e-6, axis=1)

    if is_pbr:
        alb = _srgb_to_linear(cols).astype(np.float32)
        if on_plane is not None and on_plane.any():
            # A cut face is raw material, not a finished surface: matte, and
            # tinted so the section plane reads at a glance the way hatching
            # does on a real sectional drawing.
            alb[on_plane] = _srgb_to_linear(
                np.clip(cols[on_plane] * 0.5 + np.array([0.34, 0.09, 0.09]), 0, 1))
            mats[on_plane] = np.array([0.0, 0.92], dtype=np.float32)
    elif is_wire:
        face_col = None                    # the solid is rasterized, never shaded
    else:
        lam = np.abs(n @ _LIGHT)
        face_col = np.clip(cols * (0.30 + 0.70 * lam)[:, None]
                           + (np.clip(lam, 0, 1) ** 28)[:, None] * 0.35, 0, 1)
        if on_plane is not None and on_plane.any():
            face_col[on_plane] = np.clip(
                cols[on_plane] * 0.45 + np.array([0.42, 0.10, 0.10]) * 0.75, 0, 1)

    img = _background(w, h, mode, bg, env)
    zbuf = np.full((h, w), -1e18, dtype=np.float64)
    if is_pbr:
        g_n = np.zeros((h, w, 3), dtype=np.float32)
        g_a = np.zeros((h, w, 3), dtype=np.float32)
        g_m = np.zeros((h, w, 2), dtype=np.float32)
        g_hit = np.zeros((h, w), dtype=bool)

    X, Y, Z = proj(tris.reshape(-1, 3))
    X, Y, Z = X.reshape(-1, 3), Y.reshape(-1, 3), Z.reshape(-1, 3)

    # FRONT TO BACK, not back to front. The z-buffer already resolves depth, so
    # painter ordering bought nothing and cost everything: every triangle was
    # fully rasterised even when nearer geometry had already covered its box.
    # Nearest-first lets an occluded triangle be rejected by one min() over its
    # bounding box, before any barycentric work. Larger z is nearer here, so
    # descending mean-z is front to back.
    #
    # The reject is conservative — it fires only when the triangle's NEAREST
    # point is still behind the FARTHEST depth already written in its box, which
    # cannot hide a pixel it would have won. Same image, less work.
    xmins = np.maximum(np.floor(X.min(1)).astype(np.int64), 0)
    xmaxs = np.minimum(np.ceil(X.max(1)).astype(np.int64) + 1, w)
    ymins = np.maximum(np.floor(Y.min(1)).astype(np.int64), 0)
    ymaxs = np.minimum(np.ceil(Y.max(1)).astype(np.int64) + 1, h)
    zmaxs = Z.max(1)

    for i in np.argsort(-Z.mean(1)):
        xmin, xmax = int(xmins[i]), int(xmaxs[i])
        ymin, ymax = int(ymins[i]), int(ymaxs[i])
        if xmin >= xmax or ymin >= ymax:
            continue
        sub = zbuf[ymin:ymax, xmin:xmax]
        if zmaxs[i] <= sub.min():
            continue                      # wholly behind what is already drawn
        # Broadcasting instead of meshgrid: the arithmetic below produces the
        # same (ny, nx) arrays without materialising two of them per triangle.
        # meshgrid alone was 71k calls on one reference design.
        px = (np.arange(xmin, xmax) + 0.5)[None, :]
        py = (np.arange(ymin, ymax) + 0.5)[:, None]
        ax_, ay_ = X[i, 0], Y[i, 0]
        bx, by = X[i, 1], Y[i, 1]
        cx_, cy_ = X[i, 2], Y[i, 2]
        det = (by - ay_) * (cx_ - ax_) - (bx - ax_) * (cy_ - ay_)
        if abs(det) < 1e-12:
            continue
        w0 = ((by - ay_) * (px - ax_) - (bx - ax_) * (py - ay_)) / det
        w1 = ((py - ay_) * (cx_ - ax_) - (px - ax_) * (cy_ - ay_)) / det
        w2 = 1.0 - w0 - w1
        m = (w0 >= -1e-9) & (w1 >= -1e-9) & (w2 >= -1e-9)
        if not m.any():
            continue
        zz = w2 * Z[i, 0] + w1 * Z[i, 1] + w0 * Z[i, 2]
        upd = m & (zz > sub)
        if not upd.any():
            continue
        sub[upd] = zz[upd]
        if is_pbr:
            vn = vnorm[i]
            # same weights as zz: w2 -> vertex 0, w1 -> vertex 1, w0 -> vertex 2
            nx = w2 * vn[0, 0] + w1 * vn[1, 0] + w0 * vn[2, 0]
            ny = w2 * vn[0, 1] + w1 * vn[1, 1] + w0 * vn[2, 1]
            nz = w2 * vn[0, 2] + w1 * vn[1, 2] + w0 * vn[2, 2]
            gn = g_n[ymin:ymax, xmin:xmax]
            gn[upd, 0] = nx[upd]
            gn[upd, 1] = ny[upd]
            gn[upd, 2] = nz[upd]
            g_a[ymin:ymax, xmin:xmax][upd] = alb[i]
            g_m[ymin:ymax, xmin:xmax][upd] = mats[i]
            g_hit[ymin:ymax, xmin:xmax][upd] = True
        elif not is_wire:
            img[ymin:ymax, xmin:xmax][upd] = face_col[i]

    if is_pbr and g_hit.any():
        iy, ix = np.nonzero(g_hit)
        N = g_n[iy, ix]
        nl = np.linalg.norm(N, axis=1)
        bad = nl < 1e-9
        N[bad] = c.astype(np.float32)
        nl[bad] = 1.0
        N = N / nl[:, None]

        if projection == "perspective":
            # every pixel looks in a slightly different direction — and it must
            # be the SAME focal and centre the geometry was projected through,
            # or the shading disagrees with the silhouette
            sxp = (ix + 0.5 - w / 2.0) / focal + nxc
            syp = (iy + 0.5 - h / 2.0) / focal + nyc
            V = (c[None, :] - sxp[:, None] * r[None, :] - syp[:, None] * u[None, :])
            V = (V / np.linalg.norm(V, axis=1, keepdims=True)).astype(np.float32)
        else:
            V = np.repeat(c.astype(np.float32)[None, :], len(ix), axis=0)

        # A silhouette normal that has tipped just past the horizon shades as
        # if it were facing away and goes black. Nudge it back into view.
        NoV = np.einsum("ij,ij->i", N, V)
        turn = NoV < 0.02
        if turn.any():
            N[turn] = N[turn] - V[turn] * (NoV[turn] - 0.02)[:, None]
            N[turn] /= np.maximum(np.linalg.norm(N[turn], axis=1, keepdims=True), 1e-9)

        rgb = _shade_pbr(N, V, g_a[iy, ix], g_m[iy, ix, 0], g_m[iy, ix, 1],
                         env, LIGHT_RIG) * float(exposure)
        if ao:
            occ = _ssao(zbuf, g_hit, radius_px=max(2.0, min(w, h) * 0.012),
                        depth_scale=max(span * 0.02,
                                        depth_span * 0.02 if projection == "ortho"
                                        else span * 0.02))
            rgb *= occ[iy, ix][:, None]
        img[iy, ix] = _tonemap(rgb) ** (1.0 / 2.2)

    # Connector overlay: a bright triad at each mating frame, drawn on top of
    # everything so reference geometry reads as reference geometry. Red is the
    # mating direction, green the roll reference.
    if connectors:
        # NB: do not name locals r/u/c here — `proj` closes over the camera
        # basis (r, u, c) and shadowing them silently reprojects the whole
        # overlay through the wrong axes.
        L = span * 0.055
        for cn in connectors:
            o = np.array(cn.pos, dtype=float)
            cdir = np.array(cn.dir, dtype=float)
            cup = np.array(cn.up, dtype=float)
            for axis, col in ((cdir, (0.95, 0.25, 0.25)), (cup, (0.35, 0.9, 0.4))):
                a2 = proj(np.array([o]))
                b2 = proj(np.array([o + axis * L]))
                x0, y0 = a2[0][0], a2[1][0]
                x1, y1 = b2[0][0], b2[1][0]
                n = int(max(abs(x1 - x0), abs(y1 - y0))) + 2
                t = np.linspace(0, 1, n * 2)
                ix = np.round(x0 + (x1 - x0) * t).astype(int)
                iy = np.round(y0 + (y1 - y0) * t).astype(int)
                ok = (ix >= 2) & (ix < w - 2) & (iy >= 2) & (iy < h - 2)
                ix, iy = ix[ok], iy[ok]
                for dx in (-1, 0, 1, 2):
                    for dy in (-1, 0, 1, 2):
                        img[iy + dy, ix + dx] = col

    # Leader / reference lines: thin, dashed, blended so they read as
    # annotation over the model, never as part of it. Same projection the
    # geometry went through; no depth test on purpose — a leader that
    # vanished behind the part it points at would say nothing.
    if overlay_lines:
        for p0, p1, lc in overlay_lines:
            lc = np.clip(np.array(lc, dtype=float), 0, 1)
            a2 = proj(np.array([p0], dtype=float))
            b2 = proj(np.array([p1], dtype=float))
            x0, y0 = float(a2[0][0]), float(a2[1][0])
            x1, y1 = float(b2[0][0]), float(b2[1][0])
            ns = int(max(abs(x1 - x0), abs(y1 - y0))) + 2
            lt = np.linspace(0.0, 1.0, ns * 2)
            lx = np.round(x0 + (x1 - x0) * lt).astype(np.int64)
            ly = np.round(y0 + (y1 - y0) * lt).astype(np.int64)
            # dash on the sample index — the samples are evenly spaced on
            # the segment, so this is a uniform dash without an arc table
            dash = (np.arange(len(lx)) % (9 * ss)) < (6 * ss)
            okl = dash & (lx >= 1) & (lx < w - 1) & (ly >= 1) & (ly < h - 1)
            lx, ly = lx[okl], ly[okl]
            for ddx in (0, 1):
                for ddy in (0, 1):
                    sl = (ly + ddy, lx + ddx)
                    img[sl] = img[sl] * 0.35 + lc[None, :] * 0.65

    if edges:
        bias = (span / min(w, h)) * 1.6
        if projection == "perspective":
            # depth is now distance from the eye, not a world coordinate, so
            # the bias has to be in those units or every edge is hidden
            bias = depth_span / min(w, h) * 1.6 + span * 0.0015
        dim = 0.40 if is_pbr else 0.25
        period, duty = WIRE_DASH

        def _ink(ix, iy, value):
            """Wireframe SETS its ink instead of multiplying it.

            Multiplying compounds wherever two edges overlap — and on a
            wireframe, where nothing hides the edges behind, they overlap
            constantly and the drawing goes blotchy.
            """
            for dx in (0, 1):
                for dy in (0, 1):
                    sl = (iy + dy, ix + dx)
                    img[sl] = np.minimum(img[sl], value)

        # ONE PASS OVER EVERY SEGMENT OF EVERY EDGE. This was a Python loop
        # per segment, and on a real assembly there are a great many segments:
        # MEASURED on rc_car, 458 158 of them, each doing a linspace, two
        # rounds, two astypes and a fancy-index compare. 3.6 s inside linspace
        # alone, 0.9 M rounds, 1.4 M astypes, and several seconds more of
        # interpreter overhead wrapped round arrays four elements long.
        #
        # The arithmetic below is the SAME arithmetic; only the loop is gone.
        # Every segment is built at once and the ragged sample counts are
        # carried by `np.repeat` + an offset, which is how a variable-length
        # linspace is written without a loop.
        if edge_pts:
            lens = np.array([len(q) for q in edge_pts], dtype=np.int64)
            allp = np.vstack(edge_pts)
            ex, ey, ez = proj(allp)

            # A SEGMENT MUST NEVER SPAN TWO EDGES. Point i pairs with i+1, so
            # the last point of each polyline starts no segment — drop exactly
            # those and nothing is ever drawn between the end of one edge and
            # the start of the next.
            first_pt = np.concatenate(([0], np.cumsum(lens)))[:-1]
            keep = np.ones(len(allp), dtype=bool)
            keep[first_pt + lens - 1] = False
            si = np.nonzero(keep)[0]

            if len(si):
                x0, y0, z0 = ex[si], ey[si], ez[si]
                dxp = ex[si + 1] - x0
                dyp = ey[si + 1] - y0
                dzp = ez[si + 1] - z0
                # int(max(|dx|,|dy|)) + 1 steps, sampled twice over — verbatim
                maxd = np.maximum(np.abs(dxp), np.abs(dyp))
                nsamp = (maxd.astype(np.int64) + 1) * 2 + 2
                total = int(nsamp.sum())
                segid = np.repeat(np.arange(len(si), dtype=np.int64), nsamp)
                off = np.concatenate(([0], np.cumsum(nsamp)))[:-1]
                # np.linspace(0, 1, n) is `arange(n) * (1/(n-1))` with the
                # last element PINNED to exactly 1.0 — it multiplies by the
                # reciprocal, it does not divide. Dividing here instead cost a
                # last-ulp difference in `t`, which moved `sarc` across one
                # dash boundary and changed exactly ONE PIXEL of the plate's
                # hidden-line view. Reproduce linspace, do not approximate it.
                inv = 1.0 / (nsamp - 1).astype(np.float64)
                t = (np.arange(total, dtype=np.float64) - off[segid]) * inv[segid]
                t[off + nsamp - 1] = 1.0

                # ARC LENGTH IS ONLY EVER USED BY THE DASH PATTERN, so it is
                # computed only when there are dashes to place — which is the
                # cheaper path for every solid render in the repo.
                #
                # And it is computed to the LAST BIT of what the loop produced,
                # because two shortcuts that look exact are not:
                #
                #   * `np.cumsum(x) - x` is NOT the sequential running total.
                #     (a+b+c)-c != a+b in floating point. MEASURED over 500
                #     segments: it misses the loop's own answer by up to
                #     9.1e-13, where an exclusive prefix is exact every time.
                #   * `np.hypot` is NOT `math.hypot`. MEASURED over 200 000
                #     random pairs: 32 307 of them differ — 16% — by up to
                #     1.4e-14. CPython's two-argument hypot is a compensated
                #     algorithm and C's is not.
                #
                # Either one alone moved a sample across a dash boundary and
                # changed exactly ONE SUBPIXEL of the plate's hidden-line view.
                # A 1e-14 error in a drafting convention is meaningless, and
                # that is the reason to eliminate it rather than argue about
                # it: a check that tolerates a pixel cannot see the next bug
                # that costs one. The Python-level hypot over the segments
                # costs ~0.1 s against the ~8 s this rewrite saves.
                sarc = None
                if hidden:
                    seg = np.fromiter(
                        (math.hypot(float(a), float(b)) for a, b in zip(dxp, dyp)),
                        dtype=np.float64, count=len(dxp))
                    segper = lens - 1
                    run = np.concatenate(([0.0], np.cumsum(seg)[:-1]))
                    polyid = np.repeat(np.arange(len(lens), dtype=np.int64), segper)
                    fseg = np.concatenate(([0], np.cumsum(segper)))[:-1]
                    fseg = np.minimum(fseg, max(len(seg) - 1, 0))
                    arc0 = run - run[fseg][polyid] if len(polyid) else run
                    sarc = arc0[segid] + t * seg[segid]

                lz = z0[segid] + dzp[segid] * t
                ix = np.round(x0[segid] + dxp[segid] * t).astype(np.int64)
                iy = np.round(y0[segid] + dyp[segid] * t).astype(np.int64)

                ok = (ix >= 1) & (ix < w - 1) & (iy >= 1) & (iy < h - 1)
                ix, iy, lz = ix[ok], iy[ok], lz[ok]
                if sarc is not None:
                    sarc = sarc[ok]
                sid = segid[ok]
                if len(ix):
                    vis = lz >= zbuf[iy, ix] - bias
                    if is_wire:
                        _ink(ix[vis], iy[vis], WIRE_VISIBLE)
                    else:
                        vy, vx, vi = iy[vis], ix[vis], sid[vis]
                        # ONE FACTOR OF `dim` PER SEGMENT THAT INKS A PIXEL —
                        # which is exactly what the loop did, because numpy's
                        # BUFFERED in-place fancy-index multiply applies once
                        # per distinct index however many samples land on it.
                        # Two different segments crossing one pixel still
                        # compound, as they did. Counting samples instead would
                        # roughly double every exponent and blacken the drawing.
                        for dx in (0, 1):
                            for dy in (0, 1):
                                yy, xx = vy + dy, vx + dx
                                flat = yy * w + xx
                                once = np.unique(vi * (h * w) + flat) % (h * w)
                                pix, cnt = np.unique(once, return_counts=True)
                                img[pix // w, pix % w] *= (dim ** cnt)[:, None]
                    if hidden:
                        # THE ONE THING THIS REWRITE CHANGES, stated rather than
                        # buried. The old loop interleaved the two inks segment
                        # by segment — dim the visible pixels of segment k, then
                        # lay segment k's dashes, then move on. This lays all the
                        # visible ink and then all the dashes.
                        #
                        # A pixel is only affected if it receives BOTH: a visible
                        # edge from one segment and a hidden dash from another.
                        # `min(x, HIDDEN) * dim` and `min(x * dim, HIDDEN)` are
                        # not the same number. MEASURED, cad mode with hidden
                        # lines on: ONE subpixel of 4.2 M on the reference plate
                        # (5/255 after supersampling) and one on the ring.
                        #
                        # The old answer was not the right one either — it
                        # depended on the order `shp.Edges` happened to come
                        # back in. This one does not depend on anything.
                        # Every other mode is byte-identical and checked to be.
                        dash = (np.mod(sarc, period) < period * duty)
                        hid = (~vis) & dash
                        if hid.any():
                            _ink(ix[hid], iy[hid], WIRE_HIDDEN)

    img = img.reshape(H, ss, W, ss, 3).mean(axis=(1, 3))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    # dpi=100 so figsize * dpi lands on EXACTLY the pixels we rasterised.
    #
    # It was 155, and figsize is in hundredths, so every PNG this repo has ever
    # written was matplotlib's INTERPOLATED UPSCALE of the real render: a
    # 1240x840 buffer written out at 1922x1302. 1.55x in each axis, 2.4x the
    # pixels to encode, and not one of them carried detail the renderer had —
    # the supersampling we pay for at ss=2 was being resampled away again on
    # the way to disk. Measured: 0.043 s in matplotlib._image.resample plus
    # 0.053 s in the PNG encoder, per render, for a blurrier picture.
    #
    # 1:1 is sharper, smaller on disk and faster. If a bigger PNG is wanted,
    # raise W and H — that renders more detail, where dpi only stretched it.
    #
    # THE PNGs DID CHANGE, AND THE COMMIT THAT LANDED THIS SAID OTHERWISE.
    # 3462ff0's message claimed "verified PIXEL-IDENTICAL" over a change that
    # also moved every file from 1922x1302 to 1240x840. Two images of different
    # dimensions cannot be pixel-identical, and a reader would have taken it as
    # "the PNGs did not change". Precisely, measured:
    #
    #   the rasterizer change and the background cache ARE pixel-identical —
    #     compared at the SAME dpi, 0 differing pixels of 2,502,444
    #   this dpi change is NOT — it removes matplotlib's 1.55x upscale, so the
    #     file is now exactly the pixels the rasterizer produced
    #
    # No detail is lost, and that is a different claim: downscaling the old
    # 1922x1302 back to 1240x840 lands within 0.13/255 mean of the new file
    # (max 51, 0.70% of pixels off by >= 8/255). That residual is the round
    # trip's own resampling error, which is the evidence the old file was an
    # upscale rather than a render.
    #
    # Caught by another session reading the claim against the file sizes on
    # disk instead of taking it. "Identical to WHAT" was the right question.
    tl, tfs, band = ([], 0.0, 0) if not title else title_band(title, W)
    fig_h = H + band
    fig = plt.figure(figsize=(W / 100.0, fig_h / 100.0), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1 - (band / float(fig_h) if band else 0)])
    ax.imshow(np.clip(img, 0, 1), origin="lower")
    ax.axis("off")
    if title:
        _draw_title(fig, tl, tfs, band, fig_h)
    fig.savefig(path, facecolor="white")
    plt.close(fig)

    # READ IT BACK BEFORE FILING IT. `bin/feaimage` has done this since it was
    # written [r17]; the CAD render path never did, so a render that produced
    # a white rectangle was indistinguishable from one that produced a
    # bracket — both were "a PNG on disk", and the catalog recorded either
    # with equal confidence.
    #
    # The verification happens BEFORE `_cache_put`, on purpose: a blank that
    # reached the cache would be served as a hit for every future render with
    # the same inputs, and the cache is content-addressed, so it would never
    # re-render and never recover. One blank would become permanent.
    facts = None
    if not os.environ.get("CAD_NO_VERIFY_RENDER"):
        facts = verify_render(path)          # raises BlankRender, naming it
    _cache_put(key, path)
    if verbose:
        tag = mode + ("" if projection == "ortho" else f"/{projection} {fov:g}deg")
        extra = ("" if not facts else
                 f", ink={facts['ink_frac']:.4f}")
        print(f"  rendered {path}  ({len(tris)} tris, view={view}, {tag}{extra})")
    return path


def contact_sheet(obj, path, views=("iso", "front", "right", "top"), title=None,
                  W=620, H=430, **kw):
    """One PNG with several standard views — the fastest way to actually see a part."""
    # Same skip as render() — it reads its own per-view temp PNGs back, so
    # letting render() skip underneath it would crash on the missing files.
    if os.environ.get("CAD_NO_RENDER", "").lower() in ("1", "true", "yes"):
        print(f"  [render skipped] {path} (CAD_NO_RENDER=1 — "
              "any existing PNG there is stale)")
        return None
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg
    import tempfile

    tmp = []
    for v in views:
        f = os.path.join(tempfile.gettempdir(), f"_cs_{abs(hash((path, v)))}.png")
        render(obj, f, view=v, title=None, W=W, H=H, verbose=False, **kw)
        tmp.append((v, f))

    cols = 2 if len(tmp) > 1 else 1
    rows = (len(tmp) + cols - 1) // cols
    # dpi=100, same reason as render(): at 150 each cell was 1.5x wider than
    # the render feeding it (620 px source into a 930 px cell), so the sheet
    # was an upscale of an upscale. This is the path that matters most —
    # catalog.py:203 uses contact_sheet for every non-thumb auto-render, and
    # those bytes are what a dashboard card shows.
    fig, axes = plt.subplots(rows, cols, figsize=(cols * W / 100.0, rows * H / 100.0), dpi=100)
    axes = np.atleast_1d(axes).ravel()
    for ax in axes:
        ax.axis("off")
    for ax, (v, f) in zip(axes, tmp):
        ax.imshow(mpimg.imread(f))
        ax.set_title(v, fontsize=11, fontweight="bold", color="#333")
    if title:
        # Same measurement as render()'s band: a contact sheet's caption is
        # the same provenance line and gets clipped the same way.
        tl, tfs, _b = title_band(title, cols * W, fs=14.0)
        fig.suptitle("\n".join(tl), fontsize=tfs, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, (0.97 - 0.012 * (len(tl) - 1)) if title else 1))
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    for _, f in tmp:
        try:
            os.remove(f)
        except OSError:
            pass
    print(f"  rendered {path}  (contact sheet: {', '.join(v for v, _ in tmp)})")
    return path


# ---------------------------------------------------------------------------
# joint-directed exploded views — the plan comes from cecad.explode
# ---------------------------------------------------------------------------
_LEADER_COL = (0.42, 0.44, 0.50)     # leader-line ink: light, reads as reference
_GHOST_MIX = 0.74                    # how far a held part fades toward white


def plan_displacements(plan, t=1.0):
    """{row path: that row's OWN displacement tuple} = vector * distance * t.

    Stage nesting is applied by `leaf_displacement`, which sums a leaf's own
    row with every ancestor row — a stage-1 part inside a stage-0 unit rides
    the unit AND travels its own withdrawal. Pure tuples, so the placement
    math is testable without a kernel (tests/test_exploded_render.py).
    """
    out = {}
    for r in plan.rows:
        out[r.path] = (r.vector[0] * r.distance_mm * t,
                       r.vector[1] * r.distance_mm * t,
                       r.vector[2] * r.distance_mm * t)
    return out


def leaf_displacement(offsets, leaf_path):
    """Total world displacement of one leaf: its own row + every ancestor row.

    An ancestor is a row whose path is a strict '/'-prefix of the leaf's —
    "drive" moves "drive/motor_b1"; "drive/motor" does NOT (motor_b1 is not
    under motor). Rows for unrelated parts contribute nothing.
    """
    d = [0.0, 0.0, 0.0]
    for p, v in offsets.items():
        if leaf_path == p or leaf_path.startswith(p + "/"):
            d[0] += v[0]
            d[1] += v[1]
            d[2] += v[2]
    return (d[0], d[1], d[2])


def _exploded_layout(assembly, plan=None, part=None, t=1.0, spread=1.6,
                     axis="z", ghost=True):
    """Place every leaf of `assembly` for an exploded picture.

    Returns (shapes, leaders, caption, plan_used):
      shapes   [(shape, (r,g,b), material)] with moved placements
      leaders  [(assembled_center, exploded_center)] one per moved leaf
      caption  states HOW the picture was made — constraint plan, single-part
               pull, or the naive spread fallback — so nobody mistakes a
               hero shot for an assembly drawing
      plan_used  the cecad.explode.Plan, or None when the naive path drew it

    plan=None derives a joint-directed plan; plan=False forces the old naive
    spread; a Plan instance is drawn exactly as given. part= pulls one named
    node out along its plan vector with everything else held (ghosted).
    """
    naive_reason = None
    if part is not None:
        from .explode import explosion_plan
        if plan is None or plan is False:
            plan = explosion_plan(assembly, mode=("part", str(part)),
                                  spread=spread)
    elif plan is False:
        plan, naive_reason = None, "requested"
    elif plan is None:
        from .explode import explosion_plan
        try:
            plan = explosion_plan(assembly, spread=spread)
        except Exception as e:                       # a model the planner refuses
            plan, naive_reason = None, f"plan failed: {e}"
        if plan is not None and not any(
                r.distance_mm > 0 and any(r.vector)
                and r.basis in ("fastener", "joint-axis")
                for r in plan.rows):
            # NOT ONE row was derived from a joint — every mover would be a
            # centroid guess. A guess dressed as a constraint explosion is a
            # lie about structure, so this draws the naive spread and SAYS so.
            # A model with SOME derived rows keeps the plan, and the caption
            # counts the guessed ones.
            plan, naive_reason = None, "no derivable joints"

    shapes, leaders = [], []
    if plan is None:
        # THE NAIVE SPREAD, kept as the stated fallback: one global axis,
        # offsets scaled from bbox centres. Directions have nothing to do
        # with how the parts are joined, and the caption says so.
        ai = {"x": 0, "y": 1, "z": 2}[axis]
        # colour by ORIGINAL item index, so a part keeps the colour the
        # assembled render gave it; the sort only orders the offsets
        items = sorted(enumerate(assembly.items),
                       key=lambda e: e[1][2].BoundBox.Center[ai])
        ctr = (sum(it[2].BoundBox.Center[ai] for _, it in items)
               / len(items))
        for i, (label, p, shp, col) in items:
            d = [0.0, 0.0, 0.0]
            d[ai] = (shp.BoundBox.Center[ai] - ctr) * spread
            s = shp.copy()
            s.Placement = App.Placement(shp.Placement.Base + App.Vector(*d),
                                        shp.Placement.Rotation)
            shapes.append((s, _color(col, i), p.material))
        caption = f"naive spread along {axis} ({naive_reason}) — no joint data used"
        return shapes, leaders, caption, None

    offsets = plan_displacements(plan, t=t)
    target = str(part) if part is not None else None
    for i, (label, p, shp, col) in enumerate(assembly.items):
        d = leaf_displacement(offsets, label)
        moved = any(abs(x) > 1e-9 for x in d)
        s = shp.copy()
        if moved:
            s.Placement = App.Placement(shp.Placement.Base + App.Vector(*d),
                                        shp.Placement.Rotation)
        c = _color(col, i)
        if target is not None and ghost and not (
                label == target or label.startswith(target + "/")):
            # the inspect-this-part view: everything held fades toward white
            c = tuple(v * (1.0 - _GHOST_MIX) + _GHOST_MIX for v in c)
        shapes.append((s, c, p.material))
        if moved:
            c0 = shp.BoundBox.Center
            leaders.append(((c0.x, c0.y, c0.z),
                            (c0.x + d[0], c0.y + d[1], c0.z + d[2])))

    counts = plan.basis_counts()
    derived = counts.get("fastener", 0) + counts.get("joint-axis", 0)
    guessed = counts.get("centroid-fallback", 0)
    if target is not None:
        trow = next((r for r in plan.rows if r.path == target), None)
        basis = trow.basis if trow is not None else "?"
        caption = (f"part explosion — {target} out on its {basis} axis, "
                   f"rest held" + (" (ghosted)" if ghost else ""))
    else:
        caption = (f"constraint explosion — {plan.stages} stage(s), "
                   f"{derived} joint-directed, {guessed} centroid-fallback")
        un = counts.get("unattached", 0)
        if un:
            caption += f", {un} unattached held"
    return shapes, leaders, caption, plan


def exploded(assembly, path, spread=1.6, axis="z", plan=None, part=None,
             t=1.0, leaders=True, ghost=True, **kw):
    """Render an assembly exploded ALONG ITS OWN JOINTS.

    With joint data present, every part leaves along the axis its own joint
    withdraws on (cecad.explode.explosion_plan): a screw backs out along its
    thread, a press fit along the fit, a sub-assembly leaves as a UNIT and
    explodes internally in a later stage, and distances are staged so the
    stack order reads. Leader lines run from each part back to its
    assembled place, like an assembly drawing. The caption on the image
    states which mode drew it — never pass a naive spread off as a
    constraint explosion.

        exploded(a, "out/x.png")                          # joint-directed
        exploded(a, "out/x.png", part="drive/motor")      # pull ONE part,
                                                          # rest held, ghosted
        exploded(a, "out/x.png", plan=my_plan)            # draw a Plan as-is
        exploded(a, "out/x.png", plan=False)              # the old naive spread

    plan     None derives a plan from the declared joints; a
             cecad.explode.Plan is drawn exactly; False forces the naive
             axis spread (kept as the no-joints fallback — an assembly whose
             plan moves nothing falls back too, and the caption says so).
    part     node path to pull out alone; everything else held at its
             assembled place and ghosted (ghost=False keeps full colour).
    t        scales every travel: 1.0 = the plan's full distances.
    leaders  draw the dashed line from exploded back to assembled position.
    spread / axis   scale the plan's distances / feed the naive fallback.
    """
    shapes, lead, caption, used = _exploded_layout(
        assembly, plan=plan, part=part, t=t, spread=spread, axis=axis,
        ghost=ghost)
    title = kw.pop("title", None)
    title = f"{title} — {caption}" if title else caption
    ol = kw.pop("overlay_lines", None)
    if leaders and lead:
        ol = list(ol or []) + [(a, b, _LEADER_COL) for a, b in lead]
    print(f"  exploded: {caption}")
    return render(shapes, path, title=title, overlay_lines=ol, **kw)


def compare(obj, path, view="iso", title=None, modes=MODES, **kw):
    """The same model in every shading mode, side by side.

    Use it when deciding which mode a picture wants — and to prove they all
    agree on the geometry, which is the only thing they must agree on.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg
    import tempfile

    W = kw.pop("W", 760)
    H = kw.pop("H", 520)
    tmp = []
    for m in modes:
        f = os.path.join(tempfile.gettempdir(), f"_cmp_{abs(hash((path, m)))}.png")
        render(obj, f, view=view, title=None, verbose=False, mode=m,
               W=W, H=H, **kw)
        tmp.append((m, f))
    n = len(tmp)
    fig, axes = plt.subplots(1, n, figsize=(n * W / 100.0, H / 100.0 + 0.4),
                             dpi=100)      # see contact_sheet, same upscale
    for ax, (m, f) in zip(np.atleast_1d(axes).ravel(), tmp):
        ax.imshow(mpimg.imread(f))
        ax.axis("off")
        ax.set_title(f"mode={m}", fontsize=12, fontweight="bold", color="#333")
    if title:
        fig.suptitle(title, fontsize=14, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.94 if title else 1))
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    for _, f in tmp:
        try:
            os.remove(f)
        except OSError:
            pass
    print(f"  rendered {path}  ({' vs '.join(m for m, _ in tmp)})")
    return path


# ---------------------------------------------------------------------------
# documented() — the three standard pictures of one solid, each citing itself
# ---------------------------------------------------------------------------
#: Bumped when the picture set changes in a way that makes an older sidecar's
#: images no longer comparable. Written into every `docs/images.json`, so
#: "these pictures are from an older standard" is a MEASURABLE fact.
DOC_SHEET_VERSION = 1

#: The three views docs/part-docs.md fixes. They answer three different
#: questions and none substitutes for another:
#:   iso        what IS this thing        shaded, hidden-line, one camera
#:   contact    what are its proportions  iso/front/right/top on one sheet
#:   schematic  what is INSIDE it         wireframe, obscured edges dashed —
#:                                        read structure THROUGH the solid
DOC_KINDS = ("iso", "contact", "schematic")


def _measure(items):
    """(bbox_mm, volume_mm3, solids) read off the shapes themselves."""
    bb = None
    vol = 0.0
    solids = 0
    for shp, _c, _m in items:
        if shp is None:
            continue
        try:
            b = shp.BoundBox
        except Exception:
            continue
        if bb is None:
            bb = App.BoundBox(b)
        else:
            bb.add(b)
        try:
            vol += float(shp.Volume)
        except Exception:
            pass
        try:
            solids += len(shp.Solids)
        except Exception:
            pass
    if bb is None:
        return None, None, 0
    return ([round(bb.XLength, 4), round(bb.YLength, 4), round(bb.ZLength, 4)],
            round(vol, 4), solids)


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def documented(obj, outdir, name, cite, note=None, W=1240, H=840, tol=0.08,
               kinds=DOC_KINDS, verbose=True):
    """Write the standard picture set for one solid, with provenance ON the
    picture and BESIDE it.

    `cite` is the one line that says what this is a picture OF. The CALLER
    composes it, because only the caller knows; docs/part-docs.md fixes the
    grammar. It is drawn into the title strip of every image written here, so
    a PNG that escapes into a chat window still says where it came from.

    House rule: *a picture that does not say what it is a picture OF is
    decoration.* So `cite` is required, and an empty one is refused here
    rather than producing a PNG someone must later archaeologise.

    An EMPTY solid is a refusal, not a blank canvas — a zero-extent shape
    renders as a flat grey field that looks exactly like a working picture of
    nothing. That is checked before any pixel is drawn, so the message names
    the part instead of naming a helper.

    Raises rather than returning a half-set, so a caller counting successes
    cannot count a failure.
    """
    cite = (cite or "").strip()
    if not cite:
        raise ValueError(
            "documented(%r): cite is empty. Every generated image states the "
            "solid it was rendered from and the code that made it "
            "(docs/part-docs.md); an uncited picture is decoration." % name)

    items = _collect(obj)                      # raises a NAMED TypeError
    if not any(s is not None for s, _c, _m in items):
        raise ValueError("documented(%s): build() returned no shape at all — "
                         "there is nothing to picture." % name)
    bbox, vol, solids = _measure(items)
    if bbox is None or max(bbox) <= 0.0:
        raise ValueError(
            "documented(%s): the solid is EMPTY (bounding box %s mm). A "
            "picture of it would be a blank field indistinguishable from a "
            "working render." % (name, bbox))

    stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # The cite normally opens with the ref, which already carries the name —
    # "SG90 · part:SG90 · built by ..." reads as a stutter. Prefix only when
    # the caption would otherwise not say what the thing is called.
    strip = cite if name in cite else "%s  ·  %s" % (name, cite)
    if note:
        strip += "  ·  " + note

    os.makedirs(outdir, exist_ok=True)
    wrote = {}
    for kind in kinds:
        p = os.path.join(outdir, "%s.%s.png" % (name, kind))
        t = "%s  —  %s  —  %s" % (strip, kind, stamp)
        if kind == "contact":
            contact_sheet(obj, p, title=t, W=W // 2, H=H // 2, tol=tol)
        elif kind == "schematic":
            render(obj, p, view="iso", title=t, W=W, H=H, tol=tol,
                   mode="wire", hidden=True, projection="ortho",
                   verbose=verbose)
        else:
            render(obj, p, view=kind, title=t, W=W, H=H, tol=tol,
                   mode="cad", projection="ortho", verbose=verbose)
        wrote[kind] = p

    return {
        "name": name,
        "cite": cite,
        "generated_at": stamp,
        "generator": "cecad.render.documented v%d" % DOC_SHEET_VERSION,
        "measured": {"bbox_mm": bbox, "volume_mm3": vol, "solids": solids,
                     "shapes": len(items)},
        "images": [{"kind": k, "path": p, "bytes": os.path.getsize(p),
                    "sha256": _sha256_file(p)}
                   for k, p in wrote.items()],
    }


# ---------------------------------------------------------------------------
# reading the finished PNG back — a picture, or a named refusal
# ---------------------------------------------------------------------------

#: Ink fraction below which a CAD render is not a picture of anything.
#:
#: MEASURED 2026-08-30 over the renders already on disk, to set this from
#: evidence rather than taste. Real renders (`out/auto/*.png`, `out/*/*.png`)
#: carry an ink fraction of 0.1139 to 0.4190 and 187 to 5311 distinct colours.
#: A blank canvas is ink 0.0 with 1 colour. A title-caption-only frame — the
#: failure mode that matters, because it LOOKS like a render in a thumbnail
#: strip — lands near 0.005. The floor sits at 0.02: an order of magnitude
#: under the weakest real render and four times the caption-only case.
#: Kept as names other modules may import. The THRESHOLDS now live in one
#: place — `cecad.imgcheck` — because this file had grown a second, parallel
#: rule with a different floor (0.02 against 0.005) and a different notion of
#: background (modal colour of the whole image, which calls a large flat PART
#: the background). Two rules that answer the same question WILL drift, and
#: the calibration proved this one wrong: 0.02 would reject real renders whose
#: measured ink runs down to 0.00573.
RENDER_MIN_INK = None       # -> imgcheck.MIN_INK
RENDER_MIN_COLORS = 2


class BlankRender(Exception):
    """A file was written but it is not a picture of the model."""


def verify_render(path, min_ink=None, min_colors=2):
    """Measured facts about a rendered PNG, or `BlankRender` naming the fault.

    THIS IS NOW A THIN WRAPPER over `cecad.imgcheck.verify_png`, deliberately.

    It used to carry its own implementation, and independently rediscovered
    the same trap imgcheck did — that a long thin rod inks ~1% of a frame and
    must not be called blank — then solved it a different way (an ink SPAN
    measured below an excluded caption band). Both solutions were reasonable
    and having both was the bug: two functions answering "is this a picture?"
    with different numbers, only one of which anybody was calibrating.

    imgcheck's rule is the stronger of the two. It measures the largest
    CONNECTED mark, so it needs no assumption about where a caption sits, and
    it refuses a dense multi-line caption that a span rule passes. The
    exception type and the returned keys are kept so existing callers do not
    change.
    """
    from .imgcheck import BlankImage, verify_png as _v
    try:
        f = _v(path, min_colors=min_colors, what="render",
               **({} if min_ink is None else {"min_ink": min_ink}))
    except BlankImage as e:
        raise BlankRender(str(e))
    return {"bytes": f["bytes"], "size": f["size"],
            "distinct_colors": f["distinct_colors"],
            "ink_frac": f["ink_frac"], "background": tuple(f["bg_rgb"]),
            "max_stroke": f["max_stroke"],
            "thin_part": f["ink_frac"] < 0.02}
