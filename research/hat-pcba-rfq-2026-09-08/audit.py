"""Audit existing public HAT files; generate a quotation appendix, never fab files."""
from pathlib import Path
import collections, csv, hashlib, html, io, json, math, re, sys, urllib.request, zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from extract_hat_pcb import sexp, kids, vals
from audit_official_hat import inspect

REV = '23eab11927f95ceca0dfa35bf182caeb7db39ea0'
REF = ROOT / 'reference/pollen-elec-rpi-robot-hat'
BASE = 'https://raw.githubusercontent.com/pollen-robotics/elec_RPI_Robot_HAT/' + REV + '/'
FILES = ['elec_RPI_Robot_HAT.kicad_pcb', 'elec_RPI_Robot_HAT.kicad_pro',
         'production/ASE01187-C1_elec_RPI_Robot_HAT_BOM.csv',
         'production/ASE01187-C1_elec_RPI_Robot_HAT_POS.csv',
         'production/PCB01186-C1_elec_RPI_Robot_HAT_PCB.zip',
         'production/PCB01186-C1_elec_RPI_Robot_HAT_PCB.pdf', 'PROVENANCE.json']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_csv(path):
    return list(csv.DictReader(path.open(encoding='utf-8-sig', newline='')))


def run():
    manifest = []
    previous = json.loads((HERE/'manifest.json').read_text()) if (HERE/'manifest.json').exists() else {}
    prior = {x['path']:x for x in previous.get('files',[])}
    for rel in FILES:
        p = REF / rel
        if not p.exists():
            continue
        row = {'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size,
               'sha256': sha(p.read_bytes()), 'source_revision': REV,
               'source_url': BASE+rel if rel != 'PROVENANCE.json' else None,
               'basis': 'Existing local archive; source revision from archived PROVENANCE.json'}
        if '--verify-upstream' in sys.argv and rel in (FILES[0],FILES[2],FILES[3],FILES[4]):
            try:
                data = urllib.request.urlopen(BASE+rel, timeout=25).read()
                row['upstream_bytes_match'] = sha(data) == row['sha256']
                row['upstream_checked'] = '2026-09-08'
            except Exception as error:
                row['upstream_bytes_match'] = None
                row['upstream_error'] = str(error)
        old_record = prior.get(row['path'], {})
        if row['sha256'] == old_record.get('sha256') and 'upstream_checked' not in row:
            for key in ('upstream_checked','upstream_bytes_match','upstream_error'):
                if key in old_record: row[key] = old_record[key]
        manifest.append(row)
    pcb_raw = (REF / FILES[0]).read_bytes()
    pcb = pcb_raw.decode()
    assert sha(pcb_raw) == '26c6d77af6a650c8f601edede4389699ca4ebb942763842d60b4c2c5cc1e2cb5'
    nodes = {}
    for match in re.finditer(r'(?m)^\t\(footprint ', pcb):
        fp,_ = sexp(pcb,match.start()+1)
        properties = {vals(p)[0]:vals(p)[1] for p in kids(fp,'property') if len(vals(p))>=2}
        ref = properties['Reference']
        assert ref not in nodes
        nodes[ref] = {'node':fp,'properties':properties,'footprint':vals(fp)[0],
                      'attributes':vals(kids(fp,'attr')[0]) if kids(fp,'attr') else []}
    bom = read_csv(REF/FILES[2]); pos = read_csv(REF/FILES[3]); by_bom={}; qty_errors=[]
    for row in bom:
        refs=[r.strip() for r in row['Designator'].split(',')]
        if int(row['Quantity']) != len(refs):qty_errors.append(row['Designator'])
        for ref in refs:
            assert ref not in by_bom, 'duplicate BOM reference'
            by_bom[ref]=row
    by_pos={r['Designator']:r for r in pos};assert len(by_pos)==len(pos),'duplicate POS reference'
    artwork={ref for ref,fp in nodes.items() if 'Logo_' in fp['footprint'] or fp['footprint'].startswith('Fiducial:')}
    dnp={ref for ref,row in by_bom.items() if row['Value'].startswith('DNP')}
    physical=set(by_pos)-artwork
    fitted_bom=set(by_bom)-dnp-artwork
    comparisons=[]; quote_rows=[]; known_y1=json.loads((ROOT/'ce-parts/microduck-public-hat-y1/docs/SOURCE-FACTS.json').read_text())
    existing=json.loads((ROOT/'out/pcb/hat/components.json').read_text());old={c['refdes']:c for c in existing['components']}
    for ref in sorted(nodes):
        entry=nodes[ref];b=by_bom.get(ref,{});p=by_pos.get(ref,{});prop=entry['properties']
        pcb_lcsc=prop.get('LCSC Part') or '';bom_lcsc=b.get('LCSC Part #') or ''
        item={'designator':ref,'classification':'artwork/fiducial' if ref in artwork else 'DNP' if ref in dnp else 'fitted physical' if ref in physical else 'unresolved',
              'bom_value':b.get('Value'),'pcb_value':prop.get('Value'),'bom_lcsc':bom_lcsc,'pcb_lcsc':pcb_lcsc,
              'pos_present':bool(p),'pcb_footprint':entry['footprint'],'pcb_attributes':entry['attributes']}
        comparisons.append(item)
        if ref not in physical:continue
        quote_rows.append({'designator':ref,'value':b.get('Value','CANNOT DETERMINE'),
            'lcsc_order_code':bom_lcsc or 'CANNOT DETERMINE',
            'lcsc_link':'https://www.lcsc.com/product-detail/'+bom_lcsc+'.html' if bom_lcsc else '',
            'manufacturer_mpn':known_y1['identity']['mpn'] if ref=='Y1' else 'Resolve supplier order code; value field is not a guaranteed full MPN',
            'quantity_1_board':1,'quantity_100_boards':100,'quantity_1000_boards':1000,
            'side':p['Layer'],'pos_x_mm':p['Mid X'],'pos_y_mm':p['Mid Y'],'pos_rotation_deg':p['Rotation'],
            'process_hint':'through-hole/manual assembly review' if 'through_hole' in entry['attributes'] else 'SMT review',
            'status':'RFQ only; no production-unit match or manufacturing release'})
    lcsc_mismatch=[x for x in comparisons if x['bom_lcsc'] and x['bom_lcsc']!=x['pcb_lcsc']]
    old_mismatch=[r for r in nodes if r not in old or old[r]['footprint']!=nodes[r]['footprint'] or old[r]['lcsc']!=(nodes[r]['properties'].get('LCSC Part')) or old[r]['fitted']!=(r in by_pos)]
    stack_node,_=sexp(pcb,pcb.index('(stackup'))
    stack=[]
    for lay in kids(stack_node,'layer'):
        item={'layer':vals(lay)[0]}
        for key in ['type','thickness','material','epsilon_r','loss_tangent']:
            n=kids(lay,key)
            if n:item[key]=float(vals(n[0])[0]) if key in ['thickness','epsilon_r','loss_tangent'] else vals(n[0])[0]
        stack.append(item)
    segments=[];vias=[]
    for m in re.finditer(r'(?m)^\t\((segment|via)\b',pcb):
        node,_=sexp(pcb,m.start()+1)
        if m.group(1)=='segment':segments.append({'layer':vals(kids(node,'layer')[0])[0],'width_mm':float(vals(kids(node,'width')[0])[0])})
        else:vias.append({'drill_mm':float(vals(kids(node,'drill')[0])[0]),'diameter_mm':float(vals(kids(node,'size')[0])[0])})
    members=[];drills={}
    with zipfile.ZipFile(REF/FILES[4]) as archive:
        assert archive.testzip() is None
        for name in archive.namelist():
            raw=archive.read(name);text=raw.decode(errors='replace')
            function=re.search(r'TF.FileFunction,([^*\n]+)',text)
            members.append({'member':name,'bytes':len(raw),'sha256':sha(raw),'file_function':function.group(1) if function else None})
            if not name.endswith('.drl'):continue
            sizes={n:float(d) for n,d in re.findall(r'^T(\d+)C([\d.]+)',text,re.M)};counts=collections.Counter();tool=None
            for line in text.splitlines():
                if re.fullmatch(r'T\d+',line):tool=line[1:]
                elif line.startswith('X') and tool:counts[sizes[tool]]+=1
            drills[name]={'tool_diameters_mm':sizes,'hits_by_diameter_mm':dict(counts),'total_hits':sum(counts.values())}
    report={'document_revision':'MD-HAT-PCBA-RFQ-20260908-A','date':'2026-09-08',
        'status':'REFERENCE AND CONDITIONAL RFQ ONLY; NOT RELEASED FOR FABRICATION',
        'source_revision':REV,'pcb_revision':'C1','pcb_date':'2026-07-08',
        'counts':{'bom_rows':len(bom),'bom_designators':len(by_bom),'pcb_footprints':len(nodes),'pos_rows':len(pos),
                  'dnp_designators':len(dnp),'physical_fitted_components':len(physical),
                  'fitted_with_lcsc_code':sum(bool(by_bom.get(r,{}).get('LCSC Part #')) for r in physical),
                  'physical_sides':dict(collections.Counter(by_pos[r]['Layer'] for r in physical))},
        'consistency':{'bom_row_quantity_errors':qty_errors,'dnp_accidentally_in_pos':sorted(dnp&set(by_pos)),
            'fitted_bom_missing_pos':sorted(fitted_bom-set(by_pos)), 'physical_pos_missing_bom':sorted(physical-set(by_bom)),
            'bom_lcsc_vs_pcb_mismatches':lcsc_mismatch,'existing_extraction_mismatches':old_mismatch,
            'pos_only_artwork':sorted(set(by_pos)-set(by_bom)),'bom_only_artwork':sorted((set(by_bom)-set(by_pos))&artwork)},
        'dnp':[x for x in comparisons if x['designator'] in dnp],
        'missing_order_codes':sorted(r for r in physical if not by_bom.get(r,{}).get('LCSC Part #')),
        'geometry_source':inspect(pcb_raw), 'stackup_source_declaration':stack,
        'stackup_sum_mm':round(sum(r.get('thickness',0) for r in stack),6),
        'surface_finish':{'source_value':vals(kids(stack_node,'copper_finish')[0])[0], 'resolved_process':None,'note':'KiCad None is not an approved surface treatment. Ask factory to propose finish; engineering must decide.'},
        'copper_conflict':{'drawing_note':'35 um (1 oz) copper','stackup_outer_mm':0.07,'stackup_inner_mm':0.035,
                         'verdict':'CANNOT DETERMINE','settles':'Owner selects copper stackup; factory quotes both interpretations separately if needed.'},
        'track_measurement':{'segment_count':len(segments),'minimum_width_by_layer_mm':{layer:min(s['width_mm'] for s in segments if s['layer']==layer) for layer in sorted({s['layer'] for s in segments})},'scope':'track widths only; no measured clearance or current-carrying capacity inferred'},
        'via_measurement':{'count':len(vias),'minimum_drill_mm':min(v['drill_mm'] for v in vias),'minimum_diameter_mm':min(v['diameter_mm'] for v in vias)},
        'gerber_zip_members':members,'drill_files':drills,
        'unresolved':['J4: 40 KiCad hole-clearance errors, 0.0200 mm actual vs 0.2000 mm configured; factory DFM and engineering disposition required', 'Production Microduck specimen/revision identity and head fit', 'Copper-thickness conflict and surface finish', 'TP2/TP3/TP4 manufacturer and order code',
            'DNP R36/R37 carry same C17168 code as fitted zero-ohm links but label DNP-1M: preserve DNP; do not procure/populate from this code without clarification',
            'Y1 recommended solder-land mismatch, exact order-code timing/current guarantee',
            'Supplier resolves complete manufacturer MPN and datasheet for each LCSC code; no silent substitution',
            'Finished thickness/outline/hole tolerances, material grade/Tg, mask and legend colour, panelization and tooling rails',
            'Stencil thickness/apertures, component moisture handling and reflow profile, bottom-side retention and connector assembly process',
            'Inspection class, test coverage/fixtures, test program, programming/calibration, acceptance limits and approved golden sample',
            'Price/currency, MOQ, stock as-of date, NRE, excess component attrition, lead time and shipping destination'],
        'source_files':manifest}
    drc_path=HERE/'official-drc.json'
    if drc_path.exists():
        drc=json.loads(drc_path.read_text());report['drc']={'source_file':'official-drc.json','sha256':sha(drc_path.read_bytes()),'summary':{k:len(v) for k,v in drc.items() if isinstance(v,list)},
            'kicad_version':drc['kicad_version'], 'report_date':drc['date'],
            'severity_counts':dict(collections.Counter(x['severity'] for x in drc['violations'])),
            'type_counts':dict(collections.Counter(x['type'] for x in drc['violations'])),
            'ignored_checks':[x['key'] for x in drc['ignored_checks']],
            'command':'kicad-cli pcb drc --format json --units mm --severity-all --exit-code-violations -o research/hat-pcba-rfq-2026-09-08/official-drc.json reference/pollen-elec-rpi-robot-hat/elec_RPI_Robot_HAT.kicad_pcb',
            'observed_exit_code':5,
            'finding':'40 J4 pad-to-hole clearance errors: 0.0200 mm actual vs 0.2000 mm configured. Eight missing-library warnings (LCSC_parts_lib / Library_Pollen), one SOT-323_SC-70 library mismatch. No waiver or design change made.',
            'scope':'KiCad CLI checks existing fills, no refill/save; no schematic parity or physical test; seven checks ignored by existing configuration'}
    orientation_path=ROOT/'research/hat-orientation-audit-2026-09-08.json'
    orientation=json.loads(orientation_path.read_text())
    report['orientation']={'source_file':str(orientation_path.relative_to(ROOT)), 'sha256':sha(orientation_path.read_bytes()),'verdict':orientation['verdict'],'implication':orientation['implication'],'gpio_anchor_displacement_mm':23.010002}
    report['unresolved'].insert(2,'A 180-degree board rotation preserves four mounts but moves GPIO/anchor patterns 23.010002 mm; lower historical collision volume does not establish fit in the same fixed stack')
    (HERE/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
    with (HERE/'conditional-pcba-quote.csv').open('w',newline='') as fh:
        writer=csv.DictWriter(fh,fieldnames=list(quote_rows[0]));writer.writeheader();writer.writerows(quote_rows)
    (HERE/'manifest.json').write_text(json.dumps({'source_revision':REV,'files':manifest,'gerber_zip_members':members,'archive_reused':True,'no_new_fabrication_archive':True},indent=2)+'\n')
    render(report)
    print(json.dumps({'counts':report['counts'],'consistency':report['consistency'],'track_measurement':report['track_measurement'],'drills':drills,'drc':report.get('drc')},indent=2))


def render(r):
    e=html.escape
    def table(headers,rows):
        return '<table><thead><tr>'+''.join('<th>'+e(str(v))+'</th>' for v in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+e(str(v))+'</td>' for v in row)+'</tr>' for row in rows)+'</tbody></table>'
    content='<p>'+r['document_revision']+' · 2026-09-08</p><h1>Public Robot HAT PCBA quotation appendix<br>公开版 Robot HAT PCBA 询价附录</h1><p class="notice"><b>CONDITIONAL QUOTATION ONLY — NOT RELEASED FOR MANUFACTURE<br>仅供附条件报价 — 未批准制造</b><br>Public C1 source does not establish the installed Microduck revision. This appendix neither orders boards nor authorizes paid work.<br>公开 C1 版本不等于已确认原机同版本。本附录不构成订单，也不授权付费工作。</p>'
    content+='<p>Source '+REV+'; PCB/assembly C1, source date 2026-07-08. Existing source files are reused; hashes identify the bytes to quote. No replacement Gerbers were generated.</p>'
    content+='<h2>Decisions required before release / 放行前须确认</h2><ul>'+''.join('<li>'+e(x)+'</li>' for x in r['unresolved'])+'</ul>'
    content+='<p lang="zh">优先确认：J4有40项孔间隙检查错误（实际0.0200mm，规则0.2000mm），须工厂DFM及工程确认；旋转180°虽保持四安装孔，却使GPIO／定位孔偏移23.010002mm，不能据历史干涉减少判断原位适配；外层铜厚70μm与图纸35μm备注冲突、表面处理、TP2/3/4准确料号、Y1焊盘差异。保持全部9个DNP不装；R36/R37虽然带C17168编号，也不能据此采购或装配。先核对原机版本，再决定是否使用本公开版本。</p>'
    content+='<h2>BOM and placement reconciliation / BOM与贴装核对</h2>'+table(['Measured count','Value'],r['counts'].items())
    content+='<p>POS contains 117 rows, including 3 fiducials and the H3 logo: quote 113 physical components, not 117 placements. The BOM includes H2 artwork and 9 DNP references. TP2/3/4 remain physical components with unspecified purchase codes.<br>POS共117行，含3个基准点和H3标志；实际器件113个。BOM内H2为图案，9个DNP不装。TP2/3/4仍为实体器件，采购料号未确定。</p>'+table(['Check','Result'],[(k,json.dumps(v)) for k,v in r['consistency'].items()])
    content+='<h2>Do not populate / 不装清单</h2>'+table(['Ref','Value','LCSC code (not authority to fit)'],[(x['designator'],x['bom_value'],x['bom_lcsc'] or 'none') for x in r['dnp']])
    content+='<h2>Fabrication facts / 制板资料</h2><p>Outline coordinate span '+str(r['geometry_source']['edge_coordinate_span_xy_mm'])+' mm; declared thickness 1.000000 mm. These are file readings, not tolerances. Four copper layers; stackup below is the source declaration. Surface finish is unresolved (KiCad value: None).<br>外形及厚度为文件值，不是公差；4层铜。下表为源文件叠层声明，表面处理尚未确定。</p>'+table(['Layer','Type','Thickness mm','Material'],[(x['layer'],x.get('type'),x.get('thickness','not stated'),x.get('material','not stated')) for x in r['stackup_source_declaration']])
    content+='<p><b>Conflict:</b> PCB drawing notes 35μm copper; stackup assigns 70μm outer and 35μm inner. Request separate quotes or owner clarification; do not choose silently.</p><p>'+e(json.dumps(r['track_measurement']))+'</p>'+table(['Drill file','Hits by diameter mm'],[(name,json.dumps(row['hits_by_diameter_mm'])) for name,row in r['drill_files'].items()])
    content+='<h2>Assembly files and coordinates / 装配文件与坐标</h2><p>Use the pinned original POS values and layer names. Do not mirror the bottom-side coordinates or rotate parts automatically; supplier CAM must document its convention and provide polarity/orientation review. Existing extraction reports 4 connector-centroid offsets; this is not a blanket origin error. Quote SMT and through-hole/manual assembly separately.</p><p lang="zh">使用固定版本POS原始坐标及面别。不要自动镜像底面或旋转器件；请工厂说明CAM坐标约定，并提供极性／方向复核。既有提取记录有4个连接器中心偏移，不能当成整板原点错误。SMT与通孔／手工装配分别报价。</p>'
    content+='<h2>Verification limits / 验证范围</h2><pre>'+e(json.dumps(r['orientation'],indent=2))+'</pre><pre>'+e(json.dumps(r.get('drc',{}),indent=2))+'</pre><p>Empty mismatch lists establish source-file consistency only. They do not establish current stock, electrical safety, solderability, DRC acceptance or compatibility with a production robot.</p>'
    content+='<h2>Quotation return / 报价回复</h2><p>Quote 1 prototype PCBA, 100 PCBAs and 1,000 PCBAs separately. Use conditional-pcba-quote.csv for quantities; 9 DNP references are excluded. For each LCSC code return manufacturer, complete MPN, datasheet, package, stock/date, MOQ, unit price/currency and lead time. Separate PCB, SMT/THT, stencil/panel/tooling, testing/fixture, NRE, attrition, packaging, freight and taxes. State all substitutions and missing decisions. Do not begin production.</p><p lang="zh">分别报价1块样板、100块、1,000块PCBA，按附表数量核价，排除9个DNP。每个LCSC编号请返回厂家、完整料号、数据手册、封装、库存／日期、MOQ、单价／币种及交期。PCB、SMT／通孔装配、钢网／拼板／工装、测试／夹具、工程费、损耗、包装、运费及税费分列。替代项和待决事项明确列出，暂不启动生产。</p>'
    content+='<h2>Source manifest / 源文件清单</h2>'+table(['Existing repository path','SHA-256','Pinned remote checked'],[(x['path'],x['sha256'],x.get('upstream_bytes_match','not rechecked')) for x in r['source_files']])
    content+='<h2>Existing fabrication ZIP contents / 既有制板压缩包内容</h2>'+table(['Member','Function','SHA-256'],[(x['member'],x['file_function'],x['sha256']) for x in r['gerber_zip_members']])
    css=(ROOT/'tools/doc.css').read_text()
    (HERE/'APPENDIX.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Robot HAT PCBA RFQ</title><style>'+css+' body{max-width:1100px;margin:30px auto;padding:24px}table{width:100%;border-collapse:collapse}td,th{border-bottom:1px solid #ddd;padding:8px;text-align:left;overflow-wrap:anywhere}td{font-size:13px}h2{margin-top:32px}pre{white-space:pre-wrap}.notice{padding:18px;border:2px solid #a44220;background:#fff7f0}</style><body>'+content+'</body></html>')


if __name__=='__main__':
    run()
