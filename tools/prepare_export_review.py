"""Turn a built export directory (00 + 01 folders) into a prepared review tree for freeze_review.py.

    python3 tools/prepare_export_review.py --built <dir> --version v0005 --previous v0003 --out research/cad-export-2026-09-09/Microduck-Review-H

Writes START HERE.html and README.txt, copies both folders and their reports.
The tree is then committed and frozen with tools/freeze_review.py --prepared-prefix.
"""
import argparse, html, json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main(built, version, previous, out):
    built = built.resolve(); out = out.resolve()
    if out.exists(): raise FileExistsError(str(out))
    out.mkdir(parents=True)
    for name in ('00 Open in your own software', '01 For suppliers'):
        shutil.copytree(built/name, out/name)
    for name in ('EXPORT REPORT.json', 'EXPORT LOG.txt'):
        if (built/name).is_file(): shutil.copyfile(built/name, out/name)
    prev_sha = (ROOT/'reviews'/('Microduck-review-%s.zip.sha256' % previous)).read_text().split()[0]
    r = json.loads((built/'EXPORT REPORT.json').read_text()); F = r['files']
    def mb(n): return '%.0f MB' % (F[n]['bytes']/1e6)
    cad = [('00 Open in your own software/READ ME - which file for what.html', 'Which file for what / 哪个文件做什么'),
           ('00 Open in your own software/STEP 1 - whole robot assembled, all 70 pieces.stp', 'One STP with every part in place (%s) / 包含所有零件的 STP' % mb('STEP 1 - whole robot assembled, all 70 pieces.stp')),
           ('00 Open in your own software/STEP 2 - all 30 printed parts side by side.stp', 'All 30 printed parts side by side (%s) / 30 个打印件平铺' % mb('STEP 2 - all 30 printed parts side by side.stp')),
           ('00 Open in your own software/STEP 3 - real solid CAD parts only, assembled.stp', 'Real solid CAD parts only (%s) / 仅真实实体 CAD' % mb('STEP 3 - real solid CAD parts only, assembled.stp')),
           ('00 Open in your own software/STEP 4 - one file per printed part.zip', 'One STP per printed part (%s) / 每件一个 STP' % mb('STEP 4 - one file per printed part.zip')),
           ('00 Open in your own software/3MF 1 - whole robot assembled.3mf', 'Whole robot as 3MF, fast to open / 整机 3MF'),
           ('00 Open in your own software/3MF 2 - print all PLA parts.3mf', 'Print all PLA parts / 全部 PLA 打印件'),
           ('00 Open in your own software/3MF 3 - print all TPU parts.3mf', 'Print all TPU parts / 全部 TPU 打印件'),
           ('00 Open in your own software/STL - all 30 printed parts.zip', 'All STLs in one zip / 全部 STL')]
    sup = [('01 For suppliers/START HERE - what this is and what we need.html', 'What this is, what we need, what to do / 这是什么、需要什么、怎么做'),
           ('01 For suppliers/BOM - all purchased parts.xlsx', 'All 32 purchased lines + 30 printed parts, quantities for 1 / 10 / 100 / 全部外购件与打印件'),
           ('01 For suppliers/REPLY SHEET - fill in prices.xlsx', 'Sheet for suppliers to fill in / 供应商填价表'),
           ('01 For suppliers/OPEN DECISIONS - do not order these yet.txt', 'What not to buy yet / 未定前不要买'),
           ('01 For suppliers/LICENCE - short version.txt', 'Licence in short / 许可证简述')]
    packets = sorted(p.name for p in (out/'01 For suppliers').iterdir() if p.is_dir())
    def li(items): return ''.join('<li><a href="%s">%s</a> — %s</li>' % (html.escape(f, quote=True), html.escape(f.split('/')[-1]), html.escape(d)) for f, d in items)
    css = 'body{font:17px/1.6 system-ui;max-width:950px;margin:40px auto;padding:0 16px;color:#163447}li{margin:8px 0}small{color:#506874}h2{margin-top:30px}'
    (out/'START HERE.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Microduck %s</title><style>%s</style>' % (version, css) +
        '<h1>Microduck %s<br><small>CAD for your own software, and everything for suppliers / 给你自己软件的 CAD，以及给供应商的全部资料</small></h1>' % version +
        '<p>Supplement to review %s, which you already have. Same design; nothing new in the geometry. Two folders: <b>00</b> opens the robot in SolidWorks, Fusion, FreeCAD or any slicer in one go (one STP with all the parts, plus clearly labelled variants). <b>01</b> is what you need to get quotes and parts moving: a one-page brief, the full BOM in Excel, a reply sheet, and one forwardable packet per supplier type.</p>' % previous +
        '<p>这是对你已有的 %s 评审包的补充。设计没有变化。两个文件夹：<b>00</b> 可在 SolidWorks、Fusion、FreeCAD 或任意切片软件一次打开整机（一个包含所有零件的 STP，及清楚标注的其他版本）。<b>01</b> 是询价和采购所需的全部资料：一页说明、Excel 完整 BOM、回复表，以及按供应商类型分好的可直接转发的资料包。</p>' % previous +
        '<h2>00 Open in your own software / 用你自己的软件打开</h2><ol>'+li(cad)+'</ol>' +
        '<h2>01 For suppliers / 给供应商</h2><ol>'+li(sup)+'</ol><p>Packets / 资料包: '+', '.join(html.escape(p) for p in packets)+'</p>' +
        '<p><small>Units mm. Engineering review, not manufacturing approval. Source review %s zip SHA-256 %s. STEP verification and placement checks: EXPORT REPORT.json.</small></p></html>' % (previous, prev_sha))
    (out/'README.txt').write_text('MICRODUCK %s\n\nExtract and open START HERE.html.\n解压后打开 START HERE.html。\n\n00 Open in your own software: one STP with all the parts, plus labelled variants (3MF, STL, per-part STP).\n01 For suppliers: brief, BOM (Excel), reply sheet, one forwardable packet per supplier type.\n\nSupplement to review %s (zip SHA-256 %s). Units mm. Not manufacturing approval.\n' % (version, previous, prev_sha))
    n = sum(1 for p in out.rglob('*') if p.is_file()); print(json.dumps({'prepared': str(out), 'files': n}))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--built', type=Path, required=True); ap.add_argument('--version', required=True); ap.add_argument('--previous', required=True); ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args(); main(a.built, a.version, a.previous, a.out)
