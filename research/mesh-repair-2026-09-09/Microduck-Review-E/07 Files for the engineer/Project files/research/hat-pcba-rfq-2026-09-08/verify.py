"""Validate the reference RFQ quantities and evidence, without changing source files."""
import csv, hashlib, json
from pathlib import Path
here=Path(__file__).resolve().parent
root=here.parents[1]
a=json.loads((here/'audit.json').read_text())
m=json.loads((here/'manifest.json').read_text())
rows=list(csv.DictReader((here/'conditional-pcba-quote.csv').open()))
checks=[]
def check(name, result):
    assert result, name
    checks.append(name)
check('113 unique physical quote rows',len(rows)==len({r['designator'] for r in rows})==113)
check('DNP and artwork excluded',not ({r['designator'] for r in rows}&({r['designator'] for r in a['dnp']}|{'FID1','FID2','FID3','H2','H3'})))
check('physical batch counts',all(sum(int(r[f'quantity_{n}_board'+('s' if n!=1 else '')]) for r in rows)==113*n for n in [1,100,1000]))
check('110 supplier codes, 3 explicit unknowns',sum(r['lcsc_order_code'].startswith('C') and r['lcsc_order_code']!='CANNOT DETERMINE' for r in rows)==110 and a['missing_order_codes']==['TP2','TP3','TP4'])
check('source consistency lists empty',all(not a['consistency'][k] for k in ['bom_row_quantity_errors','dnp_accidentally_in_pos','fitted_bom_missing_pos','physical_pos_missing_bom','bom_lcsc_vs_pcb_mismatches','existing_extraction_mismatches']))
check('source hashes unchanged',all(hashlib.sha256((root/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in m['files']))
check('four pinned upstream byte checks retained',sum(f.get('upstream_bytes_match') is True for f in m['files'])==4)
check('four copper Gerbers',sum('Copper' in (f['file_function'] or '') for f in m['gerber_zip_members'])==4)
check('DRC evidence unchanged',hashlib.sha256((here/a['drc']['source_file']).read_bytes()).hexdigest()==a['drc']['sha256'])
check('DRC failures explicit',a['drc']['severity_counts']=={'error':40,'warning':9} and a['drc']['observed_exit_code']==5)
check('orientation evidence unchanged',hashlib.sha256((root/a['orientation']['source_file']).read_bytes()).hexdigest()==a['orientation']['sha256'])
check('reference-only HTML',all(t in (here/'APPENDIX.html').read_text() for t in ['NOT RELEASED FOR MANUFACTURE','23.010002','0.0200','0.2000']))
(here/'verification.json').write_text(json.dumps({'checks_passed':len(checks),'checks':checks,'scope':'File consistency and quote quantities; no physical acceptance or manufacturing release'},indent=2)+'\n')
print(f'{len(checks)} checks passed')
