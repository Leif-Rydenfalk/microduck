export const meta = {
  name: 'microduck-manufacturing',
  description: 'The documents the team executes: DFM review of every part, process selection with break-even, assembly line with jigs and torque, QA/test plan, supplier shortlist and a ready-to-send RFQ',
  phases: [
    { title: 'DFM', detail: 'manufacturability review of every mechanical part', model: 'opus' },
    { title: 'Process', detail: 'print vs mould, break-even quantities, print profiles', model: 'opus' },
    { title: 'Assembly', detail: 'line steps, jigs, fixtures, torque specs', model: 'opus' },
    { title: 'QA', detail: 'incoming inspection + functional acceptance test plan', model: 'opus' },
    { title: 'Sourcing', detail: 'supplier shortlist, pricing, MOQ, lead time, RFQ package', model: 'opus' },
    { title: 'Synthesize', detail: 'consolidate into one execution plan', model: 'opus' },
  ],
}
const REPO = '/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck'
const WS = '/Users/leifrydenfalk/dev/ce-workshop'
const CTX = `You are preparing the Pollen Robotics Microduck (a 737 g bipedal desktop robot, ~230 mm tall, 14 actuated joints driven by Dynamixel XL330-M288-T servos) for real manufacture. The team will EXECUTE what you write, so be concrete and numerical.

REPO ${REPO}. Key data you MUST read before writing anything:
- out/verify/mech_dims.json — measured bounding box of all 47 meshes in mm to 4 dp, plus the 9 parametric rebuilds and their deviation. THIS IS THE DIMENSIONAL TRUTH.
- out/stress/report.json — FEA: shin SF 7.51, ankle SF 2.02, hip-bracket SF 6.42 PASS at 20 N; upper-leg CANNOT DETERMINE.
- SPEC.md, docs/PARTS.md, docs/BOM.md, docs/PRODUCTION.md, docs/MANUFACTURING-REQUIREMENTS.md, RELEASE.html, COMPARISON.html.
- Printed parts today: 218 g PLA / 9.9 h plus 26 g TPU / 2.4 h across 30 printed parts (out/print/).

HOUSE RULES, non-negotiable:
- MEASURE/CITE, never assert. Every dimension, price, cycle time, lead time carries a source (file path, datasheet page, distributor URL). A number you cannot source is reported as CANNOT DETERMINE with null — NEVER invent a plausible value.
- Three verdicts: PASS / FAIL / CANNOT DETERMINE.
- Full engineering precision: mm to 3-4 dp, and state the tolerance basis. Units mm, g, deg, V, USD.
- You may use WebSearch/WebFetch (load via ToolSearch: "select:WebSearch,WebFetch") and Bash/Read/Grep for repo files.
- DO NOT contact any supplier, factory or person. You produce documents only.

KNOWN CRITICAL FINDINGS you must respect and not paper over:
1. The simulation head mesh (top_head_shell 91.751 x 122.688 x 46.339 mm) does NOT match the product's compact domed head in the photographs. Head tooling from this mesh would be wrong.
2. Battery mesh is np_f970 (38.600 x 20.600 x 70.800 mm) while docs say NP-F550 class.
3. Compute mesh is a Pi Zero 2 W placeholder; documented host is Radxa Zero 3W (both 65 x 30 mm).
4. Two ankle revisions exist (ankle_left Y=36.500 vs ankle_l_v1 Y=46.500 mm).
5. Three custom PCBs (Robot HAT, imu_to_dxl, banana contact) have NO published design files.`

const DFM = { type:'object', properties:{
  group:{type:'string'},
  parts:{type:'array', items:{type:'object', properties:{
    part:{type:'string'}, dims_mm:{type:'string'}, function:{type:'string'},
    material:{type:'string'}, process:{type:'string'},
    dfm_issues:{type:'array', items:{type:'string'}},
    wall_thickness_mm:{type:['number','null']}, draft_needed:{type:'boolean'},
    tolerance_class:{type:'string'}, critical_features:{type:'array', items:{type:'string'}},
    verdict:{type:'string', enum:['PASS','FAIL','CANNOT DETERMINE']} }, required:['part','process','verdict'] }},
  notes:{type:'string'} }, required:['group','parts'] }

phase('DFM')
const GROUPS = [
  ['Trunk & structure','trunk_base, power_support, banana_pcb_locker, trunk_shell_left, trunk_shell_right, left_shell, right_shell, motor_support'],
  ['Hip & upper leg','yaw2roll, bearing_roll, hip_l, upper_leg_left, upper_leg_right, upper_leg_rigidity_plate, left_upper_leg, right_upper_leg'],
  ['Lower leg & foot','leg, ankle_left, ankle_right, ankle_l_v1, ankle_r_v1, foot_left, foot_right, sole_left, sole_right'],
  ['Head & face','top_head_shell, bottom_head_shell, face_part, jaw, jaw_soft, soft_mouth_top, noenoeil, m12_lens_holder, lens'],
  ['Neck & misc','neck, neck_pitch, yaw_roll_motion, rim, tire, roller_blade, speaker'],
]
const dfm = await parallel(GROUPS.map(([g, parts]) => () =>
  agent(`${CTX}\n\nDFM REVIEW — group "${g}": ${parts}\n\nRead out/verify/mech_dims.json for the real dimensions of each part in this group. For EVERY part: state its measured bbox, what it does structurally, the material you recommend and why, the process (FDM print / SLA / injection mould / CNC / bought), the DFM issues (thin walls, unsupported overhangs, trapped volumes, undercuts preventing tool release, press-fit tolerance risk, anisotropy vs the load direction), the minimum wall thickness if you can determine it, whether draft is needed for moulding, a tolerance class, and the critical features that must be controlled. Flag any part whose sim mesh you do NOT trust (see critical findings). Verdict per part.`,
    { label:`dfm:${g.slice(0,16)}`, phase:'DFM', schema:DFM, model:'opus', effort:'high' })))

phase('Process')
const proc = await agent(`${CTX}\n\nDFM results:\n${JSON.stringify(dfm.filter(Boolean)).slice(0,14000)}\n\nPROCESS SELECTION AND ECONOMICS. For each printed part decide FDM vs SLA vs injection moulding, and compute the BREAK-EVEN QUANTITY where tooling amortises against per-part print cost. Use real numbers: research current injection-mould tooling costs for small aluminium/steel tools for parts of these sizes, real per-cavity cycle times, and real FDM cost basis (the repo has 218 g PLA / 9.9 h and 26 g TPU / 2.4 h measured for a full set). Give a table: part, process at qty 1/10/100/1000/10000, unit cost at each, tooling cost, break-even qty. State every assumption and cite prices. Also specify print profiles for the FDM parts (layer height, walls, infill, material, supports, orientation and WHY that orientation given the load direction) and note that no brim is used in this workshop.`,
  { label:'process-economics', phase:'Process', model:'opus', effort:'high',
    schema:{ type:'object', properties:{ decisions:{type:'array', items:{type:'object', properties:{ part:{type:'string'}, process_by_qty:{type:'string'}, unit_cost_usd:{type:'string'}, tooling_usd:{type:['number','null']}, breakeven_qty:{type:['integer','null']}, rationale:{type:'string'} }, required:['part','process_by_qty'] }}, print_profiles:{type:'array', items:{type:'object', properties:{ part:{type:'string'}, layer_mm:{type:['number','null']}, walls:{type:['integer','null']}, infill_pct:{type:['integer','null']}, material:{type:'string'}, orientation:{type:'string'}, supports:{type:'string'} }, required:['part','material','orientation'] }}, assumptions:{type:'array', items:{type:'string'}}, citations:{type:'array', items:{type:'string'}}, summary:{type:'string'} }, required:['decisions','summary'] } })

phase('Assembly')
const asm = await agent(`${CTX}\n\nDFM:\n${JSON.stringify(dfm.filter(Boolean)).slice(0,7000)}\n\nASSEMBLY LINE DEFINITION. Read ce-assemblies/microduck/current/manual/MANUAL.md and joints.json. Produce the production assembly process: ordered stations, what happens at each, cycle time estimate per station, the JIGS AND FIXTURES that must be built (describe each one concretely enough to make it — what it locates, how it clamps), fastener schedule (every fastener: size, length, count, where, and torque — note that torque into plastic is unspecified by Pollen so give a researched recommendation for M2 into PLA/PETG with the basis), servo ID programming step and the risk of duplicate IDs on the daisy chain, bearing press procedure and press force, cable routing and strain relief, and the ESD precautions for the boards. Call out every step where a mistake requires disassembly.`,
  { label:'assembly-line', phase:'Assembly', model:'opus', effort:'high',
    schema:{ type:'object', properties:{ stations:{type:'array', items:{type:'object', properties:{ n:{type:'integer'}, name:{type:'string'}, operations:{type:'array',items:{type:'string'}}, cycle_min:{type:['number','null']}, tools:{type:'array',items:{type:'string'}}, risks:{type:'array',items:{type:'string'}} }, required:['n','name','operations'] }}, jigs:{type:'array', items:{type:'object', properties:{ name:{type:'string'}, purpose:{type:'string'}, description:{type:'string'} }, required:['name','purpose'] }}, fasteners:{type:'array', items:{type:'object', properties:{ spec:{type:'string'}, count:{type:['integer','null']}, location:{type:'string'}, torque_Nm:{type:['number','null']}, basis:{type:'string'} }, required:['spec','location'] }}, summary:{type:'string'} }, required:['stations','summary'] } })

phase('QA')
const qa = await agent(`${CTX}\n\nAssembly:\n${JSON.stringify(asm).slice(0,7000)}\n\nQUALITY PLAN. Define (a) incoming inspection for every bought item and every printed part — what is measured, with what instrument, to what limit, and the sampling plan; (b) in-process checks at each assembly station; (c) the END-OF-LINE FUNCTIONAL ACCEPTANCE TEST: electrical bring-up sequence and expected currents, servo enumeration on the bus (15 devices + IMU at ID 200, 1 Mbps), per-joint range-of-motion check against the measured joint limits in ce-assemblies/microduck/current/joints.json, IMU sanity, camera, ToF, audio, battery runtime, and a walk acceptance criterion (the repo measured 0.79 m in 8 s). Every test needs an explicit PASS/FAIL threshold and what to do on failure. Also list the test equipment required and any test fixture that must be built.`,
  { label:'qa-test-plan', phase:'QA', model:'opus', effort:'high',
    schema:{ type:'object', properties:{ incoming:{type:'array', items:{type:'object', properties:{ item:{type:'string'}, check:{type:'string'}, instrument:{type:'string'}, limit:{type:'string'}, sampling:{type:'string'} }, required:['item','check'] }}, inprocess:{type:'array', items:{type:'object', properties:{ station:{type:'string'}, check:{type:'string'}, limit:{type:'string'} }, required:['station','check'] }}, eol:{type:'array', items:{type:'object', properties:{ n:{type:'integer'}, test:{type:'string'}, method:{type:'string'}, pass_criterion:{type:'string'}, on_failure:{type:'string'} }, required:['n','test','pass_criterion'] }}, equipment:{type:'array',items:{type:'string'}}, fixtures:{type:'array',items:{type:'string'}}, summary:{type:'string'} }, required:['eol','summary'] } })

phase('Sourcing')
const SRC = [
  ['Actuators & motion','Dynamixel XL330-M288-T x15, the 22x16x4 and 15x15x3 bearings, any horns/hardware'],
  ['Compute, sensors & boards','Radxa Zero 3W, IMX219 camera + M12 lens, VL53L8CX ToF, LSM6DSV16X, BMI088, TLV320AIC3104, FUSB302, PN7150'],
  ['Power, cable & hardware','NP-F550 class 2S cell + holder, wiring/JST-GH harness, M2 fastener schedule, threaded inserts, filament (PLA/PETG/TPU) by the kg'],
]
const src = await parallel(SRC.map(([g, items]) => () =>
  agent(`${CTX}\n\nSOURCING — "${g}": ${items}\n\nFor EVERY line item give: exact manufacturer part number, at least TWO real distributors with live URLs, unit price at qty 1 / 100 / 1000 where shown, MOQ, stated lead time, and at least one qualified ALTERNATE with the trade-off. Note anything with a long lead time or single source as a supply risk. Cite every price with its URL and note the date. If a price is not published, say CANNOT DETERMINE with null rather than estimating. Also state the quantity per robot from the repo BOM.`,
    { label:`src:${g.slice(0,18)}`, phase:'Sourcing', model:'opus', effort:'high',
      schema:{ type:'object', properties:{ group:{type:'string'}, lines:{type:'array', items:{type:'object', properties:{ item:{type:'string'}, mpn:{type:'string'}, qty_per_robot:{type:['number','null']}, distributors:{type:'array', items:{type:'object', properties:{ name:{type:'string'}, url:{type:'string'}, price_1:{type:['number','null']}, price_100:{type:['number','null']}, price_1000:{type:['number','null']}, moq:{type:['integer','null']}, lead_time:{type:'string'} }, required:['name'] }}, alternate:{type:'string'}, risk:{type:'string'} }, required:['item','mpn','distributors'] }}, group_cost_qty1_usd:{type:['number','null']}, group_cost_qty100_usd:{type:['number','null']}, notes:{type:'string'} }, required:['group','lines'] } })))

phase('Synthesize')
const plan = await agent(`${CTX}\n\nDFM:\n${JSON.stringify(dfm.filter(Boolean)).slice(0,6000)}\n\nProcess:\n${JSON.stringify(proc).slice(0,6000)}\n\nAssembly:\n${JSON.stringify(asm).slice(0,6000)}\n\nQA:\n${JSON.stringify(qa).slice(0,5000)}\n\nSourcing:\n${JSON.stringify(src.filter(Boolean)).slice(0,8000)}\n\nCONSOLIDATE into the execution plan the team will follow. Give: the total per-robot cost at qty 1 / 100 / 1000 (mechanical + electronics + labour, stating what is missing from the roll-up); a critical-path schedule from today to first article, with durations and dependencies; the ordered list of decisions the human must make (each with options and your recommendation); every open blocker with the concrete next action and owner-role; and the risk register with likelihood/impact/mitigation. Be specific and numerical. Do not hide uncertainty.`,
  { label:'execution-plan', phase:'Synthesize', model:'opus', effort:'high',
    schema:{ type:'object', properties:{ cost_per_robot:{type:'object', properties:{ qty1_usd:{type:['number','null']}, qty100_usd:{type:['number','null']}, qty1000_usd:{type:['number','null']}, missing:{type:'array',items:{type:'string'}} }}, critical_path:{type:'array', items:{type:'object', properties:{ step:{type:'string'}, duration:{type:'string'}, depends_on:{type:'string'} }, required:['step','duration'] }}, decisions_for_human:{type:'array', items:{type:'object', properties:{ question:{type:'string'}, options:{type:'array',items:{type:'string'}}, recommendation:{type:'string'} }, required:['question','recommendation'] }}, blockers:{type:'array', items:{type:'object', properties:{ what:{type:'string'}, action:{type:'string'}, role:{type:'string'} }, required:['what','action'] }}, risks:{type:'array', items:{type:'object', properties:{ risk:{type:'string'}, likelihood:{type:'string'}, impact:{type:'string'}, mitigation:{type:'string'} }, required:['risk','mitigation'] }}, summary:{type:'string'} }, required:['summary','blockers','critical_path'] } })

return { dfm: dfm.filter(Boolean), process: proc, assembly: asm, qa, sourcing: src.filter(Boolean), plan }
