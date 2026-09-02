"""publish_to_dashboard — put assembly:microduck AND every one of its parts on
the ce-cad dashboard (http://localhost:8765/web/).

Run through ce-cad's bin/cad so CAD_ROOT points at the ce-cad checkout: that is
the tree the dashboard serves (out/web/catalog.json + out/web/meshes +
out/web/exports). CE_TRIAD_ROOT must name the microduck design root first so
`triad.load` resolves the microduck refs.

    export CE_TRIAD_ROOT="<microduck-root>:<ce-workshop>"
    /Users/leifrydenfalk/dev/ce-workshop/ce-cad/bin/cad \
        <microduck-root>/tools/publish_to_dashboard.py

This is Option 1 from the task: PUBLISH INTO ce-cad/out/web with a triad ref.
No change to bin/dash is needed — publish() already writes the viewer mesh, the
renders, and the STEP/STL/GLB exports into the tree the dashboard serves, and
stamps the triad ref onto the entry for a ref-built object. publish() with
components=True (the default) then publishes every unique part as its own card.
"""
import os
import FreeCAD as App
import cecad.triad as triad
from cecad import publish

REF = "assembly:microduck"

def main():
    print("CAD_ROOT      =", os.environ.get("CAD_ROOT"))
    print("CE_TRIAD_ROOT =", os.environ.get("CE_TRIAD_ROOT"))
    print("triad roots   =", triad.roots())

    doc = App.newDocument("microduck")
    print("loading", REF, "…")
    a = triad.load(doc, REF)
    print("built assembly:", a.name, "with", len(a.items), "placements")
    for n in getattr(a, "notes", []) or []:
        print("  note:", n)

    entry = publish(
        a,
        id="microduck",
        title="Microduck — whole robot",
        triad=REF,
        kind="assembly",
        description=("Pollen Robotics Microduck, ported part-by-part into "
                     "cecad: trunk, two 5-DoF legs, 4-DoF neck/head, 1-DoF "
                     "beak. 15x XL330 servos, ~38 distinct parts, 70 "
                     "placements. Placed from the MJCF zero-pose transforms."),
        tags=["assembly", "microduck", "robot", "pollen"],
        components=True,        # publish every unique part as its own card too
    )
    print("PUBLISHED assembly id:", entry.get("id"))
    print("  triad     :", entry.get("triad"))
    print("  builder   :", (entry.get("builder") or {}).get("ref"))
    print("  components:", len(entry.get("components") or []))
    print("  mesh      :", entry.get("mesh"))
    ex = entry.get("exports") or {}
    for k in ("step", "stl", "glb"):
        r = ex.get(k) or {}
        print(f"  export {k:4s}: {r.get('state')} {r.get('path')} "
              f"({r.get('bytes', 0)} bytes)"
              + (f" parts={r.get('parts')} tris={r.get('tris')}"
                 if k == "glb" and r.get("parts") else ""))
    print("  motion    :", entry.get("motion_state"), "-", entry.get("motion_reason"))

if __name__ == "__main__":
    main()
