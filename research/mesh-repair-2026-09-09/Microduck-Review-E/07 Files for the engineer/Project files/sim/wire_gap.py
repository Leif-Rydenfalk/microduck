"""wire_gap — THE BATTERY FEED CANNOT BE ROUTED AT ALL. WHERE IS THE WALL?

    ce-cad/bin/cad sim/wire_gap.py

out/wiring/cables3d-hat.json records bat-hat as FAIL with the same line at every
rung of the clearance ladder, 1.0000 mm down to 0.0000 mm: "no corridor on the
4.0 mm grid and none on the 1.0 mm grid either". At a ZERO clearance floor. That
is not a tight fit the router lost; it is a claim that no path of free cells
exists between the pack's contact end and the HAT's battery connector.

The real Microduck runs off that pack, so the correct first conclusion is that
OUR MODEL is wrong, and the useful output is not a verdict but a LOCATION: which
body's material severs the free space, how thick it is there, and what a
pass-through would cost. This pass answers exactly that.

  1. label every connected component of the FREE cells of the 1.0000 mm
     occupancy (26-connectivity, so a diagonal counts -- the most generous
     reading, which makes a severed answer stronger).
  2. say which component every cable endpoint in wiring/cables.json sits in,
     WITH THAT COMPONENT'S SIZE, because "component 84" means nothing until you
     know whether it is a room or a 20-cell blister. An endpoint that is inside
     material, or closer to a surface than the cable is thick, is not in any
     component at all: it is SNAPPED to the nearest cell of the space and the
     snap distance is reported, because a connector sitting on a board is
     supposed to be against a surface and calling that "severed" would be an
     artefact of the question rather than a fact about the robot.
     Two endpoints of one run in two components is a run nothing can route.
  3. for each severed run, measure the THINNEST material between its two
     components: the Euclidean distance from every cell of the far component to
     the near one, minimised over the near component. That distance is the
     length of the shortest pass-through that would join them, its endpoints
     are where to drill, and the owner field names the part it goes through.
  4. repeat the whole thing on the space a CABLE can occupy -- cells at least
     (OD/2 + floor) from any surface -- because a hole a point can pass through
     is not a hole a 3.1243 mm bundle can.

Nothing here proposes a change to any part. It measures what our model says and
names the wall, so the next lane can compare that wall against a photograph.
"""
import json, math, os, sys
from collections import Counter

import numpy as np
from scipy import ndimage

R = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck"
OUT = R + "/out/wiring/gap.json"
OCC = "/private/tmp/int-wire3d/occ.npz"
LABELS = "/private/tmp/int-wire3d/labels.json"
OD = 3.1243
FLOOR = 1.0


def main():
    z = np.load(OCC)
    grid = z["grid"].astype(bool)
    own = z["owner"]
    edt = z["edt"]
    lo = z["lo"]
    cell = float(z["cell"][0])
    shape = np.array(grid.shape)
    labels = json.load(open(LABELS))
    rows = json.load(open(R + "/ce-assemblies/microduck/current/placements.json"))["record"]["rows"]
    row_part = {i + 1: (r.get("part") or r.get("mesh")) for i, r in enumerate(rows)}
    row_mesh = {i + 1: (r.get("mesh") or r.get("part")) for i, r in enumerate(rows)}

    cab = json.load(open(R + "/wiring/cables.json"))["record"]
    c3 = {}
    for name in ("cables3d.json", "cables3d-hat.json"):
        p = os.path.join(R, "out/wiring", name)
        if os.path.exists(p):
            for c in json.load(open(p))["record"]["cables"]:
                c3[c["id"]] = c

    def idx(p):
        c = np.floor((np.asarray(p, float) - lo) / cell).astype(int)
        return tuple(np.clip(c, 0, shape - 1))

    struct = np.ones((3, 3, 3), bool)          # 26-connectivity

    def analyse(free, tag, note):
        lab, n = ndimage.label(free, structure=struct)
        sizes = np.bincount(lab.ravel())
        sizes[0] = 0
        big = int(np.argmax(sizes))
        dfree, ifree = ndimage.distance_transform_edt(~free, sampling=cell, return_indices=True)
        out = {"tag": tag, "note": note, "components": int(n),
               "largest_component_cells": int(sizes[big]),
               "free_cells": int(free.sum()),
               "largest_share_pct": round(100.0 * sizes[big] / max(1, int(free.sum())), 3)}
        # where does every endpoint sit?
        pts = {}
        for c in cab["cables"]:
            e = c3.get(c["id"], {}).get("ends") or []
            for k, key in ((0, "from"), (1, "to")):
                if k < len(e):
                    p = e[k].get("launch_mm") or e[k].get("connector_xyz_mm")
                    if p:
                        pts[(c["id"], c[key])] = p
            if c.get("from_xyz_mm") and (c["id"], c["from"]) not in pts:
                pts[(c["id"], c["from"])] = c["from_xyz_mm"]
            if c.get("to_xyz_mm") and (c["id"], c["to"]) not in pts:
                pts[(c["id"], c["to"])] = c["to_xyz_mm"]
        comp_of, ep_out = {}, {}
        for k, p in pts.items():
            i = idx(p)
            c0 = int(lab[i])
            snap = 0.0
            if c0 == 0:
                j = (int(ifree[0][i]), int(ifree[1][i]), int(ifree[2][i]))
                snap = float(dfree[i])
                c0 = int(lab[j])
            comp_of[k] = c0
            vol = float(sizes[c0]) * cell ** 3 if c0 else 0.0
            ep_out["%s/%s" % k] = {"component": c0, "snapped_mm": round(snap, 4),
                                   "component_cells": int(sizes[c0]) if c0 else 0,
                                   "component_mm3": round(vol, 1),
                                   "is_the_largest_component": c0 == big}
        out["endpoints"] = ep_out
        out["largest_component_id"] = big
        # severed runs
        sev = []
        for c in cab["cables"]:
            ka, kb = (c["id"], c["from"]), (c["id"], c["to"])
            if ka not in comp_of or kb not in comp_of:
                continue
            ca, cb = comp_of[ka], comp_of[kb]
            if ca == cb and ca != 0:
                continue
            row = {"id": c["id"], "from": c["from"], "to": c["to"],
                   "component_from": ca, "component_to": cb,
                   "component_from_cells": int(sizes[ca]) if ca else 0,
                   "component_to_cells": int(sizes[cb]) if cb else 0,
                   "snapped_from_mm": ep_out["%s/%s" % ka]["snapped_mm"],
                   "snapped_to_mm": ep_out["%s/%s" % kb]["snapped_mm"]}
            if ca != 0 and cb != 0:
                A = (lab == ca)
                B = (lab == cb)
                dB, iB = ndimage.distance_transform_edt(~B, sampling=cell, return_indices=True)
                dA = np.where(A, dB, np.inf)
                fl = int(np.argmin(dA))
                ai = np.unravel_index(fl, dA.shape)
                bi = (int(iB[0][ai]), int(iB[1][ai]), int(iB[2][ai]))
                pa = lo + (np.array(ai) + 0.5) * cell
                pb = lo + (np.array(bi) + 0.5) * cell
                thick = float(np.linalg.norm(pb - pa))
                t = np.linspace(0, 1, max(3, int(thick / (cell / 4)) + 2))
                mid = pa[None, :] + (pb - pa)[None, :] * t[:, None]
                mi = np.clip(np.floor((mid - lo) / cell).astype(int), 0, shape - 1)
                ow = own[mi[:, 0], mi[:, 1], mi[:, 2]]
                sol = grid[mi[:, 0], mi[:, 1], mi[:, 2]]
                cnt = Counter(row_part.get(int(w)) for w, s in zip(ow, sol) if s)
                mcnt = Counter(row_mesh.get(int(w)) for w, s in zip(ow, sol) if s)
                row.update(thinnest_wall_mm=round(thick, 4),
                           drill_from_mm=[round(float(x), 4) for x in pa],
                           drill_to_mm=[round(float(x), 4) for x in pb],
                           wall_parts=[k for k, _ in cnt.most_common()],
                           wall_meshes=[k for k, _ in mcnt.most_common()],
                           what_would_join_them=("a through-hole %.4f mm long from %s to %s, "
                                                 "through %s" % (thick,
                                                                 np.round(pa, 3).tolist(),
                                                                 np.round(pb, 3).tolist(),
                                                                 ", ".join(str(k) for k, _ in cnt.most_common()) or "nothing marked")))
            sev.append(row)
        out["severed_runs"] = sev
        out["severed_count"] = len(sev)
        return out

    free_point = ~grid
    need = OD / 2.0 + FLOOR
    free_cable = (~grid) & (edt >= need)
    res = [analyse(free_point, "point",
                   "every non-solid cell: the most generous free space there is, a cable of zero "
                   "thickness with zero clearance"),
           analyse(free_cable, "cable",
                   "cells at least %.4f mm from any surface (bundle radius %.4f + the lane's "
                   "1.0000 mm floor): the space a real bundle can occupy" % (need, OD / 2.0))]
    counts = {
        "cables": len(cab["cables"]),
        "point_space_components": res[0]["components"],
        "point_space_severed_runs": res[0]["severed_count"],
        "cable_space_components": res[1]["components"],
        "cable_space_severed_runs": res[1]["severed_count"],
        "grid_cell_mm": cell,
    }
    rec = {"$triad": 1, "kind": "wire-gap", "generated_by": "sim/wire_gap.py",
           "record": {"units": "mm", "method": __doc__.strip(), "counts": counts,
                      "spaces": res}}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(rec, open(OUT, "w"), indent=1)
    print(json.dumps(counts, indent=1))
    for r in res:
        print("\n== %s space: %d components, largest holds %.3f%% of %d free cells"
              % (r["tag"], r["components"], r["largest_share_pct"], r["free_cells"]))
        for s in r["severed_runs"]:
            print("  %-20s comps %s(%s cells)/%s(%s cells) snap %.2f/%.2f  wall=%-9s %s" % (
                s["id"], s["component_from"], s["component_from_cells"],
                s["component_to"], s["component_to_cells"],
                s["snapped_from_mm"], s["snapped_to_mm"],
                s.get("thinnest_wall_mm"), ",".join(str(x) for x in (s.get("wall_meshes") or []))[:60]))
    print("wrote", OUT)


main()
