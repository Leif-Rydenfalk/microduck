"""dfm_orient.py — the orientation pass, with the BED taken out of the count.

    ce-cad/bin/cad tools/dfm_orient.py      # merges into out/dfm/dfm-rebuilt.json

WHY THIS EXISTS. tools/dfm_rebuilt.py measures overhang as "area of facets
whose angle to the build plate beta is under 30 deg". That number is right and
it is also USELESS FOR PICKING AN ORIENTATION, because the part's whole FLAT
BOTTOM is a beta = 0 facet and it is not unsupported — it is lying on the bed.
MEASURED, and this is what caught it: microduck-trunk-base, a 57 x 36 x 3 mm
flat plate, scored 43.7% beta<30 laid flat (+Z) and 2.4% stood on its 57 mm
edge, so the naive ranking recommended printing a 3 mm plate on edge, 285
layers tall. That is a wrong answer produced by a correct measurement.

THE FIX, and it is still a measurement: split the beta<30 area into
  * ON THE PLATE — every vertex of the facet within one first layer of the
    part's lowest point in that build direction. The bed carries it.
  * ELEVATED — everything else. That is what support material has to reach.
and rank orientations on ELEVATED area only.

WHAT IT STILL IS NOT. An elevated down-face that spans between two walls is a
BRIDGE and prints; one with nothing on either side is an island and does not.
This does not tell them apart, and no tool in ce-cad does, so `elevated_lt30`
is an UPPER BOUND on support and is labelled as one. Bed adhesion (footprint
area) and part height are reported beside it because a tie on support is
broken by whichever stands shorter on a wider foot.

Every run re-checks itself against solids whose answer is known first.
"""
import json, math, os, struct, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, "tools/dfm_rebuilt.py")).read()
_ns = {"np": np, "math": math, "os": os, "struct": struct}
exec(src[src.index("def read_stl"):src.index("def wall_rays")], _ns)
read_stl, overhang = _ns["read_stl"], _ns["overhang"]

DIRS = {"+X": (1.,0.,0.), "-X": (-1.,0.,0.), "+Y": (0.,1.,0.),
        "-Y": (0.,-1.,0.), "+Z": (0.,0.,1.), "-Z": (0.,0.,-1.)}
LAYER = 0.2
FIRST_LAYER = 0.2        # a facet whose HIGHEST vertex is within this of the
                         # part's lowest point is lying on the build plate


def orient(V, N, A, u):
    """One build direction, with the bed's own contact area taken out."""
    u = np.asarray(u, float)
    d = -(N @ u)                       # 1 = flat down-face, 0 = vertical wall
    h = V @ u                          # (nf, 3) vertex heights
    hmin, hmax = float(h.min()), float(h.max())
    on_bed = h.max(axis=1) <= hmin + FIRST_LAYER
    tot = float(A.sum())
    out = {"height_mm": round(hmax - hmin, 4),
           "layers_at_0p2": int(math.ceil((hmax - hmin) / LAYER)),
           "bed_contact_mm2": round(float(A[on_bed & (d > 0.5)].sum()), 3)}
    for tag, beta in (("lt45", 45.), ("lt30", 30.), ("lt10", 10.)):
        m = d > math.cos(math.radians(beta))
        out["all_" + tag + "_mm2"] = round(float(A[m].sum()), 3)
        out["elevated_" + tag + "_mm2"] = round(float(A[m & ~on_bed].sum()), 3)
        out["elevated_" + tag + "_frac"] = (
            round(float(A[m & ~on_bed].sum() / tot), 6) if tot else None)
    return out


def check():
    """Known answers first, or the numbers below are not evidence."""
    def mesh(t):
        Vv = np.array(t, float)
        cr = np.cross(Vv[:,1]-Vv[:,0], Vv[:,2]-Vv[:,0])
        ln = np.linalg.norm(cr, axis=1)
        return Vv, cr/ln[:,None], ln*0.5
    c = []
    def quad(a,b,cc,dd): c.append([a,b,cc]); c.append([a,cc,dd])
    P = lambda x,y,z: (x,y,z)
    quad(P(0,10,0),P(10,10,0),P(10,0,0),P(0,0,0))       # bottom, outward -Z
    quad(P(0,0,10),P(10,0,10),P(10,10,10),P(0,10,10))   # top,    outward +Z
    quad(P(0,0,0),P(10,0,0),P(10,0,10),P(0,0,10))       # -Y
    quad(P(10,10,0),P(0,10,0),P(0,10,10),P(10,10,10))   # +Y
    quad(P(10,0,0),P(10,10,0),P(10,10,10),P(10,0,10))   # +X
    quad(P(0,10,0),P(0,0,0),P(0,0,10),P(0,10,10))       # -X
    V, N, A = mesh(c)
    assert len({tuple(np.round(n,3)) for n in N}) == 6
    o = orient(V, N, A, (0,0,1))
    print("  cube 10 mm, +Z: all_lt30 %.1f  bed_contact %.1f  ELEVATED_lt30 %.1f"
          " (expect 100 / 100 / 0)  h %.1f  layers %d"
          % (o["all_lt30_mm2"], o["bed_contact_mm2"], o["elevated_lt30_mm2"],
             o["height_mm"], o["layers_at_0p2"]))
    assert abs(o["all_lt30_mm2"] - 100.0) < 1e-6
    assert abs(o["bed_contact_mm2"] - 100.0) < 1e-6
    assert abs(o["elevated_lt30_mm2"]) < 1e-9, "the bed is not support material"
    assert abs(o["all_lt45_mm2"] - 100.0) < 1e-6, "vertical walls are not overhang"
    assert o["layers_at_0p2"] == 50
    # a table: 10x10x1 slab on 4 legs 5 mm tall -> the slab's underside IS support work
    t = []
    def box(x0,y0,z0,x1,y1,z1):
        pts = [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
               (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
        for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(2,3,7,6),(1,2,6,5),(3,0,4,7)):
            t.append([pts[f[0]],pts[f[1]],pts[f[2]]])
            t.append([pts[f[0]],pts[f[2]],pts[f[3]]])
    box(0,0,5,10,10,6)
    for (x,y) in ((0,0),(9,0),(0,9),(9,9)):
        box(x,y,0,x+1,y+1,5)
    V, N, A = mesh(t)
    o = orient(V, N, A, (0,0,1))
    # NOTE the expected 100, not 96: these are five OVERLAPPING boxes, not a
    # boolean union, so the slab keeps its whole 10 x 10 underside and the four
    # leg tops are buried inside it. The first run of this check asserted 96 and
    # FAILED — the assertion was wrong, the measurement was right, and that is
    # the only reason this line is trustworthy now. all_lt30 = 104 = the slab's
    # 100 underside + the four 1 mm2 leg feet; the feet are the bed contact.
    print("  table (10x10x1 slab on four 1x1x5 legs), +Z: all_lt30 %.1f (expect 104)"
          "  bed_contact %.1f (expect 4)  ELEVATED_lt30 %.1f (expect 100)"
          % (o["all_lt30_mm2"], o["bed_contact_mm2"], o["elevated_lt30_mm2"]))
    assert abs(o["all_lt30_mm2"] - 104.0) < 1e-6, o
    assert abs(o["bed_contact_mm2"] - 4.0) < 1e-6, o
    assert abs(o["elevated_lt30_mm2"] - 100.0) < 1e-6, o
    for beta, w45, w30 in ((20.,1,1), (29.,1,1), (31.,1,0), (44.,1,0), (46.,0,0)):
        r = math.radians(beta)
        n = np.array([math.sin(r), 0., -math.cos(r)])
        e1 = np.array([0.,1.,0.]); e2 = np.cross(n, e1)
        # lift it clear of the plate so it is ELEVATED, not bed contact
        base = np.array([0.,0.,20.])
        tri = [[list(base), list(base+e1*2.), list(base+e2*1.)]]
        Vm, Nm, Am = mesh(tri)
        if float(np.dot(Nm[0], n)) < 0:
            tri = [[tri[0][0], tri[0][2], tri[0][1]]]; Vm, Nm, Am = mesh(tri)
        o = orient(Vm, Nm, Am, (0,0,1))
        g45 = int(o["elevated_lt45_mm2"] > 0); g30 = int(o["elevated_lt30_mm2"] > 0)
        assert (g45, g30) == (w45, w30), (beta, o)
    print("  thresholds bite at 30 and 45 deg exactly")
    print("orient() self-check PASS")


def main():
    print("self-check:")
    check()
    p = os.path.join(ROOT, "out/dfm/dfm-rebuilt.json")
    doc = json.load(open(p))
    print("\n%-36s %-28s %-28s" % ("part", "naive best (bed counted)", "HONEST best (bed removed)"))
    for slug, rec in sorted(doc["parts"].items()):
        stl = os.path.join(ROOT, "out/dfm/stl-rebuilt", slug + ".stl")
        if not os.path.exists(stl):
            rec["orientation"] = {"reason": "no STL at " + stl}
            continue
        V, N, A = read_stl(stl)
        o = {k: orient(V, N, A, u) for k, u in DIRS.items()}
        best = sorted(o.items(), key=lambda kv: (kv[1]["elevated_lt30_mm2"],
                                                 kv[1]["elevated_lt45_mm2"],
                                                 kv[1]["height_mm"]))[0]
        naive = sorted(o.items(), key=lambda kv: (kv[1]["all_lt30_mm2"],
                                                  kv[1]["all_lt45_mm2"],
                                                  kv[1]["height_mm"]))[0]
        rec["orientation"] = {
            "rule": ("rank the six axis-aligned build directions by ELEVATED "
                     "beta<30 deg area (bed contact removed); ties on elevated "
                     "beta<45, then on height. Upper bound on support: a bridge "
                     "between two walls is counted with a floating island."),
            "first_layer_mm": FIRST_LAYER, "by_dir": o,
            "best": best[0], "naive_best_bed_counted": naive[0],
            "best_elevated_lt30_mm2": best[1]["elevated_lt30_mm2"],
            "best_elevated_lt30_frac": best[1]["elevated_lt30_frac"],
            "best_elevated_lt10_mm2": best[1]["elevated_lt10_mm2"],
            "best_bed_contact_mm2": best[1]["bed_contact_mm2"],
            "best_height_mm": best[1]["height_mm"],
            "best_layers": best[1]["layers_at_0p2"],
            "z_up": o["+Z"]}
        print("%-36s %-6s %7.1f mm2 elev   %-6s %7.1f mm2 elev  %5.1f mm tall, "
              "%4d layers, foot %6.1f mm2"
              % (slug.replace("microduck-",""), naive[0],
                 naive[1]["elevated_lt30_mm2"], best[0],
                 best[1]["elevated_lt30_mm2"], best[1]["height_mm"],
                 best[1]["layers_at_0p2"], best[1]["bed_contact_mm2"]))
    doc["$orientation"] = ("out/dfm/dfm-rebuilt.json 'orientation' block added by "
                          "tools/dfm_orient.py — the mesh block's best_build_dir "
                          "counts the bed as unsupported and MUST NOT be used to "
                          "pick an orientation. Use orientation.best.")
    json.dump(doc, open(p, "w"), indent=1)
    print("\nmerged into", p)


main()
