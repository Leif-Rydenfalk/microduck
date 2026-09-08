"""Freeze a numbered review from committed Git objects, never the live worktree."""
import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
WORKSHOP = ROOT.parents[1]
PREFIXES = (
    'research/xl330-geometry-revision-2026-09-08/',
    'research/xl330-mechanical-source-2026-09-08/',
    'research/xl330-interface-revision-review-2026-09-08/',
    'research/servo-fastener-restriction-2026-09-08/',
    'research/rfq-source-corrections-2026-09-08/',
    'research/servo-capture-tooling-2026-09-08/',
    'ce-parts/xl330-m288-t/iterations/v0.0.1/',
)
FILES = (
    'SOURCING.html', 'RFQ.html', 'spec/sourcing.json', 'tools/doc.css',
    'ce-parts/xl330-m288-t/component.json',
    'research/servo-power-audit-2026-09-08/AUDIT.md',
    'out/handover/HEAD-JOB-OBSERVATION-2026-09-08-2318.json',
    'out/drawings/microduck-shin/microduck-shin.pdf',
    'out/drawings/microduck-shin/microduck-shin.svg',
    'out/drawings/microduck-shin/result.json',
    'out/drawings/microduck-shin/pdf-readback.json',
    'out/drawings/microduck-shin/render-scale-readback.json',
    'out/drawings/microduck-shin/detail-A-supplement-build/microduck-shin.pdf',
    'out/drawings/microduck-shin/detail-A-supplement-build/microduck-shin.svg',
    'out/drawings/microduck-shin/detail-A-supplement-build/result.json',
    'out/drawings/microduck-shin/detail-A-supplement-build/pdf-readback.json',
    'out/drawings/microduck-shin/detail-A-supplement-build/render-scale-readback.json',
)


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def freeze(version, revision, core_revision, previous=None):
    if not re.fullmatch(r'v\d{4}', version):
        raise ValueError('Version must be vNNNN')
    out = ROOT/'reviews'
    target, archive = out/version, out/('Microduck-review-'+version+'.zip')
    if target.exists() or archive.exists():
        raise FileExistsError('Issued versions cannot be overwritten: '+version)
    if previous and not (out/previous/'MANIFEST.json').is_file():
        raise ValueError('Previous issued version is missing')
    revision = git(ROOT, 'rev-parse', revision+'^{commit}').decode().strip()
    core_revision = git(WORKSHOP, 'rev-parse', core_revision+'^{commit}').decode().strip()
    entries = {}
    for record in git(ROOT, 'ls-tree', '-rz', revision).split(b'\0'):
        if not record:
            continue
        meta, raw_path = record.split(b'\t', 1)
        path = raw_path.decode()
        if path in FILES or path.startswith(PREFIXES):
            mode, kind, oid = meta.decode().split()
            if kind != 'blob' or mode == '120000':
                raise ValueError('Unexpected non-file review input: '+path)
            entries[path] = oid
    if set(FILES) - entries.keys():
        raise ValueError('Required files missing from pinned revision')
    out.mkdir(exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix='.'+version+'-', dir=out))
    zip_temp = temp.with_suffix('.zip.tmp')
    try:
        for path, oid in entries.items():
            dest = temp/path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(git(ROOT, 'cat-file', 'blob', oid))
        for path in ('ce-cad/cecad/render.py', 'ce-cad/cecad/autosheet.py'):
            dest = temp/'core-source'/path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(git(WORKSHOP, 'show', core_revision+':'+path))
        brief = f'''# Microduck 1:1 recreation — review {version}

**Engineering review only. A complete 1:1 recreation has not been verified.**

This numbered package is frozen. Later experiments and drawing changes are
separate versions and are not included. Nothing has been sent to your boss by
this tool.

## Version identity

- Microduck source commit: `{revision}`
- CAD core commit: `{core_revision}`
- Previous issued package: `{previous or 'none — first numbered boss review'}`
- Every included file is listed with its SHA-256 in `MANIFEST.json`.
- Source history remains in Git; the published servo v0.0.1 and the corrected
  research candidate are both included separately. This is a selected evidence
  package, not a complete repository backup or an archive of every temporary run.

## What changed and what remains open

| Area | Verified evidence | Remaining limitation |
|---|---|---|
| Servo mechanics | Manufacturer maximum pilot depth is 3 mm; existing model used 6 mm. Corrected mounting-hole candidate passed 100 geometric probes. | Center geometry and other exterior details remain incomplete; original installed identity is unverified in this revision. |
| Fasteners | All 52 servo ISO-length proposals withdrawn; 35 historical modeled penetrations exceeded 3 mm. Rebuild guard preserves existing assembly records. | Exact original tapping screws, seating, usable engagement and torque remain unresolved. |
| Drawings | Shin principal sheet and enlarged ankle supplement pass eight sheet gates plus PDF, scale and locator readbacks. | Full contract is INCOMPLETE. Hidden E009/E047/E061 leaders and additional enlarged feature clusters remain open in this frozen version. |
| Electronics | Public PCB/runtime and manufacturer voltage limits are reconciled; power-test holds remain explicit. | No completed physical electrical acceptance. Original servo variant and installed power route remain unresolved. |
| Sourcing | Conditional supplier inquiries and priced candidates are available. | Source availability is not original-part identity or purchasing approval; quoted scope is not a complete landed robot cost. |
| Fabrication | Included printer observation records the head job running at 24% on 2026-09-08 at 23:18 UTC+08. | A dated running observation is not print completion, dimensional acceptance or a verified robot. |

## Read first

- [Shin principal drawing](out/drawings/microduck-shin/microduck-shin.pdf)
- [Enlarged ankle supplement](out/drawings/microduck-shin/detail-A-supplement-build/microduck-shin.pdf)
- [Servo source comparison](research/xl330-mechanical-source-2026-09-08/REPORT.html)
- [Servo revision dependencies](research/xl330-interface-revision-review-2026-09-08/REPORT.html)
- [Fastener withdrawal evidence](research/servo-fastener-restriction-2026-09-08/REPORT.html)
- [Sourcing](SOURCING.html) and [supplier questions](RFQ.html)

Manufacturer and supplier links may require internet access. Original research
reports can cite repository sources outside this selected package; the exact
source commit above identifies those records. Synthetic capture examples are
test fixtures, not observations of a physical robot.
'''
        (temp/'README.md').write_text(brief)
        # A self-contained landing page; all links below are included in this package.
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', brief)
        items = ''.join('<li><a href="'+html.escape(url, quote=True)+'">'+html.escape(label)+'</a></li>' for label, url in links)
        (temp/'START-HERE.html').write_text('<!doctype html><meta charset="utf-8"><title>Microduck '+version+'</title><style>body{max-width:1000px;margin:40px auto;font:17px/1.5 system-ui}pre{white-space:pre-wrap;font:15px/1.5 system-ui}</style><h1>Microduck review '+version+'</h1><p><strong>Engineering review — complete 1:1 verification remains open.</strong></p><ul>'+items+'</ul><pre>'+html.escape(brief)+'</pre>')
        for _, path in links:
            if not (temp/path).is_file():
                raise ValueError('Broken landing-page link: '+path)
        manifest = {'version': version, 'previous_version': previous,
                    'created_utc': datetime.now(timezone.utc).isoformat(),
                    'source_revision': revision, 'cad_core_revision': core_revision,
                    'scope': 'Selected engineering review; not a production release or full source backup',
                    'files': []}
        for p in sorted(temp.rglob('*')):
            if p.is_file():
                manifest['files'].append({'path': p.relative_to(temp).as_posix(),
                                          'bytes': p.stat().st_size,
                                          'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
        (temp/'MANIFEST.json').write_text(json.dumps(manifest, indent=2)+'\n')
        with zipfile.ZipFile(zip_temp, 'w', zipfile.ZIP_DEFLATED) as z:
            for p in sorted(temp.rglob('*')):
                if p.is_file():
                    z.write(p, version+'/'+p.relative_to(temp).as_posix())
        with zipfile.ZipFile(zip_temp) as z:
            assert z.testzip() is None
            for row in manifest['files']:
                assert hashlib.sha256(z.read(version+'/'+row['path'])).hexdigest() == row['sha256']
        temp.rename(target)
        zip_temp.rename(archive)
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        (out/(archive.name+'.sha256')).write_text(digest+'  '+archive.name+'\n')
        print(json.dumps({'directory': str(target), 'zip': str(archive), 'files': len(manifest['files']), 'sha256': digest}, indent=2))
    finally:
        if temp.exists():
            shutil.rmtree(temp)
        if zip_temp.exists():
            zip_temp.unlink()


def freeze_prepared(version, revision, core_revision, prefix, previous=None):
    """Freeze a complete illustrated review from committed files under prefix."""
    if not re.fullmatch(r'v\d{4}', version):
        raise ValueError('Version must be vNNNN')
    revision = git(ROOT, 'rev-parse', revision+'^{commit}').decode().strip()
    core_revision = git(WORKSHOP, 'rev-parse', core_revision+'^{commit}').decode().strip()
    prefix = prefix.strip('/')+'/'
    if '..' in Path(prefix).parts:
        raise ValueError('Invalid prepared prefix')
    out=ROOT/'reviews'; target=out/version; archive=out/('Microduck-review-'+version+'.zip')
    if target.exists() or archive.exists():
        raise FileExistsError('Issued versions cannot be overwritten')
    if previous and not (out/previous).is_dir():
        raise ValueError('Missing previous release')
    entries=[]
    for record in git(ROOT, 'ls-tree', '-rz', revision, '--', prefix).split(b'\0'):
        if not record: continue
        meta, path=record.split(b'\t',1); path=path.decode(); mode,kind,oid=meta.decode().split()
        if kind!='blob' or mode=='120000': raise ValueError('Non-file input: '+path)
        rel=path[len(prefix):]
        if rel in ('MANIFEST.csv','MANIFEST.json','VERSION.json'): continue
        entries.append((rel,oid))
    if 'START HERE.html' not in {p for p,_ in entries}: raise ValueError('Missing first document')
    out.mkdir(exist_ok=True); temp=Path(tempfile.mkdtemp(prefix='.'+version+'-',dir=out))
    zip_temp=temp.with_suffix('.zip.tmp')
    try:
        proc=subprocess.Popen(['git','-C',str(ROOT),'cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        try:
            for path,oid in entries:
                proc.stdin.write((oid+'\n').encode());proc.stdin.flush()
                header=proc.stdout.readline().split(); size=int(header[2]); data=proc.stdout.read(size)
                if len(data)!=size or proc.stdout.read(1)!=b'\n':raise ValueError('Truncated Git object')
                dest=temp/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        finally:
            proc.stdin.close();proc.wait()
        version_record={'version':version,'previous':previous,'source_revision':revision,'core_revision':core_revision,'prepared_prefix':prefix,'scope':'Engineering review; manufacturing approval pending','sent':False}
        (temp/'VERSION.json').write_text(json.dumps(version_record,indent=2)+'\n')
        manifest={**version_record,'files':[]}
        for p in sorted(temp.rglob('*')):
            if p.is_file():manifest['files'].append({'path':p.relative_to(temp).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        (temp/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
        with zipfile.ZipFile(zip_temp,'w',zipfile.ZIP_DEFLATED,compresslevel=1,allowZip64=True) as z:
            for p in sorted(temp.rglob('*')):
                if p.is_file():z.write(p,'Microduck/'+p.relative_to(temp).as_posix())
        with zipfile.ZipFile(zip_temp) as z:
            if z.testzip():raise ValueError('ZIP CRC failure')
            for r in manifest['files']:
                if hashlib.sha256(z.read('Microduck/'+r['path'])).hexdigest()!=r['sha256']:raise ValueError('ZIP hash mismatch: '+r['path'])
        temp.rename(target);zip_temp.rename(archive)
        digest=hashlib.sha256(archive.read_bytes()).hexdigest()
        (out/(archive.name+'.sha256')).write_text(digest+'  '+archive.name+'\n')
        print(json.dumps({'directory':str(target),'zip':str(archive),'files':len(manifest['files'])+1,'sha256':digest},indent=2))
    finally:
        if temp.exists():shutil.rmtree(temp)
        if zip_temp.exists():zip_temp.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', required=True)
    parser.add_argument('--source-revision', required=True)
    parser.add_argument('--core-revision', required=True)
    parser.add_argument('--previous')
    parser.add_argument('--prepared-prefix')
    args = parser.parse_args()
    if args.prepared_prefix:
        freeze_prepared(args.version, args.source_revision, args.core_revision, args.prepared_prefix, args.previous)
    else:
        freeze(args.version, args.source_revision, args.core_revision, args.previous)
