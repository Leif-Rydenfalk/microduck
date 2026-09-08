"""Read-only checks of public Y1 BOM/PCB against archived source facts."""
from pathlib import Path
import csv, hashlib, json, re

PART = Path(__file__).resolve().parents[1]
ROOT = PART.parents[1]


def check():
    facts = json.loads((PART / 'SOURCE-FACTS.json').read_text()) if (PART / 'SOURCE-FACTS.json').exists() else json.loads((PART / 'docs/SOURCE-FACTS.json').read_text())
    provenance = json.loads((PART / 'PROVENANCE.json').read_text())
    for source in provenance['sources']:
        assert hashlib.sha256((ROOT / source['path']).read_bytes()).hexdigest() == source['sha256']
    bom = list(csv.DictReader((ROOT / provenance['sources'][1]['path']).open()))
    row = next(r for r in bom if 'Y1' in r.values())
    assert 'C7425459' in row.values() and '12 MHz' in row.values()
    pcb = (ROOT / provenance['sources'][0]['path']).read_text()
    start = pcb.index('(footprint "Oscillator:Oscillator_SMD_Abracon_ASDMB-4Pin_2.5x2.0mm"')
    end = pcb.index('\n\t(footprint ', start + 1)
    footprint = pcb[start:end]
    assert '(property "Reference" "Y1"' in footprint
    pads = re.findall(r'\(pad "([1-4])" smd rect\s+\(at ([\d.-]+) ([\d.-]+)\)\s+\(size ([\d.]+) ([\d.]+)\).*?\(net \d+ "([^"]+)"\)\s+\(pinfunction "([^"]+)"\)', footprint, re.S)
    assert len(pads) == 4
    for number,x,y,w,h,net,function in pads:
        expected = provenance['pins'][number]
        assert net == expected['net'] and function == expected['function']
        assert [float(w),float(h)] == facts['pcb_comparison']['pad_mm']
        assert function.upper().replace('-', '') == facts['family_evidence_only']['pin_functions'][number].upper().replace('-', '').replace('OUTPUT', 'OUT')
    xs = sorted(set(float(p[1]) for p in pads)); ys = sorted(set(float(p[2]) for p in pads))
    assert [round(xs[1]-xs[0], 4), round(ys[1]-ys[0], 4)] == facts['pcb_comparison']['center_spacing_mm']
    component = json.loads((PART / 'component.json').read_text())['record']
    chip = json.loads((PART / 'electrical.chip.json').read_text())['record']
    assert component['mpn'] == facts['identity']['mpn'] == chip['part']
    assert component['assembly_purchase_quantity'] == 0 and not component['verified']
    assert component['verdict'] == 'CANNOT DETERMINE'
    assert chip['supplies'][0]['v_min'] == 1.8 and chip['supplies'][0]['v_max'] == 3.3
    assert 'current_mA' not in chip, 'Family current must not become an exact-code guarantee'
    assert facts['pcb_comparison']['pad_mm'] != facts['family_evidence_only']['recommended_land_mm']
    return {'source_hashes': 'PASS', 'public_bom_identity': 'PASS', 'pcb_pin_semantics': 'PASS',
            'pcb_pad_measurements': 'PASS', 'manufacturer_recommended_land_match': 'FAIL',
            'exact_code_timing_current': 'CANNOT DETERMINE', 'production_unit_identity': 'CANNOT DETERMINE'}


if __name__ == '__main__':
    result = check()
    (PART / 'docs/verification.json').write_text(json.dumps(result, indent=1)+'\n')
    print(json.dumps(result, indent=1))
