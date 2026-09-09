"""Build "00 Open in your own software": everything Ming asked for, in one place.

    python3 tools/export_bundles.py --review reviews/v0003 --out <new dir>

Ming's feedback (via Leif, 2026-09-09): the STP files come one by one; he wants
an export-all for 3D printing and options for SolidWorks, Fusion, other CAD and
print software. This writes, from the issued review he already has:

  STEP 1 - whole robot assembled, all 70 pieces.stp     what Ming asked for: one STP with every part
  STEP 2 - all 30 printed parts side by side.stp        every printed part, one file, laid out flat
  STEP 3 - real solid CAD parts only, assembled.stp     the 10 parts that have true CAD, positioned
  STEP 4 - one file per printed part.zip                 30 single-part STPs + servo and HAT references
  3MF 1 - whole robot assembled.3mf                      same robot for slicers and mesh-capable CAD
  3MF 2 - print all PLA parts.3mf, 3MF 3 - ... TPU       every printable part with quantities
  STL - all 30 printed parts.zip                         plain STLs by material
  READ ME - which file for what.html / .txt              bilingual guide

Leif, 2026-09-09: "make different versions so he can grab whatever he needs
with clear labeling". Real solid CAD is used where it exists and matches the
STL (FreeCAD check); the manufacturer servo solid is placed with the proven
frame; bearings are simplified rings; every other part is a faceted body made
from the very mesh Ming has, and is labelled "(mesh body)". Nothing here sends
anything.
"""
import argparse, csv, hashlib, html, io, json, math, os, re, shutil, struct, subprocess, sys, tempfile, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from indexed_3mf import mesh_xml

FREECADCMD = os.environ.get('FREECADCMD', '/opt/homebrew/bin/freecadcmd')
# Solid CAD sources for the parts Ming has as STL. Verified against that STL before use.
STEP_SOURCES = {
    'microduck-hip-bracket': 'research/mesh-quality-2026-09-09/microduck-hip-bracket.step',
    'microduck-power-support': 'research/mesh-quality-2026-09-09/microduck-power-support.step',
    'microduck-upper-leg-left': 'research/mesh-repair-2026-09-09/indexed-cavity/microduck-upper-leg-left.step',
    'microduck-upper-leg-right': 'research/mesh-repair-2026-09-09/indexed-cavity/microduck-upper-leg-right.step',
    'microduck-yaw-roll-motion': 'research/mesh-repair-2026-09-09/yaw-rebuild/microduck-yaw-roll-motion.step',
    'microduck-shin': 'research/mesh-repair-2026-09-09/microduck-shin.step',
    'microduck-trunk-base': 'research/mesh-repair-2026-09-09/microduck-trunk-base.step',
    'microduck-yaw2roll': 'research/mesh-repair-2026-09-09/microduck-yaw2roll.step',
    'microduck-bearing-roll': 'research/mesh-repair-2026-09-09/microduck-bearing-roll.step',
    'microduck-banana-pcb-locker': 'research/mesh-repair-2026-09-09/microduck-banana-pcb-locker.step',
}
REFERENCE_STEPS = {  # bought parts: manufacturer / board files, shipped as-is
    'ROBOTIS XL330 servo (manufacturer STEP).stp': 'ce-parts/xl330-m288-t/iterations/v0.0.1/geometry/robotis-xl-xc-330.stp',
    'Robot HAT PCBA (our board, unreleased).step': 'out/pcb/hat/robot-hat-pcba.step',
}
COLORS = {'print': '#7fb3d5', 'bought': '#8d8d8d', 'tpu': '#f0b27a'}
FOLDER = '00 Open in your own software'
BEARINGS = {'bearing-22x16x4': (22, 16, 4), 'bearing-15x10x3': (15, 10, 3)}
SERVO_STEP = 'ce-parts/xl330-m288-t/iterations/v0.0.1/geometry/robotis-xl-xc-330.stp'
NAMES = {'step_all': 'STEP 1 - whole robot assembled, all 70 pieces.stp', 'step_flat': 'STEP 2 - all 30 printed parts side by side.stp', 'step_solids': 'STEP 3 - real solid CAD parts only, assembled.stp', 'step_zip': 'STEP 4 - one file per printed part.zip', 'mf_all': '3MF 1 - whole robot assembled.3mf', 'mf_PLA': '3MF 2 - print all PLA parts.3mf', 'mf_TPU': '3MF 3 - print all TPU parts.3mf', 'stl_zip': 'STL - all 30 printed parts.zip', 'readme': 'READ ME - which file for what'}


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read_stl(path):
    data = Path(path).read_bytes()
    if len(data) >= 84 and len(data) == 84+50*struct.unpack_from('<I', data, 80)[0]:
        tris = [row[3:12] for row in struct.iter_unpack('<12fH', data[84:])]
    else:
        v = [float(x) for m in re.finditer(rb'vertex\s+([-+\deE.]+)\s+([-+\deE.]+)\s+([-+\deE.]+)', data) for x in m.groups()]
        tris = [tuple(v[i:i+9]) for i in range(0, len(v), 9)]
    if not tris: raise ValueError('empty STL '+str(path))
    return tris


def tri_verts(tris):
    for t in tris:
        yield t[0:3]; yield t[3:6]; yield t[6:9]


def bounds(pts):
    xs, ys, zs = zip(*pts)
    return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))


def indexed_mesh_xml(positions, indices):
    verts = ''.join('<vertex x="%.4f" y="%.4f" z="%.4f"/>\n' % tuple(positions[3*i:3*i+3]) for i in range(len(positions)//3))
    tris = ''.join('<triangle v1="%d" v2="%d" v3="%d"/>\n' % tuple(indices[i:i+3]) for i in range(0, len(indices), 3))
    return '<mesh><vertices>\n'+verts+'</vertices><triangles>\n'+tris+'</triangles></mesh>'


def write_3mf(path, objects, items, title, materials):
    """objects: [(id, name, mesh_xml, material_index)], items: [(object id, 4x3 transform or None)]."""
    mats = ''.join('<base name="%s" displaycolor="%s"/>' % (html.escape(n), c) for n, c in materials)
    model = ['<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n',
             '<metadata name="Title">%s</metadata><metadata name="Designer">Leif Rydenfalk</metadata><metadata name="Application">ce-workshop export_bundles</metadata>\n' % html.escape(title),
             '<resources>\n<basematerials id="1">%s</basematerials>\n' % mats]
    for oid, name, mesh, mi in objects:
        model.append('<object id="%d" name="%s" type="model" pid="1" pindex="%d">%s</object>\n' % (oid, html.escape(name, quote=True), mi, mesh))
    model.append('</resources>\n<build>\n')
    for oid, tf in items:
        model.append('<item objectid="%d"%s/>\n' % (oid, (' transform="%s"' % ' '.join('%.4f' % v for v in tf)) if tf else ''))
    model.append('</build>\n</model>\n')
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr('3D/3dmodel.model', ''.join(model))
    return {'objects': len(objects), 'items': len(items), 'bytes': os.path.getsize(path)}


def grid_layout(entries, width=240.0, gap=6.0):
    """entries: [(footprint w, d)] -> [(x, y)] row packing, largest first order kept by caller."""
    x = y = rowh = 0.0; out = []
    for w, d in entries:
        if x > 0 and x+w > width:
            x = 0.0; y += rowh+gap; rowh = 0.0
        out.append((x, y)); x += w+gap; rowh = max(rowh, d)
    return out


def build(review, out, project=ROOT):
    review = review.resolve(); out = out.resolve(); project = project.resolve()
    if out.exists(): raise FileExistsError('choose a new output directory: '+str(out))
    dest = out/FOLDER; dest.mkdir(parents=True)
    parts = list(csv.DictReader((review/'PARTS.csv').open(encoding='utf-8-sig')))
    manifest = json.loads((project/'out/print/stl_manifest.json').read_text())
    printable = [r for r in parts if r['slug'] in manifest]
    report = {'review': str(review), 'review_version': json.loads((review/'VERSION.json').read_text()), 'files': {}}

    # 1. Whole robot 3MF: the published 70-piece mesh, placed, one object per piece.
    mesh_json = review/'01 See the robot/Published assembly mesh.json'
    robot = json.loads(mesh_json.read_text())
    materials = [('Printed part (PLA)', COLORS['print']), ('Bought component', COLORS['bought']), ('Printed part (TPU)', COLORS['tpu'])]
    objects, items = [], []
    for i, p in enumerate(robot['parts'], 1):
        slug = p['name'].split('/')[1].split('#')[0]
        mi = 0 if slug in manifest and manifest[slug]['material'] == 'PLA' else 2 if slug in manifest else 1
        objects.append((i, p['name'], indexed_mesh_xml(p['positions'], p['indices']), mi)); items.append((i, None))
    f = dest/NAMES['mf_all']
    report['files'][f.name] = write_3mf(f, objects, items, 'Microduck - whole robot, 70 placed pieces, review geometry', materials)

    # 2. Print-all 3MF per material and the STL zip, from the STLs already in the review.
    stlzip = dest/NAMES['stl_zip']; rows = []; printed = {}
    with zipfile.ZipFile(stlzip, 'w', zipfile.ZIP_DEFLATED) as z:
        for mat in ('PLA', 'TPU'):
            sel = [r for r in printable if manifest[r['slug']]['material'] == mat]
            objs, its, geo = [], [], []
            for r in sel:
                src = review/r['stl']; tris = read_stl(src)
                lo, hi = bounds(list(tri_verts(tris)))
                qty = int(manifest[r['slug']].get('qty') or 1)
                name = '%02d %s x%d.stl' % (int(r['number']), r['part'], qty)
                z.write(src, mat+'/'+name)
                rows.append({'number': r['number'], 'part': r['part'], 'slug': r['slug'], 'quantity': qty, 'material': mat, 'stl_in_zip': mat+'/'+name,
                             'bbox_mm': [round(hi[k]-lo[k], 1) for k in range(3)], 'orientation_note': manifest[r['slug']].get('orientation_rule', ''), 'source': r['source_kind']})
                geo.append((r, tris, lo, hi, qty))
                printed[r['slug']] = {'stl': str(src), 'label': '%02d %s' % (int(r['number']), r['part']), 'out_name': '%02d %s' % (int(r['number']), r['part']), 'stl_min': list(lo), 'stl_max': list(hi)}
            geo.sort(key=lambda g: -(g[3][0]-g[2][0])*(g[3][1]-g[2][1]))
            cells = [(hi[0]-lo[0], hi[1]-lo[1]) for r, tris, lo, hi, qty in geo for _ in range(qty)]
            pos = grid_layout(cells); k = 0
            for oid, (r, tris, lo, hi, qty) in enumerate(geo, 1):
                objs.append((oid, r['part'], mesh_xml(list(tri_verts(tris))), 0 if mat == 'PLA' else 2))
                for c in range(qty):
                    x, y = pos[k]; k += 1
                    its.append((oid, [1, 0, 0, 0, 1, 0, 0, 0, 1, x-lo[0], y-lo[1], -lo[2]]))
            f = dest/NAMES['mf_'+mat]
            report['files'][f.name] = write_3mf(f, objs, its, 'Microduck - all %s parts with quantities' % mat, materials)
    report['files'][stlzip.name] = {'bytes': stlzip.stat().st_size, 'files': len(rows)}
    # side-by-side cells for STEP 2: one of each printed part, largest footprint first
    order = sorted(printed, key=lambda s: -(printed[s]['stl_max'][0]-printed[s]['stl_min'][0])*(printed[s]['stl_max'][1]-printed[s]['stl_min'][1]))
    for s, cell in zip(order, grid_layout([(printed[s]['stl_max'][0]-printed[s]['stl_min'][0], printed[s]['stl_max'][1]-printed[s]['stl_min'][1]) for s in order], width=320.0, gap=10.0)):
        printed[s]['cell'] = list(cell)

    # 3. STEP variants via FreeCAD.
    tmp = Path(tempfile.mkdtemp(prefix='bundles-')); part_dir = tmp/'parts'; part_dir.mkdir()
    cands = {slug: {'step': str(project/src)} for slug, src in STEP_SOURCES.items() if slug in printed and (project/src).is_file()}
    job = {'candidates': cands, 'printed': printed, 'bearings': BEARINGS, 'servo_step': str(project/SERVO_STEP) if (project/SERVO_STEP).is_file() else None,
           'scene': json.loads((project/'out/web/scene.json').read_text()), 'mesh_json': str(mesh_json), 'part_dir': str(part_dir),
           'step_all': str(dest/NAMES['step_all']), 'step_flat': str(dest/NAMES['step_flat']), 'step_solids': str(dest/NAMES['step_solids']),
           'result': str(tmp/'result.json'), 'log': str(out/'EXPORT LOG.txt')}
    (tmp/'job.json').write_text(json.dumps(job))
    proc = subprocess.run([FREECADCMD, str(ROOT/'tools/export_assembly_step.py'), str(tmp/'job.json')], capture_output=True, text=True, timeout=7200)
    if not (tmp/'result.json').is_file():
        raise RuntimeError('FreeCAD export failed:\n'+proc.stdout[-3000:]+proc.stderr[-3000:])
    fc = json.loads((tmp/'result.json').read_text())
    stepzip = dest/NAMES['step_zip']
    with zipfile.ZipFile(stepzip, 'w', zipfile.ZIP_DEFLATED) as z:
        for slug, rec in fc['parts'].items():
            z.write(rec['file'], 'Printed parts/'+Path(rec['file']).name)
        for name, src in REFERENCE_STEPS.items():
            if (project/src).is_file(): z.write(project/src, 'Bought parts (reference)/'+name)
        z.writestr('WHICH PARTS ARE REAL CAD.txt', which_parts_text(rows, fc))
    report['files'][stepzip.name] = {'bytes': stepzip.stat().st_size, 'files': len(fc['parts'])+len(REFERENCE_STEPS)+1}
    for key in ('step_all', 'step_flat', 'step_solids'):
        report['files'][NAMES[key]] = {k: v for k, v in fc['files'][key].items() if k != 'file'}
    report['step_parts'] = fc['parts']; report['assembled_pieces'] = fc['pieces']; report['servo'] = fc.get('servo'); report['freecad_seconds'] = fc.get('seconds')
    for r in rows: r['cad'] = fc['parts'][r['slug']]['kind']
    shutil.rmtree(tmp)

    # 4. Instructions and index.
    write_readme(dest, rows, report)
    with (dest/'PARTS - formats.csv').open('w', newline='', encoding='utf-8-sig') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows([{k: (json.dumps(v) if isinstance(v, list) else v) for k, v in r.items()} for r in rows])
    files = sorted(p for p in out.rglob('*') if p.is_file())
    report['manifest'] = [{'file': p.relative_to(out).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p)} for p in files]
    (out/'EXPORT REPORT.json').write_text(json.dumps(report, indent=1))
    return report


def which_parts_text(rows, fc):
    lines = ['Which printed parts are real solid CAD and which are faceted mesh bodies', '哪些打印件是真实实体 CAD，哪些是网格面体', '',
             'A "mesh body" is the STL you already have, converted face by face so it opens in a STEP file. It measures correctly but has no editable features.',
             '"网格面体" 是你已有的 STL 逐面转换而成，可在 STEP 中打开，尺寸正确，但没有可编辑特征。', '']
    for r in rows:
        lines.append('%02d %s (%s): %s' % (int(r['number']), r['part'], r['material'], fc['parts'][r['slug']]['kind']))
    return '\n'.join(lines)+'\n'


def write_readme(dest, rows, report):
    n_solid = sum(r['cad'].startswith('solid') for r in rows); n = len(rows)
    F = report['files']
    def mb(name): return '%.0f MB' % (F[name]['bytes']/1e6) if F[name]['bytes'] >= 1e6 else '%.0f KB' % (F[name]['bytes']/1e3)
    variants = [
        (NAMES['step_all'], 'One STP with every part of the robot in its place: %d pieces. This is the "STP with all the parts". Real CAD where it exists, manufacturer servo solids, simplified bearing rings, and faceted mesh bodies for the rest (labelled "mesh body"). Large file: SolidWorks and Fusion take minutes to import it.' % F[NAMES['step_all']]['pieces'],
         '一个 STP 包含整机全部 %d 个零件并已定位，即"包含所有零件的 STP"。有真实 CAD 的用真实 CAD，舵机用厂商实体，轴承用简化圆环，其余为网格面体（标注 "mesh body"）。文件较大，SolidWorks/Fusion 导入需几分钟。' % F[NAMES['step_all']]['pieces']),
        (NAMES['step_flat'], 'One STP with each of the %d printed parts once, laid out side by side, not assembled. For checking parts one at a time without opening files one by one.' % n,
         '一个 STP 包含 %d 个打印件各一个，平铺摆放，未装配。适合逐个检查零件而不必逐个打开文件。' % n),
        (NAMES['step_solids'], 'Only the %d parts that exist as true solid CAD (%d pieces), assembled. Small and clean; editable features. No shells, no bought parts.' % (n_solid, F[NAMES['step_solids']]['pieces']),
         '仅包含 %d 个有真实实体 CAD 的零件（%d 件），已装配。文件小而干净，可编辑。不含外壳和外购件。' % (n_solid, F[NAMES['step_solids']]['pieces'])),
        (NAMES['step_zip'], 'Every printed part as its own STP (%d files), plus the manufacturer servo STEP and our HAT board. Mesh bodies are marked in the file name.' % n,
         '每个打印件一个 STP（%d 个），另附厂商舵机 STEP 和我们的 HAT 板。网格面体在文件名中标明。' % n),
        (NAMES['mf_all'], 'The same whole robot as a 3MF mesh. Opens in Bambu Studio, OrcaSlicer, PrusaSlicer, Cura, Windows 3D Viewer, Fusion 360 and SolidWorks 2023+. Fast to open.',
         '同样的整机，3MF 网格格式。可在 Bambu Studio、OrcaSlicer、PrusaSlicer、Cura、Windows 3D 查看器、Fusion 360、SolidWorks 2023+ 中打开，打开速度快。'),
        (NAMES['mf_PLA'], 'Every PLA part with its quantity already placed for a slicer. Use Arrange and Orient for your printer; this is a flat grid, not a validated plate.',
         '全部 PLA 打印件按数量放好，供切片软件使用。请用自动排列和自动朝向；这只是平铺，不是验证过的打印盘。'),
        (NAMES['mf_TPU'], 'Every TPU (soft) part, same idea.', '全部 TPU 软件零件，同上。'),
        (NAMES['stl_zip'], 'Plain STL files, one zip, PLA and TPU folders, quantity in each file name.', '普通 STL 文件一个压缩包，分 PLA/TPU 文件夹，文件名含数量。'),
    ]
    soft = [
        ('SolidWorks', 'File › Open, file type STEP. STP and STEP are the same format. Whole robot: STEP 1. Quick and clean: STEP 3. Individual parts: STEP 4. 3MF opens in SolidWorks 2023 or newer as mesh bodies.',
         '文件 › 打开，类型 STEP。STP 与 STEP 是同一格式。整机：STEP 1；小而干净：STEP 3；单个零件：STEP 4。SolidWorks 2023 以上可打开 3MF 网格体。'),
        ('Fusion 360', 'File › Upload any STP, or Insert › Insert Mesh for 3MF/STL. Mesh bodies can be converted with Mesh › Convert Mesh if you want to edit a shell.',
         '文件 › 上传任意 STP，或 插入 › 插入网格 打开 3MF/STL。需要编辑外壳时用 网格 › 转换网格。'),
        ('FreeCAD, Onshape, Inventor, Creo, NX, Rhino', 'STP files open directly; 3MF and STL import as meshes.', 'STP 直接打开；3MF 与 STL 作为网格导入。'),
        ('Bambu Studio, OrcaSlicer, PrusaSlicer, Cura', 'Open 3MF 2 and 3MF 3 to print, or drag STLs from the STL zip.', '打开 3MF 2 和 3MF 3 进行打印，或从 STL 压缩包拖入。'),
        ('Just looking (Windows 3D Viewer, macOS Preview, phone)', 'Open 3MF 1 or any STL.', '打开 3MF 1 或任意 STL。'),
    ]
    vt = ''.join('<tr><td><b>%s</b><br><small>%s</small></td><td>%s<br><small>%s</small></td></tr>' % (html.escape(f), mb(f), html.escape(a), html.escape(b)) for f, a, b in variants)
    st = ''.join('<tr><td>%s</td><td>%s<br><small>%s</small></td></tr>' % (html.escape(a), html.escape(b), html.escape(c)) for a, b, c in soft)
    pt = ''.join('<tr><td>%02d</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (int(r['number']), html.escape(r['part']), r['quantity'], r['material'], html.escape(r['cad'])) for r in rows)
    body = ('<h1>Microduck: which file for what / 哪个文件做什么</h1>'
            '<p>Pick the one you need. All files describe the same geometry, in millimetres, from review v0003. Engineering review, not manufacturing approval.</p>'
            '<p>按需选择。所有文件描述同一几何，单位毫米，来自评审包 v0003。仅供工程评审，不是生产批准。</p>'
            '<h2>The files / 文件</h2><table><tr><th>File / 文件</th><th>What it is for / 用途</th></tr>'+vt+'</table>'
            '<h2>By program / 按软件</h2><table><tr><th>Software / 软件</th><th>What to open / 打开什么</th></tr>'+st+'</table>'
            '<h2>Real CAD or mesh body? / 真实 CAD 还是网格面体？</h2><p>%d of the %d printed parts exist as true solid CAD and are verified against the STL. The other %d are vendor reference meshes with no solid source; in the STP files they are faceted mesh bodies (correct dimensions, no editable features), labelled "mesh body". Bought parts: servos are the manufacturer solid placed with the proven frame, bearings are catalogue-size rings, boards and battery are envelopes.</p>'
            '<p>%d 个打印件中 %d 个有真实实体 CAD 并已与 STL 校验；其余 %d 个为供应商参考网格，没有实体来源，在 STP 中为网格面体（尺寸正确，无可编辑特征），标注 "mesh body"。外购件：舵机为厂商实体并按验证过的坐标系放置，轴承为标准尺寸圆环，板卡和电池为外形包络。</p>'
            '<h2>Parts / 零件</h2><table><tr><th>#</th><th>Part</th><th>Qty</th><th>Material</th><th>CAD kind</th></tr>'+pt+'</table>') % (n_solid, n, n-n_solid, n, n_solid, n-n_solid)
    css = 'body{font:16px/1.5 system-ui;max-width:1000px;margin:32px auto;padding:0 16px;color:#163447}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #d2e0e5;padding:8px;text-align:left;vertical-align:top}small{color:#506874}'
    (dest/(NAMES['readme']+'.html')).write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Microduck: which file for what</title><style>'+css+'</style>'+body+'</html>')
    txt = ['MICRODUCK: WHICH FILE FOR WHAT / 哪个文件做什么', '', 'Units mm. Review geometry, not manufacturing approval. STP and STEP are the same format.', '']
    for f, a, b in variants: txt += [f+'  ('+mb(f)+')', '  '+a, '  '+b, '']
    txt += ['BY PROGRAM / 按软件', '']
    for a, b, c in soft: txt += [a+':', '  '+b, '  '+c, '']
    (dest/(NAMES['readme']+'.txt')).write_text('\n'.join(txt))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--review', type=Path, required=True, help='issued review directory, e.g. reviews/v0003')
    ap.add_argument('--out', type=Path, required=True, help='new directory to write into')
    a = ap.parse_args()
    r = build(a.review, a.out)
    print(json.dumps({k: v for k, v in r.items() if k in ('files', 'assembly')}, indent=1, default=str)[:4000])
