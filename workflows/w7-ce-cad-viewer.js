export const meta = {
  name: 'microduck-ce-cad-viewer',
  description: 'Make microduck manipulable in the ce-cad dashboard: publish the assembly + every part into the catalog, export one GLB, bake the mechanism so the viewer PLAYS its hinges and the walk trajectory',
  whenToUse: 'When microduck (or any design-root design) must appear at http://localhost:8765/web/ so its parts, mechanics and software can be inspected in the browser',
  phases: [
    { title: 'Publish', detail: 'build assembly:microduck through bin/cad, publish it + every unique part into ce-cad/out/web/catalog.json with triad refs, export one GLB' },
    { title: 'Mechanics', detail: 'bake the 14 hinges from joints.json + the sim walk/sit trajectories so the viewer ticks the mechanism live' },
    { title: 'Verify', detail: 'curl /api/files?id=microduck must list entries; the mesh must load; screenshot the dashboard and confirm it DREW microduck' },
  ],
}
const REPO = '/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck'
const WS = '/Users/leifrydenfalk/dev/ce-workshop'
const CAD = `${WS}/ce-cad`
// The design lives in a DIFFERENT out/ tree than the dashboard serves. The
// dashboard (bin/dash, :8765, http://localhost:8765/web/) reads
// ce-cad/out/web/catalog.json and serves ce-cad/out/. A design-root's own
// out/ is invisible to it. The chosen bridge is NOT a symlink and NOT a
// bin/dash change: cecad.catalog.publish() writes into WEB_OUT (=ce-cad/out/web,
// from CAD_ROOT which defaults to the ce-cad repo) and TESSELLATES the meshes
// there itself, so a build run under bin/cad with CE_TRIAD_ROOT pointing at the
// design publishes straight into the dashboard's own tree with the triad ref
// stamped on the entry (publish(triad='assembly:microduck')). No copy, no
// second source of truth. This is backward compatible: every existing model is
// untouched; microduck is one more row.
const CTX = `Leif, 2026-09-02: "open microduck in ce-cad so i can manipulate its mechanics, simulate its software and mechanics and look at all of the parts." Repo ${REPO} (git; do NOT commit). The ce-cad dashboard is bin/dash on :8765 (http://localhost:8765/web/); it reads ${CAD}/out/web/catalog.json and serves ${CAD}/out/. Assets: assembly:microduck builds in the kernel (bin/cad assembly:microduck, ~7 min, 70 placements) and each part via cecad.triad.load; spec/mesh-placements.json = each mesh world pose + material_rgba; spec/mesh-to-part.json = mesh -> part ref; ce-assemblies/microduck/current/joints.json = 14 hinges (axes+ranges); sim/*_traj.npz = MuJoCo qpos trajectories (walk/sit/stand). Tools: cecad.catalog.publish(obj, triad='assembly:microduck', ...) writes the catalog + viewer mesh into ce-cad/out/web (NEVER set CAD_ROOT to the design root — that would write into the design's out/ and the dashboard would not see it); cecad.catalog.publish_components(asm) publishes every unique part; cecad.glb.glb_from_mesh_json(out/web/meshes/<id>.json, out/web/exports/<id>.glb) exports one GLB with per-part named nodes + colours; cecad.playback.bake / publish(motion=) bakes mechanism motion; cecad.vision.screenshot_url + page_ok proves a page DREW. export CE_TRIAD_ROOT="${REPO}:${WS}"; CAD_MAX_JOBS=2, one heavy build at a time, the Mac is shared. Do NOT commit ce-cad changes; keep them backward compatible and tested. House rules: MEASURE never assert; a page that answers 200 but draws nothing is broken; three verdicts (PASS / FAIL / CANNOT DETERMINE); break a check before trusting it.`
const OUT = { type: 'object', properties: { files: { type: 'array', items: { type: 'string' } }, urls: { type: 'array', items: { type: 'string' } }, verdicts: { type: 'array', items: { type: 'string' } }, cannot_determine: { type: 'array', items: { type: 'string' } }, changed_in_ce_cad: { type: 'array', items: { type: 'string' } }, notes: { type: 'string' } }, required: ['files', 'verdicts', 'notes'] }
const VERDICT = { type: 'object', properties: { ok: { type: 'boolean' }, measured: { type: 'array', items: { type: 'string' } }, problems: { type: 'array', items: { type: 'string' } } }, required: ['ok', 'problems'] }

phase('Publish')
const pub = await agent(`${CTX}

PUBLISH microduck INTO THE ce-cad DASHBOARD so all parts appear at http://localhost:8765/web/. Write a build+publish script (run it under bin/cad so the FreeCAD kernel is booted) that:
(1) triad.load(doc, 'assembly:microduck') — the 70-placement assembly;
(2) colours each placement from spec/mesh-placements.json material_rgba (map mesh->part via spec/mesh-to-part.json, match the part slug that appears in each assembly item label), so the cards and the GLB carry the real material colours, not just the default palette;
(3) cecad.catalog.publish(a, triad='assembly:microduck', description=..., tags=['microduck','robot','assembly']) — this stamps the triad ref and writes the viewer mesh into ce-cad/out/web/meshes/microduck.json and an auto-render;
(4) cecad.catalog.publish_components(a) — every unique part as its own card with a render (~38 parts);
(5) cecad.glb.glb_from_mesh_json('ce-cad/out/web/meshes/microduck.json', 'ce-cad/out/web/exports/microduck.glb') — one GLB, validated, per-part named nodes + colours.
MEASURE IT: curl 'http://localhost:8765/api/files?id=microduck' must return microduck entries incl. the GLB and the mesh; curl the mesh URL and confirm it has parts with positions+indices. If bin/dash cannot reach the model, decide and IMPLEMENT the fix backward-compatibly (publish writes into ce-cad/out/web already — prefer that over a bin/dash change; if you DO change bin/dash to teach it a design-root, keep every existing model working and say exactly what you changed). Return files written, the URLs, what (if anything) changed in ce-cad, verdicts, and the curl proof in notes.`, { label: 'publish', phase: 'Publish', schema: OUT })

phase('Mechanics')
const mech = await agent(`${CTX}

Publish phase result: ${JSON.stringify(pub).slice(0, 3000)}

MAKE THE MECHANISM MANIPULABLE. The published assembly places every part with joint='clamped' (a literal port of Pollen's MJCF), so the viewer shows a static pose. Give it motion so Leif can manipulate/simulate the mechanics:
(1) read ce-assemblies/microduck/current/joints.json (14 hinges: parent/child, axis, range) and cecad.playback / cecad.kinematics — bake a motion track the dashboard viewer can PLAY (publish(motion={...}) or playback.bake) that drives the hinges through their declared ranges; a bolted/clamped placement that cannot move is reported no-mobility, not a failure.
(2) the MuJoCo lane already produced qpos trajectories (out/sim/*_traj.npz, 50 Hz walk/sit/stand from run_policy.py). Convert at least the walk trajectory into a viewer motion track keyed to the hinge names (there is a per-hinge qpos index in the MJCF reference/pollen-microduck-rl/robot_walk.xml) so the dashboard can play the ACTUAL learned gait. If the placement-based assembly cannot accept per-joint qpos without the kinematic tree, say so precisely and state what the next iteration needs (the joint walk that replaces the literal placements). 
MEASURE: curl the motion track URL and confirm frame count + joint count; if you PLAY it, screenshot two distinct frames and confirm the pose changed. Return files, URLs, verdicts, and CANNOT DETERMINE for anything the placement port cannot yet express.`, { label: 'mechanics', phase: 'Mechanics', schema: OUT })

phase('Verify')
const ver = await agent(`${CTX}

Publish: ${JSON.stringify(pub).slice(0, 2000)}
Mechanics: ${JSON.stringify(mech).slice(0, 2000)}

INDEPENDENTLY VERIFY the whole thing, measuring everything yourself:
(1) curl 'http://localhost:8765/api/files?id=microduck' — the assembly entry exists, carries triad='assembly:microduck', and lists a GLB + a mesh; count the part cards for microduck in the catalog (grep the catalog.json or /api/files) and confirm ~38 unique parts are published;
(2) fetch the viewer mesh JSON and the GLB; parse the GLB header (magic 'glTF', version 2, chunk lengths against file size) and count its named nodes — confirm one node per part with a colour;
(3) load http://localhost:8765/web/ (and the model's viewer URL) with cecad.vision.screenshot_url + page_ok under bin/cad and CONFIRM IT DREW microduck (not a blank canvas answering 200) — save the screenshot path;
(4) confirm NOTHING in ce-cad was committed and any tool change is backward compatible (existing models still list). Return ok + problems (file:line / URL), the screenshot path in measured, and a one-line final verdict.`, { label: 'verify', phase: 'Verify', schema: VERDICT, effort: 'high' })

return { publish: pub, mechanics: mech, verify: ver }
