#!/usr/bin/env python3
"""Build an additional review packet. Never modifies package A or delivery state."""
from pathlib import Path
import hashlib, html, json, zipfile, shutil
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
FILES = [
 'research/ming-handoff-2026-09-08/Microduck-Ming-20260908-A.zip',
 'research/hat-pcba-rfq-2026-09-08/APPENDIX.html',
 'research/hat-pcba-rfq-2026-09-08/conditional-pcba-quote.csv',
 'research/hat-pcba-rfq-2026-09-08/audit.json',
 'research/hat-pcba-rfq-2026-09-08/manifest.json',
 'research/servo-power-audit-2026-09-08/AUDIT.md',
 'research/fastener-reconciliation-2026-09-08/AUDIT.md',
 'research/fastener-reconciliation-2026-09-08/per-line.csv',
 'research/imu-contact-identity-2026-09-08/AUDIT.md',
 'research/bearing-sourcing-2026-09-08/REPORT.html',
 'research/bearing-sourcing-2026-09-08/conditional-rfq.csv',
 'research/camera-identity-2026-09-08/REPORT.html',
 'research/hat-orientation-audit-2026-09-08.json',
 'research/original-unit-route-2026-09-08/BRIEF.html',
 'ce-parts/microduck-public-hat-y1/docs/SOURCE-FACTS.json',
 'ce-parts/microduck-public-hat-y1/datasheet.pdf',
 'reference/pollen-elec-rpi-robot-hat/production/PCB01186-C1_elec_RPI_Robot_HAT_PCB.zip',
]
TEXT = '''Ming 你好，这是 Microduck 1:1 复原的补充工程评审包 B，内含原参考包 A。
请先打开 READ-FIRST.html。新增资料列出 PCB DRC／铜厚／元件问题、舵机供电核查步骤、紧固件遗漏和轴承尺寸纠正。
请安排工程师评审，并帮助确认原机版本、实物与板件标识，再反馈 DFM、准确物料和报价。
这些文件用于工程评审和询价，尚未批准采购或生产。请回复负责人和预计反馈日期。谢谢！

Hi Ming, this is supplemental engineering review packet B for the 1:1 Microduck recreation, including original reference packet A.
Please open READ-FIRST.html. New material covers PCB DRC/copper/component issues, servo-power evidence capture, missing fastener lines and a bearing width correction.
Please assign an engineer, help identify the original unit/revision and fitted boards, and return DFM feedback, exact parts and an itemized quote.
These files are for review and quotation; purchasing and production are not released. Please confirm the engineering contact and expected response date. Thank you.
'''

def main():
 delivery=OUT/"delivery.json"
 if delivery.exists() and json.loads(delivery.read_text()).get("sent"):
  raise SystemExit("Packet B has been sent; create a new revision instead of rebuilding it")
 records=[]
 for rel in FILES:
  p=ROOT/rel
  data=p.read_bytes()
  local=OUT/'evidence'/rel
  local.parent.mkdir(parents=True,exist_ok=True)
  shutil.copy2(p,local)
  records.append(dict(path='evidence/'+rel,source=rel,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
 labels = ['Original reference package A / 原参考包 A', 'PCBA engineering questions / PCB 工程评审', 'PCBA quote quantities / PCB 报价数量', 'PCBA audit data', 'PCBA source manifest', 'Servo power evidence procedure / 舵机供电核查', 'Fastener omissions and thread identity / 紧固件遗漏与牙型', 'Fastener line comparison / 紧固件逐行对照', 'IMU and contact-board identity / IMU 与触点板身份', 'Bearing source comparison / 轴承来源比较', 'Bearing quote quantities / 轴承报价数量', 'Camera and cable comparison / 相机与排线比较', 'HAT orientation correction / HAT 朝向纠正', 'Original-unit access / 原机获取途径', 'Oscillator source facts / 晶振来源证据', 'Oscillator family datasheet / 晶振系列规格书', 'Official public HAT Gerbers / 官方公开 HAT 制板文件']
 assert len(labels)==len(records)
 links=''.join('<li><a href="'+html.escape(r['path'])+'">'+html.escape(label)+'</a></li>' for r,label in zip(records,labels))
 page='''<!doctype html><meta charset="utf-8"><title>Microduck review packet B</title><style>body{max-width:960px;margin:40px auto;padding:0 24px;font:18px/1.6 system-ui}li{margin:12px 0;overflow-wrap:anywhere}.notice{border:2px solid #a43;padding:18px}h1{line-height:1.25}</style><h1>Microduck 工程评审补充包 B<br>Microduck engineering review packet B</h1><p class="notice">仅供评审和询价。原机身份、板卡适配和电气限制尚未确认，未批准采购或制造。<br>Review and quotation only. Original-unit identity, board fit and electrical limits remain unresolved. No purchasing or manufacturing release.</p><p>原包 A 保持原样；本补充包列出后续核查发现。旧图纸的检查结果不代表目前已通过制造验收。<br>Package A is preserved as its dated snapshot. This supplement records subsequent findings. Historical drawings do not establish manufacturing acceptance.</p><ol>'''+links+'''</ol><p>manifest.json records attachment hashes. Sources in the reports identify public-board evidence separately from the unconfirmed original unit. Requested quantities are quotation scenarios, not orders.</p>'''
 (OUT/'MESSAGE.txt').write_text(TEXT)
 (OUT/'READ-FIRST.html').write_text(page)
 manifest=dict(id='MD-MING-20260908-B',purpose='Engineering review and conditional quotation',files=records,supersedes_delivery_packet='A included unchanged; no prior delivery claimed')
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 archive=OUT/'Microduck-Ming-20260908-B.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for name in ('MESSAGE.txt','READ-FIRST.html','manifest.json'):z.write(OUT/name,name)
  for r in records:z.write(OUT/r['path'],r['path'])
 with zipfile.ZipFile(archive) as z:
  for r in records:assert hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256']
 result=dict(archive=archive.name,bytes=archive.stat().st_size,sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),verified_attachments=len(records),delivery='not attempted by this builder')
 (OUT/'build-verification.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
