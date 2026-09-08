export const meta = {
  name: 'microduck-elec-verify',
  description: 'Verify every Microduck electronic component: exact part, package, physical dimensions (mm), pinout, voltage, and real sourcing (vendor, unit price, MOQ, lead time) — each with citations',
  phases: [
    { title: 'Components', detail: 'one agent per component: datasheet spec + physical dimensions + sourcing' },
    { title: 'Custom', detail: 'the three unpublished custom PCBs — what must be designed & fabbed' },
    { title: 'Synthesize', detail: 'compile a single verified electronics + sourcing table' },
  ],
}
const REPO = '/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck'
const WS = '/Users/leifrydenfalk/dev/ce-workshop'
const CTX = `You are verifying the electronics of the Pollen Robotics Microduck for a manufacturing release. Repo ${REPO} (read docs/ELECTRONICS-AND-SOFTWARE.md, docs/ELECTRONICS-DATASHEET.html, electronics/netlist.json, electronics/elec-spec.json). Global shelf ${WS}/ce-parts/<name>/electrical.chip.json may carry a cited pinout for some ICs (check, do not assume the name matches). HOUSE RULES: measure/cite, never assert. Every physical dimension and price MUST carry a source (datasheet page, distributor URL, vendor page) — a value you cannot source is reported as CANNOT DETERMINE with null, never guessed. Use WebSearch/WebFetch (load them via ToolSearch: "select:WebSearch,WebFetch"). Units mm, grams, volts. Real distributors only (Robotis, DigiKey, Mouser, LCSC, Arrow, the vendor's own store).`
const SCHEMA = { type:'object', properties:{
  component:{type:'string'}, exact_part:{type:'string'}, function:{type:'string'},
  package:{type:'string'},
  dims_mm:{type:'object', properties:{l:{type:['number','null']},w:{type:['number','null']},h:{type:['number','null']}}, required:['l','w','h']},
  mass_g:{type:['number','null']}, pins:{type:['integer','null']}, interface:{type:'string'}, voltage:{type:'string'},
  qty_per_robot:{type:['integer','null']},
  sourcing:{type:'array', items:{type:'object', properties:{vendor:{type:'string'}, url:{type:'string'}, unit_price_usd:{type:['number','null']}, moq:{type:['integer','null']}, lead_time:{type:'string'}}, required:['vendor']}},
  citations:{type:'array', items:{type:'string'}},
  verdict:{type:'string', enum:['VERIFIED','PARTIAL','CANNOT DETERMINE']}, notes:{type:'string'}
}, required:['component','exact_part','dims_mm','sourcing','verdict','citations'] }
const COMPONENTS = [
  ['Radxa Zero 3W','RK3566 SBC compute module, host','1x'],
  ['Dynamixel XL330-M288-T','TTL smart servo, the 14 joint actuators + 1 IMU-bus node','15x — biggest cost line, get Robotis pricing + qty breaks'],
  ['LSM6DSV16X','6-axis IMU, Dynamixel Protocol-2 slave on imu_to_dxl','1x'],
  ['TLV320AIC3104','stereo audio codec on the Robot HAT','1x'],
  ['VL53L8CX','8x8 multizone ToF (confirm L8 vs L5CX)','1x'],
  ['IMX219','8MP camera image sensor + M12 lens','1x'],
  ['BMI088','6-axis IMU (secondary/dormant on the HAT)','1x'],
  ['FUSB302','USB-C PD controller','1x'],
  ['PN7150','NFC controller (confirm vs ST25R3916)','1x'],
  ['NP-F550 battery','2S Li-ion camcorder cell ~7.4V (NOTE: sim mesh is np_f970 — flag the drift, verify the shipping cell)','1x'],
  ['MEMS microphone + speaker','the audio in/out transducers wired to the codec','confirm parts'],
]
phase('Components')
const comps = await parallel(COMPONENTS.map(([name,fn,qty]) => () =>
  agent(`${CTX}\n\nCOMPONENT: ${name}\nRole: ${fn}\nQuantity note: ${qty}\n\nReturn its exact manufacturer part number, package, PHYSICAL DIMENSIONS in mm (l×w×h of the actual part/module as sold), mass if available, pin count, primary interface, operating voltage, quantity per robot, and REAL sourcing (>=2 distributors with unit price at qty 1 and at 100/1000 if shown, MOQ, lead time). Cite every number. If Microduck uses a module/board carrying this IC (not the bare IC), give the MODULE's dimensions and note that. Verdict VERIFIED only if dims AND at least one live price are sourced.`,
    { label:`elec:${name.slice(0,18)}`, phase:'Components', schema:SCHEMA, effort:'high' })))
phase('Custom')
const CUSTOM = [
  ['microduck-robot-hat-pcb','Pollen Robot HAT: TLV320AIC3104 + BMI088 + Stemma J5 ToF + half-duplex Dynamixel transceiver + 2S->5V, Pi-Zero footprint. UNPUBLISHED.'],
  ['microduck-imu-to-dxl','imu_to_dxl v2: LSM6DSV16X as a Dynamixel Protocol-2 slave (ID 200) + its MCU. UNPUBLISHED schematic+firmware.'],
  ['microduck-banana-contact-pcb','battery banana-plug contact board in the trunk. UNPUBLISHED.'],
]
const custom = await parallel(CUSTOM.map(([name,desc]) => () =>
  agent(`${CTX}\n\nCUSTOM BOARD: ${name}\n${desc}\n\nThis board has NO published design files. Report: board outline size (mm, from the mesh at ${REPO}/reference/pollen-microduck-rl/assets/ or spec), the known ICs it must carry, connector list, and EXACTLY what must be done to make it fabricable (schematic capture, layout, Gerber, fab house options with quick-turn price/lead e.g. JLCPCB/PCBWay/OSHPark, assembly). Be concrete about the work and cost. Verdict is CANNOT DETERMINE for the design (unpublished) but VERIFIED for the action plan if you give real fab options with prices.`,
    { label:`custom:${name.slice(10,26)}`, phase:'Custom', schema:{type:'object', properties:{ board:{type:'string'}, outline_mm:{type:'string'}, ics:{type:'array',items:{type:'string'}}, connectors:{type:'array',items:{type:'string'}}, work_to_fab:{type:'array',items:{type:'string'}}, fab_options:{type:'array',items:{type:'object',properties:{house:{type:'string'},price:{type:'string'},lead:{type:'string'}}}}, citations:{type:'array',items:{type:'string'}}, verdict:{type:'string'} }, required:['board','work_to_fab','verdict'] }, effort:'high' })))
phase('Synthesize')
const synth = await agent(`${CTX}\n\nHere are the verified components:\n${JSON.stringify(comps.filter(Boolean)).slice(0,9000)}\n\nAnd the custom boards:\n${JSON.stringify(custom.filter(Boolean)).slice(0,4000)}\n\nProduce a clean consolidated summary object: total component count, how many VERIFIED vs PARTIAL vs CANNOT DETERMINE, the estimated per-robot electronics BOM cost at qty 1 and qty 100 (sum the sourced unit prices; state what is missing), the biggest cost lines, and the top manufacturing blockers with the concrete next action for each. This becomes the electronics section of the release + the RFQ input.`,
  { label:'synth', phase:'Synthesize', schema:{type:'object', properties:{ n_components:{type:'integer'}, verified:{type:'integer'}, partial:{type:'integer'}, cannot_determine:{type:'integer'}, bom_cost_qty1_usd:{type:['number','null']}, bom_cost_qty100_usd:{type:['number','null']}, biggest_cost_lines:{type:'array',items:{type:'string'}}, blockers:{type:'array',items:{type:'object',properties:{what:{type:'string'},action:{type:'string'}}}}, summary:{type:'string'} }, required:['n_components','summary','blockers'] }, effort:'high' })
return { components: comps.filter(Boolean), custom: custom.filter(Boolean), synth }
