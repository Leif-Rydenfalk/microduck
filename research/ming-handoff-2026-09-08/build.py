"""Rebuild a reference-only supplier inquiry; writes exclusively beside this script."""
from pathlib import Path
import base64, hashlib, html, json, shutil, subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REV = 'MD-MING-20260908-A'
UPSTREAM = '23eab11927f95ceca0dfa35bf182caeb7db39ea0'
questions = [
('01 Original baseline / 原机基准',
 'Can you obtain access to an original Microduck? Please identify its version/serial and provide overall, head, eye-ring, ankle and both-side PCB photographs with a scale. Record component markings and measured critical dimensions. State which original unit each answer describes.',
 '能否找到可核对的 Microduck 原机？请注明版本／序列号，提供整机、头壳、眼圈、脚踝及各电路板正反面带比例尺照片，并记录元件丝印和关键尺寸实测值。每项答复请注明对应哪台原机。'),
('02 Servos and supply / 舵机与供电',
 'Confirm all 15 installed servo model suffixes, gear ratios, firmware versions and any OEM voltage variant. Catalog XL330 input is 3.7–6.0 V, while the runtime describes 6.6–8.2 V. Please establish the actual power topology and qualified measurement plan before any powered testing; do not infer servo voltage from battery voltage. Can you source the exact variant and identify included cables, horns and screws?',
 '请确认全部 15 个舵机的完整型号后缀、减速比、固件版本及是否为定制电压版本。目录 XL330 额定输入为 3.7–6.0 V，而运行程序记录 6.6–8.2 V。请先核实实际供电拓扑并提出由合格工程师执行的测量方案，再进行通电测试；不要用电池电压推断舵机供电。能否采购同版本，并列明随附线缆、舵盘及螺钉？'),
('03 Exact electronics / 电子部件原型确认',
 'Identify the fitted Robot HAT assembly/PCB revision and DNP population, IMU-to-Dynamixel bridge MCU/transceiver/firmware, and battery-contact board/contact MPN. Public HAT source is available, but production-unit identity and fit are unconfirmed. Confirm Radxa RAM/eMMC/header SKU: the stated 1GB/32GB is absent from the published catalog. Identify camera PCB, lens MPN/FOV, CSI cable pinout/contact orientation/length, ToF generation/carrier, speaker, microphone, NFC and LEDs.',
 '请确认原机 Robot HAT 装配／PCB 版本及不装件清单、IMU 转 Dynamixel 板的 MCU／收发器／固件，以及电池接触板和触点料号。官方 HAT 文件已公开，但尚未确认是否为原机同版本及是否适配。请确认 Radxa 内存／eMMC／排针完整 SKU：公开目录没有所述 1GB／32GB 配置。请识别摄像头板、镜头料号／视场角、CSI 排线针序／接点朝向／长度、ToF 代际／载板、扬声器、麦克风、NFC 和 LED。'),
('04 Battery and mechanical BOM / 电池与机械清单',
 'Identify battery maker/MPN, capacity, dimensions, mass, protection and discharge specification; NP-F550 shape alone is insufficient. Confirm each bearing maker/suffix/seal, exact fastener type and quantity, insert specification, soft-part material/Shore hardness and wire cut lengths from the original. Separate retail-kit contents from additional purchases.',
 '请确认电池厂家／料号、容量、尺寸、重量、保护及放电规格；仅知道 NP-F550 外形还不够。请按原机核对轴承厂家／后缀／密封形式、各紧固件种类及数量、嵌件规格、软胶材料／邵氏硬度和线缆下料长度。随零售套件附带的零件请与额外采购分开。'),
('05 DFM review / 可制造性评审',
 'Return marked-up reference drawings identifying inaccessible features, fit risks, wall/support concerns, assembly clearance and surface-finish issues. Propose measured process capability/coupons for bearing seats and M2 joints, including insertion/pull-out/strip tests. Quote coupon work separately; do not start it. List PCB fabrication/SMT capability, inspection and required release files. Propose changes separately with their effect on 1:1 fidelity; do not silently substitute materials or geometry.',
 '请在参考图上批注难加工特征、配合风险、壁厚／支撑、装配间隙及外观问题。请提出轴承座和 M2 连接的工艺能力／试件验证方案，包括压入、拔出及滑牙试验。试件工作单独报价，暂不启动。请提供 PCB／SMT 能力、检验方式及所需正式发布文件清单。改动建议请单列并说明对 1:1 一致性的影响，不要直接替换材料或几何。'),
('06 Separate quotations / 分别报价',
 'Please quote (a) engineering review and one prototype, (b) 100 complete units, and (c) 1,000 complete units separately. For every line state exact MPN/revision, supplier, evidence link, quantity, available stock and date, MOQ, unit price/currency, lead time, quote validity and substitutions. Separate NRE, tooling/stencils, purchased parts, PCB/SMT, printing, assembly, inspection, packaging, freight and tax. Name unresolved items and assumptions; provide a schedule conditional on identity confirmation and approved release. Confirm delivery destination before pricing freight.',
 '请分别报价：(a) 工程评审与 1 台样机，(b) 100 台整机，(c) 1,000 台整机。每项列明完整料号／版本、供应商、证据链接、数量、库存及查询日期、MOQ、单价／币种、交期、报价有效期及替代项。工程开发费、模具／钢网、外购件、PCB／SMT、打印、装配、检验、包装、运费和税费请分列。标明未决项和假设；工期以原型身份确认及正式文件批准为前提。运费报价前请确认收货地点。'),
]
message_zh = 'Ming 你好，我们希望做 Microduck 的 1:1 复刻，先确认原机版本与完整部件身份，再做样机。附件是本次参考资料和问题清单，目前仅供寻源、工程评审与报价，尚未批准制造。请优先帮忙核对原机舵机及供电、HAT／IMU 板版本、Radxa 配置、摄像头／镜头和电池的准确料号，并在图纸上标注 DFM 问题。请将工程评审＋1 台样机、100 台及 1,000 台报价分别列出，包含库存、MOQ、交期和各项费用。任何替代件或改动请单列。请先回复能提供哪些原机资料、负责工程师和预计答复时间。本次不是采购订单，也不授权投板、开模或付费试制。谢谢！'
message_en = 'Hi Ming, we want a 1:1 Microduck recreation, starting with identification of the original revision and fitted components. Attached are reference documents and questions for sourcing, engineering review and quotation; manufacturing is not approved. Please prioritize exact servo/power, HAT/IMU board revision, Radxa configuration, camera/lens and battery identification, and mark up DFM issues. Quote engineering review plus one prototype, 100 units and 1,000 units separately, including stock, MOQ, lead times and itemized costs. List substitutions and changes separately. Please first confirm available original-unit evidence, engineering owner and expected response date. This is not a purchase order or authorization for PCB fabrication, tooling or paid prototyping. Thank you.'
(HERE/'MESSAGE.txt').write_text(message_zh+'\n\n'+message_en+'\n')
sources = [
 ('docs/RECREATION-2026-09-08.md','Current correction and sourcing audit; overrides conflicting historical assertions'),
 ('research/official-hat-audit-2026-09-08.json','Pinned official HAT geometry measurement; not a physical fit test'),
 ('out/open/identity-evidence/hat/ASE01187-C1_elec_RPI_Robot_HAT_BOM.csv','Official HAT family BOM; production Microduck identity/DNP unresolved'),
 ('out/open/identity-evidence/hat/ASE01187-C1_elec_RPI_Robot_HAT_POS.csv','Official HAT family placement reference; not released for assembly'),
 ('out/open/identity-evidence/hat/LICENSE','License accompanying official HAT family evidence'),
 ('images/store/store_microduck-cream-standing-profile-left.jpg','Published product photograph; no calibrated dimension inferred'),
]
for slug in ['microduck-top-head-shell','microduck-shin','microduck-ankle-left']:
 for suffix in [slug+'.svg','result.json']:
  sources.append((f'out/drawings/{slug}/{suffix}','Historical nominal reference drawing/data; original-unit equivalence and manufacturing acceptance unresolved'))
assets=[]
for relative,purpose in sources:
 source=ROOT/relative
 target=HERE/'references'/relative
 target.parent.mkdir(parents=True,exist_ok=True)
 shutil.copyfile(source,target)
 content=target.read_bytes()
 assets.append(dict(source_path=relative,package_path=str(target.relative_to(HERE)),sha256=hashlib.sha256(content).hexdigest(),bytes=len(content),purpose=purpose,release_status='REFERENCE ONLY — NOT READY TO MANUFACTURE',source_revision=UPSTREAM if 'identity-evidence/hat/' in relative else 'working-tree snapshot; SHA-256 authoritative'))
inputs=[]
for relative in ['GOAL.md','tools/data/factory_pack.json','tools/data/factory_questions.json','tools/doc.css']:
 content=(ROOT/relative).read_bytes()
 inputs.append(dict(path=relative,sha256=hashlib.sha256(content).hexdigest()))
manifest=dict(package_revision=REV,date='2026-09-08',status='INQUIRY ONLY; NO ORDER OR FABRICATION AUTHORIZATION',repository_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),working_tree_snapshot=True,official_hat_revision=UPSTREAM,unresolved_identity=['reference production unit/revision','servo model/firmware/supply','HAT production revision/DNP','IMU bridge/controller','Radxa SKU','camera/lens/FFC','battery/contacts','ToF/carrier','speaker/NFC/LED','fasteners/bearings/materials'],inputs=inputs,attachments=assets)
(HERE/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
esc=html.escape
css=(ROOT/'tools/doc.css').read_text()
photo=ROOT/'images/store/store_microduck-cream-standing-profile-left.jpg'
body=f'<p>{REV} · 2026-09-08</p><h1>Microduck 1:1 recreation<br>Microduck 1:1 复刻询价与工程评审</h1><div class="notice"><b>INQUIRY ONLY — NOT READY TO MANUFACTURE<br>仅供询价与评审 — 尚未达到制造放行条件</b><p>No order commitment, tooling, fabrication or paid prototype authorization. Original-unit identities, critical fits and electrical suitability remain unresolved.<br>不构成采购订单，不授权开模、投板或付费试制。原机部件身份、关键配合和电气适用性仍待确认。</p></div>'
body+=f'<p>{esc(message_en)}</p><p lang="zh">{esc(message_zh)}</p>'
body+='<h2>Known correction / 已确认的资料更正</h2><p>The official HAT source at '+UPSTREAM+' is published. PCB-file outline span is 65.000034 × 30.900064 mm, thickness declaration 1 mm; four 2.7 mm mounting holes on a 58 × 23 mm pattern. These are file measurements, not production-unit measurements. Historical 65 × 48.5 mm / “no mounting holes” claims are incorrect. Match the original PCB silkscreen and assembly revision before selecting it.</p><p lang="zh">官方 HAT 文件已公开，固定版本见上。PCB 文件外形坐标跨度为 65.000034 × 30.900064 mm，声明厚度 1 mm；4 个 2.7 mm 安装孔，孔距 58 × 23 mm。以上为文件测量，不是原机实测。旧资料中 65 × 48.5 mm 及“无安装孔”的说法有误。选板前须核对原机丝印及装配版本。</p>'
body+='<h2>Reference appearance / 外观参考</h2><img style="max-width:360px;width:100%" src="data:image/jpeg;base64,'+base64.b64encode(photo.read_bytes()).decode()+'"><p>Pollen product photograph; no scale calibration / Pollen 产品照片；未作尺度标定。</p>'
for title,en,zh in questions:
 body+=f'<h2>{esc(title)}</h2><p>{esc(en)}</p><p lang="zh">{esc(zh)}</p>'
body+='<h2>Reply format / 回复格式</h2><p>Question ID | confirmed original / candidate / unknown | MPN and revision | evidence/photo/measurement | supplier and quote | owner | next action and date.<br>问题编号 | 已确认原机同款／候选／未知 | 料号及版本 | 证据／照片／测量 | 供应商及报价 | 负责人 | 下一步及日期。</p><h2>Selected references / 随附参考文件</h2><p>All attachments are reference-only snapshots. A drawing PASS is not a manufacturing release or proof of 1:1 fidelity. No Gerbers or printer commands are supplied. See manifest.json for full hashes and provenance.<br>所有附件均为参考快照。图纸 PASS 不等于制造放行，也不证明 1:1 一致性。不提供 Gerber 或打印机指令。完整哈希与来源见 manifest.json。</p><ul>'
for a in assets:
 body+=f'<li><code>{esc(a["source_path"])}</code><br>{esc(a["purpose"])}<br>SHA-256 <code>{a["sha256"]}</code></li>'
body+='</ul>'
(HERE/'BRIEF.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+REV+'</title><style>'+css+'\nbody{max-width:960px;margin:32px auto;padding:24px;font-size:16px;line-height:1.6} .notice{border:2px solid #a44220;padding:18px;background:#fff7f0} code{overflow-wrap:anywhere} h2{margin-top:32px} li{margin-bottom:16px} </style><body>'+body+'</body></html>')
print(json.dumps({'revision':REV,'attachments':len(assets),'brief_bytes':(HERE/'BRIEF.html').stat().st_size}))
