"""Refuse a test-plan release that silently re-enables unresolved power tests."""
HELD = {'EB-04','EB-05','EB-06','EN-01','EN-02'}

def check(doc):
    bad=[]
    hold=doc.get('power_execution_hold',{})
    if hold.get('status')!='HOLD':bad.append('original power execution hold absent')
    rows={t['id']:t for s in doc['sections'] for t in (s.get('tests') or s.get('rows') or [])}
    for ident in HELD:
        t=rows[ident]
        if t.get('execution_status')!='HOLD' or not any('HOLD' in s for s in t['pre']):bad.append(ident+': missing execution HOLD')
        if 'Unavailable' not in t['gate']['PASS']:bad.append(ident+': held test offers PASS')
        if any(any(v in s.get('do','') for v in ('8.20','8.200','7.40','7.400','6.60','6.600')) for s in t['steps']):bad.append(ident+': obsolete voltage sequence active')
        if not any(e[0]==ident and 'HOLD' in e[1] for e in doc['eol']):bad.append(ident+': EOL row omits HOLD')
    sv = rows['SV-01']
    if sv.get('execution_status') != 'IDENTIFICATION_ONLY' or any(r[1] != 'verify' for r in sv['readback']):
        bad.append('SV-01 must retain read-only identity gate')
    if 'Unavailable' not in sv['gate']['PASS'] or not all(n in str(sv) for n in ('1200', '1190')):
        bad.append('SV-01 must not equate local M288 model with confirmed original identity')
    sn = rows['SN-05']['gate']['CD']
    if 'inspected on 2026-09-08' not in sn or 'for that board exists' in sn:
        bad.append('SN-05 source absence must be scoped to inspected sources')
    wk = rows['WK-02']
    if wk.get('criterion_scope') != 'LOCAL_SIMULATION_COMPARISON_NOT_ORIGINAL_ACCEPTANCE' or 'Local comparison only' not in wk['gate']['PASS']:
        bad.append('WK-02 local simulation criterion must not become original acceptance')
    return bad
