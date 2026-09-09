"""Build "00 Open in your own software": everything Ming asked for, in one place.

    python3 tools/export_bundles.py --review reviews/v0003 --out <new dir>

Ming's feedback (via Leif, 2026-09-09): the STP files come one by one; he wants
an export-all for 3D printing and options for SolidWorks, Fusion, other CAD and
print software. This writes, from the issued review he already has:

  Microduck - whole robot.3mf        all 70 placed pieces, one file (CAD + slicers)
  Microduck - assembly.step          positioned solids for the parts with real CAD
  Print all - PLA.3mf, - TPU.3mf     every printable part, quantities included
  Print all - STL.zip                the same STLs, one zip, by material
  CAD - STEP.zip                     verified single-part STEPs + servo reference
  READ ME - open in your software.html / .txt   what to open in which program

STEP is written only where a solid CAD source exists and matches the STL in the
package (FreeCAD check). Vendor reference meshes stay meshes; no solid is
fabricated from a mesh. Nothing here sends anything.
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

    # 1. Whole robot: the published 70-piece mesh, placed, one object per piece.
    robot = json.loads((review/'01 See the robot/Published assembly mesh.json').read_text())
    materials = [('Printed part (PLA)', COLORS['print']), ('Bought component', COLORS['bought']), ('Printed part (TPU)', COLORS['tpu'])]
    objects, items, pieces = [], [], []
    for i, p in enumerate(robot['parts'], 1):
        slug = p['name'].split('/')[1].split('#')[0]
        mi = 0 if slug in manifest and manifest[slug]['material'] == 'PLA' else 2 if slug in manifest else 1
        objects.append((i, p['name'], indexed_mesh_xml(p['positions'], p['indices']), mi)); items.append((i, None))
        lo, hi = bounds([tuple(p['positions'][3*k:3*k+3]) for k in range(len(p['positions'])//3)])
        pieces.append({'name': p['name'], 'bbox_min': list(lo), 'bbox_max': list(hi)})
    f = dest/'Microduck - whole robot.3mf'
    report['files'][f.name] = write_3mf(f, objects, items, 'Microduck - whole robot, 70 placed pieces, review geometry', materials)

    # 2. Print-all 3MF per material and the STL zip, from the STLs already in the review.
    stlzip = dest/'Print all - STL.zip'; rows = []
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
            geo.sort(key=lambda g: -(g[3][0]-g[2][0])*(g[3][1]-g[2][1]))
            cells = []
            for r, tris, lo, hi, qty in geo:
                for _ in range(qty): cells.append((hi[0]-lo[0], hi[1]-lo[1]))
            pos = grid_layout(cells); k = 0
            for oid, (r, tris, lo, hi, qty) in enumerate(geo, 1):
                objs.append((oid, r['part'], mesh_xml(list(tri_verts(tris))), 0 if mat == 'PLA' else 2))
                for c in range(qty):
                    x, y = pos[k]; k += 1
                    its.append((oid, [1, 0, 0, 0, 1, 0, 0, 0, 1, x-lo[0], y-lo[1], -lo[2]]))
            f = dest/('Print all - %s.3mf' % mat)
            report['files'][f.name] = write_3mf(f, objs, its, 'Microduck - all %s parts with quantities' % mat, materials)
    report['files'][stlzip.name] = {'bytes': stlzip.stat().st_size, 'files': len(rows)}

    # 3. STEP: verify each solid source against the review STL, then place the verified ones.
    tmp = Path(tempfile.mkdtemp(prefix='bundles-')); step_dir = tmp/'step'; step_dir.mkdir()
    cands = {}
    for r in printable:
        src = STEP_SOURCES.get(r['slug'])
        if src and (project/src).is_file():
            cands[r['slug']] = {'step': str(project/src), 'stl': str(review/r['stl']), 'out_name': '%02d %s.step' % (int(r['number']), r['part'])}
    job = {'candidates': cands, 'scene': json.loads((project/'out/web/scene.json').read_text()), 'pieces': pieces,
           'step_dir': str(step_dir), 'assembly_step': str(dest/'Microduck - assembly.step'), 'result': str(tmp/'result.json')}
    (tmp/'job.json').write_text(json.dumps(job))
    proc = subprocess.run([FREECADCMD, str(ROOT/'tools/export_assembly_step.py'), str(tmp/'job.json')], capture_output=True, text=True, timeout=1800)
    if not (tmp/'result.json').is_file():
        raise RuntimeError('FreeCAD export failed:\n'+proc.stdout[-3000:]+proc.stderr[-3000:])
    fc = json.loads((tmp/'result.json').read_text())
    stepzip = dest/'CAD - STEP.zip'; verified = []
    with zipfile.ZipFile(stepzip, 'w', zipfile.ZIP_DEFLATED) as z:
        for slug, rec in fc['parts'].items():
            if rec.get('verified'):
                z.write(rec['written'], 'Printed parts (solid CAD)/'+Path(rec['written']).name); verified.append(slug)
        for name, src in REFERENCE_STEPS.items():
            if (project/src).is_file(): z.write(project/src, 'Bought parts (reference)/'+name)
        z.writestr('WHICH PARTS HAVE STEP.txt', which_parts_text(rows, fc))
    report['files'][stepzip.name] = {'bytes': stepzip.stat().st_size, 'verified_parts': verified}
    report['step_verification'] = fc['parts']; report['assembly'] = fc['assembly']
    if fc['assembly'] and fc['assembly'].get('file'):
        report['files']['Microduck - assembly.step'] = {'bytes': fc['assembly']['bytes'], 'placed_pieces': len(fc['assembly']['placed']), 'readback_solids': fc['assembly']['readback_solids']}
    for r in rows: r['step'] = 'yes' if r['slug'] in verified else 'no solid CAD source' if r['slug'] not in cands else 'CAD source did not match the STL; withheld'
    shutil.rmtree(tmp)

    # 4. Instructions and index.
    write_readme(dest, rows, report)
    (dest/'PARTS - formats.csv').open('w', newline='', encoding='utf-8-sig')
    with (dest/'PARTS - formats.csv').open('w', newline='', encoding='utf-8-sig') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows([{k: (json.dumps(v) if isinstance(v, list) else v) for k, v in r.items()} for r in rows])
    files = sorted(p for p in out.rglob('*') if p.is_file())
    report['manifest'] = [{'file': p.relative_to(out).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p)} for p in files]
    (out/'EXPORT REPORT.json').write_text(json.dumps(report, indent=1))
    return report


def which_parts_text(rows, fc):
    lines = ['Which printed parts have a real STEP solid, and why not otherwise', '哪些打印件有真实STEP实体，没有的原因', '']
    for r in rows:
        rec = fc['parts'].get(r['slug'])
        state = 'STEP verified against the STL' if rec and rec.get('verified') else (rec.get('reason') if rec else 'vendor reference mesh only; no solid CAD source exists, so no STEP is fabricated from it')
        lines.append('%02d %s (%s): %s' % (int(r['number']), r['part'], r['material'], state))
    return '\n'.join(lines)+'\n'


def write_readme(dest, rows, report):
    n_step = sum(r['step'] == 'yes' for r in rows); n = len(rows)
    asm = report.get('assembly') or {}
    placed = len(asm.get('placed') or [])
    soft = [
        ('SolidWorks', 'Open “Microduck - assembly.step” (File › Open, type STEP) for the %d positioned solid parts. For the complete robot with every shell, open “Microduck - whole robot.3mf” (SolidWorks 2023 or newer imports 3MF as mesh bodies) or open the STL files from “Print all - STL.zip” with “Open as Solid Body / Graphics Body”. Single parts: “CAD - STEP.zip”.' % placed,
         '打开 “Microduck - assembly.step”（文件 › 打开，STEP）查看 %d 个已定位实体零件。要看含外壳的整机，打开 “Microduck - whole robot.3mf”（SolidWorks 2023 以上可导入 3MF 网格体），或从 “Print all - STL.zip” 打开 STL（作为实体/图形体）。单个零件见 “CAD - STEP.zip”。' % placed),
        ('Fusion 360', 'File › Upload “Microduck - assembly.step” for solids, or “Microduck - whole robot.3mf” for everything. Insert › Insert Mesh takes any STL. Mesh bodies can be converted (Mesh › Convert Mesh) if you want to edit a shell.',
         '文件 › 上传 “Microduck - assembly.step”（实体）或 “Microduck - whole robot.3mf”（全部）。插入 › 插入网格可打开任意 STL；需要编辑外壳时用 网格 › 转换网格。'),
        ('FreeCAD, Onshape, Inventor, Creo, NX, Rhino', 'STEP files open directly. The 3MF and STL files import as meshes.',
         'STEP 可直接打开；3MF 与 STL 作为网格导入。'),
        ('Bambu Studio, OrcaSlicer, PrusaSlicer, Cura', 'Open “Print all - PLA.3mf” and “Print all - TPU.3mf”: every printable part is already there with the right quantity. Use the slicer’s Arrange and Orient for your printer; the layout here is a flat grid, not a validated plate. Or drag STLs from “Print all - STL.zip”.',
         '打开 “Print all - PLA.3mf” 和 “Print all - TPU.3mf”：所有打印件已按数量放好。请用切片软件的自动排列和自动朝向；此处只是平铺，不是验证过的打印盘。也可从 “Print all - STL.zip” 拖入 STL。'),
        ('Just looking (Windows 3D Viewer, macOS Preview, phone)', 'Open “Microduck - whole robot.3mf” or the STL files.',
         '直接打开 “Microduck - whole robot.3mf” 或 STL 文件即可。'),
    ]
    table = ''.join('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (html.escape('%02d' % int(r['number'])), html.escape(r['part']), r['quantity'], r['material'], html.escape(r['step']), html.escape(r['orientation_note'] or '')) for r in rows)
    files = ''.join('<li><b>%s</b> — %s</li>' % (html.escape(k), html.escape(json.dumps(v))) for k, v in report['files'].items())
    body = ('<h1>Open Microduck in your own software / 用你自己的软件打开</h1>'
            '<p>Everything in one place: one file for the whole robot, one file per material for printing, one zip of every STL, one zip of every real STEP, and the positioned assembly as STEP. Units are millimetres. Review geometry, not manufacturing approval.</p>'
            '<p>所有文件集中在此：整机一个文件、每种材料一个打印文件、全部 STL 一个压缩包、全部真实 STEP 一个压缩包，以及已定位的装配 STEP。单位毫米。仅供评审，不是生产批准。</p>'
            '<h2>Which program / 用哪个软件</h2><table><tr><th>Software / 软件</th><th>What to open / 打开什么</th></tr>'
            + ''.join('<tr><td>%s</td><td>%s<br><small>%s</small></td></tr>' % (html.escape(a), html.escape(b), html.escape(c)) for a, b, c in soft) + '</table>'
            '<h2>Honest note about STEP / 关于 STEP 的说明</h2><p>%d of the %d printed parts exist as real solid CAD and are in the STEP files; the rest are vendor reference meshes with no solid source, so they are supplied as STL/3MF only. No solid was fabricated from a mesh. Bought parts (servos, bearings, boards) are simplified envelopes in the 3MF; the manufacturer servo STEP is in “CAD - STEP.zip”.</p>'
            '<p>%d 个打印件中有 %d 个有真实实体 CAD，已提供 STEP；其余为供应商参考网格，没有实体来源，因此只提供 STL/3MF，未从网格伪造实体。外购件（舵机、轴承、板卡）在 3MF 中为简化外形；舵机厂商 STEP 在 “CAD - STEP.zip” 中。</p>'
            '<h2>Parts / 零件</h2><table><tr><th>#</th><th>Part</th><th>Qty</th><th>Material</th><th>STEP</th><th>Print orientation note</th></tr>%s</table>'
            '<h2>Files / 文件</h2><ul>%s</ul>') % (n_step, n, n, n_step, table, files)
    css = 'body{font:16px/1.5 system-ui;max-width:1000px;margin:32px auto;padding:0 16px;color:#163447}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #d2e0e5;padding:8px;text-align:left;vertical-align:top}small{color:#506874}'
    (dest/'READ ME - open in your software.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Open Microduck in your software</title><style>'+css+'</style>'+body+'</html>')
    txt = ['OPEN MICRODUCK IN YOUR OWN SOFTWARE / 用你自己的软件打开', '', 'Units: mm. Review geometry, not manufacturing approval.', '']
    for a, b, c in soft: txt += [a+':', '  '+b, '  '+c, '']
    txt += ['STEP exists for %d of %d printed parts (see CAD - STEP.zip / WHICH PARTS HAVE STEP.txt).' % (n_step, n), '']
    (dest/'READ ME - open in your software.txt').write_text('\n'.join(txt))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--review', type=Path, required=True, help='issued review directory, e.g. reviews/v0003')
    ap.add_argument('--out', type=Path, required=True, help='new directory to write into')
    a = ap.parse_args()
    r = build(a.review, a.out)
    print(json.dumps({k: v for k, v in r.items() if k in ('files', 'assembly')}, indent=1, default=str)[:4000])
