# Integrate into the next review

Copy this whole directory into the next review's electronics folder; link `START HERE.html` from the first document and embed its five PNGs there if desired. All guide images are embedded; rotating views and PCB source downloads use relative files. `Cables and connections.pdf` is the PDF alternative. No native Windows execution was measured; Chrome on macOS was tested with networking disabled.

`Cable overlay.json` holds sixteen cable parts in the same world-mm zero-pose frame as `ce-cad/out/web/meshes/microduck.json`. These exact saved cable STLs may be added as a visibly labeled routing-review overlay. Do not animate them as flexible cable mechanics or count their saved route verdicts as current clearance proof. Their bodies can intersect revised geometry and their endpoints are unresolved.

## Regenerate after the robot geometry changes

From the Microduck project root (use a NEW directory for an issued review):

```sh
python3 tools/build_pcb_review_map.py --out research/cable-review-2026-09-09
python3 tools/build_cable_review.py --cad-root ../../ce-cad --out research/cable-review-2026-09-09
node tools/render_cable_review.mjs research/cable-review-2026-09-09 ../../ce-cad
python3 tools/build_cable_review.py --cad-root ../../ce-cad --out research/cable-review-2026-09-09 --document
node tools/render_cable_review.mjs research/cable-review-2026-09-09 ../../ce-cad --document
```

Browser port is 9494. Render source hashes appear in PROVENANCE.json and the browser evidence. Re-run exact cable and image/link verification if the underlying STLs or package layout changes. Renderer works directly from actual published triangles, avoiding the old slow FreeCAD mesh-to-planar-face conversion and box substitutes.

Owned reusable source: tools/build_cable_review.py, tools/render_cable_review.mjs, tools/build_pcb_review_map.py. Root should stage these explicit paths plus this review directory, after reviewing tracked/binary size rules. The fetched replica clone stays private workspace cache; only its seven explicit public IMU source files were copied, with hashes and its clean commit a1f4979c425bd9228622be89f2bfa4d1de7fbde3. Older mechanical source 2549257 and public HAT 23eab119 are separate pins.
