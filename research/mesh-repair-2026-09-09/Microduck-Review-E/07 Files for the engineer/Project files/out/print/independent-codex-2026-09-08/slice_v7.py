import sys,json,zipfile,copy
from pathlib import Path
sys.path.insert(0,'/Users/leifrydenfalk/dev/ce-workshop/ce-print-scheduler')
from scheduler import config,partgate
base=Path(__file__).parent;out=base.parent/'plates/HEAD-V7-candidate';doc=config.load();mc=copy.deepcopy(next(m for m in doc['printers'].values() if 'H2D' in m.get('model','')))
original=json.loads(zipfile.ZipFile(out.parent/'HEAD-V5/microduck-head-v5.gcode.3mf').read('Metadata/project_settings.config'))
proc=json.loads((base/'experiments/eye-ring-indexed-3mf/_process_resolved.json').read_text());pv={k:original[k] for k in proc if k in original and k not in {'name','from','type','version','inherits','instantiation','setting_id'}};mc.setdefault('slice_overrides',{})['process_values']=pv
(out/'process-values-from-v5.json').write_text(json.dumps(pv,indent=2))
res=partgate.gate([str(out/'microduck-head-v7-jaw-side.3mf')],mc,doc.get('policy',{}),mc['model'],'PLA',nozzle_pair=['0.4','0.6'],keep_dir=str(out));(out/'partgate-result.json').write_text(json.dumps(res,indent=2))
