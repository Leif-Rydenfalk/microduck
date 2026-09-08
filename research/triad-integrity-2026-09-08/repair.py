"""One authorized append-only integrity repair; refuses repeat execution."""
from pathlib import Path
import json,hashlib,subprocess,sys,os
p=Path(__file__).resolve().parent;root=p.parents[1]
if (p/'repair.json').exists():raise SystemExit('Already recorded; do not duplicate evidence')
sys.path.insert(0,'/Users/leifrydenfalk/dev/ce-workshop/bin');import _triadlib as t
slugs=['microduck-bottom-head-shell','microduck-face-part','microduck-jaw','microduck-top-head-shell'];cli='/Users/leifrydenfalk/dev/ce-workshop/bin/triad';env={**os.environ,'CE_TRIAD_ROOT':str(root)}
def sha(b):return hashlib.sha256(b).hexdigest()
artifact=root/'out/head/front_fit.json';artifact_before=artifact.read_bytes()
summary='INTEGRITY UPDATE ONLY: exact historical front_fit.json digest d40c24cc3a8bbb21d085a1624ca1bf3af561d435454a6d8bc84dfb9e862e81bc recovered at git6d028a87ff754e2e43abafc8f04f82f3f23feff5. Current digest differs only in generated timestamp and an added single-photo limitation paragraph at comparison/band_over_shell/basis; all numerical values and verdicts unchanged. Same-artifact hash supersession under TRIAD.md Correcting an artifact. No new physical test, geometry, original-unit identity or fidelity claim. Prior field FAIL/CANNOT DETERMINE remains; this export/CANNOT DETERMINE row is ignored by trust tier.'
record={'date':'2026-09-08','artifact':'out/head/front_fit.json','artifact_sha256_before':sha(artifact_before),'rows':[]}
for slug in slugs:
 ref='part:'+slug+'@v0.0.1';res=t.resolve(str(root),ref);ledger=Path(t.ledger_path(res));trust=Path(res.dir)/'trust.json';before=ledger.read_bytes();tb=trust.read_bytes();entries,probs=t.read_ledger(str(ledger));tier=t.compute_trust(res,entries=entries,problems=probs)['record']['tier'];assert json.loads(tb)['record']['tier']==tier=='T0'
 (p/(slug+'-ledger-before.jsonl')).write_bytes(before);(p/(slug+'-trust-before.json')).write_bytes(tb)
 cmd=[cli,'evidence',ref,'--kind','export','--outcome','CANNOT DETERMINE','--summary',summary,'--artifact','../../../../out/head/front_fit.json','--by','Codex source_audit integrity review 2026-09-08','--date','2026-09-08']
 result=subprocess.run(cmd,cwd=root,env=env,text=True,capture_output=True);(p/(slug+'-append.log')).write_text(result.stdout+result.stderr);assert result.returncode==0
 after=ledger.read_bytes();assert after.startswith(before);assert len(after.splitlines())==len(before.splitlines())+1;new=json.loads(after.splitlines()[-1]);assert new['kind']=='export' and new['outcome']=='CANNOT DETERMINE';assert new['sha256']==sha(artifact_before)
 ta=trust.read_bytes();assert json.loads(ta)['record']['tier']==tier
 (p/(slug+'-ledger-after.jsonl')).write_bytes(after);(p/(slug+'-trust-after.json')).write_bytes(ta)
 check=subprocess.run([cli,'check',ref,'--json'],cwd=root,env=env,text=True,capture_output=True);(p/(slug+'-check.json')).write_text(check.stdout);(p/(slug+'-check.stderr')).write_text(check.stderr)
 record['rows'].append({'ref':ref,'command':cmd,'ledger_sha256_before':sha(before),'ledger_sha256_after':sha(after),'trust_sha256_before':sha(tb),'trust_sha256_after':sha(ta),'trust_tier_before':tier,'trust_tier_after':json.loads(ta)['record']['tier'],'appended_lines':1,'check_exit_code':check.returncode})
assert artifact.read_bytes()==artifact_before
record['artifact_sha256_after']=sha(artifact.read_bytes());(p/'repair.json').write_text(json.dumps(record,indent=2)+'\n');print('PASS four append-only CLI repairs; T0 unchanged; source artifact unchanged')
