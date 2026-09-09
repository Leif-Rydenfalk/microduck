"""Build "01 For suppliers": what Ming needs to get quotes and parts moving.

    python3 tools/export_supplier_pack.py --review reviews/v0003 --bundles <dir with 00 folder> --out <same dir>

Leif, 2026-09-09: "think from his perspective: he gets this document, then what?
He owns factories and has a bunch of contacts; this document must contain
everything he needs." So the folder is organised by what Ming does next:
read one page, forward one packet per supplier type, collect prices on one
sheet, and not buy the things that are still undecided. All data comes from
spec/sourcing.json, out/release/bom.csv, docs/DFM.md, docs/PRODUCTION.md,
out/procurement/SOURCING-CN.md, the three PCB fab packages and the licence
position. Nothing here sends anything.
"""
import argparse, csv, html, json, re, shutil, struct, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from xlsx_min import write_xlsx

FOLDER = '01 For suppliers'
TIERS = [1, 10, 100]
ADDRESS_CN = '广东省深圳市福田区华强北 深南中路2070号 电子科技大厦 405室  收件人：Leif Rydenfalk  电话：[Leif 填写]'
ADDRESS_EN = 'Black Ark, Room 405, Electronic Technology Building (电子科技大厦), 2070 Shennan Middle Road, Huaqiangbei, Futian, Shenzhen. Consignee: Leif Rydenfalk. Phone: [Leif fills in]'

CN = {'B1': '舵机 ROBOTIS DYNAMIXEL XL330-M288-T', 'B2': '舵机总线线 X3P 180mm（10条装）', 'B3': 'Radxa ZERO 3W 单板电脑', 'B4': 'NP-F550 型 2S 锂电池 + 双充充电器', 'B6': 'IMX219 摄像头板（M12 接口）', 'B7': 'M12 广角镜头', 'B8': '22pin 0.5mm MIPI CSI 排线', 'B9': 'ToF 8×8 激光测距模块（VL53L5CX / L8CX）', 'B10': '微型轴承 22×16×4（MR1622）', 'B11': '微型轴承 15×10×3（MR6700 开式）', 'B12': '喇叭 35×25×7mm 8Ω 2W（待核实）', 'B13': '麦克风（型号未定）', 'B14': 'NFC 读卡芯片 + 2 个天线', 'B15': '摄像指示 LED', 'B16': '蓝牙手柄（Xbox 布局）', 'B17': 'USB-C 线', 'B18a': 'M2×6 内六角螺丝 不锈钢', 'B18b': 'M2 内六角螺丝其他长度 + M2 螺母 + M2.5×6', 'B18c': 'M2 热熔铜螺母', 'B19a': 'PLA 耗材 1.75mm', 'B19b': 'TPU 85A 耗材 1.75mm', 'P1c': '音频编解码芯片 TLV320AIC3104IRHBR', 'P2c': '六轴 IMU LSM6DSV16X', 'P1d': '六轴 IMU BMI088（可选）', 'R1': 'USB-C PD 控制芯片（参考，随 Radxa 板自带）', 'R2': 'MCP73213 充电管理芯片（参考，在充电器内）', 'R3': 'S-8252 电池保护芯片（参考，在电池内）', 'C1': 'JST EH 3pin 连接器套件（自制舵机线束用）', 'C2': 'JST SH 4pin / GH 2pin 连接器', 'P1': 'Robot HAT 定制 PCB', 'P2': 'imu_to_dxl v2 定制 PCB', 'P3': 'banana 电池触点 PCB'}
PACKET = {'A': ['B19a', 'B19b'], 'B': ['B1', 'B2', 'C1'], 'C': ['B10', 'B11', 'B18a', 'B18b', 'B18c'], 'D': ['B14', 'P1c', 'P2c', 'P1d', 'R1', 'R2', 'R3', 'C2'], 'E': ['P1', 'P2', 'P3'], 'F': ['B3', 'B4', 'B6', 'B7', 'B8', 'B9', 'B12', 'B13', 'B15', 'B16', 'B17']}
PACKET_NAME = {'A': ('Packet A - plastic parts (3D print now, mould later)', '塑料件（现打印，后开模）'), 'B': ('Packet B - servos and servo cables (decision pending)', '舵机与线束（待决定）'), 'C': ('Packet C - bearings, screws, inserts', '轴承、螺丝、热熔螺母'), 'D': ('Packet D - chips and connectors (LCSC or agent)', '芯片与连接器'), 'E': ('Packet E - PCB fab and SMT (quote only, not released)', 'PCB 打样与贴片（仅报价）'), 'F': ('Packet F - computer, camera, battery, sensors, misc', '电脑、摄像头、电池、传感器、杂项')}
ACTION = {  # what Ming may do with the line right now
    'B1': ('QUOTE BOTH ROUTES, DO NOT BUY: Dynamixel XL330 (imported) vs Feetech STS3215 (Shenzhen). Leif decides after prices.', '两条路线都报价，先不买：Dynamixel XL330（进口）对比 飞特 STS3215（深圳本地）。Leif 看价后决定。'),
    'B2': ('Quote with the servos; retail XL330 may include one lead each.', '与舵机一起报价；零售 XL330 可能每只附一条线。'),
    'C1': ('Only if we crimp our own harness; quote as alternative to B2.', '仅在自制线束时需要；作为 B2 的替代报价。'),
    'B3': ('CONFIRM FIRST: the 1 GB/32 GB configuration is not in Radxa\'s catalogue. Propose what is in stock (2 GB/16 GB preferred).', '先确认：1GB/32GB 配置官网目录没有。请报现货配置（优先 2GB/16GB）。'),
    'B4': ('Confirm pack and charger identity, then buy 1 set.', '确认电池和充电器型号后可买 1 套。'),
    'B6': ('Confirm board revision and lens; send photo/datasheet before buying.', '先确认板型和镜头，购买前发照片/规格书。'),
    'B7': ('Quote 70/90/140 degree options; FOV not fixed.', '报 70/90/140 度三种；视角未定。'),
    'B8': ('Buy 100/150/200 mm one each once camera end is known.', '摄像头端确定后各买一条 100/150/200mm。'),
    'B9': ('Quote VL53L5CX and VL53L8CX carriers with mounting drawing.', 'VL53L5CX 与 VL53L8CX 模块都报价，附安装尺寸图。'),
    'B10': ('OK to buy for 1 robot (11 pcs). Quote ZZ and open.', '可买 1 台用量（11 个）。带盖和开式都报价。'),
    'B11': ('OK to buy (3 pcs); 3 mm wide, not the common 4 mm 6700ZZ.', '可买（3 个）；宽 3mm，不要用常见 4mm 宽的 6700ZZ 代替。'),
    'B12': ('Buy one cheap candidate, measure, then confirm.', '先买一个便宜候选，量尺寸后确认。'),
    'B13': ('Not quotable yet (type and count unknown).', '暂无法报价（类型、数量未定）。'),
    'B14': ('Quote PN7150 or ST25R3916 route; whether the robot needs NFC at all is open.', '报 PN7150 或 ST25R3916 方案；是否需要 NFC 尚未定。'),
    'B15': ('Not quotable yet.', '暂无法报价。'),
    'B16': ('Commodity; any Xbox-layout BT gamepad.', '通用件；任意 Xbox 布局蓝牙手柄。'),
    'B17': ('Commodity.', '通用件。'),
    'B18a': ('QUOTE ONLY; a cheap assortment set is fine. Thread form and lengths not final.', '仅报价；便宜的套装可以买。牙型和长度未定。'),
    'B18b': ('Same as B18a.', '同 B18a。'),
    'B18c': ('Quote 60 pcs class; assortment acceptable.', '报 60 个左右；套装可以。'),
    'B19a': ('OK to buy 1 kg (Bambu PLA Basic or equal).', '可买 1kg（拓竹 PLA Basic 或同级）。'),
    'B19b': ('OK to buy 0.5-1 kg TPU 85A.', '可买 0.5-1kg TPU 85A。'),
    'P1c': ('Quote; buy only together with the PCB build.', '报价；与 PCB 一起买。'), 'P2c': ('Quote; long lead time reported (24 weeks at DigiKey).', '报价；有报道交期长（DigiKey 24 周）。'), 'P1d': ('Optional footprint; quote only.', '可选位置；仅报价。'),
    'R1': ('Reference only, never ordered separately.', '仅参考，不单独采购。'), 'R2': ('Reference only.', '仅参考。'), 'R3': ('Reference only.', '仅参考。'),
    'C2': ('Quote housings + crimp contacts, 2 of each per robot.', '报壳体 + 端子，每台各 2 个。'),
    'P1': ('QUOTE BARE BOARD FROM GERBERS ONLY. Design has open DRC failures; do not fabricate.', '仅按 Gerber 报裸板价。设计尚有 DRC 问题，不要投产。'), 'P2': ('Same as P1.', '同 P1。'), 'P3': ('Bare board quote, ENIG, 4.6 mm wide strip.', '裸板报价，沉金，4.6mm 宽条板。'),
}
VISIBLE = {'microduck-trunk-shell-left', 'microduck-trunk-shell-right', 'microduck-top-head-shell', 'microduck-bottom-head-shell', 'microduck-jaw', 'microduck-face-part', 'microduck-ankle-left', 'microduck-ankle-right', 'microduck-foot-left', 'microduck-foot-right'}
FAB = {'P1': 'electronics/robot-hat/out/fab/microduck_robot_hat-fab.zip', 'P2': 'electronics/imu-to-dxl/out/fab/microduck_imu_to_dxl-fab.zip', 'P3': 'electronics/banana-contact/out/fab/microduck_banana_contact-fab.zip'}
BOARD = {'P1': 'Robot HAT 65.0 x 30.0 mm, 2 layers, 0.15 mm min track', 'P2': 'imu_to_dxl v2 40.0 x 22.0 mm, 2 layers, 0.15 mm min track', 'P3': 'banana battery-contact strip 45.8 x 4.6 mm, corner R0.5, ENIG'}


def stl_volume_cm3(path):
    data = Path(path).read_bytes(); n = struct.unpack_from('<I', data, 80)[0]; v = 0.0
    for row in struct.iter_unpack('<12fH', data[84:84+50*n]):
        a, b, c = row[3:6], row[6:9], row[9:12]
        v += (a[0]*(b[1]*c[2]-b[2]*c[1]) - a[1]*(b[0]*c[2]-b[2]*c[0]) + a[2]*(b[0]*c[1]-b[1]*c[0]))/6
    return abs(v)/1000


def dfm_grams(project):
    g = {}
    for line in (project/'docs/DFM.md').read_text().splitlines():
        m = re.match(r'\|\s*\**([a-z0-9\-]+)\**\s*\|\s*(PLA|TPU)\s*\|[^|]*\|[^|]*\|[^|]*\|\s*([\d.]+)\s*\|', line)
        if m: g['microduck-'+m.group(1)] = float(m.group(3))
    return g


def cn_block(md, heading):
    """First fenced block after a heading in SOURCING-CN.md."""
    i = md.index(heading); j = md.index('```', i); k = md.index('```', j+3)
    return md[j+3:k].strip()


def csvw(path, rows, fields=None):
    with path.open('w', newline='', encoding='utf-8-sig') as fh:
        w = csv.DictWriter(fh, fieldnames=fields or list(rows[0])); w.writeheader(); w.writerows(rows)


def page(title, body):
    css = 'body{font:16px/1.55 system-ui;max-width:1000px;margin:32px auto;padding:0 16px;color:#163447}table{border-collapse:collapse;width:100%;font-size:14px}td,th{border-bottom:1px solid #d2e0e5;padding:7px;text-align:left;vertical-align:top}small{color:#506874}.warn{background:#fff1cf;padding:10px 14px;border-radius:8px}h2{margin-top:28px}li{margin:6px 0}'
    return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+'</title><style>'+css+'</style>'+body+'</html>'


def build(review, out, project=ROOT):
    review = review.resolve(); out = out.resolve(); project = project.resolve()
    dest = out/FOLDER
    if dest.exists(): raise FileExistsError(str(dest))
    dest.mkdir(parents=True)
    src = json.loads((project/'spec/sourcing.json').read_text()); lines = {l['id']: l for l in src['lines']}
    priced = {r['line_id']: r for r in csv.DictReader((project/'out/release/bom.csv').open(encoding='utf-8-sig'))}
    cnmd = (project/'out/procurement/SOURCING-CN.md').read_text()
    packet_of = {lid: k for k, v in PACKET.items() for lid in v}
    report = {'lines': len(lines), 'files': []}

    # ---- BOM and reply sheet
    bom = []
    for lid, l in lines.items():
        q = l.get('qty_per_robot'); pr = priced.get(lid, {})
        price = pr.get('unit_price', ''); price = price if re.match(r'^[\d.]+$', str(price)) else ''
        bom.append({'id': lid, 'packet': packet_of.get(lid, ''), 'item': l['item'], '中文': CN.get(lid, ''), 'category': l.get('category', ''),
                    'qty per robot': q if q is not None else '', 'qty for 10 robots': (q*10 if isinstance(q, (int, float)) else ''), 'qty for 100 robots': (q*100 if isinstance(q, (int, float)) else ''),
                    'exact part (MPN)': l.get('mpn') or '', 'identity status': l.get('mpn_status') or '', 'verdict': l.get('verdict', ''),
                    'what to do now': ACTION.get(lid, ('', ''))[0], '现在怎么做': ACTION.get(lid, ('', ''))[1],
                    'specification for the supplier': (l.get('rfq_spec') or '').replace('\n', ' '),
                    'best price we read (unit)': price, 'currency': pr.get('currency', '') if price else '', 'read from vendor': pr.get('vendor', '') if price else '',
                    'open questions': ' | '.join(l.get('unknowns') or [])})
    csvw(dest/'BOM - all purchased parts.csv', bom)
    reply = [{'id': r['id'], 'item': r['item'], '中文': r['中文'], 'qty per robot': r['qty per robot'], 'supplier name 供应商': '', 'exact model offered 型号': '', 'unit price 单价': '', 'currency 币种': 'CNY', 'MOQ 起订量': '', 'lead time 交期': '', 'in stock in Shenzhen? 深圳现货?': '', 'link / photo / datasheet 链接': '', 'notes 备注': ''} for r in bom if r['verdict'] != 'reference']

    # ---- printed parts table
    parts = list(csv.DictReader((review/'PARTS.csv').open(encoding='utf-8-sig')))
    manifest = json.loads((project/'out/print/stl_manifest.json').read_text()); grams = dfm_grams(project)
    printed = []
    for r in parts:
        s = r['slug']
        if s not in manifest: continue
        m = manifest[s]; stl = review/r['stl']; vol = stl_volume_cm3(stl); bb = json.loads(r['measured_bbox_mm']) if r.get('measured_bbox_mm') else []
        printed.append({'number': int(r['number']), 'part': r['part'], 'slug': s, 'qty per robot': int(m.get('qty') or 1), 'material': m['material'], 'size mm (x y z)': ' x '.join('%.1f' % v for v in bb),
                        'solid volume cm3': round(vol, 2), 'sliced weight g (FDM 0.2 mm)': grams.get(s, ''), 'process now': 'FDM print (%s)' % m['material'],
                        'at 1000 units': 'visible part: injection mould candidate after DFM redesign' if s in VISIBLE else 'keep printing (small bracket) or MJF', 'drawing PDF': '', 'STL': 'in Packet A / STL zip', 'STEP': 'in Packet A / STEP zip', 'geometry source': r['source_kind']})
    for p in printed: reply.append({'id': 'PRINT-%02d' % p['number'], 'item': p['part'], '中文': '', 'qty per robot': p['qty per robot'], 'supplier name 供应商': '', 'exact model offered 型号': p['material'], 'unit price 单价': '', 'currency 币种': 'CNY', 'MOQ 起订量': '', 'lead time 交期': '', 'in stock in Shenzhen? 深圳现货?': '', 'link / photo / datasheet 链接': '', 'notes 备注': 'print quote at 1 / 10 / 100 sets'})
    csvw(dest/'REPLY SHEET - fill in prices.csv', reply)
    write_xlsx(dest/'BOM - all purchased parts.xlsx', {'Purchased parts': [list(bom[0])]+[[r[k] for k in bom[0]] for r in bom], 'Printed parts': [list(printed[0])]+[[r[k] for k in printed[0]] for r in printed]})
    write_xlsx(dest/'REPLY SHEET - fill in prices.xlsx', {'Reply': [list(reply[0])]+[[r[k] for k in reply[0]] for r in reply]})

    # ---- packets
    bundles = out/'00 Open in your own software'
    def packet(key):
        d = dest/PACKET_NAME[key][0]; d.mkdir(); rows = [r for r in bom if r['packet'] == key]
        if rows: csvw(d/'LINES.csv', rows)
        return d, rows
    # A plastics
    d, rows = packet('A')
    csvw(d/'PRINTED PARTS.csv', printed); write_xlsx(d/'PRINTED PARTS.xlsx', {'Printed parts': [list(printed[0])]+[[r[k] for k in printed[0]] for r in printed]})
    for name in ('STL - all 30 printed parts.zip', 'STEP 4 - one file per printed part.zip', '3MF 2 - print all PLA parts.3mf', '3MF 3 - print all TPU parts.3mf'):
        if (bundles/name).is_file(): shutil.copyfile(bundles/name, d/name)
    (d/'Drawings (PDF)').mkdir(); n_pdf = 0
    for p in printed:
        folder = review/'02 Look at the parts'/('%02d %s' % (p['number'], p['part']))/'Drawings and details'
        for pdf in sorted(folder.glob('*.pdf')):
            shutil.copyfile(pdf, d/'Drawings (PDF)'/('%02d %s%s.pdf' % (p['number'], p['part'], '' if pdf.stem.endswith(p['slug'].split('-', 1)[1]) else ' - '+pdf.stem))); n_pdf += 1; p['drawing PDF'] = 'yes'
    tot_g = sum(float(p['sliced weight g (FDM 0.2 mm)'] or 0)*p['qty per robot'] for p in printed)
    (d/'REQUEST - paste to supplier.txt').write_text(
        'REQUEST FOR QUOTE - printed plastic parts / 询价：3D 打印塑料件\n\n'
        'EN: Please quote FDM printing of the attached %d parts (%d pieces per robot, %d PLA + %d TPU 85A pieces, about %.0f g PLA/TPU per set) at 1 / 10 / 100 sets, 0.2 mm layer, natural or grey colour, supports removed, bearing bores to size. Files: STL zip (every part), STEP zip (same parts as STEP), 3MF plates, PDF drawings for %d parts. Also state: (a) your printer type, (b) delivery time per set, (c) whether you can do 1 mm walls (rigidity plate) and Ø15 bearing seats within +0/-0.1 mm. Separate question for later: injection-mould tooling estimate for the 10 visible parts marked "mould candidate" in PRINTED PARTS.xlsx at 1000 sets, after we redesign for draft.\n\n'
        '中文：请按附件报 %d 个零件（每台 %d 件，PLA %d 件 + TPU 85A %d 件，每套约 %.0f 克）的 FDM 打印价格，数量 1 / 10 / 100 套，层高 0.2mm，本色或灰色，去除支撑，轴承孔按图到位。文件：STL 压缩包（全部零件）、STEP 压缩包（同样零件）、3MF 打印盘、%d 个零件的 PDF 图纸。另请说明：(a) 打印机类型，(b) 每套交期，(c) 能否做 1mm 薄壁（加强板）和 Ø15 轴承位公差 +0/-0.1mm。另一个以后的问题：PRINTED PARTS.xlsx 中标注 "mould candidate" 的 10 个外观件，我们改好拔模后，1000 套的注塑开模估价。\n\n'
        'Delivery / 收货：%s\n' % (len(printed), sum(p['qty per robot'] for p in printed), sum(p['qty per robot'] for p in printed if p['material'] == 'PLA'), sum(p['qty per robot'] for p in printed if p['material'] == 'TPU'), tot_g, n_pdf,
                                     len(printed), sum(p['qty per robot'] for p in printed), sum(p['qty per robot'] for p in printed if p['material'] == 'PLA'), sum(p['qty per robot'] for p in printed if p['material'] == 'TPU'), tot_g, n_pdf, ADDRESS_CN))
    csvw(d/'PRINTED PARTS.csv', printed)
    # B servos
    d, rows = packet('B')
    servo_step = project/'ce-parts/xl330-m288-t/iterations/v0.0.1/geometry/robotis-xl-xc-330.stp'
    if servo_step.is_file(): shutil.copyfile(servo_step, d/'ROBOTIS XL330 manufacturer STEP.stp')
    (d/'REQUEST - paste to supplier.txt').write_text(
        'SERVOS - TWO ROUTES, QUOTE BOTH, BUY NOTHING YET / 舵机：两条路线都报价，先不买\n\n'
        'Why: the current CAD is modelled on the ROBOTIS XL330-M288-T (imported, about US$23.90 each, 15 per robot). Feetech STS3215 7.4 V (Shenzhen, about ¥100) would cut cost ~60% and remove the import, but the leg and head brackets must be re-modelled for it. Leif decides after seeing both prices. Also note: the XL330 is rated 3.7-6 V while our battery window is 6.6-8.2 V, so the power route is not settled either.\n'
        '原因：现有 CAD 按 ROBOTIS XL330-M288-T 建模（进口，约 23.9 美元/只，每台 15 只）。飞特 STS3215 7.4V（深圳，约 100 元）可省约 60% 并免进口，但腿部和头部支架要重新建模。Leif 看到两边价格后决定。另外 XL330 额定 3.7-6V，而电池窗口 6.6-8.2V，供电方案也未定。\n\n'
        'Quantities / 数量：1 robot: 15 + 2 spare = 17；10 robots: 152；100 robots: 1502.\n\n'
        '=== Route 1: Feetech STS3215 (paste to 1688 / 淘宝 / 飞特官方店) ===\n'+cn_block(cnmd, '### 询价 message — Feetech STS3215')+'\n\n'
        '=== Route 2: ROBOTIS DYNAMIXEL XL330-M288-T ===\n'
        'EN: Please quote genuine ROBOTIS DYNAMIXEL XL330-M288-T (SKU 902-0163-000) at 17 / 152 / 1502 pieces, with Robot Cable-X3P 180 mm leads (10-pack, SKU 903-0251-000) for 16 / 160 / 1600 leads, and state whether each retail servo includes one lead. Confirm M288-T vs M077-T availability. Lead time and whether stock is in Shenzhen or imported.\n'
        '中文：请报原装 ROBOTIS DYNAMIXEL XL330-M288-T（货号 902-0163-000）17 / 152 / 1502 只的价格，以及 X3P 180mm 舵机线（10 条装，903-0251-000）16 / 160 / 1600 条；请说明零售舵机是否每只附一条线，M288-T 与 M077-T 哪个有货，交期，深圳现货还是进口。\n\n'
        'Harness alternative (if we crimp our own) / 自制线束替代：JST EH 3-pin housings EHR-3 x32 per robot, SEH-001T-P0.6 contacts x96 per robot, 22 AWG wire.\n\nDelivery / 收货：%s\n' % ADDRESS_CN)
    # C mechanical
    d, rows = packet('C')
    (d/'REQUEST - paste to supplier.txt').write_text(
        'BEARINGS, SCREWS, INSERTS / 轴承、螺丝、热熔螺母\n\n'
        'Per robot / 每台：bearing 22x16x4 (MR1622, quote ZZ shielded AND open) x11；bearing 15x10x3 (MR6700 open, 3 mm wide - NOT the 4 mm 6700ZZ) x3；M2 socket-head screws (4/6/8/12 mm, about 195 total) + M2 nuts x50 + M2.5x6 x20；M2 heat-set brass inserts ~3 mm x60.\n'
        'For 10 robots multiply by 10; for 100 by 100. Bearings can be bought now for 1 robot. Screws: QUOTE ONLY, or buy one cheap assortment; thread form and lengths are not final (the servo tapping screws are a separate question).\n'
        '10 台乘 10，100 台乘 100。轴承可先买 1 台用量。螺丝：仅报价，或买一套便宜套装；牙型和长度未定（舵机自攻螺钉另行确认）。\n\n'
        '华强北 walk-in / 一句话：\n'+cn_block(cnmd, '### 华强北 walk-in phrase')+'\n\n'
        'Taobao references found by the replica builder (not verified by us) / 复刻者用过的淘宝链接（未经我们核实）：NBZH 永天轴承 ¥2.2 (539024647147)；鑫燚 NSK both sizes ¥5 (670727787832)；广州信邦 M2 套装 600 pcs ¥26.8 (842110292995)；榕誉 M2 热熔螺母 400 pcs ¥22 (1000673642588).\n\nDelivery / 收货：%s\n' % ADDRESS_CN)
    # D chips
    d, rows = packet('D')
    shutil.copyfile(project/'out/procurement/lcsc-bom.csv', d/'LCSC upload - lcsc-bom.csv')
    (d/'REQUEST - paste to supplier.txt').write_text(
        'CHIPS AND CONNECTORS / 芯片与连接器\n\n'
        'EN: Quote the lines in LINES.csv at 1 / 10 / 100 robots (quantity per robot in the sheet), authorised channel with date codes. Key parts: TLV320AIC3104IRHBR (LCSC C181753, verified), LSM6DSV16XTR, BMI088 (optional), NFC route PN7150 or ST25R3916 (open), JST SH 4-pin SHR-04V-S-B and GH 2-pin GHR-02V-S housings with contacts (2 each per robot). Buy only together with the PCB build.\n'
        '中文：请按 LINES.csv 报 1 / 10 / 100 台的价格（每台用量见表），正规渠道并注明批号。主要器件：TLV320AIC3104IRHBR（立创 C181753，已核实）、LSM6DSV16XTR、BMI088（可选）、NFC 方案 PN7150 或 ST25R3916（未定）、JST SH 4pin SHR-04V-S-B 与 GH 2pin GHR-02V-S 壳体及端子（每台各 2 个）。与 PCB 一起采购。\n'
        'LCSC upload file: "LCSC upload - lcsc-bom.csv" / 立创 BOM 工具可直接上传。\n')
    # E PCB
    d, rows = packet('E'); n_fab = 0
    for lid, rel in FAB.items():
        if (project/rel).is_file(): shutil.copyfile(project/rel, d/('%s - %s' % (lid, Path(rel).name))); n_fab += 1
    hat = project/'out/pcb/hat/robot-hat-pcba.step'
    if hat.is_file(): shutil.copyfile(hat, d/'P1 Robot HAT assembled board (STEP, reference).step')
    (d/'REQUEST - paste to supplier.txt').write_text(
        'PCB FAB AND SMT - QUOTE ONLY, DESIGN NOT RELEASED / PCB 打样与贴片：仅报价，设计未放行\n\n'
        'IMPORTANT: all three boards still have open design-rule failures and connector/version questions. Please quote from the Gerbers but DO NOT manufacture until Leif releases them. / 重要：三块板都还有 DRC 未通过和连接器/版本问题。请按 Gerber 报价，Leif 放行前不要投产。\n\n'
        'Boards / 板：\n' + ''.join('  %s: %s\n' % (lid, BOARD[lid]) for lid in FAB) +
        '\nEN: Quote bare boards at 5 / 50 / 500 pieces each (2-layer, 1.6 mm FR-4, HASL lead-free; P3 ENIG), and turnkey SMT for P1 and P2 with the BOM and positions.csv inside each fab zip. State minimum track/space you accept (we have 0.15 mm), lead time, and whether you can source the ICs listed in Packet D. We also need a contact for a PCB engineer who can review the HAT design.\n'
        '中文：请报裸板 5 / 50 / 500 片价格（两层，1.6mm FR-4，无铅喷锡；P3 沉金），以及 P1、P2 的贴片代工价（BOM 和坐标文件在各自 fab 压缩包内）。请说明可接受的最小线宽/线距（我们是 0.15mm）、交期，以及能否代购 Packet D 的芯片。另外我们需要一位能评审 HAT 板设计的 PCB 工程师联系方式。\n'
        'Fab packages included / 附件：%d of 3\n' % n_fab)
    # F computer, camera, battery, sensors
    d, rows = packet('F')
    (d/'REQUEST - paste to supplier.txt').write_text(
        'HEAD PARTS FIRST / 头部件优先（Radxa、摄像头、ToF、喇叭、电池）\n\n'
        'This is the same list Leif sent on 2026-09-08 (see ALREADY SENT). Nothing changed. For each item we need: link or local shop, exact model, price, earliest delivery, and a photo/datasheet if the model is uncertain. Confirm before buying.\n'
        '与 2026-09-08 已发清单一致（见 ALREADY SENT），没有变化。每项需要：链接或本地店、准确型号、价格、最早到货，型号不确定的发照片/规格书。确认后再买。\n\n'
        + ''.join('%s  %s\n   EN: %s\n   中文: %s\n   Spec: %s\n\n' % (r['id'], r['item'], ACTION.get(r['id'], ('', ''))[0], ACTION.get(r['id'], ('', ''))[1], r['specification for the supplier'][:300]) for r in rows)
        + 'Delivery / 收货：%s\n' % ADDRESS_CN)

    # ---- already sent, licence, open decisions
    shutil.copyfile(project/'research/ming-parts-request-2026-09-08/MESSAGE.txt', dest/'ALREADY SENT - parts list of 2026-09-08 (unchanged).txt')
    lic = project/'LICENCE-POSITION.html'
    if lic.is_file(): shutil.copyfile(lic, dest/'LICENCE - read before quoting production.html')
    (dest/'LICENCE - short version.txt').write_text(
        'LICENCE, IN SHORT / 许可证简述\n\n'
        'The reference 3D models come from Pollen Robotics under CC BY-NC-SA (non-commercial). Building prototypes and quoting parts for our own engineering is fine. SELLING robots made from that geometry is not allowed by that licence at any quantity; the parts we designed ourselves (the 10 "solid CAD" parts) are ours, the mesh-only parts are derived from Pollen\'s. Any production run beyond prototypes is a licensing decision for Leif before any tooling is ordered. Details with sources: "LICENCE - read before quoting production.html".\n\n'
        '参考 3D 模型来自 Pollen Robotics，许可证为 CC BY-NC-SA（非商业）。做样机和为我们自己的工程报价没有问题。用这些几何生产销售机器人不被该许可证允许，无论数量。我们自己设计的零件（10 个 "solid CAD" 件）归我们，网格件来源于 Pollen。样机以外的量产是 Leif 在下任何模具订单前要先决定的许可问题。详情见 "LICENCE - read before quoting production.html"。\n')
    decisions = [
        ('Servo route: Dynamixel XL330 vs Feetech STS3215', '舵机路线：XL330 还是 飞特 STS3215', 'Quote both (Packet B). Do not buy servos. Also the XL330 supply voltage conflict is real, not a typo.', '两边报价（Packet B），先不买舵机。XL330 供电电压冲突是真实存在的。'),
        ('Screw thread form and lengths', '螺丝牙型和长度', 'Quote only; the servo screws are M2 tapping into Ø1.6 pilots, max 3 mm deep, not standard M2.', '仅报价；舵机螺钉为 Ø1.6 底孔自攻，最深 3mm，不是普通 M2。'),
        ('Radxa ZERO 3W configuration', 'Radxa ZERO 3W 配置', 'The 1 GB/32 GB SKU does not exist; propose what is in stock, 2 GB/16 GB preferred.', '1GB/32GB 不存在；报现货配置，优先 2GB/16GB。'),
        ('Camera board, lens FOV, CSI cable', '摄像头板、镜头视角、排线', 'Board revision and FOV not fixed; quote options, buy after photo/datasheet.', '板型和视角未定；报几种，看照片/规格书后再买。'),
        ('ToF generation (L5CX vs L8CX)', 'ToF 代际', 'Quote both carriers with mounting drawings.', '两种模块都报价并附安装图。'),
        ('PCBs', 'PCB', 'DRC failures open; quote from Gerbers, do not fabricate.', 'DRC 未通过；按 Gerber 报价，不投产。'),
        ('Charger float voltage (8.2/8.4/8.7/8.8 V)', '充电器浮充电压', 'Affects the MCP73213 suffix; nobody has chosen yet.', '影响 MCP73213 后缀；尚未选定。'),
    ]
    (dest/'OPEN DECISIONS - do not order these yet.txt').write_text('OPEN DECISIONS (Leif\'s side) - do not order these until settled / 未决事项（Leif 方）：未定前不要下单\n\n'+''.join('- %s / %s\n    %s\n    %s\n' % d_ for d_ in decisions))

    # ---- start here
    steps = [
        ('Read this page (2 minutes).', '先读这一页（2 分钟）。'),
        ('Forward one packet to each of your people: A to a 3D-print shop, B to a servo supplier (both routes), C to the bearing/screw stall, D to LCSC or your component agent, E to a PCB house (quote only), F to the electronics market or your agent for the head parts.', '把各个 Packet 转给对应的人：A 给打印厂，B 给舵机供应商（两条路线都问），C 给轴承螺丝档口，D 给立创或元器件代理，E 给 PCB 厂（仅报价），F 给电子市场或代理（头部件）。'),
        ('Each packet has a paste-ready request in English and Chinese, the files, and a LINES.csv with quantities for 1 / 10 / 100 robots.', '每个 Packet 都有中英文可直接粘贴的询价文字、文件，以及 1 / 10 / 100 台数量的 LINES.csv。'),
        ('Collect answers on "REPLY SHEET - fill in prices.xlsx" (or just reply on WeChat with price, MOQ, lead time, link, photo).', '把回复填在 "REPLY SHEET - fill in prices.xlsx"（或直接微信回复价格、起订量、交期、链接、照片）。'),
        ('Do not buy anything listed in "OPEN DECISIONS" until Leif confirms. Everything marked "OK to buy" in the BOM can be bought for one robot now.', '"OPEN DECISIONS" 里的东西在 Leif 确认前不要买。BOM 里标 "OK to buy" 的可先按一台买。'),
        ('Two contacts we are asking you for: a PCB fab/SMT house that also sources parts, and a PCB engineer who can review the HAT board.', '请帮忙介绍两个联系人：一家能代购元件的 PCB 打样贴片厂，和一位能评审 HAT 板的 PCB 工程师。'),
    ]
    body = ('<h1>Microduck: for suppliers / 给供应商的资料</h1>'
            '<p class="warn">What this is: Leif\'s engineering recreation of the Microduck, a 26 cm two-legged desk robot with 15 servos, camera, distance sensor, speaker, a Radxa computer and a 2S battery. 30 printed plastic parts (26 PLA, 4 TPU), 3 small custom PCBs, and 32 purchased lines. One robot is being built in Shenzhen now; 10 is the next step; 100 is a planning question. Everything here is for quotes and for buying prototype parts, not for production (see LICENCE).</p>'
            '<p class="warn">这是什么：Leif 对 Microduck 的工程复现。26cm 双足桌面机器人，15 个舵机、摄像头、测距传感器、喇叭、Radxa 电脑、2S 电池。30 个打印塑料件（26 PLA，4 TPU）、3 块小定制 PCB、32 项外购件。现在在深圳做 1 台，下一步 10 台，100 台是规划问题。这里的资料用于询价和购买样机零件，不是量产（见 LICENCE）。</p>'
            '<h2>What to do / 怎么做</h2><ol>'+''.join('<li>%s<br><small>%s</small></li>' % (html.escape(a), html.escape(b)) for a, b in steps)+'</ol>'
            '<h2>Files in this folder / 本文件夹</h2><ul>'
            '<li><b>BOM - all purchased parts.xlsx / .csv</b>: %d purchased lines with quantity per robot and for 10 / 100, exact part numbers, what to do now (EN + 中文), specification text, best price we found, open questions. Second sheet: the 30 printed parts.</li>'
            '<li><b>REPLY SHEET - fill in prices.xlsx / .csv</b>: one row per line for your suppliers to fill in.</li>'
            '<li><b>Packet A-F</b>: one folder per supplier type, each self-contained and forwardable.</li>'
            '<li><b>OPEN DECISIONS - do not order these yet.txt</b>: what Leif still has to decide.</li>'
            '<li><b>ALREADY SENT - parts list of 2026-09-08.txt</b>: the list you already have, unchanged.</li>'
            '<li><b>LICENCE</b>: short version and the full sourced position.</li></ul>'
            '<h2>Packets / 资料包</h2><table><tr><th>Packet</th><th>Send to / 转给</th><th>Lines</th></tr>'
            + ''.join('<tr><td>%s<br><small>%s</small></td><td>%s</td><td>%s</td></tr>' % (html.escape(PACKET_NAME[k][0]), PACKET_NAME[k][1], html.escape({'A': '3D print shop / 打印厂', 'B': 'servo supplier, both routes / 舵机供应商', 'C': 'bearing and fastener stall, HQB / 轴承螺丝档口', 'D': 'LCSC or component agent / 立创或代理', 'E': 'PCB fab + SMT house, quote only / PCB 厂', 'F': 'electronics market or agent, head first / 电子市场或代理'}[k]), (('30 printed parts + ' if k == 'A' else '')+', '.join(PACKET[k]))) for k in 'ABCDEF')
            + '</table><h2>Contact and delivery / 联系与收货</h2><p>Leif Rydenfalk, WeChat. Delivery: %s</p><p>%s</p>'
            '<h2>Where the CAD is / CAD 在哪</h2><p>Folder "00 Open in your own software" next to this one: STP with every part, 3MF, STL, per-part files.</p><p><small>Sources: spec/sourcing.json rev %s, out/release/bom.csv, docs/DFM.md, docs/PRODUCTION.md, out/procurement/SOURCING-CN.md, electronics fab packages, LICENCE-POSITION.html. Prices are what we read on vendor pages on the dates recorded in the BOM, not offers.</small></p>') % (len(bom), html.escape(ADDRESS_EN), ADDRESS_CN, src.get('revision', ''))
    (dest/'START HERE - what this is and what we need.html').write_text(page('Microduck: for suppliers', body))
    txt = ['MICRODUCK: FOR SUPPLIERS / 给供应商的资料', '', 'One robot now, 10 next, 100 as a planning question. Quotes and prototype parts, not production (see LICENCE).', '现在 1 台，下一步 10 台，100 台是规划问题。用于询价和样机零件，不是量产（见 LICENCE）。', '', 'WHAT TO DO / 怎么做']
    for i, (a, b) in enumerate(steps, 1): txt += ['%d. %s' % (i, a), '   %s' % b]
    txt += ['', 'Delivery / 收货：'+ADDRESS_CN]
    (dest/'START HERE - what this is and what we need.txt').write_text('\n'.join(txt)+'\n')
    report['files'] = sorted(p.relative_to(dest).as_posix() for p in dest.rglob('*') if p.is_file()); report['printed_parts'] = len(printed); report['drawing_pdfs'] = n_pdf; report['fab_packages'] = n_fab
    (dest/'SUPPLIER PACK REPORT.json').write_text(json.dumps(report, indent=1))
    return report


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--review', type=Path, required=True); ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args(); r = build(a.review, a.out); print(json.dumps({k: v for k, v in r.items() if k != 'files'}, indent=1)); print(len(r['files']), 'files')
