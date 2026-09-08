export const meta = {
  name: 'microduck-rung6-deliver',
  description: 'Close rung 6: package the manufacturing deliverable and verify it is complete enough for a factory',
  phases: [{ title: 'Assess' }, { title: 'Verify' }],
}
const REPO = '~/dev/ce-workshop/ce-designs/microduck'
const CTX = `REPO: ${REPO}. STATUS.md rung 6 (manufacturing) is PARTIAL: "10/10 drawings verified,
all 30 printed parts sliced with REAL slicer numbers, 2 plate 3MFs, 7-step manual, bom.csv;
bin/deliver package + verify still queued."

Since that was written: plates were re-cut for the two machines that actually exist on the LAN
(out/print/plates/HEAD-X1C for a Bambu X1 Carbon 0.4, HEAD-BIG for an H2D 0.6), every one verified
INSIDE the 3mf (non-empty tray_info_idx and used_g > 0), and out/print/PRINT-X1C.md records why the
original H2S plates do not fit. tools/plate_for_printer.py is the tool that cuts them.

RULES: MEASURE never assert. PASS / FAIL / CANNOT DETERMINE. Every number carries its file. A tool
reporting success is not evidence — VERIFY BY COUNTING. Report what you discarded.`
const S = { type:'object', properties:{
  task:{type:'string'}, verdict:{type:'string',enum:['PASS','FAIL','CANNOT_DETERMINE']},
  findings:{type:'array',items:{type:'object',properties:{
    what:{type:'string'}, value:{type:'string'}, evidence:{type:'string'},
    status:{type:'string',enum:['MEASURED','CANNOT_DETERMINE']}},required:['what','value','evidence','status']}},
  missing:{type:'array',items:{type:'string'}}, discarded:{type:'array',items:{type:'string'}}},
  required:['task','verdict','findings','missing','discarded'] }
const TASKS = [
  { k:'inventory', t:'What does a factory need, and what is actually on disk?',
    a:'Build the list a real shop needs to make this robot: printed-part files + settings, drawings, BOM with sources, assembly manual, wiring, fasteners. Then COUNT what exists: STLs, 3MFs, drawing sheets (out/drawings), the manual, bom.csv. Name every gap. docs/PRODUCTION.md and docs/MANUFACTURING-REQUIREMENTS.md exist — read them for what this project already decided a pack must contain.' },
  { k:'licence', t:'The licence gate, and it blocks selling not printing',
    a:'out/print/PRINT.md records that of 30 printed parts, 8 are OUR parametric rebuilds and 22 are Pollen vendor meshes as shelved, CC BY-SA-NC — fine to print, NOT licensed for sale. Establish exactly WHICH 22, and which of the 8 rebuilds already PASS refcheck (STATUS.md rung 1 claims 20 parametric rebuilds PASS, which conflicts with 8 in the manifest — resolve that conflict by counting, do not repeat either number). The deliverable is the list of parts that must be rebuilt before anything can be sold.' },
  { k:'deliver', t:'What is bin/deliver and what would package+verify actually do?',
    a:'Find the deliver tooling (ce-workshop/bin, ce-cad/bin, or this repo). Read what package and verify are supposed to produce for an assembly. Determine whether it can run for microduck today and what it would refuse on. If the tool does not exist here, say so plainly — that is then the rung-6 gap, and specify what the pack should contain instead.' },
  { k:'gap', t:'State the one number that closes rung 6, or the one that blocks it',
    a:'Rung 6 says PARTIAL. Decide what single measurable condition would move it to PASS, in this project\'s own terms (a count, a verified pack, a refcheck result) — and whether that condition is met today. If it is not met, give the shortest path to it. Do not declare PASS on a rung whose own STATUS line lists queued work.' },
]
const out = await pipeline(TASKS,
  t => agent(`${CTX}\n\nTASK: ${t.t}\n${t.a}`, {label:`a:${t.k}`, phase:'Assess', schema:S}),
  (r,t) => agent(`ADVERSARIAL CHECK. Open every cited file. Counts must be RE-COUNTED, not repeated —
this project has had three numbers amplified upward and all three flattered. Demote any claim whose
citation does not support it. Do not mark a rung PASS to be helpful.\n\n${JSON.stringify(r,null,2)}`,
    {label:`v:${t.k}`, phase:'Verify', schema:S, effort:'high'}))
return { tasks: out.filter(Boolean) }
