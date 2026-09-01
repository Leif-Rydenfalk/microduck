export const meta = {
  name: 'microduck-wiring',
  description: 'Wiring lane: the servo daisy chain, IMU board, ToF, codec, camera and power as a ce-wire design with cable lengths measured off the placements',
  phases: [
    { title: 'Wire', detail: 'ce-wire design + cecad.harness lengths' },
    { title: 'Verify', detail: 'independent re-measure' },
  ],
}
const REPO = '/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck'
const WS = '/Users/leifrydenfalk/dev/ce-workshop'
const CTX = `Repo ${REPO} (git; do NOT commit). GOAL.md rung 5. Facts: docs/ELECTRONICS-AND-SOFTWARE.md (bus topology, IDs, pins), electronics/netlist.py if it exists, ce-assemblies/microduck/current/placements.json (every part's world pose in mm, zero pose) and joints.json (14 hinges, ranges). Tools: ${WS}/ce-wire (bin/wire, README — what is connected to what as a folder of files), cecad.harness (wire(asm, a, b) measures route length off the solids; check_drop voltage drop needs stated bases), cecad.unify (bind netlist labels to assembly nodes). export CE_TRIAD_ROOT="${REPO}:${WS}"; CAD_MAX_JOBS=2, one build at a time. Measure, never assert; a cable length is a route floor (straight line through the joints' clearance) and says so.`
const OUT = { type: 'object', properties: { files: { type: 'array', items: { type: 'string' } }, cables: { type: 'integer' }, total_length_m: { type: 'number' }, verdicts: { type: 'array', items: { type: 'string' } }, cannot_determine: { type: 'array', items: { type: 'string' } }, notes: { type: 'string' } }, required: ['files', 'verdicts', 'notes'] }
const VERDICT = { type: 'object', properties: { ok: { type: 'boolean' }, measured: { type: 'array', items: { type: 'string' } }, problems: { type: 'array', items: { type: 'string' } } }, required: ['ok', 'measured', 'problems'] }
phase('Wire')
const w = await agent(`${CTX}\n\nWRITE THE WIRING as ${REPO}/wiring/ (a ce-wire design) + wiring/README.md: (1) the Dynamixel daisy chain — order the 15 servos + imu_to_dxl along the physical chain (trunk hip-yaw pair -> each leg down to the ankle; trunk -> neck -> head), each hop's cable length = straight-line distance between the two servo connector positions from placements.json plus a stated slack for the joint's range (say the rule), JST 3-pin X3P both ends; (2) the HAT harness: I2C3 to ToF (JST-SH 4), codec to mic + speaker, CSI ribbon length to the camera in the head (through the ±170 deg head yaw — name the routing problem), battery contacts -> HAT, HAT -> bus power; (3) a table of every cable: from, to, pins, length mm (floor), connector, qty, and the voltage-drop check for the servo bus at 8.2 V and 6.6 V with 1 A per moving servo (cecad.harness.check_drop with bases stated; CANNOT DETERMINE if the transceiver/wire gauge is unpublished — use 22 AWG as ROBOTIS' cable and say so); (4) bin/wire check output recorded. Return files, cable count, total length, verdicts, CANNOT DETERMINE list.`, { label: 'wire', phase: 'Wire', schema: OUT })
phase('Verify')
const v = await agent(`${CTX}\n\nINDEPENDENTLY VERIFY the wiring lane: ${JSON.stringify(w).slice(0, 4000)}. Recompute three cable lengths yourself from placements.json; check the chain order against the MJCF tree (docs/PARTS.md body column); re-run bin/wire check; look for any length typed rather than derived. Return ok + problems file:line.`, { label: 'verify', phase: 'Verify', schema: VERDICT, effort: 'medium' })
return { wiring: w, verify: v }
