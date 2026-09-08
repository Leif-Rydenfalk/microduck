export const meta = {
  name: 'microduck-rung4-electronics',
  description: 'Close rung 4: the Robot HAT design files DO exist — verify them and correct the docs that deny it',
  phases: [{ title: 'Verify' }, { title: 'Correct' }],
}
const REPO = '~/dev/ce-workshop/ce-designs/microduck'
const CTX = `REPO: ${REPO}. STATUS.md rung 4 (electronics) is PARTIAL, blocked on "Robot HAT PCB +
electronics verify still queued". docs/BOM.md states, for P1/P2/P3, "no design files exist - must be
designed, not bought".

THAT CLAIM IS FALSE and a prior workflow established it: electronics/robot-hat/out/fab/ holds a
complete fabrication set — microduck_robot_hat.kicad_pcb, Gerbers (F.Cu/B.Cu/F.Silk/F.Paste/
B.Mask/Edge.Cuts), PTH.drl, and a positions CSV. reference/pollen-elec-rpi-robot-hat/ holds
Pollen's own schematic and part datasheets.

RULES: MEASURE never assert. PASS / FAIL / CANNOT DETERMINE; a missing value stays missing. Every
number carries the file it came from. Do NOT invent pin numbers, net names or part numbers — a
fabricated pinout becomes copper. Report what you discarded.`
const S = { type:'object', properties:{
  task:{type:'string'}, verdict:{type:'string',enum:['PASS','FAIL','CANNOT_DETERMINE']},
  findings:{type:'array',items:{type:'object',properties:{
    what:{type:'string'}, value:{type:'string'}, evidence:{type:'string'},
    status:{type:'string',enum:['MEASURED','CANNOT_DETERMINE']}},required:['what','value','evidence','status']}},
  doc_corrections:{type:'array',items:{type:'string'}},
  discarded:{type:'array',items:{type:'string'}}},
  required:['task','verdict','findings','doc_corrections','discarded'] }
const TASKS = [
  { k:'fabset', t:'Is the fabrication set COMPLETE and self-consistent?',
    a:'Inventory electronics/robot-hat/out/fab/. Does it have every layer a fab needs, a drill file, and a positions file? Do the Gerber layer count and the kicad_pcb stackup agree? Does the board outline match the 65 x 30 mm the BOM states and the ce-parts/microduck-robot-hat-pcb shelved part? Count components in the PCB and in the positions CSV and say whether they agree — a prior audit found 127 components, 95 nets (not 96), and 117 placements, so check those numbers rather than repeat them.' },
  { k:'bom', t:'Extract a real, orderable BOM from the PCB',
    a:'From microduck_robot_hat.kicad_pcb and any BOM/positions file, produce the actual component list with reference designators, values, footprints and quantities. Flag every part with no MPN. This is what JLCPCB assembly would need. Do not invent LCSC codes — the only verified one in this project is C181753 for TLV320AIC3104IRHBR.' },
  { k:'p2p3', t:'What about P2 (imu_to_dxl) and P3 (banana battery PCB)?',
    a:'The HAT is P1. docs/BOM.md also lists P2 imu_to_dxl v2 (LSM6DSV16X + MCU as a Dynamixel protocol-2 slave, ID 200, 12-byte block at register 124) and P3 the banana battery-contact PCB. Do design files exist for these two as well? Search the repo the same way the HAT was found. If they genuinely do not exist, say so with what you searched, because that is then the REAL remaining rung-4 gap.' },
  { k:'docs', t:'Which documents state the false claim, and exactly what should they say?',
    a:'Find every place in the repo that says the HAT design files do not exist or that rung 4 is blocked on designing them — docs/BOM.md, STATUS.md, GOAL.md, any HTML. Quote each verbatim with file and line, and write the exact replacement sentence, grounded in what the fab set actually contains. Do NOT edit the files; produce the corrections for review.' },
]
const out = await pipeline(TASKS,
  t => agent(`${CTX}\n\nTASK: ${t.t}\n${t.a}`, {label:`v:${t.k}`, phase:'Verify', schema:S}),
  (r,t) => agent(`ADVERSARIAL CHECK of this rung-4 finding. Open every cited file; if a citation does
not exist or does not say what is claimed, demote it. Any part number, pin or net not traceable to a
real file is FABRICATION — list it. A block that is mostly CANNOT_DETERMINE gets that verdict; do not
mark PASS because it looks complete.\n\n${JSON.stringify(r,null,2)}`,
    {label:`c:${t.k}`, phase:'Correct', schema:S, effort:'high'}))
return { tasks: out.filter(Boolean) }
