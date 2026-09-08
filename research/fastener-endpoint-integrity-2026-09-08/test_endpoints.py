import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[2]
AUDIT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT/'tools'), str(ROOT.parents[1]/'ce-cad')]
import place_fasteners as P
from cecad import triad
TRIAD_ROOT = str(ROOT)

def load(p): return json.loads((ROOT/p).read_text())

class Endpoints(unittest.TestCase):
    def test_all_paths_instances_and_world_centers_resolve(self):
        runs = [r for r in load('out/fasteners/runs.json')['runs'] if r['verdict']=='PASS']
        rows = load('ce-assemblies/microduck/current/placements.json')['record']['rows']
        joints = [j for j in load('ce-assemblies/microduck/current/joints.json')['record']['rows'] if j.get('owned_by')=='tools/place_fasteners.py']
        self.assertEqual(len(joints),64)
        world = load('out/fasteners/world-placements.json')['placements']
        for r,j in zip(runs,joints):
            e = P.resolve_pilot_endpoint(r,rows)
            self.assertEqual({k:j['b'][k] for k in e},e)
            iface = triad.interface(e['ref'],e['interface'],triad_root=TRIAD_ROOT).as_record()
            self.assertEqual(iface['thread_identity']['verdict'],'CANNOT DETERMINE')
            self.assertNotIn('thread',iface)
            matches = [p for p in world if p.get('class')=='visual' and p['body']==e['in_body'] and p['geom_index']==e['geom_index'] and p['mesh']==e['in_mesh']]
            self.assertEqual(len(matches),1)
            pl=matches[0]; c=iface['frame']['origin_mm']
            actual=[sum(pl['R'][i][k]*c[k] for k in range(3))+pl['t_mm'][i] for i in range(3)]
            self.assertLess(max(abs(a-b) for a,b in zip(actual,r['pilot_endpoint']['center_world'])),1e-8)
            p=next(p for p in rows if p.get('body')==e['in_body'] and p.get('geom_index')==e['geom_index'] and p.get('mesh')==e['in_mesh'])
            self.assertEqual(e['instance'],'%s/%s#%d'%(p['body'],p['part'].split(':')[1],rows.index(p)))

    def test_missing_and_duplicate_target_refused(self):
        r=next(r for r in load('out/fasteners/runs.json')['runs'] if r['verdict']=='PASS')
        rows=load('ce-assemblies/microduck/current/placements.json')['record']['rows']
        e=r['pilot_endpoint'];p=next(p for p in rows if all(p.get(k)==e[k] for k in ('body','geom_index','mesh')))
        for bad in ([p for p in rows if not all(p.get(k)==e[k] for k in ('body','geom_index','mesh'))], rows+[copy.deepcopy(p)]):
            with self.assertRaises(ValueError): P.resolve_pilot_endpoint(r,bad)
        with self.assertRaises(ValueError): P.resolve_pilot_endpoint({},rows)

    def test_no_geometry_or_unowned_row_change(self):
        old=json.loads((AUDIT/'placed-before.json').read_text())['placed'];new=load('out/fasteners/placed.json')['placed']
        self.assertEqual(len(old),len(new))
        for a,b in zip(old,new):
            self.assertEqual(a,{k:v for k,v in b.items() if k!='pilot_endpoint'})
        for n in ('placements','joints','bom'):
            old=json.loads((AUDIT/(n+'-before.json')).read_text());new=load('ce-assemblies/microduck/current/'+n+'.json')
            self.assertEqual(old['record']['counts'],new['record']['counts'])
            self.assertEqual([r for r in old['record']['rows'] if r.get('owned_by')!='tools/place_fasteners.py'],[r for r in new['record']['rows'] if r.get('owned_by')!='tools/place_fasteners.py'])

    def test_stale_verifier_inputs_refuse_in_temporary_root(self):
        import gen_fastener_verify as G
        hashes = json.loads((AUDIT/'verify-input-hashes.json').read_text())
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for rel in hashes:
                p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/rel).read_bytes())
            script=root/'ce-assemblies/microduck/iterations/v0.0.1/evidence/verify.py'
            script.parent.mkdir(parents=True,exist_ok=True)
            script.write_bytes((ROOT/'ce-assemblies/microduck/current/evidence/verify.py').read_bytes())
            changed=root/next(iter(hashes));changed.write_text(changed.read_text()+' ')
            result=subprocess.run([sys.executable,str(script)],text=True,capture_output=True)
            self.assertEqual(result.returncode,2)
            doc=json.loads(result.stdout)
            self.assertEqual(doc['verdict'],'CANNOT DETERMINE')
            self.assertIn('stale',doc)

    def test_existing_interfaces_unchanged(self):
        paths=sorted({str(triad.resolve(j['b']['ref'],triad_root=TRIAD_ROOT).find('cad/interfaces.json')) for j in load('ce-assemblies/microduck/current/joints.json')['record']['rows'] if j.get('owned_by')=='tools/place_fasteners.py'})
        for path in paths:
            rel=str(Path(path).resolve().relative_to(ROOT))
            old=json.loads(subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT,text=True));new=json.loads(Path(path).read_text())
            def rows(d):return d.get('interfaces',d.get('record',{}).get('interfaces'))
            self.assertEqual(rows(old),[r for r in rows(new) if r.get('owned_by')!='tools/gen_pilot_interfaces.py'])

if __name__=='__main__':unittest.main()
