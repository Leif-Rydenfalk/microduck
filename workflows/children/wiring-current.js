export const meta = {
  name: 'microduck-wiring-current',
  description: 'A 3 A connector is carrying a 15 A assumption and the check prints PASS — re-grade the wiring on current, not just voltage drop',
  phases: [{ title: 'Measure' }, { title: 'Verify' }],
}
const REPO = '~/dev/ce-workshop/ce-designs/microduck'
const CTX = `REPO: ${REPO}. A prior audit found a real defect and it is the reason this workflow exists:

  ce-parts/jst-b3b-eh-a/component.json:33 records current_rating_A = 3.0, cited
  "eEH.pdf p.1 'Current rating: 3 A AC/DC (AWG #22)'".
  wiring/CABLES.md:35 states the basis "1 A per moving servo" and applies it to ALL 15 moving
  servos downstream of a hop. The first hop therefore carries 15 A across that 3 A contact —
  and check_drop prints PASS, because it grades VOLTAGE DROP and never looks at current rating.
  ROBOTIS' own e-Manual names the identical connector (JST B3B-EH-A) with 21 AWG wire, one gauge
  FATTER than the AWG #22 the 3 A rating is conditioned on.

RULES: MEASURE never assert. PASS / FAIL / CANNOT DETERMINE. Every number carries its source.
The XL330's published figures are standby 17 mA and stall 1.47 A at 5 V; the vendor publishes NO
running current, so "1 A per servo" is an ASSUMPTION between them — treat it as such, and say what
would settle it. Report what you discarded.`
const S = { type:'object', properties:{
  task:{type:'string'}, verdict:{type:'string',enum:['PASS','FAIL','CANNOT_DETERMINE']},
  findings:{type:'array',items:{type:'object',properties:{
    what:{type:'string'}, value:{type:'string'}, evidence:{type:'string'},
    status:{type:'string',enum:['MEASURED','CANNOT_DETERMINE']}},required:['what','value','evidence','status']}},
  fix:{type:'string'}, discarded:{type:'array',items:{type:'string'}}},
  required:['task','verdict','findings','fix','discarded'] }
const TASKS = [
  { k:'worst', t:'What current does each hop actually carry, and which hops exceed 3 A?',
    a:'Read wiring/CABLES.md, wiring/drop.json and the chain order from the MJCF tree. For every hop compute the current under the stated 1 A/servo basis AND under the vendor stall figure 1.47 A, and list every hop above the 3 A connector rating. Give the worst hop by name.' },
  { k:'basis', t:'Is 1 A per servo defensible, and what is the real number?',
    a:'The XL330-M288-T publishes standby 17 mA and stall 1.47 A at 5 V and no running current. Find any better basis in the repo, in ROBOTIS documentation already shelved, or in the sim (a walk policy exists and out/sim has real trajectories — torque over time could bound it). If nothing settles it, say CANNOT_DETERMINE and name the measurement that would: a clamp meter on one servo during the walk is cheap and Leif is in a hardware lab.' },
  { k:'topology', t:'Does the topology have to put 15 servos on one contact at all?',
    a:'The Dynamixel bus is a daisy chain, but POWER does not have to follow the data chain. Look at the HAT (electronics/robot-hat/out/fab/microduck_robot_hat.kicad_pcb) — how many servo connectors does it have, and are they parallel? A prior audit found J13/J14 fully parallel including the data net, and four motor connectors on a 1.000 mm +BATT bus. Work out how the 15 servos SHOULD be split across the available connectors so no contact exceeds its rating, and whether the current harness already does that or not.' },
  { k:'check', t:'Fix the check that cannot fail',
    a:'check_drop grades voltage drop and prints PASS on a hop carrying 5x its connector rating. That is a check that cannot fail in the dimension that matters. Specify exactly what a current-rating gate should test, where it belongs in the wiring tooling, and what it must refuse. Name the file and function. Do not write the code — specify the check, its inputs, and the case that must make it go red.' },
]
const out = await pipeline(TASKS,
  t => agent(`${CTX}\n\nTASK: ${t.t}\n${t.a}`, {label:`m:${t.k}`, phase:'Measure', schema:S}),
  (r,t) => agent(`ADVERSARIAL CHECK. Open every cited file and line. Demote anything whose citation
does not say what is claimed. A current figure without a source is not a measurement. Watch for a
proposed fix that would merely LOOSEN the check to pass — this project's standing rule is never
loosen a check to pass it.\n\n${JSON.stringify(r,null,2)}`,
    {label:`v:${t.k}`, phase:'Verify', schema:S, effort:'high'}))
return { tasks: out.filter(Boolean) }
