"""Offline engineering review packages. Existing artifacts only; no manufacture verdict.

python3 -m cecad.reviewpack --project ROOT --mesh ASSEMBLY.json --out NEW_DIR
Copies all available geometry and an explicit engineering snapshot, inventories
omissions, and verifies bytes after archive extraction. Never sends or deploys.
"""
from pathlib import Path
import argparse, base64, csv, hashlib, html, io, json, re, shutil, struct, zipfile
from collections import Counter
from datetime import datetime, timezone

GEOMETRY={'.stl','.step','.stp','.brep','.obj','.3mf','.glb','.gltf','.iges','.igs','.dxf'}
TEXT={'.md','.json','.csv','.txt','.py','.cpp','.c','.h','.hpp','.toml','.yaml','.yml','.xml','.svg','.html','.css','.js','.mjs','.sh','.pdf','.ino','.kicad_pcb','.kicad_sch','.kicad_pro','.kicad_mod','.kicad_sym','.gbr','.drl','.pos','.sch','.pcb','.urdf','.sdf','.srdf','.onnx','.pt','.pth','.npz','.npz','.bin'}
CSS='''*{box-sizing:border-box}body{font:17px/1.6 system-ui;color:#163447;background:#f0f4f5;margin:0}main{max-width:1050px;margin:auto;padding:36px}h1{font-size:38px;line-height:1.2}h2{font-size:24px}a{color:#075b80}section,.card{background:white;border:1px solid #d2e0e5;border-radius:12px;padding:24px;margin:18px 0}small{color:#506874}img{max-width:100%;max-height:360px;object-fit:contain}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:10px;text-align:left;border-bottom:1px solid #d2e0e5;overflow-wrap:anywhere}input{padding:12px;width:100%;font:inherit}.tag{display:inline-block;padding:4px 12px;background:#fff1cf;border-radius:6px}nav a{display:inline-block;margin-right:15px}@media print{body{background:white}main{padding:0}section,.card{break-inside:avoid}a{color:inherit}input,nav{display:none}h1{font-size:28px}.grid{display:block}}'''
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def page(title,body): return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+'</title><style>'+CSS+'</style><main>'+body+'</main></html>'
def csvwrite(path,rows):
    if not rows:return
    with path.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def stl_mesh(path):
    data=path.read_bytes();v=[]
    if len(data)>=84 and len(data)==84+50*struct.unpack_from('<I',data,80)[0]:
        for row in struct.iter_unpack('<12fH',data[84:]):v.extend(row[3:12])
    else:
        for match in re.finditer(rb'\bvertex\s+([-+\deE.]+)\s+([-+\deE.]+)\s+([-+\deE.]+)',data):v.extend(float(x) for x in match.groups())
    if not v or len(v)%9:raise ValueError('Invalid/empty triangle STL: '+str(path))
    import math
    if not all(math.isfinite(x) for x in v):raise ValueError('Nonfinite STL: '+str(path))
    return {'name':path.stem,'positions':v,'color':[.42,.66,.79]}
def write_mesh_stl(model,path):
    """Export a published triangle snapshot exactly; never infer a CAD solid."""
    triangles=sum(len(p['indices'])//3 for p in model['parts'])
    with path.open('wb') as f:
        f.write(b'Published assembled review mesh; mm; not a single printable part'.ljust(80,b' '))
        f.write(struct.pack('<I',triangles))
        for p in model['parts']:
            for i in range(0,len(p['indices']),3):
                v=[p['positions'][3*j+k] for j in p['indices'][i:i+3] for k in range(3)]
                f.write(struct.pack('<12fH',0.,0.,0.,*v,0))
    if path.stat().st_size!=84+50*triangles:raise ValueError('STL export length mismatch')
    return {'triangles':triangles,'sha256':sha(path),'scope':'Exact published mesh triangulation in mm; assembled viewing only, not printing or editable solid CAD'}

def viewer(out,model,title,scope,back):
    template=(Path(__file__).resolve().parents[1]/'web/review-viewer.html').read_text()
    for a,b in {'__TITLE__':html.escape(title),'__SCOPE__':html.escape(scope),'__BACK__':back,'__GEOMETRY__':json.dumps(model,separators=(',',':')).replace('</','<\\/')}.items():template=template.replace(a,b)
    out.write_text(template)

def build(project,mesh,out):
    project=project.resolve();out=out.resolve()
    if out.exists():raise ValueError('Choose a new release directory; existing releases are immutable')
    out.mkdir(parents=True)
    folders=['01 See the robot','02 Look at the parts','03 How it fits together','04 Electronics and wires','05 Shopping list','06 Questions to resolve','07 Files for the engineer']
    for folder in folders:(out/folder).mkdir()
    source_root=out/folders[-1]/'Project files';source_root.mkdir()
    copied={};omitted=[];rows=[]
    def copy(p,rel):
        q=out/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
        record={'file':q.relative_to(out).as_posix(),'source':p.relative_to(project).as_posix() if p.is_relative_to(project) else p.name,'bytes':q.stat().st_size,'sha256':sha(q)}
        rows.append(record);return q
    files=sorted(p for p in project.rglob('*') if p.is_file())
    for p in files:
        rel=p.relative_to(project);parts=rel.parts;ext=p.suffix.lower();reason=None
        if any(x in ('.git','__pycache__','node_modules','.venv','trash') for x in parts):reason='Development cache/history; not engineering deliverable'
        elif p.is_symlink():reason='Symlink alias; target inventoried separately'
        elif any(x.startswith('.') for x in parts) and p.name not in ('.gitignore',):reason='Hidden local configuration excluded'
        elif any(x in rel.as_posix().lower() for x in ('ming-handoff','ming-parts','ming-relationship','relationship-management','wechat-transcript','review-release','networking','shenzhen-outreach','contact-route','supplier-contact')):reason='Private correspondence or earlier delivery package excluded'
        elif ext in GEOMETRY:reason=None
        elif parts[0] in ('ce-parts','ce-connections','ce-assemblies','electronics','firmware','software','wiring','spec','docs','tools','sim','reference','workflows') and (ext in TEXT or p.name.lower().startswith(('license','licence','copying','readme'))):reason=None
        elif parts[0]=='research' and ext in TEXT:reason=None
        elif parts[0]=='out' and (ext in TEXT or (len(parts)>1 and parts[1] in ('assembly','drawings','render','internals','wiring','ref','sim') and ext in ('.png','.jpg','.gif','.mp4'))):reason=None
        elif len(parts)==1 and ext in TEXT:reason=None
        elif parts[0]=='images' and ext in ('.jpg','.jpeg','.png','.md','.json'):reason=None
        else:reason='Redundant screenshots, temporary logs or simulation frame dump; not a design source'
        if reason:
            omitted.append({'source':rel.as_posix(),'bytes':p.stat().st_size,'reason':reason});continue
        # No links leave the snapshot; repository-relative source paths preserved.
        q=copy(p,(source_root.relative_to(out)/rel).as_posix())
        copied[rel.as_posix()]=q.relative_to(out).as_posix()
    manifest=json.loads((project/'out/print/stl_manifest.json').read_text())
    parts=[]
    for number,(slug,item) in enumerate(sorted(manifest.items()),1):
        name=slug.removeprefix('microduck-').replace('-',' ').title();folder=out/folders[1]/f'{number:02d} {name}';folder.mkdir()
        p=project/item['stl'];record={'number':number,'part':name,'slug':slug,'quantity':item.get('qty'),'source_kind':item.get('stl_source'),'source_path':item['stl'],'stl':None,'drawing_files':0}
        if p.exists():
            q=copy(p,(folder.relative_to(out)/(name+'.stl')).as_posix());m=stl_mesh(q)
            record['stl']=q.relative_to(out).as_posix();record['triangles']=len(m['positions'])//9
            record['measured_bbox_mm']=[max(m['positions'][i::3])-min(m['positions'][i::3]) for i in range(3)]
            expected=item.get('bbox_mm');record['manifest_bounds_match']=expected is not None and all(round(a,1)==round(b,1) for a,b in zip(record['measured_bbox_mm'],expected))
            viewer(folder/'Look at this part.html',{'parts':[m],'units':item.get('units','unknown')},name,'Source: '+str(item.get('stl_source'))+'. Review geometry; not manufacturing approval.','../../START HERE.html')
        else:record['missing']='Manifest STL is missing on disk'
        for d in sorted((project/'out/drawings'/slug).glob('*')):
            if d.suffix.lower() in ('.pdf','.svg','.dxf','.step','.stl','.json','.png'):
                copy(d,(folder.relative_to(out)/'Drawings and details'/d.name).as_posix());record['drawing_files']+=1
        (folder/'READ ME.txt').write_text(f'{name}\n零件 {number} / Part {number}\nQuantity in source list / 清单数量: {item.get("qty", "unknown")}\nOrigin: {item.get("stl_source")}\nThe file is for review. See Questions to resolve before manufacturing. / 仅供评审，生产前请查看待确认事项。\nThe full historical/reference geometry is in 07 Files for the engineer.\n')
        parts.append(record)
    robot=json.loads(mesh.read_text());write_mesh_stl(robot,out/folders[0]/'Whole robot - view only.stl');copy(mesh,folders[0]+'/Published assembly mesh.json');viewer(out/folders[0]/'Turn the robot around.html',robot,'Microduck — look inside / 查看内部','Published reconstruction snapshot, '+str(len(robot['parts']))+' placed pieces. Not original editable manufacturer CAD. Historical fastener and interface limitations remain open.','../START HERE.html')
    for p in sorted((project/'out/assembly').glob('*.png')):copy(p,folders[2]+'/'+p.name)
    for stem in ('duck-now_iso.png','duck-now_front.png','duck-now_left.png','assembly-now.png'):
        p=project/'out/render'/stem
        if p.exists():copy(p,folders[0]+'/'+stem)
    for p in (project/'out/sim').glob('*.mp4'):
        if p.name in ('walk.mp4','stand.mp4','sitstand.mp4'):copy(p,folders[0]+'/Recorded simulation - '+p.name)
    for name in ('RELEASE.html','BUILD-BOOK.html','INTERNALS.html'):
        # Use intact source copy; do not flatten documents and break relative links.
        pass
    def links(prefix):return ''.join(f'<li><a href="../{html.escape(dest)}">{html.escape(src)}</a></li>' for src,dest in copied.items() if any(src.startswith(x) for x in prefix))
    (out/folders[3]/'START HERE.html').write_text(page('Electronics and wires','<a href="../START HERE.html">← Back / 返回</a><h1>Electronics and wires / 电子与接线</h1><p>Boards, schematics, component lists and wiring files. PCB reports include unresolved failures; do not fabricate from a failed report. / 包含板图、原理图、物料清单及接线资料；请先审查未解决问题。</p><ul>'+links(('electronics/','wiring/'))+'</ul>'))
    (out/folders[4]/'START HERE.html').write_text(page('Shopping list','<a href="../START HERE.html">← Back / 返回</a><h1>Shopping list / 采购清单</h1><p>Check exact model, quantity and availability with an engineer. Recorded prices are historical observations. / 请由工程师确认型号、数量及供货情况，历史价格仅供参考。</p><ul>'+links(('out/release/','out/procurement/','spec/sourcing','docs/BOM','docs/PARTS'))+'</ul>'))
    questions=[('Which physical robot are we matching?','需要比对哪一台原机？','Original fitted board and servo revisions are not fully established.'),('Do the parts fit and move together?','零件是否可以正确装配和运动？','The reconstruction has unresolved servo interfaces and withdrawn screw proposals. The 70-piece view is not proof that every fastener or cable is represented.'),('Can the electronics be built safely?','电子部分是否可以正确制作？','PCB design-rule failures and servo supply compatibility remain open. Use the included reports for engineering review.'),('What is needed before making parts?','加工前还需要什么？','Confirm drawings, materials, tolerances, current geometry and the original-unit comparison with the responsible engineer.')]
    (out/folders[5]/'START HERE.html').write_text(page('Questions to resolve','<a href="../START HERE.html">← Back / 返回</a><h1>Questions to resolve / 待确认事项</h1>'+''.join(f'<section><h2>{a}<br>{b}</h2><p>{c}</p></section>' for a,b,c in questions)+'<a href="../'+copied['docs/RECREATION-2026-09-08.md']+'">Detailed current engineering findings / 工程问题详情</a>'))
    partcards=''
    for r in parts:
        folder=f'{r["number"]:02d} {r["part"]}'
        href=f'{folders[1]}/{folder}/Look at this part.html'
        partcards+=f'<article class="card"><h2>{r["number"]:02d} · {html.escape(r["part"])}</h2><p>Quantity / 数量: {r["quantity"]}</p><small>{html.escape(str(r["source_kind"]))}</small><p><a href="{html.escape(href)}">Turn this part around / 旋转查看</a></p><a href="{html.escape(r["stl"] or "#")}">STL file / STL文件</a></article>'
    (out/'PARTS.html').write_text(page('All parts','<a href="START HERE.html">← Start here / 返回</a><h1>Look at each part / 查看每个零件</h1><p>These are the named files from the project’s print-source list. All other STL/CAD variants are also included in the engineer folder and indexed below. / 此处按零件列出打印来源文件，其他STL及CAD版本另收录于工程师文件夹。</p><input aria-label="Search parts" placeholder="Find a part / 搜索零件" oninput="document.querySelectorAll(\'.card\').forEach(x=>x.hidden=!x.textContent.toLowerCase().includes(this.value.toLowerCase()))"><div class="grid">'+partcards+'</div>'))
    counts=Counter(Path(r['file']).suffix.lower() for r in rows);nav=[('See the robot / 看整机',folders[0]+'/Turn the robot around.html','Rotate it, remove the covers and choose individual pieces. / 旋转整机、隐藏外壳、选择零件。'),('Look at each part / 看零件','PARTS.html','One named folder per part, with STL, a 3D preview and available drawings. / 每个零件一个文件夹。'),('How it fits together / 看装配',folders[2]+'/START HERE.html','Pictures explain the assembly stages. / 按图片查看装配阶段。'),('Electronics and wires / 看电子接线',folders[3]+'/START HERE.html','Schematics, PCB files and wiring records. / 原理图、PCB与接线资料。'),('Shopping list / 看采购清单',folders[4]+'/START HERE.html','Bought components and quantities. / 外购件与数量。'),('Questions to resolve / 看待确认事项',folders[5]+'/START HERE.html','What the engineer must confirm before manufacturing. / 生产前由工程师确认。'),('All engineering files / 全部工程文件','ALL FILES.html','Search every included file and see the source of each. / 搜索文件并查看来源。')]
    photo='01 See the robot/duck-now_iso.png'
    body='<h1>Microduck<br><small>Review the robot / 机器人评审</small></h1><span class="tag">ENGINEERING REVIEW · 工程评审</span><p>Start with the robot, then open any part you want to examine. / 请先看整机，再选择要查看的零件。</p><p>Extract this folder once, then open START HERE.html in Chrome or Edge. No account, installation, server or internet connection is needed. On a phone, begin with START HERE.pdf. / 解压后用浏览器打开，无需安装或联网；手机请先查看PDF。</p><img src="'+photo+'" alt="Published reconstructed Microduck model"><div class="grid">'+''.join(f'<section><h2><a href="{u}">{a}</a></h2><p>{b}</p></section>' for a,u,b in nav)+'</div><section><h2>What these files represent / 文件说明</h2><p>The main part list contains '+str(len(parts))+' named parts. The published assembled view contains '+str(len(robot['parts']))+' placed pieces. The package preserves available reference meshes, reconstructed parts and historical CAD variants, identified by their original paths. It is not a complete original manufacturer CAD release or approval to manufacture.</p><p>主清单按零件整理；整机视图是已发布的重建模型。参考网格、重建零件及历史版本分别标明来源。本包不是原厂完整CAD，也不代表已批准生产。</p><p>Editable whole-robot STEP availability: '+('present' if any('microduck.step' in x for x in copied) else 'not established; no synthetic STEP substituted')+'. Missing/withdrawn details are listed in Questions to resolve.</p></section>'
    (out/'START HERE.html').write_text(page('Microduck review',body))
    (out/folders[2]/'START HERE.html').write_text(page('How it fits together','<a href="../START HERE.html">← Back / 返回</a><h1>How it fits together / 装配过程</h1><p>Published assembly illustrations, not a verified factory build instruction. / 已发布的装配示意，尚非经实物验证的工厂作业指导书。</p>'+''.join(f'<section><h2>{html.escape(p.stem)}</h2><img src="{p.name}" alt="Assembly stage {p.stem}"></section>' for p in sorted((out/folders[2]).glob('*.png')))))
    table=''.join('<tr><td><a href="'+html.escape(r['file'])+'">'+html.escape(r['file'])+'</a></td><td>'+str(r['bytes'])+'</td><td>'+html.escape(r['source'])+'</td></tr>' for r in rows)
    (out/'ALL FILES.html').write_text(page('All files','<a href="START HERE.html">← Start here / 返回</a><h1>All included files / 全部文件</h1><p>Source paths distinguish original references, reconstructions and historical studies. / 原路径用于区分参考、重建及历史研究。</p><input aria-label="Search files" placeholder="Type STL, STEP, a part name… / 输入文件名" oninput="document.querySelectorAll(\'tbody tr\').forEach(x=>x.hidden=!x.textContent.toLowerCase().includes(this.value.toLowerCase()))"><table><thead><tr><th>File / 文件</th><th>Bytes</th><th>Original source / 来源</th></tr></thead><tbody>'+table+'</tbody></table>'))
    (out/'README.txt').write_text('MICRODUCK — ENGINEERING REVIEW / 工程评审\n\n1. Extract the complete folder. / 解压整个文件夹。\n2. Open START HERE.html in a browser, or START HERE.pdf on a phone.\n3. Use PARTS.html for named STL files. Use ALL FILES.html for every engineering file.\n\nNot manufacturing approval. Original-reference and reconstructed files are labelled separately. No passwords or internet needed for the main review pages. Historical engineering HTML may refer to external sources; the included source snapshot preserves relative paths wherever available.\n')
    csvwrite(out/'PARTS.csv',[{k:(json.dumps(v) if isinstance(v,list) else v) for k,v in r.items()} for r in parts])
    csvwrite(out/'SOURCE FILES.csv',rows);csvwrite(out/'OMITTED FILES.csv',omitted)
    missing=[r for r in parts if not r['stl']];bounds=[r['part'] for r in parts if r.get('manifest_bounds_match') is False]
    allgeom=[p.relative_to(project).as_posix() for p in files if p.suffix.lower() in GEOMETRY and not any(x in p.parts for x in ('.git','trash')) and 'review-release' not in str(p)]
    missinggeom=[p for p in allgeom if p not in copied and not any(x['source']==p and 'Private correspondence' in x['reason'] for x in omitted)]
    report={'purpose':'engineering review, not manufacturing release','created':datetime.now(timezone.utc).isoformat(),'project':str(project),'mesh_source':str(mesh),'mesh_sha256':sha(mesh),'assembled_pieces':len(robot['parts']),'part_count':len(parts),'source_file_count':len(rows),'extensions':dict(counts),'missing_primary_stls':missing,'manifest_bounds_mismatches':bounds,'geometry_not_copied':missinggeom,'omitted_count':len(omitted),'sent':False}
    (out/'PACKAGE REPORT.json').write_text(json.dumps(report,indent=2))
    return report

def verify_manifest(out):
    checked=0
    for row in csv.DictReader(io.StringIO((out/'MANIFEST.csv').read_text(encoding='utf-8-sig'))):
        p=(out/row['file']).resolve()
        if not p.is_relative_to(out.resolve()):raise ValueError('Manifest escapes package')
        if not p.is_file() or sha(p)!=row['sha256'] or p.stat().st_size!=int(row['bytes']):raise ValueError('Missing or changed file: '+row['file'])
        checked+=1
    return checked

def refresh_index(out):
    sources={r['file']:r['source'] for r in csv.DictReader((out/'SOURCE FILES.csv').open(encoding='utf-8-sig'))}
    rows=[{'file':p.relative_to(out).as_posix(),'source':sources.get(p.relative_to(out).as_posix(),'Generated review artifact'),'bytes':p.stat().st_size} for p in sorted(out.rglob('*')) if p.is_file() and p.name!='MANIFEST.csv']
    body='<a href="START HERE.html">← Start here / 返回</a><h1>All included files / 全部文件</h1><p>Current parts are in folder02. Folder07 preserves technical sources and historical variants. / 当前零件见02文件夹，技术来源及历史版本见07。</p><input aria-label="Search files" placeholder="Find STL, STEP or a part / 搜索" oninput="document.querySelectorAll(\'tbody tr\').forEach(x=>x.hidden=!x.textContent.toLowerCase().includes(this.value.toLowerCase()))"><table><thead><tr><th>File / 文件</th><th>Bytes</th><th>Source / 来源</th></tr></thead><tbody>'
    body+=''.join('<tr><td><a href="'+html.escape(r['file'])+'">'+html.escape(r['file'])+'</a></td><td>'+str(r['bytes'])+'</td><td>'+html.escape(r['source'])+'</td></tr>' for r in rows)
    (out/'ALL FILES.html').write_text(page('All files',body+'</tbody></table>'))
    report=json.loads((out/'PACKAGE REPORT.json').read_text());report['included_file_count_before_manifest']=len(rows);report['final_extensions']=dict(Counter(Path(r['file']).suffix.lower() for r in rows));(out/'PACKAGE REPORT.json').write_text(json.dumps(report,indent=2))

def seal(out):
    out=out.resolve();refresh_index(out);files=sorted(p for p in out.rglob('*') if p.is_file() and p.name!='MANIFEST.csv')
    rows=[{'file':p.relative_to(out).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files];csvwrite(out/'MANIFEST.csv',rows)
    archive=out.with_suffix('.zip')
    if archive.exists():raise ValueError('Archive already exists; use new release name')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=1,allowZip64=True) as z:
        for p in sorted(out.rglob('*')):
            if p.is_file():z.write(p,out.name+'/'+p.relative_to(out).as_posix())
    with zipfile.ZipFile(archive) as z:
        bad=z.testzip()
        if bad:raise ValueError('Archive CRC failure: '+bad)
        for row in rows:
            if hashlib.sha256(z.read(out.name+'/'+row['file'])).hexdigest()!=row['sha256']:raise ValueError('Archive hash mismatch: '+row['file'])
    return {'archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'verified_files':len(rows)+1,'crc':'PASS','sha256_readback':'PASS'}
def illustrate(out,project):
    """Make the first document the complete visual review, using measured previews."""
    def img(p,alt):
        if not p.exists():raise ValueError('Missing review picture: '+str(p))
        return '<img src="data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode()+'" alt="'+html.escape(alt)+'">'
    start=out/'START HERE.html';text=start.read_text()
    # All pictures embedded: the first HTML is also readable when copied alone.
    text=re.sub(r'<img src="01 See the robot/duck-now_iso.png"[^>]*>',img(out/'01 See the robot/Whole robot.png','Whole reconstructed robot'),text)
    gallery='<section><h2>See the actual model / 查看实际模型</h2><p>Rotate the model with one click, or review these pictures directly. / 点击进入3D，也可直接查看下列图片。</p><div class="grid">'
    for name,label in [('Whole robot.png','Whole robot / 整机'),('Inside the robot.png','Covers removed / 隐藏外壳'),('Separated pieces.png','Pieces separated for viewing / 分开查看零件')]:
        gallery+='<article><h3>'+label+'</h3>'+img(out/'01 See the robot'/name,label)+'</article>'
    gallery+='</div><a href="01 See the robot/Turn the robot around.html">Open interactive 3D / 打开交互式3D</a></section><section><h2>Every named print-list part / 打印清单零件总览</h2><p>Click a picture to turn the actual STL around. Source labels distinguish reference meshes from reconstructed parts. / 点击图片旋转查看STL，来源标签区分参考网格和重建零件。</p><div class="grid">'
    records=list(csv.DictReader((out/'PARTS.csv').open(encoding='utf-8-sig')))
    for r in records:
        folder=out/'02 Look at the parts'/f'{int(r["number"]):02d} {r["part"]}';href=folder.relative_to(out).as_posix()
        gallery+='<article class="card"><h3>'+r['number']+' · '+html.escape(r['part'])+'</h3><a href="'+href+'/Look at this part.html">'+img(folder/'Part picture.png',r['part'])+'</a><p>Quantity / 数量: '+r['quantity']+'</p><small>'+html.escape(r['source_kind'])+'</small><p><a href="'+html.escape(r['stl'])+'">STL</a> · <a href="'+href+'/Look at this part.html">3D view / 查看3D</a></p></article>'
    gallery+='</div></section><section><h2>Assembly pictures / 装配示意图</h2><p>Published reconstruction sequence; physical assembly is not yet verified. / 重建模型装配顺序，尚未经实物验证。</p><div class="grid">'
    for p in sorted((out/'03 How it fits together').glob('*.png')):gallery+='<article><h3>'+p.stem+'</h3>'+img(p,p.stem)+'</article>'
    gallery+='</div></section>'
    oldpath=project/'research/ming-parts-request-2026-09-08/SOURCE-LIST.csv'
    old=list(csv.DictReader(oldpath.open()));current=json.loads((project/'spec/sourcing.json').read_text())['lines'];lookup={r['id']:r for r in current};changes=[]
    fields=[('item','item'),('recorded_qty_per_robot','qty_per_robot'),('identity_status','mpn_status'),('recorded_mpn','mpn')]
    for r in old:
        n=lookup.get(r['id'])
        if n is None:changes.append({'id':r['id'],'field':'line','sent':r['item'],'current':'REMOVED'});continue
        for a,b in fields:
            before=str(r[a] or '');after=str(n.get(b) if n.get(b) is not None else '')
            if before!=after:changes.append({'id':r['id'],'field':a,'sent':before,'current':after})
    for n in current:
        if n['id'] not in {r['id'] for r in old}:changes.append({'id':n['id'],'field':'line','sent':'NOT LISTED','current':n['item']})
    shop=out/'05 Shopping list';shutil.copyfile(oldpath,shop/'Original list already sent.csv');csvwrite(shop/'Changes since original list.csv',changes)
    currentrows=[{'id':r['id'],'item':r['item'],'quantity':r.get('qty_per_robot'),'exact_part':r.get('mpn'),'identity_status':r.get('mpn_status')} for r in current];csvwrite(shop/'Current parts to review.csv',currentrows)
    summary={'original_count':len(old),'current_count':len(current),'quantity_changes':[r for r in changes if r['field']=='recorded_qty_per_robot'],'changed_ids':sorted({r['id'] for r in changes}),'changes':changes,'original_sha256':sha(oldpath),'current_source_sha256':sha(project/'spec/sourcing.json')};(shop/'Comparison evidence.json').write_text(json.dumps(summary,indent=2))
    gallery+='<section><h2>Purchased parts: what changed? / 外购件清单有何变化？</h2><p>The same32 purchased-part lines remain, with no quantity changes. Three descriptions are clarified: battery/charger kit, unconfirmed ToF module, and unconfirmed speaker specification. The STL list is additional; it does not replace this shopping list.</p><p>仍为32项外购件，数量未更改。仅补充电池与充电器套件、待确认的ToF模块及喇叭规格。STL零件清单为新增部分，不替代采购清单。</p><a href="05 Shopping list/Original list already sent.csv">Original list / 原清单</a> · <a href="05 Shopping list/Changes since original list.csv">Exact changes / 具体变更</a><table><tr><th>ID</th><th>Part / 零件</th><th>Qty / 数量</th><th>Identity / 型号确认</th></tr>'
    for r in currentrows:gallery+='<tr>'+''.join('<td>'+html.escape(str(r[k] if r[k] is not None else 'Needs confirmation / 待确认'))+'</td>' for k in ('id','item','quantity','identity_status'))+'</tr>'
    gallery+='</table></section>'
    text=text.replace('</main>',gallery+'</main>');start.write_text(text)
    # The gallery page also gains the exact-STL pictures, not generic CAD icons.
    parts=out/'PARTS.html';parttext=parts.read_text()
    for r in records:
        folder=out/'02 Look at the parts'/f'{int(r["number"]):02d} {r["part"]}'
        needle=f'<h2>{int(r["number"]):02d} · {html.escape(r["part"])}</h2>'
        parttext=parttext.replace(needle,needle+img(folder/'Part picture.png',r['part']))
    parts.write_text(parttext)
    report=json.loads((out/'PACKAGE REPORT.json').read_text());report['first_document_embedded_images']=text.count('<img ');report['purchased_list_comparison']=summary
    report['windows_path_check']={'maximum_relative_file_path':max(len(out.name+'/'+p.relative_to(out).as_posix()) for p in out.rglob('*') if p.is_file()),'instruction':'Extract All to a short folder, e.g. C:\\Microduck. Windows execution has not been tested on a Windows host.'}
    (out/'PACKAGE REPORT.json').write_text(json.dumps(report,indent=2));return {'images':report['first_document_embedded_images'],'comparison':summary,'windows':report['windows_path_check']}

def add_bought_model_parts(out,catalog,mesh):
    model=json.loads(mesh.read_text());entry=next(x for x in json.loads(catalog.read_text())['models'] if x['id']==model['id'])
    records=list(csv.DictReader(io.StringIO((out/'PARTS.csv').read_text(encoding='utf-8-sig'))));known={r['slug'] for r in records};extra=[]
    for component in entry['components']:
        slug=component['part']
        if slug in known:continue
        known.add(slug);name=slug.removeprefix('microduck-').replace('-',' ').title();number=len(records)+1
        folder=out/'02 Look at the parts'/f'{number:02d} {name}';folder.mkdir()
        part=next(p for p in model['parts'] if p['name']==component['label']);m={'parts':[part],'units':'mm'}
        dst=folder/(name+' - model representation.stl');write_mesh_stl(m,dst)
        viewer(folder/'Look at this part.html',m,name,'Bought-component shape in the published assembly. May be simplified; does not establish the fitted manufacturer or part number.','../../START HERE.html')
        (folder/'READ ME.txt').write_text('Purchased component / 外购件\nThis is its placed shape in the published model, not a printable replacement. Some bought components are simplified envelopes and original identity remains unconfirmed. / 这是整机模型中的零件外形，不是可打印的替代件，部分为简化外形，原件型号仍需确认。\n')
        record={k:'' for k in records[0]};record.update(number=number,part=name,slug=slug,quantity=sum(c['part']==slug for c in entry['components']),source_kind='Bought component model / 外购件模型',source_path=component['label'],stl=dst.relative_to(out).as_posix(),triangles=len(part['indices'])//3)
        records.append(record);extra.append(record)
    csvwrite(out/'PARTS.csv',records);(out/'BOUGHT MODEL PARTS.json').write_text(json.dumps(extra,indent=2));return extra

def illustrate_bought(out):
    extra=json.loads((out/'BOUGHT MODEL PARTS.json').read_text());cards=''
    for r in extra:
        folder=out/'02 Look at the parts'/f'{r["number"]:02d} {r["part"]}';src='data:image/png;base64,'+base64.b64encode((folder/'Part picture.png').read_bytes()).decode();rel=folder.relative_to(out).as_posix()
        cards+='<article class="card"><h3>'+str(r['number'])+' · '+html.escape(r['part'])+'</h3><a href="'+rel+'/Look at this part.html"><img src="'+src+'" alt="'+html.escape(r['part'])+'"></a><p>Shown in model / 模型数量: '+str(r['quantity'])+'</p><small>Bought-component representation / 外购件外形，不是打印替代件</small><p><a href="'+rel+'/Look at this part.html">3D view / 查看3D</a> · <a href="'+r['stl']+'">STL representation / 模型STL</a></p></article>'
    section='<section><h2>Bought parts shown in the robot / 整机中的外购件</h2><p>These eight shapes complete the38 distinct components in the published70-piece model. Some are simplified envelopes. The shopping list has32 different procurement lines, including things not represented as separate geometry.</p><p>这8种外形补全已发布整机模型的38种零件，部分为简化外形。采购清单仍为32项，包含没有单独几何模型的物料。</p><div class="grid">'+cards+'</div></section>'
    for name in ('START HERE.html','PARTS.html'):
        p=out/name;p.write_text(p.read_text().replace('</main>',section+'</main>'))
    p=out/'PACKAGE REPORT.json';d=json.loads(p.read_text());d['modeled_distinct_parts']=38;d['first_document_embedded_images']=(out/'START HERE.html').read_text().count('<img ');p.write_text(json.dumps(d,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--project',type=Path);ap.add_argument('--mesh',type=Path);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--seal',action='store_true');ap.add_argument('--illustrate',action='store_true');args=ap.parse_args()
    print(json.dumps(seal(args.out) if args.seal else illustrate(args.out,args.project) if args.illustrate else build(args.project,args.mesh,args.out),indent=2))
